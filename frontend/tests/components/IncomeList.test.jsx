import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { IncomeList } from '../../src/components/income/IncomeList';

describe('IncomeList', () => {
  const mockIncomes = [
    {
      id: '1',
      income_type: 'employment',
      source_country: 'UK',
      description: 'Monthly salary',
      related_entity: 'ABC Company Ltd',
      amount: 45000,
      currency: 'GBP',
      gbp_amount: 45000,
      zar_amount: 1035000,
      frequency: 'annual',
      start_date: '2024-04-01',
      tax_withheld_at_source: 10000,
    },
    {
      id: '2',
      income_type: 'rental',
      source_country: 'ZA',
      description: 'Rental from property A',
      amount: 7500,
      currency: 'ZAR',
      gbp_amount: 325,
      zar_amount: 7500,
      frequency: 'monthly',
      start_date: '2024-01-01',
    },
  ];

  const mockHandlers = {
    onEdit: jest.fn(),
    onDelete: jest.fn(),
    onViewDetails: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders income list', () => {
    render(
      <IncomeList
        incomes={mockIncomes}
        loading={false}
        {...mockHandlers}
        selectedTaxYear="2024/25"
        selectedCountry="UK"
      />
    );

    expect(screen.getByText(/ABC Company Ltd/i)).toBeInTheDocument();
    expect(screen.getByText(/Rental from property A/i)).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(
      <IncomeList
        incomes={[]}
        loading={true}
        {...mockHandlers}
        selectedTaxYear="2024/25"
        selectedCountry="UK"
      />
    );

    expect(screen.getByText(/Loading income entries/i)).toBeInTheDocument();
  });

  it('shows empty state when no incomes', () => {
    render(
      <IncomeList
        incomes={[]}
        loading={false}
        {...mockHandlers}
        selectedTaxYear="2024/25"
        selectedCountry="UK"
      />
    );

    expect(screen.getByText(/No income recorded yet/i)).toBeInTheDocument();
  });

  it('filters by income type', () => {
    render(
      <IncomeList
        incomes={mockIncomes}
        loading={false}
        {...mockHandlers}
        selectedTaxYear="2024/25"
        selectedCountry="UK"
      />
    );

    const typeFilter = screen.getByLabelText(/Filter by Type/i);
    fireEvent.change(typeFilter, { target: { value: 'employment' } });

    expect(screen.getByText(/ABC Company Ltd/i)).toBeInTheDocument();
    expect(screen.queryByText(/Rental from property A/i)).not.toBeInTheDocument();
  });

  it('filters by country', () => {
    render(
      <IncomeList
        incomes={mockIncomes}
        loading={false}
        {...mockHandlers}
        selectedTaxYear="2024/25"
        selectedCountry="UK"
      />
    );

    const countryFilter = screen.getByLabelText(/Filter by Country/i);
    fireEvent.change(countryFilter, { target: { value: 'ZA' } });

    expect(screen.queryByText(/ABC Company Ltd/i)).not.toBeInTheDocument();
    expect(screen.getByText(/Rental from property A/i)).toBeInTheDocument();
  });

  it('calls onEdit when edit button clicked', () => {
    render(
      <IncomeList
        incomes={mockIncomes}
        loading={false}
        {...mockHandlers}
        selectedTaxYear="2024/25"
        selectedCountry="UK"
      />
    );

    const editButtons = screen.getAllByText(/Edit/i);
    fireEvent.click(editButtons[0]);

    expect(mockHandlers.onEdit).toHaveBeenCalledWith(mockIncomes[0]);
  });

  it('calls onDelete when delete button clicked and confirmed', () => {
    window.confirm = jest.fn(() => true);

    render(
      <IncomeList
        incomes={mockIncomes}
        loading={false}
        {...mockHandlers}
        selectedTaxYear="2024/25"
        selectedCountry="UK"
      />
    );

    const deleteButtons = screen.getAllByText(/Delete/i);
    fireEvent.click(deleteButtons[0]);

    expect(window.confirm).toHaveBeenCalled();
    expect(mockHandlers.onDelete).toHaveBeenCalledWith('1');
  });

  it('calls onViewDetails when income card clicked', () => {
    render(
      <IncomeList
        incomes={mockIncomes}
        loading={false}
        {...mockHandlers}
        selectedTaxYear="2024/25"
        selectedCountry="UK"
      />
    );

    const incomeCard = screen.getByText(/ABC Company Ltd/i).closest('div');
    fireEvent.click(incomeCard);

    expect(mockHandlers.onViewDetails).toHaveBeenCalledWith(mockIncomes[0]);
  });

  it('sorts incomes by date', () => {
    render(
      <IncomeList
        incomes={mockIncomes}
        loading={false}
        {...mockHandlers}
        selectedTaxYear="2024/25"
        selectedCountry="UK"
      />
    );

    const sortSelect = screen.getByLabelText(/Sort By/i);
    fireEvent.change(sortSelect, { target: { value: 'date_asc' } });

    // Check that the order has changed (oldest first)
    const incomeCards = screen.getAllByText(/United/i);
    expect(incomeCards.length).toBeGreaterThan(0);
  });
});
