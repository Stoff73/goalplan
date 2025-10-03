"""add_session_and_login_attempt_tables

Revision ID: 2736a7dd16c1
Revises: 8b03bf58059b
Create Date: 2025-10-01 17:15:48.472991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2736a7dd16c1'
down_revision = '8b03bf58059b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('session_token', sa.String(length=255), nullable=False),
        sa.Column('access_token_jti', sa.String(length=255), nullable=True),
        sa.Column('device_info', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('last_activity', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for user_sessions
    op.create_index('idx_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('idx_user_sessions_session_token', 'user_sessions', ['session_token'], unique=True)
    op.create_index('idx_user_sessions_expires_at', 'user_sessions', ['expires_at'])
    op.create_index('idx_user_sessions_is_active', 'user_sessions', ['is_active'])

    # Create login_attempts table
    op.create_table(
        'login_attempts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('failure_reason', sa.String(length=100), nullable=True),
        sa.Column('attempted_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for login_attempts
    op.create_index('idx_login_attempts_email', 'login_attempts', ['email'])
    op.create_index('idx_login_attempts_ip_address', 'login_attempts', ['ip_address'])
    op.create_index('idx_login_attempts_attempted_at', 'login_attempts', ['attempted_at'])
    op.create_index('idx_login_attempts_user_id', 'login_attempts', ['user_id'])


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop login_attempts table and indexes
    op.drop_index('idx_login_attempts_user_id', table_name='login_attempts')
    op.drop_index('idx_login_attempts_attempted_at', table_name='login_attempts')
    op.drop_index('idx_login_attempts_ip_address', table_name='login_attempts')
    op.drop_index('idx_login_attempts_email', table_name='login_attempts')
    op.drop_table('login_attempts')

    # Drop user_sessions table and indexes
    op.drop_index('idx_user_sessions_is_active', table_name='user_sessions')
    op.drop_index('idx_user_sessions_expires_at', table_name='user_sessions')
    op.drop_index('idx_user_sessions_session_token', table_name='user_sessions')
    op.drop_index('idx_user_sessions_user_id', table_name='user_sessions')
    op.drop_table('user_sessions')
