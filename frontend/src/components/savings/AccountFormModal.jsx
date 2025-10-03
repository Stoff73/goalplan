import React, { useState, useEffect } from 'react';
import { Button, Input, Label, Select } from 'internal-packages/ui';

export function AccountFormModal({ account, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    bankName: '',
    accountName: '',
    accountType: 'SAVINGS',
    currency: 'GBP',
    currentBalance: '',
    interestRate: '',
    interestPaymentFrequency: 'ANNUALLY',
    isIsa: false,
    isTfsa: false,
    accountPurpose: 'GENERAL',
    country: 'UK',
  });

  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (account) {
      setFormData({
        bankName: account.bankName || '',
        accountName: account.accountName || '',
        accountType: account.accountType || 'SAVINGS',
        currency: account.currency || 'GBP',
        currentBalance: account.currentBalance?.toString() || '',
        interestRate: account.interestRate?.toString() || '',
        interestPaymentFrequency: account.interestPaymentFrequency || 'ANNUALLY',
        isIsa: account.isIsa || false,
        isTfsa: account.isTfsa || false,
        accountPurpose: account.accountPurpose || 'GENERAL',
        country: account.country || 'UK',
      });
    }
  }, [account]);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const handleCheckboxChange = (field) => {
    const newValue = !formData[field];
    setFormData(prev => ({
      ...prev,
      [field]: newValue,
      // Can't be both ISA and TFSA
      ...(field === 'isIsa' && newValue ? { isTfsa: false } : {}),
      ...(field === 'isTfsa' && newValue ? { isIsa: false } : {}),
    }));
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.bankName.trim()) {
      newErrors.bankName = 'Bank name is required';
    }

    if (!formData.accountName.trim()) {
      newErrors.accountName = 'Account name is required';
    }

    if (!formData.currentBalance || parseFloat(formData.currentBalance) < 0) {
      newErrors.currentBalance = 'Balance must be 0 or greater';
    }

    if (formData.interestRate && parseFloat(formData.interestRate) < 0) {
      newErrors.interestRate = 'Interest rate must be 0 or greater';
    }

    if (formData.isIsa && formData.country !== 'UK') {
      newErrors.isIsa = 'ISAs are only available for UK accounts';
    }

    if (formData.isTfsa && formData.country !== 'SA') {
      newErrors.isTfsa = 'TFSAs are only available for South African accounts';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setSaving(true);

    try {
      const submitData = {
        ...formData,
        currentBalance: parseFloat(formData.currentBalance),
        interestRate: formData.interestRate ? parseFloat(formData.interestRate) : null,
      };

      await onSave(submitData);
    } catch (err) {
      console.error('Error saving account:', err);
    } finally {
      setSaving(false);
    }
  };

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
    padding: '32px',
    maxWidth: '600px',
    width: '100%',
    maxHeight: '90vh',
    overflowY: 'auto',
    boxShadow: '0 20px 25px rgba(0, 0, 0, 0.1)',
  };

  const modalTitleStyle = {
    fontSize: '1.5rem',
    fontWeight: 700,
    color: '#0F172A',
    marginBottom: '24px',
  };

  const formGroupStyle = {
    marginBottom: '20px',
  };

  const errorStyle = {
    color: '#EF4444',
    fontSize: '0.875rem',
    marginTop: '4px',
  };

  const checkboxGroupStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '12px',
  };

  const buttonGroupStyle = {
    display: 'flex',
    gap: '12px',
    marginTop: '32px',
  };

  return (
    <div style={modalOverlayStyle} onClick={onCancel}>
      <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
        <h2 style={modalTitleStyle}>
          {account ? 'Edit Savings Account' : 'Add Savings Account'}
        </h2>

        <form onSubmit={handleSubmit}>
          {/* Bank Name */}
          <div style={formGroupStyle}>
            <Label htmlFor="bankName">Bank Name *</Label>
            <Input
              id="bankName"
              type="text"
              value={formData.bankName}
              onChange={(e) => handleChange('bankName', e.target.value)}
              placeholder="e.g., Barclays, Standard Bank"
            />
            {errors.bankName && <p style={errorStyle}>{errors.bankName}</p>}
          </div>

          {/* Account Name */}
          <div style={formGroupStyle}>
            <Label htmlFor="accountName">Account Name *</Label>
            <Input
              id="accountName"
              type="text"
              value={formData.accountName}
              onChange={(e) => handleChange('accountName', e.target.value)}
              placeholder="e.g., Main Savings, Emergency Fund"
            />
            {errors.accountName && <p style={errorStyle}>{errors.accountName}</p>}
          </div>

          {/* Account Type */}
          <div style={formGroupStyle}>
            <Label htmlFor="accountType">Account Type *</Label>
            <Select
              id="accountType"
              value={formData.accountType}
              onChange={(e) => handleChange('accountType', e.target.value)}
              options={[
                { value: 'CURRENT', label: 'Current Account' },
                { value: 'SAVINGS', label: 'Savings Account' },
                { value: 'FIXED_DEPOSIT', label: 'Fixed Deposit' },
                { value: 'MONEY_MARKET', label: 'Money Market' },
                { value: 'CASH_ISA', label: 'Cash ISA' },
                { value: 'TFSA', label: 'TFSA' },
                { value: 'NOTICE_ACCOUNT', label: 'Notice Account' },
                { value: 'OTHER', label: 'Other' },
              ]}
            />
          </div>

          {/* Country */}
          <div style={formGroupStyle}>
            <Label htmlFor="country">Country *</Label>
            <Select
              id="country"
              value={formData.country}
              onChange={(e) => handleChange('country', e.target.value)}
              options={[
                { value: 'UK', label: 'United Kingdom' },
                { value: 'SA', label: 'South Africa' },
                { value: 'OTHER', label: 'Other' },
              ]}
            />
          </div>

          {/* Currency */}
          <div style={formGroupStyle}>
            <Label htmlFor="currency">Currency *</Label>
            <Select
              id="currency"
              value={formData.currency}
              onChange={(e) => handleChange('currency', e.target.value)}
              options={[
                { value: 'GBP', label: 'GBP (£)' },
                { value: 'ZAR', label: 'ZAR (R)' },
                { value: 'USD', label: 'USD ($)' },
                { value: 'EUR', label: 'EUR (€)' },
              ]}
            />
          </div>

          {/* Current Balance */}
          <div style={formGroupStyle}>
            <Label htmlFor="currentBalance">Current Balance *</Label>
            <Input
              id="currentBalance"
              type="number"
              step="0.01"
              min="0"
              value={formData.currentBalance}
              onChange={(e) => handleChange('currentBalance', e.target.value)}
              placeholder="0.00"
            />
            {errors.currentBalance && <p style={errorStyle}>{errors.currentBalance}</p>}
          </div>

          {/* Interest Rate */}
          <div style={formGroupStyle}>
            <Label htmlFor="interestRate">Interest Rate (% per year)</Label>
            <Input
              id="interestRate"
              type="number"
              step="0.01"
              min="0"
              value={formData.interestRate}
              onChange={(e) => handleChange('interestRate', e.target.value)}
              placeholder="e.g., 4.5"
            />
            {errors.interestRate && <p style={errorStyle}>{errors.interestRate}</p>}
          </div>

          {/* Interest Payment Frequency */}
          <div style={formGroupStyle}>
            <Label htmlFor="interestPaymentFrequency">Interest Payment Frequency</Label>
            <Select
              id="interestPaymentFrequency"
              value={formData.interestPaymentFrequency}
              onChange={(e) => handleChange('interestPaymentFrequency', e.target.value)}
              options={[
                { value: 'MONTHLY', label: 'Monthly' },
                { value: 'QUARTERLY', label: 'Quarterly' },
                { value: 'ANNUALLY', label: 'Annually' },
                { value: 'MATURITY', label: 'At Maturity' },
              ]}
            />
          </div>

          {/* Purpose */}
          <div style={formGroupStyle}>
            <Label htmlFor="accountPurpose">Account Purpose</Label>
            <Select
              id="accountPurpose"
              value={formData.accountPurpose}
              onChange={(e) => handleChange('accountPurpose', e.target.value)}
              options={[
                { value: 'EMERGENCY_FUND', label: 'Emergency Fund' },
                { value: 'SHORT_TERM_GOAL', label: 'Short-term Goal' },
                { value: 'LONG_TERM_SAVINGS', label: 'Long-term Savings' },
                { value: 'GENERAL', label: 'General Savings' },
              ]}
            />
          </div>

          {/* Checkboxes */}
          <div style={formGroupStyle}>
            <div style={checkboxGroupStyle}>
              <input
                type="checkbox"
                id="isIsa"
                checked={formData.isIsa}
                onChange={() => handleCheckboxChange('isIsa')}
                style={{ width: '16px', height: '16px', cursor: 'pointer' }}
              />
              <Label htmlFor="isIsa" style={{ cursor: 'pointer', marginBottom: 0 }}>
                This is an ISA (UK only)
              </Label>
            </div>
            {errors.isIsa && <p style={errorStyle}>{errors.isIsa}</p>}

            <div style={checkboxGroupStyle}>
              <input
                type="checkbox"
                id="isTfsa"
                checked={formData.isTfsa}
                onChange={() => handleCheckboxChange('isTfsa')}
                style={{ width: '16px', height: '16px', cursor: 'pointer' }}
              />
              <Label htmlFor="isTfsa" style={{ cursor: 'pointer', marginBottom: 0 }}>
                This is a TFSA (South Africa only)
              </Label>
            </div>
            {errors.isTfsa && <p style={errorStyle}>{errors.isTfsa}</p>}
          </div>

          {/* Buttons */}
          <div style={buttonGroupStyle}>
            <Button type="button" variant="outline" onClick={onCancel} style={{ flex: 1 }}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={saving} style={{ flex: 1 }}>
              {saving ? 'Saving...' : account ? 'Update Account' : 'Add Account'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
