import React from 'react';
import { RegistrationForm } from '../components/auth/RegistrationForm';
import { useNavigate } from 'react-router-dom';

export default function RegisterPage() {
  const navigate = useNavigate();

  const handleSuccess = () => {
    // Registration form already shows success message
    // Navigate to login after a delay if needed
    setTimeout(() => {
      navigate('/login');
    }, 5000);
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
      <RegistrationForm onSuccess={handleSuccess} />
    </div>
  );
}
