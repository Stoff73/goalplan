import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { IncomeFormModal } from '../../src/components/income/IncomeFormModal';

describe('IncomeFormModal', () => {
  const mockHandlers = {
    onSave: jest.fn(),
    onCancel: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders add income modal', () => {
    render(
      <IncomeFormModal
        income={null}
        loading={false}
        {...mockHandlers}
      />
    );

    expect(screen.getByText(/Add income entry/i)).toBeInTheDocument();
    expect(screen.getByText(/Record your income to track earnings/i)).toBeInTheDocument();
  });

  it('renders edit income modal with data', () => {
    const mockIncome = {
      income_type: 'employment',
      source_country: 'UK',
      description: 'Monthly salary',
      related_entity: 'ABC Company',
      amount: 45000,
      currency: 'GBP',
      frequency: 'annual',
      start_date: '2024-04-01',
      is_gross: true,
    };

    render(
      <IncomeFormModal
        income={mockIncome}
        loading={false}
        {...mockHandlers}
      />
    );

    expect(screen.getByText(/Edit income entry/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue('45000')).toBeInTheDocument();
    expect(screen.getByDisplayValue('ABC Company')).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    render(
      <IncomeFormModal
        income={null}
        loading={false}
        {...mockHandlers}
      />
    );

    const submitButton = screen.getByText(/Add Income/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Income type is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Amount must be greater than 0/i)).toBeInTheDocument();
      expect(screen.getByText(/Start date is required/i)).toBeInTheDocument();
    });

    expect(mockHandlers.onSave).not.toHaveBeenCalled();
  });

  it('submits form with valid data', async () => {
    render(
      <IncomeFormModal
        income={null}
        loading={false}
        {...mockHandlers}
      />
    );

    // Fill in required fields
    const typeSelect = screen.getByLabelText(/Income Type/i);
    fireEvent.change(typeSelect, { target: { value: 'employment' } });

    const amountInput = screen.getByLabelText(/Amount/i);
    fireEvent.change(amountInput, { target: { value: '45000' } });

    const dateInput = screen.getByLabelText(/Start Date/i);
    fireEvent.change(dateInput, { target: { value: '2024-04-01' } });

    const submitButton = screen.getByText(/Add Income/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockHandlers.onSave).toHaveBeenCalledWith(
        expect.objectContaining({
          incomeType: 'employment',
          amount: 45000,
          startDate: '2024-04-01',
        })
      );
    });
  });

  it('shows foreign income callout for non-UK/ZA countries', () => {
    render(
      <IncomeFormModal
        income={null}
        loading={false}
        {...mockHandlers}
      />
    );

    const countrySelect = screen.getByLabelText(/Source Country/i);
    fireEvent.change(countrySelect, { target: { value: 'US' } });

    expect(screen.getByText(/Foreign income detected/i)).toBeInTheDocument();
  });

  it('shows tax withheld section when checkbox is checked', () => {
    render(
      <IncomeFormModal
        income={null}
        loading={false}
        {...mockHandlers}
      />
    );

    const checkbox = screen.getByLabelText(/Tax withheld at source/i);
    fireEvent.click(checkbox);

    expect(screen.getByLabelText(/Tax Withheld Amount/i)).toBeInTheDocument();
  });

  it('validates tax withheld does not exceed income', async () => {
    render(
      <IncomeFormModal
        income={null}
        loading={false}
        {...mockHandlers}
      />
    );

    // Fill in amount
    const amountInput = screen.getByLabelText(/Amount/i);
    fireEvent.change(amountInput, { target: { value: '1000' } });

    // Show tax withheld section
    const checkbox = screen.getByLabelText(/Tax withheld at source/i);
    fireEvent.click(checkbox);

    // Enter tax withheld greater than amount
    const taxWithheldInput = screen.getByLabelText(/Tax Withheld Amount/i);
    fireEvent.change(taxWithheldInput, { target: { value: '2000' } });

    // Fill other required fields
    const typeSelect = screen.getByLabelText(/Income Type/i);
    fireEvent.change(typeSelect, { target: { value: 'employment' } });

    const dateInput = screen.getByLabelText(/Start Date/i);
    fireEvent.change(dateInput, { target: { value: '2024-04-01' } });

    const submitButton = screen.getByText(/Add Income/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Tax withheld cannot exceed income amount/i)).toBeInTheDocument();
    });
  });

  it('calls onCancel when cancel button clicked', () => {
    render(
      <IncomeFormModal
        income={null}
        loading={false}
        {...mockHandlers}
      />
    );

    const cancelButton = screen.getByText(/Cancel/i);
    fireEvent.click(cancelButton);

    expect(mockHandlers.onCancel).toHaveBeenCalled();
  });

  it('disables buttons when loading', () => {
    render(
      <IncomeFormModal
        income={null}
        loading={true}
        {...mockHandlers}
      />
    );

    const submitButton = screen.getByText(/Saving.../i);
    const cancelButton = screen.getByText(/Cancel/i);

    expect(submitButton).toBeDisabled();
    expect(cancelButton).toBeDisabled();
  });
});
