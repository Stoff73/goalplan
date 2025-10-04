"""
Life assurance policy models for protection module.

This module provides SQLAlchemy models for:
- Life assurance policies with encrypted policy numbers
- Policy beneficiaries with encrypted PII
- Trust details for UK policies
- Policy document tracking

Business logic:
- Policy number encryption for security
- Beneficiary PII encryption (name, DOB, address)
- Multi-currency support with GBP/ZAR conversion
- Trust structure tracking for IHT planning
- Soft delete for audit trail
- Document storage tracking
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
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, validates

from database import Base
from models.user import GUID
from utils.encryption import encrypt_value, decrypt_value


class ProviderCountry(str, enum.Enum):
    """Policy provider country enumeration."""
    UK = 'UK'
    SA = 'SA'
    OTHER = 'OTHER'


class PolicyType(str, enum.Enum):
    """Life assurance policy type enumeration."""
    TERM = 'TERM'
    WHOLE_OF_LIFE = 'WHOLE_OF_LIFE'
    DECREASING_TERM = 'DECREASING_TERM'
    LEVEL_TERM = 'LEVEL_TERM'
    INCREASING_TERM = 'INCREASING_TERM'
    FAMILY_INCOME_BENEFIT = 'FAMILY_INCOME_BENEFIT'
    OTHER = 'OTHER'


class PremiumFrequency(str, enum.Enum):
    """Premium payment frequency enumeration."""
    MONTHLY = 'MONTHLY'
    ANNUALLY = 'ANNUALLY'
    SINGLE = 'SINGLE'


class TrustType(str, enum.Enum):
    """Trust type enumeration for UK policies."""
    BARE = 'BARE'
    DISCRETIONARY = 'DISCRETIONARY'
    INTEREST_IN_POSSESSION = 'INTEREST_IN_POSSESSION'


class PolicyStatus(str, enum.Enum):
    """Policy status enumeration."""
    ACTIVE = 'ACTIVE'
    LAPSED = 'LAPSED'
    CLAIMED = 'CLAIMED'
    MATURED = 'MATURED'


class BeneficiaryRelationship(str, enum.Enum):
    """Beneficiary relationship enumeration."""
    SPOUSE = 'SPOUSE'
    CHILD = 'CHILD'
    PARENT = 'PARENT'
    SIBLING = 'SIBLING'
    OTHER = 'OTHER'


class DocumentType(str, enum.Enum):
    """Policy document type enumeration."""
    POLICY_DOCUMENT = 'POLICY_DOCUMENT'
    SCHEDULE = 'SCHEDULE'
    TRUST_DEED = 'TRUST_DEED'
    OTHER = 'OTHER'


class Currency(str, enum.Enum):
    """Supported currency codes."""
    GBP = 'GBP'
    ZAR = 'ZAR'
    USD = 'USD'
    EUR = 'EUR'


class LifeAssurancePolicy(Base):
    """
    Life assurance policy tracking with encrypted policy numbers.

    Tracks life assurance policies across multiple countries with:
    - Encrypted policy numbers for security
    - Multi-currency support with GBP/ZAR conversion
    - Trust structure tracking for UK policies
    - Premium and coverage tracking
    - Tax impact calculations (UK IHT, SA Estate Duty)
    - Soft delete for audit trail
    """

    __tablename__ = 'life_assurance_policies'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Policy Details
    policy_number_encrypted = Column(Text, nullable=False)  # Encrypted policy number
    provider = Column(String(255), nullable=False)
    provider_country = Column(
        SQLEnum(ProviderCountry, name='provider_country_enum', create_type=False),
        nullable=False
    )

    policy_type = Column(
        SQLEnum(PolicyType, name='policy_type_enum', create_type=False),
        nullable=False
    )

    # Coverage Amount
    cover_amount = Column(
        Numeric(15, 2),
        nullable=False
    )
    currency = Column(
        SQLEnum(Currency, name='currency_enum', create_type=False),
        nullable=False
    )

    # Calculated conversion fields
    cover_amount_gbp = Column(
        Numeric(15, 2),
        nullable=True
    )
    cover_amount_zar = Column(
        Numeric(15, 2),
        nullable=True
    )

    # Premium Details
    premium_amount = Column(
        Numeric(10, 2),
        nullable=False
    )
    premium_frequency = Column(
        SQLEnum(PremiumFrequency, name='premium_frequency_enum', create_type=False),
        nullable=False
    )

    # Calculated annual premium
    annual_premium = Column(
        Numeric(10, 2),
        nullable=True
    )

    # Policy Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # NULL for whole of life

    # Trust Details (UK policies)
    written_in_trust = Column(Boolean, default=False, nullable=False)
    trust_type = Column(
        SQLEnum(TrustType, name='trust_type_enum', create_type=False),
        nullable=True
    )

    # Additional Coverage
    critical_illness_rider = Column(Boolean, default=False, nullable=False)
    waiver_of_premium = Column(Boolean, default=False, nullable=False)
    indexation_rate = Column(Numeric(5, 2), nullable=True)  # For increasing policies

    # Tax Impact (calculated fields)
    uk_iht_impact = Column(Boolean, nullable=True)
    sa_estate_duty_impact = Column(Boolean, nullable=True)

    # Status
    status = Column(
        SQLEnum(PolicyStatus, name='policy_status_enum', create_type=False),
        default=PolicyStatus.ACTIVE,
        nullable=False,
        index=True
    )

    # Notes and Soft Delete
    notes = Column(Text, nullable=True)
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
    user = relationship("User", back_populates="life_assurance_policies")
    beneficiaries = relationship(
        "PolicyBeneficiary",
        back_populates="policy",
        cascade="all, delete-orphan"
    )
    trust_detail = relationship(
        "PolicyTrustDetail",
        back_populates="policy",
        uselist=False,
        cascade="all, delete-orphan"
    )
    documents = relationship(
        "PolicyDocument",
        back_populates="policy",
        cascade="all, delete-orphan"
    )

    # Table Constraints
    __table_args__ = (
        CheckConstraint('cover_amount > 0', name='check_positive_cover_amount'),
        CheckConstraint('premium_amount >= 0', name='check_positive_premium_amount'),
        Index('idx_life_policy_user_status', 'user_id', 'status'),
        Index('idx_life_policy_user_provider', 'user_id', 'provider'),
    )

    def set_policy_number(self, policy_number: str) -> None:
        """
        Encrypt and set policy number.

        Args:
            policy_number: Plain text policy number
        """
        self.policy_number_encrypted = encrypt_value(policy_number)

    def get_policy_number(self) -> str:
        """
        Decrypt and return policy number.

        Returns:
            str: Decrypted policy number
        """
        return decrypt_value(self.policy_number_encrypted)

    def calculate_annual_premium(self) -> Decimal:
        """
        Calculate annual premium based on frequency.

        Returns:
            Decimal: Annual premium amount
        """
        if self.premium_frequency == PremiumFrequency.MONTHLY:
            return Decimal(str(self.premium_amount)) * 12
        elif self.premium_frequency == PremiumFrequency.ANNUALLY:
            return Decimal(str(self.premium_amount))
        elif self.premium_frequency == PremiumFrequency.SINGLE:
            return Decimal(str(self.premium_amount))
        return Decimal('0.00')

    def calculate_uk_iht_impact(self) -> bool:
        """
        Calculate if policy is in UK estate for IHT purposes.

        Returns:
            bool: True if policy forms part of UK estate for IHT
        """
        # If written in trust, policy is outside estate
        if self.written_in_trust:
            return False

        # If UK policy not in trust, it's in the estate
        if self.provider_country == ProviderCountry.UK:
            return True

        # Other scenarios require more complex logic (domicile, residency, etc.)
        return False

    def calculate_sa_estate_duty_impact(self) -> bool:
        """
        Calculate if policy is in SA estate for estate duty purposes.

        Returns:
            bool: True if policy forms part of SA estate
        """
        # SA policies generally form part of estate unless specific exemptions apply
        if self.provider_country == ProviderCountry.SA:
            return True

        return False

    def __repr__(self) -> str:
        return (
            f"<LifeAssurancePolicy(id={self.id}, user_id={self.user_id}, "
            f"provider={self.provider}, cover={self.cover_amount} {self.currency})>"
        )


class PolicyBeneficiary(Base):
    """
    Policy beneficiary tracking with encrypted PII.

    Tracks beneficiaries for life assurance policies with:
    - Encrypted personal information (name, DOB, address)
    - Relationship tracking
    - Percentage allocation (must total 100% per policy)
    """

    __tablename__ = 'policy_beneficiaries'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    policy_id = Column(
        GUID,
        ForeignKey('life_assurance_policies.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Beneficiary Details (encrypted PII)
    name_encrypted = Column(Text, nullable=False)
    date_of_birth_encrypted = Column(Text, nullable=False)
    address_encrypted = Column(Text, nullable=False)

    beneficiary_relationship = Column(
        SQLEnum(BeneficiaryRelationship, name='beneficiary_relationship_enum', create_type=False),
        nullable=False
    )

    percentage = Column(
        Numeric(5, 2),
        nullable=False
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
    policy = relationship("LifeAssurancePolicy", back_populates="beneficiaries")

    # Table Constraints
    __table_args__ = (
        CheckConstraint('percentage > 0 AND percentage <= 100', name='check_valid_percentage'),
        Index('idx_beneficiary_policy', 'policy_id'),
    )

    def set_name(self, name: str) -> None:
        """Encrypt and set beneficiary name."""
        self.name_encrypted = encrypt_value(name)

    def get_name(self) -> str:
        """Decrypt and return beneficiary name."""
        return decrypt_value(self.name_encrypted)

    def set_date_of_birth(self, dob: date) -> None:
        """Encrypt and set beneficiary date of birth."""
        self.date_of_birth_encrypted = encrypt_value(dob.isoformat())

    def get_date_of_birth(self) -> date:
        """Decrypt and return beneficiary date of birth."""
        dob_str = decrypt_value(self.date_of_birth_encrypted)
        return date.fromisoformat(dob_str)

    def set_address(self, address: str) -> None:
        """Encrypt and set beneficiary address."""
        self.address_encrypted = encrypt_value(address)

    def get_address(self) -> str:
        """Decrypt and return beneficiary address."""
        return decrypt_value(self.address_encrypted)

    def __repr__(self) -> str:
        return (
            f"<PolicyBeneficiary(id={self.id}, policy_id={self.policy_id}, "
            f"relationship={self.beneficiary_relationship}, percentage={self.percentage})>"
        )


class PolicyTrustDetail(Base):
    """
    Policy trust details for UK policies written in trust.

    One-to-one relationship with LifeAssurancePolicy.
    Stores trust structure details for estate planning.
    """

    __tablename__ = 'policy_trust_details'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    policy_id = Column(
        GUID,
        ForeignKey('life_assurance_policies.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,  # One-to-one relationship
        index=True
    )

    # Trust Details
    trust_type = Column(
        SQLEnum(TrustType, name='trust_type_enum', create_type=False),
        nullable=False
    )

    # Store trustees as JSON array for PostgreSQL, or Text for SQLite compatibility
    trustees = Column(Text, nullable=False)  # JSON array stored as text

    trust_beneficiaries = Column(Text, nullable=True)  # Description of trust beneficiaries
    trust_created_date = Column(Date, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    policy = relationship("LifeAssurancePolicy", back_populates="trust_detail")

    def set_trustees(self, trustees: List[str]) -> None:
        """
        Set trustees list as JSON string.

        Args:
            trustees: List of trustee names
        """
        import json
        self.trustees = json.dumps(trustees)

    def get_trustees(self) -> List[str]:
        """
        Get trustees list from JSON string.

        Returns:
            List[str]: List of trustee names
        """
        import json
        if self.trustees:
            return json.loads(self.trustees)
        return []

    def __repr__(self) -> str:
        return (
            f"<PolicyTrustDetail(id={self.id}, policy_id={self.policy_id}, "
            f"trust_type={self.trust_type})>"
        )


class PolicyDocument(Base):
    """
    Policy document tracking.

    Tracks uploaded policy documents with:
    - Document type classification
    - File path and metadata
    - File size and MIME type tracking
    """

    __tablename__ = 'policy_documents'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    policy_id = Column(
        GUID,
        ForeignKey('life_assurance_policies.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Document Details
    document_type = Column(
        SQLEnum(DocumentType, name='document_type_enum', create_type=False),
        nullable=False
    )

    file_path = Column(String(500), nullable=False)
    upload_date = Column(Date, nullable=False, default=date.today)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    policy = relationship("LifeAssurancePolicy", back_populates="documents")

    # Table Constraints
    __table_args__ = (
        CheckConstraint('file_size > 0', name='check_positive_file_size'),
        Index('idx_policy_document_policy', 'policy_id'),
    )

    def __repr__(self) -> str:
        return (
            f"<PolicyDocument(id={self.id}, policy_id={self.policy_id}, "
            f"type={self.document_type})>"
        )


# Create additional indexes for performance
Index(
    "idx_life_policy_status",
    LifeAssurancePolicy.status
)

Index(
    "idx_life_policy_provider_country",
    LifeAssurancePolicy.provider_country
)

Index(
    "idx_life_policy_trust",
    LifeAssurancePolicy.written_in_trust,
    postgresql_where=(LifeAssurancePolicy.written_in_trust.is_(True))
)


class ReminderType(str, enum.Enum):
    """Premium reminder type enumeration."""
    EMAIL = 'EMAIL'
    IN_APP = 'IN_APP'


class CoverageNeedsAnalysis(Base):
    """
    Coverage needs analysis model for gap analysis.

    Stores coverage needs calculations based on user's financial situation:
    - Income replacement needs
    - Outstanding debts
    - Children's education costs
    - Funeral costs
    - Existing assets

    Uses temporal data pattern with effective_from/effective_to to track
    historical coverage analysis over time.

    Business Logic:
        recommended_cover = (annual_income * income_multiplier) +
                           outstanding_debts +
                           (children_count * education_cost_per_child) +
                           funeral_costs -
                           existing_assets

        coverage_gap = recommended_cover - current_total_cover
    """

    __tablename__ = 'coverage_needs_analysis'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Analysis Date
    calculation_date = Column(
        Date,
        nullable=False,
        doc="Date when this analysis was performed"
    )

    # Income Replacement
    annual_income = Column(
        Numeric(15, 2),
        nullable=False,
        doc="User's annual income for replacement calculation"
    )
    income_multiplier = Column(
        Numeric(3, 1),
        default=Decimal('10.0'),
        nullable=False,
        doc="Income multiplier for replacement needs (typically 10)"
    )

    # Financial Obligations
    outstanding_debts = Column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Total outstanding debts (mortgage, loans, etc.)"
    )

    # Children's Education
    children_count = Column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of dependent children"
    )
    education_cost_per_child = Column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Estimated education cost per child"
    )

    # Other Costs
    funeral_costs = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Estimated funeral and final expenses"
    )

    # Existing Resources
    existing_assets = Column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Existing liquid assets available to family"
    )

    # Calculated Fields
    recommended_cover = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Calculated recommended coverage amount"
    )
    current_total_cover = Column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Sum of all active life assurance policies"
    )
    coverage_gap = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Gap between recommended and current cover (can be negative)"
    )

    # Notes
    notes = Column(Text, nullable=True)

    # Temporal Data (for historical tracking)
    effective_from = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        doc="When this analysis becomes valid"
    )
    effective_to = Column(
        DateTime,
        nullable=True,
        doc="When this analysis is superseded (NULL = current)"
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
    user = relationship("User", back_populates="coverage_analyses")

    # Table Constraints
    __table_args__ = (
        CheckConstraint('annual_income >= 0', name='check_positive_annual_income'),
        CheckConstraint('income_multiplier > 0', name='check_positive_income_multiplier'),
        CheckConstraint('outstanding_debts >= 0', name='check_positive_debts'),
        CheckConstraint('children_count >= 0', name='check_positive_children_count'),
        CheckConstraint('education_cost_per_child >= 0', name='check_positive_education_cost'),
        CheckConstraint('funeral_costs >= 0', name='check_positive_funeral_costs'),
        CheckConstraint('existing_assets >= 0', name='check_positive_existing_assets'),
        CheckConstraint('recommended_cover >= 0', name='check_positive_recommended_cover'),
        CheckConstraint(
            'effective_to IS NULL OR effective_to > effective_from',
            name='check_valid_effective_dates'
        ),
        Index('idx_coverage_analysis_user_effective_from', 'user_id', 'effective_from'),
        Index('idx_coverage_analysis_user_effective_to', 'user_id', 'effective_to'),
        Index(
            'idx_coverage_analysis_current',
            'user_id',
            'effective_to',
            postgresql_where="effective_to IS NULL"
        ),
    )

    def calculate_recommended_cover(self) -> Decimal:
        """
        Calculate recommended coverage amount based on family needs analysis.

        Formula:
            (annual_income * income_multiplier) +
            outstanding_debts +
            (children_count * education_cost_per_child) +
            funeral_costs -
            existing_assets

        Returns:
            Decimal: Recommended coverage amount
        """
        income_replacement = Decimal(str(self.annual_income)) * Decimal(str(self.income_multiplier))
        children_education = Decimal(str(self.children_count)) * Decimal(str(self.education_cost_per_child))

        recommended = (
            income_replacement +
            Decimal(str(self.outstanding_debts)) +
            children_education +
            Decimal(str(self.funeral_costs)) -
            Decimal(str(self.existing_assets))
        )

        # Ensure recommended cover is never negative
        return max(recommended, Decimal('0.00'))

    def calculate_coverage_gap(self) -> Decimal:
        """
        Calculate gap between recommended and current cover.

        Returns:
            Decimal: Coverage gap (positive = under-insured, negative = over-insured)
        """
        return Decimal(str(self.recommended_cover)) - Decimal(str(self.current_total_cover))

    @classmethod
    async def get_current_analysis(cls, db_session, user_id: uuid.UUID) -> Optional['CoverageNeedsAnalysis']:
        """
        Get current (active) coverage analysis for a user.

        Args:
            db_session: Database session
            user_id: User UUID

        Returns:
            CoverageNeedsAnalysis or None if no current analysis exists
        """
        from sqlalchemy import select

        query = select(cls).where(
            cls.user_id == user_id,
            cls.effective_to.is_(None)
        )

        result = await db_session.execute(query)
        return result.scalar_one_or_none()

    def __repr__(self) -> str:
        return (
            f"<CoverageNeedsAnalysis(id={self.id}, user_id={self.user_id}, "
            f"recommended={self.recommended_cover}, gap={self.coverage_gap})>"
        )


class PolicyPremiumReminder(Base):
    """
    Premium payment reminder tracking.

    Tracks scheduled reminders for policy premium payments with:
    - Reminder date and type (email or in-app)
    - Sent status tracking
    - Cascade delete when policy is deleted
    """

    __tablename__ = 'policy_premium_reminders'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    policy_id = Column(
        GUID,
        ForeignKey('life_assurance_policies.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Reminder Details
    reminder_date = Column(
        Date,
        nullable=False,
        doc="Date when reminder should be sent"
    )
    reminder_type = Column(
        SQLEnum(ReminderType, name='reminder_type_enum', create_type=False),
        default=ReminderType.IN_APP,
        nullable=False,
        doc="Type of reminder (EMAIL or IN_APP)"
    )

    # Status Tracking
    reminder_sent = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether reminder has been sent"
    )
    sent_at = Column(
        DateTime,
        nullable=True,
        doc="When reminder was actually sent"
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
    policy = relationship(
        "LifeAssurancePolicy",
        backref="premium_reminders"
    )

    # Table Constraints
    __table_args__ = (
        Index('idx_premium_reminder_date_sent', 'reminder_date', 'reminder_sent'),
        Index('idx_premium_reminder_policy', 'policy_id'),
    )

    def __repr__(self) -> str:
        return (
            f"<PolicyPremiumReminder(id={self.id}, policy_id={self.policy_id}, "
            f"date={self.reminder_date}, sent={self.reminder_sent})>"
        )
