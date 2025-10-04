import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Button, Alert, Badge } from 'internal-packages/ui';
import { authStorage } from '../../utils/auth';

/**
 * ScenarioComparison - Side-by-side scenario comparison
 *
 * Follows STYLEGUIDE.md narrative storytelling:
 * - Conversational intro about comparing options
 * - Multi-select for scenarios
 * - Comparison table with narrative column headers
 * - Highlighted differences with color coding
 */
export function ScenarioComparison() {
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenarios, setSelectedScenarios] = useState([]);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    try {
      const response = await fetch('/api/v1/scenarios', {
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
        throw new Error('Failed to load scenarios');
      }

      const data = await response.json();
      setScenarios(data);
    } catch (err) {
      console.error('Error loading scenarios:', err);
    }
  };

  const compareScenarios = async () => {
    if (selectedScenarios.length < 2) {
      setError('Please select at least 2 scenarios to compare');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/scenarios/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({
          scenario_ids: selectedScenarios,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to compare scenarios');
      }

      const data = await response.json();
      setComparison(data);
    } catch (err) {
      setError('Failed to compare scenarios. Please try again.');
      console.error('Error comparing scenarios:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleScenario = (scenarioId) => {
    if (selectedScenarios.includes(scenarioId)) {
      setSelectedScenarios(selectedScenarios.filter(id => id !== scenarioId));
    } else {
      if (selectedScenarios.length >= 3) {
        setError('You can compare up to 3 scenarios at once');
        return;
      }
      setSelectedScenarios([...selectedScenarios, scenarioId]);
    }
    setError(null);
  };

  const formatCurrency = (amount) => {
    if (!amount) return '£0';
    return `£${Math.round(amount).toLocaleString('en-GB')}`;
  };

  const formatPercentage = (value) => {
    if (!value) return '0%';
    return `${Math.round(value)}%`;
  };

  const getDifferenceColor = (value, higher_is_better = true) => {
    if (!value || value === 0) return '#64748B';
    if (higher_is_better) {
      return value > 0 ? '#10B981' : '#EF4444';
    } else {
      return value < 0 ? '#10B981' : '#EF4444';
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      {/* Narrative Introduction */}
      <Card style={{ padding: '32px', marginBottom: '24px', lineHeight: '1.7' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
          Compare your scenarios side-by-side
        </h3>
        <p style={{ color: '#475569', marginBottom: '16px' }}>
          Making a big decision? Compare different scenarios to see which option works best for
          your financial future. Select 2-3 scenarios below to see a detailed comparison.
        </p>
        <p style={{ color: '#475569', marginBottom: '0' }}>
          We'll highlight the key differences and help you understand the trade-offs between
          each option.
        </p>
      </Card>

      {/* Scenario Selection */}
      <Card style={{ padding: '32px', marginBottom: '24px' }}>
        <CardHeader>
          <CardTitle>Choose scenarios to compare</CardTitle>
        </CardHeader>
        <CardContent>
          {scenarios.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#94A3B8' }}>
              <p>No scenarios available to compare.</p>
              <p style={{ fontSize: '0.875rem', marginTop: '8px' }}>
                Create some scenarios using the tabs above first.
              </p>
            </div>
          ) : (
            <>
              <div style={{ display: 'grid', gap: '12px', marginBottom: '20px' }}>
                {scenarios.map((scenario) => (
                  <div
                    key={scenario.id}
                    onClick={() => toggleScenario(scenario.id)}
                    style={{
                      padding: '16px',
                      border: selectedScenarios.includes(scenario.id)
                        ? '2px solid #2563EB'
                        : '1px solid #E2E8F0',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      backgroundColor: selectedScenarios.includes(scenario.id)
                        ? '#EFF6FF'
                        : '#FFFFFF',
                      transition: 'all 150ms ease-in-out'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontWeight: 600, color: '#0F172A', marginBottom: '4px' }}>
                          {scenario.name}
                        </div>
                        <div style={{ fontSize: '0.875rem', color: '#64748B' }}>
                          {scenario.scenario_type}
                        </div>
                      </div>
                      {selectedScenarios.includes(scenario.id) && (
                        <Badge variant="info">Selected</Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <Button
                onClick={compareScenarios}
                disabled={loading || selectedScenarios.length < 2}
                style={{ width: '100%' }}
              >
                {loading ? 'Comparing...' : `Compare ${selectedScenarios.length} scenario${selectedScenarios.length > 1 ? 's' : ''}`}
              </Button>

              {error && (
                <Alert variant="error" style={{ marginTop: '16px' }}>
                  {error}
                </Alert>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Comparison Results */}
      {comparison && !loading && (
        <>
          <Card style={{ padding: '32px', marginBottom: '24px', lineHeight: '1.7' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px', color: '#0F172A' }}>
              Comparison results
            </h3>

            {/* Comparison table */}
            <div style={{ overflowX: 'auto' }}>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                fontSize: '0.95rem'
              }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #E2E8F0' }}>
                    <th style={{
                      textAlign: 'left',
                      padding: '12px',
                      fontWeight: 600,
                      color: '#0F172A'
                    }}>
                      What changes?
                    </th>
                    {comparison.scenarios.map((scenario) => (
                      <th
                        key={scenario.id}
                        style={{
                          textAlign: 'right',
                          padding: '12px',
                          fontWeight: 600,
                          color: '#0F172A'
                        }}
                      >
                        {scenario.name}
                      </th>
                    ))}
                    <th style={{
                      textAlign: 'right',
                      padding: '12px',
                      fontWeight: 600,
                      color: '#0F172A'
                    }}>
                      Difference
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {/* Net Worth */}
                  <tr style={{ borderBottom: '1px solid #F1F5F9' }}>
                    <td style={{ padding: '12px', color: '#475569' }}>
                      Net worth at retirement
                    </td>
                    {comparison.scenarios.map((scenario) => (
                      <td
                        key={scenario.id}
                        style={{
                          textAlign: 'right',
                          padding: '12px',
                          fontFamily: 'monospace',
                          fontWeight: 600
                        }}
                      >
                        {formatCurrency(scenario.results?.net_worth_at_retirement)}
                      </td>
                    ))}
                    <td style={{
                      textAlign: 'right',
                      padding: '12px',
                      fontFamily: 'monospace',
                      fontWeight: 600,
                      color: getDifferenceColor(
                        comparison.metrics?.net_worth_difference,
                        true
                      )
                    }}>
                      {comparison.metrics?.net_worth_difference
                        ? formatCurrency(Math.abs(comparison.metrics.net_worth_difference))
                        : '-'
                      }
                    </td>
                  </tr>

                  {/* Retirement Income */}
                  <tr style={{ borderBottom: '1px solid #F1F5F9' }}>
                    <td style={{ padding: '12px', color: '#475569' }}>
                      Annual retirement income
                    </td>
                    {comparison.scenarios.map((scenario) => (
                      <td
                        key={scenario.id}
                        style={{
                          textAlign: 'right',
                          padding: '12px',
                          fontFamily: 'monospace',
                          fontWeight: 600
                        }}
                      >
                        {formatCurrency(scenario.results?.retirement_income)}
                      </td>
                    ))}
                    <td style={{
                      textAlign: 'right',
                      padding: '12px',
                      fontFamily: 'monospace',
                      fontWeight: 600,
                      color: getDifferenceColor(
                        comparison.metrics?.income_difference,
                        true
                      )
                    }}>
                      {comparison.metrics?.income_difference
                        ? formatCurrency(Math.abs(comparison.metrics.income_difference))
                        : '-'
                      }
                    </td>
                  </tr>

                  {/* Lifetime Tax */}
                  <tr style={{ borderBottom: '1px solid #F1F5F9' }}>
                    <td style={{ padding: '12px', color: '#475569' }}>
                      Lifetime tax paid
                    </td>
                    {comparison.scenarios.map((scenario) => (
                      <td
                        key={scenario.id}
                        style={{
                          textAlign: 'right',
                          padding: '12px',
                          fontFamily: 'monospace',
                          fontWeight: 600
                        }}
                      >
                        {formatCurrency(scenario.results?.lifetime_tax)}
                      </td>
                    ))}
                    <td style={{
                      textAlign: 'right',
                      padding: '12px',
                      fontFamily: 'monospace',
                      fontWeight: 600,
                      color: getDifferenceColor(
                        comparison.metrics?.tax_difference,
                        false
                      )
                    }}>
                      {comparison.metrics?.tax_difference
                        ? formatCurrency(Math.abs(comparison.metrics.tax_difference))
                        : '-'
                      }
                    </td>
                  </tr>

                  {/* Retirement Age */}
                  {comparison.metrics?.retirement_age_difference !== undefined && (
                    <tr style={{ borderBottom: '1px solid #F1F5F9' }}>
                      <td style={{ padding: '12px', color: '#475569' }}>
                        Retirement age
                      </td>
                      {comparison.scenarios.map((scenario) => (
                        <td
                          key={scenario.id}
                          style={{
                            textAlign: 'right',
                            padding: '12px',
                            fontFamily: 'monospace',
                            fontWeight: 600
                          }}
                        >
                          {scenario.results?.retirement_age || '-'}
                        </td>
                      ))}
                      <td style={{
                        textAlign: 'right',
                        padding: '12px',
                        fontFamily: 'monospace',
                        fontWeight: 600,
                        color: getDifferenceColor(
                          comparison.metrics.retirement_age_difference,
                          false
                        )
                      }}>
                        {comparison.metrics.retirement_age_difference
                          ? `${Math.abs(comparison.metrics.retirement_age_difference)} years`
                          : '-'
                        }
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Trade-offs */}
          {comparison.trade_offs && comparison.trade_offs.length > 0 && (
            <Alert variant="info" style={{ marginBottom: '24px', lineHeight: '1.7' }}>
              <strong>💡 Key trade-offs to consider:</strong>
              <div style={{ marginTop: '12px' }}>
                {comparison.trade_offs.map((tradeoff, idx) => (
                  <div
                    key={idx}
                    style={{
                      marginBottom: idx < comparison.trade_offs.length - 1 ? '16px' : '0',
                      paddingBottom: idx < comparison.trade_offs.length - 1 ? '16px' : '0',
                      borderBottom: idx < comparison.trade_offs.length - 1 ? '1px solid rgba(37, 99, 235, 0.1)' : 'none'
                    }}
                  >
                    <div style={{ fontWeight: 600, marginBottom: '4px' }}>
                      {tradeoff.title}
                    </div>
                    <p style={{ color: '#475569', fontSize: '0.95rem', marginBottom: '0' }}>
                      {tradeoff.description}
                    </p>
                  </div>
                ))}
              </div>
            </Alert>
          )}

          {/* Best scenario */}
          {comparison.best_scenario && (
            <Card style={{ padding: '24px', backgroundColor: '#F0FDF4', border: '1px solid #BBF7D0' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span style={{ fontSize: '1.5rem' }}>✓</span>
                <strong style={{ fontSize: '1.1rem', color: '#059669' }}>
                  Best overall scenario
                </strong>
              </div>
              <p style={{ color: '#475569', marginBottom: '0', lineHeight: '1.7' }}>
                Based on this analysis, <strong>{comparison.best_scenario.name}</strong> appears
                to be the strongest option for your long-term financial goals.
              </p>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
