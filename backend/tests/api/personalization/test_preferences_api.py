"""
Tests for Personalization Preferences API endpoints.

Test Coverage:
- GET /api/v1/personalization/preferences
- POST /api/v1/personalization/preferences
- POST /api/v1/personalization/behavior/track
- GET /api/v1/personalization/dashboard/personalized
- GET /api/v1/personalization/insights
- GET /api/v1/personalization/behavior/analysis
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestPreferencesAPI:
    """Test user preference management endpoints."""

    @pytest.mark.asyncio
    async def test_get_preferences_returns_defaults(
        self,
        test_client: AsyncClient,
        auth_headers: dict
    ):
        """Test GET /api/v1/personalization/preferences returns defaults for new user."""
        response = await test_client.get(
            "/api/v1/personalization/preferences",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "preferences" in data
        assert data["preferences"]["DEFAULT_CURRENCY"] == "GBP"
        assert data["preferences"]["THEME"] == "light"
        assert data["preferences"]["NOTIFICATION_FREQUENCY"] == "weekly"

    @pytest.mark.asyncio
    async def test_save_preference(
        self,
        test_client: AsyncClient,
        auth_headers: dict
    ):
        """Test POST /api/v1/personalization/preferences creates/updates preference."""
        # Save a preference
        response = await test_client.post(
            "/api/v1/personalization/preferences",
            json={
                "preference_type": "DEFAULT_CURRENCY",
                "preference_value": "USD"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["preference_type"] == "DEFAULT_CURRENCY"
        assert data["preference_value"] == "USD"
        assert "id" in data
        assert "user_id" in data

    @pytest.mark.asyncio
    async def test_save_preference_updates_existing(
        self,
        test_client: AsyncClient,
        auth_headers: dict
    ):
        """Test saving same preference twice updates instead of creating new."""
        # Save first time
        response1 = await test_client.post(
            "/api/v1/personalization/preferences",
            json={
                "preference_type": "THEME",
                "preference_value": "dark"
            },
            headers=auth_headers
        )
        assert response1.status_code == 200
        pref_id_1 = response1.json()["id"]

        # Save second time with different value
        response2 = await test_client.post(
            "/api/v1/personalization/preferences",
            json={
                "preference_type": "THEME",
                "preference_value": "light"
            },
            headers=auth_headers
        )
        assert response2.status_code == 200
        pref_id_2 = response2.json()["id"]

        # Should be same ID (update, not create)
        assert pref_id_1 == pref_id_2
        assert response2.json()["preference_value"] == "light"

    @pytest.mark.asyncio
    async def test_get_preferences_includes_saved_values(
        self,
        test_client: AsyncClient,
        auth_headers: dict
    ):
        """Test GET preferences returns saved values."""
        # Save a custom preference
        await test_client.post(
            "/api/v1/personalization/preferences",
            json={
                "preference_type": "DEFAULT_CURRENCY",
                "preference_value": "EUR"
            },
            headers=auth_headers
        )

        # Get preferences
        response = await test_client.get(
            "/api/v1/personalization/preferences",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should include saved value
        assert data["preferences"]["DEFAULT_CURRENCY"] == "EUR"
        # Should still include defaults for unset preferences
        assert data["preferences"]["THEME"] == "light"


class TestBehaviorTracking:
    """Test behavior tracking endpoints."""

    @pytest.mark.asyncio
    async def test_track_behavior(
        self,
        test_client: AsyncClient,
        auth_headers: dict
    ):
        """Test POST /api/v1/personalization/behavior/track logs action."""
        response = await test_client.post(
            "/api/v1/personalization/behavior/track",
            json={
                "action_type": "PAGE_VIEW",
                "action_context": {
                    "page": "dashboard",
                    "duration": 45
                }
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "tracked"

    @pytest.mark.asyncio
    async def test_behavior_analysis(
        self,
        test_client: AsyncClient,
        auth_headers: dict
    ):
        """Test GET /api/v1/personalization/behavior/analysis returns metrics."""
        # Track some behaviors first
        await test_client.post(
            "/api/v1/personalization/behavior/track",
            json={
                "action_type": "PAGE_VIEW",
                "action_context": {"page": "dashboard"}
            },
            headers=auth_headers
        )

        await test_client.post(
            "/api/v1/personalization/behavior/track",
            json={
                "action_type": "FEATURE_USAGE",
                "action_context": {"feature": "goal_tracking"}
            },
            headers=auth_headers
        )

        # Get analysis
        response = await test_client.get(
            "/api/v1/personalization/behavior/analysis?days=30",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "most_viewed_pages" in data
        assert "most_used_features" in data
        assert "engagement_score" in data
        assert "total_actions" in data
        assert data["total_actions"] >= 2


class TestPersonalizedDashboard:
    """Test personalized dashboard endpoints."""

    @pytest.mark.asyncio
    async def test_get_personalized_dashboard_default(
        self,
        test_client: AsyncClient,
        auth_headers: dict
    ):
        """Test GET /api/v1/personalization/dashboard/personalized returns default layout."""
        response = await test_client.get(
            "/api/v1/personalization/dashboard/personalized",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "widget_order" in data
        assert "visible_widgets" in data
        assert "hidden_widgets" in data

        # Should have default widgets
        assert len(data["widget_order"]) > 0
        assert "net_worth" in data["widget_order"]

    @pytest.mark.asyncio
    async def test_get_personalized_dashboard_with_behavior(
        self,
        test_client: AsyncClient,
        auth_headers: dict
    ):
        """Test dashboard personalizes based on behavior."""
        # Track some page views to influence dashboard
        for _ in range(10):
            await test_client.post(
                "/api/v1/personalization/behavior/track",
                json={
                    "action_type": "PAGE_VIEW",
                    "action_context": {"page": "goals"}
                },
                headers=auth_headers
            )

        for _ in range(5):
            await test_client.post(
                "/api/v1/personalization/behavior/track",
                json={
                    "action_type": "PAGE_VIEW",
                    "action_context": {"page": "savings"}
                },
                headers=auth_headers
            )

        # Get personalized dashboard
        response = await test_client.get(
            "/api/v1/personalization/dashboard/personalized",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Goals should be prioritized (most viewed)
        assert "goals" in data["widget_order"]
        # Most viewed page should be first
        assert data["widget_order"][0] in ["goals", "savings"]


class TestPersonalizedInsights:
    """Test personalized insights endpoints."""

    @pytest.mark.asyncio
    async def test_get_insights(
        self,
        test_client: AsyncClient,
        auth_headers: dict
    ):
        """Test GET /api/v1/personalization/insights generates insights."""
        response = await test_client.get(
            "/api/v1/personalization/insights?limit=5",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) <= 5

        # Check insight structure if any returned
        if len(data) > 0:
            insight = data[0]
            assert "id" in insight
            assert "user_id" in insight
            assert "insight_type" in insight
            assert "insight_text" in insight
            assert "relevance_score" in insight

    @pytest.mark.asyncio
    async def test_insights_ordered_by_relevance(
        self,
        test_client: AsyncClient,
        auth_headers: dict
    ):
        """Test insights are ordered by relevance score."""
        response = await test_client.get(
            "/api/v1/personalization/insights?limit=10",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check insights are in descending relevance order
        if len(data) > 1:
            for i in range(len(data) - 1):
                current_score = float(data[i]["relevance_score"])
                next_score = float(data[i + 1]["relevance_score"])
                assert current_score >= next_score


class TestAuthentication:
    """Test authentication requirements."""

    @pytest.mark.asyncio
    async def test_preferences_requires_auth(self, test_client: AsyncClient):
        """Test preferences endpoint requires authentication."""
        response = await test_client.get("/api/v1/personalization/preferences")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_behavior_tracking_requires_auth(self, test_client: AsyncClient):
        """Test behavior tracking requires authentication."""
        response = await test_client.post(
            "/api/v1/personalization/behavior/track",
            json={
                "action_type": "PAGE_VIEW",
                "action_context": {"page": "dashboard"}
            }
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_dashboard_requires_auth(self, test_client: AsyncClient):
        """Test dashboard endpoint requires authentication."""
        response = await test_client.get(
            "/api/v1/personalization/dashboard/personalized"
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_insights_requires_auth(self, test_client: AsyncClient):
        """Test insights endpoint requires authentication."""
        response = await test_client.get("/api/v1/personalization/insights")
        assert response.status_code == 401
