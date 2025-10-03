"""
Tests for email verification API endpoint.

This module tests the GET /api/v1/auth/verify-email endpoint including:
- Valid token verification
- Expired token handling
- Invalid token handling
- Already verified (idempotent) behavior
- User status updates
- Token used flag updates

Test Coverage:
- Happy path verification
- Token expiration
- Invalid/non-existent tokens
- Idempotent verification (already verified)
- Database state changes
"""

import pytest
import uuid
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, EmailVerificationToken, UserStatus, CountryPreference


class TestEmailVerification:
    """Tests for GET /api/v1/auth/verify-email endpoint."""

    @pytest.fixture
    async def unverified_user_with_token(self, db_session: AsyncSession):
        """Create an unverified user with a valid verification token."""
        # Create user
        user = User(
            email="unverified@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            country_preference=CountryPreference.UK,
            status=UserStatus.PENDING_VERIFICATION,
            email_verified=False,
            terms_accepted_at=datetime.utcnow(),
            marketing_consent=False,
        )
        db_session.add(user)
        await db_session.flush()

        # Create verification token
        token = str(uuid.uuid4())
        verification_token = EmailVerificationToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=24),
            used=False,
        )
        db_session.add(verification_token)
        await db_session.commit()

        return {"user": user, "token": token, "token_obj": verification_token}

    @pytest.mark.asyncio
    async def test_valid_token_verifies_successfully(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        unverified_user_with_token: dict,
    ):
        """Test that a valid token successfully verifies the user's email."""
        # Arrange
        token = unverified_user_with_token["token"]
        user_id = unverified_user_with_token["user"].id

        # Act
        response = await test_client.get(
            f"/api/v1/auth/verify-email?token={token}"
        )

        # Assert response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "verified successfully" in data["message"].lower()

        # Assert user status updated
        stmt = select(User).where(User.id == user_id)
        result = await db_session.execute(stmt)
        user = result.scalar_one()

        assert user.email_verified is True
        assert user.status == UserStatus.ACTIVE

        # Assert token marked as used
        stmt = select(EmailVerificationToken).where(
            EmailVerificationToken.token == token
        )
        result = await db_session.execute(stmt)
        token_obj = result.scalar_one()
        assert token_obj.used is True

    @pytest.mark.asyncio
    async def test_expired_token_returns_error(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Test that an expired token returns 400 error."""
        # Arrange: Create user with expired token
        user = User(
            email="expired@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            country_preference=CountryPreference.UK,
            status=UserStatus.PENDING_VERIFICATION,
            email_verified=False,
            terms_accepted_at=datetime.utcnow(),
            marketing_consent=False,
        )
        db_session.add(user)
        await db_session.flush()

        # Create expired token (25 hours ago)
        token = str(uuid.uuid4())
        verification_token = EmailVerificationToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() - timedelta(hours=1),  # Expired
            used=False,
        )
        db_session.add(verification_token)
        await db_session.commit()

        # Act
        response = await test_client.get(
            f"/api/v1/auth/verify-email?token={token}"
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "expired" in data["detail"].lower()

        # User should still be unverified
        stmt = select(User).where(User.id == user.id)
        result = await db_session.execute(stmt)
        user = result.scalar_one()
        assert user.email_verified is False
        assert user.status == UserStatus.PENDING_VERIFICATION

    @pytest.mark.asyncio
    async def test_invalid_token_returns_error(
        self,
        test_client: AsyncClient,
    ):
        """Test that an invalid/non-existent token returns 400 error."""
        # Arrange: Use a random UUID that doesn't exist
        invalid_token = str(uuid.uuid4())

        # Act
        response = await test_client.get(
            f"/api/v1/auth/verify-email?token={invalid_token}"
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "invalid" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_already_verified_returns_success_idempotent(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Test that verifying an already verified user returns success (idempotent)."""
        # Arrange: Create already verified user
        user = User(
            email="already.verified@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            country_preference=CountryPreference.UK,
            status=UserStatus.ACTIVE,  # Already active
            email_verified=True,  # Already verified
            terms_accepted_at=datetime.utcnow(),
            marketing_consent=False,
        )
        db_session.add(user)
        await db_session.flush()

        # Create verification token (still valid)
        token = str(uuid.uuid4())
        verification_token = EmailVerificationToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=24),
            used=True,  # Already used
        )
        db_session.add(verification_token)
        await db_session.commit()

        # Act
        response = await test_client.get(
            f"/api/v1/auth/verify-email?token={token}"
        )

        # Assert: Returns success (idempotent)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "already been verified" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_multiple_verification_attempts_idempotent(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        unverified_user_with_token: dict,
    ):
        """Test that multiple verification attempts are idempotent."""
        # Arrange
        token = unverified_user_with_token["token"]

        # Act: First verification
        response1 = await test_client.get(
            f"/api/v1/auth/verify-email?token={token}"
        )
        assert response1.status_code == 200
        assert "verified successfully" in response1.json()["message"].lower()

        # Refresh session to get updated user
        await db_session.rollback()

        # Act: Second verification (should be idempotent)
        response2 = await test_client.get(
            f"/api/v1/auth/verify-email?token={token}"
        )

        # Assert: Second attempt returns success
        assert response2.status_code == 200
        data = response2.json()
        assert data["success"] is True
        assert "already been verified" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_user_status_changes_to_active(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        unverified_user_with_token: dict,
    ):
        """Test that user status changes from PENDING_VERIFICATION to ACTIVE."""
        # Arrange
        token = unverified_user_with_token["token"]
        user_id = unverified_user_with_token["user"].id

        # Verify initial state
        stmt = select(User).where(User.id == user_id)
        result = await db_session.execute(stmt)
        user_before = result.scalar_one()
        assert user_before.status == UserStatus.PENDING_VERIFICATION

        # Act
        response = await test_client.get(
            f"/api/v1/auth/verify-email?token={token}"
        )

        # Assert
        assert response.status_code == 200

        # Check updated state
        await db_session.rollback()  # Refresh session
        stmt = select(User).where(User.id == user_id)
        result = await db_session.execute(stmt)
        user_after = result.scalar_one()
        assert user_after.status == UserStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_email_verified_flag_set_to_true(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        unverified_user_with_token: dict,
    ):
        """Test that email_verified flag is set to True."""
        # Arrange
        token = unverified_user_with_token["token"]
        user_id = unverified_user_with_token["user"].id

        # Verify initial state
        stmt = select(User).where(User.id == user_id)
        result = await db_session.execute(stmt)
        user_before = result.scalar_one()
        assert user_before.email_verified is False

        # Act
        response = await test_client.get(
            f"/api/v1/auth/verify-email?token={token}"
        )

        # Assert
        assert response.status_code == 200

        # Check updated state
        await db_session.rollback()  # Refresh session
        stmt = select(User).where(User.id == user_id)
        result = await db_session.execute(stmt)
        user_after = result.scalar_one()
        assert user_after.email_verified is True

    @pytest.mark.asyncio
    async def test_token_marked_as_used(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        unverified_user_with_token: dict,
    ):
        """Test that verification token is marked as used after verification."""
        # Arrange
        token = unverified_user_with_token["token"]

        # Verify initial state
        stmt = select(EmailVerificationToken).where(
            EmailVerificationToken.token == token
        )
        result = await db_session.execute(stmt)
        token_before = result.scalar_one()
        assert token_before.used is False

        # Act
        response = await test_client.get(
            f"/api/v1/auth/verify-email?token={token}"
        )

        # Assert
        assert response.status_code == 200

        # Check updated state
        await db_session.rollback()  # Refresh session
        stmt = select(EmailVerificationToken).where(
            EmailVerificationToken.token == token
        )
        result = await db_session.execute(stmt)
        token_after = result.scalar_one()
        assert token_after.used is True

    @pytest.mark.asyncio
    async def test_missing_token_parameter_returns_error(
        self,
        test_client: AsyncClient,
    ):
        """Test that missing token parameter returns validation error."""
        # Act: Call without token parameter
        response = await test_client.get("/api/v1/auth/verify-email")

        # Assert: Returns 422 validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_empty_token_returns_error(
        self,
        test_client: AsyncClient,
    ):
        """Test that empty token string returns error."""
        # Act
        response = await test_client.get("/api/v1/auth/verify-email?token=")

        # Assert: Returns 400 or 422 error
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_malformed_token_returns_error(
        self,
        test_client: AsyncClient,
    ):
        """Test that malformed token (not UUID format) returns error."""
        # Act: Use obviously invalid token format
        response = await test_client.get(
            "/api/v1/auth/verify-email?token=not-a-valid-uuid"
        )

        # Assert: Returns 400 (invalid token)
        assert response.status_code == 400
        data = response.json()
        assert "invalid" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_verification_within_24_hour_window(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Test that token is valid within the 24-hour expiration window."""
        # Arrange: Create user with token expiring in 1 hour
        user = User(
            email="expires.soon@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            country_preference=CountryPreference.UK,
            status=UserStatus.PENDING_VERIFICATION,
            email_verified=False,
            terms_accepted_at=datetime.utcnow(),
            marketing_consent=False,
        )
        db_session.add(user)
        await db_session.flush()

        # Token expires in 1 hour (still valid)
        token = str(uuid.uuid4())
        verification_token = EmailVerificationToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            used=False,
        )
        db_session.add(verification_token)
        await db_session.commit()

        # Act
        response = await test_client.get(
            f"/api/v1/auth/verify-email?token={token}"
        )

        # Assert: Should succeed (still within 24-hour window)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_verification_exactly_at_expiration_boundary(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Test token that expires right at the boundary (edge case)."""
        # Arrange: Create token that expires in 1 second
        user = User(
            email="boundary@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            country_preference=CountryPreference.UK,
            status=UserStatus.PENDING_VERIFICATION,
            email_verified=False,
            terms_accepted_at=datetime.utcnow(),
            marketing_consent=False,
        )
        db_session.add(user)
        await db_session.flush()

        # Token expires in 1 second
        token = str(uuid.uuid4())
        verification_token = EmailVerificationToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(seconds=1),
            used=False,
        )
        db_session.add(verification_token)
        await db_session.commit()

        # Act immediately (should still be valid)
        response = await test_client.get(
            f"/api/v1/auth/verify-email?token={token}"
        )

        # Assert: Should succeed (still valid)
        assert response.status_code == 200
