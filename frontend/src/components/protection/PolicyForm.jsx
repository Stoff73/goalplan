import React, { useState, useEffect } from 'react';
import { Button, Input, Label } from 'internal-packages/ui';

export function PolicyForm({ policy, onSave, onCancel, loading }) {
  const isEditing = !!policy;

  // Form state
  const [formData, setFormData] = useState({
    policyNumber: '',
    provider: '',
    providerCountry: 'UK',
    policyType: 'TERM',
    coverAmount: '',
    currency: 'GBP',
    premiumAmount: '',
    premiumFrequency: 'MONTHLY',
    startDate: '',
    endDate: '',
    criticalIllnessRider: false,
    waiverOfPremium: false,
    indexationRate: '',
    writtenInTrust: false,
    trustType: '',
    trustees: [''],
    beneficiaries: [
      {
        name: '',
        dateOfBirth: '',
        relationship: 'SPOUSE',
        percentage: '',
        address: '',
      },
    ],
    status: 'ACTIVE',
    notes: '',
  });

  const [errors, setErrors] = useState({});
  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 4;

  // Load policy data for editing
  useEffect(() => {
    if (policy) {
      setFormData({
        policyNumber: policy.policyNumber || '',
        provider: policy.provider || '',
        providerCountry: policy.providerCountry || 'UK',
        policyType: policy.policyType || 'TERM',
        coverAmount: policy.coverAmount?.toString() || '',
        currency: policy.currency || 'GBP',
        premiumAmount: policy.premiumAmount?.toString() || '',
        premiumFrequency: policy.premiumFrequency || 'MONTHLY',
        startDate: policy.startDate || '',
        endDate: policy.endDate || '',
        criticalIllnessRider: policy.criticalIllnessRider || false,
        waiverOfPremium: policy.waiverOfPremium || false,
        indexationRate: policy.indexationRate?.toString() || '',
        writtenInTrust: policy.writtenInTrust || false,
        trustType: policy.trustType || '',
        trustees: policy.trustees && policy.trustees.length > 0 ? policy.trustees.map(t => t.name || t) : [''],
        beneficiaries:
          policy.beneficiaries && policy.beneficiaries.length > 0
            ? policy.beneficiaries.map((b) => ({
                name: b.name || '',
                dateOfBirth: b.dateOfBirth || '',
                relationship: b.relationship || 'SPOUSE',
                percentage: b.percentage?.toString() || '',
                address: b.address || '',
              }))
            : [{ name: '', dateOfBirth: '', relationship: 'SPOUSE', percentage: '', address: '' }],
        status: policy.status || 'ACTIVE',
        notes: policy.notes || '',
      });
    }
  }, [policy]);

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  const handleCheckboxChange = (field) => {
    const newValue = !formData[field];
    setFormData((prev) => ({ ...prev, [field]: newValue }));

    // If unchecking writtenInTrust, clear trust fields
    if (field === 'writtenInTrust' && !newValue) {
      setFormData((prev) => ({
        ...prev,
        trustType: '',
        trustees: [''],
      }));
    }
  };

  const handleBeneficiaryChange = (index, field, value) => {
    const newBeneficiaries = [...formData.beneficiaries];
    newBeneficiaries[index] = { ...newBeneficiaries[index], [field]: value };
    setFormData((prev) => ({ ...prev, beneficiaries: newBeneficiaries }));

    // Clear error for this beneficiary field
    if (errors[`beneficiary_${index}_${field}`]) {
      setErrors((prev) => ({ ...prev, [`beneficiary_${index}_${field}`]: null }));
    }
  };

  const addBeneficiary = () => {
    setFormData((prev) => ({
      ...prev,
      beneficiaries: [
        ...prev.beneficiaries,
        { name: '', dateOfBirth: '', relationship: 'SPOUSE', percentage: '', address: '' },
      ],
    }));
  };

  const removeBeneficiary = (index) => {
    if (formData.beneficiaries.length === 1) {
      return; // Must have at least one beneficiary
    }
    const newBeneficiaries = formData.beneficiaries.filter((_, i) => i !== index);
    setFormData((prev) => ({ ...prev, beneficiaries: newBeneficiaries }));
  };

  const handleTrusteeChange = (index, value) => {
    const newTrustees = [...formData.trustees];
    newTrustees[index] = value;
    setFormData((prev) => ({ ...prev, trustees: newTrustees }));
  };

  const addTrustee = () => {
    setFormData((prev) => ({
      ...prev,
      trustees: [...prev.trustees, ''],
    }));
  };

  const removeTrustee = (index) => {
    if (formData.trustees.length === 1) {
      return; // Must have at least one trustee if in trust
    }
    const newTrustees = formData.trustees.filter((_, i) => i !== index);
    setFormData((prev) => ({ ...prev, trustees: newTrustees }));
  };

  // Calculate total percentage
  const totalPercentage = formData.beneficiaries.reduce((sum, b) => {
    const percentage = parseFloat(b.percentage) || 0;
    return sum + percentage;
  }, 0);

  const percentageIsValid = Math.abs(totalPercentage - 100) < 0.01; // Allow for floating point errors

  const validate = () => {
    const newErrors = {};

    // Step 1: Provider Details
    if (!formData.policyNumber.trim()) {
      newErrors.policyNumber = 'Policy number is required';
    }

    if (!formData.provider.trim()) {
      newErrors.provider = 'Provider name is required';
    }

    // Step 2: Cover Details
    if (!formData.coverAmount || parseFloat(formData.coverAmount) <= 0) {
      newErrors.coverAmount = 'Cover amount must be greater than 0';
    }

    if (!formData.premiumAmount || parseFloat(formData.premiumAmount) < 0) {
      newErrors.premiumAmount = 'Premium amount must be 0 or greater';
    }

    if (!formData.startDate) {
      newErrors.startDate = 'Start date is required';
    }

    // End date must be after start date if provided (except whole of life)
    if (formData.endDate && formData.startDate) {
      if (new Date(formData.endDate) <= new Date(formData.startDate)) {
        newErrors.endDate = 'End date must be after start date';
      }
    }

    // Step 3: Beneficiaries and Trust
    if (formData.writtenInTrust) {
      if (!formData.trustType) {
        newErrors.trustType = 'Trust type is required when policy is written in trust';
      }

      const nonEmptyTrustees = formData.trustees.filter((t) => t.trim());
      if (nonEmptyTrustees.length === 0) {
        newErrors.trustees = 'At least one trustee is required for trust policies';
      }
    }

    // Beneficiary validation
    formData.beneficiaries.forEach((b, index) => {
      if (!b.name.trim()) {
        newErrors[`beneficiary_${index}_name`] = 'Beneficiary name is required';
      }
      if (!b.dateOfBirth) {
        newErrors[`beneficiary_${index}_dateOfBirth`] = 'Date of birth is required';
      }
      if (!b.address.trim()) {
        newErrors[`beneficiary_${index}_address`] = 'Address is required';
      }
      if (!b.percentage || parseFloat(b.percentage) <= 0) {
        newErrors[`beneficiary_${index}_percentage`] = 'Percentage must be greater than 0';
      }
    });

    // Total percentage must be 100%
    if (!percentageIsValid) {
      newErrors.beneficiaryTotal = `Beneficiary percentages must total 100%. Current total: ${totalPercentage.toFixed(2)}%`;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep = (step) => {
    const newErrors = {};

    if (step === 1) {
      // Provider Details
      if (!formData.policyNumber.trim()) {
        newErrors.policyNumber = 'Policy number is required';
      }
      if (!formData.provider.trim()) {
        newErrors.provider = 'Provider name is required';
      }
    } else if (step === 2) {
      // Cover Details
      if (!formData.coverAmount || parseFloat(formData.coverAmount) <= 0) {
        newErrors.coverAmount = 'Cover amount must be greater than 0';
      }
      if (!formData.premiumAmount || parseFloat(formData.premiumAmount) < 0) {
        newErrors.premiumAmount = 'Premium amount must be 0 or greater';
      }
      if (!formData.startDate) {
        newErrors.startDate = 'Start date is required';
      }
      if (formData.endDate && formData.startDate) {
        if (new Date(formData.endDate) <= new Date(formData.startDate)) {
          newErrors.endDate = 'End date must be after start date';
        }
      }
    } else if (step === 3) {
      // Beneficiaries
      if (formData.writtenInTrust) {
        if (!formData.trustType) {
          newErrors.trustType = 'Trust type is required when policy is written in trust';
        }
        const nonEmptyTrustees = formData.trustees.filter((t) => t.trim());
        if (nonEmptyTrustees.length === 0) {
          newErrors.trustees = 'At least one trustee is required for trust policies';
        }
      }

      formData.beneficiaries.forEach((b, index) => {
        if (!b.name.trim()) {
          newErrors[`beneficiary_${index}_name`] = 'Beneficiary name is required';
        }
        if (!b.dateOfBirth) {
          newErrors[`beneficiary_${index}_dateOfBirth`] = 'Date of birth is required';
        }
        if (!b.address.trim()) {
          newErrors[`beneficiary_${index}_address`] = 'Address is required';
        }
        if (!b.percentage || parseFloat(b.percentage) <= 0) {
          newErrors[`beneficiary_${index}_percentage`] = 'Percentage must be greater than 0';
        }
      });

      if (!percentageIsValid) {
        newErrors.beneficiaryTotal = `Beneficiary percentages must total 100%. Current total: ${totalPercentage.toFixed(2)}%`;
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(prev + 1, totalSteps));
    }
  };

  const handlePrevious = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('🔍 Form submit triggered', { formData });

    if (!validate()) {
      console.log('❌ Validation failed', { errors });
      // Find the first step with errors and go to it
      const errorKeys = Object.keys(errors);
      if (errorKeys.some((k) => ['policyNumber', 'provider'].includes(k))) {
        setCurrentStep(1);
      } else if (errorKeys.some((k) => ['coverAmount', 'premiumAmount', 'startDate', 'endDate'].includes(k))) {
        setCurrentStep(2);
      } else if (errorKeys.some((k) => k.includes('beneficiary') || k.includes('trust'))) {
        setCurrentStep(3);
      }
      return;
    }

    console.log('✅ Validation passed, preparing submit data');

    // Prepare submit data with snake_case fields for backend
    const submitData = {
      policy_number: formData.policyNumber.trim(),
      provider: formData.provider.trim(),
      provider_country: formData.providerCountry,
      policy_type: formData.policyType,
      cover_amount: parseFloat(formData.coverAmount),
      currency: formData.currency,
      premium_amount: parseFloat(formData.premiumAmount),
      premium_frequency: formData.premiumFrequency,
      start_date: formData.startDate,
      end_date: formData.endDate || null,
      critical_illness_rider: formData.criticalIllnessRider,
      waiver_of_premium: formData.waiverOfPremium,
      indexation_rate: formData.indexationRate ? parseFloat(formData.indexationRate) : null,
      beneficiaries: formData.beneficiaries.map((b) => ({
        name: b.name.trim(),
        date_of_birth: b.dateOfBirth || null,
        relationship: b.relationship,
        percentage: parseFloat(b.percentage),
        address: b.address.trim() || null,
      })),
      status: formData.status,
      notes: formData.notes.trim(),
    };

    // Add trust_details as nested object if UK policy with trust
    if (formData.writtenInTrust && formData.providerCountry === 'UK') {
      submitData.trust_details = {
        trust_type: formData.trustType,
        trustees: formData.trustees.filter((t) => t.trim()),
      };
    }

    console.log('📤 Calling onSave with data:', submitData);
    onSave(submitData);
  };

  // Styles
  const modalHeaderStyle = {
    fontSize: '1.5rem',
    fontWeight: 700,
    color: '#0F172A',
    marginBottom: '8px',
  };

  const modalDescStyle = {
    color: '#64748B',
    fontSize: '0.95rem',
    marginBottom: '24px',
    lineHeight: '1.7',
  };

  const stepIndicatorStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '32px',
    position: 'relative',
  };

  const stepStyle = (step) => ({
    flex: 1,
    textAlign: 'center',
    position: 'relative',
    zIndex: 1,
  });

  const stepCircleStyle = (step) => ({
    width: '32px',
    height: '32px',
    borderRadius: '50%',
    backgroundColor: step <= currentStep ? '#2563EB' : '#E2E8F0',
    color: step <= currentStep ? '#FFFFFF' : '#94A3B8',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto',
    fontWeight: 600,
    fontSize: '0.875rem',
  });

  const stepLabelStyle = (step) => ({
    marginTop: '8px',
    fontSize: '0.75rem',
    color: step <= currentStep ? '#0F172A' : '#94A3B8',
    fontWeight: step === currentStep ? 600 : 400,
  });

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

  const warningCalloutStyle = {
    backgroundColor: '#FEF3C7',
    border: '1px solid #FDE68A',
    borderLeft: '4px solid #F59E0B',
    padding: '16px',
    borderRadius: '8px',
    marginBottom: '24px',
  };

  const successCalloutStyle = {
    backgroundColor: '#D1FAE5',
    border: '1px solid #A7F3D0',
    borderLeft: '4px solid #10B981',
    padding: '16px',
    borderRadius: '8px',
    marginBottom: '24px',
  };

  const actionsStyle = {
    display: 'flex',
    gap: '12px',
    justifyContent: 'space-between',
    marginTop: '32px',
    paddingTop: '24px',
    borderTop: '1px solid #E2E8F0',
  };

  const beneficiaryCardStyle = {
    padding: '16px',
    backgroundColor: '#F8FAFC',
    border: '1px solid #E2E8F0',
    borderRadius: '8px',
    marginBottom: '16px',
  };

  const beneficiaryHeaderStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px',
  };

  const percentageTotalStyle = {
    padding: '12px',
    backgroundColor: percentageIsValid ? '#D1FAE5' : '#FEE2E2',
    border: `1px solid ${percentageIsValid ? '#A7F3D0' : '#FECACA'}`,
    borderRadius: '8px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontSize: '0.95rem',
    fontWeight: 600,
    color: percentageIsValid ? '#065F46' : '#991B1B',
  };

  const selectStyle = {
    width: '100%',
    padding: '0.5rem 0.75rem',
    border: '1px solid #D1D5DB',
    borderRadius: '0.375rem',
    boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    fontSize: '1rem',
    outline: 'none',
    fontFamily: 'inherit',
  };

  // Dropdown options
  const countries = [
    { value: 'UK', label: 'United Kingdom' },
    { value: 'ZA', label: 'South Africa' },
    { value: 'OTHER', label: 'Other' },
  ];

  const policyTypes = [
    { value: 'TERM', label: 'Term Life' },
    { value: 'WHOLE_OF_LIFE', label: 'Whole of Life' },
    { value: 'DECREASING_TERM', label: 'Decreasing Term' },
    { value: 'LEVEL_TERM', label: 'Level Term' },
    { value: 'INCREASING_TERM', label: 'Increasing Term' },
    { value: 'FAMILY_INCOME_BENEFIT', label: 'Family Income Benefit' },
    { value: 'OTHER', label: 'Other' },
  ];

  const currencies = [
    { value: 'GBP', label: 'GBP (£)' },
    { value: 'ZAR', label: 'ZAR (R)' },
    { value: 'USD', label: 'USD ($)' },
    { value: 'EUR', label: 'EUR (€)' },
  ];

  const frequencies = [
    { value: 'MONTHLY', label: 'Monthly' },
    { value: 'ANNUALLY', label: 'Annually' },
    { value: 'SINGLE', label: 'Single Premium' },
  ];

  const trustTypes = [
    { value: 'BARE', label: 'Bare Trust' },
    { value: 'DISCRETIONARY', label: 'Discretionary Trust' },
    { value: 'INTEREST_IN_POSSESSION', label: 'Interest in Possession Trust' },
  ];

  const relationships = [
    { value: 'SPOUSE', label: 'Spouse / Partner' },
    { value: 'CHILD', label: 'Child' },
    { value: 'PARENT', label: 'Parent' },
    { value: 'SIBLING', label: 'Sibling' },
    { value: 'OTHER', label: 'Other' },
  ];

  const statuses = [
    { value: 'ACTIVE', label: 'Active' },
    { value: 'LAPSED', label: 'Lapsed' },
    { value: 'CLAIMED', label: 'Claimed' },
    { value: 'MATURED', label: 'Matured' },
  ];

  return (
    <form onSubmit={handleSubmit}>
      <h2 style={modalHeaderStyle}>{isEditing ? 'Edit life assurance policy' : 'Add life assurance policy'}</h2>
      <p style={modalDescStyle}>
        Track your life assurance policy to ensure your family is protected. We'll help you understand coverage
        gaps and tax implications (especially UK Inheritance Tax).
      </p>

      {/* Step Indicator */}
      <div style={stepIndicatorStyle}>
        {[1, 2, 3, 4].map((step) => (
          <div key={step} style={stepStyle(step)}>
            <div style={stepCircleStyle(step)}>{step}</div>
            <div style={stepLabelStyle(step)}>
              {step === 1 && 'Provider'}
              {step === 2 && 'Coverage'}
              {step === 3 && 'Beneficiaries'}
              {step === 4 && 'Details'}
            </div>
          </div>
        ))}
      </div>

      {/* Step 1: Provider Details */}
      {currentStep === 1 && (
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
            Tell us about your policy provider
          </h3>

          <div style={formGridStyle}>
            <div style={formGroupStyle}>
              <Label>
                Policy Number <span style={{ color: '#EF4444' }}>*</span>
              </Label>
              <Input
                type="text"
                placeholder="e.g., POL123456"
                value={formData.policyNumber}
                onChange={(e) => handleChange('policyNumber', e.target.value)}
              />
              {errors.policyNumber && <div style={errorStyle}>{errors.policyNumber}</div>}
              <div style={helpTextStyle}>Your unique policy reference number</div>
            </div>

            <div style={formGroupStyle}>
              <Label>
                Provider Name <span style={{ color: '#EF4444' }}>*</span>
              </Label>
              <Input
                type="text"
                placeholder="e.g., Aviva, Old Mutual"
                value={formData.provider}
                onChange={(e) => handleChange('provider', e.target.value)}
              />
              {errors.provider && <div style={errorStyle}>{errors.provider}</div>}
              <div style={helpTextStyle}>The insurance company providing your policy</div>
            </div>
          </div>

          <div style={formGridStyle}>
            <div style={formGroupStyle}>
              <Label>
                Provider Country <span style={{ color: '#EF4444' }}>*</span>
              </Label>
              <select
                value={formData.providerCountry}
                onChange={(e) => handleChange('providerCountry', e.target.value)}
                style={selectStyle}
              >
                {countries.map((country) => (
                  <option key={country.value} value={country.value}>
                    {country.label}
                  </option>
                ))}
              </select>
              <div style={helpTextStyle}>Where the policy is issued</div>
            </div>

            <div style={formGroupStyle}>
              <Label>
                Policy Type <span style={{ color: '#EF4444' }}>*</span>
              </Label>
              <select value={formData.policyType} onChange={(e) => handleChange('policyType', e.target.value)} style={selectStyle}>
                {policyTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
              <div style={helpTextStyle}>The type of life assurance coverage</div>
            </div>
          </div>
        </div>
      )}

      {/* Step 2: Cover Details */}
      {currentStep === 2 && (
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
            What coverage do you have?
          </h3>

          <div style={formGridStyle}>
            <div style={formGroupStyle}>
              <Label>
                Cover Amount <span style={{ color: '#EF4444' }}>*</span>
              </Label>
              <Input
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={formData.coverAmount}
                onChange={(e) => handleChange('coverAmount', e.target.value)}
              />
              {errors.coverAmount && <div style={errorStyle}>{errors.coverAmount}</div>}
              <div style={helpTextStyle}>The payout amount your beneficiaries will receive</div>
            </div>

            <div style={formGroupStyle}>
              <Label>
                Currency <span style={{ color: '#EF4444' }}>*</span>
              </Label>
              <select value={formData.currency} onChange={(e) => handleChange('currency', e.target.value)} style={selectStyle}>
                {currencies.map((curr) => (
                  <option key={curr.value} value={curr.value}>
                    {curr.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div style={formGridStyle}>
            <div style={formGroupStyle}>
              <Label>
                Premium Amount <span style={{ color: '#EF4444' }}>*</span>
              </Label>
              <Input
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={formData.premiumAmount}
                onChange={(e) => handleChange('premiumAmount', e.target.value)}
              />
              {errors.premiumAmount && <div style={errorStyle}>{errors.premiumAmount}</div>}
              <div style={helpTextStyle}>How much you pay for this policy</div>
            </div>

            <div style={formGroupStyle}>
              <Label>
                Premium Frequency <span style={{ color: '#EF4444' }}>*</span>
              </Label>
              <select value={formData.premiumFrequency} onChange={(e) => handleChange('premiumFrequency', e.target.value)} style={selectStyle}>
                {frequencies.map((freq) => (
                  <option key={freq.value} value={freq.value}>
                    {freq.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div style={formGridStyle}>
            <div style={formGroupStyle}>
              <Label>
                Start Date <span style={{ color: '#EF4444' }}>*</span>
              </Label>
              <Input type="date" value={formData.startDate} onChange={(e) => handleChange('startDate', e.target.value)} />
              {errors.startDate && <div style={errorStyle}>{errors.startDate}</div>}
            </div>

            <div style={formGroupStyle}>
              <Label>End Date</Label>
              <Input type="date" value={formData.endDate} onChange={(e) => handleChange('endDate', e.target.value)} />
              {errors.endDate && <div style={errorStyle}>{errors.endDate}</div>}
              <div style={helpTextStyle}>Leave blank for whole of life policies</div>
            </div>
          </div>

          {/* Optional riders */}
          <div style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <input
                type="checkbox"
                id="criticalIllnessRider"
                checked={formData.criticalIllnessRider}
                onChange={() => handleCheckboxChange('criticalIllnessRider')}
                style={{ width: '16px', height: '16px', cursor: 'pointer' }}
              />
              <Label htmlFor="criticalIllnessRider" style={{ cursor: 'pointer', marginBottom: 0 }}>
                Critical Illness Rider
              </Label>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <input
                type="checkbox"
                id="waiverOfPremium"
                checked={formData.waiverOfPremium}
                onChange={() => handleCheckboxChange('waiverOfPremium')}
                style={{ width: '16px', height: '16px', cursor: 'pointer' }}
              />
              <Label htmlFor="waiverOfPremium" style={{ cursor: 'pointer', marginBottom: 0 }}>
                Waiver of Premium
              </Label>
            </div>
          </div>

          {/* Indexation rate for increasing policies */}
          {formData.policyType === 'INCREASING_TERM' && (
            <div style={formGroupStyle}>
              <Label>Indexation Rate (%)</Label>
              <Input
                type="number"
                step="0.1"
                min="0"
                max="100"
                placeholder="e.g., 3.0"
                value={formData.indexationRate}
                onChange={(e) => handleChange('indexationRate', e.target.value)}
              />
              <div style={helpTextStyle}>Annual increase rate for your cover amount</div>
            </div>
          )}
        </div>
      )}

      {/* Step 3: Beneficiaries */}
      {currentStep === 3 && (
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
            Who will receive the payout?
          </h3>

          {/* Written in Trust (UK only) */}
          {formData.providerCountry === 'UK' && (
            <>
              <div style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                  <input
                    type="checkbox"
                    id="writtenInTrust"
                    checked={formData.writtenInTrust}
                    onChange={() => handleCheckboxChange('writtenInTrust')}
                    style={{ width: '16px', height: '16px', cursor: 'pointer' }}
                  />
                  <Label htmlFor="writtenInTrust" style={{ cursor: 'pointer', marginBottom: 0 }}>
                    Written in Trust (Recommended for UK policies)
                  </Label>
                </div>

                {formData.writtenInTrust && (
                  <div style={successCalloutStyle}>
                    <p style={{ fontWeight: 600, color: '#065F46', marginBottom: '4px' }}>Great choice!</p>
                    <p style={{ fontSize: '0.875rem', color: '#047857', lineHeight: '1.6' }}>
                      Writing your policy in trust means the payout goes directly to beneficiaries, avoiding the 40%
                      Inheritance Tax on your estate. This also speeds up the payout process.
                    </p>
                  </div>
                )}

                {!formData.writtenInTrust && formData.providerCountry === 'UK' && (
                  <div style={warningCalloutStyle}>
                    <p style={{ fontWeight: 600, color: '#92400E', marginBottom: '4px' }}>Consider writing in trust</p>
                    <p style={{ fontSize: '0.875rem', color: '#78350F', lineHeight: '1.6' }}>
                      Without a trust, the policy payout becomes part of your estate and may be subject to 40%
                      Inheritance Tax. Contact your provider to arrange a trust.
                    </p>
                  </div>
                )}
              </div>

              {/* Trust Details */}
              {formData.writtenInTrust && (
                <>
                  <div style={formGroupStyle}>
                    <Label>
                      Trust Type <span style={{ color: '#EF4444' }}>*</span>
                    </Label>
                    <select value={formData.trustType} onChange={(e) => handleChange('trustType', e.target.value)} style={selectStyle}>
                      <option value="">Select trust type</option>
                      {trustTypes.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                    {errors.trustType && <div style={errorStyle}>{errors.trustType}</div>}
                    <div style={helpTextStyle}>The type of trust arrangement</div>
                  </div>

                  <div style={{ marginBottom: '24px' }}>
                    <Label>
                      Trustees <span style={{ color: '#EF4444' }}>*</span>
                    </Label>
                    <div style={helpTextStyle}>People who manage the trust (usually you and a trusted relative)</div>
                    {formData.trustees.map((trustee, index) => (
                      <div key={index} style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                        <Input
                          type="text"
                          placeholder="Trustee name"
                          value={trustee}
                          onChange={(e) => handleTrusteeChange(index, e.target.value)}
                          style={{ flex: 1 }}
                        />
                        {formData.trustees.length > 1 && (
                          <Button type="button" variant="outline" onClick={() => removeTrustee(index)}>
                            Remove
                          </Button>
                        )}
                      </div>
                    ))}
                    {errors.trustees && <div style={errorStyle}>{errors.trustees}</div>}
                    <Button type="button" variant="secondary" onClick={addTrustee} style={{ marginTop: '8px' }}>
                      + Add Trustee
                    </Button>
                  </div>
                </>
              )}
            </>
          )}

          {/* Beneficiaries */}
          <div style={{ marginBottom: '24px' }}>
            <Label>
              Beneficiaries <span style={{ color: '#EF4444' }}>*</span>
            </Label>
            <div style={helpTextStyle}>People who will receive the payout. Percentages must total 100%.</div>

            {formData.beneficiaries.map((beneficiary, index) => (
              <div key={index} style={beneficiaryCardStyle}>
                <div style={beneficiaryHeaderStyle}>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#0F172A' }}>
                    Beneficiary {index + 1}
                  </h4>
                  {formData.beneficiaries.length > 1 && (
                    <Button type="button" variant="outline" size="small" onClick={() => removeBeneficiary(index)}>
                      Remove
                    </Button>
                  )}
                </div>

                <div style={formGridStyle}>
                  <div style={formGroupStyle}>
                    <Label>
                      Name <span style={{ color: '#EF4444' }}>*</span>
                    </Label>
                    <Input
                      type="text"
                      placeholder="Full name"
                      value={beneficiary.name}
                      onChange={(e) => handleBeneficiaryChange(index, 'name', e.target.value)}
                    />
                    {errors[`beneficiary_${index}_name`] && (
                      <div style={errorStyle}>{errors[`beneficiary_${index}_name`]}</div>
                    )}
                  </div>

                  <div style={formGroupStyle}>
                    <Label>
                      Date of Birth <span style={{ color: '#EF4444' }}>*</span>
                    </Label>
                    <Input
                      type="date"
                      value={beneficiary.dateOfBirth}
                      onChange={(e) => handleBeneficiaryChange(index, 'dateOfBirth', e.target.value)}
                    />
                    {errors[`beneficiary_${index}_dateOfBirth`] && (
                      <div style={errorStyle}>{errors[`beneficiary_${index}_dateOfBirth`]}</div>
                    )}
                  </div>
                </div>

                <div style={formGridStyle}>
                  <div style={formGroupStyle}>
                    <Label>
                      Relationship <span style={{ color: '#EF4444' }}>*</span>
                    </Label>
                    <select
                      value={beneficiary.relationship}
                      onChange={(e) => handleBeneficiaryChange(index, 'relationship', e.target.value)}
                      style={selectStyle}
                    >
                      {relationships.map((rel) => (
                        <option key={rel.value} value={rel.value}>
                          {rel.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div style={formGroupStyle}>
                    <Label>
                      Percentage <span style={{ color: '#EF4444' }}>*</span>
                    </Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      max="100"
                      placeholder="0.00"
                      value={beneficiary.percentage}
                      onChange={(e) => handleBeneficiaryChange(index, 'percentage', e.target.value)}
                    />
                    {errors[`beneficiary_${index}_percentage`] && (
                      <div style={errorStyle}>{errors[`beneficiary_${index}_percentage`]}</div>
                    )}
                  </div>
                </div>

                <div style={formGroupStyle}>
                  <Label>
                    Address <span style={{ color: '#EF4444' }}>*</span>
                  </Label>
                  <textarea
                    placeholder="Full address"
                    value={beneficiary.address}
                    onChange={(e) => handleBeneficiaryChange(index, 'address', e.target.value)}
                    rows={2}
                    style={{
                      width: '100%',
                      padding: '0.5rem 0.75rem',
                      border: '1px solid #D1D5DB',
                      borderRadius: '0.375rem',
                      boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                      fontSize: '1rem',
                      lineHeight: '1.5',
                      outline: 'none',
                      fontFamily: 'inherit',
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#3B82F6';
                      e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = '#D1D5DB';
                      e.target.style.boxShadow = '0 1px 2px 0 rgba(0, 0, 0, 0.05)';
                    }}
                  />
                  {errors[`beneficiary_${index}_address`] && (
                    <div style={errorStyle}>{errors[`beneficiary_${index}_address`]}</div>
                  )}
                </div>
              </div>
            ))}

            {/* Percentage Total */}
            <div style={percentageTotalStyle}>
              <span>Total Percentage:</span>
              <span style={{ fontSize: '1.2rem', fontFamily: 'monospace' }}>{totalPercentage.toFixed(2)}%</span>
            </div>
            {errors.beneficiaryTotal && <div style={errorStyle}>{errors.beneficiaryTotal}</div>}

            <Button type="button" variant="secondary" onClick={addBeneficiary} style={{ marginTop: '12px' }}>
              + Add Beneficiary
            </Button>
          </div>
        </div>
      )}

      {/* Step 4: Additional Details */}
      {currentStep === 4 && (
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
            Additional information
          </h3>

          {isEditing && (
            <div style={formGroupStyle}>
              <Label>Status</Label>
              <select value={formData.status} onChange={(e) => handleChange('status', e.target.value)} style={selectStyle}>
                {statuses.map((status) => (
                  <option key={status.value} value={status.value}>
                    {status.label}
                  </option>
                ))}
              </select>
              <div style={helpTextStyle}>Current status of the policy</div>
            </div>
          )}

          <div style={formGroupStyle}>
            <Label>Notes</Label>
            <textarea
              placeholder="Any additional information about this policy..."
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              rows={4}
              style={{
                width: '100%',
                padding: '0.5rem 0.75rem',
                border: '1px solid #D1D5DB',
                borderRadius: '0.375rem',
                boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                fontSize: '1rem',
                lineHeight: '1.5',
                outline: 'none',
                fontFamily: 'inherit',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#3B82F6';
                e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#D1D5DB';
                e.target.style.boxShadow = '0 1px 2px 0 rgba(0, 0, 0, 0.05)';
              }}
            />
            <div style={helpTextStyle}>Optional notes or reminders about this policy</div>
          </div>

          {/* Summary */}
          <div style={calloutStyle}>
            <h4 style={{ fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>Policy Summary</h4>
            <div style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
              <p>
                <strong>Provider:</strong> {formData.provider || 'Not specified'} ({formData.providerCountry})
              </p>
              <p>
                <strong>Type:</strong> {policyTypes.find((t) => t.value === formData.policyType)?.label}
              </p>
              <p>
                <strong>Cover:</strong>{' '}
                {formData.coverAmount
                  ? `${currencies.find((c) => c.value === formData.currency)?.label?.match(/\((.+)\)/)?.[1] || formData.currency}${parseFloat(formData.coverAmount).toLocaleString()}`
                  : 'Not specified'}
              </p>
              <p>
                <strong>Premium:</strong>{' '}
                {formData.premiumAmount
                  ? `${currencies.find((c) => c.value === formData.currency)?.label?.match(/\((.+)\)/)?.[1] || formData.currency}${parseFloat(formData.premiumAmount).toLocaleString()} ${frequencies.find((f) => f.value === formData.premiumFrequency)?.label.toLowerCase()}`
                  : 'Not specified'}
              </p>
              <p>
                <strong>Beneficiaries:</strong> {formData.beneficiaries.filter((b) => b.name.trim()).length}
              </p>
              {formData.writtenInTrust && (
                <p style={{ color: '#10B981', fontWeight: 600 }}>✓ Written in Trust (IHT-efficient)</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div style={actionsStyle}>
        <div style={{ display: 'flex', gap: '12px' }}>
          {currentStep > 1 && (
            <Button type="button" variant="secondary" onClick={handlePrevious}>
              ← Previous
            </Button>
          )}
          <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
        </div>
        <div>
          {currentStep < totalSteps ? (
            <Button type="button" variant="primary" onClick={handleNext}>
              Next →
            </Button>
          ) : (
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? 'Saving...' : isEditing ? 'Update Policy' : 'Add Policy'}
            </Button>
          )}
        </div>
      </div>
    </form>
  );
}
