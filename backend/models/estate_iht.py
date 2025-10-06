"""
Estate valuation and IHT planning database models.

This module provides SQLAlchemy models for:
- Estate assets (property, investments, cash, business interests, etc.)
- Estate liabilities (mortgages, loans, credit cards, etc.)
- UK IHT calculations (Nil Rate Band, Residence NRB, reliefs)
- SA Estate Duty calculations (abatement, rates)

Business logic:
- Temporal data support (effective_from/effective_to) for asset and liability tracking
- Soft delete for audit trail
- Multi-currency support with GBP and ZAR
- Asset categorization for IHT/Estate Duty purposes
- Liability deductibility determination
- NRB and RNRB tracking with transferable allowances
- Estate duty calculations with SA abatement
"""

import uuid
import enum
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column, String, ForeignKey, Numeric, Boolean, DateTime,
    Date, Text, CheckConstraint, Index, Enum as SQLEnum
)
from sqlalchemy.orm import relationship, validates

from database import Base
from models.user import GUID


class AssetType(str, enum.Enum):
    """Estate asset type enumeration."""
    PROPERTY = 'PROPERTY'
    INVESTMENTS = 'INVESTMENTS'
    PENSIONS = 'PENSIONS'
    LIFE_ASSURANCE = 'LIFE_ASSURANCE'
    BUSINESS = 'BUSINESS'
    OTHER = 'OTHER'


class LiabilityType(str, enum.Enum):
    """Estate liability type enumeration."""
    MORTGAGE = 'MORTGAGE'
    LOAN = 'LOAN'
    CREDIT_CARD = 'CREDIT_CARD'
    OTHER = 'OTHER'


class EstateAsset(Base):
    """
    Estate asset tracking for IHT planning.

    Tracks all estate assets with:
    - Asset type, description, and estimated value
    - Multi-currency support (GBP, ZAR)
    - Ownership structure (individual, joint)
    - Inclusion in UK and/or SA estate
    - Temporal data support (effective_from/effective_to)
    - Soft delete for audit trail
    """

    __tablename__ = 'estate_assets'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Asset Details
    asset_type = Column(
        SQLEnum(AssetType, name='asset_type_enum', create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        doc="Type of asset (property, investments, etc.)"
    )
    description = Column(
        String(500),
        nullable=False,
        doc="Description of the asset"
    )

    # Valuation
    estimated_value = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Current estimated value"
    )
    currency = Column(
        String(3),
        nullable=False,
        default='GBP',
        doc="Currency code (GBP, ZAR, etc.)"
    )

    # Ownership
    owned_individually = Column(
        Boolean,
        nullable=False,
        default=True,
        doc="True if owned individually, False if joint ownership"
    )
    joint_ownership = Column(
        String(255),
        nullable=True,
        doc="Name of co-owner if jointly owned"
    )

    # Estate Inclusion
    included_in_uk_estate = Column(
        Boolean,
        nullable=False,
        default=True,
        doc="Whether asset is included in UK estate for IHT"
    )
    included_in_sa_estate = Column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether asset is included in SA estate for Estate Duty"
    )

    # Temporal Data Support
    effective_from = Column(
        Date,
        nullable=False,
        doc="Date when this asset valuation becomes effective"
    )
    effective_to = Column(
        Date,
        nullable=True,
        doc="Date when this asset valuation stops (NULL = current)"
    )

    # Soft Delete
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="estate_assets")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'estimated_value >= 0',
            name='check_estate_asset_non_negative_value'
        ),
        CheckConstraint(
            'effective_to IS NULL OR effective_to >= effective_from',
            name='check_estate_asset_valid_effective_dates'
        ),
        Index('idx_estate_asset_user_id', 'user_id'),
        Index('idx_estate_asset_user_type', 'user_id', 'asset_type'),
        Index('idx_estate_asset_user_deleted', 'user_id', 'is_deleted'),
        Index('idx_estate_asset_effective_dates', 'user_id', 'effective_from', 'effective_to'),
    )

    @validates('currency')
    def validate_currency(self, key, value):
        """Validate currency code is 3 characters."""
        if value and len(value) != 3:
            raise ValueError(f"Currency must be 3 characters. Got: {value}")
        return value.upper() if value else value

    def __repr__(self) -> str:
        return (
            f"<EstateAsset(id={self.id}, user_id={self.user_id}, "
            f"type={self.asset_type}, value={self.estimated_value} {self.currency})>"
        )


class EstateLiability(Base):
    """
    Estate liability tracking for IHT planning.

    Tracks all estate liabilities with:
    - Liability type, description, and amount outstanding
    - Multi-currency support (GBP, ZAR)
    - Deductibility from estate
    - Temporal data support (effective_from/effective_to)
    - Soft delete for audit trail
    """

    __tablename__ = 'estate_liabilities'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Liability Details
    liability_type = Column(
        SQLEnum(LiabilityType, name='liability_type_enum', create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        doc="Type of liability (mortgage, loan, etc.)"
    )
    description = Column(
        String(500),
        nullable=False,
        doc="Description of the liability"
    )

    # Amount
    amount_outstanding = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Current outstanding balance"
    )
    currency = Column(
        String(3),
        nullable=False,
        default='GBP',
        doc="Currency code (GBP, ZAR, etc.)"
    )

    # Deductibility
    deductible_from_estate = Column(
        Boolean,
        nullable=False,
        default=True,
        doc="Whether liability is deductible from estate for IHT/Estate Duty"
    )

    # Temporal Data Support
    effective_from = Column(
        Date,
        nullable=False,
        doc="Date when this liability becomes effective"
    )
    effective_to = Column(
        Date,
        nullable=True,
        doc="Date when this liability stops (NULL = current)"
    )

    # Soft Delete
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="estate_liabilities")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'amount_outstanding >= 0',
            name='check_estate_liability_non_negative_amount'
        ),
        CheckConstraint(
            'effective_to IS NULL OR effective_to >= effective_from',
            name='check_estate_liability_valid_effective_dates'
        ),
        Index('idx_estate_liability_user_id', 'user_id'),
        Index('idx_estate_liability_user_type', 'user_id', 'liability_type'),
        Index('idx_estate_liability_user_deleted', 'user_id', 'is_deleted'),
        Index('idx_estate_liability_effective_dates', 'user_id', 'effective_from', 'effective_to'),
    )

    @validates('currency')
    def validate_currency(self, key, value):
        """Validate currency code is 3 characters."""
        if value and len(value) != 3:
            raise ValueError(f"Currency must be 3 characters. Got: {value}")
        return value.upper() if value else value

    def __repr__(self) -> str:
        return (
            f"<EstateLiability(id={self.id}, user_id={self.user_id}, "
            f"type={self.liability_type}, amount={self.amount_outstanding} {self.currency})>"
        )


class IHTCalculation(Base):
    """
    UK Inheritance Tax calculation tracking.

    Stores IHT calculations with:
    - Gross and net estate values
    - Nil Rate Band (NRB) and Residence NRB tracking
    - Transferable NRB from deceased spouse
    - Taxable estate and IHT owed
    - Tax year tracking
    """

    __tablename__ = 'iht_calculations'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Calculation Details
    calculation_date = Column(
        Date,
        nullable=False,
        doc="Date of calculation"
    )
    tax_year = Column(
        String(7),
        nullable=False,
        doc="UK tax year in format YYYY/YY (e.g., 2024/25)"
    )

    # Estate Values
    gross_estate_value = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Gross estate value before liabilities"
    )
    net_estate_value = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Net estate value after deducting liabilities"
    )

    # Nil Rate Bands
    nil_rate_band = Column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal('325000.00'),
        doc="Standard Nil Rate Band (£325,000 as of 2024)"
    )
    residence_nil_rate_band = Column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Residence Nil Rate Band (max £175,000, tapered if estate > £2M)"
    )
    transferable_nil_rate_band = Column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Transferable NRB from deceased spouse"
    )
    total_nil_rate_band_available = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Total NRB available (standard + residence + transferable)"
    )

    # IHT Calculation
    taxable_estate = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Taxable estate after NRB deductions"
    )
    iht_owed = Column(
        Numeric(15, 2),
        nullable=False,
        doc="IHT owed (40% of taxable estate, or 36% if 10%+ to charity)"
    )

    # Currency
    currency = Column(
        String(3),
        nullable=False,
        default='GBP',
        doc="Currency code (GBP)"
    )

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="iht_calculations")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'gross_estate_value >= 0',
            name='check_iht_non_negative_gross_estate'
        ),
        CheckConstraint(
            'net_estate_value >= 0',
            name='check_iht_non_negative_net_estate'
        ),
        CheckConstraint(
            'nil_rate_band >= 0',
            name='check_iht_non_negative_nrb'
        ),
        CheckConstraint(
            'residence_nil_rate_band >= 0',
            name='check_iht_non_negative_rnrb'
        ),
        CheckConstraint(
            'transferable_nil_rate_band >= 0',
            name='check_iht_non_negative_transferable_nrb'
        ),
        CheckConstraint(
            'total_nil_rate_band_available >= 0',
            name='check_iht_non_negative_total_nrb'
        ),
        CheckConstraint(
            'taxable_estate >= 0',
            name='check_iht_non_negative_taxable_estate'
        ),
        CheckConstraint(
            'iht_owed >= 0',
            name='check_iht_non_negative_iht_owed'
        ),
        Index('idx_iht_calculation_user_id', 'user_id'),
        Index('idx_iht_calculation_date', 'user_id', 'calculation_date'),
        Index('idx_iht_calculation_tax_year', 'user_id', 'tax_year'),
    )

    @validates('tax_year')
    def validate_tax_year_format(self, key, value):
        """Validate UK tax year format (YYYY/YY)."""
        if value and len(value) == 7 and value[4] == '/':
            return value
        raise ValueError(f"Invalid UK tax year format: {value}. Expected format: YYYY/YY (e.g., 2024/25)")

    def calculate_iht(
        self,
        charitable_gift_percentage: Decimal = Decimal('0.00')
    ) -> Decimal:
        """
        Calculate IHT owed based on taxable estate.

        Args:
            charitable_gift_percentage: Percentage of estate left to charity (0-100)

        Returns:
            Decimal: IHT owed
        """
        # Determine IHT rate
        if charitable_gift_percentage >= Decimal('10.00'):
            iht_rate = Decimal('0.36')  # 36% reduced rate
        else:
            iht_rate = Decimal('0.40')  # 40% standard rate

        # Calculate IHT
        taxable = Decimal(str(self.taxable_estate))
        return taxable * iht_rate

    def __repr__(self) -> str:
        return (
            f"<IHTCalculation(id={self.id}, user_id={self.user_id}, "
            f"tax_year={self.tax_year}, iht_owed={self.iht_owed})>"
        )


class SAEstateDutyCalculation(Base):
    """
    South African Estate Duty calculation tracking.

    Stores Estate Duty calculations with:
    - Estate value and abatement
    - Dutiable amount and duty rate
    - Estate duty owed
    - Tax year tracking
    """

    __tablename__ = 'sa_estate_duty_calculations'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Calculation Details
    calculation_date = Column(
        Date,
        nullable=False,
        doc="Date of calculation"
    )

    # Estate Values
    estate_value = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Total estate value"
    )
    abatement = Column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal('3500000.00'),
        doc="SA Estate Duty abatement (R3.5M as of 2024)"
    )
    dutiable_amount = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Dutiable amount (estate_value - abatement)"
    )

    # Estate Duty Calculation
    estate_duty_rate = Column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal('20.00'),
        doc="Estate duty rate (20% on R0-30M, 25% on >30M)"
    )
    estate_duty_owed = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Estate duty owed"
    )

    # Currency
    currency = Column(
        String(3),
        nullable=False,
        default='ZAR',
        doc="Currency code (ZAR)"
    )

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sa_estate_duty_calculations")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'estate_value >= 0',
            name='check_sa_estate_duty_non_negative_estate_value'
        ),
        CheckConstraint(
            'abatement >= 0',
            name='check_sa_estate_duty_non_negative_abatement'
        ),
        CheckConstraint(
            'dutiable_amount >= 0',
            name='check_sa_estate_duty_non_negative_dutiable_amount'
        ),
        CheckConstraint(
            'estate_duty_rate >= 0 AND estate_duty_rate <= 100',
            name='check_sa_estate_duty_valid_rate'
        ),
        CheckConstraint(
            'estate_duty_owed >= 0',
            name='check_sa_estate_duty_non_negative_owed'
        ),
        Index('idx_sa_estate_duty_user_id', 'user_id'),
        Index('idx_sa_estate_duty_date', 'user_id', 'calculation_date'),
    )

    def calculate_estate_duty(self) -> Decimal:
        """
        Calculate SA Estate Duty owed based on dutiable amount.

        SA Estate Duty rates (as of 2024):
        - 20% on dutiable amount up to R30 million
        - 25% on dutiable amount above R30 million

        Returns:
            Decimal: Estate duty owed
        """
        dutiable = Decimal(str(self.dutiable_amount))
        threshold = Decimal('30000000.00')  # R30M threshold

        if dutiable <= threshold:
            # 20% on full amount
            return dutiable * Decimal('0.20')
        else:
            # 20% on first R30M + 25% on excess
            duty_on_first_30m = threshold * Decimal('0.20')
            excess = dutiable - threshold
            duty_on_excess = excess * Decimal('0.25')
            return duty_on_first_30m + duty_on_excess

    def __repr__(self) -> str:
        return (
            f"<SAEstateDutyCalculation(id={self.id}, user_id={self.user_id}, "
            f"estate_duty_owed={self.estate_duty_owed})>"
        )


# Create additional indexes for performance
Index(
    "idx_estate_asset_type",
    EstateAsset.asset_type
)

Index(
    "idx_estate_liability_type",
    EstateLiability.liability_type
)

Index(
    "idx_iht_calculation_created",
    IHTCalculation.created_at
)

Index(
    "idx_sa_estate_duty_created",
    SAEstateDutyCalculation.created_at
)


class GiftType(str, enum.Enum):
    """Gift type enumeration for IHT purposes."""
    PET = 'PET'  # Potentially Exempt Transfer
    EXEMPT = 'EXEMPT'  # Immediately exempt (spouse, charity, annual exemption)
    CHARGEABLE = 'CHARGEABLE'  # Chargeable lifetime transfer (e.g., discretionary trust)


class ExemptionType(str, enum.Enum):
    """Gift exemption type enumeration."""
    ANNUAL_EXEMPTION = 'ANNUAL_EXEMPTION'  # £3,000/year
    SMALL_GIFTS = 'SMALL_GIFTS'  # £250/person/year
    NORMAL_EXPENDITURE = 'NORMAL_EXPENDITURE'  # Regular gifts from income
    WEDDING = 'WEDDING'  # £5k child, £2.5k grandchild, £1k other
    CHARITY = 'CHARITY'  # Unlimited to charity
    SPOUSE = 'SPOUSE'  # Unlimited to UK-domiciled spouse


class Gift(Base):
    """
    Lifetime gift tracking for IHT planning (7-year rule).

    Tracks all lifetime gifts with:
    - Gift recipient, date, value, and type
    - Gift classification (PET, EXEMPT, CHARGEABLE)
    - Exemption type applied
    - 7-year PET period tracking
    - Taper relief calculation
    - Soft delete for audit trail

    Business logic:
    - PETs become exempt after 7 years
    - Taper relief applies if death 3-7 years after gift
    - Annual exemption tracking (£3k/year + carry forward)
    """

    __tablename__ = 'gifts'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Gift Details
    recipient = Column(
        String(255),
        nullable=False,
        doc="Name of gift recipient"
    )
    gift_date = Column(
        Date,
        nullable=False,
        index=True,
        doc="Date the gift was made"
    )
    gift_value = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Value of the gift"
    )
    currency = Column(
        String(3),
        nullable=False,
        default='GBP',
        doc="Currency code (GBP, ZAR, etc.)"
    )

    # Gift Classification
    gift_type = Column(
        SQLEnum(GiftType, name='gift_type_enum', create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        doc="Gift type (PET, EXEMPT, CHARGEABLE)"
    )
    exemption_type = Column(
        SQLEnum(ExemptionType, name='exemption_type_enum', create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
        doc="Exemption type applied (if EXEMPT gift)"
    )

    # PET Period Tracking (calculated fields)
    becomes_exempt_date = Column(
        Date,
        nullable=True,
        doc="Date when PET becomes exempt (gift_date + 7 years)"
    )
    still_in_pet_period = Column(
        Boolean,
        nullable=True,
        doc="True if gift_date + 7 years > today (for PETs only)"
    )

    # Additional Information
    description = Column(
        String(500),
        nullable=True,
        doc="Optional description of the gift"
    )

    # Soft Delete
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="gifts")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'gift_value >= 0',
            name='check_gift_non_negative_value'
        ),
        Index('idx_gift_user_id', 'user_id'),
        Index('idx_gift_user_date', 'user_id', 'gift_date'),
        Index('idx_gift_user_deleted', 'user_id', 'is_deleted'),
    )

    @validates('currency')
    def validate_currency(self, key, value):
        """Validate currency code is 3 characters."""
        if value and len(value) != 3:
            raise ValueError(f"Currency must be 3 characters. Got: {value}")
        return value.upper() if value else value

    def calculate_becomes_exempt_date(self) -> Optional[date]:
        """
        Calculate when a PET becomes exempt (gift_date + 7 years).

        Returns:
            date: Date when gift becomes exempt (None for non-PET gifts)
        """
        if self.gift_type != GiftType.PET:
            return None

        from dateutil.relativedelta import relativedelta
        return self.gift_date + relativedelta(years=7)

    def is_still_in_pet_period(self) -> Optional[bool]:
        """
        Check if gift is still within the 7-year PET period.

        Returns:
            bool: True if still in PET period, False if exempt, None for non-PET
        """
        if self.gift_type != GiftType.PET:
            return None

        exempt_date = self.calculate_becomes_exempt_date()
        if exempt_date is None:
            return None

        from datetime import date as date_class
        return exempt_date > date_class.today()

    def years_remaining_until_exempt(self) -> Decimal:
        """
        Calculate years remaining until PET becomes exempt.

        Returns:
            Decimal: Years remaining (0-7), or 0 if already exempt or not a PET
        """
        if self.gift_type != GiftType.PET:
            return Decimal('0.00')

        from datetime import date as date_class
        from dateutil.relativedelta import relativedelta

        exempt_date = self.calculate_becomes_exempt_date()
        if exempt_date is None:
            return Decimal('0.00')

        today = date_class.today()
        if today >= exempt_date:
            return Decimal('0.00')

        # Calculate years remaining (with decimal precision)
        delta = relativedelta(exempt_date, today)
        years = delta.years
        months = delta.months
        days = delta.days

        # Convert to decimal years
        years_decimal = Decimal(str(years))
        months_decimal = Decimal(str(months)) / Decimal('12')
        days_decimal = Decimal(str(days)) / Decimal('365.25')

        total_years = years_decimal + months_decimal + days_decimal

        # Clamp to 0-7 range
        return max(Decimal('0.00'), min(total_years, Decimal('7.00')))

    def calculate_taper_relief(self) -> Decimal:
        """
        Calculate taper relief percentage based on years since gift.

        Taper relief bands (reduces tax, not value):
        - 0-3 years: 0% relief (40% IHT rate)
        - 3-4 years: 20% relief (32% IHT rate)
        - 4-5 years: 40% relief (24% IHT rate)
        - 5-6 years: 60% relief (16% IHT rate)
        - 6-7 years: 80% relief (8% IHT rate)
        - 7+ years: 100% relief (0% IHT - exempt)

        Returns:
            Decimal: Taper relief percentage (0.00 to 1.00)
        """
        if self.gift_type != GiftType.PET:
            return Decimal('1.00') if self.gift_type == GiftType.EXEMPT else Decimal('0.00')

        from datetime import date as date_class
        from dateutil.relativedelta import relativedelta

        today = date_class.today()
        delta = relativedelta(today, self.gift_date)

        # Calculate total years since gift (with decimal precision)
        years = delta.years
        months = delta.months
        days = delta.days

        years_decimal = Decimal(str(years))
        months_decimal = Decimal(str(months)) / Decimal('12')
        days_decimal = Decimal(str(days)) / Decimal('365.25')

        years_since_gift = years_decimal + months_decimal + days_decimal

        # Apply taper relief bands
        if years_since_gift < Decimal('3.00'):
            return Decimal('0.00')  # 0% relief
        elif years_since_gift < Decimal('4.00'):
            return Decimal('0.20')  # 20% relief
        elif years_since_gift < Decimal('5.00'):
            return Decimal('0.40')  # 40% relief
        elif years_since_gift < Decimal('6.00'):
            return Decimal('0.60')  # 60% relief
        elif years_since_gift < Decimal('7.00'):
            return Decimal('0.80')  # 80% relief
        else:
            return Decimal('1.00')  # 100% relief (exempt)

    def __repr__(self) -> str:
        return (
            f"<Gift(id={self.id}, user_id={self.user_id}, "
            f"recipient={self.recipient}, value={self.gift_value} {self.currency}, "
            f"type={self.gift_type})>"
        )


class IHTExemption(Base):
    """
    UK IHT annual exemption tracking.

    Tracks annual exemption usage with:
    - Annual limit (£3,000/year)
    - Amount used and remaining
    - Carry forward from previous year (max £3,000)
    - Small gifts and wedding gifts exemptions
    - Tax year tracking

    Business logic:
    - Annual exemption can be carried forward ONE year only
    - Small gifts exemption: £250/person/year
    - Wedding gifts: £5k (child), £2.5k (grandchild), £1k (other)
    """

    __tablename__ = 'iht_exemptions'

    # Primary Key (composite with user_id and tax_year)
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Tax Year
    tax_year = Column(
        String(7),
        nullable=False,
        index=True,
        doc="UK tax year in format YYYY/YY (e.g., 2024/25)"
    )

    # Annual Exemption (£3,000/year)
    annual_exemption_limit = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('3000.00'),
        doc="Annual exemption limit (£3,000)"
    )
    annual_exemption_used = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Annual exemption used this year"
    )
    annual_exemption_remaining = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('3000.00'),
        doc="Annual exemption remaining (limit - used)"
    )

    # Carry Forward from Previous Year
    carried_forward_from_previous_year = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Unused annual exemption from previous year (max £3,000)"
    )

    # Other Exemptions Usage Tracking
    small_gifts_exemption_used = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Total small gifts exemption used (£250/person/year)"
    )
    wedding_gifts_exemption_used = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Total wedding gifts exemption used (£5k child, £2.5k grandchild, £1k other)"
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="iht_exemptions")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'annual_exemption_limit >= 0',
            name='check_iht_exemption_non_negative_limit'
        ),
        CheckConstraint(
            'annual_exemption_used >= 0',
            name='check_iht_exemption_non_negative_used'
        ),
        CheckConstraint(
            'annual_exemption_remaining >= 0',
            name='check_iht_exemption_non_negative_remaining'
        ),
        CheckConstraint(
            'carried_forward_from_previous_year >= 0',
            name='check_iht_exemption_non_negative_carried_forward'
        ),
        CheckConstraint(
            'small_gifts_exemption_used >= 0',
            name='check_iht_exemption_non_negative_small_gifts'
        ),
        CheckConstraint(
            'wedding_gifts_exemption_used >= 0',
            name='check_iht_exemption_non_negative_wedding_gifts'
        ),
        Index('idx_iht_exemption_user_id', 'user_id'),
        Index('idx_iht_exemption_user_tax_year', 'user_id', 'tax_year', unique=True),
    )

    @validates('tax_year')
    def validate_tax_year_format(self, key, value):
        """Validate UK tax year format (YYYY/YY)."""
        if value and len(value) == 7 and value[4] == '/':
            return value
        raise ValueError(f"Invalid UK tax year format: {value}. Expected format: YYYY/YY (e.g., 2024/25)")

    def total_exemption_available(self) -> Decimal:
        """
        Calculate total annual exemption available (current + carried forward).

        Returns:
            Decimal: Total exemption available
        """
        remaining = Decimal(str(self.annual_exemption_remaining))
        carried_forward = Decimal(str(self.carried_forward_from_previous_year))
        return remaining + carried_forward

    def apply_exemption(self, amount: Decimal) -> Decimal:
        """
        Apply annual exemption to a gift amount.

        Deducts from current year first, then carried forward amount.

        Args:
            amount: Gift amount to apply exemption to

        Returns:
            Decimal: Amount of exemption actually applied
        """
        amount = Decimal(str(amount))
        applied = Decimal('0.00')

        # Apply current year exemption first
        current_remaining = Decimal(str(self.annual_exemption_remaining))
        if current_remaining > Decimal('0.00'):
            current_applied = min(amount, current_remaining)
            self.annual_exemption_used = Decimal(str(self.annual_exemption_used)) + current_applied
            self.annual_exemption_remaining = current_remaining - current_applied
            applied += current_applied
            amount -= current_applied

        # Apply carried forward exemption if needed
        if amount > Decimal('0.00'):
            carried_forward = Decimal(str(self.carried_forward_from_previous_year))
            if carried_forward > Decimal('0.00'):
                carried_applied = min(amount, carried_forward)
                self.carried_forward_from_previous_year = carried_forward - carried_applied
                applied += carried_applied

        return applied

    def __repr__(self) -> str:
        return (
            f"<IHTExemption(id={self.id}, user_id={self.user_id}, "
            f"tax_year={self.tax_year}, remaining={self.annual_exemption_remaining})>"
        )


# Create additional indexes for Gift and IHTExemption tables
Index(
    "idx_gift_type",
    Gift.gift_type
)

Index(
    "idx_gift_becomes_exempt_date",
    Gift.becomes_exempt_date
)

Index(
    "idx_iht_exemption_tax_year",
    IHTExemption.tax_year
)
