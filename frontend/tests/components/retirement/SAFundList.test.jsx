import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SAFundList } from '../../../src/components/retirement/SAFundList';
import { authStorage } from '../../../src/utils/auth';

// Mock auth storage
jest.mock('../../../src/utils/auth', () => ({
  authStorage: {
    getAccessToken: jest.fn(() => 'mock-token'),
    clear: jest.fn(),
  },
}));

// Mock fetch
global.fetch = jest.fn();

describe('SAFundList', () => {
  const mockFunds = [
    {
      id: '1',
      fundType: 'PENSION_FUND',
      provider: 'Old Mutual',
      fundName: 'Balanced Fund',
      employerName: 'Test Corp',
      currentValue: 850000,
      monthlyContribution: 5000,
      employerContribution: 3000,
      retirementAge: 65,
      projectedValue: 2500000,
      startDate: '2020-01-01',
      regulation28Compliant: true,
      maxLumpSum: 283333,
      portfolioName: 'Balanced Portfolio',
      assetAllocation: {
        equityPercentage: 60,
        bondsPercentage: 25,
        cashPercentage: 10,
        propertyPercentage: 5,
        offshorePercentage: 20,
      },
    },
  ];

  const mockTotalSavings = {
    totalValue: 850000,
    projectedValue: 2500000,
    annualContributions: 96000,
    retirementAge: 65,
  };

  const mockSection10C = {
    taxYear: '2024/2025',
    totalContributions: 96000,
    maxDeductible: 350000,
    deductionClaimed: 96000,
    taxSaving: 38400,
    remainingAllowance: 254000,
    remuneration: 500000,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();
  });

  it('should render loading state initially', () => {
    global.fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<SAFundList onAddFund={jest.fn()} onEditFund={jest.fn()} />);

    expect(screen.getByText(/Loading your SA retirement funds/i)).toBeInTheDocument();
  });

  it('should render empty state when no funds', async () => {
    global.fetch
      .mockResolvedValueOnce({ ok: true, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, json: async () => null })
      .mockResolvedValueOnce({ ok: true, json: async () => null });

    render(<SAFundList onAddFund={jest.fn()} onEditFund={jest.fn()} />);

    await waitFor(() => {
      expect(screen.getByText(/Start tracking your South African retirement funds/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Why track your SA retirement funds/i)).toBeInTheDocument();
  });

  it('should render funds list with hero section', async () => {
    global.fetch
      .mockResolvedValueOnce({ ok: true, json: async () => mockFunds })
      .mockResolvedValueOnce({ ok: true, json: async () => mockTotalSavings })
      .mockResolvedValueOnce({ ok: true, json: async () => mockSection10C });

    render(<SAFundList onAddFund={jest.fn()} onEditFund={jest.fn()} />);

    await waitFor(() => {
      expect(screen.getByText(/Your South African retirement savings:/i)).toBeInTheDocument();
    });

    // Check hero section displays total value
    expect(screen.getByText(/R850,000/i)).toBeInTheDocument();

    // Check narrative text
    expect(screen.getByText(/You have/i)).toBeInTheDocument();
    expect(screen.getByText(/1/i)).toBeInTheDocument();
    expect(screen.getByText(/fund building your retirement nest egg/i)).toBeInTheDocument();
  });

  it('should render Section 10C deduction status', async () => {
    global.fetch
      .mockResolvedValueOnce({ ok: true, json: async () => mockFunds })
      .mockResolvedValueOnce({ ok: true, json: async () => mockTotalSavings })
      .mockResolvedValueOnce({ ok: true, json: async () => mockSection10C });

    render(<SAFundList onAddFund={jest.fn()} onEditFund={jest.fn()} />);

    await waitFor(() => {
      expect(screen.getByText(/Section 10C tax deduction status/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/R96,000/i)).toBeInTheDocument();
    expect(screen.getByText(/R254,000/i)).toBeInTheDocument();
  });

  it('should render fund cards with narrative descriptions', async () => {
    global.fetch
      .mockResolvedValueOnce({ ok: true, json: async () => mockFunds })
      .mockResolvedValueOnce({ ok: true, json: async () => mockTotalSavings })
      .mockResolvedValueOnce({ ok: true, json: async () => mockSection10C });

    render(<SAFundList onAddFund={jest.fn()} onEditFund={jest.fn()} />);

    await waitFor(() => {
      expect(screen.getByText(/Old Mutual Pension Fund/i)).toBeInTheDocument();
    });

    // Check narrative description
    expect(screen.getByText(/This fund is currently worth/i)).toBeInTheDocument();
    expect(screen.getByText(/You contribute/i)).toBeInTheDocument();
    expect(screen.getByText(/R5,000/i)).toBeInTheDocument();
  });

  it('should show Regulation 28 warning for non-compliant funds', async () => {
    const nonCompliantFunds = [
      {
        ...mockFunds[0],
        regulation28Compliant: false,
      },
    ];

    global.fetch
      .mockResolvedValueOnce({ ok: true, json: async () => nonCompliantFunds })
      .mockResolvedValueOnce({ ok: true, json: async () => mockTotalSavings })
      .mockResolvedValueOnce({ ok: true, json: async () => mockSection10C });

    render(<SAFundList onAddFund={jest.fn()} onEditFund={jest.fn()} />);

    await waitFor(() => {
      expect(screen.getByText(/Regulation 28 compliance alert/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/⚠️ Regulation 28 violation/i)).toBeInTheDocument();
  });

  it('should expand fund details when "Tell me more" is clicked', async () => {
    global.fetch
      .mockResolvedValueOnce({ ok: true, json: async () => mockFunds })
      .mockResolvedValueOnce({ ok: true, json: async () => mockTotalSavings })
      .mockResolvedValueOnce({ ok: true, json: async () => mockSection10C });

    render(<SAFundList onAddFund={jest.fn()} onEditFund={jest.fn()} />);

    await waitFor(() => {
      expect(screen.getByText(/Tell me more about this fund/i)).toBeInTheDocument();
    });

    // Click expand button
    fireEvent.click(screen.getByText(/Tell me more about this fund/i));

    await waitFor(() => {
      expect(screen.getByText(/Started:/i)).toBeInTheDocument();
      expect(screen.getByText(/Investment portfolio:/i)).toBeInTheDocument();
      expect(screen.getByText(/Asset allocation:/i)).toBeInTheDocument();
    });
  });

  it('should call onAddFund when add fund button is clicked', async () => {
    const mockOnAddFund = jest.fn();

    global.fetch
      .mockResolvedValueOnce({ ok: true, json: async () => mockFunds })
      .mockResolvedValueOnce({ ok: true, json: async () => mockTotalSavings })
      .mockResolvedValueOnce({ ok: true, json: async () => mockSection10C });

    render(<SAFundList onAddFund={mockOnAddFund} onEditFund={jest.fn()} />);

    await waitFor(() => {
      expect(screen.getByText(/Add another SA retirement fund/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/Add another SA retirement fund/i));

    expect(mockOnAddFund).toHaveBeenCalledTimes(1);
  });

  it('should call onEditFund when edit button is clicked', async () => {
    const mockOnEditFund = jest.fn();

    global.fetch
      .mockResolvedValueOnce({ ok: true, json: async () => mockFunds })
      .mockResolvedValueOnce({ ok: true, json: async () => mockTotalSavings })
      .mockResolvedValueOnce({ ok: true, json: async () => mockSection10C });

    render(<SAFundList onAddFund={jest.fn()} onEditFund={mockOnEditFund} />);

    await waitFor(() => {
      expect(screen.getAllByText(/Edit/i)[0]).toBeInTheDocument();
    });

    fireEvent.click(screen.getAllByText(/Edit/i)[0]);

    expect(mockOnEditFund).toHaveBeenCalledWith('1');
  });

  it('should handle delete fund with confirmation', async () => {
    global.confirm = jest.fn(() => true);

    global.fetch
      .mockResolvedValueOnce({ ok: true, json: async () => mockFunds })
      .mockResolvedValueOnce({ ok: true, json: async () => mockTotalSavings })
      .mockResolvedValueOnce({ ok: true, json: async () => mockSection10C })
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) }) // DELETE
      .mockResolvedValueOnce({ ok: true, json: async () => [] }) // Reload funds
      .mockResolvedValueOnce({ ok: true, json: async () => null }) // Reload total
      .mockResolvedValueOnce({ ok: true, json: async () => null }); // Reload section 10C

    render(<SAFundList onAddFund={jest.fn()} onEditFund={jest.fn()} />);

    await waitFor(() => {
      expect(screen.getAllByText(/Delete/i)[0]).toBeInTheDocument();
    });

    fireEvent.click(screen.getAllByText(/Delete/i)[0]);

    expect(global.confirm).toHaveBeenCalledWith('Are you sure you want to delete this retirement fund?');

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/retirement/sa-funds/1',
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });
  });

  it('should handle API error gracefully', async () => {
    global.fetch.mockRejectedValue(new Error('API Error'));

    render(<SAFundList onAddFund={jest.fn()} onEditFund={jest.fn()} />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to load SA retirement funds/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Try Again/i)).toBeInTheDocument();
  });

  it('should handle unauthorized (401) by redirecting to login', async () => {
    global.fetch.mockResolvedValueOnce({ ok: false, status: 401 });

    delete window.location;
    window.location = { href: '' };

    render(<SAFundList onAddFund={jest.fn()} onEditFund={jest.fn()} />);

    await waitFor(() => {
      expect(authStorage.clear).toHaveBeenCalled();
      expect(window.location.href).toBe('/login');
    });
  });
});
