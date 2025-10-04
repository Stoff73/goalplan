"""
AI Recommendation models for personalized financial advice.

This module provides SQLAlchemy models for:
- Recommendations based on user's financial data
- Recommendation tracking (dismissed, completed)
- Priority and type classification
- Soft delete for audit trail

Business logic:
- Rule-based recommendation generation (Phase 2)
- AI/ML integration in Phase 4
- Multi-currency support for potential savings
- Action items and priority assignment
- User ownership verification
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
import enum

from sqlalchemy import (
    Column, String, ForeignKey, Numeric, Boolean, DateTime,
    Text, CheckConstraint, Index, Enum as SQLEnum, JSON
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, validates
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

from database import Base
from models.user import GUID


class RecommendationType(str, enum.Enum):
    """Recommendation type enumeration."""
    PROTECTION = 'PROTECTION'
    ISA = 'ISA'
    TFSA = 'TFSA'
    EMERGENCY_FUND = 'EMERGENCY_FUND'
    TAX_EFFICIENCY = 'TAX_EFFICIENCY'
    PENSION = 'PENSION'
    INVESTMENT_DIVERSIFICATION = 'INVESTMENT_DIVERSIFICATION'
    CGT_HARVESTING = 'CGT_HARVESTING'
    DEBT_REDUCTION = 'DEBT_REDUCTION'


class RecommendationPriority(str, enum.Enum):
    """Recommendation priority enumeration."""
    HIGH = 'HIGH'      # Immediate financial risk or significant savings (>£1,000/year)
    MEDIUM = 'MEDIUM'  # Good opportunities but not urgent (£500-£1,000/year)
    LOW = 'LOW'        # Nice to have, small impact (<£500/year)


class Currency(str, enum.Enum):
    """Supported currency codes."""
    GBP = 'GBP'
    ZAR = 'ZAR'
    USD = 'USD'
    EUR = 'EUR'


class Recommendation(Base):
    """
    Financial recommendation tracking.

    Stores personalized financial recommendations with:
    - Recommendation type and priority
    - Title, description, and action items
    - Potential savings calculation
    - Dismissal and completion tracking
    - Soft delete for audit trail
    """

    __tablename__ = 'recommendations'

    # Primary Key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Recommendation Classification
    recommendation_type = Column(
        SQLEnum(RecommendationType, name='recommendation_type_enum', create_type=False),
        nullable=False,
        index=True
    )
    priority = Column(
        SQLEnum(RecommendationPriority, name='recommendation_priority_enum', create_type=False),
        nullable=False,
        index=True
    )

    # Content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    action_items = Column(
        JSON,
        nullable=True,
        doc="List of specific actions user should take (JSON array for SQLite compatibility)"
    )

    # Financial Impact
    potential_savings = Column(
        Numeric(12, 2),
        nullable=True,
        doc="Estimated financial benefit in base currency"
    )
    currency = Column(
        SQLEnum(Currency, name='currency_enum', create_type=False),
        default=Currency.GBP,
        nullable=False
    )

    # Status Tracking
    created_date = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="When recommendation was generated"
    )

    dismissed = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Whether user dismissed this recommendation"
    )
    dismissed_date = Column(
        DateTime,
        nullable=True,
        doc="When recommendation was dismissed"
    )

    completed = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Whether user marked this as completed"
    )
    completed_date = Column(
        DateTime,
        nullable=True,
        doc="When recommendation was marked complete"
    )

    # Soft Delete
    deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Soft delete flag"
    )
    deleted_at = Column(
        DateTime,
        nullable=True,
        doc="When recommendation was deleted"
    )

    # Timestamps
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user = relationship("User", backref="recommendations")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            'potential_savings IS NULL OR potential_savings >= 0',
            name='check_non_negative_potential_savings'
        ),
        Index('idx_recommendation_user_active', 'user_id', 'deleted', 'dismissed'),
        Index('idx_recommendation_priority', 'priority', 'created_date'),
        Index('idx_recommendation_type', 'recommendation_type'),
    )

    def dismiss(self) -> None:
        """
        Dismiss this recommendation.

        Sets dismissed=True and dismissed_date=now.
        """
        self.dismissed = True
        self.dismissed_date = datetime.utcnow()

    def complete(self) -> None:
        """
        Mark this recommendation as completed.

        Sets completed=True and completed_date=now.
        """
        self.completed = True
        self.completed_date = datetime.utcnow()

    def soft_delete(self) -> None:
        """
        Soft delete this recommendation.

        Sets deleted=True and deleted_at=now.
        """
        self.deleted = True
        self.deleted_at = datetime.utcnow()

    @property
    def is_active(self) -> bool:
        """
        Check if recommendation is active (not dismissed, not deleted).

        Returns:
            bool: True if active
        """
        return not self.dismissed and not self.deleted

    def __repr__(self) -> str:
        return (
            f"<Recommendation(id={self.id}, user_id={self.user_id}, "
            f"type={self.recommendation_type}, priority={self.priority})>"
        )


# Create additional indexes for performance
Index(
    "idx_recommendation_user_priority",
    Recommendation.user_id,
    Recommendation.priority,
    Recommendation.created_date.desc()
)

Index(
    "idx_recommendation_active_by_type",
    Recommendation.recommendation_type,
    Recommendation.deleted,
    Recommendation.dismissed
)
