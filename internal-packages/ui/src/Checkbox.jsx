import React from 'react';

export function Checkbox({
  id,
  name,
  checked,
  onChange,
  label,
  disabled = false,
  className = '',
  ...props
}) {
  return (
    <div className={`flex items-center ${className}`}>
      <input
        type="checkbox"
        id={id}
        name={name}
        checked={checked}
        onChange={onChange}
        disabled={disabled}
        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed"
        {...props}
      />
      {label && (
        <label
          htmlFor={id}
          className="ml-2 block text-sm text-gray-900"
        >
          {label}
        </label>
      )}
    </div>
  );
}
