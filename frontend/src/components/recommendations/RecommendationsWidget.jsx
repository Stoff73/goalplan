import React, { useState, useEffect } from 'react';
import { Card, Badge } from 'internal-packages-ui';
import { authStorage } from '../../utils/auth';

/**
 * RecommendationsWidget - Compact widget for displaying top HIGH priority recommendations
 *
 * Features:
 * - Shows top 3 HIGH priority recommendations only
 * - Compact card design for dashboard integration
 * - Priority badge, truncated title, potential savings
 * - "View All Recommendations" link at bottom
 * - Auto-refresh every 5 minutes (optional)
 *
 * Design Principles:
 * - Follows STYLEGUIDE.md narrative approach
 * - Conversational, second-person language
 * - Color-coded priority for visual urgency
 * - Generous white space for readability
 */
export function RecommendationsWidget() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadRecommendations();

    // Auto-refresh every 5 minutes (optional)
    const interval = setInterval(loadRecommendations, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const loadRecommendations = async () => {
    setError(null);

    try {
      const response = await fetch('/api/v1/recommendations/?priority=HIGH', {
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
        throw new Error('Failed to fetch recommendations');
      }

      const data = await response.json();
      // Take top 3 HIGH priority recommendations
      const topThree = (data.recommendations || [])
        .filter((rec) => rec.priority === 'HIGH')
        .slice(0, 3);
      setRecommendations(topThree);
    } catch (err) {
      setError('Failed to load recommendations');
      console.error('Error loading recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const truncateTitle = (title, maxLength = 60) => {
    if (title.length <= maxLength) return title;
    return title.substring(0, maxLength) + '...';
  };

  const formatCurrency = (amount, currency = 'GBP') => {
    if (!amount) return null;
    const symbol = currency === 'GBP' ? '£' : currency === 'ZAR' ? 'R' : currency;
    return `${symbol}${amount.toLocaleString('en-GB', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })}`;
  };

  const getPriorityBadgeStyle = (priority) => {
    const styles = {
      HIGH: {
        backgroundColor: '#FEE2E2',
        borderColor: '#EF4444',
        color: '#991B1B',
      },
      MEDIUM: {
        backgroundColor: '#FEF3C7',
        borderColor: '#F59E0B',
        color: '#92400E',
      },
      LOW: {
        backgroundColor: '#D1FAE5',
        borderColor: '#10B981',
        color: '#065F46',
      },
    };
    return styles[priority] || styles.LOW;
  };

  // Styles following STYLEGUIDE.md
  const widgetContainerStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    lineHeight: '1.7',
  };

  const headingStyle = {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '16px',
  };

  const subheadingStyle = {
    fontSize: '0.95rem',
    color: '#475569',
    marginBottom: '24px',
    lineHeight: '1.7',
  };

  const recommendationItemStyle = {
    padding: '16px',
    backgroundColor: '#F8FAFC',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
    marginBottom: '12px',
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px',
  };

  const priorityBadgeStyle = (priority) => ({
    padding: '4px 8px',
    borderRadius: '9999px',
    fontSize: '0.65rem',
    fontWeight: 600,
    border: `1px solid ${getPriorityBadgeStyle(priority).borderColor}`,
    ...getPriorityBadgeStyle(priority),
    flexShrink: 0,
  });

  const titleStyle = {
    fontSize: '0.95rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '4px',
  };

  const savingsTextStyle = {
    fontSize: '0.875rem',
    color: '#10B981',
    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace',
    fontWeight: 600,
  };

  const viewAllLinkStyle = {
    display: 'block',
    textAlign: 'center',
    marginTop: '16px',
    padding: '12px',
    color: '#2563EB',
    textDecoration: 'none',
    fontWeight: 500,
    fontSize: '0.95rem',
    borderRadius: '8px',
    transition: 'background-color 0.15s',
  };

  const emptyStateStyle = {
    textAlign: 'center',
    padding: '32px 16px',
    color: '#94A3B8',
  };

  const skeletonItemStyle = {
    padding: '16px',
    backgroundColor: '#F8FAFC',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
    marginBottom: '12px',
    animation: 'pulse 1.5s ease-in-out infinite',
  };

  const skeletonLineStyle = (width) => ({
    height: '12px',
    backgroundColor: '#E2E8F0',
    borderRadius: '4px',
    width: width,
    marginBottom: '8px',
  });

  // Loading state
  if (loading) {
    return (
      <div style={widgetContainerStyle}>
        <h3 style={headingStyle}>Recommended Actions</h3>
        <p style={subheadingStyle}>Loading your top priorities...</p>

        {[1, 2, 3].map((i) => (
          <div key={i} style={skeletonItemStyle}>
            <div style={skeletonLineStyle('30%')}></div>
            <div style={skeletonLineStyle('80%')}></div>
          </div>
        ))}

        <style>{`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}</style>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={widgetContainerStyle}>
        <h3 style={headingStyle}>Recommended Actions</h3>
        <div style={emptyStateStyle}>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  // Empty state - no high priority recommendations
  if (recommendations.length === 0) {
    return (
      <div style={widgetContainerStyle}>
        <h3 style={headingStyle}>Recommended Actions</h3>
        <div style={emptyStateStyle}>
          <div style={{ fontSize: '2rem', marginBottom: '12px' }}>✓</div>
          <p style={{ fontSize: '0.95rem', color: '#475569', lineHeight: '1.7' }}>
            No urgent recommendations right now. You're managing your finances well!
          </p>
          <a
            href="/recommendations"
            style={{
              ...viewAllLinkStyle,
              marginTop: '16px',
              display: 'inline-block',
            }}
            onMouseEnter={(e) => (e.target.style.backgroundColor = '#EFF6FF')}
            onMouseLeave={(e) => (e.target.style.backgroundColor = 'transparent')}
          >
            View All Recommendations →
          </a>
        </div>
      </div>
    );
  }

  // Main widget with recommendations
  return (
    <div style={widgetContainerStyle}>
      <h3 style={headingStyle}>Recommended Actions</h3>
      <p style={subheadingStyle}>
        Here {recommendations.length === 1 ? 'is' : 'are'} your top {recommendations.length} high-priority {recommendations.length === 1 ? 'recommendation' : 'recommendations'} to help optimize your financial position:
      </p>

      {recommendations.map((rec) => (
        <div key={rec.id} style={recommendationItemStyle}>
          {/* Priority Badge */}
          <div style={priorityBadgeStyle(rec.priority)}>
            {rec.priority}
          </div>

          {/* Content */}
          <div style={{ flex: 1 }}>
            <div style={titleStyle}>{truncateTitle(rec.title)}</div>

            {/* Potential Savings */}
            {rec.estimated_benefit && rec.estimated_benefit.amount_gbp && (
              <div style={savingsTextStyle}>
                Could save you {formatCurrency(rec.estimated_benefit.amount_gbp, rec.estimated_benefit.currency || 'GBP')}
              </div>
            )}
          </div>
        </div>
      ))}

      {/* View All Link */}
      <a
        href="/recommendations"
        style={viewAllLinkStyle}
        onMouseEnter={(e) => (e.target.style.backgroundColor = '#EFF6FF')}
        onMouseLeave={(e) => (e.target.style.backgroundColor = 'transparent')}
      >
        View All Recommendations →
      </a>
    </div>
  );
}
