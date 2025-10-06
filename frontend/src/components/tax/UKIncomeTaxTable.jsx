import React from 'react';

export function UKIncomeTaxTable() {
  const taxBands = [
    {
      band: 'Personal Allowance',
      income: '£0 - £12,570',
      rate: '0%',
      taxOnBand: '£0',
      description: 'You don\'t pay tax on this portion of your income'
    },
    {
      band: 'Basic Rate',
      income: '£12,571 - £50,270',
      rate: '20%',
      taxOnBand: 'Up to £7,540',
      description: 'Most UK taxpayers fall into this bracket'
    },
    {
      band: 'Higher Rate',
      income: '£50,271 - £125,140',
      rate: '40%',
      taxOnBand: 'Up to £29,948',
      description: 'Higher earners pay this rate on income above £50,270'
    },
    {
      band: 'Additional Rate',
      income: 'Over £125,140',
      rate: '45%',
      taxOnBand: 'No limit',
      description: 'Top earners pay 45% on income above this threshold'
    }
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
      <h2 style={titleStyle}>UK Income Tax Rates 2025/26</h2>
      <p style={subtitleStyle}>
        These are the income tax rates and bands for England, Wales, and Northern Ireland.
        Scotland has different rates and bands.
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

      <div style={calloutStyle}>
        <div style={calloutTitleStyle}>Important Notes</div>
        <p style={calloutTextStyle}>
          <strong>Personal Allowance Taper:</strong> Your Personal Allowance reduces by £1 for every £2 
          you earn over £100,000. This means it's completely gone if you earn £125,140 or more.
        </p>
        <p style={calloutTextStyle}>
          <strong>National Insurance:</strong> You also pay National Insurance on employment income:
          12% on earnings between £12,570 and £50,270, and 2% on earnings above £50,270.
        </p>
        <p style={calloutTextStyle}>
          <strong>Scotland:</strong> If you're a Scottish taxpayer, different rates apply. Check HMRC's
          guidance for Scottish income tax rates.
        </p>
        <p style={calloutTextStyle}>
          <strong>Dividends:</strong> Different rates apply to dividend income: 8.75% (basic), 33.75% (higher),
          and 39.35% (additional), with a £500 dividend allowance.
        </p>
      </div>
    </div>
  );
}
