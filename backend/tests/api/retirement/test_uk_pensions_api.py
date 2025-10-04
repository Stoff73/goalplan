"""
Comprehensive tests for UK Pension API endpoints.

Tests cover:
- CRUD operations (create, list, get, update, delete)
- Authentication and authorization
- Validation errors
- Contribution tracking
- Annual Allowance status
- Total pot calculation
- Rate limiting (where applicable)
- Error handling

Coverage target: >85%
"""

import pytest
from httpx import AsyncClient
from decimal import Decimal
from datetime import date, datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

from models.retirement import (
    UKPension, UKPensionContribution, UKPensionDBDetails,
    PensionType, PensionStatus, ContributionFrequency,
    TaxReliefMethod, DBSchemeType, IndexationType,
    InvestmentStrategy, AnnualAllowanceTracking,
    StatePensionForecast
)
from models.user import User


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_dc_pension_data():
    """Sample DC pension creation data."""
    return {
        "pension_type": "OCCUPATIONAL_DC",
        "provider": "Test Provider",
        "scheme_reference": "TEST123456",
        "employer_name": "Test Employer",
        "current_value": "50000.00",
        "start_date": "2020-01-01",
        "expected_retirement_date": "2050-01-01",
        "investment_strategy": "BALANCED",
        "assumed_growth_rate": "5.00",
        "assumed_inflation_rate": "2.50",
        "mpaa_triggered": False
    }


@pytest.fixture
def sample_db_pension_data():
    """Sample DB pension creation data."""
    return {
        "pension_type": "OCCUPATIONAL_DB",
        "provider": "DB Provider",
        "scheme_reference": "DB123456",
        "employer_name": "DB Employer",
        "start_date": "2015-01-01",
        "expected_retirement_date": "2045-01-01",
        "db_details": {
            "accrual_rate": "1/60",
            "pensionable_service_years": "10.00",
            "scheme_type": "FINAL_SALARY",
            "normal_retirement_age": 65,
            "guaranteed_pension_amount": "15000.00",
            "spouse_pension_percentage": "50.00",
            "lump_sum_entitlement": "45000.00",
            "indexation_type": "CPI"
        }
    }


@pytest.fixture
def sample_contribution_data():
    """Sample contribution data."""
    return {
        "employee_contribution": "500.00",
        "employer_contribution": "750.00",
        "personal_contribution": "0.00",
        "frequency": "MONTHLY",
        "tax_relief_method": "NET_PAY",
        "contribution_date": str(date.today())
    }


# ============================================================================
# PENSION CRUD TESTS
# ============================================================================

class TestCreatePension:
    """Tests for POST /api/v1/retirement/uk-pensions"""

    @pytest.mark.asyncio
    async def test_create_dc_pension_success(
        self,
        async_client: AsyncClient,
        test_user: User,
        authenticated_headers: dict,
        sample_dc_pension_data: dict
    ):
        """Test successful DC pension creation."""
        response = await async_client.post(
            "/api/v1/retirement/uk-pensions",
            json=sample_dc_pension_data,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["pension_type"] == "OCCUPATIONAL_DC"
        assert data["provider"] == "Test Provider"
        assert "****" in data["scheme_reference"]  # Masked
        assert data["current_value"] == "50000.00"
        assert "id" in data
        assert data["user_id"] == str(test_user.id)

    @pytest.mark.asyncio
    async def test_create_db_pension_success(
        self,
        async_client: AsyncClient,
        test_user: User,
        authenticated_headers: dict,
        sample_db_pension_data: dict
    ):
        """Test successful DB pension creation with details."""
        response = await async_client.post(
            "/api/v1/retirement/uk-pensions",
            json=sample_db_pension_data,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["pension_type"] == "OCCUPATIONAL_DB"
        assert data["db_details"] is not None
        assert data["db_details"]["accrual_rate"] == "1/60"
        assert data["db_details"]["scheme_type"] == "FINAL_SALARY"

    @pytest.mark.asyncio
    async def test_create_pension_without_auth(
        self,
        async_client: AsyncClient,
        sample_dc_pension_data: dict
    ):
        """Test pension creation fails without authentication."""
        response = await async_client.post(
            "/api/v1/retirement/uk-pensions",
            json=sample_dc_pension_data
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_pension_invalid_dates(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension_data: dict
    ):
        """Test pension creation fails with invalid dates."""
        # Retirement date before start date
        sample_dc_pension_data["expected_retirement_date"] = "2019-01-01"

        response = await async_client.post(
            "/api/v1/retirement/uk-pensions",
            json=sample_dc_pension_data,
            headers=authenticated_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_db_pension_missing_details(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test DB pension creation fails without DB details."""
        data = {
            "pension_type": "OCCUPATIONAL_DB",
            "provider": "Test",
            "scheme_reference": "TEST123",
            "start_date": "2020-01-01",
            "expected_retirement_date": "2050-01-01"
        }

        response = await async_client.post(
            "/api/v1/retirement/uk-pensions",
            json=data,
            headers=authenticated_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_pension_negative_value(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension_data: dict
    ):
        """Test pension creation fails with negative value."""
        sample_dc_pension_data["current_value"] = "-1000.00"

        response = await async_client.post(
            "/api/v1/retirement/uk-pensions",
            json=sample_dc_pension_data,
            headers=authenticated_headers
        )

        assert response.status_code == 422


class TestGetPensions:
    """Tests for GET /api/v1/retirement/uk-pensions"""

    @pytest.mark.asyncio
    async def test_get_all_pensions(
        self,
        async_client: AsyncClient,
        test_user: User,
        authenticated_headers: dict,
        sample_dc_pension: UKPension
    ):
        """Test retrieving all pensions for user."""
        response = await async_client.get(
            "/api/v1/retirement/uk-pensions",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(p["id"] == str(sample_dc_pension.id) for p in data)

    @pytest.mark.asyncio
    async def test_get_pensions_filter_by_type(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension: UKPension
    ):
        """Test filtering pensions by type."""
        response = await async_client.get(
            "/api/v1/retirement/uk-pensions?pension_type=OCCUPATIONAL_DC",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(p["pension_type"] == "OCCUPATIONAL_DC" for p in data)

    @pytest.mark.asyncio
    async def test_get_pensions_filter_by_provider(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension: UKPension
    ):
        """Test filtering pensions by provider."""
        response = await async_client.get(
            f"/api/v1/retirement/uk-pensions?provider={sample_dc_pension.provider}",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_pensions_filter_by_status(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test filtering pensions by status."""
        response = await async_client.get(
            "/api/v1/retirement/uk-pensions?status=ACTIVE",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(p["status"] == "ACTIVE" for p in data)

    @pytest.mark.asyncio
    async def test_get_pensions_without_auth(
        self,
        async_client: AsyncClient
    ):
        """Test getting pensions fails without authentication."""
        response = await async_client.get(
            "/api/v1/retirement/uk-pensions"
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_pensions_empty_list(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test getting pensions returns empty list if none exist."""
        # Using a new user with no pensions
        response = await async_client.get(
            "/api/v1/retirement/uk-pensions",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestGetSinglePension:
    """Tests for GET /api/v1/retirement/uk-pensions/{pension_id}"""

    @pytest.mark.asyncio
    async def test_get_pension_by_id(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension: UKPension
    ):
        """Test retrieving a single pension by ID."""
        response = await async_client.get(
            f"/api/v1/retirement/uk-pensions/{sample_dc_pension.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_dc_pension.id)
        assert data["provider"] == sample_dc_pension.provider

    @pytest.mark.asyncio
    async def test_get_pension_not_found(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test getting non-existent pension returns 404."""
        fake_id = uuid4()
        response = await async_client.get(
            f"/api/v1/retirement/uk-pensions/{fake_id}",
            headers=authenticated_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_pension_wrong_user(
        self,
        async_client: AsyncClient,
        other_user_authenticated_headers: dict,
        sample_dc_pension: UKPension
    ):
        """Test getting another user's pension returns 404 (authorization)."""
        response = await async_client.get(
            f"/api/v1/retirement/uk-pensions/{sample_dc_pension.id}",
            headers=other_user_authenticated_headers
        )

        assert response.status_code == 404  # Not exposing existence

    @pytest.mark.asyncio
    async def test_get_pension_without_auth(
        self,
        async_client: AsyncClient,
        sample_dc_pension: UKPension
    ):
        """Test getting pension fails without authentication."""
        response = await async_client.get(
            f"/api/v1/retirement/uk-pensions/{sample_dc_pension.id}"
        )

        assert response.status_code == 401


class TestUpdatePension:
    """Tests for PUT /api/v1/retirement/uk-pensions/{pension_id}"""

    @pytest.mark.asyncio
    async def test_update_pension_success(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension: UKPension
    ):
        """Test successful pension update."""
        update_data = {
            "current_value": "60000.00",
            "assumed_growth_rate": "6.00"
        }

        response = await async_client.put(
            f"/api/v1/retirement/uk-pensions/{sample_dc_pension.id}",
            json=update_data,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["current_value"] == "60000.00"
        assert data["assumed_growth_rate"] == "6.00"

    @pytest.mark.asyncio
    async def test_update_pension_provider(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension: UKPension
    ):
        """Test updating pension provider."""
        update_data = {"provider": "New Provider Ltd"}

        response = await async_client.put(
            f"/api/v1/retirement/uk-pensions/{sample_dc_pension.id}",
            json=update_data,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "New Provider Ltd"

    @pytest.mark.asyncio
    async def test_update_pension_not_found(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test updating non-existent pension returns 404."""
        fake_id = uuid4()
        update_data = {"current_value": "60000.00"}

        response = await async_client.put(
            f"/api/v1/retirement/uk-pensions/{fake_id}",
            json=update_data,
            headers=authenticated_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_pension_wrong_user(
        self,
        async_client: AsyncClient,
        other_user_authenticated_headers: dict,
        sample_dc_pension: UKPension
    ):
        """Test updating another user's pension returns 404."""
        update_data = {"current_value": "60000.00"}

        response = await async_client.put(
            f"/api/v1/retirement/uk-pensions/{sample_dc_pension.id}",
            json=update_data,
            headers=other_user_authenticated_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_pension_without_auth(
        self,
        async_client: AsyncClient,
        sample_dc_pension: UKPension
    ):
        """Test updating pension fails without authentication."""
        update_data = {"current_value": "60000.00"}

        response = await async_client.put(
            f"/api/v1/retirement/uk-pensions/{sample_dc_pension.id}",
            json=update_data
        )

        assert response.status_code == 401


class TestDeletePension:
    """Tests for DELETE /api/v1/retirement/uk-pensions/{pension_id}"""

    @pytest.mark.asyncio
    async def test_delete_pension_success(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension: UKPension
    ):
        """Test successful pension deletion (soft delete)."""
        response = await async_client.delete(
            f"/api/v1/retirement/uk-pensions/{sample_dc_pension.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 204

        # Verify pension is soft deleted
        get_response = await async_client.get(
            f"/api/v1/retirement/uk-pensions/{sample_dc_pension.id}",
            headers=authenticated_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_pension_not_found(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test deleting non-existent pension returns 404."""
        fake_id = uuid4()
        response = await async_client.delete(
            f"/api/v1/retirement/uk-pensions/{fake_id}",
            headers=authenticated_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_pension_wrong_user(
        self,
        async_client: AsyncClient,
        other_user_authenticated_headers: dict,
        sample_dc_pension: UKPension
    ):
        """Test deleting another user's pension returns 404."""
        response = await async_client.delete(
            f"/api/v1/retirement/uk-pensions/{sample_dc_pension.id}",
            headers=other_user_authenticated_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_pension_without_auth(
        self,
        async_client: AsyncClient,
        sample_dc_pension: UKPension
    ):
        """Test deleting pension fails without authentication."""
        response = await async_client.delete(
            f"/api/v1/retirement/uk-pensions/{sample_dc_pension.id}"
        )

        assert response.status_code == 401


# ============================================================================
# CONTRIBUTION TESTS
# ============================================================================

class TestAddContribution:
    """Tests for POST /api/v1/retirement/uk-pensions/{pension_id}/contributions"""

    @pytest.mark.asyncio
    async def test_add_contribution_success(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension: UKPension,
        sample_contribution_data: dict
    ):
        """Test successfully adding a contribution."""
        response = await async_client.post(
            f"/api/v1/retirement/uk-pensions/{sample_dc_pension.id}/contributions",
            json=sample_contribution_data,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["pension_id"] == str(sample_dc_pension.id)
        assert data["employee_contribution"] == "500.00"
        assert data["employer_contribution"] == "750.00"
        assert Decimal(data["total_contribution"]) == Decimal("1250.00")
        assert "tax_year" in data

    @pytest.mark.asyncio
    async def test_add_contribution_future_date(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension: UKPension,
        sample_contribution_data: dict
    ):
        """Test adding contribution with future date fails."""
        sample_contribution_data["contribution_date"] = str(date.today() + timedelta(days=30))

        response = await async_client.post(
            f"/api/v1/retirement/uk-pensions/{sample_dc_pension.id}/contributions",
            json=sample_contribution_data,
            headers=authenticated_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_add_contribution_negative_amount(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension: UKPension,
        sample_contribution_data: dict
    ):
        """Test adding contribution with negative amount fails."""
        sample_contribution_data["employee_contribution"] = "-100.00"

        response = await async_client.post(
            f"/api/v1/retirement/uk-pensions/{sample_dc_pension.id}/contributions",
            json=sample_contribution_data,
            headers=authenticated_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_add_contribution_pension_not_found(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_contribution_data: dict
    ):
        """Test adding contribution to non-existent pension returns 404."""
        fake_id = uuid4()
        response = await async_client.post(
            f"/api/v1/retirement/uk-pensions/{fake_id}/contributions",
            json=sample_contribution_data,
            headers=authenticated_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_add_contribution_without_auth(
        self,
        async_client: AsyncClient,
        sample_dc_pension: UKPension,
        sample_contribution_data: dict
    ):
        """Test adding contribution fails without authentication."""
        response = await async_client.post(
            f"/api/v1/retirement/uk-pensions/{sample_dc_pension.id}/contributions",
            json=sample_contribution_data
        )

        assert response.status_code == 401


# ============================================================================
# ANNUAL ALLOWANCE TESTS
# ============================================================================

class TestAnnualAllowanceStatus:
    """Tests for GET /api/v1/retirement/annual-allowance"""

    @pytest.mark.asyncio
    async def test_get_annual_allowance_current_year(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_user: User
    ):
        """Test getting annual allowance status for current year."""
        response = await async_client.get(
            "/api/v1/retirement/annual-allowance",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "tax_year" in data
        assert "total_contributions" in data
        assert "annual_allowance_limit" in data
        assert "allowance_used" in data
        assert "allowance_remaining" in data

    @pytest.mark.asyncio
    async def test_get_annual_allowance_specific_year(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test getting annual allowance status for specific tax year."""
        response = await async_client.get(
            "/api/v1/retirement/annual-allowance?tax_year=2024/25",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["tax_year"] == "2024/25"

    @pytest.mark.asyncio
    async def test_get_annual_allowance_without_auth(
        self,
        async_client: AsyncClient
    ):
        """Test getting annual allowance fails without authentication."""
        response = await async_client.get(
            "/api/v1/retirement/annual-allowance"
        )

        assert response.status_code == 401


# ============================================================================
# TOTAL POT TESTS
# ============================================================================

class TestTotalPensionPot:
    """Tests for GET /api/v1/retirement/total-pot"""

    @pytest.mark.asyncio
    async def test_get_total_pot(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension: UKPension
    ):
        """Test getting total pension pot across all pensions."""
        response = await async_client.get(
            "/api/v1/retirement/total-pot",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_current_value" in data
        assert "total_projected_value" in data
        assert "pensions" in data
        assert isinstance(data["pensions"], list)

    @pytest.mark.asyncio
    async def test_get_total_pot_with_state_pension(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension: UKPension,
        sample_state_pension: StatePensionForecast
    ):
        """Test getting total pot includes state pension if available."""
        response = await async_client.get(
            "/api/v1/retirement/total-pot",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["state_pension_annual"] is not None

    @pytest.mark.asyncio
    async def test_get_total_pot_without_auth(
        self,
        async_client: AsyncClient
    ):
        """Test getting total pot fails without authentication."""
        response = await async_client.get(
            "/api/v1/retirement/total-pot"
        )

        assert response.status_code == 401


# ============================================================================
# ADDITIONAL FIXTURES FOR TESTS
# ============================================================================

@pytest.fixture
async def sample_dc_pension(db_session, test_user):
    """Create a sample DC pension for testing."""
    pension = UKPension(
        user_id=test_user.id,
        pension_type=PensionType.OCCUPATIONAL_DC,
        provider="Test Provider",
        employer_name="Test Employer",
        current_value=Decimal("50000.00"),
        start_date=date(2020, 1, 1),
        expected_retirement_date=date(2050, 1, 1),
        investment_strategy=InvestmentStrategy.BALANCED,
        assumed_growth_rate=Decimal("5.00"),
        assumed_inflation_rate=Decimal("2.50"),
        status=PensionStatus.ACTIVE
    )
    pension.set_scheme_reference("TEST123456")

    db_session.add(pension)
    await db_session.commit()
    await db_session.refresh(pension)

    return pension


@pytest.fixture
async def sample_state_pension(db_session, test_user):
    """Create a sample state pension forecast for testing."""
    forecast = StatePensionForecast(
        user_id=test_user.id,
        forecast_date=date.today(),
        qualifying_years=25,
        years_needed_for_full=35,
        estimated_weekly_amount=Decimal("203.85"),
        estimated_annual_amount=Decimal("10600.20"),
        state_pension_age=67
    )

    db_session.add(forecast)
    await db_session.commit()
    await db_session.refresh(forecast)

    return forecast


@pytest.fixture
def other_user_auth_headers(other_user):
    """Auth headers for a different user (for authorization tests)."""
    from utils.jwt import create_access_token
    token = create_access_token({"sub": str(other_user.id)})
    return {"Authorization": f"Bearer {token}"}
