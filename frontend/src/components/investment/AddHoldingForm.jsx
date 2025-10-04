import React, { useState } from 'react';
import { Button, Card, Input, Label, Select, Alert } from 'internal-packages/ui';

/**
 * AddHoldingForm - Form to add new investment holding
 *
 * Features:
 * - Account selector dropdown
 * - Security type selection
 * - Text inputs for ticker, name
 * - Number inputs for quantity, purchase price
 * - Date picker for purchase date
 * - Asset class, region, sector selection
 * - Currency selector
 * - Client-side validation
 * - Modal/slide-over display
 *
 * Follows STYLEGUIDE.md design system
 */
export function AddHoldingForm({ accounts, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    accountId: '',
    securityType: 'STOCK',
    ticker: '',
    name: '',
    quantity: '',
    purchasePrice: '',
    purchaseDate: new Date().toISOString().split('T')[0],
    assetClass: 'EQUITY',
    region: 'UK',
    sector: '',
    currency: 'GBP',
  });

  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const securityTypes = [
    { value: 'STOCK', label: 'Stock' },
    { value: 'ETF', label: 'ETF' },
    { value: 'FUND', label: 'Fund' },
    { value: 'BOND', label: 'Bond' },
    { value: 'VCT', label: 'VCT' },
    { value: 'EIS_SHARE', label: 'EIS Share' },
    { value: 'SEIS_SHARE', label: 'SEIS Share' },
  ];

  const assetClasses = [
    { value: 'EQUITY', label: 'Equity' },
    { value: 'FIXED_INCOME', label: 'Fixed Income' },
    { value: 'PROPERTY', label: 'Property' },
    { value: 'COMMODITY', label: 'Commodity' },
    { value: 'CASH', label: 'Cash' },
    { value: 'ALTERNATIVE', label: 'Alternative' },
  ];

  const regions = [
    { value: 'UK', label: 'UK' },
    { value: 'US', label: 'US' },
    { value: 'EUROPE', label: 'Europe' },
    { value: 'ASIA', label: 'Asia' },
    { value: 'EMERGING', label: 'Emerging Markets' },
    { value: 'GLOBAL', label: 'Global' },
  ];

  const currencies = [
    { value: 'GBP', label: 'GBP (£)' },
    { value: 'USD', label: 'USD ($)' },
    { value: 'EUR', label: 'EUR (€)' },
    { value: 'ZAR', label: 'ZAR (R)' },
  ];

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Required fields
    if (!formData.accountId) {
      newErrors.accountId = 'Please select an account';
    }
    if (!formData.ticker.trim()) {
      newErrors.ticker = 'Ticker symbol is required';
    }
    if (!formData.name.trim()) {
      newErrors.name = 'Security name is required';
    }

    // Quantity validation
    const quantity = parseFloat(formData.quantity);
    if (!formData.quantity || isNaN(quantity)) {
      newErrors.quantity = 'Quantity is required';
    } else if (quantity <= 0) {
      newErrors.quantity = 'Quantity must be greater than 0';
    }

    // Purchase price validation
    const purchasePrice = parseFloat(formData.purchasePrice);
    if (!formData.purchasePrice || isNaN(purchasePrice)) {
      newErrors.purchasePrice = 'Purchase price is required';
    } else if (purchasePrice < 0) {
      newErrors.purchasePrice = 'Purchase price cannot be negative';
    }

    // Purchase date validation
    if (!formData.purchaseDate) {
      newErrors.purchaseDate = 'Purchase date is required';
    } else {
      const purchaseDate = new Date(formData.purchaseDate);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (purchaseDate > today) {
        newErrors.purchaseDate = 'Purchase date cannot be in the future';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError(null);

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      // Convert string values to numbers
      const submitData = {
        ...formData,
        quantity: parseFloat(formData.quantity),
        purchasePrice: parseFloat(formData.purchasePrice),
      };

      await onSubmit(submitData);
    } catch (err) {
      setSubmitError(err.message || 'Failed to add holding. Please try again.');
      setIsSubmitting(false);
    }
  };

  // Styles following STYLEGUIDE.md
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
    boxShadow: '0 10px 15px rgba(0, 0, 0, 0.1)',
    maxWidth: '600px',
    width: '100%',
    maxHeight: '90vh',
    overflowY: 'auto',
    padding: '32px',
  };

  const modalHeaderStyle = {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#0F172A',
    marginBottom: '8px',
  };

  const modalSubheaderStyle = {
    color: '#475569',
    lineHeight: '1.7',
    marginBottom: '24px',
  };

  const formGroupStyle = {
    marginBottom: '20px',
  };

  const labelStyle = {
    display: 'block',
    marginBottom: '8px',
    fontSize: '0.875rem',
    fontWeight: 600,
    color: '#0F172A',
  };

  const errorStyle = {
    color: '#EF4444',
    fontSize: '0.875rem',
    marginTop: '4px',
  };

  const inputErrorStyle = {
    borderColor: '#EF4444',
  };

  const buttonGroupStyle = {
    display: 'flex',
    gap: '12px',
    marginTop: '32px',
  };

  const twoColumnStyle = {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '16px',
    marginBottom: '20px',
  };

  return (
    <div style={modalOverlayStyle} onClick={onCancel}>
      <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
        <h2 style={modalHeaderStyle}>Add New Holding</h2>
        <p style={modalSubheaderStyle}>
          Add a new investment holding to track its performance and manage tax reporting.
        </p>

        {submitError && (
          <Alert variant="error" style={{ marginBottom: '24px' }}>
            {submitError}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          {/* Account Selection */}
          <div style={formGroupStyle}>
            <Label style={labelStyle}>Investment Account *</Label>
            <Select
              value={formData.accountId}
              onChange={(e) => handleChange('accountId', e.target.value)}
              style={errors.accountId ? inputErrorStyle : {}}
            >
              <option value="">Select an account</option>
              {accounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.provider} - {account.accountType}
                </option>
              ))}
            </Select>
            {errors.accountId && <p style={errorStyle}>{errors.accountId}</p>}
          </div>

          {/* Security Type */}
          <div style={formGroupStyle}>
            <Label style={labelStyle}>Security Type *</Label>
            <Select
              value={formData.securityType}
              onChange={(e) => handleChange('securityType', e.target.value)}
            >
              {securityTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </Select>
          </div>

          {/* Ticker and Name */}
          <div style={twoColumnStyle}>
            <div>
              <Label style={labelStyle}>Ticker Symbol *</Label>
              <Input
                type="text"
                value={formData.ticker}
                onChange={(e) => handleChange('ticker', e.target.value.toUpperCase())}
                placeholder="AAPL"
                style={errors.ticker ? inputErrorStyle : {}}
              />
              {errors.ticker && <p style={errorStyle}>{errors.ticker}</p>}
            </div>

            <div>
              <Label style={labelStyle}>Currency *</Label>
              <Select
                value={formData.currency}
                onChange={(e) => handleChange('currency', e.target.value)}
              >
                {currencies.map((curr) => (
                  <option key={curr.value} value={curr.value}>
                    {curr.label}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          <div style={formGroupStyle}>
            <Label style={labelStyle}>Security Name *</Label>
            <Input
              type="text"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="Apple Inc."
              style={errors.name ? inputErrorStyle : {}}
            />
            {errors.name && <p style={errorStyle}>{errors.name}</p>}
          </div>

          {/* Quantity and Purchase Price */}
          <div style={twoColumnStyle}>
            <div>
              <Label style={labelStyle}>Quantity *</Label>
              <Input
                type="number"
                step="0.0001"
                value={formData.quantity}
                onChange={(e) => handleChange('quantity', e.target.value)}
                placeholder="100"
                style={errors.quantity ? inputErrorStyle : {}}
              />
              {errors.quantity && <p style={errorStyle}>{errors.quantity}</p>}
            </div>

            <div>
              <Label style={labelStyle}>Purchase Price *</Label>
              <Input
                type="number"
                step="0.01"
                value={formData.purchasePrice}
                onChange={(e) => handleChange('purchasePrice', e.target.value)}
                placeholder="150.00"
                style={errors.purchasePrice ? inputErrorStyle : {}}
              />
              {errors.purchasePrice && <p style={errorStyle}>{errors.purchasePrice}</p>}
            </div>
          </div>

          {/* Purchase Date */}
          <div style={formGroupStyle}>
            <Label style={labelStyle}>Purchase Date *</Label>
            <Input
              type="date"
              value={formData.purchaseDate}
              onChange={(e) => handleChange('purchaseDate', e.target.value)}
              max={new Date().toISOString().split('T')[0]}
              style={errors.purchaseDate ? inputErrorStyle : {}}
            />
            {errors.purchaseDate && <p style={errorStyle}>{errors.purchaseDate}</p>}
          </div>

          {/* Asset Class and Region */}
          <div style={twoColumnStyle}>
            <div>
              <Label style={labelStyle}>Asset Class</Label>
              <Select
                value={formData.assetClass}
                onChange={(e) => handleChange('assetClass', e.target.value)}
              >
                {assetClasses.map((asset) => (
                  <option key={asset.value} value={asset.value}>
                    {asset.label}
                  </option>
                ))}
              </Select>
            </div>

            <div>
              <Label style={labelStyle}>Region</Label>
              <Select
                value={formData.region}
                onChange={(e) => handleChange('region', e.target.value)}
              >
                {regions.map((region) => (
                  <option key={region.value} value={region.value}>
                    {region.label}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          {/* Sector (Optional) */}
          <div style={formGroupStyle}>
            <Label style={labelStyle}>Sector (Optional)</Label>
            <Input
              type="text"
              value={formData.sector}
              onChange={(e) => handleChange('sector', e.target.value)}
              placeholder="Technology, Healthcare, etc."
            />
          </div>

          {/* Buttons */}
          <div style={buttonGroupStyle}>
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={isSubmitting}
              style={{ flex: 1 }}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={isSubmitting}
              style={{ flex: 1 }}
            >
              {isSubmitting ? 'Adding...' : 'Add Holding'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
