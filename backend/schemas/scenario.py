"""
Pydantic schemas for scenario analysis API endpoints.

This module provides request and response schemas for:
- Scenario CRUD operations
- Scenario assumptions
- Scenario execution and results
- Scenario comparison
- Monte Carlo simulations
- What-if analysis

All schemas include validation and serialization logic.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

from models.scenario import ScenarioType, ScenarioStatus


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class ScenarioAssumptionBase(BaseModel):
    """Base schema for scenario assumptions."""
    assumption_type: str = Field(..., min_length=1, max_length=100, description="Type of assumption")
    assumption_key: str = Field(..., min_length=1, max_length=100, description="Assumption key")
    assumption_value: str = Field(..., min_length=1, max_length=500, description="Assumption value")
    unit: Optional[str] = Field(None, max_length=50, description="Optional unit")


class ScenarioAssumptionResponse(ScenarioAssumptionBase):
    """Response schema for scenario assumption."""
    id: UUID
    scenario_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SCENARIO CRUD SCHEMAS
# ============================================================================

class ScenarioCreate(BaseModel):
    """Schema for creating a new scenario."""
    scenario_name: str = Field(..., min_length=1, max_length=255, description="Scenario name")
    scenario_type: ScenarioType = Field(..., description="Type of scenario")
    description: Optional[str] = Field(None, description="Optional scenario description")
    base_case: bool = Field(False, description="Whether this is the base case")
    assumptions: List[ScenarioAssumptionBase] = Field(default_factory=list, description="Scenario assumptions")

    @field_validator('scenario_name')
    @classmethod
    def validate_scenario_name(cls, v):
        """Ensure scenario name is not empty."""
        if not v or not v.strip():
            raise ValueError("Scenario name cannot be empty")
        return v.strip()


class ScenarioUpdate(BaseModel):
    """Schema for updating an existing scenario."""
    scenario_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ScenarioStatus] = None
    assumptions: Optional[List[ScenarioAssumptionBase]] = None


class ScenarioResponse(BaseModel):
    """Response schema for scenario with all details."""
    id: UUID
    user_id: UUID
    scenario_name: str
    scenario_type: ScenarioType
    description: Optional[str]
    base_case: bool
    status: ScenarioStatus
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime
    expires_at: datetime
    assumptions: List[ScenarioAssumptionResponse] = []
    has_results: bool = Field(False, description="Whether results are available")

    class Config:
        from_attributes = True


# ============================================================================
# SCENARIO EXECUTION SCHEMAS
# ============================================================================

class ScenarioExecutionRequest(BaseModel):
    """Request schema for executing a scenario calculation."""
    projection_years: int = Field(30, ge=1, le=30, description="Number of years to project")
    growth_rate: Optional[Decimal] = Field(Decimal('6.00'), ge=0, le=20, description="Assumed investment growth rate (%)")
    inflation_rate: Optional[Decimal] = Field(Decimal('2.50'), ge=0, le=10, description="Assumed inflation rate (%)")
    include_monte_carlo: bool = Field(False, description="Run Monte Carlo simulation")
    monte_carlo_simulations: int = Field(10000, ge=1000, le=50000, description="Number of Monte Carlo simulations")

    @field_validator('projection_years')
    @classmethod
    def validate_projection_years(cls, v):
        """Ensure projection years is reasonable."""
        if v < 1 or v > 30:
            raise ValueError("Projection years must be between 1 and 30")
        return v


class YearProjection(BaseModel):
    """Single year projection data."""
    year: int = Field(..., description="Year number (1, 2, 3, ...)")
    age: int = Field(..., description="User's age in this year")
    net_worth: Decimal = Field(..., description="Net worth at end of year")
    income: Decimal = Field(..., description="Annual income")
    expenses: Decimal = Field(..., description="Annual expenses")
    tax: Decimal = Field(..., description="Annual tax liability")
    savings: Decimal = Field(..., description="Annual savings")


class RetirementProjection(BaseModel):
    """Retirement income projection."""
    retirement_age: int = Field(..., description="Retirement age")
    pension_pot_at_retirement: Decimal = Field(..., description="Total pension pot at retirement")
    tax_free_lump_sum: Decimal = Field(..., description="Tax-free lump sum (25%)")
    annual_income: Decimal = Field(..., description="Projected annual retirement income")
    monthly_income: Decimal = Field(..., description="Projected monthly retirement income")
    replacement_ratio: Decimal = Field(..., description="Income replacement ratio (%)")
    adequate: bool = Field(..., description="Whether retirement income is adequate")


class MonteCarloResult(BaseModel):
    """Monte Carlo simulation results."""
    simulations_run: int = Field(..., description="Number of simulations")
    probability_of_success: Decimal = Field(..., description="Probability of success (%)")
    percentile_10: Decimal = Field(..., description="10th percentile outcome")
    percentile_25: Decimal = Field(..., description="25th percentile outcome")
    percentile_50: Decimal = Field(..., description="50th percentile (median)")
    percentile_75: Decimal = Field(..., description="75th percentile outcome")
    percentile_90: Decimal = Field(..., description="90th percentile outcome")
    worst_case: Decimal = Field(..., description="Worst case outcome")
    best_case: Decimal = Field(..., description="Best case outcome")
    expected_value: Decimal = Field(..., description="Expected value (mean)")


class ScenarioResultResponse(BaseModel):
    """Response schema for scenario execution results."""
    id: UUID
    scenario_id: UUID
    calculation_date: datetime
    calculation_version: str
    projection_years: int

    # Summary metrics
    total_lifetime_tax: Optional[Decimal] = Field(None, description="Total lifetime tax paid")
    final_net_worth: Optional[Decimal] = Field(None, description="Final net worth")
    retirement_adequacy_ratio: Optional[Decimal] = Field(None, description="Retirement adequacy (%)")
    goals_achieved_count: Optional[int] = Field(None, description="Goals achieved")
    goals_achieved_percentage: Optional[Decimal] = Field(None, description="Goals achieved (%)")
    probability_of_success: Optional[Decimal] = Field(None, description="Monte Carlo success probability (%)")

    # Detailed projections
    net_worth_projection: Optional[List[Dict[str, Any]]] = Field(None, description="Year-by-year net worth")
    retirement_income_projection: Optional[Dict[str, Any]] = Field(None, description="Retirement income details")
    tax_liability_projection: Optional[List[Dict[str, Any]]] = Field(None, description="Year-by-year tax")
    goal_achievement_projection: Optional[Dict[str, Any]] = Field(None, description="Goal achievement details")
    monte_carlo_results: Optional[Dict[str, Any]] = Field(None, description="Monte Carlo simulation results")

    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SCENARIO COMPARISON SCHEMAS
# ============================================================================

class ScenarioComparisonRequest(BaseModel):
    """Request schema for comparing scenarios."""
    scenario_ids: List[UUID] = Field(..., min_length=2, max_length=5, description="Scenario IDs to compare")

    @field_validator('scenario_ids')
    @classmethod
    def validate_scenario_ids(cls, v):
        """Ensure at least 2 scenarios provided."""
        if len(v) < 2:
            raise ValueError("Need at least 2 scenarios to compare")
        if len(v) > 5:
            raise ValueError("Cannot compare more than 5 scenarios")
        if len(v) != len(set(v)):
            raise ValueError("Duplicate scenario IDs provided")
        return v


class MetricComparison(BaseModel):
    """Comparison of a single metric across scenarios."""
    metric_name: str = Field(..., description="Name of the metric")
    higher_is_better: bool = Field(..., description="Whether higher values are better")
    values: List[Dict[str, Any]] = Field(..., description="Values by scenario")
    best_scenario_id: UUID = Field(..., description="Scenario with best value")
    worst_scenario_id: UUID = Field(..., description="Scenario with worst value")
    range: Decimal = Field(..., description="Range (max - min)")
    average: Decimal = Field(..., description="Average across scenarios")


class TradeOff(BaseModel):
    """Identified trade-off between scenarios."""
    trade_off_type: str = Field(..., description="Type of trade-off")
    description: str = Field(..., description="Trade-off description")
    scenario_a_id: UUID = Field(..., description="First scenario in trade-off")
    scenario_b_id: UUID = Field(..., description="Second scenario in trade-off")
    decision_factors: List[str] = Field(..., description="Factors to consider")


class ScenarioComparisonResponse(BaseModel):
    """Response schema for scenario comparison."""
    scenarios: List[ScenarioResponse] = Field(..., description="Scenarios being compared")
    metric_comparisons: Dict[str, MetricComparison] = Field(..., description="Metric comparisons")
    trade_offs: List[TradeOff] = Field(..., description="Identified trade-offs")
    overall_best_scenario_id: Optional[UUID] = Field(None, description="Overall best scenario")
    recommendations: List[str] = Field(..., description="Recommendations")


# ============================================================================
# SPECIFIC SCENARIO TYPE SCHEMAS
# ============================================================================

class RetirementAgeScenarioRequest(BaseModel):
    """Request for retirement age scenario modeling."""
    retirement_age: int = Field(..., ge=55, le=70, description="Target retirement age")
    current_pension_pot: Optional[Decimal] = Field(None, ge=0, description="Current pension pot value")
    annual_contributions: Optional[Decimal] = Field(None, ge=0, description="Annual pension contributions")

    @field_validator('retirement_age')
    @classmethod
    def validate_retirement_age(cls, v):
        """Validate retirement age is reasonable."""
        if v < 55 or v > 70:
            raise ValueError("Retirement age must be between 55 and 70")
        return v


class RetirementAgeScenarioResponse(BaseModel):
    """Response for retirement age scenario."""
    retirement_age: int
    pension_pot_at_retirement: Decimal
    annual_retirement_income: Decimal
    monthly_retirement_income: Decimal
    pot_depletion_age: Optional[int] = Field(None, description="Age when pot depletes (None if lasts)")
    replacement_ratio: Decimal = Field(..., description="Income replacement ratio (%)")
    comparison_to_base: Optional[Dict[str, Any]] = Field(None, description="Comparison to base case")


class CareerChangeScenarioRequest(BaseModel):
    """Request for career change scenario modeling."""
    new_salary: Decimal = Field(..., gt=0, description="New annual salary")
    change_date: date = Field(..., description="Date of career change")
    salary_increase_rate: Optional[Decimal] = Field(Decimal('3.00'), ge=0, le=10, description="Annual salary increase (%)")

    @field_validator('change_date')
    @classmethod
    def validate_change_date(cls, v):
        """Ensure change date is not in past."""
        if v < date.today():
            raise ValueError("Career change date must be today or in the future")
        return v


class CareerChangeScenarioResponse(BaseModel):
    """Response for career change scenario."""
    new_salary: Decimal
    change_date: date
    impact_on_pension: Decimal = Field(..., description="Impact on pension pot at retirement")
    impact_on_tax: Decimal = Field(..., description="Annual tax impact")
    impact_on_net_worth: Decimal = Field(..., description="Impact on final net worth")
    break_even_years: Optional[int] = Field(None, description="Years to break even (if applicable)")


class PropertyScenarioRequest(BaseModel):
    """Request for property purchase scenario modeling."""
    property_value: Decimal = Field(..., gt=0, description="Property purchase price")
    deposit: Decimal = Field(..., ge=0, description="Deposit amount")
    mortgage_rate: Decimal = Field(..., ge=0, le=20, description="Mortgage interest rate (%)")
    mortgage_term_years: int = Field(..., ge=5, le=35, description="Mortgage term in years")
    stamp_duty: Optional[Decimal] = Field(None, ge=0, description="Stamp duty cost")

    @field_validator('deposit')
    @classmethod
    def validate_deposit(cls, v, info):
        """Ensure deposit doesn't exceed property value."""
        if 'property_value' in info.data and v > info.data['property_value']:
            raise ValueError("Deposit cannot exceed property value")
        return v


class PropertyScenarioResponse(BaseModel):
    """Response for property purchase scenario."""
    property_value: Decimal
    deposit: Decimal
    mortgage_amount: Decimal
    monthly_payment: Decimal
    total_interest: Decimal
    total_cost: Decimal
    affordability_percentage: Decimal = Field(..., description="Monthly payment as % of income")
    impact_on_cash_flow: Decimal = Field(..., description="Monthly cash flow impact")
    impact_on_net_worth: Decimal = Field(..., description="Impact on net worth over time")


class MonteCarloRequest(BaseModel):
    """Request for Monte Carlo simulation."""
    simulations: int = Field(10000, ge=1000, le=50000, description="Number of simulations")
    mean_return: Decimal = Field(Decimal('6.00'), description="Mean investment return (%)")
    volatility: Decimal = Field(Decimal('15.00'), description="Return volatility/std dev (%)")
    mean_inflation: Decimal = Field(Decimal('2.50'), description="Mean inflation rate (%)")
    inflation_volatility: Decimal = Field(Decimal('1.00'), description="Inflation volatility (%)")
    retirement_age: int = Field(..., ge=55, le=75, description="Target retirement age")
    target_income: Decimal = Field(..., gt=0, description="Target annual retirement income")


class MonteCarloResponse(BaseModel):
    """Response for Monte Carlo simulation."""
    simulations_run: int
    probability_of_success: Decimal = Field(..., description="Probability retirement goal is met (%)")
    safe_withdrawal_rate: Decimal = Field(..., description="Safe withdrawal rate with 90% confidence (%)")
    percentiles: Dict[str, Decimal] = Field(..., description="Outcome percentiles")
    confidence_intervals: Dict[str, Dict[str, Decimal]] = Field(..., description="95% confidence intervals")
    worst_case: Decimal
    best_case: Decimal
    expected_value: Decimal
