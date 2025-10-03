"""
Tests for dashboard net worth API endpoint.

This module tests the complete dashboard net worth summary endpoint
including authentication, caching, breakdowns, trends, and changes.
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch

from main import app


@pytest.mark.asyncio
class TestNetWorthDashboardAPI:
    """Tests for GET /api/v1/dashboard/net-worth endpoint."""

    async def test_get_net_worth_summary_success(
        self, async_client: AsyncClient, authenticated_headers, db_session
    ):
        """Test successful retrieval of net worth summary."""
        # Mock the aggregation service to return sample data
        mock_summary = {
            'net_worth': 325000.00,
            'total_assets': 425000.00,
            'total_liabilities': 100000.00,
            'base_currency': 'GBP',
            'as_of_date': date.today().isoformat(),
            'last_updated': datetime.utcnow().isoformat(),
            'breakdown_by_country': [
                {'category': 'UK', 'assets': 250000.00, 'liabilities': 0.00, 'net': 250000.00, 'percentage': 76.9},
                {'category': 'SA', 'assets': 75000.00, 'liabilities': 0.00, 'net': 75000.00, 'percentage': 23.1}
            ],
            'breakdown_by_asset_class': [
                {'category': 'Cash', 'assets': 50000.00, 'liabilities': 0.00, 'net': 50000.00, 'percentage': 15.4},
                {'category': 'Property', 'assets': 300000.00, 'liabilities': 0.00, 'net': 300000.00, 'percentage': 92.3}
            ],
            'breakdown_by_currency': [
                {'currency': 'GBP', 'amount': 250000.00, 'percentage': 76.9},
                {'currency': 'ZAR', 'amount': 75000.00, 'percentage': 23.1}
            ]
        }

        mock_trend = [
            {'date': '2024-11-01', 'net_worth': 300000.00},
            {'date': '2024-12-01', 'net_worth': 310000.00},
            {'date': '2025-01-01', 'net_worth': 320000.00}
        ]

        mock_changes = {
            'day': {'amount': 1000.00, 'percentage': 0.31},
            'month': {'amount': 5000.00, 'percentage': 1.56},
            'year': {'amount': 25000.00, 'percentage': 8.33}
        }

        # Patch the services
        with patch('api.v1.dashboard.net_worth.DashboardAggregationService') as MockAggService, \
             patch('api.v1.dashboard.net_worth.NetWorthSnapshotService') as MockSnapshotService:

            # Setup mocks
            mock_agg_instance = AsyncMock()
            mock_agg_instance.get_net_worth_summary.return_value = mock_summary
            MockAggService.return_value = mock_agg_instance

            mock_snapshot_instance = AsyncMock()
            mock_snapshot_instance.get_trend_data.return_value = mock_trend
            mock_snapshot_instance.calculate_changes.return_value = mock_changes
            MockSnapshotService.return_value = mock_snapshot_instance

            response = await async_client.get(
                "/api/v1/dashboard/net-worth",
                headers=authenticated_headers
            )

        assert response.status_code == 200
        result = response.json()

        # Verify response structure
        assert 'netWorth' in result
        assert 'totalAssets' in result
        assert 'totalLiabilities' in result
        assert 'baseCurrency' in result
        assert 'asOfDate' in result
        assert 'lastUpdated' in result
        assert 'breakdownByCountry' in result
        assert 'breakdownByAssetClass' in result
        assert 'breakdownByCurrency' in result
        assert 'trendData' in result
        assert 'changes' in result

        # Verify values (Decimal fields are serialized as strings in JSON)
        assert float(result['netWorth']) == 325000.00
        assert float(result['totalAssets']) == 425000.00
        assert float(result['totalLiabilities']) == 100000.00
        assert result['baseCurrency'] == 'GBP'

        # Verify breakdowns
        assert len(result['breakdownByCountry']) == 2
        assert result['breakdownByCountry'][0]['country'] == 'UK'
        assert float(result['breakdownByCountry'][0]['amount']) == 250000.00
        assert result['breakdownByCountry'][0]['percentage'] == 76.9

        # Verify trend data
        assert len(result['trendData']) == 3
        assert result['trendData'][0]['date'] == '2024-11-01'
        assert float(result['trendData'][0]['netWorth']) == 300000.00

        # Verify changes
        assert float(result['changes']['day']['amount']) == 1000.00
        assert float(result['changes']['month']['amount']) == 5000.00
        assert float(result['changes']['year']['amount']) == 25000.00

    async def test_authentication_required(self, async_client: AsyncClient):
        """Test that authentication is required."""
        response = await async_client.get("/api/v1/dashboard/net-worth")

        assert response.status_code == 401
        result = response.json()
        assert 'detail' in result

    async def test_base_currency_parameter(
        self, async_client: AsyncClient, authenticated_headers, db_session
    ):
        """Test base currency query parameter."""
        mock_summary = {
            'net_worth': 7687500.00,
            'total_assets': 10062500.00,
            'total_liabilities': 2375000.00,
            'base_currency': 'ZAR',
            'as_of_date': date.today().isoformat(),
            'last_updated': datetime.utcnow().isoformat(),
            'breakdown_by_country': [],
            'breakdown_by_asset_class': [],
            'breakdown_by_currency': []
        }

        with patch('api.v1.dashboard.net_worth.DashboardAggregationService') as MockAggService, \
             patch('api.v1.dashboard.net_worth.NetWorthSnapshotService') as MockSnapshotService:

            mock_agg_instance = AsyncMock()
            mock_agg_instance.get_net_worth_summary.return_value = mock_summary
            MockAggService.return_value = mock_agg_instance

            mock_snapshot_instance = AsyncMock()
            mock_snapshot_instance.get_trend_data.return_value = []
            mock_snapshot_instance.calculate_changes.return_value = {
                'day': {'amount': 0.0, 'percentage': 0.0},
                'month': {'amount': 0.0, 'percentage': 0.0},
                'year': {'amount': 0.0, 'percentage': 0.0}
            }
            MockSnapshotService.return_value = mock_snapshot_instance

            response = await async_client.get(
                "/api/v1/dashboard/net-worth?baseCurrency=ZAR",
                headers=authenticated_headers
            )

        assert response.status_code == 200
        result = response.json()
        assert result['baseCurrency'] == 'ZAR'
        assert float(result['netWorth']) == 7687500.00

    async def test_invalid_currency(
        self, async_client: AsyncClient, authenticated_headers
    ):
        """Test invalid currency parameter."""
        response = await async_client.get(
            "/api/v1/dashboard/net-worth?baseCurrency=JPY",
            headers=authenticated_headers
        )

        assert response.status_code == 400
        result = response.json()
        assert 'Invalid currency' in result['detail']

    async def test_as_of_date_parameter(
        self, async_client: AsyncClient, authenticated_headers, db_session
    ):
        """Test asOfDate query parameter for historical data."""
        historical_date = date(2024, 12, 31)

        mock_summary = {
            'net_worth': 300000.00,
            'total_assets': 400000.00,
            'total_liabilities': 100000.00,
            'base_currency': 'GBP',
            'as_of_date': historical_date.isoformat(),
            'last_updated': datetime.utcnow().isoformat(),
            'breakdown_by_country': [],
            'breakdown_by_asset_class': [],
            'breakdown_by_currency': []
        }

        with patch('api.v1.dashboard.net_worth.DashboardAggregationService') as MockAggService, \
             patch('api.v1.dashboard.net_worth.NetWorthSnapshotService') as MockSnapshotService:

            mock_agg_instance = AsyncMock()
            mock_agg_instance.get_net_worth_summary.return_value = mock_summary
            MockAggService.return_value = mock_agg_instance

            mock_snapshot_instance = AsyncMock()
            mock_snapshot_instance.get_trend_data.return_value = []
            mock_snapshot_instance.calculate_changes.return_value = {
                'day': {'amount': 0.0, 'percentage': 0.0},
                'month': {'amount': 0.0, 'percentage': 0.0},
                'year': {'amount': 0.0, 'percentage': 0.0}
            }
            MockSnapshotService.return_value = mock_snapshot_instance

            response = await async_client.get(
                f"/api/v1/dashboard/net-worth?asOfDate={historical_date.isoformat()}",
                headers=authenticated_headers
            )

        assert response.status_code == 200
        result = response.json()
        assert result['asOfDate'] == historical_date.isoformat()
        assert float(result['netWorth']) == 300000.00

    async def test_empty_data(
        self, async_client: AsyncClient, authenticated_headers, db_session
    ):
        """Test response when user has no data."""
        mock_summary = {
            'net_worth': 0.00,
            'total_assets': 0.00,
            'total_liabilities': 0.00,
            'base_currency': 'GBP',
            'as_of_date': date.today().isoformat(),
            'last_updated': datetime.utcnow().isoformat(),
            'breakdown_by_country': [],
            'breakdown_by_asset_class': [],
            'breakdown_by_currency': []
        }

        with patch('api.v1.dashboard.net_worth.DashboardAggregationService') as MockAggService, \
             patch('api.v1.dashboard.net_worth.NetWorthSnapshotService') as MockSnapshotService:

            mock_agg_instance = AsyncMock()
            mock_agg_instance.get_net_worth_summary.return_value = mock_summary
            MockAggService.return_value = mock_agg_instance

            mock_snapshot_instance = AsyncMock()
            mock_snapshot_instance.get_trend_data.return_value = []
            mock_snapshot_instance.calculate_changes.return_value = {
                'day': {'amount': 0.0, 'percentage': 0.0},
                'month': {'amount': 0.0, 'percentage': 0.0},
                'year': {'amount': 0.0, 'percentage': 0.0}
            }
            MockSnapshotService.return_value = mock_snapshot_instance

            response = await async_client.get(
                "/api/v1/dashboard/net-worth",
                headers=authenticated_headers
            )

        assert response.status_code == 200
        result = response.json()
        assert float(result['netWorth']) == 0.00
        assert float(result['totalAssets']) == 0.00
        assert float(result['totalLiabilities']) == 0.00
        assert len(result['breakdownByCountry']) == 0
        assert len(result['breakdownByAssetClass']) == 0
        assert len(result['breakdownByCurrency']) == 0
        assert len(result['trendData']) == 0

    async def test_negative_net_worth(
        self, async_client: AsyncClient, authenticated_headers, db_session
    ):
        """Test response with negative net worth (liabilities > assets)."""
        mock_summary = {
            'net_worth': -50000.00,
            'total_assets': 50000.00,
            'total_liabilities': 100000.00,
            'base_currency': 'GBP',
            'as_of_date': date.today().isoformat(),
            'last_updated': datetime.utcnow().isoformat(),
            'breakdown_by_country': [],
            'breakdown_by_asset_class': [],
            'breakdown_by_currency': []
        }

        with patch('api.v1.dashboard.net_worth.DashboardAggregationService') as MockAggService, \
             patch('api.v1.dashboard.net_worth.NetWorthSnapshotService') as MockSnapshotService:

            mock_agg_instance = AsyncMock()
            mock_agg_instance.get_net_worth_summary.return_value = mock_summary
            MockAggService.return_value = mock_agg_instance

            mock_snapshot_instance = AsyncMock()
            mock_snapshot_instance.get_trend_data.return_value = []
            mock_snapshot_instance.calculate_changes.return_value = {
                'day': {'amount': 0.0, 'percentage': 0.0},
                'month': {'amount': 0.0, 'percentage': 0.0},
                'year': {'amount': 0.0, 'percentage': 0.0}
            }
            MockSnapshotService.return_value = mock_snapshot_instance

            response = await async_client.get(
                "/api/v1/dashboard/net-worth",
                headers=authenticated_headers
            )

        assert response.status_code == 200
        result = response.json()
        assert float(result['netWorth']) == -50000.00
        assert float(result['totalAssets']) == 50000.00
        assert float(result['totalLiabilities']) == 100000.00

    async def test_all_breakdown_types_present(
        self, async_client: AsyncClient, authenticated_headers, db_session
    ):
        """Test that all breakdown types are included in response."""
        mock_summary = {
            'net_worth': 500000.00,
            'total_assets': 600000.00,
            'total_liabilities': 100000.00,
            'base_currency': 'GBP',
            'as_of_date': date.today().isoformat(),
            'last_updated': datetime.utcnow().isoformat(),
            'breakdown_by_country': [
                {'category': 'UK', 'assets': 400000.00, 'liabilities': 50000.00, 'net': 350000.00, 'percentage': 70.0},
                {'category': 'SA', 'assets': 200000.00, 'liabilities': 50000.00, 'net': 150000.00, 'percentage': 30.0}
            ],
            'breakdown_by_asset_class': [
                {'category': 'Cash', 'assets': 100000.00, 'liabilities': 0.00, 'net': 100000.00, 'percentage': 20.0},
                {'category': 'Property', 'assets': 400000.00, 'liabilities': 0.00, 'net': 400000.00, 'percentage': 80.0},
                {'category': 'Pensions', 'assets': 100000.00, 'liabilities': 0.00, 'net': 100000.00, 'percentage': 20.0}
            ],
            'breakdown_by_currency': [
                {'currency': 'GBP', 'amount': 400000.00, 'percentage': 66.7},
                {'currency': 'ZAR', 'amount': 200000.00, 'percentage': 33.3}
            ]
        }

        with patch('api.v1.dashboard.net_worth.DashboardAggregationService') as MockAggService, \
             patch('api.v1.dashboard.net_worth.NetWorthSnapshotService') as MockSnapshotService:

            mock_agg_instance = AsyncMock()
            mock_agg_instance.get_net_worth_summary.return_value = mock_summary
            MockAggService.return_value = mock_agg_instance

            mock_snapshot_instance = AsyncMock()
            mock_snapshot_instance.get_trend_data.return_value = []
            mock_snapshot_instance.calculate_changes.return_value = {
                'day': {'amount': 0.0, 'percentage': 0.0},
                'month': {'amount': 0.0, 'percentage': 0.0},
                'year': {'amount': 0.0, 'percentage': 0.0}
            }
            MockSnapshotService.return_value = mock_snapshot_instance

            response = await async_client.get(
                "/api/v1/dashboard/net-worth",
                headers=authenticated_headers
            )

        assert response.status_code == 200
        result = response.json()

        # Verify all breakdown types present
        assert 'breakdownByCountry' in result
        assert len(result['breakdownByCountry']) == 2

        assert 'breakdownByAssetClass' in result
        assert len(result['breakdownByAssetClass']) == 3

        assert 'breakdownByCurrency' in result
        assert len(result['breakdownByCurrency']) == 2

    async def test_trend_data_12_months(
        self, async_client: AsyncClient, authenticated_headers, db_session
    ):
        """Test that trend data includes up to 12 months."""
        # Generate 12 months of trend data
        mock_trend = []
        for i in range(12):
            month_date = date.today() - timedelta(days=(11-i) * 30)
            mock_trend.append({
                'date': month_date.isoformat(),
                'net_worth': 300000.00 + (i * 1000)
            })

        mock_summary = {
            'net_worth': 325000.00,
            'total_assets': 425000.00,
            'total_liabilities': 100000.00,
            'base_currency': 'GBP',
            'as_of_date': date.today().isoformat(),
            'last_updated': datetime.utcnow().isoformat(),
            'breakdown_by_country': [],
            'breakdown_by_asset_class': [],
            'breakdown_by_currency': []
        }

        with patch('api.v1.dashboard.net_worth.DashboardAggregationService') as MockAggService, \
             patch('api.v1.dashboard.net_worth.NetWorthSnapshotService') as MockSnapshotService:

            mock_agg_instance = AsyncMock()
            mock_agg_instance.get_net_worth_summary.return_value = mock_summary
            MockAggService.return_value = mock_agg_instance

            mock_snapshot_instance = AsyncMock()
            mock_snapshot_instance.get_trend_data.return_value = mock_trend
            mock_snapshot_instance.calculate_changes.return_value = {
                'day': {'amount': 0.0, 'percentage': 0.0},
                'month': {'amount': 0.0, 'percentage': 0.0},
                'year': {'amount': 0.0, 'percentage': 0.0}
            }
            MockSnapshotService.return_value = mock_snapshot_instance

            response = await async_client.get(
                "/api/v1/dashboard/net-worth",
                headers=authenticated_headers
            )

        assert response.status_code == 200
        result = response.json()

        assert 'trendData' in result
        assert len(result['trendData']) == 12
        assert all('date' in point and 'netWorth' in point for point in result['trendData'])

    async def test_change_calculations(
        self, async_client: AsyncClient, authenticated_headers, db_session
    ):
        """Test that all change periods (day, month, year) are included."""
        mock_summary = {
            'net_worth': 325000.00,
            'total_assets': 425000.00,
            'total_liabilities': 100000.00,
            'base_currency': 'GBP',
            'as_of_date': date.today().isoformat(),
            'last_updated': datetime.utcnow().isoformat(),
            'breakdown_by_country': [],
            'breakdown_by_asset_class': [],
            'breakdown_by_currency': []
        }

        mock_changes = {
            'day': {'amount': 1000.00, 'percentage': 0.31},
            'month': {'amount': 5000.00, 'percentage': 1.56},
            'year': {'amount': 25000.00, 'percentage': 8.33}
        }

        with patch('api.v1.dashboard.net_worth.DashboardAggregationService') as MockAggService, \
             patch('api.v1.dashboard.net_worth.NetWorthSnapshotService') as MockSnapshotService:

            mock_agg_instance = AsyncMock()
            mock_agg_instance.get_net_worth_summary.return_value = mock_summary
            MockAggService.return_value = mock_agg_instance

            mock_snapshot_instance = AsyncMock()
            mock_snapshot_instance.get_trend_data.return_value = []
            mock_snapshot_instance.calculate_changes.return_value = mock_changes
            MockSnapshotService.return_value = mock_snapshot_instance

            response = await async_client.get(
                "/api/v1/dashboard/net-worth",
                headers=authenticated_headers
            )

        assert response.status_code == 200
        result = response.json()

        assert 'changes' in result
        assert 'day' in result['changes']
        assert 'month' in result['changes']
        assert 'year' in result['changes']

        assert float(result['changes']['day']['amount']) == 1000.00
        assert result['changes']['day']['percentage'] == 0.31
        assert float(result['changes']['month']['amount']) == 5000.00
        assert float(result['changes']['year']['amount']) == 25000.00

    async def test_error_handling(
        self, async_client: AsyncClient, authenticated_headers, db_session
    ):
        """Test error handling when service fails."""
        with patch('api.v1.dashboard.net_worth.DashboardAggregationService') as MockAggService:
            mock_agg_instance = AsyncMock()
            mock_agg_instance.get_net_worth_summary.side_effect = Exception("Database error")
            MockAggService.return_value = mock_agg_instance

            response = await async_client.get(
                "/api/v1/dashboard/net-worth",
                headers=authenticated_headers
            )

        assert response.status_code == 500
        result = response.json()
        assert 'detail' in result
        assert 'Failed to retrieve net worth summary' in result['detail']

    async def test_response_format_matches_specification(
        self, async_client: AsyncClient, authenticated_headers, db_session
    ):
        """Test that response format exactly matches the specification."""
        mock_summary = {
            'net_worth': 325000.00,
            'total_assets': 425000.00,
            'total_liabilities': 100000.00,
            'base_currency': 'GBP',
            'as_of_date': date.today().isoformat(),
            'last_updated': datetime.utcnow().isoformat(),
            'breakdown_by_country': [
                {'category': 'UK', 'assets': 250000.00, 'liabilities': 0.00, 'net': 250000.00, 'percentage': 76.9}
            ],
            'breakdown_by_asset_class': [
                {'category': 'Cash', 'assets': 50000.00, 'liabilities': 0.00, 'net': 50000.00, 'percentage': 15.4}
            ],
            'breakdown_by_currency': [
                {'currency': 'GBP', 'amount': 250000.00, 'percentage': 76.9}
            ]
        }

        mock_trend = [{'date': '2024-11-01', 'net_worth': 300000.00}]
        mock_changes = {
            'day': {'amount': 1000.00, 'percentage': 0.31},
            'month': {'amount': 5000.00, 'percentage': 1.56},
            'year': {'amount': 25000.00, 'percentage': 8.33}
        }

        with patch('api.v1.dashboard.net_worth.DashboardAggregationService') as MockAggService, \
             patch('api.v1.dashboard.net_worth.NetWorthSnapshotService') as MockSnapshotService:

            mock_agg_instance = AsyncMock()
            mock_agg_instance.get_net_worth_summary.return_value = mock_summary
            MockAggService.return_value = mock_agg_instance

            mock_snapshot_instance = AsyncMock()
            mock_snapshot_instance.get_trend_data.return_value = mock_trend
            mock_snapshot_instance.calculate_changes.return_value = mock_changes
            MockSnapshotService.return_value = mock_snapshot_instance

            response = await async_client.get(
                "/api/v1/dashboard/net-worth",
                headers=authenticated_headers
            )

        assert response.status_code == 200
        result = response.json()

        # Verify exact field names match specification
        expected_fields = {
            'netWorth', 'totalAssets', 'totalLiabilities', 'baseCurrency',
            'asOfDate', 'lastUpdated', 'breakdownByCountry', 'breakdownByAssetClass',
            'breakdownByCurrency', 'trendData', 'changes'
        }
        assert set(result.keys()) == expected_fields

        # Verify breakdown field names
        assert 'country' in result['breakdownByCountry'][0]
        assert 'amount' in result['breakdownByCountry'][0]
        assert 'percentage' in result['breakdownByCountry'][0]

        assert 'assetClass' in result['breakdownByAssetClass'][0]
        assert 'amount' in result['breakdownByAssetClass'][0]
        assert 'percentage' in result['breakdownByAssetClass'][0]

        assert 'currency' in result['breakdownByCurrency'][0]
        assert 'amount' in result['breakdownByCurrency'][0]
        assert 'percentage' in result['breakdownByCurrency'][0]

        # Verify trend data structure
        assert 'date' in result['trendData'][0]
        assert 'netWorth' in result['trendData'][0]

        # Verify changes structure
        assert 'day' in result['changes']
        assert 'month' in result['changes']
        assert 'year' in result['changes']
        assert 'amount' in result['changes']['day']
        assert 'percentage' in result['changes']['day']
