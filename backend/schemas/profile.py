"""
User profile schemas for request/response validation.

This module provides Pydantic models for user profile management endpoints.
"""

import re
from typing import Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID


class AddressSchema(BaseModel):
    """Address schema for structured address data."""

    line1: str = Field(..., min_length=1, max_length=200, description="Address line 1")
    line2: Optional[str] = Field(None, max_length=200, description="Address line 2")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    postcode: str = Field(..., min_length=1, max_length=20, description="Postal/ZIP code")
    country: str = Field(..., min_length=2, max_length=2, description="ISO 2-letter country code (UK or ZA)")

    @field_validator("country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        """Validate country is UK or ZA."""
        allowed = ["UK", "ZA", "GB"]  # GB is ISO code for UK
        if v.upper() not in allowed:
            raise ValueError("Country must be UK or ZA")
        # Normalize GB to UK
        return "UK" if v.upper() == "GB" else v.upper()


class UserProfileResponse(BaseModel):
    """Response schema for GET /api/v1/user/profile."""

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    first_name: str = Field(..., description="User first name", serialization_alias="firstName")
    last_name: str = Field(..., description="User last name", serialization_alias="lastName")
    phone: Optional[str] = Field(None, description="User phone number")
    date_of_birth: Optional[date] = Field(None, description="User date of birth", serialization_alias="dateOfBirth")
    address: Optional[Dict[str, Any]] = Field(None, description="User address")
    timezone: str = Field(..., description="User timezone preference")
    status: str = Field(..., description="Account status")
    email_verified: bool = Field(..., description="Email verification status", serialization_alias="emailVerified")
    two_factor_enabled: bool = Field(default=False, description="2FA enabled status", serialization_alias="twoFactorEnabled")
    country_preference: str = Field(..., description="Country preference (UK/SA/BOTH)", serialization_alias="countryPreference")
    created_at: datetime = Field(..., description="Account creation timestamp", serialization_alias="createdAt")
    updated_at: datetime = Field(..., description="Last update timestamp", serialization_alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class ProfileUpdateRequest(BaseModel):
    """Request schema for PATCH /api/v1/user/profile."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name", alias="firstName")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Last name", alias="lastName")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    date_of_birth: Optional[date] = Field(None, description="Date of birth", alias="dateOfBirth")
    address: Optional[AddressSchema] = Field(None, description="Address")
    timezone: Optional[str] = Field(None, max_length=50, description="Timezone preference")

    class Config:
        populate_by_name = True

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format (international format)."""
        if v is None:
            return v

        # Allow international format: +[country code][number]
        # E.g., +447911123456, +27821234567
        if not re.match(r'^\+?[1-9]\d{1,14}$', v):
            raise ValueError(
                "Invalid phone number format. Use international format (e.g., +447911123456)"
            )
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: Optional[date]) -> Optional[date]:
        """Validate date of birth is in the past and user is at least 18."""
        if v is None:
            return v

        today = date.today()

        if v >= today:
            raise ValueError("Date of birth must be in the past")

        # Calculate age
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))

        if age < 18:
            raise ValueError("You must be at least 18 years old")

        if age > 120:
            raise ValueError("Invalid date of birth")

        return v

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: Optional[str]) -> Optional[str]:
        """Validate timezone is a valid IANA timezone."""
        if v is None:
            return v

        # Common timezones we support
        valid_timezones = [
            "Europe/London",
            "Africa/Johannesburg",
            "America/New_York",
            "America/Los_Angeles",
            "Europe/Paris",
            "Asia/Dubai",
            "Australia/Sydney",
            "UTC",
        ]

        if v not in valid_timezones:
            raise ValueError(
                f"Invalid timezone. Supported timezones: {', '.join(valid_timezones)}"
            )

        return v


class ProfileUpdateResponse(BaseModel):
    """Response schema for PATCH /api/v1/user/profile."""

    success: bool = Field(..., description="Update success status")
    message: str = Field(..., description="Success message")
    user: UserProfileResponse = Field(..., description="Updated user profile")


class ChangePasswordRequest(BaseModel):
    """Request schema for POST /api/v1/user/change-password."""

    current_password: str = Field(..., min_length=1, max_length=128, description="Current password", alias="currentPassword")
    new_password: str = Field(..., min_length=12, max_length=128, description="New password", alias="newPassword")

    class Config:
        populate_by_name = True

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate new password meets security requirements.

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


class ChangePasswordResponse(BaseModel):
    """Response schema for POST /api/v1/user/change-password."""

    success: bool = Field(..., description="Password change success status")
    message: str = Field(..., description="Success message")


class ChangeEmailRequest(BaseModel):
    """Request schema for POST /api/v1/user/change-email."""

    new_email: EmailStr = Field(..., description="New email address", alias="newEmail")
    password: str = Field(..., min_length=1, max_length=128, description="Current password for confirmation")

    class Config:
        populate_by_name = True

    @field_validator("new_email")
    @classmethod
    def lowercase_email(cls, v: EmailStr) -> str:
        """Convert email to lowercase."""
        return v.lower()


class ChangeEmailResponse(BaseModel):
    """Response schema for POST /api/v1/user/change-email."""

    success: bool = Field(..., description="Email change request success status")
    message: str = Field(..., description="Success message")


class VerifyEmailChangeRequest(BaseModel):
    """Request schema for POST /api/v1/user/verify-email-change."""

    token: str = Field(..., min_length=1, description="Email change verification token")


class VerifyEmailChangeResponse(BaseModel):
    """Response schema for POST /api/v1/user/verify-email-change."""

    success: bool = Field(..., description="Email change verification success status")
    message: str = Field(..., description="Success message")
    email: str = Field(..., description="New email address")


class DeleteAccountRequest(BaseModel):
    """Request schema for POST /api/v1/user/delete-account."""

    password: str = Field(..., min_length=1, max_length=128, description="Current password for confirmation")
    export_data: bool = Field(default=False, description="Generate data export before deletion", alias="exportData")

    class Config:
        populate_by_name = True


class DeleteAccountResponse(BaseModel):
    """Response schema for POST /api/v1/user/delete-account."""

    success: bool = Field(..., description="Account deletion success status")
    message: str = Field(..., description="Success message")
    export_url: Optional[str] = Field(None, description="Data export download URL (if requested)", serialization_alias="exportUrl")
    deletion_date: datetime = Field(..., description="Permanent deletion date (30 days from now)", serialization_alias="deletionDate")

    class Config:
        populate_by_name = True


class ProfileHistoryEntry(BaseModel):
    """Profile history entry schema."""

    id: str = Field(..., description="History entry ID")
    field_name: str = Field(..., description="Field that was changed", serialization_alias="fieldName")
    old_value: Optional[str] = Field(None, description="Previous value", serialization_alias="oldValue")
    new_value: Optional[str] = Field(None, description="New value", serialization_alias="newValue")
    changed_at: datetime = Field(..., description="Timestamp of change", serialization_alias="changedAt")
    ip_address: Optional[str] = Field(None, description="IP address of request", serialization_alias="ipAddress")

    class Config:
        from_attributes = True
        populate_by_name = True
