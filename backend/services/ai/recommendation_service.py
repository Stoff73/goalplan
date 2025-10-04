"""
Recommendation Service - Rule-Based Financial Recommendations

This service generates personalized financial recommendations based on user's
complete financial data. Phase 2 implementation uses rule-based logic.
AI/ML integration planned for Phase 4.

Business Rules:
- Protection: Coverage gap analysis
- ISA: UK tax year allowance optimization (£20,000)
- TFSA: SA tax year allowance optimization (R36,000)
- Emergency Fund: 3-6 months expenses
- Tax Efficiency: GIA→ISA transfers, personal allowance taper
- Pension: Employer match, annual allowance

Priority Assignment:
- HIGH: Immediate financial risk or significant savings (>£1,000/year)
- MEDIUM: Good opportunities (£500-£1,000/year savings)
- LOW: Nice to have (<£500/year impact)

Performance:
- Target: <3 seconds for full recommendation generation
- Async/await patterns throughout
- Database query optimization
"""

import logging
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from sqlalchemy.orm import selectinload

from models.recommendation import (
    Recommendation,
    RecommendationType,
    RecommendationPriority,
    Currency
)
from models.user import User
from models.life_assurance import LifeAssurancePolicy, CoverageNeedsAnalysis
from models.savings_account import SavingsAccount, ISAContribution, TFSAContribution, AccountPurpose
from models.income import UserIncome
from models.investment import InvestmentAccount, InvestmentHolding, AccountType as InvAccountType
from models.tax_status import UserTaxStatus
from services.emergency_fund_assessment import EmergencyFundAssessmentService

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating and managing financial recommendations."""

    # Constants
    ISA_ANNUAL_ALLOWANCE = Decimal('20000.00')  # 2024/25
    TFSA_ANNUAL_ALLOWANCE = Decimal('36000.00')  # 2024/25 (ZAR)
    TFSA_LIFETIME_ALLOWANCE = Decimal('500000.00')  # ZAR
    EMERGENCY_FUND_MONTHS = 3  # Minimum months
    HIGH_SAVINGS_THRESHOLD = Decimal('1000.00')  # £1,000/year
    MEDIUM_SAVINGS_THRESHOLD = Decimal('500.00')  # £500/year

    def __init__(self, db: AsyncSession):
        """
        Initialize recommendation service.

        Args:
            db: Database session for queries
        """
        self.db = db

    async def generate_recommendations(
        self,
        user_id: UUID,
        base_currency: str = "GBP"
    ) -> List[Recommendation]:
        """
        Generate all recommendations for a user.

        Analyzes user's complete financial data and generates personalized
        recommendations across all modules.

        Args:
            user_id: User UUID
            base_currency: Base currency for calculations (default: GBP)

        Returns:
            List of Recommendation objects (not yet persisted)

        Raises:
            ValueError: If user not found
        """
        logger.info(f"Generating recommendations for user {user_id}")

        # Verify user exists
        user = await self._get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        recommendations = []

        # Generate recommendations from each category
        recommendations.extend(await self._generate_protection_recommendations(user_id, base_currency))
        recommendations.extend(await self._generate_isa_recommendations(user_id, base_currency))
        recommendations.extend(await self._generate_tfsa_recommendations(user_id, base_currency))
        recommendations.extend(await self._generate_emergency_fund_recommendations(user_id, base_currency))
        recommendations.extend(await self._generate_tax_efficiency_recommendations(user_id, base_currency))
        recommendations.extend(await self._generate_pension_recommendations(user_id, base_currency))

        logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")

        return recommendations

    async def get_user_recommendations(
        self,
        user_id: UUID,
        priority: Optional[RecommendationPriority] = None,
        recommendation_type: Optional[RecommendationType] = None
    ) -> List[Recommendation]:
        """
        Get active recommendations for a user.

        Retrieves all active (not dismissed, not deleted) recommendations
        with optional filtering.

        Args:
            user_id: User UUID
            priority: Optional priority filter (HIGH, MEDIUM, LOW)
            recommendation_type: Optional type filter

        Returns:
            List of Recommendation objects
        """
        # Build query
        filters = [
            Recommendation.user_id == user_id,
            Recommendation.deleted == False,
            Recommendation.dismissed == False
        ]

        if priority:
            filters.append(Recommendation.priority == priority)

        if recommendation_type:
            filters.append(Recommendation.recommendation_type == recommendation_type)

        # Custom priority ordering: HIGH (3), MEDIUM (2), LOW (1)
        from sqlalchemy import case

        priority_order = case(
            (Recommendation.priority == RecommendationPriority.HIGH, 3),
            (Recommendation.priority == RecommendationPriority.MEDIUM, 2),
            (Recommendation.priority == RecommendationPriority.LOW, 1),
            else_=0
        )

        stmt = (
            select(Recommendation)
            .where(and_(*filters))
            .order_by(
                # Order by priority (HIGH first), then created_date DESC
                priority_order.desc(),
                Recommendation.created_date.desc()
            )
        )

        result = await self.db.execute(stmt)
        recommendations = result.scalars().all()

        return list(recommendations)

    async def dismiss_recommendation(
        self,
        recommendation_id: UUID,
        user_id: UUID
    ) -> Recommendation:
        """
        Dismiss a recommendation.

        Args:
            recommendation_id: Recommendation UUID
            user_id: User UUID (for authorization)

        Returns:
            Updated Recommendation object

        Raises:
            ValueError: If recommendation not found
            PermissionError: If user doesn't own the recommendation
        """
        # Get recommendation
        stmt = select(Recommendation).where(Recommendation.id == recommendation_id)
        result = await self.db.execute(stmt)
        recommendation = result.scalar_one_or_none()

        if not recommendation:
            raise ValueError(f"Recommendation {recommendation_id} not found")

        # Verify ownership
        if recommendation.user_id != user_id:
            raise PermissionError(f"User {user_id} does not own recommendation {recommendation_id}")

        # Dismiss
        recommendation.dismiss()

        await self.db.commit()
        await self.db.refresh(recommendation)

        logger.info(f"Dismissed recommendation {recommendation_id} for user {user_id}")

        return recommendation

    async def complete_recommendation(
        self,
        recommendation_id: UUID,
        user_id: UUID
    ) -> Recommendation:
        """
        Mark a recommendation as completed.

        Args:
            recommendation_id: Recommendation UUID
            user_id: User UUID (for authorization)

        Returns:
            Updated Recommendation object

        Raises:
            ValueError: If recommendation not found
            PermissionError: If user doesn't own the recommendation
        """
        # Get recommendation
        stmt = select(Recommendation).where(Recommendation.id == recommendation_id)
        result = await self.db.execute(stmt)
        recommendation = result.scalar_one_or_none()

        if not recommendation:
            raise ValueError(f"Recommendation {recommendation_id} not found")

        # Verify ownership
        if recommendation.user_id != user_id:
            raise PermissionError(f"User {user_id} does not own recommendation {recommendation_id}")

        # Complete
        recommendation.complete()

        await self.db.commit()
        await self.db.refresh(recommendation)

        logger.info(f"Completed recommendation {recommendation_id} for user {user_id}")

        return recommendation

    # ===== HELPER METHODS =====

    async def _get_user(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_current_tax_status(self, user_id: UUID) -> Optional[UserTaxStatus]:
        """Get user's current tax status."""
        stmt = (
            select(UserTaxStatus)
            .where(
                UserTaxStatus.user_id == user_id,
                UserTaxStatus.effective_to.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ===== PROTECTION RECOMMENDATIONS =====

    async def _generate_protection_recommendations(
        self,
        user_id: UUID,
        base_currency: str
    ) -> List[Recommendation]:
        """
        Generate protection (life assurance) recommendations.

        Rules:
        - HIGH priority if coverage gap > 0
        - Recommendations based on coverage needs analysis
        """
        recommendations = []

        # Get current coverage analysis
        stmt = (
            select(CoverageNeedsAnalysis)
            .where(
                CoverageNeedsAnalysis.user_id == user_id,
                CoverageNeedsAnalysis.effective_to.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        analysis = result.scalar_one_or_none()

        if not analysis:
            # No analysis yet - user should create one
            return recommendations

        # Check for coverage gap
        if analysis.coverage_gap > 0:
            gap = Decimal(str(analysis.coverage_gap))
            current_cover = Decimal(str(analysis.current_total_cover))
            recommended_cover = Decimal(str(analysis.recommended_cover))

            recommendation = Recommendation(
                user_id=user_id,
                recommendation_type=RecommendationType.PROTECTION,
                priority=RecommendationPriority.HIGH,
                title="Increase your life assurance cover",
                description=(
                    f"You have a coverage gap of £{gap:,.2f}. Your current life assurance "
                    f"cover (£{current_cover:,.2f}) may not be sufficient to protect your family. "
                    f"We recommend £{recommended_cover:,.2f} based on your income, debts, and family needs."
                ),
                action_items=[
                    "Review your current life assurance policies",
                    "Get quotes for additional term life assurance",
                    "Consider income protection insurance if you have dependents"
                ],
                potential_savings=None,  # Risk mitigation, not savings
                currency=Currency.GBP
            )

            recommendations.append(recommendation)

        return recommendations

    # ===== ISA RECOMMENDATIONS =====

    async def _generate_isa_recommendations(
        self,
        user_id: UUID,
        base_currency: str
    ) -> List[Recommendation]:
        """
        Generate ISA (UK) recommendations.

        Rules:
        - Check if user is UK tax resident
        - Calculate ISA allowance used for current tax year
        - HIGH priority if < 60 days until year end and > £5,000 unused
        - MEDIUM priority otherwise
        """
        recommendations = []

        # Check if UK tax resident
        tax_status = await self._get_current_tax_status(user_id)
        if not tax_status or not tax_status.uk_tax_resident:
            return recommendations

        # Get current UK tax year (April 6 - April 5)
        today = date.today()
        if today.month < 4 or (today.month == 4 and today.day < 6):
            tax_year = f"{today.year - 1}/{str(today.year)[-2:]}"
        else:
            tax_year = f"{today.year}/{str(today.year + 1)[-2:]}"

        # Calculate ISA contributions for current tax year
        stmt = (
            select(func.sum(ISAContribution.contribution_amount))
            .where(
                ISAContribution.user_id == user_id,
                ISAContribution.tax_year == tax_year
            )
        )
        result = await self.db.execute(stmt)
        total_contributed = result.scalar() or Decimal('0.00')
        total_contributed = Decimal(str(total_contributed))

        # Calculate remaining allowance
        remaining = self.ISA_ANNUAL_ALLOWANCE - total_contributed

        # Only recommend if significant allowance remaining
        if remaining > Decimal('5000.00'):
            # Calculate days until year end (April 5)
            if today.month < 4 or (today.month == 4 and today.day < 6):
                year_end = date(today.year, 4, 5)
            else:
                year_end = date(today.year + 1, 4, 5)

            days_remaining = (year_end - today).days

            # Calculate potential tax saving (assume 5% return, 20% basic rate)
            assumed_return = remaining * Decimal('0.05')
            tax_saving = assumed_return * Decimal('0.20')

            # Determine priority based on urgency
            if days_remaining < 60:
                priority = RecommendationPriority.HIGH
            else:
                priority = RecommendationPriority.MEDIUM

            recommendation = Recommendation(
                user_id=user_id,
                recommendation_type=RecommendationType.ISA,
                priority=priority,
                title="Use your remaining ISA allowance",
                description=(
                    f"You have £{remaining:,.2f} of unused ISA allowance for the {tax_year} tax year. "
                    f"ISA allowances don't carry forward - you have {days_remaining} days until April 5 to use it. "
                    f"Moving investments to an ISA wrapper provides tax-free returns."
                ),
                action_items=[
                    f"Transfer up to £{remaining:,.2f} to your ISA before April 5",
                    "Consider a Stocks & Shares ISA for long-term growth",
                    "Set up automatic monthly transfers to maximize your allowance"
                ],
                potential_savings=tax_saving,
                currency=Currency.GBP
            )

            recommendations.append(recommendation)

        return recommendations

    # ===== TFSA RECOMMENDATIONS =====

    async def _generate_tfsa_recommendations(
        self,
        user_id: UUID,
        base_currency: str
    ) -> List[Recommendation]:
        """
        Generate TFSA (SA) recommendations.

        Rules:
        - Check if user is SA tax resident
        - Calculate TFSA allowance used for current tax year
        - Check lifetime limit as well
        - HIGH priority if < 60 days until year end and > R10,000 unused
        - MEDIUM priority otherwise
        """
        recommendations = []

        # Check if SA tax resident
        tax_status = await self._get_current_tax_status(user_id)
        if not tax_status or not tax_status.sa_tax_resident:
            return recommendations

        # Get current SA tax year (March 1 - Feb 28/29)
        today = date.today()
        if today.month < 3:
            tax_year = f"{today.year - 1}/{today.year}"
        else:
            tax_year = f"{today.year}/{today.year + 1}"

        # Calculate TFSA contributions for current tax year
        stmt_annual = (
            select(func.sum(TFSAContribution.contribution_amount))
            .where(
                TFSAContribution.user_id == user_id,
                TFSAContribution.tax_year == tax_year
            )
        )
        result = await self.db.execute(stmt_annual)
        annual_contributed = result.scalar() or Decimal('0.00')
        annual_contributed = Decimal(str(annual_contributed))

        # Calculate lifetime contributions
        stmt_lifetime = (
            select(func.sum(TFSAContribution.contribution_amount))
            .where(TFSAContribution.user_id == user_id)
        )
        result = await self.db.execute(stmt_lifetime)
        lifetime_contributed = result.scalar() or Decimal('0.00')
        lifetime_contributed = Decimal(str(lifetime_contributed))

        # Calculate remaining allowances
        annual_remaining = self.TFSA_ANNUAL_ALLOWANCE - annual_contributed
        lifetime_remaining = self.TFSA_LIFETIME_ALLOWANCE - lifetime_contributed

        # Only recommend if significant allowance remaining and not hitting lifetime limit
        if annual_remaining > Decimal('10000.00') and lifetime_remaining > annual_remaining:
            # Calculate days until year end (Feb 28/29)
            if today.month < 3:
                year_end = date(today.year, 2, 28 if today.year % 4 != 0 else 29)
            else:
                year_end = date(today.year + 1, 2, 28 if (today.year + 1) % 4 != 0 else 29)

            days_remaining = (year_end - today).days

            # Determine priority based on urgency
            if days_remaining < 60:
                priority = RecommendationPriority.HIGH
            else:
                priority = RecommendationPriority.MEDIUM

            recommendation = Recommendation(
                user_id=user_id,
                recommendation_type=RecommendationType.TFSA,
                priority=priority,
                title="Maximize your Tax-Free Savings Account",
                description=(
                    f"You have R{annual_remaining:,.2f} of unused TFSA allowance for the {tax_year} tax year. "
                    f"TFSA returns are completely tax-free. You have {days_remaining} days until February 28 to use it. "
                    f"Lifetime remaining: R{lifetime_remaining:,.2f}"
                ),
                action_items=[
                    f"Contribute up to R{annual_remaining:,.2f} to your TFSA before February 28",
                    "Ensure you don't exceed the lifetime limit of R500,000",
                    "Consider using TFSA for long-term tax-free growth"
                ],
                potential_savings=None,  # ZAR savings, currency conversion complex
                currency=Currency.ZAR
            )

            recommendations.append(recommendation)

        return recommendations

    # ===== EMERGENCY FUND RECOMMENDATIONS =====

    async def _generate_emergency_fund_recommendations(
        self,
        user_id: UUID,
        base_currency: str
    ) -> List[Recommendation]:
        """
        Generate emergency fund recommendations.

        Rules:
        - HIGH priority if < 3 months expenses
        - Use EmergencyFundAssessmentService
        """
        recommendations = []

        # Get emergency fund service
        ef_service = EmergencyFundAssessmentService(self.db)

        # Get user's monthly income (use as proxy for expenses if not available)
        stmt = (
            select(func.sum(UserIncome.amount))
            .where(
                UserIncome.user_id == user_id,
                UserIncome.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        monthly_income = result.scalar() or Decimal('0.00')
        monthly_income = Decimal(str(monthly_income))

        # Estimate monthly expenses as 70% of income
        monthly_expenses = monthly_income * Decimal('0.70') if monthly_income > 0 else Decimal('2000.00')

        # Get current emergency fund
        current_ef = await ef_service.get_current_emergency_fund(user_id, base_currency)

        # Calculate months covered
        if monthly_expenses > 0:
            months_covered = current_ef / monthly_expenses
        else:
            months_covered = Decimal('0.00')

        # Recommend if < 3 months
        if months_covered < self.EMERGENCY_FUND_MONTHS:
            recommended = monthly_expenses * self.EMERGENCY_FUND_MONTHS
            shortfall = recommended - current_ef

            recommendation = Recommendation(
                user_id=user_id,
                recommendation_type=RecommendationType.EMERGENCY_FUND,
                priority=RecommendationPriority.HIGH,
                title="Build your emergency fund",
                description=(
                    f"You have only £{current_ef:,.2f} in emergency savings ({months_covered:.1f} months of expenses). "
                    f"We recommend at least 3-6 months of expenses (£{recommended:,.2f}) in easily accessible accounts. "
                    f"You need £{shortfall:,.2f} more to reach the minimum 3-month target."
                ),
                action_items=[
                    f"Set up automatic transfers of £{shortfall / 12:,.2f} per month to build your fund over 12 months",
                    "Keep emergency funds in instant-access savings accounts",
                    "Mark appropriate savings accounts as 'Emergency Fund' to track your progress"
                ],
                potential_savings=None,  # Financial resilience, not savings
                currency=Currency.GBP
            )

            recommendations.append(recommendation)

        return recommendations

    # ===== TAX EFFICIENCY RECOMMENDATIONS =====

    async def _generate_tax_efficiency_recommendations(
        self,
        user_id: UUID,
        base_currency: str
    ) -> List[Recommendation]:
        """
        Generate tax efficiency recommendations.

        Rules:
        - Check for GIA (General Investment Account) when ISA allowance available
        - Calculate potential tax savings
        """
        recommendations = []

        # Check if UK tax resident
        tax_status = await self._get_current_tax_status(user_id)
        if not tax_status or not tax_status.uk_tax_resident:
            return recommendations

        # Get GIA holdings
        stmt = (
            select(InvestmentAccount)
            .where(
                InvestmentAccount.user_id == user_id,
                InvestmentAccount.account_type == InvAccountType.GIA,
                InvestmentAccount.status == 'ACTIVE',
                InvestmentAccount.deleted == False
            )
            .options(selectinload(InvestmentAccount.holdings))
        )
        result = await self.db.execute(stmt)
        gia_accounts = result.scalars().all()

        # Calculate total GIA value
        total_gia_value = Decimal('0.00')
        for account in gia_accounts:
            for holding in account.holdings:
                if not holding.deleted:
                    total_gia_value += holding.current_value

        # Check ISA allowance remaining (from ISA recommendation logic)
        today = date.today()
        if today.month < 4 or (today.month == 4 and today.day < 6):
            tax_year = f"{today.year - 1}/{str(today.year)[-2:]}"
        else:
            tax_year = f"{today.year}/{str(today.year + 1)[-2:]}"

        stmt = (
            select(func.sum(ISAContribution.contribution_amount))
            .where(
                ISAContribution.user_id == user_id,
                ISAContribution.tax_year == tax_year
            )
        )
        result = await self.db.execute(stmt)
        total_contributed = result.scalar() or Decimal('0.00')
        total_contributed = Decimal(str(total_contributed))

        isa_remaining = self.ISA_ANNUAL_ALLOWANCE - total_contributed

        # Recommend if GIA > £5,000 and ISA allowance available
        if total_gia_value > Decimal('5000.00') and isa_remaining > Decimal('5000.00'):
            # Calculate potential annual tax saving (6% return, 20% tax)
            annual_return = total_gia_value * Decimal('0.06')
            tax_saving = annual_return * Decimal('0.20')

            recommendation = Recommendation(
                user_id=user_id,
                recommendation_type=RecommendationType.TAX_EFFICIENCY,
                priority=RecommendationPriority.MEDIUM,
                title="Transfer investments from GIA to ISA",
                description=(
                    f"You have £{total_gia_value:,.2f} in a General Investment Account that could be "
                    f"sheltered in an ISA. You have £{isa_remaining:,.2f} of ISA allowance remaining. "
                    f"Moving investments to an ISA could save you approximately £{tax_saving:,.2f} per year in tax "
                    f"(based on a 6% return assumption)."
                ),
                action_items=[
                    f"Consider 'Bed and ISA' to transfer up to £{min(total_gia_value, isa_remaining):,.2f} of holdings",
                    "Contact your investment platform to arrange the transfer",
                    "Be aware of potential CGT implications on the sale"
                ],
                potential_savings=tax_saving,
                currency=Currency.GBP
            )

            recommendations.append(recommendation)

        return recommendations

    # ===== PENSION RECOMMENDATIONS =====

    async def _generate_pension_recommendations(
        self,
        user_id: UUID,
        base_currency: str
    ) -> List[Recommendation]:
        """
        Generate pension recommendations.

        Rules:
        - Check for employer pension contributions
        - Recommend maximizing employer match
        - HIGH priority if missing free money
        """
        recommendations = []

        # Note: In a real implementation, we would:
        # 1. Check user's pension contributions
        # 2. Check employer pension scheme details
        # 3. Calculate if user is missing employer match
        # For this simplified version, we'll return empty list
        # This would be implemented in Phase 2C or 3

        return recommendations
