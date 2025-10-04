import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { GiftTracker } from '../../../src/components/iht/GiftTracker';
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

describe('GiftTracker Component', () => {
  const mockGiftsData = {
    totalGiftsLast7Years: 25000,
    activePETCount: 3,
    potentialIHTIfDeathToday: 6000,
    gifts: [
      {
        id: 'gift-1',
        giftDate: '2022-05-15',
        recipientName: 'John Smith',
        recipientRelationship: 'CHILD',
        giftValue: 10000,
        classification: 'PET',
        yearsElapsed: 2.4,
        yearsRemaining: 4.6,
        potentialIHT: 2000,
      },
      {
        id: 'gift-2',
        giftDate: '2020-08-20',
        recipientName: 'Jane Doe',
        recipientRelationship: 'GRANDCHILD',
        giftValue: 8000,
        classification: 'PET',
        yearsElapsed: 4.2,
        yearsRemaining: 2.8,
        potentialIHT: 1600,
      },
      {
        id: 'gift-3',
        giftDate: '2019-03-10',
        recipientName: 'Charity ABC',
        recipientRelationship: 'CHARITY',
        giftValue: 7000,
        classification: 'CHARITY_EXEMPT',
        yearsElapsed: 5.6,
        yearsRemaining: 1.4,
        potentialIHT: 0,
      },
    ],
    annualExemption: {
      currentYear: 2024,
      limit: 3000,
      used: 1500,
      available: 1500,
      carriedForward: 3000,
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    fetch.mockImplementation(() => new Promise(() => {}));

    render(<GiftTracker />);

    expect(screen.getByText(/Loading your gift history/i)).toBeInTheDocument();
  });

  it('renders gift tracker with data', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/seven-year-summary')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockGiftsData),
        });
      }
    });

    render(<GiftTracker />);

    await waitFor(() => {
      expect(screen.getByText(/You've given/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/£25,000/)).toBeInTheDocument();
    expect(screen.getByText(/in the last 7 years/i)).toBeInTheDocument();
  });

  it('displays gift timeline visualization', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/seven-year-summary')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockGiftsData),
        });
      }
    });

    render(<GiftTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Your 7-year gift timeline/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/0-3 years \(No relief\)/i)).toBeInTheDocument();
    expect(screen.getByText(/3-5 years \(20-40% relief\)/i)).toBeInTheDocument();
    expect(screen.getByText(/5-7 years \(60-80% relief\)/i)).toBeInTheDocument();
    expect(screen.getByText(/7\+ years \(Exempt\)/i)).toBeInTheDocument();
  });

  it('renders gift list table with all gifts', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/seven-year-summary')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockGiftsData),
        });
      }
    });

    render(<GiftTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Your lifetime gifts/i)).toBeInTheDocument();
    });

    expect(screen.getByText('John Smith')).toBeInTheDocument();
    expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    expect(screen.getByText('Charity ABC')).toBeInTheDocument();
  });

  it('displays years remaining and taper relief correctly', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/seven-year-summary')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockGiftsData),
        });
      }
    });

    render(<GiftTracker />);

    await waitFor(() => {
      expect(screen.getByText(/4.6 years/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/2.8 years/i)).toBeInTheDocument();
    expect(screen.getByText(/1.4 years/i)).toBeInTheDocument();
  });

  it('displays potential IHT for each gift', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/seven-year-summary')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockGiftsData),
        });
      }
    });

    render(<GiftTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Your lifetime gifts/i)).toBeInTheDocument();
    });

    // Find all cells with currency values
    const potentialTaxCells = screen.getAllByText(/£[0-9,]+/);
    expect(potentialTaxCells.length).toBeGreaterThan(0);
  });

  it('renders annual exemption tracker', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/seven-year-summary')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockGiftsData),
        });
      }
    });

    render(<GiftTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Your tax-free allowances/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Annual exemption \(2024\/25\)/i)).toBeInTheDocument();
    expect(screen.getByText(/£1,500 of £3,000 remaining/i)).toBeInTheDocument();
    expect(screen.getByText(/Carried forward from last year/i)).toBeInTheDocument();
    expect(screen.getByText(/£3,000/)).toBeInTheDocument();
  });

  it('renders smart gifting strategies', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/seven-year-summary')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockGiftsData),
        });
      }
    });

    render(<GiftTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Smart gifting strategies/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Use your £3,000 annual exemption/i)).toBeInTheDocument();
    expect(screen.getByText(/Give £250 to as many people as you like/i)).toBeInTheDocument();
    expect(screen.getByText(/Wedding gifts are exempt/i)).toBeInTheDocument();
  });

  it('handles delete gift', async () => {
    window.confirm = jest.fn(() => true);

    fetch.mockImplementation((url, options) => {
      if (url.includes('/seven-year-summary') && !options?.method) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockGiftsData),
        });
      }
      if (url.includes('/gifts/') && options?.method === 'DELETE') {
        return Promise.resolve({ ok: true });
      }
      return Promise.reject(new Error('Not found'));
    });

    render(<GiftTracker />);

    await waitFor(() => {
      expect(screen.getByText('John Smith')).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByText(/Delete/i);
    fireEvent.click(deleteButtons[0]);

    expect(window.confirm).toHaveBeenCalledWith(
      'Are you sure you want to delete this gift?'
    );

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/gifts/gift-1'),
        expect.objectContaining({ method: 'DELETE' })
      );
    });
  });

  it('renders empty state when no gifts', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/seven-year-summary')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ gifts: [] }),
        });
      }
    });

    render(<GiftTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Track your lifetime gifts/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Record Your First Gift/i)).toBeInTheDocument();
  });

  it('handles error state', async () => {
    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: false,
        status: 500,
      })
    );

    render(<GiftTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Error Loading Gifts/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Try Again/i)).toBeInTheDocument();
  });

  it('handles 401 unauthorized and redirects to login', async () => {
    delete window.location;
    window.location = { href: '' };

    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: false,
        status: 401,
      })
    );

    render(<GiftTracker />);

    await waitFor(() => {
      expect(authStorage.clear).toHaveBeenCalled();
      expect(window.location.href).toBe('/login');
    });
  });

  it('displays educational tooltip for 7-year rule', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/seven-year-summary')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockGiftsData),
        });
      }
    });

    render(<GiftTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Tell me more about the 7-year rule:/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/potentially exempt transfer/i)).toBeInTheDocument();
  });

  it('displays educational tooltip for exemptions', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('/seven-year-summary')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockGiftsData),
        });
      }
    });

    render(<GiftTracker />);

    await waitFor(() => {
      expect(screen.getByText(/Tell me more about exemptions:/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/You can give away £3,000 each year/i)).toBeInTheDocument();
  });
});
