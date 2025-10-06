"""
Emergency Fund Assessment Service

Assesses emergency fund adequacy based on monthly expenses and designated accounts.

Business Rules:
- Recommended emergency fund: 6 months of essential monthly expenses
- Status determination:
  - ADEQUATE: >= 6 months covered
  - INSUFFICIENT: > 0 but < 6 months covered
  - NONE: No emergency fund designated
- Only accounts with purpose='EMERGENCY_FUND' and is_active=True are counted
- Multi-currency support with conversion to base currency

Performance:
- Target: <200ms for assessment
- Simple aggregation queries
- No caching (real-time assessment)
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from models.savings_account import SavingsAccount, AccountPurpose
from models.income import UserIncome
from services.currency_conversion import CurrencyConversionService

logger = logging.getLogger(__name__)


class EmergencyFundAssessmentService:
    """Service for assessing emergency fund adequacy."""

    # Standard recommendation: 6 months of expenses
    RECOMMENDED_MONTHS = 6

    def __init__(self, db: AsyncSession):
        """
        Initialize emergency fund assessment service.

        Args:
            db: Database session for queries
        """
        self.db = db
        self.currency_service = CurrencyConversionService(db)

    def calculate_recommended_emergency_fund(
        self,
        monthly_expenses: Decimal
    ) -> Decimal:
        """
        Calculate recommended emergency fund amount.

        Args:
            monthly_expenses: Monthly expenses amount

        Returns:
            Recommended emergency fund (6 × monthly_expenses)
        """
        return monthly_expenses * self.RECOMMENDED_MONTHS

    async def get_current_emergency_fund(
        self,
        user_id: UUID,
        base_currency: str = "GBP"
    ) -> Decimal:
        """
        Sum all accounts marked as emergency fund.

        Args:
            user_id: User UUID
            base_currency: Currency for result

        Returns:
            Total emergency fund in base currency
        """
        # Query all active emergency fund accounts
        stmt = select(SavingsAccount).where(
            and_(
                SavingsAccount.user_id == user_id,
                SavingsAccount.purpose == AccountPurpose.EMERGENCY_FUND,
                SavingsAccount.is_active == True,
                SavingsAccount.deleted_at.is_(None)
            )
        )

        result = await self.db.execute(stmt)
        accounts = result.scalars().all()

        if not accounts:
            return Decimal('0.00')

        # Sum balances with currency conversion
        total = Decimal('0.00')

        for account in accounts:
            # Convert to base currency if needed
            if account.currency.value == base_currency:
                total += account.current_balance
            else:
                converted, _, _ = await self.currency_service.convert_amount(
                    amount=account.current_balance,
                    from_currency=account.currency.value,
                    to_currency=base_currency
                )
                total += converted

        return total

    async def get_emergency_fund_accounts(
        self,
        user_id: UUID
    ) -> List[SavingsAccount]:
        """
        Get all accounts marked as emergency fund.

        Args:
            user_id: User UUID

        Returns:
            List of emergency fund accounts
        """
        stmt = select(SavingsAccount).where(
            and_(
                SavingsAccount.user_id == user_id,
                SavingsAccount.purpose == AccountPurpose.EMERGENCY_FUND,
                SavingsAccount.is_active == True,
                SavingsAccount.deleted_at.is_(None)
            )
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def estimate_monthly_expenses_from_income(
        self,
        user_id: UUID
    ) -> Decimal:
        """
        Estimate monthly expenses from income if not provided.

        Uses 70% of net monthly income as rough estimate.

        Args:
            user_id: User UUID

        Returns:
            Estimated monthly expenses
        """
        # Get user's total income
        stmt = select(func.sum(UserIncome.amount)).where(
            and_(
                UserIncome.user_id == user_id,
                UserIncome.deleted_at.is_(None)
            )
        )

        result = await self.db.execute(stmt)
        total_income = result.scalar()

        if not total_income or total_income == 0:
            # No income data, return minimum buffer
            return Decimal('2000.00')

        # Estimate expenses as 70% of income
        # This is a rough estimate for assessment purposes
        estimated_expenses = Decimal(str(total_income)) * Decimal('0.70')

        return estimated_expenses

    def _determine_status(
        self,
        current: Decimal,
        recommended: Decimal
    ) -> str:
        """
        Determine emergency fund status.

        Args:
            current: Current emergency fund
            recommended: Recommended emergency fund

        Returns:
            Status: ADEQUATE, INSUFFICIENT, or NONE
        """
        if current == 0:
            return "NONE"
        elif current >= recommended:
            return "ADEQUATE"
        else:
            return "INSUFFICIENT"

    def _generate_status_message(
        self,
        status: str,
        months_covered: Decimal,
        shortfall: Decimal,
        base_currency: str
    ) -> str:
        """
        Generate human-readable status message.

        Args:
            status: Emergency fund status
            months_covered: Number of months covered
            shortfall: Amount short of recommended
            base_currency: Currency symbol

        Returns:
            Status message string
        """
        symbol = "£" if base_currency == "GBP" else "R" if base_currency == "ZAR" else base_currency

        if status == "ADEQUATE":
            return (
                f"Your emergency fund is adequate. You have {months_covered:.1f} "
                f"months of expenses covered."
            )
        elif status == "INSUFFICIENT":
            return (
                f"Your emergency fund is insufficient. You have {months_covered:.1f} "
                f"months covered but need {symbol}{shortfall:,.2f} more to reach 6 months."
            )
        else:  # NONE
            return (
                "You don't have an emergency fund yet. Consider building one "
                "with 6 months of expenses."
            )

    def generate_recommendations(
        self,
        status: str,
        current: Decimal,
        recommended: Decimal,
        shortfall: Decimal,
        base_currency: str
    ) -> List[str]:
        """
        Generate personalized recommendations based on status.

        Args:
            status: Emergency fund status
            current: Current emergency fund
            recommended: Recommended emergency fund
            shortfall: Amount short of recommended
            base_currency: Currency symbol

        Returns:
            List of recommendation strings
        """
        symbol = "£" if base_currency == "GBP" else "R" if base_currency == "ZAR" else base_currency
        recommendations = []

        if status == "ADEQUATE":
            recommendations.append(
                "Great job! Your emergency fund is well-stocked."
            )
            recommendations.append(
                "Review your fund annually to ensure it still covers 6 months of expenses."
            )

        elif status == "INSUFFICIENT":
            months_covered = current / (recommended / 6) if recommended > 0 else 0
            recommendations.append(
                f"You have {months_covered:.1f} months covered. Aim to reach 6 months "
                f"({symbol}{shortfall:,.2f} more needed)."
            )
            recommendations.append(
                "Consider setting up automatic transfers to build your fund faster."
            )
            recommendations.append(
                "Keep your emergency fund in instant-access accounts."
            )

        else:  # NONE
            recommendations.append(
                f"Start by saving {symbol}500-{symbol}1,000 as an initial emergency buffer."
            )
            recommendations.append(
                f"Gradually build up to 6 months of expenses ({symbol}{recommended:,.2f})."
            )
            recommendations.append(
                "Mark a savings account as 'Emergency Fund' to track your progress."
            )
            recommendations.append(
                "Keep emergency funds separate from savings goals."
            )

        return recommendations

    async def assess_emergency_fund(
        self,
        user_id: UUID,
        monthly_expenses: Decimal,
        base_currency: str = "GBP"
    ) -> Dict:
        """
        Main assessment method.

        Args:
            user_id: User UUID
            monthly_expenses: Monthly expenses amount
            base_currency: Currency for all amounts

        Returns:
            Dict with structure:
            {
                "current_emergency_fund": Decimal,
                "recommended_emergency_fund": Decimal,
                "months_covered": Decimal,
                "ratio": Decimal,
                "status": str,
                "status_message": str,
                "recommendations": List[str]
            }

        Raises:
            ValueError: If monthly_expenses is negative
        """
        if monthly_expenses < 0:
            raise ValueError("Monthly expenses cannot be negative")

        logger.info(
            f"Assessing emergency fund for user {user_id} "
            f"(monthly expenses: {base_currency} {monthly_expenses})"
        )

        # Calculate recommended amount
        recommended = self.calculate_recommended_emergency_fund(monthly_expenses)

        # Get current emergency fund
        current = await self.get_current_emergency_fund(user_id, base_currency)

        # Calculate metrics
        if monthly_expenses > 0:
            months_covered = current / monthly_expenses
        else:
            months_covered = Decimal('0.00')

        if recommended > 0:
            ratio = current / recommended
        else:
            ratio = Decimal('0.00')

        # Determine status
        status = self._determine_status(current, recommended)

        # Calculate shortfall
        shortfall = max(recommended - current, Decimal('0.00'))

        # Generate status message
        status_message = self._generate_status_message(
            status,
            months_covered,
            shortfall,
            base_currency
        )

        # Generate recommendations
        recommendations = self.generate_recommendations(
            status,
            current,
            recommended,
            shortfall,
            base_currency
        )

        assessment = {
            "current_emergency_fund": float(current),
            "recommended_emergency_fund": float(recommended),
            "months_covered": float(months_covered),
            "ratio": float(ratio),
            "status": status,
            "status_message": status_message,
            "recommendations": recommendations,
            "base_currency": base_currency
        }

        logger.info(
            f"Emergency fund assessment complete for user {user_id}: "
            f"Status={status}, Ratio={ratio:.2f}"
        )

        return assessment
