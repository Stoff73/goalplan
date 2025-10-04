"""
Pydantic schemas for tax calculation API requests and responses.

This module provides validation schemas for:
- UK Income Tax calculations
- UK National Insurance calculations
- UK Capital Gains Tax calculations
- UK Dividend Tax calculations
- SA Income Tax calculations
- SA Capital Gains Tax calculations
- SA Dividend Tax calculations
- Comprehensive tax summary

All schemas include comprehensive validation and documentation.
"""

from decimal import Decimal
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# UK TAX REQUEST SCHEMAS
# ============================================================================

class UKIncomeTaxRequest(BaseModel):
    """
    Schema for UK Income Tax calculation request.

    Validates:
    - Income is non-negative
    - Tax year format
    - Scottish residence flag
    """

    income: Decimal = Field(
        ...,
        ge=0,
        description="Gross income amount (GBP)"
    )

    is_scottish_resident: bool = Field(
        default=False,
        description="Whether taxpayer is Scottish resident (Scottish rates not yet implemented)"
    )

    tax_year: str = Field(
        default="2024/25",
        pattern=r"^20\d{2}/\d{2}$",
        description="UK tax year (e.g., 2024/25)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "income": "60000.00",
                "is_scottish_resident": False,
                "tax_year": "2024/25"
            }
        }


class UKNationalInsuranceRequest(BaseModel):
    """
    Schema for UK National Insurance calculation request.

    Validates:
    - Employment income and profits are non-negative
    - Either employee or self-employed flag set
    """

    employment_income: Decimal = Field(
        ...,
        ge=0,
        description="Employment income for Class 1 NI (GBP)"
    )

    is_self_employed: bool = Field(
        default=False,
        description="Whether taxpayer is self-employed (for Class 2 & 4 NI)"
    )

    profits: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Self-employment profits for Class 4 NI (GBP)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "employment_income": "50000.00",
                "is_self_employed": False,
                "profits": "0.00"
            }
        }


class UKCapitalGainsRequest(BaseModel):
    """
    Schema for UK Capital Gains Tax calculation request.

    Validates:
    - Total gains is non-negative
    - Annual exempt amount used is non-negative
    """

    total_gains: Decimal = Field(
        ...,
        ge=0,
        description="Total capital gains for the year (GBP)"
    )

    annual_exempt_amount_used: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Amount of annual exemption already used (GBP)"
    )

    is_higher_rate_taxpayer: bool = Field(
        default=False,
        description="Whether taxpayer pays higher/additional rate income tax"
    )

    is_property: bool = Field(
        default=False,
        description="Whether gains are from residential property"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_gains": "15000.00",
                "annual_exempt_amount_used": "0.00",
                "is_higher_rate_taxpayer": True,
                "is_property": False
            }
        }


class UKDividendTaxRequest(BaseModel):
    """
    Schema for UK Dividend Tax calculation request.

    Validates:
    - Dividend income and other income are non-negative
    """

    dividend_income: Decimal = Field(
        ...,
        ge=0,
        description="Total dividend income (GBP)"
    )

    other_income: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Other taxable income (employment, rental, etc.) (GBP)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "dividend_income": "5000.00",
                "other_income": "50000.00"
            }
        }


# ============================================================================
# SA TAX REQUEST SCHEMAS
# ============================================================================

class SAIncomeTaxRequest(BaseModel):
    """
    Schema for SA Income Tax calculation request.

    Validates:
    - Income is non-negative
    - Age is valid if provided
    - Tax year format
    """

    income: Decimal = Field(
        ...,
        ge=0,
        description="Gross taxable income (ZAR)"
    )

    age: Optional[int] = Field(
        None,
        ge=18,
        le=120,
        description="Age of taxpayer (for rebate calculation)"
    )

    tax_year: str = Field(
        default="2024/25",
        pattern=r"^20\d{2}/\d{2}$",
        description="SA tax year (e.g., 2024/25)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "income": "500000.00",
                "age": 40,
                "tax_year": "2024/25"
            }
        }


class SACapitalGainsRequest(BaseModel):
    """
    Schema for SA Capital Gains Tax calculation request.

    Validates:
    - Total gains is non-negative
    - Annual exclusion used is non-negative
    - Inclusion rate is valid percentage if provided
    """

    total_gains: Decimal = Field(
        ...,
        ge=0,
        description="Total capital gains for the year (ZAR)"
    )

    annual_exclusion_used: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Amount of annual exclusion already used (ZAR)"
    )

    inclusion_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=1,
        description="Inclusion rate (0.40 for individuals, 0.80 for companies)"
    )

    taxable_income: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Existing taxable income (to determine marginal rate) (ZAR)"
    )

    age: Optional[int] = Field(
        None,
        ge=18,
        le=120,
        description="Age of taxpayer (for income tax calculation)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_gains": "100000.00",
                "annual_exclusion_used": "0.00",
                "inclusion_rate": None,
                "taxable_income": "500000.00",
                "age": 40
            }
        }


class SADividendTaxRequest(BaseModel):
    """
    Schema for SA Dividend Tax calculation request.

    Validates:
    - Dividend income is non-negative
    - Exemption used is non-negative
    """

    dividend_income: Decimal = Field(
        ...,
        ge=0,
        description="Total dividend income (ZAR)"
    )

    exemption_used: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Amount of exemption already used (ZAR)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "dividend_income": "50000.00",
                "exemption_used": "0.00"
            }
        }


# ============================================================================
# TAX RESPONSE SCHEMAS
# ============================================================================

class TaxBandBreakdown(BaseModel):
    """Breakdown of tax by band/bracket."""

    band: str = Field(..., description="Band name or range")
    amount: Decimal = Field(..., description="Amount taxed in this band")
    rate: float = Field(..., description="Tax rate (percentage)")
    tax: Decimal = Field(..., description="Tax due in this band")

    class Config:
        from_attributes = True


class UKIncomeTaxResponse(BaseModel):
    """Response schema for UK Income Tax calculation."""

    tax_owed: Decimal = Field(..., description="Total income tax payable (GBP)")
    effective_rate: float = Field(..., description="Effective tax rate (%)")
    breakdown: List[TaxBandBreakdown] = Field(..., description="Tax breakdown by band")
    personal_allowance: Decimal = Field(..., description="Personal allowance applied (GBP)")
    taxable_income: Decimal = Field(..., description="Taxable income after allowance (GBP)")
    gross_income: Decimal = Field(..., description="Gross income (GBP)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "tax_owed": "11432.00",
                "effective_rate": 19.05,
                "breakdown": [
                    {"band": "Basic rate", "amount": "37700.00", "rate": 20.0, "tax": "7540.00"},
                    {"band": "Higher rate", "amount": "9730.00", "rate": 40.0, "tax": "3892.00"}
                ],
                "personal_allowance": "12570.00",
                "taxable_income": "47430.00",
                "gross_income": "60000.00"
            }
        }


class NIBreakdown(BaseModel):
    """Breakdown of National Insurance by class/band."""

    type: str = Field(..., description="NI class (Class 1, 2, 4)")
    band: str = Field(..., description="Band description")
    amount: Decimal = Field(..., description="Income in this band")
    rate: float | str = Field(..., description="NI rate (percentage or 'Flat')")
    ni: Decimal = Field(..., description="NI due in this band")

    class Config:
        from_attributes = True


class UKNationalInsuranceResponse(BaseModel):
    """Response schema for UK National Insurance calculation."""

    ni_owed: Decimal = Field(..., description="Total NI payable (GBP)")
    class_1: Decimal = Field(..., description="Class 1 NI (employees) (GBP)")
    class_2: Decimal = Field(..., description="Class 2 NI (self-employed) (GBP)")
    class_4: Decimal = Field(..., description="Class 4 NI (self-employed) (GBP)")
    breakdown: List[NIBreakdown] = Field(..., description="NI breakdown by class")

    class Config:
        from_attributes = True


class UKCapitalGainsResponse(BaseModel):
    """Response schema for UK Capital Gains Tax calculation."""

    cgt_owed: Decimal = Field(..., description="Total CGT payable (GBP)")
    taxable_gain: Decimal = Field(..., description="Gain after exemption (GBP)")
    exempt_amount: Decimal = Field(..., description="Exemption used (GBP)")
    rate_applied: float = Field(..., description="Tax rate applied (%)")
    total_gains: Decimal = Field(..., description="Total capital gains (GBP)")

    class Config:
        from_attributes = True


class UKDividendTaxResponse(BaseModel):
    """Response schema for UK Dividend Tax calculation."""

    dividend_tax_owed: Decimal = Field(..., description="Total dividend tax payable (GBP)")
    taxable_dividends: Decimal = Field(..., description="Dividends after allowance (GBP)")
    allowance_used: Decimal = Field(..., description="Dividend allowance used (GBP)")
    breakdown: List[TaxBandBreakdown] = Field(..., description="Tax breakdown by band")

    class Config:
        from_attributes = True


class SAIncomeTaxResponse(BaseModel):
    """Response schema for SA Income Tax calculation."""

    tax_owed: Decimal = Field(..., description="Total income tax payable (after rebates) (ZAR)")
    effective_rate: float = Field(..., description="Effective tax rate (%)")
    rebates_applied: Decimal = Field(..., description="Total rebate amount (ZAR)")
    breakdown: List[Dict] = Field(..., description="Tax breakdown by bracket")
    gross_income: Decimal = Field(..., description="Gross income (ZAR)")
    gross_tax_before_rebates: Decimal = Field(..., description="Tax before rebates (ZAR)")

    class Config:
        from_attributes = True


class SACapitalGainsResponse(BaseModel):
    """Response schema for SA Capital Gains Tax calculation."""

    cgt_owed: Decimal = Field(..., description="Total CGT payable (ZAR)")
    taxable_gain: Decimal = Field(..., description="Gain after exclusion (ZAR)")
    included_amount: Decimal = Field(..., description="Amount included in taxable income (ZAR)")
    exclusion_used: Decimal = Field(..., description="Annual exclusion applied (ZAR)")
    effective_cgt_rate: float = Field(..., description="Effective CGT rate (%)")
    total_gains: Decimal = Field(..., description="Total capital gains (ZAR)")
    inclusion_rate: float = Field(..., description="Inclusion rate applied (%)")

    class Config:
        from_attributes = True


class SADividendTaxResponse(BaseModel):
    """Response schema for SA Dividend Tax calculation."""

    dividend_tax_owed: Decimal = Field(..., description="Total dividend tax payable (ZAR)")
    taxable_dividends: Decimal = Field(..., description="Dividends after exemption (ZAR)")
    exemption_used: Decimal = Field(..., description="Exemption amount applied (ZAR)")
    gross_dividends: Decimal = Field(..., description="Gross dividends (ZAR)")
    tax_rate: float = Field(..., description="Dividend tax rate (%)")

    class Config:
        from_attributes = True


# ============================================================================
# TAX SUMMARY SCHEMAS
# ============================================================================

class CountryTaxSummary(BaseModel):
    """Summary of tax liabilities for a single country."""

    income_tax: Decimal = Field(..., description="Income tax liability")
    national_insurance: Optional[Decimal] = Field(None, description="NI liability (UK only)")
    dividend_tax: Decimal = Field(..., description="Dividend tax liability")
    capital_gains_tax: Decimal = Field(..., description="CGT liability")
    total: Decimal = Field(..., description="Total tax liability")
    currency: str = Field(..., description="Currency (GBP or ZAR)")

    class Config:
        from_attributes = True


class IncomeSources(BaseModel):
    """Breakdown of income sources."""

    employment: Decimal = Field(default=Decimal("0"), description="Employment income")
    self_employment: Decimal = Field(default=Decimal("0"), description="Self-employment income")
    dividends: Decimal = Field(default=Decimal("0"), description="Dividend income")
    interest: Decimal = Field(default=Decimal("0"), description="Interest income")
    rental: Decimal = Field(default=Decimal("0"), description="Rental income")
    capital_gains: Decimal = Field(default=Decimal("0"), description="Capital gains")
    other: Decimal = Field(default=Decimal("0"), description="Other income")
    total: Decimal = Field(default=Decimal("0"), description="Total income")

    class Config:
        from_attributes = True


class AllowancesUsed(BaseModel):
    """Summary of allowances used and remaining."""

    personal_allowance: Optional[Decimal] = Field(None, description="Personal allowance used (UK)")
    isa_allowance_used: Optional[Decimal] = Field(None, description="ISA allowance used (UK)")
    isa_allowance_remaining: Optional[Decimal] = Field(None, description="ISA allowance remaining (UK)")
    tfsa_allowance_used: Optional[Decimal] = Field(None, description="TFSA allowance used (SA)")
    tfsa_allowance_remaining: Optional[Decimal] = Field(None, description="TFSA allowance remaining (SA)")
    cgt_exemption_used: Decimal = Field(default=Decimal("0"), description="CGT exemption used")
    dividend_allowance_used: Decimal = Field(default=Decimal("0"), description="Dividend allowance used")

    class Config:
        from_attributes = True


class TaxSummaryResponse(BaseModel):
    """
    Comprehensive tax summary response.

    Aggregates all tax liabilities from user's income sources, investments,
    and savings across both UK and SA jurisdictions.
    """

    uk_taxes: Optional[CountryTaxSummary] = Field(
        None,
        description="UK tax liabilities"
    )

    sa_taxes: Optional[CountryTaxSummary] = Field(
        None,
        description="SA tax liabilities"
    )

    uk_income_sources: Optional[IncomeSources] = Field(
        None,
        description="UK income sources breakdown"
    )

    sa_income_sources: Optional[IncomeSources] = Field(
        None,
        description="SA income sources breakdown"
    )

    allowances: AllowancesUsed = Field(
        default_factory=AllowancesUsed,
        description="Allowances used and remaining"
    )

    total_tax_liability_gbp: Decimal = Field(
        ...,
        description="Total tax liability (all jurisdictions in GBP)"
    )

    total_tax_liability_zar: Decimal = Field(
        ...,
        description="Total tax liability (all jurisdictions in ZAR)"
    )

    effective_rate_combined: float = Field(
        ...,
        description="Combined effective tax rate across all income (%)"
    )

    tax_year: str = Field(
        ...,
        description="Tax year for calculations"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "uk_taxes": {
                    "income_tax": "11432.00",
                    "national_insurance": "4156.00",
                    "dividend_tax": "1050.00",
                    "capital_gains_tax": "2400.00",
                    "total": "19038.00",
                    "currency": "GBP"
                },
                "sa_taxes": {
                    "income_tax": "69376.00",
                    "national_insurance": None,
                    "dividend_tax": "10000.00",
                    "capital_gains_tax": "5400.00",
                    "total": "84776.00",
                    "currency": "ZAR"
                },
                "uk_income_sources": {
                    "employment": "60000.00",
                    "self_employment": "0.00",
                    "dividends": "5000.00",
                    "interest": "2000.00",
                    "rental": "0.00",
                    "capital_gains": "15000.00",
                    "other": "0.00",
                    "total": "82000.00"
                },
                "sa_income_sources": {
                    "employment": "500000.00",
                    "self_employment": "0.00",
                    "dividends": "50000.00",
                    "interest": "10000.00",
                    "rental": "0.00",
                    "capital_gains": "100000.00",
                    "other": "0.00",
                    "total": "660000.00"
                },
                "allowances": {
                    "personal_allowance": "12570.00",
                    "isa_allowance_used": "15000.00",
                    "isa_allowance_remaining": "5000.00",
                    "tfsa_allowance_used": "36000.00",
                    "tfsa_allowance_remaining": "0.00",
                    "cgt_exemption_used": "3000.00",
                    "dividend_allowance_used": "500.00"
                },
                "total_tax_liability_gbp": "23565.00",
                "total_tax_liability_zar": "529390.00",
                "effective_rate_combined": 18.5,
                "tax_year": "2024/25"
            }
        }


# ============================================================================
# DTA RELIEF REQUEST/RESPONSE SCHEMAS
# ============================================================================

class DTAEmploymentIncomeRequest(BaseModel):
    """Schema for DTA employment income relief calculation request."""

    uk_income: Decimal = Field(
        ...,
        ge=0,
        description="Employment income from UK sources"
    )

    sa_income: Decimal = Field(
        ...,
        ge=0,
        description="Employment income from SA sources"
    )

    uk_resident: bool = Field(
        ...,
        description="Whether taxpayer is UK resident"
    )

    sa_resident: bool = Field(
        ...,
        description="Whether taxpayer is SA resident"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "uk_income": "50000.00",
                "sa_income": "200000.00",
                "uk_resident": True,
                "sa_resident": False
            }
        }


class DTAEmploymentIncomeResponse(BaseModel):
    """Response schema for DTA employment income relief calculation."""

    uk_tax: Decimal = Field(..., description="UK tax liability")
    sa_tax: Decimal = Field(..., description="SA tax liability")
    relief: Decimal = Field(..., description="Foreign tax credit relief amount")
    net_tax: Decimal = Field(..., description="Net tax after relief")
    explanation: str = Field(..., description="Explanation of relief calculation")

    class Config:
        from_attributes = True


class DTADividendRequest(BaseModel):
    """Schema for DTA dividend relief calculation request."""

    dividend_amount: Decimal = Field(
        ...,
        ge=0,
        description="Dividend amount"
    )

    source_country: str = Field(
        ...,
        pattern="^(UK|SA)$",
        description="Country where dividend sourced"
    )

    residence_country: str = Field(
        ...,
        pattern="^(UK|SA)$",
        description="Country of residence"
    )

    withholding_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=1,
        description="Custom withholding rate (default 15%)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "dividend_amount": "10000.00",
                "source_country": "SA",
                "residence_country": "UK",
                "withholding_rate": None
            }
        }


class DTADividendResponse(BaseModel):
    """Response schema for DTA dividend relief calculation."""

    withholding_tax: Decimal = Field(..., description="Withholding tax in source country")
    residence_tax: Decimal = Field(..., description="Tax in residence country (before credit)")
    foreign_tax_credit: Decimal = Field(..., description="Foreign tax credit")
    net_tax: Decimal = Field(..., description="Total net tax")
    explanation: str = Field(..., description="Explanation of relief calculation")

    class Config:
        from_attributes = True


class DTAInterestRequest(BaseModel):
    """Schema for DTA interest relief calculation request."""

    interest_amount: Decimal = Field(
        ...,
        ge=0,
        description="Interest amount"
    )

    source_country: str = Field(
        ...,
        pattern="^(UK|SA)$",
        description="Country where interest sourced"
    )

    residence_country: str = Field(
        ...,
        pattern="^(UK|SA)$",
        description="Country of residence"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "interest_amount": "5000.00",
                "source_country": "UK",
                "residence_country": "SA"
            }
        }


class DTAInterestResponse(BaseModel):
    """Response schema for DTA interest relief calculation."""

    withholding_tax: Decimal = Field(..., description="Withholding tax (0% for UK-SA DTA)")
    residence_tax: Decimal = Field(..., description="Tax in residence country")
    net_tax: Decimal = Field(..., description="Total net tax")
    explanation: str = Field(..., description="Explanation of relief calculation")

    class Config:
        from_attributes = True


class DTACapitalGainsRequest(BaseModel):
    """Schema for DTA capital gains relief calculation request."""

    gain_amount: Decimal = Field(
        ...,
        ge=0,
        description="Capital gain amount"
    )

    asset_type: str = Field(
        ...,
        description="Asset type (IMMOVABLE_PROPERTY, BUSINESS_PROPERTY, SHARES, OTHER)"
    )

    asset_location: str = Field(
        ...,
        pattern="^(UK|SA)$",
        description="Country where asset located"
    )

    residence_country: str = Field(
        ...,
        pattern="^(UK|SA)$",
        description="Country of residence"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "gain_amount": "50000.00",
                "asset_type": "IMMOVABLE_PROPERTY",
                "asset_location": "UK",
                "residence_country": "SA"
            }
        }


class DTACapitalGainsResponse(BaseModel):
    """Response schema for DTA capital gains relief calculation."""

    taxing_country: str = Field(..., description="Country with primary taxing rights")
    tax_amount: Decimal = Field(..., description="Tax amount in taxing country")
    relief_country: str = Field(..., description="Country giving relief (or 'None')")
    explanation: str = Field(..., description="Explanation of taxing rights")

    class Config:
        from_attributes = True


class DTAPensionRequest(BaseModel):
    """Schema for DTA pension relief calculation request."""

    pension_amount: Decimal = Field(
        ...,
        ge=0,
        description="Pension amount"
    )

    pension_type: str = Field(
        ...,
        pattern="^(PRIVATE|GOVERNMENT)$",
        description="Pension type"
    )

    source_country: str = Field(
        ...,
        pattern="^(UK|SA)$",
        description="Country paying pension"
    )

    residence_country: str = Field(
        ...,
        pattern="^(UK|SA)$",
        description="Country of residence"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pension_amount": "30000.00",
                "pension_type": "PRIVATE",
                "source_country": "UK",
                "residence_country": "SA"
            }
        }


class DTAPensionResponse(BaseModel):
    """Response schema for DTA pension relief calculation."""

    taxing_country: str = Field(..., description="Country with taxing rights")
    tax_amount: Decimal = Field(..., description="Tax amount")
    explanation: str = Field(..., description="Explanation of taxing rights")

    class Config:
        from_attributes = True


class DTATieBreakerRequest(BaseModel):
    """Schema for DTA tie-breaker rules request."""

    has_uk_home: bool = Field(..., description="Has permanent home in UK")
    has_sa_home: bool = Field(..., description="Has permanent home in SA")
    uk_vital_interests: bool = Field(..., description="Centre of vital interests in UK")
    sa_vital_interests: bool = Field(..., description="Centre of vital interests in SA")
    uk_habitual_abode: bool = Field(..., description="Habitual abode in UK")
    sa_habitual_abode: bool = Field(..., description="Habitual abode in SA")
    nationality: str = Field(
        ...,
        pattern="^(UK|SA|BOTH)$",
        description="Nationality"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "has_uk_home": True,
                "has_sa_home": True,
                "uk_vital_interests": True,
                "sa_vital_interests": False,
                "uk_habitual_abode": True,
                "sa_habitual_abode": False,
                "nationality": "UK"
            }
        }


class DTATieBreakerResponse(BaseModel):
    """Response schema for DTA tie-breaker rules."""

    sole_residence: str = Field(..., description="Sole residence determination (UK, SA, or UNDETERMINED)")
    test_applied: str = Field(..., description="Test that determined residence")
    explanation: str = Field(..., description="Explanation of determination")

    class Config:
        from_attributes = True


# ============================================================================
# TAX RESIDENCY REQUEST/RESPONSE SCHEMAS
# ============================================================================

class UKSRTRequest(BaseModel):
    """Schema for UK Statutory Residence Test request."""

    days_in_uk: int = Field(
        ...,
        ge=0,
        le=366,
        description="Days present in UK during tax year"
    )

    has_family: bool = Field(
        default=False,
        description="Has UK resident spouse/partner or minor children"
    )

    has_accommodation: bool = Field(
        default=False,
        description="Has UK accommodation available"
    )

    accommodation_days: int = Field(
        default=0,
        ge=0,
        description="Days spent at UK accommodation"
    )

    work_days: int = Field(
        default=0,
        ge=0,
        description="Days working >=3 hours in UK"
    )

    prior_year_days: List[int] = Field(
        default_factory=lambda: [0, 0],
        description="Days in UK in prior 2 years [year-1, year-2]"
    )

    prior_residence: List[bool] = Field(
        default_factory=lambda: [False, False, False],
        description="UK residence in prior 3 years [year-1, year-2, year-3]"
    )

    full_time_work_abroad: bool = Field(
        default=False,
        description="Working full-time abroad"
    )

    uk_days_while_working_abroad: int = Field(
        default=0,
        ge=0,
        description="UK days while working abroad"
    )

    has_uk_home: bool = Field(
        default=False,
        description="Has UK home available for >=91 days"
    )

    days_at_uk_home: int = Field(
        default=0,
        ge=0,
        description="Days present at UK home"
    )

    full_time_work_uk: bool = Field(
        default=False,
        description="Full-time work in UK"
    )

    days_in_other_countries: Optional[Dict[str, int]] = Field(
        None,
        description="Days in other countries (for country tie)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "days_in_uk": 95,
                "has_family": True,
                "has_accommodation": True,
                "accommodation_days": 50,
                "work_days": 45,
                "prior_year_days": [100, 95],
                "prior_residence": [True, True, False],
                "full_time_work_abroad": False,
                "uk_days_while_working_abroad": 0,
                "has_uk_home": False,
                "days_at_uk_home": 0,
                "full_time_work_uk": False,
                "days_in_other_countries": {"SA": 200, "US": 30}
            }
        }


class UKSRTResponse(BaseModel):
    """Response schema for UK Statutory Residence Test."""

    resident: bool = Field(..., description="UK resident determination")
    determination_method: str = Field(..., description="Method used (Automatic Overseas/UK Test, Sufficient Ties)")
    test_passed: Optional[str] = Field(None, description="Specific test passed (if automatic)")
    days_in_uk: int = Field(..., description="Days in UK")
    ties_count: int = Field(..., description="Number of UK ties")
    ties_detail: Optional[List[str]] = Field(None, description="List of ties met")
    threshold: Optional[str] = Field(None, description="Ties threshold required (if sufficient ties test)")
    status: Optional[str] = Field(None, description="Arriver or Leaver status")
    explanation: str = Field(..., description="Explanation of determination")

    class Config:
        from_attributes = True


class SAPresenceRequest(BaseModel):
    """Schema for SA Physical Presence Test request."""

    days_current_year: int = Field(
        ...,
        ge=0,
        le=366,
        description="Days in SA in current tax year"
    )

    days_prior_years: List[int] = Field(
        default_factory=lambda: [0, 0, 0, 0, 0],
        description="Days in SA in prior 5 years [year-1, year-2, year-3, year-4, year-5]"
    )

    ordinarily_resident: bool = Field(
        default=False,
        description="Has traditional home in SA"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "days_current_year": 120,
                "days_prior_years": [110, 105, 100, 95, 92],
                "ordinarily_resident": False
            }
        }


class SAPresenceResponse(BaseModel):
    """Response schema for SA Physical Presence Test."""

    resident: bool = Field(..., description="SA resident determination")
    test_passed: Optional[str] = Field(None, description="Test that determined residence")
    days_current_year: int = Field(..., description="Days in SA current year")
    days_breakdown: Optional[Dict] = Field(None, description="Detailed days breakdown")
    explanation: str = Field(..., description="Explanation of determination")

    class Config:
        from_attributes = True
