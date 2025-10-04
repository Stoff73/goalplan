"""add personalization tables

Revision ID: 20251004_0900
Revises: (add previous revision here)
Create Date: 2025-10-04 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251004_0900'
down_revision = 'i1j2k3l4m5n6'  # Points to scenario tables
branch_labels = None
depends_on = None


def upgrade():
    """Create personalization tables."""

    # Create ENUM types for PostgreSQL
    preference_type_enum = postgresql.ENUM(
        'DASHBOARD_LAYOUT',
        'DEFAULT_CURRENCY',
        'NOTIFICATION_FREQUENCY',
        'THEME',
        'NUMBER_FORMAT',
        'DATE_FORMAT',
        name='preference_type_enum',
        create_type=False
    )

    action_type_enum = postgresql.ENUM(
        'PAGE_VIEW',
        'FEATURE_USAGE',
        'TIME_SPENT',
        'CLICK',
        'FORM_SUBMIT',
        name='action_type_enum',
        create_type=False
    )

    insight_type_enum = postgresql.ENUM(
        'GOAL_ADVICE',
        'SAVINGS_TIP',
        'INVESTMENT_TIP',
        'TAX_TIP',
        'SPENDING_INSIGHT',
        name='insight_type_enum',
        create_type=False
    )

    # Create ENUM types if they don't exist
    op.execute("CREATE TYPE preference_type_enum AS ENUM ('DASHBOARD_LAYOUT', 'DEFAULT_CURRENCY', 'NOTIFICATION_FREQUENCY', 'THEME', 'NUMBER_FORMAT', 'DATE_FORMAT')")
    op.execute("CREATE TYPE action_type_enum AS ENUM ('PAGE_VIEW', 'FEATURE_USAGE', 'TIME_SPENT', 'CLICK', 'FORM_SUBMIT')")
    op.execute("CREATE TYPE insight_type_enum AS ENUM ('GOAL_ADVICE', 'SAVINGS_TIP', 'INVESTMENT_TIP', 'TAX_TIP', 'SPENDING_INSIGHT')")

    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('preference_type', preference_type_enum, nullable=False),
        sa.Column('preference_value', sa.Text(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for user_preferences
    op.create_index(
        'idx_user_preference_type',
        'user_preferences',
        ['user_id', 'preference_type']
    )
    op.create_index(
        'idx_user_preference_deleted',
        'user_preferences',
        ['user_id', 'deleted_at']
    )

    # Create user_behavior table
    op.create_table(
        'user_behavior',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action_type', action_type_enum, nullable=False),
        sa.Column('action_context', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for user_behavior
    op.create_index(
        'idx_user_behavior_timestamp',
        'user_behavior',
        ['user_id', 'timestamp']
    )
    op.create_index(
        'idx_user_behavior_action_type',
        'user_behavior',
        ['user_id', 'action_type']
    )
    op.create_index(
        'idx_user_id_behavior',
        'user_behavior',
        ['user_id']
    )
    op.create_index(
        'idx_action_type_behavior',
        'user_behavior',
        ['action_type']
    )
    op.create_index(
        'idx_timestamp_behavior',
        'user_behavior',
        ['timestamp']
    )

    # Create personalized_insights table
    op.create_table(
        'personalized_insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('insight_type', insight_type_enum, nullable=False),
        sa.Column('insight_text', sa.Text(), nullable=False),
        sa.Column('relevance_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('shown_date', sa.DateTime(), nullable=True),
        sa.Column('clicked', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('dismissed', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint(
            'relevance_score >= 0 AND relevance_score <= 100',
            name='check_insight_valid_relevance_score'
        ),
    )

    # Create indexes for personalized_insights
    op.create_index(
        'idx_user_insight_type',
        'personalized_insights',
        ['user_id', 'insight_type']
    )
    op.create_index(
        'idx_user_insight_relevance',
        'personalized_insights',
        ['user_id', 'relevance_score']
    )
    op.create_index(
        'idx_user_insight_deleted',
        'personalized_insights',
        ['user_id', 'deleted_at']
    )
    op.create_index(
        'idx_user_id_insights',
        'personalized_insights',
        ['user_id']
    )
    op.create_index(
        'idx_insight_type_insights',
        'personalized_insights',
        ['insight_type']
    )


def downgrade():
    """Drop personalization tables."""

    # Drop tables
    op.drop_table('personalized_insights')
    op.drop_table('user_behavior')
    op.drop_table('user_preferences')

    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS insight_type_enum')
    op.execute('DROP TYPE IF EXISTS action_type_enum')
    op.execute('DROP TYPE IF EXISTS preference_type_enum')
