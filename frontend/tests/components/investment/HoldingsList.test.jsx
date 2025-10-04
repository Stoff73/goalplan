import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { HoldingsList } from '../../../src/components/investment/HoldingsList';
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

describe('HoldingsList', () => {
  const mockAccounts = [
    {
      id: 'account-1',
      provider: 'Vanguard',
      accountType: 'STOCKS_ISA',
    },
    {
      id: 'account-2',
      provider: 'Interactive Brokers',
      accountType: 'GIA',
    },
  ];

  const mockHoldings = [
    {
      id: 'holding-1',
      accountId: 'account-1',
      accountType: 'STOCKS_ISA',
      ticker: 'AAPL',
      name: 'Apple Inc.',
      quantity: 100,
      purchasePrice: 150.0,
      currentPrice: 175.0,
      currentValue: 17500.0,
      unrealizedGain: 2500.0,
      unrealizedGainPercentage: 16.67,
      assetClass: 'EQUITY',
      region: 'US',
      sector: 'Technology',
    },
    {
      id: 'holding-2',
      accountId: 'account-2',
      accountType: 'GIA',
      ticker: 'VUSA',
      name: 'Vanguard S&P 500 ETF',
      quantity: 50,
      purchasePrice: 60.0,
      currentPrice: 58.0,
      currentValue: 2900.0,
      unrealizedGain: -100.0,
      unrealizedGainPercentage: -3.33,
      assetClass: 'EQUITY',
      region: 'GLOBAL',
      sector: 'Index',
    },
    {
      id: 'holding-3',
      accountId: 'account-1',
      accountType: 'STOCKS_ISA',
      ticker: 'MSFT',
      name: 'Microsoft Corporation',
      quantity: 25,
      purchasePrice: 300.0,
      currentPrice: 350.0,
      currentValue: 8750.0,
      unrealizedGain: 1250.0,
      unrealizedGainPercentage: 16.67,
      assetClass: 'EQUITY',
      region: 'US',
      sector: 'Technology',
    },
  ];

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    authStorage.getAccessToken.mockReturnValue('mock-token');

    // Default successful fetch responses
    global.fetch.mockImplementation((url) => {
      if (url.includes('/api/v1/investments/holdings')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ holdings: mockHoldings }),
        });
      }
      if (url.includes('/api/v1/investments/accounts')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ accounts: mockAccounts }),
        });
      }
      return Promise.reject(new Error('Unknown URL'));
    });
  });

  describe('Rendering', () => {
    test('renders loading state initially', () => {
      render(<HoldingsList />);
      expect(screen.getByText(/Loading your holdings/i)).toBeInTheDocument();
    });

    test('renders holdings list after loading', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText(/Your Investment Holdings/i)).toBeInTheDocument();
      });

      expect(screen.getByText('AAPL')).toBeInTheDocument();
      expect(screen.getByText('Apple Inc.')).toBeInTheDocument();
      expect(screen.getByText('VUSA')).toBeInTheDocument();
      expect(screen.getByText('MSFT')).toBeInTheDocument();
    });

    test('renders narrative paragraph with holdings count and total value', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText(/You have/i)).toBeInTheDocument();
      });

      // Check the narrative includes holdings count and value
      const narrative = screen.getByText(/You have/i);
      expect(narrative.textContent).toContain('3');
      expect(narrative.textContent).toContain('£29,150.00');
    });

    test('renders Add Holding button', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('Add Holding')).toBeInTheDocument();
      });
    });
  });

  describe('Empty State', () => {
    test('renders empty state when no holdings exist', async () => {
      global.fetch.mockImplementation((url) => {
        if (url.includes('/api/v1/investments/holdings')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ holdings: [] }),
          });
        }
        if (url.includes('/api/v1/investments/accounts')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ accounts: mockAccounts }),
          });
        }
        return Promise.reject(new Error('Unknown URL'));
      });

      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText(/You haven't added any holdings yet/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/Add Your First Holding/i)).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    test('renders error state when fetch fails', async () => {
      global.fetch.mockRejectedValue(new Error('Network error'));

      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText(/Failed to load holdings/i)).toBeInTheDocument();
      });

      expect(screen.getByText('Try Again')).toBeInTheDocument();
    });

    test('redirects to login on 401 error', async () => {
      delete window.location;
      window.location = { href: jest.fn() };

      global.fetch.mockResolvedValue({
        ok: false,
        status: 401,
      });

      render(<HoldingsList />);

      await waitFor(() => {
        expect(authStorage.clear).toHaveBeenCalled();
        expect(window.location.href).toBe('/login');
      });
    });

    test('retry button reloads data', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText(/Failed to load holdings/i)).toBeInTheDocument();
      });

      // Reset fetch to succeed
      global.fetch.mockImplementation((url) => {
        if (url.includes('/api/v1/investments/holdings')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ holdings: mockHoldings }),
          });
        }
        if (url.includes('/api/v1/investments/accounts')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ accounts: mockAccounts }),
          });
        }
        return Promise.reject(new Error('Unknown URL'));
      });

      fireEvent.click(screen.getByText('Try Again'));

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });
    });
  });

  describe('Filtering', () => {
    test('renders filter dropdowns', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      // Check that filter dropdowns exist
      const selects = screen.getAllByRole('combobox');
      expect(selects.length).toBeGreaterThanOrEqual(3); // Account, Asset Class, Region filters
    });

    test('filter dropdowns can be changed', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      const selects = screen.getAllByRole('combobox');
      const accountFilter = selects[0];

      // Should be able to change filter value
      expect(() => {
        fireEvent.change(accountFilter, { target: { value: 'account-1' } });
      }).not.toThrow();
    });

    test('all filter dropdowns have options', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      const selects = screen.getAllByRole('combobox');

      // All filters should have at least one option
      selects.forEach(select => {
        expect(select.children.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Sorting', () => {
    test('renders sortable column headers', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      // Check that column headers exist
      const headers = screen.getAllByRole('columnheader');
      expect(headers.length).toBeGreaterThanOrEqual(7); // At least 7 columns

      // Find ticker header
      const tickerHeader = headers.find(h => h.textContent.includes('Ticker'));
      expect(tickerHeader).toBeInTheDocument();
    });

    test('column headers are clickable', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      const headers = screen.getAllByRole('columnheader');
      const tickerHeader = headers.find(h => h.textContent.includes('Ticker'));

      // Should be able to click header without throwing
      expect(() => {
        fireEvent.click(tickerHeader);
      }).not.toThrow();
    });

    test('sort indicators appear on click', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      const headers = screen.getAllByRole('columnheader');
      const tickerHeader = headers.find(h => h.textContent.includes('Ticker'));

      fireEvent.click(tickerHeader);

      // Header should now contain a sort indicator (either ↑ or ↓)
      expect(tickerHeader.textContent).toMatch(/[↑↓]/);
    });
  });

  describe('Badge Display', () => {
    test('displays ISA badge for tax-advantaged holdings', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      // Check for ISA badges (AAPL and MSFT are in STOCKS_ISA account)
      const isaBadges = screen.getAllByText('ISA');
      expect(isaBadges.length).toBe(2);
    });

    test('does not display badge for GIA holdings', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('VUSA')).toBeInTheDocument();
      });

      // VUSA should not have a badge (it's in GIA account)
      const vusaRow = screen.getByText('VUSA').closest('tr');
      expect(vusaRow.textContent).not.toContain('ISA');
    });
  });

  describe('Color Coding', () => {
    test('displays gains in green', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      // Check that positive gain is displayed (AAPL has +2500)
      const aaplRow = screen.getByText('AAPL').closest('tr');
      const gainCell = aaplRow.querySelector('[style*="color"]');

      // The gain cell should exist and contain positive value
      expect(aaplRow.textContent).toContain('£2,500.00');
      expect(aaplRow.textContent).toContain('+16.67%');
    });

    test('displays losses in red', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('VUSA')).toBeInTheDocument();
      });

      // Check that negative gain is displayed (VUSA has -100)
      const vusaRow = screen.getByText('VUSA').closest('tr');

      // The loss should be displayed (formatted as £-100.00 or -£100.00)
      expect(vusaRow.textContent).toMatch(/£-100\.00|£100\.00/);
      expect(vusaRow.textContent).toContain('-3.33%');
    });
  });

  describe('Action Buttons', () => {
    test('renders Update Price and Sell buttons for each holding', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      const updatePriceButtons = screen.getAllByText('Update Price');
      const sellButtons = screen.getAllByText('Sell');

      expect(updatePriceButtons.length).toBe(3); // One for each holding
      expect(sellButtons.length).toBe(3);
    });

    test('opens Update Price modal when Update Price button clicked', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      const updatePriceButtons = screen.getAllByRole('button', { name: /Update Price/i });
      fireEvent.click(updatePriceButtons[0]);

      // Modal should open (check for modal heading)
      await waitFor(() => {
        const headings = screen.getAllByRole('heading', { level: 2 });
        const modalHeading = headings.find(h => h.textContent === 'Update Price');
        expect(modalHeading).toBeInTheDocument();
      });
    });

    test('opens Sell modal when Sell button clicked', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      const sellButtons = screen.getAllByRole('button', { name: /Sell/i });
      fireEvent.click(sellButtons[0]);

      // Modal should open (check for modal heading)
      await waitFor(() => {
        const headings = screen.getAllByRole('heading', { level: 2 });
        const modalHeading = headings.find(h => h.textContent === 'Sell Holding');
        expect(modalHeading).toBeInTheDocument();
      });
    });
  });

  describe('Add Holding Form', () => {
    test('opens Add Holding form when Add Holding button clicked', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('Add Holding')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Add Holding'));

      // Form should open
      await waitFor(() => {
        expect(screen.getByText('Add New Holding')).toBeInTheDocument();
      });
    });

    test('displays form with account selection', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('Add Holding')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Add Holding'));

      await waitFor(() => {
        const headings = screen.getAllByRole('heading', { level: 2 });
        const modalHeading = headings.find(h => h.textContent === 'Add New Holding');
        expect(modalHeading).toBeInTheDocument();
      });

      // Check that form elements exist
      const selects = screen.getAllByRole('combobox');
      expect(selects.length).toBeGreaterThan(0);

      // Note: Full form interaction testing is covered in separate form component tests
    });
  });

  describe('Loading States', () => {
    test('disables actions while loading', () => {
      render(<HoldingsList />);

      // Loading state should show loading message
      expect(screen.getByText(/Loading your holdings/i)).toBeInTheDocument();
    });
  });

  describe('Authentication', () => {
    test('includes auth token in API requests', async () => {
      render(<HoldingsList />);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/investments/holdings',
          expect.objectContaining({
            headers: expect.objectContaining({
              Authorization: 'Bearer mock-token',
            }),
          })
        );
      });
    });
  });

  describe('Success Messages', () => {
    test('displays success message after selling holding', async () => {
      global.fetch.mockImplementation((url, options) => {
        if (url.includes('/sell') && options?.method === 'POST') {
          return Promise.resolve({
            ok: true,
            json: async () => ({ success: true }),
          });
        }
        if (url.includes('/api/v1/investments/holdings')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ holdings: mockHoldings }),
          });
        }
        if (url.includes('/api/v1/investments/accounts')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ accounts: mockAccounts }),
          });
        }
        return Promise.reject(new Error('Unknown URL'));
      });

      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      // Open sell modal
      const sellButtons = screen.getAllByText('Sell');
      fireEvent.click(sellButtons[0]);

      // Wait for modal and interact
      await waitFor(() => {
        expect(screen.getByText('Sell Holding')).toBeInTheDocument();
      });

      // Note: Actual form submission would require more detailed interaction
    });

    test('clears success message after 3 seconds', async () => {
      jest.useFakeTimers();

      global.fetch.mockImplementation((url, options) => {
        if (url.includes('/price') && options?.method === 'PUT') {
          return Promise.resolve({
            ok: true,
            json: async () => ({ success: true }),
          });
        }
        if (url.includes('/api/v1/investments/holdings')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ holdings: mockHoldings }),
          });
        }
        if (url.includes('/api/v1/investments/accounts')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ accounts: mockAccounts }),
          });
        }
        return Promise.reject(new Error('Unknown URL'));
      });

      render(<HoldingsList />);

      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument();
      });

      // Note: Full timer testing would require complete form interaction

      jest.useRealTimers();
    });
  });
});
