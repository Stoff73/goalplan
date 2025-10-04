"""
Tests for Goal Optimization Service

Tests cover:
- Goal prioritization (urgency, importance, feasibility)
- Savings allocation across multiple goals
- Conflict detection (insufficient income, competing deadlines)
- Goal adjustment suggestions
- Edge cases (no goals, single goal, extreme scenarios)
"""

import pytest
from datetime import date
from decimal import Decimal
from uuid import uuid4
from dateutil.relativedelta import relativedelta

from sqlalchemy.ext.asyncio import AsyncSession

from models.goal import (
    FinancialGoal, GoalType, GoalPriority, GoalStatus
)
from services.goals.goal_optimization_service import (
    GoalOptimizationService, ValidationError
)


@pytest.fixture
async def optimization_service(db_session: AsyncSession):
    """Create goal optimization service instance."""
    return GoalOptimizationService(db_session)


@pytest.fixture
async def test_user_id():
    """Generate test user ID."""
    return uuid4()


@pytest.fixture
async def multiple_goals(db_session: AsyncSession, test_user_id):
    """Create multiple goals with different priorities and timelines."""
    goals = [
        # High urgency, high importance (Emergency fund)
        FinancialGoal(
            id=uuid4(),
            user_id=test_user_id,
            goal_name="Emergency Fund",
            goal_type=GoalType.EMERGENCY_FUND,
            target_amount=Decimal('15000.00'),
            currency='GBP',
            current_amount=Decimal('5000.00'),
            target_date=date.today() + relativedelta(months=6),  # Urgent
            start_date=date.today() - relativedelta(months=3),
            priority=GoalPriority.HIGH,
            status=GoalStatus.IN_PROGRESS
        ),
        # Medium urgency, high importance (Retirement)
        FinancialGoal(
            id=uuid4(),
            user_id=test_user_id,
            goal_name="Retirement Fund",
            goal_type=GoalType.RETIREMENT,
            target_amount=Decimal('500000.00'),
            currency='GBP',
            current_amount=Decimal('50000.00'),
            target_date=date.today() + relativedelta(years=20),  # Long-term
            start_date=date.today() - relativedelta(years=5),
            priority=GoalPriority.HIGH,
            status=GoalStatus.IN_PROGRESS
        ),
        # High urgency, medium importance (Holiday)
        FinancialGoal(
            id=uuid4(),
            user_id=test_user_id,
            goal_name="Holiday to Spain",
            goal_type=GoalType.HOLIDAY_TRAVEL,
            target_amount=Decimal('3000.00'),
            currency='GBP',
            current_amount=Decimal('500.00'),
            target_date=date.today() + relativedelta(months=8),  # Soon
            start_date=date.today() - relativedelta(months=2),
            priority=GoalPriority.MEDIUM,
            status=GoalStatus.IN_PROGRESS
        ),
        # Low urgency, medium importance (Home improvement)
        FinancialGoal(
            id=uuid4(),
            user_id=test_user_id,
            goal_name="Kitchen Renovation",
            goal_type=GoalType.HOME_IMPROVEMENT,
            target_amount=Decimal('25000.00'),
            currency='GBP',
            current_amount=Decimal('2000.00'),
            target_date=date.today() + relativedelta(years=3),  # Long-term
            start_date=date.today() - relativedelta(months=6),
            priority=GoalPriority.LOW,
            status=GoalStatus.IN_PROGRESS
        )
    ]

    for goal in goals:
        db_session.add(goal)

    await db_session.commit()

    # Refresh all
    for goal in goals:
        await db_session.refresh(goal)

    return goals


# ============================================================================
# PRIORITIZATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_prioritize_goals(
    optimization_service: GoalOptimizationService,
    multiple_goals
):
    """Test goal prioritization."""
    user_id = multiple_goals[0].user_id
    prioritized = await optimization_service.prioritize_goals(user_id)

    assert len(prioritized) == 4

    # Check that all have required fields
    for item in prioritized:
        assert "goal_id" in item
        assert "goal_name" in item
        assert "priority_score" in item
        assert "urgency_score" in item
        assert "importance_score" in item
        assert "feasibility_score" in item
        assert "rank" in item

    # Check ranks are sequential
    ranks = [item["rank"] for item in prioritized]
    assert ranks == [1, 2, 3, 4]

    # Check priority scores are descending
    scores = [item["priority_score"] for item in prioritized]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_prioritize_emergency_fund_highest(
    optimization_service: GoalOptimizationService,
    multiple_goals
):
    """Test that emergency fund gets high priority."""
    user_id = multiple_goals[0].user_id
    prioritized = await optimization_service.prioritize_goals(user_id)

    # Emergency fund should be high priority (near top)
    emergency_fund = next(
        item for item in prioritized
        if "Emergency Fund" in item["goal_name"]
    )

    # Should have high importance score
    assert emergency_fund["importance_score"] >= Decimal('90')


@pytest.mark.asyncio
async def test_prioritize_urgent_goals_higher(
    optimization_service: GoalOptimizationService,
    multiple_goals
):
    """Test that urgent goals get higher urgency scores."""
    user_id = multiple_goals[0].user_id
    prioritized = await optimization_service.prioritize_goals(user_id)

    # Emergency fund (6 months) should have higher urgency than retirement (20 years)
    emergency = next(
        item for item in prioritized
        if "Emergency Fund" in item["goal_name"]
    )
    retirement = next(
        item for item in prioritized
        if "Retirement Fund" in item["goal_name"]
    )

    assert emergency["urgency_score"] > retirement["urgency_score"]


@pytest.mark.asyncio
async def test_prioritize_no_goals(
    optimization_service: GoalOptimizationService,
    test_user_id
):
    """Test prioritization with no goals."""
    prioritized = await optimization_service.prioritize_goals(test_user_id)

    assert len(prioritized) == 0


@pytest.mark.asyncio
async def test_prioritize_user_priority_affects_score(
    optimization_service: GoalOptimizationService,
    db_session: AsyncSession,
    test_user_id
):
    """Test that user-set priority affects importance score."""
    # Create two identical goals with different priorities
    goal_high = FinancialGoal(
        id=uuid4(),
        user_id=test_user_id,
        goal_name="High Priority Goal",
        goal_type=GoalType.CUSTOM,
        target_amount=Decimal('10000.00'),
        currency='GBP',
        current_amount=Decimal('1000.00'),
        target_date=date.today() + relativedelta(years=2),
        start_date=date.today(),
        priority=GoalPriority.HIGH,
        status=GoalStatus.IN_PROGRESS
    )

    goal_low = FinancialGoal(
        id=uuid4(),
        user_id=test_user_id,
        goal_name="Low Priority Goal",
        goal_type=GoalType.CUSTOM,
        target_amount=Decimal('10000.00'),
        currency='GBP',
        current_amount=Decimal('1000.00'),
        target_date=date.today() + relativedelta(years=2),
        start_date=date.today(),
        priority=GoalPriority.LOW,
        status=GoalStatus.IN_PROGRESS
    )

    db_session.add(goal_high)
    db_session.add(goal_low)
    await db_session.commit()

    prioritized = await optimization_service.prioritize_goals(test_user_id)

    high = next(item for item in prioritized if "High Priority" in item["goal_name"])
    low = next(item for item in prioritized if "Low Priority" in item["goal_name"])

    assert high["importance_score"] > low["importance_score"]
    assert high["priority_score"] > low["priority_score"]


# ============================================================================
# ALLOCATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_allocate_available_savings(
    optimization_service: GoalOptimizationService,
    multiple_goals
):
    """Test savings allocation across goals."""
    user_id = multiple_goals[0].user_id
    available = Decimal('2000.00')  # £2000/month available

    allocation = await optimization_service.allocate_available_savings(
        user_id,
        available
    )

    assert "total_available" in allocation
    assert "total_allocated" in allocation
    assert "total_required" in allocation
    assert "allocations" in allocation
    assert "fully_funded_goals" in allocation
    assert "partially_funded_goals" in allocation
    assert "unfunded_goals" in allocation

    assert allocation["total_available"] == available
    assert allocation["total_allocated"] <= available


@pytest.mark.asyncio
async def test_allocate_fully_funds_high_priority_first(
    optimization_service: GoalOptimizationService,
    db_session: AsyncSession,
    test_user_id
):
    """Test that high-priority goals are fully funded first."""
    # Create 2 goals: one small high-priority, one large low-priority
    goal1 = FinancialGoal(
        id=uuid4(),
        user_id=test_user_id,
        goal_name="Small High Priority",
        goal_type=GoalType.EMERGENCY_FUND,
        target_amount=Decimal('6000.00'),
        currency='GBP',
        current_amount=Decimal('0.00'),
        target_date=date.today() + relativedelta(months=6),
        start_date=date.today(),
        priority=GoalPriority.HIGH,
        status=GoalStatus.NOT_STARTED
    )

    goal2 = FinancialGoal(
        id=uuid4(),
        user_id=test_user_id,
        goal_name="Large Low Priority",
        goal_type=GoalType.HOLIDAY_TRAVEL,
        target_amount=Decimal('12000.00'),
        currency='GBP',
        current_amount=Decimal('0.00'),
        target_date=date.today() + relativedelta(months=12),
        start_date=date.today(),
        priority=GoalPriority.LOW,
        status=GoalStatus.NOT_STARTED
    )

    db_session.add(goal1)
    db_session.add(goal2)
    await db_session.commit()

    # Allocate with sufficient budget for goal1 but not both
    allocation = await optimization_service.allocate_available_savings(
        test_user_id,
        Decimal('1500.00')  # Should cover goal1 (~1000) but not goal2 (~1000)
    )

    # Goal1 should be fully or mostly funded
    goal1_alloc = next(
        a for a in allocation["allocations"]
        if "Small High Priority" in a["goal_name"]
    )

    assert goal1_alloc["funding_status"] in ["FULLY_FUNDED", "PARTIALLY_FUNDED"]


@pytest.mark.asyncio
async def test_allocate_insufficient_budget(
    optimization_service: GoalOptimizationService,
    multiple_goals
):
    """Test allocation when budget is insufficient for all goals."""
    user_id = multiple_goals[0].user_id

    allocation = await optimization_service.allocate_available_savings(
        user_id,
        Decimal('100.00')  # Very small budget
    )

    # Should have unfunded goals
    assert len(allocation["unfunded_goals"]) > 0

    # Total allocated should equal available (fully used)
    assert allocation["total_allocated"] == Decimal('100.00')


@pytest.mark.asyncio
async def test_allocate_excess_budget(
    optimization_service: GoalOptimizationService,
    multiple_goals
):
    """Test allocation when budget exceeds requirements."""
    user_id = multiple_goals[0].user_id

    allocation = await optimization_service.allocate_available_savings(
        user_id,
        Decimal('50000.00')  # Huge budget
    )

    # Should have unallocated funds
    assert allocation["unallocated"] > Decimal('0')

    # All goals should be fully funded
    assert len(allocation["unfunded_goals"]) == 0


@pytest.mark.asyncio
async def test_allocate_negative_budget_raises_error(
    optimization_service: GoalOptimizationService,
    test_user_id
):
    """Test that negative budget raises ValidationError."""
    with pytest.raises(ValidationError):
        await optimization_service.allocate_available_savings(
            test_user_id,
            Decimal('-100.00')
        )


@pytest.mark.asyncio
async def test_allocate_zero_budget(
    optimization_service: GoalOptimizationService,
    multiple_goals
):
    """Test allocation with zero budget."""
    user_id = multiple_goals[0].user_id

    allocation = await optimization_service.allocate_available_savings(
        user_id,
        Decimal('0.00')
    )

    # All goals should be unfunded
    assert len(allocation["unfunded_goals"]) == len(multiple_goals)
    assert allocation["total_allocated"] == Decimal('0.00')


# ============================================================================
# CONFLICT DETECTION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_identify_insufficient_income_conflict(
    optimization_service: GoalOptimizationService,
    multiple_goals
):
    """Test detection of insufficient income conflict."""
    user_id = multiple_goals[0].user_id

    # Set very low available savings
    conflicts = await optimization_service.identify_conflicting_goals(
        user_id,
        Decimal('100.00')  # Too low for all goals
    )

    # Should detect insufficient income conflict
    insufficient_income = next(
        (c for c in conflicts if c["conflict_type"] == "INSUFFICIENT_INCOME"),
        None
    )

    assert insufficient_income is not None
    assert insufficient_income["severity"] == "HIGH"
    assert "shortfall" in insufficient_income
    assert insufficient_income["shortfall"] > Decimal('0')
    assert len(insufficient_income["resolution_options"]) > 0


@pytest.mark.asyncio
async def test_identify_competing_deadlines_conflict(
    optimization_service: GoalOptimizationService,
    db_session: AsyncSession,
    test_user_id
):
    """Test detection of competing near-term deadlines."""
    # Create 3 goals with deadlines within 12 months
    goals = []
    for i in range(3):
        goal = FinancialGoal(
            id=uuid4(),
            user_id=test_user_id,
            goal_name=f"Near Term Goal {i}",
            goal_type=GoalType.CUSTOM,
            target_amount=Decimal('5000.00'),
            currency='GBP',
            current_amount=Decimal('0.00'),
            target_date=date.today() + relativedelta(months=6 + i),
            start_date=date.today(),
            priority=GoalPriority.MEDIUM,
            status=GoalStatus.NOT_STARTED
        )
        goals.append(goal)
        db_session.add(goal)

    await db_session.commit()

    conflicts = await optimization_service.identify_conflicting_goals(
        test_user_id,
        Decimal('1000.00')
    )

    # Should detect competing deadlines
    competing = next(
        (c for c in conflicts if c["conflict_type"] == "COMPETING_DEADLINES"),
        None
    )

    assert competing is not None
    assert competing["severity"] == "MEDIUM"
    assert len(competing["affected_goals"]) >= 3


@pytest.mark.asyncio
async def test_identify_retirement_underprioritized_conflict(
    optimization_service: GoalOptimizationService,
    db_session: AsyncSession,
    test_user_id
):
    """Test detection of underprioritized retirement."""
    # Create retirement goal requiring £1000/month
    retirement = FinancialGoal(
        id=uuid4(),
        user_id=test_user_id,
        goal_name="Retirement",
        goal_type=GoalType.RETIREMENT,
        target_amount=Decimal('500000.00'),
        currency='GBP',
        current_amount=Decimal('0.00'),
        target_date=date.today() + relativedelta(years=25),
        start_date=date.today(),
        priority=GoalPriority.HIGH,
        status=GoalStatus.NOT_STARTED
    )

    # Create multiple short-term goals requiring more total
    for i in range(3):
        goal = FinancialGoal(
            id=uuid4(),
            user_id=test_user_id,
            goal_name=f"Short Term {i}",
            goal_type=GoalType.HOLIDAY_TRAVEL,
            target_amount=Decimal('12000.00'),
            currency='GBP',
            current_amount=Decimal('0.00'),
            target_date=date.today() + relativedelta(months=12),
            start_date=date.today(),
            priority=GoalPriority.MEDIUM,
            status=GoalStatus.NOT_STARTED
        )
        db_session.add(goal)

    db_session.add(retirement)
    await db_session.commit()

    conflicts = await optimization_service.identify_conflicting_goals(
        test_user_id,
        Decimal('2000.00')
    )

    # Should detect retirement underprioritized
    retirement_conflict = next(
        (c for c in conflicts if c["conflict_type"] == "RETIREMENT_UNDERPRIORITIZED"),
        None
    )

    assert retirement_conflict is not None
    assert retirement_conflict["severity"] == "HIGH"


@pytest.mark.asyncio
async def test_identify_no_conflicts(
    optimization_service: GoalOptimizationService,
    db_session: AsyncSession,
    test_user_id
):
    """Test conflict detection with no conflicts."""
    # Create single modest goal
    goal = FinancialGoal(
        id=uuid4(),
        user_id=test_user_id,
        goal_name="Small Goal",
        goal_type=GoalType.CUSTOM,
        target_amount=Decimal('6000.00'),
        currency='GBP',
        current_amount=Decimal('0.00'),
        target_date=date.today() + relativedelta(years=2),
        start_date=date.today(),
        priority=GoalPriority.MEDIUM,
        status=GoalStatus.NOT_STARTED
    )
    db_session.add(goal)
    await db_session.commit()

    conflicts = await optimization_service.identify_conflicting_goals(
        test_user_id,
        Decimal('5000.00')  # Plenty of budget
    )

    assert len(conflicts) == 0


# ============================================================================
# ADJUSTMENT SUGGESTION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_suggest_adjustments_extend_timeline(
    optimization_service: GoalOptimizationService,
    db_session: AsyncSession,
    test_user_id
):
    """Test adjustment suggestion to extend timeline."""
    # Create goal with insufficient budget
    goal = FinancialGoal(
        id=uuid4(),
        user_id=test_user_id,
        goal_name="Ambitious Goal",
        goal_type=GoalType.CUSTOM,
        target_amount=Decimal('24000.00'),
        currency='GBP',
        current_amount=Decimal('0.00'),
        target_date=date.today() + relativedelta(months=12),
        start_date=date.today(),
        priority=GoalPriority.MEDIUM,
        status=GoalStatus.NOT_STARTED
    )
    db_session.add(goal)
    await db_session.commit()

    # Available budget too low (need £2000/month, have £500)
    suggestions = await optimization_service.suggest_goal_adjustments(
        goal.id,
        Decimal('500.00')
    )

    # Should suggest extending timeline
    extend = next(
        (s for s in suggestions if s["adjustment_type"] == "EXTEND_TIMELINE"),
        None
    )

    assert extend is not None
    assert "new_value" in extend
    assert extend["feasibility"] == "HIGHLY_FEASIBLE"


@pytest.mark.asyncio
async def test_suggest_adjustments_reduce_target(
    optimization_service: GoalOptimizationService,
    db_session: AsyncSession,
    test_user_id
):
    """Test adjustment suggestion to reduce target amount."""
    # Create goal with very high target
    goal = FinancialGoal(
        id=uuid4(),
        user_id=test_user_id,
        goal_name="Expensive Goal",
        goal_type=GoalType.CUSTOM,
        target_amount=Decimal('100000.00'),
        currency='GBP',
        current_amount=Decimal('0.00'),
        target_date=date.today() + relativedelta(months=12),
        start_date=date.today(),
        priority=GoalPriority.MEDIUM,
        status=GoalStatus.NOT_STARTED
    )
    db_session.add(goal)
    await db_session.commit()

    # Very limited budget
    suggestions = await optimization_service.suggest_goal_adjustments(
        goal.id,
        Decimal('200.00')
    )

    # Should suggest reducing target
    reduce = next(
        (s for s in suggestions if s["adjustment_type"] == "REDUCE_TARGET"),
        None
    )

    assert reduce is not None
    assert "new_value" in reduce
    assert reduce["feasibility"] == "FEASIBLE"


@pytest.mark.asyncio
async def test_suggest_adjustments_increase_contributions(
    optimization_service: GoalOptimizationService,
    db_session: AsyncSession,
    test_user_id
):
    """Test adjustment suggestion to increase contributions for at-risk goal."""
    # Create at-risk goal with available budget
    goal = FinancialGoal(
        id=uuid4(),
        user_id=test_user_id,
        goal_name="At Risk Goal",
        goal_type=GoalType.CUSTOM,
        target_amount=Decimal('12000.00'),
        currency='GBP',
        current_amount=Decimal('1000.00'),
        target_date=date.today() + relativedelta(months=12),
        start_date=date.today() - relativedelta(months=12),
        priority=GoalPriority.HIGH,
        status=GoalStatus.AT_RISK
    )
    db_session.add(goal)
    await db_session.commit()

    # Plenty of budget available
    suggestions = await optimization_service.suggest_goal_adjustments(
        goal.id,
        Decimal('2000.00')
    )

    # Should suggest increasing contributions
    increase = next(
        (s for s in suggestions if s["adjustment_type"] == "INCREASE_CONTRIBUTIONS"),
        None
    )

    assert increase is not None
    assert "new_value" in increase
    assert increase["feasibility"] == "FEASIBLE"


@pytest.mark.asyncio
async def test_suggest_adjustments_pause_goal(
    optimization_service: GoalOptimizationService,
    db_session: AsyncSession,
    test_user_id
):
    """Test adjustment suggestion to pause infeasible goal."""
    # Create completely infeasible goal
    goal = FinancialGoal(
        id=uuid4(),
        user_id=test_user_id,
        goal_name="Infeasible Goal",
        goal_type=GoalType.CUSTOM,
        target_amount=Decimal('100000.00'),
        currency='GBP',
        current_amount=Decimal('0.00'),
        target_date=date.today() + relativedelta(months=6),
        start_date=date.today(),
        priority=GoalPriority.LOW,
        status=GoalStatus.NOT_STARTED
    )
    db_session.add(goal)
    await db_session.commit()

    # Zero budget
    suggestions = await optimization_service.suggest_goal_adjustments(
        goal.id,
        Decimal('0.00')
    )

    # Should suggest pausing
    pause = next(
        (s for s in suggestions if s["adjustment_type"] == "PAUSE_GOAL"),
        None
    )

    assert pause is not None
    assert pause["feasibility"] == "RECOMMENDED"


@pytest.mark.asyncio
async def test_suggest_adjustments_lump_sum(
    optimization_service: GoalOptimizationService,
    db_session: AsyncSession,
    test_user_id
):
    """Test adjustment suggestion for lump sum contribution."""
    # Create goal slightly over budget
    goal = FinancialGoal(
        id=uuid4(),
        user_id=test_user_id,
        goal_name="Goal Needing Lump Sum",
        goal_type=GoalType.CUSTOM,
        target_amount=Decimal('18000.00'),
        currency='GBP',
        current_amount=Decimal('0.00'),
        target_date=date.today() + relativedelta(months=12),
        start_date=date.today(),
        priority=GoalPriority.MEDIUM,
        status=GoalStatus.NOT_STARTED
    )
    db_session.add(goal)
    await db_session.commit()

    # Budget slightly under requirement
    suggestions = await optimization_service.suggest_goal_adjustments(
        goal.id,
        Decimal('1200.00')  # Need ~1500, have 1200
    )

    # Should suggest lump sum
    lump_sum = next(
        (s for s in suggestions if s["adjustment_type"] == "LUMP_SUM_CONTRIBUTION"),
        None
    )

    assert lump_sum is not None
    assert "new_value" in lump_sum


@pytest.mark.asyncio
async def test_suggest_adjustments_invalid_goal(
    optimization_service: GoalOptimizationService
):
    """Test adjustment suggestions with non-existent goal."""
    fake_id = uuid4()

    with pytest.raises(ValidationError):
        await optimization_service.suggest_goal_adjustments(
            fake_id,
            Decimal('1000.00')
        )


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_allocation_with_single_goal(
    optimization_service: GoalOptimizationService,
    db_session: AsyncSession,
    test_user_id
):
    """Test allocation with single goal."""
    goal = FinancialGoal(
        id=uuid4(),
        user_id=test_user_id,
        goal_name="Only Goal",
        goal_type=GoalType.CUSTOM,
        target_amount=Decimal('12000.00'),
        currency='GBP',
        current_amount=Decimal('0.00'),
        target_date=date.today() + relativedelta(months=12),
        start_date=date.today(),
        priority=GoalPriority.MEDIUM,
        status=GoalStatus.NOT_STARTED
    )
    db_session.add(goal)
    await db_session.commit()

    allocation = await optimization_service.allocate_available_savings(
        test_user_id,
        Decimal('1500.00')
    )

    # Should fully allocate to single goal
    assert len(allocation["allocations"]) == 1
    assert len(allocation["fully_funded_goals"]) == 1


@pytest.mark.asyncio
async def test_prioritize_handles_zero_days_to_target(
    optimization_service: GoalOptimizationService,
    db_session: AsyncSession,
    test_user_id
):
    """Test prioritization with goal at target date."""
    goal = FinancialGoal(
        id=uuid4(),
        user_id=test_user_id,
        goal_name="Due Today",
        goal_type=GoalType.CUSTOM,
        target_amount=Decimal('1000.00'),
        currency='GBP',
        current_amount=Decimal('500.00'),
        target_date=date.today(),
        start_date=date.today() - relativedelta(months=6),
        priority=GoalPriority.HIGH,
        status=GoalStatus.IN_PROGRESS
    )
    db_session.add(goal)
    await db_session.commit()

    # Should not crash
    prioritized = await optimization_service.prioritize_goals(test_user_id)

    assert len(prioritized) == 1
    # Should have high urgency
    assert prioritized[0]["urgency_score"] >= Decimal('80')
