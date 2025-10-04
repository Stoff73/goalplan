"""Add gift and PET tracking tables

Revision ID: j1k2l3m4n5o6
Revises: i0j1k2l3m4n5
Create Date: 2025-10-03 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'j1k2l3m4n5o6'
down_revision = 'i0j1k2l3m4n5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create gifts and iht_exemptions tables."""

    # Create GiftType enum
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE gift_type_enum AS ENUM ('PET', 'EXEMPT', 'CHARGEABLE');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # Create ExemptionType enum
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE exemption_type_enum AS ENUM (
                'ANNUAL_EXEMPTION',
                'SMALL_GIFTS',
                'NORMAL_EXPENDITURE',
                'WEDDING',
                'CHARITY',
                'SPOUSE'
            );
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # Create gifts table
    op.create_table(
        'gifts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recipient', sa.String(length=255), nullable=False),
        sa.Column('gift_date', sa.Date(), nullable=False),
        sa.Column('gift_value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='GBP'),
        sa.Column('gift_type', sa.Enum('PET', 'EXEMPT', 'CHARGEABLE', name='gift_type_enum'), nullable=False),
        sa.Column('exemption_type', sa.Enum(
            'ANNUAL_EXEMPTION', 'SMALL_GIFTS', 'NORMAL_EXPENDITURE',
            'WEDDING', 'CHARITY', 'SPOUSE',
            name='exemption_type_enum'
        ), nullable=True),
        sa.Column('becomes_exempt_date', sa.Date(), nullable=True),
        sa.Column('still_in_pet_period', sa.Boolean(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('gift_value >= 0', name='check_gift_non_negative_value')
    )

    # Create indexes for gifts table
    op.create_index('idx_gift_user_id', 'gifts', ['user_id'])
    op.create_index('idx_gift_user_date', 'gifts', ['user_id', 'gift_date'])
    op.create_index('idx_gift_user_deleted', 'gifts', ['user_id', 'is_deleted'])
    op.create_index('idx_gift_type', 'gifts', ['gift_type'])
    op.create_index('idx_gift_becomes_exempt_date', 'gifts', ['becomes_exempt_date'])

    # Create iht_exemptions table
    op.create_table(
        'iht_exemptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tax_year', sa.String(length=7), nullable=False),
        sa.Column('annual_exemption_limit', sa.Numeric(precision=10, scale=2), nullable=False, server_default='3000.00'),
        sa.Column('annual_exemption_used', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('annual_exemption_remaining', sa.Numeric(precision=10, scale=2), nullable=False, server_default='3000.00'),
        sa.Column('carried_forward_from_previous_year', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('small_gifts_exemption_used', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('wedding_gifts_exemption_used', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('annual_exemption_limit >= 0', name='check_iht_exemption_non_negative_limit'),
        sa.CheckConstraint('annual_exemption_used >= 0', name='check_iht_exemption_non_negative_used'),
        sa.CheckConstraint('annual_exemption_remaining >= 0', name='check_iht_exemption_non_negative_remaining'),
        sa.CheckConstraint('carried_forward_from_previous_year >= 0', name='check_iht_exemption_non_negative_carried_forward'),
        sa.CheckConstraint('small_gifts_exemption_used >= 0', name='check_iht_exemption_non_negative_small_gifts'),
        sa.CheckConstraint('wedding_gifts_exemption_used >= 0', name='check_iht_exemption_non_negative_wedding_gifts')
    )

    # Create indexes for iht_exemptions table
    op.create_index('idx_iht_exemption_user_id', 'iht_exemptions', ['user_id'])
    op.create_index('idx_iht_exemption_user_tax_year', 'iht_exemptions', ['user_id', 'tax_year'], unique=True)
    op.create_index('idx_iht_exemption_tax_year', 'iht_exemptions', ['tax_year'])


def downgrade() -> None:
    """Drop gifts and iht_exemptions tables."""

    # Drop indexes
    op.drop_index('idx_iht_exemption_tax_year', 'iht_exemptions')
    op.drop_index('idx_iht_exemption_user_tax_year', 'iht_exemptions')
    op.drop_index('idx_iht_exemption_user_id', 'iht_exemptions')

    op.drop_index('idx_gift_becomes_exempt_date', 'gifts')
    op.drop_index('idx_gift_type', 'gifts')
    op.drop_index('idx_gift_user_deleted', 'gifts')
    op.drop_index('idx_gift_user_date', 'gifts')
    op.drop_index('idx_gift_user_id', 'gifts')

    # Drop tables
    op.drop_table('iht_exemptions')
    op.drop_table('gifts')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS exemption_type_enum CASCADE')
    op.execute('DROP TYPE IF EXISTS gift_type_enum CASCADE')
