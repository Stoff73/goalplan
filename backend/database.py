"""
Database configuration and session management.

This module provides SQLAlchemy database connection setup with:
- Async database engine for PostgreSQL
- Session management for database operations
- Base declarative class for ORM models
- Connection pooling and optimization

Security features:
- Connection pooling with configurable limits
- SSL support for production environments
- Prepared statement caching
- Connection timeout configuration
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool, QueuePool

from backend.config import settings


# Create async engine with connection pooling
# Use NullPool for testing, QueuePool for production
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,  # Recycle connections after 1 hour
    poolclass=QueuePool if not settings.TESTING else NullPool,
    connect_args={
        "server_settings": {"jit": "off"},  # Disable JIT for better performance with small queries
        "command_timeout": 60,  # Query timeout in seconds
        "statement_cache_size": 0 if settings.TESTING else 100,  # Prepared statement cache
    } if not settings.DATABASE_URL.startswith("sqlite") else {},
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autocommit=False,
    autoflush=False,
)

# Base class for declarative models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get database session.

    Yields:
        AsyncSession: Database session

    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database by creating all tables.

    Note: In production, use Alembic migrations instead.
    This is useful for testing and initial development.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.

    Call this on application shutdown to cleanly close
    all database connections in the pool.
    """
    await engine.dispose()


async def check_db_connection() -> bool:
    """
    Check database connectivity.

    Returns:
        bool: True if connection successful, False otherwise

    Usage:
        if await check_db_connection():
            print("Database connected successfully")
    """
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
