"""add_life_assurance_tables

Revision ID: a2b3c4d5e6f7
Revises: f5g6h7i8j9k0
Create Date: 2025-10-03 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a2b3c4d5e6f7'
down_revision = 'f5g6h7i8j9k0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""

    # Define ENUM types
    provider_country_enum = postgresql.ENUM(
        'UK', 'SA', 'OTHER',
        name='provider_country_enum',
        create_type=True
    )

    policy_type_enum = postgresql.ENUM(
        'TERM', 'WHOLE_OF_LIFE', 'DECREASING_TERM', 'LEVEL_TERM',
        'INCREASING_TERM', 'FAMILY_INCOME_BENEFIT', 'OTHER',
        name='policy_type_enum',
        create_type=True
    )

    premium_frequency_enum = postgresql.ENUM(
        'MONTHLY', 'ANNUALLY', 'SINGLE',
        name='premium_frequency_enum',
        create_type=True
    )

    trust_type_enum = postgresql.ENUM(
        'BARE', 'DISCRETIONARY', 'INTEREST_IN_POSSESSION',
        name='trust_type_enum',
        create_type=True
    )

    policy_status_enum = postgresql.ENUM(
        'ACTIVE', 'LAPSED', 'CLAIMED', 'MATURED',
        name='policy_status_enum',
        create_type=True
    )

    beneficiary_relationship_enum = postgresql.ENUM(
        'SPOUSE', 'CHILD', 'PARENT', 'SIBLING', 'OTHER',
        name='beneficiary_relationship_enum',
        create_type=True
    )

    document_type_enum = postgresql.ENUM(
        'POLICY_DOCUMENT', 'SCHEDULE', 'TRUST_DEED', 'OTHER',
        name='document_type_enum',
        create_type=True
    )

    # Create life_assurance_policies table
    op.create_table(
        'life_assurance_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Policy Details
        sa.Column('policy_number_encrypted', sa.Text(), nullable=False),
        sa.Column('provider', sa.String(length=255), nullable=False),
        sa.Column('provider_country', provider_country_enum, nullable=False),
        sa.Column('policy_type', policy_type_enum, nullable=False),

        # Coverage Amount
        sa.Column('cover_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', postgresql.ENUM(
            'GBP', 'ZAR', 'USD', 'EUR',
            name='currency_enum',
            create_type=False  # Reuse existing enum
        ), nullable=False),
        sa.Column('cover_amount_gbp', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('cover_amount_zar', sa.Numeric(precision=15, scale=2), nullable=True),

        # Premium Details
        sa.Column('premium_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('premium_frequency', premium_frequency_enum, nullable=False),
        sa.Column('annual_premium', sa.Numeric(precision=10, scale=2), nullable=True),

        # Policy Dates
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),

        # Trust Details
        sa.Column('written_in_trust', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('trust_type', trust_type_enum, nullable=True),

        # Additional Coverage
        sa.Column('critical_illness_rider', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('waiver_of_premium', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('indexation_rate', sa.Numeric(precision=5, scale=2), nullable=True),

        # Tax Impact
        sa.Column('uk_iht_impact', sa.Boolean(), nullable=True),
        sa.Column('sa_estate_duty_impact', sa.Boolean(), nullable=True),

        # Status
        sa.Column('status', policy_status_enum, nullable=False, server_default='ACTIVE'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Foreign key
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),

        # Constraints
        sa.CheckConstraint('cover_amount > 0', name='check_positive_cover_amount'),
        sa.CheckConstraint('premium_amount >= 0', name='check_positive_premium_amount'),
    )

    # Create indexes for life_assurance_policies
    op.create_index(
        'idx_life_policy_user_id',
        'life_assurance_policies',
        ['user_id'],
        unique=False
    )

    op.create_index(
        'idx_life_policy_user_status',
        'life_assurance_policies',
        ['user_id', 'status'],
        unique=False
    )

    op.create_index(
        'idx_life_policy_user_provider',
        'life_assurance_policies',
        ['user_id', 'provider'],
        unique=False
    )

    op.create_index(
        'idx_life_policy_status',
        'life_assurance_policies',
        ['status'],
        unique=False
    )

    op.create_index(
        'idx_life_policy_provider_country',
        'life_assurance_policies',
        ['provider_country'],
        unique=False
    )

    op.create_index(
        'idx_life_policy_trust',
        'life_assurance_policies',
        ['written_in_trust'],
        unique=False,
        postgresql_where=sa.text('written_in_trust = true')
    )

    # Create policy_beneficiaries table
    op.create_table(
        'policy_beneficiaries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Beneficiary Details (encrypted)
        sa.Column('name_encrypted', sa.Text(), nullable=False),
        sa.Column('date_of_birth_encrypted', sa.Text(), nullable=False),
        sa.Column('address_encrypted', sa.Text(), nullable=False),
        sa.Column('beneficiary_relationship', beneficiary_relationship_enum, nullable=False),
        sa.Column('percentage', sa.Numeric(precision=5, scale=2), nullable=False),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Foreign key
        sa.ForeignKeyConstraint(['policy_id'], ['life_assurance_policies.id'], ondelete='CASCADE'),

        # Constraints
        sa.CheckConstraint('percentage > 0 AND percentage <= 100', name='check_valid_percentage'),
    )

    # Create indexes for policy_beneficiaries
    op.create_index(
        'idx_beneficiary_policy',
        'policy_beneficiaries',
        ['policy_id'],
        unique=False
    )

    # Create policy_trust_details table
    op.create_table(
        'policy_trust_details',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Trust Details
        sa.Column('trust_type', trust_type_enum, nullable=False),
        sa.Column('trustees', sa.Text(), nullable=False),
        sa.Column('trust_beneficiaries', sa.Text(), nullable=True),
        sa.Column('trust_created_date', sa.Date(), nullable=False),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Foreign key (unique for one-to-one relationship)
        sa.ForeignKeyConstraint(['policy_id'], ['life_assurance_policies.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('policy_id', name='unique_trust_per_policy'),
    )

    # Create indexes for policy_trust_details
    op.create_index(
        'idx_trust_detail_policy',
        'policy_trust_details',
        ['policy_id'],
        unique=True
    )

    # Create policy_documents table
    op.create_table(
        'policy_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Document Details
        sa.Column('document_type', document_type_enum, nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('upload_date', sa.Date(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),

        # Timestamp
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Foreign key
        sa.ForeignKeyConstraint(['policy_id'], ['life_assurance_policies.id'], ondelete='CASCADE'),

        # Constraints
        sa.CheckConstraint('file_size > 0', name='check_positive_file_size'),
    )

    # Create indexes for policy_documents
    op.create_index(
        'idx_policy_document_policy',
        'policy_documents',
        ['policy_id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade database schema."""

    # Drop indexes for policy_documents
    op.drop_index('idx_policy_document_policy', table_name='policy_documents')

    # Drop policy_documents table
    op.drop_table('policy_documents')

    # Drop indexes for policy_trust_details
    op.drop_index('idx_trust_detail_policy', table_name='policy_trust_details')

    # Drop policy_trust_details table
    op.drop_table('policy_trust_details')

    # Drop indexes for policy_beneficiaries
    op.drop_index('idx_beneficiary_policy', table_name='policy_beneficiaries')

    # Drop policy_beneficiaries table
    op.drop_table('policy_beneficiaries')

    # Drop indexes for life_assurance_policies
    op.drop_index('idx_life_policy_trust', table_name='life_assurance_policies')
    op.drop_index('idx_life_policy_provider_country', table_name='life_assurance_policies')
    op.drop_index('idx_life_policy_status', table_name='life_assurance_policies')
    op.drop_index('idx_life_policy_user_provider', table_name='life_assurance_policies')
    op.drop_index('idx_life_policy_user_status', table_name='life_assurance_policies')
    op.drop_index('idx_life_policy_user_id', table_name='life_assurance_policies')

    # Drop life_assurance_policies table
    op.drop_table('life_assurance_policies')

    # Drop ENUM types (in reverse order of creation)
    document_type_enum = postgresql.ENUM(
        'POLICY_DOCUMENT', 'SCHEDULE', 'TRUST_DEED', 'OTHER',
        name='document_type_enum'
    )
    document_type_enum.drop(op.get_bind(), checkfirst=True)

    beneficiary_relationship_enum = postgresql.ENUM(
        'SPOUSE', 'CHILD', 'PARENT', 'SIBLING', 'OTHER',
        name='beneficiary_relationship_enum'
    )
    beneficiary_relationship_enum.drop(op.get_bind(), checkfirst=True)

    policy_status_enum = postgresql.ENUM(
        'ACTIVE', 'LAPSED', 'CLAIMED', 'MATURED',
        name='policy_status_enum'
    )
    policy_status_enum.drop(op.get_bind(), checkfirst=True)

    trust_type_enum = postgresql.ENUM(
        'BARE', 'DISCRETIONARY', 'INTEREST_IN_POSSESSION',
        name='trust_type_enum'
    )
    trust_type_enum.drop(op.get_bind(), checkfirst=True)

    premium_frequency_enum = postgresql.ENUM(
        'MONTHLY', 'ANNUALLY', 'SINGLE',
        name='premium_frequency_enum'
    )
    premium_frequency_enum.drop(op.get_bind(), checkfirst=True)

    policy_type_enum = postgresql.ENUM(
        'TERM', 'WHOLE_OF_LIFE', 'DECREASING_TERM', 'LEVEL_TERM',
        'INCREASING_TERM', 'FAMILY_INCOME_BENEFIT', 'OTHER',
        name='policy_type_enum'
    )
    policy_type_enum.drop(op.get_bind(), checkfirst=True)

    provider_country_enum = postgresql.ENUM(
        'UK', 'SA', 'OTHER',
        name='provider_country_enum'
    )
    provider_country_enum.drop(op.get_bind(), checkfirst=True)
