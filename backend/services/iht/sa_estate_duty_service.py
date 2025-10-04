"""
SA Estate Duty Service

Provides comprehensive South African Estate Duty calculation including:
- SA estate value calculation (SA-situs assets)
- SA Estate Duty calculation with abatement
- Tiered rate application (20% up to R30M, 25% above)
- Estate Duty calculation storage for audit trail

Business Rules:
- SA Abatement: R3,500,000 (2024)
- SA Estate Duty rates (tiered):
  - First R30,000,000: 20%
  - Above R30,000,000: 25%
- Only SA-situs assets included in SA estate
- Deductible liabilities reduce estate value
- All calculations use Decimal for precision
- Temporal data filtering (effective_from/effective_to)

Performance:
- Target: <500ms for estate duty calculation
- Target: <200ms for SA estate value queries
- Async database operations throughout
"""

import logging
import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.estate_iht import (
    EstateAsset, EstateLiability, SAEstateDutyCalculation
)

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when estate duty data validation fails."""
    pass


class NotFoundError(Exception):
    """Raised when estate entity not found."""
    pass


class SAEstateDutyService:
    """Service for South African Estate Duty calculations."""

    # Constants (2024)
    SA_ABATEMENT = Decimal('3500000.00')  # R3.5M
    SA_TIER_THRESHOLD = Decimal('30000000.00')  # R30M
    SA_RATE_TIER_1 = Decimal('0.20')  # 20% on first R30M
    SA_RATE_TIER_2 = Decimal('0.25')  # 25% above R30M

    def __init__(self, db: AsyncSession):
        """
        Initialize SA estate duty service.

        Args:
            db: Database session for operations
        """
        self.db = db

    async def calculate_sa_estate_value(
        self,
        user_id: UUID,
        as_of_date: Optional[date] = None
    ) -> Decimal:
        """
        Calculate SA estate value (all SA-situs assets).

        Queries all EstateAssets for user where included_in_sa_estate=True,
        filters by temporal data (effective_from/effective_to), and sums values in ZAR.

        Args:
            user_id: User UUID
            as_of_date: Date for temporal query (default: today)

        Returns:
            SA estate value in ZAR

        Business Logic:
            - Only include assets where included_in_sa_estate=True
            - Filter by effective_from <= as_of_date < effective_to
            - If effective_to IS NULL, asset is current
            - Sum all asset values (assumes ZAR, currency conversion TBD)
        """
        if as_of_date is None:
            as_of_date = date.today()

        logger.info(f"Calculating SA estate value for user {user_id} as of {as_of_date}")

        # Query assets with temporal filtering
        result = await self.db.execute(
            select(func.sum(EstateAsset.estimated_value)).where(
                and_(
                    EstateAsset.user_id == user_id,
                    EstateAsset.included_in_sa_estate == True,
                    EstateAsset.is_deleted == False,
                    EstateAsset.effective_from <= as_of_date,
                    (
                        (EstateAsset.effective_to.is_(None)) |
                        (EstateAsset.effective_to > as_of_date)
                    )
                )
            )
        )

        estate_value = result.scalar()

        if estate_value is None:
            estate_value = Decimal('0.00')
        else:
            estate_value = Decimal(str(estate_value))

        logger.info(f"SA estate value calculated: R{estate_value:,.2f}")
        return estate_value

    async def calculate_estate_duty(
        self,
        user_id: UUID,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculate SA Estate Duty with full breakdown.

        Args:
            user_id: User UUID
            as_of_date: Date for calculation (default: today)

        Returns:
            Dict with complete Estate Duty calculation breakdown:
                - estate_value: Decimal (gross SA estate)
                - liabilities: Decimal (deductible liabilities)
                - net_estate: Decimal (estate_value - liabilities)
                - abatement: Decimal (R3,500,000)
                - dutiable_amount: Decimal (max(0, net_estate - abatement))
                - estate_duty_owed: Decimal (tiered calculation)
                - effective_rate: Decimal (estate_duty / net_estate as percentage)

        Business Logic:
            - Calculate SA estate value
            - Deduct deductible liabilities
            - Net estate = estate_value - liabilities
            - Abatement = R3,500,000 (2024)
            - Dutiable amount = max(0, net_estate - abatement)
            - Tiered Estate Duty:
              - If dutiable_amount <= R30,000,000:
                duty = dutiable_amount * 20%
              - If dutiable_amount > R30,000,000:
                duty = (R30,000,000 * 20%) + ((dutiable_amount - R30,000,000) * 25%)
        """
        if as_of_date is None:
            as_of_date = date.today()

        logger.info(f"Calculating SA Estate Duty for user {user_id} as of {as_of_date}")

        # Calculate SA estate value
        estate_value = await self.calculate_sa_estate_value(user_id, as_of_date)

        # Query deductible liabilities with temporal filtering
        # Note: Using same deductible_from_estate flag for simplicity
        # In production, might have separate SA-specific deductibility flag
        result = await self.db.execute(
            select(func.sum(EstateLiability.amount_outstanding)).where(
                and_(
                    EstateLiability.user_id == user_id,
                    EstateLiability.deductible_from_estate == True,
                    EstateLiability.is_deleted == False,
                    EstateLiability.effective_from <= as_of_date,
                    (
                        (EstateLiability.effective_to.is_(None)) |
                        (EstateLiability.effective_to > as_of_date)
                    )
                )
            )
        )

        liabilities = result.scalar()

        if liabilities is None:
            liabilities = Decimal('0.00')
        else:
            liabilities = Decimal(str(liabilities))

        # Calculate net estate
        net_estate = estate_value - liabilities

        # Apply abatement
        abatement = self.SA_ABATEMENT
        dutiable_amount = max(Decimal('0.00'), net_estate - abatement)

        # Calculate estate duty with tiered rates
        if dutiable_amount <= self.SA_TIER_THRESHOLD:
            # 20% on full amount
            estate_duty_owed = dutiable_amount * self.SA_RATE_TIER_1
        else:
            # 20% on first R30M + 25% on excess
            duty_tier_1 = self.SA_TIER_THRESHOLD * self.SA_RATE_TIER_1
            excess = dutiable_amount - self.SA_TIER_THRESHOLD
            duty_tier_2 = excess * self.SA_RATE_TIER_2
            estate_duty_owed = duty_tier_1 + duty_tier_2

        # Calculate effective rate
        if net_estate > Decimal('0.00'):
            effective_rate = (estate_duty_owed / net_estate) * Decimal('100')
        else:
            effective_rate = Decimal('0.00')

        result = {
            "estate_value": estate_value,
            "liabilities": liabilities,
            "net_estate": net_estate,
            "abatement": abatement,
            "dutiable_amount": dutiable_amount,
            "estate_duty_owed": estate_duty_owed,
            "effective_rate": effective_rate
        }

        logger.info(
            f"SA Estate Duty calculated: net_estate=R{net_estate:,.2f}, "
            f"abatement=R{abatement:,.2f}, "
            f"dutiable=R{dutiable_amount:,.2f}, "
            f"duty_owed=R{estate_duty_owed:,.2f}, "
            f"effective_rate={effective_rate:.2f}%"
        )

        return result

    async def save_estate_duty_calculation(
        self,
        user_id: UUID,
        calculation_data: Dict[str, Any]
    ) -> SAEstateDutyCalculation:
        """
        Save SA Estate Duty calculation for audit trail.

        Args:
            user_id: User UUID
            calculation_data: Dict from calculate_estate_duty() containing all components

        Returns:
            Saved SAEstateDutyCalculation record

        Raises:
            ValidationError: If calculation_data is invalid
        """
        logger.info(f"Saving SA Estate Duty calculation for user {user_id}")

        # Validate required fields in calculation_data
        required_fields = [
            'estate_value', 'liabilities', 'net_estate',
            'abatement', 'dutiable_amount', 'estate_duty_owed'
        ]
        for field in required_fields:
            if field not in calculation_data:
                raise ValidationError(f"Missing required field in calculation_data: {field}")

        # Determine estate duty rate (for storage)
        # Use simple logic: if dutiable_amount <= R30M, use 20%, else effective rate
        dutiable_amount = calculation_data['dutiable_amount']
        if dutiable_amount <= self.SA_TIER_THRESHOLD:
            estate_duty_rate = self.SA_RATE_TIER_1 * Decimal('100')  # Convert to percentage
        else:
            estate_duty_rate = calculation_data.get('effective_rate', Decimal('20.00'))

        # Create calculation record
        calculation = SAEstateDutyCalculation(
            id=uuid.uuid4(),
            user_id=user_id,
            calculation_date=date.today(),
            estate_value=calculation_data['estate_value'],
            abatement=calculation_data['abatement'],
            dutiable_amount=calculation_data['dutiable_amount'],
            estate_duty_rate=estate_duty_rate,
            estate_duty_owed=calculation_data['estate_duty_owed'],
            currency='ZAR'
        )

        self.db.add(calculation)
        await self.db.commit()
        await self.db.refresh(calculation)

        logger.info(f"SA Estate Duty calculation saved: id={calculation.id}")
        return calculation


# Factory function
def get_sa_estate_duty_service(db: AsyncSession) -> SAEstateDutyService:
    """
    Get SA estate duty service instance.

    Args:
        db: Database session

    Returns:
        SAEstateDutyService instance
    """
    return SAEstateDutyService(db)
