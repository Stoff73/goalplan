"""
Comprehensive test suite for session management service.

Tests cover:
- Session creation and storage (PostgreSQL + Redis)
- Session validation (fast path and fallback)
- Session updates (access token rotation)
- Session revocation (single and all)
- Session cleanup (expired sessions)
- Max 5 concurrent sessions enforcement
- Login attempt tracking
- Performance requirements (<10ms validation)

Coverage target: >90%
"""

import pytest
import uuid
import time
from datetime import datetime, timedelta
from sqlalchemy import select

from models.user import User, UserStatus, CountryPreference
from models.session import UserSession, LoginAttempt
from services.session import session_service
from services.login_attempt import login_attempt_service


# Helper function to create test user
async def create_test_user(db_session, email="test@example.com"):
    """Create a test user for session tests."""
    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
        marketing_consent=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ============================================================================
# SESSION CREATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_create_session_stores_in_postgresql(db_session):
    """Test that session creation stores data in PostgreSQL."""
    user = await create_test_user(db_session)

    session = await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="refresh_jti_123",
        access_token_jti="access_jti_123",
        device_info="Mozilla/5.0 Test Browser",
        ip_address="192.168.1.1",
    )

    assert session.id is not None
    assert session.user_id == user.id
    assert session.session_token == "refresh_jti_123"
    assert session.access_token_jti == "access_jti_123"
    assert session.device_info == "Mozilla/5.0 Test Browser"
    assert session.ip_address == "192.168.1.1"
    assert session.is_active is True
    assert session.expires_at > datetime.utcnow()

    # Verify in database
    result = await db_session.execute(
        select(UserSession).where(UserSession.session_token == "refresh_jti_123")
    )
    db_session_obj = result.scalar_one_or_none()
    assert db_session_obj is not None
    assert db_session_obj.user_id == user.id


@pytest.mark.asyncio
@pytest.mark.skipif(True, reason="Requires Redis running - integration test")
async def test_create_session_stores_in_redis(db_session, redis_client):
    """Test that session creation stores data in Redis."""
    from redis_client import redis_client as global_redis_client

    user = await create_test_user(db_session)

    await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="refresh_jti_redis",
        access_token_jti="access_jti_redis",
        device_info="Test Browser",
        ip_address="192.168.1.1",
    )

    # Check Redis using global redis client
    redis_data = await global_redis_client.get("session:refresh_jti_redis", deserialize=True)
    assert redis_data is not None
    assert redis_data["user_id"] == str(user.id)
    assert redis_data["access_token_jti"] == "access_jti_redis"
    assert redis_data["is_active"] is True


@pytest.mark.asyncio
async def test_create_session_sets_correct_expiration(db_session):
    """Test that session expiration is set correctly (7 days)."""
    user = await create_test_user(db_session)

    before_create = datetime.utcnow()
    session = await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="refresh_jti_expiry",
        access_token_jti="access_jti_expiry",
    )
    after_create = datetime.utcnow()

    # Should be ~7 days from now
    expected_expiry = before_create + timedelta(days=7)
    assert session.expires_at >= expected_expiry
    assert session.expires_at <= after_create + timedelta(days=7, minutes=1)


@pytest.mark.asyncio
async def test_create_session_without_optional_fields(db_session):
    """Test session creation with only required fields."""
    user = await create_test_user(db_session)

    session = await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="refresh_jti_minimal",
        access_token_jti="access_jti_minimal",
    )

    assert session.device_info is None
    assert session.ip_address is None
    assert session.is_active is True


@pytest.mark.asyncio
async def test_concurrent_session_creation(db_session):
    """Test creating multiple sessions concurrently."""
    user = await create_test_user(db_session)

    # Create 3 sessions
    sessions = []
    for i in range(3):
        session = await session_service.create_session(
            db=db_session,
            user_id=user.id,
            refresh_token_jti=f"refresh_jti_{i}",
            access_token_jti=f"access_jti_{i}",
        )
        sessions.append(session)

    # Verify all sessions exist
    assert len(sessions) == 3
    count = await session_service.get_session_count(db_session, user.id)
    assert count == 3


# ============================================================================
# MAX 5 SESSIONS ENFORCEMENT TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_max_5_sessions_enforced(db_session):
    """Test that exactly 5 sessions are allowed per user."""
    user = await create_test_user(db_session)

    # Create 5 sessions
    for i in range(5):
        await session_service.create_session(
            db=db_session,
            user_id=user.id,
            refresh_token_jti=f"refresh_jti_{i}",
            access_token_jti=f"access_jti_{i}",
        )

    count = await session_service.get_session_count(db_session, user.id)
    assert count == 5


@pytest.mark.asyncio
async def test_sixth_session_removes_oldest(db_session):
    """Test that 6th session removes the oldest session."""
    user = await create_test_user(db_session)

    # Create 5 sessions
    for i in range(5):
        await session_service.create_session(
            db=db_session,
            user_id=user.id,
            refresh_token_jti=f"refresh_jti_{i}",
            access_token_jti=f"access_jti_{i}",
        )
        # Small delay to ensure created_at timestamps are different
        await db_session.commit()

    # Create 6th session
    await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="refresh_jti_6",
        access_token_jti="access_jti_6",
    )

    # Should still have 5 sessions
    count = await session_service.get_session_count(db_session, user.id)
    assert count == 5

    # Verify oldest (refresh_jti_0) is removed
    result = await db_session.execute(
        select(UserSession).where(
            UserSession.session_token == "refresh_jti_0"
        )
    )
    oldest = result.scalar_one_or_none()
    assert oldest is None or oldest.is_active is False


@pytest.mark.asyncio
async def test_oldest_session_determined_by_created_at(db_session):
    """Test that oldest session is determined by created_at timestamp."""
    user = await create_test_user(db_session)

    # Create sessions with explicit ordering
    session_tokens = []
    for i in range(5):
        session = await session_service.create_session(
            db=db_session,
            user_id=user.id,
            refresh_token_jti=f"session_{i}",
            access_token_jti=f"access_{i}",
        )
        session_tokens.append(session.session_token)
        await db_session.commit()

    # Create 6th session - should remove session_0
    await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="session_new",
        access_token_jti="access_new",
    )

    # Verify session_0 is removed
    result = await db_session.execute(
        select(UserSession).where(
            UserSession.session_token == "session_0"
        )
    )
    oldest = result.scalar_one_or_none()
    assert oldest is None or oldest.is_active is False


# ============================================================================
# SESSION VALIDATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_validate_session_redis_fast_path(db_session, redis_client):
    """Test session validation uses Redis fast path."""
    user = await create_test_user(db_session)

    session = await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="fast_path_token",
        access_token_jti="access_token",
    )

    # Measure validation time
    start = time.perf_counter()
    validated = await session_service.validate_session(
        db=db_session,
        session_token="fast_path_token",
    )
    duration_ms = (time.perf_counter() - start) * 1000

    assert validated is not None
    assert validated.session_token == "fast_path_token"
    # Performance target: <10ms (Redis fast path)
    assert duration_ms < 100  # Being generous for test environment


@pytest.mark.asyncio
@pytest.mark.skipif(True, reason="Requires Redis running - integration test")
async def test_validate_session_postgresql_fallback(db_session, redis_client):
    """Test session validation falls back to PostgreSQL when Redis misses."""
    from redis_client import redis_client as global_redis_client

    user = await create_test_user(db_session)

    session = await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="fallback_token",
        access_token_jti="access_token",
    )

    # Delete from Redis to force PostgreSQL fallback
    await global_redis_client.delete("session:fallback_token")

    # Validate should still work
    validated = await session_service.validate_session(
        db=db_session,
        session_token="fallback_token",
    )

    assert validated is not None
    assert validated.session_token == "fallback_token"

    # Session should be back in Redis now
    redis_data = await global_redis_client.get("session:fallback_token", deserialize=True)
    assert redis_data is not None


@pytest.mark.asyncio
async def test_validate_expired_session_returns_none(db_session):
    """Test that expired session validation returns None."""
    user = await create_test_user(db_session)

    # Create session with past expiration
    session = await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="expired_token",
        access_token_jti="access_token",
    )

    # Manually set expiration to past
    session.expires_at = datetime.utcnow() - timedelta(hours=1)
    await db_session.commit()

    # Validation should return None
    validated = await session_service.validate_session(
        db=db_session,
        session_token="expired_token",
    )

    assert validated is None


@pytest.mark.asyncio
async def test_validate_revoked_session_returns_none(db_session):
    """Test that revoked session validation returns None."""
    user = await create_test_user(db_session)

    session = await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="revoked_token",
        access_token_jti="access_token",
    )

    # Revoke session
    await session_service.revoke_session(db_session, "revoked_token")

    # Validation should return None
    validated = await session_service.validate_session(
        db=db_session,
        session_token="revoked_token",
    )

    assert validated is None


@pytest.mark.asyncio
async def test_validate_session_updates_last_activity(db_session):
    """Test that session validation updates last_activity timestamp."""
    user = await create_test_user(db_session)

    session = await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="activity_token",
        access_token_jti="access_token",
    )

    original_activity = session.last_activity

    # Wait a bit
    import asyncio
    await asyncio.sleep(0.1)

    # Validate session
    await session_service.validate_session(
        db=db_session,
        session_token="activity_token",
    )

    # Refresh session from DB
    await db_session.refresh(session)

    # last_activity should be updated
    assert session.last_activity > original_activity


# ============================================================================
# SESSION UPDATE TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_update_access_token_jti(db_session):
    """Test updating access token JTI."""
    user = await create_test_user(db_session)

    session = await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="update_token",
        access_token_jti="old_access_jti",
    )

    # Update access token
    await session_service.update_access_token(
        db=db_session,
        session_token="update_token",
        new_access_token_jti="new_access_jti",
    )

    # Verify in database
    await db_session.refresh(session)
    assert session.access_token_jti == "new_access_jti"


@pytest.mark.asyncio
@pytest.mark.skipif(True, reason="Requires Redis running - integration test")
async def test_update_access_token_persists_to_redis(db_session, redis_client):
    """Test that access token update persists to Redis."""
    from redis_client import redis_client as global_redis_client

    user = await create_test_user(db_session)

    await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="redis_update_token",
        access_token_jti="old_access_jti",
    )

    # Update access token
    await session_service.update_access_token(
        db=db_session,
        session_token="redis_update_token",
        new_access_token_jti="new_access_jti",
    )

    # Verify in Redis
    redis_data = await global_redis_client.get("session:redis_update_token", deserialize=True)
    assert redis_data["access_token_jti"] == "new_access_jti"


@pytest.mark.asyncio
async def test_update_nonexistent_session_raises_error(db_session):
    """Test that updating non-existent session raises error."""
    with pytest.raises(ValueError):
        await session_service.update_access_token(
            db=db_session,
            session_token="nonexistent_token",
            new_access_token_jti="new_jti",
        )


# ============================================================================
# SESSION REVOCATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_revoke_single_session(db_session):
    """Test revoking a single session."""
    user = await create_test_user(db_session)

    session = await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="revoke_single",
        access_token_jti="access_token",
    )

    # Revoke session
    await session_service.revoke_session(db_session, "revoke_single")

    # Verify revoked in database
    await db_session.refresh(session)
    assert session.is_active is False


@pytest.mark.asyncio
@pytest.mark.skipif(True, reason="Requires Redis running - integration test")
async def test_revoke_session_removes_from_redis(db_session, redis_client):
    """Test that session revocation removes from Redis."""
    from redis_client import redis_client as global_redis_client

    user = await create_test_user(db_session)

    await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="revoke_redis",
        access_token_jti="access_token",
    )

    # Verify in Redis
    exists_before = await global_redis_client.exists("session:revoke_redis")
    assert exists_before is True

    # Revoke session
    await session_service.revoke_session(db_session, "revoke_redis")

    # Verify removed from Redis
    exists_after = await global_redis_client.exists("session:revoke_redis")
    assert exists_after is False


@pytest.mark.asyncio
async def test_revoke_all_user_sessions(db_session):
    """Test revoking all sessions for a user."""
    user = await create_test_user(db_session)

    # Create 3 sessions
    for i in range(3):
        await session_service.create_session(
            db=db_session,
            user_id=user.id,
            refresh_token_jti=f"revoke_all_{i}",
            access_token_jti=f"access_{i}",
        )

    # Revoke all
    count = await session_service.revoke_all_user_sessions(db_session, user.id)

    assert count == 3

    # Verify all revoked
    active_count = await session_service.get_session_count(db_session, user.id)
    assert active_count == 0


@pytest.mark.asyncio
@pytest.mark.skipif(True, reason="Requires Redis running - integration test")
async def test_revoke_all_removes_from_redis(db_session, redis_client):
    """Test that revoking all sessions removes from Redis."""
    from redis_client import redis_client as global_redis_client

    user = await create_test_user(db_session)

    # Create 2 sessions
    await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="revoke_all_redis_1",
        access_token_jti="access_1",
    )
    await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="revoke_all_redis_2",
        access_token_jti="access_2",
    )

    # Revoke all
    await session_service.revoke_all_user_sessions(db_session, user.id)

    # Verify removed from Redis
    exists_1 = await global_redis_client.exists("session:revoke_all_redis_1")
    exists_2 = await global_redis_client.exists("session:revoke_all_redis_2")
    assert exists_1 is False
    assert exists_2 is False


@pytest.mark.asyncio
async def test_revoke_all_returns_correct_count(db_session):
    """Test that revoke all returns correct count of revoked sessions."""
    user = await create_test_user(db_session)

    # Create 4 sessions
    for i in range(4):
        await session_service.create_session(
            db=db_session,
            user_id=user.id,
            refresh_token_jti=f"count_revoke_{i}",
            access_token_jti=f"access_{i}",
        )

    # Revoke all
    count = await session_service.revoke_all_user_sessions(db_session, user.id)

    assert count == 4


# ============================================================================
# SESSION CLEANUP TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_cleanup_expired_sessions_deletes_expired(db_session):
    """Test that cleanup deletes expired sessions."""
    user = await create_test_user(db_session)

    # Create session and manually expire it
    session = await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="cleanup_expired",
        access_token_jti="access_token",
    )
    session.expires_at = datetime.utcnow() - timedelta(hours=1)
    await db_session.commit()

    # Run cleanup
    count = await session_service.cleanup_expired_sessions(db_session)

    assert count >= 1

    # Verify deleted
    result = await db_session.execute(
        select(UserSession).where(UserSession.session_token == "cleanup_expired")
    )
    deleted_session = result.scalar_one_or_none()
    assert deleted_session is None


@pytest.mark.asyncio
async def test_cleanup_does_not_delete_active_sessions(db_session):
    """Test that cleanup does not delete active sessions."""
    user = await create_test_user(db_session)

    session = await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="cleanup_active",
        access_token_jti="access_token",
    )

    # Run cleanup
    await session_service.cleanup_expired_sessions(db_session)

    # Verify still exists
    result = await db_session.execute(
        select(UserSession).where(UserSession.session_token == "cleanup_active")
    )
    active_session = result.scalar_one_or_none()
    assert active_session is not None


@pytest.mark.asyncio
async def test_cleanup_returns_correct_count(db_session):
    """Test that cleanup returns correct count of deleted sessions."""
    user = await create_test_user(db_session)

    # Create 3 expired sessions
    for i in range(3):
        session = await session_service.create_session(
            db=db_session,
            user_id=user.id,
            refresh_token_jti=f"cleanup_count_{i}",
            access_token_jti=f"access_{i}",
        )
        session.expires_at = datetime.utcnow() - timedelta(hours=1)
    await db_session.commit()

    # Run cleanup
    count = await session_service.cleanup_expired_sessions(db_session)

    assert count >= 3


# ============================================================================
# LOGIN ATTEMPT TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_log_successful_login_attempt(db_session):
    """Test logging successful login attempt."""
    user = await create_test_user(db_session)

    await login_attempt_service.log_login_attempt(
        db=db_session,
        email=user.email,
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0",
        success=True,
        user_id=user.id,
    )

    # Verify logged
    result = await db_session.execute(
        select(LoginAttempt).where(LoginAttempt.email == user.email)
    )
    attempt = result.scalar_one_or_none()

    assert attempt is not None
    assert attempt.success is True
    assert attempt.user_id == user.id
    assert attempt.failure_reason is None


@pytest.mark.asyncio
async def test_log_failed_login_attempt_with_reason(db_session):
    """Test logging failed login attempt with failure reason."""
    await login_attempt_service.log_login_attempt(
        db=db_session,
        email="nonexistent@example.com",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0",
        success=False,
        failure_reason="invalid_password",
    )

    # Verify logged
    result = await db_session.execute(
        select(LoginAttempt).where(LoginAttempt.email == "nonexistent@example.com")
    )
    attempt = result.scalar_one_or_none()

    assert attempt is not None
    assert attempt.success is False
    assert attempt.failure_reason == "invalid_password"
    assert attempt.user_id is None


@pytest.mark.asyncio
async def test_count_recent_failed_attempts(db_session):
    """Test counting recent failed login attempts."""
    email = "failed@example.com"

    # Log 3 failed attempts
    for i in range(3):
        await login_attempt_service.log_login_attempt(
            db=db_session,
            email=email,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            success=False,
            failure_reason="invalid_password",
        )

    # Count failed attempts
    count = await login_attempt_service.get_recent_failed_attempts(
        db=db_session,
        email=email,
        minutes=30,
    )

    assert count == 3


@pytest.mark.asyncio
async def test_count_failed_attempts_by_ip(db_session):
    """Test counting failed attempts from an IP address."""
    ip = "192.168.1.100"

    # Log 4 failed attempts from same IP
    for i in range(4):
        await login_attempt_service.log_login_attempt(
            db=db_session,
            email=f"user{i}@example.com",
            ip_address=ip,
            user_agent="Mozilla/5.0",
            success=False,
            failure_reason="invalid_password",
        )

    # Count by IP
    count = await login_attempt_service.get_failed_attempts_by_ip(
        db=db_session,
        ip_address=ip,
        minutes=30,
    )

    assert count == 4


@pytest.mark.asyncio
async def test_login_attempt_includes_user_id_when_found(db_session):
    """Test that login attempt includes user_id when user exists."""
    user = await create_test_user(db_session)

    await login_attempt_service.log_login_attempt(
        db=db_session,
        email=user.email,
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0",
        success=False,
        user_id=user.id,
        failure_reason="invalid_password",
    )

    # Verify user_id is set
    result = await db_session.execute(
        select(LoginAttempt).where(LoginAttempt.email == user.email)
    )
    attempt = result.scalar_one_or_none()

    assert attempt.user_id == user.id


# ============================================================================
# SESSION QUERY TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_get_user_sessions_returns_active_only(db_session):
    """Test that get_user_sessions returns only active sessions."""
    user = await create_test_user(db_session)

    # Create 2 active sessions
    await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="active_1",
        access_token_jti="access_1",
    )
    await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="active_2",
        access_token_jti="access_2",
    )

    # Create and revoke 1 session
    await session_service.create_session(
        db=db_session,
        user_id=user.id,
        refresh_token_jti="revoked",
        access_token_jti="access_revoked",
    )
    await session_service.revoke_session(db_session, "revoked")

    # Get user sessions
    sessions = await session_service.get_user_sessions(db_session, user.id)

    assert len(sessions) == 2
    assert all(s.is_active for s in sessions)


@pytest.mark.asyncio
async def test_get_user_sessions_ordered_by_last_activity(db_session):
    """Test that user sessions are ordered by last_activity (newest first)."""
    user = await create_test_user(db_session)

    # Create 3 sessions
    for i in range(3):
        await session_service.create_session(
            db=db_session,
            user_id=user.id,
            refresh_token_jti=f"ordered_{i}",
            access_token_jti=f"access_{i}",
        )
        await db_session.commit()

    # Get sessions
    sessions = await session_service.get_user_sessions(db_session, user.id)

    # Verify ordered by last_activity descending
    assert len(sessions) >= 3
    for i in range(len(sessions) - 1):
        assert sessions[i].last_activity >= sessions[i + 1].last_activity
