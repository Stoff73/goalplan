"""
Tests for savings account API endpoints.

Covers:
- CRUD operations (create, read, update, delete)
- Balance management (update balance, history)
- Summary endpoint (aggregation)
- ISA/TFSA contribution tracking
- Authentication and authorization
- Validation and error handling
"""

import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta
from uuid import uuid4

from models.savings_account import (
    SavingsAccount,
    AccountBalanceHistory,
    AccountType,
    AccountPurpose,
    AccountCountry,
    Currency,
    ISAContribution,
    TFSAContribution
)


@pytest.mark.asyncio
class TestCreateSavingsAccount:
    """Tests for POST /api/v1/savings/accounts"""

    async def test_create_basic_account(self, test_client, authenticated_headers):
        """Test creating a basic savings account."""
        payload = {
            "bank_name": "Barclays",
            "account_name": "My Savings",
            "account_number": "12345678",
            "account_type": "SAVINGS",
            "currency": "GBP",
            "current_balance": 10000.00,
            "interest_rate": 4.5,
            "interest_payment_frequency": "MONTHLY",
            "is_isa": False,
            "is_tfsa": False,
            "purpose": "EMERGENCY_FUND",
            "country": "UK"
        }

        response = await test_client.post(
            "/api/v1/savings/accounts",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["bank_name"] == "Barclays"
        assert data["account_name"] == "My Savings"
        assert data["account_type"] == "SAVINGS"
        assert Decimal(str(data["current_balance"])) == Decimal("10000.00")
        assert data["is_isa"] is False
        assert data["is_tfsa"] is False
        assert "****" in data["account_number"]  # Account number should be masked

    async def test_create_isa_account_records_contribution(
        self, test_client, authenticated_headers, db_session
    ):
        """Test creating an ISA account records contribution."""
        payload = {
            "bank_name": "HSBC",
            "account_name": "Cash ISA",
            "account_number": "87654321",
            "account_type": "ISA",
            "currency": "GBP",
            "current_balance": 5000.00,
            "interest_rate": 4.0,
            "interest_payment_frequency": "ANNUALLY",
            "is_isa": True,
            "is_tfsa": False,
            "purpose": "GENERAL",
            "country": "UK"
        }

        response = await test_client.post(
            "/api/v1/savings/accounts",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["is_isa"] is True

        # Verify ISA contribution was recorded
        from sqlalchemy import select
        stmt = select(ISAContribution).where(
            ISAContribution.savings_account_id == data["id"]
        )
        result = await db_session.execute(stmt)
        contribution = result.scalar_one_or_none()

        assert contribution is not None
        assert contribution.contribution_amount == Decimal("5000.00")

    async def test_create_tfsa_account_records_contribution(
        self, test_client, authenticated_headers, db_session
    ):
        """Test creating a TFSA account records contribution."""
        payload = {
            "bank_name": "Standard Bank",
            "account_name": "TFSA Savings",
            "account_number": "11112222",
            "account_type": "TFSA",
            "currency": "ZAR",
            "current_balance": 20000.00,
            "interest_rate": 6.0,
            "interest_payment_frequency": "MONTHLY",
            "is_isa": False,
            "is_tfsa": True,
            "purpose": "GENERAL",
            "country": "SA"
        }

        response = await test_client.post(
            "/api/v1/savings/accounts",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["is_tfsa"] is True

        # Verify TFSA contribution was recorded
        from sqlalchemy import select
        stmt = select(TFSAContribution).where(
            TFSAContribution.savings_account_id == data["id"]
        )
        result = await db_session.execute(stmt)
        contribution = result.scalar_one_or_none()

        assert contribution is not None
        assert contribution.contribution_amount == Decimal("20000.00")

    async def test_create_account_isa_tfsa_mutual_exclusivity(
        self, test_client, authenticated_headers
    ):
        """Test that ISA and TFSA cannot both be True."""
        payload = {
            "bank_name": "Test Bank",
            "account_name": "Invalid Account",
            "account_number": "12345678",
            "account_type": "SAVINGS",
            "currency": "GBP",
            "current_balance": 1000.00,
            "is_isa": True,
            "is_tfsa": True,  # Invalid: both True
            "country": "UK"
        }

        response = await test_client.post(
            "/api/v1/savings/accounts",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Validation error

    async def test_create_account_without_authentication(self, test_client):
        """Test creating account without authentication fails."""
        payload = {
            "bank_name": "Test Bank",
            "account_name": "Test Account",
            "account_number": "12345678",
            "account_type": "SAVINGS",
            "currency": "GBP",
            "current_balance": 1000.00,
            "country": "UK"
        }

        response = await test_client.post(
            "/api/v1/savings/accounts",
            json=payload
        )

        assert response.status_code == 401


@pytest.mark.asyncio
class TestGetSavingsAccounts:
    """Tests for GET /api/v1/savings/accounts"""

    async def test_get_all_accounts_empty(self, test_client, authenticated_headers):
        """Test getting accounts when none exist."""
        response = await test_client.get(
            "/api/v1/savings/accounts",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_get_all_accounts_multiple(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test getting multiple accounts."""
        # Create test accounts
        accounts = [
            SavingsAccount(
                user_id=test_user.id,
                bank_name="Bank A",
                account_name="Account 1",
                account_number_encrypted="encrypted1",
                account_type=AccountType.SAVINGS,
                currency=Currency.GBP,
                current_balance=Decimal("10000"),
                country=AccountCountry.UK,
                purpose=AccountPurpose.EMERGENCY_FUND
            ),
            SavingsAccount(
                user_id=test_user.id,
                bank_name="Bank B",
                account_name="Account 2",
                account_number_encrypted="encrypted2",
                account_type=AccountType.ISA,
                currency=Currency.GBP,
                current_balance=Decimal("5000"),
                country=AccountCountry.UK,
                is_isa=True
            ),
        ]

        for account in accounts:
            db_session.add(account)
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/savings/accounts",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_accounts_filter_by_type(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test filtering accounts by type."""
        # Create mixed accounts
        accounts = [
            SavingsAccount(
                user_id=test_user.id,
                bank_name="Bank A",
                account_name="Savings",
                account_number_encrypted="encrypted1",
                account_type=AccountType.SAVINGS,
                currency=Currency.GBP,
                current_balance=Decimal("10000"),
                country=AccountCountry.UK
            ),
            SavingsAccount(
                user_id=test_user.id,
                bank_name="Bank B",
                account_name="ISA",
                account_number_encrypted="encrypted2",
                account_type=AccountType.ISA,
                currency=Currency.GBP,
                current_balance=Decimal("5000"),
                country=AccountCountry.UK,
                is_isa=True
            ),
        ]

        for account in accounts:
            db_session.add(account)
        await db_session.commit()

        # Filter by ISA
        response = await test_client.get(
            "/api/v1/savings/accounts?account_type=ISA",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["account_type"] == "ISA"

    async def test_get_accounts_filter_by_currency(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test filtering accounts by currency."""
        # Create accounts in different currencies
        accounts = [
            SavingsAccount(
                user_id=test_user.id,
                bank_name="UK Bank",
                account_name="GBP Account",
                account_number_encrypted="encrypted1",
                account_type=AccountType.SAVINGS,
                currency=Currency.GBP,
                current_balance=Decimal("10000"),
                country=AccountCountry.UK
            ),
            SavingsAccount(
                user_id=test_user.id,
                bank_name="SA Bank",
                account_name="ZAR Account",
                account_number_encrypted="encrypted2",
                account_type=AccountType.SAVINGS,
                currency=Currency.ZAR,
                current_balance=Decimal("200000"),
                country=AccountCountry.SA
            ),
        ]

        for account in accounts:
            db_session.add(account)
        await db_session.commit()

        # Filter by ZAR
        response = await test_client.get(
            "/api/v1/savings/accounts?currency=ZAR",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["currency"] == "ZAR"


@pytest.mark.asyncio
class TestGetSingleAccount:
    """Tests for GET /api/v1/savings/accounts/{account_id}"""

    async def test_get_account_success(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test getting a single account by ID."""
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted="encrypted",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("10000"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        response = await test_client.get(
            f"/api/v1/savings/accounts/{account.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(account.id)
        assert data["account_name"] == "Test Account"

    async def test_get_account_not_found(self, test_client, authenticated_headers):
        """Test getting a non-existent account returns 404."""
        fake_id = uuid4()
        response = await test_client.get(
            f"/api/v1/savings/accounts/{fake_id}",
            headers=authenticated_headers
        )

        assert response.status_code == 404

    async def test_get_account_forbidden_other_user(
        self, test_client, authenticated_headers, db_session
    ):
        """Test that users cannot access other users' accounts."""
        # Create account for different user
        other_user_id = uuid4()
        account = SavingsAccount(
            user_id=other_user_id,
            bank_name="Other Bank",
            account_name="Other Account",
            account_number_encrypted="encrypted",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("10000"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        response = await test_client.get(
            f"/api/v1/savings/accounts/{account.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 404  # Returns 404 to prevent info leakage


@pytest.mark.asyncio
class TestUpdateAccount:
    """Tests for PATCH /api/v1/savings/accounts/{account_id}"""

    async def test_update_account_name(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test updating account name."""
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Old Name",
            account_number_encrypted="encrypted",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("10000"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        response = await test_client.patch(
            f"/api/v1/savings/accounts/{account.id}",
            json={"account_name": "New Name"},
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["account_name"] == "New Name"

    async def test_update_account_balance(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test updating account balance."""
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted="encrypted",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("10000"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        response = await test_client.patch(
            f"/api/v1/savings/accounts/{account.id}",
            json={"current_balance": 15000.00},
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert Decimal(str(data["current_balance"])) == Decimal("15000.00")


@pytest.mark.asyncio
class TestDeleteAccount:
    """Tests for DELETE /api/v1/savings/accounts/{account_id}"""

    async def test_delete_account_success(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test soft deleting an account."""
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted="encrypted",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("10000"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        response = await test_client.delete(
            f"/api/v1/savings/accounts/{account.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Account deleted successfully"
        assert data["account_id"] == str(account.id)

        # Verify account is soft-deleted
        await db_session.refresh(account)
        assert account.deleted_at is not None
        assert account.is_active is False


@pytest.mark.asyncio
class TestBalanceUpdate:
    """Tests for POST /api/v1/savings/accounts/{account_id}/balance"""

    async def test_update_balance_success(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test updating account balance."""
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted="encrypted",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("10000"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        response = await test_client.post(
            f"/api/v1/savings/accounts/{account.id}/balance",
            json={
                "balance": 12000.00,
                "balance_date": date.today().isoformat(),
                "notes": "Monthly deposit"
            },
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert Decimal(str(data["current_balance"])) == Decimal("12000.00")
        assert Decimal(str(data["previous_balance"])) == Decimal("10000.00")
        assert Decimal(str(data["change"])) == Decimal("2000.00")

    async def test_update_balance_creates_history(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test that balance update creates history entry."""
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted="encrypted",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("10000"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        await test_client.post(
            f"/api/v1/savings/accounts/{account.id}/balance",
            json={
                "balance": 12000.00,
                "balance_date": date.today().isoformat(),
                "notes": "Test update"
            },
            headers=authenticated_headers
        )

        # Check history was created
        from sqlalchemy import select
        stmt = select(AccountBalanceHistory).where(
            AccountBalanceHistory.savings_account_id == account.id
        )
        result = await db_session.execute(stmt)
        history = result.scalars().all()

        # Should have initial balance + this update
        assert len(history) >= 1


@pytest.mark.asyncio
class TestBalanceHistory:
    """Tests for GET /api/v1/savings/accounts/{account_id}/balance-history"""

    async def test_get_balance_history(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test retrieving balance history."""
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted="encrypted",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("10000"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.flush()

        # Create history entries
        history_entries = [
            AccountBalanceHistory(
                savings_account_id=account.id,
                balance=Decimal("10000"),
                balance_date=date.today() - timedelta(days=2),
                notes="Day 1"
            ),
            AccountBalanceHistory(
                savings_account_id=account.id,
                balance=Decimal("11000"),
                balance_date=date.today() - timedelta(days=1),
                notes="Day 2"
            ),
        ]

        for entry in history_entries:
            db_session.add(entry)
        await db_session.commit()
        await db_session.refresh(account)

        response = await test_client.get(
            f"/api/v1/savings/accounts/{account.id}/balance-history",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


@pytest.mark.asyncio
class TestSavingsSummary:
    """Tests for GET /api/v1/savings/summary"""

    async def test_get_summary_empty(self, test_client, authenticated_headers):
        """Test summary with no accounts."""
        response = await test_client.get(
            "/api/v1/savings/summary",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_accounts"] == 0
        assert Decimal(str(data["total_balance_gbp"])) == Decimal("0")

    async def test_get_summary_multiple_accounts(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test summary with multiple accounts."""
        accounts = [
            SavingsAccount(
                user_id=test_user.id,
                bank_name="Bank A",
                account_name="Account 1",
                account_number_encrypted="encrypted1",
                account_type=AccountType.SAVINGS,
                currency=Currency.GBP,
                current_balance=Decimal("10000"),
                country=AccountCountry.UK,
                purpose=AccountPurpose.EMERGENCY_FUND
            ),
            SavingsAccount(
                user_id=test_user.id,
                bank_name="Bank B",
                account_name="Account 2",
                account_number_encrypted="encrypted2",
                account_type=AccountType.ISA,
                currency=Currency.GBP,
                current_balance=Decimal("5000"),
                country=AccountCountry.UK,
                is_isa=True
            ),
        ]

        for account in accounts:
            db_session.add(account)
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/savings/summary",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_accounts"] == 2
        assert Decimal(str(data["total_balance_gbp"])) == Decimal("15000")
        assert data["isa_accounts"] == 1
