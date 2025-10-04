import React, { useState } from 'react';
import { Button } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * GiftForm - Modal form for recording lifetime gifts
 *
 * Features:
 * - Gift date, recipient, value
 * - Gift type and description
 * - Exemptions (annual, small gifts, wedding, etc.)
 * - Real-time exemption calculation
 * - Validation
 */
export function GiftForm({ gift, onClose, onSave }) {
  const isEditing = !!gift;

  const [formData, setFormData] = useState({
    giftDate: gift?.giftDate || new Date().toISOString().split('T')[0],
    recipientName: gift?.recipientName || '',
    recipientRelationship: gift?.recipientRelationship || '',
    giftType: gift?.giftType || 'CASH',
    giftDescription: gift?.giftDescription || '',
    giftValue: gift?.giftValue || '',
    currency: gift?.currency || 'GBP',
    claimAnnualExemption: gift?.exemptions?.annualExemption?.claimCurrent ?? true,
    claimPreviousYearExemption: gift?.exemptions?.annualExemption?.claimPreviousYear ?? false,
    claimSmallGiftsExemption: false,
    claimWeddingExemption: false,
    weddingAmount: 0,
    claimNormalExpenditure: false,
  });

  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);
  const [exemptionSummary, setExemptionSummary] = useState(null);

  const relationships = [
    { value: 'SPOUSE', label: 'Spouse/Partner' },
    { value: 'CHILD', label: 'Child' },
    { value: 'GRANDCHILD', label: 'Grandchild' },
    { value: 'PARENT', label: 'Parent' },
    { value: 'SIBLING', label: 'Sibling' },
    { value: 'FRIEND', label: 'Friend' },
    { value: 'CHARITY', label: 'Charity' },
    { value: 'TRUST', label: 'Trust' },
    { value: 'OTHER', label: 'Other' },
  ];

  const giftTypes = [
    { value: 'CASH', label: 'Cash' },
    { value: 'PROPERTY', label: 'Property' },
    { value: 'SHARES', label: 'Shares' },
    { value: 'OTHER_ASSET', label: 'Other Asset' },
  ];

  const currencies = [
    { value: 'GBP', label: 'GBP (£)' },
    { value: 'ZAR', label: 'ZAR (R)' },
    { value: 'USD', label: 'USD ($)' },
    { value: 'EUR', label: 'EUR (€)' },
  ];

  const validateForm = () => {
    const newErrors = {};

    if (!formData.giftDate) {
      newErrors.giftDate = 'Gift date is required';
    }
    if (!formData.recipientName) {
      newErrors.recipientName = 'Recipient name is required';
    }
    if (!formData.giftValue || formData.giftValue <= 0) {
      newErrors.giftValue = 'Gift value must be greater than zero';
    }

    const giftDate = new Date(formData.giftDate);
    const today = new Date();
    if (giftDate > today) {
      newErrors.giftDate = 'Gift date cannot be in the future';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const calculateExemptions = () => {
    const value = parseFloat(formData.giftValue) || 0;
    let remaining = value;
    const exemptions = [];

    // Spouse exemption (unlimited)
    if (formData.recipientRelationship === 'SPOUSE') {
      exemptions.push({ type: 'Spouse exemption', amount: value });
      remaining = 0;
    }
    // Charity exemption (unlimited)
    else if (formData.recipientRelationship === 'CHARITY') {
      exemptions.push({ type: 'Charity exemption', amount: value });
      remaining = 0;
    }
    // Other exemptions
    else {
      // Small gifts exemption (£250)
      if (formData.claimSmallGiftsExemption && value <= 250) {
        exemptions.push({ type: 'Small gifts exemption', amount: value });
        remaining = 0;
      }
      // Annual exemption (£3,000)
      else if (formData.claimAnnualExemption) {
        const annualAmount = Math.min(remaining, 3000);
        if (annualAmount > 0) {
          exemptions.push({ type: 'Annual exemption', amount: annualAmount });
          remaining -= annualAmount;
        }

        // Previous year carry forward
        if (formData.claimPreviousYearExemption && remaining > 0) {
          const carryForward = Math.min(remaining, 3000);
          if (carryForward > 0) {
            exemptions.push({ type: 'Previous year carry forward', amount: carryForward });
            remaining -= carryForward;
          }
        }
      }

      // Wedding exemption
      if (formData.claimWeddingExemption && formData.weddingAmount > 0 && remaining > 0) {
        const weddingAmount = Math.min(remaining, formData.weddingAmount);
        exemptions.push({ type: 'Wedding gift exemption', amount: weddingAmount });
        remaining -= weddingAmount;
      }

      // Normal expenditure out of income
      if (formData.claimNormalExpenditure && remaining > 0) {
        exemptions.push({ type: 'Normal expenditure (requires evidence)', amount: remaining });
        remaining = 0;
      }
    }

    setExemptionSummary({
      totalValue: value,
      totalExemptions: value - remaining,
      taxableValue: remaining,
      exemptions,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setSaving(true);

    try {
      const url = isEditing
        ? `/api/v1/iht/gifts/${gift.id}`
        : '/api/v1/iht/gifts';

      const method = isEditing ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({
          giftDate: formData.giftDate,
          recipient: {
            name: formData.recipientName,
            relationship: formData.recipientRelationship,
          },
          giftType: formData.giftType,
          giftDescription: formData.giftDescription,
          giftValue: parseFloat(formData.giftValue),
          currency: formData.currency,
          exemptions: {
            annualExemption: {
              claimCurrent: formData.claimAnnualExemption,
              claimPreviousYear: formData.claimPreviousYearExemption,
            },
            smallGiftsExemption: formData.claimSmallGiftsExemption,
            weddingGiftExemption: {
              applicable: formData.claimWeddingExemption,
              amount: formData.weddingAmount,
            },
            normalExpenditureOutOfIncome: formData.claimNormalExpenditure,
            spouseExemption: formData.recipientRelationship === 'SPOUSE',
            charityExemption: formData.recipientRelationship === 'CHARITY',
          },
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save gift');
      }

      const savedGift = await response.json();
      onSave(savedGift);
      onClose();
    } catch (err) {
      console.error('Error saving gift:', err);
      alert(err.message || 'Failed to save gift. Please try again.');
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

  // Auto-calculate wedding exemption based on relationship
  const handleRelationshipChange = (relationship) => {
    handleChange('recipientRelationship', relationship);

    // Auto-set wedding amount if wedding exemption is claimed
    if (formData.claimWeddingExemption) {
      if (relationship === 'CHILD') {
        handleChange('weddingAmount', 5000);
      } else if (relationship === 'GRANDCHILD') {
        handleChange('weddingAmount', 2500);
      } else {
        handleChange('weddingAmount', 1000);
      }
    }
  };

  // Recalculate exemptions when relevant fields change
  React.useEffect(() => {
    if (formData.giftValue && formData.recipientRelationship) {
      calculateExemptions();
    }
  }, [
    formData.giftValue,
    formData.recipientRelationship,
    formData.claimAnnualExemption,
    formData.claimPreviousYearExemption,
    formData.claimSmallGiftsExemption,
    formData.claimWeddingExemption,
    formData.weddingAmount,
    formData.claimNormalExpenditure,
  ]);

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

  const exemptionBoxStyle = {
    padding: '16px',
    backgroundColor: '#ECFDF5',
    border: '1px solid #A7F3D0',
    borderRadius: '8px',
    marginTop: '16px',
  };

  const formatCurrency = (amount) => {
    return `£${amount.toLocaleString('en-GB', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
  };

  return (
    <div style={modalOverlayStyle} onClick={onClose}>
      <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
        <h2 style={modalHeaderStyle}>
          {isEditing ? 'Edit Gift' : 'Record Gift'}
        </h2>

        <form onSubmit={handleSubmit}>
          {/* Gift Date */}
          <div style={formGroupStyle}>
            <label htmlFor="giftDate" style={labelStyle}>
              Gift Date *
            </label>
            <input
              type="date"
              id="giftDate"
              value={formData.giftDate}
              onChange={(e) => handleChange('giftDate', e.target.value)}
              max={new Date().toISOString().split('T')[0]}
              style={{ ...inputStyle, ...(errors.giftDate ? { borderColor: '#EF4444' } : {}) }}
              required
            />
            {errors.giftDate && <div style={errorStyle}>{errors.giftDate}</div>}
          </div>

          {/* Recipient Name */}
          <div style={formGroupStyle}>
            <label htmlFor="recipientName" style={labelStyle}>
              Recipient Name *
            </label>
            <input
              type="text"
              id="recipientName"
              value={formData.recipientName}
              onChange={(e) => handleChange('recipientName', e.target.value)}
              placeholder="e.g., John Smith"
              style={{ ...inputStyle, ...(errors.recipientName ? { borderColor: '#EF4444' } : {}) }}
              required
            />
            {errors.recipientName && <div style={errorStyle}>{errors.recipientName}</div>}
          </div>

          {/* Relationship */}
          <div style={formGroupStyle}>
            <label htmlFor="recipientRelationship" style={labelStyle}>
              Relationship to You
            </label>
            <select
              id="recipientRelationship"
              value={formData.recipientRelationship}
              onChange={(e) => handleRelationshipChange(e.target.value)}
              style={inputStyle}
            >
              <option value="">Select relationship</option>
              {relationships.map((rel) => (
                <option key={rel.value} value={rel.value}>
                  {rel.label}
                </option>
              ))}
            </select>
          </div>

          {/* Gift Type */}
          <div style={formGroupStyle}>
            <label htmlFor="giftType" style={labelStyle}>
              Gift Type
            </label>
            <select
              id="giftType"
              value={formData.giftType}
              onChange={(e) => handleChange('giftType', e.target.value)}
              style={inputStyle}
            >
              {giftTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Description */}
          <div style={formGroupStyle}>
            <label htmlFor="giftDescription" style={labelStyle}>
              Description (Optional)
            </label>
            <input
              type="text"
              id="giftDescription"
              value={formData.giftDescription}
              onChange={(e) => handleChange('giftDescription', e.target.value)}
              placeholder="e.g., Birthday gift, Wedding gift"
              style={inputStyle}
            />
          </div>

          {/* Gift Value and Currency */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '12px', marginBottom: '20px' }}>
            <div>
              <label htmlFor="giftValue" style={labelStyle}>
                Gift Value *
              </label>
              <input
                type="number"
                id="giftValue"
                value={formData.giftValue}
                onChange={(e) => handleChange('giftValue', e.target.value)}
                placeholder="0"
                step="0.01"
                style={{ ...inputStyle, ...(errors.giftValue ? { borderColor: '#EF4444' } : {}) }}
                required
              />
              {errors.giftValue && <div style={errorStyle}>{errors.giftValue}</div>}
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

          {/* Exemptions */}
          <div style={{ ...formGroupStyle, padding: '16px', backgroundColor: '#F8FAFC', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#0F172A', marginBottom: '12px' }}>
              Exemptions to Apply
            </div>

            {/* Disable exemptions for spouse/charity */}
            {formData.recipientRelationship === 'SPOUSE' && (
              <div style={{ fontSize: '0.875rem', color: '#10B981', marginBottom: '12px' }}>
                ✓ Spouse exemption (unlimited) - fully exempt
              </div>
            )}
            {formData.recipientRelationship === 'CHARITY' && (
              <div style={{ fontSize: '0.875rem', color: '#10B981', marginBottom: '12px' }}>
                ✓ Charity exemption (unlimited) - fully exempt
              </div>
            )}

            {formData.recipientRelationship !== 'SPOUSE' && formData.recipientRelationship !== 'CHARITY' && (
              <>
                <label style={checkboxLabelStyle}>
                  <input
                    type="checkbox"
                    checked={formData.claimAnnualExemption}
                    onChange={(e) => handleChange('claimAnnualExemption', e.target.checked)}
                    style={checkboxStyle}
                  />
                  Use annual exemption (£3,000)
                </label>

                {formData.claimAnnualExemption && (
                  <label style={{ ...checkboxLabelStyle, marginLeft: '24px' }}>
                    <input
                      type="checkbox"
                      checked={formData.claimPreviousYearExemption}
                      onChange={(e) => handleChange('claimPreviousYearExemption', e.target.checked)}
                      style={checkboxStyle}
                    />
                    Carry forward from previous year
                  </label>
                )}

                <label style={checkboxLabelStyle}>
                  <input
                    type="checkbox"
                    checked={formData.claimSmallGiftsExemption}
                    onChange={(e) => handleChange('claimSmallGiftsExemption', e.target.checked)}
                    style={checkboxStyle}
                  />
                  Small gifts exemption (≤£250)
                </label>

                <label style={checkboxLabelStyle}>
                  <input
                    type="checkbox"
                    checked={formData.claimWeddingExemption}
                    onChange={(e) => {
                      handleChange('claimWeddingExemption', e.target.checked);
                      if (e.target.checked) {
                        // Auto-set amount based on relationship
                        if (formData.recipientRelationship === 'CHILD') {
                          handleChange('weddingAmount', 5000);
                        } else if (formData.recipientRelationship === 'GRANDCHILD') {
                          handleChange('weddingAmount', 2500);
                        } else {
                          handleChange('weddingAmount', 1000);
                        }
                      }
                    }}
                    style={checkboxStyle}
                  />
                  Wedding/civil partnership gift
                </label>

                <label style={checkboxLabelStyle}>
                  <input
                    type="checkbox"
                    checked={formData.claimNormalExpenditure}
                    onChange={(e) => handleChange('claimNormalExpenditure', e.target.checked)}
                    style={checkboxStyle}
                  />
                  Normal expenditure out of income (requires evidence)
                </label>
              </>
            )}
          </div>

          {/* Exemption Summary */}
          {exemptionSummary && (
            <div style={exemptionBoxStyle}>
              <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#065F46', marginBottom: '8px' }}>
                Exemption Summary
              </div>

              <div style={{ fontSize: '0.875rem', color: '#064E3B', lineHeight: '1.7' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span>Gift value:</span>
                  <span style={{ fontFamily: 'monospace' }}>{formatCurrency(exemptionSummary.totalValue)}</span>
                </div>

                {exemptionSummary.exemptions.map((exemption, index) => (
                  <div key={index} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span>- {exemption.type}:</span>
                    <span style={{ fontFamily: 'monospace', color: '#10B981' }}>
                      -{formatCurrency(exemption.amount)}
                    </span>
                  </div>
                ))}

                <div style={{ borderTop: '1px solid #A7F3D0', marginTop: '8px', paddingTop: '8px', display: 'flex', justifyContent: 'space-between', fontWeight: 600 }}>
                  <span>Taxable value:</span>
                  <span style={{ fontFamily: 'monospace', color: exemptionSummary.taxableValue > 0 ? '#F59E0B' : '#10B981' }}>
                    {formatCurrency(exemptionSummary.taxableValue)}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div style={buttonGroupStyle}>
            <Button variant="outline" onClick={onClose} disabled={saving}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={saving}>
              {saving ? 'Saving...' : isEditing ? 'Update Gift' : 'Record Gift'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
