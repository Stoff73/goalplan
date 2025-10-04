"""
Pydantic schemas for Personalization API.

Request and response models for:
- User preferences
- Behavior tracking
- Personalized insights
- Dashboard personalization
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from models.personalization import PreferenceType, ActionType, InsightType


# ============================================================================
# PREFERENCE SCHEMAS
# ============================================================================

class PreferenceCreate(BaseModel):
    """Request schema for creating/updating a preference."""

    preference_type: PreferenceType = Field(..., description="Type of preference")
    preference_value: str = Field(..., description="Preference value (JSON string for complex preferences)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "preference_type": "DEFAULT_CURRENCY",
                "preference_value": "GBP"
            }
        }
    }


class PreferenceUpdate(BaseModel):
    """Request schema for updating a preference."""

    preference_value: str = Field(..., description="New preference value")

    model_config = {
        "json_schema_extra": {
            "example": {
                "preference_value": "ZAR"
            }
        }
    }


class PreferenceResponse(BaseModel):
    """Response schema for a user preference."""

    id: UUID
    user_id: UUID
    preference_type: PreferenceType
    preference_value: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "preference_type": "DEFAULT_CURRENCY",
                "preference_value": "GBP",
                "created_at": "2025-10-04T10:00:00Z",
                "updated_at": "2025-10-04T10:00:00Z"
            }
        }
    }


# ============================================================================
# BEHAVIOR TRACKING SCHEMAS
# ============================================================================

class BehaviorTrackRequest(BaseModel):
    """Request schema for tracking user behavior."""

    action_type: ActionType = Field(..., description="Type of action")
    action_context: Dict[str, Any] = Field(..., description="Action context metadata")

    model_config = {
        "json_schema_extra": {
            "example": {
                "action_type": "PAGE_VIEW",
                "action_context": {
                    "page": "dashboard",
                    "duration": 45,
                    "referrer": "navigation"
                }
            }
        }
    }


class BehaviorResponse(BaseModel):
    """Response schema for behavior tracking."""

    id: UUID
    user_id: UUID
    action_type: ActionType
    action_context: str
    timestamp: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "action_type": "PAGE_VIEW",
                "action_context": "{\"page\": \"dashboard\", \"duration\": 45}",
                "timestamp": "2025-10-04T10:00:00Z"
            }
        }
    }


# ============================================================================
# INSIGHT SCHEMAS
# ============================================================================

class InsightResponse(BaseModel):
    """Response schema for personalized insight."""

    id: UUID
    user_id: UUID
    insight_type: InsightType
    insight_text: str
    relevance_score: Decimal
    shown_date: Optional[datetime] = None
    clicked: bool
    dismissed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "insight_type": "GOAL_ADVICE",
                "insight_text": "You're 50% to your house deposit - consider increasing savings by £200/month",
                "relevance_score": 85.50,
                "shown_date": None,
                "clicked": False,
                "dismissed": False,
                "created_at": "2025-10-04T10:00:00Z",
                "updated_at": "2025-10-04T10:00:00Z"
            }
        }
    }


# ============================================================================
# PERSONALIZED DASHBOARD SCHEMAS
# ============================================================================

class PersonalizedDashboardResponse(BaseModel):
    """Response schema for personalized dashboard layout."""

    widget_order: List[str] = Field(..., description="Ordered list of widget names")
    visible_widgets: List[str] = Field(..., description="Widgets to show")
    hidden_widgets: List[str] = Field(..., description="Widgets to hide/collapse")

    model_config = {
        "json_schema_extra": {
            "example": {
                "widget_order": ["net_worth", "goals", "savings", "investments"],
                "visible_widgets": ["net_worth", "goals", "savings", "investments"],
                "hidden_widgets": ["retirement", "protection"]
            }
        }
    }


# ============================================================================
# BEHAVIOR ANALYSIS SCHEMAS
# ============================================================================

class BehaviorAnalysisResponse(BaseModel):
    """Response schema for behavior analysis."""

    most_viewed_pages: List[str] = Field(..., description="Most frequently viewed pages")
    most_used_features: List[str] = Field(..., description="Most frequently used features")
    engagement_score: int = Field(..., ge=0, le=100, description="Overall engagement score (0-100)")
    total_actions: int = Field(..., ge=0, description="Total number of actions tracked")

    model_config = {
        "json_schema_extra": {
            "example": {
                "most_viewed_pages": ["dashboard", "goals", "savings"],
                "most_used_features": ["goal_tracking", "account_management"],
                "engagement_score": 75,
                "total_actions": 150
            }
        }
    }


# ============================================================================
# PREFERENCES DICT SCHEMA
# ============================================================================

class PreferencesDictResponse(BaseModel):
    """Response schema for all user preferences as a dictionary."""

    preferences: Dict[str, str] = Field(..., description="User preferences by type")

    model_config = {
        "json_schema_extra": {
            "example": {
                "preferences": {
                    "DEFAULT_CURRENCY": "GBP",
                    "THEME": "dark",
                    "NOTIFICATION_FREQUENCY": "daily"
                }
            }
        }
    }
