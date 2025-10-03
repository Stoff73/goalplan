"""create_tax_status_tables

Revision ID: a6157b39183b
Revises: c4d5e6f7g8h9
Create Date: 2025-10-02 08:33:46.490331

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a6157b39183b'
down_revision = 'c4d5e6f7g8h9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""

    # Create UK domicile status enum
    uk_domicile_status_enum = postgresql.ENUM(
        'uk_domicile', 'non_uk_domicile', 'deemed_domicile',
        name='ukdomicilestatus',
        create_type=False
    )
    uk_domicile_status_enum.create(op.get_bind(), checkfirst=True)

    # Create user_tax_status table
    op.create_table(
        'user_tax_status',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),

        # UK tax status
        sa.Column('uk_tax_resident', sa.Boolean(), nullable=False),
        sa.Column('uk_domicile', uk_domicile_status_enum, nullable=True),
        sa.Column('uk_deemed_domicile_date', sa.Date(), nullable=True),
        sa.Column('uk_split_year_treatment', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('uk_remittance_basis', sa.Boolean(), nullable=False, server_default='false'),

        # SA tax status
        sa.Column('sa_tax_resident', sa.Boolean(), nullable=False),
        sa.Column('sa_ordinarily_resident', sa.Boolean(), nullable=False, server_default='false'),

        # Dual residency
        sa.Column('dual_resident', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('dta_tie_breaker_country', sa.String(length=2), nullable=True),

        # Audit fields
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Foreign key
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),

        # Constraints
        sa.CheckConstraint(
            'effective_to IS NULL OR effective_to > effective_from',
            name='valid_effective_dates'
        ),
        sa.UniqueConstraint('user_id', 'effective_from', name='no_overlapping_periods'),
    )

    # Create indexes for user_tax_status
    op.create_index(
        'idx_tax_status_user_current',
        'user_tax_status',
        ['user_id', 'effective_to'],
        unique=False,
        postgresql_where=sa.text('effective_to IS NULL')
    )
    op.create_index(
        'idx_tax_status_user_dates',
        'user_tax_status',
        ['user_id', 'effective_from', 'effective_to'],
        unique=False
    )

    # Create uk_srt_data table
    op.create_table(
        'uk_srt_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tax_year', sa.String(length=10), nullable=False),

        # Days in UK
        sa.Column('days_in_uk', sa.Integer(), nullable=False),

        # Five UK ties
        sa.Column('family_tie', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('accommodation_tie', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('work_tie', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('ninety_day_tie', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('country_tie', sa.Boolean(), nullable=False, server_default='false'),

        # Calculated result
        sa.Column('tax_resident', sa.Boolean(), nullable=True),
        sa.Column('test_result', sa.String(length=50), nullable=True),

        # Audit fields
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Foreign key
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),

        # Constraints
        sa.UniqueConstraint('user_id', 'tax_year', name='unique_srt_per_user_year'),
    )

    # Create indexes for uk_srt_data
    op.create_index('idx_srt_user_year', 'uk_srt_data', ['user_id', 'tax_year'], unique=False)

    # Create sa_presence_data table
    op.create_table(
        'sa_presence_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tax_year', sa.String(length=10), nullable=False),

        # Days in SA
        sa.Column('days_in_sa', sa.Integer(), nullable=False),

        # 5-year tracking
        sa.Column('year_minus_1_days', sa.Integer(), nullable=True),
        sa.Column('year_minus_2_days', sa.Integer(), nullable=True),
        sa.Column('year_minus_3_days', sa.Integer(), nullable=True),
        sa.Column('year_minus_4_days', sa.Integer(), nullable=True),

        # Calculated result
        sa.Column('tax_resident', sa.Boolean(), nullable=True),
        sa.Column('ordinarily_resident', sa.Boolean(), nullable=True),
        sa.Column('test_result', sa.String(length=50), nullable=True),
        sa.Column('five_year_average', sa.Numeric(precision=5, scale=2), nullable=True),

        # Audit fields
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Foreign key
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),

        # Constraints
        sa.UniqueConstraint('user_id', 'tax_year', name='unique_sa_presence_per_user_year'),
    )

    # Create indexes for sa_presence_data
    op.create_index('idx_sa_presence_user_year', 'sa_presence_data', ['user_id', 'tax_year'], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""

    # Drop tables (in reverse order)
    op.drop_table('sa_presence_data')
    op.drop_table('uk_srt_data')
    op.drop_table('user_tax_status')

    # Drop enum
    uk_domicile_status_enum = postgresql.ENUM(
        'uk_domicile', 'non_uk_domicile', 'deemed_domicile',
        name='ukdomicilestatus'
    )
    uk_domicile_status_enum.drop(op.get_bind(), checkfirst=True)
