import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from 'internal-packages/ui';
import { Alert } from 'internal-packages/ui';
import { Button } from 'internal-packages/ui';
import {
  getUKResidencyDescription,
  getSAResidencyDescription,
  getDomicileDescription,
  getDTATieBreakerDescription,
  formatDateRange,
} from '../../utils/taxStatus';

export function CurrentTaxStatusSection({ taxStatus, onEdit, loading }) {
  const [showExplanations, setShowExplanations] = useState({});

  const toggleExplanation = (key) => {
    setShowExplanations((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Your current tax status</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  if (!taxStatus) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Your current tax status</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="info" className="mb-4">
            <p className="font-medium">You haven't set up your tax status yet</p>
            <p className="mt-1 text-sm">
              Let's get started by telling us about your tax residency and domicile status.
              This helps us provide accurate tax advice tailored to your situation.
            </p>
          </Alert>
          <Button onClick={onEdit}>Set up your tax status</Button>
        </CardContent>
      </Card>
    );
  }

  const { uk_tax_resident, sa_tax_resident, domicile, dual_resident, dta_tie_breaker_result } =
    taxStatus;

  const isDualResident = uk_tax_resident && sa_tax_resident;

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle>Your current tax status</CardTitle>
          <Button variant="outline" onClick={onEdit}>
            Update
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Effective date range */}
        <div>
          <p className="text-sm text-gray-500">
            Effective {formatDateRange(taxStatus.effective_from, taxStatus.effective_to)}
          </p>
        </div>

        {/* UK Residency Status */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">UK Tax Residency</h3>
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                uk_tax_resident
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {uk_tax_resident ? 'Resident' : 'Non-Resident'}
            </span>
          </div>
          <p className="text-gray-700" style={{ lineHeight: 1.7 }}>
            {getUKResidencyDescription(uk_tax_resident)}
          </p>
        </div>

        {/* SA Residency Status */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">South African Tax Residency</h3>
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                sa_tax_resident
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {sa_tax_resident ? 'Resident' : 'Non-Resident'}
            </span>
          </div>
          <p className="text-gray-700" style={{ lineHeight: 1.7 }}>
            {getSAResidencyDescription(sa_tax_resident)}
          </p>
        </div>

        {/* Dual Residency Warning */}
        {isDualResident && (
          <Alert variant="warning">
            <p className="font-medium">
              You're resident in both the UK and South Africa
            </p>
            <p className="mt-1 text-sm" style={{ lineHeight: 1.7 }}>
              When you're tax resident in both countries, the Double Tax Agreement (DTA) determines
              which country has primary taxing rights.{' '}
              {dta_tie_breaker_result && getDTATieBreakerDescription(dta_tie_breaker_result)}
            </p>
            <button
              onClick={() => toggleExplanation('dta')}
              className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-800"
            >
              {showExplanations.dta ? 'Hide details' : 'What is the DTA? →'}
            </button>
            {showExplanations.dta && (
              <div className="mt-3 p-3 bg-white rounded border border-yellow-200">
                <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
                  The Double Tax Agreement (DTA) is a treaty between the UK and South Africa that
                  prevents you from being taxed twice on the same income. It includes "tie-breaker"
                  rules to determine which country should be treated as your primary residence for
                  tax purposes, based on factors like where your permanent home is, your center of
                  vital interests, and habitual residence.
                </p>
              </div>
            )}
          </Alert>
        )}

        {/* Domicile Status */}
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">Domicile Status</h3>
          <p className="text-gray-700" style={{ lineHeight: 1.7 }}>
            {getDomicileDescription(domicile)}
          </p>
          <button
            onClick={() => toggleExplanation('domicile')}
            className="text-sm font-medium text-blue-600 hover:text-blue-800"
          >
            {showExplanations.domicile ? 'Hide details' : 'What is domicile? →'}
          </button>
          {showExplanations.domicile && (
            <div className="mt-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
                Your domicile is your permanent home country—the place you consider your long-term
                base. It's different from residence. Domicile affects inheritance tax: UK domiciled
                individuals pay UK inheritance tax on their worldwide estate, while non-UK domiciled
                individuals only pay it on UK assets. Domicile is difficult to change and typically
                requires demonstrating a permanent intention to live in a new country.
              </p>
            </div>
          )}
        </div>

        {/* Remittance Basis */}
        {taxStatus.uk_residence_basis === 'REMITTANCE' && (
          <Alert variant="info">
            <p className="font-medium">You're using the remittance basis</p>
            <p className="mt-1 text-sm" style={{ lineHeight: 1.7 }}>
              As a non-UK domiciled individual, you've chosen to pay UK tax only on income and
              gains brought to (remitted to) the UK. Foreign income and gains that remain overseas
              are not taxed in the UK. Note that using the remittance basis may reduce your
              personal allowances.
            </p>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
