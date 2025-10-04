import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MonteCarloScenario } from '../../../src/components/scenarios/MonteCarloScenario';
import { authStorage } from '../../../src/utils/auth';

jest.mock('../../../src/utils/auth', () => ({
  authStorage: {
    getAccessToken: jest.fn(() => 'mock-token'),
    clear: jest.fn(),
  },
}));

global.fetch = jest.fn();

describe('MonteCarloScenario', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();
  });

  it('renders narrative introduction', () => {
    render(<MonteCarloScenario />);

    expect(screen.getByText(/How confident can you be/i)).toBeInTheDocument();
    expect(screen.getByText(/10,000 simulations/i)).toBeInTheDocument();
  });

  it('shows run simulation button initially', () => {
    render(<MonteCarloScenario />);

    expect(screen.getByText(/Run Monte Carlo analysis/i)).toBeInTheDocument();
  });

  it('shows loading state during simulation', async () => {
    global.fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<MonteCarloScenario />);

    const runButton = screen.getByText(/Run Monte Carlo analysis/i);
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText(/Running 10,000 retirement simulations/i)).toBeInTheDocument();
    });
  });

  it('runs Monte Carlo simulation', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success_probability: 87,
        safe_withdrawal_rate: 3.8,
        worst_case_depletion_age: 82,
        best_case_remaining: 650000,
        expected_value: 450000,
        worst_case: 200000,
        best_case: 700000,
        percentiles: {
          p10: 250000,
          p25: 350000,
          p50: 450000,
          p75: 550000,
          p90: 650000,
        },
      }),
    });

    render(<MonteCarloScenario />);

    const runButton = screen.getByText(/Run Monte Carlo analysis/i);
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/scenarios/monte-carlo',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            simulations: 10000,
            years: 30,
          }),
        })
      );
    });
  });

  it('displays simulation results with probability', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success_probability: 87,
        safe_withdrawal_rate: 3.8,
        worst_case_depletion_age: 82,
        best_case_remaining: 650000,
        expected_value: 450000,
        percentiles: {
          p10: 250000,
          p25: 350000,
          p50: 450000,
          p75: 550000,
          p90: 650000,
        },
      }),
    });

    render(<MonteCarloScenario />);

    const runButton = screen.getByText(/Run Monte Carlo analysis/i);
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getAllByText(/87%/)[0]).toBeInTheDocument();
      expect(screen.getByText(/3.8%/)).toBeInTheDocument();
      expect(screen.getByText(/Age 82/)).toBeInTheDocument();
    });
  });

  it('shows success message for high probability', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success_probability: 92,
        safe_withdrawal_rate: 4.0,
        worst_case_depletion_age: 88,
        best_case_remaining: 700000,
        expected_value: 500000,
        percentiles: {
          p10: 300000,
          p25: 400000,
          p50: 500000,
          p75: 600000,
          p90: 700000,
        },
      }),
    });

    render(<MonteCarloScenario />);

    const runButton = screen.getByText(/Run Monte Carlo analysis/i);
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText(/Strong position/i)).toBeInTheDocument();
      expect(screen.getByText(/excellent/i)).toBeInTheDocument();
    });
  });

  it('shows warning for low probability', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success_probability: 65,
        safe_withdrawal_rate: 3.0,
        worst_case_depletion_age: 75,
        best_case_remaining: 400000,
        expected_value: 300000,
        percentiles: {
          p10: 100000,
          p25: 200000,
          p50: 300000,
          p75: 400000,
          p90: 500000,
        },
      }),
    });

    render(<MonteCarloScenario />);

    const runButton = screen.getByText(/Run Monte Carlo analysis/i);
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText(/Consider these adjustments/i)).toBeInTheDocument();
      expect(screen.getByText(/Increasing your pension contributions/i)).toBeInTheDocument();
    });
  });

  it('displays percentile range', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success_probability: 87,
        safe_withdrawal_rate: 3.8,
        percentiles: {
          p10: 250000,
          p25: 350000,
          p50: 450000,
          p75: 550000,
          p90: 650000,
        },
      }),
    });

    render(<MonteCarloScenario />);

    const runButton = screen.getByText(/Run Monte Carlo analysis/i);
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText(/Worst Case \(10th percentile\)/i)).toBeInTheDocument();
      expect(screen.getByText(/Best Case \(90th percentile\)/i)).toBeInTheDocument();
    });
  });

  it('allows re-running simulation', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        success_probability: 87,
        safe_withdrawal_rate: 3.8,
        expected_value: 450000,
        percentiles: {
          p10: 250000,
          p50: 450000,
          p90: 650000,
        },
      }),
    });

    render(<MonteCarloScenario />);

    const runButton = screen.getByText(/Run Monte Carlo analysis/i);
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText(/87%/)).toBeInTheDocument();
    });

    const runAgainButton = screen.getByText(/Run simulation again/i);
    fireEvent.click(runAgainButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
  });
});
