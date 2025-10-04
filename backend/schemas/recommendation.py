"""
Pydantic schemas for recommendation API endpoints.

Schemas for:
- Request/response for recommendation generation
- Filtering recommendations by priority/type
- Response models with proper serialization
- Currency and priority enums
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from models.recommendation import RecommendationPriority, RecommendationType, Currency


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class RecommendationFilters(BaseModel):
    """
    Filters for retrieving recommendations.

    Used as query parameters for GET /recommendations endpoint.
    """
    priority: Optional[RecommendationPriority] = Field(
        None,
        description="Filter by priority (HIGH, MEDIUM, LOW)"
    )
    type: Optional[RecommendationType] = Field(
        None,
        alias="type",
        description="Filter by recommendation type (PROTECTION, ISA, TFSA, etc.)"
    )


class GenerateRecommendationsRequest(BaseModel):
    """
    Request to generate new recommendations.

    Used for POST /recommendations/generate endpoint.
    """
    base_currency: str = Field(
        default="GBP",
        description="Base currency for calculations (GBP, ZAR, USD, EUR)",
        pattern="^(GBP|ZAR|USD|EUR)$"
    )


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class RecommendationResponse(BaseModel):
    """
    Recommendation response schema.

    Returns full recommendation details with all fields.
    """
    id: UUID = Field(..., description="Recommendation unique identifier")
    user_id: UUID = Field(..., description="User who owns this recommendation")
    recommendation_type: RecommendationType = Field(..., description="Type of recommendation")
    priority: RecommendationPriority = Field(..., description="Priority level")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed description")
    action_items: List[str] = Field(
        default_factory=list,
        description="List of specific actions to take"
    )
    potential_savings: Optional[Decimal] = Field(
        None,
        description="Estimated financial benefit in currency"
    )
    currency: Currency = Field(..., description="Currency for potential_savings")
    created_date: datetime = Field(..., description="When recommendation was created")
    dismissed: bool = Field(..., description="Whether user dismissed this")
    dismissed_date: Optional[datetime] = Field(None, description="When dismissed")
    completed: bool = Field(..., description="Whether user completed this")
    completed_date: Optional[datetime] = Field(None, description="When completed")

    model_config = ConfigDict(from_attributes=True)


class BulkRecommendationsResponse(BaseModel):
    """
    Response for bulk recommendation generation.

    Returns list of newly created recommendations.
    """
    recommendations: List[RecommendationResponse] = Field(
        ...,
        description="List of generated recommendations"
    )
    count: int = Field(..., description="Number of recommendations generated")
