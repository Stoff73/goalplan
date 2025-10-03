"""
User email change endpoints.

Endpoints:
- POST /api/v1/user/change-email - Request email change
- POST /api/v1/user/verify-email-change - Verify email change with token
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth import get_current_active_user
from models.user import User
from schemas.profile import (
    ChangeEmailRequest,
    ChangeEmailResponse,
    VerifyEmailChangeRequest,
    VerifyEmailChangeResponse,
)
from utils.password import verify_password
from services.profile import profile_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/change-email",
    response_model=ChangeEmailResponse,
    status_code=status.HTTP_200_OK,
    summary="Request Email Change",
    description="Request to change the user's email address (requires verification)",
)
async def change_email(
    email_request: ChangeEmailRequest,
    user_id: str = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Request email change for the current user.

    Flow:
    1. Verify current password for security
    2. Check new email is not already in use
    3. Create email change verification token
    4. Send verification email to NEW email address
    5. Send notification email to OLD email address
    6. Email is updated only after verification

    Security:
    - Password confirmation required
    - Both old and new email notified
    - Token expires in 24 hours
    - Single-use token

    Returns:
        ChangeEmailResponse: Success message

    Raises:
        401: Unauthorized (wrong password or invalid token)
        403: Forbidden (user not ACTIVE)
        400: Bad Request (validation error)
        404: User not found
        409: Conflict (email already in use)
    """
    try:
        # Fetch user from database
        result = await db.execute(
            select(User).where(User.id == UUID(user_id))
        )
        user = result.scalar_one_or_none()

        if not user:
            logger.error(f"User {user_id} not found in database")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Verify password
        if not verify_password(email_request.password, user.password_hash):
            logger.warning(f"Invalid password for email change request from user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password is incorrect",
            )

        # Check if new email is same as current
        if email_request.new_email.lower() == user.email.lower():
            logger.warning(f"User {user_id} tried to change to same email")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New email must be different from current email",
            )

        # Check if new email is already in use
        result = await db.execute(
            select(User).where(User.email == email_request.new_email.lower())
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            logger.warning(
                f"User {user_id} tried to change to email already in use: {email_request.new_email}"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email address is already in use",
            )

        # Create email change token
        email_token = await profile_service.create_email_change_token(
            db=db,
            user=user,
            new_email=email_request.new_email,
        )

        # Send verification email to NEW email
        try:
            await profile_service.send_email_change_verification(
                new_email=email_request.new_email,
                user_name=user.first_name,
                token=email_token.token,
            )
        except Exception as e:
            logger.error(f"Failed to send email change verification: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email",
            )

        # Send notification to OLD email
        try:
            await profile_service.send_email_change_notification(
                old_email=user.email,
                user_name=user.first_name,
            )
        except Exception as e:
            logger.error(f"Failed to send email change notification to old email: {e}")
            # Don't fail the request if this email fails

        logger.info(
            f"Email change requested for user {user_id}: {user.email} -> {email_request.new_email}"
        )

        return ChangeEmailResponse(
            success=True,
            message="Verification email sent to your new email address. Please check your inbox.",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting email change for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request email change",
        )


@router.post(
    "/verify-email-change",
    response_model=VerifyEmailChangeResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify Email Change",
    description="Verify email change using token from verification email",
)
async def verify_email_change(
    verification_request: VerifyEmailChangeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify email change using verification token.

    This endpoint does NOT require authentication because the user
    may be accessing it from the new email account without being logged in.

    The token itself provides authentication.

    Flow:
    1. Validate token (not expired, not used)
    2. Update user's email address
    3. Mark token as used
    4. Log change to audit trail

    Returns:
        VerifyEmailChangeResponse: Success message with new email

    Raises:
        400: Bad Request (invalid/expired/used token)
        404: Token not found
    """
    try:
        # Verify token
        email_token = await profile_service.verify_email_change_token(
            db=db,
            token=verification_request.token,
        )

        if not email_token:
            logger.warning(f"Invalid email change token: {verification_request.token}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        # Fetch user
        result = await db.execute(
            select(User).where(User.id == email_token.user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            logger.error(f"User {email_token.user_id} not found for email change")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Check if new email is still available (could have been taken since request)
        result = await db.execute(
            select(User).where(User.email == email_token.new_email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user and existing_user.id != user.id:
            logger.warning(
                f"Email {email_token.new_email} taken since email change request"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email address is no longer available",
            )

        # Update user's email
        old_email = user.email
        user.email = email_token.new_email
        await db.commit()

        # Log change to audit trail
        await profile_service.log_profile_change(
            db=db,
            user_id=user.id,
            field_name="email",
            old_value=old_email,
            new_value=email_token.new_email,
        )

        logger.info(
            f"Email changed for user {user.id}: {old_email} -> {email_token.new_email}"
        )

        return VerifyEmailChangeResponse(
            success=True,
            message="Email address updated successfully",
            email=email_token.new_email,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying email change: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email change",
        )
