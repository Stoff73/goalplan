"""
SA Retirement Funds API endpoints.

Provides REST API for SA retirement fund management:
- POST /sa-funds - Create fund
- GET /sa-funds - List funds
- GET /sa-funds/{id} - Get fund details
- PUT /sa-funds/{id} - Update fund
- DELETE /sa-funds/{id} - Delete fund (soft)
- POST /sa-funds/{id}/contributions - Add contribution
- GET /sa-tax-deduction - Get Section 10C deduction status
"""

import logging
from datetime import date
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth import get_current_user
from models.user import User
from schemas.retirement import (
    SAFundCreate, SAFundUpdate, SAFundResponse,
    SAContributionCreate, SAContributionResponse,
    SADeductionResponse, SAFundProjectionRequest,
    SAFundProjectionResponse, SATotalFundResponse
)
from services.retirement.sa_retirement_service import (
    SARetirementService,
    ValidationError,
    NotFoundError,
    PermissionError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sa-funds", tags=["SA Retirement Funds"])


def _calculate_sa_tax_year(contribution_date: date) -> str:
    """Calculate SA tax year (March 1 - Feb 28/29) from date."""
    if contribution_date.month < 3:
        return f"{contribution_date.year - 1}/{contribution_date.year}"
    return f"{contribution_date.year}/{contribution_date.year + 1}"


@router.post("/", response_model=SAFundResponse, status_code=status.HTTP_201_CREATED)
async def create_fund(
    fund_data: SAFundCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new SA retirement fund."""
    service = SARetirementService(db)

    try:
        fund = await service.create_fund(
            user_id=current_user.id,
            fund_data=fund_data.model_dump()
        )

        # Mask fund number for response
        response_data = SAFundResponse.model_validate(fund)
        fund_number = fund.get_fund_number()
        response_data.fund_number = f"****{fund_number[-4:]}" if len(fund_number) >= 4 else "****"

        return response_data

    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[SAFundResponse])
async def list_funds(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all SA retirement funds for the current user."""
    from sqlalchemy import select
    from models.retirement import SARetirementFund

    result = await db.execute(
        select(SARetirementFund).where(
            SARetirementFund.user_id == current_user.id,
            SARetirementFund.is_deleted == False
        )
    )
    funds = result.scalars().all()

    # Mask fund numbers
    response_funds = []
    for fund in funds:
        response_data = SAFundResponse.model_validate(fund)
        fund_number = fund.get_fund_number()
        response_data.fund_number = f"****{fund_number[-4:]}" if len(fund_number) >= 4 else "****"
        response_funds.append(response_data)

    return response_funds


@router.post("/{fund_id}/contributions", response_model=SAContributionResponse, status_code=status.HTTP_201_CREATED)
async def add_contribution(
    fund_id: UUID,
    contribution_data: SAContributionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a contribution to an SA retirement fund."""
    service = SARetirementService(db)

    # Calculate tax year and temporal dates
    contribution_date = contribution_data.contribution_date
    tax_year = _calculate_sa_tax_year(contribution_date)

    contribution_dict = contribution_data.model_dump()
    contribution_dict['tax_year'] = tax_year
    contribution_dict['effective_from'] = contribution_date
    contribution_dict['effective_to'] = None  # Current contribution

    try:
        contribution = await service.add_contribution(
            fund_id=fund_id,
            user_id=current_user.id,
            contribution_data=contribution_dict
        )

        return SAContributionResponse.model_validate(contribution)

    except (NotFoundError, PermissionError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/sa-tax-deduction", response_model=SADeductionResponse)
async def get_tax_deduction_status(
    tax_year: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get Section 10C tax deduction status for a tax year."""
    service = SARetirementService(db)

    deduction_status = await service.get_deduction_status(
        user_id=current_user.id,
        tax_year=tax_year
    )

    return SADeductionResponse(**deduction_status)
