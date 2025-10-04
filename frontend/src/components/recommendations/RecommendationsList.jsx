import React, { useState, useEffect } from 'react';
import { Card, Badge, Button, Alert } from 'internal-packages-ui';
import { authStorage } from '../../utils/auth';

/**
 * RecommendationsList - Display financial recommendations with narrative storytelling
 *
 * Features:
 * - Recommendations displayed as cards with priority badges
 * - Filter by priority and type
 * - Dismiss and complete actions
 * - Empty states and loading states
 * - Follows STYLEGUIDE.md narrative approach
 *
 * Design Principles:
 * - Conversational, educational tone
 * - Color-coded priority (HIGH=red, MEDIUM=amber, LOW=green)
 * - Generous white space and accessibility
 * - Progressive disclosure for action items
 */
export function RecommendationsList() {
  const [recommendations, setRecommendations] = useState([]);
  const [filteredRecommendations, setFilteredRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterPriority, setFilterPriority] = useState('All');
  const [filterType, setFilterType] = useState('All');
  const [expandedRecommendations, setExpandedRecommendations] = useState({});
  const [dismissingId, setDismissingId] = useState(null);
  const [completingId, setCompletingId] = useState(null);

  useEffect(() => {
    loadRecommendations();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [recommendations, filterPriority, filterType]);

  const loadRecommendations = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/recommendations/', {
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
      setRecommendations(data.recommendations || []);
    } catch (err) {
      setError('Failed to load recommendations. Please try again.');
      console.error('Error loading recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...recommendations];

    // Filter by priority
    if (filterPriority !== 'All') {
      filtered = filtered.filter((rec) => rec.priority === filterPriority);
    }

    // Filter by type
    if (filterType !== 'All') {
      filtered = filtered.filter((rec) => rec.category === filterType);
    }

    // Sort by priority (HIGH first), then date
    const priorityOrder = { HIGH: 1, MEDIUM: 2, LOW: 3 };
    filtered.sort((a, b) => {
      const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
      if (priorityDiff !== 0) return priorityDiff;
      return new Date(b.generated_at) - new Date(a.generated_at);
    });

    setFilteredRecommendations(filtered);
  };

  const handleDismiss = async (id) => {
    if (!window.confirm('Are you sure you want to dismiss this recommendation?')) {
      return;
    }

    setDismissingId(id);

    try {
      const response = await fetch(`/api/v1/recommendations/${id}/dismiss`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to dismiss recommendation');
      }

      // Remove from list with fade-out (immediate visual feedback)
      setRecommendations((prev) => prev.filter((rec) => rec.id !== id));
    } catch (err) {
      alert('Failed to dismiss recommendation. Please try again.');
      console.error('Error dismissing recommendation:', err);
    } finally {
      setDismissingId(null);
    }
  };

  const handleComplete = async (id) => {
    if (!window.confirm('Mark this recommendation as completed?')) {
      return;
    }

    setCompletingId(id);

    try {
      const response = await fetch(`/api/v1/recommendations/${id}/complete`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to complete recommendation');
      }

      // Show success badge, then fade out after 2 seconds
      setRecommendations((prev) =>
        prev.map((rec) =>
          rec.id === id ? { ...rec, status: 'COMPLETED' } : rec
        )
      );

      setTimeout(() => {
        setRecommendations((prev) => prev.filter((rec) => rec.id !== id));
      }, 2000);
    } catch (err) {
      alert('Failed to mark recommendation as complete. Please try again.');
      console.error('Error completing recommendation:', err);
    } finally {
      setCompletingId(null);
    }
  };

  const toggleActionItems = (id) => {
    setExpandedRecommendations((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
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
  const containerStyle = {
    maxWidth: '1280px',
    margin: '0 auto',
    padding: '32px 16px',
  };

  const pageHeadingStyle = {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#0F172A',
    marginBottom: '16px',
  };

  const pageSubheadingStyle = {
    fontSize: '1.1rem',
    color: '#475569',
    marginBottom: '32px',
    lineHeight: '1.7',
  };

  const filterContainerStyle = {
    display: 'flex',
    gap: '16px',
    marginBottom: '32px',
    flexWrap: 'wrap',
  };

  const selectStyle = {
    padding: '8px 12px',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
    fontSize: '0.875rem',
    color: '#0F172A',
    backgroundColor: '#FFFFFF',
    cursor: 'pointer',
  };

  const recommendationCardStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
    lineHeight: '1.7',
    position: 'relative',
  };

  const priorityBadgeStyle = (priority) => ({
    position: 'absolute',
    top: '16px',
    right: '16px',
    padding: '4px 12px',
    borderRadius: '9999px',
    fontSize: '0.75rem',
    fontWeight: 600,
    border: `1px solid ${getPriorityBadgeStyle(priority).borderColor}`,
    ...getPriorityBadgeStyle(priority),
  });

  const titleStyle = {
    fontSize: '1.2rem',
    fontWeight: 'bold',
    color: '#0F172A',
    marginBottom: '12px',
    marginRight: '120px', // Space for badge
  };

  const descriptionStyle = {
    color: '#475569',
    marginBottom: '16px',
    lineHeight: '1.7',
    fontSize: '1rem',
  };

  const savingsBadgeStyle = {
    display: 'inline-block',
    padding: '8px 16px',
    backgroundColor: '#D1FAE5',
    borderRadius: '8px',
    border: '1px solid #10B981',
    marginTop: '12px',
  };

  const savingsTextStyle = {
    fontSize: '0.75rem',
    color: '#065F46',
    marginBottom: '2px',
  };

  const savingsValueStyle = {
    fontSize: '1.1rem',
    fontWeight: 'bold',
    color: '#10B981',
    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace',
  };

  const actionItemsContainerStyle = {
    marginTop: '16px',
    padding: '16px',
    backgroundColor: '#F8FAFC',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
  };

  const expandTriggerStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: 500,
    color: '#2563EB',
    padding: '0',
    background: 'none',
    border: '0',
    width: '100%',
    marginBottom: '12px',
  };

  const actionButtonsStyle = {
    display: 'flex',
    gap: '12px',
    marginTop: '24px',
  };

  const emptyStateStyle = {
    padding: '64px 32px',
    textAlign: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
  };

  const skeletonCardStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
    animation: 'pulse 1.5s ease-in-out infinite',
  };

  const skeletonLineStyle = (width) => ({
    height: '16px',
    backgroundColor: '#E2E8F0',
    borderRadius: '4px',
    width: width,
    marginBottom: '12px',
  });

  // Loading state - skeleton cards
  if (loading) {
    return (
      <div style={containerStyle}>
        <h1 style={pageHeadingStyle}>Your Recommended Actions</h1>
        <p style={pageSubheadingStyle}>
          Loading your personalized recommendations...
        </p>

        {[1, 2, 3].map((i) => (
          <div key={i} style={skeletonCardStyle}>
            <div style={skeletonLineStyle('40%')}></div>
            <div style={skeletonLineStyle('80%')}></div>
            <div style={skeletonLineStyle('60%')}></div>
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
      <div style={containerStyle}>
        <h1 style={pageHeadingStyle}>Your Recommended Actions</h1>
        <Alert variant="error">
          <p style={{ fontWeight: 600 }}>Error Loading Recommendations</p>
          <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
        </Alert>
        <Button
          variant="outline"
          onClick={loadRecommendations}
          style={{ marginTop: '16px' }}
        >
          Try Again
        </Button>
      </div>
    );
  }

  // Empty state - no recommendations
  if (recommendations.length === 0) {
    return (
      <div style={containerStyle}>
        <h1 style={pageHeadingStyle}>Your Recommended Actions</h1>
        <p style={pageSubheadingStyle}>
          Check back for personalized recommendations based on your financial situation.
        </p>

        <div style={emptyStateStyle}>
          <div style={{ fontSize: '4rem', marginBottom: '24px' }}>✓</div>
          <h3 style={{ fontSize: '1.5rem', fontWeight: 600, color: '#0F172A', marginBottom: '16px' }}>
            Great job! You're making the most of your finances.
          </h3>
          <p style={{ color: '#475569', lineHeight: '1.7', marginBottom: '24px', maxWidth: '600px', margin: '0 auto 24px' }}>
            We'll check back regularly for new opportunities to help you optimize your financial position.
            Our recommendations are based on your income, savings, investments, and tax situation.
          </p>
          <Button variant="primary" onClick={loadRecommendations}>
            Generate Recommendations
          </Button>
        </div>
      </div>
    );
  }

  // Main view with recommendations
  return (
    <div style={containerStyle}>
      <h1 style={pageHeadingStyle}>Your Recommended Actions</h1>
      <p style={pageSubheadingStyle}>
        Based on your financial situation, we've identified {filteredRecommendations.length} {filteredRecommendations.length === 1 ? 'recommendation' : 'recommendations'} to help you optimize your finances.
      </p>

      {/* Filters */}
      <div style={filterContainerStyle}>
        <div>
          <label htmlFor="priority-filter" style={{ display: 'block', fontSize: '0.75rem', color: '#475569', marginBottom: '4px' }}>
            Filter by Priority
          </label>
          <select
            id="priority-filter"
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            style={selectStyle}
          >
            <option value="All">All Priorities</option>
            <option value="HIGH">High Priority</option>
            <option value="MEDIUM">Medium Priority</option>
            <option value="LOW">Low Priority</option>
          </select>
        </div>

        <div>
          <label htmlFor="type-filter" style={{ display: 'block', fontSize: '0.75rem', color: '#475569', marginBottom: '4px' }}>
            Filter by Type
          </label>
          <select
            id="type-filter"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            style={selectStyle}
          >
            <option value="All">All Types</option>
            <option value="PROTECTION">Protection</option>
            <option value="SAVINGS">Savings</option>
            <option value="INVESTMENT">Investment</option>
            <option value="RETIREMENT">Retirement</option>
            <option value="TAX">Tax Efficiency</option>
            <option value="IHT">IHT Planning</option>
          </select>
        </div>
      </div>

      {/* Recommendations List */}
      {filteredRecommendations.map((rec) => (
        <div
          key={rec.id}
          style={{
            ...recommendationCardStyle,
            opacity: rec.status === 'COMPLETED' ? 0.6 : 1,
            transition: 'opacity 0.3s ease-in-out',
          }}
        >
          {/* Priority Badge */}
          <div style={priorityBadgeStyle(rec.priority)}>
            {rec.priority}
          </div>

          {/* Completed Badge (if applicable) */}
          {rec.status === 'COMPLETED' && (
            <div
              style={{
                position: 'absolute',
                top: '60px',
                right: '16px',
                padding: '4px 12px',
                borderRadius: '9999px',
                fontSize: '0.75rem',
                fontWeight: 600,
                backgroundColor: '#D1FAE5',
                color: '#065F46',
                border: '1px solid #10B981',
              }}
            >
              ✓ Completed
            </div>
          )}

          {/* Title */}
          <h3 style={titleStyle}>{rec.title}</h3>

          {/* Description */}
          <p style={descriptionStyle}>{rec.description}</p>

          {/* Potential Savings */}
          {rec.estimated_benefit && rec.estimated_benefit.amount_gbp && (
            <div style={savingsBadgeStyle}>
              <div style={savingsTextStyle}>Potential savings</div>
              <div style={savingsValueStyle}>
                {formatCurrency(rec.estimated_benefit.amount_gbp, rec.estimated_benefit.currency || 'GBP')}
                {rec.estimated_benefit.description && ` - ${rec.estimated_benefit.description}`}
              </div>
            </div>
          )}

          {/* Action Items (Expandable) */}
          {rec.reasoning && rec.reasoning.length > 0 && (
            <div style={actionItemsContainerStyle}>
              <button
                onClick={() => toggleActionItems(rec.id)}
                style={expandTriggerStyle}
                aria-expanded={expandedRecommendations[rec.id]}
              >
                <span>Why this matters</span>
                <span style={{ fontSize: '0.75rem' }}>
                  {expandedRecommendations[rec.id] ? '▼' : '▶'}
                </span>
              </button>

              {expandedRecommendations[rec.id] && (
                <ol style={{ paddingLeft: '20px', color: '#475569', lineHeight: '1.7', marginTop: '8px' }}>
                  {rec.reasoning.map((reason, idx) => (
                    <li key={idx} style={{ marginBottom: '8px' }}>{reason}</li>
                  ))}
                </ol>
              )}
            </div>
          )}

          {/* Action Buttons */}
          {rec.status !== 'COMPLETED' && (
            <div style={actionButtonsStyle}>
              <Button
                variant="outline"
                onClick={() => handleDismiss(rec.id)}
                disabled={dismissingId === rec.id}
              >
                {dismissingId === rec.id ? 'Dismissing...' : 'Dismiss'}
              </Button>
              <Button
                variant="primary"
                onClick={() => handleComplete(rec.id)}
                disabled={completingId === rec.id}
              >
                {completingId === rec.id ? 'Completing...' : 'Mark Complete'}
              </Button>
            </div>
          )}
        </div>
      ))}

      {/* No results after filtering */}
      {filteredRecommendations.length === 0 && recommendations.length > 0 && (
        <div style={emptyStateStyle}>
          <p style={{ color: '#475569', lineHeight: '1.7' }}>
            No recommendations match your current filters. Try adjusting the filters above.
          </p>
        </div>
      )}
    </div>
  );
}
