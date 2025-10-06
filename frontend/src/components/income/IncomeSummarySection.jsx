import React from 'react';
import { Card } from 'internal-packages/ui';
import {
  formatCurrency,
  getIncomeTypeLabel,
  getIncomeTypeIcon,
  getCountryLabel,
  getCountryFlag
} from '../../utils/income';

export function IncomeSummarySection({ summary, taxYear, country, loading }) {
  const narrativeSectionStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
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

  const metricGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
    marginTop: '24px',
  };

  const compactMetricStyle = {
    padding: '16px',
    backgroundColor: '#F8FAFC',
    borderRadius: '8px',
    border: '1px solid #E2E8F0',
  };

  const metricValueStyle = {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#0F172A',
    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace',
  };

  const metricLabelStyle = {
    fontSize: '0.75rem',
    color: '#475569',
    marginTop: '4px',
  };

  const breakdownSectionStyle = {
    marginTop: '32px',
  };

  const breakdownItemStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px',
    backgroundColor: '#F8FAFC',
    borderRadius: '6px',
    marginBottom: '8px',
  };

  const breakdownLabelStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    color: '#475569',
    fontSize: '0.95rem',
  };

  const breakdownValueStyle = {
    fontWeight: 600,
    color: '#0F172A',
    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace',
  };

  const emptyStateStyle = {
    textAlign: 'center',
    padding: '48px 32px',
    color: '#64748B',
  };

  if (loading) {
    return (
      <div style={narrativeSectionStyle}>
        <div style={{ color: '#64748B', textAlign: 'center', padding: '32px' }}>
          Loading income summary...
        </div>
      </div>
    );
  }

  if (!summary || summary.totalIncomeGbp === 0) {
    return (
      <div style={narrativeSectionStyle}>
        <h3 style={sectionHeadingStyle}>Your income for {taxYear}</h3>
        <div style={emptyStateStyle}>
          <p style={{ fontSize: '1.1rem', marginBottom: '16px' }}>
            No income recorded for this tax year yet.
          </p>
          <p style={{ color: '#94A3B8' }}>
            Add your first income entry to start tracking your earnings and tax obligations.
          </p>
        </div>
      </div>
    );
  }

  const totalGBP = parseFloat(summary.totalIncomeGbp) || 0;
  const totalZAR = parseFloat(summary.totalIncomeZar) || 0;
  const taxWithheld = parseFloat(summary.totalTaxWithheld) || 0;
  const foreignIncome = parseFloat(summary.foreignIncome) || 0;
  const foreignTaxCredits = parseFloat(summary.foreignTaxCredit) || 0;

  // Build narrative text
  const getNarrativeText = () => {
    const gbpFormatted = formatCurrency(totalGBP, 'GBP');
    const zarFormatted = formatCurrency(totalZAR, 'ZAR');

    let narrative = `Your net income for ${taxYear}: `;

    if (totalGBP > 0 && totalZAR > 0) {
      narrative += `${gbpFormatted} from UK sources and ${zarFormatted} from SA sources (after tax withheld).`;
    } else if (totalGBP > 0) {
      narrative += `${gbpFormatted} from UK sources (after tax withheld).`;
    } else if (totalZAR > 0) {
      narrative += `${zarFormatted} from SA sources (after tax withheld).`;
    } else {
      narrative += `No income recorded for this tax year.`;
    }

    return narrative;
  };

  return (
    <div style={narrativeSectionStyle}>
      <h3 style={sectionHeadingStyle}>Your income summary for {taxYear}</h3>

      <p style={paragraphStyle}>{getNarrativeText()}</p>

      {/* Key Metrics */}
      <div style={metricGridStyle}>
        {totalGBP > 0 && (
          <div style={compactMetricStyle}>
            <div style={metricValueStyle}>{formatCurrency(totalGBP, 'GBP')}</div>
            <div style={metricLabelStyle}>UK Income (Net)</div>
          </div>
        )}
        {totalZAR > 0 && (
          <div style={compactMetricStyle}>
            <div style={metricValueStyle}>{formatCurrency(totalZAR, 'ZAR')}</div>
            <div style={metricLabelStyle}>SA Income (Net)</div>
          </div>
        )}
        {taxWithheld > 0 && (
          <div style={compactMetricStyle}>
            <div style={metricValueStyle}>{formatCurrency(taxWithheld, 'GBP')}</div>
            <div style={metricLabelStyle}>Tax Withheld</div>
          </div>
        )}
        {foreignIncome > 0 && (
          <div style={compactMetricStyle}>
            <div style={metricValueStyle}>{formatCurrency(foreignIncome, 'GBP')}</div>
            <div style={metricLabelStyle}>Foreign Income</div>
          </div>
        )}
      </div>

      {/* Tax Withheld Information */}
      {taxWithheld > 0 && (
        <p style={{ ...paragraphStyle, marginTop: '24px' }}>
          You've already paid <strong>{formatCurrency(taxWithheld, 'GBP')}</strong> in tax through
          PAYE or withholding at source. This will be credited against your final tax liability.
        </p>
      )}

      {/* Foreign Income Information */}
      {foreignIncome > 0 && (
        <div
          style={{
            backgroundColor: '#EFF6FF',
            borderLeft: '4px solid #3B82F6',
            padding: '16px 24px',
            borderRadius: '8px',
            marginTop: '24px',
          }}
        >
          <p style={{ fontWeight: 600, color: '#1E40AF', marginBottom: '8px' }}>
            Foreign income detected
          </p>
          <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
            You have <strong>{formatCurrency(foreignIncome, 'GBP')}</strong> in foreign income.
            Under the UK-SA Double Tax Agreement, you may be able to claim credit for foreign tax
            paid ({formatCurrency(foreignTaxCredits, 'GBP')} in credits available).
          </p>
        </div>
      )}

      {/* Income by Type Breakdown */}
      {summary.incomeByType && Object.keys(summary.incomeByType).length > 0 && (
        <div style={breakdownSectionStyle}>
          <h4 style={{ ...sectionHeadingStyle, fontSize: '1rem', marginBottom: '12px' }}>
            Income by Type
          </h4>
          {Object.entries(summary.incomeByType).map(([type, amount]) => (
            <div key={type} style={breakdownItemStyle}>
              <div style={breakdownLabelStyle}>
                <span>{getIncomeTypeIcon(type)}</span>
                <span>{getIncomeTypeLabel(type)}</span>
              </div>
              <div style={breakdownValueStyle}>{formatCurrency(amount, 'GBP')}</div>
            </div>
          ))}
        </div>
      )}

      {/* Income by Country Breakdown */}
      {summary.incomeBySource && Object.keys(summary.incomeBySource).length > 0 && (
        <div style={breakdownSectionStyle}>
          <h4 style={{ ...sectionHeadingStyle, fontSize: '1rem', marginBottom: '12px' }}>
            Income by Source Country
          </h4>
          {Object.entries(summary.incomeBySource).map(([countryCode, amount]) => (
            <div key={countryCode} style={breakdownItemStyle}>
              <div style={breakdownLabelStyle}>
                <span>{getCountryFlag(countryCode)}</span>
                <span>{getCountryLabel(countryCode)}</span>
              </div>
              <div style={breakdownValueStyle}>{formatCurrency(amount, 'GBP')}</div>
            </div>
          ))}
        </div>
      )}

      {/* Educational Callout */}
      <div
        style={{
          backgroundColor: '#F0FDF4',
          borderLeft: '4px solid #10B981',
          padding: '16px 24px',
          borderRadius: '8px',
          marginTop: '24px',
        }}
      >
        <p style={{ fontWeight: 600, color: '#065F46', marginBottom: '8px' }}>
          Understanding your income
        </p>
        <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.7' }}>
          This is your gross income before tax. We track your income in the currency you received it,
          then convert to GBP and ZAR for tax calculations. Your actual tax liability will depend on
          your tax residency status, domicile, and applicable allowances.
        </p>
      </div>
    </div>
  );
}
