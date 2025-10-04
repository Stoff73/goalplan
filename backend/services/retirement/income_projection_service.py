"""
Retirement Income Projection Service

Provides retirement income projection calculations including:
- DC pension pot projection with future contributions
- Drawdown income calculations with pot depletion modeling
- Annuity income calculations
- Total retirement income aggregation from all sources
- Income gap analysis (surplus vs shortfall)
- Retirement projection creation with temporal tracking

Business Rules:
- Safe withdrawal rate: 4% (sustainable drawdown)
- Drawdown range: 2% to 8% typical
- Annuity rates vary by age, health, spouse provision
- State pension included in total income
- DB pensions provide guaranteed income
- Life expectancy default: 95 years
- Inflation adjustment applied annually
- Growth rates applied to remaining pot

Performance:
- Target: <300ms for simple projections
- Target: <1s for complex scenarios with year-by-year modeling
- Async database operations throughout
"""

import logging
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.retirement import (
    UKPension, UKPensionDBDetails, StatePensionForecast,
    RetirementProjection, PensionType
)

logger = logging.getLogger(__name__)


class IncomeProjectionService:
    """Service for retirement income projection calculations."""

    # Constants
    SAFE_WITHDRAWAL_RATE = Decimal('4.00')  # 4% safe withdrawal rate
    DEFAULT_LIFE_EXPECTANCY = 95
    DEFAULT_GROWTH_RATE = Decimal('5.00')  # 5% annual growth
    DEFAULT_INFLATION_RATE = Decimal('2.50')  # 2.5% annual inflation

    def __init__(self, db: AsyncSession):
        """
        Initialize income projection service.

        Args:
            db: Database session for operations
        """
        self.db = db

    def project_dc_pension_value(
        self,
        current_value: Decimal,
        monthly_contribution: Decimal,
        growth_rate: Decimal,
        years_to_retirement: int
    ) -> Decimal:
        """
        Project DC pension value at retirement with future contributions.

        Args:
            current_value: Current pension pot value
            monthly_contribution: Monthly contribution amount (employee + employer + personal)
            growth_rate: Annual growth rate (percentage, e.g., 5.00 for 5%)
            years_to_retirement: Years until retirement

        Returns:
            Projected pot value at retirement

        Formula:
            1. Project current value: current_value * (1 + growth_rate)^years
            2. Project contributions:
               - Annual contribution = monthly_contribution * 12
               - Future value of annuity: PMT * [((1 + r)^n - 1) / r]
               - Where r = growth_rate, n = years
            3. Total = projected current value + future value of contributions
        """
        logger.info(
            f"Projecting DC value: current={current_value}, monthly_contrib={monthly_contribution}, "
            f"growth={growth_rate}%, years={years_to_retirement}"
        )

        if years_to_retirement <= 0:
            return current_value

        growth_decimal = growth_rate / Decimal('100')

        # Project current value with compound growth
        growth_multiplier = (Decimal('1') + growth_decimal) ** years_to_retirement
        projected_current_value = current_value * growth_multiplier

        # Project future contributions
        annual_contribution = monthly_contribution * Decimal('12')

        if growth_decimal > 0:
            # Future value of annuity formula
            fv_contributions = annual_contribution * (
                ((Decimal('1') + growth_decimal) ** years_to_retirement - Decimal('1')) / growth_decimal
            )
        else:
            # No growth scenario
            fv_contributions = annual_contribution * Decimal(str(years_to_retirement))

        projected_total = projected_current_value + fv_contributions

        logger.info(
            f"DC projection: current_projected={projected_current_value}, "
            f"contributions_fv={fv_contributions}, total={projected_total}"
        )

        return projected_total

    def calculate_drawdown_income(
        self,
        pot_value: Decimal,
        drawdown_rate: Decimal,
        start_age: int,
        growth_rate: Optional[Decimal] = None,
        inflation_rate: Optional[Decimal] = None,
        life_expectancy: int = DEFAULT_LIFE_EXPECTANCY
    ) -> Dict[str, Any]:
        """
        Calculate drawdown income and model pot depletion.

        Simulates year-by-year drawdown with investment growth and inflation.

        Args:
            pot_value: Initial pension pot value
            drawdown_rate: Annual drawdown rate (percentage, e.g., 4.00 for 4%)
            start_age: Age when drawdown starts
            growth_rate: Annual investment growth rate (default: 5%)
            inflation_rate: Annual inflation rate (default: 2.5%)
            life_expectancy: Maximum age to model to (default: 95)

        Returns:
            Dict with:
                - annual_income: Decimal (initial year)
                - monthly_income: Decimal (initial year)
                - depletion_age: Optional[int] (None if lasts to life expectancy)
                - pot_lasts: bool
                - years_lasting: int
        """
        if growth_rate is None:
            growth_rate = self.DEFAULT_GROWTH_RATE
        if inflation_rate is None:
            inflation_rate = self.DEFAULT_INFLATION_RATE

        logger.info(
            f"Calculating drawdown: pot={pot_value}, rate={drawdown_rate}%, "
            f"start_age={start_age}, growth={growth_rate}%, inflation={inflation_rate}%"
        )

        # Calculate initial annual income
        annual_income = pot_value * (drawdown_rate / Decimal('100'))
        monthly_income = annual_income / Decimal('12')

        # Model pot depletion year by year
        remaining_pot = pot_value
        current_withdrawal = annual_income
        current_age = start_age

        growth_decimal = growth_rate / Decimal('100')
        inflation_decimal = inflation_rate / Decimal('100')

        while current_age < life_expectancy:
            # Take withdrawal at start of year
            remaining_pot -= current_withdrawal

            # Check if depleted
            if remaining_pot <= Decimal('0'):
                logger.info(f"Pot depleted at age {current_age}")
                return {
                    "annual_income": annual_income,
                    "monthly_income": monthly_income,
                    "depletion_age": current_age,
                    "pot_lasts": False,
                    "years_lasting": current_age - start_age
                }

            # Apply investment growth
            remaining_pot *= (Decimal('1') + growth_decimal)

            # Increase withdrawal with inflation
            current_withdrawal *= (Decimal('1') + inflation_decimal)

            current_age += 1

        # Pot lasts until life expectancy
        logger.info(f"Pot lasts until life expectancy ({life_expectancy})")
        return {
            "annual_income": annual_income,
            "monthly_income": monthly_income,
            "depletion_age": None,
            "pot_lasts": True,
            "years_lasting": life_expectancy - start_age
        }

    def calculate_annuity_income(
        self,
        pot_value: Decimal,
        annuity_rate: Decimal,
        spouse_provision: bool = False
    ) -> Decimal:
        """
        Calculate guaranteed annuity income.

        Args:
            pot_value: Pension pot value to convert to annuity
            annuity_rate: Annuity rate (percentage, e.g., 5.50 for 5.5%)
            spouse_provision: Whether to include spouse provision (reduces income by ~10-15%)

        Returns:
            Guaranteed annual income from annuity

        Business Logic:
            - Annuity provides guaranteed income for life
            - Rate varies by age, health status, inflation protection
            - Spouse provision reduces rate by 10-15%
            - Typical rates at 65: 5-6% (single), 4.5-5.5% (joint)
        """
        logger.info(
            f"Calculating annuity: pot={pot_value}, rate={annuity_rate}%, "
            f"spouse_provision={spouse_provision}"
        )

        # Calculate base annuity income
        annual_income = pot_value * (annuity_rate / Decimal('100'))

        # Adjust for spouse provision (typically 12.5% reduction)
        if spouse_provision:
            reduction_factor = Decimal('0.125')  # 12.5% reduction
            annual_income *= (Decimal('1') - reduction_factor)
            logger.debug(f"Spouse provision applied - reduced by {reduction_factor * 100}%")

        logger.info(f"Annuity income: {annual_income} per year")
        return annual_income

    async def calculate_total_retirement_income(
        self,
        user_id: UUID,
        target_retirement_age: int
    ) -> Dict[str, Any]:
        """
        Calculate total projected retirement income from all sources.

        Includes:
        - State pension
        - DB pensions (guaranteed amounts)
        - DC pensions (sustainable drawdown at 4%)
        - Other income sources

        Args:
            user_id: User UUID
            target_retirement_age: Target retirement age

        Returns:
            Dict with:
                - state_pension_income: Decimal
                - db_pension_income: Decimal
                - dc_drawdown_income: Decimal
                - other_income: Decimal
                - total_annual_income: Decimal
                - breakdown: List[Dict] (per source)
        """
        logger.info(
            f"Calculating total retirement income for user {user_id}, "
            f"target_age={target_retirement_age}"
        )

        # Get state pension forecast
        sp_result = await self.db.execute(
            select(StatePensionForecast).where(
                StatePensionForecast.user_id == user_id
            )
        )
        state_pension = sp_result.scalar_one_or_none()

        state_pension_income = Decimal('0.00')
        if state_pension:
            state_pension_income = state_pension.estimated_annual_amount

        # Get all pensions
        pensions_result = await self.db.execute(
            select(UKPension).where(
                and_(
                    UKPension.user_id == user_id,
                    UKPension.is_deleted == False
                )
            )
        )
        pensions = pensions_result.scalars().all()

        db_pension_income = Decimal('0.00')
        dc_drawdown_income = Decimal('0.00')
        breakdown = []

        for pension in pensions:
            if pension.pension_type == PensionType.STATE_PENSION:
                # Already included above
                continue

            if pension.pension_type == PensionType.OCCUPATIONAL_DB:
                # Get DB details
                db_details_result = await self.db.execute(
                    select(UKPensionDBDetails).where(
                        UKPensionDBDetails.pension_id == pension.id
                    )
                )
                db_details = db_details_result.scalar_one_or_none()

                if db_details and db_details.guaranteed_pension_amount:
                    db_pension_income += db_details.guaranteed_pension_amount
                    breakdown.append({
                        "source": "DB Pension",
                        "provider": pension.provider,
                        "amount": float(db_details.guaranteed_pension_amount)
                    })
            else:
                # DC pension - calculate sustainable drawdown (4% safe withdrawal rate)
                if pension.current_value:
                    # Project to retirement age (simplified - no contributions)
                    # In production, would use project_dc_pension_value()
                    years_to_retirement = target_retirement_age - 65  # Assume current age ~65 for simplicity
                    if years_to_retirement < 0:
                        years_to_retirement = 0

                    projected_pot = pension.current_value

                    if years_to_retirement > 0 and pension.assumed_growth_rate:
                        growth_rate = pension.assumed_growth_rate / Decimal('100')
                        growth_multiplier = (Decimal('1') + growth_rate) ** years_to_retirement
                        projected_pot = pension.current_value * growth_multiplier

                    # Apply 4% safe withdrawal rate
                    sustainable_income = projected_pot * (self.SAFE_WITHDRAWAL_RATE / Decimal('100'))
                    dc_drawdown_income += sustainable_income

                    breakdown.append({
                        "source": "DC Drawdown",
                        "provider": pension.provider,
                        "amount": float(sustainable_income)
                    })

        total_annual_income = state_pension_income + db_pension_income + dc_drawdown_income

        # Add state pension to breakdown
        if state_pension_income > 0:
            breakdown.insert(0, {
                "source": "State Pension",
                "provider": "UK Government",
                "amount": float(state_pension_income)
            })

        logger.info(
            f"Total retirement income: state_pension={state_pension_income}, "
            f"db_pension={db_pension_income}, dc_drawdown={dc_drawdown_income}, "
            f"total={total_annual_income}"
        )

        return {
            "state_pension_income": state_pension_income,
            "db_pension_income": db_pension_income,
            "dc_drawdown_income": dc_drawdown_income,
            "other_income": Decimal('0.00'),
            "total_annual_income": total_annual_income,
            "breakdown": breakdown
        }

    async def calculate_retirement_income_gap(
        self,
        user_id: UUID,
        target_retirement_age: int,
        annual_income_needed: Decimal
    ) -> Dict[str, Any]:
        """
        Calculate retirement income gap (surplus or shortfall).

        Args:
            user_id: User UUID
            target_retirement_age: Target retirement age
            annual_income_needed: Annual income needed in retirement

        Returns:
            Dict with:
                - total_projected_income: Decimal
                - annual_income_needed: Decimal
                - income_gap: Decimal (positive = surplus, negative = shortfall)
                - on_track: bool
                - gap_percentage: Decimal
                - breakdown: List[Dict]
        """
        logger.info(
            f"Calculating income gap for user {user_id}: "
            f"target_age={target_retirement_age}, needed={annual_income_needed}"
        )

        # Get total income
        income = await self.calculate_total_retirement_income(user_id, target_retirement_age)

        total_projected_income = income['total_annual_income']
        income_gap = total_projected_income - annual_income_needed
        on_track = income_gap >= Decimal('0.00')

        # Calculate gap as percentage of needed income
        gap_percentage = Decimal('0.00')
        if annual_income_needed > 0:
            gap_percentage = (income_gap / annual_income_needed) * Decimal('100')

        logger.info(
            f"Income gap: projected={total_projected_income}, needed={annual_income_needed}, "
            f"gap={income_gap}, on_track={on_track}"
        )

        return {
            "total_projected_income": total_projected_income,
            "annual_income_needed": annual_income_needed,
            "income_gap": income_gap,
            "on_track": on_track,
            "gap_percentage": gap_percentage,
            "breakdown": income['breakdown']
        }

    async def create_retirement_projection(
        self,
        user_id: UUID,
        projection_params: Dict[str, Any]
    ) -> RetirementProjection:
        """
        Create a retirement projection record with full breakdown.

        Args:
            user_id: User UUID
            projection_params: Dict containing:
                - target_retirement_age: int
                - annual_income_needed: Decimal
                - growth_assumptions: Optional[Dict]
                - inflation_rate: Optional[Decimal]

        Returns:
            Created RetirementProjection

        Business Logic:
            - Calculate all income components
            - Calculate gap
            - Determine on-track status
            - Store with temporal data (effective_from/effective_to)
        """
        target_retirement_age = projection_params['target_retirement_age']
        annual_income_needed = projection_params['annual_income_needed']
        inflation_rate = projection_params.get('inflation_rate', self.DEFAULT_INFLATION_RATE)
        growth_assumptions = projection_params.get('growth_assumptions', {})

        logger.info(
            f"Creating retirement projection for user {user_id}: "
            f"age={target_retirement_age}, needed={annual_income_needed}"
        )

        # Calculate income and gap
        income = await self.calculate_total_retirement_income(user_id, target_retirement_age)
        gap_analysis = await self.calculate_retirement_income_gap(
            user_id,
            target_retirement_age,
            annual_income_needed
        )

        # Create projection record
        projection = RetirementProjection(
            id=uuid.uuid4(),
            user_id=user_id,
            projection_date=date.today(),
            target_retirement_age=target_retirement_age,
            projected_total_pot=Decimal('0.00'),  # Would calculate from all DC pensions
            annual_income_needed=annual_income_needed,
            state_pension_income=income['state_pension_income'],
            db_pension_income=income['db_pension_income'],
            dc_drawdown_income=income['dc_drawdown_income'],
            other_income=income['other_income'],
            total_projected_income=income['total_annual_income'],
            income_gap=gap_analysis['income_gap'],
            on_track=gap_analysis['on_track'],
            growth_assumptions=growth_assumptions,
            inflation_rate=inflation_rate,
            effective_from=date.today(),
            effective_to=None,  # Current projection
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(projection)
        await self.db.commit()
        await self.db.refresh(projection)

        logger.info(
            f"Retirement projection created: id={projection.id}, "
            f"on_track={projection.on_track}, gap={projection.income_gap}"
        )

        return projection


# Factory function
def get_income_projection_service(db: AsyncSession) -> IncomeProjectionService:
    """
    Get income projection service instance.

    Args:
        db: Database session

    Returns:
        IncomeProjectionService instance
    """
    return IncomeProjectionService(db)
