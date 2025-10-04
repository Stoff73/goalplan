"""
Tests for SA Retirement Fund models.

Tests cover:
- SARetirementFund model creation and validation
- SAFundContribution model with temporal data
- SARetirementDeductionLimits model
- Fund number encryption/decryption
- Projected value calculations
- Tax deduction calculations
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import select

from models.retirement import (
    SARetirementFund, SAFundContribution, SARetirementDeductionLimits,
    SAFundType, SAFundStatus, InvestmentStrategy
)
from models.user import User, UserStatus


@pytest.mark.asyncio
async def test_create_sa_retirement_fund(db_session):
    """Test creating an SA retirement fund with encryption."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash="hashed",
        status=UserStatus.ACTIVE
    )
    db_session.add(user)
    await db_session.commit()

    # Create SA retirement fund
    fund = SARetirementFund(
        user_id=user.id,
        fund_type=SAFundType.PENSION_FUND,
        provider="Old Mutual",
        fund_name="Old Mutual Pension Fund",
        employer_name="Test Company",
        current_value=Decimal('500000.00'),
        start_date=date(2020, 1, 1),
        retirement_age=65,
        investment_strategy=InvestmentStrategy.BALANCED,
        assumed_growth_rate=Decimal('8.00'),
        status=SAFundStatus.ACTIVE
    )

    # Set encrypted fund number
    fund.set_fund_number("PF123456789")

    db_session.add(fund)
    await db_session.commit()
    await db_session.refresh(fund)

    # Assertions
    assert fund.id is not None
    assert fund.user_id == user.id
    assert fund.fund_type == SAFundType.PENSION_FUND
    assert fund.provider == "Old Mutual"
    assert fund.current_value == Decimal('500000.00')
    assert fund.get_fund_number() == "PF123456789"  # Decrypt works
    assert fund.status == SAFundStatus.ACTIVE


@pytest.mark.asyncio
async def test_sa_fund_contribution(db_session):
    """Test creating SA fund contribution with temporal data."""
    # Create user and fund
    user = User(
        email="test@example.com",
        password_hash="hashed",
        status=UserStatus.ACTIVE
    )
    db_session.add(user)

    fund = SARetirementFund(
        user_id=user.id,
        fund_type=SAFundType.RETIREMENT_ANNUITY,
        provider="Allan Gray",
        fund_name="Allan Gray RA",
        current_value=Decimal('300000.00'),
        start_date=date(2022, 1, 1),
        retirement_age=65
    )
    fund.set_fund_number("RA987654321")

    db_session.add(fund)
    await db_session.commit()

    # Create contribution
    contribution = SAFundContribution(
        fund_id=fund.id,
        employee_contribution=Decimal('3000.00'),
        employer_contribution=Decimal('0.00'),
        contribution_date=date(2024, 6, 1),
        tax_year="2024/2025",
        tax_deduction_claimed=Decimal('3000.00'),
        effective_from=date(2024, 6, 1),
        effective_to=None
    )

    db_session.add(contribution)
    await db_session.commit()
    await db_session.refresh(contribution)

    # Assertions
    assert contribution.id is not None
    assert contribution.fund_id == fund.id
    assert contribution.total_contribution == Decimal('3000.00')
    assert contribution.tax_year == "2024/2025"
    assert contribution.effective_to is None  # Current contribution


@pytest.mark.asyncio
async def test_sa_deduction_limits(db_session):
    """Test SA Section 10C deduction limits tracking."""
    # Create user
    user = User(
        email="test@example.com",
        password_hash="hashed",
        status=UserStatus.ACTIVE
    )
    db_session.add(user)
    await db_session.commit()

    # Create deduction limits
    limits = SARetirementDeductionLimits(
        user_id=user.id,
        tax_year="2024/2025",
        annual_deduction_limit=Decimal('275000.00'),  # 27.5% of R1M income
        deductions_claimed=Decimal('150000.00'),
        deductions_remaining=Decimal('125000.00')
    )

    db_session.add(limits)
    await db_session.commit()
    await db_session.refresh(limits)

    # Assertions
    assert limits.id is not None
    assert limits.tax_year == "2024/2025"
    assert limits.annual_deduction_limit == Decimal('275000.00')
    assert limits.deductions_claimed == Decimal('150000.00')
    assert limits.deductions_remaining == Decimal('125000.00')
    assert limits.calculate_excess() == Decimal('0.00')


@pytest.mark.asyncio
async def test_sa_deduction_limits_excess(db_session):
    """Test SA deduction limits with excess contributions."""
    user = User(
        email="test@example.com",
        password_hash="hashed",
        status=UserStatus.ACTIVE
    )
    db_session.add(user)
    await db_session.commit()

    # Create limits with excess
    limits = SARetirementDeductionLimits(
        user_id=user.id,
        tax_year="2024/2025",
        annual_deduction_limit=Decimal('350000.00'),  # Max limit
        deductions_claimed=Decimal('400000.00'),  # Excess!
        deductions_remaining=Decimal('0.00')
    )

    db_session.add(limits)
    await db_session.commit()

    # Assertions
    assert limits.calculate_excess() == Decimal('50000.00')


@pytest.mark.asyncio
async def test_sa_fund_projected_value(db_session):
    """Test projected value calculation."""
    user = User(
        email="test@example.com",
        password_hash="hashed",
        status=UserStatus.ACTIVE
    )
    db_session.add(user)

    fund = SARetirementFund(
        user_id=user.id,
        fund_type=SAFundType.PROVIDENT_FUND,
        provider="Sanlam",
        fund_name="Sanlam Provident Fund",
        current_value=Decimal('500000.00'),
        start_date=date(2024, 1, 1),
        retirement_age=65,
        assumed_growth_rate=Decimal('8.00')
    )
    fund.set_fund_number("PV111222333")

    db_session.add(fund)
    await db_session.commit()

    # Calculate projection
    projected = fund.calculate_projected_value(target_age=65)

    # Assertions
    assert projected > fund.current_value  # Should grow
    assert isinstance(projected, Decimal)


@pytest.mark.asyncio
async def test_sa_fund_validation_retirement_age(db_session):
    """Test retirement age validation."""
    user = User(
        email="test@example.com",
        password_hash="hashed",
        status=UserStatus.ACTIVE
    )
    db_session.add(user)
    await db_session.commit()

    # This will fail constraint check on commit
    fund = SARetirementFund(
        user_id=user.id,
        fund_type=SAFundType.PENSION_FUND,
        provider="Test Provider",
        fund_name="Test Fund",
        current_value=Decimal('100000.00'),
        start_date=date(2024, 1, 1),
        retirement_age=50  # Too young!
    )
    fund.set_fund_number("TEST123")

    db_session.add(fund)

    with pytest.raises(Exception):  # Will raise DB constraint violation
        await db_session.commit()
