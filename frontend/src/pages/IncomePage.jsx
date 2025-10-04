import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { Button, Alert } from 'internal-packages/ui';
import { IncomeSummarySection } from '../components/income/IncomeSummarySection';
import { IncomeList } from '../components/income/IncomeList';
import { IncomeFormModal } from '../components/income/IncomeFormModal';
import { IncomeDetailsModal } from '../components/income/IncomeDetailsModal';
import { IncomeTaxYearSwitcher } from '../components/income/IncomeTaxYearSwitcher';
import { incomeEndpoints } from '../utils/api';
import { getCurrentUKTaxYear, getCurrentSATaxYear } from '../utils/income';
import { authStorage } from '../utils/auth';

export default function IncomePage() {
  const navigate = useNavigate();
  const [incomes, setIncomes] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const [selectedCountry, setSelectedCountry] = useState('UK');
  const [selectedTaxYear, setSelectedTaxYear] = useState(getCurrentUKTaxYear());

  const [showFormModal, setShowFormModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedIncome, setSelectedIncome] = useState(null);

  useEffect(() => {
    // Check authentication first
    if (!authStorage.isAuthenticated()) {
      navigate('/login');
      return;
    }
    loadIncomes();
  }, [navigate]);

  useEffect(() => {
    loadSummary();
  }, [selectedCountry, selectedTaxYear]);

  const loadIncomes = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await incomeEndpoints.getAll();
      setIncomes(data || []);
    } catch (err) {
      setError('Failed to load income entries. Please try again.');
      console.error('Error loading incomes:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    setSummaryLoading(true);

    try {
      const data = await incomeEndpoints.getSummary(selectedTaxYear, selectedCountry);
      setSummary(data);
    } catch (err) {
      console.error('Error loading summary:', err);
      setSummary(null);
    } finally {
      setSummaryLoading(false);
    }
  };

  const handleCountryChange = (country) => {
    setSelectedCountry(country);
    // Update tax year to match country
    if (country === 'UK') {
      setSelectedTaxYear(getCurrentUKTaxYear());
    } else {
      setSelectedTaxYear(getCurrentSATaxYear());
    }
  };

  const handleAddIncome = () => {
    setSelectedIncome(null);
    setShowFormModal(true);
    setError(null);
    setSuccess(null);
  };

  const handleEditIncome = (income) => {
    setSelectedIncome(income);
    setShowFormModal(true);
    setShowDetailsModal(false);
    setError(null);
    setSuccess(null);
  };

  const handleViewDetails = (income) => {
    setSelectedIncome(income);
    setShowDetailsModal(true);
  };

  const handleSaveIncome = async (formData) => {
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      if (selectedIncome) {
        // Update existing income
        await incomeEndpoints.update(selectedIncome.id, formData);
        setSuccess('Income updated successfully!');
      } else {
        // Create new income
        await incomeEndpoints.create(formData);
        setSuccess('Income added successfully!');
      }

      setShowFormModal(false);
      setSelectedIncome(null);

      // Reload data
      await loadIncomes();
      await loadSummary();

      // Auto-hide success message after 5 seconds
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setError(err.message || 'Failed to save income. Please try again.');
      console.error('Error saving income:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteIncome = async (incomeId) => {
    setError(null);
    setSuccess(null);

    try {
      await incomeEndpoints.delete(incomeId);
      setSuccess('Income deleted successfully!');

      // Reload data
      await loadIncomes();
      await loadSummary();

      // Auto-hide success message after 5 seconds
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setError(err.message || 'Failed to delete income. Please try again.');
      console.error('Error deleting income:', err);
    }
  };

  const handleCancelForm = () => {
    setShowFormModal(false);
    setSelectedIncome(null);
    setError(null);
  };

  const handleCloseDetails = () => {
    setShowDetailsModal(false);
    setSelectedIncome(null);
  };

  const pageHeaderStyle = {
    marginBottom: '32px',
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

  const headerActionsStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '32px',
    flexWrap: 'wrap',
    gap: '16px',
  };

  const educationalSectionStyle = {
    padding: '16px',
    backgroundColor: '#EFF6FF',
    border: '1px solid #BFDBFE',
    borderLeft: '4px solid #3B82F6',
    borderRadius: '8px',
    marginTop: '48px',
  };

  const educationalTitleStyle = {
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '8px',
  };

  const educationalTextStyle = {
    fontSize: '0.95rem',
    color: '#475569',
    lineHeight: '1.7',
  };

  return (
    <Layout>
      {/* Page Header */}
      <div style={pageHeaderStyle}>
        <h1 style={pageTitleStyle}>Your income across two countries</h1>
        <p style={pageDescStyle}>
          Track all your income sources from the UK and South Africa. We'll help you understand your
          total earnings, tax withholding, and how the UK-SA Double Tax Agreement prevents you from
          being taxed twice on the same income.
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

      {/* Header Actions */}
      <div style={headerActionsStyle}>
        <IncomeTaxYearSwitcher
          country={selectedCountry}
          taxYear={selectedTaxYear}
          onCountryChange={handleCountryChange}
          onTaxYearChange={setSelectedTaxYear}
        />
        <Button variant="primary" onClick={handleAddIncome}>
          + Add Income
        </Button>
      </div>

      {/* Income Summary Section */}
      <IncomeSummarySection
        summary={summary}
        taxYear={selectedTaxYear}
        country={selectedCountry}
        loading={summaryLoading}
      />

      {/* Income List */}
      <IncomeList
        incomes={incomes}
        loading={loading}
        onEdit={handleEditIncome}
        onDelete={handleDeleteIncome}
        onViewDetails={handleViewDetails}
        selectedTaxYear={selectedTaxYear}
        selectedCountry={selectedCountry}
      />

      {/* Educational Footer */}
      <div style={educationalSectionStyle}>
        <h3 style={educationalTitleStyle}>How we track your income</h3>
        <div style={educationalTextStyle}>
          <p style={{ marginBottom: '12px' }}>
            We track your income in the currency you received it, then convert to both GBP and ZAR using
            official exchange rates. This gives you a clear picture of your earnings in both tax jurisdictions.
          </p>
          <p style={{ marginBottom: '12px' }}>
            <strong>Foreign income</strong> means income from countries other than the UK and SA. Under the
            UK-SA Double Tax Agreement, you can claim credit for foreign tax paid, preventing double taxation
            on the same income. This is crucial for managing your overall tax position.
          </p>
          <p style={{ marginBottom: '12px' }}>
            <strong>Tax withheld</strong> includes PAYE (UK), PAYE (SA), and other withholding taxes deducted
            at source. These amounts are credited against your final tax bill when you file your tax return,
            so tracking them accurately is essential.
          </p>
          <p>
            Your actual tax liability depends on your tax residency status, domicile, and available allowances
            like the UK Personal Savings Allowance (£1,000 for basic rate taxpayers) or SA interest exemption
            (R23,800 for under-65s). Getting this right helps you avoid overpaying tax.
          </p>
        </div>
      </div>

      {/* Form Modal */}
      {showFormModal && (
        <IncomeFormModal
          income={selectedIncome}
          onSave={handleSaveIncome}
          onCancel={handleCancelForm}
          loading={saving}
        />
      )}

      {/* Details Modal */}
      {showDetailsModal && selectedIncome && (
        <IncomeDetailsModal
          income={selectedIncome}
          onEdit={handleEditIncome}
          onDelete={handleDeleteIncome}
          onClose={handleCloseDetails}
        />
      )}
    </Layout>
  );
}
