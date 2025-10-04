import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AssetAllocation } from '../../../src/components/investment/AssetAllocation';
import { authStorage } from '../../../src/utils/auth';

// Mock authStorage
jest.mock('../../../src/utils/auth', () => ({
  authStorage: {
    getAccessToken: jest.fn(),
    clear: jest.fn(),
  },
}));

// Mock window.location
delete window.location;
window.location = { href: '' };

describe('AssetAllocation', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    authStorage.getAccessToken.mockReturnValue('mock-token');
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  const mockAssetClassData = {
    totalValue: 125000,
    allocations: [
      {
        category: 'EQUITY',
        value: 75000,
        percentage: 60,
        holdingsCount: 8,
      },
      {
        category: 'FIXED_INCOME',
        value: 25000,
        percentage: 20,
        holdingsCount: 3,
      },
      {
        category: 'CASH',
        value: 15000,
        percentage: 12,
        holdingsCount: 2,
      },
      {
        category: 'PROPERTY',
        value: 10000,
        percentage: 8,
        holdingsCount: 1,
      },
    ],
  };

  const mockRegionData = {
    totalValue: 125000,
    allocations: [
      {
        category: 'UK',
        value: 50000,
        percentage: 40,
        holdingsCount: 5,
      },
      {
        category: 'US',
        value: 40000,
        percentage: 32,
        holdingsCount: 4,
      },
      {
        category: 'EUROPE',
        value: 20000,
        percentage: 16,
        holdingsCount: 3,
      },
      {
        category: 'ASIA_PACIFIC',
        value: 15000,
        percentage: 12,
        holdingsCount: 2,
      },
    ],
  };

  const mockSectorData = {
    totalValue: 125000,
    allocations: [
      {
        category: 'TECHNOLOGY',
        value: 35000,
        percentage: 28,
        holdingsCount: 4,
      },
      {
        category: 'HEALTHCARE',
        value: 30000,
        percentage: 24,
        holdingsCount: 3,
      },
      {
        category: 'FINANCIALS',
        value: 25000,
        percentage: 20,
        holdingsCount: 3,
      },
      {
        category: 'CONSUMER',
        value: 20000,
        percentage: 16,
        holdingsCount: 2,
      },
      {
        category: 'ENERGY',
        value: 15000,
        percentage: 12,
        holdingsCount: 2,
      },
    ],
  };

  describe('Loading State', () => {
    it('should display loading state initially', () => {
      global.fetch.mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(() => resolve({ ok: true, json: () => mockAssetClassData }), 100);
          })
      );

      render(<AssetAllocation />);

      expect(screen.getByText(/Loading allocation data/i)).toBeInTheDocument();
      expect(screen.getByText('⏳')).toBeInTheDocument();
    });
  });

  describe('Asset Class Tab', () => {
    it('should render asset class allocation by default', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockAssetClassData,
      });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getByText('Asset Allocation Analysis')).toBeInTheDocument();
      });

      // Check narrative text
      expect(
        screen.getByText(/Your portfolio is allocated across/i, { exact: false })
      ).toBeInTheDocument();
      expect(screen.getByText(/asset classes/i)).toBeInTheDocument();

      // Check allocation items (multiple instances in visual display and table)
      expect(screen.getAllByText('EQUITY').length).toBeGreaterThan(0);
      expect(screen.getAllByText('FIXED INCOME').length).toBeGreaterThan(0);
      expect(screen.getAllByText('CASH').length).toBeGreaterThan(0);
      expect(screen.getAllByText('PROPERTY').length).toBeGreaterThan(0);

      // Check percentages (using getAllByText since they appear in multiple places)
      expect(screen.getAllByText(/60\.0/).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/20\.0/).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/12\.0/).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/8\.0/).length).toBeGreaterThan(0);

      // Check table headers
      expect(screen.getByText('Category')).toBeInTheDocument();
      expect(screen.getByText('Value')).toBeInTheDocument();
      expect(screen.getByText('Percentage')).toBeInTheDocument();
      expect(screen.getByText('Holdings')).toBeInTheDocument();
    });

    it('should display correct API endpoint for asset class', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockAssetClassData,
      });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/investments/portfolio/allocation?by=asset_class',
          expect.objectContaining({
            headers: {
              Authorization: 'Bearer mock-token',
            },
          })
        );
      });
    });

    it('should show educational content when expanded', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockAssetClassData,
      });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getByText('Asset Allocation Analysis')).toBeInTheDocument();
      });

      // Wait for data to be fully rendered
      await waitFor(() => {
        expect(screen.getAllByText('EQUITY').length).toBeGreaterThan(0);
      });

      const expandButtonText = screen.getByText(/Tell me more about asset class allocation/i);
      expect(expandButtonText).toBeInTheDocument();

      // Find the parent button element
      const expandButton = expandButtonText.closest('button');
      fireEvent.click(expandButton);

      await waitFor(() => {
        expect(
          screen.getByText(/are broad categories of investments/i, { exact: false })
        ).toBeInTheDocument();
        expect(screen.getByText(/Equity:/i)).toBeInTheDocument();
        expect(screen.getByText(/Fixed Income:/i)).toBeInTheDocument();
      });
    });
  });

  describe('Tab Switching', () => {
    it('should switch to region tab and fetch region data', async () => {
      global.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockAssetClassData,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockRegionData,
        });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getAllByText('EQUITY').length).toBeGreaterThan(0);
      });

      const regionTab = screen.getByText('Region');
      fireEvent.click(regionTab);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/investments/portfolio/allocation?by=region',
          expect.objectContaining({
            headers: {
              Authorization: 'Bearer mock-token',
            },
          })
        );
      });

      await waitFor(() => {
        expect(screen.getAllByText('UK').length).toBeGreaterThan(0);
        expect(screen.getAllByText('US').length).toBeGreaterThan(0);
        expect(screen.getAllByText('EUROPE').length).toBeGreaterThan(0);
        expect(screen.getAllByText('ASIA PACIFIC').length).toBeGreaterThan(0);
      });

      // Check narrative text changes
      expect(screen.getByText(/geographic regions/i, { exact: false })).toBeInTheDocument();
    });

    it('should switch to sector tab and fetch sector data', async () => {
      global.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockAssetClassData,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockSectorData,
        });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getAllByText('EQUITY').length).toBeGreaterThan(0);
      });

      const sectorTab = screen.getByText('Sector');
      fireEvent.click(sectorTab);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/investments/portfolio/allocation?by=sector',
          expect.objectContaining({
            headers: {
              Authorization: 'Bearer mock-token',
            },
          })
        );
      });

      await waitFor(() => {
        expect(screen.getAllByText('TECHNOLOGY').length).toBeGreaterThan(0);
        expect(screen.getAllByText('HEALTHCARE').length).toBeGreaterThan(0);
        expect(screen.getAllByText('FINANCIALS').length).toBeGreaterThan(0);
        expect(screen.getAllByText('CONSUMER').length).toBeGreaterThan(0);
        expect(screen.getAllByText('ENERGY').length).toBeGreaterThan(0);
      });

      // Check narrative text changes
      expect(screen.getByText(/industry sectors/i, { exact: false })).toBeInTheDocument();
    });

    it('should show loading state when switching tabs', async () => {
      global.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockAssetClassData,
        })
        .mockImplementation(
          () =>
            new Promise((resolve) => {
              setTimeout(() => resolve({ ok: true, json: () => mockRegionData }), 100);
            })
        );

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getAllByText('EQUITY').length).toBeGreaterThan(0);
      });

      const regionTab = screen.getByText('Region');
      fireEvent.click(regionTab);

      // Should show loading state
      expect(screen.getByText(/Loading allocation data/i)).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should display error message on fetch failure', async () => {
      global.fetch.mockRejectedValue(new Error('Network error'));

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getByText('Error Loading Allocation')).toBeInTheDocument();
        expect(
          screen.getByText(/Failed to load allocation data. Please try again./i)
        ).toBeInTheDocument();
      });

      // Check Try Again button exists
      expect(screen.getByText('Try Again')).toBeInTheDocument();
    });

    it('should retry fetch when Try Again button is clicked', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error')).mockResolvedValueOnce({
        ok: true,
        json: async () => mockAssetClassData,
      });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getByText('Error Loading Allocation')).toBeInTheDocument();
      });

      const retryButton = screen.getByText('Try Again');
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getByText('Asset Allocation Analysis')).toBeInTheDocument();
        expect(screen.getAllByText('EQUITY').length).toBeGreaterThan(0);
      });
    });

    it('should handle 401 unauthorized and redirect to login', async () => {
      global.fetch.mockResolvedValue({
        ok: false,
        status: 401,
      });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(authStorage.clear).toHaveBeenCalled();
        expect(window.location.href).toBe('/login');
      });
    });

    it('should handle 404 not found as empty data', async () => {
      global.fetch.mockResolvedValue({
        ok: false,
        status: 404,
      });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(
          screen.getByText(/You haven't added any investments yet/i)
        ).toBeInTheDocument();
      });
    });

    it('should handle 500 server error', async () => {
      global.fetch.mockResolvedValue({
        ok: false,
        status: 500,
      });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getByText('Error Loading Allocation')).toBeInTheDocument();
      });
    });
  });

  describe('Empty State', () => {
    it('should display empty state when no allocations exist', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          totalValue: 0,
          allocations: [],
        }),
      });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(
          screen.getByText(/You haven't added any investments yet/i)
        ).toBeInTheDocument();
      });

      // Check educational callout
      expect(screen.getByText(/Why is asset allocation important?/i)).toBeInTheDocument();
      expect(
        screen.getByText(/Asset allocation is one of the most important factors/i, {
          exact: false,
        })
      ).toBeInTheDocument();

      // Check CTA button
      expect(screen.getByText(/Add Your First Investment/i)).toBeInTheDocument();
    });

    it('should display empty state when allocations is null', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          totalValue: 0,
          allocations: null,
        }),
      });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(
          screen.getByText(/You haven't added any investments yet/i)
        ).toBeInTheDocument();
      });
    });
  });

  describe('Data Visualization', () => {
    it('should display progress bars for each allocation', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockAssetClassData,
      });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getAllByText('EQUITY').length).toBeGreaterThan(0);
      });

      // Check that allocation items are rendered
      const equityItems = screen.getAllByText('EQUITY');
      expect(equityItems.length).toBeGreaterThan(0);

      // Check percentages are displayed (multiple instances)
      expect(screen.getAllByText(/60\.0/).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/20\.0/).length).toBeGreaterThan(0);
    });

    it('should display table with all allocations and totals', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockAssetClassData,
      });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getByText('Asset Allocation Analysis')).toBeInTheDocument();
      });

      // Check table exists
      expect(screen.getByText('Category')).toBeInTheDocument();

      // Check total row
      const totalTexts = screen.getAllByText('Total');
      expect(totalTexts.length).toBeGreaterThan(0);

      // Check 100% total (using regex to handle split text nodes)
      const percentages = screen.getAllByText(/100\.0/);
      expect(percentages.length).toBeGreaterThan(0);
    });

    it('should display holdings count when available', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockAssetClassData,
      });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getByText('Asset Allocation Analysis')).toBeInTheDocument();
      });

      // Check Holdings column header
      expect(screen.getByText('Holdings')).toBeInTheDocument();

      // Check holdings counts are displayed
      const holdingsCounts = screen.getAllByText('8');
      expect(holdingsCounts.length).toBeGreaterThan(0);
    });
  });

  describe('Color Coding', () => {
    it('should apply consistent colors to asset classes', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockAssetClassData,
      });

      const { container } = render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getAllByText('EQUITY').length).toBeGreaterThan(0);
      });

      // Check color indicators exist (by checking for elements with specific styles)
      const colorIndicators = container.querySelectorAll('[style*="background-color"]');
      expect(colorIndicators.length).toBeGreaterThan(0);
    });
  });

  describe('Accessibility', () => {
    it('should have proper aria-expanded attribute on expandable section', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockAssetClassData,
      });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getByText('Asset Allocation Analysis')).toBeInTheDocument();
      });

      // Wait for data to be fully rendered
      await waitFor(() => {
        expect(screen.getAllByText('EQUITY').length).toBeGreaterThan(0);
      });

      const expandButtonText = screen.getByText(/Tell me more about asset class allocation/i);
      // Find the parent button element which has aria-expanded
      const expandButton = expandButtonText.closest('button');
      expect(expandButton).toHaveAttribute('aria-expanded', 'false');

      fireEvent.click(expandButton);

      await waitFor(() => {
        expect(expandButton).toHaveAttribute('aria-expanded', 'true');
      });
    });

    it('should have semantic table structure', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockAssetClassData,
      });

      const { container } = render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getByText('Asset Allocation Analysis')).toBeInTheDocument();
      });

      // Check table structure
      const table = container.querySelector('table');
      expect(table).toBeInTheDocument();

      const thead = container.querySelector('thead');
      expect(thead).toBeInTheDocument();

      const tbody = container.querySelector('tbody');
      expect(tbody).toBeInTheDocument();
    });
  });

  describe('Currency Formatting', () => {
    it('should format currency values correctly', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => mockAssetClassData,
      });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getByText('Asset Allocation Analysis')).toBeInTheDocument();
      });

      // Check full format in table
      expect(screen.getByText('£75,000')).toBeInTheDocument();
      expect(screen.getByText('£25,000')).toBeInTheDocument();
      expect(screen.getByText('£15,000')).toBeInTheDocument();

      // Check short format in visual display
      expect(screen.getByText('£75k')).toBeInTheDocument();
      expect(screen.getByText('£25k')).toBeInTheDocument();
    });

    it('should format large values with m suffix', async () => {
      const largeValueData = {
        totalValue: 2500000,
        allocations: [
          {
            category: 'EQUITY',
            value: 2000000,
            percentage: 80,
            holdingsCount: 10,
          },
        ],
      };

      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => largeValueData,
      });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getByText('£2.0m')).toBeInTheDocument();
      });
    });
  });

  describe('Educational Content', () => {
    it('should show region-specific educational content', async () => {
      global.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockAssetClassData,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockRegionData,
        });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getAllByText('EQUITY').length).toBeGreaterThan(0);
      });

      // Switch to region tab
      fireEvent.click(screen.getByText('Region'));

      await waitFor(() => {
        expect(screen.getAllByText('UK').length).toBeGreaterThan(0);
      });

      // Expand educational content
      const expandButtonText = screen.getByText(/Tell me more about region allocation/i);
      const expandButton = expandButtonText.closest('button');
      fireEvent.click(expandButton);

      await waitFor(() => {
        expect(
          screen.getByText(/means spreading your investments across different regions/i, { exact: false })
        ).toBeInTheDocument();
        expect(screen.getByText(/home bias/i, { exact: false })).toBeInTheDocument();
      });
    });

    it('should show sector-specific educational content', async () => {
      global.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockAssetClassData,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockSectorData,
        });

      render(<AssetAllocation />);

      await waitFor(() => {
        expect(screen.getAllByText('EQUITY').length).toBeGreaterThan(0);
      });

      // Switch to sector tab
      fireEvent.click(screen.getByText('Sector'));

      await waitFor(() => {
        expect(screen.getAllByText('TECHNOLOGY').length).toBeGreaterThan(0);
      });

      // Expand educational content
      const expandButtonText = screen.getByText(/Tell me more about sector allocation/i);
      const expandButton = expandButtonText.closest('button');
      fireEvent.click(expandButton);

      await waitFor(() => {
        expect(
          screen.getByText(/shows how your investments are distributed/i, { exact: false })
        ).toBeInTheDocument();
        expect(screen.getByText(/Avoid overconcentration/i, { exact: false })).toBeInTheDocument();
      });
    });
  });
});
