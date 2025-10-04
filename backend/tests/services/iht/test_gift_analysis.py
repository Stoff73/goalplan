"""
Tests for Gift Analysis Service

Tests cover:
- Gift recording with classification (PET, EXEMPT, CHARGEABLE)
- Exemption application (annual, small gifts, wedding)
- 7-year PET period tracking
- Taper relief calculation at all time bands
- Potential IHT calculation on PETs
- Edge cases (zero values, date boundaries)
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4
from dateutil.relativedelta import relativedelta

from sqlalchemy.ext.asyncio import AsyncSession

from models.estate_iht import Gift, GiftType, ExemptionType, IHTExemption
from services.iht.gift_analysis_service import (
    GiftAnalysisService, ValidationError
)


@pytest.fixture
async def gift_service(db_session: AsyncSession):
    """Create gift analysis service instance."""
    return GiftAnalysisService(db_session)


@pytest.fixture
async def test_user_id():
    """Generate test user ID."""
    return uuid4()


class TestGiftRecording:
    """Tests for gift recording."""

    async def test_record_pet_gift(
        self,
        gift_service: GiftAnalysisService,
        test_user_id
    ):
        """Test recording a basic PET gift."""
        gift_data = {
            'recipient': 'John Doe',
            'gift_date': date.today() - timedelta(days=365),
            'gift_value': Decimal('50000.00'),
            'currency': 'GBP',
            'description': 'Cash gift to son'
        }

        gift = await gift_service.record_gift(test_user_id, gift_data)

        assert gift.id is not None
        assert gift.user_id == test_user_id
        assert gift.recipient == 'John Doe'
        assert gift.gift_value == Decimal('50000.00')
        assert gift.gift_type == GiftType.PET
        assert gift.still_in_pet_period is True
        # becomes_exempt_date should be gift_date + 7 years
        expected_exempt_date = gift_data['gift_date'] + relativedelta(years=7)
        assert gift.becomes_exempt_date == expected_exempt_date

    async def test_record_spouse_exempt_gift(
        self,
        gift_service: GiftAnalysisService,
        test_user_id
    ):
        """Test recording gift to spouse (immediately exempt)."""
        gift_data = {
            'recipient': 'Jane Doe (spouse)',
            'gift_date': date.today() - timedelta(days=100),
            'gift_value': Decimal('100000.00'),
            'exemption_type': ExemptionType.SPOUSE
        }

        gift = await gift_service.record_gift(test_user_id, gift_data)

        assert gift.gift_type == GiftType.EXEMPT
        assert gift.exemption_type == ExemptionType.SPOUSE
        assert gift.still_in_pet_period is False
        # Exempt gifts have becomes_exempt_date = gift_date
        assert gift.becomes_exempt_date == gift_data['gift_date']

    async def test_record_charity_exempt_gift(
        self,
        gift_service: GiftAnalysisService,
        test_user_id
    ):
        """Test recording gift to charity (immediately exempt)."""
        gift_data = {
            'recipient': 'Cancer Research UK',
            'gift_date': date.today() - timedelta(days=200),
            'gift_value': Decimal('25000.00'),
            'exemption_type': ExemptionType.CHARITY
        }

        gift = await gift_service.record_gift(test_user_id, gift_data)

        assert gift.gift_type == GiftType.EXEMPT
        assert gift.exemption_type == ExemptionType.CHARITY

    async def test_record_gift_validation_negative_value(
        self,
        gift_service: GiftAnalysisService,
        test_user_id
    ):
        """Test gift recording fails with negative value."""
        gift_data = {
            'recipient': 'John Doe',
            'gift_date': date.today(),
            'gift_value': Decimal('-1000.00')
        }

        with pytest.raises(ValidationError):
            await gift_service.record_gift(test_user_id, gift_data)

    async def test_record_gift_validation_future_date(
        self,
        gift_service: GiftAnalysisService,
        test_user_id
    ):
        """Test gift recording fails with future date."""
        gift_data = {
            'recipient': 'John Doe',
            'gift_date': date.today() + timedelta(days=365),
            'gift_value': Decimal('10000.00')
        }

        with pytest.raises(ValidationError):
            await gift_service.record_gift(test_user_id, gift_data)

    async def test_record_gift_missing_required_field(
        self,
        gift_service: GiftAnalysisService,
        test_user_id
    ):
        """Test gift recording fails with missing required field."""
        gift_data = {
            'recipient': 'John Doe',
            # Missing gift_date
            'gift_value': Decimal('10000.00')
        }

        with pytest.raises(ValidationError):
            await gift_service.record_gift(test_user_id, gift_data)


class TestPETPeriodTracking:
    """Tests for 7-year PET period tracking."""

    async def test_get_gifts_in_pet_period(
        self,
        gift_service: GiftAnalysisService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test getting gifts still in PET period."""
        today = date.today()

        # Gift within PET period (1 year ago)
        recent_gift = Gift(
            id=uuid4(),
            user_id=test_user_id,
            recipient='Alice',
            gift_date=today - relativedelta(years=1),
            gift_value=Decimal('50000.00'),
            currency='GBP',
            gift_type=GiftType.PET,
            becomes_exempt_date=today + relativedelta(years=6),
            still_in_pet_period=True,
            is_deleted=False
        )

        # Gift outside PET period (8 years ago)
        old_gift = Gift(
            id=uuid4(),
            user_id=test_user_id,
            recipient='Bob',
            gift_date=today - relativedelta(years=8),
            gift_value=Decimal('30000.00'),
            currency='GBP',
            gift_type=GiftType.PET,
            becomes_exempt_date=today - relativedelta(years=1),
            still_in_pet_period=False,
            is_deleted=False
        )

        db_session.add(recent_gift)
        db_session.add(old_gift)
        await db_session.commit()

        gifts_in_period = await gift_service.get_gifts_in_pet_period(test_user_id)

        assert len(gifts_in_period) == 1
        assert gifts_in_period[0].recipient == 'Alice'

    async def test_get_gifts_in_pet_period_empty(
        self,
        gift_service: GiftAnalysisService,
        test_user_id
    ):
        """Test getting PET gifts with no gifts in period."""
        gifts_in_period = await gift_service.get_gifts_in_pet_period(test_user_id)

        assert len(gifts_in_period) == 0

    async def test_get_gifts_in_pet_period_sorted_by_date(
        self,
        gift_service: GiftAnalysisService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test gifts are returned sorted by gift_date (oldest first)."""
        today = date.today()

        # Create gifts in random order
        gift2 = Gift(
            id=uuid4(),
            user_id=test_user_id,
            recipient='Gift 2',
            gift_date=today - relativedelta(years=2),
            gift_value=Decimal('20000.00'),
            currency='GBP',
            gift_type=GiftType.PET,
            becomes_exempt_date=today + relativedelta(years=5),
            still_in_pet_period=True,
            is_deleted=False
        )

        gift1 = Gift(
            id=uuid4(),
            user_id=test_user_id,
            recipient='Gift 1',
            gift_date=today - relativedelta(years=5),
            gift_value=Decimal('30000.00'),
            currency='GBP',
            gift_type=GiftType.PET,
            becomes_exempt_date=today + relativedelta(years=2),
            still_in_pet_period=True,
            is_deleted=False
        )

        gift3 = Gift(
            id=uuid4(),
            user_id=test_user_id,
            recipient='Gift 3',
            gift_date=today - relativedelta(years=1),
            gift_value=Decimal('10000.00'),
            currency='GBP',
            gift_type=GiftType.PET,
            becomes_exempt_date=today + relativedelta(years=6),
            still_in_pet_period=True,
            is_deleted=False
        )

        db_session.add(gift2)
        db_session.add(gift1)
        db_session.add(gift3)
        await db_session.commit()

        gifts = await gift_service.get_gifts_in_pet_period(test_user_id)

        assert len(gifts) == 3
        # Should be sorted oldest to newest
        assert gifts[0].recipient == 'Gift 1'
        assert gifts[1].recipient == 'Gift 2'
        assert gifts[2].recipient == 'Gift 3'


class TestTaperReliefCalculation:
    """Tests for taper relief calculation."""

    async def test_calculate_potential_iht_no_taper(
        self,
        gift_service: GiftAnalysisService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test potential IHT with no taper relief (0-3 years)."""
        death_date = date.today()
        gift_date = death_date - relativedelta(years=2)

        gift = Gift(
            id=uuid4(),
            user_id=test_user_id,
            recipient='Alice',
            gift_date=gift_date,
            gift_value=Decimal('100000.00'),
            currency='GBP',
            gift_type=GiftType.PET,
            becomes_exempt_date=gift_date + relativedelta(years=7),
            still_in_pet_period=True,
            is_deleted=False
        )
        db_session.add(gift)
        await db_session.commit()

        calculations = await gift_service.calculate_potential_iht_on_pets(
            test_user_id,
            death_date
        )

        assert len(calculations) == 1
        calc = calculations[0]
        assert calc['gift_value'] == Decimal('100000.00')
        assert calc['taper_relief_percent'] == Decimal('0.00')  # 0% relief
        assert calc['effective_iht_rate'] == Decimal('0.40')  # Full 40%
        assert calc['potential_iht'] == Decimal('40000.00')  # £100k * 40%

    async def test_calculate_potential_iht_20_percent_taper(
        self,
        gift_service: GiftAnalysisService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test potential IHT with 20% taper relief (3-4 years)."""
        death_date = date.today()
        gift_date = death_date - relativedelta(years=3, months=6)

        gift = Gift(
            id=uuid4(),
            user_id=test_user_id,
            recipient='Bob',
            gift_date=gift_date,
            gift_value=Decimal('100000.00'),
            currency='GBP',
            gift_type=GiftType.PET,
            becomes_exempt_date=gift_date + relativedelta(years=7),
            still_in_pet_period=True,
            is_deleted=False
        )
        db_session.add(gift)
        await db_session.commit()

        calculations = await gift_service.calculate_potential_iht_on_pets(
            test_user_id,
            death_date
        )

        calc = calculations[0]
        assert calc['taper_relief_percent'] == Decimal('0.20')  # 20% relief
        assert calc['effective_iht_rate'] == Decimal('0.32')  # 40% * (1 - 0.20)
        assert calc['potential_iht'] == Decimal('32000.00')  # £100k * 32%

    async def test_calculate_potential_iht_40_percent_taper(
        self,
        gift_service: GiftAnalysisService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test potential IHT with 40% taper relief (4-5 years)."""
        death_date = date.today()
        gift_date = death_date - relativedelta(years=4, months=6)

        gift = Gift(
            id=uuid4(),
            user_id=test_user_id,
            recipient='Charlie',
            gift_date=gift_date,
            gift_value=Decimal('100000.00'),
            currency='GBP',
            gift_type=GiftType.PET,
            becomes_exempt_date=gift_date + relativedelta(years=7),
            still_in_pet_period=True,
            is_deleted=False
        )
        db_session.add(gift)
        await db_session.commit()

        calculations = await gift_service.calculate_potential_iht_on_pets(
            test_user_id,
            death_date
        )

        calc = calculations[0]
        assert calc['taper_relief_percent'] == Decimal('0.40')  # 40% relief
        assert calc['effective_iht_rate'] == Decimal('0.24')  # 40% * (1 - 0.40)
        assert calc['potential_iht'] == Decimal('24000.00')  # £100k * 24%

    async def test_calculate_potential_iht_60_percent_taper(
        self,
        gift_service: GiftAnalysisService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test potential IHT with 60% taper relief (5-6 years)."""
        death_date = date.today()
        gift_date = death_date - relativedelta(years=5, months=6)

        gift = Gift(
            id=uuid4(),
            user_id=test_user_id,
            recipient='Diana',
            gift_date=gift_date,
            gift_value=Decimal('100000.00'),
            currency='GBP',
            gift_type=GiftType.PET,
            becomes_exempt_date=gift_date + relativedelta(years=7),
            still_in_pet_period=True,
            is_deleted=False
        )
        db_session.add(gift)
        await db_session.commit()

        calculations = await gift_service.calculate_potential_iht_on_pets(
            test_user_id,
            death_date
        )

        calc = calculations[0]
        assert calc['taper_relief_percent'] == Decimal('0.60')  # 60% relief
        assert calc['effective_iht_rate'] == Decimal('0.16')  # 40% * (1 - 0.60)
        assert calc['potential_iht'] == Decimal('16000.00')  # £100k * 16%

    async def test_calculate_potential_iht_80_percent_taper(
        self,
        gift_service: GiftAnalysisService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test potential IHT with 80% taper relief (6-7 years)."""
        death_date = date.today()
        gift_date = death_date - relativedelta(years=6, months=6)

        gift = Gift(
            id=uuid4(),
            user_id=test_user_id,
            recipient='Edward',
            gift_date=gift_date,
            gift_value=Decimal('100000.00'),
            currency='GBP',
            gift_type=GiftType.PET,
            becomes_exempt_date=gift_date + relativedelta(years=7),
            still_in_pet_period=True,
            is_deleted=False
        )
        db_session.add(gift)
        await db_session.commit()

        calculations = await gift_service.calculate_potential_iht_on_pets(
            test_user_id,
            death_date
        )

        calc = calculations[0]
        assert calc['taper_relief_percent'] == Decimal('0.80')  # 80% relief
        assert calc['effective_iht_rate'] == Decimal('0.08')  # 40% * (1 - 0.80)
        assert calc['potential_iht'] == Decimal('8000.00')  # £100k * 8%


class TestExemptionApplication:
    """Tests for exemption application."""

    async def test_apply_annual_exemption_full(
        self,
        gift_service: GiftAnalysisService,
        test_user_id
    ):
        """Test applying annual exemption fully covers gift."""
        result = await gift_service.apply_exemptions(
            test_user_id,
            Decimal('3000.00'),  # Exactly annual limit
            2024,
            "ANNUAL_EXEMPTION"
        )

        assert result['exemption_applied'] == Decimal('3000.00')
        assert result['remaining_gift_value'] == Decimal('0.00')
        assert result['exemption_remaining'] == Decimal('0.00')

    async def test_apply_annual_exemption_partial(
        self,
        gift_service: GiftAnalysisService,
        test_user_id
    ):
        """Test applying annual exemption partially covers gift."""
        result = await gift_service.apply_exemptions(
            test_user_id,
            Decimal('5000.00'),  # More than annual limit
            2024,
            "ANNUAL_EXEMPTION"
        )

        assert result['exemption_applied'] == Decimal('3000.00')
        assert result['remaining_gift_value'] == Decimal('2000.00')

    async def test_apply_annual_exemption_multiple_gifts(
        self,
        gift_service: GiftAnalysisService,
        test_user_id
    ):
        """Test annual exemption depletes across multiple gifts."""
        # First gift: £2,000
        result1 = await gift_service.apply_exemptions(
            test_user_id,
            Decimal('2000.00'),
            2024,
            "ANNUAL_EXEMPTION"
        )
        assert result1['exemption_applied'] == Decimal('2000.00')
        assert result1['exemption_remaining'] == Decimal('1000.00')

        # Second gift: £1,500 (only £1,000 available)
        result2 = await gift_service.apply_exemptions(
            test_user_id,
            Decimal('1500.00'),
            2024,
            "ANNUAL_EXEMPTION"
        )
        assert result2['exemption_applied'] == Decimal('1000.00')
        assert result2['remaining_gift_value'] == Decimal('500.00')
        assert result2['exemption_remaining'] == Decimal('0.00')

    async def test_apply_small_gifts_exemption(
        self,
        gift_service: GiftAnalysisService,
        test_user_id
    ):
        """Test applying small gifts exemption."""
        result = await gift_service.apply_exemptions(
            test_user_id,
            Decimal('250.00'),
            2024,
            "SMALL_GIFTS"
        )

        assert result['exemption_applied'] == Decimal('250.00')
        assert result['remaining_gift_value'] == Decimal('0.00')

    async def test_get_exemption_status_no_usage(
        self,
        gift_service: GiftAnalysisService,
        test_user_id
    ):
        """Test getting exemption status with no usage."""
        status = await gift_service.get_exemption_status(
            test_user_id,
            '2024/25'
        )

        assert status['annual_exemption_limit'] == Decimal('3000.00')
        assert status['annual_exemption_used'] == Decimal('0.00')
        assert status['annual_exemption_remaining'] == Decimal('3000.00')
        assert status['total_available'] == Decimal('3000.00')

    async def test_get_exemption_status_with_usage(
        self,
        gift_service: GiftAnalysisService,
        test_user_id
    ):
        """Test getting exemption status after usage."""
        # Apply exemption
        await gift_service.apply_exemptions(
            test_user_id,
            Decimal('1500.00'),
            2024,
            "ANNUAL_EXEMPTION"
        )

        # Check status
        status = await gift_service.get_exemption_status(
            test_user_id,
            '2024/25'
        )

        assert status['annual_exemption_used'] == Decimal('1500.00')
        assert status['annual_exemption_remaining'] == Decimal('1500.00')


class TestEdgeCases:
    """Tests for edge cases."""

    async def test_calculate_potential_iht_no_pets(
        self,
        gift_service: GiftAnalysisService,
        test_user_id
    ):
        """Test calculating IHT with no PETs."""
        calculations = await gift_service.calculate_potential_iht_on_pets(
            test_user_id
        )

        assert len(calculations) == 0

    async def test_gift_exactly_7_years_ago(
        self,
        gift_service: GiftAnalysisService,
        db_session: AsyncSession,
        test_user_id
    ):
        """Test gift exactly 7 years ago (exempt)."""
        death_date = date.today()
        gift_date = death_date - relativedelta(years=7)

        gift = Gift(
            id=uuid4(),
            user_id=test_user_id,
            recipient='Test',
            gift_date=gift_date,
            gift_value=Decimal('50000.00'),
            currency='GBP',
            gift_type=GiftType.PET,
            becomes_exempt_date=death_date,
            still_in_pet_period=False,
            is_deleted=False
        )
        db_session.add(gift)
        await db_session.commit()

        # Should still be included in calculation (marginal case)
        calculations = await gift_service.calculate_potential_iht_on_pets(
            test_user_id,
            death_date
        )

        # Gift exactly 7 years = 100% taper relief
        calc = calculations[0]
        assert calc['taper_relief_percent'] == Decimal('1.00')
        assert calc['potential_iht'] == Decimal('0.00')
