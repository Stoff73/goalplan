"""
Comprehensive tests for AI Advisory API endpoints.

Tests all 10 endpoints with:
- Authentication and authorization
- Rate limiting
- Input validation
- Error handling
- Success cases
- Mock AI service calls (no actual LLM calls)
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import status
from sqlalchemy import select

from models.user import User, UserStatus
from models.goal import FinancialGoal, GoalStatus, GoalType, GoalPriority
from models.recommendation import Recommendation, RecommendationType, RecommendationPriority, Currency
from models.retirement import UKPension
from models.tax_status import UserTaxStatus
from models.income import UserIncome, IncomeType


@pytest.mark.asyncio
class TestRetirementAdviceEndpoint:
    """Tests for POST /api/v1/ai/retirement-advice."""

    async def test_get_retirement_advice_success(
        self,
        async_client,
        test_user,
        authenticated_headers
    ):
        """Test successful retirement advice generation."""
        # Mock AI service response
        mock_advice = {
            "advice": "You're on track for retirement. Consider increasing contributions by £100/month.",
            "recommendations": [
                {
                    "action": "Increase pension contributions",
                    "reason": "Maximize tax relief",
                    "impact": "Additional £50k in retirement pot"
                }
            ],
            "confidence_score": 0.85,
            "requires_human_review": False,
            "sources": ["UK pension rules"],
            "metadata": {"model": "gpt-4"}
        }

        with patch('api.v1.ai.advisory.AIAdvisoryService') as mock_service:
            mock_service.return_value.generate_retirement_advice = AsyncMock(
                return_value=mock_advice
            )

            response = await async_client.post(
                "/api/v1/ai/retirement-advice",
                headers=authenticated_headers
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "advice" in data
        assert data["confidence_score"] == 0.85
        assert data["requires_human_review"] is False
        assert len(data["recommendations"]) == 1
        assert "disclaimer" in data
        assert data["sources"] == ["UK pension rules"]

    async def test_retirement_advice_unauthorized(self, async_client):
        """Test retirement advice requires authentication."""
        response = await async_client.post("/api/v1/ai/retirement-advice")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_retirement_advice_rate_limit(
        self,
        async_client,
        test_user,
        authenticated_headers
    ):
        """Test rate limiting on retirement advice endpoint."""
        mock_advice = {
            "advice": "Test advice",
            "recommendations": [],
            "confidence_score": 0.9,
            "requires_human_review": False,
            "sources": [],
            "metadata": {}
        }

        with patch('api.v1.ai.advisory.AIAdvisoryService') as mock_service:
            mock_service.return_value.generate_retirement_advice = AsyncMock(
                return_value=mock_advice
            )

            # Make 5 requests (should all succeed)
            for i in range(5):
                response = await async_client.post(
                    "/api/v1/ai/retirement-advice",
                    headers=authenticated_headers
                )
                assert response.status_code == status.HTTP_200_OK

            # 6th request should be rate limited (5/hour limit)
            response = await async_client.post(
                "/api/v1/ai/retirement-advice",
                headers=authenticated_headers
            )
            assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
class TestInvestmentAdviceEndpoint:
    """Tests for POST /api/v1/ai/investment-advice."""

    async def test_get_investment_advice_success(
        self,
        async_client,
        test_user,
        authenticated_headers
    ):
        """Test successful investment advice generation."""
        mock_advice = {
            "advice": "Your portfolio is 80% equities. Consider rebalancing to 60/40.",
            "recommendations": [
                {
                    "action": "Rebalance to 60% equities, 40% bonds",
                    "reason": "Reduce portfolio volatility",
                    "impact": "Lower risk for your age"
                }
            ],
            "confidence_score": 0.80,
            "requires_human_review": False,
            "sources": ["Modern Portfolio Theory"],
            "metadata": {}
        }

        with patch('api.v1.ai.advisory.AIAdvisoryService') as mock_service:
            mock_service.return_value.generate_investment_advice = AsyncMock(
                return_value=mock_advice
            )

            response = await async_client.post(
                "/api/v1/ai/investment-advice",
                headers=authenticated_headers
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "advice" in data
        assert data["confidence_score"] == 0.80
        assert len(data["recommendations"]) == 1


@pytest.mark.asyncio
class TestTaxAdviceEndpoint:
    """Tests for POST /api/v1/ai/tax-advice."""

    async def test_get_tax_advice_success(
        self,
        async_client,
        test_user,
        authenticated_headers
    ):
        """Test successful tax optimization advice generation."""
        mock_advice = {
            "advice": "You're £2,000 from the higher rate threshold. Pension contributions could save £800 in tax.",
            "recommendations": [
                {
                    "action": "Make £2,000 pension contribution",
                    "reason": "Stay below higher rate threshold",
                    "impact": "Save £800 in tax"
                }
            ],
            "confidence_score": 0.90,
            "requires_human_review": False,
            "sources": ["UK Income Tax rates"],
            "metadata": {}
        }

        with patch('api.v1.ai.advisory.AIAdvisoryService') as mock_service:
            mock_service.return_value.generate_tax_optimization_advice = AsyncMock(
                return_value=mock_advice
            )

            response = await async_client.post(
                "/api/v1/ai/tax-advice",
                headers=authenticated_headers
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "advice" in data
        assert data["confidence_score"] == 0.90


@pytest.mark.asyncio
class TestGoalAdviceEndpoint:
    """Tests for POST /api/v1/ai/goal-advice/{goal_id}."""

    async def test_get_goal_advice_success(
        self,
        async_client,
        test_user,
        authenticated_headers,
        db_session
    ):
        """Test successful goal advice generation."""
        # Create a goal for the user
        goal = FinancialGoal(
            user_id=test_user.id,
            goal_name="Emergency Fund",
            goal_type=GoalType.EMERGENCY_FUND,
            target_amount=Decimal("10000.00"),
            current_amount=Decimal("5000.00"),
            target_date=(datetime.utcnow() + timedelta(days=180)).date(),
            status=GoalStatus.IN_PROGRESS
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        mock_advice = {
            "advice": "You need £5,000 more in 6 months. Save £833/month to reach your goal.",
            "recommendations": [
                {
                    "action": "Set up automatic transfer of £833/month",
                    "reason": "Reach goal on schedule",
                    "impact": "Emergency fund fully funded"
                }
            ],
            "confidence_score": 0.95,
            "requires_human_review": False,
            "sources": ["Goal planning best practices"],
            "metadata": {"goal_name": "Emergency Fund"}
        }

        with patch('api.v1.ai.advisory.AIAdvisoryService') as mock_service:
            mock_service.return_value.generate_goal_advice = AsyncMock(
                return_value=mock_advice
            )

            response = await async_client.post(
                f"/api/v1/ai/goal-advice/{goal.id}",
                headers=authenticated_headers
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "advice" in data
        assert data["confidence_score"] == 0.95

    async def test_goal_advice_goal_not_found(
        self,
        async_client,
        test_user,
        authenticated_headers
    ):
        """Test 404 when goal doesn't exist."""
        fake_goal_id = uuid4()

        response = await async_client.post(
            f"/api/v1/ai/goal-advice/{fake_goal_id}",
            headers=authenticated_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    async def test_goal_advice_forbidden(
        self,
        async_client,
        test_user,
        db_session
    ):
        """Test 403 when accessing another user's goal."""
        # Create another user
        other_user = User(
            email="other@example.com",
            hashed_password="hashed",
            first_name="Other",
            last_name="User",
            status=UserStatus.ACTIVE
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Create goal for other user
        goal = FinancialGoal(
            user_id=other_user.id,
            goal_name="Other's Goal",
            goal_type=GoalType.EMERGENCY_FUND,
            target_amount=Decimal("10000.00"),
            target_date=datetime.utcnow().date()
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(goal)

        # Try to access as test_user
        from utils.jwt import create_access_token
        token = create_access_token(str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post(
            f"/api/v1/ai/goal-advice/{goal.id}",
            headers=headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "permission" in response.json()["detail"].lower()


@pytest.mark.asyncio
class TestAskQuestionEndpoint:
    """Tests for POST /api/v1/ai/ask."""

    async def test_ask_question_success(
        self,
        async_client,
        test_user,
        authenticated_headers
    ):
        """Test successful question answering."""
        mock_advice = {
            "advice": "For your situation, I'd recommend contributing £500/month to your pension.",
            "recommendations": [
                {
                    "action": "Increase pension contributions to £500/month",
                    "reason": "Maximize tax relief",
                    "impact": "Save £200/month in tax"
                }
            ],
            "confidence_score": 0.75,
            "requires_human_review": False,
            "sources": ["General financial planning principles"],
            "metadata": {}
        }

        with patch('api.v1.ai.advisory.AIAdvisoryService') as mock_service:
            mock_service.return_value.answer_financial_question = AsyncMock(
                return_value=mock_advice
            )

            response = await async_client.post(
                "/api/v1/ai/ask",
                json={"question": "How much should I contribute to my pension?"},
                headers=authenticated_headers
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "advice" in data
        assert data["confidence_score"] == 0.75

    async def test_ask_question_too_short(
        self,
        async_client,
        test_user,
        authenticated_headers
    ):
        """Test validation for too-short question."""
        response = await async_client.post(
            "/api/v1/ai/ask",
            json={"question": "Help?"},
            headers=authenticated_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_ask_question_too_long(
        self,
        async_client,
        test_user,
        authenticated_headers
    ):
        """Test validation for too-long question."""
        long_question = "x" * 501

        response = await async_client.post(
            "/api/v1/ai/ask",
            json={"question": long_question},
            headers=authenticated_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
class TestMonthlyInsightsEndpoint:
    """Tests for GET /api/v1/ai/monthly-insights."""

    async def test_get_monthly_insights_success(
        self,
        async_client,
        test_user,
        authenticated_headers
    ):
        """Test successful monthly insights generation."""
        mock_insights = {
            "advice": "Great month! Your net worth increased by £2,500. Keep up the savings momentum.",
            "recommendations": [
                {
                    "action": "Continue current savings rate",
                    "reason": "You're on track for all goals",
                    "impact": "Financial independence by 55"
                }
            ],
            "confidence_score": 0.80,
            "requires_human_review": False,
            "sources": ["Personal financial data analysis"],
            "metadata": {
                "period": "monthly",
                "generated_at": datetime.utcnow().isoformat()
            }
        }

        with patch('api.v1.ai.advisory.AIAdvisoryService') as mock_service:
            mock_service.return_value.generate_monthly_insights = AsyncMock(
                return_value=mock_insights
            )

            response = await async_client.get(
                "/api/v1/ai/monthly-insights",
                headers=authenticated_headers
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "advice" in data
        assert data["confidence_score"] == 0.80
        assert "metadata" in data


@pytest.mark.asyncio
class TestAlertsEndpoint:
    """Tests for GET /api/v1/ai/alerts."""

    async def test_get_alerts_success(
        self,
        async_client,
        test_user,
        authenticated_headers,
        db_session
    ):
        """Test successful alerts retrieval."""
        # Create some alerts (using Recommendation model)
        alert1 = Recommendation(
            user_id=test_user.id,
            recommendation_type=RecommendationType.ISA,
            priority=RecommendationPriority.HIGH,
            title="ISA Allowance",
            description="You have £15,000 unused ISA allowance",
            action_items=["Transfer to ISA"],
            potential_savings=Decimal("500.00"),
            currency=Currency.GBP
        )
        alert2 = Recommendation(
            user_id=test_user.id,
            recommendation_type=RecommendationType.PENSION,
            priority=RecommendationPriority.MEDIUM,
            title="Pension Contribution",
            description="Consider increasing pension contributions",
            action_items=["Increase by £100/month"],
            potential_savings=Decimal("1000.00"),
            currency=Currency.GBP
        )
        db_session.add(alert1)
        db_session.add(alert2)
        await db_session.commit()

        response = await async_client.get(
            "/api/v1/ai/alerts",
            headers=authenticated_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "alerts" in data
        assert "total" in data
        assert "unread_count" in data
        assert data["total"] == 2
        assert data["unread_count"] == 2
        assert len(data["alerts"]) == 2

    async def test_get_alerts_filtered_by_urgency(
        self,
        async_client,
        test_user,
        authenticated_headers,
        db_session
    ):
        """Test filtering alerts by urgency."""
        # Create HIGH priority alert
        alert = Recommendation(
            user_id=test_user.id,
            recommendation_type=RecommendationType.ISA,
            priority=RecommendationPriority.HIGH,
            title="Urgent Alert",
            description="Tax year ending soon",
            action_items=["Take action now"],
            currency=Currency.GBP
        )
        db_session.add(alert)
        await db_session.commit()

        response = await async_client.get(
            "/api/v1/ai/alerts?urgency=HIGH",
            headers=authenticated_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["alerts"]) == 1
        assert data["alerts"][0]["urgency"] == "HIGH"

    async def test_get_alerts_unread_only(
        self,
        async_client,
        test_user,
        authenticated_headers,
        db_session
    ):
        """Test filtering to show only unread alerts."""
        # Create alerts (one read, one unread)
        unread_alert = Recommendation(
            user_id=test_user.id,
            recommendation_type=RecommendationType.ISA,
            priority=RecommendationPriority.HIGH,
            title="Unread Alert",
            description="New alert",
            currency=Currency.GBP
        )
        read_alert = Recommendation(
            user_id=test_user.id,
            recommendation_type=RecommendationType.PENSION,
            priority=RecommendationPriority.MEDIUM,
            title="Read Alert",
            description="Old alert",
            dismissed=True,
            dismissed_date=datetime.utcnow(),
            currency=Currency.GBP
        )
        db_session.add(unread_alert)
        db_session.add(read_alert)
        await db_session.commit()

        response = await async_client.get(
            "/api/v1/ai/alerts?unread_only=true",
            headers=authenticated_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["alerts"]) == 1
        assert data["alerts"][0]["read_at"] is None


@pytest.mark.asyncio
class TestMarkAlertAsReadEndpoint:
    """Tests for POST /api/v1/ai/alerts/{id}/mark-read."""

    async def test_mark_alert_as_read_success(
        self,
        async_client,
        test_user,
        authenticated_headers,
        db_session
    ):
        """Test successfully marking alert as read."""
        # Create alert
        alert = Recommendation(
            user_id=test_user.id,
            recommendation_type=RecommendationType.ISA,
            priority=RecommendationPriority.HIGH,
            title="Test Alert",
            description="Test",
            currency=Currency.GBP
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)

        response = await async_client.post(
            f"/api/v1/ai/alerts/{alert.id}/mark-read",
            headers=authenticated_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify alert was marked as read
        await db_session.refresh(alert)
        assert alert.dismissed is True
        assert alert.dismissed_date is not None

    async def test_mark_alert_as_read_not_found(
        self,
        async_client,
        test_user,
        authenticated_headers
    ):
        """Test 404 when alert doesn't exist."""
        fake_alert_id = uuid4()

        response = await async_client.post(
            f"/api/v1/ai/alerts/{fake_alert_id}/mark-read",
            headers=authenticated_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
class TestDismissAlertEndpoint:
    """Tests for POST /api/v1/ai/alerts/{id}/dismiss."""

    async def test_dismiss_alert_success(
        self,
        async_client,
        test_user,
        authenticated_headers,
        db_session
    ):
        """Test successfully dismissing alert."""
        # Create alert
        alert = Recommendation(
            user_id=test_user.id,
            recommendation_type=RecommendationType.ISA,
            priority=RecommendationPriority.HIGH,
            title="Test Alert",
            description="Test",
            currency=Currency.GBP
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)

        response = await async_client.post(
            f"/api/v1/ai/alerts/{alert.id}/dismiss",
            headers=authenticated_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify alert was dismissed
        await db_session.refresh(alert)
        assert alert.dismissed is True
        assert alert.dismissed_date is not None


@pytest.mark.asyncio
class TestTriggerAlertGenerationEndpoint:
    """Tests for POST /api/v1/ai/alerts/generate (admin only)."""

    async def test_trigger_alert_generation_success_admin(
        self,
        async_client,
        db_session
    ):
        """Test successful alert generation by admin."""
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            hashed_password="hashed",
            first_name="Admin",
            last_name="User",
            status=UserStatus.ACTIVE,
            role="admin"
        )
        db_session.add(admin_user)
        await db_session.commit()
        await db_session.refresh(admin_user)

        # Create auth token for admin
        from utils.jwt import create_access_token
        token = create_access_token(str(admin_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        mock_summary = {
            "users_analyzed": 10,
            "alerts_generated": 25,
            "errors": 0
        }

        with patch('api.v1.ai.advisory.ProactiveAlertsService') as mock_service:
            mock_service.return_value.schedule_daily_analysis = AsyncMock(
                return_value=mock_summary
            )

            response = await async_client.post(
                "/api/v1/ai/alerts/generate",
                headers=headers
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["users_analyzed"] == 10
        assert data["alerts_generated"] == 25
        assert data["errors"] == 0
        assert "timestamp" in data

    async def test_trigger_alert_generation_forbidden_non_admin(
        self,
        async_client,
        test_user,
        authenticated_headers
    ):
        """Test 403 when non-admin tries to trigger alert generation."""
        response = await async_client.post(
            "/api/v1/ai/alerts/generate",
            headers=authenticated_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "admin" in response.json()["detail"].lower()


@pytest.mark.asyncio
class TestAuthenticationAndAuthorization:
    """Test authentication and authorization across all endpoints."""

    async def test_all_endpoints_require_auth(self, async_client):
        """Test all endpoints require authentication."""
        endpoints = [
            ("POST", "/api/v1/ai/retirement-advice"),
            ("POST", "/api/v1/ai/investment-advice"),
            ("POST", "/api/v1/ai/tax-advice"),
            ("POST", "/api/v1/ai/ask", {"question": "Test question here"}),
            ("GET", "/api/v1/ai/monthly-insights"),
            ("GET", "/api/v1/ai/alerts"),
        ]

        for method, path, *body in endpoints:
            if method == "POST":
                json_data = body[0] if body else None
                response = await async_client.post(path, json=json_data)
            else:
                response = await async_client.get(path)

            assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling across endpoints."""

    async def test_service_error_returns_500(
        self,
        async_client,
        test_user,
        authenticated_headers
    ):
        """Test 500 error when service fails."""
        with patch('api.v1.ai.advisory.AIAdvisoryService') as mock_service:
            mock_service.return_value.generate_retirement_advice = AsyncMock(
                side_effect=Exception("Service error")
            )

            response = await async_client.post(
                "/api/v1/ai/retirement-advice",
                headers=authenticated_headers
            )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to generate retirement advice" in response.json()["detail"]
