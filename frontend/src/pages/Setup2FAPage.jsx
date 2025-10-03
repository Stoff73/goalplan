import React from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { TwoFactorSetup } from '../components/auth/TwoFactorSetup';

export default function Setup2FAPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const allowSkip = searchParams.get('allowSkip') === 'true';

  const handleSuccess = () => {
    navigate('/dashboard');
  };

  const handleSkip = () => {
    navigate('/dashboard');
  };

  const pageStyle = {
    minHeight: '100vh',
    backgroundColor: '#F8FAFC',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '32px 16px',
  };

  return (
    <div style={pageStyle}>
      <TwoFactorSetup
        onSuccess={handleSuccess}
        onSkip={handleSkip}
        allowSkip={allowSkip}
      />
    </div>
  );
}
