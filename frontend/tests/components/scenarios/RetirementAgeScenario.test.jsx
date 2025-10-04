import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { RetirementAgeScenario } from '../../../src/components/scenarios/RetirementAgeScenario';
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

describe('RetirementAgeScenario', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();
  });

  it('renders narrative introduction', () => {
    render(<RetirementAgeScenario />);

    expect(screen.getByText(/Explore when to retire/i)).toBeInTheDocument();
    expect(screen.getByText(/You're currently planning to retire/i)).toBeInTheDocument();
  });

  it('renders retirement age slider', () => {
    render(<RetirementAgeScenario />);

    const slider = screen.getByRole('slider');
    expect(slider).toBeInTheDocument();
    expect(slider).toHaveAttribute('min', '55');
    expect(slider).toHaveAttribute('max', '70');
  });

  it('loads baseline retirement age on mount', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ planned_retirement_age: 67 }),
    });

    render(<RetirementAgeScenario />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/retirement/summary',
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer mock-token',
          }),
        })
      );
    });
  });

  it('runs scenario when slider changes', async () => {
    // Mock baseline load
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ planned_retirement_age: 65 }),
    });

    // Mock scenario calculation
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        retirement_age: 60,
        pension_pot: 450000,
        annual_income: 18000,
        pot_depletion_age: 82,
        baseline_pension_pot: 550000,
        baseline_annual_income: 22000,
      }),
    });

    render(<RetirementAgeScenario />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '60' } });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/scenarios/retirement-age',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ retirement_age: 60 }),
        })
      );
    });
  });

  it('displays scenario results with narrative', async () => {
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ planned_retirement_age: 65 }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          retirement_age: 65,
          pension_pot: 500000,
          annual_income: 20000,
          pot_depletion_age: 90,
          state_pension_annual: 11500,
          state_pension_age: 67,
        }),
      });

    render(<RetirementAgeScenario />);

    await waitFor(() => {
      expect(screen.getByText(/If you retired at 65/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/£500,000/)).toBeInTheDocument();
    expect(screen.getByText(/£20,000/)).toBeInTheDocument();
    expect(screen.getByText(/Age 90/)).toBeInTheDocument();
  });

  it('shows comparison callout when retirement age differs from baseline', async () => {
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ planned_retirement_age: 65 }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          retirement_age: 60,
          pension_pot: 450000,
          annual_income: 18000,
          baseline_pension_pot: 550000,
          baseline_annual_income: 22000,
          salary_change: -50000,
        }),
      });

    render(<RetirementAgeScenario />);

    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '60' } });

    await waitFor(() => {
      expect(screen.getByText(/Retiring 5 years earlier/i)).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ planned_retirement_age: 65 }),
      })
      .mockResolvedValueOnce({
        ok: false,
      });

    render(<RetirementAgeScenario />);

    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '60' } });

    await waitFor(() => {
      expect(screen.getByText(/Failed to calculate retirement scenario/i)).toBeInTheDocument();
    });
  });

  it('redirects to login on 401 error', async () => {
    delete window.location;
    window.location = { href: '' };

    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    render(<RetirementAgeScenario />);

    await waitFor(() => {
      expect(authStorage.clear).toHaveBeenCalled();
      expect(window.location.href).toBe('/login');
    });
  });
});
