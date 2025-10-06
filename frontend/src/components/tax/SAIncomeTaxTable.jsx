import React from 'react';

export function SAIncomeTaxTable() {
  const taxBands = [
    {
      band: 'Band 1',
      income: 'R0 - R237,100',
      rate: '18%',
      taxOnBand: 'Up to R42,678',
      description: 'Entry-level tax bracket'
    },
    {
      band: 'Band 2',
      income: 'R237,101 - R370,500',
      rate: '26%',
      taxOnBand: 'R42,678 + 26% above R237,100',
      description: 'Standard rate for middle income'
    },
    {
      band: 'Band 3',
      income: 'R370,501 - R512,800',
      rate: '31%',
      taxOnBand: 'R77,362 + 31% above R370,500',
      description: 'Higher middle income bracket'
    },
    {
      band: 'Band 4',
      income: 'R512,801 - R673,000',
      rate: '36%',
      taxOnBand: 'R121,475 + 36% above R512,800',
      description: 'Upper middle income bracket'
    },
    {
      band: 'Band 5',
      income: 'R673,001 - R857,900',
      rate: '39%',
      taxOnBand: 'R179,147 + 39% above R673,000',
      description: 'High income earners'
    },
    {
      band: 'Band 6',
      income: 'R857,901 - R1,817,000',
      rate: '41%',
      taxOnBand: 'R251,258 + 41% above R857,900',
      description: 'Very high income earners'
    },
    {
      band: 'Band 7',
      income: 'Over R1,817,000',
      rate: '45%',
      taxOnBand: 'R644,489 + 45% above R1,817,000',
      description: 'Top income bracket'
    }
  ];

  const rebates = [
    { type: 'Primary Rebate', amount: 'R17,235', description: 'Available to all taxpayers' },
    { type: 'Secondary Rebate (65+)', amount: 'R9,444', description: 'Additional rebate for taxpayers aged 65 and over' },
    { type: 'Tertiary Rebate (75+)', amount: 'R3,145', description: 'Additional rebate for taxpayers aged 75 and over' }
  ];

  const sectionStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
  };

  const titleStyle = {
    fontSize: '1.4rem',
    fontWeight: 700,
    color: '#0F172A',
    marginBottom: '8px',
  };

  const subtitleStyle = {
    color: '#64748B',
    fontSize: '0.95rem',
    marginBottom: '32px',
    lineHeight: '1.7',
  };

  const tableStyle = {
    width: '100%',
    borderCollapse: 'separate',
    borderSpacing: '0',
    marginBottom: '32px',
  };

  const thStyle = {
    backgroundColor: '#F1F5F9',
    padding: '16px',
    textAlign: 'left',
    fontWeight: 600,
    color: '#0F172A',
    fontSize: '0.9rem',
    borderBottom: '2px solid #E2E8F0',
  };

  const tdStyle = {
    padding: '16px',
    borderBottom: '1px solid #E2E8F0',
    color: '#475569',
  };

  const bandNameStyle = {
    fontWeight: 600,
    color: '#0F172A',
    fontSize: '1rem',
  };

  const rateStyle = {
    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace',
    fontWeight: 600,
    color: '#2563EB',
    fontSize: '1.05rem',
  };

  const calloutStyle = {
    padding: '20px',
    backgroundColor: '#EFF6FF',
    borderLeft: '4px solid #3B82F6',
    borderRadius: '8px',
    marginTop: '24px',
  };

  const calloutTitleStyle = {
    fontWeight: 600,
    color: '#1E40AF',
    marginBottom: '12px',
    fontSize: '1rem',
  };

  const calloutTextStyle = {
    color: '#475569',
    fontSize: '0.95rem',
    lineHeight: '1.7',
    marginBottom: '8px',
  };

  return (
    <div style={sectionStyle}>
      <h2 style={titleStyle}>South Africa Income Tax Rates 2025/26</h2>
      <p style={subtitleStyle}>
        These are the income tax rates and bands for South African residents for the 2025/26 tax year
        (1 March 2025 - 28 February 2026).
      </p>

      <table style={tableStyle}>
        <thead>
          <tr>
            <th style={thStyle}>Tax Band</th>
            <th style={thStyle}>Taxable Income</th>
            <th style={thStyle}>Tax Rate</th>
            <th style={thStyle}>Tax on Band</th>
          </tr>
        </thead>
        <tbody>
          {taxBands.map((band, index) => (
            <tr key={index}>
              <td style={tdStyle}>
                <div style={bandNameStyle}>{band.band}</div>
                <div style={{ fontSize: '0.85rem', color: '#94A3B8', marginTop: '4px' }}>
                  {band.description}
                </div>
              </td>
              <td style={tdStyle}>
                <span style={{ fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace' }}>
                  {band.income}
                </span>
              </td>
              <td style={tdStyle}>
                <span style={rateStyle}>{band.rate}</span>
              </td>
              <td style={tdStyle}>
                <span style={{ fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace' }}>
                  {band.taxOnBand}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Tax Rebates Section */}
      <div style={{ marginTop: '48px' }}>
        <h3 style={{ ...titleStyle, fontSize: '1.2rem', marginBottom: '16px' }}>Tax Rebates (Primary, Secondary, Tertiary)</h3>
        <p style={subtitleStyle}>
          South Africa uses a rebate system instead of a personal allowance. These rebates reduce your calculated tax.
        </p>

        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>Rebate Type</th>
              <th style={thStyle}>Annual Amount</th>
              <th style={thStyle}>Eligibility</th>
            </tr>
          </thead>
          <tbody>
            {rebates.map((rebate, index) => (
              <tr key={index}>
                <td style={tdStyle}>
                  <div style={bandNameStyle}>{rebate.type}</div>
                </td>
                <td style={tdStyle}>
                  <span style={{ fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace', fontWeight: 600 }}>
                    {rebate.amount}
                  </span>
                </td>
                <td style={tdStyle}>
                  <span style={{ fontSize: '0.9rem' }}>{rebate.description}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={calloutStyle}>
        <div style={calloutTitleStyle}>Important Notes</div>
        <p style={calloutTextStyle}>
          <strong>Tax Thresholds:</strong> After applying rebates, the effective tax-free threshold is R95,750 for
          those under 65, R148,217 for those aged 65-74, and R165,689 for those 75 and older.
        </p>
        <p style={calloutTextStyle}>
          <strong>Interest Exemption:</strong> Interest income up to R23,800 (under 65) or R34,500 (65+) is exempt
          from tax.
        </p>
        <p style={calloutTextStyle}>
          <strong>Dividends Tax:</strong> Dividends are subject to a 20% withholding tax at source, not included
          in these rates.
        </p>
        <p style={calloutTextStyle}>
          <strong>Capital Gains:</strong> 40% of capital gains are included in taxable income (or 80% for companies),
          making the effective rate 18% for individuals in the top bracket.
        </p>
      </div>
    </div>
  );
}
