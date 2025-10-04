"""
Financial goal planning database models.

This module provides SQLAlchemy models for:
- Financial goals with target amounts and timelines
- Goal milestones tracking
- Progress history with temporal data
- Goal recommendations and action items

Business logic:
- Multi-currency support for goal targets
- Automatic contribution tracking
- Linked accounts for progress calculation
- Soft delete for audit trail
- Temporal data for historical tracking
"""

import uuid
import enum
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column, String, ForeignKey, Numeric, Boolean, DateTime,
    Date, Text, CheckConstraint, Index, Enum as SQLEnum, Integer, ARRAY
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship, validates

from database import Base
from models.user import GUID


class GoalType(str, enum.Enum):
    """Financial goal type enumeration."""
    RETIREMENT = 'RETIREMENT'
    PROPERTY_PURCHASE = 'PROPERTY_PURCHASE'
    EDUCATION = 'EDUCATION'
    EMERGENCY_FUND = 'EMERGENCY_FUND'
    DEBT_PAYOFF = 'DEBT_PAYOFF'
    HOUSE_PURCHASE = 'HOUSE_PURCHASE'
    HOME_IMPROVEMENT = 'HOME_IMPROVEMENT'
    VEHICLE_PURCHASE = 'VEHICLE_PURCHASE'
    WEDDING = 'WEDDING'
    HOLIDAY_TRAVEL = 'HOLIDAY_TRAVEL'
    BUSINESS_START = 'BUSINESS_START'
    INHERITANCE_PLANNING = 'INHERITANCE_PLANNING'
    FINANCIAL_INDEPENDENCE = 'FINANCIAL_INDEPENDENCE'
    CHARITABLE_GIVING = 'CHARITABLE_GIVING'
    CUSTOM = 'CUSTOM'


class GoalPriority(str, enum.Enum):
    """Goal priority enumeration."""
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'


class GoalStatus(str, enum.Enum):
    """Goal status enumeration."""
    NOT_STARTED = 'NOT_STARTED'
    IN_PROGRESS = 'IN_PROGRESS'
    ON_TRACK = 'ON_TRACK'
    AT_RISK = 'AT_RISK'
    ACHIEVED = 'ACHIEVED'
    ABANDONED = 'ABANDONED'


class ContributionFrequency(str, enum.Enum):
    """Contribution frequency enumeration."""
    WEEKLY = 'WEEKLY'
    MONTHLY = 'MONTHLY'
    QUARTERLY = 'QUARTERLY'
    ANNUALLY = 'ANNUALLY'
    ONE_OFF = 'ONE_OFF'


class MilestoneStatus(str, enum.Enum):
    """Milestone status enumeration."""
    PENDING = 'PENDING'
    ACHIEVED = 'ACHIEVED'
    MISSED = 'MISSED'


class RecommendationType(str, enum.Enum):
    """Goal recommendation type enumeration."""
    OPEN_ACCOUNT = 'OPEN_ACCOUNT'
    AUTOMATE_SAVINGS = 'AUTOMATE_SAVINGS'
    LUMP_SUM_CONTRIBUTION = 'LUMP_SUM_CONTRIBUTION'
    MAXIMIZE_TAX_RELIEF = 'MAXIMIZE_TAX_RELIEF'
    ADJUST_GOAL = 'ADJUST_GOAL'
    INCREASE_INCOME = 'INCREASE_INCOME'
    REDUCE_EXPENSES = 'REDUCE_EXPENSES'
    DEPRIORITIZE_GOALS = 'DEPRIORITIZE_GOALS'
    OTHER = 'OTHER'


class FinancialGoal(Base):
    """
    Financial goal tracking with target amounts and timelines.

    Tracks user financial goals with:
    - Goal type, target amount, and target date
    - Current progress (calculated from linked accounts)
    - Priority and status
    - Auto-contribution settings
    - Soft delete for audit trail
    """

    __tablename__ = 'financial_goals'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Goal Details
    goal_name = Column(
        String(255),
        nullable=False,
        doc="User-friendly name for the goal"
    )
    goal_type = Column(
        SQLEnum(GoalType, name='goal_type_enum', create_type=False),
        nullable=False,
        index=True
    )
    description = Column(
        Text,
        nullable=True,
        doc="Optional detailed description of the goal"
    )

    # Target Details
    target_amount = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Target amount to save for the goal"
    )
    currency = Column(
        String(3),
        nullable=False,
        default='GBP',
        doc="Currency code (GBP, ZAR, USD, EUR)"
    )

    # Progress
    current_amount = Column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Current progress toward goal (calculated from linked accounts)"
    )
    progress_percentage = Column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal('0.00'),
        doc="Progress as percentage (0-100)"
    )

    # Timeline
    target_date = Column(
        Date,
        nullable=False,
        doc="Target date to achieve the goal"
    )
    start_date = Column(
        Date,
        nullable=False,
        default=date.today,
        doc="Date when goal tracking started"
    )

    # Priority and Status
    priority = Column(
        SQLEnum(GoalPriority, name='goal_priority_enum', create_type=False),
        nullable=False,
        default=GoalPriority.MEDIUM
    )
    status = Column(
        SQLEnum(GoalStatus, name='goal_status_enum', create_type=False),
        nullable=False,
        default=GoalStatus.NOT_STARTED,
        index=True
    )

    # Linked Accounts
    linked_accounts = Column(
        JSON,
        nullable=True,
        doc="Array of account IDs linked to this goal for progress tracking"
    )

    # Auto Contribution
    auto_contribution = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether automatic contributions are set up"
    )
    contribution_amount = Column(
        Numeric(10, 2),
        nullable=True,
        doc="Automatic contribution amount per period"
    )
    contribution_frequency = Column(
        SQLEnum(ContributionFrequency, name='contribution_frequency_enum', create_type=False),
        nullable=True,
        doc="Frequency of automatic contributions"
    )

    # Soft Delete
    deleted_at = Column(
        DateTime,
        nullable=True,
        doc="Soft delete timestamp"
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    achieved_at = Column(
        DateTime,
        nullable=True,
        doc="Timestamp when goal was achieved"
    )

    # Relationships
    user = relationship("User", backref="financial_goals")
    milestones = relationship(
        "GoalMilestone",
        back_populates="goal",
        cascade="all, delete-orphan",
        order_by="GoalMilestone.milestone_target_date"
    )
    progress_history = relationship(
        "GoalProgressHistory",
        back_populates="goal",
        cascade="all, delete-orphan",
        order_by="desc(GoalProgressHistory.snapshot_date)"
    )
    recommendations = relationship(
        "GoalRecommendation",
        back_populates="goal",
        cascade="all, delete-orphan",
        order_by="desc(GoalRecommendation.created_date)"
    )

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'target_amount > 0',
            name='check_goal_positive_target_amount'
        ),
        CheckConstraint(
            'current_amount >= 0',
            name='check_goal_non_negative_current_amount'
        ),
        CheckConstraint(
            'progress_percentage >= 0 AND progress_percentage <= 100',
            name='check_goal_valid_progress_percentage'
        ),
        CheckConstraint(
            'target_date > start_date',
            name='check_goal_target_after_start'
        ),
        CheckConstraint(
            'contribution_amount IS NULL OR contribution_amount >= 0',
            name='check_goal_non_negative_contribution'
        ),
        Index('idx_goal_user_status', 'user_id', 'status'),
        Index('idx_goal_user_deleted', 'user_id', 'deleted_at'),
        Index('idx_goal_user_type', 'user_id', 'goal_type'),
        Index('idx_goal_target_date', 'target_date'),
    )

    def calculate_progress_percentage(self) -> Decimal:
        """
        Calculate progress percentage toward goal.

        Returns:
            Decimal: Progress percentage (0-100)
        """
        if self.target_amount == 0:
            return Decimal('0.00')

        percentage = (Decimal(str(self.current_amount)) / Decimal(str(self.target_amount))) * 100
        return min(percentage, Decimal('100.00'))

    def is_on_track(self) -> bool:
        """
        Determine if goal is on track based on timeline and progress.

        Returns:
            bool: True if on track, False otherwise
        """
        if self.status in [GoalStatus.ACHIEVED, GoalStatus.ABANDONED]:
            return False

        days_total = (self.target_date - self.start_date).days
        days_elapsed = (date.today() - self.start_date).days

        if days_total <= 0:
            return False

        expected_progress = (days_elapsed / days_total) * 100
        actual_progress = float(self.progress_percentage)

        # Allow 10% variance
        return actual_progress >= (expected_progress - 10)

    def days_remaining(self) -> int:
        """
        Calculate days remaining until target date.

        Returns:
            int: Days remaining (can be negative if overdue)
        """
        return (self.target_date - date.today()).days

    def __repr__(self) -> str:
        return (
            f"<FinancialGoal(id={self.id}, user_id={self.user_id}, "
            f"name={self.goal_name}, target={self.target_amount} {self.currency}, "
            f"status={self.status})>"
        )


class GoalMilestone(Base):
    """
    Goal milestone tracking for progress monitoring.

    Tracks milestones within a goal with:
    - Milestone target amounts and dates
    - Achievement status
    - Progress tracking
    """

    __tablename__ = 'goal_milestones'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    goal_id = Column(
        GUID,
        ForeignKey('financial_goals.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Milestone Details
    milestone_name = Column(
        String(255),
        nullable=False,
        doc="Descriptive name for the milestone"
    )
    milestone_target_amount = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Target amount for this milestone"
    )
    milestone_target_date = Column(
        Date,
        nullable=False,
        doc="Target date for achieving this milestone"
    )

    # Achievement
    status = Column(
        SQLEnum(MilestoneStatus, name='milestone_status_enum', create_type=False),
        nullable=False,
        default=MilestoneStatus.PENDING
    )
    achieved_date = Column(
        Date,
        nullable=True,
        doc="Date when milestone was achieved"
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    goal = relationship("FinancialGoal", back_populates="milestones")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'milestone_target_amount > 0',
            name='check_milestone_positive_target_amount'
        ),
        Index('idx_milestone_goal_status', 'goal_id', 'status'),
        Index('idx_milestone_goal_date', 'goal_id', 'milestone_target_date'),
    )

    def is_achieved(self, current_amount: Decimal) -> bool:
        """
        Check if milestone is achieved based on current amount.

        Args:
            current_amount: Current goal progress amount

        Returns:
            bool: True if milestone target reached
        """
        return Decimal(str(current_amount)) >= Decimal(str(self.milestone_target_amount))

    def __repr__(self) -> str:
        return (
            f"<GoalMilestone(id={self.id}, goal_id={self.goal_id}, "
            f"name={self.milestone_name}, status={self.status})>"
        )


class GoalProgressHistory(Base):
    """
    Goal progress history with temporal tracking.

    Tracks goal progress over time with:
    - Snapshot of amounts and targets at specific dates
    - Progress percentage at snapshot time
    - On-track status
    - Projected completion dates
    - Temporal data support (effective_from/effective_to)
    """

    __tablename__ = 'goal_progress_history'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    goal_id = Column(
        GUID,
        ForeignKey('financial_goals.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Snapshot Data
    snapshot_date = Column(
        Date,
        nullable=False,
        doc="Date of this progress snapshot"
    )
    amount_at_snapshot = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Goal progress amount at snapshot date"
    )
    target_amount_at_snapshot = Column(
        Numeric(15, 2),
        nullable=False,
        doc="Target amount at snapshot date (may change over time)"
    )
    progress_percentage = Column(
        Numeric(5, 2),
        nullable=False,
        doc="Progress percentage at snapshot (0-100)"
    )

    # Status
    on_track = Column(
        Boolean,
        nullable=False,
        default=True,
        doc="Whether goal was on track at snapshot date"
    )
    projected_completion_date = Column(
        Date,
        nullable=True,
        doc="Projected completion date based on snapshot data"
    )

    # Temporal Data Support
    effective_from = Column(
        Date,
        nullable=False,
        doc="Start date when this snapshot is effective"
    )
    effective_to = Column(
        Date,
        nullable=True,
        doc="End date when this snapshot stops (NULL = current)"
    )

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    goal = relationship("FinancialGoal", back_populates="progress_history")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'amount_at_snapshot >= 0',
            name='check_progress_non_negative_amount'
        ),
        CheckConstraint(
            'target_amount_at_snapshot > 0',
            name='check_progress_positive_target'
        ),
        CheckConstraint(
            'progress_percentage >= 0 AND progress_percentage <= 100',
            name='check_progress_valid_percentage'
        ),
        CheckConstraint(
            'effective_to IS NULL OR effective_to >= effective_from',
            name='check_progress_valid_effective_dates'
        ),
        Index('idx_progress_goal_date', 'goal_id', 'snapshot_date'),
        Index('idx_progress_effective_dates', 'goal_id', 'effective_from', 'effective_to'),
    )

    def __repr__(self) -> str:
        return (
            f"<GoalProgressHistory(id={self.id}, goal_id={self.goal_id}, "
            f"snapshot_date={self.snapshot_date}, progress={self.progress_percentage}%)>"
        )


class GoalRecommendation(Base):
    """
    Goal recommendations and action items.

    Tracks AI-driven and rule-based recommendations for goals with:
    - Recommendation type and text
    - Action items
    - Priority
    - Dismissal tracking
    """

    __tablename__ = 'goal_recommendations'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    goal_id = Column(
        GUID,
        ForeignKey('financial_goals.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Recommendation Details
    recommendation_type = Column(
        SQLEnum(RecommendationType, name='recommendation_type_enum', create_type=False),
        nullable=False
    )
    recommendation_text = Column(
        Text,
        nullable=False,
        doc="Detailed recommendation text"
    )
    action_items = Column(
        JSON,
        nullable=True,
        doc="Array of specific action items for the user"
    )

    # Priority
    priority = Column(
        SQLEnum(GoalPriority, name='goal_priority_enum', create_type=False),
        nullable=False,
        default=GoalPriority.MEDIUM
    )

    # Dismissal
    dismissed = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether user has dismissed this recommendation"
    )
    dismissed_at = Column(
        DateTime,
        nullable=True,
        doc="Timestamp when recommendation was dismissed"
    )

    # Timestamps
    created_date = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    goal = relationship("FinancialGoal", back_populates="recommendations")

    # Table Constraints
    __table_args__ = (
        Index('idx_recommendation_goal_dismissed', 'goal_id', 'dismissed'),
        Index('idx_recommendation_goal_priority', 'goal_id', 'priority'),
    )

    def dismiss(self) -> None:
        """Mark recommendation as dismissed."""
        self.dismissed = True
        self.dismissed_at = datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"<GoalRecommendation(id={self.id}, goal_id={self.goal_id}, "
            f"type={self.recommendation_type}, priority={self.priority})>"
        )


# Additional indexes are already defined in __table_args__ for each model
# No need for standalone Index() definitions to avoid duplicates
