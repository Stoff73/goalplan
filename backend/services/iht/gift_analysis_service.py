"""
Gift Analysis Service

Provides comprehensive lifetime gift tracking and PET analysis including:
- Gift recording with automatic classification (PET, EXEMPT, CHARGEABLE)
- Exemption application (annual, small gifts, wedding, etc.)
- 7-year PET period tracking
- Taper relief calculation
- Potential IHT calculation on gifts

Business Rules:
- Annual exemption: £3,000/year (can carry forward 1 year unused)
- Small gifts: £250/person/year (cannot use with annual exemption)
- Wedding gifts: £5,000 (child), £2,500 (grandchild), £1,000 (other)
- PETs become exempt after 7 years if donor survives
- Taper relief: 0-3 years (0%), 3-4 (20%), 4-5 (40%), 5-6 (60%), 6-7 (80%), 7+ (100%)
- Taper relief reduces TAX, not value
- IHT rate on gifts: 20% (lifetime) becomes 40% (death) with taper relief

Performance:
- Target: <200ms for gift recording
- Target: <500ms for PET analysis with calculations
- Async database operations throughout
"""

import logging
import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from dateutil.relativedelta import relativedelta

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.estate_iht import (
    Gift, GiftType, ExemptionType, IHTExemption
)

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when gift data validation fails."""
    pass


class NotFoundError(Exception):
    """Raised when gift entity not found."""
    pass


class GiftAnalysisService:
    """Service for lifetime gift tracking and PET analysis."""

    # Constants
    ANNUAL_EXEMPTION_LIMIT = Decimal('3000.00')
    SMALL_GIFT_LIMIT = Decimal('250.00')
    WEDDING_GIFT_CHILD = Decimal('5000.00')
    WEDDING_GIFT_GRANDCHILD = Decimal('2500.00')
    WEDDING_GIFT_OTHER = Decimal('1000.00')

    def __init__(self, db: AsyncSession):
        """
        Initialize gift analysis service.

        Args:
            db: Database session for operations
        """
        self.db = db

    async def record_gift(
        self,
        user_id: UUID,
        gift_data: Dict[str, Any]
    ) -> Gift:
        """
        Record a lifetime gift with automatic classification and exemption application.

        Args:
            user_id: User UUID
            gift_data: Dict containing:
                - recipient: str (required)
                - gift_date: date (required)
                - gift_value: Decimal (required)
                - currency: str (default: 'GBP')
                - description: Optional[str]
                - exemption_type: Optional[ExemptionType]

        Returns:
            Created Gift record

        Raises:
            ValidationError: If gift data is invalid

        Business Logic:
            - Validates gift data (value > 0, date <= today)
            - Determines gift_type based on exemption_type:
              - SPOUSE/CHARITY exemption -> EXEMPT
              - Otherwise -> PET (Potentially Exempt Transfer)
            - Calculates becomes_exempt_date for PETs (gift_date + 7 years)
            - Applies exemptions if specified
        """
        logger.info(
            f"Recording gift for user {user_id}: "
            f"recipient={gift_data.get('recipient')}, value={gift_data.get('gift_value')}"
        )

        # Validate required fields
        required_fields = ['recipient', 'gift_date', 'gift_value']
        for field in required_fields:
            if field not in gift_data:
                raise ValidationError(f"Missing required field: {field}")

        # Validate gift value
        gift_value = Decimal(str(gift_data['gift_value']))
        if gift_value <= Decimal('0.00'):
            raise ValidationError(f"Gift value must be positive. Got: {gift_value}")

        # Validate gift date
        gift_date = gift_data['gift_date']
        if gift_date > date.today():
            raise ValidationError(f"Gift date cannot be in future: {gift_date}")

        # Determine gift classification
        exemption_type = gift_data.get('exemption_type')
        if exemption_type == ExemptionType.SPOUSE or exemption_type == ExemptionType.CHARITY:
            # Immediately exempt
            gift_type = GiftType.EXEMPT
            becomes_exempt_date = gift_date
            still_in_pet_period = False
        elif exemption_type in [
            ExemptionType.ANNUAL_EXEMPTION,
            ExemptionType.SMALL_GIFTS,
            ExemptionType.WEDDING
        ]:
            # Try to apply exemption - if fully covered, EXEMPT, otherwise PET
            exemption_applied = await self.apply_exemptions(
                user_id,
                gift_value,
                gift_date.year,  # Use calendar year for simplicity
                exemption_type.value if exemption_type else "ANNUAL_EXEMPTION"
            )

            if exemption_applied['remaining_gift_value'] == Decimal('0.00'):
                gift_type = GiftType.EXEMPT
                becomes_exempt_date = gift_date
                still_in_pet_period = False
            else:
                gift_type = GiftType.PET
                becomes_exempt_date = gift_date + relativedelta(years=7)
                still_in_pet_period = True
        else:
            # Default: PET
            gift_type = GiftType.PET
            becomes_exempt_date = gift_date + relativedelta(years=7)
            still_in_pet_period = True

        # Create gift record
        gift = Gift(
            id=uuid.uuid4(),
            user_id=user_id,
            recipient=gift_data['recipient'],
            gift_date=gift_date,
            gift_value=gift_value,
            currency=gift_data.get('currency', 'GBP'),
            gift_type=gift_type,
            exemption_type=exemption_type,
            becomes_exempt_date=becomes_exempt_date,
            still_in_pet_period=still_in_pet_period,
            description=gift_data.get('description'),
            is_deleted=False
        )

        self.db.add(gift)
        await self.db.commit()
        await self.db.refresh(gift)

        logger.info(
            f"Gift recorded: id={gift.id}, type={gift_type.value}, "
            f"becomes_exempt={becomes_exempt_date}"
        )

        return gift

    async def get_gifts_in_pet_period(
        self,
        user_id: UUID,
        as_of_date: Optional[date] = None
    ) -> List[Gift]:
        """
        Get all gifts still within the 7-year PET period.

        Args:
            user_id: User UUID
            as_of_date: Date for checking PET period (default: today)

        Returns:
            List of Gift records still in PET period (sorted by gift_date, oldest first)

        Business Logic:
            - Query gifts where gift_type = PET
            - Filter where becomes_exempt_date > as_of_date (or calculate if not set)
            - Sort by gift_date ascending (oldest first)
        """
        if as_of_date is None:
            as_of_date = date.today()

        logger.info(f"Getting gifts in PET period for user {user_id} as of {as_of_date}")

        # Query PET gifts
        result = await self.db.execute(
            select(Gift).where(
                and_(
                    Gift.user_id == user_id,
                    Gift.gift_type == GiftType.PET,
                    Gift.is_deleted == False,
                    Gift.becomes_exempt_date > as_of_date
                )
            ).order_by(Gift.gift_date.asc())
        )

        gifts = result.scalars().all()

        logger.info(f"Found {len(gifts)} gifts in PET period")
        return list(gifts)

    async def calculate_potential_iht_on_pets(
        self,
        user_id: UUID,
        death_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Calculate potential IHT on all PETs if death occurs on specified date.

        Args:
            user_id: User UUID
            death_date: Assumed death date for calculation (default: today)

        Returns:
            List of dicts with potential IHT for each gift:
                - gift_id: UUID
                - recipient: str
                - gift_date: date
                - gift_value: Decimal
                - years_since_gift: Decimal
                - taper_relief_percent: Decimal
                - effective_iht_rate: Decimal
                - potential_iht: Decimal

        Business Logic:
            - Get all PETs within 7 years of death_date
            - For each gift:
              - Calculate years since gift
              - Apply taper relief (Gift model method)
              - Effective IHT rate = 40% * (1 - taper_relief)
              - Potential IHT = gift_value * effective_rate
        """
        if death_date is None:
            death_date = date.today()

        logger.info(f"Calculating potential IHT on PETs for user {user_id} with death date {death_date}")

        # Get all PETs within 7 years of death_date
        seven_years_before = death_date - relativedelta(years=7)

        result = await self.db.execute(
            select(Gift).where(
                and_(
                    Gift.user_id == user_id,
                    Gift.gift_type == GiftType.PET,
                    Gift.is_deleted == False,
                    Gift.gift_date >= seven_years_before,
                    Gift.gift_date <= death_date
                )
            ).order_by(Gift.gift_date.asc())
        )

        gifts = result.scalars().all()

        pet_calculations = []

        for gift in gifts:
            # Calculate years since gift
            delta = relativedelta(death_date, gift.gift_date)
            years = delta.years
            months = delta.months
            days = delta.days

            years_decimal = Decimal(str(years))
            months_decimal = Decimal(str(months)) / Decimal('12')
            days_decimal = Decimal(str(days)) / Decimal('365.25')
            years_since_gift = years_decimal + months_decimal + days_decimal

            # Calculate taper relief using Gift model method
            # We need to temporarily set the gift_date context for calculation
            # For this calculation, we use the death_date as "today"
            # Taper relief bands:
            # 0-3 years: 0%, 3-4: 20%, 4-5: 40%, 5-6: 60%, 6-7: 80%, 7+: 100%
            if years_since_gift < Decimal('3.00'):
                taper_relief_percent = Decimal('0.00')
            elif years_since_gift < Decimal('4.00'):
                taper_relief_percent = Decimal('0.20')
            elif years_since_gift < Decimal('5.00'):
                taper_relief_percent = Decimal('0.40')
            elif years_since_gift < Decimal('6.00'):
                taper_relief_percent = Decimal('0.60')
            elif years_since_gift < Decimal('7.00'):
                taper_relief_percent = Decimal('0.80')
            else:
                taper_relief_percent = Decimal('1.00')

            # Effective IHT rate = 40% * (1 - taper_relief)
            base_rate = Decimal('0.40')
            effective_iht_rate = base_rate * (Decimal('1.00') - taper_relief_percent)

            # Potential IHT = gift_value * effective_rate
            potential_iht = gift.gift_value * effective_iht_rate

            pet_calculations.append({
                "gift_id": gift.id,
                "recipient": gift.recipient,
                "gift_date": gift.gift_date,
                "gift_value": gift.gift_value,
                "years_since_gift": years_since_gift,
                "taper_relief_percent": taper_relief_percent,
                "effective_iht_rate": effective_iht_rate,
                "potential_iht": potential_iht
            })

        logger.info(f"Calculated potential IHT for {len(pet_calculations)} PETs")
        return pet_calculations

    async def apply_exemptions(
        self,
        user_id: UUID,
        gift_value: Decimal,
        tax_year: int,
        exemption_type: str = "ANNUAL_EXEMPTION"
    ) -> Dict[str, Any]:
        """
        Apply IHT exemptions to a gift amount.

        Args:
            user_id: User UUID
            gift_value: Gift amount to apply exemption to
            tax_year: Calendar year (e.g., 2024)
            exemption_type: Type of exemption to apply (default: "ANNUAL_EXEMPTION")

        Returns:
            Dict with:
                - exemption_applied: Decimal
                - remaining_gift_value: Decimal
                - exemption_remaining: Decimal

        Business Logic:
            - Get or create IHTExemption for tax_year
            - If ANNUAL_EXEMPTION:
              - Try to apply from current year allowance first
              - Then apply from carried forward amount
              - Update exemption record
            - If SMALL_GIFTS:
              - Check £250 limit (simplified: total tracking)
            - Return exemption applied and remaining gift value
        """
        logger.info(
            f"Applying {exemption_type} exemption for user {user_id}: "
            f"gift_value=£{gift_value:,.2f}, year={tax_year}"
        )

        # Convert tax_year to UK format (YYYY/YY)
        uk_tax_year = f"{tax_year}/{str(tax_year + 1)[-2:]}"

        # Get or create IHTExemption for tax year
        result = await self.db.execute(
            select(IHTExemption).where(
                and_(
                    IHTExemption.user_id == user_id,
                    IHTExemption.tax_year == uk_tax_year
                )
            )
        )

        exemption_record = result.scalar_one_or_none()

        if exemption_record is None:
            # Create new exemption record
            exemption_record = IHTExemption(
                id=uuid.uuid4(),
                user_id=user_id,
                tax_year=uk_tax_year,
                annual_exemption_limit=self.ANNUAL_EXEMPTION_LIMIT,
                annual_exemption_used=Decimal('0.00'),
                annual_exemption_remaining=self.ANNUAL_EXEMPTION_LIMIT,
                carried_forward_from_previous_year=Decimal('0.00'),
                small_gifts_exemption_used=Decimal('0.00'),
                wedding_gifts_exemption_used=Decimal('0.00')
            )
            self.db.add(exemption_record)

        exemption_applied = Decimal('0.00')
        remaining_gift_value = gift_value

        if exemption_type == "ANNUAL_EXEMPTION":
            # Apply current year exemption first
            current_remaining = exemption_record.annual_exemption_remaining
            if current_remaining > Decimal('0.00'):
                current_applied = min(remaining_gift_value, current_remaining)
                exemption_record.annual_exemption_used += current_applied
                exemption_record.annual_exemption_remaining -= current_applied
                exemption_applied += current_applied
                remaining_gift_value -= current_applied

            # Apply carried forward if needed
            if remaining_gift_value > Decimal('0.00'):
                carried_forward = exemption_record.carried_forward_from_previous_year
                if carried_forward > Decimal('0.00'):
                    carried_applied = min(remaining_gift_value, carried_forward)
                    exemption_record.carried_forward_from_previous_year -= carried_applied
                    exemption_applied += carried_applied
                    remaining_gift_value -= carried_applied

        elif exemption_type == "SMALL_GIFTS":
            # Small gifts: £250 per person per year
            # Simplified: apply up to £250
            small_gift_applied = min(remaining_gift_value, self.SMALL_GIFT_LIMIT)
            exemption_record.small_gifts_exemption_used += small_gift_applied
            exemption_applied += small_gift_applied
            remaining_gift_value -= small_gift_applied

        elif exemption_type == "WEDDING":
            # Wedding gifts: varies by relationship (simplified here)
            # Using default £1,000 limit
            wedding_gift_applied = min(remaining_gift_value, self.WEDDING_GIFT_OTHER)
            exemption_record.wedding_gifts_exemption_used += wedding_gift_applied
            exemption_applied += wedding_gift_applied
            remaining_gift_value -= wedding_gift_applied

        await self.db.commit()
        await self.db.refresh(exemption_record)

        exemption_remaining = exemption_record.total_exemption_available()

        logger.info(
            f"Exemption applied: applied=£{exemption_applied:,.2f}, "
            f"remaining_gift=£{remaining_gift_value:,.2f}, "
            f"exemption_remaining=£{exemption_remaining:,.2f}"
        )

        return {
            "exemption_applied": exemption_applied,
            "remaining_gift_value": remaining_gift_value,
            "exemption_remaining": exemption_remaining
        }

    async def get_exemption_status(
        self,
        user_id: UUID,
        tax_year: str
    ) -> Dict[str, Any]:
        """
        Get IHT exemption status for a tax year.

        Args:
            user_id: User UUID
            tax_year: UK tax year in format YYYY/YY (e.g., '2024/25')

        Returns:
            Dict with:
                - annual_exemption_limit: Decimal
                - annual_exemption_used: Decimal
                - annual_exemption_remaining: Decimal
                - carried_forward: Decimal
                - total_available: Decimal

        Business Logic:
            - Get IHTExemption for tax_year
            - Return status with all exemption amounts
            - If no record exists, return defaults (£3,000 available)
        """
        logger.info(f"Getting exemption status for user {user_id}, tax year {tax_year}")

        result = await self.db.execute(
            select(IHTExemption).where(
                and_(
                    IHTExemption.user_id == user_id,
                    IHTExemption.tax_year == tax_year
                )
            )
        )

        exemption_record = result.scalar_one_or_none()

        if exemption_record is None:
            # No record exists - return defaults
            status = {
                "annual_exemption_limit": self.ANNUAL_EXEMPTION_LIMIT,
                "annual_exemption_used": Decimal('0.00'),
                "annual_exemption_remaining": self.ANNUAL_EXEMPTION_LIMIT,
                "carried_forward": Decimal('0.00'),
                "total_available": self.ANNUAL_EXEMPTION_LIMIT
            }
        else:
            status = {
                "annual_exemption_limit": exemption_record.annual_exemption_limit,
                "annual_exemption_used": exemption_record.annual_exemption_used,
                "annual_exemption_remaining": exemption_record.annual_exemption_remaining,
                "carried_forward": exemption_record.carried_forward_from_previous_year,
                "total_available": exemption_record.total_exemption_available()
            }

        logger.info(f"Exemption status: {status}")
        return status


# Factory function
def get_gift_analysis_service(db: AsyncSession) -> GiftAnalysisService:
    """
    Get gift analysis service instance.

    Args:
        db: Database session

    Returns:
        GiftAnalysisService instance
    """
    return GiftAnalysisService(db)
