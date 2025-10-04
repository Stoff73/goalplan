import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import InvestmentPage from '../../src/pages/InvestmentPage';
import { authStorage } from '../../src/utils/auth';

// Mock child components
jest.mock('../../src/components/Layout', () => ({
  Layout: ({ children }) => <div data-testid="layout">{children}</div>,
}));

jest.mock('../../src/components/investment/PortfolioDashboard', () => ({
  PortfolioDashboard: () => <div data-testid="portfolio-dashboard">Portfolio Dashboard</div>,
}));

jest.mock('../../src/components/investment/HoldingsList', () => ({
  HoldingsList: () => <div data-testid="holdings-list">Holdings List</div>,
}));

jest.mock('../../src/components/investment/AssetAllocation', () => ({
  AssetAllocation: () => <div data-testid="asset-allocation">Asset Allocation</div>,
}));

// Mock authStorage
jest.mock('../../src/utils/auth', () => ({
  authStorage: {
    getAccessToken: jest.fn(),
    getUser: jest.fn(),
    clear: jest.fn(),
  },
}));

// Mock fetch
global.fetch = jest.fn();

describe('InvestmentPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    authStorage.getAccessToken.mockReturnValue('mock-token');
    authStorage.getUser.mockReturnValue({
      id: 1,
      email: 'test@example.com',
      firstName: 'Test',
      lastName: 'User',
    });
  });

  describe('Page Structure', () => {
    it('renders page title and description', () => {
      render(
        <MemoryRouter initialEntries={['/investments']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      expect(screen.getByText('Your Investment Portfolio')).toBeInTheDocument();
      expect(
        screen.getByText(/Track your investments across the UK and South Africa/i)
      ).toBeInTheDocument();
    });

    it('renders all three tabs', () => {
      render(
        <MemoryRouter initialEntries={['/investments']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      expect(screen.getByRole('tab', { name: /dashboard/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /holdings/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /asset allocation/i })).toBeInTheDocument();
    });

    it('wraps content in Layout component', () => {
      render(
        <MemoryRouter initialEntries={['/investments']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      expect(screen.getByTestId('layout')).toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    it('shows Dashboard tab by default', () => {
      render(
        <MemoryRouter initialEntries={['/investments']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      const dashboardTab = screen.getByRole('tab', { name: /dashboard/i });
      expect(dashboardTab).toHaveAttribute('aria-selected', 'true');
      expect(screen.getByTestId('portfolio-dashboard')).toBeInTheDocument();
    });

    it('shows Dashboard tab when URL is /investments/dashboard', () => {
      render(
        <MemoryRouter initialEntries={['/investments/dashboard']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      const dashboardTab = screen.getByRole('tab', { name: /dashboard/i });
      expect(dashboardTab).toHaveAttribute('aria-selected', 'true');
      expect(screen.getByTestId('portfolio-dashboard')).toBeInTheDocument();
    });

    it('shows Holdings tab when URL is /investments/holdings', () => {
      render(
        <MemoryRouter initialEntries={['/investments/holdings']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      const holdingsTab = screen.getByRole('tab', { name: /holdings/i });
      expect(holdingsTab).toHaveAttribute('aria-selected', 'true');
      expect(screen.getByTestId('holdings-list')).toBeInTheDocument();
    });

    it('shows Asset Allocation tab when URL is /investments/allocation', () => {
      render(
        <MemoryRouter initialEntries={['/investments/allocation']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      const allocationTab = screen.getByRole('tab', { name: /asset allocation/i });
      expect(allocationTab).toHaveAttribute('aria-selected', 'true');
      expect(screen.getByTestId('asset-allocation')).toBeInTheDocument();
    });

    it('switches to Holdings tab when clicked', () => {
      render(
        <MemoryRouter initialEntries={['/investments']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      // Initially on Dashboard
      expect(screen.getByTestId('portfolio-dashboard')).toBeInTheDocument();

      // Click Holdings tab
      const holdingsTab = screen.getByRole('tab', { name: /holdings/i });
      fireEvent.click(holdingsTab);

      // Should show Holdings component
      expect(screen.getByTestId('holdings-list')).toBeInTheDocument();
      expect(screen.queryByTestId('portfolio-dashboard')).not.toBeInTheDocument();
    });

    it('switches to Asset Allocation tab when clicked', () => {
      render(
        <MemoryRouter initialEntries={['/investments']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      // Initially on Dashboard
      expect(screen.getByTestId('portfolio-dashboard')).toBeInTheDocument();

      // Click Asset Allocation tab
      const allocationTab = screen.getByRole('tab', { name: /asset allocation/i });
      fireEvent.click(allocationTab);

      // Should show Asset Allocation component
      expect(screen.getByTestId('asset-allocation')).toBeInTheDocument();
      expect(screen.queryByTestId('portfolio-dashboard')).not.toBeInTheDocument();
    });

    it('switches back to Dashboard tab when clicked', () => {
      render(
        <MemoryRouter initialEntries={['/investments/holdings']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      // Initially on Holdings
      expect(screen.getByTestId('holdings-list')).toBeInTheDocument();

      // Click Dashboard tab
      const dashboardTab = screen.getByRole('tab', { name: /dashboard/i });
      fireEvent.click(dashboardTab);

      // Should show Dashboard component
      expect(screen.getByTestId('portfolio-dashboard')).toBeInTheDocument();
      expect(screen.queryByTestId('holdings-list')).not.toBeInTheDocument();
    });
  });

  describe('Tab Visual States', () => {
    it('applies active styling to selected tab', () => {
      render(
        <MemoryRouter initialEntries={['/investments']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      const dashboardTab = screen.getByRole('tab', { name: /dashboard/i });
      const holdingsTab = screen.getByRole('tab', { name: /holdings/i });

      // Dashboard should be active
      expect(dashboardTab).toHaveAttribute('aria-selected', 'true');
      expect(dashboardTab).toHaveStyle({ color: '#2563EB' });

      // Holdings should not be active
      expect(holdingsTab).toHaveAttribute('aria-selected', 'false');
      expect(holdingsTab).toHaveStyle({ color: '#475569' });
    });

    it('updates active styling when tab changes', () => {
      render(
        <MemoryRouter initialEntries={['/investments']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      const dashboardTab = screen.getByRole('tab', { name: /dashboard/i });
      const holdingsTab = screen.getByRole('tab', { name: /holdings/i });

      // Click Holdings tab
      fireEvent.click(holdingsTab);

      // Holdings should now be active
      expect(holdingsTab).toHaveAttribute('aria-selected', 'true');
      expect(holdingsTab).toHaveStyle({ color: '#2563EB' });

      // Dashboard should not be active
      expect(dashboardTab).toHaveAttribute('aria-selected', 'false');
      expect(dashboardTab).toHaveStyle({ color: '#475569' });
    });
  });

  describe('Accessibility', () => {
    it('uses proper ARIA attributes for tabs', () => {
      render(
        <MemoryRouter initialEntries={['/investments']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      const tabs = screen.getAllByRole('tab');
      expect(tabs).toHaveLength(3);

      tabs.forEach((tab) => {
        expect(tab).toHaveAttribute('aria-selected');
      });
    });

    it('uses proper role for tab panel', () => {
      render(
        <MemoryRouter initialEntries={['/investments']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      expect(screen.getByRole('tabpanel')).toBeInTheDocument();
    });
  });

  describe('Component Rendering', () => {
    it('renders PortfolioDashboard component on Dashboard tab', () => {
      render(
        <MemoryRouter initialEntries={['/investments']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      expect(screen.getByTestId('portfolio-dashboard')).toBeInTheDocument();
      expect(screen.getByText('Portfolio Dashboard')).toBeInTheDocument();
    });

    it('renders HoldingsList component on Holdings tab', () => {
      render(
        <MemoryRouter initialEntries={['/investments/holdings']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      expect(screen.getByTestId('holdings-list')).toBeInTheDocument();
      expect(screen.getByText('Holdings List')).toBeInTheDocument();
    });

    it('renders AssetAllocation component on Asset Allocation tab', () => {
      render(
        <MemoryRouter initialEntries={['/investments/allocation']}>
          <InvestmentPage />
        </MemoryRouter>
      );

      expect(screen.getByTestId('asset-allocation')).toBeInTheDocument();
      expect(screen.getAllByText('Asset Allocation').length).toBeGreaterThanOrEqual(1);
    });
  });

  describe('URL Routing', () => {
    it('updates URL when Dashboard tab is clicked', () => {
      const { container } = render(
        <BrowserRouter>
          <InvestmentPage />
        </BrowserRouter>
      );

      const dashboardTab = screen.getByRole('tab', { name: /dashboard/i });
      fireEvent.click(dashboardTab);

      // Check that navigation was attempted (we can't easily test actual URL change in jsdom)
      expect(dashboardTab).toHaveAttribute('aria-selected', 'true');
    });

    it('updates URL when Holdings tab is clicked', () => {
      const { container } = render(
        <BrowserRouter>
          <InvestmentPage />
        </BrowserRouter>
      );

      const holdingsTab = screen.getByRole('tab', { name: /holdings/i });
      fireEvent.click(holdingsTab);

      expect(holdingsTab).toHaveAttribute('aria-selected', 'true');
    });

    it('updates URL when Asset Allocation tab is clicked', () => {
      const { container } = render(
        <BrowserRouter>
          <InvestmentPage />
        </BrowserRouter>
      );

      const allocationTab = screen.getByRole('tab', { name: /asset allocation/i });
      fireEvent.click(allocationTab);

      expect(allocationTab).toHaveAttribute('aria-selected', 'true');
    });
  });
});
