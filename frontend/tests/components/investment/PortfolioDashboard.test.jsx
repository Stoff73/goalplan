import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { PortfolioDashboard } from '../../../src/components/investment/PortfolioDashboard';
import { authStorage } from '../../../src/utils/auth';

// Mock authStorage
jest.mock('../../../src/utils/auth', () => ({
  authStorage: {
    getAccessToken: jest.fn(),
    clear: jest.fn(),
  },
}));

// Mock fetch globally
global.fetch = jest.fn();

describe('PortfolioDashboard', () => {
  const mockAccessToken = 'mock-access-token';

  beforeEach(() => {
    jest.clearAllMocks();
    authStorage.getAccessToken.mockReturnValue(mockAccessToken);
    delete window.location;
    window.location = { href: '' };
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  const mockPortfolioData = {
    totalValue: {
      gbp: 83333.33,
      zar: 1600000.00,
    },
    totalUnrealizedGain: 8333.33,
    totalUnrealizedGainPercentage: 11.11,
    totalAccounts: 3,
    totalHoldings: 15,
    ytdDividendIncome: 1250.50,
    assetAllocation: [
      {
        assetClass: 'EQUITY',
        value: 50000.00,
        percentage: 60.0,
      },
      {
        assetClass: 'FIXED_INCOME',
        value: 20000.00,
        percentage: 24.0,
      },
      {
        assetClass: 'PROPERTY',
        value: 10000.00,
        percentage: 12.0,
      },
      {
        assetClass: 'CASH',
        value: 3333.33,
        percentage: 4.0,
      },
    ],
    topHoldings: [
      {
        ticker: 'VWRL',
        name: 'Vanguard FTSE All-World ETF',
        currentValue: 15000.00,
        unrealizedGain: 2000.00,
        unrealizedGainPercentage: 15.38,
        portfolioPercentage: 18.0,
      },
      {
        ticker: 'AAPL',
        name: 'Apple Inc.',
        currentValue: 12000.00,
        unrealizedGain: 3000.00,
        unrealizedGainPercentage: 33.33,
        portfolioPercentage: 14.4,
      },
      {
        ticker: 'MSFT',
        name: 'Microsoft Corporation',
        currentValue: 10000.00,
        unrealizedGain: 1500.00,
        unrealizedGainPercentage: 17.65,
        portfolioPercentage: 12.0,
      },
      {
        ticker: 'GOOGL',
        name: 'Alphabet Inc.',
        currentValue: 8000.00,
        unrealizedGain: -500.00,
        unrealizedGainPercentage: -5.88,
        portfolioPercentage: 9.6,
      },
      {
        ticker: 'AMZN',
        name: 'Amazon.com Inc.',
        currentValue: 7000.00,
        unrealizedGain: 1000.00,
        unrealizedGainPercentage: 16.67,
        portfolioPercentage: 8.4,
      },
    ],
    performanceSummary: {
      timeWeightedReturn: 12.5,
      moneyWeightedReturn: 11.8,
      benchmarkComparison: {
        portfolioReturn: 12.5,
        benchmarkReturn: 10.0,
        outperformance: 2.5,
      },
    },
  };

  const mockPortfolioDataNegativeGain = {
    ...mockPortfolioData,
    totalUnrealizedGain: -5000.00,
    totalUnrealizedGainPercentage: -6.25,
  };

  describe('Loading State', () => {
    test('displays loading state while fetching data', () => {
      global.fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<PortfolioDashboard />);

      expect(screen.getByText(/loading your portfolio/i)).toBeInTheDocument();
    });
  });

  describe('Error State', () => {
    test('displays error message when fetch fails', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/failed to load portfolio data/i)).toBeInTheDocument();
      });
    });

    test('displays try again button on error', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      render(<PortfolioDashboard />);

      await waitFor(() => {
        const tryAgainButton = screen.getByRole('button', { name: /try again/i });
        expect(tryAgainButton).toBeInTheDocument();
      });
    });

    test('retries fetch when try again button is clicked', async () => {
      global.fetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPortfolioData,
        });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/failed to load portfolio data/i)).toBeInTheDocument();
      });

      const tryAgainButton = screen.getByRole('button', { name: /try again/i });
      fireEvent.click(tryAgainButton);

      await waitFor(() => {
        expect(screen.getByText(/your investment portfolio/i)).toBeInTheDocument();
        expect(screen.getByText(/£83,333.33/)).toBeInTheDocument();
      });
    });

    test('redirects to login on 401 error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(authStorage.clear).toHaveBeenCalled();
        expect(window.location.href).toBe('/login');
      });
    });
  });

  describe('Empty State', () => {
    test('displays empty state when no portfolio exists', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/start building your portfolio/i)).toBeInTheDocument();
        expect(screen.getByText(/you haven't added any investment accounts yet/i)).toBeInTheDocument();
      });
    });

    test('displays empty state when totalAccounts is 0', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...mockPortfolioData, totalAccounts: 0 }),
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/start building your portfolio/i)).toBeInTheDocument();
      });
    });

    test('displays add account button in empty state', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        const addButton = screen.getByRole('button', { name: /add your first investment account/i });
        expect(addButton).toBeInTheDocument();
      });
    });
  });

  describe('Portfolio Summary', () => {
    test('renders portfolio summary with correct data', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioData,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        // Check title
        expect(screen.getByText(/your investment portfolio: growing strong/i)).toBeInTheDocument();

        // Check total value
        expect(screen.getByText('£83,333.33')).toBeInTheDocument();

        // Check unrealized gain
        expect(screen.getByText(/grown by/i)).toBeInTheDocument();
        expect(screen.getByText(/£8,333.33/i)).toBeInTheDocument();
        expect(screen.getByText(/\+11\.11%/i)).toBeInTheDocument();

        // Check holdings and accounts (appear in multiple places)
        expect(screen.getAllByText(/15/i).length).toBeGreaterThan(0);
        expect(screen.getAllByText(/holdings/i).length).toBeGreaterThan(0);
        expect(screen.getAllByText(/3/).length).toBeGreaterThan(0);
        expect(screen.getAllByText(/accounts/i).length).toBeGreaterThan(0);

        // Check dividend income
        expect(screen.getByText(/£1,250\.50/i)).toBeInTheDocument();
        expect(screen.getByText(/dividend income/i)).toBeInTheDocument();
      });
    });

    test('renders portfolio summary with negative gains', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioDataNegativeGain,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        // Check title reflects loss
        expect(screen.getByText(/your investment portfolio: needs attention/i)).toBeInTheDocument();

        // Check loss messaging
        expect(screen.getByText(/decreased by/i)).toBeInTheDocument();
        expect(screen.getByText(/£5,000\.00/i)).toBeInTheDocument();
        expect(screen.getByText(/-6\.25%/i)).toBeInTheDocument();
        expect(screen.getByText(/let's review your strategy/i)).toBeInTheDocument();
      });
    });

    test('uses authorization header in fetch request', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioData,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/investments/portfolio/summary',
          expect.objectContaining({
            headers: {
              Authorization: `Bearer ${mockAccessToken}`,
            },
          })
        );
      });
    });
  });

  describe('Asset Allocation', () => {
    test('renders asset allocation section', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioData,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/your asset allocation/i)).toBeInTheDocument();
        expect(screen.getByText(/diversified across different asset classes/i)).toBeInTheDocument();
      });
    });

    test('renders all asset classes', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioData,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.getByText('EQUITY')).toBeInTheDocument();
        expect(screen.getByText('FIXED_INCOME')).toBeInTheDocument();
        expect(screen.getByText('PROPERTY')).toBeInTheDocument();
        expect(screen.getByText('CASH')).toBeInTheDocument();

        // Use getAllByText for percentages as they may appear multiple times
        expect(screen.getAllByText('60.0%').length).toBeGreaterThan(0);
        expect(screen.getAllByText('24.0%').length).toBeGreaterThan(0);
        expect(screen.getAllByText('12.0%').length).toBeGreaterThan(0);
        expect(screen.getAllByText('4.0%').length).toBeGreaterThan(0);
      });
    });

    test('toggles asset allocation educational content', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioData,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/tell me more about asset allocation/i)).toBeInTheDocument();
      });

      // Educational content should not be visible initially
      expect(screen.queryByText(/asset allocation is how you divide your portfolio/i)).not.toBeInTheDocument();

      // Click to expand
      const expandButton = screen.getByText(/tell me more about asset allocation/i);
      fireEvent.click(expandButton);

      // Educational content should now be visible
      await waitFor(() => {
        expect(screen.getByText(/asset allocation is how you divide your portfolio/i)).toBeInTheDocument();
      });

      // Click again to collapse
      fireEvent.click(expandButton);

      await waitFor(() => {
        expect(screen.queryByText(/asset allocation is how you divide your portfolio/i)).not.toBeInTheDocument();
      });
    });

    test('does not render asset allocation if no data', async () => {
      const dataWithoutAllocation = { ...mockPortfolioData, assetAllocation: [] };
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => dataWithoutAllocation,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.queryByText(/your asset allocation/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Top Holdings Table', () => {
    test('renders top holdings table', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioData,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/your top holdings/i)).toBeInTheDocument();
        expect(screen.getByText(/largest holdings by value/i)).toBeInTheDocument();
      });
    });

    test('renders table headers', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioData,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.getByText('Ticker')).toBeInTheDocument();
        expect(screen.getByText('Name')).toBeInTheDocument();
        expect(screen.getByText('Value')).toBeInTheDocument();
        expect(screen.getByText('Gain/Loss')).toBeInTheDocument();
        expect(screen.getByText('% of Portfolio')).toBeInTheDocument();
      });
    });

    test('renders all top holdings', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioData,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.getByText('VWRL')).toBeInTheDocument();
        expect(screen.getByText('Vanguard FTSE All-World ETF')).toBeInTheDocument();
        expect(screen.getByText('£15,000.00')).toBeInTheDocument();

        expect(screen.getByText('AAPL')).toBeInTheDocument();
        expect(screen.getByText('Apple Inc.')).toBeInTheDocument();

        expect(screen.getByText('GOOGL')).toBeInTheDocument();
        expect(screen.getByText('Alphabet Inc.')).toBeInTheDocument();
      });
    });

    test('displays gains and losses with correct colors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioData,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        // Positive gain should be present
        expect(screen.getByText(/£2,000\.00/i)).toBeInTheDocument();
        expect(screen.getByText(/\+15\.38%/i)).toBeInTheDocument();

        // Negative gain should be present (with - prefix before £)
        expect(screen.getByText(/-£500\.00/i)).toBeInTheDocument();
        expect(screen.getByText(/-5\.88%/i)).toBeInTheDocument();
      });
    });

    test('limits display to top 10 holdings', async () => {
      const dataWithManyHoldings = {
        ...mockPortfolioData,
        topHoldings: Array(20).fill(mockPortfolioData.topHoldings[0]),
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => dataWithManyHoldings,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        const rows = screen.getAllByText('VWRL');
        expect(rows.length).toBeLessThanOrEqual(10);
      });
    });

    test('does not render holdings table if no data', async () => {
      const dataWithoutHoldings = { ...mockPortfolioData, topHoldings: [] };
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => dataWithoutHoldings,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.queryByText(/your top holdings/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Performance Overview', () => {
    test('renders performance summary', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioData,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/performance overview/i)).toBeInTheDocument();
        expect(screen.getByText(/returned/i)).toBeInTheDocument();
        expect(screen.getByText(/\+12\.50%/i)).toBeInTheDocument();
        expect(screen.getByText(/solid performance/i)).toBeInTheDocument();
      });
    });

    test('renders benchmark comparison', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioData,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/outperformed/i)).toBeInTheDocument();
        expect(screen.getByText(/\+2\.50%/i)).toBeInTheDocument();
      });
    });

    test('renders negative performance correctly', async () => {
      const dataWithNegativePerformance = {
        ...mockPortfolioData,
        performanceSummary: {
          timeWeightedReturn: -5.5,
          benchmarkComparison: {
            outperformance: -2.0,
          },
        },
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => dataWithNegativePerformance,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/returned/i)).toBeInTheDocument();
        expect(screen.getByText(/-5\.50%/i)).toBeInTheDocument();
        expect(screen.getByText(/markets can be volatile in the short term/i)).toBeInTheDocument();
        expect(screen.getByText(/underperformed/i)).toBeInTheDocument();
        expect(screen.getByText(/\+2\.00%/i)).toBeInTheDocument(); // formatPercentage uses absolute value
      });
    });

    test('does not render performance section if no data', async () => {
      const dataWithoutPerformance = { ...mockPortfolioData, performanceSummary: null };
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => dataWithoutPerformance,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.queryByText(/performance overview/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    test('expandable section has proper aria attributes', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioData,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        const expandButton = screen.getByText(/tell me more about asset allocation/i);
        expect(expandButton.closest('button')).toHaveAttribute('aria-expanded', 'false');
      });

      const expandButton = screen.getByText(/tell me more about asset allocation/i);
      fireEvent.click(expandButton);

      await waitFor(() => {
        expect(expandButton.closest('button')).toHaveAttribute('aria-expanded', 'true');
      });
    });

    test('buttons have proper roles', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioData,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        const buttons = screen.getAllByRole('button');
        expect(buttons.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Currency Formatting', () => {
    test('formats large numbers with commas', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioData,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        expect(screen.getByText('£83,333.33')).toBeInTheDocument();
        expect(screen.getByText('£15,000.00')).toBeInTheDocument();
      });
    });

    test('formats short numbers with k/m suffixes', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolioData,
      });

      render(<PortfolioDashboard />);

      await waitFor(() => {
        // Compact metrics use short format
        expect(screen.getByText('£83k')).toBeInTheDocument();
        expect(screen.getByText('£8k')).toBeInTheDocument();
      });
    });
  });
});
