"""add_investment_tables

Revision ID: d5e6f7g8h9i0
Revises: b3c4d5e6f7g8
Create Date: 2025-10-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd5e6f7g8h9i0'
down_revision = 'b3c4d5e6f7g8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""

    # Define ENUM types
    account_type_enum = postgresql.ENUM(
        'STOCKS_ISA', 'GIA', 'VCT', 'EIS', 'SEIS',
        'SA_UNIT_TRUST', 'SA_ETF', 'SA_DIRECT_SHARES', 'OFFSHORE_BOND',
        name='account_type_enum',
        create_type=True
    )

    account_country_enum = postgresql.ENUM(
        'UK', 'SA', 'OFFSHORE',
        name='account_country_enum',
        create_type=True
    )

    account_status_enum = postgresql.ENUM(
        'ACTIVE', 'CLOSED',
        name='account_status_enum',
        create_type=True
    )

    security_type_enum = postgresql.ENUM(
        'STOCK', 'FUND', 'ETF', 'BOND', 'VCT', 'EIS_SHARE', 'SEIS_SHARE',
        name='security_type_enum',
        create_type=True
    )

    asset_class_enum = postgresql.ENUM(
        'EQUITY', 'FIXED_INCOME', 'PROPERTY', 'COMMODITY', 'CASH', 'ALTERNATIVE',
        name='asset_class_enum',
        create_type=True
    )

    region_enum = postgresql.ENUM(
        'UK', 'US', 'EUROPE', 'ASIA', 'EMERGING', 'GLOBAL',
        name='region_enum',
        create_type=True
    )

    disposal_method_enum = postgresql.ENUM(
        'FIFO', 'AVERAGE_COST', 'SPECIFIC_IDENTIFICATION',
        name='disposal_method_enum',
        create_type=True
    )

    source_country_enum = postgresql.ENUM(
        'UK', 'SA', 'US', 'OTHER',
        name='source_country_enum',
        create_type=True
    )

    # Create investment_accounts table
    op.create_table(
        'investment_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Account Details
        sa.Column('account_type', account_type_enum, nullable=False),
        sa.Column('provider', sa.String(length=255), nullable=False),
        sa.Column('account_number_encrypted', sa.Text(), nullable=False),
        sa.Column('account_number_last_4', sa.String(length=4), nullable=True),
        sa.Column('country', account_country_enum, nullable=False),
        sa.Column('base_currency', sa.String(length=3), nullable=False),
        sa.Column('account_open_date', sa.Date(), nullable=True),

        # Status
        sa.Column('status', account_status_enum, nullable=False, server_default='ACTIVE'),
        sa.Column('deleted', sa.Boolean(), nullable=False, server_default='false'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),

        # Foreign Keys
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create investment_holdings table
    op.create_table(
        'investment_holdings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Security Details
        sa.Column('security_type', security_type_enum, nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=True),
        sa.Column('isin', sa.String(length=12), nullable=True),
        sa.Column('security_name', sa.String(length=255), nullable=False),

        # Quantity and Pricing
        sa.Column('quantity', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('purchase_date', sa.Date(), nullable=False),
        sa.Column('purchase_price', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('purchase_currency', sa.String(length=3), nullable=False),
        sa.Column('current_price', sa.Numeric(precision=15, scale=4), nullable=False),

        # Asset Classification
        sa.Column('asset_class', asset_class_enum, nullable=False),
        sa.Column('region', region_enum, nullable=False),
        sa.Column('sector', sa.String(length=100), nullable=True),

        # Price Update Tracking
        sa.Column('last_price_update', sa.DateTime(), nullable=True),

        # Soft Delete
        sa.Column('deleted', sa.Boolean(), nullable=False, server_default='false'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),

        # Foreign Keys
        sa.ForeignKeyConstraint(['account_id'], ['investment_accounts.id'], ondelete='CASCADE'),

        # Check Constraints
        sa.CheckConstraint('quantity > 0', name='check_positive_quantity'),
        sa.CheckConstraint('purchase_price >= 0', name='check_non_negative_purchase_price'),
        sa.CheckConstraint('current_price >= 0', name='check_non_negative_current_price'),
    )

    # Create tax_lots table
    op.create_table(
        'tax_lots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('holding_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Purchase Details
        sa.Column('purchase_date', sa.Date(), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('purchase_price', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('purchase_currency', sa.String(length=3), nullable=False),

        # Cost Basis
        sa.Column('cost_basis_gbp', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('cost_basis_zar', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('exchange_rate', sa.Numeric(precision=10, scale=6), nullable=False),

        # Disposal Details
        sa.Column('disposal_date', sa.Date(), nullable=True),
        sa.Column('disposal_quantity', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('disposal_proceeds', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('realized_gain', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('cgt_tax_year', sa.String(length=10), nullable=True),
        sa.Column('disposal_method', disposal_method_enum, nullable=True),

        # Timestamp
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),

        # Foreign Keys
        sa.ForeignKeyConstraint(['holding_id'], ['investment_holdings.id'], ondelete='CASCADE'),

        # Check Constraints
        sa.CheckConstraint('quantity > 0', name='check_tax_lot_positive_quantity'),
        sa.CheckConstraint('purchase_price >= 0', name='check_tax_lot_non_negative_purchase_price'),
        sa.CheckConstraint('cost_basis_gbp >= 0', name='check_tax_lot_non_negative_cost_basis_gbp'),
        sa.CheckConstraint('cost_basis_zar >= 0', name='check_tax_lot_non_negative_cost_basis_zar'),
        sa.CheckConstraint('disposal_quantity IS NULL OR disposal_quantity > 0', name='check_tax_lot_positive_disposal_quantity'),
        sa.CheckConstraint('disposal_proceeds IS NULL OR disposal_proceeds >= 0', name='check_tax_lot_non_negative_disposal_proceeds'),
    )

    # Create dividend_income table
    op.create_table(
        'dividend_income',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('holding_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Dividend Details
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('ex_dividend_date', sa.Date(), nullable=True),
        sa.Column('dividend_per_share', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('total_dividend_gross', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('withholding_tax', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('total_dividend_net', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),

        # Source Country
        sa.Column('source_country', source_country_enum, nullable=False),

        # Tax Year Allocation
        sa.Column('uk_tax_year', sa.String(length=7), nullable=True),
        sa.Column('sa_tax_year', sa.String(length=9), nullable=True),

        # Timestamp
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),

        # Foreign Keys
        sa.ForeignKeyConstraint(['holding_id'], ['investment_holdings.id'], ondelete='CASCADE'),

        # Check Constraints
        sa.CheckConstraint('dividend_per_share >= 0', name='check_dividend_non_negative_dividend_per_share'),
        sa.CheckConstraint('total_dividend_gross >= 0', name='check_dividend_non_negative_total_gross'),
        sa.CheckConstraint('withholding_tax >= 0', name='check_dividend_non_negative_withholding_tax'),
        sa.CheckConstraint('total_dividend_net >= 0', name='check_dividend_non_negative_total_net'),
    )

    # Create capital_gains_realized table
    op.create_table(
        'capital_gains_realized',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('holding_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Disposal Details
        sa.Column('disposal_date', sa.Date(), nullable=False),
        sa.Column('quantity_sold', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('sale_price', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('sale_value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('cost_basis', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('gain_loss', sa.Numeric(precision=15, scale=2), nullable=False),

        # Tax Details
        sa.Column('tax_year', sa.String(length=10), nullable=False),
        sa.Column('country', account_country_enum, nullable=False),

        # Timestamp
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),

        # Foreign Keys
        sa.ForeignKeyConstraint(['holding_id'], ['investment_holdings.id'], ondelete='CASCADE'),

        # Check Constraints
        sa.CheckConstraint('quantity_sold > 0', name='check_cg_positive_quantity_sold'),
        sa.CheckConstraint('sale_price >= 0', name='check_cg_non_negative_sale_price'),
        sa.CheckConstraint('sale_value >= 0', name='check_cg_non_negative_sale_value'),
        sa.CheckConstraint('cost_basis >= 0', name='check_cg_non_negative_cost_basis'),
    )

    # Create indexes for investment_accounts
    op.create_index('idx_investment_account_user_deleted', 'investment_accounts', ['user_id', 'deleted'])
    op.create_index('idx_investment_account_user_status', 'investment_accounts', ['user_id', 'status'])
    op.create_index('idx_investment_account_status', 'investment_accounts', ['status'])
    op.create_index('idx_investment_account_country', 'investment_accounts', ['country'])

    # Create indexes for investment_holdings
    op.create_index('idx_investment_holding_account_deleted', 'investment_holdings', ['account_id', 'deleted'])
    op.create_index('idx_investment_holding_ticker', 'investment_holdings', ['ticker'])
    op.create_index('idx_investment_holding_security_type', 'investment_holdings', ['security_type'])
    op.create_index('idx_investment_holding_asset_class', 'investment_holdings', ['asset_class'])

    # Create indexes for tax_lots
    op.create_index('idx_tax_lot_holding_disposal', 'tax_lots', ['holding_id', 'disposal_date'])

    # Create indexes for dividend_income
    op.create_index('idx_dividend_holding_payment_date', 'dividend_income', ['holding_id', 'payment_date'])

    # Create indexes for capital_gains_realized
    op.create_index('idx_capital_gain_holding_tax_year', 'capital_gains_realized', ['holding_id', 'tax_year'])


def downgrade() -> None:
    """Downgrade database schema."""

    # Drop indexes
    op.drop_index('idx_capital_gain_holding_tax_year', table_name='capital_gains_realized')
    op.drop_index('idx_dividend_holding_payment_date', table_name='dividend_income')
    op.drop_index('idx_tax_lot_holding_disposal', table_name='tax_lots')
    op.drop_index('idx_investment_holding_asset_class', table_name='investment_holdings')
    op.drop_index('idx_investment_holding_security_type', table_name='investment_holdings')
    op.drop_index('idx_investment_holding_ticker', table_name='investment_holdings')
    op.drop_index('idx_investment_holding_account_deleted', table_name='investment_holdings')
    op.drop_index('idx_investment_account_country', table_name='investment_accounts')
    op.drop_index('idx_investment_account_status', table_name='investment_accounts')
    op.drop_index('idx_investment_account_user_status', table_name='investment_accounts')
    op.drop_index('idx_investment_account_user_deleted', table_name='investment_accounts')

    # Drop tables
    op.drop_table('capital_gains_realized')
    op.drop_table('dividend_income')
    op.drop_table('tax_lots')
    op.drop_table('investment_holdings')
    op.drop_table('investment_accounts')

    # Drop ENUM types
    sa.Enum(name='source_country_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='disposal_method_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='region_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='asset_class_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='security_type_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='account_status_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='account_country_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='account_type_enum').drop(op.get_bind(), checkfirst=True)
