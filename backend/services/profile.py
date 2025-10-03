"""
User profile management service.

This module provides services for user profile operations including:
- Profile retrieval and updates
- Audit trail tracking for all changes
- Email change verification
- Password changes
- Account deletion (soft delete)

All profile changes are logged to the user_profile_history table for
security monitoring and compliance.
"""

import json
import logging
import uuid
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any, List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.profile import UserProfileHistory, EmailChangeToken
from services.email import email_service

logger = logging.getLogger(__name__)


class ProfileService:
    """
    Service for managing user profiles.

    Handles profile updates, audit trail creation, and related operations.
    """

    async def log_profile_change(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        field_name: str,
        old_value: Any,
        new_value: Any,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserProfileHistory:
        """
        Log a profile field change to the audit trail.

        Args:
            db: Database session
            user_id: User whose profile was changed
            field_name: Name of the changed field
            old_value: Previous value
            new_value: New value
            ip_address: IP address of the request
            user_agent: User agent string

        Returns:
            UserProfileHistory: Created history record
        """
        # Serialize values to text
        old_value_str = self._serialize_value(old_value)
        new_value_str = self._serialize_value(new_value)

        # Create history record
        history_entry = UserProfileHistory(
            id=uuid.uuid4(),
            user_id=user_id,
            field_name=field_name,
            old_value=old_value_str,
            new_value=new_value_str,
            changed_by=user_id,  # Self-service change
            changed_at=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.add(history_entry)
        await db.commit()
        await db.refresh(history_entry)

        logger.info(
            f"Profile change logged: user_id={user_id}, field={field_name}"
        )

        return history_entry

    async def get_profile_history(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        limit: int = 50,
    ) -> List[UserProfileHistory]:
        """
        Get profile change history for a user.

        Args:
            db: Database session
            user_id: User identifier
            limit: Maximum number of records to return

        Returns:
            List[UserProfileHistory]: History records (newest first)
        """
        result = await db.execute(
            select(UserProfileHistory)
            .where(UserProfileHistory.user_id == user_id)
            .order_by(UserProfileHistory.changed_at.desc())
            .limit(limit)
        )

        return result.scalars().all()

    async def update_profile(
        self,
        db: AsyncSession,
        user: User,
        updates: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> User:
        """
        Update user profile fields and log changes.

        Args:
            db: Database session
            user: User to update
            updates: Dictionary of field updates
            ip_address: IP address of request
            user_agent: User agent string

        Returns:
            User: Updated user object
        """
        # Track which fields actually changed
        changed_fields = []

        for field_name, new_value in updates.items():
            # Get old value
            old_value = getattr(user, field_name, None)

            # Skip if value hasn't changed
            if old_value == new_value:
                continue

            # Update the field
            setattr(user, field_name, new_value)

            # Log the change
            await self.log_profile_change(
                db=db,
                user_id=user.id,
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            changed_fields.append(field_name)

        # Commit user updates
        if changed_fields:
            await db.commit()
            await db.refresh(user)

            logger.info(
                f"Profile updated for user {user.id}: {', '.join(changed_fields)}"
            )

        return user

    async def create_email_change_token(
        self,
        db: AsyncSession,
        user: User,
        new_email: str,
    ) -> EmailChangeToken:
        """
        Create an email change verification token.

        Args:
            db: Database session
            user: User requesting email change
            new_email: New email address

        Returns:
            EmailChangeToken: Created token
        """
        # Generate token
        token = str(uuid.uuid4())

        # Calculate expiration (24 hours)
        expires_at = datetime.utcnow() + timedelta(hours=24)

        # Create token record
        email_token = EmailChangeToken(
            id=uuid.uuid4(),
            user_id=user.id,
            new_email=new_email.lower(),
            old_email=user.email,
            token=token,
            expires_at=expires_at,
            used=False,
            created_at=datetime.utcnow(),
        )

        db.add(email_token)
        await db.commit()
        await db.refresh(email_token)

        logger.info(
            f"Email change token created for user {user.id}: {user.email} -> {new_email}"
        )

        return email_token

    async def verify_email_change_token(
        self,
        db: AsyncSession,
        token: str,
    ) -> Optional[EmailChangeToken]:
        """
        Verify and consume an email change token.

        Args:
            db: Database session
            token: Verification token

        Returns:
            EmailChangeToken if valid, None if invalid/expired
        """
        # Find token
        result = await db.execute(
            select(EmailChangeToken).where(EmailChangeToken.token == token)
        )
        email_token = result.scalar_one_or_none()

        if not email_token:
            logger.warning(f"Email change token not found: {token}")
            return None

        # Check if already used
        if email_token.used:
            logger.warning(f"Email change token already used: {token}")
            return None

        # Check if expired
        if email_token.expires_at <= datetime.utcnow():
            logger.warning(f"Email change token expired: {token}")
            return None

        # Mark as used
        email_token.used = True
        email_token.used_at = datetime.utcnow()
        await db.commit()

        logger.info(
            f"Email change token verified for user {email_token.user_id}"
        )

        return email_token

    async def send_profile_change_notification(
        self,
        user: User,
        field_name: str,
    ) -> bool:
        """
        Send email notification about profile change.

        Args:
            user: User whose profile was changed
            field_name: Name of changed field

        Returns:
            bool: True if sent successfully
        """
        field_labels = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "phone": "Phone Number",
            "date_of_birth": "Date of Birth",
            "address": "Address",
            "timezone": "Timezone",
        }

        field_label = field_labels.get(field_name, field_name)

        html_content = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>Profile Update Notification</h2>
    <p>Hello {user.first_name},</p>
    <p>Your <strong>{field_label}</strong> has been updated successfully.</p>
    <p>If you did not make this change, please contact our support team immediately.</p>
    <p>Best regards,<br>The GoalPlan Team</p>
</body>
</html>
"""

        return await email_service.send_email(
            to_email=user.email,
            subject=f"GoalPlan Profile Updated: {field_label}",
            html_content=html_content,
        )

    async def send_password_change_notification(self, user: User) -> bool:
        """
        Send email notification about password change.

        Args:
            user: User whose password was changed

        Returns:
            bool: True if sent successfully
        """
        html_content = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>Password Changed</h2>
    <p>Hello {user.first_name},</p>
    <p>Your password has been changed successfully.</p>
    <p><strong>If you did not make this change, your account may be compromised.
    Please contact our support team immediately and reset your password.</strong></p>
    <p>Best regards,<br>The GoalPlan Team</p>
</body>
</html>
"""

        return await email_service.send_email(
            to_email=user.email,
            subject="GoalPlan Password Changed",
            html_content=html_content,
        )

    async def send_email_change_verification(
        self,
        new_email: str,
        user_name: str,
        token: str,
    ) -> bool:
        """
        Send verification email to new email address.

        Args:
            new_email: New email address to verify
            user_name: User's name
            token: Verification token

        Returns:
            bool: True if sent successfully
        """
        from config import settings

        verification_url = f"{settings.FRONTEND_URL}/verify-email-change?token={token}"

        html_content = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>Verify Your New Email Address</h2>
    <p>Hello {user_name},</p>
    <p>You requested to change your email address on GoalPlan.</p>
    <p>To complete this change, please click the button below:</p>
    <p style="text-align: center; margin: 30px 0;">
        <a href="{verification_url}"
           style="background-color: #0066cc; color: white; padding: 12px 30px;
                  text-decoration: none; border-radius: 4px; display: inline-block;">
            Verify New Email
        </a>
    </p>
    <p>This link will expire in 24 hours.</p>
    <p>If you didn't request this change, please ignore this email.</p>
    <p>Best regards,<br>The GoalPlan Team</p>
</body>
</html>
"""

        return await email_service.send_email(
            to_email=new_email,
            subject="GoalPlan - Verify Your New Email Address",
            html_content=html_content,
        )

    async def send_email_change_notification(
        self,
        old_email: str,
        user_name: str,
    ) -> bool:
        """
        Send notification to old email about email change request.

        Args:
            old_email: Current email address
            user_name: User's name

        Returns:
            bool: True if sent successfully
        """
        html_content = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>Email Change Request</h2>
    <p>Hello {user_name},</p>
    <p>A request has been made to change the email address on your GoalPlan account.</p>
    <p>If you made this request, please check your new email address for a verification link.</p>
    <p><strong>If you did not make this request, please contact our support team immediately
    as your account may be compromised.</strong></p>
    <p>Best regards,<br>The GoalPlan Team</p>
</body>
</html>
"""

        return await email_service.send_email(
            to_email=old_email,
            subject="GoalPlan - Email Change Request",
            html_content=html_content,
        )

    async def send_account_deletion_notification(
        self,
        user: User,
        deletion_date: datetime,
    ) -> bool:
        """
        Send notification about account deletion.

        Args:
            user: User whose account is being deleted
            deletion_date: Date when account will be permanently deleted

        Returns:
            bool: True if sent successfully
        """
        html_content = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>Account Deletion Confirmation</h2>
    <p>Hello {user.first_name},</p>
    <p>Your GoalPlan account has been scheduled for deletion.</p>
    <p><strong>Your data will be permanently deleted on {deletion_date.strftime('%B %d, %Y')}.</strong></p>
    <p>If you change your mind, you can contact our support team before this date to restore your account.</p>
    <p>We're sorry to see you go!</p>
    <p>Best regards,<br>The GoalPlan Team</p>
</body>
</html>
"""

        return await email_service.send_email(
            to_email=user.email,
            subject="GoalPlan Account Deletion Confirmation",
            html_content=html_content,
        )

    def _serialize_value(self, value: Any) -> Optional[str]:
        """
        Serialize a value to text for storage in history.

        Args:
            value: Value to serialize

        Returns:
            str: Serialized value
        """
        if value is None:
            return None

        if isinstance(value, (str, int, float, bool)):
            return str(value)

        if isinstance(value, (date, datetime)):
            return value.isoformat()

        if isinstance(value, dict):
            return json.dumps(value)

        # Default: convert to string
        return str(value)


# Create singleton instance
profile_service = ProfileService()
