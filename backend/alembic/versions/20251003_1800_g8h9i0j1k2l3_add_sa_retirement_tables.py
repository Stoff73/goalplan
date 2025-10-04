"""add SA retirement tables

Revision ID: g8h9i0j1k2l3
Revises: f7g8h9i0j1k2
Create Date: 2025-10-03 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'g8h9i0j1k2l3'
down_revision = 'f7g8h9i0j1k2'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add SA retirement fund tables and enum types.

    Tables:
    - sa_retirement_funds: Main fund tracking
    - sa_fund_contributions: Contribution tracking with temporal data
    - sa_retirement_deduction_limits: Section 10C deduction tracking

    Enums:
    - sa_fund_type_enum: PENSION_FUND, PROVIDENT_FUND, RETIREMENT_ANNUITY, PRESERVATION_FUND
    - sa_fund_status_enum: ACTIVE, PRESERVED, PAID_OUT, TRANSFERRED
    """

    # Create SA fund type enum
    sa_fund_type_enum = postgresql.ENUM(
        'PENSION_FUND',
        'PROVIDENT_FUND',
        'RETIREMENT_ANNUITY',
        'PRESERVATION_FUND',
        name='sa_fund_type_enum',
        create_type=True
    )
    sa_fund_type_enum.create(op.get_bind(), checkfirst=True)

    # Create SA fund status enum
    sa_fund_status_enum = postgresql.ENUM(
        'ACTIVE',
        'PRESERVED',
        'PAID_OUT',
        'TRANSFERRED',
        name='sa_fund_status_enum',
        create_type=True
    )
    sa_fund_status_enum.create(op.get_bind(), checkfirst=True)

    # Create sa_retirement_funds table
    op.create_table(
        'sa_retirement_funds',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fund_type', sa_fund_type_enum, nullable=False),
        sa.Column('provider', sa.String(length=255), nullable=False),
        sa.Column('fund_name', sa.String(length=255), nullable=False),
        sa.Column('fund_number_encrypted', sa.Text(), nullable=False),
        sa.Column('employer_name', sa.String(length=255), nullable=True),
        sa.Column('current_value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('retirement_age', sa.Integer(), nullable=False),
        sa.Column('investment_strategy', sa.Enum('CONSERVATIVE', 'BALANCED', 'AGGRESSIVE', 'CUSTOM', name='investment_strategy_enum', create_type=False), nullable=True),
        sa.Column('assumed_growth_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('status', sa_fund_status_enum, nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('current_value >= 0', name='check_sa_fund_non_negative_value'),
        sa.CheckConstraint('retirement_age >= 55 AND retirement_age <= 75', name='check_sa_fund_valid_retirement_age'),
        sa.CheckConstraint('assumed_growth_rate IS NULL OR assumed_growth_rate >= 0', name='check_sa_fund_non_negative_growth')
    )

    # Create indexes for sa_retirement_funds
    op.create_index('idx_sa_fund_user_status', 'sa_retirement_funds', ['user_id', 'status'])
    op.create_index('idx_sa_fund_user_deleted', 'sa_retirement_funds', ['user_id', 'is_deleted'])
    op.create_index('idx_sa_fund_type', 'sa_retirement_funds', ['fund_type'])
    op.create_index(op.f('ix_sa_retirement_funds_user_id'), 'sa_retirement_funds', ['user_id'])

    # Create sa_fund_contributions table
    op.create_table(
        'sa_fund_contributions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fund_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_contribution', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('employer_contribution', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('contribution_date', sa.Date(), nullable=False),
        sa.Column('tax_year', sa.String(length=9), nullable=False),
        sa.Column('tax_deduction_claimed', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['fund_id'], ['sa_retirement_funds.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('employee_contribution IS NULL OR employee_contribution >= 0', name='check_sa_contribution_non_negative_employee'),
        sa.CheckConstraint('employer_contribution IS NULL OR employer_contribution >= 0', name='check_sa_contribution_non_negative_employer'),
        sa.CheckConstraint('tax_deduction_claimed IS NULL OR tax_deduction_claimed >= 0', name='check_sa_contribution_non_negative_deduction'),
        sa.CheckConstraint('effective_to IS NULL OR effective_to >= effective_from', name='check_sa_contribution_valid_effective_dates')
    )

    # Create indexes for sa_fund_contributions
    op.create_index('idx_sa_contribution_fund_tax_year', 'sa_fund_contributions', ['fund_id', 'tax_year'])
    op.create_index('idx_sa_contribution_effective_dates', 'sa_fund_contributions', ['fund_id', 'effective_from', 'effective_to'])
    op.create_index('idx_sa_contribution_date', 'sa_fund_contributions', ['contribution_date'])
    op.create_index(op.f('ix_sa_fund_contributions_fund_id'), 'sa_fund_contributions', ['fund_id'])

    # Create sa_retirement_deduction_limits table
    op.create_table(
        'sa_retirement_deduction_limits',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tax_year', sa.String(length=9), nullable=False),
        sa.Column('annual_deduction_limit', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('deductions_claimed', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('deductions_remaining', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('annual_deduction_limit >= 0', name='check_sa_deduction_non_negative_limit'),
        sa.CheckConstraint('deductions_claimed >= 0', name='check_sa_deduction_non_negative_claimed'),
        sa.CheckConstraint('deductions_remaining >= 0', name='check_sa_deduction_non_negative_remaining')
    )

    # Create indexes for sa_retirement_deduction_limits
    op.create_index('idx_sa_deduction_user_tax_year', 'sa_retirement_deduction_limits', ['user_id', 'tax_year'], unique=True)
    op.create_index(op.f('ix_sa_retirement_deduction_limits_user_id'), 'sa_retirement_deduction_limits', ['user_id'])


def downgrade():
    """Remove SA retirement fund tables and enum types."""

    # Drop tables
    op.drop_table('sa_retirement_deduction_limits')
    op.drop_table('sa_fund_contributions')
    op.drop_table('sa_retirement_funds')

    # Drop enums
    sa_fund_status_enum = postgresql.ENUM(
        'ACTIVE',
        'PRESERVED',
        'PAID_OUT',
        'TRANSFERRED',
        name='sa_fund_status_enum'
    )
    sa_fund_status_enum.drop(op.get_bind(), checkfirst=True)

    sa_fund_type_enum = postgresql.ENUM(
        'PENSION_FUND',
        'PROVIDENT_FUND',
        'RETIREMENT_ANNUITY',
        'PRESERVATION_FUND',
        name='sa_fund_type_enum'
    )
    sa_fund_type_enum.drop(op.get_bind(), checkfirst=True)
