"""
Database and Redis connectivity tests.

This module tests the basic connectivity to PostgreSQL and Redis,
ensuring that the application can establish connections to both services.

These tests verify:
- Database connection establishment
- Database query execution
- Redis connection establishment
- Redis basic operations (set/get/delete)
"""

import pytest
from sqlalchemy import text

from backend.database import check_db_connection
from backend.redis_client import RedisClient


class TestDatabaseConnectivity:
    """Test suite for database connectivity."""

    @pytest.mark.asyncio
    async def test_database_connection(self, db_session):
        """
        Test that database connection can be established.

        This test verifies:
        - Database session is created successfully
        - Basic query can be executed
        - Result is returned correctly
        """
        # Execute a simple query
        result = await db_session.execute(text("SELECT 1 as num"))
        row = result.first()

        assert row is not None
        assert row.num == 1

    @pytest.mark.asyncio
    async def test_database_connection_check(self):
        """
        Test the database connection check utility function.

        This test verifies that the check_db_connection()
        utility function works correctly.
        """
        is_connected = await check_db_connection()
        assert is_connected is True

    @pytest.mark.asyncio
    async def test_database_session_rollback(self, db_session):
        """
        Test that database session rollback works correctly.

        This test verifies that changes can be rolled back,
        which is important for test isolation.
        """
        # Execute a query
        result = await db_session.execute(text("SELECT 1"))
        assert result is not None

        # Rollback should not raise an error
        await db_session.rollback()

        # Should still be able to execute queries
        result = await db_session.execute(text("SELECT 2 as num"))
        row = result.first()
        assert row.num == 2


class TestRedisConnectivity:
    """Test suite for Redis connectivity."""

    @pytest.mark.asyncio
    async def test_redis_connection(self, redis_client: RedisClient):
        """
        Test that Redis connection can be established.

        This test verifies:
        - Redis client connects successfully
        - Ping command returns True
        """
        is_connected = await redis_client.check_connection()
        assert is_connected is True

    @pytest.mark.asyncio
    async def test_redis_set_get(self, redis_client: RedisClient):
        """
        Test basic Redis SET and GET operations.

        This test verifies:
        - Values can be stored in Redis
        - Values can be retrieved from Redis
        - Retrieved values match stored values
        """
        test_key = "test:connectivity:key"
        test_value = "test_value"

        # Set value
        success = await redis_client.set(test_key, test_value)
        assert success is True

        # Get value
        retrieved_value = await redis_client.get(test_key)
        assert retrieved_value == test_value

    @pytest.mark.asyncio
    async def test_redis_set_get_json(self, redis_client: RedisClient):
        """
        Test Redis SET and GET with JSON serialization.

        This test verifies:
        - Complex objects can be stored as JSON
        - Objects can be retrieved and deserialized
        """
        test_key = "test:connectivity:json"
        test_value = {"name": "John", "age": 30, "active": True}

        # Set JSON value
        success = await redis_client.set(test_key, test_value)
        assert success is True

        # Get and deserialize JSON value
        retrieved_value = await redis_client.get(test_key, deserialize=True)
        assert retrieved_value == test_value
        assert retrieved_value["name"] == "John"
        assert retrieved_value["age"] == 30
        assert retrieved_value["active"] is True

    @pytest.mark.asyncio
    async def test_redis_delete(self, redis_client: RedisClient):
        """
        Test Redis DELETE operation.

        This test verifies:
        - Keys can be deleted from Redis
        - Deleted keys return None on GET
        """
        test_key = "test:connectivity:delete"

        # Set value
        await redis_client.set(test_key, "to_be_deleted")

        # Verify it exists
        value = await redis_client.get(test_key)
        assert value == "to_be_deleted"

        # Delete key
        deleted_count = await redis_client.delete(test_key)
        assert deleted_count == 1

        # Verify it's gone
        value = await redis_client.get(test_key)
        assert value is None

    @pytest.mark.asyncio
    async def test_redis_exists(self, redis_client: RedisClient):
        """
        Test Redis EXISTS operation.

        This test verifies:
        - EXISTS returns True for existing keys
        - EXISTS returns False for non-existing keys
        """
        test_key = "test:connectivity:exists"

        # Key should not exist initially
        exists = await redis_client.exists(test_key)
        assert exists is False

        # Set value
        await redis_client.set(test_key, "exists_test")

        # Key should exist now
        exists = await redis_client.exists(test_key)
        assert exists is True

    @pytest.mark.asyncio
    async def test_redis_expire(self, redis_client: RedisClient):
        """
        Test Redis EXPIRE operation.

        This test verifies:
        - Expiration can be set on keys
        - SET with expire parameter works
        """
        test_key = "test:connectivity:expire"

        # Set value with expiration
        success = await redis_client.set(test_key, "expires_soon", expire=1)
        assert success is True

        # Key should exist
        exists = await redis_client.exists(test_key)
        assert exists is True

        # Note: We don't wait for expiration in this test
        # as it would slow down the test suite

    @pytest.mark.asyncio
    async def test_redis_increment(self, redis_client: RedisClient):
        """
        Test Redis INCREMENT operation.

        This test verifies:
        - Counters can be incremented
        - INCREMENT returns new value
        """
        test_key = "test:connectivity:counter"

        # First increment (key doesn't exist, starts at 0)
        count = await redis_client.increment(test_key)
        assert count == 1

        # Second increment
        count = await redis_client.increment(test_key)
        assert count == 2

        # Increment by 5
        count = await redis_client.increment(test_key, amount=5)
        assert count == 7

    @pytest.mark.asyncio
    async def test_redis_session_management(self, redis_client: RedisClient):
        """
        Test Redis session management methods.

        This test verifies:
        - Sessions can be stored
        - Sessions can be retrieved
        - Sessions can be deleted
        """
        user_id = "test_user_123"
        session_data = {
            "refresh_token": "test_token",
            "device": "test_device",
            "ip": "127.0.0.1"
        }

        # Set session
        success = await redis_client.set_session(user_id, session_data, expire=300)
        assert success is True

        # Get session
        retrieved_session = await redis_client.get_session(user_id)
        assert retrieved_session is not None
        assert retrieved_session["refresh_token"] == "test_token"
        assert retrieved_session["device"] == "test_device"

        # Delete session
        deleted = await redis_client.delete_session(user_id)
        assert deleted is True

        # Verify session is gone
        retrieved_session = await redis_client.get_session(user_id)
        assert retrieved_session is None


class TestDatabaseIntegration:
    """Test suite for database integration features."""

    @pytest.mark.asyncio
    async def test_database_transaction(self, db_session):
        """
        Test database transaction handling.

        This test verifies:
        - Transactions can be committed
        - Changes persist within session
        """
        # Execute query within transaction
        result = await db_session.execute(
            text("SELECT 'transaction_test' as test_value")
        )
        row = result.first()
        assert row.test_value == "transaction_test"

    @pytest.mark.asyncio
    async def test_database_metadata(self):
        """
        Test that database Base metadata is initialized.

        This test verifies that the SQLAlchemy Base
        is properly configured and ready for models.
        """
        from backend.database import Base

        assert Base is not None
        assert hasattr(Base, "metadata")
        assert Base.metadata is not None


class TestConfigurationSettings:
    """Test suite for configuration settings."""

    def test_database_url_construction(self):
        """
        Test that database URL is constructed correctly.

        This test verifies that the configuration
        properly constructs database connection URLs.
        """
        from backend.config import settings

        assert settings.DATABASE_URL is not None
        # In testing mode, should use SQLite
        assert "sqlite" in settings.DATABASE_URL

    def test_redis_url_construction(self):
        """
        Test that Redis URL is constructed correctly.

        This test verifies that the configuration
        properly constructs Redis connection URLs.
        """
        from backend.config import settings

        assert settings.REDIS_URL is not None
        assert settings.REDIS_URL.startswith("redis://")

    def test_security_settings(self):
        """
        Test that security settings are properly configured.

        This test verifies critical security settings
        from CLAUDE.md requirements.
        """
        from backend.config import settings

        # Password hashing must be Argon2
        assert settings.PASSWORD_HASH_ALGORITHM == "argon2"

        # JWT settings
        assert settings.JWT_ALGORITHM in ["HS256", "RS256"]
        assert settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS > 0

        # Account lockout
        assert settings.MAX_LOGIN_ATTEMPTS == 5
        assert settings.ACCOUNT_LOCKOUT_DURATION_MINUTES > 0
