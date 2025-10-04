import React, { useState, useEffect } from 'react';
import { Card, Badge, Button, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * InsightsFeed - Display personalized insights ranked by relevance
 *
 * Follows STYLEGUIDE.md narrative storytelling approach:
 * - Introduction: "Here's what we noticed about your finances"
 * - Each insight with type badge and relevance indicator
 * - Dismiss functionality
 * - Click tracking
 * - Empty state with encouraging message
 * - Line height 1.7, generous spacing
 *
 * Features:
 * - Show top insights ordered by relevance
 * - Dismiss insights
 * - Track which insights are clicked
 * - Refresh insights
 */
export function InsightsFeed({ limit = 5 }) {
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadInsights();
  }, [limit]);

  async function loadInsights() {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/personalization/insights?limit=${limit}`, {
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
        throw new Error('Failed to load insights');
      }

      const data = await response.json();
      setInsights(data);
    } catch (err) {
      setError('Unable to load personalized insights. Please try again.');
      console.error('Error loading insights:', err);
    } finally {
      setLoading(false);
    }
  }

  async function trackInsightAction(insightId, action) {
    try {
      await fetch('/api/v1/personalization/behavior/track', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({
          action_type: 'INSIGHT_INTERACTION',
          action_context: {
            insight_id: insightId,
            action: action,
          },
        }),
      });
    } catch (err) {
      console.error('Error tracking insight action:', err);
    }
  }

  async function dismissInsight(insightId) {
    // Track dismissal
    await trackInsightAction(insightId, 'dismissed');

    // Remove from UI
    setInsights(insights.filter(insight => insight.id !== insightId));
  }

  async function clickInsight(insightId) {
    // Track click
    await trackInsightAction(insightId, 'clicked');
  }

  const getInsightTypeBadge = (insightType) => {
    const badges = {
      GOAL_ADVICE: { text: 'Goal Advice', color: '#2563EB', bg: '#EFF6FF' },
      SAVINGS_TIP: { text: 'Savings Tip', color: '#10B981', bg: '#F0FDF4' },
      INVESTMENT_TIP: { text: 'Investment Tip', color: '#8B5CF6', bg: '#F5F3FF' },
      TAX_TIP: { text: 'Tax Tip', color: '#F59E0B', bg: '#FEF3C7' },
      SPENDING_INSIGHT: { text: 'Spending Insight', color: '#EF4444', bg: '#FEF2F2' },
    };

    const badge = badges[insightType] || { text: 'Insight', color: '#64748B', bg: '#F8FAFC' };

    return (
      <Badge style={{
        backgroundColor: badge.bg,
        color: badge.color,
        fontSize: '0.75rem',
        padding: '4px 8px'
      }}>
        {badge.text}
      </Badge>
    );
  };

  const getRelevanceColor = (score) => {
    if (score >= 80) return '#10B981'; // Green
    if (score >= 50) return '#F59E0B'; // Amber
    return '#94A3B8'; // Gray
  };

  const getRelevanceLabel = (score) => {
    if (score >= 80) return 'Highly relevant';
    if (score >= 50) return 'Moderately relevant';
    return 'May be relevant';
  };

  if (loading) {
    return (
      <Card style={{ padding: '24px', textAlign: 'center' }}>
        <p style={{ color: '#94A3B8' }}>Loading insights...</p>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="error">
        {error}
      </Alert>
    );
  }

  if (insights.length === 0) {
    return (
      <Card style={{ padding: '32px', textAlign: 'center', lineHeight: '1.7' }}>
        <p style={{ fontSize: '2rem', marginBottom: '16px' }}>💡</p>
        <h4 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>
          No insights yet
        </h4>
        <p style={{ color: '#64748B', marginBottom: '16px' }}>
          We're still learning about your financial patterns. Check back soon for personalized insights
          tailored to your situation.
        </p>
        <Button variant="secondary" onClick={loadInsights}>
          Refresh Insights
        </Button>
      </Card>
    );
  }

  return (
    <div>
      {/* Introduction */}
      <p style={{ color: '#475569', marginBottom: '24px', lineHeight: '1.7' }}>
        Here's what we noticed about your finances. These insights are personalized based on your goals,
        behavior, and financial data.
      </p>

      {/* Insights List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {insights.map((insight) => (
          <Card
            key={insight.id}
            style={{
              padding: '24px',
              border: '1px solid #E2E8F0',
              cursor: 'pointer',
              transition: 'all 150ms ease-in-out'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#2563EB';
              e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.07)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#E2E8F0';
              e.currentTarget.style.boxShadow = 'none';
            }}
            onClick={() => clickInsight(insight.id)}
          >
            {/* Header with badge and relevance */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '12px',
              flexWrap: 'wrap',
              gap: '8px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '1.2rem' }}>💡</span>
                {getInsightTypeBadge(insight.insight_type)}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div
                  style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: getRelevanceColor(parseFloat(insight.relevance_score))
                  }}
                />
                <span style={{
                  fontSize: '0.75rem',
                  color: getRelevanceColor(parseFloat(insight.relevance_score)),
                  fontWeight: 500
                }}>
                  {Math.round(parseFloat(insight.relevance_score))}% relevant
                </span>
              </div>
            </div>

            {/* Insight text */}
            <p style={{
              color: '#0F172A',
              lineHeight: '1.7',
              marginBottom: '12px',
              fontSize: '0.95rem'
            }}>
              {insight.insight_text}
            </p>

            {/* Actions */}
            <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
              <Button
                variant="ghost"
                onClick={(e) => {
                  e.stopPropagation();
                  dismissInsight(insight.id);
                }}
                style={{ fontSize: '0.875rem', padding: '4px 12px' }}
              >
                Dismiss
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Refresh button */}
      <div style={{ marginTop: '24px', textAlign: 'center' }}>
        <Button variant="secondary" onClick={loadInsights}>
          Refresh Insights
        </Button>
      </div>
    </div>
  );
}
