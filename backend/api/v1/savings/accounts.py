"""
Savings account API endpoints.

This module provides CRUD operations for savings accounts:
- Create account with ISA/TFSA contribution tracking
- Retrieve accounts with filtering
- Update account details
- Delete account (soft delete)
- Update balance with history tracking
- Get balance history

Business logic:
- Encrypt account numbers for security
- Track ISA/TFSA contributions when balance increases
- Enforce max 10 balance updates per day per account
- Multi-currency support
- Real-time currency conversion
- Summary aggregation across all accounts
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
import logging

from database import get_db
from middleware.auth import get_current_user
from models.savings_account import (
    SavingsAccount,
    AccountBalanceHistory,
    AccountType,
    AccountPurpose,
    AccountCountry,
    Currency
)
from schemas.savings import (
    SavingsAccountCreate,
    SavingsAccountUpdate,
    SavingsAccountResponse,
    SavingsAccountSummary,
    SavingsTotalSummary,
    BalanceHistoryCreate,
    BalanceHistoryResponse
)
from services.isa_tfsa_tracking import ISATrackingService, TFSATrackingService
from services.interest_calculation import InterestCalculationService
from services.emergency_fund_assessment import EmergencyFundAssessmentService
from services.currency_conversion import CurrencyConversionService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# CRUD OPERATIONS
# ============================================================================

@router.post("/accounts", response_model=SavingsAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_savings_account(
    data: SavingsAccountCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new savings account.

    Business logic:
    1. Validate ISA/TFSA mutual exclusivity
    2. Encrypt account number
    3. Create account record
    4. If ISA or TFSA and balance > 0, record initial contribution
    5. Create initial balance history entry

    Args:
        data: Savings account creation data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        SavingsAccountResponse: Created account details

    Raises:
        400: Validation error (ISA/TFSA rules, country mismatch, etc.)
        500: Internal server error
    """
    try:
        # Create savings account
        account = SavingsAccount(
            user_id=UUID(current_user_id),
            bank_name=data.bank_name,
            account_name=data.account_name,
            account_type=data.account_type,
            currency=data.currency,
            current_balance=data.current_balance,
            interest_rate=data.interest_rate,
            interest_payment_frequency=data.interest_payment_frequency,
            is_isa=data.is_isa,
            is_tfsa=data.is_tfsa,
            purpose=data.purpose,
            country=data.country,
            is_active=True
        )

        # Encrypt and set account number
        account.set_account_number(data.account_number)

        db.add(account)
        await db.flush()  # Get ID before committing

        # Create initial balance history entry
        if data.current_balance > 0:
            initial_balance = AccountBalanceHistory(
                savings_account_id=account.id,
                balance=data.current_balance,
                balance_date=date.today(),
                notes="Initial account balance"
            )
            db.add(initial_balance)

        # Record ISA contribution if applicable
        if data.is_isa and data.current_balance > 0 and data.currency == Currency.GBP:
            isa_service = ISATrackingService(db)
            try:
                await isa_service.record_isa_contribution(
                    user_id=UUID(current_user_id),
                    account_id=account.id,
                    amount=data.current_balance,
                    contribution_date=date.today(),
                    notes=f"Initial ISA account balance - {data.account_name}"
                )
                logger.info(
                    f"Recorded ISA contribution of £{data.current_balance} "
                    f"for account {account.id}"
                )
            except ValueError as e:
                # ISA allowance exceeded
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )

        # Record TFSA contribution if applicable
        if data.is_tfsa and data.current_balance > 0 and data.currency == Currency.ZAR:
            tfsa_service = TFSATrackingService(db)
            try:
                await tfsa_service.record_tfsa_contribution(
                    user_id=UUID(current_user_id),
                    account_id=account.id,
                    amount=data.current_balance,
                    contribution_type="DEPOSIT",
                    contribution_date=date.today(),
                    notes=f"Initial TFSA account balance - {data.account_name}"
                )
                logger.info(
                    f"Recorded TFSA contribution of R{data.current_balance} "
                    f"for account {account.id}"
                )
            except ValueError as e:
                # TFSA allowance exceeded
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )

        await db.commit()
        await db.refresh(account)

        logger.info(
            f"Created savings account {account.id} for user {current_user_id}: "
            f"{data.account_name} ({data.account_type.value})"
        )

        return _map_account_to_response(account)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create savings account: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create savings account: {str(e)}"
        )


@router.get("/accounts", response_model=List[SavingsAccountResponse])
async def get_all_accounts(
    current_user_id: str = Depends(get_current_user),
    account_type: Optional[AccountType] = Query(None, description="Filter by account type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    currency: Optional[Currency] = Query(None, description="Filter by currency"),
    purpose: Optional[AccountPurpose] = Query(None, description="Filter by purpose"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all savings accounts for the authenticated user.

    Supports filtering by:
    - account_type: CURRENT, SAVINGS, ISA, TFSA, etc.
    - is_active: true/false
    - currency: GBP, ZAR, USD, EUR
    - purpose: EMERGENCY_FUND, SAVINGS_GOAL, GENERAL

    Args:
        current_user_id: Authenticated user ID
        account_type: Optional account type filter
        is_active: Optional active status filter
        currency: Optional currency filter
        purpose: Optional purpose filter
        db: Database session

    Returns:
        List[SavingsAccountResponse]: List of accounts
    """
    try:
        # Build query with filters
        conditions = [
            SavingsAccount.user_id == UUID(current_user_id),
            SavingsAccount.deleted_at.is_(None)  # Exclude soft-deleted
        ]

        if account_type is not None:
            conditions.append(SavingsAccount.account_type == account_type)

        if is_active is not None:
            conditions.append(SavingsAccount.is_active == is_active)

        if currency is not None:
            conditions.append(SavingsAccount.currency == currency)

        if purpose is not None:
            conditions.append(SavingsAccount.purpose == purpose)

        stmt = select(SavingsAccount).where(and_(*conditions)).order_by(
            SavingsAccount.created_at.desc()
        )

        result = await db.execute(stmt)
        accounts = result.scalars().all()

        return [_map_account_to_response(account) for account in accounts]

    except Exception as e:
        logger.error(f"Failed to retrieve savings accounts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve savings accounts"
        )


@router.get("/accounts/{account_id}", response_model=SavingsAccountResponse)
async def get_account(
    account_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single savings account by ID.

    Verifies ownership before returning account details.

    Args:
        account_id: Account UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        SavingsAccountResponse: Account details

    Raises:
        404: Account not found or not owned by user
    """
    account = await _get_account_or_404(account_id, UUID(current_user_id), db)
    return _map_account_to_response(account)


@router.patch("/accounts/{account_id}", response_model=SavingsAccountResponse)
async def update_account(
    account_id: UUID,
    data: SavingsAccountUpdate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update savings account details.

    Allows partial updates. Cannot change user_id.
    If account_number is updated, it will be re-encrypted.

    Args:
        account_id: Account UUID
        data: Update data (all fields optional)
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        SavingsAccountResponse: Updated account details

    Raises:
        404: Account not found or not owned by user
        400: Validation error
    """
    try:
        account = await _get_account_or_404(account_id, UUID(current_user_id), db)

        # Update fields if provided
        if data.bank_name is not None:
            account.bank_name = data.bank_name

        if data.account_name is not None:
            account.account_name = data.account_name

        if data.account_number is not None:
            account.set_account_number(data.account_number)

        if data.account_type is not None:
            account.account_type = data.account_type

        if data.currency is not None:
            account.currency = data.currency

        if data.current_balance is not None:
            account.current_balance = data.current_balance

        if data.interest_rate is not None:
            account.interest_rate = data.interest_rate

        if data.interest_payment_frequency is not None:
            account.interest_payment_frequency = data.interest_payment_frequency

        if data.purpose is not None:
            account.purpose = data.purpose

        if data.is_active is not None:
            account.is_active = data.is_active

        account.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(account)

        logger.info(f"Updated savings account {account_id} for user {current_user_id}")

        return _map_account_to_response(account)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update savings account: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update savings account"
        )


@router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete a savings account.

    Sets is_active=False and deleted_at timestamp.
    Retains data for audit trail.

    Args:
        account_id: Account UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        dict: Deletion confirmation

    Raises:
        404: Account not found or not owned by user
    """
    try:
        account = await _get_account_or_404(account_id, UUID(current_user_id), db)

        account.is_active = False
        account.deleted_at = datetime.utcnow()

        await db.commit()

        logger.info(f"Soft deleted savings account {account_id} for user {current_user_id}")

        return {
            "message": "Account deleted successfully",
            "account_id": str(account_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete savings account: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete savings account"
        )


# ============================================================================
# BALANCE MANAGEMENT
# ============================================================================

@router.post("/accounts/{account_id}/balance")
async def update_account_balance(
    account_id: UUID,
    data: BalanceHistoryCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update account balance and create history entry.

    Business logic:
    1. Verify ownership
    2. Check max 10 updates per day limit
    3. Create balance history entry
    4. Update account's current_balance
    5. If ISA/TFSA and balance increased, record contribution

    Args:
        account_id: Account UUID
        data: Balance update data (balance, date, notes)
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        dict: Balance update summary with current, previous, and change

    Raises:
        404: Account not found
        409: Too many balance updates (max 10/day)
        400: ISA/TFSA allowance exceeded
    """
    try:
        account = await _get_account_or_404(account_id, UUID(current_user_id), db)

        # Check balance update limit (max 10 per day)
        count_stmt = select(func.count(AccountBalanceHistory.id)).where(
            and_(
                AccountBalanceHistory.savings_account_id == account_id,
                AccountBalanceHistory.balance_date == data.balance_date
            )
        )
        result = await db.execute(count_stmt)
        update_count = result.scalar()

        if update_count >= 10:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Maximum 10 balance updates per day reached. Please try again tomorrow."
            )

        # Store previous balance
        previous_balance = account.current_balance

        # Create balance history entry
        history = AccountBalanceHistory(
            savings_account_id=account_id,
            balance=data.balance,
            balance_date=data.balance_date,
            notes=data.notes
        )
        db.add(history)

        # Update account balance
        account.current_balance = data.balance
        account.updated_at = datetime.utcnow()

        # If ISA and balance increased, record contribution
        if account.is_isa and data.balance > previous_balance:
            contribution_amount = data.balance - previous_balance
            if account.currency == Currency.GBP:
                isa_service = ISATrackingService(db)
                try:
                    await isa_service.record_isa_contribution(
                        user_id=UUID(current_user_id),
                        account_id=account_id,
                        amount=contribution_amount,
                        contribution_date=data.balance_date,
                        notes=f"Balance increase: {data.notes or 'No notes'}"
                    )
                    logger.info(
                        f"Recorded ISA contribution of £{contribution_amount} "
                        f"for account {account_id}"
                    )
                except ValueError as e:
                    # ISA allowance exceeded
                    await db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=str(e)
                    )

        # If TFSA and balance increased, record contribution
        if account.is_tfsa and data.balance > previous_balance:
            contribution_amount = data.balance - previous_balance
            if account.currency == Currency.ZAR:
                tfsa_service = TFSATrackingService(db)
                try:
                    await tfsa_service.record_tfsa_contribution(
                        user_id=UUID(current_user_id),
                        account_id=account_id,
                        amount=contribution_amount,
                        contribution_type="DEPOSIT",
                        contribution_date=data.balance_date,
                        notes=f"Balance increase: {data.notes or 'No notes'}"
                    )
                    logger.info(
                        f"Recorded TFSA contribution of R{contribution_amount} "
                        f"for account {account_id}"
                    )
                except ValueError as e:
                    # TFSA allowance exceeded
                    await db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=str(e)
                    )

        await db.commit()

        change = data.balance - previous_balance

        logger.info(
            f"Updated balance for account {account_id}: "
            f"{previous_balance} → {data.balance} ({change:+})"
        )

        return {
            "current_balance": float(data.balance),
            "previous_balance": float(previous_balance),
            "change": float(change),
            "balance_date": data.balance_date.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update balance: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update account balance"
        )


@router.get("/accounts/{account_id}/balance-history", response_model=List[BalanceHistoryResponse])
async def get_balance_history(
    account_id: UUID,
    current_user_id: str = Depends(get_current_user),
    from_date: Optional[date] = Query(None, description="Start date for filtering"),
    to_date: Optional[date] = Query(None, description="End date for filtering"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get balance history for an account.

    Supports optional date range filtering.

    Args:
        account_id: Account UUID
        current_user_id: Authenticated user ID
        from_date: Optional start date filter
        to_date: Optional end date filter
        db: Database session

    Returns:
        List[BalanceHistoryResponse]: Balance history entries (newest first)

    Raises:
        404: Account not found or not owned by user
    """
    try:
        # Verify ownership
        await _get_account_or_404(account_id, UUID(current_user_id), db)

        # Build query with date filters
        conditions = [AccountBalanceHistory.savings_account_id == account_id]

        if from_date:
            conditions.append(AccountBalanceHistory.balance_date >= from_date)

        if to_date:
            conditions.append(AccountBalanceHistory.balance_date <= to_date)

        stmt = select(AccountBalanceHistory).where(and_(*conditions)).order_by(
            AccountBalanceHistory.balance_date.desc()
        )

        result = await db.execute(stmt)
        history = result.scalars().all()

        return [
            BalanceHistoryResponse(
                id=entry.id,
                savings_account_id=entry.savings_account_id,
                balance=entry.balance,
                balance_date=entry.balance_date,
                notes=entry.notes,
                created_at=entry.created_at
            )
            for entry in history
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve balance history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve balance history"
        )


# ============================================================================
# SUMMARY AND AGGREGATION
# ============================================================================

@router.get("/summary", response_model=SavingsTotalSummary)
async def get_savings_summary(
    current_user_id: str = Depends(get_current_user),
    base_currency: Optional[str] = Query("GBP", description="Base currency for totals"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get summary of all savings accounts.

    Calculates:
    - Total savings by currency
    - Total ISA and TFSA accounts
    - Emergency fund and savings goal totals
    - Projected annual interest

    Args:
        current_user_id: Authenticated user ID
        base_currency: Base currency for conversion (default: GBP)
        db: Database session

    Returns:
        SavingsTotalSummary: Aggregated summary data
    """
    try:
        # Get all active accounts
        stmt = select(SavingsAccount).where(
            and_(
                SavingsAccount.user_id == UUID(current_user_id),
                SavingsAccount.is_active == True,
                SavingsAccount.deleted_at.is_(None)
            )
        )

        result = await db.execute(stmt)
        accounts = result.scalars().all()

        # Initialize aggregations
        total_accounts = len(accounts)
        total_gbp = Decimal('0')
        total_zar = Decimal('0')
        total_usd = Decimal('0')
        total_eur = Decimal('0')
        isa_count = 0
        tfsa_count = 0
        emergency_fund_total = Decimal('0')
        savings_goal_total = Decimal('0')

        # Currency service for conversions
        currency_service = CurrencyConversionService(db)

        # Aggregate by currency
        for account in accounts:
            balance = account.current_balance

            # Aggregate by native currency
            if account.currency == Currency.GBP:
                total_gbp += balance
            elif account.currency == Currency.ZAR:
                total_zar += balance
            elif account.currency == Currency.USD:
                total_usd += balance
            elif account.currency == Currency.EUR:
                total_eur += balance

            # Count ISA/TFSA
            if account.is_isa:
                isa_count += 1
            if account.is_tfsa:
                tfsa_count += 1

            # Purpose totals (convert to GBP)
            if account.purpose == AccountPurpose.EMERGENCY_FUND:
                if account.currency == Currency.GBP:
                    emergency_fund_total += balance
                else:
                    converted, _, _ = await currency_service.convert_amount(
                        balance,
                        account.currency.value,
                        "GBP"
                    )
                    emergency_fund_total += converted

            if account.purpose == AccountPurpose.SAVINGS_GOAL:
                if account.currency == Currency.GBP:
                    savings_goal_total += balance
                else:
                    converted, _, _ = await currency_service.convert_amount(
                        balance,
                        account.currency.value,
                        "GBP"
                    )
                    savings_goal_total += converted

        return SavingsTotalSummary(
            total_accounts=total_accounts,
            total_balance_gbp=total_gbp,
            total_balance_zar=total_zar,
            total_balance_usd=total_usd,
            total_balance_eur=total_eur,
            isa_accounts=isa_count,
            tfsa_accounts=tfsa_count,
            emergency_fund_total=emergency_fund_total,
            savings_goal_total=savings_goal_total
        )

    except Exception as e:
        logger.error(f"Failed to generate savings summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate savings summary"
        )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _get_account_or_404(
    account_id: UUID,
    user_id: UUID,
    db: AsyncSession
) -> SavingsAccount:
    """
    Get savings account or raise 404.

    Verifies ownership and excludes soft-deleted accounts.

    Args:
        account_id: Account UUID
        user_id: User UUID
        db: Database session

    Returns:
        SavingsAccount: Account if found and owned by user

    Raises:
        HTTPException: 404 if not found or not owned
    """
    stmt = select(SavingsAccount).where(
        and_(
            SavingsAccount.id == account_id,
            SavingsAccount.user_id == user_id,
            SavingsAccount.deleted_at.is_(None)
        )
    )

    result = await db.execute(stmt)
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Savings account {account_id} not found"
        )

    return account


def _map_account_to_response(account: SavingsAccount) -> SavingsAccountResponse:
    """
    Map SavingsAccount model to response schema.

    Decrypts account number (masked in production).

    Args:
        account: SavingsAccount model instance

    Returns:
        SavingsAccountResponse: Response schema
    """
    # Decrypt account number (consider masking in production)
    try:
        account_number = account.get_account_number()
        # Mask all but last 4 digits
        if len(account_number) > 4:
            account_number = "****" + account_number[-4:]
    except Exception:
        account_number = "****"

    return SavingsAccountResponse(
        id=account.id,
        user_id=account.user_id,
        bank_name=account.bank_name,
        account_name=account.account_name,
        account_number=account_number,
        account_type=account.account_type,
        currency=account.currency,
        current_balance=account.current_balance,
        interest_rate=account.interest_rate,
        interest_payment_frequency=account.interest_payment_frequency,
        is_isa=account.is_isa,
        is_tfsa=account.is_tfsa,
        purpose=account.purpose,
        country=account.country,
        is_active=account.is_active,
        created_at=account.created_at,
        updated_at=account.updated_at,
        deleted_at=account.deleted_at
    )
