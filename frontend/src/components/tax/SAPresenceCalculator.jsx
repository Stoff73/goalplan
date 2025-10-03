import React, { useState } from 'react';
import { Input } from 'internal-packages/ui';
import { Label } from 'internal-packages/ui';
import { Button } from 'internal-packages/ui';
import { Alert } from 'internal-packages/ui';
import { formatSATaxYear, getCurrentSATaxYear } from '../../utils/taxStatus';
import { taxStatusEndpoints } from '../../utils/api';

export function SAPresenceCalculator() {
  const [formData, setFormData] = useState({
    tax_year: getCurrentSATaxYear(),
    days_in_sa_current: '',
    days_in_sa_year1: '',
    days_in_sa_year2: '',
    days_in_sa_year3: '',
    days_in_sa_year4: '',
    days_in_sa_year5: '',
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCalculate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await taxStatusEndpoints.calculateSAPresence({
        tax_year: formData.tax_year,
        days_in_sa_current: parseInt(formData.days_in_sa_current),
        days_previous_years: [
          parseInt(formData.days_in_sa_year1 || 0),
          parseInt(formData.days_in_sa_year2 || 0),
          parseInt(formData.days_in_sa_year3 || 0),
          parseInt(formData.days_in_sa_year4 || 0),
          parseInt(formData.days_in_sa_year5 || 0),
        ],
      });

      setResult(response);
    } catch (err) {
      setError(err.message || 'Failed to calculate SA residency. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-gray-900">
          South African Physical Presence Test Calculator
        </h3>
        <p className="mt-2 text-gray-600" style={{ lineHeight: 1.7 }}>
          Determine if you're a South African tax resident using the physical presence test. You're
          resident if you were in SA for more than 91 days this year AND more than 91 days on
          average over the last 5 years.
        </p>
      </div>

      <form onSubmit={handleCalculate} className="space-y-6">
        {/* Tax Year */}
        <div>
          <Label htmlFor="tax_year">Tax year</Label>
          <Input
            type="text"
            id="tax_year"
            name="tax_year"
            value={formData.tax_year}
            onChange={handleChange}
            placeholder="e.g. 2024/2025"
            required
          />
          <p className="mt-1 text-sm text-gray-500">
            SA tax year runs from 1 March to 28/29 February
          </p>
        </div>

        {/* Current Year Days */}
        <div>
          <Label htmlFor="days_in_sa_current">Days in South Africa (current tax year) *</Label>
          <Input
            type="number"
            id="days_in_sa_current"
            name="days_in_sa_current"
            value={formData.days_in_sa_current}
            onChange={handleChange}
            placeholder="0-365"
            min="0"
            max="365"
            required
          />
          <p className="mt-1 text-sm text-gray-500">
            Count any day you were physically present in South Africa
          </p>
        </div>

        {/* Previous Years */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Days in previous 5 years</h4>
          <p className="text-sm text-gray-600" style={{ lineHeight: 1.7 }}>
            Enter the number of days you spent in South Africa for each of the previous 5 tax
            years. Leave blank or enter 0 if you weren't in SA that year.
          </p>

          <div>
            <Label htmlFor="days_in_sa_year1">Year 1 (most recent)</Label>
            <Input
              type="number"
              id="days_in_sa_year1"
              name="days_in_sa_year1"
              value={formData.days_in_sa_year1}
              onChange={handleChange}
              placeholder="0-365"
              min="0"
              max="365"
            />
          </div>

          <div>
            <Label htmlFor="days_in_sa_year2">Year 2</Label>
            <Input
              type="number"
              id="days_in_sa_year2"
              name="days_in_sa_year2"
              value={formData.days_in_sa_year2}
              onChange={handleChange}
              placeholder="0-365"
              min="0"
              max="365"
            />
          </div>

          <div>
            <Label htmlFor="days_in_sa_year3">Year 3</Label>
            <Input
              type="number"
              id="days_in_sa_year3"
              name="days_in_sa_year3"
              value={formData.days_in_sa_year3}
              onChange={handleChange}
              placeholder="0-365"
              min="0"
              max="365"
            />
          </div>

          <div>
            <Label htmlFor="days_in_sa_year4">Year 4</Label>
            <Input
              type="number"
              id="days_in_sa_year4"
              name="days_in_sa_year4"
              value={formData.days_in_sa_year4}
              onChange={handleChange}
              placeholder="0-365"
              min="0"
              max="365"
            />
          </div>

          <div>
            <Label htmlFor="days_in_sa_year5">Year 5 (oldest)</Label>
            <Input
              type="number"
              id="days_in_sa_year5"
              name="days_in_sa_year5"
              value={formData.days_in_sa_year5}
              onChange={handleChange}
              placeholder="0-365"
              min="0"
              max="365"
            />
          </div>
        </div>

        {/* Submit Button */}
        <Button type="submit" disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate residency status'}
        </Button>
      </form>

      {/* Error Display */}
      {error && (
        <Alert variant="error">
          <p className="font-medium">Error</p>
          <p className="mt-1 text-sm">{error}</p>
        </Alert>
      )}

      {/* Results Display */}
      {result && (
        <div className="space-y-4">
          <Alert variant={result.sa_resident ? 'success' : 'info'}>
            <p className="text-lg font-semibold">
              {result.sa_resident
                ? "You're a South African tax resident!"
                : "You're not a South African tax resident"}
            </p>
            <p className="mt-2 text-sm" style={{ lineHeight: 1.7 }}>
              {result.reasoning}
            </p>
          </Alert>

          {/* Detailed Breakdown */}
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h4 className="font-medium text-gray-900 mb-3">Calculation Details</h4>
            <div className="space-y-2 text-sm">
              <p>
                <span className="font-medium">Days in SA (current year):</span>{' '}
                {result.days_current_year}
              </p>
              <p>
                <span className="font-medium">Average days over 6 years:</span>{' '}
                {result.average_days_6_years?.toFixed(1)}
              </p>

              {result.days_by_year && (
                <div className="mt-3">
                  <p className="font-medium mb-2">Days by year:</p>
                  <div className="space-y-1">
                    {result.days_by_year.map((yearData, index) => (
                      <p key={index} className="text-gray-700">
                        Year {index + 1}: {yearData.days} days
                      </p>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-3 pt-3 border-t border-gray-300">
                <p className="font-medium mb-1">Requirements:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li className={result.days_current_year > 91 ? 'text-green-700' : 'text-red-700'}>
                    More than 91 days in current year:{' '}
                    {result.days_current_year > 91 ? '✓ Yes' : '✗ No'}
                  </li>
                  <li
                    className={
                      result.average_days_6_years > 91 ? 'text-green-700' : 'text-red-700'
                    }
                  >
                    More than 91 days average over 6 years:{' '}
                    {result.average_days_6_years > 91 ? '✓ Yes' : '✗ No'}
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* Educational Section */}
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm font-medium text-gray-900 mb-2">What this means</p>
            <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
              {result.sa_resident
                ? "As a South African tax resident, you're liable to SA tax on your worldwide income and gains. You'll need to declare all your income on your SA tax return. If you've paid tax in other countries, you may be able to claim foreign tax credits to avoid double taxation."
                : "As a non-SA tax resident, you're only liable to SA tax on SA-source income (such as South African rental income, employment income from SA work, or SA pensions). Foreign income is generally not taxable in South Africa."}
            </p>

            {!result.sa_resident &&
              result.days_current_year > 91 &&
              result.average_days_6_years <= 91 && (
                <p className="mt-3 text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
                  Note: You met the current year requirement (more than 91 days) but not the
                  5-year average. If you continue spending significant time in SA, you may become
                  resident in future years.
                </p>
              )}
          </div>

          {/* Ordinarily Resident Note */}
          {result.sa_resident && (
            <Alert variant="info">
              <p className="font-medium text-sm">About ordinary residence</p>
              <p className="mt-1 text-sm" style={{ lineHeight: 1.7 }}>
                If you've been a South African tax resident for 3 or more consecutive years, you're
                also considered "ordinarily resident." This affects how your foreign pensions and
                retirement funds are taxed.
              </p>
            </Alert>
          )}
        </div>
      )}
    </div>
  );
}
