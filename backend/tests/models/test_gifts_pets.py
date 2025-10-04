"""
Tests for Gift and IHTExemption models (Task 3.7.2).

Tests cover:
- Gift creation with all gift types (PET, EXEMPT, CHARGEABLE)
- PET period calculation (becomes_exempt_date)
- still_in_pet_period flag logic
- years_remaining_until_exempt calculation
- Taper relief calculation at different time periods
- IHTExemption creation and usage tracking
- Exemption application (annual, carried forward)
- total_exemption_available calculation
- Soft delete functionality for gifts
- Constraints (non-negative values)
- 7-year rule edge cases
"""

import pytest
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import User, Gift, IHTExemption, GiftType, ExemptionType
from models.user import UserStatus, CountryPreference


@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email='gift_test@example.com',
        first_name='Gift',
        last_name='Tester',
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=date.today()
    )
    db_session.add(user)
    db_session.commit()
    return user


class TestGiftModel:
    """Tests for Gift model."""

    def test_create_pet_gift(self, db_session, test_user):
        """Test creating a Potentially Exempt Transfer (PET) gift."""
        gift_date = date.today() - relativedelta(years=2)
        gift = Gift(
            user_id=test_user.id,
            recipient='John Smith',
            gift_date=gift_date,
            gift_value=Decimal('50000.00'),
            currency='GBP',
            gift_type=GiftType.PET,
            description='Cash gift to son'
        )
        db_session.add(gift)
        db_session.commit()

        assert gift.id is not None
        assert gift.recipient == 'John Smith'
        assert gift.gift_value == Decimal('50000.00')
        assert gift.gift_type == GiftType.PET
        assert gift.is_deleted is False

    def test_create_exempt_gift_spouse(self, db_session, test_user):
        """Test creating an exempt gift to spouse."""
        gift = Gift(
            user_id=test_user.id,
            recipient='Spouse',
            gift_date=date.today(),
            gift_value=Decimal('100000.00'),
            currency='GBP',
            gift_type=GiftType.EXEMPT,
            exemption_type=ExemptionType.SPOUSE
        )
        db_session.add(gift)
        db_session.commit()

        assert gift.gift_type == GiftType.EXEMPT
        assert gift.exemption_type == ExemptionType.SPOUSE

    def test_create_exempt_gift_charity(self, db_session, test_user):
        """Test creating an exempt gift to charity."""
        gift = Gift(
            user_id=test_user.id,
            recipient='Cancer Research UK',
            gift_date=date.today(),
            gift_value=Decimal('10000.00'),
            currency='GBP',
            gift_type=GiftType.EXEMPT,
            exemption_type=ExemptionType.CHARITY
        )
        db_session.add(gift)
        db_session.commit()

        assert gift.gift_type == GiftType.EXEMPT
        assert gift.exemption_type == ExemptionType.CHARITY

    def test_create_chargeable_gift(self, db_session, test_user):
        """Test creating a chargeable lifetime transfer (CLT)."""
        gift = Gift(
            user_id=test_user.id,
            recipient='Family Trust',
            gift_date=date.today(),
            gift_value=Decimal('400000.00'),
            currency='GBP',
            gift_type=GiftType.CHARGEABLE,
            description='Gift to discretionary trust'
        )
        db_session.add(gift)
        db_session.commit()

        assert gift.gift_type == GiftType.CHARGEABLE

    def test_calculate_becomes_exempt_date(self, db_session, test_user):
        """Test calculation of becomes_exempt_date for PET."""
        gift_date = date(2020, 6, 15)
        gift = Gift(
            user_id=test_user.id,
            recipient='Daughter',
            gift_date=gift_date,
            gift_value=Decimal('30000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )

        exempt_date = gift.calculate_becomes_exempt_date()
        expected_date = date(2027, 6, 15)  # 7 years later

        assert exempt_date == expected_date

    def test_becomes_exempt_date_none_for_exempt_gift(self, db_session, test_user):
        """Test that becomes_exempt_date is None for EXEMPT gifts."""
        gift = Gift(
            user_id=test_user.id,
            recipient='Spouse',
            gift_date=date.today(),
            gift_value=Decimal('50000.00'),
            currency='GBP',
            gift_type=GiftType.EXEMPT,
            exemption_type=ExemptionType.SPOUSE
        )

        exempt_date = gift.calculate_becomes_exempt_date()
        assert exempt_date is None

    def test_is_still_in_pet_period_true(self, db_session, test_user):
        """Test still_in_pet_period returns True for recent PET."""
        gift_date = date.today() - relativedelta(years=2)
        gift = Gift(
            user_id=test_user.id,
            recipient='Son',
            gift_date=gift_date,
            gift_value=Decimal('40000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )

        assert gift.is_still_in_pet_period() is True

    def test_is_still_in_pet_period_false(self, db_session, test_user):
        """Test still_in_pet_period returns False for old PET."""
        gift_date = date.today() - relativedelta(years=8)  # 8 years ago
        gift = Gift(
            user_id=test_user.id,
            recipient='Nephew',
            gift_date=gift_date,
            gift_value=Decimal('25000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )

        assert gift.is_still_in_pet_period() is False

    def test_is_still_in_pet_period_none_for_exempt(self, db_session, test_user):
        """Test still_in_pet_period returns None for EXEMPT gifts."""
        gift = Gift(
            user_id=test_user.id,
            recipient='Charity',
            gift_date=date.today(),
            gift_value=Decimal('5000.00'),
            currency='GBP',
            gift_type=GiftType.EXEMPT,
            exemption_type=ExemptionType.CHARITY
        )

        assert gift.is_still_in_pet_period() is None

    def test_years_remaining_until_exempt(self, db_session, test_user):
        """Test calculation of years remaining until exempt."""
        gift_date = date.today() - relativedelta(years=3, months=6)
        gift = Gift(
            user_id=test_user.id,
            recipient='Friend',
            gift_date=gift_date,
            gift_value=Decimal('20000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )

        years_remaining = gift.years_remaining_until_exempt()

        # Should be approximately 3.5 years remaining (7 - 3.5 = 3.5)
        assert years_remaining > Decimal('3.0')
        assert years_remaining < Decimal('4.0')

    def test_years_remaining_zero_for_old_pet(self, db_session, test_user):
        """Test years_remaining_until_exempt returns 0 for old PET."""
        gift_date = date.today() - relativedelta(years=10)
        gift = Gift(
            user_id=test_user.id,
            recipient='Niece',
            gift_date=gift_date,
            gift_value=Decimal('15000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )

        years_remaining = gift.years_remaining_until_exempt()
        assert years_remaining == Decimal('0.00')

    def test_years_remaining_zero_for_exempt(self, db_session, test_user):
        """Test years_remaining_until_exempt returns 0 for EXEMPT gifts."""
        gift = Gift(
            user_id=test_user.id,
            recipient='Spouse',
            gift_date=date.today(),
            gift_value=Decimal('50000.00'),
            currency='GBP',
            gift_type=GiftType.EXEMPT,
            exemption_type=ExemptionType.SPOUSE
        )

        years_remaining = gift.years_remaining_until_exempt()
        assert years_remaining == Decimal('0.00')

    def test_taper_relief_0_3_years(self, db_session, test_user):
        """Test taper relief for gift made 0-3 years ago (0% relief)."""
        gift_date = date.today() - relativedelta(years=2)
        gift = Gift(
            user_id=test_user.id,
            recipient='Son',
            gift_date=gift_date,
            gift_value=Decimal('50000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )

        taper_relief = gift.calculate_taper_relief()
        assert taper_relief == Decimal('0.00')  # 0% relief

    def test_taper_relief_3_4_years(self, db_session, test_user):
        """Test taper relief for gift made 3-4 years ago (20% relief)."""
        gift_date = date.today() - relativedelta(years=3, months=6)
        gift = Gift(
            user_id=test_user.id,
            recipient='Daughter',
            gift_date=gift_date,
            gift_value=Decimal('60000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )

        taper_relief = gift.calculate_taper_relief()
        assert taper_relief == Decimal('0.20')  # 20% relief

    def test_taper_relief_4_5_years(self, db_session, test_user):
        """Test taper relief for gift made 4-5 years ago (40% relief)."""
        gift_date = date.today() - relativedelta(years=4, months=6)
        gift = Gift(
            user_id=test_user.id,
            recipient='Grandson',
            gift_date=gift_date,
            gift_value=Decimal('70000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )

        taper_relief = gift.calculate_taper_relief()
        assert taper_relief == Decimal('0.40')  # 40% relief

    def test_taper_relief_5_6_years(self, db_session, test_user):
        """Test taper relief for gift made 5-6 years ago (60% relief)."""
        gift_date = date.today() - relativedelta(years=5, months=6)
        gift = Gift(
            user_id=test_user.id,
            recipient='Nephew',
            gift_date=gift_date,
            gift_value=Decimal('80000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )

        taper_relief = gift.calculate_taper_relief()
        assert taper_relief == Decimal('0.60')  # 60% relief

    def test_taper_relief_6_7_years(self, db_session, test_user):
        """Test taper relief for gift made 6-7 years ago (80% relief)."""
        gift_date = date.today() - relativedelta(years=6, months=6)
        gift = Gift(
            user_id=test_user.id,
            recipient='Friend',
            gift_date=gift_date,
            gift_value=Decimal('90000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )

        taper_relief = gift.calculate_taper_relief()
        assert taper_relief == Decimal('0.80')  # 80% relief

    def test_taper_relief_7_plus_years(self, db_session, test_user):
        """Test taper relief for gift made 7+ years ago (100% relief)."""
        gift_date = date.today() - relativedelta(years=8)
        gift = Gift(
            user_id=test_user.id,
            recipient='Niece',
            gift_date=gift_date,
            gift_value=Decimal('100000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )

        taper_relief = gift.calculate_taper_relief()
        assert taper_relief == Decimal('1.00')  # 100% relief (exempt)

    def test_taper_relief_exempt_gift(self, db_session, test_user):
        """Test taper relief for EXEMPT gift (always 100%)."""
        gift = Gift(
            user_id=test_user.id,
            recipient='Charity',
            gift_date=date.today(),
            gift_value=Decimal('10000.00'),
            currency='GBP',
            gift_type=GiftType.EXEMPT,
            exemption_type=ExemptionType.CHARITY
        )

        taper_relief = gift.calculate_taper_relief()
        assert taper_relief == Decimal('1.00')  # 100% relief

    def test_taper_relief_chargeable_gift(self, db_session, test_user):
        """Test taper relief for CHARGEABLE gift (0%)."""
        gift = Gift(
            user_id=test_user.id,
            recipient='Trust',
            gift_date=date.today(),
            gift_value=Decimal('400000.00'),
            currency='GBP',
            gift_type=GiftType.CHARGEABLE
        )

        taper_relief = gift.calculate_taper_relief()
        assert taper_relief == Decimal('0.00')  # 0% relief for CLTs

    def test_soft_delete(self, db_session, test_user):
        """Test soft delete functionality."""
        gift = Gift(
            user_id=test_user.id,
            recipient='Brother',
            gift_date=date.today(),
            gift_value=Decimal('5000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )
        db_session.add(gift)
        db_session.commit()

        # Soft delete
        gift.is_deleted = True
        db_session.commit()

        assert gift.is_deleted is True
        assert gift.id is not None  # Still exists in database

    def test_currency_validation(self, db_session, test_user):
        """Test currency code validation (must be 3 characters)."""
        gift = Gift(
            user_id=test_user.id,
            recipient='Friend',
            gift_date=date.today(),
            gift_value=Decimal('1000.00'),
            currency='USD',  # Valid 3-char code
            gift_type=GiftType.PET
        )
        db_session.add(gift)
        db_session.commit()

        assert gift.currency == 'USD'

    def test_negative_gift_value_constraint(self, db_session, test_user):
        """Test that negative gift values are rejected."""
        gift = Gift(
            user_id=test_user.id,
            recipient='Test',
            gift_date=date.today(),
            gift_value=Decimal('-1000.00'),  # Negative value
            currency='GBP',
            gift_type=GiftType.PET
        )
        db_session.add(gift)

        with pytest.raises(Exception):  # Should raise constraint violation
            db_session.commit()
        db_session.rollback()

    def test_gift_repr(self, db_session, test_user):
        """Test Gift __repr__ method."""
        gift = Gift(
            user_id=test_user.id,
            recipient='Test Recipient',
            gift_date=date.today(),
            gift_value=Decimal('10000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )

        repr_str = repr(gift)
        assert 'Gift' in repr_str
        assert 'Test Recipient' in repr_str
        assert 'PET' in repr_str


class TestIHTExemptionModel:
    """Tests for IHTExemption model."""

    def test_create_iht_exemption(self, db_session, test_user):
        """Test creating an IHTExemption record."""
        exemption = IHTExemption(
            user_id=test_user.id,
            tax_year='2024/25',
            annual_exemption_limit=Decimal('3000.00'),
            annual_exemption_used=Decimal('0.00'),
            annual_exemption_remaining=Decimal('3000.00'),
            carried_forward_from_previous_year=Decimal('0.00')
        )
        db_session.add(exemption)
        db_session.commit()

        assert exemption.id is not None
        assert exemption.tax_year == '2024/25'
        assert exemption.annual_exemption_limit == Decimal('3000.00')
        assert exemption.annual_exemption_remaining == Decimal('3000.00')

    def test_total_exemption_available(self, db_session, test_user):
        """Test total_exemption_available calculation."""
        exemption = IHTExemption(
            user_id=test_user.id,
            tax_year='2024/25',
            annual_exemption_limit=Decimal('3000.00'),
            annual_exemption_used=Decimal('1000.00'),
            annual_exemption_remaining=Decimal('2000.00'),
            carried_forward_from_previous_year=Decimal('1500.00')
        )

        total_available = exemption.total_exemption_available()
        assert total_available == Decimal('3500.00')  # 2000 + 1500

    def test_apply_exemption_current_year_only(self, db_session, test_user):
        """Test applying exemption from current year only."""
        exemption = IHTExemption(
            user_id=test_user.id,
            tax_year='2024/25',
            annual_exemption_limit=Decimal('3000.00'),
            annual_exemption_used=Decimal('0.00'),
            annual_exemption_remaining=Decimal('3000.00'),
            carried_forward_from_previous_year=Decimal('0.00')
        )

        applied = exemption.apply_exemption(Decimal('2000.00'))

        assert applied == Decimal('2000.00')
        assert exemption.annual_exemption_used == Decimal('2000.00')
        assert exemption.annual_exemption_remaining == Decimal('1000.00')
        assert exemption.carried_forward_from_previous_year == Decimal('0.00')

    def test_apply_exemption_with_carry_forward(self, db_session, test_user):
        """Test applying exemption using current year + carried forward."""
        exemption = IHTExemption(
            user_id=test_user.id,
            tax_year='2024/25',
            annual_exemption_limit=Decimal('3000.00'),
            annual_exemption_used=Decimal('0.00'),
            annual_exemption_remaining=Decimal('3000.00'),
            carried_forward_from_previous_year=Decimal('2000.00')
        )

        applied = exemption.apply_exemption(Decimal('4500.00'))

        # Should use all current year (3000) + 1500 from carried forward
        assert applied == Decimal('4500.00')
        assert exemption.annual_exemption_used == Decimal('3000.00')
        assert exemption.annual_exemption_remaining == Decimal('0.00')
        assert exemption.carried_forward_from_previous_year == Decimal('500.00')

    def test_apply_exemption_exceeds_total(self, db_session, test_user):
        """Test applying exemption when amount exceeds total available."""
        exemption = IHTExemption(
            user_id=test_user.id,
            tax_year='2024/25',
            annual_exemption_limit=Decimal('3000.00'),
            annual_exemption_used=Decimal('0.00'),
            annual_exemption_remaining=Decimal('3000.00'),
            carried_forward_from_previous_year=Decimal('1000.00')
        )

        applied = exemption.apply_exemption(Decimal('6000.00'))

        # Should use all available (3000 + 1000 = 4000)
        assert applied == Decimal('4000.00')
        assert exemption.annual_exemption_remaining == Decimal('0.00')
        assert exemption.carried_forward_from_previous_year == Decimal('0.00')

    def test_tax_year_format_validation(self, db_session, test_user):
        """Test tax year format validation (YYYY/YY)."""
        exemption = IHTExemption(
            user_id=test_user.id,
            tax_year='2024/25',  # Valid format
            annual_exemption_limit=Decimal('3000.00')
        )
        db_session.add(exemption)
        db_session.commit()

        assert exemption.tax_year == '2024/25'

    def test_invalid_tax_year_format(self, db_session, test_user):
        """Test that invalid tax year format is rejected."""
        with pytest.raises(ValueError, match="Invalid UK tax year format"):
            exemption = IHTExemption(
                user_id=test_user.id,
                tax_year='2024',  # Invalid format
                annual_exemption_limit=Decimal('3000.00')
            )

    def test_unique_user_tax_year_constraint(self, db_session, test_user):
        """Test unique constraint on user_id + tax_year."""
        exemption1 = IHTExemption(
            user_id=test_user.id,
            tax_year='2024/25',
            annual_exemption_limit=Decimal('3000.00')
        )
        db_session.add(exemption1)
        db_session.commit()

        # Try to create duplicate
        exemption2 = IHTExemption(
            user_id=test_user.id,
            tax_year='2024/25',  # Same tax year
            annual_exemption_limit=Decimal('3000.00')
        )
        db_session.add(exemption2)

        with pytest.raises(Exception):  # Should raise unique constraint violation
            db_session.commit()
        db_session.rollback()

    def test_negative_exemption_amounts_constraint(self, db_session, test_user):
        """Test that negative exemption amounts are rejected."""
        exemption = IHTExemption(
            user_id=test_user.id,
            tax_year='2024/25',
            annual_exemption_limit=Decimal('3000.00'),
            annual_exemption_used=Decimal('-500.00')  # Negative value
        )
        db_session.add(exemption)

        with pytest.raises(Exception):  # Should raise constraint violation
            db_session.commit()
        db_session.rollback()

    def test_iht_exemption_repr(self, db_session, test_user):
        """Test IHTExemption __repr__ method."""
        exemption = IHTExemption(
            user_id=test_user.id,
            tax_year='2024/25',
            annual_exemption_limit=Decimal('3000.00'),
            annual_exemption_remaining=Decimal('2500.00')
        )

        repr_str = repr(exemption)
        assert 'IHTExemption' in repr_str
        assert '2024/25' in repr_str


class TestGiftAndExemptionIntegration:
    """Integration tests for Gift and IHTExemption working together."""

    def test_track_multiple_gifts_with_exemptions(self, db_session, test_user):
        """Test tracking multiple gifts and exemption usage."""
        # Create exemption record
        exemption = IHTExemption(
            user_id=test_user.id,
            tax_year='2024/25',
            annual_exemption_limit=Decimal('3000.00'),
            annual_exemption_used=Decimal('0.00'),
            annual_exemption_remaining=Decimal('3000.00'),
            carried_forward_from_previous_year=Decimal('0.00')
        )
        db_session.add(exemption)

        # Create multiple gifts
        gift1 = Gift(
            user_id=test_user.id,
            recipient='Child',
            gift_date=date.today(),
            gift_value=Decimal('10000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )
        gift2 = Gift(
            user_id=test_user.id,
            recipient='Friend',
            gift_date=date.today(),
            gift_value=Decimal('5000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )
        gift3 = Gift(
            user_id=test_user.id,
            recipient='Charity',
            gift_date=date.today(),
            gift_value=Decimal('2000.00'),
            currency='GBP',
            gift_type=GiftType.EXEMPT,
            exemption_type=ExemptionType.CHARITY
        )

        db_session.add_all([gift1, gift2, gift3])
        db_session.commit()

        # Verify all gifts were created
        user_gifts = db_session.query(Gift).filter_by(user_id=test_user.id).all()
        assert len(user_gifts) == 3

    def test_seven_year_rule_edge_cases(self, db_session, test_user):
        """Test 7-year rule edge cases."""
        # Gift exactly 7 years ago (should be exempt)
        gift_7_years = Gift(
            user_id=test_user.id,
            recipient='Test',
            gift_date=date.today() - relativedelta(years=7),
            gift_value=Decimal('20000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )

        assert gift_7_years.is_still_in_pet_period() is False
        assert gift_7_years.calculate_taper_relief() == Decimal('1.00')

        # Gift 7 years minus 1 day (should still be in period)
        gift_almost_7_years = Gift(
            user_id=test_user.id,
            recipient='Test2',
            gift_date=date.today() - relativedelta(years=7) + timedelta(days=1),
            gift_value=Decimal('25000.00'),
            currency='GBP',
            gift_type=GiftType.PET
        )

        assert gift_almost_7_years.is_still_in_pet_period() is True
        assert gift_almost_7_years.calculate_taper_relief() == Decimal('0.80')  # 6-7 years
