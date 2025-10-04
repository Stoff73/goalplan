import React, { useState } from 'react';
import { Button, Input, Label, Select, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * PensionForm - Add/Edit UK Pension with clear guidance
 *
 * Features:
 * - Step-by-step pension entry with explanatory text
 * - Different fields based on pension type (DC vs DB)
 * - Client-side validation with clear error messages
 * - Educational tips throughout
 * - Follows STYLEGUIDE.md narrative approach
 */
export function PensionForm({ pensionId, onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    pensionType: 'OCCUPATIONAL_DC',
    provider: '',
    schemeReference: '',
    employerName: '',
    currentValue: '',
    monthlyContribution: '',
    employerContribution: '',
    personalContribution: '',
    taxReliefMethod: 'NET_PAY',
    investmentStrategy: 'BALANCED',
    assumedGrowthRate: '5',
    startDate: '',
    retirementAge: '67',
    // DB fields
    accrualRate: '1/60',
    pensionableServiceYears: '',
    finalSalary: '',
    schemeType: 'FINAL_SALARY',
    guaranteedAnnualPension: '',
    spousePensionPercentage: '50',
    normalRetirementAge: '65',
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  const isDC = ['OCCUPATIONAL_DC', 'SIPP', 'PERSONAL_PENSION'].includes(formData.pensionType);

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.provider.trim()) {
      newErrors.provider = 'Provider name is required';
    }

    if (isDC) {
      if (!formData.currentValue || parseFloat(formData.currentValue) < 0) {
        newErrors.currentValue = 'Please enter a valid pension value (0 or more)';
      }
      if (!formData.monthlyContribution || parseFloat(formData.monthlyContribution) < 0) {
        newErrors.monthlyContribution = 'Please enter a valid monthly contribution (0 or more)';
      }
    } else {
      // DB validation
      if (!formData.guaranteedAnnualPension || parseFloat(formData.guaranteedAnnualPension) <= 0) {
        newErrors.guaranteedAnnualPension = 'Please enter the annual pension amount';
      }
    }

    if (!formData.startDate) {
      newErrors.startDate = 'Start date is required';
    }

    if (!formData.retirementAge || parseInt(formData.retirementAge) < 55) {
      newErrors.retirementAge = 'Retirement age must be at least 55';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setSubmitError(null);

    try {
      // Prepare request body based on pension type
      const requestBody = {
        pensionType: formData.pensionType,
        provider: formData.provider,
        schemeReference: formData.schemeReference || null,
        employerName: formData.employerName || null,
        startDate: formData.startDate,
        expectedRetirementDate: calculateRetirementDate(),
        normalRetirementAge: parseInt(formData.normalRetirementAge || formData.retirementAge),
      };

      if (isDC) {
        requestBody.currentValue = parseFloat(formData.currentValue);
        requestBody.contributionDetails = {
          employeeContribution: {
            amount: parseFloat(formData.monthlyContribution || 0),
            frequency: 'MONTHLY',
            type: 'FIXED_AMOUNT',
          },
          employerContribution: {
            amount: parseFloat(formData.employerContribution || 0),
            frequency: 'MONTHLY',
            type: 'FIXED_AMOUNT',
          },
          personalContribution: {
            amount: parseFloat(formData.personalContribution || 0),
            frequency: 'MONTHLY',
          },
          taxReliefMethod: formData.taxReliefMethod,
        };
        requestBody.investmentStrategy = formData.investmentStrategy;
        requestBody.assumedGrowthRate = parseFloat(formData.assumedGrowthRate);
        requestBody.assumedInflationRate = 2.5; // Default
      } else {
        // DB pension
        requestBody.definedBenefitDetails = {
          accrualRate: formData.accrualRate,
          pensionableService: parseFloat(formData.pensionableServiceYears || 0),
          finalSalary: parseFloat(formData.finalSalary || 0),
          schemeType: formData.schemeType,
          normalRetirementAge: parseInt(formData.normalRetirementAge),
          guaranteedPension: parseFloat(formData.guaranteedAnnualPension),
          spousePension: parseFloat(formData.spousePensionPercentage),
          lumpSumEntitlement: 0, // Optional
          indexation: 'CPI',
        };
      }

      const method = pensionId ? 'PUT' : 'POST';
      const url = pensionId
        ? `/api/v1/retirement/uk-pensions/${pensionId}`
        : '/api/v1/retirement/uk-pensions';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        if (response.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save pension');
      }

      onSuccess();
    } catch (err) {
      setSubmitError(err.message);
      console.error('Error saving pension:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateRetirementDate = () => {
    if (!formData.startDate || !formData.retirementAge) return null;
    // This is a simplified calculation - in production, you'd use user's DOB
    const today = new Date();
    const retirementYear = today.getFullYear() + (parseInt(formData.retirementAge) - 30); // Assuming current age ~30
    return `${retirementYear}-04-06`; // UK tax year start
  };

  // Styles
  const formContainerStyle = {
    maxWidth: '800px',
    margin: '0 auto',
  };

  const sectionStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
  };

  const sectionHeadingStyle = {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '8px',
  };

  const sectionDescStyle = {
    fontSize: '0.875rem',
    color: '#475569',
    lineHeight: '1.7',
    marginBottom: '24px',
  };

  const fieldGroupStyle = {
    marginBottom: '24px',
  };

  const labelStyle = {
    display: 'block',
    fontSize: '1rem',
    fontWeight: 500,
    color: '#0F172A',
    marginBottom: '8px',
  };

  const helpTextStyle = {
    fontSize: '0.875rem',
    color: '#475569',
    marginBottom: '8px',
    lineHeight: '1.7',
  };

  const errorStyle = {
    fontSize: '0.875rem',
    color: '#EF4444',
    marginTop: '4px',
  };

  const tipBoxStyle = {
    backgroundColor: '#DBEAFE',
    border: '1px solid #BFDBFE',
    borderLeft: '4px solid #3B82F6',
    padding: '12px 16px',
    borderRadius: '8px',
    fontSize: '0.875rem',
    color: '#1E40AF',
    lineHeight: '1.7',
  };

  const buttonGroupStyle = {
    display: 'flex',
    gap: '12px',
    justifyContent: 'flex-end',
    marginTop: '32px',
  };

  return (
    <form onSubmit={handleSubmit} style={formContainerStyle}>
      {submitError && (
        <Alert variant="error" style={{ marginBottom: '24px' }}>
          <p style={{ fontWeight: 600 }}>Error saving pension</p>
          <p style={{ marginTop: '4px' }}>{submitError}</p>
        </Alert>
      )}

      {/* Step 1: Pension Type */}
      <div style={sectionStyle}>
        <h3 style={sectionHeadingStyle}>What type of pension is this?</h3>
        <p style={sectionDescStyle}>
          Choose the pension type. If you're unsure, check your pension statement or ask your employer.
        </p>

        <div style={fieldGroupStyle}>
          <Label htmlFor="pensionType" style={labelStyle}>
            Pension type
          </Label>
          <Select
            id="pensionType"
            value={formData.pensionType}
            onChange={(e) => handleChange('pensionType', e.target.value)}
          >
            <option value="OCCUPATIONAL_DC">Workplace Pension (Defined Contribution)</option>
            <option value="SIPP">Self-Invested Personal Pension (SIPP)</option>
            <option value="OCCUPATIONAL_DB">Final Salary / Defined Benefit</option>
            <option value="PERSONAL_PENSION">Personal Pension</option>
            <option value="STAKEHOLDER">Stakeholder Pension</option>
            <option value="GROUP_PERSONAL_PENSION">Group Personal Pension</option>
          </Select>
        </div>

        <div style={tipBoxStyle}>
          <strong>Not sure?</strong> Most modern workplace pensions are Defined Contribution (DC).
          Final Salary pensions are Defined Benefit (DB) - common in public sector and older schemes.
        </div>
      </div>

      {/* Step 2: Provider & Scheme Details */}
      <div style={sectionStyle}>
        <h3 style={sectionHeadingStyle}>Provider and scheme details</h3>
        <p style={sectionDescStyle}>
          Enter the pension provider and scheme information. You'll find this on your pension statement.
        </p>

        <div style={fieldGroupStyle}>
          <Label htmlFor="provider" style={labelStyle}>
            Provider name *
          </Label>
          <Input
            id="provider"
            type="text"
            value={formData.provider}
            onChange={(e) => handleChange('provider', e.target.value)}
            placeholder="e.g., Aviva, Legal & General, Fidelity"
          />
          {errors.provider && <p style={errorStyle}>{errors.provider}</p>}
        </div>

        <div style={fieldGroupStyle}>
          <Label htmlFor="schemeReference" style={labelStyle}>
            Scheme reference number
          </Label>
          <p style={helpTextStyle}>Optional - helps you identify this pension later</p>
          <Input
            id="schemeReference"
            type="text"
            value={formData.schemeReference}
            onChange={(e) => handleChange('schemeReference', e.target.value)}
            placeholder="e.g., 12345678"
          />
        </div>

        {['OCCUPATIONAL_DC', 'OCCUPATIONAL_DB', 'GROUP_PERSONAL_PENSION'].includes(
          formData.pensionType
        ) && (
          <div style={fieldGroupStyle}>
            <Label htmlFor="employerName" style={labelStyle}>
              Employer name
            </Label>
            <p style={helpTextStyle}>The employer this pension is linked to</p>
            <Input
              id="employerName"
              type="text"
              value={formData.employerName}
              onChange={(e) => handleChange('employerName', e.target.value)}
              placeholder="e.g., ABC Company Ltd"
            />
          </div>
        )}

        <div style={fieldGroupStyle}>
          <Label htmlFor="startDate" style={labelStyle}>
            Start date *
          </Label>
          <p style={helpTextStyle}>When did you start contributing to this pension?</p>
          <Input
            id="startDate"
            type="date"
            value={formData.startDate}
            onChange={(e) => handleChange('startDate', e.target.value)}
          />
          {errors.startDate && <p style={errorStyle}>{errors.startDate}</p>}
        </div>
      </div>

      {/* Step 3: Contributions (DC only) */}
      {isDC && (
        <div style={sectionStyle}>
          <h3 style={sectionHeadingStyle}>Current value and contributions</h3>
          <p style={sectionDescStyle}>
            Enter the current pot value and how much you contribute. You'll find this on your latest
            pension statement.
          </p>

          <div style={fieldGroupStyle}>
            <Label htmlFor="currentValue" style={labelStyle}>
              Current pot value (£) *
            </Label>
            <p style={helpTextStyle}>The total value of your pension pot today</p>
            <Input
              id="currentValue"
              type="number"
              step="0.01"
              value={formData.currentValue}
              onChange={(e) => handleChange('currentValue', e.target.value)}
              placeholder="0.00"
            />
            {errors.currentValue && <p style={errorStyle}>{errors.currentValue}</p>}
          </div>

          <div style={fieldGroupStyle}>
            <Label htmlFor="monthlyContribution" style={labelStyle}>
              Your monthly contribution (£) *
            </Label>
            <p style={helpTextStyle}>How much you contribute each month</p>
            <Input
              id="monthlyContribution"
              type="number"
              step="0.01"
              value={formData.monthlyContribution}
              onChange={(e) => handleChange('monthlyContribution', e.target.value)}
              placeholder="0.00"
            />
            {errors.monthlyContribution && <p style={errorStyle}>{errors.monthlyContribution}</p>}
          </div>

          <div style={fieldGroupStyle}>
            <Label htmlFor="employerContribution" style={labelStyle}>
              Employer contribution (£)
            </Label>
            <p style={helpTextStyle}>How much your employer adds each month (if applicable)</p>
            <Input
              id="employerContribution"
              type="number"
              step="0.01"
              value={formData.employerContribution}
              onChange={(e) => handleChange('employerContribution', e.target.value)}
              placeholder="0.00"
            />
          </div>

          <div style={fieldGroupStyle}>
            <Label htmlFor="personalContribution" style={labelStyle}>
              Additional personal contributions (£)
            </Label>
            <p style={helpTextStyle}>Extra contributions you make outside of salary sacrifice</p>
            <Input
              id="personalContribution"
              type="number"
              step="0.01"
              value={formData.personalContribution}
              onChange={(e) => handleChange('personalContribution', e.target.value)}
              placeholder="0.00"
            />
          </div>

          <div style={fieldGroupStyle}>
            <Label htmlFor="taxReliefMethod" style={labelStyle}>
              Tax relief method
            </Label>
            <Select
              id="taxReliefMethod"
              value={formData.taxReliefMethod}
              onChange={(e) => handleChange('taxReliefMethod', e.target.value)}
            >
              <option value="NET_PAY">Net Pay (relief at source)</option>
              <option value="RELIEF_AT_SOURCE">Relief at Source</option>
            </Select>
          </div>

          <div style={tipBoxStyle}>
            <strong>Tax relief:</strong> Net Pay means contributions are taken before tax. Relief at
            Source means contributions are taken after tax, then 20% is added back automatically.
          </div>
        </div>
      )}

      {/* Step 3: DB Details (DB only) */}
      {!isDC && (
        <div style={sectionStyle}>
          <h3 style={sectionHeadingStyle}>Defined benefit pension details</h3>
          <p style={sectionDescStyle}>
            Enter your guaranteed pension amount. You'll find this on your annual benefit statement.
          </p>

          <div style={fieldGroupStyle}>
            <Label htmlFor="guaranteedAnnualPension" style={labelStyle}>
              Annual pension at retirement (£) *
            </Label>
            <p style={helpTextStyle}>The guaranteed amount you'll receive each year</p>
            <Input
              id="guaranteedAnnualPension"
              type="number"
              step="0.01"
              value={formData.guaranteedAnnualPension}
              onChange={(e) => handleChange('guaranteedAnnualPension', e.target.value)}
              placeholder="0.00"
            />
            {errors.guaranteedAnnualPension && (
              <p style={errorStyle}>{errors.guaranteedAnnualPension}</p>
            )}
          </div>

          <div style={fieldGroupStyle}>
            <Label htmlFor="normalRetirementAge" style={labelStyle}>
              Normal retirement age
            </Label>
            <p style={helpTextStyle}>The age when you can take this pension without reduction</p>
            <Input
              id="normalRetirementAge"
              type="number"
              value={formData.normalRetirementAge}
              onChange={(e) => handleChange('normalRetirementAge', e.target.value)}
              placeholder="65"
            />
          </div>

          <div style={fieldGroupStyle}>
            <Label htmlFor="accrualRate" style={labelStyle}>
              Accrual rate
            </Label>
            <Select
              id="accrualRate"
              value={formData.accrualRate}
              onChange={(e) => handleChange('accrualRate', e.target.value)}
            >
              <option value="1/60">1/60th (common)</option>
              <option value="1/80">1/80th</option>
              <option value="1/54">1/54th</option>
            </Select>
          </div>

          <div style={fieldGroupStyle}>
            <Label htmlFor="pensionableServiceYears" style={labelStyle}>
              Years of service
            </Label>
            <p style={helpTextStyle}>How many years you've been in this pension scheme</p>
            <Input
              id="pensionableServiceYears"
              type="number"
              step="0.1"
              value={formData.pensionableServiceYears}
              onChange={(e) => handleChange('pensionableServiceYears', e.target.value)}
              placeholder="0"
            />
          </div>

          <div style={fieldGroupStyle}>
            <Label htmlFor="spousePensionPercentage" style={labelStyle}>
              Spouse's pension (%)
            </Label>
            <p style={helpTextStyle}>Percentage of your pension paid to spouse if you die first</p>
            <Input
              id="spousePensionPercentage"
              type="number"
              value={formData.spousePensionPercentage}
              onChange={(e) => handleChange('spousePensionPercentage', e.target.value)}
              placeholder="50"
            />
          </div>
        </div>
      )}

      {/* Step 4: Projections */}
      <div style={sectionStyle}>
        <h3 style={sectionHeadingStyle}>Retirement planning</h3>
        <p style={sectionDescStyle}>
          When do you plan to retire, and what growth do you expect? These help us project your
          retirement income.
        </p>

        <div style={fieldGroupStyle}>
          <Label htmlFor="retirementAge" style={labelStyle}>
            Expected retirement age *
          </Label>
          <p style={helpTextStyle}>The age you plan to start drawing this pension</p>
          <Input
            id="retirementAge"
            type="number"
            value={formData.retirementAge}
            onChange={(e) => handleChange('retirementAge', e.target.value)}
            placeholder="67"
          />
          {errors.retirementAge && <p style={errorStyle}>{errors.retirementAge}</p>}
        </div>

        {isDC && (
          <>
            <div style={fieldGroupStyle}>
              <Label htmlFor="investmentStrategy" style={labelStyle}>
                Investment strategy
              </Label>
              <Select
                id="investmentStrategy"
                value={formData.investmentStrategy}
                onChange={(e) => handleChange('investmentStrategy', e.target.value)}
              >
                <option value="CONSERVATIVE">Conservative (lower risk)</option>
                <option value="BALANCED">Balanced (medium risk)</option>
                <option value="AGGRESSIVE">Aggressive (higher risk)</option>
              </Select>
            </div>

            <div style={fieldGroupStyle}>
              <Label htmlFor="assumedGrowthRate" style={labelStyle}>
                Assumed annual growth rate (%)
              </Label>
              <p style={helpTextStyle}>
                Historical average is 5-7%. Conservative: 3-4%, Balanced: 5-6%, Aggressive: 7-8%
              </p>
              <Input
                id="assumedGrowthRate"
                type="number"
                step="0.1"
                value={formData.assumedGrowthRate}
                onChange={(e) => handleChange('assumedGrowthRate', e.target.value)}
                placeholder="5.0"
              />
            </div>
          </>
        )}

        <div style={tipBoxStyle}>
          <strong>Important:</strong> These are projections only. Actual returns may be higher or
          lower. Review your pension regularly and adjust assumptions as needed.
        </div>
      </div>

      {/* Submit Buttons */}
      <div style={buttonGroupStyle}>
        <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
        <Button type="submit" variant="primary" disabled={loading}>
          {loading ? 'Saving...' : pensionId ? 'Update Pension' : 'Add Pension'}
        </Button>
      </div>
    </form>
  );
}
