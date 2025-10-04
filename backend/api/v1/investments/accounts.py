"""
Investment account API endpoints.

This module provides CRUD operations for investment accounts:
- Create account with encrypted account number
- Retrieve accounts with filtering
- Get single account details
- Delete account (soft delete with holdings)

Business logic:
- Encrypt account numbers for security
- Validate account ownership
- Track holdings count per account
- Multi-currency support
- Soft delete with cascade to holdings
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import logging

from database import get_db
from middleware.auth import get_current_user
from models.investment import (
    InvestmentAccount,
    InvestmentHolding,
    AccountType,
    AccountCountry,
    AccountStatus
)
from schemas.investment import (
    CreateAccountRequest,
    AccountResponse
)
from services.investment.portfolio_service import get_portfolio_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# CRUD OPERATIONS
# ============================================================================

@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_investment_account(
    data: CreateAccountRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new investment account.

    Business logic:
    1. Validate account type
    2. Encrypt account number (store last 4 for display)
    3. Create account record
    4. Return account with masked account number

    Args:
        data: Investment account creation data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        AccountResponse: Created account details with masked account number

    Raises:
        400: Validation error
        500: Internal server error
    """
    try:
        # Get portfolio service
        portfolio_service = get_portfolio_service(db)

        # Create account
        account = await portfolio_service.create_account(
            user_id=UUID(current_user_id),
            account_type=data.account_type,
            provider=data.provider,
            account_number=data.account_number,
            country=data.country,
            base_currency=data.base_currency,
            account_open_date=data.account_open_date
        )

        logger.info(
            f"Created investment account {account.id} for user {current_user_id}: "
            f"{data.provider} ({data.account_type.value})"
        )

        return await _map_account_to_response(account, db)

    except ValueError as e:
        logger.error(f"Validation error creating investment account: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create investment account: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create investment account: {str(e)}"
        )


@router.get("/accounts", response_model=List[AccountResponse])
async def get_all_accounts(
    current_user_id: str = Depends(get_current_user),
    account_type: Optional[AccountType] = Query(None, description="Filter by account type"),
    country: Optional[AccountCountry] = Query(None, description="Filter by country"),
    status_filter: Optional[AccountStatus] = Query(None, alias="status", description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all investment accounts for the authenticated user.

    Supports filtering by:
    - account_type: STOCKS_ISA, GIA, VCT, etc.
    - country: UK, SA, OFFSHORE
    - status: ACTIVE, CLOSED
    - Pagination with skip and limit

    Args:
        current_user_id: Authenticated user ID
        account_type: Optional account type filter
        country: Optional country filter
        status_filter: Optional status filter
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List[AccountResponse]: List of accounts with holdings count
    """
    try:
        # Build query with filters
        conditions = [
            InvestmentAccount.user_id == UUID(current_user_id),
            InvestmentAccount.deleted == False  # Exclude soft-deleted
        ]

        if account_type is not None:
            conditions.append(InvestmentAccount.account_type == account_type)

        if country is not None:
            conditions.append(InvestmentAccount.country == country)

        if status_filter is not None:
            conditions.append(InvestmentAccount.status == status_filter)

        stmt = (
            select(InvestmentAccount)
            .where(and_(*conditions))
            .order_by(InvestmentAccount.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)
        accounts = result.scalars().all()

        # Map to response with holdings count
        responses = []
        for account in accounts:
            response = await _map_account_to_response(account, db)
            responses.append(response)

        return responses

    except Exception as e:
        logger.error(f"Failed to retrieve investment accounts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve investment accounts"
        )


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single investment account by ID.

    Verifies ownership before returning account details.

    Args:
        account_id: Account UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        AccountResponse: Account details with holdings count

    Raises:
        404: Account not found or not owned by user
    """
    account = await _get_account_or_404(account_id, UUID(current_user_id), db)
    return await _map_account_to_response(account, db)


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete an investment account.

    Sets deleted=True and cascades to all holdings.
    Retains data for audit trail.

    Args:
        account_id: Account UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        204 No Content on success

    Raises:
        404: Account not found or not owned by user
        500: Internal server error
    """
    try:
        account = await _get_account_or_404(account_id, UUID(current_user_id), db)

        # Soft delete account
        account.deleted = True
        account.status = AccountStatus.CLOSED

        # Soft delete all holdings in this account
        holdings_stmt = select(InvestmentHolding).where(
            InvestmentHolding.account_id == account_id
        )
        holdings_result = await db.execute(holdings_stmt)
        holdings = holdings_result.scalars().all()

        for holding in holdings:
            holding.deleted = True

        await db.commit()

        logger.info(
            f"Soft deleted investment account {account_id} and {len(holdings)} holdings "
            f"for user {current_user_id}"
        )

        return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete investment account: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete investment account"
        )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _get_account_or_404(
    account_id: UUID,
    user_id: UUID,
    db: AsyncSession
) -> InvestmentAccount:
    """
    Get investment account or raise 404.

    Verifies ownership and excludes soft-deleted accounts.

    Args:
        account_id: Account UUID
        user_id: User UUID
        db: Database session

    Returns:
        InvestmentAccount: Account if found and owned by user

    Raises:
        HTTPException: 404 if not found or not owned
    """
    stmt = select(InvestmentAccount).where(
        and_(
            InvestmentAccount.id == account_id,
            InvestmentAccount.user_id == user_id,
            InvestmentAccount.deleted == False
        )
    )

    result = await db.execute(stmt)
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investment account {account_id} not found"
        )

    return account


async def _map_account_to_response(
    account: InvestmentAccount,
    db: AsyncSession
) -> AccountResponse:
    """
    Map InvestmentAccount model to response schema.

    Masks account number (only last 4 digits shown).
    Counts holdings for the account.

    Args:
        account: InvestmentAccount model instance
        db: Database session

    Returns:
        AccountResponse: Response schema
    """
    # Get account number (last 4 digits)
    try:
        account_number = account.get_account_number()
        # Mask all but last 4 digits
        if len(account_number) > 4:
            account_number = "****" + account_number[-4:]
    except Exception:
        account_number = "****"

    # Count holdings
    holdings_count_stmt = select(func.count(InvestmentHolding.id)).where(
        and_(
            InvestmentHolding.account_id == account.id,
            InvestmentHolding.deleted == False
        )
    )
    holdings_count_result = await db.execute(holdings_count_stmt)
    holdings_count = holdings_count_result.scalar() or 0

    return AccountResponse(
        id=account.id,
        user_id=account.user_id,
        account_type=account.account_type,
        provider=account.provider,
        account_number=account_number,
        country=account.country,
        base_currency=account.base_currency,
        account_open_date=account.account_open_date,
        status=account.status,
        deleted=account.deleted,
        holdings_count=holdings_count,
        created_at=account.created_at,
        updated_at=account.updated_at
    )
