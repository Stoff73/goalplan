"""add_coverage_calculation_models

Revision ID: b3c4d5e6f7g8
Revises: a2b3c4d5e6f7
Create Date: 2025-10-03 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b3c4d5e6f7g8'
down_revision = 'a2b3c4d5e6f7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""

    # Define reminder_type enum
    reminder_type_enum = postgresql.ENUM(
        'EMAIL', 'IN_APP',
        name='reminder_type_enum',
        create_type=True
    )

    # Create coverage_needs_analysis table
    op.create_table(
        'coverage_needs_analysis',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Analysis Date
        sa.Column('calculation_date', sa.Date(), nullable=False),

        # Income Replacement
        sa.Column('annual_income', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('income_multiplier', sa.Numeric(precision=3, scale=1), nullable=False, server_default='10.0'),

        # Financial Obligations
        sa.Column('outstanding_debts', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),

        # Children's Education
        sa.Column('children_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('education_cost_per_child', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),

        # Other Costs
        sa.Column('funeral_costs', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),

        # Existing Resources
        sa.Column('existing_assets', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),

        # Calculated Fields
        sa.Column('recommended_cover', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('current_total_cover', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),
        sa.Column('coverage_gap', sa.Numeric(precision=15, scale=2), nullable=False),

        # Notes
        sa.Column('notes', sa.Text(), nullable=True),

        # Temporal Data
        sa.Column('effective_from', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('effective_to', sa.DateTime(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),

        # Foreign Keys
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),

        # Check Constraints
        sa.CheckConstraint('annual_income >= 0', name='check_positive_annual_income'),
        sa.CheckConstraint('income_multiplier > 0', name='check_positive_income_multiplier'),
        sa.CheckConstraint('outstanding_debts >= 0', name='check_positive_debts'),
        sa.CheckConstraint('children_count >= 0', name='check_positive_children_count'),
        sa.CheckConstraint('education_cost_per_child >= 0', name='check_positive_education_cost'),
        sa.CheckConstraint('funeral_costs >= 0', name='check_positive_funeral_costs'),
        sa.CheckConstraint('existing_assets >= 0', name='check_positive_existing_assets'),
        sa.CheckConstraint('recommended_cover >= 0', name='check_positive_recommended_cover'),
        sa.CheckConstraint(
            'effective_to IS NULL OR effective_to > effective_from',
            name='check_valid_effective_dates'
        ),
    )

    # Create indexes for coverage_needs_analysis
    op.create_index(
        'idx_coverage_analysis_user_effective_from',
        'coverage_needs_analysis',
        ['user_id', 'effective_from']
    )
    op.create_index(
        'idx_coverage_analysis_user_effective_to',
        'coverage_needs_analysis',
        ['user_id', 'effective_to']
    )
    op.create_index(
        'idx_coverage_analysis_current',
        'coverage_needs_analysis',
        ['user_id', 'effective_to'],
        postgresql_where=sa.text('effective_to IS NULL')
    )
    op.create_index(
        'idx_coverage_analysis_user_id',
        'coverage_needs_analysis',
        ['user_id']
    )

    # Create policy_premium_reminders table
    op.create_table(
        'policy_premium_reminders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Reminder Details
        sa.Column('reminder_date', sa.Date(), nullable=False),
        sa.Column('reminder_type', reminder_type_enum, nullable=False, server_default='IN_APP'),

        # Status Tracking
        sa.Column('reminder_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sent_at', sa.DateTime(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),

        # Foreign Keys
        sa.ForeignKeyConstraint(['policy_id'], ['life_assurance_policies.id'], ondelete='CASCADE'),
    )

    # Create indexes for policy_premium_reminders
    op.create_index(
        'idx_premium_reminder_date_sent',
        'policy_premium_reminders',
        ['reminder_date', 'reminder_sent']
    )
    op.create_index(
        'idx_premium_reminder_policy',
        'policy_premium_reminders',
        ['policy_id']
    )


def downgrade() -> None:
    """Downgrade database schema."""

    # Drop policy_premium_reminders table and indexes
    op.drop_index('idx_premium_reminder_policy', table_name='policy_premium_reminders')
    op.drop_index('idx_premium_reminder_date_sent', table_name='policy_premium_reminders')
    op.drop_table('policy_premium_reminders')

    # Drop coverage_needs_analysis table and indexes
    op.drop_index('idx_coverage_analysis_user_id', table_name='coverage_needs_analysis')
    op.drop_index('idx_coverage_analysis_current', table_name='coverage_needs_analysis')
    op.drop_index('idx_coverage_analysis_user_effective_to', table_name='coverage_needs_analysis')
    op.drop_index('idx_coverage_analysis_user_effective_from', table_name='coverage_needs_analysis')
    op.drop_table('coverage_needs_analysis')

    # Drop enum types
    op.execute('DROP TYPE reminder_type_enum')
