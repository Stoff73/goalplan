"""
Net Worth Dashboard API endpoint.

This module provides the main dashboard endpoint for net worth summary
including breakdowns by country, asset class, and currency, plus trend
data and change calculations.

Performance target: <500ms (leverages caching via DashboardAggregationService)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from datetime import date, datetime
import logging

from database import get_db
from middleware.auth import get_current_user
from services.dashboard_aggregation import DashboardAggregationService
from services.net_worth_snapshot import NetWorthSnapshotService
from schemas.dashboard import (
    NetWorthSummaryResponse,
    CountryBreakdownItem,
    AssetClassBreakdownItem,
    CurrencyBreakdownItem,
    TrendDataPoint,
    Changes,
    Change
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/net-worth", response_model=NetWorthSummaryResponse)
async def get_net_worth_summary(
    baseCurrency: str = Query("GBP", description="Base currency for all amounts (GBP, ZAR, USD, EUR)"),
    asOfDate: Optional[date] = Query(None, description="Calculate as of specific date (default: today)"),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive net worth summary.

    This endpoint returns complete dashboard data including:
    - Total net worth (assets - liabilities)
    - Breakdown by country (UK, SA, Other)
    - Breakdown by asset class (Cash, Investments, Property, Pensions, etc.)
    - Breakdown by currency (original currency exposure)
    - Historical trend data (last 12 months)
    - Changes over day, month, and year

    Performance:
    - Target: <500ms (95th percentile)
    - Uses Redis caching (5-minute TTL)
    - Async database queries

    Query Parameters:
        baseCurrency (str): Currency for all amounts (default: GBP)
        asOfDate (date): Optional date for historical calculation (default: today)

    Returns:
        NetWorthSummaryResponse: Complete dashboard data

    Raises:
        400: Invalid currency or date
        401: Unauthorized (no valid token)
        500: Internal server error
    """
    try:
        # Validate base currency
        valid_currencies = ["GBP", "ZAR", "USD", "EUR"]
        if baseCurrency.upper() not in valid_currencies:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid currency. Supported: {', '.join(valid_currencies)}"
            )

        baseCurrency = baseCurrency.upper()
        user_id = UUID(current_user_id)

        logger.info(
            f"Getting net worth summary for user {user_id} "
            f"in {baseCurrency}, asOfDate={asOfDate}"
        )

        # Initialize services
        aggregation_service = DashboardAggregationService(db)
        snapshot_service = NetWorthSnapshotService(db)

        # Get current net worth summary (uses caching)
        summary = await aggregation_service.get_net_worth_summary(
            user_id=user_id,
            base_currency=baseCurrency,
            as_of_date=asOfDate,
            use_cache=True
        )

        # Get trend data (last 12 months)
        trend_data = await snapshot_service.get_trend_data(
            user_id=user_id,
            base_currency=baseCurrency,
            months=12
        )

        # Calculate changes (day, month, year)
        changes_data = await snapshot_service.calculate_changes(
            user_id=user_id,
            base_currency=baseCurrency
        )

        # Build response
        response = NetWorthSummaryResponse(
            netWorth=summary['net_worth'],
            totalAssets=summary['total_assets'],
            totalLiabilities=summary['total_liabilities'],
            baseCurrency=summary['base_currency'],
            asOfDate=summary['as_of_date'],
            lastUpdated=summary['last_updated'],
            breakdownByCountry=_map_country_breakdown(summary['breakdown_by_country']),
            breakdownByAssetClass=_map_asset_class_breakdown(summary['breakdown_by_asset_class']),
            breakdownByCurrency=_map_currency_breakdown(summary['breakdown_by_currency']),
            trendData=_map_trend_data(trend_data),
            changes=_map_changes(changes_data)
        )

        logger.info(
            f"Successfully retrieved net worth summary for user {user_id}: "
            f"net_worth={response.netWorth} {baseCurrency}"
        )

        return response

    except HTTPException:
        raise

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"Failed to get net worth summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve net worth summary"
        )


# Helper functions for mapping data to response schemas

def _map_country_breakdown(breakdown: list) -> list[CountryBreakdownItem]:
    """Map country breakdown to response schema."""
    if not breakdown:
        return []

    return [
        CountryBreakdownItem(
            country=item.get('category', 'Unknown'),
            amount=item['net'],
            percentage=item['percentage']
        )
        for item in breakdown
    ]


def _map_asset_class_breakdown(breakdown: list) -> list[AssetClassBreakdownItem]:
    """Map asset class breakdown to response schema."""
    if not breakdown:
        return []

    return [
        AssetClassBreakdownItem(
            assetClass=item.get('category', 'Unknown'),
            amount=item['net'],
            percentage=item['percentage']
        )
        for item in breakdown
    ]


def _map_currency_breakdown(breakdown: list) -> list[CurrencyBreakdownItem]:
    """Map currency breakdown to response schema."""
    if not breakdown:
        return []

    return [
        CurrencyBreakdownItem(
            currency=item['currency'],
            amount=item['amount'],
            percentage=item['percentage']
        )
        for item in breakdown
    ]


def _map_trend_data(trend_data: list) -> list[TrendDataPoint]:
    """Map trend data to response schema."""
    if not trend_data:
        return []

    return [
        TrendDataPoint(
            date=point['date'],
            netWorth=point['net_worth']
        )
        for point in trend_data
    ]


def _map_changes(changes_data: dict) -> Optional[Changes]:
    """Map changes data to response schema."""
    if not changes_data:
        return None

    return Changes(
        day=Change(
            amount=changes_data['day']['amount'],
            percentage=changes_data['day']['percentage']
        ),
        month=Change(
            amount=changes_data['month']['amount'],
            percentage=changes_data['month']['percentage']
        ),
        year=Change(
            amount=changes_data['year']['amount'],
            percentage=changes_data['year']['percentage']
        )
    )
