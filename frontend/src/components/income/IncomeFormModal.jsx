import React, { useState, useEffect } from 'react';
import { Button, Input, Label, Select, Card } from 'internal-packages/ui';
import { getIncomeTypeLabel } from '../../utils/income';

export function IncomeFormModal({ income, onSave, onCancel, loading }) {
  const isEditing = !!income;

  const [formData, setFormData] = useState({
    incomeType: '',
    sourceCountry: 'UK',
    description: '',
    relatedEntity: '',
    amount: '',
    currency: 'GBP',
    frequency: 'annual',
    startDate: '',
    endDate: '',
    isGross: true,
    taxWithheldAtSource: '',
    payeReference: '',
    isForeign: false,
    foreignTaxCredit: '',
  });

  const [errors, setErrors] = useState({});
  const [showTaxWithheld, setShowTaxWithheld] = useState(false);

  useEffect(() => {
    if (income) {
      setFormData({
        incomeType: income.income_type || income.incomeType || '',
        sourceCountry: income.source_country || income.sourceCountry || 'UK',
        description: income.description || '',
        relatedEntity: income.related_entity || income.relatedEntity || '',
        amount: income.amount?.toString() || '',
        currency: income.currency || 'GBP',
        frequency: income.frequency || 'annual',
        startDate: income.start_date || income.startDate || '',
        endDate: income.end_date || income.endDate || '',
        isGross: income.is_gross !== undefined ? income.is_gross : (income.isGross !== undefined ? income.isGross : true),
        taxWithheldAtSource: income.tax_withheld_at_source?.toString() || income.taxWithheldAtSource?.toString() || '',
        payeReference: income.paye_reference || income.payeReference || '',
        isForeign: (income.source_country || income.sourceCountry) !== 'UK' && (income.source_country || income.sourceCountry) !== 'ZA',
        foreignTaxCredit: '',
      });

      if (income.tax_withheld_at_source || income.taxWithheldAtSource) {
        setShowTaxWithheld(true);
      }
    }
  }, [income]);

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  const handleCountryChange = (country) => {
    handleChange('sourceCountry', country);
    handleChange('isForeign', country !== 'UK' && country !== 'ZA');
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.incomeType) {
      newErrors.incomeType = 'Income type is required';
    }

    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      newErrors.amount = 'Amount must be greater than 0';
    }

    if (!formData.currency) {
      newErrors.currency = 'Currency is required';
    }

    if (!formData.startDate) {
      newErrors.startDate = 'Start date is required';
    }

    if (formData.taxWithheldAtSource && parseFloat(formData.taxWithheldAtSource) > parseFloat(formData.amount)) {
      newErrors.taxWithheldAtSource = 'Tax withheld cannot exceed income amount';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    const submitData = {
      incomeType: formData.incomeType,
      sourceCountry: formData.sourceCountry,
      description: formData.description,
      relatedEntity: formData.relatedEntity,
      amount: parseFloat(formData.amount),
      currency: formData.currency,
      frequency: formData.frequency,
      startDate: formData.startDate,
      endDate: formData.endDate || null,
      isGross: formData.isGross,
      taxWithheldAtSource: formData.taxWithheldAtSource ? parseFloat(formData.taxWithheldAtSource) : null,
      payeReference: formData.payeReference || null,
    };

    onSave(submitData);
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
    boxShadow: '0 10px 15px rgba(0, 0, 0, 0.1)',
    maxWidth: '800px',
    width: '100%',
    maxHeight: '90vh',
    overflow: 'auto',
    padding: '32px',
  };

  const modalHeaderStyle = {
    fontSize: '1.5rem',
    fontWeight: 700,
    color: '#0F172A',
    marginBottom: '8px',
  };

  const modalDescStyle = {
    color: '#64748B',
    fontSize: '0.95rem',
    marginBottom: '32px',
    lineHeight: '1.7',
  };

  const formGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    marginBottom: '24px',
  };

  const formGroupStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  };

  const errorStyle = {
    color: '#EF4444',
    fontSize: '0.875rem',
    marginTop: '4px',
  };

  const helpTextStyle = {
    fontSize: '0.875rem',
    color: '#64748B',
    marginTop: '4px',
  };

  const calloutStyle = {
    backgroundColor: '#EFF6FF',
    border: '1px solid #BFDBFE',
    borderLeft: '4px solid #3B82F6',
    padding: '16px',
    borderRadius: '8px',
    marginBottom: '24px',
  };

  const actionsStyle = {
    display: 'flex',
    gap: '12px',
    justifyContent: 'flex-end',
    marginTop: '32px',
    paddingTop: '24px',
    borderTop: '1px solid #E2E8F0',
  };

  const incomeTypes = [
    { value: 'employment', label: 'Employment' },
    { value: 'self_employment', label: 'Self-Employment' },
    { value: 'rental', label: 'Rental Income' },
    { value: 'dividend', label: 'Dividend Income' },
    { value: 'interest', label: 'Interest Income' },
    { value: 'investment', label: 'Investment Income' },
    { value: 'pension', label: 'Pension' },
    { value: 'capital_gains', label: 'Capital Gains' },
    { value: 'other', label: 'Other Income' },
  ];

  const countries = [
    { value: 'UK', label: 'United Kingdom' },
    { value: 'ZA', label: 'South Africa' },
    { value: 'US', label: 'United States' },
    { value: 'EU', label: 'European Union' },
    { value: 'OTHER', label: 'Other' },
  ];

  const currencies = [
    { value: 'GBP', label: 'GBP (£)' },
    { value: 'ZAR', label: 'ZAR (R)' },
    { value: 'USD', label: 'USD ($)' },
    { value: 'EUR', label: 'EUR (€)' },
  ];

  const frequencies = [
    { value: 'annual', label: 'Annually' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'quarterly', label: 'Quarterly' },
    { value: 'one_time', label: 'One-time' },
  ];

  return (
    <div style={modalOverlayStyle} onClick={onCancel}>
      <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
        <h2 style={modalHeaderStyle}>
          {isEditing ? 'Edit income entry' : 'Add income entry'}
        </h2>
        <p style={modalDescStyle}>
          Record your income to track earnings and tax obligations across the UK and South Africa.
          We'll automatically convert amounts and calculate tax treatment.
        </p>

        <form onSubmit={handleSubmit}>
          {/* Income Type */}
          <div style={formGridStyle}>
            <div style={formGroupStyle}>
              <Label>
                Income Type <span style={{ color: '#EF4444' }}>*</span>
              </Label>
              <Select
                value={formData.incomeType}
                onChange={(e) => handleChange('incomeType', e.target.value)}
              >
                <option value="">Select income type</option>
                {incomeTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </Select>
              {errors.incomeType && <div style={errorStyle}>{errors.incomeType}</div>}
            </div>

            <div style={formGroupStyle}>
              <Label>
                Source Country <span style={{ color: '#EF4444' }}>*</span>
              </Label>
              <Select
                value={formData.sourceCountry}
                onChange={(e) => handleCountryChange(e.target.value)}
              >
                {countries.map((country) => (
                  <option key={country.value} value={country.value}>
                    {country.label}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          {/* Foreign Income Callout */}
          {formData.isForeign && (
            <div style={calloutStyle}>
              <p style={{ fontWeight: 600, color: '#1E40AF', marginBottom: '4px' }}>
                Foreign income detected
              </p>
              <p style={{ fontSize: '0.875rem', color: '#475569', lineHeight: '1.6' }}>
                Income from outside the UK and SA. We'll calculate tax treatment under Double Tax
                Agreements to prevent you from being taxed twice on the same income.
              </p>
            </div>
          )}

          {/* Description and Entity */}
          <div style={formGridStyle}>
            <div style={formGroupStyle}>
              <Label>Description</Label>
              <Input
                type="text"
                placeholder="e.g., Monthly salary, Rental from property A"
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
              />
              <div style={helpTextStyle}>Brief description of this income</div>
            </div>

            <div style={formGroupStyle}>
              <Label>
                {formData.incomeType === 'employment'
                  ? 'Employer Name'
                  : formData.incomeType === 'rental'
                  ? 'Property Reference'
                  : 'Source/Entity'}
              </Label>
              <Input
                type="text"
                placeholder={
                  formData.incomeType === 'employment'
                    ? 'e.g., ABC Company Ltd'
                    : 'e.g., Property A, Portfolio 1'
                }
                value={formData.relatedEntity}
                onChange={(e) => handleChange('relatedEntity', e.target.value)}
              />
            </div>
          </div>

          {/* Amount and Currency */}
          <div style={formGridStyle}>
            <div style={formGroupStyle}>
              <Label>
                Amount <span style={{ color: '#EF4444' }}>*</span>
              </Label>
              <Input
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={formData.amount}
                onChange={(e) => handleChange('amount', e.target.value)}
              />
              {errors.amount && <div style={errorStyle}>{errors.amount}</div>}
              <div style={helpTextStyle}>Enter the amount in the currency you received it</div>
            </div>

            <div style={formGroupStyle}>
              <Label>
                Currency <span style={{ color: '#EF4444' }}>*</span>
              </Label>
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

            <div style={formGroupStyle}>
              <Label>
                Frequency <span style={{ color: '#EF4444' }}>*</span>
              </Label>
              <Select
                value={formData.frequency}
                onChange={(e) => handleChange('frequency', e.target.value)}
              >
                {frequencies.map((freq) => (
                  <option key={freq.value} value={freq.value}>
                    {freq.label}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          {/* Dates */}
          <div style={formGridStyle}>
            <div style={formGroupStyle}>
              <Label>
                Start Date <span style={{ color: '#EF4444' }}>*</span>
              </Label>
              <Input
                type="date"
                value={formData.startDate}
                onChange={(e) => handleChange('startDate', e.target.value)}
              />
              {errors.startDate && <div style={errorStyle}>{errors.startDate}</div>}
            </div>

            <div style={formGroupStyle}>
              <Label>End Date (Optional)</Label>
              <Input
                type="date"
                value={formData.endDate}
                onChange={(e) => handleChange('endDate', e.target.value)}
              />
              <div style={helpTextStyle}>Leave blank if ongoing</div>
            </div>
          </div>

          {/* Gross/Net Toggle */}
          <div style={{ marginBottom: '24px' }}>
            <Label>Income Type</Label>
            <div style={{ display: 'flex', gap: '16px', marginTop: '8px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="isGross"
                  checked={formData.isGross === true}
                  onChange={() => handleChange('isGross', true)}
                />
                <span>Gross (before tax)</span>
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="isGross"
                  checked={formData.isGross === false}
                  onChange={() => handleChange('isGross', false)}
                />
                <span>Net (after tax)</span>
              </label>
            </div>
            <div style={helpTextStyle}>
              Gross = before tax, Net = after tax. Choose gross for accurate tax calculations.
            </div>
          </div>

          {/* Tax Withheld Section */}
          <div style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <input
                type="checkbox"
                id="showTaxWithheld"
                checked={showTaxWithheld}
                onChange={(e) => setShowTaxWithheld(e.target.checked)}
              />
              <Label htmlFor="showTaxWithheld" style={{ margin: 0 }}>
                Tax withheld at source (PAYE, PASE, etc.)
              </Label>
            </div>

            {showTaxWithheld && (
              <div style={formGridStyle}>
                <div style={formGroupStyle}>
                  <Label>Tax Withheld Amount</Label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="0.00"
                    value={formData.taxWithheldAtSource}
                    onChange={(e) => handleChange('taxWithheldAtSource', e.target.value)}
                  />
                  {errors.taxWithheldAtSource && (
                    <div style={errorStyle}>{errors.taxWithheldAtSource}</div>
                  )}
                  <div style={helpTextStyle}>
                    Tax already deducted (PAYE in UK, PASE in SA)
                  </div>
                </div>

                {formData.incomeType === 'employment' && (
                  <div style={formGroupStyle}>
                    <Label>PAYE Reference (Optional)</Label>
                    <Input
                      type="text"
                      placeholder="e.g., 123/AB12345"
                      value={formData.payeReference}
                      onChange={(e) => handleChange('payeReference', e.target.value)}
                    />
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Actions */}
          <div style={actionsStyle}>
            <Button variant="secondary" onClick={onCancel} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? 'Saving...' : isEditing ? 'Update Income' : 'Add Income'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
