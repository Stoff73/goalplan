"""
Pydantic schemas for life assurance policy API requests and responses.

This module provides validation schemas for:
- Creating and updating life assurance policies
- Managing beneficiaries
- Trust detail tracking
- Policy response data

All schemas include comprehensive validation and documentation.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from models.life_assurance import (
    PolicyType,
    ProviderCountry,
    PremiumFrequency,
    TrustType,
    BeneficiaryRelationship,
    PolicyStatus,
    Currency
)


# ============================================================================
# BENEFICIARY SCHEMAS
# ============================================================================

class BeneficiaryCreate(BaseModel):
    """
    Schema for creating a policy beneficiary.

    Validates:
    - Required personal details
    - Valid percentage (0-100)
    - Proper relationship type
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Beneficiary full name (will be encrypted)"
    )

    date_of_birth: date = Field(
        ...,
        description="Beneficiary date of birth (will be encrypted)"
    )

    relationship: BeneficiaryRelationship = Field(
        ...,
        description="Relationship to policyholder"
    )

    percentage: Decimal = Field(
        ...,
        gt=0,
        le=100,
        description="Percentage of benefit (must be > 0 and <= 100)"
    )

    address: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Beneficiary address (will be encrypted)"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "name": "Jane Doe",
                "date_of_birth": "1985-06-15",
                "relationship": "SPOUSE",
                "percentage": 50.00,
                "address": "123 Main St, London, UK"
            }
        }


class BeneficiaryUpdate(BaseModel):
    """
    Schema for updating a beneficiary.

    All fields optional - only provided fields will be updated.
    """

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255
    )

    date_of_birth: Optional[date] = None

    relationship: Optional[BeneficiaryRelationship] = None

    percentage: Optional[Decimal] = Field(
        None,
        gt=0,
        le=100
    )

    address: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500
    )

    class Config:
        from_attributes = True


class BeneficiaryResponse(BaseModel):
    """Schema for beneficiary response data."""

    id: UUID
    name: str
    date_of_birth: date
    relationship: BeneficiaryRelationship
    percentage: Decimal
    address: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# TRUST DETAIL SCHEMAS
# ============================================================================

class TrustDetailCreate(BaseModel):
    """
    Schema for creating trust details.

    Required when written_in_trust = True for UK policies.
    """

    trust_type: TrustType = Field(
        ...,
        description="Type of trust structure"
    )

    trustees: List[str] = Field(
        ...,
        min_length=1,
        description="List of trustee names (at least one required)"
    )

    trust_beneficiaries: Optional[str] = Field(
        None,
        max_length=1000,
        description="Description of trust beneficiaries"
    )

    trust_created_date: date = Field(
        ...,
        description="Date when trust was created"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "trust_type": "DISCRETIONARY",
                "trustees": ["John Smith", "Mary Johnson"],
                "trust_beneficiaries": "Spouse and children",
                "trust_created_date": "2023-01-15"
            }
        }


class TrustDetailResponse(BaseModel):
    """Schema for trust detail response data."""

    id: UUID
    trust_type: TrustType
    trustees: List[str]
    trust_beneficiaries: Optional[str]
    trust_created_date: date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# POLICY SCHEMAS
# ============================================================================

class PolicyCreate(BaseModel):
    """
    Schema for creating a new life assurance policy.

    Validates:
    - Required policy details
    - Positive amounts
    - Valid dates
    - Beneficiary percentage totals
    - Trust requirements
    """

    policy_number: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Policy number (will be encrypted)"
    )

    provider: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Insurance provider name"
    )

    provider_country: ProviderCountry = Field(
        ...,
        description="Country of insurance provider"
    )

    policy_type: PolicyType = Field(
        ...,
        description="Type of life assurance policy"
    )

    cover_amount: Decimal = Field(
        ...,
        gt=0,
        description="Coverage amount in policy currency"
    )

    currency: Currency = Field(
        ...,
        description="Policy currency"
    )

    premium_amount: Decimal = Field(
        ...,
        ge=0,
        description="Premium amount"
    )

    premium_frequency: PremiumFrequency = Field(
        ...,
        description="Premium payment frequency"
    )

    start_date: date = Field(
        ...,
        description="Policy start date"
    )

    end_date: Optional[date] = Field(
        None,
        description="Policy end date (NULL for whole of life)"
    )

    written_in_trust: bool = Field(
        False,
        description="Whether policy is written in trust (UK policies)"
    )

    trust_details: Optional[TrustDetailCreate] = Field(
        None,
        description="Trust details (required if written_in_trust=True)"
    )

    beneficiaries: List[BeneficiaryCreate] = Field(
        ...,
        min_length=1,
        description="List of beneficiaries (at least one required)"
    )

    critical_illness_rider: bool = Field(
        False,
        description="Whether policy includes critical illness rider"
    )

    waiver_of_premium: bool = Field(
        False,
        description="Whether policy includes waiver of premium"
    )

    indexation_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        description="Annual indexation rate for increasing policies"
    )

    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Additional notes about the policy"
    )

    @model_validator(mode='after')
    def validate_beneficiary_percentages(self):
        """Ensure beneficiary percentages sum to exactly 100%."""
        if self.beneficiaries:
            total = sum(b.percentage for b in self.beneficiaries)
            if total != Decimal('100.00'):
                raise ValueError(
                    f"Beneficiary percentages must total exactly 100%. Current total: {total}%"
                )
        return self

    @model_validator(mode='after')
    def validate_end_date_after_start(self):
        """Ensure end date is after start date."""
        if self.end_date and self.start_date >= self.end_date:
            raise ValueError(
                f"End date must be after start date. Start: {self.start_date}, End: {self.end_date}"
            )
        return self

    @model_validator(mode='after')
    def validate_trust_requirements(self):
        """Ensure trust details are provided when written_in_trust=True."""
        if self.written_in_trust and not self.trust_details:
            raise ValueError(
                "Trust details are required when policy is written in trust"
            )
        return self

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "policy_number": "POL123456",
                "provider": "Legal & General",
                "provider_country": "UK",
                "policy_type": "TERM",
                "cover_amount": 500000.00,
                "currency": "GBP",
                "premium_amount": 45.50,
                "premium_frequency": "MONTHLY",
                "start_date": "2023-01-01",
                "end_date": "2043-01-01",
                "written_in_trust": True,
                "trust_details": {
                    "trust_type": "DISCRETIONARY",
                    "trustees": ["John Smith"],
                    "trust_beneficiaries": "Spouse and children",
                    "trust_created_date": "2023-01-01"
                },
                "beneficiaries": [
                    {
                        "name": "Jane Doe",
                        "date_of_birth": "1985-06-15",
                        "relationship": "SPOUSE",
                        "percentage": 100.00,
                        "address": "123 Main St, London, UK"
                    }
                ],
                "critical_illness_rider": True,
                "waiver_of_premium": False,
                "indexation_rate": 2.5,
                "notes": "Family protection policy"
            }
        }


class PolicyUpdate(BaseModel):
    """
    Schema for updating an existing policy.

    All fields optional - only provided fields will be updated.
    Beneficiaries and trust details updated separately.
    """

    provider: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255
    )

    provider_country: Optional[ProviderCountry] = None

    policy_type: Optional[PolicyType] = None

    cover_amount: Optional[Decimal] = Field(
        None,
        gt=0
    )

    currency: Optional[Currency] = None

    premium_amount: Optional[Decimal] = Field(
        None,
        ge=0
    )

    premium_frequency: Optional[PremiumFrequency] = None

    start_date: Optional[date] = None

    end_date: Optional[date] = None

    written_in_trust: Optional[bool] = None

    critical_illness_rider: Optional[bool] = None

    waiver_of_premium: Optional[bool] = None

    indexation_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100
    )

    status: Optional[PolicyStatus] = None

    notes: Optional[str] = Field(
        None,
        max_length=2000
    )

    class Config:
        from_attributes = True


class PolicyResponse(BaseModel):
    """
    Schema for policy response data.

    Includes calculated fields and related entities.
    """

    id: UUID
    policy_number: str
    provider: str
    provider_country: ProviderCountry
    policy_type: PolicyType
    cover_amount: Decimal
    currency: Currency
    cover_amount_gbp: Optional[Decimal]
    cover_amount_zar: Optional[Decimal]
    premium_amount: Decimal
    premium_frequency: PremiumFrequency
    annual_premium: Optional[Decimal]
    start_date: date
    end_date: Optional[date]
    written_in_trust: bool
    status: PolicyStatus
    uk_iht_impact: Optional[bool]
    sa_estate_duty_impact: Optional[bool]
    beneficiaries: List[BeneficiaryResponse]
    trust_details: Optional[TrustDetailResponse]
    critical_illness_rider: bool
    waiver_of_premium: bool
    indexation_rate: Optional[Decimal]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# COVERAGE ANALYSIS SCHEMAS
# ============================================================================

class CoverageAnalysisCreate(BaseModel):
    """
    Schema for creating a coverage needs analysis.

    Validates all input values are non-negative and income multiplier is positive.
    """

    annual_income: Decimal = Field(
        ...,
        ge=0,
        description="Annual income for replacement calculation"
    )

    income_multiplier: Decimal = Field(
        Decimal('10.0'),
        gt=0,
        description="Income replacement multiplier (default: 10.0)"
    )

    outstanding_debts: Decimal = Field(
        ...,
        ge=0,
        description="Total outstanding debts (mortgage, loans, etc.)"
    )

    children_count: int = Field(
        ...,
        ge=0,
        description="Number of dependent children"
    )

    education_cost_per_child: Decimal = Field(
        ...,
        ge=0,
        description="Estimated education cost per child"
    )

    funeral_costs: Decimal = Field(
        ...,
        ge=0,
        description="Estimated funeral and final expenses"
    )

    existing_assets: Decimal = Field(
        ...,
        ge=0,
        description="Existing liquid assets available to family"
    )

    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Additional notes about the analysis"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "annual_income": 75000.00,
                "income_multiplier": 10.0,
                "outstanding_debts": 250000.00,
                "children_count": 2,
                "education_cost_per_child": 100000.00,
                "funeral_costs": 5000.00,
                "existing_assets": 50000.00,
                "notes": "Family needs analysis for comprehensive protection"
            }
        }


class CoverageAnalysisResponse(BaseModel):
    """Schema for coverage analysis response data."""

    id: UUID
    calculation_date: date
    annual_income: Decimal
    income_multiplier: Decimal
    outstanding_debts: Decimal
    children_count: int
    education_cost_per_child: Decimal
    funeral_costs: Decimal
    existing_assets: Decimal
    recommended_cover: Decimal
    current_total_cover: Decimal
    coverage_gap: Decimal
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CoverageSummaryResponse(BaseModel):
    """Schema for coverage summary with status and gap analysis."""

    analysis_date: Optional[date] = Field(
        None,
        description="Date of most recent analysis (None if no analysis exists)"
    )

    annual_income: Optional[Decimal] = Field(
        None,
        description="Annual income from analysis (None if no analysis exists)"
    )

    outstanding_debts: Optional[Decimal] = Field(
        None,
        description="Outstanding debts from analysis (None if no analysis exists)"
    )

    children_count: Optional[int] = Field(
        None,
        description="Number of children from analysis (None if no analysis exists)"
    )

    recommended_cover: Decimal = Field(
        ...,
        description="Recommended coverage amount (0 if no analysis)"
    )

    current_total_cover: Decimal = Field(
        ...,
        description="Sum of all active policy coverage"
    )

    coverage_gap: Decimal = Field(
        ...,
        description="Difference between recommended and current (positive = under-insured)"
    )

    gap_percentage: Decimal = Field(
        ...,
        description="Percentage gap relative to recommended cover"
    )

    status: str = Field(
        ...,
        description="Coverage status: ADEQUATE, UNDER_INSURED, or OVER_INSURED"
    )

    policies_count: int = Field(
        ...,
        description="Number of active policies contributing to coverage"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "analysis_date": "2024-01-15",
                "annual_income": 75000.00,
                "outstanding_debts": 250000.00,
                "children_count": 2,
                "recommended_cover": 1005000.00,
                "current_total_cover": 500000.00,
                "coverage_gap": 505000.00,
                "gap_percentage": 50.25,
                "status": "UNDER_INSURED",
                "policies_count": 2
            }
        }
