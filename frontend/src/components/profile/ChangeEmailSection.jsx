import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from 'internal-packages/ui';
import { Button } from 'internal-packages/ui';
import { Input } from 'internal-packages/ui';
import { Label } from 'internal-packages/ui';
import { Alert } from 'internal-packages/ui';
import { profileEndpoints } from '../../utils/api';
import { validateEmail } from '../../utils/auth';

export function ChangeEmailSection({ currentEmail }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    newEmail: '',
    password: '',
  });

  const [validationErrors, setValidationErrors] = useState({});

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

    // Validate email
    if (!formData.newEmail) {
      errors.newEmail = 'Email is required';
    } else if (!validateEmail(formData.newEmail)) {
      errors.newEmail = 'Please enter a valid email address';
    } else if (formData.newEmail.toLowerCase() === currentEmail?.toLowerCase()) {
      errors.newEmail = 'New email must be different from current email';
    }

    // Password required
    if (!formData.password) {
      errors.password = 'Password is required to confirm email change';
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
      await profileEndpoints.changeEmail(formData.newEmail, formData.password);

      setSuccess(
        `Verification email sent to ${formData.newEmail}. Please check your inbox and click the verification link to complete the email change.`
      );

      // Reset form
      setFormData({
        newEmail: '',
        password: '',
      });
    } catch (err) {
      setError(err.message || 'Failed to send verification email. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Change your email address</CardTitle>
        <p style={{ marginTop: '8px', color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
          Your email is used to sign in and receive important notifications. Changing it requires verification.
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
              backgroundColor: '#DBEAFE',
              border: '1px solid #3B82F6',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '24px',
            }}
          >
            <p style={{ color: '#1E40AF', fontSize: '0.875rem', fontWeight: 500, marginBottom: '8px' }}>
              Important:
            </p>
            <ul style={{ color: '#1E40AF', fontSize: '0.875rem', lineHeight: '1.7', paddingLeft: '20px' }}>
              <li>A notification has been sent to your current email address ({currentEmail})</li>
              <li>Your email won't change until you click the verification link</li>
              <li>The verification link expires in 24 hours</li>
            </ul>
          </div>
        )}

        {/* How it works info */}
        <div
          style={{
            backgroundColor: '#F8FAFC',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '24px',
          }}
        >
          <p style={{ fontSize: '0.875rem', fontWeight: 500, marginBottom: '8px' }}>
            How email change works:
          </p>
          <ol style={{ fontSize: '0.875rem', color: '#475569', lineHeight: '1.7', paddingLeft: '20px' }}>
            <li>Enter your new email address and password</li>
            <li>We'll send a verification link to your new email</li>
            <li>Click the link to confirm the change</li>
            <li>Your email will be updated and you'll be notified</li>
          </ol>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gap: '24px' }}>
            {/* Current Email (read-only) */}
            <div>
              <Label htmlFor="currentEmail">Current email address</Label>
              <Input
                id="currentEmail"
                value={currentEmail || ''}
                disabled
                style={{ marginTop: '8px', backgroundColor: '#F8FAFC' }}
              />
            </div>

            {/* New Email */}
            <div>
              <Label htmlFor="newEmail">New email address</Label>
              <p style={{ fontSize: '0.875rem', color: '#475569', marginTop: '4px' }}>
                Enter your new email address. We'll send you a verification link.
              </p>
              <Input
                id="newEmail"
                name="newEmail"
                type="email"
                value={formData.newEmail}
                onChange={handleInputChange}
                disabled={loading}
                placeholder="your.new.email@example.com"
                style={{ marginTop: '8px' }}
                error={validationErrors.newEmail}
                autoComplete="email"
              />
              {validationErrors.newEmail && (
                <p style={{ fontSize: '0.875rem', color: '#EF4444', marginTop: '4px' }}>
                  {validationErrors.newEmail}
                </p>
              )}
            </div>

            {/* Password Confirmation */}
            <div>
              <Label htmlFor="password">Confirm your password</Label>
              <p style={{ fontSize: '0.875rem', color: '#475569', marginTop: '4px' }}>
                Enter your current password to authorize this change
              </p>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleInputChange}
                disabled={loading}
                style={{ marginTop: '8px' }}
                error={validationErrors.password}
                autoComplete="current-password"
              />
              {validationErrors.password && (
                <p style={{ fontSize: '0.875rem', color: '#EF4444', marginTop: '4px' }}>
                  {validationErrors.password}
                </p>
              )}
            </div>

            {/* Submit Button */}
            <div style={{ marginTop: '8px' }}>
              <Button type="submit" disabled={loading}>
                {loading ? 'Sending verification email...' : 'Send verification email'}
              </Button>
            </div>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
