"""
Monte Carlo Simulation Service

Runs probabilistic retirement planning simulations to:
- Calculate probability of retirement success
- Determine safe withdrawal rate
- Provide confidence intervals
- Model uncertainty in returns and inflation

Uses numpy for efficient simulation.
"""

import logging
import numpy as np
from decimal import Decimal
from typing import Dict, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class MonteCarloService:
    """Service for Monte Carlo retirement simulations."""

    def __init__(self, db: AsyncSession):
        """Initialize Monte Carlo service."""
        self.db = db

    async def run_monte_carlo_retirement(
        self,
        user_id: UUID,
        starting_pot: Decimal,
        retirement_age: int,
        life_expectancy: int,
        target_annual_income: Decimal,
        mean_return: Decimal = Decimal('6.00'),
        return_volatility: Decimal = Decimal('15.00'),
        mean_inflation: Decimal = Decimal('2.50'),
        inflation_volatility: Decimal = Decimal('1.00'),
        simulations: int = 10000
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for retirement planning.

        Args:
            user_id: User UUID
            starting_pot: Starting pension pot value
            retirement_age: Age when retirement starts
            life_expectancy: Expected life expectancy
            target_annual_income: Target annual retirement income
            mean_return: Mean annual investment return (%)
            return_volatility: Return volatility/std dev (%)
            mean_inflation: Mean annual inflation rate (%)
            inflation_volatility: Inflation volatility (%)
            simulations: Number of simulations to run (1000-50000)

        Returns:
            Dict with:
            - simulations_run
            - probability_of_success
            - safe_withdrawal_rate
            - percentiles (10th, 25th, 50th, 75th, 90th)
            - confidence_intervals
            - worst_case, best_case, expected_value
        """
        logger.info(f"Running {simulations} Monte Carlo simulations for user {user_id}")

        if simulations < 1000 or simulations > 50000:
            raise ValueError("Simulations must be between 1000 and 50000")

        years_in_retirement = life_expectancy - retirement_age
        if years_in_retirement <= 0:
            raise ValueError("Life expectancy must be after retirement age")

        # Convert Decimal to float for numpy
        starting_pot_float = float(starting_pot)
        target_income_float = float(target_annual_income)
        mean_return_float = float(mean_return) / 100.0
        return_vol_float = float(return_volatility) / 100.0
        mean_inflation_float = float(mean_inflation) / 100.0
        inflation_vol_float = float(inflation_volatility) / 100.0

        # Run simulations
        final_pot_values = []
        success_count = 0

        np.random.seed(42)  # For reproducibility in tests

        for _ in range(simulations):
            pot = starting_pot_float
            annual_withdrawal = target_income_float

            for year in range(years_in_retirement):
                # Generate random return and inflation
                annual_return = np.random.normal(mean_return_float, return_vol_float)
                annual_inflation = np.random.normal(mean_inflation_float, inflation_vol_float)

                # Apply return
                pot = pot * (1 + annual_return)

                # Withdraw with inflation adjustment
                annual_withdrawal = annual_withdrawal * (1 + annual_inflation)
                pot = pot - annual_withdrawal

                # Check if pot depleted
                if pot <= 0:
                    break

            # Record final pot value (or 0 if depleted)
            final_pot_values.append(max(0, pot))

            # Count as success if pot lasted entire retirement
            if pot > 0:
                success_count += 1

        # Calculate probability of success
        probability_of_success = (success_count / simulations) * 100.0

        # Calculate percentiles
        percentiles = np.percentile(final_pot_values, [10, 25, 50, 75, 90])

        # Calculate safe withdrawal rate (rate that gives 90% success probability)
        safe_withdrawal_rate = await self._calculate_safe_withdrawal_rate(
            starting_pot_float,
            retirement_age,
            life_expectancy,
            mean_return_float,
            return_vol_float,
            mean_inflation_float,
            inflation_vol_float,
            simulations
        )

        # Calculate confidence intervals (95%)
        confidence_95 = np.percentile(final_pot_values, [2.5, 97.5])

        return {
            'simulations_run': simulations,
            'probability_of_success': float(Decimal(str(probability_of_success))),
            'safe_withdrawal_rate': float(safe_withdrawal_rate),
            'percentiles': {
                'p10': float(Decimal(str(percentiles[0]))),
                'p25': float(Decimal(str(percentiles[1]))),
                'p50': float(Decimal(str(percentiles[2]))),  # Median
                'p75': float(Decimal(str(percentiles[3]))),
                'p90': float(Decimal(str(percentiles[4]))),
            },
            'confidence_intervals': {
                'net_worth': {
                    'lower_95': float(Decimal(str(confidence_95[0]))),
                    'upper_95': float(Decimal(str(confidence_95[1])))
                }
            },
            'worst_case': float(Decimal(str(min(final_pot_values)))),
            'best_case': float(Decimal(str(max(final_pot_values)))),
            'expected_value': float(Decimal(str(np.mean(final_pot_values))))
        }

    async def calculate_safe_withdrawal_rate(
        self,
        user_id: UUID,
        starting_pot: Decimal,
        retirement_age: int,
        life_expectancy: int,
        mean_return: Decimal = Decimal('6.00'),
        return_volatility: Decimal = Decimal('15.00'),
        mean_inflation: Decimal = Decimal('2.50'),
        inflation_volatility: Decimal = Decimal('1.00'),
        simulations: int = 10000,
        target_probability: Decimal = Decimal('90.00')
    ) -> Decimal:
        """
        Calculate safe withdrawal rate with target success probability.

        Args:
            user_id: User UUID
            starting_pot: Starting pension pot value
            retirement_age: Age when retirement starts
            life_expectancy: Expected life expectancy
            mean_return: Mean annual investment return (%)
            return_volatility: Return volatility (%)
            mean_inflation: Mean annual inflation rate (%)
            inflation_volatility: Inflation volatility (%)
            simulations: Number of simulations
            target_probability: Target success probability (%)

        Returns:
            Safe withdrawal rate as percentage
        """
        logger.info(f"Calculating safe withdrawal rate for user {user_id}")

        starting_pot_float = float(starting_pot)
        mean_return_float = float(mean_return) / 100.0
        return_vol_float = float(return_volatility) / 100.0
        mean_inflation_float = float(mean_inflation) / 100.0
        inflation_vol_float = float(inflation_volatility) / 100.0

        safe_rate = await self._calculate_safe_withdrawal_rate(
            starting_pot_float,
            retirement_age,
            life_expectancy,
            mean_return_float,
            return_vol_float,
            mean_inflation_float,
            inflation_vol_float,
            simulations,
            float(target_probability) / 100.0
        )

        return Decimal(str(safe_rate))

    async def _calculate_safe_withdrawal_rate(
        self,
        starting_pot: float,
        retirement_age: int,
        life_expectancy: int,
        mean_return: float,
        return_volatility: float,
        mean_inflation: float,
        inflation_volatility: float,
        simulations: int,
        target_probability: float = 0.90
    ) -> float:
        """
        Binary search for safe withdrawal rate.

        Returns:
            Safe withdrawal rate as decimal (e.g., 0.04 for 4%)
        """
        years_in_retirement = life_expectancy - retirement_age

        # Binary search for rate
        low_rate = 0.01  # 1%
        high_rate = 0.10  # 10%
        tolerance = 0.001  # 0.1%

        while high_rate - low_rate > tolerance:
            test_rate = (low_rate + high_rate) / 2.0
            annual_withdrawal = starting_pot * test_rate

            # Run simulations with this rate
            success_count = 0
            np.random.seed(42)

            for _ in range(simulations):
                pot = starting_pot
                withdrawal = annual_withdrawal

                for year in range(years_in_retirement):
                    annual_return = np.random.normal(mean_return, return_volatility)
                    annual_inflation = np.random.normal(mean_inflation, inflation_volatility)

                    pot = pot * (1 + annual_return)
                    withdrawal = withdrawal * (1 + annual_inflation)
                    pot = pot - withdrawal

                    if pot <= 0:
                        break

                if pot > 0:
                    success_count += 1

            success_probability = success_count / simulations

            if success_probability >= target_probability:
                low_rate = test_rate
            else:
                high_rate = test_rate

        safe_rate = (low_rate + high_rate) / 2.0
        return safe_rate * 100.0  # Return as percentage
