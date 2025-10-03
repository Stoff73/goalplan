"""
Tests for User2FA model with encryption.

Tests cover:
- 2FA record creation
- Secret encryption/decryption
- Backup codes storage and encryption
- Relationships with User model
"""

import pytest
import uuid
from datetime import datetime
from sqlalchemy import select

from models import User, User2FA, UserStatus
from models.user import CountryPreference


@pytest.mark.asyncio
class TestUser2FAModel:
    """Test suite for User2FA model."""

    async def test_create_2fa_record(self, db_session, test_user):
        """Test creating a 2FA record for a user."""
        # Create 2FA record
        secret = "JBSWY3DPEHPK3PXP"  # Example base32 secret
        user_2fa = User2FA(
            user_id=test_user.id,
            secret=secret,
            enabled=False,
            backup_codes=[],
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Verify record was created
        result = await db_session.execute(
            select(User2FA).where(User2FA.user_id == test_user.id)
        )
        saved_2fa = result.scalar_one_or_none()

        assert saved_2fa is not None
        assert saved_2fa.user_id == test_user.id
        assert saved_2fa.enabled is False
        assert saved_2fa.created_at is not None
        assert saved_2fa.updated_at is not None

    async def test_secret_encryption(self, db_session, test_user):
        """Test that secrets are encrypted in storage."""
        secret = "JBSWY3DPEHPK3PXP"
        user_2fa = User2FA(
            user_id=test_user.id,
            secret=secret,
            enabled=False,
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Check that encrypted value is different from plaintext
        assert user_2fa._secret_encrypted != secret

        # Check that we can decrypt it back
        assert user_2fa.secret == secret

    async def test_secret_decryption(self, db_session, test_user):
        """Test that secrets can be decrypted correctly."""
        original_secret = "JBSWY3DPEHPK3PXP"
        user_2fa = User2FA(
            user_id=test_user.id,
            secret=original_secret,
            enabled=False,
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Retrieve from database
        result = await db_session.execute(
            select(User2FA).where(User2FA.user_id == test_user.id)
        )
        retrieved_2fa = result.scalar_one()

        # Verify decrypted secret matches original
        assert retrieved_2fa.secret == original_secret

    async def test_backup_codes_encryption(self, db_session, test_user):
        """Test that backup codes are encrypted in storage."""
        secret = "JBSWY3DPEHPK3PXP"
        backup_codes = ["12345678", "87654321", "11111111"]

        user_2fa = User2FA(
            user_id=test_user.id,
            secret=secret,
            enabled=True,
            backup_codes=backup_codes,
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Check that encrypted value is different from plaintext
        assert user_2fa._backup_codes_encrypted != str(backup_codes)

        # Check that we can decrypt it back
        assert user_2fa.backup_codes == backup_codes

    async def test_backup_codes_decryption(self, db_session, test_user):
        """Test that backup codes can be decrypted correctly."""
        secret = "JBSWY3DPEHPK3PXP"
        original_codes = ["12345678", "87654321", "11111111"]

        user_2fa = User2FA(
            user_id=test_user.id,
            secret=secret,
            enabled=True,
            backup_codes=original_codes,
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Retrieve from database
        result = await db_session.execute(
            select(User2FA).where(User2FA.user_id == test_user.id)
        )
        retrieved_2fa = result.scalar_one()

        # Verify decrypted codes match original
        assert retrieved_2fa.backup_codes == original_codes

    async def test_empty_backup_codes(self, db_session, test_user):
        """Test handling of empty backup codes list."""
        secret = "JBSWY3DPEHPK3PXP"
        user_2fa = User2FA(
            user_id=test_user.id,
            secret=secret,
            enabled=False,
            backup_codes=[],
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Retrieve from database
        result = await db_session.execute(
            select(User2FA).where(User2FA.user_id == test_user.id)
        )
        retrieved_2fa = result.scalar_one()

        # Verify empty list is handled correctly
        assert retrieved_2fa.backup_codes == []

    async def test_user_relationship(self, db_session, test_user):
        """Test relationship between User and User2FA."""
        secret = "JBSWY3DPEHPK3PXP"
        user_2fa = User2FA(
            user_id=test_user.id,
            secret=secret,
            enabled=True,
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Access 2FA through user relationship
        result = await db_session.execute(
            select(User).where(User.id == test_user.id)
        )
        user = result.scalar_one()

        # Note: Need to explicitly load relationship in async
        await db_session.refresh(user, ['two_factor_auth'])

        assert user.two_factor_auth is not None
        assert user.two_factor_auth.user_id == test_user.id
        assert user.two_factor_auth.enabled is True

    async def test_cascade_delete(self, db_session):
        """Test that 2FA record is deleted when user is deleted."""
        # Create user
        user = User(
            email="test2fa@example.com",
            password_hash="$argon2id$test",
            first_name="Test",
            last_name="User",
            country_preference=CountryPreference.UK,
            status=UserStatus.ACTIVE,
            email_verified=True,
            terms_accepted_at=datetime.utcnow(),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create 2FA record
        user_2fa = User2FA(
            user_id=user.id,
            secret="JBSWY3DPEHPK3PXP",
            enabled=True,
        )
        db_session.add(user_2fa)
        await db_session.commit()

        user_id = user.id

        # Delete user
        await db_session.delete(user)
        await db_session.commit()

        # Verify 2FA record was also deleted
        result = await db_session.execute(
            select(User2FA).where(User2FA.user_id == user_id)
        )
        deleted_2fa = result.scalar_one_or_none()

        assert deleted_2fa is None

    async def test_enabled_status(self, db_session, test_user):
        """Test 2FA enabled/disabled status."""
        secret = "JBSWY3DPEHPK3PXP"

        # Create disabled 2FA
        user_2fa = User2FA(
            user_id=test_user.id,
            secret=secret,
            enabled=False,
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Verify disabled
        result = await db_session.execute(
            select(User2FA).where(User2FA.user_id == test_user.id)
        )
        saved_2fa = result.scalar_one()
        assert saved_2fa.enabled is False

        # Enable 2FA
        saved_2fa.enabled = True
        await db_session.commit()

        # Verify enabled
        result = await db_session.execute(
            select(User2FA).where(User2FA.user_id == test_user.id)
        )
        updated_2fa = result.scalar_one()
        assert updated_2fa.enabled is True

    async def test_last_used_at_update(self, db_session, test_user):
        """Test updating last_used_at timestamp."""
        secret = "JBSWY3DPEHPK3PXP"
        user_2fa = User2FA(
            user_id=test_user.id,
            secret=secret,
            enabled=True,
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Initially null
        assert user_2fa.last_used_at is None

        # Update last_used_at
        now = datetime.utcnow()
        user_2fa.last_used_at = now
        await db_session.commit()

        # Verify updated
        result = await db_session.execute(
            select(User2FA).where(User2FA.user_id == test_user.id)
        )
        updated_2fa = result.scalar_one()
        assert updated_2fa.last_used_at is not None
        # Allow small time difference
        assert abs((updated_2fa.last_used_at - now).total_seconds()) < 1
