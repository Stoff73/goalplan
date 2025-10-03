import React, { useState } from 'react';
import { Input } from 'internal-packages/ui';
import { Checkbox } from 'internal-packages/ui';
import { Label } from 'internal-packages/ui';
import { Button } from 'internal-packages/ui';
import { Alert } from 'internal-packages/ui';
import { formatUKTaxYear, getCurrentUKTaxYear, getSRTTieDescription } from '../../utils/taxStatus';
import { taxStatusEndpoints } from '../../utils/api';

export function SRTCalculator() {
  const [formData, setFormData] = useState({
    tax_year: getCurrentUKTaxYear(),
    days_in_uk: '',
    family_tie: false,
    accommodation_tie: false,
    work_tie: false,
    ninety_day_tie: false,
    country_tie: false,
    previous_year_resident: false,
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showHelp, setShowHelp] = useState({});

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const toggleHelp = (key) => {
    setShowHelp((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleCalculate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await taxStatusEndpoints.calculateSRT({
        tax_year: formData.tax_year,
        days_in_uk: parseInt(formData.days_in_uk),
        ties: {
          family_tie: formData.family_tie,
          accommodation_tie: formData.accommodation_tie,
          work_tie: formData.work_tie,
          ninety_day_tie: formData.ninety_day_tie,
          country_tie: formData.country_tie,
        },
        previous_year_resident: formData.previous_year_resident,
      });

      setResult(response);
    } catch (err) {
      setError(err.message || 'Failed to calculate UK residency. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-gray-900">UK Statutory Residence Test Calculator</h3>
        <p className="mt-2 text-gray-600" style={{ lineHeight: 1.7 }}>
          Not sure if you're UK tax resident? This calculator follows HMRC's official rules to
          determine your residency status.
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
            placeholder="e.g. 2024/25"
            required
          />
          <p className="mt-1 text-sm text-gray-500">UK tax year runs from 6 April to 5 April</p>
        </div>

        {/* Days in UK */}
        <div>
          <Label htmlFor="days_in_uk">Days in the UK during the tax year *</Label>
          <Input
            type="number"
            id="days_in_uk"
            name="days_in_uk"
            value={formData.days_in_uk}
            onChange={handleChange}
            placeholder="0-365"
            min="0"
            max="365"
            required
          />
          <p className="mt-1 text-sm text-gray-500">
            Count any day you were in the UK at midnight (even if you arrived late or left early)
          </p>
        </div>

        {/* Previous Year Resident */}
        <div>
          <Checkbox
            id="previous_year_resident"
            name="previous_year_resident"
            checked={formData.previous_year_resident}
            onChange={handleChange}
            label="I was UK resident in at least one of the previous 3 tax years"
          />
          <p className="mt-1 text-sm text-gray-500">
            This determines whether you're an "arriver" or "leaver" for tie-breaker purposes
          </p>
        </div>

        {/* UK Ties */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">UK Ties</h4>
          <p className="text-sm text-gray-600" style={{ lineHeight: 1.7 }}>
            The SRT uses five "ties" to the UK. The more ties you have, the fewer days you can
            spend in the UK before becoming resident.
          </p>

          {/* Family Tie */}
          <div>
            <Checkbox
              id="family_tie"
              name="family_tie"
              checked={formData.family_tie}
              onChange={handleChange}
              label="Family tie"
            />
            <button
              type="button"
              onClick={() => toggleHelp('family')}
              className="mt-1 text-sm text-blue-600 hover:text-blue-800"
            >
              {showHelp.family ? 'Hide details' : 'What is this? →'}
            </button>
            {showHelp.family && (
              <div className="mt-2 p-3 bg-blue-50 rounded border border-blue-200">
                <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
                  {getSRTTieDescription('FAMILY')}. This includes your spouse, civil partner, or
                  minor children (under 18) who are UK resident during the tax year.
                </p>
              </div>
            )}
          </div>

          {/* Accommodation Tie */}
          <div>
            <Checkbox
              id="accommodation_tie"
              name="accommodation_tie"
              checked={formData.accommodation_tie}
              onChange={handleChange}
              label="Accommodation tie"
            />
            <button
              type="button"
              onClick={() => toggleHelp('accommodation')}
              className="mt-1 text-sm text-blue-600 hover:text-blue-800"
            >
              {showHelp.accommodation ? 'Hide details' : 'What is this? →'}
            </button>
            {showHelp.accommodation && (
              <div className="mt-2 p-3 bg-blue-50 rounded border border-blue-200">
                <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
                  {getSRTTieDescription('ACCOMMODATION')}. This includes property you own, rent, or
                  have available for your use for at least 91 consecutive days during the tax year,
                  and you spent at least one night there.
                </p>
              </div>
            )}
          </div>

          {/* Work Tie */}
          <div>
            <Checkbox
              id="work_tie"
              name="work_tie"
              checked={formData.work_tie}
              onChange={handleChange}
              label="Work tie"
            />
            <button
              type="button"
              onClick={() => toggleHelp('work')}
              className="mt-1 text-sm text-blue-600 hover:text-blue-800"
            >
              {showHelp.work ? 'Hide details' : 'What is this? →'}
            </button>
            {showHelp.work && (
              <div className="mt-2 p-3 bg-blue-50 rounded border border-blue-200">
                <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
                  {getSRTTieDescription('WORK')}. You worked in the UK for 40 or more days during
                  the tax year, where you did more than 3 hours work per day. This includes
                  employment, self-employment, or working for a UK-based business.
                </p>
              </div>
            )}
          </div>

          {/* 90-Day Tie */}
          <div>
            <Checkbox
              id="ninety_day_tie"
              name="ninety_day_tie"
              checked={formData.ninety_day_tie}
              onChange={handleChange}
              label="90-day tie"
            />
            <button
              type="button"
              onClick={() => toggleHelp('ninetyDay')}
              className="mt-1 text-sm text-blue-600 hover:text-blue-800"
            >
              {showHelp.ninetyDay ? 'Hide details' : 'What is this? →'}
            </button>
            {showHelp.ninetyDay && (
              <div className="mt-2 p-3 bg-blue-50 rounded border border-blue-200">
                <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
                  {getSRTTieDescription('90_DAY')}. This looks back at the two tax years before the
                  current one. If you spent 90 or more days in the UK in either of those years,
                  this tie applies.
                </p>
              </div>
            )}
          </div>

          {/* Country Tie */}
          <div>
            <Checkbox
              id="country_tie"
              name="country_tie"
              checked={formData.country_tie}
              onChange={handleChange}
              label="Country tie"
            />
            <button
              type="button"
              onClick={() => toggleHelp('country')}
              className="mt-1 text-sm text-blue-600 hover:text-blue-800"
            >
              {showHelp.country ? 'Hide details' : 'What is this? →'}
            </button>
            {showHelp.country && (
              <div className="mt-2 p-3 bg-blue-50 rounded border border-blue-200">
                <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
                  {getSRTTieDescription('COUNTRY')}. You were present in the UK more than any other
                  single country during the tax year. This tie only applies to "leavers" (those who
                  were UK resident in at least one of the previous 3 years).
                </p>
              </div>
            )}
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
          <Alert variant={result.uk_resident ? 'success' : 'info'}>
            <p className="text-lg font-semibold">
              {result.uk_resident
                ? "You're a UK tax resident!"
                : "You're not a UK tax resident"}
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
                <span className="font-medium">Days in UK:</span> {result.days_in_uk}
              </p>
              <p>
                <span className="font-medium">Determination method:</span>{' '}
                {result.determination_method?.replace(/_/g, ' ')}
              </p>

              {result.ties_count !== undefined && (
                <>
                  <p>
                    <span className="font-medium">Ties:</span> {result.ties_count} (needed:{' '}
                    {result.ties_needed})
                  </p>
                  {result.ties_detail && (
                    <div className="mt-2">
                      <p className="font-medium mb-1">Tie breakdown:</p>
                      <ul className="list-disc list-inside space-y-1 ml-2">
                        {result.ties_detail.map((tie, index) => (
                          <li key={index} className="text-gray-700">
                            {tie.tie.replace(/_/g, ' ')}: {tie.met ? '✓ Yes' : '✗ No'}
                            {tie.reason && ` - ${tie.reason}`}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Educational Section */}
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm font-medium text-gray-900 mb-2">What this means</p>
            <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
              {result.uk_resident
                ? "As a UK tax resident, you're liable to UK tax on your worldwide income and gains. You should declare all your income on your UK tax return, though you may be able to claim Double Tax Relief for tax paid in other countries."
                : "As a non-UK tax resident, you're only liable to UK tax on UK-source income (such as rental income from UK property, employment income from UK work, or UK pensions). Foreign income is generally not taxable in the UK."}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
