"""
Tests for ScenarioService.

Tests:
- Scenario CRUD operations
- Scenario execution
- Scenario comparison
- Scenario limits and validation
"""

import pytest
from datetime import datetime, timedelta, date
from decimal import Decimal
import uuid

from models.scenario import ScenarioType, ScenarioStatus
from services.scenarios import ScenarioService
from services.scenarios.scenario_service import (
    ValidationError, NotFoundError, PermissionError, ScenarioLimitError
)


@pytest.mark.asyncio
async def test_create_scenario(db_session, test_user):
    """Test creating a scenario."""
    service = ScenarioService(db_session)

    scenario_data = {
        'scenario_name': "Retire at 60",
        'scenario_type': ScenarioType.RETIREMENT_AGE_CHANGE,
        'description': "Test retiring at 60 instead of 65",
        'base_case': False,
        'assumptions': [
            {
                'assumption_type': 'retirement',
                'assumption_key': 'retirement_age',
                'assumption_value': '60',
                'unit': 'years'
            }
        ]
    }

    scenario = await service.create_scenario(test_user.id, scenario_data)

    assert scenario.id is not None
    assert scenario.scenario_name == "Retire at 60"
    assert scenario.scenario_type == ScenarioType.RETIREMENT_AGE_CHANGE
    assert scenario.status == ScenarioStatus.DRAFT
    assert len(scenario.assumptions) == 1
    assert scenario.assumptions[0].assumption_value == '60'


@pytest.mark.asyncio
async def test_create_base_case_clears_existing(db_session, test_user):
    """Test that creating a base case clears existing base case."""
    service = ScenarioService(db_session)

    # Create first base case
    scenario1_data = {
        'scenario_name': "Base Case 1",
        'scenario_type': ScenarioType.CUSTOM,
        'base_case': True,
        'assumptions': []
    }

    scenario1 = await service.create_scenario(test_user.id, scenario1_data)
    assert scenario1.base_case is True

    # Create second base case
    scenario2_data = {
        'scenario_name': "Base Case 2",
        'scenario_type': ScenarioType.CUSTOM,
        'base_case': True,
        'assumptions': []
    }

    scenario2 = await service.create_scenario(test_user.id, scenario2_data)
    assert scenario2.base_case is True

    # Refresh scenario1
    await db_session.refresh(scenario1)
    assert scenario1.base_case is False  # Should be cleared


@pytest.mark.asyncio
async def test_scenario_limit(db_session, test_user):
    """Test maximum scenario limit."""
    service = ScenarioService(db_session)

    # Create 5 scenarios (max)
    for i in range(5):
        scenario_data = {
            'scenario_name': f"Scenario {i+1}",
            'scenario_type': ScenarioType.CUSTOM,
            'assumptions': []
        }
        await service.create_scenario(test_user.id, scenario_data)

    # Try to create 6th scenario
    with pytest.raises(ScenarioLimitError):
        scenario_data = {
            'scenario_name': "Scenario 6",
            'scenario_type': ScenarioType.CUSTOM,
            'assumptions': []
        }
        await service.create_scenario(test_user.id, scenario_data)


@pytest.mark.asyncio
async def test_get_scenario(db_session, test_user):
    """Test getting a scenario by ID."""
    service = ScenarioService(db_session)

    # Create scenario
    scenario_data = {
        'scenario_name': "Test Get",
        'scenario_type': ScenarioType.CAREER_CHANGE,
        'assumptions': []
    }

    created = await service.create_scenario(test_user.id, scenario_data)

    # Get scenario
    scenario = await service.get_scenario(created.id, test_user.id)

    assert scenario.id == created.id
    assert scenario.scenario_name == "Test Get"


@pytest.mark.asyncio
async def test_get_scenario_not_found(db_session, test_user):
    """Test getting non-existent scenario."""
    service = ScenarioService(db_session)

    with pytest.raises(NotFoundError):
        await service.get_scenario(uuid.uuid4(), test_user.id)


@pytest.mark.asyncio
async def test_list_scenarios(db_session, test_user):
    """Test listing scenarios."""
    service = ScenarioService(db_session)

    # Create scenarios with different statuses
    scenario1_data = {
        'scenario_name': "Draft Scenario",
        'scenario_type': ScenarioType.CUSTOM,
        'assumptions': []
    }
    await service.create_scenario(test_user.id, scenario1_data)

    # List all scenarios
    scenarios = await service.list_scenarios(test_user.id)
    assert len(scenarios) >= 1


@pytest.mark.asyncio
async def test_update_scenario(db_session, test_user):
    """Test updating a scenario."""
    service = ScenarioService(db_session)

    # Create scenario
    scenario_data = {
        'scenario_name': "Original Name",
        'scenario_type': ScenarioType.CUSTOM,
        'assumptions': []
    }

    created = await service.create_scenario(test_user.id, scenario_data)

    # Update scenario
    update_data = {
        'scenario_name': "Updated Name",
        'description': "New description"
    }

    updated = await service.update_scenario(created.id, test_user.id, update_data)

    assert updated.scenario_name == "Updated Name"
    assert updated.description == "New description"


@pytest.mark.asyncio
async def test_delete_scenario(db_session, test_user):
    """Test deleting (archiving) a scenario."""
    service = ScenarioService(db_session)

    # Create scenario
    scenario_data = {
        'scenario_name': "To Delete",
        'scenario_type': ScenarioType.CUSTOM,
        'assumptions': []
    }

    created = await service.create_scenario(test_user.id, scenario_data)

    # Delete scenario
    await service.delete_scenario(created.id, test_user.id)

    # Verify status is ARCHIVED
    scenario = await service.get_scenario(created.id, test_user.id)
    assert scenario.status == ScenarioStatus.ARCHIVED


@pytest.mark.asyncio
async def test_run_scenario(db_session, test_user, test_savings_account):
    """Test running a scenario."""
    service = ScenarioService(db_session)

    # Create scenario
    scenario_data = {
        'scenario_name': "Test Run",
        'scenario_type': ScenarioType.RETIREMENT_AGE_CHANGE,
        'assumptions': [
            {
                'assumption_type': 'retirement',
                'assumption_key': 'retirement_age',
                'assumption_value': '65',
                'unit': 'years'
            }
        ]
    }

    scenario = await service.create_scenario(test_user.id, scenario_data)

    # Run scenario
    execution_params = {
        'projection_years': 20,
        'growth_rate': Decimal('6.00'),
        'inflation_rate': Decimal('2.50'),
        'include_monte_carlo': False
    }

    result = await service.run_scenario(scenario.id, test_user.id, execution_params)

    assert result is not None
    assert result.scenario_id == scenario.id
    assert result.projection_years == 20
    assert result.final_net_worth is not None

    # Verify scenario status updated
    await db_session.refresh(scenario)
    assert scenario.status == ScenarioStatus.CALCULATED
