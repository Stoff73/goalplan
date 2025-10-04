import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AlertsList } from '../../../src/components/ai/AlertsList';

// Mock authStorage
jest.mock('../../../src/utils/auth', () => ({
  authStorage: {
    getAccessToken: jest.fn(() => 'mock-token'),
    clear: jest.fn(),
  },
}));

// Mock fetch
global.fetch = jest.fn();

// Mock window.confirm
global.confirm = jest.fn(() => true);

describe('AlertsList', () => {
  const mockAlerts = {
    alerts: [
      {
        id: '1',
        message: 'ISA allowance deadline approaching - 30 days left',
        urgency: 'HIGH',
        read_at: null,
        action_url: '/savings',
        created_at: '2025-03-01T10:00:00Z',
      },
      {
        id: '2',
        message: 'Your pension contribution is below recommended level',
        urgency: 'MEDIUM',
        read_at: '2025-03-02T14:00:00Z',
        action_url: null,
        created_at: '2025-02-28T10:00:00Z',
      },
      {
        id: '3',
        message: 'Consider reviewing your asset allocation',
        urgency: 'LOW',
        read_at: null,
        action_url: '/investments',
        created_at: '2025-02-25T10:00:00Z',
      },
    ],
  };

  beforeEach(() => {
    fetch.mockClear();
    global.confirm.mockClear();
  });

  test('loads and displays alerts on mount', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAlerts,
    });

    render(<AlertsList />);

    await waitFor(() => {
      expect(screen.getByText(/ISA allowance deadline approaching/i)).toBeInTheDocument();
      expect(screen.getByText(/pension contribution is below recommended/i)).toBeInTheDocument();
    });
  });

  test('displays correct unread count', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAlerts,
    });

    render(<AlertsList />);

    await waitFor(() => {
      // 2 unread alerts (id 1 and 3)
      expect(screen.getByText(/You have 2 unread alerts out of 3 total/i)).toBeInTheDocument();
    });
  });

  test('filters by unread only', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAlerts,
    });

    render(<AlertsList />);

    await waitFor(() => {
      expect(screen.getByText(/pension contribution/i)).toBeInTheDocument();
    });

    const unreadCheckbox = screen.getByLabelText('Unread only');
    fireEvent.click(unreadCheckbox);

    // Read alert should be filtered out
    expect(screen.queryByText(/pension contribution/i)).not.toBeInTheDocument();
    // Unread alerts should still be visible
    expect(screen.getByText(/ISA allowance deadline/i)).toBeInTheDocument();
  });

  test('filters by urgency level', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAlerts,
    });

    render(<AlertsList />);

    await waitFor(() => {
      expect(screen.getByText(/ISA allowance deadline/i)).toBeInTheDocument();
    });

    const urgencySelect = screen.getByLabelText('Urgency');
    fireEvent.change(urgencySelect, { target: { value: 'HIGH' } });

    // Only HIGH urgency alert should be visible
    expect(screen.getByText(/ISA allowance deadline/i)).toBeInTheDocument();
    expect(screen.queryByText(/pension contribution/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/asset allocation/i)).not.toBeInTheDocument();
  });

  test('marks alert as read', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAlerts,
    });

    render(<AlertsList />);

    await waitFor(() => {
      expect(screen.getByText(/ISA allowance deadline/i)).toBeInTheDocument();
    });

    // Find the "Mark as Read" button for the first unread alert
    const markReadButtons = screen.getAllByRole('button', { name: /Mark as Read/i });

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

    fireEvent.click(markReadButtons[0]);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/ai/alerts/'),
        expect.objectContaining({
          method: 'POST',
        })
      );
    });
  });

  test('dismisses alert with confirmation', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAlerts,
    });

    render(<AlertsList />);

    await waitFor(() => {
      expect(screen.getByText(/ISA allowance deadline/i)).toBeInTheDocument();
    });

    const dismissButtons = screen.getAllByRole('button', { name: /Dismiss/i });

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

    fireEvent.click(dismissButtons[0]);

    expect(global.confirm).toHaveBeenCalledWith(
      'Are you sure you want to dismiss this alert?'
    );

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/dismiss'),
        expect.objectContaining({
          method: 'POST',
        })
      );
    });
  });

  test('shows empty state when no alerts', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ alerts: [] }),
    });

    render(<AlertsList />);

    await waitFor(() => {
      expect(screen.getByText(/No alerts right now - you're all caught up!/i)).toBeInTheDocument();
    });
  });

  test('handles error loading alerts', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ detail: 'Server error' }),
    });

    render(<AlertsList />);

    await waitFor(() => {
      expect(screen.getByText(/Unable to Load Alerts/i)).toBeInTheDocument();
      expect(screen.getByText(/Server error/i)).toBeInTheDocument();
    });
  });

  test('displays urgency badges with correct styling', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAlerts,
    });

    render(<AlertsList />);

    await waitFor(() => {
      expect(screen.getByText('HIGH')).toBeInTheDocument();
      expect(screen.getByText('MEDIUM')).toBeInTheDocument();
      expect(screen.getByText('LOW')).toBeInTheDocument();
    });
  });
});
