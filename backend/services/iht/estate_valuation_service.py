"""
Estate Valuation Service

Provides comprehensive estate valuation and UK IHT calculation including:
- Gross estate calculation (all assets)
- Net estate calculation (assets minus deductible liabilities)
- Residence Nil Rate Band (RNRB) calculation with tapering
- UK IHT calculation with NRB, RNRB, and transferable allowances
- IHT calculation storage for audit trail

Business Rules:
- Standard NRB: £325,000 (2024/25)
- RNRB: Max £175,000, tapered if estate > £2M
- RNRB taper: Reduce £1 for every £2 over £2M threshold
- IHT rate: 40% standard, 36% if >=10% to charity
- Transferable NRB/RNRB from deceased spouse supported
- All calculations use Decimal for precision
- Temporal data filtering (effective_from/effective_to)

Performance:
- Target: <500ms for estate calculation
- Target: <200ms for gross/net estate queries
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
    EstateAsset, EstateLiability, IHTCalculation
)

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when estate data validation fails."""
    pass


class NotFoundError(Exception):
    """Raised when estate entity not found."""
    pass


class EstateValuationService:
    """Service for estate valuation and UK IHT calculations."""

    # Constants (2024/25 tax year)
    STANDARD_NRB = Decimal('325000.00')
    MAX_RNRB = Decimal('175000.00')
    RNRB_TAPER_THRESHOLD = Decimal('2000000.00')
    IHT_STANDARD_RATE = Decimal('0.40')
    IHT_CHARITY_RATE = Decimal('0.36')
    CHARITY_THRESHOLD = Decimal('10.00')

    def __init__(self, db: AsyncSession):
        """
        Initialize estate valuation service.

        Args:
            db: Database session for operations
        """
        self.db = db

    async def calculate_gross_estate(
        self,
        user_id: UUID,
        as_of_date: Optional[date] = None
    ) -> Decimal:
        """
        Calculate gross estate value (all UK-includable assets).

        Queries all EstateAssets for user where included_in_uk_estate=True,
        filters by temporal data (effective_from/effective_to), and sums values.

        Args:
            user_id: User UUID
            as_of_date: Date for temporal query (default: today)

        Returns:
            Gross estate value in GBP

        Business Logic:
            - Only include assets where included_in_uk_estate=True
            - Filter by effective_from <= as_of_date < effective_to
            - If effective_to IS NULL, asset is current
            - Sum all asset values (assumes GBP, currency conversion TBD)
        """
        if as_of_date is None:
            as_of_date = date.today()

        logger.info(f"Calculating gross estate for user {user_id} as of {as_of_date}")

        # Query assets with temporal filtering
        result = await self.db.execute(
            select(func.sum(EstateAsset.estimated_value)).where(
                and_(
                    EstateAsset.user_id == user_id,
                    EstateAsset.included_in_uk_estate == True,
                    EstateAsset.is_deleted == False,
                    EstateAsset.effective_from <= as_of_date,
                    (
                        (EstateAsset.effective_to.is_(None)) |
                        (EstateAsset.effective_to > as_of_date)
                    )
                )
            )
        )

        gross_estate = result.scalar()

        if gross_estate is None:
            gross_estate = Decimal('0.00')
        else:
            gross_estate = Decimal(str(gross_estate))

        logger.info(f"Gross estate calculated: £{gross_estate:,.2f}")
        return gross_estate

    async def calculate_net_estate(
        self,
        user_id: UUID,
        as_of_date: Optional[date] = None
    ) -> Decimal:
        """
        Calculate net estate value (gross estate minus deductible liabilities).

        Args:
            user_id: User UUID
            as_of_date: Date for temporal query (default: today)

        Returns:
            Net estate value in GBP

        Business Logic:
            - Net estate = gross_estate - deductible_liabilities
            - Only liabilities where deductible_from_estate=True
            - Temporal filtering applied to liabilities
        """
        if as_of_date is None:
            as_of_date = date.today()

        logger.info(f"Calculating net estate for user {user_id} as of {as_of_date}")

        # Calculate gross estate
        gross_estate = await self.calculate_gross_estate(user_id, as_of_date)

        # Query deductible liabilities with temporal filtering
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

        total_liabilities = result.scalar()

        if total_liabilities is None:
            total_liabilities = Decimal('0.00')
        else:
            total_liabilities = Decimal(str(total_liabilities))

        net_estate = gross_estate - total_liabilities

        logger.info(
            f"Net estate calculated: £{net_estate:,.2f} "
            f"(gross: £{gross_estate:,.2f}, liabilities: £{total_liabilities:,.2f})"
        )

        return net_estate

    async def calculate_residence_nil_rate_band(
        self,
        user_id: UUID,
        net_estate_value: Decimal,
        property_left_to_descendants: bool
    ) -> Decimal:
        """
        Calculate Residence Nil Rate Band (RNRB) with tapering.

        Args:
            user_id: User UUID
            net_estate_value: Net estate value for taper calculation
            property_left_to_descendants: True if qualifying property left to children/grandchildren

        Returns:
            Applicable RNRB amount in GBP

        Business Logic:
            - Standard RNRB: £175,000 (2024/25)
            - Only applies if property left to direct descendants
            - Taper: If net estate > £2,000,000:
              - Reduce RNRB by £1 for every £2 over threshold
            - Minimum RNRB: £0
        """
        logger.info(
            f"Calculating RNRB for user {user_id}: "
            f"estate=£{net_estate_value:,.2f}, to_descendants={property_left_to_descendants}"
        )

        # RNRB only applies if property left to descendants
        if not property_left_to_descendants:
            logger.info("RNRB not applicable: property not left to descendants")
            return Decimal('0.00')

        # Start with maximum RNRB
        rnrb = self.MAX_RNRB

        # Apply taper if estate exceeds threshold
        if net_estate_value > self.RNRB_TAPER_THRESHOLD:
            excess = net_estate_value - self.RNRB_TAPER_THRESHOLD
            taper_reduction = excess / Decimal('2')  # £1 reduction per £2 over

            rnrb = self.MAX_RNRB - taper_reduction

            # RNRB cannot be negative
            rnrb = max(rnrb, Decimal('0.00'))

            logger.info(
                f"RNRB tapered: excess=£{excess:,.2f}, "
                f"reduction=£{taper_reduction:,.2f}, final_rnrb=£{rnrb:,.2f}"
            )
        else:
            logger.info(f"RNRB not tapered: £{rnrb:,.2f}")

        return rnrb

    async def calculate_iht(
        self,
        user_id: UUID,
        transferable_nrb_percent: Decimal = Decimal('0'),
        property_to_descendants: bool = False,
        charitable_gifts_percent: Decimal = Decimal('0'),
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculate UK Inheritance Tax with full breakdown.

        Args:
            user_id: User UUID
            transferable_nrb_percent: Percentage of NRB from deceased spouse (0-100)
            property_to_descendants: True if qualifying property left to descendants
            charitable_gifts_percent: Percentage of estate left to charity (0-100)
            as_of_date: Date for calculation (default: today)

        Returns:
            Dict with complete IHT calculation breakdown:
                - gross_estate: Decimal
                - net_estate: Decimal
                - standard_nrb: Decimal
                - residence_nrb: Decimal
                - transferable_nrb: Decimal
                - total_nrb: Decimal
                - taxable_estate: Decimal
                - iht_rate: Decimal (0.40 or 0.36)
                - iht_owed: Decimal
                - breakdown: List[Dict] (calculation steps)

        Business Logic:
            - Standard NRB: £325,000
            - Transferable NRB: £325,000 * (transferable_nrb_percent / 100)
            - RNRB: Calculate with tapering
            - Total NRB: standard + rnrb + transferable
            - Taxable estate: max(0, net_estate - total_nrb)
            - IHT rate: 36% if >=10% to charity, else 40%
            - IHT owed: taxable_estate * rate
        """
        if as_of_date is None:
            as_of_date = date.today()

        logger.info(
            f"Calculating IHT for user {user_id}: "
            f"transferable={transferable_nrb_percent}%, "
            f"to_descendants={property_to_descendants}, "
            f"charity={charitable_gifts_percent}%"
        )

        # Calculate estate values
        gross_estate = await self.calculate_gross_estate(user_id, as_of_date)
        net_estate = await self.calculate_net_estate(user_id, as_of_date)

        # Standard NRB
        standard_nrb = self.STANDARD_NRB

        # Calculate RNRB
        residence_nrb = await self.calculate_residence_nil_rate_band(
            user_id,
            net_estate,
            property_to_descendants
        )

        # Transferable NRB from deceased spouse
        transferable_nrb = standard_nrb * (transferable_nrb_percent / Decimal('100'))

        # Total NRB available
        total_nrb = standard_nrb + residence_nrb + transferable_nrb

        # Taxable estate
        taxable_estate = max(Decimal('0.00'), net_estate - total_nrb)

        # Determine IHT rate
        if charitable_gifts_percent >= self.CHARITY_THRESHOLD:
            iht_rate = self.IHT_CHARITY_RATE
        else:
            iht_rate = self.IHT_STANDARD_RATE

        # Calculate IHT owed
        iht_owed = taxable_estate * iht_rate

        # Build breakdown
        breakdown = [
            {"step": "Gross Estate", "amount": float(gross_estate)},
            {"step": "Less: Liabilities", "amount": float(gross_estate - net_estate)},
            {"step": "Net Estate", "amount": float(net_estate)},
            {"step": "Less: Standard NRB", "amount": float(standard_nrb)},
            {"step": "Less: Residence NRB", "amount": float(residence_nrb)},
            {"step": "Less: Transferable NRB", "amount": float(transferable_nrb)},
            {"step": "Taxable Estate", "amount": float(taxable_estate)},
            {"step": f"IHT at {float(iht_rate * 100):.0f}%", "amount": float(iht_owed)},
        ]

        result = {
            "gross_estate": gross_estate,
            "net_estate": net_estate,
            "standard_nrb": standard_nrb,
            "residence_nrb": residence_nrb,
            "transferable_nrb": transferable_nrb,
            "total_nrb": total_nrb,
            "taxable_estate": taxable_estate,
            "iht_rate": iht_rate,
            "iht_owed": iht_owed,
            "breakdown": breakdown
        }

        logger.info(
            f"IHT calculated: net_estate=£{net_estate:,.2f}, "
            f"total_nrb=£{total_nrb:,.2f}, "
            f"taxable=£{taxable_estate:,.2f}, "
            f"iht_owed=£{iht_owed:,.2f}"
        )

        return result

    async def save_iht_calculation(
        self,
        user_id: UUID,
        calculation_data: Dict[str, Any],
        tax_year: str
    ) -> IHTCalculation:
        """
        Save IHT calculation for audit trail.

        Args:
            user_id: User UUID
            calculation_data: Dict from calculate_iht() containing all components
            tax_year: UK tax year in format YYYY/YY (e.g., '2024/25')

        Returns:
            Saved IHTCalculation record

        Raises:
            ValidationError: If tax_year format invalid
        """
        logger.info(f"Saving IHT calculation for user {user_id}, tax year {tax_year}")

        # Validate tax year format
        if len(tax_year) != 7 or tax_year[4] != '/':
            raise ValidationError(
                f"Invalid tax year format: {tax_year}. Expected format: YYYY/YY (e.g., 2024/25)"
            )

        # Create calculation record
        calculation = IHTCalculation(
            id=uuid.uuid4(),
            user_id=user_id,
            calculation_date=date.today(),
            tax_year=tax_year,
            gross_estate_value=calculation_data['gross_estate'],
            net_estate_value=calculation_data['net_estate'],
            nil_rate_band=calculation_data['standard_nrb'],
            residence_nil_rate_band=calculation_data['residence_nrb'],
            transferable_nil_rate_band=calculation_data['transferable_nrb'],
            total_nil_rate_band_available=calculation_data['total_nrb'],
            taxable_estate=calculation_data['taxable_estate'],
            iht_owed=calculation_data['iht_owed'],
            currency='GBP'
        )

        self.db.add(calculation)
        await self.db.commit()
        await self.db.refresh(calculation)

        logger.info(f"IHT calculation saved: id={calculation.id}")
        return calculation


# Factory function
def get_estate_valuation_service(db: AsyncSession) -> EstateValuationService:
    """
    Get estate valuation service instance.

    Args:
        db: Database session

    Returns:
        EstateValuationService instance
    """
    return EstateValuationService(db)
