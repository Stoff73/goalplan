"""
Goal Optimization Service

Provides intelligent goal prioritization and resource allocation including:
- Goal prioritization based on urgency, importance, and feasibility
- Savings allocation across multiple goals
- Conflict detection (insufficient funds, competing deadlines)
- Goal adjustment recommendations

Business Rules:
- Prioritization considers:
  - Urgency (time to target date)
  - Importance (goal type and user priority)
  - Feasibility (achievability with available resources)
- High-priority goals funded first in allocation
- Conflicts detected when total required > available
- Recommendations provided for infeasible goals
- Emergency fund and debt repayment prioritized

Performance:
- Target: <500ms for prioritization and allocation
- Target: <300ms for conflict detection
- Async database operations throughout
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID
from dateutil.relativedelta import relativedelta

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.goal import FinancialGoal, GoalType, GoalPriority, GoalStatus

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when optimization data validation fails."""
    pass


class GoalOptimizationService:
    """Service for goal optimization and intelligent allocation."""

    # Goal type importance scores (base values)
    GOAL_TYPE_IMPORTANCE = {
        GoalType.EMERGENCY_FUND: 100,
        GoalType.DEBT_PAYOFF: 95,
        GoalType.RETIREMENT: 90,
        GoalType.PROPERTY_PURCHASE: 85,
        GoalType.HOUSE_PURCHASE: 85,
        GoalType.EDUCATION: 85,
        GoalType.WEDDING: 70,
        GoalType.VEHICLE_PURCHASE: 60,
        GoalType.HOME_IMPROVEMENT: 55,
        GoalType.HOLIDAY_TRAVEL: 40,
        GoalType.BUSINESS_START: 75,
        GoalType.INHERITANCE_PLANNING: 70,
        GoalType.FINANCIAL_INDEPENDENCE: 90,
        GoalType.CHARITABLE_GIVING: 50,
        GoalType.CUSTOM: 50
    }

    def __init__(self, db: AsyncSession):
        """
        Initialize goal optimization service.

        Args:
            db: Database session for operations
        """
        self.db = db

    async def prioritize_goals(
        self,
        user_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Prioritize user goals intelligently.

        Args:
            user_id: User UUID

        Returns:
            List of prioritized goals with scores:
                - goal_id: UUID
                - goal_name: str
                - goal_type: GoalType
                - priority_score: Decimal
                - urgency_score: Decimal
                - importance_score: Decimal
                - feasibility_score: Decimal
                - rank: int

        Business Logic:
            - Calculate priority score for each active goal
            - Priority score = weighted average:
              - Urgency: 30% (based on time remaining)
              - Importance: 40% (goal type + user priority)
              - Feasibility: 30% (based on progress and timeline)
            - Sort goals by priority score (descending)
            - Assign ranks
        """
        logger.info(f"Prioritizing goals for user {user_id}")

        # Query all active goals
        result = await self.db.execute(
            select(FinancialGoal).where(
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
        goals = result.scalars().all()

        prioritized = []

        for goal in goals:
            # Calculate scores
            urgency_score = self._calculate_urgency_score(goal)
            importance_score = self._calculate_importance_score(goal)
            feasibility_score = self._calculate_feasibility_score(goal)

            # Calculate weighted priority score
            priority_score = (
                urgency_score * Decimal('0.30') +
                importance_score * Decimal('0.40') +
                feasibility_score * Decimal('0.30')
            )

            prioritized.append({
                "goal_id": goal.id,
                "goal_name": goal.goal_name,
                "goal_type": goal.goal_type,
                "target_amount": goal.target_amount,
                "current_amount": goal.current_amount,
                "target_date": goal.target_date,
                "priority_score": priority_score.quantize(Decimal('0.01')),
                "urgency_score": urgency_score.quantize(Decimal('0.01')),
                "importance_score": importance_score.quantize(Decimal('0.01')),
                "feasibility_score": feasibility_score.quantize(Decimal('0.01'))
            })

        # Sort by priority score (descending)
        prioritized.sort(key=lambda x: x["priority_score"], reverse=True)

        # Assign ranks
        for idx, item in enumerate(prioritized, start=1):
            item["rank"] = idx

        logger.info(f"Goals prioritized: {len(prioritized)} goals ranked")

        return prioritized

    async def allocate_available_savings(
        self,
        user_id: UUID,
        total_available_monthly_savings: Decimal
    ) -> Dict[str, Any]:
        """
        Allocate available savings across goals based on priority.

        Args:
            user_id: User UUID
            total_available_monthly_savings: Total monthly savings to allocate

        Returns:
            Dict with allocation details:
                - total_available: Decimal
                - total_allocated: Decimal
                - total_required: Decimal
                - unallocated: Decimal
                - allocations: List[Dict] with goal_id, amount, percentage
                - fully_funded_goals: List[UUID]
                - partially_funded_goals: List[UUID]
                - unfunded_goals: List[UUID]

        Business Logic:
            - Get prioritized goals
            - Calculate required monthly savings for each goal
            - Allocate in priority order:
              - High-priority goals funded fully first
              - If insufficient funds, allocate proportionally to lower priority
            - Return allocation breakdown
        """
        logger.info(
            f"Allocating {total_available_monthly_savings} monthly savings "
            f"for user {user_id}"
        )

        if total_available_monthly_savings < 0:
            raise ValidationError("Available savings cannot be negative")

        # Get prioritized goals
        prioritized = await self.prioritize_goals(user_id)

        # Calculate required monthly savings for each goal
        from services.goals.goal_service import get_goal_service
        goal_service = get_goal_service(self.db)

        allocations = []
        remaining_budget = total_available_monthly_savings
        total_required = Decimal('0.00')
        fully_funded = []
        partially_funded = []
        unfunded = []

        for goal_data in prioritized:
            goal_id = goal_data["goal_id"]

            # Calculate required monthly savings
            calc = await goal_service.calculate_monthly_savings_needed(goal_id)
            required = calc["monthly_savings_needed"]
            total_required += required

            if remaining_budget >= required:
                # Fully fund this goal
                allocated = required
                fully_funded.append(goal_id)
                remaining_budget -= required
            elif remaining_budget > 0:
                # Partially fund this goal
                allocated = remaining_budget
                partially_funded.append(goal_id)
                remaining_budget = Decimal('0.00')
            else:
                # Cannot fund this goal
                allocated = Decimal('0.00')
                unfunded.append(goal_id)

            if total_available_monthly_savings > 0:
                percentage = (allocated / total_available_monthly_savings) * Decimal('100')
            else:
                percentage = Decimal('0.00')

            allocations.append({
                "goal_id": str(goal_id),
                "goal_name": goal_data["goal_name"],
                "required_monthly": required.quantize(Decimal('0.01')),
                "allocated_monthly": allocated.quantize(Decimal('0.01')),
                "allocation_percentage": percentage.quantize(Decimal('0.01')),
                "funding_status": (
                    "FULLY_FUNDED" if goal_id in fully_funded
                    else "PARTIALLY_FUNDED" if goal_id in partially_funded
                    else "UNFUNDED"
                )
            })

        total_allocated = total_available_monthly_savings - remaining_budget

        result = {
            "total_available": total_available_monthly_savings.quantize(Decimal('0.01')),
            "total_allocated": total_allocated.quantize(Decimal('0.01')),
            "total_required": total_required.quantize(Decimal('0.01')),
            "unallocated": remaining_budget.quantize(Decimal('0.01')),
            "allocations": allocations,
            "fully_funded_goals": [str(g) for g in fully_funded],
            "partially_funded_goals": [str(g) for g in partially_funded],
            "unfunded_goals": [str(g) for g in unfunded]
        }

        logger.info(
            f"Savings allocated: {len(fully_funded)} fully funded, "
            f"{len(partially_funded)} partially funded, "
            f"{len(unfunded)} unfunded"
        )

        return result

    async def identify_conflicting_goals(
        self,
        user_id: UUID,
        total_available_monthly_savings: Decimal
    ) -> List[Dict[str, Any]]:
        """
        Identify conflicting goals (insufficient funds, competing deadlines).

        Args:
            user_id: User UUID
            total_available_monthly_savings: Available monthly savings

        Returns:
            List of conflicts:
                - conflict_type: str (INSUFFICIENT_INCOME, COMPETING_DEADLINES, etc.)
                - severity: str (HIGH, MEDIUM, LOW)
                - description: str
                - affected_goals: List[UUID]
                - shortfall: Optional[Decimal]
                - resolution_options: List[Dict]

        Business Logic:
            - Conflict 1: Total required > available (INSUFFICIENT_INCOME)
            - Conflict 2: Multiple goals with near-term deadlines (COMPETING_DEADLINES)
            - Conflict 3: Retirement underfunded while pursuing other goals
            - Return conflicts with resolution suggestions
        """
        logger.info(f"Identifying goal conflicts for user {user_id}")

        conflicts = []

        # Get prioritized goals
        prioritized = await self.prioritize_goals(user_id)

        if not prioritized:
            return conflicts

        # Calculate total required monthly savings
        from services.goals.goal_service import get_goal_service
        goal_service = get_goal_service(self.db)

        total_required = Decimal('0.00')
        goal_requirements = []

        for goal_data in prioritized:
            calc = await goal_service.calculate_monthly_savings_needed(goal_data["goal_id"])
            required = calc["monthly_savings_needed"]
            total_required += required

            goal_requirements.append({
                "goal_id": goal_data["goal_id"],
                "goal_name": goal_data["goal_name"],
                "goal_type": goal_data["goal_type"],
                "required_monthly": required,
                "target_date": goal_data["target_date"]
            })

        # CONFLICT 1: Insufficient income
        if total_required > total_available_monthly_savings:
            shortfall = total_required - total_available_monthly_savings

            conflicts.append({
                "conflict_type": "INSUFFICIENT_INCOME",
                "severity": "HIGH",
                "description": (
                    f"Total required monthly contributions ({total_required:.2f}) "
                    f"exceed available savings ({total_available_monthly_savings:.2f}). "
                    f"Shortfall: {shortfall:.2f} per month."
                ),
                "affected_goals": [g["goal_id"] for g in goal_requirements],
                "shortfall": shortfall.quantize(Decimal('0.01')),
                "resolution_options": [
                    {
                        "option": "PRIORITIZE_GOALS",
                        "description": "Focus on highest priority goals only",
                        "action": "Review prioritized list and pause lower priority goals"
                    },
                    {
                        "option": "EXTEND_TIMELINES",
                        "description": "Extend target dates for lower priority goals",
                        "action": f"Extending timelines would reduce monthly requirement by {(shortfall * Decimal('0.5')).quantize(Decimal('0.01'))}"
                    },
                    {
                        "option": "INCREASE_INCOME",
                        "description": f"Increase monthly income by {shortfall:.2f}",
                        "action": "Seek additional income sources or salary increase"
                    },
                    {
                        "option": "REDUCE_TARGET_AMOUNTS",
                        "description": "Lower target amounts for some goals",
                        "action": "Adjust expectations to match available resources"
                    }
                ]
            })

        # CONFLICT 2: Competing near-term deadlines
        near_term_goals = [
            g for g in goal_requirements
            if (g["target_date"] - date.today()).days < 365
        ]

        if len(near_term_goals) > 2:
            conflicts.append({
                "conflict_type": "COMPETING_DEADLINES",
                "severity": "MEDIUM",
                "description": (
                    f"{len(near_term_goals)} goals have deadlines within 12 months. "
                    f"This may create cashflow pressure."
                ),
                "affected_goals": [g["goal_id"] for g in near_term_goals],
                "shortfall": None,
                "resolution_options": [
                    {
                        "option": "STAGGER_GOALS",
                        "description": "Extend deadlines to spread out timing",
                        "action": "Move some goal deadlines to future years"
                    },
                    {
                        "option": "PRIORITIZE_MOST_URGENT",
                        "description": "Focus on most urgent goal, pause others",
                        "action": "Concentrate resources on single highest-priority goal"
                    }
                ]
            })

        # CONFLICT 3: Retirement underprioritized
        retirement_goals = [
            g for g in goal_requirements
            if g["goal_type"] == GoalType.RETIREMENT
        ]

        if retirement_goals:
            retirement_goal = retirement_goals[0]
            non_retirement_total = sum(
                g["required_monthly"]
                for g in goal_requirements
                if g["goal_type"] != GoalType.RETIREMENT
            )

            if non_retirement_total > retirement_goal["required_monthly"] * Decimal('2'):
                conflicts.append({
                    "conflict_type": "RETIREMENT_UNDERPRIORITIZED",
                    "severity": "HIGH",
                    "description": (
                        "Retirement goal may be underfunded. "
                        f"Non-retirement goals require {non_retirement_total:.2f}/month "
                        f"vs {retirement_goal['required_monthly']:.2f}/month for retirement."
                    ),
                    "affected_goals": [retirement_goal["goal_id"]],
                    "shortfall": None,
                    "resolution_options": [
                        {
                            "option": "INCREASE_RETIREMENT_PRIORITY",
                            "description": "Reduce other contributions to fund retirement adequately",
                            "action": f"Consider allocating at least {retirement_goal['required_monthly']:.2f}/month to retirement"
                        },
                        {
                            "option": "EXTEND_OTHER_GOALS",
                            "description": "Extend timelines for short-term goals",
                            "action": "Prioritize long-term financial security over short-term wants"
                        }
                    ]
                })

        logger.info(f"Goal conflicts identified: {len(conflicts)} conflicts found")

        return conflicts

    async def suggest_goal_adjustments(
        self,
        goal_id: UUID,
        available_monthly_budget: Decimal
    ) -> List[Dict[str, Any]]:
        """
        Suggest adjustments for goals at risk or infeasible.

        Args:
            goal_id: Goal UUID
            available_monthly_budget: Available monthly budget for this goal

        Returns:
            List of adjustment suggestions:
                - adjustment_type: str
                - description: str
                - impact: str
                - new_value: Any (date, Decimal, etc.)
                - feasibility: str

        Business Logic:
            - If goal at risk: Suggest increasing contributions or extending timeline
            - If insufficient budget: Suggest timeline extension or target reduction
            - Calculate new values that would make goal achievable
            - Return multiple options for user to choose from
        """
        logger.info(f"Generating adjustment suggestions for goal {goal_id}")

        # Get goal
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
            raise ValidationError(f"Goal not found: {goal_id}")

        # Calculate current required monthly savings
        from services.goals.goal_service import get_goal_service
        goal_service = get_goal_service(self.db)

        calc = await goal_service.calculate_monthly_savings_needed(goal_id)
        required_monthly = calc["monthly_savings_needed"]
        months_remaining = calc["months_remaining"]

        suggestions = []

        # SUGGESTION 1: Increase contributions (if goal at risk but budget available)
        if goal.status == GoalStatus.AT_RISK and available_monthly_budget >= required_monthly * Decimal('1.2'):
            increased_contribution = required_monthly * Decimal('1.2')
            suggestions.append({
                "adjustment_type": "INCREASE_CONTRIBUTIONS",
                "description": f"Increase monthly contributions to {increased_contribution:.2f}",
                "impact": "Get back on track and potentially achieve goal earlier",
                "new_value": increased_contribution.quantize(Decimal('0.01')),
                "feasibility": "FEASIBLE"
            })

        # SUGGESTION 2: Extend timeline (if insufficient budget)
        if available_monthly_budget < required_monthly:
            # Calculate new timeline that matches available budget
            shortfall = goal.target_amount - goal.current_amount
            if available_monthly_budget > 0:
                new_months = int(shortfall / available_monthly_budget) + 1
                new_target_date = date.today() + relativedelta(months=new_months)

                suggestions.append({
                    "adjustment_type": "EXTEND_TIMELINE",
                    "description": f"Extend target date to {new_target_date}",
                    "impact": f"Reduce monthly requirement from {required_monthly:.2f} to {available_monthly_budget:.2f}",
                    "new_value": str(new_target_date),
                    "feasibility": "HIGHLY_FEASIBLE"
                })

        # SUGGESTION 3: Reduce target amount (if significantly short)
        if required_monthly > available_monthly_budget * Decimal('1.5'):
            # Calculate affordable target
            affordable_target = goal.current_amount + (available_monthly_budget * Decimal(str(months_remaining)))
            reduction = goal.target_amount - affordable_target

            suggestions.append({
                "adjustment_type": "REDUCE_TARGET",
                "description": f"Reduce target from {goal.target_amount:.2f} to {affordable_target:.2f}",
                "impact": f"Makes goal achievable with current timeline and budget (reduction: {reduction:.2f})",
                "new_value": affordable_target.quantize(Decimal('0.01')),
                "feasibility": "FEASIBLE"
            })

        # SUGGESTION 4: One-time lump sum contribution
        if required_monthly > available_monthly_budget:
            # Calculate lump sum needed to make goal affordable
            lump_sum_needed = (required_monthly - available_monthly_budget) * Decimal(str(months_remaining))

            suggestions.append({
                "adjustment_type": "LUMP_SUM_CONTRIBUTION",
                "description": f"Make one-time contribution of {lump_sum_needed:.2f}",
                "impact": f"Reduce monthly requirement to {available_monthly_budget:.2f}",
                "new_value": lump_sum_needed.quantize(Decimal('0.01')),
                "feasibility": "REQUIRES_WINDFALL"
            })

        # SUGGESTION 5: Pause goal temporarily (if severely infeasible)
        if available_monthly_budget == 0 or required_monthly > available_monthly_budget * Decimal('3'):
            suggestions.append({
                "adjustment_type": "PAUSE_GOAL",
                "description": "Temporarily pause this goal to focus on higher priorities",
                "impact": "Free up budget for more urgent or achievable goals",
                "new_value": None,
                "feasibility": "RECOMMENDED"
            })

        logger.info(f"Adjustment suggestions generated: {len(suggestions)} options")

        return suggestions

    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================

    def _calculate_urgency_score(self, goal: FinancialGoal) -> Decimal:
        """
        Calculate urgency score based on time remaining.

        Returns:
            Decimal score 0-100 (higher = more urgent)
        """
        months_remaining = self._calculate_months_between(date.today(), goal.target_date)

        if months_remaining < 12:
            return Decimal('100')
        elif months_remaining < 24:
            return Decimal('80')
        elif months_remaining < 60:
            return Decimal('60')
        else:
            return Decimal('40')

    def _calculate_importance_score(self, goal: FinancialGoal) -> Decimal:
        """
        Calculate importance score based on goal type and user priority.

        Returns:
            Decimal score 0-120 (base + priority multiplier)
        """
        base_score = Decimal(str(self.GOAL_TYPE_IMPORTANCE.get(goal.goal_type, 50)))

        # Adjust for user-specified priority
        if goal.priority == GoalPriority.HIGH:
            multiplier = Decimal('1.2')
        elif goal.priority == GoalPriority.LOW:
            multiplier = Decimal('0.8')
        else:
            multiplier = Decimal('1.0')

        return base_score * multiplier

    def _calculate_feasibility_score(self, goal: FinancialGoal) -> Decimal:
        """
        Calculate feasibility score based on progress and timeline.

        Returns:
            Decimal score 0-100 (higher = more feasible/on track)
        """
        # Check if on track
        if goal.is_on_track():
            return Decimal('100')

        # Calculate how far behind
        days_total = (goal.target_date - goal.start_date).days
        days_elapsed = (date.today() - goal.start_date).days

        if days_total <= 0:
            return Decimal('0')

        expected_progress = Decimal(str((days_elapsed / days_total) * 100))
        actual_progress = goal.progress_percentage

        # Calculate variance
        variance = actual_progress - expected_progress

        if variance >= Decimal('0'):
            # Ahead of schedule
            return Decimal('100')
        elif variance >= Decimal('-10'):
            # Slightly behind
            return Decimal('80')
        elif variance >= Decimal('-20'):
            # Moderately behind
            return Decimal('60')
        elif variance >= Decimal('-30'):
            # Significantly behind
            return Decimal('40')
        else:
            # Severely behind
            return Decimal('20')

    def _calculate_months_between(self, start: date, end: date) -> int:
        """Calculate number of months between two dates."""
        delta = relativedelta(end, start)
        return delta.years * 12 + delta.months


# Factory function
def get_goal_optimization_service(db: AsyncSession) -> GoalOptimizationService:
    """
    Get goal optimization service instance.

    Args:
        db: Database session

    Returns:
        GoalOptimizationService instance
    """
    return GoalOptimizationService(db)
