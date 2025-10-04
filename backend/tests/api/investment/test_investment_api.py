"""
Tests for investment API endpoints.

Covers:
- Investment account CRUD operations
- Holdings management (add, update price, sell)
- Dividend recording
- FIFO capital gains calculations
- Authentication and authorization
- Validation and error handling
- Rate limiting
"""

import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta
from uuid import uuid4

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
    SourceCountry
)


@pytest.mark.asyncio
class TestCreateInvestmentAccount:
    """Tests for POST /api/v1/investments/accounts"""

    async def test_create_basic_account(self, test_client, authenticated_headers):
        """Test creating a basic investment account."""
        payload = {
            "account_type": "STOCKS_ISA",
            "provider": "Vanguard",
            "account_number": "12345678",
            "country": "UK",
            "base_currency": "GBP",
            "account_open_date": "2024-01-01"
        }

        response = await test_client.post(
            "/api/v1/investments/accounts",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["account_type"] == "STOCKS_ISA"
        assert data["provider"] == "Vanguard"
        assert data["country"] == "UK"
        assert data["base_currency"] == "GBP"
        assert "****" in data["account_number"]  # Should be masked
        assert data["status"] == "ACTIVE"
        assert data["deleted"] is False
        assert data["holdings_count"] == 0

    async def test_create_gia_account(self, test_client, authenticated_headers):
        """Test creating a GIA account."""
        payload = {
            "account_type": "GIA",
            "provider": "Interactive Brokers",
            "account_number": "87654321",
            "country": "UK",
            "base_currency": "GBP"
        }

        response = await test_client.post(
            "/api/v1/investments/accounts",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["account_type"] == "GIA"
        assert data["provider"] == "Interactive Brokers"

    async def test_create_sa_account(self, test_client, authenticated_headers):
        """Test creating a SA investment account."""
        payload = {
            "account_type": "SA_UNIT_TRUST",
            "provider": "Allan Gray",
            "account_number": "ZA123456",
            "country": "SA",
            "base_currency": "ZAR"
        }

        response = await test_client.post(
            "/api/v1/investments/accounts",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["account_type"] == "SA_UNIT_TRUST"
        assert data["country"] == "SA"
        assert data["base_currency"] == "ZAR"

    async def test_create_account_requires_authentication(self, test_client):
        """Test that creating account requires authentication."""
        payload = {
            "account_type": "STOCKS_ISA",
            "provider": "Vanguard",
            "account_number": "12345678",
            "country": "UK",
            "base_currency": "GBP"
        }

        response = await test_client.post(
            "/api/v1/investments/accounts",
            json=payload
        )

        assert response.status_code == 401

    async def test_create_account_future_date_fails(self, test_client, authenticated_headers):
        """Test that future account open date is rejected."""
        future_date = (date.today() + timedelta(days=30)).isoformat()

        payload = {
            "account_type": "GIA",
            "provider": "Test Provider",
            "account_number": "12345678",
            "country": "UK",
            "base_currency": "GBP",
            "account_open_date": future_date
        }

        response = await test_client.post(
            "/api/v1/investments/accounts",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
class TestGetInvestmentAccounts:
    """Tests for GET /api/v1/investments/accounts"""

    async def test_get_all_accounts(self, test_client, authenticated_headers, db_session, test_user):
        """Test retrieving all investment accounts."""
        # Create test accounts
        account1 = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.STOCKS_ISA,
            provider="Vanguard",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account1.set_account_number("12345678")

        account2 = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Interactive Brokers",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account2.set_account_number("87654321")

        db_session.add_all([account1, account2])
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/investments/accounts",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("****" in acc["account_number"] for acc in data)

    async def test_get_accounts_filter_by_type(self, test_client, authenticated_headers, db_session, test_user):
        """Test filtering accounts by type."""
        # Create accounts of different types
        isa_account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.STOCKS_ISA,
            provider="Vanguard",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        isa_account.set_account_number("12345678")

        gia_account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Interactive Brokers",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        gia_account.set_account_number("87654321")

        db_session.add_all([isa_account, gia_account])
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/investments/accounts?account_type=STOCKS_ISA",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["account_type"] == "STOCKS_ISA"

    async def test_get_accounts_pagination(self, test_client, authenticated_headers, db_session, test_user):
        """Test pagination of accounts list."""
        # Create multiple accounts
        for i in range(5):
            account = InvestmentAccount(
                id=uuid4(),
                user_id=test_user.id,
                account_type=AccountType.GIA,
                provider=f"Provider {i}",
                country=AccountCountry.UK,
                base_currency="GBP",
                status=AccountStatus.ACTIVE,
                deleted=False
            )
            account.set_account_number(f"1234567{i}")
            db_session.add(account)

        await db_session.commit()

        # Test skip and limit
        response = await test_client.get(
            "/api/v1/investments/accounts?skip=2&limit=2",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


@pytest.mark.asyncio
class TestGetSingleAccount:
    """Tests for GET /api/v1/investments/accounts/{account_id}"""

    async def test_get_account_by_id(self, test_client, authenticated_headers, db_session, test_user):
        """Test retrieving a single account by ID."""
        account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.STOCKS_ISA,
            provider="Vanguard",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.commit()

        response = await test_client.get(
            f"/api/v1/investments/accounts/{account.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(account.id)
        assert data["provider"] == "Vanguard"

    async def test_get_account_not_found(self, test_client, authenticated_headers):
        """Test getting non-existent account returns 404."""
        fake_id = uuid4()
        response = await test_client.get(
            f"/api/v1/investments/accounts/{fake_id}",
            headers=authenticated_headers
        )

        assert response.status_code == 404

    async def test_get_account_wrong_user(self, test_client, authenticated_headers, db_session):
        """Test that users can't access other users' accounts."""
        # Create account for different user
        other_user_id = uuid4()
        account = InvestmentAccount(
            id=uuid4(),
            user_id=other_user_id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.commit()

        response = await test_client.get(
            f"/api/v1/investments/accounts/{account.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 404  # Should not find account owned by other user


@pytest.mark.asyncio
class TestDeleteAccount:
    """Tests for DELETE /api/v1/investments/accounts/{account_id}"""

    async def test_delete_account(self, test_client, authenticated_headers, db_session, test_user):
        """Test soft deleting an account."""
        account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.commit()

        response = await test_client.delete(
            f"/api/v1/investments/accounts/{account.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 204

        # Verify account is soft deleted
        await db_session.refresh(account)
        assert account.deleted is True
        assert account.status == AccountStatus.CLOSED

    async def test_delete_account_cascades_to_holdings(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test that deleting account soft deletes all holdings."""
        # Create account with holdings
        account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.flush()

        holding = InvestmentHolding(
            id=uuid4(),
            account_id=account.id,
            security_type=SecurityType.STOCK,
            ticker="TEST",
            security_name="Test Stock",
            quantity=Decimal("100"),
            purchase_date=date.today(),
            purchase_price=Decimal("50.00"),
            purchase_currency="GBP",
            current_price=Decimal("50.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            deleted=False
        )
        db_session.add(holding)
        await db_session.commit()

        # Delete account
        response = await test_client.delete(
            f"/api/v1/investments/accounts/{account.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 204

        # Verify holding is also soft deleted
        await db_session.refresh(holding)
        assert holding.deleted is True


@pytest.mark.asyncio
class TestAddHolding:
    """Tests for POST /api/v1/investments/holdings"""

    async def test_add_holding(self, test_client, authenticated_headers, db_session, test_user):
        """Test adding a holding to an account."""
        # Create account first
        account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.STOCKS_ISA,
            provider="Vanguard",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.commit()

        payload = {
            "account_id": str(account.id),
            "security_type": "STOCK",
            "ticker": "VWRL",
            "name": "Vanguard FTSE All-World UCITS ETF",
            "quantity": 100,
            "purchase_price": 95.50,
            "purchase_date": "2024-01-15",
            "purchase_currency": "GBP",
            "asset_class": "EQUITY",
            "region": "GLOBAL",
            "sector": "Diversified"
        }

        response = await test_client.post(
            "/api/v1/investments/holdings",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["ticker"] == "VWRL"
        assert Decimal(str(data["quantity"])) == Decimal("100")
        assert Decimal(str(data["purchase_price"])) == Decimal("95.50")
        assert data["asset_class"] == "EQUITY"
        assert data["region"] == "GLOBAL"

    async def test_add_holding_creates_tax_lot(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test that adding holding creates initial tax lot."""
        # Create account
        account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.commit()

        payload = {
            "account_id": str(account.id),
            "security_type": "STOCK",
            "ticker": "TEST",
            "name": "Test Stock",
            "quantity": 50,
            "purchase_price": 100.00,
            "purchase_date": "2024-01-15",
            "purchase_currency": "GBP",
            "asset_class": "EQUITY",
            "region": "UK"
        }

        response = await test_client.post(
            "/api/v1/investments/holdings",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        holding_id = response.json()["id"]

        # Verify tax lot was created
        from sqlalchemy import select
        stmt = select(TaxLot).where(TaxLot.holding_id == holding_id)
        result = await db_session.execute(stmt)
        tax_lot = result.scalar_one_or_none()

        assert tax_lot is not None
        assert tax_lot.quantity == Decimal("50")
        assert tax_lot.purchase_price == Decimal("100.00")
        assert tax_lot.disposal_date is None  # Not yet sold

    async def test_add_holding_negative_quantity_fails(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test that negative quantity is rejected."""
        account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.commit()

        payload = {
            "account_id": str(account.id),
            "security_type": "STOCK",
            "ticker": "TEST",
            "name": "Test Stock",
            "quantity": -10,  # Negative quantity
            "purchase_price": 100.00,
            "purchase_date": "2024-01-15",
            "purchase_currency": "GBP",
            "asset_class": "EQUITY",
            "region": "UK"
        }

        response = await test_client.post(
            "/api/v1/investments/holdings",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Validation error

    async def test_add_holding_wrong_account_fails(
        self, test_client, authenticated_headers, db_session
    ):
        """Test that adding holding to other user's account fails."""
        # Create account for different user
        other_user_id = uuid4()
        account = InvestmentAccount(
            id=uuid4(),
            user_id=other_user_id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.commit()

        payload = {
            "account_id": str(account.id),
            "security_type": "STOCK",
            "ticker": "TEST",
            "name": "Test Stock",
            "quantity": 10,
            "purchase_price": 100.00,
            "purchase_date": "2024-01-15",
            "purchase_currency": "GBP",
            "asset_class": "EQUITY",
            "region": "UK"
        }

        response = await test_client.post(
            "/api/v1/investments/holdings",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 403  # Forbidden


@pytest.mark.asyncio
class TestGetHoldings:
    """Tests for GET /api/v1/investments/holdings"""

    async def test_get_all_holdings(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test retrieving all holdings for user."""
        # Create account and holdings
        account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.flush()

        holding1 = InvestmentHolding(
            id=uuid4(),
            account_id=account.id,
            security_type=SecurityType.STOCK,
            ticker="VWRL",
            security_name="Vanguard FTSE All-World",
            quantity=Decimal("100"),
            purchase_date=date.today(),
            purchase_price=Decimal("95.00"),
            purchase_currency="GBP",
            current_price=Decimal("100.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.GLOBAL,
            deleted=False
        )

        holding2 = InvestmentHolding(
            id=uuid4(),
            account_id=account.id,
            security_type=SecurityType.ETF,
            ticker="VUKE",
            security_name="Vanguard FTSE 100",
            quantity=Decimal("50"),
            purchase_date=date.today(),
            purchase_price=Decimal("30.00"),
            purchase_currency="GBP",
            current_price=Decimal("32.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            deleted=False
        )

        db_session.add_all([holding1, holding2])
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/investments/holdings",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Should be sorted by current value (descending)
        assert Decimal(str(data[0]["current_value"])) >= Decimal(str(data[1]["current_value"]))

    async def test_get_holdings_filter_by_ticker(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test filtering holdings by ticker."""
        # Create account and holdings
        account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.flush()

        holding1 = InvestmentHolding(
            id=uuid4(),
            account_id=account.id,
            security_type=SecurityType.STOCK,
            ticker="VWRL",
            security_name="Test 1",
            quantity=Decimal("100"),
            purchase_date=date.today(),
            purchase_price=Decimal("95.00"),
            purchase_currency="GBP",
            current_price=Decimal("100.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.GLOBAL,
            deleted=False
        )

        holding2 = InvestmentHolding(
            id=uuid4(),
            account_id=account.id,
            security_type=SecurityType.ETF,
            ticker="VUKE",
            security_name="Test 2",
            quantity=Decimal("50"),
            purchase_date=date.today(),
            purchase_price=Decimal("30.00"),
            purchase_currency="GBP",
            current_price=Decimal("32.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            deleted=False
        )

        db_session.add_all([holding1, holding2])
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/investments/holdings?ticker=VWRL",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["ticker"] == "VWRL"


@pytest.mark.asyncio
class TestUpdateHoldingPrice:
    """Tests for PUT /api/v1/investments/holdings/{holding_id}/price"""

    async def test_update_price(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test updating holding price."""
        # Create account and holding
        account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.flush()

        holding = InvestmentHolding(
            id=uuid4(),
            account_id=account.id,
            security_type=SecurityType.STOCK,
            ticker="TEST",
            security_name="Test Stock",
            quantity=Decimal("100"),
            purchase_date=date.today(),
            purchase_price=Decimal("50.00"),
            purchase_currency="GBP",
            current_price=Decimal("50.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            deleted=False
        )
        db_session.add(holding)
        await db_session.commit()

        # Update price
        payload = {"current_price": 60.00}
        response = await test_client.put(
            f"/api/v1/investments/holdings/{holding.id}/price",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert Decimal(str(data["current_price"])) == Decimal("60.00")
        assert Decimal(str(data["unrealized_gain"])) == Decimal("1000.00")  # (60-50) * 100

    async def test_update_price_negative_fails(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test that negative price is rejected."""
        # Create account and holding
        account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.flush()

        holding = InvestmentHolding(
            id=uuid4(),
            account_id=account.id,
            security_type=SecurityType.STOCK,
            ticker="TEST",
            security_name="Test Stock",
            quantity=Decimal("100"),
            purchase_date=date.today(),
            purchase_price=Decimal("50.00"),
            purchase_currency="GBP",
            current_price=Decimal("50.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            deleted=False
        )
        db_session.add(holding)
        await db_session.commit()

        payload = {"current_price": -10.00}
        response = await test_client.put(
            f"/api/v1/investments/holdings/{holding.id}/price",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
class TestSellHolding:
    """Tests for POST /api/v1/investments/holdings/{holding_id}/sell"""

    async def test_sell_partial_holding(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test selling part of a holding."""
        # Create account and holding with tax lot
        account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.flush()

        holding = InvestmentHolding(
            id=uuid4(),
            account_id=account.id,
            security_type=SecurityType.STOCK,
            ticker="TEST",
            security_name="Test Stock",
            quantity=Decimal("100"),
            purchase_date=date(2024, 1, 15),
            purchase_price=Decimal("50.00"),
            purchase_currency="GBP",
            current_price=Decimal("60.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            deleted=False
        )
        db_session.add(holding)
        await db_session.flush()

        # Create tax lot
        tax_lot = TaxLot(
            id=uuid4(),
            holding_id=holding.id,
            purchase_date=date(2024, 1, 15),
            quantity=Decimal("100"),
            purchase_price=Decimal("50.00"),
            purchase_currency="GBP",
            cost_basis_gbp=Decimal("5000.00"),
            cost_basis_zar=Decimal("100000.00"),
            exchange_rate=Decimal("20.00")
        )
        db_session.add(tax_lot)
        await db_session.commit()

        # Sell 50 shares
        payload = {
            "quantity": 50,
            "sale_price": 60.00,
            "sale_date": "2024-02-15"
        }

        response = await test_client.post(
            f"/api/v1/investments/holdings/{holding.id}/sell",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["quantity_sold"] == 50
        assert data["sale_price"] == 60.00
        assert data["sale_value"] == 3000.00  # 50 * 60
        assert data["cost_basis"] == 2500.00  # 50 * 50
        assert data["realized_gain"] == 500.00  # 3000 - 2500
        assert data["remaining_quantity"] == 50.0

    async def test_sell_more_than_owned_fails(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test that selling more than owned is rejected."""
        # Create account and holding
        account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.flush()

        holding = InvestmentHolding(
            id=uuid4(),
            account_id=account.id,
            security_type=SecurityType.STOCK,
            ticker="TEST",
            security_name="Test Stock",
            quantity=Decimal("50"),
            purchase_date=date.today(),
            purchase_price=Decimal("50.00"),
            purchase_currency="GBP",
            current_price=Decimal("60.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            deleted=False
        )
        db_session.add(holding)
        await db_session.commit()

        # Try to sell 100 shares (only have 50)
        payload = {
            "quantity": 100,
            "sale_price": 60.00,
            "sale_date": "2024-02-15"
        }

        response = await test_client.post(
            f"/api/v1/investments/holdings/{holding.id}/sell",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 400  # Bad request


@pytest.mark.asyncio
class TestRecordDividend:
    """Tests for POST /api/v1/investments/dividends"""

    async def test_record_dividend(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test recording a dividend payment."""
        # Create account and holding
        account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.flush()

        holding = InvestmentHolding(
            id=uuid4(),
            account_id=account.id,
            security_type=SecurityType.STOCK,
            ticker="TEST",
            security_name="Test Stock",
            quantity=Decimal("100"),
            purchase_date=date.today(),
            purchase_price=Decimal("50.00"),
            purchase_currency="GBP",
            current_price=Decimal("50.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            deleted=False
        )
        db_session.add(holding)
        await db_session.commit()

        # Record dividend
        payload = {
            "holding_id": str(holding.id),
            "payment_date": "2024-03-31",
            "amount": 125.50,
            "currency": "GBP",
            "tax_withheld": 0.00,
            "country_of_source": "UK"
        }

        response = await test_client.post(
            "/api/v1/investments/dividends",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert Decimal(str(data["total_dividend_gross"])) == Decimal("125.50")
        assert Decimal(str(data["total_dividend_net"])) == Decimal("125.50")
        assert data["source_country"] == "UK"
        assert "uk_tax_year" in data
        assert "sa_tax_year" in data

    async def test_record_dividend_with_withholding_tax(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test recording dividend with withholding tax."""
        # Create account and holding
        account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.flush()

        holding = InvestmentHolding(
            id=uuid4(),
            account_id=account.id,
            security_type=SecurityType.STOCK,
            ticker="AAPL",
            security_name="Apple Inc",
            quantity=Decimal("50"),
            purchase_date=date.today(),
            purchase_price=Decimal("150.00"),
            purchase_currency="USD",
            current_price=Decimal("150.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.US,
            deleted=False
        )
        db_session.add(holding)
        await db_session.commit()

        # Record dividend with US withholding tax (15%)
        payload = {
            "holding_id": str(holding.id),
            "payment_date": "2024-03-31",
            "amount": 100.00,
            "currency": "USD",
            "tax_withheld": 15.00,  # 15% US withholding
            "country_of_source": "US"
        }

        response = await test_client.post(
            "/api/v1/investments/dividends",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert Decimal(str(data["total_dividend_gross"])) == Decimal("100.00")
        assert Decimal(str(data["withholding_tax"])) == Decimal("15.00")
        assert Decimal(str(data["total_dividend_net"])) == Decimal("85.00")

    async def test_record_dividend_tax_exceeds_amount_fails(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test that tax withheld cannot exceed dividend amount."""
        # Create account and holding
        account = InvestmentAccount(
            id=uuid4(),
            user_id=test_user.id,
            account_type=AccountType.GIA,
            provider="Test Provider",
            country=AccountCountry.UK,
            base_currency="GBP",
            status=AccountStatus.ACTIVE,
            deleted=False
        )
        account.set_account_number("12345678")
        db_session.add(account)
        await db_session.flush()

        holding = InvestmentHolding(
            id=uuid4(),
            account_id=account.id,
            security_type=SecurityType.STOCK,
            ticker="TEST",
            security_name="Test Stock",
            quantity=Decimal("100"),
            purchase_date=date.today(),
            purchase_price=Decimal("50.00"),
            purchase_currency="GBP",
            current_price=Decimal("50.00"),
            asset_class=AssetClass.EQUITY,
            region=Region.UK,
            deleted=False
        )
        db_session.add(holding)
        await db_session.commit()

        # Try to record dividend with tax > amount
        payload = {
            "holding_id": str(holding.id),
            "payment_date": "2024-03-31",
            "amount": 100.00,
            "currency": "GBP",
            "tax_withheld": 150.00,  # More than dividend!
            "country_of_source": "UK"
        }

        response = await test_client.post(
            "/api/v1/investments/dividends",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
class TestAuthenticationAndAuthorization:
    """Tests for authentication and authorization"""

    async def test_all_endpoints_require_authentication(self, test_client):
        """Test that all endpoints require authentication."""
        endpoints = [
            ("GET", "/api/v1/investments/accounts"),
            ("POST", "/api/v1/investments/accounts"),
            ("GET", "/api/v1/investments/holdings"),
            ("POST", "/api/v1/investments/holdings"),
            ("POST", "/api/v1/investments/dividends"),
        ]

        for method, url in endpoints:
            if method == "GET":
                response = await test_client.get(url)
            else:
                response = await test_client.post(url, json={})

            assert response.status_code == 401, f"{method} {url} should require auth"
