"""
Two-factor authentication API endpoints.

This module provides endpoints for:
- Enabling 2FA (setup initiation)
- Verifying 2FA setup (with backup codes)
- Disabling 2FA

All endpoints require authentication (except the initial setup).
"""

from typing import Annotated
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User, User2FA
from schemas.two_factor import (
    Enable2FAResponse,
    Verify2FASetupRequest,
    Verify2FASetupResponse,
    Disable2FARequest,
    Disable2FAResponse,
)
from services.totp import TOTPService
from middleware.auth import get_current_user
from sqlalchemy import select

router = APIRouter()


@router.post(
    "/2fa/enable",
    response_model=Enable2FAResponse,
    status_code=status.HTTP_200_OK,
    summary="Enable 2FA - Initiate Setup",
    description=(
        "Generate TOTP secret and QR code for 2FA setup. "
        "The secret is stored but 2FA is not enabled until verification. "
        "Requires authentication."
    ),
)
async def enable_2fa(
    current_user_id: Annotated[str, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Enable2FAResponse:
    """
    Initiate 2FA setup for the authenticated user.

    Steps:
    1. Check if 2FA is already enabled
    2. Generate new TOTP secret
    3. Generate QR code for authenticator apps
    4. Store secret (encrypted) but don't enable yet
    5. Return secret and QR code to user

    Args:
        current_user_id: Authenticated user ID (from JWT token)
        db: Database session

    Returns:
        Enable2FAResponse: Contains secret and QR code

    Raises:
        HTTPException: 400 if 2FA already enabled
        HTTPException: 500 if database error
    """
    # Get user to access email
    user_result = await db.execute(
        select(User).where(User.id == UUID(current_user_id))
    )
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if 2FA is already enabled
    result = await db.execute(
        select(User2FA).where(User2FA.user_id == UUID(current_user_id))
    )
    existing_2fa = result.scalar_one_or_none()

    if existing_2fa and existing_2fa.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled for this account. Disable it first to re-enable.",
        )

    # Generate TOTP secret
    secret = TOTPService.generate_secret()

    # Generate QR code
    qr_code = TOTPService.generate_qr_code(secret, user.email)

    # Store secret (encrypted) but don't enable yet
    if existing_2fa:
        # Update existing record
        existing_2fa.secret = secret
        existing_2fa.enabled = False
        existing_2fa.backup_codes = []
        existing_2fa.updated_at = datetime.utcnow()
    else:
        # Create new record
        new_2fa = User2FA(
            user_id=UUID(current_user_id),
            secret=secret,
            enabled=False,
            backup_codes=[],
        )
        db.add(new_2fa)

    await db.commit()

    return Enable2FAResponse(
        success=True,
        secret=secret,
        qr_code=qr_code,
        message=(
            "Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.) "
            "or enter the secret manually. Then verify with a code to complete setup."
        ),
    )


@router.post(
    "/2fa/verify-setup",
    response_model=Verify2FASetupResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify 2FA Setup",
    description=(
        "Verify TOTP code to complete 2FA setup. "
        "Returns backup codes (shown only once). "
        "Requires authentication."
    ),
)
async def verify_2fa_setup(
    request: Verify2FASetupRequest,
    current_user_id: Annotated[str, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Verify2FASetupResponse:
    """
    Complete 2FA setup by verifying TOTP code.

    Steps:
    1. Retrieve stored secret
    2. Verify TOTP code
    3. Generate backup codes
    4. Enable 2FA
    5. Return backup codes (shown only once)

    Args:
        request: Contains TOTP code
        current_user_id: Authenticated user ID (from JWT token)
        db: Database session

    Returns:
        Verify2FASetupResponse: Contains backup codes

    Raises:
        HTTPException: 400 if no setup in progress
        HTTPException: 401 if TOTP code is invalid
        HTTPException: 500 if database error
    """
    # Get 2FA record
    result = await db.execute(
        select(User2FA).where(User2FA.user_id == UUID(current_user_id))
    )
    user_2fa = result.scalar_one_or_none()

    if not user_2fa or not user_2fa.secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No 2FA setup in progress. Please initiate 2FA setup first.",
        )

    if user_2fa.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled for this account.",
        )

    # Verify TOTP code
    if not TOTPService.verify_totp(user_2fa.secret, request.totp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired TOTP code. Please try again.",
        )

    # Generate backup codes
    backup_codes = TOTPService.generate_backup_codes()
    hashed_backup_codes = [
        TOTPService.hash_backup_code(code) for code in backup_codes
    ]

    # Enable 2FA and store backup codes
    user_2fa.enabled = True
    user_2fa.backup_codes = hashed_backup_codes
    user_2fa.updated_at = datetime.utcnow()

    await db.commit()

    return Verify2FASetupResponse(
        success=True,
        message=(
            "2FA successfully enabled! "
            "Save these backup codes in a secure location. "
            "Each code can only be used once. "
            "You will need them if you lose access to your authenticator app."
        ),
        backup_codes=backup_codes,
    )


@router.post(
    "/2fa/disable",
    response_model=Disable2FAResponse,
    status_code=status.HTTP_200_OK,
    summary="Disable 2FA",
    description=(
        "Disable 2FA for the account. "
        "Requires password and TOTP/backup code for security. "
        "Requires authentication."
    ),
)
async def disable_2fa(
    request: Disable2FARequest,
    current_user_id: Annotated[str, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Disable2FAResponse:
    """
    Disable 2FA for the authenticated user.

    Security requirements:
    1. Must provide current password
    2. Must provide valid TOTP code or backup code

    Args:
        request: Contains password and TOTP/backup code
        current_user_id: Authenticated user ID (from JWT token)
        db: Database session

    Returns:
        Disable2FAResponse: Success message

    Raises:
        HTTPException: 400 if 2FA not enabled
        HTTPException: 401 if password or code invalid
        HTTPException: 500 if database error
    """
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError

    # Get user to verify password
    user_result = await db.execute(
        select(User).where(User.id == UUID(current_user_id))
    )
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get 2FA record
    result = await db.execute(
        select(User2FA).where(User2FA.user_id == UUID(current_user_id))
    )
    user_2fa = result.scalar_one_or_none()

    if not user_2fa or not user_2fa.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this account.",
        )

    # Verify password
    ph = PasswordHasher()
    try:
        ph.verify(user.password_hash, request.password)
    except VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password.",
        )

    # Verify TOTP code or backup code
    code_valid = False

    if request.totp_code:
        # Check if it's a backup code (8 digits)
        if TOTPService.is_backup_code_format(request.totp_code):
            # Validate backup code
            is_valid, matched_hash = TOTPService.validate_backup_codes(
                request.totp_code, user_2fa.backup_codes
            )
            code_valid = is_valid
        else:
            # Validate TOTP code (6 digits)
            code_valid = TOTPService.verify_totp(user_2fa.secret, request.totp_code)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP code or backup code is required to disable 2FA.",
        )

    if not code_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired TOTP/backup code.",
        )

    # Disable 2FA and remove all data
    await db.delete(user_2fa)
    await db.commit()

    return Disable2FAResponse(
        success=True,
        message="2FA has been successfully disabled for your account.",
    )
