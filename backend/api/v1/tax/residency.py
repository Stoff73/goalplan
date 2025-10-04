"""
Tax Residency API Endpoints

This module provides API endpoints for UK and SA tax residency determinations.

Endpoints:
- POST /uk-srt: UK Statutory Residence Test
- POST /sa-presence: SA Physical Presence Test
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict

from schemas.tax import (
    UKSRTRequest,
    UKSRTResponse,
    SAPresenceRequest,
    SAPresenceResponse,
)
from services.tax.uk_srt_service import uk_srt_service
from services.tax.sa_presence_service import sa_presence_service


router = APIRouter()


@router.post(
    "/uk-srt",
    response_model=UKSRTResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate UK Statutory Residence Test",
    description="Determine UK tax residence status using the Statutory Residence Test (SRT) with automatic tests and sufficient ties"
)
async def calculate_uk_srt(
    request: UKSRTRequest
) -> UKSRTResponse:
    """
    Calculate UK tax residence using Statutory Residence Test.

    Tests applied in order:
    1. Automatic Overseas Test (if passes: not resident)
    2. Automatic UK Test (if passes: resident)
    3. Sufficient Ties Test (based on days and ties)
    """
    try:
        # Prepare ties data
        ties_data = uk_srt_service.calculate_uk_ties(
            has_family=request.has_family,
            has_accommodation=request.has_accommodation,
            accommodation_days=request.accommodation_days,
            work_days=request.work_days,
            prior_year_days=request.prior_year_days,
            is_leaver=any(request.prior_residence) if request.prior_residence else False,
            days_in_other_countries=request.days_in_other_countries
        )

        # Prepare work status data
        work_status = {
            "full_time_work_abroad": request.full_time_work_abroad,
            "uk_days_while_working_abroad": request.uk_days_while_working_abroad,
            "has_uk_home": request.has_uk_home,
            "days_at_uk_home": request.days_at_uk_home,
            "full_time_work_uk": request.full_time_work_uk,
            "days_in_other_countries": request.days_in_other_countries or {}
        }

        # Calculate UK residence
        result = uk_srt_service.calculate_uk_residence(
            days_in_uk=request.days_in_uk,
            ties=ties_data,
            prior_residence=request.prior_residence,
            work_status=work_status
        )

        return UKSRTResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating UK SRT: {str(e)}"
        )


@router.post(
    "/sa-presence",
    response_model=SAPresenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate SA Physical Presence Test",
    description="Determine SA tax residence status using the physical presence test (91 days current year + 5 year average)"
)
async def calculate_sa_presence(
    request: SAPresenceRequest
) -> SAPresenceResponse:
    """
    Calculate SA tax residence using physical presence test.

    Requirements:
    - Ordinarily resident (traditional home in SA), OR
    - >=91 days in current year AND
    - >=91 days in each of prior 5 years AND
    - >=915 days total in prior 5 years
    """
    try:
        result = sa_presence_service.calculate_sa_residence(
            days_current_year=request.days_current_year,
            days_prior_years=request.days_prior_years,
            ordinarily_resident=request.ordinarily_resident
        )

        return SAPresenceResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating SA presence test: {str(e)}"
        )
