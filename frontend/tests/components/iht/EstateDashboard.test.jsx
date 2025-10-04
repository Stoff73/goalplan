import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { EstateDashboard } from '../../../src/components/iht/EstateDashboard';
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

describe('EstateDashboard Component', () => {
  const mockEstateData = {
    calculationDate: '2024-10-03',
    scenarioType: 'CURRENT',
    estateValuation: {
      grossEstate: { gbp: 500000, zar: 9500000 },
      totalLiabilities: { gbp: 150000, zar: 2850000 },
      netEstate: { gbp: 350000, zar: 6650000 },
    },
    assetBreakdown: {
      ukAssets: { gbp: 400000, percentage: 80 },
      saAssets: { zar: 1900000, percentage: 20 },
      excludedProperty: { gbp: 0 },
      assets: [
        {
          id: 'asset-1',
          description: 'Main residence',
          assetType: 'PROPERTY',
          currentValue: 350000,
          ukIhtApplicable: true,
        },
        {
          id: 'asset-2',
          description: 'Investment portfolio',
          assetType: 'INVESTMENT',
          currentValue: 150000,
          ukIhtApplicable: true,
        },
      ],
    },
    ukInheritanceTax: {
      taxableEstate: 350000,
      nilRateBand: {
        current: 325000,
        transferredFromSpouse: 0,
        total: 325000,
        unused: 0,
      },
      residenceNilRateBand: {
        maximum: 175000,
        taperReduction: 0,
        available: 175000,
        transferredFromSpouse: 0,
        total: 175000,
      },
      reliefs: {
        businessPropertyRelief: 0,
        agriculturalPropertyRelief: 0,
        total: 0,
      },
      chargeableEstate: 0,
      taxRate: 0.40,
      grossTaxLiability: 0,
      dtaRelief: 0,
      netTaxLiability: 0,
      effectiveRate: 0,
    },
    totalDeathTaxes: {
      ukIht: 0,
      saEstateDuty: 0,
      total: { gbp: 0, zar: 0 },
      effectiveOverallRate: 0,
    },
    netEstateAfterTax: {
      beforeTax: { gbp: 350000, zar: 6650000 },
      totalTax: { gbp: 0, zar: 0 },
      afterTax: { gbp: 350000, zar: 6650000 },
      percentageReduction: 0,
    },
    liabilities: [
      {
        id: 'liability-1',
        description: 'Mortgage',
        liabilityType: 'MORTGAGE',
        outstandingBalance: 150000,
        ukIhtDeductible: true,
      },
    ],
    recommendations: [
      {
        category: 'GIFT_PLANNING',
        title: 'Start lifetime gifting',
        description: 'Consider making gifts to reduce your estate',
        estimatedSaving: { gbp: 10000, zar: 190000 },
        priority: 'HIGH',
      },
    ],
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    fetch.mockImplementation(() => new Promise(() => {}));

    render(<EstateDashboard />);

    expect(screen.getByText(/Loading your estate calculation/i)).toBeInTheDocument();
  });

  it('renders estate dashboard with data', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/estate-calculation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockEstateData),
        });
      }
    });

    render(<EstateDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Your estate:/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/£350,000/)).toBeInTheDocument();
    expect(screen.getByText(/Good news! Based on current rules, you won't owe any Inheritance Tax/i)).toBeInTheDocument();
  });

  it('renders estate with IHT liability', async () => {
    const estateWithTax = {
      ...mockEstateData,
      estateValuation: {
        grossEstate: { gbp: 800000, zar: 15200000 },
        totalLiabilities: { gbp: 100000, zar: 1900000 },
        netEstate: { gbp: 700000, zar: 13300000 },
      },
      ukInheritanceTax: {
        ...mockEstateData.ukInheritanceTax,
        taxableEstate: 700000,
        chargeableEstate: 200000,
        grossTaxLiability: 80000,
        netTaxLiability: 80000,
      },
    };

    fetch.mockImplementation((url) => {
      if (url.includes('/estate-calculation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(estateWithTax),
        });
      }
    });

    render(<EstateDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/you might owe/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/£80,000/)).toBeInTheDocument();
    expect(screen.getByText(/in Inheritance Tax/i)).toBeInTheDocument();
  });

  it('renders asset table with edit and delete actions', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/estate-calculation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockEstateData),
        });
      }
    });

    render(<EstateDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/What you own/i)).toBeInTheDocument();
    });

    expect(screen.getByText('Main residence')).toBeInTheDocument();
    expect(screen.getByText('Investment portfolio')).toBeInTheDocument();

    const editButtons = screen.getAllByText(/Edit/i);
    expect(editButtons.length).toBeGreaterThan(0);

    const deleteButtons = screen.getAllByText(/Delete/i);
    expect(deleteButtons.length).toBeGreaterThan(0);
  });

  it('renders liabilities table', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/estate-calculation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockEstateData),
        });
      }
    });

    render(<EstateDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/What you owe/i)).toBeInTheDocument();
    });

    expect(screen.getByText('Mortgage')).toBeInTheDocument();
  });

  it('renders recommendations section', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/estate-calculation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockEstateData),
        });
      }
    });

    render(<EstateDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/What to do next/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Start lifetime gifting/i)).toBeInTheDocument();
  });

  it('updates IHT calculation when parameters change', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/estate-calculation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockEstateData),
        });
      }
    });

    render(<EstateDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Your estate:/i)).toBeInTheDocument();
    });

    // Find and change the transferable NRB slider
    const slider = screen.getByLabelText(/Transferable NRB from spouse/i);
    fireEvent.change(slider, { target: { value: '162500' } });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/estate-calculation'),
        expect.objectContaining({
          method: 'POST',
        })
      );
    });
  });

  it('handles delete asset', async () => {
    window.confirm = jest.fn(() => true);

    fetch.mockImplementation((url, options) => {
      if (url.includes('/estate-calculation') && !options?.method) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockEstateData),
        });
      }
      if (url.includes('/assets/') && options?.method === 'DELETE') {
        return Promise.resolve({ ok: true });
      }
      return Promise.reject(new Error('Not found'));
    });

    render(<EstateDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Main residence')).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByText(/Delete/i);
    fireEvent.click(deleteButtons[0]);

    expect(window.confirm).toHaveBeenCalledWith(
      'Are you sure you want to delete this asset?'
    );

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/assets/asset-1'),
        expect.objectContaining({ method: 'DELETE' })
      );
    });
  });

  it('renders empty state when no assets', async () => {
    const emptyEstateData = {
      ...mockEstateData,
      estateValuation: {
        grossEstate: { gbp: 0, zar: 0 },
        totalLiabilities: { gbp: 0, zar: 0 },
        netEstate: { gbp: 0, zar: 0 },
      },
    };

    fetch.mockImplementation((url) => {
      if (url.includes('/estate-calculation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(emptyEstateData),
        });
      }
    });

    render(<EstateDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Plan your estate and inheritance tax/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Add Your First Asset/i)).toBeInTheDocument();
  });

  it('handles error state', async () => {
    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: false,
        status: 500,
      })
    );

    render(<EstateDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Error Loading Estate/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Try Again/i)).toBeInTheDocument();
  });

  it('handles 401 unauthorized and redirects to login', async () => {
    delete window.location;
    window.location = { href: '' };

    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: false,
        status: 401,
      })
    );

    render(<EstateDashboard />);

    await waitFor(() => {
      expect(authStorage.clear).toHaveBeenCalled();
      expect(window.location.href).toBe('/login');
    });
  });

  it('toggles expandable sections', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/estate-calculation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockEstateData),
        });
      }
    });

    render(<EstateDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Tell me more about nil rate bands/i)).toBeInTheDocument();
    });

    const expandButton = screen.getByText(/Tell me more about nil rate bands/i);
    fireEvent.click(expandButton);

    await waitFor(() => {
      expect(screen.getByText(/The nil rate band means the first £325,000/i)).toBeInTheDocument();
    });
  });
});
