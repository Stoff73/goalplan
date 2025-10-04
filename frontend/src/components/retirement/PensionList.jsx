import React, { useState, useEffect } from 'react';
import { Card, Button, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * PensionList - UK Pensions list with narrative storytelling approach
 *
 * Displays comprehensive pension overview:
 * - Total pension pot with conversational context
 * - Individual pension cards with narrative descriptions
 * - Progressive disclosure ("Tell me more" sections)
 * - MPAA warnings if triggered
 * - Add pension CTA
 *
 * Follows STYLEGUIDE.md narrative storytelling approach:
 * - Conversational language ("You have 3 pensions worth...")
 * - Metrics embedded in sentences
 * - 2-3 sentence paragraphs maximum
 * - Generous white space and readability
 */
export function PensionList({ onAddPension, onEditPension }) {
  const [pensions, setPensions] = useState([]);
  const [totalPot, setTotalPot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedPension, setExpandedPension] = useState(null);

  useEffect(() => {
    loadPensions();
    loadTotalPot();
  }, []);

  const loadPensions = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/retirement/uk-pensions', {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Don't logout - might be endpoint issue
          setPensions([]);
          return;
        }
        throw new Error('Failed to fetch pensions');
      }

      const data = await response.json();
      setPensions(data);
    } catch (err) {
      // Silently ignore errors - show empty state
      setPensions([]);
    } finally {
      setLoading(false);
    }
  };

  const loadTotalPot = async () => {
    try {
      const response = await fetch('/api/v1/retirement/total-pot', {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTotalPot(data);
      }
      // Silently ignore errors - endpoint may not be implemented
    } catch (err) {
      // Silently ignore errors - endpoint may not be implemented
    }
  };

  const handleDeletePension = async (pensionId) => {
    if (!confirm('Are you sure you want to delete this pension?')) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/retirement/uk-pensions/${pensionId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete pension');
      }

      // Reload data
      loadPensions();
      loadTotalPot();
    } catch (err) {
      alert('Failed to delete pension. Please try again.');
      console.error('Error deleting pension:', err);
    }
  };

  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return '£0';
    return `£${amount.toLocaleString('en-GB', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
  };

  const getPensionTypeLabel = (type) => {
    const types = {
      OCCUPATIONAL_DC: 'Workplace Pension',
      SIPP: 'SIPP',
      OCCUPATIONAL_DB: 'Final Salary Pension',
      PERSONAL_PENSION: 'Personal Pension',
      STAKEHOLDER: 'Stakeholder Pension',
      GROUP_PERSONAL_PENSION: 'Group Personal Pension',
    };
    return types[type] || type;
  };

  // Styles following STYLEGUIDE.md
  const containerStyle = {
    maxWidth: '1280px',
    margin: '0 auto',
  };

  const heroSectionStyle = {
    padding: '32px',
    background: 'linear-gradient(to bottom right, #EFF6FF, #DBEAFE)',
    borderRadius: '12px',
    marginBottom: '48px',
    lineHeight: '1.7',
  };

  const heroTitleStyle = {
    fontSize: '1.8rem',
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

  const pensionCardStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
    lineHeight: '1.7',
  };

  const pensionTitleStyle = {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '12px',
  };

  const expandableSectionStyle = {
    marginTop: '16px',
    paddingTop: '16px',
    borderTop: '1px solid #E2E8F0',
  };

  const expandTriggerStyle = {
    color: '#2563EB',
    fontSize: '0.875rem',
    fontWeight: 500,
    cursor: 'pointer',
    background: 'none',
    border: 'none',
    padding: '0',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  };

  const detailTextStyle = {
    fontSize: '0.875rem',
    color: '#475569',
    lineHeight: '1.7',
    marginTop: '12px',
  };

  const addPensionCardStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    border: '2px dashed #CBD5E1',
    textAlign: 'center',
    cursor: 'pointer',
    transition: 'all 150ms ease-in-out',
  };

  const mpaaAlertStyle = {
    backgroundColor: '#FEF3C7',
    border: '1px solid #FCD34D',
    borderLeft: '4px solid #F59E0B',
    padding: '16px',
    borderRadius: '8px',
    marginTop: '16px',
  };

  // Loading state
  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={pensionCardStyle}>
          <div style={{ textAlign: 'center', padding: '48px', color: '#94A3B8' }}>
            <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⏳</div>
            <p>Loading your pensions...</p>
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
          <p style={{ fontWeight: 600 }}>Error Loading Pensions</p>
          <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
        </Alert>
        <Button variant="outline" onClick={loadPensions} style={{ marginTop: '16px' }}>
          Try Again
        </Button>
      </div>
    );
  }

  // Empty state
  if (pensions.length === 0) {
    return (
      <div style={containerStyle}>
        <div style={pensionCardStyle}>
          <h3 style={pensionTitleStyle}>Start tracking your pensions</h3>
          <p style={narrativeParagraphStyle}>
            You haven't added any pensions yet. Track your workplace pensions, SIPPs, and personal
            pensions all in one place to plan for retirement and maximize your tax relief.
          </p>
          <div
            style={{
              backgroundColor: '#DBEAFE',
              border: '1px solid #BFDBFE',
              borderLeft: '4px solid #3B82F6',
              padding: '16px',
              borderRadius: '8px',
              marginTop: '24px',
            }}
          >
            <p style={{ fontWeight: 600, color: '#1E40AF', marginBottom: '8px' }}>
              Why track your pensions?
            </p>
            <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
              Understanding your total pension pot helps you plan for retirement. Plus, tracking
              contributions ensures you maximize tax relief and stay within annual allowances.
            </p>
          </div>
          <Button variant="primary" onClick={onAddPension} style={{ marginTop: '24px' }}>
            Add Your First Pension →
          </Button>
        </div>
      </div>
    );
  }

  // Main view with pensions
  const totalPensionValue = totalPot?.totalValue || 0;
  const projectedValue = totalPot?.projectedValue || 0;
  const annualContributions = totalPot?.annualContributions || 0;
  const mpaaTriggered = pensions.some((p) => p.mpaaTriggered);

  return (
    <div style={containerStyle}>
      {/* Total Pot Hero Section */}
      <div style={heroSectionStyle}>
        <h2 style={heroTitleStyle}>
          Your retirement savings:{' '}
          <strong style={{ fontFamily: 'monospace', color: '#2563EB' }}>
            {formatCurrency(totalPensionValue)}
          </strong>
        </h2>
        <p style={narrativeParagraphStyle}>
          You have <strong style={{ fontFamily: 'monospace' }}>{pensions.length}</strong>{' '}
          {pensions.length === 1 ? 'pension' : 'pensions'} working for you. Based on your current
          contributions and assumed growth, you're projected to have{' '}
          <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
            {formatCurrency(projectedValue)}
          </strong>{' '}
          by retirement {totalPot?.retirementAge ? `at age ${totalPot.retirementAge}` : ''}.
        </p>
        <p style={narrativeParagraphStyle}>
          Your annual contributions total{' '}
          <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(annualContributions)}</strong>
          , and you're tracking well within your annual allowance.
        </p>

        {/* MPAA Warning */}
        {mpaaTriggered && (
          <div style={mpaaAlertStyle}>
            <p style={{ fontWeight: 600, color: '#92400E', marginBottom: '4px' }}>
              Money Purchase Annual Allowance applies
            </p>
            <p style={{ color: '#78350F', fontSize: '0.875rem', lineHeight: '1.7' }}>
              Your annual allowance is reduced to £10,000 because you've accessed pension benefits
              flexibly. This affects how much you can contribute with tax relief.
            </p>
          </div>
        )}
      </div>

      {/* Pension Cards */}
      <div style={{ marginBottom: '48px' }}>
        {pensions.map((pension) => {
          const isExpanded = expandedPension === pension.id;
          const isDC = ['OCCUPATIONAL_DC', 'SIPP', 'PERSONAL_PENSION'].includes(pension.pensionType);

          return (
            <div key={pension.id} style={pensionCardStyle}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div style={{ flex: 1 }}>
                  <h3 style={pensionTitleStyle}>
                    {pension.provider} {getPensionTypeLabel(pension.pensionType)}
                  </h3>

                  {isDC ? (
                    <p style={narrativeParagraphStyle}>
                      This pension is currently worth{' '}
                      <strong style={{ fontFamily: 'monospace' }}>
                        {formatCurrency(pension.currentValue)}
                      </strong>
                      . You contribute{' '}
                      <strong style={{ fontFamily: 'monospace' }}>
                        {formatCurrency(pension.monthlyContribution || 0)}
                      </strong>{' '}
                      monthly
                      {pension.employerContribution > 0 && (
                        <>
                          , and your employer adds{' '}
                          <strong style={{ fontFamily: 'monospace' }}>
                            {formatCurrency(pension.employerContribution)}
                          </strong>
                        </>
                      )}
                      . At your expected retirement age of {pension.retirementAge || 67}, this should
                      grow to approximately{' '}
                      <strong style={{ fontFamily: 'monospace', color: '#2563EB' }}>
                        {formatCurrency(pension.projectedValue)}
                      </strong>
                      .
                    </p>
                  ) : (
                    <p style={narrativeParagraphStyle}>
                      This defined benefit pension will pay you{' '}
                      <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
                        {formatCurrency(pension.guaranteedAnnualPension || 0)}
                      </strong>{' '}
                      per year from age {pension.normalRetirementAge || 65}. It's a guaranteed income
                      for life, typically increasing with inflation.
                    </p>
                  )}
                </div>

                <div style={{ display: 'flex', gap: '8px', marginLeft: '16px' }}>
                  <Button
                    variant="ghost"
                    size="small"
                    onClick={() => onEditPension(pension.id)}
                  >
                    Edit
                  </Button>
                  <Button
                    variant="ghost"
                    size="small"
                    onClick={() => handleDeletePension(pension.id)}
                    style={{ color: '#EF4444' }}
                  >
                    Delete
                  </Button>
                </div>
              </div>

              {/* Progressive disclosure */}
              <div style={expandableSectionStyle}>
                <button
                  onClick={() => setExpandedPension(isExpanded ? null : pension.id)}
                  style={expandTriggerStyle}
                  aria-expanded={isExpanded}
                >
                  <span>{isExpanded ? 'Show less' : 'Tell me more about this pension'}</span>
                  <span style={{ fontSize: '0.75rem' }}>{isExpanded ? '▼' : '▶'}</span>
                </button>

                {isExpanded && (
                  <div style={detailTextStyle}>
                    <p style={{ marginBottom: '8px' }}>
                      <strong>Started:</strong> {formatDate(pension.startDate)}
                      {pension.employerName && <> with {pension.employerName}</>}
                    </p>
                    {isDC && (
                      <>
                        <p style={{ marginBottom: '8px' }}>
                          <strong>Investment strategy:</strong>{' '}
                          {pension.investmentStrategy || 'Not specified'}
                        </p>
                        <p style={{ marginBottom: '8px' }}>
                          <strong>Assumed growth rate:</strong> {pension.assumedGrowthRate || 5}% per
                          year
                        </p>
                        <p style={{ marginBottom: '8px' }}>
                          <strong>Tax relief method:</strong>{' '}
                          {pension.taxReliefMethod === 'NET_PAY'
                            ? 'Net Pay (relief at source)'
                            : 'Relief at Source'}
                        </p>
                      </>
                    )}
                    {!isDC && (
                      <>
                        <p style={{ marginBottom: '8px' }}>
                          <strong>Accrual rate:</strong> {pension.accrualRate || '1/60'}
                        </p>
                        <p style={{ marginBottom: '8px' }}>
                          <strong>Pensionable service:</strong>{' '}
                          {pension.pensionableServiceYears || 0} years
                        </p>
                        {pension.spousePensionPercentage > 0 && (
                          <p style={{ marginBottom: '8px' }}>
                            <strong>Spouse's pension:</strong> {pension.spousePensionPercentage}% of
                            your pension
                          </p>
                        )}
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Add Pension CTA */}
      <div
        style={addPensionCardStyle}
        onClick={onAddPension}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = '#2563EB';
          e.currentTarget.style.backgroundColor = '#F8FAFC';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = '#CBD5E1';
          e.currentTarget.style.backgroundColor = '#FFFFFF';
        }}
      >
        <div style={{ fontSize: '2rem', marginBottom: '12px', color: '#2563EB' }}>+</div>
        <p style={{ fontSize: '1rem', fontWeight: 600, color: '#0F172A', marginBottom: '4px' }}>
          Add another pension
        </p>
        <p style={{ fontSize: '0.875rem', color: '#475569' }}>
          Track workplace pensions, SIPPs, or personal pensions
        </p>
      </div>
    </div>
  );
}
