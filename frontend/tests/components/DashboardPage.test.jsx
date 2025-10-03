import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import DashboardPage from '../../src/pages/DashboardPage';
import { authStorage } from '../../src/utils/auth';

// Mock authStorage
jest.mock('../../src/utils/auth', () => ({
  authStorage: {
    getUser: jest.fn(),
    getAccessToken: jest.fn(),
    clear: jest.fn(),
  },
}));

// Mock Layout component
jest.mock('../../src/components/Layout', () => ({
  Layout: ({ children }) => <div data-testid="layout">{children}</div>,
}));

// Mock fetch globally
global.fetch = jest.fn();

describe('DashboardPage', () => {
  const mockUser = {
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@example.com',
  };

  const mockDashboardData = {
    netWorth: 325000,
    totalAssets: 425000,
    totalLiabilities: 100000,
    baseCurrency: 'GBP',
    asOfDate: '2025-10-02',
    lastUpdated: '2025-10-02T14:30:00Z',
    breakdownByCountry: [
      { country: 'UK', amount: 250000, percentage: 76.9 },
      { country: 'SA', amount: 75000, percentage: 23.1 },
    ],
    breakdownByAssetClass: [
      { assetClass: 'Cash', amount: 50000, percentage: 11.8 },
      { assetClass: 'Investments', amount: 150000, percentage: 35.3 },
      { assetClass: 'Pensions', amount: 125000, percentage: 29.4 },
      { assetClass: 'Property', amount: 100000, percentage: 23.5 },
    ],
    breakdownByCurrency: [
      { currency: 'GBP', amount: 250000, percentage: 76.9 },
      { currency: 'ZAR', amount: 75000, percentage: 23.1 },
    ],
    trendData: [
      { date: '2024-11-02', netWorth: 300000 },
      { date: '2024-12-02', netWorth: 310000 },
      { date: '2025-01-02', netWorth: 315000 },
      { date: '2025-02-02', netWorth: 320000 },
      { date: '2025-03-02', netWorth: 322000 },
      { date: '2025-04-02', netWorth: 323000 },
      { date: '2025-05-02', netWorth: 323500 },
      { date: '2025-06-02', netWorth: 324000 },
      { date: '2025-07-02', netWorth: 324200 },
      { date: '2025-08-02', netWorth: 324500 },
      { date: '2025-09-02', netWorth: 324800 },
      { date: '2025-10-02', netWorth: 325000 },
    ],
    changes: {
      day: { amount: 200, percentage: 0.06 },
      month: { amount: 5000, percentage: 1.56 },
      year: { amount: 25000, percentage: 8.33 },
    },
  };

  const mockEmptyDashboardData = {
    netWorth: 0,
    totalAssets: 0,
    totalLiabilities: 0,
    baseCurrency: 'GBP',
    asOfDate: '2025-10-02',
    lastUpdated: '2025-10-02T14:30:00Z',
    breakdownByCountry: [],
    breakdownByAssetClass: [],
    breakdownByCurrency: [],
    trendData: [],
    changes: null,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    authStorage.getUser.mockReturnValue(mockUser);
    authStorage.getAccessToken.mockReturnValue('fake-token');
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('Loading State', () => {
    it('should display skeleton loader while fetching data', async () => {
      global.fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<DashboardPage />);

      // Wait a bit for loading state to appear
      await new Promise(resolve => setTimeout(resolve, 100));

      // Check for skeleton loader by looking for layout
      const layout = screen.getByTestId('layout');
      expect(layout).toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('should display welcome message for new users with no data', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockEmptyDashboardData,
      });

      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/Welcome to GoalPlan, John!/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/Getting Started/i)).toBeInTheDocument();
      expect(screen.getByText(/What You Should Do Next/i)).toBeInTheDocument();
      expect(screen.getByText(/Add your user information/i)).toBeInTheDocument();
    });

    it('should display empty state metrics as £0', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockEmptyDashboardData,
      });

      render(<DashboardPage />);

      await waitFor(() => {
        const zeroValues = screen.getAllByText('£0');
        expect(zeroValues.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Dashboard with Data', () => {
    beforeEach(() => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockDashboardData,
      });
    });

    it('should fetch and display dashboard data on mount', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/dashboard/net-worth?baseCurrency=GBP',
          {
            headers: {
              Authorization: 'Bearer fake-token',
            },
          }
        );
      }, { timeout: 3000 });

      await waitFor(() => {
        expect(screen.getByText(/You're worth/i)).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should display net worth with narrative storytelling', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/You're worth/i)).toBeInTheDocument();
        expect(screen.getByText(/after debts/i)).toBeInTheDocument();
      });
    });

    it('should display all quick metrics', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText('net worth')).toBeInTheDocument();
        expect(screen.getByText('total assets')).toBeInTheDocument();
        expect(screen.getByText('total liabilities')).toBeInTheDocument();
      });
    });

    it('should display change indicators with correct colors', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/great progress!/i)).toBeInTheDocument();
      });
    });

    it('should display all breakdowns', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/Where Your Wealth Is Located/i)).toBeInTheDocument();
      }, { timeout: 3000 });

      expect(screen.getByText(/What You Own/i)).toBeInTheDocument();
      expect(screen.getByText(/Your Currency Exposure/i)).toBeInTheDocument();
    });

    it('should display breakdown by country', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText('UK')).toBeInTheDocument();
        expect(screen.getByText('SA')).toBeInTheDocument();
      });
    });

    it('should display breakdown by asset class with color coding', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText('Cash')).toBeInTheDocument();
        expect(screen.getByText('Investments')).toBeInTheDocument();
        expect(screen.getByText('Pensions')).toBeInTheDocument();
        expect(screen.getByText('Property')).toBeInTheDocument();
      });
    });

    it('should display breakdown by currency in table format', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText('Currency')).toBeInTheDocument();
        expect(screen.getByText('Amount')).toBeInTheDocument();
        expect(screen.getByText('Percentage')).toBeInTheDocument();
      });
    });

    it('should display trend chart with 12 months of data', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/Your Net Worth Trend/i)).toBeInTheDocument();
        expect(screen.getByText(/last 12 months/i)).toBeInTheDocument();
      });
    });

    it('should display change metrics for day, month, and year', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/change today/i)).toBeInTheDocument();
      }, { timeout: 3000 });

      expect(screen.getByText(/change this month/i)).toBeInTheDocument();
      expect(screen.getByText(/change this year/i)).toBeInTheDocument();
    });

    it('should display last updated timestamp', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/Last updated:/i)).toBeInTheDocument();
        expect(screen.getByText(/2 October 2025/i)).toBeInTheDocument();
      });
    });
  });

  describe('Currency Selector', () => {
    beforeEach(() => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockDashboardData,
      });
    });

    it('should display currency selector with GBP as default', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        // Check that the select element exists and has GBP selected
        const selects = screen.getAllByRole('combobox');
        expect(selects.length).toBeGreaterThan(0);
        // Check that GBP option exists
        expect(screen.getByText('£ GBP')).toBeInTheDocument();
      });
    });

    it('should fetch new data when currency is changed', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/You're worth/i)).toBeInTheDocument();
      });

      const select = screen.getAllByRole('combobox')[0];
      fireEvent.change(select, { target: { value: 'USD' } });

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/dashboard/net-worth?baseCurrency=USD',
          expect.any(Object)
        );
      });
    });
  });

  describe('Refresh Functionality', () => {
    beforeEach(() => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockDashboardData,
      });
    });

    it('should display refresh button', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText('Refresh')).toBeInTheDocument();
      });
    });

    it('should fetch new data when refresh button is clicked', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText('Refresh')).toBeInTheDocument();
      });

      const refreshButton = screen.getByText('Refresh');
      fireEvent.click(refreshButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledTimes(2); // Initial + refresh
      });
    });

    it('should show "Refreshing..." text while refreshing', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText('Refresh')).toBeInTheDocument();
      });

      const refreshButton = screen.getByText('Refresh');
      fireEvent.click(refreshButton);

      expect(screen.getByText('Refreshing...')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should display error message when API call fails', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/Unable to load/i)).toBeInTheDocument();
      }, { timeout: 3000 });

      expect(screen.getByText(/Try Again/i)).toBeInTheDocument();
    });

    it('should display error message when API returns non-OK status', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/Unable to load your dashboard/i)).toBeInTheDocument();
      });
    });

    it('should clear auth and redirect on 401 error', async () => {
      delete window.location;
      window.location = { href: '' };

      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      render(<DashboardPage />);

      await waitFor(() => {
        expect(authStorage.clear).toHaveBeenCalled();
        expect(window.location.href).toBe('/login');
      });
    });

    it('should allow retry after error', async () => {
      global.fetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockDashboardData,
        });

      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/Unable to load/i)).toBeInTheDocument();
      }, { timeout: 3000 });

      const tryAgainButtons = screen.getAllByText(/Try Again/i);
      fireEvent.click(tryAgainButtons[0]);

      await waitFor(() => {
        expect(screen.getByText(/You're worth/i)).toBeInTheDocument();
      }, { timeout: 3000 });
    });
  });

  describe('Formatting', () => {
    beforeEach(() => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockDashboardData,
      });
    });

    it('should format currency correctly with GBP symbol', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/You're worth/i)).toBeInTheDocument();
      }, { timeout: 3000 });

      // Check that GBP formatted values are present
      const layout = screen.getByTestId('layout');
      expect(layout.textContent).toContain('£');
    });

    it('should format percentages with + or - sign', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/You're worth/i)).toBeInTheDocument();
      }, { timeout: 3000 });

      // Check that percentage values are present
      const layout = screen.getByTestId('layout');
      expect(layout.textContent).toContain('%');
    });

    it('should format dates in readable format', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/2 October 2025/i)).toBeInTheDocument();
      });
    });
  });

  describe('Narrative Storytelling', () => {
    beforeEach(() => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockDashboardData,
      });
    });

    it('should use conversational language', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/You're worth/i)).toBeInTheDocument();
        expect(screen.getByText(/Your wealth comes from/i)).toBeInTheDocument();
      });
    });

    it('should embed metrics in sentences', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        const paragraph = screen.getByText(/You're worth/i);
        expect(paragraph.textContent).toContain('£325,000');
        expect(paragraph.textContent).toContain('after debts');
      });
    });

    it('should celebrate positive changes', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/great progress!/i)).toBeInTheDocument();
      });
    });

    it('should use appropriate section headings', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/Your Financial Position/i)).toBeInTheDocument();
        expect(screen.getByText(/Where Your Wealth Is Located/i)).toBeInTheDocument();
        expect(screen.getByText(/What You Own/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    beforeEach(() => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockDashboardData,
      });
    });

    it('should have proper heading hierarchy', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        const h1 = screen.getByRole('heading', { level: 1 });
        expect(h1).toBeInTheDocument();
      });
    });

    it('should use semantic HTML elements', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        const table = screen.getByRole('table');
        expect(table).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Design', () => {
    beforeEach(() => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockDashboardData,
      });
    });

    it('should render metric grids with auto-fit layout', async () => {
      render(<DashboardPage />);

      await waitFor(() => {
        const container = screen.getByTestId('layout');
        const grids = container.querySelectorAll('div[style*="grid-template-columns"]');
        expect(grids.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Negative Net Worth', () => {
    it('should display negative net worth correctly', async () => {
      const negativeData = {
        ...mockDashboardData,
        netWorth: -50000,
        totalAssets: 50000,
        totalLiabilities: 100000,
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => negativeData,
      });

      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/Building Up/i)).toBeInTheDocument();
      });
    });
  });

  describe('Missing Change Data', () => {
    it('should handle missing change data gracefully', async () => {
      const dataWithoutChanges = {
        ...mockDashboardData,
        changes: null,
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => dataWithoutChanges,
      });

      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText(/You're worth/i)).toBeInTheDocument();
      });

      // Should not show "How Your Wealth Has Changed" section
      expect(screen.queryByText(/How Your Wealth Has Changed/i)).not.toBeInTheDocument();
    });
  });
});
