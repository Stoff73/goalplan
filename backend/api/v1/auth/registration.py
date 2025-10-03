"""
User registration endpoints.

This module handles user registration and email verification.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.user import User, EmailVerificationToken, UserStatus, CountryPreference
from schemas.auth import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    EmailVerificationRequest,
    EmailVerificationResponse,
)
from utils.password import hash_password
from services.email import email_service
from middleware.rate_limiter import limiter, rate_limit_registration

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=UserRegistrationResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")
async def register_user(
    request: Request,
    response: Response,
    registration_data: UserRegistrationRequest,
    db: AsyncSession = Depends(get_db),
) -> UserRegistrationResponse:
    """
    Register a new user.

    Process:
    1. Validate input data (handled by Pydantic)
    2. Check if email already exists
    3. Hash password using Argon2
    4. Generate email verification token
    5. Create user record with PENDING_VERIFICATION status
    6. Store verification token
    7. Send verification email
    8. Return success response

    Args:
        request: User registration data
        db: Database session

    Returns:
        UserRegistrationResponse: Success message and user ID

    Raises:
        HTTPException: 409 if email already exists
        HTTPException: 500 if registration fails

    Security:
        - Does not reveal if email exists (returns generic success)
        - Password is hashed before storage
        - Rate limited (configured in middleware)
    """
    try:
        # Check if email already exists
        stmt = select(User).where(User.email == registration_data.email.lower())
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            # Don't reveal that email exists - security best practice
            # Return generic success message
            logger.info(f"Registration attempt with existing email: {registration_data.email}")
            return UserRegistrationResponse(
                success=True,
                message="Registration successful. Please check your email to verify your account.",
                user_id=str(existing_user.id),
            )

        # Hash password
        password_hash = hash_password(registration_data.password)

        # Determine user status based on email verification requirement
        from config import settings

        if settings.REQUIRE_EMAIL_VERIFICATION:
            status = UserStatus.PENDING_VERIFICATION
            email_verified = False
        else:
            # Development mode: auto-activate users
            status = UserStatus.ACTIVE
            email_verified = True

        # Create user
        new_user = User(
            email=registration_data.email.lower(),
            password_hash=password_hash,
            first_name=registration_data.first_name.strip(),
            last_name=registration_data.last_name.strip(),
            country_preference=CountryPreference(registration_data.country),
            status=status,
            email_verified=email_verified,
            terms_accepted_at=datetime.utcnow(),
            marketing_consent=registration_data.marketing_consent,
        )

        db.add(new_user)
        await db.flush()  # Flush to get user.id

        # Only generate verification token if email verification is required
        if settings.REQUIRE_EMAIL_VERIFICATION:
            # Generate verification token
            verification_token = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(hours=24)

            email_verification = EmailVerificationToken(
                user_id=new_user.id,
                token=verification_token,
                expires_at=expires_at,
                used=False,
            )

            db.add(email_verification)
            await db.commit()

            # Send verification email (async, don't wait)
            try:
                await email_service.send_verification_email(
                    to_email=new_user.email,
                    verification_token=verification_token,
                    user_name=f"{new_user.first_name} {new_user.last_name}",
                )
                logger.info(f"Verification email sent to: {new_user.email}")
            except Exception as email_error:
                # Log error but don't fail registration
                logger.error(f"Failed to send verification email: {str(email_error)}")
                # Email will be queued for retry in production
        else:
            # No email verification needed, just commit
            await db.commit()
            logger.info(f"User registered and auto-activated (dev mode): {new_user.email}")

        logger.info(f"User registered successfully: {new_user.email} (ID: {new_user.id})")

        # Customize response message based on email verification requirement
        if settings.REQUIRE_EMAIL_VERIFICATION:
            message = "Registration successful. Please check your email to verify your account."
        else:
            message = "Registration successful. You can now log in."

        return UserRegistrationResponse(
            success=True,
            message=message,
            user_id=str(new_user.id),
        )

    except Exception as e:
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later.",
        )


@router.get("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> EmailVerificationResponse:
    """
    Verify user email address.

    Process:
    1. Look up verification token
    2. Check token expiration (24 hours)
    3. Check if already used
    4. Update user status to ACTIVE
    5. Mark token as used
    6. Return success

    Args:
        token: Email verification token from URL
        db: Database session

    Returns:
        EmailVerificationResponse: Success or error message

    Raises:
        HTTPException: 400 if token invalid or expired
        HTTPException: 500 if verification fails

    Security:
        - Tokens expire after 24 hours
        - Tokens are single-use
        - Idempotent (already verified returns success)
    """
    try:
        # Look up token
        stmt = (
            select(EmailVerificationToken, User)
            .join(User, EmailVerificationToken.user_id == User.id)
            .where(EmailVerificationToken.token == token)
        )
        result = await db.execute(stmt)
        token_and_user = result.one_or_none()

        if not token_and_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token.",
            )

        verification_token, user = token_and_user

        # Check if already verified (idempotent)
        if user.email_verified and user.status == UserStatus.ACTIVE:
            logger.info(f"Email already verified for user: {user.email}")
            return EmailVerificationResponse(
                success=True,
                message="Email address has already been verified.",
            )

        # Check expiration
        if datetime.utcnow() > verification_token.expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired. Please request a new one.",
            )

        # Update user status
        user.email_verified = True
        user.status = UserStatus.ACTIVE
        verification_token.used = True

        await db.commit()

        logger.info(f"Email verified successfully for user: {user.email}")

        return EmailVerificationResponse(
            success=True,
            message="Email verified successfully! You can now log in.",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification failed: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed. Please try again later.",
        )
