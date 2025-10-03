"""
Pydantic schemas for dashboard API endpoints.

This module provides request/response models for:
- Net worth summary
- Breakdowns by country, asset class, and currency
- Trend data for charts
- Change calculations (day, month, year)

All schemas match the specification from CentralDashboard.md
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date, datetime
from decimal import Decimal


class BreakdownItem(BaseModel):
    """Schema for breakdown items (country, asset class, or currency)."""

    category: str = Field(..., description="Category name (e.g., 'UK', 'Cash', 'GBP')")
    amount: Decimal = Field(..., description="Amount in base currency")
    percentage: float = Field(..., ge=0, le=100, description="Percentage of total")

    model_config = {
        "json_schema_extra": {
            "example": {
                "category": "UK",
                "amount": 250000.00,
                "percentage": 76.9
            }
        }
    }


class CountryBreakdownItem(BaseModel):
    """Schema for country breakdown items."""

    country: str = Field(..., description="Country code (e.g., 'UK', 'SA')")
    amount: Decimal = Field(..., description="Amount in base currency")
    percentage: float = Field(..., ge=0, le=100, description="Percentage of total")

    model_config = {
        "json_schema_extra": {
            "example": {
                "country": "UK",
                "amount": 250000.00,
                "percentage": 76.9
            }
        }
    }


class AssetClassBreakdownItem(BaseModel):
    """Schema for asset class breakdown items."""

    assetClass: str = Field(..., description="Asset class (e.g., 'Cash', 'Property', 'Pensions')")
    amount: Decimal = Field(..., description="Amount in base currency")
    percentage: float = Field(..., ge=0, le=100, description="Percentage of total")

    model_config = {
        "json_schema_extra": {
            "example": {
                "assetClass": "Cash",
                "amount": 50000.00,
                "percentage": 15.4
            }
        }
    }


class CurrencyBreakdownItem(BaseModel):
    """Schema for currency breakdown items."""

    currency: str = Field(..., description="Currency code (e.g., 'GBP', 'ZAR')")
    amount: Decimal = Field(..., description="Amount in base currency")
    percentage: float = Field(..., ge=0, le=100, description="Percentage of total exposure")

    model_config = {
        "json_schema_extra": {
            "example": {
                "currency": "GBP",
                "amount": 250000.00,
                "percentage": 76.9
            }
        }
    }


class TrendDataPoint(BaseModel):
    """Schema for trend data point."""

    date: str = Field(..., description="Date of snapshot (ISO format)")
    netWorth: Decimal = Field(..., description="Net worth on that date")

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2024-11-01",
                "netWorth": 300000.00
            }
        }
    }


class Change(BaseModel):
    """Schema for net worth change over a period."""

    amount: Decimal = Field(..., description="Change amount in base currency")
    percentage: float = Field(..., description="Percentage change")

    model_config = {
        "json_schema_extra": {
            "example": {
                "amount": 5000.00,
                "percentage": 1.56
            }
        }
    }


class Changes(BaseModel):
    """Schema for all change periods."""

    day: Change = Field(..., description="Change over last day")
    month: Change = Field(..., description="Change over last month (30 days)")
    year: Change = Field(..., description="Change over last year (365 days)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "day": {"amount": 1000.00, "percentage": 0.31},
                "month": {"amount": 5000.00, "percentage": 1.56},
                "year": {"amount": 25000.00, "percentage": 8.33}
            }
        }
    }


class NetWorthSummaryResponse(BaseModel):
    """
    Complete net worth summary response.

    This is the main response schema for GET /api/v1/dashboard/net-worth
    and includes all data needed for the dashboard UI.
    """

    netWorth: Decimal = Field(..., description="Total net worth (assets - liabilities)")
    totalAssets: Decimal = Field(..., description="Total assets value")
    totalLiabilities: Decimal = Field(..., description="Total liabilities value")
    baseCurrency: str = Field(..., description="Currency for all amounts")
    asOfDate: str = Field(..., description="Date of calculation (ISO format)")
    lastUpdated: str = Field(..., description="Timestamp of last update (ISO format)")

    breakdownByCountry: List[CountryBreakdownItem] = Field(
        default_factory=list,
        description="Net worth breakdown by country"
    )
    breakdownByAssetClass: List[AssetClassBreakdownItem] = Field(
        default_factory=list,
        description="Net worth breakdown by asset class"
    )
    breakdownByCurrency: List[CurrencyBreakdownItem] = Field(
        default_factory=list,
        description="Currency exposure breakdown"
    )

    trendData: List[TrendDataPoint] = Field(
        default_factory=list,
        description="Historical trend data (last 12 months)"
    )

    changes: Optional[Changes] = Field(
        None,
        description="Net worth changes over different periods"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "netWorth": 325000.00,
                "totalAssets": 425000.00,
                "totalLiabilities": 100000.00,
                "baseCurrency": "GBP",
                "asOfDate": "2025-10-02",
                "lastUpdated": "2025-10-02T14:30:00Z",
                "breakdownByCountry": [
                    {"country": "UK", "amount": 250000.00, "percentage": 76.9},
                    {"country": "SA", "amount": 75000.00, "percentage": 23.1}
                ],
                "breakdownByAssetClass": [
                    {"assetClass": "Cash", "amount": 50000.00, "percentage": 15.4},
                    {"assetClass": "Property", "amount": 300000.00, "percentage": 92.3},
                    {"assetClass": "Pensions", "amount": 75000.00, "percentage": 23.1}
                ],
                "breakdownByCurrency": [
                    {"currency": "GBP", "amount": 250000.00, "percentage": 76.9},
                    {"currency": "ZAR", "amount": 75000.00, "percentage": 23.1}
                ],
                "trendData": [
                    {"date": "2024-11-01", "netWorth": 300000.00},
                    {"date": "2024-12-01", "netWorth": 310000.00}
                ],
                "changes": {
                    "day": {"amount": 1000.00, "percentage": 0.31},
                    "month": {"amount": 5000.00, "percentage": 1.56},
                    "year": {"amount": 25000.00, "percentage": 8.33}
                }
            }
        }
    }
