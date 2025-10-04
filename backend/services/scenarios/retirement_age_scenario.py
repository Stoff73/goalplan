"""
Retirement Age Scenario Service

Models different retirement ages (55-70) and their impact on:
- Pension pot at retirement
- Annual retirement income
- Pot depletion age
- Replacement ratio

Uses time-value-of-money calculations with compound interest.
"""

import logging
from decimal import Decimal
from typing import Dict, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class RetirementAgeScenarioService:
    """Service for retirement age scenario modeling."""

    def __init__(self, db: AsyncSession):
        """Initialize retirement age scenario service."""
        self.db = db

    async def model_retirement_age(
        self,
        user_id: UUID,
        retirement_age: int,
        current_age: int,
        current_pension_pot: Decimal,
        annual_contributions: Decimal,
        growth_rate: Decimal = Decimal('6.00'),
        life_expectancy: int = 90
    ) -> Dict[str, Any]:
        """
        Model a specific retirement age scenario.

        Args:
            user_id: User UUID
            retirement_age: Target retirement age (55-70)
            current_age: Current age
            current_pension_pot: Current pension pot value
            annual_contributions: Annual pension contributions
            growth_rate: Expected annual growth rate (%)
            life_expectancy: Expected life expectancy

        Returns:
            Dict with:
            - pension_pot_at_retirement
            - annual_retirement_income
            - monthly_retirement_income
            - pot_depletion_age
            - replacement_ratio
        """
        logger.info(f"Modeling retirement age {retirement_age} for user {user_id}")

        # Validate inputs
        if retirement_age < 55 or retirement_age > 70:
            raise ValueError("Retirement age must be between 55 and 70")

        years_to_retirement = retirement_age - current_age
        if years_to_retirement < 0:
            raise ValueError("Retirement age must be in the future")

        # Project pension pot to retirement using compound interest
        pension_pot = current_pension_pot
        growth_factor = Decimal('1') + (growth_rate / Decimal('100'))

        for year in range(years_to_retirement):
            # Apply growth
            pension_pot *= growth_factor
            # Add contribution
            pension_pot += annual_contributions

        # Calculate tax-free lump sum (25%)
        tax_free_lump_sum = pension_pot * Decimal('0.25')
        remaining_pot = pension_pot - tax_free_lump_sum

        # Calculate sustainable withdrawal rate (4% rule)
        annual_income = remaining_pot * Decimal('0.04')
        monthly_income = annual_income / Decimal('12')

        # Calculate pot depletion age
        # Using 4% withdrawal with assumed growth continuing
        years_in_retirement = life_expectancy - retirement_age
        pot_depletion_age = self._calculate_depletion_age(
            remaining_pot,
            annual_income,
            growth_rate,
            retirement_age,
            life_expectancy
        )

        # Calculate replacement ratio (assume current salary = contributions * 10)
        estimated_salary = annual_contributions * Decimal('10')
        replacement_ratio = (annual_income / estimated_salary * Decimal('100')) if estimated_salary > 0 else Decimal('0')

        return {
            'retirement_age': retirement_age,
            'years_to_retirement': years_to_retirement,
            'pension_pot_at_retirement': float(pension_pot),
            'tax_free_lump_sum': float(tax_free_lump_sum),
            'remaining_for_income': float(remaining_pot),
            'annual_retirement_income': float(annual_income),
            'monthly_retirement_income': float(monthly_income),
            'pot_depletion_age': pot_depletion_age,
            'replacement_ratio': float(replacement_ratio),
            'adequate': replacement_ratio >= Decimal('70.00')  # 70% is typical target
        }

    async def optimize_retirement_age(
        self,
        user_id: UUID,
        current_age: int,
        current_pension_pot: Decimal,
        annual_contributions: Decimal,
        target_income: Decimal,
        growth_rate: Decimal = Decimal('6.00')
    ) -> Dict[str, Any]:
        """
        Find optimal retirement age to achieve target income.

        Args:
            user_id: User UUID
            current_age: Current age
            current_pension_pot: Current pension pot value
            annual_contributions: Annual pension contributions
            target_income: Target annual retirement income
            growth_rate: Expected annual growth rate (%)

        Returns:
            Dict with:
            - optimal_retirement_age
            - pension_pot_needed
            - reasoning
        """
        logger.info(f"Optimizing retirement age for user {user_id} with target income {target_income}")

        # Try ages from 55 to 70
        best_age = None
        closest_income = Decimal('0')
        closest_diff = Decimal('999999999')

        for age in range(max(55, current_age + 1), 71):
            result = await self.model_retirement_age(
                user_id,
                age,
                current_age,
                current_pension_pot,
                annual_contributions,
                growth_rate
            )

            income = Decimal(str(result['annual_retirement_income']))
            diff = abs(income - target_income)

            if diff < closest_diff:
                closest_diff = diff
                closest_income = income
                best_age = age

            # If we've achieved or exceeded target, that's the optimal age
            if income >= target_income:
                best_age = age
                break

        pension_pot_needed = target_income / Decimal('0.04')  # 4% rule reversed

        reasoning = []
        if best_age:
            reasoning.append(f"Retiring at age {best_age} provides annual income of £{closest_income:,.2f}")
            if closest_income >= target_income:
                reasoning.append(f"This meets your target income of £{target_income:,.2f}")
            else:
                shortfall = target_income - closest_income
                reasoning.append(f"This is £{shortfall:,.2f} short of your target")
                reasoning.append(f"Consider increasing contributions or working longer")

        return {
            'optimal_retirement_age': best_age,
            'achievable_income': float(closest_income),
            'target_income': float(target_income),
            'pension_pot_needed': float(pension_pot_needed),
            'reasoning': reasoning
        }

    def _calculate_depletion_age(
        self,
        starting_pot: Decimal,
        annual_withdrawal: Decimal,
        growth_rate: Decimal,
        retirement_age: int,
        life_expectancy: int
    ) -> Optional[int]:
        """
        Calculate age when pension pot depletes.

        Returns:
            Age when pot depletes, or None if pot lasts until life expectancy
        """
        pot = starting_pot
        growth_factor = Decimal('1') + (growth_rate / Decimal('100'))
        current_age = retirement_age

        while current_age < life_expectancy:
            # Apply growth
            pot *= growth_factor
            # Withdraw
            pot -= annual_withdrawal

            if pot <= 0:
                return current_age

            current_age += 1

        return None  # Pot lasts until life expectancy
