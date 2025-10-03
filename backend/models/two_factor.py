"""
Two-factor authentication models.

This module contains the User2FA model for TOTP-based two-factor authentication
with encrypted secret storage and backup codes.

Security:
- TOTP secrets encrypted using Fernet (AES-128)
- Backup codes encrypted as JSON
- Single-use backup codes enforced
"""

import json
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, Index
from sqlalchemy.orm import relationship

from database import Base
from models.user import GUID
from config import settings


class User2FA(Base):
    """
    Two-factor authentication model.

    Stores TOTP secrets and backup codes for users with 2FA enabled.
    All sensitive data is encrypted at rest using Fernet encryption.

    Fields:
        id: Primary key (UUID)
        user_id: Foreign key to users table (unique)
        secret: Encrypted TOTP secret (base32 encoded)
        backup_codes: Encrypted JSON array of backup codes
        enabled: Whether 2FA is currently enabled
        created_at: When 2FA was first set up
        updated_at: Last update timestamp
        last_used_at: Last successful 2FA authentication

    Relationships:
        user: The user this 2FA configuration belongs to

    Security:
        - secret stored encrypted using Fernet (from ENCRYPTION_KEY env var)
        - backup_codes stored as encrypted JSON
        - Encryption/decryption handled transparently via properties
    """

    __tablename__ = "user_2fa"

    # Primary Key
    id = Column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique 2FA record identifier",
    )

    # Foreign Key
    user_id = Column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        doc="User this 2FA configuration belongs to",
    )

    # Encrypted Fields (stored encrypted, accessed via properties)
    _secret_encrypted = Column(
        "secret",
        Text,
        nullable=False,
        doc="Encrypted TOTP secret (base32 encoded)",
    )

    _backup_codes_encrypted = Column(
        "backup_codes",
        Text,
        nullable=True,
        doc="Encrypted JSON array of backup codes",
    )

    # Status Fields
    enabled = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether 2FA is currently enabled",
    )

    # Audit Fields
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="When 2FA was first set up",
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Last update timestamp",
    )
    last_used_at = Column(
        DateTime,
        nullable=True,
        doc="Last successful 2FA authentication",
    )

    # Relationships
    user = relationship("User", back_populates="two_factor_auth")

    def _get_cipher(self):
        """
        Get Fernet cipher instance for encryption/decryption.

        Returns:
            Fernet cipher instance

        Raises:
            ValueError: If ENCRYPTION_KEY not configured
        """
        from cryptography.fernet import Fernet

        if not settings.ENCRYPTION_KEY:
            raise ValueError(
                "ENCRYPTION_KEY not configured. Cannot encrypt/decrypt 2FA data."
            )

        # Ensure key is bytes
        key = settings.ENCRYPTION_KEY
        if isinstance(key, str):
            key = key.encode()

        return Fernet(key)

    @property
    def secret(self) -> str:
        """
        Decrypt and return TOTP secret.

        Returns:
            str: Decrypted TOTP secret (base32 encoded)

        Raises:
            ValueError: If secret cannot be decrypted
        """
        if not self._secret_encrypted:
            return ""

        try:
            cipher = self._get_cipher()
            decrypted = cipher.decrypt(self._secret_encrypted.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt 2FA secret: {e}")

    @secret.setter
    def secret(self, value: str) -> None:
        """
        Encrypt and store TOTP secret.

        Args:
            value: TOTP secret to encrypt (base32 encoded)

        Raises:
            ValueError: If secret cannot be encrypted
        """
        if not value:
            self._secret_encrypted = None
            return

        try:
            cipher = self._get_cipher()
            encrypted = cipher.encrypt(value.encode())
            self._secret_encrypted = encrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to encrypt 2FA secret: {e}")

    @property
    def backup_codes(self) -> List[str]:
        """
        Decrypt and return backup codes.

        Returns:
            List[str]: List of backup codes (may include used markers)

        Raises:
            ValueError: If backup codes cannot be decrypted
        """
        if not self._backup_codes_encrypted:
            return []

        try:
            cipher = self._get_cipher()
            decrypted = cipher.decrypt(self._backup_codes_encrypted.encode())
            return json.loads(decrypted.decode())
        except Exception as e:
            raise ValueError(f"Failed to decrypt backup codes: {e}")

    @backup_codes.setter
    def backup_codes(self, value: List[str]) -> None:
        """
        Encrypt and store backup codes.

        Args:
            value: List of backup codes to encrypt

        Raises:
            ValueError: If backup codes cannot be encrypted
        """
        if not value:
            self._backup_codes_encrypted = None
            return

        try:
            cipher = self._get_cipher()
            json_data = json.dumps(value)
            encrypted = cipher.encrypt(json_data.encode())
            self._backup_codes_encrypted = encrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to encrypt backup codes: {e}")

    def __repr__(self) -> str:
        """String representation of User2FA."""
        return f"<User2FA(id={self.id}, user_id={self.user_id}, enabled={self.enabled})>"


# Create indexes for performance
Index("idx_user_2fa_user_id", User2FA.user_id, unique=True)
