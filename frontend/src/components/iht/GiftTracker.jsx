import React, { useState, useEffect } from 'react';
import { Card, Button, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * GiftTracker - Lifetime gifts and PET tracking with 7-year timeline visualization
 *
 * Features:
 * - Hero section with total gifts in last 7 years
 * - 7-year timeline visualization with color coding
 * - Gift list table with years remaining
 * - Annual exemption tracker
 * - Smart gifting strategies recommendations
 *
 * Follows STYLEGUIDE.md narrative storytelling approach:
 * - Conversational language about 7-year rule
 * - Visual timeline with progressive disclosure
 * - Educational tips about exemptions
 */
export function GiftTracker() {
  const [giftsData, setGiftsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showGiftModal, setShowGiftModal] = useState(false);
  const [editingGift, setEditingGift] = useState(null);

  useEffect(() => {
    loadGiftsData();
  }, []);

  const loadGiftsData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/iht/gifts/pet-period', {
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
          setGiftsData(null);
          setLoading(false);
          return;
        }
        throw new Error('Failed to fetch gifts data');
      }

      const data = await response.json();
      setGiftsData(data);
    } catch (err) {
      setError('Failed to load gifts data. Please try again.');
      console.error('Error loading gifts:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteGift = async (giftId) => {
    if (!confirm('Are you sure you want to delete this gift?')) return;

    try {
      const response = await fetch(`/api/v1/iht/gifts/${giftId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (response.ok) {
        loadGiftsData();
      }
    } catch (err) {
      console.error('Error deleting gift:', err);
      alert('Failed to delete gift');
    }
  };

  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return '£0';
    return `£${Math.abs(amount).toLocaleString('en-GB', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  const getColorForYearsRemaining = (yearsRemaining) => {
    if (yearsRemaining >= 7) return '#3B82F6'; // Blue - exempt
    if (yearsRemaining >= 5) return '#10B981'; // Green - 60-80% relief
    if (yearsRemaining >= 3) return '#F59E0B'; // Amber - 20-40% relief
    return '#EF4444'; // Red - 0% relief
  };

  const getTaperReliefText = (yearsRemaining) => {
    if (yearsRemaining >= 7) return '100% relief (Exempt)';
    if (yearsRemaining >= 6) return '80% taper relief';
    if (yearsRemaining >= 5) return '60% taper relief';
    if (yearsRemaining >= 4) return '40% taper relief';
    if (yearsRemaining >= 3) return '20% taper relief';
    return 'No taper relief';
  };

  // Styles
  const containerStyle = {
    maxWidth: '1280px',
    margin: '0 auto',
  };

  const heroSectionStyle = {
    padding: '32px',
    background: 'linear-gradient(to bottom right, #ECFDF5, #D1FAE5)',
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

  const timelineContainerStyle = {
    position: 'relative',
    padding: '32px 0',
    marginTop: '24px',
  };

  const timelineBarStyle = {
    height: '8px',
    backgroundColor: '#E2E8F0',
    borderRadius: '4px',
    position: 'relative',
    marginBottom: '32px',
  };

  const timelineMarkerStyle = (position, color) => ({
    position: 'absolute',
    left: `${position}%`,
    top: '-12px',
    width: '32px',
    height: '32px',
    backgroundColor: color,
    borderRadius: '50%',
    border: '3px solid #FFFFFF',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#FFFFFF',
    fontSize: '0.75rem',
    fontWeight: 600,
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

  const badgeStyle = (color) => ({
    display: 'inline-block',
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '0.75rem',
    fontWeight: 600,
    backgroundColor: `${color}20`,
    color: color,
  });

  const progressBarStyle = (percentage, color) => ({
    width: '100%',
    height: '8px',
    backgroundColor: '#E2E8F0',
    borderRadius: '4px',
    overflow: 'hidden',
    position: 'relative',
  });

  const progressFillStyle = (percentage, color) => ({
    width: `${percentage}%`,
    height: '100%',
    backgroundColor: color,
    transition: 'width 0.3s ease',
  });

  const actionButtonStyle = {
    padding: '6px 12px',
    fontSize: '0.75rem',
    marginLeft: '8px',
  };

  const calloutBoxStyle = {
    padding: '16px',
    backgroundColor: '#DBEAFE',
    border: '1px solid #BFDBFE',
    borderLeft: '4px solid #3B82F6',
    borderRadius: '8px',
    marginTop: '16px',
  };

  // Loading state
  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={sectionStyle}>
          <div style={{ textAlign: 'center', padding: '48px', color: '#94A3B8' }}>
            <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⏳</div>
            <p>Loading your gift history...</p>
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
          <p style={{ fontWeight: 600 }}>Error Loading Gifts</p>
          <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
        </Alert>
        <Button variant="outline" onClick={loadGiftsData} style={{ marginTop: '16px' }}>
          Try Again
        </Button>
      </div>
    );
  }

  // Empty state
  if (!giftsData || !giftsData.gifts || giftsData.gifts.length === 0) {
    return (
      <div style={containerStyle}>
        <div style={sectionStyle}>
          <h3 style={sectionHeadingStyle}>Track your lifetime gifts</h3>
          <p style={narrativeParagraphStyle}>
            Record gifts you've made to track the 7-year rule and understand potential IHT implications.
            Gifts become tax-free if you survive 7 years after making them.
          </p>
          <Button variant="primary" onClick={() => { setEditingGift(null); setShowGiftModal(true); }} style={{ marginTop: '16px' }}>
            Record Your First Gift
          </Button>
        </div>
      </div>
    );
  }

  // Main view with data
  const {
    totalGiftsLast7Years,
    activePETCount,
    potentialIHTIfDeathToday,
    gifts,
    annualExemption,
  } = giftsData;

  return (
    <div style={containerStyle}>
      {/* Hero Section */}
      <div style={heroSectionStyle}>
        <h1 style={heroTitleStyle}>
          You've given <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
            {formatCurrency(totalGiftsLast7Years)}
          </strong> in the last 7 years
        </h1>

        <p style={narrativeParagraphStyle}>
          That's good news! Lifetime gifts become tax-free after 7 years. You have{' '}
          <strong style={{ fontFamily: 'monospace' }}>{activePETCount}</strong>{' '}
          {activePETCount === 1 ? 'gift' : 'gifts'} that {activePETCount === 1 ? 'is' : 'are'} still in the 7-year window.
          {potentialIHTIfDeathToday > 0 && (
            <>
              {' '}If you were to pass away today, they might incur{' '}
              <strong style={{ fontFamily: 'monospace', color: '#F59E0B' }}>
                {formatCurrency(potentialIHTIfDeathToday)}
              </strong>{' '}
              in Inheritance Tax.
            </>
          )}
        </p>

        <p style={{ fontSize: '0.875rem', color: '#64748B', lineHeight: '1.7' }}>
          The good news: the tax reduces each year. After 3 years, you get 20% relief. After 7 years, they're
          completely tax-free.
        </p>
      </div>

      {/* 7-Year Timeline Visualization */}
      <div style={sectionStyle}>
        <h2 style={sectionHeadingStyle}>Your 7-year gift timeline</h2>

        <div style={timelineContainerStyle}>
          {/* Timeline bar with markers */}
          <div style={timelineBarStyle}>
            {gifts.map((gift) => {
              const yearsElapsed = gift.yearsElapsed || 0;
              const position = (yearsElapsed / 7) * 100;
              const color = getColorForYearsRemaining(gift.yearsRemaining);

              return (
                <div
                  key={gift.id}
                  style={timelineMarkerStyle(position, color)}
                  title={`${gift.recipientName}: ${formatCurrency(gift.giftValue)} (${formatDate(gift.giftDate)})`}
                >
                  £
                </div>
              );
            })}
          </div>

          {/* Timeline labels */}
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94A3B8' }}>
            <span>Today</span>
            <span>3 years</span>
            <span>5 years</span>
            <span>7 years (Exempt)</span>
          </div>

          {/* Color legend */}
          <div style={{ display: 'flex', gap: '16px', marginTop: '24px', fontSize: '0.875rem' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ width: '16px', height: '16px', backgroundColor: '#EF4444', borderRadius: '50%', marginRight: '8px' }} />
              <span>0-3 years (No relief)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ width: '16px', height: '16px', backgroundColor: '#F59E0B', borderRadius: '50%', marginRight: '8px' }} />
              <span>3-5 years (20-40% relief)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ width: '16px', height: '16px', backgroundColor: '#10B981', borderRadius: '50%', marginRight: '8px' }} />
              <span>5-7 years (60-80% relief)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ width: '16px', height: '16px', backgroundColor: '#3B82F6', borderRadius: '50%', marginRight: '8px' }} />
              <span>7+ years (Exempt)</span>
            </div>
          </div>
        </div>

        <div style={calloutBoxStyle}>
          <p style={{ fontSize: '0.875rem', color: '#1E40AF', lineHeight: '1.7', margin: 0 }}>
            <strong>Tell me more about the 7-year rule:</strong> When you give money away, it's called a
            "potentially exempt transfer" (PET). If you survive 7 years after making the gift, it becomes
            completely tax-free. If you die within 7 years, the gift is added back to your estate and may be
            taxed. However, taper relief reduces the tax if you survive more than 3 years.
          </p>
        </div>
      </div>

      {/* Gift List Table */}
      <div style={sectionStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={sectionHeadingStyle}>Your lifetime gifts</h2>
          <Button variant="primary" onClick={() => { setEditingGift(null); setShowGiftModal(true); }}>
            Record Gift
          </Button>
        </div>

        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>Recipient</th>
              <th style={thStyle}>Date</th>
              <th style={{ ...thStyle, textAlign: 'right' }}>Value</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Years Remaining</th>
              <th style={{ ...thStyle, textAlign: 'right' }}>Potential Tax</th>
              <th style={{ ...thStyle, textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {gifts.map((gift) => {
              const color = getColorForYearsRemaining(gift.yearsRemaining);
              const taperText = getTaperReliefText(gift.yearsRemaining);

              return (
                <tr key={gift.id}>
                  <td style={tdStyle}>{gift.recipientName}</td>
                  <td style={tdStyle}>{formatDate(gift.giftDate)}</td>
                  <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'monospace' }}>
                    {formatCurrency(gift.giftValue)}
                  </td>
                  <td style={tdStyle}>
                    <span style={badgeStyle(color)}>
                      {gift.classification}
                    </span>
                  </td>
                  <td style={tdStyle}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={progressBarStyle(100, '#E2E8F0')}>
                        <div style={progressFillStyle(((7 - gift.yearsRemaining) / 7) * 100, color)} />
                      </div>
                      <span style={{ fontSize: '0.75rem', color: '#64748B', whiteSpace: 'nowrap' }}>
                        {gift.yearsRemaining.toFixed(1)} years
                      </span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '4px' }}>
                      {taperText}
                    </div>
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'monospace', color: gift.potentialIHT > 0 ? '#F59E0B' : '#10B981' }}>
                    {formatCurrency(gift.potentialIHT)}
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'right' }}>
                    <Button
                      variant="outline"
                      onClick={() => { setEditingGift(gift); setShowGiftModal(true); }}
                      style={actionButtonStyle}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => deleteGift(gift.id)}
                      style={{ ...actionButtonStyle, color: '#EF4444', borderColor: '#EF4444' }}
                    >
                      Delete
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Exemption Tracker */}
      {annualExemption && (
        <div style={sectionStyle}>
          <h2 style={sectionHeadingStyle}>Your tax-free allowances</h2>

          <div style={{ marginBottom: '24px' }}>
            {/* Annual exemption */}
            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.875rem', color: '#0F172A' }}>
                  Annual exemption (2024/25)
                </span>
                <span style={{ fontSize: '0.875rem', fontFamily: 'monospace', color: '#475569' }}>
                  {formatCurrency(annualExemption.available)} of £3,000 remaining
                </span>
              </div>
              <div style={progressBarStyle(100, '#E2E8F0')}>
                <div style={progressFillStyle((annualExemption.used / 3000) * 100, '#10B981')} />
              </div>
            </div>

            {/* Carried forward */}
            {annualExemption.carriedForward > 0 && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
                  <span style={{ color: '#0F172A' }}>Carried forward from last year</span>
                  <span style={{ fontFamily: 'monospace', color: '#10B981' }}>
                    {formatCurrency(annualExemption.carriedForward)}
                  </span>
                </div>
              </div>
            )}
          </div>

          <div style={calloutBoxStyle}>
            <p style={{ fontSize: '0.875rem', color: '#1E40AF', lineHeight: '1.7', margin: 0 }}>
              <strong>Tell me more about exemptions:</strong> You can give away £3,000 each year without it
              counting towards your estate. If you don't use it all, you can carry forward one year's unused
              amount. There are also other exemptions like £250 to unlimited people (small gifts) and wedding
              gifts up to £5,000 to children.
            </p>
          </div>
        </div>
      )}

      {/* Action Section - Smart Gifting Strategies */}
      <div style={{ ...sectionStyle, backgroundColor: '#ECFDF5' }}>
        <h2 style={sectionHeadingStyle}>Smart gifting strategies</h2>
        <ul style={{ paddingLeft: '20px', fontSize: '0.875rem', color: '#475569', lineHeight: '1.7' }}>
          <li style={{ marginBottom: '8px' }}>
            Use your £3,000 annual exemption each year (you can carry forward one year)
          </li>
          <li style={{ marginBottom: '8px' }}>
            Give £250 to as many people as you like (small gifts exemption)
          </li>
          <li style={{ marginBottom: '8px' }}>
            Wedding gifts are exempt: £5,000 to children, £2,500 to grandchildren, £1,000 to others
          </li>
          <li style={{ marginBottom: '8px' }}>
            Regular gifts from income are immediately exempt if they leave you with enough to maintain
            your lifestyle (keep records!)
          </li>
          <li>
            Consider making larger gifts earlier to maximize the chance they become exempt within your lifetime
          </li>
        </ul>
      </div>
    </div>
  );
}
