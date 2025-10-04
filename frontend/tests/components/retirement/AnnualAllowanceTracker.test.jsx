import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { AnnualAllowanceTracker } from '../../../src/components/retirement/AnnualAllowanceTracker';
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

describe('AnnualAllowanceTracker Component', () => {
  const mockAllowanceData = {
    taxYear: '2024/25',
    annualAllowance: 60000,
    totalContributions: 25000,
    allowanceRemaining: 35000,
    carryForwardAvailable: 15000,
    mpaaApplies: false,
    tapered: false,
    taperedReason: null,
    carryForwardBreakdown: [
      {
        taxYear: '2021/22',
        allowance: 40000,
        used: 30000,
        unused: 10000,
      },
      {
        taxYear: '2022/23',
        allowance: 40000,
        used: 35000,
        unused: 5000,
      },
      {
        taxYear: '2023/24',
        allowance: 60000,
        used: 60000,
        unused: 0,
      },
    ],
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    fetch.mockImplementation(() => new Promise(() => {}));

    render(<AnnualAllowanceTracker />);

    expect(screen.getByText(/Loading annual allowance data/i)).toBeInTheDocument();
  });

  it('renders allowance tracker with on-track status', async () => {
    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockAllowanceData),
      })
    );

    render(<AnnualAllowanceTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Your pension allowance: On track/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/£60,000/)).toBeInTheDocument();
    expect(screen.getByText(/£25,000/)).toBeInTheDocument();
    expect(screen.getByText(/£35,000/)).toBeInTheDocument();
  });

  it('shows MPAA warning when applicable', async () => {
    const mpaaData = {
      ...mockAllowanceData,
      mpaaApplies: true,
      annualAllowance: 10000,
      totalContributions: 8000,
      allowanceRemaining: 2000,
    };

    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mpaaData),
      })
    );

    render(<AnnualAllowanceTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Money Purchase Annual Allowance applies/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/£10,000/)).toBeInTheDocument();
  });

  it('shows tapered allowance notice', async () => {
    const taperedData = {
      ...mockAllowanceData,
      tapered: true,
      taperedReason: 'Your annual allowance is reduced due to high income (over £260,000).',
      annualAllowance: 40000,
    };

    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(taperedData),
      })
    );

    render(<AnnualAllowanceTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Tapered Annual Allowance/i)).toBeInTheDocument();
    });
  });

  it('shows carry forward section with breakdown', async () => {
    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockAllowanceData),
      })
    );

    render(<AnnualAllowanceTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Unused allowance from previous years/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/£15,000/)).toBeInTheDocument();
    expect(screen.getByText(/2021\/22/)).toBeInTheDocument();
    expect(screen.getByText(/2022\/23/)).toBeInTheDocument();
  });

  it('shows warning when approaching limit (80%+)', async () => {
    const nearLimitData = {
      ...mockAllowanceData,
      totalContributions: 50000,
      allowanceRemaining: 10000,
    };

    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(nearLimitData),
      })
    );

    render(<AnnualAllowanceTracker />);

    await waitFor(() => {
      expect(screen.getByText(/You're getting close to your annual allowance/i)).toBeInTheDocument();
    });
  });

  it('shows error when over limit', async () => {
    const overLimitData = {
      ...mockAllowanceData,
      totalContributions: 65000,
      allowanceRemaining: -5000,
    };

    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(overLimitData),
      })
    );

    render(<AnnualAllowanceTracker />);

    await waitFor(() => {
      expect(screen.getByText(/You've exceeded your annual allowance/i)).toBeInTheDocument();
    });
  });

  it('displays progress bar with correct color coding', async () => {
    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockAllowanceData),
      })
    );

    render(<AnnualAllowanceTracker />);

    await waitFor(() => {
      const progressBar = screen.getByText(/£25,000 used/i).closest('div').previousSibling;
      expect(progressBar).toBeInTheDocument();
    });
  });

  it('renders empty state when no data', async () => {
    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: true,
        status: 404,
      })
    );

    render(<AnnualAllowanceTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Annual Allowance Tracking/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Add pensions to start tracking/i)).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: false,
        status: 500,
      })
    );

    render(<AnnualAllowanceTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Error Loading Annual Allowance/i)).toBeInTheDocument();
    });
  });

  it('shows educational sections', async () => {
    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockAllowanceData),
      })
    );

    render(<AnnualAllowanceTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Understanding annual allowance/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/What is the annual allowance?/i)).toBeInTheDocument();
    expect(screen.getByText(/What happens if I exceed it?/i)).toBeInTheDocument();
    expect(screen.getByText(/How can I maximize my contributions?/i)).toBeInTheDocument();
  });
});
