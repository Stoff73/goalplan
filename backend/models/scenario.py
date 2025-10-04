"""
Scenario Analysis and What-If Modeling Models

This module contains database models for scenario planning:
- Scenario: User-created financial scenarios
- ScenarioAssumption: Assumptions for each scenario (e.g., retirement_age=65)
- ScenarioResult: Calculated results and projections for scenarios

Supports:
- Multiple scenario types (retirement age, career change, property, etc.)
- Flexible assumptions storage (JSON)
- Comprehensive result tracking
- Scenario comparison

Business Rules:
- Maximum 5 active scenarios per user
- Scenarios expire after 90 days if not accessed
- Calculation time: <5 seconds per scenario
- Can model up to 30 years into future
"""

import enum
import uuid
from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey,
    String, Text, Index, Integer, Numeric, CheckConstraint
)
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from database import Base
from models.user import GUID


class ScenarioType(str, enum.Enum):
    """
    Types of financial scenarios that can be modeled.

    Each type applies different modifications to the user's baseline financial state.
    """
    RETIREMENT_AGE_CHANGE = "RETIREMENT_AGE_CHANGE"
    RELOCATION = "RELOCATION"
    CAREER_CHANGE = "CAREER_CHANGE"
    BUSINESS_SALE = "BUSINESS_SALE"
    PROPERTY_PURCHASE = "PROPERTY_PURCHASE"
    PROPERTY_SALE = "PROPERTY_SALE"
    INHERITANCE_RECEIVED = "INHERITANCE_RECEIVED"
    MAJOR_EXPENSE = "MAJOR_EXPENSE"
    INVESTMENT_STRATEGY_CHANGE = "INVESTMENT_STRATEGY_CHANGE"
    TAX_RESIDENCY_CHANGE = "TAX_RESIDENCY_CHANGE"
    DIVORCE_SEPARATION = "DIVORCE_SEPARATION"
    MARRIAGE = "MARRIAGE"
    CHILD_BIRTH = "CHILD_BIRTH"
    CUSTOM = "CUSTOM"


class ScenarioStatus(str, enum.Enum):
    """
    Scenario processing status.

    - DRAFT: Created but not calculated
    - CALCULATED: Results available
    - ARCHIVED: Expired or no longer relevant
    """
    DRAFT = "DRAFT"
    CALCULATED = "CALCULATED"
    ARCHIVED = "ARCHIVED"


class Scenario(Base):
    """
    Financial scenario model.

    Stores user-created scenarios for what-if analysis.
    Each scenario applies modifications to the user's baseline financial state.

    Fields:
        id: Primary key (UUID)
        user_id: Foreign key to users table
        scenario_name: User-provided scenario name
        scenario_type: Type of scenario (RETIREMENT_AGE_CHANGE, etc.)
        description: Optional scenario description
        base_case: Whether this is the base case scenario (one per user)
        status: Scenario status (DRAFT, CALCULATED, ARCHIVED)
        created_at: Scenario creation timestamp
        updated_at: Last update timestamp
        last_accessed_at: Last time scenario was accessed
        expires_at: Expiration timestamp (90 days from last access)

    Relationships:
        user: The user who created this scenario
        assumptions: Assumptions for this scenario
        results: Calculated results for this scenario

    Constraints:
        - Maximum 5 active (non-archived) scenarios per user
        - Only one base_case per user
    """
    __tablename__ = "scenarios"

    # Primary Key
    id = Column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique scenario identifier"
    )

    # Foreign Keys
    user_id = Column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="User who created this scenario"
    )

    # Scenario Details
    scenario_name = Column(
        String(255),
        nullable=False,
        doc="User-provided scenario name"
    )
    scenario_type = Column(
        Enum(ScenarioType),
        nullable=False,
        doc="Type of scenario"
    )
    description = Column(
        Text,
        nullable=True,
        doc="Optional scenario description"
    )
    base_case = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is the base case scenario"
    )
    status = Column(
        Enum(ScenarioStatus),
        default=ScenarioStatus.DRAFT,
        nullable=False,
        index=True,
        doc="Scenario processing status"
    )

    # Audit Fields
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Scenario creation timestamp"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Last update timestamp"
    )
    last_accessed_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        doc="Last access timestamp (for expiration)"
    )
    expires_at = Column(
        DateTime,
        nullable=False,
        index=True,
        doc="Expiration timestamp (90 days from last access)"
    )

    # Relationships
    user = relationship("User", backref="scenarios")
    assumptions = relationship(
        "ScenarioAssumption",
        back_populates="scenario",
        cascade="all, delete-orphan",
        order_by="ScenarioAssumption.created_at"
    )
    results = relationship(
        "ScenarioResult",
        back_populates="scenario",
        uselist=False,  # One-to-one
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Scenario."""
        return f"<Scenario(id={self.id}, name={self.scenario_name}, type={self.scenario_type.value})>"


class ScenarioAssumption(Base):
    """
    Scenario assumption model.

    Stores individual assumptions for a scenario.
    Examples: retirement_age=65, salary_increase=3%, property_value=500000

    Fields:
        id: Primary key (UUID)
        scenario_id: Foreign key to scenarios table
        assumption_type: Type of assumption (e.g., 'retirement_age', 'salary')
        assumption_key: Specific key for the assumption
        assumption_value: Value of the assumption (stored as string, parsed as needed)
        unit: Optional unit (e.g., 'years', 'GBP', '%')
        created_at: Assumption creation timestamp

    Relationships:
        scenario: The scenario this assumption belongs to
    """
    __tablename__ = "scenario_assumptions"

    # Primary Key
    id = Column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique assumption identifier"
    )

    # Foreign Keys
    scenario_id = Column(
        GUID,
        ForeignKey("scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Scenario this assumption belongs to"
    )

    # Assumption Details
    assumption_type = Column(
        String(100),
        nullable=False,
        doc="Type of assumption (e.g., 'retirement_age', 'salary')"
    )
    assumption_key = Column(
        String(100),
        nullable=False,
        doc="Specific key for the assumption"
    )
    assumption_value = Column(
        String(500),
        nullable=False,
        doc="Value of the assumption (stored as string)"
    )
    unit = Column(
        String(50),
        nullable=True,
        doc="Optional unit (e.g., 'years', 'GBP', '%')"
    )

    # Audit Fields
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Assumption creation timestamp"
    )

    # Relationships
    scenario = relationship("Scenario", back_populates="assumptions")

    def __repr__(self) -> str:
        """String representation of ScenarioAssumption."""
        return f"<ScenarioAssumption(type={self.assumption_type}, key={self.assumption_key}, value={self.assumption_value})>"


class ScenarioResult(Base):
    """
    Scenario result model.

    Stores calculated results and projections for a scenario.
    Results include net worth projections, retirement income, tax liability, etc.

    Fields:
        id: Primary key (UUID)
        scenario_id: Foreign key to scenarios table (one-to-one)
        calculation_date: When results were calculated
        calculation_version: Version of calculation engine used
        projection_years: Number of years projected
        net_worth_projection: Net worth projection over time (JSON array)
        retirement_income_projection: Retirement income projection (JSON)
        tax_liability_projection: Tax liability over time (JSON array)
        goal_achievement_projection: Goal achievement likelihood (JSON)
        detailed_breakdown: Full detailed results (JSON)
        total_lifetime_tax: Total tax paid over projection period
        final_net_worth: Final net worth at end of projection
        retirement_adequacy_ratio: Retirement income vs needed (%)
        goals_achieved_count: Number of goals achieved
        goals_achieved_percentage: Percentage of goals achieved
        probability_of_success: Monte Carlo success probability (%)
        created_at: Result creation timestamp

    Relationships:
        scenario: The scenario these results belong to

    Constraints:
        - projection_years between 1 and 30
        - Probabilities between 0 and 100
    """
    __tablename__ = "scenario_results"

    # Primary Key
    id = Column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique result identifier"
    )

    # Foreign Keys (one-to-one with scenario)
    scenario_id = Column(
        GUID,
        ForeignKey("scenarios.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        doc="Scenario these results belong to"
    )

    # Calculation Metadata
    calculation_date = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="When results were calculated"
    )
    calculation_version = Column(
        String(50),
        nullable=False,
        default="1.0.0",
        doc="Version of calculation engine"
    )
    projection_years = Column(
        Integer,
        nullable=False,
        doc="Number of years projected"
    )

    # Projection Results (stored as JSON for flexibility)
    net_worth_projection = Column(
        JSON,
        nullable=True,
        doc="Net worth projection over time (array of year objects)"
    )
    retirement_income_projection = Column(
        JSON,
        nullable=True,
        doc="Retirement income projection by source"
    )
    tax_liability_projection = Column(
        JSON,
        nullable=True,
        doc="Tax liability over time (array of year objects)"
    )
    goal_achievement_projection = Column(
        JSON,
        nullable=True,
        doc="Goal achievement likelihood and timeline"
    )
    detailed_breakdown = Column(
        JSON,
        nullable=True,
        doc="Full detailed results and breakdowns"
    )

    # Summary Metrics
    total_lifetime_tax = Column(
        Numeric(15, 2),
        nullable=True,
        doc="Total tax paid over projection period"
    )
    final_net_worth = Column(
        Numeric(15, 2),
        nullable=True,
        doc="Final net worth at end of projection"
    )
    retirement_adequacy_ratio = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Retirement income vs needed (%)"
    )
    goals_achieved_count = Column(
        Integer,
        nullable=True,
        default=0,
        doc="Number of goals achieved"
    )
    goals_achieved_percentage = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Percentage of goals achieved"
    )
    probability_of_success = Column(
        Numeric(5, 2),
        nullable=True,
        doc="Monte Carlo success probability (%)"
    )

    # Audit Fields
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Result creation timestamp"
    )

    # Relationships
    scenario = relationship("Scenario", back_populates="results")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            'projection_years >= 1 AND projection_years <= 30',
            name='check_projection_years_range'
        ),
        CheckConstraint(
            'probability_of_success IS NULL OR (probability_of_success >= 0 AND probability_of_success <= 100)',
            name='check_probability_range'
        ),
        CheckConstraint(
            'retirement_adequacy_ratio IS NULL OR retirement_adequacy_ratio >= 0',
            name='check_adequacy_ratio_positive'
        ),
        CheckConstraint(
            'goals_achieved_percentage IS NULL OR (goals_achieved_percentage >= 0 AND goals_achieved_percentage <= 100)',
            name='check_goals_percentage_range'
        ),
    )

    def __repr__(self) -> str:
        """String representation of ScenarioResult."""
        return f"<ScenarioResult(scenario_id={self.scenario_id}, final_net_worth={self.final_net_worth})>"


# Create indexes for efficient querying
Index("idx_scenarios_user_status", Scenario.user_id, Scenario.status)
Index("idx_scenarios_user_base_case", Scenario.user_id, Scenario.base_case)
Index("idx_scenarios_expires_at", Scenario.expires_at)
Index("idx_scenario_assumptions_scenario_type", ScenarioAssumption.scenario_id, ScenarioAssumption.assumption_type)
Index("idx_scenario_results_scenario_id", ScenarioResult.scenario_id, unique=True)
