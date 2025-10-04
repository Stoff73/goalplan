"""
Tests for UK pension database models.

This module tests:
- UKPension model creation and validation
- UKPensionContribution with temporal data
- UKPensionDBDetails for DB pensions
- AnnualAllowanceTracking with carry forward
- StatePensionForecast tracking
- Encryption of scheme references
- Relationships and cascades
- Constraints and validations
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models.retirement import (
    UKPension,
    UKPensionContribution,
    UKPensionDBDetails,
    AnnualAllowanceTracking,
    StatePensionForecast,
    PensionType,
    PensionStatus,
    ContributionFrequency,
    TaxReliefMethod,
    DBSchemeType,
    IndexationType,
    InvestmentStrategy,
)
from models.user import User, UserStatus, CountryPreference


@pytest.mark.asyncio
class TestUKPensionModel:
    """Test UKPension model."""

    async def test_create_dc_pension(self, db_session, test_user):
        """Test creating a Defined Contribution pension."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider="Vanguard",
            employer_name=None,
            current_value=Decimal('50000.00'),
            start_date=date(2020, 1, 1),
            expected_retirement_date=date(2050, 1, 1),
            investment_strategy=InvestmentStrategy.BALANCED,
            assumed_growth_rate=Decimal('5.00'),
            assumed_inflation_rate=Decimal('2.50'),
            mpaa_triggered=False,
            status=PensionStatus.ACTIVE
        )
        pension.set_scheme_reference("SIPP123456")

        db_session.add(pension)
        await db_session.commit()
        await db_session.refresh(pension)

        assert pension.id is not None
        assert pension.user_id == test_user.id
        assert pension.pension_type == PensionType.SIPP
        assert pension.provider == "Vanguard"
        assert pension.current_value == Decimal('50000.00')
        assert pension.mpaa_triggered is False
        assert pension.is_deleted is False

    async def test_pension_scheme_reference_encryption(self, db_session, test_user):
        """Test scheme reference is encrypted."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.PERSONAL_PENSION,
            provider="Aviva",
            start_date=date(2015, 1, 1),
            expected_retirement_date=date(2045, 1, 1)
        )

        scheme_ref = "SCHEME-987654321"
        pension.set_scheme_reference(scheme_ref)

        db_session.add(pension)
        await db_session.commit()
        await db_session.refresh(pension)

        # Encrypted value should be different from plain text
        assert pension.scheme_reference_encrypted != scheme_ref

        # Decryption should return original value
        decrypted = pension.get_scheme_reference()
        assert decrypted == scheme_ref

    async def test_create_db_pension(self, db_session, test_user):
        """Test creating a Defined Benefit pension."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.OCCUPATIONAL_DB,
            provider="NHS Pension Scheme",
            employer_name="NHS Trust",
            current_value=None,  # DB pensions don't have current_value
            start_date=date(2010, 1, 1),
            expected_retirement_date=date(2040, 1, 1),
            status=PensionStatus.ACTIVE
        )
        pension.set_scheme_reference("NHS-DB-12345")

        db_session.add(pension)
        await db_session.commit()
        await db_session.refresh(pension)

        assert pension.pension_type == PensionType.OCCUPATIONAL_DB
        assert pension.employer_name == "NHS Trust"
        assert pension.current_value is None

    async def test_mpaa_tracking(self, db_session, test_user):
        """Test MPAA (Money Purchase Annual Allowance) tracking."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider="Hargreaves Lansdown",
            start_date=date(2018, 1, 1),
            expected_retirement_date=date(2048, 1, 1),
            current_value=Decimal('100000.00'),
            mpaa_triggered=True,
            mpaa_date=date(2023, 6, 1)
        )
        pension.set_scheme_reference("HL-SIPP-123")

        db_session.add(pension)
        await db_session.commit()
        await db_session.refresh(pension)

        assert pension.mpaa_triggered is True
        assert pension.mpaa_date == date(2023, 6, 1)

    async def test_pension_value_constraint(self, db_session, test_user):
        """Test current_value must be non-negative."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider="Test Provider",
            current_value=Decimal('-1000.00'),  # Invalid negative value
            start_date=date(2020, 1, 1),
            expected_retirement_date=date(2050, 1, 1)
        )
        pension.set_scheme_reference("TEST-123")

        db_session.add(pension)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert "check_uk_pension_non_negative_value" in str(exc_info.value)
        await db_session.rollback()

    async def test_retirement_date_constraint(self, db_session, test_user):
        """Test expected_retirement_date must be after start_date."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider="Test Provider",
            current_value=Decimal('10000.00'),
            start_date=date(2025, 1, 1),
            expected_retirement_date=date(2020, 1, 1)  # Invalid: before start
        )
        pension.set_scheme_reference("TEST-456")

        db_session.add(pension)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert "check_uk_pension_valid_retirement_date" in str(exc_info.value)
        await db_session.rollback()

    async def test_calculate_projected_value(self, db_session, test_user):
        """Test projected value calculation for DC pensions."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider="Vanguard",
            current_value=Decimal('100000.00'),
            start_date=date(2020, 1, 1),
            expected_retirement_date=date(2040, 1, 1),
            assumed_growth_rate=Decimal('5.00')
        )
        pension.set_scheme_reference("VG-SIPP-789")

        db_session.add(pension)
        await db_session.commit()

        # Calculate projected value (simplified, doesn't include contributions)
        projected = pension.calculate_projected_value()

        # Should be greater than current value due to growth
        assert projected is not None
        assert projected > pension.current_value

    async def test_calculate_projected_value_db_pension(self, db_session, test_user):
        """Test projected value is None for DB pensions."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.OCCUPATIONAL_DB,
            provider="Civil Service Pension",
            employer_name="Government",
            start_date=date(2010, 1, 1),
            expected_retirement_date=date(2040, 1, 1)
        )
        pension.set_scheme_reference("CIVIL-DB-456")

        db_session.add(pension)
        await db_session.commit()

        # DB pensions don't have projected values
        projected = pension.calculate_projected_value()
        assert projected is None

    async def test_soft_delete(self, db_session, test_user):
        """Test soft delete functionality."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider="Test Provider",
            current_value=Decimal('25000.00'),
            start_date=date(2020, 1, 1),
            expected_retirement_date=date(2050, 1, 1)
        )
        pension.set_scheme_reference("TEST-SOFT-DELETE")

        db_session.add(pension)
        await db_session.commit()
        await db_session.refresh(pension)

        pension_id = pension.id

        # Soft delete
        pension.is_deleted = True
        await db_session.commit()

        # Pension still exists in database but marked deleted
        result = await db_session.execute(
            select(UKPension).where(UKPension.id == pension_id)
        )
        deleted_pension = result.scalar_one()
        assert deleted_pension.is_deleted is True


@pytest.mark.asyncio
class TestUKPensionContributionModel:
    """Test UKPensionContribution model with temporal data."""

    async def test_create_contribution(self, db_session, test_user):
        """Test creating a pension contribution record."""
        # Create pension first
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.OCCUPATIONAL_DC,
            provider="Nest",
            employer_name="Acme Corp",
            current_value=Decimal('30000.00'),
            start_date=date(2020, 1, 1),
            expected_retirement_date=date(2050, 1, 1)
        )
        pension.set_scheme_reference("NEST-12345")
        db_session.add(pension)
        await db_session.commit()

        # Create contribution
        contribution = UKPensionContribution(
            pension_id=pension.id,
            employee_contribution=Decimal('200.00'),
            employer_contribution=Decimal('150.00'),
            personal_contribution=Decimal('0.00'),
            frequency=ContributionFrequency.MONTHLY,
            tax_relief_method=TaxReliefMethod.NET_PAY,
            contribution_date=date(2024, 10, 1),
            tax_year='2024/25',
            effective_from=date(2024, 10, 1),
            effective_to=None  # Current contribution
        )

        db_session.add(contribution)
        await db_session.commit()
        await db_session.refresh(contribution)

        assert contribution.id is not None
        assert contribution.pension_id == pension.id
        assert contribution.employee_contribution == Decimal('200.00')
        assert contribution.employer_contribution == Decimal('150.00')
        assert contribution.total_contribution == Decimal('350.00')
        assert contribution.frequency == ContributionFrequency.MONTHLY
        assert contribution.tax_year == '2024/25'

    async def test_contribution_temporal_data(self, db_session, test_user):
        """Test temporal data support with effective_from/effective_to."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider="Vanguard",
            current_value=Decimal('40000.00'),
            start_date=date(2020, 1, 1),
            expected_retirement_date=date(2050, 1, 1)
        )
        pension.set_scheme_reference("VG-TEMPORAL-123")
        db_session.add(pension)
        await db_session.commit()

        # Old contribution (historical)
        old_contribution = UKPensionContribution(
            pension_id=pension.id,
            personal_contribution=Decimal('300.00'),
            frequency=ContributionFrequency.MONTHLY,
            contribution_date=date(2023, 1, 1),
            tax_year='2023/24',
            effective_from=date(2023, 1, 1),
            effective_to=date(2024, 3, 31)  # Ended
        )

        # New contribution (current)
        new_contribution = UKPensionContribution(
            pension_id=pension.id,
            personal_contribution=Decimal('400.00'),
            frequency=ContributionFrequency.MONTHLY,
            contribution_date=date(2024, 4, 1),
            tax_year='2024/25',
            effective_from=date(2024, 4, 1),
            effective_to=None  # Current
        )

        db_session.add_all([old_contribution, new_contribution])
        await db_session.commit()

        # Query current contribution (effective_to IS NULL)
        result = await db_session.execute(
            select(UKPensionContribution)
            .where(
                UKPensionContribution.pension_id == pension.id,
                UKPensionContribution.effective_to.is_(None)
            )
        )
        current = result.scalar_one()
        assert current.personal_contribution == Decimal('400.00')

    async def test_tax_year_validation(self, db_session, test_user):
        """Test tax year format validation."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider="Test Provider",
            current_value=Decimal('10000.00'),
            start_date=date(2020, 1, 1),
            expected_retirement_date=date(2050, 1, 1)
        )
        pension.set_scheme_reference("TEST-TAX-YEAR")
        db_session.add(pension)
        await db_session.commit()

        # Invalid tax year format - should raise during object creation
        with pytest.raises(ValueError) as exc_info:
            contribution = UKPensionContribution(
                pension_id=pension.id,
                personal_contribution=Decimal('100.00'),
                frequency=ContributionFrequency.MONTHLY,
                contribution_date=date(2024, 10, 1),
                tax_year='2024-2025',  # Invalid format (should be 2024/25)
                effective_from=date(2024, 10, 1)
            )

        assert "Invalid UK tax year format" in str(exc_info.value)

    async def test_negative_contribution_constraint(self, db_session, test_user):
        """Test contributions cannot be negative."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider="Test Provider",
            current_value=Decimal('10000.00'),
            start_date=date(2020, 1, 1),
            expected_retirement_date=date(2050, 1, 1)
        )
        pension.set_scheme_reference("TEST-NEG-CONTRIB")
        db_session.add(pension)
        await db_session.commit()

        contribution = UKPensionContribution(
            pension_id=pension.id,
            employee_contribution=Decimal('-100.00'),  # Invalid
            frequency=ContributionFrequency.MONTHLY,
            contribution_date=date(2024, 10, 1),
            tax_year='2024/25',
            effective_from=date(2024, 10, 1)
        )

        db_session.add(contribution)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert "check_contribution_non_negative_employee" in str(exc_info.value)
        await db_session.rollback()


@pytest.mark.asyncio
class TestUKPensionDBDetailsModel:
    """Test UKPensionDBDetails model."""

    async def test_create_db_details(self, db_session, test_user):
        """Test creating DB pension details."""
        # Create DB pension
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.OCCUPATIONAL_DB,
            provider="Teachers' Pension Scheme",
            employer_name="Local Education Authority",
            start_date=date(2010, 1, 1),
            expected_retirement_date=date(2038, 1, 1)
        )
        pension.set_scheme_reference("TEACHERS-DB-789")
        db_session.add(pension)
        await db_session.commit()

        # Create DB details
        db_details = UKPensionDBDetails(
            pension_id=pension.id,
            accrual_rate='1/60',
            pensionable_service_years=Decimal('15.50'),
            scheme_type=DBSchemeType.CAREER_AVERAGE,
            normal_retirement_age=65,
            guaranteed_pension_amount=Decimal('20000.00'),
            spouse_pension_percentage=Decimal('50.00'),
            lump_sum_entitlement=Decimal('60000.00'),
            indexation_type=IndexationType.CPI
        )

        db_session.add(db_details)
        await db_session.commit()
        await db_session.refresh(db_details)

        assert db_details.id is not None
        assert db_details.pension_id == pension.id
        assert db_details.accrual_rate == '1/60'
        assert db_details.pensionable_service_years == Decimal('15.50')
        assert db_details.scheme_type == DBSchemeType.CAREER_AVERAGE
        assert db_details.spouse_pension_percentage == Decimal('50.00')

    async def test_accrual_rate_validation(self, db_session, test_user):
        """Test accrual rate format validation."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.OCCUPATIONAL_DB,
            provider="Test DB Scheme",
            employer_name="Test Employer",
            start_date=date(2010, 1, 1),
            expected_retirement_date=date(2040, 1, 1)
        )
        pension.set_scheme_reference("TEST-ACCRUAL")
        db_session.add(pension)
        await db_session.commit()

        # Invalid accrual rate format - should raise during object creation
        with pytest.raises(ValueError) as exc_info:
            db_details = UKPensionDBDetails(
                pension_id=pension.id,
                accrual_rate='60',  # Invalid (should be '1/60')
                pensionable_service_years=Decimal('10.00'),
                scheme_type=DBSchemeType.FINAL_SALARY,
                normal_retirement_age=65,
                indexation_type=IndexationType.RPI
            )

        assert "Invalid accrual rate format" in str(exc_info.value)

    async def test_retirement_age_constraint(self, db_session, test_user):
        """Test normal retirement age must be >= 55."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.OCCUPATIONAL_DB,
            provider="Test DB Scheme",
            employer_name="Test Employer",
            start_date=date(2010, 1, 1),
            expected_retirement_date=date(2040, 1, 1)
        )
        pension.set_scheme_reference("TEST-RETIRE-AGE")
        db_session.add(pension)
        await db_session.commit()

        db_details = UKPensionDBDetails(
            pension_id=pension.id,
            accrual_rate='1/80',
            pensionable_service_years=Decimal('20.00'),
            scheme_type=DBSchemeType.FINAL_SALARY,
            normal_retirement_age=50,  # Invalid (below 55)
            indexation_type=IndexationType.CPI
        )

        db_session.add(db_details)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert "check_db_valid_retirement_age" in str(exc_info.value)
        await db_session.rollback()


@pytest.mark.asyncio
class TestAnnualAllowanceTrackingModel:
    """Test AnnualAllowanceTracking model."""

    async def test_create_annual_allowance_tracking(self, db_session, test_user):
        """Test creating annual allowance tracking record."""
        aa_tracking = AnnualAllowanceTracking(
            user_id=test_user.id,
            tax_year='2024/25',
            total_contributions=Decimal('45000.00'),
            annual_allowance_limit=Decimal('60000.00'),
            carry_forward_available={'2023/24': 15000, '2022/23': 10000, '2021/22': 5000},
            tapered_allowance=False,
            allowance_used=Decimal('45000.00'),
            allowance_remaining=Decimal('15000.00')
        )

        db_session.add(aa_tracking)
        await db_session.commit()
        await db_session.refresh(aa_tracking)

        assert aa_tracking.id is not None
        assert aa_tracking.user_id == test_user.id
        assert aa_tracking.tax_year == '2024/25'
        assert aa_tracking.total_contributions == Decimal('45000.00')
        assert aa_tracking.annual_allowance_limit == Decimal('60000.00')
        assert aa_tracking.tapered_allowance is False

    async def test_tapered_annual_allowance(self, db_session, test_user):
        """Test tapered annual allowance for high earners."""
        aa_tracking = AnnualAllowanceTracking(
            user_id=test_user.id,
            tax_year='2024/25',
            total_contributions=Decimal('30000.00'),
            annual_allowance_limit=Decimal('40000.00'),  # Tapered down
            tapered_allowance=True,
            adjusted_income=Decimal('280000.00'),  # High earner
            allowance_used=Decimal('30000.00'),
            allowance_remaining=Decimal('10000.00')
        )

        db_session.add(aa_tracking)
        await db_session.commit()
        await db_session.refresh(aa_tracking)

        assert aa_tracking.tapered_allowance is True
        assert aa_tracking.adjusted_income == Decimal('280000.00')
        assert aa_tracking.annual_allowance_limit == Decimal('40000.00')

    async def test_calculate_excess(self, db_session, test_user):
        """Test excess contribution calculation."""
        aa_tracking = AnnualAllowanceTracking(
            user_id=test_user.id,
            tax_year='2024/25',
            total_contributions=Decimal('75000.00'),
            annual_allowance_limit=Decimal('60000.00'),
            allowance_used=Decimal('60000.00'),
            allowance_remaining=Decimal('0.00')
        )

        db_session.add(aa_tracking)
        await db_session.commit()

        # Calculate excess
        excess = aa_tracking.calculate_excess()
        assert excess == Decimal('75000.00')

    async def test_unique_user_tax_year(self, db_session, test_user):
        """Test user can only have one AA record per tax year."""
        aa_tracking1 = AnnualAllowanceTracking(
            user_id=test_user.id,
            tax_year='2024/25',
            total_contributions=Decimal('30000.00'),
            annual_allowance_limit=Decimal('60000.00'),
            allowance_used=Decimal('30000.00'),
            allowance_remaining=Decimal('30000.00')
        )

        db_session.add(aa_tracking1)
        await db_session.commit()

        # Try to create duplicate for same tax year
        aa_tracking2 = AnnualAllowanceTracking(
            user_id=test_user.id,
            tax_year='2024/25',  # Duplicate
            total_contributions=Decimal('40000.00'),
            annual_allowance_limit=Decimal('60000.00'),
            allowance_used=Decimal('40000.00'),
            allowance_remaining=Decimal('20000.00')
        )

        db_session.add(aa_tracking2)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert "idx_aa_user_tax_year" in str(exc_info.value) or "unique" in str(exc_info.value).lower()
        await db_session.rollback()


@pytest.mark.asyncio
class TestStatePensionForecastModel:
    """Test StatePensionForecast model."""

    async def test_create_state_pension_forecast(self, db_session, test_user):
        """Test creating State Pension forecast."""
        forecast = StatePensionForecast(
            user_id=test_user.id,
            forecast_date=date(2024, 10, 1),
            qualifying_years=25,
            years_needed_for_full=35,
            estimated_weekly_amount=Decimal('168.60'),
            estimated_annual_amount=Decimal('8767.20'),
            state_pension_age=67
        )

        db_session.add(forecast)
        await db_session.commit()
        await db_session.refresh(forecast)

        assert forecast.id is not None
        assert forecast.user_id == test_user.id
        assert forecast.qualifying_years == 25
        assert forecast.years_needed_for_full == 35
        assert forecast.state_pension_age == 67

    async def test_years_to_full_pension(self, db_session, test_user):
        """Test calculation of years remaining to full pension."""
        forecast = StatePensionForecast(
            user_id=test_user.id,
            forecast_date=date(2024, 10, 1),
            qualifying_years=30,
            years_needed_for_full=35,
            estimated_weekly_amount=Decimal('180.00'),
            estimated_annual_amount=Decimal('9360.00'),
            state_pension_age=67
        )

        db_session.add(forecast)
        await db_session.commit()

        # Years to full pension
        years_remaining = forecast.years_to_full_pension
        assert years_remaining == 5

    async def test_one_forecast_per_user(self, db_session, test_user):
        """Test user can only have one State Pension forecast."""
        forecast1 = StatePensionForecast(
            user_id=test_user.id,
            forecast_date=date(2024, 10, 1),
            qualifying_years=25,
            years_needed_for_full=35,
            estimated_weekly_amount=Decimal('168.60'),
            estimated_annual_amount=Decimal('8767.20'),
            state_pension_age=67
        )

        db_session.add(forecast1)
        await db_session.commit()

        # Try to create duplicate
        forecast2 = StatePensionForecast(
            user_id=test_user.id,  # Same user
            forecast_date=date(2024, 11, 1),
            qualifying_years=26,
            years_needed_for_full=35,
            estimated_weekly_amount=Decimal('173.40'),
            estimated_annual_amount=Decimal('9016.80'),
            state_pension_age=67
        )

        db_session.add(forecast2)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert "unique" in str(exc_info.value).lower() or "user_id" in str(exc_info.value)
        await db_session.rollback()


@pytest.mark.asyncio
class TestRelationshipsAndCascades:
    """Test relationships and cascade deletes."""

    async def test_user_pension_relationship(self, db_session, test_user):
        """Test User to UKPension relationship."""
        pension1 = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider="Provider 1",
            current_value=Decimal('50000.00'),
            start_date=date(2020, 1, 1),
            expected_retirement_date=date(2050, 1, 1)
        )
        pension1.set_scheme_reference("SCHEME-1")

        pension2 = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.PERSONAL_PENSION,
            provider="Provider 2",
            current_value=Decimal('30000.00'),
            start_date=date(2018, 1, 1),
            expected_retirement_date=date(2048, 1, 1)
        )
        pension2.set_scheme_reference("SCHEME-2")

        db_session.add_all([pension1, pension2])
        await db_session.commit()

        # Query pensions for this user
        result = await db_session.execute(
            select(UKPension).where(UKPension.user_id == test_user.id)
        )
        pensions = result.scalars().all()

        # User should have 2 pensions
        assert len(pensions) == 2

    async def test_pension_contribution_cascade(self, db_session, test_user):
        """Test cascade delete from pension to contributions."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.SIPP,
            provider="Test Provider",
            current_value=Decimal('40000.00'),
            start_date=date(2020, 1, 1),
            expected_retirement_date=date(2050, 1, 1)
        )
        pension.set_scheme_reference("CASCADE-TEST")
        db_session.add(pension)
        await db_session.commit()

        # Add contributions
        contribution1 = UKPensionContribution(
            pension_id=pension.id,
            personal_contribution=Decimal('300.00'),
            frequency=ContributionFrequency.MONTHLY,
            contribution_date=date(2024, 1, 1),
            tax_year='2024/25',
            effective_from=date(2024, 1, 1)
        )
        contribution2 = UKPensionContribution(
            pension_id=pension.id,
            personal_contribution=Decimal('350.00'),
            frequency=ContributionFrequency.MONTHLY,
            contribution_date=date(2024, 6, 1),
            tax_year='2024/25',
            effective_from=date(2024, 6, 1)
        )
        db_session.add_all([contribution1, contribution2])
        await db_session.commit()

        pension_id = pension.id

        # Delete pension
        await db_session.delete(pension)
        await db_session.commit()

        # Contributions should be deleted (cascade)
        result = await db_session.execute(
            select(UKPensionContribution).where(UKPensionContribution.pension_id == pension_id)
        )
        contributions = result.scalars().all()
        assert len(contributions) == 0

    async def test_pension_db_details_cascade(self, db_session, test_user):
        """Test cascade delete from pension to DB details."""
        pension = UKPension(
            user_id=test_user.id,
            pension_type=PensionType.OCCUPATIONAL_DB,
            provider="Test DB Provider",
            employer_name="Test Employer",
            start_date=date(2010, 1, 1),
            expected_retirement_date=date(2040, 1, 1)
        )
        pension.set_scheme_reference("DB-CASCADE-TEST")
        db_session.add(pension)
        await db_session.commit()

        # Add DB details
        db_details = UKPensionDBDetails(
            pension_id=pension.id,
            accrual_rate='1/60',
            pensionable_service_years=Decimal('15.00'),
            scheme_type=DBSchemeType.FINAL_SALARY,
            normal_retirement_age=65,
            indexation_type=IndexationType.CPI
        )
        db_session.add(db_details)
        await db_session.commit()

        pension_id = pension.id

        # Delete pension
        await db_session.delete(pension)
        await db_session.commit()

        # DB details should be deleted (cascade)
        result = await db_session.execute(
            select(UKPensionDBDetails).where(UKPensionDBDetails.pension_id == pension_id)
        )
        details = result.scalar_one_or_none()
        assert details is None
