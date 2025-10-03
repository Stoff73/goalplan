"""
Tax status management API endpoints.

This module provides endpoints for managing user tax status, including:
- CRUD operations for tax status records (temporal data)
- UK Statutory Residence Test calculator
- SA Physical Presence Test calculator
- Deemed domicile calculation

All endpoints require authentication.
"""

from datetime import date
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth import get_current_user
from models.tax_status import UserTaxStatus, UKDomicileStatus
from schemas.tax_status import (
    TaxStatusCreate,
    TaxStatusResponse,
    SRTCalculatorRequest,
    SRTCalculatorResponse,
    SAPresenceTestRequest,
    SAPresenceTestResponse,
    DeemedDomicileResponse
)
from services.deemed_domicile import DeemedDomicileService
from services.srt_calculator import SRTCalculatorService
from services.sa_presence_calculator import SAPresenceCalculatorService


router = APIRouter(prefix="/tax-status", tags=["Tax Status"])


# ===== Tax Status CRUD Endpoints =====

@router.post("", response_model=TaxStatusResponse, status_code=status.HTTP_201_CREATED)
async def create_tax_status(
    data: TaxStatusCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new tax status record.

    Business logic:
    1. Validate no overlapping effective dates
    2. Auto-adjust previous record's effective_to
    3. Calculate deemed domicile if applicable
    4. Store record

    Temporal data management:
    - New record with effective_to=NULL becomes current
    - Previous current record's effective_to is set to new record's effective_from - 1 day
    """
    # Check for overlapping periods
    overlap_query = select(UserTaxStatus).where(
        and_(
            UserTaxStatus.user_id == UUID(current_user_id),
            or_(
                # New record starts before existing record ends
                and_(
                    UserTaxStatus.effective_from <= data.effectiveFrom,
                    or_(
                        UserTaxStatus.effective_to.is_(None),
                        UserTaxStatus.effective_to > data.effectiveFrom
                    )
                ),
                # New record ends after existing record starts
                and_(
                    data.effectiveTo is not None,
                    UserTaxStatus.effective_from < data.effectiveTo,
                    or_(
                        UserTaxStatus.effective_to.is_(None),
                        UserTaxStatus.effective_to > UserTaxStatus.effective_from
                    )
                )
            )
        )
    )

    result = await db.execute(overlap_query)
    overlapping_record = result.scalar_one_or_none()

    if overlapping_record:
        # Auto-adjust previous record's effective_to
        if data.effectiveTo is None:
            # New record is current (no end date)
            # Set previous record's end date to day before new record starts
            from datetime import timedelta
            overlapping_record.effective_to = data.effectiveFrom - timedelta(days=1)
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A tax status record already exists for this period. Please adjust dates."
            )

    # Calculate deemed domicile if UK resident
    deemed_domicile_date = None
    if data.ukTaxResident:
        deemed_domicile_service = DeemedDomicileService(db)
        deemed_domicile_date = await deemed_domicile_service.update_deemed_domicile_status(
            UUID(current_user_id),
            data.effectiveFrom
        )

    # Create new tax status record
    tax_status = UserTaxStatus(
        user_id=UUID(current_user_id),
        effective_from=data.effectiveFrom,
        effective_to=data.effectiveTo,
        uk_tax_resident=data.ukTaxResident,
        uk_domicile=data.ukDomicile,
        uk_deemed_domicile_date=deemed_domicile_date,
        uk_split_year_treatment=data.ukSplitYearTreatment,
        uk_remittance_basis=data.ukRemittanceBasis,
        sa_tax_resident=data.saTaxResident,
        sa_ordinarily_resident=data.saOrdinarilyResident,
        dual_resident=data.dualResident,
        dta_tie_breaker_country=data.dtaTieBreakerCountry
    )

    db.add(tax_status)
    await db.commit()
    await db.refresh(tax_status)

    # Convert to response format
    return TaxStatusResponse(
        id=tax_status.id,
        userId=tax_status.user_id,
        effectiveFrom=tax_status.effective_from,
        effectiveTo=tax_status.effective_to,
        ukTaxResident=tax_status.uk_tax_resident,
        ukDomicile=tax_status.uk_domicile,
        ukDeemedDomicileDate=tax_status.uk_deemed_domicile_date,
        ukSplitYearTreatment=tax_status.uk_split_year_treatment,
        ukRemittanceBasis=tax_status.uk_remittance_basis,
        saTaxResident=tax_status.sa_tax_resident,
        saOrdinarilyResident=tax_status.sa_ordinarily_resident,
        dualResident=tax_status.dual_resident,
        dtaTieBreakerCountry=tax_status.dta_tie_breaker_country,
        createdAt=tax_status.created_at,
        updatedAt=tax_status.updated_at
    )


@router.get("", response_model=TaxStatusResponse)
async def get_current_tax_status(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current tax status (where effective_to IS NULL).

    Returns the active tax status record for the user.
    """
    query = select(UserTaxStatus).where(
        and_(
            UserTaxStatus.user_id == UUID(current_user_id),
            UserTaxStatus.effective_to.is_(None)
        )
    )

    result = await db.execute(query)
    tax_status = result.scalar_one_or_none()

    if not tax_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No current tax status found. Please create a tax status record."
        )

    return TaxStatusResponse(
        id=tax_status.id,
        userId=tax_status.user_id,
        effectiveFrom=tax_status.effective_from,
        effectiveTo=tax_status.effective_to,
        ukTaxResident=tax_status.uk_tax_resident,
        ukDomicile=tax_status.uk_domicile,
        ukDeemedDomicileDate=tax_status.uk_deemed_domicile_date,
        ukSplitYearTreatment=tax_status.uk_split_year_treatment,
        ukRemittanceBasis=tax_status.uk_remittance_basis,
        saTaxResident=tax_status.sa_tax_resident,
        saOrdinarilyResident=tax_status.sa_ordinarily_resident,
        dualResident=tax_status.dual_resident,
        dtaTieBreakerCountry=tax_status.dta_tie_breaker_country,
        createdAt=tax_status.created_at,
        updatedAt=tax_status.updated_at
    )


@router.get("/history", response_model=List[TaxStatusResponse])
async def get_tax_status_history(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tax status records ordered by effective_from DESC.

    Returns complete history of tax status changes.
    """
    query = select(UserTaxStatus).where(
        UserTaxStatus.user_id == UUID(current_user_id)
    ).order_by(UserTaxStatus.effective_from.desc())

    result = await db.execute(query)
    tax_statuses = result.scalars().all()

    return [
        TaxStatusResponse(
            id=ts.id,
            userId=ts.user_id,
            effectiveFrom=ts.effective_from,
            effectiveTo=ts.effective_to,
            ukTaxResident=ts.uk_tax_resident,
            ukDomicile=ts.uk_domicile,
            ukDeemedDomicileDate=ts.uk_deemed_domicile_date,
            ukSplitYearTreatment=ts.uk_split_year_treatment,
            ukRemittanceBasis=ts.uk_remittance_basis,
            saTaxResident=ts.sa_tax_resident,
            saOrdinarilyResident=ts.sa_ordinarily_resident,
            dualResident=ts.dual_resident,
            dtaTieBreakerCountry=ts.dta_tie_breaker_country,
            createdAt=ts.created_at,
            updatedAt=ts.updated_at
        )
        for ts in tax_statuses
    ]


@router.get("/at-date", response_model=TaxStatusResponse)
async def get_tax_status_at_date(
    query_date: date = Query(..., alias="date", description="Date to query (YYYY-MM-DD)"),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get tax status at a specific date.

    Point-in-time query:
    WHERE effective_from <= date AND (effective_to IS NULL OR effective_to > date)
    """
    query = select(UserTaxStatus).where(
        and_(
            UserTaxStatus.user_id == UUID(current_user_id),
            UserTaxStatus.effective_from <= query_date,
            or_(
                UserTaxStatus.effective_to.is_(None),
                UserTaxStatus.effective_to > query_date
            )
        )
    )

    result = await db.execute(query)
    tax_status = result.scalar_one_or_none()

    if not tax_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No tax status found for date {query_date}"
        )

    return TaxStatusResponse(
        id=tax_status.id,
        userId=tax_status.user_id,
        effectiveFrom=tax_status.effective_from,
        effectiveTo=tax_status.effective_to,
        ukTaxResident=tax_status.uk_tax_resident,
        ukDomicile=tax_status.uk_domicile,
        ukDeemedDomicileDate=tax_status.uk_deemed_domicile_date,
        ukSplitYearTreatment=tax_status.uk_split_year_treatment,
        ukRemittanceBasis=tax_status.uk_remittance_basis,
        saTaxResident=tax_status.sa_tax_resident,
        saOrdinarilyResident=tax_status.sa_ordinarily_resident,
        dualResident=tax_status.dual_resident,
        dtaTieBreakerCountry=tax_status.dta_tie_breaker_country,
        createdAt=tax_status.created_at,
        updatedAt=tax_status.updated_at
    )


# ===== Calculator Endpoints =====

@router.post("/srt-calculator", response_model=SRTCalculatorResponse)
async def calculate_srt(
    data: SRTCalculatorRequest,
    save: bool = Query(False, description="Whether to save result to database"),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate UK Statutory Residence Test.

    Determines UK tax residency using the three-part SRT:
    1. Automatic Overseas Test
    2. Automatic UK Test
    3. Sufficient Ties Test

    Optionally saves result to uk_srt_data table if save=true.
    """
    srt_service = SRTCalculatorService(db)
    result = await srt_service.calculate_residency(
        data,
        user_id=UUID(current_user_id),
        save_result=save
    )

    return result


@router.post("/sa-presence-test", response_model=SAPresenceTestResponse)
async def calculate_sa_presence(
    data: SAPresenceTestRequest,
    save: bool = Query(False, description="Whether to save result to database"),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate SA Physical Presence Test.

    Determines SA tax residency based on:
    1. 91+ days in current tax year
    2. 91+ days average over 5 years (current + 4 previous)

    Also determines ordinarily resident status (3+ consecutive years).

    Optionally saves result to sa_presence_data table if save=true.
    """
    sa_service = SAPresenceCalculatorService(db)
    result = await sa_service.calculate_residency(
        data,
        user_id=UUID(current_user_id),
        save_result=save
    )

    return result


@router.get("/deemed-domicile", response_model=DeemedDomicileResponse)
async def get_deemed_domicile(
    as_of_date: date = Query(None, alias="date", description="Date to calculate (default: today)"),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate deemed domicile status.

    UK deemed domicile rules:
    - Deemed domiciled if UK resident for 15 of last 20 tax years
    - Deemed domiciled if UK domicile of origin AND UK resident in 1 of last 2 years

    Returns:
        - Whether user is deemed domiciled
        - Date deemed domicile started
        - Reason for deemed domicile status
        - Number of UK resident years in last 20
    """
    deemed_domicile_service = DeemedDomicileService(db)
    result = await deemed_domicile_service.calculate_deemed_domicile(
        UUID(current_user_id),
        as_of_date
    )

    return result
