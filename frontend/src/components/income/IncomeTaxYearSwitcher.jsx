import React from 'react';
import { Select, Label } from 'internal-packages/ui';
import {
  getRecentUKTaxYears,
  getRecentSATaxYears,
  getUKTaxYearDates,
  getSATaxYearDates,
  getCurrentUKTaxYear,
  getCurrentSATaxYear
} from '../../utils/income';

export function IncomeTaxYearSwitcher({ country, taxYear, onCountryChange, onTaxYearChange }) {
  const ukTaxYears = getRecentUKTaxYears(6);
  const saTaxYears = getRecentSATaxYears(6);

  const taxYears = country === 'UK' ? ukTaxYears : saTaxYears;
  const currentTaxYear = country === 'UK' ? getCurrentUKTaxYear() : getCurrentSATaxYear();
  const selectedYear = taxYear || currentTaxYear;

  const getDatesText = () => {
    if (country === 'UK') {
      const dates = getUKTaxYearDates(selectedYear);
      return `${dates.start} - ${dates.end}`;
    } else {
      const dates = getSATaxYearDates(selectedYear);
      return `${dates.start} - ${dates.end}`;
    }
  };

  const containerStyle = {
    display: 'flex',
    gap: '16px',
    alignItems: 'end',
    flexWrap: 'wrap',
  };

  const fieldGroupStyle = {
    flex: '1 1 200px',
    minWidth: '200px',
  };

  const helpTextStyle = {
    fontSize: '0.875rem',
    color: '#64748B',
    marginTop: '8px',
    lineHeight: '1.5',
  };

  const dateDisplayStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '8px 12px',
    backgroundColor: '#F8FAFC',
    border: '1px solid #E2E8F0',
    borderRadius: '6px',
    fontSize: '0.875rem',
    color: '#475569',
    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace',
  };

  return (
    <div>
      <div style={containerStyle}>
        <div style={fieldGroupStyle}>
          <Label>Tax Year Country</Label>
          <Select
            value={country}
            onChange={(e) => onCountryChange(e.target.value)}
          >
            <option value="UK">UK Tax Year</option>
            <option value="SA">SA Tax Year</option>
          </Select>
          <div style={helpTextStyle}>
            {country === 'UK'
              ? 'UK tax year runs from 6 April to 5 April'
              : 'SA tax year runs from 1 March to 28 February'}
          </div>
        </div>

        <div style={fieldGroupStyle}>
          <Label>Tax Year</Label>
          <Select
            value={selectedYear}
            onChange={(e) => onTaxYearChange(e.target.value)}
          >
            {taxYears.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </Select>
          <div style={helpTextStyle}>
            <span style={dateDisplayStyle}>{getDatesText()}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
