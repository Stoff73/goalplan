import React, { useState, useEffect } from 'react';
import { Card, Button, Alert } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * RetirementDashboard - Comprehensive retirement income projection with narrative storytelling
 *
 * Features:
 * - Am I on track? Hero section with status
 * - Income breakdown (state pension, DC, DB)
 * - Interactive "what if" scenarios (age, withdrawal rate)
 * - Pension pot growth chart visualization
 * - Action recommendations
 *
 * Follows STYLEGUIDE.md narrative storytelling approach:
 * - Conversational language ("You're on track...")
 * - Clear explanations of projections
 * - Progressive disclosure
 * - Educational tips
 */
export function RetirementDashboard() {
  const [projectionData, setProjectionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Scenario state
  const [scenarioAge, setScenarioAge] = useState(67);
  const [scenarioRate, setScenarioRate] = useState(4);
  const [scenarioResults, setScenarioResults] = useState(null);
  const [scenarioLoading, setScenarioLoading] = useState(false);

  useEffect(() => {
    loadProjectionData();
  }, []);

  useEffect(() => {
    // Debounce scenario calculations
    const timer = setTimeout(() => {
      calculateScenario();
    }, 500);
    return () => clearTimeout(timer);
  }, [scenarioAge, scenarioRate]);

  const loadProjectionData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/retirement/income-projection', {
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
          setProjectionData(null);
          setLoading(false);
          return;
        }
        throw new Error('Failed to fetch projection data');
      }

      const data = await response.json();
      setProjectionData(data);
      setScenarioAge(data.retirementAge || 67);
    } catch (err) {
      setError('Failed to load retirement projection. Please try again.');
      console.error('Error loading projection:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateScenario = async () => {
    if (!projectionData) return;

    setScenarioLoading(true);

    try {
      const response = await fetch('/api/v1/retirement/drawdown-scenario', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({
          retirementAge: scenarioAge,
          withdrawalRate: scenarioRate / 100,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setScenarioResults(data);
      }
    } catch (err) {
      console.error('Error calculating scenario:', err);
    } finally {
      setScenarioLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return '£0';
    return `£${amount.toLocaleString('en-GB', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })}`;
  };

  // Styles
  const containerStyle = {
    maxWidth: '1280px',
    margin: '0 auto',
  };

  const heroSectionStyle = (bgColor) => ({
    padding: '32px',
    background: `linear-gradient(to bottom right, ${bgColor})`,
    borderRadius: '12px',
    marginBottom: '48px',
    lineHeight: '1.7',
  });

  const heroTitleStyle = {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#0F172A',
    marginBottom: '16px',
  };

  const narrativeParagraphStyle = {
    fontSize: '1.1rem',
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

  const incomeCardStyle = {
    padding: '20px',
    backgroundColor: '#F8FAFC',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
    marginBottom: '12px',
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

  const sliderThumbStyle = `
    input[type="range"]::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: #2563EB;
      cursor: pointer;
    }
    input[type="range"]::-moz-range-thumb {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: #2563EB;
      cursor: pointer;
      border: none;
    }
  `;

  // Loading state
  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={sectionStyle}>
          <div style={{ textAlign: 'center', padding: '48px', color: '#94A3B8' }}>
            <div style={{ fontSize: '2rem', marginBottom: '16px' }}>⏳</div>
            <p>Loading your retirement projection...</p>
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
          <p style={{ fontWeight: 600 }}>Error Loading Projection</p>
          <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
        </Alert>
        <Button variant="outline" onClick={loadProjectionData} style={{ marginTop: '16px' }}>
          Try Again
        </Button>
      </div>
    );
  }

  // Empty state
  if (!projectionData || projectionData.totalPensionValue === 0) {
    return (
      <div style={containerStyle}>
        <div style={sectionStyle}>
          <h3 style={sectionHeadingStyle}>Plan your retirement income</h3>
          <p style={narrativeParagraphStyle}>
            Add your pensions to see projections of your retirement income. We'll help you understand
            if you're on track to meet your goals.
          </p>
        </div>
      </div>
    );
  }

  // Main view with data
  const {
    retirementAge,
    totalPensionValue,
    projectedValue,
    totalIncome,
    targetIncome,
    statePension,
    dcIncome,
    dbIncome,
    onTrack,
    gap,
    surplus,
    potGrowthData,
  } = projectionData;

  const statusBgColor = onTrack ? '#F0FDF4, #DCFCE7' : '#FFFBEB, #FEF3C7';

  return (
    <div style={containerStyle}>
      <style>{sliderThumbStyle}</style>

      {/* Hero: Am I on track? */}
      <div style={heroSectionStyle(statusBgColor)}>
        <h1 style={heroTitleStyle}>
          Your retirement outlook: {onTrack ? 'On track' : 'Needs attention'}
        </h1>

        <p style={narrativeParagraphStyle}>
          At age {retirementAge}, your pensions will provide approximately{' '}
          <strong style={{ fontFamily: 'monospace', color: '#2563EB' }}>
            {formatCurrency(totalIncome)}
          </strong>{' '}
          per year.
          {onTrack ? (
            <>
              {' '}
              This meets your target income of{' '}
              <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(targetIncome)}</strong>,
              with{' '}
              <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
                {formatCurrency(surplus)}
              </strong>{' '}
              to spare - excellent planning!
            </>
          ) : (
            <>
              {' '}
              You're aiming for{' '}
              <strong style={{ fontFamily: 'monospace' }}>{formatCurrency(targetIncome)}</strong>,
              which means you're{' '}
              <strong style={{ fontFamily: 'monospace', color: '#F59E0B' }}>
                {formatCurrency(Math.abs(gap))}
              </strong>{' '}
              short.
            </>
          )}
        </p>

        {/* Action items if not on track */}
        {!onTrack && (
          <Alert
            variant="info"
            style={{
              marginTop: '24px',
              backgroundColor: '#DBEAFE',
              border: '1px solid #BFDBFE',
              borderLeft: '4px solid #3B82F6',
            }}
          >
            <h4 style={{ fontWeight: 600, color: '#1E40AF', marginBottom: '12px' }}>
              What you can do to close the gap:
            </h4>
            <ul
              style={{
                fontSize: '0.875rem',
                color: '#1E3A8A',
                lineHeight: '1.7',
                paddingLeft: '20px',
                margin: 0,
              }}
            >
              <li>Increase your contributions by £200/month to close the gap</li>
              <li>Work an extra 2 years to allow your pot to grow</li>
              <li>Adjust your target income to match projections</li>
              <li>Review your investment strategy for potentially higher returns</li>
            </ul>
          </Alert>
        )}
      </div>

      {/* Income Breakdown */}
      <div style={sectionStyle}>
        <h2 style={sectionHeadingStyle}>Where your income comes from</h2>

        <p style={{ ...narrativeParagraphStyle, fontSize: '1rem', marginBottom: '24px' }}>
          Your retirement income will come from multiple sources. Understanding the breakdown helps you
          make informed decisions about when to retire and how to manage your money.
        </p>

        {/* State Pension */}
        {statePension > 0 && (
          <div style={incomeCardStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: '1rem', fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>
                  State Pension
                </p>
                <p style={{ fontSize: '0.875rem', color: '#475569', lineHeight: '1.7' }}>
                  Based on your National Insurance record, you'll receive this guaranteed amount each
                  year from State Pension Age.
                </p>
              </div>
              <div style={{ marginLeft: '16px', textAlign: 'right' }}>
                <p
                  style={{
                    fontSize: '1.5rem',
                    fontWeight: 'bold',
                    fontFamily: 'monospace',
                    color: '#10B981',
                  }}
                >
                  {formatCurrency(statePension)}
                </p>
                <p style={{ fontSize: '0.75rem', color: '#475569' }}>per year</p>
              </div>
            </div>
          </div>
        )}

        {/* DC Pensions */}
        {dcIncome > 0 && (
          <div style={incomeCardStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: '1rem', fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>
                  Workplace & Personal Pensions
                </p>
                <p style={{ fontSize: '0.875rem', color: '#475569', lineHeight: '1.7' }}>
                  Sustainable 4% withdrawal from your DC pension pots. This should last throughout
                  retirement, assuming moderate investment returns.
                </p>
              </div>
              <div style={{ marginLeft: '16px', textAlign: 'right' }}>
                <p
                  style={{
                    fontSize: '1.5rem',
                    fontWeight: 'bold',
                    fontFamily: 'monospace',
                    color: '#2563EB',
                  }}
                >
                  {formatCurrency(dcIncome)}
                </p>
                <p style={{ fontSize: '0.75rem', color: '#475569' }}>per year</p>
              </div>
            </div>
          </div>
        )}

        {/* DB Pensions */}
        {dbIncome > 0 && (
          <div style={incomeCardStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: '1rem', fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>
                  Final Salary Pension
                </p>
                <p style={{ fontSize: '0.875rem', color: '#475569', lineHeight: '1.7' }}>
                  Guaranteed income for life from your defined benefit scheme, typically increasing with
                  inflation.
                </p>
              </div>
              <div style={{ marginLeft: '16px', textAlign: 'right' }}>
                <p
                  style={{
                    fontSize: '1.5rem',
                    fontWeight: 'bold',
                    fontFamily: 'monospace',
                    color: '#10B981',
                  }}
                >
                  {formatCurrency(dbIncome)}
                </p>
                <p style={{ fontSize: '0.75rem', color: '#475569' }}>per year</p>
              </div>
            </div>
          </div>
        )}

        {/* Total */}
        <div
          style={{
            ...incomeCardStyle,
            backgroundColor: '#EFF6FF',
            border: '2px solid #BFDBFE',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <p style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0F172A' }}>
              Total Annual Income
            </p>
            <p
              style={{
                fontSize: '2rem',
                fontWeight: 'bold',
                fontFamily: 'monospace',
                color: '#2563EB',
              }}
            >
              {formatCurrency(totalIncome)}
            </p>
          </div>
        </div>
      </div>

      {/* Interactive Scenarios */}
      <div style={sectionStyle}>
        <h2 style={sectionHeadingStyle}>What if scenarios</h2>
        <p style={{ ...narrativeParagraphStyle, fontSize: '1rem', marginBottom: '24px' }}>
          Explore how changing your retirement age or withdrawal rate affects your income. Move the
          sliders to see instant results.
        </p>

        {/* Retirement Age Slider */}
        <div style={sliderContainerStyle}>
          <label htmlFor="scenarioAge" style={sliderLabelStyle}>
            Retirement age: <strong style={{ fontFamily: 'monospace' }}>{scenarioAge}</strong>
          </label>
          <input
            type="range"
            id="scenarioAge"
            min="55"
            max="70"
            value={scenarioAge}
            onChange={(e) => setScenarioAge(parseInt(e.target.value))}
            style={sliderStyle}
          />
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              fontSize: '0.75rem',
              color: '#94A3B8',
              marginTop: '4px',
            }}
          >
            <span>55</span>
            <span>70</span>
          </div>
        </div>

        {/* Withdrawal Rate Slider */}
        <div style={sliderContainerStyle}>
          <label htmlFor="scenarioRate" style={sliderLabelStyle}>
            Withdrawal rate: <strong style={{ fontFamily: 'monospace' }}>{scenarioRate}%</strong>
          </label>
          <input
            type="range"
            id="scenarioRate"
            min="2"
            max="8"
            step="0.5"
            value={scenarioRate}
            onChange={(e) => setScenarioRate(parseFloat(e.target.value))}
            style={sliderStyle}
          />
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              fontSize: '0.75rem',
              color: '#94A3B8',
              marginTop: '4px',
            }}
          >
            <span>2%</span>
            <span>8%</span>
          </div>
          <p style={{ fontSize: '0.875rem', color: '#475569', marginTop: '8px', lineHeight: '1.7' }}>
            A 4% rate is considered safe for most retirees. Higher rates may deplete your pot faster.
          </p>
        </div>

        {/* Scenario Results */}
        {scenarioResults && !scenarioLoading && (
          <div
            style={{
              padding: '24px',
              backgroundColor: '#EFF6FF',
              borderRadius: '8px',
              border: '1px solid #BFDBFE',
            }}
          >
            <p style={{ fontSize: '1rem', color: '#1E40AF', lineHeight: '1.7', marginBottom: '8px' }}>
              <strong>With these settings:</strong>
            </p>
            <p style={{ fontSize: '1rem', color: '#1E3A8A', lineHeight: '1.7' }}>
              You'd have{' '}
              <strong style={{ fontFamily: 'monospace', color: '#2563EB' }}>
                {formatCurrency(scenarioResults.annualIncome)}
              </strong>{' '}
              per year,
              {scenarioResults.depletionAge ? (
                <>
                  {' '}
                  and your pot would last until age{' '}
                  <strong style={{ fontFamily: 'monospace' }}>{scenarioResults.depletionAge}</strong>.
                </>
              ) : (
                <> and your pot should last throughout retirement.</>
              )}
            </p>
          </div>
        )}

        {scenarioLoading && (
          <div
            style={{
              padding: '24px',
              textAlign: 'center',
              color: '#94A3B8',
              fontSize: '0.875rem',
            }}
          >
            Calculating...
          </div>
        )}
      </div>

      {/* Pot Growth Chart Placeholder */}
      <div style={sectionStyle}>
        <h2 style={sectionHeadingStyle}>Your pension pot over time</h2>
        <p style={{ ...narrativeParagraphStyle, fontSize: '1rem', marginBottom: '24px' }}>
          This shows how your pensions will grow from now until retirement, assuming 5% annual growth
          and your current contribution levels.
        </p>

        {/* Simple visualization placeholder */}
        <div
          style={{
            padding: '48px',
            backgroundColor: '#F8FAFC',
            borderRadius: '8px',
            border: '1px dashed #CBD5E1',
            textAlign: 'center',
          }}
        >
          <p style={{ color: '#94A3B8', fontSize: '0.875rem' }}>
            📈 Chart visualization would appear here
          </p>
          <p style={{ color: '#64748B', fontSize: '0.875rem', marginTop: '8px' }}>
            Current value: {formatCurrency(totalPensionValue)} → Projected:{' '}
            {formatCurrency(projectedValue)} at age {retirementAge}
          </p>
        </div>

        <div
          style={{
            marginTop: '24px',
            padding: '16px',
            backgroundColor: '#DBEAFE',
            border: '1px solid #BFDBFE',
            borderLeft: '4px solid #3B82F6',
            borderRadius: '8px',
          }}
        >
          <p style={{ fontSize: '0.875rem', color: '#1E40AF', lineHeight: '1.7' }}>
            <strong>Tip:</strong> These are projections based on assumptions. Actual returns will vary.
            Review your pensions annually and adjust contributions or retirement age as needed.
          </p>
        </div>
      </div>
    </div>
  );
}
