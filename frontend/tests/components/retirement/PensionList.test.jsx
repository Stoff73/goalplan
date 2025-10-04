import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { PensionList } from '../../../src/components/retirement/PensionList';
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

describe('PensionList Component', () => {
  const mockPensions = [
    {
      id: '1',
      pensionType: 'OCCUPATIONAL_DC',
      provider: 'Aviva',
      employerName: 'ABC Company',
      currentValue: 50000,
      monthlyContribution: 500,
      employerContribution: 300,
      retirementAge: 67,
      projectedValue: 150000,
      startDate: '2020-01-01',
      investmentStrategy: 'BALANCED',
      assumedGrowthRate: 5,
      taxReliefMethod: 'NET_PAY',
      mpaaTriggered: false,
    },
    {
      id: '2',
      pensionType: 'SIPP',
      provider: 'Fidelity',
      currentValue: 75000,
      monthlyContribution: 800,
      employerContribution: 0,
      retirementAge: 65,
      projectedValue: 200000,
      startDate: '2018-06-15',
      investmentStrategy: 'AGGRESSIVE',
      assumedGrowthRate: 7,
      taxReliefMethod: 'RELIEF_AT_SOURCE',
      mpaaTriggered: false,
    },
  ];

  const mockTotalPot = {
    totalValue: 125000,
    projectedValue: 350000,
    annualContributions: 15600,
    retirementAge: 67,
  };

  const mockOnAddPension = jest.fn();
  const mockOnEditPension = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders loading state initially', () => {
    fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<PensionList onAddPension={mockOnAddPension} onEditPension={mockOnEditPension} />);

    expect(screen.getByText(/Loading your pensions/i)).toBeInTheDocument();
  });

  it('renders pension list with data', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/uk-pensions')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockPensions),
        });
      }
      if (url.includes('/total-pot')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTotalPot),
        });
      }
    });

    render(<PensionList onAddPension={mockOnAddPension} onEditPension={mockOnEditPension} />);

    await waitFor(() => {
      expect(screen.getByText(/Your retirement savings:/i)).toBeInTheDocument();
    });

    // Check total pot display
    expect(screen.getByText(/£125,000/)).toBeInTheDocument();
    expect(screen.getByText(/£350,000/)).toBeInTheDocument();

    // Check pension providers
    expect(screen.getByText(/Aviva Workplace Pension/i)).toBeInTheDocument();
    expect(screen.getByText(/Fidelity SIPP/i)).toBeInTheDocument();
  });

  it('shows MPAA badge when triggered', async () => {
    const pensionsWithMPAA = [
      { ...mockPensions[0], mpaaTriggered: true },
    ];

    fetch.mockImplementation((url) => {
      if (url.includes('/uk-pensions')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(pensionsWithMPAA),
        });
      }
      if (url.includes('/total-pot')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTotalPot),
        });
      }
    });

    render(<PensionList onAddPension={mockOnAddPension} onEditPension={mockOnEditPension} />);

    await waitFor(() => {
      expect(screen.getByText(/Money Purchase Annual Allowance applies/i)).toBeInTheDocument();
    });
  });

  it('shows progressive disclosure when "Tell me more" is clicked', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/uk-pensions')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockPensions),
        });
      }
      if (url.includes('/total-pot')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTotalPot),
        });
      }
    });

    render(<PensionList onAddPension={mockOnAddPension} onEditPension={mockOnEditPension} />);

    await waitFor(() => {
      expect(screen.getByText(/Aviva Workplace Pension/i)).toBeInTheDocument();
    });

    // Click "Tell me more"
    const tellMeMoreButtons = screen.getAllByText(/Tell me more about this pension/i);
    fireEvent.click(tellMeMoreButtons[0]);

    // Check details are shown
    await waitFor(() => {
      expect(screen.getByText(/Started:/i)).toBeInTheDocument();
      expect(screen.getByText(/Investment strategy:/i)).toBeInTheDocument();
    });
  });

  it('calls onEditPension when Edit button is clicked', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/uk-pensions')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockPensions),
        });
      }
      if (url.includes('/total-pot')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTotalPot),
        });
      }
    });

    render(<PensionList onAddPension={mockOnAddPension} onEditPension={mockOnEditPension} />);

    await waitFor(() => {
      expect(screen.getByText(/Aviva Workplace Pension/i)).toBeInTheDocument();
    });

    const editButtons = screen.getAllByText(/Edit/i);
    fireEvent.click(editButtons[0]);

    expect(mockOnEditPension).toHaveBeenCalledWith('1');
  });

  it('calls onAddPension when Add button is clicked', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/uk-pensions')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockPensions),
        });
      }
      if (url.includes('/total-pot')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTotalPot),
        });
      }
    });

    render(<PensionList onAddPension={mockOnAddPension} onEditPension={mockOnEditPension} />);

    await waitFor(() => {
      expect(screen.getByText(/Add another pension/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/Add another pension/i).closest('div'));

    expect(mockOnAddPension).toHaveBeenCalled();
  });

  it('renders empty state when no pensions', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/uk-pensions')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([]),
        });
      }
      if (url.includes('/total-pot')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(null),
        });
      }
    });

    render(<PensionList onAddPension={mockOnAddPension} onEditPension={mockOnEditPension} />);

    await waitFor(() => {
      expect(screen.getByText(/Start tracking your pensions/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Add Your First Pension/i)).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: false,
        status: 500,
      })
    );

    render(<PensionList onAddPension={mockOnAddPension} onEditPension={mockOnEditPension} />);

    await waitFor(() => {
      expect(screen.getByText(/Error Loading Pensions/i)).toBeInTheDocument();
    });
  });

  it('handles delete pension with confirmation', async () => {
    global.confirm = jest.fn(() => true);
    global.alert = jest.fn();

    fetch.mockImplementation((url, options) => {
      if (url.includes('/uk-pensions') && !options) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockPensions),
        });
      }
      if (url.includes('/total-pot')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTotalPot),
        });
      }
      if (options?.method === 'DELETE') {
        return Promise.resolve({
          ok: true,
        });
      }
    });

    render(<PensionList onAddPension={mockOnAddPension} onEditPension={mockOnEditPension} />);

    await waitFor(() => {
      expect(screen.getByText(/Aviva Workplace Pension/i)).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByText(/Delete/i);
    fireEvent.click(deleteButtons[0]);

    expect(global.confirm).toHaveBeenCalledWith('Are you sure you want to delete this pension?');
  });
});
