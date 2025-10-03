"""
Application configuration management.

This module provides centralized configuration using Pydantic Settings
with support for environment variables and .env files.

Security features:
- Environment-based configuration
- Sensitive data loaded from environment variables
- Validation of configuration values
- Type safety with Pydantic
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, RedisDsn, field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables.
    For local development, create a .env file in the backend directory.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "GoalPlan API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    TESTING: bool = Field(default=False, description="Testing mode")

    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: list[str] = Field(default=["*"], description="CORS allowed hosts")

    # Database - PostgreSQL
    DATABASE_HOST: str = Field(default="localhost", description="Database host")
    DATABASE_PORT: int = Field(default=5432, description="Database port")
    DATABASE_USER: str = Field(default="goalplan_user", description="Database user")
    DATABASE_PASSWORD: str = Field(default="", description="Database password")
    DATABASE_NAME: str = Field(default="goalplan_dev", description="Database name")
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")

    # Database - Connection Pool
    DATABASE_POOL_SIZE: int = Field(default=5, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Max overflow connections")
    DATABASE_POOL_RECYCLE: int = Field(default=3600, description="Recycle connections after N seconds")

    # Redis
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    REDIS_MAX_CONNECTIONS: int = Field(default=10, description="Redis connection pool size")

    # Security - JWT (RS256 with asymmetric keys)
    JWT_ALGORITHM: str = Field(default="RS256", description="JWT algorithm (RS256 for asymmetric signing)")
    JWT_PRIVATE_KEY_PATH: str = Field(
        default="keys/jwt_private_key.pem",
        description="Path to RSA private key for JWT signing"
    )
    JWT_PUBLIC_KEY_PATH: str = Field(
        default="keys/jwt_public_key.pem",
        description="Path to RSA public key for JWT verification"
    )
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, description="Access token expiration")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration")

    # Security - Password Hashing
    PASSWORD_HASH_ALGORITHM: str = Field(default="argon2", description="Password hashing algorithm")
    PASSWORD_MIN_LENGTH: int = Field(default=12, description="Minimum password length")

    # Security - Account Lockout
    MAX_LOGIN_ATTEMPTS: int = Field(default=5, description="Max failed login attempts")
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = Field(default=30, description="Account lockout duration")

    # Security - Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Max requests per minute")

    # Encryption - Data at Rest
    ENCRYPTION_KEY: Optional[str] = Field(
        default=None,
        description="Encryption key for sensitive data (AES-256)"
    )

    # Email Configuration
    EMAIL_BACKEND: str = Field(
        default="console",
        description="Email backend: 'sendgrid' or 'console' (development)"
    )
    SENDGRID_API_KEY: Optional[str] = Field(
        default=None,
        description="SendGrid API key for email sending"
    )
    EMAIL_FROM_ADDRESS: str = Field(
        default="noreply@goalplan.com",
        description="From email address"
    )
    EMAIL_FROM_NAME: str = Field(
        default="GoalPlan",
        description="From name for emails"
    )
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Frontend URL for email links"
    )
    REQUIRE_EMAIL_VERIFICATION: bool = Field(
        default=False,
        description="Require email verification before login (set to False for development)"
    )

    @property
    def DATABASE_URL(self) -> str:
        """
        Construct PostgreSQL database URL.

        Returns:
            str: Async PostgreSQL connection string

        Note: Uses asyncpg driver for async support
        """
        if self.TESTING:
            # Use SQLite for testing
            return "sqlite+aiosqlite:///./test.db"

        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """
        Construct synchronous PostgreSQL database URL for Alembic migrations.

        Returns:
            str: Sync PostgreSQL connection string

        Note: Alembic requires synchronous connection
        """
        if self.TESTING:
            return "sqlite:///./test.db"

        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @property
    def REDIS_URL(self) -> str:
        """
        Construct Redis connection URL.

        Returns:
            str: Redis connection string
        """
        if self.REDIS_PASSWORD:
            return (
                f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:"
                f"{self.REDIS_PORT}/{self.REDIS_DB}"
            )
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production", "testing"]
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of: {', '.join(allowed)}")
        return v.lower()

    @field_validator("JWT_ALGORITHM")
    @classmethod
    def validate_jwt_algorithm(cls, v: str) -> str:
        """Validate JWT algorithm - must be RS256 for security."""
        if v != "RS256":
            raise ValueError("JWT algorithm must be RS256 (asymmetric signing required per CLAUDE.md)")
        return v

    @field_validator("PASSWORD_HASH_ALGORITHM")
    @classmethod
    def validate_password_algorithm(cls, v: str) -> str:
        """Validate password hashing algorithm."""
        if v.lower() != "argon2":
            raise ValueError("Password hashing must use Argon2 (as per CLAUDE.md)")
        return v.lower()

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    def get_jwt_private_key(self) -> str:
        """
        Load JWT private key from file.

        Returns:
            str: PEM-encoded RSA private key

        Raises:
            FileNotFoundError: If private key file not found
            ValueError: If key file is empty or invalid
        """
        import os
        from pathlib import Path

        # Get absolute path to key file
        base_dir = Path(__file__).parent
        key_path = base_dir / self.JWT_PRIVATE_KEY_PATH

        if not key_path.exists():
            raise FileNotFoundError(
                f"JWT private key not found at {key_path}. "
                "Run key generation script to create keys."
            )

        private_key = key_path.read_text()
        if not private_key:
            raise ValueError(f"JWT private key file is empty: {key_path}")

        return private_key

    def get_jwt_public_key(self) -> str:
        """
        Load JWT public key from file.

        Returns:
            str: PEM-encoded RSA public key

        Raises:
            FileNotFoundError: If public key file not found
            ValueError: If key file is empty or invalid
        """
        import os
        from pathlib import Path

        # Get absolute path to key file
        base_dir = Path(__file__).parent
        key_path = base_dir / self.JWT_PUBLIC_KEY_PATH

        if not key_path.exists():
            raise FileNotFoundError(
                f"JWT public key not found at {key_path}. "
                "Run key generation script to create keys."
            )

        public_key = key_path.read_text()
        if not public_key:
            raise ValueError(f"JWT public key file is empty: {key_path}")

        return public_key


# Global settings instance
settings = Settings()
