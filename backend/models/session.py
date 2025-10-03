"""
Session management models.

This module contains models for user session tracking and login attempt logging.
Sessions are stored in both PostgreSQL (persistence) and Redis (fast validation).

Compliance:
- GDPR/POPIA compliant with audit fields
- Temporal data tracking with timestamps
- IP address and device tracking for security monitoring
- Support for max 5 concurrent sessions per user
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text, Index, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
from models.user import GUID


class UserSession(Base):
    """
    User session model for JWT token tracking.

    Tracks active user sessions with JWT tokens stored in both PostgreSQL
    (for persistence and audit) and Redis (for fast validation <10ms).

    Fields:
        id: Primary key (UUID)
        user_id: Foreign key to users table
        session_token: JTI from JWT refresh token (unique identifier)
        access_token_jti: JTI from current access token (nullable, updated on refresh)
        device_info: User agent string for device identification
        ip_address: IP address of the client
        created_at: Session creation timestamp
        last_activity: Last API request timestamp (updated on validation)
        expires_at: Session expiration timestamp (refresh token expiration)
        is_active: Whether session is active (can be revoked)

    Relationships:
        user: The user this session belongs to

    Indexes:
        - user_id (for user-specific queries)
        - session_token (unique, for fast session lookups)
        - expires_at (for cleanup queries)
        - is_active (for active session queries)

    Security:
        - Max 5 concurrent sessions per user (enforced by service)
        - Sessions can be revoked individually or all at once
        - Device and IP tracking for security monitoring
        - Automatic cleanup of expired sessions

    Performance:
        - Redis fast path: <10ms session validation
        - PostgreSQL fallback: Full audit trail
        - Indexes optimize common queries
    """
    __tablename__ = "user_sessions"

    # Primary Key
    id = Column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique session identifier"
    )

    # Foreign Key
    user_id = Column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="User this session belongs to"
    )

    # Session Token Fields
    session_token = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="JTI from JWT refresh token (unique session identifier)"
    )
    access_token_jti = Column(
        String(255),
        nullable=True,
        doc="JTI from current access token (updated on refresh)"
    )

    # Device and Network Information
    device_info = Column(
        Text,
        nullable=True,
        doc="User agent string for device identification"
    )
    ip_address = Column(
        String(45),  # IPv6 max length
        nullable=True,
        doc="IP address of the client"
    )

    # Session Status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        doc="Whether session is active (false = revoked)"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Session creation timestamp"
    )
    last_activity = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Last API request timestamp (updated on validation)"
    )
    expires_at = Column(
        DateTime,
        nullable=False,
        index=True,
        doc="Session expiration timestamp (refresh token expiration)"
    )

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self) -> str:
        """String representation of UserSession."""
        return (
            f"<UserSession(id={self.id}, user_id={self.user_id}, "
            f"active={self.is_active}, expires={self.expires_at})>"
        )

    def is_expired(self) -> bool:
        """
        Check if session is expired.

        Returns:
            bool: True if session has expired, False otherwise
        """
        return datetime.utcnow() >= self.expires_at

    def is_valid(self) -> bool:
        """
        Check if session is valid (active and not expired).

        Returns:
            bool: True if session is valid, False otherwise
        """
        return self.is_active and not self.is_expired()


class LoginAttempt(Base):
    """
    Login attempt tracking model for security monitoring.

    Logs all login attempts (successful and failed) for:
    - Account lockout after 5 failed attempts
    - Brute force attack detection
    - Security monitoring and audit
    - IP-based rate limiting

    Fields:
        id: Primary key (UUID)
        email: Attempted email address (indexed for lookups)
        ip_address: IP address of the client
        user_agent: User agent string
        success: Whether login was successful
        failure_reason: Reason for failure (e.g., "invalid_password", "account_locked")
        attempted_at: Timestamp of login attempt
        user_id: Foreign key to users table (nullable, only if user found)

    Relationships:
        user: The user this attempt belongs to (if user exists)

    Indexes:
        - email (for user-specific lockout queries)
        - ip_address (for IP-based rate limiting)
        - attempted_at (for time-windowed queries)
        - user_id (for user-specific audit)

    Security:
        - Track failed attempts for account lockout (5 attempts = 30 min lockout)
        - IP-based rate limiting to prevent distributed attacks
        - Audit trail for security investigations
        - Failure reason tracking for analytics

    Performance:
        - Indexes optimize time-windowed queries (last 30 minutes)
        - Cleanup old attempts periodically (retention policy)
    """
    __tablename__ = "login_attempts"

    # Primary Key
    id = Column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique attempt identifier"
    )

    # Attempt Information
    email = Column(
        String(255),
        nullable=False,
        index=True,
        doc="Attempted email address (indexed for lockout queries)"
    )
    ip_address = Column(
        String(45),  # IPv6 max length
        nullable=False,
        index=True,
        doc="IP address of the client"
    )
    user_agent = Column(
        Text,
        nullable=True,
        doc="User agent string"
    )

    # Attempt Result
    success = Column(
        Boolean,
        nullable=False,
        doc="Whether login was successful"
    )
    failure_reason = Column(
        String(100),
        nullable=True,
        doc="Reason for failure (e.g., 'invalid_password', 'account_locked')"
    )

    # Timestamp
    attempted_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        doc="Timestamp of login attempt"
    )

    # Optional Foreign Key (only if user exists)
    user_id = Column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="User this attempt belongs to (if user found)"
    )

    # Relationships
    user = relationship("User", back_populates="login_attempts")

    def __repr__(self) -> str:
        """String representation of LoginAttempt."""
        return (
            f"<LoginAttempt(id={self.id}, email={self.email}, "
            f"success={self.success}, attempted_at={self.attempted_at})>"
        )


# Create indexes explicitly for better control
Index("idx_user_sessions_user_id", UserSession.user_id)
Index("idx_user_sessions_session_token", UserSession.session_token, unique=True)
Index("idx_user_sessions_expires_at", UserSession.expires_at)
Index("idx_user_sessions_is_active", UserSession.is_active)

Index("idx_login_attempts_email", LoginAttempt.email)
Index("idx_login_attempts_ip_address", LoginAttempt.ip_address)
Index("idx_login_attempts_attempted_at", LoginAttempt.attempted_at)
Index("idx_login_attempts_user_id", LoginAttempt.user_id)
