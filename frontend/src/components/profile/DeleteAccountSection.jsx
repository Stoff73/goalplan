import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from 'internal-packages/ui';
import { Button } from 'internal-packages/ui';
import { Input } from 'internal-packages/ui';
import { Label } from 'internal-packages/ui';
import { Checkbox } from 'internal-packages/ui';
import { Alert } from 'internal-packages/ui';
import { profileEndpoints } from '../../utils/api';
import { authStorage } from '../../utils/auth';
import { getAccountDeletionDate } from '../../utils/profile';

export function DeleteAccountSection() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);

  const [formData, setFormData] = useState({
    password: '',
    exportData: false,
  });

  const [validationErrors, setValidationErrors] = useState({});

  function handleInputChange(e) {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));

    // Clear validation error
    if (validationErrors[name]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }

    setError('');
  }

  function validateForm() {
    const errors = {};

    if (!formData.password) {
      errors.password = 'Password is required to delete your account';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  }

  function handleDeleteClick() {
    setError('');

    if (!validateForm()) {
      setError('Please enter your password to continue');
      return;
    }

    // Show confirmation modal
    setShowModal(true);
  }

  function handleCancelDelete() {
    setShowModal(false);
    setError('');
  }

  async function handleConfirmDelete() {
    setLoading(true);
    setError('');

    try {
      const response = await profileEndpoints.deleteAccount(formData.password, formData.exportData);

      // Clear auth data
      authStorage.clear();

      // Show success message and redirect
      alert(
        `Your account has been scheduled for deletion on ${getAccountDeletionDate()}. ` +
          (formData.exportData ? 'Your data export will be emailed to you shortly.' : '') +
          ' You have been logged out.'
      );

      navigate('/login');
    } catch (err) {
      setError(err.message || 'Failed to delete account. Please check your password and try again.');
      setShowModal(false);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Card style={{ border: '2px solid #FEE2E2', backgroundColor: '#FEF2F2' }}>
        <CardHeader>
          <CardTitle style={{ color: '#991B1B' }}>Delete your account</CardTitle>
          <p style={{ marginTop: '8px', color: '#7F1D1D', fontSize: '0.95rem', lineHeight: '1.7' }}>
            This will permanently delete your account and all associated data after 30 days. This action cannot
            be undone.
          </p>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert type="error" style={{ marginBottom: '24px' }}>
              {error}
            </Alert>
          )}

          {/* Warning Box */}
          <div
            style={{
              backgroundColor: '#FEF3C7',
              border: '2px solid #F59E0B',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '24px',
            }}
          >
            <p style={{ color: '#92400E', fontSize: '0.875rem', fontWeight: 600, marginBottom: '8px' }}>
              Warning: This will delete:
            </p>
            <ul style={{ color: '#92400E', fontSize: '0.875rem', lineHeight: '1.7', paddingLeft: '20px' }}>
              <li>All your financial data (accounts, transactions, balances)</li>
              <li>Tax records and calculations</li>
              <li>Investment and retirement information</li>
              <li>All saved documents and reports</li>
              <li>Your profile and preferences</li>
            </ul>
          </div>

          {/* 30-day retention notice */}
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
              30-day grace period:
            </p>
            <p style={{ color: '#1E40AF', fontSize: '0.875rem', lineHeight: '1.7' }}>
              Your account will be scheduled for deletion on{' '}
              <strong>{getAccountDeletionDate()}</strong>. During this period, you can contact support to
              cancel the deletion and restore your account.
            </p>
          </div>

          <div style={{ display: 'grid', gap: '24px' }}>
            {/* Export Data Checkbox */}
            <div style={{ display: 'flex', alignItems: 'start', gap: '12px' }}>
              <Checkbox
                id="exportData"
                name="exportData"
                checked={formData.exportData}
                onChange={handleInputChange}
                disabled={loading}
              />
              <div>
                <Label htmlFor="exportData" style={{ cursor: 'pointer' }}>
                  Download a copy of your data before deletion (recommended)
                </Label>
                <p style={{ fontSize: '0.875rem', color: '#475569', marginTop: '4px' }}>
                  We'll email you a complete export of your financial data in JSON format
                </p>
              </div>
            </div>

            {/* Password Confirmation */}
            <div>
              <Label htmlFor="password">Confirm your password</Label>
              <p style={{ fontSize: '0.875rem', color: '#475569', marginTop: '4px' }}>
                Enter your password to authorize account deletion
              </p>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleInputChange}
                disabled={loading}
                placeholder="Enter your password"
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

            {/* Delete Button */}
            <div style={{ marginTop: '8px' }}>
              <Button variant="danger" onClick={handleDeleteClick} disabled={loading}>
                Delete my account
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Confirmation Modal */}
      {showModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
          }}
          onClick={handleCancelDelete}
        >
          <div
            style={{
              backgroundColor: '#FFFFFF',
              borderRadius: '12px',
              padding: '32px',
              maxWidth: '500px',
              width: '90%',
              boxShadow: '0 20px 25px rgba(0, 0, 0, 0.1)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0F172A', marginBottom: '16px' }}>
              Are you absolutely sure?
            </h2>

            <div
              style={{
                backgroundColor: '#FEF2F2',
                border: '2px solid #EF4444',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '24px',
              }}
            >
              <p style={{ color: '#991B1B', fontSize: '0.95rem', lineHeight: '1.7', fontWeight: 500 }}>
                This will delete all your financial data, tax records, and account history. This action cannot
                be undone after the 30-day grace period.
              </p>
            </div>

            <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7', marginBottom: '24px' }}>
              Your account will be permanently deleted on{' '}
              <strong style={{ color: '#0F172A' }}>{getAccountDeletionDate()}</strong>.
              {formData.exportData && ' You will receive a data export via email shortly.'}
            </p>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <Button variant="secondary" onClick={handleCancelDelete} disabled={loading}>
                Cancel
              </Button>
              <Button variant="danger" onClick={handleConfirmDelete} disabled={loading}>
                {loading ? 'Deleting account...' : 'Yes, delete my account'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
