"""create estate iht tables

Revision ID: i0j1k2l3m4n5
Revises: h9i0j1k2l3m4
Create Date: 2025-10-03 22:00:00.000000

Creates tables for Estate Valuation and IHT Planning Module:
- estate_assets: Estate asset tracking with temporal data
- estate_liabilities: Estate liability tracking with temporal data
- iht_calculations: UK IHT calculation tracking
- sa_estate_duty_calculations: SA Estate Duty calculation tracking

Includes:
- Enums: asset_type_enum, liability_type_enum
- Constraints: Non-negative values, valid date ranges
- Indexes: For user queries and date lookups
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'i0j1k2l3m4n5'
down_revision = 'h9i0j1k2l3m4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create estate IHT tables."""

    # Create enums (drop if exist first to ensure clean state)
    op.execute("DROP TYPE IF EXISTS asset_type_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS liability_type_enum CASCADE")

    op.execute("""
        CREATE TYPE asset_type_enum AS ENUM (
            'PROPERTY',
            'INVESTMENTS',
            'PENSIONS',
            'LIFE_ASSURANCE',
            'BUSINESS',
            'OTHER'
        )
    """)

    op.execute("""
        CREATE TYPE liability_type_enum AS ENUM (
            'MORTGAGE',
            'LOAN',
            'CREDIT_CARD',
            'OTHER'
        )
    """)

    # Create estate_assets table
    op.create_table(
        'estate_assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_type', sa.Enum(
            'PROPERTY', 'INVESTMENTS', 'PENSIONS', 'LIFE_ASSURANCE', 'BUSINESS', 'OTHER',
            name='asset_type_enum', create_type=False
        ), nullable=False),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('estimated_value', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='GBP'),
        sa.Column('owned_individually', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('joint_ownership', sa.String(255), nullable=True),
        sa.Column('included_in_uk_estate', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('included_in_sa_estate', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('estimated_value >= 0', name='check_estate_asset_non_negative_value'),
        sa.CheckConstraint(
            'effective_to IS NULL OR effective_to >= effective_from',
            name='check_estate_asset_valid_effective_dates'
        )
    )

    # Create indexes for estate_assets
    op.create_index('idx_estate_asset_user_id', 'estate_assets', ['user_id'])
    op.create_index('idx_estate_asset_user_type', 'estate_assets', ['user_id', 'asset_type'])
    op.create_index('idx_estate_asset_user_deleted', 'estate_assets', ['user_id', 'is_deleted'])
    op.create_index('idx_estate_asset_effective_dates', 'estate_assets', ['user_id', 'effective_from', 'effective_to'])
    op.create_index('idx_estate_asset_type', 'estate_assets', ['asset_type'])

    # Create estate_liabilities table
    op.create_table(
        'estate_liabilities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('liability_type', sa.Enum(
            'MORTGAGE', 'LOAN', 'CREDIT_CARD', 'OTHER',
            name='liability_type_enum', create_type=False
        ), nullable=False),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('amount_outstanding', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='GBP'),
        sa.Column('deductible_from_estate', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('amount_outstanding >= 0', name='check_estate_liability_non_negative_amount'),
        sa.CheckConstraint(
            'effective_to IS NULL OR effective_to >= effective_from',
            name='check_estate_liability_valid_effective_dates'
        )
    )

    # Create indexes for estate_liabilities
    op.create_index('idx_estate_liability_user_id', 'estate_liabilities', ['user_id'])
    op.create_index('idx_estate_liability_user_type', 'estate_liabilities', ['user_id', 'liability_type'])
    op.create_index('idx_estate_liability_user_deleted', 'estate_liabilities', ['user_id', 'is_deleted'])
    op.create_index('idx_estate_liability_effective_dates', 'estate_liabilities', ['user_id', 'effective_from', 'effective_to'])
    op.create_index('idx_estate_liability_type', 'estate_liabilities', ['liability_type'])

    # Create iht_calculations table
    op.create_table(
        'iht_calculations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('calculation_date', sa.Date(), nullable=False),
        sa.Column('tax_year', sa.String(7), nullable=False),
        sa.Column('gross_estate_value', sa.Numeric(15, 2), nullable=False),
        sa.Column('net_estate_value', sa.Numeric(15, 2), nullable=False),
        sa.Column('nil_rate_band', sa.Numeric(15, 2), nullable=False, server_default='325000.00'),
        sa.Column('residence_nil_rate_band', sa.Numeric(15, 2), nullable=False, server_default='0.00'),
        sa.Column('transferable_nil_rate_band', sa.Numeric(15, 2), nullable=False, server_default='0.00'),
        sa.Column('total_nil_rate_band_available', sa.Numeric(15, 2), nullable=False),
        sa.Column('taxable_estate', sa.Numeric(15, 2), nullable=False),
        sa.Column('iht_owed', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='GBP'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('gross_estate_value >= 0', name='check_iht_non_negative_gross_estate'),
        sa.CheckConstraint('net_estate_value >= 0', name='check_iht_non_negative_net_estate'),
        sa.CheckConstraint('nil_rate_band >= 0', name='check_iht_non_negative_nrb'),
        sa.CheckConstraint('residence_nil_rate_band >= 0', name='check_iht_non_negative_rnrb'),
        sa.CheckConstraint('transferable_nil_rate_band >= 0', name='check_iht_non_negative_transferable_nrb'),
        sa.CheckConstraint('total_nil_rate_band_available >= 0', name='check_iht_non_negative_total_nrb'),
        sa.CheckConstraint('taxable_estate >= 0', name='check_iht_non_negative_taxable_estate'),
        sa.CheckConstraint('iht_owed >= 0', name='check_iht_non_negative_iht_owed')
    )

    # Create indexes for iht_calculations
    op.create_index('idx_iht_calculation_user_id', 'iht_calculations', ['user_id'])
    op.create_index('idx_iht_calculation_date', 'iht_calculations', ['user_id', 'calculation_date'])
    op.create_index('idx_iht_calculation_tax_year', 'iht_calculations', ['user_id', 'tax_year'])
    op.create_index('idx_iht_calculation_created', 'iht_calculations', ['created_at'])

    # Create sa_estate_duty_calculations table
    op.create_table(
        'sa_estate_duty_calculations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('calculation_date', sa.Date(), nullable=False),
        sa.Column('estate_value', sa.Numeric(15, 2), nullable=False),
        sa.Column('abatement', sa.Numeric(15, 2), nullable=False, server_default='3500000.00'),
        sa.Column('dutiable_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('estate_duty_rate', sa.Numeric(5, 2), nullable=False, server_default='20.00'),
        sa.Column('estate_duty_owed', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='ZAR'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('estate_value >= 0', name='check_sa_estate_duty_non_negative_estate_value'),
        sa.CheckConstraint('abatement >= 0', name='check_sa_estate_duty_non_negative_abatement'),
        sa.CheckConstraint('dutiable_amount >= 0', name='check_sa_estate_duty_non_negative_dutiable_amount'),
        sa.CheckConstraint(
            'estate_duty_rate >= 0 AND estate_duty_rate <= 100',
            name='check_sa_estate_duty_valid_rate'
        ),
        sa.CheckConstraint('estate_duty_owed >= 0', name='check_sa_estate_duty_non_negative_owed')
    )

    # Create indexes for sa_estate_duty_calculations
    op.create_index('idx_sa_estate_duty_user_id', 'sa_estate_duty_calculations', ['user_id'])
    op.create_index('idx_sa_estate_duty_date', 'sa_estate_duty_calculations', ['user_id', 'calculation_date'])
    op.create_index('idx_sa_estate_duty_created', 'sa_estate_duty_calculations', ['created_at'])


def downgrade() -> None:
    """Drop estate IHT tables."""

    # Drop tables
    op.drop_table('sa_estate_duty_calculations')
    op.drop_table('iht_calculations')
    op.drop_table('estate_liabilities')
    op.drop_table('estate_assets')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS liability_type_enum CASCADE')
    op.execute('DROP TYPE IF EXISTS asset_type_enum CASCADE')
