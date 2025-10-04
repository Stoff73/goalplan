"""
Proactive Alerts Service - AI-Powered Financial Alert Detection and Generation

This service analyzes user financial data to detect significant changes, identify
opportunities, and generate personalized proactive alerts using AI.

Features:
- Detects financial changes (spending spikes, income changes, balance drops)
- Identifies opportunities (unused allowances, goal milestones, tax optimization)
- Generates personalized alert messages using LLM
- Classifies alert urgency (HIGH, MEDIUM, LOW)
- Batch processing for all users (daily/monthly insights)
- Deduplication to prevent alert spam
- Rate limiting per user

Alert Types:
- ALLOWANCE: Unused ISA/TFSA allowances
- GOAL: Goal progress updates (milestones, falling behind)
- TAX: Tax threshold warnings, optimization opportunities
- SPENDING: Unusual spending patterns
- INVESTMENT: Portfolio rebalancing, performance alerts
- RETIREMENT: Pension contribution opportunities
"""

import logging
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from datetime import datetime, date, timedelta
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc

from models.user import User
from models.tax_status import UserTaxStatus
from models.income import UserIncome
from models.savings_account import SavingsAccount, ISAContribution, TFSAContribution
from models.investment import InvestmentAccount, InvestmentHolding
from models.retirement import UKPension, SARetirementFund, AnnualAllowanceTracking
from models.life_assurance import LifeAssurancePolicy
from models.goal import FinancialGoal, GoalStatus
from models.recommendation import Recommendation, RecommendationType, RecommendationPriority, Currency
from services.ai.llm_service import LLMService, AdviceType
from services.dashboard_aggregation import DashboardAggregationService

logger = logging.getLogger(__name__)


class AlertType(str, Enum):
    """Alert type enumeration."""
    ALLOWANCE = "ALLOWANCE"
    GOAL = "GOAL"
    TAX = "TAX"
    SPENDING = "SPENDING"
    INVESTMENT = "INVESTMENT"
    RETIREMENT = "RETIREMENT"


class AlertUrgency(str, Enum):
    """Alert urgency classification."""
    HIGH = "HIGH"      # Tax deadlines, goal at risk, security concerns
    MEDIUM = "MEDIUM"  # Opportunities, milestones, rebalancing
    LOW = "LOW"        # General tips, insights


class ProactiveAlertsService:
    """
    Service for proactive financial alert detection and generation.

    Uses AI to analyze user financial data, detect significant changes,
    identify opportunities, and generate personalized alert messages.
    """

    # Thresholds for change detection
    LARGE_EXPENSE_THRESHOLD_GBP = Decimal('1000.00')
    LARGE_EXPENSE_PCT_THRESHOLD = Decimal('0.10')  # 10% of monthly avg
    INCOME_CHANGE_THRESHOLD = Decimal('0.20')  # 20% variation
    BALANCE_DROP_THRESHOLD = Decimal('0.30')  # 30% decrease
    INVESTMENT_PERFORMANCE_THRESHOLD = Decimal('0.15')  # 15% gain/loss

    # Allowance thresholds
    ISA_ALLOWANCE_ANNUAL_GBP = Decimal('20000.00')  # 2024/25
    TFSA_ALLOWANCE_ANNUAL_ZAR = Decimal('36000.00')  # 2024/25
    ALLOWANCE_REMAINING_THRESHOLD = Decimal('0.50')  # 50% remaining
    ALLOWANCE_DEADLINE_DAYS = 90  # 3 months

    # Tax thresholds
    UK_HIGHER_RATE_THRESHOLD_GBP = Decimal('50270.00')  # 2024/25
    TAX_THRESHOLD_WARNING_GBP = Decimal('5000.00')  # Warn when within £5k

    # Portfolio rebalancing
    PORTFOLIO_DEVIATION_THRESHOLD = Decimal('0.10')  # 10% from target

    # Deduplication window (don't send same alert twice within 7 days)
    DEDUP_WINDOW_DAYS = 7

    # Maximum alerts per user per run
    MAX_ALERTS_PER_USER = 10

    def __init__(self, db: AsyncSession):
        """
        Initialize proactive alerts service.

        Args:
            db: Database session for queries
        """
        self.db = db
        self.llm_service = LLMService(db)
        self.dashboard_service = DashboardAggregationService(db)

    async def analyze_financial_changes(
        self,
        user_id: UUID,
        lookback_days: int = 30
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Analyze user's financial data for significant changes.

        Detects:
        - Large expenses (>£1000 or >10% monthly avg)
        - Income changes (>20% variation)
        - Account balance drops (>30% decrease)
        - Goal progress changes (milestones, falling behind)
        - Investment performance (>15% gain/loss)

        Args:
            user_id: User UUID
            lookback_days: Number of days to analyze (default: 30)

        Returns:
            Dictionary with:
                - changes: List of significant changes detected
                - opportunities: List of opportunities identified
        """
        logger.info(f"Analyzing financial changes for user {user_id} (lookback: {lookback_days} days)")

        changes = []
        opportunities = []

        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User {user_id} not found")

        # 1. Detect spending changes
        spending_changes = await self._detect_spending_changes(user_id, lookback_days)
        changes.extend(spending_changes)

        # 2. Detect income changes
        income_changes = await self._detect_income_changes(user_id, lookback_days)
        changes.extend(income_changes)

        # 3. Detect balance drops
        balance_changes = await self._detect_balance_drops(user_id, lookback_days)
        changes.extend(balance_changes)

        # 4. Detect goal progress changes
        goal_changes = await self._detect_goal_changes(user_id)
        changes.extend(goal_changes)

        # 5. Detect investment performance
        investment_changes = await self._detect_investment_changes(user_id, lookback_days)
        changes.extend(investment_changes)

        # 6. Identify allowance opportunities
        allowance_opps = await self._identify_allowance_opportunities(user_id)
        opportunities.extend(allowance_opps)

        # 7. Identify tax opportunities
        tax_opps = await self._identify_tax_opportunities(user_id)
        opportunities.extend(tax_opps)

        # 8. Identify emergency fund opportunities
        emergency_opps = await self._identify_emergency_fund_opportunities(user_id)
        opportunities.extend(emergency_opps)

        # 9. Identify portfolio rebalancing opportunities
        portfolio_opps = await self._identify_portfolio_opportunities(user_id)
        opportunities.extend(portfolio_opps)

        logger.info(f"Detected {len(changes)} changes and {len(opportunities)} opportunities for user {user_id}")

        return {
            "changes": changes,
            "opportunities": opportunities
        }

    async def generate_alerts(
        self,
        user_id: UUID,
        changes: List[Dict[str, Any]],
        opportunities: List[Dict[str, Any]]
    ) -> List[Recommendation]:
        """
        Generate personalized alerts from detected changes and opportunities.

        Uses LLM to create human-readable, actionable alert messages.
        Determines urgency and creates alert records.

        Args:
            user_id: User UUID
            changes: List of detected changes
            opportunities: List of identified opportunities

        Returns:
            List of generated alert (Recommendation) objects
        """
        logger.info(f"Generating alerts for user {user_id}: {len(changes)} changes, {len(opportunities)} opportunities")

        alerts = []

        # Get financial context for LLM
        context = await self.llm_service.create_financial_context(user_id)

        # Deduplicate against recent alerts
        recent_alerts = await self._get_recent_alerts(user_id, days=self.DEDUP_WINDOW_DAYS)

        # Process changes
        for change in changes:
            # Check if we've already alerted about this recently
            if self._is_duplicate_alert(change, recent_alerts):
                logger.debug(f"Skipping duplicate alert for {change['type']}")
                continue

            alert = await self._create_alert_from_change(user_id, change, context)
            if alert:
                alerts.append(alert)

            # Limit alerts per user
            if len(alerts) >= self.MAX_ALERTS_PER_USER:
                logger.warning(f"Reached max alerts ({self.MAX_ALERTS_PER_USER}) for user {user_id}")
                break

        # Process opportunities
        for opportunity in opportunities:
            if len(alerts) >= self.MAX_ALERTS_PER_USER:
                break

            if self._is_duplicate_alert(opportunity, recent_alerts):
                logger.debug(f"Skipping duplicate alert for {opportunity['type']}")
                continue

            alert = await self._create_alert_from_opportunity(user_id, opportunity, context)
            if alert:
                alerts.append(alert)

        # Save alerts to database
        for alert in alerts:
            self.db.add(alert)

        await self.db.commit()

        logger.info(f"Generated {len(alerts)} alerts for user {user_id}")

        return alerts

    async def generate_allowance_alert(
        self,
        user_id: UUID,
        allowance_data: Dict[str, Any]
    ) -> Optional[Recommendation]:
        """
        Generate ISA/TFSA allowance usage alert.

        Example: "You've used only £5,000 of your £20,000 ISA allowance.
        Consider transferring from your General Investment Account before April 5th."

        Args:
            user_id: User UUID
            allowance_data: Dict with allowance info (type, used, remaining, deadline)

        Returns:
            Recommendation object or None
        """
        logger.info(f"Generating allowance alert for user {user_id}")

        allowance_type = allowance_data.get("type")  # "ISA" or "TFSA"
        used = Decimal(str(allowance_data.get("used", 0)))
        remaining = Decimal(str(allowance_data.get("remaining", 0)))
        annual_limit = Decimal(str(allowance_data.get("annual_limit", 0)))
        deadline = allowance_data.get("deadline")  # date object
        currency = allowance_data.get("currency", "GBP")

        # Get context for LLM
        context = await self.llm_service.create_financial_context(user_id)

        # Build prompt for LLM
        days_until_deadline = (deadline - date.today()).days if deadline else 90

        prompt = f"""
Generate a brief, friendly alert message (2-3 sentences) about unused {allowance_type} allowance.

Details:
- Annual allowance: {currency_symbol(currency)}{annual_limit:,.2f}
- Used so far: {currency_symbol(currency)}{used:,.2f}
- Remaining: {currency_symbol(currency)}{remaining:,.2f}
- Tax year ends in: {days_until_deadline} days

Key points to mention:
1. How much allowance is still available
2. That allowances don't carry forward (use it or lose it)
3. Suggest action (e.g., transfer from General Investment Account to {allowance_type})
4. Mention the deadline

Keep it conversational and actionable.
"""

        # Generate message
        llm_response = await self.llm_service.generate_completion(
            prompt=prompt,
            context=context,
            advice_type=AdviceType.TAX_OPTIMIZATION,
            temperature=0.7
        )

        # Determine urgency based on deadline
        if days_until_deadline < 30:
            urgency = RecommendationPriority.HIGH
        elif days_until_deadline < 60:
            urgency = RecommendationPriority.MEDIUM
        else:
            urgency = RecommendationPriority.LOW

        # Create recommendation
        alert = Recommendation(
            user_id=user_id,
            recommendation_type=RecommendationType.ISA if allowance_type == "ISA" else RecommendationType.TFSA,
            priority=urgency,
            title=f"Use your remaining {allowance_type} allowance",
            description=llm_response["advice"],
            action_items=[
                f"Transfer {currency_symbol(currency)}{remaining:,.2f} to {allowance_type} before {deadline.strftime('%B %d, %Y')}"
            ],
            potential_savings=None,  # Could calculate tax savings
            currency=Currency.GBP if currency == "GBP" else Currency.ZAR
        )

        return alert

    async def generate_goal_progress_alert(
        self,
        user_id: UUID,
        goal: FinancialGoal
    ) -> Optional[Recommendation]:
        """
        Generate goal progress alert (milestone or falling behind).

        Examples:
        - "Congratulations! You're 25% of the way to your emergency fund goal."
        - "Your house deposit goal is falling behind. Increase monthly savings by £200."

        Args:
            user_id: User UUID
            goal: FinancialGoal object

        Returns:
            Recommendation object or None
        """
        logger.info(f"Generating goal progress alert for user {user_id}, goal {goal.id}")

        # Calculate progress
        progress_pct = float(goal.progress_percentage)
        is_on_track = goal.is_on_track()
        days_remaining = goal.days_remaining()

        # Get context
        context = await self.llm_service.create_financial_context(user_id)

        # Determine alert type
        if progress_pct >= 100:
            alert_type = "achieved"
        elif progress_pct % 25 < 5 and progress_pct >= 25:  # Near a milestone (25%, 50%, 75%)
            alert_type = "milestone"
        elif not is_on_track and days_remaining > 0:
            alert_type = "falling_behind"
        else:
            return None  # No alert needed

        # Build prompt
        if alert_type == "achieved":
            prompt = f"""
Generate a brief, celebratory message (2-3 sentences) congratulating the user on achieving their goal.

Goal: {goal.goal_name}
Target: £{goal.target_amount:,.2f}
Achieved: £{goal.current_amount:,.2f}

Make it warm, encouraging, and suggest next steps.
"""
            urgency = RecommendationPriority.LOW

        elif alert_type == "milestone":
            prompt = f"""
Generate a brief, encouraging message (2-3 sentences) celebrating a milestone achievement.

Goal: {goal.goal_name}
Target: £{goal.target_amount:,.2f}
Progress: {progress_pct:.0f}%
Current: £{goal.current_amount:,.2f}

Celebrate the progress and encourage them to keep going.
"""
            urgency = RecommendationPriority.LOW

        else:  # falling_behind
            shortfall = float(goal.target_amount) - float(goal.current_amount)
            monthly_needed = shortfall / max(1, days_remaining / 30)

            prompt = f"""
Generate a brief, supportive but direct message (2-3 sentences) about falling behind on a goal.

Goal: {goal.goal_name}
Target: £{goal.target_amount:,.2f}
Current: £{goal.current_amount:,.2f}
Days remaining: {days_remaining}
Shortfall: £{shortfall:,.2f}
Monthly savings needed: £{monthly_needed:,.2f}

Be encouraging but realistic about what needs to happen to get back on track.
"""
            urgency = RecommendationPriority.MEDIUM

        # Generate message
        llm_response = await self.llm_service.generate_completion(
            prompt=prompt,
            context=context,
            advice_type=AdviceType.GENERAL,
            temperature=0.8  # More creative for encouragement
        )

        # Create recommendation
        alert = Recommendation(
            user_id=user_id,
            recommendation_type=RecommendationType.EMERGENCY_FUND if goal.goal_type.value == "EMERGENCY_FUND" else RecommendationType.TAX_EFFICIENCY,
            priority=urgency,
            title=f"Goal Update: {goal.goal_name}",
            description=llm_response["advice"],
            action_items=[
                f"Review your goal progress" if alert_type != "falling_behind" else f"Increase monthly savings by £{monthly_needed:.2f}"
            ],
            potential_savings=None,
            currency=Currency.GBP if goal.currency == "GBP" else Currency.ZAR
        )

        return alert

    async def generate_tax_threshold_alert(
        self,
        user_id: UUID,
        income_data: Dict[str, Any]
    ) -> Optional[Recommendation]:
        """
        Generate tax threshold proximity alert.

        Example: "You're £3,500 away from the higher rate tax threshold.
        Consider increasing pension contributions to reduce your tax bill."

        Args:
            user_id: User UUID
            income_data: Dict with income and threshold info

        Returns:
            Recommendation object or None
        """
        logger.info(f"Generating tax threshold alert for user {user_id}")

        income = Decimal(str(income_data.get("income", 0)))
        threshold = Decimal(str(income_data.get("threshold", self.UK_HIGHER_RATE_THRESHOLD_GBP)))
        distance_to_threshold = threshold - income

        if distance_to_threshold > self.TAX_THRESHOLD_WARNING_GBP:
            return None  # Too far away

        # Get context
        context = await self.llm_service.create_financial_context(user_id)

        # Build prompt
        prompt = f"""
Generate a brief, actionable alert (2-3 sentences) about approaching a tax threshold.

Current income: £{income:,.2f}
Higher rate threshold: £{threshold:,.2f}
Distance to threshold: £{distance_to_threshold:,.2f}

Suggest pension contributions or other tax-efficient strategies to avoid crossing into the higher rate band.
Quantify the potential tax savings.
"""

        # Generate message
        llm_response = await self.llm_service.generate_completion(
            prompt=prompt,
            context=context,
            advice_type=AdviceType.TAX_OPTIMIZATION,
            temperature=0.7
        )

        # Calculate potential tax saving
        potential_saving = distance_to_threshold * Decimal('0.20')  # Save 20% tax

        # Create recommendation
        alert = Recommendation(
            user_id=user_id,
            recommendation_type=RecommendationType.TAX_EFFICIENCY,
            priority=RecommendationPriority.MEDIUM,
            title="Tax Threshold Alert",
            description=llm_response["advice"],
            action_items=[
                f"Consider pension contribution of £{distance_to_threshold:,.2f} to stay below threshold"
            ],
            potential_savings=potential_saving,
            currency=Currency.GBP
        )

        return alert

    async def generate_spending_alert(
        self,
        user_id: UUID,
        spending_data: Dict[str, Any]
    ) -> Optional[Recommendation]:
        """
        Generate unusual spending pattern alert.

        Example: "Your spending increased 30% this month (£3,200 vs usual £2,500).
        Review your budget to stay on track."

        Args:
            user_id: User UUID
            spending_data: Dict with spending info

        Returns:
            Recommendation object or None
        """
        logger.info(f"Generating spending alert for user {user_id}")

        current_spending = Decimal(str(spending_data.get("current", 0)))
        average_spending = Decimal(str(spending_data.get("average", 0)))
        increase_pct = Decimal(str(spending_data.get("increase_pct", 0)))

        # Get context
        context = await self.llm_service.create_financial_context(user_id)

        # Build prompt
        prompt = f"""
Generate a brief, non-judgmental alert (2-3 sentences) about increased spending.

Current month spending: £{current_spending:,.2f}
Average monthly spending: £{average_spending:,.2f}
Increase: {increase_pct:.0f}%

Be supportive and suggest reviewing the budget. Don't be preachy.
"""

        # Generate message
        llm_response = await self.llm_service.generate_completion(
            prompt=prompt,
            context=context,
            advice_type=AdviceType.GENERAL,
            temperature=0.8
        )

        # Create recommendation
        alert = Recommendation(
            user_id=user_id,
            recommendation_type=RecommendationType.DEBT_REDUCTION,
            priority=RecommendationPriority.MEDIUM,
            title="Spending Pattern Alert",
            description=llm_response["advice"],
            action_items=[
                "Review this month's transactions",
                "Check budget categories"
            ],
            potential_savings=None,
            currency=Currency.GBP
        )

        return alert

    async def generate_investment_alert(
        self,
        user_id: UUID,
        portfolio_data: Dict[str, Any]
    ) -> Optional[Recommendation]:
        """
        Generate portfolio rebalancing or performance alert.

        Example: "Your portfolio is overweight in UK equities (65% vs target 50%).
        Consider rebalancing to reduce risk."

        Args:
            user_id: User UUID
            portfolio_data: Dict with portfolio allocation info

        Returns:
            Recommendation object or None
        """
        logger.info(f"Generating investment alert for user {user_id}")

        alert_type = portfolio_data.get("alert_type")  # "rebalance" or "performance"

        # Get context
        context = await self.llm_service.create_financial_context(user_id)

        if alert_type == "rebalance":
            asset_class = portfolio_data.get("asset_class")
            current_pct = Decimal(str(portfolio_data.get("current_pct", 0)))
            target_pct = Decimal(str(portfolio_data.get("target_pct", 0)))

            prompt = f"""
Generate a brief alert (2-3 sentences) about portfolio rebalancing.

Asset class: {asset_class}
Current allocation: {current_pct:.0f}%
Target allocation: {target_pct:.0f}%

Suggest rebalancing to reduce concentration risk.
"""
        else:  # performance
            performance_pct = Decimal(str(portfolio_data.get("performance_pct", 0)))
            period = portfolio_data.get("period", "month")

            prompt = f"""
Generate a brief, informative alert (2-3 sentences) about investment performance.

Performance this {period}: {performance_pct:+.1f}%

{"Congratulate them on gains" if performance_pct > 0 else "Reassure them about losses"} but remind them to stay focused on long-term goals.
"""

        # Generate message
        llm_response = await self.llm_service.generate_completion(
            prompt=prompt,
            context=context,
            advice_type=AdviceType.INVESTMENT,
            temperature=0.7
        )

        # Create recommendation
        alert = Recommendation(
            user_id=user_id,
            recommendation_type=RecommendationType.INVESTMENT_DIVERSIFICATION,
            priority=RecommendationPriority.MEDIUM if alert_type == "rebalance" else RecommendationPriority.LOW,
            title="Portfolio Update" if alert_type == "performance" else "Rebalancing Opportunity",
            description=llm_response["advice"],
            action_items=[
                "Review portfolio allocation" if alert_type == "rebalance" else "Review investment performance"
            ],
            potential_savings=None,
            currency=Currency.GBP
        )

        return alert

    async def generate_retirement_alert(
        self,
        user_id: UUID,
        pension_data: Dict[str, Any]
    ) -> Optional[Recommendation]:
        """
        Generate pension contribution opportunity alert.

        Example: "Increasing your pension contribution by £100/month could save
        you £25,000 in tax over 10 years and boost your retirement pot by £35,000."

        Args:
            user_id: User UUID
            pension_data: Dict with pension info

        Returns:
            Recommendation object or None
        """
        logger.info(f"Generating retirement alert for user {user_id}")

        additional_contribution = Decimal(str(pension_data.get("additional_contribution", 0)))
        tax_saving_annual = Decimal(str(pension_data.get("tax_saving_annual", 0)))
        years_to_retirement = int(pension_data.get("years_to_retirement", 10))

        # Get context
        context = await self.llm_service.create_financial_context(user_id)

        # Calculate long-term benefit
        total_tax_saving = tax_saving_annual * years_to_retirement
        growth_assumption = Decimal('1.05') ** years_to_retirement  # 5% annual growth
        retirement_pot_boost = (additional_contribution * 12 * years_to_retirement) * growth_assumption

        prompt = f"""
Generate a brief, motivating alert (2-3 sentences) about pension contributions.

Additional monthly contribution: £{additional_contribution:,.2f}
Tax relief per year: £{tax_saving_annual:,.2f}
Total tax saving over {years_to_retirement} years: £{total_tax_saving:,.2f}
Retirement pot increase: £{retirement_pot_boost:,.2f}

Make it clear and compelling. Focus on the long-term benefit.
"""

        # Generate message
        llm_response = await self.llm_service.generate_completion(
            prompt=prompt,
            context=context,
            advice_type=AdviceType.RETIREMENT,
            temperature=0.7
        )

        # Create recommendation
        alert = Recommendation(
            user_id=user_id,
            recommendation_type=RecommendationType.PENSION,
            priority=RecommendationPriority.MEDIUM,
            title="Pension Contribution Opportunity",
            description=llm_response["advice"],
            action_items=[
                f"Increase pension contribution by £{additional_contribution:,.2f}/month"
            ],
            potential_savings=total_tax_saving,
            currency=Currency.GBP
        )

        return alert

    async def batch_generate_monthly_insights(self) -> Dict[str, Any]:
        """
        Generate monthly insights for all active users.

        Runs analysis for each user and generates personalized monthly summary:
        - Wins (achievements, milestones)
        - Concerns (falling behind, unusual patterns)
        - Trends (spending, saving, investing)
        - Recommendations (actionable next steps)

        Returns:
            Summary of insights generated:
                - total_users: Number of users processed
                - insights_generated: Number of insights created
                - errors: Number of errors encountered
        """
        logger.info("Starting batch monthly insights generation for all users")

        # Get all active users
        result = await self.db.execute(
            select(User).where(User.status == "ACTIVE")
        )
        users = result.scalars().all()

        total_users = len(users)
        insights_generated = 0
        errors = 0

        for user in users:
            try:
                # Generate monthly insights for this user
                insights = await self._generate_user_monthly_insights(user.id)

                if insights:
                    insights_generated += 1
                    logger.info(f"Generated monthly insights for user {user.id}")

            except Exception as e:
                logger.error(f"Error generating insights for user {user.id}: {str(e)}")
                errors += 1

        await self.db.commit()

        summary = {
            "total_users": total_users,
            "insights_generated": insights_generated,
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"Batch monthly insights complete: {summary}")

        return summary

    async def schedule_daily_analysis(self) -> Dict[str, int]:
        """
        Daily background job to analyze all users and generate alerts.

        Runs for all active users:
        1. Analyze past 30 days for changes
        2. Identify opportunities
        3. Generate alerts
        4. Store in database
        5. Trigger notifications

        Returns:
            Summary:
                - users_analyzed: Number of users processed
                - alerts_generated: Total alerts created
                - errors: Number of errors
        """
        logger.info("Starting daily analysis for all users")

        # Get all active users
        result = await self.db.execute(
            select(User).where(User.status == "ACTIVE")
        )
        users = result.scalars().all()

        users_analyzed = 0
        alerts_generated = 0
        errors = 0

        for user in users:
            try:
                # Analyze changes and opportunities
                analysis = await self.analyze_financial_changes(user.id, lookback_days=30)

                # Generate alerts
                alerts = await self.generate_alerts(
                    user.id,
                    analysis["changes"],
                    analysis["opportunities"]
                )

                users_analyzed += 1
                alerts_generated += len(alerts)

                logger.info(f"Generated {len(alerts)} alerts for user {user.id}")

            except Exception as e:
                logger.error(f"Error in daily analysis for user {user.id}: {str(e)}")
                errors += 1

        await self.db.commit()

        summary = {
            "users_analyzed": users_analyzed,
            "alerts_generated": alerts_generated,
            "errors": errors
        }

        logger.info(f"Daily analysis complete: {summary}")

        return summary

    # ==================== PRIVATE HELPER METHODS ====================

    async def _detect_spending_changes(
        self,
        user_id: UUID,
        lookback_days: int
    ) -> List[Dict[str, Any]]:
        """Detect unusual spending patterns."""
        # TODO: Implement actual spending change detection
        # For now, return empty list (would need transaction data)
        return []

    async def _detect_income_changes(
        self,
        user_id: UUID,
        lookback_days: int
    ) -> List[Dict[str, Any]]:
        """Detect significant income changes."""
        changes = []

        # Get current income
        result = await self.db.execute(
            select(UserIncome).where(UserIncome.user_id == user_id)
        )
        incomes = result.scalars().all()

        if not incomes:
            return []

        # Simple check: if income changed recently
        # In production, would compare against historical data
        for income in incomes:
            if income.updated_at and income.updated_at >= datetime.utcnow() - timedelta(days=lookback_days):
                changes.append({
                    "type": "income_change",
                    "description": f"Income updated: {income.income_type}",
                    "amount": float(income.annual_amount),
                    "severity": "medium"
                })

        return changes

    async def _detect_balance_drops(
        self,
        user_id: UUID,
        lookback_days: int
    ) -> List[Dict[str, Any]]:
        """Detect significant account balance decreases."""
        # TODO: Implement balance drop detection
        # Would need historical balance snapshots
        return []

    async def _detect_goal_changes(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Detect goal progress changes (milestones, falling behind)."""
        changes = []

        # Get active goals
        result = await self.db.execute(
            select(FinancialGoal).where(
                and_(
                    FinancialGoal.user_id == user_id,
                    FinancialGoal.status.in_([GoalStatus.IN_PROGRESS, GoalStatus.ON_TRACK, GoalStatus.AT_RISK])
                )
            )
        )
        goals = result.scalars().all()

        for goal in goals:
            progress_pct = float(goal.progress_percentage)
            is_on_track = goal.is_on_track()

            # Check for milestones
            if progress_pct >= 100:
                changes.append({
                    "type": "goal_achieved",
                    "goal_id": str(goal.id),
                    "goal_name": goal.goal_name,
                    "severity": "low"
                })
            elif progress_pct % 25 < 5 and progress_pct >= 25:
                changes.append({
                    "type": "goal_milestone",
                    "goal_id": str(goal.id),
                    "goal_name": goal.goal_name,
                    "progress_pct": progress_pct,
                    "severity": "low"
                })

            # Check if falling behind
            if not is_on_track and goal.days_remaining() > 0:
                changes.append({
                    "type": "goal_falling_behind",
                    "goal_id": str(goal.id),
                    "goal_name": goal.goal_name,
                    "severity": "medium"
                })

        return changes

    async def _detect_investment_changes(
        self,
        user_id: UUID,
        lookback_days: int
    ) -> List[Dict[str, Any]]:
        """Detect investment performance changes."""
        # TODO: Implement investment performance detection
        # Would need historical performance data
        return []

    async def _identify_allowance_opportunities(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Identify unused ISA/TFSA allowances."""
        opportunities = []

        # Get user tax status
        result = await self.db.execute(
            select(UserTaxStatus)
            .where(UserTaxStatus.user_id == user_id)
            .order_by(UserTaxStatus.created_at.desc())
        )
        tax_status = result.scalar_one_or_none()

        # Check ISA allowance (UK)
        if tax_status and tax_status.uk_tax_resident:
            # Get ISA contributions this tax year
            uk_tax_year_start = self._get_uk_tax_year_start()

            result = await self.db.execute(
                select(func.sum(ISAContribution.contribution_amount))
                .where(
                    and_(
                        ISAContribution.user_id == user_id,
                        ISAContribution.contribution_date >= uk_tax_year_start
                    )
                )
            )
            isa_used = result.scalar() or Decimal('0')
            isa_remaining = self.ISA_ALLOWANCE_ANNUAL_GBP - isa_used

            # Alert if >50% remaining and <3 months to deadline
            days_to_deadline = (self._get_uk_tax_year_end() - date.today()).days

            if isa_remaining > (self.ISA_ALLOWANCE_ANNUAL_GBP * self.ALLOWANCE_REMAINING_THRESHOLD):
                if days_to_deadline < self.ALLOWANCE_DEADLINE_DAYS:
                    opportunities.append({
                        "type": "isa_allowance",
                        "allowance_type": "ISA",
                        "used": float(isa_used),
                        "remaining": float(isa_remaining),
                        "annual_limit": float(self.ISA_ALLOWANCE_ANNUAL_GBP),
                        "deadline": self._get_uk_tax_year_end(),
                        "currency": "GBP",
                        "severity": "high" if days_to_deadline < 30 else "medium"
                    })

        # Check TFSA allowance (SA)
        if tax_status and tax_status.sa_tax_resident:
            # Similar logic for TFSA
            sa_tax_year_start = self._get_sa_tax_year_start()

            result = await self.db.execute(
                select(func.sum(TFSAContribution.contribution_amount))
                .where(
                    and_(
                        TFSAContribution.user_id == user_id,
                        TFSAContribution.contribution_date >= sa_tax_year_start
                    )
                )
            )
            tfsa_used = result.scalar() or Decimal('0')
            tfsa_remaining = self.TFSA_ALLOWANCE_ANNUAL_ZAR - tfsa_used

            days_to_deadline = (self._get_sa_tax_year_end() - date.today()).days

            if tfsa_remaining > (self.TFSA_ALLOWANCE_ANNUAL_ZAR * self.ALLOWANCE_REMAINING_THRESHOLD):
                if days_to_deadline < self.ALLOWANCE_DEADLINE_DAYS:
                    opportunities.append({
                        "type": "tfsa_allowance",
                        "allowance_type": "TFSA",
                        "used": float(tfsa_used),
                        "remaining": float(tfsa_remaining),
                        "annual_limit": float(self.TFSA_ALLOWANCE_ANNUAL_ZAR),
                        "deadline": self._get_sa_tax_year_end(),
                        "currency": "ZAR",
                        "severity": "high" if days_to_deadline < 30 else "medium"
                    })

        return opportunities

    async def _identify_tax_opportunities(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Identify tax optimization opportunities."""
        opportunities = []

        # Get total income
        result = await self.db.execute(
            select(func.sum(UserIncome.annual_amount))
            .where(UserIncome.user_id == user_id)
        )
        total_income = result.scalar() or Decimal('0')

        # Check if approaching higher rate threshold
        distance_to_threshold = self.UK_HIGHER_RATE_THRESHOLD_GBP - total_income

        if Decimal('0') < distance_to_threshold <= self.TAX_THRESHOLD_WARNING_GBP:
            opportunities.append({
                "type": "tax_threshold",
                "income": float(total_income),
                "threshold": float(self.UK_HIGHER_RATE_THRESHOLD_GBP),
                "distance": float(distance_to_threshold),
                "severity": "medium"
            })

        return opportunities

    async def _identify_emergency_fund_opportunities(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Identify emergency fund inadequacies."""
        opportunities = []

        # Get total savings
        result = await self.db.execute(
            select(func.sum(SavingsAccount.current_balance))
            .where(
                and_(
                    SavingsAccount.user_id == user_id,
                    SavingsAccount.account_type.in_(["CURRENT_ACCOUNT", "SAVINGS_ACCOUNT"])
                )
            )
        )
        emergency_fund = result.scalar() or Decimal('0')

        # Get monthly income
        result = await self.db.execute(
            select(func.sum(UserIncome.annual_amount))
            .where(UserIncome.user_id == user_id)
        )
        annual_income = result.scalar() or Decimal('0')
        monthly_income = annual_income / 12

        # Recommended: 6 months expenses (assume 80% of income)
        recommended_emergency_fund = monthly_income * 6 * Decimal('0.80')

        if emergency_fund < recommended_emergency_fund:
            opportunities.append({
                "type": "emergency_fund",
                "current": float(emergency_fund),
                "recommended": float(recommended_emergency_fund),
                "shortfall": float(recommended_emergency_fund - emergency_fund),
                "severity": "high" if emergency_fund < monthly_income * 3 else "medium"
            })

        return opportunities

    async def _identify_portfolio_opportunities(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Identify portfolio rebalancing opportunities."""
        # TODO: Implement portfolio rebalancing detection
        # Would need target allocations and current allocations
        return []

    async def _create_alert_from_change(
        self,
        user_id: UUID,
        change: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[Recommendation]:
        """Create alert from detected change."""
        change_type = change.get("type")

        if change_type == "goal_achieved" or change_type == "goal_milestone" or change_type == "goal_falling_behind":
            # Get goal
            goal_id = UUID(change["goal_id"])
            result = await self.db.execute(
                select(FinancialGoal).where(FinancialGoal.id == goal_id)
            )
            goal = result.scalar_one_or_none()
            if goal:
                return await self.generate_goal_progress_alert(user_id, goal)

        elif change_type == "income_change":
            return await self.generate_spending_alert(user_id, change)

        return None

    async def _create_alert_from_opportunity(
        self,
        user_id: UUID,
        opportunity: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[Recommendation]:
        """Create alert from identified opportunity."""
        opp_type = opportunity.get("type")

        if opp_type in ["isa_allowance", "tfsa_allowance"]:
            return await self.generate_allowance_alert(user_id, opportunity)

        elif opp_type == "tax_threshold":
            return await self.generate_tax_threshold_alert(user_id, opportunity)

        elif opp_type == "emergency_fund":
            # Could generate emergency fund alert
            pass

        return None

    async def _get_recent_alerts(self, user_id: UUID, days: int) -> List[Recommendation]:
        """Get recent alerts for deduplication."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        result = await self.db.execute(
            select(Recommendation).where(
                and_(
                    Recommendation.user_id == user_id,
                    Recommendation.created_date >= cutoff_date,
                    Recommendation.deleted == False
                )
            )
        )

        return result.scalars().all()

    def _is_duplicate_alert(
        self,
        new_alert_data: Dict[str, Any],
        recent_alerts: List[Recommendation]
    ) -> bool:
        """Check if this alert is a duplicate of a recent one."""
        alert_type = new_alert_data.get("type")

        for alert in recent_alerts:
            # Simple duplication check based on type
            if alert_type == "isa_allowance" and alert.recommendation_type == RecommendationType.ISA:
                return True
            elif alert_type == "tfsa_allowance" and alert.recommendation_type == RecommendationType.TFSA:
                return True
            elif alert_type == "tax_threshold" and alert.recommendation_type == RecommendationType.TAX_EFFICIENCY:
                return True
            # Add more duplication checks as needed

        return False

    async def _generate_user_monthly_insights(self, user_id: UUID) -> Optional[Recommendation]:
        """Generate monthly insights for a single user."""
        # Get dashboard data
        dashboard_data = await self.dashboard_service.get_dashboard_summary(user_id)

        # Get financial context
        context = await self.llm_service.create_financial_context(user_id)

        # Build prompt
        net_worth = dashboard_data.get("net_worth", {}).get("total_gbp", 0)

        prompt = f"""
Generate a brief monthly financial summary (3-4 sentences) for the user.

Current net worth: £{net_worth:,.2f}

Include:
1. A warm greeting and brief overview
2. One positive observation (achievement or progress)
3. One area for improvement or opportunity
4. Encouraging closing statement

Keep it conversational, supportive, and actionable.
"""

        # Generate insights
        llm_response = await self.llm_service.generate_completion(
            prompt=prompt,
            context=context,
            advice_type=AdviceType.GENERAL,
            temperature=0.8
        )

        # Create recommendation
        insight = Recommendation(
            user_id=user_id,
            recommendation_type=RecommendationType.TAX_EFFICIENCY,
            priority=RecommendationPriority.LOW,
            title="Your Monthly Financial Summary",
            description=llm_response["advice"],
            action_items=["Review your monthly progress"],
            potential_savings=None,
            currency=Currency.GBP
        )

        self.db.add(insight)

        return insight

    def _get_uk_tax_year_start(self) -> date:
        """Get UK tax year start date (April 6)."""
        today = date.today()
        if today.month >= 4 and today.day >= 6:
            return date(today.year, 4, 6)
        else:
            return date(today.year - 1, 4, 6)

    def _get_uk_tax_year_end(self) -> date:
        """Get UK tax year end date (April 5)."""
        today = date.today()
        if today.month >= 4 and today.day >= 6:
            return date(today.year + 1, 4, 5)
        else:
            return date(today.year, 4, 5)

    def _get_sa_tax_year_start(self) -> date:
        """Get SA tax year start date (March 1)."""
        today = date.today()
        if today.month >= 3:
            return date(today.year, 3, 1)
        else:
            return date(today.year - 1, 3, 1)

    def _get_sa_tax_year_end(self) -> date:
        """Get SA tax year end date (February 28/29)."""
        today = date.today()
        if today.month >= 3:
            year = today.year + 1
        else:
            year = today.year

        # Check for leap year
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            return date(year, 2, 29)
        else:
            return date(year, 2, 28)


def currency_symbol(currency: str) -> str:
    """Get currency symbol from currency code."""
    symbols = {
        "GBP": "£",
        "ZAR": "R",
        "USD": "$",
        "EUR": "€"
    }
    return symbols.get(currency, currency)
