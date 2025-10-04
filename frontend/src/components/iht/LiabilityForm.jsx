import React, { useState } from 'react';
import { Button } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * LiabilityForm - Modal form for adding/editing liabilities
 *
 * Features:
 * - Liability type, description, creditor
 * - Outstanding balance, interest rate
 * - Security (linked asset)
 * - Deductibility flags
 * - Validation
 */
export function LiabilityForm({ liability, onClose, onSave }) {
  const isEditing = !!liability;

  const [formData, setFormData] = useState({
    liabilityType: liability?.liabilityType || '',
    description: liability?.description || '',
    creditor: liability?.creditor || '',
    outstandingBalance: liability?.outstandingBalance || '',
    currency: liability?.currency || 'GBP',
    interestRate: liability?.interestRate || '',
    isSecured: liability?.linkedAsset?.isSecured || false,
    linkedAssetId: liability?.linkedAsset?.assetId || '',
    ukIhtDeductible: liability?.deductibility?.ukIht?.deductible ?? true,
    saEstateDutyDeductible: liability?.deductibility?.saEstateDuty?.deductible ?? true,
  });

  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  const liabilityTypes = [
    { value: 'MORTGAGE', label: 'Mortgage' },
    { value: 'PERSONAL_LOAN', label: 'Personal Loan' },
    { value: 'CREDIT_CARD', label: 'Credit Card' },
    { value: 'BUSINESS_LOAN', label: 'Business Loan' },
    { value: 'OVERDRAFT', label: 'Overdraft' },
    { value: 'TAX_LIABILITY', label: 'Tax Liability' },
    { value: 'OTHER', label: 'Other' },
  ];

  const currencies = [
    { value: 'GBP', label: 'GBP (£)' },
    { value: 'ZAR', label: 'ZAR (R)' },
    { value: 'USD', label: 'USD ($)' },
    { value: 'EUR', label: 'EUR (€)' },
  ];

  const validateForm = () => {
    const newErrors = {};

    if (!formData.liabilityType) {
      newErrors.liabilityType = 'Liability type is required';
    }
    if (!formData.description) {
      newErrors.description = 'Description is required';
    }
    if (!formData.outstandingBalance || formData.outstandingBalance <= 0) {
      newErrors.outstandingBalance = 'Balance must be greater than zero';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setSaving(true);

    try {
      const url = isEditing
        ? `/api/v1/iht/liabilities/${liability.id}`
        : '/api/v1/iht/liabilities';

      const method = isEditing ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({
          liabilityType: formData.liabilityType,
          description: formData.description,
          creditor: formData.creditor,
          financial: {
            outstandingBalance: parseFloat(formData.outstandingBalance),
            currency: formData.currency,
            interestRate: formData.interestRate ? parseFloat(formData.interestRate) : null,
          },
          linkedAsset: {
            isSecured: formData.isSecured,
            linkedAssetId: formData.linkedAssetId || null,
          },
          deductibility: {
            ukIhtDeductible: formData.ukIhtDeductible,
            saEstateDutyDeductible: formData.saEstateDutyDeductible,
          },
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save liability');
      }

      const savedLiability = await response.json();
      onSave(savedLiability);
      onClose();
    } catch (err) {
      console.error('Error saving liability:', err);
      alert(err.message || 'Failed to save liability. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  // Styles (reuse from AssetForm)
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
  };

  const modalContentStyle = {
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    padding: '32px',
    width: '90%',
    maxWidth: '600px',
    maxHeight: '90vh',
    overflowY: 'auto',
    boxShadow: '0 20px 25px rgba(0, 0, 0, 0.1)',
  };

  const modalHeaderStyle = {
    fontSize: '1.5rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '24px',
  };

  const formGroupStyle = {
    marginBottom: '20px',
  };

  const labelStyle = {
    display: 'block',
    fontSize: '0.875rem',
    fontWeight: 500,
    color: '#0F172A',
    marginBottom: '6px',
  };

  const inputStyle = {
    width: '100%',
    padding: '10px 12px',
    fontSize: '0.875rem',
    border: '1px solid #E2E8F0',
    borderRadius: '8px',
    outline: 'none',
    transition: 'border-color 0.15s',
  };

  const errorStyle = {
    fontSize: '0.75rem',
    color: '#EF4444',
    marginTop: '4px',
  };

  const buttonGroupStyle = {
    display: 'flex',
    gap: '12px',
    marginTop: '32px',
    justifyContent: 'flex-end',
  };

  const checkboxLabelStyle = {
    display: 'flex',
    alignItems: 'center',
    fontSize: '0.875rem',
    color: '#475569',
    cursor: 'pointer',
    marginBottom: '8px',
  };

  const checkboxStyle = {
    marginRight: '8px',
    width: '16px',
    height: '16px',
    cursor: 'pointer',
  };

  return (
    <div style={modalOverlayStyle} onClick={onClose}>
      <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
        <h2 style={modalHeaderStyle}>
          {isEditing ? 'Edit Liability' : 'Add Liability'}
        </h2>

        <form onSubmit={handleSubmit}>
          {/* Liability Type */}
          <div style={formGroupStyle}>
            <label htmlFor="liabilityType" style={labelStyle}>
              Liability Type *
            </label>
            <select
              id="liabilityType"
              value={formData.liabilityType}
              onChange={(e) => handleChange('liabilityType', e.target.value)}
              style={{ ...inputStyle, ...(errors.liabilityType ? { borderColor: '#EF4444' } : {}) }}
              required
            >
              <option value="">Select liability type</option>
              {liabilityTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
            {errors.liabilityType && <div style={errorStyle}>{errors.liabilityType}</div>}
          </div>

          {/* Description */}
          <div style={formGroupStyle}>
            <label htmlFor="description" style={labelStyle}>
              Description *
            </label>
            <input
              type="text"
              id="description"
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              placeholder="e.g., Mortgage on main residence"
              style={{ ...inputStyle, ...(errors.description ? { borderColor: '#EF4444' } : {}) }}
              required
            />
            {errors.description && <div style={errorStyle}>{errors.description}</div>}
          </div>

          {/* Creditor */}
          <div style={formGroupStyle}>
            <label htmlFor="creditor" style={labelStyle}>
              Creditor / Lender
            </label>
            <input
              type="text"
              id="creditor"
              value={formData.creditor}
              onChange={(e) => handleChange('creditor', e.target.value)}
              placeholder="e.g., Bank name"
              style={inputStyle}
            />
          </div>

          {/* Outstanding Balance and Currency */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '12px', marginBottom: '20px' }}>
            <div>
              <label htmlFor="outstandingBalance" style={labelStyle}>
                Outstanding Balance *
              </label>
              <input
                type="number"
                id="outstandingBalance"
                value={formData.outstandingBalance}
                onChange={(e) => handleChange('outstandingBalance', e.target.value)}
                placeholder="0"
                step="0.01"
                style={{ ...inputStyle, ...(errors.outstandingBalance ? { borderColor: '#EF4444' } : {}) }}
                required
              />
              {errors.outstandingBalance && <div style={errorStyle}>{errors.outstandingBalance}</div>}
            </div>

            <div>
              <label htmlFor="currency" style={labelStyle}>
                Currency
              </label>
              <select
                id="currency"
                value={formData.currency}
                onChange={(e) => handleChange('currency', e.target.value)}
                style={inputStyle}
              >
                {currencies.map((curr) => (
                  <option key={curr.value} value={curr.value}>
                    {curr.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Interest Rate */}
          <div style={formGroupStyle}>
            <label htmlFor="interestRate" style={labelStyle}>
              Interest Rate (% per year)
            </label>
            <input
              type="number"
              id="interestRate"
              value={formData.interestRate}
              onChange={(e) => handleChange('interestRate', e.target.value)}
              placeholder="e.g., 5.5"
              step="0.01"
              style={inputStyle}
            />
          </div>

          {/* Security */}
          <div style={{ ...formGroupStyle, padding: '16px', backgroundColor: '#F8FAFC', borderRadius: '8px' }}>
            <label style={checkboxLabelStyle}>
              <input
                type="checkbox"
                checked={formData.isSecured}
                onChange={(e) => handleChange('isSecured', e.target.checked)}
                style={checkboxStyle}
              />
              This liability is secured against an asset
            </label>

            {formData.isSecured && (
              <div style={{ marginTop: '12px' }}>
                <label htmlFor="linkedAssetId" style={labelStyle}>
                  Linked Asset (Optional)
                </label>
                <input
                  type="text"
                  id="linkedAssetId"
                  value={formData.linkedAssetId}
                  onChange={(e) => handleChange('linkedAssetId', e.target.value)}
                  placeholder="Asset ID"
                  style={inputStyle}
                />
                <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '4px' }}>
                  Link this liability to a specific asset in your estate
                </div>
              </div>
            )}
          </div>

          {/* Deductibility */}
          <div style={{ ...formGroupStyle, padding: '16px', backgroundColor: '#F8FAFC', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#0F172A', marginBottom: '12px' }}>
              Deductibility
            </div>

            <label style={checkboxLabelStyle}>
              <input
                type="checkbox"
                checked={formData.ukIhtDeductible}
                onChange={(e) => handleChange('ukIhtDeductible', e.target.checked)}
                style={checkboxStyle}
              />
              Deductible for UK Inheritance Tax
            </label>

            <label style={checkboxLabelStyle}>
              <input
                type="checkbox"
                checked={formData.saEstateDutyDeductible}
                onChange={(e) => handleChange('saEstateDutyDeductible', e.target.checked)}
                style={checkboxStyle}
              />
              Deductible for SA Estate Duty
            </label>

            <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '8px', lineHeight: '1.6' }}>
              Most legitimate debts are deductible. However, liabilities to connected persons may not be.
            </div>
          </div>

          {/* Action Buttons */}
          <div style={buttonGroupStyle}>
            <Button variant="outline" onClick={onClose} disabled={saving}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={saving}>
              {saving ? 'Saving...' : isEditing ? 'Update Liability' : 'Add Liability'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
