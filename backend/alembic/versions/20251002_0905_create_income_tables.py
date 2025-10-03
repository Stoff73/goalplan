"""create_income_tables

Revision ID: d8e9f0a1b2c3
Revises: b70b0678b4fd
Create Date: 2025-10-02 09:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd8e9f0a1b2c3'
down_revision = 'b70b0678b4fd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create income tracking tables:
    - exchange_rates: Currency conversion rates
    - user_income: Multi-currency income records
    - income_tax_withholding: PAYE/PASE tax withholding details
    """

    # Create ENUM types
    op.execute("CREATE TYPE income_type_enum AS ENUM ('employment', 'self_employment', 'rental', 'investment', 'pension', 'other')")
    op.execute("CREATE TYPE currency_enum AS ENUM ('GBP', 'ZAR', 'USD', 'EUR')")
    op.execute("CREATE TYPE income_frequency_enum AS ENUM ('annual', 'monthly', 'weekly', 'one_time')")

    # Create exchange_rates table
    op.create_table(
        'exchange_rates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('from_currency', sa.String(3), nullable=False),
        sa.Column('to_currency', sa.String(3), nullable=False),
        sa.Column('rate', sa.Numeric(10, 6), nullable=False),
        sa.Column('rate_date', sa.Date(), nullable=False),
        sa.Column('source', sa.String(50), nullable=False, server_default='exchangerate-api'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('from_currency', 'to_currency', 'rate_date', name='unique_rate_per_day'),
    )

    # Create indexes for exchange_rates
    op.create_index(
        'idx_exchange_rates_currencies_date',
        'exchange_rates',
        ['from_currency', 'to_currency', 'rate_date']
    )

    # Create user_income table
    op.create_table(
        'user_income',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),

        # Income details
        sa.Column('income_type', postgresql.ENUM('employment', 'self_employment', 'rental', 'investment', 'pension', 'other', name='income_type_enum', create_type=False), nullable=False),
        sa.Column('source_country', sa.String(2), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('employer_name', sa.String(255), nullable=True),

        # Amount and currency
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', postgresql.ENUM('GBP', 'ZAR', 'USD', 'EUR', name='currency_enum', create_type=False), nullable=False),
        sa.Column('amount_in_gbp', sa.Numeric(15, 2), nullable=True),
        sa.Column('amount_in_zar', sa.Numeric(15, 2), nullable=True),
        sa.Column('exchange_rate', sa.Numeric(10, 6), nullable=True),
        sa.Column('exchange_rate_date', sa.Date(), nullable=True),

        # Frequency and tax year
        sa.Column('frequency', postgresql.ENUM('annual', 'monthly', 'weekly', 'one_time', name='income_frequency_enum', create_type=False), nullable=False),
        sa.Column('tax_year_uk', sa.String(10), nullable=True),
        sa.Column('tax_year_sa', sa.String(10), nullable=True),
        sa.Column('income_date', sa.Date(), nullable=False),

        # Gross/net and tax withholding
        sa.Column('is_gross', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('tax_withheld_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('tax_withheld_currency', postgresql.ENUM('GBP', 'ZAR', 'USD', 'EUR', name='currency_enum', create_type=False), nullable=True),

        # Foreign income details
        sa.Column('is_foreign_income', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('foreign_tax_credit', sa.Numeric(15, 2), nullable=True),
        sa.Column('dta_applicable', sa.Boolean(), nullable=False, server_default=sa.text('false')),

        # Metadata
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),

        sa.CheckConstraint('amount > 0', name='check_positive_amount'),
    )

    # Create indexes for user_income
    op.create_index(
        'idx_income_user_active',
        'user_income',
        ['user_id', 'deleted_at'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )
    op.create_index('idx_income_tax_year_uk', 'user_income', ['user_id', 'tax_year_uk'])
    op.create_index('idx_income_tax_year_sa', 'user_income', ['user_id', 'tax_year_sa'])
    op.create_index('idx_income_date', 'user_income', ['user_id', 'income_date'])
    op.create_index('idx_income_type', 'user_income', ['user_id', 'income_type'])

    # Create income_tax_withholding table
    op.create_table(
        'income_tax_withholding',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('income_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_income.id', ondelete='CASCADE'), nullable=False, unique=True, index=True),

        # UK PAYE details
        sa.Column('paye_income_tax', sa.Numeric(15, 2), nullable=True),
        sa.Column('paye_ni_class1', sa.Numeric(15, 2), nullable=True),
        sa.Column('paye_tax_code', sa.String(20), nullable=True),

        # SA PASE details
        sa.Column('pase_income_tax', sa.Numeric(15, 2), nullable=True),
        sa.Column('pase_uif', sa.Numeric(15, 2), nullable=True),

        # Employer contributions
        sa.Column('employer_ni', sa.Numeric(15, 2), nullable=True),
        sa.Column('employer_uif', sa.Numeric(15, 2), nullable=True),

        # Metadata
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    """Drop income tracking tables."""

    # Drop tables in reverse order
    op.drop_table('income_tax_withholding')
    op.drop_table('user_income')
    op.drop_table('exchange_rates')

    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS income_frequency_enum')
    op.execute('DROP TYPE IF EXISTS currency_enum')
    op.execute('DROP TYPE IF EXISTS income_type_enum')
