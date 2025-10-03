import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from 'internal-packages/ui';
import { Alert } from 'internal-packages/ui';
import {
  getYearsUntilDeemedDomicile,
  getDeemedDomicileProgress,
} from '../../utils/taxStatus';

export function DeemedDomicileSection({ deemedDomicileData, loading }) {
  const [showExplanation, setShowExplanation] = useState(false);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Your deemed domicile status</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  if (!deemedDomicileData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Your deemed domicile status</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="info">
            <p className="text-sm">
              Set up your tax status to see your deemed domicile calculation.
            </p>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const {
    uk_deemed_domicile,
    deemed_domicile_reason,
    uk_resident_years_in_last_20,
    deemed_domicile_date,
  } = deemedDomicileData;

  const yearsUntilDeemed = getYearsUntilDeemedDomicile(uk_resident_years_in_last_20 || 0);
  const progress = getDeemedDomicileProgress(uk_resident_years_in_last_20 || 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Your deemed domicile status</CardTitle>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Status Display */}
        {uk_deemed_domicile ? (
          <Alert variant="warning">
            <div className="space-y-2">
              <p className="font-medium text-lg">You're deemed UK domiciled</p>
              <p className="text-sm" style={{ lineHeight: 1.7 }}>
                {deemed_domicile_date
                  ? `You became deemed UK domiciled from ${new Date(deemed_domicile_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })}.`
                  : 'You are deemed UK domiciled.'}{' '}
                This means you're subject to UK inheritance tax on your worldwide estate, not just
                UK assets.
              </p>
              {deemed_domicile_reason && (
                <p className="text-sm font-medium mt-2">Reason: {deemed_domicile_reason}</p>
              )}
            </div>
          </Alert>
        ) : (
          <Alert variant="info">
            <div className="space-y-2">
              <p className="font-medium text-lg">You're not deemed UK domiciled</p>
              <p className="text-sm" style={{ lineHeight: 1.7 }}>
                You haven't yet met the 15-year threshold for deemed domicile. You've been UK
                resident for {uk_resident_years_in_last_20 || 0} of the last 20 years.
              </p>
            </div>
          </Alert>
        )}

        {/* Progress to Deemed Domicile */}
        {!uk_deemed_domicile && (
          <div>
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-medium text-gray-900">Progress to deemed domicile</h3>
              <span className="text-sm text-gray-600">
                {uk_resident_years_in_last_20 || 0} / 15 years
              </span>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>

            <p className="mt-2 text-sm text-gray-600" style={{ lineHeight: 1.7 }}>
              {yearsUntilDeemed > 0
                ? `You need ${yearsUntilDeemed} more ${yearsUntilDeemed === 1 ? 'year' : 'years'} of UK residence to become deemed domiciled.`
                : 'You have met the 15-year requirement.'}
            </p>
          </div>
        )}

        {/* Explanation Section */}
        <div>
          <button
            onClick={() => setShowExplanation(!showExplanation)}
            className="text-sm font-medium text-blue-600 hover:text-blue-800 focus:outline-none"
          >
            {showExplanation ? 'Hide explanation' : 'What is deemed domicile? →'}
          </button>

          {showExplanation && (
            <div className="mt-3 space-y-3">
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h4 className="font-medium text-gray-900 mb-2">Understanding deemed domicile</h4>
                <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
                  Deemed domicile is a UK tax concept that affects inheritance tax (IHT). Even if
                  you're not UK domiciled by birth or choice, you become deemed UK domiciled if:
                </p>
                <ul className="mt-2 space-y-1 text-sm text-gray-700 list-disc list-inside">
                  <li>You've been UK tax resident for 15 of the last 20 tax years, OR</li>
                  <li>
                    You were born in the UK with a UK domicile of origin, and you've been UK
                    resident in at least 1 of the previous 2 tax years
                  </li>
                </ul>
              </div>

              <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
                <h4 className="font-medium text-gray-900 mb-2">Why it matters</h4>
                <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
                  Once you're deemed UK domiciled, you're subject to UK inheritance tax at 40% on
                  your worldwide estate (after allowances). This includes:
                </p>
                <ul className="mt-2 space-y-1 text-sm text-gray-700 list-disc list-inside">
                  <li>All UK assets (property, investments, bank accounts)</li>
                  <li>All foreign assets (overseas property, foreign investments)</li>
                  <li>Worldwide estate subject to IHT above the nil-rate band (£325,000)</li>
                </ul>
                <p className="mt-2 text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
                  Non-UK domiciled individuals only pay UK IHT on UK assets—foreign assets remain
                  outside the UK IHT net.
                </p>
              </div>

              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <h4 className="font-medium text-gray-900 mb-2">Planning opportunities</h4>
                <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
                  If you're approaching deemed domicile status, consider:
                </p>
                <ul className="mt-2 space-y-1 text-sm text-gray-700 list-disc list-inside">
                  <li>Reviewing your estate and potential IHT liability</li>
                  <li>Making gifts now (7-year rule for IHT exemption)</li>
                  <li>Setting up trusts to protect foreign assets</li>
                  <li>Discussing with a tax advisor before you become deemed domiciled</li>
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* IHT Implications */}
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-2">Inheritance tax implications</h4>
          <p className="text-sm text-gray-700" style={{ lineHeight: 1.7 }}>
            {uk_deemed_domicile
              ? 'As a deemed UK domiciled individual, your entire worldwide estate is subject to UK inheritance tax. Consider using the IHT Planning module to explore strategies to reduce your potential tax liability.'
              : 'Currently, only your UK assets are subject to UK inheritance tax (unless you have a UK domicile of choice). Your foreign assets remain outside the UK IHT net, but this will change if you become deemed domiciled.'}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
