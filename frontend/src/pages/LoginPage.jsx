import React from 'react';
import { LoginForm } from '../components/auth/LoginForm';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const navigate = useNavigate();

  const handleSuccess = () => {
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
      <LoginForm onSuccess={handleSuccess} />
    </div>
  );
}
