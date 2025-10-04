import React, { useState, useEffect } from 'react';
import { Card, Button, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * CoverageGapWidget - Dashboard widget showing life insurance coverage gap status
 *
 * Displays coverage summary with narrative storytelling:
 * - Current total coverage (from all active policies)
 * - Recommended coverage (from analysis)
 * - Coverage gap (recommended - current)
 * - Percentage covered (visual progress bar)
 * - Status indicator (ADEQUATE, UNDER_INSURED, CRITICAL)
 * - Action buttons based on status
 */
export function CoverageGapWidget({ onRefresh }) {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    loadCoverageAnalysis();
  }, []);

  const loadCoverageAnalysis = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/protection/coverage-analysis/summary', {
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
        if (response.status === 404) {
          // No analysis exists yet
          setAnalysis(null);
          setLoading(false);
          return;
        }
        throw new Error('Failed to fetch coverage analysis');
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError('Failed to load coverage analysis. Please try again.');
      console.error('Error loading coverage analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return '£0';
    return `£${amount.toLocaleString('en-GB', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })}`;
  };

  const formatCurrencyShort = (amount) => {
    if (amount === null || amount === undefined) return '£0';
    if (amount >= 1000000) {
      return `£${(amount / 1000000).toFixed(1)}m`;
    }
    if (amount >= 1000) {
      return `£${(amount / 1000).toFixed(0)}k`;
    }
    return `£${amount.toLocaleString('en-GB')}`;
  };

  const getStatus = () => {
    if (!analysis || !analysis.recommendedCover) return 'NO_ANALYSIS';

    const percentageCovered = (analysis.currentTotalCover / analysis.recommendedCover) * 100;
    const gapPercentage = ((analysis.recommendedCover - analysis.currentTotalCover) / analysis.recommendedCover) * 100;

    // ADEQUATE: 90%+ covered (within 10% of recommended)
    if (percentageCovered >= 90) return 'ADEQUATE';

    // CRITICAL: <70% covered (gap > 30%)
    if (percentageCovered < 70) return 'CRITICAL';

    // UNDER_INSURED: 70-89% covered (gap 11-30%)
    return 'UNDER_INSURED';
  };

  const getStatusConfig = (status) => {
    const configs = {
      ADEQUATE: {
        color: '#10B981',
        bgColor: '#D1FAE5',
        borderColor: '#10B981',
        icon: '✓',
        label: 'Well Protected',
        message: "You're well protected! Your coverage meets or exceeds your recommended needs.",
        actionLabel: 'Review Coverage',
      },
      UNDER_INSURED: {
        color: '#F59E0B',
        bgColor: '#FEF3C7',
        borderColor: '#F59E0B',
        icon: '⚠',
        label: 'Needs Attention',
        message: "You need {gap} more coverage. Consider increasing your life insurance.",
        actionLabel: 'Add Policy',
      },
      CRITICAL: {
        color: '#EF4444',
        bgColor: '#FEE2E2',
        borderColor: '#EF4444',
        icon: '✕',
        label: 'Critical Gap',
        message: "Critical gap! You need {gap} more coverage to protect your family.",
        actionLabel: 'Add Policy',
      },
      NO_ANALYSIS: {
        color: '#3B82F6',
        bgColor: '#DBEAFE',
        borderColor: '#3B82F6',
        icon: '?',
        label: 'Not Calculated',
        message: "Calculate your coverage needs to see how well protected you are.",
        actionLabel: 'Calculate My Needs',
      },
    };

    return configs[status] || configs.NO_ANALYSIS;
  };

  // Styles
  const widgetStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '32px',
    lineHeight: '1.7',
  };

  const headingStyle = {
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

  const progressBarContainerStyle = {
    width: '100%',
    height: '12px',
    backgroundColor: '#E2E8F0',
    borderRadius: '6px',
    overflow: 'hidden',
    marginTop: '16px',
    marginBottom: '8px',
  };

  const metricGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
    gap: '12px',
    marginTop: '16px',
    marginBottom: '16px',
  };

  const compactMetricStyle = {
    padding: '12px',
    backgroundColor: '#F8FAFC',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
  };

  const metricValueStyle = {
    fontSize: '1.25rem',
    fontWeight: 'bold',
    color: '#0F172A',
    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace',
  };

  const metricLabelStyle = {
    fontSize: '0.7rem',
    color: '#475569',
    marginTop: '4px',
  };

  const statusBadgeStyle = (config) => ({
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 16px',
    backgroundColor: config.bgColor,
    border: `2px solid ${config.borderColor}`,
    borderRadius: '8px',
    fontSize: '0.875rem',
    fontWeight: 600,
    color: config.color,
    marginBottom: '16px',
  });

  const expandableSectionStyle = {
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
    border: 'none',
    width: '100%',
  };

  // Loading state
  if (loading) {
    return (
      <div style={widgetStyle}>
        <div style={{ textAlign: 'center', padding: '32px', color: '#94A3B8' }}>
          <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⏳</div>
          <p>Loading coverage analysis...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={widgetStyle}>
        <Alert variant="error">
          <p style={{ fontWeight: 600 }}>Error</p>
          <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
        </Alert>
        <Button
          variant="outline"
          onClick={loadCoverageAnalysis}
          style={{ marginTop: '16px' }}
        >
          Try Again
        </Button>
      </div>
    );
  }

  const status = getStatus();
  const config = getStatusConfig(status);

  // Empty state - no analysis exists
  if (!analysis || status === 'NO_ANALYSIS') {
    return (
      <div style={widgetStyle}>
        <h3 style={headingStyle}>Your Coverage Protection Status</h3>

        <div style={statusBadgeStyle(config)}>
          <span style={{ fontSize: '1.2rem' }}>{config.icon}</span>
          <span>{config.label}</span>
        </div>

        <p style={narrativeParagraphStyle}>
          You haven't calculated your coverage needs yet. Understanding how much life insurance
          you need is essential to protecting your family's financial future.
        </p>

        <div style={{
          backgroundColor: '#DBEAFE',
          border: '1px solid #BFDBFE',
          borderLeft: '4px solid #3B82F6',
          padding: '16px',
          borderRadius: '8px',
          marginTop: '16px',
        }}>
          <p style={{ fontWeight: 600, color: '#1E40AF', marginBottom: '8px' }}>
            Why calculate coverage needs?
          </p>
          <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
            Most families need life insurance equal to 10-12 times their annual income, plus
            outstanding debts and future expenses. Our calculator helps you determine the right
            amount for your specific situation.
          </p>
        </div>

        <Button variant="primary" style={{ marginTop: '24px' }}>
          {config.actionLabel} →
        </Button>
      </div>
    );
  }

  // Calculate percentages and values
  const currentCover = analysis.currentTotalCover || 0;
  const recommendedCover = analysis.recommendedCover || 0;
  const coverageGap = Math.max(0, recommendedCover - currentCover);
  const percentageCovered = recommendedCover > 0
    ? Math.min(100, (currentCover / recommendedCover) * 100)
    : 0;

  const progressBarStyle = {
    height: '100%',
    width: `${percentageCovered}%`,
    backgroundColor: config.color,
    transition: 'width 0.3s ease-in-out',
  };

  // Generate message with gap amount
  const message = config.message.replace('{gap}', formatCurrency(coverageGap));

  return (
    <div style={widgetStyle}>
      <h3 style={headingStyle}>Your Coverage Protection Status</h3>

      <div style={statusBadgeStyle(config)}>
        <span style={{ fontSize: '1.2rem' }}>{config.icon}</span>
        <span>{config.label}</span>
      </div>

      <p style={narrativeParagraphStyle}>
        {status === 'ADEQUATE' ? (
          <>
            Your current policies provide <strong style={{ fontFamily: 'monospace' }}>
              {formatCurrency(currentCover)}
            </strong> of protection, which {percentageCovered >= 100 ? 'exceeds' : 'meets'} your
            recommended coverage of <strong style={{ fontFamily: 'monospace' }}>
              {formatCurrency(recommendedCover)}
            </strong>. {message}
          </>
        ) : (
          <>
            Your current policies provide <strong style={{ fontFamily: 'monospace' }}>
              {formatCurrency(currentCover)}
            </strong> of protection, but you need <strong style={{ fontFamily: 'monospace' }}>
              {formatCurrency(recommendedCover)}
            </strong> to fully protect your family. {message}
          </>
        )}
      </p>

      {/* Progress bar */}
      <div style={progressBarContainerStyle}>
        <div style={progressBarStyle} />
      </div>
      <p style={{ fontSize: '0.75rem', color: '#475569', marginBottom: '16px' }}>
        {percentageCovered.toFixed(0)}% of recommended coverage
      </p>

      {/* Metric grid */}
      <div style={metricGridStyle}>
        <div style={compactMetricStyle}>
          <div style={metricValueStyle}>{formatCurrencyShort(currentCover)}</div>
          <div style={metricLabelStyle}>current coverage</div>
        </div>
        <div style={compactMetricStyle}>
          <div style={metricValueStyle}>{formatCurrencyShort(recommendedCover)}</div>
          <div style={metricLabelStyle}>recommended</div>
        </div>
        <div style={compactMetricStyle}>
          <div style={{ ...metricValueStyle, color: coverageGap > 0 ? config.color : '#10B981' }}>
            {formatCurrencyShort(coverageGap)}
          </div>
          <div style={metricLabelStyle}>coverage gap</div>
        </div>
      </div>

      {/* Action button */}
      <Button
        variant={status === 'ADEQUATE' ? 'outline' : 'primary'}
        style={{ marginTop: '16px' }}
      >
        {config.actionLabel} →
      </Button>

      {/* Expandable educational section */}
      <div style={expandableSectionStyle}>
        <button
          onClick={() => setExpanded(!expanded)}
          style={expandTriggerStyle}
          aria-expanded={expanded}
        >
          <span>Tell me more about coverage needs</span>
          <span style={{ fontSize: '0.75rem' }}>{expanded ? '▼' : '▶'}</span>
        </button>

        {expanded && (
          <div style={{ marginTop: '12px', fontSize: '0.9rem', color: '#475569', lineHeight: '1.7' }}>
            <p style={{ marginBottom: '12px' }}>
              Your coverage needs are calculated based on your family's financial situation.
              The recommended amount typically includes:
            </p>
            <ul style={{ paddingLeft: '20px', marginBottom: '12px' }}>
              <li>10-12 times your annual income (to replace lost earnings)</li>
              <li>Outstanding debts like mortgages and loans</li>
              <li>Future expenses like children's education</li>
              <li>Funeral and estate settlement costs</li>
            </ul>
            <p style={{ marginBottom: '12px' }}>
              This ensures your family can maintain their lifestyle if you're not there
              to provide for them. Your existing liquid assets are deducted from this amount
              to calculate the insurance coverage you need.
            </p>
            {status !== 'ADEQUATE' && (
              <p style={{ fontWeight: 600, color: '#1E40AF' }}>
                Tip: Many people are underinsured without realizing it. Reviewing your
                coverage regularly ensures your protection keeps pace with your life changes.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
