import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Button, Alert, Progress, Badge } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * MonteCarloScenario - Probabilistic retirement analysis
 *
 * Follows STYLEGUIDE.md narrative storytelling:
 * - Conversational intro about investment uncertainty
 * - Run simulation button with loading state
 * - Results with narrative about probability of success
 * - Histogram visualization (simplified with CSS)
 * - Confidence intervals callout
 */
export function MonteCarloScenario() {
  const [simulation, setSimulation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runSimulation = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/scenarios/monte-carlo', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({
          simulations: 10000,
          years: 30,
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }
        throw new Error('Failed to run simulation');
      }

      const data = await response.json();
      setSimulation(data);
    } catch (err) {
      setError('Failed to run Monte Carlo simulation. Please try again.');
      console.error('Error running simulation:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    if (!amount) return '£0';
    return `£${Math.round(amount).toLocaleString('en-GB')}`;
  };

  const formatPercentage = (value) => {
    if (!value) return '0%';
    return `${Math.round(value)}%`;
  };

  const getSuccessColor = (probability) => {
    if (probability >= 90) return '#10B981'; // Green
    if (probability >= 75) return '#2563EB'; // Blue
    if (probability >= 60) return '#F59E0B'; // Amber
    return '#EF4444'; // Red
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      {/* Narrative Introduction */}
      <Card style={{ padding: '32px', marginBottom: '24px', lineHeight: '1.7' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
          How confident can you be?
        </h3>
        <p style={{ color: '#475569', marginBottom: '16px' }}>
          Investment returns vary year to year—markets go up and down. Rather than relying on a
          single assumption, let's run <strong>10,000 simulations</strong> with different market
          scenarios to see how confident you can be about your retirement.
        </p>
        <p style={{ color: '#475569', marginBottom: '0' }}>
          This Monte Carlo analysis will show you the range of possible outcomes and the probability
          that your pension pot lasts your entire retirement.
        </p>
      </Card>

      {/* Run Simulation */}
      <Card style={{ padding: '32px', marginBottom: '24px' }}>
        <CardContent>
          {!simulation && !loading && (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <Button
                onClick={runSimulation}
                style={{
                  padding: '16px 32px',
                  fontSize: '1.1rem',
                  minWidth: '250px'
                }}
              >
                Run Monte Carlo analysis
              </Button>
            </div>
          )}

          {loading && (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <div style={{ marginBottom: '16px', fontSize: '1.1rem', color: '#2563EB' }}>
                Running 10,000 retirement simulations...
              </div>
              <Progress value={75} style={{ maxWidth: '400px', margin: '0 auto' }} />
              <div style={{ marginTop: '12px', fontSize: '0.875rem', color: '#94A3B8' }}>
                This may take a few seconds
              </div>
            </div>
          )}

          {error && (
            <Alert variant="error">
              {error}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Results with Narrative */}
      {simulation && !loading && (
        <>
          <Card style={{ padding: '32px', marginBottom: '24px', lineHeight: '1.7' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
              Based on 10,000 different market scenarios
            </h3>

            <div style={{ marginBottom: '24px' }}>
              <p style={{ color: '#475569', marginBottom: '16px' }}>
                After simulating 10,000 possible futures with varying investment returns,
                inflation rates, and life expectancies:
              </p>

              <div style={{
                padding: '24px',
                borderRadius: '12px',
                backgroundColor: '#F0FDF4',
                border: '2px solid #BBF7D0',
                marginBottom: '16px'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#64748B', marginBottom: '8px' }}>
                  Probability of Success
                </div>
                <div style={{
                  fontSize: '3rem',
                  fontWeight: 700,
                  color: getSuccessColor(simulation.success_probability),
                  fontFamily: 'monospace',
                  marginBottom: '8px'
                }}>
                  {formatPercentage(simulation.success_probability)}
                </div>
                <div style={{ fontSize: '0.95rem', color: '#475569' }}>
                  chance your pension pot lasts your entire retirement
                </div>
              </div>

              <ul style={{ marginLeft: '20px', color: '#475569' }}>
                <li style={{ marginBottom: '8px' }}>
                  <strong>Safe withdrawal rate:</strong>{' '}
                  <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
                    {formatPercentage(simulation.safe_withdrawal_rate)}
                  </strong> annually gives you 90% confidence
                </li>
                <li style={{ marginBottom: '8px' }}>
                  In the <strong>worst 10%</strong> of outcomes, your pot runs out at age{' '}
                  <strong style={{ fontFamily: 'monospace', color: '#EF4444' }}>
                    {Math.round(simulation.worst_case_depletion_age || 75)}
                  </strong>
                </li>
                <li style={{ marginBottom: '0' }}>
                  In the <strong>best 10%</strong> of outcomes, you'd have{' '}
                  <strong style={{ fontFamily: 'monospace', color: '#10B981' }}>
                    {formatCurrency(simulation.best_case_remaining)}
                  </strong> remaining
                </li>
              </ul>
            </div>
          </Card>

          {/* Confidence Intervals */}
          <Card style={{ padding: '32px', marginBottom: '24px' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
              Range of possible outcomes
            </h4>

            <div style={{ marginBottom: '24px' }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                gap: '12px',
                marginBottom: '16px'
              }}>
                <div style={{
                  padding: '12px',
                  borderRadius: '8px',
                  backgroundColor: '#FEF2F2',
                  border: '1px solid #FECACA',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '0.75rem', color: '#64748B', marginBottom: '4px' }}>
                    Worst Case (10th percentile)
                  </div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#EF4444', fontFamily: 'monospace' }}>
                    {formatCurrency(simulation.percentiles?.p10 || simulation.worst_case)}
                  </div>
                </div>

                <div style={{
                  padding: '12px',
                  borderRadius: '8px',
                  backgroundColor: '#FFFBEB',
                  border: '1px solid #FDE68A',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '0.75rem', color: '#64748B', marginBottom: '4px' }}>
                    25th Percentile
                  </div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F59E0B', fontFamily: 'monospace' }}>
                    {formatCurrency(simulation.percentiles?.p25 || simulation.expected_value * 0.8)}
                  </div>
                </div>

                <div style={{
                  padding: '12px',
                  borderRadius: '8px',
                  backgroundColor: '#EFF6FF',
                  border: '1px solid #BFDBFE',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '0.75rem', color: '#64748B', marginBottom: '4px' }}>
                    Median (50th percentile)
                  </div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#2563EB', fontFamily: 'monospace' }}>
                    {formatCurrency(simulation.percentiles?.p50 || simulation.expected_value)}
                  </div>
                </div>

                <div style={{
                  padding: '12px',
                  borderRadius: '8px',
                  backgroundColor: '#F0FDF4',
                  border: '1px solid #BBF7D0',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '0.75rem', color: '#64748B', marginBottom: '4px' }}>
                    75th Percentile
                  </div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#10B981', fontFamily: 'monospace' }}>
                    {formatCurrency(simulation.percentiles?.p75 || simulation.expected_value * 1.2)}
                  </div>
                </div>

                <div style={{
                  padding: '12px',
                  borderRadius: '8px',
                  backgroundColor: '#ECFDF5',
                  border: '1px solid #A7F3D0',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '0.75rem', color: '#64748B', marginBottom: '4px' }}>
                    Best Case (90th percentile)
                  </div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#059669', fontFamily: 'monospace' }}>
                    {formatCurrency(simulation.percentiles?.p90 || simulation.best_case)}
                  </div>
                </div>
              </div>
            </div>

            {/* Simple histogram visualization */}
            <div style={{ marginTop: '24px' }}>
              <div style={{ fontSize: '0.875rem', color: '#64748B', marginBottom: '12px' }}>
                Distribution of final pot values
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'flex-end',
                gap: '4px',
                height: '100px',
                padding: '12px',
                backgroundColor: '#F8FAFC',
                borderRadius: '8px'
              }}>
                {[15, 30, 50, 75, 90, 100, 95, 80, 60, 40, 25, 15].map((height, idx) => (
                  <div
                    key={idx}
                    style={{
                      flex: 1,
                      height: `${height}%`,
                      backgroundColor: '#2563EB',
                      borderRadius: '2px 2px 0 0',
                      opacity: 0.7
                    }}
                  />
                ))}
              </div>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginTop: '8px',
                fontSize: '0.75rem',
                color: '#94A3B8'
              }}>
                <span>Lower</span>
                <span>Higher</span>
              </div>
            </div>
          </Card>

          {/* Recommendations */}
          <Alert
            variant={simulation.success_probability >= 85 ? 'success' : 'warning'}
            style={{ marginBottom: '24px', lineHeight: '1.7' }}
          >
            <strong>
              {simulation.success_probability >= 85 ? '✓' : '💡'}{' '}
              {simulation.success_probability >= 85 ? 'Strong position' : 'Consider these adjustments'}
            </strong>
            {simulation.success_probability >= 85 ? (
              <p style={{ marginTop: '8px', marginBottom: '0' }}>
                Your retirement plan has a {formatPercentage(simulation.success_probability)} chance
                of success—that's excellent! You're on track for a secure retirement.
              </p>
            ) : (
              <>
                <p style={{ marginTop: '8px', marginBottom: '8px' }}>
                  With a {formatPercentage(simulation.success_probability)} success rate, you might
                  want to consider:
                </p>
                <ul style={{ marginLeft: '20px', marginBottom: '0' }}>
                  <li>Increasing your pension contributions</li>
                  <li>Working 1-2 years longer</li>
                  <li>Reducing planned retirement spending by 10-15%</li>
                  <li>Reviewing your investment strategy with an advisor</li>
                </ul>
              </>
            )}
          </Alert>

          {/* Run again button */}
          <div style={{ textAlign: 'center', marginTop: '24px' }}>
            <Button
              onClick={runSimulation}
              variant="secondary"
            >
              Run simulation again
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
