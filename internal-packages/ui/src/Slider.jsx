import React from 'react';

export function Slider({
  min = 0,
  max = 100,
  step = 1,
  value,
  onChange,
  label,
  className = ''
}) {
  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <div className={`slider-container ${className}`} style={{ width: '100%' }}>
      {label && (
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: '8px',
          fontSize: '14px',
          color: '#475569'
        }}>
          <label>{label}</label>
          <span style={{
            fontWeight: 600,
            color: '#0F172A',
            fontFamily: 'ui-monospace, SFMono-Regular, monospace'
          }}>
            {value}
          </span>
        </div>
      )}
      <div style={{ position: 'relative', width: '100%' }}>
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          style={{
            width: '100%',
            height: '8px',
            borderRadius: '4px',
            background: `linear-gradient(to right, #2563EB 0%, #2563EB ${percentage}%, #E2E8F0 ${percentage}%, #E2E8F0 100%)`,
            outline: 'none',
            cursor: 'pointer',
            WebkitAppearance: 'none',
            appearance: 'none'
          }}
          className="slider-input"
        />
      </div>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        marginTop: '4px',
        fontSize: '12px',
        color: '#94A3B8'
      }}>
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}
