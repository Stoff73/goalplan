"""
Tests for coverage calculation models.

This module tests:
- CoverageNeedsAnalysis model creation and validation
- Recommended cover calculation logic
- Coverage gap calculation
- Temporal data (effective_from/effective_to)
- get_current_analysis method
- PolicyPremiumReminder model creation
- Reminder relationships and cascade deletes
- Constraint violations
- Database indexes
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid

from sqlalchemy import select, func, inspect
from sqlalchemy.exc import IntegrityError

from models.life_assurance import (
    CoverageNeedsAnalysis,
    PolicyPremiumReminder,
    LifeAssurancePolicy,
    ReminderType,
    ProviderCountry,
    PolicyType,
    PremiumFrequency,
    PolicyStatus,
    Currency
)
from models.user import User, CountryPreference


@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    user = User(
        email=f"test_{uuid.uuid4()}@example.com",
        first_name="Test",
        last_name="User",
        country_preference=CountryPreference.BOTH,
        terms_accepted_at=datetime.utcnow(),
        email_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_policy(db_session, test_user):
    """Create a test life assurance policy."""
    policy = LifeAssurancePolicy(
        user_id=test_user.id,
        provider="Legal & General",
        provider_country=ProviderCountry.UK,
        policy_type=PolicyType.TERM,
        cover_amount=Decimal("500000.00"),
        currency=Currency.GBP,
        premium_amount=Decimal("50.00"),
        premium_frequency=PremiumFrequency.MONTHLY,
        start_date=date(2024, 1, 1),
        end_date=date(2044, 1, 1),
        written_in_trust=False,
        status=PolicyStatus.ACTIVE
    )
    policy.set_policy_number("POL123456")
    db_session.add(policy)
    await db_session.commit()
    await db_session.refresh(policy)
    return policy


@pytest.fixture
async def test_coverage_analysis(db_session, test_user):
    """Create a test coverage needs analysis."""
    analysis = CoverageNeedsAnalysis(
        user_id=test_user.id,
        calculation_date=date.today(),
        annual_income=Decimal("75000.00"),
        income_multiplier=Decimal("10.0"),
        outstanding_debts=Decimal("250000.00"),
        children_count=2,
        education_cost_per_child=Decimal("50000.00"),
        funeral_costs=Decimal("10000.00"),
        existing_assets=Decimal("100000.00"),
        recommended_cover=Decimal("960000.00"),  # Will be calculated
        current_total_cover=Decimal("500000.00"),
        coverage_gap=Decimal("460000.00"),  # Will be calculated
        effective_from=datetime.utcnow()
    )
    db_session.add(analysis)
    await db_session.commit()
    await db_session.refresh(analysis)
    return analysis


class TestCoverageNeedsAnalysis:
    """Test CoverageNeedsAnalysis model."""

    @pytest.mark.asyncio
    async def test_create_analysis_with_valid_data(self, db_session, test_user):
        """Test creating a coverage analysis with valid data."""
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date(2024, 10, 3),
            annual_income=Decimal("60000.00"),
            income_multiplier=Decimal("10.0"),
            outstanding_debts=Decimal("200000.00"),
            children_count=2,
            education_cost_per_child=Decimal("40000.00"),
            funeral_costs=Decimal("8000.00"),
            existing_assets=Decimal("50000.00"),
            recommended_cover=Decimal("838000.00"),
            current_total_cover=Decimal("400000.00"),
            coverage_gap=Decimal("438000.00"),
            effective_from=datetime.utcnow()
        )

        db_session.add(analysis)
        await db_session.commit()
        await db_session.refresh(analysis)

        assert analysis.id is not None
        assert analysis.user_id == test_user.id
        assert analysis.annual_income == Decimal("60000.00")
        assert analysis.children_count == 2
        assert analysis.recommended_cover == Decimal("838000.00")
        assert analysis.coverage_gap == Decimal("438000.00")
        assert analysis.effective_to is None  # Current analysis

    @pytest.mark.asyncio
    async def test_calculate_recommended_cover(self, db_session, test_user):
        """Test recommended cover calculation."""
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal("80000.00"),
            income_multiplier=Decimal("10.0"),
            outstanding_debts=Decimal("300000.00"),
            children_count=3,
            education_cost_per_child=Decimal("50000.00"),
            funeral_costs=Decimal("12000.00"),
            existing_assets=Decimal("150000.00"),
            recommended_cover=Decimal("0.00"),  # Will calculate
            current_total_cover=Decimal("0.00"),
            coverage_gap=Decimal("0.00")
        )

        # Calculate recommended cover
        calculated_cover = analysis.calculate_recommended_cover()

        # Expected: (80000 * 10) + 300000 + (3 * 50000) + 12000 - 150000
        #         = 800000 + 300000 + 150000 + 12000 - 150000
        #         = 1,112,000
        expected_cover = Decimal("1112000.00")

        assert calculated_cover == expected_cover

    @pytest.mark.asyncio
    async def test_calculate_recommended_cover_no_children(self, db_session, test_user):
        """Test recommended cover calculation with no children."""
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal("100000.00"),
            income_multiplier=Decimal("8.0"),
            outstanding_debts=Decimal("400000.00"),
            children_count=0,
            education_cost_per_child=Decimal("0.00"),
            funeral_costs=Decimal("15000.00"),
            existing_assets=Decimal("200000.00"),
            recommended_cover=Decimal("0.00"),
            current_total_cover=Decimal("0.00"),
            coverage_gap=Decimal("0.00")
        )

        calculated_cover = analysis.calculate_recommended_cover()

        # Expected: (100000 * 8) + 400000 + 0 + 15000 - 200000
        #         = 800000 + 400000 + 15000 - 200000
        #         = 1,015,000
        expected_cover = Decimal("1015000.00")

        assert calculated_cover == expected_cover

    @pytest.mark.asyncio
    async def test_calculate_recommended_cover_never_negative(self, db_session, test_user):
        """Test that recommended cover never goes negative."""
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal("50000.00"),
            income_multiplier=Decimal("5.0"),
            outstanding_debts=Decimal("0.00"),
            children_count=0,
            education_cost_per_child=Decimal("0.00"),
            funeral_costs=Decimal("0.00"),
            existing_assets=Decimal("500000.00"),  # More assets than income replacement
            recommended_cover=Decimal("0.00"),
            current_total_cover=Decimal("0.00"),
            coverage_gap=Decimal("0.00")
        )

        calculated_cover = analysis.calculate_recommended_cover()

        # Expected: (50000 * 5) - 500000 = -250000, but should be clamped to 0
        assert calculated_cover == Decimal("0.00")

    @pytest.mark.asyncio
    async def test_calculate_coverage_gap_positive(self, db_session, test_user):
        """Test coverage gap calculation when under-insured."""
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal("70000.00"),
            income_multiplier=Decimal("10.0"),
            outstanding_debts=Decimal("0.00"),
            children_count=0,
            education_cost_per_child=Decimal("0.00"),
            funeral_costs=Decimal("0.00"),
            existing_assets=Decimal("0.00"),
            recommended_cover=Decimal("700000.00"),
            current_total_cover=Decimal("400000.00"),
            coverage_gap=Decimal("0.00")
        )

        gap = analysis.calculate_coverage_gap()

        # Expected: 700000 - 400000 = 300000 (under-insured)
        assert gap == Decimal("300000.00")

    @pytest.mark.asyncio
    async def test_calculate_coverage_gap_negative(self, db_session, test_user):
        """Test coverage gap calculation when over-insured."""
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal("50000.00"),
            income_multiplier=Decimal("10.0"),
            outstanding_debts=Decimal("0.00"),
            children_count=0,
            education_cost_per_child=Decimal("0.00"),
            funeral_costs=Decimal("0.00"),
            existing_assets=Decimal("0.00"),
            recommended_cover=Decimal("500000.00"),
            current_total_cover=Decimal("800000.00"),
            coverage_gap=Decimal("0.00")
        )

        gap = analysis.calculate_coverage_gap()

        # Expected: 500000 - 800000 = -300000 (over-insured)
        assert gap == Decimal("-300000.00")

    @pytest.mark.asyncio
    async def test_temporal_data_effective_dates(self, db_session, test_user):
        """Test temporal data with effective_from and effective_to."""
        # Create first analysis
        analysis1 = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date(2024, 1, 1),
            annual_income=Decimal("60000.00"),
            income_multiplier=Decimal("10.0"),
            outstanding_debts=Decimal("200000.00"),
            children_count=2,
            education_cost_per_child=Decimal("40000.00"),
            funeral_costs=Decimal("8000.00"),
            existing_assets=Decimal("50000.00"),
            recommended_cover=Decimal("838000.00"),
            current_total_cover=Decimal("400000.00"),
            coverage_gap=Decimal("438000.00"),
            effective_from=datetime(2024, 1, 1, 0, 0, 0),
            effective_to=None
        )
        db_session.add(analysis1)
        await db_session.commit()
        await db_session.refresh(analysis1)

        # Create second analysis (supersedes first)
        now = datetime.utcnow()
        analysis2 = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal("70000.00"),
            income_multiplier=Decimal("10.0"),
            outstanding_debts=Decimal("180000.00"),
            children_count=2,
            education_cost_per_child=Decimal("50000.00"),
            funeral_costs=Decimal("10000.00"),
            existing_assets=Decimal("60000.00"),
            recommended_cover=Decimal("830000.00"),
            current_total_cover=Decimal("500000.00"),
            coverage_gap=Decimal("330000.00"),
            effective_from=now,
            effective_to=None
        )
        db_session.add(analysis2)

        # Update first analysis to set effective_to
        analysis1.effective_to = now
        await db_session.commit()
        await db_session.refresh(analysis1)
        await db_session.refresh(analysis2)

        # Check temporal data
        assert analysis1.effective_to == now
        assert analysis2.effective_to is None  # Current
        assert analysis2.effective_from == now

    @pytest.mark.asyncio
    async def test_get_current_analysis(self, db_session, test_user):
        """Test get_current_analysis method."""
        # Create multiple analyses
        past_time = datetime.utcnow() - timedelta(days=30)
        now = datetime.utcnow()

        # Old analysis (superseded)
        analysis1 = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today() - timedelta(days=30),
            annual_income=Decimal("60000.00"),
            income_multiplier=Decimal("10.0"),
            outstanding_debts=Decimal("200000.00"),
            children_count=2,
            education_cost_per_child=Decimal("40000.00"),
            funeral_costs=Decimal("8000.00"),
            existing_assets=Decimal("50000.00"),
            recommended_cover=Decimal("838000.00"),
            current_total_cover=Decimal("400000.00"),
            coverage_gap=Decimal("438000.00"),
            effective_from=past_time,
            effective_to=now  # Superseded
        )
        db_session.add(analysis1)

        # Current analysis
        analysis2 = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal("70000.00"),
            income_multiplier=Decimal("10.0"),
            outstanding_debts=Decimal("180000.00"),
            children_count=2,
            education_cost_per_child=Decimal("50000.00"),
            funeral_costs=Decimal("10000.00"),
            existing_assets=Decimal("60000.00"),
            recommended_cover=Decimal("830000.00"),
            current_total_cover=Decimal("500000.00"),
            coverage_gap=Decimal("330000.00"),
            effective_from=now,
            effective_to=None  # Current
        )
        db_session.add(analysis2)
        await db_session.commit()

        # Get current analysis
        current = await CoverageNeedsAnalysis.get_current_analysis(db_session, test_user.id)

        assert current is not None
        assert current.id == analysis2.id
        assert current.effective_to is None
        assert current.annual_income == Decimal("70000.00")

    @pytest.mark.asyncio
    async def test_get_current_analysis_no_analysis(self, db_session, test_user):
        """Test get_current_analysis when no analysis exists."""
        current = await CoverageNeedsAnalysis.get_current_analysis(db_session, test_user.id)
        assert current is None

    @pytest.mark.asyncio
    async def test_constraint_negative_annual_income(self, db_session, test_user):
        """Test that negative annual income violates constraint."""
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal("-10000.00"),  # Negative
            income_multiplier=Decimal("10.0"),
            outstanding_debts=Decimal("0.00"),
            children_count=0,
            education_cost_per_child=Decimal("0.00"),
            funeral_costs=Decimal("0.00"),
            existing_assets=Decimal("0.00"),
            recommended_cover=Decimal("0.00"),
            current_total_cover=Decimal("0.00"),
            coverage_gap=Decimal("0.00")
        )
        db_session.add(analysis)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert "check_positive_annual_income" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_constraint_zero_income_multiplier(self, db_session, test_user):
        """Test that zero income multiplier violates constraint."""
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal("50000.00"),
            income_multiplier=Decimal("0.0"),  # Zero (should be > 0)
            outstanding_debts=Decimal("0.00"),
            children_count=0,
            education_cost_per_child=Decimal("0.00"),
            funeral_costs=Decimal("0.00"),
            existing_assets=Decimal("0.00"),
            recommended_cover=Decimal("0.00"),
            current_total_cover=Decimal("0.00"),
            coverage_gap=Decimal("0.00")
        )
        db_session.add(analysis)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert "check_positive_income_multiplier" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_constraint_negative_children_count(self, db_session, test_user):
        """Test that negative children count violates constraint."""
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal("50000.00"),
            income_multiplier=Decimal("10.0"),
            outstanding_debts=Decimal("0.00"),
            children_count=-1,  # Negative
            education_cost_per_child=Decimal("0.00"),
            funeral_costs=Decimal("0.00"),
            existing_assets=Decimal("0.00"),
            recommended_cover=Decimal("0.00"),
            current_total_cover=Decimal("0.00"),
            coverage_gap=Decimal("0.00")
        )
        db_session.add(analysis)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert "check_positive_children_count" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_constraint_invalid_effective_dates(self, db_session, test_user):
        """Test that effective_to < effective_from violates constraint."""
        now = datetime.utcnow()
        past = now - timedelta(days=1)

        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal("50000.00"),
            income_multiplier=Decimal("10.0"),
            outstanding_debts=Decimal("0.00"),
            children_count=0,
            education_cost_per_child=Decimal("0.00"),
            funeral_costs=Decimal("0.00"),
            existing_assets=Decimal("0.00"),
            recommended_cover=Decimal("0.00"),
            current_total_cover=Decimal("0.00"),
            coverage_gap=Decimal("0.00"),
            effective_from=now,
            effective_to=past  # Before effective_from
        )
        db_session.add(analysis)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert "check_valid_effective_dates" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_user_relationship_cascade_delete(self, db_session, test_user):
        """Test that deleting user cascades to coverage analyses."""
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal("50000.00"),
            income_multiplier=Decimal("10.0"),
            outstanding_debts=Decimal("0.00"),
            children_count=0,
            education_cost_per_child=Decimal("0.00"),
            funeral_costs=Decimal("0.00"),
            existing_assets=Decimal("0.00"),
            recommended_cover=Decimal("500000.00"),
            current_total_cover=Decimal("0.00"),
            coverage_gap=Decimal("500000.00")
        )
        db_session.add(analysis)
        await db_session.commit()

        analysis_id = analysis.id

        # Delete user
        await db_session.delete(test_user)
        await db_session.commit()

        # Check analysis is deleted
        query = select(CoverageNeedsAnalysis).where(CoverageNeedsAnalysis.id == analysis_id)
        result = await db_session.execute(query)
        deleted_analysis = result.scalar_one_or_none()

        assert deleted_analysis is None


class TestPolicyPremiumReminder:
    """Test PolicyPremiumReminder model."""

    @pytest.mark.asyncio
    async def test_create_reminder_with_valid_data(self, db_session, test_policy):
        """Test creating a premium reminder with valid data."""
        reminder = PolicyPremiumReminder(
            policy_id=test_policy.id,
            reminder_date=date(2024, 12, 1),
            reminder_type=ReminderType.EMAIL,
            reminder_sent=False
        )

        db_session.add(reminder)
        await db_session.commit()
        await db_session.refresh(reminder)

        assert reminder.id is not None
        assert reminder.policy_id == test_policy.id
        assert reminder.reminder_date == date(2024, 12, 1)
        assert reminder.reminder_type == ReminderType.EMAIL
        assert reminder.reminder_sent is False
        assert reminder.sent_at is None

    @pytest.mark.asyncio
    async def test_default_reminder_type(self, db_session, test_policy):
        """Test default reminder type is IN_APP."""
        reminder = PolicyPremiumReminder(
            policy_id=test_policy.id,
            reminder_date=date(2024, 11, 15)
        )

        db_session.add(reminder)
        await db_session.commit()
        await db_session.refresh(reminder)

        assert reminder.reminder_type == ReminderType.IN_APP

    @pytest.mark.asyncio
    async def test_mark_reminder_sent(self, db_session, test_policy):
        """Test marking reminder as sent."""
        reminder = PolicyPremiumReminder(
            policy_id=test_policy.id,
            reminder_date=date(2024, 10, 15),
            reminder_type=ReminderType.IN_APP,
            reminder_sent=False
        )

        db_session.add(reminder)
        await db_session.commit()
        await db_session.refresh(reminder)

        # Mark as sent
        sent_time = datetime.utcnow()
        reminder.reminder_sent = True
        reminder.sent_at = sent_time

        await db_session.commit()
        await db_session.refresh(reminder)

        assert reminder.reminder_sent is True
        assert reminder.sent_at == sent_time

    @pytest.mark.asyncio
    async def test_policy_relationship(self, db_session, test_policy):
        """Test relationship with policy."""
        reminder = PolicyPremiumReminder(
            policy_id=test_policy.id,
            reminder_date=date(2024, 10, 20),
            reminder_type=ReminderType.EMAIL
        )

        db_session.add(reminder)
        await db_session.commit()
        await db_session.refresh(reminder)

        # Access relationship
        assert reminder.policy is not None
        assert reminder.policy.id == test_policy.id
        assert reminder.policy.provider == "Legal & General"

    @pytest.mark.asyncio
    async def test_cascade_delete_on_policy_delete(self, db_session, test_policy):
        """Test that deleting policy cascades to reminders."""
        # Skip if using SQLite (cascade deletes not fully supported in test DB)
        if 'sqlite' in str(db_session.bind.url).lower():
            pytest.skip("Cascade delete testing not reliable on SQLite test DB")

        # Create multiple reminders
        reminder1 = PolicyPremiumReminder(
            policy_id=test_policy.id,
            reminder_date=date(2024, 10, 15),
            reminder_type=ReminderType.EMAIL
        )
        reminder2 = PolicyPremiumReminder(
            policy_id=test_policy.id,
            reminder_date=date(2024, 11, 15),
            reminder_type=ReminderType.IN_APP
        )

        db_session.add(reminder1)
        db_session.add(reminder2)
        await db_session.commit()

        reminder1_id = reminder1.id
        reminder2_id = reminder2.id

        # Delete policy
        await db_session.delete(test_policy)
        await db_session.commit()

        # Check reminders are deleted
        query = select(PolicyPremiumReminder).where(
            PolicyPremiumReminder.id.in_([reminder1_id, reminder2_id])
        )
        result = await db_session.execute(query)
        reminders = result.scalars().all()

        assert len(reminders) == 0

    @pytest.mark.asyncio
    async def test_multiple_reminders_per_policy(self, db_session, test_policy):
        """Test creating multiple reminders for one policy."""
        reminders = [
            PolicyPremiumReminder(
                policy_id=test_policy.id,
                reminder_date=date(2024, 10, 1),
                reminder_type=ReminderType.EMAIL
            ),
            PolicyPremiumReminder(
                policy_id=test_policy.id,
                reminder_date=date(2024, 11, 1),
                reminder_type=ReminderType.IN_APP
            ),
            PolicyPremiumReminder(
                policy_id=test_policy.id,
                reminder_date=date(2024, 12, 1),
                reminder_type=ReminderType.EMAIL
            ),
        ]

        for reminder in reminders:
            db_session.add(reminder)

        await db_session.commit()

        # Query reminders for policy
        query = select(PolicyPremiumReminder).where(
            PolicyPremiumReminder.policy_id == test_policy.id
        )
        result = await db_session.execute(query)
        fetched_reminders = result.scalars().all()

        assert len(fetched_reminders) == 3


class TestIndexes:
    """Test that database indexes exist."""

    @pytest.mark.asyncio
    async def test_coverage_analysis_indexes_exist(self, db_session):
        """Test that coverage analysis indexes exist."""
        # Skip if using SQLite (test DB uses SQLite, production uses PostgreSQL)
        if 'sqlite' in str(db_session.bind.url).lower():
            pytest.skip("Index inspection not reliable on SQLite test DB")

        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('coverage_needs_analysis')
        index_names = [idx['name'] for idx in indexes]

        # Check required indexes exist
        assert 'idx_coverage_analysis_user_effective_from' in index_names
        assert 'idx_coverage_analysis_user_effective_to' in index_names
        assert 'idx_coverage_analysis_user_id' in index_names

    @pytest.mark.asyncio
    async def test_premium_reminder_indexes_exist(self, db_session):
        """Test that premium reminder indexes exist."""
        # Skip if using SQLite (test DB uses SQLite, production uses PostgreSQL)
        if 'sqlite' in str(db_session.bind.url).lower():
            pytest.skip("Index inspection not reliable on SQLite test DB")

        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('policy_premium_reminders')
        index_names = [idx['name'] for idx in indexes]

        # Check required indexes exist
        assert 'idx_premium_reminder_date_sent' in index_names
        assert 'idx_premium_reminder_policy' in index_names
