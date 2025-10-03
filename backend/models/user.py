"""
User authentication models.

This module contains the User and EmailVerificationToken models for
user registration, authentication, and email verification.

Compliance:
- GDPR/POPIA compliant with audit fields
- Temporal data tracking with timestamps
- Secure password storage (hashed only)
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Date, Enum, ForeignKey, String, Text, Index, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from database import Base


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses CHAR(36) storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            else:
                return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if isinstance(value, uuid.UUID):
                return value
            else:
                return uuid.UUID(value)


class UserStatus(str, enum.Enum):
    """
    User account status enumeration.

    - PENDING_VERIFICATION: Account created but email not verified
    - ACTIVE: Email verified, account in good standing
    - SUSPENDED: Account temporarily disabled (admin action or security)
    - DELETED: Account marked for deletion (soft delete)
    """
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class CountryPreference(str, enum.Enum):
    """
    User's country preference for financial planning.

    - UK: United Kingdom only
    - SA: South Africa only
    - BOTH: Both UK and South Africa
    """
    UK = "UK"
    SA = "SA"
    BOTH = "BOTH"


class User(Base):
    """
    User account model.

    Stores core user information for authentication and profile management.
    Password is stored as a hash only (using Argon2).

    Fields:
        id: Primary key (UUID)
        email: Unique email address (login identifier)
        password_hash: Argon2 hashed password (nullable during registration flow)
        first_name: User's first name
        last_name: User's last name
        country_preference: Primary country for financial planning (UK/SA/BOTH)
        status: Account status (PENDING_VERIFICATION, ACTIVE, SUSPENDED, DELETED)
        email_verified: Email verification status
        terms_accepted_at: Timestamp of terms and conditions acceptance
        marketing_consent: User consent for marketing communications
        created_at: Account creation timestamp
        updated_at: Last update timestamp (auto-updated)
        last_login_at: Last successful login timestamp

    Relationships:
        verification_tokens: Email verification tokens for this user

    Indexes:
        - email (unique, for login lookups)

    Compliance:
        - GDPR: Tracks consent (terms_accepted_at, marketing_consent)
        - POPIA: Same consent tracking
        - Audit: created_at, updated_at for audit trail
    """
    __tablename__ = "users"

    # Primary Key
    id = Column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique user identifier"
    )

    # Authentication Fields
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="User email address (unique, used for login)"
    )
    password_hash = Column(
        String(255),
        nullable=True,  # Nullable initially, set after email verification
        doc="Argon2 password hash"
    )

    # Profile Fields
    first_name = Column(
        String(100),
        nullable=False,
        doc="User's first name"
    )
    last_name = Column(
        String(100),
        nullable=False,
        doc="User's last name"
    )
    country_preference = Column(
        Enum(CountryPreference),
        nullable=False,
        doc="Primary country for financial planning (UK/SA/BOTH)"
    )

    # Account Status
    status = Column(
        Enum(UserStatus),
        default=UserStatus.PENDING_VERIFICATION,
        nullable=False,
        doc="Account status"
    )
    email_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Email verification status"
    )

    # Compliance & Consent (GDPR/POPIA)
    terms_accepted_at = Column(
        DateTime,
        nullable=False,
        doc="Timestamp when user accepted terms and conditions"
    )
    marketing_consent = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="User consent for marketing communications"
    )

    # Audit Fields
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Account creation timestamp"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Last update timestamp"
    )
    last_login_at = Column(
        DateTime,
        nullable=True,
        doc="Last successful login timestamp"
    )

    # Profile Fields (Phase 1B - Task 1.5.1)
    phone = Column(
        String(20),
        nullable=True,
        doc="User's phone number (international format)"
    )
    date_of_birth = Column(
        Date,
        nullable=True,
        doc="User's date of birth"
    )
    address = Column(
        JSON,  # Use JSON instead of JSONB for SQLite compatibility
        nullable=True,
        doc="User's address (JSON: line1, line2, city, postcode, country)"
    )
    timezone = Column(
        String(50),
        nullable=False,
        default='Europe/London',
        server_default='Europe/London',
        doc="User's timezone preference"
    )
    deleted_at = Column(
        DateTime,
        nullable=True,
        doc="Soft delete timestamp (account deletion)"
    )

    # Relationships
    verification_tokens = relationship(
        "EmailVerificationToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    login_attempts = relationship(
        "LoginAttempt",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    two_factor_auth = relationship(
        "User2FA",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    tax_statuses = relationship(
        "UserTaxStatus",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(UserTaxStatus.effective_from)"
    )
    uk_srt_records = relationship(
        "UKSRTData",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    sa_presence_records = relationship(
        "SAPresenceData",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    income_records = relationship(
        "UserIncome",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    savings_accounts = relationship(
        "SavingsAccount",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    isa_contributions = relationship(
        "ISAContribution",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    tfsa_contributions = relationship(
        "TFSAContribution",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email={self.email}, status={self.status.value})>"


class EmailVerificationToken(Base):
    """
    Email verification token model.

    Stores tokens for email verification during user registration.
    Tokens are UUID-based, expire after 24 hours, and are single-use.

    Fields:
        id: Primary key (UUID)
        user_id: Foreign key to users table
        token: Verification token (UUID, unique)
        expires_at: Token expiration timestamp (24 hours from creation)
        used: Whether token has been used
        created_at: Token creation timestamp

    Relationships:
        user: The user this token belongs to

    Indexes:
        - token (unique, for fast lookups)
        - expires_at (for cleanup queries)
        - user_id (for user-specific queries)

    Security:
        - Tokens expire after 24 hours
        - Single-use only (idempotent verification)
        - UUID prevents token guessing
    """
    __tablename__ = "email_verification_tokens"

    # Primary Key
    id = Column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique token identifier"
    )

    # Foreign Key
    user_id = Column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="User this token belongs to"
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

    # Audit Fields
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Token creation timestamp"
    )

    # Relationships
    user = relationship("User", back_populates="verification_tokens")

    def __repr__(self) -> str:
        """String representation of EmailVerificationToken."""
        return f"<EmailVerificationToken(id={self.id}, user_id={self.user_id}, used={self.used})>"


# Create indexes explicitly for better control
Index("idx_users_email", User.email, unique=True)
Index("idx_email_verification_tokens_token", EmailVerificationToken.token, unique=True)
Index("idx_email_verification_tokens_expires_at", EmailVerificationToken.expires_at)
Index("idx_email_verification_tokens_user_id", EmailVerificationToken.user_id)
