import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from 'internal-packages/ui';
import { Button } from 'internal-packages/ui';
import { Input } from 'internal-packages/ui';
import { Label } from 'internal-packages/ui';
import { Alert } from 'internal-packages/ui';
import { profileEndpoints } from '../../utils/api';
import { validatePassword, getPasswordStrength } from '../../utils/auth';

export function ChangePasswordSection() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });

  const [validationErrors, setValidationErrors] = useState({});

  const passwordStrength = getPasswordStrength(formData.newPassword);

  function handleInputChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }

    // Clear messages
    setError('');
    setSuccess('');
  }

  function validateForm() {
    const errors = {};

    // Current password required
    if (!formData.currentPassword) {
      errors.currentPassword = 'Current password is required';
    }

    // New password validation
    const passwordValidation = validatePassword(formData.newPassword);
    if (!passwordValidation.valid) {
      errors.newPassword = passwordValidation.message;
    }

    // Confirm password match
    if (formData.newPassword !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }

    // Check that new password is different from current
    if (formData.currentPassword && formData.currentPassword === formData.newPassword) {
      errors.newPassword = 'New password must be different from current password';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!validateForm()) {
      setError('Please fix the errors below');
      return;
    }

    setLoading(true);

    try {
      await profileEndpoints.changePassword(formData.currentPassword, formData.newPassword);

      setSuccess('Your password has been changed successfully. All other devices will be logged out.');

      // Reset form
      setFormData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
    } catch (err) {
      setError(err.message || 'Failed to change password. Please check your current password and try again.');
    } finally {
      setLoading(false);
    }
  }

  function togglePasswordVisibility(field) {
    setShowPasswords((prev) => ({ ...prev, [field]: !prev[field] }));
  }

  const strengthColors = {
    none: '#94A3B8',
    weak: '#EF4444',
    medium: '#F59E0B',
    strong: '#10B981',
  };

  const strengthText = {
    none: '',
    weak: 'Weak',
    medium: 'Medium',
    strong: 'Strong',
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Change your password</CardTitle>
        <p style={{ marginTop: '8px', color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
          Choose a strong password to keep your financial information secure. We recommend using a password
          manager.
        </p>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert type="error" style={{ marginBottom: '24px' }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert type="success" style={{ marginBottom: '24px' }}>
            {success}
          </Alert>
        )}

        {success && (
          <div
            style={{
              backgroundColor: '#FEF3C7',
              border: '1px solid #F59E0B',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '24px',
            }}
          >
            <p style={{ color: '#92400E', fontSize: '0.875rem', fontWeight: 500 }}>
              Important: All other devices will be logged out for security.
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gap: '24px' }}>
            {/* Current Password */}
            <div>
              <Label htmlFor="currentPassword">Current password</Label>
              <p style={{ fontSize: '0.875rem', color: '#475569', marginTop: '4px' }}>
                Enter your current password to confirm your identity
              </p>
              <div style={{ position: 'relative', marginTop: '8px' }}>
                <Input
                  id="currentPassword"
                  name="currentPassword"
                  type={showPasswords.current ? 'text' : 'password'}
                  value={formData.currentPassword}
                  onChange={handleInputChange}
                  disabled={loading}
                  error={validationErrors.currentPassword}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('current')}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    color: '#475569',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    padding: '4px 8px',
                  }}
                >
                  {showPasswords.current ? 'Hide' : 'Show'}
                </button>
              </div>
              {validationErrors.currentPassword && (
                <p style={{ fontSize: '0.875rem', color: '#EF4444', marginTop: '4px' }}>
                  {validationErrors.currentPassword}
                </p>
              )}
            </div>

            {/* New Password */}
            <div>
              <Label htmlFor="newPassword">New password</Label>
              <div style={{ position: 'relative', marginTop: '8px' }}>
                <Input
                  id="newPassword"
                  name="newPassword"
                  type={showPasswords.new ? 'text' : 'password'}
                  value={formData.newPassword}
                  onChange={handleInputChange}
                  disabled={loading}
                  error={validationErrors.newPassword}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('new')}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    color: '#475569',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    padding: '4px 8px',
                  }}
                >
                  {showPasswords.new ? 'Hide' : 'Show'}
                </button>
              </div>

              {/* Password Strength Indicator */}
              {formData.newPassword && (
                <div style={{ marginTop: '8px' }}>
                  <div
                    style={{
                      height: '4px',
                      backgroundColor: '#E2E8F0',
                      borderRadius: '2px',
                      overflow: 'hidden',
                    }}
                  >
                    <div
                      style={{
                        height: '100%',
                        backgroundColor: strengthColors[passwordStrength],
                        width:
                          passwordStrength === 'weak'
                            ? '33%'
                            : passwordStrength === 'medium'
                            ? '66%'
                            : passwordStrength === 'strong'
                            ? '100%'
                            : '0%',
                        transition: 'width 250ms ease-in-out',
                      }}
                    />
                  </div>
                  <p
                    style={{
                      fontSize: '0.875rem',
                      color: strengthColors[passwordStrength],
                      marginTop: '4px',
                    }}
                  >
                    {strengthText[passwordStrength]}
                  </p>
                </div>
              )}

              {validationErrors.newPassword && (
                <p style={{ fontSize: '0.875rem', color: '#EF4444', marginTop: '4px' }}>
                  {validationErrors.newPassword}
                </p>
              )}

              {/* Password Requirements */}
              <div
                style={{
                  marginTop: '12px',
                  padding: '12px',
                  backgroundColor: '#F8FAFC',
                  borderRadius: '8px',
                }}
              >
                <p style={{ fontSize: '0.875rem', fontWeight: 500, marginBottom: '8px' }}>
                  Password requirements:
                </p>
                <ul style={{ fontSize: '0.875rem', color: '#475569', lineHeight: '1.7', paddingLeft: '20px' }}>
                  <li>At least 12 characters long</li>
                  <li>At least 1 uppercase letter</li>
                  <li>At least 1 lowercase letter</li>
                  <li>At least 1 number</li>
                  <li>At least 1 special character (!@#$%^&*)</li>
                </ul>
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <Label htmlFor="confirmPassword">Confirm new password</Label>
              <div style={{ position: 'relative', marginTop: '8px' }}>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showPasswords.confirm ? 'text' : 'password'}
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  disabled={loading}
                  error={validationErrors.confirmPassword}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('confirm')}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    color: '#475569',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    padding: '4px 8px',
                  }}
                >
                  {showPasswords.confirm ? 'Hide' : 'Show'}
                </button>
              </div>
              {validationErrors.confirmPassword && (
                <p style={{ fontSize: '0.875rem', color: '#EF4444', marginTop: '4px' }}>
                  {validationErrors.confirmPassword}
                </p>
              )}
            </div>

            {/* Submit Button */}
            <div style={{ marginTop: '8px' }}>
              <Button type="submit" disabled={loading}>
                {loading ? 'Changing password...' : 'Change password'}
              </Button>
            </div>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
