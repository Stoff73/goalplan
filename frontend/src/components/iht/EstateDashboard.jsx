import React, { useState, useEffect } from 'react';
import { Card, Button, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * EstateDashboard - Comprehensive estate valuation and IHT calculation with narrative storytelling
 *
 * Features:
 * - Hero section with conversational estate summary
 * - IHT breakdown with nil rate bands visualization
 * - Asset and liability tables with edit/delete actions
 * - Real-time IHT calculation with interactive parameters
 * - Action recommendations section
 *
 * Follows STYLEGUIDE.md narrative storytelling approach:
 * - Conversational language ("Your estate is worth £500,000")
 * - Embed metrics in sentences with context
 * - Progressive disclosure with "Tell me more" sections
 * - Line height 1.7, generous white space
 */
export function EstateDashboard() {
  const [estateData, setEstateData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Interactive parameters state
  const [transferableNRB, setTransferableNRB] = useState(0);
  const [rnrbApplicable, setRnrbApplicable] = useState(false);
  const [charitableGifts, setCharitableGifts] = useState(0);

  // Modal states
  const [showAssetModal, setShowAssetModal] = useState(false);
  const [showLiabilityModal, setShowLiabilityModal] = useState(false);
  const [editingAsset, setEditingAsset] = useState(null);
  const [editingLiability, setEditingLiability] = useState(null);

  // Expandable sections state
  const [expandedSections, setExpandedSections] = useState({
    nilRateBands: false,
    assets: false,
    liabilities: false,
  });

  useEffect(() => {
    loadEstateData();
  }, []);

  useEffect(() => {
    // Recalculate IHT when parameters change
    if (estateData) {
      calculateIHT();
    }
  }, [transferableNRB, rnrbApplicable, charitableGifts]);

  const loadEstateData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/iht/estate/valuation', {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }
        if (response.status === 404) {
          setEstateData(null);
          setLoading(false);
          return;
        }
        throw new Error('Failed to fetch estate data');
      }

      const data = await response.json();
      setEstateData(data);

      // Set initial parameters from data
      if (data.ukInheritanceTax?.nilRateBand?.transferredFromSpouse) {
        setTransferableNRB(data.ukInheritanceTax.nilRateBand.transferredFromSpouse);
      }
      if (data.ukInheritanceTax?.residenceNilRateBand?.available > 0) {
        setRnrbApplicable(true);
      }
    } catch (err) {
      setError('Failed to load estate data. Please try again.');
      console.error('Error loading estate:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateIHT = async () => {
    try {
      const response = await fetch('/api/v1/iht/estate-calculation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({
          transferableNRB,
          rnrbApplicable,
          charitableGiftsPercentage: charitableGifts,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setEstateData(data);
      }
    } catch (err) {
      console.error('Error calculating IHT:', err);
    }
  };

  const deleteAsset = async (assetId) => {
    if (!confirm('Are you sure you want to delete this asset?')) return;

    try {
      const response = await fetch(`/api/v1/iht/assets/${assetId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (response.ok) {
        loadEstateData(); // Reload to get updated calculation
      }
    } catch (err) {
      console.error('Error deleting asset:', err);
      alert('Failed to delete asset');
    }
  };

  const deleteLiability = async (liabilityId) => {
    if (!confirm('Are you sure you want to delete this liability?')) return;

    try {
      const response = await fetch(`/api/v1/iht/liabilities/${liabilityId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (response.ok) {
        loadEstateData();
      }
    } catch (err) {
      console.error('Error deleting liability:', err);
      alert('Failed to delete liability');
    }
  };

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return '£0';
    return `£${Math.abs(amount).toLocaleString('en-GB', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })}`;
  };

  // Styles following STYLEGUIDE.md
  const containerStyle = {
    maxWidth: '1280px',
    margin: '0 auto',
  };

  const heroSectionStyle = {
    padding: '32px',
    background: 'linear-gradient(to bottom right, #F3E8FF, #E9D5FF)',
    borderRadius: '12px',
    marginBottom: '48px',
    lineHeight: '1.7',
  };

  const heroTitleStyle = {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#0F172A',
    marginBottom: '16px',
  };

  const narrativeParagraphStyle = {
    fontSize: '1rem',
    color: '#475569',
    lineHeight: '1.7',
    marginBottom: '12px',
  };

  const sectionStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '48px',
    lineHeight: '1.7',
  };

  const sectionHeadingStyle = {
    fontSize: '1.5rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '16px',
  };

  const breakdownBarStyle = (percentage, color) => ({
    height: '40px',
    width: `${percentage}%`,
    backgroundColor: color,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#FFFFFF',
    fontWeight: 600,
    fontSize: '0.875rem',
    transition: 'width 0.3s ease',
  });

  const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    marginTop: '16px',
  };

  const thStyle = {
    textAlign: 'left',
    padding: '12px',
    borderBottom: '2px solid #E2E8F0',
    fontSize: '0.875rem',
    fontWeight: 600,
    color: '#475569',
  };

  const tdStyle = {
    padding: '12px',
    borderBottom: '1px solid #E2E8F0',
    fontSize: '0.875rem',
    color: '#0F172A',
  };

  const actionButtonStyle = {
    padding: '6px 12px',
    fontSize: '0.75rem',
    marginLeft: '8px',
  };

  const sliderContainerStyle = {
    marginBottom: '24px',
  };

  const sliderLabelStyle = {
    fontSize: '0.875rem',
    fontWeight: 500,
    color: '#0F172A',
    marginBottom: '8px',
    display: 'block',
  };

  const sliderStyle = {
    width: '100%',
    height: '8px',
    borderRadius: '4px',
    background: '#E2E8F0',
    outline: 'none',
    WebkitAppearance: 'none',
  };

  const calloutBoxStyle = {
    padding: '16px',
    backgroundColor: '#DBEAFE',
    border: '1px solid #BFDBFE',
    borderLeft: '4px solid #3B82F6',
    borderRadius: '8px',
    marginTop: '16px',
  };

  const expandableTriggerStyle = {
    display: 'flex',
    alignItems: 'center',
    fontSize: '0.875rem',
    color: '#2563EB',
    cursor: 'pointer',
    fontWeight: 500,
    marginTop: '12px',
  };

  // Loading state
  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={sectionStyle}>
          <div style={{ textAlign: 'center', padding: '48px', color: '#94A3B8' }}>
            <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⏳</div>
            <p>Loading your estate calculation...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={containerStyle}>
        <Alert variant="error">
          <p style={{ fontWeight: 600 }}>Error Loading Estate</p>
          <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
        </Alert>
        <Button variant="outline" onClick={loadEstateData} style={{ marginTop: '16px' }}>
          Try Again
        </Button>
      </div>
    );
  }

  // Empty state
  if (!estateData || estateData.estateValuation?.grossEstate?.gbp === 0) {
    return (
      <div style={containerStyle}>
        <div style={sectionStyle}>
          <h3 style={sectionHeadingStyle}>Plan your estate and inheritance tax</h3>
          <p style={narrativeParagraphStyle}>
            Add your assets and liabilities to see your estate value and potential inheritance tax liability.
            We'll help you understand the tax implications and explore ways to reduce the burden on your beneficiaries.
          </p>
          <Button variant="primary" onClick={() => setShowAssetModal(true)} style={{ marginTop: '16px' }}>
            Add Your First Asset
          </Button>
        </div>
      </div>
    );
  }

  // Main view with data
  const {
    estateValuation,
    assetBreakdown,
    ukInheritanceTax,
    totalDeathTaxes,
    netEstateAfterTax,
    recommendations,
  } = estateData;

  const netEstate = estateValuation?.netEstate?.gbp || 0;
  const ihtLiability = ukInheritanceTax?.netTaxLiability || 0;
  const chargeableEstate = ukInheritanceTax?.chargeableEstate || 0;
  const totalNRB = ukInheritanceTax?.nilRateBand?.total || 325000;
  const totalRNRB = ukInheritanceTax?.residenceNilRateBand?.total || 0;

  const hasIHTLiability = ihtLiability > 0;

  return (
    <div style={containerStyle}>
      {/* Hero Section */}
      <div style={heroSectionStyle}>
        <h1 style={heroTitleStyle}>
          Your estate: <strong style={{ fontFamily: 'monospace', color: '#9333EA' }}>
            {formatCurrency(netEstate)}
          </strong>
        </h1>

        <p style={narrativeParagraphStyle}>
          After debts, your estate is worth <strong style={{ fontFamily: 'monospace' }}>
            {formatCurrency(netEstate)}
          </strong>.{' '}
          {hasIHTLiability ? (
            <>
              Based on current rules, you might owe{' '}
              <strong style={{ fontFamily: 'monospace', color: '#EF4444' }}>
                {formatCurrency(ihtLiability)}
              </strong>{' '}
              in Inheritance Tax at 40%. But there are ways to reduce this.
            </>
          ) : (
            <>
              Good news! Based on current rules, you won't owe any Inheritance Tax. Your estate is within
              the tax-free allowances.
            </>
          )}
        </p>

        <p style={{ fontSize: '0.875rem', color: '#64748B', lineHeight: '1.7' }}>
          The good news: everyone gets a{' '}
          <strong style={{ fontFamily: 'monospace' }}>£325,000</strong> tax-free allowance.
          {rnrbApplicable && (
            <>
              {' '}If you're leaving your home to children, you get another{' '}
              <strong style={{ fontFamily: 'monospace' }}>£175,000</strong>.
            </>
          )}
          {transferableNRB > 0 && (
            <>
              {' '}And you've inherited{' '}
              <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(transferableNRB)}</strong>{' '}
              from your spouse's unused allowance.
            </>
          )}
        </p>
      </div>

      {/* IHT Breakdown Card */}
      <div style={sectionStyle}>
        <h2 style={sectionHeadingStyle}>How much tax you might owe</h2>

        <div style={{ marginBottom: '24px' }}>
          {/* Visual breakdown bars */}
          <div style={{ marginBottom: '8px' }}>
            <div style={{ fontSize: '0.875rem', color: '#475569', marginBottom: '4px' }}>
              Net estate: {formatCurrency(netEstate)}
            </div>
            <div style={{ width: '100%', backgroundColor: '#F1F5F9', borderRadius: '8px', overflow: 'hidden' }}>
              {netEstate > 0 && (
                <div style={breakdownBarStyle(100, '#9333EA')}>
                  {formatCurrency(netEstate)}
                </div>
              )}
            </div>
          </div>

          <div style={{ marginBottom: '8px' }}>
            <div style={{ fontSize: '0.875rem', color: '#475569', marginBottom: '4px' }}>
              Minus nil rate bands: {formatCurrency(totalNRB + totalRNRB)}
            </div>
            <div style={{ width: '100%', backgroundColor: '#F1F5F9', borderRadius: '8px', overflow: 'hidden' }}>
              {totalNRB + totalRNRB > 0 && (
                <div style={breakdownBarStyle(Math.min((totalNRB + totalRNRB) / netEstate * 100, 100), '#10B981')}>
                  {formatCurrency(totalNRB + totalRNRB)}
                </div>
              )}
            </div>
          </div>

          {chargeableEstate > 0 && (
            <div style={{ marginBottom: '8px' }}>
              <div style={{ fontSize: '0.875rem', color: '#475569', marginBottom: '4px' }}>
                Taxable estate: {formatCurrency(chargeableEstate)}
              </div>
              <div style={{ width: '100%', backgroundColor: '#F1F5F9', borderRadius: '8px', overflow: 'hidden' }}>
                <div style={breakdownBarStyle((chargeableEstate / netEstate) * 100, '#F59E0B')}>
                  {formatCurrency(chargeableEstate)}
                </div>
              </div>
            </div>
          )}

          {ihtLiability > 0 && (
            <div>
              <div style={{ fontSize: '0.875rem', color: '#475569', marginBottom: '4px' }}>
                IHT owed at 40%: {formatCurrency(ihtLiability)}
              </div>
              <div style={{ width: '100%', backgroundColor: '#F1F5F9', borderRadius: '8px', overflow: 'hidden' }}>
                <div style={breakdownBarStyle((ihtLiability / netEstate) * 100, '#EF4444')}>
                  {formatCurrency(ihtLiability)}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Interactive parameters */}
        <div style={{ marginTop: '32px', padding: '24px', backgroundColor: '#F8FAFC', borderRadius: '8px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '16px' }}>Adjust your situation</h3>

          {/* Transferable NRB slider */}
          <div style={sliderContainerStyle}>
            <label htmlFor="transferableNRB" style={sliderLabelStyle}>
              Transferable NRB from spouse:{' '}
              <strong style={{ fontFamily: 'monospace' }}>{(transferableNRB / 325000 * 100).toFixed(0)}%</strong>
              {' '}({formatCurrency(transferableNRB)})
            </label>
            <input
              type="range"
              id="transferableNRB"
              min="0"
              max="325000"
              step="16250"
              value={transferableNRB}
              onChange={(e) => setTransferableNRB(parseInt(e.target.value))}
              style={sliderStyle}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94A3B8', marginTop: '4px' }}>
              <span>0%</span>
              <span>100%</span>
            </div>
          </div>

          {/* RNRB checkbox */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'flex', alignItems: 'center', fontSize: '0.875rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={rnrbApplicable}
                onChange={(e) => setRnrbApplicable(e.target.checked)}
                style={{ marginRight: '8px', width: '16px', height: '16px', cursor: 'pointer' }}
              />
              Leaving property to direct descendants (RNRB)
            </label>
          </div>

          {/* Charitable gifts slider */}
          <div style={sliderContainerStyle}>
            <label htmlFor="charitableGifts" style={sliderLabelStyle}>
              Charitable gifts:{' '}
              <strong style={{ fontFamily: 'monospace' }}>{charitableGifts}%</strong>
              {charitableGifts >= 10 && <span style={{ color: '#10B981' }}> (Reduces rate to 36%)</span>}
            </label>
            <input
              type="range"
              id="charitableGifts"
              min="0"
              max="50"
              step="1"
              value={charitableGifts}
              onChange={(e) => setCharitableGifts(parseInt(e.target.value))}
              style={sliderStyle}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94A3B8', marginTop: '4px' }}>
              <span>0%</span>
              <span>50%</span>
            </div>
          </div>
        </div>

        {/* Tell me more about nil rate bands */}
        <div
          onClick={() => toggleSection('nilRateBands')}
          style={expandableTriggerStyle}
        >
          <span style={{ marginRight: '8px' }}>{expandedSections.nilRateBands ? '▼' : '▶'}</span>
          Tell me more about nil rate bands
        </div>

        {expandedSections.nilRateBands && (
          <div style={{ marginTop: '12px', padding: '16px', backgroundColor: '#F8FAFC', borderRadius: '8px', fontSize: '0.875rem', color: '#475569', lineHeight: '1.7' }}>
            <p style={{ marginBottom: '12px' }}>
              The nil rate band means the first £325,000 of your estate is tax-free. This is called the "nil rate band" because there's nil (zero) tax on it.
            </p>
            <p style={{ marginBottom: '12px' }}>
              If your spouse has passed away and didn't use all of their nil rate band, you can claim the unused portion. This is called "transferable nil rate band" and can give you up to £650,000 tax-free.
            </p>
            <p>
              The residence nil rate band (RNRB) is an additional £175,000 tax-free allowance if you're leaving your home to children or grandchildren. However, it's tapered away if your estate exceeds £2 million.
            </p>
          </div>
        )}
      </div>

      {/* Asset Breakdown Table */}
      <div style={sectionStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={sectionHeadingStyle}>What you own</h2>
          <Button variant="primary" onClick={() => { setEditingAsset(null); setShowAssetModal(true); }}>
            Add Asset
          </Button>
        </div>

        {assetBreakdown?.assets && assetBreakdown.assets.length > 0 ? (
          <table style={tableStyle}>
            <thead>
              <tr>
                <th style={thStyle}>Asset</th>
                <th style={thStyle}>Type</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Value</th>
                <th style={{ ...thStyle, textAlign: 'center' }}>In UK Estate</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {assetBreakdown.assets.map((asset) => (
                <tr key={asset.id} style={{ transition: 'background-color 0.15s' }}>
                  <td style={tdStyle}>{asset.description}</td>
                  <td style={tdStyle}>{asset.assetType}</td>
                  <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'monospace' }}>
                    {formatCurrency(asset.currentValue)}
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'center' }}>
                    {asset.ukIhtApplicable ? (
                      <span style={{ color: '#10B981' }}>✓</span>
                    ) : (
                      <span style={{ color: '#94A3B8' }}>—</span>
                    )}
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'right' }}>
                    <Button
                      variant="outline"
                      onClick={() => { setEditingAsset(asset); setShowAssetModal(true); }}
                      style={actionButtonStyle}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => deleteAsset(asset.id)}
                      style={{ ...actionButtonStyle, color: '#EF4444', borderColor: '#EF4444' }}
                    >
                      Delete
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ ...narrativeParagraphStyle, textAlign: 'center', padding: '32px', color: '#94A3B8' }}>
            No assets added yet. Click "Add Asset" to get started.
          </p>
        )}
      </div>

      {/* Liabilities Table */}
      <div style={sectionStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={sectionHeadingStyle}>What you owe</h2>
          <Button variant="primary" onClick={() => { setEditingLiability(null); setShowLiabilityModal(true); }}>
            Add Liability
          </Button>
        </div>

        {estateData.liabilities && estateData.liabilities.length > 0 ? (
          <table style={tableStyle}>
            <thead>
              <tr>
                <th style={thStyle}>Liability</th>
                <th style={thStyle}>Type</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Amount</th>
                <th style={{ ...thStyle, textAlign: 'center' }}>Deductible</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {estateData.liabilities.map((liability) => (
                <tr key={liability.id}>
                  <td style={tdStyle}>{liability.description}</td>
                  <td style={tdStyle}>{liability.liabilityType}</td>
                  <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'monospace' }}>
                    {formatCurrency(liability.outstandingBalance)}
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'center' }}>
                    {liability.ukIhtDeductible ? (
                      <span style={{ color: '#10B981' }}>✓</span>
                    ) : (
                      <span style={{ color: '#EF4444' }}>✗</span>
                    )}
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'right' }}>
                    <Button
                      variant="outline"
                      onClick={() => { setEditingLiability(liability); setShowLiabilityModal(true); }}
                      style={actionButtonStyle}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => deleteLiability(liability.id)}
                      style={{ ...actionButtonStyle, color: '#EF4444', borderColor: '#EF4444' }}
                    >
                      Delete
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ ...narrativeParagraphStyle, textAlign: 'center', padding: '32px', color: '#94A3B8' }}>
            No liabilities added yet. Click "Add Liability" to record debts.
          </p>
        )}
      </div>

      {/* Action Section */}
      {recommendations && recommendations.length > 0 && (
        <div style={{ ...sectionStyle, backgroundColor: '#EFF6FF' }}>
          <h2 style={sectionHeadingStyle}>What to do next</h2>
          <p style={narrativeParagraphStyle}>
            The most effective ways to reduce Inheritance Tax are:
          </p>
          <ul style={{ paddingLeft: '20px', fontSize: '0.875rem', color: '#475569', lineHeight: '1.7' }}>
            {recommendations.map((rec, index) => (
              <li key={index} style={{ marginBottom: '8px' }}>
                {rec.title}: {rec.description}
                {rec.estimatedSaving?.gbp > 0 && (
                  <strong style={{ color: '#10B981', fontFamily: 'monospace' }}>
                    {' '}(Save {formatCurrency(rec.estimatedSaving.gbp)})
                  </strong>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {!hasIHTLiability && (
        <div style={calloutBoxStyle}>
          <p style={{ fontSize: '0.875rem', color: '#1E40AF', lineHeight: '1.7', margin: 0 }}>
            <strong>Good work!</strong> Your estate is currently within the tax-free allowances. Keep monitoring
            your estate value and consider lifetime gifting to stay ahead.
          </p>
        </div>
      )}
    </div>
  );
}
