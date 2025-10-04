"""
AI Advisory Service - AI-Powered Financial Recommendations

This service uses the LLM Service to generate personalized financial advice
across all modules: retirement, investment, tax, goals, and general queries.

Features:
- Retirement planning advice
- Investment portfolio optimization
- Tax optimization strategies
- Goal achievement recommendations
- Monthly financial insights generation
- Free-form question answering

All advice includes:
- Clear reasoning and explanations
- Quantified benefits where possible
- Action steps
- Risk considerations
- Mandatory disclaimers
"""

import logging
from decimal import Decimal
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from models.user import User
from models.tax_status import UserTaxStatus
from models.income import UserIncome
from models.savings_account import SavingsAccount
from models.investment import InvestmentAccount, InvestmentHolding
from models.retirement import UKPension, SARetirementFund
from models.life_assurance import LifeAssurancePolicy
from models.goal import FinancialGoal, GoalStatus
from services.ai.llm_service import LLMService, AdviceType, PROMPT_TEMPLATES
from services.dashboard_aggregation import DashboardAggregationService

logger = logging.getLogger(__name__)


class AIAdvisoryService:
    """
    Service for generating AI-powered financial advice.

    Uses LLM integration to provide personalized, context-aware financial
    recommendations across all financial planning modules.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize AI advisory service.

        Args:
            db: Database session for queries
        """
        self.db = db
        self.llm_service = LLMService(db)

    async def generate_retirement_advice(
        self,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Generate personalized retirement planning advice.

        Analyzes:
        - Current pension pot size
        - Annual contributions
        - Expected retirement age
        - Income replacement needs
        - UK/SA pension rules

        Args:
            user_id: User UUID

        Returns:
            Dictionary with:
                - advice: Human-readable advice text
                - recommendations: List of actionable recommendations
                - confidence_score: 0.0-1.0
                - requires_human_review: Boolean
                - sources: List of sources/rules referenced
        """
        logger.info(f"Generating retirement advice for user {user_id}")

        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Get pensions
        result = await self.db.execute(
            select(UKPension).where(UKPension.user_id == user_id)
        )
        uk_pensions = result.scalars().all()

        result = await self.db.execute(
            select(SARetirementFund).where(SARetirementFund.user_id == user_id)
        )
        sa_pensions = result.scalars().all()

        total_pension_pot = (
            sum(p.current_value for p in uk_pensions) +
            sum(p.current_value for p in sa_pensions)
        )

        # Get income
        result = await self.db.execute(
            select(UserIncome).where(UserIncome.user_id == user_id)
        )
        incomes = result.scalars().all()
        total_income = sum(income.annual_amount for income in incomes)

        # Calculate age and retirement age
        age = self._calculate_age(user.date_of_birth)
        retirement_age = 67  # Default UK state pension age

        # Create context
        context = await self.llm_service.create_financial_context(user_id)

        # Build prompt
        prompt = f"""
I am {age} years old and planning to retire at {retirement_age}. My current pension pot is £{total_pension_pot:,.2f}
and I earn £{total_income:,.2f} per year.

Questions:
1. Am I on track for a comfortable retirement?
2. How much should I be contributing to my pension?
3. Should I consider additional pension contributions for tax relief?
4. What is the optimal retirement age for my situation?
5. Are there any UK or SA pension strategies I should consider?

Please provide specific, actionable advice with clear reasoning.
"""

        # Generate advice
        llm_response = await self.llm_service.generate_completion(
            prompt=prompt,
            context=context,
            advice_type=AdviceType.RETIREMENT
        )

        # Parse recommendations from advice text
        recommendations = self._parse_recommendations(llm_response["advice"])

        return {
            "advice": llm_response["advice"],
            "recommendations": recommendations,
            "confidence_score": llm_response["confidence_score"],
            "requires_human_review": llm_response["requires_human_review"],
            "sources": [
                "UK pension annual allowance rules",
                "UK state pension age",
                "SA Regulation 28",
                "Section 10C tax deduction (SA)"
            ],
            "metadata": llm_response["metadata"]
        }

    async def generate_investment_advice(
        self,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Generate personalized investment advice.

        Analyzes:
        - Portfolio allocation (equity/bonds/cash)
        - Diversification
        - Tax efficiency (ISA/GIA usage)
        - Risk tolerance
        - Investment horizon

        Args:
            user_id: User UUID

        Returns:
            Dictionary with advice, recommendations, and metadata
        """
        logger.info(f"Generating investment advice for user {user_id}")

        # Get investments
        result = await self.db.execute(
            select(InvestmentAccount).where(InvestmentAccount.user_id == user_id)
        )
        investments = result.scalars().all()

        if not investments:
            return {
                "advice": "You don't have any investment accounts set up yet. Consider starting with tax-advantaged accounts like ISAs (UK) or TFSAs (SA).",
                "recommendations": [
                    {
                        "action": "Open an ISA account",
                        "reason": "Tax-free investment growth",
                        "impact": "Potential tax savings on investment returns"
                    }
                ],
                "confidence_score": 0.9,
                "requires_human_review": False,
                "sources": ["UK ISA rules"],
                "metadata": {}
            }

        # Calculate portfolio allocation
        total_value = sum(inv.current_value for inv in investments)

        # Get holdings for allocation analysis (simplified)
        equity_pct = 60  # Placeholder - would calculate from holdings
        bonds_pct = 30
        cash_pct = 10

        # Get user risk tolerance
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        risk_tolerance = "moderate"  # Default risk tolerance

        # Create context
        context = await self.llm_service.create_financial_context(user_id)

        # Build prompt
        prompt = f"""
My investment portfolio is worth £{total_value:,.2f} with approximately:
- {equity_pct}% in equities
- {bonds_pct}% in bonds
- {cash_pct}% in cash

My risk tolerance is {risk_tolerance} and I'm {self._calculate_age(user.date_of_birth)} years old.

Questions:
1. Is my asset allocation appropriate for my risk tolerance and age?
2. Should I rebalance my portfolio?
3. Am I properly diversified?
4. Should I be using ISAs or other tax-advantaged accounts?
5. Are there any tax-efficient investment strategies I should consider?

Please provide specific recommendations with clear reasoning.
"""

        # Generate advice
        llm_response = await self.llm_service.generate_completion(
            prompt=prompt,
            context=context,
            advice_type=AdviceType.INVESTMENT
        )

        recommendations = self._parse_recommendations(llm_response["advice"])

        return {
            "advice": llm_response["advice"],
            "recommendations": recommendations,
            "confidence_score": llm_response["confidence_score"],
            "requires_human_review": llm_response["requires_human_review"],
            "sources": [
                "Modern Portfolio Theory",
                "Age-based asset allocation guidelines",
                "UK ISA rules",
                "SA TFSA regulations"
            ],
            "metadata": llm_response["metadata"]
        }

    async def generate_tax_optimization_advice(
        self,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Generate tax optimization strategies.

        Analyzes:
        - Income sources and levels
        - Allowances used (ISA, pension, CGT, etc.)
        - Tax residency status
        - Deductions and reliefs available
        - DTA opportunities

        Args:
            user_id: User UUID

        Returns:
            Dictionary with tax-saving strategies and estimated savings
        """
        logger.info(f"Generating tax optimization advice for user {user_id}")

        # Get tax status
        result = await self.db.execute(
            select(UserTaxStatus)
            .where(UserTaxStatus.user_id == user_id)
            .order_by(UserTaxStatus.created_at.desc())
        )
        tax_status = result.scalar_one_or_none()

        # Get income
        result = await self.db.execute(
            select(UserIncome).where(UserIncome.user_id == user_id)
        )
        incomes = result.scalars().all()
        total_income = sum(income.annual_amount for income in incomes)

        # Get ISA usage
        result = await self.db.execute(
            select(func.sum(SavingsAccount.current_balance))
            .where(
                and_(
                    SavingsAccount.user_id == user_id,
                    SavingsAccount.account_type == "ISA"
                )
            )
        )
        isa_balance = result.scalar() or Decimal('0')

        # Get pension contributions (simplified)
        result = await self.db.execute(
            select(UKPension).where(UKPension.user_id == user_id)
        )
        pensions = result.scalars().all()
        total_pension_contrib = sum(
            p.employee_contribution_amount or Decimal('0')
            for p in pensions
        )

        # Create context
        context = await self.llm_service.create_financial_context(user_id)

        # Build prompt
        tax_residence = "UK"
        if tax_status:
            if tax_status.uk_tax_resident and tax_status.sa_tax_resident:
                tax_residence = "both UK and SA"
            elif tax_status.sa_tax_resident:
                tax_residence = "SA"

        prompt = f"""
I earn £{total_income:,.2f} per year and am tax resident in {tax_residence}.

Current tax-advantaged usage:
- ISA balance: £{isa_balance:,.2f} (annual allowance: £20,000)
- Pension contributions: £{total_pension_contrib:,.2f} per year

Questions:
1. What tax-saving opportunities am I missing?
2. Should I increase my pension contributions for tax relief?
3. Should I use my ISA allowance more effectively?
4. Are there any allowances or reliefs I'm not using?
5. If I'm resident in both UK and SA, how can I optimize for both systems?

Please provide specific tax strategies with estimated savings.
"""

        # Generate advice
        llm_response = await self.llm_service.generate_completion(
            prompt=prompt,
            context=context,
            advice_type=AdviceType.TAX_OPTIMIZATION
        )

        recommendations = self._parse_recommendations(llm_response["advice"])

        return {
            "advice": llm_response["advice"],
            "recommendations": recommendations,
            "confidence_score": llm_response["confidence_score"],
            "requires_human_review": llm_response["requires_human_review"],
            "sources": [
                "UK Income Tax rates and allowances",
                "UK pension tax relief",
                "UK ISA rules",
                "SA Income Tax Act",
                "UK-SA Double Tax Agreement"
            ],
            "metadata": llm_response["metadata"]
        }

    async def generate_goal_advice(
        self,
        goal_id: UUID
    ) -> Dict[str, Any]:
        """
        Generate advice for achieving a specific goal.

        Analyzes:
        - Goal target and deadline
        - Current progress
        - Required monthly savings
        - Strategies to accelerate achievement

        Args:
            goal_id: Goal UUID

        Returns:
            Dictionary with strategies to achieve goal faster
        """
        logger.info(f"Generating goal advice for goal {goal_id}")

        # Get goal
        result = await self.db.execute(
            select(FinancialGoal).where(FinancialGoal.id == goal_id)
        )
        goal = result.scalar_one_or_none()

        if not goal:
            raise ValueError(f"Goal {goal_id} not found")

        # Create context
        context = await self.llm_service.create_financial_context(goal.user_id)

        # Calculate progress
        progress_pct = (float(goal.current_amount) / float(goal.target_amount)) * 100 if goal.target_amount > 0 else 0

        # Calculate time remaining
        months_remaining = 0
        if goal.target_date:
            today = datetime.utcnow().date()
            if goal.target_date > today:
                months_remaining = (goal.target_date.year - today.year) * 12 + (goal.target_date.month - today.month)

        # Build prompt
        prompt = f"""
I'm saving for: {goal.name}
Target amount: £{goal.target_amount:,.2f}
Current progress: £{goal.current_amount:,.2f} ({progress_pct:.1f}%)
Target date: {goal.target_date.strftime('%B %Y') if goal.target_date else 'Not set'}
Time remaining: {months_remaining} months

Questions:
1. How can I achieve this goal faster?
2. What is a realistic monthly savings target?
3. Should I adjust my timeline or target amount?
4. Are there any tax-advantaged ways to save for this goal?
5. What risks should I consider?

Please provide specific, actionable strategies.
"""

        # Generate advice
        llm_response = await self.llm_service.generate_completion(
            prompt=prompt,
            context=context,
            advice_type=AdviceType.GENERAL
        )

        recommendations = self._parse_recommendations(llm_response["advice"])

        return {
            "advice": llm_response["advice"],
            "recommendations": recommendations,
            "confidence_score": llm_response["confidence_score"],
            "requires_human_review": llm_response["requires_human_review"],
            "sources": [
                "Goal planning best practices",
                "Tax-efficient savings strategies"
            ],
            "metadata": {
                **llm_response["metadata"],
                "goal_name": goal.name,
                "progress_percentage": progress_pct
            }
        }

    async def answer_financial_question(
        self,
        user_id: UUID,
        question: str
    ) -> Dict[str, Any]:
        """
        Answer a free-form financial question.

        Args:
            user_id: User UUID
            question: User's question

        Returns:
            Dictionary with personalized answer
        """
        logger.info(f"Answering financial question for user {user_id}")

        # Create context
        context = await self.llm_service.create_financial_context(user_id)

        # Generate advice
        llm_response = await self.llm_service.generate_completion(
            prompt=question,
            context=context,
            advice_type=AdviceType.GENERAL
        )

        return {
            "advice": llm_response["advice"],
            "recommendations": self._parse_recommendations(llm_response["advice"]),
            "confidence_score": llm_response["confidence_score"],
            "requires_human_review": llm_response["requires_human_review"],
            "sources": ["General financial planning principles"],
            "metadata": llm_response["metadata"]
        }

    async def generate_monthly_insights(
        self,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Generate monthly financial insights and summary.

        Analyzes changes over the past month:
        - Income changes
        - Expense patterns
        - Net worth changes
        - Goal progress
        - Notable transactions

        Args:
            user_id: User UUID

        Returns:
            Dictionary with monthly summary and 3-5 key insights
        """
        logger.info(f"Generating monthly insights for user {user_id}")

        # Get current dashboard data
        dashboard_service = DashboardAggregationService(self.db)
        current_data = await dashboard_service.get_dashboard_summary(user_id)

        # Get goals progress
        result = await self.db.execute(
            select(FinancialGoal)
            .where(
                and_(
                    FinancialGoal.user_id == user_id,
                    FinancialGoal.status == GoalStatus.IN_PROGRESS
                )
            )
        )
        goals = result.scalars().all()

        # Create context
        context = await self.llm_service.create_financial_context(user_id)

        # Build prompt
        current_net_worth = current_data.get("net_worth", {}).get("total_gbp", 0)
        active_goals = len(goals)

        prompt = f"""
Generate a monthly financial summary for me.

Current situation:
- Net worth: £{current_net_worth:,.2f}
- Active goals: {active_goals}

Please provide:
1. A brief summary of my financial month (2-3 sentences)
2. 3-5 key insights or observations
3. Any notable trends or patterns
4. Actionable recommendations for next month
5. Encouragement or praise for positive progress

Keep it conversational, supportive, and actionable.
"""

        # Generate insights
        llm_response = await self.llm_service.generate_completion(
            prompt=prompt,
            context=context,
            advice_type=AdviceType.GENERAL,
            temperature=0.8  # Slightly higher temperature for more engaging content
        )

        return {
            "advice": llm_response["advice"],
            "recommendations": self._parse_recommendations(llm_response["advice"]),
            "confidence_score": llm_response["confidence_score"],
            "requires_human_review": False,  # Monthly insights don't need review
            "sources": ["Personal financial data analysis"],
            "metadata": {
                **llm_response["metadata"],
                "period": "monthly",
                "generated_at": datetime.utcnow().isoformat()
            }
        }

    def _calculate_age(self, date_of_birth: Optional[datetime.date]) -> int:
        """
        Calculate age from date of birth.

        Args:
            date_of_birth: Date of birth

        Returns:
            Age in years
        """
        if not date_of_birth:
            return 35  # Default age if not provided

        today = datetime.utcnow().date()
        age = today.year - date_of_birth.year

        if today.month < date_of_birth.month or \
           (today.month == date_of_birth.month and today.day < date_of_birth.day):
            age -= 1

        return age

    def _parse_recommendations(self, advice_text: str) -> List[Dict[str, str]]:
        """
        Parse recommendations from advice text.

        Looks for numbered lists or bullet points and extracts them
        as structured recommendations.

        Args:
            advice_text: The full advice text

        Returns:
            List of recommendation dictionaries
        """
        recommendations = []

        # Look for numbered recommendations (1., 2., etc.)
        import re
        numbered_pattern = r'\d+\.\s+(.+?)(?=\n\d+\.|\n\n|$)'
        matches = re.findall(numbered_pattern, advice_text, re.DOTALL)

        for match in matches:
            # Clean up the text
            rec_text = match.strip()

            # Try to extract action and reason
            if ':' in rec_text:
                parts = rec_text.split(':', 1)
                action = parts[0].strip()
                reason = parts[1].strip()
            else:
                action = rec_text
                reason = "See advice text for details"

            recommendations.append({
                "action": action,
                "reason": reason,
                "impact": "Varies - see advice text"
            })

        # If no numbered list found, return generic recommendation
        if not recommendations:
            recommendations.append({
                "action": "Review the detailed advice above",
                "reason": "Multiple strategies discussed",
                "impact": "See advice text for estimated impact"
            })

        return recommendations[:5]  # Limit to 5 recommendations
