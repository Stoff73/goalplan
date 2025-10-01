"""
Redis client configuration for caching and session management.

This module provides Redis connection setup with:
- Connection pooling for optimal performance
- Async support for non-blocking operations
- Session storage and caching utilities
- Health check functionality

Use cases:
- User session storage (JWT refresh tokens)
- Rate limiting counters
- Caching expensive database queries
- Temporary data storage (OTP codes, verification tokens)
"""

from typing import Optional, Any
import json
from datetime import timedelta

from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import RedisError

from config import settings


class RedisClient:
    """
    Redis client wrapper with connection pooling and utility methods.

    Attributes:
        pool: Redis connection pool
        client: Redis client instance
    """

    def __init__(self):
        """Initialize Redis client with connection pool."""
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[Redis] = None

    async def connect(self) -> None:
        """
        Establish Redis connection with connection pool.

        Creates a connection pool for efficient connection reuse.
        Should be called during application startup.
        """
        self.pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True,  # Auto-decode bytes to strings
            socket_connect_timeout=5,
            socket_keepalive=True,
            health_check_interval=30,
        )
        self.client = Redis(connection_pool=self.pool)

    async def disconnect(self) -> None:
        """
        Close Redis connection and cleanup resources.

        Should be called during application shutdown.
        """
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()

    async def check_connection(self) -> bool:
        """
        Check Redis connectivity.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if not self.client:
                return False
            await self.client.ping()
            return True
        except RedisError as e:
            print(f"Redis connection failed: {e}")
            return False

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """
        Set a key-value pair in Redis.

        Args:
            key: Redis key
            value: Value to store (will be JSON serialized if not string)
            expire: Optional expiration time in seconds

        Returns:
            bool: True if successful, False otherwise

        Example:
            await redis_client.set("user:123:session", session_data, expire=900)
        """
        try:
            if not isinstance(value, str):
                value = json.dumps(value)

            if expire:
                await self.client.setex(key, expire, value)
            else:
                await self.client.set(key, value)
            return True
        except RedisError as e:
            print(f"Redis SET failed for key {key}: {e}")
            return False

    async def get(self, key: str, deserialize: bool = False) -> Optional[Any]:
        """
        Get value from Redis by key.

        Args:
            key: Redis key
            deserialize: If True, attempt to JSON deserialize the value

        Returns:
            Value if key exists, None otherwise

        Example:
            session_data = await redis_client.get("user:123:session", deserialize=True)
        """
        try:
            value = await self.client.get(key)
            if value and deserialize:
                return json.loads(value)
            return value
        except RedisError as e:
            print(f"Redis GET failed for key {key}: {e}")
            return None

    async def delete(self, *keys: str) -> int:
        """
        Delete one or more keys from Redis.

        Args:
            *keys: One or more Redis keys to delete

        Returns:
            int: Number of keys deleted

        Example:
            await redis_client.delete("user:123:session", "user:123:cart")
        """
        try:
            return await self.client.delete(*keys)
        except RedisError as e:
            print(f"Redis DELETE failed: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis.

        Args:
            key: Redis key

        Returns:
            bool: True if key exists, False otherwise
        """
        try:
            return await self.client.exists(key) > 0
        except RedisError as e:
            print(f"Redis EXISTS failed for key {key}: {e}")
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration time for a key.

        Args:
            key: Redis key
            seconds: Expiration time in seconds

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return await self.client.expire(key, seconds)
        except RedisError as e:
            print(f"Redis EXPIRE failed for key {key}: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a counter stored in Redis.

        Args:
            key: Redis key
            amount: Amount to increment by (default: 1)

        Returns:
            int: New value after increment, None on error

        Example:
            # Rate limiting
            count = await redis_client.increment("rate_limit:user:123")
            if count == 1:
                await redis_client.expire("rate_limit:user:123", 60)
        """
        try:
            return await self.client.incrby(key, amount)
        except RedisError as e:
            print(f"Redis INCR failed for key {key}: {e}")
            return None

    async def set_session(
        self,
        user_id: str,
        session_data: dict,
        expire: int = 604800  # 7 days default
    ) -> bool:
        """
        Store user session data.

        Args:
            user_id: User identifier
            session_data: Session data dictionary
            expire: Session expiration in seconds (default: 7 days)

        Returns:
            bool: True if successful, False otherwise

        Example:
            await redis_client.set_session(
                user_id="123",
                session_data={"refresh_token": "...", "device": "mobile"},
                expire=604800
            )
        """
        key = f"session:{user_id}"
        return await self.set(key, session_data, expire=expire)

    async def get_session(self, user_id: str) -> Optional[dict]:
        """
        Retrieve user session data.

        Args:
            user_id: User identifier

        Returns:
            dict: Session data if exists, None otherwise

        Example:
            session = await redis_client.get_session("123")
            if session:
                refresh_token = session.get("refresh_token")
        """
        key = f"session:{user_id}"
        return await self.get(key, deserialize=True)

    async def delete_session(self, user_id: str) -> bool:
        """
        Delete user session (logout).

        Args:
            user_id: User identifier

        Returns:
            bool: True if deleted, False otherwise
        """
        key = f"session:{user_id}"
        return await self.delete(key) > 0


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """
    Dependency for FastAPI to get Redis client.

    Returns:
        RedisClient: Redis client instance

    Usage:
        @app.get("/check-cache")
        async def check_cache(redis: RedisClient = Depends(get_redis)):
            value = await redis.get("my_key")
            return {"value": value}
    """
    return redis_client
