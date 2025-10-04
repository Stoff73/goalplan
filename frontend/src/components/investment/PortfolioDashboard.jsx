import React, { useState, useEffect } from 'react';
import { Card, Button, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * PortfolioDashboard - Investment portfolio overview with narrative storytelling
 *
 * Displays comprehensive portfolio summary:
 * - Total portfolio value with context
 * - Unrealized gains/losses with color coding
 * - Number of holdings and accounts
 * - YTD dividend income
 * - Asset allocation chart
 * - Top 10 holdings table
 * - Performance overview
 *
 * Follows STYLEGUIDE.md narrative storytelling approach:
 * - Conversational language ("Your portfolio is worth...")
 * - Metrics embedded in sentences
 * - 2-3 sentence paragraphs maximum
 * - Progressive disclosure
 * - Generous white space and readability
 */
export function PortfolioDashboard() {
  const [portfolioData, setPortfolioData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    loadPortfolioData();
  }, []);

  const loadPortfolioData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/investments/portfolio/summary', {
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
          // No portfolio exists yet
          setPortfolioData(null);
          setLoading(false);
          return;
        }
        throw new Error('Failed to fetch portfolio data');
      }

      const data = await response.json();
      setPortfolioData(data);
    } catch (err) {
      setError('Failed to load portfolio data. Please try again.');
      console.error('Error loading portfolio:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount, currency = 'GBP') => {
    if (amount === null || amount === undefined) return '£0';
    const symbol = currency === 'GBP' ? '£' : currency === 'ZAR' ? 'R' : currency;
    return `${symbol}${amount.toLocaleString('en-GB', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const formatCurrencyShort = (amount, currency = 'GBP') => {
    if (amount === null || amount === undefined) return '£0';
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
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
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
    textTransform: 'lowercase',
  };

  const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    marginTop: '24px',
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
    padding: '16px',
    fontSize: '0.875rem',
    color: '#0F172A',
  };

  const calloutBoxStyle = {
    backgroundColor: '#DBEAFE',
    border: '1px solid #BFDBFE',
    borderLeft: '4px solid #3B82F6',
    padding: '16px',
    borderRadius: '8px',
    marginTop: '24px',
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

  // Loading state
  if (loading) {
    return (
      <div style={dashboardContainerStyle}>
        <div style={narrativeSectionStyle}>
          <div style={{ textAlign: 'center', padding: '48px', color: '#94A3B8' }}>
            <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⏳</div>
            <p>Loading your portfolio...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={dashboardContainerStyle}>
        <h1 style={pageHeadingStyle}>Your Investment Portfolio</h1>
        <div style={narrativeSectionStyle}>
          <Alert variant="error">
            <p style={{ fontWeight: 600 }}>Error Loading Portfolio</p>
            <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
          </Alert>
          <Button
            variant="outline"
            onClick={loadPortfolioData}
            style={{ marginTop: '16px' }}
          >
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  // Empty state - no portfolio
  if (!portfolioData || portfolioData.totalAccounts === 0) {
    return (
      <div style={dashboardContainerStyle}>
        <h1 style={pageHeadingStyle}>Your Investment Portfolio</h1>
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Start Building Your Portfolio</h3>

          <p style={narrativeParagraphStyle}>
            You haven't added any investment accounts yet. Track your stocks, funds, ISAs, and
            other investments all in one place to monitor performance and manage tax efficiently.
          </p>

          <div style={calloutBoxStyle}>
            <p style={{ fontWeight: 600, color: '#1E40AF', marginBottom: '8px' }}>
              Why track your investments?
            </p>
            <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
              Understanding your total portfolio value, asset allocation, and performance helps
              you make informed decisions. Plus, tracking cost basis and gains is essential for
              accurate tax reporting in both the UK and South Africa.
            </p>
          </div>

          <Button variant="primary" style={{ marginTop: '24px' }}>
            Add Your First Investment Account →
          </Button>
        </div>
      </div>
    );
  }

  // Main dashboard view with data
  // Safety check: ensure portfolioData exists before destructuring
  if (!portfolioData) {
    return (
      <div style={dashboardContainerStyle}>
        <Alert variant="info">
          No portfolio data available. Start by adding your first investment account.
        </Alert>
      </div>
    );
  }

  const {
    totalValue = { gbp: 0, zar: 0 },
    totalUnrealizedGain = 0,
    totalUnrealizedGainPercentage = 0,
    totalAccounts = 0,
    totalHoldings = 0,
    ytdDividendIncome = 0,
    assetAllocation = [],
    topHoldings = [],
    performanceSummary = {},
  } = portfolioData;

  const gainColor = totalUnrealizedGain >= 0 ? '#10B981' : '#EF4444';
  const gainText = totalUnrealizedGain >= 0 ? 'grown' : 'decreased';

  return (
    <div style={dashboardContainerStyle}>
      <h1 style={pageHeadingStyle}>Your Investment Portfolio: {totalUnrealizedGain >= 0 ? 'Growing Strong' : 'Needs Attention'}</h1>

      {/* Portfolio Summary Section */}
      <div style={narrativeSectionStyle}>
        <h3 style={sectionHeadingStyle}>Your Portfolio Position</h3>

        <p style={narrativeParagraphStyle}>
          Your portfolio is currently worth <strong style={{ fontFamily: 'monospace' }}>
            {formatCurrency(totalValue.gbp)}
          </strong>. Since you purchased your investments, your portfolio has{' '}
          <strong style={{ color: gainColor }}>
            {gainText} by {formatCurrency(Math.abs(totalUnrealizedGain))}
          </strong> ({formatPercentage(totalUnrealizedGainPercentage)}) - {totalUnrealizedGain >= 0 ? 'great work!' : 'let\'s review your strategy.'}
        </p>

        <p style={narrativeParagraphStyle}>
          You're tracking <strong>{totalHoldings}</strong> holdings across{' '}
          <strong>{totalAccounts}</strong> investment accounts.
          {ytdDividendIncome > 0 && (
            <> Your investments have generated{' '}
              <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
                {formatCurrency(ytdDividendIncome)}
              </strong> in dividend income this year.
            </>
          )}
        </p>

        {/* Metric Grid */}
        <div style={metricGridStyle}>
          <div style={compactMetricStyle}>
            <div style={metricValueStyle}>{formatCurrencyShort(totalValue.gbp)}</div>
            <div style={metricLabelStyle}>total value</div>
          </div>
          <div style={compactMetricStyle}>
            <div style={{ ...metricValueStyle, color: gainColor }}>
              {formatCurrencyShort(Math.abs(totalUnrealizedGain))}
            </div>
            <div style={metricLabelStyle}>unrealized {totalUnrealizedGain >= 0 ? 'gains' : 'losses'}</div>
          </div>
          <div style={compactMetricStyle}>
            <div style={metricValueStyle}>{totalHoldings}</div>
            <div style={metricLabelStyle}>holdings</div>
          </div>
          <div style={compactMetricStyle}>
            <div style={metricValueStyle}>{totalAccounts}</div>
            <div style={metricLabelStyle}>accounts</div>
          </div>
        </div>

        <Button variant="outline" style={{ marginTop: '16px' }}>
          View Detailed Performance →
        </Button>
      </div>

      {/* Asset Allocation Section */}
      {assetAllocation && assetAllocation.length > 0 && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Your Asset Allocation</h3>

          <p style={narrativeParagraphStyle}>
            Your portfolio is diversified across different asset classes. Here's how your
            investments are distributed:
          </p>

          {/* Asset Allocation List (placeholder for chart) */}
          <div style={{ marginTop: '24px' }}>
            {assetAllocation.map((asset, index) => (
              <div
                key={index}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 16px',
                  backgroundColor: index % 2 === 0 ? '#F8FAFC' : '#FFFFFF',
                  borderRadius: '4px',
                  marginBottom: '8px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div
                    style={{
                      width: '12px',
                      height: '12px',
                      borderRadius: '50%',
                      backgroundColor: ['#2563EB', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'][index % 5],
                    }}
                  />
                  <span style={{ fontWeight: 500, color: '#0F172A' }}>{asset.assetClass}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <span style={{ fontFamily: 'monospace', color: '#475569' }}>
                    {formatCurrencyShort(asset.value)}
                  </span>
                  <span style={{ fontWeight: 600, color: '#0F172A', minWidth: '60px', textAlign: 'right' }}>
                    {asset.percentage.toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Educational callout */}
          <div style={expandableSectionStyle}>
            <button
              onClick={() => setExpanded(!expanded)}
              style={expandTriggerStyle}
              aria-expanded={expanded}
            >
              <span>Tell me more about asset allocation</span>
              <span style={{ fontSize: '0.75rem' }}>{expanded ? '▼' : '▶'}</span>
            </button>

            {expanded && (
              <div style={{ marginTop: '12px', fontSize: '0.9rem', color: '#475569', lineHeight: '1.7' }}>
                <p style={{ marginBottom: '12px' }}>
                  Asset allocation is how you divide your portfolio across different investment types
                  (stocks, bonds, property, etc.). It's one of the most important factors in
                  long-term investment success.
                </p>
                <p style={{ marginBottom: '12px' }}>
                  A diversified portfolio helps manage risk - when one asset class performs poorly,
                  others may perform well, smoothing out your overall returns.
                </p>
                <p style={{ fontWeight: 600, color: '#1E40AF' }}>
                  Tip: Most financial advisors recommend reviewing your allocation annually
                  and rebalancing if any asset class has drifted more than 5% from your target.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Top Holdings Section */}
      {topHoldings && topHoldings.length > 0 && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Your Top Holdings</h3>

          <p style={narrativeParagraphStyle}>
            Here are your largest holdings by value. Keep an eye on concentration risk -
            no single holding should typically represent more than 10% of your portfolio.
          </p>

          <div style={{ overflowX: 'auto' }}>
            <table style={tableStyle}>
              <thead style={tableHeaderStyle}>
                <tr>
                  <th style={tableHeaderCellStyle}>Ticker</th>
                  <th style={tableHeaderCellStyle}>Name</th>
                  <th style={{ ...tableHeaderCellStyle, textAlign: 'right' }}>Value</th>
                  <th style={{ ...tableHeaderCellStyle, textAlign: 'right' }}>Gain/Loss</th>
                  <th style={{ ...tableHeaderCellStyle, textAlign: 'right' }}>% of Portfolio</th>
                </tr>
              </thead>
              <tbody>
                {topHoldings.slice(0, 10).map((holding, index) => {
                  const holdingGainColor = holding.unrealizedGain >= 0 ? '#10B981' : '#EF4444';
                  return (
                    <tr key={index} style={tableRowStyle}>
                      <td style={{ ...tableCellStyle, fontWeight: 600, fontFamily: 'monospace' }}>
                        {holding.ticker}
                      </td>
                      <td style={tableCellStyle}>{holding.name}</td>
                      <td style={{ ...tableCellStyle, textAlign: 'right', fontFamily: 'monospace' }}>
                        {formatCurrency(holding.currentValue)}
                      </td>
                      <td
                        style={{
                          ...tableCellStyle,
                          textAlign: 'right',
                          fontFamily: 'monospace',
                          color: holdingGainColor,
                          fontWeight: 500,
                        }}
                      >
                        {holding.unrealizedGain < 0 ? '-' : ''}{formatCurrency(Math.abs(holding.unrealizedGain))} ({formatPercentage(holding.unrealizedGainPercentage)})
                      </td>
                      <td
                        style={{
                          ...tableCellStyle,
                          textAlign: 'right',
                          fontWeight: 600,
                        }}
                      >
                        {holding.portfolioPercentage.toFixed(1)}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <Button variant="outline" style={{ marginTop: '24px' }}>
            View All Holdings →
          </Button>
        </div>
      )}

      {/* Performance Overview Section */}
      {performanceSummary && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Performance Overview</h3>

          <p style={narrativeParagraphStyle}>
            {performanceSummary.timeWeightedReturn >= 0 ? (
              <>
                Your portfolio has returned{' '}
                <strong style={{ color: '#10B981' }}>
                  {formatPercentage(performanceSummary.timeWeightedReturn)}
                </strong>{' '}
                over the tracked period - solid performance!
              </>
            ) : (
              <>
                Your portfolio has returned{' '}
                <strong style={{ color: '#EF4444' }}>
                  {formatPercentage(performanceSummary.timeWeightedReturn)}
                </strong>{' '}
                over the tracked period. Markets can be volatile in the short term, but long-term
                investing typically smooths out these fluctuations.
              </>
            )}
          </p>

          {performanceSummary.benchmarkComparison && (
            <p style={narrativeParagraphStyle}>
              Compared to the benchmark, your portfolio has{' '}
              {performanceSummary.benchmarkComparison.outperformance >= 0 ? 'outperformed' : 'underperformed'} by{' '}
              <strong style={{
                color: performanceSummary.benchmarkComparison.outperformance >= 0 ? '#10B981' : '#EF4444'
              }}>
                {formatPercentage(Math.abs(performanceSummary.benchmarkComparison.outperformance))}
              </strong>.
            </p>
          )}

          <Button variant="primary" style={{ marginTop: '24px' }}>
            View Detailed Performance Analysis →
          </Button>
        </div>
      )}
    </div>
  );
}
