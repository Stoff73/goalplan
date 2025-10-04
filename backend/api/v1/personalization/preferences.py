"""
Personalization API Endpoints

Provides REST API for:
- User preference management (save/retrieve)
- Behavior tracking
- Personalized dashboard layout
- Personalized insights generation

All endpoints require authentication via JWT token.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from database import get_db
from middleware.auth import get_current_user
from schemas.personalization import (
    PreferenceCreate,
    PreferenceUpdate,
    PreferenceResponse,
    BehaviorTrackRequest,
    PersonalizedDashboardResponse,
    InsightResponse,
    PreferencesDictResponse,
    BehaviorAnalysisResponse
)
from services.personalization.preference_service import PreferenceService

router = APIRouter()


@router.get("/preferences", response_model=PreferencesDictResponse)
async def get_user_preferences(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all user preferences with defaults.

    Returns a dictionary with all preference types and their values.
    If a preference hasn't been set, returns the default value.

    Response Example:
    {
        "preferences": {
            "DEFAULT_CURRENCY": "GBP",
            "THEME": "light",
            "NOTIFICATION_FREQUENCY": "weekly"
        }
    }
    """
    service = PreferenceService(db)
    preferences = await service.get_preferences(UUID(current_user_id))
    return {"preferences": preferences}


@router.post("/preferences", response_model=PreferenceResponse)
async def save_preference(
    preference: PreferenceCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Save or update a user preference.

    If preference exists, updates value and updated_at timestamp.
    If preference doesn't exist, creates new preference.

    Request Body:
    {
        "preference_type": "DEFAULT_CURRENCY",
        "preference_value": "GBP"
    }

    Returns the saved preference object.
    """
    service = PreferenceService(db)
    pref = await service.save_preference(
        user_id=UUID(current_user_id),
        preference_type=preference.preference_type,
        preference_value=preference.preference_value
    )
    return PreferenceResponse.model_validate(pref)


@router.post("/behavior/track")
async def track_behavior(
    behavior: BehaviorTrackRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Track user behavior action.

    Logs user actions for personalization and analytics.
    Actions are stored asynchronously and don't block the response.

    Request Body:
    {
        "action_type": "PAGE_VIEW",
        "action_context": {
            "page": "dashboard",
            "duration": 45,
            "referrer": "navigation"
        }
    }

    Returns success status.
    """
    service = PreferenceService(db)
    await service.track_behavior(
        user_id=UUID(current_user_id),
        action_type=behavior.action_type,
        action_context=behavior.action_context
    )
    return {"status": "tracked"}


@router.get("/dashboard/personalized", response_model=PersonalizedDashboardResponse)
async def get_personalized_dashboard(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized dashboard layout.

    Returns dashboard widget order based on user behavior.
    Widgets are ordered by frequency of use (most used first).
    Widgets with <5% usage are hidden by default.

    Response Example:
    {
        "widget_order": ["net_worth", "goals", "savings", "investments"],
        "visible_widgets": ["net_worth", "goals", "savings", "investments"],
        "hidden_widgets": ["retirement", "protection"]
    }
    """
    service = PreferenceService(db)
    dashboard = await service.personalize_dashboard(UUID(current_user_id))
    return dashboard


@router.get("/insights", response_model=List[InsightResponse])
async def get_personalized_insights(
    limit: int = 10,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized insights.

    Generates insights based on user profile, behavior, and financial data.
    Insights are ranked by relevance score (0-100).

    Query Parameters:
    - limit: Maximum number of insights to return (default: 10)

    Returns list of insights ordered by relevance (highest first).
    """
    service = PreferenceService(db)
    insights = await service.generate_personalized_insights(
        user_id=UUID(current_user_id),
        limit=limit
    )
    return [InsightResponse.model_validate(i) for i in insights]


@router.get("/behavior/analysis", response_model=BehaviorAnalysisResponse)
async def get_behavior_analysis(
    days: int = 30,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get behavior analysis for user.

    Analyzes user behavior over the last N days.
    Provides engagement metrics and usage patterns.

    Query Parameters:
    - days: Number of days to analyze (default: 30)

    Response Example:
    {
        "most_viewed_pages": ["dashboard", "goals", "savings"],
        "most_used_features": ["goal_tracking", "account_management"],
        "engagement_score": 75,
        "total_actions": 150
    }
    """
    service = PreferenceService(db)
    analysis = await service.analyze_behavior(UUID(current_user_id), days)
    return analysis
