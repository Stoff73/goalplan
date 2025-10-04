import React, { useState } from 'react';
import { Card, Button, Input, Label, Select, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * GoalForm - Create or edit financial goals with SMART validation
 *
 * Features:
 * - Narrative guidance throughout the form
 * - SMART criteria validation (Specific, Measurable, Achievable, Relevant, Time-bound)
 * - Goal type selection with icons
 * - Target amount and date inputs
 * - Priority selection with context
 * - Auto-contribution setup
 * - Expandable "Tell me more" sections
 * - Friendly validation messages
 *
 * Follows STYLEGUIDE.md:
 * - Conversational form labels
 * - Educational help text
 * - Progressive disclosure
 * - Clear validation feedback
 */
export function GoalForm({ goalId = null, initialData = null, onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    goal_type: initialData?.goal_type || 'EMERGENCY_FUND',
    title: initialData?.title || '',
    description: initialData?.description || '',
    target_amount: initialData?.target_amount || '',
    currency: initialData?.currency || 'GBP',
    target_date: initialData?.target_date || '',
    priority: initialData?.priority || 'MEDIUM',
    auto_contribution_enabled: initialData?.auto_contribution_enabled || false,
    auto_contribution_amount: initialData?.auto_contribution_amount || '',
    auto_contribution_frequency: initialData?.auto_contribution_frequency || 'MONTHLY',
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [showSmartTips, setShowSmartTips] = useState(false);
  const [showAutoContribution, setShowAutoContribution] = useState(false);

  const goalTypes = [
    { value: 'EMERGENCY_FUND', label: 'Emergency Fund', icon: '🛡️' },
    { value: 'HOUSE_PURCHASE', label: 'House Purchase', icon: '🏠' },
    { value: 'HOME_IMPROVEMENT', label: 'Home Improvement', icon: '🔨' },
    { value: 'DEBT_REPAYMENT', label: 'Debt Repayment', icon: '💳' },
    { value: 'VEHICLE_PURCHASE', label: 'Vehicle Purchase', icon: '🚗' },
    { value: 'WEDDING', label: 'Wedding', icon: '💍' },
    { value: 'HOLIDAY_TRAVEL', label: 'Holiday/Travel', icon: '✈️' },
    { value: 'EDUCATION_CHILDREN', label: "Children's Education", icon: '🎓' },
    { value: 'EDUCATION_SELF', label: 'Self Education', icon: '📚' },
    { value: 'RETIREMENT', label: 'Retirement', icon: '🌴' },
    { value: 'BUSINESS_START', label: 'Business Start', icon: '💼' },
    { value: 'INHERITANCE_PLANNING', label: 'Inheritance Planning', icon: '📜' },
    { value: 'FINANCIAL_INDEPENDENCE', label: 'Financial Independence', icon: '💰' },
    { value: 'CHARITABLE_GIVING', label: 'Charitable Giving', icon: '❤️' },
    { value: 'OTHER', label: 'Other', icon: '🎯' },
  ];

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Title validation (Specific)
    if (!formData.title || formData.title.trim().length < 3) {
      newErrors.title = 'Please give your goal a clear, specific name (at least 3 characters)';
    }

    // Target amount validation (Measurable)
    const targetAmount = parseFloat(formData.target_amount);
    if (!formData.target_amount || isNaN(targetAmount) || targetAmount <= 0) {
      newErrors.target_amount = 'Please enter a specific target amount (must be positive)';
    } else if (targetAmount < 100) {
      newErrors.target_amount = 'Target amount should be at least £100 for meaningful goals';
    } else if (targetAmount > 10000000) {
      newErrors.target_amount = 'Target amount seems unrealistically high (max £10,000,000)';
    }

    // Target date validation (Time-bound)
    if (!formData.target_date) {
      newErrors.target_date = 'Please set a target date to make your goal time-bound';
    } else {
      const targetDate = new Date(formData.target_date);
      const today = new Date();
      const monthsToGoal = (targetDate - today) / (1000 * 60 * 60 * 24 * 30);

      if (monthsToGoal < 6) {
        newErrors.target_date =
          'Your goal should be at least 6 months in the future for realistic planning';
      } else if (monthsToGoal > 600) {
        // 50 years
        newErrors.target_date = 'Your goal cannot be more than 50 years in the future';
      }
    }

    // Auto-contribution validation
    if (formData.auto_contribution_enabled) {
      const autoAmount = parseFloat(formData.auto_contribution_amount);
      if (!formData.auto_contribution_amount || isNaN(autoAmount) || autoAmount <= 0) {
        newErrors.auto_contribution_amount =
          'Please enter a positive amount for automatic contributions';
      } else if (autoAmount < 10) {
        newErrors.auto_contribution_amount =
          'Automatic contribution should be at least £10/month for meaningful progress';
      }
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

    try {
      const payload = {
        goal_type: formData.goal_type,
        title: formData.title.trim(),
        description: formData.description.trim() || null,
        target_amount: parseFloat(formData.target_amount),
        currency: formData.currency,
        target_date: formData.target_date,
        priority: formData.priority,
        auto_contribution_enabled: formData.auto_contribution_enabled,
        auto_contribution_amount: formData.auto_contribution_enabled
          ? parseFloat(formData.auto_contribution_amount)
          : null,
        auto_contribution_frequency: formData.auto_contribution_enabled
          ? formData.auto_contribution_frequency
          : null,
      };

      const url = goalId ? `/api/v1/goals/${goalId}` : '/api/v1/goals';
      const method = goalId ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        if (response.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }

        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save goal');
      }

      const result = await response.json();
      onSuccess(result);
    } catch (err) {
      setErrors({ submit: err.message });
      console.error('Error saving goal:', err);
    } finally {
      setLoading(false);
    }
  };

  // Styles
  const formContainerStyle = {
    maxWidth: '800px',
    margin: '0 auto',
  };

  const formSectionStyle = {
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

  const helpTextStyle = {
    fontSize: '0.9rem',
    color: '#475569',
    lineHeight: '1.7',
    marginBottom: '24px',
  };

  const fieldGroupStyle = {
    marginBottom: '24px',
  };

  const labelStyle = {
    display: 'block',
    fontSize: '0.95rem',
    fontWeight: 500,
    color: '#0F172A',
    marginBottom: '8px',
  };

  const inputStyle = {
    width: '100%',
    padding: '12px',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
    fontSize: '1rem',
  };

  const errorStyle = {
    color: '#EF4444',
    fontSize: '0.85rem',
    marginTop: '6px',
  };

  const goalTypeGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
    gap: '12px',
    marginBottom: '24px',
  };

  const goalTypeButtonStyle = (isSelected) => ({
    padding: '16px',
    borderRadius: '8px',
    border: isSelected ? '2px solid #2563EB' : '1px solid #E2E8F0',
    backgroundColor: isSelected ? '#EFF6FF' : '#FFFFFF',
    cursor: 'pointer',
    textAlign: 'center',
    transition: 'all 0.2s ease-in-out',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
  });

  const expandableSectionStyle = {
    marginTop: '16px',
    padding: '16px',
    backgroundColor: '#EFF6FF',
    border: '1px solid #BFDBFE',
    borderRadius: '8px',
  };

  const toggleButtonStyle = {
    background: 'none',
    border: 'none',
    color: '#2563EB',
    fontSize: '0.9rem',
    cursor: 'pointer',
    textDecoration: 'underline',
    padding: 0,
    marginTop: '8px',
  };

  return (
    <div style={formContainerStyle}>
      <form onSubmit={handleSubmit}>
        {/* Goal Type Selection */}
        <div style={formSectionStyle}>
          <h3 style={sectionHeadingStyle}>What are you saving for?</h3>
          <p style={helpTextStyle}>
            Choose the type of goal that best matches what you're working toward. This helps us
            provide tailored guidance and recommendations.
          </p>

          <div style={goalTypeGridStyle}>
            {goalTypes.map((type) => (
              <div
                key={type.value}
                style={goalTypeButtonStyle(formData.goal_type === type.value)}
                onClick={() => handleChange('goal_type', type.value)}
              >
                <span style={{ fontSize: '2rem' }}>{type.icon}</span>
                <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>{type.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Goal Details */}
        <div style={formSectionStyle}>
          <h3 style={sectionHeadingStyle}>Tell us about your goal</h3>
          <p style={helpTextStyle}>
            Give your goal a clear name and specify how much you need and when you need it by.
            Being specific makes it easier to track your progress.
          </p>

          <div style={fieldGroupStyle}>
            <label style={labelStyle} htmlFor="title">
              Goal Name *
            </label>
            <input
              id="title"
              type="text"
              value={formData.title}
              onChange={(e) => handleChange('title', e.target.value)}
              placeholder="e.g., House Deposit for London Flat"
              style={inputStyle}
              maxLength={100}
            />
            {errors.title && <div style={errorStyle}>{errors.title}</div>}
          </div>

          <div style={fieldGroupStyle}>
            <label style={labelStyle} htmlFor="description">
              Description (Optional)
            </label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              placeholder="Add any additional details about this goal..."
              style={{ ...inputStyle, minHeight: '80px', resize: 'vertical' }}
              maxLength={500}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px' }}>
            <div style={fieldGroupStyle}>
              <label style={labelStyle} htmlFor="target_amount">
                How much do you need? *
              </label>
              <input
                id="target_amount"
                type="number"
                value={formData.target_amount}
                onChange={(e) => handleChange('target_amount', e.target.value)}
                placeholder="e.g., 40000"
                style={inputStyle}
                step="0.01"
                min="0"
              />
              {errors.target_amount && <div style={errorStyle}>{errors.target_amount}</div>}
            </div>

            <div style={fieldGroupStyle}>
              <label style={labelStyle} htmlFor="currency">
                Currency
              </label>
              <select
                id="currency"
                value={formData.currency}
                onChange={(e) => handleChange('currency', e.target.value)}
                style={inputStyle}
              >
                <option value="GBP">£ GBP</option>
                <option value="ZAR">R ZAR</option>
                <option value="USD">$ USD</option>
                <option value="EUR">€ EUR</option>
              </select>
            </div>
          </div>

          <div style={fieldGroupStyle}>
            <label style={labelStyle} htmlFor="target_date">
              When do you need it by? *
            </label>
            <input
              id="target_date"
              type="date"
              value={formData.target_date}
              onChange={(e) => handleChange('target_date', e.target.value)}
              style={inputStyle}
              min={new Date(Date.now() + 180 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]} // 6 months from now
            />
            {errors.target_date && <div style={errorStyle}>{errors.target_date}</div>}
          </div>
        </div>

        {/* Priority */}
        <div style={formSectionStyle}>
          <h3 style={sectionHeadingStyle}>How important is this goal?</h3>
          <p style={helpTextStyle}>
            Priority helps you focus on what matters most when you have multiple goals. High
            priority goals get first claim on your savings budget.
          </p>

          <div style={{ display: 'flex', gap: '12px' }}>
            {['HIGH', 'MEDIUM', 'LOW'].map((priority) => (
              <button
                key={priority}
                type="button"
                onClick={() => handleChange('priority', priority)}
                style={{
                  flex: 1,
                  padding: '16px',
                  borderRadius: '8px',
                  border: formData.priority === priority ? '2px solid #2563EB' : '1px solid #E2E8F0',
                  backgroundColor: formData.priority === priority ? '#EFF6FF' : '#FFFFFF',
                  cursor: 'pointer',
                  fontSize: '1rem',
                  fontWeight: 500,
                  color: formData.priority === priority ? '#1E40AF' : '#475569',
                  transition: 'all 0.2s ease-in-out',
                }}
              >
                {priority === 'HIGH' && '🔥 '}{priority === 'MEDIUM' && '⭐ '}{priority === 'LOW' && '📌 '}
                {priority.charAt(0) + priority.slice(1).toLowerCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Auto-Contribution (Optional) */}
        <div style={formSectionStyle}>
          <h3 style={sectionHeadingStyle}>Automate your savings (optional)</h3>
          <p style={helpTextStyle}>
            Setting up automatic contributions makes it easier to stay on track. You can always
            adjust this later.
          </p>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={formData.auto_contribution_enabled}
                onChange={(e) => {
                  handleChange('auto_contribution_enabled', e.target.checked);
                  setShowAutoContribution(e.target.checked);
                }}
              />
              <span style={{ fontSize: '0.95rem', fontWeight: 500 }}>
                Yes, I want to set up automatic contributions
              </span>
            </label>
          </div>

          {showAutoContribution && formData.auto_contribution_enabled && (
            <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #E2E8F0' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px' }}>
                <div style={fieldGroupStyle}>
                  <label style={labelStyle} htmlFor="auto_contribution_amount">
                    Monthly Amount
                  </label>
                  <input
                    id="auto_contribution_amount"
                    type="number"
                    value={formData.auto_contribution_amount}
                    onChange={(e) => handleChange('auto_contribution_amount', e.target.value)}
                    placeholder="e.g., 500"
                    style={inputStyle}
                    step="0.01"
                    min="0"
                  />
                  {errors.auto_contribution_amount && (
                    <div style={errorStyle}>{errors.auto_contribution_amount}</div>
                  )}
                </div>

                <div style={fieldGroupStyle}>
                  <label style={labelStyle} htmlFor="auto_contribution_frequency">
                    Frequency
                  </label>
                  <select
                    id="auto_contribution_frequency"
                    value={formData.auto_contribution_frequency}
                    onChange={(e) => handleChange('auto_contribution_frequency', e.target.value)}
                    style={inputStyle}
                  >
                    <option value="WEEKLY">Weekly</option>
                    <option value="MONTHLY">Monthly</option>
                    <option value="QUARTERLY">Quarterly</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* SMART Tips (Expandable) */}
        <div style={{ ...formSectionStyle, backgroundColor: '#F0FDF4', border: '1px solid #86EFAC' }}>
          <h4 style={{ ...sectionHeadingStyle, color: '#166534' }}>
            💡 Your goal follows SMART criteria
          </h4>
          <p style={{ ...helpTextStyle, color: '#166534', marginBottom: '8px' }}>
            This form helps you create goals that are Specific, Measurable, Achievable, Relevant,
            and Time-bound - the best way to ensure success.
          </p>

          <button type="button" onClick={() => setShowSmartTips(!showSmartTips)} style={toggleButtonStyle}>
            {showSmartTips ? '▼' : '▶'} Tell me more about SMART goals
          </button>

          {showSmartTips && (
            <div style={{ marginTop: '16px', color: '#166534' }}>
              <ul style={{ paddingLeft: '20px', lineHeight: '1.7' }}>
                <li style={{ marginBottom: '8px' }}>
                  <strong>Specific:</strong> Clear goal name and type (e.g., "House Deposit" not "Save Money")
                </li>
                <li style={{ marginBottom: '8px' }}>
                  <strong>Measurable:</strong> Exact target amount so you can track progress
                </li>
                <li style={{ marginBottom: '8px' }}>
                  <strong>Achievable:</strong> Realistic based on your income and timeline
                </li>
                <li style={{ marginBottom: '8px' }}>
                  <strong>Relevant:</strong> Aligned with your life priorities
                </li>
                <li>
                  <strong>Time-bound:</strong> Clear target date to create urgency and focus
                </li>
              </ul>
            </div>
          )}
        </div>

        {/* Submit Buttons */}
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" disabled={loading}>
            {loading ? 'Saving...' : goalId ? 'Update Goal' : 'Create Goal'}
          </Button>
        </div>

        {errors.submit && (
          <Alert variant="error" style={{ marginTop: '16px' }}>
            {errors.submit}
          </Alert>
        )}
      </form>
    </div>
  );
}
