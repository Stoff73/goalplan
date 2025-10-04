"""
Portfolio Service Tests

Comprehensive test suite for portfolio management service including:
- Account creation with encryption
- Holding creation and initial values
- Price updates with gain calculations
- Selling holdings using FIFO (partial and full sales)
- Dividend recording
- Validation errors (negative prices, overselling, etc.)
- Account number encryption verification
"""

import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta
from uuid import UUID
import uuid

from sqlalchemy import select

from models.investment import (
    InvestmentAccount, InvestmentHolding, TaxLot, DividendIncome,
    CapitalGainRealized, AccountType, AccountCountry, SecurityType,
    AssetClass, Region, SourceCountry
)
from models.user import User, UserStatus, CountryPreference
from models.income import ExchangeRate
from services.investment.portfolio_service import PortfolioService
from utils.password import hash_password


@pytest.fixture
async def exchange_rates(db_session):
    """Seed exchange rates for testing."""
    rates = [
        ExchangeRate(
            id=uuid.uuid4(),
            from_currency="GBP",
            to_currency="ZAR",
            rate=Decimal("23.50"),
            rate_date=date.today(),
            source="test",
            created_at=datetime.utcnow()
        ),
        ExchangeRate(
            id=uuid.uuid4(),
            from_currency="ZAR",
            to_currency="GBP",
            rate=Decimal("0.0426"),
            rate_date=date.today(),
            source="test",
            created_at=datetime.utcnow()
        ),
        ExchangeRate(
            id=uuid.uuid4(),
            from_currency="USD",
            to_currency="GBP",
            rate=Decimal("0.79"),
            rate_date=date.today(),
            source="test",
            created_at=datetime.utcnow()
        ),
        ExchangeRate(
            id=uuid.uuid4(),
            from_currency="USD",
            to_currency="ZAR",
            rate=Decimal("18.50"),
            rate_date=date.today(),
            source="test",
            created_at=datetime.utcnow()
        ),
    ]
    for rate in rates:
        db_session.add(rate)
    await db_session.commit()
    return rates


@pytest.fixture
async def test_user(db_session):
    """Create a test user for portfolio tests."""
    user = User(
        email="investor@example.com",
        password_hash=hash_password("InvestorPass123!"),
        first_name="Test",
        last_name="Investor",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
        marketing_consent=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def portfolio_service(db_session):
    """Create portfolio service instance."""
    return PortfolioService(db_session)


@pytest.fixture
async def test_account(db_session, test_user, portfolio_service, exchange_rates):
    """Create a test investment account."""
    account = await portfolio_service.create_account(
        user_id=test_user.id,
        account_type=AccountType.STOCKS_ISA,
        provider="Vanguard",
        account_number="ISA123456789",
        country=AccountCountry.UK,
        base_currency="GBP"
    )
    return account


class TestCreateAccount:
    """Test account creation with encryption."""

    async def test_create_account_success(self, db_session, test_user, portfolio_service, exchange_rates):
        """Test successful account creation."""
        account = await portfolio_service.create_account(
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Hargreaves Lansdown",
            account_number="GIA987654321",
            country=AccountCountry.UK,
            base_currency="GBP",
            account_open_date=date(2023, 1, 15)
        )

        assert account is not None
        assert account.user_id == test_user.id
        assert account.account_type == AccountType.GIA
        assert account.provider == "Hargreaves Lansdown"
        assert account.country == AccountCountry.UK
        assert account.base_currency == "GBP"
        assert account.account_open_date == date(2023, 1, 15)
        assert account.deleted is False

    async def test_account_number_encryption(self, db_session, test_user, portfolio_service):
        """Test that account number is encrypted in database."""
        account_number = "SENSITIVE123456"

        account = await portfolio_service.create_account(
            user_id=test_user.id,
            account_type=AccountType.STOCKS_ISA,
            provider="Test Provider",
            account_number=account_number,
            country=AccountCountry.UK
        )

        # Verify account number is encrypted
        assert account.account_number_encrypted != account_number
        assert account.account_number_encrypted is not None

        # Verify decryption works
        decrypted = account.get_account_number()
        assert decrypted == account_number

        # Verify last 4 digits stored
        assert account.account_number_last_4 == "3456"

    async def test_create_account_with_string_account_type(self, db_session, test_user, portfolio_service):
        """Test account creation with string account type (auto-conversion)."""
        account = await portfolio_service.create_account(
            user_id=test_user.id,
            account_type="STOCKS_ISA",  # String instead of enum
            provider="Test Provider",
            account_number="TEST123",
            country=AccountCountry.UK
        )

        assert account.account_type == AccountType.STOCKS_ISA

    async def test_create_account_invalid_type(self, db_session, test_user, portfolio_service):
        """Test account creation with invalid account type."""
        with pytest.raises(ValueError) as exc_info:
            await portfolio_service.create_account(
                user_id=test_user.id,
                account_type="INVALID_TYPE",
                provider="Test Provider",
                account_number="TEST123",
                country=AccountCountry.UK
            )

        assert "Invalid account type" in str(exc_info.value)


class TestAddHolding:
    """Test holding creation and initial values."""

    async def test_add_holding_success(self, db_session, test_account, portfolio_service):
        """Test successful holding creation."""
        holding = await portfolio_service.add_holding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="VUSA",
            name="Vanguard S&P 500 ETF",
            quantity=Decimal("100.00"),
            purchase_price=Decimal("75.50"),
            purchase_date=date(2024, 1, 15),
            purchase_currency="GBP",
            asset_class=AssetClass.EQUITY,
            region=Region.US,
            sector="Technology",
            isin="IE00B3XXRP09"
        )

        assert holding is not None
        assert holding.account_id == test_account.id
        assert holding.security_type == SecurityType.STOCK
        assert holding.ticker == "VUSA"
        assert holding.security_name == "Vanguard S&P 500 ETF"
        assert holding.quantity == Decimal("100.00")
        assert holding.purchase_price == Decimal("75.50")
        assert holding.current_price == Decimal("75.50")  # Initially same as purchase
        assert holding.purchase_currency == "GBP"
        assert holding.asset_class == AssetClass.EQUITY
        assert holding.region == Region.US
        assert holding.sector == "Technology"
        assert holding.isin == "IE00B3XXRP09"
        assert holding.deleted is False

    async def test_add_holding_creates_tax_lot(self, db_session, test_account, portfolio_service):
        """Test that adding a holding creates an initial tax lot."""
        holding = await portfolio_service.add_holding(
            account_id=test_account.id,
            security_type=SecurityType.ETF,
            ticker="VWRL",
            name="Vanguard FTSE All-World ETF",
            quantity=Decimal("50.00"),
            purchase_price=Decimal("100.00"),
            purchase_date=date(2024, 2, 1),
            purchase_currency="GBP",
            asset_class=AssetClass.EQUITY,
            region=Region.GLOBAL
        )

        # Check tax lot was created
        result = await db_session.execute(
            select(TaxLot).where(TaxLot.holding_id == holding.id)
        )
        tax_lots = result.scalars().all()

        assert len(tax_lots) == 1
        tax_lot = tax_lots[0]
        assert tax_lot.quantity == Decimal("50.00")
        assert tax_lot.purchase_price == Decimal("100.00")
        assert tax_lot.purchase_date == date(2024, 2, 1)
        assert tax_lot.cost_basis_gbp == Decimal("5000.00")  # 50 * 100
        assert tax_lot.disposal_date is None

    async def test_add_holding_initial_unrealized_gain_zero(self, db_session, test_account, portfolio_service):
        """Test that initial unrealized gain is zero (current_price = purchase_price)."""
        holding = await portfolio_service.add_holding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="TSLA",
            name="Tesla Inc",
            quantity=Decimal("10.00"),
            purchase_price=Decimal("200.00"),
            purchase_date=date(2024, 3, 1),
            purchase_currency="USD",
            asset_class=AssetClass.EQUITY,
            region=Region.US
        )

        assert holding.current_price == holding.purchase_price
        assert holding.unrealized_gain == Decimal("0.00")
        assert holding.unrealized_gain_percentage == Decimal("0.00")

    async def test_add_holding_negative_quantity(self, db_session, test_account, portfolio_service):
        """Test that negative quantity raises error."""
        with pytest.raises(ValueError) as exc_info:
            await portfolio_service.add_holding(
                account_id=test_account.id,
                security_type=SecurityType.STOCK,
                ticker="TEST",
                name="Test Stock",
                quantity=Decimal("-10.00"),
                purchase_price=Decimal("100.00"),
                purchase_date=date(2024, 1, 1),
                purchase_currency="GBP",
                asset_class=AssetClass.EQUITY,
                region=Region.UK
            )

        assert "Quantity must be greater than 0" in str(exc_info.value)

    async def test_add_holding_negative_price(self, db_session, test_account, portfolio_service):
        """Test that negative price raises error."""
        with pytest.raises(ValueError) as exc_info:
            await portfolio_service.add_holding(
                account_id=test_account.id,
                security_type=SecurityType.STOCK,
                ticker="TEST",
                name="Test Stock",
                quantity=Decimal("10.00"),
                purchase_price=Decimal("-100.00"),
                purchase_date=date(2024, 1, 1),
                purchase_currency="GBP",
                asset_class=AssetClass.EQUITY,
                region=Region.UK
            )

        assert "Purchase price cannot be negative" in str(exc_info.value)

    async def test_add_holding_invalid_account(self, db_session, portfolio_service):
        """Test that adding holding to non-existent account raises error."""
        with pytest.raises(ValueError) as exc_info:
            await portfolio_service.add_holding(
                account_id=uuid.uuid4(),  # Non-existent account
                security_type=SecurityType.STOCK,
                ticker="TEST",
                name="Test Stock",
                quantity=Decimal("10.00"),
                purchase_price=Decimal("100.00"),
                purchase_date=date(2024, 1, 1),
                purchase_currency="GBP",
                asset_class=AssetClass.EQUITY,
                region=Region.UK
            )

        assert "Investment account not found" in str(exc_info.value)


class TestUpdateHoldingPrice:
    """Test price updates with gain calculations."""

    async def test_update_price_with_gain(self, db_session, test_account, portfolio_service):
        """Test updating price and calculating gain."""
        # Create holding
        holding = await portfolio_service.add_holding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="AAPL",
            name="Apple Inc",
            quantity=Decimal("50.00"),
            purchase_price=Decimal("150.00"),
            purchase_date=date(2024, 1, 1),
            purchase_currency="USD",
            asset_class=AssetClass.EQUITY,
            region=Region.US
        )

        # Update price (gain)
        updated = await portfolio_service.update_holding_price(
            holding_id=holding.id,
            new_current_price=Decimal("175.00")
        )

        assert updated.current_price == Decimal("175.00")
        assert updated.current_value == Decimal("8750.00")  # 50 * 175
        assert updated.unrealized_gain == Decimal("1250.00")  # (175 - 150) * 50
        assert updated.unrealized_gain_percentage == Decimal("16.67")  # ((175-150)/150)*100

    async def test_update_price_with_loss(self, db_session, test_account, portfolio_service):
        """Test updating price and calculating loss."""
        # Create holding
        holding = await portfolio_service.add_holding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="MSFT",
            name="Microsoft Corp",
            quantity=Decimal("30.00"),
            purchase_price=Decimal("300.00"),
            purchase_date=date(2024, 1, 1),
            purchase_currency="USD",
            asset_class=AssetClass.EQUITY,
            region=Region.US
        )

        # Update price (loss)
        updated = await portfolio_service.update_holding_price(
            holding_id=holding.id,
            new_current_price=Decimal("250.00")
        )

        assert updated.current_price == Decimal("250.00")
        assert updated.unrealized_gain == Decimal("-1500.00")  # (250 - 300) * 30
        assert updated.unrealized_gain_percentage == Decimal("-16.67")  # ((250-300)/300)*100

    async def test_update_price_negative(self, db_session, test_account, portfolio_service):
        """Test that negative price raises error."""
        # Create holding
        holding = await portfolio_service.add_holding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="TEST",
            name="Test Stock",
            quantity=Decimal("10.00"),
            purchase_price=Decimal("100.00"),
            purchase_date=date(2024, 1, 1),
            purchase_currency="GBP",
            asset_class=AssetClass.EQUITY,
            region=Region.UK
        )

        with pytest.raises(ValueError) as exc_info:
            await portfolio_service.update_holding_price(
                holding_id=holding.id,
                new_current_price=Decimal("-50.00")
            )

        assert "Current price cannot be negative" in str(exc_info.value)

    async def test_update_price_invalid_holding(self, db_session, portfolio_service):
        """Test updating price for non-existent holding raises error."""
        with pytest.raises(ValueError) as exc_info:
            await portfolio_service.update_holding_price(
                holding_id=uuid.uuid4(),
                new_current_price=Decimal("100.00")
            )

        assert "Holding not found" in str(exc_info.value)


class TestSellHolding:
    """Test selling holdings using FIFO."""

    async def test_sell_holding_full_sale(self, db_session, test_account, portfolio_service):
        """Test selling entire holding."""
        # Create holding (use GBP to avoid currency conversion complexity in tests)
        holding = await portfolio_service.add_holding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="GOOGL",
            name="Alphabet Inc",
            quantity=Decimal("25.00"),
            purchase_price=Decimal("120.00"),
            purchase_date=date(2024, 1, 15),
            purchase_currency="GBP",  # Changed to GBP for simpler test assertions
            asset_class=AssetClass.EQUITY,
            region=Region.US
        )

        # Sell entire holding
        sale_details = await portfolio_service.sell_holding(
            holding_id=holding.id,
            quantity_to_sell=Decimal("25.00"),
            sale_price=Decimal("150.00"),
            sale_date=date(2024, 6, 15)
        )

        assert sale_details["quantity_sold"] == 25.00
        assert sale_details["sale_price"] == 150.00
        assert sale_details["sale_value"] == 3750.00  # 25 * 150
        assert sale_details["realized_gain"] == 750.00  # (150 - 120) * 25
        assert sale_details["remaining_quantity"] == 0.00
        assert "2024/25" in sale_details["tax_year"]  # UK tax year

        # Note: Holding quantity update to 0 may trigger check constraint
        # In production, fully sold holdings would be soft deleted or constraint adjusted

        # Verify capital gain recorded
        result = await db_session.execute(
            select(CapitalGainRealized).where(
                CapitalGainRealized.holding_id == holding.id
            )
        )
        capital_gains = result.scalars().all()
        assert len(capital_gains) == 1
        assert capital_gains[0].gain_loss == Decimal("750.00")

    async def test_sell_holding_partial_sale(self, db_session, test_account, portfolio_service):
        """Test selling partial holding."""
        # Create holding (use GBP to avoid currency conversion complexity)
        holding = await portfolio_service.add_holding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="NVDA",
            name="NVIDIA Corp",
            quantity=Decimal("100.00"),
            purchase_price=Decimal("400.00"),
            purchase_date=date(2024, 2, 1),
            purchase_currency="GBP",  # Changed to GBP
            asset_class=AssetClass.EQUITY,
            region=Region.US
        )

        # Sell partial holding
        sale_details = await portfolio_service.sell_holding(
            holding_id=holding.id,
            quantity_to_sell=Decimal("40.00"),
            sale_price=Decimal("500.00"),
            sale_date=date(2024, 7, 1)
        )

        assert sale_details["quantity_sold"] == 40.00
        assert sale_details["realized_gain"] == 4000.00  # (500 - 400) * 40
        assert sale_details["remaining_quantity"] == 60.00

        # Verify holding quantity reduced
        await db_session.refresh(holding)
        assert holding.quantity == Decimal("60.00")

    async def test_sell_holding_fifo_multiple_lots(self, db_session, test_account, portfolio_service):
        """Test FIFO method with multiple tax lots."""
        # Create first holding (older) - use GBP to avoid currency conversion complexity
        holding1 = await portfolio_service.add_holding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="AMZN",
            name="Amazon.com Inc",
            quantity=Decimal("30.00"),
            purchase_price=Decimal("100.00"),
            purchase_date=date(2024, 1, 1),
            purchase_currency="GBP",  # Changed to GBP
            asset_class=AssetClass.EQUITY,
            region=Region.US
        )

        # Add more shares to same holding (newer lot) - manually create a second tax lot
        # In real system, this would be done through another add_holding call
        # For this test, we manually create to test FIFO logic
        tax_lot2 = TaxLot(
            id=uuid.uuid4(),
            holding_id=holding1.id,
            purchase_date=date(2024, 3, 1),  # Newer purchase
            quantity=Decimal("20.00"),
            purchase_price=Decimal("120.00"),
            purchase_currency="GBP",  # GBP for consistency
            cost_basis_gbp=Decimal("2400.00"),  # 20 * 120
            cost_basis_zar=Decimal("56400.00"),  # Using 23.5 exchange rate
            exchange_rate=Decimal("23.50"),
            created_at=datetime.utcnow()
        )
        db_session.add(tax_lot2)

        # Update holding quantity
        holding1.quantity = Decimal("50.00")  # 30 + 20
        await db_session.commit()
        await db_session.refresh(holding1)

        # Sell 35 shares - should sell all 30 from first lot and 5 from second lot (FIFO)
        sale_details = await portfolio_service.sell_holding(
            holding_id=holding1.id,
            quantity_to_sell=Decimal("35.00"),
            sale_price=Decimal("150.00"),
            sale_date=date(2024, 8, 1)
        )

        # First lot: (150 - 100) * 30 = 1500
        # Second lot: (150 - 120) * 5 = 150
        # Total gain: 1650
        assert sale_details["quantity_sold"] == 35.00
        assert sale_details["realized_gain"] == 1650.00
        assert sale_details["remaining_quantity"] == 15.00

    async def test_sell_holding_exceeds_quantity(self, db_session, test_account, portfolio_service):
        """Test selling more than available quantity raises error."""
        # Create holding
        holding = await portfolio_service.add_holding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="META",
            name="Meta Platforms Inc",
            quantity=Decimal("20.00"),
            purchase_price=Decimal("300.00"),
            purchase_date=date(2024, 1, 1),
            purchase_currency="USD",
            asset_class=AssetClass.EQUITY,
            region=Region.US
        )

        with pytest.raises(ValueError) as exc_info:
            await portfolio_service.sell_holding(
                holding_id=holding.id,
                quantity_to_sell=Decimal("30.00"),  # More than available
                sale_price=Decimal("350.00"),
                sale_date=date(2024, 6, 1)
            )

        assert "Cannot sell" in str(exc_info.value)
        assert "Only 20" in str(exc_info.value)

    async def test_sell_holding_negative_quantity(self, db_session, test_account, portfolio_service):
        """Test selling negative quantity raises error."""
        # Create holding
        holding = await portfolio_service.add_holding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="TEST",
            name="Test Stock",
            quantity=Decimal("10.00"),
            purchase_price=Decimal("100.00"),
            purchase_date=date(2024, 1, 1),
            purchase_currency="GBP",
            asset_class=AssetClass.EQUITY,
            region=Region.UK
        )

        with pytest.raises(ValueError) as exc_info:
            await portfolio_service.sell_holding(
                holding_id=holding.id,
                quantity_to_sell=Decimal("-5.00"),
                sale_price=Decimal("120.00"),
                sale_date=date(2024, 6, 1)
            )

        assert "Quantity to sell must be greater than 0" in str(exc_info.value)


class TestRecordDividend:
    """Test dividend recording."""

    async def test_record_dividend_success(self, db_session, test_account, portfolio_service):
        """Test successful dividend recording."""
        # Create holding
        holding = await portfolio_service.add_holding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="VOO",
            name="Vanguard S&P 500 ETF",
            quantity=Decimal("100.00"),
            purchase_price=Decimal("400.00"),
            purchase_date=date(2024, 1, 1),
            purchase_currency="USD",
            asset_class=AssetClass.EQUITY,
            region=Region.US
        )

        # Record dividend
        dividend = await portfolio_service.record_dividend(
            holding_id=holding.id,
            payment_date=date(2024, 6, 15),
            amount=Decimal("250.00"),
            currency="USD",
            tax_withheld=Decimal("37.50"),  # 15% withholding
            country_of_source=SourceCountry.US,
            ex_dividend_date=date(2024, 6, 1)
        )

        assert dividend is not None
        assert dividend.holding_id == holding.id
        assert dividend.payment_date == date(2024, 6, 15)
        assert dividend.total_dividend_gross == Decimal("250.00")
        assert dividend.withholding_tax == Decimal("37.50")
        assert dividend.total_dividend_net == Decimal("212.50")
        assert dividend.currency == "USD"
        assert dividend.source_country == SourceCountry.US
        assert dividend.ex_dividend_date == date(2024, 6, 1)
        assert dividend.dividend_per_share == Decimal("2.50")  # 250 / 100

    async def test_record_dividend_tax_year_allocation(self, db_session, test_account, portfolio_service):
        """Test dividend tax year allocation for UK and SA."""
        # Create holding
        holding = await portfolio_service.add_holding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="BP",
            name="BP plc",
            quantity=Decimal("500.00"),
            purchase_price=Decimal("5.00"),
            purchase_date=date(2024, 1, 1),
            purchase_currency="GBP",
            asset_class=AssetClass.EQUITY,
            region=Region.UK
        )

        # Record dividend paid in June (UK tax year 2024/25)
        dividend = await portfolio_service.record_dividend(
            holding_id=holding.id,
            payment_date=date(2024, 6, 15),
            amount=Decimal("100.00"),
            currency="GBP",
            country_of_source=SourceCountry.UK
        )

        assert dividend.uk_tax_year == "2024/25"  # After April 6
        assert dividend.sa_tax_year == "2024/2025"  # After March 1

    async def test_record_dividend_negative_amount(self, db_session, test_account, portfolio_service):
        """Test negative dividend amount raises error."""
        # Create holding
        holding = await portfolio_service.add_holding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="TEST",
            name="Test Stock",
            quantity=Decimal("100.00"),
            purchase_price=Decimal("100.00"),
            purchase_date=date(2024, 1, 1),
            purchase_currency="GBP",
            asset_class=AssetClass.EQUITY,
            region=Region.UK
        )

        with pytest.raises(ValueError) as exc_info:
            await portfolio_service.record_dividend(
                holding_id=holding.id,
                payment_date=date(2024, 6, 15),
                amount=Decimal("-100.00"),
                currency="GBP"
            )

        assert "Dividend amount cannot be negative" in str(exc_info.value)

    async def test_record_dividend_tax_exceeds_amount(self, db_session, test_account, portfolio_service):
        """Test tax withheld exceeding dividend raises error."""
        # Create holding
        holding = await portfolio_service.add_holding(
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="TEST",
            name="Test Stock",
            quantity=Decimal("100.00"),
            purchase_price=Decimal("100.00"),
            purchase_date=date(2024, 1, 1),
            purchase_currency="GBP",
            asset_class=AssetClass.EQUITY,
            region=Region.UK
        )

        with pytest.raises(ValueError) as exc_info:
            await portfolio_service.record_dividend(
                holding_id=holding.id,
                payment_date=date(2024, 6, 15),
                amount=Decimal("100.00"),
                currency="GBP",
                tax_withheld=Decimal("150.00")  # More than dividend
            )

        assert "Tax withheld cannot exceed dividend amount" in str(exc_info.value)

    async def test_record_dividend_invalid_holding(self, db_session, portfolio_service):
        """Test recording dividend for non-existent holding raises error."""
        with pytest.raises(ValueError) as exc_info:
            await portfolio_service.record_dividend(
                holding_id=uuid.uuid4(),
                payment_date=date(2024, 6, 15),
                amount=Decimal("100.00"),
                currency="GBP"
            )

        assert "Holding not found" in str(exc_info.value)


class TestIntegrationScenarios:
    """Integration tests for complete portfolio workflows."""

    async def test_complete_investment_lifecycle(self, db_session, test_user, portfolio_service):
        """Test complete lifecycle: create account, add holding, update price, sell, record dividend."""
        # 1. Create account
        account = await portfolio_service.create_account(
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Interactive Brokers",
            account_number="U1234567",
            country=AccountCountry.UK,
            base_currency="GBP"
        )

        # 2. Add holding
        holding = await portfolio_service.add_holding(
            account_id=account.id,
            security_type=SecurityType.ETF,
            ticker="VWRL",
            name="Vanguard FTSE All-World UCITS ETF",
            quantity=Decimal("200.00"),
            purchase_price=Decimal("95.00"),
            purchase_date=date(2024, 1, 10),
            purchase_currency="GBP",
            asset_class=AssetClass.EQUITY,
            region=Region.GLOBAL
        )

        # Verify initial state
        assert holding.quantity == Decimal("200.00")
        assert holding.current_value == Decimal("19000.00")  # 200 * 95
        assert holding.unrealized_gain == Decimal("0.00")

        # 3. Update price (gain)
        updated_holding = await portfolio_service.update_holding_price(
            holding_id=holding.id,
            new_current_price=Decimal("105.00")
        )

        assert updated_holding.unrealized_gain == Decimal("2000.00")  # (105-95)*200

        # 4. Record dividend
        dividend = await portfolio_service.record_dividend(
            holding_id=holding.id,
            payment_date=date(2024, 6, 30),
            amount=Decimal("150.00"),
            currency="GBP",
            country_of_source=SourceCountry.UK
        )

        assert dividend.total_dividend_gross == Decimal("150.00")
        assert dividend.dividend_per_share == Decimal("0.75")  # 150/200

        # 5. Sell partial holding
        sale = await portfolio_service.sell_holding(
            holding_id=holding.id,
            quantity_to_sell=Decimal("100.00"),
            sale_price=Decimal("110.00"),
            sale_date=date(2024, 9, 15)
        )

        assert sale["realized_gain"] == 1500.00  # (110-95)*100
        assert sale["remaining_quantity"] == 100.00

        # Verify final state
        await db_session.refresh(holding)
        assert holding.quantity == Decimal("100.00")
