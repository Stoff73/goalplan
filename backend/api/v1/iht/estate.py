"""
Estate and IHT API endpoints.

This module provides REST API endpoints for:
- Estate asset CRUD operations (4 endpoints)
- Estate liability CRUD operations (4 endpoints)
- Estate valuation and IHT calculation (2 endpoints)
- Gift and PET tracking (5 endpoints)
- SA Estate Duty calculation (1 endpoint)

Business logic:
- Authentication required for all endpoints
- Authorization checks (users can only access own data)
- Rate limiting on mutation endpoints
- Temporal data support (effective_from/effective_to)
- Soft delete for audit trail
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
from models.estate_iht import (
    EstateAsset, EstateLiability, AssetType, LiabilityType,
    Gift, GiftType, ExemptionType
)
from schemas.iht import (
    EstateAssetCreate, EstateAssetUpdate, EstateAssetResponse,
    EstateLiabilityCreate, EstateLiabilityUpdate, EstateLiabilityResponse,
    EstateValuationResponse, IHTCalculationRequest, IHTCalculationResponse,
    GiftCreate, GiftResponse, PotentialIHTResponse, ExemptionStatusResponse,
    SAEstateDutyCalculationRequest, SAEstateDutyCalculationResponse
)
from services.iht.estate_valuation_service import EstateValuationService
from services.iht.gift_analysis_service import GiftAnalysisService
from services.iht.sa_estate_duty_service import SAEstateDutyService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _get_asset_or_404(
    asset_id: UUID,
    user_id: UUID,
    db: AsyncSession
) -> EstateAsset:
    """
    Get estate asset or raise 404.

    Verifies ownership and excludes soft-deleted assets.
    """
    stmt = select(EstateAsset).where(
        and_(
            EstateAsset.id == asset_id,
            EstateAsset.user_id == user_id,
            EstateAsset.is_deleted == False
        )
    )

    result = await db.execute(stmt)
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estate asset {asset_id} not found"
        )

    return asset


async def _get_liability_or_404(
    liability_id: UUID,
    user_id: UUID,
    db: AsyncSession
) -> EstateLiability:
    """
    Get estate liability or raise 404.

    Verifies ownership and excludes soft-deleted liabilities.
    """
    stmt = select(EstateLiability).where(
        and_(
            EstateLiability.id == liability_id,
            EstateLiability.user_id == user_id,
            EstateLiability.is_deleted == False
        )
    )

    result = await db.execute(stmt)
    liability = result.scalar_one_or_none()

    if not liability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estate liability {liability_id} not found"
        )

    return liability


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
# ESTATE ASSET ENDPOINTS
# ============================================================================

@router.post("/estate/assets", response_model=EstateAssetResponse, status_code=status.HTTP_201_CREATED)
async def create_estate_asset(
    data: EstateAssetCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new estate asset.

    Args:
        data: Asset creation data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        EstateAssetResponse: Created asset details

    Raises:
        400: Validation error
        401: Not authenticated
        500: Internal server error
    """
    try:
        import uuid

        asset = EstateAsset(
            id=uuid.uuid4(),
            user_id=UUID(current_user_id),
            asset_type=data.asset_type,
            description=data.description,
            estimated_value=data.estimated_value,
            currency=data.currency,
            owned_individually=data.owned_individually,
            joint_ownership=data.joint_ownership,
            included_in_uk_estate=data.included_in_uk_estate,
            included_in_sa_estate=data.included_in_sa_estate,
            effective_from=data.effective_from,
            effective_to=None,
            is_deleted=False
        )

        db.add(asset)
        await db.commit()
        await db.refresh(asset)

        logger.info(
            f"Created estate asset {asset.id} for user {current_user_id}: "
            f"{data.description} ({data.asset_type.value}), value={data.estimated_value} {data.currency}"
        )

        return EstateAssetResponse.model_validate(asset)

    except ValueError as e:
        logger.error(f"Validation error creating estate asset: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create estate asset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create estate asset: {str(e)}"
        )


@router.get("/estate/assets", response_model=List[EstateAssetResponse])
async def get_all_estate_assets(
    current_user_id: str = Depends(get_current_user),
    asset_type: Optional[AssetType] = Query(None, description="Filter by asset type"),
    as_of_date: Optional[date] = Query(None, description="Temporal query date"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all estate assets for the authenticated user.

    Supports filtering by:
    - asset_type: Type of asset
    - as_of_date: Date for temporal queries (default: today)

    Args:
        current_user_id: Authenticated user ID
        asset_type: Optional asset type filter
        as_of_date: Optional temporal query date
        db: Database session

    Returns:
        List[EstateAssetResponse]: List of estate assets
    """
    try:
        # Build query with filters
        conditions = [
            EstateAsset.user_id == UUID(current_user_id),
            EstateAsset.is_deleted == False
        ]

        if asset_type is not None:
            conditions.append(EstateAsset.asset_type == asset_type)

        # Temporal filtering
        if as_of_date is not None:
            conditions.append(EstateAsset.effective_from <= as_of_date)
            conditions.append(
                (EstateAsset.effective_to.is_(None)) |
                (EstateAsset.effective_to > as_of_date)
            )

        stmt = (
            select(EstateAsset)
            .where(and_(*conditions))
            .order_by(EstateAsset.created_at.desc())
        )

        result = await db.execute(stmt)
        assets = result.scalars().all()

        return [EstateAssetResponse.model_validate(asset) for asset in assets]

    except Exception as e:
        logger.error(f"Failed to retrieve estate assets: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve estate assets"
        )


@router.put("/estate/assets/{asset_id}", response_model=EstateAssetResponse)
async def update_estate_asset(
    asset_id: UUID,
    data: EstateAssetUpdate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing estate asset.

    Creates a new temporal record (closes old, creates new with effective dates).

    Args:
        asset_id: Asset UUID
        data: Asset update data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        EstateAssetResponse: Updated asset details

    Raises:
        404: Asset not found or not owned by user
        400: Validation error
        500: Internal server error
    """
    try:
        import uuid

        # Verify ownership
        old_asset = await _get_asset_or_404(asset_id, UUID(current_user_id), db)

        # Close old temporal record
        old_asset.effective_to = date.today()

        # Create new temporal record with updates
        update_data = data.model_dump(exclude_unset=True)

        new_asset = EstateAsset(
            id=uuid.uuid4(),
            user_id=old_asset.user_id,
            asset_type=update_data.get('asset_type', old_asset.asset_type),
            description=update_data.get('description', old_asset.description),
            estimated_value=update_data.get('estimated_value', old_asset.estimated_value),
            currency=update_data.get('currency', old_asset.currency),
            owned_individually=update_data.get('owned_individually', old_asset.owned_individually),
            joint_ownership=update_data.get('joint_ownership', old_asset.joint_ownership),
            included_in_uk_estate=update_data.get('included_in_uk_estate', old_asset.included_in_uk_estate),
            included_in_sa_estate=update_data.get('included_in_sa_estate', old_asset.included_in_sa_estate),
            effective_from=update_data.get('effective_from', date.today()),
            effective_to=None,
            is_deleted=False
        )

        db.add(new_asset)
        await db.commit()
        await db.refresh(new_asset)

        logger.info(f"Updated estate asset {asset_id} for user {current_user_id}")

        return EstateAssetResponse.model_validate(new_asset)

    except ValueError as e:
        logger.error(f"Validation error updating estate asset: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update estate asset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update estate asset: {str(e)}"
        )


@router.delete("/estate/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_estate_asset(
    asset_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete an estate asset.

    Sets is_deleted=True. Retains data for audit trail.

    Args:
        asset_id: Asset UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        204 No Content on success

    Raises:
        404: Asset not found or not owned by user
        500: Internal server error
    """
    try:
        # Verify ownership
        asset = await _get_asset_or_404(asset_id, UUID(current_user_id), db)

        # Soft delete
        asset.is_deleted = True
        await db.commit()

        logger.info(f"Deleted estate asset {asset_id} for user {current_user_id}")

        return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete estate asset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete estate asset"
        )


# ============================================================================
# ESTATE LIABILITY ENDPOINTS
# ============================================================================

@router.post("/estate/liabilities", response_model=EstateLiabilityResponse, status_code=status.HTTP_201_CREATED)
async def create_estate_liability(
    data: EstateLiabilityCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new estate liability.

    Args:
        data: Liability creation data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        EstateLiabilityResponse: Created liability details

    Raises:
        400: Validation error
        401: Not authenticated
        500: Internal server error
    """
    try:
        import uuid

        liability = EstateLiability(
            id=uuid.uuid4(),
            user_id=UUID(current_user_id),
            liability_type=data.liability_type,
            description=data.description,
            amount_outstanding=data.amount_outstanding,
            currency=data.currency,
            deductible_from_estate=data.deductible_from_estate,
            effective_from=data.effective_from,
            effective_to=None,
            is_deleted=False
        )

        db.add(liability)
        await db.commit()
        await db.refresh(liability)

        logger.info(
            f"Created estate liability {liability.id} for user {current_user_id}: "
            f"{data.description} ({data.liability_type.value}), amount={data.amount_outstanding} {data.currency}"
        )

        return EstateLiabilityResponse.model_validate(liability)

    except ValueError as e:
        logger.error(f"Validation error creating estate liability: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create estate liability: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create estate liability: {str(e)}"
        )


@router.get("/estate/liabilities", response_model=List[EstateLiabilityResponse])
async def get_all_estate_liabilities(
    current_user_id: str = Depends(get_current_user),
    liability_type: Optional[LiabilityType] = Query(None, description="Filter by liability type"),
    as_of_date: Optional[date] = Query(None, description="Temporal query date"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all estate liabilities for the authenticated user.

    Supports filtering by:
    - liability_type: Type of liability
    - as_of_date: Date for temporal queries (default: today)

    Args:
        current_user_id: Authenticated user ID
        liability_type: Optional liability type filter
        as_of_date: Optional temporal query date
        db: Database session

    Returns:
        List[EstateLiabilityResponse]: List of estate liabilities
    """
    try:
        # Build query with filters
        conditions = [
            EstateLiability.user_id == UUID(current_user_id),
            EstateLiability.is_deleted == False
        ]

        if liability_type is not None:
            conditions.append(EstateLiability.liability_type == liability_type)

        # Temporal filtering
        if as_of_date is not None:
            conditions.append(EstateLiability.effective_from <= as_of_date)
            conditions.append(
                (EstateLiability.effective_to.is_(None)) |
                (EstateLiability.effective_to > as_of_date)
            )

        stmt = (
            select(EstateLiability)
            .where(and_(*conditions))
            .order_by(EstateLiability.created_at.desc())
        )

        result = await db.execute(stmt)
        liabilities = result.scalars().all()

        return [EstateLiabilityResponse.model_validate(liability) for liability in liabilities]

    except Exception as e:
        logger.error(f"Failed to retrieve estate liabilities: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve estate liabilities"
        )


@router.put("/estate/liabilities/{liability_id}", response_model=EstateLiabilityResponse)
async def update_estate_liability(
    liability_id: UUID,
    data: EstateLiabilityUpdate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing estate liability.

    Creates a new temporal record (closes old, creates new with effective dates).

    Args:
        liability_id: Liability UUID
        data: Liability update data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        EstateLiabilityResponse: Updated liability details

    Raises:
        404: Liability not found or not owned by user
        400: Validation error
        500: Internal server error
    """
    try:
        import uuid

        # Verify ownership
        old_liability = await _get_liability_or_404(liability_id, UUID(current_user_id), db)

        # Close old temporal record
        old_liability.effective_to = date.today()

        # Create new temporal record with updates
        update_data = data.model_dump(exclude_unset=True)

        new_liability = EstateLiability(
            id=uuid.uuid4(),
            user_id=old_liability.user_id,
            liability_type=update_data.get('liability_type', old_liability.liability_type),
            description=update_data.get('description', old_liability.description),
            amount_outstanding=update_data.get('amount_outstanding', old_liability.amount_outstanding),
            currency=update_data.get('currency', old_liability.currency),
            deductible_from_estate=update_data.get('deductible_from_estate', old_liability.deductible_from_estate),
            effective_from=update_data.get('effective_from', date.today()),
            effective_to=None,
            is_deleted=False
        )

        db.add(new_liability)
        await db.commit()
        await db.refresh(new_liability)

        logger.info(f"Updated estate liability {liability_id} for user {current_user_id}")

        return EstateLiabilityResponse.model_validate(new_liability)

    except ValueError as e:
        logger.error(f"Validation error updating estate liability: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update estate liability: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update estate liability: {str(e)}"
        )


@router.delete("/estate/liabilities/{liability_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_estate_liability(
    liability_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete an estate liability.

    Sets is_deleted=True. Retains data for audit trail.

    Args:
        liability_id: Liability UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        204 No Content on success

    Raises:
        404: Liability not found or not owned by user
        500: Internal server error
    """
    try:
        # Verify ownership
        liability = await _get_liability_or_404(liability_id, UUID(current_user_id), db)

        # Soft delete
        liability.is_deleted = True
        await db.commit()

        logger.info(f"Deleted estate liability {liability_id} for user {current_user_id}")

        return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete estate liability: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete estate liability"
        )


# ============================================================================
# ESTATE VALUATION AND IHT CALCULATION ENDPOINTS
# ============================================================================

@router.get("/estate/valuation", response_model=EstateValuationResponse)
async def get_estate_valuation(
    current_user_id: str = Depends(get_current_user),
    as_of_date: Optional[date] = Query(None, description="Valuation date (default: today)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get estate valuation (gross and net estate).

    Args:
        current_user_id: Authenticated user ID
        as_of_date: Optional valuation date
        db: Database session

    Returns:
        EstateValuationResponse: Estate valuation breakdown
    """
    try:
        service = EstateValuationService(db)

        if as_of_date is None:
            as_of_date = date.today()

        gross_estate = await service.calculate_gross_estate(UUID(current_user_id), as_of_date)
        net_estate = await service.calculate_net_estate(UUID(current_user_id), as_of_date)

        total_liabilities = gross_estate - net_estate

        return EstateValuationResponse(
            gross_estate_value=gross_estate,
            total_liabilities=total_liabilities,
            net_estate_value=net_estate,
            currency='GBP',
            as_of_date=as_of_date,
            asset_breakdown=[]  # TODO: Add asset breakdown by type
        )

    except Exception as e:
        logger.error(f"Failed to get estate valuation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get estate valuation"
        )


@router.post("/calculate", response_model=IHTCalculationResponse)
async def calculate_iht(
    data: IHTCalculationRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate UK Inheritance Tax.

    Args:
        data: IHT calculation request data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        IHTCalculationResponse: Complete IHT calculation breakdown

    Raises:
        400: Validation error
        500: Internal server error
    """
    try:
        service = EstateValuationService(db)

        # Calculate IHT
        calculation = await service.calculate_iht(
            user_id=UUID(current_user_id),
            transferable_nrb_percent=data.transferable_nrb_percent,
            property_to_descendants=data.property_to_descendants,
            charitable_gifts_percent=data.charitable_gifts_percent
        )

        calculation_id = None

        # Save if requested
        if data.save_calculation:
            tax_year = _get_current_uk_tax_year()
            saved_calc = await service.save_iht_calculation(
                user_id=UUID(current_user_id),
                calculation_data=calculation,
                tax_year=tax_year
            )
            calculation_id = saved_calc.id

        logger.info(
            f"Calculated IHT for user {current_user_id}: "
            f"net_estate=£{calculation['net_estate']:,.2f}, "
            f"iht_owed=£{calculation['iht_owed']:,.2f}"
        )

        return IHTCalculationResponse(
            gross_estate=calculation['gross_estate'],
            net_estate=calculation['net_estate'],
            standard_nrb=calculation['standard_nrb'],
            residence_nrb=calculation['residence_nrb'],
            transferable_nrb=calculation['transferable_nrb'],
            total_nrb=calculation['total_nrb'],
            taxable_estate=calculation['taxable_estate'],
            iht_rate=calculation['iht_rate'],
            iht_owed=calculation['iht_owed'],
            breakdown=calculation['breakdown'],
            calculation_id=calculation_id
        )

    except ValueError as e:
        logger.error(f"Validation error calculating IHT: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to calculate IHT: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate IHT: {str(e)}"
        )


# ============================================================================
# GIFT AND PET TRACKING ENDPOINTS
# ============================================================================

@router.post("/gifts", response_model=GiftResponse, status_code=status.HTTP_201_CREATED)
async def record_gift(
    data: GiftCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Record a lifetime gift.

    Automatically applies exemptions and classifies as PET/EXEMPT.

    Args:
        data: Gift creation data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        GiftResponse: Created gift with classification

    Raises:
        400: Validation error
        500: Internal server error
    """
    try:
        service = GiftAnalysisService(db)

        gift_data = {
            'recipient': data.recipient,
            'gift_date': data.gift_date,
            'gift_value': data.gift_value,
            'currency': data.currency,
            'description': data.description,
            'exemption_type': data.exemption_type
        }

        gift = await service.record_gift(UUID(current_user_id), gift_data)

        logger.info(
            f"Recorded gift {gift.id} for user {current_user_id}: "
            f"{data.recipient}, value={data.gift_value} {data.currency}, type={gift.gift_type.value}"
        )

        return GiftResponse.model_validate(gift)

    except ValueError as e:
        logger.error(f"Validation error recording gift: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to record gift: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record gift: {str(e)}"
        )


@router.get("/gifts", response_model=List[GiftResponse])
async def get_all_gifts(
    current_user_id: str = Depends(get_current_user),
    gift_type: Optional[GiftType] = Query(None, description="Filter by gift type"),
    only_pet_period: bool = Query(False, description="Only gifts in PET period"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all gifts for the authenticated user.

    Supports filtering by:
    - gift_type: PET, EXEMPT, CHARGEABLE
    - only_pet_period: Only gifts still in 7-year PET period

    Args:
        current_user_id: Authenticated user ID
        gift_type: Optional gift type filter
        only_pet_period: Only PET period gifts
        db: Database session

    Returns:
        List[GiftResponse]: List of gifts
    """
    try:
        conditions = [
            Gift.user_id == UUID(current_user_id),
            Gift.is_deleted == False
        ]

        if gift_type is not None:
            conditions.append(Gift.gift_type == gift_type)

        if only_pet_period:
            conditions.append(Gift.still_in_pet_period == True)

        stmt = (
            select(Gift)
            .where(and_(*conditions))
            .order_by(Gift.gift_date.desc())
        )

        result = await db.execute(stmt)
        gifts = result.scalars().all()

        return [GiftResponse.model_validate(gift) for gift in gifts]

    except Exception as e:
        logger.error(f"Failed to retrieve gifts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve gifts"
        )


@router.get("/gifts/pet-period", response_model=List[GiftResponse])
async def get_gifts_in_pet_period(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all gifts still within the 7-year PET period.

    Args:
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        List[GiftResponse]: Gifts in PET period (sorted by gift_date, oldest first)
    """
    try:
        service = GiftAnalysisService(db)

        gifts = await service.get_gifts_in_pet_period(UUID(current_user_id))

        return [GiftResponse.model_validate(gift) for gift in gifts]

    except Exception as e:
        logger.error(f"Failed to get PET period gifts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get PET period gifts"
        )


@router.post("/gifts/potential-iht", response_model=List[PotentialIHTResponse])
async def calculate_potential_iht_on_pets(
    current_user_id: str = Depends(get_current_user),
    death_date: Optional[date] = Query(None, description="Assumed death date (default: today)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate potential IHT on all PETs if death occurs on specified date.

    Args:
        current_user_id: Authenticated user ID
        death_date: Assumed death date for calculation
        db: Database session

    Returns:
        List[PotentialIHTResponse]: List of gifts with potential IHT
    """
    try:
        service = GiftAnalysisService(db)

        if death_date is None:
            death_date = date.today()

        pet_calculations = await service.calculate_potential_iht_on_pets(
            UUID(current_user_id),
            death_date
        )

        return [PotentialIHTResponse(**calc) for calc in pet_calculations]

    except Exception as e:
        logger.error(f"Failed to calculate potential IHT on PETs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate potential IHT on PETs"
        )


@router.get("/exemptions/{tax_year:path}", response_model=ExemptionStatusResponse)
async def get_exemption_status(
    tax_year: str,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get IHT exemption status for a tax year.

    Args:
        tax_year: UK tax year in format YYYY/YY (e.g., '2024/25')
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        ExemptionStatusResponse: Exemption usage and availability

    Raises:
        400: Invalid tax year format
    """
    try:
        # Validate tax year format
        if len(tax_year) != 7 or tax_year[4] != '/':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tax year format: {tax_year}. Expected format: YYYY/YY (e.g., 2024/25)"
            )

        service = GiftAnalysisService(db)

        exemption_status = await service.get_exemption_status(UUID(current_user_id), tax_year)

        return ExemptionStatusResponse(**exemption_status)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get exemption status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get exemption status"
        )


# ============================================================================
# SA ESTATE DUTY ENDPOINT
# ============================================================================

@router.post("/sa-estate-duty/calculate", response_model=SAEstateDutyCalculationResponse)
async def calculate_sa_estate_duty(
    data: SAEstateDutyCalculationRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate South African Estate Duty.

    Args:
        data: SA Estate Duty calculation request
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        SAEstateDutyCalculationResponse: Complete Estate Duty calculation breakdown

    Raises:
        400: Validation error
        500: Internal server error
    """
    try:
        service = SAEstateDutyService(db)

        as_of_date = data.as_of_date if data.as_of_date else date.today()

        # Calculate Estate Duty
        calculation = await service.calculate_estate_duty(
            user_id=UUID(current_user_id),
            as_of_date=as_of_date
        )

        calculation_id = None

        # Save if requested
        if data.save_calculation:
            saved_calc = await service.save_estate_duty_calculation(
                user_id=UUID(current_user_id),
                calculation_data=calculation
            )
            calculation_id = saved_calc.id

        logger.info(
            f"Calculated SA Estate Duty for user {current_user_id}: "
            f"net_estate=R{calculation['net_estate']:,.2f}, "
            f"duty_owed=R{calculation['estate_duty_owed']:,.2f}"
        )

        return SAEstateDutyCalculationResponse(
            estate_value=calculation['estate_value'],
            liabilities=calculation['liabilities'],
            net_estate=calculation['net_estate'],
            abatement=calculation['abatement'],
            dutiable_amount=calculation['dutiable_amount'],
            estate_duty_owed=calculation['estate_duty_owed'],
            effective_rate=calculation['effective_rate'],
            calculation_id=calculation_id,
            currency='ZAR'
        )

    except ValueError as e:
        logger.error(f"Validation error calculating SA Estate Duty: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to calculate SA Estate Duty: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate SA Estate Duty: {str(e)}"
        )
