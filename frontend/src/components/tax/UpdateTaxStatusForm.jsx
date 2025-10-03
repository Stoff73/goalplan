import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from 'internal-packages/ui';
import { Input } from 'internal-packages/ui';
import { Select } from 'internal-packages/ui';
import { Checkbox } from 'internal-packages/ui';
import { Label } from 'internal-packages/ui';
import { Button } from 'internal-packages/ui';
import { Alert } from 'internal-packages/ui';
import { formatDateForInput } from '../../utils/taxStatus';

export function UpdateTaxStatusForm({ onSubmit, onCancel, loading }) {
  const [formData, setFormData] = useState({
    effective_from: formatDateForInput(new Date()),
    uk_tax_resident: false,
    sa_tax_resident: false,
    domicile: '',
    domicile_of_origin: '',
    uk_residence_basis: 'ARISING',
    split_year_treatment: false,
    sa_ordinarily_resident: false,
    dta_tie_breaker_result: '',
    notes: '',
  });

  const [errors, setErrors] = useState({});
  const [showHelp, setShowHelp] = useState({});

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const toggleHelp = (key) => {
    setShowHelp((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.effective_from) {
      newErrors.effective_from = 'Effective date is required';
    }

    if (!formData.domicile) {
      newErrors.domicile = 'Please select your domicile status';
    }

    if (!formData.domicile_of_origin) {
      newErrors.domicile_of_origin = 'Please select your domicile of origin';
    }

    // Remittance basis validation
    if (
      formData.uk_residence_basis === 'REMITTANCE' &&
      (formData.domicile === 'UK_DOMICILED' || formData.domicile === 'DEEMED_UK_DOMICILE')
    ) {
      newErrors.uk_residence_basis =
        'Remittance basis is only available for non-UK domiciled individuals';
    }

    // Dual residency requires DTA tie-breaker
    if (formData.uk_tax_resident && formData.sa_tax_resident && !formData.dta_tie_breaker_result) {
      newErrors.dta_tie_breaker_result =
        'Please select DTA tie-breaker result when resident in both countries';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    // Transform domicile values from UI format to API format
    const domicileMap = {
      'UK_DOMICILED': 'uk_domicile',
      'NON_UK_DOMICILED': 'non_uk_domicile',
      'DEEMED_UK_DOMICILE': 'deemed_domicile',
    };

    // Transform DTA tie-breaker from UI format to API format
    const dtaMap = {
      'UK_RESIDENT': 'UK',
      'SA_RESIDENT': 'ZA',
    };

    // Transform snake_case to camelCase for API
    const apiData = {
      effectiveFrom: formData.effective_from,
      ukTaxResident: formData.uk_tax_resident,
      saTaxResident: formData.sa_tax_resident,
      ukDomicile: domicileMap[formData.domicile] || formData.domicile,
      ukSplitYearTreatment: formData.split_year_treatment,
      ukRemittanceBasis: formData.uk_residence_basis === 'REMITTANCE',
      saOrdinarilyResident: formData.sa_ordinarily_resident,
      dualResident: formData.uk_tax_resident && formData.sa_tax_resident,
      dtaTieBreakerCountry: formData.dta_tie_breaker_result
        ? (dtaMap[formData.dta_tie_breaker_result] || formData.dta_tie_breaker_result)
        : null,
    };

    onSubmit(apiData);
  };

  const isDualResident = formData.uk_tax_resident && formData.sa_tax_resident;
  const isNonUKDomiciled = formData.domicile === 'NON_UK_DOMICILED';

  return (
    <Card>
      <CardHeader>
        <CardTitle>Update your tax status</CardTitle>
        <p className="mt-2 text-gray-600" style={{ lineHeight: 1.7 }}>
          Your tax status determines how you're taxed in the UK and South Africa. We'll help you
          understand your obligations.
        </p>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Effective From Date */}
          <div>
            <Label htmlFor="effective_from">Effective from date *</Label>
            <Input
              type="date"
              id="effective_from"
              name="effective_from"
              value={formData.effective_from}
              onChange={handleChange}
              error={errors.effective_from}
              required
            />
            <p className="mt-1 text-sm text-gray-500">
              The date this tax status becomes effective (usually start of tax year)
            </p>
          </div>

          {/* UK Tax Resident */}
          <div>
            <Checkbox
              id="uk_tax_resident"
              name="uk_tax_resident"
              checked={formData.uk_tax_resident}
              onChange={handleChange}
              label="I am a UK tax resident"
            />
            <button
              type="button"
              onClick={() => toggleHelp('ukResident')}
              className="mt-1 text-sm text-blue-600 hover:text-blue-800"
            >
              {showHelp.ukResident ? 'Hide help' : 'How do I know? →'}
            </button>
            {showHelp.ukResident && (
              <div className="mt-2 p-3 bg-blue-50 rounded border border-blue-200">
                <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
                  You're UK tax resident if you spent 183+ days in the UK during the tax year, or
                  if you pass the Statutory Residence Test (SRT). Use the SRT calculator below if
                  you're unsure.
                </p>
              </div>
            )}
          </div>

          {/* SA Tax Resident */}
          <div>
            <Checkbox
              id="sa_tax_resident"
              name="sa_tax_resident"
              checked={formData.sa_tax_resident}
              onChange={handleChange}
              label="I am a South African tax resident"
            />
            <button
              type="button"
              onClick={() => toggleHelp('saResident')}
              className="mt-1 text-sm text-blue-600 hover:text-blue-800"
            >
              {showHelp.saResident ? 'Hide help' : 'How do I know? →'}
            </button>
            {showHelp.saResident && (
              <div className="mt-2 p-3 bg-blue-50 rounded border border-blue-200">
                <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
                  You're SA tax resident if you were physically present in South Africa for more
                  than 91 days in the current year AND more than 91 days on average over the
                  previous 5 years. Use the SA Presence Test calculator below to check.
                </p>
              </div>
            )}
          </div>

          {/* Dual Residency Warning */}
          {isDualResident && (
            <Alert variant="warning">
              <p className="font-medium">You're resident in both countries</p>
              <p className="mt-1 text-sm" style={{ lineHeight: 1.7 }}>
                The Double Tax Agreement (DTA) determines which country has primary taxing rights.
                You'll need to select the DTA tie-breaker result below.
              </p>
            </Alert>
          )}

          {/* Domicile Status */}
          <div>
            <Label htmlFor="domicile">Domicile status *</Label>
            <Select
              id="domicile"
              name="domicile"
              value={formData.domicile}
              onChange={handleChange}
              error={errors.domicile}
              options={[
                { value: 'UK_DOMICILED', label: 'UK Domiciled' },
                { value: 'NON_UK_DOMICILED', label: 'Non-UK Domiciled' },
                { value: 'DEEMED_UK_DOMICILE', label: 'Deemed UK Domiciled' },
              ]}
              placeholder="Select domicile status"
              required
            />
            <button
              type="button"
              onClick={() => toggleHelp('domicile')}
              className="mt-1 text-sm text-blue-600 hover:text-blue-800"
            >
              {showHelp.domicile ? 'Hide help' : 'What is domicile? →'}
            </button>
            {showHelp.domicile && (
              <div className="mt-2 p-3 bg-blue-50 rounded border border-blue-200">
                <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
                  Your domicile is your permanent home country. It determines your inheritance tax
                  treatment. Most people have the same domicile their entire life. Deemed domicile
                  applies if you've been UK resident for 15 of the last 20 years.
                </p>
              </div>
            )}
          </div>

          {/* Domicile of Origin */}
          <div>
            <Label htmlFor="domicile_of_origin">Domicile of origin *</Label>
            <Select
              id="domicile_of_origin"
              name="domicile_of_origin"
              value={formData.domicile_of_origin}
              onChange={handleChange}
              error={errors.domicile_of_origin}
              options={[
                { value: 'UK', label: 'United Kingdom' },
                { value: 'SA', label: 'South Africa' },
                { value: 'OTHER', label: 'Other country' },
              ]}
              placeholder="Select domicile of origin"
              required
            />
            <p className="mt-1 text-sm text-gray-500">
              The country where you were born or where your father was domiciled when you were born
            </p>
          </div>

          {/* Remittance Basis (only for non-UK domiciled) */}
          {isNonUKDomiciled && formData.uk_tax_resident && (
            <div>
              <Label htmlFor="uk_residence_basis">UK residence basis</Label>
              <Select
                id="uk_residence_basis"
                name="uk_residence_basis"
                value={formData.uk_residence_basis}
                onChange={handleChange}
                error={errors.uk_residence_basis}
                options={[
                  { value: 'ARISING', label: 'Arising basis (taxed on worldwide income)' },
                  { value: 'REMITTANCE', label: 'Remittance basis (taxed on UK income only)' },
                ]}
              />
              <p className="mt-1 text-sm text-gray-500">
                Non-UK domiciled individuals can choose the remittance basis to only pay UK tax on
                income brought to the UK
              </p>
            </div>
          )}

          {/* Split Year Treatment */}
          {formData.uk_tax_resident && (
            <div>
              <Checkbox
                id="split_year_treatment"
                name="split_year_treatment"
                checked={formData.split_year_treatment}
                onChange={handleChange}
                label="Split year treatment applies"
              />
              <p className="mt-1 text-sm text-gray-500">
                Only applies if you moved to/from the UK mid-year in specific circumstances
              </p>
            </div>
          )}

          {/* SA Ordinarily Resident */}
          {formData.sa_tax_resident && (
            <div>
              <Checkbox
                id="sa_ordinarily_resident"
                name="sa_ordinarily_resident"
                checked={formData.sa_ordinarily_resident}
                onChange={handleChange}
                label="I am ordinarily resident in South Africa"
              />
              <p className="mt-1 text-sm text-gray-500">
                You're ordinarily resident if you've been SA tax resident for 3+ consecutive years
              </p>
            </div>
          )}

          {/* DTA Tie-Breaker (only if dual resident) */}
          {isDualResident && (
            <div>
              <Label htmlFor="dta_tie_breaker_result">
                DTA tie-breaker result (which country treats you as resident?) *
              </Label>
              <Select
                id="dta_tie_breaker_result"
                name="dta_tie_breaker_result"
                value={formData.dta_tie_breaker_result}
                onChange={handleChange}
                error={errors.dta_tie_breaker_result}
                options={[
                  { value: 'UK_RESIDENT', label: 'UK (primary residence in UK)' },
                  { value: 'SA_RESIDENT', label: 'South Africa (primary residence in SA)' },
                ]}
                placeholder="Select tie-breaker result"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                The DTA uses tie-breaker rules based on permanent home, center of vital interests,
                and habitual residence
              </p>
            </div>
          )}

          {/* Notes */}
          <div>
            <Label htmlFor="notes">Additional notes (optional)</Label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Any additional information about your tax status..."
            />
          </div>

          {/* Form Actions */}
          <div className="flex gap-3 pt-4">
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : 'Save tax status'}
            </Button>
            <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
              Cancel
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
