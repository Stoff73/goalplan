"""
Income tracking models for multi-currency, multi-jurisdiction income management.

This module provides SQLAlchemy models for:
- User income records with currency conversion
- Tax withholding details (PAYE/PASE)
- Exchange rate history for accurate conversion

Business logic:
- Multi-currency support (GBP, ZAR, USD, EUR)
- UK and SA tax year allocation
- Foreign income and DTA tracking
- Soft delete for audit trail
- Currency conversion caching for performance
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column, String, ForeignKey, Numeric, Boolean, DateTime,
    Date, Text, CheckConstraint, UniqueConstraint, Index, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
import enum

from database import Base
from models.user import GUID  # Use platform-independent GUID type


class IncomeType(str, enum.Enum):
    """Income type enumeration."""
    EMPLOYMENT = 'employment'
    SELF_EMPLOYMENT = 'self_employment'
    RENTAL = 'rental'
    INVESTMENT = 'investment'
    PENSION = 'pension'
    OTHER = 'other'


class IncomeFrequency(str, enum.Enum):
    """Income frequency enumeration."""
    ANNUAL = 'annual'
    MONTHLY = 'monthly'
    WEEKLY = 'weekly'
    ONE_TIME = 'one_time'


class Currency(str, enum.Enum):
    """Supported currency codes."""
    GBP = 'GBP'
    ZAR = 'ZAR'
    USD = 'USD'
    EUR = 'EUR'


class UserIncome(Base):
    """
    User income tracking with multi-currency support.

    Tracks income from various sources across different countries with:
    - Multi-currency amounts and conversions
    - UK and SA tax year allocation
    - Gross/net income handling
    - Tax withholding at source
    - Foreign income and DTA tracking
    - Soft delete for audit trail
    """

    __tablename__ = 'user_income'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Income Details
    income_type = Column(
        SQLEnum(IncomeType, name='income_type_enum', create_type=True),
        nullable=False
    )
    source_country = Column(String(2), nullable=False)  # 'UK', 'ZA', 'US', etc.
    description = Column(Text, nullable=True)
    employer_name = Column(String(255), nullable=True)  # For employment income

    # Amount and Currency
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(
        SQLEnum(Currency, name='currency_enum', create_type=True),
        nullable=False
    )
    amount_in_gbp = Column(Numeric(15, 2), nullable=True)  # Converted amount (cached)
    amount_in_zar = Column(Numeric(15, 2), nullable=True)  # Converted amount (cached)
    exchange_rate = Column(Numeric(10, 6), nullable=True)  # Rate used for conversion
    exchange_rate_date = Column(Date, nullable=True)  # Date of exchange rate

    # Frequency and Tax Year
    frequency = Column(
        SQLEnum(IncomeFrequency, name='income_frequency_enum', create_type=True),
        nullable=False
    )
    tax_year_uk = Column(String(10), nullable=True)  # '2023/24' format
    tax_year_sa = Column(String(10), nullable=True)  # '2023/24' format
    income_date = Column(Date, nullable=False)  # Date income was received

    # Gross/Net and Tax Withholding
    is_gross = Column(Boolean, default=True, nullable=False)  # TRUE = gross, FALSE = net
    tax_withheld_amount = Column(Numeric(15, 2), nullable=True)
    tax_withheld_currency = Column(
        SQLEnum(Currency, name='currency_enum', create_type=False),
        nullable=True
    )

    # Foreign Income Details
    is_foreign_income = Column(Boolean, default=False, nullable=False)
    foreign_tax_credit = Column(Numeric(15, 2), nullable=True)  # Tax paid in foreign country
    dta_applicable = Column(Boolean, default=False, nullable=False)  # Double Tax Agreement applies

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # Relationships
    user = relationship("User", back_populates="income_records")
    tax_withholding = relationship("IncomeTaxWithholding", back_populates="income", uselist=False, cascade="all, delete-orphan")

    # Table Constraints
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_positive_amount'),
        Index('idx_income_user_active', 'user_id', 'deleted_at', postgresql_where=(deleted_at.is_(None))),
        Index('idx_income_tax_year_uk', 'user_id', 'tax_year_uk'),
        Index('idx_income_tax_year_sa', 'user_id', 'tax_year_sa'),
        Index('idx_income_date', 'user_id', 'income_date'),
        Index('idx_income_type', 'user_id', 'income_type'),
    )

    def __repr__(self) -> str:
        return (
            f"<UserIncome(id={self.id}, user_id={self.user_id}, "
            f"type={self.income_type}, amount={self.amount} {self.currency})>"
        )


class IncomeTaxWithholding(Base):
    """
    PAYE/PASE withholding details for employment income.

    Tracks tax withheld at source:
    - UK PAYE (Pay As You Earn) details
    - SA PASE (Pay As You Earn) details
    - National Insurance / UIF contributions
    - Employer contributions
    """

    __tablename__ = 'income_tax_withholding'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    income_id = Column(
        GUID,
        ForeignKey('user_income.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )

    # UK PAYE Details
    paye_income_tax = Column(Numeric(15, 2), nullable=True)
    paye_ni_class1 = Column(Numeric(15, 2), nullable=True)
    paye_tax_code = Column(String(20), nullable=True)

    # SA PASE Details
    pase_income_tax = Column(Numeric(15, 2), nullable=True)
    pase_uif = Column(Numeric(15, 2), nullable=True)  # Unemployment Insurance Fund

    # Employer Contributions (for completeness)
    employer_ni = Column(Numeric(15, 2), nullable=True)  # UK employer NI
    employer_uif = Column(Numeric(15, 2), nullable=True)  # SA employer UIF

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    income = relationship("UserIncome", back_populates="tax_withholding")

    def __repr__(self) -> str:
        return f"<IncomeTaxWithholding(id={self.id}, income_id={self.income_id})>"


class ExchangeRate(Base):
    """
    Exchange rate history for currency conversions.

    Stores daily exchange rates from external APIs:
    - Supports all currency pairs (GBP, ZAR, USD, EUR)
    - One rate per currency pair per day
    - Tracks source API for audit trail
    - Used for income currency conversion
    """

    __tablename__ = 'exchange_rates'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)

    # Exchange Rate Details
    from_currency = Column(String(3), nullable=False)
    to_currency = Column(String(3), nullable=False)
    rate = Column(Numeric(10, 6), nullable=False)
    rate_date = Column(Date, nullable=False)
    source = Column(String(50), default='exchangerate-api', nullable=False)  # API source

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Table Constraints
    __table_args__ = (
        UniqueConstraint('from_currency', 'to_currency', 'rate_date', name='unique_rate_per_day'),
        Index('idx_exchange_rates_currencies_date', 'from_currency', 'to_currency', 'rate_date'),
    )

    def __repr__(self) -> str:
        return (
            f"<ExchangeRate({self.from_currency}/{self.to_currency}={self.rate} "
            f"on {self.rate_date})>"
        )
