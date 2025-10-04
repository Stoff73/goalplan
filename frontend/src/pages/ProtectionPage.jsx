import React, { useState, useEffect } from 'react';
import { Layout } from '../components/Layout';
import { Button, Alert } from 'internal-packages/ui';
import { PolicyList } from '../components/protection/PolicyList';
import { PolicyFormModal } from '../components/protection/PolicyFormModal';
import { CoverageGapWidget } from '../components/protection/CoverageGapWidget';
import { authStorage } from '../utils/auth';

export default function ProtectionPage() {
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [policyToEdit, setPolicyToEdit] = useState(null);
  const [widgetRefreshKey, setWidgetRefreshKey] = useState(0);

  console.log('🔄 ProtectionPage rendering, isModalOpen:', isModalOpen);

  useEffect(() => {
    loadPolicies();
  }, []);

  const loadPolicies = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/protection/life-assurance', {
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
        throw new Error('Failed to fetch policies');
      }

      const data = await response.json();
      setPolicies(data || []);
    } catch (err) {
      setError('Failed to load life assurance policies. Please try again.');
      console.error('Error loading policies:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddPolicy = () => {
    console.log('🔘 Add Policy button clicked');
    setPolicyToEdit(null);
    setIsModalOpen(true);
    console.log('🔘 Modal should now be open, isModalOpen set to true');
  };

  const handleEditPolicy = (policy) => {
    setPolicyToEdit(policy);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setPolicyToEdit(null);
  };

  const handleSavePolicy = async (policyData) => {
    console.log('🌐 ProtectionPage: handleSavePolicy called', { policyData, policyToEdit });

    const url = policyToEdit
      ? `/api/v1/protection/life-assurance/${policyToEdit.id}`
      : '/api/v1/protection/life-assurance';

    const method = policyToEdit ? 'PUT' : 'POST';

    console.log('🌐 ProtectionPage: Making request', { url, method });

    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify(policyData),
      });

      console.log('🌐 ProtectionPage: Response received', {
        status: response.status,
        ok: response.ok
      });

      if (!response.ok) {
        if (response.status === 401) {
          console.log('🌐 ProtectionPage: Unauthorized, redirecting to login');
          authStorage.clear();
          window.location.href = '/login';
          return;
        }

        const errorData = await response.json();
        console.error('🌐 ProtectionPage: Error response', errorData);
        throw new Error(errorData.detail || 'Failed to save policy');
      }

      console.log('🌐 ProtectionPage: Save successful!');
      setSuccess(policyToEdit ? 'Policy updated successfully!' : 'Policy added successfully!');
      await loadPolicies();
      handleCloseModal();

      // Refresh widget after policy changes
      setWidgetRefreshKey(prev => prev + 1);

      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      console.error('🌐 ProtectionPage: Error in handleSavePolicy', err);
      throw err; // Re-throw so the modal can handle it
    }
  };

  const handleViewPolicy = (policy) => {
    // TODO: Open policy details modal
    console.log('View policy:', policy);
    alert(`View details for ${policy.provider} - Coming soon!`);
  };

  const handleDeletePolicy = async (policyId) => {
    try {
      const response = await fetch(`/api/v1/protection/life-assurance/${policyId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete policy');
      }

      setSuccess('Policy deleted successfully!');
      await loadPolicies();

      // Refresh widget after policy changes
      setWidgetRefreshKey(prev => prev + 1);

      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setError(err.message || 'Failed to delete policy. Please try again.');
      console.error('Error deleting policy:', err);
    }
  };

  const formatCurrency = (amount, currency = 'GBP') => {
    if (amount === null || amount === undefined) return '-';
    const symbols = { GBP: '£', USD: '$', EUR: '€', ZAR: 'R' };
    const symbol = symbols[currency] || currency;
    return `${symbol}${amount.toLocaleString('en-GB', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })}`;
  };

  // Calculate summary stats
  const activePolicies = policies.filter((p) => p.status === 'ACTIVE');
  const totalCoverGBP = activePolicies.reduce((sum, p) => {
    // Convert all to GBP for summary
    const gbpAmount = p.coverAmountGbp || p.coverAmount || 0;
    return sum + gbpAmount;
  }, 0);
  const totalAnnualPremium = activePolicies.reduce((sum, p) => {
    const annualPremium = p.annualPremium || 0;
    return sum + annualPremium;
  }, 0);

  // Styles
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
    marginBottom: '48px',
  };

  // Empty State
  const hasActivePolicies = activePolicies.length > 0;

  if (!loading && !hasActivePolicies) {
    return (
      <Layout showHeader={true} containerWidth="xl">
        <h1 style={pageTitleStyle}>Your Life Assurance Protection</h1>
        <p style={pageDescStyle}>
          Protect your family's financial future with comprehensive life assurance coverage across the UK and South Africa.
        </p>

        {error && (
          <Alert variant="error" style={{ marginBottom: '24px' }}>
            <p style={{ fontWeight: 600 }}>Error</p>
            <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
          </Alert>
        )}

        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Welcome to Your Protection Dashboard</h3>
          <p style={paragraphStyle}>
            You haven't added any life assurance policies yet. Life assurance is one of the most important
            financial protections you can have—it ensures your family is financially secure if something
            happens to you.
          </p>
          <p style={paragraphStyle}>
            GoalPlan helps you track all your life assurance policies in one place, whether they're from
            the UK, South Africa, or elsewhere. We'll help you understand your total coverage, identify
            any gaps, and optimize for tax efficiency (especially UK Inheritance Tax).
          </p>

          <div style={calloutStyle}>
            <p style={{ fontWeight: 600, color: '#1E40AF', marginBottom: '8px' }}>
              Why track life assurance?
            </p>
            <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
              Tracking your life assurance helps ensure you have adequate coverage to protect your family,
              that policies are written in trust to avoid Inheritance Tax (UK), and that premiums are
              competitive. Most families need cover of 10-12 times annual income to replace lost earnings
              and maintain their lifestyle.
            </p>
          </div>

          <Button variant="primary" onClick={handleAddPolicy} style={{ marginTop: '24px' }}>
            + Add Your First Policy
          </Button>
        </div>

        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>What You Can Track</h3>
          <p style={paragraphStyle}>
            GoalPlan supports all major life assurance policy types:
          </p>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: '16px',
              marginTop: '24px',
            }}
          >
            <div style={{ padding: '16px', border: '1px solid #E2E8F0', borderRadius: '8px' }}>
              <h4 style={{ fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>UK Policies</h4>
              <ul style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7', paddingLeft: '20px' }}>
                <li>Term life assurance</li>
                <li>Whole of life policies</li>
                <li>Policies written in trust (IHT-efficient)</li>
                <li>Critical illness riders</li>
              </ul>
            </div>

            <div style={{ padding: '16px', border: '1px solid #E2E8F0', borderRadius: '8px' }}>
              <h4 style={{ fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>South African Policies</h4>
              <ul style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7', paddingLeft: '20px' }}>
                <li>Life cover policies</li>
                <li>Funeral plans</li>
                <li>Estate duty considerations</li>
                <li>Disability cover</li>
              </ul>
            </div>

            <div style={{ padding: '16px', border: '1px solid #E2E8F0', borderRadius: '8px' }}>
              <h4 style={{ fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>Coverage Analysis</h4>
              <ul style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7', paddingLeft: '20px' }}>
                <li>Total coverage calculation</li>
                <li>Coverage gap analysis</li>
                <li>Beneficiary tracking</li>
                <li>Premium cost comparison</li>
              </ul>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // Main protection page with policies
  return (
    <Layout showHeader={true} containerWidth="xl">
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: '32px',
          flexWrap: 'wrap',
          gap: '16px',
        }}
      >
        <div>
          <h1 style={pageTitleStyle}>Your Life Assurance Protection</h1>
          <p style={{ color: '#475569', fontSize: '0.875rem' }}>
            You have {activePolicies.length} active polic{activePolicies.length === 1 ? 'y' : 'ies'} protecting your family
          </p>
        </div>
        <Button variant="primary" onClick={handleAddPolicy}>
          + Add Policy
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

      {/* Coverage Gap Widget */}
      <CoverageGapWidget key={widgetRefreshKey} onRefresh={loadPolicies} />

      {/* Coverage Summary */}
      {activePolicies.length > 0 && (
        <div style={narrativeSectionStyle}>
          <h3 style={sectionHeadingStyle}>Your Protection Coverage</h3>
          <p style={paragraphStyle}>
            You have <strong style={{ fontFamily: 'monospace', fontSize: '1.1rem' }}>
              {formatCurrency(totalCoverGBP, 'GBP')}
            </strong> in total life assurance coverage across {activePolicies.length} active polic{activePolicies.length === 1 ? 'y' : 'ies'}.{' '}
            {totalCoverGBP > 0
              ? "That's protecting your family's financial future."
              : 'Consider adding policies to protect your loved ones.'}
          </p>

          <div style={metricGridStyle}>
            <div style={compactMetricStyle}>
              <div style={metricValueStyle}>{formatCurrency(totalCoverGBP, 'GBP')}</div>
              <div style={metricLabelStyle}>total coverage (GBP equivalent)</div>
            </div>
            <div style={compactMetricStyle}>
              <div style={metricValueStyle}>{activePolicies.length}</div>
              <div style={metricLabelStyle}>active policies</div>
            </div>
            <div style={compactMetricStyle}>
              <div style={metricValueStyle}>{formatCurrency(totalAnnualPremium, 'GBP')}</div>
              <div style={metricLabelStyle}>annual premiums</div>
            </div>
          </div>
        </div>
      )}

      {/* Policy List */}
      <PolicyList
        policies={policies}
        loading={loading}
        onEdit={handleEditPolicy}
        onDelete={handleDeletePolicy}
        onView={handleViewPolicy}
        onAdd={handleAddPolicy}
      />

      {/* Educational Footer */}
      <div style={calloutStyle}>
        <h3 style={{ fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>
          Making the Most of Your Life Assurance
        </h3>
        <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7', marginBottom: '12px' }}>
          <strong>UK Policies in Trust:</strong> Writing your life assurance policy in trust means the payout
          goes directly to your beneficiaries without forming part of your estate. This avoids Inheritance Tax
          (40% on amounts above £325,000) and speeds up the payout process. If your UK policies aren't in trust,
          consider arranging this with your provider.
        </p>
        <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7', marginBottom: '12px' }}>
          <strong>Coverage Needs:</strong> Financial advisors typically recommend life cover of 10-12 times your
          annual income, plus outstanding debts (mortgage, loans) and future expenses (children's education).
          This ensures your family can maintain their lifestyle if you're not there to provide for them.
        </p>
        <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
          <strong>Critical Illness Cover:</strong> Many policies include critical illness riders that pay out
          if you're diagnosed with a serious condition (cancer, heart attack, stroke). This provides financial
          support during recovery when you may not be able to work.
        </p>
      </div>

      {/* Policy Form Modal */}
      <PolicyFormModal
        key={`modal-${isModalOpen}`}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        policy={policyToEdit}
        onSave={handleSavePolicy}
      />
    </Layout>
  );
}
