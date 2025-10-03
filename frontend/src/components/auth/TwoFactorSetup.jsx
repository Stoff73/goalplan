import React, { useState, useEffect } from 'react';
import { Button, Input, Alert } from 'internal-packages-ui';
import { authEndpoints } from '../../utils/api';

export function TwoFactorSetup({ onSuccess, onSkip, allowSkip = false }) {
  const [step, setStep] = useState('loading'); // loading, setup, verify, complete
  const [qrCode, setQrCode] = useState('');
  const [secret, setSecret] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [backupCodes, setBackupCodes] = useState([]);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [codesDownloaded, setCodesDownloaded] = useState(false);

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
    fontWeight: 700,
    lineHeight: 1.2,
    color: '#0F172A',
    marginBottom: '16px',
  };

  const descriptionStyle = {
    color: '#475569',
    marginBottom: '24px',
    lineHeight: '1.7',
  };

  const labelStyle = {
    display: 'block',
    fontSize: '0.875rem',
    fontWeight: 500,
    color: '#0F172A',
    marginBottom: '8px',
  };

  const helpTextStyle = {
    fontSize: '0.875rem',
    color: '#475569',
    marginTop: '8px',
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
  };

  const calloutStyle = {
    backgroundColor: '#EFF6FF',
    border: '1px solid #BFDBFE',
    borderLeft: '4px solid #3B82F6',
    padding: '16px',
    borderRadius: '8px',
    marginTop: '24px',
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
    const initiate2FA = async () => {
      try {
        const response = await authEndpoints.enable2FA();
        setQrCode(response.qrCode || response.qr_code);
        setSecret(response.secret);
        setStep('setup');
      } catch (err) {
        setError(err.message || 'Failed to initialize 2FA setup');
        setStep('setup');
      }
    };

    initiate2FA();
  }, []);

  const handleVerify = async (e) => {
    e.preventDefault();
    setError('');

    if (!verificationCode || verificationCode.length !== 6) {
      setError('Please enter a valid 6-digit code');
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await authEndpoints.verify2FASetup(verificationCode);
      setBackupCodes(response.backupCodes || response.backup_codes || []);
      setStep('complete');
    } catch (err) {
      setError(err.message || 'Invalid verification code. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDownloadBackupCodes = () => {
    const codesText = backupCodes.join('\n');
    const blob = new Blob([codesText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'goalplan-backup-codes.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setCodesDownloaded(true);
  };

  const handleComplete = () => {
    if (!codesDownloaded) {
      setError('Please download your backup codes before continuing');
      return;
    }

    if (onSuccess) {
      onSuccess();
    }
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

      {step === 'loading' && (
        <>
          <h1 style={headingStyle}>Setting up two-factor authentication</h1>
          <div style={{ textAlign: 'center', padding: '32px 0' }}>
            <div style={spinnerStyle}></div>
            <p style={descriptionStyle}>
              Generating your unique authentication code...
            </p>
          </div>
        </>
      )}

      {step === 'setup' && (
          <>
            <h1 style={headingStyle}>Secure your account with 2FA</h1>
            <p style={descriptionStyle}>
              Two-factor authentication adds an extra layer of security to your account. Even if someone
              gets your password, they won't be able to access your financial information without your
              authentication app.
            </p>

            {error && (
              <Alert variant="error" style={{ marginBottom: '24px' }}>
                {error}
              </Alert>
            )}

            <div style={calloutStyle}>
              <p style={{ fontWeight: 600, color: '#1E40AF', marginBottom: '8px' }}>
                Step 1: Scan the QR code
              </p>
              <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
                Open your authenticator app (Google Authenticator, Authy, or similar) and scan this
                QR code. The app will generate a new 6-digit code every 30 seconds.
              </p>
            </div>

            {/* QR Code Display */}
            {qrCode && (
              <div style={{ display: 'flex', justifyContent: 'center', backgroundColor: '#FFFFFF', padding: '24px', border: '1px solid #E2E8F0', borderRadius: '8px', margin: '24px 0' }}>
                <img src={qrCode} alt="Scan this QR code with your authenticator app" style={{ width: '192px', height: '192px' }} />
              </div>
            )}

            {/* Text Secret Fallback */}
            {secret && (
              <div style={{ backgroundColor: '#F8FAFC', padding: '16px', borderRadius: '8px', border: '1px solid #E2E8F0', marginBottom: '24px' }}>
                <p style={{ fontSize: '0.75rem', color: '#475569', marginBottom: '8px' }}>
                  Can't scan the QR code? Enter this secret key manually:
                </p>
                <code style={{ fontSize: '0.875rem', fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace', wordBreak: 'break-all', color: '#0F172A' }}>{secret}</code>
              </div>
            )}

            <form onSubmit={handleVerify} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div>
                <label htmlFor="verificationCode" style={labelStyle}>
                  Step 2: Enter the code from your app
                </label>
                <Input
                  type="text"
                  id="verificationCode"
                  name="verificationCode"
                  value={verificationCode}
                  onChange={(e) => {
                    setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6));
                    setError('');
                  }}
                  placeholder="Enter 6-digit code"
                  maxLength={6}
                  disabled={isSubmitting}
                  required
                />
                <p style={helpTextStyle}>
                  Enter the current 6-digit code shown in your authenticator app
                </p>
              </div>

              <div style={{ display: 'flex', gap: '12px' }}>
                <Button
                  type="submit"
                  style={{ ...buttonStyle, flex: 1 }}
                  disabled={isSubmitting || verificationCode.length !== 6}
                  onMouseOver={(e) => !isSubmitting && verificationCode.length === 6 && (e.target.style.backgroundColor = '#1E40AF')}
                  onMouseOut={(e) => !isSubmitting && (e.target.style.backgroundColor = '#2563EB')}
                >
                  {isSubmitting ? 'Verifying...' : 'Verify and continue'}
                </Button>
                {allowSkip && (
                  <Button
                    type="button"
                    onClick={onSkip}
                    disabled={isSubmitting}
                    style={{ ...buttonStyle, backgroundColor: '#F8FAFC', color: '#475569', border: '1px solid #E2E8F0' }}
                    onMouseOver={(e) => !isSubmitting && (e.target.style.backgroundColor = '#F1F5F9')}
                    onMouseOut={(e) => !isSubmitting && (e.target.style.backgroundColor = '#F8FAFC')}
                  >
                    Skip for now
                  </Button>
                )}
              </div>
            </form>
          </>
        )}

        {step === 'complete' && (
          <>
            <h1 style={headingStyle}>Two-factor authentication enabled!</h1>
            <Alert variant="success" style={{ marginBottom: '24px' }}>
              <p style={{ fontWeight: 600, marginBottom: '8px' }}>Your account is now more secure</p>
              <p style={{ color: '#475569', lineHeight: '1.7' }}>
                Two-factor authentication is now active on your account. You'll need both your password
                and your authenticator app to sign in.
              </p>
            </Alert>

            <div style={calloutStyle}>
              <p style={{ fontWeight: 600, color: '#1E40AF', marginBottom: '8px' }}>
                Important: Save your backup codes
              </p>
              <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7', marginBottom: '16px' }}>
                These backup codes let you access your account if you lose your phone or can't use
                your authenticator app. Save them somewhere safe - treat them like your password.
              </p>

              <div style={{ backgroundColor: '#FFFFFF', padding: '16px', borderRadius: '8px', border: '1px solid #E2E8F0', marginBottom: '16px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
                  {backupCodes.map((code, index) => (
                    <code key={index} style={{ fontSize: '0.875rem', fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace', color: '#0F172A' }}>
                      {code}
                    </code>
                  ))}
                </div>
              </div>

              <Button
                onClick={handleDownloadBackupCodes}
                style={{ ...buttonStyle, backgroundColor: codesDownloaded ? '#10B981' : '#2563EB' }}
                onMouseOver={(e) => !codesDownloaded && (e.target.style.backgroundColor = '#1E40AF')}
                onMouseOut={(e) => !codesDownloaded && (e.target.style.backgroundColor = '#2563EB')}
              >
                {codesDownloaded ? 'Backup codes downloaded ✓' : 'Download backup codes'}
              </Button>
            </div>

            {error && (
              <Alert variant="error" style={{ marginTop: '24px' }}>
                {error}
              </Alert>
            )}

            <Button
              onClick={handleComplete}
              style={{ ...buttonStyle, marginTop: '24px', opacity: !codesDownloaded ? 0.5 : 1 }}
              disabled={!codesDownloaded}
              onMouseOver={(e) => codesDownloaded && (e.target.style.backgroundColor = '#1E40AF')}
              onMouseOut={(e) => codesDownloaded && (e.target.style.backgroundColor = '#2563EB')}
            >
              I've saved my backup codes
            </Button>

            {!codesDownloaded && (
              <p style={{ fontSize: '0.875rem', textAlign: 'center', color: '#EF4444', marginTop: '12px' }}>
                Please download your backup codes before continuing
              </p>
            )}
          </>
        )}
    </div>
  );
}
