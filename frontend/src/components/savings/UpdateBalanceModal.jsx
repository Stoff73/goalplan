import React, { useState } from 'react';
import { Button, Input, Label } from 'internal-packages/ui';

export function UpdateBalanceModal({ account, onSave, onCancel, formatCurrency }) {
  const [newBalance, setNewBalance] = useState(account.currentBalance?.toString() || '');
  const [balanceDate, setBalanceDate] = useState(new Date().toISOString().split('T')[0]);
  const [notes, setNotes] = useState('');
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  const currentBalance = account.currentBalance || 0;
  const balanceChange = newBalance ? parseFloat(newBalance) - currentBalance : 0;

  const validate = () => {
    const newErrors = {};

    if (!newBalance || parseFloat(newBalance) < 0) {
      newErrors.newBalance = 'Balance must be 0 or greater';
    }

    if (!balanceDate) {
      newErrors.balanceDate = 'Date is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setSaving(true);

    try {
      await onSave({
        balance: parseFloat(newBalance),
        balanceDate,
        notes: notes.trim() || null,
        updateType: 'MANUAL',
      });
    } catch (err) {
      console.error('Error updating balance:', err);
    } finally {
      setSaving(false);
    }
  };

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
  };

  const modalContentStyle = {
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    padding: '32px',
    maxWidth: '500px',
    width: '100%',
    boxShadow: '0 20px 25px rgba(0, 0, 0, 0.1)',
  };

  const modalTitleStyle = {
    fontSize: '1.5rem',
    fontWeight: 700,
    color: '#0F172A',
    marginBottom: '8px',
  };

  const accountNameStyle = {
    fontSize: '0.875rem',
    color: '#475569',
    marginBottom: '24px',
  };

  const formGroupStyle = {
    marginBottom: '20px',
  };

  const errorStyle = {
    color: '#EF4444',
    fontSize: '0.875rem',
    marginTop: '4px',
  };

  const currentBalanceBoxStyle = {
    padding: '16px',
    backgroundColor: '#F8FAFC',
    borderRadius: '8px',
    marginBottom: '20px',
    border: '1px solid #E2E8F0',
  };

  const changeIndicatorStyle = {
    padding: '16px',
    backgroundColor: balanceChange > 0 ? '#F0FDF4' : balanceChange < 0 ? '#FEF2F2' : '#F8FAFC',
    border: `1px solid ${balanceChange > 0 ? '#86EFAC' : balanceChange < 0 ? '#FCA5A5' : '#E2E8F0'}`,
    borderRadius: '8px',
    marginBottom: '20px',
  };

  const buttonGroupStyle = {
    display: 'flex',
    gap: '12px',
    marginTop: '32px',
  };

  return (
    <div style={modalOverlayStyle} onClick={onCancel}>
      <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
        <h2 style={modalTitleStyle}>Update Balance</h2>
        <p style={accountNameStyle}>
          {account.accountName} • {account.bankName}
        </p>

        <form onSubmit={handleSubmit}>
          {/* Current Balance Display */}
          <div style={currentBalanceBoxStyle}>
            <p style={{ fontSize: '0.75rem', color: '#475569', marginBottom: '4px' }}>Current Balance</p>
            <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#0F172A', fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace' }}>
              {formatCurrency(currentBalance, account.currency)}
            </p>
          </div>

          {/* New Balance */}
          <div style={formGroupStyle}>
            <Label htmlFor="newBalance">New Balance *</Label>
            <Input
              id="newBalance"
              type="number"
              step="0.01"
              min="0"
              value={newBalance}
              onChange={(e) => {
                setNewBalance(e.target.value);
                if (errors.newBalance) {
                  setErrors(prev => ({ ...prev, newBalance: null }));
                }
              }}
              placeholder="0.00"
              autoFocus
            />
            {errors.newBalance && <p style={errorStyle}>{errors.newBalance}</p>}
          </div>

          {/* Change Indicator */}
          {newBalance && !errors.newBalance && (
            <div style={changeIndicatorStyle}>
              <p style={{ fontSize: '0.75rem', color: '#475569', marginBottom: '4px' }}>Change</p>
              <p style={{ fontSize: '1.2rem', fontWeight: 'bold', color: balanceChange > 0 ? '#10B981' : balanceChange < 0 ? '#EF4444' : '#475569', fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace' }}>
                {balanceChange > 0 ? '+' : ''}{formatCurrency(balanceChange, account.currency)}
              </p>
            </div>
          )}

          {/* Balance Date */}
          <div style={formGroupStyle}>
            <Label htmlFor="balanceDate">Balance Date *</Label>
            <Input
              id="balanceDate"
              type="date"
              value={balanceDate}
              onChange={(e) => {
                setBalanceDate(e.target.value);
                if (errors.balanceDate) {
                  setErrors(prev => ({ ...prev, balanceDate: null }));
                }
              }}
            />
            {errors.balanceDate && <p style={errorStyle}>{errors.balanceDate}</p>}
          </div>

          {/* Notes */}
          <div style={formGroupStyle}>
            <Label htmlFor="notes">Notes (optional)</Label>
            <textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g., Salary deposit, Interest payment"
              rows={3}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                fontSize: '0.875rem',
                fontFamily: 'inherit',
                resize: 'vertical',
              }}
            />
          </div>

          {/* Buttons */}
          <div style={buttonGroupStyle}>
            <Button type="button" variant="outline" onClick={onCancel} style={{ flex: 1 }}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={saving} style={{ flex: 1 }}>
              {saving ? 'Updating...' : 'Update Balance'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
