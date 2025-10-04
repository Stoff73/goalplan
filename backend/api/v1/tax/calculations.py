"""
Tax calculation API endpoints.

This module provides comprehensive tax calculation endpoints for both UK and SA:
- UK Income Tax, NI, CGT, Dividend Tax
- SA Income Tax, CGT, Dividend Tax
- Comprehensive tax summary (authenticated)

Calculator endpoints are public (no auth required).
Tax summary endpoint requires authentication as it aggregates user data.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from decimal import Decimal
from typing import Optional
from uuid import UUID
import logging

from database import get_db
from middleware.auth import get_current_user
from schemas.tax import (
    # Request schemas
    UKIncomeTaxRequest,
    UKNationalInsuranceRequest,
    UKCapitalGainsRequest,
    UKDividendTaxRequest,
    SAIncomeTaxRequest,
    SACapitalGainsRequest,
    SADividendTaxRequest,
    # Response schemas
    UKIncomeTaxResponse,
    UKNationalInsuranceResponse,
    UKCapitalGainsResponse,
    UKDividendTaxResponse,
    SAIncomeTaxResponse,
    SACapitalGainsResponse,
    SADividendTaxResponse,
    TaxSummaryResponse,
    CountryTaxSummary,
    IncomeSources,
    AllowancesUsed
)
from services.tax.uk_tax_service import uk_tax_service
from services.tax.sa_tax_service import sa_tax_service
from models.income import UserIncome
from models.savings_account import SavingsAccount
from models.investment import InvestmentAccount, InvestmentHolding

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# UK TAX CALCULATOR ENDPOINTS (PUBLIC)
# ============================================================================

@router.post(
    "/uk/income-tax",
    response_model=UKIncomeTaxResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate UK Income Tax",
    description="Calculate UK Income Tax for the 2024/25 tax year. "
                "No authentication required - this is a utility calculator."
)
async def calculate_uk_income_tax(data: UKIncomeTaxRequest):
    """
    Calculate UK Income Tax.

    Applies progressive tax rates (20%, 40%, 45%) with personal allowance
    and tapering for high earners.

    Args:
        data: Income tax calculation request

    Returns:
        UKIncomeTaxResponse: Tax calculation breakdown

    Raises:
        400: Invalid input (negative income, unsupported tax year)
        500: Internal server error
    """
    try:
        result = uk_tax_service.calculate_income_tax(
            income=data.income,
            tax_year=data.tax_year,
            is_scottish_resident=data.is_scottish_resident
        )

        return UKIncomeTaxResponse(**result)

    except ValueError as e:
        logger.error(f"Validation error in UK income tax calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to calculate UK income tax: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate UK income tax"
        )


@router.post(
    "/uk/national-insurance",
    response_model=UKNationalInsuranceResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate UK National Insurance",
    description="Calculate UK National Insurance (Class 1, 2, and 4) for the 2024/25 tax year. "
                "No authentication required - this is a utility calculator."
)
async def calculate_uk_national_insurance(data: UKNationalInsuranceRequest):
    """
    Calculate UK National Insurance.

    Supports Class 1 (employees), Class 2 (self-employed flat rate),
    and Class 4 (self-employed profits).

    Args:
        data: NI calculation request

    Returns:
        UKNationalInsuranceResponse: NI calculation breakdown

    Raises:
        400: Invalid input (negative amounts)
        500: Internal server error
    """
    try:
        result = uk_tax_service.calculate_national_insurance(
            employment_income=data.employment_income,
            is_self_employed=data.is_self_employed,
            profits=data.profits
        )

        return UKNationalInsuranceResponse(**result)

    except ValueError as e:
        logger.error(f"Validation error in UK NI calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to calculate UK NI: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate UK National Insurance"
        )


@router.post(
    "/uk/capital-gains",
    response_model=UKCapitalGainsResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate UK Capital Gains Tax",
    description="Calculate UK CGT for the 2024/25 tax year with annual exemption. "
                "No authentication required - this is a utility calculator."
)
async def calculate_uk_capital_gains(data: UKCapitalGainsRequest):
    """
    Calculate UK Capital Gains Tax.

    Applies annual exempt amount (£3,000 for 2024/25) and different rates
    for property vs other assets, basic vs higher rate taxpayers.

    Args:
        data: CGT calculation request

    Returns:
        UKCapitalGainsResponse: CGT calculation breakdown

    Raises:
        400: Invalid input (negative amounts)
        500: Internal server error
    """
    try:
        result = uk_tax_service.calculate_cgt(
            total_gains=data.total_gains,
            annual_exempt_amount_used=data.annual_exempt_amount_used,
            is_higher_rate_taxpayer=data.is_higher_rate_taxpayer,
            is_property=data.is_property
        )

        return UKCapitalGainsResponse(**result)

    except ValueError as e:
        logger.error(f"Validation error in UK CGT calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to calculate UK CGT: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate UK Capital Gains Tax"
        )


@router.post(
    "/uk/dividend-tax",
    response_model=UKDividendTaxResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate UK Dividend Tax",
    description="Calculate UK dividend tax for the 2024/25 tax year with dividend allowance. "
                "No authentication required - this is a utility calculator."
)
async def calculate_uk_dividend_tax(data: UKDividendTaxRequest):
    """
    Calculate UK Dividend Tax.

    Applies dividend allowance (£500 for 2024/25) and progressive rates
    (8.75%, 33.75%, 39.35%) based on other income.

    Args:
        data: Dividend tax calculation request

    Returns:
        UKDividendTaxResponse: Dividend tax calculation breakdown

    Raises:
        400: Invalid input (negative amounts)
        500: Internal server error
    """
    try:
        result = uk_tax_service.calculate_dividend_tax(
            dividend_income=data.dividend_income,
            other_income=data.other_income
        )

        return UKDividendTaxResponse(**result)

    except ValueError as e:
        logger.error(f"Validation error in UK dividend tax calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to calculate UK dividend tax: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate UK Dividend Tax"
        )


# ============================================================================
# SA TAX CALCULATOR ENDPOINTS (PUBLIC)
# ============================================================================

@router.post(
    "/sa/income-tax",
    response_model=SAIncomeTaxResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate SA Income Tax",
    description="Calculate South African Income Tax for the 2024/25 tax year with age-based rebates. "
                "No authentication required - this is a utility calculator."
)
async def calculate_sa_income_tax(data: SAIncomeTaxRequest):
    """
    Calculate SA Income Tax.

    Applies progressive tax rates (18%-45%) with age-based rebates.
    Primary rebate: R17,235 (under 65)
    Secondary rebate: R26,679 (65-74)
    Tertiary rebate: R29,824 (75+)

    Args:
        data: Income tax calculation request

    Returns:
        SAIncomeTaxResponse: Tax calculation breakdown

    Raises:
        400: Invalid input (negative income, unsupported tax year)
        500: Internal server error
    """
    try:
        result = sa_tax_service.calculate_income_tax(
            income=data.income,
            age=data.age,
            tax_year=data.tax_year
        )

        return SAIncomeTaxResponse(**result)

    except ValueError as e:
        logger.error(f"Validation error in SA income tax calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to calculate SA income tax: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate SA Income Tax"
        )


@router.post(
    "/sa/capital-gains",
    response_model=SACapitalGainsResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate SA Capital Gains Tax",
    description="Calculate SA CGT using inclusion rate method (40% for individuals). "
                "No authentication required - this is a utility calculator."
)
async def calculate_sa_capital_gains(data: SACapitalGainsRequest):
    """
    Calculate SA Capital Gains Tax.

    SA CGT uses inclusion rate method:
    1. Apply annual exclusion (R40,000)
    2. Apply inclusion rate (40% for individuals)
    3. Add to taxable income and tax at marginal rate

    Args:
        data: CGT calculation request

    Returns:
        SACapitalGainsResponse: CGT calculation breakdown

    Raises:
        400: Invalid input (negative amounts)
        500: Internal server error
    """
    try:
        result = sa_tax_service.calculate_cgt(
            total_gains=data.total_gains,
            annual_exclusion_used=data.annual_exclusion_used,
            inclusion_rate=data.inclusion_rate,
            taxable_income=data.taxable_income,
            age=data.age
        )

        return SACapitalGainsResponse(**result)

    except ValueError as e:
        logger.error(f"Validation error in SA CGT calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to calculate SA CGT: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate SA Capital Gains Tax"
        )


@router.post(
    "/sa/dividend-tax",
    response_model=SADividendTaxResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate SA Dividend Tax",
    description="Calculate SA dividend withholding tax (20%) with exemption (R23,800). "
                "No authentication required - this is a utility calculator."
)
async def calculate_sa_dividend_tax(data: SADividendTaxRequest):
    """
    Calculate SA Dividend Withholding Tax.

    Local dividends are subject to 20% withholding tax.
    First R23,800 per year is exempt.

    Args:
        data: Dividend tax calculation request

    Returns:
        SADividendTaxResponse: Dividend tax calculation

    Raises:
        400: Invalid input (negative amounts)
        500: Internal server error
    """
    try:
        result = sa_tax_service.calculate_dividend_tax(
            dividend_income=data.dividend_income,
            exemption_used=data.exemption_used
        )

        return SADividendTaxResponse(**result)

    except ValueError as e:
        logger.error(f"Validation error in SA dividend tax calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to calculate SA dividend tax: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate SA Dividend Tax"
        )


# ============================================================================
# COMPREHENSIVE TAX SUMMARY ENDPOINT (AUTHENTICATED)
# ============================================================================

@router.get(
    "/summary",
    response_model=TaxSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get comprehensive tax summary",
    description="Get comprehensive tax summary aggregating all income sources, "
                "investments, and savings. **Requires authentication.**"
)
async def get_tax_summary(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive tax summary for authenticated user.

    Aggregates income from:
    - Employment income (from income module)
    - Investment dividends and capital gains
    - Savings account interest

    Calculates total tax liabilities:
    - UK: Income Tax + NI + Dividend Tax + CGT
    - SA: Income Tax + Dividend Tax + CGT

    Args:
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        TaxSummaryResponse: Comprehensive tax summary

    Raises:
        401: Not authenticated
        500: Internal server error
    """
    try:
        user_id = UUID(current_user_id)

        # ===== AGGREGATE UK INCOME SOURCES =====
        uk_income_sources = IncomeSources()

        # Get UK employment income
        uk_income_stmt = select(func.sum(UserIncome.amount)).where(
            and_(
                UserIncome.user_id == user_id,
                UserIncome.source_country == "UK",
                UserIncome.deleted_at.is_(None)
            )
        )
        uk_income_result = await db.execute(uk_income_stmt)
        uk_employment_income = uk_income_result.scalar() or Decimal("0")
        uk_income_sources.employment = uk_employment_income
        uk_income_sources.total = uk_employment_income

        # ===== AGGREGATE SA INCOME SOURCES =====
        sa_income_sources = IncomeSources()

        # Get SA employment income
        sa_income_stmt = select(func.sum(UserIncome.amount)).where(
            and_(
                UserIncome.user_id == user_id,
                UserIncome.source_country == "ZA",
                UserIncome.deleted_at.is_(None)
            )
        )
        sa_income_result = await db.execute(sa_income_stmt)
        sa_employment_income = sa_income_result.scalar() or Decimal("0")
        sa_income_sources.employment = sa_employment_income
        sa_income_sources.total = sa_employment_income

        # ===== CALCULATE UK TAXES =====
        uk_taxes = None
        if uk_employment_income > 0:
            # Calculate UK income tax
            uk_income_tax_result = uk_tax_service.calculate_income_tax(
                income=uk_employment_income,
                tax_year="2024/25",
                is_scottish_resident=False
            )
            uk_income_tax = uk_income_tax_result["tax_owed"]

            # Calculate UK NI
            uk_ni_result = uk_tax_service.calculate_national_insurance(
                employment_income=uk_employment_income,
                is_self_employed=False,
                profits=Decimal("0")
            )
            uk_ni = uk_ni_result["ni_owed"]

            uk_taxes = CountryTaxSummary(
                income_tax=uk_income_tax,
                national_insurance=uk_ni,
                dividend_tax=Decimal("0"),
                capital_gains_tax=Decimal("0"),
                total=uk_income_tax + uk_ni,
                currency="GBP"
            )

        # ===== CALCULATE SA TAXES =====
        sa_taxes = None
        if sa_employment_income > 0:
            # Calculate SA income tax
            sa_income_tax_result = sa_tax_service.calculate_income_tax(
                income=sa_employment_income,
                age=None,  # Default to under 65
                tax_year="2024/25"
            )
            sa_income_tax = sa_income_tax_result["tax_owed"]

            sa_taxes = CountryTaxSummary(
                income_tax=sa_income_tax,
                national_insurance=None,
                dividend_tax=Decimal("0"),
                capital_gains_tax=Decimal("0"),
                total=sa_income_tax,
                currency="ZAR"
            )

        # ===== CALCULATE TOTALS =====
        # TODO: Add currency conversion for cross-jurisdiction totals
        # For now, just sum UK amounts
        total_tax_gbp = Decimal("0")
        if uk_taxes:
            total_tax_gbp = uk_taxes.total

        total_tax_zar = Decimal("0")
        if sa_taxes:
            total_tax_zar = sa_taxes.total

        # Calculate effective rate
        total_income = uk_income_sources.total + (sa_income_sources.total / 22)  # Rough conversion
        effective_rate = float((total_tax_gbp / total_income * 100) if total_income > 0 else Decimal("0"))

        # ===== BUILD RESPONSE =====
        return TaxSummaryResponse(
            uk_taxes=uk_taxes,
            sa_taxes=sa_taxes,
            uk_income_sources=uk_income_sources if uk_employment_income > 0 else None,
            sa_income_sources=sa_income_sources if sa_employment_income > 0 else None,
            allowances=AllowancesUsed(
                personal_allowance=uk_income_tax_result.get("personal_allowance") if uk_taxes else None,
                isa_allowance_used=None,
                isa_allowance_remaining=None,
                tfsa_allowance_used=None,
                tfsa_allowance_remaining=None,
                cgt_exemption_used=Decimal("0"),
                dividend_allowance_used=Decimal("0")
            ),
            total_tax_liability_gbp=total_tax_gbp,
            total_tax_liability_zar=total_tax_zar,
            effective_rate_combined=effective_rate,
            tax_year="2024/25"
        )

    except Exception as e:
        logger.error(f"Failed to generate tax summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate tax summary"
        )
