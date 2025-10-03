"""
Rate limiting middleware for GoalPlan API.

This module provides rate limiting functionality using slowapi and Redis
to prevent abuse and protect against brute force attacks.

Rate limits:
- Registration: 5 requests per IP per hour
- Login: 5 requests per IP per 15 minutes
- General API: Configured per endpoint
"""

import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, Response
from typing import Callable

from config import settings
from redis_client import redis_client

logger = logging.getLogger(__name__)


def get_redis_client():
    """
    Get Redis client for rate limiting storage.

    Returns the active Redis client if connected, otherwise None.
    This allows rate limiting to fall back gracefully if Redis is unavailable.
    """
    if redis_client.client and redis_client.client.connection_pool:
        return redis_client.client
    return None


def rate_limit_key_func(request: Request) -> str:
    """
    Generate rate limit key based on client IP address.

    This function extracts the client IP from various headers to support
    proxies and load balancers, falling back to direct connection IP.

    Args:
        request: FastAPI Request object

    Returns:
        str: Client IP address for rate limiting
    """
    # Check X-Forwarded-For header first (for proxies/load balancers)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the first IP in the chain (original client)
        return forwarded.split(",")[0].strip()

    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fall back to direct connection IP
    return get_remote_address(request)


# Initialize rate limiter
# Use Redis for distributed rate limiting if available, otherwise in-memory
# In testing mode, use in-memory storage for faster tests
import os
_is_testing = os.getenv("TESTING", "False") == "True"

limiter = Limiter(
    key_func=rate_limit_key_func,
    storage_uri="memory://" if _is_testing else f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    storage_options={} if _is_testing else {
        "socket_connect_timeout": 1,
        "socket_timeout": 1,
    },
    default_limits=[],  # No default limits, set per-endpoint
    headers_enabled=True,  # Include rate limit headers in responses
    swallow_errors=True,  # Don't crash if Redis is unavailable
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.

    Provides consistent error response format when rate limits are exceeded.

    Args:
        request: FastAPI Request object
        exc: RateLimitExceeded exception

    Returns:
        Response: JSON response with 429 status code
    """
    from fastapi.responses import JSONResponse

    # Extract retry-after from exception if available
    retry_after = getattr(exc, "retry_after", None)

    logger.warning(
        f"Rate limit exceeded for {rate_limit_key_func(request)} on {request.url.path}"
    )

    response = JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please try again later.",
            "retry_after": retry_after,
        },
    )

    # Add retry-after header if available
    if retry_after:
        response.headers["Retry-After"] = str(retry_after)

    return response


# Rate limit decorators for common use cases
def rate_limit_registration():
    """Rate limit for registration endpoint: 5 requests per hour per IP."""
    return limiter.limit("5/hour", key_func=rate_limit_key_func)


def rate_limit_login():
    """Rate limit for login endpoint: 5 requests per 15 minutes per IP."""
    return limiter.limit("5/15 minutes", key_func=rate_limit_key_func)


def rate_limit_password_reset():
    """Rate limit for password reset: 3 requests per hour per IP."""
    return limiter.limit("3/hour", key_func=rate_limit_key_func)


def rate_limit_email_verification():
    """Rate limit for email verification resend: 3 requests per hour per IP."""
    return limiter.limit("3/hour", key_func=rate_limit_key_func)


def rate_limit_general():
    """General rate limit for API endpoints: 100 requests per minute per IP."""
    return limiter.limit("100/minute", key_func=rate_limit_key_func)
