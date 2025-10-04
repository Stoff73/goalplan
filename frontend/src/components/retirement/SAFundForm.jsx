import React, { useState, useEffect } from 'react';
import { Button, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * SAFundForm - Form for adding/editing SA retirement funds
 *
 * Features:
 * - Multi-step form with clear guidance
 * - Fund type selector with explanatory text
 * - Asset allocation with Regulation 28 compliance checking
 * - Client-side validation
 * - Narrative explanations for each field
 *
 * Follows STYLEGUIDE.md:
 * - Clear, descriptive labels
 * - Help text below inputs
 * - Conversational error messages
 * - Progressive disclosure for advanced options
 */
export function SAFundForm({ fundId, onSuccess, onCancel }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});

  // Form state
  const [formData, setFormData] = useState({
    fundType: '',
    provider: '',
    fundName: '',
    employerName: '',
    memberNumber: '',
    currentValue: '',
    currency: 'ZAR',
    monthlyContribution: '',
    employerContribution: '',
    portfolioName: '',
    equityPercentage: '',
    bondsPercentage: '',
    cashPercentage: '',
    propertyPercentage: '',
    offshorePercentage: '',
    startDate: '',
    expectedRetirementAge: '',
    // Preservation fund fields
    sourceFundType: '',
    transferDate: '',
    withdrawalTaken: false,
    withdrawalDate: '',
    withdrawalAmount: '',
    // Provident fund fields
    contributionsBeforeMarch2021: '',
    contributionsAfterMarch2021: '',
  });

  // Load existing fund data if editing
  useEffect(() => {
    if (fundId) {
      loadFund();
    }
  }, [fundId]);

  const loadFund = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/retirement/sa-funds/${fundId}`, {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load fund');
      }

      const data = await response.json();
      setFormData({
        fundType: data.fundType || '',
        provider: data.provider || '',
        fundName: data.fundName || '',
        employerName: data.employerName || '',
        memberNumber: data.memberNumber || '',
        currentValue: data.currentValue || '',
        currency: data.currency || 'ZAR',
        monthlyContribution: data.monthlyContribution || '',
        employerContribution: data.employerContribution || '',
        portfolioName: data.portfolioName || '',
        equityPercentage: data.assetAllocation?.equityPercentage || '',
        bondsPercentage: data.assetAllocation?.bondsPercentage || '',
        cashPercentage: data.assetAllocation?.cashPercentage || '',
        propertyPercentage: data.assetAllocation?.propertyPercentage || '',
        offshorePercentage: data.assetAllocation?.offshorePercentage || '',
        startDate: data.startDate || '',
        expectedRetirementAge: data.expectedRetirementAge || '',
        sourceFundType: data.sourceFundType || '',
        transferDate: data.transferDate || '',
        withdrawalTaken: data.withdrawalTaken || false,
        withdrawalDate: data.withdrawalDate || '',
        withdrawalAmount: data.withdrawalAmount || '',
        contributionsBeforeMarch2021: data.contributionsBeforeMarch2021 || '',
        contributionsAfterMarch2021: data.contributionsAfterMarch2021 || '',
      });
    } catch (err) {
      setError('Failed to load fund details. Please try again.');
      console.error('Error loading fund:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validateStep = (stepNumber) => {
    const errors = {};

    if (stepNumber === 1) {
      if (!formData.fundType) {
        errors.fundType = 'Please select a fund type';
      }
    } else if (stepNumber === 2) {
      if (!formData.provider) {
        errors.provider = 'Provider name is required';
      }
      if (!formData.fundName) {
        errors.fundName = 'Fund name is required';
      }
    } else if (stepNumber === 3) {
      if (!formData.currentValue || parseFloat(formData.currentValue) < 0) {
        errors.currentValue = 'Please enter a valid fund value';
      }
    } else if (stepNumber === 4) {
      const total =
        parseFloat(formData.equityPercentage || 0) +
        parseFloat(formData.bondsPercentage || 0) +
        parseFloat(formData.cashPercentage || 0) +
        parseFloat(formData.propertyPercentage || 0) +
        parseFloat(formData.offshorePercentage || 0);

      if (total !== 100 && total !== 0) {
        errors.assetAllocation = `Asset allocation must total 100%. Current total: ${total}%`;
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(step)) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    setStep(step - 1);
  };

  const handleSubmit = async () => {
    if (!validateStep(step)) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const url = fundId
        ? `/api/v1/retirement/sa-funds/${fundId}`
        : '/api/v1/retirement/sa-funds';

      const method = fundId ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({
          fundType: formData.fundType,
          provider: formData.provider,
          fundName: formData.fundName,
          employerName: formData.employerName,
          memberNumber: formData.memberNumber,
          currentValue: parseFloat(formData.currentValue),
          currency: formData.currency,
          contributionDetails: {
            employeeContribution: {
              amount: parseFloat(formData.monthlyContribution || 0),
              frequency: 'MONTHLY',
            },
            employerContribution: {
              amount: parseFloat(formData.employerContribution || 0),
              frequency: 'MONTHLY',
            },
          },
          investmentChoice: {
            portfolioName: formData.portfolioName,
            assetAllocation: {
              equityPercentage: parseFloat(formData.equityPercentage || 0),
              bondsPercentage: parseFloat(formData.bondsPercentage || 0),
              cashPercentage: parseFloat(formData.cashPercentage || 0),
              propertyPercentage: parseFloat(formData.propertyPercentage || 0),
              offshorePercentage: parseFloat(formData.offshorePercentage || 0),
            },
          },
          startDate: formData.startDate,
          expectedRetirementAge: parseInt(formData.expectedRetirementAge),
          // Preservation fund fields
          ...(formData.fundType.includes('PRESERVATION') && {
            preservationFundSource: formData.sourceFundType,
            transferDate: formData.transferDate,
            withdrawalTaken: formData.withdrawalTaken,
            withdrawalDate: formData.withdrawalDate,
            withdrawalAmount: parseFloat(formData.withdrawalAmount || 0),
          }),
          // Provident fund fields
          ...(formData.fundType === 'PROVIDENT_FUND' && {
            contributionsBeforeMarch2021: parseFloat(formData.contributionsBeforeMarch2021 || 0),
            contributionsAfterMarch2021: parseFloat(formData.contributionsAfterMarch2021 || 0),
          }),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to save fund');
      }

      onSuccess();
    } catch (err) {
      setError(err.message || 'Failed to save fund. Please try again.');
      console.error('Error saving fund:', err);
    } finally {
      setLoading(false);
    }
  };

  // Check Regulation 28 compliance
  const checkRegulation28 = () => {
    const equity = parseFloat(formData.equityPercentage || 0);
    const offshore = parseFloat(formData.offshorePercentage || 0);
    const property = parseFloat(formData.propertyPercentage || 0);

    const violations = [];
    if (equity > 75) {
      violations.push(`Equity ${equity}% exceeds 75% limit`);
    }
    if (offshore > 30) {
      violations.push(`Offshore ${offshore}% exceeds 30% limit`);
    }
    if (property > 25) {
      violations.push(`Property ${property}% exceeds 25% limit`);
    }

    return violations;
  };

  const regulation28Violations = checkRegulation28();

  // Styles
  const formGroupStyle = {
    marginBottom: '24px',
  };

  const labelStyle = {
    display: 'block',
    fontSize: '0.875rem',
    fontWeight: 500,
    color: '#0F172A',
    marginBottom: '8px',
  };

  const inputStyle = {
    width: '100%',
    padding: '12px',
    fontSize: '1rem',
    border: '1px solid #CBD5E1',
    borderRadius: '8px',
    transition: 'border-color 150ms ease-in-out',
  };

  const helpTextStyle = {
    fontSize: '0.875rem',
    color: '#64748B',
    marginTop: '4px',
    lineHeight: '1.5',
  };

  const errorTextStyle = {
    fontSize: '0.875rem',
    color: '#EF4444',
    marginTop: '4px',
  };

  const fundTypeCardStyle = (isSelected) => ({
    padding: '16px',
    border: isSelected ? '2px solid #F59E0B' : '1px solid #CBD5E1',
    borderRadius: '8px',
    cursor: 'pointer',
    backgroundColor: isSelected ? '#FFFBEB' : '#FFFFFF',
    transition: 'all 150ms ease-in-out',
    marginBottom: '12px',
  });

  const buttonContainerStyle = {
    display: 'flex',
    gap: '12px',
    justifyContent: 'space-between',
    marginTop: '32px',
    paddingTop: '24px',
    borderTop: '1px solid #E2E8F0',
  };

  const stepIndicatorStyle = {
    display: 'flex',
    gap: '8px',
    marginBottom: '32px',
    justifyContent: 'center',
  };

  const stepDotStyle = (isActive, isComplete) => ({
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    backgroundColor: isComplete || isActive ? '#F59E0B' : '#CBD5E1',
    transition: 'all 150ms ease-in-out',
  });

  const isPreservationFund = formData.fundType.includes('PRESERVATION');
  const isProvidentFund = formData.fundType === 'PROVIDENT_FUND';

  if (loading && fundId) {
    return (
      <div style={{ textAlign: 'center', padding: '48px' }}>
        <p style={{ color: '#64748B' }}>Loading fund details...</p>
      </div>
    );
  }

  return (
    <div>
      {/* Step Indicator */}
      <div style={stepIndicatorStyle}>
        {[1, 2, 3, 4, 5].map((s) => (
          <div key={s} style={stepDotStyle(s === step, s < step)} />
        ))}
      </div>

      {error && (
        <Alert variant="error" style={{ marginBottom: '24px' }}>
          {error}
        </Alert>
      )}

      {/* Step 1: Fund Type */}
      {step === 1 && (
        <div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px' }}>
            What type of retirement fund is this?
          </h3>
          <p style={{ color: '#64748B', marginBottom: '24px', lineHeight: '1.7' }}>
            Select the type that matches your fund. Each type has different tax treatment and withdrawal rules.
          </p>

          <div
            style={fundTypeCardStyle(formData.fundType === 'PENSION_FUND')}
            onClick={() => handleChange('fundType', 'PENSION_FUND')}
          >
            <h4 style={{ fontWeight: 600, marginBottom: '4px' }}>Pension Fund</h4>
            <p style={{ fontSize: '0.875rem', color: '#64748B' }}>
              Employer-sponsored fund. At retirement, max 1/3 lump sum, min 2/3 to annuity.
            </p>
          </div>

          <div
            style={fundTypeCardStyle(formData.fundType === 'PROVIDENT_FUND')}
            onClick={() => handleChange('fundType', 'PROVIDENT_FUND')}
          >
            <h4 style={{ fontWeight: 600, marginBottom: '4px' }}>Provident Fund</h4>
            <p style={{ fontSize: '0.875rem', color: '#64748B' }}>
              Employer-sponsored fund. Post-March 2021 contributions follow pension fund rules.
            </p>
          </div>

          <div
            style={fundTypeCardStyle(formData.fundType === 'RETIREMENT_ANNUITY')}
            onClick={() => handleChange('fundType', 'RETIREMENT_ANNUITY')}
          >
            <h4 style={{ fontWeight: 600, marginBottom: '4px' }}>Retirement Annuity (RA)</h4>
            <p style={{ fontSize: '0.875rem', color: '#64748B' }}>
              Personal retirement savings. Same withdrawal rules as pension funds.
            </p>
          </div>

          <div
            style={fundTypeCardStyle(formData.fundType === 'PRESERVATION_FUND_PENSION')}
            onClick={() => handleChange('fundType', 'PRESERVATION_FUND_PENSION')}
          >
            <h4 style={{ fontWeight: 600, marginBottom: '4px' }}>Preservation Fund (Pension)</h4>
            <p style={{ fontSize: '0.875rem', color: '#64748B' }}>
              Transferred from a pension fund. One withdrawal allowed before retirement.
            </p>
          </div>

          <div
            style={fundTypeCardStyle(formData.fundType === 'PRESERVATION_FUND_PROVIDENT')}
            onClick={() => handleChange('fundType', 'PRESERVATION_FUND_PROVIDENT')}
          >
            <h4 style={{ fontWeight: 600, marginBottom: '4px' }}>Preservation Fund (Provident)</h4>
            <p style={{ fontSize: '0.875rem', color: '#64748B' }}>
              Transferred from a provident fund. One withdrawal allowed before retirement.
            </p>
          </div>

          {validationErrors.fundType && (
            <p style={errorTextStyle}>{validationErrors.fundType}</p>
          )}
        </div>
      )}

      {/* Step 2: Provider & Details */}
      {step === 2 && (
        <div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px' }}>
            Fund provider and details
          </h3>

          <div style={formGroupStyle}>
            <label style={labelStyle}>Provider name *</label>
            <input
              type="text"
              value={formData.provider}
              onChange={(e) => handleChange('provider', e.target.value)}
              style={inputStyle}
              placeholder="e.g., Old Mutual, Allan Gray, Sanlam"
            />
            {validationErrors.provider && (
              <p style={errorTextStyle}>{validationErrors.provider}</p>
            )}
          </div>

          <div style={formGroupStyle}>
            <label style={labelStyle}>Fund name *</label>
            <input
              type="text"
              value={formData.fundName}
              onChange={(e) => handleChange('fundName', e.target.value)}
              style={inputStyle}
              placeholder="e.g., Balanced Fund, High Equity Portfolio"
            />
            {validationErrors.fundName && (
              <p style={errorTextStyle}>{validationErrors.fundName}</p>
            )}
          </div>

          {!isPreservationFund && (
            <div style={formGroupStyle}>
              <label style={labelStyle}>Employer name (if applicable)</label>
              <input
                type="text"
                value={formData.employerName}
                onChange={(e) => handleChange('employerName', e.target.value)}
                style={inputStyle}
                placeholder="Your employer's name"
              />
              <p style={helpTextStyle}>
                For employer-sponsored pension or provident funds
              </p>
            </div>
          )}

          <div style={formGroupStyle}>
            <label style={labelStyle}>Member number</label>
            <input
              type="text"
              value={formData.memberNumber}
              onChange={(e) => handleChange('memberNumber', e.target.value)}
              style={inputStyle}
              placeholder="Your fund member number"
            />
          </div>

          <div style={formGroupStyle}>
            <label style={labelStyle}>Start date</label>
            <input
              type="date"
              value={formData.startDate}
              onChange={(e) => handleChange('startDate', e.target.value)}
              style={inputStyle}
            />
          </div>
        </div>
      )}

      {/* Step 3: Value & Contributions */}
      {step === 3 && (
        <div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px' }}>
            Current value and contributions
          </h3>

          <div style={formGroupStyle}>
            <label style={labelStyle}>Current fund value *</label>
            <input
              type="number"
              value={formData.currentValue}
              onChange={(e) => handleChange('currentValue', e.target.value)}
              style={inputStyle}
              placeholder="0"
            />
            <p style={helpTextStyle}>
              The latest value shown on your fund statement
            </p>
            {validationErrors.currentValue && (
              <p style={errorTextStyle}>{validationErrors.currentValue}</p>
            )}
          </div>

          {!isPreservationFund && (
            <>
              <div style={formGroupStyle}>
                <label style={labelStyle}>Your monthly contribution</label>
                <input
                  type="number"
                  value={formData.monthlyContribution}
                  onChange={(e) => handleChange('monthlyContribution', e.target.value)}
                  style={inputStyle}
                  placeholder="0"
                />
                <p style={helpTextStyle}>
                  How much you contribute each month
                </p>
              </div>

              <div style={formGroupStyle}>
                <label style={labelStyle}>Employer monthly contribution</label>
                <input
                  type="number"
                  value={formData.employerContribution}
                  onChange={(e) => handleChange('employerContribution', e.target.value)}
                  style={inputStyle}
                  placeholder="0"
                />
                <p style={helpTextStyle}>
                  How much your employer contributes each month (if applicable)
                </p>
              </div>
            </>
          )}

          {isProvidentFund && (
            <>
              <div style={formGroupStyle}>
                <label style={labelStyle}>Contributions before 1 March 2021</label>
                <input
                  type="number"
                  value={formData.contributionsBeforeMarch2021}
                  onChange={(e) => handleChange('contributionsBeforeMarch2021', e.target.value)}
                  style={inputStyle}
                  placeholder="0"
                />
                <p style={helpTextStyle}>
                  Full cash withdrawal allowed for these contributions
                </p>
              </div>

              <div style={formGroupStyle}>
                <label style={labelStyle}>Contributions after 1 March 2021</label>
                <input
                  type="number"
                  value={formData.contributionsAfterMarch2021}
                  onChange={(e) => handleChange('contributionsAfterMarch2021', e.target.value)}
                  style={inputStyle}
                  placeholder="0"
                />
                <p style={helpTextStyle}>
                  Subject to 1/3 lump sum, 2/3 annuity rule
                </p>
              </div>
            </>
          )}

          {isPreservationFund && (
            <>
              <div style={formGroupStyle}>
                <label style={labelStyle}>Original fund type</label>
                <select
                  value={formData.sourceFundType}
                  onChange={(e) => handleChange('sourceFundType', e.target.value)}
                  style={inputStyle}
                >
                  <option value="">Select...</option>
                  <option value="PENSION_FUND">Pension Fund</option>
                  <option value="PROVIDENT_FUND">Provident Fund</option>
                </select>
                <p style={helpTextStyle}>
                  What type of fund did you transfer from?
                </p>
              </div>

              <div style={formGroupStyle}>
                <label style={labelStyle}>Transfer date</label>
                <input
                  type="date"
                  value={formData.transferDate}
                  onChange={(e) => handleChange('transferDate', e.target.value)}
                  style={inputStyle}
                />
              </div>

              <div style={formGroupStyle}>
                <label style={{ ...labelStyle, display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="checkbox"
                    checked={formData.withdrawalTaken}
                    onChange={(e) => handleChange('withdrawalTaken', e.target.checked)}
                  />
                  I've already taken my pre-retirement withdrawal
                </label>
                <p style={helpTextStyle}>
                  Preservation funds allow one withdrawal before retirement
                </p>
              </div>

              {formData.withdrawalTaken && (
                <>
                  <div style={formGroupStyle}>
                    <label style={labelStyle}>Withdrawal amount</label>
                    <input
                      type="number"
                      value={formData.withdrawalAmount}
                      onChange={(e) => handleChange('withdrawalAmount', e.target.value)}
                      style={inputStyle}
                      placeholder="0"
                    />
                  </div>

                  <div style={formGroupStyle}>
                    <label style={labelStyle}>Withdrawal date</label>
                    <input
                      type="date"
                      value={formData.withdrawalDate}
                      onChange={(e) => handleChange('withdrawalDate', e.target.value)}
                      style={inputStyle}
                    />
                  </div>
                </>
              )}
            </>
          )}

          <div style={formGroupStyle}>
            <label style={labelStyle}>Expected retirement age</label>
            <input
              type="number"
              value={formData.expectedRetirementAge}
              onChange={(e) => handleChange('expectedRetirementAge', e.target.value)}
              style={inputStyle}
              placeholder="65"
              min="55"
            />
            <p style={helpTextStyle}>
              When do you plan to retire? (minimum age 55 for most funds)
            </p>
          </div>
        </div>
      )}

      {/* Step 4: Investment Choice */}
      {step === 4 && (
        <div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px' }}>
            Investment portfolio
          </h3>

          <div style={formGroupStyle}>
            <label style={labelStyle}>Portfolio name</label>
            <input
              type="text"
              value={formData.portfolioName}
              onChange={(e) => handleChange('portfolioName', e.target.value)}
              style={inputStyle}
              placeholder="e.g., Balanced Fund, High Equity"
            />
          </div>

          <div style={formGroupStyle}>
            <label style={labelStyle}>Asset allocation</label>
            <p style={{ ...helpTextStyle, marginBottom: '12px' }}>
              Enter the percentage allocated to each asset class. Total must equal 100%.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <label style={{ ...labelStyle, fontSize: '0.75rem' }}>Equity %</label>
                <input
                  type="number"
                  value={formData.equityPercentage}
                  onChange={(e) => handleChange('equityPercentage', e.target.value)}
                  style={inputStyle}
                  placeholder="0"
                  min="0"
                  max="100"
                />
              </div>

              <div>
                <label style={{ ...labelStyle, fontSize: '0.75rem' }}>Bonds %</label>
                <input
                  type="number"
                  value={formData.bondsPercentage}
                  onChange={(e) => handleChange('bondsPercentage', e.target.value)}
                  style={inputStyle}
                  placeholder="0"
                  min="0"
                  max="100"
                />
              </div>

              <div>
                <label style={{ ...labelStyle, fontSize: '0.75rem' }}>Cash %</label>
                <input
                  type="number"
                  value={formData.cashPercentage}
                  onChange={(e) => handleChange('cashPercentage', e.target.value)}
                  style={inputStyle}
                  placeholder="0"
                  min="0"
                  max="100"
                />
              </div>

              <div>
                <label style={{ ...labelStyle, fontSize: '0.75rem' }}>Property %</label>
                <input
                  type="number"
                  value={formData.propertyPercentage}
                  onChange={(e) => handleChange('propertyPercentage', e.target.value)}
                  style={inputStyle}
                  placeholder="0"
                  min="0"
                  max="100"
                />
              </div>

              <div>
                <label style={{ ...labelStyle, fontSize: '0.75rem' }}>Offshore %</label>
                <input
                  type="number"
                  value={formData.offshorePercentage}
                  onChange={(e) => handleChange('offshorePercentage', e.target.value)}
                  style={inputStyle}
                  placeholder="0"
                  min="0"
                  max="100"
                />
              </div>
            </div>

            {validationErrors.assetAllocation && (
              <p style={errorTextStyle}>{validationErrors.assetAllocation}</p>
            )}
          </div>

          {/* Regulation 28 Compliance Check */}
          {regulation28Violations.length > 0 && (
            <div
              style={{
                backgroundColor: '#FEF3C7',
                border: '1px solid #FCD34D',
                borderLeft: '4px solid #F59E0B',
                padding: '16px',
                borderRadius: '8px',
                marginTop: '16px',
              }}
            >
              <p style={{ fontWeight: 600, color: '#92400E', marginBottom: '8px' }}>
                ⚠️ Regulation 28 compliance warning
              </p>
              <ul style={{ color: '#78350F', fontSize: '0.875rem', paddingLeft: '20px', margin: 0 }}>
                {regulation28Violations.map((v, i) => (
                  <li key={i}>{v}</li>
                ))}
              </ul>
              <p style={{ color: '#78350F', fontSize: '0.875rem', marginTop: '8px' }}>
                Limits: Max 75% equity, 30% offshore, 25% property
              </p>
            </div>
          )}

          {regulation28Violations.length === 0 && (formData.equityPercentage || formData.offshorePercentage) && (
            <div
              style={{
                backgroundColor: '#D1FAE5',
                border: '1px solid #86EFAC',
                borderLeft: '4px solid #10B981',
                padding: '16px',
                borderRadius: '8px',
                marginTop: '16px',
              }}
            >
              <p style={{ fontWeight: 600, color: '#065F46', marginBottom: '4px' }}>
                ✓ Regulation 28 compliant
              </p>
              <p style={{ color: '#047857', fontSize: '0.875rem' }}>
                Your asset allocation meets all regulatory requirements
              </p>
            </div>
          )}
        </div>
      )}

      {/* Step 5: Review */}
      {step === 5 && (
        <div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px' }}>
            Review your fund details
          </h3>

          <div
            style={{
              backgroundColor: '#F8FAFC',
              padding: '24px',
              borderRadius: '8px',
              marginBottom: '24px',
            }}
          >
            <h4 style={{ fontWeight: 600, marginBottom: '12px' }}>Fund Information</h4>
            <p style={{ fontSize: '0.875rem', color: '#475569', marginBottom: '8px' }}>
              <strong>Type:</strong> {formData.fundType.replace(/_/g, ' ')}
            </p>
            <p style={{ fontSize: '0.875rem', color: '#475569', marginBottom: '8px' }}>
              <strong>Provider:</strong> {formData.provider}
            </p>
            <p style={{ fontSize: '0.875rem', color: '#475569', marginBottom: '8px' }}>
              <strong>Fund:</strong> {formData.fundName}
            </p>
            <p style={{ fontSize: '0.875rem', color: '#475569', marginBottom: '8px' }}>
              <strong>Current Value:</strong> R{parseFloat(formData.currentValue || 0).toLocaleString()}
            </p>
            {formData.monthlyContribution && (
              <p style={{ fontSize: '0.875rem', color: '#475569', marginBottom: '8px' }}>
                <strong>Monthly Contribution:</strong> R{parseFloat(formData.monthlyContribution).toLocaleString()}
              </p>
            )}
            {formData.portfolioName && (
              <p style={{ fontSize: '0.875rem', color: '#475569', marginBottom: '8px' }}>
                <strong>Portfolio:</strong> {formData.portfolioName}
              </p>
            )}
          </div>

          <p style={{ color: '#64748B', fontSize: '0.875rem', lineHeight: '1.7' }}>
            Please review your details. You can go back to make changes or save this fund.
          </p>
        </div>
      )}

      {/* Navigation Buttons */}
      <div style={buttonContainerStyle}>
        <div>
          {step > 1 && (
            <Button variant="outline" onClick={handleBack} disabled={loading}>
              ← Back
            </Button>
          )}
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <Button variant="ghost" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>

          {step < 5 ? (
            <Button variant="primary" onClick={handleNext} disabled={loading}>
              Next →
            </Button>
          ) : (
            <Button variant="primary" onClick={handleSubmit} disabled={loading}>
              {loading ? 'Saving...' : fundId ? 'Update Fund' : 'Add Fund'}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
