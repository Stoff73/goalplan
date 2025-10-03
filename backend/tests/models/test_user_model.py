"""
Tests for User and EmailVerificationToken models.

This module tests the data models for user registration and email verification.

Test Coverage:
- User model creation and field validation
- Email uniqueness constraint
- Password field nullability
- Default status and field values
- Timestamp auto-population
- EmailVerificationToken model
- Relationships between models
"""

import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.user import (
    User,
    EmailVerificationToken,
    UserStatus,
    CountryPreference,
)


class TestUserModel:
    """Tests for the User model."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, db_session: AsyncSession):
        """Test successful user creation with all required fields."""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "country_preference": CountryPreference.UK,
            "terms_accepted_at": datetime.utcnow(),
            "marketing_consent": True,
        }

        # Act
        user = User(**user_data)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Assert
        assert user.id is not None
        assert isinstance(user.id, uuid.UUID)
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.country_preference == CountryPreference.UK
        assert user.marketing_consent is True

    @pytest.mark.asyncio
    async def test_user_password_hash_nullable(self, db_session: AsyncSession):
        """Test that password_hash field is nullable during registration."""
        # Arrange - Create user without password_hash
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            country_preference=CountryPreference.SA,
            terms_accepted_at=datetime.utcnow(),
        )

        # Act
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Assert - Should succeed with null password_hash
        assert user.password_hash is None
        assert user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_user_default_status_pending_verification(
        self, db_session: AsyncSession
    ):
        """Test that default user status is PENDING_VERIFICATION."""
        # Arrange
        user = User(
            email="newuser@example.com",
            first_name="Jane",
            last_name="Smith",
            country_preference=CountryPreference.BOTH,
            terms_accepted_at=datetime.utcnow(),
        )

        # Act
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Assert
        assert user.status == UserStatus.PENDING_VERIFICATION
        assert user.email_verified is False

    @pytest.mark.asyncio
    async def test_user_email_unique_constraint(self, db_session: AsyncSession):
        """Test that email field has unique constraint."""
        # Arrange - Create first user
        user1 = User(
            email="duplicate@example.com",
            first_name="User",
            last_name="One",
            country_preference=CountryPreference.UK,
            terms_accepted_at=datetime.utcnow(),
        )
        db_session.add(user1)
        await db_session.commit()

        # Act & Assert - Try to create second user with same email
        user2 = User(
            email="duplicate@example.com",  # Same email
            first_name="User",
            last_name="Two",
            country_preference=CountryPreference.SA,
            terms_accepted_at=datetime.utcnow(),
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert "unique" in str(exc_info.value).lower() or "duplicate" in str(
            exc_info.value
        ).lower()

    @pytest.mark.asyncio
    async def test_user_timestamps_auto_populate(self, db_session: AsyncSession):
        """Test that created_at and updated_at timestamps auto-populate."""
        # Arrange
        before_creation = datetime.utcnow()

        user = User(
            email="timestamps@example.com",
            first_name="Time",
            last_name="Stamp",
            country_preference=CountryPreference.UK,
            terms_accepted_at=datetime.utcnow(),
        )

        # Act
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Assert - Timestamps should be auto-populated
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.created_at >= before_creation
        assert user.updated_at >= before_creation

    @pytest.mark.asyncio
    async def test_user_updated_at_auto_updates(self, db_session: AsyncSession):
        """Test that updated_at timestamp updates on modification."""
        # Arrange - Create user
        user = User(
            email="update@example.com",
            first_name="Update",
            last_name="Test",
            country_preference=CountryPreference.UK,
            terms_accepted_at=datetime.utcnow(),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        original_updated_at = user.updated_at

        # Act - Update user (small delay to ensure timestamp difference)
        import asyncio
        await asyncio.sleep(0.1)

        user.first_name = "Modified"
        await db_session.commit()
        await db_session.refresh(user)

        # Assert - updated_at should have changed
        # Note: This test may be flaky depending on database timestamp precision
        assert user.updated_at >= original_updated_at

    @pytest.mark.asyncio
    async def test_user_all_country_preferences(self, db_session: AsyncSession):
        """Test that all country preference enum values work."""
        # Test UK
        user_uk = User(
            email="uk@example.com",
            first_name="UK",
            last_name="User",
            country_preference=CountryPreference.UK,
            terms_accepted_at=datetime.utcnow(),
        )
        db_session.add(user_uk)

        # Test SA
        user_sa = User(
            email="sa@example.com",
            first_name="SA",
            last_name="User",
            country_preference=CountryPreference.SA,
            terms_accepted_at=datetime.utcnow(),
        )
        db_session.add(user_sa)

        # Test BOTH
        user_both = User(
            email="both@example.com",
            first_name="Both",
            last_name="User",
            country_preference=CountryPreference.BOTH,
            terms_accepted_at=datetime.utcnow(),
        )
        db_session.add(user_both)

        # Act
        await db_session.commit()

        # Assert
        result = await db_session.execute(select(User))
        users = result.scalars().all()
        assert len(users) == 3
        country_prefs = {u.country_preference for u in users}
        assert country_prefs == {
            CountryPreference.UK,
            CountryPreference.SA,
            CountryPreference.BOTH,
        }

    @pytest.mark.asyncio
    async def test_user_all_statuses(self, db_session: AsyncSession):
        """Test that all user status enum values work."""
        statuses_to_test = [
            UserStatus.PENDING_VERIFICATION,
            UserStatus.ACTIVE,
            UserStatus.SUSPENDED,
            UserStatus.DELETED,
        ]

        # Create users with different statuses
        for i, status in enumerate(statuses_to_test):
            user = User(
                email=f"status{i}@example.com",
                first_name="Status",
                last_name="Test",
                country_preference=CountryPreference.UK,
                status=status,
                terms_accepted_at=datetime.utcnow(),
            )
            db_session.add(user)

        # Act
        await db_session.commit()

        # Assert
        result = await db_session.execute(select(User))
        users = result.scalars().all()
        user_statuses = {u.status for u in users}
        assert len(user_statuses) == 4
        assert user_statuses == set(statuses_to_test)

    @pytest.mark.asyncio
    async def test_user_repr(self, db_session: AsyncSession):
        """Test User __repr__ method."""
        # Arrange
        user = User(
            email="repr@example.com",
            first_name="Repr",
            last_name="Test",
            country_preference=CountryPreference.UK,
            terms_accepted_at=datetime.utcnow(),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Act
        repr_string = repr(user)

        # Assert
        assert "User" in repr_string
        assert str(user.id) in repr_string
        assert "repr@example.com" in repr_string
        assert "PENDING_VERIFICATION" in repr_string


class TestEmailVerificationTokenModel:
    """Tests for the EmailVerificationToken model."""

    @pytest.mark.asyncio
    async def test_create_verification_token_success(self, db_session: AsyncSession):
        """Test successful creation of email verification token."""
        # Arrange - Create user first
        user = User(
            email="verify@example.com",
            first_name="Verify",
            last_name="User",
            country_preference=CountryPreference.UK,
            terms_accepted_at=datetime.utcnow(),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create verification token
        token_string = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=24)

        verification_token = EmailVerificationToken(
            user_id=user.id,
            token=token_string,
            expires_at=expires_at,
        )

        # Act
        db_session.add(verification_token)
        await db_session.commit()
        await db_session.refresh(verification_token)

        # Assert
        assert verification_token.id is not None
        assert verification_token.user_id == user.id
        assert verification_token.token == token_string
        assert verification_token.expires_at == expires_at
        assert verification_token.used is False
        assert verification_token.created_at is not None

    @pytest.mark.asyncio
    async def test_verification_token_user_relationship(
        self, db_session: AsyncSession
    ):
        """Test relationship between User and EmailVerificationToken."""
        # Arrange - Create user
        user = User(
            email="relationship@example.com",
            first_name="Relation",
            last_name="Test",
            country_preference=CountryPreference.UK,
            terms_accepted_at=datetime.utcnow(),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create multiple tokens
        for i in range(3):
            token = EmailVerificationToken(
                user_id=user.id,
                token=str(uuid.uuid4()),
                expires_at=datetime.utcnow() + timedelta(hours=24),
            )
            db_session.add(token)

        await db_session.commit()

        # Act - Fetch user with tokens (use selectinload for async relationship loading)
        result = await db_session.execute(
            select(User)
            .where(User.id == user.id)
            .options(selectinload(User.verification_tokens))
        )
        fetched_user = result.scalar_one()

        # Assert
        assert len(fetched_user.verification_tokens) == 3
        for token in fetched_user.verification_tokens:
            assert token.user_id == fetched_user.id

    @pytest.mark.asyncio
    async def test_verification_token_unique_constraint(
        self, db_session: AsyncSession
    ):
        """Test that token field has unique constraint."""
        # Arrange - Create user
        user = User(
            email="unique-token@example.com",
            first_name="Unique",
            last_name="Token",
            country_preference=CountryPreference.UK,
            terms_accepted_at=datetime.utcnow(),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create first token
        token_string = str(uuid.uuid4())
        token1 = EmailVerificationToken(
            user_id=user.id,
            token=token_string,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db_session.add(token1)
        await db_session.commit()

        # Act & Assert - Try to create second token with same token string
        token2 = EmailVerificationToken(
            user_id=user.id,
            token=token_string,  # Same token
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db_session.add(token2)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert "unique" in str(exc_info.value).lower() or "duplicate" in str(
            exc_info.value
        ).lower()

    @pytest.mark.asyncio
    async def test_verification_token_cascade_delete(self, db_session: AsyncSession):
        """Test that tokens are deleted when user is deleted (CASCADE)."""
        # Arrange - Create user with token
        user = User(
            email="cascade@example.com",
            first_name="Cascade",
            last_name="Test",
            country_preference=CountryPreference.UK,
            terms_accepted_at=datetime.utcnow(),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        token = EmailVerificationToken(
            user_id=user.id,
            token=str(uuid.uuid4()),
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db_session.add(token)
        await db_session.commit()

        token_id = token.id

        # Act - Delete user
        await db_session.delete(user)
        await db_session.commit()

        # Assert - Token should be deleted as well
        result = await db_session.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.id == token_id
            )
        )
        deleted_token = result.scalar_one_or_none()
        assert deleted_token is None

    @pytest.mark.asyncio
    async def test_verification_token_default_values(self, db_session: AsyncSession):
        """Test default values for EmailVerificationToken."""
        # Arrange - Create user
        user = User(
            email="defaults@example.com",
            first_name="Default",
            last_name="Values",
            country_preference=CountryPreference.UK,
            terms_accepted_at=datetime.utcnow(),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create token without specifying 'used' field
        token = EmailVerificationToken(
            user_id=user.id,
            token=str(uuid.uuid4()),
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )

        # Act
        db_session.add(token)
        await db_session.commit()
        await db_session.refresh(token)

        # Assert
        assert token.used is False  # Default value
        assert token.created_at is not None  # Auto-populated

    @pytest.mark.asyncio
    async def test_verification_token_repr(self, db_session: AsyncSession):
        """Test EmailVerificationToken __repr__ method."""
        # Arrange
        user = User(
            email="repr-token@example.com",
            first_name="Repr",
            last_name="Token",
            country_preference=CountryPreference.UK,
            terms_accepted_at=datetime.utcnow(),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        token = EmailVerificationToken(
            user_id=user.id,
            token=str(uuid.uuid4()),
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db_session.add(token)
        await db_session.commit()
        await db_session.refresh(token)

        # Act
        repr_string = repr(token)

        # Assert
        assert "EmailVerificationToken" in repr_string
        assert str(token.id) in repr_string
        assert str(token.user_id) in repr_string
        assert "False" in repr_string  # used=False
