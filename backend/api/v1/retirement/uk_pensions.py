"""
UK Pension API endpoints.

This module provides REST API endpoints for:
- UK Pension CRUD operations (create, list, get, update, delete)
- Pension contribution tracking
- Annual Allowance status
- Total pension pot calculation
- Retirement income projections
- Drawdown scenario modeling
- Annuity quote calculations

Business logic:
- Authentication required for all endpoints
- Authorization checks (users can only access own pensions)
- Rate limiting on mutation endpoints
- Encrypted scheme references
- Temporal contribution tracking
- Annual allowance automatic updates
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import date
import logging

from database import get_db
from middleware.auth import get_current_user
from models.retirement import (
    UKPension, UKPensionContribution, UKPensionDBDetails,
    PensionType, PensionStatus, AnnualAllowanceTracking,
    StatePensionForecast, RetirementProjection, DrawdownScenario
)
from schemas.retirement import (
    PensionCreate, PensionUpdate, PensionResponse,
    ContributionCreate, ContributionResponse,
    AnnualAllowanceResponse, TotalPotResponse, PensionPotSummary,
    ProjectionCreate, ProjectionResponse, IncomeBreakdown,
    DrawdownScenarioCreate, DrawdownScenarioResponse,
    AnnuityQuoteRequest, AnnuityQuoteResponse,
    DBDetailsResponse
)
from services.retirement.uk_pension_service import UKPensionService
from services.retirement.annual_allowance_service import AnnualAllowanceService
from services.retirement.income_projection_service import IncomeProjectionService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _get_pension_or_404(
    pension_id: UUID,
    user_id: UUID,
    db: AsyncSession
) -> UKPension:
    """
    Get pension or raise 404.

    Verifies ownership and excludes soft-deleted pensions.
    """
    stmt = select(UKPension).where(
        and_(
            UKPension.id == pension_id,
            UKPension.user_id == user_id,
            UKPension.is_deleted == False
        )
    )

    result = await db.execute(stmt)
    pension = result.scalar_one_or_none()

    if not pension:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pension {pension_id} not found"
        )

    return pension


async def _map_pension_to_response(
    pension: UKPension,
    db: AsyncSession
) -> PensionResponse:
    """Map UKPension model to response schema."""
    # Mask scheme reference (show only last 4 digits)
    try:
        scheme_ref = pension.get_scheme_reference()
        if len(scheme_ref) > 4:
            scheme_ref = "****" + scheme_ref[-4:]
    except Exception:
        scheme_ref = "****"

    # Calculate projected value
    projected_value = pension.calculate_projected_value()

    # Get DB details if applicable
    db_details = None
    if pension.pension_type == PensionType.OCCUPATIONAL_DB and pension.db_details:
        db_details = DBDetailsResponse.model_validate(pension.db_details)

    return PensionResponse(
        id=pension.id,
        user_id=pension.user_id,
        pension_type=pension.pension_type,
        provider=pension.provider,
        scheme_reference=scheme_ref,
        employer_name=pension.employer_name,
        current_value=pension.current_value,
        start_date=pension.start_date,
        expected_retirement_date=pension.expected_retirement_date,
        investment_strategy=pension.investment_strategy,
        assumed_growth_rate=pension.assumed_growth_rate,
        assumed_inflation_rate=pension.assumed_inflation_rate,
        mpaa_triggered=pension.mpaa_triggered,
        mpaa_date=pension.mpaa_date,
        status=pension.status,
        projected_value=projected_value,
        db_details=db_details
    )


def _get_current_uk_tax_year() -> str:
    """Get current UK tax year in format YYYY/YY."""
    today = date.today()
    if today.month < 4 or (today.month == 4 and today.day < 6):
        # Before April 6th - previous tax year
        year = today.year - 1
    else:
        # After April 6th - current tax year
        year = today.year

    next_year = str(year + 1)[-2:]
    return f"{year}/{next_year}"


# ============================================================================
# PENSION CRUD ENDPOINTS
# ============================================================================

@router.post("/retirement/uk-pensions", response_model=PensionResponse, status_code=status.HTTP_201_CREATED)
async def create_uk_pension(
    data: PensionCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new UK pension.

    Business logic:
    1. Validate pension data (type, dates, values)
    2. Encrypt scheme reference
    3. Create pension record
    4. Create DB details if applicable
    5. Return pension with masked scheme reference

    Args:
        data: Pension creation data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        PensionResponse: Created pension details

    Raises:
        400: Validation error
        401: Not authenticated
        500: Internal server error
    """
    try:
        service = UKPensionService(db)

        # Prepare pension data
        pension_data = {
            "pension_type": data.pension_type,
            "provider": data.provider,
            "scheme_reference": data.scheme_reference,
            "employer_name": data.employer_name,
            "current_value": data.current_value,
            "start_date": data.start_date,
            "expected_retirement_date": data.expected_retirement_date,
            "investment_strategy": data.investment_strategy,
            "assumed_growth_rate": data.assumed_growth_rate,
            "assumed_inflation_rate": data.assumed_inflation_rate,
            "mpaa_triggered": data.mpaa_triggered,
            "mpaa_date": data.mpaa_date,
        }

        # Add DB details if provided
        if data.db_details:
            pension_data["db_details"] = {
                "accrual_rate": data.db_details.accrual_rate,
                "pensionable_service_years": data.db_details.pensionable_service_years,
                "scheme_type": data.db_details.scheme_type,
                "normal_retirement_age": data.db_details.normal_retirement_age,
                "guaranteed_pension_amount": data.db_details.guaranteed_pension_amount,
                "spouse_pension_percentage": data.db_details.spouse_pension_percentage,
                "lump_sum_entitlement": data.db_details.lump_sum_entitlement,
                "indexation_type": data.db_details.indexation_type,
            }

        # Create pension
        pension = await service.create_pension(
            user_id=UUID(current_user_id),
            pension_data=pension_data
        )

        logger.info(
            f"Created UK pension {pension.id} for user {current_user_id}: "
            f"{data.provider} ({data.pension_type.value})"
        )

        return await _map_pension_to_response(pension, db)

    except ValueError as e:
        logger.error(f"Validation error creating pension: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create pension: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pension: {str(e)}"
        )


@router.get("/retirement/uk-pensions", response_model=List[PensionResponse])
async def get_all_pensions(
    current_user_id: str = Depends(get_current_user),
    pension_type: Optional[PensionType] = Query(None, description="Filter by pension type"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    status_filter: Optional[PensionStatus] = Query(None, alias="status", description="Filter by status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all UK pensions for the authenticated user.

    Supports filtering by:
    - pension_type: OCCUPATIONAL_DB, OCCUPATIONAL_DC, PERSONAL_PENSION, SIPP, STATE_PENSION
    - provider: Provider name (partial match)
    - status: ACTIVE, DEFERRED, IN_PAYMENT, TRANSFERRED_OUT

    Args:
        current_user_id: Authenticated user ID
        pension_type: Optional pension type filter
        provider: Optional provider filter
        status_filter: Optional status filter
        db: Database session

    Returns:
        List[PensionResponse]: List of pensions with projected values
    """
    try:
        # Build query with filters
        conditions = [
            UKPension.user_id == UUID(current_user_id),
            UKPension.is_deleted == False
        ]

        if pension_type is not None:
            conditions.append(UKPension.pension_type == pension_type)

        if provider is not None:
            conditions.append(UKPension.provider.ilike(f"%{provider}%"))

        if status_filter is not None:
            conditions.append(UKPension.status == status_filter)

        stmt = (
            select(UKPension)
            .where(and_(*conditions))
            .order_by(UKPension.created_at.desc())
        )

        result = await db.execute(stmt)
        pensions = result.scalars().all()

        # Map to response
        responses = []
        for pension in pensions:
            response = await _map_pension_to_response(pension, db)
            responses.append(response)

        return responses

    except Exception as e:
        logger.error(f"Failed to retrieve pensions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pensions"
        )


@router.get("/retirement/uk-pensions/{pension_id}", response_model=PensionResponse)
async def get_pension(
    pension_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single UK pension by ID.

    Verifies ownership before returning pension details.

    Args:
        pension_id: Pension UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        PensionResponse: Pension details with projected value

    Raises:
        404: Pension not found or not owned by user
    """
    pension = await _get_pension_or_404(pension_id, UUID(current_user_id), db)
    return await _map_pension_to_response(pension, db)


@router.put("/retirement/uk-pensions/{pension_id}", response_model=PensionResponse)
async def update_pension(
    pension_id: UUID,
    data: PensionUpdate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing UK pension.

    All fields are optional. Only provided fields will be updated.

    Args:
        pension_id: Pension UUID
        data: Pension update data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        PensionResponse: Updated pension details

    Raises:
        404: Pension not found or not owned by user
        400: Validation error
        500: Internal server error
    """
    try:
        service = UKPensionService(db)

        # Verify ownership
        await _get_pension_or_404(pension_id, UUID(current_user_id), db)

        # Prepare update data (only include fields that were provided)
        update_data = data.model_dump(exclude_unset=True)

        # Update pension
        pension = await service.update_pension(pension_id, update_data)

        logger.info(f"Updated pension {pension_id} for user {current_user_id}")

        return await _map_pension_to_response(pension, db)

    except ValueError as e:
        logger.error(f"Validation error updating pension: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update pension: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update pension: {str(e)}"
        )


@router.delete("/retirement/uk-pensions/{pension_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pension(
    pension_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete a UK pension.

    Sets is_deleted=True and cascades to all contributions.
    Retains data for audit trail.

    Args:
        pension_id: Pension UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        204 No Content on success

    Raises:
        404: Pension not found or not owned by user
        500: Internal server error
    """
    try:
        service = UKPensionService(db)

        # Verify ownership
        await _get_pension_or_404(pension_id, UUID(current_user_id), db)

        # Delete pension
        await service.delete_pension(pension_id)

        logger.info(f"Deleted pension {pension_id} for user {current_user_id}")

        return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete pension: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete pension"
        )


# ============================================================================
# CONTRIBUTION ENDPOINTS
# ============================================================================

@router.post("/retirement/uk-pensions/{pension_id}/contributions", response_model=ContributionResponse, status_code=status.HTTP_201_CREATED)
async def add_contribution(
    pension_id: UUID,
    data: ContributionCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a pension contribution.

    Automatically updates Annual Allowance tracking.

    Args:
        pension_id: Pension UUID
        data: Contribution data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        ContributionResponse: Created contribution details

    Raises:
        404: Pension not found or not owned by user
        400: Validation error
        500: Internal server error
    """
    try:
        service = UKPensionService(db)

        # Verify ownership
        await _get_pension_or_404(pension_id, UUID(current_user_id), db)

        # Add contribution
        contribution = await service.add_contribution(
            pension_id=pension_id,
            employee_contribution=data.employee_contribution,
            employer_contribution=data.employer_contribution,
            personal_contribution=data.personal_contribution,
            frequency=data.frequency,
            tax_relief_method=data.tax_relief_method,
            contribution_date=data.contribution_date
        )

        logger.info(
            f"Added contribution to pension {pension_id}: "
            f"total={contribution.total_contribution}"
        )

        return ContributionResponse.model_validate(contribution)

    except ValueError as e:
        logger.error(f"Validation error adding contribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add contribution: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add contribution: {str(e)}"
        )


# ============================================================================
# ANNUAL ALLOWANCE ENDPOINTS
# ============================================================================

@router.get("/retirement/annual-allowance", response_model=AnnualAllowanceResponse)
async def get_annual_allowance_status(
    current_user_id: str = Depends(get_current_user),
    tax_year: Optional[str] = Query(None, description="Tax year (YYYY/YY), defaults to current"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get Annual Allowance status for a tax year.

    Returns allowance limit, used, remaining, and carry forward.

    Args:
        current_user_id: Authenticated user ID
        tax_year: Optional tax year (defaults to current UK tax year)
        db: Database session

    Returns:
        AnnualAllowanceResponse: Annual allowance status
    """
    try:
        service = AnnualAllowanceService(db)

        # Default to current tax year
        if tax_year is None:
            tax_year = _get_current_uk_tax_year()

        # Calculate allowance usage
        aa_status = await service.calculate_allowance_usage(
            user_id=UUID(current_user_id),
            tax_year=tax_year
        )

        return AnnualAllowanceResponse.model_validate(aa_status)

    except Exception as e:
        logger.error(f"Failed to get annual allowance status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get annual allowance status"
        )


# ============================================================================
# TOTAL POT ENDPOINT
# ============================================================================

@router.get("/retirement/total-pot", response_model=TotalPotResponse)
async def get_total_pension_pot(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get total pension pot across all pensions.

    Aggregates current and projected values from all active pensions.

    Args:
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        TotalPotResponse: Total pot with breakdown by pension
    """
    try:
        service = UKPensionService(db)

        # Get total pot
        total_data = await service.get_total_pension_pot(UUID(current_user_id))

        # Get state pension if available
        state_pension_stmt = select(StatePensionForecast).where(
            StatePensionForecast.user_id == UUID(current_user_id)
        )
        result = await db.execute(state_pension_stmt)
        state_pension = result.scalar_one_or_none()

        return TotalPotResponse(
            total_current_value=total_data["total_current_value"],
            total_projected_value=total_data["total_projected_value"],
            pensions=[
                PensionPotSummary(**pension_data)
                for pension_data in total_data["pensions"]
            ],
            state_pension_annual=state_pension.estimated_annual_amount if state_pension else None
        )

    except Exception as e:
        logger.error(f"Failed to get total pension pot: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get total pension pot"
        )


# ============================================================================
# PROJECTION ENDPOINTS
# ============================================================================

@router.post("/retirement/projections", response_model=ProjectionResponse, status_code=status.HTTP_201_CREATED)
async def create_retirement_projection(
    data: ProjectionCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate retirement projection.

    Projects total retirement income from all sources and calculates income gap.

    Args:
        data: Projection creation data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        ProjectionResponse: Retirement projection with income breakdown

    Raises:
        400: Validation error
        500: Internal server error
    """
    try:
        service = IncomeProjectionService(db)

        # Create projection
        projection = await service.create_retirement_projection(
            user_id=UUID(current_user_id),
            target_retirement_age=data.target_retirement_age,
            annual_income_needed=data.annual_income_needed,
            growth_assumptions=data.growth_assumptions,
            inflation_rate=data.inflation_rate
        )

        logger.info(
            f"Created retirement projection {projection.id} for user {current_user_id}: "
            f"target_age={data.target_retirement_age}, on_track={projection.on_track}"
        )

        # Build income breakdown
        income_breakdown = IncomeBreakdown(
            state_pension_income=projection.state_pension_income,
            db_pension_income=projection.db_pension_income,
            dc_drawdown_income=projection.dc_drawdown_income,
            other_income=projection.other_income,
            total_income=projection.total_projected_income
        )

        return ProjectionResponse(
            id=projection.id,
            user_id=projection.user_id,
            projection_date=projection.projection_date,
            target_retirement_age=projection.target_retirement_age,
            projected_total_pot=projection.projected_total_pot,
            annual_income_needed=projection.annual_income_needed,
            income_breakdown=income_breakdown,
            income_gap=projection.income_gap,
            on_track=projection.on_track,
            growth_assumptions=projection.growth_assumptions,
            inflation_rate=projection.inflation_rate
        )

    except ValueError as e:
        logger.error(f"Validation error creating projection: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create projection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create projection: {str(e)}"
        )


@router.get("/retirement/income-projection", response_model=IncomeBreakdown)
async def get_income_projection(
    current_user_id: str = Depends(get_current_user),
    retirement_age: Optional[int] = Query(None, ge=55, le=75, description="Target retirement age"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current retirement income projection.

    Calculates projected income from all sources at retirement age.

    Args:
        current_user_id: Authenticated user ID
        retirement_age: Optional target retirement age
        db: Database session

    Returns:
        IncomeBreakdown: Income breakdown by source
    """
    try:
        service = IncomeProjectionService(db)

        # Calculate total income
        income_data = await service.calculate_total_retirement_income(
            user_id=UUID(current_user_id),
            target_retirement_age=retirement_age
        )

        return IncomeBreakdown(
            state_pension_income=income_data["state_pension_income"],
            db_pension_income=income_data["db_pension_income"],
            dc_drawdown_income=income_data["dc_drawdown_income"],
            other_income=income_data["other_income"],
            total_income=income_data["total_annual_income"]
        )

    except Exception as e:
        logger.error(f"Failed to get income projection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get income projection"
        )


@router.post("/retirement/drawdown-scenario", response_model=DrawdownScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_drawdown_scenario(
    data: DrawdownScenarioCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Model a pension drawdown scenario.

    Calculates projected income and pot depletion age.

    Args:
        data: Drawdown scenario data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        DrawdownScenarioResponse: Drawdown scenario with projected income

    Raises:
        404: Pension not found or not owned by user
        400: Validation error
        500: Internal server error
    """
    try:
        service = IncomeProjectionService(db)

        # Verify pension ownership
        await _get_pension_or_404(data.pension_id, UUID(current_user_id), db)

        # Calculate drawdown income
        drawdown_data = await service.calculate_drawdown_income(
            pension_id=data.pension_id,
            drawdown_rate=data.drawdown_rate,
            start_age=data.start_age
        )

        # Create DrawdownScenario record
        scenario = DrawdownScenario(
            pension_id=data.pension_id,
            scenario_name=data.scenario_name,
            drawdown_rate=data.drawdown_rate,
            start_age=data.start_age,
            projected_annual_income=drawdown_data["annual_income"],
            pot_depletion_age=drawdown_data["pot_depletion_age"],
            tax_implications=drawdown_data.get("tax_implications"),
            assumptions=drawdown_data.get("assumptions")
        )

        db.add(scenario)
        await db.commit()
        await db.refresh(scenario)

        logger.info(
            f"Created drawdown scenario {scenario.id} for pension {data.pension_id}: "
            f"rate={data.drawdown_rate}%, income={drawdown_data['annual_income']}"
        )

        return DrawdownScenarioResponse.model_validate(scenario)

    except ValueError as e:
        logger.error(f"Validation error creating drawdown scenario: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create drawdown scenario: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create drawdown scenario: {str(e)}"
        )


@router.post("/retirement/annuity-quote", response_model=AnnuityQuoteResponse)
async def calculate_annuity_quote(
    data: AnnuityQuoteRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate annuity income quote.

    Estimates annual and monthly income from annuity purchase.

    Args:
        data: Annuity quote request
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        AnnuityQuoteResponse: Annuity quote with projected income

    Raises:
        404: Pension not found or not owned by user
        400: Validation error
        500: Internal server error
    """
    try:
        service = IncomeProjectionService(db)

        # Verify pension ownership
        pension = await _get_pension_or_404(data.pension_id, UUID(current_user_id), db)

        # Calculate annuity income
        annuity_data = await service.calculate_annuity_income(
            pension_id=data.pension_id,
            annuity_rate=data.annuity_rate,
            spouse_provision=data.spouse_provision
        )

        logger.info(
            f"Calculated annuity quote for pension {data.pension_id}: "
            f"rate={data.annuity_rate}%, annual_income={annuity_data['annual_income']}"
        )

        return AnnuityQuoteResponse(
            pension_id=data.pension_id,
            pot_value=annuity_data["pot_value"],
            annuity_rate=data.annuity_rate,
            annual_income=annuity_data["annual_income"],
            monthly_income=annuity_data["monthly_income"],
            spouse_provision=data.spouse_provision,
            escalation_rate=data.escalation_rate,
            guaranteed_period=annuity_data.get("guaranteed_period")
        )

    except ValueError as e:
        logger.error(f"Validation error calculating annuity quote: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate annuity quote: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate annuity quote: {str(e)}"
        )
