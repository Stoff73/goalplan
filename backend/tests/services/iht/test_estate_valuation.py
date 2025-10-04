"""
Tests for Estate Valuation Service

Tests cover:
- Gross estate calculation with temporal filtering
- Net estate calculation with liabilities
- RNRB calculation with tapering edge cases
- IHT calculation at 40% and 36% rates
- Transferable NRB application
- IHT calculation saving
- Edge cases (zero estate, negative values handled)
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from models.estate_iht import (
    EstateAsset, EstateLiability, IHTCalculation, AssetType, LiabilityType
)
from services.iht.estate_valuation_service import (
    EstateValuationService, ValidationError
)


@pytest.fixture
async def estate_service(db_session: AsyncSession):
    """Create estate valuation service instance."""
    return EstateValuationService(db_session)


@pytest.fixture
async def test_user_id():
    """Generate test user ID."""
    return uuid4()


@pytest.fixture
async def sample_assets(db_session: AsyncSession, test_user_id):
    """Create sample estate assets."""
    today = date.today()

    assets = [
        EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.PROPERTY,
            description="Primary residence",
            estimated_value=Decimal('500000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
            effective_from=today - timedelta(days=365),
            effective_to=None,
            is_deleted=False
        ),
        EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.INVESTMENTS,
            description="ISA investments",
            estimated_value=Decimal('200000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
            effective_from=today - timedelta(days=365),
            effective_to=None,
            is_deleted=False
        ),
        EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.PENSIONS,
            description="Personal pension",
            estimated_value=Decimal('300000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
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
async def sample_liabilities(db_session: AsyncSession, test_user_id):
    """Create sample estate liabilities."""
    today = date.today()

    liabilities = [
        EstateLiability(
            id=uuid4(),
            user_id=test_user_id,
            liability_type=LiabilityType.MORTGAGE,
            description="Mortgage on primary residence",
            amount_outstanding=Decimal('150000.00'),
            currency='GBP',
            deductible_from_estate=True,
            effective_from=today - timedelta(days=365),
            effective_to=None,
            is_deleted=False
        ),
        EstateLiability(
            id=uuid4(),
            user_id=test_user_id,
            liability_type=LiabilityType.LOAN,
            description="Personal loan",
            amount_outstanding=Decimal('50000.00'),
            currency='GBP',
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


class TestGrossEstateCalculation:
    """Tests for gross estate calculation."""

    async def test_calculate_gross_estate_basic(
        self,
        estate_service: EstateValuationService,
        test_user_id,
        sample_assets
    ):
        """Test basic gross estate calculation."""
        gross_estate = await estate_service.calculate_gross_estate(test_user_id)

        # Sum: £500k + £200k + £300k = £1,000k
        assert gross_estate == Decimal('1000000.00')

    async def test_calculate_gross_estate_empty(
        self,
        estate_service: EstateValuationService
    ):
        """Test gross estate with no assets."""
        empty_user_id = uuid4()
        gross_estate = await estate_service.calculate_gross_estate(empty_user_id)

        assert gross_estate == Decimal('0.00')

    async def test_calculate_gross_estate_temporal_filtering(
        self,
        estate_service: EstateValuationService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test gross estate with temporal filtering."""
        today = date.today()

        # Asset that was effective in past but ended
        past_asset = EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.PROPERTY,
            description="Sold property",
            estimated_value=Decimal('100000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
            effective_from=today - timedelta(days=730),
            effective_to=today - timedelta(days=365),
            is_deleted=False
        )
        db_session.add(past_asset)

        # Current asset
        current_asset = EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.INVESTMENTS,
            description="Current investment",
            estimated_value=Decimal('50000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
            effective_from=today - timedelta(days=100),
            effective_to=None,
            is_deleted=False
        )
        db_session.add(current_asset)

        await db_session.commit()

        # Should only include current asset
        gross_estate = await estate_service.calculate_gross_estate(test_user_id)
        assert gross_estate == Decimal('50000.00')

    async def test_calculate_gross_estate_only_uk_included(
        self,
        estate_service: EstateValuationService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test that only UK-included assets are counted."""
        today = date.today()

        # SA-only asset (not UK-included)
        sa_asset = EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.PROPERTY,
            description="SA property",
            estimated_value=Decimal('200000.00'),
            currency='ZAR',
            owned_individually=True,
            included_in_uk_estate=False,
            included_in_sa_estate=True,
            effective_from=today - timedelta(days=365),
            effective_to=None,
            is_deleted=False
        )
        db_session.add(sa_asset)

        await db_session.commit()

        # Should not include SA-only asset
        gross_estate = await estate_service.calculate_gross_estate(test_user_id)
        assert gross_estate == Decimal('0.00')


class TestNetEstateCalculation:
    """Tests for net estate calculation."""

    async def test_calculate_net_estate_basic(
        self,
        estate_service: EstateValuationService,
        test_user_id,
        sample_assets,
        sample_liabilities
    ):
        """Test basic net estate calculation."""
        net_estate = await estate_service.calculate_net_estate(test_user_id)

        # Gross: £1,000k, Liabilities: £200k, Net: £800k
        assert net_estate == Decimal('800000.00')

    async def test_calculate_net_estate_no_liabilities(
        self,
        estate_service: EstateValuationService,
        test_user_id,
        sample_assets
    ):
        """Test net estate with no liabilities."""
        net_estate = await estate_service.calculate_net_estate(test_user_id)

        # Should equal gross estate
        assert net_estate == Decimal('1000000.00')

    async def test_calculate_net_estate_only_deductible_liabilities(
        self,
        estate_service: EstateValuationService,
        db_session: AsyncSession,
        test_user_id,
        sample_assets
    ):
        """Test that only deductible liabilities are subtracted."""
        today = date.today()

        # Non-deductible liability
        non_deductible = EstateLiability(
            id=uuid4(),
            user_id=test_user_id,
            liability_type=LiabilityType.OTHER,
            description="Non-deductible liability",
            amount_outstanding=Decimal('100000.00'),
            currency='GBP',
            deductible_from_estate=False,
            effective_from=today - timedelta(days=365),
            effective_to=None,
            is_deleted=False
        )
        db_session.add(non_deductible)

        await db_session.commit()

        net_estate = await estate_service.calculate_net_estate(test_user_id)

        # Should not deduct non-deductible liability
        assert net_estate == Decimal('1000000.00')


class TestRNRBCalculation:
    """Tests for Residence Nil Rate Band calculation."""

    async def test_calculate_rnrb_full_amount(
        self,
        estate_service: EstateValuationService,
        test_user_id
    ):
        """Test RNRB with estate below taper threshold."""
        net_estate = Decimal('1000000.00')
        rnrb = await estate_service.calculate_residence_nil_rate_band(
            test_user_id,
            net_estate,
            property_left_to_descendants=True
        )

        # Full RNRB: £175,000
        assert rnrb == Decimal('175000.00')

    async def test_calculate_rnrb_not_applicable(
        self,
        estate_service: EstateValuationService,
        test_user_id
    ):
        """Test RNRB when not leaving property to descendants."""
        net_estate = Decimal('1000000.00')
        rnrb = await estate_service.calculate_residence_nil_rate_band(
            test_user_id,
            net_estate,
            property_left_to_descendants=False
        )

        assert rnrb == Decimal('0.00')

    async def test_calculate_rnrb_taper_partial(
        self,
        estate_service: EstateValuationService,
        test_user_id
    ):
        """Test RNRB tapering with estate over £2M."""
        # Estate of £2.2M -> £200k over threshold
        # Taper: £200k / 2 = £100k reduction
        # RNRB: £175k - £100k = £75k
        net_estate = Decimal('2200000.00')
        rnrb = await estate_service.calculate_residence_nil_rate_band(
            test_user_id,
            net_estate,
            property_left_to_descendants=True
        )

        assert rnrb == Decimal('75000.00')

    async def test_calculate_rnrb_taper_to_zero(
        self,
        estate_service: EstateValuationService,
        test_user_id
    ):
        """Test RNRB tapering to zero."""
        # Estate of £2.35M -> £350k over threshold
        # Taper: £350k / 2 = £175k reduction
        # RNRB: £175k - £175k = £0
        net_estate = Decimal('2350000.00')
        rnrb = await estate_service.calculate_residence_nil_rate_band(
            test_user_id,
            net_estate,
            property_left_to_descendants=True
        )

        assert rnrb == Decimal('0.00')

    async def test_calculate_rnrb_taper_beyond_zero(
        self,
        estate_service: EstateValuationService,
        test_user_id
    ):
        """Test RNRB tapering doesn't go negative."""
        # Estate of £3M -> £1M over threshold
        # Taper would be £500k, but RNRB capped at £0
        net_estate = Decimal('3000000.00')
        rnrb = await estate_service.calculate_residence_nil_rate_band(
            test_user_id,
            net_estate,
            property_left_to_descendants=True
        )

        assert rnrb == Decimal('0.00')


class TestIHTCalculation:
    """Tests for UK Inheritance Tax calculation."""

    async def test_calculate_iht_below_nrb(
        self,
        estate_service: EstateValuationService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test IHT with estate below NRB."""
        today = date.today()

        # Small estate: £300k
        asset = EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.INVESTMENTS,
            description="Small estate",
            estimated_value=Decimal('300000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
            effective_from=today,
            effective_to=None,
            is_deleted=False
        )
        db_session.add(asset)
        await db_session.commit()

        result = await estate_service.calculate_iht(test_user_id)

        assert result['net_estate'] == Decimal('300000.00')
        assert result['standard_nrb'] == Decimal('325000.00')
        assert result['taxable_estate'] == Decimal('0.00')
        assert result['iht_owed'] == Decimal('0.00')

    async def test_calculate_iht_standard_rate(
        self,
        estate_service: EstateValuationService,
        test_user_id,
        sample_assets,
        sample_liabilities
    ):
        """Test IHT at 40% standard rate."""
        result = await estate_service.calculate_iht(
            test_user_id,
            property_to_descendants=False,
            charitable_gifts_percent=Decimal('0')
        )

        # Net estate: £800k
        # NRB: £325k
        # Taxable: £475k
        # IHT at 40%: £190k
        assert result['net_estate'] == Decimal('800000.00')
        assert result['standard_nrb'] == Decimal('325000.00')
        assert result['residence_nrb'] == Decimal('0.00')
        assert result['taxable_estate'] == Decimal('475000.00')
        assert result['iht_rate'] == Decimal('0.40')
        assert result['iht_owed'] == Decimal('190000.00')

    async def test_calculate_iht_charity_rate(
        self,
        estate_service: EstateValuationService,
        test_user_id,
        sample_assets,
        sample_liabilities
    ):
        """Test IHT at 36% reduced rate with >=10% to charity."""
        result = await estate_service.calculate_iht(
            test_user_id,
            property_to_descendants=False,
            charitable_gifts_percent=Decimal('10')
        )

        # Net estate: £800k
        # NRB: £325k
        # Taxable: £475k
        # IHT at 36%: £171k
        assert result['taxable_estate'] == Decimal('475000.00')
        assert result['iht_rate'] == Decimal('0.36')
        assert result['iht_owed'] == Decimal('171000.00')

    async def test_calculate_iht_with_rnrb(
        self,
        estate_service: EstateValuationService,
        test_user_id,
        sample_assets,
        sample_liabilities
    ):
        """Test IHT with Residence NRB."""
        result = await estate_service.calculate_iht(
            test_user_id,
            property_to_descendants=True
        )

        # Net estate: £800k
        # Standard NRB: £325k
        # RNRB: £175k (no taper at £800k)
        # Total NRB: £500k
        # Taxable: £300k
        # IHT at 40%: £120k
        assert result['standard_nrb'] == Decimal('325000.00')
        assert result['residence_nrb'] == Decimal('175000.00')
        assert result['total_nrb'] == Decimal('500000.00')
        assert result['taxable_estate'] == Decimal('300000.00')
        assert result['iht_owed'] == Decimal('120000.00')

    async def test_calculate_iht_with_transferable_nrb(
        self,
        estate_service: EstateValuationService,
        test_user_id,
        sample_assets,
        sample_liabilities
    ):
        """Test IHT with transferable NRB from deceased spouse."""
        result = await estate_service.calculate_iht(
            test_user_id,
            transferable_nrb_percent=Decimal('100'),  # Full spouse NRB
            property_to_descendants=True
        )

        # Standard NRB: £325k
        # Transferable NRB: £325k (100%)
        # RNRB: £175k
        # Total NRB: £825k
        # Net estate: £800k
        # Taxable: £0 (below total NRB)
        # IHT: £0
        assert result['transferable_nrb'] == Decimal('325000.00')
        assert result['total_nrb'] == Decimal('825000.00')
        assert result['taxable_estate'] == Decimal('0.00')
        assert result['iht_owed'] == Decimal('0.00')

    async def test_calculate_iht_partial_transferable_nrb(
        self,
        estate_service: EstateValuationService,
        test_user_id,
        sample_assets,
        sample_liabilities
    ):
        """Test IHT with partial transferable NRB."""
        result = await estate_service.calculate_iht(
            test_user_id,
            transferable_nrb_percent=Decimal('50'),  # 50% of spouse NRB
            property_to_descendants=False
        )

        # Standard NRB: £325k
        # Transferable NRB: £162.5k (50%)
        # Total NRB: £487.5k
        # Net estate: £800k
        # Taxable: £312.5k
        assert result['transferable_nrb'] == Decimal('162500.00')
        assert result['taxable_estate'] == Decimal('312500.00')


class TestIHTCalculationSaving:
    """Tests for saving IHT calculations."""

    async def test_save_iht_calculation(
        self,
        estate_service: EstateValuationService,
        test_user_id,
        sample_assets,
        sample_liabilities
    ):
        """Test saving IHT calculation."""
        # Calculate IHT
        calculation_data = await estate_service.calculate_iht(test_user_id)

        # Save calculation
        saved_calculation = await estate_service.save_iht_calculation(
            test_user_id,
            calculation_data,
            '2024/25'
        )

        assert saved_calculation.id is not None
        assert saved_calculation.user_id == test_user_id
        assert saved_calculation.tax_year == '2024/25'
        assert saved_calculation.net_estate_value == Decimal('800000.00')
        assert saved_calculation.iht_owed == calculation_data['iht_owed']

    async def test_save_iht_calculation_invalid_tax_year(
        self,
        estate_service: EstateValuationService,
        test_user_id
    ):
        """Test saving with invalid tax year format."""
        calculation_data = {
            'gross_estate': Decimal('1000000.00'),
            'net_estate': Decimal('800000.00'),
            'standard_nrb': Decimal('325000.00'),
            'residence_nrb': Decimal('0.00'),
            'transferable_nrb': Decimal('0.00'),
            'total_nrb': Decimal('325000.00'),
            'taxable_estate': Decimal('475000.00'),
            'iht_rate': Decimal('0.40'),
            'iht_owed': Decimal('190000.00')
        }

        with pytest.raises(ValidationError):
            await estate_service.save_iht_calculation(
                test_user_id,
                calculation_data,
                '2024'  # Invalid format
            )


class TestEdgeCases:
    """Tests for edge cases."""

    async def test_zero_estate(
        self,
        estate_service: EstateValuationService,
        test_user_id
    ):
        """Test calculation with zero estate."""
        result = await estate_service.calculate_iht(test_user_id)

        assert result['gross_estate'] == Decimal('0.00')
        assert result['net_estate'] == Decimal('0.00')
        assert result['taxable_estate'] == Decimal('0.00')
        assert result['iht_owed'] == Decimal('0.00')

    async def test_negative_net_estate_prevented(
        self,
        estate_service: EstateValuationService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test that net estate doesn't go negative."""
        today = date.today()

        # Small asset
        asset = EstateAsset(
            id=uuid4(),
            user_id=test_user_id,
            asset_type=AssetType.INVESTMENTS,
            description="Small asset",
            estimated_value=Decimal('50000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
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
            amount_outstanding=Decimal('100000.00'),
            currency='GBP',
            deductible_from_estate=True,
            effective_from=today,
            effective_to=None,
            is_deleted=False
        )

        db_session.add(asset)
        db_session.add(liability)
        await db_session.commit()

        net_estate = await estate_service.calculate_net_estate(test_user_id)

        # Net estate should be negative (assets < liabilities)
        # This is allowed - indicates insolvent estate
        assert net_estate == Decimal('-50000.00')

        # IHT calculation should handle negative net estate
        result = await estate_service.calculate_iht(test_user_id)
        assert result['taxable_estate'] == Decimal('0.00')
        assert result['iht_owed'] == Decimal('0.00')
