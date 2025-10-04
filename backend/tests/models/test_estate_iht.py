"""
Tests for Estate IHT models.

This module tests:
- EstateAsset model creation and validation
- EstateLiability model creation and validation
- IHTCalculation model and calculation methods
- SAEstateDutyCalculation model and calculation methods
- Temporal data handling (effective_from/effective_to)
- Soft delete functionality
- Constraints (non-negative values, valid dates)
- Relationships to User model
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
import uuid

from models.user import User, UserStatus, CountryPreference
from models.estate_iht import (
    EstateAsset,
    EstateLiability,
    IHTCalculation,
    SAEstateDutyCalculation,
    AssetType,
    LiabilityType,
)


@pytest.fixture
def test_user(db_session):
    """Create a test user for estate IHT tests."""
    user = User(
        email=f"estate_test_{uuid.uuid4()}@example.com",
        first_name="Estate",
        last_name="Tester",
        country_preference=CountryPreference.BOTH,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
        marketing_consent=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestEstateAsset:
    """Test EstateAsset model."""

    def test_create_estate_asset_all_types(self, db_session, test_user):
        """Test creating estate assets with all asset types."""
        asset_types = [
            AssetType.PROPERTY,
            AssetType.INVESTMENTS,
            AssetType.PENSIONS,
            AssetType.LIFE_ASSURANCE,
            AssetType.BUSINESS,
            AssetType.OTHER
        ]

        for asset_type in asset_types:
            asset = EstateAsset(
                user_id=test_user.id,
                asset_type=asset_type,
                description=f"Test {asset_type.value} asset",
                estimated_value=Decimal('500000.00'),
                currency='GBP',
                owned_individually=True,
                included_in_uk_estate=True,
                included_in_sa_estate=False,
                effective_from=date.today()
            )
            db_session.add(asset)
            db_session.commit()
            db_session.refresh(asset)

            assert asset.id is not None
            assert asset.user_id == test_user.id
            assert asset.asset_type == asset_type
            assert asset.estimated_value == Decimal('500000.00')
            assert asset.currency == 'GBP'
            assert asset.is_deleted is False

    def test_estate_asset_with_joint_ownership(self, db_session, test_user):
        """Test estate asset with joint ownership."""
        asset = EstateAsset(
            user_id=test_user.id,
            asset_type=AssetType.PROPERTY,
            description="Jointly owned property",
            estimated_value=Decimal('800000.00'),
            currency='GBP',
            owned_individually=False,
            joint_ownership="Spouse Name",
            included_in_uk_estate=True,
            included_in_sa_estate=False,
            effective_from=date.today()
        )
        db_session.add(asset)
        db_session.commit()
        db_session.refresh(asset)

        assert asset.owned_individually is False
        assert asset.joint_ownership == "Spouse Name"

    def test_estate_asset_multi_currency(self, db_session, test_user):
        """Test estate asset with different currencies."""
        currencies = ['GBP', 'ZAR', 'USD', 'EUR']

        for currency in currencies:
            asset = EstateAsset(
                user_id=test_user.id,
                asset_type=AssetType.INVESTMENTS,
                description=f"Investment in {currency}",
                estimated_value=Decimal('100000.00'),
                currency=currency,
                owned_individually=True,
                included_in_uk_estate=True,
                included_in_sa_estate=False,
                effective_from=date.today()
            )
            db_session.add(asset)
            db_session.commit()
            db_session.refresh(asset)

            assert asset.currency == currency

    def test_estate_asset_temporal_data(self, db_session, test_user):
        """Test estate asset with temporal data."""
        effective_from = date(2024, 1, 1)
        effective_to = date(2024, 12, 31)

        asset = EstateAsset(
            user_id=test_user.id,
            asset_type=AssetType.PROPERTY,
            description="Property with temporal data",
            estimated_value=Decimal('600000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
            effective_from=effective_from,
            effective_to=effective_to
        )
        db_session.add(asset)
        db_session.commit()
        db_session.refresh(asset)

        assert asset.effective_from == effective_from
        assert asset.effective_to == effective_to

    def test_estate_asset_soft_delete(self, db_session, test_user):
        """Test estate asset soft delete."""
        asset = EstateAsset(
            user_id=test_user.id,
            asset_type=AssetType.PROPERTY,
            description="Asset to be deleted",
            estimated_value=Decimal('500000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
            effective_from=date.today()
        )
        db_session.add(asset)
        db_session.commit()
        db_session.refresh(asset)

        # Soft delete
        asset.is_deleted = True
        db_session.commit()
        db_session.refresh(asset)

        assert asset.is_deleted is True
        assert asset.id is not None  # Still exists in database

    def test_estate_asset_negative_value_constraint(self, db_session, test_user):
        """Test estate asset with negative value fails."""
        asset = EstateAsset(
            user_id=test_user.id,
            asset_type=AssetType.PROPERTY,
            description="Invalid negative value asset",
            estimated_value=Decimal('-100000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
            effective_from=date.today()
        )
        db_session.add(asset)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_estate_asset_invalid_effective_dates(self, db_session, test_user):
        """Test estate asset with effective_to before effective_from fails."""
        asset = EstateAsset(
            user_id=test_user.id,
            asset_type=AssetType.PROPERTY,
            description="Invalid date range asset",
            estimated_value=Decimal('500000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
            effective_from=date(2024, 12, 31),
            effective_to=date(2024, 1, 1)
        )
        db_session.add(asset)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_estate_asset_relationship_to_user(self, db_session, test_user):
        """Test estate asset relationship to user."""
        asset = EstateAsset(
            user_id=test_user.id,
            asset_type=AssetType.PROPERTY,
            description="Test relationship",
            estimated_value=Decimal('500000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
            effective_from=date.today()
        )
        db_session.add(asset)
        db_session.commit()
        db_session.refresh(asset)

        assert asset.user.id == test_user.id
        assert asset in test_user.estate_assets


class TestEstateLiability:
    """Test EstateLiability model."""

    def test_create_estate_liability_all_types(self, db_session, test_user):
        """Test creating estate liabilities with all liability types."""
        liability_types = [
            LiabilityType.MORTGAGE,
            LiabilityType.LOAN,
            LiabilityType.CREDIT_CARD,
            LiabilityType.OTHER
        ]

        for liability_type in liability_types:
            liability = EstateLiability(
                user_id=test_user.id,
                liability_type=liability_type,
                description=f"Test {liability_type.value} liability",
                amount_outstanding=Decimal('50000.00'),
                currency='GBP',
                deductible_from_estate=True,
                effective_from=date.today()
            )
            db_session.add(liability)
            db_session.commit()
            db_session.refresh(liability)

            assert liability.id is not None
            assert liability.user_id == test_user.id
            assert liability.liability_type == liability_type
            assert liability.amount_outstanding == Decimal('50000.00')
            assert liability.is_deleted is False

    def test_estate_liability_non_deductible(self, db_session, test_user):
        """Test estate liability that is not deductible."""
        liability = EstateLiability(
            user_id=test_user.id,
            liability_type=LiabilityType.LOAN,
            description="Non-deductible loan",
            amount_outstanding=Decimal('25000.00'),
            currency='GBP',
            deductible_from_estate=False,
            effective_from=date.today()
        )
        db_session.add(liability)
        db_session.commit()
        db_session.refresh(liability)

        assert liability.deductible_from_estate is False

    def test_estate_liability_temporal_data(self, db_session, test_user):
        """Test estate liability with temporal data."""
        effective_from = date(2024, 1, 1)
        effective_to = date(2024, 12, 31)

        liability = EstateLiability(
            user_id=test_user.id,
            liability_type=LiabilityType.MORTGAGE,
            description="Mortgage with temporal data",
            amount_outstanding=Decimal('200000.00'),
            currency='GBP',
            deductible_from_estate=True,
            effective_from=effective_from,
            effective_to=effective_to
        )
        db_session.add(liability)
        db_session.commit()
        db_session.refresh(liability)

        assert liability.effective_from == effective_from
        assert liability.effective_to == effective_to

    def test_estate_liability_soft_delete(self, db_session, test_user):
        """Test estate liability soft delete."""
        liability = EstateLiability(
            user_id=test_user.id,
            liability_type=LiabilityType.LOAN,
            description="Liability to be deleted",
            amount_outstanding=Decimal('50000.00'),
            currency='GBP',
            deductible_from_estate=True,
            effective_from=date.today()
        )
        db_session.add(liability)
        db_session.commit()
        db_session.refresh(liability)

        # Soft delete
        liability.is_deleted = True
        db_session.commit()
        db_session.refresh(liability)

        assert liability.is_deleted is True
        assert liability.id is not None  # Still exists in database

    def test_estate_liability_negative_amount_constraint(self, db_session, test_user):
        """Test estate liability with negative amount fails."""
        liability = EstateLiability(
            user_id=test_user.id,
            liability_type=LiabilityType.LOAN,
            description="Invalid negative amount",
            amount_outstanding=Decimal('-50000.00'),
            currency='GBP',
            deductible_from_estate=True,
            effective_from=date.today()
        )
        db_session.add(liability)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_estate_liability_relationship_to_user(self, db_session, test_user):
        """Test estate liability relationship to user."""
        liability = EstateLiability(
            user_id=test_user.id,
            liability_type=LiabilityType.MORTGAGE,
            description="Test relationship",
            amount_outstanding=Decimal('200000.00'),
            currency='GBP',
            deductible_from_estate=True,
            effective_from=date.today()
        )
        db_session.add(liability)
        db_session.commit()
        db_session.refresh(liability)

        assert liability.user.id == test_user.id
        assert liability in test_user.estate_liabilities


class TestIHTCalculation:
    """Test IHTCalculation model."""

    def test_create_iht_calculation(self, db_session, test_user):
        """Test creating IHT calculation."""
        calculation = IHTCalculation(
            user_id=test_user.id,
            calculation_date=date.today(),
            tax_year='2024/25',
            gross_estate_value=Decimal('1000000.00'),
            net_estate_value=Decimal('900000.00'),
            nil_rate_band=Decimal('325000.00'),
            residence_nil_rate_band=Decimal('175000.00'),
            transferable_nil_rate_band=Decimal('0.00'),
            total_nil_rate_band_available=Decimal('500000.00'),
            taxable_estate=Decimal('400000.00'),
            iht_owed=Decimal('160000.00'),
            currency='GBP'
        )
        db_session.add(calculation)
        db_session.commit()
        db_session.refresh(calculation)

        assert calculation.id is not None
        assert calculation.user_id == test_user.id
        assert calculation.gross_estate_value == Decimal('1000000.00')
        assert calculation.iht_owed == Decimal('160000.00')

    def test_iht_calculation_with_transferable_nrb(self, db_session, test_user):
        """Test IHT calculation with transferable NRB from spouse."""
        calculation = IHTCalculation(
            user_id=test_user.id,
            calculation_date=date.today(),
            tax_year='2024/25',
            gross_estate_value=Decimal('2000000.00'),
            net_estate_value=Decimal('1900000.00'),
            nil_rate_band=Decimal('325000.00'),
            residence_nil_rate_band=Decimal('175000.00'),
            transferable_nil_rate_band=Decimal('325000.00'),  # Full NRB from spouse
            total_nil_rate_band_available=Decimal('825000.00'),
            taxable_estate=Decimal('1075000.00'),
            iht_owed=Decimal('430000.00'),
            currency='GBP'
        )
        db_session.add(calculation)
        db_session.commit()
        db_session.refresh(calculation)

        assert calculation.transferable_nil_rate_band == Decimal('325000.00')
        assert calculation.total_nil_rate_band_available == Decimal('825000.00')

    def test_iht_calculation_standard_rate(self, db_session, test_user):
        """Test IHT calculation with standard 40% rate."""
        calculation = IHTCalculation(
            user_id=test_user.id,
            calculation_date=date.today(),
            tax_year='2024/25',
            gross_estate_value=Decimal('1000000.00'),
            net_estate_value=Decimal('1000000.00'),
            nil_rate_band=Decimal('325000.00'),
            residence_nil_rate_band=Decimal('175000.00'),
            transferable_nil_rate_band=Decimal('0.00'),
            total_nil_rate_band_available=Decimal('500000.00'),
            taxable_estate=Decimal('500000.00'),
            iht_owed=Decimal('0.00'),  # Will calculate
            currency='GBP'
        )
        db_session.add(calculation)
        db_session.commit()
        db_session.refresh(calculation)

        # Calculate IHT with standard rate (40%)
        iht = calculation.calculate_iht(charitable_gift_percentage=Decimal('0.00'))
        assert iht == Decimal('200000.00')  # 40% of 500,000

    def test_iht_calculation_reduced_rate_charity(self, db_session, test_user):
        """Test IHT calculation with reduced 36% rate (10%+ to charity)."""
        calculation = IHTCalculation(
            user_id=test_user.id,
            calculation_date=date.today(),
            tax_year='2024/25',
            gross_estate_value=Decimal('1000000.00'),
            net_estate_value=Decimal('1000000.00'),
            nil_rate_band=Decimal('325000.00'),
            residence_nil_rate_band=Decimal('175000.00'),
            transferable_nil_rate_band=Decimal('0.00'),
            total_nil_rate_band_available=Decimal('500000.00'),
            taxable_estate=Decimal('500000.00'),
            iht_owed=Decimal('0.00'),  # Will calculate
            currency='GBP'
        )
        db_session.add(calculation)
        db_session.commit()
        db_session.refresh(calculation)

        # Calculate IHT with reduced rate (36% if 10%+ to charity)
        iht = calculation.calculate_iht(charitable_gift_percentage=Decimal('10.00'))
        assert iht == Decimal('180000.00')  # 36% of 500,000

    def test_iht_calculation_tax_year_format_validation(self, db_session, test_user):
        """Test IHT calculation tax year format validation."""
        # Valid format
        calculation = IHTCalculation(
            user_id=test_user.id,
            calculation_date=date.today(),
            tax_year='2024/25',
            gross_estate_value=Decimal('1000000.00'),
            net_estate_value=Decimal('900000.00'),
            nil_rate_band=Decimal('325000.00'),
            residence_nil_rate_band=Decimal('175000.00'),
            transferable_nil_rate_band=Decimal('0.00'),
            total_nil_rate_band_available=Decimal('500000.00'),
            taxable_estate=Decimal('400000.00'),
            iht_owed=Decimal('160000.00'),
            currency='GBP'
        )
        db_session.add(calculation)
        db_session.commit()

        assert calculation.tax_year == '2024/25'

    def test_iht_calculation_relationship_to_user(self, db_session, test_user):
        """Test IHT calculation relationship to user."""
        calculation = IHTCalculation(
            user_id=test_user.id,
            calculation_date=date.today(),
            tax_year='2024/25',
            gross_estate_value=Decimal('1000000.00'),
            net_estate_value=Decimal('900000.00'),
            nil_rate_band=Decimal('325000.00'),
            residence_nil_rate_band=Decimal('175000.00'),
            transferable_nil_rate_band=Decimal('0.00'),
            total_nil_rate_band_available=Decimal('500000.00'),
            taxable_estate=Decimal('400000.00'),
            iht_owed=Decimal('160000.00'),
            currency='GBP'
        )
        db_session.add(calculation)
        db_session.commit()
        db_session.refresh(calculation)

        assert calculation.user.id == test_user.id
        assert calculation in test_user.iht_calculations


class TestSAEstateDutyCalculation:
    """Test SAEstateDutyCalculation model."""

    def test_create_sa_estate_duty_calculation(self, db_session, test_user):
        """Test creating SA Estate Duty calculation."""
        calculation = SAEstateDutyCalculation(
            user_id=test_user.id,
            calculation_date=date.today(),
            estate_value=Decimal('10000000.00'),
            abatement=Decimal('3500000.00'),
            dutiable_amount=Decimal('6500000.00'),
            estate_duty_rate=Decimal('20.00'),
            estate_duty_owed=Decimal('1300000.00'),
            currency='ZAR'
        )
        db_session.add(calculation)
        db_session.commit()
        db_session.refresh(calculation)

        assert calculation.id is not None
        assert calculation.user_id == test_user.id
        assert calculation.estate_value == Decimal('10000000.00')
        assert calculation.abatement == Decimal('3500000.00')
        assert calculation.estate_duty_owed == Decimal('1300000.00')

    def test_sa_estate_duty_calculation_below_threshold(self, db_session, test_user):
        """Test SA Estate Duty calculation for estate below R30M threshold (20% rate)."""
        calculation = SAEstateDutyCalculation(
            user_id=test_user.id,
            calculation_date=date.today(),
            estate_value=Decimal('20000000.00'),
            abatement=Decimal('3500000.00'),
            dutiable_amount=Decimal('16500000.00'),
            estate_duty_rate=Decimal('20.00'),
            estate_duty_owed=Decimal('0.00'),  # Will calculate
            currency='ZAR'
        )
        db_session.add(calculation)
        db_session.commit()
        db_session.refresh(calculation)

        # Calculate estate duty (20% on full amount)
        duty = calculation.calculate_estate_duty()
        assert duty == Decimal('3300000.00')  # 20% of R16.5M

    def test_sa_estate_duty_calculation_above_threshold(self, db_session, test_user):
        """Test SA Estate Duty calculation for estate above R30M threshold (25% rate on excess)."""
        calculation = SAEstateDutyCalculation(
            user_id=test_user.id,
            calculation_date=date.today(),
            estate_value=Decimal('50000000.00'),
            abatement=Decimal('3500000.00'),
            dutiable_amount=Decimal('46500000.00'),
            estate_duty_rate=Decimal('20.00'),  # Base rate
            estate_duty_owed=Decimal('0.00'),  # Will calculate
            currency='ZAR'
        )
        db_session.add(calculation)
        db_session.commit()
        db_session.refresh(calculation)

        # Calculate estate duty (20% on first R30M + 25% on excess)
        duty = calculation.calculate_estate_duty()
        # First R30M: 30,000,000 * 0.20 = 6,000,000
        # Excess R16.5M: 16,500,000 * 0.25 = 4,125,000
        # Total: 10,125,000
        assert duty == Decimal('10125000.00')

    def test_sa_estate_duty_calculation_no_duty_owed(self, db_session, test_user):
        """Test SA Estate Duty calculation where estate is below abatement (no duty)."""
        calculation = SAEstateDutyCalculation(
            user_id=test_user.id,
            calculation_date=date.today(),
            estate_value=Decimal('3000000.00'),
            abatement=Decimal('3500000.00'),
            dutiable_amount=Decimal('0.00'),  # Estate < abatement
            estate_duty_rate=Decimal('20.00'),
            estate_duty_owed=Decimal('0.00'),
            currency='ZAR'
        )
        db_session.add(calculation)
        db_session.commit()
        db_session.refresh(calculation)

        assert calculation.estate_duty_owed == Decimal('0.00')

    def test_sa_estate_duty_calculation_relationship_to_user(self, db_session, test_user):
        """Test SA Estate Duty calculation relationship to user."""
        calculation = SAEstateDutyCalculation(
            user_id=test_user.id,
            calculation_date=date.today(),
            estate_value=Decimal('10000000.00'),
            abatement=Decimal('3500000.00'),
            dutiable_amount=Decimal('6500000.00'),
            estate_duty_rate=Decimal('20.00'),
            estate_duty_owed=Decimal('1300000.00'),
            currency='ZAR'
        )
        db_session.add(calculation)
        db_session.commit()
        db_session.refresh(calculation)

        assert calculation.user.id == test_user.id
        assert calculation in test_user.sa_estate_duty_calculations


class TestEstateIHTIntegration:
    """Integration tests for Estate IHT models."""

    def test_complete_estate_calculation_scenario(self, db_session, test_user):
        """Test complete estate calculation scenario with assets, liabilities, and IHT calculation."""
        # Create assets
        property_asset = EstateAsset(
            user_id=test_user.id,
            asset_type=AssetType.PROPERTY,
            description="Primary residence",
            estimated_value=Decimal('800000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
            effective_from=date.today()
        )
        investment_asset = EstateAsset(
            user_id=test_user.id,
            asset_type=AssetType.INVESTMENTS,
            description="Investment portfolio",
            estimated_value=Decimal('500000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
            effective_from=date.today()
        )
        db_session.add(property_asset)
        db_session.add(investment_asset)
        db_session.commit()

        # Create liabilities
        mortgage = EstateLiability(
            user_id=test_user.id,
            liability_type=LiabilityType.MORTGAGE,
            description="Property mortgage",
            amount_outstanding=Decimal('200000.00'),
            currency='GBP',
            deductible_from_estate=True,
            effective_from=date.today()
        )
        db_session.add(mortgage)
        db_session.commit()

        # Calculate gross and net estate
        gross_estate = Decimal('1300000.00')  # 800k + 500k
        net_estate = Decimal('1100000.00')  # 1300k - 200k

        # Create IHT calculation
        iht_calc = IHTCalculation(
            user_id=test_user.id,
            calculation_date=date.today(),
            tax_year='2024/25',
            gross_estate_value=gross_estate,
            net_estate_value=net_estate,
            nil_rate_band=Decimal('325000.00'),
            residence_nil_rate_band=Decimal('175000.00'),
            transferable_nil_rate_band=Decimal('0.00'),
            total_nil_rate_band_available=Decimal('500000.00'),
            taxable_estate=Decimal('600000.00'),  # 1100k - 500k
            iht_owed=Decimal('240000.00'),  # 40% of 600k
            currency='GBP'
        )
        db_session.add(iht_calc)
        db_session.commit()

        # Verify all data
        assert len(test_user.estate_assets) == 2
        assert len(test_user.estate_liabilities) == 1
        assert len(test_user.iht_calculations) == 1
        assert iht_calc.net_estate_value == net_estate
        assert iht_calc.iht_owed == Decimal('240000.00')

    def test_multiple_calculations_over_time(self, db_session, test_user):
        """Test tracking multiple IHT calculations over time."""
        # Create calculations for different dates
        calc_2023 = IHTCalculation(
            user_id=test_user.id,
            calculation_date=date(2023, 12, 31),
            tax_year='2023/24',
            gross_estate_value=Decimal('900000.00'),
            net_estate_value=Decimal('850000.00'),
            nil_rate_band=Decimal('325000.00'),
            residence_nil_rate_band=Decimal('175000.00'),
            transferable_nil_rate_band=Decimal('0.00'),
            total_nil_rate_band_available=Decimal('500000.00'),
            taxable_estate=Decimal('350000.00'),
            iht_owed=Decimal('140000.00'),
            currency='GBP'
        )
        calc_2024 = IHTCalculation(
            user_id=test_user.id,
            calculation_date=date(2024, 12, 31),
            tax_year='2024/25',
            gross_estate_value=Decimal('1100000.00'),
            net_estate_value=Decimal('1050000.00'),
            nil_rate_band=Decimal('325000.00'),
            residence_nil_rate_band=Decimal('175000.00'),
            transferable_nil_rate_band=Decimal('0.00'),
            total_nil_rate_band_available=Decimal('500000.00'),
            taxable_estate=Decimal('550000.00'),
            iht_owed=Decimal('220000.00'),
            currency='GBP'
        )
        db_session.add(calc_2023)
        db_session.add(calc_2024)
        db_session.commit()

        # Verify both calculations exist
        assert len(test_user.iht_calculations) == 2

        # Verify estate growth over time
        assert calc_2024.net_estate_value > calc_2023.net_estate_value
        assert calc_2024.iht_owed > calc_2023.iht_owed
