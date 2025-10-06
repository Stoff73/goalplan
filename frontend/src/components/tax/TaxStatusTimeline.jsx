import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from 'internal-packages/ui';
import { Alert } from 'internal-packages/ui';
import { formatDateRange } from '../../utils/taxStatus';

export function TaxStatusTimeline({ history, loading }) {
  const [expandedId, setExpandedId] = useState(null);

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Tax status history</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  if (!history || history.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Tax status history</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="info">
            <p className="text-sm">
              No tax status history yet. Your history will appear here once you create your first
              tax status record.
            </p>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const getStatusBadge = (isResident) => {
    return (
      <span
        className={`px-2 py-1 rounded text-xs font-medium ${
          isResident ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
        }`}
      >
        {isResident ? 'Resident' : 'Non-Resident'}
      </span>
    );
  };

  const getDomicileBadge = (domicile) => {
    const labels = {
      UK_DOMICILED: 'UK Dom',
      NON_UK_DOMICILED: 'Non-UK Dom',
      DEEMED_UK_DOMICILE: 'Deemed UK Dom',
    };

    const colors = {
      UK_DOMICILED: 'bg-purple-100 text-purple-800',
      NON_UK_DOMICILED: 'bg-gray-100 text-gray-800',
      DEEMED_UK_DOMICILE: 'bg-amber-100 text-amber-800',
    };

    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${colors[domicile] || 'bg-gray-100 text-gray-800'}`}>
        {labels[domicile] || domicile}
      </span>
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Tax status history</CardTitle>
        <p className="mt-2 text-sm text-gray-600">
          Your historical tax status records, showing changes over time
        </p>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {history.map((record, index) => {
            const isExpanded = expandedId === record.id;
            const isCurrent = !record.effective_to;

            return (
              <div
                key={record.id}
                className={`border rounded-lg overflow-hidden transition-all ${
                  isCurrent ? 'border-blue-300 bg-blue-50' : 'border-gray-200 bg-white'
                }`}
              >
                {/* Timeline Item Header */}
                <div
                  className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                  onClick={() => toggleExpand(record.id)}
                  role="button"
                  tabIndex={0}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') toggleExpand(record.id);
                  }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      {/* Date Range */}
                      <div className="flex items-center gap-2 mb-2">
                        <p className="font-medium text-gray-900">
                          {formatDateRange(record.effective_from, record.effective_to)}
                        </p>
                        {isCurrent && (
                          <span className="px-2 py-1 bg-blue-600 text-white rounded text-xs font-medium">
                            Current
                          </span>
                        )}
                      </div>

                      {/* Status Badges */}
                      <div className="flex flex-wrap gap-2">
                        <div className="flex items-center gap-1">
                          <span className="text-xs text-gray-600">UK:</span>
                          {getStatusBadge(record.uk_tax_resident)}
                        </div>
                        <div className="flex items-center gap-1">
                          <span className="text-xs text-gray-600">SA:</span>
                          {getStatusBadge(record.sa_tax_resident)}
                        </div>
                        {getDomicileBadge(record.domicile)}
                      </div>
                    </div>

                    {/* Expand/Collapse Icon */}
                    <div className="ml-4">
                      <svg
                        className={`w-5 h-5 text-gray-400 transition-transform ${
                          isExpanded ? 'rotate-180' : ''
                        }`}
                        fill="none"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path d="M19 9l-7 7-7-7"></path>
                      </svg>
                    </div>
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="px-4 pb-4 border-t border-gray-200 bg-white">
                    <div className="pt-4 space-y-3 text-sm">
                      {/* UK Residency */}
                      <div>
                        <p className="font-medium text-gray-900">UK Tax Residency</p>
                        <p className="text-gray-700" style={{ lineHeight: 1.7 }}>
                          {record.uk_tax_resident
                            ? "UK tax resident - liable to UK tax on worldwide income"
                            : "Non-UK tax resident - only liable to UK tax on UK-source income"}
                        </p>
                        {record.uk_residence_basis && (
                          <p className="text-gray-600 mt-1">
                            Basis: {record.uk_residence_basis === 'REMITTANCE' ? 'Remittance basis (non-UK domiciled)' : 'Arising basis'}
                          </p>
                        )}
                        {record.split_year_treatment && (
                          <p className="text-gray-600 mt-1">Split year treatment applied</p>
                        )}
                      </div>

                      {/* SA Residency */}
                      <div>
                        <p className="font-medium text-gray-900">SA Tax Residency</p>
                        <p className="text-gray-700" style={{ lineHeight: 1.7 }}>
                          {record.sa_tax_resident
                            ? "SA tax resident - liable to SA tax on worldwide income"
                            : "Non-SA tax resident - only liable to SA tax on SA-source income"}
                        </p>
                        {record.sa_ordinarily_resident && (
                          <p className="text-gray-600 mt-1">Ordinarily resident in SA</p>
                        )}
                      </div>

                      {/* Dual Residency */}
                      {record.dual_resident && (
                        <div>
                          <p className="font-medium text-gray-900">Dual Residency</p>
                          <p className="text-gray-700" style={{ lineHeight: 1.7 }}>
                            Resident in both UK and SA. DTA tie-breaker:{' '}
                            {record.dta_tie_breaker_result === 'UK_RESIDENT'
                              ? 'Treated as UK resident'
                              : record.dta_tie_breaker_result === 'SA_RESIDENT'
                              ? 'Treated as SA resident'
                              : 'Not specified'}
                          </p>
                        </div>
                      )}

                      {/* Domicile */}
                      <div>
                        <p className="font-medium text-gray-900">Domicile</p>
                        <p className="text-gray-700" style={{ lineHeight: 1.7 }}>
                          {record.domicile === 'UK_DOMICILED' && 'UK domiciled'}
                          {record.domicile === 'NON_UK_DOMICILED' && 'Non-UK domiciled'}
                          {record.domicile === 'DEEMED_UK_DOMICILE' && 'Deemed UK domiciled'}
                        </p>
                        {record.domicile_of_origin && (
                          <p className="text-gray-600 mt-1">
                            Domicile of origin: {record.domicile_of_origin}
                          </p>
                        )}
                        {record.uk_deemed_domicile && (
                          <p className="text-gray-600 mt-1">
                            UK deemed domicile status active
                          </p>
                        )}
                      </div>

                      {/* Notes */}
                      {record.notes && (
                        <div>
                          <p className="font-medium text-gray-900">Notes</p>
                          <p className="text-gray-700" style={{ lineHeight: 1.7 }}>
                            {record.notes}
                          </p>
                        </div>
                      )}

                      {/* Created Info */}
                      <div className="pt-2 border-t border-gray-200 text-xs text-gray-500">
                        Created on{' '}
                        {new Date(record.created_at).toLocaleDateString('en-GB', {
                          day: 'numeric',
                          month: 'long',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Timeline Connector (visual line between items) */}
        <style>{`
          .space-y-4 > div:not(:last-child)::after {
            content: '';
            display: block;
            width: 2px;
            height: 16px;
            background-color: #e2e8f0;
            margin: 0 auto;
            margin-top: 16px;
          }
        `}</style>
      </CardContent>
    </Card>
  );
}
