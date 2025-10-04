import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { CoverageGapWidget } from '../../../src/components/protection/CoverageGapWidget';
import { authStorage } from '../../../src/utils/auth';

// Mock authStorage
jest.mock('../../../src/utils/auth', () => ({
  authStorage: {
    getAccessToken: jest.fn(),
    clear: jest.fn(),
  },
}));

// Mock fetch
global.fetch = jest.fn();

describe('CoverageGapWidget', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Set up default mock return value for getAccessToken
    authStorage.getAccessToken.mockReturnValue('mock-token');
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('Loading State', () => {
    test('displays loading state initially', () => {
      global.fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<CoverageGapWidget />);

      expect(screen.getByText('Loading coverage analysis...')).toBeInTheDocument();
      expect(screen.getByText('⏳')).toBeInTheDocument();
    });
  });

  describe('Error State', () => {
    test('displays error message when API call fails', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Error')).toBeInTheDocument();
        expect(screen.getByText('Failed to load coverage analysis. Please try again.')).toBeInTheDocument();
      });
    });

    test('displays try again button on error', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Try Again')).toBeInTheDocument();
      });
    });

    test('retries loading when try again button clicked', async () => {
      global.fetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            currentTotalCover: 500000,
            recommendedCover: 500000,
            coverageGap: 0,
          }),
        });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Try Again')).toBeInTheDocument();
      });

      const tryAgainButton = screen.getByText('Try Again');
      fireEvent.click(tryAgainButton);

      await waitFor(() => {
        expect(screen.getByText('Well Protected')).toBeInTheDocument();
      });
    });

    test('handles 401 unauthorized by clearing auth and redirecting', async () => {
      const originalLocation = window.location;
      delete window.location;
      window.location = { href: '' };

      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(authStorage.clear).toHaveBeenCalled();
        expect(window.location.href).toBe('/login');
      });

      window.location = originalLocation;
    });
  });

  describe('Empty State (No Analysis)', () => {
    test('displays empty state when no analysis exists (404)', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Your Coverage Protection Status')).toBeInTheDocument();
        expect(screen.getByText('Not Calculated')).toBeInTheDocument();
        expect(screen.getByText(/You haven't calculated your coverage needs yet/)).toBeInTheDocument();
      });
    });

    test('displays calculate needs button in empty state', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Calculate My Needs →')).toBeInTheDocument();
      });
    });

    test('displays educational content in empty state', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Why calculate coverage needs?')).toBeInTheDocument();
        expect(screen.getByText(/Most families need life insurance equal to 10-12 times/)).toBeInTheDocument();
      });
    });
  });

  describe('ADEQUATE Status (Green)', () => {
    test('displays ADEQUATE status when coverage is 100%+', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 500000,
          recommendedCover: 500000,
          coverageGap: 0,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Well Protected')).toBeInTheDocument();
        expect(screen.getByText(/You're well protected!/)).toBeInTheDocument();
      });
    });

    test('displays ADEQUATE status when coverage is 90-100%', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 450000,
          recommendedCover: 500000,
          coverageGap: 50000,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Well Protected')).toBeInTheDocument();
      });
    });

    test('displays over-insured message when coverage exceeds 100%', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 600000,
          recommendedCover: 500000,
          coverageGap: 0,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText(/exceeds/)).toBeInTheDocument();
      });
    });

    test('displays review coverage button for adequate status', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 500000,
          recommendedCover: 500000,
          coverageGap: 0,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Review Coverage →')).toBeInTheDocument();
      });
    });

    test('displays correct percentage covered for adequate status', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 475000,
          recommendedCover: 500000,
          coverageGap: 25000,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('95% of recommended coverage')).toBeInTheDocument();
      });
    });
  });

  describe('UNDER_INSURED Status (Yellow)', () => {
    test('displays UNDER_INSURED status when coverage is 70-89%', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 400000,
          recommendedCover: 500000,
          coverageGap: 100000,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Needs Attention')).toBeInTheDocument();
        expect(screen.getByText(/You need £100,000 more coverage/)).toBeInTheDocument();
      });
    });

    test('displays correct coverage gap amount for under-insured status', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 350000,
          recommendedCover: 500000,
          coverageGap: 150000,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText(/£150,000 more coverage/)).toBeInTheDocument();
      });
    });

    test('displays add policy button for under-insured status', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 400000,
          recommendedCover: 500000,
          coverageGap: 100000,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Add Policy →')).toBeInTheDocument();
      });
    });

    test('displays correct percentage covered for under-insured status', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 400000,
          recommendedCover: 500000,
          coverageGap: 100000,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('80% of recommended coverage')).toBeInTheDocument();
      });
    });
  });

  describe('CRITICAL Status (Red)', () => {
    test('displays CRITICAL status when coverage is <70%', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 200000,
          recommendedCover: 500000,
          coverageGap: 300000,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Critical Gap')).toBeInTheDocument();
        expect(screen.getByText(/Critical gap! You need £300,000 more coverage/)).toBeInTheDocument();
      });
    });

    test('displays correct coverage gap amount for critical status', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 100000,
          recommendedCover: 500000,
          coverageGap: 400000,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText(/£400,000 more coverage/)).toBeInTheDocument();
      });
    });

    test('displays add policy button for critical status', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 200000,
          recommendedCover: 500000,
          coverageGap: 300000,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Add Policy →')).toBeInTheDocument();
      });
    });

    test('displays correct percentage covered for critical status', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 200000,
          recommendedCover: 500000,
          coverageGap: 300000,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('40% of recommended coverage')).toBeInTheDocument();
      });
    });
  });

  describe('Metrics Display', () => {
    test('displays current coverage metric', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 300000,
          recommendedCover: 500000,
          coverageGap: 200000,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('£300k')).toBeInTheDocument();
        expect(screen.getByText('current coverage')).toBeInTheDocument();
      });
    });

    test('displays recommended coverage metric', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 300000,
          recommendedCover: 500000,
          coverageGap: 200000,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('£500k')).toBeInTheDocument();
        expect(screen.getByText('recommended')).toBeInTheDocument();
      });
    });

    test('displays coverage gap metric', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 300000,
          recommendedCover: 500000,
          coverageGap: 200000,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('£200k')).toBeInTheDocument();
        expect(screen.getByText('coverage gap')).toBeInTheDocument();
      });
    });

    test('formats large numbers correctly (millions)', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 1500000,
          recommendedCover: 2000000,
          coverageGap: 500000,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('£1.5m')).toBeInTheDocument();
        expect(screen.getByText('£2.0m')).toBeInTheDocument();
      });
    });
  });

  describe('Progressive Disclosure', () => {
    test('expandable section is collapsed by default', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 500000,
          recommendedCover: 500000,
          coverageGap: 0,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Tell me more about coverage needs')).toBeInTheDocument();
      });

      expect(screen.queryByText(/10-12 times your annual income/)).not.toBeInTheDocument();
    });

    test('expandable section opens when clicked', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 500000,
          recommendedCover: 500000,
          coverageGap: 0,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Tell me more about coverage needs')).toBeInTheDocument();
      });

      const expandButton = screen.getByText('Tell me more about coverage needs');
      fireEvent.click(expandButton);

      await waitFor(() => {
        expect(screen.getByText(/10-12 times your annual income/)).toBeInTheDocument();
      });
    });

    test('expandable section shows educational content', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 500000,
          recommendedCover: 500000,
          coverageGap: 0,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Tell me more about coverage needs')).toBeInTheDocument();
      });

      const expandButton = screen.getByText('Tell me more about coverage needs');
      fireEvent.click(expandButton);

      await waitFor(() => {
        expect(screen.getByText(/Outstanding debts like mortgages and loans/)).toBeInTheDocument();
        expect(screen.getByText(/Future expenses like children's education/)).toBeInTheDocument();
      });
    });

    test('expandable section shows tip for underinsured status', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 200000,
          recommendedCover: 500000,
          coverageGap: 300000,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Tell me more about coverage needs')).toBeInTheDocument();
      });

      const expandButton = screen.getByText('Tell me more about coverage needs');
      fireEvent.click(expandButton);

      await waitFor(() => {
        expect(screen.getByText(/Many people are underinsured without realizing it/)).toBeInTheDocument();
      });
    });
  });

  describe('API Integration', () => {
    test('calls API with correct endpoint and authorization', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 500000,
          recommendedCover: 500000,
          coverageGap: 0,
        }),
      });

      render(<CoverageGapWidget />);

      // Wait for component to load and make the API call
      await waitFor(() => {
        expect(screen.getByText('Well Protected')).toBeInTheDocument();
      });

      // Now check that fetch was called correctly
      expect(global.fetch).toHaveBeenCalledTimes(1);
      const [url, options] = global.fetch.mock.calls[0];
      expect(url).toBe('/api/v1/protection/coverage-analysis/summary');
      expect(options).toBeDefined();
      expect(options.headers).toBeDefined();
      expect(options.headers.Authorization).toBe('Bearer mock-token');
    });

    test('handles null/undefined values gracefully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: null,
          recommendedCover: null,
          coverageGap: null,
        }),
      });

      render(<CoverageGapWidget />);

      await waitFor(() => {
        expect(screen.getByText('Not Calculated')).toBeInTheDocument();
      });
    });
  });

  describe('Narrative Storytelling', () => {
    test('uses conversational language for adequate status', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 500000,
          recommendedCover: 500000,
          coverageGap: 0,
        }),
      });

      const { container } = render(<CoverageGapWidget />);

      await waitFor(() => {
        // Check for narrative paragraph containing the coverage information
        const narrativeText = container.textContent;
        expect(narrativeText).toMatch(/Your current policies provide.*of protection/);
        expect(screen.getByText('Well Protected')).toBeInTheDocument();
      });
    });

    test('embeds metrics in sentences (not standalone)', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 300000,
          recommendedCover: 500000,
          coverageGap: 200000,
        }),
      });

      const { container } = render(<CoverageGapWidget />);

      await waitFor(() => {
        // Check that amounts are embedded in narrative sentences
        const narrativeText = container.textContent;
        expect(narrativeText).toMatch(/Your current policies provide.*of protection/);
      });
    });

    test('uses monospace font for currency values', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          currentTotalCover: 500000,
          recommendedCover: 500000,
          coverageGap: 0,
        }),
      });

      const { container } = render(<CoverageGapWidget />);

      await waitFor(() => {
        const monospaceElements = container.querySelectorAll('[style*="monospace"]');
        expect(monospaceElements.length).toBeGreaterThan(0);
      });
    });
  });
});
