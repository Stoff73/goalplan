"""
Tests for RetirementAgeScenarioService and MonteCarloService.

Tests:
- Retirement age modeling
- Retirement age optimization
- Monte Carlo simulations
- Safe withdrawal rate calculation
"""

import pytest
from decimal import Decimal

from services.scenarios import RetirementAgeScenarioService, MonteCarloService


@pytest.mark.asyncio
async def test_model_retirement_age(db_session, test_user):
    """Test modeling a specific retirement age."""
    service = RetirementAgeScenarioService(db_session)

    result = await service.model_retirement_age(
        user_id=test_user.id,
        retirement_age=65,
        current_age=35,
        current_pension_pot=Decimal('50000.00'),
        annual_contributions=Decimal('5000.00'),
        growth_rate=Decimal('6.00'),
        life_expectancy=90
    )

    assert result['retirement_age'] == 65
    assert result['years_to_retirement'] == 30
    assert result['pension_pot_at_retirement'] > 0
    assert result['annual_retirement_income'] > 0
    assert result['monthly_retirement_income'] > 0
    assert 'pot_depletion_age' in result
    assert 'replacement_ratio' in result


@pytest.mark.asyncio
async def test_model_retirement_age_early(db_session, test_user):
    """Test modeling early retirement (age 60)."""
    service = RetirementAgeScenarioService(db_session)

    result_60 = await service.model_retirement_age(
        user_id=test_user.id,
        retirement_age=60,
        current_age=35,
        current_pension_pot=Decimal('50000.00'),
        annual_contributions=Decimal('5000.00'),
        growth_rate=Decimal('6.00'),
        life_expectancy=90
    )

    result_65 = await service.model_retirement_age(
        user_id=test_user.id,
        retirement_age=65,
        current_age=35,
        current_pension_pot=Decimal('50000.00'),
        annual_contributions=Decimal('5000.00'),
        growth_rate=Decimal('6.00'),
        life_expectancy=90
    )

    # Early retirement should have smaller pot
    assert result_60['pension_pot_at_retirement'] < result_65['pension_pot_at_retirement']


@pytest.mark.asyncio
async def test_optimize_retirement_age(db_session, test_user):
    """Test optimizing retirement age for target income."""
    service = RetirementAgeScenarioService(db_session)

    result = await service.optimize_retirement_age(
        user_id=test_user.id,
        current_age=35,
        current_pension_pot=Decimal('50000.00'),
        annual_contributions=Decimal('5000.00'),
        target_income=Decimal('25000.00'),
        growth_rate=Decimal('6.00')
    )

    assert 'optimal_retirement_age' in result
    assert result['optimal_retirement_age'] is not None
    assert result['optimal_retirement_age'] >= 55
    assert result['optimal_retirement_age'] <= 70
    assert 'pension_pot_needed' in result
    assert 'reasoning' in result


@pytest.mark.asyncio
async def test_retirement_age_invalid_inputs(db_session, test_user):
    """Test validation of retirement age inputs."""
    service = RetirementAgeScenarioService(db_session)

    # Test age too low
    with pytest.raises(ValueError):
        await service.model_retirement_age(
            user_id=test_user.id,
            retirement_age=50,  # Too low
            current_age=35,
            current_pension_pot=Decimal('50000.00'),
            annual_contributions=Decimal('5000.00')
        )

    # Test age too high
    with pytest.raises(ValueError):
        await service.model_retirement_age(
            user_id=test_user.id,
            retirement_age=75,  # Too high
            current_age=35,
            current_pension_pot=Decimal('50000.00'),
            annual_contributions=Decimal('5000.00')
        )

    # Test retirement in past
    with pytest.raises(ValueError):
        await service.model_retirement_age(
            user_id=test_user.id,
            retirement_age=30,  # Before current age
            current_age=35,
            current_pension_pot=Decimal('50000.00'),
            annual_contributions=Decimal('5000.00')
        )


@pytest.mark.asyncio
async def test_monte_carlo_simulation(db_session, test_user):
    """Test Monte Carlo retirement simulation."""
    service = MonteCarloService(db_session)

    result = await service.run_monte_carlo_retirement(
        user_id=test_user.id,
        starting_pot=Decimal('500000.00'),
        retirement_age=65,
        life_expectancy=90,
        target_annual_income=Decimal('25000.00'),
        mean_return=Decimal('6.00'),
        return_volatility=Decimal('15.00'),
        mean_inflation=Decimal('2.50'),
        inflation_volatility=Decimal('1.00'),
        simulations=1000  # Fewer for faster tests
    )

    assert result['simulations_run'] == 1000
    assert 'probability_of_success' in result
    assert result['probability_of_success'] >= 0
    assert result['probability_of_success'] <= 100
    assert 'safe_withdrawal_rate' in result
    assert 'percentiles' in result
    assert 'p10' in result['percentiles']
    assert 'p25' in result['percentiles']
    assert 'p50' in result['percentiles']
    assert 'p75' in result['percentiles']
    assert 'p90' in result['percentiles']
    assert 'worst_case' in result
    assert 'best_case' in result
    assert 'expected_value' in result


@pytest.mark.asyncio
async def test_monte_carlo_higher_success_with_higher_pot(db_session, test_user):
    """Test that higher pot gives higher success probability."""
    service = MonteCarloService(db_session)

    # Simulation with lower pot
    result_low = await service.run_monte_carlo_retirement(
        user_id=test_user.id,
        starting_pot=Decimal('300000.00'),
        retirement_age=65,
        life_expectancy=90,
        target_annual_income=Decimal('25000.00'),
        simulations=1000
    )

    # Simulation with higher pot
    result_high = await service.run_monte_carlo_retirement(
        user_id=test_user.id,
        starting_pot=Decimal('700000.00'),
        retirement_age=65,
        life_expectancy=90,
        target_annual_income=Decimal('25000.00'),
        simulations=1000
    )

    # Higher pot should have higher success probability
    assert result_high['probability_of_success'] > result_low['probability_of_success']


@pytest.mark.asyncio
async def test_safe_withdrawal_rate(db_session, test_user):
    """Test safe withdrawal rate calculation."""
    service = MonteCarloService(db_session)

    safe_rate = await service.calculate_safe_withdrawal_rate(
        user_id=test_user.id,
        starting_pot=Decimal('500000.00'),
        retirement_age=65,
        life_expectancy=90,
        mean_return=Decimal('6.00'),
        return_volatility=Decimal('15.00'),
        mean_inflation=Decimal('2.50'),
        inflation_volatility=Decimal('1.00'),
        simulations=1000,
        target_probability=Decimal('90.00')
    )

    assert safe_rate is not None
    assert safe_rate > Decimal('0')
    assert safe_rate < Decimal('10')  # Should be reasonable (< 10%)


@pytest.mark.asyncio
async def test_monte_carlo_invalid_inputs(db_session, test_user):
    """Test Monte Carlo validation."""
    service = MonteCarloService(db_session)

    # Test too few simulations
    with pytest.raises(ValueError):
        await service.run_monte_carlo_retirement(
            user_id=test_user.id,
            starting_pot=Decimal('500000.00'),
            retirement_age=65,
            life_expectancy=90,
            target_annual_income=Decimal('25000.00'),
            simulations=500  # Too few
        )

    # Test too many simulations
    with pytest.raises(ValueError):
        await service.run_monte_carlo_retirement(
            user_id=test_user.id,
            starting_pot=Decimal('500000.00'),
            retirement_age=65,
            life_expectancy=90,
            target_annual_income=Decimal('25000.00'),
            simulations=60000  # Too many
        )

    # Test invalid life expectancy
    with pytest.raises(ValueError):
        await service.run_monte_carlo_retirement(
            user_id=test_user.id,
            starting_pot=Decimal('500000.00'),
            retirement_age=70,
            life_expectancy=65,  # Before retirement
            target_annual_income=Decimal('25000.00'),
            simulations=1000
        )
