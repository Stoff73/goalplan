"""
Token refresh endpoint.

This module handles JWT access token refresh using valid refresh tokens.

Key features:
- Validates refresh token (JWT signature, expiration, type)
- Verifies session still active and not expired
- Generates new access token ONLY (does NOT issue new refresh token)
- Updates session tracking (last_activity, access_token_jti)
- Security: Token type validation, session validation, expiration checks
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.auth import TokenRefreshRequest, TokenRefreshResponse
from utils.jwt import verify_token, generate_access_token, get_token_jti
from services.session import session_service
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/refresh", response_model=TokenRefreshResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenRefreshResponse:
    """
    Refresh access token using a valid refresh token.

    Process:
    1. Validate refresh token (JWT signature, expiration)
    2. Verify token type is "refresh" (not "access")
    3. Extract refresh token JTI
    4. Look up session by refresh token JTI
    5. Verify session is active and not expired
    6. Extract user_id from refresh token
    7. Generate new access token with same user_id
    8. Update session with new access token JTI
    9. Update session last_activity timestamp
    10. Return new access token

    Args:
        refresh_data: Request containing refresh token
        db: Database session

    Returns:
        TokenRefreshResponse: New access token with expiration

    Raises:
        HTTPException: 401 if refresh token invalid, expired, or wrong type
        HTTPException: 401 if session not found, revoked, or expired
        HTTPException: 500 if token generation or session update fails

    Security:
        - RS256 signature verification
        - Token expiration validation
        - Token type validation (must be "refresh")
        - Session active status check
        - Session expiration check
        - Refresh token can be used multiple times (not invalidated)
        - Access token rotates on each refresh

    Note:
        Refresh tokens remain valid for their full 7-day lifetime.
        Only access tokens are rotated on refresh.
        If a user needs to invalidate all sessions, use logout-all endpoint.
    """
    try:
        # Step 1-2: Validate refresh token and verify type
        try:
            payload = verify_token(refresh_data.refresh_token, token_type="refresh")
        except ValueError as e:
            logger.warning(f"Invalid refresh token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        # Step 3: Extract refresh token JTI (session identifier)
        refresh_token_jti = payload.get("jti")
        if not refresh_token_jti:
            logger.error("Refresh token missing jti claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Extract user_id from token
        user_id_str = payload.get("sub")
        if not user_id_str:
            logger.error("Refresh token missing sub claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Step 4-5: Look up and validate session
        session = await session_service.validate_session(
            db=db,
            session_token=refresh_token_jti,
        )

        if not session:
            logger.warning(f"Session not found or invalid for refresh token: {refresh_token_jti}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or revoked. Please login again.",
            )

        # Verify user_id from token matches session user_id
        if str(session.user_id) != user_id_str:
            logger.error(
                f"User ID mismatch: token={user_id_str}, session={session.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Step 7: Generate new access token
        new_access_token = generate_access_token(session.user_id)
        new_access_token_jti = get_token_jti(new_access_token)

        # Step 8-9: Update session with new access token JTI
        # (validate_session already updated last_activity, but update_access_token will commit)
        await session_service.update_access_token(
            db=db,
            session_token=refresh_token_jti,
            new_access_token_jti=new_access_token_jti,
        )

        logger.info(f"Access token refreshed for user {session.user_id}")

        # Step 10: Return new access token
        return TokenRefreshResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        )

    except HTTPException:
        # Re-raise HTTP exceptions (already handled above)
        raise

    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed. Please try again later.",
        )
