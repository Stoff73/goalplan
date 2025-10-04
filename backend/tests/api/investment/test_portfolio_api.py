"""
Tests for portfolio analysis API endpoints.

Covers:
- Portfolio summary with aggregated metrics
- Asset allocation (by asset_class, region, sector)
- Performance metrics with dividends
- Capital gains tax calculations (UK and SA)
- Dividend tax calculations (UK and SA)
- Authentication and authorization
- Empty portfolio handling
- Error handling
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta
from uuid import uuid4, UUID

from models.investment import (
    InvestmentAccount,
    InvestmentHolding,
    DividendIncome,
    CapitalGainRealized,
    AccountType,
    AccountCountry,
    AccountStatus,
    SecurityType,
    AssetClass,
    Region,
    SourceCountry
)


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
async def investment_account_uk(db_session, test_user):
    """Create a UK ISA investment account for testing."""
    account = InvestmentAccount(
        id=uuid4(),
        user_id=test_user.id,
        account_type=AccountType.STOCKS_ISA,
        provider="Vanguard",
        account_number_encrypted="****5678",
        country=AccountCountry.UK,
        base_currency="GBP",
        account_open_date=date(2024, 1, 1),
        status=AccountStatus.ACTIVE,
        deleted=False
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def investment_account_gia(db_session, test_user):
    """Create a UK GIA investment account for testing."""
    account = InvestmentAccount(
        id=uuid4(),
        user_id=test_user.id,
        account_type=AccountType.GIA,
        provider="Interactive Brokers",
        account_number_encrypted="****1234",
        country=AccountCountry.UK,
        base_currency="GBP",
        account_open_date=date(2024, 1, 1),
        status=AccountStatus.ACTIVE,
        deleted=False
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def investment_account_sa(db_session, test_user):
    """Create a SA investment account for testing."""
    account = InvestmentAccount(
        id=uuid4(),
        user_id=test_user.id,
        account_type=AccountType.SA_UNIT_TRUST,
        provider="Allan Gray",
        account_number_encrypted="****9999",
        country=AccountCountry.SA,
        base_currency="ZAR",
        account_open_date=date(2024, 1, 1),
        status=AccountStatus.ACTIVE,
        deleted=False
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def holding_equity_uk(db_session, investment_account_uk):
    """Create a UK equity holding."""
    holding = InvestmentHolding(
        id=uuid4(),
        account_id=investment_account_uk.id,
        security_type=SecurityType.STOCK,
        ticker="VWRL",
        isin="IE00B3RBWM25",
        security_name="Vanguard FTSE All-World UCITS ETF",
        quantity=Decimal("100.0000"),
        purchase_date=date(2024, 1, 15),
        purchase_price=Decimal("95.50"),
        purchase_currency="GBP",
        current_price=Decimal("98.75"),
        asset_class=AssetClass.EQUITY,
        region=Region.GLOBAL,
        sector="Diversified",
        deleted=False
    )
    db_session.add(holding)
    await db_session.commit()
    await db_session.refresh(holding)
    return holding


@pytest.fixture
async def holding_fixed_income(db_session, investment_account_gia):
    """Create a fixed income holding."""
    holding = InvestmentHolding(
        id=uuid4(),
        account_id=investment_account_gia.id,
        security_type=SecurityType.BOND,
        ticker="VGOV",
        isin="IE00BZ163L38",
        security_name="Vanguard UK Government Bond Index Fund",
        quantity=Decimal("200.0000"),
        purchase_date=date(2024, 2, 1),
        purchase_price=Decimal("100.00"),
        purchase_currency="GBP",
        current_price=Decimal("100.00"),
        asset_class=AssetClass.FIXED_INCOME,
        region=Region.UK,
        sector="Government Bonds",
        deleted=False
    )
    db_session.add(holding)
    await db_session.commit()
    await db_session.refresh(holding)
    return holding


@pytest.fixture
async def holding_sa(db_session, investment_account_sa):
    """Create a SA holding."""
    holding = InvestmentHolding(
        id=uuid4(),
        account_id=investment_account_sa.id,
        security_type=SecurityType.FUND,
        ticker="ALLGR",
        security_name="Allan Gray Balanced Fund",
        quantity=Decimal("500.0000"),
        purchase_date=date(2024, 1, 10),
        purchase_price=Decimal("50.00"),
        purchase_currency="ZAR",
        current_price=Decimal("52.00"),
        asset_class=AssetClass.EQUITY,
        region=Region.EMERGING,
        sector="Balanced Fund",
        deleted=False
    )
    db_session.add(holding)
    await db_session.commit()
    await db_session.refresh(holding)
    return holding


@pytest.fixture
async def dividend_isa(db_session, holding_equity_uk):
    """Create a dividend payment for ISA holding."""
    dividend = DividendIncome(
        id=uuid4(),
        holding_id=holding_equity_uk.id,
        payment_date=date(2024, 3, 31),
        ex_dividend_date=date(2024, 3, 15),
        dividend_per_share=Decimal("1.25"),
        total_dividend_gross=Decimal("125.00"),
        withholding_tax=Decimal("0.00"),
        total_dividend_net=Decimal("125.00"),
        currency="GBP",
        source_country=SourceCountry.UK,
        uk_tax_year="2023/24",
        sa_tax_year="2023/2024"
    )
    db_session.add(dividend)
    await db_session.commit()
    await db_session.refresh(dividend)
    return dividend


@pytest.fixture
async def dividend_gia(db_session, holding_fixed_income):
    """Create a dividend payment for GIA holding."""
    dividend = DividendIncome(
        id=uuid4(),
        holding_id=holding_fixed_income.id,
        payment_date=date(2025, 4, 30),
        ex_dividend_date=date(2025, 4, 15),
        dividend_per_share=Decimal("2.00"),
        total_dividend_gross=Decimal("400.00"),
        withholding_tax=Decimal("0.00"),
        total_dividend_net=Decimal("400.00"),
        currency="GBP",
        source_country=SourceCountry.UK,
        uk_tax_year="2025/26",  # Current UK tax year
        sa_tax_year="2025/2026"
    )
    db_session.add(dividend)
    await db_session.commit()
    await db_session.refresh(dividend)
    return dividend


@pytest.fixture
async def capital_gain_uk(db_session, holding_fixed_income):
    """Create a realized capital gain for UK GIA holding."""
    gain = CapitalGainRealized(
        id=uuid4(),
        holding_id=holding_fixed_income.id,
        disposal_date=date(2024, 5, 15),
        quantity_sold=Decimal("50.0000"),
        sale_price=Decimal("105.00"),
        sale_value=Decimal("5250.00"),  # 50 * 105
        cost_basis=Decimal("5000.00"),  # 50 * 100
        gain_loss=Decimal("250.00"),    # 5250 - 5000
        tax_year="2024/25",
        country=AccountCountry.UK
    )
    db_session.add(gain)
    await db_session.commit()
    await db_session.refresh(gain)
    return gain


@pytest.fixture
async def capital_gain_sa(db_session, holding_sa):
    """Create a realized capital gain for SA holding."""
    gain = CapitalGainRealized(
        id=uuid4(),
        holding_id=holding_sa.id,
        disposal_date=date(2024, 5, 20),
        quantity_sold=Decimal("100.0000"),
        sale_price=Decimal("55.00"),
        sale_value=Decimal("5500.00"),  # 100 * 55
        cost_basis=Decimal("5000.00"),  # 100 * 50
        gain_loss=Decimal("500.00"),    # 5500 - 5000
        tax_year="2024/25",
        country=AccountCountry.SA
    )
    db_session.add(gain)
    await db_session.commit()
    await db_session.refresh(gain)
    return gain


# ============================================================================
# PORTFOLIO SUMMARY TESTS
# ============================================================================

@pytest.mark.asyncio
class TestPortfolioSummary:
    """Tests for GET /api/v1/investments/portfolio/summary"""

    async def test_portfolio_summary_with_holdings(
        self,
        test_client,
        authenticated_headers,
        holding_equity_uk,
        holding_fixed_income
    ):
        """Test portfolio summary with multiple holdings."""
        response = await test_client.get(
            "/api/v1/investments/portfolio/summary",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check basic metrics
        assert "total_value" in data
        assert "total_cost_basis" in data
        assert "total_unrealized_gain" in data
        assert "unrealized_gain_percentage" in data
        assert "num_holdings" in data
        assert "num_accounts" in data

        # Verify counts
        assert data["num_holdings"] == 2
        assert data["num_accounts"] == 2

        # Check allocation structures
        assert "currency_exposure" in data
        assert "asset_allocation" in data
        assert "top_holdings" in data

        # Verify currency exposure
        assert "GBP" in data["currency_exposure"]
        assert "value" in data["currency_exposure"]["GBP"]
        assert "percentage" in data["currency_exposure"]["GBP"]

        # Verify asset allocation
        assert "EQUITY" in data["asset_allocation"]
        assert "FIXED_INCOME" in data["asset_allocation"]

        # Verify top holdings
        assert len(data["top_holdings"]) <= 10
        if len(data["top_holdings"]) > 0:
            top_holding = data["top_holdings"][0]
            assert "id" in top_holding
            assert "security_name" in top_holding
            assert "ticker" in top_holding
            assert "current_value" in top_holding
            assert "percentage_of_portfolio" in top_holding

    async def test_portfolio_summary_empty_portfolio(
        self,
        test_client,
        authenticated_headers
    ):
        """Test portfolio summary with no holdings."""
        response = await test_client.get(
            "/api/v1/investments/portfolio/summary",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should return zero values
        assert Decimal(str(data["total_value"])) == Decimal("0.00")
        assert data["num_holdings"] == 0
        assert data["currency_exposure"] == {}
        assert data["asset_allocation"] == {}
        assert data["top_holdings"] == []

    async def test_portfolio_summary_requires_authentication(self, test_client):
        """Test that portfolio summary requires authentication."""
        response = await test_client.get(
            "/api/v1/investments/portfolio/summary"
        )

        assert response.status_code == 401


# ============================================================================
# ALLOCATION TESTS
# ============================================================================

@pytest.mark.asyncio
class TestPortfolioAllocation:
    """Tests for GET /api/v1/investments/portfolio/allocation"""

    async def test_allocation_by_asset_class(
        self,
        test_client,
        authenticated_headers,
        holding_equity_uk,
        holding_fixed_income
    ):
        """Test allocation by asset class."""
        response = await test_client.get(
            "/api/v1/investments/portfolio/allocation?by=asset_class",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "allocation" in data
        allocation = data["allocation"]

        # Should have EQUITY and FIXED_INCOME
        assert "EQUITY" in allocation
        assert "FIXED_INCOME" in allocation

        # Each allocation should have value and percentage
        assert "value" in allocation["EQUITY"]
        assert "percentage" in allocation["EQUITY"]

    async def test_allocation_by_region(
        self,
        test_client,
        authenticated_headers,
        holding_equity_uk,
        holding_fixed_income
    ):
        """Test allocation by region."""
        response = await test_client.get(
            "/api/v1/investments/portfolio/allocation?by=region",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "allocation" in data
        allocation = data["allocation"]

        # Should have GLOBAL and UK
        assert "GLOBAL" in allocation or "UK" in allocation

    async def test_allocation_by_sector(
        self,
        test_client,
        authenticated_headers,
        holding_equity_uk,
        holding_fixed_income
    ):
        """Test allocation by sector."""
        response = await test_client.get(
            "/api/v1/investments/portfolio/allocation?by=sector",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "allocation" in data
        allocation = data["allocation"]

        # Should have sectors
        assert len(allocation) >= 1

    async def test_allocation_invalid_by_parameter(
        self,
        test_client,
        authenticated_headers
    ):
        """Test allocation with invalid 'by' parameter."""
        response = await test_client.get(
            "/api/v1/investments/portfolio/allocation?by=invalid",
            headers=authenticated_headers
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower()

    async def test_allocation_default_to_asset_class(
        self,
        test_client,
        authenticated_headers,
        holding_equity_uk
    ):
        """Test allocation defaults to asset_class when 'by' not specified."""
        response = await test_client.get(
            "/api/v1/investments/portfolio/allocation",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "allocation" in data

    async def test_allocation_empty_portfolio(
        self,
        test_client,
        authenticated_headers
    ):
        """Test allocation with empty portfolio."""
        response = await test_client.get(
            "/api/v1/investments/portfolio/allocation?by=asset_class",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["allocation"] == {}

    async def test_allocation_requires_authentication(self, test_client):
        """Test that allocation requires authentication."""
        response = await test_client.get(
            "/api/v1/investments/portfolio/allocation"
        )

        assert response.status_code == 401


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.asyncio
class TestPortfolioPerformance:
    """Tests for GET /api/v1/investments/portfolio/performance"""

    async def test_performance_with_holdings_and_dividends(
        self,
        test_client,
        authenticated_headers,
        holding_equity_uk,
        holding_fixed_income,
        dividend_isa,
        dividend_gia
    ):
        """Test performance metrics with holdings and dividends."""
        response = await test_client.get(
            "/api/v1/investments/portfolio/performance",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check all required fields
        assert "total_value" in data
        assert "total_cost_basis" in data
        assert "total_unrealized_gain" in data
        assert "unrealized_gain_percentage" in data
        assert "ytd_dividend_income" in data
        assert "total_dividend_income" in data

        # Verify values are non-zero
        assert Decimal(str(data["total_value"])) > 0
        assert Decimal(str(data["total_cost_basis"])) > 0

        # Verify dividend income is tracked
        # dividend_gia is in current tax year (2024/25)
        assert Decimal(str(data["ytd_dividend_income"])) >= Decimal("400.00")
        # Total should include both dividends
        assert Decimal(str(data["total_dividend_income"])) >= Decimal("525.00")

    async def test_performance_empty_portfolio(
        self,
        test_client,
        authenticated_headers
    ):
        """Test performance metrics with empty portfolio."""
        response = await test_client.get(
            "/api/v1/investments/portfolio/performance",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        # All values should be zero
        assert Decimal(str(data["total_value"])) == Decimal("0.00")
        assert Decimal(str(data["total_cost_basis"])) == Decimal("0.00")
        assert Decimal(str(data["total_unrealized_gain"])) == Decimal("0.00")
        assert Decimal(str(data["ytd_dividend_income"])) == Decimal("0.00")
        assert Decimal(str(data["total_dividend_income"])) == Decimal("0.00")

    async def test_performance_requires_authentication(self, test_client):
        """Test that performance requires authentication."""
        response = await test_client.get(
            "/api/v1/investments/portfolio/performance"
        )

        assert response.status_code == 401


# ============================================================================
# CAPITAL GAINS TAX TESTS
# ============================================================================

@pytest.mark.asyncio
class TestCapitalGainsTax:
    """Tests for GET /api/v1/investments/tax/capital-gains"""

    async def test_capital_gains_uk(
        self,
        test_client,
        authenticated_headers,
        capital_gain_uk
    ):
        """Test UK capital gains tax calculation."""
        response = await test_client.get(
            "/api/v1/investments/tax/capital-gains?country=UK&tax_year=2024/25",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "capital_gains" in data
        assert "dividend_tax" in data

        # Check UK CGT fields
        cgt = data["capital_gains"]
        assert "total_gains" in cgt
        assert "exempt_amount" in cgt
        assert "taxable_gains" in cgt
        assert "tax_rate" in cgt
        assert "tax_owed" in cgt
        assert "isa_gains_tax_free" in cgt

        # Verify calculation
        assert Decimal(str(cgt["total_gains"])) >= Decimal("250.00")

    async def test_capital_gains_sa(
        self,
        test_client,
        authenticated_headers,
        capital_gain_sa
    ):
        """Test SA capital gains tax calculation."""
        response = await test_client.get(
            "/api/v1/investments/tax/capital-gains?country=SA&tax_year=2024/25",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "capital_gains" in data
        assert "dividend_tax" in data

        # Check SA CGT fields
        cgt = data["capital_gains"]
        assert "total_gains" in cgt
        assert "inclusion_rate" in cgt
        assert "included_gain" in cgt
        assert "tax_rate" in cgt
        assert "tax_owed" in cgt

        # Verify inclusion rate (40%)
        assert Decimal(str(cgt["inclusion_rate"])) == Decimal("0.40")

        # Verify calculation
        assert Decimal(str(cgt["total_gains"])) >= Decimal("500.00")

    async def test_capital_gains_default_tax_year(
        self,
        test_client,
        authenticated_headers
    ):
        """Test capital gains defaults to current tax year."""
        response = await test_client.get(
            "/api/v1/investments/tax/capital-gains?country=UK",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "capital_gains" in data

    async def test_capital_gains_invalid_country(
        self,
        test_client,
        authenticated_headers
    ):
        """Test capital gains with invalid country."""
        response = await test_client.get(
            "/api/v1/investments/tax/capital-gains?country=US",
            headers=authenticated_headers
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    async def test_capital_gains_different_tax_years(
        self,
        test_client,
        authenticated_headers
    ):
        """Test capital gains for different tax years."""
        # Current year
        response1 = await test_client.get(
            "/api/v1/investments/tax/capital-gains?country=UK&tax_year=2024/25",
            headers=authenticated_headers
        )
        assert response1.status_code == 200

        # Previous year
        response2 = await test_client.get(
            "/api/v1/investments/tax/capital-gains?country=UK&tax_year=2023/24",
            headers=authenticated_headers
        )
        assert response2.status_code == 200

    async def test_capital_gains_requires_authentication(self, test_client):
        """Test that capital gains requires authentication."""
        response = await test_client.get(
            "/api/v1/investments/tax/capital-gains"
        )

        assert response.status_code == 401


# ============================================================================
# DIVIDEND TAX TESTS (via capital-gains endpoint)
# ============================================================================

@pytest.mark.asyncio
class TestDividendTax:
    """Tests for dividend tax calculations within capital-gains endpoint"""

    async def test_dividend_tax_uk_with_isa_and_gia(
        self,
        test_client,
        authenticated_headers,
        dividend_isa,
        dividend_gia
    ):
        """Test UK dividend tax calculation with ISA and GIA dividends."""
        response = await test_client.get(
            "/api/v1/investments/tax/capital-gains?country=UK&tax_year=2025/26",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check dividend tax structure
        div_tax = data["dividend_tax"]
        assert "total_dividends" in div_tax
        assert "allowance" in div_tax
        assert "taxable_dividends" in div_tax
        assert "tax_rate" in div_tax
        assert "tax_owed" in div_tax
        assert "isa_dividends_tax_free" in div_tax

        # Verify dividend tracking
        # dividend_isa is in 2023/24 (tax-free ISA), dividend_gia is in 2025/26 (current year GIA)
        # The GIA dividend (£400) should be tracked for the current tax year
        assert Decimal(str(div_tax["total_dividends"])) >= Decimal("400.00")

    async def test_dividend_tax_sa(
        self,
        test_client,
        authenticated_headers,
        holding_sa
    ):
        """Test SA dividend withholding tax calculation."""
        response = await test_client.get(
            "/api/v1/investments/tax/capital-gains?country=SA&tax_year=2024/25",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check SA dividend tax structure
        div_tax = data["dividend_tax"]
        assert "total_dividends" in div_tax
        assert "withholding_rate" in div_tax
        assert "tax_withheld" in div_tax

        # Verify withholding rate (20%)
        assert Decimal(str(div_tax["withholding_rate"])) == Decimal("0.20")


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

@pytest.mark.asyncio
class TestEdgeCases:
    """Tests for edge cases and error handling"""

    async def test_soft_deleted_holdings_excluded(
        self,
        test_client,
        authenticated_headers,
        db_session,
        holding_equity_uk
    ):
        """Test that soft-deleted holdings are excluded from portfolio."""
        # Soft delete holding
        holding_equity_uk.deleted = True
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/investments/portfolio/summary",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["num_holdings"] == 0

    async def test_inactive_accounts_excluded(
        self,
        test_client,
        authenticated_headers,
        db_session,
        investment_account_uk,
        holding_equity_uk
    ):
        """Test that holdings from inactive accounts are excluded."""
        # Set account to closed
        investment_account_uk.status = AccountStatus.CLOSED
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/investments/portfolio/summary",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["num_holdings"] == 0
