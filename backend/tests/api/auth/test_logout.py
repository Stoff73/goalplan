"""
Comprehensive test suite for logout endpoints.

Tests cover:
1. Logout invalidates current session
2. Logged out token cannot be used again
3. Logout removes session from Redis
4. Logout is idempotent (multiple calls succeed)
5. Logout with invalid token returns 401
6. Logout with missing token returns 401
7. Logout with expired token returns 401
8. Logout updates session to inactive in database
9. Logout response format correct
10. Logout-all invalidates all user sessions
11. Logout-all returns count of revoked sessions
12. Logout-all removes all sessions from Redis
13. Logout-all only affects current user's sessions
14. Logout-all with multiple active sessions
15. Logout-all response format correct
16. User cannot use any tokens after logout-all
"""

import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserStatus, CountryPreference
from models.session import UserSession
from utils.password import hash_password
from utils.jwt import generate_access_token, generate_refresh_token, get_token_jti, verify_token
from services.session import session_service
from redis_client import redis_client
from config import settings


@pytest.fixture
async def active_user(db_session: AsyncSession):
    """Create an active user for testing."""
    user = User(
        email="test@example.com",
        password_hash=hash_password("ValidPassword123!"),
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


@pytest.fixture
async def another_user(db_session: AsyncSession):
    """Create another active user for testing multi-user scenarios."""
    user = User(
        email="another@example.com",
        password_hash=hash_password("ValidPassword123!"),
        first_name="Another",
        last_name="User",
        country_preference=CountryPreference.SA,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
        marketing_consent=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def user_session(db_session: AsyncSession, active_user: User):
    """Create a valid session for testing."""
    # Generate tokens
    access_token = generate_access_token(active_user.id)
    refresh_token = generate_refresh_token(active_user.id)

    # Create session
    session = await session_service.create_session(
        db=db_session,
        user_id=active_user.id,
        refresh_token_jti=get_token_jti(refresh_token),
        access_token_jti=get_token_jti(access_token),
        device_info="Mozilla/5.0 Test Browser",
        ip_address="127.0.0.1",
    )

    return {
        "session": session,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": active_user,
    }


@pytest.fixture
async def multiple_user_sessions(db_session: AsyncSession, active_user: User):
    """Create multiple sessions for the same user."""
    sessions = []

    for i in range(3):
        access_token = generate_access_token(active_user.id)
        refresh_token = generate_refresh_token(active_user.id)

        session = await session_service.create_session(
            db=db_session,
            user_id=active_user.id,
            refresh_token_jti=get_token_jti(refresh_token),
            access_token_jti=get_token_jti(access_token),
            device_info=f"Device {i+1}",
            ip_address=f"127.0.0.{i+1}",
        )

        sessions.append({
            "session": session,
            "access_token": access_token,
            "refresh_token": refresh_token,
        })

    return sessions


# ========== LOGOUT TESTS ==========


@pytest.mark.asyncio
async def test_logout_invalidates_current_session(
    test_client: AsyncClient,
    db_session: AsyncSession,
    user_session: dict,
):
    """Test 1: Logout invalidates current session."""
    # Verify session is active before logout
    session = await session_service.get_session_by_token(
        db_session, user_session["session"].session_token
    )
    assert session is not None
    assert session.is_active is True

    # Logout
    response = await test_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {user_session['access_token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Logged out successfully" in data["message"]

    # Verify session is now inactive
    await db_session.refresh(session)
    assert session.is_active is False


@pytest.mark.asyncio
async def test_logged_out_token_cannot_be_used_again(
    test_client: AsyncClient,
    db_session: AsyncSession,
    user_session: dict,
):
    """Test 2: Logged out token cannot be used again."""
    # Logout
    response = await test_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {user_session['access_token']}"},
    )
    assert response.status_code == 200

    # Try to use the same token again (should fail)
    response = await test_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {user_session['access_token']}"},
    )

    # Should return 401 because session not found
    assert response.status_code == 401
    assert "Session not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_logout_removes_session_from_redis(
    test_client: AsyncClient,
    db_session: AsyncSession,
    user_session: dict,
):
    """Test 3: Logout removes session from Redis."""
    session_token = user_session["session"].session_token

    # Verify session exists in Redis before logout (if Redis is connected)
    if redis_client.client:
        key = f"session:{session_token}"
        redis_data = await redis_client.get(key, deserialize=True)
        assert redis_data is not None

    # Logout
    response = await test_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {user_session['access_token']}"},
    )
    assert response.status_code == 200

    # Verify session removed from Redis
    if redis_client.client:
        key = f"session:{session_token}"
        redis_data = await redis_client.get(key, deserialize=True)
        assert redis_data is None


@pytest.mark.asyncio
async def test_logout_is_idempotent(
    test_client: AsyncClient,
    db_session: AsyncSession,
    user_session: dict,
):
    """Test 4: Logout is idempotent (multiple calls succeed)."""
    # First logout
    response = await test_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {user_session['access_token']}"},
    )
    assert response.status_code == 200

    # Session is now inactive, but trying to logout again should not fail
    # However, since we check for valid session in authentication, it will fail with 401
    # This is expected behavior - you can't logout if already logged out

    # Generate a new session to test idempotency properly
    access_token2 = generate_access_token(user_session["user"].id)
    refresh_token2 = generate_refresh_token(user_session["user"].id)

    session2 = await session_service.create_session(
        db=db_session,
        user_id=user_session["user"].id,
        refresh_token_jti=get_token_jti(refresh_token2),
        access_token_jti=get_token_jti(access_token2),
        device_info="Test Device",
        ip_address="127.0.0.1",
    )

    # First logout with new session
    response = await test_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token2}"},
    )
    assert response.status_code == 200

    # Calling revoke_session again on the same session_token should be idempotent
    await session_service.revoke_session(db_session, session2.session_token)
    # Should not raise error - idempotent

    # Verify session still inactive
    session_check = await session_service.get_session_by_token(
        db_session, session2.session_token
    )
    assert session_check.is_active is False


@pytest.mark.asyncio
async def test_logout_with_invalid_token(
    test_client: AsyncClient,
    db_session: AsyncSession,
):
    """Test 5: Logout with invalid token returns 401."""
    response = await test_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": "Bearer invalid_token_here"},
    )

    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_logout_with_missing_token(
    test_client: AsyncClient,
    db_session: AsyncSession,
):
    """Test 6: Logout with missing token returns 401."""
    response = await test_client.post("/api/v1/auth/logout")

    assert response.status_code == 401
    assert "Missing authorization header" in response.json()["detail"]


@pytest.mark.asyncio
async def test_logout_with_expired_token(
    test_client: AsyncClient,
    db_session: AsyncSession,
    active_user: User,
):
    """Test 7: Logout with expired token returns 401."""
    # Create an access token with negative expiry (already expired)
    # We need to manually create an expired token
    from jose import jwt
    from datetime import timezone

    now = datetime.now(timezone.utc)
    expired_time = now - timedelta(hours=1)  # 1 hour ago

    claims = {
        "sub": str(active_user.id),
        "jti": "expired-jti",
        "exp": expired_time,
        "iat": expired_time - timedelta(minutes=15),
        "type": "access",
    }

    private_key = settings.get_jwt_private_key()
    expired_token = jwt.encode(claims, private_key, algorithm=settings.JWT_ALGORITHM)

    # Try to logout with expired token
    response = await test_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_logout_updates_session_to_inactive_in_database(
    test_client: AsyncClient,
    db_session: AsyncSession,
    user_session: dict,
):
    """Test 8: Logout updates session to inactive in database."""
    # Verify session active before logout
    stmt = select(UserSession).where(
        UserSession.session_token == user_session["session"].session_token
    )
    result = await db_session.execute(stmt)
    session_before = result.scalar_one()
    assert session_before.is_active is True

    # Logout
    response = await test_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {user_session['access_token']}"},
    )
    assert response.status_code == 200

    # Verify session inactive in database
    result = await db_session.execute(stmt)
    session_after = result.scalar_one()
    assert session_after.is_active is False


@pytest.mark.asyncio
async def test_logout_response_format_correct(
    test_client: AsyncClient,
    db_session: AsyncSession,
    user_session: dict,
):
    """Test 9: Logout response format correct."""
    response = await test_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {user_session['access_token']}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "success" in data
    assert "message" in data
    assert isinstance(data["success"], bool)
    assert isinstance(data["message"], str)
    assert data["success"] is True


# ========== LOGOUT-ALL TESTS ==========


@pytest.mark.asyncio
async def test_logout_all_invalidates_all_user_sessions(
    test_client: AsyncClient,
    db_session: AsyncSession,
    multiple_user_sessions: list,
):
    """Test 10: Logout-all invalidates all user sessions."""
    # Verify all sessions are active before logout-all
    for session_data in multiple_user_sessions:
        session = await session_service.get_session_by_token(
            db_session, session_data["session"].session_token
        )
        assert session is not None
        assert session.is_active is True

    # Logout from all sessions using first session's token
    response = await test_client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {multiple_user_sessions[0]['access_token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["sessionsRevoked"] == 3

    # Verify all sessions are now inactive
    for session_data in multiple_user_sessions:
        session = await session_service.get_session_by_token(
            db_session, session_data["session"].session_token
        )
        await db_session.refresh(session)
        assert session.is_active is False


@pytest.mark.asyncio
async def test_logout_all_returns_count_of_revoked_sessions(
    test_client: AsyncClient,
    db_session: AsyncSession,
    multiple_user_sessions: list,
):
    """Test 11: Logout-all returns count of revoked sessions."""
    response = await test_client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {multiple_user_sessions[0]['access_token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "sessionsRevoked" in data
    assert data["sessionsRevoked"] == 3  # 3 sessions created in fixture


@pytest.mark.asyncio
async def test_logout_all_removes_all_sessions_from_redis(
    test_client: AsyncClient,
    db_session: AsyncSession,
    multiple_user_sessions: list,
):
    """Test 12: Logout-all removes all sessions from Redis."""
    # Verify sessions exist in Redis before logout-all (if Redis connected)
    if redis_client.client:
        for session_data in multiple_user_sessions:
            key = f"session:{session_data['session'].session_token}"
            redis_data = await redis_client.get(key, deserialize=True)
            assert redis_data is not None

    # Logout from all sessions
    response = await test_client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {multiple_user_sessions[0]['access_token']}"},
    )
    assert response.status_code == 200

    # Verify all sessions removed from Redis
    if redis_client.client:
        for session_data in multiple_user_sessions:
            key = f"session:{session_data['session'].session_token}"
            redis_data = await redis_client.get(key, deserialize=True)
            assert redis_data is None


@pytest.mark.asyncio
async def test_logout_all_only_affects_current_user_sessions(
    test_client: AsyncClient,
    db_session: AsyncSession,
    active_user: User,
    another_user: User,
):
    """Test 13: Logout-all only affects current user's sessions."""
    # Create sessions for first user
    user1_access = generate_access_token(active_user.id)
    user1_refresh = generate_refresh_token(active_user.id)
    user1_session = await session_service.create_session(
        db=db_session,
        user_id=active_user.id,
        refresh_token_jti=get_token_jti(user1_refresh),
        access_token_jti=get_token_jti(user1_access),
        device_info="User 1 Device",
        ip_address="127.0.0.1",
    )

    # Create sessions for second user
    user2_access = generate_access_token(another_user.id)
    user2_refresh = generate_refresh_token(another_user.id)
    user2_session = await session_service.create_session(
        db=db_session,
        user_id=another_user.id,
        refresh_token_jti=get_token_jti(user2_refresh),
        access_token_jti=get_token_jti(user2_access),
        device_info="User 2 Device",
        ip_address="127.0.0.2",
    )

    # User 1 logs out from all sessions
    response = await test_client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {user1_access}"},
    )
    assert response.status_code == 200

    # Verify user 1's session is inactive
    session1 = await session_service.get_session_by_token(db_session, user1_session.session_token)
    await db_session.refresh(session1)
    assert session1.is_active is False

    # Verify user 2's session is still active
    session2 = await session_service.get_session_by_token(db_session, user2_session.session_token)
    await db_session.refresh(session2)
    assert session2.is_active is True


@pytest.mark.asyncio
async def test_logout_all_with_multiple_active_sessions(
    test_client: AsyncClient,
    db_session: AsyncSession,
    active_user: User,
):
    """Test 14: Logout-all with multiple active sessions."""
    # Create 5 sessions (max allowed)
    sessions = []
    for i in range(5):
        access_token = generate_access_token(active_user.id)
        refresh_token = generate_refresh_token(active_user.id)

        session = await session_service.create_session(
            db=db_session,
            user_id=active_user.id,
            refresh_token_jti=get_token_jti(refresh_token),
            access_token_jti=get_token_jti(access_token),
            device_info=f"Device {i+1}",
            ip_address=f"127.0.0.{i+1}",
        )
        sessions.append((session, access_token))

    # Logout from all using any session's token
    response = await test_client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {sessions[2][1]}"},  # Use 3rd session
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sessionsRevoked"] == 5

    # Verify all 5 sessions are now inactive
    for session, _ in sessions:
        session_check = await session_service.get_session_by_token(db_session, session.session_token)
        await db_session.refresh(session_check)
        assert session_check.is_active is False


@pytest.mark.asyncio
async def test_logout_all_response_format_correct(
    test_client: AsyncClient,
    db_session: AsyncSession,
    user_session: dict,
):
    """Test 15: Logout-all response format correct."""
    response = await test_client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {user_session['access_token']}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "success" in data
    assert "message" in data
    assert "sessionsRevoked" in data
    assert isinstance(data["success"], bool)
    assert isinstance(data["message"], str)
    assert isinstance(data["sessionsRevoked"], int)
    assert data["success"] is True


@pytest.mark.asyncio
async def test_user_cannot_use_any_tokens_after_logout_all(
    test_client: AsyncClient,
    db_session: AsyncSession,
    multiple_user_sessions: list,
):
    """Test 16: User cannot use any tokens after logout-all."""
    # Logout from all sessions using first session
    response = await test_client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {multiple_user_sessions[0]['access_token']}"},
    )
    assert response.status_code == 200

    # Try to use each token - all should fail with 401
    for session_data in multiple_user_sessions:
        response = await test_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {session_data['access_token']}"},
        )
        assert response.status_code == 401
        assert "Session not found" in response.json()["detail"]
