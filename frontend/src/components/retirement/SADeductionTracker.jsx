import React, { useState, useEffect } from 'react';
import { Card, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * SADeductionTracker - Section 10C tax deduction tracker
 *
 * Shows SA retirement contribution tax deduction status:
 * - Narrative explanation of Section 10C
 * - Visual progress bar showing usage
 * - Warning if approaching limit
 * - Clear display of 27.5% of income vs R350k cap
 *
 * Follows STYLEGUIDE.md:
 * - Conversational tone
 * - Metrics embedded in sentences
 * - Color-coded progress indicators
 * - Educational callouts
 */
export function SADeductionTracker() {
  const [deductionData, setDeductionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDeductionData();
  }, []);

  const loadDeductionData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/retirement/sa-section-10c', {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!response.ok) {
        // Handle all errors gracefully - show empty state
        setDeductionData(null);
        setLoading(false);
        return;
      }

      const data = await response.json();
      setDeductionData(data);
    } catch (err) {
      // Silently ignore errors - endpoint may not be implemented
      setDeductionData(null);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return 'R0';
    return `R${amount.toLocaleString('en-ZA', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })}`;
  };

  // Styles following STYLEGUIDE.md
  const containerStyle = {
    maxWidth: '1280px',
    margin: '0 auto',
  };

  const cardStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    lineHeight: '1.7',
  };

  const titleStyle = {
    fontSize: '1.5rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '16px',
  };

  const narrativeParagraphStyle = {
    fontSize: '1rem',
    color: '#475569',
    lineHeight: '1.7',
    marginBottom: '16px',
  };

  const progressContainerStyle = {
    marginTop: '24px',
    marginBottom: '24px',
  };

  const progressBarBackgroundStyle = {
    width: '100%',
    height: '40px',
    backgroundColor: '#E2E8F0',
    borderRadius: '20px',
    overflow: 'hidden',
    position: 'relative',
  };

  const calloutStyle = (type) => {
    const styles = {
      info: {
        backgroundColor: '#DBEAFE',
        border: '1px solid #BFDBFE',
        borderLeft: '4px solid #3B82F6',
        color: '#1E3A8A',
      },
      warning: {
        backgroundColor: '#FEF3C7',
        border: '1px solid #FCD34D',
        borderLeft: '4px solid #F59E0B',
        color: '#78350F',
      },
      success: {
        backgroundColor: '#D1FAE5',
        border: '1px solid #86EFAC',
        borderLeft: '4px solid #10B981',
        color: '#065F46',
      },
    };

    return {
      ...styles[type],
      padding: '16px',
      borderRadius: '8px',
      marginTop: '24px',
    };
  };

  const metricGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
    marginTop: '24px',
  };

  const metricCardStyle = {
    padding: '16px',
    backgroundColor: '#F8FAFC',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
  };

  const metricLabelStyle = {
    fontSize: '0.75rem',
    fontWeight: 500,
    color: '#64748B',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    marginBottom: '4px',
  };

  const metricValueStyle = {
    fontSize: '1.5rem',
    fontWeight: 700,
    fontFamily: 'monospace',
    color: '#0F172A',
  };

  // Loading state
  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={cardStyle}>
          <div style={{ textAlign: 'center', padding: '48px', color: '#94A3B8' }}>
            <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⏳</div>
            <p>Loading Section 10C deduction data...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={containerStyle}>
        <Alert variant="error">
          <p style={{ fontWeight: 600 }}>Error Loading Deduction Data</p>
          <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
        </Alert>
      </div>
    );
  }

  if (!deductionData) {
    return (
      <div style={containerStyle}>
        <div style={cardStyle}>
          <p style={narrativeParagraphStyle}>
            No Section 10C deduction data available. Add SA retirement funds to start tracking your tax deductions.
          </p>
        </div>
      </div>
    );
  }

  const {
    taxYear,
    totalContributions,
    maxDeductible,
    deductionClaimed,
    taxSaving,
    remainingAllowance,
    remuneration,
  } = deductionData;

  const percentageUsed = maxDeductible > 0 ? (deductionClaimed / maxDeductible) * 100 : 0;
  const isApproachingLimit = percentageUsed >= 80;
  const isAtLimit = percentageUsed >= 100;

  // Determine progress bar color
  let progressColor = '#10B981'; // Green (good)
  if (isAtLimit) {
    progressColor = '#EF4444'; // Red (at limit)
  } else if (isApproachingLimit) {
    progressColor = '#F59E0B'; // Amber (warning)
  }

  const progressBarStyle = {
    width: `${Math.min(percentageUsed, 100)}%`,
    height: '100%',
    backgroundColor: progressColor,
    transition: 'width 500ms ease-in-out, background-color 250ms ease-in-out',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    paddingRight: '12px',
  };

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        <h2 style={titleStyle}>Section 10C Tax Deduction Tracker</h2>

        <p style={narrativeParagraphStyle}>
          This tax year (<strong>{taxYear}</strong>), you can deduct up to{' '}
          <strong style={{ fontFamily: 'monospace', color: '#2563EB' }}>
            {formatCurrency(maxDeductible)}
          </strong>{' '}
          from your taxable income for retirement contributions. That's 27.5% of your remuneration or the R350,000
          cap, whichever is lower.
        </p>

        <p style={narrativeParagraphStyle}>
          You've contributed{' '}
          <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(totalContributions)}</strong> so far,
          claiming a tax deduction of{' '}
          <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
            {formatCurrency(deductionClaimed)}
          </strong>
          . This saves you approximately{' '}
          <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
            {formatCurrency(taxSaving)}
          </strong>{' '}
          in tax.
        </p>

        {/* Progress Bar */}
        <div style={progressContainerStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.875rem', color: '#64748B' }}>Deduction used</span>
            <span style={{ fontSize: '0.875rem', fontWeight: 600, color: progressColor }}>
              {percentageUsed.toFixed(1)}%
            </span>
          </div>

          <div style={progressBarBackgroundStyle}>
            <div style={progressBarStyle}>
              {percentageUsed >= 20 && (
                <span style={{ color: '#FFFFFF', fontSize: '0.875rem', fontWeight: 600 }}>
                  {formatCurrency(deductionClaimed)}
                </span>
              )}
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px' }}>
            <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>R0</span>
            <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>{formatCurrency(maxDeductible)}</span>
          </div>
        </div>

        {/* Metric Grid */}
        <div style={metricGridStyle}>
          <div style={metricCardStyle}>
            <div style={metricLabelStyle}>Total Contributions</div>
            <div style={metricValueStyle}>{formatCurrency(totalContributions)}</div>
          </div>

          <div style={metricCardStyle}>
            <div style={metricLabelStyle}>Tax Deduction</div>
            <div style={{ ...metricValueStyle, color: '#10B981' }}>{formatCurrency(deductionClaimed)}</div>
          </div>

          <div style={metricCardStyle}>
            <div style={metricLabelStyle}>Tax Saving</div>
            <div style={{ ...metricValueStyle, color: '#10B981' }}>{formatCurrency(taxSaving)}</div>
          </div>

          <div style={metricCardStyle}>
            <div style={metricLabelStyle}>Remaining Allowance</div>
            <div style={{ ...metricValueStyle, color: isAtLimit ? '#EF4444' : '#2563EB' }}>
              {formatCurrency(remainingAllowance)}
            </div>
          </div>
        </div>

        {/* Status Callout */}
        {isAtLimit && (
          <div style={calloutStyle('warning')}>
            <p style={{ fontWeight: 600, marginBottom: '8px' }}>⚠️ Deduction limit reached</p>
            <p style={{ fontSize: '0.875rem', lineHeight: '1.7' }}>
              You've reached your maximum Section 10C deduction for this tax year. Additional contributions
              won't provide further tax relief, though they'll still grow tax-free until retirement.
            </p>
          </div>
        )}

        {isApproachingLimit && !isAtLimit && (
          <div style={calloutStyle('warning')}>
            <p style={{ fontWeight: 600, marginBottom: '8px' }}>Approaching deduction limit</p>
            <p style={{ fontSize: '0.875rem', lineHeight: '1.7' }}>
              You have{' '}
              <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(remainingAllowance)}</strong> of
              deduction allowance remaining. Consider maximizing your contributions to get the full tax benefit.
            </p>
          </div>
        )}

        {!isApproachingLimit && (
          <div style={calloutStyle('success')}>
            <p style={{ fontWeight: 600, marginBottom: '8px' }}>Room to contribute more</p>
            <p style={{ fontSize: '0.875rem', lineHeight: '1.7' }}>
              You still have{' '}
              <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(remainingAllowance)}</strong> of tax
              deduction available. Increasing your contributions could save you more tax while building your
              retirement savings.
            </p>
          </div>
        )}

        {/* Educational Section */}
        <div style={calloutStyle('info')}>
          <p style={{ fontWeight: 600, marginBottom: '8px' }}>How Section 10C works</p>
          <ul style={{ fontSize: '0.875rem', lineHeight: '1.7', paddingLeft: '20px', margin: 0 }}>
            <li>You can deduct up to 27.5% of your remuneration (salary + benefits)</li>
            <li>Maximum annual deduction is capped at R350,000</li>
            <li>Applies to pension funds, provident funds, and retirement annuities</li>
            <li>Reduces your taxable income, lowering your tax bill</li>
            <li>Excess contributions carry forward to future tax years</li>
          </ul>
        </div>

        {/* Calculation Details */}
        <div
          style={{
            marginTop: '24px',
            padding: '16px',
            backgroundColor: '#F1F5F9',
            borderRadius: '8px',
            fontSize: '0.875rem',
          }}
        >
          <p style={{ fontWeight: 600, marginBottom: '8px', color: '#334155' }}>Your calculation:</p>
          <p style={{ color: '#475569', marginBottom: '4px' }}>
            Remuneration: <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(remuneration)}</strong>
          </p>
          <p style={{ color: '#475569', marginBottom: '4px' }}>
            27.5% of remuneration:{' '}
            <strong style={{ fontFamily: 'monospace' }}>
              {formatCurrency(remuneration * 0.275)}
            </strong>
          </p>
          <p style={{ color: '#475569', marginBottom: '4px' }}>
            Statutory cap: <strong style={{ fontFamily: 'monospace' }}>R350,000</strong>
          </p>
          <p style={{ color: '#0F172A', fontWeight: 600, marginTop: '8px' }}>
            Your limit:{' '}
            <strong style={{ fontFamily: 'monospace', color: '#2563EB' }}>
              {formatCurrency(maxDeductible)}
            </strong>
          </p>
        </div>
      </div>
    </div>
  );
}
