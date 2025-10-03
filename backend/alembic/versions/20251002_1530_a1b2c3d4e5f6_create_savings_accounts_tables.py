"""create_savings_accounts_tables

Revision ID: a1b2c3d4e5f6
Revises: e9f0a1b2c3d4
Create Date: 2025-10-02 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'e9f0a1b2c3d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""

    # Define ENUM types (will be created automatically with table)
    savings_account_type_enum = postgresql.ENUM(
        'CURRENT', 'SAVINGS', 'ISA', 'TFSA', 'FIXED_DEPOSIT',
        'MONEY_MARKET', 'NOTICE_ACCOUNT', 'OTHER',
        name='savings_account_type_enum',
        create_type=True
    )

    savings_account_purpose_enum = postgresql.ENUM(
        'EMERGENCY_FUND', 'SAVINGS_GOAL', 'GENERAL', 'OTHER',
        name='savings_account_purpose_enum',
        create_type=True
    )

    savings_account_country_enum = postgresql.ENUM(
        'UK', 'SA', 'OFFSHORE',
        name='savings_account_country_enum',
        create_type=True
    )

    savings_interest_frequency_enum = postgresql.ENUM(
        'MONTHLY', 'QUARTERLY', 'ANNUALLY', 'MATURITY',
        name='savings_interest_frequency_enum',
        create_type=True
    )

    # Create savings_accounts table
    op.create_table(
        'savings_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Account Details
        sa.Column('bank_name', sa.String(length=255), nullable=False),
        sa.Column('account_name', sa.String(length=255), nullable=False),
        sa.Column('account_number_encrypted', sa.Text(), nullable=False),
        sa.Column('account_type', savings_account_type_enum, nullable=False),
        sa.Column('currency', postgresql.ENUM(
            'GBP', 'ZAR', 'USD', 'EUR',
            name='currency_enum',
            create_type=False  # Reuse existing enum from income tables
        ), nullable=False),

        # Balance Information
        sa.Column('current_balance', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),

        # Interest Details
        sa.Column('interest_rate', sa.Numeric(precision=5, scale=2), nullable=True, server_default='0.00'),
        sa.Column('interest_payment_frequency', savings_interest_frequency_enum, nullable=True),

        # Tax-Advantaged Account Flags
        sa.Column('is_isa', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_tfsa', sa.Boolean(), nullable=False, server_default='false'),

        # Account Purpose and Location
        sa.Column('purpose', savings_account_purpose_enum, nullable=True),
        sa.Column('country', savings_account_country_enum, nullable=False),

        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),

        # Foreign key
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),

        # Constraints
        sa.CheckConstraint('current_balance >= 0', name='check_positive_balance'),
        sa.CheckConstraint('interest_rate >= 0', name='check_positive_interest_rate'),
        sa.CheckConstraint(
            'NOT (is_isa = true AND is_tfsa = true)',
            name='check_isa_tfsa_mutually_exclusive'
        ),
    )

    # Create indexes for savings_accounts
    op.create_index(
        'idx_savings_account_user_id',
        'savings_accounts',
        ['user_id'],
        unique=False
    )

    op.create_index(
        'idx_savings_account_type',
        'savings_accounts',
        ['account_type'],
        unique=False
    )

    op.create_index(
        'idx_savings_user_active',
        'savings_accounts',
        ['user_id', 'is_active'],
        unique=False
    )

    op.create_index(
        'idx_savings_user_deleted',
        'savings_accounts',
        ['user_id', 'deleted_at'],
        unique=False
    )

    op.create_index(
        'idx_savings_isa',
        'savings_accounts',
        ['is_isa'],
        unique=False,
        postgresql_where=sa.text('is_isa = true')
    )

    op.create_index(
        'idx_savings_tfsa',
        'savings_accounts',
        ['is_tfsa'],
        unique=False,
        postgresql_where=sa.text('is_tfsa = true')
    )

    # Create account_balance_history table
    op.create_table(
        'account_balance_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('savings_account_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Balance Information
        sa.Column('balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('balance_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),

        # Timestamp
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Foreign key
        sa.ForeignKeyConstraint(['savings_account_id'], ['savings_accounts.id'], ondelete='CASCADE'),

        # Constraints
        sa.CheckConstraint('balance >= 0', name='check_positive_balance_history'),
        sa.UniqueConstraint(
            'savings_account_id',
            'balance_date',
            name='unique_balance_per_account_per_day'
        ),
    )

    # Create indexes for account_balance_history
    op.create_index(
        'idx_balance_history_account_id',
        'account_balance_history',
        ['savings_account_id'],
        unique=False
    )

    op.create_index(
        'idx_balance_history_account_date',
        'account_balance_history',
        ['savings_account_id', sa.text('balance_date DESC')],
        unique=False
    )


def downgrade() -> None:
    """Downgrade database schema."""

    # Drop indexes for account_balance_history
    op.drop_index('idx_balance_history_account_date', table_name='account_balance_history')
    op.drop_index('idx_balance_history_account_id', table_name='account_balance_history')

    # Drop account_balance_history table
    op.drop_table('account_balance_history')

    # Drop indexes for savings_accounts
    op.drop_index('idx_savings_tfsa', table_name='savings_accounts')
    op.drop_index('idx_savings_isa', table_name='savings_accounts')
    op.drop_index('idx_savings_user_deleted', table_name='savings_accounts')
    op.drop_index('idx_savings_user_active', table_name='savings_accounts')
    op.drop_index('idx_savings_account_type', table_name='savings_accounts')
    op.drop_index('idx_savings_account_user_id', table_name='savings_accounts')

    # Drop savings_accounts table
    op.drop_table('savings_accounts')

    # Drop ENUM types (in reverse order of creation)
    savings_interest_frequency_enum = postgresql.ENUM(
        'MONTHLY', 'QUARTERLY', 'ANNUALLY', 'MATURITY',
        name='savings_interest_frequency_enum'
    )
    savings_interest_frequency_enum.drop(op.get_bind(), checkfirst=True)

    savings_account_country_enum = postgresql.ENUM(
        'UK', 'SA', 'OFFSHORE',
        name='savings_account_country_enum'
    )
    savings_account_country_enum.drop(op.get_bind(), checkfirst=True)

    savings_account_purpose_enum = postgresql.ENUM(
        'EMERGENCY_FUND', 'SAVINGS_GOAL', 'GENERAL', 'OTHER',
        name='savings_account_purpose_enum'
    )
    savings_account_purpose_enum.drop(op.get_bind(), checkfirst=True)

    savings_account_type_enum = postgresql.ENUM(
        'CURRENT', 'SAVINGS', 'ISA', 'TFSA', 'FIXED_DEPOSIT',
        'MONEY_MARKET', 'NOTICE_ACCOUNT', 'OTHER',
        name='savings_account_type_enum'
    )
    savings_account_type_enum.drop(op.get_bind(), checkfirst=True)
