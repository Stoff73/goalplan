"""
Comprehensive tests for financial goal planning models.

Tests cover:
- Financial goal creation with all types
- Milestone tracking
- Progress history with temporal data
- Goal recommendations
- Model constraints and validations
- Soft delete functionality
- Calculated properties and methods
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from dateutil.relativedelta import relativedelta

from models.goal import (
    FinancialGoal,
    GoalMilestone,
    GoalProgressHistory,
    GoalRecommendation,
    GoalType,
    GoalPriority,
    GoalStatus,
    ContributionFrequency,
    MilestoneStatus,
    RecommendationType
)
from models.user import User, UserStatus, CountryPreference


@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    user = User(
        email=f"test_{uuid4()}@example.com",
        first_name="Test",
        last_name="User",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        terms_accepted_at=datetime.utcnow()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


class TestFinancialGoalModel:
    """Tests for FinancialGoal model."""

    @pytest.mark.asyncio
    async def test_create_financial_goal_all_types(self, db_session, test_user):
        """Test creating goals with all goal types."""
        goal_types = [
            GoalType.RETIREMENT,
            GoalType.PROPERTY_PURCHASE,
            GoalType.EDUCATION,
            GoalType.EMERGENCY_FUND,
            GoalType.DEBT_PAYOFF
        ]

        for goal_type in goal_types:
            goal = FinancialGoal(
                user_id=test_user.id,
                goal_name=f"Test {goal_type.value} Goal",
                goal_type=goal_type,
                target_amount=Decimal('50000.00'),
                currency='GBP',
                target_date=date.today() + relativedelta(years=5),
                start_date=date.today(),
                priority=GoalPriority.HIGH
            )
            db_session.add(goal)
            await db_session.commit()
            await db_session.refresh(goal)

            assert goal.id is not None
            assert goal.goal_type == goal_type
            assert goal.status == GoalStatus.NOT_STARTED
            assert goal.current_amount == Decimal('0.00')
            assert goal.progress_percentage == Decimal('0.00')

    @pytest.mark.asyncio
    async def test_goal_with_auto_contribution(self, db_session, test_user):
        """Test creating goal with auto-contribution settings."""
        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="House Deposit",
            goal_type=GoalType.PROPERTY_PURCHASE,
            target_amount=Decimal('30000.00'),
            currency='GBP',
            target_date=date.today() + relativedelta(years=3),
            start_date=date.today(),
            auto_contribution=True,
            contribution_amount=Decimal('500.00'),
            contribution_frequency=ContributionFrequency.MONTHLY
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        assert goal.auto_contribution is True
        assert goal.contribution_amount == Decimal('500.00')
        assert goal.contribution_frequency == ContributionFrequency.MONTHLY

    @pytest.mark.asyncio
    async def test_goal_with_linked_accounts(self, db_session, test_user):
        """Test creating goal with linked accounts."""
        account_ids = [str(uuid4()), str(uuid4())]

        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="Emergency Fund",
            goal_type=GoalType.EMERGENCY_FUND,
            target_amount=Decimal('10000.00'),
            currency='GBP',
            target_date=date.today() + relativedelta(years=1),
            start_date=date.today(),
            linked_accounts=account_ids
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        assert goal.linked_accounts == account_ids
        assert len(goal.linked_accounts) == 2

    @pytest.mark.asyncio
    async def test_goal_target_amount_positive_constraint(self, db_session, test_user):
        """Test that target_amount must be positive."""
        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="Invalid Goal",
            goal_type=GoalType.CUSTOM,
            target_amount=Decimal('-1000.00'),  # Invalid: negative
            currency='GBP',
            target_date=date.today() + relativedelta(years=1),
            start_date=date.today()
        )
        db_session.add(goal)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert 'check_goal_positive_target_amount' in str(exc_info.value).lower() or 'constraint' in str(exc_info.value).lower()
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_calculate_progress_percentage(self, db_session, test_user):
        """Test progress percentage calculation."""
        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="Test Goal",
            goal_type=GoalType.CUSTOM,
            target_amount=Decimal('10000.00'),
            current_amount=Decimal('2500.00'),
            currency='GBP',
            target_date=date.today() + relativedelta(years=1),
            start_date=date.today()
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        percentage = goal.calculate_progress_percentage()
        assert percentage == Decimal('25.00')

    @pytest.mark.asyncio
    async def test_is_on_track_method(self, db_session, test_user):
        """Test on-track calculation based on timeline and progress."""
        # Goal 50% of the way through timeline with 50% progress
        start = date.today() - relativedelta(months=6)
        target = date.today() + relativedelta(months=6)

        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="Test Goal",
            goal_type=GoalType.CUSTOM,
            target_amount=Decimal('10000.00'),
            current_amount=Decimal('5000.00'),  # 50% progress
            progress_percentage=Decimal('50.00'),
            currency='GBP',
            target_date=target,
            start_date=start
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        assert goal.is_on_track() is True

    @pytest.mark.asyncio
    async def test_days_remaining_method(self, db_session, test_user):
        """Test days remaining calculation."""
        target = date.today() + relativedelta(days=100)

        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="Test Goal",
            goal_type=GoalType.CUSTOM,
            target_amount=Decimal('10000.00'),
            currency='GBP',
            target_date=target,
            start_date=date.today()
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        days = goal.days_remaining()
        assert days == 100

    @pytest.mark.asyncio
    async def test_soft_delete_functionality(self, db_session, test_user):
        """Test soft delete with deleted_at timestamp."""
        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="Test Goal",
            goal_type=GoalType.CUSTOM,
            target_amount=Decimal('10000.00'),
            currency='GBP',
            target_date=date.today() + relativedelta(years=1),
            start_date=date.today()
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        goal_id = goal.id

        # Soft delete
        goal.deleted_at = datetime.utcnow()
        await db_session.commit()

        # Goal still exists in database
        result = await db_session.execute(
            select(FinancialGoal).where(FinancialGoal.id == goal_id)
        )
        found_goal = result.scalar_one_or_none()
        assert found_goal is not None
        assert found_goal.deleted_at is not None


class TestGoalMilestoneModel:
    """Tests for GoalMilestone model."""

    @pytest.mark.asyncio
    async def test_create_milestone(self, db_session, test_user):
        """Test creating a milestone."""
        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="Test Goal",
            goal_type=GoalType.PROPERTY_PURCHASE,
            target_amount=Decimal('30000.00'),
            currency='GBP',
            target_date=date.today() + relativedelta(years=3),
            start_date=date.today()
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        milestone = GoalMilestone(
            goal_id=goal.id,
            milestone_name="25% Progress",
            milestone_target_amount=Decimal('7500.00'),
            milestone_target_date=date.today() + relativedelta(months=9)
        )
        db_session.add(milestone)
        await db_session.commit()
        await db_session.refresh(milestone)

        assert milestone.id is not None
        assert milestone.status == MilestoneStatus.PENDING
        assert milestone.achieved_date is None

    @pytest.mark.asyncio
    async def test_milestone_target_amount_positive_constraint(self, db_session, test_user):
        """Test that milestone_target_amount must be positive."""
        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="Test Goal",
            goal_type=GoalType.CUSTOM,
            target_amount=Decimal('10000.00'),
            currency='GBP',
            target_date=date.today() + relativedelta(years=1),
            start_date=date.today()
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        milestone = GoalMilestone(
            goal_id=goal.id,
            milestone_name="Invalid Milestone",
            milestone_target_amount=Decimal('-100.00'),  # Invalid: negative
            milestone_target_date=date.today() + relativedelta(months=6)
        )
        db_session.add(milestone)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert 'check_milestone_positive_target_amount' in str(exc_info.value).lower() or 'constraint' in str(exc_info.value).lower()
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_is_achieved_method(self, db_session, test_user):
        """Test milestone achievement check."""
        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="Test Goal",
            goal_type=GoalType.CUSTOM,
            target_amount=Decimal('10000.00'),
            currency='GBP',
            target_date=date.today() + relativedelta(years=1),
            start_date=date.today()
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        milestone = GoalMilestone(
            goal_id=goal.id,
            milestone_name="50% Progress",
            milestone_target_amount=Decimal('5000.00'),
            milestone_target_date=date.today() + relativedelta(months=6)
        )
        db_session.add(milestone)
        await db_session.commit()
        await db_session.refresh(milestone)

        # Not achieved yet
        assert milestone.is_achieved(Decimal('3000.00')) is False

        # Achieved
        assert milestone.is_achieved(Decimal('5000.00')) is True
        assert milestone.is_achieved(Decimal('6000.00')) is True


class TestGoalProgressHistoryModel:
    """Tests for GoalProgressHistory model."""

    @pytest.mark.asyncio
    async def test_create_progress_history(self, db_session, test_user):
        """Test creating progress history record."""
        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="Test Goal",
            goal_type=GoalType.CUSTOM,
            target_amount=Decimal('10000.00'),
            currency='GBP',
            target_date=date.today() + relativedelta(years=1),
            start_date=date.today()
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        progress = GoalProgressHistory(
            goal_id=goal.id,
            snapshot_date=date.today(),
            amount_at_snapshot=Decimal('2500.00'),
            target_amount_at_snapshot=Decimal('10000.00'),
            progress_percentage=Decimal('25.00'),
            on_track=True,
            effective_from=date.today()
        )
        db_session.add(progress)
        await db_session.commit()
        await db_session.refresh(progress)

        assert progress.id is not None
        assert progress.snapshot_date == date.today()
        assert progress.on_track is True
        assert progress.effective_to is None  # Current snapshot

    @pytest.mark.asyncio
    async def test_progress_temporal_data(self, db_session, test_user):
        """Test temporal data support with effective_from and effective_to."""
        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="Test Goal",
            goal_type=GoalType.CUSTOM,
            target_amount=Decimal('10000.00'),
            currency='GBP',
            target_date=date.today() + relativedelta(years=1),
            start_date=date.today()
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        # Historical snapshot (no longer current)
        old_progress = GoalProgressHistory(
            goal_id=goal.id,
            snapshot_date=date.today() - relativedelta(months=1),
            amount_at_snapshot=Decimal('1000.00'),
            target_amount_at_snapshot=Decimal('10000.00'),
            progress_percentage=Decimal('10.00'),
            on_track=True,
            effective_from=date.today() - relativedelta(months=1),
            effective_to=date.today()  # No longer current
        )
        db_session.add(old_progress)

        # Current snapshot
        current_progress = GoalProgressHistory(
            goal_id=goal.id,
            snapshot_date=date.today(),
            amount_at_snapshot=Decimal('2500.00'),
            target_amount_at_snapshot=Decimal('10000.00'),
            progress_percentage=Decimal('25.00'),
            on_track=True,
            effective_from=date.today(),
            effective_to=None  # Current
        )
        db_session.add(current_progress)
        await db_session.commit()

        # Query current snapshot
        result = await db_session.execute(
            select(GoalProgressHistory)
            .where(GoalProgressHistory.goal_id == goal.id)
            .where(GoalProgressHistory.effective_to.is_(None))
        )
        current = result.scalar_one_or_none()

        assert current is not None
        assert current.amount_at_snapshot == Decimal('2500.00')


class TestGoalRecommendationModel:
    """Tests for GoalRecommendation model."""

    @pytest.mark.asyncio
    async def test_create_recommendation(self, db_session, test_user):
        """Test creating a recommendation."""
        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="Test Goal",
            goal_type=GoalType.PROPERTY_PURCHASE,
            target_amount=Decimal('30000.00'),
            currency='GBP',
            target_date=date.today() + relativedelta(years=3),
            start_date=date.today()
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        recommendation = GoalRecommendation(
            goal_id=goal.id,
            recommendation_type=RecommendationType.AUTOMATE_SAVINGS,
            recommendation_text="Set up automatic monthly transfer of £500",
            action_items=[
                {"action": "Set up standing order", "completed": False},
                {"action": "Link savings account", "completed": False}
            ],
            priority=GoalPriority.HIGH
        )
        db_session.add(recommendation)
        await db_session.commit()
        await db_session.refresh(recommendation)

        assert recommendation.id is not None
        assert recommendation.dismissed is False
        assert recommendation.dismissed_at is None
        assert len(recommendation.action_items) == 2

    @pytest.mark.asyncio
    async def test_dismiss_recommendation(self, db_session, test_user):
        """Test dismissing a recommendation."""
        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="Test Goal",
            goal_type=GoalType.CUSTOM,
            target_amount=Decimal('10000.00'),
            currency='GBP',
            target_date=date.today() + relativedelta(years=1),
            start_date=date.today()
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        recommendation = GoalRecommendation(
            goal_id=goal.id,
            recommendation_type=RecommendationType.INCREASE_INCOME,
            recommendation_text="Consider taking on additional work",
            priority=GoalPriority.MEDIUM
        )
        db_session.add(recommendation)
        await db_session.commit()
        await db_session.refresh(recommendation)

        # Dismiss recommendation
        before_dismiss = datetime.utcnow()
        recommendation.dismiss()
        await db_session.commit()
        await db_session.refresh(recommendation)

        assert recommendation.dismissed is True
        assert recommendation.dismissed_at is not None
        assert recommendation.dismissed_at >= before_dismiss


class TestGoalRelationships:
    """Tests for goal model relationships."""

    @pytest.mark.asyncio
    async def test_goal_milestones_relationship(self, db_session, test_user):
        """Test goal to milestones relationship."""
        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="Test Goal",
            goal_type=GoalType.CUSTOM,
            target_amount=Decimal('10000.00'),
            currency='GBP',
            target_date=date.today() + relativedelta(years=1),
            start_date=date.today()
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        # Add milestones
        milestone1 = GoalMilestone(
            goal_id=goal.id,
            milestone_name="25% Progress",
            milestone_target_amount=Decimal('2500.00'),
            milestone_target_date=date.today() + relativedelta(months=3)
        )
        milestone2 = GoalMilestone(
            goal_id=goal.id,
            milestone_name="50% Progress",
            milestone_target_amount=Decimal('5000.00'),
            milestone_target_date=date.today() + relativedelta(months=6)
        )
        db_session.add_all([milestone1, milestone2])
        await db_session.commit()

        # Refresh and access milestones through relationship
        await db_session.refresh(goal)
        assert len(goal.milestones) == 2


class TestGoalIndexes:
    """Tests to verify indexes are working correctly."""

    @pytest.mark.asyncio
    async def test_user_status_index(self, db_session, test_user):
        """Test querying goals by user_id and status uses index."""
        # Create multiple goals with different statuses
        for i in range(5):
            goal = FinancialGoal(
                user_id=test_user.id,
                goal_name=f"Test Goal {i}",
                goal_type=GoalType.CUSTOM,
                target_amount=Decimal('10000.00'),
                currency='GBP',
                target_date=date.today() + relativedelta(years=1),
                start_date=date.today(),
                status=GoalStatus.IN_PROGRESS if i % 2 == 0 else GoalStatus.ON_TRACK
            )
            db_session.add(goal)
        await db_session.commit()

        # Query should use idx_goal_user_status
        result = await db_session.execute(
            select(FinancialGoal)
            .where(FinancialGoal.user_id == test_user.id)
            .where(FinancialGoal.status == GoalStatus.IN_PROGRESS)
        )
        goals = result.scalars().all()

        assert len(goals) == 3  # 3 IN_PROGRESS goals
