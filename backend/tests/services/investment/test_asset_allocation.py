"""
Tests for Asset Allocation Service

Test Coverage:
- Asset class allocation with multiple holdings
- Region allocation
- Sector allocation
- Portfolio summary aggregation
- Top holdings sorting
- Percentage calculations
- Single holding scenarios
- Empty portfolio handling
- Multiple accounts
- Currency exposure calculation
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import select

from models.investment import (
    InvestmentAccount, InvestmentHolding,
    AccountType, AccountCountry, AccountStatus,
    SecurityType, AssetClass, Region
)
from services.investment.asset_allocation_service import AssetAllocationService


@pytest.fixture
async def test_user(db_session):
    """Create test user."""
    from models.user import User, UserStatus, CountryPreference
    user = User(
        id=uuid4(),
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password_hash="hashed",
        email_verified=True,
        status=UserStatus.ACTIVE,
        country_preference=CountryPreference.BOTH,
        terms_accepted_at=datetime.utcnow(),
        marketing_consent=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_account(db_session, test_user):
    """Create test investment account."""
    from utils.encryption import encrypt_value

    account = InvestmentAccount(
        id=uuid4(),
        user_id=test_user.id,
        account_type=AccountType.GIA,
        provider="Test Broker",
        account_number_encrypted=encrypt_value("12345678"),
        account_number_last_4="5678",
        country=AccountCountry.UK,
        base_currency="GBP",
        account_open_date=date(2023, 1, 1),
        status=AccountStatus.ACTIVE,
        deleted=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def test_account_2(db_session, test_user):
    """Create second test investment account."""
    from utils.encryption import encrypt_value

    account = InvestmentAccount(
        id=uuid4(),
        user_id=test_user.id,
        account_type=AccountType.STOCKS_ISA,
        provider="ISA Provider",
        account_number_encrypted=encrypt_value("87654321"),
        account_number_last_4="4321",
        country=AccountCountry.UK,
        base_currency="GBP",
        account_open_date=date(2023, 6, 1),
        status=AccountStatus.ACTIVE,
        deleted=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def multiple_holdings(db_session, test_account, test_account_2):
    """Create multiple test holdings across different asset classes, regions, and sectors."""
    holdings = [
        # Account 1 - GIA
        InvestmentHolding(
            id=uuid4(),
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="AAPL",
            security_name="Apple Inc",
            quantity=Decimal('100.0000'),
            purchase_date=date(2023, 1, 15),
            purchase_price=Decimal('150.00'),
            purchase_currency="USD",
            current_price=Decimal('180.00'),
            asset_class=AssetClass.EQUITY,
            region=Region.US,
            sector="TECHNOLOGY",
            last_price_update=datetime.utcnow(),
            deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        InvestmentHolding(
            id=uuid4(),
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="MSFT",
            security_name="Microsoft Corp",
            quantity=Decimal('50.0000'),
            purchase_date=date(2023, 2, 1),
            purchase_price=Decimal('250.00'),
            purchase_currency="USD",
            current_price=Decimal('300.00'),
            asset_class=AssetClass.EQUITY,
            region=Region.US,
            sector="TECHNOLOGY",
            last_price_update=datetime.utcnow(),
            deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        InvestmentHolding(
            id=uuid4(),
            account_id=test_account.id,
            security_type=SecurityType.BOND,
            ticker="GILT10Y",
            security_name="UK 10Y Gilt",
            quantity=Decimal('1000.0000'),
            purchase_date=date(2023, 3, 1),
            purchase_price=Decimal('95.00'),
            purchase_currency="GBP",
            current_price=Decimal('98.00'),
            asset_class=AssetClass.FIXED_INCOME,
            region=Region.UK,
            sector="GOVERNMENT",
            last_price_update=datetime.utcnow(),
            deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        # Account 2 - ISA
        InvestmentHolding(
            id=uuid4(),
            account_id=test_account_2.id,
            security_type=SecurityType.ETF,
            ticker="VWRL",
            security_name="Vanguard FTSE All-World",
            quantity=Decimal('200.0000'),
            purchase_date=date(2023, 6, 15),
            purchase_price=Decimal('90.00'),
            purchase_currency="GBP",
            current_price=Decimal('95.00'),
            asset_class=AssetClass.EQUITY,
            region=Region.GLOBAL,
            sector="DIVERSIFIED",
            last_price_update=datetime.utcnow(),
            deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        InvestmentHolding(
            id=uuid4(),
            account_id=test_account_2.id,
            security_type=SecurityType.FUND,
            ticker="VUKE",
            security_name="Vanguard FTSE 100",
            quantity=Decimal('100.0000'),
            purchase_date=date(2023, 7, 1),
            purchase_price=Decimal('30.00'),
            purchase_currency="GBP",
            current_price=Decimal('32.00'),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            sector="DIVERSIFIED",
            last_price_update=datetime.utcnow(),
            deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
    ]

    for holding in holdings:
        db_session.add(holding)

    await db_session.commit()

    # Refresh all holdings
    for holding in holdings:
        await db_session.refresh(holding)

    return holdings


class TestAssetAllocationByAssetClass:
    """Tests for calculate_allocation_by_asset_class method."""

    async def test_allocation_with_multiple_holdings(self, db_session, test_user, multiple_holdings):
        """Test asset class allocation with multiple holdings across different classes."""
        service = AssetAllocationService(db_session)

        allocation = await service.calculate_allocation_by_asset_class(test_user.id)

        # Should have EQUITY and FIXED_INCOME
        assert 'EQUITY' in allocation
        assert 'FIXED_INCOME' in allocation

        # EQUITY should have 4 holdings (AAPL, MSFT, VWRL, VUKE)
        # AAPL: 100 * 180 = 18,000
        # MSFT: 50 * 300 = 15,000
        # VWRL: 200 * 95 = 19,000
        # VUKE: 100 * 32 = 3,200
        # Total EQUITY = 55,200

        # FIXED_INCOME should have 1 holding (GILT10Y)
        # GILT10Y: 1000 * 98 = 98,000
        # Total FIXED_INCOME = 98,000

        # Total portfolio = 153,200

        equity_value = allocation['EQUITY']['value']
        fixed_income_value = allocation['FIXED_INCOME']['value']

        assert equity_value == Decimal('55200.00')
        assert fixed_income_value == Decimal('98000.00')

        # Check percentages
        # EQUITY: 55,200 / 153,200 * 100 = 36.03%
        # FIXED_INCOME: 98,000 / 153,200 * 100 = 63.97%
        assert allocation['EQUITY']['percentage'] == Decimal('36.03')
        assert allocation['FIXED_INCOME']['percentage'] == Decimal('63.97')

    async def test_allocation_with_empty_portfolio(self, db_session, test_user):
        """Test asset class allocation with no holdings."""
        service = AssetAllocationService(db_session)

        allocation = await service.calculate_allocation_by_asset_class(test_user.id)

        assert allocation == {}

    async def test_allocation_with_single_holding(self, db_session, test_account):
        """Test asset class allocation with single holding."""
        # Create single holding
        holding = InvestmentHolding(
            id=uuid4(),
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="TEST",
            security_name="Test Stock",
            quantity=Decimal('100.0000'),
            purchase_date=date(2023, 1, 1),
            purchase_price=Decimal('50.00'),
            purchase_currency="GBP",
            current_price=Decimal('75.00'),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            sector="TECHNOLOGY",
            last_price_update=datetime.utcnow(),
            deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(holding)
        await db_session.commit()

        # Get account to get user_id
        result = await db_session.execute(
            select(InvestmentAccount).where(InvestmentAccount.id == test_account.id)
        )
        account = result.scalar_one()

        service = AssetAllocationService(db_session)
        allocation = await service.calculate_allocation_by_asset_class(account.user_id)

        # Should have only EQUITY at 100%
        assert len(allocation) == 1
        assert 'EQUITY' in allocation
        assert allocation['EQUITY']['value'] == Decimal('7500.00')
        assert allocation['EQUITY']['percentage'] == Decimal('100.00')

    async def test_allocation_excludes_deleted_holdings(self, db_session, test_account):
        """Test that deleted holdings are excluded from allocation."""
        # Create active holding
        active_holding = InvestmentHolding(
            id=uuid4(),
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="ACTIVE",
            security_name="Active Stock",
            quantity=Decimal('100.0000'),
            purchase_date=date(2023, 1, 1),
            purchase_price=Decimal('50.00'),
            purchase_currency="GBP",
            current_price=Decimal('60.00'),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            sector="TECHNOLOGY",
            last_price_update=datetime.utcnow(),
            deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Create deleted holding
        deleted_holding = InvestmentHolding(
            id=uuid4(),
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="DELETED",
            security_name="Deleted Stock",
            quantity=Decimal('100.0000'),
            purchase_date=date(2023, 1, 1),
            purchase_price=Decimal('50.00'),
            purchase_currency="GBP",
            current_price=Decimal('100.00'),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            sector="TECHNOLOGY",
            last_price_update=datetime.utcnow(),
            deleted=True,  # Deleted
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db_session.add(active_holding)
        db_session.add(deleted_holding)
        await db_session.commit()

        # Get account to get user_id
        result = await db_session.execute(
            select(InvestmentAccount).where(InvestmentAccount.id == test_account.id)
        )
        account = result.scalar_one()

        service = AssetAllocationService(db_session)
        allocation = await service.calculate_allocation_by_asset_class(account.user_id)

        # Should only include active holding (6,000)
        assert allocation['EQUITY']['value'] == Decimal('6000.00')


class TestAssetAllocationByRegion:
    """Tests for calculate_allocation_by_region method."""

    async def test_region_allocation_with_multiple_holdings(self, db_session, test_user, multiple_holdings):
        """Test region allocation with multiple holdings across different regions."""
        service = AssetAllocationService(db_session)

        allocation = await service.calculate_allocation_by_region(test_user.id)

        # Should have US, UK, and GLOBAL
        assert 'US' in allocation
        assert 'UK' in allocation
        assert 'GLOBAL' in allocation

        # US: AAPL (18,000) + MSFT (15,000) = 33,000
        # UK: GILT10Y (98,000) + VUKE (3,200) = 101,200
        # GLOBAL: VWRL (19,000) = 19,000
        # Total: 153,200

        assert allocation['US']['value'] == Decimal('33000.00')
        assert allocation['UK']['value'] == Decimal('101200.00')
        assert allocation['GLOBAL']['value'] == Decimal('19000.00')

        # Check percentages
        # US: 33,000 / 153,200 * 100 = 21.54%
        # UK: 101,200 / 153,200 * 100 = 66.06%
        # GLOBAL: 19,000 / 153,200 * 100 = 12.40%
        assert allocation['US']['percentage'] == Decimal('21.54')
        assert allocation['UK']['percentage'] == Decimal('66.06')
        assert allocation['GLOBAL']['percentage'] == Decimal('12.40')

    async def test_region_allocation_with_empty_portfolio(self, db_session, test_user):
        """Test region allocation with no holdings."""
        service = AssetAllocationService(db_session)

        allocation = await service.calculate_allocation_by_region(test_user.id)

        assert allocation == {}


class TestAssetAllocationBySector:
    """Tests for calculate_allocation_by_sector method."""

    async def test_sector_allocation_with_multiple_holdings(self, db_session, test_user, multiple_holdings):
        """Test sector allocation with multiple holdings across different sectors."""
        service = AssetAllocationService(db_session)

        allocation = await service.calculate_allocation_by_sector(test_user.id)

        # Should have TECHNOLOGY, GOVERNMENT, and DIVERSIFIED
        assert 'TECHNOLOGY' in allocation
        assert 'GOVERNMENT' in allocation
        assert 'DIVERSIFIED' in allocation

        # TECHNOLOGY: AAPL (18,000) + MSFT (15,000) = 33,000
        # GOVERNMENT: GILT10Y (98,000) = 98,000
        # DIVERSIFIED: VWRL (19,000) + VUKE (3,200) = 22,200
        # Total: 153,200

        assert allocation['TECHNOLOGY']['value'] == Decimal('33000.00')
        assert allocation['GOVERNMENT']['value'] == Decimal('98000.00')
        assert allocation['DIVERSIFIED']['value'] == Decimal('22200.00')

        # Check percentages
        assert allocation['TECHNOLOGY']['percentage'] == Decimal('21.54')
        assert allocation['GOVERNMENT']['percentage'] == Decimal('63.97')
        assert allocation['DIVERSIFIED']['percentage'] == Decimal('14.49')

    async def test_sector_allocation_with_null_sector(self, db_session, test_account):
        """Test sector allocation with holdings that have null sector."""
        # Create holding with null sector
        holding = InvestmentHolding(
            id=uuid4(),
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="NULL",
            security_name="Null Sector Stock",
            quantity=Decimal('100.0000'),
            purchase_date=date(2023, 1, 1),
            purchase_price=Decimal('50.00'),
            purchase_currency="GBP",
            current_price=Decimal('60.00'),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            sector=None,  # Null sector
            last_price_update=datetime.utcnow(),
            deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(holding)
        await db_session.commit()

        # Get account to get user_id
        result = await db_session.execute(
            select(InvestmentAccount).where(InvestmentAccount.id == test_account.id)
        )
        account = result.scalar_one()

        service = AssetAllocationService(db_session)
        allocation = await service.calculate_allocation_by_sector(account.user_id)

        # Should have UNCLASSIFIED
        assert 'UNCLASSIFIED' in allocation
        assert allocation['UNCLASSIFIED']['value'] == Decimal('6000.00')
        assert allocation['UNCLASSIFIED']['percentage'] == Decimal('100.00')


class TestPortfolioSummary:
    """Tests for get_portfolio_summary method."""

    async def test_portfolio_summary_with_multiple_holdings(self, db_session, test_user, multiple_holdings):
        """Test portfolio summary with multiple holdings."""
        service = AssetAllocationService(db_session)

        summary = await service.get_portfolio_summary(test_user.id)

        # Total value: 153,200
        assert summary['total_value'] == Decimal('153200.00')

        # Total cost basis:
        # AAPL: 100 * 150 = 15,000
        # MSFT: 50 * 250 = 12,500
        # GILT10Y: 1000 * 95 = 95,000
        # VWRL: 200 * 90 = 18,000
        # VUKE: 100 * 30 = 3,000
        # Total: 143,500
        assert summary['total_cost_basis'] == Decimal('143500.00')

        # Total unrealized gain: 153,200 - 143,500 = 9,700
        assert summary['total_unrealized_gain'] == Decimal('9700.00')

        # Unrealized gain percentage: 9,700 / 143,500 * 100 = 6.76%
        assert summary['unrealized_gain_percentage'] == Decimal('6.76')

        # Number of holdings
        assert summary['num_holdings'] == 5

        # Number of accounts
        assert summary['num_accounts'] == 2

        # Currency exposure
        assert 'USD' in summary['currency_exposure']
        assert 'GBP' in summary['currency_exposure']

        # Asset allocation
        assert 'EQUITY' in summary['asset_allocation']
        assert 'FIXED_INCOME' in summary['asset_allocation']

        # Top holdings
        assert len(summary['top_holdings']) == 5

        # First top holding should be GILT10Y (98,000)
        assert summary['top_holdings'][0]['security_name'] == 'UK 10Y Gilt'
        assert summary['top_holdings'][0]['current_value'] == Decimal('98000.00')

        # Percentage of portfolio
        # GILT10Y: 98,000 / 153,200 * 100 = 63.97%
        assert summary['top_holdings'][0]['percentage_of_portfolio'] == Decimal('63.97')

    async def test_portfolio_summary_with_empty_portfolio(self, db_session, test_user):
        """Test portfolio summary with no holdings."""
        service = AssetAllocationService(db_session)

        summary = await service.get_portfolio_summary(test_user.id)

        assert summary['total_value'] == Decimal('0.00')
        assert summary['total_cost_basis'] == Decimal('0.00')
        assert summary['total_unrealized_gain'] == Decimal('0.00')
        assert summary['unrealized_gain_percentage'] == Decimal('0.00')
        assert summary['num_holdings'] == 0
        assert summary['num_accounts'] == 0
        assert summary['currency_exposure'] == {}
        assert summary['asset_allocation'] == {}
        assert summary['top_holdings'] == []

    async def test_top_holdings_sorting(self, db_session, test_user, multiple_holdings):
        """Test that top holdings are sorted by value descending."""
        service = AssetAllocationService(db_session)

        summary = await service.get_portfolio_summary(test_user.id)

        top_holdings = summary['top_holdings']

        # Should be sorted by current_value descending
        # 1. GILT10Y: 98,000
        # 2. VWRL: 19,000
        # 3. AAPL: 18,000
        # 4. MSFT: 15,000
        # 5. VUKE: 3,200

        assert top_holdings[0]['security_name'] == 'UK 10Y Gilt'
        assert top_holdings[0]['current_value'] == Decimal('98000.00')

        assert top_holdings[1]['security_name'] == 'Vanguard FTSE All-World'
        assert top_holdings[1]['current_value'] == Decimal('19000.00')

        assert top_holdings[2]['security_name'] == 'Apple Inc'
        assert top_holdings[2]['current_value'] == Decimal('18000.00')

        assert top_holdings[3]['security_name'] == 'Microsoft Corp'
        assert top_holdings[3]['current_value'] == Decimal('15000.00')

        assert top_holdings[4]['security_name'] == 'Vanguard FTSE 100'
        assert top_holdings[4]['current_value'] == Decimal('3200.00')

    async def test_top_holdings_limited_to_10(self, db_session, test_account):
        """Test that top holdings are limited to 10 items."""
        # Create 15 holdings
        for i in range(15):
            holding = InvestmentHolding(
                id=uuid4(),
                account_id=test_account.id,
                security_type=SecurityType.STOCK,
                ticker=f"STOCK{i}",
                security_name=f"Stock {i}",
                quantity=Decimal('100.0000'),
                purchase_date=date(2023, 1, 1),
                purchase_price=Decimal('50.00'),
                purchase_currency="GBP",
                current_price=Decimal(str(50 + i)),  # Different prices for different values
                asset_class=AssetClass.EQUITY,
                region=Region.UK,
                sector="TECHNOLOGY",
                last_price_update=datetime.utcnow(),
                deleted=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db_session.add(holding)

        await db_session.commit()

        # Get account to get user_id
        result = await db_session.execute(
            select(InvestmentAccount).where(InvestmentAccount.id == test_account.id)
        )
        account = result.scalar_one()

        service = AssetAllocationService(db_session)
        summary = await service.get_portfolio_summary(account.user_id)

        # Should only return 10 holdings
        assert len(summary['top_holdings']) == 10

        # Should be sorted descending, so first should be Stock 14 (100 * 64 = 6400)
        assert summary['top_holdings'][0]['security_name'] == 'Stock 14'

    async def test_currency_exposure_calculation(self, db_session, test_user, multiple_holdings):
        """Test currency exposure calculation."""
        service = AssetAllocationService(db_session)

        summary = await service.get_portfolio_summary(test_user.id)

        currency_exposure = summary['currency_exposure']

        # USD holdings: AAPL (18,000) + MSFT (15,000) = 33,000
        # GBP holdings: GILT10Y (98,000) + VWRL (19,000) + VUKE (3,200) = 120,200
        # Total: 153,200

        assert 'USD' in currency_exposure
        assert 'GBP' in currency_exposure

        assert currency_exposure['USD']['value'] == Decimal('33000.00')
        assert currency_exposure['GBP']['value'] == Decimal('120200.00')

        # Check percentages
        # USD: 33,000 / 153,200 * 100 = 21.54%
        # GBP: 120,200 / 153,200 * 100 = 78.46%
        assert currency_exposure['USD']['percentage'] == Decimal('21.54')
        assert currency_exposure['GBP']['percentage'] == Decimal('78.46')

    async def test_percentage_calculation_precision(self, db_session, test_account):
        """Test that percentages are calculated to 2 decimal places."""
        # Create holdings with values that result in non-round percentages
        holdings = [
            InvestmentHolding(
                id=uuid4(),
                account_id=test_account.id,
                security_type=SecurityType.STOCK,
                ticker="STOCK1",
                security_name="Stock 1",
                quantity=Decimal('100.0000'),
                purchase_date=date(2023, 1, 1),
                purchase_price=Decimal('33.33'),
                purchase_currency="GBP",
                current_price=Decimal('33.33'),
                asset_class=AssetClass.EQUITY,
                region=Region.UK,
                sector="TECHNOLOGY",
                last_price_update=datetime.utcnow(),
                deleted=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            InvestmentHolding(
                id=uuid4(),
                account_id=test_account.id,
                security_type=SecurityType.STOCK,
                ticker="STOCK2",
                security_name="Stock 2",
                quantity=Decimal('100.0000'),
                purchase_date=date(2023, 1, 1),
                purchase_price=Decimal('66.67'),
                purchase_currency="GBP",
                current_price=Decimal('66.67'),
                asset_class=AssetClass.EQUITY,
                region=Region.US,
                sector="HEALTHCARE",
                last_price_update=datetime.utcnow(),
                deleted=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
        ]

        for holding in holdings:
            db_session.add(holding)

        await db_session.commit()

        # Get account to get user_id
        result = await db_session.execute(
            select(InvestmentAccount).where(InvestmentAccount.id == test_account.id)
        )
        account = result.scalar_one()

        service = AssetAllocationService(db_session)
        allocation = await service.calculate_allocation_by_region(account.user_id)

        # Total: 10,000
        # UK: 3,333 (33.33%)
        # US: 6,667 (66.67%)

        # Check that percentages are rounded to 2 decimal places
        assert allocation['UK']['percentage'] == Decimal('33.33')
        assert allocation['US']['percentage'] == Decimal('66.67')


class TestMultipleAccounts:
    """Tests for portfolio with multiple accounts."""

    async def test_summary_with_multiple_accounts(self, db_session, test_user, multiple_holdings):
        """Test portfolio summary includes holdings from multiple accounts."""
        service = AssetAllocationService(db_session)

        summary = await service.get_portfolio_summary(test_user.id)

        # Should have 2 accounts
        assert summary['num_accounts'] == 2

        # Should have 5 holdings total (3 from account 1, 2 from account 2)
        assert summary['num_holdings'] == 5

    async def test_allocation_excludes_closed_accounts(self, db_session, test_user, test_account):
        """Test that holdings from closed accounts are excluded."""
        # Create active holding
        active_holding = InvestmentHolding(
            id=uuid4(),
            account_id=test_account.id,
            security_type=SecurityType.STOCK,
            ticker="ACTIVE",
            security_name="Active Stock",
            quantity=Decimal('100.0000'),
            purchase_date=date(2023, 1, 1),
            purchase_price=Decimal('50.00'),
            purchase_currency="GBP",
            current_price=Decimal('60.00'),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            sector="TECHNOLOGY",
            last_price_update=datetime.utcnow(),
            deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(active_holding)

        # Create closed account
        from utils.encryption import encrypt_value
        closed_account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Closed Broker",
            account_number_encrypted=encrypt_value("99999999"),
            account_number_last_4="9999",
            country=AccountCountry.UK,
            base_currency="GBP",
            account_open_date=date(2022, 1, 1),
            status=AccountStatus.CLOSED,  # Closed
            deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(closed_account)
        await db_session.flush()

        # Create holding in closed account
        closed_holding = InvestmentHolding(
            id=uuid4(),
            account_id=closed_account.id,
            security_type=SecurityType.STOCK,
            ticker="CLOSED",
            security_name="Closed Account Stock",
            quantity=Decimal('100.0000'),
            purchase_date=date(2022, 1, 1),
            purchase_price=Decimal('50.00'),
            purchase_currency="GBP",
            current_price=Decimal('100.00'),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            sector="TECHNOLOGY",
            last_price_update=datetime.utcnow(),
            deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(closed_holding)
        await db_session.commit()

        service = AssetAllocationService(db_session)
        summary = await service.get_portfolio_summary(test_user.id)

        # Should only include active holding (6,000), not closed holding (10,000)
        assert summary['total_value'] == Decimal('6000.00')
        assert summary['num_holdings'] == 1

        # Should only count active account
        assert summary['num_accounts'] == 1
