import React from 'react';

export function Progress({ value = 0, max = 100, className = '' }) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  const getColor = () => {
    if (percentage >= 80) return '#10B981'; // Green
    if (percentage >= 50) return '#2563EB'; // Blue
    if (percentage >= 30) return '#F59E0B'; // Amber
    return '#EF4444'; // Red
  };

  return (
    <div
      className={`progress-container ${className}`}
      style={{
        width: '100%',
        height: '12px',
        backgroundColor: '#F1F5F9',
        borderRadius: '6px',
        overflow: 'hidden',
        position: 'relative'
      }}
    >
      <div
        className="progress-bar"
        style={{
          width: `${percentage}%`,
          height: '100%',
          backgroundColor: getColor(),
          transition: 'width 250ms ease-in-out',
          borderRadius: '6px'
        }}
      />
    </div>
  );
}
