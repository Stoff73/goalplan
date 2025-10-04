import React, { useState, useEffect } from 'react';
import { Card, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * AnnualAllowanceTracker - UK Pension Annual Allowance tracker with narrative approach
 *
 * Displays:
 * - Current tax year allowance usage
 * - Visual progress bar
 * - Carry forward from previous years
 * - Warnings when approaching/exceeding limits
 * - Educational tips about annual allowance
 *
 * Follows STYLEGUIDE.md narrative storytelling approach:
 * - Conversational explanations
 * - Color-coded progress (green/amber/red)
 * - Clear guidance on what to do
 */
export function AnnualAllowanceTracker() {
  const [allowanceData, setAllowanceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAllowanceData();
  }, []);

  const loadAllowanceData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/retirement/annual-allowance', {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!response.ok) {
        // Handle all errors gracefully - show empty state
        setAllowanceData(null);
        setLoading(false);
        return;
      }

      const data = await response.json();
      setAllowanceData(data);
    } catch (err) {
      // Silently ignore errors - endpoint may not be fully implemented
      setAllowanceData(null);
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

  // Styles
  const containerStyle = {
    maxWidth: '1280px',
    margin: '0 auto',
  };

  const heroSectionStyle = (bgColor) => ({
    padding: '32px',
    background: `linear-gradient(to bottom right, ${bgColor})`,
    borderRadius: '12px',
    marginBottom: '48px',
    lineHeight: '1.7',
  });

  const heroTitleStyle = {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#0F172A',
    marginBottom: '16px',
  };

  const narrativeParagraphStyle = {
    fontSize: '1rem',
    color: '#475569',
    lineHeight: '1.7',
    marginBottom: '12px',
  };

  const progressBarContainerStyle = {
    width: '100%',
    height: '12px',
    backgroundColor: '#E2E8F0',
    borderRadius: '6px',
    overflow: 'hidden',
    marginTop: '24px',
    marginBottom: '8px',
  };

  const progressBarFillStyle = (percentage, color) => ({
    height: '100%',
    width: `${Math.min(percentage, 100)}%`,
    backgroundColor: color,
    transition: 'width 300ms ease-in-out',
  });

  const progressLabelsStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '0.875rem',
    color: '#475569',
    marginTop: '8px',
  };

  const carryForwardSectionStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
  };

  const sectionHeadingStyle = {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '12px',
  };

  const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    marginTop: '16px',
  };

  const tableHeaderStyle = {
    backgroundColor: '#F8FAFC',
    borderBottom: '2px solid #E2E8F0',
  };

  const tableHeaderCellStyle = {
    padding: '12px 16px',
    textAlign: 'left',
    fontSize: '0.875rem',
    fontWeight: 600,
    color: '#475569',
  };

  const tableRowStyle = {
    borderBottom: '1px solid #F1F5F9',
  };

  const tableCellStyle = {
    padding: '12px 16px',
    fontSize: '0.875rem',
    color: '#0F172A',
  };

  // Loading state
  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={carryForwardSectionStyle}>
          <div style={{ textAlign: 'center', padding: '48px', color: '#94A3B8' }}>
            <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⏳</div>
            <p>Loading annual allowance data...</p>
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
          <p style={{ fontWeight: 600 }}>Error Loading Annual Allowance</p>
          <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
        </Alert>
      </div>
    );
  }

  // No data state
  if (!allowanceData) {
    return (
      <div style={containerStyle}>
        <div style={carryForwardSectionStyle}>
          <h3 style={sectionHeadingStyle}>Annual Allowance Tracking</h3>
          <p style={narrativeParagraphStyle}>
            Add pensions to start tracking your annual allowance usage. We'll automatically calculate
            how much you can contribute with tax relief.
          </p>
        </div>
      </div>
    );
  }

  // Calculate status
  const {
    taxYear,
    annualAllowance,
    totalContributions,
    allowanceRemaining,
    carryForwardAvailable,
    mpaaApplies,
    tapered,
    taperedReason,
    carryForwardBreakdown,
  } = allowanceData;

  const usagePercentage = (totalContributions / annualAllowance) * 100;
  const onTrack = usagePercentage < 80;
  const nearLimit = usagePercentage >= 80 && usagePercentage < 100;
  const overLimit = usagePercentage >= 100;

  // Determine colors and background
  let progressColor, bgGradient, statusText;
  if (overLimit) {
    progressColor = '#EF4444';
    bgGradient = '#FEF2F2, #FEE2E2';
    statusText = 'Over limit';
  } else if (nearLimit) {
    progressColor = '#F59E0B';
    bgGradient = '#FFFBEB, #FEF3C7';
    statusText = 'Approaching limit';
  } else {
    progressColor = '#10B981';
    bgGradient = '#F0FDF4, #DCFCE7';
    statusText = 'On track';
  }

  return (
    <div style={containerStyle}>
      {/* Hero Section */}
      <div style={heroSectionStyle(bgGradient)}>
        <h2 style={heroTitleStyle}>
          Your pension allowance: {statusText}
        </h2>

        <p style={narrativeParagraphStyle}>
          This tax year ({taxYear}), you can contribute up to{' '}
          <strong style={{ fontFamily: 'monospace' }}>
            {formatCurrency(annualAllowance)}
          </strong>{' '}
          to your pensions before paying extra tax. So far, you've contributed{' '}
          <strong style={{ fontFamily: 'monospace' }}>
            {formatCurrency(totalContributions)}
          </strong>
          , leaving{' '}
          <strong style={{ fontFamily: 'monospace', color: progressColor }}>
            {formatCurrency(allowanceRemaining)}
          </strong>{' '}
          available.
        </p>

        {/* Progress Bar */}
        <div style={progressBarContainerStyle}>
          <div style={progressBarFillStyle(usagePercentage, progressColor)} />
        </div>
        <div style={progressLabelsStyle}>
          <span>{formatCurrency(totalContributions)} used</span>
          <span>{formatCurrency(allowanceRemaining)} remaining</span>
        </div>

        {/* MPAA Notice */}
        {mpaaApplies && (
          <Alert
            variant="warning"
            style={{
              marginTop: '24px',
              backgroundColor: '#FEF3C7',
              border: '1px solid #FCD34D',
              borderLeft: '4px solid #F59E0B',
            }}
          >
            <p style={{ fontWeight: 600, color: '#92400E', marginBottom: '4px' }}>
              Money Purchase Annual Allowance applies
            </p>
            <p style={{ color: '#78350F', fontSize: '0.875rem', lineHeight: '1.7' }}>
              Your annual allowance is reduced to £10,000 because you've flexibly accessed pension
              benefits. This limits how much you can contribute with tax relief.
            </p>
          </Alert>
        )}

        {/* Tapered Allowance Notice */}
        {tapered && (
          <Alert
            variant="info"
            style={{
              marginTop: '24px',
              backgroundColor: '#DBEAFE',
              border: '1px solid #BFDBFE',
              borderLeft: '4px solid #3B82F6',
            }}
          >
            <p style={{ fontWeight: 600, color: '#1E40AF', marginBottom: '4px' }}>
              Tapered Annual Allowance
            </p>
            <p style={{ color: '#1E3A8A', fontSize: '0.875rem', lineHeight: '1.7' }}>
              {taperedReason || 'Your annual allowance is reduced due to high income (over £260,000).'}
            </p>
          </Alert>
        )}
      </div>

      {/* Carry Forward Section */}
      {carryForwardAvailable > 0 && (
        <div style={carryForwardSectionStyle}>
          <h3 style={sectionHeadingStyle}>Unused allowance from previous years</h3>

          <p style={narrativeParagraphStyle}>
            <strong>Good news:</strong> You have{' '}
            <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
              {formatCurrency(carryForwardAvailable)}
            </strong>{' '}
            of unused allowance from previous years that you can use this year if you want to
            contribute more.
          </p>

          <div
            style={{
              backgroundColor: '#DBEAFE',
              border: '1px solid #BFDBFE',
              borderLeft: '4px solid #3B82F6',
              padding: '16px',
              borderRadius: '8px',
              marginTop: '16px',
              marginBottom: '24px',
            }}
          >
            <p style={{ fontSize: '0.875rem', color: '#1E40AF', lineHeight: '1.7' }}>
              <strong>How carry forward works:</strong> You can carry forward unused annual allowance
              from the previous three tax years. This lets you make larger contributions and still get
              tax relief - perfect for catch-up contributions or bonuses.
            </p>
          </div>

          {/* Carry Forward Breakdown Table */}
          {carryForwardBreakdown && carryForwardBreakdown.length > 0 && (
            <div style={{ overflowX: 'auto' }}>
              <table style={tableStyle}>
                <thead style={tableHeaderStyle}>
                  <tr>
                    <th style={tableHeaderCellStyle}>Tax Year</th>
                    <th style={{ ...tableHeaderCellStyle, textAlign: 'right' }}>
                      Annual Allowance
                    </th>
                    <th style={{ ...tableHeaderCellStyle, textAlign: 'right' }}>Used</th>
                    <th style={{ ...tableHeaderCellStyle, textAlign: 'right' }}>
                      Unused (Available)
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {carryForwardBreakdown.map((year, index) => (
                    <tr key={index} style={tableRowStyle}>
                      <td style={tableCellStyle}>{year.taxYear}</td>
                      <td style={{ ...tableCellStyle, textAlign: 'right', fontFamily: 'monospace' }}>
                        {formatCurrency(year.allowance)}
                      </td>
                      <td style={{ ...tableCellStyle, textAlign: 'right', fontFamily: 'monospace' }}>
                        {formatCurrency(year.used)}
                      </td>
                      <td
                        style={{
                          ...tableCellStyle,
                          textAlign: 'right',
                          fontFamily: 'monospace',
                          fontWeight: 600,
                          color: year.unused > 0 ? '#10B981' : '#94A3B8',
                        }}
                      >
                        {formatCurrency(year.unused)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Warning if approaching limit */}
      {nearLimit && !mpaaApplies && (
        <Alert
          variant="warning"
          style={{
            backgroundColor: '#FEF3C7',
            border: '1px solid #FCD34D',
            borderLeft: '4px solid #F59E0B',
          }}
        >
          <p style={{ fontWeight: 600, color: '#92400E', marginBottom: '8px' }}>
            You're getting close to your annual allowance
          </p>
          <p style={{ color: '#78350F', fontSize: '0.875rem', lineHeight: '1.7', marginBottom: '8px' }}>
            Contributing more than your limit means paying tax on the excess at your marginal rate.
            {carryForwardAvailable > 0 && (
              <> However, you can use your {formatCurrency(carryForwardAvailable)} carry forward
              allowance to contribute more.</>
            )}
          </p>
        </Alert>
      )}

      {/* Warning if over limit */}
      {overLimit && (
        <Alert
          variant="error"
          style={{
            backgroundColor: '#FEF2F2',
            border: '1px solid #FECACA',
            borderLeft: '4px solid #EF4444',
          }}
        >
          <p style={{ fontWeight: 600, color: '#991B1B', marginBottom: '8px' }}>
            You've exceeded your annual allowance
          </p>
          <p style={{ color: '#7F1D1D', fontSize: '0.875rem', lineHeight: '1.7', marginBottom: '8px' }}>
            Your contributions of {formatCurrency(totalContributions)} exceed your allowance of{' '}
            {formatCurrency(annualAllowance)} by{' '}
            <strong>{formatCurrency(totalContributions - annualAllowance)}</strong>. You may face an
            annual allowance charge on your tax return.
          </p>
          {carryForwardAvailable > 0 && (
            <p style={{ color: '#7F1D1D', fontSize: '0.875rem', lineHeight: '1.7' }}>
              <strong>Good news:</strong> You have {formatCurrency(carryForwardAvailable)} carry
              forward available, which may reduce or eliminate the charge.
            </p>
          )}
        </Alert>
      )}

      {/* Educational Section */}
      <div style={carryForwardSectionStyle}>
        <h3 style={sectionHeadingStyle}>Understanding annual allowance</h3>

        <div style={{ display: 'grid', gap: '16px' }}>
          <div
            style={{
              padding: '16px',
              backgroundColor: '#F8FAFC',
              borderRadius: '8px',
              border: '1px solid #E2E8F0',
            }}
          >
            <p style={{ fontSize: '0.875rem', fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>
              What is the annual allowance?
            </p>
            <p style={{ fontSize: '0.875rem', color: '#475569', lineHeight: '1.7' }}>
              The annual allowance is the maximum you can contribute to pensions each tax year while
              still getting tax relief. The standard allowance is £60,000, but it can be reduced if
              you have high income (tapered) or have accessed benefits flexibly (MPAA).
            </p>
          </div>

          <div
            style={{
              padding: '16px',
              backgroundColor: '#F8FAFC',
              borderRadius: '8px',
              border: '1px solid #E2E8F0',
            }}
          >
            <p style={{ fontSize: '0.875rem', fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>
              What happens if I exceed it?
            </p>
            <p style={{ fontSize: '0.875rem', color: '#475569', lineHeight: '1.7' }}>
              You'll pay an annual allowance charge on the excess, taxed at your marginal rate. You
              can sometimes ask your pension scheme to pay this (Scheme Pays), but this reduces your
              pension pot.
            </p>
          </div>

          <div
            style={{
              padding: '16px',
              backgroundColor: '#F8FAFC',
              borderRadius: '8px',
              border: '1px solid #E2E8F0',
            }}
          >
            <p style={{ fontSize: '0.875rem', fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>
              How can I maximize my contributions?
            </p>
            <p style={{ fontSize: '0.875rem', color: '#475569', lineHeight: '1.7' }}>
              Use carry forward from previous years if available. Spread large contributions across
              tax years. Consider salary sacrifice to reduce adjusted income (helps avoid tapering).
              Always check your allowance before making large contributions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
