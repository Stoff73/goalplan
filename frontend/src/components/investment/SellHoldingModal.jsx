import React, { useState } from 'react';
import { Button, Input, Label, Alert } from 'internal-packages/ui';

/**
 * SellHoldingModal - Modal to sell investment holding
 *
 * Features:
 * - Display holding details (ticker, name, quantity owned)
 * - Number input for quantity to sell (max = owned quantity)
 * - Number input for sale price
 * - Date picker for sale date (default today)
 * - Calculate and preview realized gain
 * - Validation (quantity <= owned, sale price >= 0, date not future)
 * - Narrative style gain preview with color coding
 *
 * Follows STYLEGUIDE.md design system
 */
export function SellHoldingModal({ holding, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    quantity: '',
    salePrice: '',
    saleDate: new Date().toISOString().split('T')[0],
  });

  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  const calculateRealizedGain = () => {
    const quantity = parseFloat(formData.quantity);
    const salePrice = parseFloat(formData.salePrice);

    if (isNaN(quantity) || isNaN(salePrice)) {
      return null;
    }

    const purchasePrice = holding.purchasePrice || holding.averageCostBasis || 0;
    const realizedGain = (salePrice - purchasePrice) * quantity;
    const realizedGainPercentage = purchasePrice > 0
      ? ((salePrice - purchasePrice) / purchasePrice) * 100
      : 0;

    return { realizedGain, realizedGainPercentage };
  };

  const validateForm = () => {
    const newErrors = {};

    // Quantity validation
    const quantity = parseFloat(formData.quantity);
    if (!formData.quantity || isNaN(quantity)) {
      newErrors.quantity = 'Quantity to sell is required';
    } else if (quantity <= 0) {
      newErrors.quantity = 'Quantity must be greater than 0';
    } else if (quantity > holding.quantity) {
      newErrors.quantity = `Cannot sell more than ${holding.quantity} shares owned`;
    }

    // Sale price validation
    const salePrice = parseFloat(formData.salePrice);
    if (!formData.salePrice || isNaN(salePrice)) {
      newErrors.salePrice = 'Sale price is required';
    } else if (salePrice < 0) {
      newErrors.salePrice = 'Sale price cannot be negative';
    }

    // Sale date validation
    if (!formData.saleDate) {
      newErrors.saleDate = 'Sale date is required';
    } else {
      const saleDate = new Date(formData.saleDate);
      const today = new Date();
      today.setHours(23, 59, 59, 999); // End of today
      if (saleDate > today) {
        newErrors.saleDate = 'Sale date cannot be in the future';
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
      const submitData = {
        quantity: parseFloat(formData.quantity),
        salePrice: parseFloat(formData.salePrice),
        saleDate: formData.saleDate,
      };

      await onSubmit(submitData);
    } catch (err) {
      setSubmitError(err.message || 'Failed to sell holding. Please try again.');
      setIsSubmitting(false);
    }
  };

  const formatCurrency = (amount, currency = 'GBP') => {
    if (amount === null || amount === undefined) return '£0.00';
    const symbol = currency === 'GBP' ? '£' : currency === 'ZAR' ? 'R' : currency;
    const absAmount = Math.abs(amount);
    return `${amount < 0 ? '-' : ''}${symbol}${absAmount.toLocaleString('en-GB', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const gainPreview = calculateRealizedGain();
  const gainColor = gainPreview && gainPreview.realizedGain >= 0 ? '#10B981' : '#EF4444';
  const gainText = gainPreview && gainPreview.realizedGain >= 0 ? 'gain' : 'loss';

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
    maxWidth: '500px',
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

  const holdingDetailsStyle = {
    backgroundColor: '#F8FAFC',
    padding: '16px',
    borderRadius: '8px',
    marginBottom: '24px',
    border: '1px solid #E2E8F0',
  };

  const detailRowStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '8px',
    fontSize: '0.875rem',
  };

  const detailLabelStyle = {
    color: '#475569',
  };

  const detailValueStyle = {
    fontWeight: 600,
    color: '#0F172A',
    fontFamily: 'monospace',
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

  const gainPreviewStyle = {
    backgroundColor: '#F8FAFC',
    padding: '16px',
    borderRadius: '8px',
    marginBottom: '24px',
    border: `2px solid ${gainPreview ? gainColor : '#E2E8F0'}`,
    lineHeight: '1.7',
  };

  const buttonGroupStyle = {
    display: 'flex',
    gap: '12px',
    marginTop: '24px',
  };

  const twoColumnStyle = {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '16px',
  };

  return (
    <div style={modalOverlayStyle} onClick={onCancel}>
      <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
        <h2 style={modalHeaderStyle}>Sell Holding</h2>

        {/* Holding Details */}
        <div style={holdingDetailsStyle}>
          <div style={detailRowStyle}>
            <span style={detailLabelStyle}>Ticker:</span>
            <span style={detailValueStyle}>{holding.ticker}</span>
          </div>
          <div style={detailRowStyle}>
            <span style={detailLabelStyle}>Name:</span>
            <span style={{ ...detailValueStyle, fontFamily: 'inherit' }}>{holding.name}</span>
          </div>
          <div style={detailRowStyle}>
            <span style={detailLabelStyle}>Quantity Owned:</span>
            <span style={detailValueStyle}>{holding.quantity.toFixed(4)}</span>
          </div>
          <div style={detailRowStyle}>
            <span style={detailLabelStyle}>Purchase Price:</span>
            <span style={detailValueStyle}>
              {formatCurrency(holding.purchasePrice || holding.averageCostBasis)}
            </span>
          </div>
        </div>

        {submitError && (
          <Alert variant="error" style={{ marginBottom: '24px' }}>
            {submitError}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          {/* Quantity and Sale Price */}
          <div style={twoColumnStyle}>
            <div style={formGroupStyle}>
              <Label style={labelStyle}>Quantity to Sell *</Label>
              <Input
                type="number"
                step="0.0001"
                value={formData.quantity}
                onChange={(e) => handleChange('quantity', e.target.value)}
                placeholder={holding.quantity.toString()}
                max={holding.quantity}
                style={errors.quantity ? inputErrorStyle : {}}
              />
              {errors.quantity && <p style={errorStyle}>{errors.quantity}</p>}
            </div>

            <div style={formGroupStyle}>
              <Label style={labelStyle}>Sale Price *</Label>
              <Input
                type="number"
                step="0.01"
                value={formData.salePrice}
                onChange={(e) => handleChange('salePrice', e.target.value)}
                placeholder="150.00"
                style={errors.salePrice ? inputErrorStyle : {}}
              />
              {errors.salePrice && <p style={errorStyle}>{errors.salePrice}</p>}
            </div>
          </div>

          {/* Sale Date */}
          <div style={formGroupStyle}>
            <Label style={labelStyle}>Sale Date *</Label>
            <Input
              type="date"
              value={formData.saleDate}
              onChange={(e) => handleChange('saleDate', e.target.value)}
              max={new Date().toISOString().split('T')[0]}
              style={errors.saleDate ? inputErrorStyle : {}}
            />
            {errors.saleDate && <p style={errorStyle}>{errors.saleDate}</p>}
          </div>

          {/* Realized Gain Preview */}
          {gainPreview && (
            <div style={gainPreviewStyle}>
              <p style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '8px', color: '#0F172A' }}>
                Realized Gain Preview
              </p>
              <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
                This sale will realize a{' '}
                <strong style={{ color: gainColor }}>
                  {gainText} of {formatCurrency(Math.abs(gainPreview.realizedGain))}
                </strong>
                {' '}({gainPreview.realizedGainPercentage >= 0 ? '+' : ''}
                {gainPreview.realizedGainPercentage.toFixed(2)}%).
                {gainPreview.realizedGain >= 0
                  ? ' This gain may be subject to capital gains tax.'
                  : ' This loss may be used to offset capital gains.'}
              </p>
            </div>
          )}

          {/* Warning for tax-advantaged accounts */}
          {(holding.accountType === 'VCT' || holding.accountType === 'EIS' || holding.accountType === 'SEIS') && (
            <Alert variant="warning" style={{ marginBottom: '24px' }}>
              <p style={{ fontWeight: 600, marginBottom: '4px' }}>Tax Relief Warning</p>
              <p style={{ fontSize: '0.95rem' }}>
                Selling this holding may affect your tax relief. Please check the holding period
                requirements before proceeding.
              </p>
            </Alert>
          )}

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
              {isSubmitting ? 'Selling...' : 'Confirm Sale'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
