"""
Tests for Annual Allowance Service

Tests comprehensive AA calculations including:
- Standard annual allowance (£60,000)
- MPAA (£10,000) calculations
- Tapered annual allowance for high earners
- Carry forward from previous 3 years
- Annual allowance usage tracking
- Annual allowance charge calculations
- Edge cases and thresholds

Target: >85% coverage
"""

import pytest
import uuid
from datetime import date
from decimal import Decimal

from models.retirement import (
    UKPension, UKPensionContribution, AnnualAllowanceTracking,
    PensionType, ContributionFrequency
)
from models.user import User, UserStatus
from services.retirement import AnnualAllowanceService



@pytest.fixture
async def aa_service(db_session):
    """Create Annual Allowance service instance."""
    return AnnualAllowanceService(db_session)


@pytest.fixture
async def test_pension(db_session, test_user):
    """Create a test pension."""
    pension = UKPension(
        id=uuid.uuid4(),
        user_id=test_user.id,
        pension_type=PensionType.SIPP,
        provider='Test Provider',
        scheme_reference_encrypted='encrypted_ref',
        start_date=date(2020, 1, 1),
        expected_retirement_date=date(2050, 1, 1),
        mpaa_triggered=False,
        is_deleted=False
    )
    db_session.add(pension)
    await db_session.commit()
    await db_session.refresh(pension)
    return pension


class TestCalculateAnnualAllowance:
    """Tests for annual allowance calculation."""

    async def test_standard_allowance(self, aa_service, test_user):
        """Test standard annual allowance (£60,000)."""
        allowance = aa_service.calculate_annual_allowance(
            test_user.id,
            '2024/25',
            adjusted_income=Decimal('50000.00'),  # Below threshold
            mpaa_triggered=False
        )

        assert allowance == Decimal('60000.00')

    async def test_mpaa_allowance(self, aa_service, test_user):
        """Test MPAA (£10,000) when triggered."""
        allowance = aa_service.calculate_annual_allowance(
            test_user.id,
            '2024/25',
            adjusted_income=Decimal('50000.00'),
            mpaa_triggered=True  # MPAA triggered
        )

        assert allowance == Decimal('10000.00')

    async def test_tapered_allowance_just_over_threshold(self, aa_service, test_user):
        """Test tapering just over £260,000 threshold."""
        # Adjusted income: £270,000 (£10,000 over threshold)
        # Reduction: £10,000 / 2 = £5,000
        # Tapered allowance: £60,000 - £5,000 = £55,000
        allowance = aa_service.calculate_annual_allowance(
            test_user.id,
            '2024/25',
            adjusted_income=Decimal('270000.00'),
            mpaa_triggered=False
        )

        assert allowance == Decimal('55000.00')

    async def test_tapered_allowance_high_income(self, aa_service, test_user):
        """Test tapering with high income."""
        # Adjusted income: £300,000 (£40,000 over threshold)
        # Reduction: £40,000 / 2 = £20,000
        # Tapered allowance: £60,000 - £20,000 = £40,000
        allowance = aa_service.calculate_annual_allowance(
            test_user.id,
            '2024/25',
            adjusted_income=Decimal('300000.00'),
            mpaa_triggered=False
        )

        assert allowance == Decimal('40000.00')

    async def test_tapered_allowance_minimum(self, aa_service, test_user):
        """Test tapering reaches minimum (£10,000)."""
        # Adjusted income: £500,000 (£240,000 over threshold)
        # Reduction: £240,000 / 2 = £120,000
        # Tapered allowance would be: £60,000 - £120,000 = -£60,000
        # But minimum is £10,000
        allowance = aa_service.calculate_annual_allowance(
            test_user.id,
            '2024/25',
            adjusted_income=Decimal('500000.00'),
            mpaa_triggered=False
        )

        assert allowance == Decimal('10000.00')

    async def test_tapered_allowance_exactly_at_threshold(self, aa_service, test_user):
        """Test no tapering exactly at threshold."""
        allowance = aa_service.calculate_annual_allowance(
            test_user.id,
            '2024/25',
            adjusted_income=Decimal('260000.00'),  # Exactly at threshold
            mpaa_triggered=False
        )

        # No tapering yet
        assert allowance == Decimal('60000.00')


class TestCalculateCarryForward:
    """Tests for carry forward calculation."""

    async def test_carry_forward_no_previous_tracking(self, aa_service, test_user):
        """Test carry forward with no previous tracking records."""
        carry_forward = await aa_service.calculate_carry_forward(test_user.id, '2024/25')

        # Should have 3 years (2021/22, 2022/23, 2023/24)
        assert len(carry_forward) == 3

        # Each year should show full allowance (£60,000)
        assert carry_forward.get('2021/22') == Decimal('60000.00')
        assert carry_forward.get('2022/23') == Decimal('60000.00')
        assert carry_forward.get('2023/24') == Decimal('60000.00')

    async def test_carry_forward_with_partial_usage(self, aa_service, test_user, db_session):
        """Test carry forward with partial usage in previous years."""
        # Create tracking record for 2023/24 with partial usage
        tracking = AnnualAllowanceTracking(
            id=uuid.uuid4(),
            user_id=test_user.id,
            tax_year='2023/24',
            total_contributions=Decimal('40000.00'),
            annual_allowance_limit=Decimal('60000.00'),
            allowance_used=Decimal('40000.00'),
            allowance_remaining=Decimal('20000.00'),
            tapered_allowance=False
        )
        db_session.add(tracking)
        await db_session.commit()

        # Calculate carry forward for 2024/25
        carry_forward = await aa_service.calculate_carry_forward(test_user.id, '2024/25')

        # 2023/24 should have £20,000 unused
        assert carry_forward.get('2023/24') == Decimal('20000.00')

        # 2021/22 and 2022/23 should have full allowance
        assert carry_forward.get('2021/22') == Decimal('60000.00')
        assert carry_forward.get('2022/23') == Decimal('60000.00')

    async def test_carry_forward_with_full_usage(self, aa_service, test_user, db_session):
        """Test carry forward when previous year fully used."""
        # Create tracking record for 2023/24 with full usage
        tracking = AnnualAllowanceTracking(
            id=uuid.uuid4(),
            user_id=test_user.id,
            tax_year='2023/24',
            total_contributions=Decimal('60000.00'),
            annual_allowance_limit=Decimal('60000.00'),
            allowance_used=Decimal('60000.00'),
            allowance_remaining=Decimal('0.00'),
            tapered_allowance=False
        )
        db_session.add(tracking)
        await db_session.commit()

        # Calculate carry forward
        carry_forward = await aa_service.calculate_carry_forward(test_user.id, '2024/25')

        # 2023/24 should not be in carry forward (fully used)
        assert '2023/24' not in carry_forward

        # 2021/22 and 2022/23 should still be available
        assert carry_forward.get('2021/22') == Decimal('60000.00')
        assert carry_forward.get('2022/23') == Decimal('60000.00')


class TestCalculateAllowanceUsage:
    """Tests for allowance usage calculation."""

    async def test_usage_no_contributions(self, aa_service, test_user):
        """Test usage calculation with no contributions."""
        usage = await aa_service.calculate_allowance_usage(test_user.id, '2024/25')

        assert usage['total_contributions'] == Decimal('0.00')
        assert usage['annual_allowance'] == Decimal('60000.00')
        assert usage['allowance_used'] == Decimal('0.00')
        assert usage['allowance_remaining'] == Decimal('180000.00')  # 60k + 60k + 60k carry forward
        assert usage['excess'] == Decimal('0.00')

    async def test_usage_with_contributions(self, aa_service, test_user, test_pension, db_session):
        """Test usage calculation with contributions."""
        # Add contribution
        contribution = UKPensionContribution(
            id=uuid.uuid4(),
            pension_id=test_pension.id,
            employee_contribution=Decimal('20000.00'),
            employer_contribution=Decimal('15000.00'),
            personal_contribution=Decimal('0.00'),
            frequency=ContributionFrequency.ANNUAL,
            contribution_date=date(2024, 6, 1),
            tax_year='2024/25',
            effective_from=date(2024, 6, 1)
        )
        db_session.add(contribution)
        await db_session.commit()

        usage = await aa_service.calculate_allowance_usage(test_user.id, '2024/25')

        # Total contributions: 20000 + 15000 = 35000
        assert usage['total_contributions'] == Decimal('35000.00')
        assert usage['allowance_used'] == Decimal('35000.00')

        # Remaining: (60000 + 180000 carry forward) - 35000 = 205000
        # But carry forward is calculated separately, so remaining is: 60000 + carry_forward - 35000
        assert usage['allowance_remaining'] > Decimal('0.00')
        assert usage['excess'] == Decimal('0.00')

    async def test_usage_exceeding_allowance(self, aa_service, test_user, test_pension, db_session):
        """Test usage exceeding annual allowance."""
        # Add large contribution
        contribution = UKPensionContribution(
            id=uuid.uuid4(),
            pension_id=test_pension.id,
            employee_contribution=Decimal('100000.00'),
            employer_contribution=Decimal('50000.00'),
            frequency=ContributionFrequency.ANNUAL,
            contribution_date=date(2024, 6, 1),
            tax_year='2024/25',
            effective_from=date(2024, 6, 1)
        )
        db_session.add(contribution)
        await db_session.commit()

        usage = await aa_service.calculate_allowance_usage(test_user.id, '2024/25')

        # Total contributions: 150000
        assert usage['total_contributions'] == Decimal('150000.00')

        # With carry forward (60k + 180k = 240k total), no excess
        assert usage['total_available'] == Decimal('240000.00')
        assert usage['excess'] == Decimal('0.00')

    async def test_usage_with_mpaa(self, aa_service, test_user, db_session):
        """Test usage calculation when MPAA applies."""
        # Create pension with MPAA triggered
        pension = UKPension(
            id=uuid.uuid4(),
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider='MPAA Provider',
            scheme_reference_encrypted='encrypted_mpaa',
            start_date=date(2020, 1, 1),
            expected_retirement_date=date(2050, 1, 1),
            mpaa_triggered=True,  # MPAA triggered
            mpaa_date=date(2023, 6, 1),
            is_deleted=False
        )
        db_session.add(pension)
        await db_session.flush()

        # Add contribution
        contribution = UKPensionContribution(
            id=uuid.uuid4(),
            pension_id=pension.id,
            employee_contribution=Decimal('8000.00'),
            frequency=ContributionFrequency.ANNUAL,
            contribution_date=date(2024, 6, 1),
            tax_year='2024/25',
            effective_from=date(2024, 6, 1)
        )
        db_session.add(contribution)
        await db_session.commit()

        usage = await aa_service.calculate_allowance_usage(test_user.id, '2024/25')

        # Annual allowance should be MPAA (£10,000)
        assert usage['annual_allowance'] == Decimal('10000.00')
        assert usage['mpaa_applies'] == True
        assert usage['total_contributions'] == Decimal('8000.00')


class TestCheckAnnualAllowanceCharge:
    """Tests for annual allowance charge calculation."""

    async def test_no_charge_within_limits(self, aa_service, test_user, test_pension, db_session):
        """Test no charge when within limits."""
        # Add contribution within limits
        contribution = UKPensionContribution(
            id=uuid.uuid4(),
            pension_id=test_pension.id,
            employee_contribution=Decimal('30000.00'),
            frequency=ContributionFrequency.ANNUAL,
            contribution_date=date(2024, 6, 1),
            tax_year='2024/25',
            effective_from=date(2024, 6, 1)
        )
        db_session.add(contribution)
        await db_session.commit()

        charge = await aa_service.check_annual_allowance_charge(
            test_user.id,
            '2024/25',
            marginal_rate=Decimal('0.40')  # 40% marginal rate
        )

        assert charge['charge_applies'] == False
        assert charge['excess_contributions'] == Decimal('0.00')
        assert charge['charge_amount'] == Decimal('0.00')

    async def test_charge_applies_excess_contributions(self, aa_service, test_user, test_pension, db_session):
        """Test charge calculation with excess contributions."""
        # Add contribution exceeding all allowances (including carry forward)
        contribution = UKPensionContribution(
            id=uuid.uuid4(),
            pension_id=test_pension.id,
            employee_contribution=Decimal('200000.00'),
            employer_contribution=Decimal('100000.00'),  # Total: 300k
            frequency=ContributionFrequency.ANNUAL,
            contribution_date=date(2024, 6, 1),
            tax_year='2024/25',
            effective_from=date(2024, 6, 1)
        )
        db_session.add(contribution)
        await db_session.commit()

        # Assuming no carry forward, total available = 60k + 180k carry forward = 240k
        # Excess = 300k - 240k = 60k
        charge = await aa_service.check_annual_allowance_charge(
            test_user.id,
            '2024/25',
            marginal_rate=Decimal('0.40')  # 40% marginal rate
        )

        # Excess: 300000 - 240000 = 60000
        assert charge['charge_applies'] == True
        assert charge['excess_contributions'] == Decimal('60000.00')

        # Charge: 60000 * 0.40 = 24000
        assert charge['charge_amount'] == Decimal('24000.00')
        assert charge['marginal_rate'] == Decimal('0.40')

    async def test_charge_with_higher_marginal_rate(self, aa_service, test_user, test_pension, db_session):
        """Test charge calculation with 45% marginal rate."""
        # Add excess contribution
        contribution = UKPensionContribution(
            id=uuid.uuid4(),
            pension_id=test_pension.id,
            employee_contribution=Decimal('250000.00'),
            frequency=ContributionFrequency.ANNUAL,
            contribution_date=date(2024, 6, 1),
            tax_year='2024/25',
            effective_from=date(2024, 6, 1)
        )
        db_session.add(contribution)
        await db_session.commit()

        charge = await aa_service.check_annual_allowance_charge(
            test_user.id,
            '2024/25',
            marginal_rate=Decimal('0.45')  # 45% marginal rate
        )

        # Excess: 250k - 240k = 10k
        assert charge['charge_applies'] == True
        assert charge['excess_contributions'] == Decimal('10000.00')

        # Charge: 10k * 0.45 = 4.5k
        assert charge['charge_amount'] == Decimal('4500.00')


class TestUpdateAnnualAllowanceTracking:
    """Tests for updating AA tracking records."""

    async def test_create_new_tracking_record(self, aa_service, test_user, test_pension, db_session):
        """Test creating new tracking record."""
        # Add contribution
        contribution = UKPensionContribution(
            id=uuid.uuid4(),
            pension_id=test_pension.id,
            employee_contribution=Decimal('25000.00'),
            frequency=ContributionFrequency.ANNUAL,
            contribution_date=date(2024, 6, 1),
            tax_year='2024/25',
            effective_from=date(2024, 6, 1)
        )
        db_session.add(contribution)
        await db_session.commit()

        # Update tracking
        tracking = await aa_service.update_annual_allowance_tracking(test_user.id, '2024/25')

        assert tracking.id is not None
        assert tracking.user_id == test_user.id
        assert tracking.tax_year == '2024/25'
        assert tracking.total_contributions == Decimal('25000.00')
        assert tracking.annual_allowance_limit == Decimal('60000.00')

    async def test_update_existing_tracking_record(self, aa_service, test_user, test_pension, db_session):
        """Test updating existing tracking record."""
        # Create initial tracking
        initial_tracking = AnnualAllowanceTracking(
            id=uuid.uuid4(),
            user_id=test_user.id,
            tax_year='2024/25',
            total_contributions=Decimal('10000.00'),
            annual_allowance_limit=Decimal('60000.00'),
            allowance_used=Decimal('10000.00'),
            allowance_remaining=Decimal('230000.00'),
            tapered_allowance=False
        )
        db_session.add(initial_tracking)
        await db_session.commit()

        initial_id = initial_tracking.id

        # Add contribution
        contribution = UKPensionContribution(
            id=uuid.uuid4(),
            pension_id=test_pension.id,
            employee_contribution=Decimal('15000.00'),
            frequency=ContributionFrequency.ANNUAL,
            contribution_date=date(2024, 6, 1),
            tax_year='2024/25',
            effective_from=date(2024, 6, 1)
        )
        db_session.add(contribution)
        await db_session.commit()

        # Update tracking
        tracking = await aa_service.update_annual_allowance_tracking(test_user.id, '2024/25')

        # Should update existing record (same ID)
        assert tracking.id == initial_id

        # Should have new contribution included (15000)
        assert tracking.total_contributions == Decimal('15000.00')


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    async def test_carry_forward_invalid_tax_year_format(self, aa_service, test_user):
        """Test carry forward with invalid tax year format."""
        # Invalid format should return empty dict
        carry_forward = await aa_service.calculate_carry_forward(test_user.id, 'invalid')

        assert carry_forward == {}

    async def test_taper_calculation_precision(self, aa_service, test_user):
        """Test tapering calculation precision."""
        # Adjusted income: £260,001 (£1 over threshold)
        # Reduction: £1 / 2 = £0.50
        # Tapered allowance: £60,000 - £0.50 = £59,999.50
        allowance = aa_service.calculate_annual_allowance(
            test_user.id,
            '2024/25',
            adjusted_income=Decimal('260001.00'),
            mpaa_triggered=False
        )

        # Decimal precision should be maintained
        assert allowance == Decimal('59999.50')

    async def test_zero_contributions(self, aa_service, test_user):
        """Test handling of zero contributions."""
        usage = await aa_service.calculate_allowance_usage(test_user.id, '2024/25')

        assert usage['total_contributions'] == Decimal('0.00')
        assert usage['excess'] == Decimal('0.00')
        assert usage['allowance_remaining'] > Decimal('0.00')
