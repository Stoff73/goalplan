"""
Coverage analysis API endpoints.

This module provides endpoints for coverage needs analysis:
- Create coverage analysis
- Get coverage summary
- List historical analyses
- Get specific analysis by ID
- Update existing analysis

All endpoints require authentication and implement proper authorization checks.
"""

import logging
from typing import List
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth import get_current_user
from schemas.protection import (
    CoverageAnalysisCreate,
    CoverageAnalysisResponse,
    CoverageSummaryResponse
)
from services.protection.coverage_analysis_service import (
    create_coverage_analysis,
    get_coverage_summary,
    get_historical_coverage_analyses,
    update_coverage_analysis,
    calculate_coverage_gap
)
from services.protection.exceptions import (
    CoverageAnalysisNotFoundError,
    CoverageAnalysisValidationError
)
from models.life_assurance import CoverageNeedsAnalysis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/coverage-analysis", tags=["Coverage Analysis"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _map_analysis_to_response(analysis: CoverageNeedsAnalysis) -> CoverageAnalysisResponse:
    """
    Map CoverageNeedsAnalysis model to CoverageAnalysisResponse schema.

    Args:
        analysis: CoverageNeedsAnalysis model instance

    Returns:
        CoverageAnalysisResponse: Response schema
    """
    return CoverageAnalysisResponse(
        id=analysis.id,
        calculation_date=analysis.calculation_date,
        annual_income=analysis.annual_income,
        income_multiplier=analysis.income_multiplier,
        outstanding_debts=analysis.outstanding_debts,
        children_count=analysis.children_count,
        education_cost_per_child=analysis.education_cost_per_child,
        funeral_costs=analysis.funeral_costs,
        existing_assets=analysis.existing_assets,
        recommended_cover=analysis.recommended_cover,
        current_total_cover=analysis.current_total_cover,
        coverage_gap=analysis.coverage_gap,
        notes=analysis.notes,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at
    )


# ============================================================================
# COVERAGE ANALYSIS ENDPOINTS
# ============================================================================

@router.post("", response_model=CoverageAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    data: CoverageAnalysisCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new coverage needs analysis.

    Business logic:
    1. Validate input data (all non-negative values)
    2. Calculate recommended coverage using family needs formula
    3. Get current total coverage from active policies
    4. Calculate coverage gap and status
    5. Store analysis with temporal data (expires previous analysis)

    Args:
        data: Coverage analysis input data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        CoverageAnalysisResponse: Created analysis with calculated fields

    Raises:
        400: Validation error (negative values, invalid multiplier)
        401: Authentication required
        500: Internal server error
    """
    try:
        # Convert Pydantic model to dict
        analysis_data = data.model_dump()

        # Create analysis via service
        analysis = await create_coverage_analysis(
            db=db,
            user_id=UUID(current_user_id),
            analysis_data=analysis_data
        )

        logger.info(
            f"Created coverage analysis {analysis.id} for user {current_user_id}: "
            f"Recommended={analysis.recommended_cover}, Gap={analysis.coverage_gap}"
        )

        return _map_analysis_to_response(analysis)

    except CoverageAnalysisValidationError as e:
        logger.warning(f"Coverage analysis validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Failed to create coverage analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create coverage analysis: {str(e)}"
        )


@router.get("/summary", response_model=CoverageSummaryResponse)
async def get_summary(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current coverage summary for user.

    Combines coverage analysis data with actual policy coverage to provide
    a comprehensive overview of protection status.

    If no analysis exists:
    - Returns current coverage from active policies
    - Sets recommended_cover = 0
    - Gap shows current coverage (negative = over-insured against zero recommended)

    Args:
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        CoverageSummaryResponse: Coverage summary with status and gap analysis

    Raises:
        401: Authentication required
        500: Internal server error
    """
    try:
        # Get coverage summary
        summary = await get_coverage_summary(
            db=db,
            user_id=UUID(current_user_id)
        )

        # If no analysis exists, calculate just current coverage
        if summary is None:
            logger.info(f"No coverage analysis found for user {current_user_id}, calculating current coverage only")

            gap_data = await calculate_coverage_gap(
                db=db,
                user_id=UUID(current_user_id),
                recommended_cover=0.0
            )

            return CoverageSummaryResponse(
                analysis_date=None,
                annual_income=None,
                outstanding_debts=None,
                children_count=None,
                recommended_cover=Decimal('0.00'),
                current_total_cover=Decimal(str(gap_data['current_total_cover'])),
                coverage_gap=Decimal(str(gap_data['coverage_gap'])),
                gap_percentage=Decimal(str(gap_data['gap_percentage'])),
                status=gap_data['status'],
                policies_count=gap_data['policies_contributing']
            )

        logger.info(f"Retrieved coverage summary for user {current_user_id}: Status={summary['status']}")

        return CoverageSummaryResponse(
            analysis_date=summary['analysis_date'],
            annual_income=Decimal(str(summary['annual_income'])),
            outstanding_debts=Decimal(str(summary['outstanding_debts'])),
            children_count=summary['children_count'],
            recommended_cover=Decimal(str(summary['recommended_cover'])),
            current_total_cover=Decimal(str(summary['current_total_cover'])),
            coverage_gap=Decimal(str(summary['coverage_gap'])),
            gap_percentage=Decimal(str(summary['gap_percentage'])),
            status=summary['status'],
            policies_count=summary['policies_count']
        )

    except Exception as e:
        logger.error(f"Failed to retrieve coverage summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve coverage summary"
        )


@router.get("", response_model=List[CoverageAnalysisResponse])
async def list_historical_analyses(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all coverage analyses for user, including historical.

    Returns analyses ordered by calculation_date descending (newest first).

    Args:
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        List[CoverageAnalysisResponse]: All analyses (current and historical)

    Raises:
        401: Authentication required
        500: Internal server error
    """
    try:
        analyses = await get_historical_coverage_analyses(
            db=db,
            user_id=UUID(current_user_id)
        )

        logger.info(f"Retrieved {len(analyses)} coverage analyses for user {current_user_id}")

        return [_map_analysis_to_response(analysis) for analysis in analyses]

    except Exception as e:
        logger.error(f"Failed to retrieve historical analyses: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve historical analyses"
        )


@router.get("/{analysis_id}", response_model=CoverageAnalysisResponse)
async def get_analysis_by_id(
    analysis_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific coverage analysis by ID.

    Verifies user owns the analysis before returning details.

    Args:
        analysis_id: Analysis UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        CoverageAnalysisResponse: Analysis details

    Raises:
        401: Authentication required
        403: User does not own analysis
        404: Analysis not found
        500: Internal server error
    """
    try:
        from sqlalchemy import select
        from models.life_assurance import CoverageNeedsAnalysis

        # Get analysis
        stmt = select(CoverageNeedsAnalysis).where(
            CoverageNeedsAnalysis.id == analysis_id
        )
        result = await db.execute(stmt)
        analysis = result.scalar_one_or_none()

        if not analysis:
            raise CoverageAnalysisNotFoundError(
                f"Coverage analysis {analysis_id} not found"
            )

        # Verify user owns the analysis
        if str(analysis.user_id) != current_user_id:
            logger.warning(
                f"User {current_user_id} attempted to access analysis {analysis_id} "
                f"owned by user {analysis.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have permission to access analysis {analysis_id}"
            )

        logger.info(f"Retrieved coverage analysis {analysis_id} for user {current_user_id}")

        return _map_analysis_to_response(analysis)

    except CoverageAnalysisNotFoundError as e:
        logger.warning(f"Coverage analysis not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve coverage analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve coverage analysis"
        )


@router.put("/{analysis_id}", response_model=CoverageAnalysisResponse)
async def update_analysis(
    analysis_id: UUID,
    data: CoverageAnalysisCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing coverage analysis.

    Re-calculates recommended cover and gap after update.

    Args:
        analysis_id: Analysis UUID
        data: Updated analysis data (reuses CoverageAnalysisCreate schema)
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        CoverageAnalysisResponse: Updated analysis with recalculated fields

    Raises:
        400: Validation error
        401: Authentication required
        403: User does not own analysis
        404: Analysis not found
        500: Internal server error
    """
    try:
        # Convert to dict
        update_data = data.model_dump()

        # Update analysis via service
        analysis = await update_coverage_analysis(
            db=db,
            analysis_id=analysis_id,
            user_id=UUID(current_user_id),
            update_data=update_data
        )

        logger.info(
            f"Updated coverage analysis {analysis_id} for user {current_user_id}: "
            f"Recommended={analysis.recommended_cover}, Gap={analysis.coverage_gap}"
        )

        return _map_analysis_to_response(analysis)

    except CoverageAnalysisNotFoundError as e:
        logger.warning(f"Coverage analysis not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except CoverageAnalysisValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Failed to update coverage analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update coverage analysis"
        )
