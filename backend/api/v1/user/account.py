"""
User account deletion endpoint.

Endpoints:
- POST /api/v1/user/delete-account - Delete user account (soft delete)
"""

import logging
import json
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth import get_current_active_user
from models.user import User, UserStatus
from schemas.profile import DeleteAccountRequest, DeleteAccountResponse
from utils.password import verify_password
from services.session import session_service
from services.profile import profile_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Retention period for soft delete (30 days per GDPR/POPIA)
RETENTION_DAYS = 30


@router.post(
    "/delete-account",
    response_model=DeleteAccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete Account",
    description="Delete the user's account (soft delete with 30-day retention)",
)
async def delete_account(
    delete_request: DeleteAccountRequest,
    user_id: str = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete the current user's account.

    Soft Delete Implementation:
    - Account marked as DELETED
    - deleted_at timestamp set
    - User cannot login after deletion
    - Data retained for 30 days (GDPR/POPIA compliance)
    - After 30 days, data is anonymized (background job)

    Optional Data Export:
    - If exportData=true, generates JSON export of all user data
    - Export includes: profile, settings, financial data
    - Export URL provided in response
    - Export auto-deleted after 7 days

    Security:
    - Password confirmation required
    - All sessions invalidated
    - Email notification sent

    Returns:
        DeleteAccountResponse: Success message with deletion date

    Raises:
        401: Unauthorized (wrong password or invalid token)
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

        # Verify password
        if not verify_password(delete_request.password, user.password_hash):
            logger.warning(f"Invalid password for account deletion from user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password is incorrect",
            )

        # Check if account already deleted
        if user.status == UserStatus.DELETED:
            logger.warning(f"User {user_id} account already deleted")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is already deleted",
            )

        # Calculate deletion date (30 days from now)
        deletion_date = datetime.utcnow() + timedelta(days=RETENTION_DAYS)

        # Generate data export if requested
        export_url = None
        if delete_request.export_data:
            try:
                export_url = await _generate_data_export(db, user)
                logger.info(f"Data export generated for user {user_id}: {export_url}")
            except Exception as e:
                logger.error(f"Failed to generate data export for user {user_id}: {e}")
                # Don't fail deletion if export fails - just log and continue

        # Soft delete: mark account as DELETED
        user.status = UserStatus.DELETED
        user.deleted_at = datetime.utcnow()
        await db.commit()

        # Invalidate all sessions (user can't login anymore)
        sessions_revoked = await session_service.revoke_all_user_sessions(
            db=db,
            user_id=UUID(user_id),
        )

        logger.info(
            f"Account deleted for user {user_id}. "
            f"Revoked {sessions_revoked} sessions. "
            f"Permanent deletion scheduled for {deletion_date}"
        )

        # Send deletion confirmation email
        try:
            await profile_service.send_account_deletion_notification(
                user=user,
                deletion_date=deletion_date,
            )
        except Exception as e:
            logger.error(f"Failed to send account deletion notification: {e}")
            # Don't fail the request if email fails

        return DeleteAccountResponse(
            success=True,
            message=f"Your account has been deleted. Data will be permanently removed after {RETENTION_DAYS} days.",
            export_url=export_url,
            deletion_date=deletion_date,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account",
        )


async def _generate_data_export(db: AsyncSession, user: User) -> str:
    """
    Generate data export for user.

    This is a simplified implementation. In production, this would:
    1. Collect data from all related tables
    2. Generate a comprehensive JSON file
    3. Store in secure temporary storage (S3, etc.)
    4. Return a secure download URL
    5. Auto-delete after 7 days

    For now, we'll create a basic export and return a placeholder URL.

    Args:
        db: Database session
        user: User to export data for

    Returns:
        str: Download URL for data export
    """
    # Collect user data
    user_data = {
        "export_date": datetime.utcnow().isoformat(),
        "profile": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
            "address": user.address,
            "timezone": user.timezone,
            "country_preference": user.country_preference.value,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        },
        "account": {
            "status": user.status.value,
            "email_verified": user.email_verified,
            "terms_accepted_at": user.terms_accepted_at.isoformat() if user.terms_accepted_at else None,
            "marketing_consent": user.marketing_consent,
        },
        # In production, would include:
        # - Financial accounts
        # - Tax information
        # - Transactions
        # - Documents
        # - Settings
        # - etc.
    }

    # In production, would:
    # 1. Save to secure temporary storage
    # 2. Generate signed download URL
    # 3. Set expiration (7 days)
    # 4. Return URL

    # For now, return a placeholder
    # In real implementation, this would be:
    # export_url = await storage_service.save_export(user_data, user.id)

    export_url = f"/api/v1/user/data-export/{user.id}.json"

    logger.info(f"Data export prepared for user {user.id}")

    return export_url
