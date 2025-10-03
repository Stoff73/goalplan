"""
User profile history and email change token models.

This module contains models for tracking profile changes and managing
email change verification.

Compliance:
- GDPR/POPIA compliant with full audit trail
- IP address and user agent tracking for security
- Temporal data tracking with timestamps
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database import Base
from models.user import GUID


class UserProfileHistory(Base):
    """
    User profile history model for audit trail.

    Tracks all changes to user profile fields for security monitoring
    and compliance. Each record represents a single field change.

    Fields:
        id: Primary key (UUID)
        user_id: User whose profile was changed
        field_name: Name of the changed field (e.g., 'phone', 'address')
        old_value: Previous value (serialized as text)
        new_value: New value (serialized as text)
        changed_by: User who made the change (typically same as user_id)
        changed_at: Timestamp of change
        ip_address: IP address of the request
        user_agent: User agent string from the request

    Relationships:
        user: The user whose profile was changed
        changed_by_user: The user who made the change

    Indexes:
        - (user_id, changed_at DESC) for efficient user history queries
        - changed_at for cleanup and reporting

    Use Cases:
        - Security audit trail
        - Account takeover detection
        - Compliance reporting
        - User activity history
    """
    __tablename__ = "user_profile_history"

    # Primary Key
    id = Column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier"
    )

    # Foreign Keys
    user_id = Column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="User whose profile was changed"
    )
    changed_by = Column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        doc="User who made the change"
    )

    # Change Details
    field_name = Column(
        String(50),
        nullable=False,
        doc="Name of the field that was changed"
    )
    old_value = Column(
        Text,
        nullable=True,
        doc="Previous value (serialized as text)"
    )
    new_value = Column(
        Text,
        nullable=True,
        doc="New value (serialized as text)"
    )

    # Audit Fields
    changed_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Timestamp of change"
    )
    ip_address = Column(
        String(45),
        nullable=True,
        doc="IP address of the request (IPv4 or IPv6)"
    )
    user_agent = Column(
        Text,
        nullable=True,
        doc="User agent string from the request"
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="profile_history")
    changed_by_user = relationship("User", foreign_keys=[changed_by])

    def __repr__(self) -> str:
        """String representation of UserProfileHistory."""
        return (
            f"<UserProfileHistory(id={self.id}, user_id={self.user_id}, "
            f"field={self.field_name}, changed_at={self.changed_at})>"
        )


class EmailChangeToken(Base):
    """
    Email change verification token model.

    Stores tokens for email change verification. Similar to email verification
    but tracks both old and new email addresses for security.

    Fields:
        id: Primary key (UUID)
        user_id: User requesting email change
        new_email: New email address (pending verification)
        old_email: Current email address (for audit)
        token: Verification token (UUID)
        expires_at: Token expiration timestamp (24 hours from creation)
        used: Whether token has been used
        used_at: Timestamp when token was used
        created_at: Token creation timestamp

    Relationships:
        user: The user requesting email change

    Indexes:
        - token (unique, for fast lookups)
        - user_id (for user-specific queries)
        - expires_at (for cleanup queries)

    Security:
        - Tokens expire after 24 hours
        - Single-use only (idempotent verification)
        - UUID prevents token guessing
        - Both old and new email tracked for audit
    """
    __tablename__ = "email_change_tokens"

    # Primary Key
    id = Column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier"
    )

    # Foreign Key
    user_id = Column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="User requesting email change"
    )

    # Email Addresses
    new_email = Column(
        String(255),
        nullable=False,
        doc="New email address (pending verification)"
    )
    old_email = Column(
        String(255),
        nullable=False,
        doc="Current email address (for audit)"
    )

    # Token Fields
    token = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Verification token (UUID)"
    )
    expires_at = Column(
        DateTime,
        nullable=False,
        index=True,
        doc="Token expiration timestamp"
    )
    used = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether token has been used"
    )
    used_at = Column(
        DateTime,
        nullable=True,
        doc="Timestamp when token was used"
    )

    # Audit Fields
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Token creation timestamp"
    )

    # Relationships
    user = relationship("User", backref="email_change_tokens")

    def __repr__(self) -> str:
        """String representation of EmailChangeToken."""
        return (
            f"<EmailChangeToken(id={self.id}, user_id={self.user_id}, "
            f"old_email={self.old_email}, new_email={self.new_email}, used={self.used})>"
        )


# Create indexes explicitly for better control
Index(
    "idx_profile_history_user_changed",
    UserProfileHistory.user_id,
    UserProfileHistory.changed_at.desc()
)
Index("idx_profile_history_changed_at", UserProfileHistory.changed_at)

Index("idx_email_change_tokens_token", EmailChangeToken.token, unique=True)
Index("idx_email_change_tokens_user_id", EmailChangeToken.user_id)
Index("idx_email_change_tokens_expires_at", EmailChangeToken.expires_at)
