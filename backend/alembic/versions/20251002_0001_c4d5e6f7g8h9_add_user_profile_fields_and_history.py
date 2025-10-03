"""add user profile fields and history

Revision ID: c4d5e6f7g8h9
Revises: 245e31a72e28
Create Date: 2025-10-02 00:01:00.000000

This migration adds profile fields to the users table and creates
the user_profile_history table for audit trail tracking.

Profile Fields Added to users table:
- phone: VARCHAR(20) - User's phone number
- date_of_birth: DATE - User's date of birth
- address: JSONB - Structured address (line1, line2, city, postcode, country)
- timezone: VARCHAR(50) - User's timezone preference (default: Europe/London)
- deleted_at: TIMESTAMP - Soft delete timestamp (for account deletion)

New Table: user_profile_history
- Tracks all changes to user profile fields
- Includes: field_name, old_value, new_value, timestamp, IP, user agent
- Used for audit trail and security monitoring
- Indexed for efficient query by user_id and changed_at

New Table: email_change_tokens
- Tracks email change requests
- Similar to email verification but stores both old and new email
- Tokens expire after 24 hours
- Single-use only
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic
revision = 'c4d5e6f7g8h9'
down_revision = '245e31a72e28'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add profile fields to users table and create supporting tables.
    """
    # Add profile fields to users table
    op.add_column(
        'users',
        sa.Column('phone', sa.String(20), nullable=True, comment='User phone number')
    )

    op.add_column(
        'users',
        sa.Column('date_of_birth', sa.Date(), nullable=True, comment='User date of birth')
    )

    op.add_column(
        'users',
        sa.Column('address', JSONB, nullable=True, comment='Structured address JSON')
    )

    op.add_column(
        'users',
        sa.Column(
            'timezone',
            sa.String(50),
            nullable=False,
            server_default='Europe/London',
            comment='User timezone preference'
        )
    )

    op.add_column(
        'users',
        sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='Soft delete timestamp')
    )

    # Create user_profile_history table for audit trail
    op.create_table(
        'user_profile_history',
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
            comment='Unique identifier'
        ),
        sa.Column(
            'user_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
            comment='User whose profile was changed'
        ),
        sa.Column(
            'field_name',
            sa.String(50),
            nullable=False,
            comment='Name of the field that was changed'
        ),
        sa.Column(
            'old_value',
            sa.Text(),
            nullable=True,
            comment='Previous value (serialized as text)'
        ),
        sa.Column(
            'new_value',
            sa.Text(),
            nullable=True,
            comment='New value (serialized as text)'
        ),
        sa.Column(
            'changed_by',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='SET NULL'),
            nullable=True,
            comment='User who made the change (same as user_id for self-service)'
        ),
        sa.Column(
            'changed_at',
            sa.DateTime(),
            server_default=sa.func.current_timestamp(),
            nullable=False,
            comment='Timestamp of change'
        ),
        sa.Column(
            'ip_address',
            sa.String(45),
            nullable=True,
            comment='IP address of the request (IPv4 or IPv6)'
        ),
        sa.Column(
            'user_agent',
            sa.Text(),
            nullable=True,
            comment='User agent string from the request'
        ),
        comment='Audit trail for all user profile changes'
    )

    # Create indexes for efficient querying
    op.create_index(
        'idx_profile_history_user_changed',
        'user_profile_history',
        ['user_id', sa.text('changed_at DESC')]
    )

    op.create_index(
        'idx_profile_history_changed_at',
        'user_profile_history',
        ['changed_at']
    )

    # Create email_change_tokens table
    op.create_table(
        'email_change_tokens',
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
            comment='Unique identifier'
        ),
        sa.Column(
            'user_id',
            UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
            comment='User requesting email change'
        ),
        sa.Column(
            'new_email',
            sa.String(255),
            nullable=False,
            comment='New email address (pending verification)'
        ),
        sa.Column(
            'old_email',
            sa.String(255),
            nullable=False,
            comment='Current email address (for audit)'
        ),
        sa.Column(
            'token',
            sa.String(255),
            unique=True,
            nullable=False,
            comment='Verification token'
        ),
        sa.Column(
            'expires_at',
            sa.DateTime(),
            nullable=False,
            comment='Token expiration timestamp (24 hours)'
        ),
        sa.Column(
            'used',
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
            comment='Whether token has been used'
        ),
        sa.Column(
            'used_at',
            sa.DateTime(),
            nullable=True,
            comment='Timestamp when token was used'
        ),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.func.current_timestamp(),
            nullable=False,
            comment='Token creation timestamp'
        ),
        comment='Tokens for email change verification'
    )

    # Create indexes for email_change_tokens
    op.create_index(
        'idx_email_change_tokens_token',
        'email_change_tokens',
        ['token'],
        unique=True
    )

    op.create_index(
        'idx_email_change_tokens_user_id',
        'email_change_tokens',
        ['user_id']
    )

    op.create_index(
        'idx_email_change_tokens_expires_at',
        'email_change_tokens',
        ['expires_at']
    )


def downgrade() -> None:
    """
    Remove profile fields and supporting tables.
    """
    # Drop email_change_tokens table
    op.drop_index('idx_email_change_tokens_expires_at', table_name='email_change_tokens')
    op.drop_index('idx_email_change_tokens_user_id', table_name='email_change_tokens')
    op.drop_index('idx_email_change_tokens_token', table_name='email_change_tokens')
    op.drop_table('email_change_tokens')

    # Drop user_profile_history table
    op.drop_index('idx_profile_history_changed_at', table_name='user_profile_history')
    op.drop_index('idx_profile_history_user_changed', table_name='user_profile_history')
    op.drop_table('user_profile_history')

    # Remove profile columns from users table
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'address')
    op.drop_column('users', 'date_of_birth')
    op.drop_column('users', 'phone')
