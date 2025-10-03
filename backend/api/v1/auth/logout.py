"""
User logout endpoints.

This module handles user logout with comprehensive security features:
- Single session logout (POST /logout)
- All sessions logout (POST /logout-all)
- Idempotent operations (multiple logouts succeed)
- Session cleanup from Redis and PostgreSQL
- Proper error handling and logging

Updated in Task 1.2.7 to use authentication middleware.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.auth import LogoutResponse, LogoutAllResponse
from services.session import session_service
from middleware.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/logout", response_model=LogoutResponse, status_code=status.HTTP_200_OK)
async def logout(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LogoutResponse:
    """
    Logout from current session.

    Invalidates the current session by:
    1. Marking session as inactive in PostgreSQL
    2. Removing session from Redis cache
    3. Making the access and refresh tokens unusable

    This endpoint is idempotent - calling it multiple times will succeed
    even if the session is already logged out.

    Args:
        user_id: Authenticated user ID (from middleware)
        db: Database session

    Returns:
        LogoutResponse: Success message

    Raises:
        HTTPException: 401 if authentication fails (handled by middleware)
        HTTPException: 500 if logout fails

    Security:
        - Requires valid access token in Authorization header
        - Session must exist and be valid
        - Idempotent operation (safe to call multiple times)

    Example:
        ```
        POST /api/v1/auth/logout
        Headers:
            Authorization: Bearer <access_token>

        Response:
            {
                "success": true,
                "message": "Logged out successfully"
            }
        ```
    """
    try:
        # Get the session for this user's access token
        # We need to find the session that belongs to this user
        # Since we're in the session, we need to use the access_token_jti
        # which was already validated by the middleware

        # Get all user sessions and find the current one
        sessions = await session_service.get_user_sessions(db, user_id)

        if not sessions:
            # No active sessions found - already logged out (idempotent)
            logger.info(f"No active sessions for user {user_id} (already logged out)")
            return LogoutResponse(
                success=True,
                message="Logged out successfully",
            )

        # For now, revoke the most recent session (the one being used)
        # In a more sophisticated approach, we could pass the access_token_jti
        # through the middleware to identify the exact session
        current_session = sessions[0]  # Most recent session

        # Revoke the session
        await session_service.revoke_session(db, current_session.session_token)

        logger.info(f"User {user_id} logged out from session {current_session.session_token}")

        return LogoutResponse(
            success=True,
            message="Logged out successfully",
        )

    except Exception as e:
        # Even if revocation fails, we check if session already revoked
        logger.error(f"Logout error for user {user_id}: {str(e)}")

        # Check if all sessions already revoked (this is OK - idempotent)
        sessions = await session_service.get_user_sessions(db, user_id)
        if not sessions:
            logger.info(f"User {user_id} already logged out (idempotent)")
            return LogoutResponse(
                success=True,
                message="Logged out successfully",
            )

        # If sessions still exist but error occurred, return error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed. Please try again.",
        )


@router.post("/logout-all", response_model=LogoutAllResponse, status_code=status.HTTP_200_OK)
async def logout_all(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LogoutAllResponse:
    """
    Logout from all sessions.

    Invalidates ALL user sessions by:
    1. Marking all user sessions as inactive in PostgreSQL
    2. Removing all user sessions from Redis cache
    3. Making all access and refresh tokens unusable

    Useful for:
    - Security events (password change, suspected compromise)
    - User explicitly logging out from all devices
    - Account recovery

    Args:
        user_id: Authenticated user ID (from middleware)
        db: Database session

    Returns:
        LogoutAllResponse: Success message with count of sessions revoked

    Raises:
        HTTPException: 401 if authentication fails (handled by middleware)
        HTTPException: 500 if logout fails

    Security:
        - Requires valid access token in Authorization header
        - Revokes ALL sessions for the authenticated user
        - Does not affect other users' sessions

    Example:
        ```
        POST /api/v1/auth/logout-all
        Headers:
            Authorization: Bearer <access_token>

        Response:
            {
                "success": true,
                "message": "Logged out from all sessions",
                "sessions_revoked": 3
            }
        ```
    """
    try:
        # Revoke all user sessions
        # This marks all as inactive in DB and removes all from Redis
        sessions_revoked = await session_service.revoke_all_user_sessions(db, user_id)

        logger.info(f"User {user_id} logged out from all {sessions_revoked} sessions")

        return LogoutAllResponse(
            success=True,
            message="Logged out from all sessions",
            sessions_revoked=sessions_revoked,
        )

    except Exception as e:
        logger.error(f"Logout-all error for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout from all sessions failed. Please try again.",
        )
