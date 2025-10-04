"""
Investment account and holdings models for portfolio tracking.

This module provides SQLAlchemy models for:
- Investment accounts (ISA, GIA, VCT, EIS, SEIS, SA accounts)
- Investment holdings with encrypted account numbers
- Tax lot tracking for FIFO CGT calculations
- Dividend income tracking
- Realized capital gains tracking

Business logic:
- Account number encryption for security
- Multi-currency support with GBP/ZAR conversion
- Tax lot tracking for accurate CGT calculation
- Dividend withholding tax tracking
- Soft delete for audit trail
- Asset allocation and performance metrics
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
import enum

from sqlalchemy import (
    Column, String, ForeignKey, Numeric, Boolean, DateTime,
    Date, Text, CheckConstraint, Index, Enum as SQLEnum, Integer
)
from sqlalchemy.orm import relationship, validates

from database import Base
from models.user import GUID
from utils.encryption import encrypt_value, decrypt_value
from dateutil.relativedelta import relativedelta


class AccountType(str, enum.Enum):
    """Investment account type enumeration."""
    STOCKS_ISA = 'STOCKS_ISA'
    GIA = 'GIA'
    VCT = 'VCT'
    EIS = 'EIS'
    SEIS = 'SEIS'
    SA_UNIT_TRUST = 'SA_UNIT_TRUST'
    SA_ETF = 'SA_ETF'
    SA_DIRECT_SHARES = 'SA_DIRECT_SHARES'
    OFFSHORE_BOND = 'OFFSHORE_BOND'


class AccountCountry(str, enum.Enum):
    """Account country enumeration."""
    UK = 'UK'
    SA = 'SA'
    OFFSHORE = 'OFFSHORE'


class AccountStatus(str, enum.Enum):
    """Account status enumeration."""
    ACTIVE = 'ACTIVE'
    CLOSED = 'CLOSED'


class SecurityType(str, enum.Enum):
    """Security type enumeration."""
    STOCK = 'STOCK'
    FUND = 'FUND'
    ETF = 'ETF'
    BOND = 'BOND'
    VCT = 'VCT'
    EIS_SHARE = 'EIS_SHARE'
    SEIS_SHARE = 'SEIS_SHARE'


class AssetClass(str, enum.Enum):
    """Asset class enumeration."""
    EQUITY = 'EQUITY'
    FIXED_INCOME = 'FIXED_INCOME'
    PROPERTY = 'PROPERTY'
    COMMODITY = 'COMMODITY'
    CASH = 'CASH'
    ALTERNATIVE = 'ALTERNATIVE'


class Region(str, enum.Enum):
    """Region enumeration."""
    UK = 'UK'
    US = 'US'
    EUROPE = 'EUROPE'
    ASIA = 'ASIA'
    EMERGING = 'EMERGING'
    GLOBAL = 'GLOBAL'


class DisposalMethod(str, enum.Enum):
    """Disposal method enumeration for CGT calculation."""
    FIFO = 'FIFO'
    AVERAGE_COST = 'AVERAGE_COST'
    SPECIFIC_IDENTIFICATION = 'SPECIFIC_IDENTIFICATION'


class SourceCountry(str, enum.Enum):
    """Source country enumeration for dividends."""
    UK = 'UK'
    SA = 'SA'
    US = 'US'
    OTHER = 'OTHER'


class Currency(str, enum.Enum):
    """Supported currency codes."""
    GBP = 'GBP'
    ZAR = 'ZAR'
    USD = 'USD'
    EUR = 'EUR'


class SchemeType(str, enum.Enum):
    """Tax-advantaged investment scheme type enumeration."""
    EIS = 'EIS'
    SEIS = 'SEIS'
    VCT = 'VCT'


class InvestmentAccount(Base):
    """
    Investment account tracking with encrypted account numbers.

    Tracks investment accounts across multiple countries and types with:
    - Encrypted account numbers for security
    - Multi-currency support
    - Account status tracking
    - Soft delete for audit trail
    """

    __tablename__ = 'investment_accounts'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Account Details
    account_type = Column(
        SQLEnum(AccountType, name='account_type_enum', create_type=False),
        nullable=False
    )
    provider = Column(String(255), nullable=False)
    account_number_encrypted = Column(Text, nullable=False)  # Encrypted account number
    account_number_last_4 = Column(String(4), nullable=True)  # Last 4 digits for display
    country = Column(
        SQLEnum(AccountCountry, name='account_country_enum', create_type=False),
        nullable=False
    )
    base_currency = Column(String(3), nullable=False)
    account_open_date = Column(Date, nullable=True)

    # Status
    status = Column(
        SQLEnum(AccountStatus, name='account_status_enum', create_type=False),
        default=AccountStatus.ACTIVE,
        nullable=False,
        index=True
    )

    # Soft Delete
    deleted = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="investment_accounts")
    holdings = relationship(
        "InvestmentHolding",
        back_populates="account",
        cascade="all, delete-orphan"
    )

    # Table Constraints
    __table_args__ = (
        Index('idx_investment_account_user_deleted', 'user_id', 'deleted'),
        Index('idx_investment_account_user_status', 'user_id', 'status'),
    )

    def set_account_number(self, account_number: str) -> None:
        """
        Encrypt and set account number.

        Args:
            account_number: Plain text account number
        """
        self.account_number_encrypted = encrypt_value(account_number)
        # Store last 4 digits for display
        if len(account_number) >= 4:
            self.account_number_last_4 = account_number[-4:]
        else:
            self.account_number_last_4 = account_number

    def get_account_number(self) -> str:
        """
        Decrypt and return account number.

        Returns:
            str: Decrypted account number
        """
        return decrypt_value(self.account_number_encrypted)

    def __repr__(self) -> str:
        return (
            f"<InvestmentAccount(id={self.id}, user_id={self.user_id}, "
            f"type={self.account_type}, provider={self.provider})>"
        )


class InvestmentHolding(Base):
    """
    Investment holding tracking with calculated metrics.

    Tracks individual security holdings with:
    - Security details (ticker, ISIN, name)
    - Quantity and pricing information
    - Calculated unrealized gains/losses
    - Asset allocation metadata
    - Soft delete for audit trail
    """

    __tablename__ = 'investment_holdings'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    account_id = Column(
        GUID,
        ForeignKey('investment_accounts.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Security Details
    security_type = Column(
        SQLEnum(SecurityType, name='security_type_enum', create_type=False),
        nullable=False
    )
    ticker = Column(String(20), nullable=True, index=True)
    isin = Column(String(12), nullable=True)
    security_name = Column(String(255), nullable=False)

    # Quantity and Pricing
    quantity = Column(Numeric(15, 4), nullable=False)
    purchase_date = Column(Date, nullable=False)
    purchase_price = Column(Numeric(15, 4), nullable=False)
    purchase_currency = Column(String(3), nullable=False)
    current_price = Column(Numeric(15, 4), nullable=False)

    # Asset Classification
    asset_class = Column(
        SQLEnum(AssetClass, name='asset_class_enum', create_type=False),
        nullable=False
    )
    region = Column(
        SQLEnum(Region, name='region_enum', create_type=False),
        nullable=False
    )
    sector = Column(String(100), nullable=True)

    # Price Update Tracking
    last_price_update = Column(DateTime, nullable=True)

    # Soft Delete
    deleted = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    account = relationship("InvestmentAccount", back_populates="holdings")
    tax_lots = relationship(
        "TaxLot",
        back_populates="holding",
        cascade="all, delete-orphan"
    )
    dividends = relationship(
        "DividendIncome",
        back_populates="holding",
        cascade="all, delete-orphan"
    )
    capital_gains = relationship(
        "CapitalGainRealized",
        back_populates="holding",
        cascade="all, delete-orphan"
    )
    tax_advantaged = relationship(
        "TaxAdvantagedInvestment",
        back_populates="holding",
        uselist=False,  # One-to-one relationship
        cascade="all, delete-orphan"
    )

    # Table Constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_positive_quantity'),
        CheckConstraint('purchase_price >= 0', name='check_non_negative_purchase_price'),
        CheckConstraint('current_price >= 0', name='check_non_negative_current_price'),
        Index('idx_investment_holding_account_deleted', 'account_id', 'deleted'),
        Index('idx_investment_holding_ticker', 'ticker'),
    )

    @property
    def current_value(self) -> Decimal:
        """
        Calculate current value of holding.

        Returns:
            Decimal: Current value (current_price * quantity)
        """
        return Decimal(str(self.current_price)) * Decimal(str(self.quantity))

    @property
    def unrealized_gain(self) -> Decimal:
        """
        Calculate unrealized gain/loss.

        Returns:
            Decimal: Unrealized gain (can be negative for loss)
        """
        return (Decimal(str(self.current_price)) - Decimal(str(self.purchase_price))) * Decimal(str(self.quantity))

    @property
    def unrealized_gain_percentage(self) -> Decimal:
        """
        Calculate unrealized gain/loss percentage.

        Returns:
            Decimal: Unrealized gain percentage (rounded to 2 decimal places)
        """
        if self.purchase_price == 0:
            return Decimal('0.00')
        percentage = ((Decimal(str(self.current_price)) - Decimal(str(self.purchase_price))) / Decimal(str(self.purchase_price))) * 100
        # Round to 2 decimal places for display
        return percentage.quantize(Decimal('0.01'))

    def __repr__(self) -> str:
        return (
            f"<InvestmentHolding(id={self.id}, account_id={self.account_id}, "
            f"security={self.security_name}, quantity={self.quantity})>"
        )


class TaxLot(Base):
    """
    Tax lot tracking for FIFO CGT calculations.

    Tracks individual purchase lots for accurate capital gains tax calculation with:
    - Purchase details and cost basis
    - Multi-currency cost basis (GBP and ZAR)
    - Disposal tracking
    - FIFO, average cost, or specific identification methods
    """

    __tablename__ = 'tax_lots'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    holding_id = Column(
        GUID,
        ForeignKey('investment_holdings.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Purchase Details
    purchase_date = Column(Date, nullable=False)
    quantity = Column(Numeric(15, 4), nullable=False)
    purchase_price = Column(Numeric(15, 4), nullable=False)
    purchase_currency = Column(String(3), nullable=False)

    # Cost Basis
    cost_basis_gbp = Column(Numeric(15, 2), nullable=False)
    cost_basis_zar = Column(Numeric(15, 2), nullable=False)
    exchange_rate = Column(Numeric(10, 6), nullable=False)

    # Disposal Details
    disposal_date = Column(Date, nullable=True)
    disposal_quantity = Column(Numeric(15, 4), nullable=True)
    disposal_proceeds = Column(Numeric(15, 2), nullable=True)
    realized_gain = Column(Numeric(15, 2), nullable=True)
    cgt_tax_year = Column(String(10), nullable=True)
    disposal_method = Column(
        SQLEnum(DisposalMethod, name='disposal_method_enum', create_type=False),
        nullable=True
    )

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    holding = relationship("InvestmentHolding", back_populates="tax_lots")

    # Table Constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_tax_lot_positive_quantity'),
        CheckConstraint('purchase_price >= 0', name='check_tax_lot_non_negative_purchase_price'),
        CheckConstraint('cost_basis_gbp >= 0', name='check_tax_lot_non_negative_cost_basis_gbp'),
        CheckConstraint('cost_basis_zar >= 0', name='check_tax_lot_non_negative_cost_basis_zar'),
        CheckConstraint('disposal_quantity IS NULL OR disposal_quantity > 0', name='check_tax_lot_positive_disposal_quantity'),
        CheckConstraint('disposal_proceeds IS NULL OR disposal_proceeds >= 0', name='check_tax_lot_non_negative_disposal_proceeds'),
        Index('idx_tax_lot_holding_disposal', 'holding_id', 'disposal_date'),
    )

    def __repr__(self) -> str:
        return (
            f"<TaxLot(id={self.id}, holding_id={self.holding_id}, "
            f"quantity={self.quantity}, purchase_date={self.purchase_date})>"
        )


class DividendIncome(Base):
    """
    Dividend income tracking with withholding tax.

    Tracks dividend payments with:
    - Dividend amounts (gross and net)
    - Withholding tax tracking
    - Source country for DTA relief
    - Tax year allocation (UK and SA)
    """

    __tablename__ = 'dividend_income'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    holding_id = Column(
        GUID,
        ForeignKey('investment_holdings.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Dividend Details
    payment_date = Column(Date, nullable=False)
    ex_dividend_date = Column(Date, nullable=True)
    dividend_per_share = Column(Numeric(10, 4), nullable=False)
    total_dividend_gross = Column(Numeric(10, 2), nullable=False)
    withholding_tax = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    total_dividend_net = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)

    # Source Country
    source_country = Column(
        SQLEnum(SourceCountry, name='source_country_enum', create_type=False),
        nullable=False
    )

    # Tax Year Allocation
    uk_tax_year = Column(String(7), nullable=True)  # e.g., "2024/25"
    sa_tax_year = Column(String(9), nullable=True)  # e.g., "2024/2025"

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    holding = relationship("InvestmentHolding", back_populates="dividends")

    # Table Constraints
    __table_args__ = (
        CheckConstraint('dividend_per_share >= 0', name='check_dividend_non_negative_dividend_per_share'),
        CheckConstraint('total_dividend_gross >= 0', name='check_dividend_non_negative_total_gross'),
        CheckConstraint('withholding_tax >= 0', name='check_dividend_non_negative_withholding_tax'),
        CheckConstraint('total_dividend_net >= 0', name='check_dividend_non_negative_total_net'),
        Index('idx_dividend_holding_payment_date', 'holding_id', 'payment_date'),
    )

    def __repr__(self) -> str:
        return (
            f"<DividendIncome(id={self.id}, holding_id={self.holding_id}, "
            f"payment_date={self.payment_date}, amount={self.total_dividend_net})>"
        )


class CapitalGainRealized(Base):
    """
    Realized capital gains tracking.

    Tracks realized capital gains from disposals with:
    - Sale details (quantity, price, value)
    - Cost basis and calculated gain/loss
    - Tax year allocation
    - Country for tax reporting
    """

    __tablename__ = 'capital_gains_realized'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    holding_id = Column(
        GUID,
        ForeignKey('investment_holdings.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Disposal Details
    disposal_date = Column(Date, nullable=False)
    quantity_sold = Column(Numeric(15, 4), nullable=False)
    sale_price = Column(Numeric(15, 4), nullable=False)
    sale_value = Column(Numeric(15, 2), nullable=False)
    cost_basis = Column(Numeric(15, 2), nullable=False)
    gain_loss = Column(Numeric(15, 2), nullable=False)

    # Tax Details
    tax_year = Column(String(10), nullable=False)
    country = Column(
        SQLEnum(AccountCountry, name='account_country_enum', create_type=False),
        nullable=False
    )

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    holding = relationship("InvestmentHolding", back_populates="capital_gains")

    # Table Constraints
    __table_args__ = (
        CheckConstraint('quantity_sold > 0', name='check_cg_positive_quantity_sold'),
        CheckConstraint('sale_price >= 0', name='check_cg_non_negative_sale_price'),
        CheckConstraint('sale_value >= 0', name='check_cg_non_negative_sale_value'),
        CheckConstraint('cost_basis >= 0', name='check_cg_non_negative_cost_basis'),
        Index('idx_capital_gain_holding_tax_year', 'holding_id', 'tax_year'),
    )

    def __repr__(self) -> str:
        return (
            f"<CapitalGainRealized(id={self.id}, holding_id={self.holding_id}, "
            f"disposal_date={self.disposal_date}, gain_loss={self.gain_loss})>"
        )


class TaxAdvantagedInvestment(Base):
    """
    Tax-advantaged investment tracking (EIS, SEIS, VCT).

    Tracks UK tax-advantaged investments with:
    - Income tax relief tracking (30% EIS/VCT, 50% SEIS)
    - Minimum holding period monitoring (3 years EIS/SEIS, 5 years VCT)
    - CGT deferral/exemption eligibility
    - Relief withdrawal tracking
    """

    __tablename__ = 'tax_advantaged_investments'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    holding_id = Column(
        GUID,
        ForeignKey('investment_holdings.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,  # One-to-one relationship
        index=True
    )

    # Scheme Details
    scheme_type = Column(
        SQLEnum(SchemeType, name='scheme_type_enum', create_type=False),
        nullable=False
    )
    investment_date = Column(Date, nullable=False)
    investment_amount = Column(Numeric(15, 2), nullable=False)

    # Income Tax Relief
    income_tax_relief_claimed = Column(Numeric(10, 2), nullable=False)
    income_tax_relief_percentage = Column(Numeric(5, 2), nullable=False)
    tax_year_claimed = Column(String(7), nullable=False)  # Format: 2023/24

    # Holding Period
    minimum_holding_period_years = Column(Integer, nullable=False)
    holding_period_end_date = Column(Date, nullable=False)

    # CGT Benefits
    cgt_deferral_claimed = Column(Numeric(10, 2), nullable=True)  # EIS only
    cgt_exemption_eligible = Column(Boolean, default=False, nullable=False)

    # Relief Status
    relief_withdrawn = Column(Boolean, default=False, nullable=False)
    relief_withdrawal_reason = Column(Text, nullable=True)
    relief_withdrawal_date = Column(Date, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    holding = relationship("InvestmentHolding", back_populates="tax_advantaged")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'income_tax_relief_percentage IN (30.0, 50.0)',
            name='check_valid_relief_percentage'
        ),
        CheckConstraint(
            'minimum_holding_period_years IN (3, 5)',
            name='check_valid_holding_period'
        ),
        CheckConstraint(
            'investment_amount > 0',
            name='check_positive_investment_amount'
        ),
        CheckConstraint(
            'income_tax_relief_claimed >= 0',
            name='check_non_negative_relief_claimed'
        ),
        CheckConstraint(
            'cgt_deferral_claimed IS NULL OR cgt_deferral_claimed >= 0',
            name='check_non_negative_cgt_deferral'
        ),
        Index('idx_tax_advantaged_holding_id', 'holding_id'),
        Index('idx_tax_advantaged_scheme_type', 'scheme_type'),
        Index('idx_tax_advantaged_holding_period_end', 'holding_period_end_date'),
        Index('idx_tax_advantaged_at_risk', 'holding_period_end_date', 'relief_withdrawn'),
    )

    @property
    def years_held(self) -> Decimal:
        """
        Calculate years held from investment date to today.

        Returns:
            Decimal: Number of years held (can be fractional)
        """
        delta = date.today() - self.investment_date
        return Decimal(str(delta.days / 365.25))

    @property
    def holding_period_remaining(self) -> Decimal:
        """
        Calculate remaining years to hold for relief retention.

        Returns:
            Decimal: Remaining years (0 if holding period complete)
        """
        remaining = Decimal(str(self.minimum_holding_period_years)) - self.years_held
        return max(Decimal('0'), remaining)

    @property
    def at_risk_of_losing_relief(self) -> bool:
        """
        Check if relief is at risk (still within holding period).

        Returns:
            bool: True if still within holding period and relief not withdrawn
        """
        return self.holding_period_remaining > 0 and not self.relief_withdrawn

    @property
    def relief_secure(self) -> bool:
        """
        Check if relief is secure (holding period complete).

        Returns:
            bool: True if holding period complete and relief not withdrawn
        """
        return self.holding_period_remaining == 0 and not self.relief_withdrawn

    def calculate_holding_period_end_date(self) -> date:
        """
        Calculate when holding period ends.

        Returns:
            date: Date when holding period ends
        """
        return self.investment_date + relativedelta(years=self.minimum_holding_period_years)

    def withdraw_relief(self, reason: str) -> None:
        """
        Withdraw tax relief (e.g., sold before holding period).

        Args:
            reason: Reason for withdrawing relief
        """
        self.relief_withdrawn = True
        self.relief_withdrawal_reason = reason
        self.relief_withdrawal_date = date.today()

    def __repr__(self) -> str:
        return (
            f"<TaxAdvantagedInvestment(id={self.id}, holding_id={self.holding_id}, "
            f"scheme_type={self.scheme_type}, investment_amount={self.investment_amount})>"
        )


# Create additional indexes for performance
Index(
    "idx_investment_account_status",
    InvestmentAccount.status
)

Index(
    "idx_investment_account_country",
    InvestmentAccount.country
)

Index(
    "idx_investment_holding_security_type",
    InvestmentHolding.security_type
)

Index(
    "idx_investment_holding_asset_class",
    InvestmentHolding.asset_class
)
