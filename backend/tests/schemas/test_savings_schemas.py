"""
Tests for savings account Pydantic schemas.

This module tests:
- Schema validation
- ISA/TFSA mutual exclusivity
- Country validation
- Field constraints
- Serialization
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4
from pydantic import ValidationError

from schemas.savings import (
    SavingsAccountCreate,
    SavingsAccountUpdate,
    SavingsAccountResponse,
    BalanceHistoryCreate,
    BalanceHistoryResponse,
    SavingsAccountSummary,
    SavingsTotalSummary
)
from models.savings_account import (
    AccountType,
    AccountPurpose,
    AccountCountry,
    InterestFrequency,
    Currency
)


class TestSavingsAccountCreate:
    """Test SavingsAccountCreate schema."""

    def test_valid_savings_account_create(self):
        """Test creating valid savings account schema."""
        data = {
            "bank_name": "Barclays",
            "account_name": "Emergency Fund",
            "account_number": "12345678",
            "account_type": AccountType.SAVINGS,
            "currency": Currency.GBP,
            "current_balance": Decimal("10000.00"),
            "interest_rate": Decimal("4.5"),
            "interest_payment_frequency": InterestFrequency.MONTHLY,
            "is_isa": False,
            "is_tfsa": False,
            "purpose": AccountPurpose.EMERGENCY_FUND,
            "country": AccountCountry.UK
        }

        schema = SavingsAccountCreate(**data)

        assert schema.bank_name == "Barclays"
        assert schema.account_name == "Emergency Fund"
        assert schema.account_type == AccountType.SAVINGS
        assert schema.current_balance == Decimal("10000.00")
        assert schema.interest_rate == Decimal("4.5")

    def test_isa_tfsa_mutual_exclusivity(self):
        """Test ISA and TFSA cannot both be true."""
        data = {
            "bank_name": "Test Bank",
            "account_name": "Invalid Account",
            "account_number": "12345678",
            "account_type": AccountType.SAVINGS,
            "currency": Currency.GBP,
            "current_balance": Decimal("5000.00"),
            "is_isa": True,
            "is_tfsa": True,  # Both true - should fail
            "country": AccountCountry.UK
        }

        with pytest.raises(ValidationError, match="Account cannot be both ISA and TFSA"):
            SavingsAccountCreate(**data)

    def test_isa_must_be_uk(self):
        """Test ISA accounts can only be in UK."""
        data = {
            "bank_name": "Test Bank",
            "account_name": "ISA Account",
            "account_number": "12345678",
            "account_type": AccountType.ISA,
            "currency": Currency.GBP,
            "current_balance": Decimal("5000.00"),
            "is_isa": True,
            "is_tfsa": False,
            "country": AccountCountry.SA  # ISA in SA - should fail
        }

        with pytest.raises(ValidationError, match="ISA accounts can only be held in the UK"):
            SavingsAccountCreate(**data)

    def test_tfsa_must_be_sa(self):
        """Test TFSA accounts can only be in SA."""
        data = {
            "bank_name": "Test Bank",
            "account_name": "TFSA Account",
            "account_number": "12345678",
            "account_type": AccountType.TFSA,
            "currency": Currency.ZAR,
            "current_balance": Decimal("50000.00"),
            "is_isa": False,
            "is_tfsa": True,
            "country": AccountCountry.UK  # TFSA in UK - should fail
        }

        with pytest.raises(ValidationError, match="TFSA accounts can only be held in South Africa"):
            SavingsAccountCreate(**data)

    def test_negative_balance_rejected(self):
        """Test negative balance is rejected."""
        data = {
            "bank_name": "Test Bank",
            "account_name": "Test Account",
            "account_number": "12345678",
            "account_type": AccountType.SAVINGS,
            "currency": Currency.GBP,
            "current_balance": Decimal("-100.00"),  # Negative
            "country": AccountCountry.UK
        }

        with pytest.raises(ValidationError):
            SavingsAccountCreate(**data)

    def test_negative_interest_rate_rejected(self):
        """Test negative interest rate is rejected."""
        data = {
            "bank_name": "Test Bank",
            "account_name": "Test Account",
            "account_number": "12345678",
            "account_type": AccountType.SAVINGS,
            "currency": Currency.GBP,
            "current_balance": Decimal("5000.00"),
            "interest_rate": Decimal("-1.0"),  # Negative
            "country": AccountCountry.UK
        }

        with pytest.raises(ValidationError):
            SavingsAccountCreate(**data)

    def test_interest_rate_max_100_percent(self):
        """Test interest rate cannot exceed 100%."""
        data = {
            "bank_name": "Test Bank",
            "account_name": "Test Account",
            "account_number": "12345678",
            "account_type": AccountType.SAVINGS,
            "currency": Currency.GBP,
            "current_balance": Decimal("5000.00"),
            "interest_rate": Decimal("150.0"),  # Over 100%
            "country": AccountCountry.UK
        }

        with pytest.raises(ValidationError):
            SavingsAccountCreate(**data)

    def test_account_number_min_length(self):
        """Test account number minimum length."""
        data = {
            "bank_name": "Test Bank",
            "account_name": "Test Account",
            "account_number": "123",  # Too short (min 4)
            "account_type": AccountType.SAVINGS,
            "currency": Currency.GBP,
            "current_balance": Decimal("5000.00"),
            "country": AccountCountry.UK
        }

        with pytest.raises(ValidationError):
            SavingsAccountCreate(**data)

    def test_optional_fields(self):
        """Test schema with only required fields."""
        data = {
            "bank_name": "Test Bank",
            "account_name": "Test Account",
            "account_number": "12345678",
            "account_type": AccountType.CURRENT,
            "currency": Currency.GBP,
            "current_balance": Decimal("5000.00"),
            "country": AccountCountry.UK
        }

        schema = SavingsAccountCreate(**data)

        assert schema.interest_rate is None
        assert schema.interest_payment_frequency is None
        assert schema.purpose is None
        assert schema.is_isa is False
        assert schema.is_tfsa is False


class TestSavingsAccountUpdate:
    """Test SavingsAccountUpdate schema."""

    def test_all_fields_optional(self):
        """Test that all fields are optional in update schema."""
        data = {}

        schema = SavingsAccountUpdate(**data)

        assert schema.bank_name is None
        assert schema.account_name is None
        assert schema.current_balance is None

    def test_partial_update(self):
        """Test partial update with some fields."""
        data = {
            "account_name": "Updated Name",
            "current_balance": Decimal("15000.00")
        }

        schema = SavingsAccountUpdate(**data)

        assert schema.account_name == "Updated Name"
        assert schema.current_balance == Decimal("15000.00")
        assert schema.bank_name is None


class TestBalanceHistoryCreate:
    """Test BalanceHistoryCreate schema."""

    def test_valid_balance_history_create(self):
        """Test creating valid balance history schema."""
        data = {
            "balance": Decimal("10500.00"),
            "balance_date": date.today(),
            "notes": "Monthly interest payment"
        }

        schema = BalanceHistoryCreate(**data)

        assert schema.balance == Decimal("10500.00")
        assert schema.balance_date == date.today()
        assert schema.notes == "Monthly interest payment"

    def test_future_date_rejected(self):
        """Test that future balance date is rejected."""
        from datetime import timedelta

        data = {
            "balance": Decimal("10500.00"),
            "balance_date": date.today() + timedelta(days=1),  # Future date
        }

        with pytest.raises(ValidationError, match="Balance date cannot be in the future"):
            BalanceHistoryCreate(**data)

    def test_negative_balance_rejected(self):
        """Test negative balance is rejected."""
        data = {
            "balance": Decimal("-100.00"),  # Negative
            "balance_date": date.today()
        }

        with pytest.raises(ValidationError):
            BalanceHistoryCreate(**data)

    def test_optional_notes(self):
        """Test notes field is optional."""
        data = {
            "balance": Decimal("10500.00"),
            "balance_date": date.today()
        }

        schema = BalanceHistoryCreate(**data)

        assert schema.notes is None


class TestBalanceHistoryResponse:
    """Test BalanceHistoryResponse schema."""

    def test_valid_balance_history_response(self):
        """Test creating valid balance history response schema."""
        data = {
            "id": uuid4(),
            "savings_account_id": uuid4(),
            "balance": Decimal("10500.00"),
            "balance_date": date.today(),
            "notes": "Monthly interest payment",
            "created_at": datetime.utcnow()
        }

        schema = BalanceHistoryResponse(**data)

        assert schema.balance == Decimal("10500.00")
        assert schema.notes == "Monthly interest payment"


class TestSavingsAccountResponse:
    """Test SavingsAccountResponse schema."""

    def test_valid_savings_account_response(self):
        """Test creating valid savings account response schema."""
        data = {
            "id": uuid4(),
            "user_id": uuid4(),
            "bank_name": "Barclays",
            "account_name": "Emergency Fund",
            "account_number": "****5678",
            "account_type": AccountType.SAVINGS,
            "currency": Currency.GBP,
            "current_balance": Decimal("10000.00"),
            "interest_rate": Decimal("4.5"),
            "interest_payment_frequency": InterestFrequency.MONTHLY,
            "is_isa": False,
            "is_tfsa": False,
            "purpose": AccountPurpose.EMERGENCY_FUND,
            "country": AccountCountry.UK,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "deleted_at": None
        }

        schema = SavingsAccountResponse(**data)

        assert schema.bank_name == "Barclays"
        assert schema.account_type == AccountType.SAVINGS
        assert schema.current_balance == Decimal("10000.00")


class TestSavingsAccountSummary:
    """Test SavingsAccountSummary schema."""

    def test_valid_savings_account_summary(self):
        """Test creating valid savings account summary schema."""
        data = {
            "id": uuid4(),
            "account_name": "Emergency Fund",
            "bank_name": "Barclays",
            "account_type": AccountType.SAVINGS,
            "currency": Currency.GBP,
            "current_balance": Decimal("10000.00"),
            "purpose": AccountPurpose.EMERGENCY_FUND,
            "is_isa": False,
            "is_tfsa": False,
            "country": AccountCountry.UK
        }

        schema = SavingsAccountSummary(**data)

        assert schema.account_name == "Emergency Fund"
        assert schema.current_balance == Decimal("10000.00")


class TestSavingsTotalSummary:
    """Test SavingsTotalSummary schema."""

    def test_valid_savings_total_summary(self):
        """Test creating valid savings total summary schema."""
        data = {
            "total_accounts": 5,
            "total_balance_gbp": Decimal("45000.00"),
            "total_balance_zar": Decimal("250000.00"),
            "total_balance_usd": Decimal("10000.00"),
            "total_balance_eur": Decimal("5000.00"),
            "isa_accounts": 2,
            "tfsa_accounts": 1,
            "emergency_fund_total": Decimal("30000.00"),
            "savings_goal_total": Decimal("15000.00")
        }

        schema = SavingsTotalSummary(**data)

        assert schema.total_accounts == 5
        assert schema.total_balance_gbp == Decimal("45000.00")
        assert schema.isa_accounts == 2
        assert schema.tfsa_accounts == 1
