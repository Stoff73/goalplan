"""Add scenario analysis tables

Revision ID: i1j2k3l4m5n6
Revises: h9i0j1k2l3m4
Create Date: 2025-10-03 24:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'i1j2k3l4m5n6'
down_revision = 'h9i0j1k2l3m4'  # Points to retirement projection models
branch_labels = None
depends_on = None


def upgrade():
    """
    Create scenario analysis tables for what-if modeling.

    Tables:
    - scenarios: User-created financial scenarios
    - scenario_assumptions: Assumptions for each scenario
    - scenario_results: Calculated results and projections
    """

    # Create ScenarioType enum
    scenario_type_enum = postgresql.ENUM(
        'RETIREMENT_AGE_CHANGE',
        'RELOCATION',
        'CAREER_CHANGE',
        'BUSINESS_SALE',
        'PROPERTY_PURCHASE',
        'PROPERTY_SALE',
        'INHERITANCE_RECEIVED',
        'MAJOR_EXPENSE',
        'INVESTMENT_STRATEGY_CHANGE',
        'TAX_RESIDENCY_CHANGE',
        'DIVORCE_SEPARATION',
        'MARRIAGE',
        'CHILD_BIRTH',
        'CUSTOM',
        name='scenariotype'
    )
    scenario_type_enum.create(op.get_bind())

    # Create ScenarioStatus enum
    scenario_status_enum = postgresql.ENUM(
        'DRAFT',
        'CALCULATED',
        'ARCHIVED',
        name='scenariostatus'
    )
    scenario_status_enum.create(op.get_bind())

    # Create scenarios table
    op.create_table(
        'scenarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scenario_name', sa.String(255), nullable=False),
        sa.Column('scenario_type', scenario_type_enum, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('base_case', sa.Boolean, default=False, nullable=False),
        sa.Column('status', scenario_status_enum, default='DRAFT', nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('last_accessed_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
    )

    # Create indexes for scenarios
    op.create_index('idx_scenarios_user_status', 'scenarios', ['user_id', 'status'])
    op.create_index('idx_scenarios_user_base_case', 'scenarios', ['user_id', 'base_case'])
    op.create_index('idx_scenarios_expires_at', 'scenarios', ['expires_at'])

    # Create scenario_assumptions table
    op.create_table(
        'scenario_assumptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('scenario_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scenarios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assumption_type', sa.String(100), nullable=False),
        sa.Column('assumption_key', sa.String(100), nullable=False),
        sa.Column('assumption_value', sa.String(500), nullable=False),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
    )

    # Create indexes for scenario_assumptions
    op.create_index('idx_scenario_assumptions_scenario_type', 'scenario_assumptions', ['scenario_id', 'assumption_type'])

    # Create scenario_results table
    op.create_table(
        'scenario_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('scenario_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scenarios.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('calculation_date', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('calculation_version', sa.String(50), nullable=False, server_default='1.0.0'),
        sa.Column('projection_years', sa.Integer, nullable=False),
        sa.Column('net_worth_projection', sa.JSON, nullable=True),
        sa.Column('retirement_income_projection', sa.JSON, nullable=True),
        sa.Column('tax_liability_projection', sa.JSON, nullable=True),
        sa.Column('goal_achievement_projection', sa.JSON, nullable=True),
        sa.Column('detailed_breakdown', sa.JSON, nullable=True),
        sa.Column('total_lifetime_tax', sa.Numeric(15, 2), nullable=True),
        sa.Column('final_net_worth', sa.Numeric(15, 2), nullable=True),
        sa.Column('retirement_adequacy_ratio', sa.Numeric(5, 2), nullable=True),
        sa.Column('goals_achieved_count', sa.Integer, nullable=True, server_default='0'),
        sa.Column('goals_achieved_percentage', sa.Numeric(5, 2), nullable=True),
        sa.Column('probability_of_success', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),

        # Constraints
        sa.CheckConstraint(
            'projection_years >= 1 AND projection_years <= 30',
            name='check_projection_years_range'
        ),
        sa.CheckConstraint(
            'probability_of_success IS NULL OR (probability_of_success >= 0 AND probability_of_success <= 100)',
            name='check_probability_range'
        ),
        sa.CheckConstraint(
            'retirement_adequacy_ratio IS NULL OR retirement_adequacy_ratio >= 0',
            name='check_adequacy_ratio_positive'
        ),
        sa.CheckConstraint(
            'goals_achieved_percentage IS NULL OR (goals_achieved_percentage >= 0 AND goals_achieved_percentage <= 100)',
            name='check_goals_percentage_range'
        ),
    )

    # Create indexes for scenario_results
    op.create_index('idx_scenario_results_scenario_id', 'scenario_results', ['scenario_id'], unique=True)


def downgrade():
    """Drop scenario analysis tables."""

    # Drop indexes
    op.drop_index('idx_scenario_results_scenario_id', table_name='scenario_results')
    op.drop_index('idx_scenario_assumptions_scenario_type', table_name='scenario_assumptions')
    op.drop_index('idx_scenarios_expires_at', table_name='scenarios')
    op.drop_index('idx_scenarios_user_base_case', table_name='scenarios')
    op.drop_index('idx_scenarios_user_status', table_name='scenarios')

    # Drop tables
    op.drop_table('scenario_results')
    op.drop_table('scenario_assumptions')
    op.drop_table('scenarios')

    # Drop enums
    sa.Enum(name='scenariostatus').drop(op.get_bind())
    sa.Enum(name='scenariotype').drop(op.get_bind())
