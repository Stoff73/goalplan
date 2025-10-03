"""create isa tfsa contribution tables

Revision ID: f5g6h7i8j9k0
Revises: a1b2c3d4e5f6
Create Date: 2025-10-02 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f5g6h7i8j9k0'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create ISA and TFSA contribution tracking tables.

    Tables:
    - isa_contributions: UK ISA contribution tracking by tax year
    - tfsa_contributions: SA TFSA contribution tracking by tax year
    """

    # Create TFSA contribution type enum only if it doesn't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE tfsa_contribution_type_enum AS ENUM ('DEPOSIT', 'GROWTH');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create isa_contributions table
    op.create_table(
        'isa_contributions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('savings_account_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tax_year', sa.String(7), nullable=False),  # Format: "2024/25"
        sa.Column('contribution_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('contribution_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),

        # Foreign Keys
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['savings_account_id'], ['savings_accounts.id'], ondelete='SET NULL'),

        # Constraints
        sa.CheckConstraint('contribution_amount > 0', name='check_positive_isa_contribution'),
    )

    # Create indexes for isa_contributions
    op.create_index('idx_isa_contributions_user_id', 'isa_contributions', ['user_id'])
    op.create_index('idx_isa_contributions_account_id', 'isa_contributions', ['savings_account_id'])
    op.create_index('idx_isa_contributions_tax_year', 'isa_contributions', ['tax_year'])
    op.create_index('idx_isa_contributions_date', 'isa_contributions', ['contribution_date'])
    op.create_index('idx_isa_user_tax_year', 'isa_contributions', ['user_id', 'tax_year'])
    op.create_index('idx_isa_account_tax_year', 'isa_contributions', ['savings_account_id', 'tax_year'])

    # Create tfsa_contributions table (use string type for enum column)
    op.create_table(
        'tfsa_contributions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('savings_account_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tax_year', sa.String(7), nullable=False),  # Format: "2024/25"
        sa.Column('contribution_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('contribution_type', postgresql.ENUM('DEPOSIT', 'GROWTH', name='tfsa_contribution_type_enum', create_type=False), nullable=False, server_default='DEPOSIT'),
        sa.Column('contribution_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),

        # Foreign Keys
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['savings_account_id'], ['savings_accounts.id'], ondelete='SET NULL'),

        # Constraints
        sa.CheckConstraint('contribution_amount > 0', name='check_positive_tfsa_contribution'),
    )

    # Create indexes for tfsa_contributions
    op.create_index('idx_tfsa_contributions_user_id', 'tfsa_contributions', ['user_id'])
    op.create_index('idx_tfsa_contributions_account_id', 'tfsa_contributions', ['savings_account_id'])
    op.create_index('idx_tfsa_contributions_tax_year', 'tfsa_contributions', ['tax_year'])
    op.create_index('idx_tfsa_contributions_date', 'tfsa_contributions', ['contribution_date'])
    op.create_index('idx_tfsa_user_tax_year', 'tfsa_contributions', ['user_id', 'tax_year'])
    op.create_index('idx_tfsa_account_tax_year', 'tfsa_contributions', ['savings_account_id', 'tax_year'])


def downgrade() -> None:
    """
    Drop ISA and TFSA contribution tracking tables.
    """
    # Drop tables
    op.drop_table('tfsa_contributions')
    op.drop_table('isa_contributions')

    # Drop enum type
    op.execute("DROP TYPE IF EXISTS tfsa_contribution_type_enum")
