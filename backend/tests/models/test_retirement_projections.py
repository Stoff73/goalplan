"""
Tests for retirement projection models.

Tests cover:
- RetirementProjection model creation and validation
- Income gap calculation (positive and negative)
- On-track status determination
- Temporal data support
- DrawdownScenario model creation and validation
- Drawdown rate validation
- Pot depletion calculation
- Relationships and cascades
- Database constraints
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models.retirement import (
    RetirementProjection,
    DrawdownScenario,
    UKPension,
    PensionType,
    InvestmentStrategy
)
from models.user import User


@pytest.mark.asyncio
class TestRetirementProjection:
    """Test RetirementProjection model."""

    async def test_create_retirement_projection(self, db_session, test_user):
        """Test creating a retirement projection with all fields."""
        projection = RetirementProjection(
            user_id=test_user.id,
            projection_date=date.today(),
            target_retirement_age=65,
            projected_total_pot=Decimal('400000.00'),
            annual_income_needed=Decimal('30000.00'),
            state_pension_income=Decimal('11500.00'),
            db_pension_income=Decimal('10000.00'),
            dc_drawdown_income=Decimal('8000.00'),
            other_income=Decimal('1500.00'),
            total_projected_income=Decimal('31000.00'),
            income_gap=Decimal('1000.00'),
            on_track=True,
            inflation_rate=Decimal('2.50'),
            effective_from=date.today()
        )

        db_session.add(projection)
        await db_session.commit()
        await db_session.refresh(projection)

        assert projection.id is not None
        assert projection.user_id == test_user.id
        assert projection.target_retirement_age == 65
        assert projection.projected_total_pot == Decimal('400000.00')
        assert projection.annual_income_needed == Decimal('30000.00')
        assert projection.total_projected_income == Decimal('31000.00')
        assert projection.income_gap == Decimal('1000.00')
        assert projection.on_track is True
        assert projection.inflation_rate == Decimal('2.50')

    async def test_calculate_income_gap_surplus(self, db_session, test_user):
        """Test income gap calculation with surplus (positive gap)."""
        projection = RetirementProjection(
            user_id=test_user.id,
            projection_date=date.today(),
            target_retirement_age=67,
            projected_total_pot=Decimal('500000.00'),
            annual_income_needed=Decimal('30000.00'),
            state_pension_income=Decimal('11500.00'),
            db_pension_income=Decimal('15000.00'),
            dc_drawdown_income=Decimal('8000.00'),
            other_income=Decimal('1000.00'),
            effective_from=date.today()
        )

        # Calculate gap
        gap = projection.calculate_income_gap()

        # Expected: 11500 + 15000 + 8000 + 1000 - 30000 = 5500
        assert gap == Decimal('5500.00')
        assert gap > 0  # Surplus

    async def test_calculate_income_gap_shortfall(self, db_session, test_user):
        """Test income gap calculation with shortfall (negative gap)."""
        projection = RetirementProjection(
            user_id=test_user.id,
            projection_date=date.today(),
            target_retirement_age=67,
            projected_total_pot=Decimal('300000.00'),
            annual_income_needed=Decimal('40000.00'),
            state_pension_income=Decimal('11500.00'),
            db_pension_income=Decimal('10000.00'),
            dc_drawdown_income=Decimal('6000.00'),
            other_income=Decimal('0.00'),
            effective_from=date.today()
        )

        # Calculate gap
        gap = projection.calculate_income_gap()

        # Expected: 11500 + 10000 + 6000 + 0 - 40000 = -12500
        assert gap == Decimal('-12500.00')
        assert gap < 0  # Shortfall

    async def test_is_on_track_true(self, db_session, test_user):
        """Test on_track determination when income meets needs."""
        projection = RetirementProjection(
            user_id=test_user.id,
            projection_date=date.today(),
            target_retirement_age=67,
            projected_total_pot=Decimal('500000.00'),
            annual_income_needed=Decimal('30000.00'),
            state_pension_income=Decimal('11500.00'),
            db_pension_income=Decimal('15000.00'),
            dc_drawdown_income=Decimal('8000.00'),
            other_income=Decimal('0.00'),
            effective_from=date.today()
        )

        # Check on track status
        on_track = projection.is_on_track()

        # Expected: Income (34500) > Needed (30000) = True
        assert on_track is True

    async def test_is_on_track_false(self, db_session, test_user):
        """Test on_track determination when income doesn't meet needs."""
        projection = RetirementProjection(
            user_id=test_user.id,
            projection_date=date.today(),
            target_retirement_age=67,
            projected_total_pot=Decimal('200000.00'),
            annual_income_needed=Decimal('40000.00'),
            state_pension_income=Decimal('11500.00'),
            db_pension_income=Decimal('5000.00'),
            dc_drawdown_income=Decimal('8000.00'),
            other_income=Decimal('0.00'),
            effective_from=date.today()
        )

        # Check on track status
        on_track = projection.is_on_track()

        # Expected: Income (24500) < Needed (40000) = False
        assert on_track is False

    async def test_temporal_data_support(self, db_session, test_user):
        """Test temporal data with effective_from and effective_to."""
        # Create historical projection
        historical_projection = RetirementProjection(
            user_id=test_user.id,
            projection_date=date(2024, 1, 1),
            target_retirement_age=67,
            projected_total_pot=Decimal('300000.00'),
            annual_income_needed=Decimal('30000.00'),
            state_pension_income=Decimal('11500.00'),
            effective_from=date(2024, 1, 1),
            effective_to=date(2024, 6, 30)  # No longer current
        )

        # Create current projection
        current_projection = RetirementProjection(
            user_id=test_user.id,
            projection_date=date(2024, 7, 1),
            target_retirement_age=67,
            projected_total_pot=Decimal('350000.00'),
            annual_income_needed=Decimal('32000.00'),
            state_pension_income=Decimal('11500.00'),
            effective_from=date(2024, 7, 1),
            effective_to=None  # Current
        )

        db_session.add_all([historical_projection, current_projection])
        await db_session.commit()

        # Query current projection (effective_to IS NULL)
        result = await db_session.execute(
            select(RetirementProjection).filter(
                RetirementProjection.user_id == test_user.id,
                RetirementProjection.effective_to.is_(None)
            )
        )
        current = result.scalars().first()

        assert current is not None
        assert current.projected_total_pot == Decimal('350000.00')
        assert current.effective_to is None

        # Query historical projection
        result = await db_session.execute(
            select(RetirementProjection).filter(
                RetirementProjection.user_id == test_user.id,
                RetirementProjection.effective_to.isnot(None)
            )
        )
        historical = result.scalars().first()

        assert historical is not None
        assert historical.projected_total_pot == Decimal('300000.00')
        assert historical.effective_to == date(2024, 6, 30)

    async def test_growth_assumptions_json(self, db_session, test_user):
        """Test storing growth assumptions as JSON."""
        projection = RetirementProjection(
            user_id=test_user.id,
            projection_date=date.today(),
            target_retirement_age=67,
            projected_total_pot=Decimal('500000.00'),
            annual_income_needed=Decimal('35000.00'),
            growth_assumptions={
                'equities': 7.5,
                'bonds': 3.0,
                'cash': 1.5,
                'property': 5.0
            },
            effective_from=date.today()
        )

        db_session.add(projection)
        await db_session.commit()
        await db_session.refresh(projection)

        assert projection.growth_assumptions is not None
        assert projection.growth_assumptions['equities'] == 7.5
        assert projection.growth_assumptions['bonds'] == 3.0
        assert projection.growth_assumptions['cash'] == 1.5
        assert projection.growth_assumptions['property'] == 5.0

    async def test_constraint_target_retirement_age_min(self, db_session, test_user):
        """Test constraint: target_retirement_age >= 55."""
        projection = RetirementProjection(
            user_id=test_user.id,
            projection_date=date.today(),
            target_retirement_age=50,  # Invalid: < 55
            projected_total_pot=Decimal('500000.00'),
            annual_income_needed=Decimal('35000.00'),
            effective_from=date.today()
        )

        db_session.add(projection)
        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()
        assert 'check_projection_valid_retirement_age' in str(exc_info.value).lower()

    async def test_constraint_annual_income_needed_positive(self, db_session, test_user):
        """Test constraint: annual_income_needed > 0."""
        projection = RetirementProjection(
            user_id=test_user.id,
            projection_date=date.today(),
            target_retirement_age=67,
            projected_total_pot=Decimal('500000.00'),
            annual_income_needed=Decimal('0.00'),  # Invalid: must be > 0
            effective_from=date.today()
        )

        db_session.add(projection)
        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()
        assert 'check_projection_positive_income_needed' in str(exc_info.value).lower()

    async def test_constraint_effective_dates_valid(self, db_session, test_user):
        """Test constraint: effective_to >= effective_from."""
        projection = RetirementProjection(
            user_id=test_user.id,
            projection_date=date.today(),
            target_retirement_age=67,
            projected_total_pot=Decimal('500000.00'),
            annual_income_needed=Decimal('35000.00'),
            effective_from=date(2024, 7, 1),
            effective_to=date(2024, 1, 1)  # Invalid: before effective_from
        )

        db_session.add(projection)
        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()
        assert 'check_projection_valid_effective_dates' in str(exc_info.value).lower()

    async def test_user_relationship_cascade_delete(self, db_session, test_user):
        """Test cascade delete when user is deleted."""
        projection = RetirementProjection(
            user_id=test_user.id,
            projection_date=date.today(),
            target_retirement_age=67,
            projected_total_pot=Decimal('500000.00'),
            annual_income_needed=Decimal('35000.00'),
            effective_from=date.today()
        )

        db_session.add(projection)
        await db_session.commit()

        projection_id = projection.id

        # Delete user
        await db_session.delete(test_user)
        await db_session.commit()

        # Projection should be deleted
        result = await db_session.execute(
            select(RetirementProjection).filter(RetirementProjection.id == projection_id)
        )
        deleted_projection = result.scalars().first()
        assert deleted_projection is None


@pytest.mark.asyncio
class TestDrawdownScenario:
    """Test DrawdownScenario model."""

    @pytest.fixture
    async def sample_pension(self, db_session, test_user):
        """Create a sample UK pension."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider="Vanguard UK",
            employer_name=None,
            current_value=Decimal('250000.00'),
            start_date=date(2010, 1, 1),
            expected_retirement_date=date(2035, 3, 20),
            investment_strategy=InvestmentStrategy.BALANCED,
            assumed_growth_rate=Decimal('6.00'),
            assumed_inflation_rate=Decimal('2.50')
        )
        pension.set_scheme_reference("SIPP123456")

        db_session.add(pension)
        await db_session.commit()
        await db_session.refresh(pension)
        return pension

    async def test_create_drawdown_scenario(self, db_session, test_user, sample_pension):
        """Test creating a drawdown scenario."""
        scenario = DrawdownScenario(
            pension_id=sample_pension.id,
            scenario_name="Conservative 4%",
            drawdown_rate=Decimal('4.00'),
            start_age=65,
            projected_annual_income=Decimal('10000.00'),
            pot_depletion_age=None,  # Pot lasts
            tax_implications={
                'income_tax_rate': 20,
                'personal_allowance': 12570
            },
            assumptions={
                'growth_rate': 5.0,
                'inflation_rate': 2.5
            }
        )

        db_session.add(scenario)
        await db_session.commit()
        await db_session.refresh(scenario)

        assert scenario.id is not None
        assert scenario.pension_id == sample_pension.id
        assert scenario.scenario_name == "Conservative 4%"
        assert scenario.drawdown_rate == Decimal('4.00')
        assert scenario.start_age == 65
        assert scenario.projected_annual_income == Decimal('10000.00')
        assert scenario.pot_depletion_age is None

    async def test_drawdown_rate_validation_too_low(self, db_session, test_user, sample_pension):
        """Test validation: drawdown_rate must be >= 2%."""
        with pytest.raises(ValueError) as exc_info:
            scenario = DrawdownScenario(
                pension_id=sample_pension.id,
                scenario_name="Too Low",
                drawdown_rate=Decimal('1.50'),  # Invalid: < 2%
                start_age=65,
                projected_annual_income=Decimal('5000.00')
            )
        assert "between 2% and 8%" in str(exc_info.value)

    async def test_drawdown_rate_validation_too_high(self, db_session, test_user, sample_pension):
        """Test validation: drawdown_rate must be <= 8%."""
        with pytest.raises(ValueError) as exc_info:
            scenario = DrawdownScenario(
                pension_id=sample_pension.id,
                scenario_name="Too High",
                drawdown_rate=Decimal('9.00'),  # Invalid: > 8%
                start_age=65,
                projected_annual_income=Decimal('20000.00')
            )
        assert "between 2% and 8%" in str(exc_info.value)

    async def test_start_age_validation_too_low(self, db_session, test_user, sample_pension):
        """Test validation: start_age must be >= 55."""
        with pytest.raises(ValueError) as exc_info:
            scenario = DrawdownScenario(
                pension_id=sample_pension.id,
                scenario_name="Too Young",
                drawdown_rate=Decimal('4.00'),
                start_age=50,  # Invalid: < 55
                projected_annual_income=Decimal('10000.00')
            )
        assert "between 55 and 75" in str(exc_info.value)

    async def test_start_age_validation_too_high(self, db_session, test_user, sample_pension):
        """Test validation: start_age must be <= 75."""
        with pytest.raises(ValueError) as exc_info:
            scenario = DrawdownScenario(
                pension_id=sample_pension.id,
                scenario_name="Too Old",
                drawdown_rate=Decimal('4.00'),
                start_age=80,  # Invalid: > 75
                projected_annual_income=Decimal('10000.00')
            )
        assert "between 55 and 75" in str(exc_info.value)

    async def test_calculate_pot_depletion_depletes(self, db_session, test_user, sample_pension):
        """Test pot depletion calculation when pot runs out."""
        scenario = DrawdownScenario(
            pension_id=sample_pension.id,
            scenario_name="High Drawdown",
            drawdown_rate=Decimal('7.00'),
            start_age=65,
            projected_annual_income=Decimal('17500.00')  # 7% of 250k
        )

        db_session.add(scenario)
        await db_session.commit()

        # Calculate depletion with low growth (pot will deplete)
        depletion_age = scenario.calculate_pot_depletion(
            current_pot_value=Decimal('250000.00'),
            growth_rate=Decimal('3.00'),  # Low growth
            inflation_rate=Decimal('2.50'),
            life_expectancy=95
        )

        # Pot should deplete at some age
        assert depletion_age is not None
        assert depletion_age > scenario.start_age
        assert depletion_age < 95

    async def test_calculate_pot_depletion_lasts(self, db_session, test_user, sample_pension):
        """Test pot depletion calculation when pot lasts until life expectancy."""
        scenario = DrawdownScenario(
            pension_id=sample_pension.id,
            scenario_name="Conservative Drawdown",
            drawdown_rate=Decimal('3.00'),
            start_age=65,
            projected_annual_income=Decimal('7500.00')  # 3% of 250k
        )

        db_session.add(scenario)
        await db_session.commit()

        # Calculate depletion with good growth (pot should last)
        depletion_age = scenario.calculate_pot_depletion(
            current_pot_value=Decimal('250000.00'),
            growth_rate=Decimal('7.00'),  # High growth
            inflation_rate=Decimal('2.50'),
            life_expectancy=95
        )

        # Pot should last until life expectancy
        assert depletion_age is None

    async def test_multiple_scenarios_per_pension(self, db_session, test_user, sample_pension):
        """Test creating multiple drawdown scenarios for one pension."""
        conservative = DrawdownScenario(
            pension_id=sample_pension.id,
            scenario_name="Conservative",
            drawdown_rate=Decimal('3.00'),
            start_age=65,
            projected_annual_income=Decimal('7500.00')
        )

        moderate = DrawdownScenario(
            pension_id=sample_pension.id,
            scenario_name="Moderate",
            drawdown_rate=Decimal('4.50'),
            start_age=65,
            projected_annual_income=Decimal('11250.00')
        )

        aggressive = DrawdownScenario(
            pension_id=sample_pension.id,
            scenario_name="Aggressive",
            drawdown_rate=Decimal('6.00'),
            start_age=65,
            projected_annual_income=Decimal('15000.00')
        )

        db_session.add_all([conservative, moderate, aggressive])
        await db_session.commit()

        # Query all scenarios for this pension
        result = await db_session.execute(
            select(DrawdownScenario)
            .filter(DrawdownScenario.pension_id == sample_pension.id)
            .order_by(DrawdownScenario.drawdown_rate)
        )
        scenarios = result.scalars().all()

        assert len(scenarios) == 3
        assert scenarios[0].scenario_name == "Conservative"
        assert scenarios[1].scenario_name == "Moderate"
        assert scenarios[2].scenario_name == "Aggressive"

    async def test_pension_relationship_cascade_delete(self, db_session, test_user):
        """Test cascade delete when pension is deleted."""
        # Create a fresh pension for this test
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider="Test Cascade Provider",
            employer_name=None,
            current_value=Decimal('100000.00'),
            start_date=date(2015, 1, 1),
            expected_retirement_date=date(2040, 1, 1),
            investment_strategy=InvestmentStrategy.BALANCED,
            assumed_growth_rate=Decimal('6.00'),
            assumed_inflation_rate=Decimal('2.50')
        )
        pension.set_scheme_reference("CASCADE-TEST-123")

        db_session.add(pension)
        await db_session.commit()
        await db_session.refresh(pension)

        # Create scenario linked to this pension
        scenario = DrawdownScenario(
            pension_id=pension.id,
            scenario_name="Test Scenario",
            drawdown_rate=Decimal('4.00'),
            start_age=65,
            projected_annual_income=Decimal('10000.00')
        )

        db_session.add(scenario)
        await db_session.commit()

        pension_id = pension.id
        scenario_id = scenario.id

        # Delete pension
        await db_session.delete(pension)
        await db_session.commit()

        # Scenario should be deleted (cascade)
        result = await db_session.execute(
            select(DrawdownScenario).filter(DrawdownScenario.id == scenario_id)
        )
        deleted_scenario = result.scalars().first()
        assert deleted_scenario is None

    async def test_constraint_pot_depletion_age_valid(self, db_session, test_user, sample_pension):
        """Test constraint: pot_depletion_age >= start_age if not NULL."""
        scenario = DrawdownScenario(
            pension_id=sample_pension.id,
            scenario_name="Invalid Depletion",
            drawdown_rate=Decimal('4.00'),
            start_age=65,
            projected_annual_income=Decimal('10000.00'),
            pot_depletion_age=60  # Invalid: < start_age
        )

        db_session.add(scenario)
        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()
        assert 'check_drawdown_valid_depletion_age' in str(exc_info.value).lower()
