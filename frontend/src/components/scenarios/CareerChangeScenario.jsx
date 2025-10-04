import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Input, Label, Button, Alert, Select } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * CareerChangeScenario - Model career change financial impact
 *
 * Follows STYLEGUIDE.md narrative storytelling:
 * - Conversational intro about career changes
 * - Input fields for new salary and date
 * - Results with narrative explaining impact
 * - Comparison charts showing before/after
 */
export function CareerChangeScenario() {
  const [newSalary, setNewSalary] = useState('');
  const [currency, setCurrency] = useState('GBP');
  const [changeDate, setChangeDate] = useState('');
  const [scenario, setScenario] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runScenario = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/scenarios/career-change', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({
          new_salary: parseFloat(newSalary),
          currency,
          change_date: changeDate,
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
      setError('Failed to calculate career change scenario. Please try again.');
      console.error('Error running scenario:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount, curr = currency) => {
    if (!amount) return '£0';
    const symbol = curr === 'GBP' ? '£' : curr === 'ZAR' ? 'R' : curr;
    return `${symbol}${Math.round(amount).toLocaleString('en-GB')}`;
  };

  const formatMonths = (months) => {
    if (!months) return '0 months';
    if (months < 12) return `${Math.round(months)} month${months > 1 ? 's' : ''}`;
    const years = Math.floor(months / 12);
    const remainingMonths = months % 12;
    if (remainingMonths === 0) return `${years} year${years > 1 ? 's' : ''}`;
    return `${years} year${years > 1 ? 's' : ''} and ${remainingMonths} month${remainingMonths > 1 ? 's' : ''}`;
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      {/* Narrative Introduction */}
      <Card style={{ padding: '32px', marginBottom: '24px', lineHeight: '1.7' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
          Model a job change
        </h3>
        <p style={{ color: '#475569', marginBottom: '16px' }}>
          Thinking about a career change? Whether it's a promotion, new job, or career switch,
          let's see how a change in salary affects your financial future.
        </p>
        <p style={{ color: '#475569', marginBottom: '0' }}>
          We'll calculate the impact on your take-home pay, pension contributions, net worth,
          and long-term financial goals.
        </p>
      </Card>

      {/* Input Form */}
      <Card style={{ padding: '32px', marginBottom: '24px' }}>
        <CardHeader>
          <CardTitle>Career change details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={runScenario}>
            <div style={{ marginBottom: '20px' }}>
              <Label htmlFor="newSalary">New annual salary</Label>
              <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                <Input
                  id="newSalary"
                  type="number"
                  value={newSalary}
                  onChange={(e) => setNewSalary(e.target.value)}
                  placeholder="50000"
                  required
                  style={{ flex: 1 }}
                />
                <Select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  style={{ width: '100px' }}
                >
                  <option value="GBP">GBP (£)</option>
                  <option value="ZAR">ZAR (R)</option>
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                </Select>
              </div>
            </div>

            <div style={{ marginBottom: '24px' }}>
              <Label htmlFor="changeDate">When would this happen?</Label>
              <Input
                id="changeDate"
                type="date"
                value={changeDate}
                onChange={(e) => setChangeDate(e.target.value)}
                required
                style={{ marginTop: '8px' }}
              />
            </div>

            <Button
              type="submit"
              disabled={loading || !newSalary || !changeDate}
              style={{ width: '100%' }}
            >
              {loading ? 'Calculating...' : 'Show me the impact'}
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
              {scenario.salary_change >= 0 ? '📈 ' : '📉 '}
              {scenario.salary_change >= 0 ? 'Good news!' : 'Impact analysis'}
            </h3>

            <div style={{ marginBottom: '24px' }}>
              <p style={{ color: '#475569', marginBottom: '12px' }}>
                A salary {scenario.salary_change >= 0 ? 'increase' : 'decrease'} of{' '}
                <strong style={{ fontFamily: 'monospace', color: scenario.salary_change >= 0 ? '#10B981' : '#EF4444' }}>
                  {formatCurrency(Math.abs(scenario.salary_change))}
                </strong>{' '}
                from <strong>{new Date(changeDate).toLocaleDateString('en-GB', { month: 'long', year: 'numeric' })}</strong>{' '}
                would mean:
              </p>

              <ul style={{ marginLeft: '20px', color: '#475569' }}>
                <li style={{ marginBottom: '8px' }}>
                  <strong style={{ fontFamily: 'monospace' }}>
                    {formatCurrency(scenario.monthly_takehome_change)}
                  </strong> {scenario.monthly_takehome_change >= 0 ? 'more' : 'less'} in monthly
                  take-home pay (after tax)
                </li>
                <li style={{ marginBottom: '8px' }}>
                  Your pension contributions would {scenario.pension_change >= 0 ? 'increase' : 'decrease'} by{' '}
                  <strong style={{ fontFamily: 'monospace' }}>
                    {formatCurrency(Math.abs(scenario.pension_change_monthly))}
                  </strong>/month
                </li>
                {scenario.break_even_months && (
                  <li style={{ marginBottom: '8px' }}>
                    You'd break even on the change within{' '}
                    <strong>{formatMonths(scenario.break_even_months)}</strong>
                  </li>
                )}
                <li style={{ marginBottom: '0' }}>
                  Your net worth would be{' '}
                  <strong style={{ fontFamily: 'monospace', color: scenario.net_worth_impact >= 0 ? '#10B981' : '#EF4444' }}>
                    {formatCurrency(Math.abs(scenario.net_worth_impact))}
                  </strong>{' '}
                  {scenario.net_worth_impact >= 0 ? 'higher' : 'lower'} by retirement
                </li>
              </ul>
            </div>

            {scenario.tax_impact && (
              <p style={{
                color: '#475569',
                marginTop: '16px',
                padding: '12px',
                backgroundColor: '#F8FAFC',
                borderRadius: '8px',
                fontSize: '0.95rem'
              }}>
                <strong>Tax impact:</strong> Your annual tax bill would{' '}
                {scenario.tax_impact >= 0 ? 'increase' : 'decrease'} by approximately{' '}
                <strong style={{ fontFamily: 'monospace' }}>
                  {formatCurrency(Math.abs(scenario.tax_impact))}
                </strong>.
              </p>
            )}
          </Card>

          {/* Comparison visualization */}
          <Card style={{ padding: '32px', marginBottom: '24px' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
              Before vs After comparison
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
                backgroundColor: '#F8FAFC',
                border: '1px solid #E2E8F0'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#64748B', marginBottom: '4px' }}>
                  Current Salary
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#475569', fontFamily: 'monospace' }}>
                  {formatCurrency(scenario.current_salary)}
                </div>
              </div>

              <div style={{
                padding: '16px',
                borderRadius: '8px',
                backgroundColor: scenario.salary_change >= 0 ? '#F0FDF4' : '#FEF2F2',
                border: `1px solid ${scenario.salary_change >= 0 ? '#BBF7D0' : '#FECACA'}`
              }}>
                <div style={{ fontSize: '0.875rem', color: '#64748B', marginBottom: '4px' }}>
                  New Salary
                </div>
                <div style={{
                  fontSize: '1.25rem',
                  fontWeight: 700,
                  color: scenario.salary_change >= 0 ? '#10B981' : '#EF4444',
                  fontFamily: 'monospace'
                }}>
                  {formatCurrency(parseFloat(newSalary))}
                </div>
              </div>

              <div style={{
                padding: '16px',
                borderRadius: '8px',
                backgroundColor: '#EFF6FF',
                border: '1px solid #BFDBFE'
              }}>
                <div style={{ fontSize: '0.875rem', color: '#64748B', marginBottom: '4px' }}>
                  Monthly Change
                </div>
                <div style={{
                  fontSize: '1.25rem',
                  fontWeight: 700,
                  color: '#2563EB',
                  fontFamily: 'monospace'
                }}>
                  {scenario.monthly_takehome_change >= 0 ? '+' : ''}
                  {formatCurrency(scenario.monthly_takehome_change)}
                </div>
              </div>
            </div>
          </Card>

          {/* Recommendations */}
          {scenario.recommendations && scenario.recommendations.length > 0 && (
            <Alert variant="info" style={{ marginBottom: '24px', lineHeight: '1.7' }}>
              <strong>💡 What to consider:</strong>
              <ul style={{ marginTop: '8px', marginLeft: '20px', marginBottom: '0' }}>
                {scenario.recommendations.map((rec, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>{rec}</li>
                ))}
              </ul>
            </Alert>
          )}
        </>
      )}
    </div>
  );
}
