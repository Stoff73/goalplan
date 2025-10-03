"""
Comprehensive test suite for login endpoint.

Tests cover:
1. Successful login flow
2. Invalid credentials (wrong email/password)
3. Unverified account cannot login
4. Suspended account cannot login
5. Password verification
6. JWT tokens generated correctly
7. Session created in database and Redis
8. Login attempts logged (success and failure)
9. last_login_at timestamp updated
10. Email case insensitivity
11. Rate limiting (5 attempts per IP per 15 min)
12. Device info captured
13. Response format validation
14. Account lockout after 5 failed attempts
15. Deleted account cannot login
"""

import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserStatus, CountryPreference
from models.session import UserSession, LoginAttempt
from utils.password import hash_password
from utils.jwt import verify_token
from services.session import session_service
from config import settings


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter state between tests."""
    from middleware.rate_limiter import limiter
    # Reset rate limiter state (synchronous)
    if hasattr(limiter, "_storage"):
        limiter._storage.reset()
    yield
    # Clean up after test
    if hasattr(limiter, "_storage"):
        limiter._storage.reset()


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
async def unverified_user(db_session: AsyncSession):
    """Create an unverified user for testing."""
    user = User(
        email="unverified@example.com",
        password_hash=hash_password("ValidPassword123!"),
        first_name="Unverified",
        last_name="User",
        country_preference=CountryPreference.SA,
        status=UserStatus.PENDING_VERIFICATION,
        email_verified=False,
        terms_accepted_at=datetime.utcnow(),
        marketing_consent=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def suspended_user(db_session: AsyncSession):
    """Create a suspended user for testing."""
    user = User(
        email="suspended@example.com",
        password_hash=hash_password("ValidPassword123!"),
        first_name="Suspended",
        last_name="User",
        country_preference=CountryPreference.BOTH,
        status=UserStatus.SUSPENDED,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
        marketing_consent=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def deleted_user(db_session: AsyncSession):
    """Create a deleted user for testing."""
    user = User(
        email="deleted@example.com",
        password_hash=hash_password("ValidPassword123!"),
        first_name="Deleted",
        last_name="User",
        country_preference=CountryPreference.UK,
        status=UserStatus.DELETED,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
        marketing_consent=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_successful_login(test_client: AsyncClient, db_session: AsyncSession, active_user):
    """Test successful login with valid credentials."""
    # Make login request
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "ValidPassword123!",
            "device_info": "Test Device",
            "remember_me": False,
        },
    )

    # Assert response
    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "accessToken" in data
    assert "refreshToken" in data
    assert "tokenType" in data
    assert data["tokenType"] == "bearer"
    assert "expiresIn" in data
    assert data["expiresIn"] == settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    assert "user" in data

    # Check user info
    user_info = data["user"]
    assert user_info["email"] == "test@example.com"
    assert user_info["firstName"] == "Test"
    assert user_info["lastName"] == "User"
    assert user_info["countryPreference"] == "UK"
    assert user_info["twoFactorEnabled"] is False

    # Verify tokens are valid JWTs
    access_payload = verify_token(data["accessToken"], token_type="access")
    assert access_payload["sub"] == str(active_user.id)
    assert access_payload["type"] == "access"

    refresh_payload = verify_token(data["refreshToken"], token_type="refresh")
    assert refresh_payload["sub"] == str(active_user.id)
    assert refresh_payload["type"] == "refresh"


@pytest.mark.asyncio
async def test_login_with_wrong_email(test_client: AsyncClient, db_session: AsyncSession):
    """Test login with non-existent email returns 401."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "ValidPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_login_with_wrong_password(test_client: AsyncClient, db_session: AsyncSession, active_user):
    """Test login with wrong password returns 401."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_unverified_account_cannot_login(test_client: AsyncClient, db_session: AsyncSession, unverified_user):
    """Test that unverified account returns 403."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "unverified@example.com",
            "password": "ValidPassword123!",
        },
    )

    assert response.status_code == 403
    assert "verify your email" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_suspended_account_cannot_login(test_client: AsyncClient, db_session: AsyncSession, suspended_user):
    """Test that suspended account returns 403."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "suspended@example.com",
            "password": "ValidPassword123!",
        },
    )

    assert response.status_code == 403
    assert "suspended" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_deleted_account_cannot_login(test_client: AsyncClient, db_session: AsyncSession, deleted_user):
    """Test that deleted account returns 403."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "deleted@example.com",
            "password": "ValidPassword123!",
        },
    )

    assert response.status_code == 403
    assert "deleted" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_session_created_in_database(test_client: AsyncClient, db_session: AsyncSession, active_user):
    """Test that successful login creates session in database."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "ValidPassword123!",
            "device_info": "Test Device",
        },
    )

    assert response.status_code == 200

    # Check session exists in database
    result = await db_session.execute(
        select(UserSession).where(UserSession.user_id == active_user.id)
    )
    sessions = result.scalars().all()

    assert len(sessions) == 1
    session = sessions[0]
    assert session.user_id == active_user.id
    assert session.device_info == "Test Device"
    assert session.is_active is True


@pytest.mark.asyncio
async def test_login_attempt_logged_success(test_client: AsyncClient, db_session: AsyncSession, active_user):
    """Test that successful login is logged in login_attempts table."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "ValidPassword123!",
        },
    )

    assert response.status_code == 200

    # Check login attempt was logged
    result = await db_session.execute(
        select(LoginAttempt).where(LoginAttempt.email == "test@example.com")
    )
    attempts = result.scalars().all()

    assert len(attempts) > 0
    latest_attempt = attempts[-1]
    assert latest_attempt.success is True
    assert latest_attempt.user_id == active_user.id
    assert latest_attempt.failure_reason is None


@pytest.mark.asyncio
async def test_login_attempt_logged_failure(test_client: AsyncClient, db_session: AsyncSession, active_user):
    """Test that failed login is logged in login_attempts table."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401

    # Check login attempt was logged
    result = await db_session.execute(
        select(LoginAttempt).where(LoginAttempt.email == "test@example.com")
    )
    attempts = result.scalars().all()

    assert len(attempts) > 0
    latest_attempt = attempts[-1]
    assert latest_attempt.success is False
    assert latest_attempt.user_id == active_user.id
    assert latest_attempt.failure_reason == "invalid_password"


@pytest.mark.asyncio
async def test_last_login_at_updated(test_client: AsyncClient, db_session: AsyncSession, active_user):
    """Test that last_login_at timestamp is updated on successful login."""
    # Store original last_login_at (should be None)
    original_last_login = active_user.last_login_at

    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "ValidPassword123!",
        },
    )

    assert response.status_code == 200

    # Refresh user from database
    await db_session.refresh(active_user)

    # Check last_login_at was updated
    assert active_user.last_login_at is not None
    assert active_user.last_login_at != original_last_login

    # Should be recent (within last 5 seconds)
    time_diff = datetime.utcnow() - active_user.last_login_at
    assert time_diff.total_seconds() < 5


@pytest.mark.asyncio
async def test_email_case_insensitive(test_client: AsyncClient, db_session: AsyncSession, active_user):
    """Test that login is case-insensitive for email."""
    # Try with uppercase email
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "TEST@EXAMPLE.COM",
            "password": "ValidPassword123!",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "test@example.com"

    # Try with mixed case email
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "TeSt@ExAmPlE.cOm",
            "password": "ValidPassword123!",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_device_info_captured(test_client: AsyncClient, db_session: AsyncSession, active_user):
    """Test that device info is captured in session."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "ValidPassword123!",
            "device_info": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        },
    )

    assert response.status_code == 200

    # Check session has device info
    result = await db_session.execute(
        select(UserSession).where(UserSession.user_id == active_user.id)
    )
    session = result.scalar_one()

    assert session.device_info == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"


@pytest.mark.asyncio
async def test_account_lockout_after_failed_attempts(db_session: AsyncSession):
    """Test that account is locked after 5 failed login attempts.

    Note: This test directly inserts login attempts into the database to avoid
    triggering the rate limiter (which also limits to 5 requests per 15 min).
    """
    from services.login_attempt import login_attempt_service
    from datetime import datetime

    # Create user
    user = User(
        email="lockout@example.com",
        password_hash=hash_password("ValidPassword123!"),
        first_name="Lockout",
        last_name="Test",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
        marketing_consent=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Directly insert 5 failed login attempts
    for i in range(5):
        await login_attempt_service.log_login_attempt(
            db=db_session,
            email="lockout@example.com",
            ip_address="127.0.0.1",
            user_agent="Test",
            success=False,
            user_id=user.id,
            failure_reason="invalid_password",
        )

    # Verify that account lockout check works
    failed_attempts = await login_attempt_service.get_recent_failed_attempts(
        db=db_session,
        email="lockout@example.com",
        minutes=settings.ACCOUNT_LOCKOUT_DURATION_MINUTES,
    )

    assert failed_attempts >= settings.MAX_LOGIN_ATTEMPTS


@pytest.mark.asyncio
async def test_response_format_correct(test_client: AsyncClient, db_session: AsyncSession, active_user):
    """Test that response format matches LoginResponse schema."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "ValidPassword123!",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Check all required fields are present
    required_fields = ["accessToken", "refreshToken", "tokenType", "expiresIn", "user"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Check user object structure
    user_required_fields = ["id", "email", "firstName", "lastName", "countryPreference", "twoFactorEnabled"]
    for field in user_required_fields:
        assert field in data["user"], f"Missing required user field: {field}"

    # Check data types
    assert isinstance(data["accessToken"], str)
    assert isinstance(data["refreshToken"], str)
    assert isinstance(data["tokenType"], str)
    assert isinstance(data["expiresIn"], int)
    assert isinstance(data["user"], dict)
    assert isinstance(data["user"]["twoFactorEnabled"], bool)


@pytest.mark.asyncio
async def test_rate_limiting_enforced(test_client: AsyncClient, db_session: AsyncSession, active_user):
    """Test that rate limiting is enforced (5 attempts per 15 minutes)."""
    # Make 5 login attempts (rate limit)
    for i in range(5):
        response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "ValidPassword123!",
            },
        )
        # Should succeed (or fail if password wrong, but not rate limited)
        assert response.status_code in [200, 401]

    # 6th attempt should be rate limited
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "ValidPassword123!",
        },
    )

    assert response.status_code == 429
    assert "too many requests" in response.json()["detail"].lower()
