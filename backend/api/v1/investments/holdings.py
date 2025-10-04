"""
Investment holdings API endpoints.

This module provides operations for investment holdings:
- Add holding to account
- Retrieve holdings with filtering
- Get single holding details
- Update holding price
- Sell holding (FIFO method for CGT)
- Record dividend payments

Business logic:
- Tax lot tracking for FIFO CGT calculations
- Rate limiting on mutation endpoints
- Multi-currency support
- Ownership validation
- Realized gain calculation
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
import logging

from database import get_db
from middleware.auth import get_current_user
from middleware.rate_limiter import limiter
from models.investment import (
    InvestmentAccount,
    InvestmentHolding,
    SecurityType,
    AssetClass,
    Region
)
from schemas.investment import (
    CreateHoldingRequest,
    HoldingResponse,
    UpdatePriceRequest,
    SellHoldingRequest,
    SellHoldingResponse,
    RecordDividendRequest,
    DividendResponse
)
from services.investment.portfolio_service import get_portfolio_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# HOLDINGS CRUD
# ============================================================================

@router.post("/holdings", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def add_holding(
    request: Request,
    response: Response,
    data: CreateHoldingRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a new holding to an investment account.

    Creates holding and initial tax lot for CGT tracking.
    Rate limited to 10 requests per minute.

    Business logic:
    1. Verify account ownership
    2. Validate quantity > 0, price >= 0
    3. Create holding and tax lot
    4. Return holding details

    Args:
        data: Holding creation data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        HoldingResponse: Created holding with current values

    Raises:
        400: Validation error
        403: Account not owned by user
        404: Account not found
        429: Rate limit exceeded
        500: Internal server error
    """
    try:
        # Verify account ownership
        await _verify_account_ownership(data.account_id, UUID(current_user_id), db)

        # Get portfolio service
        portfolio_service = get_portfolio_service(db)

        # Add holding
        holding = await portfolio_service.add_holding(
            account_id=data.account_id,
            security_type=data.security_type,
            ticker=data.ticker,
            name=data.name,
            quantity=data.quantity,
            purchase_price=data.purchase_price,
            purchase_date=data.purchase_date,
            purchase_currency=data.purchase_currency,
            asset_class=data.asset_class,
            region=data.region,
            sector=data.sector,
            isin=data.isin
        )

        logger.info(
            f"Added holding {holding.id} to account {data.account_id}: "
            f"{data.ticker} x {data.quantity}"
        )

        return _map_holding_to_response(holding)

    except ValueError as e:
        logger.error(f"Validation error adding holding: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add holding: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add holding: {str(e)}"
        )


@router.get("/holdings", response_model=List[HoldingResponse])
async def get_all_holdings(
    current_user_id: str = Depends(get_current_user),
    account_id: Optional[UUID] = Query(None, description="Filter by account ID"),
    ticker: Optional[str] = Query(None, description="Filter by ticker symbol"),
    asset_class: Optional[AssetClass] = Query(None, description="Filter by asset class"),
    region: Optional[Region] = Query(None, description="Filter by region"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all holdings for the authenticated user.

    Supports filtering by:
    - account_id: Specific investment account
    - ticker: Ticker symbol
    - asset_class: EQUITY, FIXED_INCOME, etc.
    - region: UK, US, EUROPE, etc.
    - sector: Sector name
    - Pagination with skip and limit

    Results sorted by current value (descending).

    Args:
        current_user_id: Authenticated user ID
        account_id: Optional account filter
        ticker: Optional ticker filter
        asset_class: Optional asset class filter
        region: Optional region filter
        sector: Optional sector filter
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List[HoldingResponse]: List of holdings with current values
    """
    try:
        # Get user's accounts
        accounts_stmt = select(InvestmentAccount.id).where(
            and_(
                InvestmentAccount.user_id == UUID(current_user_id),
                InvestmentAccount.deleted == False
            )
        )
        accounts_result = await db.execute(accounts_stmt)
        user_account_ids = [row[0] for row in accounts_result.all()]

        if not user_account_ids:
            return []

        # Build query with filters
        conditions = [
            InvestmentHolding.account_id.in_(user_account_ids),
            InvestmentHolding.deleted == False
        ]

        if account_id is not None:
            # Verify ownership of specified account
            if account_id not in user_account_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this account"
                )
            conditions.append(InvestmentHolding.account_id == account_id)

        if ticker is not None:
            conditions.append(InvestmentHolding.ticker.ilike(f"%{ticker}%"))

        if asset_class is not None:
            conditions.append(InvestmentHolding.asset_class == asset_class)

        if region is not None:
            conditions.append(InvestmentHolding.region == region)

        if sector is not None:
            conditions.append(InvestmentHolding.sector.ilike(f"%{sector}%"))

        stmt = (
            select(InvestmentHolding)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)
        holdings = result.scalars().all()

        # Sort by current value (descending) in Python since it's a computed property
        holdings_sorted = sorted(
            holdings,
            key=lambda h: h.current_value,
            reverse=True
        )

        return [_map_holding_to_response(h) for h in holdings_sorted]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve holdings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve holdings"
        )


@router.get("/holdings/{holding_id}", response_model=HoldingResponse)
async def get_holding(
    holding_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single holding by ID.

    Verifies ownership before returning holding details.

    Args:
        holding_id: Holding UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        HoldingResponse: Holding details including tax lots

    Raises:
        404: Holding not found or not owned by user
    """
    holding = await _get_holding_or_404(holding_id, UUID(current_user_id), db)
    return _map_holding_to_response(holding)


# ============================================================================
# PRICE UPDATES
# ============================================================================

@router.put("/holdings/{holding_id}/price", response_model=HoldingResponse)
async def update_holding_price(
    holding_id: UUID,
    data: UpdatePriceRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the current price of a holding.

    Recalculates unrealized gains based on new price.

    Args:
        holding_id: Holding UUID
        data: Price update data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        HoldingResponse: Updated holding with recalculated gains

    Raises:
        400: Invalid price (negative)
        404: Holding not found or not owned by user
        500: Internal server error
    """
    try:
        # Verify ownership
        await _get_holding_or_404(holding_id, UUID(current_user_id), db)

        # Get portfolio service
        portfolio_service = get_portfolio_service(db)

        # Update price
        holding = await portfolio_service.update_holding_price(
            holding_id=holding_id,
            new_current_price=data.current_price
        )

        logger.info(
            f"Updated price for holding {holding_id}: {data.current_price}, "
            f"unrealized_gain={holding.unrealized_gain}"
        )

        return _map_holding_to_response(holding)

    except ValueError as e:
        logger.error(f"Validation error updating price: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update holding price: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update holding price"
        )


# ============================================================================
# SELLING HOLDINGS
# ============================================================================

@router.post("/holdings/{holding_id}/sell", response_model=SellHoldingResponse)
@limiter.limit("10/minute")
async def sell_holding(
    request: Request,
    response: Response,
    holding_id: UUID,
    data: SellHoldingRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sell a holding (partial or full) using FIFO method for CGT.

    Creates capital gain record and updates tax lots.
    Rate limited to 10 requests per minute.

    Business logic:
    1. Verify ownership
    2. Validate quantity <= owned
    3. Calculate realized gain using FIFO
    4. Update tax lots
    5. Reduce holding quantity or soft delete if fully sold

    Args:
        holding_id: Holding UUID
        data: Sale details (quantity, price, date)
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        SellHoldingResponse: Sale details with realized gain and tax year

    Raises:
        400: Validation error (quantity exceeds available, etc.)
        404: Holding not found or not owned by user
        429: Rate limit exceeded
        500: Internal server error
    """
    try:
        # Verify ownership
        await _get_holding_or_404(holding_id, UUID(current_user_id), db)

        # Get portfolio service
        portfolio_service = get_portfolio_service(db)

        # Sell holding
        sale_details = await portfolio_service.sell_holding(
            holding_id=holding_id,
            quantity_to_sell=data.quantity,
            sale_price=data.sale_price,
            sale_date=data.sale_date
        )

        logger.info(
            f"Sold holding {holding_id}: quantity={data.quantity}, "
            f"realized_gain={sale_details['realized_gain']}"
        )

        return SellHoldingResponse(**sale_details)

    except ValueError as e:
        logger.error(f"Validation error selling holding: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sell holding: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sell holding"
        )


# ============================================================================
# DIVIDEND RECORDING
# ============================================================================

@router.post("/dividends", response_model=DividendResponse, status_code=status.HTTP_201_CREATED)
async def record_dividend(
    data: RecordDividendRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Record a dividend payment.

    Tracks dividend income by source country for tax purposes.

    Business logic:
    1. Verify holding ownership
    2. Validate amounts (tax withheld <= dividend)
    3. Calculate net dividend
    4. Determine UK and SA tax years
    5. Create dividend record

    Args:
        data: Dividend details
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        DividendResponse: Dividend record with tax year assignments

    Raises:
        400: Validation error
        404: Holding not found or not owned by user
        500: Internal server error
    """
    try:
        # Verify holding ownership
        await _get_holding_or_404(data.holding_id, UUID(current_user_id), db)

        # Get portfolio service
        portfolio_service = get_portfolio_service(db)

        # Record dividend
        dividend = await portfolio_service.record_dividend(
            holding_id=data.holding_id,
            payment_date=data.payment_date,
            amount=data.amount,
            currency=data.currency,
            tax_withheld=data.tax_withheld,
            country_of_source=data.country_of_source,
            ex_dividend_date=data.ex_dividend_date
        )

        logger.info(
            f"Recorded dividend for holding {data.holding_id}: "
            f"amount={data.amount}, net={dividend.total_dividend_net}"
        )

        return DividendResponse(
            id=dividend.id,
            holding_id=dividend.holding_id,
            payment_date=dividend.payment_date,
            ex_dividend_date=dividend.ex_dividend_date,
            dividend_per_share=dividend.dividend_per_share,
            total_dividend_gross=dividend.total_dividend_gross,
            withholding_tax=dividend.withholding_tax,
            total_dividend_net=dividend.total_dividend_net,
            currency=dividend.currency,
            source_country=dividend.source_country,
            uk_tax_year=dividend.uk_tax_year,
            sa_tax_year=dividend.sa_tax_year,
            created_at=dividend.created_at
        )

    except ValueError as e:
        logger.error(f"Validation error recording dividend: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record dividend: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record dividend"
        )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _verify_account_ownership(
    account_id: UUID,
    user_id: UUID,
    db: AsyncSession
) -> None:
    """
    Verify that user owns the specified account.

    Args:
        account_id: Account UUID
        user_id: User UUID
        db: Database session

    Raises:
        HTTPException: 404 if account not found, 403 if not owned
    """
    stmt = select(InvestmentAccount).where(
        and_(
            InvestmentAccount.id == account_id,
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

    if account.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this account"
        )


async def _get_holding_or_404(
    holding_id: UUID,
    user_id: UUID,
    db: AsyncSession
) -> InvestmentHolding:
    """
    Get holding or raise 404.

    Verifies ownership via account relationship and excludes soft-deleted holdings.

    Args:
        holding_id: Holding UUID
        user_id: User UUID
        db: Database session

    Returns:
        InvestmentHolding: Holding if found and owned by user

    Raises:
        HTTPException: 404 if not found or not owned
    """
    # Get holding with account relationship
    stmt = (
        select(InvestmentHolding)
        .join(InvestmentAccount)
        .where(
            and_(
                InvestmentHolding.id == holding_id,
                InvestmentHolding.deleted == False,
                InvestmentAccount.user_id == user_id,
                InvestmentAccount.deleted == False
            )
        )
    )

    result = await db.execute(stmt)
    holding = result.scalar_one_or_none()

    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holding {holding_id} not found"
        )

    return holding


def _map_holding_to_response(holding: InvestmentHolding) -> HoldingResponse:
    """
    Map InvestmentHolding model to response schema.

    Includes computed properties for current value and gains.

    Args:
        holding: InvestmentHolding model instance

    Returns:
        HoldingResponse: Response schema
    """
    return HoldingResponse(
        id=holding.id,
        account_id=holding.account_id,
        security_type=holding.security_type,
        ticker=holding.ticker,
        isin=holding.isin,
        security_name=holding.security_name,
        quantity=holding.quantity,
        purchase_date=holding.purchase_date,
        purchase_price=holding.purchase_price,
        purchase_currency=holding.purchase_currency,
        current_price=holding.current_price,
        current_value=holding.current_value,
        unrealized_gain=holding.unrealized_gain,
        unrealized_gain_percentage=holding.unrealized_gain_percentage,
        asset_class=holding.asset_class,
        region=holding.region,
        sector=holding.sector,
        last_price_update=holding.last_price_update,
        deleted=holding.deleted,
        created_at=holding.created_at,
        updated_at=holding.updated_at
    )
