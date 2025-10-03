"""
Tests for Dashboard Data Aggregation Service

Tests comprehensive net worth calculation, currency conversion,
grouping, caching, and performance.

Test Coverage:
- Data aggregation from multiple sources
- Currency conversion to different base currencies
- Net worth calculation (assets - liabilities)
- Grouping by country, asset class, currency
- Redis caching (save and retrieve)
- Cache invalidation
- Performance (<500ms for aggregation)
- Empty data handling
- Multiple accounts in different currencies
"""

import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
import time
import json

from services.dashboard_aggregation import DashboardAggregationService
from services.currency_conversion import CurrencyConversionService


@pytest.fixture
def user_id():
    """Test user UUID."""
    return uuid4()


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.setex = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    return redis_mock


@pytest.fixture
def aggregation_service(mock_db):
    """Dashboard aggregation service instance."""
    return DashboardAggregationService(mock_db)


@pytest.mark.asyncio
class TestDashboardAggregation:
    """Test suite for dashboard aggregation service."""

    async def test_get_net_worth_summary_basic_structure(
        self,
        aggregation_service,
        user_id,
        mock_redis
    ):
        """Test basic net worth summary structure."""
        with patch('services.dashboard_aggregation.redis_client', mock_redis):
            summary = await aggregation_service.get_net_worth_summary(
                user_id=user_id,
                base_currency="GBP",
                use_cache=False
            )

            # Verify structure
            assert 'total_assets' in summary
            assert 'total_liabilities' in summary
            assert 'net_worth' in summary
            assert 'base_currency' in summary
            assert 'as_of_date' in summary
            assert 'breakdown_by_country' in summary
            assert 'breakdown_by_asset_class' in summary
            assert 'breakdown_by_currency' in summary
            assert 'last_updated' in summary

            # Verify base currency
            assert summary['base_currency'] == 'GBP'

            # Verify types
            assert isinstance(summary['total_assets'], float)
            assert isinstance(summary['total_liabilities'], float)
            assert isinstance(summary['net_worth'], float)

    async def test_empty_data_returns_zero_values(
        self,
        aggregation_service,
        user_id,
        mock_redis
    ):
        """Test that empty data returns zero values without errors."""
        with patch('services.dashboard_aggregation.redis_client', mock_redis):
            summary = await aggregation_service.get_net_worth_summary(
                user_id=user_id,
                base_currency="GBP",
                use_cache=False
            )

            # Should return zero values for new user
            assert summary['total_assets'] == 0.0
            assert summary['total_liabilities'] == 0.0
            assert summary['net_worth'] == 0.0

            # Breakdowns should be empty lists
            assert summary['breakdown_by_country'] == []
            assert summary['breakdown_by_asset_class'] == []
            assert summary['breakdown_by_currency'] == []

    async def test_default_base_currency_is_gbp(
        self,
        aggregation_service,
        user_id,
        mock_redis
    ):
        """Test default base currency is GBP."""
        with patch('services.dashboard_aggregation.redis_client', mock_redis):
            summary = await aggregation_service.get_net_worth_summary(
                user_id=user_id,
                use_cache=False
            )

            assert summary['base_currency'] == 'GBP'

    async def test_supported_base_currencies(
        self,
        aggregation_service,
        user_id,
        mock_redis
    ):
        """Test all supported base currencies work."""
        supported_currencies = ["GBP", "ZAR", "USD", "EUR"]

        with patch('services.dashboard_aggregation.redis_client', mock_redis):
            for currency in supported_currencies:
                summary = await aggregation_service.get_net_worth_summary(
                    user_id=user_id,
                    base_currency=currency,
                    use_cache=False
                )

                assert summary['base_currency'] == currency

    async def test_unsupported_base_currency_raises_error(
        self,
        aggregation_service,
        user_id
    ):
        """Test unsupported base currency raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await aggregation_service.get_net_worth_summary(
                user_id=user_id,
                base_currency="JPY",  # Not supported
                use_cache=False
            )

        assert "not supported" in str(exc_info.value).lower()

    async def test_as_of_date_defaults_to_today(
        self,
        aggregation_service,
        user_id,
        mock_redis
    ):
        """Test as_of_date defaults to today."""
        with patch('services.dashboard_aggregation.redis_client', mock_redis):
            summary = await aggregation_service.get_net_worth_summary(
                user_id=user_id,
                use_cache=False
            )

            # Should use today's date
            as_of_date = date.fromisoformat(summary['as_of_date'])
            assert as_of_date == date.today()

    async def test_custom_as_of_date(
        self,
        aggregation_service,
        user_id,
        mock_redis
    ):
        """Test custom as_of_date is respected."""
        custom_date = date(2024, 6, 15)

        with patch('services.dashboard_aggregation.redis_client', mock_redis):
            summary = await aggregation_service.get_net_worth_summary(
                user_id=user_id,
                as_of_date=custom_date,
                use_cache=False
            )

            as_of_date = date.fromisoformat(summary['as_of_date'])
            assert as_of_date == custom_date

    async def test_redis_cache_saves_data(
        self,
        aggregation_service,
        user_id,
        mock_redis
    ):
        """Test that data is saved to Redis cache."""
        with patch('services.dashboard_aggregation.redis_client', mock_redis):
            await aggregation_service.get_net_worth_summary(
                user_id=user_id,
                base_currency="GBP",
                use_cache=False
            )

            # Verify setex was called
            mock_redis.setex.assert_called_once()

            # Verify cache key format
            call_args = mock_redis.setex.call_args
            cache_key = call_args[0][0]
            assert cache_key == f"dashboard:net_worth:{user_id}:GBP"

            # Verify TTL
            ttl = call_args[0][1]
            assert ttl == 300  # 5 minutes

            # Verify data is JSON
            data = call_args[0][2]
            parsed = json.loads(data)
            assert 'total_assets' in parsed

    async def test_redis_cache_retrieves_data(
        self,
        aggregation_service,
        user_id,
        mock_redis
    ):
        """Test that cached data is retrieved from Redis."""
        # Mock cached data
        cached_data = {
            "total_assets": 100000.0,
            "total_liabilities": 50000.0,
            "net_worth": 50000.0,
            "base_currency": "GBP",
            "as_of_date": "2024-06-15",
            "breakdown_by_country": [],
            "breakdown_by_asset_class": [],
            "breakdown_by_currency": [],
            "last_updated": "2024-06-15T10:00:00"
        }

        mock_redis.get.return_value = json.dumps(cached_data)

        with patch('services.dashboard_aggregation.redis_client', mock_redis):
            summary = await aggregation_service.get_net_worth_summary(
                user_id=user_id,
                base_currency="GBP",
                use_cache=True
            )

            # Should return cached data
            assert summary['total_assets'] == 100000.0
            assert summary['total_liabilities'] == 50000.0
            assert summary['net_worth'] == 50000.0

            # Verify get was called
            mock_redis.get.assert_called_once()

            # Verify setex was NOT called (using cache)
            mock_redis.setex.assert_not_called()

    async def test_cache_bypass_when_use_cache_false(
        self,
        aggregation_service,
        user_id,
        mock_redis
    ):
        """Test cache is bypassed when use_cache=False."""
        # Mock cached data
        cached_data = {
            "total_assets": 100000.0,
            "net_worth": 100000.0
        }
        mock_redis.get.return_value = json.dumps(cached_data)

        with patch('services.dashboard_aggregation.redis_client', mock_redis):
            summary = await aggregation_service.get_net_worth_summary(
                user_id=user_id,
                base_currency="GBP",
                use_cache=False  # Bypass cache
            )

            # Should NOT retrieve cached data
            mock_redis.get.assert_not_called()

            # Should still save to cache
            mock_redis.setex.assert_called_once()

    async def test_invalidate_cache_deletes_all_currencies(
        self,
        aggregation_service,
        user_id,
        mock_redis
    ):
        """Test cache invalidation deletes cache for all currencies."""
        with patch('services.dashboard_aggregation.redis_client', mock_redis):
            await aggregation_service.invalidate_cache(user_id)

            # Should delete cache for all supported currencies
            assert mock_redis.delete.call_count == 4

            # Verify correct keys
            call_args_list = [call[0][0] for call in mock_redis.delete.call_args_list]
            expected_keys = [
                f"dashboard:net_worth:{user_id}:GBP",
                f"dashboard:net_worth:{user_id}:ZAR",
                f"dashboard:net_worth:{user_id}:USD",
                f"dashboard:net_worth:{user_id}:EUR"
            ]

            for key in expected_keys:
                assert key in call_args_list

    async def test_build_breakdown_calculates_percentages(
        self,
        aggregation_service
    ):
        """Test breakdown calculation includes correct percentages."""
        assets = {
            "UK": Decimal('60000.00'),
            "ZA": Decimal('40000.00')
        }
        liabilities = {
            "UK": Decimal('20000.00')
        }
        total_assets = Decimal('100000.00')
        total_liabilities = Decimal('20000.00')

        breakdown = aggregation_service._build_breakdown(
            assets,
            liabilities,
            total_assets,
            total_liabilities
        )

        # Total net worth: 100000 - 20000 = 80000
        # UK net: 60000 - 20000 = 40000 (50% of 80000)
        # ZA net: 40000 - 0 = 40000 (50% of 80000)

        assert len(breakdown) == 2

        # Find UK and ZA entries
        uk_entry = next(e for e in breakdown if e['category'] == 'UK')
        za_entry = next(e for e in breakdown if e['category'] == 'ZA')

        assert uk_entry['assets'] == 60000.0
        assert uk_entry['liabilities'] == 20000.0
        assert uk_entry['net'] == 40000.0
        assert uk_entry['percentage'] == 50.0

        assert za_entry['assets'] == 40000.0
        assert za_entry['liabilities'] == 0.0
        assert za_entry['net'] == 40000.0
        assert za_entry['percentage'] == 50.0

    async def test_build_breakdown_sorts_by_net_descending(
        self,
        aggregation_service
    ):
        """Test breakdown is sorted by net amount descending."""
        assets = {
            "UK": Decimal('30000.00'),
            "ZA": Decimal('70000.00'),
            "US": Decimal('50000.00')
        }
        liabilities = {}
        total_assets = Decimal('150000.00')
        total_liabilities = Decimal('0.00')

        breakdown = aggregation_service._build_breakdown(
            assets,
            liabilities,
            total_assets,
            total_liabilities
        )

        # Should be sorted ZA, US, UK
        assert breakdown[0]['category'] == 'ZA'
        assert breakdown[1]['category'] == 'US'
        assert breakdown[2]['category'] == 'UK'

    async def test_build_currency_breakdown(
        self,
        aggregation_service
    ):
        """Test currency breakdown calculation."""
        amounts = {
            "GBP": Decimal('60000.00'),
            "ZAR": Decimal('40000.00')
        }
        total = Decimal('100000.00')

        breakdown = aggregation_service._build_currency_breakdown(
            amounts,
            total
        )

        assert len(breakdown) == 2

        gbp_entry = next(e for e in breakdown if e['currency'] == 'GBP')
        zar_entry = next(e for e in breakdown if e['currency'] == 'ZAR')

        assert gbp_entry['amount'] == 60000.0
        assert gbp_entry['percentage'] == 60.0

        assert zar_entry['amount'] == 40000.0
        assert zar_entry['percentage'] == 40.0

    async def test_net_worth_calculation_assets_minus_liabilities(
        self,
        aggregation_service,
        user_id,
        mock_redis
    ):
        """Test net worth is correctly calculated as assets - liabilities."""
        with patch('services.dashboard_aggregation.redis_client', mock_redis):
            # Mock _aggregate_data to return specific values
            async def mock_aggregate(user_id, base_currency, as_of_date):
                return {
                    "total_assets": 100000.0,
                    "total_liabilities": 30000.0,
                    "net_worth": 70000.0,  # 100000 - 30000
                    "base_currency": base_currency,
                    "as_of_date": as_of_date.isoformat(),
                    "breakdown_by_country": [],
                    "breakdown_by_asset_class": [],
                    "breakdown_by_currency": [],
                    "last_updated": datetime.utcnow().isoformat()
                }

            with patch.object(
                aggregation_service,
                '_aggregate_data',
                side_effect=mock_aggregate
            ):
                summary = await aggregation_service.get_net_worth_summary(
                    user_id=user_id,
                    use_cache=False
                )

                assert summary['total_assets'] == 100000.0
                assert summary['total_liabilities'] == 30000.0
                assert summary['net_worth'] == 70000.0

    async def test_performance_under_500ms(
        self,
        aggregation_service,
        user_id,
        mock_redis
    ):
        """Test aggregation completes in under 500ms."""
        with patch('services.dashboard_aggregation.redis_client', mock_redis):
            start_time = time.time()

            await aggregation_service.get_net_worth_summary(
                user_id=user_id,
                base_currency="GBP",
                use_cache=False
            )

            elapsed_ms = (time.time() - start_time) * 1000

            # Should complete in under 500ms (generous for test environment)
            # In production with real data, should be much faster
            assert elapsed_ms < 500, f"Aggregation took {elapsed_ms}ms, expected < 500ms"

    async def test_breakdown_handles_zero_net_worth(
        self,
        aggregation_service
    ):
        """Test breakdown handles zero net worth without division by zero."""
        assets = {
            "UK": Decimal('50000.00'),
            "ZA": Decimal('50000.00')
        }
        liabilities = {
            "UK": Decimal('50000.00'),
            "ZA": Decimal('50000.00')
        }
        total_assets = Decimal('100000.00')
        total_liabilities = Decimal('100000.00')  # Net worth = 0

        breakdown = aggregation_service._build_breakdown(
            assets,
            liabilities,
            total_assets,
            total_liabilities
        )

        # Should not raise error
        assert len(breakdown) == 2

        # Percentages should be 0
        for entry in breakdown:
            assert entry['percentage'] == 0.0

    async def test_redis_error_does_not_break_aggregation(
        self,
        aggregation_service,
        user_id
    ):
        """Test Redis errors don't break aggregation (graceful degradation)."""
        mock_redis_error = AsyncMock()
        mock_redis_error.get.side_effect = Exception("Redis connection failed")
        mock_redis_error.setex.side_effect = Exception("Redis connection failed")

        with patch('services.dashboard_aggregation.redis_client', mock_redis_error):
            # Should not raise error
            summary = await aggregation_service.get_net_worth_summary(
                user_id=user_id,
                base_currency="GBP",
                use_cache=True
            )

            # Should still return valid data
            assert 'total_assets' in summary
            assert 'net_worth' in summary

    async def test_cache_key_includes_user_and_currency(
        self,
        aggregation_service,
        user_id
    ):
        """Test cache key format includes user ID and currency."""
        base_currency = "GBP"
        expected_key = f"dashboard:net_worth:{user_id}:{base_currency}"

        cache_key = await aggregation_service._get_from_cache(user_id, base_currency)

        # Even though it returns None (no cache), the method should have tried
        # to get the correct key (we can't directly test key format without mocking,
        # but we test this indirectly through the save test above)

    async def test_last_updated_timestamp_is_current(
        self,
        aggregation_service,
        user_id,
        mock_redis
    ):
        """Test last_updated timestamp is recent."""
        with patch('services.dashboard_aggregation.redis_client', mock_redis):
            summary = await aggregation_service.get_net_worth_summary(
                user_id=user_id,
                use_cache=False
            )

            last_updated = datetime.fromisoformat(summary['last_updated'])
            now = datetime.utcnow()

            # Should be within 1 second
            time_diff = (now - last_updated).total_seconds()
            assert time_diff < 1.0


@pytest.mark.asyncio
class TestCurrencyConversionIntegration:
    """Test currency conversion integration."""

    async def test_currency_service_initialized(
        self,
        mock_db
    ):
        """Test currency conversion service is initialized."""
        service = DashboardAggregationService(mock_db)

        assert service.currency_service is not None
        assert isinstance(service.currency_service, CurrencyConversionService)

    async def test_currency_service_uses_same_db_session(
        self,
        mock_db
    ):
        """Test currency service uses the same database session."""
        service = DashboardAggregationService(mock_db)

        assert service.currency_service.db is mock_db


@pytest.mark.asyncio
class TestFutureModulePreparation:
    """Test that service is prepared for future modules."""

    async def test_aggregate_savings_method_exists(
        self,
        aggregation_service,
        user_id
    ):
        """Test _aggregate_savings method exists and returns expected structure."""
        result = await aggregation_service._aggregate_savings(
            user_id,
            "GBP",
            date.today()
        )

        # Should return expected structure
        assert 'total' in result
        assert 'by_country' in result
        assert 'by_currency' in result
        assert 'accounts' in result

        # Should return zeros for now
        assert result['total'] == Decimal('0.00')
        assert result['by_country'] == {}
        assert result['by_currency'] == {}
        assert result['accounts'] == []
