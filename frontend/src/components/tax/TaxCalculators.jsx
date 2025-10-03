import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from 'internal-packages/ui';
import { SRTCalculator } from './SRTCalculator';
import { SAPresenceCalculator } from './SAPresenceCalculator';

export function TaxCalculators() {
  const [activeTab, setActiveTab] = useState('uk-srt');

  const tabStyle = (isActive) => ({
    padding: '12px 24px',
    borderBottom: isActive ? '2px solid #2563EB' : '2px solid transparent',
    color: isActive ? '#2563EB' : '#475569',
    fontWeight: isActive ? 600 : 500,
    cursor: 'pointer',
    transition: 'all 150ms ease-in-out',
    backgroundColor: isActive ? '#EFF6FF' : 'transparent',
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Tax Residency Calculators</CardTitle>
        <p className="mt-2 text-gray-600" style={{ lineHeight: 1.7 }}>
          Use these calculators to determine your tax residency status in the UK and South Africa.
          The results can help you complete your tax status form accurately.
        </p>
      </CardHeader>

      <CardContent>
        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <div className="flex gap-2">
            <button
              style={tabStyle(activeTab === 'uk-srt')}
              onClick={() => setActiveTab('uk-srt')}
              className="focus:outline-none"
            >
              UK Statutory Residence Test
            </button>
            <button
              style={tabStyle(activeTab === 'sa-presence')}
              onClick={() => setActiveTab('sa-presence')}
              className="focus:outline-none"
            >
              SA Physical Presence Test
            </button>
          </div>
        </div>

        {/* Calculator Content */}
        <div>
          {activeTab === 'uk-srt' && <SRTCalculator />}
          {activeTab === 'sa-presence' && <SAPresenceCalculator />}
        </div>
      </CardContent>
    </Card>
  );
}
