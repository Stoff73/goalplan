"""
Personalization Engine database models.

This module provides SQLAlchemy models for:
- User preferences (dashboard layout, currency, notifications, etc.)
- User behavior tracking (page views, feature usage, clicks)
- Personalized insights (tailored recommendations)

Business logic:
- Track user preferences for personalized UX
- Log user actions for behavior analysis
- Generate personalized insights based on user profile
- Support soft delete for audit trail
- Temporal data for historical tracking
"""

import uuid
import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column, String, ForeignKey, Numeric, Boolean, DateTime,
    Text, Index, Enum as SQLEnum, CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship, Mapped

from database import Base
from models.user import GUID


class PreferenceType(str, enum.Enum):
    """User preference type enumeration."""
    DASHBOARD_LAYOUT = 'DASHBOARD_LAYOUT'
    DEFAULT_CURRENCY = 'DEFAULT_CURRENCY'
    NOTIFICATION_FREQUENCY = 'NOTIFICATION_FREQUENCY'
    THEME = 'THEME'
    NUMBER_FORMAT = 'NUMBER_FORMAT'
    DATE_FORMAT = 'DATE_FORMAT'


class ActionType(str, enum.Enum):
    """User action type enumeration."""
    PAGE_VIEW = 'PAGE_VIEW'
    FEATURE_USAGE = 'FEATURE_USAGE'
    TIME_SPENT = 'TIME_SPENT'
    CLICK = 'CLICK'
    FORM_SUBMIT = 'FORM_SUBMIT'


class InsightType(str, enum.Enum):
    """Personalized insight type enumeration."""
    GOAL_ADVICE = 'GOAL_ADVICE'
    SAVINGS_TIP = 'SAVINGS_TIP'
    INVESTMENT_TIP = 'INVESTMENT_TIP'
    TAX_TIP = 'TAX_TIP'
    SPENDING_INSIGHT = 'SPENDING_INSIGHT'


class UserPreference(Base):
    """
    User preference storage for personalized UX.

    Tracks user preferences for:
    - Dashboard layout and widget order
    - Default currency and number formats
    - Notification frequency
    - Theme (light/dark)
    - Date formats

    Supports soft delete for audit trail.
    """

    __tablename__ = 'user_preferences'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Preference Details
    preference_type = Column(
        SQLEnum(PreferenceType, name='preference_type_enum', create_type=False),
        nullable=False,
        doc="Type of preference (layout, currency, notifications, etc.)"
    )
    preference_value = Column(
        Text,
        nullable=False,
        doc="Preference value (JSON string for complex preferences)"
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

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="preferences")

    # Table Constraints
    __table_args__ = (
        Index('idx_user_preference_type', 'user_id', 'preference_type'),
        Index('idx_user_preference_deleted', 'user_id', 'deleted_at'),
    )

    def __repr__(self) -> str:
        return (
            f"<UserPreference(id={self.id}, user_id={self.user_id}, "
            f"type={self.preference_type})>"
        )


class UserBehavior(Base):
    """
    User behavior tracking for personalization.

    Logs user actions with:
    - Action type (page view, feature usage, clicks)
    - Action context (JSON metadata)
    - Timestamp for analysis

    Used for:
    - Engagement analysis
    - Feature usage tracking
    - Personalized dashboard layouts
    - Recommendation relevance scoring
    """

    __tablename__ = 'user_behavior'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Action Details
    action_type = Column(
        SQLEnum(ActionType, name='action_type_enum', create_type=False),
        nullable=False,
        index=True,
        doc="Type of action performed"
    )
    action_context = Column(
        Text,
        nullable=False,
        doc="Action context as JSON (page, feature, duration, etc.)"
    )

    # Timestamp
    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        doc="When the action occurred (UTC)"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="behaviors")

    # Table Constraints
    __table_args__ = (
        Index('idx_user_behavior_timestamp', 'user_id', 'timestamp'),
        Index('idx_user_behavior_action_type', 'user_id', 'action_type'),
    )

    def __repr__(self) -> str:
        return (
            f"<UserBehavior(id={self.id}, user_id={self.user_id}, "
            f"action_type={self.action_type}, timestamp={self.timestamp})>"
        )


class PersonalizedInsight(Base):
    """
    Personalized insights for users.

    Generates tailored insights based on:
    - User goals and financial data
    - Behavior patterns
    - Financial situation

    Types of insights:
    - Goal advice (progress recommendations)
    - Savings tips (account optimization)
    - Investment tips (portfolio suggestions)
    - Tax tips (tax efficiency opportunities)
    - Spending insights (behavior analysis)

    Tracks:
    - Relevance score (0-100)
    - Whether shown to user
    - Whether clicked/dismissed
    - Soft delete for audit trail
    """

    __tablename__ = 'personalized_insights'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Insight Details
    insight_type = Column(
        SQLEnum(InsightType, name='insight_type_enum', create_type=False),
        nullable=False,
        index=True,
        doc="Type of insight"
    )
    insight_text = Column(
        Text,
        nullable=False,
        doc="Insight content (personalized message)"
    )
    relevance_score = Column(
        Numeric(5, 2),
        nullable=False,
        doc="Relevance score (0-100)"
    )

    # Engagement Tracking
    shown_date = Column(
        DateTime,
        nullable=True,
        doc="When insight was shown to user"
    )
    clicked = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether user clicked on insight"
    )
    dismissed = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether user dismissed insight"
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

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="insights")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'relevance_score >= 0 AND relevance_score <= 100',
            name='check_insight_valid_relevance_score'
        ),
        Index('idx_user_insight_type', 'user_id', 'insight_type'),
        Index('idx_user_insight_relevance', 'user_id', 'relevance_score'),
        Index('idx_user_insight_deleted', 'user_id', 'deleted_at'),
    )

    def mark_shown(self) -> None:
        """Mark insight as shown to user."""
        if not self.shown_date:
            self.shown_date = datetime.utcnow()

    def mark_clicked(self) -> None:
        """Mark insight as clicked by user."""
        self.clicked = True
        if not self.shown_date:
            self.shown_date = datetime.utcnow()

    def mark_dismissed(self) -> None:
        """Mark insight as dismissed by user."""
        self.dismissed = True
        if not self.shown_date:
            self.shown_date = datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"<PersonalizedInsight(id={self.id}, user_id={self.user_id}, "
            f"type={self.insight_type}, relevance={self.relevance_score})>"
        )
