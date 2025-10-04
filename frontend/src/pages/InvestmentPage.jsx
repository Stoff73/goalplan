import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { Button } from 'internal-packages/ui';
import { PortfolioDashboard } from '../components/investment/PortfolioDashboard';
import { HoldingsList } from '../components/investment/HoldingsList';
import { AssetAllocation } from '../components/investment/AssetAllocation';

/**
 * InvestmentPage - Main investment module page with tab navigation
 *
 * Features:
 * - Tab-based navigation (Dashboard, Holdings, Allocation)
 * - URL-based routing for tabs
 * - STYLEGUIDE.md narrative storytelling approach
 * - Responsive design
 *
 * Tabs:
 * - Dashboard: Portfolio overview with performance metrics
 * - Holdings: Detailed holdings list with filtering
 * - Allocation: Asset allocation analysis
 */
export default function InvestmentPage() {
  const location = useLocation();
  const navigate = useNavigate();

  // Determine active tab from URL
  const getActiveTab = () => {
    const path = location.pathname;
    if (path.includes('/holdings')) return 'holdings';
    if (path.includes('/allocation')) return 'allocation';
    return 'dashboard';
  };

  const [activeTab, setActiveTab] = useState(getActiveTab());

  // Update active tab when URL changes
  useEffect(() => {
    setActiveTab(getActiveTab());
  }, [location.pathname]);

  const handleTabChange = (tab) => {
    setActiveTab(tab);

    // Update URL
    switch (tab) {
      case 'holdings':
        navigate('/investments/holdings');
        break;
      case 'allocation':
        navigate('/investments/allocation');
        break;
      default:
        navigate('/investments/dashboard');
        break;
    }
  };

  // Styles following STYLEGUIDE.md
  const pageTitleStyle = {
    fontSize: '1.8rem',
    fontWeight: 700,
    lineHeight: 1.2,
    color: '#0F172A',
    marginBottom: '16px',
  };

  const pageDescStyle = {
    color: '#475569',
    fontSize: '1rem',
    lineHeight: '1.7',
    marginBottom: '32px',
  };

  const tabContainerStyle = {
    display: 'flex',
    gap: '8px',
    borderBottom: '2px solid #E2E8F0',
    marginBottom: '32px',
    flexWrap: 'wrap',
  };

  const tabButtonStyle = (isActive) => ({
    padding: '12px 24px',
    fontSize: '1rem',
    fontWeight: 600,
    color: isActive ? '#2563EB' : '#475569',
    backgroundColor: 'transparent',
    border: 'none',
    borderBottom: isActive ? '3px solid #2563EB' : '3px solid transparent',
    marginBottom: '-2px',
    cursor: 'pointer',
    transition: 'all 150ms ease-in-out',
  });

  const tabButtonHoverStyle = {
    color: '#2563EB',
  };

  return (
    <Layout showHeader={true} containerWidth="xl">
      <h1 style={pageTitleStyle}>Your Investment Portfolio</h1>
      <p style={pageDescStyle}>
        Track your investments across the UK and South Africa. Monitor performance, manage holdings,
        and optimize your asset allocation for long-term growth.
      </p>

      {/* Tab Navigation */}
      <div style={tabContainerStyle}>
        <button
          style={tabButtonStyle(activeTab === 'dashboard')}
          onClick={() => handleTabChange('dashboard')}
          onMouseEnter={(e) => {
            if (activeTab !== 'dashboard') {
              e.target.style.color = tabButtonHoverStyle.color;
            }
          }}
          onMouseLeave={(e) => {
            if (activeTab !== 'dashboard') {
              e.target.style.color = '#475569';
            }
          }}
          aria-selected={activeTab === 'dashboard'}
          role="tab"
        >
          Dashboard
        </button>

        <button
          style={tabButtonStyle(activeTab === 'holdings')}
          onClick={() => handleTabChange('holdings')}
          onMouseEnter={(e) => {
            if (activeTab !== 'holdings') {
              e.target.style.color = tabButtonHoverStyle.color;
            }
          }}
          onMouseLeave={(e) => {
            if (activeTab !== 'holdings') {
              e.target.style.color = '#475569';
            }
          }}
          aria-selected={activeTab === 'holdings'}
          role="tab"
        >
          Holdings
        </button>

        <button
          style={tabButtonStyle(activeTab === 'allocation')}
          onClick={() => handleTabChange('allocation')}
          onMouseEnter={(e) => {
            if (activeTab !== 'allocation') {
              e.target.style.color = tabButtonHoverStyle.color;
            }
          }}
          onMouseLeave={(e) => {
            if (activeTab !== 'allocation') {
              e.target.style.color = '#475569';
            }
          }}
          aria-selected={activeTab === 'allocation'}
          role="tab"
        >
          Asset Allocation
        </button>
      </div>

      {/* Tab Content */}
      <div role="tabpanel">
        {activeTab === 'dashboard' && <PortfolioDashboard />}
        {activeTab === 'holdings' && <HoldingsList />}
        {activeTab === 'allocation' && <AssetAllocation />}
      </div>
    </Layout>
  );
}
