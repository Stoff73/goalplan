import React, { useState } from 'react';
import { Layout } from '../components/Layout';
import { EstateDashboard } from '../components/iht/EstateDashboard';
import { GiftTracker } from '../components/iht/GiftTracker';

/**
 * IHTPage - Main page for Inheritance Tax planning with tab navigation
 *
 * Features:
 * - Tab navigation: Estate, Gifts, SA Estate Duty
 * - State preservation between tabs
 * - Responsive layout
 * - Educational header section
 *
 * Follows STYLEGUIDE.md narrative storytelling approach
 */
export function IHTPage() {
  const [activeTab, setActiveTab] = useState('estate');

  // Styles
  const containerStyle = {
    padding: '0',
  };

  const headerStyle = {
    marginBottom: '48px',
  };

  const titleStyle = {
    fontSize: '2.5rem',
    fontWeight: 'bold',
    color: '#0F172A',
    marginBottom: '16px',
  };

  const subtitleStyle = {
    fontSize: '1.1rem',
    color: '#475569',
    lineHeight: '1.7',
    maxWidth: '800px',
  };

  const tabContainerStyle = {
    borderBottom: '2px solid #E2E8F0',
    marginBottom: '48px',
    display: 'flex',
    gap: '32px',
  };

  const tabStyle = (isActive) => ({
    padding: '12px 0',
    fontSize: '1rem',
    fontWeight: 600,
    color: isActive ? '#2563EB' : '#64748B',
    borderBottom: isActive ? '3px solid #2563EB' : '3px solid transparent',
    cursor: 'pointer',
    transition: 'all 0.15s ease',
    position: 'relative',
    top: '2px',
  });

  const tabHoverStyle = {
    color: '#2563EB',
  };

  return (
    <Layout>
      <div style={containerStyle}>
        {/* Header */}
        <div style={headerStyle}>
          <h1 style={titleStyle}>Inheritance Tax Planning</h1>
          <p style={subtitleStyle}>
            Understand your estate value and potential inheritance tax liability. We'll help you explore
            strategies to reduce the tax burden on your beneficiaries through lifetime gifting, nil rate bands,
            and reliefs.
          </p>
        </div>

        {/* Tab Navigation */}
        <div style={tabContainerStyle}>
        <div
          style={tabStyle(activeTab === 'estate')}
          onClick={() => setActiveTab('estate')}
          onMouseEnter={(e) => {
            if (activeTab !== 'estate') {
              e.target.style.color = tabHoverStyle.color;
            }
          }}
          onMouseLeave={(e) => {
            if (activeTab !== 'estate') {
              e.target.style.color = '#64748B';
            }
          }}
        >
          Estate Calculation
        </div>

        <div
          style={tabStyle(activeTab === 'gifts')}
          onClick={() => setActiveTab('gifts')}
          onMouseEnter={(e) => {
            if (activeTab !== 'gifts') {
              e.target.style.color = tabHoverStyle.color;
            }
          }}
          onMouseLeave={(e) => {
            if (activeTab !== 'gifts') {
              e.target.style.color = '#64748B';
            }
          }}
        >
          Lifetime Gifts
        </div>

        <div
          style={tabStyle(activeTab === 'sa')}
          onClick={() => setActiveTab('sa')}
          onMouseEnter={(e) => {
            if (activeTab !== 'sa') {
              e.target.style.color = tabHoverStyle.color;
            }
          }}
          onMouseLeave={(e) => {
            if (activeTab !== 'sa') {
              e.target.style.color = '#64748B';
            }
          }}
        >
          SA Estate Duty
        </div>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'estate' && <EstateDashboard />}
        {activeTab === 'gifts' && <GiftTracker />}
        {activeTab === 'sa' && (
          <div
            style={{
              padding: '64px 32px',
              textAlign: 'center',
              backgroundColor: '#F8FAFC',
              borderRadius: '12px',
              border: '1px dashed #CBD5E1',
            }}
          >
            <h3 style={{ fontSize: '1.5rem', fontWeight: 600, color: '#0F172A', marginBottom: '16px' }}>
              SA Estate Duty Coming Soon
            </h3>
            <p style={{ fontSize: '1rem', color: '#64748B', lineHeight: '1.7', maxWidth: '600px', margin: '0 auto' }}>
              South African Estate Duty calculation will be available here. This will include the R3.5 million
              abatement, Section 4(q) deductions, and dual tax relief calculations.
            </p>
          </div>
        )}
      </div>
      </div>
    </Layout>
  );
}
