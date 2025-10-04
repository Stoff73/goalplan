"""
Tax Treatment Service for Life Assurance Protection Module.

This service handles tax implications of life assurance policies across UK and SA:
- UK Inheritance Tax (IHT) impact determination
- SA Estate Duty impact determination
- Trust structure tax optimization
- Estate value impact calculations

Business Rules (from Protection.md):
- UK policies written in trust are OUTSIDE the UK estate for IHT
- UK policies NOT in trust are IN the UK estate for IHT
- SA policies are generally IN the estate for estate duty
- UK IHT rate: 40% on estate
- SA Estate Duty: 20% on amounts above R30 million threshold

Tax Rates:
- UK IHT: 40% of cover amount if in estate
- SA Estate Duty: 20% on portion above R30,000,000 threshold
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from models.life_assurance import (
    LifeAssurancePolicy,
    ProviderCountry,
    PolicyStatus
)

logger = logging.getLogger(__name__)

# Tax Constants
UK_IHT_RATE = Decimal('0.40')  # 40%
SA_ESTATE_DUTY_RATE = Decimal('0.20')  # 20%
SA_ESTATE_DUTY_THRESHOLD = Decimal('30000000.00')  # R30 million


class TaxTreatmentService:
    """Service for determining tax treatment of life assurance policies."""

    def __init__(self, db: AsyncSession):
        """
        Initialize tax treatment service.

        Args:
            db: Async database session
        """
        self.db = db

    def determine_iht_impact(self, policy: LifeAssurancePolicy) -> Dict:
        """
        Determine if UK policy is in the IHT estate.

        Business Logic from Protection.md:
            IF provider_country = 'UK' AND written_in_trust = TRUE:
                outside_uk_estate_for_iht = TRUE
                explanation = "Policy written in trust - outside UK estate for IHT purposes"
            ELSE IF provider_country = 'UK' AND written_in_trust = FALSE:
                in_uk_estate_for_iht = TRUE
                explanation = "Policy NOT in trust - forms part of UK estate for IHT"
            ELSE:
                Not applicable (non-UK policy)

        Args:
            policy: LifeAssurancePolicy instance

        Returns:
            dict: IHT impact details with:
                - iht_applicable: bool (True if UK policy)
                - in_estate: bool (True if in IHT estate, False if outside)
                - explanation: str
                - trust_type: str | None (Type of trust if in trust)
                - potential_iht_liability: Decimal | None (40% of cover if in estate)
        """
        # Check if UK policy
        if policy.provider_country != ProviderCountry.UK:
            return {
                'iht_applicable': False,
                'in_estate': False,
                'explanation': 'Not a UK policy - UK IHT not applicable',
                'trust_type': None,
                'potential_iht_liability': None
            }

        # UK policy - check if in trust
        if policy.written_in_trust:
            return {
                'iht_applicable': True,
                'in_estate': False,
                'explanation': 'Policy written in trust - outside UK estate for IHT purposes',
                'trust_type': policy.trust_type.value if policy.trust_type else None,
                'potential_iht_liability': Decimal('0.00')
            }
        else:
            # UK policy NOT in trust - in estate
            # Calculate potential IHT liability: 40% of cover amount
            cover_gbp = policy.cover_amount_gbp or policy.cover_amount
            potential_liability = cover_gbp * UK_IHT_RATE

            return {
                'iht_applicable': True,
                'in_estate': True,
                'explanation': 'Policy NOT in trust - forms part of UK estate for IHT',
                'trust_type': None,
                'potential_iht_liability': potential_liability
            }

    def determine_sa_estate_duty_impact(self, policy: LifeAssurancePolicy) -> Dict:
        """
        Determine if SA policy is subject to estate duty.

        Business Logic from Protection.md:
            IF provider_country = 'SA':
                SA policies generally part of estate
                Estate duty = 20% on portion above R30 million threshold

        Args:
            policy: LifeAssurancePolicy instance

        Returns:
            dict: SA estate duty details with:
                - estate_duty_applicable: bool (True if SA policy)
                - in_estate: bool (Always True for SA policies)
                - explanation: str
                - threshold: Decimal (R30,000,000)
                - rate: Decimal (0.20 / 20%)
                - notes: str (Additional SA-specific notes)
        """
        # Check if SA policy
        if policy.provider_country != ProviderCountry.SA:
            return {
                'estate_duty_applicable': False,
                'in_estate': False,
                'explanation': 'Not a SA policy - SA Estate Duty not applicable',
                'threshold': None,
                'rate': None,
                'notes': None
            }

        # SA policy - always in estate
        return {
            'estate_duty_applicable': True,
            'in_estate': True,
            'explanation': 'SA policy forms part of estate for Estate Duty purposes',
            'threshold': SA_ESTATE_DUTY_THRESHOLD,
            'rate': SA_ESTATE_DUTY_RATE,
            'notes': 'Estate Duty applies at 20% on the portion of the estate above R30 million threshold'
        }

    def get_policy_tax_summary(self, policy: LifeAssurancePolicy) -> Dict:
        """
        Get comprehensive tax treatment for any policy.

        Calls both determine_iht_impact() and determine_sa_estate_duty_impact()
        and provides tax planning recommendations.

        Args:
            policy: LifeAssurancePolicy instance

        Returns:
            dict: Combined tax summary with:
                - policy_id: UUID
                - provider_country: str
                - written_in_trust: bool
                - uk_tax_treatment: dict (from determine_iht_impact)
                - sa_tax_treatment: dict (from determine_sa_estate_duty_impact)
                - recommendations: list[str] (Tax planning recommendations)
        """
        # Get UK and SA tax treatments
        uk_treatment = self.determine_iht_impact(policy)
        sa_treatment = self.determine_sa_estate_duty_impact(policy)

        # Build recommendations
        recommendations = []

        # UK policy recommendations
        if policy.provider_country == ProviderCountry.UK:
            if not policy.written_in_trust:
                recommendations.append(
                    "Consider placing policy in trust to remove from IHT estate"
                )
            else:
                recommendations.append(
                    "Policy correctly structured for IHT efficiency"
                )

        # SA policy recommendations
        if policy.provider_country == ProviderCountry.SA:
            cover_zar = policy.cover_amount_zar or policy.cover_amount
            if cover_zar > Decimal('10000000.00'):  # High value policy
                recommendations.append(
                    "Consult with SA estate planner regarding R30m threshold"
                )

        return {
            'policy_id': policy.id,
            'provider_country': policy.provider_country.value,
            'written_in_trust': policy.written_in_trust,
            'uk_tax_treatment': uk_treatment,
            'sa_tax_treatment': sa_treatment,
            'recommendations': recommendations
        }

    async def calculate_estate_value_impact(
        self,
        user_id: UUID
    ) -> Dict:
        """
        Calculate total impact on user's estate from all active policies.

        Gets all active policies for user, sums those in UK estate (not in trust)
        and SA policies, and calculates potential tax liabilities.

        Args:
            user_id: User UUID

        Returns:
            dict: Estate impact summary with:
                - total_uk_policies_in_estate: Decimal (Sum of UK non-trust policies)
                - total_sa_policies_in_estate: Decimal (Sum of SA policies)
                - potential_uk_iht: Decimal (40% of UK policies in estate)
                - policies_in_uk_estate_count: int
                - policies_in_sa_estate_count: int
                - recommendations: list[str]
        """
        # Get all active policies for user
        stmt = select(LifeAssurancePolicy).where(
            and_(
                LifeAssurancePolicy.user_id == user_id,
                LifeAssurancePolicy.status == PolicyStatus.ACTIVE,
                LifeAssurancePolicy.is_deleted == False
            )
        )

        result = await self.db.execute(stmt)
        policies = result.scalars().all()

        # Initialize totals
        total_uk_in_estate = Decimal('0.00')
        total_sa_in_estate = Decimal('0.00')
        uk_count = 0
        sa_count = 0

        # Process each policy
        for policy in policies:
            # UK policies NOT in trust
            if policy.provider_country == ProviderCountry.UK and not policy.written_in_trust:
                cover_gbp = policy.cover_amount_gbp or policy.cover_amount
                total_uk_in_estate += cover_gbp
                uk_count += 1

            # SA policies (always in estate)
            if policy.provider_country == ProviderCountry.SA:
                cover_zar = policy.cover_amount_zar or policy.cover_amount
                total_sa_in_estate += cover_zar
                sa_count += 1

        # Calculate potential UK IHT (40% of UK policies in estate)
        potential_uk_iht = total_uk_in_estate * UK_IHT_RATE

        # Build recommendations
        recommendations = []

        if uk_count > 0:
            recommendations.append(
                f"{uk_count} UK {'policy' if uk_count == 1 else 'policies'} in estate. "
                f"Consider trust arrangements to reduce IHT liability of £{potential_uk_iht:,.2f}"
            )

        if total_sa_in_estate > SA_ESTATE_DUTY_THRESHOLD:
            recommendations.append(
                f"SA policies total R{total_sa_in_estate:,.2f}, which exceeds the "
                f"R30 million estate duty threshold. Estate planning recommended."
            )

        if not policies:
            recommendations.append(
                "No active life assurance policies found. Consider coverage needs analysis."
            )

        return {
            'total_uk_policies_in_estate': total_uk_in_estate,
            'total_sa_policies_in_estate': total_sa_in_estate,
            'potential_uk_iht': potential_uk_iht,
            'policies_in_uk_estate_count': uk_count,
            'policies_in_sa_estate_count': sa_count,
            'recommendations': recommendations
        }

    async def get_policy_tax_treatment_by_id(
        self,
        policy_id: UUID,
        user_id: UUID
    ) -> Dict:
        """
        Get tax treatment for a specific policy by ID.

        Args:
            policy_id: Policy UUID
            user_id: User UUID (for authorization)

        Returns:
            dict: Tax treatment summary

        Raises:
            ValueError: If policy not found or user doesn't own it
        """
        # Get policy
        stmt = select(LifeAssurancePolicy).where(
            and_(
                LifeAssurancePolicy.id == policy_id,
                LifeAssurancePolicy.user_id == user_id,
                LifeAssurancePolicy.is_deleted == False
            )
        )

        result = await self.db.execute(stmt)
        policy = result.scalar_one_or_none()

        if not policy:
            raise ValueError(
                f"Policy {policy_id} not found or user {user_id} doesn't have permission"
            )

        return self.get_policy_tax_summary(policy)
