"""
Scenarios API Endpoints

Provides REST API for scenario analysis:
- POST /api/v1/scenarios - Create scenario
- GET /api/v1/scenarios - List scenarios
- GET /api/v1/scenarios/{id} - Get scenario
- PUT /api/v1/scenarios/{id} - Update scenario
- DELETE /api/v1/scenarios/{id} - Delete scenario
- POST /api/v1/scenarios/{id}/run - Run scenario
- POST /api/v1/scenarios/compare - Compare scenarios
- POST /api/v1/scenarios/retirement-age - Model retirement age
- POST /api/v1/scenarios/career-change - Model career change
- POST /api/v1/scenarios/property-purchase - Model property purchase
- POST /api/v1/scenarios/monte-carlo - Run Monte Carlo simulation

All endpoints require authentication.
"""

import logging
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth import get_current_user
from models.user import User
from models.scenario import ScenarioType, ScenarioStatus
from schemas.scenario import (
    ScenarioCreate, ScenarioUpdate, ScenarioResponse,
    ScenarioExecutionRequest, ScenarioResultResponse,
    ScenarioComparisonRequest, ScenarioComparisonResponse,
    RetirementAgeScenarioRequest, RetirementAgeScenarioResponse,
    CareerChangeScenarioRequest, CareerChangeScenarioResponse,
    PropertyScenarioRequest, PropertyScenarioResponse,
    MonteCarloRequest, MonteCarloResponse
)
from services.scenarios import (
    ScenarioService, RetirementAgeScenarioService,
    CareerChangeScenarioService, PropertyScenarioService,
    MonteCarloService
)

router = APIRouter(prefix="/scenarios", tags=["scenarios"])
logger = logging.getLogger(__name__)


@router.post("", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    scenario_data: ScenarioCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new financial scenario.

    Requires:
    - scenario_name: Name for the scenario
    - scenario_type: Type of scenario
    - assumptions: List of assumptions

    Returns:
    - Created scenario with ID
    """
    try:
        service = ScenarioService(db)

        scenario_dict = scenario_data.model_dump()
        scenario = await service.create_scenario(current_user.id, scenario_dict)

        return ScenarioResponse.model_validate(scenario)

    except Exception as e:
        logger.error(f"Error creating scenario: {str(e)}")
        if "maximum" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create scenario")


@router.get("", response_model=List[ScenarioResponse])
async def list_scenarios(
    status_filter: Optional[ScenarioStatus] = None,
    include_expired: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all scenarios for the current user.

    Query parameters:
    - status: Filter by status (DRAFT, CALCULATED, ARCHIVED)
    - include_expired: Include expired scenarios

    Returns:
    - List of scenarios
    """
    try:
        service = ScenarioService(db)
        scenarios = await service.list_scenarios(current_user.id, status_filter, include_expired)

        return [ScenarioResponse.model_validate(s) for s in scenarios]

    except Exception as e:
        logger.error(f"Error listing scenarios: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list scenarios")


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific scenario by ID.

    Returns:
    - Scenario details with assumptions and results
    """
    try:
        service = ScenarioService(db)
        scenario = await service.get_scenario(scenario_id, current_user.id)

        return ScenarioResponse.model_validate(scenario)

    except Exception as e:
        logger.error(f"Error getting scenario: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "permission" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get scenario")


@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: UUID,
    update_data: ScenarioUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a scenario.

    Allowed updates:
    - scenario_name
    - description
    - status
    - assumptions

    Returns:
    - Updated scenario
    """
    try:
        service = ScenarioService(db)

        update_dict = update_data.model_dump(exclude_unset=True)
        scenario = await service.update_scenario(scenario_id, current_user.id, update_dict)

        return ScenarioResponse.model_validate(scenario)

    except Exception as e:
        logger.error(f"Error updating scenario: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "permission" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update scenario")


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(
    scenario_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete (archive) a scenario.

    Returns:
    - 204 No Content on success
    """
    try:
        service = ScenarioService(db)
        await service.delete_scenario(scenario_id, current_user.id)

        return None

    except Exception as e:
        logger.error(f"Error deleting scenario: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "permission" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete scenario")


@router.post("/{scenario_id}/run", response_model=ScenarioResultResponse)
async def run_scenario(
    scenario_id: UUID,
    execution_params: ScenarioExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute scenario calculations.

    Parameters:
    - projection_years: Number of years to project (1-30)
    - growth_rate: Investment growth rate (%)
    - inflation_rate: Inflation rate (%)
    - include_monte_carlo: Run Monte Carlo simulation
    - monte_carlo_simulations: Number of simulations

    Returns:
    - Scenario results with projections
    """
    try:
        service = ScenarioService(db)

        execution_dict = execution_params.model_dump()
        result = await service.run_scenario(scenario_id, current_user.id, execution_dict)

        return ScenarioResultResponse.model_validate(result)

    except Exception as e:
        logger.error(f"Error running scenario: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "permission" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to run scenario")


@router.post("/compare", response_model=ScenarioComparisonResponse)
async def compare_scenarios(
    comparison_request: ScenarioComparisonRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare multiple scenarios side-by-side.

    Parameters:
    - scenario_ids: List of 2-5 scenario IDs

    Returns:
    - Comparison with metrics, trade-offs, and recommendations
    """
    try:
        service = ScenarioService(db)

        comparison = await service.compare_scenarios(comparison_request.scenario_ids, current_user.id)

        return comparison

    except Exception as e:
        logger.error(f"Error comparing scenarios: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "validation" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to compare scenarios")


@router.post("/retirement-age", response_model=RetirementAgeScenarioResponse)
async def model_retirement_age(
    request: RetirementAgeScenarioRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Model a specific retirement age scenario.

    Parameters:
    - retirement_age: Target retirement age (55-70)
    - current_pension_pot: Current pension value (optional)
    - annual_contributions: Annual contributions (optional)

    Returns:
    - Retirement age scenario results
    """
    try:
        service = RetirementAgeScenarioService(db)

        # Get user age (simplified - would get from user profile)
        current_age = 35  # Placeholder

        result = await service.model_retirement_age(
            current_user.id,
            request.retirement_age,
            current_age,
            request.current_pension_pot or Decimal('0'),
            request.annual_contributions or Decimal('0')
        )

        return result

    except Exception as e:
        logger.error(f"Error modeling retirement age: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/career-change", response_model=CareerChangeScenarioResponse)
async def model_career_change(
    request: CareerChangeScenarioRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Model career change financial impact.

    Parameters:
    - new_salary: New annual salary
    - change_date: Date of change
    - salary_increase_rate: Annual increase rate (%)

    Returns:
    - Career change impact analysis
    """
    try:
        service = CareerChangeScenarioService(db)

        # Get current salary (simplified - would get from user income records)
        current_salary = Decimal('50000')  # Placeholder
        current_age = 35  # Placeholder

        result = await service.model_career_change(
            current_user.id,
            current_salary,
            request.new_salary,
            request.change_date,
            current_age
        )

        return result

    except Exception as e:
        logger.error(f"Error modeling career change: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/property-purchase", response_model=PropertyScenarioResponse)
async def model_property_purchase(
    request: PropertyScenarioRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Model property purchase scenario.

    Parameters:
    - property_value: Purchase price
    - deposit: Deposit amount
    - mortgage_rate: Interest rate (%)
    - mortgage_term_years: Term in years

    Returns:
    - Property purchase analysis with affordability
    """
    try:
        service = PropertyScenarioService(db)

        # Get annual income (simplified - would get from user income records)
        annual_income = Decimal('50000')  # Placeholder

        result = await service.model_property_purchase(
            current_user.id,
            request.property_value,
            request.deposit,
            request.mortgage_rate,
            request.mortgage_term_years,
            annual_income,
            request.stamp_duty
        )

        return result

    except Exception as e:
        logger.error(f"Error modeling property purchase: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/monte-carlo", response_model=MonteCarloResponse)
async def run_monte_carlo(
    request: MonteCarloRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Run Monte Carlo simulation for retirement planning.

    Parameters:
    - simulations: Number of simulations (1000-50000)
    - mean_return: Mean investment return (%)
    - volatility: Return volatility (%)
    - retirement_age: Target retirement age
    - target_income: Target annual income

    Returns:
    - Monte Carlo results with probability distributions
    """
    try:
        service = MonteCarloService(db)

        # Get pension pot (simplified - would get from retirement accounts)
        starting_pot = Decimal('100000')  # Placeholder
        life_expectancy = 90  # Placeholder

        result = await service.run_monte_carlo_retirement(
            current_user.id,
            starting_pot,
            request.retirement_age,
            life_expectancy,
            request.target_income,
            request.mean_return,
            request.volatility,
            request.mean_inflation,
            request.inflation_volatility,
            request.simulations
        )

        return result

    except Exception as e:
        logger.error(f"Error running Monte Carlo: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
