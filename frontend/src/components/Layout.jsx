import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogoutButton } from './auth/LogoutButton';
import { authStorage } from '../utils/auth';

export function Layout({ children, showHeader = true, containerWidth = 'xl' }) {
  const user = authStorage.getUser();
  const navigate = useNavigate();

  const containerStyles = {
    sm: { maxWidth: '640px' },
    md: { maxWidth: '768px' },
    lg: { maxWidth: '1024px' },
    xl: { maxWidth: '1280px' },
  };

  const headerStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    height: '80px',
    backgroundColor: '#FFFFFF',
    borderBottom: '1px solid #E2E8F0',
    boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
    zIndex: 1000,
  };

  const headerContentStyle = {
    maxWidth: '1280px',
    margin: '0 auto',
    padding: '0 32px',
    height: '100%',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  };

  const logoStyle = {
    fontSize: '1.5rem',
    fontWeight: 700,
    color: '#0F172A',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  };

  const navStyle = {
    display: 'flex',
    gap: '32px',
    alignItems: 'center',
  };

  const navLinkStyle = {
    color: '#475569',
    textDecoration: 'none',
    fontSize: '1rem',
    fontWeight: 500,
    transition: 'color 150ms ease-in-out',
  };

  const mainStyle = {
    marginTop: showHeader ? '80px' : 0,
    minHeight: showHeader ? 'calc(100vh - 80px)' : '100vh',
    backgroundColor: '#FFFFFF',
  };

  const containerStyle = {
    ...containerStyles[containerWidth],
    margin: '0 auto',
    padding: '32px',
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#FFFFFF' }}>
      {showHeader && user && (
        <header style={headerStyle}>
          <div style={headerContentStyle}>
            <div
              style={logoStyle}
              onClick={() => navigate('/dashboard')}
              role="button"
              tabIndex={0}
              onKeyPress={(e) => {
                if (e.key === 'Enter') navigate('/dashboard');
              }}
            >
              <span style={{ color: '#2563EB' }}>Goal</span>
              <span>Plan</span>
            </div>
            <nav style={navStyle}>
              <a
                href="/dashboard"
                style={navLinkStyle}
                onMouseOver={(e) => (e.target.style.color = '#2563EB')}
                onMouseOut={(e) => (e.target.style.color = '#475569')}
              >
                Dashboard
              </a>
              <a
                href="/tax-status"
                style={navLinkStyle}
                onMouseOver={(e) => (e.target.style.color = '#2563EB')}
                onMouseOut={(e) => (e.target.style.color = '#475569')}
              >
                Tax Status
              </a>
              <a
                href="/income"
                style={navLinkStyle}
                onMouseOver={(e) => (e.target.style.color = '#2563EB')}
                onMouseOut={(e) => (e.target.style.color = '#475569')}
              >
                Income
              </a>
              <a
                href="/savings"
                style={navLinkStyle}
                onMouseOver={(e) => (e.target.style.color = '#2563EB')}
                onMouseOut={(e) => (e.target.style.color = '#475569')}
              >
                Savings
              </a>
              <a
                href="/profile"
                style={navLinkStyle}
                onMouseOver={(e) => (e.target.style.color = '#2563EB')}
                onMouseOut={(e) => (e.target.style.color = '#475569')}
              >
                Profile
              </a>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <span style={{ color: '#475569', fontSize: '0.875rem' }}>
                  {user.firstName} {user.lastName}
                </span>
                <LogoutButton variant="secondary" />
              </div>
            </nav>
          </div>
        </header>
      )}

      <main style={mainStyle}>
        <div style={containerStyle}>{children}</div>
      </main>
    </div>
  );
}
