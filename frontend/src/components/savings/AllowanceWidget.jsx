import React from 'react';

export function AllowanceWidget({ allowance, type, formatCurrency }) {
  if (!allowance) return null;

  const isISA = type === 'ISA';
  const isTFSA = type === 'TFSA';

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

  if (isISA) {
    const { limit = 0, used = 0, remaining = 0, percentageUsed = 0, taxYear = '', daysRemaining = 0 } = allowance || {};

    const getWarningColor = () => {
      if (percentageUsed >= 90) return '#EF4444'; // red
      if (percentageUsed >= 70) return '#F59E0B'; // amber
      return '#10B981'; // green
    };

    const getMessage = () => {
      if (percentageUsed >= 100) {
        return `You've fully used your ${formatCurrency(limit, 'GBP')} ISA allowance for ${taxYear}. Great job maximizing your tax-free savings!`;
      }
      if (percentageUsed >= 90) {
        return `You've used ${formatCurrency(used, 'GBP')} of your ${formatCurrency(limit, 'GBP')} ISA allowance for ${taxYear}. Only ${formatCurrency(remaining, 'GBP')} left!`;
      }
      if (percentageUsed >= 50) {
        return `You've used ${formatCurrency(used, 'GBP')} of your ${formatCurrency(limit, 'GBP')} ISA allowance for ${taxYear}. You have ${formatCurrency(remaining, 'GBP')} remaining.`;
      }
      return `You have ${formatCurrency(remaining, 'GBP')} of ISA allowance left for ${taxYear}. That's ${percentageUsed.toFixed(0)}% used so far.`;
    };

    const getActionMessage = () => {
      if (percentageUsed >= 100) {
        return 'Your allowance resets on 6 April. Start planning for next tax year!';
      }
      if (daysRemaining && daysRemaining < 30) {
        return `Only ${daysRemaining} days left in the tax year! Use your remaining allowance before it's gone.`;
      }
      if (percentageUsed < 50) {
        return 'Consider maximizing your ISA contributions to make the most of tax-free growth.';
      }
      return 'Keep contributing to make the most of your tax-free allowance.';
    };

    return (
      <div style={narrativeSectionStyle}>
        <h3 style={sectionHeadingStyle}>Your ISA Allowance ({taxYear})</h3>
        <p style={paragraphStyle}>
          <strong style={{ color: getWarningColor() }}>{getMessage()}</strong>
        </p>
        <p style={paragraphStyle}>
          {getActionMessage()}
        </p>

        {/* Progress Bar */}
        <div style={{ marginTop: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.875rem', color: '#475569', fontWeight: 500 }}>
              Used: {formatCurrency(used, 'GBP')}
            </span>
            <span style={{ fontSize: '0.875rem', color: '#475569', fontWeight: 500 }}>
              Remaining: {formatCurrency(remaining, 'GBP')}
            </span>
          </div>
          <div style={{ width: '100%', height: '24px', backgroundColor: '#E2E8F0', borderRadius: '12px', overflow: 'hidden' }}>
            <div
              style={{
                width: `${Math.min(percentageUsed, 100)}%`,
                height: '100%',
                backgroundColor: getWarningColor(),
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
              {percentageUsed > 15 && `${percentageUsed.toFixed(0)}%`}
            </div>
          </div>
        </div>

        {/* Expandable Educational Content */}
        <details style={{ marginTop: '16px', cursor: 'pointer' }}>
          <summary style={{ fontSize: '0.875rem', color: '#2563EB', fontWeight: 500 }}>
            Tell me more about ISAs →
          </summary>
          <div style={{ marginTop: '12px', padding: '16px', backgroundColor: '#F8FAFC', borderRadius: '8px', fontSize: '0.95rem', color: '#475569', lineHeight: '1.7' }}>
            <p style={{ marginBottom: '12px' }}>
              <strong>Individual Savings Accounts (ISAs)</strong> are a tax-efficient way to save in the UK.
              You can save up to £20,000 per tax year (6 April to 5 April) across all ISA types, and all
              interest, dividends, and capital gains are completely tax-free.
            </p>
            <p style={{ marginBottom: '12px' }}>
              <strong>Types of ISAs:</strong> Cash ISAs (savings), Stocks & Shares ISAs (investments),
              Lifetime ISAs (for first-time home buyers or retirement), and Innovative Finance ISAs (peer-to-peer lending).
            </p>
            <p>
              <strong>Important:</strong> Your allowance doesn't roll over. Any unused allowance is lost
              at the end of the tax year, so it's worth maximizing your contributions if you can.
            </p>
          </div>
        </details>
      </div>
    );
  }

  if (isTFSA) {
    const { annualLimit = 0, annualUsed = 0, annualRemaining = 0, lifetimeLimit = 0, lifetimeUsed = 0, lifetimeRemaining = 0, taxYear = '' } = allowance || {};

    const annualPercentage = (annualUsed / annualLimit) * 100;
    const lifetimePercentage = (lifetimeUsed / lifetimeLimit) * 100;

    const getAnnualColor = () => {
      if (annualPercentage >= 90) return '#EF4444';
      if (annualPercentage >= 70) return '#F59E0B';
      return '#10B981';
    };

    const getLifetimeColor = () => {
      if (lifetimePercentage >= 90) return '#EF4444';
      if (lifetimePercentage >= 70) return '#F59E0B';
      return '#10B981';
    };

    const getMessage = () => {
      if (annualPercentage >= 100 && lifetimePercentage >= 100) {
        return `You've reached both your annual (R${annualLimit.toLocaleString()}) and lifetime (R${lifetimeLimit.toLocaleString()}) TFSA limits. Well done!`;
      }
      if (annualPercentage >= 100) {
        return `You've fully used your R${annualLimit.toLocaleString()} TFSA allowance for ${taxYear}. You still have R${lifetimeRemaining.toLocaleString()} lifetime allowance remaining.`;
      }
      if (lifetimePercentage >= 100) {
        return `You've reached your R${lifetimeLimit.toLocaleString()} lifetime TFSA limit. You can't contribute more, but your investments can continue to grow tax-free.`;
      }
      return `You've used R${annualUsed.toLocaleString()} of your R${annualLimit.toLocaleString()} annual TFSA allowance for ${taxYear}.`;
    };

    return (
      <div style={narrativeSectionStyle}>
        <h3 style={sectionHeadingStyle}>Your TFSA Allowance ({taxYear})</h3>
        <p style={paragraphStyle}>
          <strong>{getMessage()}</strong>
        </p>

        {/* Annual Allowance Progress Bar */}
        <div style={{ marginTop: '24px' }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#0F172A', marginBottom: '12px' }}>
            Annual Allowance
          </h4>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.875rem', color: '#475569', fontWeight: 500 }}>
              Used: R{annualUsed.toLocaleString()}
            </span>
            <span style={{ fontSize: '0.875rem', color: '#475569', fontWeight: 500 }}>
              Remaining: R{annualRemaining.toLocaleString()}
            </span>
          </div>
          <div style={{ width: '100%', height: '24px', backgroundColor: '#E2E8F0', borderRadius: '12px', overflow: 'hidden' }}>
            <div
              style={{
                width: `${Math.min(annualPercentage, 100)}%`,
                height: '100%',
                backgroundColor: getAnnualColor(),
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
              {annualPercentage > 15 && `${annualPercentage.toFixed(0)}%`}
            </div>
          </div>
        </div>

        {/* Lifetime Allowance Progress Bar */}
        <div style={{ marginTop: '24px' }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#0F172A', marginBottom: '12px' }}>
            Lifetime Allowance (R500,000 cap)
          </h4>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.875rem', color: '#475569', fontWeight: 500 }}>
              Used: R{lifetimeUsed.toLocaleString()}
            </span>
            <span style={{ fontSize: '0.875rem', color: '#475569', fontWeight: 500 }}>
              Remaining: R{lifetimeRemaining.toLocaleString()}
            </span>
          </div>
          <div style={{ width: '100%', height: '24px', backgroundColor: '#E2E8F0', borderRadius: '12px', overflow: 'hidden' }}>
            <div
              style={{
                width: `${Math.min(lifetimePercentage, 100)}%`,
                height: '100%',
                backgroundColor: getLifetimeColor(),
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
              {lifetimePercentage > 15 && `${lifetimePercentage.toFixed(0)}%`}
            </div>
          </div>
        </div>

        {/* Expandable Educational Content */}
        <details style={{ marginTop: '16px', cursor: 'pointer' }}>
          <summary style={{ fontSize: '0.875rem', color: '#2563EB', fontWeight: 500 }}>
            Tell me more about TFSAs →
          </summary>
          <div style={{ marginTop: '12px', padding: '16px', backgroundColor: '#F8FAFC', borderRadius: '8px', fontSize: '0.95rem', color: '#475569', lineHeight: '1.7' }}>
            <p style={{ marginBottom: '12px' }}>
              <strong>Tax-Free Savings Accounts (TFSAs)</strong> are South Africa's tax-efficient investment
              vehicle. You can contribute up to R36,000 per tax year (1 March to 28/29 February) with a
              lifetime limit of R500,000.
            </p>
            <p style={{ marginBottom: '12px' }}>
              <strong>Important difference from ISAs:</strong> Unlike UK ISAs, TFSA withdrawals do NOT
              restore your contribution room. Once you've contributed R500,000 over your lifetime, you
              cannot contribute more—even if you withdraw funds.
            </p>
            <p>
              <strong>Tax benefits:</strong> All interest, dividends, and capital gains within a TFSA are
              completely tax-free. This makes TFSAs excellent for long-term wealth building.
            </p>
          </div>
        </details>
      </div>
    );
  }

  return null;
}
