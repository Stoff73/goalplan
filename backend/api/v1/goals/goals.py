"""
Goals API endpoints.

This module provides RESTful API for financial goal planning:
- POST /goals - Create financial goal
- GET /goals - List user goals with filtering
- GET /goals/{id} - Get single goal with details
- PUT /goals/{id} - Update goal
- POST /goals/{id}/milestones - Add milestone
- POST /goals/{id}/link-account - Link account to goal
- GET /goals/overview - Goals dashboard summary
- POST /goals/optimize - Optimize goal allocation

Business logic:
- SMART criteria validation (done in schemas)
- Maximum 10 active goals per user
- User authorization enforced (can only access own goals)
- Progress tracking from linked accounts
- Milestone achievement detection
- Intelligent prioritization and allocation
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
import logging

from database import get_db
from middleware.auth import get_current_user
from models.goal import (
    FinancialGoal, GoalMilestone, GoalRecommendation,
    GoalType, GoalPriority, GoalStatus
)
from schemas.goal import (
    CreateGoalRequest, UpdateGoalRequest, GoalResponse,
    GoalSummaryResponse, CreateMilestoneRequest, MilestoneResponse,
    RecommendationResponse, GoalStatistics
)
from services.goals.goal_service import (
    get_goal_service, ValidationError, NotFoundError, GoalLimitError
)
from services.goals.goal_optimization_service import get_goal_optimization_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# GOAL CREATION AND MANAGEMENT
# ============================================================================

@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    data: CreateGoalRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new financial goal with SMART criteria validation.

    Creates a financial goal for the authenticated user with:
    - SMART criteria validation (Specific, Measurable, Achievable, Relevant, Time-bound)
    - Target amount and date
    - Priority and optional auto-contribution settings
    - Initial progress tracking

    Business Rules:
    - Goal target date must be at least 6 months in the future (max 50 years)
    - Maximum 10 active goals per user
    - Target amount must be positive
    - Auto-contribution requires amount and frequency

    Args:
        data: Goal creation data (validated by schema)
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        GoalResponse: Created goal with all details

    Raises:
        400: Validation error (invalid data, goal limit exceeded)
        401: Unauthorized
        500: Internal server error
    """
    try:
        # Get goal service
        service = get_goal_service(db)

        # Create goal
        goal = await service.create_goal(
            user_id=UUID(current_user_id),
            goal_data=data
        )

        # Calculate additional fields for response
        goal_dict = {
            **goal.__dict__,
            "days_remaining": goal.days_remaining(),
            "on_track": goal.is_on_track()
        }
        response = GoalResponse.model_validate(goal_dict)

        logger.info(
            f"Goal created: id={goal.id}, user={current_user_id}, "
            f"name={goal.goal_name}, target={goal.target_amount}"
        )

        return response

    except GoalLimitError as e:
        logger.warning(f"Goal limit exceeded for user {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValidationError as e:
        logger.warning(f"Goal validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create goal: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create goal"
        )


@router.get("", response_model=List[GoalSummaryResponse])
async def list_goals(
    current_user_id: str = Depends(get_current_user),
    goal_type: Optional[GoalType] = Query(None, description="Filter by goal type"),
    status_filter: Optional[GoalStatus] = Query(None, alias="status", description="Filter by status"),
    priority: Optional[GoalPriority] = Query(None, description="Filter by priority"),
    sort_by: str = Query("priority", description="Sort by: priority, target_date, created_at"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all goals for the authenticated user with filtering and sorting.

    Retrieves user's financial goals with optional filtering by type, status, and priority.
    Results can be sorted by priority, target date, or creation date.

    Args:
        current_user_id: Authenticated user ID
        goal_type: Optional filter by goal type
        status_filter: Optional filter by status
        priority: Optional filter by priority
        sort_by: Sort field (priority, target_date, created_at)
        db: Database session

    Returns:
        List[GoalSummaryResponse]: List of goals (lightweight response)

    Raises:
        401: Unauthorized
        500: Internal server error
    """
    try:
        # Build query
        query = select(FinancialGoal).where(
            and_(
                FinancialGoal.user_id == UUID(current_user_id),
                FinancialGoal.deleted_at.is_(None)
            )
        )

        # Apply filters
        if goal_type:
            query = query.where(FinancialGoal.goal_type == goal_type)
        if status_filter:
            query = query.where(FinancialGoal.status == status_filter)
        if priority:
            query = query.where(FinancialGoal.priority == priority)

        # Apply sorting
        if sort_by == "target_date":
            query = query.order_by(FinancialGoal.target_date.asc())
        elif sort_by == "created_at":
            query = query.order_by(FinancialGoal.created_at.desc())
        else:  # priority (default)
            # Sort by priority (HIGH -> MEDIUM -> LOW), then target_date
            query = query.order_by(
                FinancialGoal.priority.desc(),
                FinancialGoal.target_date.asc()
            )

        # Execute query
        result = await db.execute(query)
        goals = result.scalars().all()

        # Map to summary responses
        responses = []
        for goal in goals:
            goal_dict = {
                **goal.__dict__,
                "on_track": goal.is_on_track()
            }
            response = GoalSummaryResponse.model_validate(goal_dict)
            responses.append(response)

        logger.info(
            f"Retrieved {len(responses)} goals for user {current_user_id} "
            f"(type={goal_type}, status={status_filter}, priority={priority})"
        )

        return responses

    except Exception as e:
        logger.error(f"Failed to retrieve goals: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve goals"
        )


# ============================================================================
# GOAL OVERVIEW AND STATISTICS
# ============================================================================

@router.get("/overview", response_model=GoalStatistics)
async def get_goals_overview(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get goals dashboard overview with statistics.

    Provides summary statistics for all user goals:
    - Total goals count by status
    - Total target and current amounts
    - Overall progress percentage
    - Goals on track vs at risk

    Args:
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        GoalStatistics: Dashboard statistics

    Raises:
        401: Unauthorized
        500: Internal server error
    """
    try:
        # Query all user goals (not deleted)
        result = await db.execute(
            select(FinancialGoal).where(
                and_(
                    FinancialGoal.user_id == UUID(current_user_id),
                    FinancialGoal.deleted_at.is_(None)
                )
            )
        )
        goals = result.scalars().all()

        # Calculate statistics
        total_goals = len(goals)
        active_goals = sum(
            1 for g in goals
            if g.status in [GoalStatus.NOT_STARTED, GoalStatus.IN_PROGRESS, GoalStatus.ON_TRACK, GoalStatus.AT_RISK]
        )
        achieved_goals = sum(1 for g in goals if g.status == GoalStatus.ACHIEVED)

        total_target_amount = sum(g.target_amount for g in goals)
        total_current_amount = sum(g.current_amount for g in goals)

        # Overall progress percentage
        if total_target_amount > 0:
            overall_progress = (total_current_amount / total_target_amount) * Decimal('100')
        else:
            overall_progress = Decimal('0.00')

        # Count on-track and at-risk goals
        on_track_count = sum(1 for g in goals if g.is_on_track() and g.status != GoalStatus.ACHIEVED)
        at_risk_count = sum(1 for g in goals if g.status == GoalStatus.AT_RISK)

        statistics = GoalStatistics(
            total_goals=total_goals,
            active_goals=active_goals,
            achieved_goals=achieved_goals,
            total_target_amount=total_target_amount,
            total_current_amount=total_current_amount,
            overall_progress_percentage=overall_progress.quantize(Decimal('0.01')),
            on_track_count=on_track_count,
            at_risk_count=at_risk_count
        )

        logger.info(f"Goals overview retrieved for user {current_user_id}")

        return statistics

    except Exception as e:
        logger.error(f"Failed to retrieve goals overview: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve goals overview"
        )


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single goal with full details.

    Retrieves complete goal details including:
    - All goal attributes
    - Progress and status information
    - Calculated fields (days remaining, on track status)

    Args:
        goal_id: Goal UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        GoalResponse: Complete goal details

    Raises:
        403: Forbidden (goal belongs to another user)
        404: Goal not found
        401: Unauthorized
        500: Internal server error
    """
    try:
        # Query goal
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
                detail="Goal not found"
            )

        # Check ownership
        if str(goal.user_id) != current_user_id:
            logger.warning(
                f"User {current_user_id} attempted to access goal {goal_id} "
                f"belonging to user {goal.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Build response with calculated fields
        goal_dict = {
            **goal.__dict__,
            "days_remaining": goal.days_remaining(),
            "on_track": goal.is_on_track()
        }
        response = GoalResponse.model_validate(goal_dict)

        logger.info(f"Retrieved goal {goal_id} for user {current_user_id}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve goal: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve goal"
        )


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: UUID,
    data: UpdateGoalRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing financial goal.

    Allows updating goal details including:
    - Target amount and date
    - Priority and status
    - Auto-contribution settings
    - Linked accounts

    Business Rules:
    - Progress and projections recalculated on target changes
    - Cannot change goal_type after creation
    - User can only update own goals

    Args:
        goal_id: Goal UUID
        data: Update data (all fields optional)
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        GoalResponse: Updated goal details

    Raises:
        403: Forbidden (goal belongs to another user)
        404: Goal not found
        400: Validation error
        401: Unauthorized
        500: Internal server error
    """
    try:
        # Query goal
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
                detail="Goal not found"
            )

        # Check ownership
        if str(goal.user_id) != current_user_id:
            logger.warning(
                f"User {current_user_id} attempted to update goal {goal_id} "
                f"belonging to user {goal.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Apply updates
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)

        # Recalculate progress percentage if target_amount changed
        if "target_amount" in update_data:
            goal.progress_percentage = goal.calculate_progress_percentage()

        await db.commit()
        await db.refresh(goal)

        # Update progress if significant changes
        if "target_amount" in update_data or "target_date" in update_data:
            service = get_goal_service(db)
            await service.update_goal_progress(goal_id)
            await db.refresh(goal)

        # Build response
        goal_dict = {
            **goal.__dict__,
            "days_remaining": goal.days_remaining(),
            "on_track": goal.is_on_track()
        }
        response = GoalResponse.model_validate(goal_dict)

        logger.info(f"Goal updated: id={goal_id}, user={current_user_id}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update goal: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update goal"
        )


# ============================================================================
# MILESTONE MANAGEMENT
# ============================================================================

@router.post("/{goal_id}/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def add_milestone(
    goal_id: UUID,
    data: CreateMilestoneRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a milestone to a financial goal.

    Creates a milestone for tracking progress toward a goal with:
    - Target amount and date
    - Achievement status tracking
    - Validation against goal constraints

    Business Rules:
    - Milestone date must be between goal start and target dates
    - Milestone amount must not exceed goal target amount
    - Milestones automatically marked as achieved if current progress sufficient

    Args:
        goal_id: Goal UUID
        data: Milestone creation data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        MilestoneResponse: Created milestone

    Raises:
        403: Forbidden (goal belongs to another user)
        404: Goal not found
        400: Validation error
        401: Unauthorized
        500: Internal server error
    """
    try:
        # Verify goal ownership
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
                detail="Goal not found"
            )

        if str(goal.user_id) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Create milestone
        service = get_goal_service(db)
        milestone = await service.create_milestone(
            goal_id=goal_id,
            milestone_name=data.milestone_name,
            milestone_target_amount=data.milestone_target_amount,
            milestone_target_date=data.milestone_target_date
        )

        response = MilestoneResponse.model_validate(milestone)

        logger.info(
            f"Milestone created: id={milestone.id}, goal={goal_id}, "
            f"user={current_user_id}"
        )

        return response

    except HTTPException:
        raise
    except ValidationError as e:
        logger.warning(f"Milestone validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create milestone: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create milestone"
        )


# ============================================================================
# ACCOUNT LINKING
# ============================================================================

@router.post("/{goal_id}/link-account", response_model=GoalResponse)
async def link_account(
    goal_id: UUID,
    account_id: str = Query(..., description="Account UUID to link"),
    account_type: str = Query(..., description="Account type (SAVINGS_ACCOUNT, ISA, etc.)"),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Link an account to a goal for automatic progress tracking.

    Links a financial account to a goal so that the account balance
    contributes to goal progress calculations.

    Business Rules:
    - Account must belong to the same user
    - Progress automatically updated after linking
    - Account can be linked to multiple goals
    - User can only link accounts to own goals

    Args:
        goal_id: Goal UUID
        account_id: Account UUID to link
        account_type: Type of account
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        GoalResponse: Updated goal with linked account

    Raises:
        403: Forbidden (goal belongs to another user)
        404: Goal not found
        401: Unauthorized
        500: Internal server error
    """
    try:
        # Verify goal ownership
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
                detail="Goal not found"
            )

        if str(goal.user_id) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Link account
        service = get_goal_service(db)
        updated_goal = await service.link_account_to_goal(
            goal_id=goal_id,
            account_id=account_id,
            account_type=account_type
        )

        # Build response
        goal_dict = {
            **updated_goal.__dict__,
            "days_remaining": updated_goal.days_remaining(),
            "on_track": updated_goal.is_on_track()
        }
        response = GoalResponse.model_validate(goal_dict)

        logger.info(
            f"Account linked: goal={goal_id}, account={account_id}, "
            f"user={current_user_id}"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to link account: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to link account"
        )


# ============================================================================
# GOAL OPTIMIZATION
# ============================================================================

@router.post("/optimize")
async def optimize_goal_allocation(
    available_monthly_savings: Decimal = Query(..., gt=0, description="Available monthly savings to allocate"),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Optimize savings allocation across all goals.

    Analyzes user's active goals and provides optimized allocation of
    available monthly savings based on:
    - Goal priority and urgency
    - Required monthly contributions
    - Intelligent prioritization algorithm

    Business Rules:
    - High-priority goals funded fully first
    - Lower priority goals allocated proportionally if funds remain
    - Returns allocation breakdown and funding status

    Args:
        available_monthly_savings: Total monthly savings to allocate
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        Dict with allocation details:
            - total_available: Decimal
            - total_allocated: Decimal
            - total_required: Decimal
            - unallocated: Decimal
            - allocations: List of allocation per goal
            - fully_funded_goals: List of goal IDs
            - partially_funded_goals: List of goal IDs
            - unfunded_goals: List of goal IDs

    Raises:
        400: Validation error (negative savings)
        401: Unauthorized
        500: Internal server error
    """
    try:
        # Get optimization service
        service = get_goal_optimization_service(db)

        # Allocate savings
        allocation = await service.allocate_available_savings(
            user_id=UUID(current_user_id),
            total_available_monthly_savings=available_monthly_savings
        )

        logger.info(
            f"Goal allocation optimized for user {current_user_id}: "
            f"available={available_monthly_savings}, "
            f"allocated={allocation['total_allocated']}"
        )

        return allocation

    except ValidationError as e:
        logger.warning(f"Optimization validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to optimize allocation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to optimize allocation"
        )
