import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { PersonalizedDashboard } from '../../../src/components/personalization/PersonalizedDashboard';
import { authStorage } from '../../../src/utils/auth';

// Mock dependencies
jest.mock('../../../src/utils/auth');
jest.mock('../../../src/components/personalization/InsightsFeed', () => ({
  InsightsFeed: () => <div data-testid="insights-feed">Insights Feed</div>
}));
jest.mock('../../../src/components/personalization/BehaviorTracker', () => ({
  BehaviorTracker: () => null
}));

// Mock fetch
global.fetch = jest.fn();

describe('PersonalizedDashboard', () => {
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

    render(<PersonalizedDashboard />);

    expect(screen.getByText(/Loading your personalized dashboard/i)).toBeInTheDocument();
  });

  test('fetches and displays personalized dashboard', async () => {
    const mockDashboard = {
      widget_order: ['net_worth', 'goals', 'savings'],
      visible_widgets: ['net_worth', 'goals', 'savings'],
      hidden_widgets: []
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDashboard
    });

    render(<PersonalizedDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Your personalized dashboard/i)).toBeInTheDocument();
    });

    // Check that widgets are displayed
    expect(screen.getByText('Net Worth Overview')).toBeInTheDocument();
    expect(screen.getByText('Financial Goals')).toBeInTheDocument();
    expect(screen.getByText('Savings & Cash')).toBeInTheDocument();

    // Check API was called correctly
    expect(fetch).toHaveBeenCalledWith(
      '/api/v1/personalization/dashboard/personalized',
      expect.objectContaining({
        headers: {
          Authorization: 'Bearer test-token'
        }
      })
    );
  });

  test('displays widgets in personalized order with most used badge', async () => {
    const mockDashboard = {
      widget_order: ['goals', 'net_worth', 'savings'],
      visible_widgets: ['goals', 'net_worth', 'savings'],
      hidden_widgets: []
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDashboard
    });

    render(<PersonalizedDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Financial Goals')).toBeInTheDocument();
    });

    // Check that most used badge appears
    expect(screen.getByText('Most Used')).toBeInTheDocument();

    // Check narrative mentions most used widget
    expect(screen.getByText(/Financial Goals/i)).toBeInTheDocument();
  });

  test('shows insights feed component', async () => {
    const mockDashboard = {
      widget_order: ['net_worth'],
      visible_widgets: ['net_worth'],
      hidden_widgets: []
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDashboard
    });

    render(<PersonalizedDashboard />);

    await waitFor(() => {
      expect(screen.getByTestId('insights-feed')).toBeInTheDocument();
    });
  });

  test('shows hidden widgets with progressive disclosure', async () => {
    const mockDashboard = {
      widget_order: ['net_worth', 'goals', 'retirement', 'protection'],
      visible_widgets: ['net_worth', 'goals'],
      hidden_widgets: ['retirement', 'protection']
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDashboard
    });

    render(<PersonalizedDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Show 2 less-used section/i)).toBeInTheDocument();
    });

    // Hidden widgets should not be visible initially
    expect(screen.queryByText('Retirement Planning')).not.toBeInTheDocument();
    expect(screen.queryByText('Life Protection')).not.toBeInTheDocument();

    // Click to expand
    const showButton = screen.getByText(/Show 2 less-used section/i);
    fireEvent.click(showButton);

    // Hidden widgets should now be visible
    expect(screen.getByText('Retirement Planning')).toBeInTheDocument();
    expect(screen.getByText('Life Protection')).toBeInTheDocument();
  });

  test('handles API error', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500
    });

    render(<PersonalizedDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Unable to load your personalized dashboard/i)).toBeInTheDocument();
    });

    // Should show try again button
    expect(screen.getByText(/Try Again/i)).toBeInTheDocument();
  });

  test('redirects on 401 unauthorized', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 401
    });

    render(<PersonalizedDashboard />);

    await waitFor(() => {
      expect(authStorage.clear).toHaveBeenCalled();
      expect(window.location.href).toBe('/login');
    });
  });

  test('navigates to personalization settings', async () => {
    const mockDashboard = {
      widget_order: ['net_worth'],
      visible_widgets: ['net_worth'],
      hidden_widgets: []
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDashboard
    });

    render(<PersonalizedDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Open Personalization Settings/i)).toBeInTheDocument();
    });

    const settingsButton = screen.getByText(/Open Personalization Settings/i);
    fireEvent.click(settingsButton);

    expect(window.location.href).toBe('/settings/personalization');
  });
});
