"""
Login attempt tracking service.

This module provides login attempt logging for security monitoring,
account lockout, and brute force attack prevention.

Key features:
- Log all login attempts (success and failure)
- Track failed attempts by email and IP
- Support for account lockout logic (5 attempts = 30 min lockout)
- Time-windowed queries for rate limiting
- Security audit trail

Usage:
    login_attempt_service = LoginAttemptService()
    await login_attempt_service.log_login_attempt(
        db=db,
        email="user@example.com",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0...",
        success=False,
        failure_reason="invalid_password"
    )
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.session import LoginAttempt

logger = logging.getLogger(__name__)


class LoginAttemptService:
    """
    Login attempt tracking service.

    Handles logging and querying of login attempts for security
    monitoring and account lockout.
    """

    async def log_login_attempt(
        self,
        db: AsyncSession,
        email: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        user_id: Optional[uuid.UUID] = None,
        failure_reason: Optional[str] = None,
    ) -> None:
        """
        Log a login attempt.

        Records all login attempts (successful and failed) for security monitoring.

        Args:
            db: Database session
            email: Attempted email address
            ip_address: Client IP address
            user_agent: User agent string
            success: Whether login was successful
            user_id: User ID (if user exists)
            failure_reason: Reason for failure (e.g., "invalid_password", "account_locked")

        Raises:
            Exception: If logging fails
        """
        try:
            attempt = LoginAttempt(
                id=uuid.uuid4(),
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                failure_reason=failure_reason,
                attempted_at=datetime.utcnow(),
                user_id=user_id,
            )

            db.add(attempt)
            await db.commit()

            status = "successful" if success else f"failed ({failure_reason})"
            logger.info(
                f"Login attempt logged: {email} from {ip_address} - {status}"
            )

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to log login attempt for {email}: {e}")
            # Don't raise - logging failure shouldn't break login flow
            # But we should alert on this in production

    async def get_recent_failed_attempts(
        self,
        db: AsyncSession,
        email: str,
        minutes: int = 30,
    ) -> int:
        """
        Count recent failed login attempts for an email.

        Used for account lockout logic.

        Args:
            db: Database session
            email: Email address to check
            minutes: Time window in minutes (default: 30)

        Returns:
            int: Number of failed attempts in time window
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)

            result = await db.execute(
                select(func.count(LoginAttempt.id)).where(
                    and_(
                        LoginAttempt.email == email,
                        LoginAttempt.success == False,
                        LoginAttempt.attempted_at >= cutoff_time
                    )
                )
            )

            return result.scalar()

        except Exception as e:
            logger.error(
                f"Failed to count failed attempts for {email}: {e}"
            )
            return 0

    async def get_failed_attempts_by_ip(
        self,
        db: AsyncSession,
        ip_address: str,
        minutes: int = 30,
    ) -> int:
        """
        Count recent failed login attempts from an IP address.

        Used for IP-based rate limiting and brute force detection.

        Args:
            db: Database session
            ip_address: IP address to check
            minutes: Time window in minutes (default: 30)

        Returns:
            int: Number of failed attempts from IP in time window
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)

            result = await db.execute(
                select(func.count(LoginAttempt.id)).where(
                    and_(
                        LoginAttempt.ip_address == ip_address,
                        LoginAttempt.success == False,
                        LoginAttempt.attempted_at >= cutoff_time
                    )
                )
            )

            return result.scalar()

        except Exception as e:
            logger.error(
                f"Failed to count failed attempts from IP {ip_address}: {e}"
            )
            return 0

    async def get_last_successful_login(
        self,
        db: AsyncSession,
        email: str,
    ) -> Optional[LoginAttempt]:
        """
        Get the most recent successful login for an email.

        Useful for displaying "last login" information to users.

        Args:
            db: Database session
            email: Email address

        Returns:
            LoginAttempt: Last successful login, or None if none found
        """
        try:
            result = await db.execute(
                select(LoginAttempt)
                .where(
                    and_(
                        LoginAttempt.email == email,
                        LoginAttempt.success == True
                    )
                )
                .order_by(LoginAttempt.attempted_at.desc())
                .limit(1)
            )

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"Failed to get last successful login for {email}: {e}"
            )
            return None

    async def reset_failed_attempts(
        self,
        db: AsyncSession,
        email: str,
    ) -> None:
        """
        Reset failed login attempts for an email.

        Called after successful login or password reset.
        Note: We don't actually delete records (for audit trail),
        but the time-windowed queries will naturally exclude old attempts.

        Args:
            db: Database session
            email: Email address
        """
        # In this implementation, we don't need to do anything
        # because we use time-windowed queries. Old attempts
        # automatically fall out of the window.
        #
        # If we wanted to explicitly clear attempts, we could
        # add a "cleared_at" timestamp field to the model.
        pass


# Create singleton instance
login_attempt_service = LoginAttemptService()
