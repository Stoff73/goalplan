import React, { useState, useEffect } from 'react';
import { Layout } from '../components/Layout';
import { Button, Alert } from 'internal-packages/ui';
import { authStorage } from '../utils/auth';
import { EmergencyFundWidget } from '../components/savings/EmergencyFundWidget';
import { AllowanceWidget } from '../components/savings/AllowanceWidget';
import { AccountCard } from '../components/savings/AccountCard';
import { AccountFormModal } from '../components/savings/AccountFormModal';
import { UpdateBalanceModal } from '../components/savings/UpdateBalanceModal';

export default function SavingsPage() {
  const [accounts, setAccounts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [isaAllowance, setIsaAllowance] = useState(null);
  const [tfsaAllowance, setTfsaAllowance] = useState(null);
  const [emergencyFund, setEmergencyFund] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const [showAccountForm, setShowAccountForm] = useState(false);
  const [showBalanceModal, setShowBalanceModal] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [baseCurrency, setBaseCurrency] = useState('GBP');
  const [filterType, setFilterType] = useState('ALL');
  const [expandedAccounts, setExpandedAccounts] = useState(new Set());

  useEffect(() => {
    loadData();
  }, [baseCurrency]);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      await Promise.all([
        loadAccounts(),
        loadSummary(),
        loadAllowances(),
        loadEmergencyFund(),
      ]);
    } catch (err) {
      setError('Failed to load savings data. Please try again.');
      console.error('Error loading savings data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadAccounts = async () => {
    const response = await fetch('/api/v1/savings/accounts', {
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
      throw new Error('Failed to fetch accounts');
    }

    const data = await response.json();
    setAccounts(data || []);
  };

  const loadSummary = async () => {
    const response = await fetch(`/api/v1/savings/summary?base_currency=${baseCurrency}`, {
      headers: {
        'Authorization': `Bearer ${authStorage.getAccessToken()}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      setSummary(data);
    }
  };

  const loadAllowances = async () => {
    // Load ISA allowance
    try {
      const isaResponse = await fetch('/api/v1/savings/isa-allowance', {
        headers: {
          'Authorization': `Bearer ${authStorage.getAccessToken()}`,
        },
      });
      if (isaResponse.ok) {
        const isaData = await isaResponse.json();
        setIsaAllowance(isaData);
      }
    } catch (err) {
      console.error('Error loading ISA allowance:', err);
    }

    // Load TFSA allowance
    try {
      const tfsaResponse = await fetch('/api/v1/savings/tfsa-allowance', {
        headers: {
          'Authorization': `Bearer ${authStorage.getAccessToken()}`,
        },
      });
      if (tfsaResponse.ok) {
        const tfsaData = await tfsaResponse.json();
        setTfsaAllowance(tfsaData);
      }
    } catch (err) {
      console.error('Error loading TFSA allowance:', err);
    }
  };

  const loadEmergencyFund = async () => {
    try {
      const response = await fetch('/api/v1/savings/emergency-fund-assessment?monthly_expenses=2000', {
        headers: {
          'Authorization': `Bearer ${authStorage.getAccessToken()}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setEmergencyFund(data);
      }
    } catch (err) {
      console.error('Error loading emergency fund:', err);
    }
  };

  const handleAddAccount = () => {
    setSelectedAccount(null);
    setShowAccountForm(true);
    setError(null);
    setSuccess(null);
  };

  const handleEditAccount = (account) => {
    setSelectedAccount(account);
    setShowAccountForm(true);
    setError(null);
    setSuccess(null);
  };

  const handleUpdateBalance = (account) => {
    setSelectedAccount(account);
    setShowBalanceModal(true);
    setError(null);
    setSuccess(null);
  };

  const handleSaveAccount = async (formData) => {
    try {
      const url = selectedAccount
        ? `/api/v1/savings/accounts/${selectedAccount.id}`
        : '/api/v1/savings/accounts';

      const method = selectedAccount ? 'PATCH' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${authStorage.getAccessToken()}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save account');
      }

      setSuccess(selectedAccount ? 'Account updated successfully!' : 'Account added successfully!');
      setShowAccountForm(false);
      setSelectedAccount(null);
      await loadData();

      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSaveBalance = async (balanceData) => {
    try {
      const response = await fetch(`/api/v1/savings/accounts/${selectedAccount.id}/balance`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authStorage.getAccessToken()}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(balanceData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update balance');
      }

      setSuccess('Balance updated successfully!');
      setShowBalanceModal(false);
      setSelectedAccount(null);
      await loadData();

      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteAccount = async (accountId) => {
    if (!confirm('Are you sure you want to delete this account? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/savings/accounts/${accountId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete account');
      }

      setSuccess('Account deleted successfully!');
      await loadData();

      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setError(err.message);
    }
  };

  const toggleAccountExpansion = (accountId) => {
    const newExpanded = new Set(expandedAccounts);
    if (newExpanded.has(accountId)) {
      newExpanded.delete(accountId);
    } else {
      newExpanded.add(accountId);
    }
    setExpandedAccounts(newExpanded);
  };

  const formatCurrency = (amount, currency = baseCurrency) => {
    if (amount === null || amount === undefined) return '-';
    const symbols = { GBP: '£', USD: '$', EUR: '€', ZAR: 'R' };
    const symbol = symbols[currency] || currency;
    return `${symbol}${amount.toLocaleString('en-GB', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
  };

  // Filter accounts
  const filteredAccounts = accounts.filter(account => {
    if (filterType === 'ALL') return true;
    if (filterType === 'ISA') return account.isIsa;
    if (filterType === 'TFSA') return account.isTfsa;
    if (filterType === 'EMERGENCY') return account.accountPurpose === 'EMERGENCY_FUND';
    if (filterType === 'GBP') return account.currency === 'GBP';
    if (filterType === 'ZAR') return account.currency === 'ZAR';
    return true;
  });

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

  const filterButtonStyle = (isActive) => ({
    padding: '8px 16px',
    borderRadius: '8px',
    border: isActive ? '2px solid #2563EB' : '1px solid #E2E8F0',
    backgroundColor: isActive ? '#EFF6FF' : '#FFFFFF',
    color: isActive ? '#2563EB' : '#475569',
    fontWeight: isActive ? 600 : 400,
    cursor: 'pointer',
    fontSize: '0.875rem',
    transition: 'all 150ms ease-in-out',
  });

  // Loading State
  if (loading) {
    return (
      <Layout showHeader={true} containerWidth="xl">
        <div style={{ padding: '48px 0' }}>
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

  // Empty State
  const hasAccounts = accounts.length > 0;

  if (!hasAccounts) {
    return (
      <Layout showHeader={true} containerWidth="xl">
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, lineHeight: 1.2, color: '#0F172A', marginBottom: '16px' }}>
          Your Savings: Getting Started
        </h1>
        <p style={{ color: '#475569', fontSize: '1rem', lineHeight: '1.7', marginBottom: '48px' }}>
          Track your savings across the UK and South Africa, manage ISAs and TFSAs, and build your emergency fund.
        </p>

        {error && (
          <Alert variant="error" style={{ marginBottom: '24px' }}>
            <p style={{ fontWeight: 600 }}>Error</p>
            <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
          </Alert>
        )}

        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Welcome to Your Savings Dashboard</h3>
          <p style={paragraphStyle}>
            You haven't added any savings accounts yet. Let's get started! Adding your accounts
            helps you track your total savings, monitor ISA and TFSA allowances, and assess
            whether your emergency fund is adequate.
          </p>
          <p style={paragraphStyle}>
            GoalPlan tracks all your savings in one place—current accounts, savings accounts,
            ISAs (UK), and TFSAs (South Africa). We'll help you understand how your savings
            are working for you and where you might improve.
          </p>

          <div style={calloutStyle}>
            <p style={{ fontWeight: 600, color: '#1E40AF', marginBottom: '8px' }}>
              Why track your savings?
            </p>
            <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
              Tracking your savings helps you see the full picture of your liquid assets, ensure
              you're maximizing tax-efficient accounts (ISAs and TFSAs), and maintain an adequate
              emergency fund. Most experts recommend 6 months of expenses in easily accessible savings.
            </p>
          </div>

          <Button variant="primary" onClick={handleAddAccount} style={{ marginTop: '24px' }}>
            + Add Your First Account
          </Button>
        </div>

        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>What You Can Track</h3>
          <p style={paragraphStyle}>
            GoalPlan supports all major savings account types:
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginTop: '24px' }}>
            <div style={{ padding: '16px', border: '1px solid #E2E8F0', borderRadius: '8px' }}>
              <h4 style={{ fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>UK Accounts</h4>
              <ul style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7', paddingLeft: '20px' }}>
                <li>Current accounts</li>
                <li>Savings accounts</li>
                <li>Cash ISAs (£20,000 allowance)</li>
                <li>Fixed-term deposits</li>
              </ul>
            </div>

            <div style={{ padding: '16px', border: '1px solid #E2E8F0', borderRadius: '8px' }}>
              <h4 style={{ fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>South African Accounts</h4>
              <ul style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7', paddingLeft: '20px' }}>
                <li>Cheque accounts</li>
                <li>Savings accounts</li>
                <li>TFSAs (R36,000 annual, R500,000 lifetime)</li>
                <li>Notice accounts</li>
              </ul>
            </div>

            <div style={{ padding: '16px', border: '1px solid #E2E8F0', borderRadius: '8px' }}>
              <h4 style={{ fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>Emergency Fund</h4>
              <ul style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7', paddingLeft: '20px' }}>
                <li>Mark accounts as emergency fund</li>
                <li>Track months of coverage</li>
                <li>Get recommendations</li>
                <li>Build your financial safety net</li>
              </ul>
            </div>
          </div>
        </div>

        {showAccountForm && (
          <AccountFormModal
            account={selectedAccount}
            onSave={handleSaveAccount}
            onCancel={() => setShowAccountForm(false)}
          />
        )}
      </Layout>
    );
  }

  // Main savings page with data
  const totalSavings = summary?.totalSavings || 0;
  const accountCount = accounts.length;

  return (
    <Layout showHeader={true} containerWidth="xl">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 700, lineHeight: 1.2, color: '#0F172A', marginBottom: '8px' }}>
            Your Savings
          </h1>
          <p style={{ color: '#475569', fontSize: '0.875rem' }}>
            You have {accountCount} account{accountCount !== 1 ? 's' : ''} across {summary?.currencyCount || 1} {summary?.currencyCount === 1 ? 'currency' : 'currencies'}
          </p>
        </div>
        <Button variant="primary" onClick={handleAddAccount}>
          + Add Account
        </Button>
      </div>

      {error && (
        <Alert variant="error" style={{ marginBottom: '24px' }}>
          <p style={{ fontWeight: 600 }}>Error</p>
          <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
        </Alert>
      )}

      {success && (
        <Alert variant="success" style={{ marginBottom: '24px' }}>
          <p style={{ fontWeight: 600 }}>{success}</p>
        </Alert>
      )}

      {/* Summary Section */}
      <div style={narrativeSectionStyle}>
        <h3 style={sectionHeadingStyle}>Your Savings Position</h3>
        <p style={paragraphStyle}>
          You have <strong style={{ fontFamily: 'monospace', fontSize: '1.1rem' }}>{formatCurrency(totalSavings)}</strong> saved
          across all your accounts. {totalSavings > 0 ? "That's a solid foundation for your financial future!" : "Let's start building your savings!"}
        </p>

        <div style={metricGridStyle}>
          <div style={compactMetricStyle}>
            <div style={metricValueStyle}>{formatCurrency(totalSavings)}</div>
            <div style={metricLabelStyle}>total savings</div>
          </div>
          <div style={compactMetricStyle}>
            <div style={metricValueStyle}>{accountCount}</div>
            <div style={metricLabelStyle}>accounts tracked</div>
          </div>
          {summary?.interestEarned && (
            <div style={compactMetricStyle}>
              <div style={metricValueStyle}>{formatCurrency(summary.interestEarned)}</div>
              <div style={metricLabelStyle}>projected annual interest</div>
            </div>
          )}
        </div>
      </div>

      {/* Emergency Fund Widget */}
      {emergencyFund && (
        <EmergencyFundWidget emergencyFund={emergencyFund} formatCurrency={formatCurrency} />
      )}

      {/* ISA Allowance Widget */}
      {isaAllowance && (
        <AllowanceWidget allowance={isaAllowance} type="ISA" formatCurrency={formatCurrency} />
      )}

      {/* TFSA Allowance Widget */}
      {tfsaAllowance && (
        <AllowanceWidget allowance={tfsaAllowance} type="TFSA" formatCurrency={formatCurrency} />
      )}

      {/* Filter Buttons */}
      <div style={{ marginBottom: '24px', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        <button style={filterButtonStyle(filterType === 'ALL')} onClick={() => setFilterType('ALL')}>
          All Accounts
        </button>
        <button style={filterButtonStyle(filterType === 'ISA')} onClick={() => setFilterType('ISA')}>
          ISAs
        </button>
        <button style={filterButtonStyle(filterType === 'TFSA')} onClick={() => setFilterType('TFSA')}>
          TFSAs
        </button>
        <button style={filterButtonStyle(filterType === 'EMERGENCY')} onClick={() => setFilterType('EMERGENCY')}>
          Emergency Fund
        </button>
        <button style={filterButtonStyle(filterType === 'GBP')} onClick={() => setFilterType('GBP')}>
          GBP
        </button>
        <button style={filterButtonStyle(filterType === 'ZAR')} onClick={() => setFilterType('ZAR')}>
          ZAR
        </button>
      </div>

      {/* Accounts List */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '24px', marginBottom: '48px' }}>
        {filteredAccounts.map(account => (
          <AccountCard
            key={account.id}
            account={account}
            formatCurrency={formatCurrency}
            onEdit={handleEditAccount}
            onDelete={handleDeleteAccount}
            onUpdateBalance={handleUpdateBalance}
            isExpanded={expandedAccounts.has(account.id)}
            onToggleExpand={() => toggleAccountExpansion(account.id)}
          />
        ))}
      </div>

      {filteredAccounts.length === 0 && (
        <div style={narrativeSectionStyle}>
          <p style={{ ...paragraphStyle, textAlign: 'center', color: '#94A3B8' }}>
            No accounts match your filter. Try selecting a different filter option.
          </p>
        </div>
      )}

      {/* Educational Footer */}
      <div style={calloutStyle}>
        <h3 style={{ fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>
          Making the Most of Your Savings
        </h3>
        <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7', marginBottom: '12px' }}>
          <strong>ISAs (UK):</strong> You can save up to £20,000 per tax year (April to April) in ISAs
          completely tax-free. Interest, dividends, and capital gains are all exempt from tax. Make sure
          you use your allowance before the tax year ends!
        </p>
        <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7', marginBottom: '12px' }}>
          <strong>TFSAs (South Africa):</strong> You can contribute R36,000 per tax year (March to February)
          with a lifetime limit of R500,000. All returns are tax-free, making TFSAs an excellent way to
          build wealth over time.
        </p>
        <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
          <strong>Emergency Fund:</strong> Most financial advisors recommend keeping 3-6 months of expenses
          in an easily accessible savings account. This provides a safety net for unexpected events like
          job loss, medical emergencies, or urgent home repairs.
        </p>
      </div>

      {/* Modals */}
      {showAccountForm && (
        <AccountFormModal
          account={selectedAccount}
          onSave={handleSaveAccount}
          onCancel={() => setShowAccountForm(false)}
        />
      )}

      {showBalanceModal && selectedAccount && (
        <UpdateBalanceModal
          account={selectedAccount}
          onSave={handleSaveBalance}
          onCancel={() => setShowBalanceModal(false)}
          formatCurrency={formatCurrency}
        />
      )}
    </Layout>
  );
}
