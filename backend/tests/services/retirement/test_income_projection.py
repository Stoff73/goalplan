"""
Tests for Income Projection Service

Tests retirement income projection calculations including:
- DC pension pot projection with contributions
- Drawdown income calculations with pot depletion
- Annuity income calculations
- Total retirement income aggregation
- Income gap analysis
- Retirement projection creation
- Edge cases and scenarios

Target: >85% coverage
"""

import pytest
import uuid
from datetime import date
from decimal import Decimal

from models.retirement import (
    UKPension, UKPensionDBDetails, StatePensionForecast,
    RetirementProjection, PensionType, DBSchemeType
)
from models.user import User, UserStatus
from services.retirement import IncomeProjectionService



@pytest.fixture
async def projection_service(db_session):
    """Create Income Projection service instance."""
    return IncomeProjectionService(db_session)


class TestProjectDCPensionValue:
    """Tests for DC pension projection."""

    async def test_project_value_no_contributions(self, projection_service):
        """Test projection with current value only (no future contributions)."""
        projected_value = projection_service.project_dc_pension_value(
            current_value=Decimal('100000.00'),
            monthly_contribution=Decimal('0.00'),
            growth_rate=Decimal('5.00'),  # 5% annual growth
            years_to_retirement=10
        )

        # 100,000 * (1.05)^10 ≈ 162,889
        assert projected_value > Decimal('162000.00')
        assert projected_value < Decimal('163000.00')

    async def test_project_value_with_contributions(self, projection_service):
        """Test projection with future contributions."""
        projected_value = projection_service.project_dc_pension_value(
            current_value=Decimal('50000.00'),
            monthly_contribution=Decimal('1000.00'),  # £1,000/month = £12,000/year
            growth_rate=Decimal('5.00'),
            years_to_retirement=20
        )

        # Should be significantly higher due to contributions
        # Current value grows: 50,000 * (1.05)^20 ≈ 132,664
        # Contributions FV: 12,000 * [((1.05)^20 - 1) / 0.05] ≈ 396,528
        # Total ≈ 529,192
        assert projected_value > Decimal('520000.00')
        assert projected_value < Decimal('540000.00')

    async def test_project_value_zero_years(self, projection_service):
        """Test projection with zero years to retirement."""
        projected_value = projection_service.project_dc_pension_value(
            current_value=Decimal('100000.00'),
            monthly_contribution=Decimal('500.00'),
            growth_rate=Decimal('5.00'),
            years_to_retirement=0
        )

        # Should return current value unchanged
        assert projected_value == Decimal('100000.00')

    async def test_project_value_zero_growth(self, projection_service):
        """Test projection with zero growth rate."""
        projected_value = projection_service.project_dc_pension_value(
            current_value=Decimal('50000.00'),
            monthly_contribution=Decimal('500.00'),
            growth_rate=Decimal('0.00'),  # No growth
            years_to_retirement=10
        )

        # Current value stays same: 50,000
        # Contributions: 500 * 12 * 10 = 60,000
        # Total: 110,000
        assert projected_value == Decimal('110000.00')


class TestCalculateDrawdownIncome:
    """Tests for drawdown income calculation."""

    async def test_drawdown_pot_lasts_to_life_expectancy(self, projection_service):
        """Test sustainable drawdown that lasts to life expectancy."""
        result = projection_service.calculate_drawdown_income(
            pot_value=Decimal('500000.00'),
            drawdown_rate=Decimal('4.00'),  # 4% safe withdrawal rate
            start_age=65,
            growth_rate=Decimal('5.00'),
            inflation_rate=Decimal('2.50'),
            life_expectancy=95
        )

        # Annual income: 500,000 * 4% = 20,000
        assert result['annual_income'] == Decimal('20000.00')
        assert result['monthly_income'] == Decimal('20000.00') / Decimal('12')
        assert result['pot_lasts'] == True
        assert result['depletion_age'] is None
        assert result['years_lasting'] == 30  # 95 - 65

    async def test_drawdown_pot_depletes(self, projection_service):
        """Test high drawdown rate that depletes pot."""
        result = projection_service.calculate_drawdown_income(
            pot_value=Decimal('200000.00'),
            drawdown_rate=Decimal('8.00'),  # 8% high withdrawal (unsustainable)
            start_age=65,
            growth_rate=Decimal('3.00'),  # Lower growth than withdrawal
            inflation_rate=Decimal('2.50'),
            life_expectancy=95
        )

        # Pot should deplete before life expectancy
        assert result['pot_lasts'] == False
        assert result['depletion_age'] is not None
        assert result['depletion_age'] < 95
        assert result['depletion_age'] >= 65

    async def test_drawdown_conservative_rate(self, projection_service):
        """Test conservative 2.5% drawdown rate."""
        result = projection_service.calculate_drawdown_income(
            pot_value=Decimal('1000000.00'),
            drawdown_rate=Decimal('2.50'),  # Very conservative
            start_age=60,
            growth_rate=Decimal('5.00'),
            inflation_rate=Decimal('2.00'),
            life_expectancy=95
        )

        # Annual income: 1,000,000 * 2.5% = 25,000
        assert result['annual_income'] == Decimal('25000.00')
        assert result['pot_lasts'] == True  # Should definitely last


class TestCalculateAnnuityIncome:
    """Tests for annuity income calculation."""

    async def test_annuity_single_life(self, projection_service):
        """Test single life annuity calculation."""
        annual_income = projection_service.calculate_annuity_income(
            pot_value=Decimal('100000.00'),
            annuity_rate=Decimal('5.50'),  # 5.5% annuity rate
            spouse_provision=False
        )

        # 100,000 * 5.5% = 5,500
        assert annual_income == Decimal('5500.00')

    async def test_annuity_with_spouse_provision(self, projection_service):
        """Test joint life annuity with spouse provision."""
        annual_income = projection_service.calculate_annuity_income(
            pot_value=Decimal('100000.00'),
            annuity_rate=Decimal('5.50'),
            spouse_provision=True  # Reduces income by 12.5%
        )

        # 100,000 * 5.5% * (1 - 0.125) = 5,500 * 0.875 = 4,812.50
        assert annual_income == Decimal('4812.50')

    async def test_annuity_large_pot(self, projection_service):
        """Test annuity with large pot value."""
        annual_income = projection_service.calculate_annuity_income(
            pot_value=Decimal('500000.00'),
            annuity_rate=Decimal('6.00'),
            spouse_provision=False
        )

        # 500,000 * 6% = 30,000
        assert annual_income == Decimal('30000.00')


class TestCalculateTotalRetirementIncome:
    """Tests for total retirement income calculation."""

    async def test_total_income_state_pension_only(self, projection_service, test_user, db_session):
        """Test income with state pension only."""
        # Create state pension forecast
        state_pension = StatePensionForecast(
            id=uuid.uuid4(),
            user_id=test_user.id,
            forecast_date=date(2024, 1, 1),
            qualifying_years=35,
            years_needed_for_full=35,
            estimated_weekly_amount=Decimal('203.85'),
            estimated_annual_amount=Decimal('11203.85'),  # Full state pension 2024/25
            state_pension_age=67
        )
        db_session.add(state_pension)
        await db_session.commit()

        income = await projection_service.calculate_total_retirement_income(
            test_user.id,
            target_retirement_age=67
        )

        assert income['state_pension_income'] == Decimal('11203.85')
        assert income['db_pension_income'] == Decimal('0.00')
        assert income['dc_drawdown_income'] == Decimal('0.00')
        assert income['total_annual_income'] == Decimal('11203.85')

    async def test_total_income_multiple_sources(self, projection_service, test_user, db_session):
        """Test income from multiple sources."""
        # State pension
        state_pension = StatePensionForecast(
            id=uuid.uuid4(),
            user_id=test_user.id,
            forecast_date=date(2024, 1, 1),
            qualifying_years=35,
            years_needed_for_full=35,
            estimated_weekly_amount=Decimal('203.85'),
            estimated_annual_amount=Decimal('11203.85'),
            state_pension_age=67
        )
        db_session.add(state_pension)

        # DB pension
        db_pension = UKPension(
            id=uuid.uuid4(),
            user_id=test_user.id,
            pension_type=PensionType.OCCUPATIONAL_DB,
            provider='DB Provider',
            scheme_reference_encrypted='encrypted_db',
            start_date=date(2010, 1, 1),
            expected_retirement_date=date(2040, 1, 1),
            is_deleted=False
        )
        db_session.add(db_pension)
        await db_session.flush()

        db_details = UKPensionDBDetails(
            id=uuid.uuid4(),
            pension_id=db_pension.id,
            accrual_rate='1/60',
            pensionable_service_years=Decimal('20.00'),
            scheme_type=DBSchemeType.FINAL_SALARY,
            normal_retirement_age=65,
            guaranteed_pension_amount=Decimal('15000.00')  # £15k guaranteed
        )
        db_session.add(db_details)

        # DC pension
        dc_pension = UKPension(
            id=uuid.uuid4(),
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider='DC Provider',
            scheme_reference_encrypted='encrypted_dc',
            current_value=Decimal('250000.00'),
            start_date=date(2020, 1, 1),
            expected_retirement_date=date(2050, 1, 1),
            assumed_growth_rate=Decimal('5.00'),
            is_deleted=False
        )
        db_session.add(dc_pension)
        await db_session.commit()

        income = await projection_service.calculate_total_retirement_income(
            test_user.id,
            target_retirement_age=67
        )

        # State pension
        assert income['state_pension_income'] == Decimal('11203.85')

        # DB pension
        assert income['db_pension_income'] == Decimal('15000.00')

        # DC drawdown (4% of 250k = 10k)
        assert income['dc_drawdown_income'] == Decimal('10000.00')

        # Total: 11,203.85 + 15,000 + 10,000 = 36,203.85
        assert income['total_annual_income'] == Decimal('36203.85')

        # Should have 3 items in breakdown
        assert len(income['breakdown']) == 3


class TestCalculateRetirementIncomeGap:
    """Tests for income gap calculation."""

    async def test_income_gap_on_track(self, projection_service, test_user, db_session):
        """Test income gap when on track (surplus)."""
        # Create state pension with full amount
        state_pension = StatePensionForecast(
            id=uuid.uuid4(),
            user_id=test_user.id,
            forecast_date=date(2024, 1, 1),
            qualifying_years=35,
            years_needed_for_full=35,
            estimated_weekly_amount=Decimal('203.85'),
            estimated_annual_amount=Decimal('11203.85'),
            state_pension_age=67
        )
        db_session.add(state_pension)

        # Create DC pension
        dc_pension = UKPension(
            id=uuid.uuid4(),
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider='Provider',
            scheme_reference_encrypted='encrypted',
            current_value=Decimal('300000.00'),
            start_date=date(2020, 1, 1),
            expected_retirement_date=date(2050, 1, 1),
            is_deleted=False
        )
        db_session.add(dc_pension)
        await db_session.commit()

        # Need £20k per year
        gap = await projection_service.calculate_retirement_income_gap(
            test_user.id,
            target_retirement_age=67,
            annual_income_needed=Decimal('20000.00')
        )

        # Projected: 11,203.85 (state) + 12,000 (4% of 300k) = 23,203.85
        # Gap: 23,203.85 - 20,000 = 3,203.85 (surplus)
        assert gap['total_projected_income'] == Decimal('23203.85')
        assert gap['annual_income_needed'] == Decimal('20000.00')
        assert gap['income_gap'] > Decimal('0.00')  # Positive = surplus
        assert gap['on_track'] == True

    async def test_income_gap_shortfall(self, projection_service, test_user, db_session):
        """Test income gap with shortfall."""
        # Create state pension only
        state_pension = StatePensionForecast(
            id=uuid.uuid4(),
            user_id=test_user.id,
            forecast_date=date(2024, 1, 1),
            qualifying_years=35,
            years_needed_for_full=35,
            estimated_weekly_amount=Decimal('203.85'),
            estimated_annual_amount=Decimal('11203.85'),
            state_pension_age=67
        )
        db_session.add(state_pension)
        await db_session.commit()

        # Need £30k per year
        gap = await projection_service.calculate_retirement_income_gap(
            test_user.id,
            target_retirement_age=67,
            annual_income_needed=Decimal('30000.00')
        )

        # Projected: 11,203.85
        # Gap: 11,203.85 - 30,000 = -18,796.15 (shortfall)
        assert gap['total_projected_income'] == Decimal('11203.85')
        assert gap['annual_income_needed'] == Decimal('30000.00')
        assert gap['income_gap'] < Decimal('0.00')  # Negative = shortfall
        assert gap['on_track'] == False
        assert gap['gap_percentage'] < Decimal('0.00')


class TestCreateRetirementProjection:
    """Tests for retirement projection creation."""

    async def test_create_projection_success(self, projection_service, test_user, db_session):
        """Test successful projection creation."""
        # Create state pension
        state_pension = StatePensionForecast(
            id=uuid.uuid4(),
            user_id=test_user.id,
            forecast_date=date(2024, 1, 1),
            qualifying_years=30,
            years_needed_for_full=35,
            estimated_weekly_amount=Decimal('175.00'),
            estimated_annual_amount=Decimal('9100.00'),
            state_pension_age=67
        )
        db_session.add(state_pension)
        await db_session.commit()

        projection_params = {
            'target_retirement_age': 65,
            'annual_income_needed': Decimal('25000.00'),
            'inflation_rate': Decimal('2.50'),
            'growth_assumptions': {
                'dc_growth': 5.0,
                'db_growth': 0.0
            }
        }

        projection = await projection_service.create_retirement_projection(
            test_user.id,
            projection_params
        )

        assert projection.id is not None
        assert projection.user_id == test_user.id
        assert projection.target_retirement_age == 65
        assert projection.annual_income_needed == Decimal('25000.00')
        assert projection.state_pension_income == Decimal('9100.00')
        assert projection.inflation_rate == Decimal('2.50')
        assert projection.effective_from == date.today()
        assert projection.effective_to is None  # Current projection

    async def test_create_projection_on_track_status(self, projection_service, test_user, db_session):
        """Test projection on_track status determination."""
        # Create generous state pension + DC
        state_pension = StatePensionForecast(
            id=uuid.uuid4(),
            user_id=test_user.id,
            forecast_date=date(2024, 1, 1),
            qualifying_years=35,
            years_needed_for_full=35,
            estimated_weekly_amount=Decimal('203.85'),
            estimated_annual_amount=Decimal('11203.85'),
            state_pension_age=67
        )
        db_session.add(state_pension)

        dc_pension = UKPension(
            id=uuid.uuid4(),
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider='Provider',
            scheme_reference_encrypted='encrypted',
            current_value=Decimal('500000.00'),
            start_date=date(2020, 1, 1),
            expected_retirement_date=date(2050, 1, 1),
            is_deleted=False
        )
        db_session.add(dc_pension)
        await db_session.commit()

        projection_params = {
            'target_retirement_age': 67,
            'annual_income_needed': Decimal('25000.00')
        }

        projection = await projection_service.create_retirement_projection(
            test_user.id,
            projection_params
        )

        # Should be on track (11,203.85 + 20,000 = 31,203.85 > 25,000)
        assert projection.on_track == True
        assert projection.income_gap > Decimal('0.00')


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    async def test_zero_pot_value(self, projection_service):
        """Test projection with zero pot value."""
        projected_value = projection_service.project_dc_pension_value(
            current_value=Decimal('0.00'),
            monthly_contribution=Decimal('500.00'),
            growth_rate=Decimal('5.00'),
            years_to_retirement=10
        )

        # Only contributions + growth
        # 500 * 12 * FV factor
        assert projected_value > Decimal('0.00')

    async def test_very_high_growth_rate(self, projection_service):
        """Test projection with very high growth rate."""
        projected_value = projection_service.project_dc_pension_value(
            current_value=Decimal('10000.00'),
            monthly_contribution=Decimal('0.00'),
            growth_rate=Decimal('15.00'),  # 15% annual growth
            years_to_retirement=20
        )

        # 10,000 * (1.15)^20 ≈ 163,665
        assert projected_value > Decimal('160000.00')

    async def test_negative_years_to_retirement(self, projection_service):
        """Test projection with negative years (already retired)."""
        projected_value = projection_service.project_dc_pension_value(
            current_value=Decimal('100000.00'),
            monthly_contribution=Decimal('0.00'),
            growth_rate=Decimal('5.00'),
            years_to_retirement=-5  # Already retired
        )

        # Should return current value
        assert projected_value == Decimal('100000.00')

    async def test_no_pensions_or_state_pension(self, projection_service, test_user):
        """Test income calculation with no pensions at all."""
        income = await projection_service.calculate_total_retirement_income(
            test_user.id,
            target_retirement_age=67
        )

        # Everything should be zero
        assert income['state_pension_income'] == Decimal('0.00')
        assert income['db_pension_income'] == Decimal('0.00')
        assert income['dc_drawdown_income'] == Decimal('0.00')
        assert income['total_annual_income'] == Decimal('0.00')
        assert len(income['breakdown']) == 0
