import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { CurrentTaxStatusSection } from '../../src/components/tax/CurrentTaxStatusSection';

describe('CurrentTaxStatusSection', () => {
  const mockOnEdit = jest.fn();

  const mockTaxStatus = {
    id: '1',
    effective_from: '2024-04-06',
    effective_to: null,
    uk_tax_resident: true,
    sa_tax_resident: false,
    domicile: 'UK_DOMICILED',
    domicile_of_origin: 'UK',
    uk_residence_basis: 'ARISING',
    dual_resident: false,
    dta_tie_breaker_result: null,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state', () => {
    render(<CurrentTaxStatusSection taxStatus={null} onEdit={mockOnEdit} loading={true} />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('renders no status message when taxStatus is null', () => {
    render(<CurrentTaxStatusSection taxStatus={null} onEdit={mockOnEdit} loading={false} />);

    expect(screen.getByText(/haven't set up your tax status yet/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /set up your tax status/i })).toBeInTheDocument();
  });

  test('calls onEdit when setup button is clicked', () => {
    render(<CurrentTaxStatusSection taxStatus={null} onEdit={mockOnEdit} loading={false} />);

    const setupButton = screen.getByRole('button', { name: /set up your tax status/i });
    fireEvent.click(setupButton);

    expect(mockOnEdit).toHaveBeenCalledTimes(1);
  });

  test('renders UK resident status correctly', () => {
    render(<CurrentTaxStatusSection taxStatus={mockTaxStatus} onEdit={mockOnEdit} loading={false} />);

    expect(screen.getByText(/UK Tax Residency/i)).toBeInTheDocument();
    expect(screen.getByText(/Resident/)).toBeInTheDocument();
    expect(screen.getByText(/considered a UK tax resident/i)).toBeInTheDocument();
  });

  test('renders non-resident status correctly', () => {
    const nonResidentStatus = { ...mockTaxStatus, uk_tax_resident: false };
    render(<CurrentTaxStatusSection taxStatus={nonResidentStatus} onEdit={mockOnEdit} loading={false} />);

    expect(screen.getByText(/Non-Resident/)).toBeInTheDocument();
    expect(screen.getByText(/not a UK tax resident/i)).toBeInTheDocument();
  });

  test('shows dual residency warning when both UK and SA resident', () => {
    const dualResidentStatus = {
      ...mockTaxStatus,
      uk_tax_resident: true,
      sa_tax_resident: true,
      dual_resident: true,
      dta_tie_breaker_result: 'UK_RESIDENT',
    };

    render(<CurrentTaxStatusSection taxStatus={dualResidentStatus} onEdit={mockOnEdit} loading={false} />);

    expect(screen.getByText(/resident in both the UK and South Africa/i)).toBeInTheDocument();
  });

  test('shows remittance basis alert when applicable', () => {
    const remittanceStatus = {
      ...mockTaxStatus,
      domicile: 'NON_UK_DOMICILED',
      uk_residence_basis: 'REMITTANCE',
    };

    render(<CurrentTaxStatusSection taxStatus={remittanceStatus} onEdit={mockOnEdit} loading={false} />);

    expect(screen.getByText(/using the remittance basis/i)).toBeInTheDocument();
  });

  test('toggles explanation sections', () => {
    render(<CurrentTaxStatusSection taxStatus={mockTaxStatus} onEdit={mockOnEdit} loading={false} />);

    const domicileButton = screen.getByText(/what is domicile/i);
    fireEvent.click(domicileButton);

    expect(screen.getByText(/permanent home country/i)).toBeInTheDocument();

    // Click again to hide
    fireEvent.click(domicileButton);
    expect(screen.queryByText(/permanent home country/i)).not.toBeInTheDocument();
  });

  test('calls onEdit when update button is clicked', () => {
    render(<CurrentTaxStatusSection taxStatus={mockTaxStatus} onEdit={mockOnEdit} loading={false} />);

    const updateButton = screen.getByRole('button', { name: /update/i });
    fireEvent.click(updateButton);

    expect(mockOnEdit).toHaveBeenCalledTimes(1);
  });
});
