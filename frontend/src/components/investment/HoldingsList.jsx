import React, { useState, useEffect } from 'react';
import { Button, Card, Alert, Select } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';
import { AddHoldingForm } from './AddHoldingForm';
import { SellHoldingModal } from './SellHoldingModal';
import { UpdatePriceModal } from './UpdatePriceModal';

/**
 * HoldingsList - Investment holdings list with filtering and management
 *
 * Features:
 * - Display holdings in sortable, filterable table
 * - Filter by account, asset class, region
 * - Color coding for gains (green) and losses (red)
 * - Badge display for tax-advantaged investments (ISA, VCT, EIS, SEIS)
 * - Add holding form
 * - Sell and update price actions
 * - Loading, error, and empty states
 *
 * Follows STYLEGUIDE.md narrative storytelling approach
 */
export function HoldingsList() {
  const [holdings, setHoldings] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Filtering state
  const [filterAccount, setFilterAccount] = useState('all');
  const [filterAssetClass, setFilterAssetClass] = useState('all');
  const [filterRegion, setFilterRegion] = useState('all');

  // Sorting state
  const [sortColumn, setSortColumn] = useState('currentValue');
  const [sortDirection, setSortDirection] = useState('desc');

  // Modal state
  const [showAddForm, setShowAddForm] = useState(false);
  const [showSellModal, setShowSellModal] = useState(false);
  const [showUpdatePriceModal, setShowUpdatePriceModal] = useState(false);
  const [selectedHolding, setSelectedHolding] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load holdings and accounts in parallel
      const [holdingsResponse, accountsResponse] = await Promise.all([
        fetch('/api/v1/investments/holdings', {
          headers: {
            Authorization: `Bearer ${authStorage.getAccessToken()}`,
          },
        }),
        fetch('/api/v1/investments/accounts', {
          headers: {
            Authorization: `Bearer ${authStorage.getAccessToken()}`,
          },
        }),
      ]);

      if (!holdingsResponse.ok || !accountsResponse.ok) {
        if (holdingsResponse.status === 401 || accountsResponse.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }
        throw new Error('Failed to fetch holdings data');
      }

      const holdingsData = await holdingsResponse.json();
      const accountsData = await accountsResponse.json();

      setHoldings(holdingsData.holdings || []);
      setAccounts(accountsData.accounts || []);
    } catch (err) {
      setError('Failed to load holdings. Please try again.');
      console.error('Error loading holdings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddHolding = async (holdingData) => {
    try {
      const response = await fetch('/api/v1/investments/holdings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify(holdingData),
      });

      if (!response.ok) {
        throw new Error('Failed to add holding');
      }

      setSuccessMessage('Holding added successfully!');
      setShowAddForm(false);
      await loadData();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      throw new Error('Failed to add holding. Please try again.');
    }
  };

  const handleSellHolding = async (holdingId, sellData) => {
    try {
      const response = await fetch(`/api/v1/investments/holdings/${holdingId}/sell`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify(sellData),
      });

      if (!response.ok) {
        throw new Error('Failed to sell holding');
      }

      setSuccessMessage('Holding sold successfully!');
      setShowSellModal(false);
      setSelectedHolding(null);
      await loadData();

      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      throw new Error('Failed to sell holding. Please try again.');
    }
  };

  const handleUpdatePrice = async (holdingId, newPrice) => {
    try {
      const response = await fetch(`/api/v1/investments/holdings/${holdingId}/price`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({ currentPrice: newPrice }),
      });

      if (!response.ok) {
        throw new Error('Failed to update price');
      }

      setSuccessMessage('Price updated successfully!');
      setShowUpdatePriceModal(false);
      setSelectedHolding(null);
      await loadData();

      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      throw new Error('Failed to update price. Please try again.');
    }
  };

  const handleSort = (column) => {
    if (sortColumn === column) {
      // Toggle direction if same column
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // Set new column with default desc direction
      setSortColumn(column);
      setSortDirection('desc');
    }
  };

  // Filter holdings
  const filteredHoldings = holdings.filter((holding) => {
    if (filterAccount !== 'all' && holding.accountId !== filterAccount) return false;
    if (filterAssetClass !== 'all' && holding.assetClass !== filterAssetClass) return false;
    if (filterRegion !== 'all' && holding.region !== filterRegion) return false;
    return true;
  });

  // Sort holdings
  const sortedHoldings = [...filteredHoldings].sort((a, b) => {
    let aValue = a[sortColumn];
    let bValue = b[sortColumn];

    // Handle different data types
    if (typeof aValue === 'string') {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }

    if (sortDirection === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  // Get unique values for filters
  const assetClasses = [...new Set(holdings.map((h) => h.assetClass))];
  const regions = [...new Set(holdings.map((h) => h.region))];

  const formatCurrency = (amount, currency = 'GBP') => {
    if (amount === null || amount === undefined) return '£0.00';
    const symbol = currency === 'GBP' ? '£' : currency === 'ZAR' ? 'R' : currency;
    return `${symbol}${amount.toLocaleString('en-GB', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const formatPercentage = (value) => {
    if (value === null || value === undefined) return '0.00%';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getTaxBadge = (accountType) => {
    const badges = {
      STOCKS_ISA: { text: 'ISA', color: '#10B981' },
      VCT: { text: 'VCT', color: '#8B5CF6' },
      EIS: { text: 'EIS', color: '#3B82F6' },
      SEIS: { text: 'SEIS', color: '#F59E0B' },
    };
    return badges[accountType] || null;
  };

  // Styles following STYLEGUIDE.md
  const containerStyle = {
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

  const narrativeParagraphStyle = {
    color: '#475569',
    marginBottom: '24px',
    lineHeight: '1.7',
    fontSize: '1rem',
  };

  const filterBarStyle = {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '16px',
    marginBottom: '24px',
    padding: '24px',
    backgroundColor: '#F8FAFC',
    borderRadius: '12px',
    border: '1px solid #E2E8F0',
  };

  const filterGroupStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    flex: '1',
    minWidth: '200px',
  };

  const filterLabelStyle = {
    fontSize: '0.875rem',
    fontWeight: 600,
    color: '#475569',
  };

  const tableContainerStyle = {
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    overflowX: 'auto',
  };

  const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
  };

  const tableHeaderStyle = {
    backgroundColor: '#F8FAFC',
    borderBottom: '2px solid #E2E8F0',
  };

  const tableHeaderCellStyle = {
    padding: '16px',
    textAlign: 'left',
    fontSize: '0.875rem',
    fontWeight: 600,
    color: '#475569',
    cursor: 'pointer',
    userSelect: 'none',
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

  const badgeStyle = (color) => ({
    display: 'inline-block',
    padding: '2px 8px',
    fontSize: '0.75rem',
    fontWeight: 600,
    color: '#FFFFFF',
    backgroundColor: color,
    borderRadius: '4px',
    marginLeft: '8px',
  });

  const actionButtonStyle = {
    padding: '6px 12px',
    fontSize: '0.75rem',
    marginRight: '8px',
  };

  // Loading state
  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={{ textAlign: 'center', padding: '48px', color: '#94A3B8' }}>
          <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⏳</div>
          <p>Loading your holdings...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={containerStyle}>
        <h1 style={pageHeadingStyle}>Your Investment Holdings</h1>
        <Alert variant="error">
          <p style={{ fontWeight: 600 }}>Error Loading Holdings</p>
          <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
        </Alert>
        <Button variant="outline" onClick={loadData} style={{ marginTop: '16px' }}>
          Try Again
        </Button>
      </div>
    );
  }

  // Empty state
  if (holdings.length === 0) {
    return (
      <div style={containerStyle}>
        <h1 style={pageHeadingStyle}>Your Investment Holdings</h1>

        <p style={narrativeParagraphStyle}>
          You haven't added any holdings yet. Start tracking your investments to monitor
          performance, calculate gains, and manage tax efficiently.
        </p>

        <Button variant="primary" onClick={() => setShowAddForm(true)}>
          Add Your First Holding →
        </Button>

        {showAddForm && (
          <AddHoldingForm
            accounts={accounts}
            onSubmit={handleAddHolding}
            onCancel={() => setShowAddForm(false)}
          />
        )}
      </div>
    );
  }

  // Main holdings list view
  return (
    <div style={containerStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h1 style={pageHeadingStyle}>Your Investment Holdings</h1>
        <Button variant="primary" onClick={() => setShowAddForm(true)}>
          Add Holding
        </Button>
      </div>

      <p style={narrativeParagraphStyle}>
        You have <strong>{holdings.length}</strong> holdings worth{' '}
        <strong style={{ fontFamily: 'monospace' }}>
          {formatCurrency(holdings.reduce((sum, h) => sum + (h.currentValue || 0), 0))}
        </strong>. Use the filters below to find specific investments.
      </p>

      {successMessage && (
        <Alert variant="success" style={{ marginBottom: '24px' }}>
          {successMessage}
        </Alert>
      )}

      {/* Filter Bar */}
      <div style={filterBarStyle}>
        <div style={filterGroupStyle}>
          <label style={filterLabelStyle}>Account</label>
          <Select
            value={filterAccount}
            onChange={(e) => setFilterAccount(e.target.value)}
          >
            <option value="all">All Accounts</option>
            {accounts.map((account) => (
              <option key={account.id} value={account.id}>
                {account.provider} - {account.accountType}
              </option>
            ))}
          </Select>
        </div>

        <div style={filterGroupStyle}>
          <label style={filterLabelStyle}>Asset Class</label>
          <Select
            value={filterAssetClass}
            onChange={(e) => setFilterAssetClass(e.target.value)}
          >
            <option value="all">All Asset Classes</option>
            {assetClasses.map((assetClass) => (
              <option key={assetClass} value={assetClass}>
                {assetClass}
              </option>
            ))}
          </Select>
        </div>

        <div style={filterGroupStyle}>
          <label style={filterLabelStyle}>Region</label>
          <Select
            value={filterRegion}
            onChange={(e) => setFilterRegion(e.target.value)}
          >
            <option value="all">All Regions</option>
            {regions.map((region) => (
              <option key={region} value={region}>
                {region}
              </option>
            ))}
          </Select>
        </div>
      </div>

      {/* Holdings Table */}
      <div style={tableContainerStyle}>
        <table style={tableStyle}>
          <thead style={tableHeaderStyle}>
            <tr>
              <th
                style={tableHeaderCellStyle}
                onClick={() => handleSort('ticker')}
              >
                Ticker {sortColumn === 'ticker' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th
                style={tableHeaderCellStyle}
                onClick={() => handleSort('name')}
              >
                Name {sortColumn === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th
                style={{ ...tableHeaderCellStyle, textAlign: 'right' }}
                onClick={() => handleSort('quantity')}
              >
                Quantity {sortColumn === 'quantity' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th
                style={{ ...tableHeaderCellStyle, textAlign: 'right' }}
                onClick={() => handleSort('purchasePrice')}
              >
                Purchase Price {sortColumn === 'purchasePrice' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th
                style={{ ...tableHeaderCellStyle, textAlign: 'right' }}
                onClick={() => handleSort('currentPrice')}
              >
                Current Price {sortColumn === 'currentPrice' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th
                style={{ ...tableHeaderCellStyle, textAlign: 'right' }}
                onClick={() => handleSort('currentValue')}
              >
                Value {sortColumn === 'currentValue' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th
                style={{ ...tableHeaderCellStyle, textAlign: 'right' }}
                onClick={() => handleSort('unrealizedGain')}
              >
                Unrealized Gain {sortColumn === 'unrealizedGain' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th style={{ ...tableHeaderCellStyle, textAlign: 'center' }}>
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedHoldings.map((holding) => {
              const gainColor = holding.unrealizedGain >= 0 ? '#10B981' : '#EF4444';
              const badge = getTaxBadge(holding.accountType);

              return (
                <tr
                  key={holding.id}
                  style={tableRowStyle}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#F8FAFC';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                >
                  <td style={{ ...tableCellStyle, fontWeight: 600, fontFamily: 'monospace' }}>
                    {holding.ticker}
                    {badge && (
                      <span style={badgeStyle(badge.color)}>{badge.text}</span>
                    )}
                  </td>
                  <td style={tableCellStyle}>{holding.name}</td>
                  <td style={{ ...tableCellStyle, textAlign: 'right', fontFamily: 'monospace' }}>
                    {holding.quantity.toFixed(4)}
                  </td>
                  <td style={{ ...tableCellStyle, textAlign: 'right', fontFamily: 'monospace' }}>
                    {formatCurrency(holding.purchasePrice)}
                  </td>
                  <td style={{ ...tableCellStyle, textAlign: 'right', fontFamily: 'monospace' }}>
                    {formatCurrency(holding.currentPrice)}
                  </td>
                  <td style={{ ...tableCellStyle, textAlign: 'right', fontFamily: 'monospace' }}>
                    {formatCurrency(holding.currentValue)}
                  </td>
                  <td
                    style={{
                      ...tableCellStyle,
                      textAlign: 'right',
                      fontFamily: 'monospace',
                      color: gainColor,
                      fontWeight: 600,
                    }}
                  >
                    {formatCurrency(holding.unrealizedGain)} ({formatPercentage(holding.unrealizedGainPercentage)})
                  </td>
                  <td style={{ ...tableCellStyle, textAlign: 'center' }}>
                    <Button
                      variant="outline"
                      size="small"
                      style={actionButtonStyle}
                      onClick={() => {
                        setSelectedHolding(holding);
                        setShowUpdatePriceModal(true);
                      }}
                    >
                      Update Price
                    </Button>
                    <Button
                      variant="outline"
                      size="small"
                      style={actionButtonStyle}
                      onClick={() => {
                        setSelectedHolding(holding);
                        setShowSellModal(true);
                      }}
                    >
                      Sell
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Modals */}
      {showAddForm && (
        <AddHoldingForm
          accounts={accounts}
          onSubmit={handleAddHolding}
          onCancel={() => setShowAddForm(false)}
        />
      )}

      {showSellModal && selectedHolding && (
        <SellHoldingModal
          holding={selectedHolding}
          onSubmit={(sellData) => handleSellHolding(selectedHolding.id, sellData)}
          onCancel={() => {
            setShowSellModal(false);
            setSelectedHolding(null);
          }}
        />
      )}

      {showUpdatePriceModal && selectedHolding && (
        <UpdatePriceModal
          holding={selectedHolding}
          onSubmit={(newPrice) => handleUpdatePrice(selectedHolding.id, newPrice)}
          onCancel={() => {
            setShowUpdatePriceModal(false);
            setSelectedHolding(null);
          }}
        />
      )}
    </div>
  );
}
