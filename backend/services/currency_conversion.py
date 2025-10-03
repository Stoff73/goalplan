"""
Currency conversion service with caching.

This module provides currency conversion functionality:
- Fetches exchange rates from external API (exchangerate-api.com)
- Caches rates daily in database for performance
- Supports GBP, ZAR, USD, EUR currency pairs
- Historical rate lookup for tax year calculations
- Fallback to cached rates on API failure

Performance:
- Database-cached rates: <10ms lookup
- API fallback: <500ms
- Daily rate caching reduces API calls

API Integration:
- exchangerate-api.com (free tier: 1,500 requests/month)
- Alternative: openexchangerates.org, fixer.io
"""

import aiohttp
from datetime import date, timedelta, datetime
from typing import Optional, Tuple, List
from decimal import Decimal
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from models.income import ExchangeRate

logger = logging.getLogger(__name__)


class CurrencyConversionService:
    """
    Currency conversion service with caching.

    Uses exchangerate-api.com (or similar) for live rates.
    Caches rates daily for performance.
    """

    # API configuration
    API_URL = "https://api.exchangerate-api.com/v4/latest/{currency}"
    API_TIMEOUT = 10  # seconds
    CACHE_TTL_DAYS = 1  # Cache rates for 1 day

    # Supported currencies
    SUPPORTED_CURRENCIES = ['GBP', 'ZAR', 'USD', 'EUR']

    def __init__(self, db: AsyncSession):
        """
        Initialize currency conversion service.

        Args:
            db: Database session for caching rates
        """
        self.db = db

    async def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
        rate_date: Optional[date] = None
    ) -> Decimal:
        """
        Get exchange rate for a specific date.

        Args:
            from_currency: Source currency (GBP, ZAR, USD, EUR)
            to_currency: Target currency
            rate_date: Date for rate (default: today)

        Returns:
            Decimal: Exchange rate

        Raises:
            ValueError: If currencies not supported
            Exception: If rate not available and API fails
        """
        # Validate currencies
        self._validate_currency(from_currency)
        self._validate_currency(to_currency)

        # Same currency
        if from_currency == to_currency:
            return Decimal('1.0')

        # Default to today
        rate_date = rate_date or date.today()

        # Check cache first
        cached_rate = await self._get_cached_rate(from_currency, to_currency, rate_date)
        if cached_rate:
            logger.info(
                f"Using cached rate: {from_currency}/{to_currency} = {cached_rate} on {rate_date}"
            )
            return cached_rate

        # Fetch from API (only for current/recent dates)
        if rate_date >= date.today() - timedelta(days=7):
            try:
                rate = await self._fetch_rate_from_api(from_currency, to_currency, rate_date)
                # Cache it
                await self._cache_rate(from_currency, to_currency, rate_date, rate)
                logger.info(
                    f"Fetched and cached rate from API: {from_currency}/{to_currency} = {rate} on {rate_date}"
                )
                return rate
            except Exception as e:
                logger.error(f"Failed to fetch rate from API: {e}")
                # Try to get nearest cached rate as fallback
                fallback_rate = await self._get_nearest_cached_rate(from_currency, to_currency, rate_date)
                if fallback_rate:
                    logger.warning(
                        f"Using nearest cached rate as fallback: {from_currency}/{to_currency} = {fallback_rate}"
                    )
                    return fallback_rate
                raise

        # For historical dates, use cached rate or fail
        logger.error(
            f"No cached rate available for {from_currency}/{to_currency} on {rate_date}"
        )
        raise ValueError(
            f"Exchange rate not available for {from_currency}/{to_currency} on {rate_date}. "
            f"Please ensure historical rates are imported."
        )

    async def convert_amount(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        rate_date: Optional[date] = None
    ) -> Tuple[Decimal, Decimal, date]:
        """
        Convert amount from one currency to another.

        Args:
            amount: Amount to convert
            from_currency: Source currency
            to_currency: Target currency
            rate_date: Date for exchange rate (default: today)

        Returns:
            tuple: (converted_amount, exchange_rate, rate_date_used)
        """
        rate_date = rate_date or date.today()
        rate = await self.get_exchange_rate(from_currency, to_currency, rate_date)
        converted = (amount * rate).quantize(Decimal('0.01'))
        return (converted, rate, rate_date)

    async def get_historical_rates(
        self,
        from_currency: str,
        to_currency: str,
        start_date: date,
        end_date: date
    ) -> List[dict]:
        """
        Get historical rates for a date range.

        Args:
            from_currency: Source currency
            to_currency: Target currency
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            list: List of {date, rate} dicts
        """
        self._validate_currency(from_currency)
        self._validate_currency(to_currency)

        stmt = select(ExchangeRate).where(
            and_(
                ExchangeRate.from_currency == from_currency,
                ExchangeRate.to_currency == to_currency,
                ExchangeRate.rate_date >= start_date,
                ExchangeRate.rate_date <= end_date
            )
        ).order_by(ExchangeRate.rate_date)

        result = await self.db.execute(stmt)
        rates = result.scalars().all()

        return [
            {
                'date': rate.rate_date,
                'rate': rate.rate,
                'source': rate.source
            }
            for rate in rates
        ]

    async def _get_cached_rate(
        self,
        from_currency: str,
        to_currency: str,
        rate_date: date
    ) -> Optional[Decimal]:
        """Get rate from exchange_rates table."""
        stmt = select(ExchangeRate).where(
            and_(
                ExchangeRate.from_currency == from_currency,
                ExchangeRate.to_currency == to_currency,
                ExchangeRate.rate_date == rate_date
            )
        )

        result = await self.db.execute(stmt)
        rate_record = result.scalar_one_or_none()

        if rate_record:
            return rate_record.rate

        return None

    async def _get_nearest_cached_rate(
        self,
        from_currency: str,
        to_currency: str,
        target_date: date
    ) -> Optional[Decimal]:
        """
        Get nearest cached rate (within 7 days) as fallback.

        Args:
            from_currency: Source currency
            to_currency: Target currency
            target_date: Target date

        Returns:
            Nearest rate within 7 days, or None
        """
        # Try dates within +/- 7 days
        stmt = select(ExchangeRate).where(
            and_(
                ExchangeRate.from_currency == from_currency,
                ExchangeRate.to_currency == to_currency,
                ExchangeRate.rate_date >= target_date - timedelta(days=7),
                ExchangeRate.rate_date <= target_date + timedelta(days=7)
            )
        ).order_by(
            # Order by closeness to target date
            (ExchangeRate.rate_date - target_date).abs()
        ).limit(1)

        result = await self.db.execute(stmt)
        rate_record = result.scalar_one_or_none()

        if rate_record:
            logger.warning(
                f"Using rate from {rate_record.rate_date} instead of {target_date} "
                f"({(target_date - rate_record.rate_date).days} days difference)"
            )
            return rate_record.rate

        return None

    async def _cache_rate(
        self,
        from_currency: str,
        to_currency: str,
        rate_date: date,
        rate: Decimal
    ) -> None:
        """Store rate in exchange_rates table."""
        try:
            # Check if already exists
            existing = await self._get_cached_rate(from_currency, to_currency, rate_date)
            if existing:
                logger.info(f"Rate already cached for {from_currency}/{to_currency} on {rate_date}")
                return

            # Insert new rate
            exchange_rate = ExchangeRate(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=rate,
                rate_date=rate_date,
                source='exchangerate-api',
                created_at=datetime.utcnow()
            )

            self.db.add(exchange_rate)
            await self.db.commit()

            logger.info(
                f"Cached exchange rate: {from_currency}/{to_currency} = {rate} on {rate_date}"
            )

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to cache exchange rate: {e}")
            # Don't raise - caching failure shouldn't break conversion

    async def _fetch_rate_from_api(
        self,
        from_currency: str,
        to_currency: str,
        rate_date: date
    ) -> Decimal:
        """
        Fetch rate from external API.

        Args:
            from_currency: Source currency
            to_currency: Target currency
            rate_date: Date for rate (not used by exchangerate-api, always returns latest)

        Returns:
            Exchange rate

        Raises:
            aiohttp.ClientError: If API request fails
            KeyError: If currency not found in response
            ValueError: If rate invalid
        """
        url = self.API_URL.format(currency=from_currency)

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.API_TIMEOUT)) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()

                    # Check for errors in response
                    if 'error' in data:
                        raise ValueError(f"API error: {data.get('error-type', 'Unknown error')}")

                    # Extract rate
                    if 'rates' not in data or to_currency not in data['rates']:
                        raise KeyError(
                            f"Currency {to_currency} not found in API response"
                        )

                    rate = Decimal(str(data['rates'][to_currency]))

                    # Validate rate
                    if rate <= 0:
                        raise ValueError(f"Invalid exchange rate: {rate}")

                    return rate

        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {e}")
            raise
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid API response: {e}")
            raise

    def _validate_currency(self, currency: str) -> None:
        """
        Validate currency code.

        Args:
            currency: Currency code to validate

        Raises:
            ValueError: If currency not supported
        """
        if currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(
                f"Currency {currency} not supported. "
                f"Supported currencies: {', '.join(self.SUPPORTED_CURRENCIES)}"
            )


# Helper function for tax year calculations
def get_uk_tax_year(income_date: date) -> str:
    """
    Calculate UK tax year from date.

    UK tax year: April 6 to April 5
    Example: 2023-05-01 → '2023/24'

    Args:
        income_date: Date of income

    Returns:
        UK tax year string (e.g., '2023/24')
    """
    if income_date.month < 4 or (income_date.month == 4 and income_date.day < 6):
        year = income_date.year - 1
    else:
        year = income_date.year

    return f"{year}/{str(year + 1)[-2:]}"


def get_sa_tax_year(income_date: date) -> str:
    """
    Calculate SA tax year from date.

    SA tax year: March 1 to February 28/29
    Example: 2023-05-01 → '2023/24'

    Args:
        income_date: Date of income

    Returns:
        SA tax year string (e.g., '2023/24')
    """
    if income_date.month < 3:
        year = income_date.year - 1
    else:
        year = income_date.year

    return f"{year}/{str(year + 1)[-2:]}"
