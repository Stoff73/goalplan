"""
Recommendations API endpoints.

This module provides RESTful API for AI-driven financial recommendations:
- GET /recommendations - Retrieve user's recommendations with filtering
- POST /recommendations/generate - Generate new recommendations
- POST /recommendations/{id}/dismiss - Dismiss a recommendation
- POST /recommendations/{id}/complete - Mark recommendation as completed

Business logic:
- Rule-based recommendation engine (Phase 2)
- AI/ML integration planned for Phase 4
- User authorization enforced (can only access own recommendations)
- Filtering by priority (HIGH/MEDIUM/LOW) and type
- Idempotent generation (check if recent recommendations exist)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import logging

from database import get_db
from middleware.auth import get_current_user
from models.recommendation import RecommendationPriority, RecommendationType
from schemas.recommendation import (
    RecommendationResponse,
    GenerateRecommendationsRequest,
    BulkRecommendationsResponse
)
from services.ai.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# RECOMMENDATION RETRIEVAL
# ============================================================================

@router.get("/", response_model=List[RecommendationResponse])
async def get_recommendations(
    current_user_id: str = Depends(get_current_user),
    priority: Optional[RecommendationPriority] = Query(
        None,
        description="Filter by priority (HIGH, MEDIUM, LOW)"
    ),
    type: Optional[RecommendationType] = Query(
        None,
        alias="type",
        description="Filter by recommendation type"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all active recommendations for the authenticated user.

    Retrieves recommendations with optional filtering by priority and type.
    Returns only active recommendations (not dismissed, not deleted).
    Results sorted by priority (HIGH first), then created_date DESC.

    Args:
        current_user_id: Authenticated user ID
        priority: Optional priority filter (HIGH, MEDIUM, LOW)
        type: Optional type filter (PROTECTION, ISA, TFSA, etc.)
        db: Database session

    Returns:
        List[RecommendationResponse]: List of recommendations matching filters

    Raises:
        401: Unauthorized (no valid token)
        500: Internal server error
    """
    try:
        # Get recommendation service
        service = RecommendationService(db)

        # Retrieve recommendations with filters
        recommendations = await service.get_user_recommendations(
            user_id=UUID(current_user_id),
            priority=priority,
            recommendation_type=type
        )

        # Map to response schemas
        responses = [
            RecommendationResponse.model_validate(rec)
            for rec in recommendations
        ]

        logger.info(
            f"Retrieved {len(responses)} recommendations for user {current_user_id} "
            f"(priority={priority}, type={type})"
        )

        return responses

    except Exception as e:
        logger.error(f"Failed to retrieve recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recommendations"
        )


# ============================================================================
# RECOMMENDATION GENERATION
# ============================================================================

@router.post("/generate", response_model=BulkRecommendationsResponse, status_code=status.HTTP_201_CREATED)
async def generate_recommendations(
    data: GenerateRecommendationsRequest = GenerateRecommendationsRequest(),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate new recommendations for the authenticated user.

    Analyzes user's complete financial data and generates personalized
    recommendations across all modules (protection, ISA, TFSA, emergency fund, etc.).

    This is an idempotent operation - will analyze current financial state
    and create new recommendations. Consider checking for recent recommendations
    before calling to avoid duplicates.

    Args:
        data: Generation request (optional base_currency)
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        BulkRecommendationsResponse: List of newly created recommendations

    Raises:
        400: Validation error (invalid user or data)
        401: Unauthorized
        500: Internal server error
    """
    try:
        # Get recommendation service
        service = RecommendationService(db)

        # Generate recommendations
        recommendations = await service.generate_recommendations(
            user_id=UUID(current_user_id),
            base_currency=data.base_currency
        )

        # Persist recommendations to database
        for rec in recommendations:
            db.add(rec)

        await db.commit()

        # Refresh to get IDs
        for rec in recommendations:
            await db.refresh(rec)

        # Map to response schemas
        responses = [
            RecommendationResponse.model_validate(rec)
            for rec in recommendations
        ]

        logger.info(
            f"Generated {len(responses)} recommendations for user {current_user_id} "
            f"(base_currency={data.base_currency})"
        )

        return BulkRecommendationsResponse(
            recommendations=responses,
            count=len(responses)
        )

    except ValueError as e:
        logger.error(f"Validation error generating recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to generate recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations"
        )


# ============================================================================
# RECOMMENDATION ACTIONS
# ============================================================================

@router.post("/{recommendation_id}/dismiss", response_model=RecommendationResponse)
async def dismiss_recommendation(
    recommendation_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Dismiss a recommendation.

    Sets dismissed=True and dismissed_date=now. Dismissed recommendations
    are excluded from default retrieval but can still be accessed via API.

    Args:
        recommendation_id: Recommendation UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        RecommendationResponse: Updated recommendation

    Raises:
        401: Unauthorized
        403: Forbidden (user doesn't own recommendation)
        404: Recommendation not found
        500: Internal server error
    """
    try:
        # Get recommendation service
        service = RecommendationService(db)

        # Dismiss recommendation (service handles ownership check)
        recommendation = await service.dismiss_recommendation(
            recommendation_id=recommendation_id,
            user_id=UUID(current_user_id)
        )

        logger.info(
            f"User {current_user_id} dismissed recommendation {recommendation_id}"
        )

        return RecommendationResponse.model_validate(recommendation)

    except ValueError as e:
        logger.warning(f"Recommendation not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        logger.warning(f"Permission denied: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to dismiss recommendation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to dismiss recommendation"
        )


@router.post("/{recommendation_id}/complete", response_model=RecommendationResponse)
async def complete_recommendation(
    recommendation_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a recommendation as completed.

    Sets completed=True and completed_date=now. Completed recommendations
    indicate the user has acted on the advice.

    Args:
        recommendation_id: Recommendation UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        RecommendationResponse: Updated recommendation

    Raises:
        401: Unauthorized
        403: Forbidden (user doesn't own recommendation)
        404: Recommendation not found
        500: Internal server error
    """
    try:
        # Get recommendation service
        service = RecommendationService(db)

        # Complete recommendation (service handles ownership check)
        recommendation = await service.complete_recommendation(
            recommendation_id=recommendation_id,
            user_id=UUID(current_user_id)
        )

        logger.info(
            f"User {current_user_id} completed recommendation {recommendation_id}"
        )

        return RecommendationResponse.model_validate(recommendation)

    except ValueError as e:
        logger.warning(f"Recommendation not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        logger.warning(f"Permission denied: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to complete recommendation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete recommendation"
        )
