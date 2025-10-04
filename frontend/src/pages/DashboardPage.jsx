import React, { useState, useEffect } from 'react';
import { Card } from 'internal-packages-ui';
import { Layout } from '../components/Layout';
import { authStorage } from '../utils/auth';
import { Button } from 'internal-packages-ui';
import { Select } from 'internal-packages-ui';
import { Alert } from 'internal-packages-ui';
import { RecommendationsWidget } from '../components/recommendations/RecommendationsWidget';

export default function DashboardPage() {
  const user = authStorage.getUser();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [baseCurrency, setBaseCurrency] = useState('GBP');
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async (currency = baseCurrency) => {
    try {
      setError(null);
      const response = await fetch(`/api/v1/dashboard/net-worth?baseCurrency=${currency}`, {
        headers: {
          'Authorization': `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }
        throw new Error('Failed to fetch dashboard data');
      }

      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleCurrencyChange = (e) => {
    const newCurrency = e.target.value;
    setBaseCurrency(newCurrency);
    setLoading(true);
    fetchDashboardData(newCurrency);
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  const formatCurrency = (amount, currency = baseCurrency) => {
    const symbols = { GBP: '£', USD: '$', EUR: '€', ZAR: 'R' };
    const symbol = symbols[currency] || currency;
    return `${symbol}${amount.toLocaleString('en-GB', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
  };

  const formatPercentage = (value) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getChangeColor = (value) => {
    if (value > 0) return '#10B981'; // success green
    if (value < 0) return '#EF4444'; // error red
    return '#475569'; // neutral
  };

  // Styles following STYLEGUIDE.md
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
  };

  const calloutStyle = {
    backgroundColor: '#EFF6FF',
    border: '1px solid #BFDBFE',
    borderLeft: '4px solid #3B82F6',
    padding: '16px',
    borderRadius: '8px',
    marginTop: '16px',
  };

  const metricGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
    marginTop: '24px',
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
  };

  const metricLabelStyle = {
    fontSize: '0.75rem',
    color: '#475569',
    marginTop: '4px',
  };

  const actionListStyle = {
    listStyle: 'decimal',
    paddingLeft: '24px',
    color: '#475569',
    lineHeight: '1.7',
  };

  const actionItemStyle = {
    marginBottom: '12px',
  };

  const linkStyle = {
    color: '#2563EB',
    textDecoration: 'none',
    fontWeight: 500,
  };

  const barStyle = (percentage, color) => ({
    height: '24px',
    backgroundColor: color,
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    paddingRight: '8px',
    color: '#FFFFFF',
    fontSize: '0.875rem',
    fontWeight: 600,
    width: `${percentage}%`,
    minWidth: percentage > 0 ? '40px' : '0',
  });

  // Loading State
  if (loading && !dashboardData) {
    return (
      <Layout showHeader={true} containerWidth="xl">
        <div style={{ padding: '48px 0' }}>
          {/* Skeleton loader */}
          <div style={{ height: '40px', backgroundColor: '#E2E8F0', borderRadius: '8px', marginBottom: '16px', width: '60%' }}></div>
          <div style={{ height: '20px', backgroundColor: '#E2E8F0', borderRadius: '8px', marginBottom: '48px', width: '40%' }}></div>

          <div style={narrativeSectionStyle}>
            <div style={{ height: '24px', backgroundColor: '#E2E8F0', borderRadius: '8px', marginBottom: '16px', width: '40%' }}></div>
            <div style={{ height: '80px', backgroundColor: '#E2E8F0', borderRadius: '8px' }}></div>
          </div>
        </div>
      </Layout>
    );
  }

  // Error State
  if (error) {
    return (
      <Layout showHeader={true} containerWidth="xl">
        <div style={{ padding: '48px 0' }}>
          <Alert variant="error">
            <p style={{ fontWeight: 600, marginBottom: '8px' }}>Unable to load your dashboard</p>
            <p>We encountered an issue loading your financial data. Please try again.</p>
            <Button onClick={handleRefresh} style={{ marginTop: '16px' }}>
              Try Again
            </Button>
          </Alert>
        </div>
      </Layout>
    );
  }

  // Empty State (no data)
  const hasData = dashboardData && (dashboardData.totalAssets > 0 || dashboardData.totalLiabilities > 0);

  if (!hasData) {
    return (
      <Layout showHeader={true} containerWidth="xl">
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, lineHeight: 1.2, color: '#0F172A', marginBottom: '16px' }}>
          Your Financial Health: Getting Started
        </h1>
        <p style={{ color: '#475569', fontSize: '1rem', lineHeight: '1.7', marginBottom: '48px' }}>
          Welcome to your financial command center. Let's build a complete picture of your wealth across the UK and South Africa.
        </p>

        {/* Welcome Section */}
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Welcome to GoalPlan, {user?.firstName}!</h3>
          <p style={paragraphStyle}>
            We're here to help you manage your finances across the UK and South Africa.
            GoalPlan gives you a clear picture of your wealth, helps you plan for the future,
            and provides guidance tailored to your unique cross-border financial situation.
          </p>
          <p style={paragraphStyle}>
            Let's start by setting up your financial information. Once you've added your
            accounts and assets, we'll show you a complete picture of your financial health
            and provide personalized recommendations to help you reach your goals.
          </p>

          <div style={calloutStyle}>
            <p style={{ fontWeight: 600, color: '#1E40AF', marginBottom: '8px' }}>
              Why GoalPlan is different
            </p>
            <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
              GoalPlan understands the complexity of managing finances in two countries. We help
              you navigate dual tax systems, understand your domicile status, and make informed
              decisions about pensions, investments, and inheritance planning across borders.
            </p>
          </div>
        </div>

        {/* Current Financial Position */}
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Your Financial Position</h3>
          <p style={paragraphStyle}>
            Right now, you're just getting started. Once you add your accounts, property, and pensions,
            this section will show you your complete net worth. You'll see how your wealth is distributed
            and get personalized recommendations to optimize your financial position.
          </p>
          <p style={paragraphStyle}>
            For now, your dashboard shows <strong style={{ fontFamily: 'monospace' }}>£0</strong> in
            tracked assets. That's normal—we need you to add your accounts first!
          </p>

          <div style={metricGridStyle}>
            <div style={compactMetricStyle}>
              <div style={metricValueStyle}>£0</div>
              <div style={metricLabelStyle}>total assets</div>
            </div>
            <div style={compactMetricStyle}>
              <div style={metricValueStyle}>£0</div>
              <div style={metricLabelStyle}>pensions</div>
            </div>
            <div style={compactMetricStyle}>
              <div style={metricValueStyle}>£0</div>
              <div style={metricLabelStyle}>investments</div>
            </div>
            <div style={compactMetricStyle}>
              <div style={metricValueStyle}>£0</div>
              <div style={metricLabelStyle}>savings</div>
            </div>
          </div>
        </div>

        {/* What to Do Next */}
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>What You Should Do Next</h3>
          <p style={paragraphStyle}>
            To get the most out of GoalPlan, we recommend completing these steps in order.
            Each step helps us understand your situation better and provide more accurate
            guidance.
          </p>

          <ol style={actionListStyle}>
            <li style={actionItemStyle}>
              <strong>Add your user information</strong> - Tell us about your tax residency
              status and domicile. This is crucial for accurate tax planning across the UK
              and South Africa.
            </li>
            <li style={actionItemStyle}>
              <strong>Set up your savings accounts</strong> - Add your bank accounts, ISAs,
              and TFSAs. We'll track your balances and alert you when you're approaching
              contribution limits.
            </li>
            <li style={actionItemStyle}>
              <strong>Add your pensions</strong> - Include UK pensions, South African retirement
              funds, and any QROPS. We'll help you understand your projected retirement income.
            </li>
            <li style={actionItemStyle}>
              <strong>Review your protection</strong> - Add life insurance and critical illness
              cover. We'll help ensure you and your family are properly protected.
            </li>
          </ol>

          <p style={{ ...paragraphStyle, marginTop: '24px' }}>
            Ready to begin?{' '}
            <a href="/user-info" style={linkStyle}>
              Start by adding your user information →
            </a>
          </p>
        </div>
      </Layout>
    );
  }

  // Dashboard with data
  const { netWorth, totalAssets, totalLiabilities, breakdownByCountry, breakdownByAssetClass,
          breakdownByCurrency, trendData, changes, lastUpdated } = dashboardData;

  // Calculate change descriptions
  const getChangeDescription = (change) => {
    if (!change || change.amount === 0) return "stayed the same";
    const action = change.amount > 0 ? "increased" : "decreased";
    return `${action} by ${formatCurrency(Math.abs(change.amount))}`;
  };

  return (
    <Layout showHeader={true} containerWidth="xl">
      {/* Header with currency selector */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 700, lineHeight: 1.2, color: '#0F172A', marginBottom: '8px' }}>
            Your Financial Health: {netWorth >= 0 ? 'Strong' : 'Building Up'}
          </h1>
          <p style={{ color: '#475569', fontSize: '0.875rem' }}>
            Last updated: {formatDate(lastUpdated)}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <Select
            value={baseCurrency}
            onChange={handleCurrencyChange}
            options={[
              { value: 'GBP', label: '£ GBP' },
              { value: 'USD', label: '$ USD' },
              { value: 'EUR', label: '€ EUR' },
              { value: 'ZAR', label: 'R ZAR' },
            ]}
            className="w-32"
          />
          <Button
            onClick={handleRefresh}
            disabled={refreshing}
            variant="outline"
          >
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>
      </div>

      {/* Net Worth Summary */}
      <div style={narrativeSectionStyle}>
        <h3 style={sectionHeadingStyle}>Your Financial Position</h3>
        <p style={paragraphStyle}>
          You're worth <strong style={{ fontFamily: 'monospace', fontSize: '1.1rem' }}>{formatCurrency(netWorth)}</strong> after debts.
          {changes?.month && (
            <span> That's <strong style={{ color: getChangeColor(changes.month.amount) }}>
              {getChangeDescription(changes.month)}
            </strong> since last month{changes.month.amount > 0 ? ' - great progress!' : '.'}</span>
          )}
        </p>
        <p style={paragraphStyle}>
          Your wealth comes from <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(totalAssets)}</strong> in assets,
          with <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(totalLiabilities)}</strong> in liabilities.
        </p>

        {/* Quick metrics */}
        <div style={metricGridStyle}>
          <div style={compactMetricStyle}>
            <div style={metricValueStyle}>{formatCurrency(netWorth)}</div>
            <div style={metricLabelStyle}>net worth</div>
          </div>
          <div style={compactMetricStyle}>
            <div style={metricValueStyle}>{formatCurrency(totalAssets)}</div>
            <div style={metricLabelStyle}>total assets</div>
          </div>
          <div style={compactMetricStyle}>
            <div style={metricValueStyle}>{formatCurrency(totalLiabilities)}</div>
            <div style={metricLabelStyle}>total liabilities</div>
          </div>
          {changes?.year && (
            <div style={compactMetricStyle}>
              <div style={{ ...metricValueStyle, color: getChangeColor(changes.year.amount) }}>
                {formatPercentage(changes.year.percentage)}
              </div>
              <div style={metricLabelStyle}>change this year</div>
            </div>
          )}
        </div>
      </div>

      {/* Recommended Actions Widget */}
      <RecommendationsWidget />

      {/* Changes Over Time */}
      {changes && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>How Your Wealth Has Changed</h3>
          <p style={paragraphStyle}>
            Here's how your net worth has evolved over different time periods:
          </p>

          <div style={metricGridStyle}>
            {changes.day && (
              <div style={compactMetricStyle}>
                <div style={{ ...metricValueStyle, color: getChangeColor(changes.day.amount), fontSize: '1.2rem' }}>
                  {formatCurrency(changes.day.amount)}
                </div>
                <div style={metricLabelStyle}>change today ({formatPercentage(changes.day.percentage)})</div>
              </div>
            )}
            {changes.month && (
              <div style={compactMetricStyle}>
                <div style={{ ...metricValueStyle, color: getChangeColor(changes.month.amount), fontSize: '1.2rem' }}>
                  {formatCurrency(changes.month.amount)}
                </div>
                <div style={metricLabelStyle}>change this month ({formatPercentage(changes.month.percentage)})</div>
              </div>
            )}
            {changes.year && (
              <div style={compactMetricStyle}>
                <div style={{ ...metricValueStyle, color: getChangeColor(changes.year.amount), fontSize: '1.2rem' }}>
                  {formatCurrency(changes.year.amount)}
                </div>
                <div style={metricLabelStyle}>change this year ({formatPercentage(changes.year.percentage)})</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Net Worth Trend */}
      {trendData && trendData.length > 0 && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Your Net Worth Trend</h3>
          <p style={paragraphStyle}>
            Here's how your net worth has changed over the last 12 months:
          </p>

          <div style={{ marginTop: '24px', padding: '16px', backgroundColor: '#F8FAFC', borderRadius: '8px' }}>
            {/* Simple bar chart */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {trendData.slice(-12).map((point, index) => {
                const maxValue = Math.max(...trendData.map(p => p.netWorth));
                const percentage = (point.netWorth / maxValue) * 100;
                const date = new Date(point.date);
                const monthName = date.toLocaleDateString('en-GB', { month: 'short', year: '2-digit' });

                return (
                  <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ width: '60px', fontSize: '0.75rem', color: '#475569', textAlign: 'right' }}>
                      {monthName}
                    </div>
                    <div style={{ flex: 1, backgroundColor: '#E2E8F0', borderRadius: '4px', height: '24px', position: 'relative' }}>
                      <div style={barStyle(percentage, '#2563EB')}>
                        {formatCurrency(point.netWorth)}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Breakdown by Country */}
      {breakdownByCountry && breakdownByCountry.length > 0 && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Where Your Wealth Is Located</h3>
          <p style={paragraphStyle}>
            Your assets are spread across different countries. Here's the breakdown:
          </p>

          <div style={{ marginTop: '24px' }}>
            {breakdownByCountry.map((item, index) => (
              <div key={index} style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ color: '#475569', fontWeight: 500 }}>{item.country}</span>
                  <span style={{ color: '#0F172A', fontWeight: 600, fontFamily: 'monospace' }}>
                    {formatCurrency(item.amount)} ({item.percentage.toFixed(1)}%)
                  </span>
                </div>
                <div style={{ backgroundColor: '#E2E8F0', borderRadius: '4px', height: '12px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${item.percentage}%`,
                    height: '100%',
                    backgroundColor: '#2563EB',
                    borderRadius: '4px',
                  }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Breakdown by Asset Class */}
      {breakdownByAssetClass && breakdownByAssetClass.length > 0 && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>What You Own</h3>
          <p style={paragraphStyle}>
            Your wealth is held in different types of assets. Here's how it breaks down:
          </p>

          <div style={{ marginTop: '24px' }}>
            {breakdownByAssetClass.map((item, index) => {
              // Color coding for different asset classes
              const colors = {
                'Cash': '#10B981',
                'Investments': '#3B82F6',
                'Property': '#F59E0B',
                'Pensions': '#8B5CF6',
                'Protection': '#EC4899',
                'Other': '#6B7280',
              };
              const color = colors[item.assetClass] || '#6B7280';

              return (
                <div key={index} style={{ marginBottom: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ color: '#475569', fontWeight: 500 }}>{item.assetClass}</span>
                    <span style={{ color: '#0F172A', fontWeight: 600, fontFamily: 'monospace' }}>
                      {formatCurrency(item.amount)} ({item.percentage.toFixed(1)}%)
                    </span>
                  </div>
                  <div style={{ backgroundColor: '#E2E8F0', borderRadius: '4px', height: '12px', overflow: 'hidden' }}>
                    <div style={{
                      width: `${item.percentage}%`,
                      height: '100%',
                      backgroundColor: color,
                      borderRadius: '4px',
                    }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Breakdown by Currency */}
      {breakdownByCurrency && breakdownByCurrency.length > 0 && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Your Currency Exposure</h3>
          <p style={paragraphStyle}>
            Your assets are held in different currencies. Here's your currency exposure:
          </p>

          <div style={{ marginTop: '24px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #E2E8F0' }}>
                  <th style={{ padding: '12px', textAlign: 'left', color: '#475569', fontWeight: 600, fontSize: '0.875rem' }}>
                    Currency
                  </th>
                  <th style={{ padding: '12px', textAlign: 'right', color: '#475569', fontWeight: 600, fontSize: '0.875rem' }}>
                    Amount
                  </th>
                  <th style={{ padding: '12px', textAlign: 'right', color: '#475569', fontWeight: 600, fontSize: '0.875rem' }}>
                    Percentage
                  </th>
                </tr>
              </thead>
              <tbody>
                {breakdownByCurrency.map((item, index) => (
                  <tr key={index} style={{ borderBottom: '1px solid #F1F5F9' }}>
                    <td style={{ padding: '12px', color: '#0F172A', fontWeight: 500 }}>
                      {item.currency}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right', fontFamily: 'monospace', color: '#0F172A' }}>
                      {formatCurrency(item.amount, item.currency)}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right', color: '#475569' }}>
                      {item.percentage.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* What's Next */}
      <div style={narrativeSectionStyle}>
        <h3 style={sectionHeadingStyle}>What You Should Do Next</h3>
        <p style={paragraphStyle}>
          Now that you have a clear picture of your finances, here are some recommendations to help you optimize your wealth:
        </p>

        <div style={{ ...calloutStyle, backgroundColor: '#F0FDF4', borderLeft: '4px solid #10B981' }}>
          <p style={{ fontWeight: 600, color: '#065F46', marginBottom: '8px' }}>
            Keep your data up to date
          </p>
          <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
            Update your accounts regularly to ensure your net worth calculation stays accurate.
            We recommend reviewing your dashboard at least once a month to track your progress.
          </p>
        </div>
      </div>
    </Layout>
  );
}
