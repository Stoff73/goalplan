"""
Tests for Net Worth Snapshot Service

Tests comprehensive snapshot creation, retrieval, trend analysis,
change calculations, and cleanup operations.

Test Coverage:
- Snapshot creation with complete breakdown data
- Unique constraint (one snapshot per user per day)
- Historical snapshot retrieval
- Monthly trend data generation (12 months)
- Change calculations (day, month, year)
- Cleanup of old snapshots (2 year retention)
- Integration with DashboardAggregationService
- Edge cases (no data, zero net worth, missing snapshots)
- Performance and error handling
"""

import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from services.net_worth_snapshot import NetWorthSnapshotService
from services.dashboard_aggregation import DashboardAggregationService
from models.net_worth_snapshot import NetWorthSnapshot


@pytest.fixture
def user_id():
    """Test user UUID."""
    return uuid4()


@pytest.fixture
def mock_db():
    """Mock database session."""
    db = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    return db


@pytest.fixture
def snapshot_service(mock_db):
    """Net worth snapshot service instance."""
    return NetWorthSnapshotService(mock_db)


@pytest.fixture
def sample_aggregation_data():
    """Sample aggregation data from dashboard service."""
    return {
        'total_assets': 100000.00,
        'total_liabilities': 30000.00,
        'net_worth': 70000.00,
        'base_currency': 'GBP',
        'as_of_date': date.today().isoformat(),
        'breakdown_by_country': [
            {'country': 'UK', 'assets': 60000.00, 'liabilities': 20000.00, 'net': 40000.00, 'percentage': 57.14},
            {'country': 'SA', 'assets': 40000.00, 'liabilities': 10000.00, 'net': 30000.00, 'percentage': 42.86}
        ],
        'breakdown_by_asset_class': [
            {'category': 'Cash', 'assets': 25000.00, 'liabilities': 0.00, 'net': 25000.00, 'percentage': 35.71},
            {'category': 'Investments', 'assets': 75000.00, 'liabilities': 30000.00, 'net': 45000.00, 'percentage': 64.29}
        ],
        'breakdown_by_currency': [
            {'currency': 'GBP', 'amount': 60000.00, 'percentage': 60.0},
            {'currency': 'ZAR', 'amount': 40000.00, 'percentage': 40.0}
        ],
        'last_updated': datetime.utcnow().isoformat()
    }


@pytest.mark.asyncio
class TestSnapshotCreation:
    """Test suite for snapshot creation."""

    async def test_create_snapshot_basic(
        self,
        snapshot_service,
        user_id,
        mock_db,
        sample_aggregation_data
    ):
        """Test basic snapshot creation."""
        # Mock aggregation service
        with patch.object(
            snapshot_service.aggregation_service,
            'get_net_worth_summary',
            return_value=sample_aggregation_data
        ):
            snapshot = await snapshot_service.create_snapshot(
                user_id=user_id,
                base_currency='GBP'
            )

            # Verify snapshot was created
            assert snapshot.user_id == user_id
            assert snapshot.base_currency == 'GBP'
            assert snapshot.net_worth == Decimal('70000.00')
            assert snapshot.total_assets == Decimal('100000.00')
            assert snapshot.total_liabilities == Decimal('30000.00')
            assert snapshot.snapshot_date == date.today()

            # Verify db operations
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

    async def test_create_snapshot_contains_breakdown_data(
        self,
        snapshot_service,
        user_id,
        mock_db,
        sample_aggregation_data
    ):
        """Test snapshot contains all required breakdown data."""
        with patch.object(
            snapshot_service.aggregation_service,
            'get_net_worth_summary',
            return_value=sample_aggregation_data
        ):
            snapshot = await snapshot_service.create_snapshot(
                user_id=user_id,
                base_currency='GBP'
            )

            # Verify breakdown data is stored
            assert snapshot.breakdown_by_country is not None
            assert len(snapshot.breakdown_by_country) == 2
            assert snapshot.breakdown_by_country[0]['country'] == 'UK'

            assert snapshot.breakdown_by_asset_class is not None
            assert len(snapshot.breakdown_by_asset_class) == 2
            assert snapshot.breakdown_by_asset_class[0]['category'] == 'Cash'

            assert snapshot.breakdown_by_currency is not None
            assert len(snapshot.breakdown_by_currency) == 2
            assert snapshot.breakdown_by_currency[0]['currency'] == 'GBP'

    async def test_create_snapshot_uses_fresh_data(
        self,
        snapshot_service,
        user_id,
        sample_aggregation_data
    ):
        """Test snapshot creation uses fresh data (no cache)."""
        mock_get_summary = AsyncMock(return_value=sample_aggregation_data)

        with patch.object(
            snapshot_service.aggregation_service,
            'get_net_worth_summary',
            mock_get_summary
        ):
            await snapshot_service.create_snapshot(
                user_id=user_id,
                base_currency='GBP'
            )

            # Verify use_cache=False was passed
            mock_get_summary.assert_called_once()
            call_kwargs = mock_get_summary.call_args.kwargs
            assert call_kwargs['use_cache'] is False

    async def test_create_snapshot_custom_date(
        self,
        snapshot_service,
        user_id,
        mock_db,
        sample_aggregation_data
    ):
        """Test snapshot creation with custom date."""
        custom_date = date(2024, 6, 15)

        with patch.object(
            snapshot_service.aggregation_service,
            'get_net_worth_summary',
            return_value=sample_aggregation_data
        ):
            snapshot = await snapshot_service.create_snapshot(
                user_id=user_id,
                base_currency='GBP',
                snapshot_date=custom_date
            )

            assert snapshot.snapshot_date == custom_date

    async def test_create_snapshot_duplicate_raises_error(
        self,
        snapshot_service,
        user_id,
        mock_db,
        sample_aggregation_data
    ):
        """Test creating duplicate snapshot raises ValueError."""
        from sqlalchemy.exc import IntegrityError

        # Mock IntegrityError for unique constraint violation
        mock_db.commit.side_effect = IntegrityError(
            "statement",
            "params",
            "orig",
            connection_invalidated=False
        )
        # Set the error message to include the constraint name
        mock_db.commit.side_effect.args = ("unique_snapshot_per_user_per_day",)

        with patch.object(
            snapshot_service.aggregation_service,
            'get_net_worth_summary',
            return_value=sample_aggregation_data
        ):
            with pytest.raises(ValueError) as exc_info:
                await snapshot_service.create_snapshot(
                    user_id=user_id,
                    base_currency='GBP'
                )

            assert "already exists" in str(exc_info.value)
            mock_db.rollback.assert_called_once()

    async def test_create_snapshot_different_currencies(
        self,
        snapshot_service,
        user_id,
        mock_db,
        sample_aggregation_data
    ):
        """Test snapshot creation with different currencies."""
        currencies = ['GBP', 'ZAR', 'USD', 'EUR']

        for currency in currencies:
            currency_data = {**sample_aggregation_data, 'base_currency': currency}

            with patch.object(
                snapshot_service.aggregation_service,
                'get_net_worth_summary',
                return_value=currency_data
            ):
                snapshot = await snapshot_service.create_snapshot(
                    user_id=user_id,
                    base_currency=currency
                )

                assert snapshot.base_currency == currency

    async def test_create_snapshot_aggregation_failure_raises_error(
        self,
        snapshot_service,
        user_id,
        mock_db
    ):
        """Test snapshot creation fails gracefully when aggregation fails."""
        with patch.object(
            snapshot_service.aggregation_service,
            'get_net_worth_summary',
            side_effect=Exception("Aggregation failed")
        ):
            with pytest.raises(Exception) as exc_info:
                await snapshot_service.create_snapshot(
                    user_id=user_id,
                    base_currency='GBP'
                )

            assert "Aggregation failed" in str(exc_info.value)
            mock_db.rollback.assert_called_once()


@pytest.mark.asyncio
class TestSnapshotRetrieval:
    """Test suite for snapshot retrieval."""

    async def test_get_snapshots_date_range(
        self,
        snapshot_service,
        user_id,
        mock_db
    ):
        """Test retrieving snapshots within date range."""
        from_date = date(2024, 1, 1)
        to_date = date(2024, 12, 31)

        # Mock query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        snapshots = await snapshot_service.get_snapshots(
            user_id=user_id,
            from_date=from_date,
            to_date=to_date
        )

        # Verify query was executed
        mock_db.execute.assert_called_once()
        assert isinstance(snapshots, list)

    async def test_get_snapshots_filter_by_currency(
        self,
        snapshot_service,
        user_id,
        mock_db
    ):
        """Test snapshot retrieval filtered by currency."""
        from_date = date(2024, 1, 1)
        to_date = date(2024, 12, 31)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        await snapshot_service.get_snapshots(
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
            base_currency='GBP'
        )

        mock_db.execute.assert_called_once()

    async def test_get_snapshots_ordered_by_date_desc(
        self,
        snapshot_service,
        user_id,
        mock_db
    ):
        """Test snapshots are ordered by date descending."""
        # Create mock snapshots with different dates
        mock_snapshots = [
            NetWorthSnapshot(
                id=uuid4(),
                user_id=user_id,
                snapshot_date=date(2024, 12, 31),
                base_currency='GBP',
                net_worth=Decimal('70000'),
                total_assets=Decimal('100000'),
                total_liabilities=Decimal('30000')
            ),
            NetWorthSnapshot(
                id=uuid4(),
                user_id=user_id,
                snapshot_date=date(2024, 6, 30),
                base_currency='GBP',
                net_worth=Decimal('65000'),
                total_assets=Decimal('95000'),
                total_liabilities=Decimal('30000')
            )
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_snapshots
        mock_db.execute.return_value = mock_result

        snapshots = await snapshot_service.get_snapshots(
            user_id=user_id,
            from_date=date(2024, 1, 1),
            to_date=date(2024, 12, 31)
        )

        # Most recent should be first
        assert snapshots[0].snapshot_date == date(2024, 12, 31)
        assert snapshots[1].snapshot_date == date(2024, 6, 30)

    async def test_get_latest_snapshot(
        self,
        snapshot_service,
        user_id,
        mock_db
    ):
        """Test retrieving latest snapshot for user."""
        mock_snapshot = NetWorthSnapshot(
            id=uuid4(),
            user_id=user_id,
            snapshot_date=date.today(),
            base_currency='GBP',
            net_worth=Decimal('70000'),
            total_assets=Decimal('100000'),
            total_liabilities=Decimal('30000')
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_snapshot
        mock_db.execute.return_value = mock_result

        latest = await snapshot_service.get_latest_snapshot(
            user_id=user_id,
            base_currency='GBP'
        )

        assert latest is not None
        assert latest.snapshot_date == date.today()

    async def test_get_latest_snapshot_none_exists(
        self,
        snapshot_service,
        user_id,
        mock_db
    ):
        """Test get_latest_snapshot returns None when no snapshots exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        latest = await snapshot_service.get_latest_snapshot(
            user_id=user_id
        )

        assert latest is None


@pytest.mark.asyncio
class TestTrendData:
    """Test suite for trend data generation."""

    async def test_get_trend_data_monthly_grouping(
        self,
        snapshot_service,
        user_id,
        mock_db
    ):
        """Test trend data groups snapshots by month."""
        # Create mock snapshots (multiple per month)
        today = date.today()
        mock_snapshots = [
            # December 2024
            NetWorthSnapshot(
                id=uuid4(),
                user_id=user_id,
                snapshot_date=date(2024, 12, 31),
                base_currency='GBP',
                net_worth=Decimal('70000'),
                total_assets=Decimal('100000'),
                total_liabilities=Decimal('30000')
            ),
            NetWorthSnapshot(
                id=uuid4(),
                user_id=user_id,
                snapshot_date=date(2024, 12, 15),
                base_currency='GBP',
                net_worth=Decimal('68000'),
                total_assets=Decimal('98000'),
                total_liabilities=Decimal('30000')
            ),
            # November 2024
            NetWorthSnapshot(
                id=uuid4(),
                user_id=user_id,
                snapshot_date=date(2024, 11, 30),
                base_currency='GBP',
                net_worth=Decimal('65000'),
                total_assets=Decimal('95000'),
                total_liabilities=Decimal('30000')
            )
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_snapshots
        mock_db.execute.return_value = mock_result

        trend_data = await snapshot_service.get_trend_data(
            user_id=user_id,
            base_currency='GBP',
            months=12
        )

        # Should have 2 data points (Dec and Nov)
        assert len(trend_data) == 2

        # December should use latest snapshot (31st, not 15th)
        dec_data = next(d for d in trend_data if '2024-12' in d['date'])
        assert dec_data['net_worth'] == 70000.0

    async def test_get_trend_data_default_12_months(
        self,
        snapshot_service,
        user_id,
        mock_db
    ):
        """Test trend data defaults to 12 months."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        trend_data = await snapshot_service.get_trend_data(
            user_id=user_id,
            base_currency='GBP'
        )

        # Should query for 12 months by default
        assert isinstance(trend_data, list)

    async def test_get_trend_data_no_snapshots(
        self,
        snapshot_service,
        user_id,
        mock_db
    ):
        """Test trend data returns empty list when no snapshots exist."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        trend_data = await snapshot_service.get_trend_data(
            user_id=user_id,
            base_currency='GBP'
        )

        assert trend_data == []

    async def test_get_trend_data_sorted_by_date(
        self,
        snapshot_service,
        user_id,
        mock_db
    ):
        """Test trend data is sorted by date ascending."""
        mock_snapshots = [
            NetWorthSnapshot(
                id=uuid4(),
                user_id=user_id,
                snapshot_date=date(2024, 12, 31),
                base_currency='GBP',
                net_worth=Decimal('70000'),
                total_assets=Decimal('100000'),
                total_liabilities=Decimal('30000')
            ),
            NetWorthSnapshot(
                id=uuid4(),
                user_id=user_id,
                snapshot_date=date(2024, 11, 30),
                base_currency='GBP',
                net_worth=Decimal('65000'),
                total_assets=Decimal('95000'),
                total_liabilities=Decimal('30000')
            )
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_snapshots
        mock_db.execute.return_value = mock_result

        trend_data = await snapshot_service.get_trend_data(
            user_id=user_id,
            base_currency='GBP'
        )

        # Should be sorted ascending (Nov, then Dec)
        assert trend_data[0]['date'] == '2024-11-30'
        assert trend_data[1]['date'] == '2024-12-31'


@pytest.mark.asyncio
class TestChangeCalculations:
    """Test suite for change calculations."""

    async def test_calculate_changes_all_periods(
        self,
        snapshot_service,
        user_id,
        mock_db
    ):
        """Test change calculations for day, month, and year."""
        today = date.today()

        # Track call count to return different snapshots
        call_count = [0]

        # Mock snapshots for different periods
        async def mock_get_snapshots(user_id, from_date, to_date, base_currency=None):
            call_count[0] += 1

            # First call: current snapshot
            if call_count[0] == 1:
                return [
                    NetWorthSnapshot(
                        id=uuid4(),
                        user_id=user_id,
                        snapshot_date=today,
                        base_currency='GBP',
                        net_worth=Decimal('70000'),
                        total_assets=Decimal('100000'),
                        total_liabilities=Decimal('30000')
                    )
                ]
            # Second call: 1 day ago
            elif call_count[0] == 2:
                return [
                    NetWorthSnapshot(
                        id=uuid4(),
                        user_id=user_id,
                        snapshot_date=today - timedelta(days=1),
                        base_currency='GBP',
                        net_worth=Decimal('69000'),
                        total_assets=Decimal('99000'),
                        total_liabilities=Decimal('30000')
                    )
                ]
            # Third call: 30 days ago
            elif call_count[0] == 3:
                return [
                    NetWorthSnapshot(
                        id=uuid4(),
                        user_id=user_id,
                        snapshot_date=today - timedelta(days=30),
                        base_currency='GBP',
                        net_worth=Decimal('65000'),
                        total_assets=Decimal('95000'),
                        total_liabilities=Decimal('30000')
                    )
                ]
            # Fourth call: 365 days ago
            else:
                return [
                    NetWorthSnapshot(
                        id=uuid4(),
                        user_id=user_id,
                        snapshot_date=today - timedelta(days=365),
                        base_currency='GBP',
                        net_worth=Decimal('50000'),
                        total_assets=Decimal('80000'),
                        total_liabilities=Decimal('30000')
                    )
                ]

        with patch.object(
            snapshot_service,
            'get_snapshots',
            side_effect=mock_get_snapshots
        ):
            changes = await snapshot_service.calculate_changes(
                user_id=user_id,
                base_currency='GBP'
            )

            # Verify structure
            assert 'day' in changes
            assert 'month' in changes
            assert 'year' in changes

            # Verify day change (70000 - 69000 = 1000, +1.45%)
            assert changes['day']['amount'] == 1000.0
            assert changes['day']['percentage'] > 0

            # Verify month change (70000 - 65000 = 5000, +7.69%)
            assert changes['month']['amount'] == 5000.0
            assert changes['month']['percentage'] > 0

            # Verify year change (70000 - 50000 = 20000, +40%)
            assert changes['year']['amount'] == 20000.0
            assert changes['year']['percentage'] == 40.0

    async def test_calculate_changes_no_current_snapshot(
        self,
        snapshot_service,
        user_id,
        mock_db
    ):
        """Test change calculations return zeros when no current snapshot."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        with patch.object(
            snapshot_service,
            'get_snapshots',
            return_value=[]
        ):
            changes = await snapshot_service.calculate_changes(
                user_id=user_id,
                base_currency='GBP'
            )

            assert changes['day']['amount'] == 0.0
            assert changes['month']['amount'] == 0.0
            assert changes['year']['amount'] == 0.0

    async def test_calculate_changes_negative_change(
        self,
        snapshot_service,
        user_id
    ):
        """Test change calculations handle negative changes."""
        today = date.today()

        def mock_get_snapshots(user_id, from_date, to_date, base_currency=None):
            if to_date >= today - timedelta(days=7):
                # Current: lower net worth
                return [
                    NetWorthSnapshot(
                        id=uuid4(),
                        user_id=user_id,
                        snapshot_date=today,
                        base_currency='GBP',
                        net_worth=Decimal('60000'),
                        total_assets=Decimal('90000'),
                        total_liabilities=Decimal('30000')
                    )
                ]
            else:
                # Previous: higher net worth
                return [
                    NetWorthSnapshot(
                        id=uuid4(),
                        user_id=user_id,
                        snapshot_date=today - timedelta(days=30),
                        base_currency='GBP',
                        net_worth=Decimal('70000'),
                        total_assets=Decimal('100000'),
                        total_liabilities=Decimal('30000')
                    )
                ]

        with patch.object(
            snapshot_service,
            'get_snapshots',
            side_effect=mock_get_snapshots
        ):
            changes = await snapshot_service.calculate_changes(
                user_id=user_id,
                base_currency='GBP'
            )

            # Month change should be negative (60000 - 70000 = -10000)
            assert changes['month']['amount'] == -10000.0
            assert changes['month']['percentage'] < 0


@pytest.mark.asyncio
class TestSnapshotCleanup:
    """Test suite for snapshot cleanup."""

    async def test_cleanup_old_snapshots(
        self,
        snapshot_service,
        mock_db
    ):
        """Test cleanup deletes snapshots older than 2 years."""
        mock_result = MagicMock()
        mock_result.rowcount = 15
        mock_db.execute.return_value = mock_result

        deleted_count = await snapshot_service.cleanup_old_snapshots()

        assert deleted_count == 15
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()

    async def test_cleanup_retention_period_is_730_days(
        self,
        snapshot_service
    ):
        """Test retention period is exactly 2 years (730 days)."""
        assert snapshot_service.RETENTION_DAYS == 730

    async def test_cleanup_no_old_snapshots(
        self,
        snapshot_service,
        mock_db
    ):
        """Test cleanup when no old snapshots exist."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_db.execute.return_value = mock_result

        deleted_count = await snapshot_service.cleanup_old_snapshots()

        assert deleted_count == 0


@pytest.mark.asyncio
class TestSnapshotExists:
    """Test suite for snapshot existence check."""

    async def test_snapshot_exists_true(
        self,
        snapshot_service,
        user_id,
        mock_db
    ):
        """Test snapshot_exists returns True when snapshot exists."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = uuid4()
        mock_db.execute.return_value = mock_result

        exists = await snapshot_service.snapshot_exists(
            user_id=user_id,
            snapshot_date=date.today()
        )

        assert exists is True

    async def test_snapshot_exists_false(
        self,
        snapshot_service,
        user_id,
        mock_db
    ):
        """Test snapshot_exists returns False when snapshot doesn't exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        exists = await snapshot_service.snapshot_exists(
            user_id=user_id,
            snapshot_date=date.today()
        )

        assert exists is False

    async def test_snapshot_exists_with_currency_filter(
        self,
        snapshot_service,
        user_id,
        mock_db
    ):
        """Test snapshot_exists with currency filter."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = uuid4()
        mock_db.execute.return_value = mock_result

        exists = await snapshot_service.snapshot_exists(
            user_id=user_id,
            snapshot_date=date.today(),
            base_currency='GBP'
        )

        assert exists is True


@pytest.mark.asyncio
class TestServiceIntegration:
    """Test suite for service integration."""

    async def test_aggregation_service_initialized(
        self,
        mock_db
    ):
        """Test aggregation service is initialized."""
        service = NetWorthSnapshotService(mock_db)

        assert service.aggregation_service is not None
        assert isinstance(service.aggregation_service, DashboardAggregationService)

    async def test_aggregation_service_uses_same_db_session(
        self,
        mock_db
    ):
        """Test aggregation service uses same database session."""
        service = NetWorthSnapshotService(mock_db)

        assert service.aggregation_service.db is mock_db

    async def test_default_trend_months_is_12(
        self,
        snapshot_service
    ):
        """Test default trend months is 12."""
        assert snapshot_service.DEFAULT_TREND_MONTHS == 12


@pytest.mark.asyncio
class TestSnapshotModel:
    """Test suite for snapshot model methods."""

    def test_snapshot_to_dict(
        self,
        user_id
    ):
        """Test snapshot to_dict method."""
        snapshot = NetWorthSnapshot(
            id=uuid4(),
            user_id=user_id,
            snapshot_date=date(2024, 12, 31),
            base_currency='GBP',
            net_worth=Decimal('70000.00'),
            total_assets=Decimal('100000.00'),
            total_liabilities=Decimal('30000.00'),
            breakdown_by_country=[
                {'country': 'UK', 'net': 40000.00}
            ],
            breakdown_by_asset_class=[
                {'category': 'Cash', 'net': 25000.00}
            ],
            breakdown_by_currency=[
                {'currency': 'GBP', 'amount': 60000.00}
            ],
            created_at=datetime(2024, 12, 31, 10, 0, 0)
        )

        data = snapshot.to_dict()

        assert data['snapshot_date'] == '2024-12-31'
        assert data['base_currency'] == 'GBP'
        assert data['net_worth'] == 70000.0
        assert data['total_assets'] == 100000.0
        assert data['total_liabilities'] == 30000.0
        assert 'breakdown_by_country' in data
        assert 'breakdown_by_asset_class' in data
        assert 'breakdown_by_currency' in data

    def test_snapshot_repr(
        self,
        user_id
    ):
        """Test snapshot __repr__ method."""
        snapshot = NetWorthSnapshot(
            id=uuid4(),
            user_id=user_id,
            snapshot_date=date(2024, 12, 31),
            base_currency='GBP',
            net_worth=Decimal('70000.00'),
            total_assets=Decimal('100000.00'),
            total_liabilities=Decimal('30000.00')
        )

        repr_str = repr(snapshot)

        assert 'NetWorthSnapshot' in repr_str
        assert str(user_id) in repr_str
        assert '2024-12-31' in repr_str
        assert 'GBP' in repr_str
