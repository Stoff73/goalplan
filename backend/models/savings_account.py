"""
Savings account models for multi-currency cash management.

This module provides SQLAlchemy models for:
- Savings accounts with encrypted account numbers
- Balance history tracking
- ISA/TFSA support with allowance tracking
- Multi-currency support

Business logic:
- Account number encryption for security
- Balance history for temporal tracking
- ISA and TFSA mutual exclusivity
- Soft delete for audit trail
- Multi-currency with conversion support
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
import enum

from sqlalchemy import (
    Column, String, ForeignKey, Numeric, Boolean, DateTime,
    Date, Text, CheckConstraint, UniqueConstraint, Index,
    Enum as SQLEnum, func
)
from sqlalchemy.orm import relationship, validates

from database import Base
from models.user import GUID
from utils.encryption import encrypt_account_number, decrypt_account_number


class AccountType(str, enum.Enum):
    """Account type enumeration."""
    CURRENT = 'CURRENT'
    SAVINGS = 'SAVINGS'
    ISA = 'ISA'
    TFSA = 'TFSA'
    FIXED_DEPOSIT = 'FIXED_DEPOSIT'
    MONEY_MARKET = 'MONEY_MARKET'
    NOTICE_ACCOUNT = 'NOTICE_ACCOUNT'
    OTHER = 'OTHER'


class AccountPurpose(str, enum.Enum):
    """Account purpose enumeration."""
    EMERGENCY_FUND = 'EMERGENCY_FUND'
    SAVINGS_GOAL = 'SAVINGS_GOAL'
    GENERAL = 'GENERAL'
    OTHER = 'OTHER'


class AccountCountry(str, enum.Enum):
    """Account country enumeration."""
    UK = 'UK'
    SA = 'SA'
    OFFSHORE = 'OFFSHORE'


class InterestFrequency(str, enum.Enum):
    """Interest payment frequency enumeration."""
    MONTHLY = 'MONTHLY'
    QUARTERLY = 'QUARTERLY'
    ANNUALLY = 'ANNUALLY'
    MATURITY = 'MATURITY'


class Currency(str, enum.Enum):
    """Supported currency codes."""
    GBP = 'GBP'
    ZAR = 'ZAR'
    USD = 'USD'
    EUR = 'EUR'


class TFSAContributionType(str, enum.Enum):
    """TFSA contribution type enumeration."""
    DEPOSIT = 'DEPOSIT'  # Cash contribution
    GROWTH = 'GROWTH'    # Investment growth (also counts toward annual limit)


class SavingsAccount(Base):
    """
    Savings account tracking with encrypted account numbers.

    Tracks savings accounts across multiple countries with:
    - Encrypted account numbers for security
    - Multi-currency support
    - ISA/TFSA tracking (mutually exclusive)
    - Balance history tracking
    - Interest rate tracking
    - Soft delete for audit trail
    """

    __tablename__ = 'savings_accounts'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Account Details
    bank_name = Column(String(255), nullable=False)
    account_name = Column(String(255), nullable=False)  # User-defined name
    account_number_encrypted = Column(Text, nullable=False)  # Encrypted account number

    account_type = Column(
        SQLEnum(AccountType, name='savings_account_type_enum', create_type=False),
        nullable=False,
        index=True
    )

    currency = Column(
        SQLEnum(Currency, name='currency_enum', create_type=False),
        nullable=False
    )

    # Balance Information
    current_balance = Column(
        Numeric(15, 2),
        nullable=False,
        default=0.00
    )

    # Interest Details
    interest_rate = Column(
        Numeric(5, 2),
        nullable=True,
        default=0.00
    )  # Annual percentage

    interest_payment_frequency = Column(
        SQLEnum(InterestFrequency, name='savings_interest_frequency_enum', create_type=False),
        nullable=True
    )

    # Tax-Advantaged Account Flags (mutually exclusive)
    is_isa = Column(Boolean, default=False, nullable=False, index=True)
    is_tfsa = Column(Boolean, default=False, nullable=False, index=True)

    # Account Purpose and Location
    purpose = Column(
        SQLEnum(AccountPurpose, name='savings_account_purpose_enum', create_type=False),
        nullable=True
    )

    country = Column(
        SQLEnum(AccountCountry, name='savings_account_country_enum', create_type=False),
        nullable=False
    )

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # Relationships
    user = relationship("User", back_populates="savings_accounts")
    balance_history = relationship(
        "AccountBalanceHistory",
        back_populates="savings_account",
        cascade="all, delete-orphan",
        order_by="desc(AccountBalanceHistory.balance_date)"
    )

    # Table Constraints
    __table_args__ = (
        CheckConstraint('current_balance >= 0', name='check_positive_balance'),
        CheckConstraint('interest_rate >= 0', name='check_positive_interest_rate'),
        CheckConstraint(
            'NOT (is_isa = true AND is_tfsa = true)',
            name='check_isa_tfsa_mutually_exclusive'
        ),
        Index('idx_savings_user_active', 'user_id', 'is_active'),
        Index('idx_savings_user_deleted', 'user_id', 'deleted_at'),
    )

    @validates('is_isa', 'is_tfsa')
    def validate_isa_tfsa_mutual_exclusivity(self, key, value):
        """Ensure ISA and TFSA are mutually exclusive."""
        if key == 'is_isa' and value is True and self.is_tfsa is True:
            raise ValueError("Account cannot be both ISA and TFSA")
        if key == 'is_tfsa' and value is True and self.is_isa is True:
            raise ValueError("Account cannot be both ISA and TFSA")
        return value

    def set_account_number(self, account_number: str) -> None:
        """
        Encrypt and set account number.

        Args:
            account_number: Plain text account number
        """
        self.account_number_encrypted = encrypt_account_number(account_number)

    def get_account_number(self) -> str:
        """
        Decrypt and return account number.

        Returns:
            str: Decrypted account number
        """
        return decrypt_account_number(self.account_number_encrypted)

    def __repr__(self) -> str:
        return (
            f"<SavingsAccount(id={self.id}, user_id={self.user_id}, "
            f"bank={self.bank_name}, type={self.account_type}, "
            f"balance={self.current_balance} {self.currency})>"
        )


class AccountBalanceHistory(Base):
    """
    Historical balance tracking for savings accounts.

    Tracks balance changes over time with:
    - Point-in-time balance records
    - Optional notes for context
    - Unique constraint per account per day
    - Maximum 10 updates per day per account
    """

    __tablename__ = 'account_balance_history'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)

    savings_account_id = Column(
        GUID,
        ForeignKey('savings_accounts.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Balance Information
    balance = Column(Numeric(15, 2), nullable=False)
    balance_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    savings_account = relationship(
        "SavingsAccount",
        back_populates="balance_history"
    )

    # Table Constraints
    __table_args__ = (
        CheckConstraint('balance >= 0', name='check_positive_balance_history'),
        UniqueConstraint(
            'savings_account_id',
            'balance_date',
            name='unique_balance_per_account_per_day'
        ),
        Index(
            'idx_balance_history_account_date',
            'savings_account_id',
            'balance_date',
            postgresql_using='btree',
            postgresql_ops={'balance_date': 'DESC'}
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<AccountBalanceHistory(id={self.id}, "
            f"account_id={self.savings_account_id}, "
            f"balance={self.balance}, date={self.balance_date})>"
        )


# Update User model relationship (this will be added via migration)
# User.savings_accounts = relationship("SavingsAccount", back_populates="user", cascade="all, delete-orphan")


class ISAContribution(Base):
    """
    ISA contribution tracking for UK tax year allowances.

    Tracks ISA contributions by tax year with:
    - Annual allowance tracking (£20,000 for 2024/25)
    - Link to savings account (nullable for manual entries)
    - Tax year in UK format (YYYY/YY, e.g., "2024/25")
    - Contribution date for accurate tax year allocation
    """

    __tablename__ = 'isa_contributions'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Optional link to savings account
    savings_account_id = Column(
        GUID,
        ForeignKey('savings_accounts.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )

    # Tax Year and Contribution Details
    tax_year = Column(
        String(7),  # Format: "2024/25"
        nullable=False,
        index=True
    )
    contribution_amount = Column(
        Numeric(10, 2),
        nullable=False
    )
    contribution_date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="isa_contributions")
    savings_account = relationship("SavingsAccount")

    # Table Constraints
    __table_args__ = (
        CheckConstraint('contribution_amount > 0', name='check_positive_isa_contribution'),
        Index('idx_isa_user_tax_year', 'user_id', 'tax_year'),
        Index('idx_isa_account_tax_year', 'savings_account_id', 'tax_year'),
    )

    def __repr__(self) -> str:
        return (
            f"<ISAContribution(id={self.id}, user_id={self.user_id}, "
            f"tax_year={self.tax_year}, amount={self.contribution_amount})>"
        )


class TFSAContribution(Base):
    """
    TFSA contribution tracking for SA tax year allowances.

    Tracks TFSA contributions by tax year with:
    - Annual allowance tracking (R36,000 for 2024/25)
    - Lifetime allowance tracking (R500,000)
    - Contribution type (DEPOSIT or GROWTH)
    - Link to savings account (nullable for manual entries)
    - Tax year in SA format (YYYY/YY, e.g., "2024/25")
    """

    __tablename__ = 'tfsa_contributions'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Optional link to savings account
    savings_account_id = Column(
        GUID,
        ForeignKey('savings_accounts.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )

    # Tax Year and Contribution Details
    tax_year = Column(
        String(7),  # Format: "2024/25"
        nullable=False,
        index=True
    )
    contribution_amount = Column(
        Numeric(10, 2),
        nullable=False
    )
    contribution_type = Column(
        SQLEnum(TFSAContributionType, name='tfsa_contribution_type_enum', create_type=False),
        nullable=False,
        default=TFSAContributionType.DEPOSIT
    )
    contribution_date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="tfsa_contributions")
    savings_account = relationship("SavingsAccount")

    # Table Constraints
    __table_args__ = (
        CheckConstraint('contribution_amount > 0', name='check_positive_tfsa_contribution'),
        Index('idx_tfsa_user_tax_year', 'user_id', 'tax_year'),
        Index('idx_tfsa_account_tax_year', 'savings_account_id', 'tax_year'),
    )

    def __repr__(self) -> str:
        return (
            f"<TFSAContribution(id={self.id}, user_id={self.user_id}, "
            f"tax_year={self.tax_year}, amount={self.contribution_amount}, "
            f"type={self.contribution_type})>"
        )


# Create indexes explicitly for better control
Index(
    "idx_savings_account_type",
    SavingsAccount.account_type
)
Index(
    "idx_savings_isa",
    SavingsAccount.is_isa,
    postgresql_where=(SavingsAccount.is_isa.is_(True))
)
Index(
    "idx_savings_tfsa",
    SavingsAccount.is_tfsa,
    postgresql_where=(SavingsAccount.is_tfsa.is_(True))
)
