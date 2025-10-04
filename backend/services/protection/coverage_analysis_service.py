"""
Coverage Gap Analysis Service for Life Assurance Protection Module.

This service handles coverage needs analysis and gap calculations:
- Family needs analysis based on income, debts, children, etc.
- Coverage gap calculation comparing recommended vs actual cover
- Historical analysis tracking with temporal data
- Support for multiple active policies
- Status determination (adequate, under-insured, over-insured)

Business Logic:
    recommended_cover = (annual_income * income_multiplier) +
                       outstanding_debts +
                       (children_count * education_cost_per_child) +
                       funeral_costs -
                       existing_assets

    coverage_gap = recommended_cover - total_current_cover

    Status:
    - ADEQUATE: gap within ±10% of recommended
    - UNDER_INSURED: gap > 10% of recommended
    - OVER_INSURED: gap < -10% of recommended

Performance:
- Uses async/await for database operations
- Eager loads policies to avoid N+1 queries
- Validates data before calculations
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID
from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from models.life_assurance import (
    CoverageNeedsAnalysis,
    LifeAssurancePolicy,
    PolicyStatus
)
from services.protection.exceptions import (
    CoverageAnalysisNotFoundError,
    CoverageAnalysisValidationError
)

logger = logging.getLogger(__name__)


def calculate_recommended_cover(
    annual_income: float,
    outstanding_debts: float,
    children_count: int,
    education_cost_per_child: float,
    funeral_costs: float,
    existing_assets: float,
    income_multiplier: float = 10.0
) -> float:
    """
    Calculate recommended life assurance coverage based on family needs analysis.

    Formula:
        recommended_cover = (annual_income * income_multiplier) +
                           outstanding_debts +
                           (children_count * education_cost_per_child) +
                           funeral_costs -
                           existing_assets

    Args:
        annual_income: User's annual income for replacement calculation
        outstanding_debts: Total outstanding debts (mortgage, loans, etc.)
        children_count: Number of dependent children
        education_cost_per_child: Estimated education cost per child (£100k UK, R500k SA)
        funeral_costs: Estimated funeral and final expenses (£5k UK, R50k SA)
        existing_assets: Existing liquid assets available to family
        income_multiplier: Income replacement multiplier (default: 10.0)

    Returns:
        float: Recommended coverage amount (never negative)

    Raises:
        CoverageAnalysisValidationError: If any input is negative
    """
    # Validate inputs
    if annual_income < 0:
        raise CoverageAnalysisValidationError(
            f"Annual income must be >= 0. Got: {annual_income}"
        )
    if outstanding_debts < 0:
        raise CoverageAnalysisValidationError(
            f"Outstanding debts must be >= 0. Got: {outstanding_debts}"
        )
    if children_count < 0:
        raise CoverageAnalysisValidationError(
            f"Children count must be >= 0. Got: {children_count}"
        )
    if education_cost_per_child < 0:
        raise CoverageAnalysisValidationError(
            f"Education cost per child must be >= 0. Got: {education_cost_per_child}"
        )
    if funeral_costs < 0:
        raise CoverageAnalysisValidationError(
            f"Funeral costs must be >= 0. Got: {funeral_costs}"
        )
    if existing_assets < 0:
        raise CoverageAnalysisValidationError(
            f"Existing assets must be >= 0. Got: {existing_assets}"
        )
    if income_multiplier <= 0:
        raise CoverageAnalysisValidationError(
            f"Income multiplier must be > 0. Got: {income_multiplier}"
        )

    # Calculate components
    income_replacement = Decimal(str(annual_income)) * Decimal(str(income_multiplier))
    children_education = Decimal(str(children_count)) * Decimal(str(education_cost_per_child))

    # Calculate recommended cover
    recommended = (
        income_replacement +
        Decimal(str(outstanding_debts)) +
        children_education +
        Decimal(str(funeral_costs)) -
        Decimal(str(existing_assets))
    )

    # Ensure recommended cover is never negative
    recommended = max(recommended, Decimal('0.00'))

    return float(recommended)


async def calculate_coverage_gap(
    db: AsyncSession,
    user_id: UUID,
    recommended_cover: float
) -> Dict:
    """
    Calculate coverage gap between recommended and actual coverage.

    Compares recommended coverage against sum of all active life assurance policies.

    Args:
        db: Async database session
        user_id: User ID
        recommended_cover: Recommended coverage amount

    Returns:
        dict: Coverage gap analysis with:
            - current_total_cover: Sum of all active policies
            - recommended_cover: Recommended coverage amount
            - coverage_gap: Difference (positive = under-insured, negative = over-insured)
            - gap_percentage: Percentage gap relative to recommended
            - policies_contributing: Count of active policies
            - status: 'ADEQUATE', 'UNDER_INSURED', or 'OVER_INSURED'
    """
    # Get all active policies for user
    stmt = select(LifeAssurancePolicy).where(
        and_(
            LifeAssurancePolicy.user_id == user_id,
            LifeAssurancePolicy.status == PolicyStatus.ACTIVE,
            LifeAssurancePolicy.is_deleted == False
        )
    )

    result = await db.execute(stmt)
    active_policies = result.scalars().all()

    # Sum total coverage
    total_current_cover = sum(
        float(policy.cover_amount) for policy in active_policies
    )

    # Calculate gap
    coverage_gap = recommended_cover - total_current_cover

    # Calculate gap percentage
    if recommended_cover > 0:
        gap_percentage = (coverage_gap / recommended_cover) * 100
    else:
        gap_percentage = 0.0

    # Determine status
    if abs(gap_percentage) <= 10.0:
        status = 'ADEQUATE'
    elif gap_percentage > 10.0:
        status = 'UNDER_INSURED'
    else:
        status = 'OVER_INSURED'

    logger.info(
        f"Coverage gap for user {user_id}: "
        f"Recommended={recommended_cover}, Current={total_current_cover}, "
        f"Gap={coverage_gap}, Status={status}"
    )

    return {
        'current_total_cover': total_current_cover,
        'recommended_cover': recommended_cover,
        'coverage_gap': coverage_gap,
        'gap_percentage': gap_percentage,
        'policies_contributing': len(active_policies),
        'status': status
    }


async def get_coverage_summary(
    db: AsyncSession,
    user_id: UUID
) -> Optional[Dict]:
    """
    Get comprehensive coverage summary for user.

    Retrieves current coverage analysis and combines with actual policy coverage.

    Args:
        db: Async database session
        user_id: User ID

    Returns:
        dict or None: Coverage summary with analysis data and current coverage, or None if no analysis exists
            - analysis_date: Date of analysis
            - annual_income: Annual income used in analysis
            - outstanding_debts: Outstanding debts
            - children_count: Number of children
            - recommended_cover: Recommended coverage amount
            - current_total_cover: Sum of active policies
            - coverage_gap: Difference between recommended and current
            - gap_percentage: Percentage gap
            - status: Coverage status
            - policies_count: Number of active policies
    """
    # Get current coverage analysis
    stmt = select(CoverageNeedsAnalysis).where(
        and_(
            CoverageNeedsAnalysis.user_id == user_id,
            CoverageNeedsAnalysis.effective_to.is_(None)
        )
    )

    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()

    if not analysis:
        logger.info(f"No current coverage analysis found for user {user_id}")
        return None

    # Get current coverage from active policies
    gap_data = await calculate_coverage_gap(
        db=db,
        user_id=user_id,
        recommended_cover=float(analysis.recommended_cover)
    )

    return {
        'analysis_date': analysis.calculation_date,
        'annual_income': float(analysis.annual_income),
        'outstanding_debts': float(analysis.outstanding_debts),
        'children_count': analysis.children_count,
        'recommended_cover': float(analysis.recommended_cover),
        'current_total_cover': gap_data['current_total_cover'],
        'coverage_gap': gap_data['coverage_gap'],
        'gap_percentage': gap_data['gap_percentage'],
        'status': gap_data['status'],
        'policies_count': gap_data['policies_contributing']
    }


async def create_coverage_analysis(
    db: AsyncSession,
    user_id: UUID,
    analysis_data: Dict
) -> CoverageNeedsAnalysis:
    """
    Create new coverage needs analysis for user.

    Uses temporal data pattern: sets effective_to on previous analysis before creating new one.

    Args:
        db: Async database session
        user_id: User ID
        analysis_data: Analysis input data containing:
            - annual_income: float
            - outstanding_debts: float
            - children_count: int
            - education_cost_per_child: float
            - funeral_costs: float
            - existing_assets: float
            - income_multiplier: float (optional, default 10.0)
            - notes: str (optional)

    Returns:
        CoverageNeedsAnalysis: Created analysis with calculated fields

    Raises:
        CoverageAnalysisValidationError: If input validation fails
    """
    # Calculate recommended cover
    recommended = calculate_recommended_cover(
        annual_income=analysis_data['annual_income'],
        outstanding_debts=analysis_data['outstanding_debts'],
        children_count=analysis_data['children_count'],
        education_cost_per_child=analysis_data['education_cost_per_child'],
        funeral_costs=analysis_data['funeral_costs'],
        existing_assets=analysis_data['existing_assets'],
        income_multiplier=analysis_data.get('income_multiplier', 10.0)
    )

    # Get current coverage from active policies
    gap_data = await calculate_coverage_gap(
        db=db,
        user_id=user_id,
        recommended_cover=recommended
    )

    # Expire existing current analysis (temporal data)
    stmt = select(CoverageNeedsAnalysis).where(
        and_(
            CoverageNeedsAnalysis.user_id == user_id,
            CoverageNeedsAnalysis.effective_to.is_(None)
        )
    )
    result = await db.execute(stmt)
    existing_analysis = result.scalar_one_or_none()

    if existing_analysis:
        existing_analysis.effective_to = datetime.utcnow()
        logger.info(f"Expired previous coverage analysis {existing_analysis.id} for user {user_id}")

    # Create new analysis
    analysis = CoverageNeedsAnalysis(
        user_id=user_id,
        calculation_date=date.today(),
        annual_income=Decimal(str(analysis_data['annual_income'])),
        income_multiplier=Decimal(str(analysis_data.get('income_multiplier', 10.0))),
        outstanding_debts=Decimal(str(analysis_data['outstanding_debts'])),
        children_count=analysis_data['children_count'],
        education_cost_per_child=Decimal(str(analysis_data['education_cost_per_child'])),
        funeral_costs=Decimal(str(analysis_data['funeral_costs'])),
        existing_assets=Decimal(str(analysis_data['existing_assets'])),
        recommended_cover=Decimal(str(recommended)),
        current_total_cover=Decimal(str(gap_data['current_total_cover'])),
        coverage_gap=Decimal(str(gap_data['coverage_gap'])),
        notes=analysis_data.get('notes'),
        effective_from=datetime.utcnow(),
        effective_to=None  # Current analysis
    )

    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    logger.info(
        f"Created coverage analysis {analysis.id} for user {user_id}: "
        f"Recommended={recommended}, Gap={gap_data['coverage_gap']}"
    )

    return analysis


async def update_coverage_analysis(
    db: AsyncSession,
    analysis_id: UUID,
    user_id: UUID,
    update_data: Dict
) -> CoverageNeedsAnalysis:
    """
    Update existing coverage needs analysis.

    Re-calculates recommended cover and gap after update.

    Args:
        db: Async database session
        analysis_id: Analysis ID to update
        user_id: User ID (for authorization)
        update_data: Fields to update (any subset of analysis_data fields)

    Returns:
        CoverageNeedsAnalysis: Updated analysis with recalculated fields

    Raises:
        CoverageAnalysisNotFoundError: If analysis doesn't exist
        CoverageAnalysisValidationError: If user doesn't own analysis or validation fails
    """
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
    if analysis.user_id != user_id:
        raise CoverageAnalysisValidationError(
            f"User {user_id} does not have permission to update analysis {analysis_id}"
        )

    # Update fields
    for field, value in update_data.items():
        if field in ['annual_income', 'outstanding_debts', 'education_cost_per_child',
                     'funeral_costs', 'existing_assets', 'income_multiplier']:
            setattr(analysis, field, Decimal(str(value)))
        elif field == 'children_count':
            analysis.children_count = value
        elif field == 'notes':
            analysis.notes = value

    # Recalculate recommended cover
    recommended = calculate_recommended_cover(
        annual_income=float(analysis.annual_income),
        outstanding_debts=float(analysis.outstanding_debts),
        children_count=analysis.children_count,
        education_cost_per_child=float(analysis.education_cost_per_child),
        funeral_costs=float(analysis.funeral_costs),
        existing_assets=float(analysis.existing_assets),
        income_multiplier=float(analysis.income_multiplier)
    )

    # Get current coverage and recalculate gap
    gap_data = await calculate_coverage_gap(
        db=db,
        user_id=user_id,
        recommended_cover=recommended
    )

    # Update calculated fields
    analysis.recommended_cover = Decimal(str(recommended))
    analysis.current_total_cover = Decimal(str(gap_data['current_total_cover']))
    analysis.coverage_gap = Decimal(str(gap_data['coverage_gap']))
    analysis.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(analysis)

    logger.info(f"Updated coverage analysis {analysis_id} for user {user_id}")

    return analysis


async def get_historical_coverage_analyses(
    db: AsyncSession,
    user_id: UUID
) -> List[CoverageNeedsAnalysis]:
    """
    Get all coverage analyses for user, including historical.

    Returns analyses ordered by effective_from descending (newest first).

    Args:
        db: Async database session
        user_id: User ID

    Returns:
        List[CoverageNeedsAnalysis]: All analyses for user (current and historical)
    """
    stmt = select(CoverageNeedsAnalysis).where(
        CoverageNeedsAnalysis.user_id == user_id
    ).order_by(CoverageNeedsAnalysis.effective_from.desc())

    result = await db.execute(stmt)
    analyses = result.scalars().all()

    logger.info(f"Retrieved {len(analyses)} coverage analyses for user {user_id}")

    return list(analyses)
