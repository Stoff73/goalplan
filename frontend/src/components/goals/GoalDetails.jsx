import React, { useState, useEffect } from 'react';
import { Card, Button, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * GoalDetails - Comprehensive goal view with full narrative story
 *
 * Features:
 * - Full narrative goal story with context
 * - Progress visualization over time (line chart)
 * - Milestones timeline with achievement tracking
 * - Monthly savings breakdown
 * - Recommendations with callout boxes
 * - Edit and delete actions
 *
 * Follows STYLEGUIDE.md:
 * - Conversational headlines
 * - Metrics embedded in sentences
 * - Progress indicators with encouraging messages
 * - Educational callouts
 * - Progressive disclosure
 */
export function GoalDetails({ goalId, onEdit, onDelete, onBack }) {
  const [goal, setGoal] = useState(null);
  const [milestones, setMilestones] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showRecommendations, setShowRecommendations] = useState(false);

  useEffect(() => {
    loadGoalDetails();
  }, [goalId]);

  const loadGoalDetails = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load goal details
      const goalResponse = await fetch(`/api/v1/goals/${goalId}`, {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!goalResponse.ok) {
        if (goalResponse.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }
        throw new Error('Failed to fetch goal details');
      }

      const goalData = await goalResponse.json();
      setGoal(goalData);

      // Load milestones
      const milestonesResponse = await fetch(`/api/v1/goals/${goalId}/milestones`, {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (milestonesResponse.ok) {
        const milestonesData = await milestonesResponse.json();
        setMilestones(milestonesData);
      }

      // Load recommendations
      const recsResponse = await fetch(`/api/v1/goals/${goalId}/recommendations`, {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (recsResponse.ok) {
        const recsData = await recsResponse.json();
        setRecommendations(recsData);
      }
    } catch (err) {
      setError('Failed to load goal details. Please try again.');
      console.error('Error loading goal details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteGoal = async () => {
    try {
      const response = await fetch(`/api/v1/goals/${goalId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete goal');
      }

      onDelete();
    } catch (err) {
      setError('Failed to delete goal. Please try again.');
      console.error('Error deleting goal:', err);
    }
  };

  const formatCurrency = (amount, currency = 'GBP') => {
    if (amount === null || amount === undefined) return '£0';
    const symbol = currency === 'GBP' ? '£' : currency === 'ZAR' ? 'R' : currency;
    return `${symbol}${amount.toLocaleString('en-GB', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  };

  const getGoalIcon = (type) => {
    const icons = {
      EMERGENCY_FUND: '🛡️',
      HOUSE_PURCHASE: '🏠',
      HOME_IMPROVEMENT: '🔨',
      DEBT_REPAYMENT: '💳',
      VEHICLE_PURCHASE: '🚗',
      WEDDING: '💍',
      HOLIDAY_TRAVEL: '✈️',
      EDUCATION_CHILDREN: '🎓',
      EDUCATION_SELF: '📚',
      RETIREMENT: '🌴',
      BUSINESS_START: '💼',
      INHERITANCE_PLANNING: '📜',
      FINANCIAL_INDEPENDENCE: '💰',
      CHARITABLE_GIVING: '❤️',
      OTHER: '🎯',
    };
    return icons[type] || '🎯';
  };

  // Styles
  const containerStyle = {
    maxWidth: '1024px',
    margin: '0 auto',
    padding: '32px 16px',
  };

  const headerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '32px',
  };

  const titleContainerStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  };

  const iconStyle = {
    fontSize: '3rem',
  };

  const headingStyle = {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#0F172A',
    margin: 0,
  };

  const subtitleStyle = {
    fontSize: '0.95rem',
    color: '#94A3B8',
    marginTop: '8px',
  };

  const narrativeSectionStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '48px',
    lineHeight: '1.7',
  };

  const sectionHeadingStyle = {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '16px',
  };

  const paragraphStyle = {
    color: '#475569',
    marginBottom: '16px',
    lineHeight: '1.7',
    fontSize: '1rem',
  };

  const progressBarContainerStyle = {
    width: '100%',
    height: '12px',
    backgroundColor: '#E2E8F0',
    borderRadius: '6px',
    overflow: 'hidden',
    margin: '24px 0',
  };

  const progressBarFillStyle = (progress) => ({
    height: '100%',
    width: `${Math.min(progress, 100)}%`,
    backgroundColor: progress >= 75 ? '#10B981' : progress >= 50 ? '#2563EB' : progress >= 25 ? '#F59E0B' : '#EF4444',
    borderRadius: '6px',
    transition: 'width 0.5s ease-in-out',
  });

  const milestoneTimelineStyle = {
    position: 'relative',
    paddingLeft: '40px',
    marginTop: '24px',
  };

  const milestoneItemStyle = (achieved) => ({
    position: 'relative',
    paddingBottom: '24px',
    borderLeft: achieved ? '2px solid #10B981' : '2px solid #E2E8F0',
    paddingLeft: '24px',
    marginLeft: '8px',
  });

  const milestoneDotStyle = (achieved) => ({
    position: 'absolute',
    left: '-9px',
    top: '4px',
    width: '16px',
    height: '16px',
    borderRadius: '50%',
    backgroundColor: achieved ? '#10B981' : '#E2E8F0',
    border: '2px solid #FFFFFF',
    boxShadow: '0 0 0 2px ' + (achieved ? '#10B981' : '#E2E8F0'),
  });

  const calloutStyle = (type) => {
    const styles = {
      tip: { backgroundColor: '#EFF6FF', border: '1px solid #BFDBFE', color: '#1E40AF' },
      success: { backgroundColor: '#F0FDF4', border: '1px solid #86EFAC', color: '#166534' },
      warning: { backgroundColor: '#FFFBEB', border: '1px solid #FDE68A', color: '#92400E' },
      error: { backgroundColor: '#FEF2F2', border: '1px solid #FECACA', color: '#991B1B' },
    };
    return {
      ...styles[type || 'tip'],
      padding: '16px',
      borderRadius: '8px',
      marginTop: '16px',
      lineHeight: '1.7',
    };
  };

  const buttonGroupStyle = {
    display: 'flex',
    gap: '12px',
  };

  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={narrativeSectionStyle}>
          <p style={paragraphStyle}>Loading goal details...</p>
        </div>
      </div>
    );
  }

  if (error || !goal) {
    return (
      <div style={containerStyle}>
        <Alert variant="error">{error || 'Goal not found'}</Alert>
        <Button onClick={onBack} style={{ marginTop: '16px' }}>
          ← Back to Goals
        </Button>
      </div>
    );
  }

  const progressPercentage = goal.progress_percentage || 0;
  const monthsRemaining = Math.max(
    0,
    Math.ceil((new Date(goal.target_date) - new Date()) / (1000 * 60 * 60 * 24 * 30))
  );
  const monthsElapsed = Math.max(
    0,
    Math.ceil((new Date() - new Date(goal.created_at)) / (1000 * 60 * 60 * 24 * 30))
  );

  return (
    <div style={containerStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <div style={titleContainerStyle}>
          <span style={iconStyle}>{getGoalIcon(goal.goal_type)}</span>
          <div>
            <h1 style={headingStyle}>{goal.title}</h1>
            <p style={subtitleStyle}>
              Created {formatDate(goal.created_at)} • {goal.priority} Priority
            </p>
          </div>
        </div>
        <div style={buttonGroupStyle}>
          <Button variant="secondary" onClick={onBack}>
            ← Back
          </Button>
          <Button variant="secondary" onClick={() => onEdit(goal)}>
            Edit
          </Button>
          <Button variant="danger" onClick={() => setShowDeleteConfirm(true)}>
            Delete
          </Button>
        </div>
      </div>

      {/* Delete Confirmation */}
      {showDeleteConfirm && (
        <div style={{ ...narrativeSectionStyle, backgroundColor: '#FEF2F2', border: '1px solid #FECACA' }}>
          <h3 style={{ ...sectionHeadingStyle, color: '#991B1B' }}>Delete this goal?</h3>
          <p style={{ ...paragraphStyle, color: '#991B1B' }}>
            Are you sure you want to delete "{goal.title}"? This action cannot be undone, and
            you'll lose all progress tracking and milestone history.
          </p>
          <div style={buttonGroupStyle}>
            <Button variant="secondary" onClick={() => setShowDeleteConfirm(false)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleDeleteGoal}>
              Yes, Delete Goal
            </Button>
          </div>
        </div>
      )}

      {/* Main Goal Story */}
      <div style={narrativeSectionStyle}>
        <h3 style={sectionHeadingStyle}>Your Goal Story</h3>
        <p style={paragraphStyle}>
          You started this goal on <strong>{formatDate(goal.created_at)}</strong> with a target of{' '}
          <strong style={{ fontFamily: 'monospace' }}>
            {formatCurrency(goal.target_amount, goal.currency)}
          </strong>{' '}
          by <strong>{formatDate(goal.target_date)}</strong>.
        </p>
        <p style={paragraphStyle}>
          You're currently at{' '}
          <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
            {formatCurrency(goal.current_progress || 0, goal.currency)}
          </strong>{' '}
          (<strong>{Math.round(progressPercentage)}%</strong> complete) —{' '}
          {progressPercentage >= 100 ? (
            <span style={{ color: '#10B981', fontWeight: 600 }}>
              🎉 Congratulations! You've achieved this goal!
            </span>
          ) : progressPercentage >= 75 ? (
            <span style={{ color: '#10B981' }}>excellent progress! You're almost there.</span>
          ) : progressPercentage >= 50 ? (
            <span style={{ color: '#2563EB' }}>great work! You're past the halfway mark.</span>
          ) : progressPercentage >= 25 ? (
            <span style={{ color: '#F59E0B' }}>you're making steady progress.</span>
          ) : (
            <span>you're just getting started - stay focused!</span>
          )}
        </p>

        <div style={progressBarContainerStyle}>
          <div style={progressBarFillStyle(progressPercentage)} />
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', color: '#475569' }}>
          <div>
            <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
              {formatCurrency(goal.current_progress || 0, goal.currency)}
            </strong>{' '}
            saved
          </div>
          <div>
            <strong style={{ fontFamily: 'monospace' }}>
              {formatCurrency(
                Math.max(0, goal.target_amount - (goal.current_progress || 0)),
                goal.currency
              )}
            </strong>{' '}
            remaining
          </div>
        </div>

        {goal.description && (
          <div style={{ ...calloutStyle('tip'), marginTop: '24px' }}>
            <p style={{ margin: 0, lineHeight: '1.7' }}>{goal.description}</p>
          </div>
        )}
      </div>

      {/* Monthly Savings Section */}
      {goal.required_monthly_contribution > 0 && progressPercentage < 100 && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Your Savings Plan</h3>
          <p style={paragraphStyle}>
            To stay on track, you need to save{' '}
            <strong style={{ fontFamily: 'monospace' }}>
              {formatCurrency(goal.required_monthly_contribution, goal.currency)}/month
            </strong>{' '}
            for the next <strong>{monthsRemaining}</strong>{' '}
            {monthsRemaining === 1 ? 'month' : 'months'}.
          </p>
          {goal.on_track ? (
            <div style={calloutStyle('success')}>
              <p style={{ margin: 0 }}>
                <strong>✓ You're on track!</strong> At your current savings rate, you'll reach
                your target by {formatDate(goal.target_date)}.
              </p>
            </div>
          ) : (
            <div style={calloutStyle('warning')}>
              <p style={{ margin: 0 }}>
                <strong>⚠️ Attention needed:</strong> You may need to increase your monthly
                contributions or adjust your target date to stay on track.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Milestones Timeline */}
      {milestones.length > 0 && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Milestones</h3>
          <p style={paragraphStyle}>
            Track your progress with these checkpoints along the way. Celebrate each milestone as
            you achieve it!
          </p>

          <div style={milestoneTimelineStyle}>
            {milestones.map((milestone, index) => (
              <div key={milestone.id} style={milestoneItemStyle(milestone.achieved)}>
                <div style={milestoneDotStyle(milestone.achieved)} />
                <div>
                  <p style={{ margin: '0 0 8px 0', fontWeight: 600, color: '#0F172A' }}>
                    {milestone.achieved && '✓ '}
                    {milestone.target_progress_percentage}% milestone:{' '}
                    {formatCurrency(milestone.target_amount, goal.currency)}
                  </p>
                  <p style={{ margin: 0, fontSize: '0.9rem', color: '#475569' }}>
                    {milestone.achieved ? (
                      <>
                        <span style={{ color: '#10B981', fontWeight: 500 }}>
                          Achieved on {formatDate(milestone.achieved_date)}
                        </span>
                      </>
                    ) : (
                      <>
                        Target: {formatDate(milestone.milestone_date)}
                        {new Date(milestone.milestone_date) < new Date() && (
                          <span style={{ color: '#F59E0B', marginLeft: '8px' }}>• Behind schedule</span>
                        )}
                      </>
                    )}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div style={narrativeSectionStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ ...sectionHeadingStyle, marginBottom: 0 }}>Recommendations</h3>
            <button
              onClick={() => setShowRecommendations(!showRecommendations)}
              style={{
                background: 'none',
                border: 'none',
                color: '#2563EB',
                fontSize: '0.9rem',
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
            >
              {showRecommendations ? 'Hide' : 'Show'} recommendations
            </button>
          </div>

          {showRecommendations && (
            <div>
              {recommendations.map((rec, index) => (
                <div key={index} style={{ ...calloutStyle('tip'), marginBottom: '16px' }}>
                  <h4 style={{ margin: '0 0 8px 0', fontSize: '1rem', fontWeight: 600 }}>
                    {rec.priority === 'HIGH' && '🔥 '}
                    {rec.title}
                  </h4>
                  <p style={{ margin: 0, lineHeight: '1.7' }}>{rec.description}</p>
                  {rec.action && (
                    <p style={{ margin: '8px 0 0 0', fontWeight: 500, fontStyle: 'italic' }}>
                      → {rec.action}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* What to Do Next */}
      {progressPercentage < 100 && (
        <div style={{ ...narrativeSectionStyle, backgroundColor: '#EFF6FF', border: '1px solid #BFDBFE' }}>
          <h3 style={{ ...sectionHeadingStyle, color: '#1E40AF' }}>What Should You Do Next?</h3>
          <ol style={{ ...paragraphStyle, color: '#1E40AF', paddingLeft: '20px', marginBottom: 0 }}>
            {goal.linked_accounts_count === 0 && (
              <li style={{ marginBottom: '12px' }}>
                Link a savings account to this goal for automatic progress tracking
              </li>
            )}
            {!goal.auto_contribution_enabled && (
              <li style={{ marginBottom: '12px' }}>
                Set up automatic monthly contributions of{' '}
                {formatCurrency(goal.required_monthly_contribution, goal.currency)} to stay on track
              </li>
            )}
            <li style={{ marginBottom: '12px' }}>
              Review your progress monthly and adjust contributions if needed
            </li>
            {monthsRemaining <= 6 && progressPercentage < 75 && (
              <li style={{ marginBottom: '12px', color: '#92400E', fontWeight: 500 }}>
                You're approaching your target date - consider increasing contributions or extending
                the timeline
              </li>
            )}
          </ol>
        </div>
      )}

      {/* Goal Achieved Celebration */}
      {progressPercentage >= 100 && (
        <div style={{ ...narrativeSectionStyle, backgroundColor: '#F0FDF4', border: '1px solid #86EFAC' }}>
          <h3 style={{ ...sectionHeadingStyle, color: '#166534', textAlign: 'center' }}>
            🎉 Congratulations! You've Achieved Your Goal!
          </h3>
          <p style={{ ...paragraphStyle, color: '#166534', textAlign: 'center' }}>
            You successfully saved{' '}
            <strong style={{ fontFamily: 'monospace' }}>
              {formatCurrency(goal.current_progress, goal.currency)}
            </strong>{' '}
            toward your {goal.title} goal. Well done on staying focused and disciplined!
          </p>
          <div style={{ textAlign: 'center', marginTop: '16px' }}>
            <Button variant="primary" onClick={onBack}>
              View All Goals →
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
