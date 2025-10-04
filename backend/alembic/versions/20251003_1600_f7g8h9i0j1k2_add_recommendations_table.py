"""add recommendations table

Revision ID: f7g8h9i0j1k2
Revises: e6f7g8h9i0j1
Create Date: 2025-10-03 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f7g8h9i0j1k2'
down_revision = 'e6f7g8h9i0j1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create recommendations table and related enums."""

    # Create enums first (skip if they already exist)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE recommendation_type_enum AS ENUM ('PROTECTION', 'ISA', 'TFSA', 'EMERGENCY_FUND', 'TAX_EFFICIENCY', 'PENSION', 'INVESTMENT_DIVERSIFICATION', 'CGT_HARVESTING', 'DEBT_REDUCTION');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE recommendation_priority_enum AS ENUM ('HIGH', 'MEDIUM', 'LOW');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('recommendation_type', sa.Enum(
            'PROTECTION',
            'ISA',
            'TFSA',
            'EMERGENCY_FUND',
            'TAX_EFFICIENCY',
            'PENSION',
            'INVESTMENT_DIVERSIFICATION',
            'CGT_HARVESTING',
            'DEBT_REDUCTION',
            name='recommendation_type_enum',
            create_type=False
        ), nullable=False),
        sa.Column('priority', sa.Enum(
            'HIGH',
            'MEDIUM',
            'LOW',
            name='recommendation_priority_enum',
            create_type=False
        ), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('action_items', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('potential_savings', sa.Numeric(12, 2), nullable=True),
        sa.Column('currency', sa.Enum(
            'GBP',
            'ZAR',
            'USD',
            'EUR',
            name='currency_enum',
            create_type=False
        ), nullable=False, server_default='GBP'),
        sa.Column('created_date', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('dismissed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('dismissed_date', sa.DateTime(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('completed_date', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint(
            'potential_savings IS NULL OR potential_savings >= 0',
            name='check_non_negative_potential_savings'
        )
    )

    # Create indexes
    op.create_index(
        'idx_recommendation_user_id',
        'recommendations',
        ['user_id']
    )

    op.create_index(
        'idx_recommendation_type',
        'recommendations',
        ['recommendation_type']
    )

    op.create_index(
        'idx_recommendation_priority',
        'recommendations',
        ['priority', 'created_date']
    )

    op.create_index(
        'idx_recommendation_dismissed',
        'recommendations',
        ['dismissed']
    )

    op.create_index(
        'idx_recommendation_completed',
        'recommendations',
        ['completed']
    )

    op.create_index(
        'idx_recommendation_deleted',
        'recommendations',
        ['deleted']
    )

    op.create_index(
        'idx_recommendation_user_active',
        'recommendations',
        ['user_id', 'deleted', 'dismissed']
    )

    op.create_index(
        'idx_recommendation_user_priority',
        'recommendations',
        ['user_id', 'priority', sa.text('created_date DESC')]
    )

    op.create_index(
        'idx_recommendation_active_by_type',
        'recommendations',
        ['recommendation_type', 'deleted', 'dismissed']
    )


def downgrade() -> None:
    """Drop recommendations table and related enums."""

    # Drop indexes
    op.drop_index('idx_recommendation_active_by_type', 'recommendations')
    op.drop_index('idx_recommendation_user_priority', 'recommendations')
    op.drop_index('idx_recommendation_user_active', 'recommendations')
    op.drop_index('idx_recommendation_deleted', 'recommendations')
    op.drop_index('idx_recommendation_completed', 'recommendations')
    op.drop_index('idx_recommendation_dismissed', 'recommendations')
    op.drop_index('idx_recommendation_priority', 'recommendations')
    op.drop_index('idx_recommendation_type', 'recommendations')
    op.drop_index('idx_recommendation_user_id', 'recommendations')

    # Drop table
    op.drop_table('recommendations')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS recommendation_priority_enum")
    op.execute("DROP TYPE IF EXISTS recommendation_type_enum")
