"""
Policy Management Service for Life Assurance Protection Module.

This service handles all CRUD operations for life assurance policies with:
- Comprehensive validation (beneficiary percentages, amounts, dates)
- PII encryption for policy numbers and beneficiary data
- Tax impact calculations (UK IHT, SA Estate Duty)
- Trust structure management
- Authorization checks (user owns policy)
- Soft delete for audit trail

Business Rules:
- Beneficiary percentages must sum to exactly 100%
- Cover amount must be > 0
- Premium amount must be >= 0
- End date must be > start date (if not whole of life)
- If written_in_trust = True, must have trust_type and trustees
- Policy numbers and beneficiary PII are encrypted at rest

Performance:
- Eager loads relationships to avoid N+1 queries
- Uses async/await for database operations
- Validates data before database operations
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import date, datetime
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from models.life_assurance import (
    LifeAssurancePolicy,
    PolicyBeneficiary,
    PolicyTrustDetail,
    PolicyStatus,
    PremiumFrequency,
    ProviderCountry,
    BeneficiaryRelationship
)
from utils.encryption import encrypt_value, decrypt_value
from services.protection.exceptions import (
    PolicyValidationError,
    PolicyNotFoundError,
    PolicyPermissionError
)

logger = logging.getLogger(__name__)


class PolicyService:
    """Service for life assurance policy CRUD operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize policy service.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_policy(
        self,
        user_id: UUID,
        policy_data: dict
    ) -> LifeAssurancePolicy:
        """
        Create a new life assurance policy with validation and encryption.

        Args:
            user_id: User ID who owns the policy
            policy_data: Policy data dictionary containing:
                - policy_number: str
                - provider: str
                - provider_country: str
                - policy_type: str
                - cover_amount: Decimal
                - currency: str
                - premium_amount: Decimal
                - premium_frequency: str
                - start_date: date
                - end_date: date (optional)
                - written_in_trust: bool (optional)
                - trust_details: dict (optional, required if written_in_trust=True)
                - beneficiaries: list[dict]
                - critical_illness_rider: bool (optional)
                - waiver_of_premium: bool (optional)
                - indexation_rate: Decimal (optional)
                - notes: str (optional)

        Returns:
            LifeAssurancePolicy: Created policy with relationships loaded

        Raises:
            PolicyValidationError: If validation fails
        """
        # Validate input data
        self._validate_policy_data(policy_data)

        # Validate beneficiaries
        beneficiaries_data = policy_data.get('beneficiaries', [])
        self.validate_beneficiary_percentages(beneficiaries_data)

        # Check if trust details provided (indicates written in trust)
        trust_details = policy_data.get('trust_details')
        has_trust = trust_details is not None

        # Create policy instance
        policy = LifeAssurancePolicy(
            user_id=user_id,
            provider=policy_data['provider'],
            provider_country=policy_data['provider_country'],
            policy_type=policy_data['policy_type'],
            cover_amount=policy_data['cover_amount'],
            currency=policy_data['currency'],
            premium_amount=policy_data['premium_amount'],
            premium_frequency=policy_data['premium_frequency'],
            start_date=policy_data['start_date'],
            end_date=policy_data.get('end_date'),
            written_in_trust=has_trust,
            trust_type=trust_details.get('trust_type') if has_trust else None,
            critical_illness_rider=policy_data.get('critical_illness_rider', False),
            waiver_of_premium=policy_data.get('waiver_of_premium', False),
            indexation_rate=policy_data.get('indexation_rate'),
            status=PolicyStatus.ACTIVE,
            notes=policy_data.get('notes')
        )

        # Encrypt policy number
        policy.set_policy_number(policy_data['policy_number'])

        # Calculate annual premium
        policy.annual_premium = policy.calculate_annual_premium()

        # Calculate tax impacts
        policy.uk_iht_impact = policy.calculate_uk_iht_impact()
        policy.sa_estate_duty_impact = policy.calculate_sa_estate_duty_impact()

        # Add policy to session
        self.db.add(policy)
        await self.db.flush()  # Get policy ID

        # Create beneficiaries
        for ben_data in beneficiaries_data:
            beneficiary = PolicyBeneficiary(
                policy_id=policy.id,
                beneficiary_relationship=ben_data['relationship'],
                percentage=ben_data['percentage']
            )
            # Encrypt PII
            beneficiary.set_name(ben_data['name'])
            beneficiary.set_date_of_birth(ben_data['date_of_birth'])
            beneficiary.set_address(ben_data['address'])

            self.db.add(beneficiary)

        # Create trust details if provided (already retrieved above)
        if trust_details:
            trust_detail = PolicyTrustDetail(
                policy_id=policy.id,
                trust_type=trust_details['trust_type'],
                trust_created_date=trust_details.get('trust_created_date', date.today())
            )
            trust_detail.set_trustees(trust_details['trustees'])
            trust_detail.trust_beneficiaries = trust_details.get('trust_beneficiaries')

            self.db.add(trust_detail)

        # Commit transaction
        await self.db.commit()

        # Reload with relationships
        await self.db.refresh(
            policy,
            ['beneficiaries', 'trust_detail']
        )

        logger.info(f"Created policy {policy.id} for user {user_id}")
        return policy

    async def update_policy(
        self,
        policy_id: UUID,
        user_id: UUID,
        update_data: dict
    ) -> LifeAssurancePolicy:
        """
        Update an existing life assurance policy.

        Args:
            policy_id: Policy ID to update
            user_id: User ID (for authorization)
            update_data: Fields to update

        Returns:
            LifeAssurancePolicy: Updated policy

        Raises:
            PolicyNotFoundError: If policy doesn't exist
            PolicyPermissionError: If user doesn't own policy
            PolicyValidationError: If validation fails
        """
        # Get policy with authorization check
        policy = await self._get_policy_with_auth(policy_id, user_id)

        # Validate update data
        if update_data:
            self._validate_policy_data(update_data, is_update=True)

        # Update fields
        for field, value in update_data.items():
            if field == 'policy_number':
                policy.set_policy_number(value)
            elif field == 'beneficiaries':
                # Handle beneficiary updates separately
                continue
            elif hasattr(policy, field):
                setattr(policy, field, value)

        # Recalculate annual premium if premium changed
        if 'premium_amount' in update_data or 'premium_frequency' in update_data:
            policy.annual_premium = policy.calculate_annual_premium()

        # Recalculate tax impacts if trust status changed
        if 'written_in_trust' in update_data:
            policy.uk_iht_impact = policy.calculate_uk_iht_impact()
            policy.sa_estate_duty_impact = policy.calculate_sa_estate_duty_impact()

        # Update timestamp
        policy.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(policy, ['beneficiaries', 'trust_detail'])

        logger.info(f"Updated policy {policy_id} for user {user_id}")
        return policy

    async def delete_policy(
        self,
        policy_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Soft delete a life assurance policy.

        Args:
            policy_id: Policy ID to delete
            user_id: User ID (for authorization)

        Returns:
            bool: True on success

        Raises:
            PolicyNotFoundError: If policy doesn't exist
            PolicyPermissionError: If user doesn't own policy
        """
        # Get policy with authorization check
        policy = await self._get_policy_with_auth(policy_id, user_id)

        # Perform soft delete
        policy.is_deleted = True
        policy.updated_at = datetime.utcnow()

        await self.db.commit()

        logger.info(f"Soft deleted policy {policy_id} for user {user_id}")
        return True

    async def get_user_policies(
        self,
        user_id: UUID,
        include_deleted: bool = False,
        status: Optional[str] = None,
        provider: Optional[str] = None
    ) -> List[LifeAssurancePolicy]:
        """
        Get all policies for a user with optional filtering.

        Args:
            user_id: User ID
            include_deleted: Include soft-deleted policies
            status: Filter by status (optional)
            provider: Filter by provider (optional)

        Returns:
            List[LifeAssurancePolicy]: List of policies
        """
        # Build query
        query = select(LifeAssurancePolicy).where(
            LifeAssurancePolicy.user_id == user_id
        )

        # Filter by deleted status
        if not include_deleted:
            query = query.where(LifeAssurancePolicy.is_deleted == False)

        # Filter by status
        if status:
            query = query.where(LifeAssurancePolicy.status == status)

        # Filter by provider
        if provider:
            query = query.where(LifeAssurancePolicy.provider == provider)

        # Eager load relationships
        query = query.options(
            selectinload(LifeAssurancePolicy.beneficiaries),
            selectinload(LifeAssurancePolicy.trust_detail)
        )

        result = await self.db.execute(query)
        policies = result.scalars().all()

        logger.info(f"Retrieved {len(policies)} policies for user {user_id}")
        return list(policies)

    async def get_policy_by_id(
        self,
        policy_id: UUID,
        user_id: UUID
    ) -> LifeAssurancePolicy:
        """
        Get a specific policy by ID with decrypted data.

        Args:
            policy_id: Policy ID
            user_id: User ID (for authorization)

        Returns:
            LifeAssurancePolicy: Policy with relationships loaded and decrypted data

        Raises:
            PolicyNotFoundError: If policy doesn't exist
            PolicyPermissionError: If user doesn't own policy
        """
        # Get policy with authorization check
        policy = await self._get_policy_with_auth(policy_id, user_id)

        # Reload with all relationships
        await self.db.refresh(
            policy,
            ['beneficiaries', 'trust_detail', 'documents']
        )

        logger.info(f"Retrieved policy {policy_id} for user {user_id}")
        return policy

    async def add_beneficiary(
        self,
        policy_id: UUID,
        user_id: UUID,
        beneficiary_data: dict
    ) -> PolicyBeneficiary:
        """
        Add a beneficiary to a policy.

        Args:
            policy_id: Policy ID
            user_id: User ID (for authorization)
            beneficiary_data: Beneficiary data:
                - name: str
                - date_of_birth: date
                - address: str
                - relationship: str
                - percentage: Decimal

        Returns:
            PolicyBeneficiary: Created beneficiary

        Raises:
            PolicyNotFoundError: If policy doesn't exist
            PolicyPermissionError: If user doesn't own policy
            PolicyValidationError: If percentages would exceed 100%
        """
        # Get policy with authorization check
        policy = await self._get_policy_with_auth(policy_id, user_id)

        # Validate percentage
        percentage = beneficiary_data['percentage']
        if percentage <= 0 or percentage > 100:
            raise PolicyValidationError(
                f"Beneficiary percentage must be > 0 and <= 100. Got: {percentage}%"
            )

        # Get existing beneficiaries
        await self.db.refresh(policy, ['beneficiaries'])
        existing_total = sum(b.percentage for b in policy.beneficiaries)

        # Check total wouldn't exceed 100%
        new_total = existing_total + percentage
        if new_total > 100:
            raise PolicyValidationError(
                f"Total beneficiary percentages would exceed 100%. "
                f"Current total: {existing_total}%, Adding: {percentage}%, "
                f"New total would be: {new_total}%"
            )

        # Create beneficiary
        beneficiary = PolicyBeneficiary(
            policy_id=policy_id,
            beneficiary_relationship=beneficiary_data['relationship'],
            percentage=percentage
        )

        # Encrypt PII
        beneficiary.set_name(beneficiary_data['name'])
        beneficiary.set_date_of_birth(beneficiary_data['date_of_birth'])
        beneficiary.set_address(beneficiary_data['address'])

        self.db.add(beneficiary)
        await self.db.commit()
        await self.db.refresh(beneficiary)

        logger.info(f"Added beneficiary {beneficiary.id} to policy {policy_id}")
        return beneficiary

    async def update_beneficiary(
        self,
        beneficiary_id: UUID,
        user_id: UUID,
        update_data: dict
    ) -> PolicyBeneficiary:
        """
        Update a beneficiary.

        Args:
            beneficiary_id: Beneficiary ID
            user_id: User ID (for authorization)
            update_data: Fields to update

        Returns:
            PolicyBeneficiary: Updated beneficiary

        Raises:
            PolicyNotFoundError: If beneficiary doesn't exist
            PolicyPermissionError: If user doesn't own policy
            PolicyValidationError: If percentages would exceed 100%
        """
        # Get beneficiary
        stmt = select(PolicyBeneficiary).where(
            PolicyBeneficiary.id == beneficiary_id
        ).options(selectinload(PolicyBeneficiary.policy))

        result = await self.db.execute(stmt)
        beneficiary = result.scalar_one_or_none()

        if not beneficiary:
            raise PolicyNotFoundError(
                f"Beneficiary {beneficiary_id} not found"
            )

        # Verify user owns the policy
        if beneficiary.policy.user_id != user_id:
            raise PolicyPermissionError(
                f"User {user_id} does not have permission to modify beneficiary {beneficiary_id}"
            )

        # If updating percentage, validate it wouldn't break 100% rule
        if 'percentage' in update_data:
            new_percentage = update_data['percentage']
            if new_percentage <= 0 or new_percentage > 100:
                raise PolicyValidationError(
                    f"Beneficiary percentage must be > 0 and <= 100. Got: {new_percentage}%"
                )

            # Get all beneficiaries for the policy
            await self.db.refresh(beneficiary.policy, ['beneficiaries'])
            other_beneficiaries_total = sum(
                b.percentage for b in beneficiary.policy.beneficiaries
                if b.id != beneficiary_id
            )

            new_total = other_beneficiaries_total + new_percentage
            if new_total > 100:
                raise PolicyValidationError(
                    f"Total beneficiary percentages would exceed 100%. "
                    f"Other beneficiaries total: {other_beneficiaries_total}%, "
                    f"New percentage: {new_percentage}%, "
                    f"Total would be: {new_total}%"
                )

            beneficiary.percentage = new_percentage

        # Update other fields
        for field, value in update_data.items():
            if field == 'name':
                beneficiary.set_name(value)
            elif field == 'date_of_birth':
                beneficiary.set_date_of_birth(value)
            elif field == 'address':
                beneficiary.set_address(value)
            elif field == 'relationship':
                beneficiary.beneficiary_relationship = value
            elif field == 'percentage':
                # Already handled above
                pass

        beneficiary.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(beneficiary)

        logger.info(f"Updated beneficiary {beneficiary_id}")
        return beneficiary

    async def delete_beneficiary(
        self,
        beneficiary_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a beneficiary (hard delete).

        Args:
            beneficiary_id: Beneficiary ID
            user_id: User ID (for authorization)

        Returns:
            bool: True on success

        Raises:
            PolicyNotFoundError: If beneficiary doesn't exist
            PolicyPermissionError: If user doesn't own policy
        """
        # Get beneficiary
        stmt = select(PolicyBeneficiary).where(
            PolicyBeneficiary.id == beneficiary_id
        ).options(selectinload(PolicyBeneficiary.policy))

        result = await self.db.execute(stmt)
        beneficiary = result.scalar_one_or_none()

        if not beneficiary:
            raise PolicyNotFoundError(
                f"Beneficiary {beneficiary_id} not found"
            )

        # Verify user owns the policy
        if beneficiary.policy.user_id != user_id:
            raise PolicyPermissionError(
                f"User {user_id} does not have permission to delete beneficiary {beneficiary_id}"
            )

        # Hard delete
        await self.db.delete(beneficiary)
        await self.db.commit()

        logger.info(f"Deleted beneficiary {beneficiary_id}")
        return True

    @staticmethod
    def validate_beneficiary_percentages(beneficiaries: List[dict]) -> None:
        """
        Validate that beneficiary percentages sum to exactly 100%.

        Args:
            beneficiaries: List of beneficiary dicts with 'percentage' field

        Raises:
            PolicyValidationError: If percentages don't sum to exactly 100%
        """
        if not beneficiaries:
            return  # No beneficiaries is valid

        total = sum(Decimal(str(b['percentage'])) for b in beneficiaries)

        if total != Decimal('100.00'):
            raise PolicyValidationError(
                f"Beneficiary percentages must total exactly 100%. Current total: {total}%"
            )

    def _validate_policy_data(self, policy_data: dict, is_update: bool = False) -> None:
        """
        Validate policy data.

        Args:
            policy_data: Policy data to validate
            is_update: If True, some fields are optional

        Raises:
            PolicyValidationError: If validation fails
        """
        # Cover amount validation
        if 'cover_amount' in policy_data:
            cover_amount = policy_data['cover_amount']
            if cover_amount <= 0:
                raise PolicyValidationError(
                    f"Cover amount must be > 0. Got: {cover_amount}"
                )

        # Premium amount validation
        if 'premium_amount' in policy_data:
            premium_amount = policy_data['premium_amount']
            if premium_amount < 0:
                raise PolicyValidationError(
                    f"Premium amount must be >= 0. Got: {premium_amount}"
                )

        # Date validation
        if 'start_date' in policy_data and 'end_date' in policy_data:
            start_date = policy_data['start_date']
            end_date = policy_data['end_date']
            if end_date and start_date >= end_date:
                raise PolicyValidationError(
                    f"End date must be after start date. Start: {start_date}, End: {end_date}"
                )

        # Trust validation
        if policy_data.get('written_in_trust'):
            trust_details = policy_data.get('trust_details')
            if not trust_details:
                raise PolicyValidationError(
                    "Trust details are required when policy is written in trust"
                )

            if not trust_details.get('trust_type'):
                raise PolicyValidationError(
                    "Trust type is required when policy is written in trust"
                )

            if not trust_details.get('trustees'):
                raise PolicyValidationError(
                    "At least one trustee is required when policy is written in trust"
                )

    async def _get_policy_with_auth(
        self,
        policy_id: UUID,
        user_id: UUID
    ) -> LifeAssurancePolicy:
        """
        Get policy and verify user owns it.

        Args:
            policy_id: Policy ID
            user_id: User ID for authorization

        Returns:
            LifeAssurancePolicy: Policy if authorized

        Raises:
            PolicyNotFoundError: If policy doesn't exist or is deleted
            PolicyPermissionError: If user doesn't own policy
        """
        stmt = select(LifeAssurancePolicy).where(
            LifeAssurancePolicy.id == policy_id,
            LifeAssurancePolicy.is_deleted == False
        )

        result = await self.db.execute(stmt)
        policy = result.scalar_one_or_none()

        if not policy:
            raise PolicyNotFoundError(
                f"Policy {policy_id} not found or has been deleted"
            )

        if policy.user_id != user_id:
            raise PolicyPermissionError(
                f"User {user_id} does not have permission to access policy {policy_id}"
            )

        return policy
