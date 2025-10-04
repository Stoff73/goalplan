"""
Annual Allowance Service

Provides UK pension Annual Allowance calculations including:
- Standard annual allowance (£60,000)
- Money Purchase Annual Allowance (MPAA) (£10,000)
- Tapered annual allowance for high earners
- Carry forward from previous 3 years
- Annual allowance usage tracking
- Annual allowance charge calculations

Business Rules:
- Standard AA: £60,000 (2024/25)
- MPAA: £10,000 (if triggered by flexible access)
- Tapering: £1 reduction per £2 over £260,000 adjusted income
- Minimum tapered allowance: £10,000
- Carry forward: Look back 3 previous tax years
- Carry forward: Use oldest first (FIFO)
- Excess contributions subject to tax charge at marginal rate

Tax Years:
- UK tax year: April 6 to April 5
- Format: YYYY/YY (e.g., 2024/25)

Performance:
- Target: <100ms for calculations
- Target: <200ms for carry forward lookback
- Async database operations throughout
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.retirement import (
    UKPension, UKPensionContribution, AnnualAllowanceTracking
)

logger = logging.getLogger(__name__)


class AnnualAllowanceService:
    """Service for UK pension Annual Allowance calculations."""

    # Constants (2024/25 tax year)
    STANDARD_ANNUAL_ALLOWANCE = Decimal('60000.00')
    MPAA_ALLOWANCE = Decimal('10000.00')
    TAPER_THRESHOLD = Decimal('260000.00')
    TAPER_RATE = Decimal('0.50')  # £1 reduction per £2 over threshold
    MINIMUM_TAPERED_ALLOWANCE = Decimal('10000.00')

    def __init__(self, db: AsyncSession):
        """
        Initialize Annual Allowance service.

        Args:
            db: Database session for operations
        """
        self.db = db

    def calculate_annual_allowance(
        self,
        user_id: UUID,
        tax_year: str,
        adjusted_income: Decimal,
        mpaa_triggered: bool = False
    ) -> Decimal:
        """
        Calculate applicable annual allowance for a user.

        Args:
            user_id: User UUID
            tax_year: Tax year (format: YYYY/YY)
            adjusted_income: Adjusted income for taper calculation
            mpaa_triggered: Whether MPAA has been triggered

        Returns:
            Applicable annual allowance amount

        Business Logic:
            1. If MPAA triggered: £10,000
            2. If adjusted_income > £260,000: apply tapering
               - Reduction: £1 per £2 over threshold
               - Minimum: £10,000
            3. Otherwise: £60,000 standard allowance
        """
        logger.info(
            f"Calculating annual allowance for user {user_id}, tax year {tax_year}, "
            f"adjusted_income={adjusted_income}, mpaa_triggered={mpaa_triggered}"
        )

        # If MPAA triggered, reduced allowance applies
        if mpaa_triggered:
            logger.info(f"MPAA triggered - allowance: {self.MPAA_ALLOWANCE}")
            return self.MPAA_ALLOWANCE

        # If adjusted income exceeds threshold, apply tapering
        if adjusted_income > self.TAPER_THRESHOLD:
            excess_income = adjusted_income - self.TAPER_THRESHOLD
            reduction = excess_income * self.TAPER_RATE

            tapered_allowance = self.STANDARD_ANNUAL_ALLOWANCE - reduction

            # Ensure minimum tapered allowance
            tapered_allowance = max(tapered_allowance, self.MINIMUM_TAPERED_ALLOWANCE)

            logger.info(
                f"Tapered allowance applied: adjusted_income={adjusted_income}, "
                f"excess={excess_income}, reduction={reduction}, "
                f"tapered_allowance={tapered_allowance}"
            )

            return tapered_allowance

        # Standard allowance
        logger.info(f"Standard allowance: {self.STANDARD_ANNUAL_ALLOWANCE}")
        return self.STANDARD_ANNUAL_ALLOWANCE

    async def calculate_carry_forward(
        self,
        user_id: UUID,
        tax_year: str
    ) -> Dict[str, Decimal]:
        """
        Calculate carry forward available from previous 3 years.

        Looks back at previous 3 tax years and calculates unused allowance
        that can be carried forward to current year.

        Args:
            user_id: User UUID
            tax_year: Current tax year (format: YYYY/YY)

        Returns:
            Dict mapping tax year to unused allowance:
            {
                "2021/22": Decimal("10000.00"),
                "2022/23": Decimal("5000.00"),
                "2023/24": Decimal("15000.00")
            }

        Business Logic:
            - Look back 3 previous tax years
            - For each year: unused = annual_allowance - contributions
            - Only carry forward if positive unused amount
            - Use FIFO: oldest unused allowance first
        """
        logger.info(f"Calculating carry forward for user {user_id}, tax year {tax_year}")

        # Parse current tax year to get previous years
        # Format: YYYY/YY -> e.g., "2024/25"
        year_parts = tax_year.split('/')
        if len(year_parts) != 2:
            logger.error(f"Invalid tax year format: {tax_year}")
            return {}

        current_year_start = int(year_parts[0])

        # Calculate previous 3 tax years
        previous_years = []
        for i in range(1, 4):
            prev_year_start = current_year_start - i
            prev_year_end = str(prev_year_start + 1)[-2:]
            prev_tax_year = f"{prev_year_start}/{prev_year_end}"
            previous_years.append(prev_tax_year)

        # Reverse to get oldest first (FIFO)
        previous_years.reverse()

        logger.info(f"Looking back at tax years: {previous_years}")

        carry_forward = {}

        for prev_year in previous_years:
            # Get AA tracking for this year
            result = await self.db.execute(
                select(AnnualAllowanceTracking).where(
                    and_(
                        AnnualAllowanceTracking.user_id == user_id,
                        AnnualAllowanceTracking.tax_year == prev_year
                    )
                )
            )
            aa_tracking = result.scalar_one_or_none()

            if aa_tracking:
                # Calculate unused allowance
                unused = aa_tracking.annual_allowance_limit - aa_tracking.allowance_used

                if unused > 0:
                    carry_forward[prev_year] = unused
                    logger.debug(f"Carry forward from {prev_year}: {unused}")
            else:
                # No tracking record - assume full allowance available
                # (user may not have contributed in that year)
                carry_forward[prev_year] = self.STANDARD_ANNUAL_ALLOWANCE
                logger.debug(f"No tracking for {prev_year} - assuming full allowance available")

        total_carry_forward = sum(carry_forward.values())
        logger.info(f"Total carry forward available: {total_carry_forward}")

        return carry_forward

    async def calculate_allowance_usage(
        self,
        user_id: UUID,
        tax_year: str
    ) -> Dict[str, Any]:
        """
        Calculate annual allowance usage for a tax year.

        Includes:
        - Total contributions for the year
        - Applicable annual allowance
        - Carry forward available
        - Allowance used, remaining, and excess (if any)

        Args:
            user_id: User UUID
            tax_year: Tax year (format: YYYY/YY)

        Returns:
            Dict with:
                - tax_year: str
                - total_contributions: Decimal
                - annual_allowance: Decimal
                - carry_forward: Dict[str, Decimal]
                - total_carry_forward: Decimal
                - allowance_used: Decimal
                - allowance_remaining: Decimal
                - excess: Decimal (0 if no excess)
                - mpaa_applies: bool
                - tapered: bool
        """
        logger.info(f"Calculating allowance usage for user {user_id}, tax year {tax_year}")

        # Get all contributions for this tax year
        contributions_result = await self.db.execute(
            select(UKPensionContribution)
            .join(UKPension)
            .where(
                and_(
                    UKPension.user_id == user_id,
                    UKPensionContribution.tax_year == tax_year,
                    UKPension.is_deleted == False
                )
            )
        )
        contributions = contributions_result.scalars().all()

        # Calculate total contributions
        total_contributions = Decimal('0.00')
        for contribution in contributions:
            total_contributions += contribution.total_contribution

        # Check if MPAA applies (any pension has mpaa_triggered)
        mpaa_result = await self.db.execute(
            select(UKPension).where(
                and_(
                    UKPension.user_id == user_id,
                    UKPension.mpaa_triggered == True,
                    UKPension.is_deleted == False
                )
            )
        )
        mpaa_triggered = mpaa_result.scalar_one_or_none() is not None

        # For now, assume no tapering (would require user income data)
        # In production, this would fetch from user income records
        adjusted_income = Decimal('0.00')
        tapered = False

        # Calculate annual allowance
        annual_allowance = self.calculate_annual_allowance(
            user_id,
            tax_year,
            adjusted_income,
            mpaa_triggered
        )

        # Calculate carry forward
        carry_forward = await self.calculate_carry_forward(user_id, tax_year)
        total_carry_forward = sum(carry_forward.values())

        # Calculate usage
        total_available = annual_allowance + total_carry_forward
        allowance_used = min(total_contributions, total_available)
        allowance_remaining = max(Decimal('0.00'), total_available - total_contributions)
        excess = max(Decimal('0.00'), total_contributions - total_available)

        usage = {
            "tax_year": tax_year,
            "total_contributions": total_contributions,
            "annual_allowance": annual_allowance,
            "carry_forward": carry_forward,
            "total_carry_forward": total_carry_forward,
            "total_available": total_available,
            "allowance_used": allowance_used,
            "allowance_remaining": allowance_remaining,
            "excess": excess,
            "mpaa_applies": mpaa_triggered,
            "tapered": tapered
        }

        logger.info(
            f"Allowance usage calculated: contributions={total_contributions}, "
            f"allowance={annual_allowance}, used={allowance_used}, "
            f"remaining={allowance_remaining}, excess={excess}"
        )

        return usage

    async def check_annual_allowance_charge(
        self,
        user_id: UUID,
        tax_year: str,
        marginal_rate: Decimal
    ) -> Dict[str, Any]:
        """
        Check if annual allowance charge applies and calculate amount.

        Args:
            user_id: User UUID
            tax_year: Tax year (format: YYYY/YY)
            marginal_rate: User's marginal tax rate (e.g., 0.40 for 40%)

        Returns:
            Dict with:
                - charge_applies: bool
                - excess_contributions: Decimal
                - charge_amount: Decimal
                - explanation: str

        Business Logic:
            - Charge applies if contributions > (allowance + carry_forward)
            - Charge = excess * marginal_rate
            - User pays charge via self-assessment or Scheme Pays
        """
        logger.info(
            f"Checking annual allowance charge for user {user_id}, "
            f"tax year {tax_year}, marginal_rate={marginal_rate}"
        )

        # Get allowance usage
        usage = await self.calculate_allowance_usage(user_id, tax_year)

        excess = usage['excess']

        if excess <= 0:
            return {
                "charge_applies": False,
                "excess_contributions": Decimal('0.00'),
                "charge_amount": Decimal('0.00'),
                "explanation": "No annual allowance charge - contributions within limits"
            }

        # Calculate charge
        charge_amount = excess * marginal_rate

        explanation = (
            f"Annual allowance charge applies. You contributed £{usage['total_contributions']:.2f} "
            f"but your available allowance (including carry forward) was £{usage['total_available']:.2f}. "
            f"Excess contributions of £{excess:.2f} will be taxed at your marginal rate of {marginal_rate * 100:.0f}%, "
            f"resulting in a charge of £{charge_amount:.2f}."
        )

        logger.info(f"Annual allowance charge: excess={excess}, charge={charge_amount}")

        return {
            "charge_applies": True,
            "excess_contributions": excess,
            "charge_amount": charge_amount,
            "marginal_rate": marginal_rate,
            "explanation": explanation
        }

    async def update_annual_allowance_tracking(
        self,
        user_id: UUID,
        tax_year: str
    ) -> AnnualAllowanceTracking:
        """
        Update or create annual allowance tracking record.

        Recalculates current usage and updates tracking record.

        Args:
            user_id: User UUID
            tax_year: Tax year (format: YYYY/YY)

        Returns:
            Updated or created AnnualAllowanceTracking record
        """
        logger.info(f"Updating AA tracking for user {user_id}, tax year {tax_year}")

        # Calculate current usage
        usage = await self.calculate_allowance_usage(user_id, tax_year)

        # Check if tracking record exists
        result = await self.db.execute(
            select(AnnualAllowanceTracking).where(
                and_(
                    AnnualAllowanceTracking.user_id == user_id,
                    AnnualAllowanceTracking.tax_year == tax_year
                )
            )
        )
        tracking = result.scalar_one_or_none()

        if tracking:
            # Update existing record
            tracking.total_contributions = usage['total_contributions']
            tracking.annual_allowance_limit = usage['annual_allowance']
            tracking.carry_forward_available = usage['carry_forward']
            tracking.tapered_allowance = usage['tapered']
            tracking.allowance_used = usage['allowance_used']
            tracking.allowance_remaining = usage['allowance_remaining']

            logger.info(f"Updated existing AA tracking record: {tracking.id}")
        else:
            # Create new record
            import uuid
            from datetime import datetime

            tracking = AnnualAllowanceTracking(
                id=uuid.uuid4(),
                user_id=user_id,
                tax_year=tax_year,
                total_contributions=usage['total_contributions'],
                annual_allowance_limit=usage['annual_allowance'],
                carry_forward_available=usage['carry_forward'],
                tapered_allowance=usage['tapered'],
                adjusted_income=None,
                allowance_used=usage['allowance_used'],
                allowance_remaining=usage['allowance_remaining'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(tracking)
            logger.info(f"Created new AA tracking record for {tax_year}")

        await self.db.commit()
        await self.db.refresh(tracking)

        return tracking


# Factory function
def get_annual_allowance_service(db: AsyncSession) -> AnnualAllowanceService:
    """
    Get Annual Allowance service instance.

    Args:
        db: Database session

    Returns:
        AnnualAllowanceService instance
    """
    return AnnualAllowanceService(db)
