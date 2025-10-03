"""
Tests for user registration API endpoint.

This module tests the POST /api/v1/auth/register endpoint including:
- Successful registration flow
- Duplicate email handling
- Password validation
- Email format validation
- Terms acceptance validation
- Token generation and storage
- Email queueing
- Security (no user existence leakage)

Test Coverage:
- Happy path registration
- Validation errors (weak password, invalid email, terms not accepted)
- Duplicate email handling (security - no leakage)
- Verification token creation
- Email service integration
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, EmailVerificationToken, UserStatus, CountryPreference


class TestUserRegistration:
    """Tests for POST /api/v1/auth/register endpoint."""

    @pytest.fixture(autouse=True)
    async def reset_rate_limiter(self):
        """Reset rate limiter before each test to avoid state leakage."""
        from middleware.rate_limiter import limiter
        # Reset the in-memory storage
        if hasattr(limiter._storage, 'storage'):
            limiter._storage.storage.clear()
        yield
        # Clean up after test
        if hasattr(limiter._storage, 'storage'):
            limiter._storage.storage.clear()

    @pytest.fixture
    def valid_registration_data(self):
        """Provide valid registration data for tests."""
        return {
            "email": "test@example.com",
            "password": "SecurePass123!@#",
            "first_name": "John",
            "last_name": "Doe",
            "country": "UK",
            "terms_accepted": True,
            "marketing_consent": False,
        }

    @pytest.mark.asyncio
    async def test_successful_registration(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        valid_registration_data: dict,
    ):
        """Test successful user registration flow."""
        # Mock the email service to prevent actual email sending
        with patch("api.v1.auth.registration.email_service.send_verification_email", new_callable=AsyncMock) as mock_email:
            # Act
            response = await test_client.post(
                "/api/v1/auth/register",
                json=valid_registration_data,
            )

            # Assert response
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            # In dev mode (REQUIRE_EMAIL_VERIFICATION=False), users can log in immediately
            assert "you can now log in" in data["message"].lower()
            assert "userId" in data
            assert uuid.UUID(data["userId"])  # Valid UUID

            # Assert user created in database
            stmt = select(User).where(User.email == valid_registration_data["email"].lower())
            result = await db_session.execute(stmt)
            user = result.scalar_one_or_none()

            assert user is not None
            assert user.email == valid_registration_data["email"].lower()
            assert user.first_name == valid_registration_data["first_name"]
            assert user.last_name == valid_registration_data["last_name"]
            assert user.country_preference == CountryPreference.UK
            # In dev mode, users are auto-activated
            assert user.status == UserStatus.ACTIVE
            assert user.email_verified is True
            assert user.password_hash is not None
            assert user.password_hash != valid_registration_data["password"]  # Hashed
            assert user.marketing_consent is False
            assert user.terms_accepted_at is not None

            # In dev mode, no verification token is created
            stmt = select(EmailVerificationToken).where(
                EmailVerificationToken.user_id == user.id
            )
            result = await db_session.execute(stmt)
            token = result.scalar_one_or_none()

            assert token is None  # No token in dev mode

            # In dev mode, no email is sent
            mock_email.assert_not_called()

    @pytest.mark.asyncio
    async def test_duplicate_email_does_not_leak_existence(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        valid_registration_data: dict,
    ):
        """Test that duplicate email returns success (security - no user enumeration)."""
        # Arrange: Create existing user
        existing_user = User(
            email=valid_registration_data["email"].lower(),
            password_hash="existing_hash",
            first_name="Existing",
            last_name="User",
            country_preference=CountryPreference.UK,
            status=UserStatus.ACTIVE,
            email_verified=True,
            terms_accepted_at=datetime.utcnow(),
            marketing_consent=False,
        )
        db_session.add(existing_user)
        await db_session.commit()

        # Act: Try to register with same email
        with patch("api.v1.auth.registration.email_service.send_verification_email", new_callable=AsyncMock):
            response = await test_client.post(
                "/api/v1/auth/register",
                json=valid_registration_data,
            )

        # Assert: Returns success (security best practice)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "check your email" in data["message"].lower()

        # Assert: No new user created
        stmt = select(User).where(User.email == valid_registration_data["email"].lower())
        result = await db_session.execute(stmt)
        users = result.scalars().all()
        assert len(users) == 1  # Only the original user

    @pytest.mark.asyncio
    async def test_weak_password_rejected(
        self,
        test_client: AsyncClient,
        valid_registration_data: dict,
    ):
        """Test that weak password is rejected with validation error."""
        # Arrange: Weak passwords (various scenarios)
        weak_passwords = [
            "short1!A",  # Too short (< 12 chars)
            "nouppercase1!",  # No uppercase
            "NOLOWERCASE1!",  # No lowercase
            "NoDigitsHere!",  # No digits
            "NoSpecialChar1",  # No special character
            "12345678901",  # Only digits
        ]

        for weak_password in weak_passwords:
            data = valid_registration_data.copy()
            data["password"] = weak_password

            # Act
            response = await test_client.post(
                "/api/v1/auth/register",
                json=data,
            )

            # Assert
            assert response.status_code == 422  # Validation error
            error_data = response.json()
            assert "detail" in error_data

    @pytest.mark.asyncio
    async def test_invalid_email_format_rejected(
        self,
        test_client: AsyncClient,
        valid_registration_data: dict,
    ):
        """Test that invalid email format is rejected."""
        # Arrange: Invalid email formats
        invalid_emails = [
            "notanemail",
            "missing@domain",
            "@nodomain.com",
            "spaces in@email.com",
            "",
        ]

        for invalid_email in invalid_emails:
            data = valid_registration_data.copy()
            data["email"] = invalid_email

            # Act
            response = await test_client.post(
                "/api/v1/auth/register",
                json=data,
            )

            # Assert
            assert response.status_code == 422  # Validation error
            error_data = response.json()
            assert "detail" in error_data

    @pytest.mark.asyncio
    async def test_terms_not_accepted_rejected(
        self,
        test_client: AsyncClient,
        valid_registration_data: dict,
    ):
        """Test that registration without accepting terms is rejected."""
        # Arrange
        data = valid_registration_data.copy()
        data["terms_accepted"] = False

        # Act
        response = await test_client.post(
            "/api/v1/auth/register",
            json=data,
        )

        # Assert
        assert response.status_code == 422  # Validation error
        error_data = response.json()
        assert "detail" in error_data
        # Check that error message mentions terms
        error_str = str(error_data).lower()
        assert "terms" in error_str

    @pytest.mark.asyncio
    async def test_missing_required_fields_rejected(
        self,
        test_client: AsyncClient,
        valid_registration_data: dict,
    ):
        """Test that missing required fields are rejected."""
        required_fields = ["email", "password", "first_name", "last_name", "country", "terms_accepted"]

        for field in required_fields:
            # Arrange: Remove one required field
            data = valid_registration_data.copy()
            del data[field]

            # Act
            response = await test_client.post(
                "/api/v1/auth/register",
                json=data,
            )

            # Assert
            assert response.status_code == 422  # Validation error
            error_data = response.json()
            assert "detail" in error_data

    @pytest.mark.asyncio
    async def test_invalid_country_rejected(
        self,
        test_client: AsyncClient,
        valid_registration_data: dict,
    ):
        """Test that invalid country preference is rejected."""
        # Arrange
        data = valid_registration_data.copy()
        data["country"] = "INVALID"

        # Act
        response = await test_client.post(
            "/api/v1/auth/register",
            json=data,
        )

        # Assert
        assert response.status_code == 422  # Validation error
        error_data = response.json()
        assert "detail" in error_data

    @pytest.mark.asyncio
    async def test_verification_token_generated_and_stored(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        valid_registration_data: dict,
    ):
        """Test that verification token is generated and stored correctly."""
        # Enable email verification for this test
        from config import settings
        with patch.object(settings, 'REQUIRE_EMAIL_VERIFICATION', True):
            # Act
            with patch("api.v1.auth.registration.email_service.send_verification_email", new_callable=AsyncMock):
                response = await test_client.post(
                    "/api/v1/auth/register",
                    json=valid_registration_data,
                )

            # Assert
            assert response.status_code == 201
            user_id = response.json()["userId"]

            # Check token in database
            stmt = select(EmailVerificationToken).where(
                EmailVerificationToken.user_id == uuid.UUID(user_id)
            )
            result = await db_session.execute(stmt)
            token = result.scalar_one_or_none()

            assert token is not None
            assert isinstance(token.token, str)
            assert len(token.token) > 0
            assert token.used is False
            assert token.expires_at > datetime.utcnow()

            # Token should be valid UUID
            uuid.UUID(token.token)  # Raises ValueError if not valid

    @pytest.mark.asyncio
    async def test_verification_email_queued(
        self,
        test_client: AsyncClient,
        valid_registration_data: dict,
    ):
        """Test that verification email is queued/sent."""
        # Enable email verification for this test
        from config import settings
        with patch.object(settings, 'REQUIRE_EMAIL_VERIFICATION', True):
            # Mock email service
            with patch("api.v1.auth.registration.email_service.send_verification_email", new_callable=AsyncMock) as mock_email:
                # Act
                response = await test_client.post(
                    "/api/v1/auth/register",
                    json=valid_registration_data,
                )

                # Assert
                assert response.status_code == 201

                # Verify email service was called
                mock_email.assert_called_once()

                # Verify email parameters
                call_kwargs = mock_email.call_args.kwargs
                assert call_kwargs["to_email"] == valid_registration_data["email"].lower()
                assert "verification_token" in call_kwargs
                assert "user_name" in call_kwargs

    @pytest.mark.asyncio
    async def test_email_case_insensitive(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        valid_registration_data: dict,
    ):
        """Test that email is stored in lowercase (case-insensitive)."""
        # Arrange: Use mixed case email
        data = valid_registration_data.copy()
        data["email"] = "Test.User@EXAMPLE.COM"

        # Act
        with patch("api.v1.auth.registration.email_service.send_verification_email", new_callable=AsyncMock):
            response = await test_client.post(
                "/api/v1/auth/register",
                json=data,
            )

        # Assert
        assert response.status_code == 201

        # Check user in database
        stmt = select(User).where(User.email == "test.user@example.com")
        result = await db_session.execute(stmt)
        user = result.scalar_one_or_none()

        assert user is not None
        assert user.email == "test.user@example.com"  # Stored in lowercase

    @pytest.mark.asyncio
    async def test_password_is_hashed_not_plain(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        valid_registration_data: dict,
    ):
        """Test that password is hashed using Argon2, not stored in plain text."""
        # Act
        with patch("api.v1.auth.registration.email_service.send_verification_email", new_callable=AsyncMock):
            response = await test_client.post(
                "/api/v1/auth/register",
                json=valid_registration_data,
            )

        # Assert
        assert response.status_code == 201
        user_id = response.json()["userId"]

        # Check user in database
        stmt = select(User).where(User.id == uuid.UUID(user_id))
        result = await db_session.execute(stmt)
        user = result.scalar_one()

        # Password should be hashed
        assert user.password_hash is not None
        assert user.password_hash != valid_registration_data["password"]

        # Should be Argon2 hash (starts with $argon2)
        assert user.password_hash.startswith("$argon2")

    @pytest.mark.asyncio
    async def test_user_name_trimmed(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        valid_registration_data: dict,
    ):
        """Test that user first_name and last_name are trimmed of whitespace."""
        # Arrange: Add whitespace to names
        data = valid_registration_data.copy()
        data["first_name"] = "  John  "
        data["last_name"] = "  Doe  "

        # Act
        with patch("api.v1.auth.registration.email_service.send_verification_email", new_callable=AsyncMock):
            response = await test_client.post(
                "/api/v1/auth/register",
                json=data,
            )

        # Assert
        assert response.status_code == 201
        user_id = response.json()["userId"]

        # Check user in database
        stmt = select(User).where(User.id == uuid.UUID(user_id))
        result = await db_session.execute(stmt)
        user = result.scalar_one()

        assert user.first_name == "John"
        assert user.last_name == "Doe"

    @pytest.mark.asyncio
    async def test_all_country_preferences_accepted(
        self,
        test_client: AsyncClient,
        valid_registration_data: dict,
    ):
        """Test that all valid country preferences (UK, SA, BOTH) are accepted."""
        valid_countries = ["UK", "SA", "BOTH"]

        for country in valid_countries:
            # Arrange
            data = valid_registration_data.copy()
            data["email"] = f"test_{country.lower()}@example.com"
            data["country"] = country

            # Act
            with patch("api.v1.auth.registration.email_service.send_verification_email", new_callable=AsyncMock):
                response = await test_client.post(
                    "/api/v1/auth/register",
                    json=data,
                )

            # Assert
            assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_marketing_consent_optional(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        valid_registration_data: dict,
    ):
        """Test that marketing_consent is optional and defaults to False."""
        # Arrange: Remove marketing_consent from request
        data = valid_registration_data.copy()
        if "marketing_consent" in data:
            del data["marketing_consent"]

        # Act
        with patch("api.v1.auth.registration.email_service.send_verification_email", new_callable=AsyncMock):
            response = await test_client.post(
                "/api/v1/auth/register",
                json=data,
            )

        # Assert
        assert response.status_code == 201
        user_id = response.json()["userId"]

        # Check user in database
        stmt = select(User).where(User.id == uuid.UUID(user_id))
        result = await db_session.execute(stmt)
        user = result.scalar_one()

        assert user.marketing_consent is False  # Default

    @pytest.mark.asyncio
    async def test_email_failure_does_not_prevent_registration(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        valid_registration_data: dict,
    ):
        """Test that email sending failure does not prevent successful registration."""
        # Mock email service to raise exception
        with patch("api.v1.auth.registration.email_service.send_verification_email", new_callable=AsyncMock) as mock_email:
            mock_email.side_effect = Exception("Email service unavailable")

            # Act
            response = await test_client.post(
                "/api/v1/auth/register",
                json=valid_registration_data,
            )

            # Assert: Registration still succeeds
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True

            # User should still be created
            stmt = select(User).where(User.email == valid_registration_data["email"].lower())
            result = await db_session.execute(stmt)
            user = result.scalar_one_or_none()
            assert user is not None
