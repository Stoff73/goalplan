import React from 'react';

export function Badge({
  children,
  variant = 'default',
  className = ''
}) {
  const getVariantStyles = () => {
    switch (variant) {
      case 'success':
        return {
          backgroundColor: '#ECFDF5',
          color: '#059669',
          border: '1px solid #A7F3D0'
        };
      case 'warning':
        return {
          backgroundColor: '#FFFBEB',
          color: '#D97706',
          border: '1px solid #FDE68A'
        };
      case 'error':
        return {
          backgroundColor: '#FEF2F2',
          color: '#DC2626',
          border: '1px solid #FECACA'
        };
      case 'info':
        return {
          backgroundColor: '#EFF6FF',
          color: '#2563EB',
          border: '1px solid #BFDBFE'
        };
      default:
        return {
          backgroundColor: '#F8FAFC',
          color: '#475569',
          border: '1px solid #E2E8F0'
        };
    }
  };

  return (
    <span
      className={`badge ${className}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '4px 12px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: 500,
        ...getVariantStyles()
      }}
    >
      {children}
    </span>
  );
}
