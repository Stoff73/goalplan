import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { RetirementDashboard } from '../../../src/components/retirement/RetirementDashboard';
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

describe('RetirementDashboard Component', () => {
  const mockProjectionData = {
    retirementAge: 67,
    totalPensionValue: 250000,
    projectedValue: 450000,
    totalIncome: 40000,
    targetIncome: 35000,
    statePension: 11500,
    dcIncome: 22500,
    dbIncome: 6000,
    onTrack: true,
    gap: 0,
    surplus: 5000,
    potGrowthData: [
      { year: 2024, value: 250000 },
      { year: 2030, value: 350000 },
      { year: 2040, value: 450000 },
    ],
  };

  const mockScenarioResults = {
    annualIncome: 38000,
    depletionAge: null,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    fetch.mockImplementation(() => new Promise(() => {}));

    render(<RetirementDashboard />);

    expect(screen.getByText(/Loading your retirement projection/i)).toBeInTheDocument();
  });

  it('renders dashboard with on-track status', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/income-projection')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockProjectionData),
        });
      }
    });

    render(<RetirementDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Your retirement outlook: On track/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/£40,000/)).toBeInTheDocument();
    expect(screen.getByText(/£35,000/)).toBeInTheDocument();
    expect(screen.getByText(/£5,000/)).toBeInTheDocument();
  });

  it('renders dashboard with off-track status and action items', async () => {
    const offTrackData = {
      ...mockProjectionData,
      totalIncome: 28000,
      onTrack: false,
      gap: -7000,
      surplus: 0,
    };

    fetch.mockImplementation((url) => {
      if (url.includes('/income-projection')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(offTrackData),
        });
      }
    });

    render(<RetirementDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Your retirement outlook: Needs attention/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/What you can do to close the gap:/i)).toBeInTheDocument();
    expect(screen.getByText(/Increase your contributions/i)).toBeInTheDocument();
  });

  it('displays income breakdown correctly', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/income-projection')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockProjectionData),
        });
      }
    });

    render(<RetirementDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Where your income comes from/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/State Pension/i)).toBeInTheDocument();
    expect(screen.getByText(/£11,500/)).toBeInTheDocument();

    expect(screen.getByText(/Workplace & Personal Pensions/i)).toBeInTheDocument();
    expect(screen.getByText(/£22,500/)).toBeInTheDocument();

    expect(screen.getByText(/Final Salary Pension/i)).toBeInTheDocument();
    expect(screen.getByText(/£6,000/)).toBeInTheDocument();
  });

  it('handles scenario slider changes', async () => {
    fetch.mockImplementation((url, options) => {
      if (url.includes('/income-projection')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockProjectionData),
        });
      }
      if (url.includes('/drawdown-scenario') && options?.method === 'POST') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockScenarioResults),
        });
      }
    });

    render(<RetirementDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/What if scenarios/i)).toBeInTheDocument();
    });

    // Change retirement age slider
    const ageSlider = screen.getByLabelText(/Retirement age:/i);
    fireEvent.change(ageSlider, { target: { value: '65' } });

    await waitFor(() => {
      expect(screen.getByText(/65/)).toBeInTheDocument();
    });

    // Change withdrawal rate slider
    const rateSlider = screen.getByLabelText(/Withdrawal rate:/i);
    fireEvent.change(rateSlider, { target: { value: '5' } });

    await waitFor(() => {
      expect(screen.getByText(/5%/)).toBeInTheDocument();
    });
  });

  it('displays scenario results after slider change', async () => {
    fetch.mockImplementation((url, options) => {
      if (url.includes('/income-projection')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockProjectionData),
        });
      }
      if (url.includes('/drawdown-scenario')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockScenarioResults),
        });
      }
    });

    render(<RetirementDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/What if scenarios/i)).toBeInTheDocument();
    });

    // Wait for initial scenario calculation
    await waitFor(
      () => {
        expect(screen.getByText(/With these settings:/i)).toBeInTheDocument();
      },
      { timeout: 2000 }
    );

    expect(screen.getByText(/£38,000/)).toBeInTheDocument();
  });

  it('shows pot growth visualization placeholder', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/income-projection')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockProjectionData),
        });
      }
    });

    render(<RetirementDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Your pension pot over time/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Chart visualization would appear here/i)).toBeInTheDocument();
  });

  it('renders empty state when no data', async () => {
    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: true,
        status: 404,
      })
    );

    render(<RetirementDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Plan your retirement income/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Add your pensions to see projections/i)).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: false,
        status: 500,
      })
    );

    render(<RetirementDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Error Loading Projection/i)).toBeInTheDocument();
    });
  });

  it('shows depletion age warning when pot runs out', async () => {
    const depletionScenario = {
      annualIncome: 50000,
      depletionAge: 85,
    };

    fetch.mockImplementation((url, options) => {
      if (url.includes('/income-projection')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockProjectionData),
        });
      }
      if (url.includes('/drawdown-scenario')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(depletionScenario),
        });
      }
    });

    render(<RetirementDashboard />);

    await waitFor(
      () => {
        expect(screen.getByText(/your pot would last until age 85/i)).toBeInTheDocument();
      },
      { timeout: 2000 }
    );
  });
});
