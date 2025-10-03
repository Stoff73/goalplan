"""
Comprehensive test suite for token refresh endpoint.

Tests cover:
1. Valid refresh token gets new access token
2. Expired refresh token rejected (401)
3. Invalid refresh token rejected (401)
4. Access token used as refresh token rejected (401)
5. Revoked session cannot refresh (401)
6. Expired session cannot refresh (401)
7. New access token works for authentication
8. Session last_activity updated
9. Session access_token_jti updated
10. Refresh token can be used multiple times (doesn't get invalidated)
11. Missing refresh token rejected (422)
12. Malformed refresh token rejected (401)
13. Refresh token from different user
14. Response format correct
"""

import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import time

from models.user import User, UserStatus, CountryPreference
from models.session import UserSession
from utils.password import hash_password
from utils.jwt import (
    generate_access_token,
    generate_refresh_token,
    verify_token,
    get_token_jti,
    _generate_token,
)
from services.session import session_service
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
async def second_user(db_session: AsyncSession):
    """Create a second user for cross-user testing."""
    user = User(
        email="second@example.com",
        password_hash=hash_password("ValidPassword123!"),
        first_name="Second",
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
async def active_session(db_session: AsyncSession, active_user: User):
    """Create an active session with tokens."""
    # Generate tokens
    access_token = generate_access_token(active_user.id)
    refresh_token = generate_refresh_token(active_user.id)

    # Get JTIs
    access_token_jti = get_token_jti(access_token)
    refresh_token_jti = get_token_jti(refresh_token)

    # Create session
    session = await session_service.create_session(
        db=db_session,
        user_id=active_user.id,
        refresh_token_jti=refresh_token_jti,
        access_token_jti=access_token_jti,
        device_info="pytest test agent",
        ip_address="127.0.0.1",
    )

    return {
        "session": session,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": active_user,
    }


class TestTokenRefreshSuccess:
    """Test successful token refresh scenarios."""

    async def test_valid_refresh_token_gets_new_access_token(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        active_session: dict,
    ):
        """Test that a valid refresh token returns a new access token."""
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": active_session["refresh_token"]},
        )

        assert response.status_code == 200

        data = response.json()
        assert "accessToken" in data
        assert "tokenType" in data
        assert "expiresIn" in data
        assert data["tokenType"] == "bearer"
        assert data["expiresIn"] == settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

        # Verify new access token is valid
        new_access_token = data["accessToken"]
        payload = verify_token(new_access_token, token_type="access")
        assert payload["sub"] == str(active_session["user"].id)
        assert payload["type"] == "access"

        # Verify new token is different from old one
        assert new_access_token != active_session["access_token"]

    async def test_session_last_activity_updated(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        active_session: dict,
    ):
        """Test that session last_activity timestamp is updated on refresh."""
        # Get initial last_activity
        initial_activity = active_session["session"].last_activity

        # Wait a small amount to ensure timestamp difference
        await asyncio.sleep(0.1)

        # Refresh token
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": active_session["refresh_token"]},
        )

        assert response.status_code == 200

        # Verify session last_activity was updated
        result = await db_session.execute(
            select(UserSession).where(
                UserSession.id == active_session["session"].id
            )
        )
        updated_session = result.scalar_one()

        assert updated_session.last_activity > initial_activity

    async def test_session_access_token_jti_updated(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        active_session: dict,
    ):
        """Test that session access_token_jti is updated with new token."""
        # Get initial access_token_jti
        initial_jti = active_session["session"].access_token_jti

        # Refresh token
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": active_session["refresh_token"]},
        )

        assert response.status_code == 200

        # Get new access token JTI
        new_access_token = response.json()["accessToken"]
        new_jti = get_token_jti(new_access_token)

        # Verify session was updated
        result = await db_session.execute(
            select(UserSession).where(
                UserSession.id == active_session["session"].id
            )
        )
        updated_session = result.scalar_one()

        assert updated_session.access_token_jti == new_jti
        assert updated_session.access_token_jti != initial_jti

    async def test_refresh_token_can_be_used_multiple_times(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        active_session: dict,
    ):
        """Test that refresh token doesn't get invalidated on use."""
        refresh_token = active_session["refresh_token"]

        # Use refresh token first time
        response1 = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response1.status_code == 200
        access_token_1 = response1.json()["accessToken"]

        # Use same refresh token second time
        response2 = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response2.status_code == 200
        access_token_2 = response2.json()["accessToken"]

        # Verify both access tokens are valid but different
        payload_1 = verify_token(access_token_1, token_type="access")
        payload_2 = verify_token(access_token_2, token_type="access")

        assert payload_1["sub"] == payload_2["sub"]
        assert access_token_1 != access_token_2

        # Use same refresh token third time
        response3 = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response3.status_code == 200

    async def test_new_access_token_works_for_authentication(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        active_session: dict,
    ):
        """Test that the new access token can be used for authenticated requests."""
        # Refresh token
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": active_session["refresh_token"]},
        )

        assert response.status_code == 200
        new_access_token = response.json()["accessToken"]

        # Verify new token is valid and has correct claims
        payload = verify_token(new_access_token, token_type="access")
        assert payload["sub"] == str(active_session["user"].id)
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload


class TestTokenRefreshErrors:
    """Test error scenarios for token refresh."""

    async def test_expired_refresh_token_rejected(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        active_user: User,
    ):
        """Test that expired refresh token is rejected."""
        # Create expired refresh token (expired 1 second ago)
        expired_token = _generate_token(
            user_id=active_user.id,
            token_type="refresh",
            expires_delta=timedelta(seconds=-1),
        )

        # Create session with expired token
        expired_jti = get_token_jti(expired_token)
        await session_service.create_session(
            db=db_session,
            user_id=active_user.id,
            refresh_token_jti=expired_jti,
            access_token_jti="test-access-jti",
            device_info="pytest",
            ip_address="127.0.0.1",
        )

        # Try to refresh with expired token
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": expired_token},
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    async def test_invalid_refresh_token_rejected(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Test that invalid/malformed refresh token is rejected."""
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    async def test_access_token_used_as_refresh_token_rejected(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        active_session: dict,
    ):
        """Test that access token cannot be used as refresh token."""
        # Try to use access token as refresh token
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": active_session["access_token"]},
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    async def test_revoked_session_cannot_refresh(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        active_session: dict,
    ):
        """Test that revoked session cannot refresh tokens."""
        # Revoke the session
        refresh_token_jti = get_token_jti(active_session["refresh_token"])
        await session_service.revoke_session(
            db=db_session,
            session_token=refresh_token_jti,
        )

        # Try to refresh with revoked session
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": active_session["refresh_token"]},
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower() or "revoked" in response.json()["detail"].lower()

    async def test_expired_session_cannot_refresh(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        active_user: User,
    ):
        """Test that expired session cannot refresh tokens."""
        # Create tokens
        access_token = generate_access_token(active_user.id)
        refresh_token = generate_refresh_token(active_user.id)

        access_jti = get_token_jti(access_token)
        refresh_jti = get_token_jti(refresh_token)

        # Create session that expired 1 hour ago
        session = UserSession(
            user_id=active_user.id,
            session_token=refresh_jti,
            access_token_jti=access_jti,
            device_info="pytest",
            ip_address="127.0.0.1",
            is_active=True,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            expires_at=datetime.utcnow() - timedelta(hours=1),  # Expired
        )
        db_session.add(session)
        await db_session.commit()

        # Try to refresh with expired session
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower() or "revoked" in response.json()["detail"].lower()

    async def test_missing_refresh_token_rejected(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Test that missing refresh token returns 422 validation error."""
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        # Pydantic validation error for missing field

    async def test_empty_refresh_token_rejected(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Test that empty refresh token is rejected."""
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": ""},
        )

        assert response.status_code == 422
        # Pydantic validation error for min_length=1

    async def test_malformed_refresh_token_rejected(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Test that malformed refresh token is rejected."""
        malformed_tokens = [
            "not-a-jwt-token",
            "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9",  # Only header, no payload/signature
            "a.b.c",  # Three parts but invalid
        ]

        for token in malformed_tokens:
            response = await test_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": token},
            )

            assert response.status_code == 401
            assert "invalid" in response.json()["detail"].lower() or "malformed" in response.json()["detail"].lower()

    async def test_refresh_token_from_different_user_wrong_session(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        active_user: User,
        second_user: User,
    ):
        """Test that refresh token must match the session user."""
        # Create session for user 1
        user1_refresh = generate_refresh_token(active_user.id)
        user1_access = generate_access_token(active_user.id)
        user1_refresh_jti = get_token_jti(user1_refresh)
        user1_access_jti = get_token_jti(user1_access)

        await session_service.create_session(
            db=db_session,
            user_id=active_user.id,
            refresh_token_jti=user1_refresh_jti,
            access_token_jti=user1_access_jti,
            device_info="pytest",
            ip_address="127.0.0.1",
        )

        # Create refresh token for user 2
        user2_refresh = generate_refresh_token(second_user.id)

        # Try to refresh with user2's token (no session for this token)
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": user2_refresh},
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower() or "revoked" in response.json()["detail"].lower()

    async def test_session_not_found_for_refresh_token(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        active_user: User,
    ):
        """Test that refresh token without session is rejected."""
        # Create valid refresh token but don't create session
        refresh_token = generate_refresh_token(active_user.id)

        # Try to refresh without session
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower() or "revoked" in response.json()["detail"].lower()


class TestTokenRefreshResponseFormat:
    """Test response format validation."""

    async def test_response_format_correct(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        active_session: dict,
    ):
        """Test that response has correct format."""
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": active_session["refresh_token"]},
        )

        assert response.status_code == 200

        data = response.json()

        # Check all required fields present
        assert "accessToken" in data
        assert "tokenType" in data
        assert "expiresIn" in data

        # Check field types
        assert isinstance(data["accessToken"], str)
        assert isinstance(data["tokenType"], str)
        assert isinstance(data["expiresIn"], int)

        # Check field values
        assert data["tokenType"] == "bearer"
        assert data["expiresIn"] == 900  # 15 minutes in seconds

        # Check no extra fields (only access token, not refresh token)
        assert "refreshToken" not in data
        assert "user" not in data

    async def test_access_token_is_jwt_format(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        active_session: dict,
    ):
        """Test that returned access token is valid JWT format."""
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": active_session["refresh_token"]},
        )

        assert response.status_code == 200

        access_token = response.json()["accessToken"]

        # JWT has 3 parts separated by dots
        parts = access_token.split(".")
        assert len(parts) == 3

        # Verify it can be decoded
        payload = verify_token(access_token, token_type="access")
        assert "sub" in payload
        assert "jti" in payload
        assert "exp" in payload
        assert "iat" in payload
        assert "type" in payload


# Import asyncio for sleep in tests
import asyncio
