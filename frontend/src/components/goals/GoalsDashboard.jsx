import React, { useState, useEffect } from 'react';
import { Card, Button, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * GoalsDashboard - Financial goals overview with narrative storytelling
 *
 * Displays comprehensive goals summary:
 * - Total goals count and aggregate savings
 * - On-track vs needs-attention status
 * - Individual goal cards with progress
 * - Filtering and sorting capabilities
 * - Create new goal action
 *
 * Follows STYLEGUIDE.md narrative storytelling approach:
 * - Conversational language ("You're tracking 3 financial goals...")
 * - Metrics embedded in sentences with context
 * - 2-3 sentence paragraphs maximum
 * - Progressive disclosure
 * - Generous white space (line-height 1.7, 32px padding)
 * - Encouraging, motivating tone
 */
export function GoalsDashboard({ onGoalSelect, onCreateGoal }) {
  const [goals, setGoals] = useState([]);
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterType, setFilterType] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [sortBy, setSortBy] = useState('priority');

  useEffect(() => {
    loadGoalsData();
  }, [filterType, filterStatus, sortBy]);

  const loadGoalsData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load goals overview
      const overviewResponse = await fetch('/api/v1/goals/overview', {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!overviewResponse.ok) {
        if (overviewResponse.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }
        throw new Error('Failed to fetch goals overview');
      }

      const overviewData = await overviewResponse.json();
      setOverview(overviewData);

      // Load goals list with filters
      const params = new URLSearchParams();
      if (filterType !== 'ALL') params.append('goal_type', filterType);
      if (filterStatus !== 'ALL') params.append('status', filterStatus);
      params.append('sort_by', sortBy);

      const goalsResponse = await fetch(`/api/v1/goals?${params.toString()}`, {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!goalsResponse.ok) {
        throw new Error('Failed to fetch goals list');
      }

      const goalsData = await goalsResponse.json();
      setGoals(goalsData);
    } catch (err) {
      setError('Failed to load goals data. Please try again.');
      console.error('Error loading goals:', err);
    } finally {
      setLoading(false);
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

  const formatPercentage = (value) => {
    if (value === null || value === undefined) return '0%';
    return `${Math.round(value)}%`;
  };

  const getProgressColor = (progress) => {
    if (progress >= 75) return '#10B981'; // Success green
    if (progress >= 50) return '#2563EB'; // Primary blue
    if (progress >= 25) return '#F59E0B'; // Warning amber
    return '#EF4444'; // Error red
  };

  const getGoalTypeLabel = (type) => {
    const labels = {
      EMERGENCY_FUND: 'Emergency Fund',
      HOUSE_PURCHASE: 'House Purchase',
      HOME_IMPROVEMENT: 'Home Improvement',
      DEBT_REPAYMENT: 'Debt Repayment',
      VEHICLE_PURCHASE: 'Vehicle Purchase',
      WEDDING: 'Wedding',
      HOLIDAY_TRAVEL: 'Holiday/Travel',
      EDUCATION_CHILDREN: "Children's Education",
      EDUCATION_SELF: 'Self Education',
      RETIREMENT: 'Retirement',
      BUSINESS_START: 'Business Start',
      INHERITANCE_PLANNING: 'Inheritance Planning',
      FINANCIAL_INDEPENDENCE: 'Financial Independence',
      CHARITABLE_GIVING: 'Charitable Giving',
      OTHER: 'Other',
    };
    return labels[type] || type;
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

  // Styles following STYLEGUIDE.md
  const dashboardContainerStyle = {
    maxWidth: '1280px',
    margin: '0 auto',
    padding: '32px 16px',
  };

  const pageHeadingStyle = {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#0F172A',
    marginBottom: '32px',
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

  const narrativeParagraphStyle = {
    color: '#475569',
    marginBottom: '16px',
    lineHeight: '1.7',
    fontSize: '1rem',
  };

  const goalCardStyle = {
    padding: '24px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
    cursor: 'pointer',
    transition: 'all 0.25s ease-in-out',
    border: '1px solid #E2E8F0',
  };

  const goalCardHoverStyle = {
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.07)',
    transform: 'translateY(-2px)',
  };

  const progressBarContainerStyle = {
    width: '100%',
    height: '8px',
    backgroundColor: '#E2E8F0',
    borderRadius: '4px',
    overflow: 'hidden',
    margin: '16px 0',
  };

  const progressBarFillStyle = (progress, color) => ({
    height: '100%',
    width: `${Math.min(progress, 100)}%`,
    backgroundColor: color,
    borderRadius: '4px',
    transition: 'width 0.5s ease-in-out',
  });

  const filterBarStyle = {
    display: 'flex',
    gap: '16px',
    marginBottom: '32px',
    flexWrap: 'wrap',
    alignItems: 'center',
  };

  const selectStyle = {
    padding: '8px 16px',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
    backgroundColor: '#FFFFFF',
    fontSize: '0.95rem',
    color: '#0F172A',
    cursor: 'pointer',
  };

  if (loading) {
    return (
      <div style={dashboardContainerStyle}>
        <div style={narrativeSectionStyle}>
          <p style={narrativeParagraphStyle}>Loading your goals...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={dashboardContainerStyle}>
        <Alert variant="error">{error}</Alert>
        <Button onClick={loadGoalsData} style={{ marginTop: '16px' }}>
          Try Again
        </Button>
      </div>
    );
  }

  // Empty state
  if (!overview || overview.total_goals === 0) {
    return (
      <div style={dashboardContainerStyle}>
        <h1 style={pageHeadingStyle}>Your Financial Goals</h1>

        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Start Your Journey</h3>
          <p style={narrativeParagraphStyle}>
            You haven't set any financial goals yet. Goals help you stay focused on what matters
            most and track your progress along the way.
          </p>
          <p style={narrativeParagraphStyle}>
            Whether you're saving for a house deposit, building an emergency fund, or planning for
            retirement, setting clear goals makes your financial journey more achievable.
          </p>
          <Button variant="primary" onClick={onCreateGoal} style={{ marginTop: '16px' }}>
            Create Your First Goal →
          </Button>
        </div>

        <div
          style={{
            ...narrativeSectionStyle,
            backgroundColor: '#EFF6FF',
            border: '1px solid #BFDBFE',
          }}
        >
          <h4 style={{ ...sectionHeadingStyle, color: '#1E40AF' }}>💡 Tips for Setting Goals</h4>
          <ul style={{ ...narrativeParagraphStyle, paddingLeft: '20px' }}>
            <li style={{ marginBottom: '8px' }}>
              Make them SMART: Specific, Measurable, Achievable, Relevant, Time-bound
            </li>
            <li style={{ marginBottom: '8px' }}>
              Start with your most important goal first (like an emergency fund)
            </li>
            <li style={{ marginBottom: '8px' }}>
              Link savings accounts to track progress automatically
            </li>
            <li>Be realistic about timelines and amounts</li>
          </ul>
        </div>
      </div>
    );
  }

  // Main dashboard with goals
  const onTrackCount = overview.on_track_count || 0;
  const needsAttentionCount = overview.needs_attention_count || 0;

  return (
    <div style={dashboardContainerStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <h1 style={pageHeadingStyle}>Your Financial Goals</h1>
        <Button variant="primary" onClick={onCreateGoal}>
          Create Goal +
        </Button>
      </div>

      {/* Overview Narrative Section */}
      <div style={narrativeSectionStyle}>
        <h3 style={sectionHeadingStyle}>Your Progress Overview</h3>
        <p style={narrativeParagraphStyle}>
          You're tracking <strong style={{ fontFamily: 'monospace' }}>{overview.total_goals}</strong>{' '}
          {overview.total_goals === 1 ? 'financial goal' : 'financial goals'} with total target savings of{' '}
          <strong style={{ fontFamily: 'monospace' }}>
            {formatCurrency(overview.total_target_amount)}
          </strong>
          . {overview.total_current_progress > 0 && (
            <>
              So far, you've saved{' '}
              <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
                {formatCurrency(overview.total_current_progress)}
              </strong>{' '}
              across all your goals.
            </>
          )}
        </p>
        <p style={narrativeParagraphStyle}>
          {onTrackCount > 0 && (
            <>
              <strong style={{ color: '#10B981' }}>{onTrackCount}</strong>{' '}
              {onTrackCount === 1 ? 'goal is' : 'goals are'} on track
            </>
          )}
          {onTrackCount > 0 && needsAttentionCount > 0 && ', '}
          {needsAttentionCount > 0 && (
            <>
              <strong style={{ color: '#F59E0B' }}>{needsAttentionCount}</strong>{' '}
              {needsAttentionCount === 1 ? 'needs' : 'need'} attention
            </>
          )}
          {onTrackCount === 0 && needsAttentionCount === 0 && 'Keep up the great work!'}
        </p>

        {overview.total_monthly_required > 0 && (
          <p style={narrativeParagraphStyle}>
            To stay on track, you need to save{' '}
            <strong style={{ fontFamily: 'monospace' }}>
              {formatCurrency(overview.total_monthly_required)}/month
            </strong>{' '}
            across all your goals.
          </p>
        )}
      </div>

      {/* Filters and Sorting */}
      <div style={filterBarStyle}>
        <div>
          <label style={{ fontSize: '0.9rem', color: '#475569', marginRight: '8px' }}>
            Filter by type:
          </label>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            style={selectStyle}
          >
            <option value="ALL">All Types</option>
            <option value="EMERGENCY_FUND">Emergency Fund</option>
            <option value="HOUSE_PURCHASE">House Purchase</option>
            <option value="RETIREMENT">Retirement</option>
            <option value="EDUCATION_CHILDREN">Children's Education</option>
            <option value="HOLIDAY_TRAVEL">Holiday/Travel</option>
            <option value="OTHER">Other</option>
          </select>
        </div>

        <div>
          <label style={{ fontSize: '0.9rem', color: '#475569', marginRight: '8px' }}>
            Status:
          </label>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            style={selectStyle}
          >
            <option value="ALL">All</option>
            <option value="NOT_STARTED">Not Started</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="ON_TRACK">On Track</option>
            <option value="AT_RISK">At Risk</option>
            <option value="ACHIEVED">Achieved</option>
            <option value="ABANDONED">Abandoned</option>
          </select>
        </div>

        <div>
          <label style={{ fontSize: '0.9rem', color: '#475569', marginRight: '8px' }}>
            Sort by:
          </label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} style={selectStyle}>
            <option value="priority">Priority</option>
            <option value="target_date">Target Date</option>
            <option value="progress">Progress</option>
            <option value="created_at">Recently Created</option>
          </select>
        </div>
      </div>

      {/* Goals List */}
      <div style={{ marginTop: '32px' }}>
        {goals.length === 0 ? (
          <div style={narrativeSectionStyle}>
            <p style={narrativeParagraphStyle}>
              No goals match your current filters. Try adjusting your filters or create a new goal.
            </p>
          </div>
        ) : (
          goals.map((goal) => {
            const progressPercentage = goal.progress_percentage || 0;
            const progressColor = getProgressColor(progressPercentage);
            const monthsRemaining = Math.max(
              0,
              Math.ceil(
                (new Date(goal.target_date) - new Date()) / (1000 * 60 * 60 * 24 * 30)
              )
            );

            return (
              <div
                key={goal.id}
                style={goalCardStyle}
                onClick={() => onGoalSelect(goal.id)}
                onMouseEnter={(e) => {
                  Object.assign(e.currentTarget.style, goalCardHoverStyle);
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow = goalCardStyle.boxShadow;
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ fontSize: '2rem' }}>{getGoalIcon(goal.goal_type)}</span>
                    <div>
                      <h4 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0F172A', margin: 0 }}>
                        {goal.title}
                      </h4>
                      <p style={{ fontSize: '0.85rem', color: '#94A3B8', margin: '4px 0 0 0' }}>
                        {getGoalTypeLabel(goal.goal_type)}
                      </p>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span
                      style={{
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontSize: '0.8rem',
                        fontWeight: 500,
                        backgroundColor: goal.priority === 'HIGH' ? '#FEF3C7' : goal.priority === 'MEDIUM' ? '#DBEAFE' : '#F1F5F9',
                        color: goal.priority === 'HIGH' ? '#92400E' : goal.priority === 'MEDIUM' ? '#1E40AF' : '#475569',
                      }}
                    >
                      {goal.priority} Priority
                    </span>
                  </div>
                </div>

                <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7', marginBottom: '16px' }}>
                  You're <strong style={{ color: progressColor }}>{formatPercentage(progressPercentage)} of the way</strong> to
                  your goal of{' '}
                  <strong style={{ fontFamily: 'monospace' }}>
                    {formatCurrency(goal.target_amount, goal.currency)}
                  </strong>
                  . {progressPercentage >= 75 ? (
                    <>You're making excellent progress!</>
                  ) : progressPercentage >= 50 ? (
                    <>Halfway there - keep going!</>
                  ) : progressPercentage >= 25 ? (
                    <>You're making steady progress.</>
                  ) : (
                    <>Just getting started - stay focused!</>
                  )}
                </p>

                <div style={progressBarContainerStyle}>
                  <div style={progressBarFillStyle(progressPercentage, progressColor)} />
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: '#475569' }}>
                  <div>
                    <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
                      {formatCurrency(goal.current_progress || 0, goal.currency)}
                    </strong>{' '}
                    saved
                  </div>
                  <div>
                    {monthsRemaining > 0 ? (
                      <>
                        {monthsRemaining} {monthsRemaining === 1 ? 'month' : 'months'} remaining
                      </>
                    ) : (
                      <span style={{ color: '#EF4444', fontWeight: 500 }}>Target date passed</span>
                    )}
                  </div>
                </div>

                {goal.required_monthly_contribution > 0 && (
                  <p style={{ marginTop: '12px', fontSize: '0.85rem', color: '#475569', fontStyle: 'italic' }}>
                    At your current pace of{' '}
                    <strong style={{ fontFamily: 'monospace' }}>
                      {formatCurrency(goal.required_monthly_contribution, goal.currency)}/month
                    </strong>
                    , you'll reach your target{' '}
                    {progressPercentage >= 100 ? (
                      <span style={{ color: '#10B981' }}>✓ Goal achieved!</span>
                    ) : goal.on_track ? (
                      <>by {new Date(goal.target_date).toLocaleDateString('en-GB', { month: 'long', year: 'numeric' })}</>
                    ) : (
                      <span style={{ color: '#F59E0B' }}>but you'll need to increase contributions to stay on track</span>
                    )}
                  </p>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
