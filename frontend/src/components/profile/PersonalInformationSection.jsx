import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from 'internal-packages/ui';
import { Button } from 'internal-packages/ui';
import { Input } from 'internal-packages/ui';
import { Label } from 'internal-packages/ui';
import { Select } from 'internal-packages/ui';
import { Alert } from 'internal-packages/ui';
import { profileEndpoints } from '../../utils/api';
import {
  validatePhone,
  validateDateOfBirth,
  validateTimezone,
  commonTimezones,
  formatDateForInput,
} from '../../utils/profile';

export function PersonalInformationSection({ profile, onProfileUpdate }) {
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form state
  const [formData, setFormData] = useState({
    firstName: profile?.firstName || '',
    lastName: profile?.lastName || '',
    phone: profile?.phone || '',
    dateOfBirth: profile?.dateOfBirth ? formatDateForInput(profile.dateOfBirth) : '',
    addressLine1: profile?.addressLine1 || '',
    addressLine2: profile?.addressLine2 || '',
    city: profile?.city || '',
    postalCode: profile?.postalCode || '',
    country: profile?.country || '',
    timezone: profile?.timezone || '',
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

    // Clear success/error messages on change
    setError('');
    setSuccess('');
  }

  function validateForm() {
    const errors = {};

    // Validate phone
    const phoneValidation = validatePhone(formData.phone);
    if (!phoneValidation.valid) {
      errors.phone = phoneValidation.message;
    }

    // Validate date of birth
    const dobValidation = validateDateOfBirth(formData.dateOfBirth);
    if (!dobValidation.valid) {
      errors.dateOfBirth = dobValidation.message;
    }

    // Validate timezone
    const timezoneValidation = validateTimezone(formData.timezone);
    if (!timezoneValidation.valid) {
      errors.timezone = timezoneValidation.message;
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSave() {
    setError('');
    setSuccess('');

    if (!validateForm()) {
      setError('Please fix the errors below');
      return;
    }

    setLoading(true);

    try {
      const response = await profileEndpoints.updateProfile(formData);

      setSuccess('Your personal information has been updated successfully');
      setIsEditing(false);

      // Update parent component with new profile data
      if (onProfileUpdate) {
        onProfileUpdate(response);
      }
    } catch (err) {
      setError(err.message || 'Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function handleCancel() {
    // Reset form to original profile data
    setFormData({
      firstName: profile?.firstName || '',
      lastName: profile?.lastName || '',
      phone: profile?.phone || '',
      dateOfBirth: profile?.dateOfBirth ? formatDateForInput(profile.dateOfBirth) : '',
      addressLine1: profile?.addressLine1 || '',
      addressLine2: profile?.addressLine2 || '',
      city: profile?.city || '',
      postalCode: profile?.postalCode || '',
      country: profile?.country || '',
      timezone: profile?.timezone || '',
    });
    setValidationErrors({});
    setError('');
    setSuccess('');
    setIsEditing(false);
  }

  return (
    <Card>
      <CardHeader>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <CardTitle>Your personal information</CardTitle>
            <p style={{ marginTop: '8px', color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
              We use this information to personalize your experience and comply with tax regulations in
              the UK and South Africa.
            </p>
          </div>
          {!isEditing && (
            <Button variant="secondary" onClick={() => setIsEditing(true)}>
              Edit
            </Button>
          )}
        </div>
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

        <div style={{ display: 'grid', gap: '24px' }}>
          {/* Name */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <Label htmlFor="firstName">First name</Label>
              <Input
                id="firstName"
                name="firstName"
                value={formData.firstName}
                onChange={handleInputChange}
                disabled={!isEditing || loading}
                style={{ marginTop: '8px' }}
              />
            </div>
            <div>
              <Label htmlFor="lastName">Last name</Label>
              <Input
                id="lastName"
                name="lastName"
                value={formData.lastName}
                onChange={handleInputChange}
                disabled={!isEditing || loading}
                style={{ marginTop: '8px' }}
              />
            </div>
          </div>

          {/* Phone */}
          <div>
            <Label htmlFor="phone">Phone number</Label>
            <p style={{ fontSize: '0.875rem', color: '#475569', marginTop: '4px' }}>
              We'll use this to contact you about important account matters
            </p>
            <Input
              id="phone"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleInputChange}
              disabled={!isEditing || loading}
              placeholder="+44 7700 900000"
              style={{ marginTop: '8px' }}
              error={validationErrors.phone}
            />
            {validationErrors.phone && (
              <p style={{ fontSize: '0.875rem', color: '#EF4444', marginTop: '4px' }}>
                {validationErrors.phone}
              </p>
            )}
          </div>

          {/* Date of Birth */}
          <div>
            <Label htmlFor="dateOfBirth">Date of birth</Label>
            <p style={{ fontSize: '0.875rem', color: '#475569', marginTop: '4px' }}>
              Required for tax residency calculations and age-restricted features
            </p>
            <Input
              id="dateOfBirth"
              name="dateOfBirth"
              type="date"
              value={formData.dateOfBirth}
              onChange={handleInputChange}
              disabled={!isEditing || loading}
              style={{ marginTop: '8px' }}
              error={validationErrors.dateOfBirth}
            />
            {validationErrors.dateOfBirth && (
              <p style={{ fontSize: '0.875rem', color: '#EF4444', marginTop: '4px' }}>
                {validationErrors.dateOfBirth}
              </p>
            )}
          </div>

          {/* Address */}
          <div>
            <Label htmlFor="addressLine1">Address</Label>
            <Input
              id="addressLine1"
              name="addressLine1"
              value={formData.addressLine1}
              onChange={handleInputChange}
              disabled={!isEditing || loading}
              placeholder="Street address"
              style={{ marginTop: '8px' }}
            />
          </div>

          <Input
            id="addressLine2"
            name="addressLine2"
            value={formData.addressLine2}
            onChange={handleInputChange}
            disabled={!isEditing || loading}
            placeholder="Apartment, suite, etc. (optional)"
          />

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <Label htmlFor="city">City</Label>
              <Input
                id="city"
                name="city"
                value={formData.city}
                onChange={handleInputChange}
                disabled={!isEditing || loading}
                style={{ marginTop: '8px' }}
              />
            </div>
            <div>
              <Label htmlFor="postalCode">Postal code</Label>
              <Input
                id="postalCode"
                name="postalCode"
                value={formData.postalCode}
                onChange={handleInputChange}
                disabled={!isEditing || loading}
                style={{ marginTop: '8px' }}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="country">Country</Label>
            <Select
              id="country"
              name="country"
              value={formData.country}
              onChange={handleInputChange}
              disabled={!isEditing || loading}
              style={{ marginTop: '8px' }}
            >
              <option value="">Select a country</option>
              <option value="GB">United Kingdom</option>
              <option value="ZA">South Africa</option>
              <option value="US">United States</option>
              <option value="OTHER">Other</option>
            </Select>
          </div>

          {/* Timezone */}
          <div>
            <Label htmlFor="timezone">Timezone</Label>
            <p style={{ fontSize: '0.875rem', color: '#475569', marginTop: '4px' }}>
              Used to display dates and times in your local timezone
            </p>
            <Select
              id="timezone"
              name="timezone"
              value={formData.timezone}
              onChange={handleInputChange}
              disabled={!isEditing || loading}
              style={{ marginTop: '8px' }}
              error={validationErrors.timezone}
            >
              <option value="">Select a timezone</option>
              {commonTimezones.map((tz) => (
                <option key={tz.value} value={tz.value}>
                  {tz.label}
                </option>
              ))}
            </Select>
            {validationErrors.timezone && (
              <p style={{ fontSize: '0.875rem', color: '#EF4444', marginTop: '4px' }}>
                {validationErrors.timezone}
              </p>
            )}
          </div>

          {/* Action Buttons */}
          {isEditing && (
            <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
              <Button onClick={handleSave} disabled={loading}>
                {loading ? 'Saving...' : 'Save changes'}
              </Button>
              <Button variant="secondary" onClick={handleCancel} disabled={loading}>
                Cancel
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
