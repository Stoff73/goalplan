"""
Pytest configuration and fixtures for GoalPlan backend tests.

This module provides common fixtures and configuration for all tests,
including database setup, Redis connection, and test client creation.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession

# Set testing mode before importing settings
import os
os.environ["TESTING"] = "True"
os.environ["DATABASE_HOST"] = "localhost"
os.environ["REDIS_HOST"] = "localhost"

# Generate encryption key for testing (Fernet requires 32 byte base64 key)
from cryptography.fernet import Fernet
os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()

from config import settings
from database import Base, engine, AsyncSessionLocal, get_db
from redis_client import RedisClient
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI


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


@pytest.fixture
async def test_app() -> FastAPI:
    """
    Create a FastAPI application for testing.

    This fixture:
    - Creates a minimal FastAPI app
    - Includes the registration router
    - Adds rate limiter state and exception handler
    - Returns the app for test client usage

    Usage:
        async def test_endpoint(test_client):
            response = await test_client.get("/api/v1/auth/health")
            assert response.status_code == 200
    """
    from fastapi import FastAPI
    from api.v1.auth import router as auth_router
    from api.v1.user import router as user_router
    from api.v1.dashboard import router as dashboard_router
    from api.v1.savings import router as savings_router
    from middleware.rate_limiter import limiter, rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded

    app = FastAPI(title="GoalPlan Test API")

    # Add rate limiter state
    app.state.limiter = limiter

    # Add rate limit exception handler
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # Include routers
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(user_router, prefix="/api/v1/user", tags=["User Profile"])
    app.include_router(dashboard_router, prefix="/api/v1", tags=["Dashboard"])
    app.include_router(savings_router, prefix="/api/v1/savings", tags=["Savings"])

    return app


@pytest.fixture
async def test_client(test_app: FastAPI, db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for testing API endpoints.

    This fixture:
    - Creates an AsyncClient with the test app
    - Overrides the database dependency to use the test session
    - Provides the client for making API requests in tests

    Usage:
        async def test_registration(test_client):
            response = await test_client.post("/api/v1/auth/register", json={...})
            assert response.status_code == 201
    """
    # Override the database dependency
    async def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db

    # Create the test client
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://testserver"
    ) as client:
        yield client

    # Clear dependency overrides
    test_app.dependency_overrides.clear()


@pytest.fixture
async def client(test_app: FastAPI, db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Alias for test_client fixture for shorter test code.
    """
    # Override the database dependency
    async def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db

    # Create the test client
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://testserver"
    ) as client:
        yield client

    # Clear dependency overrides
    test_app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """
    Create a test user for testing.

    Returns an active, verified user that can be used in tests.
    Password is 'SecurePass123!'
    """
    from models import User, UserStatus
    from models.user import CountryPreference
    from utils.password import hash_password
    from datetime import datetime

    user = User(
        email="testuser@example.com",
        password_hash=hash_password("SecurePass123!"),
        first_name="Test",
        last_name="User",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
        marketing_consent=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def authenticated_headers(test_user, db_session, redis_client):
    """
    Create authentication headers with a valid JWT token and session.

    Returns a dictionary with Authorization header for authenticated requests.
    """
    from utils.jwt import generate_access_token, generate_refresh_token, get_token_jti
    from services.session import session_service

    access_token = generate_access_token(test_user.id)
    refresh_token = generate_refresh_token(test_user.id)
    access_token_jti = get_token_jti(access_token)
    refresh_token_jti = get_token_jti(refresh_token)

    # Create session in database and Redis
    await session_service.create_session(
        db=db_session,
        user_id=test_user.id,
        refresh_token_jti=refresh_token_jti,
        access_token_jti=access_token_jti,
        device_info="test-device",
        ip_address="127.0.0.1",
    )

    return {
        "Authorization": f"Bearer {access_token}"
    }


# Alias for backward compatibility
@pytest.fixture
async def async_client(test_client):
    """Alias for test_client for backward compatibility."""
    return test_client
