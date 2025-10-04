import React, { useState, useEffect } from 'react';
import { Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * MonthlyInsights - Auto-loaded monthly financial summary
 *
 * Features:
 * - Auto-loads on component mount
 * - Wins section (highlights)
 * - Concerns section (areas needing attention)
 * - Trends section (what we noticed)
 * - Recommendations (what to do next)
 * - Visual progress indicators
 */
export function MonthlyInsights() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [insights, setInsights] = useState(null);

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/v1/ai/monthly-insights', {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!res.ok) {
        if (res.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }

        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to load monthly insights.');
      }

      const data = await res.json();
      setInsights(data);
    } catch (err) {
      setError(err.message || 'Failed to load monthly insights. Please try again.');
      console.error('Error loading insights:', err);
    } finally {
      setLoading(false);
    }
  };

  // Styles
  const containerStyle = {
    maxWidth: '900px',
    margin: '0 auto',
  };

  const narrativeSectionStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
    lineHeight: '1.7',
  };

  const headingStyle = {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '16px',
  };

  const sectionHeadingStyle = {
    fontSize: '1rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '12px',
    marginTop: '24px',
  };

  const paragraphStyle = {
    color: '#475569',
    marginBottom: '16px',
    lineHeight: '1.7',
  };

  const listStyle = {
    listStyleType: 'disc',
    paddingLeft: '24px',
    color: '#475569',
    lineHeight: '1.7',
  };

  const listItemStyle = {
    marginBottom: '8px',
  };

  const winItemStyle = {
    display: 'flex',
    alignItems: 'flex-start',
    marginBottom: '12px',
    padding: '12px',
    backgroundColor: '#D1FAE5',
    borderRadius: '8px',
    border: '1px solid #10B981',
  };

  const concernItemStyle = {
    display: 'flex',
    alignItems: 'flex-start',
    marginBottom: '12px',
    padding: '12px',
    backgroundColor: '#FEF3C7',
    borderRadius: '8px',
    border: '1px solid #F59E0B',
  };

  const trendItemStyle = {
    display: 'flex',
    alignItems: 'flex-start',
    marginBottom: '12px',
    padding: '12px',
    backgroundColor: '#EFF6FF',
    borderRadius: '8px',
    border: '1px solid #3B82F6',
  };

  const iconStyle = {
    fontSize: '1.5rem',
    marginRight: '12px',
    flexShrink: 0,
  };

  const textStyle = {
    flex: 1,
    color: '#0F172A',
    lineHeight: '1.6',
  };

  const skeletonCardStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
  };

  const skeletonLineStyle = (width) => ({
    height: '16px',
    backgroundColor: '#E2E8F0',
    borderRadius: '4px',
    width: width,
    marginBottom: '12px',
    animation: 'pulse 1.5s ease-in-out infinite',
  });

  // Loading state
  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={skeletonCardStyle}>
          <div style={skeletonLineStyle('40%')}></div>
          <div style={skeletonLineStyle('80%')}></div>
          <div style={skeletonLineStyle('60%')}></div>
          <div style={{ ...skeletonLineStyle('70%'), marginTop: '24px' }}></div>
          <div style={skeletonLineStyle('90%')}></div>
        </div>

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
      <div style={containerStyle}>
        <Alert variant="error">
          <p style={{ fontWeight: 600 }}>Unable to Load Insights</p>
          <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
        </Alert>
      </div>
    );
  }

  // No insights available
  if (!insights || (!insights.wins?.length && !insights.concerns?.length && !insights.trends?.length)) {
    return (
      <div style={containerStyle}>
        <div style={narrativeSectionStyle}>
          <h3 style={headingStyle}>Your Monthly Financial Summary</h3>
          <p style={paragraphStyle}>
            Check back at the start of next month for your personalized financial summary.
            I'll analyze your progress, highlight wins, and identify areas for improvement.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      {/* Introduction */}
      <div style={narrativeSectionStyle}>
        <h3 style={headingStyle}>Your Monthly Financial Summary</h3>
        <p style={paragraphStyle}>
          Here's your personalized financial summary for this month. I've analyzed your accounts,
          investments, and progress toward your goals to give you a clear picture of where you stand.
        </p>
      </div>

      {/* Wins Section */}
      {insights.wins && insights.wins.length > 0 && (
        <div style={narrativeSectionStyle}>
          <h4 style={sectionHeadingStyle}>This Month's Highlights</h4>
          <p style={paragraphStyle}>Great progress in these areas:</p>

          {insights.wins.map((win, idx) => (
            <div key={idx} style={winItemStyle}>
              <span style={iconStyle}>✓</span>
              <span style={textStyle}>{win}</span>
            </div>
          ))}
        </div>
      )}

      {/* Concerns Section */}
      {insights.concerns && insights.concerns.length > 0 && (
        <div style={narrativeSectionStyle}>
          <h4 style={sectionHeadingStyle}>Areas Needing Attention</h4>
          <p style={paragraphStyle}>Let's focus on improving these:</p>

          {insights.concerns.map((concern, idx) => (
            <div key={idx} style={concernItemStyle}>
              <span style={iconStyle}>⚠</span>
              <span style={textStyle}>{concern}</span>
            </div>
          ))}
        </div>
      )}

      {/* Trends Section */}
      {insights.trends && insights.trends.length > 0 && (
        <div style={narrativeSectionStyle}>
          <h4 style={sectionHeadingStyle}>What We Noticed</h4>
          <p style={paragraphStyle}>Interesting patterns in your finances:</p>

          {insights.trends.map((trend, idx) => (
            <div key={idx} style={trendItemStyle}>
              <span style={iconStyle}>📊</span>
              <span style={textStyle}>{trend}</span>
            </div>
          ))}
        </div>
      )}

      {/* Recommendations */}
      {insights.recommendations && insights.recommendations.length > 0 && (
        <div style={narrativeSectionStyle}>
          <h4 style={sectionHeadingStyle}>What to Do Next</h4>
          <p style={paragraphStyle}>
            Based on this month's analysis, here are my top recommendations:
          </p>

          <ul style={listStyle}>
            {insights.recommendations.map((rec, idx) => (
              <li key={idx} style={listItemStyle}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
