"""
Career Change Scenario Service

Models career change impact on:
- Pension contributions
- Tax liability
- Net worth over time
- Break-even analysis
"""

import logging
from decimal import Decimal
from datetime import date
from typing import Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class CareerChangeScenarioService:
    """Service for career change scenario modeling."""

    def __init__(self, db: AsyncSession):
        """Initialize career change scenario service."""
        self.db = db

    async def model_career_change(
        self,
        user_id: UUID,
        current_salary: Decimal,
        new_salary: Decimal,
        change_date: date,
        current_age: int,
        retirement_age: int = 67,
        pension_contribution_rate: Decimal = Decimal('10.00')
    ) -> Dict[str, Any]:
        """
        Model career change financial impact.

        Args:
            user_id: User UUID
            current_salary: Current annual salary
            new_salary: New annual salary after change
            change_date: Date of career change
            current_age: Current age
            retirement_age: Target retirement age
            pension_contribution_rate: Pension contribution as % of salary

        Returns:
            Dict with impact analysis
        """
        logger.info(f"Modeling career change for user {user_id}: £{current_salary} -> £{new_salary}")

        salary_change = new_salary - current_salary
        salary_change_pct = (salary_change / current_salary * Decimal('100')) if current_salary > 0 else Decimal('0')

        # Calculate pension impact
        years_to_retirement = retirement_age - current_age
        current_annual_contribution = current_salary * (pension_contribution_rate / Decimal('100'))
        new_annual_contribution = new_salary * (pension_contribution_rate / Decimal('100'))
        contribution_change = new_annual_contribution - current_annual_contribution

        # Project pension pot impact over remaining career
        # Simplified: just sum of additional contributions (no growth for simplicity here)
        total_pension_impact = contribution_change * Decimal(str(years_to_retirement))

        # Tax impact (simplified UK tax bands)
        current_tax = self._calculate_uk_tax(current_salary)
        new_tax = self._calculate_uk_tax(new_salary)
        tax_change = new_tax - current_tax

        # Net worth impact
        net_income_change = salary_change - tax_change - contribution_change
        total_net_worth_impact = net_income_change * Decimal(str(years_to_retirement))

        # Break-even analysis (if salary decreased)
        break_even_years = None
        if salary_change < 0:
            # How many years to recover the lost income?
            # This would involve more complex modeling in production
            break_even_years = None

        return {
            'current_salary': float(current_salary),
            'new_salary': float(new_salary),
            'salary_change': float(salary_change),
            'salary_change_percentage': float(salary_change_pct),
            'impact_on_pension': float(total_pension_impact),
            'annual_pension_contribution_change': float(contribution_change),
            'impact_on_tax': float(tax_change),
            'annual_tax_change': float(tax_change),
            'net_income_change': float(net_income_change),
            'impact_on_net_worth': float(total_net_worth_impact),
            'break_even_years': break_even_years,
            'recommendation': self._generate_recommendation(salary_change, total_net_worth_impact)
        }

    def _calculate_uk_tax(self, salary: Decimal) -> Decimal:
        """
        Calculate UK income tax (simplified).

        Bands (2024/25):
        - £0 - £12,570: 0%
        - £12,571 - £50,270: 20%
        - £50,271 - £125,140: 40%
        - £125,141+: 45%
        """
        tax = Decimal('0')

        personal_allowance = Decimal('12570')
        basic_rate_limit = Decimal('50270')
        higher_rate_limit = Decimal('125140')

        if salary <= personal_allowance:
            return Decimal('0')

        # Basic rate (20%)
        if salary > personal_allowance:
            basic_rate_income = min(salary - personal_allowance, basic_rate_limit - personal_allowance)
            tax += basic_rate_income * Decimal('0.20')

        # Higher rate (40%)
        if salary > basic_rate_limit:
            higher_rate_income = min(salary - basic_rate_limit, higher_rate_limit - basic_rate_limit)
            tax += higher_rate_income * Decimal('0.40')

        # Additional rate (45%)
        if salary > higher_rate_limit:
            additional_rate_income = salary - higher_rate_limit
            tax += additional_rate_income * Decimal('0.45')

        return tax

    def _generate_recommendation(self, salary_change: Decimal, net_worth_impact: Decimal) -> str:
        """Generate recommendation based on career change impact."""
        if salary_change > 0:
            return f"This career change increases your salary and improves your financial position by £{abs(net_worth_impact):,.2f} over your career."
        elif salary_change < 0:
            return f"This career change decreases your salary. Consider whether the non-financial benefits justify the £{abs(net_worth_impact):,.2f} impact."
        else:
            return "No change in salary."
