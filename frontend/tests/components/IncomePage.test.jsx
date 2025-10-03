import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import IncomePage from '../../src/pages/IncomePage';
import { incomeEndpoints } from '../../src/utils/api';

// Mock the API
jest.mock('../../src/utils/api', () => ({
  incomeEndpoints: {
    getAll: jest.fn(),
    getSummary: jest.fn(),
    create: jest.fn(),
    update: jest.fn(),
    delete: jest.fn(),
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

const mockIncomes = [
  {
    id: '1',
    income_type: 'employment',
    source_country: 'UK',
    description: 'Monthly salary',
    related_entity: 'ABC Company',
    amount: 45000,
    currency: 'GBP',
    gbp_amount: 45000,
    zar_amount: 1035000,
    frequency: 'annual',
    start_date: '2024-04-01',
  },
];

const mockSummary = {
  total_income_gbp: 45000,
  total_income_zar: 1035000,
  by_type: { employment: 45000 },
  by_country: { UK: 45000 },
};

describe('IncomePage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    incomeEndpoints.getAll.mockResolvedValue(mockIncomes);
    incomeEndpoints.getSummary.mockResolvedValue(mockSummary);
  });

  const renderWithRouter = (component) => {
    return render(<BrowserRouter>{component}</BrowserRouter>);
  };

  it('renders income page', async () => {
    renderWithRouter(<IncomePage />);

    await waitFor(() => {
      expect(screen.getByText(/Your Income Tracking/i)).toBeInTheDocument();
    });
  });

  it('loads incomes on mount', async () => {
    renderWithRouter(<IncomePage />);

    await waitFor(() => {
      expect(incomeEndpoints.getAll).toHaveBeenCalled();
      expect(incomeEndpoints.getSummary).toHaveBeenCalled();
    });
  });

  it('displays error message on load failure', async () => {
    incomeEndpoints.getAll.mockRejectedValue(new Error('Network error'));

    renderWithRouter(<IncomePage />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to load income entries/i)).toBeInTheDocument();
    });
  });

  it('opens add income modal when button clicked', async () => {
    renderWithRouter(<IncomePage />);

    await waitFor(() => {
      expect(screen.getByText(/ABC Company/i)).toBeInTheDocument();
    });

    const addButton = screen.getByText(/Add Income/i);
    fireEvent.click(addButton);

    expect(screen.getByText(/Add income entry/i)).toBeInTheDocument();
  });

  it('creates new income successfully', async () => {
    incomeEndpoints.create.mockResolvedValue({ id: '2' });

    renderWithRouter(<IncomePage />);

    await waitFor(() => {
      expect(screen.getByText(/ABC Company/i)).toBeInTheDocument();
    });

    // Open form
    const addButton = screen.getByText(/Add Income/i);
    fireEvent.click(addButton);

    // Fill form (simplified for test)
    const typeSelect = screen.getByLabelText(/Income Type/i);
    fireEvent.change(typeSelect, { target: { value: 'employment' } });

    const amountInput = screen.getByLabelText(/Amount/i);
    fireEvent.change(amountInput, { target: { value: '50000' } });

    const dateInput = screen.getByLabelText(/Start Date/i);
    fireEvent.change(dateInput, { target: { value: '2024-04-01' } });

    // Submit
    const submitButton = screen.getByText(/Add Income/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(incomeEndpoints.create).toHaveBeenCalled();
      expect(screen.getByText(/Income added successfully!/i)).toBeInTheDocument();
    });
  });

  it('updates existing income successfully', async () => {
    incomeEndpoints.update.mockResolvedValue({ id: '1' });

    renderWithRouter(<IncomePage />);

    await waitFor(() => {
      expect(screen.getByText(/ABC Company/i)).toBeInTheDocument();
    });

    // Click edit on first income
    const editButtons = screen.getAllByText(/Edit/i);
    fireEvent.click(editButtons[0]);

    // Modal should open with edit title
    expect(screen.getByText(/Edit income entry/i)).toBeInTheDocument();

    // Submit
    const submitButton = screen.getByText(/Update Income/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(incomeEndpoints.update).toHaveBeenCalledWith('1', expect.any(Object));
      expect(screen.getByText(/Income updated successfully!/i)).toBeInTheDocument();
    });
  });

  it('deletes income successfully', async () => {
    window.confirm = jest.fn(() => true);
    incomeEndpoints.delete.mockResolvedValue({ success: true });

    renderWithRouter(<IncomePage />);

    await waitFor(() => {
      expect(screen.getByText(/ABC Company/i)).toBeInTheDocument();
    });

    // Click delete on first income
    const deleteButtons = screen.getAllByText(/Delete/i);
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(incomeEndpoints.delete).toHaveBeenCalledWith('1');
      expect(screen.getByText(/Income deleted successfully!/i)).toBeInTheDocument();
    });
  });

  it('changes tax year and reloads summary', async () => {
    renderWithRouter(<IncomePage />);

    await waitFor(() => {
      expect(screen.getByText(/ABC Company/i)).toBeInTheDocument();
    });

    // Change tax year
    const taxYearSelect = screen.getByLabelText(/Tax Year/i);
    fireEvent.change(taxYearSelect, { target: { value: '2023/24' } });

    await waitFor(() => {
      expect(incomeEndpoints.getSummary).toHaveBeenCalledWith('2023/24', 'UK');
    });
  });

  it('changes country and updates tax year', async () => {
    renderWithRouter(<IncomePage />);

    await waitFor(() => {
      expect(screen.getByText(/ABC Company/i)).toBeInTheDocument();
    });

    // Change country
    const countrySelect = screen.getByLabelText(/Tax Year Country/i);
    fireEvent.change(countrySelect, { target: { value: 'SA' } });

    await waitFor(() => {
      // Should reload summary with SA tax year
      expect(incomeEndpoints.getSummary).toHaveBeenCalledWith(
        expect.stringContaining('/'),
        'SA'
      );
    });
  });
});
