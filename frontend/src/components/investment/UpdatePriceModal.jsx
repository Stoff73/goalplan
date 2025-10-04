import React, { useState } from 'react';
import { Button, Input, Label, Alert } from 'internal-packages/ui';

/**
 * UpdatePriceModal - Modal to update holding current price
 *
 * Features:
 * - Display holding details (ticker, current price)
 * - Number input for new current price
 * - Show old vs new price comparison
 * - Calculate new unrealized gain preview
 * - Validation (price >= 0)
 * - Narrative style with color coding
 *
 * Follows STYLEGUIDE.md design system
 */
export function UpdatePriceModal({ holding, onSubmit, onCancel }) {
  const [newPrice, setNewPrice] = useState(holding.currentPrice?.toString() || '');
  const [error, setError] = useState(null);
  const [submitError, setSubmitError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (value) => {
    setNewPrice(value);
    // Clear error when user starts typing
    if (error) {
      setError(null);
    }
  };

  const calculateNewGain = () => {
    const price = parseFloat(newPrice);

    if (isNaN(price)) {
      return null;
    }

    const purchasePrice = holding.purchasePrice || holding.averageCostBasis || 0;
    const quantity = holding.quantity || 0;
    const newUnrealizedGain = (price - purchasePrice) * quantity;
    const newUnrealizedGainPercentage = purchasePrice > 0
      ? ((price - purchasePrice) / purchasePrice) * 100
      : 0;

    return { newUnrealizedGain, newUnrealizedGainPercentage };
  };

  const validateForm = () => {
    const price = parseFloat(newPrice);

    if (!newPrice || isNaN(price)) {
      setError('Price is required');
      return false;
    }

    if (price < 0) {
      setError('Price cannot be negative');
      return false;
    }

    if (price === holding.currentPrice) {
      setError('New price must be different from current price');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError(null);

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      await onSubmit(parseFloat(newPrice));
    } catch (err) {
      setSubmitError(err.message || 'Failed to update price. Please try again.');
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

  const newGainPreview = calculateNewGain();
  const currentGainColor = holding.unrealizedGain >= 0 ? '#10B981' : '#EF4444';
  const newGainColor = newGainPreview && newGainPreview.newUnrealizedGain >= 0 ? '#10B981' : '#EF4444';

  const priceChange = newPrice ? parseFloat(newPrice) - holding.currentPrice : 0;
  const priceChangePercent = holding.currentPrice > 0
    ? (priceChange / holding.currentPrice) * 100
    : 0;

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

  const comparisonBoxStyle = {
    backgroundColor: '#F8FAFC',
    padding: '16px',
    borderRadius: '8px',
    marginBottom: '24px',
    border: '1px solid #E2E8F0',
  };

  const comparisonHeaderStyle = {
    fontSize: '0.875rem',
    fontWeight: 600,
    marginBottom: '12px',
    color: '#0F172A',
  };

  const comparisonRowStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px',
    fontSize: '0.875rem',
  };

  const gainPreviewStyle = {
    backgroundColor: '#F8FAFC',
    padding: '16px',
    borderRadius: '8px',
    marginBottom: '24px',
    border: `2px solid ${newGainPreview ? newGainColor : '#E2E8F0'}`,
    lineHeight: '1.7',
  };

  const buttonGroupStyle = {
    display: 'flex',
    gap: '12px',
    marginTop: '24px',
  };

  return (
    <div style={modalOverlayStyle} onClick={onCancel}>
      <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
        <h2 style={modalHeaderStyle}>Update Price</h2>

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
            <span style={detailLabelStyle}>Quantity:</span>
            <span style={detailValueStyle}>{holding.quantity.toFixed(4)}</span>
          </div>
        </div>

        {submitError && (
          <Alert variant="error" style={{ marginBottom: '24px' }}>
            {submitError}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          {/* New Price Input */}
          <div style={formGroupStyle}>
            <Label style={labelStyle}>New Current Price *</Label>
            <Input
              type="number"
              step="0.01"
              value={newPrice}
              onChange={(e) => handleChange(e.target.value)}
              placeholder="150.00"
              style={error ? inputErrorStyle : {}}
              autoFocus
            />
            {error && <p style={errorStyle}>{error}</p>}
          </div>

          {/* Price Comparison */}
          {newPrice && !isNaN(parseFloat(newPrice)) && (
            <div style={comparisonBoxStyle}>
              <p style={comparisonHeaderStyle}>Price Comparison</p>

              <div style={comparisonRowStyle}>
                <span style={detailLabelStyle}>Old Price:</span>
                <span style={detailValueStyle}>{formatCurrency(holding.currentPrice)}</span>
              </div>

              <div style={comparisonRowStyle}>
                <span style={detailLabelStyle}>New Price:</span>
                <span style={detailValueStyle}>{formatCurrency(parseFloat(newPrice))}</span>
              </div>

              <div style={{ ...comparisonRowStyle, marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #E2E8F0' }}>
                <span style={detailLabelStyle}>Change:</span>
                <span
                  style={{
                    ...detailValueStyle,
                    color: priceChange >= 0 ? '#10B981' : '#EF4444',
                  }}
                >
                  {priceChange >= 0 ? '+' : ''}{formatCurrency(priceChange)} ({priceChange >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%)
                </span>
              </div>
            </div>
          )}

          {/* New Unrealized Gain Preview */}
          {newGainPreview && (
            <div style={gainPreviewStyle}>
              <p style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '8px', color: '#0F172A' }}>
                New Unrealized Gain
              </p>

              <div style={{ marginBottom: '12px' }}>
                <div style={comparisonRowStyle}>
                  <span style={{ color: '#475569', fontSize: '0.875rem' }}>Current:</span>
                  <span
                    style={{
                      fontWeight: 600,
                      fontFamily: 'monospace',
                      color: currentGainColor,
                      fontSize: '0.875rem',
                    }}
                  >
                    {formatCurrency(holding.unrealizedGain)} ({holding.unrealizedGainPercentage >= 0 ? '+' : ''}{holding.unrealizedGainPercentage.toFixed(2)}%)
                  </span>
                </div>
                <div style={comparisonRowStyle}>
                  <span style={{ color: '#475569', fontSize: '0.875rem' }}>New:</span>
                  <span
                    style={{
                      fontWeight: 600,
                      fontFamily: 'monospace',
                      color: newGainColor,
                      fontSize: '0.875rem',
                    }}
                  >
                    {formatCurrency(newGainPreview.newUnrealizedGain)} ({newGainPreview.newUnrealizedGainPercentage >= 0 ? '+' : ''}{newGainPreview.newUnrealizedGainPercentage.toFixed(2)}%)
                  </span>
                </div>
              </div>

              <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
                At this new price, your holding will show a{' '}
                <strong style={{ color: newGainColor }}>
                  {newGainPreview.newUnrealizedGain >= 0 ? 'gain' : 'loss'} of{' '}
                  {formatCurrency(Math.abs(newGainPreview.newUnrealizedGain))}
                </strong>.
              </p>
            </div>
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
              {isSubmitting ? 'Updating...' : 'Update Price'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
