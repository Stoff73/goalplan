"""
Life assurance policy API endpoints.

This module provides CRUD operations for life assurance policies:
- Create policy with beneficiaries and trust details
- List user policies with filtering
- Get single policy by ID
- Update policy details
- Delete policy (soft delete)
- Manage beneficiaries (add, update, delete)

All endpoints require authentication and implement proper authorization checks.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth import get_current_user
from schemas.protection import (
    PolicyCreate,
    PolicyUpdate,
    PolicyResponse,
    BeneficiaryCreate,
    BeneficiaryUpdate,
    BeneficiaryResponse
)
from services.protection.policy_service import PolicyService
from services.protection.exceptions import (
    PolicyValidationError,
    PolicyNotFoundError,
    PolicyPermissionError
)
from models.life_assurance import PolicyStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/life-assurance", tags=["Life Assurance"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _map_policy_to_response(policy) -> PolicyResponse:
    """
    Map LifeAssurancePolicy model to PolicyResponse schema.

    Handles decryption of policy number and beneficiary PII.

    Args:
        policy: LifeAssurancePolicy model instance

    Returns:
        PolicyResponse: Response schema with decrypted data
    """
    # Decrypt policy number (mask for security)
    try:
        policy_number = policy.get_policy_number()
        # Mask all but last 4 characters
        if len(policy_number) > 4:
            policy_number = "****" + policy_number[-4:]
    except Exception:
        policy_number = "****"

    # Map beneficiaries
    beneficiaries = []
    for ben in policy.beneficiaries:
        try:
            beneficiaries.append(BeneficiaryResponse(
                id=ben.id,
                name=ben.get_name(),
                date_of_birth=ben.get_date_of_birth(),
                relationship=ben.beneficiary_relationship,
                percentage=ben.percentage,
                address=ben.get_address(),
                created_at=ben.created_at,
                updated_at=ben.updated_at
            ))
        except Exception as e:
            logger.error(f"Error decrypting beneficiary {ben.id}: {e}")
            # Skip beneficiary if decryption fails
            continue

    # Map trust details
    trust_details = None
    if policy.trust_detail:
        from schemas.protection import TrustDetailResponse
        trust_details = TrustDetailResponse(
            id=policy.trust_detail.id,
            trust_type=policy.trust_detail.trust_type,
            trustees=policy.trust_detail.get_trustees(),
            trust_beneficiaries=policy.trust_detail.trust_beneficiaries,
            trust_created_date=policy.trust_detail.trust_created_date,
            created_at=policy.trust_detail.created_at,
            updated_at=policy.trust_detail.updated_at
        )

    return PolicyResponse(
        id=policy.id,
        policy_number=policy_number,
        provider=policy.provider,
        provider_country=policy.provider_country,
        policy_type=policy.policy_type,
        cover_amount=policy.cover_amount,
        currency=policy.currency,
        cover_amount_gbp=policy.cover_amount_gbp,
        cover_amount_zar=policy.cover_amount_zar,
        premium_amount=policy.premium_amount,
        premium_frequency=policy.premium_frequency,
        annual_premium=policy.annual_premium,
        start_date=policy.start_date,
        end_date=policy.end_date,
        written_in_trust=policy.written_in_trust,
        status=policy.status,
        uk_iht_impact=policy.uk_iht_impact,
        sa_estate_duty_impact=policy.sa_estate_duty_impact,
        beneficiaries=beneficiaries,
        trust_details=trust_details,
        critical_illness_rider=policy.critical_illness_rider,
        waiver_of_premium=policy.waiver_of_premium,
        indexation_rate=policy.indexation_rate,
        notes=policy.notes,
        created_at=policy.created_at,
        updated_at=policy.updated_at
    )


# ============================================================================
# POLICY CRUD ENDPOINTS
# ============================================================================

@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    data: PolicyCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new life assurance policy.

    Business logic:
    1. Validate policy data (amounts, dates, beneficiaries)
    2. Encrypt policy number and beneficiary PII
    3. Calculate annual premium and tax impacts
    4. Create policy with beneficiaries and trust details

    Args:
        data: Policy creation data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        PolicyResponse: Created policy with all details

    Raises:
        400: Validation error (invalid data, beneficiary percentages, etc.)
        401: Authentication required
        500: Internal server error
    """
    try:
        # Convert Pydantic model to dict
        policy_data = data.model_dump()

        # Create policy via service
        service = PolicyService(db)
        policy = await service.create_policy(
            user_id=UUID(current_user_id),
            policy_data=policy_data
        )

        logger.info(
            f"Created life assurance policy {policy.id} for user {current_user_id}: "
            f"{policy.provider} - {policy.cover_amount} {policy.currency.value}"
        )

        return _map_policy_to_response(policy)

    except PolicyValidationError as e:
        logger.warning(f"Policy validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Failed to create policy: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create policy: {str(e)}"
        )


@router.get("", response_model=List[PolicyResponse])
async def list_policies(
    current_user_id: str = Depends(get_current_user),
    status_filter: Optional[PolicyStatus] = Query(None, alias="status", description="Filter by policy status"),
    provider: Optional[str] = Query(None, description="Filter by provider name"),
    include_deleted: bool = Query(False, description="Include soft-deleted policies"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all life assurance policies for the authenticated user.

    Supports filtering by:
    - status: ACTIVE, LAPSED, CLAIMED, MATURED
    - provider: Provider name (exact match)
    - include_deleted: Include soft-deleted policies

    Args:
        current_user_id: Authenticated user ID
        status_filter: Optional status filter
        provider: Optional provider filter
        include_deleted: Include deleted policies
        db: Database session

    Returns:
        List[PolicyResponse]: List of policies

    Raises:
        401: Authentication required
        500: Internal server error
    """
    try:
        service = PolicyService(db)
        policies = await service.get_user_policies(
            user_id=UUID(current_user_id),
            include_deleted=include_deleted,
            status=status_filter.value if status_filter else None,
            provider=provider
        )

        logger.info(f"Retrieved {len(policies)} policies for user {current_user_id}")

        return [_map_policy_to_response(policy) for policy in policies]

    except Exception as e:
        logger.error(f"Failed to retrieve policies: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve policies"
        )


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single life assurance policy by ID.

    Verifies user owns the policy before returning details.

    Args:
        policy_id: Policy UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        PolicyResponse: Policy details with beneficiaries and trust info

    Raises:
        401: Authentication required
        403: User does not own policy
        404: Policy not found
        500: Internal server error
    """
    try:
        service = PolicyService(db)
        policy = await service.get_policy_by_id(
            policy_id=policy_id,
            user_id=UUID(current_user_id)
        )

        logger.info(f"Retrieved policy {policy_id} for user {current_user_id}")

        return _map_policy_to_response(policy)

    except PolicyNotFoundError as e:
        logger.warning(f"Policy not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except PolicyPermissionError as e:
        logger.warning(f"Permission denied: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Failed to retrieve policy: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve policy"
        )


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: UUID,
    data: PolicyUpdate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing life assurance policy.

    Note: Rate limiting should be applied at middleware level (5 updates per minute per user).
    Only provided fields will be updated.

    Args:
        policy_id: Policy UUID
        data: Update data (all fields optional)
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        PolicyResponse: Updated policy details

    Raises:
        400: Validation error
        401: Authentication required
        403: User does not own policy
        404: Policy not found
        429: Too many requests (rate limit via middleware)
        500: Internal server error
    """
    try:
        # Convert to dict, excluding unset fields
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )

        service = PolicyService(db)
        policy = await service.update_policy(
            policy_id=policy_id,
            user_id=UUID(current_user_id),
            update_data=update_data
        )

        logger.info(f"Updated policy {policy_id} for user {current_user_id}")

        return _map_policy_to_response(policy)

    except PolicyNotFoundError as e:
        logger.warning(f"Policy not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except PolicyPermissionError as e:
        logger.warning(f"Permission denied: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except PolicyValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Failed to update policy: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update policy"
        )


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete a life assurance policy.

    Sets is_deleted=True. Policy is retained for audit trail.

    Args:
        policy_id: Policy UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        None (204 No Content)

    Raises:
        401: Authentication required
        403: User does not own policy
        404: Policy not found
        500: Internal server error
    """
    try:
        service = PolicyService(db)
        await service.delete_policy(
            policy_id=policy_id,
            user_id=UUID(current_user_id)
        )

        logger.info(f"Soft deleted policy {policy_id} for user {current_user_id}")

        return None

    except PolicyNotFoundError as e:
        logger.warning(f"Policy not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except PolicyPermissionError as e:
        logger.warning(f"Permission denied: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Failed to delete policy: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete policy"
        )


# ============================================================================
# BENEFICIARY MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/{policy_id}/beneficiaries", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
async def add_beneficiary(
    policy_id: UUID,
    data: BeneficiaryCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a beneficiary to a policy.

    Validates that total beneficiary percentages don't exceed 100%.

    Args:
        policy_id: Policy UUID
        data: Beneficiary creation data
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        BeneficiaryResponse: Created beneficiary

    Raises:
        400: Validation error (percentages would exceed 100%)
        401: Authentication required
        403: User does not own policy
        404: Policy not found
        500: Internal server error
    """
    try:
        beneficiary_data = data.model_dump()

        service = PolicyService(db)
        beneficiary = await service.add_beneficiary(
            policy_id=policy_id,
            user_id=UUID(current_user_id),
            beneficiary_data=beneficiary_data
        )

        logger.info(f"Added beneficiary {beneficiary.id} to policy {policy_id}")

        return BeneficiaryResponse(
            id=beneficiary.id,
            name=beneficiary.get_name(),
            date_of_birth=beneficiary.get_date_of_birth(),
            relationship=beneficiary.beneficiary_relationship,
            percentage=beneficiary.percentage,
            address=beneficiary.get_address(),
            created_at=beneficiary.created_at,
            updated_at=beneficiary.updated_at
        )

    except PolicyNotFoundError as e:
        logger.warning(f"Policy not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except PolicyPermissionError as e:
        logger.warning(f"Permission denied: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except PolicyValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Failed to add beneficiary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add beneficiary"
        )


@router.put("/{policy_id}/beneficiaries/{beneficiary_id}", response_model=BeneficiaryResponse)
async def update_beneficiary(
    policy_id: UUID,
    beneficiary_id: UUID,
    data: BeneficiaryUpdate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a beneficiary.

    Validates that total beneficiary percentages don't exceed 100%.

    Args:
        policy_id: Policy UUID (for validation)
        beneficiary_id: Beneficiary UUID
        data: Update data (all fields optional)
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        BeneficiaryResponse: Updated beneficiary

    Raises:
        400: Validation error (percentages would exceed 100%)
        401: Authentication required
        403: User does not own policy
        404: Beneficiary not found
        500: Internal server error
    """
    try:
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )

        service = PolicyService(db)
        beneficiary = await service.update_beneficiary(
            beneficiary_id=beneficiary_id,
            user_id=UUID(current_user_id),
            update_data=update_data
        )

        logger.info(f"Updated beneficiary {beneficiary_id} for policy {policy_id}")

        return BeneficiaryResponse(
            id=beneficiary.id,
            name=beneficiary.get_name(),
            date_of_birth=beneficiary.get_date_of_birth(),
            relationship=beneficiary.beneficiary_relationship,
            percentage=beneficiary.percentage,
            address=beneficiary.get_address(),
            created_at=beneficiary.created_at,
            updated_at=beneficiary.updated_at
        )

    except PolicyNotFoundError as e:
        logger.warning(f"Beneficiary not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except PolicyPermissionError as e:
        logger.warning(f"Permission denied: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except PolicyValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Failed to update beneficiary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update beneficiary"
        )


@router.delete("/{policy_id}/beneficiaries/{beneficiary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_beneficiary(
    policy_id: UUID,
    beneficiary_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a beneficiary (hard delete).

    Args:
        policy_id: Policy UUID (for validation)
        beneficiary_id: Beneficiary UUID
        current_user_id: Authenticated user ID
        db: Database session

    Returns:
        None (204 No Content)

    Raises:
        401: Authentication required
        403: User does not own policy
        404: Beneficiary not found
        500: Internal server error
    """
    try:
        service = PolicyService(db)
        await service.delete_beneficiary(
            beneficiary_id=beneficiary_id,
            user_id=UUID(current_user_id)
        )

        logger.info(f"Deleted beneficiary {beneficiary_id} from policy {policy_id}")

        return None

    except PolicyNotFoundError as e:
        logger.warning(f"Beneficiary not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except PolicyPermissionError as e:
        logger.warning(f"Permission denied: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Failed to delete beneficiary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete beneficiary"
        )
