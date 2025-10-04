import React, { useState, useEffect } from 'react';
import { PolicyForm } from './PolicyForm';

export function PolicyFormModal({ isOpen, onClose, policy, onSave }) {
  console.log('📋 PolicyFormModal: Component called, isOpen=', isOpen, 'Date:', new Date().toISOString());
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  // Clear error when modal opens/closes
  useEffect(() => {
    if (!isOpen) {
      setError(null);
      setSaving(false);
    }
  }, [isOpen]);

  const handleSave = async (policyData) => {
    console.log('📋 PolicyFormModal: handleSave called', { policyData });
    setSaving(true);
    setError(null);

    try {
      console.log('📋 PolicyFormModal: Calling onSave (from ProtectionPage)');
      await onSave(policyData);
      console.log('📋 PolicyFormModal: onSave completed successfully');
      // onSave should handle closing the modal on success
    } catch (err) {
      console.error('📋 PolicyFormModal: Error caught:', err);
      setError(err.message || 'Failed to save policy. Please try again.');
      setSaving(false);
    }
  };

  if (!isOpen) {
    console.log('📋 PolicyFormModal: isOpen is false, returning null');
    return null;
  }

  console.log('📋 PolicyFormModal: Rendering modal overlay');

  const modalOverlayStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: '16px',
    overflowY: 'auto',
  };

  const modalContentStyle = {
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 10px 15px rgba(0, 0, 0, 0.1)',
    maxWidth: '900px',
    width: '100%',
    maxHeight: '90vh',
    overflow: 'auto',
    padding: '32px',
    margin: '32px 0',
  };

  const errorAlertStyle = {
    backgroundColor: '#FEE2E2',
    border: '1px solid #FECACA',
    borderLeft: '4px solid #EF4444',
    padding: '16px',
    borderRadius: '8px',
    marginBottom: '24px',
  };

  return (
    <div style={modalOverlayStyle} onClick={onClose}>
      <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
        {error && (
          <div style={errorAlertStyle}>
            <p style={{ fontWeight: 600, color: '#991B1B', marginBottom: '4px' }}>Error</p>
            <p style={{ fontSize: '0.875rem', color: '#7F1D1D' }}>{error}</p>
          </div>
        )}

        <PolicyForm policy={policy} onSave={handleSave} onCancel={onClose} loading={saving} />
      </div>
    </div>
  );
}
