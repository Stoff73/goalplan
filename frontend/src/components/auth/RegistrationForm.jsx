import React, { useState } from 'react';
import { Button, Input, Label, Card, CardHeader, CardTitle, CardContent, Checkbox, Select, Alert } from 'internal-packages-ui';
import { validateEmail, validatePassword, getPasswordStrength } from '../../utils/auth';
import { authEndpoints } from '../../utils/api';

export function RegistrationForm({ onSuccess }) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    country: '',
    termsAccepted: false,
    marketingConsent: false,
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const countryOptions = [
    { value: 'UK', label: 'United Kingdom' },
    { value: 'SA', label: 'South Africa' },
    { value: 'BOTH', label: 'Both Countries' },
  ];

  const passwordStrength = getPasswordStrength(formData.password);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));

    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else {
      const passwordValidation = validatePassword(formData.password);
      if (!passwordValidation.valid) {
        newErrors.password = passwordValidation.message;
      }
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // Name validation
    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    }

    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    }

    // Country validation
    if (!formData.country) {
      newErrors.country = 'Please select a country preference';
    }

    // Terms acceptance
    if (!formData.termsAccepted) {
      newErrors.termsAccepted = 'You must accept the terms and conditions';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError('');
    setSubmitSuccess(false);

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await authEndpoints.register({
        email: formData.email,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName,
        country: formData.country,
        termsAccepted: formData.termsAccepted,
        marketingConsent: formData.marketingConsent,
      });

      setSubmitSuccess(true);

      // Call success callback if provided
      if (onSuccess) {
        onSuccess(response);
      }
    } catch (error) {
      setSubmitError(error.message || 'Registration failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const cardStyle = {
    maxWidth: '640px',
    margin: '0 auto',
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    lineHeight: '1.7',
  };

  const headingStyle = {
    fontSize: '1.8rem',
    fontWeight: 'bold',
    color: '#0F172A',
    marginBottom: '16px',
  };

  const descriptionStyle = {
    color: '#475569',
    marginBottom: '32px',
    lineHeight: '1.7',
  };

  const labelStyle = {
    display: 'block',
    fontSize: '0.875rem',
    fontWeight: 500,
    color: '#0F172A',
    marginBottom: '8px',
  };

  const helpTextStyle = {
    fontSize: '0.875rem',
    color: '#475569',
    marginTop: '8px',
  };

  const buttonStyle = {
    width: '100%',
    padding: '12px 24px',
    backgroundColor: '#2563EB',
    color: '#FFFFFF',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 150ms ease-in-out',
  };

  const linkStyle = {
    color: '#2563EB',
    textDecoration: 'none',
    fontWeight: 500,
  };

  if (submitSuccess) {
    return (
      <div style={cardStyle}>
        <h1 style={headingStyle}>Welcome to GoalPlan!</h1>
        <Alert variant="success" style={{ marginBottom: '24px' }}>
          <p style={{ fontWeight: 600, marginBottom: '8px' }}>Your account has been created</p>
          <p style={{ color: '#475569', lineHeight: '1.7' }}>
            We've sent a verification email to <strong>{formData.email}</strong>.
            Please check your inbox and click the verification link to activate your account
            and start managing your finances across the UK and South Africa.
          </p>
        </Alert>
        <p style={{ fontSize: '0.875rem', color: '#475569', marginTop: '24px' }}>
          Didn't receive the email? Check your spam folder or{' '}
          <button
            type="button"
            style={{ ...linkStyle, fontSize: '0.875rem', background: 'none', border: 'none', padding: 0, cursor: 'pointer' }}
            onClick={() => authEndpoints.resendVerification(formData.email)}
          >
            request a new verification email
          </button>
        </p>
      </div>
    );
  }

  return (
    <div style={cardStyle}>
      <h1 style={headingStyle}>Start your financial planning journey</h1>
      <p style={descriptionStyle}>
        Create your GoalPlan account to manage your wealth across the UK and South Africa.
        We'll help you understand your financial position, plan for the future, and make
        informed decisions about your money. Let's get started.
      </p>

      {submitError && (
        <Alert variant="error" style={{ marginBottom: '24px' }}>
          {submitError}
        </Alert>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Email */}
          <div>
            <label htmlFor="email" style={labelStyle}>
              Your email address
            </label>
            <Input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              error={errors.email}
              placeholder="you@example.com"
              disabled={isSubmitting}
              required
            />
            <p style={helpTextStyle}>
              We'll use this to send you important updates about your account
            </p>
          </div>

          {/* First Name */}
          <div>
            <label htmlFor="firstName" style={labelStyle}>
              Your first name
            </label>
            <Input
              type="text"
              id="firstName"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              error={errors.firstName}
              disabled={isSubmitting}
              required
            />
          </div>

          {/* Last Name */}
          <div>
            <label htmlFor="lastName" style={labelStyle}>
              Your last name
            </label>
            <Input
              type="text"
              id="lastName"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              error={errors.lastName}
              disabled={isSubmitting}
              required
            />
          </div>

          {/* Password */}
          <div>
            <label htmlFor="password" style={labelStyle}>
              Create a password
            </label>
            <Input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              error={errors.password}
              disabled={isSubmitting}
              required
            />
            {formData.password && (
              <div style={{ marginTop: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ flex: 1, height: '8px', backgroundColor: '#E2E8F0', borderRadius: '9999px', overflow: 'hidden' }}>
                    <div
                      style={{
                        height: '100%',
                        width: passwordStrength === 'weak' ? '33%' : passwordStrength === 'medium' ? '66%' : '100%',
                        backgroundColor: passwordStrength === 'weak' ? '#EF4444' : passwordStrength === 'medium' ? '#F59E0B' : '#10B981',
                        transition: 'all 150ms ease-in-out',
                      }}
                    />
                  </div>
                  <span style={{ fontSize: '0.75rem', color: '#475569', textTransform: 'capitalize' }}>{passwordStrength}</span>
                </div>
                <p style={helpTextStyle}>
                  Use at least 8 characters with a mix of letters, numbers, and symbols
                </p>
              </div>
            )}
          </div>

          {/* Confirm Password */}
          <div>
            <label htmlFor="confirmPassword" style={labelStyle}>
              Confirm your password
            </label>
            <Input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              error={errors.confirmPassword}
              disabled={isSubmitting}
              required
            />
          </div>

          {/* Country Selection */}
          <div>
            <label htmlFor="country" style={labelStyle}>
              Where do you manage your finances?
            </label>
            <Select
              id="country"
              name="country"
              value={formData.country}
              onChange={handleChange}
              options={countryOptions}
              error={errors.country}
              disabled={isSubmitting}
              placeholder="Select your country"
              required
            />
            <p style={helpTextStyle}>
              Choose where you primarily manage your finances. You can update this later.
            </p>
          </div>

          {/* Terms Acceptance */}
          <div>
            <Checkbox
              id="termsAccepted"
              name="termsAccepted"
              checked={formData.termsAccepted}
              onChange={handleChange}
              disabled={isSubmitting}
              label={
                <span style={{ fontSize: '0.875rem', color: '#475569' }}>
                  I accept the{' '}
                  <a href="/terms" style={linkStyle} target="_blank" rel="noopener noreferrer">
                    Terms and Conditions
                  </a>{' '}
                  and{' '}
                  <a href="/privacy" style={linkStyle} target="_blank" rel="noopener noreferrer">
                    Privacy Policy
                  </a>
                </span>
              }
            />
            {errors.termsAccepted && (
              <p style={{ marginTop: '4px', fontSize: '0.875rem', color: '#EF4444' }}>{errors.termsAccepted}</p>
            )}
          </div>

          {/* Marketing Consent */}
          <div>
            <Checkbox
              id="marketingConsent"
              name="marketingConsent"
              checked={formData.marketingConsent}
              onChange={handleChange}
              disabled={isSubmitting}
              label={
                <span style={{ fontSize: '0.875rem', color: '#475569' }}>
                  Send me tips and updates about financial planning
                </span>
              }
            />
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            style={buttonStyle}
            disabled={isSubmitting}
            onMouseOver={(e) => !isSubmitting && (e.target.style.backgroundColor = '#1E40AF')}
            onMouseOut={(e) => !isSubmitting && (e.target.style.backgroundColor = '#2563EB')}
          >
            {isSubmitting ? 'Creating your account...' : 'Create my account'}
          </Button>

          {/* Login Link */}
          <p style={{ textAlign: 'center', fontSize: '0.875rem', color: '#475569' }}>
            Already have an account?{' '}
            <a href="/login" style={linkStyle}>
              Sign in instead
            </a>
          </p>
        </form>
    </div>
  );
}
