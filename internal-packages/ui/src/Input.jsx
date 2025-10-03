import React from 'react';

export function Input({
  type = 'text',
  id,
  name,
  value,
  onChange,
  placeholder,
  disabled = false,
  required = false,
  error,
  className = '',
  ...props
}) {
  const baseStyles = 'w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed';
  const errorStyles = error ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : 'border-gray-300';

  return (
    <div className="w-full">
      <input
        type={type}
        id={id}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        className={`${baseStyles} ${errorStyles} ${className}`}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}
