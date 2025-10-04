import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { CareerChangeScenario } from '../../../src/components/scenarios/CareerChangeScenario';
import { authStorage } from '../../../src/utils/auth';

jest.mock('../../../src/utils/auth', () => ({
  authStorage: {
    getAccessToken: jest.fn(() => 'mock-token'),
    clear: jest.fn(),
  },
}));

global.fetch = jest.fn();

describe('CareerChangeScenario', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();
  });

  it('renders narrative introduction', () => {
    render(<CareerChangeScenario />);

    expect(screen.getByText(/Model a job change/i)).toBeInTheDocument();
    expect(screen.getByText(/Thinking about a career change/i)).toBeInTheDocument();
  });

  it('renders career change form inputs', () => {
    render(<CareerChangeScenario />);

    expect(screen.getByLabelText(/New annual salary/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/When would this happen/i)).toBeInTheDocument();
    expect(screen.getByText(/Show me the impact/i)).toBeInTheDocument();
  });

  it('submits form and runs scenario', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        current_salary: 50000,
        salary_change: 10000,
        monthly_takehome_change: 500,
        pension_change_monthly: 100,
        break_even_months: 3,
        net_worth_impact: 45000,
        tax_impact: 2000,
      }),
    });

    render(<CareerChangeScenario />);

    const salaryInput = screen.getByLabelText(/New annual salary/i);
    const dateInput = screen.getByLabelText(/When would this happen/i);
    const submitButton = screen.getByText(/Show me the impact/i);

    fireEvent.change(salaryInput, { target: { value: '60000' } });
    fireEvent.change(dateInput, { target: { value: '2026-01-01' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/scenarios/career-change',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            new_salary: 60000,
            currency: 'GBP',
            change_date: '2026-01-01',
          }),
        })
      );
    });
  });

  it('displays results with narrative', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        current_salary: 50000,
        salary_change: 10000,
        monthly_takehome_change: 500,
        pension_change: 1200,
        pension_change_monthly: 100,
        break_even_months: 3,
        net_worth_impact: 45000,
        tax_impact: 2000,
        recommendations: ['Review pension contributions', 'Update emergency fund target'],
      }),
    });

    render(<CareerChangeScenario />);

    const salaryInput = screen.getByLabelText(/New annual salary/i);
    const dateInput = screen.getByLabelText(/When would this happen/i);
    const submitButton = screen.getByText(/Show me the impact/i);

    fireEvent.change(salaryInput, { target: { value: '60000' } });
    fireEvent.change(dateInput, { target: { value: '2026-01-01' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Good news!/i)).toBeInTheDocument();
      expect(screen.getByText(/£500/)).toBeInTheDocument();
      expect(screen.getByText(/£100/)).toBeInTheDocument();
      expect(screen.getByText(/3 months/i)).toBeInTheDocument();
    });
  });

  it('handles negative salary change', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        current_salary: 60000,
        salary_change: -10000,
        monthly_takehome_change: -500,
        pension_change_monthly: -100,
        net_worth_impact: -45000,
        tax_impact: -2000,
      }),
    });

    render(<CareerChangeScenario />);

    const salaryInput = screen.getByLabelText(/New annual salary/i);
    const dateInput = screen.getByLabelText(/When would this happen/i);
    const submitButton = screen.getByText(/Show me the impact/i);

    fireEvent.change(salaryInput, { target: { value: '50000' } });
    fireEvent.change(dateInput, { target: { value: '2026-01-01' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Impact analysis/i)).toBeInTheDocument();
      expect(screen.getByText(/decrease/i)).toBeInTheDocument();
    });
  });

  it('validates required fields', () => {
    render(<CareerChangeScenario />);

    const submitButton = screen.getByText(/Show me the impact/i);
    expect(submitButton).toBeDisabled();

    const salaryInput = screen.getByLabelText(/New annual salary/i);
    fireEvent.change(salaryInput, { target: { value: '60000' } });

    expect(submitButton).toBeDisabled();

    const dateInput = screen.getByLabelText(/When would this happen/i);
    fireEvent.change(dateInput, { target: { value: '2026-01-01' } });

    expect(submitButton).not.toBeDisabled();
  });

  it('allows currency selection', () => {
    render(<CareerChangeScenario />);

    const currencySelect = screen.getByDisplayValue('GBP (£)');
    expect(currencySelect).toBeInTheDocument();

    fireEvent.change(currencySelect, { target: { value: 'ZAR' } });
    expect(currencySelect.value).toBe('ZAR');
  });
});
