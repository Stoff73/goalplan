"""
Alembic migration environment configuration.

This module configures Alembic to work with our SQLAlchemy setup
and automatically detect model changes for migration generation.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine import Connection

from alembic import context

# Import application config and models
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from config import settings
from database import Base

# Import all models here to ensure they are registered with Base.metadata
# This is critical for Alembic to auto-generate migrations
from models.user import User, EmailVerificationToken
# from models.account import Account
# Add more model imports as they are created

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
# This line sets up loggers basically
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

# Override sqlalchemy.url from config with our settings
config.set_main_option("sqlalchemy.url", settings.SYNC_DATABASE_URL)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Detect column type changes
        compare_server_default=True,  # Detect server default changes
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    Creates an Engine and associates a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.SYNC_DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


# Determine which mode to run migrations in
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
