"""
Tests for income tracking models.

Tests cover:
- UserIncome model creation and validation
- IncomeTaxWithholding model
- ExchangeRate model
- Relationships and constraints
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.income import UserIncome, IncomeTaxWithholding, ExchangeRate, IncomeType, Currency, IncomeFrequency
from models.user import User


@pytest.mark.asyncio
async def test_create_income_record(db_session: AsyncSession, test_user: User):
    """Test creating a basic income record."""
    income = UserIncome(
        user_id=test_user.id,
        income_type=IncomeType.EMPLOYMENT,
        source_country='UK',
        description='Software Engineer Salary',
        employer_name='Tech Corp Ltd',
        amount=Decimal('65000.00'),
        currency=Currency.GBP,
        frequency=IncomeFrequency.ANNUAL,
        tax_year_uk='2023/24',
        tax_year_sa='2023/24',
        income_date=date(2023, 5, 1),
        is_gross=True,
    )

    db_session.add(income)
    await db_session.commit()
    await db_session.refresh(income)

    assert income.id is not None
    assert income.user_id == test_user.id
    assert income.income_type == IncomeType.EMPLOYMENT
    assert income.amount == Decimal('65000.00')
    assert income.currency == Currency.GBP
    assert income.deleted_at is None


@pytest.mark.asyncio
async def test_income_with_currency_conversion(db_session: AsyncSession, test_user: User):
    """Test income record with currency conversion fields."""
    income = UserIncome(
        user_id=test_user.id,
        income_type=IncomeType.RENTAL,
        source_country='ZA',
        description='Cape Town Rental Property',
        amount=Decimal('15000.00'),
        currency=Currency.ZAR,
        amount_in_gbp=Decimal('750.00'),
        amount_in_zar=Decimal('15000.00'),
        exchange_rate=Decimal('20.0000'),
        exchange_rate_date=date(2023, 5, 1),
        frequency=IncomeFrequency.MONTHLY,
        tax_year_uk='2023/24',
        tax_year_sa='2023/24',
        income_date=date(2023, 5, 1),
        is_gross=True,
    )

    db_session.add(income)
    await db_session.commit()
    await db_session.refresh(income)

    assert income.amount_in_gbp == Decimal('750.00')
    assert income.amount_in_zar == Decimal('15000.00')
    assert income.exchange_rate == Decimal('20.0000')
    assert income.exchange_rate_date == date(2023, 5, 1)


@pytest.mark.asyncio
async def test_income_foreign_with_dta(db_session: AsyncSession, test_user: User):
    """Test foreign income with DTA flags."""
    income = UserIncome(
        user_id=test_user.id,
        income_type=IncomeType.INVESTMENT,
        source_country='US',
        description='US Dividend Income',
        amount=Decimal('5000.00'),
        currency=Currency.USD,
        frequency=IncomeFrequency.ANNUAL,
        tax_year_uk='2023/24',
        tax_year_sa='2023/24',
        income_date=date(2023, 6, 15),
        is_gross=True,
        is_foreign_income=True,
        foreign_tax_credit=Decimal('750.00'),
        dta_applicable=True,
    )

    db_session.add(income)
    await db_session.commit()
    await db_session.refresh(income)

    assert income.is_foreign_income is True
    assert income.foreign_tax_credit == Decimal('750.00')
    assert income.dta_applicable is True


@pytest.mark.asyncio
async def test_income_with_tax_withholding(db_session: AsyncSession, test_user: User):
    """Test income with tax withholding details."""
    income = UserIncome(
        user_id=test_user.id,
        income_type=IncomeType.EMPLOYMENT,
        source_country='UK',
        amount=Decimal('65000.00'),
        currency=Currency.GBP,
        frequency=IncomeFrequency.ANNUAL,
        tax_year_uk='2023/24',
        tax_year_sa='2023/24',
        income_date=date(2023, 5, 1),
        is_gross=True,
        tax_withheld_amount=Decimal('12000.00'),
        tax_withheld_currency=Currency.GBP,
    )

    db_session.add(income)
    await db_session.commit()
    await db_session.refresh(income)

    # Create PAYE withholding details
    withholding = IncomeTaxWithholding(
        income_id=income.id,
        paye_income_tax=Decimal('10000.00'),
        paye_ni_class1=Decimal('2000.00'),
        paye_tax_code='1257L',
    )

    db_session.add(withholding)
    await db_session.commit()
    await db_session.refresh(withholding)

    assert withholding.id is not None
    assert withholding.income_id == income.id
    assert withholding.paye_income_tax == Decimal('10000.00')
    assert withholding.paye_ni_class1 == Decimal('2000.00')
    assert withholding.paye_tax_code == '1257L'


@pytest.mark.asyncio
async def test_income_soft_delete(db_session: AsyncSession, test_user: User):
    """Test soft delete of income record."""
    income = UserIncome(
        user_id=test_user.id,
        income_type=IncomeType.OTHER,
        source_country='UK',
        amount=Decimal('1000.00'),
        currency=Currency.GBP,
        frequency=IncomeFrequency.ONE_TIME,
        tax_year_uk='2023/24',
        tax_year_sa='2023/24',
        income_date=date(2023, 5, 1),
        is_gross=True,
    )

    db_session.add(income)
    await db_session.commit()
    await db_session.refresh(income)

    income_id = income.id

    # Soft delete
    income.deleted_at = datetime.utcnow()
    await db_session.commit()

    # Verify record still exists but is marked deleted
    stmt = select(UserIncome).where(UserIncome.id == income_id)
    result = await db_session.execute(stmt)
    deleted_income = result.scalar_one_or_none()

    assert deleted_income is not None
    assert deleted_income.deleted_at is not None


@pytest.mark.asyncio
async def test_exchange_rate_creation(db_session: AsyncSession):
    """Test creating exchange rate record."""
    rate = ExchangeRate(
        from_currency='GBP',
        to_currency='ZAR',
        rate=Decimal('23.6500'),
        rate_date=date(2023, 10, 1),
        source='exchangerate-api',
    )

    db_session.add(rate)
    await db_session.commit()
    await db_session.refresh(rate)

    assert rate.id is not None
    assert rate.from_currency == 'GBP'
    assert rate.to_currency == 'ZAR'
    assert rate.rate == Decimal('23.6500')
    assert rate.rate_date == date(2023, 10, 1)


@pytest.mark.asyncio
async def test_exchange_rate_unique_constraint(db_session: AsyncSession):
    """Test unique constraint on exchange rates (one rate per currency pair per day)."""
    rate1 = ExchangeRate(
        from_currency='GBP',
        to_currency='USD',
        rate=Decimal('1.2500'),
        rate_date=date(2023, 10, 1),
        source='exchangerate-api',
    )

    db_session.add(rate1)
    await db_session.commit()

    # Try to add duplicate rate for same currency pair and date
    rate2 = ExchangeRate(
        from_currency='GBP',
        to_currency='USD',
        rate=Decimal('1.2600'),
        rate_date=date(2023, 10, 1),
        source='another-api',
    )

    db_session.add(rate2)

    with pytest.raises(Exception):  # Should raise IntegrityError
        await db_session.commit()


@pytest.mark.asyncio
async def test_income_amount_positive_constraint(db_session: AsyncSession, test_user: User):
    """Test that income amount must be positive."""
    income = UserIncome(
        user_id=test_user.id,
        income_type=IncomeType.EMPLOYMENT,
        source_country='UK',
        amount=Decimal('-1000.00'),  # Negative amount
        currency=Currency.GBP,
        frequency=IncomeFrequency.ANNUAL,
        tax_year_uk='2023/24',
        tax_year_sa='2023/24',
        income_date=date(2023, 5, 1),
        is_gross=True,
    )

    db_session.add(income)

    with pytest.raises(Exception):  # Should raise CheckConstraint error
        await db_session.commit()


@pytest.mark.asyncio
async def test_income_relationship_with_user(db_session: AsyncSession, test_user: User):
    """Test relationship between income and user."""
    income1 = UserIncome(
        user_id=test_user.id,
        income_type=IncomeType.EMPLOYMENT,
        source_country='UK',
        amount=Decimal('50000.00'),
        currency=Currency.GBP,
        frequency=IncomeFrequency.ANNUAL,
        tax_year_uk='2023/24',
        tax_year_sa='2023/24',
        income_date=date(2023, 5, 1),
        is_gross=True,
    )

    income2 = UserIncome(
        user_id=test_user.id,
        income_type=IncomeType.RENTAL,
        source_country='UK',
        amount=Decimal('12000.00'),
        currency=Currency.GBP,
        frequency=IncomeFrequency.MONTHLY,
        tax_year_uk='2023/24',
        tax_year_sa='2023/24',
        income_date=date(2023, 5, 1),
        is_gross=True,
    )

    db_session.add(income1)
    db_session.add(income2)
    await db_session.commit()

    # Refresh user to load income_records relationship
    await db_session.refresh(test_user)

    # Note: In async SQLAlchemy, relationships may need explicit loading
    # For this test, we'll query the income records directly
    stmt = select(UserIncome).where(UserIncome.user_id == test_user.id)
    result = await db_session.execute(stmt)
    user_income_records = result.scalars().all()

    assert len(user_income_records) == 2


@pytest.mark.asyncio
async def test_multiple_income_types(db_session: AsyncSession, test_user: User):
    """Test creating income of different types."""
    income_types = [
        (IncomeType.EMPLOYMENT, 'Salary', Decimal('60000.00')),
        (IncomeType.SELF_EMPLOYMENT, 'Consulting', Decimal('15000.00')),
        (IncomeType.RENTAL, 'Property Rental', Decimal('12000.00')),
        (IncomeType.INVESTMENT, 'Dividends', Decimal('3000.00')),
        (IncomeType.PENSION, 'Pension Income', Decimal('8000.00')),
        (IncomeType.OTHER, 'Miscellaneous', Decimal('500.00')),
    ]

    for income_type, description, amount in income_types:
        income = UserIncome(
            user_id=test_user.id,
            income_type=income_type,
            source_country='UK',
            description=description,
            amount=amount,
            currency=Currency.GBP,
            frequency=IncomeFrequency.ANNUAL,
            tax_year_uk='2023/24',
            tax_year_sa='2023/24',
            income_date=date(2023, 5, 1),
            is_gross=True,
        )
        db_session.add(income)

    await db_session.commit()

    # Verify all income types created
    stmt = select(UserIncome).where(UserIncome.user_id == test_user.id)
    result = await db_session.execute(stmt)
    all_income = result.scalars().all()

    assert len(all_income) == 6
    created_types = {income.income_type for income in all_income}
    expected_types = {income_type for income_type, _, _ in income_types}
    assert created_types == expected_types
