"""
Pytest configuration and fixtures for GoalPlan backend tests.

This module provides common fixtures and configuration for all tests,
including database setup, Redis connection, and test client creation.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator

# Set testing mode before importing settings
import os
os.environ["TESTING"] = "True"
os.environ["DATABASE_HOST"] = "localhost"
os.environ["REDIS_HOST"] = "localhost"

from backend.config import settings
from backend.database import Base, engine, AsyncSessionLocal, get_db
from backend.redis_client import RedisClient


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create an instance of the default event loop for the test session.

    This fixture is required for async tests to work properly.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator:
    """
    Create a fresh database session for each test.

    This fixture:
    - Creates all tables before the test
    - Provides a database session
    - Rolls back changes after the test
    - Drops all tables after the test

    Usage:
        async def test_something(db_session):
            result = await db_session.execute(select(User))
            users = result.scalars().all()
            assert len(users) == 0
    """
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def redis_client() -> AsyncGenerator[RedisClient, None]:
    """
    Create a Redis client for testing.

    This fixture:
    - Connects to Redis
    - Provides the client for tests
    - Flushes the test database after the test
    - Disconnects after the test

    Usage:
        async def test_cache(redis_client):
            await redis_client.set("test_key", "test_value")
            value = await redis_client.get("test_key")
            assert value == "test_value"
    """
    client = RedisClient()
    await client.connect()

    yield client

    # Flush test database
    if client.client:
        await client.client.flushdb()

    await client.disconnect()


@pytest.fixture
def anyio_backend():
    """
    Configure anyio backend for async tests.

    Required for pytest-asyncio compatibility.
    """
    return "asyncio"
