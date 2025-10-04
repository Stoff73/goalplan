"""
Property Purchase Scenario Service

Models property purchase impact on:
- Monthly cash flow
- Net worth over time
- Affordability
- Total cost of ownership
"""

import logging
from decimal import Decimal
from typing import Dict, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class PropertyScenarioService:
    """Service for property purchase scenario modeling."""

    def __init__(self, db: AsyncSession):
        """Initialize property scenario service."""
        self.db = db

    async def model_property_purchase(
        self,
        user_id: UUID,
        property_value: Decimal,
        deposit: Decimal,
        mortgage_rate: Decimal,
        mortgage_term_years: int,
        annual_income: Decimal,
        stamp_duty: Optional[Decimal] = None,
        legal_fees: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Model property purchase scenario.

        Args:
            user_id: User UUID
            property_value: Property purchase price
            deposit: Deposit amount
            mortgage_rate: Annual mortgage interest rate (%)
            mortgage_term_years: Mortgage term in years
            annual_income: Annual income for affordability check
            stamp_duty: Stamp duty cost (calculated if not provided)
            legal_fees: Legal fees (default £2000)

        Returns:
            Dict with affordability analysis
        """
        logger.info(f"Modeling property purchase for user {user_id}: £{property_value}")

        # Validate inputs
        if deposit > property_value:
            raise ValueError("Deposit cannot exceed property value")

        if deposit < 0 or property_value <= 0:
            raise ValueError("Deposit and property value must be positive")

        # Calculate mortgage amount
        mortgage_amount = property_value - deposit
        ltv = (mortgage_amount / property_value * Decimal('100')) if property_value > 0 else Decimal('0')

        # Calculate monthly payment using mortgage formula
        # M = P[r(1+r)^n]/[(1+r)^n-1]
        # where P = principal, r = monthly rate, n = number of months
        monthly_rate = mortgage_rate / Decimal('100') / Decimal('12')
        num_payments = mortgage_term_years * 12

        if monthly_rate > 0:
            monthly_payment = (
                mortgage_amount *
                (monthly_rate * ((1 + monthly_rate) ** num_payments)) /
                (((1 + monthly_rate) ** num_payments) - 1)
            )
        else:
            monthly_payment = mortgage_amount / Decimal(str(num_payments))

        # Calculate total cost
        total_payments = monthly_payment * Decimal(str(num_payments))
        total_interest = total_payments - mortgage_amount

        # Calculate stamp duty if not provided
        if stamp_duty is None:
            stamp_duty = self._calculate_uk_stamp_duty(property_value)

        # Calculate legal fees if not provided
        if legal_fees is None:
            legal_fees = Decimal('2000')

        # Total upfront cost
        total_upfront = deposit + stamp_duty + legal_fees

        # Affordability check
        monthly_income = annual_income / Decimal('12')
        affordability_pct = (monthly_payment / monthly_income * Decimal('100')) if monthly_income > 0 else Decimal('0')
        affordable = affordability_pct <= Decimal('33.00')  # 33% rule

        # Impact on cash flow
        cash_flow_impact = -monthly_payment

        # Impact on net worth (property value - mortgage)
        net_worth_impact = property_value - mortgage_amount

        return {
            'property_value': float(property_value),
            'deposit': float(deposit),
            'mortgage_amount': float(mortgage_amount),
            'loan_to_value': float(ltv),
            'mortgage_rate': float(mortgage_rate),
            'mortgage_term_years': mortgage_term_years,
            'monthly_payment': float(monthly_payment),
            'total_payments': float(total_payments),
            'total_interest': float(total_interest),
            'total_cost': float(total_payments + total_upfront),
            'stamp_duty': float(stamp_duty),
            'legal_fees': float(legal_fees),
            'total_upfront_cost': float(total_upfront),
            'affordability_percentage': float(affordability_pct),
            'affordable': affordable,
            'impact_on_cash_flow': float(cash_flow_impact),
            'impact_on_net_worth': float(net_worth_impact),
            'recommendation': self._generate_recommendation(affordable, affordability_pct, ltv)
        }

    def _calculate_uk_stamp_duty(self, property_value: Decimal) -> Decimal:
        """
        Calculate UK stamp duty (simplified, first-time buyer not considered).

        Bands (2024/25):
        - £0 - £250,000: 0%
        - £250,001 - £925,000: 5%
        - £925,001 - £1,500,000: 10%
        - £1,500,001+: 12%
        """
        stamp_duty = Decimal('0')

        if property_value <= 250000:
            return Decimal('0')

        # 5% on £250k - £925k
        if property_value > 250000:
            band_amount = min(property_value - Decimal('250000'), Decimal('675000'))
            stamp_duty += band_amount * Decimal('0.05')

        # 10% on £925k - £1.5m
        if property_value > 925000:
            band_amount = min(property_value - Decimal('925000'), Decimal('575000'))
            stamp_duty += band_amount * Decimal('0.10')

        # 12% on £1.5m+
        if property_value > 1500000:
            band_amount = property_value - Decimal('1500000')
            stamp_duty += band_amount * Decimal('0.12')

        return stamp_duty

    def _generate_recommendation(
        self,
        affordable: bool,
        affordability_pct: Decimal,
        ltv: Decimal
    ) -> str:
        """Generate recommendation based on affordability."""
        if not affordable:
            return f"This property is not affordable. Monthly payment is {affordability_pct:.1f}% of income (should be ≤33%)."

        if ltv > Decimal('90'):
            return f"This property is affordable but LTV is high ({ltv:.1f}%). Consider a larger deposit if possible."

        if affordability_pct > Decimal('25'):
            return f"This property is affordable but will use {affordability_pct:.1f}% of your income. Ensure you have emergency savings."

        return f"This property appears affordable at {affordability_pct:.1f}% of income with {ltv:.1f}% LTV."
