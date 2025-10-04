"""add uk pension tables

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


def upgrade() -> None:
    """Create UK pension tables and related enums."""

    # Create enums first (skip if they already exist)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE pension_type_enum AS ENUM ('OCCUPATIONAL_DB', 'OCCUPATIONAL_DC', 'PERSONAL_PENSION', 'SIPP', 'STATE_PENSION');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE pension_status_enum AS ENUM ('ACTIVE', 'DEFERRED', 'IN_PAYMENT', 'TRANSFERRED_OUT');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE contribution_frequency_enum AS ENUM ('MONTHLY', 'ANNUAL', 'ONE_OFF');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE tax_relief_method_enum AS ENUM ('NET_PAY', 'RELIEF_AT_SOURCE');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE db_scheme_type_enum AS ENUM ('FINAL_SALARY', 'CAREER_AVERAGE', 'CASH_BALANCE');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE indexation_type_enum AS ENUM ('CPI', 'RPI', 'FIXED_PERCENTAGE', 'NONE');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE investment_strategy_enum AS ENUM ('CONSERVATIVE', 'BALANCED', 'AGGRESSIVE', 'CUSTOM');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create uk_pensions table
    op.create_table(
        'uk_pensions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pension_type', sa.Enum(
            'OCCUPATIONAL_DB',
            'OCCUPATIONAL_DC',
            'PERSONAL_PENSION',
            'SIPP',
            'STATE_PENSION',
            name='pension_type_enum',
            create_type=False
        ), nullable=False),
        sa.Column('provider', sa.String(255), nullable=False),
        sa.Column('scheme_reference_encrypted', sa.Text(), nullable=False),
        sa.Column('employer_name', sa.String(255), nullable=True),
        sa.Column('current_value', sa.Numeric(15, 2), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('expected_retirement_date', sa.Date(), nullable=False),
        sa.Column('investment_strategy', sa.Enum(
            'CONSERVATIVE',
            'BALANCED',
            'AGGRESSIVE',
            'CUSTOM',
            name='investment_strategy_enum',
            create_type=False
        ), nullable=True),
        sa.Column('assumed_growth_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('assumed_inflation_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('mpaa_triggered', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('mpaa_date', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum(
            'ACTIVE',
            'DEFERRED',
            'IN_PAYMENT',
            'TRANSFERRED_OUT',
            name='pension_status_enum',
            create_type=False
        ), nullable=False, server_default='ACTIVE'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint(
            'current_value IS NULL OR current_value >= 0',
            name='check_uk_pension_non_negative_value'
        ),
        sa.CheckConstraint(
            'expected_retirement_date > start_date',
            name='check_uk_pension_valid_retirement_date'
        ),
        sa.CheckConstraint(
            'assumed_growth_rate IS NULL OR assumed_growth_rate >= 0',
            name='check_uk_pension_non_negative_growth'
        ),
        sa.CheckConstraint(
            'assumed_inflation_rate IS NULL OR assumed_inflation_rate >= 0',
            name='check_uk_pension_non_negative_inflation'
        )
    )

    # Create uk_pension_contributions table
    op.create_table(
        'uk_pension_contributions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('pension_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('uk_pensions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_contribution', sa.Numeric(10, 2), nullable=True),
        sa.Column('employer_contribution', sa.Numeric(10, 2), nullable=True),
        sa.Column('personal_contribution', sa.Numeric(10, 2), nullable=True),
        sa.Column('frequency', sa.Enum(
            'MONTHLY',
            'ANNUAL',
            'ONE_OFF',
            name='contribution_frequency_enum',
            create_type=False
        ), nullable=False),
        sa.Column('tax_relief_method', sa.Enum(
            'NET_PAY',
            'RELIEF_AT_SOURCE',
            name='tax_relief_method_enum',
            create_type=False
        ), nullable=True),
        sa.Column('contribution_date', sa.Date(), nullable=False),
        sa.Column('tax_year', sa.String(7), nullable=False),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint(
            'employee_contribution IS NULL OR employee_contribution >= 0',
            name='check_contribution_non_negative_employee'
        ),
        sa.CheckConstraint(
            'employer_contribution IS NULL OR employer_contribution >= 0',
            name='check_contribution_non_negative_employer'
        ),
        sa.CheckConstraint(
            'personal_contribution IS NULL OR personal_contribution >= 0',
            name='check_contribution_non_negative_personal'
        ),
        sa.CheckConstraint(
            'effective_to IS NULL OR effective_to >= effective_from',
            name='check_contribution_valid_effective_dates'
        )
    )

    # Create uk_pension_db_details table
    op.create_table(
        'uk_pension_db_details',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('pension_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('uk_pensions.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('accrual_rate', sa.String(10), nullable=False),
        sa.Column('pensionable_service_years', sa.Numeric(5, 2), nullable=False),
        sa.Column('scheme_type', sa.Enum(
            'FINAL_SALARY',
            'CAREER_AVERAGE',
            'CASH_BALANCE',
            name='db_scheme_type_enum',
            create_type=False
        ), nullable=False),
        sa.Column('normal_retirement_age', sa.Integer(), nullable=False),
        sa.Column('guaranteed_pension_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('spouse_pension_percentage', sa.Numeric(5, 2), nullable=True),
        sa.Column('lump_sum_entitlement', sa.Numeric(10, 2), nullable=True),
        sa.Column('indexation_type', sa.Enum(
            'CPI',
            'RPI',
            'FIXED_PERCENTAGE',
            'NONE',
            name='indexation_type_enum',
            create_type=False
        ), nullable=False, server_default='CPI'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint(
            'pensionable_service_years >= 0',
            name='check_db_non_negative_service'
        ),
        sa.CheckConstraint(
            'normal_retirement_age >= 55',
            name='check_db_valid_retirement_age'
        ),
        sa.CheckConstraint(
            'guaranteed_pension_amount IS NULL OR guaranteed_pension_amount >= 0',
            name='check_db_non_negative_pension'
        ),
        sa.CheckConstraint(
            'spouse_pension_percentage IS NULL OR (spouse_pension_percentage >= 0 AND spouse_pension_percentage <= 100)',
            name='check_db_valid_spouse_percentage'
        ),
        sa.CheckConstraint(
            'lump_sum_entitlement IS NULL OR lump_sum_entitlement >= 0',
            name='check_db_non_negative_lump_sum'
        )
    )

    # Create annual_allowance_tracking table
    op.create_table(
        'annual_allowance_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tax_year', sa.String(7), nullable=False),
        sa.Column('total_contributions', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('annual_allowance_limit', sa.Numeric(10, 2), nullable=False, server_default='60000.00'),
        sa.Column('carry_forward_available', postgresql.JSONB(), nullable=True),
        sa.Column('tapered_allowance', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('adjusted_income', sa.Numeric(15, 2), nullable=True),
        sa.Column('allowance_used', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('allowance_remaining', sa.Numeric(10, 2), nullable=False, server_default='60000.00'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint(
            'total_contributions >= 0',
            name='check_aa_non_negative_contributions'
        ),
        sa.CheckConstraint(
            'annual_allowance_limit >= 0',
            name='check_aa_non_negative_limit'
        ),
        sa.CheckConstraint(
            'allowance_used >= 0',
            name='check_aa_non_negative_used'
        ),
        sa.CheckConstraint(
            'adjusted_income IS NULL OR adjusted_income >= 0',
            name='check_aa_non_negative_income'
        )
    )

    # Create state_pension_forecast table
    op.create_table(
        'state_pension_forecast',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('forecast_date', sa.Date(), nullable=False),
        sa.Column('qualifying_years', sa.Integer(), nullable=False),
        sa.Column('years_needed_for_full', sa.Integer(), nullable=False, server_default='35'),
        sa.Column('estimated_weekly_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('estimated_annual_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('state_pension_age', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint(
            'qualifying_years >= 0',
            name='check_sp_non_negative_qualifying_years'
        ),
        sa.CheckConstraint(
            'years_needed_for_full > 0',
            name='check_sp_positive_years_needed'
        ),
        sa.CheckConstraint(
            'estimated_weekly_amount >= 0',
            name='check_sp_non_negative_weekly_amount'
        ),
        sa.CheckConstraint(
            'estimated_annual_amount >= 0',
            name='check_sp_non_negative_annual_amount'
        ),
        sa.CheckConstraint(
            'state_pension_age >= 55',
            name='check_sp_valid_pension_age'
        )
    )

    # Create indexes for uk_pensions
    op.create_index('idx_uk_pension_user_id', 'uk_pensions', ['user_id'])
    op.create_index('idx_uk_pension_user_status', 'uk_pensions', ['user_id', 'status'])
    op.create_index('idx_uk_pension_user_deleted', 'uk_pensions', ['user_id', 'is_deleted'])
    op.create_index('idx_uk_pension_type', 'uk_pensions', ['pension_type'])
    op.create_index('idx_uk_pension_mpaa', 'uk_pensions', ['mpaa_triggered'])

    # Create indexes for uk_pension_contributions
    op.create_index('idx_contribution_pension_id', 'uk_pension_contributions', ['pension_id'])
    op.create_index('idx_contribution_pension_tax_year', 'uk_pension_contributions', ['pension_id', 'tax_year'])
    op.create_index('idx_contribution_effective_dates', 'uk_pension_contributions', ['pension_id', 'effective_from', 'effective_to'])
    op.create_index('idx_contribution_date', 'uk_pension_contributions', ['contribution_date'])

    # Create indexes for uk_pension_db_details
    op.create_index('idx_db_details_pension_id', 'uk_pension_db_details', ['pension_id'])

    # Create indexes for annual_allowance_tracking
    op.create_index('idx_aa_user_id', 'annual_allowance_tracking', ['user_id'])
    op.create_index('idx_aa_user_tax_year', 'annual_allowance_tracking', ['user_id', 'tax_year'], unique=True)
    op.create_index('idx_aa_tapered', 'annual_allowance_tracking', ['tapered_allowance'])

    # Create indexes for state_pension_forecast
    op.create_index('idx_sp_user_id', 'state_pension_forecast', ['user_id'])


def downgrade() -> None:
    """Drop UK pension tables and related enums."""

    # Drop indexes for state_pension_forecast
    op.drop_index('idx_sp_user_id', 'state_pension_forecast')

    # Drop indexes for annual_allowance_tracking
    op.drop_index('idx_aa_tapered', 'annual_allowance_tracking')
    op.drop_index('idx_aa_user_tax_year', 'annual_allowance_tracking')
    op.drop_index('idx_aa_user_id', 'annual_allowance_tracking')

    # Drop indexes for uk_pension_db_details
    op.drop_index('idx_db_details_pension_id', 'uk_pension_db_details')

    # Drop indexes for uk_pension_contributions
    op.drop_index('idx_contribution_date', 'uk_pension_contributions')
    op.drop_index('idx_contribution_effective_dates', 'uk_pension_contributions')
    op.drop_index('idx_contribution_pension_tax_year', 'uk_pension_contributions')
    op.drop_index('idx_contribution_pension_id', 'uk_pension_contributions')

    # Drop indexes for uk_pensions
    op.drop_index('idx_uk_pension_mpaa', 'uk_pensions')
    op.drop_index('idx_uk_pension_type', 'uk_pensions')
    op.drop_index('idx_uk_pension_user_deleted', 'uk_pensions')
    op.drop_index('idx_uk_pension_user_status', 'uk_pensions')
    op.drop_index('idx_uk_pension_user_id', 'uk_pensions')

    # Drop tables
    op.drop_table('state_pension_forecast')
    op.drop_table('annual_allowance_tracking')
    op.drop_table('uk_pension_db_details')
    op.drop_table('uk_pension_contributions')
    op.drop_table('uk_pensions')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS investment_strategy_enum")
    op.execute("DROP TYPE IF EXISTS indexation_type_enum")
    op.execute("DROP TYPE IF EXISTS db_scheme_type_enum")
    op.execute("DROP TYPE IF EXISTS tax_relief_method_enum")
    op.execute("DROP TYPE IF EXISTS contribution_frequency_enum")
    op.execute("DROP TYPE IF EXISTS pension_status_enum")
    op.execute("DROP TYPE IF EXISTS pension_type_enum")
