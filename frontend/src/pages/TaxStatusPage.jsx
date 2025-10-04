import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { Alert } from 'internal-packages/ui';
import { CurrentTaxStatusSection } from '../components/tax/CurrentTaxStatusSection';
import { UpdateTaxStatusForm } from '../components/tax/UpdateTaxStatusForm';
import { TaxCalculators } from '../components/tax/TaxCalculators';
import { DeemedDomicileSection } from '../components/tax/DeemedDomicileSection';
import { TaxStatusTimeline } from '../components/tax/TaxStatusTimeline';
import { taxStatusEndpoints } from '../utils/api';
import { authStorage } from '../utils/auth';

export default function TaxStatusPage() {
  const navigate = useNavigate();
  const [currentStatus, setCurrentStatus] = useState(null);
  const [history, setHistory] = useState([]);
  const [deemedDomicile, setDeemedDomicile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showUpdateForm, setShowUpdateForm] = useState(false);

  useEffect(() => {
    // Check authentication first
    if (!authStorage.isAuthenticated()) {
      navigate('/login');
      return;
    }
    loadData();
  }, [navigate]);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load current status, history, and deemed domicile in parallel
      const [currentResponse, historyResponse, deemedResponse] = await Promise.allSettled([
        taxStatusEndpoints.getCurrent(),
        taxStatusEndpoints.getHistory(),
        taxStatusEndpoints.getDeemedDomicile(),
      ]);

      // Handle current status
      if (currentResponse.status === 'fulfilled') {
        setCurrentStatus(currentResponse.value);
      } else if (currentResponse.reason?.status !== 404) {
        console.error('Failed to load current status:', currentResponse.reason);
      }

      // Handle history
      if (historyResponse.status === 'fulfilled') {
        setHistory(historyResponse.value || []);
      } else {
        console.error('Failed to load history:', historyResponse.reason);
      }

      // Handle deemed domicile
      if (deemedResponse.status === 'fulfilled') {
        setDeemedDomicile(deemedResponse.value);
      } else if (deemedResponse.reason?.status !== 404) {
        console.error('Failed to load deemed domicile:', deemedResponse.reason);
      }

      // If no current status, show update form by default
      if (currentResponse.status !== 'fulfilled') {
        setShowUpdateForm(true);
      }
    } catch (err) {
      setError('Failed to load tax status data. Please try again.');
      console.error('Error loading tax status:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveTaxStatus = async (formData) => {
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await taxStatusEndpoints.create(formData);
      setSuccess('Tax status saved successfully!');
      setShowUpdateForm(false);

      // Reload all data
      await loadData();

      // Auto-hide success message after 5 seconds
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setError(err.message || 'Failed to save tax status. Please try again.');
      console.error('Error saving tax status:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleCancelUpdate = () => {
    setShowUpdateForm(false);
    setError(null);
  };

  const handleEditStatus = () => {
    setShowUpdateForm(true);
    setError(null);
    setSuccess(null);
  };

  const pageHeaderStyle = {
    marginBottom: '48px',
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
  };

  const sectionSpacingStyle = {
    marginTop: '48px',
  };

  const calloutStyle = {
    padding: '24px',
    backgroundColor: '#EFF6FF',
    border: '1px solid #BFDBFE',
    borderLeft: '4px solid #3B82F6',
    borderRadius: '8px',
    marginTop: '48px',
  };

  const calloutTitleStyle = {
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '8px',
  };

  const calloutTextStyle = {
    fontSize: '0.95rem',
    color: '#475569',
    lineHeight: '1.7',
  };

  return (
    <Layout>
      <div>
        {/* Page Header */}
        <div style={pageHeaderStyle}>
          <h1 style={pageTitleStyle}>Understanding your tax status</h1>
          <p style={pageDescStyle}>
            Your tax residency and domicile determine where you owe tax and how much. We'll help you
            understand your status in both the UK and South Africa, and what it means for your financial planning.
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="error" style={{ marginBottom: '24px' }}>
            <p style={{ fontWeight: 600 }}>Error</p>
            <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
          </Alert>
        )}

        {/* Success Alert */}
        {success && (
          <Alert variant="success" style={{ marginBottom: '24px' }}>
            <p style={{ fontWeight: 600 }}>{success}</p>
          </Alert>
        )}

        {/* Current Tax Status Section */}
        {!showUpdateForm && (
          <div style={sectionSpacingStyle}>
            <CurrentTaxStatusSection
              taxStatus={currentStatus}
              onEdit={handleEditStatus}
              loading={loading}
            />
          </div>
        )}

        {/* Update Tax Status Form */}
        {showUpdateForm && (
          <div style={sectionSpacingStyle}>
            <UpdateTaxStatusForm
              onSubmit={handleSaveTaxStatus}
              onCancel={handleCancelUpdate}
              loading={saving}
            />
          </div>
        )}

        {/* Tax Calculators */}
        {!showUpdateForm && (
          <div style={sectionSpacingStyle}>
            <TaxCalculators />
          </div>
        )}

        {/* Deemed Domicile Section */}
        {!showUpdateForm && (
          <div style={sectionSpacingStyle}>
            <DeemedDomicileSection deemedDomicileData={deemedDomicile} loading={loading} />
          </div>
        )}

        {/* Historical Timeline */}
        {!showUpdateForm && (
          <div style={sectionSpacingStyle}>
            <TaxStatusTimeline history={history} loading={loading} />
          </div>
        )}

        {/* Educational Footer */}
        <div style={calloutStyle}>
          <h3 style={calloutTitleStyle}>Need help understanding your tax status?</h3>
          <p style={calloutTextStyle}>
            Tax residency and domicile can be complex topics, especially when you have ties to both
            the UK and South Africa. Don't worry—that's exactly why GoalPlan exists!
          </p>
          <p style={{ ...calloutTextStyle, marginTop: '12px' }}>
            If you're unsure about your status, we recommend:
          </p>
          <ul style={{
            marginTop: '8px',
            paddingLeft: '20px',
            color: '#475569',
            fontSize: '0.95rem',
            lineHeight: '1.7',
            listStyleType: 'disc'
          }}>
            <li style={{ marginBottom: '4px' }}>Using the calculators above to determine your UK and SA residency</li>
            <li style={{ marginBottom: '4px' }}>Consulting HMRC's Statutory Residence Test guidance for UK residency</li>
            <li style={{ marginBottom: '4px' }}>Reviewing SARS's physical presence test rules for SA residency</li>
            <li style={{ marginBottom: '4px' }}>Speaking with a qualified tax advisor if you have a complex situation</li>
          </ul>
          <p style={{ ...calloutTextStyle, marginTop: '12px' }}>
            Your tax status affects everything from income tax to inheritance tax planning. Getting
            it right is essential for accurate calculations and financial planning across both countries.
          </p>
        </div>
      </div>
    </Layout>
  );
}
