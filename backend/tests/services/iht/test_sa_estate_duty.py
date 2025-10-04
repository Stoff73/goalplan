"""
Tests for SA Estate Duty Service

Tests cover:
- SA estate value calculation (SA-situs assets only)
- SA Estate Duty calculation with abatement
- Tiered rate application (20% up to R30M, 25% above)
- Estate Duty calculation saving
- Edge cases (zero estate, negative values, threshold boundaries)
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from models.estate_iht import (
    EstateAsset, EstateLiability, SAEstateDutyCalculation, AssetType, LiabilityType
)
from services.iht.sa_estate_duty_service import (
    SAEstateDutyService, ValidationError
)


@pytest.fixture
async def sa_service(db_session: AsyncSession):
    """Create SA estate duty service instance."""
    return SAEstateDutyService(db_session)


@pytest.fixture
async def test_user_id():
    """Generate test user ID."""
    return uuid4()


@pytest.fixture
async def sample_sa_assets(db_session: AsyncSession, test_user_id):
    """Create sample SA estate assets."""
    today = date.today()

    assets = [
        EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.PROPERTY,
            description="SA property",
            estimated_value=Decimal('5000000.00'),  # R5M
            currency='ZAR',
            owned_individually=True,
            included_in_uk_estate=False,
            included_in_sa_estate=True,
            effective_from=today - timedelta(days=365),
            effective_to=None,
            is_deleted=False
        ),
        EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.INVESTMENTS,
            description="SA shares",
            estimated_value=Decimal('2000000.00'),  # R2M
            currency='ZAR',
            owned_individually=True,
            included_in_uk_estate=False,
            included_in_sa_estate=True,
            effective_from=today - timedelta(days=365),
            effective_to=None,
            is_deleted=False
        ),
    ]

    for asset in assets:
        db_session.add(asset)

    await db_session.commit()
    return assets


@pytest.fixture
async def sample_sa_liabilities(db_session: AsyncSession, test_user_id):
    """Create sample SA estate liabilities."""
    today = date.today()

    liabilities = [
        EstateLiability(
            id=uuid4(),
            user_id=test_user_id,
            liability_type=LiabilityType.MORTGAGE,
            description="Mortgage on SA property",
            amount_outstanding=Decimal('1000000.00'),  # R1M
            currency='ZAR',
            deductible_from_estate=True,
            effective_from=today - timedelta(days=365),
            effective_to=None,
            is_deleted=False
        ),
    ]

    for liability in liabilities:
        db_session.add(liability)

    await db_session.commit()
    return liabilities


class TestSAEstateValueCalculation:
    """Tests for SA estate value calculation."""

    async def test_calculate_sa_estate_value_basic(
        self,
        sa_service: SAEstateDutyService,
        test_user_id,
        sample_sa_assets
    ):
        """Test basic SA estate value calculation."""
        estate_value = await sa_service.calculate_sa_estate_value(test_user_id)

        # Sum: R5M + R2M = R7M
        assert estate_value == Decimal('7000000.00')

    async def test_calculate_sa_estate_value_empty(
        self,
        sa_service: SAEstateDutyService
    ):
        """Test SA estate value with no assets."""
        empty_user_id = uuid4()
        estate_value = await sa_service.calculate_sa_estate_value(empty_user_id)

        assert estate_value == Decimal('0.00')

    async def test_calculate_sa_estate_value_only_sa_included(
        self,
        sa_service: SAEstateDutyService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test that only SA-included assets are counted."""
        today = date.today()

        # UK-only asset (not SA-included)
        uk_asset = EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.PROPERTY,
            description="UK property",
            estimated_value=Decimal('500000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
            effective_from=today - timedelta(days=365),
            effective_to=None,
            is_deleted=False
        )
        db_session.add(uk_asset)

        await db_session.commit()

        # Should not include UK-only asset
        estate_value = await sa_service.calculate_sa_estate_value(test_user_id)
        assert estate_value == Decimal('0.00')

    async def test_calculate_sa_estate_value_temporal_filtering(
        self,
        sa_service: SAEstateDutyService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test SA estate value with temporal filtering."""
        today = date.today()

        # Asset that ended in past
        past_asset = EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.PROPERTY,
            description="Sold SA property",
            estimated_value=Decimal('1000000.00'),
            currency='ZAR',
            owned_individually=True,
            included_in_uk_estate=False,
            included_in_sa_estate=True,
            effective_from=today - timedelta(days=730),
            effective_to=today - timedelta(days=365),
            is_deleted=False
        )

        # Current asset
        current_asset = EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.INVESTMENTS,
            description="Current SA investment",
            estimated_value=Decimal('500000.00'),
            currency='ZAR',
            owned_individually=True,
            included_in_uk_estate=False,
            included_in_sa_estate=True,
            effective_from=today - timedelta(days=100),
            effective_to=None,
            is_deleted=False
        )

        db_session.add(past_asset)
        db_session.add(current_asset)
        await db_session.commit()

        # Should only include current asset
        estate_value = await sa_service.calculate_sa_estate_value(test_user_id)
        assert estate_value == Decimal('500000.00')


class TestEstateDutyCalculation:
    """Tests for SA Estate Duty calculation."""

    async def test_calculate_estate_duty_below_abatement(
        self,
        sa_service: SAEstateDutyService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test estate duty with estate below abatement."""
        today = date.today()

        # Small estate: R3M (below R3.5M abatement)
        asset = EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.INVESTMENTS,
            description="Small SA investment",
            estimated_value=Decimal('3000000.00'),
            currency='ZAR',
            owned_individually=True,
            included_in_uk_estate=False,
            included_in_sa_estate=True,
            effective_from=today,
            effective_to=None,
            is_deleted=False
        )
        db_session.add(asset)
        await db_session.commit()

        result = await sa_service.calculate_estate_duty(test_user_id)

        assert result['estate_value'] == Decimal('3000000.00')
        assert result['net_estate'] == Decimal('3000000.00')
        assert result['abatement'] == Decimal('3500000.00')
        assert result['dutiable_amount'] == Decimal('0.00')
        assert result['estate_duty_owed'] == Decimal('0.00')

    async def test_calculate_estate_duty_tier_1_only(
        self,
        sa_service: SAEstateDutyService,
        test_user_id,
        sample_sa_assets,
        sample_sa_liabilities
    ):
        """Test estate duty at 20% (below R30M threshold)."""
        result = await sa_service.calculate_estate_duty(test_user_id)

        # Estate: R7M, Liabilities: R1M, Net: R6M
        # Abatement: R3.5M
        # Dutiable: R2.5M
        # Duty at 20%: R500k
        assert result['estate_value'] == Decimal('7000000.00')
        assert result['liabilities'] == Decimal('1000000.00')
        assert result['net_estate'] == Decimal('6000000.00')
        assert result['abatement'] == Decimal('3500000.00')
        assert result['dutiable_amount'] == Decimal('2500000.00')
        assert result['estate_duty_owed'] == Decimal('500000.00')

    async def test_calculate_estate_duty_tier_2(
        self,
        sa_service: SAEstateDutyService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test estate duty with tiered rates (above R30M threshold)."""
        today = date.today()

        # Large estate: R40M
        asset = EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.PROPERTY,
            description="Large SA estate",
            estimated_value=Decimal('40000000.00'),
            currency='ZAR',
            owned_individually=True,
            included_in_uk_estate=False,
            included_in_sa_estate=True,
            effective_from=today,
            effective_to=None,
            is_deleted=False
        )
        db_session.add(asset)
        await db_session.commit()

        result = await sa_service.calculate_estate_duty(test_user_id)

        # Estate: R40M
        # Net estate: R40M
        # Abatement: R3.5M
        # Dutiable: R36.5M
        # Duty calculation:
        #   - First R30M: R30M * 20% = R6M
        #   - Excess R6.5M: R6.5M * 25% = R1.625M
        #   - Total: R6M + R1.625M = R7.625M
        assert result['net_estate'] == Decimal('40000000.00')
        assert result['dutiable_amount'] == Decimal('36500000.00')

        expected_duty = (Decimal('30000000.00') * Decimal('0.20')) + \
                       (Decimal('6500000.00') * Decimal('0.25'))
        assert result['estate_duty_owed'] == expected_duty
        assert result['estate_duty_owed'] == Decimal('7625000.00')

    async def test_calculate_estate_duty_exactly_at_threshold(
        self,
        sa_service: SAEstateDutyService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test estate duty at exactly R30M threshold."""
        today = date.today()

        # Estate exactly at threshold after abatement
        # Net estate: R33.5M
        # Abatement: R3.5M
        # Dutiable: R30M exactly
        asset = EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.PROPERTY,
            description="Estate at threshold",
            estimated_value=Decimal('33500000.00'),
            currency='ZAR',
            owned_individually=True,
            included_in_uk_estate=False,
            included_in_sa_estate=True,
            effective_from=today,
            effective_to=None,
            is_deleted=False
        )
        db_session.add(asset)
        await db_session.commit()

        result = await sa_service.calculate_estate_duty(test_user_id)

        assert result['dutiable_amount'] == Decimal('30000000.00')
        # Duty at 20%: R6M
        assert result['estate_duty_owed'] == Decimal('6000000.00')

    async def test_calculate_estate_duty_just_above_threshold(
        self,
        sa_service: SAEstateDutyService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test estate duty just above R30M threshold."""
        today = date.today()

        # Net estate: R33.5M + R1
        # Dutiable: R30M + R1
        asset = EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.PROPERTY,
            description="Estate just over threshold",
            estimated_value=Decimal('33500001.00'),
            currency='ZAR',
            owned_individually=True,
            included_in_uk_estate=False,
            included_in_sa_estate=True,
            effective_from=today,
            effective_to=None,
            is_deleted=False
        )
        db_session.add(asset)
        await db_session.commit()

        result = await sa_service.calculate_estate_duty(test_user_id)

        assert result['dutiable_amount'] == Decimal('30000001.00')
        # Duty: (R30M * 20%) + (R1 * 25%)
        # = R6,000,000 + R0.25 = R6,000,000.25
        expected_duty = (Decimal('30000000.00') * Decimal('0.20')) + \
                       (Decimal('1.00') * Decimal('0.25'))
        assert result['estate_duty_owed'] == expected_duty

    async def test_calculate_estate_duty_with_liabilities(
        self,
        sa_service: SAEstateDutyService,
        test_user_id,
        sample_sa_assets,
        sample_sa_liabilities
    ):
        """Test estate duty with deductible liabilities."""
        result = await sa_service.calculate_estate_duty(test_user_id)

        # Gross: R7M, Liabilities: R1M, Net: R6M
        assert result['estate_value'] == Decimal('7000000.00')
        assert result['liabilities'] == Decimal('1000000.00')
        assert result['net_estate'] == Decimal('6000000.00')

    async def test_calculate_estate_duty_effective_rate(
        self,
        sa_service: SAEstateDutyService,
        test_user_id,
        sample_sa_assets,
        sample_sa_liabilities
    ):
        """Test effective rate calculation."""
        result = await sa_service.calculate_estate_duty(test_user_id)

        # Net estate: R6M
        # Duty owed: R500k
        # Effective rate: (R500k / R6M) * 100 = 8.33%
        expected_rate = (result['estate_duty_owed'] / result['net_estate']) * Decimal('100')
        assert abs(result['effective_rate'] - expected_rate) < Decimal('0.01')


class TestEstateDutyCalculationSaving:
    """Tests for saving estate duty calculations."""

    async def test_save_estate_duty_calculation(
        self,
        sa_service: SAEstateDutyService,
        test_user_id,
        sample_sa_assets,
        sample_sa_liabilities
    ):
        """Test saving estate duty calculation."""
        # Calculate duty
        calculation_data = await sa_service.calculate_estate_duty(test_user_id)

        # Save calculation
        saved_calculation = await sa_service.save_estate_duty_calculation(
            test_user_id,
            calculation_data
        )

        assert saved_calculation.id is not None
        assert saved_calculation.user_id == test_user_id
        assert saved_calculation.estate_value == Decimal('7000000.00')
        assert saved_calculation.abatement == Decimal('3500000.00')
        assert saved_calculation.dutiable_amount == Decimal('2500000.00')
        assert saved_calculation.estate_duty_owed == Decimal('500000.00')
        assert saved_calculation.currency == 'ZAR'

    async def test_save_estate_duty_calculation_missing_field(
        self,
        sa_service: SAEstateDutyService,
        test_user_id
    ):
        """Test saving with missing required field."""
        incomplete_data = {
            'estate_value': Decimal('5000000.00'),
            # Missing other required fields
        }

        with pytest.raises(ValidationError):
            await sa_service.save_estate_duty_calculation(
                test_user_id,
                incomplete_data
            )


class TestEdgeCases:
    """Tests for edge cases."""

    async def test_zero_estate(
        self,
        sa_service: SAEstateDutyService,
        test_user_id
    ):
        """Test calculation with zero estate."""
        result = await sa_service.calculate_estate_duty(test_user_id)

        assert result['estate_value'] == Decimal('0.00')
        assert result['net_estate'] == Decimal('0.00')
        assert result['dutiable_amount'] == Decimal('0.00')
        assert result['estate_duty_owed'] == Decimal('0.00')
        assert result['effective_rate'] == Decimal('0.00')

    async def test_negative_net_estate(
        self,
        sa_service: SAEstateDutyService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test calculation with negative net estate (insolvent)."""
        today = date.today()

        # Small asset
        asset = EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.INVESTMENTS,
            description="Small asset",
            estimated_value=Decimal('500000.00'),
            currency='ZAR',
            owned_individually=True,
            included_in_uk_estate=False,
            included_in_sa_estate=True,
            effective_from=today,
            effective_to=None,
            is_deleted=False
        )

        # Large liability
        liability = EstateLiability(
            id=uuid4(),
            user_id=test_user_id,
            liability_type=LiabilityType.LOAN,
            description="Large loan",
            amount_outstanding=Decimal('1000000.00'),
            currency='ZAR',
            deductible_from_estate=True,
            effective_from=today,
            effective_to=None,
            is_deleted=False
        )

        db_session.add(asset)
        db_session.add(liability)
        await db_session.commit()

        result = await sa_service.calculate_estate_duty(test_user_id)

        # Net estate is negative
        assert result['net_estate'] == Decimal('-500000.00')
        # No duty on insolvent estate
        assert result['dutiable_amount'] == Decimal('0.00')
        assert result['estate_duty_owed'] == Decimal('0.00')

    async def test_estate_exactly_at_abatement(
        self,
        sa_service: SAEstateDutyService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test estate exactly at abatement threshold."""
        today = date.today()

        # Estate exactly R3.5M
        asset = EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.INVESTMENTS,
            description="Estate at abatement",
            estimated_value=Decimal('3500000.00'),
            currency='ZAR',
            owned_individually=True,
            included_in_uk_estate=False,
            included_in_sa_estate=True,
            effective_from=today,
            effective_to=None,
            is_deleted=False
        )
        db_session.add(asset)
        await db_session.commit()

        result = await sa_service.calculate_estate_duty(test_user_id)

        assert result['net_estate'] == Decimal('3500000.00')
        assert result['abatement'] == Decimal('3500000.00')
        assert result['dutiable_amount'] == Decimal('0.00')
        assert result['estate_duty_owed'] == Decimal('0.00')

    async def test_very_large_estate(
        self,
        sa_service: SAEstateDutyService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test with very large estate."""
        today = date.today()

        # Very large estate: R100M
        asset = EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.PROPERTY,
            description="Very large estate",
            estimated_value=Decimal('100000000.00'),
            currency='ZAR',
            owned_individually=True,
            included_in_uk_estate=False,
            included_in_sa_estate=True,
            effective_from=today,
            effective_to=None,
            is_deleted=False
        )
        db_session.add(asset)
        await db_session.commit()

        result = await sa_service.calculate_estate_duty(test_user_id)

        # Net: R100M
        # Dutiable: R96.5M (after R3.5M abatement)
        # Duty:
        #   - First R30M: R30M * 20% = R6M
        #   - Excess R66.5M: R66.5M * 25% = R16.625M
        #   - Total: R22.625M
        assert result['net_estate'] == Decimal('100000000.00')
        assert result['dutiable_amount'] == Decimal('96500000.00')

        expected_duty = (Decimal('30000000.00') * Decimal('0.20')) + \
                       (Decimal('66500000.00') * Decimal('0.25'))
        assert result['estate_duty_owed'] == expected_duty
        assert result['estate_duty_owed'] == Decimal('22625000.00')
