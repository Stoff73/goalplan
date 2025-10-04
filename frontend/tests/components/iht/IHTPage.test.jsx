import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { IHTPage } from '../../../src/pages/IHTPage';

// Mock the child components
jest.mock('../../../src/components/iht/EstateDashboard', () => ({
  EstateDashboard: () => <div data-testid="estate-dashboard">Estate Dashboard</div>,
}));

jest.mock('../../../src/components/iht/GiftTracker', () => ({
  GiftTracker: () => <div data-testid="gift-tracker">Gift Tracker</div>,
}));

describe('IHTPage Component', () => {
  it('renders page header and title', () => {
    render(<IHTPage />);

    expect(screen.getByText(/Inheritance Tax Planning/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Understand your estate value and potential inheritance tax liability/i)
    ).toBeInTheDocument();
  });

  it('renders all tab navigation items', () => {
    render(<IHTPage />);

    expect(screen.getByText('Estate Calculation')).toBeInTheDocument();
    expect(screen.getByText('Lifetime Gifts')).toBeInTheDocument();
    expect(screen.getByText('SA Estate Duty')).toBeInTheDocument();
  });

  it('shows Estate Calculation tab by default', () => {
    render(<IHTPage />);

    expect(screen.getByTestId('estate-dashboard')).toBeInTheDocument();
    expect(screen.queryByTestId('gift-tracker')).not.toBeInTheDocument();
  });

  it('switches to Lifetime Gifts tab when clicked', () => {
    render(<IHTPage />);

    const giftsTab = screen.getByText('Lifetime Gifts');
    fireEvent.click(giftsTab);

    expect(screen.queryByTestId('estate-dashboard')).not.toBeInTheDocument();
    expect(screen.getByTestId('gift-tracker')).toBeInTheDocument();
  });

  it('switches to SA Estate Duty tab and shows coming soon message', () => {
    render(<IHTPage />);

    const saTab = screen.getByText('SA Estate Duty');
    fireEvent.click(saTab);

    expect(screen.queryByTestId('estate-dashboard')).not.toBeInTheDocument();
    expect(screen.queryByTestId('gift-tracker')).not.toBeInTheDocument();
    expect(screen.getByText(/SA Estate Duty Coming Soon/i)).toBeInTheDocument();
  });

  it('preserves state when switching between tabs', () => {
    render(<IHTPage />);

    // Start on Estate tab
    expect(screen.getByTestId('estate-dashboard')).toBeInTheDocument();

    // Switch to Gifts tab
    const giftsTab = screen.getByText('Lifetime Gifts');
    fireEvent.click(giftsTab);
    expect(screen.getByTestId('gift-tracker')).toBeInTheDocument();

    // Switch back to Estate tab
    const estateTab = screen.getByText('Estate Calculation');
    fireEvent.click(estateTab);
    expect(screen.getByTestId('estate-dashboard')).toBeInTheDocument();
  });

  it('applies active styling to current tab', () => {
    render(<IHTPage />);

    const estateTab = screen.getByText('Estate Calculation');
    const giftsTab = screen.getByText('Lifetime Gifts');

    // Estate tab should be active initially
    expect(estateTab).toHaveStyle({ color: '#2563EB' });
    expect(giftsTab).toHaveStyle({ color: '#64748B' });

    // Click Gifts tab
    fireEvent.click(giftsTab);

    // Gifts tab should now be active
    expect(giftsTab).toHaveStyle({ color: '#2563EB' });
  });

  it('renders responsive container', () => {
    const { container } = render(<IHTPage />);

    const mainContainer = container.firstChild;
    expect(mainContainer).toHaveStyle({
      maxWidth: '1280px',
      margin: '0 auto',
    });
  });

  it('has accessible tab navigation', () => {
    render(<IHTPage />);

    const estateTab = screen.getByText('Estate Calculation');
    const giftsTab = screen.getByText('Lifetime Gifts');
    const saTab = screen.getByText('SA Estate Duty');

    // All tabs should be clickable
    expect(estateTab).toHaveStyle({ cursor: 'pointer' });
    expect(giftsTab).toHaveStyle({ cursor: 'pointer' });
    expect(saTab).toHaveStyle({ cursor: 'pointer' });
  });
});
