import React, { useState, useEffect } from 'react';
import { Card, Button, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * TaxSummary - Comprehensive tax summary dashboard
 *
 * Displays user's tax liabilities across UK and South Africa with narrative storytelling:
 * - Overall tax summary with conversational context
 * - UK tax breakdown (Income Tax, NI, CGT, Dividend Tax)
 * - SA tax breakdown (Income Tax, CGT, Dividend Tax)
 * - Income breakdown by source
 * - Tax efficiency score (0-100) with recommendations
 * - Actionable insights for tax optimization
 *
 * Follows STYLEGUIDE.md narrative storytelling approach:
 * - Conversational language ("You'll owe approximately £X,XXX this year")
 * - Metrics embedded in sentences with context
 * - 2-3 sentence paragraphs maximum
 * - Progressive disclosure ("Tell me more" sections)
 * - Generous white space and readability
 * - Educational tone with explanations
 */
export function TaxSummary() {
  const [taxData, setTaxData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedSections, setExpandedSections] = useState({
    ukDetails: false,
    saDetails: false,
    incomeBreakdown: false,
    insights: true, // Default open for insights
  });

  useEffect(() => {
    loadTaxData();
  }, []);

  const loadTaxData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/tax/summary', {
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
          // No income data yet
          setTaxData(null);
          setLoading(false);
          return;
        }
        throw new Error('Failed to fetch tax summary data');
      }

      const data = await response.json();
      setTaxData(data);
    } catch (err) {
      setError('Failed to load tax summary. Please try again.');
      console.error('Error loading tax summary:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const formatCurrency = (amount, currency = 'GBP') => {
    if (amount === null || amount === undefined) return currency === 'GBP' ? '£0' : 'R0';
    const symbol = currency === 'GBP' ? '£' : currency === 'ZAR' ? 'R' : currency;
    return `${symbol}${amount.toLocaleString('en-GB', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })}`;
  };

  const formatCurrencyShort = (amount, currency = 'GBP') => {
    if (amount === null || amount === undefined) return currency === 'GBP' ? '£0' : 'R0';
    const symbol = currency === 'GBP' ? '£' : currency === 'ZAR' ? 'R' : currency;

    if (amount >= 1000000) {
      return `${symbol}${(amount / 1000000).toFixed(1)}m`;
    }
    if (amount >= 1000) {
      return `${symbol}${(amount / 1000).toFixed(0)}k`;
    }
    return `${symbol}${amount.toLocaleString('en-GB')}`;
  };

  const formatPercentage = (value) => {
    if (value === null || value === undefined) return '0%';
    return `${value.toFixed(1)}%`;
  };

  const calculateTaxEfficiencyScore = (data) => {
    if (!data) return 0;

    let score = 0;
    let maxScore = 100;

    // ISA allowance utilization (20 points)
    if (data.uk_tax && data.uk_tax.isa_allowance_used !== undefined) {
      const isaUsageRate = (data.uk_tax.isa_allowance_used / 20000) * 100;
      score += Math.min(isaUsageRate / 100 * 20, 20);
    }

    // Pension contributions (20 points)
    if (data.uk_tax && data.uk_tax.pension_contributions !== undefined) {
      const pensionUsageRate = (data.uk_tax.pension_contributions / 60000) * 100;
      score += Math.min(pensionUsageRate / 100 * 20, 20);
    } else {
      score += 10; // Partial credit if no data
    }

    // Personal allowance utilization (20 points)
    if (data.uk_tax && data.uk_tax.personal_allowance_used !== undefined) {
      const allowanceUsageRate = (data.uk_tax.personal_allowance_used / 12570) * 100;
      score += Math.min(allowanceUsageRate / 100 * 20, 20);
    } else {
      score += 15;
    }

    // Annual exempt amounts used (20 points)
    if (data.uk_tax && data.uk_tax.capital_gains_tax && data.uk_tax.capital_gains_tax.annual_exemption_used !== undefined) {
      const cgtExemptionUsed = data.uk_tax.capital_gains_tax.annual_exemption_used > 0 ? 20 : 10;
      score += cgtExemptionUsed;
    } else {
      score += 10;
    }

    // Tax-efficient account usage (20 points)
    if (data.sa_tax && data.sa_tax.tfsa_contributions !== undefined) {
      const tfsaUsageRate = (data.sa_tax.tfsa_contributions / 36000) * 100;
      score += Math.min(tfsaUsageRate / 100 * 20, 20);
    } else {
      score += 10;
    }

    return Math.round(score);
  };

  const getTaxEfficiencyColor = (score) => {
    if (score >= 80) return '#10B981'; // Green
    if (score >= 60) return '#F59E0B'; // Amber
    return '#EF4444'; // Red
  };

  const getTaxEfficiencyMessage = (score) => {
    if (score >= 80) return 'excellent tax efficiency!';
    if (score >= 60) return 'good tax efficiency with room for improvement.';
    return 'significant opportunity to optimize your tax position.';
  };

  const generateInsights = (data) => {
    const insights = [];

    // ISA allowance insight
    if (data.uk_tax && data.uk_tax.isa_allowance_used < 20000) {
      const remaining = 20000 - data.uk_tax.isa_allowance_used;
      insights.push({
        type: 'tip',
        title: 'Maximize your ISA allowance',
        description: `You have ${formatCurrency(remaining)} of ISA allowance remaining this tax year. Moving investments into an ISA can save you tax on dividends and capital gains.`,
        savingsPotential: Math.round(remaining * 0.2 * 0.075), // Rough estimate
      });
    }

    // Pension contribution insight
    if (data.uk_tax && data.uk_tax.pension_contributions < 40000) {
      const remaining = 40000 - data.uk_tax.pension_contributions;
      insights.push({
        type: 'tip',
        title: 'Boost your pension contributions',
        description: `You can contribute up to ${formatCurrency(remaining)} more to your pension this year with tax relief. At higher rate (40%), this could save you ${formatCurrency(remaining * 0.4)} in tax.`,
        savingsPotential: Math.round(remaining * 0.4),
      });
    }

    // CGT annual exemption insight
    if (data.uk_tax && data.uk_tax.capital_gains_tax && data.uk_tax.capital_gains_tax.annual_exemption_used === 0) {
      insights.push({
        type: 'tip',
        title: 'Use your CGT annual exemption',
        description: 'You have a £3,000 annual exemption for capital gains. Consider realizing gains up to this amount tax-free before the tax year ends.',
        savingsPotential: 600, // £3,000 * 20%
      });
    }

    // High effective tax rate warning
    if (data.overall && data.overall.effective_tax_rate > 35) {
      insights.push({
        type: 'warning',
        title: 'High effective tax rate',
        description: `Your effective tax rate of ${formatPercentage(data.overall.effective_tax_rate)} is quite high. Consider reviewing tax-efficient investment structures and allowances to reduce your liability.`,
      });
    }

    // SA TFSA insight
    if (data.sa_tax && data.sa_tax.tfsa_contributions < 36000) {
      const remaining = 36000 - data.sa_tax.tfsa_contributions;
      insights.push({
        type: 'tip',
        title: 'Maximize your TFSA contributions',
        description: `You have R${remaining.toLocaleString()} remaining TFSA allowance this year. TFSA returns are completely tax-free - no tax on interest, dividends, or capital gains.`,
      });
    }

    return insights;
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
    marginBottom: '16px',
  };

  const pageSubheadingStyle = {
    fontSize: '1.1rem',
    color: '#475569',
    marginBottom: '32px',
    lineHeight: '1.7',
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

  const metricGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
    gap: '16px',
    marginTop: '24px',
    marginBottom: '24px',
  };

  const compactMetricStyle = {
    padding: '16px',
    backgroundColor: '#F8FAFC',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
  };

  const metricValueStyle = {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#0F172A',
    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace',
    marginBottom: '4px',
  };

  const metricLabelStyle = {
    fontSize: '0.75rem',
    color: '#475569',
  };

  const calloutBoxStyle = (type = 'info') => {
    const colors = {
      info: { bg: '#DBEAFE', border: '#BFDBFE', borderLeft: '#3B82F6' },
      tip: { bg: '#D1FAE5', border: '#A7F3D0', borderLeft: '#10B981' },
      warning: { bg: '#FEF3C7', border: '#FDE68A', borderLeft: '#F59E0B' },
      error: { bg: '#FEE2E2', border: '#FECACA', borderLeft: '#EF4444' },
    };
    const color = colors[type] || colors.info;

    return {
      backgroundColor: color.bg,
      border: `1px solid ${color.border}`,
      borderLeft: `4px solid ${color.borderLeft}`,
      padding: '16px',
      borderRadius: '8px',
      marginTop: '16px',
      marginBottom: '16px',
    };
  };

  const expandableSectionStyle = {
    marginTop: '24px',
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

  const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    marginTop: '16px',
  };

  const tableRowStyle = {
    borderBottom: '1px solid #F1F5F9',
  };

  const tableCellStyle = {
    padding: '12px 8px',
    fontSize: '0.875rem',
    color: '#0F172A',
  };

  const tableCellRightStyle = {
    ...tableCellStyle,
    textAlign: 'right',
    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace',
  };

  const efficiencyScoreContainerStyle = (score) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '24px',
    padding: '24px',
    backgroundColor: '#F8FAFC',
    borderRadius: '12px',
    border: '2px solid #E2E8F0',
    marginTop: '24px',
  });

  const scoreCircleStyle = (score) => {
    const color = getTaxEfficiencyColor(score);
    return {
      width: '120px',
      height: '120px',
      borderRadius: '50%',
      border: `8px solid ${color}`,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      backgroundColor: '#FFFFFF',
    };
  };

  const scoreValueStyle = {
    fontSize: '2.5rem',
    fontWeight: 'bold',
    color: '#0F172A',
    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace',
  };

  const scoreMaxStyle = {
    fontSize: '0.875rem',
    color: '#94A3B8',
    marginTop: '-8px',
  };

  // Loading state
  if (loading) {
    return (
      <div style={dashboardContainerStyle}>
        <div style={narrativeSectionStyle}>
          <div style={{ textAlign: 'center', padding: '48px', color: '#94A3B8' }}>
            <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⏳</div>
            <p>Loading your tax summary...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={dashboardContainerStyle}>
        <h1 style={pageHeadingStyle}>Your Tax Summary</h1>
        <div style={narrativeSectionStyle}>
          <Alert variant="error">
            <p style={{ fontWeight: 600 }}>Error Loading Tax Summary</p>
            <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
          </Alert>
          <Button
            variant="outline"
            onClick={loadTaxData}
            style={{ marginTop: '16px' }}
          >
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  // Empty state - no income data
  if (!taxData || (!taxData.uk_tax && !taxData.sa_tax)) {
    return (
      <div style={dashboardContainerStyle}>
        <h1 style={pageHeadingStyle}>Your Tax Summary</h1>
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>No Income Data Yet</h3>

          <p style={narrativeParagraphStyle}>
            You haven't added any income sources yet. Add your employment income, dividends,
            capital gains, or other income to see your estimated tax liability.
          </p>

          <div style={calloutBoxStyle('info')}>
            <p style={{ fontWeight: 600, color: '#1E40AF', marginBottom: '8px' }}>
              Why track your tax?
            </p>
            <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
              Understanding your tax position helps you plan ahead, avoid surprises, and
              identify opportunities to reduce your tax liability legally through allowances,
              reliefs, and tax-efficient investments.
            </p>
          </div>

          <Button variant="primary" style={{ marginTop: '24px' }}>
            Add Income Sources →
          </Button>
        </div>
      </div>
    );
  }

  // Calculate tax efficiency score
  const efficiencyScore = calculateTaxEfficiencyScore(taxData);
  const insights = generateInsights(taxData);

  // Main dashboard view with data
  const { overall, uk_tax, sa_tax, income_breakdown } = taxData;

  return (
    <div style={dashboardContainerStyle}>
      <h1 style={pageHeadingStyle}>
        Your Tax Summary: {overall && overall.total_tax > 0 ? `${formatCurrency(overall.total_tax)} estimated` : 'No tax liability'}
      </h1>
      {overall && overall.previous_year_tax && (
        <p style={pageSubheadingStyle}>
          {overall.total_tax > overall.previous_year_tax
            ? `That's ${formatCurrency(overall.total_tax - overall.previous_year_tax)} more than last year`
            : `That's ${formatCurrency(overall.previous_year_tax - overall.total_tax)} less than last year`}
        </p>
      )}

      {/* Overall Tax Summary Section */}
      {overall && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Your Tax Situation</h3>

          <p style={narrativeParagraphStyle}>
            Based on your current income and investments, you'll owe approximately{' '}
            <strong style={{ fontFamily: 'monospace', fontSize: '1.1rem' }}>
              {formatCurrency(overall.total_tax)}
            </strong>{' '}
            in taxes this year. That works out to an effective tax rate of{' '}
            <strong>{formatPercentage(overall.effective_tax_rate)}</strong> on your total income
            of <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(overall.total_income)}</strong>.
          </p>

          {uk_tax && sa_tax && (
            <p style={narrativeParagraphStyle}>
              Your tax liability is split across both jurisdictions: <strong>{formatCurrency(uk_tax.total_tax)}</strong> in
              the UK and <strong>{formatCurrency(sa_tax.total_tax, 'ZAR')}</strong> in South Africa.
            </p>
          )}

          {/* Metric Grid */}
          <div style={metricGridStyle}>
            <div style={compactMetricStyle}>
              <div style={metricValueStyle}>{formatCurrencyShort(overall.total_tax)}</div>
              <div style={metricLabelStyle}>total tax</div>
            </div>
            <div style={compactMetricStyle}>
              <div style={metricValueStyle}>{formatPercentage(overall.effective_tax_rate)}</div>
              <div style={metricLabelStyle}>effective rate</div>
            </div>
            <div style={compactMetricStyle}>
              <div style={metricValueStyle}>{formatCurrencyShort(overall.total_income)}</div>
              <div style={metricLabelStyle}>total income</div>
            </div>
            {overall.net_income && (
              <div style={compactMetricStyle}>
                <div style={metricValueStyle}>{formatCurrencyShort(overall.net_income)}</div>
                <div style={metricLabelStyle}>after-tax income</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* UK Tax Liabilities Section */}
      {uk_tax && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Your UK Tax Liabilities</h3>

          <p style={narrativeParagraphStyle}>
            In the UK, you'll pay <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(uk_tax.total_tax)}</strong> in
            total taxes. This includes Income Tax, National Insurance, and any Capital Gains or Dividend Tax you owe.
          </p>

          {/* UK Tax Breakdown Table */}
          <table style={tableStyle}>
            <tbody>
              {uk_tax.income_tax && uk_tax.income_tax.total_tax > 0 && (
                <tr style={tableRowStyle}>
                  <td style={tableCellStyle}>
                    <strong>Income Tax</strong>
                    {uk_tax.income_tax.tax_by_band && (
                      <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '4px' }}>
                        {uk_tax.income_tax.tax_by_band.map((band, idx) => (
                          <div key={idx}>
                            {formatCurrency(band.taxable_amount)} @ {formatPercentage(band.rate * 100)}
                          </div>
                        ))}
                      </div>
                    )}
                  </td>
                  <td style={tableCellRightStyle}>
                    <strong>{formatCurrency(uk_tax.income_tax.total_tax)}</strong>
                  </td>
                </tr>
              )}
              {uk_tax.national_insurance && uk_tax.national_insurance.total_ni > 0 && (
                <tr style={tableRowStyle}>
                  <td style={tableCellStyle}>
                    <strong>National Insurance</strong>
                    <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '4px' }}>
                      {uk_tax.national_insurance.class_1_ni && `Class 1: ${formatCurrency(uk_tax.national_insurance.class_1_ni)}`}
                      {uk_tax.national_insurance.class_2_ni && `Class 2: ${formatCurrency(uk_tax.national_insurance.class_2_ni)}`}
                      {uk_tax.national_insurance.class_4_ni && ` Class 4: ${formatCurrency(uk_tax.national_insurance.class_4_ni)}`}
                    </div>
                  </td>
                  <td style={tableCellRightStyle}>
                    <strong>{formatCurrency(uk_tax.national_insurance.total_ni)}</strong>
                  </td>
                </tr>
              )}
              {uk_tax.capital_gains_tax && uk_tax.capital_gains_tax.total_cgt > 0 && (
                <tr style={tableRowStyle}>
                  <td style={tableCellStyle}>
                    <strong>Capital Gains Tax</strong>
                    <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '4px' }}>
                      Annual exemption used: {formatCurrency(uk_tax.capital_gains_tax.annual_exemption_used)}
                    </div>
                  </td>
                  <td style={tableCellRightStyle}>
                    <strong>{formatCurrency(uk_tax.capital_gains_tax.total_cgt)}</strong>
                  </td>
                </tr>
              )}
              {uk_tax.dividend_tax && uk_tax.dividend_tax.total_tax > 0 && (
                <tr style={tableRowStyle}>
                  <td style={tableCellStyle}>
                    <strong>Dividend Tax</strong>
                    <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '4px' }}>
                      Dividend allowance used: {formatCurrency(uk_tax.dividend_tax.dividend_allowance_used)}
                    </div>
                  </td>
                  <td style={tableCellRightStyle}>
                    <strong>{formatCurrency(uk_tax.dividend_tax.total_tax)}</strong>
                  </td>
                </tr>
              )}
              <tr style={{ ...tableRowStyle, borderTop: '2px solid #E2E8F0' }}>
                <td style={{ ...tableCellStyle, fontWeight: 'bold', fontSize: '1rem' }}>
                  Total UK Tax
                </td>
                <td style={{ ...tableCellRightStyle, fontWeight: 'bold', fontSize: '1rem', color: '#EF4444' }}>
                  {formatCurrency(uk_tax.total_tax)}
                </td>
              </tr>
            </tbody>
          </table>

          {/* Expandable UK details */}
          <div style={expandableSectionStyle}>
            <button
              onClick={() => toggleSection('ukDetails')}
              style={expandTriggerStyle}
              aria-expanded={expandedSections.ukDetails}
            >
              <span>Tell me more about UK tax calculations</span>
              <span style={{ fontSize: '0.75rem' }}>{expandedSections.ukDetails ? '▼' : '▶'}</span>
            </button>

            {expandedSections.ukDetails && (
              <div style={{ marginTop: '12px', fontSize: '0.9rem', color: '#475569', lineHeight: '1.7' }}>
                <p style={{ marginBottom: '12px' }}>
                  <strong>Income Tax:</strong> Calculated on taxable income after personal allowance (£12,570).
                  Tax bands are 20% (basic), 40% (higher), and 45% (additional rate).
                </p>
                <p style={{ marginBottom: '12px' }}>
                  <strong>National Insurance:</strong> Class 1 NI is 8% on earnings between £12,570 and £50,270,
                  then 2% above. Self-employed pay Class 2 (flat rate) and Class 4 (6% then 2%).
                </p>
                <p style={{ marginBottom: '12px' }}>
                  <strong>Capital Gains Tax:</strong> £3,000 annual exemption. Rates are 10%/20% for most assets,
                  18%/24% for residential property (depending on your income tax band).
                </p>
                <p style={{ fontWeight: 600, color: '#1E40AF' }}>
                  Tip: Maximize your ISA and pension allowances to reduce your taxable income and gains.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* SA Tax Liabilities Section */}
      {sa_tax && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Your South Africa Tax Liabilities</h3>

          <p style={narrativeParagraphStyle}>
            In South Africa, you'll pay <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(sa_tax.total_tax, 'ZAR')}</strong> in
            total taxes. This includes Income Tax, Capital Gains Tax (if applicable), and Dividend Withholding Tax.
          </p>

          {uk_tax && (
            <p style={narrativeParagraphStyle}>
              That's approximately <strong>{formatCurrency(sa_tax.total_tax_gbp)}</strong> at current exchange rates,
              bringing your total tax across both countries to{' '}
              <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(overall.total_tax)}</strong>.
            </p>
          )}

          {/* SA Tax Breakdown Table */}
          <table style={tableStyle}>
            <tbody>
              {sa_tax.income_tax && sa_tax.income_tax.tax_payable > 0 && (
                <tr style={tableRowStyle}>
                  <td style={tableCellStyle}>
                    <strong>Income Tax</strong>
                    {sa_tax.income_tax.tax_by_band && (
                      <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '4px' }}>
                        {sa_tax.income_tax.tax_by_band.slice(0, 2).map((band, idx) => (
                          <div key={idx}>
                            R{band.taxable_amount.toLocaleString()} @ {formatPercentage(band.rate * 100)}
                          </div>
                        ))}
                        {sa_tax.income_tax.tax_by_band.length > 2 && <div>+ {sa_tax.income_tax.tax_by_band.length - 2} more bands</div>}
                      </div>
                    )}
                  </td>
                  <td style={tableCellRightStyle}>
                    <strong>{formatCurrency(sa_tax.income_tax.tax_payable, 'ZAR')}</strong>
                  </td>
                </tr>
              )}
              {sa_tax.capital_gains_tax && sa_tax.capital_gains_tax.cgt > 0 && (
                <tr style={tableRowStyle}>
                  <td style={tableCellStyle}>
                    <strong>Capital Gains Tax</strong>
                    <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '4px' }}>
                      Inclusion rate method: {formatPercentage(40)} of gain taxable
                    </div>
                  </td>
                  <td style={tableCellRightStyle}>
                    <strong>{formatCurrency(sa_tax.capital_gains_tax.cgt, 'ZAR')}</strong>
                  </td>
                </tr>
              )}
              {sa_tax.dividend_tax && sa_tax.dividend_tax.dividend_tax_withheld > 0 && (
                <tr style={tableRowStyle}>
                  <td style={tableCellStyle}>
                    <strong>Dividend Withholding Tax</strong>
                    <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '4px' }}>
                      20% withheld at source on local dividends
                    </div>
                  </td>
                  <td style={tableCellRightStyle}>
                    <strong>{formatCurrency(sa_tax.dividend_tax.dividend_tax_withheld, 'ZAR')}</strong>
                  </td>
                </tr>
              )}
              <tr style={{ ...tableRowStyle, borderTop: '2px solid #E2E8F0' }}>
                <td style={{ ...tableCellStyle, fontWeight: 'bold', fontSize: '1rem' }}>
                  Total SA Tax
                </td>
                <td style={{ ...tableCellRightStyle, fontWeight: 'bold', fontSize: '1rem', color: '#EF4444' }}>
                  {formatCurrency(sa_tax.total_tax, 'ZAR')}
                </td>
              </tr>
            </tbody>
          </table>

          {/* Expandable SA details */}
          <div style={expandableSectionStyle}>
            <button
              onClick={() => toggleSection('saDetails')}
              style={expandTriggerStyle}
              aria-expanded={expandedSections.saDetails}
            >
              <span>Tell me more about SA tax calculations</span>
              <span style={{ fontSize: '0.75rem' }}>{expandedSections.saDetails ? '▼' : '▶'}</span>
            </button>

            {expandedSections.saDetails && (
              <div style={{ marginTop: '12px', fontSize: '0.9rem', color: '#475569', lineHeight: '1.7' }}>
                <p style={{ marginBottom: '12px' }}>
                  <strong>Income Tax:</strong> Progressive rates from 18% to 45% with age-dependent rebates.
                  Primary rebate for under 65: R17,235. Interest exemption: R23,800 (under 65).
                </p>
                <p style={{ marginBottom: '12px' }}>
                  <strong>Capital Gains Tax:</strong> Uses inclusion rate method - 40% of capital gain (after
                  R40,000 exclusion) is added to taxable income and taxed at marginal rate.
                </p>
                <p style={{ marginBottom: '12px' }}>
                  <strong>Dividend Tax:</strong> 20% withholding tax on local dividends (withheld at source).
                  Foreign dividends included in taxable income.
                </p>
                <p style={{ fontWeight: 600, color: '#1E40AF' }}>
                  Tip: Maximize your TFSA contributions (R36,000 annual limit) for completely tax-free returns.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Income Breakdown Section */}
      {income_breakdown && income_breakdown.length > 0 && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Your Income Breakdown</h3>

          <p style={narrativeParagraphStyle}>
            Your income comes from {income_breakdown.length} different sources. Understanding where your income
            comes from helps you plan tax-efficient strategies for each type.
          </p>

          {/* Income source list */}
          <div style={{ marginTop: '24px' }}>
            {income_breakdown.map((source, index) => {
              const percentage = (source.amount / overall.total_income) * 100;
              const isLargest = index === 0;

              return (
                <div
                  key={index}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '12px 16px',
                    backgroundColor: isLargest ? '#EFF6FF' : '#F8FAFC',
                    borderRadius: '8px',
                    marginBottom: '8px',
                    border: isLargest ? '2px solid #BFDBFE' : '1px solid #E2E8F0',
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600, color: '#0F172A' }}>{source.source_type}</div>
                    <div style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: '2px' }}>
                      {source.country} • {isLargest && 'Your largest source'}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontFamily: 'monospace', fontWeight: 600, color: '#0F172A' }}>
                      {formatCurrency(source.amount)}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#475569', marginTop: '2px' }}>
                      {formatPercentage(percentage)} of total
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {income_breakdown.length > 0 && (
            <p style={{ ...narrativeParagraphStyle, marginTop: '16px' }}>
              Your <strong>{income_breakdown[0].source_type}</strong> income of{' '}
              <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(income_breakdown[0].amount)}</strong> is
              your largest source, making up{' '}
              <strong>{formatPercentage((income_breakdown[0].amount / overall.total_income) * 100)}</strong> of
              your total income.
            </p>
          )}
        </div>
      )}

      {/* Tax Efficiency Score Section */}
      <div style={narrativeSectionStyle}>
        <h3 style={sectionHeadingStyle}>Your Tax Efficiency Score</h3>

        <p style={narrativeParagraphStyle}>
          Based on your use of tax allowances, reliefs, and tax-efficient accounts, your tax efficiency
          score is <strong>{efficiencyScore} out of 100</strong> - {getTaxEfficiencyMessage(efficiencyScore)}
        </p>

        <div style={efficiencyScoreContainerStyle(efficiencyScore)}>
          <div style={scoreCircleStyle(efficiencyScore)}>
            <div style={scoreValueStyle}>{efficiencyScore}</div>
            <div style={scoreMaxStyle}>/ 100</div>
          </div>

          <div style={{ flex: 1 }}>
            <p style={{ fontSize: '0.95rem', color: '#475569', lineHeight: '1.7', marginBottom: '12px' }}>
              This score reflects how well you're using:
            </p>
            <ul style={{ fontSize: '0.875rem', color: '#475569', lineHeight: '1.7', marginLeft: '20px' }}>
              <li>ISA and TFSA allowances (20%)</li>
              <li>Pension contributions (20%)</li>
              <li>Personal allowances (20%)</li>
              <li>Annual exempt amounts (20%)</li>
              <li>Tax-efficient accounts (20%)</li>
            </ul>
          </div>
        </div>

        {efficiencyScore < 80 && (
          <div style={calloutBoxStyle('tip')}>
            <p style={{ fontWeight: 600, color: '#065F46', marginBottom: '8px' }}>
              Good news: You can improve your score!
            </p>
            <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
              Follow the recommendations below to maximize your tax efficiency and potentially save
              thousands in tax each year.
            </p>
          </div>
        )}
      </div>

      {/* Actionable Insights Section */}
      {insights.length > 0 && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>What You Can Do to Reduce Your Tax</h3>

          <p style={narrativeParagraphStyle}>
            Based on your current situation, here are {insights.length} specific actions you can take
            to reduce your tax liability and improve your efficiency score:
          </p>

          {insights.map((insight, index) => (
            <div key={index} style={calloutBoxStyle(insight.type)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <p style={{ fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>
                    {index + 1}. {insight.title}
                  </p>
                  <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
                    {insight.description}
                  </p>
                </div>
                {insight.savingsPotential && (
                  <div
                    style={{
                      marginLeft: '16px',
                      padding: '8px 12px',
                      backgroundColor: 'rgba(16, 185, 129, 0.1)',
                      borderRadius: '8px',
                      textAlign: 'center',
                      minWidth: '100px',
                    }}
                  >
                    <div style={{ fontSize: '0.75rem', color: '#065F46', marginBottom: '2px' }}>
                      potential savings
                    </div>
                    <div style={{ fontWeight: 700, color: '#10B981', fontFamily: 'monospace', fontSize: '1.1rem' }}>
                      {formatCurrency(insight.savingsPotential)}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          <div style={calloutBoxStyle('info')}>
            <p style={{ fontWeight: 600, color: '#1E40AF', marginBottom: '8px' }}>
              Need help implementing these strategies?
            </p>
            <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7', marginBottom: '12px' }}>
              Tax planning can be complex, especially across two jurisdictions. Consider speaking with
              a qualified tax advisor who understands UK-SA tax treaties and dual residency rules.
            </p>
            <Button variant="outline" size="small">
              Find a Tax Advisor →
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
