import React, { useState } from 'react';
import { Layout } from '../components/Layout';
import { AskAI } from '../components/ai/AskAI';
import { RetirementAdvice } from '../components/ai/RetirementAdvice';
import { InvestmentAdvice } from '../components/ai/InvestmentAdvice';
import { TaxAdvice } from '../components/ai/TaxAdvice';
import { MonthlyInsights } from '../components/ai/MonthlyInsights';
import { AlertsList } from '../components/ai/AlertsList';

/**
 * AIAdvisorPage - Main page for AI financial advisor
 *
 * Features:
 * - Tabbed interface for different advice types
 * - Tabs: Ask AI, Retirement, Investment, Tax, Monthly Insights, Alerts
 * - Responsive tab switching
 * - Follows STYLEGUIDE.md design patterns
 */
export default function AIAdvisorPage() {
  const [activeTab, setActiveTab] = useState('ask');

  const tabs = [
    { id: 'ask', label: 'Ask AI', component: AskAI },
    { id: 'retirement', label: 'Retirement', component: RetirementAdvice },
    { id: 'investment', label: 'Investment', component: InvestmentAdvice },
    { id: 'tax', label: 'Tax', component: TaxAdvice },
    { id: 'insights', label: 'Monthly Insights', component: MonthlyInsights },
    { id: 'alerts', label: 'Alerts', component: AlertsList },
  ];

  const ActiveComponent = tabs.find((tab) => tab.id === activeTab)?.component || AskAI;

  // Styles
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
    marginBottom: '32px',
    borderBottom: '1px solid #E2E8F0',
    overflowX: 'auto',
    flexWrap: 'wrap',
  };

  const tabButtonStyle = (isActive) => ({
    padding: '12px 20px',
    backgroundColor: 'transparent',
    border: '0',
    borderBottom: isActive ? '2px solid #2563EB' : '2px solid transparent',
    color: isActive ? '#2563EB' : '#475569',
    fontSize: '0.95rem',
    fontWeight: isActive ? 600 : 500,
    cursor: 'pointer',
    transition: 'all 150ms ease-in-out',
    whiteSpace: 'nowrap',
  });

  return (
    <Layout showHeader={true} containerWidth="xl">
      <h1 style={pageTitleStyle}>AI Financial Advisor</h1>
      <p style={pageDescStyle}>
        Get personalized financial advice powered by AI, tailored to your UK and South African
        financial situation. Ask questions, get insights, and receive actionable recommendations.
      </p>

      {/* Tabs */}
      <div style={tabContainerStyle}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={tabButtonStyle(activeTab === tab.id)}
            onMouseEnter={(e) => {
              if (activeTab !== tab.id) {
                e.currentTarget.style.color = '#2563EB';
                e.currentTarget.style.backgroundColor = '#EFF6FF';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== tab.id) {
                e.currentTarget.style.color = '#475569';
                e.currentTarget.style.backgroundColor = 'transparent';
              }
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Active Tab Content */}
      <ActiveComponent />
    </Layout>
  );
}
