"""
Asset Allocation Analysis Service

Provides comprehensive portfolio allocation analysis including:
- Asset class allocation (EQUITY, FIXED_INCOME, PROPERTY, etc.)
- Regional allocation (UK, US, EUROPE, ASIA_PACIFIC, etc.)
- Sector allocation (TECHNOLOGY, HEALTHCARE, FINANCIALS, etc.)
- Portfolio summary with aggregated metrics
- Top holdings analysis
- Currency exposure breakdown

Business Rules:
- Only include active accounts (status=ACTIVE, deleted=False)
- Filter out soft-deleted holdings (deleted=False)
- Calculate percentages to 2 decimal places
- Group by asset_class, region, and sector
- Sort top holdings by current_value descending
- Handle empty portfolios gracefully

Performance:
- Target: <500ms for allocation calculations
- Target: <1s for complete portfolio summary
- Use async database operations throughout
"""

import logging
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any, Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.investment import (
    InvestmentAccount, InvestmentHolding, AssetClass, Region,
    AccountStatus
)

logger = logging.getLogger(__name__)


class AssetAllocationService:
    """Service for portfolio asset allocation analysis."""

    def __init__(self, db: AsyncSession):
        """
        Initialize asset allocation service.

        Args:
            db: Database session for operations
        """
        self.db = db

    async def _get_active_holdings(self, user_id: UUID) -> List[InvestmentHolding]:
        """
        Get all active holdings for a user.

        Args:
            user_id: User UUID

        Returns:
            List of active InvestmentHolding objects

        Notes:
            - Only includes holdings from active accounts
            - Filters out soft-deleted holdings
            - Eagerly loads account relationship
        """
        result = await self.db.execute(
            select(InvestmentHolding)
            .join(InvestmentAccount)
            .where(
                and_(
                    InvestmentAccount.user_id == user_id,
                    InvestmentAccount.status == AccountStatus.ACTIVE,
                    InvestmentAccount.deleted == False,
                    InvestmentHolding.deleted == False
                )
            )
            .options(selectinload(InvestmentHolding.account))
        )
        return result.scalars().all()

    async def calculate_allocation_by_asset_class(
        self,
        user_id: UUID
    ) -> Dict[str, Dict[str, Decimal]]:
        """
        Calculate portfolio allocation by asset class.

        Groups all user's holdings by asset_class (EQUITY, FIXED_INCOME, PROPERTY,
        COMMODITY, CASH, ALTERNATIVE) and calculates total value and percentage
        of portfolio for each class.

        Args:
            user_id: User UUID

        Returns:
            Dict mapping asset_class to {value: Decimal, percentage: Decimal}
            Example:
            {
                'EQUITY': {'value': Decimal('50000.00'), 'percentage': Decimal('60.00')},
                'FIXED_INCOME': {'value': Decimal('20000.00'), 'percentage': Decimal('24.00')},
                'CASH': {'value': Decimal('13333.33'), 'percentage': Decimal('16.00')}
            }

        Notes:
            - Returns empty dict if no holdings
            - Percentages rounded to 2 decimal places
            - Total value calculated from current_value property
        """
        logger.info(f"Calculating asset class allocation for user {user_id}")

        holdings = await self._get_active_holdings(user_id)

        if not holdings:
            logger.info(f"No active holdings found for user {user_id}")
            return {}

        # Calculate total portfolio value
        total_value = sum(holding.current_value for holding in holdings)

        if total_value == 0:
            logger.warning(f"Total portfolio value is zero for user {user_id}")
            return {}

        # Group by asset class
        allocation: Dict[str, Decimal] = defaultdict(Decimal)
        for holding in holdings:
            allocation[holding.asset_class.value] += holding.current_value

        # Calculate percentages
        result = {}
        for asset_class, value in allocation.items():
            percentage = (value / total_value * 100).quantize(Decimal('0.01'))
            result[asset_class] = {
                'value': value,
                'percentage': percentage
            }

        logger.info(
            f"Asset class allocation calculated for user {user_id}: "
            f"{len(result)} classes, total_value={total_value}"
        )

        return result

    async def calculate_allocation_by_region(
        self,
        user_id: UUID
    ) -> Dict[str, Dict[str, Decimal]]:
        """
        Calculate portfolio allocation by geographic region.

        Groups holdings by region (UK, US, EUROPE, ASIA_PACIFIC, EMERGING_MARKETS,
        GLOBAL) and calculates total value and percentage for each region.

        Args:
            user_id: User UUID

        Returns:
            Dict mapping region to {value: Decimal, percentage: Decimal}
            Example:
            {
                'UK': {'value': Decimal('30000.00'), 'percentage': Decimal('36.00')},
                'US': {'value': Decimal('25000.00'), 'percentage': Decimal('30.00')},
                'EUROPE': {'value': Decimal('18333.33'), 'percentage': Decimal('22.00')},
                'GLOBAL': {'value': Decimal('10000.00'), 'percentage': Decimal('12.00')}
            }

        Notes:
            - Returns empty dict if no holdings
            - Percentages rounded to 2 decimal places
        """
        logger.info(f"Calculating region allocation for user {user_id}")

        holdings = await self._get_active_holdings(user_id)

        if not holdings:
            logger.info(f"No active holdings found for user {user_id}")
            return {}

        # Calculate total portfolio value
        total_value = sum(holding.current_value for holding in holdings)

        if total_value == 0:
            logger.warning(f"Total portfolio value is zero for user {user_id}")
            return {}

        # Group by region
        allocation: Dict[str, Decimal] = defaultdict(Decimal)
        for holding in holdings:
            allocation[holding.region.value] += holding.current_value

        # Calculate percentages
        result = {}
        for region, value in allocation.items():
            percentage = (value / total_value * 100).quantize(Decimal('0.01'))
            result[region] = {
                'value': value,
                'percentage': percentage
            }

        logger.info(
            f"Region allocation calculated for user {user_id}: "
            f"{len(result)} regions, total_value={total_value}"
        )

        return result

    async def calculate_allocation_by_sector(
        self,
        user_id: UUID
    ) -> Dict[str, Dict[str, Decimal]]:
        """
        Calculate portfolio allocation by sector.

        Groups holdings by sector (TECHNOLOGY, HEALTHCARE, FINANCIALS, CONSUMER,
        ENERGY, etc.) and calculates total value and percentage for each sector.

        Args:
            user_id: User UUID

        Returns:
            Dict mapping sector to {value: Decimal, percentage: Decimal}
            Example:
            {
                'TECHNOLOGY': {'value': Decimal('40000.00'), 'percentage': Decimal('48.00')},
                'HEALTHCARE': {'value': Decimal('20000.00'), 'percentage': Decimal('24.00')},
                'FINANCIALS': {'value': Decimal('15000.00'), 'percentage': Decimal('18.00')},
                'CONSUMER': {'value': Decimal('8333.33'), 'percentage': Decimal('10.00')}
            }

        Notes:
            - Returns empty dict if no holdings
            - Percentages rounded to 2 decimal places
            - Holdings with null sector are grouped under 'UNCLASSIFIED'
        """
        logger.info(f"Calculating sector allocation for user {user_id}")

        holdings = await self._get_active_holdings(user_id)

        if not holdings:
            logger.info(f"No active holdings found for user {user_id}")
            return {}

        # Calculate total portfolio value
        total_value = sum(holding.current_value for holding in holdings)

        if total_value == 0:
            logger.warning(f"Total portfolio value is zero for user {user_id}")
            return {}

        # Group by sector
        allocation: Dict[str, Decimal] = defaultdict(Decimal)
        for holding in holdings:
            sector = holding.sector if holding.sector else 'UNCLASSIFIED'
            allocation[sector] += holding.current_value

        # Calculate percentages
        result = {}
        for sector, value in allocation.items():
            percentage = (value / total_value * 100).quantize(Decimal('0.01'))
            result[sector] = {
                'value': value,
                'percentage': percentage
            }

        logger.info(
            f"Sector allocation calculated for user {user_id}: "
            f"{len(result)} sectors, total_value={total_value}"
        )

        return result

    async def get_portfolio_summary(
        self,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get comprehensive portfolio summary with aggregated metrics.

        Calculates:
        - Total portfolio value (sum of all current_value across all holdings)
        - Total unrealized gains/losses (sum of unrealized_gain across all holdings)
        - Unrealized gain percentage
        - Number of holdings
        - Number of accounts
        - Currency exposure (breakdown by currency)
        - Asset allocation breakdown (by class)
        - Top 10 holdings (sorted by value, descending)

        Args:
            user_id: User UUID

        Returns:
            Dict with comprehensive portfolio summary:
            {
                'total_value': Decimal,
                'total_cost_basis': Decimal,
                'total_unrealized_gain': Decimal,
                'unrealized_gain_percentage': Decimal,
                'num_holdings': int,
                'num_accounts': int,
                'currency_exposure': {
                    'GBP': {'value': Decimal, 'percentage': Decimal},
                    'USD': {'value': Decimal, 'percentage': Decimal},
                    ...
                },
                'asset_allocation': {
                    'EQUITY': {'value': Decimal, 'percentage': Decimal},
                    ...
                },
                'top_holdings': [
                    {
                        'id': str,
                        'security_name': str,
                        'ticker': str,
                        'quantity': Decimal,
                        'current_price': Decimal,
                        'current_value': Decimal,
                        'unrealized_gain': Decimal,
                        'unrealized_gain_percentage': Decimal,
                        'asset_class': str,
                        'region': str,
                        'percentage_of_portfolio': Decimal
                    },
                    ...
                ]
            }

        Notes:
            - Returns empty structure if no holdings
            - All monetary values are Decimal
            - Percentages calculated to 2 decimal places
        """
        logger.info(f"Generating portfolio summary for user {user_id}")

        holdings = await self._get_active_holdings(user_id)

        # Get unique account count
        account_result = await self.db.execute(
            select(InvestmentAccount)
            .where(
                and_(
                    InvestmentAccount.user_id == user_id,
                    InvestmentAccount.status == AccountStatus.ACTIVE,
                    InvestmentAccount.deleted == False
                )
            )
        )
        accounts = account_result.scalars().all()
        num_accounts = len(accounts)

        if not holdings:
            logger.info(f"No active holdings found for user {user_id}")
            return {
                'total_value': Decimal('0.00'),
                'total_cost_basis': Decimal('0.00'),
                'total_unrealized_gain': Decimal('0.00'),
                'unrealized_gain_percentage': Decimal('0.00'),
                'num_holdings': 0,
                'num_accounts': num_accounts,
                'currency_exposure': {},
                'asset_allocation': {},
                'top_holdings': []
            }

        # Calculate aggregated metrics
        total_value = Decimal('0.00')
        total_cost_basis = Decimal('0.00')
        total_unrealized_gain = Decimal('0.00')

        for holding in holdings:
            current_value = holding.current_value
            total_value += current_value

            # Calculate cost basis
            cost_basis = holding.purchase_price * holding.quantity
            total_cost_basis += cost_basis

            # Calculate unrealized gain
            unrealized_gain = holding.unrealized_gain
            total_unrealized_gain += unrealized_gain

        # Calculate unrealized gain percentage
        if total_cost_basis > 0:
            unrealized_gain_percentage = (
                total_unrealized_gain / total_cost_basis * 100
            ).quantize(Decimal('0.01'))
        else:
            unrealized_gain_percentage = Decimal('0.00')

        # Currency exposure
        currency_exposure: Dict[str, Decimal] = defaultdict(Decimal)
        for holding in holdings:
            currency = holding.purchase_currency
            currency_exposure[currency] += holding.current_value

        # Calculate currency percentages
        currency_breakdown = {}
        if total_value > 0:
            for currency, value in currency_exposure.items():
                percentage = (value / total_value * 100).quantize(Decimal('0.01'))
                currency_breakdown[currency] = {
                    'value': value,
                    'percentage': percentage
                }

        # Get asset allocation (reuse existing method)
        asset_allocation = await self.calculate_allocation_by_asset_class(user_id)

        # Top 10 holdings
        sorted_holdings = sorted(
            holdings,
            key=lambda h: h.current_value,
            reverse=True
        )[:10]

        top_holdings = []
        for holding in sorted_holdings:
            percentage_of_portfolio = Decimal('0.00')
            if total_value > 0:
                percentage_of_portfolio = (
                    holding.current_value / total_value * 100
                ).quantize(Decimal('0.01'))

            top_holdings.append({
                'id': str(holding.id),
                'security_name': holding.security_name,
                'ticker': holding.ticker,
                'quantity': holding.quantity,
                'current_price': holding.current_price,
                'current_value': holding.current_value,
                'unrealized_gain': holding.unrealized_gain,
                'unrealized_gain_percentage': holding.unrealized_gain_percentage,
                'asset_class': holding.asset_class.value,
                'region': holding.region.value,
                'percentage_of_portfolio': percentage_of_portfolio
            })

        summary = {
            'total_value': total_value,
            'total_cost_basis': total_cost_basis,
            'total_unrealized_gain': total_unrealized_gain,
            'unrealized_gain_percentage': unrealized_gain_percentage,
            'num_holdings': len(holdings),
            'num_accounts': num_accounts,
            'currency_exposure': currency_breakdown,
            'asset_allocation': asset_allocation,
            'top_holdings': top_holdings
        }

        logger.info(
            f"Portfolio summary generated for user {user_id}: "
            f"total_value={total_value}, num_holdings={len(holdings)}, "
            f"num_accounts={num_accounts}"
        )

        return summary


# Factory function
def get_asset_allocation_service(db: AsyncSession) -> AssetAllocationService:
    """
    Get asset allocation service instance.

    Args:
        db: Database session

    Returns:
        AssetAllocationService instance
    """
    return AssetAllocationService(db)
