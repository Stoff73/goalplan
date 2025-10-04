import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { Button } from 'internal-packages/ui';
import { RetirementDashboard } from '../components/retirement/RetirementDashboard';
import { PensionList } from '../components/retirement/PensionList';
import { AnnualAllowanceTracker } from '../components/retirement/AnnualAllowanceTracker';
import { PensionForm } from '../components/retirement/PensionForm';
import { SAFundList } from '../components/retirement/SAFundList';
import { SAFundForm } from '../components/retirement/SAFundForm';
import { SADeductionTracker } from '../components/retirement/SADeductionTracker';

/**
 * RetirementPage - Main retirement module page with tab navigation
 *
 * Features:
 * - Tab-based navigation (Overview, UK Pensions, SA Funds, Annual Allowance, SA Deduction)
 * - URL-based routing for tabs
 * - Modal for add/edit pension/fund
 * - STYLEGUIDE.md narrative storytelling approach
 * - Responsive design
 *
 * Tabs:
 * - Overview: Retirement dashboard with projections and scenarios
 * - UK Pensions: UK pension list with add/edit functionality
 * - SA Funds: SA retirement fund list with add/edit functionality
 * - Annual Allowance: UK AA tracker with carry forward
 * - SA Deduction: SA Section 10C deduction tracker
 */
export default function RetirementPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState('overview');
  const [showPensionForm, setShowPensionForm] = useState(false);
  const [editingPensionId, setEditingPensionId] = useState(null);
  const [showSAFundForm, setShowSAFundForm] = useState(false);
  const [editingSAFundId, setEditingSAFundId] = useState(null);

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    // Tab switching uses local state only - no URL navigation
  };

  const handleAddPension = () => {
    setEditingPensionId(null);
    setShowPensionForm(true);
  };

  const handleEditPension = (pensionId) => {
    setEditingPensionId(pensionId);
    setShowPensionForm(true);
  };

  const handleAddSAFund = () => {
    setEditingSAFundId(null);
    setShowSAFundForm(true);
  };

  const handleEditSAFund = (fundId) => {
    setEditingSAFundId(fundId);
    setShowSAFundForm(true);
  };

  const handleFormSuccess = () => {
    setShowPensionForm(false);
    setEditingPensionId(null);
    setShowSAFundForm(false);
    setEditingSAFundId(null);
    // Reload current tab data
    window.location.reload();
  };

  const handleFormCancel = () => {
    setShowPensionForm(false);
    setEditingPensionId(null);
    setShowSAFundForm(false);
    setEditingSAFundId(null);
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

  const modalOverlayStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: '16px',
  };

  const modalContentStyle = {
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    maxWidth: '900px',
    width: '100%',
    maxHeight: '90vh',
    overflow: 'auto',
    padding: '32px',
    position: 'relative',
  };

  const modalHeaderStyle = {
    fontSize: '1.5rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '24px',
  };

  const closeButtonStyle = {
    position: 'absolute',
    top: '16px',
    right: '16px',
    background: 'none',
    border: 'none',
    fontSize: '1.5rem',
    color: '#94A3B8',
    cursor: 'pointer',
    padding: '8px',
    lineHeight: 1,
  };

  return (
    <Layout showHeader={true} containerWidth="xl">
      <h1 style={pageTitleStyle}>Your Retirement Planning</h1>
      <p style={pageDescStyle}>
        Plan for a comfortable retirement with comprehensive pension tracking, income projections, and
        tax-efficient contribution strategies.
      </p>

      {/* Tab Navigation */}
      <div style={tabContainerStyle}>
        <button
          style={tabButtonStyle(activeTab === 'overview')}
          onClick={() => handleTabChange('overview')}
          onMouseEnter={(e) => {
            if (activeTab !== 'overview') {
              e.target.style.color = '#2563EB';
            }
          }}
          onMouseLeave={(e) => {
            if (activeTab !== 'overview') {
              e.target.style.color = '#475569';
            }
          }}
          aria-selected={activeTab === 'overview'}
          role="tab"
        >
          Overview
        </button>

        <button
          style={tabButtonStyle(activeTab === 'uk-pensions')}
          onClick={() => handleTabChange('uk-pensions')}
          onMouseEnter={(e) => {
            if (activeTab !== 'uk-pensions') {
              e.target.style.color = '#2563EB';
            }
          }}
          onMouseLeave={(e) => {
            if (activeTab !== 'uk-pensions') {
              e.target.style.color = '#475569';
            }
          }}
          aria-selected={activeTab === 'uk-pensions'}
          role="tab"
        >
          UK Pensions
        </button>

        <button
          style={tabButtonStyle(activeTab === 'sa-funds')}
          onClick={() => handleTabChange('sa-funds')}
          onMouseEnter={(e) => {
            if (activeTab !== 'sa-funds') {
              e.target.style.color = '#2563EB';
            }
          }}
          onMouseLeave={(e) => {
            if (activeTab !== 'sa-funds') {
              e.target.style.color = '#475569';
            }
          }}
          aria-selected={activeTab === 'sa-funds'}
          role="tab"
        >
          SA Funds
        </button>

        <button
          style={tabButtonStyle(activeTab === 'uk-allowance')}
          onClick={() => handleTabChange('uk-allowance')}
          onMouseEnter={(e) => {
            if (activeTab !== 'uk-allowance') {
              e.target.style.color = '#2563EB';
            }
          }}
          onMouseLeave={(e) => {
            if (activeTab !== 'uk-allowance') {
              e.target.style.color = '#475569';
            }
          }}
          aria-selected={activeTab === 'uk-allowance'}
          role="tab"
        >
          UK Allowance
        </button>

        <button
          style={tabButtonStyle(activeTab === 'sa-deduction')}
          onClick={() => handleTabChange('sa-deduction')}
          onMouseEnter={(e) => {
            if (activeTab !== 'sa-deduction') {
              e.target.style.color = '#2563EB';
            }
          }}
          onMouseLeave={(e) => {
            if (activeTab !== 'sa-deduction') {
              e.target.style.color = '#475569';
            }
          }}
          aria-selected={activeTab === 'sa-deduction'}
          role="tab"
        >
          SA Deduction
        </button>
      </div>

      {/* Tab Content */}
      <div role="tabpanel">
        {activeTab === 'overview' && <RetirementDashboard />}
        {activeTab === 'uk-pensions' && (
          <PensionList onAddPension={handleAddPension} onEditPension={handleEditPension} />
        )}
        {activeTab === 'sa-funds' && (
          <SAFundList onAddFund={handleAddSAFund} onEditFund={handleEditSAFund} />
        )}
        {activeTab === 'uk-allowance' && <AnnualAllowanceTracker />}
        {activeTab === 'sa-deduction' && <SADeductionTracker />}
      </div>

      {/* Pension Form Modal */}
      {showPensionForm && (
        <div style={modalOverlayStyle} onClick={handleFormCancel}>
          <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
            <button
              style={closeButtonStyle}
              onClick={handleFormCancel}
              aria-label="Close"
              onMouseEnter={(e) => {
                e.target.style.color = '#0F172A';
              }}
              onMouseLeave={(e) => {
                e.target.style.color = '#94A3B8';
              }}
            >
              ×
            </button>
            <h2 style={modalHeaderStyle}>
              {editingPensionId ? 'Edit Pension' : 'Add New Pension'}
            </h2>
            <PensionForm
              pensionId={editingPensionId}
              onSuccess={handleFormSuccess}
              onCancel={handleFormCancel}
            />
          </div>
        </div>
      )}

      {/* SA Fund Form Modal */}
      {showSAFundForm && (
        <div style={modalOverlayStyle} onClick={handleFormCancel}>
          <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
            <button
              style={closeButtonStyle}
              onClick={handleFormCancel}
              aria-label="Close"
              onMouseEnter={(e) => {
                e.target.style.color = '#0F172A';
              }}
              onMouseLeave={(e) => {
                e.target.style.color = '#94A3B8';
              }}
            >
              ×
            </button>
            <h2 style={modalHeaderStyle}>
              {editingSAFundId ? 'Edit SA Retirement Fund' : 'Add New SA Retirement Fund'}
            </h2>
            <SAFundForm
              fundId={editingSAFundId}
              onSuccess={handleFormSuccess}
              onCancel={handleFormCancel}
            />
          </div>
        </div>
      )}
    </Layout>
  );
}
