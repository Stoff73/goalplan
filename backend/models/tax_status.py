"""
Tax status and residency models.

This module contains models for tracking user tax status across UK and SA jurisdictions,
including temporal tax status records, UK SRT data, and SA presence data.

Compliance:
- Temporal data with effective_from/effective_to for historical accuracy
- Point-in-time queries supported
- Audit trail with created_at timestamps
"""

import enum
import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Date, Enum, ForeignKey, String, Integer,
    Numeric, Text, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship

from database import Base
from models.user import GUID


class UKDomicileStatus(str, enum.Enum):
    """
    UK domicile status enumeration.

    - UK_DOMICILE: UK domiciled by origin or choice
    - NON_UK_DOMICILE: Non-UK domiciled
    - DEEMED_DOMICILE: Deemed domiciled for UK tax purposes (15 of 20 years rule)
    """
    UK_DOMICILE = 'uk_domicile'
    NON_UK_DOMICILE = 'non_uk_domicile'
    DEEMED_DOMICILE = 'deemed_domicile'


class UserTaxStatus(Base):
    """
    User tax status model (temporal data).

    Tracks tax residency and domicile status over time with temporal validity.
    Each record has effective_from and effective_to dates to support historical queries.

    Fields:
        id: Primary key (UUID)
        user_id: Foreign key to users table
        effective_from: Start date of this tax status (inclusive)
        effective_to: End date of this tax status (exclusive, NULL = current/active)

        UK tax status:
        uk_tax_resident: Whether user is UK tax resident
        uk_domicile: UK domicile status (uk_domicile/non_uk_domicile/deemed_domicile)
        uk_deemed_domicile_date: Date when deemed domicile started (if applicable)
        uk_split_year_treatment: Whether split year treatment applies
        uk_remittance_basis: Whether using remittance basis (non-doms only)

        SA tax status:
        sa_tax_resident: Whether user is SA tax resident
        sa_ordinarily_resident: Whether user is SA ordinarily resident

        Dual residency:
        dual_resident: Whether user is dual resident (both UK and SA)
        dta_tie_breaker_country: DTA tie-breaker result ('UK' or 'ZA')

        Audit:
        created_at: Record creation timestamp
        updated_at: Last update timestamp

    Relationships:
        user: The user this tax status belongs to

    Constraints:
        - effective_to must be NULL or > effective_from
        - No overlapping effective periods for same user (unique on user_id, effective_from)
        - dta_tie_breaker_country required if dual_resident is True

    Temporal Query Examples:
        Current status: WHERE effective_to IS NULL
        Status at date: WHERE effective_from <= date AND (effective_to IS NULL OR effective_to > date)
        History: ORDER BY effective_from DESC
    """
    __tablename__ = "user_tax_status"

    # Primary Key
    id = Column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique tax status record identifier"
    )

    # Foreign Key
    user_id = Column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="User this tax status belongs to"
    )

    # Temporal Validity
    effective_from = Column(
        Date,
        nullable=False,
        doc="Start date of this tax status (inclusive)"
    )
    effective_to = Column(
        Date,
        nullable=True,
        doc="End date of this tax status (exclusive, NULL = current)"
    )

    # UK Tax Status
    uk_tax_resident = Column(
        Boolean,
        nullable=False,
        doc="Whether user is UK tax resident"
    )
    uk_domicile = Column(
        Enum(UKDomicileStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
        doc="UK domicile status"
    )
    uk_deemed_domicile_date = Column(
        Date,
        nullable=True,
        doc="Date when deemed domicile started (calculated)"
    )
    uk_split_year_treatment = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether split year treatment applies"
    )
    uk_remittance_basis = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether using remittance basis (non-UK domiciled only)"
    )

    # SA Tax Status
    sa_tax_resident = Column(
        Boolean,
        nullable=False,
        doc="Whether user is SA tax resident"
    )
    sa_ordinarily_resident = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether user is SA ordinarily resident"
    )

    # Dual Residency
    dual_resident = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether user is dual resident (both UK and SA)"
    )
    dta_tie_breaker_country = Column(
        String(2),
        nullable=True,
        doc="DTA tie-breaker result ('UK' or 'ZA')"
    )

    # Audit Fields
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Record creation timestamp"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Last update timestamp"
    )

    # Relationships
    user = relationship("User", back_populates="tax_statuses")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="valid_effective_dates"
        ),
        UniqueConstraint(
            "user_id", "effective_from",
            name="no_overlapping_periods"
        ),
        Index(
            "idx_tax_status_user_current",
            "user_id", "effective_to",
            postgresql_where="effective_to IS NULL"
        ),
        Index(
            "idx_tax_status_user_dates",
            "user_id", "effective_from", "effective_to"
        ),
    )

    def __repr__(self) -> str:
        """String representation of UserTaxStatus."""
        return (
            f"<UserTaxStatus(id={self.id}, user_id={self.user_id}, "
            f"effective_from={self.effective_from}, uk_resident={self.uk_tax_resident}, "
            f"sa_resident={self.sa_tax_resident})>"
        )


class UKSRTData(Base):
    """
    UK Statutory Residence Test data model.

    Stores UK SRT calculation data and results for each tax year.
    Used to determine UK tax residency based on days in UK and ties.

    Fields:
        id: Primary key (UUID)
        user_id: Foreign key to users table
        tax_year: UK tax year (format: '2023/24')

        Days in UK:
        days_in_uk: Number of days present in UK during tax year

        Five UK ties:
        family_tie: Spouse/civil partner or minor children resident in UK
        accommodation_tie: Available UK accommodation used during year
        work_tie: 40+ days doing >3 hours work in UK
        ninety_day_tie: 90+ days in UK in either of previous 2 tax years
        country_tie: More days in UK than any other single country

        Calculated result:
        tax_resident: Whether user is UK tax resident
        test_result: Which test determined residency (automatic_overseas/automatic_uk/sufficient_ties)

        Audit:
        created_at: Record creation timestamp

    Constraints:
        - Unique per user per tax year

    Business Rules:
        - Automatic overseas: < 16 days (or < 46 if not resident in previous 3 years)
        - Automatic UK: >= 183 days
        - Sufficient ties: Depends on days and number of ties (arriver vs leaver)
    """
    __tablename__ = "uk_srt_data"

    # Primary Key
    id = Column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique SRT record identifier"
    )

    # Foreign Key
    user_id = Column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="User this SRT data belongs to"
    )

    # Tax Year
    tax_year = Column(
        String(10),
        nullable=False,
        doc="UK tax year (format: '2023/24')"
    )

    # Days in UK
    days_in_uk = Column(
        Integer,
        nullable=False,
        doc="Number of days present in UK during tax year"
    )

    # Five UK Ties
    family_tie = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Family tie: Spouse/civil partner or minor children resident in UK"
    )
    accommodation_tie = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Accommodation tie: Available UK accommodation used during year"
    )
    work_tie = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Work tie: 40+ days doing >3 hours work in UK"
    )
    ninety_day_tie = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="90-day tie: 90+ days in UK in either of previous 2 tax years"
    )
    country_tie = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Country tie: More days in UK than any other single country"
    )

    # Calculated Result
    tax_resident = Column(
        Boolean,
        nullable=True,
        doc="Whether user is UK tax resident (calculated)"
    )
    test_result = Column(
        String(50),
        nullable=True,
        doc="Which test determined residency (automatic_overseas/automatic_uk/sufficient_ties)"
    )

    # Audit Fields
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Record creation timestamp"
    )

    # Relationships
    user = relationship("User", back_populates="uk_srt_records")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "user_id", "tax_year",
            name="unique_srt_per_user_year"
        ),
        Index("idx_srt_user_year", "user_id", "tax_year"),
    )

    def __repr__(self) -> str:
        """String representation of UKSRTData."""
        return (
            f"<UKSRTData(id={self.id}, user_id={self.user_id}, "
            f"tax_year={self.tax_year}, tax_resident={self.tax_resident})>"
        )


class SAPresenceData(Base):
    """
    SA Physical Presence Test data model.

    Stores SA physical presence test calculation data and results for each tax year.
    Used to determine SA tax residency based on days in SA.

    Fields:
        id: Primary key (UUID)
        user_id: Foreign key to users table
        tax_year: SA tax year (format: '2023/24' - March 1 to Feb 28)

        Days in SA:
        days_in_sa: Number of days present in SA during current tax year

        5-year tracking for average calculation:
        year_minus_1_days: Days in SA in previous year (Y-1)
        year_minus_2_days: Days in SA 2 years ago (Y-2)
        year_minus_3_days: Days in SA 3 years ago (Y-3)
        year_minus_4_days: Days in SA 4 years ago (Y-4)

        Calculated result:
        tax_resident: Whether user is SA tax resident
        ordinarily_resident: Whether user is SA ordinarily resident (3+ consecutive years)
        test_result: Which test determined residency (91_day_current/5_year_average/non_resident)
        five_year_average: Average days over 5 years (current + 4 previous)

        Audit:
        created_at: Record creation timestamp

    Constraints:
        - Unique per user per tax year

    Business Rules:
        - Resident if: 91+ days in current year AND 91+ days average over 5 years
        - Ordinarily resident if: Resident for 3+ consecutive years
    """
    __tablename__ = "sa_presence_data"

    # Primary Key
    id = Column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique SA presence record identifier"
    )

    # Foreign Key
    user_id = Column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="User this SA presence data belongs to"
    )

    # Tax Year
    tax_year = Column(
        String(10),
        nullable=False,
        doc="SA tax year (format: '2023/24' - March 1 to Feb 28)"
    )

    # Days in SA
    days_in_sa = Column(
        Integer,
        nullable=False,
        doc="Number of days present in SA during current tax year"
    )

    # 5-Year Tracking
    year_minus_1_days = Column(
        Integer,
        nullable=True,
        doc="Days in SA in previous year (Y-1)"
    )
    year_minus_2_days = Column(
        Integer,
        nullable=True,
        doc="Days in SA 2 years ago (Y-2)"
    )
    year_minus_3_days = Column(
        Integer,
        nullable=True,
        doc="Days in SA 3 years ago (Y-3)"
    )
    year_minus_4_days = Column(
        Integer,
        nullable=True,
        doc="Days in SA 4 years ago (Y-4)"
    )

    # Calculated Result
    tax_resident = Column(
        Boolean,
        nullable=True,
        doc="Whether user is SA tax resident (calculated)"
    )
    ordinarily_resident = Column(
        Boolean,
        nullable=True,
        doc="Whether user is SA ordinarily resident (3+ consecutive years)"
    )
    test_result = Column(
        String(50),
        nullable=True,
        doc="Which test determined residency (91_day_current/5_year_average/non_resident)"
    )
    five_year_average = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Average days over 5 years (current + 4 previous)"
    )

    # Audit Fields
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Record creation timestamp"
    )

    # Relationships
    user = relationship("User", back_populates="sa_presence_records")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "user_id", "tax_year",
            name="unique_sa_presence_per_user_year"
        ),
        Index("idx_sa_presence_user_year", "user_id", "tax_year"),
    )

    def __repr__(self) -> str:
        """String representation of SAPresenceData."""
        return (
            f"<SAPresenceData(id={self.id}, user_id={self.user_id}, "
            f"tax_year={self.tax_year}, tax_resident={self.tax_resident})>"
        )
