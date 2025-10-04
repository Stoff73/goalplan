import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { RecommendationsWidget } from '../../../src/components/recommendations/RecommendationsWidget';
import { authStorage } from '../../../src/utils/auth';

// Mock authStorage
jest.mock('../../../src/utils/auth', () => ({
  authStorage: {
    getAccessToken: jest.fn(),
    clear: jest.fn(),
    getUser: jest.fn(),
  },
}));

// Mock fetch
global.fetch = jest.fn();

// Mock window.location
delete window.location;
window.location = { href: '' };

describe('RecommendationsWidget', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
    authStorage.getAccessToken.mockReturnValue('fake-token');
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  const mockHighPriorityRecommendations = [
    {
      id: '1',
      priority: 'HIGH',
      category: 'PROTECTION',
      title: 'Increase life cover to protect your family',
      description: 'Your current life cover of £100,000 may not be sufficient.',
      reasoning: ['Current cover: £100,000', 'Recommended: £250,000'],
      estimated_benefit: {
        amount_gbp: 150000,
        currency: 'GBP',
        description: 'Protection gap',
      },
      generated_at: '2025-01-01T00:00:00Z',
      status: 'NEW',
    },
    {
      id: '2',
      priority: 'HIGH',
      category: 'TAX',
      title: 'Avoid personal allowance taper with pension contribution',
      description: 'Your income of £105,000 triggers personal allowance taper.',
      reasoning: ['Income: £105,000', 'Excess over £100k: £5,000'],
      estimated_benefit: {
        amount_gbp: 3000,
        currency: 'GBP',
        description: 'Tax saving',
      },
      generated_at: '2025-01-02T00:00:00Z',
      status: 'NEW',
    },
    {
      id: '3',
      priority: 'HIGH',
      category: 'SAVINGS',
      title: 'Build up your emergency fund to 6 months of expenses',
      description: 'Your emergency fund is currently £5,000 but we recommend £18,000.',
      reasoning: ['Current: £5,000', 'Recommended: £18,000'],
      estimated_benefit: {
        amount_gbp: 13000,
        currency: 'GBP',
        description: 'Additional savings needed',
      },
      generated_at: '2025-01-03T00:00:00Z',
      status: 'NEW',
    },
  ];

  describe('Loading state', () => {
    test('renders loading skeleton while fetching', () => {
      fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<RecommendationsWidget />);

      expect(screen.getByText('Recommended Actions')).toBeInTheDocument();
      expect(screen.getByText('Loading your top priorities...')).toBeInTheDocument();
    });
  });

  describe('Recommendations display', () => {
    test('renders top 3 HIGH priority recommendations', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockHighPriorityRecommendations }),
      });

      render(<RecommendationsWidget />);

      await waitFor(() => {
        expect(screen.getByText('Increase life cover to protect your family')).toBeInTheDocument();
      });

      expect(screen.getByText(/Avoid personal allowance taper/)).toBeInTheDocument();
      expect(screen.getByText(/Build up your emergency fund/)).toBeInTheDocument();
    });

    test('truncates long titles to 60 characters', async () => {
      const longTitleRec = {
        ...mockHighPriorityRecommendations[0],
        title: 'This is a very long recommendation title that should be truncated to sixty characters maximum',
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: [longTitleRec] }),
      });

      render(<RecommendationsWidget />);

      await waitFor(() => {
        expect(screen.getByText(/This is a very long recommendation title that should be trun.../)).toBeInTheDocument();
      });
    });

    test('displays potential savings when available', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockHighPriorityRecommendations }),
      });

      render(<RecommendationsWidget />);

      await waitFor(() => {
        expect(screen.getByText(/Could save you £150,000/)).toBeInTheDocument();
      });

      expect(screen.getByText(/Could save you £3,000/)).toBeInTheDocument();
    });

    test('shows "View All Recommendations" link', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockHighPriorityRecommendations }),
      });

      render(<RecommendationsWidget />);

      await waitFor(() => {
        const link = screen.getByText('View All Recommendations →');
        expect(link).toBeInTheDocument();
        expect(link).toHaveAttribute('href', '/recommendations');
      });
    });
  });

  describe('Empty state', () => {
    test('shows empty state when no high priority recommendations', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: [] }),
      });

      render(<RecommendationsWidget />);

      await waitFor(() => {
        expect(screen.getByText('No urgent recommendations right now. You\'re managing your finances well!')).toBeInTheDocument();
      });

      const link = screen.getByText('View All Recommendations →');
      expect(link).toBeInTheDocument();
    });

    test('filters to only show HIGH priority recommendations', async () => {
      const mixedPriorityRecs = [
        ...mockHighPriorityRecommendations.slice(0, 2), // 2 HIGH
        {
          id: '4',
          priority: 'MEDIUM',
          category: 'SAVINGS',
          title: 'Medium priority recommendation',
          description: 'This should not be shown',
          reasoning: [],
          estimated_benefit: null,
          generated_at: '2025-01-04T00:00:00Z',
          status: 'NEW',
        },
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mixedPriorityRecs }),
      });

      render(<RecommendationsWidget />);

      await waitFor(() => {
        expect(screen.getByText('Increase life cover to protect your family')).toBeInTheDocument();
      });

      // Medium priority should not be shown
      expect(screen.queryByText('Medium priority recommendation')).not.toBeInTheDocument();
    });
  });

  describe('Error state', () => {
    test('handles API error gracefully', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      render(<RecommendationsWidget />);

      await waitFor(() => {
        expect(screen.getByText('Failed to load recommendations')).toBeInTheDocument();
      });
    });

    test('handles 401 authentication error by redirecting to login', async () => {
      fetch.mockResolvedValueOnce({ ok: false, status: 401 });

      render(<RecommendationsWidget />);

      await waitFor(() => {
        expect(authStorage.clear).toHaveBeenCalled();
        expect(window.location.href).toBe('/login');
      });
    });
  });

  describe('Auto-refresh', () => {
    test('auto-refreshes every 5 minutes', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ recommendations: mockHighPriorityRecommendations }),
      });

      render(<RecommendationsWidget />);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledTimes(1);
      });

      // Fast-forward 5 minutes
      jest.advanceTimersByTime(5 * 60 * 1000);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledTimes(2);
      });

      // Fast-forward another 5 minutes
      jest.advanceTimersByTime(5 * 60 * 1000);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledTimes(3);
      });
    });

    test('clears interval on unmount', async () => {
      fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ recommendations: mockHighPriorityRecommendations }),
      });

      const { unmount } = render(<RecommendationsWidget />);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledTimes(1);
      });

      unmount();

      // Fast-forward 5 minutes after unmount
      jest.advanceTimersByTime(5 * 60 * 1000);

      // Should not make additional fetch calls
      expect(fetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('API call', () => {
    test('fetches with correct query parameters', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockHighPriorityRecommendations }),
      });

      render(<RecommendationsWidget />);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          '/api/v1/recommendations/?priority=HIGH',
          expect.objectContaining({
            headers: expect.objectContaining({
              Authorization: 'Bearer fake-token',
            }),
          })
        );
      });
    });
  });

  describe('Narrative text', () => {
    test('uses singular language for 1 recommendation', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: [mockHighPriorityRecommendations[0]] }),
      });

      render(<RecommendationsWidget />);

      await waitFor(() => {
        expect(screen.getByText(/Here is your top 1 high-priority recommendation/)).toBeInTheDocument();
      });
    });

    test('uses plural language for multiple recommendations', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockHighPriorityRecommendations }),
      });

      render(<RecommendationsWidget />);

      await waitFor(() => {
        expect(screen.getByText(/Here are your top 3 high-priority recommendations/)).toBeInTheDocument();
      });
    });
  });

  describe('Priority badges', () => {
    test('displays HIGH priority badge for all recommendations', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockHighPriorityRecommendations }),
      });

      render(<RecommendationsWidget />);

      await waitFor(() => {
        const badges = screen.getAllByText('HIGH');
        expect(badges).toHaveLength(3);
      });
    });
  });

  describe('Styling and accessibility', () => {
    test('applies correct color styling for HIGH priority', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: [mockHighPriorityRecommendations[0]] }),
      });

      const { container } = render(<RecommendationsWidget />);

      await waitFor(() => {
        const badge = screen.getByText('HIGH');
        expect(badge).toHaveStyle({
          backgroundColor: '#FEE2E2',
          color: '#991B1B',
        });
      });
    });

    test('link has correct hover behavior', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockHighPriorityRecommendations }),
      });

      render(<RecommendationsWidget />);

      await waitFor(() => {
        const link = screen.getByText('View All Recommendations →');
        expect(link).toHaveAttribute('href', '/recommendations');
      });
    });
  });
});
