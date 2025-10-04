import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { PersonalizationSettings } from '../../../src/components/personalization/PersonalizationSettings';
import { authStorage } from '../../../src/utils/auth';

// Mock dependencies
jest.mock('../../../src/utils/auth');
jest.mock('../../../src/components/personalization/BehaviorTracker', () => ({
  BehaviorTracker: () => null
}));

// Mock fetch
global.fetch = jest.fn();

describe('PersonalizationSettings', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    authStorage.getAccessToken.mockReturnValue('test-token');
    authStorage.clear = jest.fn();
    delete window.location;
    window.location = { href: '' };
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('renders loading state initially', () => {
    // Mock pending fetch
    fetch.mockImplementation(() => new Promise(() => {}));

    render(<PersonalizationSettings />);

    expect(screen.getByText(/Loading your preferences/i)).toBeInTheDocument();
  });

  test('loads and displays preferences', async () => {
    const mockPreferences = {
      preferences: {
        DEFAULT_CURRENCY: 'GBP',
        THEME: 'light',
        NOTIFICATION_FREQUENCY: 'weekly',
        NUMBER_FORMAT: 'en-GB',
        DATE_FORMAT: 'DD/MM/YYYY'
      }
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPreferences
    });

    render(<PersonalizationSettings />);

    await waitFor(() => {
      expect(screen.getByText(/Personalization settings/i)).toBeInTheDocument();
    });

    // Check that form sections are displayed
    expect(screen.getByText('Currency & Formatting')).toBeInTheDocument();
    expect(screen.getByText('Notifications')).toBeInTheDocument();
    expect(screen.getByText('Appearance')).toBeInTheDocument();

    // Check API was called correctly
    expect(fetch).toHaveBeenCalledWith(
      '/api/v1/personalization/preferences',
      expect.objectContaining({
        headers: {
          Authorization: 'Bearer test-token'
        }
      })
    );
  });

  test('updates preference and shows success message', async () => {
    const mockPreferences = {
      preferences: {
        DEFAULT_CURRENCY: 'GBP',
        THEME: 'light',
        NOTIFICATION_FREQUENCY: 'weekly',
        NUMBER_FORMAT: 'en-GB',
        DATE_FORMAT: 'DD/MM/YYYY'
      }
    };

    // Mock load preferences
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPreferences
    });

    render(<PersonalizationSettings />);

    await waitFor(() => {
      expect(screen.getByText(/Personalization settings/i)).toBeInTheDocument();
    });

    // Change currency
    const currencySelect = screen.getByLabelText(/Default Currency/i);
    fireEvent.change(currencySelect, { target: { value: 'USD' } });

    // Mock save preferences (5 calls - one for each preference)
    fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ id: '123', preference_type: 'DEFAULT_CURRENCY', preference_value: 'USD' })
    });

    // Click save
    const saveButton = screen.getByText(/Save All Preferences/i);
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText(/Preferences saved!/i)).toBeInTheDocument();
    });

    // Check that save was called for all preferences
    expect(fetch).toHaveBeenCalledWith(
      '/api/v1/personalization/preferences',
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token'
        },
        body: expect.stringContaining('DEFAULT_CURRENCY')
      })
    );
  });

  test('handles save error', async () => {
    const mockPreferences = {
      preferences: {
        DEFAULT_CURRENCY: 'GBP',
        THEME: 'light',
        NOTIFICATION_FREQUENCY: 'weekly',
        NUMBER_FORMAT: 'en-GB',
        DATE_FORMAT: 'DD/MM/YYYY'
      }
    };

    // Mock load preferences
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPreferences
    });

    render(<PersonalizationSettings />);

    await waitFor(() => {
      expect(screen.getByText(/Personalization settings/i)).toBeInTheDocument();
    });

    // Mock failed save
    fetch.mockResolvedValue({
      ok: false,
      status: 500
    });

    // Click save
    const saveButton = screen.getByText(/Save All Preferences/i);
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText(/Failed to save some preferences/i)).toBeInTheDocument();
    });
  });

  test('redirects on 401 unauthorized', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 401
    });

    render(<PersonalizationSettings />);

    await waitFor(() => {
      expect(authStorage.clear).toHaveBeenCalled();
      expect(window.location.href).toBe('/login');
    });
  });

  test('allows changing all preference fields', async () => {
    const mockPreferences = {
      preferences: {
        DEFAULT_CURRENCY: 'GBP',
        THEME: 'light',
        NOTIFICATION_FREQUENCY: 'weekly',
        NUMBER_FORMAT: 'en-GB',
        DATE_FORMAT: 'DD/MM/YYYY'
      }
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPreferences
    });

    render(<PersonalizationSettings />);

    await waitFor(() => {
      expect(screen.getByLabelText(/Default Currency/i)).toBeInTheDocument();
    });

    // Test changing each field
    const currencySelect = screen.getByLabelText(/Default Currency/i);
    const themeSelect = screen.getByLabelText(/Theme/i);
    const notificationSelect = screen.getByLabelText(/Notification Frequency/i);
    const numberFormatSelect = screen.getByLabelText(/Number Format/i);
    const dateFormatSelect = screen.getByLabelText(/Date Format/i);

    expect(currencySelect).toBeInTheDocument();
    expect(themeSelect).toBeInTheDocument();
    expect(notificationSelect).toBeInTheDocument();
    expect(numberFormatSelect).toBeInTheDocument();
    expect(dateFormatSelect).toBeInTheDocument();

    // Change values
    fireEvent.change(currencySelect, { target: { value: 'USD' } });
    fireEvent.change(themeSelect, { target: { value: 'dark' } });
    fireEvent.change(notificationSelect, { target: { value: 'daily' } });

    expect(currencySelect.value).toBe('USD');
    expect(themeSelect.value).toBe('dark');
    expect(notificationSelect.value).toBe('daily');
  });

  test('cancel button navigates to personalized dashboard', async () => {
    const mockPreferences = {
      preferences: {
        DEFAULT_CURRENCY: 'GBP',
        THEME: 'light',
        NOTIFICATION_FREQUENCY: 'weekly',
        NUMBER_FORMAT: 'en-GB',
        DATE_FORMAT: 'DD/MM/YYYY'
      }
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPreferences
    });

    render(<PersonalizationSettings />);

    await waitFor(() => {
      expect(screen.getByText(/Cancel/i)).toBeInTheDocument();
    });

    const cancelButton = screen.getByText(/Cancel/i);
    fireEvent.click(cancelButton);

    expect(window.location.href).toBe('/personalized-dashboard');
  });
});
