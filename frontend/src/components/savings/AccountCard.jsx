import React from 'react';
import { Button } from 'internal-packages/ui';

export function AccountCard({
  account,
  formatCurrency,
  onEdit,
  onDelete,
  onUpdateBalance,
  isExpanded,
  onToggleExpand,
}) {
  const {
    id,
    bankName,
    accountName,
    accountType,
    currentBalance,
    currency,
    interestRate,
    isIsa,
    isTfsa,
    accountPurpose,
    country,
  } = account;

  const getAccountTypeBadge = () => {
    if (isIsa) return { text: 'ISA', color: '#2563EB', bg: '#EFF6FF' };
    if (isTfsa) return { text: 'TFSA', color: '#8B5CF6', bg: '#F5F3FF' };
    if (accountPurpose === 'EMERGENCY_FUND') return { text: 'Emergency', color: '#EF4444', bg: '#FEF2F2' };
    return null;
  };

  const badge = getAccountTypeBadge();

  const cardStyle = {
    padding: '24px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    border: '1px solid #E2E8F0',
    transition: 'all 250ms ease-in-out',
    cursor: 'pointer',
  };

  const cardHoverStyle = {
    ...cardStyle,
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.07)',
    transform: 'translateY(-2px)',
  };

  const [isHovered, setIsHovered] = React.useState(false);

  return (
    <div
      style={isHovered ? cardHoverStyle : cardStyle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onToggleExpand}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <div style={{ flex: 1 }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0F172A', marginBottom: '4px' }}>
            {accountName}
          </h3>
          <p style={{ fontSize: '0.875rem', color: '#475569' }}>
            {bankName} • {country}
          </p>
        </div>
        {badge && (
          <span
            style={{
              padding: '4px 12px',
              borderRadius: '12px',
              backgroundColor: badge.bg,
              color: badge.color,
              fontSize: '0.75rem',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}
          >
            {badge.text}
          </span>
        )}
      </div>

      {/* Balance */}
      <div style={{ marginBottom: '16px' }}>
        <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#0F172A', fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace' }}>
          {formatCurrency(currentBalance, currency)}
        </p>
        <p style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: '4px' }}>
          Current balance
        </p>
      </div>

      {/* Account Details (when expanded) */}
      {isExpanded && (
        <div
          style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #E2E8F0' }}
          onClick={(e) => e.stopPropagation()}
        >
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
            <div>
              <p style={{ fontSize: '0.75rem', color: '#94A3B8', marginBottom: '4px' }}>Account Type</p>
              <p style={{ fontSize: '0.875rem', color: '#0F172A', fontWeight: 500 }}>{accountType}</p>
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', color: '#94A3B8', marginBottom: '4px' }}>Interest Rate</p>
              <p style={{ fontSize: '0.875rem', color: '#0F172A', fontWeight: 500 }}>
                {interestRate ? `${interestRate}%` : 'N/A'}
              </p>
            </div>
            {account.projectedAnnualInterest && (
              <div style={{ gridColumn: '1 / -1' }}>
                <p style={{ fontSize: '0.75rem', color: '#94A3B8', marginBottom: '4px' }}>Projected Annual Interest</p>
                <p style={{ fontSize: '0.875rem', color: '#10B981', fontWeight: 600 }}>
                  {formatCurrency(account.projectedAnnualInterest, currency)}
                </p>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
            <Button
              variant="outline"
              onClick={(e) => {
                e.stopPropagation();
                onUpdateBalance(account);
              }}
              style={{ flex: 1, fontSize: '0.875rem' }}
            >
              Update Balance
            </Button>
            <Button
              variant="outline"
              onClick={(e) => {
                e.stopPropagation();
                onEdit(account);
              }}
              style={{ flex: 1, fontSize: '0.875rem' }}
            >
              Edit
            </Button>
            <Button
              variant="danger"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(id);
              }}
              style={{ fontSize: '0.875rem' }}
            >
              Delete
            </Button>
          </div>
        </div>
      )}

      {/* Expand/Collapse Indicator */}
      {!isExpanded && (
        <div style={{ marginTop: '12px', textAlign: 'center' }}>
          <p style={{ fontSize: '0.75rem', color: '#2563EB', fontWeight: 500 }}>
            Click to view details →
          </p>
        </div>
      )}
    </div>
  );
}
