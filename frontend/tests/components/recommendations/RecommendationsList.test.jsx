import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { RecommendationsList } from '../../../src/components/recommendations/RecommendationsList';
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

// Mock window.confirm
global.confirm = jest.fn(() => true);

// Mock window.location
delete window.location;
window.location = { href: '' };

describe('RecommendationsList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    authStorage.getAccessToken.mockReturnValue('fake-token');
    global.confirm.mockReturnValue(true);
  });

  const mockRecommendations = [
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
      priority: 'MEDIUM',
      category: 'SAVINGS',
      title: 'Use your remaining ISA allowance',
      description: 'You have £5,000 of unused ISA allowance.',
      reasoning: ['ISA allowance: £20,000', 'Used: £15,000'],
      estimated_benefit: {
        amount_gbp: 1200,
        currency: 'GBP',
        description: 'Annual tax saving',
      },
      generated_at: '2025-01-02T00:00:00Z',
      status: 'NEW',
    },
    {
      id: '3',
      priority: 'LOW',
      category: 'TAX',
      title: 'Consider dividend tax planning',
      description: 'You could optimize your dividend tax strategy.',
      reasoning: ['Dividend income: £2,000', 'Dividend allowance: £500'],
      estimated_benefit: null,
      generated_at: '2025-01-03T00:00:00Z',
      status: 'NEW',
    },
  ];

  describe('Loading state', () => {
    test('renders loading skeleton while fetching', () => {
      fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<RecommendationsList />);

      expect(screen.getByText('Your Recommended Actions')).toBeInTheDocument();
      expect(screen.getByText('Loading your personalized recommendations...')).toBeInTheDocument();
    });
  });

  describe('Recommendations display', () => {
    test('renders list of recommendations correctly', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockRecommendations }),
      });

      render(<RecommendationsList />);

      await waitFor(() => {
        expect(screen.getByText('Increase life cover to protect your family')).toBeInTheDocument();
      });

      expect(screen.getByText('Use your remaining ISA allowance')).toBeInTheDocument();
      expect(screen.getByText('Consider dividend tax planning')).toBeInTheDocument();
    });

    test('displays priority badges with correct colors', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockRecommendations }),
      });

      render(<RecommendationsList />);

      await waitFor(() => {
        const highBadges = screen.getAllByText('HIGH');
        expect(highBadges.length).toBeGreaterThan(0);
      });

      expect(screen.getByText('MEDIUM')).toBeInTheDocument();
      expect(screen.getByText('LOW')).toBeInTheDocument();
    });

    test('shows potential savings when available', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockRecommendations }),
      });

      render(<RecommendationsList />);

      await waitFor(() => {
        expect(screen.getByText(/£150,000/)).toBeInTheDocument();
      });

      expect(screen.getByText(/£1,200/)).toBeInTheDocument();
    });

    test('sorts recommendations by priority then date', async () => {
      const unsortedRecommendations = [
        { ...mockRecommendations[1], generated_at: '2025-01-05T00:00:00Z' },
        { ...mockRecommendations[0], generated_at: '2025-01-04T00:00:00Z' },
        { ...mockRecommendations[2], generated_at: '2025-01-06T00:00:00Z' },
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: unsortedRecommendations }),
      });

      render(<RecommendationsList />);

      // Wait for HIGH priority recommendation to appear first
      await waitFor(() => {
        expect(screen.getByText('Increase life cover to protect your family')).toBeInTheDocument();
      });

      // Verify it's sorted correctly (HIGH priority first)
      const allTitles = screen.queryAllByRole('heading', { level: 3 });
      expect(allTitles[0]).toHaveTextContent('Increase life cover to protect your family');
    });
  });

  describe('Filtering', () => {
    test('filters by priority correctly', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockRecommendations }),
      });

      render(<RecommendationsList />);

      await waitFor(() => {
        expect(screen.getByText('Increase life cover to protect your family')).toBeInTheDocument();
      });

      // Filter to only HIGH priority
      const priorityFilter = screen.getByLabelText('Filter by Priority');
      fireEvent.change(priorityFilter, { target: { value: 'HIGH' } });

      await waitFor(() => {
        expect(screen.getByText('Increase life cover to protect your family')).toBeInTheDocument();
        expect(screen.queryByText('Use your remaining ISA allowance')).not.toBeInTheDocument();
        expect(screen.queryByText('Consider dividend tax planning')).not.toBeInTheDocument();
      });
    });

    test('filters by type correctly', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockRecommendations }),
      });

      render(<RecommendationsList />);

      await waitFor(() => {
        expect(screen.getByText('Increase life cover to protect your family')).toBeInTheDocument();
      });

      // Filter to only SAVINGS
      const typeFilter = screen.getByLabelText('Filter by Type');
      fireEvent.change(typeFilter, { target: { value: 'SAVINGS' } });

      await waitFor(() => {
        expect(screen.getByText('Use your remaining ISA allowance')).toBeInTheDocument();
        expect(screen.queryByText('Increase life cover to protect your family')).not.toBeInTheDocument();
      });
    });
  });

  describe('Actions', () => {
    test('dismisses recommendation on button click', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockRecommendations }),
      });

      render(<RecommendationsList />);

      await waitFor(() => {
        expect(screen.getByText('Increase life cover to protect your family')).toBeInTheDocument();
      });

      // Mock dismiss API call
      fetch.mockResolvedValueOnce({ ok: true });

      const dismissButtons = screen.getAllByText('Dismiss');
      fireEvent.click(dismissButtons[0]);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          '/api/v1/recommendations/1/dismiss',
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              Authorization: 'Bearer fake-token',
            }),
          })
        );
      });

      // Card should be removed
      await waitFor(() => {
        expect(screen.queryByText('Increase life cover to protect your family')).not.toBeInTheDocument();
      });
    });

    test('marks recommendation as complete on button click', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockRecommendations }),
      });

      render(<RecommendationsList />);

      await waitFor(() => {
        expect(screen.getByText('Increase life cover to protect your family')).toBeInTheDocument();
      });

      // Mock complete API call
      fetch.mockResolvedValueOnce({ ok: true });

      const completeButtons = screen.getAllByText('Mark Complete');
      fireEvent.click(completeButtons[0]);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          '/api/v1/recommendations/1/complete',
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              Authorization: 'Bearer fake-token',
            }),
          })
        );
      });

      // Should show completed badge
      await waitFor(() => {
        expect(screen.getByText('✓ Completed')).toBeInTheDocument();
      });
    });

    test('shows confirmation dialog for destructive actions', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockRecommendations }),
      });

      render(<RecommendationsList />);

      await waitFor(() => {
        expect(screen.getByText('Increase life cover to protect your family')).toBeInTheDocument();
      });

      const dismissButtons = screen.getAllByText('Dismiss');
      fireEvent.click(dismissButtons[0]);

      expect(global.confirm).toHaveBeenCalledWith('Are you sure you want to dismiss this recommendation?');
    });
  });

  describe('Empty states', () => {
    test('handles empty state when no recommendations', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: [] }),
      });

      render(<RecommendationsList />);

      await waitFor(() => {
        expect(screen.getByText('Great job! You\'re making the most of your finances.')).toBeInTheDocument();
      });

      expect(screen.getByText('Generate Recommendations')).toBeInTheDocument();
    });

    test('shows empty state when filters return no results', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockRecommendations }),
      });

      render(<RecommendationsList />);

      await waitFor(() => {
        expect(screen.getByText('Increase life cover to protect your family')).toBeInTheDocument();
      });

      // Filter to a type that doesn't exist
      const typeFilter = screen.getByLabelText('Filter by Type');
      fireEvent.change(typeFilter, { target: { value: 'INVESTMENT' } });

      await waitFor(() => {
        expect(screen.getByText(/No recommendations match your current filters/)).toBeInTheDocument();
      });
    });
  });

  describe('Error states', () => {
    test('handles API error gracefully', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      render(<RecommendationsList />);

      await waitFor(() => {
        expect(screen.getByText('Error Loading Recommendations')).toBeInTheDocument();
      });

      expect(screen.getByText(/Failed to load recommendations/)).toBeInTheDocument();
      expect(screen.getByText('Try Again')).toBeInTheDocument();
    });

    test('handles 401 authentication error by redirecting to login', async () => {
      fetch.mockResolvedValueOnce({ ok: false, status: 401 });

      render(<RecommendationsList />);

      await waitFor(() => {
        expect(authStorage.clear).toHaveBeenCalled();
        expect(window.location.href).toBe('/login');
      });
    });

    test('shows try again button on error', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      render(<RecommendationsList />);

      await waitFor(() => {
        expect(screen.getByText('Try Again')).toBeInTheDocument();
      });

      // Click try again
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockRecommendations }),
      });

      fireEvent.click(screen.getByText('Try Again'));

      await waitFor(() => {
        expect(screen.getByText('Increase life cover to protect your family')).toBeInTheDocument();
      });
    });
  });

  describe('Expandable sections', () => {
    test('expands action items on click', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockRecommendations }),
      });

      render(<RecommendationsList />);

      await waitFor(() => {
        expect(screen.getByText('Increase life cover to protect your family')).toBeInTheDocument();
      });

      const expandButtons = screen.getAllByText('Why this matters');
      fireEvent.click(expandButtons[0]);

      await waitFor(() => {
        expect(screen.getByText('Current cover: £100,000')).toBeInTheDocument();
        expect(screen.getByText('Recommended: £250,000')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    test('has accessible labels for filters', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ recommendations: mockRecommendations }),
      });

      render(<RecommendationsList />);

      await waitFor(() => {
        expect(screen.getByLabelText('Filter by Priority')).toBeInTheDocument();
      });

      expect(screen.getByLabelText('Filter by Type')).toBeInTheDocument();
    });
  });
});
