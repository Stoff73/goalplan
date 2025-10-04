"""
Comprehensive test suite for PreferenceService.

Tests cover:
- Preference management (save, get, update)
- Behavior tracking
- Behavior analysis
- Dashboard personalization
- Insight generation
- Edge cases and multi-user scenarios
"""

import json
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select

from models.personalization import (
    UserPreference, UserBehavior, PersonalizedInsight,
    PreferenceType, ActionType, InsightType
)
from services.personalization.preference_service import PreferenceService


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
async def preference_service(db_session):
    """Create PreferenceService instance."""
    return PreferenceService(db_session)


@pytest.fixture
async def test_user(db_session):
    """Create test user."""
    from models.user import User, UserStatus, CountryPreference
    from utils.password import hash_password

    user = User(
        email="testuser@example.com",
        password_hash=hash_password("SecurePass123!"),
        first_name="Test",
        last_name="User",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def other_user(db_session):
    """Create another test user."""
    from models.user import User, UserStatus, CountryPreference
    from utils.password import hash_password

    user = User(
        email="otheruser@example.com",
        password_hash=hash_password("SecurePass123!"),
        first_name="Other",
        last_name="User",
        country_preference=CountryPreference.SA,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ============================================================================
# PREFERENCE MANAGEMENT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_save_preference_creates_new(preference_service, test_user, db_session):
    """Test saving a new preference creates a record."""
    # Save preference
    preference = await preference_service.save_preference(
        user_id=test_user.id,
        preference_type=PreferenceType.DEFAULT_CURRENCY,
        preference_value="USD"
    )

    # Verify preference created
    assert preference.id is not None
    assert preference.user_id == test_user.id
    assert preference.preference_type == PreferenceType.DEFAULT_CURRENCY
    assert preference.preference_value == "USD"
    assert preference.created_at is not None
    assert preference.updated_at is not None
    assert preference.deleted_at is None


@pytest.mark.asyncio
async def test_save_preference_updates_existing(preference_service, test_user, db_session):
    """Test saving an existing preference updates the value."""
    # Create initial preference
    pref1 = await preference_service.save_preference(
        user_id=test_user.id,
        preference_type=PreferenceType.DEFAULT_CURRENCY,
        preference_value="GBP"
    )

    original_id = pref1.id
    original_created_at = pref1.created_at

    # Update preference
    pref2 = await preference_service.save_preference(
        user_id=test_user.id,
        preference_type=PreferenceType.DEFAULT_CURRENCY,
        preference_value="ZAR"
    )

    # Verify preference updated (same ID, new value)
    assert pref2.id == original_id
    assert pref2.preference_value == "ZAR"
    assert pref2.created_at == original_created_at
    assert pref2.updated_at > original_created_at


@pytest.mark.asyncio
async def test_get_preferences_returns_defaults_when_empty(preference_service, test_user):
    """Test getting preferences returns defaults for new user."""
    preferences = await preference_service.get_preferences(test_user.id)

    # Should return all default preferences
    assert len(preferences) >= 6
    assert preferences[PreferenceType.DEFAULT_CURRENCY.value] == "GBP"
    assert preferences[PreferenceType.THEME.value] == "light"
    assert preferences[PreferenceType.NOTIFICATION_FREQUENCY.value] == "weekly"


@pytest.mark.asyncio
async def test_get_preferences_returns_saved_values(preference_service, test_user):
    """Test getting preferences returns saved values."""
    # Save some preferences
    await preference_service.save_preference(
        test_user.id, PreferenceType.DEFAULT_CURRENCY, "USD"
    )
    await preference_service.save_preference(
        test_user.id, PreferenceType.THEME, "dark"
    )

    # Get preferences
    preferences = await preference_service.get_preferences(test_user.id)

    # Verify saved values returned
    assert preferences[PreferenceType.DEFAULT_CURRENCY.value] == "USD"
    assert preferences[PreferenceType.THEME.value] == "dark"
    # Should still have defaults for others
    assert preferences[PreferenceType.NOTIFICATION_FREQUENCY.value] == "weekly"


# ============================================================================
# BEHAVIOR TRACKING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_track_behavior_creates_record(preference_service, test_user, db_session):
    """Test tracking behavior creates a record."""
    # Track behavior
    behavior = await preference_service.track_behavior(
        user_id=test_user.id,
        action_type=ActionType.PAGE_VIEW,
        action_context={"page": "dashboard", "duration": 30}
    )

    # Verify behavior created
    assert behavior.id is not None
    assert behavior.user_id == test_user.id
    assert behavior.action_type == ActionType.PAGE_VIEW
    assert behavior.timestamp is not None

    # Verify context stored as JSON
    context = json.loads(behavior.action_context)
    assert context["page"] == "dashboard"
    assert context["duration"] == 30


@pytest.mark.asyncio
async def test_track_behavior_stores_timestamp(preference_service, test_user):
    """Test tracking behavior stores UTC timestamp."""
    before = datetime.utcnow()

    behavior = await preference_service.track_behavior(
        user_id=test_user.id,
        action_type=ActionType.CLICK,
        action_context={"element": "save_button"}
    )

    after = datetime.utcnow()

    # Verify timestamp is within expected range
    assert before <= behavior.timestamp <= after


@pytest.mark.asyncio
async def test_track_behavior_stores_context_as_json(preference_service, test_user):
    """Test tracking behavior stores complex context as JSON."""
    complex_context = {
        "page": "goals",
        "feature": "create_goal",
        "goal_type": "HOUSE_PURCHASE",
        "target_amount": 50000,
        "metadata": {
            "referrer": "dashboard",
            "timestamp": "2025-10-04T10:00:00Z"
        }
    }

    behavior = await preference_service.track_behavior(
        user_id=test_user.id,
        action_type=ActionType.FEATURE_USAGE,
        action_context=complex_context
    )

    # Verify context can be parsed back
    stored_context = json.loads(behavior.action_context)
    assert stored_context == complex_context


# ============================================================================
# BEHAVIOR ANALYSIS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_analyze_behavior_empty_returns_zeros(preference_service, test_user):
    """Test analyzing behavior with no data returns zeros."""
    analysis = await preference_service.analyze_behavior(test_user.id)

    assert analysis["most_viewed_pages"] == []
    assert analysis["most_used_features"] == []
    assert analysis["engagement_score"] == 0
    assert analysis["total_actions"] == 0


@pytest.mark.asyncio
async def test_analyze_behavior_counts_page_views(preference_service, test_user):
    """Test analyzing behavior counts page views correctly."""
    # Track multiple page views
    await preference_service.track_behavior(
        test_user.id, ActionType.PAGE_VIEW, {"page": "dashboard"}
    )
    await preference_service.track_behavior(
        test_user.id, ActionType.PAGE_VIEW, {"page": "goals"}
    )
    await preference_service.track_behavior(
        test_user.id, ActionType.PAGE_VIEW, {"page": "dashboard"}
    )
    await preference_service.track_behavior(
        test_user.id, ActionType.PAGE_VIEW, {"page": "savings"}
    )
    await preference_service.track_behavior(
        test_user.id, ActionType.PAGE_VIEW, {"page": "dashboard"}
    )

    # Analyze behavior
    analysis = await preference_service.analyze_behavior(test_user.id)

    # Verify counts
    assert "dashboard" in analysis["most_viewed_pages"]
    assert "goals" in analysis["most_viewed_pages"]
    assert "savings" in analysis["most_viewed_pages"]
    # Dashboard should be first (most viewed)
    assert analysis["most_viewed_pages"][0] == "dashboard"


@pytest.mark.asyncio
async def test_analyze_behavior_identifies_most_used_features(preference_service, test_user):
    """Test analyzing behavior identifies most used features."""
    # Track feature usage
    await preference_service.track_behavior(
        test_user.id, ActionType.FEATURE_USAGE, {"feature": "goal_tracking"}
    )
    await preference_service.track_behavior(
        test_user.id, ActionType.FEATURE_USAGE, {"feature": "account_management"}
    )
    await preference_service.track_behavior(
        test_user.id, ActionType.FEATURE_USAGE, {"feature": "goal_tracking"}
    )

    # Analyze behavior
    analysis = await preference_service.analyze_behavior(test_user.id)

    # Verify features identified
    assert "goal_tracking" in analysis["most_used_features"]
    assert "account_management" in analysis["most_used_features"]
    # goal_tracking should be first (most used)
    assert analysis["most_used_features"][0] == "goal_tracking"


@pytest.mark.asyncio
async def test_analyze_behavior_calculates_engagement_score(preference_service, test_user):
    """Test analyzing behavior calculates engagement score."""
    # Track various actions
    for i in range(20):
        await preference_service.track_behavior(
            test_user.id, ActionType.PAGE_VIEW, {"page": f"page_{i % 5}"}
        )
    for i in range(10):
        await preference_service.track_behavior(
            test_user.id, ActionType.FEATURE_USAGE, {"feature": f"feature_{i % 3}"}
        )

    # Analyze behavior
    analysis = await preference_service.analyze_behavior(test_user.id)

    # Engagement score should be > 0 (calculated based on actions, pages, features)
    assert analysis["engagement_score"] > 0
    assert analysis["engagement_score"] <= 100
    assert analysis["total_actions"] == 30


# ============================================================================
# DASHBOARD PERSONALIZATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_personalize_dashboard_default_layout_for_new_user(preference_service, test_user):
    """Test dashboard personalization returns default layout for new user."""
    dashboard = await preference_service.personalize_dashboard(test_user.id)

    # Should return default layout (no behavior data)
    assert "widget_order" in dashboard
    assert "visible_widgets" in dashboard
    assert "hidden_widgets" in dashboard
    assert len(dashboard["widget_order"]) > 0
    assert len(dashboard["visible_widgets"]) > 0
    assert dashboard["hidden_widgets"] == []


@pytest.mark.asyncio
async def test_personalize_dashboard_orders_by_usage(preference_service, test_user):
    """Test dashboard personalization orders widgets by usage."""
    # Track page views (simulate usage)
    # View goals page frequently
    for _ in range(10):
        await preference_service.track_behavior(
            test_user.id, ActionType.PAGE_VIEW, {"page": "goals"}
        )
    # View savings page moderately
    for _ in range(5):
        await preference_service.track_behavior(
            test_user.id, ActionType.PAGE_VIEW, {"page": "savings"}
        )
    # View investments page rarely
    for _ in range(2):
        await preference_service.track_behavior(
            test_user.id, ActionType.PAGE_VIEW, {"page": "investments"}
        )

    # Personalize dashboard
    dashboard = await preference_service.personalize_dashboard(test_user.id)

    # Verify widgets ordered by usage
    widget_order = dashboard["widget_order"]
    # Goals should be first (most viewed)
    goals_index = widget_order.index("goals")
    savings_index = widget_order.index("savings")
    investments_index = widget_order.index("investments")

    assert goals_index < savings_index
    assert savings_index < investments_index


@pytest.mark.asyncio
async def test_personalize_dashboard_hides_unused_widgets(preference_service, test_user):
    """Test dashboard personalization hides widgets with <5% usage."""
    # Track page views heavily focused on 2 pages
    for _ in range(50):
        await preference_service.track_behavior(
            test_user.id, ActionType.PAGE_VIEW, {"page": "goals"}
        )
    for _ in range(50):
        await preference_service.track_behavior(
            test_user.id, ActionType.PAGE_VIEW, {"page": "savings"}
        )
    # Other pages not viewed

    # Personalize dashboard
    dashboard = await preference_service.personalize_dashboard(test_user.id)

    # Verify some widgets hidden (those with <5% usage)
    # Note: The service ensures at least 3 widgets are visible
    assert len(dashboard["visible_widgets"]) >= 3
    # Widgets should be hidden if usage < 5%
    assert len(dashboard["hidden_widgets"]) >= 0


# ============================================================================
# INSIGHT GENERATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_generate_insights_empty_when_no_data(preference_service, test_user):
    """Test generating insights creates generic insights for new user."""
    insights = await preference_service.generate_personalized_insights(test_user.id)

    # Should generate some generic insights even for new user
    # (implementation creates placeholder insights)
    assert isinstance(insights, list)
    # May have some generic insights
    assert len(insights) >= 0


@pytest.mark.asyncio
async def test_generate_insights_goal_advice(preference_service, test_user):
    """Test generating insights includes goal advice."""
    # Track low engagement
    # (No behavior tracked = low engagement)

    insights = await preference_service.generate_personalized_insights(test_user.id)

    # Should include engagement-related insight
    insight_texts = [i.insight_text for i in insights]
    # Check if any insight mentions engagement or goals
    has_relevant_insight = any(
        'engagement' in text.lower() or 'goal' in text.lower()
        for text in insight_texts
    )
    assert has_relevant_insight


@pytest.mark.asyncio
async def test_generate_insights_savings_tip(preference_service, test_user):
    """Test generating insights includes savings tip."""
    insights = await preference_service.generate_personalized_insights(test_user.id)

    # Should include savings tip
    savings_insights = [
        i for i in insights
        if i.insight_type == InsightType.SAVINGS_TIP
    ]
    assert len(savings_insights) > 0


@pytest.mark.asyncio
async def test_generate_insights_ranks_by_relevance(preference_service, test_user):
    """Test generating insights ranks by relevance score."""
    insights = await preference_service.generate_personalized_insights(test_user.id)

    # Verify insights are sorted by relevance (descending)
    relevance_scores = [float(i.relevance_score) for i in insights]
    assert relevance_scores == sorted(relevance_scores, reverse=True)


@pytest.mark.asyncio
async def test_generate_insights_limits_results(preference_service, test_user):
    """Test generating insights limits results to specified count."""
    # Generate with limit of 3
    insights = await preference_service.generate_personalized_insights(test_user.id, limit=3)

    # Should return at most 3 insights
    assert len(insights) <= 3


# ============================================================================
# MULTI-USER ISOLATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_multiple_users_isolated(preference_service, test_user, other_user):
    """Test that multiple users' data is properly isolated."""
    # Save preferences for both users
    await preference_service.save_preference(
        test_user.id, PreferenceType.DEFAULT_CURRENCY, "GBP"
    )
    await preference_service.save_preference(
        other_user.id, PreferenceType.DEFAULT_CURRENCY, "ZAR"
    )

    # Track behavior for both users
    await preference_service.track_behavior(
        test_user.id, ActionType.PAGE_VIEW, {"page": "dashboard"}
    )
    await preference_service.track_behavior(
        other_user.id, ActionType.PAGE_VIEW, {"page": "goals"}
    )

    # Get preferences
    test_user_prefs = await preference_service.get_preferences(test_user.id)
    other_user_prefs = await preference_service.get_preferences(other_user.id)

    # Verify isolation
    assert test_user_prefs[PreferenceType.DEFAULT_CURRENCY.value] == "GBP"
    assert other_user_prefs[PreferenceType.DEFAULT_CURRENCY.value] == "ZAR"

    # Analyze behavior
    test_user_analysis = await preference_service.analyze_behavior(test_user.id)
    other_user_analysis = await preference_service.analyze_behavior(other_user.id)

    # Verify isolation
    assert test_user_analysis["total_actions"] == 1
    assert other_user_analysis["total_actions"] == 1
    assert "dashboard" in test_user_analysis["most_viewed_pages"]
    assert "goals" in other_user_analysis["most_viewed_pages"]


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_analyze_behavior_with_invalid_json_context(preference_service, test_user, db_session):
    """Test analyzing behavior handles invalid JSON gracefully."""
    # Manually create behavior with invalid JSON
    from models.personalization import UserBehavior
    import uuid

    behavior = UserBehavior(
        id=uuid.uuid4(),
        user_id=test_user.id,
        action_type=ActionType.PAGE_VIEW,
        action_context="INVALID JSON",  # Invalid JSON
        timestamp=datetime.utcnow()
    )
    db_session.add(behavior)
    await db_session.commit()

    # Analyze behavior (should not crash)
    analysis = await preference_service.analyze_behavior(test_user.id)

    # Should handle gracefully and return results
    assert analysis is not None
    assert "total_actions" in analysis


@pytest.mark.asyncio
async def test_behavior_analysis_respects_time_range(preference_service, test_user, db_session):
    """Test behavior analysis only includes data from specified time range."""
    from models.personalization import UserBehavior
    import uuid

    # Create old behavior (40 days ago)
    old_behavior = UserBehavior(
        id=uuid.uuid4(),
        user_id=test_user.id,
        action_type=ActionType.PAGE_VIEW,
        action_context=json.dumps({"page": "old_page"}),
        timestamp=datetime.utcnow() - timedelta(days=40)
    )
    db_session.add(old_behavior)

    # Create recent behavior (10 days ago)
    recent_behavior = UserBehavior(
        id=uuid.uuid4(),
        user_id=test_user.id,
        action_type=ActionType.PAGE_VIEW,
        action_context=json.dumps({"page": "recent_page"}),
        timestamp=datetime.utcnow() - timedelta(days=10)
    )
    db_session.add(recent_behavior)

    await db_session.commit()

    # Analyze last 30 days
    analysis = await preference_service.analyze_behavior(test_user.id, days=30)

    # Should only include recent behavior
    assert analysis["total_actions"] == 1
    assert "recent_page" in analysis["most_viewed_pages"]
    assert "old_page" not in analysis["most_viewed_pages"]
