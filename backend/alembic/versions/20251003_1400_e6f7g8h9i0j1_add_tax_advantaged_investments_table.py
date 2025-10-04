"""add_tax_advantaged_investments_table

Revision ID: e6f7g8h9i0j1
Revises: d5e6f7g8h9i0
Create Date: 2025-10-03 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e6f7g8h9i0j1'
down_revision = 'd5e6f7g8h9i0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""

    # Create scheme_type enum
    scheme_type_enum = postgresql.ENUM(
        'EIS', 'SEIS', 'VCT',
        name='scheme_type_enum',
        create_type=True
    )

    # Create tax_advantaged_investments table
    op.create_table(
        'tax_advantaged_investments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('holding_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Scheme Details
        sa.Column('scheme_type', scheme_type_enum, nullable=False),
        sa.Column('investment_date', sa.Date(), nullable=False),
        sa.Column('investment_amount', sa.Numeric(precision=15, scale=2), nullable=False),

        # Income Tax Relief
        sa.Column('income_tax_relief_claimed', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('income_tax_relief_percentage', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('tax_year_claimed', sa.String(length=7), nullable=False),

        # Holding Period
        sa.Column('minimum_holding_period_years', sa.Integer(), nullable=False),
        sa.Column('holding_period_end_date', sa.Date(), nullable=False),

        # CGT Benefits
        sa.Column('cgt_deferral_claimed', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('cgt_exemption_eligible', sa.Boolean(), nullable=False, server_default='false'),

        # Relief Status
        sa.Column('relief_withdrawn', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('relief_withdrawal_reason', sa.Text(), nullable=True),
        sa.Column('relief_withdrawal_date', sa.Date(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),

        # Foreign Keys
        sa.ForeignKeyConstraint(['holding_id'], ['investment_holdings.id'], ondelete='CASCADE'),

        # Unique constraint for one-to-one relationship
        sa.UniqueConstraint('holding_id', name='uq_tax_advantaged_holding_id'),

        # Check Constraints
        sa.CheckConstraint(
            'income_tax_relief_percentage IN (30.0, 50.0)',
            name='check_valid_relief_percentage'
        ),
        sa.CheckConstraint(
            'minimum_holding_period_years IN (3, 5)',
            name='check_valid_holding_period'
        ),
        sa.CheckConstraint(
            'investment_amount > 0',
            name='check_positive_investment_amount'
        ),
        sa.CheckConstraint(
            'income_tax_relief_claimed >= 0',
            name='check_non_negative_relief_claimed'
        ),
        sa.CheckConstraint(
            'cgt_deferral_claimed IS NULL OR cgt_deferral_claimed >= 0',
            name='check_non_negative_cgt_deferral'
        ),
    )

    # Create indexes
    op.create_index('idx_tax_advantaged_holding_id', 'tax_advantaged_investments', ['holding_id'])
    op.create_index('idx_tax_advantaged_scheme_type', 'tax_advantaged_investments', ['scheme_type'])
    op.create_index('idx_tax_advantaged_holding_period_end', 'tax_advantaged_investments', ['holding_period_end_date'])
    op.create_index('idx_tax_advantaged_at_risk', 'tax_advantaged_investments', ['holding_period_end_date', 'relief_withdrawn'])


def downgrade() -> None:
    """Downgrade database schema."""

    # Drop indexes
    op.drop_index('idx_tax_advantaged_at_risk', table_name='tax_advantaged_investments')
    op.drop_index('idx_tax_advantaged_holding_period_end', table_name='tax_advantaged_investments')
    op.drop_index('idx_tax_advantaged_scheme_type', table_name='tax_advantaged_investments')
    op.drop_index('idx_tax_advantaged_holding_id', table_name='tax_advantaged_investments')

    # Drop table
    op.drop_table('tax_advantaged_investments')

    # Drop ENUM type
    sa.Enum(name='scheme_type_enum').drop(op.get_bind(), checkfirst=True)
