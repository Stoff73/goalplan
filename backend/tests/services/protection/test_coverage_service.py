"""
Tests for Coverage Gap Analysis Service

Tests comprehensive coverage analysis operations including:
- Recommended cover calculation
- Coverage gap calculation with multiple policies
- Coverage summary retrieval
- Analysis creation with temporal data
- Analysis updates with recalculation
- Historical analysis tracking
- Edge cases (no policies, over-insured, zero values)
- Status determination (adequate, under-insured, over-insured)
- Validation errors
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from uuid import uuid4, UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from services.protection import coverage_analysis_service
from services.protection.exceptions import (
    CoverageAnalysisNotFoundError,
    CoverageAnalysisValidationError
)
from models.life_assurance import (
    CoverageNeedsAnalysis,
    LifeAssurancePolicy,
    PolicyStatus,
    PremiumFrequency,
    ProviderCountry,
    PolicyType,
    Currency
)
from models.user import User


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    from models.user import UserStatus, CountryPreference

    user = User(
        id=uuid4(),
        email=f"testuser_{uuid4()}@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        status=UserStatus.ACTIVE,
        email_verified=True,
        country_preference=CountryPreference.UK,
        terms_accepted_at=datetime.utcnow()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def other_user(db_session: AsyncSession) -> User:
    """Create another test user for permission tests."""
    from models.user import UserStatus, CountryPreference

    user = User(
        id=uuid4(),
        email=f"otheruser_{uuid4()}@example.com",
        password_hash="hashed_password",
        first_name="Other",
        last_name="User",
        status=UserStatus.ACTIVE,
        email_verified=True,
        country_preference=CountryPreference.UK,
        terms_accepted_at=datetime.utcnow()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def active_policy(db_session: AsyncSession, test_user: User) -> LifeAssurancePolicy:
    """Create an active life assurance policy."""
    policy = LifeAssurancePolicy(
        id=uuid4(),
        user_id=test_user.id,
        provider="Legal & General",
        provider_country=ProviderCountry.UK,
        policy_type=PolicyType.TERM,
        cover_amount=Decimal('500000.00'),
        currency=Currency.GBP,
        premium_amount=Decimal('50.00'),
        premium_frequency=PremiumFrequency.MONTHLY,
        annual_premium=Decimal('600.00'),
        start_date=date(2024, 1, 1),
        end_date=date(2044, 1, 1),
        status=PolicyStatus.ACTIVE,
        is_deleted=False
    )
    # Set encrypted policy number
    policy.set_policy_number('POL123456')

    db_session.add(policy)
    await db_session.commit()
    await db_session.refresh(policy)
    return policy


@pytest.fixture
async def second_active_policy(db_session: AsyncSession, test_user: User) -> LifeAssurancePolicy:
    """Create a second active life assurance policy."""
    policy = LifeAssurancePolicy(
        id=uuid4(),
        user_id=test_user.id,
        provider="Aviva",
        provider_country=ProviderCountry.UK,
        policy_type=PolicyType.WHOLE_OF_LIFE,
        cover_amount=Decimal('300000.00'),
        currency=Currency.GBP,
        premium_amount=Decimal('75.00'),
        premium_frequency=PremiumFrequency.MONTHLY,
        annual_premium=Decimal('900.00'),
        start_date=date(2024, 1, 1),
        end_date=None,
        status=PolicyStatus.ACTIVE,
        is_deleted=False
    )
    policy.set_policy_number('POL789012')

    db_session.add(policy)
    await db_session.commit()
    await db_session.refresh(policy)
    return policy


@pytest.fixture
async def lapsed_policy(db_session: AsyncSession, test_user: User) -> LifeAssurancePolicy:
    """Create a lapsed policy (should not count in coverage)."""
    policy = LifeAssurancePolicy(
        id=uuid4(),
        user_id=test_user.id,
        provider="Old Mutual",
        provider_country=ProviderCountry.SA,
        policy_type=PolicyType.TERM,
        cover_amount=Decimal('1000000.00'),  # Large but lapsed
        currency=Currency.ZAR,
        premium_amount=Decimal('500.00'),
        premium_frequency=PremiumFrequency.MONTHLY,
        annual_premium=Decimal('6000.00'),
        start_date=date(2020, 1, 1),
        end_date=date(2030, 1, 1),
        status=PolicyStatus.LAPSED,
        is_deleted=False
    )
    policy.set_policy_number('LAPSED123')

    db_session.add(policy)
    await db_session.commit()
    await db_session.refresh(policy)
    return policy


# ============================================================================
# Test calculate_recommended_cover function
# ============================================================================

class TestCalculateRecommendedCover:
    """Test suite for calculate_recommended_cover function."""

    def test_basic_calculation(self):
        """Test basic recommended cover calculation."""
        recommended = coverage_analysis_service.calculate_recommended_cover(
            annual_income=50000.0,
            outstanding_debts=200000.0,
            children_count=2,
            education_cost_per_child=100000.0,
            funeral_costs=5000.0,
            existing_assets=50000.0,
            income_multiplier=10.0
        )

        # (50000 * 10) + 200000 + (2 * 100000) + 5000 - 50000 = 855000
        assert recommended == 855000.0

    def test_no_children(self):
        """Test calculation with no children."""
        recommended = coverage_analysis_service.calculate_recommended_cover(
            annual_income=60000.0,
            outstanding_debts=150000.0,
            children_count=0,
            education_cost_per_child=100000.0,
            funeral_costs=5000.0,
            existing_assets=20000.0,
            income_multiplier=10.0
        )

        # (60000 * 10) + 150000 + 0 + 5000 - 20000 = 735000
        assert recommended == 735000.0

    def test_custom_income_multiplier(self):
        """Test calculation with custom income multiplier."""
        recommended = coverage_analysis_service.calculate_recommended_cover(
            annual_income=40000.0,
            outstanding_debts=100000.0,
            children_count=1,
            education_cost_per_child=80000.0,
            funeral_costs=4000.0,
            existing_assets=10000.0,
            income_multiplier=15.0  # Higher multiplier
        )

        # (40000 * 15) + 100000 + 80000 + 4000 - 10000 = 774000
        assert recommended == 774000.0

    def test_never_returns_negative(self):
        """Test that recommended cover never goes negative."""
        # Existing assets exceed all needs
        recommended = coverage_analysis_service.calculate_recommended_cover(
            annual_income=30000.0,
            outstanding_debts=50000.0,
            children_count=0,
            education_cost_per_child=0.0,
            funeral_costs=5000.0,
            existing_assets=500000.0,  # Very high
            income_multiplier=10.0
        )

        # (30000 * 10) + 50000 + 0 + 5000 - 500000 = -145000, should return 0
        assert recommended == 0.0

    def test_zero_values(self):
        """Test calculation with all zero values."""
        recommended = coverage_analysis_service.calculate_recommended_cover(
            annual_income=0.0,
            outstanding_debts=0.0,
            children_count=0,
            education_cost_per_child=0.0,
            funeral_costs=0.0,
            existing_assets=0.0,
            income_multiplier=10.0
        )

        assert recommended == 0.0

    def test_validation_negative_income(self):
        """Test validation fails for negative annual income."""
        with pytest.raises(CoverageAnalysisValidationError) as exc_info:
            coverage_analysis_service.calculate_recommended_cover(
                annual_income=-1000.0,
                outstanding_debts=0.0,
                children_count=0,
                education_cost_per_child=0.0,
                funeral_costs=0.0,
                existing_assets=0.0,
                income_multiplier=10.0
            )
        assert "Annual income must be >= 0" in str(exc_info.value)

    def test_validation_negative_debts(self):
        """Test validation fails for negative debts."""
        with pytest.raises(CoverageAnalysisValidationError) as exc_info:
            coverage_analysis_service.calculate_recommended_cover(
                annual_income=50000.0,
                outstanding_debts=-10000.0,
                children_count=0,
                education_cost_per_child=0.0,
                funeral_costs=0.0,
                existing_assets=0.0,
                income_multiplier=10.0
            )
        assert "Outstanding debts must be >= 0" in str(exc_info.value)

    def test_validation_negative_children_count(self):
        """Test validation fails for negative children count."""
        with pytest.raises(CoverageAnalysisValidationError) as exc_info:
            coverage_analysis_service.calculate_recommended_cover(
                annual_income=50000.0,
                outstanding_debts=0.0,
                children_count=-1,
                education_cost_per_child=100000.0,
                funeral_costs=0.0,
                existing_assets=0.0,
                income_multiplier=10.0
            )
        assert "Children count must be >= 0" in str(exc_info.value)

    def test_validation_negative_education_cost(self):
        """Test validation fails for negative education cost."""
        with pytest.raises(CoverageAnalysisValidationError) as exc_info:
            coverage_analysis_service.calculate_recommended_cover(
                annual_income=50000.0,
                outstanding_debts=0.0,
                children_count=2,
                education_cost_per_child=-50000.0,
                funeral_costs=0.0,
                existing_assets=0.0,
                income_multiplier=10.0
            )
        assert "Education cost per child must be >= 0" in str(exc_info.value)

    def test_validation_negative_funeral_costs(self):
        """Test validation fails for negative funeral costs."""
        with pytest.raises(CoverageAnalysisValidationError) as exc_info:
            coverage_analysis_service.calculate_recommended_cover(
                annual_income=50000.0,
                outstanding_debts=0.0,
                children_count=0,
                education_cost_per_child=0.0,
                funeral_costs=-5000.0,
                existing_assets=0.0,
                income_multiplier=10.0
            )
        assert "Funeral costs must be >= 0" in str(exc_info.value)

    def test_validation_negative_existing_assets(self):
        """Test validation fails for negative existing assets."""
        with pytest.raises(CoverageAnalysisValidationError) as exc_info:
            coverage_analysis_service.calculate_recommended_cover(
                annual_income=50000.0,
                outstanding_debts=0.0,
                children_count=0,
                education_cost_per_child=0.0,
                funeral_costs=0.0,
                existing_assets=-10000.0,
                income_multiplier=10.0
            )
        assert "Existing assets must be >= 0" in str(exc_info.value)

    def test_validation_zero_income_multiplier(self):
        """Test validation fails for zero income multiplier."""
        with pytest.raises(CoverageAnalysisValidationError) as exc_info:
            coverage_analysis_service.calculate_recommended_cover(
                annual_income=50000.0,
                outstanding_debts=0.0,
                children_count=0,
                education_cost_per_child=0.0,
                funeral_costs=0.0,
                existing_assets=0.0,
                income_multiplier=0.0
            )
        assert "Income multiplier must be > 0" in str(exc_info.value)


# ============================================================================
# Test calculate_coverage_gap function
# ============================================================================

class TestCalculateCoverageGap:
    """Test suite for calculate_coverage_gap function."""

    @pytest.mark.asyncio
    async def test_no_policies(self, db_session: AsyncSession, test_user: User):
        """Test coverage gap with no policies."""
        gap_data = await coverage_analysis_service.calculate_coverage_gap(
            db=db_session,
            user_id=test_user.id,
            recommended_cover=500000.0
        )

        assert gap_data['current_total_cover'] == 0.0
        assert gap_data['recommended_cover'] == 500000.0
        assert gap_data['coverage_gap'] == 500000.0
        assert gap_data['gap_percentage'] == 100.0
        assert gap_data['policies_contributing'] == 0
        assert gap_data['status'] == 'UNDER_INSURED'

    @pytest.mark.asyncio
    async def test_single_active_policy(
        self,
        db_session: AsyncSession,
        test_user: User,
        active_policy: LifeAssurancePolicy
    ):
        """Test coverage gap with one active policy."""
        gap_data = await coverage_analysis_service.calculate_coverage_gap(
            db=db_session,
            user_id=test_user.id,
            recommended_cover=700000.0
        )

        assert gap_data['current_total_cover'] == 500000.0
        assert gap_data['recommended_cover'] == 700000.0
        assert gap_data['coverage_gap'] == 200000.0
        assert abs(gap_data['gap_percentage'] - 28.57) < 0.1  # ~28.57%
        assert gap_data['policies_contributing'] == 1
        assert gap_data['status'] == 'UNDER_INSURED'

    @pytest.mark.asyncio
    async def test_multiple_active_policies(
        self,
        db_session: AsyncSession,
        test_user: User,
        active_policy: LifeAssurancePolicy,
        second_active_policy: LifeAssurancePolicy
    ):
        """Test coverage gap with multiple active policies."""
        gap_data = await coverage_analysis_service.calculate_coverage_gap(
            db=db_session,
            user_id=test_user.id,
            recommended_cover=900000.0
        )

        # 500000 + 300000 = 800000
        assert gap_data['current_total_cover'] == 800000.0
        assert gap_data['recommended_cover'] == 900000.0
        assert gap_data['coverage_gap'] == 100000.0
        assert abs(gap_data['gap_percentage'] - 11.11) < 0.1  # ~11.11%
        assert gap_data['policies_contributing'] == 2
        assert gap_data['status'] == 'UNDER_INSURED'

    @pytest.mark.asyncio
    async def test_lapsed_policy_excluded(
        self,
        db_session: AsyncSession,
        test_user: User,
        active_policy: LifeAssurancePolicy,
        lapsed_policy: LifeAssurancePolicy
    ):
        """Test that lapsed policies are excluded from coverage total."""
        gap_data = await coverage_analysis_service.calculate_coverage_gap(
            db=db_session,
            user_id=test_user.id,
            recommended_cover=700000.0
        )

        # Only active policy counts (500000), lapsed policy (1000000) excluded
        assert gap_data['current_total_cover'] == 500000.0
        assert gap_data['policies_contributing'] == 1

    @pytest.mark.asyncio
    async def test_over_insured_status(
        self,
        db_session: AsyncSession,
        test_user: User,
        active_policy: LifeAssurancePolicy,
        second_active_policy: LifeAssurancePolicy
    ):
        """Test over-insured status (negative gap > 10%)."""
        gap_data = await coverage_analysis_service.calculate_coverage_gap(
            db=db_session,
            user_id=test_user.id,
            recommended_cover=500000.0  # Less than current coverage
        )

        # Current: 800000, Recommended: 500000, Gap: -300000
        assert gap_data['current_total_cover'] == 800000.0
        assert gap_data['coverage_gap'] == -300000.0
        assert gap_data['gap_percentage'] == -60.0
        assert gap_data['status'] == 'OVER_INSURED'

    @pytest.mark.asyncio
    async def test_adequate_coverage_status(
        self,
        db_session: AsyncSession,
        test_user: User,
        active_policy: LifeAssurancePolicy
    ):
        """Test adequate coverage status (within ±10%)."""
        # Recommended very close to current (within 10%)
        gap_data = await coverage_analysis_service.calculate_coverage_gap(
            db=db_session,
            user_id=test_user.id,
            recommended_cover=520000.0  # 4% higher than current 500000
        )

        assert gap_data['coverage_gap'] == 20000.0
        assert abs(gap_data['gap_percentage'] - 3.85) < 0.1  # ~3.85%
        assert gap_data['status'] == 'ADEQUATE'

    @pytest.mark.asyncio
    async def test_zero_recommended_cover(
        self,
        db_session: AsyncSession,
        test_user: User,
        active_policy: LifeAssurancePolicy
    ):
        """Test gap calculation with zero recommended cover."""
        gap_data = await coverage_analysis_service.calculate_coverage_gap(
            db=db_session,
            user_id=test_user.id,
            recommended_cover=0.0
        )

        assert gap_data['recommended_cover'] == 0.0
        assert gap_data['coverage_gap'] == -500000.0
        assert gap_data['gap_percentage'] == 0.0  # Avoid division by zero
        assert gap_data['status'] == 'ADEQUATE'  # Within ±10% of 0


# ============================================================================
# Test get_coverage_summary function
# ============================================================================

class TestGetCoverageSummary:
    """Test suite for get_coverage_summary function."""

    @pytest.mark.asyncio
    async def test_no_analysis_exists(self, db_session: AsyncSession, test_user: User):
        """Test get summary when no analysis exists."""
        summary = await coverage_analysis_service.get_coverage_summary(
            db=db_session,
            user_id=test_user.id
        )

        assert summary is None

    @pytest.mark.asyncio
    async def test_with_existing_analysis(
        self,
        db_session: AsyncSession,
        test_user: User,
        active_policy: LifeAssurancePolicy
    ):
        """Test get summary with existing analysis."""
        # Create an analysis
        analysis = CoverageNeedsAnalysis(
            id=uuid4(),
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal('60000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('200000.00'),
            children_count=2,
            education_cost_per_child=Decimal('100000.00'),
            funeral_costs=Decimal('5000.00'),
            existing_assets=Decimal('50000.00'),
            recommended_cover=Decimal('755000.00'),
            current_total_cover=Decimal('500000.00'),
            coverage_gap=Decimal('255000.00'),
            effective_from=datetime.utcnow(),
            effective_to=None  # Current analysis
        )
        db_session.add(analysis)
        await db_session.commit()

        # Get summary
        summary = await coverage_analysis_service.get_coverage_summary(
            db=db_session,
            user_id=test_user.id
        )

        assert summary is not None
        assert summary['analysis_date'] == date.today()
        assert summary['annual_income'] == 60000.0
        assert summary['outstanding_debts'] == 200000.0
        assert summary['children_count'] == 2
        assert summary['recommended_cover'] == 755000.0
        assert summary['current_total_cover'] == 500000.0  # From active_policy
        assert summary['coverage_gap'] == 255000.0
        assert summary['policies_count'] == 1

    @pytest.mark.asyncio
    async def test_summary_ignores_historical_analysis(
        self,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test that summary only returns current analysis, not historical."""
        # Create historical analysis
        old_analysis = CoverageNeedsAnalysis(
            id=uuid4(),
            user_id=test_user.id,
            calculation_date=date(2023, 1, 1),
            annual_income=Decimal('50000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('150000.00'),
            children_count=1,
            education_cost_per_child=Decimal('80000.00'),
            funeral_costs=Decimal('4000.00'),
            existing_assets=Decimal('30000.00'),
            recommended_cover=Decimal('654000.00'),
            current_total_cover=Decimal('400000.00'),
            coverage_gap=Decimal('254000.00'),
            effective_from=datetime(2023, 1, 1),
            effective_to=datetime(2024, 1, 1)  # Historical (expired)
        )
        db_session.add(old_analysis)
        await db_session.commit()

        # Get summary - should return None since no current analysis
        summary = await coverage_analysis_service.get_coverage_summary(
            db=db_session,
            user_id=test_user.id
        )

        assert summary is None


# ============================================================================
# Test create_coverage_analysis function
# ============================================================================

class TestCreateCoverageAnalysis:
    """Test suite for create_coverage_analysis function."""

    @pytest.mark.asyncio
    async def test_create_new_analysis(
        self,
        db_session: AsyncSession,
        test_user: User,
        active_policy: LifeAssurancePolicy
    ):
        """Test creating a new coverage analysis."""
        analysis_data = {
            'annual_income': 60000.0,
            'outstanding_debts': 200000.0,
            'children_count': 2,
            'education_cost_per_child': 100000.0,
            'funeral_costs': 5000.0,
            'existing_assets': 50000.0,
            'income_multiplier': 10.0,
            'notes': 'Initial analysis'
        }

        analysis = await coverage_analysis_service.create_coverage_analysis(
            db=db_session,
            user_id=test_user.id,
            analysis_data=analysis_data
        )

        assert analysis.id is not None
        assert analysis.user_id == test_user.id
        assert float(analysis.annual_income) == 60000.0
        assert float(analysis.outstanding_debts) == 200000.0
        assert analysis.children_count == 2
        # (60000 * 10) + 200000 + (2 * 100000) + 5000 - 50000 = 955000
        assert float(analysis.recommended_cover) == 955000.0
        assert float(analysis.current_total_cover) == 500000.0  # From active_policy
        assert float(analysis.coverage_gap) == 455000.0
        assert analysis.effective_to is None  # Current analysis
        assert analysis.notes == 'Initial analysis'

    @pytest.mark.asyncio
    async def test_create_analysis_with_no_policies(
        self,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test creating analysis with no policies (gap = recommended)."""
        analysis_data = {
            'annual_income': 50000.0,
            'outstanding_debts': 100000.0,
            'children_count': 1,
            'education_cost_per_child': 80000.0,
            'funeral_costs': 4000.0,
            'existing_assets': 20000.0,
            'income_multiplier': 10.0
        }

        analysis = await coverage_analysis_service.create_coverage_analysis(
            db=db_session,
            user_id=test_user.id,
            analysis_data=analysis_data
        )

        # (50000 * 10) + 100000 + 80000 + 4000 - 20000 = 664000
        assert float(analysis.recommended_cover) == 664000.0
        assert float(analysis.current_total_cover) == 0.0
        assert float(analysis.coverage_gap) == 664000.0

    @pytest.mark.asyncio
    async def test_create_expires_previous_analysis_temporal_data(
        self,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test that creating new analysis expires the previous one (temporal data)."""
        # Create first analysis
        first_analysis = CoverageNeedsAnalysis(
            id=uuid4(),
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal('50000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('100000.00'),
            children_count=1,
            education_cost_per_child=Decimal('80000.00'),
            funeral_costs=Decimal('4000.00'),
            existing_assets=Decimal('20000.00'),
            recommended_cover=Decimal('664000.00'),
            current_total_cover=Decimal('0.00'),
            coverage_gap=Decimal('664000.00'),
            effective_from=datetime.utcnow(),
            effective_to=None  # Current
        )
        db_session.add(first_analysis)
        await db_session.commit()
        first_id = first_analysis.id

        # Create second analysis
        analysis_data = {
            'annual_income': 60000.0,
            'outstanding_debts': 150000.0,
            'children_count': 2,
            'education_cost_per_child': 100000.0,
            'funeral_costs': 5000.0,
            'existing_assets': 30000.0,
            'income_multiplier': 10.0
        }

        second_analysis = await coverage_analysis_service.create_coverage_analysis(
            db=db_session,
            user_id=test_user.id,
            analysis_data=analysis_data
        )

        # Verify second analysis is current
        assert second_analysis.effective_to is None

        # Verify first analysis was expired
        await db_session.refresh(first_analysis)
        assert first_analysis.effective_to is not None

        # Verify we now have 2 analyses for this user
        stmt = select(CoverageNeedsAnalysis).where(
            CoverageNeedsAnalysis.user_id == test_user.id
        )
        result = await db_session.execute(stmt)
        all_analyses = result.scalars().all()
        assert len(all_analyses) == 2


# ============================================================================
# Test update_coverage_analysis function
# ============================================================================

class TestUpdateCoverageAnalysis:
    """Test suite for update_coverage_analysis function."""

    @pytest.mark.asyncio
    async def test_update_analysis(
        self,
        db_session: AsyncSession,
        test_user: User,
        active_policy: LifeAssurancePolicy
    ):
        """Test updating an existing coverage analysis."""
        # Create analysis
        analysis = CoverageNeedsAnalysis(
            id=uuid4(),
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal('50000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('100000.00'),
            children_count=1,
            education_cost_per_child=Decimal('80000.00'),
            funeral_costs=Decimal('4000.00'),
            existing_assets=Decimal('20000.00'),
            recommended_cover=Decimal('664000.00'),
            current_total_cover=Decimal('500000.00'),
            coverage_gap=Decimal('164000.00'),
            effective_from=datetime.utcnow(),
            effective_to=None
        )
        db_session.add(analysis)
        await db_session.commit()
        analysis_id = analysis.id

        # Update analysis
        update_data = {
            'annual_income': 70000.0,  # Increased
            'children_count': 2  # Increased
        }

        updated = await coverage_analysis_service.update_coverage_analysis(
            db=db_session,
            analysis_id=analysis_id,
            user_id=test_user.id,
            update_data=update_data
        )

        # Verify fields updated
        assert float(updated.annual_income) == 70000.0
        assert updated.children_count == 2

        # Verify recommended cover recalculated
        # (70000 * 10) + 100000 + (2 * 80000) + 4000 - 20000 = 944000
        assert float(updated.recommended_cover) == 944000.0

        # Verify gap recalculated
        assert float(updated.current_total_cover) == 500000.0
        assert float(updated.coverage_gap) == 444000.0

    @pytest.mark.asyncio
    async def test_update_analysis_not_found(
        self,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test updating non-existent analysis raises error."""
        with pytest.raises(CoverageAnalysisNotFoundError):
            await coverage_analysis_service.update_coverage_analysis(
                db=db_session,
                analysis_id=uuid4(),  # Random UUID
                user_id=test_user.id,
                update_data={'annual_income': 60000.0}
            )

    @pytest.mark.asyncio
    async def test_update_analysis_permission_error(
        self,
        db_session: AsyncSession,
        test_user: User,
        other_user: User
    ):
        """Test updating another user's analysis raises error."""
        # Create analysis for test_user
        analysis = CoverageNeedsAnalysis(
            id=uuid4(),
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal('50000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('100000.00'),
            children_count=1,
            education_cost_per_child=Decimal('80000.00'),
            funeral_costs=Decimal('4000.00'),
            existing_assets=Decimal('20000.00'),
            recommended_cover=Decimal('664000.00'),
            current_total_cover=Decimal('0.00'),
            coverage_gap=Decimal('664000.00'),
            effective_from=datetime.utcnow(),
            effective_to=None
        )
        db_session.add(analysis)
        await db_session.commit()

        # Try to update with other_user
        with pytest.raises(CoverageAnalysisValidationError) as exc_info:
            await coverage_analysis_service.update_coverage_analysis(
                db=db_session,
                analysis_id=analysis.id,
                user_id=other_user.id,  # Wrong user
                update_data={'annual_income': 60000.0}
            )
        assert "does not have permission" in str(exc_info.value)


# ============================================================================
# Test get_historical_coverage_analyses function
# ============================================================================

class TestGetHistoricalCoverageAnalyses:
    """Test suite for get_historical_coverage_analyses function."""

    @pytest.mark.asyncio
    async def test_get_no_analyses(self, db_session: AsyncSession, test_user: User):
        """Test getting historical analyses when none exist."""
        analyses = await coverage_analysis_service.get_historical_coverage_analyses(
            db=db_session,
            user_id=test_user.id
        )

        assert len(analyses) == 0

    @pytest.mark.asyncio
    async def test_get_single_current_analysis(
        self,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test getting single current analysis."""
        analysis = CoverageNeedsAnalysis(
            id=uuid4(),
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal('50000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('100000.00'),
            children_count=1,
            education_cost_per_child=Decimal('80000.00'),
            funeral_costs=Decimal('4000.00'),
            existing_assets=Decimal('20000.00'),
            recommended_cover=Decimal('664000.00'),
            current_total_cover=Decimal('0.00'),
            coverage_gap=Decimal('664000.00'),
            effective_from=datetime.utcnow(),
            effective_to=None
        )
        db_session.add(analysis)
        await db_session.commit()

        analyses = await coverage_analysis_service.get_historical_coverage_analyses(
            db=db_session,
            user_id=test_user.id
        )

        assert len(analyses) == 1
        assert analyses[0].id == analysis.id

    @pytest.mark.asyncio
    async def test_get_multiple_analyses_ordered_by_date(
        self,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test getting multiple analyses ordered by effective_from descending."""
        # Create old analysis
        old_analysis = CoverageNeedsAnalysis(
            id=uuid4(),
            user_id=test_user.id,
            calculation_date=date(2023, 1, 1),
            annual_income=Decimal('40000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('80000.00'),
            children_count=0,
            education_cost_per_child=Decimal('0.00'),
            funeral_costs=Decimal('3000.00'),
            existing_assets=Decimal('10000.00'),
            recommended_cover=Decimal('473000.00'),
            current_total_cover=Decimal('0.00'),
            coverage_gap=Decimal('473000.00'),
            effective_from=datetime(2023, 1, 1),
            effective_to=datetime(2024, 1, 1)
        )

        # Create current analysis
        current_analysis = CoverageNeedsAnalysis(
            id=uuid4(),
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal('50000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('100000.00'),
            children_count=1,
            education_cost_per_child=Decimal('80000.00'),
            funeral_costs=Decimal('4000.00'),
            existing_assets=Decimal('20000.00'),
            recommended_cover=Decimal('664000.00'),
            current_total_cover=Decimal('0.00'),
            coverage_gap=Decimal('664000.00'),
            effective_from=datetime.utcnow(),
            effective_to=None
        )

        db_session.add(old_analysis)
        db_session.add(current_analysis)
        await db_session.commit()

        # Get all analyses
        analyses = await coverage_analysis_service.get_historical_coverage_analyses(
            db=db_session,
            user_id=test_user.id
        )

        assert len(analyses) == 2
        # Should be ordered newest first
        assert analyses[0].id == current_analysis.id
        assert analyses[1].id == old_analysis.id


# ============================================================================
# Edge Cases and Integration Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases and integration scenarios."""

    @pytest.mark.asyncio
    async def test_over_insured_negative_gap(
        self,
        db_session: AsyncSession,
        test_user: User,
        active_policy: LifeAssurancePolicy,
        second_active_policy: LifeAssurancePolicy
    ):
        """Test over-insured scenario with negative gap."""
        # Current coverage: 800000 (500000 + 300000)
        # Recommended: 400000
        # Gap: -400000 (over-insured)

        analysis_data = {
            'annual_income': 30000.0,
            'outstanding_debts': 50000.0,
            'children_count': 0,
            'education_cost_per_child': 0.0,
            'funeral_costs': 5000.0,
            'existing_assets': 10000.0,
            'income_multiplier': 10.0
        }

        analysis = await coverage_analysis_service.create_coverage_analysis(
            db=db_session,
            user_id=test_user.id,
            analysis_data=analysis_data
        )

        # (30000 * 10) + 50000 + 0 + 5000 - 10000 = 345000
        assert float(analysis.recommended_cover) == 345000.0
        assert float(analysis.current_total_cover) == 800000.0
        assert float(analysis.coverage_gap) == -455000.0  # Negative = over-insured

    @pytest.mark.asyncio
    async def test_adequate_coverage_boundary(
        self,
        db_session: AsyncSession,
        test_user: User,
        active_policy: LifeAssurancePolicy
    ):
        """Test adequate coverage at the 10% boundary."""
        # Current: 500000
        # Recommended: 550000 (10% higher)
        # Gap: 50000 (10% of recommended)
        # Should be at boundary of ADEQUATE

        analysis_data = {
            'annual_income': 45000.0,
            'outstanding_debts': 100000.0,
            'children_count': 0,
            'education_cost_per_child': 0.0,
            'funeral_costs': 5000.0,
            'existing_assets': 0.0,
            'income_multiplier': 10.0
        }

        analysis = await coverage_analysis_service.create_coverage_analysis(
            db=db_session,
            user_id=test_user.id,
            analysis_data=analysis_data
        )

        # (45000 * 10) + 100000 + 0 + 5000 - 0 = 555000
        assert float(analysis.recommended_cover) == 555000.0

        # Get gap data
        gap_data = await coverage_analysis_service.calculate_coverage_gap(
            db=db_session,
            user_id=test_user.id,
            recommended_cover=555000.0
        )

        # Gap percentage: (555000 - 500000) / 555000 = ~9.9%
        assert gap_data['gap_percentage'] < 10.0
        assert gap_data['status'] == 'ADEQUATE'

    @pytest.mark.asyncio
    async def test_deleted_policy_excluded(
        self,
        db_session: AsyncSession,
        test_user: User,
        active_policy: LifeAssurancePolicy
    ):
        """Test that soft-deleted policies are excluded from coverage."""
        # Create another policy and soft delete it
        deleted_policy = LifeAssurancePolicy(
            id=uuid4(),
            user_id=test_user.id,
            provider="Deleted Provider",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal('200000.00'),
            currency=Currency.GBP,
            premium_amount=Decimal('30.00'),
            premium_frequency=PremiumFrequency.MONTHLY,
            annual_premium=Decimal('360.00'),
            start_date=date(2024, 1, 1),
            end_date=date(2044, 1, 1),
            status=PolicyStatus.ACTIVE,
            is_deleted=True  # Soft deleted
        )
        deleted_policy.set_policy_number('DELETED123')
        db_session.add(deleted_policy)
        await db_session.commit()

        # Calculate gap
        gap_data = await coverage_analysis_service.calculate_coverage_gap(
            db=db_session,
            user_id=test_user.id,
            recommended_cover=700000.0
        )

        # Should only count active_policy (500000), not deleted_policy (200000)
        assert gap_data['current_total_cover'] == 500000.0
        assert gap_data['policies_contributing'] == 1
