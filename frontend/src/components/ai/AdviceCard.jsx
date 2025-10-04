import React, { useState } from 'react';

/**
 * AdviceCard - Reusable card for displaying AI advice
 *
 * Features:
 * - Displays AI advice in narrative format
 * - Shows recommendations as bulleted action items
 * - Confidence badge (High/Medium/Low)
 * - Collapsible sources section
 * - Always visible disclaimer
 *
 * Props:
 * - advice: string - Main AI advice text
 * - recommendations: array - List of actionable recommendations
 * - confidence: string - Confidence level (high/medium/low)
 * - sources: array - Sources cited (optional)
 * - loading: boolean - Loading state
 */
export function AdviceCard({ advice, recommendations = [], confidence, sources = [], loading = false }) {
  const [sourcesExpanded, setSourcesExpanded] = useState(false);

  const getConfidenceBadgeStyle = (level) => {
    const styles = {
      high: {
        backgroundColor: '#D1FAE5',
        borderColor: '#10B981',
        color: '#065F46',
      },
      medium: {
        backgroundColor: '#FEF3C7',
        borderColor: '#F59E0B',
        color: '#92400E',
      },
      low: {
        backgroundColor: '#FEE2E2',
        borderColor: '#EF4444',
        color: '#991B1B',
      },
    };
    return styles[level?.toLowerCase()] || styles.medium;
  };

  // Styles
  const cardStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
    lineHeight: '1.7',
    position: 'relative',
  };

  const confidenceBadgeStyle = {
    position: 'absolute',
    top: '16px',
    right: '16px',
    padding: '4px 12px',
    borderRadius: '9999px',
    fontSize: '0.75rem',
    fontWeight: 600,
    border: `1px solid ${getConfidenceBadgeStyle(confidence).borderColor}`,
    ...getConfidenceBadgeStyle(confidence),
  };

  const adviceTextStyle = {
    color: '#475569',
    marginBottom: '24px',
    lineHeight: '1.7',
    fontSize: '1rem',
    marginTop: confidence ? '32px' : '0', // Account for badge
  };

  const sectionHeadingStyle = {
    fontSize: '1rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '12px',
    marginTop: '24px',
  };

  const recommendationsListStyle = {
    listStyleType: 'disc',
    paddingLeft: '24px',
    color: '#475569',
    lineHeight: '1.7',
  };

  const recommendationItemStyle = {
    marginBottom: '8px',
  };

  const sourcesContainerStyle = {
    marginTop: '24px',
    padding: '16px',
    backgroundColor: '#F8FAFC',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
  };

  const expandButtonStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: 500,
    color: '#2563EB',
    padding: '0',
    background: 'none',
    border: '0',
    width: '100%',
  };

  const disclaimerStyle = {
    marginTop: '24px',
    padding: '16px',
    backgroundColor: '#FEF3C7',
    border: '1px solid #F59E0B',
    borderLeft: '4px solid #F59E0B',
    borderRadius: '8px',
  };

  const disclaimerTextStyle = {
    fontSize: '0.875rem',
    color: '#92400E',
    lineHeight: '1.6',
    margin: 0,
  };

  const skeletonStyle = {
    height: '16px',
    backgroundColor: '#E2E8F0',
    borderRadius: '4px',
    marginBottom: '12px',
    animation: 'pulse 1.5s ease-in-out infinite',
  };

  // Loading state
  if (loading) {
    return (
      <div style={cardStyle}>
        <div style={{ ...skeletonStyle, width: '80%' }}></div>
        <div style={{ ...skeletonStyle, width: '90%' }}></div>
        <div style={{ ...skeletonStyle, width: '70%' }}></div>
        <div style={{ ...skeletonStyle, width: '85%', marginTop: '24px' }}></div>
        <div style={{ ...skeletonStyle, width: '60%' }}></div>

        <style>{`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div style={cardStyle}>
      {/* Confidence Badge */}
      {confidence && (
        <div style={confidenceBadgeStyle}>
          {confidence.toUpperCase()} CONFIDENCE
        </div>
      )}

      {/* Main Advice */}
      <p style={adviceTextStyle}>{advice}</p>

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div>
          <h4 style={sectionHeadingStyle}>What You Should Do Next</h4>
          <ul style={recommendationsListStyle}>
            {recommendations.map((rec, idx) => (
              <li key={idx} style={recommendationItemStyle}>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Sources (Collapsible) */}
      {sources && sources.length > 0 && (
        <div style={sourcesContainerStyle}>
          <button
            onClick={() => setSourcesExpanded(!sourcesExpanded)}
            style={expandButtonStyle}
            aria-expanded={sourcesExpanded}
          >
            <span>Sources & References</span>
            <span style={{ fontSize: '0.75rem' }}>
              {sourcesExpanded ? '▼' : '▶'}
            </span>
          </button>

          {sourcesExpanded && (
            <ul style={{ ...recommendationsListStyle, marginTop: '12px', fontSize: '0.875rem' }}>
              {sources.map((source, idx) => (
                <li key={idx} style={recommendationItemStyle}>
                  {source}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Disclaimer (Always Visible) */}
      <div style={disclaimerStyle}>
        <p style={disclaimerTextStyle}>
          <strong>Important:</strong> This is AI-generated advice for informational purposes only.
          It does not constitute regulated financial advice. Please consult with a qualified
          financial advisor before making any financial decisions.
        </p>
      </div>
    </div>
  );
}
