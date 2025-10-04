import { useEffect } from 'react';
import { authStorage } from '../../utils/auth';

/**
 * BehaviorTracker - Utility component for tracking user behavior
 *
 * Invisible component that tracks page views and feature usage
 * for personalization and analytics.
 *
 * Usage:
 *   <BehaviorTracker page="dashboard" />
 *   <BehaviorTracker feature="goal_creation" />
 *   <BehaviorTracker page="savings" duration={45} />
 *
 * Props:
 * - page: Page name (e.g., "dashboard", "goals", "savings")
 * - feature: Feature name (e.g., "goal_creation", "account_management")
 * - duration: Time spent in seconds (optional)
 */
export function BehaviorTracker({ page, feature, duration }) {
  useEffect(() => {
    // Temporarily disabled until backend endpoints are implemented
    // trackBehavior();
  }, [page, feature, duration]);

  async function trackBehavior() {
    // Don't track if user not authenticated
    if (!authStorage.isAuthenticated()) {
      return;
    }

    try {
      // Determine action type
      let actionType = 'PAGE_VIEW';
      const actionContext = {};

      if (page) {
        actionType = 'PAGE_VIEW';
        actionContext.page = page;
        if (duration) {
          actionContext.duration = duration;
        }
      } else if (feature) {
        actionType = 'FEATURE_USAGE';
        actionContext.feature = feature;
      }

      // Track the behavior
      const response = await fetch('/api/v1/personalization/behavior/track', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({
          action_type: actionType,
          action_context: actionContext,
        }),
      });

      // Silently ignore if endpoint doesn't exist yet (404)
      if (response.status === 404) {
        return;
      }
    } catch (err) {
      // Silently fail - don't disrupt user experience
      // Only log in development
      if (process.env.NODE_ENV === 'development') {
        console.debug('Behavior tracking failed:', err);
      }
    }
  }

  // This component doesn't render anything
  return null;
}
