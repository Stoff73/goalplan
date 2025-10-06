"""
Pydantic schemas for investment API requests and responses.

This module provides validation schemas for:
- Investment account creation and management
- Holdings management and tracking
- Price updates and selling
- Dividend recording

All schemas include comprehensive validation and documentation.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from models.investment import (
    AccountType,
    AccountCountry,
    AccountStatus,
    SecurityType,
    AssetClass,
    Region,
    SourceCountry
)


# ============================================================================
# INVESTMENT ACCOUNT SCHEMAS
# ============================================================================

class CreateAccountRequest(BaseModel):
    """
    Schema for creating a new investment account.

    Validates:
    - Account type and provider details
    - Account number (will be encrypted)
    - Country and currency
    """

    account_type: AccountType = Field(
        ...,
        description="Type of investment account (STOCKS_ISA, GIA, etc.)"
    )

    provider: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Investment provider or platform name"
    )

    account_number: str = Field(
        ...,
        min_length=4,
        max_length=100,
        description="Account number (will be encrypted, only last 4 displayed)"
    )

    country: AccountCountry = Field(
        ...,
        description="Country where account is held"
    )

    base_currency: str = Field(
        default="GBP",
        pattern="^(GBP|ZAR|USD|EUR)$",
        description="Base currency for the account"
    )

    account_open_date: Optional[date] = Field(
        None,
        description="Date when account was opened"
    )

    @field_validator('account_open_date')
    @classmethod
    def validate_date_not_future(cls, v: Optional[date]) -> Optional[date]:
        """Ensure account open date is not in the future."""
        if v and v > date.today():
            raise ValueError("Account open date cannot be in the future")
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "account_type": "STOCKS_ISA",
                "provider": "Vanguard",
                "account_number": "12345678",
                "country": "UK",
                "base_currency": "GBP",
                "account_open_date": "2024-01-01"
            }
        }


class AccountResponse(BaseModel):
    """
    Schema for investment account API responses.

    Includes:
    - All account details
    - Masked account number (last 4 digits only)
    - Status and timestamps
    - Holdings count
    """

    id: UUID
    user_id: UUID

    account_type: AccountType
    provider: str
    account_number: str  # Masked (****1234)
    country: AccountCountry
    base_currency: str
    account_open_date: Optional[date] = None

    status: AccountStatus
    deleted: bool

    holdings_count: int = Field(default=0, description="Number of holdings in account")

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440000",
                "account_type": "STOCKS_ISA",
                "provider": "Vanguard",
                "account_number": "****5678",
                "country": "UK",
                "base_currency": "GBP",
                "account_open_date": "2024-01-01",
                "status": "ACTIVE",
                "deleted": False,
                "holdings_count": 5,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


# ============================================================================
# INVESTMENT HOLDING SCHEMAS
# ============================================================================

class CreateHoldingRequest(BaseModel):
    """
    Schema for adding a new investment holding.

    Validates:
    - Security details and quantities
    - Purchase information
    - Asset classification
    """

    account_id: UUID = Field(
        ...,
        description="Investment account UUID"
    )

    security_type: SecurityType = Field(
        ...,
        description="Type of security (STOCK, FUND, ETF, etc.)"
    )

    ticker: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Ticker symbol"
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Security name"
    )

    quantity: Decimal = Field(
        ...,
        gt=0,
        description="Number of shares/units (must be positive)"
    )

    purchase_price: Decimal = Field(
        ...,
        ge=0,
        description="Purchase price per share/unit"
    )

    purchase_date: date = Field(
        ...,
        description="Date of purchase"
    )

    purchase_currency: str = Field(
        ...,
        pattern="^(GBP|ZAR|USD|EUR)$",
        description="Currency of purchase"
    )

    asset_class: AssetClass = Field(
        ...,
        description="Asset class (EQUITY, FIXED_INCOME, etc.)"
    )

    region: Region = Field(
        ...,
        description="Geographic region"
    )

    sector: Optional[str] = Field(
        None,
        max_length=100,
        description="Sector (optional)"
    )

    isin: Optional[str] = Field(
        None,
        max_length=12,
        description="ISIN code (optional)"
    )

    @field_validator('purchase_date')
    @classmethod
    def validate_purchase_date(cls, v: date) -> date:
        """Ensure purchase date is not in the future."""
        if v > date.today():
            raise ValueError("Purchase date cannot be in the future")
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "account_id": "550e8400-e29b-41d4-a716-446655440000",
                "security_type": "STOCK",
                "ticker": "VWRL",
                "name": "Vanguard FTSE All-World UCITS ETF",
                "quantity": 100,
                "purchase_price": 95.50,
                "purchase_date": "2024-01-15",
                "purchase_currency": "GBP",
                "asset_class": "EQUITY",
                "region": "GLOBAL",
                "sector": "Diversified"
            }
        }


class HoldingResponse(BaseModel):
    """
    Schema for investment holding API responses.

    Includes:
    - All holding details
    - Current value and unrealized gains
    - Asset classification
    """

    id: UUID
    account_id: UUID

    security_type: SecurityType
    ticker: Optional[str] = None
    isin: Optional[str] = None
    security_name: str

    quantity: Decimal
    purchase_date: date
    purchase_price: Decimal
    purchase_currency: str

    current_price: Decimal
    current_value: Decimal
    unrealized_gain: Decimal
    unrealized_gain_percentage: Decimal

    asset_class: AssetClass
    region: Region
    sector: Optional[str] = None

    last_price_update: Optional[datetime] = None
    deleted: bool

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "account_id": "550e8400-e29b-41d4-a716-446655440000",
                "security_type": "STOCK",
                "ticker": "VWRL",
                "isin": "IE00B3RBWM25",
                "security_name": "Vanguard FTSE All-World UCITS ETF",
                "quantity": 100,
                "purchase_date": "2024-01-15",
                "purchase_price": 95.50,
                "purchase_currency": "GBP",
                "current_price": 98.75,
                "current_value": 9875.00,
                "unrealized_gain": 325.00,
                "unrealized_gain_percentage": 3.40,
                "asset_class": "EQUITY",
                "region": "GLOBAL",
                "sector": "Diversified",
                "last_price_update": "2024-01-20T10:30:00",
                "deleted": False,
                "created_at": "2024-01-15T09:00:00",
                "updated_at": "2024-01-20T10:30:00"
            }
        }


class UpdatePriceRequest(BaseModel):
    """
    Schema for updating holding current price.

    Validates:
    - Non-negative price
    """

    current_price: Decimal = Field(
        ...,
        ge=0,
        description="New current price per share/unit"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "current_price": 98.75
            }
        }


class SellHoldingRequest(BaseModel):
    """
    Schema for selling a holding.

    Validates:
    - Positive quantity
    - Non-negative sale price
    - Valid sale date
    """

    quantity: Decimal = Field(
        ...,
        gt=0,
        description="Quantity to sell (must be positive)"
    )

    sale_price: Decimal = Field(
        ...,
        ge=0,
        description="Sale price per share/unit"
    )

    sale_date: date = Field(
        ...,
        description="Date of sale"
    )

    @field_validator('sale_date')
    @classmethod
    def validate_sale_date(cls, v: date) -> date:
        """Ensure sale date is not in the future."""
        if v > date.today():
            raise ValueError("Sale date cannot be in the future")
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "quantity": 50,
                "sale_price": 102.00,
                "sale_date": "2024-02-15"
            }
        }


class SellHoldingResponse(BaseModel):
    """
    Schema for sell holding response.

    Includes:
    - Sale details
    - Realized gain/loss
    - Tax year
    - Remaining quantity
    """

    holding_id: str
    quantity_sold: float
    sale_price: float
    sale_value: float
    cost_basis: float
    realized_gain: float
    tax_year: str
    remaining_quantity: float
    capital_gain_id: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "holding_id": "770e8400-e29b-41d4-a716-446655440000",
                "quantity_sold": 50,
                "sale_price": 102.00,
                "sale_value": 5100.00,
                "cost_basis": 4775.00,
                "realized_gain": 325.00,
                "tax_year": "2024/25",
                "remaining_quantity": 50,
                "capital_gain_id": "880e8400-e29b-41d4-a716-446655440000"
            }
        }


# ============================================================================
# DIVIDEND SCHEMAS
# ============================================================================

class RecordDividendRequest(BaseModel):
    """
    Schema for recording a dividend payment.

    Validates:
    - Holding ID and payment date
    - Positive dividend amount
    - Tax withheld validation
    """

    holding_id: UUID = Field(
        ...,
        description="Holding UUID"
    )

    payment_date: date = Field(
        ...,
        description="Date dividend was paid"
    )

    amount: Decimal = Field(
        ...,
        gt=0,
        description="Gross dividend amount (must be positive)"
    )

    currency: str = Field(
        ...,
        pattern="^(GBP|ZAR|USD|EUR)$",
        description="Currency of dividend"
    )

    tax_withheld: Decimal = Field(
        default=Decimal('0.00'),
        ge=0,
        description="Tax withheld at source"
    )

    country_of_source: SourceCountry = Field(
        default=SourceCountry.UK,
        description="Country where dividend originated"
    )

    ex_dividend_date: Optional[date] = Field(
        None,
        description="Ex-dividend date (optional)"
    )

    @model_validator(mode='after')
    def validate_tax_withheld(self):
        """Ensure tax withheld does not exceed dividend amount."""
        if self.tax_withheld > self.amount:
            raise ValueError("Tax withheld cannot exceed dividend amount")
        return self

    @field_validator('payment_date')
    @classmethod
    def validate_payment_date(cls, v: date) -> date:
        """Ensure payment date is not in the future."""
        if v > date.today():
            raise ValueError("Payment date cannot be in the future")
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "holding_id": "770e8400-e29b-41d4-a716-446655440000",
                "payment_date": "2024-03-31",
                "amount": 125.50,
                "currency": "GBP",
                "tax_withheld": 0.00,
                "country_of_source": "UK"
            }
        }


class DividendResponse(BaseModel):
    """
    Schema for dividend record API response.

    Includes:
    - All dividend details
    - Net dividend calculation
    - Tax year assignments
    """

    id: UUID
    holding_id: UUID

    payment_date: date
    ex_dividend_date: Optional[date] = None

    dividend_per_share: Decimal
    total_dividend_gross: Decimal
    withholding_tax: Decimal
    total_dividend_net: Decimal

    currency: str
    source_country: SourceCountry

    uk_tax_year: str
    sa_tax_year: str

    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "990e8400-e29b-41d4-a716-446655440000",
                "holding_id": "770e8400-e29b-41d4-a716-446655440000",
                "payment_date": "2024-03-31",
                "ex_dividend_date": "2024-03-15",
                "dividend_per_share": 1.255,
                "total_dividend_gross": 125.50,
                "withholding_tax": 0.00,
                "total_dividend_net": 125.50,
                "currency": "GBP",
                "source_country": "UK",
                "uk_tax_year": "2023/24",
                "sa_tax_year": "2023/2024",
                "created_at": "2024-03-31T10:00:00"
            }
        }


# ============================================================================
# PORTFOLIO ANALYSIS SCHEMAS
# ============================================================================

class TopHolding(BaseModel):
    """
    Schema for a top holding in portfolio summary.

    Includes holding details and portfolio percentage.
    """

    id: str
    security_name: str
    ticker: Optional[str] = None
    quantity: Decimal
    current_price: Decimal
    current_value: Decimal
    unrealized_gain: Decimal
    unrealized_gain_percentage: Decimal
    asset_class: str
    region: str
    percentage_of_portfolio: Decimal

    class Config:
        from_attributes = True


class AllocationItem(BaseModel):
    """
    Schema for an allocation item (value and percentage).
    """

    value: Decimal
    percentage: Decimal

    class Config:
        from_attributes = True


class PortfolioSummaryResponse(BaseModel):
    """
    Schema for comprehensive portfolio summary.

    Includes:
    - Total portfolio value and unrealized gains
    - Number of holdings and accounts
    - Currency exposure breakdown
    - Asset allocation breakdown
    - Top 10 holdings
    """

    total_value: Decimal = Field(
        ...,
        description="Total portfolio value across all holdings"
    )

    total_cost_basis: Decimal = Field(
        ...,
        description="Total cost basis (sum of purchase prices)"
    )

    total_unrealized_gain: Decimal = Field(
        ...,
        description="Total unrealized gains/losses"
    )

    unrealized_gain_percentage: Decimal = Field(
        ...,
        description="Unrealized gain as percentage of cost basis"
    )

    num_holdings: int = Field(
        ...,
        description="Number of holdings in portfolio"
    )

    num_accounts: int = Field(
        ...,
        description="Number of investment accounts"
    )

    currency_exposure: Dict[str, AllocationItem] = Field(
        ...,
        description="Currency exposure breakdown"
    )

    asset_allocation: Dict[str, AllocationItem] = Field(
        ...,
        description="Asset allocation breakdown by asset class"
    )

    top_holdings: List[TopHolding] = Field(
        ...,
        description="Top 10 holdings by value"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "total_value": 83333.33,
                "total_cost_basis": 80000.00,
                "total_unrealized_gain": 3333.33,
                "unrealized_gain_percentage": 4.17,
                "num_holdings": 5,
                "num_accounts": 2,
                "currency_exposure": {
                    "GBP": {"value": 50000.00, "percentage": 60.00},
                    "USD": {"value": 33333.33, "percentage": 40.00}
                },
                "asset_allocation": {
                    "EQUITY": {"value": 50000.00, "percentage": 60.00},
                    "FIXED_INCOME": {"value": 20000.00, "percentage": 24.00},
                    "CASH": {"value": 13333.33, "percentage": 16.00}
                },
                "top_holdings": []
            }
        }


class AllocationResponse(BaseModel):
    """
    Schema for asset/region/sector allocation response.

    Returns allocation percentages as a dictionary.
    """

    allocation: Dict[str, AllocationItem] = Field(
        ...,
        description="Allocation breakdown with values and percentages"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "allocation": {
                    "EQUITY": {"value": 50000.00, "percentage": 60.00},
                    "FIXED_INCOME": {"value": 20000.00, "percentage": 24.00},
                    "CASH": {"value": 13333.33, "percentage": 16.00}
                }
            }
        }


class PerformanceResponse(BaseModel):
    """
    Schema for portfolio performance metrics.

    Includes:
    - Total portfolio value
    - Total cost basis
    - Unrealized gains
    - Dividend income (YTD and all-time)
    """

    total_value: Decimal = Field(
        ...,
        description="Total portfolio value"
    )

    total_cost_basis: Decimal = Field(
        ...,
        description="Total cost basis (sum of purchase prices)"
    )

    total_unrealized_gain: Decimal = Field(
        ...,
        description="Total unrealized gains/losses"
    )

    unrealized_gain_percentage: Decimal = Field(
        ...,
        description="Unrealized gain as percentage of cost basis"
    )

    ytd_dividend_income: Decimal = Field(
        ...,
        description="Year-to-date dividend income (current tax year)"
    )

    total_dividend_income: Decimal = Field(
        ...,
        description="Total dividend income (all time)"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "total_value": 83333.33,
                "total_cost_basis": 80000.00,
                "total_unrealized_gain": 3333.33,
                "unrealized_gain_percentage": 4.17,
                "ytd_dividend_income": 500.00,
                "total_dividend_income": 2500.00
            }
        }


class CapitalGainsTaxUK(BaseModel):
    """
    Schema for UK capital gains tax calculation.
    """

    total_gains: Decimal = Field(
        ...,
        description="Total realized gains (ISA + GIA)"
    )

    exempt_amount: Decimal = Field(
        ...,
        description="Annual exempt amount used (CGT allowance)"
    )

    taxable_gains: Decimal = Field(
        ...,
        description="Gains above exemption (taxable)"
    )

    tax_rate: Decimal = Field(
        ...,
        description="Tax rate applied"
    )

    tax_owed: Decimal = Field(
        ...,
        description="Total CGT owed"
    )

    isa_gains_tax_free: Decimal = Field(
        ...,
        description="Gains from ISA accounts (tax-free)"
    )

    class Config:
        from_attributes = True


class DividendTaxUK(BaseModel):
    """
    Schema for UK dividend tax calculation.
    """

    total_dividends: Decimal = Field(
        ...,
        description="Total dividend income (ISA + GIA)"
    )

    allowance: Decimal = Field(
        ...,
        description="Dividend allowance used"
    )

    taxable_dividends: Decimal = Field(
        ...,
        description="Dividends above allowance (taxable)"
    )

    tax_rate: Decimal = Field(
        ...,
        description="Tax rate applied"
    )

    tax_owed: Decimal = Field(
        ...,
        description="Total dividend tax owed"
    )

    isa_dividends_tax_free: Decimal = Field(
        ...,
        description="Dividends from ISA accounts (tax-free)"
    )

    class Config:
        from_attributes = True


class CapitalGainsTaxSA(BaseModel):
    """
    Schema for SA capital gains tax calculation.
    """

    total_gains: Decimal = Field(
        ...,
        description="Total realized gains"
    )

    inclusion_rate: Decimal = Field(
        ...,
        description="Inclusion rate (40%)"
    )

    included_gain: Decimal = Field(
        ...,
        description="Gain included in taxable income"
    )

    tax_rate: Decimal = Field(
        ...,
        description="Effective tax rate"
    )

    tax_owed: Decimal = Field(
        ...,
        description="Total CGT owed"
    )

    class Config:
        from_attributes = True


class DividendTaxSA(BaseModel):
    """
    Schema for SA dividend withholding tax calculation.
    """

    total_dividends: Decimal = Field(
        ...,
        description="Total dividend income"
    )

    withholding_rate: Decimal = Field(
        ...,
        description="Withholding tax rate (20%)"
    )

    tax_withheld: Decimal = Field(
        ...,
        description="Total tax withheld"
    )

    class Config:
        from_attributes = True


class TaxGainsResponse(BaseModel):
    """
    Schema for capital gains and dividend tax response.

    Includes separate calculations for capital gains and dividends.
    """

    capital_gains: CapitalGainsTaxUK | CapitalGainsTaxSA = Field(
        ...,
        description="Capital gains tax calculation"
    )

    dividend_tax: DividendTaxUK | DividendTaxSA = Field(
        ...,
        description="Dividend tax calculation"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "capital_gains": {
                    "total_gains": 15000.00,
                    "exempt_amount": 3000.00,
                    "taxable_gains": 12000.00,
                    "tax_rate": 0.20,
                    "tax_owed": 2400.00,
                    "isa_gains_tax_free": 5000.00
                },
                "dividend_tax": {
                    "total_dividends": 3000.00,
                    "allowance": 500.00,
                    "taxable_dividends": 2500.00,
                    "tax_rate": 0.0875,
                    "tax_owed": 218.75,
                    "isa_dividends_tax_free": 1000.00
                }
            }
        }
