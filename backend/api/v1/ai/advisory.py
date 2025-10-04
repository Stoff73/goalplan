"""
AI Advisory API endpoints.

This module provides RESTful API for AI-powered financial advisory features:
- POST /retirement-advice - Get personalized retirement planning advice
- POST /investment-advice - Get investment portfolio optimization advice
- POST /tax-advice - Get tax optimization strategies
- POST /goal-advice/{goal_id} - Get goal-specific achievement advice
- POST /ask - Ask any financial question
- GET /monthly-insights - Get monthly financial summary
- GET /alerts - Get proactive alerts with filtering
- POST /alerts/{id}/mark-read - Mark alert as read
- POST /alerts/{id}/dismiss - Dismiss an alert
- POST /alerts/generate - Trigger alert generation (admin only)

All endpoints:
- Require authentication
- Include rate limiting
- Return comprehensive error responses
- Include mandatory disclaimers on advice
- Log all requests for audit trail
"""

import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from database import get_db
from middleware.auth import get_current_user, get_current_active_user
from models.recommendation import Recommendation, RecommendationPriority
from models.goal import FinancialGoal
from models.user import User
from schemas.ai import (
    AdviceRequest,
    AskQuestionRequest,
    AdviceResponse,
    AlertResponse,
    AlertListResponse,
    AlertGenerationSummary,
    MonthlyInsightsResponse,
    RecommendationItem
)
from services.ai.advisory_service import AIAdvisoryService
from services.ai.proactive_alerts_service import ProactiveAlertsService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# AI ADVICE ENDPOINTS
# ============================================================================

@router.post(
    "/retirement-advice",
    response_model=AdviceResponse,
    summary="Get retirement planning advice",
    description=(
        "Generate personalized retirement planning advice based on current "
        "pension pot, contributions, age, and retirement goals. "
        "Rate limit: 5 requests per hour."
    )
)
async def get_retirement_advice(
    request: Request,
    data: AdviceRequest = AdviceRequest(),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate personalized retirement planning advice.

    Analyzes:
    - Current pension pot size
    - Annual contributions
    - Expected retirement age
    - Income replacement needs
    - UK/SA pension rules and allowances

    Returns:
        AdviceResponse: Retirement advice with actionable recommendations

    Raises:
        401: Unauthorized
        429: Too many requests (rate limit exceeded)
        500: Internal server error
    """
    try:
        logger.info(f"Generating retirement advice for user {current_user_id}")

        service = AIAdvisoryService(db)
        advice_data = await service.generate_retirement_advice(UUID(current_user_id))

        # Map to response schema
        response = AdviceResponse(
            advice=advice_data["advice"],
            recommendations=[
                RecommendationItem(**rec) for rec in advice_data["recommendations"]
            ],
            confidence_score=advice_data["confidence_score"],
            requires_human_review=advice_data["requires_human_review"],
            sources=advice_data["sources"],
            metadata=advice_data.get("metadata", {})
        )

        logger.info(
            f"Retirement advice generated for user {current_user_id} "
            f"(confidence: {response.confidence_score:.2f})"
        )

        return response

    except Exception as e:
        logger.error(f"Failed to generate retirement advice: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate retirement advice"
        )


@router.post(
    "/investment-advice",
    response_model=AdviceResponse,
    summary="Get investment advice",
    description=(
        "Generate personalized investment advice based on portfolio allocation, "
        "diversification, risk tolerance, and tax efficiency. "
        "Rate limit: 5 requests per hour."
    )
)
async def get_investment_advice(
    request: Request,
    data: AdviceRequest = AdviceRequest(),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate personalized investment advice.

    Analyzes:
    - Portfolio allocation (equity/bonds/cash)
    - Diversification across asset classes
    - Tax efficiency (ISA/GIA usage)
    - Risk tolerance vs. actual allocation
    - Investment horizon

    Returns:
        AdviceResponse: Investment advice with portfolio optimization recommendations

    Raises:
        401: Unauthorized
        429: Too many requests
        500: Internal server error
    """
    try:
        logger.info(f"Generating investment advice for user {current_user_id}")

        service = AIAdvisoryService(db)
        advice_data = await service.generate_investment_advice(UUID(current_user_id))

        response = AdviceResponse(
            advice=advice_data["advice"],
            recommendations=[
                RecommendationItem(**rec) for rec in advice_data["recommendations"]
            ],
            confidence_score=advice_data["confidence_score"],
            requires_human_review=advice_data["requires_human_review"],
            sources=advice_data["sources"],
            metadata=advice_data.get("metadata", {})
        )

        logger.info(
            f"Investment advice generated for user {current_user_id} "
            f"(confidence: {response.confidence_score:.2f})"
        )

        return response

    except Exception as e:
        logger.error(f"Failed to generate investment advice: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate investment advice"
        )


@router.post(
    "/tax-advice",
    response_model=AdviceResponse,
    summary="Get tax optimization advice",
    description=(
        "Generate tax optimization strategies based on income, allowances used, "
        "tax residency status, and available deductions/reliefs. "
        "Rate limit: 5 requests per hour."
    )
)
async def get_tax_optimization_advice(
    request: Request,
    data: AdviceRequest = AdviceRequest(),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate tax optimization advice.

    Analyzes:
    - Income sources and levels
    - Allowances used (ISA, pension, CGT, etc.)
    - Tax residency status (UK/SA/both)
    - Deductions and reliefs available
    - Double Tax Agreement opportunities

    Returns:
        AdviceResponse: Tax optimization strategies with estimated savings

    Raises:
        401: Unauthorized
        429: Too many requests
        500: Internal server error
    """
    try:
        logger.info(f"Generating tax optimization advice for user {current_user_id}")

        service = AIAdvisoryService(db)
        advice_data = await service.generate_tax_optimization_advice(UUID(current_user_id))

        response = AdviceResponse(
            advice=advice_data["advice"],
            recommendations=[
                RecommendationItem(**rec) for rec in advice_data["recommendations"]
            ],
            confidence_score=advice_data["confidence_score"],
            requires_human_review=advice_data["requires_human_review"],
            sources=advice_data["sources"],
            metadata=advice_data.get("metadata", {})
        )

        logger.info(
            f"Tax optimization advice generated for user {current_user_id} "
            f"(confidence: {response.confidence_score:.2f})"
        )

        return response

    except Exception as e:
        logger.error(f"Failed to generate tax optimization advice: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate tax optimization advice"
        )


@router.post(
    "/goal-advice/{goal_id}",
    response_model=AdviceResponse,
    summary="Get goal-specific advice",
    description=(
        "Generate advice for achieving a specific financial goal faster. "
        "Rate limit: 10 requests per hour."
    )
)
async def get_goal_advice(
    request: Request,
    goal_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate advice for achieving a specific goal.

    Analyzes:
    - Goal target and deadline
    - Current progress
    - Required monthly savings
    - Strategies to accelerate achievement
    - Tax-advantaged savings options

    Args:
        goal_id: Financial goal UUID

    Returns:
        AdviceResponse: Strategies to achieve goal faster

    Raises:
        401: Unauthorized
        403: Forbidden (goal doesn't belong to user)
        404: Goal not found
        429: Too many requests
        500: Internal server error
    """
    try:
        logger.info(f"Generating goal advice for goal {goal_id}, user {current_user_id}")

        # Verify goal exists and belongs to user
        result = await db.execute(
            select(FinancialGoal).where(
                and_(
                    FinancialGoal.id == goal_id,
                    FinancialGoal.deleted_at.is_(None)
                )
            )
        )
        goal = result.scalar_one_or_none()

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Goal {goal_id} not found"
            )

        if str(goal.user_id) != current_user_id:
            logger.warning(
                f"User {current_user_id} attempted to access goal {goal_id} "
                f"belonging to user {goal.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this goal"
            )

        # Generate advice
        service = AIAdvisoryService(db)
        advice_data = await service.generate_goal_advice(goal_id)

        response = AdviceResponse(
            advice=advice_data["advice"],
            recommendations=[
                RecommendationItem(**rec) for rec in advice_data["recommendations"]
            ],
            confidence_score=advice_data["confidence_score"],
            requires_human_review=advice_data["requires_human_review"],
            sources=advice_data["sources"],
            metadata=advice_data.get("metadata", {})
        )

        logger.info(
            f"Goal advice generated for goal {goal_id}, user {current_user_id} "
            f"(confidence: {response.confidence_score:.2f})"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate goal advice: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate goal advice"
        )


@router.post(
    "/ask",
    response_model=AdviceResponse,
    summary="Ask a financial question",
    description=(
        "Ask any financial question and get a personalized answer based on "
        "your financial situation. Rate limit: 10 requests per hour."
    )
)
async def ask_financial_question(
    request: Request,
    data: AskQuestionRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Ask a free-form financial question.

    Accepts any financial question (10-500 characters) and provides a
    personalized answer based on the user's complete financial context.

    Args:
        data: Question request with validated question text

    Returns:
        AdviceResponse: Personalized answer to the question

    Raises:
        400: Invalid question (too short/long or invalid content)
        401: Unauthorized
        429: Too many requests
        500: Internal server error
    """
    try:
        logger.info(
            f"Answering financial question for user {current_user_id}: "
            f"{data.question[:50]}..."
        )

        service = AIAdvisoryService(db)
        advice_data = await service.answer_financial_question(
            user_id=UUID(current_user_id),
            question=data.question
        )

        response = AdviceResponse(
            advice=advice_data["advice"],
            recommendations=[
                RecommendationItem(**rec) for rec in advice_data["recommendations"]
            ],
            confidence_score=advice_data["confidence_score"],
            requires_human_review=advice_data["requires_human_review"],
            sources=advice_data["sources"],
            metadata=advice_data.get("metadata", {})
        )

        logger.info(
            f"Question answered for user {current_user_id} "
            f"(confidence: {response.confidence_score:.2f})"
        )

        return response

    except ValueError as e:
        logger.warning(f"Invalid question from user {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to answer question: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to answer question"
        )


@router.get(
    "/monthly-insights",
    response_model=MonthlyInsightsResponse,
    summary="Get monthly financial insights",
    description=(
        "Generate monthly financial summary with wins, concerns, trends, and "
        "recommendations. Rate limit: 3 requests per day."
    )
)
async def get_monthly_insights(
    request: Request,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate monthly financial insights.

    Analyzes changes over the past month:
    - Income and expense patterns
    - Net worth changes
    - Goal progress
    - Notable transactions

    Returns personalized monthly summary with:
    - Wins (achievements, milestones)
    - Concerns (falling behind, unusual patterns)
    - Trends (spending, saving, investing)
    - Recommendations for next month

    Returns:
        MonthlyInsightsResponse: Monthly summary and recommendations

    Raises:
        401: Unauthorized
        429: Too many requests
        500: Internal server error
    """
    try:
        logger.info(f"Generating monthly insights for user {current_user_id}")

        service = AIAdvisoryService(db)
        insights_data = await service.generate_monthly_insights(UUID(current_user_id))

        response = MonthlyInsightsResponse(
            advice=insights_data["advice"],
            recommendations=[
                RecommendationItem(**rec) for rec in insights_data["recommendations"]
            ],
            confidence_score=insights_data["confidence_score"],
            requires_human_review=insights_data.get("requires_human_review", False),
            sources=insights_data.get("sources", ["Personal financial data analysis"]),
            metadata=insights_data.get("metadata", {})
        )

        logger.info(
            f"Monthly insights generated for user {current_user_id} "
            f"(confidence: {response.confidence_score:.2f})"
        )

        return response

    except Exception as e:
        logger.error(f"Failed to generate monthly insights: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate monthly insights"
        )


# ============================================================================
# ALERT ENDPOINTS
# ============================================================================

@router.get(
    "/alerts",
    response_model=AlertListResponse,
    summary="Get proactive alerts",
    description=(
        "Get list of proactive financial alerts with optional filtering by "
        "unread status, urgency, and date range."
    )
)
async def get_alerts(
    current_user_id: str = Depends(get_current_user),
    unread_only: bool = Query(
        False,
        description="Filter to show only unread alerts"
    ),
    urgency: Optional[str] = Query(
        None,
        description="Filter by urgency (HIGH, MEDIUM, LOW)"
    ),
    from_date: Optional[datetime] = Query(
        None,
        description="Filter alerts created on or after this date"
    ),
    limit: int = Query(
        50,
        ge=1,
        le=100,
        description="Maximum number of alerts to return (1-100)"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Get proactive alerts for the authenticated user.

    Alerts include:
    - Unused allowances (ISA, TFSA)
    - Goal milestones and falling behind warnings
    - Tax optimization opportunities
    - Spending pattern changes
    - Investment rebalancing suggestions
    - Pension contribution opportunities

    Supports filtering by:
    - Unread status
    - Urgency level
    - Date range
    - Limit (pagination)

    Returns:
        AlertListResponse: List of alerts with total and unread count

    Raises:
        401: Unauthorized
        500: Internal server error
    """
    try:
        logger.info(
            f"Retrieving alerts for user {current_user_id} "
            f"(unread_only={unread_only}, urgency={urgency}, limit={limit})"
        )

        # Build query
        query = select(Recommendation).where(
            and_(
                Recommendation.user_id == UUID(current_user_id),
                Recommendation.deleted == False
            )
        )

        # Apply filters
        if unread_only:
            query = query.where(Recommendation.dismissed == False)

        if urgency:
            try:
                priority = RecommendationPriority[urgency]
                query = query.where(Recommendation.priority == priority)
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid urgency: {urgency}. Must be HIGH, MEDIUM, or LOW"
                )

        if from_date:
            query = query.where(Recommendation.created_date >= from_date)

        # Sort by urgency (HIGH first), then created_date DESC
        query = query.order_by(
            Recommendation.priority.desc(),
            Recommendation.created_date.desc()
        )

        # Apply limit
        query = query.limit(limit)

        # Execute query
        result = await db.execute(query)
        alerts = result.scalars().all()

        # Get total count
        count_query = select(func.count()).select_from(Recommendation).where(
            and_(
                Recommendation.user_id == UUID(current_user_id),
                Recommendation.deleted == False
            )
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get unread count
        unread_query = select(func.count()).select_from(Recommendation).where(
            and_(
                Recommendation.user_id == UUID(current_user_id),
                Recommendation.deleted == False,
                Recommendation.dismissed == False
            )
        )
        unread_result = await db.execute(unread_query)
        unread_count = unread_result.scalar()

        # Map to response
        alert_responses = [
            AlertResponse(
                id=alert.id,
                alert_type=alert.recommendation_type.value,
                urgency=alert.priority.value,
                message=alert.description,
                action_url=None,  # Would be populated from action_items if available
                created_at=alert.created_date,
                read_at=alert.dismissed_date if alert.dismissed else None,
                dismissed_at=alert.dismissed_date if alert.dismissed else None
            )
            for alert in alerts
        ]

        logger.info(
            f"Retrieved {len(alert_responses)} alerts for user {current_user_id} "
            f"(total={total}, unread={unread_count})"
        )

        return AlertListResponse(
            alerts=alert_responses,
            total=total,
            unread_count=unread_count
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve alerts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts"
        )


@router.post(
    "/alerts/{alert_id}/mark-read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark alert as read",
    description="Mark a specific alert as read (sets read_at timestamp)"
)
async def mark_alert_as_read(
    alert_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark an alert as read.

    Updates the alert's dismissed_date to now (reusing dismissed field
    for read tracking).

    Args:
        alert_id: Alert UUID

    Returns:
        204 No Content on success

    Raises:
        401: Unauthorized
        403: Forbidden (alert doesn't belong to user)
        404: Alert not found
        500: Internal server error
    """
    try:
        logger.info(f"Marking alert {alert_id} as read for user {current_user_id}")

        # Get alert
        result = await db.execute(
            select(Recommendation).where(
                and_(
                    Recommendation.id == alert_id,
                    Recommendation.deleted == False
                )
            )
        )
        alert = result.scalar_one_or_none()

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert {alert_id} not found"
            )

        if str(alert.user_id) != current_user_id:
            logger.warning(
                f"User {current_user_id} attempted to access alert {alert_id} "
                f"belonging to user {alert.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this alert"
            )

        # Mark as read (using dismiss method)
        if not alert.dismissed:
            alert.dismiss()
            await db.commit()

        logger.info(f"Alert {alert_id} marked as read for user {current_user_id}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to mark alert as read: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark alert as read"
        )


@router.post(
    "/alerts/{alert_id}/dismiss",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Dismiss alert",
    description="Dismiss a specific alert (permanently hides it from list)"
)
async def dismiss_alert(
    alert_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Dismiss an alert.

    Dismisses the alert and hides it from the default alert list.

    Args:
        alert_id: Alert UUID

    Returns:
        204 No Content on success

    Raises:
        401: Unauthorized
        403: Forbidden (alert doesn't belong to user)
        404: Alert not found
        500: Internal server error
    """
    try:
        logger.info(f"Dismissing alert {alert_id} for user {current_user_id}")

        # Get alert
        result = await db.execute(
            select(Recommendation).where(
                and_(
                    Recommendation.id == alert_id,
                    Recommendation.deleted == False
                )
            )
        )
        alert = result.scalar_one_or_none()

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert {alert_id} not found"
            )

        if str(alert.user_id) != current_user_id:
            logger.warning(
                f"User {current_user_id} attempted to dismiss alert {alert_id} "
                f"belonging to user {alert.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to dismiss this alert"
            )

        # Dismiss alert
        alert.dismiss()
        await db.commit()

        logger.info(f"Alert {alert_id} dismissed for user {current_user_id}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to dismiss alert: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to dismiss alert"
        )


@router.post(
    "/alerts/generate",
    response_model=AlertGenerationSummary,
    summary="Trigger alert generation (Admin only)",
    description=(
        "Manually trigger daily alert analysis and generation for all users. "
        "Admin authentication required. No rate limit."
    )
)
async def trigger_alert_generation(
    current_user_id: str = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger alert generation for all users (admin only).

    Runs daily analysis:
    1. Analyze past 30 days for changes
    2. Identify opportunities
    3. Generate alerts
    4. Store in database

    This is typically run as a background cron job, but can be manually
    triggered by admin users for testing or immediate updates.

    Returns:
        AlertGenerationSummary: Summary of alerts generated

    Raises:
        401: Unauthorized
        403: Forbidden (user is not admin)
        500: Internal server error
    """
    try:
        # Check if user is admin
        result = await db.execute(
            select(User).where(User.id == UUID(current_user_id))
        )
        user = result.scalar_one_or_none()

        if not user or user.role != "admin":
            logger.warning(
                f"Non-admin user {current_user_id} attempted to trigger alert generation"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )

        logger.info(f"Triggering alert generation (requested by admin {current_user_id})")

        service = ProactiveAlertsService(db)
        summary = await service.schedule_daily_analysis()

        logger.info(
            f"Alert generation complete: {summary['users_analyzed']} users, "
            f"{summary['alerts_generated']} alerts, {summary['errors']} errors"
        )

        return AlertGenerationSummary(
            users_analyzed=summary["users_analyzed"],
            alerts_generated=summary["alerts_generated"],
            errors=summary["errors"],
            timestamp=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger alert generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger alert generation"
        )
