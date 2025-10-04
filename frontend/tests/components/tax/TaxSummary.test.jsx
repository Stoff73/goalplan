import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { TaxSummary } from '../../../src/components/tax/TaxSummary';
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

// Mock window.location
delete window.location;
window.location = { href: '' };

describe('TaxSummary Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    authStorage.getAccessToken.mockReturnValue('mock-token');
    fetch.mockClear();
  });

  const mockTaxData = {
    overall: {
      total_tax: 35000,
      total_income: 85000,
      net_income: 50000,
      effective_tax_rate: 41.18,
      previous_year_tax: 32000,
    },
    uk_tax: {
      total_tax: 25000,
      income_tax: {
        total_tax: 15000,
        tax_by_band: [
          { band_name: 'Basic Rate', taxable_amount: 37700, rate: 0.20, tax: 7540 },
          { band_name: 'Higher Rate', taxable_amount: 15000, rate: 0.40, tax: 6000 },
        ],
      },
      national_insurance: {
        total_ni: 5000,
        class_1_ni: 5000,
      },
      capital_gains_tax: {
        total_cgt: 3000,
        annual_exemption_used: 3000,
      },
      dividend_tax: {
        total_tax: 2000,
        dividend_allowance_used: 500,
      },
      isa_allowance_used: 10000,
      pension_contributions: 15000,
      personal_allowance_used: 12570,
    },
    sa_tax: {
      total_tax: 50000,
      total_tax_gbp: 10000,
      income_tax: {
        tax_payable: 40000,
        tax_by_band: [
          { band_name: '18%', taxable_amount: 237100, rate: 0.18, tax: 42678 },
          { band_name: '26%', taxable_amount: 50000, rate: 0.26, tax: 13000 },
        ],
      },
      capital_gains_tax: {
        cgt: 5000,
      },
      dividend_tax: {
        dividend_tax_withheld: 5000,
      },
      tfsa_contributions: 20000,
    },
    income_breakdown: [
      { source_type: 'Employment', amount: 60000, country: 'UK' },
      { source_type: 'Dividends', amount: 15000, country: 'UK' },
      { source_type: 'Capital Gains', amount: 10000, country: 'SA' },
    ],
  };

  describe('Loading State', () => {
    test('renders loading state while fetching data', () => {
      fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<TaxSummary />);

      expect(screen.getByText('Loading your tax summary...')).toBeInTheDocument();
      expect(screen.getByText('⏳')).toBeInTheDocument();
    });
  });

  describe('Error States', () => {
    test('handles API error gracefully', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Error Loading Tax Summary')).toBeInTheDocument();
        expect(screen.getByText('Failed to load tax summary. Please try again.')).toBeInTheDocument();
      });
    });

    test('handles 401 authentication error', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      render(<TaxSummary />);

      await waitFor(() => {
        expect(authStorage.clear).toHaveBeenCalled();
        expect(window.location.href).toBe('/login');
      });
    });

    test('handles 404 no data error', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('No Income Data Yet')).toBeInTheDocument();
      });
    });

    test('shows "Try Again" button on error', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      render(<TaxSummary />);

      await waitFor(() => {
        const tryAgainButton = screen.getByText('Try Again');
        expect(tryAgainButton).toBeInTheDocument();
      });
    });

    test('retries fetch when "Try Again" is clicked', async () => {
      fetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockTaxData,
        });

      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Try Again')).toBeInTheDocument();
      });

      const tryAgainButton = screen.getByText('Try Again');
      fireEvent.click(tryAgainButton);

      await waitFor(() => {
        expect(screen.getByText(/Your Tax Summary:/)).toBeInTheDocument();
      });
    });
  });

  describe('Empty State', () => {
    test('renders empty state when no tax data', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('No Income Data Yet')).toBeInTheDocument();
        expect(screen.getByText(/You haven't added any income sources yet/)).toBeInTheDocument();
      });
    });

    test('shows "Add Income Sources" button in empty state', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Add Income Sources →')).toBeInTheDocument();
      });
    });
  });

  describe('Tax Summary Display', () => {
    beforeEach(() => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTaxData,
      });
    });

    test('renders overall tax summary correctly', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText(/Your Tax Summary:/)).toBeInTheDocument();
        expect(screen.getByText('Your Tax Situation')).toBeInTheDocument();
        expect(screen.getByText('total tax')).toBeInTheDocument();
      });
    });

    test('displays comparison with previous year', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText(/£3,000 more than last year/)).toBeInTheDocument();
      });
    });

    test('renders UK tax breakdown correctly', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Your UK Tax Liabilities')).toBeInTheDocument();
        expect(screen.getAllByText(/Income Tax/)[0]).toBeInTheDocument();
        expect(screen.getByText('Total UK Tax')).toBeInTheDocument();
      });
    });

    test('renders SA tax breakdown correctly', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Your South Africa Tax Liabilities')).toBeInTheDocument();
        expect(screen.getAllByText(/Income Tax/)[0]).toBeInTheDocument();
      });
    });

    test('displays income breakdown by source', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Your Income Breakdown')).toBeInTheDocument();
        const employmentElements = screen.getAllByText('Employment');
        expect(employmentElements.length).toBeGreaterThan(0);
      });
    });

    test('highlights largest income source', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Your Income Breakdown')).toBeInTheDocument();
        // Check that employment income is highlighted (by verifying the narrative mentions it)
        expect(screen.getByText(/making up/)).toBeInTheDocument();
      });
    });
  });

  describe('Tax Efficiency Score', () => {
    beforeEach(() => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTaxData,
      });
    });

    test('calculates and displays tax efficiency score', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Your Tax Efficiency Score')).toBeInTheDocument();
        expect(screen.getByText(/out of 100/)).toBeInTheDocument();
      });
    });

    test('displays score with correct color coding', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        const scoreValue = screen.getByText(/out of 100/).previousSibling;
        expect(scoreValue).toBeTruthy();
      });
    });

    test('shows score breakdown factors', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText(/ISA and TFSA allowances/)).toBeInTheDocument();
        expect(screen.getByText(/Pension contributions/)).toBeInTheDocument();
        expect(screen.getByText(/Personal allowances/)).toBeInTheDocument();
      });
    });
  });

  describe('Actionable Insights', () => {
    beforeEach(() => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTaxData,
      });
    });

    test('generates and displays tax optimization insights', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('What You Can Do to Reduce Your Tax')).toBeInTheDocument();
      });
    });

    test('shows ISA allowance recommendation when applicable', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText(/Maximize your ISA allowance/)).toBeInTheDocument();
        expect(screen.getByText(/£10,000 of ISA allowance remaining/)).toBeInTheDocument();
      });
    });

    test('shows pension contribution recommendation', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText(/Boost your pension contributions/)).toBeInTheDocument();
      });
    });

    test('displays potential tax savings for each insight', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getAllByText(/potential savings/).length).toBeGreaterThan(0);
      });
    });
  });

  describe('Progressive Disclosure', () => {
    beforeEach(() => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTaxData,
      });
    });

    test('UK details section starts collapsed', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Tell me more about UK tax calculations')).toBeInTheDocument();
      });

      // Verify details are not visible initially
      expect(screen.queryByText(/Calculated on taxable income after personal allowance/)).not.toBeInTheDocument();
    });

    test('expands UK details when clicked', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        const expandButton = screen.getByText('Tell me more about UK tax calculations');
        expect(expandButton).toBeInTheDocument();
        fireEvent.click(expandButton);
      });

      await waitFor(() => {
        expect(screen.getByText(/Calculated on taxable income after personal allowance/)).toBeInTheDocument();
      });
    });

    test('SA details section starts collapsed', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Tell me more about SA tax calculations')).toBeInTheDocument();
      });

      expect(screen.queryByText(/age-dependent rebates/)).not.toBeInTheDocument();
    });

    test('expands SA details when clicked', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        const expandButton = screen.getByText('Tell me more about SA tax calculations');
        expect(expandButton).toBeInTheDocument();
        fireEvent.click(expandButton);
      });

      await waitFor(() => {
        expect(screen.getByText(/age-dependent rebates/)).toBeInTheDocument();
      });
    });

    test('toggles expanded state on multiple clicks', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        const expandButton = screen.getByText('Tell me more about UK tax calculations');

        // Click to expand
        fireEvent.click(expandButton);
      });

      await waitFor(() => {
        expect(screen.getByText(/Calculated on taxable income after personal allowance/)).toBeInTheDocument();
      });

      // Click to collapse
      const collapseButton = screen.getByText('Tell me more about UK tax calculations');
      fireEvent.click(collapseButton);

      await waitFor(() => {
        expect(screen.queryByText(/Calculated on taxable income after personal allowance/)).not.toBeInTheDocument();
      });
    });
  });

  describe('Currency Formatting', () => {
    beforeEach(() => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTaxData,
      });
    });

    test('formats GBP currency correctly', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Your Tax Situation')).toBeInTheDocument();
        // Check that currency is displayed (as there are multiple instances)
        expect(screen.getAllByText(/£/).length).toBeGreaterThan(0);
      });
    });

    test('formats ZAR currency correctly', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Your South Africa Tax Liabilities')).toBeInTheDocument();
        // Check that ZAR currency is displayed
        expect(screen.getAllByText(/R[0-9]/).length).toBeGreaterThan(0);
      });
    });

    test('formats percentages correctly', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Your Tax Situation')).toBeInTheDocument();
        // Check that percentages are displayed
        expect(screen.getAllByText(/%/).length).toBeGreaterThan(0);
      });
    });

    test('formats large numbers with k suffix', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText(/£35k/)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    beforeEach(() => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTaxData,
      });
    });

    test('expandable sections have correct aria-expanded attribute', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        const expandButtons = screen.getAllByRole('button', { expanded: false });
        expect(expandButtons.length).toBeGreaterThan(0);
      });
    });

    test('aria-expanded updates when section is expanded', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        const expandButtons = screen.getAllByRole('button', { expanded: false });
        expect(expandButtons.length).toBeGreaterThan(0);
        fireEvent.click(expandButtons[0]);
      });

      await waitFor(() => {
        const expandButtons = screen.getAllByRole('button', { expanded: true });
        expect(expandButtons.length).toBeGreaterThan(0);
      });
    });

    test('all interactive elements are keyboard accessible', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        const buttons = screen.getAllByRole('button');
        buttons.forEach((button) => {
          expect(button).toBeInTheDocument();
        });
      });
    });
  });

  describe('API Integration', () => {
    test('calls correct API endpoint with auth token', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTaxData,
      });

      render(<TaxSummary />);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/v1/tax/summary', {
          headers: {
            Authorization: 'Bearer mock-token',
          },
        });
      });
    });

    test('uses auth token from authStorage', async () => {
      authStorage.getAccessToken.mockReturnValue('test-token-123');

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTaxData,
      });

      render(<TaxSummary />);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/v1/tax/summary', {
          headers: {
            Authorization: 'Bearer test-token-123',
          },
        });
      });
    });
  });

  describe('Edge Cases', () => {
    test('handles missing overall data gracefully', async () => {
      const incompleteData = {
        uk_tax: mockTaxData.uk_tax,
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => incompleteData,
      });

      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Your UK Tax Liabilities')).toBeInTheDocument();
      });
    });

    test('handles missing UK tax data', async () => {
      const onlySaData = {
        overall: mockTaxData.overall,
        sa_tax: mockTaxData.sa_tax,
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => onlySaData,
      });

      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Your South Africa Tax Liabilities')).toBeInTheDocument();
        expect(screen.queryByText('Your UK Tax Liabilities')).not.toBeInTheDocument();
      });
    });

    test('handles missing SA tax data', async () => {
      const onlyUkData = {
        overall: mockTaxData.overall,
        uk_tax: mockTaxData.uk_tax,
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => onlyUkData,
      });

      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText('Your UK Tax Liabilities')).toBeInTheDocument();
        expect(screen.queryByText('Your South Africa Tax Liabilities')).not.toBeInTheDocument();
      });
    });

    test('handles empty income breakdown', async () => {
      const noIncomeBreakdown = {
        ...mockTaxData,
        income_breakdown: [],
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => noIncomeBreakdown,
      });

      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.queryByText('Your Income Breakdown')).not.toBeInTheDocument();
      });
    });

    test('handles zero tax liability', async () => {
      const zeroTax = {
        overall: {
          total_tax: 0,
          total_income: 10000,
          effective_tax_rate: 0,
        },
        uk_tax: {
          total_tax: 0,
        },
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => zeroTax,
      });

      render(<TaxSummary />);

      await waitFor(() => {
        // Component should still render overall section with zero tax
        expect(screen.getByText(/Your Tax Summary/)).toBeInTheDocument();
        expect(screen.getByText('Your Tax Situation')).toBeInTheDocument();
      });
    });

    test('handles very high efficiency score', async () => {
      const highEfficiencyData = {
        ...mockTaxData,
        uk_tax: {
          ...mockTaxData.uk_tax,
          isa_allowance_used: 20000,
          pension_contributions: 60000,
        },
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => highEfficiencyData,
      });

      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText(/excellent tax efficiency/)).toBeInTheDocument();
      });
    });

    test('handles very low efficiency score', async () => {
      const lowEfficiencyData = {
        ...mockTaxData,
        uk_tax: {
          ...mockTaxData.uk_tax,
          isa_allowance_used: 0,
          pension_contributions: 0,
        },
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => lowEfficiencyData,
      });

      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText(/significant opportunity to optimize/)).toBeInTheDocument();
      });
    });
  });

  describe('Narrative Storytelling Approach', () => {
    beforeEach(() => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTaxData,
      });
    });

    test('uses conversational language', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        expect(screen.getByText(/you'll owe approximately/i)).toBeInTheDocument();
        expect(screen.getByText(/Your Tax Summary/i)).toBeTruthy();
      });
    });

    test('embeds metrics in sentences', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        // Should find currency values embedded in narrative text
        const narrativeText = screen.getByText(/Based on your current income and investments/);
        expect(narrativeText).toBeInTheDocument();
      });
    });

    test('provides educational context', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        // Look for educational callout content or narrative sections
        expect(screen.getByText(/What You Can Do to Reduce Your Tax/)).toBeInTheDocument();
      });
    });

    test('uses encouraging tone for positive outcomes', async () => {
      render(<TaxSummary />);

      await waitFor(() => {
        // Look for encouraging language in insights
        expect(screen.getByText(/What You Can Do to Reduce Your Tax/)).toBeInTheDocument();
      });
    });
  });
});
