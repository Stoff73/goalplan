"""
Tests for investment account and holdings models.

This module tests:
- InvestmentAccount model creation and validation
- InvestmentHolding model and relationships
- TaxLot model for FIFO tracking
- DividendIncome model
- CapitalGainRealized model
- Encryption of account numbers
- Calculated properties (current_value, unrealized_gain, unrealized_gain_percentage)
- Constraint violations
- Cascade deletes
- Soft delete functionality
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
    TaxLot,
    DividendIncome,
    CapitalGainRealized,
    AccountType,
    AccountCountry,
    AccountStatus,
    SecurityType,
    AssetClass,
    Region,
    DisposalMethod,
    SourceCountry,
    Currency
)
from models.user import User, CountryPreference
from utils.encryption import encrypt_value, decrypt_value


@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    user = User(
        email=f"test_{uuid.uuid4()}@example.com",
        first_name="Test",
        last_name="User",
        country_preference=CountryPreference.BOTH,
        terms_accepted_at=datetime.utcnow(),
        email_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_account(db_session, test_user):
    """Create a test investment account."""
    account = InvestmentAccount(
        user_id=test_user.id,
        account_type=AccountType.STOCKS_ISA,
        provider="Vanguard",
        country=AccountCountry.UK,
        base_currency="GBP",
        account_open_date=date(2024, 1, 1),
        status=AccountStatus.ACTIVE
    )
    account.set_account_number("ISA123456789")
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def test_holding(db_session, test_account):
    """Create a test investment holding."""
    holding = InvestmentHolding(
        account_id=test_account.id,
        security_type=SecurityType.ETF,
        ticker="VUSA",
        isin="IE00B3XXRP09",
        security_name="Vanguard S&P 500 UCITS ETF",
        quantity=Decimal("100.0000"),
        purchase_date=date(2024, 1, 15),
        purchase_price=Decimal("75.50"),
        purchase_currency="GBP",
        current_price=Decimal("82.00"),
        asset_class=AssetClass.EQUITY,
        region=Region.US,
        sector="Technology"
    )
    db_session.add(holding)
    await db_session.commit()
    await db_session.refresh(holding)
    return holding


class TestInvestmentAccount:
    """Test InvestmentAccount model."""

    @pytest.mark.asyncio
    async def test_create_account_with_valid_data(self, db_session, test_user):
        """Test creating an account with valid data."""
        account = InvestmentAccount(
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Interactive Brokers",
            country=AccountCountry.UK,
            base_currency="GBP",
            account_open_date=date(2024, 6, 1),
            status=AccountStatus.ACTIVE
        )
        account.set_account_number("GIA987654321")

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        assert account.id is not None
        assert account.user_id == test_user.id
        assert account.account_type == AccountType.GIA
        assert account.provider == "Interactive Brokers"
        assert account.get_account_number() == "GIA987654321"
        assert account.account_number_last_4 == "4321"

    @pytest.mark.asyncio
    async def test_account_number_encryption(self, db_session, test_user):
        """Test account number is encrypted."""
        account = InvestmentAccount(
            user_id=test_user.id,
            account_type=AccountType.STOCKS_ISA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP"
        )

        account_number = "SECRET123456789"
        account.set_account_number(account_number)

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        # Encrypted value should be different from original
        assert account.account_number_encrypted != account_number
        # Decrypted value should match original
        assert account.get_account_number() == account_number
        # Last 4 digits should be stored
        assert account.account_number_last_4 == "6789"

    @pytest.mark.asyncio
    async def test_account_soft_delete(self, db_session, test_account):
        """Test soft delete functionality."""
        account_id = test_account.id
        test_account.deleted = True
        await db_session.commit()

        # Account still exists in database
        result = await db_session.execute(
            select(InvestmentAccount).where(InvestmentAccount.id == account_id)
        )
        account = result.scalar_one()

        assert account.deleted is True

    @pytest.mark.asyncio
    async def test_account_status_enum(self, db_session, test_user):
        """Test account status enum values."""
        account = InvestmentAccount(
            user_id=test_user.id,
            account_type=AccountType.VCT,
            provider="VCT Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.CLOSED
        )
        account.set_account_number("VCT123")

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        assert account.status == AccountStatus.CLOSED

    @pytest.mark.asyncio
    async def test_sa_account_creation(self, db_session, test_user):
        """Test creating a South African account."""
        account = InvestmentAccount(
            user_id=test_user.id,
            account_type=AccountType.SA_UNIT_TRUST,
            provider="Allan Gray",
            country=AccountCountry.SA,
            base_currency="ZAR",
            account_open_date=date(2024, 3, 1)
        )
        account.set_account_number("AG987654")

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        assert account.country == AccountCountry.SA
        assert account.base_currency == "ZAR"
        assert account.account_type == AccountType.SA_UNIT_TRUST


class TestInvestmentHolding:
    """Test InvestmentHolding model."""

    @pytest.mark.asyncio
    async def test_create_holding_with_valid_data(self, db_session, test_account):
        """Test creating a holding with valid data."""
        holding = InvestmentHolding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="BP",
            isin="GB0007980591",
            security_name="BP plc",
            quantity=Decimal("500.0000"),
            purchase_date=date(2024, 2, 1),
            purchase_price=Decimal("4.50"),
            purchase_currency="GBP",
            current_price=Decimal("5.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            sector="Energy"
        )

        db_session.add(holding)
        await db_session.commit()
        await db_session.refresh(holding)

        assert holding.id is not None
        assert holding.account_id == test_account.id
        assert holding.ticker == "BP"
        assert holding.quantity == Decimal("500.0000")

    @pytest.mark.asyncio
    async def test_holding_current_value_property(self, db_session, test_holding):
        """Test current_value calculated property."""
        expected_value = Decimal("100.0000") * Decimal("82.00")
        assert test_holding.current_value == expected_value

    @pytest.mark.asyncio
    async def test_holding_unrealized_gain_property(self, db_session, test_holding):
        """Test unrealized_gain calculated property."""
        # (82.00 - 75.50) * 100 = 650.00
        expected_gain = (Decimal("82.00") - Decimal("75.50")) * Decimal("100.0000")
        assert test_holding.unrealized_gain == expected_gain

    @pytest.mark.asyncio
    async def test_holding_unrealized_gain_percentage_property(self, db_session, test_holding):
        """Test unrealized_gain_percentage calculated property."""
        # ((82.00 - 75.50) / 75.50) * 100 = 8.609271523178808
        expected_percentage = ((Decimal("82.00") - Decimal("75.50")) / Decimal("75.50")) * 100
        assert abs(test_holding.unrealized_gain_percentage - expected_percentage) < Decimal("0.01")

    @pytest.mark.asyncio
    async def test_holding_quantity_positive_constraint(self, db_session, test_account):
        """Test quantity must be positive."""
        holding = InvestmentHolding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="TEST",
            security_name="Test Stock",
            quantity=Decimal("-10.0000"),  # Invalid negative quantity
            purchase_date=date(2024, 1, 1),
            purchase_price=Decimal("10.00"),
            purchase_currency="GBP",
            current_price=Decimal("12.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.UK
        )

        db_session.add(holding)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_holding_price_non_negative_constraint(self, db_session, test_account):
        """Test purchase price must be non-negative."""
        holding = InvestmentHolding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="TEST",
            security_name="Test Stock",
            quantity=Decimal("10.0000"),
            purchase_date=date(2024, 1, 1),
            purchase_price=Decimal("-10.00"),  # Invalid negative price
            purchase_currency="GBP",
            current_price=Decimal("12.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.UK
        )

        db_session.add(holding)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_holding_soft_delete(self, db_session, test_holding):
        """Test soft delete functionality."""
        holding_id = test_holding.id
        test_holding.deleted = True
        await db_session.commit()

        # Holding still exists in database
        result = await db_session.execute(
            select(InvestmentHolding).where(InvestmentHolding.id == holding_id)
        )
        holding = result.scalar_one()

        assert holding.deleted is True

    @pytest.mark.asyncio
    async def test_holding_with_no_ticker(self, db_session, test_account):
        """Test creating a holding without a ticker (e.g., private equity)."""
        holding = InvestmentHolding(
            account_id=test_account.id,
            security_type=SecurityType.EIS_SHARE,
            ticker=None,
            security_name="Private Company Ltd",
            quantity=Decimal("1000.0000"),
            purchase_date=date(2024, 1, 1),
            purchase_price=Decimal("1.00"),
            purchase_currency="GBP",
            current_price=Decimal("1.50"),
            asset_class=AssetClass.EQUITY,
            region=Region.UK
        )

        db_session.add(holding)
        await db_session.commit()
        await db_session.refresh(holding)

        assert holding.ticker is None
        assert holding.security_name == "Private Company Ltd"


class TestTaxLot:
    """Test TaxLot model."""

    @pytest.mark.asyncio
    async def test_create_tax_lot(self, db_session, test_holding):
        """Test creating a tax lot."""
        tax_lot = TaxLot(
            holding_id=test_holding.id,
            purchase_date=date(2024, 1, 15),
            quantity=Decimal("100.0000"),
            purchase_price=Decimal("75.50"),
            purchase_currency="GBP",
            cost_basis_gbp=Decimal("7550.00"),
            cost_basis_zar=Decimal("180000.00"),
            exchange_rate=Decimal("23.841060")
        )

        db_session.add(tax_lot)
        await db_session.commit()
        await db_session.refresh(tax_lot)

        assert tax_lot.id is not None
        assert tax_lot.holding_id == test_holding.id
        assert tax_lot.quantity == Decimal("100.0000")
        assert tax_lot.cost_basis_gbp == Decimal("7550.00")

    @pytest.mark.asyncio
    async def test_tax_lot_with_disposal(self, db_session, test_holding):
        """Test tax lot with disposal details."""
        tax_lot = TaxLot(
            holding_id=test_holding.id,
            purchase_date=date(2024, 1, 15),
            quantity=Decimal("100.0000"),
            purchase_price=Decimal("75.50"),
            purchase_currency="GBP",
            cost_basis_gbp=Decimal("7550.00"),
            cost_basis_zar=Decimal("180000.00"),
            exchange_rate=Decimal("23.841060"),
            disposal_date=date(2024, 6, 15),
            disposal_quantity=Decimal("50.0000"),
            disposal_proceeds=Decimal("4100.00"),
            realized_gain=Decimal("325.00"),
            cgt_tax_year="2024/25",
            disposal_method=DisposalMethod.FIFO
        )

        db_session.add(tax_lot)
        await db_session.commit()
        await db_session.refresh(tax_lot)

        assert tax_lot.disposal_date == date(2024, 6, 15)
        assert tax_lot.disposal_quantity == Decimal("50.0000")
        assert tax_lot.realized_gain == Decimal("325.00")
        assert tax_lot.disposal_method == DisposalMethod.FIFO

    @pytest.mark.asyncio
    async def test_tax_lot_quantity_positive_constraint(self, db_session, test_holding):
        """Test tax lot quantity must be positive."""
        tax_lot = TaxLot(
            holding_id=test_holding.id,
            purchase_date=date(2024, 1, 15),
            quantity=Decimal("-10.0000"),  # Invalid negative quantity
            purchase_price=Decimal("75.50"),
            purchase_currency="GBP",
            cost_basis_gbp=Decimal("755.00"),
            cost_basis_zar=Decimal("18000.00"),
            exchange_rate=Decimal("23.841060")
        )

        db_session.add(tax_lot)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_tax_lot_cascade_delete(self, db_session, test_holding):
        """Test tax lots are deleted when holding is deleted."""
        tax_lot = TaxLot(
            holding_id=test_holding.id,
            purchase_date=date(2024, 1, 15),
            quantity=Decimal("100.0000"),
            purchase_price=Decimal("75.50"),
            purchase_currency="GBP",
            cost_basis_gbp=Decimal("7550.00"),
            cost_basis_zar=Decimal("180000.00"),
            exchange_rate=Decimal("23.841060")
        )

        db_session.add(tax_lot)
        await db_session.commit()

        tax_lot_id = tax_lot.id

        # Delete holding
        await db_session.delete(test_holding)
        await db_session.commit()

        # Tax lot should be deleted (cascade)
        result = await db_session.execute(
            select(TaxLot).where(TaxLot.id == tax_lot_id)
        )
        result_obj = result.scalar_one_or_none()

        assert result_obj is None


class TestDividendIncome:
    """Test DividendIncome model."""

    @pytest.mark.asyncio
    async def test_create_dividend(self, db_session, test_holding):
        """Test creating a dividend record."""
        dividend = DividendIncome(
            holding_id=test_holding.id,
            payment_date=date(2024, 3, 15),
            ex_dividend_date=date(2024, 3, 1),
            dividend_per_share=Decimal("0.50"),
            total_dividend_gross=Decimal("50.00"),
            withholding_tax=Decimal("0.00"),
            total_dividend_net=Decimal("50.00"),
            currency="GBP",
            source_country=SourceCountry.UK,
            uk_tax_year="2023/24"
        )

        db_session.add(dividend)
        await db_session.commit()
        await db_session.refresh(dividend)

        assert dividend.id is not None
        assert dividend.holding_id == test_holding.id
        assert dividend.total_dividend_gross == Decimal("50.00")
        assert dividend.source_country == SourceCountry.UK

    @pytest.mark.asyncio
    async def test_dividend_with_withholding_tax(self, db_session, test_holding):
        """Test dividend with withholding tax."""
        dividend = DividendIncome(
            holding_id=test_holding.id,
            payment_date=date(2024, 3, 15),
            dividend_per_share=Decimal("1.00"),
            total_dividend_gross=Decimal("100.00"),
            withholding_tax=Decimal("15.00"),  # 15% US withholding
            total_dividend_net=Decimal("85.00"),
            currency="USD",
            source_country=SourceCountry.US,
            uk_tax_year="2023/24"
        )

        db_session.add(dividend)
        await db_session.commit()
        await db_session.refresh(dividend)

        assert dividend.withholding_tax == Decimal("15.00")
        assert dividend.total_dividend_net == Decimal("85.00")

    @pytest.mark.asyncio
    async def test_dividend_non_negative_constraint(self, db_session, test_holding):
        """Test dividend amounts must be non-negative."""
        dividend = DividendIncome(
            holding_id=test_holding.id,
            payment_date=date(2024, 3, 15),
            dividend_per_share=Decimal("-0.50"),  # Invalid negative
            total_dividend_gross=Decimal("50.00"),
            withholding_tax=Decimal("0.00"),
            total_dividend_net=Decimal("50.00"),
            currency="GBP",
            source_country=SourceCountry.UK
        )

        db_session.add(dividend)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_dividend_cascade_delete(self, db_session, test_holding):
        """Test dividends are deleted when holding is deleted."""
        dividend = DividendIncome(
            holding_id=test_holding.id,
            payment_date=date(2024, 3, 15),
            dividend_per_share=Decimal("0.50"),
            total_dividend_gross=Decimal("50.00"),
            withholding_tax=Decimal("0.00"),
            total_dividend_net=Decimal("50.00"),
            currency="GBP",
            source_country=SourceCountry.UK
        )

        db_session.add(dividend)
        await db_session.commit()

        dividend_id = dividend.id

        # Delete holding
        await db_session.delete(test_holding)
        await db_session.commit()

        # Dividend should be deleted (cascade)
        result = await db_session.execute(
            select(DividendIncome).where(DividendIncome.id == dividend_id)
        )
        result_obj = result.scalar_one_or_none()

        assert result_obj is None


class TestCapitalGainRealized:
    """Test CapitalGainRealized model."""

    @pytest.mark.asyncio
    async def test_create_capital_gain(self, db_session, test_holding):
        """Test creating a capital gain record."""
        capital_gain = CapitalGainRealized(
            holding_id=test_holding.id,
            disposal_date=date(2024, 6, 15),
            quantity_sold=Decimal("50.0000"),
            sale_price=Decimal("82.00"),
            sale_value=Decimal("4100.00"),
            cost_basis=Decimal("3775.00"),
            gain_loss=Decimal("325.00"),
            tax_year="2024/25",
            country=AccountCountry.UK
        )

        db_session.add(capital_gain)
        await db_session.commit()
        await db_session.refresh(capital_gain)

        assert capital_gain.id is not None
        assert capital_gain.holding_id == test_holding.id
        assert capital_gain.gain_loss == Decimal("325.00")
        assert capital_gain.tax_year == "2024/25"

    @pytest.mark.asyncio
    async def test_capital_loss(self, db_session, test_holding):
        """Test creating a capital loss record."""
        capital_gain = CapitalGainRealized(
            holding_id=test_holding.id,
            disposal_date=date(2024, 6, 15),
            quantity_sold=Decimal("50.0000"),
            sale_price=Decimal("70.00"),
            sale_value=Decimal("3500.00"),
            cost_basis=Decimal("3775.00"),
            gain_loss=Decimal("-275.00"),  # Loss
            tax_year="2024/25",
            country=AccountCountry.UK
        )

        db_session.add(capital_gain)
        await db_session.commit()
        await db_session.refresh(capital_gain)

        assert capital_gain.gain_loss == Decimal("-275.00")

    @pytest.mark.asyncio
    async def test_capital_gain_quantity_positive_constraint(self, db_session, test_holding):
        """Test quantity sold must be positive."""
        capital_gain = CapitalGainRealized(
            holding_id=test_holding.id,
            disposal_date=date(2024, 6, 15),
            quantity_sold=Decimal("-10.0000"),  # Invalid negative quantity
            sale_price=Decimal("82.00"),
            sale_value=Decimal("820.00"),
            cost_basis=Decimal("755.00"),
            gain_loss=Decimal("65.00"),
            tax_year="2024/25",
            country=AccountCountry.UK
        )

        db_session.add(capital_gain)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_capital_gain_cascade_delete(self, db_session, test_holding):
        """Test capital gains are deleted when holding is deleted."""
        capital_gain = CapitalGainRealized(
            holding_id=test_holding.id,
            disposal_date=date(2024, 6, 15),
            quantity_sold=Decimal("50.0000"),
            sale_price=Decimal("82.00"),
            sale_value=Decimal("4100.00"),
            cost_basis=Decimal("3775.00"),
            gain_loss=Decimal("325.00"),
            tax_year="2024/25",
            country=AccountCountry.UK
        )

        db_session.add(capital_gain)
        await db_session.commit()

        capital_gain_id = capital_gain.id

        # Delete holding
        await db_session.delete(test_holding)
        await db_session.commit()

        # Capital gain should be deleted (cascade)
        result = await db_session.execute(
            select(CapitalGainRealized).where(CapitalGainRealized.id == capital_gain_id)
        )
        result_obj = result.scalar_one_or_none()

        assert result_obj is None


class TestRelationships:
    """Test model relationships."""

    @pytest.mark.asyncio
    async def test_account_user_relationship(self, db_session, test_user, test_account):
        """Test relationship between account and user."""
        await db_session.refresh(test_account)
        await db_session.refresh(test_user)
        assert test_account.user == test_user

    @pytest.mark.asyncio
    async def test_holding_account_relationship(self, db_session, test_account, test_holding):
        """Test relationship between holding and account."""
        await db_session.refresh(test_holding)
        await db_session.refresh(test_account)
        assert test_holding.account == test_account

    @pytest.mark.asyncio
    async def test_account_cascade_delete(self, db_session, test_user, test_account, test_holding):
        """Test cascade delete from account to holdings."""
        holding_id = test_holding.id

        # Delete account
        await db_session.delete(test_account)
        await db_session.commit()

        # Holding should be deleted (cascade)
        result = await db_session.execute(
            select(InvestmentHolding).where(InvestmentHolding.id == holding_id)
        )
        result_obj = result.scalar_one_or_none()

        assert result_obj is None


class TestIndexes:
    """Test database indexes exist."""

    @pytest.mark.asyncio
    async def test_account_indexes_exist(self, db_session, test_user):
        """Test that required indexes exist for investment_accounts table."""
        # Create test data
        account = InvestmentAccount(
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE
        )
        account.set_account_number("TEST123")
        db_session.add(account)
        await db_session.commit()

        # Query using indexed fields
        result = await db_session.execute(
            select(InvestmentAccount)
            .where(InvestmentAccount.user_id == test_user.id)
            .where(InvestmentAccount.status == AccountStatus.ACTIVE)
        )
        result_obj = result.scalar_one()

        assert result_obj is not None
        assert result_obj.user_id == test_user.id

    @pytest.mark.asyncio
    async def test_holding_indexes_exist(self, db_session, test_account):
        """Test that required indexes exist for investment_holdings table."""
        # Create test data
        holding = InvestmentHolding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="TEST",
            security_name="Test Stock",
            quantity=Decimal("100.0000"),
            purchase_date=date(2024, 1, 1),
            purchase_price=Decimal("10.00"),
            purchase_currency="GBP",
            current_price=Decimal("12.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.UK
        )
        db_session.add(holding)
        await db_session.commit()

        # Query using indexed fields
        result = await db_session.execute(
            select(InvestmentHolding)
            .where(InvestmentHolding.account_id == test_account.id)
            .where(InvestmentHolding.ticker == "TEST")
        )
        result_obj = result.scalar_one()

        assert result_obj is not None
        assert result_obj.ticker == "TEST"
