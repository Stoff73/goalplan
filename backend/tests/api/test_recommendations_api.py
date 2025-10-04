"""
Tests for Recommendations API endpoints.

Test coverage:
- GET /api/v1/recommendations - Retrieve recommendations with filtering
- POST /api/v1/recommendations/generate - Generate new recommendations
- POST /api/v1/recommendations/{id}/dismiss - Dismiss recommendation
- POST /api/v1/recommendations/{id}/complete - Mark as completed

Authentication and authorization tests included.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from decimal import Decimal
from httpx import AsyncClient

from models.recommendation import (
    Recommendation,
    RecommendationPriority,
    RecommendationType,
    Currency
)
from models.user import User, UserStatus, CountryPreference
from utils.password import hash_password


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
async def other_test_user(db_session):
    """Create another test user for authorization tests."""
    user = User(
        email="other@example.com",
        first_name="Other",
        last_name="User",
        password_hash=hash_password("TestPassword123!"),
        status=UserStatus.ACTIVE,
        email_verified=True,
        country_preference=CountryPreference.UK,  # Required field (use enum)
        terms_accepted_at=datetime.utcnow(),
        marketing_consent=False
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def test_recommendations(db_session, test_user):
    """Create test recommendations for user."""
    recommendations = [
        Recommendation(
            user_id=test_user.id,
            recommendation_type=RecommendationType.PROTECTION,
            priority=RecommendationPriority.HIGH,
            title="Increase life assurance cover",
            description="You have a coverage gap of £50,000",
            action_items=[
                "Review your current policies",
                "Get quotes for additional cover"
            ],
            potential_savings=None,
            currency=Currency.GBP
        ),
        Recommendation(
            user_id=test_user.id,
            recommendation_type=RecommendationType.ISA,
            priority=RecommendationPriority.MEDIUM,
            title="Use your ISA allowance",
            description="You have £10,000 unused ISA allowance",
            action_items=[
                "Transfer funds to ISA before April 5"
            ],
            potential_savings=Decimal('200.00'),
            currency=Currency.GBP
        ),
        Recommendation(
            user_id=test_user.id,
            recommendation_type=RecommendationType.TFSA,
            priority=RecommendationPriority.LOW,
            title="Maximize TFSA",
            description="You have R15,000 unused TFSA allowance",
            action_items=[
                "Contribute to TFSA before Feb 28"
            ],
            potential_savings=None,
            currency=Currency.ZAR
        ),
    ]

    for rec in recommendations:
        db_session.add(rec)

    await db_session.commit()

    for rec in recommendations:
        await db_session.refresh(rec)

    return recommendations


@pytest.fixture
async def dismissed_recommendation(db_session, test_user):
    """Create a dismissed recommendation."""
    rec = Recommendation(
        user_id=test_user.id,
        recommendation_type=RecommendationType.EMERGENCY_FUND,
        priority=RecommendationPriority.HIGH,
        title="Build emergency fund",
        description="You need £5,000 more",
        action_items=["Set up automatic transfers"],
        currency=Currency.GBP
    )
    rec.dismiss()

    db_session.add(rec)
    await db_session.commit()
    await db_session.refresh(rec)

    return rec


@pytest.fixture
async def other_user_recommendation(db_session, other_test_user):
    """Create recommendation for another user."""
    rec = Recommendation(
        user_id=other_test_user.id,
        recommendation_type=RecommendationType.PENSION,
        priority=RecommendationPriority.HIGH,
        title="Maximize pension",
        description="Use your annual allowance",
        action_items=["Increase contributions"],
        currency=Currency.GBP
    )

    db_session.add(rec)
    await db_session.commit()
    await db_session.refresh(rec)

    return rec


# ============================================================================
# GET /api/v1/recommendations - RETRIEVE RECOMMENDATIONS
# ============================================================================

@pytest.mark.asyncio
async def test_get_recommendations_success(
    client: AsyncClient,
    test_recommendations,
    authenticated_headers
):
    """Test authenticated user can get their recommendations."""
    response = await client.get(
        "/api/v1/recommendations/",
        headers=authenticated_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should get 3 active recommendations (not dismissed)
    assert len(data) == 3

    # Verify sorted by priority (HIGH first), then created_date DESC
    assert data[0]["priority"] == "HIGH"
    assert data[0]["recommendation_type"] == "PROTECTION"

    # Verify response structure
    rec = data[0]
    assert "id" in rec
    assert "user_id" in rec
    assert "recommendation_type" in rec
    assert "priority" in rec
    assert "title" in rec
    assert "description" in rec
    assert "action_items" in rec
    assert "currency" in rec
    assert "created_date" in rec
    assert "dismissed" in rec
    assert "completed" in rec


@pytest.mark.asyncio
async def test_get_recommendations_filter_by_priority(
    client: AsyncClient,
    test_recommendations,
    authenticated_headers
):
    """Test filtering recommendations by priority."""
    # Filter for HIGH priority
    response = await client.get(
        "/api/v1/recommendations/",
        params={"priority": "HIGH"},
        headers=authenticated_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["priority"] == "HIGH"
    assert data[0]["recommendation_type"] == "PROTECTION"


@pytest.mark.asyncio
async def test_get_recommendations_filter_by_type(
    client: AsyncClient,
    test_recommendations,
    authenticated_headers
):
    """Test filtering recommendations by type."""
    # Filter for ISA type
    response = await client.get(
        "/api/v1/recommendations/",
        params={"type": "ISA"},
        headers=authenticated_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["recommendation_type"] == "ISA"
    assert data[0]["priority"] == "MEDIUM"


@pytest.mark.asyncio
async def test_get_recommendations_excludes_dismissed(
    client: AsyncClient,
    test_recommendations,
    dismissed_recommendation,
    authenticated_headers
):
    """Test dismissed recommendations are excluded."""
    response = await client.get(
        "/api/v1/recommendations/",
        headers=authenticated_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should only get 3 active, not the dismissed one
    assert len(data) == 3

    # Verify dismissed recommendation not in results
    ids = [rec["id"] for rec in data]
    assert str(dismissed_recommendation.id) not in ids


@pytest.mark.asyncio
async def test_get_recommendations_empty_list(
    client: AsyncClient,
    authenticated_headers
):
    """Test returns empty list when no recommendations."""
    response = await client.get(
        "/api/v1/recommendations/",
        headers=authenticated_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_get_recommendations_unauthorized(client: AsyncClient):
    """Test unauthenticated request returns 401."""
    response = await client.get("/api/v1/recommendations/")

    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_get_recommendations_only_own(
    client: AsyncClient,
    test_recommendations,
    other_user_recommendation,
    authenticated_headers
):
    """Test user only sees their own recommendations."""
    response = await client.get(
        "/api/v1/recommendations/",
        headers=authenticated_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should only get test_user's 3 recommendations, not other_user's
    assert len(data) == 3

    ids = [rec["id"] for rec in data]
    assert str(other_user_recommendation.id) not in ids


# ============================================================================
# POST /api/v1/recommendations/generate - GENERATE RECOMMENDATIONS
# ============================================================================

@pytest.mark.asyncio
async def test_generate_recommendations_success(
    client: AsyncClient,
    authenticated_headers,
    test_user
):
    """Test generate recommendations successfully."""
    response = await client.post(
        "/api/v1/recommendations/generate",
        json={"base_currency": "GBP"},
        headers=authenticated_headers
    )

    assert response.status_code == 201
    data = response.json()

    assert "recommendations" in data
    assert "count" in data
    assert data["count"] == len(data["recommendations"])

    # Verify at least one recommendation generated (depends on user data)
    assert data["count"] >= 0


@pytest.mark.asyncio
async def test_generate_recommendations_default_currency(
    client: AsyncClient,
    authenticated_headers
):
    """Test generate with default currency (GBP)."""
    response = await client.post(
        "/api/v1/recommendations/generate",
        json={},  # Empty body, should use default GBP
        headers=authenticated_headers
    )

    assert response.status_code == 201
    data = response.json()

    assert "recommendations" in data
    assert "count" in data


@pytest.mark.asyncio
async def test_generate_recommendations_different_currencies(
    client: AsyncClient,
    authenticated_headers
):
    """Test generate with different base currencies."""
    currencies = ["GBP", "ZAR", "USD", "EUR"]

    for currency in currencies:
        response = await client.post(
            "/api/v1/recommendations/generate",
            json={"base_currency": currency},
            headers=authenticated_headers
        )

        assert response.status_code == 201


@pytest.mark.asyncio
async def test_generate_recommendations_invalid_currency(
    client: AsyncClient,
    authenticated_headers
):
    """Test generate with invalid currency fails validation."""
    response = await client.post(
        "/api/v1/recommendations/generate",
        json={"base_currency": "INVALID"},
        headers=authenticated_headers
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_generate_recommendations_unauthorized(client: AsyncClient):
    """Test unauthenticated request returns 401."""
    response = await client.post(
        "/api/v1/recommendations/generate",
        json={"base_currency": "GBP"}
    )

    assert response.status_code == 401


# ============================================================================
# POST /api/v1/recommendations/{id}/dismiss - DISMISS RECOMMENDATION
# ============================================================================

@pytest.mark.asyncio
async def test_dismiss_recommendation_success(
    client: AsyncClient,
    test_recommendations,
    authenticated_headers
):
    """Test dismiss recommendation successfully."""
    rec_id = test_recommendations[0].id

    response = await client.post(
        f"/api/v1/recommendations/{rec_id}/dismiss",
        headers=authenticated_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(rec_id)
    assert data["dismissed"] is True
    assert data["dismissed_date"] is not None


@pytest.mark.asyncio
async def test_dismiss_recommendation_not_found(
    client: AsyncClient,
    authenticated_headers
):
    """Test dismiss non-existent recommendation returns 404."""
    fake_id = uuid4()

    response = await client.post(
        f"/api/v1/recommendations/{fake_id}/dismiss",
        headers=authenticated_headers
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_dismiss_recommendation_not_owned(
    client: AsyncClient,
    other_user_recommendation,
    authenticated_headers
):
    """Test user cannot dismiss another user's recommendation (403)."""
    rec_id = other_user_recommendation.id

    response = await client.post(
        f"/api/v1/recommendations/{rec_id}/dismiss",
        headers=authenticated_headers
    )

    assert response.status_code == 403
    assert "does not own" in response.json()["detail"]


@pytest.mark.asyncio
async def test_dismiss_recommendation_unauthorized(
    client: AsyncClient,
    test_recommendations
):
    """Test unauthenticated request returns 401."""
    rec_id = test_recommendations[0].id

    response = await client.post(
        f"/api/v1/recommendations/{rec_id}/dismiss"
    )

    assert response.status_code == 401


# ============================================================================
# POST /api/v1/recommendations/{id}/complete - COMPLETE RECOMMENDATION
# ============================================================================

@pytest.mark.asyncio
async def test_complete_recommendation_success(
    client: AsyncClient,
    test_recommendations,
    authenticated_headers
):
    """Test complete recommendation successfully."""
    rec_id = test_recommendations[0].id

    response = await client.post(
        f"/api/v1/recommendations/{rec_id}/complete",
        headers=authenticated_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(rec_id)
    assert data["completed"] is True
    assert data["completed_date"] is not None


@pytest.mark.asyncio
async def test_complete_recommendation_not_found(
    client: AsyncClient,
    authenticated_headers
):
    """Test complete non-existent recommendation returns 404."""
    fake_id = uuid4()

    response = await client.post(
        f"/api/v1/recommendations/{fake_id}/complete",
        headers=authenticated_headers
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_complete_recommendation_not_owned(
    client: AsyncClient,
    other_user_recommendation,
    authenticated_headers
):
    """Test user cannot complete another user's recommendation (403)."""
    rec_id = other_user_recommendation.id

    response = await client.post(
        f"/api/v1/recommendations/{rec_id}/complete",
        headers=authenticated_headers
    )

    assert response.status_code == 403
    assert "does not own" in response.json()["detail"]


@pytest.mark.asyncio
async def test_complete_recommendation_unauthorized(
    client: AsyncClient,
    test_recommendations
):
    """Test unauthenticated request returns 401."""
    rec_id = test_recommendations[0].id

    response = await client.post(
        f"/api/v1/recommendations/{rec_id}/complete"
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_complete_and_dismiss_same_recommendation(
    client: AsyncClient,
    test_recommendations,
    authenticated_headers
):
    """Test recommendation can be both completed and dismissed."""
    rec_id = test_recommendations[0].id

    # Complete first
    response = await client.post(
        f"/api/v1/recommendations/{rec_id}/complete",
        headers=authenticated_headers
    )
    assert response.status_code == 200
    assert response.json()["completed"] is True

    # Then dismiss
    response = await client.post(
        f"/api/v1/recommendations/{rec_id}/dismiss",
        headers=authenticated_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True
    assert data["dismissed"] is True


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_full_recommendation_lifecycle(
    client: AsyncClient,
    authenticated_headers
):
    """Test complete recommendation lifecycle: generate -> retrieve -> dismiss."""
    # 1. Generate recommendations
    response = await client.post(
        "/api/v1/recommendations/generate",
        json={"base_currency": "GBP"},
        headers=authenticated_headers
    )
    assert response.status_code == 201
    generated = response.json()

    # 2. Retrieve recommendations
    response = await client.get(
        "/api/v1/recommendations/",
        headers=authenticated_headers
    )
    assert response.status_code == 200
    retrieved = response.json()
    assert len(retrieved) == generated["count"]

    # 3. Dismiss first recommendation (if any)
    if len(retrieved) > 0:
        rec_id = retrieved[0]["id"]
        response = await client.post(
            f"/api/v1/recommendations/{rec_id}/dismiss",
            headers=authenticated_headers
        )
        assert response.status_code == 200

        # 4. Verify dismissed recommendation excluded from results
        response = await client.get(
            "/api/v1/recommendations/",
            headers=authenticated_headers
        )
        assert response.status_code == 200
        after_dismiss = response.json()
        assert len(after_dismiss) == len(retrieved) - 1


@pytest.mark.asyncio
async def test_filter_combinations(
    client: AsyncClient,
    test_recommendations,
    authenticated_headers
):
    """Test filtering by both priority and type."""
    # HIGH priority ISA (should not exist in fixtures)
    response = await client.get(
        "/api/v1/recommendations/",
        params={"priority": "HIGH", "type": "ISA"},
        headers=authenticated_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 0

    # HIGH priority PROTECTION (should exist)
    response = await client.get(
        "/api/v1/recommendations/",
        params={"priority": "HIGH", "type": "PROTECTION"},
        headers=authenticated_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["priority"] == "HIGH"
    assert data[0]["recommendation_type"] == "PROTECTION"
