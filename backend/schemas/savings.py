"""
Pydantic schemas for savings account API requests and responses.

This module provides validation schemas for:
- Creating savings accounts
- Updating savings accounts
- Retrieving savings account data
- Balance history tracking

All schemas include comprehensive validation and documentation.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from models.savings_account import (
    AccountType,
    AccountPurpose,
    AccountCountry,
    InterestFrequency,
    Currency
)


# ============================================================================
# SAVINGS ACCOUNT SCHEMAS
# ============================================================================

class SavingsAccountCreate(BaseModel):
    """
    Schema for creating a new savings account.

    Validates:
    - Bank and account details
    - Positive balance and interest rate
    - ISA/TFSA mutual exclusivity
    - Required fields based on account type
    """

    bank_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the bank or financial institution"
    )

    account_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User-defined name for the account"
    )

    account_number: str = Field(
        ...,
        min_length=4,
        max_length=100,
        description="Bank account number (will be encrypted)"
    )

    account_type: AccountType = Field(
        ...,
        description="Type of savings account"
    )

    currency: Currency = Field(
        ...,
        description="Account currency"
    )

    current_balance: Decimal = Field(
        ...,
        ge=0,
        description="Current account balance"
    )

    interest_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        description="Annual interest rate percentage"
    )

    interest_payment_frequency: Optional[InterestFrequency] = Field(
        None,
        description="How often interest is paid"
    )

    is_isa: bool = Field(
        False,
        description="Whether this is an ISA account (UK tax-advantaged)"
    )

    is_tfsa: bool = Field(
        False,
        description="Whether this is a TFSA account (SA tax-advantaged)"
    )

    purpose: Optional[AccountPurpose] = Field(
        None,
        description="Purpose of the account"
    )

    country: AccountCountry = Field(
        ...,
        description="Country where account is held"
    )

    @model_validator(mode='after')
    def validate_isa_tfsa_mutual_exclusivity(self):
        """Ensure ISA and TFSA are mutually exclusive."""
        if self.is_isa and self.is_tfsa:
            raise ValueError("Account cannot be both ISA and TFSA")
        return self

    @model_validator(mode='after')
    def validate_isa_country(self):
        """Ensure ISA accounts are only in UK."""
        if self.is_isa and self.country != AccountCountry.UK:
            raise ValueError("ISA accounts can only be held in the UK")
        return self

    @model_validator(mode='after')
    def validate_tfsa_country(self):
        """Ensure TFSA accounts are only in SA."""
        if self.is_tfsa and self.country != AccountCountry.SA:
            raise ValueError("TFSA accounts can only be held in South Africa")
        return self

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "bank_name": "Barclays",
                "account_name": "Emergency Fund",
                "account_number": "12345678",
                "account_type": "SAVINGS",
                "currency": "GBP",
                "current_balance": 10000.00,
                "interest_rate": 4.5,
                "interest_payment_frequency": "MONTHLY",
                "is_isa": False,
                "is_tfsa": False,
                "purpose": "EMERGENCY_FUND",
                "country": "UK"
            }
        }


class SavingsAccountUpdate(BaseModel):
    """
    Schema for updating an existing savings account.

    All fields are optional - only provided fields will be updated.
    Account number encryption is handled separately.
    """

    bank_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255
    )

    account_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255
    )

    account_number: Optional[str] = Field(
        None,
        min_length=4,
        max_length=100
    )

    account_type: Optional[AccountType] = None

    currency: Optional[Currency] = None

    current_balance: Optional[Decimal] = Field(
        None,
        ge=0
    )

    interest_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100
    )

    interest_payment_frequency: Optional[InterestFrequency] = None

    purpose: Optional[AccountPurpose] = None

    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class SavingsAccountResponse(BaseModel):
    """
    Schema for savings account API responses.

    Includes:
    - All account details
    - Decrypted account number (last 4 digits only in production)
    - Timestamps
    - Relationship counts
    """

    id: UUID
    user_id: UUID

    bank_name: str
    account_name: str
    account_number: str  # Decrypted (consider masking in production)

    account_type: AccountType
    currency: Currency

    current_balance: Decimal
    interest_rate: Optional[Decimal] = None
    interest_payment_frequency: Optional[InterestFrequency] = None

    is_isa: bool
    is_tfsa: bool

    purpose: Optional[AccountPurpose] = None
    country: AccountCountry

    is_active: bool

    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440000",
                "bank_name": "Barclays",
                "account_name": "Emergency Fund",
                "account_number": "****5678",
                "account_type": "SAVINGS",
                "currency": "GBP",
                "current_balance": 10000.00,
                "interest_rate": 4.5,
                "interest_payment_frequency": "MONTHLY",
                "is_isa": False,
                "is_tfsa": False,
                "purpose": "EMERGENCY_FUND",
                "country": "UK",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "deleted_at": None
            }
        }


# ============================================================================
# BALANCE HISTORY SCHEMAS
# ============================================================================

class BalanceHistoryCreate(BaseModel):
    """
    Schema for creating a balance history record.

    Validates:
    - Positive balance
    - Valid date (not in future)
    - Optional notes
    """

    balance: Decimal = Field(
        ...,
        ge=0,
        description="Account balance at this point in time"
    )

    balance_date: date = Field(
        ...,
        description="Date of the balance snapshot"
    )

    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional notes for this balance update"
    )

    @field_validator('balance_date')
    @classmethod
    def validate_date_not_future(cls, v: date) -> date:
        """Ensure balance date is not in the future."""
        if v > date.today():
            raise ValueError("Balance date cannot be in the future")
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "balance": 10500.00,
                "balance_date": "2024-01-15",
                "notes": "Monthly interest payment received"
            }
        }


class BalanceHistoryResponse(BaseModel):
    """
    Schema for balance history API responses.

    Includes:
    - Balance information
    - Date and notes
    - Relationship to savings account
    """

    id: UUID
    savings_account_id: UUID

    balance: Decimal
    balance_date: date
    notes: Optional[str] = None

    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "savings_account_id": "550e8400-e29b-41d4-a716-446655440000",
                "balance": 10500.00,
                "balance_date": "2024-01-15",
                "notes": "Monthly interest payment received",
                "created_at": "2024-01-15T10:30:00"
            }
        }


# ============================================================================
# SUMMARY SCHEMAS
# ============================================================================

class SavingsAccountSummary(BaseModel):
    """
    Summary schema for dashboard aggregation.

    Provides high-level account information without sensitive details.
    """

    id: UUID
    account_name: str
    bank_name: str
    account_type: AccountType
    currency: Currency
    current_balance: Decimal
    purpose: Optional[AccountPurpose] = None
    is_isa: bool
    is_tfsa: bool
    country: AccountCountry

    class Config:
        from_attributes = True


class SavingsTotalSummary(BaseModel):
    """
    Total savings summary across all accounts.

    Aggregates:
    - Total by currency
    - Total converted to base currency
    - Count of accounts
    - ISA/TFSA status
    """

    total_accounts: int
    total_balance_gbp: Decimal
    total_balance_zar: Decimal
    total_balance_usd: Decimal
    total_balance_eur: Decimal

    isa_accounts: int
    tfsa_accounts: int

    emergency_fund_total: Decimal
    savings_goal_total: Decimal

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "total_accounts": 5,
                "total_balance_gbp": 45000.00,
                "total_balance_zar": 250000.00,
                "total_balance_usd": 10000.00,
                "total_balance_eur": 5000.00,
                "isa_accounts": 2,
                "tfsa_accounts": 1,
                "emergency_fund_total": 30000.00,
                "savings_goal_total": 15000.00
            }
        }
