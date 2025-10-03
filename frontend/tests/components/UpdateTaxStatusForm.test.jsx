import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UpdateTaxStatusForm } from '../../src/components/tax/UpdateTaxStatusForm';

describe('UpdateTaxStatusForm', () => {
  const mockOnSubmit = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders form fields', () => {
    render(<UpdateTaxStatusForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} loading={false} />);

    expect(screen.getByLabelText(/effective from date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/UK tax resident/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/South African tax resident/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/domicile status/i)).toBeInTheDocument();
  });

  test('shows dual residency warning when both checkboxes are checked', () => {
    render(<UpdateTaxStatusForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} loading={false} />);

    const ukCheckbox = screen.getByLabelText(/UK tax resident/i);
    const saCheckbox = screen.getByLabelText(/South African tax resident/i);

    fireEvent.click(ukCheckbox);
    fireEvent.click(saCheckbox);

    expect(screen.getByText(/resident in both countries/i)).toBeInTheDocument();
  });

  test('shows remittance basis option for non-UK domiciled residents', async () => {
    render(<UpdateTaxStatusForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} loading={false} />);

    const ukCheckbox = screen.getByLabelText(/UK tax resident/i);
    fireEvent.click(ukCheckbox);

    const domicileSelect = screen.getByLabelText(/domicile status/i);
    fireEvent.change(domicileSelect, { target: { value: 'NON_UK_DOMICILED' } });

    await waitFor(() => {
      expect(screen.getByLabelText(/UK residence basis/i)).toBeInTheDocument();
    });
  });

  test('validates required fields', async () => {
    render(<UpdateTaxStatusForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} loading={false} />);

    const submitButton = screen.getByRole('button', { name: /save tax status/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/domicile status/i)).toBeInTheDocument();
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });
  });

  test('calls onCancel when cancel button is clicked', () => {
    render(<UpdateTaxStatusForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} loading={false} />);

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalledTimes(1);
  });

  test('toggles help sections', () => {
    render(<UpdateTaxStatusForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} loading={false} />);

    const ukHelpButton = screen.getAllByText(/how do i know/i)[0];
    fireEvent.click(ukHelpButton);

    expect(screen.getByText(/183\+ days in the UK/i)).toBeInTheDocument();
  });

  test('shows disabled state when loading', () => {
    render(<UpdateTaxStatusForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} loading={true} />);

    const submitButton = screen.getByRole('button', { name: /saving/i });
    expect(submitButton).toBeDisabled();

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    expect(cancelButton).toBeDisabled();
  });

  test('requires DTA tie-breaker when dual resident', async () => {
    render(<UpdateTaxStatusForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} loading={false} />);

    // Fill in required fields
    const effectiveDate = screen.getByLabelText(/effective from date/i);
    fireEvent.change(effectiveDate, { target: { value: '2024-04-06' } });

    const ukCheckbox = screen.getByLabelText(/UK tax resident/i);
    const saCheckbox = screen.getByLabelText(/South African tax resident/i);
    fireEvent.click(ukCheckbox);
    fireEvent.click(saCheckbox);

    const domicileSelect = screen.getByLabelText(/domicile status/i);
    fireEvent.change(domicileSelect, { target: { value: 'UK_DOMICILED' } });

    const domicileOriginSelect = screen.getByLabelText(/domicile of origin/i);
    fireEvent.change(domicileOriginSelect, { target: { value: 'UK' } });

    // Try to submit without DTA tie-breaker
    const submitButton = screen.getByRole('button', { name: /save tax status/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/select DTA tie-breaker/i)).toBeInTheDocument();
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });
  });
});
