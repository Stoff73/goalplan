"""
AI Advisory API Pydantic schemas.

This module provides request and response schemas for AI advisory endpoints:
- Advice responses with recommendations and metadata
- Alert responses with urgency and action items
- Question requests for free-form financial queries
- Disclaimer and confidence score tracking

All AI advice includes mandatory disclaimers and confidence scores
to indicate when human review is recommended.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class AdviceRequest(BaseModel):
    """
    Base request for AI advice endpoints.

    Most endpoints don't need request body as context comes from user_id.
    This is a placeholder for future extensibility.
    """

    class Config:
        from_attributes = True


class AskQuestionRequest(BaseModel):
    """Request schema for asking financial questions."""

    question: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Financial question to ask (10-500 characters)",
        json_schema_extra={
            "example": "How much should I contribute to my pension to maximize tax relief?"
        }
    )

    @field_validator('question')
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate question length and content."""
        if not v.strip():
            raise ValueError("Question cannot be empty")

        # Remove extra whitespace
        v = " ".join(v.split())

        if len(v) < 10:
            raise ValueError("Question must be at least 10 characters")

        if len(v) > 500:
            raise ValueError("Question must be at most 500 characters")

        return v

    class Config:
        from_attributes = True


class RecommendationItem(BaseModel):
    """Individual recommendation within advice response."""

    action: str = Field(
        ...,
        description="Recommended action to take"
    )
    reason: str = Field(
        ...,
        description="Reasoning behind the recommendation"
    )
    impact: str = Field(
        ...,
        description="Expected impact or benefit"
    )

    class Config:
        from_attributes = True


class AdviceResponse(BaseModel):
    """
    Response schema for AI advice endpoints.

    Contains:
    - Main advice text (conversational, educational)
    - Structured recommendations (actionable steps)
    - Confidence score (0.0-1.0)
    - Human review flag (true if complex/uncertain)
    - Sources referenced
    - Mandatory disclaimer
    - Metadata (model, tokens, etc.)
    """

    advice: str = Field(
        ...,
        description="Human-readable advice text with clear explanations"
    )
    recommendations: List[RecommendationItem] = Field(
        default=[],
        description="List of structured, actionable recommendations"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score 0.0-1.0 (higher is more confident)"
    )
    requires_human_review: bool = Field(
        ...,
        description="True if advice is complex/uncertain and should be reviewed by advisor"
    )
    sources: List[str] = Field(
        default=[],
        description="List of rules, regulations, or sources referenced"
    )
    disclaimer: str = Field(
        default=(
            "This advice is for informational purposes only and does not constitute "
            "regulated financial advice. Please consult a qualified financial advisor "
            "for personalized recommendations."
        ),
        description="Mandatory disclaimer for all AI advice"
    )
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when advice was generated"
    )
    metadata: Dict[str, Any] = Field(
        default={},
        description="Additional metadata (model version, tokens used, etc.)"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "advice": "Based on your current pension pot of £250,000 and 15 years to retirement, you're on track to meet your retirement goals. However, increasing your contributions by £100/month could boost your retirement income by £15,000/year.",
                "recommendations": [
                    {
                        "action": "Increase pension contributions by £100/month",
                        "reason": "Maximize tax relief at 40% while in higher rate band",
                        "impact": "Additional £50,000 in retirement pot (with growth)"
                    },
                    {
                        "action": "Consider salary sacrifice arrangement",
                        "reason": "Save National Insurance contributions (13.8%)",
                        "impact": "Additional £1,200/year saved"
                    }
                ],
                "confidence_score": 0.85,
                "requires_human_review": False,
                "sources": [
                    "UK pension annual allowance rules",
                    "Salary sacrifice regulations"
                ],
                "disclaimer": "This advice is for informational purposes only...",
                "generated_at": "2025-10-04T10:00:00Z",
                "metadata": {
                    "model": "gpt-4",
                    "tokens_used": 450
                }
            }
        }


class AlertResponse(BaseModel):
    """
    Response schema for proactive alerts.

    Alerts are AI-generated notifications about:
    - Important financial changes (spending spikes, balance drops)
    - Opportunities (unused allowances, tax optimization)
    - Deadlines (tax year end, goal milestones)
    """

    id: UUID = Field(
        ...,
        description="Alert unique identifier"
    )
    alert_type: str = Field(
        ...,
        description="Alert type (ALLOWANCE, GOAL, TAX, SPENDING, INVESTMENT, RETIREMENT)"
    )
    urgency: str = Field(
        ...,
        description="Alert urgency (HIGH, MEDIUM, LOW)"
    )
    message: str = Field(
        ...,
        description="Alert message text (conversational, actionable)"
    )
    action_url: Optional[str] = Field(
        None,
        description="Optional URL to take action (e.g., /goals/123)"
    )
    created_at: datetime = Field(
        ...,
        description="When alert was created"
    )
    read_at: Optional[datetime] = Field(
        None,
        description="When alert was marked as read (null if unread)"
    )
    dismissed_at: Optional[datetime] = Field(
        None,
        description="When alert was dismissed (null if not dismissed)"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "alert_type": "ALLOWANCE",
                "urgency": "HIGH",
                "message": "You've used only £5,000 of your £20,000 ISA allowance. The tax year ends in 45 days - consider transferring from your General Investment Account to save tax.",
                "action_url": "/savings/isa",
                "created_at": "2025-10-04T10:00:00Z",
                "read_at": None,
                "dismissed_at": None
            }
        }


class AlertListResponse(BaseModel):
    """Response schema for list of alerts."""

    alerts: List[AlertResponse] = Field(
        default=[],
        description="List of alerts matching filters"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of alerts"
    )
    unread_count: int = Field(
        ...,
        ge=0,
        description="Number of unread alerts"
    )

    class Config:
        from_attributes = True


class AlertGenerationSummary(BaseModel):
    """Summary response for alert generation (admin endpoint)."""

    users_analyzed: int = Field(
        ...,
        ge=0,
        description="Number of users analyzed"
    )
    alerts_generated: int = Field(
        ...,
        ge=0,
        description="Total number of alerts generated"
    )
    errors: int = Field(
        default=0,
        ge=0,
        description="Number of errors encountered"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When generation was triggered"
    )

    class Config:
        from_attributes = True


class MonthlyInsightsResponse(BaseModel):
    """
    Response schema for monthly insights generation.

    Monthly insights provide a personalized summary of:
    - Financial wins (achievements, milestones)
    - Concerns (falling behind, unusual patterns)
    - Trends (spending, saving, investing)
    - Actionable recommendations for next month
    """

    advice: str = Field(
        ...,
        description="Monthly summary with encouraging, conversational tone"
    )
    recommendations: List[RecommendationItem] = Field(
        default=[],
        description="Key recommendations for next month"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for insights"
    )
    requires_human_review: bool = Field(
        default=False,
        description="Monthly insights rarely need human review"
    )
    sources: List[str] = Field(
        default=["Personal financial data analysis"],
        description="Data sources for insights"
    )
    metadata: Dict[str, Any] = Field(
        default={},
        description="Additional metadata (period, generated_at, etc.)"
    )

    class Config:
        from_attributes = True
