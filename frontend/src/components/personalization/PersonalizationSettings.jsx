import React, { useState, useEffect } from 'react';
import { Card, Select, Button, Alert, Label } from 'internal-packages/ui';
import { Layout } from '../Layout';
import { authStorage } from '../../utils/auth';
import { BehaviorTracker } from './BehaviorTracker';

/**
 * PersonalizationSettings - User preference configuration
 *
 * Follows STYLEGUIDE.md narrative storytelling approach:
 * - Conversational intro: "Customize GoalPlan to work the way you do"
 * - Settings grouped by category
 * - Each setting explained in plain language
 * - Save confirmation with friendly message
 * - Line height 1.7, generous spacing
 *
 * Settings:
 * - Default currency (GBP, ZAR, USD, EUR)
 * - Date format (DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD)
 * - Number format (1,234.56 vs 1.234,56)
 * - Notification preferences (email, in-app, frequency)
 * - Theme (light/dark mode)
 */
export function PersonalizationSettings() {
  const [preferences, setPreferences] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Form state
  const [currency, setCurrency] = useState('GBP');
  const [theme, setTheme] = useState('light');
  const [notificationFrequency, setNotificationFrequency] = useState('weekly');
  const [numberFormat, setNumberFormat] = useState('en-GB');
  const [dateFormat, setDateFormat] = useState('DD/MM/YYYY');

  useEffect(() => {
    loadPreferences();
  }, []);

  async function loadPreferences() {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/personalization/preferences', {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }
        // Silently ignore 404 - endpoint not implemented yet
        if (response.status === 404) {
          return;
        }
        throw new Error('Failed to load preferences');
      }

      const data = await response.json();
      setPreferences(data.preferences);

      // Set form values from loaded preferences
      setCurrency(data.preferences.DEFAULT_CURRENCY || 'GBP');
      setTheme(data.preferences.THEME || 'light');
      setNotificationFrequency(data.preferences.NOTIFICATION_FREQUENCY || 'weekly');
      setNumberFormat(data.preferences.NUMBER_FORMAT || 'en-GB');
      setDateFormat(data.preferences.DATE_FORMAT || 'DD/MM/YYYY');
    } catch (err) {
      setError('Unable to load your preferences. Please try again.');
      console.error('Error loading preferences:', err);
    } finally {
      setLoading(false);
    }
  }

  async function savePreference(preferenceType, preferenceValue) {
    try {
      const response = await fetch('/api/v1/personalization/preferences', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({
          preference_type: preferenceType,
          preference_value: preferenceValue,
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }
        throw new Error('Failed to save preference');
      }

      return true;
    } catch (err) {
      console.error('Error saving preference:', err);
      throw err;
    }
  }

  async function handleSaveAll() {
    setSaving(true);
    setError(null);
    setSaveSuccess(false);

    try {
      // Save all preferences
      await Promise.all([
        savePreference('DEFAULT_CURRENCY', currency),
        savePreference('THEME', theme),
        savePreference('NOTIFICATION_FREQUENCY', notificationFrequency),
        savePreference('NUMBER_FORMAT', numberFormat),
        savePreference('DATE_FORMAT', dateFormat),
      ]);

      setSaveSuccess(true);

      // Hide success message after 3 seconds
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setError('Failed to save some preferences. Please try again.');
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <Layout>
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '32px' }}>
          <Card style={{ padding: '32px', textAlign: 'center' }}>
            <p style={{ color: '#94A3B8' }}>Loading your preferences...</p>
          </Card>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '32px' }}>
        {/* Track page view */}
        <BehaviorTracker page="personalization_settings" />

      {/* Narrative Introduction */}
      <Card style={{ padding: '32px', marginBottom: '48px', lineHeight: '1.7' }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: '16px', color: '#0F172A' }}>
          Personalization settings
        </h2>
        <p style={{ color: '#475569', marginBottom: '0' }}>
          Customize GoalPlan to work the way you do. These settings control how we display information,
          when we send notifications, and how the app looks and feels.
        </p>
      </Card>

      {/* Success Message */}
      {saveSuccess && (
        <Alert variant="success" style={{ marginBottom: '24px' }}>
          <strong>✓ Preferences saved!</strong> Your changes have been applied and will take effect immediately.
        </Alert>
      )}

      {/* Error Message */}
      {error && (
        <Alert variant="error" style={{ marginBottom: '24px' }}>
          {error}
        </Alert>
      )}

      {/* Currency & Formatting Section */}
      <Card style={{ padding: '32px', marginBottom: '24px', lineHeight: '1.7' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
          Currency & Formatting
        </h3>
        <p style={{ color: '#475569', marginBottom: '24px', fontSize: '0.95rem' }}>
          Your default currency is <strong style={{ fontFamily: 'monospace' }}>{currency}</strong>.
          This is used throughout the app when we show amounts. You can still track accounts in other currencies.
        </p>

        <div style={{ marginBottom: '24px' }}>
          <Label htmlFor="currency">Default Currency</Label>
          <Select
            id="currency"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            options={[
              { value: 'GBP', label: '£ British Pound (GBP)' },
              { value: 'ZAR', label: 'R South African Rand (ZAR)' },
              { value: 'USD', label: '$ US Dollar (USD)' },
              { value: 'EUR', label: '€ Euro (EUR)' },
            ]}
          />
          <p style={{ fontSize: '0.875rem', color: '#64748B', marginTop: '4px' }}>
            Used for summaries and default displays
          </p>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <Label htmlFor="numberFormat">Number Format</Label>
          <Select
            id="numberFormat"
            value={numberFormat}
            onChange={(e) => setNumberFormat(e.target.value)}
            options={[
              { value: 'en-GB', label: '1,234.56 (UK/US style)' },
              { value: 'de-DE', label: '1.234,56 (European style)' },
            ]}
          />
          <p style={{ fontSize: '0.875rem', color: '#64748B', marginTop: '4px' }}>
            How we display large numbers and decimals
          </p>
        </div>

        <div>
          <Label htmlFor="dateFormat">Date Format</Label>
          <Select
            id="dateFormat"
            value={dateFormat}
            onChange={(e) => setDateFormat(e.target.value)}
            options={[
              { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY (e.g., 31/12/2025)' },
              { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY (e.g., 12/31/2025)' },
              { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD (e.g., 2025-12-31)' },
            ]}
          />
          <p style={{ fontSize: '0.875rem', color: '#64748B', marginTop: '4px' }}>
            How we display dates throughout the app
          </p>
        </div>
      </Card>

      {/* Notifications Section */}
      <Card style={{ padding: '32px', marginBottom: '24px', lineHeight: '1.7' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
          Notifications
        </h3>
        <p style={{ color: '#475569', marginBottom: '24px', fontSize: '0.95rem' }}>
          We'll send you updates about your financial goals, important deadlines, and personalized recommendations.
          You're currently receiving notifications <strong>{notificationFrequency}</strong>.
        </p>

        <div>
          <Label htmlFor="notificationFrequency">Notification Frequency</Label>
          <Select
            id="notificationFrequency"
            value={notificationFrequency}
            onChange={(e) => setNotificationFrequency(e.target.value)}
            options={[
              { value: 'real_time', label: 'Real-time (as they happen)' },
              { value: 'daily', label: 'Daily digest' },
              { value: 'weekly', label: 'Weekly summary (recommended)' },
              { value: 'monthly', label: 'Monthly recap only' },
            ]}
          />
          <p style={{ fontSize: '0.875rem', color: '#64748B', marginTop: '4px' }}>
            How often we send email notifications
          </p>
        </div>
      </Card>

      {/* Appearance Section */}
      <Card style={{ padding: '32px', marginBottom: '24px', lineHeight: '1.7' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
          Appearance
        </h3>
        <p style={{ color: '#475569', marginBottom: '24px', fontSize: '0.95rem' }}>
          Choose between light and dark mode. This affects the entire app.
        </p>

        <div>
          <Label htmlFor="theme">Theme</Label>
          <Select
            id="theme"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            options={[
              { value: 'light', label: '☀️ Light mode' },
              { value: 'dark', label: '🌙 Dark mode' },
              { value: 'auto', label: '🔄 Auto (match system)' },
            ]}
          />
          <p style={{ fontSize: '0.875rem', color: '#64748B', marginTop: '4px' }}>
            Your theme preference
          </p>
        </div>
      </Card>

      {/* Save Button */}
      <div style={{ display: 'flex', gap: '16px', justifyContent: 'flex-end' }}>
        <Button
          variant="secondary"
          onClick={() => window.location.href = '/personalized-dashboard'}
        >
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={handleSaveAll}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save All Preferences'}
        </Button>
      </div>

      {/* Help Text */}
      <Card style={{
        padding: '24px',
        marginTop: '48px',
        backgroundColor: '#F8FAFC',
        border: '1px solid #E2E8F0'
      }}>
        <h4 style={{ fontSize: '1rem', fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>
          💡 About personalization
        </h4>
        <p style={{ color: '#475569', marginBottom: '0', lineHeight: '1.7', fontSize: '0.95rem' }}>
          Beyond these settings, GoalPlan automatically personalizes your dashboard and recommendations based
          on how you use the app. The more you use it, the better it gets at understanding what matters to you.
        </p>
      </Card>
      </div>
    </Layout>
  );
}
