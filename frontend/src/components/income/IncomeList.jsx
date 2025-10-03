import React, { useState } from 'react';
import { Button, Select, Label } from 'internal-packages/ui';
import {
  formatCurrency,
  getIncomeTypeLabel,
  getIncomeTypeIcon,
  getCountryFlag,
  getCountryLabel,
  formatDate,
  formatFrequency,
  getRecentUKTaxYears,
  getRecentSATaxYears
} from '../../utils/income';

export function IncomeList({
  incomes,
  loading,
  onEdit,
  onDelete,
  onViewDetails,
  selectedTaxYear,
  selectedCountry
}) {
  const [typeFilter, setTypeFilter] = useState('');
  const [countryFilter, setCountryFilter] = useState('');
  const [sortBy, setSortBy] = useState('date_desc');

  const narrativeSectionStyle = {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px',
  };

  const sectionHeadingStyle = {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: '24px',
  };

  const filtersContainerStyle = {
    display: 'flex',
    gap: '16px',
    marginBottom: '24px',
    flexWrap: 'wrap',
  };

  const filterGroupStyle = {
    flex: '1 1 200px',
    minWidth: '150px',
  };

  const incomeCardStyle = {
    padding: '20px',
    backgroundColor: '#F8FAFC',
    border: '1px solid #E2E8F0',
    borderRadius: '8px',
    marginBottom: '12px',
    transition: 'all 150ms ease-in-out',
    cursor: 'pointer',
  };

  const incomeCardHoverStyle = {
    ...incomeCardStyle,
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.07)',
    transform: 'translateY(-2px)',
  };

  const incomeHeaderStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'start',
    marginBottom: '12px',
  };

  const incomeTitleStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '1.05rem',
    fontWeight: 600,
    color: '#0F172A',
  };

  const incomeAmountStyle = {
    fontSize: '1.3rem',
    fontWeight: 'bold',
    color: '#0F172A',
    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace',
  };

  const incomeDetailsRowStyle = {
    display: 'flex',
    gap: '24px',
    flexWrap: 'wrap',
    marginTop: '12px',
    fontSize: '0.875rem',
    color: '#64748B',
  };

  const incomeDetailStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  };

  const badgeStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '0.75rem',
    fontWeight: 500,
  };

  const foreignBadgeStyle = {
    ...badgeStyle,
    backgroundColor: '#DBEAFE',
    color: '#1E40AF',
  };

  const actionsStyle = {
    display: 'flex',
    gap: '8px',
    marginTop: '12px',
    paddingTop: '12px',
    borderTop: '1px solid #E2E8F0',
  };

  const emptyStateStyle = {
    textAlign: 'center',
    padding: '48px 32px',
    color: '#64748B',
  };

  // Filter and sort incomes
  const getFilteredAndSortedIncomes = () => {
    let filtered = [...incomes];

    // Apply type filter
    if (typeFilter) {
      filtered = filtered.filter(
        (income) => (income.income_type || income.incomeType) === typeFilter
      );
    }

    // Apply country filter
    if (countryFilter) {
      filtered = filtered.filter(
        (income) => (income.source_country || income.sourceCountry) === countryFilter
      );
    }

    // Sort
    filtered.sort((a, b) => {
      const dateA = new Date(a.start_date || a.startDate);
      const dateB = new Date(b.start_date || b.startDate);
      const amountA = a.gbp_amount || a.gbpAmount || 0;
      const amountB = b.gbp_amount || b.gbpAmount || 0;

      switch (sortBy) {
        case 'date_desc':
          return dateB - dateA;
        case 'date_asc':
          return dateA - dateB;
        case 'amount_desc':
          return amountB - amountA;
        case 'amount_asc':
          return amountA - amountB;
        default:
          return 0;
      }
    });

    return filtered;
  };

  const filteredIncomes = getFilteredAndSortedIncomes();

  // Get unique income types and countries from data
  const incomeTypes = [...new Set(incomes.map((i) => i.income_type || i.incomeType))];
  const sourceCountries = [...new Set(incomes.map((i) => i.source_country || i.sourceCountry))];

  const [hoveredCard, setHoveredCard] = useState(null);

  if (loading) {
    return (
      <div style={narrativeSectionStyle}>
        <div style={{ color: '#64748B', textAlign: 'center', padding: '32px' }}>
          Loading income entries...
        </div>
      </div>
    );
  }

  return (
    <div style={narrativeSectionStyle}>
      <h3 style={sectionHeadingStyle}>Income Entries</h3>

      {/* Filters */}
      {incomes.length > 0 && (
        <div style={filtersContainerStyle}>
          <div style={filterGroupStyle}>
            <Label>Filter by Type</Label>
            <Select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
              <option value="">All Types</option>
              {incomeTypes.map((type) => (
                <option key={type} value={type}>
                  {getIncomeTypeLabel(type)}
                </option>
              ))}
            </Select>
          </div>

          <div style={filterGroupStyle}>
            <Label>Filter by Country</Label>
            <Select value={countryFilter} onChange={(e) => setCountryFilter(e.target.value)}>
              <option value="">All Countries</option>
              {sourceCountries.map((country) => (
                <option key={country} value={country}>
                  {getCountryLabel(country)}
                </option>
              ))}
            </Select>
          </div>

          <div style={filterGroupStyle}>
            <Label>Sort By</Label>
            <Select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="date_desc">Date (Newest First)</option>
              <option value="date_asc">Date (Oldest First)</option>
              <option value="amount_desc">Amount (High to Low)</option>
              <option value="amount_asc">Amount (Low to High)</option>
            </Select>
          </div>
        </div>
      )}

      {/* Income Cards */}
      {filteredIncomes.length === 0 ? (
        <div style={emptyStateStyle}>
          <p style={{ fontSize: '1.1rem', marginBottom: '16px' }}>
            {incomes.length === 0
              ? 'No income recorded yet.'
              : 'No income matches your filters.'}
          </p>
          <p style={{ color: '#94A3B8' }}>
            {incomes.length === 0
              ? 'Add your first income entry to start tracking earnings →'
              : 'Try adjusting your filters to see more results.'}
          </p>
        </div>
      ) : (
        filteredIncomes.map((income) => {
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
          const taxWithheld = income.tax_withheld_at_source || income.taxWithheldAtSource || 0;
          const isForeign = sourceCountry !== 'UK' && sourceCountry !== 'ZA';

          return (
            <div
              key={income.id}
              style={hoveredCard === income.id ? incomeCardHoverStyle : incomeCardStyle}
              onMouseEnter={() => setHoveredCard(income.id)}
              onMouseLeave={() => setHoveredCard(null)}
              onClick={() => onViewDetails && onViewDetails(income)}
            >
              <div style={incomeHeaderStyle}>
                <div>
                  <div style={incomeTitleStyle}>
                    <span>{getIncomeTypeIcon(incomeType)}</span>
                    <span>
                      {relatedEntity || description || getIncomeTypeLabel(incomeType)}
                    </span>
                  </div>
                  {isForeign && (
                    <span style={{ ...foreignBadgeStyle, marginTop: '8px', display: 'inline-flex' }}>
                      Foreign income (DTA may apply)
                    </span>
                  )}
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={incomeAmountStyle}>{formatCurrency(amount, currency)}</div>
                  <div style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: '4px' }}>
                    {formatFrequency(frequency)}
                  </div>
                </div>
              </div>

              <div style={incomeDetailsRowStyle}>
                <div style={incomeDetailStyle}>
                  <span>{getCountryFlag(sourceCountry)}</span>
                  <span>{getCountryLabel(sourceCountry)}</span>
                </div>
                <div style={incomeDetailStyle}>
                  <span>📅</span>
                  <span>{formatDate(startDate)}</span>
                </div>
                <div style={incomeDetailStyle}>
                  <span>💷</span>
                  <span>GBP: {formatCurrency(gbpAmount, 'GBP')}</span>
                </div>
                <div style={incomeDetailStyle}>
                  <span>💵</span>
                  <span>ZAR: {formatCurrency(zarAmount, 'ZAR')}</span>
                </div>
                {taxWithheld > 0 && (
                  <div style={incomeDetailStyle}>
                    <span>🧾</span>
                    <span>Tax withheld: {formatCurrency(taxWithheld, currency)}</span>
                  </div>
                )}
              </div>

              <div style={actionsStyle}>
                <Button
                  variant="secondary"
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onEdit(income);
                  }}
                >
                  Edit
                </Button>
                <Button
                  variant="danger"
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (window.confirm('Are you sure you want to delete this income entry?')) {
                      onDelete(income.id);
                    }
                  }}
                >
                  Delete
                </Button>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}
