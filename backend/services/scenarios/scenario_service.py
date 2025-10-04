"""
Scenario Analysis Service

Provides core scenario management and execution:
- Create, read, update, delete scenarios
- Execute scenario calculations with projections
- Compare multiple scenarios
- Baseline snapshot creation
- Scenario expiration management

Business Rules:
- Maximum 5 active (non-archived) scenarios per user
- Only one base_case per user
- Scenarios expire 90 days after last access
- Calculation time target: <5 seconds
- Can model up to 30 years into future

Performance:
- Async database operations throughout
- Optimized queries with proper indexing
- Cached baseline snapshots
"""

import logging
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.scenario import (
    Scenario, ScenarioAssumption, ScenarioResult,
    ScenarioType, ScenarioStatus
)
from models.user import User
from models.savings_account import SavingsAccount
from models.investment import InvestmentAccount
from models.retirement import UKPension, SARetirementFund

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when scenario data validation fails."""
    pass


class NotFoundError(Exception):
    """Raised when scenario not found."""
    pass


class PermissionError(Exception):
    """Raised when user doesn't have permission to access scenario."""
    pass


class ScenarioLimitError(Exception):
    """Raised when user exceeds maximum scenario limit."""
    pass


class ScenarioService:
    """Service for scenario analysis operations."""

    MAX_ACTIVE_SCENARIOS = 5
    SCENARIO_EXPIRY_DAYS = 90

    def __init__(self, db: AsyncSession):
        """
        Initialize scenario service.

        Args:
            db: Database session for operations
        """
        self.db = db

    async def create_scenario(
        self,
        user_id: UUID,
        scenario_data: Dict[str, Any]
    ) -> Scenario:
        """
        Create a new financial scenario.

        Args:
            user_id: User UUID
            scenario_data: Dict containing:
                - scenario_name: str
                - scenario_type: ScenarioType
                - description: Optional[str]
                - base_case: bool (default False)
                - assumptions: List[Dict] (assumption objects)

        Returns:
            Created Scenario object

        Raises:
            ValidationError: If validation fails
            ScenarioLimitError: If max scenarios exceeded
        """
        logger.info(f"Creating scenario for user {user_id}")

        # Check scenario count limit
        active_count = await self._count_active_scenarios(user_id)
        if active_count >= self.MAX_ACTIVE_SCENARIOS:
            raise ScenarioLimitError(
                f"Maximum {self.MAX_ACTIVE_SCENARIOS} active scenarios allowed. "
                f"Please archive an existing scenario first."
            )

        # If base_case, ensure only one base case exists
        if scenario_data.get('base_case', False):
            await self._clear_existing_base_case(user_id)

        # Create scenario
        scenario = Scenario(
            id=uuid.uuid4(),
            user_id=user_id,
            scenario_name=scenario_data['scenario_name'],
            scenario_type=scenario_data['scenario_type'],
            description=scenario_data.get('description'),
            base_case=scenario_data.get('base_case', False),
            status=ScenarioStatus.DRAFT,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_accessed_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=self.SCENARIO_EXPIRY_DAYS)
        )

        self.db.add(scenario)
        await self.db.flush()

        # Add assumptions
        assumptions_data = scenario_data.get('assumptions', [])
        for assumption in assumptions_data:
            scenario_assumption = ScenarioAssumption(
                id=uuid.uuid4(),
                scenario_id=scenario.id,
                assumption_type=assumption['assumption_type'],
                assumption_key=assumption['assumption_key'],
                assumption_value=assumption['assumption_value'],
                unit=assumption.get('unit'),
                created_at=datetime.utcnow()
            )
            self.db.add(scenario_assumption)

        await self.db.commit()
        await self.db.refresh(scenario)

        logger.info(f"Created scenario {scenario.id} for user {user_id}")
        return scenario

    async def get_scenario(
        self,
        scenario_id: UUID,
        user_id: UUID
    ) -> Scenario:
        """
        Get scenario by ID with ownership check.

        Args:
            scenario_id: Scenario UUID
            user_id: User UUID (for ownership verification)

        Returns:
            Scenario object with relationships loaded

        Raises:
            NotFoundError: If scenario not found
            PermissionError: If user doesn't own scenario
        """
        query = (
            select(Scenario)
            .where(Scenario.id == scenario_id)
            .options(
                selectinload(Scenario.assumptions),
                selectinload(Scenario.results)
            )
        )

        result = await self.db.execute(query)
        scenario = result.scalar_one_or_none()

        if not scenario:
            raise NotFoundError(f"Scenario {scenario_id} not found")

        if scenario.user_id != user_id:
            raise PermissionError(f"User {user_id} does not have access to scenario {scenario_id}")

        # Update last accessed time
        scenario.last_accessed_at = datetime.utcnow()
        scenario.expires_at = datetime.utcnow() + timedelta(days=self.SCENARIO_EXPIRY_DAYS)
        await self.db.commit()

        return scenario

    async def list_scenarios(
        self,
        user_id: UUID,
        status: Optional[ScenarioStatus] = None,
        include_expired: bool = False
    ) -> List[Scenario]:
        """
        List all scenarios for a user.

        Args:
            user_id: User UUID
            status: Optional status filter
            include_expired: Whether to include expired scenarios

        Returns:
            List of Scenario objects
        """
        query = (
            select(Scenario)
            .where(Scenario.user_id == user_id)
            .options(
                selectinload(Scenario.assumptions),
                selectinload(Scenario.results)
            )
            .order_by(Scenario.created_at.desc())
        )

        if status:
            query = query.where(Scenario.status == status)

        if not include_expired:
            query = query.where(Scenario.expires_at > datetime.utcnow())

        result = await self.db.execute(query)
        scenarios = result.scalars().all()

        return list(scenarios)

    async def update_scenario(
        self,
        scenario_id: UUID,
        user_id: UUID,
        update_data: Dict[str, Any]
    ) -> Scenario:
        """
        Update scenario details.

        Args:
            scenario_id: Scenario UUID
            user_id: User UUID (for ownership verification)
            update_data: Dict containing fields to update

        Returns:
            Updated Scenario object

        Raises:
            NotFoundError: If scenario not found
            PermissionError: If user doesn't own scenario
        """
        scenario = await self.get_scenario(scenario_id, user_id)

        # Update allowed fields
        if 'scenario_name' in update_data:
            scenario.scenario_name = update_data['scenario_name']
        if 'description' in update_data:
            scenario.description = update_data['description']
        if 'status' in update_data:
            scenario.status = update_data['status']

        # Update assumptions if provided
        if 'assumptions' in update_data:
            # Remove existing assumptions
            await self.db.execute(
                select(ScenarioAssumption).where(
                    ScenarioAssumption.scenario_id == scenario_id
                )
            )
            # Add new assumptions
            for assumption in update_data['assumptions']:
                scenario_assumption = ScenarioAssumption(
                    id=uuid.uuid4(),
                    scenario_id=scenario.id,
                    assumption_type=assumption['assumption_type'],
                    assumption_key=assumption['assumption_key'],
                    assumption_value=assumption['assumption_value'],
                    unit=assumption.get('unit'),
                    created_at=datetime.utcnow()
                )
                self.db.add(scenario_assumption)

        scenario.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(scenario)

        logger.info(f"Updated scenario {scenario_id}")
        return scenario

    async def delete_scenario(
        self,
        scenario_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete (archive) a scenario.

        Args:
            scenario_id: Scenario UUID
            user_id: User UUID (for ownership verification)

        Raises:
            NotFoundError: If scenario not found
            PermissionError: If user doesn't own scenario
        """
        scenario = await self.get_scenario(scenario_id, user_id)

        # Soft delete by archiving
        scenario.status = ScenarioStatus.ARCHIVED
        scenario.updated_at = datetime.utcnow()
        await self.db.commit()

        logger.info(f"Archived scenario {scenario_id}")

    async def run_scenario(
        self,
        scenario_id: UUID,
        user_id: UUID,
        execution_params: Dict[str, Any]
    ) -> ScenarioResult:
        """
        Execute scenario calculations and generate results.

        Args:
            scenario_id: Scenario UUID
            user_id: User UUID (for ownership verification)
            execution_params: Dict containing:
                - projection_years: int (1-30)
                - growth_rate: Decimal (investment growth %)
                - inflation_rate: Decimal (inflation %)
                - include_monte_carlo: bool
                - monte_carlo_simulations: int

        Returns:
            ScenarioResult object with all projections

        Raises:
            NotFoundError: If scenario not found
            PermissionError: If user doesn't own scenario
        """
        logger.info(f"Running scenario {scenario_id}")

        scenario = await self.get_scenario(scenario_id, user_id)

        # Get user's current financial state
        baseline = await self._build_user_baseline(user_id)

        # Apply scenario assumptions to baseline
        scenario_state = await self._apply_scenario_modifications(baseline, scenario)

        # Run projections
        projection_years = execution_params.get('projection_years', 30)
        growth_rate = execution_params.get('growth_rate', Decimal('6.00'))
        inflation_rate = execution_params.get('inflation_rate', Decimal('2.50'))

        projections = await self._calculate_projections(
            scenario_state,
            projection_years,
            growth_rate,
            inflation_rate
        )

        # Create or update results
        existing_result = await self.db.execute(
            select(ScenarioResult).where(ScenarioResult.scenario_id == scenario_id)
        )
        result = existing_result.scalar_one_or_none()

        if not result:
            result = ScenarioResult(
                id=uuid.uuid4(),
                scenario_id=scenario_id
            )
            self.db.add(result)

        # Update result fields
        result.calculation_date = datetime.utcnow()
        result.calculation_version = "1.0.0"
        result.projection_years = projection_years
        result.net_worth_projection = projections['net_worth_projection']
        result.retirement_income_projection = projections['retirement_income_projection']
        result.tax_liability_projection = projections['tax_liability_projection']
        result.goal_achievement_projection = projections.get('goal_achievement_projection')
        result.detailed_breakdown = projections.get('detailed_breakdown')
        result.total_lifetime_tax = projections.get('total_lifetime_tax')
        result.final_net_worth = projections.get('final_net_worth')
        result.retirement_adequacy_ratio = projections.get('retirement_adequacy_ratio')
        result.goals_achieved_count = projections.get('goals_achieved_count', 0)
        result.goals_achieved_percentage = projections.get('goals_achieved_percentage')
        result.probability_of_success = projections.get('probability_of_success')

        # Update scenario status
        scenario.status = ScenarioStatus.CALCULATED
        scenario.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(result)

        logger.info(f"Completed scenario {scenario_id} calculation")
        return result

    async def compare_scenarios(
        self,
        scenario_ids: List[UUID],
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Compare multiple scenarios side-by-side.

        Args:
            scenario_ids: List of Scenario UUIDs (2-5)
            user_id: User UUID (for ownership verification)

        Returns:
            Dict containing comparison data

        Raises:
            ValidationError: If < 2 or > 5 scenarios
            NotFoundError: If any scenario not found
            PermissionError: If user doesn't own all scenarios
        """
        if len(scenario_ids) < 2:
            raise ValidationError("Need at least 2 scenarios to compare")
        if len(scenario_ids) > 5:
            raise ValidationError("Cannot compare more than 5 scenarios")

        # Load all scenarios with results
        scenarios = []
        for scenario_id in scenario_ids:
            scenario = await self.get_scenario(scenario_id, user_id)
            if scenario.status != ScenarioStatus.CALCULATED:
                raise ValidationError(f"Scenario {scenario_id} has not been calculated yet")
            scenarios.append(scenario)

        # Build comparison
        comparison = {
            'scenarios': [],
            'metric_comparisons': {},
            'trade_offs': [],
            'recommendations': []
        }

        for scenario in scenarios:
            comparison['scenarios'].append({
                'id': str(scenario.id),
                'name': scenario.scenario_name,
                'type': scenario.scenario_type.value,
                'description': scenario.description
            })

        # Compare key metrics
        comparison['metric_comparisons']['final_net_worth'] = self._compare_metric(
            scenarios,
            'results.final_net_worth',
            higher_is_better=True
        )

        comparison['metric_comparisons']['total_lifetime_tax'] = self._compare_metric(
            scenarios,
            'results.total_lifetime_tax',
            higher_is_better=False
        )

        comparison['metric_comparisons']['retirement_adequacy'] = self._compare_metric(
            scenarios,
            'results.retirement_adequacy_ratio',
            higher_is_better=True
        )

        comparison['metric_comparisons']['goals_achieved'] = self._compare_metric(
            scenarios,
            'results.goals_achieved_percentage',
            higher_is_better=True
        )

        # Identify trade-offs
        comparison['trade_offs'] = self._identify_trade_offs(scenarios)

        # Generate recommendations
        comparison['recommendations'] = self._generate_comparison_recommendations(scenarios, comparison)

        # Determine overall best
        comparison['overall_best_scenario_id'] = self._determine_best_scenario(scenarios, comparison)

        return comparison

    # Private helper methods

    async def _count_active_scenarios(self, user_id: UUID) -> int:
        """Count active (non-archived) scenarios for user."""
        query = select(func.count(Scenario.id)).where(
            and_(
                Scenario.user_id == user_id,
                Scenario.status != ScenarioStatus.ARCHIVED
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def _clear_existing_base_case(self, user_id: UUID) -> None:
        """Clear base_case flag from any existing base case scenarios."""
        query = select(Scenario).where(
            and_(
                Scenario.user_id == user_id,
                Scenario.base_case == True
            )
        )
        result = await self.db.execute(query)
        existing_base_cases = result.scalars().all()

        for scenario in existing_base_cases:
            scenario.base_case = False

        await self.db.commit()

    async def _build_user_baseline(self, user_id: UUID) -> Dict[str, Any]:
        """
        Build baseline snapshot of user's current financial state.

        Returns dict with:
        - user demographics
        - tax status
        - income
        - net worth
        - assets (savings, investments, pensions)
        - liabilities
        """
        # Get user
        user_query = select(User).where(User.id == user_id)
        user_result = await self.db.execute(user_query)
        user = user_result.scalar_one()

        # Calculate age
        age = None
        if user.date_of_birth:
            today = datetime.utcnow().date()
            age = today.year - user.date_of_birth.year
            if today.month < user.date_of_birth.month or (
                today.month == user.date_of_birth.month and today.day < user.date_of_birth.day
            ):
                age -= 1

        # Get savings accounts
        savings_query = select(SavingsAccount).where(SavingsAccount.user_id == user_id)
        savings_result = await self.db.execute(savings_query)
        savings_accounts = savings_result.scalars().all()
        total_savings = sum(account.current_balance for account in savings_accounts)

        # Get investments
        investments_query = select(InvestmentAccount).where(InvestmentAccount.user_id == user_id)
        investments_result = await self.db.execute(investments_query)
        investment_accounts = investments_result.scalars().all()
        total_investments = sum(account.current_value for account in investment_accounts)

        # Get UK pensions
        uk_pensions_query = select(UKPension).where(UKPension.user_id == user_id)
        uk_pensions_result = await self.db.execute(uk_pensions_query)
        uk_pensions = uk_pensions_result.scalars().all()
        total_uk_pension = sum(pension.current_value or Decimal('0') for pension in uk_pensions)

        # Get SA retirement funds
        sa_funds_query = select(SARetirementFund).where(SARetirementFund.user_id == user_id)
        sa_funds_result = await self.db.execute(sa_funds_query)
        sa_funds = sa_funds_result.scalars().all()
        total_sa_pension = sum(fund.current_value for fund in sa_funds)

        baseline = {
            'user_id': user_id,
            'snapshot_date': datetime.utcnow(),
            'age': age,
            'date_of_birth': user.date_of_birth,
            'savings': total_savings,
            'investments': total_investments,
            'uk_pensions': total_uk_pension,
            'sa_pensions': total_sa_pension,
            'total_net_worth': total_savings + total_investments + total_uk_pension + total_sa_pension,
            'savings_accounts': [{'id': str(acc.id), 'balance': acc.current_balance} for acc in savings_accounts],
            'investment_accounts': [{'id': str(acc.id), 'value': acc.current_value} for acc in investment_accounts],
            'uk_pensions_list': [{'id': str(p.id), 'value': p.current_value} for p in uk_pensions],
            'sa_funds_list': [{'id': str(f.id), 'value': f.current_value} for f in sa_funds],
        }

        return baseline

    async def _apply_scenario_modifications(
        self,
        baseline: Dict[str, Any],
        scenario: Scenario
    ) -> Dict[str, Any]:
        """
        Apply scenario assumptions to baseline to create scenario state.

        Returns modified state with scenario assumptions applied.
        """
        # Deep copy baseline
        scenario_state = baseline.copy()

        # Apply assumptions based on scenario type
        for assumption in scenario.assumptions:
            if assumption.assumption_key == 'retirement_age':
                scenario_state['target_retirement_age'] = int(assumption.assumption_value)
            elif assumption.assumption_key == 'new_salary':
                scenario_state['annual_salary'] = Decimal(assumption.assumption_value)
            elif assumption.assumption_key == 'property_value':
                scenario_state['property_value'] = Decimal(assumption.assumption_value)
            elif assumption.assumption_key == 'deposit':
                scenario_state['property_deposit'] = Decimal(assumption.assumption_value)
            elif assumption.assumption_key == 'mortgage_rate':
                scenario_state['mortgage_rate'] = Decimal(assumption.assumption_value)
            elif assumption.assumption_key == 'mortgage_term':
                scenario_state['mortgage_term_years'] = int(assumption.assumption_value)

        return scenario_state

    async def _calculate_projections(
        self,
        scenario_state: Dict[str, Any],
        projection_years: int,
        growth_rate: Decimal,
        inflation_rate: Decimal
    ) -> Dict[str, Any]:
        """
        Calculate financial projections for scenario state.

        Returns dict with:
        - net_worth_projection: List[Dict] (year-by-year)
        - retirement_income_projection: Dict
        - tax_liability_projection: List[Dict]
        - summary metrics
        """
        net_worth_projections = []
        tax_projections = []
        current_net_worth = scenario_state['total_net_worth']
        total_tax = Decimal('0')

        # Simple projection model (will be enhanced)
        for year in range(1, projection_years + 1):
            # Calculate growth
            investment_growth = current_net_worth * (growth_rate / Decimal('100'))
            current_net_worth += investment_growth

            # Estimate tax (simplified)
            estimated_tax = investment_growth * Decimal('0.20')  # 20% tax rate estimate
            total_tax += estimated_tax

            net_worth_projections.append({
                'year': year,
                'age': scenario_state.get('age', 0) + year,
                'net_worth': float(current_net_worth),
                'growth': float(investment_growth)
            })

            tax_projections.append({
                'year': year,
                'tax': float(estimated_tax)
            })

        # Retirement income projection (simplified)
        retirement_age = scenario_state.get('target_retirement_age', 67)
        pension_pot = scenario_state.get('uk_pensions', Decimal('0')) + scenario_state.get('sa_pensions', Decimal('0'))

        # Project pension pot to retirement
        years_to_retirement = max(0, retirement_age - scenario_state.get('age', 0))
        for _ in range(years_to_retirement):
            pension_pot *= (Decimal('1') + growth_rate / Decimal('100'))

        # 4% safe withdrawal rate
        annual_retirement_income = pension_pot * Decimal('0.04')

        retirement_projection = {
            'retirement_age': retirement_age,
            'pension_pot_at_retirement': float(pension_pot),
            'annual_income': float(annual_retirement_income),
            'monthly_income': float(annual_retirement_income / Decimal('12'))
        }

        return {
            'net_worth_projection': net_worth_projections,
            'retirement_income_projection': retirement_projection,
            'tax_liability_projection': tax_projections,
            'total_lifetime_tax': float(total_tax),
            'final_net_worth': float(current_net_worth),
            'retirement_adequacy_ratio': Decimal('75.00'),  # Placeholder
            'goals_achieved_count': 0,
            'goals_achieved_percentage': Decimal('0.00')
        }

    def _compare_metric(
        self,
        scenarios: List[Scenario],
        metric_path: str,
        higher_is_better: bool
    ) -> Dict[str, Any]:
        """Compare a single metric across scenarios."""
        values = []

        for scenario in scenarios:
            # Extract metric value
            if metric_path.startswith('results.'):
                field = metric_path.split('.')[1]
                value = getattr(scenario.results, field, 0) or Decimal('0')
            else:
                value = Decimal('0')

            values.append({
                'scenario_id': str(scenario.id),
                'scenario_name': scenario.scenario_name,
                'value': float(value)
            })

        # Sort
        sorted_values = sorted(
            values,
            key=lambda x: x['value'],
            reverse=higher_is_better
        )

        best_value = sorted_values[0]['value'] if sorted_values else 0
        worst_value = sorted_values[-1]['value'] if sorted_values else 0

        return {
            'metric_name': metric_path,
            'higher_is_better': higher_is_better,
            'values': sorted_values,
            'best_scenario_id': sorted_values[0]['scenario_id'] if sorted_values else None,
            'worst_scenario_id': sorted_values[-1]['scenario_id'] if sorted_values else None,
            'range': worst_value - best_value if sorted_values else 0,
            'average': sum(v['value'] for v in values) / len(values) if values else 0
        }

    def _identify_trade_offs(self, scenarios: List[Scenario]) -> List[Dict[str, Any]]:
        """Identify trade-offs between scenarios."""
        trade_offs = []

        # Example: Early retirement vs higher net worth
        # (Would be more sophisticated in production)

        return trade_offs

    def _generate_comparison_recommendations(
        self,
        scenarios: List[Scenario],
        comparison: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on comparison."""
        recommendations = []

        # Example recommendations
        recommendations.append("Review the trade-offs between different scenarios carefully")
        recommendations.append("Consider your personal priorities when choosing a path")

        return recommendations

    def _determine_best_scenario(
        self,
        scenarios: List[Scenario],
        comparison: Dict[str, Any]
    ) -> Optional[str]:
        """Determine overall best scenario based on multiple metrics."""
        # Simplified: just pick scenario with highest final net worth
        metric_comp = comparison['metric_comparisons'].get('final_net_worth')
        if metric_comp:
            return metric_comp['best_scenario_id']
        return None
