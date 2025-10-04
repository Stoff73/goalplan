import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { InsightsFeed } from '../../../src/components/personalization/InsightsFeed';
import { authStorage } from '../../../src/utils/auth';

// Mock dependencies
jest.mock('../../../src/utils/auth');

// Mock fetch
global.fetch = jest.fn();

describe('InsightsFeed', () => {
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

    render(<InsightsFeed limit={5} />);

    expect(screen.getByText(/Loading insights/i)).toBeInTheDocument();
  });

  test('loads and displays insights', async () => {
    const mockInsights = [
      {
        id: '1',
        user_id: 'user-123',
        insight_type: 'GOAL_ADVICE',
        insight_text: 'You\'re 50% to your house deposit - consider increasing savings',
        relevance_score: '85.50',
        clicked: false,
        dismissed: false,
        created_at: '2025-10-04T10:00:00Z',
        updated_at: '2025-10-04T10:00:00Z'
      },
      {
        id: '2',
        user_id: 'user-123',
        insight_type: 'SAVINGS_TIP',
        insight_text: 'Consider automatic savings transfers to reach goals faster',
        relevance_score: '70.00',
        clicked: false,
        dismissed: false,
        created_at: '2025-10-04T10:00:00Z',
        updated_at: '2025-10-04T10:00:00Z'
      }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockInsights
    });

    render(<InsightsFeed limit={5} />);

    await waitFor(() => {
      expect(screen.getByText(/You're 50% to your house deposit/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Consider automatic savings transfers/i)).toBeInTheDocument();

    // Check API was called correctly
    expect(fetch).toHaveBeenCalledWith(
      '/api/v1/personalization/insights?limit=5',
      expect.objectContaining({
        headers: {
          Authorization: 'Bearer test-token'
        }
      })
    );
  });

  test('shows empty state when no insights', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => []
    });

    render(<InsightsFeed limit={5} />);

    await waitFor(() => {
      expect(screen.getByText(/No insights yet/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/We're still learning about your financial patterns/i)).toBeInTheDocument();
  });

  test('dismisses insight and removes from UI', async () => {
    const mockInsights = [
      {
        id: '1',
        user_id: 'user-123',
        insight_type: 'GOAL_ADVICE',
        insight_text: 'Test insight 1',
        relevance_score: '85.50',
        clicked: false,
        dismissed: false,
        created_at: '2025-10-04T10:00:00Z',
        updated_at: '2025-10-04T10:00:00Z'
      },
      {
        id: '2',
        user_id: 'user-123',
        insight_type: 'SAVINGS_TIP',
        insight_text: 'Test insight 2',
        relevance_score: '70.00',
        clicked: false,
        dismissed: false,
        created_at: '2025-10-04T10:00:00Z',
        updated_at: '2025-10-04T10:00:00Z'
      }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockInsights
    });

    render(<InsightsFeed limit={5} />);

    await waitFor(() => {
      expect(screen.getByText('Test insight 1')).toBeInTheDocument();
    });

    // Mock behavior tracking
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'tracked' })
    });

    // Find and click dismiss button for first insight
    const dismissButtons = screen.getAllByText('Dismiss');
    fireEvent.click(dismissButtons[0]);

    // First insight should be removed
    await waitFor(() => {
      expect(screen.queryByText('Test insight 1')).not.toBeInTheDocument();
    });

    // Second insight should still be visible
    expect(screen.getByText('Test insight 2')).toBeInTheDocument();

    // Check that behavior tracking was called
    expect(fetch).toHaveBeenCalledWith(
      '/api/v1/personalization/behavior/track',
      expect.objectContaining({
        method: 'POST',
        body: expect.stringContaining('dismissed')
      })
    );
  });

  test('tracks insight click', async () => {
    const mockInsights = [
      {
        id: '1',
        user_id: 'user-123',
        insight_type: 'GOAL_ADVICE',
        insight_text: 'Test insight',
        relevance_score: '85.50',
        clicked: false,
        dismissed: false,
        created_at: '2025-10-04T10:00:00Z',
        updated_at: '2025-10-04T10:00:00Z'
      }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockInsights
    });

    render(<InsightsFeed limit={5} />);

    await waitFor(() => {
      expect(screen.getByText('Test insight')).toBeInTheDocument();
    });

    // Mock behavior tracking
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'tracked' })
    });

    // Click insight card
    const insightCard = screen.getByText('Test insight').closest('div[style*="cursor: pointer"]');
    fireEvent.click(insightCard);

    // Check that behavior tracking was called
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        '/api/v1/personalization/behavior/track',
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('clicked')
        })
      );
    });
  });

  test('displays insight type badges correctly', async () => {
    const mockInsights = [
      {
        id: '1',
        user_id: 'user-123',
        insight_type: 'GOAL_ADVICE',
        insight_text: 'Goal advice',
        relevance_score: '85.50',
        clicked: false,
        dismissed: false,
        created_at: '2025-10-04T10:00:00Z',
        updated_at: '2025-10-04T10:00:00Z'
      },
      {
        id: '2',
        user_id: 'user-123',
        insight_type: 'TAX_TIP',
        insight_text: 'Tax tip',
        relevance_score: '80.00',
        clicked: false,
        dismissed: false,
        created_at: '2025-10-04T10:00:00Z',
        updated_at: '2025-10-04T10:00:00Z'
      }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockInsights
    });

    render(<InsightsFeed limit={5} />);

    await waitFor(() => {
      expect(screen.getByText('Goal Advice')).toBeInTheDocument();
    });

    expect(screen.getByText('Tax Tip')).toBeInTheDocument();
  });

  test('displays relevance scores', async () => {
    const mockInsights = [
      {
        id: '1',
        user_id: 'user-123',
        insight_type: 'GOAL_ADVICE',
        insight_text: 'High relevance insight',
        relevance_score: '85.50',
        clicked: false,
        dismissed: false,
        created_at: '2025-10-04T10:00:00Z',
        updated_at: '2025-10-04T10:00:00Z'
      }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockInsights
    });

    render(<InsightsFeed limit={5} />);

    await waitFor(() => {
      expect(screen.getByText(/86% relevant/i)).toBeInTheDocument();
    });
  });

  test('refresh button reloads insights', async () => {
    const mockInsights = [
      {
        id: '1',
        user_id: 'user-123',
        insight_type: 'GOAL_ADVICE',
        insight_text: 'Test insight',
        relevance_score: '85.50',
        clicked: false,
        dismissed: false,
        created_at: '2025-10-04T10:00:00Z',
        updated_at: '2025-10-04T10:00:00Z'
      }
    ];

    fetch.mockResolvedValue({
      ok: true,
      json: async () => mockInsights
    });

    render(<InsightsFeed limit={5} />);

    await waitFor(() => {
      expect(screen.getByText('Test insight')).toBeInTheDocument();
    });

    // Click refresh button
    const refreshButton = screen.getByText(/Refresh Insights/i);
    fireEvent.click(refreshButton);

    // Should call API again
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(2);
    });
  });

  test('handles API error', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500
    });

    render(<InsightsFeed limit={5} />);

    await waitFor(() => {
      expect(screen.getByText(/Unable to load personalized insights/i)).toBeInTheDocument();
    });
  });

  test('redirects on 401 unauthorized', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 401
    });

    render(<InsightsFeed limit={5} />);

    await waitFor(() => {
      expect(authStorage.clear).toHaveBeenCalled();
      expect(window.location.href).toBe('/login');
    });
  });
});
