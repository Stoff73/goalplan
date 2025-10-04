"""
User login endpoints.

This module handles user authentication and login with security features:
- Rate limiting (5 attempts per IP per 15 minutes)
- Account lockout after 5 failed attempts
- Login attempt logging
- Session management with JWT tokens
- Device tracking
"""

import logging
from datetime import datetime
from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.user import User, UserStatus
from models.two_factor import User2FA
from schemas.auth import LoginRequest, LoginResponse, UserInfo
from schemas.two_factor import Login2FARequiredResponse
from utils.password import verify_password
from utils.jwt import generate_access_token, generate_refresh_token, get_token_jti
from services.session import session_service
from services.login_attempt import login_attempt_service
from services.totp import TOTPService
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.

    Checks X-Forwarded-For and X-Real-IP headers for proxy support.

    Args:
        request: FastAPI request object

    Returns:
        str: Client IP address
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """
    Extract user agent from request.

    Args:
        request: FastAPI request object

    Returns:
        str: User agent string
    """
    return request.headers.get("User-Agent", "unknown")


@router.post("/login", response_model=Union[LoginResponse, Login2FARequiredResponse], status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Union[LoginResponse, Login2FARequiredResponse]:
    """
    Authenticate user and create session.

    Process (13-step flow from userAuth.md Feature 1.2):
    1. Rate limit check (5 attempts per IP per 15 min) - handled by decorator
    2. Fetch user by email (case-insensitive)
    3. Check account status (must be ACTIVE)
    4. Verify password hash
    5. Skip 2FA for now (will be added in future)
    6. Skip device trust check for now (will be added in future)
    7. Generate access token (JWT, 15 min expiry)
    8. Generate refresh token (JWT, 7 days expiry)
    9. Store session in Redis and PostgreSQL
    10. Update last_login_at timestamp
    11. Log login event (success)
    12. Skip notification for now (will be added in future)
    13. Return tokens and user data

    Args:
        request: FastAPI request object
        response: FastAPI response object
        login_data: Login credentials and device info
        db: Database session

    Returns:
        LoginResponse: Access token, refresh token, and user info

    Raises:
        HTTPException: 401 if credentials invalid
        HTTPException: 403 if account not verified or suspended
        HTTPException: 423 if account locked
        HTTPException: 429 if rate limit exceeded (handled by decorator)
        HTTPException: 500 if login fails

    Security:
        - Rate limited (5 attempts per 15 min per IP)
        - Account lockout after 5 failed attempts in 30 min
        - All attempts logged for audit trail
        - Password verified using constant-time comparison
        - JWT tokens with RS256 signing
        - Session stored in Redis + PostgreSQL
    """
    ip_address = get_client_ip(request)
    user_agent = login_data.device_info or get_user_agent(request)

    try:
        # Step 2: Fetch user by email (case-insensitive)
        stmt = select(User).where(User.email == login_data.email.lower())
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        # If user not found, log failed attempt and return generic error
        if not user:
            await login_attempt_service.log_login_attempt(
                db=db,
                email=login_data.email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason="invalid_credentials",
            )
            logger.warning(f"Login attempt for non-existent user: {login_data.email} from {ip_address}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Check for account lockout (5 failed attempts in last 30 min)
        failed_attempts = await login_attempt_service.get_recent_failed_attempts(
            db=db,
            email=user.email,
            minutes=settings.ACCOUNT_LOCKOUT_DURATION_MINUTES,
        )

        if failed_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            await login_attempt_service.log_login_attempt(
                db=db,
                email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                user_id=user.id,
                failure_reason="account_locked",
            )
            logger.warning(f"Account locked: {user.email} from {ip_address}")
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account temporarily locked due to multiple failed login attempts. "
                       f"Please try again in {settings.ACCOUNT_LOCKOUT_DURATION_MINUTES} minutes.",
            )

        # Step 3: Check account status (must be ACTIVE)
        if user.status == UserStatus.PENDING_VERIFICATION:
            await login_attempt_service.log_login_attempt(
                db=db,
                email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                user_id=user.id,
                failure_reason="email_not_verified",
            )
            logger.warning(f"Login attempt for unverified account: {user.email} from {ip_address}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email address before logging in. Check your inbox for the verification link.",
            )

        if user.status == UserStatus.SUSPENDED:
            await login_attempt_service.log_login_attempt(
                db=db,
                email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                user_id=user.id,
                failure_reason="account_suspended",
            )
            logger.warning(f"Login attempt for suspended account: {user.email} from {ip_address}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been suspended. Please contact support for assistance.",
            )

        if user.status == UserStatus.DELETED:
            await login_attempt_service.log_login_attempt(
                db=db,
                email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                user_id=user.id,
                failure_reason="account_deleted",
            )
            logger.warning(f"Login attempt for deleted account: {user.email} from {ip_address}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deleted.",
            )

        # Step 4: Verify password hash
        if not verify_password(login_data.password, user.password_hash):
            await login_attempt_service.log_login_attempt(
                db=db,
                email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                user_id=user.id,
                failure_reason="invalid_password",
            )
            logger.warning(f"Invalid password for user: {user.email} from {ip_address}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Step 5: Check if 2FA is enabled
        result_2fa = await db.execute(
            select(User2FA).where(User2FA.user_id == user.id)
        )
        user_2fa = result_2fa.scalar_one_or_none()

        if user_2fa and user_2fa.enabled:
            # 2FA is enabled - require TOTP code
            if not login_data.totp_code:
                # No TOTP code provided - return 2FA required response
                logger.info(f"2FA required for user: {user.email} from {ip_address}")
                return Login2FARequiredResponse(
                    requires_2fa=True,
                    message="Please provide your 2FA code to complete login",
                )

            # TOTP code provided - verify it
            code_valid = False

            # Check if it's a backup code (8 digits) or TOTP code (6 digits)
            if TOTPService.is_backup_code_format(login_data.totp_code):
                # Validate backup code
                is_valid, matched_hash = TOTPService.validate_backup_codes(
                    login_data.totp_code, user_2fa.backup_codes
                )

                if is_valid:
                    code_valid = True
                    # Remove used backup code
                    updated_codes = [c for c in user_2fa.backup_codes if c != matched_hash]
                    user_2fa.backup_codes = updated_codes
                    user_2fa.last_used_at = datetime.utcnow()
                    await db.commit()
                    logger.info(f"Backup code used for user: {user.email} from {ip_address}")
            else:
                # Validate TOTP code (6 digits)
                code_valid = TOTPService.verify_totp(user_2fa.secret, login_data.totp_code)

                if code_valid:
                    user_2fa.last_used_at = datetime.utcnow()
                    await db.commit()
                    logger.info(f"TOTP code verified for user: {user.email} from {ip_address}")

            if not code_valid:
                # Invalid 2FA code
                await login_attempt_service.log_login_attempt(
                    db=db,
                    email=user.email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    user_id=user.id,
                    failure_reason="invalid_2fa_code",
                )
                logger.warning(f"Invalid 2FA code for user: {user.email} from {ip_address}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired 2FA code",
                )

        # Step 6: Device trust (skipped for now - will be added in future tasks)

        # Step 7: Generate access token (JWT, 15 min expiry)
        access_token = generate_access_token(user.id)
        access_token_jti = get_token_jti(access_token)

        # Step 8: Generate refresh token (JWT, 7 days expiry)
        refresh_token = generate_refresh_token(user.id)
        refresh_token_jti = get_token_jti(refresh_token)

        # Step 9: Store session in Redis and PostgreSQL
        await session_service.create_session(
            db=db,
            user_id=user.id,
            refresh_token_jti=refresh_token_jti,
            access_token_jti=access_token_jti,
            device_info=user_agent,
            ip_address=ip_address,
        )

        # Step 10: Update last_login_at timestamp
        user.last_login_at = datetime.utcnow()
        await db.commit()

        # Step 11: Log login event (success)
        await login_attempt_service.log_login_attempt(
            db=db,
            email=user.email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            user_id=user.id,
        )

        # Step 12: Send notification for new device (skipped for now - will be added in future)

        # Step 13: Return tokens and user data
        logger.info(f"User logged in successfully: {user.email} from {ip_address}")

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            user=UserInfo(
                id=str(user.id),
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                country_preference=user.country_preference.value,
                two_factor_enabled=(user_2fa.enabled if user_2fa else False),
            ),
        )

    except HTTPException:
        # Re-raise HTTP exceptions (already handled above)
        raise

    except Exception as e:
        logger.error(f"Login failed for {login_data.email}: {str(e)}", exc_info=True)

        # Try to log the failed attempt, but don't fail if logging fails
        try:
            await login_attempt_service.log_login_attempt(
                db=db,
                email=login_data.email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason="system_error",
            )
        except Exception as log_error:
            logger.error(f"Failed to log login attempt: {str(log_error)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again later.",
        )
