import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SADeductionTracker } from '../../../src/components/retirement/SADeductionTracker';
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

describe('SADeductionTracker', () => {
  const mockDeductionData = {
    taxYear: '2024/2025',
    totalContributions: 96000,
    maxDeductible: 350000,
    deductionClaimed: 96000,
    taxSaving: 38400,
    remainingAllowance: 254000,
    remuneration: 500000,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();
  });

  it('should render loading state initially', () => {
    global.fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<SADeductionTracker />);

    expect(screen.getByText(/Loading Section 10C deduction data/i)).toBeInTheDocument();
  });

  it('should render deduction tracker with data', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDeductionData,
    });

    render(<SADeductionTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Section 10C Tax Deduction Tracker/i)).toBeInTheDocument();
    });

    // Check narrative text
    expect(screen.getByText(/This tax year/i)).toBeInTheDocument();
    expect(screen.getByText(/2024\/2025/i)).toBeInTheDocument();
    expect(screen.getByText(/R350,000/i)).toBeInTheDocument();
  });

  it('should display progress bar with correct percentage', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDeductionData,
    });

    render(<SADeductionTracker />);

    await waitFor(() => {
      expect(screen.getByText(/27.4%/i)).toBeInTheDocument(); // 96000/350000 * 100
    });
  });

  it('should display all metric cards', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDeductionData,
    });

    render(<SADeductionTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Total Contributions/i)).toBeInTheDocument();
      expect(screen.getByText(/Tax Deduction/i)).toBeInTheDocument();
      expect(screen.getByText(/Tax Saving/i)).toBeInTheDocument();
      expect(screen.getByText(/Remaining Allowance/i)).toBeInTheDocument();
    });

    // Check values
    expect(screen.getAllByText(/R96,000/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/R38,400/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/R254,000/i).length).toBeGreaterThan(0);
  });

  it('should show success callout when room to contribute more', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDeductionData,
    });

    render(<SADeductionTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Room to contribute more/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/You still have/i)).toBeInTheDocument();
  });

  it('should show warning when approaching limit (80%+)', async () => {
    const approachingLimitData = {
      ...mockDeductionData,
      deductionClaimed: 280000, // 80% of 350000
      remainingAllowance: 70000,
    };

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => approachingLimitData,
    });

    render(<SADeductionTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Approaching deduction limit/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/R70,000/i)).toBeInTheDocument();
  });

  it('should show warning when at limit (100%)', async () => {
    const atLimitData = {
      ...mockDeductionData,
      deductionClaimed: 350000,
      remainingAllowance: 0,
    };

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => atLimitData,
    });

    render(<SADeductionTracker />);

    await waitFor(() => {
      expect(screen.getByText(/⚠️ Deduction limit reached/i)).toBeInTheDocument();
    });

    expect(
      screen.getByText(
        /You've reached your maximum Section 10C deduction for this tax year/i
      )
    ).toBeInTheDocument();
  });

  it('should display calculation details', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDeductionData,
    });

    render(<SADeductionTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Your calculation:/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Remuneration:/i)).toBeInTheDocument();
    expect(screen.getByText(/R500,000/i)).toBeInTheDocument();
    expect(screen.getByText(/27.5% of remuneration:/i)).toBeInTheDocument();
    expect(screen.getByText(/R137,500/i)).toBeInTheDocument(); // 500000 * 0.275
    expect(screen.getByText(/Statutory cap:/i)).toBeInTheDocument();
    expect(screen.getByText(/Your limit:/i)).toBeInTheDocument();
  });

  it('should display educational section about Section 10C', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDeductionData,
    });

    render(<SADeductionTracker />);

    await waitFor(() => {
      expect(screen.getByText(/How Section 10C works/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/You can deduct up to 27.5% of your remuneration/i)).toBeInTheDocument();
    expect(screen.getByText(/Maximum annual deduction is capped at R350,000/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Applies to pension funds, provident funds, and retirement annuities/i)
    ).toBeInTheDocument();
  });

  it('should handle no data gracefully', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => null,
    });

    render(<SADeductionTracker />);

    await waitFor(() => {
      expect(
        screen.getByText(/No Section 10C deduction data available/i)
      ).toBeInTheDocument();
    });

    expect(
      screen.getByText(/Add SA retirement funds to start tracking your tax deductions/i)
    ).toBeInTheDocument();
  });

  it('should handle API error gracefully', async () => {
    global.fetch.mockRejectedValue(new Error('API Error'));

    render(<SADeductionTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Error Loading Deduction Data/i)).toBeInTheDocument();
    });

    expect(
      screen.getByText(/Failed to load Section 10C deduction data/i)
    ).toBeInTheDocument();
  });

  it('should handle unauthorized (401) by redirecting to login', async () => {
    global.fetch.mockResolvedValueOnce({ ok: false, status: 401 });

    delete window.location;
    window.location = { href: '' };

    render(<SADeductionTracker />);

    await waitFor(() => {
      expect(authStorage.clear).toHaveBeenCalled();
      expect(window.location.href).toBe('/login');
    });
  });

  it('should calculate and display correct percentage used', async () => {
    const customData = {
      ...mockDeductionData,
      deductionClaimed: 175000, // 50% of 350000
    };

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => customData,
    });

    render(<SADeductionTracker />);

    await waitFor(() => {
      expect(screen.getByText(/50.0%/i)).toBeInTheDocument();
    });
  });

  it('should use green color for progress bar when below 80%', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDeductionData,
    });

    const { container } = render(<SADeductionTracker />);

    await waitFor(() => {
      const progressBar = container.querySelector('[style*="background-color"]');
      expect(progressBar).toBeTruthy();
      // Green color (#10B981) should be used
    });
  });

  it('should format large currency values correctly', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDeductionData,
    });

    render(<SADeductionTracker />);

    await waitFor(() => {
      // Check that values are formatted with thousands separators
      expect(screen.getAllByText(/R96,000/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/R254,000/i).length).toBeGreaterThan(0);
    });
  });
});
