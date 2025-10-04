"""
Preference Service

Provides comprehensive personalization functionality including:
- User preference management (save/retrieve)
- Behavior tracking and analysis
- Personalized dashboard layout generation
- Personalized insight generation

Business Rules:
- Preferences stored as key-value pairs
- Behavior tracked asynchronously
- Dashboard personalized based on usage patterns
- Insights generated based on user profile and financial data
- Default preferences provided for new users

Performance:
- Target: <200ms for preference queries
- Target: <100ms for behavior tracking
- Target: <500ms for dashboard personalization
- Target: <1s for insight generation
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from uuid import UUID
from collections import Counter

from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.personalization import (
    UserPreference, UserBehavior, PersonalizedInsight,
    PreferenceType, ActionType, InsightType
)

logger = logging.getLogger(__name__)


class PreferenceService:
    """Service for user personalization and behavior tracking."""

    # Default preferences for new users
    DEFAULT_PREFERENCES = {
        PreferenceType.DEFAULT_CURRENCY: 'GBP',
        PreferenceType.THEME: 'light',
        PreferenceType.NOTIFICATION_FREQUENCY: 'weekly',
        PreferenceType.NUMBER_FORMAT: 'en-GB',
        PreferenceType.DATE_FORMAT: 'DD/MM/YYYY',
        PreferenceType.DASHBOARD_LAYOUT: json.dumps({
            'widget_order': ['net_worth', 'goals', 'savings', 'investments', 'retirement', 'protection'],
            'visible_widgets': ['net_worth', 'goals', 'savings', 'investments', 'retirement', 'protection']
        })
    }

    # Default dashboard widget order
    DEFAULT_WIDGET_ORDER = [
        'net_worth', 'goals', 'savings', 'investments',
        'retirement', 'protection', 'tax', 'iht'
    ]

    def __init__(self, db: AsyncSession):
        """
        Initialize preference service.

        Args:
            db: Database session for operations
        """
        self.db = db

    async def save_preference(
        self,
        user_id: UUID,
        preference_type: PreferenceType,
        preference_value: str
    ) -> UserPreference:
        """
        Save or update user preference.

        Args:
            user_id: User UUID
            preference_type: Type of preference
            preference_value: Preference value (JSON string for complex preferences)

        Returns:
            Saved UserPreference

        Business Logic:
            - Check if preference exists for this user and type
            - If exists, update value and updated_at
            - If not, create new preference
            - Validate preference_value based on type (basic validation)
        """
        logger.info(f"Saving preference for user {user_id}: {preference_type} = {preference_value}")

        # Check if preference exists
        result = await self.db.execute(
            select(UserPreference).where(
                and_(
                    UserPreference.user_id == user_id,
                    UserPreference.preference_type == preference_type,
                    UserPreference.deleted_at.is_(None)
                )
            )
        )
        existing_pref = result.scalar_one_or_none()

        if existing_pref:
            # Update existing preference
            existing_pref.preference_value = preference_value
            existing_pref.updated_at = datetime.utcnow()
            preference = existing_pref
        else:
            # Create new preference
            preference = UserPreference(
                id=uuid.uuid4(),
                user_id=user_id,
                preference_type=preference_type,
                preference_value=preference_value
            )
            self.db.add(preference)

        await self.db.commit()
        await self.db.refresh(preference)

        logger.info(f"Preference saved: {preference_type} for user {user_id}")

        return preference

    async def get_preferences(self, user_id: UUID) -> Dict[str, str]:
        """
        Return all user preferences as dict.

        Args:
            user_id: User UUID

        Returns:
            Dict with preference_type as key, preference_value as value.
            Returns defaults if no preferences set.

        Business Logic:
            - Query all active preferences for user
            - Build dict with preference_type -> preference_value
            - Fill in defaults for missing preferences
        """
        logger.info(f"Getting preferences for user {user_id}")

        # Query user preferences
        result = await self.db.execute(
            select(UserPreference).where(
                and_(
                    UserPreference.user_id == user_id,
                    UserPreference.deleted_at.is_(None)
                )
            )
        )
        preferences = result.scalars().all()

        # Build dict
        prefs_dict = {}
        for pref in preferences:
            prefs_dict[pref.preference_type.value] = pref.preference_value

        # Fill in defaults for missing preferences
        for pref_type, default_value in self.DEFAULT_PREFERENCES.items():
            if pref_type.value not in prefs_dict:
                prefs_dict[pref_type.value] = default_value

        logger.info(f"Preferences retrieved for user {user_id}: {len(prefs_dict)} preferences")

        return prefs_dict

    async def track_behavior(
        self,
        user_id: UUID,
        action_type: ActionType,
        action_context: Dict
    ) -> UserBehavior:
        """
        Log user action.

        Args:
            user_id: User UUID
            action_type: Type of action
            action_context: Action context metadata (dict)

        Returns:
            Created UserBehavior record

        Business Logic:
            - Store timestamp (UTC now)
            - Store context as JSON string
            - Async/fire-and-forget for performance
        """
        logger.debug(f"Tracking behavior for user {user_id}: {action_type}")

        # Create behavior record
        behavior = UserBehavior(
            id=uuid.uuid4(),
            user_id=user_id,
            action_type=action_type,
            action_context=json.dumps(action_context),
            timestamp=datetime.utcnow()
        )

        self.db.add(behavior)
        await self.db.commit()
        await self.db.refresh(behavior)

        logger.debug(f"Behavior tracked: {action_type} for user {user_id}")

        return behavior

    async def analyze_behavior(
        self,
        user_id: UUID,
        days: int = 30
    ) -> Dict:
        """
        Analyze user behavior over last N days.

        Args:
            user_id: User UUID
            days: Number of days to analyze (default: 30)

        Returns:
            Dict with:
                - most_viewed_pages: List[str]
                - most_used_features: List[str]
                - engagement_score: int (0-100)
                - total_actions: int

        Business Logic:
            - Query behaviors from last N days
            - Parse action_context JSON
            - Count page views by page
            - Count feature usage by feature
            - Calculate engagement score based on:
              - Total actions (weight: 40%)
              - Unique pages visited (weight: 30%)
              - Feature diversity (weight: 30%)
        """
        logger.info(f"Analyzing behavior for user {user_id} (last {days} days)")

        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)

        # Query behaviors
        result = await self.db.execute(
            select(UserBehavior).where(
                and_(
                    UserBehavior.user_id == user_id,
                    UserBehavior.timestamp >= start_date
                )
            ).order_by(desc(UserBehavior.timestamp))
        )
        behaviors = result.scalars().all()

        total_actions = len(behaviors)

        # Parse behaviors
        page_views = []
        feature_usage = []

        for behavior in behaviors:
            try:
                context = json.loads(behavior.action_context)

                if behavior.action_type == ActionType.PAGE_VIEW:
                    if 'page' in context:
                        page_views.append(context['page'])

                elif behavior.action_type == ActionType.FEATURE_USAGE:
                    if 'feature' in context:
                        feature_usage.append(context['feature'])

            except json.JSONDecodeError:
                logger.warning(f"Failed to parse action_context for behavior {behavior.id}")
                continue

        # Count occurrences
        page_counter = Counter(page_views)
        feature_counter = Counter(feature_usage)

        # Get top 5 most viewed pages
        most_viewed_pages = [page for page, count in page_counter.most_common(5)]

        # Get top 5 most used features
        most_used_features = [feature for feature, count in feature_counter.most_common(5)]

        # Calculate engagement score
        # 40% based on total actions (normalize to 0-100, max 100 actions = 100%)
        action_score = min(float(total_actions) / 100.0 * 100, 100)

        # 30% based on unique pages visited (normalize to 0-100, max 10 pages = 100%)
        unique_pages = len(page_counter)
        page_score = min(float(unique_pages) / 10.0 * 100, 100)

        # 30% based on feature diversity (normalize to 0-100, max 10 features = 100%)
        unique_features = len(feature_counter)
        feature_score = min(float(unique_features) / 10.0 * 100, 100)

        engagement_score = int(
            (action_score * 0.40) +
            (page_score * 0.30) +
            (feature_score * 0.30)
        )

        result_dict = {
            "most_viewed_pages": most_viewed_pages,
            "most_used_features": most_used_features,
            "engagement_score": engagement_score,
            "total_actions": total_actions
        }

        logger.info(
            f"Behavior analysis complete for user {user_id}: "
            f"{total_actions} actions, engagement score {engagement_score}"
        )

        return result_dict

    async def personalize_dashboard(
        self,
        user_id: UUID
    ) -> Dict:
        """
        Determine personalized dashboard layout.

        Args:
            user_id: User UUID

        Returns:
            Dict with:
                - widget_order: List[str] (ordered widget names)
                - visible_widgets: List[str] (widgets to show)
                - hidden_widgets: List[str] (widgets to hide/collapse)

        Business Logic:
            - Analyze behavior to identify frequently accessed sections
            - Get user preferences for layout
            - Order widgets by usage frequency
            - Hide widgets with <5% usage rate
            - If no behavior data, return default layout
        """
        logger.info(f"Personalizing dashboard for user {user_id}")

        # Get behavior analysis
        behavior_analysis = await self.analyze_behavior(user_id, days=30)

        # If no behavior data, return default layout
        if behavior_analysis['total_actions'] == 0:
            logger.info(f"No behavior data for user {user_id}, returning default layout")
            return {
                "widget_order": self.DEFAULT_WIDGET_ORDER,
                "visible_widgets": self.DEFAULT_WIDGET_ORDER,
                "hidden_widgets": []
            }

        # Map pages to widgets
        page_to_widget = {
            'dashboard': 'net_worth',
            'goals': 'goals',
            'savings': 'savings',
            'investments': 'investments',
            'retirement': 'retirement',
            'protection': 'protection',
            'tax': 'tax',
            'iht': 'iht'
        }

        # Count widget usage from page views
        widget_usage = Counter()
        total_page_views = 0

        for page in behavior_analysis['most_viewed_pages']:
            # Get actual count from behaviors
            result = await self.db.execute(
                select(func.count(UserBehavior.id)).where(
                    and_(
                        UserBehavior.user_id == user_id,
                        UserBehavior.action_type == ActionType.PAGE_VIEW,
                        UserBehavior.action_context.like(f'%"page": "{page}"%'),
                        UserBehavior.timestamp >= datetime.utcnow() - timedelta(days=30)
                    )
                )
            )
            page_count = result.scalar() or 0
            total_page_views += page_count

            if page in page_to_widget:
                widget_usage[page_to_widget[page]] = page_count

        # Add all default widgets that weren't tracked
        for widget in self.DEFAULT_WIDGET_ORDER:
            if widget not in widget_usage:
                widget_usage[widget] = 0

        # Calculate usage percentages
        usage_percentages = {}
        for widget, count in widget_usage.items():
            if total_page_views > 0:
                usage_percentages[widget] = (count / total_page_views) * 100
            else:
                usage_percentages[widget] = 0

        # Sort widgets by usage (descending)
        sorted_widgets = sorted(
            widget_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Build widget order
        widget_order = [widget for widget, count in sorted_widgets]

        # Determine visible vs hidden (hide if <5% usage)
        visible_widgets = [
            widget for widget in widget_order
            if usage_percentages.get(widget, 0) >= 5.0
        ]

        # Ensure at least 3 widgets are visible
        if len(visible_widgets) < 3:
            visible_widgets = widget_order[:3]

        hidden_widgets = [
            widget for widget in widget_order
            if widget not in visible_widgets
        ]

        result_dict = {
            "widget_order": widget_order,
            "visible_widgets": visible_widgets,
            "hidden_widgets": hidden_widgets
        }

        logger.info(
            f"Dashboard personalized for user {user_id}: "
            f"{len(visible_widgets)} visible, {len(hidden_widgets)} hidden"
        )

        return result_dict

    async def generate_personalized_insights(
        self,
        user_id: UUID,
        limit: int = 10
    ) -> List[PersonalizedInsight]:
        """
        Generate personalized insights based on user profile.

        Args:
            user_id: User UUID
            limit: Maximum number of insights to return (default: 10)

        Returns:
            List of PersonalizedInsight objects, ordered by relevance score (descending)

        Business Logic:
            - Analyze goals, behavior, financial data
            - Create insights tailored to user
            - Calculate relevance scores (0-100)
            - Return top N insights by relevance

        Insight types:
            - GOAL_ADVICE: Goal progress recommendations
            - SAVINGS_TIP: Account optimization suggestions
            - INVESTMENT_TIP: Portfolio suggestions
            - TAX_TIP: Tax efficiency opportunities
            - SPENDING_INSIGHT: Behavior analysis

        Note:
            This is a simplified implementation. Full implementation would
            integrate with goals, accounts, investments, etc.
        """
        logger.info(f"Generating personalized insights for user {user_id}")

        insights = []

        # Get behavior analysis
        behavior_analysis = await self.analyze_behavior(user_id, days=30)

        # Generate engagement insight if low engagement
        if behavior_analysis['engagement_score'] < 50:
            insight = PersonalizedInsight(
                id=uuid.uuid4(),
                user_id=user_id,
                insight_type=InsightType.GOAL_ADVICE,
                insight_text=(
                    f"Your engagement score is {behavior_analysis['engagement_score']}%. "
                    "Setting clear financial goals can help you stay motivated and on track."
                ),
                relevance_score=Decimal('75.00')
            )
            insights.append(insight)

        # Generate feature usage insight
        if len(behavior_analysis['most_used_features']) > 0:
            top_feature = behavior_analysis['most_used_features'][0]
            insight = PersonalizedInsight(
                id=uuid.uuid4(),
                user_id=user_id,
                insight_type=InsightType.GOAL_ADVICE,
                insight_text=(
                    f"You use {top_feature} frequently. "
                    "Consider exploring related features to maximize your financial planning."
                ),
                relevance_score=Decimal('60.00')
            )
            insights.append(insight)

        # Generate generic insights as placeholders
        # In full implementation, these would be based on actual financial data

        # Savings tip
        insight = PersonalizedInsight(
            id=uuid.uuid4(),
            user_id=user_id,
            insight_type=InsightType.SAVINGS_TIP,
            insight_text=(
                "Consider setting up automatic savings transfers to reach your goals faster. "
                "Even small amounts add up over time through compound interest."
            ),
            relevance_score=Decimal('70.00')
        )
        insights.append(insight)

        # Investment tip
        insight = PersonalizedInsight(
            id=uuid.uuid4(),
            user_id=user_id,
            insight_type=InsightType.INVESTMENT_TIP,
            insight_text=(
                "Diversification reduces risk. "
                "Consider spreading investments across different asset classes and geographies."
            ),
            relevance_score=Decimal('65.00')
        )
        insights.append(insight)

        # Tax tip
        insight = PersonalizedInsight(
            id=uuid.uuid4(),
            user_id=user_id,
            insight_type=InsightType.TAX_TIP,
            insight_text=(
                "Maximize your ISA allowance (£20,000/year) to shelter investments from tax. "
                "Tax-free growth can significantly boost long-term returns."
            ),
            relevance_score=Decimal('80.00')
        )
        insights.append(insight)

        # Sort insights by relevance score (descending)
        insights.sort(key=lambda x: x.relevance_score, reverse=True)

        # Limit results
        insights = insights[:limit]

        # Save insights to database
        for insight in insights:
            self.db.add(insight)

        await self.db.commit()

        # Refresh all insights
        for insight in insights:
            await self.db.refresh(insight)

        logger.info(f"Generated {len(insights)} personalized insights for user {user_id}")

        return insights


# Factory function
def get_preference_service(db: AsyncSession) -> PreferenceService:
    """
    Get preference service instance.

    Args:
        db: Database session

    Returns:
        PreferenceService instance
    """
    return PreferenceService(db)
