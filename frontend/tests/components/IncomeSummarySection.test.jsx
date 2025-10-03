import React from 'react';
import { render, screen } from '@testing-library/react';
import { IncomeSummarySection } from '../../src/components/income/IncomeSummarySection';

describe('IncomeSummarySection', () => {
  const mockSummary = {
    total_income_gbp: 52500,
    total_income_zar: 1215000,
    total_tax_withheld_gbp: 12500,
    foreign_income_gbp: 7500,
    foreign_tax_credits_gbp: 1200,
    by_type: {
      employment: 45000,
      rental: 7500,
    },
    by_country: {
      UK: 45000,
      US: 7500,
    },
  };

  it('renders summary with data', () => {
    render(
      <IncomeSummarySection
        summary={mockSummary}
        taxYear="2024/25"
        country="UK"
        loading={false}
      />
    );

    expect(screen.getByText(/Your income summary for 2024\/25/i)).toBeInTheDocument();
    expect(screen.getByText(/£52,500.00/)).toBeInTheDocument();
    expect(screen.getByText(/R1,215,000.00/)).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(
      <IncomeSummarySection
        summary={null}
        taxYear="2024/25"
        country="UK"
        loading={true}
      />
    );

    expect(screen.getByText(/Loading income summary/i)).toBeInTheDocument();
  });

  it('shows empty state when no income', () => {
    render(
      <IncomeSummarySection
        summary={{ total_income_gbp: 0 }}
        taxYear="2024/25"
        country="UK"
        loading={false}
      />
    );

    expect(screen.getByText(/No income recorded for this tax year yet/i)).toBeInTheDocument();
  });

  it('displays tax withheld information', () => {
    render(
      <IncomeSummarySection
        summary={mockSummary}
        taxYear="2024/25"
        country="UK"
        loading={false}
      />
    );

    expect(screen.getByText(/£12,500.00/)).toBeInTheDocument();
    expect(screen.getByText(/Tax Already Withheld/i)).toBeInTheDocument();
  });

  it('displays foreign income callout', () => {
    render(
      <IncomeSummarySection
        summary={mockSummary}
        taxYear="2024/25"
        country="UK"
        loading={false}
      />
    );

    expect(screen.getByText(/Foreign income detected/i)).toBeInTheDocument();
    expect(screen.getByText(/Double Tax Agreement/i)).toBeInTheDocument();
  });

  it('displays income breakdown by type', () => {
    render(
      <IncomeSummarySection
        summary={mockSummary}
        taxYear="2024/25"
        country="UK"
        loading={false}
      />
    );

    expect(screen.getByText(/Income by Type/i)).toBeInTheDocument();
    expect(screen.getByText(/Employment/i)).toBeInTheDocument();
    expect(screen.getByText(/Rental Income/i)).toBeInTheDocument();
  });

  it('displays income breakdown by country', () => {
    render(
      <IncomeSummarySection
        summary={mockSummary}
        taxYear="2024/25"
        country="UK"
        loading={false}
      />
    );

    expect(screen.getByText(/Income by Source Country/i)).toBeInTheDocument();
    expect(screen.getByText(/United Kingdom/i)).toBeInTheDocument();
    expect(screen.getByText(/United States/i)).toBeInTheDocument();
  });
});
