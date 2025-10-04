"""
Tests for SA Retirement Service.

Tests cover:
- create_fund()
- add_contribution()
- calculate_tax_deduction()
- get_deduction_status()
- project_retirement_value()
"""

import pytest
from datetime import date
from decimal import Decimal

from services.retirement.sa_retirement_service import (
    SARetirementService, ValidationError, NotFoundError, PermissionError
)
from models.retirement import SAFundType, InvestmentStrategy
from models.user import User, UserStatus


@pytest.mark.asyncio
async def test_create_fund_success(db_session):
    """Test successful fund creation."""
    # Create user
    user = User(
        email="test@example.com",
        password_hash="hashed",
        status=UserStatus.ACTIVE
    )
    db_session.add(user)
    await db_session.commit()

    # Create service
    service = SARetirementService(db_session)

    # Fund data
    fund_data = {
        "fund_type": SAFundType.PENSION_FUND,
        "provider": "Old Mutual",
        "fund_name": "Old Mutual Pension",
        "fund_number": "PF123456",
        "employer_name": "Test Corp",
        "current_value": Decimal('500000.00'),
        "start_date": date(2020, 1, 1),
        "retirement_age": 65,
        "investment_strategy": InvestmentStrategy.BALANCED,
        "assumed_growth_rate": Decimal('8.00')
    }

    # Create fund
    fund = await service.create_fund(user.id, fund_data)

    # Assertions
    assert fund.id is not None
    assert fund.user_id == user.id
    assert fund.provider == "Old Mutual"
    assert fund.current_value == Decimal('500000.00')
    assert fund.get_fund_number() == "PF123456"


@pytest.mark.asyncio
async def test_calculate_tax_deduction(db_session):
    """Test Section 10C tax deduction calculation."""
    # Create user
    user = User(
        email="test@example.com",
        password_hash="hashed",
        status=UserStatus.ACTIVE
    )
    db_session.add(user)
    await db_session.commit()

    service = SARetirementService(db_session)

    # Calculate deduction: 27.5% of R1M = R275,000
    result = await service.calculate_tax_deduction(
        user_id=user.id,
        annual_income=Decimal('1000000.00'),
        tax_year="2024/2025"
    )

    # Assertions
    assert result['max_deductible'] == Decimal('275000.00')
    assert result['deductions_claimed'] == Decimal('0.00')
    assert result['deductions_remaining'] == Decimal('275000.00')


@pytest.mark.asyncio
async def test_calculate_tax_deduction_max_cap(db_session):
    """Test Section 10C deduction capped at R350,000."""
    user = User(
        email="test@example.com",
        password_hash="hashed",
        status=UserStatus.ACTIVE
    )
    db_session.add(user)
    await db_session.commit()

    service = SARetirementService(db_session)

    # Income is R2M, 27.5% = R550k, but capped at R350k
    result = await service.calculate_tax_deduction(
        user_id=user.id,
        annual_income=Decimal('2000000.00'),
        tax_year="2024/2025"
    )

    # Assertions
    assert result['max_deductible'] == Decimal('350000.00')  # Capped!


@pytest.mark.asyncio
async def test_add_contribution_success(db_session):
    """Test adding contribution to fund."""
    # Create user
    user = User(
        email="test@example.com",
        password_hash="hashed",
        status=UserStatus.ACTIVE
    )
    db_session.add(user)
    await db_session.commit()

    service = SARetirementService(db_session)

    # Create fund first
    fund_data = {
        "fund_type": SAFundType.RETIREMENT_ANNUITY,
        "provider": "Allan Gray",
        "fund_name": "Allan Gray RA",
        "fund_number": "RA987654",
        "current_value": Decimal('300000.00'),
        "start_date": date(2022, 1, 1),
        "retirement_age": 65
    }
    fund = await service.create_fund(user.id, fund_data)

    # Add contribution
    contribution_data = {
        "employee_contribution": Decimal('5000.00'),
        "employer_contribution": Decimal('0.00'),
        "contribution_date": date(2024, 6, 1),
        "tax_year": "2024/2025",
        "effective_from": date(2024, 6, 1),
        "effective_to": None
    }

    contribution = await service.add_contribution(
        fund_id=fund.id,
        user_id=user.id,
        contribution_data=contribution_data
    )

    # Assertions
    assert contribution.id is not None
    assert contribution.fund_id == fund.id
    assert contribution.total_contribution == Decimal('5000.00')
