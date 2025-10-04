"""
Tests for UK Pension Service

Tests comprehensive pension CRUD operations including:
- Pension creation with encryption
- Pension updates with ownership validation
- Soft delete functionality
- Contribution tracking
- DC value calculation with growth
- DB value calculation
- Total pot aggregation
- Error handling and edge cases

Target: >85% coverage
"""

import pytest
import uuid
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import select

from models.retirement import (
    UKPension, UKPensionContribution, UKPensionDBDetails,
    PensionType, PensionStatus, ContributionFrequency,
    TaxReliefMethod, DBSchemeType, IndexationType,
    InvestmentStrategy
)
from models.user import User, UserStatus
from services.retirement import (
    UKPensionService,
    ValidationError,
    NotFoundError,
    PermissionError
)



@pytest.fixture
async def pension_service(db_session):
    """Create UK Pension service instance."""
    return UKPensionService(db_session)


class TestCreatePension:
    """Tests for pension creation."""

    async def test_create_dc_pension_success(self, pension_service, test_user):
        """Test successful DC pension creation."""
        pension_data = {
            'pension_type': PensionType.OCCUPATIONAL_DC,
            'provider': 'Test Provider',
            'scheme_reference': 'SCHEME123',
            'employer_name': 'Test Employer',
            'current_value': Decimal('50000.00'),
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2050, 1, 1),
            'investment_strategy': InvestmentStrategy.BALANCED,
            'assumed_growth_rate': Decimal('5.00'),
            'assumed_inflation_rate': Decimal('2.50'),
            'mpaa_triggered': False
        }

        pension = await pension_service.create_pension(test_user.id, pension_data)

        assert pension.id is not None
        assert pension.user_id == test_user.id
        assert pension.pension_type == PensionType.OCCUPATIONAL_DC
        assert pension.provider == 'Test Provider'
        assert pension.current_value == Decimal('50000.00')
        assert pension.status == PensionStatus.ACTIVE
        assert pension.is_deleted == False

        # Verify scheme reference is encrypted
        assert pension.scheme_reference_encrypted != 'SCHEME123'

        # Verify can decrypt
        decrypted = pension.get_scheme_reference()
        assert decrypted == 'SCHEME123'

    async def test_create_db_pension_with_details(self, pension_service, test_user):
        """Test DB pension creation with DB details."""
        pension_data = {
            'pension_type': PensionType.OCCUPATIONAL_DB,
            'provider': 'DB Provider',
            'scheme_reference': 'DB123',
            'employer_name': 'DB Employer',
            'start_date': date(2015, 1, 1),
            'expected_retirement_date': date(2045, 1, 1),
            'db_details': {
                'accrual_rate': '1/60',
                'pensionable_service_years': Decimal('10.50'),
                'scheme_type': DBSchemeType.FINAL_SALARY,
                'normal_retirement_age': 65,
                'guaranteed_pension_amount': Decimal('15000.00'),
                'spouse_pension_percentage': Decimal('50.00'),
                'lump_sum_entitlement': Decimal('45000.00'),
                'indexation_type': IndexationType.CPI
            }
        }

        pension = await pension_service.create_pension(test_user.id, pension_data)

        assert pension.pension_type == PensionType.OCCUPATIONAL_DB

        # Verify DB details were created (query explicitly to avoid lazy loading issue)
        from sqlalchemy import select
        result = await pension_service.db.execute(
            select(UKPensionDBDetails).where(UKPensionDBDetails.pension_id == pension.id)
        )
        db_details = result.scalar_one_or_none()

        assert db_details is not None
        assert db_details.accrual_rate == '1/60'
        assert db_details.pensionable_service_years == Decimal('10.50')
        assert db_details.guaranteed_pension_amount == Decimal('15000.00')

    async def test_create_pension_missing_required_field(self, pension_service, test_user):
        """Test pension creation with missing required field."""
        pension_data = {
            'pension_type': PensionType.OCCUPATIONAL_DC,
            'provider': 'Test Provider',
            # Missing scheme_reference
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2050, 1, 1)
        }

        with pytest.raises(ValidationError, match="Missing required field: scheme_reference"):
            await pension_service.create_pension(test_user.id, pension_data)

    async def test_create_pension_invalid_dates(self, pension_service, test_user):
        """Test pension creation with invalid dates."""
        pension_data = {
            'pension_type': PensionType.OCCUPATIONAL_DC,
            'provider': 'Test Provider',
            'scheme_reference': 'SCHEME123',
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2019, 1, 1)  # Before start date
        }

        with pytest.raises(ValidationError, match="Expected retirement date must be after start date"):
            await pension_service.create_pension(test_user.id, pension_data)

    async def test_create_pension_negative_value(self, pension_service, test_user):
        """Test pension creation with negative current value."""
        pension_data = {
            'pension_type': PensionType.OCCUPATIONAL_DC,
            'provider': 'Test Provider',
            'scheme_reference': 'SCHEME123',
            'current_value': Decimal('-1000.00'),  # Negative
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2050, 1, 1)
        }

        with pytest.raises(ValidationError, match="Current value cannot be negative"):
            await pension_service.create_pension(test_user.id, pension_data)


class TestUpdatePension:
    """Tests for pension updates."""

    async def test_update_pension_success(self, pension_service, test_user, db_session):
        """Test successful pension update."""
        # Create pension
        pension_data = {
            'pension_type': PensionType.SIPP,
            'provider': 'Original Provider',
            'scheme_reference': 'SCHEME123',
            'current_value': Decimal('10000.00'),
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2050, 1, 1)
        }
        pension = await pension_service.create_pension(test_user.id, pension_data)

        # Update pension
        updates = {
            'provider': 'Updated Provider',
            'current_value': Decimal('12000.00')
        }
        updated_pension = await pension_service.update_pension(pension.id, test_user.id, updates)

        assert updated_pension.provider == 'Updated Provider'
        assert updated_pension.current_value == Decimal('12000.00')

    async def test_update_pension_not_found(self, pension_service, test_user):
        """Test update non-existent pension."""
        fake_id = uuid.uuid4()
        updates = {'provider': 'New Provider'}

        with pytest.raises(NotFoundError, match=f"Pension not found: {fake_id}"):
            await pension_service.update_pension(fake_id, test_user.id, updates)

    async def test_update_pension_wrong_user(self, pension_service, test_user, db_session):
        """Test update pension by non-owner."""
        # Create pension for test_user
        pension_data = {
            'pension_type': PensionType.SIPP,
            'provider': 'Provider',
            'scheme_reference': 'SCHEME123',
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2050, 1, 1)
        }
        pension = await pension_service.create_pension(test_user.id, pension_data)

        # Try to update as different user
        other_user_id = uuid.uuid4()
        updates = {'provider': 'Hacked Provider'}

        with pytest.raises(PermissionError, match="does not own pension"):
            await pension_service.update_pension(pension.id, other_user_id, updates)


class TestDeletePension:
    """Tests for pension deletion."""

    async def test_delete_pension_success(self, pension_service, test_user, db_session):
        """Test successful soft delete."""
        # Create pension
        pension_data = {
            'pension_type': PensionType.PERSONAL_PENSION,
            'provider': 'Provider',
            'scheme_reference': 'SCHEME123',
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2050, 1, 1)
        }
        pension = await pension_service.create_pension(test_user.id, pension_data)

        # Delete pension
        result = await pension_service.delete_pension(pension.id, test_user.id)

        assert result['success'] == True

        # Verify soft delete
        await db_session.refresh(pension)
        assert pension.is_deleted == True
        assert pension.status == PensionStatus.TRANSFERRED_OUT

    async def test_delete_pension_not_found(self, pension_service, test_user):
        """Test delete non-existent pension."""
        fake_id = uuid.uuid4()

        with pytest.raises(NotFoundError):
            await pension_service.delete_pension(fake_id, test_user.id)

    async def test_delete_pension_wrong_user(self, pension_service, test_user, db_session):
        """Test delete pension by non-owner."""
        # Create pension
        pension_data = {
            'pension_type': PensionType.SIPP,
            'provider': 'Provider',
            'scheme_reference': 'SCHEME123',
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2050, 1, 1)
        }
        pension = await pension_service.create_pension(test_user.id, pension_data)

        # Try to delete as different user
        other_user_id = uuid.uuid4()

        with pytest.raises(PermissionError):
            await pension_service.delete_pension(pension.id, other_user_id)


class TestAddContribution:
    """Tests for adding contributions."""

    async def test_add_contribution_success(self, pension_service, test_user):
        """Test successful contribution addition."""
        # Create pension
        pension_data = {
            'pension_type': PensionType.SIPP,
            'provider': 'Provider',
            'scheme_reference': 'SCHEME123',
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2050, 1, 1)
        }
        pension = await pension_service.create_pension(test_user.id, pension_data)

        # Add contribution
        contribution_data = {
            'employee_contribution': Decimal('500.00'),
            'employer_contribution': Decimal('500.00'),
            'personal_contribution': Decimal('0.00'),
            'frequency': ContributionFrequency.MONTHLY,
            'tax_relief_method': TaxReliefMethod.NET_PAY,
            'contribution_date': date(2024, 10, 1),
            'tax_year': '2024/25',
            'effective_from': date(2024, 10, 1),
            'effective_to': None
        }

        contribution = await pension_service.add_contribution(
            pension.id,
            test_user.id,
            contribution_data
        )

        assert contribution.id is not None
        assert contribution.pension_id == pension.id
        assert contribution.employee_contribution == Decimal('500.00')
        assert contribution.employer_contribution == Decimal('500.00')
        assert contribution.total_contribution == Decimal('1000.00')
        assert contribution.tax_year == '2024/25'

    async def test_add_contribution_negative_amounts(self, pension_service, test_user):
        """Test contribution with negative amounts."""
        # Create pension
        pension_data = {
            'pension_type': PensionType.SIPP,
            'provider': 'Provider',
            'scheme_reference': 'SCHEME123',
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2050, 1, 1)
        }
        pension = await pension_service.create_pension(test_user.id, pension_data)

        # Try to add negative contribution
        contribution_data = {
            'employee_contribution': Decimal('-500.00'),  # Negative
            'frequency': ContributionFrequency.MONTHLY,
            'contribution_date': date(2024, 10, 1),
            'tax_year': '2024/25',
            'effective_from': date(2024, 10, 1)
        }

        with pytest.raises(ValidationError, match="Contribution amounts cannot be negative"):
            await pension_service.add_contribution(pension.id, test_user.id, contribution_data)


class TestCalculateCurrentValueDC:
    """Tests for DC value calculation."""

    async def test_calculate_dc_value_with_growth(self, pension_service, test_user):
        """Test DC value calculation with growth."""
        # Create pension with starting value and growth rate
        pension_data = {
            'pension_type': PensionType.OCCUPATIONAL_DC,
            'provider': 'Provider',
            'scheme_reference': 'SCHEME123',
            'current_value': Decimal('10000.00'),
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2050, 1, 1),
            'assumed_growth_rate': Decimal('5.00')  # 5% annual growth
        }
        pension = await pension_service.create_pension(test_user.id, pension_data)

        # Calculate current value (4+ years of growth from 2020 to 2024)
        current_value = await pension_service.calculate_current_value_dc(pension.id, test_user.id)

        # Should be > original value due to growth
        assert current_value > Decimal('10000.00')
        # Roughly 10000 * 1.05^4.75 ≈ 12,600
        assert current_value > Decimal('12000.00')

    async def test_calculate_dc_value_with_contributions(self, pension_service, test_user):
        """Test DC value calculation with contributions."""
        # Create pension
        pension_data = {
            'pension_type': PensionType.SIPP,
            'provider': 'Provider',
            'scheme_reference': 'SCHEME123',
            'current_value': Decimal('5000.00'),
            'start_date': date(2023, 1, 1),
            'expected_retirement_date': date(2050, 1, 1),
            'assumed_growth_rate': Decimal('5.00')
        }
        pension = await pension_service.create_pension(test_user.id, pension_data)

        # Add contribution
        contribution_data = {
            'employee_contribution': Decimal('1000.00'),
            'frequency': ContributionFrequency.ONE_OFF,
            'contribution_date': date(2023, 6, 1),
            'tax_year': '2023/24',
            'effective_from': date(2023, 6, 1)
        }
        await pension_service.add_contribution(pension.id, test_user.id, contribution_data)

        # Calculate value
        current_value = await pension_service.calculate_current_value_dc(pension.id, test_user.id)

        # Should include contribution + growth
        assert current_value > Decimal('6000.00')

    async def test_calculate_dc_value_db_pension_returns_none(self, pension_service, test_user):
        """Test DC calculation on DB pension returns None."""
        # Create DB pension
        pension_data = {
            'pension_type': PensionType.OCCUPATIONAL_DB,
            'provider': 'Provider',
            'scheme_reference': 'SCHEME123',
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2050, 1, 1),
            'db_details': {
                'accrual_rate': '1/60',
                'pensionable_service_years': Decimal('10.00'),
                'scheme_type': DBSchemeType.FINAL_SALARY,
                'normal_retirement_age': 65
            }
        }
        pension = await pension_service.create_pension(test_user.id, pension_data)

        # Should return None for DB pension
        current_value = await pension_service.calculate_current_value_dc(pension.id, test_user.id)
        assert current_value is None


class TestCalculateDBValue:
    """Tests for DB value calculation."""

    async def test_calculate_db_value_with_guaranteed_amount(self, pension_service, test_user):
        """Test DB value with guaranteed pension amount."""
        # Create DB pension with guaranteed amount
        pension_data = {
            'pension_type': PensionType.OCCUPATIONAL_DB,
            'provider': 'Provider',
            'scheme_reference': 'SCHEME123',
            'start_date': date(2010, 1, 1),
            'expected_retirement_date': date(2040, 1, 1),
            'db_details': {
                'accrual_rate': '1/60',
                'pensionable_service_years': Decimal('15.00'),
                'scheme_type': DBSchemeType.FINAL_SALARY,
                'normal_retirement_age': 65,
                'guaranteed_pension_amount': Decimal('20000.00')  # £20k annual pension
            }
        }
        pension = await pension_service.create_pension(test_user.id, pension_data)

        # Calculate transfer value
        transfer_value = await pension_service.calculate_db_value(pension.id, test_user.id)

        # Should be ~20x annual pension = £400k
        assert transfer_value == Decimal('400000.00')

    async def test_calculate_db_value_dc_pension_returns_none(self, pension_service, test_user):
        """Test DB calculation on DC pension returns None."""
        # Create DC pension
        pension_data = {
            'pension_type': PensionType.SIPP,
            'provider': 'Provider',
            'scheme_reference': 'SCHEME123',
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2050, 1, 1)
        }
        pension = await pension_service.create_pension(test_user.id, pension_data)

        # Should return None for DC pension
        transfer_value = await pension_service.calculate_db_value(pension.id, test_user.id)
        assert transfer_value is None


class TestGetTotalPensionPot:
    """Tests for total pension pot aggregation."""

    async def test_total_pot_multiple_pensions(self, pension_service, test_user):
        """Test total pot calculation with multiple pensions."""
        # Create DC pension 1
        pension_data_1 = {
            'pension_type': PensionType.SIPP,
            'provider': 'Provider 1',
            'scheme_reference': 'SCHEME1',
            'current_value': Decimal('50000.00'),
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2050, 1, 1),
            'assumed_growth_rate': Decimal('0.00')  # No growth for simplicity
        }
        await pension_service.create_pension(test_user.id, pension_data_1)

        # Create DC pension 2
        pension_data_2 = {
            'pension_type': PensionType.OCCUPATIONAL_DC,
            'provider': 'Provider 2',
            'scheme_reference': 'SCHEME2',
            'current_value': Decimal('30000.00'),
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2050, 1, 1),
            'assumed_growth_rate': Decimal('0.00')
        }
        await pension_service.create_pension(test_user.id, pension_data_2)

        # Create DB pension
        pension_data_3 = {
            'pension_type': PensionType.OCCUPATIONAL_DB,
            'provider': 'DB Provider',
            'scheme_reference': 'SCHEME3',
            'start_date': date(2010, 1, 1),
            'expected_retirement_date': date(2040, 1, 1),
            'db_details': {
                'accrual_rate': '1/60',
                'pensionable_service_years': Decimal('10.00'),
                'scheme_type': DBSchemeType.FINAL_SALARY,
                'normal_retirement_age': 65,
                'guaranteed_pension_amount': Decimal('10000.00')  # £10k annual
            }
        }
        await pension_service.create_pension(test_user.id, pension_data_3)

        # Get total pot
        total = await pension_service.get_total_pension_pot(test_user.id)

        # DC total should be 50000 + 30000 = 80000
        assert total['dc_total'] == Decimal('80000.00')

        # DB total should be 10000 * 20 = 200000
        assert total['db_total'] == Decimal('200000.00')

        # Total pot = 80000 + 200000 = 280000
        assert total['total_pot'] == Decimal('280000.00')

        # Should have 3 pensions in breakdown
        assert len(total['breakdown']) == 3

    async def test_total_pot_no_pensions(self, pension_service, test_user):
        """Test total pot with no pensions."""
        total = await pension_service.get_total_pension_pot(test_user.id)

        assert total['total_pot'] == Decimal('0.00')
        assert total['dc_total'] == Decimal('0.00')
        assert total['db_total'] == Decimal('0.00')
        assert len(total['breakdown']) == 0


class TestEncryption:
    """Tests for scheme reference encryption."""

    async def test_scheme_reference_encrypted(self, pension_service, test_user, db_session):
        """Test that scheme reference is encrypted in database."""
        # Create pension
        pension_data = {
            'pension_type': PensionType.SIPP,
            'provider': 'Provider',
            'scheme_reference': 'SENSITIVE123',
            'start_date': date(2020, 1, 1),
            'expected_retirement_date': date(2050, 1, 1)
        }
        pension = await pension_service.create_pension(test_user.id, pension_data)

        # Verify encrypted value is different from plain text
        assert pension.scheme_reference_encrypted != 'SENSITIVE123'

        # Verify can decrypt back to original
        decrypted = pension.get_scheme_reference()
        assert decrypted == 'SENSITIVE123'

        # Verify stored in database as encrypted
        result = await db_session.execute(
            select(UKPension).where(UKPension.id == pension.id)
        )
        db_pension = result.scalar_one()
        assert db_pension.scheme_reference_encrypted != 'SENSITIVE123'
