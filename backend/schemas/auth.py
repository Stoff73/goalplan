"""
Authentication schemas for request/response validation.

This module provides Pydantic models for authentication endpoints.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserRegistrationRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=12, max_length=128, description="User password")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name", alias="firstName")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name", alias="lastName")
    country: str = Field(..., description="Country preference: UK, SA, or BOTH")
    terms_accepted: bool = Field(..., description="Terms and conditions acceptance", alias="termsAccepted")
    marketing_consent: bool = Field(default=False, description="Marketing communications consent", alias="marketingConsent")

    class Config:
        populate_by_name = True  # Allow both snake_case and camelCase

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password meets security requirements.

        Requirements:
        - Minimum 12 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters long")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")

        return v

    @field_validator("country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        """Validate country preference."""
        allowed = ["UK", "SA", "BOTH"]
        if v.upper() not in allowed:
            raise ValueError(f"Country must be one of: {', '.join(allowed)}")
        return v.upper()

    @field_validator("terms_accepted")
    @classmethod
    def validate_terms_accepted(cls, v: bool) -> bool:
        """Validate terms have been accepted."""
        if not v:
            raise ValueError("You must accept the terms and conditions")
        return v


class UserRegistrationResponse(BaseModel):
    """Response schema for user registration."""

    success: bool = Field(..., description="Registration success status")
    message: str = Field(..., description="Success message")
    user_id: str = Field(..., description="Created user ID", serialization_alias="userId")


class EmailVerificationRequest(BaseModel):
    """Request schema for email verification."""

    token: str = Field(..., min_length=1, description="Email verification token")


class EmailVerificationResponse(BaseModel):
    """Response schema for email verification."""

    success: bool = Field(..., description="Verification success status")
    message: str = Field(..., description="Success/error message")


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, max_length=128, description="User password")
    totp_code: Optional[str] = Field(default=None, min_length=6, max_length=8, description="TOTP code or backup code (if 2FA enabled)", alias="totpCode")
    device_info: Optional[str] = Field(default=None, max_length=500, description="Device information (user agent)", alias="deviceInfo")
    remember_me: Optional[bool] = Field(default=False, description="Remember device for 30 days", alias="rememberMe")

    class Config:
        populate_by_name = True  # Allow both snake_case and camelCase

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: EmailStr) -> str:
        """Convert email to lowercase for case-insensitive comparison."""
        return v.lower()


class UserInfo(BaseModel):
    """User information in login response."""

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    first_name: str = Field(..., description="User first name", serialization_alias="firstName")
    last_name: str = Field(..., description="User last name", serialization_alias="lastName")
    country_preference: str = Field(..., description="Country preference", serialization_alias="countryPreference")
    two_factor_enabled: bool = Field(default=False, description="Whether 2FA is enabled", serialization_alias="twoFactorEnabled")

    class Config:
        from_attributes = True
        populate_by_name = True


class LoginResponse(BaseModel):
    """Response schema for successful login."""

    access_token: str = Field(..., description="JWT access token", serialization_alias="accessToken")
    refresh_token: str = Field(..., description="JWT refresh token", serialization_alias="refreshToken")
    token_type: str = Field(default="bearer", description="Token type", serialization_alias="tokenType")
    expires_in: int = Field(..., description="Access token expiration in seconds", serialization_alias="expiresIn")
    user: UserInfo = Field(..., description="User information")

    class Config:
        populate_by_name = True


class TokenRefreshRequest(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str = Field(..., min_length=1, description="JWT refresh token", alias="refreshToken")

    class Config:
        populate_by_name = True


class TokenRefreshResponse(BaseModel):
    """Response schema for token refresh."""

    access_token: str = Field(..., description="New JWT access token", serialization_alias="accessToken")
    token_type: str = Field(default="bearer", description="Token type", serialization_alias="tokenType")
    expires_in: int = Field(..., description="Access token expiration in seconds", serialization_alias="expiresIn")

    class Config:
        populate_by_name = True


class LogoutResponse(BaseModel):
    """Response schema for logout."""

    success: bool = Field(..., description="Logout success status")
    message: str = Field(..., description="Success message")


class LogoutAllResponse(BaseModel):
    """Response schema for logout from all sessions."""

    success: bool = Field(..., description="Logout success status")
    message: str = Field(..., description="Success message")
    sessions_revoked: int = Field(..., description="Number of sessions revoked", serialization_alias="sessionsRevoked")

    class Config:
        populate_by_name = True
