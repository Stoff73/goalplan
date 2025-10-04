"""
Pydantic schemas for IHT Planning API endpoints.

This module provides request and response schemas for:
- Estate asset and liability CRUD operations
- Estate valuation and IHT calculations
- Gift and PET tracking
- SA Estate Duty calculations

All schemas include validation and serialization logic.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

from models.estate_iht import AssetType, LiabilityType, GiftType, ExemptionType


# ============================================================================
# ESTATE ASSET SCHEMAS
# ============================================================================

class EstateAssetBase(BaseModel):
    """Base schema with shared estate asset fields."""
    asset_type: AssetType = Field(..., description="Type of asset")
    description: str = Field(..., min_length=1, max_length=500, description="Asset description")
    estimated_value: Decimal = Field(..., ge=0, description="Current estimated value")
    currency: str = Field(default='GBP', min_length=3, max_length=3, description="Currency code")
    owned_individually: bool = Field(default=True, description="True if owned individually")
    joint_ownership: Optional[str] = Field(None, max_length=255, description="Name of co-owner if jointly owned")
    included_in_uk_estate: bool = Field(default=True, description="Include in UK estate for IHT")
    included_in_sa_estate: bool = Field(default=False, description="Include in SA estate for Estate Duty")
    effective_from: date = Field(..., description="Date when this valuation becomes effective")

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        """Ensure currency is uppercase 3 letters."""
        if v:
            return v.upper()
        return v


class EstateAssetCreate(EstateAssetBase):
    """Schema for creating a new estate asset."""
    pass


class EstateAssetUpdate(BaseModel):
    """Schema for updating an estate asset (all fields optional)."""
    asset_type: Optional[AssetType] = None
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    estimated_value: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    owned_individually: Optional[bool] = None
    joint_ownership: Optional[str] = Field(None, max_length=255)
    included_in_uk_estate: Optional[bool] = None
    included_in_sa_estate: Optional[bool] = None
    effective_from: Optional[date] = None

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        """Ensure currency is uppercase 3 letters."""
        if v:
            return v.upper()
        return v


class EstateAssetResponse(BaseModel):
    """Response schema for estate asset."""
    id: UUID
    user_id: UUID
    asset_type: AssetType
    description: str
    estimated_value: Decimal
    currency: str
    owned_individually: bool
    joint_ownership: Optional[str] = None
    included_in_uk_estate: bool
    included_in_sa_estate: bool
    effective_from: date
    effective_to: Optional[date] = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ESTATE LIABILITY SCHEMAS
# ============================================================================

class EstateLiabilityBase(BaseModel):
    """Base schema with shared estate liability fields."""
    liability_type: LiabilityType = Field(..., description="Type of liability")
    description: str = Field(..., min_length=1, max_length=500, description="Liability description")
    amount_outstanding: Decimal = Field(..., ge=0, description="Current outstanding balance")
    currency: str = Field(default='GBP', min_length=3, max_length=3, description="Currency code")
    deductible_from_estate: bool = Field(default=True, description="Whether deductible from estate")
    effective_from: date = Field(..., description="Date when this liability becomes effective")

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        """Ensure currency is uppercase 3 letters."""
        if v:
            return v.upper()
        return v


class EstateLiabilityCreate(EstateLiabilityBase):
    """Schema for creating a new estate liability."""
    pass


class EstateLiabilityUpdate(BaseModel):
    """Schema for updating an estate liability (all fields optional)."""
    liability_type: Optional[LiabilityType] = None
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    amount_outstanding: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    deductible_from_estate: Optional[bool] = None
    effective_from: Optional[date] = None

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        """Ensure currency is uppercase 3 letters."""
        if v:
            return v.upper()
        return v


class EstateLiabilityResponse(BaseModel):
    """Response schema for estate liability."""
    id: UUID
    user_id: UUID
    liability_type: LiabilityType
    description: str
    amount_outstanding: Decimal
    currency: str
    deductible_from_estate: bool
    effective_from: date
    effective_to: Optional[date] = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ESTATE VALUATION SCHEMAS
# ============================================================================

class EstateValuationResponse(BaseModel):
    """Response schema for estate valuation."""
    gross_estate_value: Decimal = Field(..., description="Gross estate value (all assets)")
    total_liabilities: Decimal = Field(..., description="Total deductible liabilities")
    net_estate_value: Decimal = Field(..., description="Net estate value (gross - liabilities)")
    currency: str = Field(default='GBP', description="Currency code")
    as_of_date: date = Field(..., description="Valuation date")
    asset_breakdown: List[Dict[str, Any]] = Field(default=[], description="Asset breakdown by type")


class IHTCalculationRequest(BaseModel):
    """Request schema for IHT calculation."""
    transferable_nrb_percent: Decimal = Field(
        default=Decimal('0'),
        ge=0,
        le=100,
        description="Percentage of NRB from deceased spouse (0-100)"
    )
    property_to_descendants: bool = Field(
        default=False,
        description="True if qualifying property left to direct descendants"
    )
    charitable_gifts_percent: Decimal = Field(
        default=Decimal('0'),
        ge=0,
        le=100,
        description="Percentage of estate left to charity (0-100)"
    )
    save_calculation: bool = Field(
        default=False,
        description="Save calculation for audit trail"
    )


class IHTCalculationResponse(BaseModel):
    """Response schema for IHT calculation."""
    gross_estate: Decimal
    net_estate: Decimal
    standard_nrb: Decimal
    residence_nrb: Decimal
    transferable_nrb: Decimal
    total_nrb: Decimal
    taxable_estate: Decimal
    iht_rate: Decimal
    iht_owed: Decimal
    breakdown: List[Dict[str, Any]] = Field(default=[])
    calculation_id: Optional[UUID] = None  # If saved


# ============================================================================
# GIFT SCHEMAS
# ============================================================================

class GiftCreate(BaseModel):
    """Schema for creating a new gift."""
    recipient: str = Field(..., min_length=1, max_length=255, description="Name of gift recipient")
    gift_date: date = Field(..., description="Date the gift was made")
    gift_value: Decimal = Field(..., gt=0, description="Value of the gift")
    currency: str = Field(default='GBP', min_length=3, max_length=3, description="Currency code")
    description: Optional[str] = Field(None, max_length=500, description="Optional gift description")
    exemption_type: Optional[ExemptionType] = Field(None, description="Exemption type to apply")

    @field_validator('gift_date')
    @classmethod
    def validate_gift_date(cls, v):
        """Ensure gift date is not in future."""
        if v > date.today():
            raise ValueError("Gift date cannot be in the future")
        return v

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        """Ensure currency is uppercase 3 letters."""
        if v:
            return v.upper()
        return v


class GiftResponse(BaseModel):
    """Response schema for gift."""
    id: UUID
    user_id: UUID
    recipient: str
    gift_date: date
    gift_value: Decimal
    currency: str
    gift_type: GiftType
    exemption_type: Optional[ExemptionType] = None
    becomes_exempt_date: Optional[date] = None
    still_in_pet_period: Optional[bool] = None
    description: Optional[str] = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PotentialIHTResponse(BaseModel):
    """Response schema for potential IHT on a gift."""
    gift_id: UUID
    recipient: str
    gift_date: date
    gift_value: Decimal
    years_since_gift: Decimal
    taper_relief_percent: Decimal
    effective_iht_rate: Decimal
    potential_iht: Decimal


class ExemptionStatusResponse(BaseModel):
    """Response schema for exemption status."""
    annual_exemption_limit: Decimal
    annual_exemption_used: Decimal
    annual_exemption_remaining: Decimal
    carried_forward: Decimal
    total_available: Decimal


# ============================================================================
# SA ESTATE DUTY SCHEMAS
# ============================================================================

class SAEstateDutyCalculationRequest(BaseModel):
    """Request schema for SA Estate Duty calculation."""
    as_of_date: Optional[date] = Field(None, description="Calculation date (default: today)")
    save_calculation: bool = Field(default=False, description="Save calculation for audit trail")


class SAEstateDutyCalculationResponse(BaseModel):
    """Response schema for SA Estate Duty calculation."""
    estate_value: Decimal = Field(..., description="Gross SA estate value (ZAR)")
    liabilities: Decimal = Field(..., description="Deductible liabilities (ZAR)")
    net_estate: Decimal = Field(..., description="Net estate value (ZAR)")
    abatement: Decimal = Field(..., description="SA Estate Duty abatement (R3.5M)")
    dutiable_amount: Decimal = Field(..., description="Dutiable amount after abatement")
    estate_duty_owed: Decimal = Field(..., description="Estate duty owed (ZAR)")
    effective_rate: Decimal = Field(..., description="Effective estate duty rate (%)")
    calculation_id: Optional[UUID] = None  # If saved
    currency: str = Field(default='ZAR', description="Currency code")
