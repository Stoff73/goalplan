"""
Pydantic schemas for retirement API endpoints.

This module provides request and response schemas for:
- UK Pension CRUD operations
- Pension contributions
- Annual Allowance tracking
- Retirement projections
- Drawdown scenarios
- Annuity quotes

All schemas include validation and serialization logic.
"""

from datetime import date
from decimal import Decimal
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

from models.retirement import (
    PensionType, PensionStatus, ContributionFrequency,
    TaxReliefMethod, DBSchemeType, IndexationType,
    InvestmentStrategy, SAFundType, SAFundStatus
)


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class PensionBase(BaseModel):
    """Base schema with shared pension fields."""
    pension_type: PensionType = Field(..., description="Type of pension scheme")
    provider: str = Field(..., min_length=1, max_length=255, description="Pension provider name")
    scheme_reference: str = Field(..., min_length=1, max_length=100, description="Scheme reference number")
    employer_name: Optional[str] = Field(None, max_length=255, description="Employer name (for occupational pensions)")
    current_value: Optional[Decimal] = Field(None, ge=0, description="Current pension pot value (DC pensions)")
    start_date: date = Field(..., description="Date pension started")
    expected_retirement_date: date = Field(..., description="Expected retirement date")
    investment_strategy: Optional[InvestmentStrategy] = Field(None, description="Investment strategy")
    assumed_growth_rate: Optional[Decimal] = Field(None, ge=0, le=20, description="Assumed annual growth rate (%)")
    assumed_inflation_rate: Optional[Decimal] = Field(None, ge=0, le=10, description="Assumed annual inflation rate (%)")

    @field_validator('expected_retirement_date')
    @classmethod
    def validate_retirement_date(cls, v, info):
        """Ensure retirement date is after start date."""
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError("Expected retirement date must be after start date")
        return v


class DBDetailsBase(BaseModel):
    """Base schema for Defined Benefit pension details."""
    accrual_rate: str = Field(..., description="Accrual rate (e.g., '1/60', '1/80')")
    pensionable_service_years: Decimal = Field(..., ge=0, description="Years of pensionable service")
    scheme_type: DBSchemeType = Field(..., description="DB scheme type")
    normal_retirement_age: int = Field(..., ge=55, le=75, description="Normal retirement age")
    guaranteed_pension_amount: Optional[Decimal] = Field(None, ge=0, description="Guaranteed annual pension")
    spouse_pension_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Spouse pension percentage")
    lump_sum_entitlement: Optional[Decimal] = Field(None, ge=0, description="Tax-free lump sum entitlement")
    indexation_type: IndexationType = Field(IndexationType.CPI, description="Indexation type")

    @field_validator('accrual_rate')
    @classmethod
    def validate_accrual_rate(cls, v):
        """Validate accrual rate format (e.g., '1/60')."""
        if '/' not in v:
            raise ValueError("Accrual rate must be in format '1/60' or '1/80'")
        parts = v.split('/')
        if len(parts) != 2:
            raise ValueError("Accrual rate must have exactly one '/' separator")
        try:
            numerator = int(parts[0])
            denominator = int(parts[1])
            if numerator <= 0 or denominator <= 0:
                raise ValueError("Accrual rate parts must be positive integers")
        except ValueError:
            raise ValueError("Accrual rate must contain valid integers")
        return v


# ============================================================================
# PENSION CRUD SCHEMAS
# ============================================================================

class PensionCreate(PensionBase):
    """Schema for creating a new pension."""
    mpaa_triggered: bool = Field(False, description="Whether MPAA has been triggered")
    mpaa_date: Optional[date] = Field(None, description="Date when MPAA was triggered")
    db_details: Optional[DBDetailsBase] = Field(None, description="DB pension details (if applicable)")

    @field_validator('db_details')
    @classmethod
    def validate_db_details(cls, v, info):
        """Ensure DB details provided only for DB pensions."""
        if 'pension_type' in info.data:
            pension_type = info.data['pension_type']
            if pension_type == PensionType.OCCUPATIONAL_DB and not v:
                raise ValueError("DB pension details required for OCCUPATIONAL_DB pension type")
            if pension_type != PensionType.OCCUPATIONAL_DB and v:
                raise ValueError("DB pension details only applicable for OCCUPATIONAL_DB pension type")
        return v


class PensionUpdate(BaseModel):
    """Schema for updating an existing pension (all fields optional)."""
    provider: Optional[str] = Field(None, min_length=1, max_length=255)
    employer_name: Optional[str] = Field(None, max_length=255)
    current_value: Optional[Decimal] = Field(None, ge=0)
    expected_retirement_date: Optional[date] = None
    investment_strategy: Optional[InvestmentStrategy] = None
    assumed_growth_rate: Optional[Decimal] = Field(None, ge=0, le=20)
    assumed_inflation_rate: Optional[Decimal] = Field(None, ge=0, le=10)
    mpaa_triggered: Optional[bool] = None
    mpaa_date: Optional[date] = None
    status: Optional[PensionStatus] = None


class DBDetailsResponse(DBDetailsBase):
    """Response schema for DB pension details."""
    id: UUID
    pension_id: UUID

    class Config:
        from_attributes = True


class PensionResponse(BaseModel):
    """Response schema for pension with all details."""
    id: UUID
    user_id: UUID
    pension_type: PensionType
    provider: str
    scheme_reference: str  # Masked (only last 4 digits)
    employer_name: Optional[str]
    current_value: Optional[Decimal]
    start_date: date
    expected_retirement_date: date
    investment_strategy: Optional[InvestmentStrategy]
    assumed_growth_rate: Optional[Decimal]
    assumed_inflation_rate: Optional[Decimal]
    mpaa_triggered: bool
    mpaa_date: Optional[date]
    status: PensionStatus
    projected_value: Optional[Decimal] = Field(None, description="Projected value at retirement")
    db_details: Optional[DBDetailsResponse] = None

    class Config:
        from_attributes = True


# ============================================================================
# CONTRIBUTION SCHEMAS
# ============================================================================

class ContributionCreate(BaseModel):
    """Schema for adding a pension contribution."""
    employee_contribution: Optional[Decimal] = Field(Decimal('0.00'), ge=0, description="Employee contribution")
    employer_contribution: Optional[Decimal] = Field(Decimal('0.00'), ge=0, description="Employer contribution")
    personal_contribution: Optional[Decimal] = Field(Decimal('0.00'), ge=0, description="Personal contribution")
    frequency: ContributionFrequency = Field(..., description="Contribution frequency")
    tax_relief_method: Optional[TaxReliefMethod] = Field(None, description="Tax relief method")
    contribution_date: date = Field(..., description="Contribution date")

    @field_validator('contribution_date')
    @classmethod
    def validate_contribution_date(cls, v):
        """Ensure contribution date is not in future."""
        if v > date.today():
            raise ValueError("Contribution date cannot be in the future")
        return v


class ContributionResponse(BaseModel):
    """Response schema for contribution."""
    id: UUID
    pension_id: UUID
    employee_contribution: Decimal
    employer_contribution: Decimal
    personal_contribution: Decimal
    total_contribution: Decimal
    frequency: ContributionFrequency
    tax_relief_method: Optional[TaxReliefMethod]
    contribution_date: date
    tax_year: str
    effective_from: date
    effective_to: Optional[date]

    class Config:
        from_attributes = True


# ============================================================================
# ANNUAL ALLOWANCE SCHEMAS
# ============================================================================

class AnnualAllowanceResponse(BaseModel):
    """Response schema for Annual Allowance status."""
    tax_year: str = Field(..., description="UK tax year (YYYY/YY)")
    total_contributions: Decimal = Field(..., description="Total contributions for the year")
    annual_allowance_limit: Decimal = Field(..., description="Annual allowance limit")
    allowance_used: Decimal = Field(..., description="Amount of allowance used")
    allowance_remaining: Decimal = Field(..., description="Remaining allowance")
    carry_forward_available: Optional[Dict[str, Decimal]] = Field(None, description="Carry forward by year")
    tapered_allowance: bool = Field(..., description="Whether allowance is tapered")
    mpaa_applies: bool = Field(False, description="Whether MPAA applies")
    excess_contributions: Decimal = Field(Decimal('0.00'), description="Excess over allowance")

    class Config:
        from_attributes = True


# ============================================================================
# TOTAL POT SCHEMAS
# ============================================================================

class PensionPotSummary(BaseModel):
    """Summary of a single pension pot."""
    pension_id: UUID
    pension_type: PensionType
    provider: str
    current_value: Decimal
    projected_value: Optional[Decimal]


class TotalPotResponse(BaseModel):
    """Response schema for total pension pot."""
    total_current_value: Decimal = Field(..., description="Total current value across all pensions")
    total_projected_value: Decimal = Field(..., description="Total projected value at retirement")
    pensions: list[PensionPotSummary] = Field(..., description="Breakdown by pension")
    state_pension_annual: Optional[Decimal] = Field(None, description="State pension annual amount")


# ============================================================================
# PROJECTION SCHEMAS
# ============================================================================

class ProjectionCreate(BaseModel):
    """Schema for creating a retirement projection."""
    target_retirement_age: int = Field(..., ge=55, le=75, description="Target retirement age")
    annual_income_needed: Decimal = Field(..., gt=0, description="Annual income needed in retirement")
    growth_assumptions: Optional[Dict[str, Decimal]] = Field(None, description="Growth rate assumptions")
    inflation_rate: Decimal = Field(Decimal('2.50'), ge=0, le=10, description="Assumed inflation rate (%)")


class IncomeBreakdown(BaseModel):
    """Income breakdown by source."""
    state_pension_income: Decimal = Field(Decimal('0.00'), description="State pension annual income")
    db_pension_income: Decimal = Field(Decimal('0.00'), description="DB pension annual income")
    dc_drawdown_income: Decimal = Field(Decimal('0.00'), description="DC drawdown income")
    other_income: Decimal = Field(Decimal('0.00'), description="Other retirement income")
    total_income: Decimal = Field(..., description="Total annual income")


class ProjectionResponse(BaseModel):
    """Response schema for retirement projection."""
    id: UUID
    user_id: UUID
    projection_date: date
    target_retirement_age: int
    projected_total_pot: Decimal
    annual_income_needed: Decimal
    income_breakdown: IncomeBreakdown
    income_gap: Decimal = Field(..., description="Income gap (positive = surplus, negative = shortfall)")
    on_track: bool = Field(..., description="Whether retirement planning is on track")
    growth_assumptions: Optional[Dict[str, Decimal]]
    inflation_rate: Decimal

    class Config:
        from_attributes = True


# ============================================================================
# DRAWDOWN SCENARIO SCHEMAS
# ============================================================================

class DrawdownScenarioCreate(BaseModel):
    """Schema for creating a drawdown scenario."""
    pension_id: UUID = Field(..., description="Pension to model drawdown for")
    scenario_name: str = Field(..., min_length=1, max_length=100, description="Scenario name")
    drawdown_rate: Decimal = Field(..., ge=2, le=8, description="Annual drawdown rate (%)")
    start_age: int = Field(..., ge=55, le=75, description="Age when drawdown starts")

    @field_validator('drawdown_rate')
    @classmethod
    def validate_drawdown_rate(cls, v):
        """Validate drawdown rate is within safe range."""
        if v < Decimal('2.00') or v > Decimal('8.00'):
            raise ValueError("Drawdown rate must be between 2% and 8%")
        return v


class DrawdownScenarioResponse(BaseModel):
    """Response schema for drawdown scenario."""
    id: UUID
    pension_id: UUID
    scenario_name: str
    drawdown_rate: Decimal
    start_age: int
    projected_annual_income: Decimal
    pot_depletion_age: Optional[int] = Field(None, description="Age when pot depletes (None if lasts)")
    tax_implications: Optional[Dict[str, Any]]
    assumptions: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# ============================================================================
# ANNUITY QUOTE SCHEMAS
# ============================================================================

class AnnuityQuoteRequest(BaseModel):
    """Request schema for annuity quote calculation."""
    pension_id: UUID = Field(..., description="Pension to use for annuity")
    annuity_rate: Decimal = Field(..., ge=3, le=15, description="Annuity rate (%)")
    spouse_provision: bool = Field(False, description="Include spouse provision")
    escalation_rate: Optional[Decimal] = Field(None, ge=0, le=5, description="Annual escalation rate (%)")


class AnnuityQuoteResponse(BaseModel):
    """Response schema for annuity quote."""
    pension_id: UUID
    pot_value: Decimal
    annuity_rate: Decimal
    annual_income: Decimal = Field(..., description="Annual income from annuity")
    monthly_income: Decimal = Field(..., description="Monthly income from annuity")
    spouse_provision: bool
    escalation_rate: Optional[Decimal]
    guaranteed_period: Optional[int] = Field(None, description="Guaranteed payment period (years)")


# ============================================================================
# SA RETIREMENT FUND SCHEMAS
# ============================================================================

class SAFundCreate(BaseModel):
    """Schema for creating a new SA retirement fund."""
    fund_type: SAFundType = Field(..., description="Type of SA retirement fund")
    provider: str = Field(..., min_length=1, max_length=255, description="Fund provider name")
    fund_name: str = Field(..., min_length=1, max_length=255, description="Fund name")
    fund_number: str = Field(..., min_length=1, max_length=100, description="Fund/member number")
    employer_name: Optional[str] = Field(None, max_length=255, description="Employer name (for pension/provident funds)")
    current_value: Decimal = Field(..., ge=0, description="Current fund value in ZAR")
    start_date: date = Field(..., description="Date fund started")
    retirement_age: int = Field(..., ge=55, le=75, description="Target retirement age")
    investment_strategy: Optional[InvestmentStrategy] = Field(None, description="Investment strategy")
    assumed_growth_rate: Optional[Decimal] = Field(Decimal('8.00'), ge=0, le=20, description="Assumed annual growth rate (%)")

    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v):
        """Ensure start date is not in future."""
        if v > date.today():
            raise ValueError("Start date cannot be in the future")
        return v


class SAFundUpdate(BaseModel):
    """Schema for updating an existing SA retirement fund (all fields optional)."""
    provider: Optional[str] = Field(None, min_length=1, max_length=255)
    fund_name: Optional[str] = Field(None, min_length=1, max_length=255)
    employer_name: Optional[str] = Field(None, max_length=255)
    current_value: Optional[Decimal] = Field(None, ge=0)
    retirement_age: Optional[int] = Field(None, ge=55, le=75)
    investment_strategy: Optional[InvestmentStrategy] = None
    assumed_growth_rate: Optional[Decimal] = Field(None, ge=0, le=20)
    status: Optional[SAFundStatus] = None


class SAFundResponse(BaseModel):
    """Response schema for SA retirement fund."""
    id: UUID
    user_id: UUID
    fund_type: SAFundType
    provider: str
    fund_name: str
    fund_number: str  # Masked (only last 4 digits)
    employer_name: Optional[str]
    current_value: Decimal
    start_date: date
    retirement_age: int
    investment_strategy: Optional[InvestmentStrategy]
    assumed_growth_rate: Optional[Decimal]
    status: SAFundStatus
    projected_value: Optional[Decimal] = Field(None, description="Projected value at retirement")

    class Config:
        from_attributes = True


class SAContributionCreate(BaseModel):
    """Schema for adding an SA fund contribution."""
    employee_contribution: Optional[Decimal] = Field(Decimal('0.00'), ge=0, description="Employee contribution")
    employer_contribution: Optional[Decimal] = Field(Decimal('0.00'), ge=0, description="Employer contribution")
    contribution_date: date = Field(..., description="Contribution date")

    @field_validator('contribution_date')
    @classmethod
    def validate_contribution_date(cls, v):
        """Ensure contribution date is not in future."""
        if v > date.today():
            raise ValueError("Contribution date cannot be in the future")
        return v


class SAContributionResponse(BaseModel):
    """Response schema for SA fund contribution."""
    id: UUID
    fund_id: UUID
    employee_contribution: Decimal
    employer_contribution: Decimal
    total_contribution: Decimal
    contribution_date: date
    tax_year: str
    tax_deduction_claimed: Decimal
    effective_from: date
    effective_to: Optional[date]

    class Config:
        from_attributes = True


class SADeductionResponse(BaseModel):
    """Response schema for Section 10C deduction status."""
    tax_year: str = Field(..., description="SA tax year (YYYY/YYYY)")
    annual_deduction_limit: Decimal = Field(..., description="Annual deduction limit (27.5% of income, max R350k)")
    deductions_claimed: Decimal = Field(..., description="Total deductions claimed")
    deductions_remaining: Decimal = Field(..., description="Remaining deduction allowance")
    excess: Decimal = Field(..., description="Excess deductions (if any)")

    class Config:
        from_attributes = True


class SAFundProjectionRequest(BaseModel):
    """Request schema for SA fund projection."""
    target_age: Optional[int] = Field(None, ge=55, le=75, description="Target age for projection")


class SAFundProjectionResponse(BaseModel):
    """Response schema for SA fund projection."""
    fund_id: UUID
    current_value: Decimal
    projected_value: Decimal
    retirement_age: int
    assumed_growth_rate: Decimal


class SATotalFundResponse(BaseModel):
    """Response schema for total SA retirement fund value."""
    total_value: Decimal = Field(..., description="Total value across all SA funds")
    breakdown: list[Dict[str, Any]] = Field(..., description="Breakdown by fund")
