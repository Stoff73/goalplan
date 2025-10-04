"""
Tests for scenarios API endpoints.

Tests:
- POST /api/v1/scenarios - Create scenario
- GET /api/v1/scenarios - List scenarios
- GET /api/v1/scenarios/{id} - Get scenario
- PUT /api/v1/scenarios/{id} - Update scenario
- DELETE /api/v1/scenarios/{id} - Delete scenario
- POST /api/v1/scenarios/{id}/run - Run scenario
- POST /api/v1/scenarios/compare - Compare scenarios
- POST /api/v1/scenarios/retirement-age - Retirement age scenario
- POST /api/v1/scenarios/monte-carlo - Monte Carlo simulation
"""

import pytest
from httpx import AsyncClient
from decimal import Decimal
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_create_scenario(async_client: AsyncClient, auth_headers):
    """Test creating a scenario."""
    scenario_data = {
        "scenario_name": "Retire at 60",
        "scenario_type": "RETIREMENT_AGE_CHANGE",
        "description": "Test early retirement",
        "base_case": False,
        "assumptions": [
            {
                "assumption_type": "retirement",
                "assumption_key": "retirement_age",
                "assumption_value": "60",
                "unit": "years"
            }
        ]
    }

    response = await async_client.post(
        "/api/v1/scenarios",
        json=scenario_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data['scenario_name'] == "Retire at 60"
    assert data['scenario_type'] == "RETIREMENT_AGE_CHANGE"
    assert data['status'] == "DRAFT"
    assert len(data['assumptions']) == 1


@pytest.mark.asyncio
async def test_list_scenarios(async_client: AsyncClient, auth_headers):
    """Test listing scenarios."""
    # Create a scenario first
    scenario_data = {
        "scenario_name": "Test List",
        "scenario_type": "CUSTOM",
        "assumptions": []
    }

    await async_client.post(
        "/api/v1/scenarios",
        json=scenario_data,
        headers=auth_headers
    )

    # List scenarios
    response = await async_client.get(
        "/api/v1/scenarios",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_scenario(async_client: AsyncClient, auth_headers):
    """Test getting a specific scenario."""
    # Create scenario
    scenario_data = {
        "scenario_name": "Test Get",
        "scenario_type": "CAREER_CHANGE",
        "assumptions": []
    }

    create_response = await async_client.post(
        "/api/v1/scenarios",
        json=scenario_data,
        headers=auth_headers
    )

    scenario_id = create_response.json()['id']

    # Get scenario
    response = await async_client.get(
        f"/api/v1/scenarios/{scenario_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data['id'] == scenario_id
    assert data['scenario_name'] == "Test Get"


@pytest.mark.asyncio
async def test_update_scenario(async_client: AsyncClient, auth_headers):
    """Test updating a scenario."""
    # Create scenario
    scenario_data = {
        "scenario_name": "Original",
        "scenario_type": "CUSTOM",
        "assumptions": []
    }

    create_response = await async_client.post(
        "/api/v1/scenarios",
        json=scenario_data,
        headers=auth_headers
    )

    scenario_id = create_response.json()['id']

    # Update scenario
    update_data = {
        "scenario_name": "Updated Name",
        "description": "Updated description"
    }

    response = await async_client.put(
        f"/api/v1/scenarios/{scenario_id}",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data['scenario_name'] == "Updated Name"
    assert data['description'] == "Updated description"


@pytest.mark.asyncio
async def test_delete_scenario(async_client: AsyncClient, auth_headers):
    """Test deleting a scenario."""
    # Create scenario
    scenario_data = {
        "scenario_name": "To Delete",
        "scenario_type": "CUSTOM",
        "assumptions": []
    }

    create_response = await async_client.post(
        "/api/v1/scenarios",
        json=scenario_data,
        headers=auth_headers
    )

    scenario_id = create_response.json()['id']

    # Delete scenario
    response = await async_client.delete(
        f"/api/v1/scenarios/{scenario_id}",
        headers=auth_headers
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_retirement_age_scenario(async_client: AsyncClient, auth_headers):
    """Test retirement age scenario endpoint."""
    request_data = {
        "retirement_age": 65,
        "current_pension_pot": 100000.00,
        "annual_contributions": 5000.00
    }

    response = await async_client.post(
        "/api/v1/scenarios/retirement-age",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data['retirement_age'] == 65
    assert 'pension_pot_at_retirement' in data
    assert 'annual_retirement_income' in data
    assert 'replacement_ratio' in data


@pytest.mark.asyncio
async def test_career_change_scenario(async_client: AsyncClient, auth_headers):
    """Test career change scenario endpoint."""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    request_data = {
        "new_salary": 75000.00,
        "change_date": tomorrow,
        "salary_increase_rate": 3.0
    }

    response = await async_client.post(
        "/api/v1/scenarios/career-change",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data['new_salary'] == 75000.00
    assert 'impact_on_pension' in data
    assert 'impact_on_tax' in data
    assert 'recommendation' in data


@pytest.mark.asyncio
async def test_property_purchase_scenario(async_client: AsyncClient, auth_headers):
    """Test property purchase scenario endpoint."""
    request_data = {
        "property_value": 300000.00,
        "deposit": 60000.00,
        "mortgage_rate": 5.0,
        "mortgage_term_years": 25
    }

    response = await async_client.post(
        "/api/v1/scenarios/property-purchase",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data['property_value'] == 300000.00
    assert data['mortgage_amount'] == 240000.00
    assert 'monthly_payment' in data
    assert 'affordability_percentage' in data
    assert 'recommendation' in data


@pytest.mark.asyncio
async def test_monte_carlo_simulation(async_client: AsyncClient, auth_headers):
    """Test Monte Carlo simulation endpoint."""
    request_data = {
        "simulations": 1000,
        "mean_return": 6.0,
        "volatility": 15.0,
        "mean_inflation": 2.5,
        "inflation_volatility": 1.0,
        "retirement_age": 65,
        "target_income": 25000.00
    }

    response = await async_client.post(
        "/api/v1/scenarios/monte-carlo",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data['simulations_run'] == 1000
    assert 'probability_of_success' in data
    assert 'safe_withdrawal_rate' in data
    assert 'percentiles' in data
    assert 'worst_case' in data
    assert 'best_case' in data


@pytest.mark.asyncio
async def test_unauthorized_access(async_client: AsyncClient):
    """Test that endpoints require authentication."""
    response = await async_client.get("/api/v1/scenarios")
    assert response.status_code == 401  # Unauthorized
