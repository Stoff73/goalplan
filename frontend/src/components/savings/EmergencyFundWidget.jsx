import React from 'react';

export function EmergencyFundWidget({ emergencyFund, formatCurrency }) {
  if (!emergencyFund) return null;

  const { status, monthsCovered, targetMonths, currentAmount, targetAmount } = emergencyFund;

  const getStatusColor = () => {
    if (status === 'ADEQUATE') return '#10B981'; // green
    if (status === 'INSUFFICIENT') return '#F59E0B'; // amber
    return '#EF4444'; // red (NONE)
  };

  const getStatusText = () => {
    if (status === 'ADEQUATE') {
      return `You have ${(monthsCovered || 0).toFixed(1)} months of expenses saved - excellent!`;
    }
    if (status === 'INSUFFICIENT') {
      return `You have ${(monthsCovered || 0).toFixed(1)} months of expenses saved. Most experts recommend 6 months.`;
    }
    return 'You haven\'t designated any accounts as emergency fund yet.';
  };

  const getActionText = () => {
    if (status === 'ADEQUATE') {
      return 'Your emergency fund is well-funded. Keep it topped up as your expenses change.';
    }
    if (status === 'INSUFFICIENT') {
      const shortfall = targetAmount - currentAmount;
      return `Build up another ${formatCurrency(shortfall)} to reach your 6-month target.`;
    }
    return 'Start building your emergency fund today. Mark one of your accounts as "Emergency Fund" and aim for 6 months of expenses.';
  };

  const percentage = Math.min((currentAmount / targetAmount) * 100, 100);

  const narrativeSectionStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '48px',
    lineHeight: '1.7',
  };

  const sectionHeadingStyle = {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '16px',
  };

  const paragraphStyle = {
    color: '#475569',
    marginBottom: '16px',
    lineHeight: '1.7',
  };

  return (
    <div style={narrativeSectionStyle}>
      <h3 style={sectionHeadingStyle}>Your Emergency Fund Status</h3>
      <p style={paragraphStyle}>
        <strong style={{ color: getStatusColor() }}>{getStatusText()}</strong>
      </p>
      <p style={paragraphStyle}>
        {getActionText()}
      </p>

      {/* Progress Bar */}
      {status !== 'NONE' && (
        <div style={{ marginTop: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.875rem', color: '#475569', fontWeight: 500 }}>
              Current: {formatCurrency(currentAmount)}
            </span>
            <span style={{ fontSize: '0.875rem', color: '#475569', fontWeight: 500 }}>
              Target: {formatCurrency(targetAmount)} ({targetMonths} months)
            </span>
          </div>
          <div style={{ width: '100%', height: '24px', backgroundColor: '#E2E8F0', borderRadius: '12px', overflow: 'hidden' }}>
            <div
              style={{
                width: `${percentage}%`,
                height: '100%',
                backgroundColor: getStatusColor(),
                borderRadius: '12px',
                transition: 'width 300ms ease-in-out',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'flex-end',
                paddingRight: '12px',
                color: '#FFFFFF',
                fontSize: '0.75rem',
                fontWeight: 600,
              }}
            >
              {percentage > 15 && `${percentage.toFixed(0)}%`}
            </div>
          </div>
        </div>
      )}

      {/* Expandable Educational Content */}
      <details style={{ marginTop: '16px', cursor: 'pointer' }}>
        <summary style={{ fontSize: '0.875rem', color: '#2563EB', fontWeight: 500 }}>
          Tell me more about emergency funds →
        </summary>
        <div style={{ marginTop: '12px', padding: '16px', backgroundColor: '#F8FAFC', borderRadius: '8px', fontSize: '0.95rem', color: '#475569', lineHeight: '1.7' }}>
          <p style={{ marginBottom: '12px' }}>
            An emergency fund is money set aside for unexpected expenses like job loss, medical emergencies,
            or urgent home repairs. It should be kept in an easily accessible savings account—not invested
            in stocks or locked away in fixed-term deposits.
          </p>
          <p style={{ marginBottom: '12px' }}>
            <strong>How much should you save?</strong> Most financial advisors recommend 3-6 months of
            essential expenses. If you're self-employed or have variable income, aim for 6-12 months.
          </p>
          <p>
            <strong>Where to keep it:</strong> Use a high-interest savings account or Cash ISA for tax
            efficiency in the UK, or a TFSA in South Africa. The key is instant access—you need to be
            able to withdraw the money quickly in an emergency.
          </p>
        </div>
      </details>
    </div>
  );
}
