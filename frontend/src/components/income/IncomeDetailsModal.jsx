import React from 'react';
import { Button } from 'internal-packages/ui';
import {
  formatCurrency,
  getIncomeTypeLabel,
  getIncomeTypeIcon,
  getCountryLabel,
  getCountryFlag,
  formatDate,
  formatFrequency
} from '../../utils/income';

export function IncomeDetailsModal({ income, onEdit, onDelete, onClose }) {
  if (!income) return null;

  const incomeType = income.income_type || income.incomeType;
  const sourceCountry = income.source_country || income.sourceCountry;
  const description = income.description || '';
  const relatedEntity = income.related_entity || income.relatedEntity || '';
  const amount = income.amount || 0;
  const currency = income.currency || 'GBP';
  const gbpAmount = income.gbp_amount || income.gbpAmount || 0;
  const zarAmount = income.zar_amount || income.zarAmount || 0;
  const frequency = income.frequency || 'annual';
  const startDate = income.start_date || income.startDate;
  const endDate = income.end_date || income.endDate;
  const isGross = income.is_gross !== undefined ? income.is_gross : (income.isGross !== undefined ? income.isGross : true);
  const taxWithheld = income.tax_withheld_at_source || income.taxWithheldAtSource || 0;
  const payeReference = income.paye_reference || income.payeReference || '';
  const exchangeRate = income.exchange_rate_used || income.exchangeRateUsed;
  const exchangeRateDate = income.exchange_rate_date || income.exchangeRateDate;
  const ukTaxYear = income.uk_tax_year || income.ukTaxYear;
  const saTaxYear = income.sa_tax_year || income.saTaxYear;

  const isForeign = sourceCountry !== 'UK' && sourceCountry !== 'ZA';

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
    boxShadow: '0 10px 15px rgba(0, 0, 0, 0.1)',
    maxWidth: '700px',
    width: '100%',
    maxHeight: '90vh',
    overflow: 'auto',
    padding: '32px',
  };

  const modalHeaderStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    fontSize: '1.5rem',
    fontWeight: 700,
    color: '#0F172A',
    marginBottom: '8px',
  };

  const modalSubtitleStyle = {
    color: '#64748B',
    fontSize: '0.95rem',
    marginBottom: '32px',
  };

  const sectionStyle = {
    marginBottom: '32px',
    paddingBottom: '24px',
    borderBottom: '1px solid #E2E8F0',
  };

  const sectionTitleStyle = {
    fontSize: '1.1rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '16px',
  };

  const detailRowStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '12px',
    backgroundColor: '#F8FAFC',
    borderRadius: '6px',
    marginBottom: '8px',
  };

  const detailLabelStyle = {
    color: '#64748B',
    fontSize: '0.95rem',
  };

  const detailValueStyle = {
    color: '#0F172A',
    fontWeight: 600,
    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace',
  };

  const calloutStyle = {
    backgroundColor: '#EFF6FF',
    border: '1px solid #BFDBFE',
    borderLeft: '4px solid #3B82F6',
    padding: '16px',
    borderRadius: '8px',
    marginTop: '16px',
  };

  const calloutTitleStyle = {
    fontWeight: 600,
    color: '#1E40AF',
    marginBottom: '8px',
  };

  const calloutTextStyle = {
    fontSize: '0.9rem',
    color: '#475569',
    lineHeight: '1.7',
  };

  const actionsStyle = {
    display: 'flex',
    gap: '12px',
    justifyContent: 'flex-end',
    marginTop: '32px',
    paddingTop: '24px',
    borderTop: '1px solid #E2E8F0',
  };

  const badgeStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '4px 12px',
    borderRadius: '4px',
    fontSize: '0.875rem',
    fontWeight: 500,
    backgroundColor: '#DBEAFE',
    color: '#1E40AF',
  };

  return (
    <div style={modalOverlayStyle} onClick={onClose}>
      <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
        <div style={modalHeaderStyle}>
          <span>{getIncomeTypeIcon(incomeType)}</span>
          <span>{relatedEntity || description || getIncomeTypeLabel(incomeType)}</span>
        </div>

        <div style={modalSubtitleStyle}>
          {getCountryFlag(sourceCountry)} {getCountryLabel(sourceCountry)} • {formatFrequency(frequency)}
          {isForeign && (
            <>
              {' • '}
              <span style={badgeStyle}>Foreign Income</span>
            </>
          )}
        </div>

        {/* Basic Information */}
        <div style={sectionStyle}>
          <h3 style={sectionTitleStyle}>Income Details</h3>

          <div style={detailRowStyle}>
            <span style={detailLabelStyle}>Income Type</span>
            <span style={detailValueStyle}>{getIncomeTypeLabel(incomeType)}</span>
          </div>

          <div style={detailRowStyle}>
            <span style={detailLabelStyle}>Amount</span>
            <span style={detailValueStyle}>{formatCurrency(amount, currency)}</span>
          </div>

          <div style={detailRowStyle}>
            <span style={detailLabelStyle}>Frequency</span>
            <span style={detailValueStyle}>{formatFrequency(frequency)}</span>
          </div>

          {description && (
            <div style={detailRowStyle}>
              <span style={detailLabelStyle}>Description</span>
              <span style={detailValueStyle}>{description}</span>
            </div>
          )}

          {relatedEntity && (
            <div style={detailRowStyle}>
              <span style={detailLabelStyle}>
                {incomeType === 'employment' ? 'Employer' : 'Related Entity'}
              </span>
              <span style={detailValueStyle}>{relatedEntity}</span>
            </div>
          )}

          <div style={detailRowStyle}>
            <span style={detailLabelStyle}>Income Type</span>
            <span style={detailValueStyle}>{isGross ? 'Gross (before tax)' : 'Net (after tax)'}</span>
          </div>

          <div style={detailRowStyle}>
            <span style={detailLabelStyle}>Start Date</span>
            <span style={detailValueStyle}>{formatDate(startDate)}</span>
          </div>

          {endDate && (
            <div style={detailRowStyle}>
              <span style={detailLabelStyle}>End Date</span>
              <span style={detailValueStyle}>{formatDate(endDate)}</span>
            </div>
          )}
        </div>

        {/* Currency Conversion */}
        <div style={sectionStyle}>
          <h3 style={sectionTitleStyle}>Currency Conversion</h3>

          <div style={detailRowStyle}>
            <span style={detailLabelStyle}>Original Amount</span>
            <span style={detailValueStyle}>{formatCurrency(amount, currency)}</span>
          </div>

          <div style={detailRowStyle}>
            <span style={detailLabelStyle}>Converted to GBP</span>
            <span style={detailValueStyle}>{formatCurrency(gbpAmount, 'GBP')}</span>
          </div>

          <div style={detailRowStyle}>
            <span style={detailLabelStyle}>Converted to ZAR</span>
            <span style={detailValueStyle}>{formatCurrency(zarAmount, 'ZAR')}</span>
          </div>

          {exchangeRate && (
            <>
              <div style={detailRowStyle}>
                <span style={detailLabelStyle}>Exchange Rate</span>
                <span style={detailValueStyle}>{exchangeRate.toFixed(6)}</span>
              </div>

              {exchangeRateDate && (
                <div style={detailRowStyle}>
                  <span style={detailLabelStyle}>Exchange Rate Date</span>
                  <span style={detailValueStyle}>{formatDate(exchangeRateDate)}</span>
                </div>
              )}
            </>
          )}
        </div>

        {/* Tax Information */}
        {(taxWithheld > 0 || payeReference) && (
          <div style={sectionStyle}>
            <h3 style={sectionTitleStyle}>Tax Withheld</h3>

            {taxWithheld > 0 && (
              <div style={detailRowStyle}>
                <span style={detailLabelStyle}>Tax Withheld at Source</span>
                <span style={detailValueStyle}>{formatCurrency(taxWithheld, currency)}</span>
              </div>
            )}

            {payeReference && (
              <div style={detailRowStyle}>
                <span style={detailLabelStyle}>PAYE Reference</span>
                <span style={detailValueStyle}>{payeReference}</span>
              </div>
            )}
          </div>
        )}

        {/* Tax Year Allocations */}
        {(ukTaxYear || saTaxYear) && (
          <div style={sectionStyle}>
            <h3 style={sectionTitleStyle}>Tax Year Allocation</h3>

            {ukTaxYear && (
              <div style={detailRowStyle}>
                <span style={detailLabelStyle}>UK Tax Year</span>
                <span style={detailValueStyle}>{ukTaxYear}</span>
              </div>
            )}

            {saTaxYear && (
              <div style={detailRowStyle}>
                <span style={detailLabelStyle}>SA Tax Year</span>
                <span style={detailValueStyle}>{saTaxYear}</span>
              </div>
            )}
          </div>
        )}

        {/* Tax Treatment Information */}
        {isForeign && (
          <div style={calloutStyle}>
            <div style={calloutTitleStyle}>Foreign Income Tax Treatment</div>
            <div style={calloutTextStyle}>
              This is {getCountryLabel(sourceCountry)}-source income. It may be taxable in the UK as
              worldwide income if you're UK tax resident. Under the UK-SA Double Tax Agreement, you can
              claim foreign tax credit for any {getCountryLabel(sourceCountry)} tax paid, preventing
              double taxation.
            </div>
          </div>
        )}

        {/* Educational Information */}
        <div style={{ ...calloutStyle, backgroundColor: '#F0FDF4', borderLeft: '4px solid #10B981' }}>
          <div style={{ ...calloutTitleStyle, color: '#065F46' }}>
            How this income is taxed
          </div>
          <div style={calloutTextStyle}>
            Your final tax liability depends on your tax residency status and domicile. We convert all
            income to GBP and ZAR for tax calculations. {taxWithheld > 0 && 'Tax already withheld will be credited against your final liability.'}
          </div>
        </div>

        {/* Actions */}
        <div style={actionsStyle}>
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
          <Button variant="secondary" onClick={() => onEdit(income)}>
            Edit
          </Button>
          <Button
            variant="danger"
            onClick={() => {
              if (window.confirm('Are you sure you want to delete this income entry?')) {
                onDelete(income.id);
                onClose();
              }
            }}
          >
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
}
