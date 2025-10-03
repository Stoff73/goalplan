import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { TaxCalculators } from '../../src/components/tax/TaxCalculators';

// Mock the calculator components
jest.mock('../../src/components/tax/SRTCalculator', () => ({
  SRTCalculator: () => <div>SRT Calculator Component</div>,
}));

jest.mock('../../src/components/tax/SAPresenceCalculator', () => ({
  SAPresenceCalculator: () => <div>SA Presence Calculator Component</div>,
}));

describe('TaxCalculators', () => {
  test('renders with UK SRT calculator tab active by default', () => {
    render(<TaxCalculators />);

    expect(screen.getByText(/tax residency calculators/i)).toBeInTheDocument();
    expect(screen.getByText(/UK Statutory Residence Test/i)).toBeInTheDocument();
    expect(screen.getByText(/SRT Calculator Component/i)).toBeInTheDocument();
  });

  test('switches to SA Presence Test calculator when tab is clicked', () => {
    render(<TaxCalculators />);

    const saTab = screen.getByText(/SA Physical Presence Test/i);
    fireEvent.click(saTab);

    expect(screen.getByText(/SA Presence Calculator Component/i)).toBeInTheDocument();
    expect(screen.queryByText(/SRT Calculator Component/i)).not.toBeInTheDocument();
  });

  test('switches back to UK SRT calculator when tab is clicked', () => {
    render(<TaxCalculators />);

    // Switch to SA tab
    const saTab = screen.getByText(/SA Physical Presence Test/i);
    fireEvent.click(saTab);

    // Switch back to UK tab
    const ukTab = screen.getByText(/UK Statutory Residence Test/i);
    fireEvent.click(ukTab);

    expect(screen.getByText(/SRT Calculator Component/i)).toBeInTheDocument();
    expect(screen.queryByText(/SA Presence Calculator Component/i)).not.toBeInTheDocument();
  });

  test('renders helpful description text', () => {
    render(<TaxCalculators />);

    expect(
      screen.getByText(/use these calculators to determine your tax residency status/i)
    ).toBeInTheDocument();
  });
});
