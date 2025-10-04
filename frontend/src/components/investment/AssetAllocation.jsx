import React, { useState, useEffect } from 'react';
import { Button, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * AssetAllocation - Investment portfolio allocation visualization with tabbed interface
 *
 * Displays portfolio allocation across three dimensions:
 * - Asset Class (EQUITY, FIXED_INCOME, PROPERTY, COMMODITY, CASH, ALTERNATIVE)
 * - Region (UK, US, EUROPE, ASIA_PACIFIC, EMERGING_MARKETS, GLOBAL)
 * - Sector (TECHNOLOGY, HEALTHCARE, FINANCIALS, CONSUMER, ENERGY, INDUSTRIALS, etc.)
 *
 * Follows STYLEGUIDE.md narrative storytelling approach:
 * - Conversational language ("Your portfolio is allocated across...")
 * - Metrics embedded in context
 * - Visual representation with color coding
 * - Progressive disclosure
 * - Generous white space and readability
 */
export function AssetAllocation() {
  const [activeTab, setActiveTab] = useState('asset_class');
  const [allocationData, setAllocationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    loadAllocationData(activeTab);
  }, [activeTab]);

  const loadAllocationData = async (allocationType) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/v1/investments/portfolio/allocation?by=${allocationType}`,
        {
          headers: {
            Authorization: `Bearer ${authStorage.getAccessToken()}`,
          },
        }
      );

      if (!response.ok) {
        if (response.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }
        if (response.status === 404) {
          // No allocation data available
          setAllocationData(null);
          setLoading(false);
          return;
        }
        throw new Error('Failed to fetch allocation data');
      }

      const data = await response.json();
      setAllocationData(data);
    } catch (err) {
      setError('Failed to load allocation data. Please try again.');
      console.error('Error loading allocation:', err);
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

  // Color schemes for different allocation types
  const getColorForCategory = (category, index) => {
    // Asset class colors
    const assetClassColors = {
      EQUITY: '#2563EB',
      FIXED_INCOME: '#10B981',
      PROPERTY: '#8B5CF6',
      COMMODITY: '#F59E0B',
      CASH: '#6B7280',
      ALTERNATIVE: '#EF4444',
    };

    // Region colors
    const regionColors = {
      UK: '#2563EB',
      US: '#EF4444',
      EUROPE: '#8B5CF6',
      ASIA_PACIFIC: '#F59E0B',
      EMERGING_MARKETS: '#10B981',
      GLOBAL: '#6B7280',
    };

    // Sector colors - rotate through palette
    const sectorColors = [
      '#2563EB', // Blue
      '#10B981', // Green
      '#8B5CF6', // Purple
      '#F59E0B', // Orange
      '#EF4444', // Red
      '#06B6D4', // Cyan
      '#EC4899', // Pink
      '#84CC16', // Lime
      '#F97316', // Orange-red
      '#6366F1', // Indigo
      '#14B8A6', // Teal
      '#A855F7', // Violet
    ];

    if (activeTab === 'asset_class') {
      return assetClassColors[category] || sectorColors[index % sectorColors.length];
    } else if (activeTab === 'region') {
      return regionColors[category] || sectorColors[index % sectorColors.length];
    } else {
      return sectorColors[index % sectorColors.length];
    }
  };

  const getTabLabel = (tab) => {
    const labels = {
      asset_class: 'Asset Class',
      region: 'Region',
      sector: 'Sector',
    };
    return labels[tab] || tab;
  };

  const getNarrativeText = () => {
    if (!allocationData || !allocationData.allocations || allocationData.allocations.length === 0) {
      return null;
    }

    const count = allocationData.allocations.length;
    const topCategory = allocationData.allocations[0];
    const totalValue = formatCurrency(allocationData.totalValue);

    if (activeTab === 'asset_class') {
      return (
        <>
          Your portfolio is allocated across <strong>{count}</strong> asset classes with a total
          value of <strong style={{ fontFamily: 'monospace' }}>{totalValue}</strong>. Your
          largest allocation is to{' '}
          <strong>{topCategory.category.toLowerCase().replace('_', ' ')}</strong> at{' '}
          <strong>{topCategory.percentage.toFixed(1)}%</strong> of your portfolio - this helps
          diversify risk across different investment types.
        </>
      );
    } else if (activeTab === 'region') {
      return (
        <>
          Your investments span <strong>{count}</strong> geographic regions. You're most exposed
          to <strong>{topCategory.category.toLowerCase().replace('_', ' ')}</strong> markets,
          which represent <strong>{topCategory.percentage.toFixed(1)}%</strong> of your{' '}
          <strong style={{ fontFamily: 'monospace' }}>{totalValue}</strong> portfolio. Geographic
          diversification helps manage regional economic risks.
        </>
      );
    } else {
      return (
        <>
          Your portfolio is diversified across <strong>{count}</strong> industry sectors. Your
          largest sector exposure is <strong>{topCategory.category.toLowerCase()}</strong> at{' '}
          <strong>{topCategory.percentage.toFixed(1)}%</strong> of your total{' '}
          <strong style={{ fontFamily: 'monospace' }}>{totalValue}</strong> portfolio value.
          Sector diversification helps protect against industry-specific downturns.
        </>
      );
    }
  };

  const getEducationalContent = () => {
    if (activeTab === 'asset_class') {
      return (
        <div style={{ marginTop: '12px', fontSize: '0.9rem', color: '#475569', lineHeight: '1.7' }}>
          <p style={{ marginBottom: '12px' }}>
            <strong>Asset classes</strong> are broad categories of investments with similar
            characteristics. The main types are:
          </p>
          <ul style={{ marginLeft: '20px', marginBottom: '12px' }}>
            <li style={{ marginBottom: '8px' }}>
              <strong>Equity:</strong> Shares in companies - higher growth potential but more
              volatile
            </li>
            <li style={{ marginBottom: '8px' }}>
              <strong>Fixed Income:</strong> Bonds and gilts - more stable income with lower
              growth
            </li>
            <li style={{ marginBottom: '8px' }}>
              <strong>Property:</strong> Real estate investments and REITs
            </li>
            <li style={{ marginBottom: '8px' }}>
              <strong>Cash:</strong> Savings and money market funds - lowest risk and return
            </li>
            <li style={{ marginBottom: '8px' }}>
              <strong>Alternative:</strong> Commodities, hedge funds, private equity
            </li>
          </ul>
          <p style={{ fontWeight: 600, color: '#1E40AF' }}>
            Tip: A balanced portfolio typically includes a mix of assets based on your risk
            tolerance and time horizon. Younger investors often hold more equity, while those
            nearing retirement typically increase fixed income holdings.
          </p>
        </div>
      );
    } else if (activeTab === 'region') {
      return (
        <div style={{ marginTop: '12px', fontSize: '0.9rem', color: '#475569', lineHeight: '1.7' }}>
          <p style={{ marginBottom: '12px' }}>
            <strong>Geographic diversification</strong> means spreading your investments across
            different regions of the world. This helps protect your portfolio from
            country-specific risks like political instability, currency fluctuations, or regional
            economic downturns.
          </p>
          <p style={{ marginBottom: '12px' }}>
            Different regions offer different opportunities: developed markets like the UK and US
            provide stability, while emerging markets can offer higher growth potential with
            increased risk.
          </p>
          <p style={{ fontWeight: 600, color: '#1E40AF' }}>
            Tip: For UK investors, home bias (overweighting UK assets) is common but can increase
            risk. Most financial advisors recommend global diversification with no more than
            30-40% in your home market.
          </p>
        </div>
      );
    } else {
      return (
        <div style={{ marginTop: '12px', fontSize: '0.9rem', color: '#475569', lineHeight: '1.7' }}>
          <p style={{ marginBottom: '12px' }}>
            <strong>Sector allocation</strong> shows how your investments are distributed across
            different industries. Each sector performs differently based on economic cycles,
            technological changes, and market conditions.
          </p>
          <p style={{ marginBottom: '12px' }}>
            Technology and healthcare have historically shown strong growth, while utilities and
            consumer staples tend to be more defensive during downturns. Energy and materials are
            often cyclical, moving with economic cycles.
          </p>
          <p style={{ fontWeight: 600, color: '#1E40AF' }}>
            Tip: Avoid overconcentration in any single sector. If one sector represents more than
            25-30% of your portfolio, consider rebalancing to reduce sector-specific risk.
          </p>
        </div>
      );
    }
  };

  // Styles following STYLEGUIDE.md
  const containerStyle = {
    maxWidth: '1280px',
    margin: '0 auto',
    padding: '0',
  };

  const narrativeSectionStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
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

  const tabContainerStyle = {
    display: 'flex',
    borderBottom: '2px solid #E2E8F0',
    marginBottom: '32px',
    gap: '8px',
  };

  const tabButtonStyle = (isActive) => ({
    padding: '12px 24px',
    fontSize: '1rem',
    fontWeight: 500,
    color: isActive ? '#2563EB' : '#475569',
    backgroundColor: 'transparent',
    border: 'none',
    borderBottom: `3px solid ${isActive ? '#2563EB' : 'transparent'}`,
    cursor: 'pointer',
    transition: 'all 150ms ease-in-out',
    marginBottom: '-2px',
  });

  const allocationItemStyle = (index) => ({
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px 20px',
    backgroundColor: index % 2 === 0 ? '#F8FAFC' : '#FFFFFF',
    borderRadius: '8px',
    marginBottom: '8px',
    border: '1px solid #E2E8F0',
    transition: 'all 150ms ease-in-out',
  });

  const colorIndicatorStyle = (color) => ({
    width: '16px',
    height: '16px',
    borderRadius: '4px',
    backgroundColor: color,
    marginRight: '12px',
  });

  const progressBarContainerStyle = {
    width: '100%',
    height: '8px',
    backgroundColor: '#E2E8F0',
    borderRadius: '4px',
    overflow: 'hidden',
    marginTop: '16px',
  };

  const progressBarStyle = (percentage, color) => ({
    width: `${percentage}%`,
    height: '100%',
    backgroundColor: color,
    transition: 'width 300ms ease-in-out',
  });

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
    transition: 'background-color 150ms ease-in-out',
  };

  const tableCellStyle = {
    padding: '16px',
    fontSize: '0.875rem',
    color: '#0F172A',
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
      <div style={containerStyle}>
        <div style={narrativeSectionStyle}>
          <div style={{ textAlign: 'center', padding: '48px', color: '#94A3B8' }}>
            <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⏳</div>
            <p>Loading allocation data...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={containerStyle}>
        <div style={narrativeSectionStyle}>
          <Alert variant="error">
            <p style={{ fontWeight: 600 }}>Error Loading Allocation</p>
            <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
          </Alert>
          <Button
            variant="outline"
            onClick={() => loadAllocationData(activeTab)}
            style={{ marginTop: '16px' }}
          >
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  // Empty state
  if (!allocationData || !allocationData.allocations || allocationData.allocations.length === 0) {
    return (
      <div style={containerStyle}>
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Asset Allocation</h3>

          <p style={narrativeParagraphStyle}>
            You haven't added any investments yet, so we can't show your allocation breakdown.
            Once you add holdings to your portfolio, you'll see how your investments are
            distributed across asset classes, regions, and sectors.
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
              Why is asset allocation important?
            </p>
            <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
              Asset allocation is one of the most important factors in investment success. By
              diversifying across different types of investments, regions, and sectors, you can
              reduce risk while maintaining growth potential. Studies show that asset allocation
              accounts for up to 90% of long-term portfolio returns.
            </p>
          </div>

          <Button variant="primary" style={{ marginTop: '24px' }}>
            Add Your First Investment →
          </Button>
        </div>
      </div>
    );
  }

  const narrativeText = getNarrativeText();

  return (
    <div style={containerStyle}>
      <div style={narrativeSectionStyle}>
        <h3 style={sectionHeadingStyle}>Asset Allocation Analysis</h3>

        <p style={narrativeParagraphStyle}>{narrativeText}</p>

        {/* Tabs */}
        <div style={tabContainerStyle}>
          <button
            style={tabButtonStyle(activeTab === 'asset_class')}
            onClick={() => setActiveTab('asset_class')}
          >
            Asset Class
          </button>
          <button
            style={tabButtonStyle(activeTab === 'region')}
            onClick={() => setActiveTab('region')}
          >
            Region
          </button>
          <button
            style={tabButtonStyle(activeTab === 'sector')}
            onClick={() => setActiveTab('sector')}
          >
            Sector
          </button>
        </div>

        {/* Visual representation with progress bars */}
        <div style={{ marginBottom: '32px' }}>
          {allocationData.allocations.map((allocation, index) => {
            const color = getColorForCategory(allocation.category, index);
            return (
              <div key={allocation.category}>
                <div style={allocationItemStyle(index)}>
                  <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                    <div style={colorIndicatorStyle(color)} />
                    <span style={{ fontWeight: 500, color: '#0F172A', fontSize: '0.95rem' }}>
                      {allocation.category.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
                    <span
                      style={{
                        fontFamily: 'monospace',
                        color: '#475569',
                        fontSize: '0.9rem',
                        minWidth: '80px',
                        textAlign: 'right',
                      }}
                    >
                      {formatCurrencyShort(allocation.value)}
                    </span>
                    <span
                      style={{
                        fontWeight: 600,
                        color: '#0F172A',
                        fontSize: '1rem',
                        minWidth: '60px',
                        textAlign: 'right',
                      }}
                    >
                      {allocation.percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>
                <div style={progressBarContainerStyle}>
                  <div style={progressBarStyle(allocation.percentage, color)} />
                </div>
              </div>
            );
          })}
        </div>

        {/* Detailed table */}
        <div style={{ overflowX: 'auto', marginTop: '32px' }}>
          <table style={tableStyle}>
            <thead style={tableHeaderStyle}>
              <tr>
                <th style={tableHeaderCellStyle}>Category</th>
                <th style={{ ...tableHeaderCellStyle, textAlign: 'right' }}>Value</th>
                <th style={{ ...tableHeaderCellStyle, textAlign: 'right' }}>Percentage</th>
                {allocationData.allocations[0].holdingsCount !== undefined && (
                  <th style={{ ...tableHeaderCellStyle, textAlign: 'right' }}>Holdings</th>
                )}
              </tr>
            </thead>
            <tbody>
              {allocationData.allocations.map((allocation, index) => {
                const color = getColorForCategory(allocation.category, index);
                return (
                  <tr key={allocation.category} style={tableRowStyle}>
                    <td style={tableCellStyle}>
                      <div style={{ display: 'flex', alignItems: 'center' }}>
                        <div
                          style={{
                            width: '8px',
                            height: '8px',
                            borderRadius: '50%',
                            backgroundColor: color,
                            marginRight: '12px',
                          }}
                        />
                        <span style={{ fontWeight: 500 }}>
                          {allocation.category.replace(/_/g, ' ')}
                        </span>
                      </div>
                    </td>
                    <td style={{ ...tableCellStyle, textAlign: 'right', fontFamily: 'monospace' }}>
                      {formatCurrency(allocation.value)}
                    </td>
                    <td
                      style={{
                        ...tableCellStyle,
                        textAlign: 'right',
                        fontWeight: 600,
                      }}
                    >
                      {allocation.percentage.toFixed(1)}%
                    </td>
                    {allocation.holdingsCount !== undefined && (
                      <td style={{ ...tableCellStyle, textAlign: 'right' }}>
                        {allocation.holdingsCount}
                      </td>
                    )}
                  </tr>
                );
              })}
              {/* Total row */}
              <tr style={{ ...tableRowStyle, borderTop: '2px solid #E2E8F0' }}>
                <td style={{ ...tableCellStyle, fontWeight: 700 }}>Total</td>
                <td
                  style={{
                    ...tableCellStyle,
                    textAlign: 'right',
                    fontFamily: 'monospace',
                    fontWeight: 700,
                  }}
                >
                  {formatCurrency(allocationData.totalValue)}
                </td>
                <td style={{ ...tableCellStyle, textAlign: 'right', fontWeight: 700 }}>100.0%</td>
                {allocationData.allocations[0].holdingsCount !== undefined && (
                  <td style={{ ...tableCellStyle, textAlign: 'right', fontWeight: 700 }}>
                    {allocationData.allocations.reduce(
                      (sum, a) => sum + (a.holdingsCount || 0),
                      0
                    )}
                  </td>
                )}
              </tr>
            </tbody>
          </table>
        </div>

        {/* Educational expandable section */}
        <div style={expandableSectionStyle}>
          <button
            onClick={() => setExpanded(!expanded)}
            style={expandTriggerStyle}
            aria-expanded={expanded}
          >
            <span>Tell me more about {getTabLabel(activeTab).toLowerCase()} allocation</span>
            <span style={{ fontSize: '0.75rem' }}>{expanded ? '▼' : '▶'}</span>
          </button>

          {expanded && getEducationalContent()}
        </div>
      </div>
    </div>
  );
}
