import React, { useState } from 'react';
import { Button, Input, Label, Card, CardHeader, CardTitle, CardContent, Checkbox, Alert } from 'internal-packages-ui';
import { authEndpoints } from '../../utils/api';
import { authStorage, validateEmail } from '../../utils/auth';

export function LoginForm({ onSuccess }) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false,
    totpCode: '',
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [requires2FA, setRequires2FA] = useState(false);
  const [showBackupCode, setShowBackupCode] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));

    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    if (requires2FA && !formData.totpCode) {
      newErrors.totpCode = '2FA code is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError('');

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const loginData = {
        email: formData.email,
        password: formData.password,
      };

      // Add TOTP code if 2FA is required
      if (requires2FA && formData.totpCode) {
        loginData.totpCode = formData.totpCode;
      }

      const response = await authEndpoints.login(loginData);

      // Check if 2FA is required
      if (response.requiresTwoFactor || response.requires_2fa) {
        setRequires2FA(true);
        setIsSubmitting(false);
        return;
      }

      // Store tokens and user data
      if (response.accessToken && response.refreshToken) {
        authStorage.setTokens(response.accessToken, response.refreshToken);
        authStorage.setUser(response.user);

        // Call success callback
        if (onSuccess) {
          onSuccess(response);
        } else {
          window.location.href = '/dashboard';
        }
      }
    } catch (error) {
      // Handle specific error cases
      if (error.status === 429) {
        setSubmitError('Too many login attempts. Please wait a few minutes before trying again.');
      } else if (error.status === 423) {
        setSubmitError('Account temporarily locked due to multiple failed login attempts. Please try again in 30 minutes.');
      } else if (error.status === 403) {
        setSubmitError('Please verify your email address before logging in.');
      } else if (error.status === 401) {
        if (requires2FA) {
          setSubmitError('Invalid or expired 2FA code. Please try again.');
        } else {
          setSubmitError('Invalid email or password.');
        }
      } else {
        setSubmitError(error.message || 'Login failed. Please try again.');
      }
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

  return (
    <div style={cardStyle}>
      {!requires2FA ? (
        <>
          <h1 style={headingStyle}>Welcome back to GoalPlan</h1>
          <p style={descriptionStyle}>
            Sign in to manage your financial planning across the UK and South Africa.
            We're here to help you understand your wealth, plan for the future, and make
            informed decisions about your finances.
          </p>
        </>
      ) : (
        <>
          <h1 style={headingStyle}>One more step to keep you secure</h1>
          <p style={descriptionStyle}>
            Enter the authentication code from your app to complete your sign in.
            This extra layer of security helps protect your financial information.
          </p>
        </>
      )}

      {submitError && (
        <Alert variant="error" style={{ marginBottom: '24px' }}>
          {submitError}
        </Alert>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {!requires2FA ? (
            <>
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
                  The email address you used when creating your account
                </p>
              </div>

              {/* Password */}
              <div>
                <label htmlFor="password" style={labelStyle}>
                  Your password
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
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }}>
                  <Checkbox
                    id="rememberMe"
                    name="rememberMe"
                    checked={formData.rememberMe}
                    onChange={handleChange}
                    disabled={isSubmitting}
                    label="Keep me signed in"
                  />
                  <a href="/forgot-password" style={{ ...linkStyle, fontSize: '0.875rem' }}>
                    Forgot your password?
                  </a>
                </div>
              </div>
            </>
          ) : (
            <>
              {/* 2FA Code Input */}
              <div>
                <label htmlFor="totpCode" style={labelStyle}>
                  {showBackupCode ? 'Your backup code' : 'Authentication code'}
                </label>
                <Input
                  type="text"
                  id="totpCode"
                  name="totpCode"
                  value={formData.totpCode}
                  onChange={handleChange}
                  error={errors.totpCode}
                  placeholder={showBackupCode ? 'Enter your backup code' : 'Enter 6-digit code'}
                  disabled={isSubmitting}
                  maxLength={showBackupCode ? 10 : 6}
                  required
                />
                <p style={helpTextStyle}>
                  {showBackupCode
                    ? 'Use one of the backup codes you saved during setup'
                    : 'Open your authenticator app and enter the 6-digit code'}
                </p>
              </div>

              {/* Toggle Backup Code */}
              <button
                type="button"
                onClick={() => {
                  setShowBackupCode(!showBackupCode);
                  setFormData((prev) => ({ ...prev, totpCode: '' }));
                  setErrors((prev) => ({ ...prev, totpCode: '' }));
                }}
                style={{ ...linkStyle, fontSize: '0.875rem', background: 'none', border: 'none', padding: 0, cursor: 'pointer' }}
              >
                {showBackupCode ? 'Use authenticator app instead' : 'Lost your device? Use a backup code'}
              </button>
            </>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            style={buttonStyle}
            disabled={isSubmitting}
            onMouseOver={(e) => !isSubmitting && (e.target.style.backgroundColor = '#1E40AF')}
            onMouseOut={(e) => !isSubmitting && (e.target.style.backgroundColor = '#2563EB')}
          >
            {isSubmitting ? 'Signing you in...' : requires2FA ? 'Verify and sign in' : 'Sign in to your account'}
          </Button>

          {/* Register Link */}
          {!requires2FA && (
            <p style={{ textAlign: 'center', fontSize: '0.875rem', color: '#475569' }}>
              New to GoalPlan?{' '}
              <a href="/register" style={linkStyle}>
                Create your account
              </a>
            </p>
          )}
        </form>
    </div>
  );
}
