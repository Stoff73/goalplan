import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Slider, Alert, Button } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * RetirementAgeScenario - Interactive retirement age modeling
 *
 * Follows STYLEGUIDE.md narrative storytelling:
 * - Conversational intro: "You're currently planning to retire at 65..."
 * - Interactive slider with real-time chart updates
 * - Results embedded in narrative sentences
 * - Comparison callout boxes
 * - Line height 1.7, generous spacing
 */
export function RetirementAgeScenario() {
  const [retirementAge, setRetirementAge] = useState(65);
  const [baselineAge, setBaselineAge] = useState(65);
  const [scenario, setScenario] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load user's current retirement age as baseline
    loadBaselineRetirementAge();
  }, []);

  useEffect(() => {
    if (retirementAge) {
      runScenario();
    }
  }, [retirementAge]);

  const loadBaselineRetirementAge = async () => {
    try {
      const response = await fetch('/api/v1/retirement/summary', {
        headers: {
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        const baseline = data.planned_retirement_age || 65;
        setBaselineAge(baseline);
        setRetirementAge(baseline);
      }
    } catch (err) {
      console.error('Failed to load baseline:', err);
      setBaselineAge(65);
      setRetirementAge(65);
    }
  };

  const runScenario = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/scenarios/retirement-age', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({
          retirement_age: retirementAge,
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }
        throw new Error('Failed to run scenario');
      }

      const data = await response.json();
      setScenario(data);
    } catch (err) {
      setError('Failed to calculate retirement scenario. Please try again.');
      console.error('Error running scenario:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    if (!amount) return '£0';
    return `£${Math.round(amount).toLocaleString('en-GB')}`;
  };

  const formatAge = (age) => {
    return Math.round(age);
  };

  const getComparisonText = () => {
    if (!scenario || retirementAge === baselineAge) return null;

    const diff = retirementAge - baselineAge;
    const direction = diff > 0 ? 'later' : 'earlier';
    const years = Math.abs(diff);

    const pensionDiff = scenario.pension_pot - (scenario.baseline_pension_pot || scenario.pension_pot);
    const incomeDiff = scenario.annual_income - (scenario.baseline_annual_income || scenario.annual_income);

    return {
      years,
      direction,
      pensionDiff,
      incomeDiff,
      isPositive: diff > 0,
    };
  };

  const comparison = getComparisonText();

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      {/* Narrative Introduction */}
      <Card style={{ padding: '32px', marginBottom: '24px', lineHeight: '1.7' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
          Explore when to retire
        </h3>
        <p style={{ color: '#475569', marginBottom: '16px' }}>
          You're currently planning to retire at <strong style={{ fontFamily: 'monospace' }}>{baselineAge}</strong>.
          But what if you could retire earlier—or needed to work longer? Let's explore how your retirement age
          affects your financial future.
        </p>
        <p style={{ color: '#475569', marginBottom: '0' }}>
          Use the slider below to see how different retirement ages impact your pension pot, annual income,
          and financial security throughout retirement.
        </p>
      </Card>

      {/* Interactive Slider */}
      <Card style={{ padding: '32px', marginBottom: '24px' }}>
        <CardHeader>
          <CardTitle>Try different retirement ages</CardTitle>
        </CardHeader>
        <CardContent>
          <div style={{ padding: '24px 0' }}>
            <Slider
              min={55}
              max={70}
              step={1}
              value={retirementAge}
              onChange={setRetirementAge}
              label="Retirement Age"
            />
          </div>

          {loading && (
            <div style={{ textAlign: 'center', padding: '20px', color: '#94A3B8' }}>
              Calculating projections...
            </div>
          )}

          {error && (
            <Alert variant="error" style={{ marginTop: '16px' }}>
              {error}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Results with Narrative */}
      {scenario && !loading && (
        <>
          <Card style={{ padding: '32px', marginBottom: '24px', lineHeight: '1.7' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
              If you retired at {retirementAge}
            </h3>

            <div style={{ marginBottom: '24px' }}>
              <p style={{ color: '#475569', marginBottom: '12px' }}>
                You'd have a pension pot of <strong style={{ fontFamily: 'monospace' }}>
                  {formatCurrency(scenario.pension_pot)}
                </strong> at retirement
                {retirementAge < baselineAge &&
                  ` (${baselineAge - retirementAge} years less growth)`
                }
                {retirementAge > baselineAge &&
                  ` (${retirementAge - baselineAge} years more growth)`
                }.
              </p>

              <p style={{ color: '#475569', marginBottom: '12px' }}>
                This would provide an annual income of <strong style={{ fontFamily: 'monospace' }}>
                  {formatCurrency(scenario.annual_income)}
                </strong> from age {retirementAge} using a safe 4% withdrawal rate.
              </p>

              <p style={{ color: '#475569', marginBottom: '0' }}>
                Your pot would last until you're approximately <strong style={{ fontFamily: 'monospace' }}>
                  {formatAge(scenario.pot_depletion_age || 90)}
                </strong>
                {scenario.pot_depletion_age && scenario.pot_depletion_age < 85 && (
                  <span style={{ color: '#EF4444', fontWeight: 500 }}>
                    {' '}(this is shorter than average life expectancy)
                  </span>
                )}
                {scenario.pot_depletion_age && scenario.pot_depletion_age >= 95 && (
                  <span style={{ color: '#10B981', fontWeight: 500 }}>
                    {' '}(comfortably beyond average life expectancy)
                  </span>
                )}.
              </p>
            </div>

            {scenario.state_pension_age && (
              <p style={{ color: '#475569', marginTop: '16px', fontSize: '0.95rem' }}>
                Plus, you'll receive State Pension of <strong style={{ fontFamily: 'monospace' }}>
                  {formatCurrency(scenario.state_pension_annual)}
                </strong> per year from age {scenario.state_pension_age}.
              </p>
            )}
          </Card>

          {/* Comparison Callout */}
          {comparison && (
            <Alert
              variant={comparison.isPositive ? 'info' : 'warning'}
              style={{ marginBottom: '24px', lineHeight: '1.7' }}
            >
              <strong>
                {comparison.isPositive ? '⏱️' : '⚠️'} Retiring {comparison.years} year{comparison.years > 1 ? 's' : ''} {comparison.direction}
              </strong>
              <p style={{ marginTop: '8px', marginBottom: '8px' }}>
                {comparison.isPositive ? (
                  <>
                    Working {comparison.years} more year{comparison.years > 1 ? 's' : ''} means{' '}
                    <strong>{formatCurrency(Math.abs(comparison.incomeDiff))}</strong> more
                    annual income in retirement.
                  </>
                ) : (
                  <>
                    Retiring {comparison.years} year{comparison.years > 1 ? 's' : ''} earlier means{' '}
                    <strong>{formatCurrency(Math.abs(comparison.incomeDiff))}</strong> less
                    annual income.
                  </>
                )}
              </p>
              {!comparison.isPositive && Math.abs(comparison.incomeDiff) > 5000 && (
                <p style={{ marginBottom: '0', fontSize: '0.95rem' }}>
                  💡 Consider working part-time until {baselineAge} to maintain your target income.
                </p>
              )}
            </Alert>
          )}

          {/* Simple visualization using CSS */}
          <Card style={{ padding: '32px', marginBottom: '24px' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
              Pension pot over time
            </h4>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
              gap: '16px',
              marginTop: '16px'
            }}>
              <div style={{
                padding: '16px',
                borderRadius: '8px',
                backgroundColor: '#EFF6FF',
                border: '1px solid #BFDBFE'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#64748B', marginBottom: '4px' }}>
                  At Retirement
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#2563EB', fontFamily: 'monospace' }}>
                  {formatCurrency(scenario.pension_pot)}
                </div>
              </div>

              <div style={{
                padding: '16px',
                borderRadius: '8px',
                backgroundColor: '#F0FDF4',
                border: '1px solid #BBF7D0'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#64748B', marginBottom: '4px' }}>
                  Annual Income
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#10B981', fontFamily: 'monospace' }}>
                  {formatCurrency(scenario.annual_income)}
                </div>
              </div>

              <div style={{
                padding: '16px',
                borderRadius: '8px',
                backgroundColor: '#FEF3C7',
                border: '1px solid #FDE68A'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#64748B', marginBottom: '4px' }}>
                  Pot Lasts Until
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#D97706', fontFamily: 'monospace' }}>
                  Age {formatAge(scenario.pot_depletion_age || 90)}
                </div>
              </div>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
