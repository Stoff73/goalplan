"""
Tests for Coverage Analysis API endpoints.

This test suite covers:
- Creating coverage analysis
- Getting coverage summary (with and without analysis)
- Getting coverage summary with no policies
- Listing historical analyses
- Getting specific analysis by ID
- Updating analysis
- Authentication (401)
- Authorization (403)
- Validation errors (400)
"""

import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta
from uuid import uuid4

from models.life_assurance import (
    CoverageNeedsAnalysis,
    LifeAssurancePolicy,
    PolicyStatus,
    PolicyType,
    ProviderCountry,
    PremiumFrequency,
    Currency,
    PolicyBeneficiary,
    BeneficiaryRelationship
)


# ============================================================================
# CREATE COVERAGE ANALYSIS TESTS
# ============================================================================

@pytest.mark.asyncio
class TestCreateCoverageAnalysis:
    """Tests for POST /api/v1/protection/coverage-analysis"""

    async def test_create_coverage_analysis(self, test_client, authenticated_headers, db_session):
        """Test creating a new coverage analysis."""
        payload = {
            "annual_income": 75000.00,
            "income_multiplier": 10.0,
            "outstanding_debts": 250000.00,
            "children_count": 2,
            "education_cost_per_child": 100000.00,
            "funeral_costs": 5000.00,
            "existing_assets": 50000.00,
            "notes": "Family needs analysis"
        }

        response = await test_client.post(
            "/api/v1/protection/coverage-analysis",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()

        assert Decimal(data["annual_income"]) == Decimal("75000.00")
        assert Decimal(data["income_multiplier"]) == Decimal("10.0")
        assert Decimal(data["outstanding_debts"]) == Decimal("250000.00")
        assert data["children_count"] == 2
        assert Decimal(data["education_cost_per_child"]) == Decimal("100000.00")
        assert Decimal(data["funeral_costs"]) == Decimal("5000.00")
        assert Decimal(data["existing_assets"]) == Decimal("50000.00")
        assert data["notes"] == "Family needs analysis"

        # Check calculated fields
        # recommended_cover = (75000 * 10) + 250000 + (2 * 100000) + 5000 - 50000 = 1,155,000
        assert Decimal(data["recommended_cover"]) == Decimal('1155000.00')
        assert Decimal(data["current_total_cover"]) == Decimal('0.00')  # No policies
        assert Decimal(data["coverage_gap"]) == Decimal('1155000.00')

        assert "id" in data
        assert "calculation_date" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_coverage_analysis_with_policy(self, test_client, authenticated_headers, test_user, db_session):
        """Test creating coverage analysis when user has active policies."""
        # Create a test policy
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Test Provider",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal('500000.00'),
            currency=Currency.GBP,
            cover_amount_gbp=Decimal('500000.00'),
            cover_amount_zar=Decimal('0.00'),
            premium_amount=Decimal('50.00'),
            premium_frequency=PremiumFrequency.MONTHLY,
            annual_premium=Decimal('600.00'),
            start_date=date(2023, 1, 1),
            end_date=date(2043, 1, 1),
            written_in_trust=False,
            status=PolicyStatus.ACTIVE,
            uk_iht_impact=True,
            sa_estate_duty_impact=False,
            critical_illness_rider=False,
            waiver_of_premium=False,
            is_deleted=False
        )
        policy.set_policy_number("TEST-POL-001")
        db_session.add(policy)
        await db_session.commit()  # Commit policy first to get ID
        await db_session.refresh(policy)

        # Add beneficiary
        beneficiary = PolicyBeneficiary(
            policy_id=policy.id,
            beneficiary_relationship=BeneficiaryRelationship.SPOUSE,
            percentage=Decimal('100.00')
        )
        beneficiary.set_name("Test Beneficiary")
        beneficiary.set_date_of_birth(date(1985, 6, 15))
        beneficiary.set_address("123 Test St")
        db_session.add(beneficiary)
        await db_session.commit()

        payload = {
            "annual_income": 75000.00,
            "income_multiplier": 10.0,
            "outstanding_debts": 250000.00,
            "children_count": 2,
            "education_cost_per_child": 100000.00,
            "funeral_costs": 5000.00,
            "existing_assets": 50000.00
        }

        response = await test_client.post(
            "/api/v1/protection/coverage-analysis",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()

        # recommended_cover = 1,155,000 (same calculation)
        # current_total_cover = 500,000 (from test_policy)
        # coverage_gap = 655,000
        assert Decimal(data["recommended_cover"]) == Decimal('1155000.00')
        assert Decimal(data["current_total_cover"]) == Decimal('500000.00')
        assert Decimal(data["coverage_gap"]) == Decimal('655000.00')

    async def test_create_coverage_analysis_validation_negative_income(self, test_client, authenticated_headers):
        """Test validation error for negative annual income."""
        payload = {
            "annual_income": -75000.00,
            "income_multiplier": 10.0,
            "outstanding_debts": 250000.00,
            "children_count": 2,
            "education_cost_per_child": 100000.00,
            "funeral_costs": 5000.00,
            "existing_assets": 50000.00
        }

        response = await test_client.post(
            "/api/v1/protection/coverage-analysis",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Pydantic validation error

    async def test_create_coverage_analysis_validation_zero_multiplier(self, test_client, authenticated_headers):
        """Test validation error for zero income multiplier."""
        payload = {
            "annual_income": 75000.00,
            "income_multiplier": 0.0,
            "outstanding_debts": 250000.00,
            "children_count": 2,
            "education_cost_per_child": 100000.00,
            "funeral_costs": 5000.00,
            "existing_assets": 50000.00
        }

        response = await test_client.post(
            "/api/v1/protection/coverage-analysis",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Pydantic validation error

    async def test_create_coverage_analysis_validation_negative_children(self, test_client, authenticated_headers):
        """Test validation error for negative children count."""
        payload = {
            "annual_income": 75000.00,
            "income_multiplier": 10.0,
            "outstanding_debts": 250000.00,
            "children_count": -1,
            "education_cost_per_child": 100000.00,
            "funeral_costs": 5000.00,
            "existing_assets": 50000.00
        }

        response = await test_client.post(
            "/api/v1/protection/coverage-analysis",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Pydantic validation error

    async def test_create_coverage_analysis_requires_auth(self, test_client):
        """Test that creating coverage analysis requires authentication."""
        payload = {
            "annual_income": 75000.00,
            "income_multiplier": 10.0,
            "outstanding_debts": 250000.00,
            "children_count": 2,
            "education_cost_per_child": 100000.00,
            "funeral_costs": 5000.00,
            "existing_assets": 50000.00
        }

        response = await test_client.post(
            "/api/v1/protection/coverage-analysis",
            json=payload
        )

        assert response.status_code == 401


# ============================================================================
# GET COVERAGE SUMMARY TESTS
# ============================================================================

@pytest.mark.asyncio
class TestGetCoverageSummary:
    """Tests for GET /api/v1/protection/coverage-analysis/summary"""

    async def test_get_coverage_summary_with_analysis(self, test_client, authenticated_headers, test_user, db_session):
        """Test getting coverage summary when analysis exists."""
        # Create test policy
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Test Provider",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal('500000.00'),
            currency=Currency.GBP,
            cover_amount_gbp=Decimal('500000.00'),
            cover_amount_zar=Decimal('0.00'),
            premium_amount=Decimal('50.00'),
            premium_frequency=PremiumFrequency.MONTHLY,
            annual_premium=Decimal('600.00'),
            start_date=date(2023, 1, 1),
            end_date=date(2043, 1, 1),
            written_in_trust=False,
            status=PolicyStatus.ACTIVE,
            uk_iht_impact=True,
            sa_estate_duty_impact=False,
            critical_illness_rider=False,
            waiver_of_premium=False,
            is_deleted=False
        )
        policy.set_policy_number("TEST-POL-001")
        db_session.add(policy)
        await db_session.commit()  # Commit policy first to get ID
        await db_session.refresh(policy)

        beneficiary = PolicyBeneficiary(
            policy_id=policy.id,
            beneficiary_relationship=BeneficiaryRelationship.SPOUSE,
            percentage=Decimal('100.00')
        )
        beneficiary.set_name("Test Beneficiary")
        beneficiary.set_date_of_birth(date(1985, 6, 15))
        beneficiary.set_address("123 Test St")
        db_session.add(beneficiary)

        # Create test analysis
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal('75000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('250000.00'),
            children_count=2,
            education_cost_per_child=Decimal('100000.00'),
            funeral_costs=Decimal('5000.00'),
            existing_assets=Decimal('50000.00'),
            recommended_cover=Decimal('1155000.00'),
            current_total_cover=Decimal('0.00'),
            coverage_gap=Decimal('1155000.00'),
            notes="Test analysis",
            effective_from=datetime.utcnow(),
            effective_to=None
        )
        db_session.add(analysis)
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/protection/coverage-analysis/summary",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["analysis_date"] is not None
        assert Decimal(data["annual_income"]) == Decimal('75000.00')
        assert Decimal(data["outstanding_debts"]) == Decimal('250000.00')
        assert data["children_count"] == 2

        # With the policy, current_total_cover = 500000
        # recommended = 1005000, gap = 505000
        assert Decimal(data["recommended_cover"]) == Decimal('1155000.00')
        assert Decimal(data["current_total_cover"]) == Decimal('500000.00')
        assert Decimal(data["coverage_gap"]) == Decimal('655000.00')

        # gap_percentage = (655000 / 1155000) * 100 = ~56.7%
        assert float(data["gap_percentage"]) > 56.0
        assert data["status"] == "UNDER_INSURED"
        assert data["policies_count"] == 1

    async def test_get_coverage_summary_without_analysis(self, test_client, authenticated_headers, test_user, db_session):
        """Test getting coverage summary when no analysis exists."""
        # Create test policy
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Test Provider",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal('500000.00'),
            currency=Currency.GBP,
            cover_amount_gbp=Decimal('500000.00'),
            cover_amount_zar=Decimal('0.00'),
            premium_amount=Decimal('50.00'),
            premium_frequency=PremiumFrequency.MONTHLY,
            annual_premium=Decimal('600.00'),
            start_date=date(2023, 1, 1),
            end_date=date(2043, 1, 1),
            written_in_trust=False,
            status=PolicyStatus.ACTIVE,
            uk_iht_impact=True,
            sa_estate_duty_impact=False,
            critical_illness_rider=False,
            waiver_of_premium=False,
            is_deleted=False
        )
        policy.set_policy_number("TEST-POL-001")
        db_session.add(policy)
        await db_session.commit()  # Commit policy first to get ID
        await db_session.refresh(policy)

        beneficiary = PolicyBeneficiary(
            policy_id=policy.id,
            beneficiary_relationship=BeneficiaryRelationship.SPOUSE,
            percentage=Decimal('100.00')
        )
        beneficiary.set_name("Test Beneficiary")
        beneficiary.set_date_of_birth(date(1985, 6, 15))
        beneficiary.set_address("123 Test St")
        db_session.add(beneficiary)
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/protection/coverage-analysis/summary",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        # No analysis, so these should be None
        assert data["analysis_date"] is None
        assert data["annual_income"] is None
        assert data["outstanding_debts"] is None
        assert data["children_count"] is None

        # But current coverage should still be calculated
        assert Decimal(data["recommended_cover"]) == Decimal('0.00')
        assert Decimal(data["current_total_cover"]) == Decimal('500000.00')
        # Gap = 0 - 500000 = -500000 (over-insured against 0 recommended)
        assert Decimal(data["coverage_gap"]) == Decimal('-500000.00')
        assert data["policies_count"] == 1

    async def test_get_coverage_summary_no_policies_no_analysis(self, test_client, authenticated_headers):
        """Test getting coverage summary with no policies and no analysis."""
        response = await test_client.get(
            "/api/v1/protection/coverage-analysis/summary",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["analysis_date"] is None
        assert Decimal(data["recommended_cover"]) == Decimal('0.00')
        assert Decimal(data["current_total_cover"]) == Decimal('0.00')
        assert Decimal(data["coverage_gap"]) == Decimal('0.00')
        assert data["policies_count"] == 0

    async def test_get_coverage_summary_requires_auth(self, test_client):
        """Test that getting coverage summary requires authentication."""
        response = await test_client.get("/api/v1/protection/coverage-analysis/summary")

        assert response.status_code == 401


# ============================================================================
# LIST HISTORICAL ANALYSES TESTS
# ============================================================================

@pytest.mark.asyncio
class TestListHistoricalAnalyses:
    """Tests for GET /api/v1/protection/coverage-analysis"""

    async def test_list_historical_analyses(self, test_client, authenticated_headers, test_user, db_session):
        """Test listing all historical coverage analyses."""
        # Create current analysis
        current_analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal('75000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('250000.00'),
            children_count=2,
            education_cost_per_child=Decimal('100000.00'),
            funeral_costs=Decimal('5000.00'),
            existing_assets=Decimal('50000.00'),
            recommended_cover=Decimal('1155000.00'),
            current_total_cover=Decimal('0.00'),
            coverage_gap=Decimal('1155000.00'),
            notes="Current analysis",
            effective_from=datetime.utcnow(),
            effective_to=None
        )
        db_session.add(current_analysis)

        # Create old analysis
        old_analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today() - timedelta(days=30),
            annual_income=Decimal('70000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('200000.00'),
            children_count=1,
            education_cost_per_child=Decimal('100000.00'),
            funeral_costs=Decimal('5000.00'),
            existing_assets=Decimal('30000.00'),
            recommended_cover=Decimal('975000.00'),
            current_total_cover=Decimal('0.00'),
            coverage_gap=Decimal('975000.00'),
            effective_from=datetime.utcnow() - timedelta(days=30),
            effective_to=datetime.utcnow() - timedelta(days=1)
        )
        db_session.add(old_analysis)
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/protection/coverage-analysis",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2
        # Should be ordered by effective_from DESC (newest first)
        assert Decimal(data[0]["annual_income"]) == Decimal('75000.00')  # Current analysis
        assert Decimal(data[1]["annual_income"]) == Decimal('70000.00')  # Old analysis

    async def test_list_historical_analyses_empty(self, test_client, authenticated_headers):
        """Test listing historical analyses when none exist."""
        response = await test_client.get(
            "/api/v1/protection/coverage-analysis",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 0

    async def test_list_historical_analyses_requires_auth(self, test_client):
        """Test that listing analyses requires authentication."""
        response = await test_client.get("/api/v1/protection/coverage-analysis")

        assert response.status_code == 401


# ============================================================================
# GET SPECIFIC ANALYSIS TESTS
# ============================================================================

@pytest.mark.asyncio
class TestGetAnalysisById:
    """Tests for GET /api/v1/protection/coverage-analysis/{id}"""

    async def test_get_analysis_by_id(self, test_client, authenticated_headers, test_user, db_session):
        """Test getting a specific coverage analysis by ID."""
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal('75000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('250000.00'),
            children_count=2,
            education_cost_per_child=Decimal('100000.00'),
            funeral_costs=Decimal('5000.00'),
            existing_assets=Decimal('50000.00'),
            recommended_cover=Decimal('1155000.00'),
            current_total_cover=Decimal('0.00'),
            coverage_gap=Decimal('1155000.00'),
            notes="Test analysis",
            effective_from=datetime.utcnow(),
            effective_to=None
        )
        db_session.add(analysis)
        await db_session.commit()
        await db_session.refresh(analysis)

        response = await test_client.get(
            f"/api/v1/protection/coverage-analysis/{analysis.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(analysis.id)
        assert Decimal(data["annual_income"]) == Decimal('75000.00')
        assert data["children_count"] == 2
        assert data["notes"] == "Test analysis"

    async def test_get_analysis_by_id_not_found(self, test_client, authenticated_headers):
        """Test getting non-existent analysis returns 404."""
        fake_id = uuid4()

        response = await test_client.get(
            f"/api/v1/protection/coverage-analysis/{fake_id}",
            headers=authenticated_headers
        )

        assert response.status_code == 404

    async def test_get_analysis_by_id_wrong_user(self, test_client, test_user, db_session):
        """Test getting analysis owned by another user returns 403."""
        # Create analysis for first user
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal('75000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('250000.00'),
            children_count=2,
            education_cost_per_child=Decimal('100000.00'),
            funeral_costs=Decimal('5000.00'),
            existing_assets=Decimal('50000.00'),
            recommended_cover=Decimal('1155000.00'),
            current_total_cover=Decimal('0.00'),
            coverage_gap=Decimal('1155000.00'),
            notes="Test analysis",
            effective_from=datetime.utcnow(),
            effective_to=None
        )
        db_session.add(analysis)
        await db_session.commit()
        await db_session.refresh(analysis)

        # Create another user
        from models.user import User, UserStatus, CountryPreference
        from utils.password import hash_password

        other_user = User(
            email="other@example.com",
            password_hash=hash_password("password123"),
            first_name="Other",
            last_name="User",
            country_preference=CountryPreference.UK,
            status=UserStatus.ACTIVE,
            email_verified=True,
            terms_accepted_at=datetime.utcnow(),
            marketing_consent=False
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Create token and session for other user
        from utils.jwt import generate_access_token, generate_refresh_token, get_token_jti
        from services.session import session_service

        access_token = generate_access_token(other_user.id)
        refresh_token = generate_refresh_token(other_user.id)
        access_token_jti = get_token_jti(access_token)
        refresh_token_jti = get_token_jti(refresh_token)

        await session_service.create_session(
            db=db_session,
            user_id=other_user.id,
            refresh_token_jti=refresh_token_jti,
            access_token_jti=access_token_jti,
            device_info="Test Device",
            ip_address="127.0.0.1",
        )

        response = await test_client.get(
            f"/api/v1/protection/coverage-analysis/{analysis.id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 403

    async def test_get_analysis_by_id_requires_auth(self, test_client, test_user, db_session):
        """Test that getting analysis by ID requires authentication."""
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal('75000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('250000.00'),
            children_count=2,
            education_cost_per_child=Decimal('100000.00'),
            funeral_costs=Decimal('5000.00'),
            existing_assets=Decimal('50000.00'),
            recommended_cover=Decimal('1155000.00'),
            current_total_cover=Decimal('0.00'),
            coverage_gap=Decimal('1155000.00'),
            effective_from=datetime.utcnow(),
            effective_to=None
        )
        db_session.add(analysis)
        await db_session.commit()
        await db_session.refresh(analysis)

        response = await test_client.get(
            f"/api/v1/protection/coverage-analysis/{analysis.id}"
        )

        assert response.status_code == 401


# ============================================================================
# UPDATE ANALYSIS TESTS
# ============================================================================

@pytest.mark.asyncio
class TestUpdateCoverageAnalysis:
    """Tests for PUT /api/v1/protection/coverage-analysis/{id}"""

    async def test_update_coverage_analysis(self, test_client, authenticated_headers, test_user, db_session):
        """Test updating an existing coverage analysis."""
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal('75000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('250000.00'),
            children_count=2,
            education_cost_per_child=Decimal('100000.00'),
            funeral_costs=Decimal('5000.00'),
            existing_assets=Decimal('50000.00'),
            recommended_cover=Decimal('1155000.00'),
            current_total_cover=Decimal('0.00'),
            coverage_gap=Decimal('1155000.00'),
            notes="Original analysis",
            effective_from=datetime.utcnow(),
            effective_to=None
        )
        db_session.add(analysis)
        await db_session.commit()
        await db_session.refresh(analysis)

        payload = {
            "annual_income": 80000.00,
            "income_multiplier": 10.0,
            "outstanding_debts": 200000.00,
            "children_count": 3,
            "education_cost_per_child": 100000.00,
            "funeral_costs": 6000.00,
            "existing_assets": 60000.00,
            "notes": "Updated analysis"
        }

        response = await test_client.put(
            f"/api/v1/protection/coverage-analysis/{analysis.id}",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(analysis.id)
        assert Decimal(data["annual_income"]) == Decimal('80000.00')
        assert data["children_count"] == 3
        assert data["notes"] == "Updated analysis"

        # Check recalculated fields
        # recommended_cover = (80000 * 10) + 200000 + (3 * 100000) + 6000 - 60000 = 1,246,000
        assert Decimal(data["recommended_cover"]) == Decimal('1246000.00')

    async def test_update_coverage_analysis_not_found(self, test_client, authenticated_headers):
        """Test updating non-existent analysis returns 404."""
        fake_id = uuid4()

        payload = {
            "annual_income": 80000.00,
            "income_multiplier": 10.0,
            "outstanding_debts": 200000.00,
            "children_count": 2,
            "education_cost_per_child": 100000.00,
            "funeral_costs": 5000.00,
            "existing_assets": 50000.00
        }

        response = await test_client.put(
            f"/api/v1/protection/coverage-analysis/{fake_id}",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 404

    async def test_update_coverage_analysis_wrong_user(self, test_client, test_user, db_session):
        """Test updating analysis owned by another user returns 400 (validation error from service)."""
        # Create analysis for first user
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal('75000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('250000.00'),
            children_count=2,
            education_cost_per_child=Decimal('100000.00'),
            funeral_costs=Decimal('5000.00'),
            existing_assets=Decimal('50000.00'),
            recommended_cover=Decimal('1155000.00'),
            current_total_cover=Decimal('0.00'),
            coverage_gap=Decimal('1155000.00'),
            effective_from=datetime.utcnow(),
            effective_to=None
        )
        db_session.add(analysis)
        await db_session.commit()
        await db_session.refresh(analysis)

        # Create another user
        from models.user import User, UserStatus, CountryPreference
        from utils.password import hash_password

        other_user = User(
            email="other2@example.com",
            password_hash=hash_password("password123"),
            first_name="Other",
            last_name="User",
            country_preference=CountryPreference.UK,
            status=UserStatus.ACTIVE,
            email_verified=True,
            terms_accepted_at=datetime.utcnow(),
            marketing_consent=False
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Create token and session for other user
        from utils.jwt import generate_access_token, generate_refresh_token, get_token_jti
        from services.session import session_service

        access_token = generate_access_token(other_user.id)
        refresh_token = generate_refresh_token(other_user.id)
        access_token_jti = get_token_jti(access_token)
        refresh_token_jti = get_token_jti(refresh_token)

        await session_service.create_session(
            db=db_session,
            user_id=other_user.id,
            refresh_token_jti=refresh_token_jti,
            access_token_jti=access_token_jti,
            device_info="Test Device",
            ip_address="127.0.0.1",
        )

        payload = {
            "annual_income": 80000.00,
            "income_multiplier": 10.0,
            "outstanding_debts": 200000.00,
            "children_count": 2,
            "education_cost_per_child": 100000.00,
            "funeral_costs": 5000.00,
            "existing_assets": 50000.00
        }

        response = await test_client.put(
            f"/api/v1/protection/coverage-analysis/{analysis.id}",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 400  # Service raises ValidationError for permission issue

    async def test_update_coverage_analysis_validation_error(self, test_client, authenticated_headers, test_user, db_session):
        """Test updating with invalid data returns 422 (Pydantic validation)."""
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal('75000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('250000.00'),
            children_count=2,
            education_cost_per_child=Decimal('100000.00'),
            funeral_costs=Decimal('5000.00'),
            existing_assets=Decimal('50000.00'),
            recommended_cover=Decimal('1155000.00'),
            current_total_cover=Decimal('0.00'),
            coverage_gap=Decimal('1155000.00'),
            effective_from=datetime.utcnow(),
            effective_to=None
        )
        db_session.add(analysis)
        await db_session.commit()
        await db_session.refresh(analysis)

        payload = {
            "annual_income": -80000.00,  # Invalid: negative
            "income_multiplier": 10.0,
            "outstanding_debts": 200000.00,
            "children_count": 2,
            "education_cost_per_child": 100000.00,
            "funeral_costs": 5000.00,
            "existing_assets": 50000.00
        }

        response = await test_client.put(
            f"/api/v1/protection/coverage-analysis/{analysis.id}",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Pydantic validation error

    async def test_update_coverage_analysis_requires_auth(self, test_client, test_user, db_session):
        """Test that updating analysis requires authentication."""
        analysis = CoverageNeedsAnalysis(
            user_id=test_user.id,
            calculation_date=date.today(),
            annual_income=Decimal('75000.00'),
            income_multiplier=Decimal('10.0'),
            outstanding_debts=Decimal('250000.00'),
            children_count=2,
            education_cost_per_child=Decimal('100000.00'),
            funeral_costs=Decimal('5000.00'),
            existing_assets=Decimal('50000.00'),
            recommended_cover=Decimal('1155000.00'),
            current_total_cover=Decimal('0.00'),
            coverage_gap=Decimal('1155000.00'),
            effective_from=datetime.utcnow(),
            effective_to=None
        )
        db_session.add(analysis)
        await db_session.commit()
        await db_session.refresh(analysis)

        payload = {
            "annual_income": 80000.00,
            "income_multiplier": 10.0,
            "outstanding_debts": 200000.00,
            "children_count": 2,
            "education_cost_per_child": 100000.00,
            "funeral_costs": 5000.00,
            "existing_assets": 50000.00
        }

        response = await test_client.put(
            f"/api/v1/protection/coverage-analysis/{analysis.id}",
            json=payload
        )

        assert response.status_code == 401
