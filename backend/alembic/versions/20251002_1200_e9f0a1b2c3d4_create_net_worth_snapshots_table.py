"""create_net_worth_snapshots_table

Revision ID: e9f0a1b2c3d4
Revises: d8e9f0a1b2c3
Create Date: 2025-10-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e9f0a1b2c3d4'
down_revision = 'd8e9f0a1b2c3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""

    # Create net_worth_snapshots table
    op.create_table(
        'net_worth_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('base_currency', sa.String(length=3), nullable=False),

        # Net Worth Summary
        sa.Column('net_worth', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('total_assets', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('total_liabilities', sa.Numeric(precision=15, scale=2), nullable=False),

        # Breakdown Data (JSONB for flexibility)
        sa.Column('breakdown_by_country', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('breakdown_by_asset_class', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('breakdown_by_currency', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # Metadata
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Foreign key
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),

        # Constraints
        sa.UniqueConstraint('user_id', 'snapshot_date', name='unique_snapshot_per_user_per_day'),
        sa.CheckConstraint('total_assets >= 0', name='check_non_negative_assets'),
        sa.CheckConstraint('total_liabilities >= 0', name='check_non_negative_liabilities'),
    )

    # Create indexes for performance
    op.create_index(
        'idx_snapshot_user_id',
        'net_worth_snapshots',
        ['user_id'],
        unique=False
    )

    op.create_index(
        'idx_snapshot_user_date_desc',
        'net_worth_snapshots',
        ['user_id', sa.text('snapshot_date DESC')],
        unique=False
    )

    op.create_index(
        'idx_snapshot_date_cleanup',
        'net_worth_snapshots',
        ['snapshot_date'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade database schema."""

    # Drop indexes
    op.drop_index('idx_snapshot_date_cleanup', table_name='net_worth_snapshots')
    op.drop_index('idx_snapshot_user_date_desc', table_name='net_worth_snapshots')
    op.drop_index('idx_snapshot_user_id', table_name='net_worth_snapshots')

    # Drop table
    op.drop_table('net_worth_snapshots')
