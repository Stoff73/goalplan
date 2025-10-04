import React, { useState } from 'react';
import { Button, Alert } from 'internal-packages/ui';
import { AdviceCard } from './AdviceCard';
import { authStorage } from '../../utils/auth';

/**
 * AskAI - Free-form question component for AI financial advice
 *
 * Features:
 * - Text input for user questions (10-500 chars)
 * - Example questions as clickable suggestions
 * - Loading state while AI generates advice
 * - Error handling with friendly messages
 * - Rate limit handling
 * - Displays AI response in AdviceCard format
 *
 * Design follows STYLEGUIDE.md narrative approach
 */
export function AskAI() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [response, setResponse] = useState(null);
  const [charCount, setCharCount] = useState(0);

  const MIN_CHARS = 10;
  const MAX_CHARS = 500;

  const exampleQuestions = [
    'How much should I contribute to my pension this year?',
    'Should I pay off my mortgage or invest in my ISA?',
    "What's the best way to save for retirement in the UK and SA?",
    'How can I reduce my inheritance tax liability?',
    'Should I transfer my UK pension to a QROPS?',
    'What tax-efficient investments should I consider?',
  ];

  const handleQuestionChange = (e) => {
    const value = e.target.value;
    if (value.length <= MAX_CHARS) {
      setQuestion(value);
      setCharCount(value.length);
    }
  };

  const handleExampleClick = (exampleQuestion) => {
    setQuestion(exampleQuestion);
    setCharCount(exampleQuestion.length);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (question.length < MIN_CHARS) {
      setError(`Please enter at least ${MIN_CHARS} characters.`);
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await fetch('/api/v1/ai/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStorage.getAccessToken()}`,
        },
        body: JSON.stringify({ question }),
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
        throw new Error(errorData.detail || 'Failed to get AI advice. Please try again.');
      }

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      setError(err.message || 'Failed to get AI advice. Please try again.');
      console.error('Error getting AI advice:', err);
    } finally {
      setLoading(false);
    }
  };

  // Styles following STYLEGUIDE.md
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

  const textareaStyle = {
    width: '100%',
    minHeight: '120px',
    padding: '12px 16px',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
    fontSize: '1rem',
    fontFamily: 'inherit',
    lineHeight: '1.7',
    resize: 'vertical',
    marginBottom: '8px',
    outline: 'none',
  };

  const charCountStyle = {
    fontSize: '0.75rem',
    color: charCount > MAX_CHARS ? '#EF4444' : '#94A3B8',
    textAlign: 'right',
    marginBottom: '16px',
  };

  const exampleQuestionsStyle = {
    marginTop: '24px',
  };

  const exampleQuestionButtonStyle = {
    display: 'block',
    width: '100%',
    padding: '12px 16px',
    marginBottom: '8px',
    backgroundColor: '#F8FAFC',
    border: '1px solid #E2E8F0',
    borderRadius: '8px',
    color: '#2563EB',
    fontSize: '0.95rem',
    textAlign: 'left',
    cursor: 'pointer',
    transition: 'all 150ms ease-in-out',
    lineHeight: '1.5',
  };

  const loadingMessageStyle = {
    padding: '32px',
    textAlign: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
  };

  const loadingTextStyle = {
    color: '#475569',
    fontSize: '1.1rem',
    fontWeight: 500,
    marginTop: '16px',
  };

  return (
    <div style={containerStyle}>
      {/* Introduction */}
      <div style={narrativeSectionStyle}>
        <h3 style={headingStyle}>Ask Your AI Financial Advisor</h3>
        <p style={paragraphStyle}>
          Have a financial question? I'm here to help with personalized advice based on your
          situation. Whether it's about pensions, investments, tax planning, or any other
          financial topic—just ask!
        </p>

        {/* Question Input */}
        <form onSubmit={handleSubmit}>
          <textarea
            value={question}
            onChange={handleQuestionChange}
            placeholder="Type your financial question here... (min 10 characters)"
            style={textareaStyle}
            disabled={loading}
            aria-label="Your financial question"
          />

          <div style={charCountStyle}>
            {charCount} / {MAX_CHARS} characters
            {charCount < MIN_CHARS && charCount > 0 && (
              <span style={{ marginLeft: '8px', color: '#F59E0B' }}>
                (minimum {MIN_CHARS} characters)
              </span>
            )}
          </div>

          <Button
            type="submit"
            variant="primary"
            disabled={loading || question.length < MIN_CHARS}
            style={{ width: '100%' }}
          >
            {loading ? 'Getting AI Advice...' : 'Get AI Advice'}
          </Button>
        </form>

        {/* Example Questions */}
        <div style={exampleQuestionsStyle}>
          <p style={{ fontSize: '0.875rem', color: '#475569', marginBottom: '12px' }}>
            Or try one of these example questions:
          </p>
          {exampleQuestions.map((example, idx) => (
            <button
              key={idx}
              onClick={() => handleExampleClick(example)}
              style={exampleQuestionButtonStyle}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#EFF6FF';
                e.currentTarget.style.borderColor = '#BFDBFE';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#F8FAFC';
                e.currentTarget.style.borderColor = '#E2E8F0';
              }}
              disabled={loading}
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* Error State */}
      {error && (
        <Alert variant="error" style={{ marginBottom: '24px' }}>
          <p style={{ fontWeight: 600 }}>Unable to Get Advice</p>
          <p style={{ marginTop: '4px', fontSize: '0.95rem' }}>{error}</p>
        </Alert>
      )}

      {/* Loading State */}
      {loading && (
        <div style={loadingMessageStyle}>
          <div
            style={{
              width: '48px',
              height: '48px',
              border: '4px solid #E2E8F0',
              borderTop: '4px solid #2563EB',
              borderRadius: '50%',
              margin: '0 auto',
              animation: 'spin 1s linear infinite',
            }}
          ></div>
          <p style={loadingTextStyle}>Analyzing your financial situation...</p>
          <p style={{ color: '#94A3B8', fontSize: '0.875rem', marginTop: '8px' }}>
            This may take a few moments
          </p>

          <style>{`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}</style>
        </div>
      )}

      {/* AI Response */}
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
