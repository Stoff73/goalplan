import React from 'react';

export function Alert({
  children,
  variant = 'info',
  className = ''
}) {
  const variants = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
  };

  const variantStyles = variants[variant] || variants.info;

  return (
    <div className={`border-l-4 p-4 ${variantStyles} ${className}`} role="alert">
      <div className="flex">
        <div className="flex-1">
          {children}
        </div>
      </div>
    </div>
  );
}
