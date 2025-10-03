"""
Two-factor authentication schemas for request/response validation.

This module provides Pydantic models for 2FA endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Enable2FAResponse(BaseModel):
    """Response schema for initiating 2FA setup."""

    success: bool = Field(..., description="Success status")
    secret: str = Field(..., description="TOTP secret (base32 encoded) - for manual entry")
    qr_code: str = Field(..., description="QR code as base64-encoded PNG image", serialization_alias="qrCode")
    message: str = Field(
        ..., description="Instructions for completing 2FA setup"
    )

    class Config:
        populate_by_name = True


class Verify2FASetupRequest(BaseModel):
    """Request schema for verifying 2FA setup."""

    totp_code: str = Field(
        ..., min_length=6, max_length=6, description="6-digit TOTP code from authenticator app", alias="totpCode"
    )

    class Config:
        populate_by_name = True


class Verify2FASetupResponse(BaseModel):
    """Response schema for successful 2FA setup verification."""

    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Success message")
    backup_codes: List[str] = Field(
        ..., description="10 backup codes (8 digits each) - SHOW ONLY ONCE", serialization_alias="backupCodes"
    )

    class Config:
        populate_by_name = True


class Disable2FARequest(BaseModel):
    """Request schema for disabling 2FA."""

    password: str = Field(..., min_length=1, description="Current password")
    totp_code: Optional[str] = Field(
        default=None, min_length=6, max_length=8, description="TOTP code (6 digits) or backup code (8 digits)", alias="totpCode"
    )

    class Config:
        populate_by_name = True


class Disable2FAResponse(BaseModel):
    """Response schema for disabling 2FA."""

    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Success message")


class Login2FARequiredResponse(BaseModel):
    """Response schema when 2FA code is required for login."""

    requires_2fa: bool = Field(default=True, description="2FA required flag", serialization_alias="requires2fa")
    message: str = Field(..., description="Message prompting for 2FA code")

    class Config:
        populate_by_name = True
