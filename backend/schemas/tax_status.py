"""
Tax status request/response schemas.

This module contains Pydantic models for tax status management,
including validation for temporal data and residency tests.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class UKDomicileStatus(str, Enum):
    """UK domicile status enumeration."""
    UK_DOMICILE = 'uk_domicile'
    NON_UK_DOMICILE = 'non_uk_domicile'
    DEEMED_DOMICILE = 'deemed_domicile'


# ===== Tax Status Schemas =====

class TaxStatusCreate(BaseModel):
    """Schema for creating a new tax status record."""

    effectiveFrom: date = Field(..., description="Start date of this tax status")
    effectiveTo: Optional[date] = Field(None, description="End date of this tax status (None = current)")

    # UK tax status
    ukTaxResident: bool = Field(..., description="Whether user is UK tax resident")
    ukDomicile: Optional[UKDomicileStatus] = Field(None, description="UK domicile status")
    ukSplitYearTreatment: bool = Field(False, description="Whether split year treatment applies")
    ukRemittanceBasis: bool = Field(False, description="Whether using remittance basis")

    # SA tax status
    saTaxResident: bool = Field(..., description="Whether user is SA tax resident")
    saOrdinarilyResident: bool = Field(False, description="Whether user is SA ordinarily resident")

    # Dual residency
    dualResident: bool = Field(False, description="Whether user is dual resident")
    dtaTieBreakerCountry: Optional[str] = Field(None, description="DTA tie-breaker country ('UK' or 'ZA')")

    @field_validator('effectiveTo')
    @classmethod
    def validate_effective_dates(cls, v, info):
        """Validate that effectiveTo is after effectiveFrom."""
        if v is not None and 'effectiveFrom' in info.data:
            if v <= info.data['effectiveFrom']:
                raise ValueError('effectiveTo must be after effectiveFrom')
        return v

    @field_validator('dtaTieBreakerCountry')
    @classmethod
    def validate_dta_country(cls, v, info):
        """Validate DTA tie-breaker country."""
        if 'dualResident' in info.data and info.data['dualResident']:
            if not v:
                raise ValueError('DTA tie-breaker country required for dual residents')
            if v not in ['UK', 'ZA']:
                raise ValueError('DTA tie-breaker must be UK or ZA')
        return v

    @field_validator('ukRemittanceBasis')
    @classmethod
    def validate_remittance_basis(cls, v, info):
        """Validate remittance basis only for non-UK domiciled."""
        if v and 'ukDomicile' in info.data:
            if info.data['ukDomicile'] == UKDomicileStatus.UK_DOMICILE:
                raise ValueError('Remittance basis only available for non-UK domiciled individuals')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "effectiveFrom": "2024-04-06",
                "effectiveTo": None,
                "ukTaxResident": True,
                "ukDomicile": "uk_domicile",
                "ukSplitYearTreatment": False,
                "ukRemittanceBasis": False,
                "saTaxResident": False,
                "saOrdinarilyResident": False,
                "dualResident": False,
                "dtaTieBreakerCountry": None
            }
        }


class TaxStatusUpdate(BaseModel):
    """Schema for updating a tax status record."""

    effectiveTo: Optional[date] = Field(None, description="End date of this tax status")
    ukTaxResident: Optional[bool] = None
    ukDomicile: Optional[UKDomicileStatus] = None
    ukSplitYearTreatment: Optional[bool] = None
    ukRemittanceBasis: Optional[bool] = None
    saTaxResident: Optional[bool] = None
    saOrdinarilyResident: Optional[bool] = None
    dualResident: Optional[bool] = None
    dtaTieBreakerCountry: Optional[str] = None


class TaxStatusResponse(BaseModel):
    """Schema for tax status response."""

    id: UUID
    userId: UUID
    effectiveFrom: date
    effectiveTo: Optional[date]

    # UK tax status
    ukTaxResident: bool
    ukDomicile: Optional[UKDomicileStatus]
    ukDeemedDomicileDate: Optional[date]
    ukSplitYearTreatment: bool
    ukRemittanceBasis: bool

    # SA tax status
    saTaxResident: bool
    saOrdinarilyResident: bool

    # Dual residency
    dualResident: bool
    dtaTieBreakerCountry: Optional[str]

    # Audit
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "userId": "123e4567-e89b-12d3-a456-426614174001",
                "effectiveFrom": "2024-04-06",
                "effectiveTo": None,
                "ukTaxResident": True,
                "ukDomicile": "deemed_domicile",
                "ukDeemedDomicileDate": "2024-04-06",
                "ukSplitYearTreatment": False,
                "ukRemittanceBasis": False,
                "saTaxResident": False,
                "saOrdinarilyResident": False,
                "dualResident": False,
                "dtaTieBreakerCountry": None,
                "createdAt": "2024-10-02T08:00:00Z",
                "updatedAt": "2024-10-02T08:00:00Z"
            }
        }


# ===== UK SRT Calculator Schemas =====

class SRTCalculatorRequest(BaseModel):
    """Schema for UK SRT calculator request."""

    taxYear: str = Field(..., description="UK tax year (format: '2023/24')")
    daysInUk: int = Field(..., ge=0, le=366, description="Number of days in UK")
    familyTie: bool = Field(False, description="Family tie: Spouse or minor children in UK")
    accommodationTie: bool = Field(False, description="Accommodation tie: Available UK accommodation")
    workTie: bool = Field(False, description="Work tie: 40+ days working in UK")
    ninetyDayTie: bool = Field(False, description="90-day tie: 90+ days in UK in previous 2 years")
    countryTie: bool = Field(False, description="Country tie: More days in UK than elsewhere")
    wasUkResidentPreviousYear: bool = Field(False, description="Was UK resident in previous year")

    @field_validator('taxYear')
    @classmethod
    def validate_tax_year(cls, v):
        """Validate UK tax year format."""
        if '/' not in v or len(v) != 7:
            raise ValueError('Tax year must be in format YYYY/YY (e.g., 2023/24)')
        parts = v.split('/')
        if len(parts) != 2:
            raise ValueError('Tax year must have exactly one / separator')
        try:
            year1 = int(parts[0])
            year2 = int(parts[1])
            if year2 != (year1 + 1) % 100:
                raise ValueError('Second year must be consecutive to first year')
        except ValueError:
            raise ValueError('Tax year parts must be valid numbers')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "taxYear": "2023/24",
                "daysInUk": 150,
                "familyTie": True,
                "accommodationTie": True,
                "workTie": False,
                "ninetyDayTie": True,
                "countryTie": False,
                "wasUkResidentPreviousYear": True
            }
        }


class SRTCalculatorResponse(BaseModel):
    """Schema for UK SRT calculator response."""

    taxResident: bool = Field(..., description="Whether user is UK tax resident")
    testResult: str = Field(..., description="Which test determined residency")
    tieCount: int = Field(..., description="Number of UK ties")
    daysInUk: int = Field(..., description="Days in UK")
    explanation: str = Field(..., description="Explanation of the result")

    class Config:
        json_schema_extra = {
            "example": {
                "taxResident": True,
                "testResult": "sufficient_ties",
                "tieCount": 3,
                "daysInUk": 150,
                "explanation": "UK resident: 3 ties (need 2 for 150 days as a leaver)"
            }
        }


# ===== SA Presence Test Schemas =====

class SAPresenceTestRequest(BaseModel):
    """Schema for SA presence test request."""

    taxYear: str = Field(..., description="SA tax year (format: '2023/24' - March 1 to Feb 28)")
    daysInSa: int = Field(..., ge=0, le=366, description="Number of days in SA")
    yearMinus1Days: Optional[int] = Field(None, ge=0, le=366, description="Days in SA last year")
    yearMinus2Days: Optional[int] = Field(None, ge=0, le=366, description="Days in SA 2 years ago")
    yearMinus3Days: Optional[int] = Field(None, ge=0, le=366, description="Days in SA 3 years ago")
    yearMinus4Days: Optional[int] = Field(None, ge=0, le=366, description="Days in SA 4 years ago")

    @field_validator('taxYear')
    @classmethod
    def validate_tax_year(cls, v):
        """Validate SA tax year format."""
        if '/' not in v or len(v) != 7:
            raise ValueError('Tax year must be in format YYYY/YY (e.g., 2023/24)')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "taxYear": "2023/24",
                "daysInSa": 120,
                "yearMinus1Days": 100,
                "yearMinus2Days": 95,
                "yearMinus3Days": 90,
                "yearMinus4Days": 85
            }
        }


class SAPresenceTestResponse(BaseModel):
    """Schema for SA presence test response."""

    taxResident: bool = Field(..., description="Whether user is SA tax resident")
    ordinarilyResident: bool = Field(..., description="Whether user is SA ordinarily resident")
    testResult: str = Field(..., description="Which test determined residency")
    fiveYearAverage: Optional[float] = Field(None, description="Average days over 5 years")
    explanation: str = Field(..., description="Explanation of the result")

    class Config:
        json_schema_extra = {
            "example": {
                "taxResident": True,
                "ordinarilyResident": False,
                "testResult": "91_day_current",
                "fiveYearAverage": 98.0,
                "explanation": "Resident: 120 days in current year (≥ 91 days)"
            }
        }


# ===== Deemed Domicile Schemas =====

class DeemedDomicileResponse(BaseModel):
    """Schema for deemed domicile calculation response."""

    isDeemedDomiciled: bool = Field(..., description="Whether user is deemed domiciled")
    deemedDomicileDate: Optional[date] = Field(None, description="Date deemed domicile started")
    reason: str = Field(..., description="Reason for deemed domicile status")
    ukResidentYears: int = Field(..., description="Number of UK resident years in last 20")

    class Config:
        json_schema_extra = {
            "example": {
                "isDeemedDomiciled": True,
                "deemedDomicileDate": "2024-04-06",
                "reason": "15 of last 20 years UK resident",
                "ukResidentYears": 16
            }
        }
