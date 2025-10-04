"""
Comprehensive tests for Retirement Projection API endpoints.

Tests cover:
- Retirement projection creation
- Income breakdown calculations
- Drawdown scenario modeling
- Annuity quote calculations
- Authentication and authorization
- Validation errors
- Error handling

Coverage target: >85%
"""

import pytest
from httpx import AsyncClient
from decimal import Decimal
from datetime import date
from uuid import uuid4

from models.retirement import (
    UKPension, RetirementProjection, DrawdownScenario,
    PensionType, PensionStatus, InvestmentStrategy
)
from models.user import User


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_projection_data():
    """Sample projection creation data."""
    return {
        "target_retirement_age": 65,
        "annual_income_needed": "40000.00",
        "inflation_rate": "2.50"
    }


@pytest.fixture
def sample_drawdown_scenario_data(sample_dc_pension):
    """Sample drawdown scenario data."""
    return {
        "pension_id": str(sample_dc_pension.id),
        "scenario_name": "Conservative Drawdown",
        "drawdown_rate": "4.00",
        "start_age": 65
    }


@pytest.fixture
def sample_annuity_quote_data(sample_dc_pension):
    """Sample annuity quote request data."""
    return {
        "pension_id": str(sample_dc_pension.id),
        "annuity_rate": "6.00",
        "spouse_provision": False
    }


# ============================================================================
# PROJECTION CREATION TESTS
# ============================================================================

class TestCreateRetirementProjection:
    """Tests for POST /api/v1/retirement/projections"""

    @pytest.mark.asyncio
    async def test_create_projection_success(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_user: User,
        sample_projection_data: dict,
        sample_dc_pension: UKPension
    ):
        """Test successfully creating a retirement projection."""
        response = await async_client.post(
            "/api/v1/retirement/projections",
            json=sample_projection_data,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == str(test_user.id)
        assert data["target_retirement_age"] == 65
        assert data["annual_income_needed"] == "40000.00"
        assert "income_breakdown" in data
        assert "income_gap" in data
        assert "on_track" in data
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_projection_with_growth_assumptions(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_projection_data: dict
    ):
        """Test creating projection with custom growth assumptions."""
        sample_projection_data["growth_assumptions"] = {
            "equity": "7.00",
            "bonds": "3.00",
            "cash": "1.00"
        }

        response = await async_client.post(
            "/api/v1/retirement/projections",
            json=sample_projection_data,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["growth_assumptions"] is not None

    @pytest.mark.asyncio
    async def test_create_projection_invalid_retirement_age(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_projection_data: dict
    ):
        """Test projection creation fails with invalid retirement age."""
        sample_projection_data["target_retirement_age"] = 50  # Below minimum

        response = await async_client.post(
            "/api/v1/retirement/projections",
            json=sample_projection_data,
            headers=authenticated_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_projection_zero_income(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_projection_data: dict
    ):
        """Test projection creation fails with zero income needed."""
        sample_projection_data["annual_income_needed"] = "0.00"

        response = await async_client.post(
            "/api/v1/retirement/projections",
            json=sample_projection_data,
            headers=authenticated_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_projection_without_auth(
        self,
        async_client: AsyncClient,
        sample_projection_data: dict
    ):
        """Test projection creation fails without authentication."""
        response = await async_client.post(
            "/api/v1/retirement/projections",
            json=sample_projection_data
        )

        assert response.status_code == 401


# ============================================================================
# INCOME PROJECTION TESTS
# ============================================================================

class TestGetIncomeProjection:
    """Tests for GET /api/v1/retirement/income-projection"""

    @pytest.mark.asyncio
    async def test_get_income_projection_default_age(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension: UKPension
    ):
        """Test getting income projection with default retirement age."""
        response = await async_client.get(
            "/api/v1/retirement/income-projection",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "state_pension_income" in data
        assert "db_pension_income" in data
        assert "dc_drawdown_income" in data
        assert "other_income" in data
        assert "total_income" in data

    @pytest.mark.asyncio
    async def test_get_income_projection_custom_age(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension: UKPension
    ):
        """Test getting income projection with custom retirement age."""
        response = await async_client.get(
            "/api/v1/retirement/income-projection?retirement_age=67",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data

    @pytest.mark.asyncio
    async def test_get_income_projection_invalid_age(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test getting income projection with invalid age fails."""
        response = await async_client.get(
            "/api/v1/retirement/income-projection?retirement_age=50",
            headers=authenticated_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_income_projection_without_auth(
        self,
        async_client: AsyncClient
    ):
        """Test getting income projection fails without authentication."""
        response = await async_client.get(
            "/api/v1/retirement/income-projection"
        )

        assert response.status_code == 401


# ============================================================================
# DRAWDOWN SCENARIO TESTS
# ============================================================================

class TestCreateDrawdownScenario:
    """Tests for POST /api/v1/retirement/drawdown-scenario"""

    @pytest.mark.asyncio
    async def test_create_drawdown_scenario_success(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_drawdown_scenario_data: dict,
        sample_dc_pension: UKPension
    ):
        """Test successfully creating a drawdown scenario."""
        response = await async_client.post(
            "/api/v1/retirement/drawdown-scenario",
            json=sample_drawdown_scenario_data,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["pension_id"] == str(sample_dc_pension.id)
        assert data["scenario_name"] == "Conservative Drawdown"
        assert data["drawdown_rate"] == "4.00"
        assert data["start_age"] == 65
        assert "projected_annual_income" in data
        assert "pot_depletion_age" in data
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_drawdown_scenario_aggressive_rate(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_drawdown_scenario_data: dict
    ):
        """Test creating drawdown scenario with higher rate."""
        sample_drawdown_scenario_data["scenario_name"] = "Aggressive Drawdown"
        sample_drawdown_scenario_data["drawdown_rate"] = "7.00"

        response = await async_client.post(
            "/api/v1/retirement/drawdown-scenario",
            json=sample_drawdown_scenario_data,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["drawdown_rate"] == "7.00"

    @pytest.mark.asyncio
    async def test_create_drawdown_scenario_invalid_rate(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_drawdown_scenario_data: dict
    ):
        """Test creating drawdown scenario with invalid rate fails."""
        sample_drawdown_scenario_data["drawdown_rate"] = "10.00"  # Too high

        response = await async_client.post(
            "/api/v1/retirement/drawdown-scenario",
            json=sample_drawdown_scenario_data,
            headers=authenticated_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_drawdown_scenario_invalid_age(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_drawdown_scenario_data: dict
    ):
        """Test creating drawdown scenario with invalid age fails."""
        sample_drawdown_scenario_data["start_age"] = 50  # Below minimum

        response = await async_client.post(
            "/api/v1/retirement/drawdown-scenario",
            json=sample_drawdown_scenario_data,
            headers=authenticated_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_drawdown_scenario_pension_not_found(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_drawdown_scenario_data: dict
    ):
        """Test creating drawdown scenario for non-existent pension fails."""
        sample_drawdown_scenario_data["pension_id"] = str(uuid4())

        response = await async_client.post(
            "/api/v1/retirement/drawdown-scenario",
            json=sample_drawdown_scenario_data,
            headers=authenticated_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_drawdown_scenario_wrong_user(
        self,
        async_client: AsyncClient,
        other_user_authenticated_headers: dict,
        sample_drawdown_scenario_data: dict
    ):
        """Test creating drawdown scenario for another user's pension fails."""
        response = await async_client.post(
            "/api/v1/retirement/drawdown-scenario",
            json=sample_drawdown_scenario_data,
            headers=other_user_authenticated_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_drawdown_scenario_without_auth(
        self,
        async_client: AsyncClient,
        sample_drawdown_scenario_data: dict
    ):
        """Test creating drawdown scenario fails without authentication."""
        response = await async_client.post(
            "/api/v1/retirement/drawdown-scenario",
            json=sample_drawdown_scenario_data
        )

        assert response.status_code == 401


# ============================================================================
# ANNUITY QUOTE TESTS
# ============================================================================

class TestCalculateAnnuityQuote:
    """Tests for POST /api/v1/retirement/annuity-quote"""

    @pytest.mark.asyncio
    async def test_calculate_annuity_quote_success(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_annuity_quote_data: dict,
        sample_dc_pension: UKPension
    ):
        """Test successfully calculating annuity quote."""
        response = await async_client.post(
            "/api/v1/retirement/annuity-quote",
            json=sample_annuity_quote_data,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["pension_id"] == str(sample_dc_pension.id)
        assert data["annuity_rate"] == "6.00"
        assert "pot_value" in data
        assert "annual_income" in data
        assert "monthly_income" in data
        assert data["spouse_provision"] == False

    @pytest.mark.asyncio
    async def test_calculate_annuity_quote_with_spouse(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_annuity_quote_data: dict
    ):
        """Test calculating annuity quote with spouse provision."""
        sample_annuity_quote_data["spouse_provision"] = True

        response = await async_client.post(
            "/api/v1/retirement/annuity-quote",
            json=sample_annuity_quote_data,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["spouse_provision"] == True

    @pytest.mark.asyncio
    async def test_calculate_annuity_quote_with_escalation(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_annuity_quote_data: dict
    ):
        """Test calculating annuity quote with escalation."""
        sample_annuity_quote_data["escalation_rate"] = "3.00"

        response = await async_client.post(
            "/api/v1/retirement/annuity-quote",
            json=sample_annuity_quote_data,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["escalation_rate"] == "3.00"

    @pytest.mark.asyncio
    async def test_calculate_annuity_quote_invalid_rate(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_annuity_quote_data: dict
    ):
        """Test calculating annuity quote with invalid rate fails."""
        sample_annuity_quote_data["annuity_rate"] = "20.00"  # Too high

        response = await async_client.post(
            "/api/v1/retirement/annuity-quote",
            json=sample_annuity_quote_data,
            headers=authenticated_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_annuity_quote_pension_not_found(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_annuity_quote_data: dict
    ):
        """Test calculating annuity quote for non-existent pension fails."""
        sample_annuity_quote_data["pension_id"] = str(uuid4())

        response = await async_client.post(
            "/api/v1/retirement/annuity-quote",
            json=sample_annuity_quote_data,
            headers=authenticated_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_calculate_annuity_quote_wrong_user(
        self,
        async_client: AsyncClient,
        other_user_authenticated_headers: dict,
        sample_annuity_quote_data: dict
    ):
        """Test calculating annuity quote for another user's pension fails."""
        response = await async_client.post(
            "/api/v1/retirement/annuity-quote",
            json=sample_annuity_quote_data,
            headers=other_user_authenticated_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_calculate_annuity_quote_without_auth(
        self,
        async_client: AsyncClient,
        sample_annuity_quote_data: dict
    ):
        """Test calculating annuity quote fails without authentication."""
        response = await async_client.post(
            "/api/v1/retirement/annuity-quote",
            json=sample_annuity_quote_data
        )

        assert response.status_code == 401


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestRetirementProjectionIntegration:
    """Integration tests for retirement projection workflows."""

    @pytest.mark.asyncio
    async def test_full_retirement_planning_workflow(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        sample_dc_pension: UKPension
    ):
        """Test complete retirement planning workflow."""
        # Step 1: Create retirement projection
        projection_data = {
            "target_retirement_age": 65,
            "annual_income_needed": "40000.00",
            "inflation_rate": "2.50"
        }

        projection_response = await async_client.post(
            "/api/v1/retirement/projections",
            json=projection_data,
            headers=authenticated_headers
        )
        assert projection_response.status_code == 201

        # Step 2: Get income projection
        income_response = await async_client.get(
            "/api/v1/retirement/income-projection?retirement_age=65",
            headers=authenticated_headers
        )
        assert income_response.status_code == 200

        # Step 3: Model drawdown scenario
        drawdown_data = {
            "pension_id": str(sample_dc_pension.id),
            "scenario_name": "Standard Drawdown",
            "drawdown_rate": "4.00",
            "start_age": 65
        }

        drawdown_response = await async_client.post(
            "/api/v1/retirement/drawdown-scenario",
            json=drawdown_data,
            headers=authenticated_headers
        )
        assert drawdown_response.status_code == 201

        # Step 4: Get annuity quote
        annuity_data = {
            "pension_id": str(sample_dc_pension.id),
            "annuity_rate": "6.00",
            "spouse_provision": False
        }

        annuity_response = await async_client.post(
            "/api/v1/retirement/annuity-quote",
            json=annuity_data,
            headers=authenticated_headers
        )
        assert annuity_response.status_code == 200

        # Verify all data is consistent
        projection = projection_response.json()
        income_breakdown = income_response.json()
        drawdown = drawdown_response.json()
        annuity = annuity_response.json()

        assert projection["target_retirement_age"] == 65
        assert "total_income" in income_breakdown
        assert drawdown["start_age"] == 65
        assert annuity["pension_id"] == str(sample_dc_pension.id)


# ============================================================================
# ADDITIONAL FIXTURES
# ============================================================================

@pytest.fixture
async def sample_dc_pension(db_session, test_user):
    """Create a sample DC pension for testing."""
    pension = UKPension(
        user_id=test_user.id,
        pension_type=PensionType.OCCUPATIONAL_DC,
        provider="Test Provider",
        employer_name="Test Employer",
        current_value=Decimal("100000.00"),
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
def other_user_auth_headers(other_user):
    """Auth headers for a different user (for authorization tests)."""
    from utils.jwt import create_access_token
    token = create_access_token({"sub": str(other_user.id)})
    return {"Authorization": f"Bearer {token}"}
