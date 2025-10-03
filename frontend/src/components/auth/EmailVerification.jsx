import React, { useState, useEffect } from 'react';
import { Alert, Button } from 'internal-packages-ui';
import { authEndpoints } from '../../utils/api';

export function EmailVerification({ token, onSuccess }) {
  const [status, setStatus] = useState('verifying'); // verifying, success, error
  const [message, setMessage] = useState('');
  const [redirectCountdown, setRedirectCountdown] = useState(3);

  const cardStyle = {
    maxWidth: '640px',
    margin: '0 auto',
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    lineHeight: '1.7',
  };

  const headingStyle = {
    fontSize: '1.8rem',
    fontWeight: 'bold',
    color: '#0F172A',
    marginBottom: '16px',
  };

  const descriptionStyle = {
    color: '#475569',
    marginBottom: '24px',
    lineHeight: '1.7',
  };

  const buttonStyle = {
    width: '100%',
    padding: '12px 24px',
    backgroundColor: '#2563EB',
    color: '#FFFFFF',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 150ms ease-in-out',
    marginTop: '16px',
  };

  const spinnerStyle = {
    border: '3px solid #E2E8F0',
    borderTop: '3px solid #2563EB',
    borderRadius: '50%',
    width: '48px',
    height: '48px',
    animation: 'spin 1s linear infinite',
    margin: '0 auto 16px',
  };

  useEffect(() => {
    const verifyEmail = async () => {
      if (!token) {
        setStatus('error');
        setMessage('Invalid verification link. No token provided.');
        return;
      }

      try {
        const response = await authEndpoints.verifyEmail(token);
        setStatus('success');
        setMessage(response.message || 'Your email has been successfully verified!');

        // Start redirect countdown
        const countdownInterval = setInterval(() => {
          setRedirectCountdown((prev) => {
            if (prev <= 1) {
              clearInterval(countdownInterval);
              if (onSuccess) {
                onSuccess();
              } else {
                window.location.href = '/login';
              }
              return 0;
            }
            return prev - 1;
          });
        }, 1000);

        return () => clearInterval(countdownInterval);
      } catch (error) {
        setStatus('error');
        setMessage(error.message || 'Email verification failed. The link may be invalid or expired.');
      }
    };

    verifyEmail();
  }, [token, onSuccess]);

  const handleResendVerification = async () => {
    // This would require the email to be passed or stored
    // For now, just show a message
    alert('Please check your email for the original verification link or contact support.');
  };

  return (
    <div style={cardStyle}>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>

      {status === 'verifying' && (
        <>
          <h1 style={headingStyle}>Verifying your email</h1>
          <div style={{ textAlign: 'center', padding: '32px 0' }}>
            <div style={spinnerStyle}></div>
            <p style={descriptionStyle}>
              Please wait while we verify your email address...
            </p>
          </div>
        </>
      )}

      {status === 'success' && (
        <>
          <h1 style={headingStyle}>Email verified successfully!</h1>
          <Alert variant="success" style={{ marginBottom: '24px' }}>
            <p style={{ fontWeight: 600, marginBottom: '8px' }}>Your email is now verified</p>
            <p style={{ color: '#475569', lineHeight: '1.7' }}>
              {message || 'Your account is ready to use. You can now sign in and start managing your finances across the UK and South Africa.'}
            </p>
          </Alert>
          <p style={{ ...descriptionStyle, textAlign: 'center' }}>
            Redirecting you to sign in in {redirectCountdown} seconds...
          </p>
          <Button
            onClick={() => window.location.href = '/login'}
            style={buttonStyle}
            onMouseOver={(e) => (e.target.style.backgroundColor = '#1E40AF')}
            onMouseOut={(e) => (e.target.style.backgroundColor = '#2563EB')}
          >
            Sign in now
          </Button>
        </>
      )}

      {status === 'error' && (
        <>
          <h1 style={headingStyle}>Verification failed</h1>
          <Alert variant="error" style={{ marginBottom: '24px' }}>
            <p style={{ fontWeight: 600, marginBottom: '8px' }}>We couldn't verify your email</p>
            <p style={{ color: '#475569', lineHeight: '1.7' }}>
              {message || 'The verification link may have expired or is invalid. This can happen if the link is more than 24 hours old or has already been used.'}
            </p>
          </Alert>
          <p style={descriptionStyle}>
            Don't worry - this is easy to fix. You can request a new verification link or try signing in
            if you've already verified your email.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <Button
              onClick={handleResendVerification}
              style={{ ...buttonStyle, backgroundColor: '#FFFFFF', color: '#2563EB', border: '2px solid #2563EB' }}
              onMouseOver={(e) => (e.target.style.backgroundColor = '#F8FAFC')}
              onMouseOut={(e) => (e.target.style.backgroundColor = '#FFFFFF')}
            >
              Request a new verification link
            </Button>
            <Button
              onClick={() => window.location.href = '/login'}
              style={{ ...buttonStyle, backgroundColor: '#F8FAFC', color: '#475569', border: '1px solid #E2E8F0' }}
              onMouseOver={(e) => (e.target.style.backgroundColor = '#F1F5F9')}
              onMouseOut={(e) => (e.target.style.backgroundColor = '#F8FAFC')}
            >
              Back to sign in
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
