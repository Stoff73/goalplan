import React, { useState, useEffect } from 'react';
import { Button, Input, Label, Select } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * AssetForm - Modal form for adding/editing estate assets
 *
 * Features:
 * - Multi-step form with validation
 * - Asset type, description, value, currency
 * - Ownership structure (sole, joint, trust, company)
 * - UK/SA inclusion determination
 * - Document attachment support
 *
 * Follows STYLEGUIDE.md patterns with clear labels and validation
 */
export function AssetForm({ asset, onClose, onSave }) {
  const isEditing = !!asset;

  const [formData, setFormData] = useState({
    assetType: asset?.assetType || '',
    assetCategory: asset?.assetCategory || '',
    description: asset?.description || '',
    location: asset?.location || 'UK',
    currentValue: asset?.currentValue || '',
    currency: asset?.currency || 'GBP',
    valuationDate: asset?.valuationDate || new Date().toISOString().split('T')[0],
    ownershipType: asset?.ownership?.type || 'SOLE',
    ownershipPercentage: asset?.ownership?.userPercentage || 100,
    ukIhtApplicable: asset?.ukIhtApplicable ?? true,
    saEstateDutyApplicable: asset?.saEstateDutyApplicable ?? false,
  });

  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  const assetTypes = [
    { value: 'PROPERTY', label: 'Property' },
    { value: 'INVESTMENT', label: 'Investment' },
    { value: 'CASH', label: 'Cash & Bank Accounts' },
    { value: 'BUSINESS_INTEREST', label: 'Business Interest' },
    { value: 'LIFE_POLICY', label: 'Life Insurance' },
    { value: 'PENSION', label: 'Pension' },
    { value: 'PERSONAL_POSSESSION', label: 'Personal Possession' },
    { value: 'OTHER', label: 'Other' },
  ];

  const locations = [
    { value: 'UK', label: 'United Kingdom' },
    { value: 'SA', label: 'South Africa' },
    { value: 'OFFSHORE', label: 'Offshore' },
    { value: 'OTHER', label: 'Other' },
  ];

  const ownershipTypes = [
    { value: 'SOLE', label: 'Sole ownership' },
    { value: 'JOINT_TENANTS', label: 'Joint tenants' },
    { value: 'TENANTS_IN_COMMON', label: 'Tenants in common' },
    { value: 'TRUST', label: 'Held in trust' },
    { value: 'COMPANY', label: 'Company ownership' },
  ];

  const currencies = [
    { value: 'GBP', label: 'GBP (£)' },
    { value: 'ZAR', label: 'ZAR (R)' },
    { value: 'USD', label: 'USD ($)' },
    { value: 'EUR', label: 'EUR (€)' },
  ];

  const validateForm = () => {
    const newErrors = {};

    if (!formData.assetType) {
      newErrors.assetType = 'Asset type is required';
    }
    if (!formData.description) {
      newErrors.description = 'Description is required';
    }
    if (!formData.currentValue || formData.currentValue <= 0) {
      newErrors.currentValue = 'Value must be greater than zero';
    }
    if (!formData.valuationDate) {
      newErrors.valuationDate = 'Valuation date is required';
    }
    if (formData.ownershipPercentage < 0 || formData.ownershipPercentage > 100) {
      newErrors.ownershipPercentage = 'Percentage must be between 0 and 100';
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
        ? `/api/v1/iht/assets/${asset.id}`
        : '/api/v1/iht/assets';

      const method = isEditing ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({
          assetType: formData.assetType,
          assetCategory: formData.assetCategory,
          description: formData.description,
          location: formData.location,
          valuation: {
            currentValue: parseFloat(formData.currentValue),
            currency: formData.currency,
            valuationDate: formData.valuationDate,
          },
          ownership: {
            ownershipType: formData.ownershipType,
            ownershipPercentage: parseFloat(formData.ownershipPercentage),
          },
          taxation: {
            ukIhtApplicable: formData.ukIhtApplicable,
            saEstateDutyApplicable: formData.saEstateDutyApplicable,
          },
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save asset');
      }

      const savedAsset = await response.json();
      onSave(savedAsset);
      onClose();
    } catch (err) {
      console.error('Error saving asset:', err);
      alert(err.message || 'Failed to save asset. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  // Styles
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

  const inputFocusStyle = {
    borderColor: '#2563EB',
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
          {isEditing ? 'Edit Asset' : 'Add Asset'}
        </h2>

        <form onSubmit={handleSubmit}>
          {/* Asset Type */}
          <div style={formGroupStyle}>
            <label htmlFor="assetType" style={labelStyle}>
              Asset Type *
            </label>
            <select
              id="assetType"
              value={formData.assetType}
              onChange={(e) => handleChange('assetType', e.target.value)}
              style={{ ...inputStyle, ...(errors.assetType ? { borderColor: '#EF4444' } : {}) }}
              required
            >
              <option value="">Select asset type</option>
              {assetTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
            {errors.assetType && <div style={errorStyle}>{errors.assetType}</div>}
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
              placeholder="e.g., Main residence, Investment portfolio"
              style={{ ...inputStyle, ...(errors.description ? { borderColor: '#EF4444' } : {}) }}
              required
            />
            {errors.description && <div style={errorStyle}>{errors.description}</div>}
          </div>

          {/* Location */}
          <div style={formGroupStyle}>
            <label htmlFor="location" style={labelStyle}>
              Location
            </label>
            <select
              id="location"
              value={formData.location}
              onChange={(e) => handleChange('location', e.target.value)}
              style={inputStyle}
            >
              {locations.map((loc) => (
                <option key={loc.value} value={loc.value}>
                  {loc.label}
                </option>
              ))}
            </select>
          </div>

          {/* Current Value and Currency */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '12px', marginBottom: '20px' }}>
            <div>
              <label htmlFor="currentValue" style={labelStyle}>
                Current Value *
              </label>
              <input
                type="number"
                id="currentValue"
                value={formData.currentValue}
                onChange={(e) => handleChange('currentValue', e.target.value)}
                placeholder="0"
                step="0.01"
                style={{ ...inputStyle, ...(errors.currentValue ? { borderColor: '#EF4444' } : {}) }}
                required
              />
              {errors.currentValue && <div style={errorStyle}>{errors.currentValue}</div>}
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

          {/* Valuation Date */}
          <div style={formGroupStyle}>
            <label htmlFor="valuationDate" style={labelStyle}>
              Valuation Date *
            </label>
            <input
              type="date"
              id="valuationDate"
              value={formData.valuationDate}
              onChange={(e) => handleChange('valuationDate', e.target.value)}
              max={new Date().toISOString().split('T')[0]}
              style={{ ...inputStyle, ...(errors.valuationDate ? { borderColor: '#EF4444' } : {}) }}
              required
            />
            {errors.valuationDate && <div style={errorStyle}>{errors.valuationDate}</div>}
          </div>

          {/* Ownership Type */}
          <div style={formGroupStyle}>
            <label htmlFor="ownershipType" style={labelStyle}>
              Ownership Structure
            </label>
            <select
              id="ownershipType"
              value={formData.ownershipType}
              onChange={(e) => handleChange('ownershipType', e.target.value)}
              style={inputStyle}
            >
              {ownershipTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Ownership Percentage (if not sole) */}
          {formData.ownershipType !== 'SOLE' && (
            <div style={formGroupStyle}>
              <label htmlFor="ownershipPercentage" style={labelStyle}>
                Your Ownership Percentage
              </label>
              <input
                type="number"
                id="ownershipPercentage"
                value={formData.ownershipPercentage}
                onChange={(e) => handleChange('ownershipPercentage', e.target.value)}
                min="0"
                max="100"
                step="0.01"
                style={{ ...inputStyle, ...(errors.ownershipPercentage ? { borderColor: '#EF4444' } : {}) }}
              />
              {errors.ownershipPercentage && <div style={errorStyle}>{errors.ownershipPercentage}</div>}
            </div>
          )}

          {/* Tax Treatment */}
          <div style={{ ...formGroupStyle, padding: '16px', backgroundColor: '#F8FAFC', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#0F172A', marginBottom: '12px' }}>
              Tax Treatment
            </div>

            <label style={checkboxLabelStyle}>
              <input
                type="checkbox"
                checked={formData.ukIhtApplicable}
                onChange={(e) => handleChange('ukIhtApplicable', e.target.checked)}
                style={checkboxStyle}
              />
              Include in UK Inheritance Tax calculation
            </label>

            <label style={checkboxLabelStyle}>
              <input
                type="checkbox"
                checked={formData.saEstateDutyApplicable}
                onChange={(e) => handleChange('saEstateDutyApplicable', e.target.checked)}
                style={checkboxStyle}
              />
              Include in SA Estate Duty calculation
            </label>
          </div>

          {/* Action Buttons */}
          <div style={buttonGroupStyle}>
            <Button variant="outline" onClick={onClose} disabled={saving}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={saving}>
              {saving ? 'Saving...' : isEditing ? 'Update Asset' : 'Add Asset'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
