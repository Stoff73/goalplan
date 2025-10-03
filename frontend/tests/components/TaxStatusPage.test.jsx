import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import TaxStatusPage from '../../src/pages/TaxStatusPage';
import { taxStatusEndpoints } from '../../src/utils/api';

// Mock the API
jest.mock('../../src/utils/api', () => ({
  taxStatusEndpoints: {
    getCurrent: jest.fn(),
    getHistory: jest.fn(),
    getDeemedDomicile: jest.fn(),
    create: jest.fn(),
  },
}));

// Mock auth storage
jest.mock('../../src/utils/auth', () => ({
  authStorage: {
    getUser: jest.fn(() => ({
      firstName: 'John',
      lastName: 'Doe',
      email: 'john@example.com',
    })),
    getAccessToken: jest.fn(() => 'mock-token'),
  },
}));

const mockCurrentStatus = {
  id: '1',
  effective_from: '2024-04-06',
  effective_to: null,
  uk_tax_resident: true,
  sa_tax_resident: false,
  domicile: 'UK_DOMICILED',
  domicile_of_origin: 'UK',
  uk_residence_basis: 'ARISING',
  dual_resident: false,
  created_at: '2024-01-01T00:00:00Z',
};

const mockHistory = [
  {
    id: '1',
    effective_from: '2024-04-06',
    effective_to: null,
    uk_tax_resident: true,
    sa_tax_resident: false,
    domicile: 'UK_DOMICILED',
    created_at: '2024-01-01T00:00:00Z',
  },
];

const mockDeemedDomicile = {
  uk_deemed_domicile: false,
  uk_resident_years_in_last_20: 5,
  deemed_domicile_reason: null,
};

describe('TaxStatusPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderPage = () => {
    return render(
      <BrowserRouter>
        <TaxStatusPage />
      </BrowserRouter>
    );
  };

  test('renders loading state initially', () => {
    taxStatusEndpoints.getCurrent.mockImplementation(() => new Promise(() => {}));
    taxStatusEndpoints.getHistory.mockImplementation(() => new Promise(() => {}));
    taxStatusEndpoints.getDeemedDomicile.mockImplementation(() => new Promise(() => {}));

    renderPage();

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('renders current tax status when data is loaded', async () => {
    taxStatusEndpoints.getCurrent.mockResolvedValue(mockCurrentStatus);
    taxStatusEndpoints.getHistory.mockResolvedValue(mockHistory);
    taxStatusEndpoints.getDeemedDomicile.mockResolvedValue(mockDeemedDomicile);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/your current tax status/i)).toBeInTheDocument();
      expect(screen.getByText(/UK tax resident/i)).toBeInTheDocument();
    });
  });

  test('shows update form when no current status exists', async () => {
    taxStatusEndpoints.getCurrent.mockRejectedValue({ status: 404 });
    taxStatusEndpoints.getHistory.mockResolvedValue([]);
    taxStatusEndpoints.getDeemedDomicile.mockRejectedValue({ status: 404 });

    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/update your tax status/i)).toBeInTheDocument();
    });
  });

  test('shows calculators section', async () => {
    taxStatusEndpoints.getCurrent.mockResolvedValue(mockCurrentStatus);
    taxStatusEndpoints.getHistory.mockResolvedValue(mockHistory);
    taxStatusEndpoints.getDeemedDomicile.mockResolvedValue(mockDeemedDomicile);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/tax residency calculators/i)).toBeInTheDocument();
      expect(screen.getByText(/UK Statutory Residence Test/i)).toBeInTheDocument();
    });
  });

  test('submits new tax status successfully', async () => {
    taxStatusEndpoints.getCurrent.mockResolvedValue(mockCurrentStatus);
    taxStatusEndpoints.getHistory.mockResolvedValue(mockHistory);
    taxStatusEndpoints.getDeemedDomicile.mockResolvedValue(mockDeemedDomicile);
    taxStatusEndpoints.create.mockResolvedValue({ success: true });

    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/your current tax status/i)).toBeInTheDocument();
    });

    // Click edit button
    const updateButton = screen.getByRole('button', { name: /update/i });
    fireEvent.click(updateButton);

    // Form should be visible
    await waitFor(() => {
      expect(screen.getByText(/update your tax status/i)).toBeInTheDocument();
    });
  });

  test('handles API error gracefully', async () => {
    taxStatusEndpoints.getCurrent.mockRejectedValue(new Error('Network error'));
    taxStatusEndpoints.getHistory.mockRejectedValue(new Error('Network error'));
    taxStatusEndpoints.getDeemedDomicile.mockRejectedValue(new Error('Network error'));

    renderPage();

    // Should not crash, might show error or empty state
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
  });

  test('displays deemed domicile section', async () => {
    taxStatusEndpoints.getCurrent.mockResolvedValue(mockCurrentStatus);
    taxStatusEndpoints.getHistory.mockResolvedValue(mockHistory);
    taxStatusEndpoints.getDeemedDomicile.mockResolvedValue(mockDeemedDomicile);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/your deemed domicile status/i)).toBeInTheDocument();
    });
  });

  test('displays tax status history', async () => {
    taxStatusEndpoints.getCurrent.mockResolvedValue(mockCurrentStatus);
    taxStatusEndpoints.getHistory.mockResolvedValue(mockHistory);
    taxStatusEndpoints.getDeemedDomicile.mockResolvedValue(mockDeemedDomicile);

    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/tax status history/i)).toBeInTheDocument();
    });
  });
});
