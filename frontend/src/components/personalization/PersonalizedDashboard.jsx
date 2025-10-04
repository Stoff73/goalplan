import React, { useState, useEffect } from 'react';
import { Card, Button, Alert, Badge } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';
import { InsightsFeed } from './InsightsFeed';
import { BehaviorTracker } from './BehaviorTracker';

/**
 * PersonalizedDashboard - Adaptive dashboard that learns from user behavior
 *
 * Follows STYLEGUIDE.md narrative storytelling approach:
 * - Conversational intro explaining personalization
 * - Widgets ordered by usage frequency
 * - Embedded metrics in narrative sentences
 * - Progressive disclosure for hidden widgets
 * - Line height 1.7, generous padding
 *
 * Features:
 * - Dynamically ordered widgets based on usage
 * - Hide unused widgets
 * - Personalized insights feed
 * - Behavior tracking
 */
export function PersonalizedDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showHiddenWidgets, setShowHiddenWidgets] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/personalization/dashboard/personalized', {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }
        // Silently ignore 404 - endpoint not implemented yet
        if (response.status === 404) {
          return;
        }
        throw new Error('Failed to load personalized dashboard');
      }

      const data = await response.json();
      setDashboard(data);
    } catch (err) {
      setError('Unable to load your personalized dashboard. Please try again.');
      console.error('Error loading dashboard:', err);
    } finally {
      setLoading(false);
    }
  }

  const getWidgetDisplayName = (widgetKey) => {
    const names = {
      net_worth: 'Net Worth Overview',
      goals: 'Financial Goals',
      savings: 'Savings & Cash',
      investments: 'Investment Portfolio',
      retirement: 'Retirement Planning',
      protection: 'Life Protection',
      tax: 'Tax Summary',
      iht: 'Inheritance Planning'
    };
    return names[widgetKey] || widgetKey;
  };

  const getWidgetLink = (widgetKey) => {
    const links = {
      net_worth: '/dashboard',
      goals: '/goals',
      savings: '/savings',
      investments: '/investments',
      retirement: '/retirement',
      protection: '/protection',
      tax: '/tax',
      iht: '/iht'
    };
    return links[widgetKey] || '/';
  };

  const getMostUsedWidget = () => {
    if (!dashboard || dashboard.widget_order.length === 0) return null;
    return dashboard.widget_order[0];
  };

  if (loading) {
    return (
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px' }}>
        <Card style={{ padding: '32px', textAlign: 'center' }}>
          <p style={{ color: '#94A3B8' }}>Loading your personalized dashboard...</p>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px' }}>
        <Alert variant="error" style={{ marginBottom: '24px' }}>
          {error}
        </Alert>
        <Button onClick={loadDashboard}>Try Again</Button>
      </div>
    );
  }

  const mostUsedWidget = getMostUsedWidget();

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px' }}>
      {/* Track page view */}
      <BehaviorTracker page="personalized_dashboard" />

      {/* Narrative Introduction */}
      <Card style={{ padding: '32px', marginBottom: '48px', lineHeight: '1.7' }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: '16px', color: '#0F172A' }}>
          Your personalized dashboard
        </h2>
        <p style={{ color: '#475569', marginBottom: '16px' }}>
          Your dashboard adapts to how you use GoalPlan. We've organized it to show{' '}
          <strong>the features you use most</strong>, making it easier to focus on what matters to you.
        </p>
        {mostUsedWidget && (
          <p style={{ color: '#475569', marginBottom: '0' }}>
            Based on your activity over the last 30 days, we've placed{' '}
            <strong style={{ color: '#2563EB' }}>{getWidgetDisplayName(mostUsedWidget)}</strong> at the top.{' '}
            {dashboard.hidden_widgets.length > 0 && (
              <span>
                We've also hidden <strong>{dashboard.hidden_widgets.length}</strong> section
                {dashboard.hidden_widgets.length > 1 ? 's' : ''} you use less often to keep things simple.
              </span>
            )}
          </p>
        )}
      </Card>

      {/* Main Dashboard Widgets */}
      <div style={{ marginBottom: '48px' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '24px', color: '#0F172A' }}>
          Your financial sections
        </h3>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '24px',
          marginBottom: '24px'
        }}>
          {dashboard.visible_widgets.map((widget, index) => (
            <Card
              key={widget}
              style={{
                padding: '24px',
                cursor: 'pointer',
                transition: 'all 150ms ease-in-out',
                border: index === 0 ? '2px solid #2563EB' : '1px solid #E2E8F0'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.07)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.06)';
              }}
              onClick={() => window.location.href = getWidgetLink(widget)}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <h4 style={{ fontSize: '1rem', fontWeight: 600, color: '#0F172A', margin: 0 }}>
                  {getWidgetDisplayName(widget)}
                </h4>
                {index === 0 && (
                  <Badge style={{ backgroundColor: '#EFF6FF', color: '#2563EB', fontSize: '0.75rem' }}>
                    Most Used
                  </Badge>
                )}
              </div>
              <p style={{ fontSize: '0.875rem', color: '#64748B', margin: 0 }}>
                Click to explore →
              </p>
            </Card>
          ))}
        </div>

        {/* Hidden Widgets - Progressive Disclosure */}
        {dashboard.hidden_widgets.length > 0 && (
          <div>
            <Button
              variant="ghost"
              onClick={() => setShowHiddenWidgets(!showHiddenWidgets)}
              style={{ marginBottom: '16px' }}
            >
              {showHiddenWidgets ? '▼' : '▶'} Show {dashboard.hidden_widgets.length} less-used section
              {dashboard.hidden_widgets.length > 1 ? 's' : ''}
            </Button>

            {showHiddenWidgets && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                gap: '24px',
                marginTop: '16px'
              }}>
                {dashboard.hidden_widgets.map((widget) => (
                  <Card
                    key={widget}
                    style={{
                      padding: '24px',
                      cursor: 'pointer',
                      opacity: 0.7,
                      transition: 'all 150ms ease-in-out'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.opacity = '1';
                      e.currentTarget.style.transform = 'translateY(-2px)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.opacity = '0.7';
                      e.currentTarget.style.transform = 'translateY(0)';
                    }}
                    onClick={() => window.location.href = getWidgetLink(widget)}
                  >
                    <h4 style={{ fontSize: '1rem', fontWeight: 600, color: '#64748B', marginBottom: '8px' }}>
                      {getWidgetDisplayName(widget)}
                    </h4>
                    <p style={{ fontSize: '0.875rem', color: '#94A3B8', margin: 0 }}>
                      Click to explore →
                    </p>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Personalized Insights Feed */}
      <div style={{ marginTop: '48px' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '24px', color: '#0F172A' }}>
          Personalized insights for you
        </h3>
        <InsightsFeed limit={5} />
      </div>

      {/* Customization Callout */}
      <Card style={{
        padding: '24px',
        marginTop: '48px',
        backgroundColor: '#F8FAFC',
        border: '1px solid #E2E8F0'
      }}>
        <h4 style={{ fontSize: '1rem', fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>
          💡 Customize your experience
        </h4>
        <p style={{ color: '#475569', marginBottom: '16px', lineHeight: '1.7' }}>
          Your dashboard personalizes automatically based on what you use. Want more control?{' '}
          Visit settings to customize currency, notifications, and display preferences.
        </p>
        <Button
          variant="secondary"
          onClick={() => window.location.href = '/settings/personalization'}
        >
          Open Personalization Settings →
        </Button>
      </Card>
    </div>
  );
}
