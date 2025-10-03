"""
Pydantic schemas for income tracking API.

This module provides request/response models for:
- Income creation and updates
- Income summaries and aggregations
- Tax withholding details
- Currency conversion results

All schemas include validation and type safety.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
import enum


class IncomeType(str, enum.Enum):
    """Income type enumeration."""
    EMPLOYMENT = 'employment'
    SELF_EMPLOYMENT = 'self_employment'
    RENTAL = 'rental'
    INVESTMENT = 'investment'
    PENSION = 'pension'
    OTHER = 'other'


class IncomeFrequency(str, enum.Enum):
    """Income frequency enumeration."""
    ANNUAL = 'annual'
    MONTHLY = 'monthly'
    WEEKLY = 'weekly'
    ONE_TIME = 'one_time'


class Currency(str, enum.Enum):
    """Supported currency codes."""
    GBP = 'GBP'
    ZAR = 'ZAR'
    USD = 'USD'
    EUR = 'EUR'


# ===== Request Schemas =====

class IncomeCreate(BaseModel):
    """Schema for creating new income record."""

    incomeType: IncomeType = Field(..., description="Type of income")
    sourceCountry: str = Field(..., min_length=2, max_length=2, description="Source country code (UK, ZA, US, etc.)")
    description: Optional[str] = Field(None, max_length=500, description="Income description")
    employerName: Optional[str] = Field(None, max_length=255, description="Employer name (for employment income)")

    amount: Decimal = Field(..., gt=0, description="Income amount")
    currency: Currency = Field(..., description="Currency code")
    frequency: IncomeFrequency = Field(..., description="Income frequency")
    incomeDate: date = Field(..., description="Date income was received")

    isGross: bool = Field(True, description="True if gross income, False if net")
    taxWithheldAmount: Optional[Decimal] = Field(None, ge=0, description="Tax withheld at source")
    taxWithheldCurrency: Optional[Currency] = Field(None, description="Currency of tax withheld")

    isForeignIncome: bool = Field(False, description="True if foreign income")
    foreignTaxCredit: Optional[Decimal] = Field(None, ge=0, description="Foreign tax credit")

    @field_validator('sourceCountry')
    @classmethod
    def validate_source_country(cls, v: str) -> str:
        """Validate source country code."""
        valid_countries = ['UK', 'ZA', 'US', 'FR', 'DE', 'AU', 'CA', 'IE', 'NZ', 'ES', 'IT']
        if v.upper() not in valid_countries:
            raise ValueError(f'Country must be one of {valid_countries}')
        return v.upper()

    @field_validator('taxWithheldAmount')
    @classmethod
    def validate_tax_withheld(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Ensure tax withheld doesn't exceed income amount."""
        if v is not None and 'amount' in info.data:
            if v > info.data['amount']:
                raise ValueError('Tax withheld cannot exceed income amount')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "incomeType": "employment",
                "sourceCountry": "UK",
                "description": "Software Engineer Salary",
                "employerName": "Tech Corp Ltd",
                "amount": 65000.00,
                "currency": "GBP",
                "frequency": "annual",
                "incomeDate": "2024-04-06",
                "isGross": True,
                "taxWithheldAmount": 12000.00,
                "taxWithheldCurrency": "GBP",
                "isForeignIncome": False,
                "foreignTaxCredit": None
            }
        }
    }


class IncomeUpdate(BaseModel):
    """Schema for updating existing income record."""

    incomeType: Optional[IncomeType] = None
    sourceCountry: Optional[str] = Field(None, min_length=2, max_length=2)
    description: Optional[str] = Field(None, max_length=500)
    employerName: Optional[str] = Field(None, max_length=255)

    amount: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[Currency] = None
    frequency: Optional[IncomeFrequency] = None
    incomeDate: Optional[date] = None

    isGross: Optional[bool] = None
    taxWithheldAmount: Optional[Decimal] = Field(None, ge=0)
    taxWithheldCurrency: Optional[Currency] = None

    isForeignIncome: Optional[bool] = None
    foreignTaxCredit: Optional[Decimal] = Field(None, ge=0)

    @field_validator('sourceCountry')
    @classmethod
    def validate_source_country(cls, v: Optional[str]) -> Optional[str]:
        """Validate source country code."""
        if v is None:
            return v
        valid_countries = ['UK', 'ZA', 'US', 'FR', 'DE', 'AU', 'CA', 'IE', 'NZ', 'ES', 'IT']
        if v.upper() not in valid_countries:
            raise ValueError(f'Country must be one of {valid_countries}')
        return v.upper()


class TaxWithholdingCreate(BaseModel):
    """Schema for creating tax withholding details."""

    # UK PAYE Details
    payeIncomeTax: Optional[Decimal] = Field(None, ge=0)
    payeNiClass1: Optional[Decimal] = Field(None, ge=0)
    payeTaxCode: Optional[str] = Field(None, max_length=20)

    # SA PASE Details
    paseIncomeTax: Optional[Decimal] = Field(None, ge=0)
    paseUif: Optional[Decimal] = Field(None, ge=0)

    # Employer Contributions
    employerNi: Optional[Decimal] = Field(None, ge=0)
    employerUif: Optional[Decimal] = Field(None, ge=0)


# ===== Response Schemas =====

class TaxWithholdingResponse(BaseModel):
    """Schema for tax withholding response."""

    id: UUID
    incomeId: UUID

    # UK PAYE Details
    payeIncomeTax: Optional[Decimal] = None
    payeNiClass1: Optional[Decimal] = None
    payeTaxCode: Optional[str] = None

    # SA PASE Details
    paseIncomeTax: Optional[Decimal] = None
    paseUif: Optional[Decimal] = None

    # Employer Contributions
    employerNi: Optional[Decimal] = None
    employerUif: Optional[Decimal] = None

    createdAt: datetime

    model_config = {"from_attributes": True}


class IncomeResponse(BaseModel):
    """Schema for income record response."""

    id: UUID
    userId: UUID

    # Income Details
    incomeType: IncomeType
    sourceCountry: str
    description: Optional[str] = None
    employerName: Optional[str] = None

    # Amount and Currency
    amount: Decimal
    currency: Currency
    amountInGbp: Optional[Decimal] = None
    amountInZar: Optional[Decimal] = None
    exchangeRate: Optional[Decimal] = None
    exchangeRateDate: Optional[date] = None

    # Frequency and Tax Year
    frequency: IncomeFrequency
    taxYearUk: Optional[str] = None
    taxYearSa: Optional[str] = None
    incomeDate: date

    # Gross/Net and Tax Withholding
    isGross: bool
    taxWithheldAmount: Optional[Decimal] = None
    taxWithheldCurrency: Optional[Currency] = None

    # Foreign Income Details
    isForeignIncome: bool
    foreignTaxCredit: Optional[Decimal] = None
    dtaApplicable: bool

    # Metadata
    createdAt: datetime
    updatedAt: datetime

    # Optional nested withholding details
    taxWithholding: Optional[TaxWithholdingResponse] = None

    model_config = {"from_attributes": True}


class IncomeSummary(BaseModel):
    """Schema for income summary by tax year."""

    taxYear: str = Field(..., description="Tax year (e.g., '2023/24')")
    country: str = Field(..., description="Country code (UK or SA)")

    totalIncomeGbp: Decimal = Field(..., description="Total income in GBP")
    totalIncomeZar: Decimal = Field(..., description="Total income in ZAR")

    incomeByType: Dict[str, Decimal] = Field(..., description="Income breakdown by type")
    incomeBySource: Dict[str, Decimal] = Field(..., description="Income breakdown by source country")

    totalTaxWithheld: Decimal = Field(..., description="Total tax withheld")
    foreignIncome: Decimal = Field(..., description="Total foreign income")
    foreignTaxCredit: Decimal = Field(..., description="Total foreign tax credits")

    recordCount: int = Field(..., description="Number of income records")

    model_config = {
        "json_schema_extra": {
            "example": {
                "taxYear": "2023/24",
                "country": "UK",
                "totalIncomeGbp": 78500.00,
                "totalIncomeZar": 1856250.00,
                "incomeByType": {
                    "employment": 65000.00,
                    "rental": 12000.00,
                    "investment": 1500.00
                },
                "incomeBySource": {
                    "UK": 65000.00,
                    "ZA": 13500.00
                },
                "totalTaxWithheld": 14200.00,
                "foreignIncome": 13500.00,
                "foreignTaxCredit": 2400.00,
                "recordCount": 5
            }
        }
    }


class ExchangeRateResponse(BaseModel):
    """Schema for exchange rate response."""

    id: UUID
    fromCurrency: str
    toCurrency: str
    rate: Decimal
    rateDate: date
    source: str
    createdAt: datetime

    model_config = {"from_attributes": True}


class CurrencyConversionResult(BaseModel):
    """Schema for currency conversion result."""

    originalAmount: Decimal
    originalCurrency: str
    convertedAmount: Decimal
    convertedCurrency: str
    exchangeRate: Decimal
    rateDate: date
    source: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "originalAmount": 10000.00,
                "originalCurrency": "GBP",
                "convertedAmount": 236500.00,
                "convertedCurrency": "ZAR",
                "exchangeRate": 23.65,
                "rateDate": "2024-10-01",
                "source": "exchangerate-api"
            }
        }
    }
