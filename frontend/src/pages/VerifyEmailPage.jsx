import React from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { EmailVerification } from '../components/auth/EmailVerification';

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const handleSuccess = () => {
    navigate('/login');
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
      <EmailVerification token={token} onSuccess={handleSuccess} />
    </div>
  );
}
