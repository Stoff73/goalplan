"""
Portfolio Analysis API Endpoints

Provides comprehensive portfolio analysis including:
- Portfolio summary with aggregated metrics
- Asset allocation (by class, region, sector)
- Performance metrics with unrealized gains
- Capital gains tax calculations (UK and SA)
- Dividend tax calculations

All endpoints require authentication.
Read-only operations (no rate limiting needed).
"""

import logging
from decimal import Decimal
from typing import Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth import get_current_user
from models.investment import InvestmentAccount, InvestmentHolding, DividendIncome, AccountStatus
from schemas.investment import (
    PortfolioSummaryResponse,
    AllocationResponse,
    AllocationItem,
    PerformanceResponse,
    TaxGainsResponse,
    CapitalGainsTaxUK,
    DividendTaxUK,
    CapitalGainsTaxSA,
    DividendTaxSA,
    TopHolding
)
from services.investment.asset_allocation_service import get_asset_allocation_service
from services.investment.investment_tax_service import InvestmentTaxService
from services.isa_tfsa_tracking import get_current_uk_tax_year

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# PORTFOLIO SUMMARY
# ============================================================================

@router.get("/portfolio/summary", response_model=PortfolioSummaryResponse)
async def get_portfolio_summary(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive portfolio summary with aggregated metrics.

    Returns:
    - Total portfolio value and unrealized gains
    - Number of holdings and accounts
    - Currency exposure breakdown
    - Asset allocation breakdown (by asset class)
    - Top 10 holdings by value

    Authentication required.

    Args:
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        PortfolioSummaryResponse: Complete portfolio summary

    Raises:
        401: Unauthorized (not authenticated)
        500: Internal server error
    """
    try:
        logger.info(f"Fetching portfolio summary for user {current_user_id}")

        # Get asset allocation service
        allocation_service = get_asset_allocation_service(db)

        # Get portfolio summary from service
        summary = await allocation_service.get_portfolio_summary(UUID(current_user_id))

        # Convert service dict to response schema
        # Convert nested dicts to AllocationItem models
        currency_exposure = {
            currency: AllocationItem(**data)
            for currency, data in summary['currency_exposure'].items()
        }

        asset_allocation = {
            asset_class: AllocationItem(**data)
            for asset_class, data in summary['asset_allocation'].items()
        }

        top_holdings = [
            TopHolding(**holding)
            for holding in summary['top_holdings']
        ]

        response = PortfolioSummaryResponse(
            total_value=summary['total_value'],
            total_cost_basis=summary['total_cost_basis'],
            total_unrealized_gain=summary['total_unrealized_gain'],
            unrealized_gain_percentage=summary['unrealized_gain_percentage'],
            num_holdings=summary['num_holdings'],
            num_accounts=summary['num_accounts'],
            currency_exposure=currency_exposure,
            asset_allocation=asset_allocation,
            top_holdings=top_holdings
        )

        logger.info(
            f"Portfolio summary retrieved for user {current_user_id}: "
            f"total_value={summary['total_value']}, "
            f"num_holdings={summary['num_holdings']}"
        )

        return response

    except Exception as e:
        logger.error(f"Failed to retrieve portfolio summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve portfolio summary"
        )


# ============================================================================
# ASSET ALLOCATION
# ============================================================================

@router.get("/portfolio/allocation", response_model=AllocationResponse)
async def get_portfolio_allocation(
    by: str = Query(
        "asset_class",
        description="Allocation type: 'asset_class', 'region', or 'sector'"
    ),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get portfolio allocation breakdown.

    Supports allocation by:
    - asset_class (default): EQUITY, FIXED_INCOME, PROPERTY, COMMODITY, CASH, ALTERNATIVE
    - region: UK, US, EUROPE, ASIA_PACIFIC, EMERGING_MARKETS, GLOBAL
    - sector: TECHNOLOGY, HEALTHCARE, FINANCIALS, etc.

    Returns value and percentage for each category.

    Authentication required.

    Args:
        by: Allocation type ('asset_class', 'region', or 'sector')
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        AllocationResponse: Allocation breakdown with values and percentages

    Raises:
        400: Invalid allocation type
        401: Unauthorized (not authenticated)
        500: Internal server error
    """
    try:
        logger.info(f"Fetching allocation by '{by}' for user {current_user_id}")

        # Validate allocation type
        valid_types = ['asset_class', 'region', 'sector']
        if by not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid allocation type '{by}'. Must be one of: {', '.join(valid_types)}"
            )

        # Get asset allocation service
        allocation_service = get_asset_allocation_service(db)

        # Get allocation based on type
        if by == 'asset_class':
            allocation_dict = await allocation_service.calculate_allocation_by_asset_class(
                UUID(current_user_id)
            )
        elif by == 'region':
            allocation_dict = await allocation_service.calculate_allocation_by_region(
                UUID(current_user_id)
            )
        elif by == 'sector':
            allocation_dict = await allocation_service.calculate_allocation_by_sector(
                UUID(current_user_id)
            )

        # Convert to AllocationItem models
        allocation = {
            category: AllocationItem(**data)
            for category, data in allocation_dict.items()
        }

        logger.info(
            f"Allocation by '{by}' retrieved for user {current_user_id}: "
            f"{len(allocation)} categories"
        )

        return AllocationResponse(allocation=allocation)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve allocation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve allocation"
        )


# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

@router.get("/portfolio/performance", response_model=PerformanceResponse)
async def get_portfolio_performance(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get portfolio performance metrics.

    Returns:
    - Total portfolio value
    - Total cost basis (sum of purchase prices)
    - Total unrealized gains/losses
    - Unrealized gain percentage
    - Year-to-date dividend income (current UK tax year)
    - Total dividend income (all time)

    Authentication required.

    Args:
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        PerformanceResponse: Performance metrics

    Raises:
        401: Unauthorized (not authenticated)
        500: Internal server error
    """
    try:
        logger.info(f"Fetching performance metrics for user {current_user_id}")

        # Get all active holdings
        holdings_result = await db.execute(
            select(InvestmentHolding)
            .join(InvestmentAccount)
            .where(
                and_(
                    InvestmentAccount.user_id == UUID(current_user_id),
                    InvestmentAccount.status == AccountStatus.ACTIVE,
                    InvestmentAccount.deleted == False,
                    InvestmentHolding.deleted == False
                )
            )
        )
        holdings = holdings_result.scalars().all()

        # Calculate portfolio metrics
        total_value = Decimal('0.00')
        total_cost_basis = Decimal('0.00')
        total_unrealized_gain = Decimal('0.00')

        for holding in holdings:
            total_value += holding.current_value
            total_cost_basis += (holding.purchase_price * holding.quantity)
            total_unrealized_gain += holding.unrealized_gain

        # Calculate unrealized gain percentage
        if total_cost_basis > 0:
            unrealized_gain_percentage = (
                total_unrealized_gain / total_cost_basis * 100
            ).quantize(Decimal('0.01'))
        else:
            unrealized_gain_percentage = Decimal('0.00')

        # Get current UK tax year for YTD dividends
        current_tax_year = get_current_uk_tax_year()

        # Get YTD dividend income
        ytd_dividends_result = await db.execute(
            select(func.coalesce(func.sum(DividendIncome.total_dividend_gross), 0))
            .join(InvestmentHolding)
            .join(InvestmentAccount)
            .where(
                and_(
                    InvestmentAccount.user_id == UUID(current_user_id),
                    InvestmentAccount.deleted == False,
                    InvestmentHolding.deleted == False,
                    DividendIncome.uk_tax_year == current_tax_year
                )
            )
        )
        ytd_dividend_income = Decimal(str(ytd_dividends_result.scalar() or 0))

        # Get total dividend income (all time)
        total_dividends_result = await db.execute(
            select(func.coalesce(func.sum(DividendIncome.total_dividend_gross), 0))
            .join(InvestmentHolding)
            .join(InvestmentAccount)
            .where(
                and_(
                    InvestmentAccount.user_id == UUID(current_user_id),
                    InvestmentAccount.deleted == False,
                    InvestmentHolding.deleted == False
                )
            )
        )
        total_dividend_income = Decimal(str(total_dividends_result.scalar() or 0))

        response = PerformanceResponse(
            total_value=total_value,
            total_cost_basis=total_cost_basis,
            total_unrealized_gain=total_unrealized_gain,
            unrealized_gain_percentage=unrealized_gain_percentage,
            ytd_dividend_income=ytd_dividend_income,
            total_dividend_income=total_dividend_income
        )

        logger.info(
            f"Performance metrics retrieved for user {current_user_id}: "
            f"total_value={total_value}, unrealized_gain={total_unrealized_gain}"
        )

        return response

    except Exception as e:
        logger.error(f"Failed to retrieve performance metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance metrics"
        )


# ============================================================================
# TAX CALCULATIONS
# ============================================================================

@router.get("/tax/capital-gains", response_model=TaxGainsResponse)
async def get_capital_gains_tax(
    tax_year: str = Query(
        None,
        description="Tax year (e.g., '2024/25'). Defaults to current tax year."
    ),
    country: str = Query(
        "UK",
        description="Country for tax calculation: 'UK' or 'SA'"
    ),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate capital gains and dividend tax for a tax year.

    Calculates both:
    - Capital gains tax (CGT)
    - Dividend tax

    For UK:
    - CGT: Annual exemption £3,000, then 10% (basic) or 20% (higher rate)
    - Dividends: Allowance £500, then 8.75%/33.75%/39.35% depending on tax band
    - ISA holdings are tax-free

    For SA:
    - CGT: 40% inclusion rate, then marginal income tax rate (up to 45%)
    - Dividends: 20% withholding tax

    Authentication required.

    Args:
        tax_year: Tax year (defaults to current UK tax year)
        country: Country for tax calculation ('UK' or 'SA')
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        TaxGainsResponse: Tax calculations for capital gains and dividends

    Raises:
        400: Invalid country
        401: Unauthorized (not authenticated)
        500: Internal server error
    """
    try:
        logger.info(
            f"Calculating capital gains tax for user {current_user_id}, "
            f"tax_year={tax_year}, country={country}"
        )

        # Validate country
        if country not in ['UK', 'SA']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Country must be 'UK' or 'SA'"
            )

        # Default to current UK tax year if not specified
        if tax_year is None:
            tax_year = get_current_uk_tax_year()

        # Get investment tax service
        tax_service = InvestmentTaxService(db)

        # Calculate taxes based on country
        if country == 'UK':
            # Calculate UK CGT
            cgt_data = await tax_service.calculate_cgt_uk(
                user_id=current_user_id,
                tax_year=tax_year
            )

            # Calculate UK dividend tax
            dividend_data = await tax_service.calculate_dividend_tax_uk(
                user_id=current_user_id,
                tax_year=tax_year
            )

            capital_gains = CapitalGainsTaxUK(**cgt_data)
            dividend_tax = DividendTaxUK(**dividend_data)

        else:  # SA
            # Calculate SA CGT
            cgt_data = await tax_service.calculate_cgt_sa(
                user_id=current_user_id,
                tax_year=tax_year
            )

            # Calculate SA dividend tax
            dividend_data = await tax_service.calculate_dividend_tax_sa(
                user_id=current_user_id,
                tax_year=tax_year
            )

            capital_gains = CapitalGainsTaxSA(**cgt_data)
            dividend_tax = DividendTaxSA(**dividend_data)

        response = TaxGainsResponse(
            capital_gains=capital_gains,
            dividend_tax=dividend_tax
        )

        logger.info(
            f"Tax calculations completed for user {current_user_id}: "
            f"country={country}, tax_year={tax_year}"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate capital gains tax: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate capital gains tax"
        )
