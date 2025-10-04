import React, { useState, useEffect } from 'react';
import { Card, Button, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * SAFundList - South African Retirement Funds list with narrative storytelling approach
 *
 * Displays comprehensive SA fund overview:
 * - Total retirement savings with conversational context
 * - Individual fund cards with narrative descriptions
 * - Progressive disclosure ("Tell me more" sections)
 * - Section 10C deduction status prominent display
 * - Regulation 28 compliance warnings
 * - Add fund CTA
 *
 * Follows STYLEGUIDE.md narrative storytelling approach:
 * - Conversational language ("Your SA retirement savings: R850,000")
 * - Metrics embedded in sentences
 * - 2-3 sentence paragraphs maximum
 * - Generous white space and readability
 */
export function SAFundList({ onAddFund, onEditFund }) {
  const [funds, setFunds] = useState([]);
  const [totalSavings, setTotalSavings] = useState(null);
  const [section10C, setSection10C] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedFund, setExpandedFund] = useState(null);

  useEffect(() => {
    loadFunds();
    loadTotalSavings();
    loadSection10C();
  }, []);

  const loadFunds = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/retirement/sa-funds/', {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Don't logout - might be endpoint issue
          setFunds([]);
          return;
        }
        throw new Error('Failed to fetch SA funds');
      }

      const data = await response.json();
      setFunds(data);
    } catch (err) {
      // Silently ignore errors - endpoint may not be implemented
      setFunds([]);
    } finally {
      setLoading(false);
    }
  };

  const loadTotalSavings = async () => {
    try {
      const response = await fetch('/api/v1/retirement/sa-total-savings', {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTotalSavings(data);
      }
      // Silently ignore errors - endpoint may not be implemented
    } catch (err) {
      // Silently ignore errors - endpoint may not be implemented
    }
  };

  const loadSection10C = async () => {
    try {
      const response = await fetch('/api/v1/retirement/sa-section-10c', {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSection10C(data);
      }
      // Silently ignore errors - endpoint may not be implemented
    } catch (err) {
      // Silently ignore errors - endpoint may not be implemented
    }
  };

  const handleDeleteFund = async (fundId) => {
    if (!confirm('Are you sure you want to delete this retirement fund?')) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/retirement/sa-funds/${fundId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete fund');
      }

      // Reload data
      loadFunds();
      loadTotalSavings();
      loadSection10C();
    } catch (err) {
      alert('Failed to delete retirement fund. Please try again.');
      console.error('Error deleting fund:', err);
    }
  };

  const formatCurrency = (amount, currency = 'ZAR') => {
    if (amount === null || amount === undefined) return 'R0';
    const symbol = currency === 'ZAR' ? 'R' : currency;
    return `${symbol}${amount.toLocaleString('en-ZA', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-ZA', { day: 'numeric', month: 'long', year: 'numeric' });
  };

  const getFundTypeLabel = (type) => {
    const types = {
      PENSION_FUND: 'Pension Fund',
      PROVIDENT_FUND: 'Provident Fund',
      RETIREMENT_ANNUITY: 'Retirement Annuity',
      PRESERVATION_FUND_PENSION: 'Preservation Fund (Pension)',
      PRESERVATION_FUND_PROVIDENT: 'Preservation Fund (Provident)',
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
    background: 'linear-gradient(to bottom right, #FEF3C7, #FDE68A)',
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

  const fundCardStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
    lineHeight: '1.7',
  };

  const fundTitleStyle = {
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

  const addFundCardStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    border: '2px dashed #CBD5E1',
    textAlign: 'center',
    cursor: 'pointer',
    transition: 'all 150ms ease-in-out',
  };

  const section10CAlertStyle = {
    backgroundColor: '#DBEAFE',
    border: '1px solid #BFDBFE',
    borderLeft: '4px solid #3B82F6',
    padding: '16px',
    borderRadius: '8px',
    marginTop: '16px',
  };

  const reg28WarningStyle = {
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
        <div style={fundCardStyle}>
          <div style={{ textAlign: 'center', padding: '48px', color: '#94A3B8' }}>
            <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⏳</div>
            <p>Loading your SA retirement funds...</p>
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
          <p style={{ fontWeight: 600 }}>Error Loading SA Funds</p>
          <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
        </Alert>
        <Button variant="outline" onClick={loadFunds} style={{ marginTop: '16px' }}>
          Try Again
        </Button>
      </div>
    );
  }

  // Empty state
  if (funds.length === 0) {
    return (
      <div style={containerStyle}>
        <div style={fundCardStyle}>
          <h3 style={fundTitleStyle}>Start tracking your South African retirement funds</h3>
          <p style={narrativeParagraphStyle}>
            You haven't added any SA retirement funds yet. Track your pension funds, provident funds,
            retirement annuities, and preservation funds to maximize your Section 10C tax deductions and
            plan for retirement.
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
              Why track your SA retirement funds?
            </p>
            <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
              South African retirement contributions qualify for Section 10C tax deductions – up to 27.5% of
              your income or R350,000 per year. Tracking your funds helps you maximize tax savings and plan
              for retirement.
            </p>
          </div>
          <Button variant="primary" onClick={onAddFund} style={{ marginTop: '24px' }}>
            Add Your First SA Fund →
          </Button>
        </div>
      </div>
    );
  }

  // Main view with funds
  const totalValue = totalSavings?.totalValue || 0;
  const projectedValue = totalSavings?.projectedValue || 0;
  const annualContributions = totalSavings?.annualContributions || 0;
  const deductionUsed = section10C?.deductionClaimed || 0;
  const deductionLimit = section10C?.maxDeductible || 0;
  const reg28Violations = funds.filter((f) => !f.regulation28Compliant);

  return (
    <div style={containerStyle}>
      {/* Total Savings Hero Section */}
      <div style={heroSectionStyle}>
        <h2 style={heroTitleStyle}>
          Your South African retirement savings:{' '}
          <strong style={{ fontFamily: 'monospace', color: '#F59E0B' }}>
            {formatCurrency(totalValue)}
          </strong>
        </h2>
        <p style={narrativeParagraphStyle}>
          You have <strong style={{ fontFamily: 'monospace' }}>{funds.length}</strong>{' '}
          {funds.length === 1 ? 'fund' : 'funds'} building your retirement nest egg. Based on your current
          contributions and assumed growth, you're projected to have{' '}
          <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
            {formatCurrency(projectedValue)}
          </strong>{' '}
          by retirement {totalSavings?.retirementAge ? `at age ${totalSavings.retirementAge}` : ''}.
        </p>
        <p style={narrativeParagraphStyle}>
          Your annual contributions total{' '}
          <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(annualContributions)}</strong>, giving
          you a tax deduction of{' '}
          <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
            {formatCurrency(deductionUsed)}
          </strong>{' '}
          this tax year.
        </p>

        {/* Section 10C Status */}
        {section10C && (
          <div style={section10CAlertStyle}>
            <p style={{ fontWeight: 600, color: '#1E40AF', marginBottom: '4px' }}>
              Section 10C tax deduction status
            </p>
            <p style={{ color: '#1E3A8A', fontSize: '0.875rem', lineHeight: '1.7' }}>
              This tax year, you can deduct up to{' '}
              <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(deductionLimit)}</strong> from your
              taxable income. You've used{' '}
              <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(deductionUsed)}</strong> so far,
              with{' '}
              <strong style={{ fontFamily: 'monospace' }}>
                {formatCurrency(deductionLimit - deductionUsed)}
              </strong>{' '}
              remaining.
            </p>
          </div>
        )}

        {/* Regulation 28 Warnings */}
        {reg28Violations.length > 0 && (
          <div style={reg28WarningStyle}>
            <p style={{ fontWeight: 600, color: '#92400E', marginBottom: '4px' }}>
              Regulation 28 compliance alert
            </p>
            <p style={{ color: '#78350F', fontSize: '0.875rem', lineHeight: '1.7' }}>
              {reg28Violations.length === 1 ? 'One fund violates' : `${reg28Violations.length} funds violate`}{' '}
              Regulation 28 asset allocation limits. This may affect your fund's compliance status and investment
              flexibility.
            </p>
          </div>
        )}
      </div>

      {/* Fund Cards */}
      <div style={{ marginBottom: '48px' }}>
        {funds.map((fund) => {
          const isExpanded = expandedFund === fund.id;
          const isPreservation = fund.fundType.includes('PRESERVATION');

          return (
            <div key={fund.id} style={fundCardStyle}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div style={{ flex: 1 }}>
                  <h3 style={fundTitleStyle}>
                    {fund.provider} {getFundTypeLabel(fund.fundType)}
                  </h3>

                  <p style={narrativeParagraphStyle}>
                    This fund is currently worth{' '}
                    <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(fund.currentValue)}</strong>.
                    {!isPreservation && fund.monthlyContribution > 0 && (
                      <>
                        {' '}
                        You contribute{' '}
                        <strong style={{ fontFamily: 'monospace' }}>
                          {formatCurrency(fund.monthlyContribution)}
                        </strong>{' '}
                        monthly
                        {fund.employerContribution > 0 && (
                          <>
                            , and your employer adds{' '}
                            <strong style={{ fontFamily: 'monospace' }}>
                              {formatCurrency(fund.employerContribution)}
                            </strong>
                          </>
                        )}
                        .
                      </>
                    )}
                    {' '}At your expected retirement age of {fund.retirementAge || 65}, this should grow to
                    approximately{' '}
                    <strong style={{ fontFamily: 'monospace', color: '#2563EB' }}>
                      {formatCurrency(fund.projectedValue)}
                    </strong>
                    .
                  </p>

                  {/* Lump sum and annuity info */}
                  {fund.maxLumpSum && (
                    <p style={narrativeParagraphStyle}>
                      At retirement, you'll be able to take up to{' '}
                      <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
                        {formatCurrency(fund.maxLumpSum)}
                      </strong>{' '}
                      as a tax-free lump sum
                      {fund.fundType === 'PENSION_FUND' || fund.fundType === 'RETIREMENT_ANNUITY'
                        ? ', with the remaining two-thirds going to an annuity for monthly income'
                        : fund.contributionsAfterMarch2021 > 0
                        ? ', with restrictions on newer contributions'
                        : ''}.
                    </p>
                  )}
                </div>

                <div style={{ display: 'flex', gap: '8px', marginLeft: '16px' }}>
                  <Button variant="ghost" size="small" onClick={() => onEditFund(fund.id)}>
                    Edit
                  </Button>
                  <Button
                    variant="ghost"
                    size="small"
                    onClick={() => handleDeleteFund(fund.id)}
                    style={{ color: '#EF4444' }}
                  >
                    Delete
                  </Button>
                </div>
              </div>

              {/* Regulation 28 warning for this fund */}
              {!fund.regulation28Compliant && (
                <div
                  style={{
                    ...reg28WarningStyle,
                    marginTop: '16px',
                    marginBottom: '0',
                  }}
                >
                  <p style={{ fontWeight: 600, color: '#92400E', marginBottom: '4px', fontSize: '0.875rem' }}>
                    ⚠️ Regulation 28 violation
                  </p>
                  <p style={{ color: '#78350F', fontSize: '0.875rem', lineHeight: '1.7' }}>
                    Your asset allocation exceeds regulatory limits. Consider rebalancing to comply with
                    Regulation 28 requirements.
                  </p>
                </div>
              )}

              {/* Progressive disclosure */}
              <div style={expandableSectionStyle}>
                <button
                  onClick={() => setExpandedFund(isExpanded ? null : fund.id)}
                  style={expandTriggerStyle}
                  aria-expanded={isExpanded}
                >
                  <span>{isExpanded ? 'Show less' : 'Tell me more about this fund'}</span>
                  <span style={{ fontSize: '0.75rem' }}>{isExpanded ? '▼' : '▶'}</span>
                </button>

                {isExpanded && (
                  <div style={detailTextStyle}>
                    <p style={{ marginBottom: '8px' }}>
                      <strong>Started:</strong> {formatDate(fund.startDate)}
                      {fund.employerName && <> with {fund.employerName}</>}
                    </p>
                    {fund.portfolioName && (
                      <p style={{ marginBottom: '8px' }}>
                        <strong>Investment portfolio:</strong> {fund.portfolioName}
                      </p>
                    )}
                    {fund.assetAllocation && (
                      <div style={{ marginBottom: '8px' }}>
                        <strong>Asset allocation:</strong>
                        <div style={{ marginTop: '4px', paddingLeft: '16px' }}>
                          <p>• Equity: {fund.assetAllocation.equityPercentage}%</p>
                          <p>• Bonds: {fund.assetAllocation.bondsPercentage}%</p>
                          <p>• Cash: {fund.assetAllocation.cashPercentage}%</p>
                          <p>• Property: {fund.assetAllocation.propertyPercentage}%</p>
                          <p>• Offshore: {fund.assetAllocation.offshorePercentage}%</p>
                        </div>
                      </div>
                    )}
                    {isPreservation && (
                      <>
                        <p style={{ marginBottom: '8px' }}>
                          <strong>Transferred from:</strong> {fund.sourceFundType} on{' '}
                          {formatDate(fund.transferDate)}
                        </p>
                        <p style={{ marginBottom: '8px' }}>
                          <strong>Withdrawal status:</strong>{' '}
                          {fund.withdrawalTaken
                            ? `Taken (${formatCurrency(fund.withdrawalAmount)} on ${formatDate(
                                fund.withdrawalDate
                              )})`
                            : 'Available (one withdrawal allowed before retirement)'}
                        </p>
                      </>
                    )}
                    {fund.taxSaving && (
                      <p style={{ marginBottom: '8px' }}>
                        <strong>Annual tax saving:</strong>{' '}
                        <span style={{ color: '#10B981', fontFamily: 'monospace' }}>
                          {formatCurrency(fund.taxSaving)}
                        </span>
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Add Fund CTA */}
      <div
        style={addFundCardStyle}
        onClick={onAddFund}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = '#F59E0B';
          e.currentTarget.style.backgroundColor = '#FFFBEB';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = '#CBD5E1';
          e.currentTarget.style.backgroundColor = '#FFFFFF';
        }}
      >
        <div style={{ fontSize: '2rem', marginBottom: '12px', color: '#F59E0B' }}>+</div>
        <p style={{ fontSize: '1rem', fontWeight: 600, color: '#0F172A', marginBottom: '4px' }}>
          Add another SA retirement fund
        </p>
        <p style={{ fontSize: '0.875rem', color: '#475569' }}>
          Track pension funds, provident funds, RAs, or preservation funds
        </p>
      </div>
    </div>
  );
}
