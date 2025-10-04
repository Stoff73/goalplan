"""
UK Pension database models for retirement tracking.

This module provides SQLAlchemy models for:
- UK pension schemes (DC, DB, SIPP, Personal Pension, State Pension)
- Pension contributions with temporal tracking
- Defined Benefit pension details
- Annual Allowance tracking with carry forward
- State Pension forecast tracking

Business logic:
- Scheme reference encryption for security
- Temporal contribution data with effective_from/effective_to
- Annual allowance tracking with MPAA support
- Tapered annual allowance calculations
- Soft delete for audit trail
- Projected value calculations
"""

import uuid
import enum
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any
from dateutil.relativedelta import relativedelta

from sqlalchemy import (
    Column, String, ForeignKey, Numeric, Boolean, DateTime,
    Date, Text, CheckConstraint, Index, Enum as SQLEnum, Integer, JSON
)
from sqlalchemy.orm import relationship, validates

from database import Base
from models.user import GUID
from utils.encryption import encrypt_value, decrypt_value


class PensionType(str, enum.Enum):
    """UK pension type enumeration."""
    OCCUPATIONAL_DB = 'OCCUPATIONAL_DB'  # Defined Benefit
    OCCUPATIONAL_DC = 'OCCUPATIONAL_DC'  # Defined Contribution
    PERSONAL_PENSION = 'PERSONAL_PENSION'
    SIPP = 'SIPP'  # Self-Invested Personal Pension
    STATE_PENSION = 'STATE_PENSION'


class PensionStatus(str, enum.Enum):
    """Pension status enumeration."""
    ACTIVE = 'ACTIVE'
    DEFERRED = 'DEFERRED'
    IN_PAYMENT = 'IN_PAYMENT'
    TRANSFERRED_OUT = 'TRANSFERRED_OUT'


class ContributionFrequency(str, enum.Enum):
    """Contribution frequency enumeration."""
    MONTHLY = 'MONTHLY'
    ANNUAL = 'ANNUAL'
    ONE_OFF = 'ONE_OFF'


class TaxReliefMethod(str, enum.Enum):
    """Tax relief method enumeration."""
    NET_PAY = 'NET_PAY'  # Employer deducts before tax
    RELIEF_AT_SOURCE = 'RELIEF_AT_SOURCE'  # Provider claims basic rate relief


class DBSchemeType(str, enum.Enum):
    """Defined Benefit scheme type enumeration."""
    FINAL_SALARY = 'FINAL_SALARY'
    CAREER_AVERAGE = 'CAREER_AVERAGE'
    CASH_BALANCE = 'CASH_BALANCE'


class IndexationType(str, enum.Enum):
    """DB pension indexation type enumeration."""
    CPI = 'CPI'
    RPI = 'RPI'
    FIXED_PERCENTAGE = 'FIXED_PERCENTAGE'
    NONE = 'NONE'


class InvestmentStrategy(str, enum.Enum):
    """Investment strategy enumeration."""
    CONSERVATIVE = 'CONSERVATIVE'
    BALANCED = 'BALANCED'
    AGGRESSIVE = 'AGGRESSIVE'
    CUSTOM = 'CUSTOM'


class UKPension(Base):
    """
    UK pension scheme tracking with encrypted scheme references.

    Tracks UK pension schemes (DC, DB, SIPP, Personal Pension) with:
    - Encrypted scheme reference for security
    - Current value and projection assumptions
    - MPAA (Money Purchase Annual Allowance) tracking
    - Soft delete for audit trail
    - Relationships to contributions and DB details
    """

    __tablename__ = 'uk_pensions'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Pension Details
    pension_type = Column(
        SQLEnum(PensionType, name='pension_type_enum', create_type=False),
        nullable=False
    )
    provider = Column(String(255), nullable=False)
    scheme_reference_encrypted = Column(Text, nullable=False)  # Encrypted
    employer_name = Column(String(255), nullable=True)  # For occupational pensions

    # Current Value (for DC pensions)
    current_value = Column(
        Numeric(15, 2),
        nullable=True,
        doc="Current pension pot value (DC pensions only)"
    )

    # Dates
    start_date = Column(Date, nullable=False)
    expected_retirement_date = Column(Date, nullable=False)

    # Investment Strategy (DC pensions)
    investment_strategy = Column(
        SQLEnum(InvestmentStrategy, name='investment_strategy_enum', create_type=False),
        nullable=True
    )
    assumed_growth_rate = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Assumed annual growth rate (percentage)"
    )
    assumed_inflation_rate = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Assumed annual inflation rate (percentage)"
    )

    # MPAA (Money Purchase Annual Allowance)
    mpaa_triggered = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether MPAA has been triggered (reduces allowance to £10,000)"
    )
    mpaa_date = Column(
        Date,
        nullable=True,
        doc="Date when MPAA was triggered"
    )

    # Status
    status = Column(
        SQLEnum(PensionStatus, name='pension_status_enum', create_type=False),
        default=PensionStatus.ACTIVE,
        nullable=False,
        index=True
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
    user = relationship("User", back_populates="uk_pensions")
    contributions = relationship(
        "UKPensionContribution",
        back_populates="pension",
        cascade="all, delete-orphan"
    )
    db_details = relationship(
        "UKPensionDBDetails",
        back_populates="pension",
        uselist=False,  # One-to-one
        cascade="all, delete-orphan"
    )

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'current_value IS NULL OR current_value >= 0',
            name='check_uk_pension_non_negative_value'
        ),
        CheckConstraint(
            'expected_retirement_date > start_date',
            name='check_uk_pension_valid_retirement_date'
        ),
        CheckConstraint(
            'assumed_growth_rate IS NULL OR assumed_growth_rate >= 0',
            name='check_uk_pension_non_negative_growth'
        ),
        CheckConstraint(
            'assumed_inflation_rate IS NULL OR assumed_inflation_rate >= 0',
            name='check_uk_pension_non_negative_inflation'
        ),
        Index('idx_uk_pension_user_status', 'user_id', 'status'),
        Index('idx_uk_pension_user_deleted', 'user_id', 'is_deleted'),
    )

    def set_scheme_reference(self, scheme_reference: str) -> None:
        """
        Encrypt and set scheme reference.

        Args:
            scheme_reference: Plain text scheme reference
        """
        self.scheme_reference_encrypted = encrypt_value(scheme_reference)

    def get_scheme_reference(self) -> str:
        """
        Decrypt and return scheme reference.

        Returns:
            str: Decrypted scheme reference
        """
        return decrypt_value(self.scheme_reference_encrypted)

    def calculate_projected_value(
        self,
        target_date: Optional[date] = None
    ) -> Optional[Decimal]:
        """
        Calculate projected pension value at target date.

        For DC pensions only. Uses compound interest with contributions.

        Args:
            target_date: Target date for projection (defaults to expected_retirement_date)

        Returns:
            Decimal: Projected value, or None if not applicable (e.g., DB pension)
        """
        if self.pension_type == PensionType.OCCUPATIONAL_DB:
            return None

        if not self.current_value or not self.assumed_growth_rate:
            return None

        if target_date is None:
            target_date = self.expected_retirement_date

        years = Decimal(str((target_date - date.today()).days / 365.25))
        if years <= 0:
            return self.current_value

        # Simple projection: current_value * (1 + growth_rate)^years
        # Note: This doesn't include future contributions - that would require
        # iterating through contribution records
        growth_rate_decimal = Decimal(str(self.assumed_growth_rate)) / Decimal('100')
        growth_multiplier = (Decimal('1') + growth_rate_decimal) ** years
        return Decimal(str(self.current_value)) * growth_multiplier

    def __repr__(self) -> str:
        return (
            f"<UKPension(id={self.id}, user_id={self.user_id}, "
            f"type={self.pension_type}, provider={self.provider})>"
        )


class UKPensionContribution(Base):
    """
    UK pension contribution tracking with temporal data support.

    Tracks pension contributions over time with:
    - Employee, employer, and personal contributions
    - Contribution frequency and tax relief method
    - Tax year allocation
    - Temporal data (effective_from/effective_to) for historical tracking
    """

    __tablename__ = 'uk_pension_contributions'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    pension_id = Column(
        GUID,
        ForeignKey('uk_pensions.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Contribution Amounts
    employee_contribution = Column(
        Numeric(10, 2),
        nullable=True,
        default=Decimal('0.00'),
        doc="Employee contribution amount per period"
    )
    employer_contribution = Column(
        Numeric(10, 2),
        nullable=True,
        default=Decimal('0.00'),
        doc="Employer contribution amount per period"
    )
    personal_contribution = Column(
        Numeric(10, 2),
        nullable=True,
        default=Decimal('0.00'),
        doc="Personal contribution amount per period (e.g., SIPP)"
    )

    # Contribution Details
    frequency = Column(
        SQLEnum(ContributionFrequency, name='contribution_frequency_enum', create_type=False),
        nullable=False
    )
    tax_relief_method = Column(
        SQLEnum(TaxReliefMethod, name='tax_relief_method_enum', create_type=False),
        nullable=True
    )

    # Dates
    contribution_date = Column(
        Date,
        nullable=False,
        doc="Date of contribution or start of contribution period"
    )
    tax_year = Column(
        String(7),
        nullable=False,
        doc="UK tax year in format YYYY/YY (e.g., 2024/25)"
    )

    # Temporal Data Support
    effective_from = Column(
        Date,
        nullable=False,
        doc="Start date when this contribution rate is effective"
    )
    effective_to = Column(
        Date,
        nullable=True,
        doc="End date when this contribution rate stops (NULL = current)"
    )

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    pension = relationship("UKPension", back_populates="contributions")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'employee_contribution IS NULL OR employee_contribution >= 0',
            name='check_contribution_non_negative_employee'
        ),
        CheckConstraint(
            'employer_contribution IS NULL OR employer_contribution >= 0',
            name='check_contribution_non_negative_employer'
        ),
        CheckConstraint(
            'personal_contribution IS NULL OR personal_contribution >= 0',
            name='check_contribution_non_negative_personal'
        ),
        CheckConstraint(
            'effective_to IS NULL OR effective_to >= effective_from',
            name='check_contribution_valid_effective_dates'
        ),
        Index('idx_contribution_pension_tax_year', 'pension_id', 'tax_year'),
        Index('idx_contribution_effective_dates', 'pension_id', 'effective_from', 'effective_to'),
    )

    @validates('tax_year')
    def validate_tax_year_format(self, key, value):
        """Validate UK tax year format (YYYY/YY)."""
        if value and len(value) == 7 and value[4] == '/':
            return value
        raise ValueError(f"Invalid UK tax year format: {value}. Expected format: YYYY/YY (e.g., 2024/25)")

    @property
    def total_contribution(self) -> Decimal:
        """Calculate total contribution from all sources."""
        employee = Decimal(str(self.employee_contribution or 0))
        employer = Decimal(str(self.employer_contribution or 0))
        personal = Decimal(str(self.personal_contribution or 0))
        return employee + employer + personal

    def __repr__(self) -> str:
        return (
            f"<UKPensionContribution(id={self.id}, pension_id={self.pension_id}, "
            f"total={self.total_contribution}, tax_year={self.tax_year})>"
        )


class UKPensionDBDetails(Base):
    """
    Defined Benefit pension details (one-to-one with UKPension).

    Tracks DB pension scheme details with:
    - Accrual rate and pensionable service
    - Scheme type (final salary, career average, cash balance)
    - Normal retirement age
    - Guaranteed pension and spouse benefits
    - Indexation details
    """

    __tablename__ = 'uk_pension_db_details'

    # Primary Key (one-to-one with uk_pensions)
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    pension_id = Column(
        GUID,
        ForeignKey('uk_pensions.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )

    # Accrual Details
    accrual_rate = Column(
        String(10),
        nullable=False,
        doc="Accrual rate (e.g., '1/60', '1/80')"
    )
    pensionable_service_years = Column(
        Numeric(5, 2),
        nullable=False,
        doc="Years of pensionable service"
    )

    # Scheme Details
    scheme_type = Column(
        SQLEnum(DBSchemeType, name='db_scheme_type_enum', create_type=False),
        nullable=False
    )
    normal_retirement_age = Column(
        Integer,
        nullable=False,
        doc="Normal retirement age for this scheme"
    )

    # Benefit Details
    guaranteed_pension_amount = Column(
        Numeric(10, 2),
        nullable=True,
        doc="Guaranteed annual pension amount at NRA"
    )
    spouse_pension_percentage = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Spouse pension as percentage of member pension (e.g., 50.00)"
    )
    lump_sum_entitlement = Column(
        Numeric(10, 2),
        nullable=True,
        doc="Tax-free lump sum entitlement (if applicable)"
    )

    # Indexation
    indexation_type = Column(
        SQLEnum(IndexationType, name='indexation_type_enum', create_type=False),
        nullable=False,
        default=IndexationType.CPI
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
    pension = relationship("UKPension", back_populates="db_details")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'pensionable_service_years >= 0',
            name='check_db_non_negative_service'
        ),
        CheckConstraint(
            'normal_retirement_age >= 55',
            name='check_db_valid_retirement_age'
        ),
        CheckConstraint(
            'guaranteed_pension_amount IS NULL OR guaranteed_pension_amount >= 0',
            name='check_db_non_negative_pension'
        ),
        CheckConstraint(
            'spouse_pension_percentage IS NULL OR (spouse_pension_percentage >= 0 AND spouse_pension_percentage <= 100)',
            name='check_db_valid_spouse_percentage'
        ),
        CheckConstraint(
            'lump_sum_entitlement IS NULL OR lump_sum_entitlement >= 0',
            name='check_db_non_negative_lump_sum'
        ),
        Index('idx_db_details_pension_id', 'pension_id'),
    )

    @validates('accrual_rate')
    def validate_accrual_rate_format(self, key, value):
        """Validate accrual rate format (e.g., '1/60', '1/80')."""
        if value and '/' in value:
            parts = value.split('/')
            if len(parts) == 2:
                try:
                    numerator = int(parts[0])
                    denominator = int(parts[1])
                    if numerator > 0 and denominator > 0:
                        return value
                except ValueError:
                    pass
        raise ValueError(f"Invalid accrual rate format: {value}. Expected format: '1/60' or '1/80'")

    def __repr__(self) -> str:
        return (
            f"<UKPensionDBDetails(id={self.id}, pension_id={self.pension_id}, "
            f"scheme_type={self.scheme_type}, accrual_rate={self.accrual_rate})>"
        )


class AnnualAllowanceTracking(Base):
    """
    Annual Allowance tracking with carry forward support.

    Tracks UK pension annual allowance usage with:
    - Total contributions for the tax year
    - Annual allowance limit (standard or tapered)
    - Carry forward from previous 3 years
    - MPAA tracking
    - Excess contribution calculations
    """

    __tablename__ = 'annual_allowance_tracking'

    # Primary Key
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
        doc="UK tax year in format YYYY/YY (e.g., 2024/25)"
    )

    # Contributions
    total_contributions = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Total pension contributions for the tax year"
    )

    # Annual Allowance
    annual_allowance_limit = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('60000.00'),
        doc="Annual allowance limit (£60,000 standard, or tapered)"
    )

    # Carry Forward (previous 3 years unused allowance)
    carry_forward_available = Column(
        JSON,
        nullable=True,
        doc="Carry forward from previous 3 years: {year: amount}"
    )

    # Taper Calculation (high earners)
    tapered_allowance = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether annual allowance is tapered (adjusted income > £260,000)"
    )
    adjusted_income = Column(
        Numeric(15, 2),
        nullable=True,
        doc="Adjusted income for taper calculation"
    )

    # Usage
    allowance_used = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Amount of annual allowance used"
    )
    allowance_remaining = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('60000.00'),
        doc="Remaining annual allowance (including carry forward)"
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
    user = relationship("User", back_populates="annual_allowance_records")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'total_contributions >= 0',
            name='check_aa_non_negative_contributions'
        ),
        CheckConstraint(
            'annual_allowance_limit >= 0',
            name='check_aa_non_negative_limit'
        ),
        CheckConstraint(
            'allowance_used >= 0',
            name='check_aa_non_negative_used'
        ),
        CheckConstraint(
            'adjusted_income IS NULL OR adjusted_income >= 0',
            name='check_aa_non_negative_income'
        ),
        Index('idx_aa_user_tax_year', 'user_id', 'tax_year', unique=True),
    )

    @validates('tax_year')
    def validate_tax_year_format(self, key, value):
        """Validate UK tax year format (YYYY/YY)."""
        if value and len(value) == 7 and value[4] == '/':
            return value
        raise ValueError(f"Invalid UK tax year format: {value}. Expected format: YYYY/YY (e.g., 2024/25)")

    def calculate_excess(self) -> Decimal:
        """
        Calculate excess contributions over annual allowance (including carry forward).

        Returns:
            Decimal: Excess amount (0 if no excess)
        """
        excess = Decimal(str(self.total_contributions)) - Decimal(str(self.allowance_remaining))
        return max(Decimal('0.00'), excess)

    def __repr__(self) -> str:
        return (
            f"<AnnualAllowanceTracking(id={self.id}, user_id={self.user_id}, "
            f"tax_year={self.tax_year}, used={self.allowance_used})>"
        )


class StatePensionForecast(Base):
    """
    UK State Pension forecast tracking.

    Tracks State Pension entitlement with:
    - Qualifying years and years needed for full pension
    - Estimated weekly and annual amounts
    - State Pension Age based on DOB
    """

    __tablename__ = 'state_pension_forecast'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,  # One forecast per user
        index=True
    )

    # Forecast Data
    forecast_date = Column(
        Date,
        nullable=False,
        doc="Date when forecast was obtained"
    )
    qualifying_years = Column(
        Integer,
        nullable=False,
        doc="Number of qualifying NI years"
    )
    years_needed_for_full = Column(
        Integer,
        nullable=False,
        default=35,
        doc="Years needed for full State Pension (typically 35)"
    )

    # Estimated Amounts
    estimated_weekly_amount = Column(
        Numeric(10, 2),
        nullable=False,
        doc="Estimated State Pension weekly amount"
    )
    estimated_annual_amount = Column(
        Numeric(10, 2),
        nullable=False,
        doc="Estimated State Pension annual amount"
    )

    # State Pension Age
    state_pension_age = Column(
        Integer,
        nullable=False,
        doc="State Pension Age based on date of birth"
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
    user = relationship("User", back_populates="state_pension_forecast")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'qualifying_years >= 0',
            name='check_sp_non_negative_qualifying_years'
        ),
        CheckConstraint(
            'years_needed_for_full > 0',
            name='check_sp_positive_years_needed'
        ),
        CheckConstraint(
            'estimated_weekly_amount >= 0',
            name='check_sp_non_negative_weekly_amount'
        ),
        CheckConstraint(
            'estimated_annual_amount >= 0',
            name='check_sp_non_negative_annual_amount'
        ),
        CheckConstraint(
            'state_pension_age >= 55',
            name='check_sp_valid_pension_age'
        ),
        Index('idx_sp_user_id', 'user_id'),
    )

    @property
    def years_to_full_pension(self) -> int:
        """Calculate years still needed for full State Pension."""
        return max(0, self.years_needed_for_full - self.qualifying_years)

    @property
    def forecast_age(self) -> bool:
        """Check if forecast data is outdated (>1 year old)."""
        return (date.today() - self.forecast_date).days > 365

    def __repr__(self) -> str:
        return (
            f"<StatePensionForecast(id={self.id}, user_id={self.user_id}, "
            f"qualifying_years={self.qualifying_years}, "
            f"estimated_annual={self.estimated_annual_amount})>"
        )


# Create additional indexes for performance
Index(
    "idx_uk_pension_type",
    UKPension.pension_type
)

Index(
    "idx_uk_pension_mpaa",
    UKPension.mpaa_triggered
)

Index(
    "idx_contribution_date",
    UKPensionContribution.contribution_date
)

Index(
    "idx_aa_tapered",
    AnnualAllowanceTracking.tapered_allowance
)


class RetirementProjection(Base):
    """
    Retirement income projection with temporal tracking.

    Tracks retirement income projections with:
    - Target retirement age and income needs
    - Income from multiple sources (state pension, DB, DC drawdown, other)
    - Income gap analysis
    - On-track status determination
    - Growth and inflation assumptions
    - Temporal data support for historical projections
    """

    __tablename__ = 'retirement_projections'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Projection Details
    projection_date = Column(
        Date,
        nullable=False,
        doc="Date when this projection was calculated"
    )
    target_retirement_age = Column(
        Integer,
        nullable=False,
        doc="Target retirement age for this projection"
    )

    # Projected Pot
    projected_total_pot = Column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Total projected pension pot at retirement (DC only)"
    )

    # Income Requirements
    annual_income_needed = Column(
        Numeric(10, 2),
        nullable=False,
        doc="Annual income needed in retirement"
    )

    # Income Sources
    state_pension_income = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Projected State Pension annual income"
    )
    db_pension_income = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Projected DB pension annual income"
    )
    dc_drawdown_income = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Projected DC drawdown income (sustainable withdrawal)"
    )
    other_income = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Other retirement income (rental, investments, etc.)"
    )

    # Calculated Fields
    total_projected_income = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Total projected annual income from all sources"
    )
    income_gap = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Income gap (negative = shortfall, positive = surplus)"
    )
    on_track = Column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether retirement planning is on track (income gap >= 0)"
    )

    # Assumptions
    growth_assumptions = Column(
        JSON,
        nullable=True,
        doc="Growth rate assumptions for different asset classes"
    )
    inflation_rate = Column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal('2.50'),
        doc="Assumed annual inflation rate (percentage)"
    )

    # Temporal Data Support
    effective_from = Column(
        Date,
        nullable=False,
        doc="Start date when this projection is effective"
    )
    effective_to = Column(
        Date,
        nullable=True,
        doc="End date when this projection stops (NULL = current)"
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
    user = relationship("User", back_populates="retirement_projections")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'target_retirement_age >= 55',
            name='check_projection_valid_retirement_age'
        ),
        CheckConstraint(
            'projected_total_pot >= 0',
            name='check_projection_non_negative_pot'
        ),
        CheckConstraint(
            'annual_income_needed > 0',
            name='check_projection_positive_income_needed'
        ),
        CheckConstraint(
            'state_pension_income >= 0',
            name='check_projection_non_negative_state_pension'
        ),
        CheckConstraint(
            'db_pension_income >= 0',
            name='check_projection_non_negative_db_pension'
        ),
        CheckConstraint(
            'dc_drawdown_income >= 0',
            name='check_projection_non_negative_dc_drawdown'
        ),
        CheckConstraint(
            'other_income >= 0',
            name='check_projection_non_negative_other_income'
        ),
        CheckConstraint(
            'total_projected_income >= 0',
            name='check_projection_non_negative_total_income'
        ),
        CheckConstraint(
            'inflation_rate >= 0',
            name='check_projection_non_negative_inflation'
        ),
        CheckConstraint(
            'effective_to IS NULL OR effective_to >= effective_from',
            name='check_projection_valid_effective_dates'
        ),
        Index('idx_projection_user_id', 'user_id'),
        Index('idx_projection_user_date', 'user_id', 'projection_date'),
        Index('idx_projection_effective_dates', 'user_id', 'effective_from', 'effective_to'),
    )

    def calculate_income_gap(self) -> Decimal:
        """
        Calculate income gap (surplus or shortfall).

        Returns:
            Decimal: Income gap amount (positive = surplus, negative = shortfall)
        """
        total_income = (
            Decimal(str(self.state_pension_income or 0)) +
            Decimal(str(self.db_pension_income or 0)) +
            Decimal(str(self.dc_drawdown_income or 0)) +
            Decimal(str(self.other_income or 0))
        )
        income_needed = Decimal(str(self.annual_income_needed or 0))
        return total_income - income_needed

    def is_on_track(self) -> bool:
        """
        Determine if retirement planning is on track.

        Returns:
            bool: True if projected income meets or exceeds needs
        """
        return self.calculate_income_gap() >= Decimal('0.00')

    def __repr__(self) -> str:
        return (
            f"<RetirementProjection(id={self.id}, user_id={self.user_id}, "
            f"projection_date={self.projection_date}, on_track={self.on_track})>"
        )


class DrawdownScenario(Base):
    """
    Pension drawdown scenario modeling.

    Tracks different drawdown scenarios for DC pensions with:
    - Scenario name and drawdown rate
    - Start age and projected annual income
    - Pot depletion age estimation
    - Tax implications
    - Assumptions used
    """

    __tablename__ = 'drawdown_scenarios'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    pension_id = Column(
        GUID,
        ForeignKey('uk_pensions.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Scenario Details
    scenario_name = Column(
        String(100),
        nullable=False,
        doc="Descriptive name for this scenario (e.g., 'Conservative', 'Aggressive')"
    )
    drawdown_rate = Column(
        Numeric(5, 2),
        nullable=False,
        doc="Annual drawdown rate as percentage (2-8%)"
    )
    start_age = Column(
        Integer,
        nullable=False,
        doc="Age when drawdown starts"
    )

    # Projected Results
    projected_annual_income = Column(
        Numeric(10, 2),
        nullable=False,
        doc="Projected annual income from this drawdown scenario"
    )
    pot_depletion_age = Column(
        Integer,
        nullable=True,
        doc="Estimated age when pot runs out (NULL if pot doesn't deplete)"
    )

    # Details
    tax_implications = Column(
        JSON,
        nullable=True,
        doc="Tax implications of this drawdown scenario"
    )
    assumptions = Column(
        JSON,
        nullable=True,
        doc="Assumptions used in this scenario (growth, inflation, etc.)"
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
    pension = relationship("UKPension", backref="drawdown_scenarios")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'drawdown_rate >= 2 AND drawdown_rate <= 8',
            name='check_drawdown_valid_rate'
        ),
        CheckConstraint(
            'start_age >= 55 AND start_age <= 75',
            name='check_drawdown_valid_start_age'
        ),
        CheckConstraint(
            'projected_annual_income >= 0',
            name='check_drawdown_non_negative_income'
        ),
        CheckConstraint(
            'pot_depletion_age IS NULL OR pot_depletion_age >= start_age',
            name='check_drawdown_valid_depletion_age'
        ),
        Index('idx_drawdown_pension_id', 'pension_id'),
        Index('idx_drawdown_pension_scenario', 'pension_id', 'scenario_name'),
    )

    @validates('drawdown_rate')
    def validate_drawdown_rate(self, key, value):
        """Validate drawdown rate is between 2% and 8%."""
        value_decimal = Decimal(str(value))
        if value_decimal < Decimal('2.00') or value_decimal > Decimal('8.00'):
            raise ValueError(f"Drawdown rate must be between 2% and 8%. Got: {value}%")
        return value

    @validates('start_age')
    def validate_start_age(self, key, value):
        """Validate start age is between 55 and 75."""
        if value < 55 or value > 75:
            raise ValueError(f"Start age must be between 55 and 75. Got: {value}")
        return value

    def calculate_pot_depletion(
        self,
        current_pot_value: Decimal,
        growth_rate: Decimal = Decimal('5.00'),
        inflation_rate: Decimal = Decimal('2.50'),
        life_expectancy: int = 95
    ) -> Optional[int]:
        """
        Calculate estimated age when pension pot depletes.

        Simulates annual drawdown with investment growth and inflation.

        Args:
            current_pot_value: Current pension pot value
            growth_rate: Assumed annual growth rate (percentage)
            inflation_rate: Assumed annual inflation rate (percentage)
            life_expectancy: Maximum age to simulate to

        Returns:
            int: Age when pot depletes, or None if pot lasts until life expectancy
        """
        pot_value = Decimal(str(current_pot_value))
        annual_withdrawal = Decimal(str(self.projected_annual_income))
        growth_decimal = Decimal(str(growth_rate)) / Decimal('100')
        inflation_decimal = Decimal(str(inflation_rate)) / Decimal('100')

        current_age = self.start_age

        while current_age < life_expectancy:
            # Apply withdrawal
            pot_value -= annual_withdrawal

            # Check if pot is depleted
            if pot_value <= Decimal('0'):
                return current_age

            # Apply growth
            pot_value *= (Decimal('1') + growth_decimal)

            # Increase withdrawal with inflation
            annual_withdrawal *= (Decimal('1') + inflation_decimal)

            current_age += 1

        # Pot lasts until life expectancy
        return None

    def __repr__(self) -> str:
        return (
            f"<DrawdownScenario(id={self.id}, pension_id={self.pension_id}, "
            f"scenario_name={self.scenario_name}, drawdown_rate={self.drawdown_rate}%)>"
        )


# Create additional indexes for performance
Index(
    "idx_retirement_projection_date",
    RetirementProjection.projection_date
)

Index(
    "idx_retirement_projection_on_track",
    RetirementProjection.on_track
)

Index(
    "idx_drawdown_scenario_name",
    DrawdownScenario.scenario_name
)


# ============================================================================
# SA RETIREMENT FUND MODELS
# ============================================================================

class SAFundType(str, enum.Enum):
    """SA retirement fund type enumeration."""
    PENSION_FUND = 'PENSION_FUND'
    PROVIDENT_FUND = 'PROVIDENT_FUND'
    RETIREMENT_ANNUITY = 'RETIREMENT_ANNUITY'
    PRESERVATION_FUND = 'PRESERVATION_FUND'


class SAFundStatus(str, enum.Enum):
    """SA fund status enumeration."""
    ACTIVE = 'ACTIVE'
    PRESERVED = 'PRESERVED'
    PAID_OUT = 'PAID_OUT'
    TRANSFERRED = 'TRANSFERRED'


class SARetirementFund(Base):
    """
    South African retirement fund tracking.

    Tracks SA retirement funds (Pension, Provident, RA, Preservation) with:
    - Encrypted fund number for security
    - Current value and contribution tracking
    - Section 10C tax deduction eligibility
    - Retirement age and investment strategy
    - Regulation 28 compliance
    - Soft delete for audit trail
    """

    __tablename__ = 'sa_retirement_funds'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Fund Details
    fund_type = Column(
        SQLEnum(SAFundType, name='sa_fund_type_enum', create_type=False),
        nullable=False
    )
    provider = Column(String(255), nullable=False)
    fund_name = Column(String(255), nullable=False)
    fund_number_encrypted = Column(Text, nullable=False)  # Encrypted
    employer_name = Column(String(255), nullable=True)  # For pension/provident funds

    # Current Value
    current_value = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Current fund value in ZAR"
    )

    # Dates
    start_date = Column(Date, nullable=False)
    retirement_age = Column(
        Integer,
        nullable=False,
        doc="Target retirement age"
    )

    # Investment Strategy
    investment_strategy = Column(
        SQLEnum(InvestmentStrategy, name='investment_strategy_enum', create_type=False),
        nullable=True
    )
    assumed_growth_rate = Column(
        Numeric(5, 2),
        nullable=True,
        default=Decimal('8.00'),
        doc="Assumed annual growth rate (percentage)"
    )

    # Status
    status = Column(
        SQLEnum(SAFundStatus, name='sa_fund_status_enum', create_type=False),
        default=SAFundStatus.ACTIVE,
        nullable=False,
        index=True
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
    user = relationship("User", back_populates="sa_retirement_funds")
    contributions = relationship(
        "SAFundContribution",
        back_populates="fund",
        cascade="all, delete-orphan"
    )

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'current_value >= 0',
            name='check_sa_fund_non_negative_value'
        ),
        CheckConstraint(
            'retirement_age >= 55 AND retirement_age <= 75',
            name='check_sa_fund_valid_retirement_age'
        ),
        CheckConstraint(
            'assumed_growth_rate IS NULL OR assumed_growth_rate >= 0',
            name='check_sa_fund_non_negative_growth'
        ),
        Index('idx_sa_fund_user_status', 'user_id', 'status'),
        Index('idx_sa_fund_user_deleted', 'user_id', 'is_deleted'),
    )

    def set_fund_number(self, fund_number: str) -> None:
        """
        Encrypt and set fund number.

        Args:
            fund_number: Plain text fund number
        """
        self.fund_number_encrypted = encrypt_value(fund_number)

    def get_fund_number(self) -> str:
        """
        Decrypt and return fund number.

        Returns:
            str: Decrypted fund number
        """
        return decrypt_value(self.fund_number_encrypted)

    def calculate_projected_value(
        self,
        target_age: Optional[int] = None
    ) -> Decimal:
        """
        Calculate projected fund value at target age.

        Uses compound interest with contributions.

        Args:
            target_age: Target age for projection (defaults to retirement_age)

        Returns:
            Decimal: Projected value in ZAR
        """
        if not self.current_value or not self.assumed_growth_rate:
            return self.current_value

        if target_age is None:
            target_age = self.retirement_age

        # Calculate years to target age
        # Note: This requires user's age, which we'd get from context
        # For now, use a simplified calculation
        years = Decimal(str(target_age - 30))  # Placeholder
        if years <= 0:
            return self.current_value

        # Compound growth: current_value * (1 + growth_rate)^years
        growth_rate_decimal = Decimal(str(self.assumed_growth_rate)) / Decimal('100')
        growth_multiplier = (Decimal('1') + growth_rate_decimal) ** years
        return Decimal(str(self.current_value)) * growth_multiplier

    def __repr__(self) -> str:
        return (
            f"<SARetirementFund(id={self.id}, user_id={self.user_id}, "
            f"type={self.fund_type}, provider={self.provider})>"
        )


class SAFundContribution(Base):
    """
    SA retirement fund contribution tracking with temporal data.

    Tracks contributions with:
    - Employee and employer contributions
    - Tax year allocation
    - Section 10C tax deduction tracking
    - Temporal data support (effective_from/effective_to)
    """

    __tablename__ = 'sa_fund_contributions'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    fund_id = Column(
        GUID,
        ForeignKey('sa_retirement_funds.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Contribution Amounts
    employee_contribution = Column(
        Numeric(10, 2),
        nullable=True,
        default=Decimal('0.00'),
        doc="Employee contribution amount per period"
    )
    employer_contribution = Column(
        Numeric(10, 2),
        nullable=True,
        default=Decimal('0.00'),
        doc="Employer contribution amount per period"
    )

    # Contribution Details
    contribution_date = Column(
        Date,
        nullable=False,
        doc="Date of contribution"
    )
    tax_year = Column(
        String(9),
        nullable=False,
        doc="SA tax year in format YYYY/YYYY (e.g., 2024/2025)"
    )

    # Tax Deduction
    tax_deduction_claimed = Column(
        Numeric(10, 2),
        nullable=True,
        default=Decimal('0.00'),
        doc="Section 10C tax deduction claimed for this contribution"
    )

    # Temporal Data Support
    effective_from = Column(
        Date,
        nullable=False,
        doc="Start date when this contribution rate is effective"
    )
    effective_to = Column(
        Date,
        nullable=True,
        doc="End date when this contribution rate stops (NULL = current)"
    )

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    fund = relationship("SARetirementFund", back_populates="contributions")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'employee_contribution IS NULL OR employee_contribution >= 0',
            name='check_sa_contribution_non_negative_employee'
        ),
        CheckConstraint(
            'employer_contribution IS NULL OR employer_contribution >= 0',
            name='check_sa_contribution_non_negative_employer'
        ),
        CheckConstraint(
            'tax_deduction_claimed IS NULL OR tax_deduction_claimed >= 0',
            name='check_sa_contribution_non_negative_deduction'
        ),
        CheckConstraint(
            'effective_to IS NULL OR effective_to >= effective_from',
            name='check_sa_contribution_valid_effective_dates'
        ),
        Index('idx_sa_contribution_fund_tax_year', 'fund_id', 'tax_year'),
        Index('idx_sa_contribution_effective_dates', 'fund_id', 'effective_from', 'effective_to'),
    )

    @validates('tax_year')
    def validate_tax_year_format(self, key, value):
        """Validate SA tax year format (YYYY/YYYY)."""
        if value and len(value) == 9 and value[4] == '/':
            return value
        raise ValueError(f"Invalid SA tax year format: {value}. Expected format: YYYY/YYYY (e.g., 2024/2025)")

    @property
    def total_contribution(self) -> Decimal:
        """Calculate total contribution from all sources."""
        employee = Decimal(str(self.employee_contribution or 0))
        employer = Decimal(str(self.employer_contribution or 0))
        return employee + employer

    def __repr__(self) -> str:
        return (
            f"<SAFundContribution(id={self.id}, fund_id={self.fund_id}, "
            f"total={self.total_contribution}, tax_year={self.tax_year})>"
        )


class SARetirementDeductionLimits(Base):
    """
    SA Section 10C tax deduction limits tracking.

    Tracks annual deduction limits with:
    - Annual limit: 27.5% of income, max R350,000
    - Deductions claimed for the tax year
    - Remaining deduction allowance
    """

    __tablename__ = 'sa_retirement_deduction_limits'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Tax Year
    tax_year = Column(
        String(9),
        nullable=False,
        doc="SA tax year in format YYYY/YYYY (e.g., 2024/2025)"
    )

    # Deduction Limits (Section 10C)
    annual_deduction_limit = Column(
        Numeric(10, 2),
        nullable=False,
        doc="Annual deduction limit: min(income * 0.275, R350,000)"
    )
    deductions_claimed = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Total deductions claimed for the tax year"
    )
    deductions_remaining = Column(
        Numeric(10, 2),
        nullable=False,
        doc="Remaining deduction allowance"
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
    user = relationship("User", back_populates="sa_deduction_limits")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'annual_deduction_limit >= 0',
            name='check_sa_deduction_non_negative_limit'
        ),
        CheckConstraint(
            'deductions_claimed >= 0',
            name='check_sa_deduction_non_negative_claimed'
        ),
        CheckConstraint(
            'deductions_remaining >= 0',
            name='check_sa_deduction_non_negative_remaining'
        ),
        Index('idx_sa_deduction_user_tax_year', 'user_id', 'tax_year', unique=True),
    )

    @validates('tax_year')
    def validate_tax_year_format(self, key, value):
        """Validate SA tax year format (YYYY/YYYY)."""
        if value and len(value) == 9 and value[4] == '/':
            return value
        raise ValueError(f"Invalid SA tax year format: {value}. Expected format: YYYY/YYYY (e.g., 2024/2025)")

    def calculate_excess(self) -> Decimal:
        """
        Calculate excess deductions over annual limit.

        Returns:
            Decimal: Excess amount (0 if no excess)
        """
        excess = Decimal(str(self.deductions_claimed)) - Decimal(str(self.annual_deduction_limit))
        return max(Decimal('0.00'), excess)

    def __repr__(self) -> str:
        return (
            f"<SARetirementDeductionLimits(id={self.id}, user_id={self.user_id}, "
            f"tax_year={self.tax_year}, limit={self.annual_deduction_limit})>"
        )


# Create additional indexes for SA retirement funds
Index(
    "idx_sa_fund_type",
    SARetirementFund.fund_type
)

Index(
    "idx_sa_contribution_date",
    SAFundContribution.contribution_date
)
