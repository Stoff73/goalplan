"""
Tests for scenario models.

Tests:
- Scenario model creation and relationships
- ScenarioAssumption model
- ScenarioResult model with constraints
- Indexes and constraints
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from models.scenario import (
    Scenario, ScenarioAssumption, ScenarioResult,
    ScenarioType, ScenarioStatus
)
from models.user import User, UserStatus, CountryPreference


@pytest.mark.asyncio
async def test_create_scenario(db_session, test_user):
    """Test creating a scenario."""
    scenario = Scenario(
        id=uuid.uuid4(),
        user_id=test_user.id,
        scenario_name="Retire at 60",
        scenario_type=ScenarioType.RETIREMENT_AGE_CHANGE,
        description="Test retiring at 60",
        base_case=False,
        status=ScenarioStatus.DRAFT,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_accessed_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=90)
    )

    db_session.add(scenario)
    await db_session.commit()
    await db_session.refresh(scenario)

    assert scenario.id is not None
    assert scenario.scenario_name == "Retire at 60"
    assert scenario.scenario_type == ScenarioType.RETIREMENT_AGE_CHANGE
    assert scenario.status == ScenarioStatus.DRAFT


@pytest.mark.asyncio
async def test_scenario_assumptions(db_session, test_user):
    """Test scenario with assumptions."""
    scenario = Scenario(
        id=uuid.uuid4(),
        user_id=test_user.id,
        scenario_name="Career Change",
        scenario_type=ScenarioType.CAREER_CHANGE,
        status=ScenarioStatus.DRAFT,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_accessed_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=90)
    )

    db_session.add(scenario)
    await db_session.flush()

    # Add assumptions
    assumption1 = ScenarioAssumption(
        id=uuid.uuid4(),
        scenario_id=scenario.id,
        assumption_type="salary",
        assumption_key="new_salary",
        assumption_value="75000",
        unit="GBP"
    )

    assumption2 = ScenarioAssumption(
        id=uuid.uuid4(),
        scenario_id=scenario.id,
        assumption_type="growth",
        assumption_key="salary_increase_rate",
        assumption_value="3.0",
        unit="%"
    )

    db_session.add_all([assumption1, assumption2])
    await db_session.commit()
    await db_session.refresh(scenario)

    assert len(scenario.assumptions) == 2
    assert scenario.assumptions[0].assumption_type == "salary"


@pytest.mark.asyncio
async def test_scenario_results(db_session, test_user):
    """Test scenario with results."""
    scenario = Scenario(
        id=uuid.uuid4(),
        user_id=test_user.id,
        scenario_name="Property Purchase",
        scenario_type=ScenarioType.PROPERTY_PURCHASE,
        status=ScenarioStatus.CALCULATED,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_accessed_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=90)
    )

    db_session.add(scenario)
    await db_session.flush()

    # Add results
    result = ScenarioResult(
        id=uuid.uuid4(),
        scenario_id=scenario.id,
        calculation_date=datetime.utcnow(),
        calculation_version="1.0.0",
        projection_years=30,
        total_lifetime_tax=Decimal('150000.00'),
        final_net_worth=Decimal('500000.00'),
        retirement_adequacy_ratio=Decimal('75.00'),
        goals_achieved_count=3,
        goals_achieved_percentage=Decimal('75.00'),
        probability_of_success=Decimal('85.00')
    )

    db_session.add(result)
    await db_session.commit()
    await db_session.refresh(scenario)

    assert scenario.results is not None
    assert scenario.results.final_net_worth == Decimal('500000.00')
    assert scenario.results.probability_of_success == Decimal('85.00')


@pytest.mark.asyncio
async def test_scenario_result_constraints(db_session, test_user):
    """Test scenario result constraints."""
    scenario = Scenario(
        id=uuid.uuid4(),
        user_id=test_user.id,
        scenario_name="Test Constraints",
        scenario_type=ScenarioType.CUSTOM,
        status=ScenarioStatus.DRAFT,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_accessed_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=90)
    )

    db_session.add(scenario)
    await db_session.flush()

    # Test valid projection_years (1-30)
    result = ScenarioResult(
        id=uuid.uuid4(),
        scenario_id=scenario.id,
        calculation_date=datetime.utcnow(),
        calculation_version="1.0.0",
        projection_years=15,
        probability_of_success=Decimal('90.00')
    )

    db_session.add(result)
    await db_session.commit()

    assert result.projection_years == 15

    # Test probability constraint (0-100)
    assert result.probability_of_success >= Decimal('0.00')
    assert result.probability_of_success <= Decimal('100.00')


@pytest.mark.asyncio
async def test_scenario_cascade_delete(db_session, test_user):
    """Test cascade delete of scenarios."""
    scenario = Scenario(
        id=uuid.uuid4(),
        user_id=test_user.id,
        scenario_name="To Delete",
        scenario_type=ScenarioType.CUSTOM,
        status=ScenarioStatus.DRAFT,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_accessed_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=90)
    )

    db_session.add(scenario)
    await db_session.flush()

    # Add assumption
    assumption = ScenarioAssumption(
        id=uuid.uuid4(),
        scenario_id=scenario.id,
        assumption_type="test",
        assumption_key="test_key",
        assumption_value="test_value"
    )

    db_session.add(assumption)
    await db_session.commit()

    scenario_id = scenario.id

    # Delete scenario
    await db_session.delete(scenario)
    await db_session.commit()

    # Check that assumptions were cascade deleted
    from sqlalchemy import select
    result = await db_session.execute(
        select(ScenarioAssumption).where(ScenarioAssumption.scenario_id == scenario_id)
    )
    assumptions = result.scalars().all()

    assert len(assumptions) == 0
