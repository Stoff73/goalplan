"""
Authentication middleware for FastAPI.

This module provides reusable authentication dependencies that can be used
to protect any endpoint. It handles JWT token validation, session verification,
and user context injection.

Key Features:
- JWT token extraction from Authorization header
- Token signature and expiration verification
- Session validation with Redis fast path (<10ms)
- User context injection into endpoints
- Comprehensive error handling with 401 responses
- Optional authentication for public endpoints

Usage:
    @router.get("/protected")
    async def protected_endpoint(user_id: str = Depends(get_current_user)):
        return {"user_id": user_id, "message": "You are authenticated"}

    @router.get("/public")
    async def public_endpoint(user_id: Optional[str] = Depends(get_current_user_optional)):
        if user_id:
            return {"message": "Welcome back!"}
        return {"message": "Welcome guest!"}

Performance:
- Session validation: <10ms (Redis fast path)
- JWT verification: <5ms
- Total auth overhead: <15ms
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from utils.jwt import verify_token
from services.session import session_service
from models.user import UserStatus

logger = logging.getLogger(__name__)


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> str:
    """
    Authentication dependency that returns the current user's ID.

    Extracts and validates JWT token from Authorization header, verifies
    session exists and is active, and returns the authenticated user's ID.

    This is the primary authentication dependency for protected endpoints.

    Args:
        authorization: Authorization header (Bearer token)
        db: Database session

    Returns:
        str: User ID (UUID as string)

    Raises:
        HTTPException: 401 Unauthorized if authentication fails

    Error Cases:
        - 401: Missing Authorization header
        - 401: Invalid Bearer token format
        - 401: Invalid or expired JWT token
        - 401: Session not found or expired
        - 401: Session inactive

    Example:
        @router.get("/protected")
        async def protected_endpoint(user_id: str = Depends(get_current_user)):
            return {"user_id": user_id}
    """
    # Extract token from Authorization header
    token = _extract_bearer_token(authorization)

    # Verify JWT token and extract payload
    payload = _verify_jwt_token(token, token_type="access")

    # Extract user_id and token JTI from payload
    user_id = payload.get("sub")
    access_token_jti = payload.get("jti")

    if not user_id:
        logger.warning("Token missing user ID (sub claim)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
        )

    if not access_token_jti:
        logger.warning(f"Token missing JTI claim for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing token ID",
        )

    # Validate session exists and is active
    session = await session_service.get_session_by_access_token_jti(db, access_token_jti)

    if not session:
        logger.warning(f"Session not found for access token JTI: {access_token_jti}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found or expired",
        )

    # Check if session is valid (active and not expired)
    if not session.is_valid():
        logger.warning(
            f"Invalid session for user {user_id}: "
            f"active={session.is_active}, expires_at={session.expires_at}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found or expired",
        )

    # All checks passed - return user_id
    logger.debug(f"Authentication successful for user {user_id}")
    return user_id


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> Optional[str]:
    """
    Optional authentication dependency.

    Returns user ID if authenticated, None if not. Does not raise exceptions
    for missing/invalid tokens. Useful for public endpoints that want to
    provide different responses for authenticated vs anonymous users.

    Args:
        authorization: Authorization header (Bearer token)
        db: Database session

    Returns:
        Optional[str]: User ID if authenticated, None otherwise

    Example:
        @router.get("/public")
        async def public_endpoint(
            user_id: Optional[str] = Depends(get_current_user_optional)
        ):
            if user_id:
                return {"message": "Welcome back!"}
            return {"message": "Welcome guest!"}
    """
    try:
        return await get_current_user(authorization=authorization, db=db)
    except HTTPException:
        # Authentication failed - return None (guest user)
        return None


async def get_current_active_user(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> str:
    """
    Authentication dependency that ensures user is ACTIVE.

    Builds on get_current_user and additionally checks that the user's
    account status is ACTIVE (not PENDING_VERIFICATION, SUSPENDED, or DELETED).

    Args:
        user_id: User ID from get_current_user dependency
        db: Database session

    Returns:
        str: User ID (if user is ACTIVE)

    Raises:
        HTTPException: 403 Forbidden if user is not ACTIVE

    Example:
        @router.post("/critical-action")
        async def critical_action(user_id: str = Depends(get_current_active_user)):
            # Only ACTIVE users can perform this action
            return {"message": "Action performed"}
    """
    from sqlalchemy import select
    from models.user import User

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        logger.error(f"User {user_id} not found in database (should not happen)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Check if user is ACTIVE
    if user.status != UserStatus.ACTIVE:
        logger.warning(
            f"User {user_id} attempted action with non-ACTIVE status: {user.status.value}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status.value}. Please contact support.",
        )

    return user_id


def _extract_bearer_token(authorization: Optional[str]) -> str:
    """
    Extract Bearer token from Authorization header.

    Args:
        authorization: Authorization header value

    Returns:
        str: JWT token

    Raises:
        HTTPException: 401 if token missing or invalid format
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    parts = authorization.split()

    if len(parts) != 2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>",
        )

    if parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>",
        )

    return parts[1]


def _verify_jwt_token(token: str, token_type: str = "access") -> dict:
    """
    Verify JWT token signature and expiration.

    Args:
        token: JWT token to verify
        token_type: Expected token type ("access" or "refresh")

    Returns:
        dict: Token payload with claims

    Raises:
        HTTPException: 401 if token invalid or expired
    """
    try:
        payload = verify_token(token, token_type=token_type)
        return payload

    except ValueError as e:
        # JWT verification errors (expired, invalid signature, etc.)
        error_message = str(e).lower()

        # Provide more specific error messages for common cases
        if "expired" in error_message:
            detail = "Token has expired"
        elif "signature" in error_message:
            detail = "Invalid token signature"
        elif "type" in error_message:
            detail = f"Invalid token type. Expected {token_type} token"
        else:
            detail = "Invalid token"

        logger.warning(f"JWT verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )

    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )
