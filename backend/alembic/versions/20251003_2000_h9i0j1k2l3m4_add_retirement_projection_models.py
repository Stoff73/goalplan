"""add retirement projection models

Revision ID: h9i0j1k2l3m4
Revises: g8h9i0j1k2l3
Create Date: 2025-10-03 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'h9i0j1k2l3m4'
down_revision = 'g8h9i0j1k2l3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create retirement projection tables."""

    # Create retirement_projections table
    op.create_table(
        'retirement_projections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('projection_date', sa.Date(), nullable=False),
        sa.Column('target_retirement_age', sa.Integer(), nullable=False),
        sa.Column('projected_total_pot', sa.Numeric(15, 2), nullable=False, server_default='0.00'),
        sa.Column('annual_income_needed', sa.Numeric(10, 2), nullable=False),
        sa.Column('state_pension_income', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('db_pension_income', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('dc_drawdown_income', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('other_income', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('total_projected_income', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('income_gap', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('on_track', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('growth_assumptions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('inflation_rate', sa.Numeric(5, 2), nullable=False, server_default='2.50'),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('target_retirement_age >= 55', name='check_projection_valid_retirement_age'),
        sa.CheckConstraint('projected_total_pot >= 0', name='check_projection_non_negative_pot'),
        sa.CheckConstraint('annual_income_needed > 0', name='check_projection_positive_income_needed'),
        sa.CheckConstraint('state_pension_income >= 0', name='check_projection_non_negative_state_pension'),
        sa.CheckConstraint('db_pension_income >= 0', name='check_projection_non_negative_db_pension'),
        sa.CheckConstraint('dc_drawdown_income >= 0', name='check_projection_non_negative_dc_drawdown'),
        sa.CheckConstraint('other_income >= 0', name='check_projection_non_negative_other_income'),
        sa.CheckConstraint('total_projected_income >= 0', name='check_projection_non_negative_total_income'),
        sa.CheckConstraint('inflation_rate >= 0', name='check_projection_non_negative_inflation'),
        sa.CheckConstraint('effective_to IS NULL OR effective_to >= effective_from', name='check_projection_valid_effective_dates')
    )

    # Create indexes for retirement_projections
    op.create_index('idx_projection_user_id', 'retirement_projections', ['user_id'])
    op.create_index('idx_projection_user_date', 'retirement_projections', ['user_id', 'projection_date'])
    op.create_index('idx_projection_effective_dates', 'retirement_projections', ['user_id', 'effective_from', 'effective_to'])
    op.create_index('idx_retirement_projection_date', 'retirement_projections', ['projection_date'])
    op.create_index('idx_retirement_projection_on_track', 'retirement_projections', ['on_track'])

    # Create drawdown_scenarios table
    op.create_table(
        'drawdown_scenarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pension_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scenario_name', sa.String(100), nullable=False),
        sa.Column('drawdown_rate', sa.Numeric(5, 2), nullable=False),
        sa.Column('start_age', sa.Integer(), nullable=False),
        sa.Column('projected_annual_income', sa.Numeric(10, 2), nullable=False),
        sa.Column('pot_depletion_age', sa.Integer(), nullable=True),
        sa.Column('tax_implications', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('assumptions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['pension_id'], ['uk_pensions.id'], ondelete='CASCADE'),
        sa.CheckConstraint('drawdown_rate >= 2 AND drawdown_rate <= 8', name='check_drawdown_valid_rate'),
        sa.CheckConstraint('start_age >= 55 AND start_age <= 75', name='check_drawdown_valid_start_age'),
        sa.CheckConstraint('projected_annual_income >= 0', name='check_drawdown_non_negative_income'),
        sa.CheckConstraint('pot_depletion_age IS NULL OR pot_depletion_age >= start_age', name='check_drawdown_valid_depletion_age')
    )

    # Create indexes for drawdown_scenarios
    op.create_index('idx_drawdown_pension_id', 'drawdown_scenarios', ['pension_id'])
    op.create_index('idx_drawdown_pension_scenario', 'drawdown_scenarios', ['pension_id', 'scenario_name'])
    op.create_index('idx_drawdown_scenario_name', 'drawdown_scenarios', ['scenario_name'])


def downgrade() -> None:
    """Drop retirement projection tables."""

    # Drop drawdown_scenarios table
    op.drop_index('idx_drawdown_scenario_name', table_name='drawdown_scenarios')
    op.drop_index('idx_drawdown_pension_scenario', table_name='drawdown_scenarios')
    op.drop_index('idx_drawdown_pension_id', table_name='drawdown_scenarios')
    op.drop_table('drawdown_scenarios')

    # Drop retirement_projections table
    op.drop_index('idx_retirement_projection_on_track', table_name='retirement_projections')
    op.drop_index('idx_retirement_projection_date', table_name='retirement_projections')
    op.drop_index('idx_projection_effective_dates', table_name='retirement_projections')
    op.drop_index('idx_projection_user_date', table_name='retirement_projections')
    op.drop_index('idx_projection_user_id', table_name='retirement_projections')
    op.drop_table('retirement_projections')
