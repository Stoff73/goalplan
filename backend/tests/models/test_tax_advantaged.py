"""
Tests for TaxAdvantagedInvestment model.

This module tests:
- TaxAdvantagedInvestment model creation and validation
- Tax relief tracking (EIS, SEIS, VCT)
- Holding period calculations (3 years EIS/SEIS, 5 years VCT)
- At-risk flag based on holding period
- CGT deferral and exemption eligibility
- Relief withdrawal tracking
- Constraint violations
- Cascade deletes
- One-to-one relationship with InvestmentHolding
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models.investment import (
    InvestmentAccount,
    InvestmentHolding,
    TaxAdvantagedInvestment,
    AccountType,
    AccountCountry,
    AccountStatus,
    SecurityType,
    AssetClass,
    Region,
    SchemeType
)
from models.user import User, CountryPreference
from dateutil.relativedelta import relativedelta


@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    user = User(
        email=f"test_{uuid.uuid4()}@example.com",
        first_name="Test",
        last_name="User",
        country_preference=CountryPreference.UK,
        terms_accepted_at=datetime.utcnow(),
        email_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_eis_account(db_session, test_user):
    """Create a test EIS account."""
    account = InvestmentAccount(
        user_id=test_user.id,
        account_type=AccountType.EIS,
        provider="EIS Fund Manager",
        country=AccountCountry.UK,
        base_currency="GBP",
        account_open_date=date(2024, 1, 1),
        status=AccountStatus.ACTIVE
    )
    account.set_account_number("EIS123456")
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def test_eis_holding(db_session, test_eis_account):
    """Create a test EIS holding."""
    investment_date = date(2024, 1, 15)
    holding = InvestmentHolding(
        account_id=test_eis_account.id,
        security_type=SecurityType.EIS_SHARE,
        ticker=None,
        security_name="Private Tech Company Ltd",
        quantity=Decimal("10000.0000"),
        purchase_date=investment_date,
        purchase_price=Decimal("1.00"),
        purchase_currency="GBP",
        current_price=Decimal("1.50"),
        asset_class=AssetClass.EQUITY,
        region=Region.UK,
        sector="Technology"
    )
    db_session.add(holding)
    await db_session.commit()
    await db_session.refresh(holding)
    return holding


@pytest.fixture
async def test_vct_account(db_session, test_user):
    """Create a test VCT account."""
    account = InvestmentAccount(
        user_id=test_user.id,
        account_type=AccountType.VCT,
        provider="Octopus VCT",
        country=AccountCountry.UK,
        base_currency="GBP",
        account_open_date=date(2024, 1, 1),
        status=AccountStatus.ACTIVE
    )
    account.set_account_number("VCT987654")
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def test_vct_holding(db_session, test_vct_account):
    """Create a test VCT holding."""
    investment_date = date(2024, 1, 15)
    holding = InvestmentHolding(
        account_id=test_vct_account.id,
        security_type=SecurityType.VCT,
        ticker="OCTV",
        security_name="Octopus AIM VCT",
        quantity=Decimal("5000.0000"),
        purchase_date=investment_date,
        purchase_price=Decimal("1.00"),
        purchase_currency="GBP",
        current_price=Decimal("1.10"),
        asset_class=AssetClass.EQUITY,
        region=Region.UK,
        sector="Venture Capital"
    )
    db_session.add(holding)
    await db_session.commit()
    await db_session.refresh(holding)
    return holding


class TestTaxAdvantagedInvestmentCreation:
    """Test TaxAdvantagedInvestment model creation."""

    @pytest.mark.asyncio
    async def test_create_eis_with_valid_data(self, db_session, test_eis_holding):
        """Test creating an EIS tax-advantaged investment with valid data."""
        investment_date = date(2024, 1, 15)
        investment_amount = Decimal("10000.00")

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=investment_amount,
            income_tax_relief_claimed=Decimal("3000.00"),  # 30% of 10000
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2023/24",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3),
            cgt_exemption_eligible=True
        )

        db_session.add(tax_advantaged)
        await db_session.commit()
        await db_session.refresh(tax_advantaged)

        assert tax_advantaged.id is not None
        assert tax_advantaged.holding_id == test_eis_holding.id
        assert tax_advantaged.scheme_type == SchemeType.EIS
        assert tax_advantaged.investment_amount == investment_amount
        assert tax_advantaged.income_tax_relief_claimed == Decimal("3000.00")
        assert tax_advantaged.income_tax_relief_percentage == Decimal("30.0")
        assert tax_advantaged.minimum_holding_period_years == 3
        assert tax_advantaged.relief_withdrawn is False

    @pytest.mark.asyncio
    async def test_create_seis_with_valid_data(self, db_session, test_eis_holding):
        """Test creating a SEIS tax-advantaged investment with valid data."""
        investment_date = date(2024, 1, 15)
        investment_amount = Decimal("50000.00")

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.SEIS,
            investment_date=investment_date,
            investment_amount=investment_amount,
            income_tax_relief_claimed=Decimal("25000.00"),  # 50% of 50000
            income_tax_relief_percentage=Decimal("50.0"),
            tax_year_claimed="2023/24",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3),
            cgt_exemption_eligible=True
        )

        db_session.add(tax_advantaged)
        await db_session.commit()
        await db_session.refresh(tax_advantaged)

        assert tax_advantaged.scheme_type == SchemeType.SEIS
        assert tax_advantaged.income_tax_relief_percentage == Decimal("50.0")
        assert tax_advantaged.income_tax_relief_claimed == Decimal("25000.00")
        assert tax_advantaged.minimum_holding_period_years == 3

    @pytest.mark.asyncio
    async def test_create_vct_with_valid_data(self, db_session, test_vct_holding):
        """Test creating a VCT tax-advantaged investment with valid data."""
        investment_date = date(2024, 1, 15)
        investment_amount = Decimal("5000.00")

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_vct_holding.id,
            scheme_type=SchemeType.VCT,
            investment_date=investment_date,
            investment_amount=investment_amount,
            income_tax_relief_claimed=Decimal("1500.00"),  # 30% of 5000
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2023/24",
            minimum_holding_period_years=5,  # VCT requires 5 years
            holding_period_end_date=investment_date + relativedelta(years=5),
            cgt_exemption_eligible=False
        )

        db_session.add(tax_advantaged)
        await db_session.commit()
        await db_session.refresh(tax_advantaged)

        assert tax_advantaged.scheme_type == SchemeType.VCT
        assert tax_advantaged.minimum_holding_period_years == 5  # VCT = 5 years
        assert tax_advantaged.income_tax_relief_percentage == Decimal("30.0")

    @pytest.mark.asyncio
    async def test_eis_with_cgt_deferral(self, db_session, test_eis_holding):
        """Test EIS with CGT deferral claimed."""
        investment_date = date(2024, 1, 15)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("20000.00"),
            income_tax_relief_claimed=Decimal("6000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2023/24",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3),
            cgt_deferral_claimed=Decimal("5000.00"),  # Deferred CGT from previous disposal
            cgt_exemption_eligible=True
        )

        db_session.add(tax_advantaged)
        await db_session.commit()
        await db_session.refresh(tax_advantaged)

        assert tax_advantaged.cgt_deferral_claimed == Decimal("5000.00")
        assert tax_advantaged.cgt_exemption_eligible is True


class TestHoldingPeriodCalculations:
    """Test holding period calculation properties."""

    @pytest.mark.asyncio
    async def test_years_held_property(self, db_session, test_eis_holding):
        """Test years_held property calculation."""
        # Investment 2 years ago
        investment_date = date.today() - relativedelta(years=2)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("3000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2021/22",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3)
        )

        db_session.add(tax_advantaged)
        await db_session.commit()
        await db_session.refresh(tax_advantaged)

        # Should be approximately 2 years
        assert abs(tax_advantaged.years_held - Decimal("2.0")) < Decimal("0.1")

    @pytest.mark.asyncio
    async def test_holding_period_remaining_within_period(self, db_session, test_eis_holding):
        """Test holding_period_remaining for investment still within holding period."""
        # Investment 1 year ago, 3-year holding period
        investment_date = date.today() - relativedelta(years=1)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("3000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2022/23",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3)
        )

        db_session.add(tax_advantaged)
        await db_session.commit()
        await db_session.refresh(tax_advantaged)

        # Should have approximately 2 years remaining
        assert abs(tax_advantaged.holding_period_remaining - Decimal("2.0")) < Decimal("0.1")
        assert tax_advantaged.holding_period_remaining > 0

    @pytest.mark.asyncio
    async def test_holding_period_remaining_after_period(self, db_session, test_eis_holding):
        """Test holding_period_remaining after holding period completed."""
        # Investment 4 years ago, 3-year holding period
        investment_date = date.today() - relativedelta(years=4)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("3000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2019/20",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3)
        )

        db_session.add(tax_advantaged)
        await db_session.commit()
        await db_session.refresh(tax_advantaged)

        # Should be 0 (holding period complete)
        assert tax_advantaged.holding_period_remaining == Decimal("0")

    @pytest.mark.asyncio
    async def test_vct_five_year_holding_period(self, db_session, test_vct_holding):
        """Test VCT requires 5-year holding period."""
        # Investment 3 years ago, 5-year holding period
        investment_date = date.today() - relativedelta(years=3)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_vct_holding.id,
            scheme_type=SchemeType.VCT,
            investment_date=investment_date,
            investment_amount=Decimal("5000.00"),
            income_tax_relief_claimed=Decimal("1500.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2020/21",
            minimum_holding_period_years=5,
            holding_period_end_date=investment_date + relativedelta(years=5)
        )

        db_session.add(tax_advantaged)
        await db_session.commit()
        await db_session.refresh(tax_advantaged)

        # Should have approximately 2 years remaining (5 - 3)
        assert abs(tax_advantaged.holding_period_remaining - Decimal("2.0")) < Decimal("0.1")
        assert tax_advantaged.holding_period_remaining > 0


class TestAtRiskFlag:
    """Test at_risk_of_losing_relief property."""

    @pytest.mark.asyncio
    async def test_at_risk_within_holding_period(self, db_session, test_eis_holding):
        """Test at_risk is True when within holding period."""
        investment_date = date.today() - relativedelta(years=1)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("3000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2022/23",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3),
            relief_withdrawn=False
        )

        db_session.add(tax_advantaged)
        await db_session.commit()
        await db_session.refresh(tax_advantaged)

        # Still within 3-year period
        assert tax_advantaged.at_risk_of_losing_relief is True
        assert tax_advantaged.relief_secure is False

    @pytest.mark.asyncio
    async def test_not_at_risk_after_holding_period(self, db_session, test_eis_holding):
        """Test at_risk is False when holding period complete."""
        investment_date = date.today() - relativedelta(years=4)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("3000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2019/20",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3),
            relief_withdrawn=False
        )

        db_session.add(tax_advantaged)
        await db_session.commit()
        await db_session.refresh(tax_advantaged)

        # Holding period complete
        assert tax_advantaged.at_risk_of_losing_relief is False
        assert tax_advantaged.relief_secure is True

    @pytest.mark.asyncio
    async def test_at_risk_when_relief_withdrawn(self, db_session, test_eis_holding):
        """Test at_risk is False when relief withdrawn (already lost)."""
        investment_date = date.today() - relativedelta(years=1)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("3000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2022/23",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3),
            relief_withdrawn=True
        )

        db_session.add(tax_advantaged)
        await db_session.commit()
        await db_session.refresh(tax_advantaged)

        # Relief already withdrawn
        assert tax_advantaged.at_risk_of_losing_relief is False
        assert tax_advantaged.relief_secure is False


class TestReliefWithdrawal:
    """Test relief withdrawal functionality."""

    @pytest.mark.asyncio
    async def test_withdraw_relief(self, db_session, test_eis_holding):
        """Test withdrawing relief."""
        investment_date = date(2024, 1, 15)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("3000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2023/24",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3)
        )

        db_session.add(tax_advantaged)
        await db_session.commit()
        await db_session.refresh(tax_advantaged)

        # Withdraw relief
        reason = "Sold shares before 3-year holding period"
        tax_advantaged.withdraw_relief(reason)
        await db_session.commit()
        await db_session.refresh(tax_advantaged)

        assert tax_advantaged.relief_withdrawn is True
        assert tax_advantaged.relief_withdrawal_reason == reason
        assert tax_advantaged.relief_withdrawal_date == date.today()


class TestConstraints:
    """Test database constraints."""

    @pytest.mark.asyncio
    async def test_invalid_relief_percentage(self, db_session, test_eis_holding):
        """Test invalid relief percentage (must be 30.0 or 50.0)."""
        investment_date = date(2024, 1, 15)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("4000.00"),
            income_tax_relief_percentage=Decimal("40.0"),  # Invalid - must be 30 or 50
            tax_year_claimed="2023/24",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3)
        )

        db_session.add(tax_advantaged)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_invalid_holding_period(self, db_session, test_eis_holding):
        """Test invalid holding period (must be 3 or 5)."""
        investment_date = date(2024, 1, 15)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("3000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2023/24",
            minimum_holding_period_years=7,  # Invalid - must be 3 or 5
            holding_period_end_date=investment_date + relativedelta(years=7)
        )

        db_session.add(tax_advantaged)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_negative_investment_amount(self, db_session, test_eis_holding):
        """Test investment amount must be positive."""
        investment_date = date(2024, 1, 15)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("-10000.00"),  # Invalid negative
            income_tax_relief_claimed=Decimal("3000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2023/24",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3)
        )

        db_session.add(tax_advantaged)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_negative_relief_claimed(self, db_session, test_eis_holding):
        """Test relief claimed must be non-negative."""
        investment_date = date(2024, 1, 15)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("-3000.00"),  # Invalid negative
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2023/24",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3)
        )

        db_session.add(tax_advantaged)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_negative_cgt_deferral(self, db_session, test_eis_holding):
        """Test CGT deferral must be non-negative when present."""
        investment_date = date(2024, 1, 15)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("3000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2023/24",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3),
            cgt_deferral_claimed=Decimal("-5000.00")  # Invalid negative
        )

        db_session.add(tax_advantaged)
        with pytest.raises(IntegrityError):
            await db_session.commit()


class TestRelationships:
    """Test model relationships."""

    @pytest.mark.asyncio
    async def test_one_to_one_relationship_with_holding(self, db_session, test_eis_holding):
        """Test one-to-one relationship with InvestmentHolding."""
        investment_date = date(2024, 1, 15)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("3000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2023/24",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3)
        )

        db_session.add(tax_advantaged)
        await db_session.commit()

        # Re-fetch to load relationships
        result = await db_session.execute(
            select(TaxAdvantagedInvestment)
            .where(TaxAdvantagedInvestment.id == tax_advantaged.id)
        )
        tax_advantaged_loaded = result.scalar_one()

        result = await db_session.execute(
            select(InvestmentHolding)
            .where(InvestmentHolding.id == test_eis_holding.id)
        )
        holding_loaded = result.scalar_one()

        # Check relationship
        assert tax_advantaged_loaded.holding_id == holding_loaded.id

    @pytest.mark.asyncio
    async def test_unique_holding_constraint(self, db_session, test_eis_holding):
        """Test one holding can only have one tax-advantaged investment."""
        investment_date = date(2024, 1, 15)

        # Create first tax-advantaged investment
        tax_advantaged1 = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("3000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2023/24",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3)
        )

        db_session.add(tax_advantaged1)
        await db_session.commit()

        # Try to create second tax-advantaged investment for same holding
        tax_advantaged2 = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,  # Same holding_id
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("5000.00"),
            income_tax_relief_claimed=Decimal("1500.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2023/24",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3)
        )

        db_session.add(tax_advantaged2)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_cascade_delete_with_holding(self, db_session, test_eis_holding):
        """Test tax-advantaged investment is deleted when holding is deleted."""
        investment_date = date(2024, 1, 15)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("3000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2023/24",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3)
        )

        db_session.add(tax_advantaged)
        await db_session.commit()

        tax_advantaged_id = tax_advantaged.id

        # Delete holding
        await db_session.delete(test_eis_holding)
        await db_session.commit()

        # Tax-advantaged investment should be deleted (cascade)
        result = await db_session.execute(
            select(TaxAdvantagedInvestment).where(TaxAdvantagedInvestment.id == tax_advantaged_id)
        )
        result_obj = result.scalar_one_or_none()

        assert result_obj is None


class TestHelperMethods:
    """Test helper methods."""

    @pytest.mark.asyncio
    async def test_calculate_holding_period_end_date(self, db_session, test_eis_holding):
        """Test calculate_holding_period_end_date method."""
        investment_date = date(2024, 1, 15)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("3000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2023/24",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3)
        )

        db_session.add(tax_advantaged)
        await db_session.commit()
        await db_session.refresh(tax_advantaged)

        calculated_end_date = tax_advantaged.calculate_holding_period_end_date()
        expected_end_date = date(2027, 1, 15)

        assert calculated_end_date == expected_end_date
        assert calculated_end_date == tax_advantaged.holding_period_end_date


class TestIndexes:
    """Test database indexes."""

    @pytest.mark.asyncio
    async def test_indexes_exist(self, db_session, test_eis_holding):
        """Test that required indexes exist for tax_advantaged_investments table."""
        investment_date = date(2024, 1, 15)

        tax_advantaged = TaxAdvantagedInvestment(
            holding_id=test_eis_holding.id,
            scheme_type=SchemeType.EIS,
            investment_date=investment_date,
            investment_amount=Decimal("10000.00"),
            income_tax_relief_claimed=Decimal("3000.00"),
            income_tax_relief_percentage=Decimal("30.0"),
            tax_year_claimed="2023/24",
            minimum_holding_period_years=3,
            holding_period_end_date=investment_date + relativedelta(years=3)
        )

        db_session.add(tax_advantaged)
        await db_session.commit()

        # Query using indexed fields
        result = await db_session.execute(
            select(TaxAdvantagedInvestment)
            .where(TaxAdvantagedInvestment.holding_id == test_eis_holding.id)
            .where(TaxAdvantagedInvestment.scheme_type == SchemeType.EIS)
        )
        result_obj = result.scalar_one()

        assert result_obj is not None
        assert result_obj.scheme_type == SchemeType.EIS
