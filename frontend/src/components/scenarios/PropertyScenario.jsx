import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Input, Label, Button, Alert, Badge } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * PropertyScenario - Property purchase affordability analysis
 *
 * Follows STYLEGUIDE.md narrative storytelling:
 * - Conversational intro about buying property
 * - Input fields for property details
 * - Affordability indicator with traffic light colors
 * - Results with narrative about monthly payments and impact
 * - Cash flow impact visualization
 */
export function PropertyScenario() {
  const [propertyValue, setPropertyValue] = useState('');
  const [deposit, setDeposit] = useState('');
  const [mortgageRate, setMortgageRate] = useState('');
  const [mortgageTerm, setMortgageTerm] = useState('25');
  const [scenario, setScenario] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runScenario = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/scenarios/property-purchase', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({
          property_value: parseFloat(propertyValue),
          deposit: parseFloat(deposit),
          mortgage_rate: parseFloat(mortgageRate),
          mortgage_term_years: parseInt(mortgageTerm),
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
      setError('Failed to calculate property scenario. Please try again.');
      console.error('Error running scenario:', err);
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

  const getAffordabilityStatus = () => {
    if (!scenario || !scenario.affordability_ratio) return null;

    const ratio = scenario.affordability_ratio;
    if (ratio <= 0.35) {
      return {
        variant: 'success',
        icon: '✓',
        label: 'Affordable',
        message: `Your mortgage is ${formatPercentage(ratio * 100)} of income (recommended < 35%)`,
      };
    } else if (ratio <= 0.45) {
      return {
        variant: 'warning',
        icon: '⚠',
        label: 'Tight',
        message: `Your mortgage is ${formatPercentage(ratio * 100)} of income (above recommended 35%)`,
      };
    } else {
      return {
        variant: 'error',
        icon: '✕',
        label: 'Unaffordable',
        message: `Your mortgage is ${formatPercentage(ratio * 100)} of income (risky)`,
      };
    }
  };

  const affordability = getAffordabilityStatus();
  const loanToValue = propertyValue && deposit ? ((parseFloat(propertyValue) - parseFloat(deposit)) / parseFloat(propertyValue)) * 100 : 0;

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      {/* Narrative Introduction */}
      <Card style={{ padding: '32px', marginBottom: '24px', lineHeight: '1.7' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
          Can you afford a property?
        </h3>
        <p style={{ color: '#475569', marginBottom: '16px' }}>
          Considering buying a property? Let's see if it fits your financial plan. We'll calculate
          your monthly mortgage payment, total interest, and impact on your cash flow.
        </p>
        <p style={{ color: '#475569', marginBottom: '0' }}>
          This will help you understand whether the property is affordable and what it means for
          your other financial goals.
        </p>
      </Card>

      {/* Input Form */}
      <Card style={{ padding: '32px', marginBottom: '24px' }}>
        <CardHeader>
          <CardTitle>Property details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={runScenario}>
            <div style={{ marginBottom: '20px' }}>
              <Label htmlFor="propertyValue">Property value</Label>
              <Input
                id="propertyValue"
                type="number"
                value={propertyValue}
                onChange={(e) => setPropertyValue(e.target.value)}
                placeholder="300000"
                required
                style={{ marginTop: '8px' }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <Label htmlFor="deposit">Deposit you have available</Label>
              <Input
                id="deposit"
                type="number"
                value={deposit}
                onChange={(e) => setDeposit(e.target.value)}
                placeholder="60000"
                required
                style={{ marginTop: '8px' }}
              />
              {propertyValue && deposit && (
                <div style={{ marginTop: '4px', fontSize: '0.875rem', color: '#64748B' }}>
                  {formatPercentage(loanToValue)} loan-to-value
                </div>
              )}
            </div>

            <div style={{ marginBottom: '20px' }}>
              <Label htmlFor="mortgageRate">Mortgage interest rate (%)</Label>
              <Input
                id="mortgageRate"
                type="number"
                step="0.01"
                value={mortgageRate}
                onChange={(e) => setMortgageRate(e.target.value)}
                placeholder="4.5"
                required
                style={{ marginTop: '8px' }}
              />
            </div>

            <div style={{ marginBottom: '24px' }}>
              <Label htmlFor="mortgageTerm">Mortgage term (years)</Label>
              <Input
                id="mortgageTerm"
                type="number"
                value={mortgageTerm}
                onChange={(e) => setMortgageTerm(e.target.value)}
                placeholder="25"
                required
                style={{ marginTop: '8px' }}
              />
            </div>

            <Button
              type="submit"
              disabled={loading || !propertyValue || !deposit || !mortgageRate || !mortgageTerm}
              style={{ width: '100%' }}
            >
              {loading ? 'Calculating...' : 'Check affordability'}
            </Button>
          </form>

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
              For a {formatCurrency(parseFloat(propertyValue))} property
            </h3>

            <div style={{ marginBottom: '24px' }}>
              <p style={{ color: '#475569', marginBottom: '12px' }}>
                With a <strong style={{ fontFamily: 'monospace' }}>
                  {formatCurrency(parseFloat(deposit))}
                </strong> deposit ({formatPercentage((parseFloat(deposit) / parseFloat(propertyValue)) * 100)}):
              </p>

              <ul style={{ marginLeft: '20px', color: '#475569' }}>
                <li style={{ marginBottom: '8px' }}>
                  Your monthly mortgage payment would be{' '}
                  <strong style={{ fontFamily: 'monospace', fontSize: '1.1rem' }}>
                    {formatCurrency(scenario.monthly_payment)}
                  </strong>
                </li>
                <li style={{ marginBottom: '8px' }}>
                  You'd pay{' '}
                  <strong style={{ fontFamily: 'monospace', color: '#EF4444' }}>
                    {formatCurrency(scenario.total_interest)}
                  </strong>{' '}
                  in interest over {mortgageTerm} years
                </li>
                <li style={{ marginBottom: '0' }}>
                  This leaves you{' '}
                  <strong style={{ fontFamily: 'monospace' }}>
                    {formatCurrency(scenario.remaining_monthly_income)}
                  </strong>/month for other expenses
                </li>
              </ul>
            </div>

            {scenario.stamp_duty && scenario.stamp_duty > 0 && (
              <p style={{
                color: '#475569',
                marginTop: '16px',
                padding: '12px',
                backgroundColor: '#FFFBEB',
                borderRadius: '8px',
                fontSize: '0.95rem'
              }}>
                <strong>Additional costs:</strong> Stamp duty of approximately{' '}
                <strong style={{ fontFamily: 'monospace' }}>
                  {formatCurrency(scenario.stamp_duty)}
                </strong> plus legal fees and surveys.
              </p>
            )}
          </Card>

          {/* Affordability Indicator */}
          {affordability && (
            <Alert variant={affordability.variant} style={{ marginBottom: '24px', lineHeight: '1.7' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span style={{ fontSize: '1.5rem' }}>{affordability.icon}</span>
                <strong style={{ fontSize: '1.1rem' }}>{affordability.label}</strong>
              </div>
              <p style={{ marginBottom: '0' }}>
                {affordability.message}
              </p>
              {affordability.variant === 'warning' && (
                <p style={{ marginTop: '8px', marginBottom: '0', fontSize: '0.95rem' }}>
                  💡 Consider a larger deposit or longer mortgage term to reduce monthly payments.
                </p>
              )}
              {affordability.variant === 'error' && (
                <p style={{ marginTop: '8px', marginBottom: '0', fontSize: '0.95rem' }}>
                  ⚠️ This mortgage may stretch your finances too thin. Consider a less expensive property
                  or saving for a larger deposit.
                </p>
              )}
            </Alert>
          )}

          {/* Cost breakdown */}
          <Card style={{ padding: '32px', marginBottom: '24px' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
              Cost breakdown
            </h4>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
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
                  Loan Amount
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#2563EB', fontFamily: 'monospace' }}>
                  {formatCurrency(parseFloat(propertyValue) - parseFloat(deposit))}
                </div>
              </div>

              <div style={{
                padding: '16px',
                borderRadius: '8px',
                backgroundColor: '#FEF2F2',
                border: '1px solid #FECACA'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#64748B', marginBottom: '4px' }}>
                  Total Interest
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#EF4444', fontFamily: 'monospace' }}>
                  {formatCurrency(scenario.total_interest)}
                </div>
              </div>

              <div style={{
                padding: '16px',
                borderRadius: '8px',
                backgroundColor: '#F0FDF4',
                border: '1px solid #BBF7D0'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#64748B', marginBottom: '4px' }}>
                  Total Repaid
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#10B981', fontFamily: 'monospace' }}>
                  {formatCurrency(scenario.total_repayment)}
                </div>
              </div>
            </div>
          </Card>

          {/* Cash flow impact */}
          {scenario.cash_flow_impact && (
            <Card style={{ padding: '32px', marginBottom: '24px', lineHeight: '1.7' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
                Impact on your finances
              </h4>
              <p style={{ color: '#475569', marginBottom: '12px' }}>
                This purchase would reduce your monthly savings capacity by{' '}
                <strong style={{ fontFamily: 'monospace', color: '#EF4444' }}>
                  {formatCurrency(Math.abs(scenario.cash_flow_impact))}
                </strong>.
              </p>
              {scenario.goal_impact && scenario.goal_impact.length > 0 && (
                <>
                  <p style={{ color: '#475569', marginBottom: '8px' }}>
                    This could affect your progress toward:
                  </p>
                  <ul style={{ marginLeft: '20px', color: '#475569', marginBottom: '0' }}>
                    {scenario.goal_impact.map((goal, idx) => (
                      <li key={idx} style={{ marginBottom: '4px' }}>{goal}</li>
                    ))}
                  </ul>
                </>
              )}
            </Card>
          )}
        </>
      )}
    </div>
  );
}
