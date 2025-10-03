"""
Dashboard Data Aggregation Service

Aggregates financial data from all modules to calculate net worth
and provide breakdowns by country, asset class, and currency.

This service is designed to be extensible for future modules (savings, investments,
pensions, property, etc.) but currently works with available data in Phase 1.

Performance:
- Target: <500ms for complete aggregation
- Redis caching with 5-minute TTL
- Async database queries
- Optimized for up to 1000 line items per user

Architecture:
- Modular design: Each asset/liability type has its own aggregation method
- Easy to add new modules as they're implemented
- Graceful degradation if module data unavailable
"""

import json
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from redis_client import redis_client
from services.currency_conversion import CurrencyConversionService
from models.income import UserIncome

logger = logging.getLogger(__name__)


class DashboardAggregationService:
    """Service for aggregating user financial data across all modules."""

    CACHE_TTL = 300  # 5 minutes
    SUPPORTED_BASE_CURRENCIES = ["GBP", "ZAR", "USD", "EUR"]

    def __init__(self, db: AsyncSession):
        """
        Initialize dashboard aggregation service.

        Args:
            db: Database session for queries
        """
        self.db = db
        self.currency_service = CurrencyConversionService(db)

    async def get_net_worth_summary(
        self,
        user_id: UUID,
        base_currency: str = "GBP",
        as_of_date: Optional[date] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive net worth summary.

        Args:
            user_id: User UUID
            base_currency: Currency for all amounts (GBP, ZAR, USD, EUR)
            as_of_date: Calculate as of specific date (default: today)
            use_cache: Use cached data if available

        Returns:
            Dict with structure:
            {
                "total_assets": Decimal,
                "total_liabilities": Decimal,
                "net_worth": Decimal,
                "base_currency": str,
                "as_of_date": date,
                "breakdown_by_country": {...},
                "breakdown_by_asset_class": {...},
                "breakdown_by_currency": {...},
                "last_updated": datetime
            }

        Raises:
            ValueError: If base_currency not supported
        """
        # Validate base currency
        if base_currency not in self.SUPPORTED_BASE_CURRENCIES:
            raise ValueError(
                f"Currency {base_currency} not supported. "
                f"Supported: {', '.join(self.SUPPORTED_BASE_CURRENCIES)}"
            )

        # Default to today
        as_of_date = as_of_date or date.today()

        # Check cache first
        if use_cache:
            cached = await self._get_from_cache(user_id, base_currency)
            if cached:
                logger.info(f"Returning cached net worth summary for user {user_id}")
                return cached

        # Aggregate data
        logger.info(f"Aggregating net worth data for user {user_id} in {base_currency}")
        summary = await self._aggregate_data(user_id, base_currency, as_of_date)

        # Cache result
        await self._save_to_cache(user_id, base_currency, summary)

        return summary

    async def _aggregate_data(
        self,
        user_id: UUID,
        base_currency: str,
        as_of_date: date
    ) -> Dict[str, Any]:
        """
        Aggregate all financial data for the user.

        This method orchestrates data collection from all modules and
        performs currency conversion and grouping.

        Args:
            user_id: User UUID
            base_currency: Target currency for conversion
            as_of_date: Date for calculations

        Returns:
            Complete net worth summary dictionary
        """
        # Initialize tracking structures
        assets_by_country: Dict[str, Decimal] = {}
        assets_by_class: Dict[str, Decimal] = {}
        assets_by_currency: Dict[str, Decimal] = {}
        liabilities_by_country: Dict[str, Decimal] = {}
        liabilities_by_class: Dict[str, Decimal] = {}

        total_assets = Decimal('0.00')
        total_liabilities = Decimal('0.00')

        # Aggregate assets from each module
        # Note: In Phase 1, we don't have savings accounts yet
        # This structure is ready for future modules

        # Future: Aggregate savings accounts
        # savings_data = await self._aggregate_savings(user_id, base_currency, as_of_date)
        # total_assets += savings_data['total']
        # ... update breakdown dicts

        # Future: Aggregate investments
        # investment_data = await self._aggregate_investments(user_id, base_currency, as_of_date)
        # total_assets += investment_data['total']
        # ... update breakdown dicts

        # Future: Aggregate pensions
        # pension_data = await self._aggregate_pensions(user_id, base_currency, as_of_date)
        # total_assets += pension_data['total']
        # ... update breakdown dicts

        # Future: Aggregate property
        # property_data = await self._aggregate_property(user_id, base_currency, as_of_date)
        # total_assets += property_data['total']
        # ... update breakdown dicts

        # Future: Aggregate liabilities (mortgages, loans, etc.)
        # liability_data = await self._aggregate_liabilities(user_id, base_currency, as_of_date)
        # total_liabilities += liability_data['total']
        # ... update breakdown dicts

        # Calculate net worth
        net_worth = total_assets - total_liabilities

        # Build breakdown structures
        breakdown_by_country = self._build_breakdown(
            assets_by_country,
            liabilities_by_country,
            total_assets,
            total_liabilities
        )

        breakdown_by_asset_class = self._build_asset_class_breakdown(
            assets_by_class,
            liabilities_by_class,
            total_assets,
            total_liabilities
        )

        breakdown_by_currency = self._build_currency_breakdown(
            assets_by_currency,
            total_assets
        )

        # Build final summary
        summary = {
            "total_assets": float(total_assets),
            "total_liabilities": float(total_liabilities),
            "net_worth": float(net_worth),
            "base_currency": base_currency,
            "as_of_date": as_of_date.isoformat(),
            "breakdown_by_country": breakdown_by_country,
            "breakdown_by_asset_class": breakdown_by_asset_class,
            "breakdown_by_currency": breakdown_by_currency,
            "last_updated": datetime.utcnow().isoformat()
        }

        return summary

    async def _aggregate_savings(
        self,
        user_id: UUID,
        base_currency: str,
        as_of_date: date
    ) -> Dict[str, Any]:
        """
        Aggregate savings accounts data.

        This method will be implemented when savings accounts are added.
        Currently returns empty data.

        Args:
            user_id: User UUID
            base_currency: Target currency
            as_of_date: Date for calculations

        Returns:
            Dict with total, by_country, by_currency breakdowns
        """
        # TODO: Implement when savings accounts model is added
        # Query savings accounts for user
        # Convert balances to base currency
        # Group by country and currency

        return {
            'total': Decimal('0.00'),
            'by_country': {},
            'by_currency': {},
            'accounts': []
        }

    def _build_breakdown(
        self,
        assets_by_category: Dict[str, Decimal],
        liabilities_by_category: Dict[str, Decimal],
        total_assets: Decimal,
        total_liabilities: Decimal
    ) -> List[Dict[str, Any]]:
        """
        Build breakdown structure with percentages.

        Args:
            assets_by_category: Assets grouped by category
            liabilities_by_category: Liabilities grouped by category
            total_assets: Total assets amount
            total_liabilities: Total liabilities amount

        Returns:
            List of breakdown items with amounts and percentages
        """
        breakdown = []

        # Get all categories
        all_categories = set(list(assets_by_category.keys()) + list(liabilities_by_category.keys()))

        for category in all_categories:
            assets = assets_by_category.get(category, Decimal('0.00'))
            liabilities = liabilities_by_category.get(category, Decimal('0.00'))
            net = assets - liabilities

            # Calculate percentage of total net worth
            total_net = total_assets - total_liabilities
            if total_net != 0:
                percentage = float((net / total_net) * 100)
            else:
                percentage = 0.0

            breakdown.append({
                'category': category,
                'assets': float(assets),
                'liabilities': float(liabilities),
                'net': float(net),
                'percentage': round(percentage, 2)
            })

        # Sort by net amount descending
        breakdown.sort(key=lambda x: x['net'], reverse=True)

        return breakdown

    def _build_asset_class_breakdown(
        self,
        assets_by_class: Dict[str, Decimal],
        liabilities_by_class: Dict[str, Decimal],
        total_assets: Decimal,
        total_liabilities: Decimal
    ) -> List[Dict[str, Any]]:
        """
        Build asset class breakdown.

        Asset classes: Cash, Investments, Property, Pensions, Protection, Other

        Args:
            assets_by_class: Assets grouped by class
            liabilities_by_class: Liabilities grouped by class
            total_assets: Total assets amount
            total_liabilities: Total liabilities amount

        Returns:
            List of asset class breakdown items
        """
        return self._build_breakdown(
            assets_by_class,
            liabilities_by_class,
            total_assets,
            total_liabilities
        )

    def _build_currency_breakdown(
        self,
        amounts_by_currency: Dict[str, Decimal],
        total_amount: Decimal
    ) -> List[Dict[str, Any]]:
        """
        Build currency exposure breakdown.

        Shows original currency amounts before conversion.

        Args:
            amounts_by_currency: Amounts grouped by original currency
            total_amount: Total amount in base currency

        Returns:
            List of currency breakdown items
        """
        breakdown = []

        for currency, amount in amounts_by_currency.items():
            # Calculate percentage of total
            if total_amount != 0:
                percentage = float((amount / total_amount) * 100)
            else:
                percentage = 0.0

            breakdown.append({
                'currency': currency,
                'amount': float(amount),
                'percentage': round(percentage, 2)
            })

        # Sort by amount descending
        breakdown.sort(key=lambda x: x['amount'], reverse=True)

        return breakdown

    async def _get_from_cache(
        self,
        user_id: UUID,
        base_currency: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached net worth summary.

        Args:
            user_id: User UUID
            base_currency: Base currency for cached data

        Returns:
            Cached summary dict or None
        """
        cache_key = f"dashboard:net_worth:{user_id}:{base_currency}"

        try:
            cached_data = await redis_client.get(cache_key)

            if cached_data:
                # Parse JSON data
                data = json.loads(cached_data)
                logger.debug(f"Cache hit for {cache_key}")
                return data

            logger.debug(f"Cache miss for {cache_key}")
            return None

        except Exception as e:
            logger.error(f"Redis cache read error: {e}")
            return None

    async def _save_to_cache(
        self,
        user_id: UUID,
        base_currency: str,
        data: Dict[str, Any]
    ) -> None:
        """
        Save net worth summary to cache.

        Args:
            user_id: User UUID
            base_currency: Base currency for data
            data: Summary data to cache
        """
        cache_key = f"dashboard:net_worth:{user_id}:{base_currency}"

        try:
            # Serialize to JSON
            json_data = json.dumps(data, default=str)

            # Save to Redis with TTL
            await redis_client.setex(
                cache_key,
                self.CACHE_TTL,
                json_data
            )

            logger.debug(f"Cached data for {cache_key} (TTL: {self.CACHE_TTL}s)")

        except Exception as e:
            logger.error(f"Redis cache write error: {e}")
            # Don't raise - caching failure shouldn't break aggregation

    async def invalidate_cache(self, user_id: UUID) -> None:
        """
        Invalidate all cached dashboard data for user.

        Call this when user updates any financial data.

        Args:
            user_id: User UUID
        """
        try:
            # Clear cache for all supported currencies
            for currency in self.SUPPORTED_BASE_CURRENCIES:
                cache_key = f"dashboard:net_worth:{user_id}:{currency}"
                await redis_client.delete(cache_key)

            logger.info(f"Invalidated dashboard cache for user {user_id}")

        except Exception as e:
            logger.error(f"Redis cache invalidation error: {e}")
            # Don't raise - cache invalidation failure is non-critical
