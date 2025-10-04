"""
Pydantic schemas for goal planning API requests and responses.

This module provides validation schemas for:
- Financial goal creation and management
- Milestone tracking
- Progress history
- Goal recommendations

All schemas include comprehensive validation and documentation.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from models.goal import (
    GoalType,
    GoalPriority,
    GoalStatus,
    ContributionFrequency,
    MilestoneStatus,
    RecommendationType
)


# ============================================================================
# FINANCIAL GOAL SCHEMAS
# ============================================================================

class CreateGoalRequest(BaseModel):
    """
    Schema for creating a new financial goal.

    Validates:
    - Goal type, name, and target details
    - Timeline (target date must be at least 6 months out)
    - Priority and optional auto-contribution settings
    """

    goal_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User-friendly name for the goal"
    )

    goal_type: GoalType = Field(
        ...,
        description="Type of financial goal"
    )

    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional detailed description"
    )

    target_amount: Decimal = Field(
        ...,
        gt=0,
        description="Target amount to save (must be positive)"
    )

    currency: str = Field(
        default="GBP",
        pattern="^(GBP|ZAR|USD|EUR)$",
        description="Currency code"
    )

    target_date: date = Field(
        ...,
        description="Target date to achieve the goal"
    )

    priority: GoalPriority = Field(
        default=GoalPriority.MEDIUM,
        description="Goal priority (HIGH, MEDIUM, LOW)"
    )

    linked_accounts: Optional[List[str]] = Field(
        None,
        description="Array of account IDs to link for progress tracking"
    )

    auto_contribution: bool = Field(
        default=False,
        description="Whether to set up automatic contributions"
    )

    contribution_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Automatic contribution amount per period"
    )

    contribution_frequency: Optional[ContributionFrequency] = Field(
        None,
        description="Frequency of automatic contributions"
    )

    @field_validator('target_date')
    @classmethod
    def validate_target_date(cls, v: date) -> date:
        """Ensure target date is at least 6 months in the future."""
        from dateutil.relativedelta import relativedelta

        min_date = date.today() + relativedelta(months=6)
        max_date = date.today() + relativedelta(years=50)

        if v < min_date:
            raise ValueError("Target date must be at least 6 months in the future")
        if v > max_date:
            raise ValueError("Target date cannot be more than 50 years in the future")

        return v

    @model_validator(mode='after')
    def validate_auto_contribution(self):
        """Validate auto-contribution settings if enabled."""
        if self.auto_contribution:
            if not self.contribution_amount or self.contribution_amount <= 0:
                raise ValueError("Contribution amount required when auto_contribution is enabled")
            if not self.contribution_frequency:
                raise ValueError("Contribution frequency required when auto_contribution is enabled")
        return self

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "goal_name": "House Deposit",
                "goal_type": "PROPERTY_PURCHASE",
                "description": "Save for 10% deposit on a £300,000 property",
                "target_amount": "30000.00",
                "currency": "GBP",
                "target_date": "2027-12-31",
                "priority": "HIGH",
                "linked_accounts": [],
                "auto_contribution": True,
                "contribution_amount": "500.00",
                "contribution_frequency": "MONTHLY"
            }
        }


class UpdateGoalRequest(BaseModel):
    """
    Schema for updating an existing financial goal.

    All fields are optional to support partial updates.
    """

    goal_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255
    )

    description: Optional[str] = Field(
        None,
        max_length=2000
    )

    target_amount: Optional[Decimal] = Field(
        None,
        gt=0
    )

    target_date: Optional[date] = None

    priority: Optional[GoalPriority] = None

    status: Optional[GoalStatus] = None

    linked_accounts: Optional[List[str]] = None

    auto_contribution: Optional[bool] = None

    contribution_amount: Optional[Decimal] = Field(
        None,
        ge=0
    )

    contribution_frequency: Optional[ContributionFrequency] = None

    class Config:
        from_attributes = True


class GoalResponse(BaseModel):
    """
    Schema for financial goal API responses.

    Includes:
    - All goal details
    - Calculated progress percentage
    - Status and timeline information
    - Linked accounts and contribution settings
    """

    id: UUID
    user_id: UUID

    goal_name: str
    goal_type: GoalType
    description: Optional[str] = None

    target_amount: Decimal
    currency: str
    current_amount: Decimal
    progress_percentage: Decimal

    target_date: date
    start_date: date

    priority: GoalPriority
    status: GoalStatus

    linked_accounts: Optional[List[str]] = None

    auto_contribution: bool
    contribution_amount: Optional[Decimal] = None
    contribution_frequency: Optional[ContributionFrequency] = None

    created_at: datetime
    updated_at: datetime
    achieved_at: Optional[datetime] = None

    # Calculated fields
    days_remaining: Optional[int] = Field(
        None,
        description="Days remaining until target date"
    )
    on_track: Optional[bool] = Field(
        None,
        description="Whether goal is on track based on timeline"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440000",
                "goal_name": "House Deposit",
                "goal_type": "PROPERTY_PURCHASE",
                "description": "Save for 10% deposit on a £300,000 property",
                "target_amount": "30000.00",
                "currency": "GBP",
                "current_amount": "12500.00",
                "progress_percentage": "41.67",
                "target_date": "2027-12-31",
                "start_date": "2024-01-01",
                "priority": "HIGH",
                "status": "IN_PROGRESS",
                "linked_accounts": ["account-uuid-1"],
                "auto_contribution": True,
                "contribution_amount": "500.00",
                "contribution_frequency": "MONTHLY",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-10-03T00:00:00",
                "achieved_at": None,
                "days_remaining": 1185,
                "on_track": True
            }
        }


class GoalSummaryResponse(BaseModel):
    """
    Schema for goal summary (lightweight response).

    Used for list endpoints to reduce payload size.
    """

    id: UUID
    goal_name: str
    goal_type: GoalType
    target_amount: Decimal
    currency: str
    current_amount: Decimal
    progress_percentage: Decimal
    target_date: date
    priority: GoalPriority
    status: GoalStatus
    on_track: Optional[bool] = None

    class Config:
        from_attributes = True


# ============================================================================
# MILESTONE SCHEMAS
# ============================================================================

class CreateMilestoneRequest(BaseModel):
    """
    Schema for creating a new goal milestone.

    Validates:
    - Milestone name and target details
    - Target date must be between goal start and target date
    """

    milestone_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Descriptive name for the milestone"
    )

    milestone_target_amount: Decimal = Field(
        ...,
        gt=0,
        description="Target amount for this milestone (must be positive)"
    )

    milestone_target_date: date = Field(
        ...,
        description="Target date for achieving this milestone"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "milestone_name": "25% Progress",
                "milestone_target_amount": "7500.00",
                "milestone_target_date": "2025-06-30"
            }
        }


class MilestoneResponse(BaseModel):
    """
    Schema for milestone API responses.

    Includes:
    - Milestone details
    - Achievement status
    - Timestamps
    """

    id: UUID
    goal_id: UUID

    milestone_name: str
    milestone_target_amount: Decimal
    milestone_target_date: date

    status: MilestoneStatus
    achieved_date: Optional[date] = None

    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "goal_id": "550e8400-e29b-41d4-a716-446655440000",
                "milestone_name": "25% Progress",
                "milestone_target_amount": "7500.00",
                "milestone_target_date": "2025-06-30",
                "status": "PENDING",
                "achieved_date": None,
                "created_at": "2024-01-01T00:00:00"
            }
        }


# ============================================================================
# PROGRESS HISTORY SCHEMAS
# ============================================================================

class ProgressHistoryResponse(BaseModel):
    """
    Schema for goal progress history API responses.

    Includes:
    - Snapshot data at specific date
    - Progress percentage and on-track status
    - Temporal data fields
    """

    id: UUID
    goal_id: UUID

    snapshot_date: date
    amount_at_snapshot: Decimal
    target_amount_at_snapshot: Decimal
    progress_percentage: Decimal

    on_track: bool
    projected_completion_date: Optional[date] = None

    effective_from: date
    effective_to: Optional[date] = None

    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "goal_id": "550e8400-e29b-41d4-a716-446655440000",
                "snapshot_date": "2024-10-01",
                "amount_at_snapshot": "12000.00",
                "target_amount_at_snapshot": "30000.00",
                "progress_percentage": "40.00",
                "on_track": True,
                "projected_completion_date": "2027-11-15",
                "effective_from": "2024-10-01",
                "effective_to": None,
                "created_at": "2024-10-01T00:00:00"
            }
        }


# ============================================================================
# RECOMMENDATION SCHEMAS
# ============================================================================

class CreateRecommendationRequest(BaseModel):
    """
    Schema for creating a new goal recommendation.

    Validates:
    - Recommendation type and text
    - Priority and action items
    """

    recommendation_type: RecommendationType = Field(
        ...,
        description="Type of recommendation"
    )

    recommendation_text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Detailed recommendation text"
    )

    action_items: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Array of specific action items"
    )

    priority: GoalPriority = Field(
        default=GoalPriority.MEDIUM,
        description="Recommendation priority"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "recommendation_type": "AUTOMATE_SAVINGS",
                "recommendation_text": "Set up automatic monthly transfer of £500 to ensure consistent progress toward your goal.",
                "action_items": [
                    {"action": "Set up standing order", "completed": False},
                    {"action": "Link savings account", "completed": False}
                ],
                "priority": "HIGH"
            }
        }


class RecommendationResponse(BaseModel):
    """
    Schema for recommendation API responses.

    Includes:
    - Recommendation details
    - Dismissal status
    - Timestamps
    """

    id: UUID
    goal_id: UUID

    recommendation_type: RecommendationType
    recommendation_text: str
    action_items: Optional[List[Dict[str, Any]]] = None

    priority: GoalPriority

    dismissed: bool
    dismissed_at: Optional[datetime] = None

    created_date: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440003",
                "goal_id": "550e8400-e29b-41d4-a716-446655440000",
                "recommendation_type": "AUTOMATE_SAVINGS",
                "recommendation_text": "Set up automatic monthly transfer of £500 to ensure consistent progress toward your goal.",
                "action_items": [
                    {"action": "Set up standing order", "completed": False},
                    {"action": "Link savings account", "completed": False}
                ],
                "priority": "HIGH",
                "dismissed": False,
                "dismissed_at": None,
                "created_date": "2024-01-15T00:00:00"
            }
        }


# ============================================================================
# AGGREGATION SCHEMAS
# ============================================================================

class GoalStatistics(BaseModel):
    """
    Schema for goal statistics and aggregations.

    Provides:
    - Total goals by status
    - Total target and current amounts
    - Progress metrics
    """

    total_goals: int = Field(..., description="Total number of goals")
    active_goals: int = Field(..., description="Number of active goals")
    achieved_goals: int = Field(..., description="Number of achieved goals")

    total_target_amount: Decimal = Field(..., description="Sum of all goal target amounts")
    total_current_amount: Decimal = Field(..., description="Sum of all goal current amounts")
    overall_progress_percentage: Decimal = Field(..., description="Overall progress across all goals")

    on_track_count: int = Field(..., description="Number of goals on track")
    at_risk_count: int = Field(..., description="Number of goals at risk")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "total_goals": 5,
                "active_goals": 4,
                "achieved_goals": 1,
                "total_target_amount": "150000.00",
                "total_current_amount": "62500.00",
                "overall_progress_percentage": "41.67",
                "on_track_count": 3,
                "at_risk_count": 1
            }
        }
