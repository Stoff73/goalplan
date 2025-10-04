"""
User profile retrieval and update endpoints.

Endpoints:
- GET /api/v1/user/profile - Get current user's profile
- PATCH /api/v1/user/profile - Update current user's profile
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth import get_current_active_user
from models.user import User, UserStatus
from models.two_factor import User2FA
from schemas.profile import (
    UserProfileResponse,
    ProfileUpdateRequest,
    ProfileUpdateResponse,
)
from services.profile import profile_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Get the authenticated user's profile information (alias for /profile)",
)
async def get_current_user_profile(
    user_id: str = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the current user's profile.

    This is an alias for GET /profile following REST conventions where
    /me refers to the currently authenticated user.

    Requires authentication via JWT access token.

    Returns:
        UserProfileResponse: User profile data
    """
    return await _get_user_profile(user_id, db)


async def _get_user_profile(user_id: str, db: AsyncSession):
    """Shared implementation for getting user profile."""
    try:
        # Get user with 2FA status
        stmt = (
            select(User, User2FA)
            .outerjoin(User2FA, User2FA.user_id == User.id)
            .where(User.id == UUID(user_id))
        )
        result = await db.execute(stmt)
        user_and_2fa = result.one_or_none()

        if not user_and_2fa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user, user_2fa = user_and_2fa

        # Check if user is active
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active",
            )

        return UserProfileResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            country_preference=user.country_preference.value,
            email_verified=user.email_verified,
            two_factor_enabled=(user_2fa.enabled if user_2fa else False),
            status=user.status.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile",
        )


@router.get(
    "/profile",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User Profile",
    description="Get the authenticated user's profile information",
)
async def get_profile(
    user_id: str = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the current user's profile.

    Requires authentication via JWT access token.

    Returns:
        UserProfileResponse: User profile data

    Raises:
        401: Unauthorized (invalid/expired token)
        403: Forbidden (user not ACTIVE)
        404: User not found
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

        # Check if 2FA is enabled
        result_2fa = await db.execute(
            select(User2FA).where(User2FA.user_id == UUID(user_id))
        )
        two_fa = result_2fa.scalar_one_or_none()
        two_factor_enabled = two_fa.enabled if two_fa else False

        # Build response
        response = UserProfileResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            date_of_birth=user.date_of_birth,
            address=user.address,
            timezone=user.timezone,
            status=user.status.value,
            email_verified=user.email_verified,
            two_factor_enabled=two_factor_enabled,
            country_preference=user.country_preference.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

        logger.info(f"Profile retrieved for user {user_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving profile for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile",
        )


@router.patch(
    "/profile",
    response_model=ProfileUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update User Profile",
    description="Update the authenticated user's profile (partial update supported)",
)
async def update_profile(
    profile_update: ProfileUpdateRequest,
    request: Request,
    user_id: str = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the current user's profile.

    Supports partial updates (PATCH semantics). Only provided fields are updated.
    All changes are logged to the audit trail.

    Updatable Fields:
    - firstName: User's first name
    - lastName: User's last name
    - phone: Phone number (international format)
    - dateOfBirth: Date of birth (must be 18+)
    - address: Address object (line1, line2, city, postcode, country)
    - timezone: Timezone preference

    Returns:
        ProfileUpdateResponse: Updated profile and success message

    Raises:
        401: Unauthorized (invalid/expired token)
        403: Forbidden (user not ACTIVE)
        400: Bad Request (validation error)
        404: User not found
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

        # Extract client info for audit trail
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Build updates dictionary (only include provided fields)
        updates = {}

        if profile_update.first_name is not None:
            updates["first_name"] = profile_update.first_name

        if profile_update.last_name is not None:
            updates["last_name"] = profile_update.last_name

        if profile_update.phone is not None:
            updates["phone"] = profile_update.phone

        if profile_update.date_of_birth is not None:
            updates["date_of_birth"] = profile_update.date_of_birth

        if profile_update.address is not None:
            # Convert Pydantic model to dict
            updates["address"] = profile_update.address.model_dump()

        if profile_update.timezone is not None:
            updates["timezone"] = profile_update.timezone

        # If no updates provided, return current profile
        if not updates:
            logger.info(f"No updates provided for user {user_id}")
            # Check if 2FA is enabled
            result_2fa = await db.execute(
                select(User2FA).where(User2FA.user_id == UUID(user_id))
            )
            two_fa = result_2fa.scalar_one_or_none()
            two_factor_enabled = two_fa.enabled if two_fa else False

            user_response = UserProfileResponse(
                id=str(user.id),
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                date_of_birth=user.date_of_birth,
                address=user.address,
                timezone=user.timezone,
                status=user.status.value,
                email_verified=user.email_verified,
                two_factor_enabled=two_factor_enabled,
                country_preference=user.country_preference.value,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )

            return ProfileUpdateResponse(
                success=True,
                message="No changes were made",
                user=user_response,
            )

        # Update profile with audit trail
        updated_user = await profile_service.update_profile(
            db=db,
            user=user,
            updates=updates,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Send notification email (for significant changes)
        # Note: We don't await this to avoid blocking the response
        if "phone" in updates or "address" in updates:
            try:
                await profile_service.send_profile_change_notification(
                    user=updated_user,
                    field_name=list(updates.keys())[0],
                )
            except Exception as e:
                logger.error(f"Failed to send profile change notification: {e}")
                # Don't fail the request if email fails

        # Check if 2FA is enabled
        result_2fa = await db.execute(
            select(User2FA).where(User2FA.user_id == UUID(user_id))
        )
        two_fa = result_2fa.scalar_one_or_none()
        two_factor_enabled = two_fa.enabled if two_fa else False

        # Build response
        user_response = UserProfileResponse(
            id=str(updated_user.id),
            email=updated_user.email,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            phone=updated_user.phone,
            date_of_birth=updated_user.date_of_birth,
            address=updated_user.address,
            timezone=updated_user.timezone,
            status=updated_user.status.value,
            email_verified=updated_user.email_verified,
            two_factor_enabled=two_factor_enabled,
            country_preference=updated_user.country_preference.value,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
        )

        logger.info(f"Profile updated for user {user_id}: {', '.join(updates.keys())}")

        return ProfileUpdateResponse(
            success=True,
            message="Profile updated successfully",
            user=user_response,
        )

    except HTTPException:
        raise
    except ValueError as e:
        # Validation error from Pydantic
        logger.warning(f"Validation error updating profile for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating profile for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        )
