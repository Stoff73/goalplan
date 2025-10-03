"""
Tests for savings account models.

This module tests:
- SavingsAccount model creation and validation
- AccountBalanceHistory tracking
- Account number encryption/decryption
- ISA/TFSA mutual exclusivity
- Multi-currency support
- Soft delete functionality
- Database constraints and indexes
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from models.savings_account import (
    SavingsAccount,
    AccountBalanceHistory,
    AccountType,
    AccountPurpose,
    AccountCountry,
    InterestFrequency,
    Currency
)
from utils.encryption import encrypt_account_number, decrypt_account_number


class TestSavingsAccountModel:
    """Test SavingsAccount model."""

    @pytest.mark.asyncio
    async def test_create_savings_account(self, db_session, test_user):
        """Test creating a savings account."""
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Barclays",
            account_name="Emergency Fund",
            account_number_encrypted=encrypt_account_number("12345678"),
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("10000.00"),
            interest_rate=Decimal("4.5"),
            interest_payment_frequency=InterestFrequency.MONTHLY,
            is_isa=False,
            is_tfsa=False,
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        assert account.id is not None
        assert account.user_id == test_user.id
        assert account.bank_name == "Barclays"
        assert account.account_name == "Emergency Fund"
        assert account.account_type == AccountType.SAVINGS
        assert account.currency == Currency.GBP
        assert account.current_balance == Decimal("10000.00")
        assert account.interest_rate == Decimal("4.5")
        assert account.is_isa is False
        assert account.is_tfsa is False
        assert account.is_active is True

    @pytest.mark.asyncio
    async def test_account_number_encryption(self, db_session, test_user):
        """Test account number encryption/decryption."""
        account_number = "GB29NWBK60161331926819"

        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted=encrypt_account_number(account_number),
            account_type=AccountType.CURRENT,
            currency=Currency.GBP,
            current_balance=Decimal("5000.00"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        # Test decryption
        decrypted = decrypt_account_number(account.account_number_encrypted)
        assert decrypted == account_number

        # Test helper methods
        account.set_account_number("NEW12345678")
        assert account.get_account_number() == "NEW12345678"

    @pytest.mark.asyncio
    async def test_isa_account_creation(self, db_session, test_user):
        """Test creating an ISA account."""
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Nationwide",
            account_name="Cash ISA",
            account_number_encrypted=encrypt_account_number("ISA123456"),
            account_type=AccountType.ISA,
            currency=Currency.GBP,
            current_balance=Decimal("15000.00"),
            interest_rate=Decimal("5.0"),
            is_isa=True,
            is_tfsa=False,
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        assert account.is_isa is True
        assert account.is_tfsa is False
        assert account.country == AccountCountry.UK

    @pytest.mark.asyncio
    async def test_tfsa_account_creation(self, db_session, test_user):
        """Test creating a TFSA account."""
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="FNB",
            account_name="Tax Free Savings",
            account_number_encrypted=encrypt_account_number("TFSA123456"),
            account_type=AccountType.TFSA,
            currency=Currency.ZAR,
            current_balance=Decimal("100000.00"),
            interest_rate=Decimal("6.0"),
            is_isa=False,
            is_tfsa=True,
            country=AccountCountry.SA
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        assert account.is_isa is False
        assert account.is_tfsa is True
        assert account.country == AccountCountry.SA

    @pytest.mark.asyncio
    async def test_isa_tfsa_mutual_exclusivity_db_constraint(self, db_session, test_user):
        """Test ISA/TFSA mutual exclusivity at model validator level."""
        # The model validator should catch this before it hits the database
        with pytest.raises(ValueError, match="Account cannot be both ISA and TFSA"):
            account = SavingsAccount(
                user_id=test_user.id,
                bank_name="Test Bank",
                account_name="Invalid Account",
                account_number_encrypted=encrypt_account_number("12345678"),
                account_type=AccountType.SAVINGS,
                currency=Currency.GBP,
                current_balance=Decimal("5000.00"),
                is_isa=True,
                is_tfsa=True,  # Both True should fail
                country=AccountCountry.UK
            )

    @pytest.mark.asyncio
    async def test_isa_tfsa_mutual_exclusivity_validator(self):
        """Test ISA/TFSA mutual exclusivity at model level."""
        account = SavingsAccount(
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted=encrypt_account_number("12345678"),
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("5000.00"),
            country=AccountCountry.UK
        )

        # Set is_isa first
        account.is_isa = True

        # Try to set is_tfsa - should raise ValueError
        with pytest.raises(ValueError, match="Account cannot be both ISA and TFSA"):
            account.is_tfsa = True

    @pytest.mark.asyncio
    async def test_negative_balance_constraint(self, db_session, test_user):
        """Test negative balance is rejected."""
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted=encrypt_account_number("12345678"),
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("-100.00"),  # Negative balance
            country=AccountCountry.UK
        )

        db_session.add(account)

        with pytest.raises(IntegrityError):
            await db_session.commit()

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_negative_interest_rate_constraint(self, db_session, test_user):
        """Test negative interest rate is rejected."""
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted=encrypt_account_number("12345678"),
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("1000.00"),
            interest_rate=Decimal("-1.0"),  # Negative interest
            country=AccountCountry.UK
        )

        db_session.add(account)

        with pytest.raises(IntegrityError):
            await db_session.commit()

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_multi_currency_support(self, db_session, test_user):
        """Test multiple currency accounts."""
        currencies = [
            (Currency.GBP, Decimal("10000.00")),
            (Currency.ZAR, Decimal("200000.00")),
            (Currency.USD, Decimal("15000.00")),
            (Currency.EUR, Decimal("12000.00"))
        ]

        for currency, balance in currencies:
            account = SavingsAccount(
                user_id=test_user.id,
                bank_name=f"Bank {currency.value}",
                account_name=f"{currency.value} Account",
                account_number_encrypted=encrypt_account_number(f"{currency.value}123456"),
                account_type=AccountType.SAVINGS,
                currency=currency,
                current_balance=balance,
                country=AccountCountry.UK
            )
            db_session.add(account)

        await db_session.commit()

        # Verify all accounts created
        result = await db_session.execute(
            select(SavingsAccount).where(SavingsAccount.user_id == test_user.id)
        )
        accounts = result.scalars().all()

        assert len(accounts) == 4
        assert set(acc.currency for acc in accounts) == {Currency.GBP, Currency.ZAR, Currency.USD, Currency.EUR}

    @pytest.mark.asyncio
    async def test_soft_delete(self, db_session, test_user):
        """Test soft delete functionality."""
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted=encrypt_account_number("12345678"),
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("5000.00"),
            country=AccountCountry.UK,
            is_active=True
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        # Soft delete
        account.is_active = False
        account.deleted_at = datetime.utcnow()
        await db_session.commit()

        # Verify account still exists but marked deleted
        result = await db_session.execute(
            select(SavingsAccount).where(SavingsAccount.id == account.id)
        )
        deleted_account = result.scalar_one()

        assert deleted_account.is_active is False
        assert deleted_account.deleted_at is not None

    @pytest.mark.asyncio
    async def test_user_relationship(self, db_session, test_user):
        """Test relationship with User model."""
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted=encrypt_account_number("12345678"),
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("5000.00"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        # Test relationship
        assert account.user.id == test_user.id
        assert account.user.email == test_user.email


class TestAccountBalanceHistory:
    """Test AccountBalanceHistory model."""

    @pytest.mark.asyncio
    async def test_create_balance_history(self, db_session, test_user):
        """Test creating a balance history record."""
        # Create account first
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted=encrypt_account_number("12345678"),
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("5000.00"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        # Create balance history
        history = AccountBalanceHistory(
            savings_account_id=account.id,
            balance=Decimal("5500.00"),
            balance_date=date.today(),
            notes="Monthly interest payment"
        )

        db_session.add(history)
        await db_session.commit()
        await db_session.refresh(history)

        assert history.id is not None
        assert history.savings_account_id == account.id
        assert history.balance == Decimal("5500.00")
        assert history.balance_date == date.today()
        assert history.notes == "Monthly interest payment"

    @pytest.mark.asyncio
    async def test_unique_balance_per_day_constraint(self, db_session, test_user):
        """Test unique constraint for one balance per account per day."""
        # Create account
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted=encrypt_account_number("12345678"),
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("5000.00"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        # Create first balance history
        history1 = AccountBalanceHistory(
            savings_account_id=account.id,
            balance=Decimal("5000.00"),
            balance_date=date.today()
        )

        db_session.add(history1)
        await db_session.commit()

        # Try to create second balance for same day - should fail
        history2 = AccountBalanceHistory(
            savings_account_id=account.id,
            balance=Decimal("5100.00"),
            balance_date=date.today()
        )

        db_session.add(history2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_balance_history_tracking(self, db_session, test_user):
        """Test tracking balance over time."""
        # Create account
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted=encrypt_account_number("12345678"),
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("5000.00"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        # Create history for 5 days
        for i in range(5):
            history = AccountBalanceHistory(
                savings_account_id=account.id,
                balance=Decimal(f"{5000 + (i * 100)}.00"),
                balance_date=date.today() - timedelta(days=i)
            )
            db_session.add(history)

        await db_session.commit()

        # Query history
        result = await db_session.execute(
            select(AccountBalanceHistory)
            .where(AccountBalanceHistory.savings_account_id == account.id)
            .order_by(AccountBalanceHistory.balance_date.desc())
        )
        history_records = result.scalars().all()

        assert len(history_records) == 5
        # Verify descending order
        assert history_records[0].balance_date == date.today()
        assert history_records[4].balance_date == date.today() - timedelta(days=4)

    @pytest.mark.asyncio
    async def test_negative_balance_history_constraint(self, db_session, test_user):
        """Test negative balance in history is rejected."""
        # Create account
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted=encrypt_account_number("12345678"),
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("5000.00"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        # Try to create history with negative balance
        history = AccountBalanceHistory(
            savings_account_id=account.id,
            balance=Decimal("-100.00"),  # Negative balance
            balance_date=date.today()
        )

        db_session.add(history)

        with pytest.raises(IntegrityError):
            await db_session.commit()

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_cascade_delete(self, db_session, test_user):
        """Test cascade delete removes balance history."""
        # Create account with history
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted=encrypt_account_number("12345678"),
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("5000.00"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        # Create history
        history = AccountBalanceHistory(
            savings_account_id=account.id,
            balance=Decimal("5500.00"),
            balance_date=date.today()
        )

        db_session.add(history)
        await db_session.commit()

        account_id = account.id

        # Delete account
        await db_session.delete(account)
        await db_session.commit()

        # Verify history is also deleted
        result = await db_session.execute(
            select(AccountBalanceHistory).where(
                AccountBalanceHistory.savings_account_id == account_id
            )
        )
        history_records = result.scalars().all()

        assert len(history_records) == 0

    @pytest.mark.asyncio
    async def test_balance_history_relationship(self, db_session, test_user):
        """Test relationship between account and balance history."""
        # Create account
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Test Account",
            account_number_encrypted=encrypt_account_number("12345678"),
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("5000.00"),
            country=AccountCountry.UK
        )

        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        # Create history via relationship
        history = AccountBalanceHistory(
            savings_account_id=account.id,
            balance=Decimal("5500.00"),
            balance_date=date.today()
        )

        db_session.add(history)
        await db_session.commit()
        await db_session.refresh(account)

        # Test relationship
        assert len(account.balance_history) == 1
        assert account.balance_history[0].balance == Decimal("5500.00")
        assert account.balance_history[0].savings_account.id == account.id
