"""
Goal Management Service

Provides comprehensive financial goal management including:
- Goal creation with SMART criteria validation
- Progress tracking with linked accounts
- Monthly savings calculations
- Milestone management
- Achievement detection and notifications

Business Rules:
- Goals must be at least 6 months in the future (max 50 years)
- Maximum 10 active goals per user
- Target amounts must be positive
- Progress calculated from linked accounts
- On-track threshold: within 10% of expected progress
- Auto-achievement detection when target met
- Temporal data for progress history

Performance:
- Target: <500ms for goal creation and updates
- Target: <200ms for progress queries
- Async database operations throughout
"""

import logging
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from uuid import UUID
from dateutil.relativedelta import relativedelta

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.goal import (
    FinancialGoal, GoalMilestone, GoalProgressHistory,
    GoalRecommendation, GoalType, GoalPriority, GoalStatus,
    MilestoneStatus, ContributionFrequency
)
from schemas.goal import CreateGoalRequest, UpdateGoalRequest

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when goal data validation fails."""
    pass


class NotFoundError(Exception):
    """Raised when goal entity not found."""
    pass


class GoalLimitError(Exception):
    """Raised when user exceeds maximum active goals."""
    pass


class GoalService:
    """Service for financial goal management."""

    MAX_ACTIVE_GOALS = 10
    MIN_GOAL_MONTHS = 6
    MAX_GOAL_YEARS = 50
    ON_TRACK_THRESHOLD = Decimal('10.00')  # 10% variance allowed

    def __init__(self, db: AsyncSession):
        """
        Initialize goal service.

        Args:
            db: Database session for operations
        """
        self.db = db

    async def create_goal(
        self,
        user_id: UUID,
        goal_data: CreateGoalRequest
    ) -> FinancialGoal:
        """
        Create a new financial goal with SMART criteria validation.

        Args:
            user_id: User UUID
            goal_data: Validated goal creation data

        Returns:
            Created FinancialGoal

        Raises:
            ValidationError: If goal data fails validation
            GoalLimitError: If user has 10+ active goals

        Business Logic:
            - Validate SMART criteria (done in schema)
            - Check active goal count (max 10)
            - Set initial status based on data:
              - NOT_STARTED if no current_amount
              - IN_PROGRESS if current_amount > 0
            - Link to user accounts if specified
            - Create initial progress snapshot
            - Calculate progress percentage
            - Store with audit trail
        """
        logger.info(f"Creating goal for user {user_id}: {goal_data.goal_name}")

        # Check active goal limit
        active_count = await self._count_active_goals(user_id)
        if active_count >= self.MAX_ACTIVE_GOALS:
            raise GoalLimitError(
                f"Maximum {self.MAX_ACTIVE_GOALS} active goals allowed. "
                f"Please complete or abandon an existing goal first."
            )

        # Determine initial status
        initial_status = GoalStatus.NOT_STARTED

        # Create goal
        goal = FinancialGoal(
            id=uuid.uuid4(),
            user_id=user_id,
            goal_name=goal_data.goal_name,
            goal_type=goal_data.goal_type,
            description=goal_data.description,
            target_amount=goal_data.target_amount,
            currency=goal_data.currency,
            current_amount=Decimal('0.00'),
            progress_percentage=Decimal('0.00'),
            target_date=goal_data.target_date,
            start_date=date.today(),
            priority=goal_data.priority,
            status=initial_status,
            linked_accounts=goal_data.linked_accounts,
            auto_contribution=goal_data.auto_contribution,
            contribution_amount=goal_data.contribution_amount,
            contribution_frequency=goal_data.contribution_frequency
        )

        self.db.add(goal)
        await self.db.commit()
        await self.db.refresh(goal)

        # Create initial progress snapshot
        await self._create_progress_snapshot(goal)

        logger.info(
            f"Goal created: id={goal.id}, name={goal.goal_name}, "
            f"target={goal.target_amount} {goal.currency}"
        )

        return goal

    async def update_goal_progress(
        self,
        goal_id: UUID
    ) -> Dict[str, Any]:
        """
        Update goal progress from linked accounts.

        Args:
            goal_id: Goal UUID

        Returns:
            Dict with progress update details:
                - current_amount: Decimal
                - progress_percentage: Decimal
                - on_track: bool
                - status: GoalStatus
                - projected_completion_date: Optional[date]
                - days_remaining: int

        Raises:
            NotFoundError: If goal not found

        Business Logic:
            - Calculate current_amount from linked accounts (placeholder)
            - Calculate progress_percentage = (current / target) * 100
            - Determine on_track based on time elapsed vs progress
            - Update status:
              - ACHIEVED if current_amount >= target_amount
              - ON_TRACK if within 10% of expected progress
              - AT_RISK if >10% behind expected progress
              - IN_PROGRESS otherwise
            - Project completion date based on current rate
            - Store progress snapshot if changed
        """
        logger.info(f"Updating progress for goal {goal_id}")

        goal = await self._get_goal_by_id(goal_id)

        # Calculate current amount from linked accounts
        # For now, keep existing current_amount (actual account linking TBD)
        current_amount = goal.current_amount

        # If linked accounts exist, you would query them here:
        # current_amount = await self._calculate_from_linked_accounts(goal.linked_accounts)

        # Calculate progress percentage
        progress_percentage = goal.calculate_progress_percentage()

        # Check if achieved
        if current_amount >= goal.target_amount:
            goal.status = GoalStatus.ACHIEVED
            goal.achieved_at = datetime.utcnow()
            on_track = True
            projected_completion = date.today()
        else:
            # Calculate expected progress
            days_total = (goal.target_date - goal.start_date).days
            days_elapsed = (date.today() - goal.start_date).days

            if days_total > 0:
                expected_progress_pct = Decimal(str((days_elapsed / days_total) * 100))
            else:
                expected_progress_pct = Decimal('0.00')

            # Calculate variance
            variance = float(progress_percentage) - float(expected_progress_pct)

            # Determine on_track status
            on_track = variance >= -float(self.ON_TRACK_THRESHOLD)

            # Update status
            if on_track:
                goal.status = GoalStatus.ON_TRACK
            else:
                goal.status = GoalStatus.AT_RISK

            # Project completion date
            if days_elapsed > 0 and current_amount > 0:
                # Linear projection: days_per_unit * units_remaining
                rate = float(current_amount) / days_elapsed  # Amount per day
                remaining = float(goal.target_amount - current_amount)

                if rate > 0:
                    days_to_complete = int(remaining / rate)
                    projected_completion = date.today() + relativedelta(days=days_to_complete)
                else:
                    projected_completion = None
            else:
                projected_completion = None

            if goal.status == GoalStatus.NOT_STARTED and current_amount > 0:
                goal.status = GoalStatus.IN_PROGRESS

        # Update goal
        goal.current_amount = current_amount
        goal.progress_percentage = progress_percentage

        await self.db.commit()
        await self.db.refresh(goal)

        # Create progress snapshot
        await self._create_progress_snapshot(goal, on_track, projected_completion)

        # Check milestones
        await self._check_milestones(goal)

        result = {
            "current_amount": current_amount,
            "progress_percentage": progress_percentage,
            "on_track": on_track,
            "status": goal.status,
            "projected_completion_date": projected_completion,
            "days_remaining": goal.days_remaining()
        }

        logger.info(
            f"Goal progress updated: id={goal_id}, "
            f"progress={progress_percentage:.2f}%, on_track={on_track}"
        )

        return result

    async def calculate_monthly_savings_needed(
        self,
        goal_id: UUID,
        expected_annual_return: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Calculate required monthly savings to achieve goal.

        Args:
            goal_id: Goal UUID
            expected_annual_return: Expected annual return rate (default: 0.02 = 2%)

        Returns:
            Dict with calculation results:
                - monthly_savings_needed: Decimal
                - months_remaining: int
                - shortfall: Decimal
                - total_contributions_needed: Decimal
                - expected_return_rate: Decimal

        Raises:
            NotFoundError: If goal not found

        Business Logic:
            - Shortfall = target_amount - current_amount
            - Months_remaining = months between today and target_date
            - If expected_return == 0:
              monthly = shortfall / months_remaining
            - Else:
              Use future value of annuity formula:
              FV = PMT × [((1 + r)^n - 1) / r]
              PMT = FV / [((1 + r)^n - 1) / r]
              where r = monthly_rate, n = months

        Formula:
            FV = target_amount - FV(current_amount)
            PMT = FV × r / ((1 + r)^n - 1)
        """
        logger.info(f"Calculating monthly savings for goal {goal_id}")

        goal = await self._get_goal_by_id(goal_id)

        # Default return rate: 2% annual (conservative)
        if expected_annual_return is None:
            expected_annual_return = Decimal('0.02')

        # Calculate shortfall and time
        shortfall = goal.target_amount - goal.current_amount
        months_remaining = self._calculate_months_between(date.today(), goal.target_date)

        if months_remaining <= 0:
            raise ValidationError("Goal target date is in the past")

        # Calculate monthly rate
        monthly_rate = expected_annual_return / Decimal('12')

        # Future value of current savings
        if monthly_rate > 0:
            fv_current = goal.current_amount * ((Decimal('1') + monthly_rate) ** months_remaining)
        else:
            fv_current = goal.current_amount

        # Required additional savings
        additional_needed = goal.target_amount - fv_current

        if additional_needed <= 0:
            monthly_savings_needed = Decimal('0.00')
            total_contributions_needed = Decimal('0.00')
        else:
            # Calculate monthly payment using future value of annuity formula
            if monthly_rate == 0:
                monthly_savings_needed = additional_needed / Decimal(str(months_remaining))
            else:
                numerator = additional_needed * monthly_rate
                denominator = ((Decimal('1') + monthly_rate) ** months_remaining) - Decimal('1')
                monthly_savings_needed = numerator / denominator

            total_contributions_needed = monthly_savings_needed * Decimal(str(months_remaining))

        result = {
            "monthly_savings_needed": monthly_savings_needed.quantize(Decimal('0.01')),
            "months_remaining": months_remaining,
            "shortfall": shortfall,
            "total_contributions_needed": total_contributions_needed.quantize(Decimal('0.01')),
            "expected_return_rate": expected_annual_return
        }

        logger.info(
            f"Monthly savings calculated: goal={goal_id}, "
            f"monthly={monthly_savings_needed:.2f}, months={months_remaining}"
        )

        return result

    async def link_account_to_goal(
        self,
        goal_id: UUID,
        account_id: str,
        account_type: str
    ) -> FinancialGoal:
        """
        Link account to goal for automatic progress tracking.

        Args:
            goal_id: Goal UUID
            account_id: Account UUID to link
            account_type: Type of account (SAVINGS_ACCOUNT, ISA, etc.)

        Returns:
            Updated FinancialGoal

        Raises:
            NotFoundError: If goal not found

        Business Logic:
            - Add account_id to goal.linked_accounts array
            - Update progress from linked accounts
            - Store account_type for reference (JSON metadata)
        """
        logger.info(f"Linking account {account_id} to goal {goal_id}")

        goal = await self._get_goal_by_id(goal_id)

        # Initialize linked_accounts if None
        if goal.linked_accounts is None:
            goal.linked_accounts = []

        # Add account if not already linked
        if account_id not in goal.linked_accounts:
            goal.linked_accounts.append(account_id)

        await self.db.commit()
        await self.db.refresh(goal)

        # Update progress from linked accounts
        await self.update_goal_progress(goal_id)

        # Refresh goal again to get latest state after progress update
        await self.db.refresh(goal)

        logger.info(f"Account linked: goal={goal_id}, account={account_id}")

        return goal

    async def create_milestone(
        self,
        goal_id: UUID,
        milestone_name: str,
        milestone_target_amount: Decimal,
        milestone_target_date: date
    ) -> GoalMilestone:
        """
        Create milestone for goal.

        Args:
            goal_id: Goal UUID
            milestone_name: Descriptive name
            milestone_target_amount: Target amount for milestone
            milestone_target_date: Target date for milestone

        Returns:
            Created GoalMilestone

        Raises:
            NotFoundError: If goal not found
            ValidationError: If milestone data invalid

        Business Logic:
            - Validate milestone_target_date is between goal start and target dates
            - Validate milestone_target_amount <= goal.target_amount
            - Create milestone with PENDING status
            - Check if already achieved based on current progress
        """
        logger.info(f"Creating milestone for goal {goal_id}: {milestone_name}")

        goal = await self._get_goal_by_id(goal_id)

        # Validate milestone date
        if milestone_target_date < goal.start_date:
            raise ValidationError("Milestone date cannot be before goal start date")
        if milestone_target_date > goal.target_date:
            raise ValidationError("Milestone date cannot be after goal target date")

        # Validate milestone amount
        if milestone_target_amount > goal.target_amount:
            raise ValidationError("Milestone amount cannot exceed goal target amount")
        if milestone_target_amount <= 0:
            raise ValidationError("Milestone amount must be positive")

        # Create milestone
        milestone = GoalMilestone(
            id=uuid.uuid4(),
            goal_id=goal_id,
            milestone_name=milestone_name,
            milestone_target_amount=milestone_target_amount,
            milestone_target_date=milestone_target_date,
            status=MilestoneStatus.PENDING
        )

        # Check if already achieved
        if goal.current_amount >= milestone_target_amount:
            milestone.status = MilestoneStatus.ACHIEVED
            milestone.achieved_date = date.today()

        self.db.add(milestone)
        await self.db.commit()
        await self.db.refresh(milestone)

        logger.info(f"Milestone created: id={milestone.id}, status={milestone.status}")

        return milestone

    async def check_goal_achievements(
        self,
        user_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Check all user goals for achievements.

        Args:
            user_id: User UUID

        Returns:
            List of achieved goals with details:
                - goal_id: UUID
                - goal_name: str
                - target_amount: Decimal
                - achieved_date: date
                - newly_achieved: bool (achieved in this check)

        Business Logic:
            - Query all active goals for user
            - Check if current_amount >= target_amount
            - Mark goal as ACHIEVED if met
            - Set achieved_at timestamp
            - Return list of achievements
            - Trigger celebration notifications (placeholder)
        """
        logger.info(f"Checking goal achievements for user {user_id}")

        # Query all non-achieved goals
        result = await self.db.execute(
            select(FinancialGoal).where(
                and_(
                    FinancialGoal.user_id == user_id,
                    FinancialGoal.status != GoalStatus.ACHIEVED,
                    FinancialGoal.status != GoalStatus.ABANDONED,
                    FinancialGoal.deleted_at.is_(None)
                )
            )
        )
        goals = result.scalars().all()

        achievements = []

        for goal in goals:
            if goal.current_amount >= goal.target_amount:
                # Mark as achieved
                newly_achieved = goal.status != GoalStatus.ACHIEVED

                goal.status = GoalStatus.ACHIEVED
                goal.achieved_at = datetime.utcnow()
                goal.progress_percentage = Decimal('100.00')

                achievements.append({
                    "goal_id": goal.id,
                    "goal_name": goal.goal_name,
                    "target_amount": goal.target_amount,
                    "achieved_date": date.today(),
                    "newly_achieved": newly_achieved
                })

                # Trigger celebration notification (placeholder)
                logger.info(
                    f"ACHIEVEMENT: Goal '{goal.goal_name}' achieved! "
                    f"Target: {goal.target_amount} {goal.currency}"
                )

        if goals:
            await self.db.commit()

        logger.info(f"Goal achievements checked: {len(achievements)} achievements found")

        return achievements

    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================

    async def _get_goal_by_id(self, goal_id: UUID) -> FinancialGoal:
        """Get goal by ID, raise NotFoundError if not found."""
        result = await self.db.execute(
            select(FinancialGoal).where(
                and_(
                    FinancialGoal.id == goal_id,
                    FinancialGoal.deleted_at.is_(None)
                )
            )
        )
        goal = result.scalar_one_or_none()

        if not goal:
            raise NotFoundError(f"Goal not found: {goal_id}")

        return goal

    async def _count_active_goals(self, user_id: UUID) -> int:
        """Count active goals for user."""
        result = await self.db.execute(
            select(func.count(FinancialGoal.id)).where(
                and_(
                    FinancialGoal.user_id == user_id,
                    FinancialGoal.status.in_([
                        GoalStatus.NOT_STARTED,
                        GoalStatus.IN_PROGRESS,
                        GoalStatus.ON_TRACK,
                        GoalStatus.AT_RISK
                    ]),
                    FinancialGoal.deleted_at.is_(None)
                )
            )
        )
        return result.scalar() or 0

    async def _create_progress_snapshot(
        self,
        goal: FinancialGoal,
        on_track: Optional[bool] = None,
        projected_completion: Optional[date] = None
    ) -> GoalProgressHistory:
        """Create progress history snapshot."""
        if on_track is None:
            on_track = goal.is_on_track()

        snapshot = GoalProgressHistory(
            id=uuid.uuid4(),
            goal_id=goal.id,
            snapshot_date=date.today(),
            amount_at_snapshot=goal.current_amount,
            target_amount_at_snapshot=goal.target_amount,
            progress_percentage=goal.progress_percentage,
            on_track=on_track,
            projected_completion_date=projected_completion,
            effective_from=date.today(),
            effective_to=None
        )

        self.db.add(snapshot)
        await self.db.commit()

        return snapshot

    async def _check_milestones(self, goal: FinancialGoal) -> None:
        """Check and update milestone achievements."""
        result = await self.db.execute(
            select(GoalMilestone).where(
                and_(
                    GoalMilestone.goal_id == goal.id,
                    GoalMilestone.status == MilestoneStatus.PENDING
                )
            )
        )
        milestones = result.scalars().all()

        for milestone in milestones:
            if goal.current_amount >= milestone.milestone_target_amount:
                milestone.status = MilestoneStatus.ACHIEVED
                milestone.achieved_date = date.today()

                logger.info(
                    f"MILESTONE ACHIEVED: '{milestone.milestone_name}' "
                    f"for goal '{goal.goal_name}'"
                )

        if milestones:
            await self.db.commit()

    def _calculate_months_between(self, start: date, end: date) -> int:
        """Calculate number of months between two dates."""
        delta = relativedelta(end, start)
        return delta.years * 12 + delta.months


# Factory function
def get_goal_service(db: AsyncSession) -> GoalService:
    """
    Get goal service instance.

    Args:
        db: Database session

    Returns:
        GoalService instance
    """
    return GoalService(db)
