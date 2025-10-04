import React, { useState } from 'react';
import { Button, Alert } from 'internal-packages/ui';
import { AdviceCard } from './AdviceCard';
import { authStorage } from '../../utils/auth';

/**
 * RetirementAdvice - AI-powered retirement planning advice
 *
 * Features:
 * - One-click to get personalized retirement advice
 * - Analyzes pension data and retirement readiness
 * - Provides actionable recommendations
 * - Shows projected impact on retirement pot
 * - Rate limit handling
 */
export function RetirementAdvice() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [response, setResponse] = useState(null);

  const handleGetAdvice = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await fetch('/api/v1/ai/retirement-advice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({}),
      });

      if (!res.ok) {
        if (res.status === 401) {
          authStorage.clear();
          window.location.href = '/login';
          return;
        }

        if (res.status === 429) {
          const data = await res.json();
          throw new Error(
            data.detail || "You've used your advice requests for now. Try again in a few minutes."
          );
        }

        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to get retirement advice. Please try again.');
      }

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      setError(err.message || 'Failed to get retirement advice. Please try again.');
      console.error('Error getting retirement advice:', err);
    } finally {
      setLoading(false);
    }
  };

  // Styles
  const containerStyle = {
    maxWidth: '900px',
    margin: '0 auto',
  };

  const narrativeSectionStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
    lineHeight: '1.7',
  };

  const headingStyle = {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '16px',
  };

  const paragraphStyle = {
    color: '#475569',
    marginBottom: '16px',
    lineHeight: '1.7',
  };

  return (
    <div style={containerStyle}>
      {/* Introduction */}
      <div style={narrativeSectionStyle}>
        <h3 style={headingStyle}>Your Personalized Retirement Strategy</h3>
        <p style={paragraphStyle}>
          Based on your pension data, I'll analyze your retirement readiness and provide
          personalized advice to help you achieve a comfortable retirement. This includes UK
          pensions, South African retirement funds, and optimal contribution strategies.
        </p>

        <Button
          variant="primary"
          onClick={handleGetAdvice}
          disabled={loading}
          style={{ width: '100%' }}
        >
          {loading ? 'Analyzing Your Retirement Plan...' : 'Get Retirement Advice'}
        </Button>
      </div>

      {/* Error State */}
      {error && (
        <Alert variant="error" style={{ marginBottom: '24px' }}>
          <p style={{ fontWeight: 600 }}>Unable to Get Retirement Advice</p>
          <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
        </Alert>
      )}

      {/* Loading/Response */}
      {loading && (
        <AdviceCard loading={true} />
      )}

      {response && !loading && (
        <AdviceCard
          advice={response.advice}
          recommendations={response.recommendations}
          confidence={response.confidence}
          sources={response.sources}
        />
      )}
    </div>
  );
}
