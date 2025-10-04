"""Add goal planning tables

Revision ID: 20251003_2400
Revises: 20251003_2300
Create Date: 2025-10-03 00:00:00.000000

This migration creates tables for financial goal planning:
- financial_goals: Main goal tracking with targets and progress
- goal_milestones: Milestone tracking within goals
- goal_progress_history: Historical progress tracking with temporal data
- goal_recommendations: AI-driven and rule-based recommendations
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251003_2400'
down_revision = '20251003_2300'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create goal planning tables.
    """
    # Create ENUM types
    op.execute("""
        CREATE TYPE goal_type_enum AS ENUM (
            'RETIREMENT', 'PROPERTY_PURCHASE', 'EDUCATION', 'EMERGENCY_FUND',
            'DEBT_PAYOFF', 'HOUSE_PURCHASE', 'HOME_IMPROVEMENT', 'VEHICLE_PURCHASE',
            'WEDDING', 'HOLIDAY_TRAVEL', 'BUSINESS_START', 'INHERITANCE_PLANNING',
            'FINANCIAL_INDEPENDENCE', 'CHARITABLE_GIVING', 'CUSTOM'
        )
    """)

    op.execute("""
        CREATE TYPE goal_priority_enum AS ENUM ('HIGH', 'MEDIUM', 'LOW')
    """)

    op.execute("""
        CREATE TYPE goal_status_enum AS ENUM (
            'NOT_STARTED', 'IN_PROGRESS', 'ON_TRACK', 'AT_RISK', 'ACHIEVED', 'ABANDONED'
        )
    """)

    op.execute("""
        CREATE TYPE contribution_frequency_enum AS ENUM (
            'WEEKLY', 'MONTHLY', 'QUARTERLY', 'ANNUALLY', 'ONE_OFF'
        )
    """)

    op.execute("""
        CREATE TYPE milestone_status_enum AS ENUM ('PENDING', 'ACHIEVED', 'MISSED')
    """)

    op.execute("""
        CREATE TYPE recommendation_type_enum AS ENUM (
            'OPEN_ACCOUNT', 'AUTOMATE_SAVINGS', 'LUMP_SUM_CONTRIBUTION',
            'MAXIMIZE_TAX_RELIEF', 'ADJUST_GOAL', 'INCREASE_INCOME',
            'REDUCE_EXPENSES', 'DEPRIORITIZE_GOALS', 'OTHER'
        )
    """)

    # Create financial_goals table
    op.create_table(
        'financial_goals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('goal_name', sa.String(length=255), nullable=False),
        sa.Column('goal_type', postgresql.ENUM(name='goal_type_enum', create_type=False), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='GBP'),
        sa.Column('current_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),
        sa.Column('progress_percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.00'),
        sa.Column('target_date', sa.Date(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('priority', postgresql.ENUM(name='goal_priority_enum', create_type=False), nullable=False, server_default='MEDIUM'),
        sa.Column('status', postgresql.ENUM(name='goal_status_enum', create_type=False), nullable=False, server_default='NOT_STARTED'),
        sa.Column('linked_accounts', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('auto_contribution', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('contribution_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('contribution_frequency', postgresql.ENUM(name='contribution_frequency_enum', create_type=False), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('achieved_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint('target_amount > 0', name='check_goal_positive_target_amount'),
        sa.CheckConstraint('current_amount >= 0', name='check_goal_non_negative_current_amount'),
        sa.CheckConstraint('progress_percentage >= 0 AND progress_percentage <= 100', name='check_goal_valid_progress_percentage'),
        sa.CheckConstraint('target_date > start_date', name='check_goal_target_after_start'),
        sa.CheckConstraint('contribution_amount IS NULL OR contribution_amount >= 0', name='check_goal_non_negative_contribution'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for financial_goals
    op.create_index('idx_goal_user_id', 'financial_goals', ['user_id'])
    op.create_index('idx_goal_goal_type', 'financial_goals', ['goal_type'])
    op.create_index('idx_goal_status', 'financial_goals', ['status'])
    op.create_index('idx_goal_user_status', 'financial_goals', ['user_id', 'status'])
    op.create_index('idx_goal_user_deleted', 'financial_goals', ['user_id', 'deleted_at'])
    op.create_index('idx_goal_user_type', 'financial_goals', ['user_id', 'goal_type'])
    op.create_index('idx_goal_target_date', 'financial_goals', ['target_date'])
    op.create_index('idx_goal_user_priority', 'financial_goals', ['user_id', 'priority'])

    # Create goal_milestones table
    op.create_table(
        'goal_milestones',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('goal_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('milestone_name', sa.String(length=255), nullable=False),
        sa.Column('milestone_target_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('milestone_target_date', sa.Date(), nullable=False),
        sa.Column('status', postgresql.ENUM(name='milestone_status_enum', create_type=False), nullable=False, server_default='PENDING'),
        sa.Column('achieved_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('milestone_target_amount > 0', name='check_milestone_positive_target_amount'),
        sa.ForeignKeyConstraint(['goal_id'], ['financial_goals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for goal_milestones
    op.create_index('idx_milestone_goal_id', 'goal_milestones', ['goal_id'])
    op.create_index('idx_milestone_status', 'goal_milestones', ['status'])
    op.create_index('idx_milestone_goal_status', 'goal_milestones', ['goal_id', 'status'])
    op.create_index('idx_milestone_goal_date', 'goal_milestones', ['goal_id', 'milestone_target_date'])

    # Create goal_progress_history table
    op.create_table(
        'goal_progress_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('goal_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('amount_at_snapshot', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('target_amount_at_snapshot', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('progress_percentage', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('on_track', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('projected_completion_date', sa.Date(), nullable=True),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('amount_at_snapshot >= 0', name='check_progress_non_negative_amount'),
        sa.CheckConstraint('target_amount_at_snapshot > 0', name='check_progress_positive_target'),
        sa.CheckConstraint('progress_percentage >= 0 AND progress_percentage <= 100', name='check_progress_valid_percentage'),
        sa.CheckConstraint('effective_to IS NULL OR effective_to >= effective_from', name='check_progress_valid_effective_dates'),
        sa.ForeignKeyConstraint(['goal_id'], ['financial_goals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for goal_progress_history
    op.create_index('idx_progress_goal_id', 'goal_progress_history', ['goal_id'])
    op.create_index('idx_progress_on_track', 'goal_progress_history', ['on_track'])
    op.create_index('idx_progress_goal_date', 'goal_progress_history', ['goal_id', 'snapshot_date'])
    op.create_index('idx_progress_effective_dates', 'goal_progress_history', ['goal_id', 'effective_from', 'effective_to'])

    # Create goal_recommendations table
    op.create_table(
        'goal_recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('goal_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recommendation_type', postgresql.ENUM(name='recommendation_type_enum', create_type=False), nullable=False),
        sa.Column('recommendation_text', sa.Text(), nullable=False),
        sa.Column('action_items', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('priority', postgresql.ENUM(name='goal_priority_enum', create_type=False), nullable=False, server_default='MEDIUM'),
        sa.Column('dismissed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('dismissed_at', sa.DateTime(), nullable=True),
        sa.Column('created_date', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['goal_id'], ['financial_goals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for goal_recommendations
    op.create_index('idx_recommendation_goal_id', 'goal_recommendations', ['goal_id'])
    op.create_index('idx_recommendation_type', 'goal_recommendations', ['recommendation_type'])
    op.create_index('idx_recommendation_goal_dismissed', 'goal_recommendations', ['goal_id', 'dismissed'])
    op.create_index('idx_recommendation_goal_priority', 'goal_recommendations', ['goal_id', 'priority'])


def downgrade() -> None:
    """
    Drop goal planning tables and ENUM types.
    """
    # Drop tables (in reverse order of creation due to foreign keys)
    op.drop_table('goal_recommendations')
    op.drop_table('goal_progress_history')
    op.drop_table('goal_milestones')
    op.drop_table('financial_goals')

    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS recommendation_type_enum')
    op.execute('DROP TYPE IF EXISTS milestone_status_enum')
    op.execute('DROP TYPE IF EXISTS contribution_frequency_enum')
    op.execute('DROP TYPE IF EXISTS goal_status_enum')
    op.execute('DROP TYPE IF EXISTS goal_priority_enum')
    op.execute('DROP TYPE IF EXISTS goal_type_enum')
