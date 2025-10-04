"""
DTA Relief API Endpoints

This module provides API endpoints for UK-SA Double Tax Agreement relief calculations.

Endpoints:
- POST /employment-income: Employment income relief
- POST /dividends: Dividend relief
- POST /interest: Interest relief
- POST /capital-gains: Capital gains relief
- POST /pensions: Pension relief
- POST /tie-breaker: Tie-breaker rules for dual residents
"""

from fastapi import APIRouter, HTTPException, status
from decimal import Decimal
from typing import Dict

from schemas.tax import (
    DTAEmploymentIncomeRequest,
    DTAEmploymentIncomeResponse,
    DTADividendRequest,
    DTADividendResponse,
    DTAInterestRequest,
    DTAInterestResponse,
    DTACapitalGainsRequest,
    DTACapitalGainsResponse,
    DTAPensionRequest,
    DTAPensionResponse,
    DTATieBreakerRequest,
    DTATieBreakerResponse,
)
from services.tax.dta_service import dta_service


router = APIRouter()


@router.post(
    "/employment-income",
    response_model=DTAEmploymentIncomeResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate DTA relief for employment income",
    description="Calculate UK-SA Double Tax Agreement relief for employment income across both jurisdictions"
)
async def calculate_employment_income_relief(
    request: DTAEmploymentIncomeRequest
) -> DTAEmploymentIncomeResponse:
    """
    Calculate DTA relief for employment income.

    Rules:
    - If UK resident earning SA income: SA taxes first, UK gives foreign tax credit
    - If SA resident earning UK income: UK taxes first, SA gives foreign tax credit
    - If dual resident: Apply tie-breaker rules
    """
    try:
        result = dta_service.calculate_employment_income_relief(
            uk_income=request.uk_income,
            sa_income=request.sa_income,
            uk_resident=request.uk_resident,
            sa_resident=request.sa_resident
        )

        return DTAEmploymentIncomeResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating employment income relief: {str(e)}"
        )


@router.post(
    "/dividends",
    response_model=DTADividendResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate DTA relief for dividends",
    description="Calculate UK-SA DTA relief for dividend income with 15% withholding limit"
)
async def calculate_dividend_relief(
    request: DTADividendRequest
) -> DTADividendResponse:
    """
    Calculate DTA relief for dividend income.

    Rules:
    - UK-SA DTA: 15% withholding limit
    - Source country withholds tax
    - Residence country gives credit for withholding
    """
    try:
        result = dta_service.calculate_dividend_relief(
            dividend_amount=request.dividend_amount,
            source_country=request.source_country,
            residence_country=request.residence_country,
            withholding_rate=request.withholding_rate
        )

        return DTADividendResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating dividend relief: {str(e)}"
        )


@router.post(
    "/interest",
    response_model=DTAInterestResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate DTA relief for interest",
    description="Calculate UK-SA DTA relief for interest income (0% withholding)"
)
async def calculate_interest_relief(
    request: DTAInterestRequest
) -> DTAInterestResponse:
    """
    Calculate DTA relief for interest income.

    Rules:
    - UK-SA DTA: 0% withholding on interest
    - Taxed only in residence country
    """
    try:
        result = dta_service.calculate_interest_relief(
            interest_amount=request.interest_amount,
            source_country=request.source_country,
            residence_country=request.residence_country
        )

        return DTAInterestResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating interest relief: {str(e)}"
        )


@router.post(
    "/capital-gains",
    response_model=DTACapitalGainsResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate DTA relief for capital gains",
    description="Calculate UK-SA DTA relief for capital gains based on asset type and location"
)
async def calculate_capital_gains_relief(
    request: DTACapitalGainsRequest
) -> DTACapitalGainsResponse:
    """
    Calculate DTA relief for capital gains.

    Rules:
    - Immovable property: Taxed where property located
    - Business property: Taxed where PE located
    - Shares/securities: Taxed in residence country (unless >50% immovable property)
    """
    try:
        result = dta_service.calculate_capital_gains_relief(
            gain_amount=request.gain_amount,
            asset_type=request.asset_type,
            asset_location=request.asset_location,
            residence_country=request.residence_country
        )

        return DTACapitalGainsResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating capital gains relief: {str(e)}"
        )


@router.post(
    "/pensions",
    response_model=DTAPensionResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate DTA relief for pensions",
    description="Calculate UK-SA DTA relief for pension income (private vs government)"
)
async def calculate_pension_relief(
    request: DTAPensionRequest
) -> DTAPensionResponse:
    """
    Calculate DTA relief for pension income.

    Rules:
    - Private pensions: Taxed in residence country
    - Government pensions: Taxed in source country (paying government)
    """
    try:
        result = dta_service.calculate_pension_relief(
            pension_amount=request.pension_amount,
            pension_type=request.pension_type,
            source_country=request.source_country,
            residence_country=request.residence_country
        )

        return DTAPensionResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating pension relief: {str(e)}"
        )


@router.post(
    "/tie-breaker",
    response_model=DTATieBreakerResponse,
    status_code=status.HTTP_200_OK,
    summary="Apply DTA tie-breaker rules",
    description="Determine sole residence for dual residents using DTA tie-breaker cascade"
)
async def apply_tie_breaker_rules(
    request: DTATieBreakerRequest
) -> DTATieBreakerResponse:
    """
    Apply DTA tie-breaker rules for dual residents.

    Rules cascade in order:
    1. Permanent home (if only in one country)
    2. Centre of vital interests (family, economic ties)
    3. Habitual abode (where normally lives)
    4. Nationality
    """
    try:
        result = dta_service.apply_tie_breaker_rules(
            has_uk_home=request.has_uk_home,
            has_sa_home=request.has_sa_home,
            uk_vital_interests=request.uk_vital_interests,
            sa_vital_interests=request.sa_vital_interests,
            uk_habitual_abode=request.uk_habitual_abode,
            sa_habitual_abode=request.sa_habitual_abode,
            nationality=request.nationality
        )

        return DTATieBreakerResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error applying tie-breaker rules: {str(e)}"
        )
