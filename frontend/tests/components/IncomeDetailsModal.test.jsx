import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { IncomeDetailsModal } from '../../src/components/income/IncomeDetailsModal';

describe('IncomeDetailsModal', () => {
  const mockIncome = {
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
    is_gross: true,
    tax_withheld_at_source: 10000,
    paye_reference: '123/AB12345',
    exchange_rate_used: 23,
    exchange_rate_date: '2024-04-01',
    uk_tax_year: '2024/25',
    sa_tax_year: '2024/2025',
  };

  const mockHandlers = {
    onEdit: jest.fn(),
    onDelete: jest.fn(),
    onClose: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders income details', () => {
    render(
      <IncomeDetailsModal
        income={mockIncome}
        {...mockHandlers}
      />
    );

    expect(screen.getByText(/ABC Company Ltd/i)).toBeInTheDocument();
    expect(screen.getByText(/Employment/i)).toBeInTheDocument();
    expect(screen.getByText(/£45,000.00/)).toBeInTheDocument();
  });

  it('displays currency conversion details', () => {
    render(
      <IncomeDetailsModal
        income={mockIncome}
        {...mockHandlers}
      />
    );

    expect(screen.getByText(/Currency Conversion/i)).toBeInTheDocument();
    expect(screen.getByText(/Converted to GBP/i)).toBeInTheDocument();
    expect(screen.getByText(/Converted to ZAR/i)).toBeInTheDocument();
    expect(screen.getByText(/23.000000/)).toBeInTheDocument(); // Exchange rate
  });

  it('displays tax withheld information', () => {
    render(
      <IncomeDetailsModal
        income={mockIncome}
        {...mockHandlers}
      />
    );

    expect(screen.getByText(/Tax Withheld/i)).toBeInTheDocument();
    expect(screen.getByText(/£10,000.00/)).toBeInTheDocument();
    expect(screen.getByText(/123\/AB12345/)).toBeInTheDocument();
  });

  it('displays tax year allocations', () => {
    render(
      <IncomeDetailsModal
        income={mockIncome}
        {...mockHandlers}
      />
    );

    expect(screen.getByText(/Tax Year Allocation/i)).toBeInTheDocument();
    expect(screen.getByText(/2024\/25/)).toBeInTheDocument();
    expect(screen.getByText(/2024\/2025/)).toBeInTheDocument();
  });

  it('shows foreign income callout for non-UK/ZA income', () => {
    const foreignIncome = {
      ...mockIncome,
      source_country: 'US',
    };

    render(
      <IncomeDetailsModal
        income={foreignIncome}
        {...mockHandlers}
      />
    );

    expect(screen.getByText(/Foreign Income Tax Treatment/i)).toBeInTheDocument();
    expect(screen.getByText(/Double Tax Agreement/i)).toBeInTheDocument();
  });

  it('calls onEdit when edit button clicked', () => {
    render(
      <IncomeDetailsModal
        income={mockIncome}
        {...mockHandlers}
      />
    );

    const editButton = screen.getByText(/Edit/i);
    fireEvent.click(editButton);

    expect(mockHandlers.onEdit).toHaveBeenCalledWith(mockIncome);
  });

  it('calls onDelete when delete button clicked and confirmed', () => {
    window.confirm = jest.fn(() => true);

    render(
      <IncomeDetailsModal
        income={mockIncome}
        {...mockHandlers}
      />
    );

    const deleteButton = screen.getByText(/Delete/i);
    fireEvent.click(deleteButton);

    expect(window.confirm).toHaveBeenCalled();
    expect(mockHandlers.onDelete).toHaveBeenCalledWith('1');
    expect(mockHandlers.onClose).toHaveBeenCalled();
  });

  it('does not call onDelete when delete is cancelled', () => {
    window.confirm = jest.fn(() => false);

    render(
      <IncomeDetailsModal
        income={mockIncome}
        {...mockHandlers}
      />
    );

    const deleteButton = screen.getByText(/Delete/i);
    fireEvent.click(deleteButton);

    expect(window.confirm).toHaveBeenCalled();
    expect(mockHandlers.onDelete).not.toHaveBeenCalled();
  });

  it('calls onClose when close button clicked', () => {
    render(
      <IncomeDetailsModal
        income={mockIncome}
        {...mockHandlers}
      />
    );

    const closeButton = screen.getByText(/Close/i);
    fireEvent.click(closeButton);

    expect(mockHandlers.onClose).toHaveBeenCalled();
  });

  it('returns null when income is null', () => {
    const { container } = render(
      <IncomeDetailsModal
        income={null}
        {...mockHandlers}
      />
    );

    expect(container.firstChild).toBeNull();
  });
});
