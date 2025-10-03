import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { DeemedDomicileSection } from '../../src/components/tax/DeemedDomicileSection';

describe('DeemedDomicileSection', () => {
  const mockDeemedDomicileData = {
    uk_deemed_domicile: false,
    uk_resident_years_in_last_20: 5,
    deemed_domicile_reason: null,
  };

  const mockDeemedDomicileActive = {
    uk_deemed_domicile: true,
    uk_resident_years_in_last_20: 15,
    deemed_domicile_reason: '15 of last 20 years UK resident',
    deemed_domicile_date: '2023-04-06',
  };

  test('renders loading state', () => {
    render(<DeemedDomicileSection deemedDomicileData={null} loading={true} />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('renders info message when no data is available', () => {
    render(<DeemedDomicileSection deemedDomicileData={null} loading={false} />);

    expect(screen.getByText(/set up your tax status/i)).toBeInTheDocument();
  });

  test('renders not deemed domiciled status correctly', () => {
    render(<DeemedDomicileSection deemedDomicileData={mockDeemedDomicileData} loading={false} />);

    expect(screen.getByText(/not deemed UK domiciled/i)).toBeInTheDocument();
    expect(screen.getByText(/5 of the last 20 years/i)).toBeInTheDocument();
  });

  test('shows progress bar for non-deemed domiciled users', () => {
    render(<DeemedDomicileSection deemedDomicileData={mockDeemedDomicileData} loading={false} />);

    expect(screen.getByText(/progress to deemed domicile/i)).toBeInTheDocument();
    expect(screen.getByText(/5 \/ 15 years/i)).toBeInTheDocument();
  });

  test('renders deemed domiciled status with warning', () => {
    render(<DeemedDomicileSection deemedDomicileData={mockDeemedDomicileActive} loading={false} />);

    expect(screen.getByText(/deemed UK domiciled/i)).toBeInTheDocument();
    expect(screen.getByText(/worldwide estate/i)).toBeInTheDocument();
  });

  test('shows deemed domicile date when provided', () => {
    render(<DeemedDomicileSection deemedDomicileData={mockDeemedDomicileActive} loading={false} />);

    expect(screen.getByText(/became deemed UK domiciled from/i)).toBeInTheDocument();
  });

  test('toggles explanation section', () => {
    render(<DeemedDomicileSection deemedDomicileData={mockDeemedDomicileData} loading={false} />);

    const explanationButton = screen.getByText(/what is deemed domicile/i);
    fireEvent.click(explanationButton);

    expect(screen.getByText(/understanding deemed domicile/i)).toBeInTheDocument();
    expect(screen.getByText(/why it matters/i)).toBeInTheDocument();

    // Hide explanation
    fireEvent.click(explanationButton);
    expect(screen.queryByText(/understanding deemed domicile/i)).not.toBeInTheDocument();
  });

  test('calculates years until deemed domicile correctly', () => {
    render(<DeemedDomicileSection deemedDomicileData={mockDeemedDomicileData} loading={false} />);

    expect(screen.getByText(/need 10 more years/i)).toBeInTheDocument();
  });

  test('does not show progress bar for deemed domiciled users', () => {
    render(<DeemedDomicileSection deemedDomicileData={mockDeemedDomicileActive} loading={false} />);

    expect(screen.queryByText(/progress to deemed domicile/i)).not.toBeInTheDocument();
  });
});
