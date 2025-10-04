import React, { useState } from 'react';
import { Button, Select, Label } from 'internal-packages/ui';

export function PolicyList({
  policies,
  loading,
  onEdit,
  onDelete,
  onView,
  onAdd,
}) {
  const [providerFilter, setProviderFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [countryFilter, setCountryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sortBy, setSortBy] = useState('provider_asc');

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

  const policyCardStyle = {
    padding: '20px',
    backgroundColor: '#F8FAFC',
    border: '1px solid #E2E8F0',
    borderRadius: '8px',
    marginBottom: '12px',
    transition: 'all 150ms ease-in-out',
    cursor: 'pointer',
  };

  const policyCardHoverStyle = {
    ...policyCardStyle,
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.07)',
    transform: 'translateY(-2px)',
  };

  const policyHeaderStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'start',
    marginBottom: '12px',
  };

  const policyTitleStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '1.05rem',
    fontWeight: 600,
    color: '#0F172A',
  };

  const coverAmountStyle = {
    fontSize: '1.3rem',
    fontWeight: 'bold',
    color: '#0F172A',
    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace',
  };

  const policyDetailsRowStyle = {
    display: 'flex',
    gap: '24px',
    flexWrap: 'wrap',
    marginTop: '12px',
    fontSize: '0.875rem',
    color: '#64748B',
  };

  const policyDetailStyle = {
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

  const [hoveredCard, setHoveredCard] = useState(null);

  // Helper functions
  const formatCurrency = (amount, currency = 'GBP') => {
    if (amount === null || amount === undefined) return '-';
    const symbols = { GBP: '£', USD: '$', EUR: '€', ZAR: 'R' };
    const symbol = symbols[currency] || currency;
    return `${symbol}${amount.toLocaleString('en-GB', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
  };

  const getPolicyTypeLabel = (type) => {
    const labels = {
      TERM: 'Term Life',
      WHOLE_OF_LIFE: 'Whole of Life',
      DECREASING_TERM: 'Decreasing Term',
      LEVEL_TERM: 'Level Term',
      INCREASING_TERM: 'Increasing Term',
      FAMILY_INCOME_BENEFIT: 'Family Income Benefit',
      OTHER: 'Other',
    };
    return labels[type] || type;
  };

  const getPolicyTypeIcon = (type) => {
    const icons = {
      TERM: '🛡️',
      WHOLE_OF_LIFE: '♾️',
      DECREASING_TERM: '📉',
      LEVEL_TERM: '➡️',
      INCREASING_TERM: '📈',
      FAMILY_INCOME_BENEFIT: '👨‍👩‍👧‍👦',
      OTHER: '📋',
    };
    return icons[type] || '📋';
  };

  const getStatusBadge = (status) => {
    const badges = {
      ACTIVE: { text: 'Active', color: '#10B981', bg: '#D1FAE5' },
      LAPSED: { text: 'Lapsed', color: '#EF4444', bg: '#FEE2E2' },
      CLAIMED: { text: 'Claimed', color: '#6B7280', bg: '#F3F4F6' },
      MATURED: { text: 'Matured', color: '#8B5CF6', bg: '#F3E8FF' },
    };
    return badges[status] || { text: status, color: '#6B7280', bg: '#F3F4F6' };
  };

  const getIHTBadge = (policy) => {
    // UK policy in trust = outside IHT estate (good)
    if (policy.providerCountry === 'UK' && policy.writtenInTrust) {
      return { text: 'IHT: In Trust ✓', color: '#10B981', bg: '#D1FAE5' };
    }
    // UK policy not in trust = in IHT estate (warning)
    if (policy.providerCountry === 'UK' && !policy.writtenInTrust) {
      return { text: 'IHT: Not in Trust', color: '#F59E0B', bg: '#FEF3C7' };
    }
    return null;
  };

  const getCountryFlag = (country) => {
    const flags = {
      UK: '🇬🇧',
      ZA: '🇿🇦',
      OTHER: '🌍',
    };
    return flags[country] || '🌍';
  };

  const formatFrequency = (frequency) => {
    const labels = {
      MONTHLY: 'monthly',
      ANNUALLY: 'annually',
      SINGLE: 'single premium',
    };
    return labels[frequency] || frequency.toLowerCase();
  };

  // Filter and sort policies
  const getFilteredAndSortedPolicies = () => {
    let filtered = [...policies];

    // Apply provider filter
    if (providerFilter) {
      filtered = filtered.filter((policy) => policy.provider === providerFilter);
    }

    // Apply type filter
    if (typeFilter) {
      filtered = filtered.filter((policy) => policy.policyType === typeFilter);
    }

    // Apply country filter
    if (countryFilter) {
      filtered = filtered.filter((policy) => policy.providerCountry === countryFilter);
    }

    // Apply status filter
    if (statusFilter) {
      filtered = filtered.filter((policy) => policy.status === statusFilter);
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'provider_asc':
          return (a.provider || '').localeCompare(b.provider || '');
        case 'provider_desc':
          return (b.provider || '').localeCompare(a.provider || '');
        case 'cover_desc':
          return (b.coverAmount || 0) - (a.coverAmount || 0);
        case 'cover_asc':
          return (a.coverAmount || 0) - (b.coverAmount || 0);
        case 'premium_desc':
          return (b.annualPremium || 0) - (a.annualPremium || 0);
        case 'premium_asc':
          return (a.annualPremium || 0) - (b.annualPremium || 0);
        case 'start_date_desc':
          return new Date(b.startDate || 0) - new Date(a.startDate || 0);
        case 'start_date_asc':
          return new Date(a.startDate || 0) - new Date(b.startDate || 0);
        default:
          return 0;
      }
    });

    return filtered;
  };

  const filteredPolicies = getFilteredAndSortedPolicies();

  // Get unique values for filters
  const providers = [...new Set(policies.map((p) => p.provider))].filter(Boolean);
  const policyTypes = [...new Set(policies.map((p) => p.policyType))].filter(Boolean);
  const countries = [...new Set(policies.map((p) => p.providerCountry))].filter(Boolean);
  const statuses = [...new Set(policies.map((p) => p.status))].filter(Boolean);

  if (loading) {
    return (
      <div style={narrativeSectionStyle}>
        <div style={{ color: '#64748B', textAlign: 'center', padding: '32px' }}>
          Loading life assurance policies...
        </div>
      </div>
    );
  }

  return (
    <div style={narrativeSectionStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h3 style={sectionHeadingStyle}>Your Life Assurance Policies</h3>
        {onAdd && (
          <Button variant="primary" onClick={onAdd}>
            + Add Policy
          </Button>
        )}
      </div>

      {/* Filters */}
      {policies.length > 0 && (
        <div style={filtersContainerStyle}>
          <div style={filterGroupStyle}>
            <Label>Filter by Provider</Label>
            <Select value={providerFilter} onChange={(e) => setProviderFilter(e.target.value)}>
              <option value="">All Providers</option>
              {providers.map((provider) => (
                <option key={provider} value={provider}>
                  {provider}
                </option>
              ))}
            </Select>
          </div>

          <div style={filterGroupStyle}>
            <Label>Filter by Type</Label>
            <Select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
              <option value="">All Types</option>
              {policyTypes.map((type) => (
                <option key={type} value={type}>
                  {getPolicyTypeLabel(type)}
                </option>
              ))}
            </Select>
          </div>

          <div style={filterGroupStyle}>
            <Label>Filter by Country</Label>
            <Select value={countryFilter} onChange={(e) => setCountryFilter(e.target.value)}>
              <option value="">All Countries</option>
              {countries.map((country) => (
                <option key={country} value={country}>
                  {getCountryFlag(country)} {country}
                </option>
              ))}
            </Select>
          </div>

          <div style={filterGroupStyle}>
            <Label>Filter by Status</Label>
            <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All Statuses</option>
              {statuses.map((status) => (
                <option key={status} value={status}>
                  {getStatusBadge(status).text}
                </option>
              ))}
            </Select>
          </div>

          <div style={filterGroupStyle}>
            <Label>Sort By</Label>
            <Select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="provider_asc">Provider (A-Z)</option>
              <option value="provider_desc">Provider (Z-A)</option>
              <option value="cover_desc">Cover Amount (High to Low)</option>
              <option value="cover_asc">Cover Amount (Low to High)</option>
              <option value="premium_desc">Premium (High to Low)</option>
              <option value="premium_asc">Premium (Low to High)</option>
              <option value="start_date_desc">Start Date (Newest First)</option>
              <option value="start_date_asc">Start Date (Oldest First)</option>
            </Select>
          </div>
        </div>
      )}

      {/* Policy Cards */}
      {filteredPolicies.length === 0 ? (
        <div style={emptyStateStyle}>
          <p style={{ fontSize: '1.1rem', marginBottom: '16px' }}>
            {policies.length === 0
              ? 'No policies yet. Add your first policy.'
              : 'No policies match your filters.'}
          </p>
          <p style={{ color: '#94A3B8' }}>
            {policies.length === 0
              ? 'Start protecting your family by adding a life assurance policy →'
              : 'Try adjusting your filters to see more results.'}
          </p>
          {policies.length === 0 && onAdd && (
            <Button variant="primary" onClick={onAdd} style={{ marginTop: '24px' }}>
              + Add Your First Policy
            </Button>
          )}
        </div>
      ) : (
        filteredPolicies.map((policy) => {
          const statusBadge = getStatusBadge(policy.status);
          const ihtBadge = getIHTBadge(policy);
          const beneficiaryCount = policy.beneficiaries?.length || 0;

          return (
            <div
              key={policy.id}
              style={hoveredCard === policy.id ? policyCardHoverStyle : policyCardStyle}
              onMouseEnter={() => setHoveredCard(policy.id)}
              onMouseLeave={() => setHoveredCard(null)}
              onClick={() => onView && onView(policy)}
            >
              <div style={policyHeaderStyle}>
                <div>
                  <div style={policyTitleStyle}>
                    <span>{getPolicyTypeIcon(policy.policyType)}</span>
                    <span>{policy.provider}</span>
                  </div>
                  <div style={{ display: 'flex', gap: '8px', marginTop: '8px', flexWrap: 'wrap' }}>
                    <span
                      style={{
                        ...badgeStyle,
                        backgroundColor: statusBadge.bg,
                        color: statusBadge.color,
                      }}
                    >
                      {statusBadge.text}
                    </span>
                    {ihtBadge && (
                      <span
                        style={{
                          ...badgeStyle,
                          backgroundColor: ihtBadge.bg,
                          color: ihtBadge.color,
                        }}
                      >
                        {ihtBadge.text}
                      </span>
                    )}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={coverAmountStyle}>
                    {formatCurrency(policy.coverAmount, policy.currency)}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: '4px' }}>
                    cover amount
                  </div>
                </div>
              </div>

              <div style={policyDetailsRowStyle}>
                <div style={policyDetailStyle}>
                  <span>{getCountryFlag(policy.providerCountry)}</span>
                  <span>{getPolicyTypeLabel(policy.policyType)}</span>
                </div>
                <div style={policyDetailStyle}>
                  <span>💰</span>
                  <span>
                    {formatCurrency(policy.premiumAmount, policy.currency)} {formatFrequency(policy.premiumFrequency)}
                  </span>
                </div>
                {beneficiaryCount > 0 && (
                  <div style={policyDetailStyle}>
                    <span>👥</span>
                    <span>
                      {beneficiaryCount} beneficiar{beneficiaryCount === 1 ? 'y' : 'ies'}
                    </span>
                  </div>
                )}
                {policy.criticalIllnessRider && (
                  <div style={policyDetailStyle}>
                    <span>🏥</span>
                    <span>Critical Illness</span>
                  </div>
                )}
              </div>

              <div style={actionsStyle}>
                <Button
                  variant="secondary"
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onView(policy);
                  }}
                >
                  View Details
                </Button>
                <Button
                  variant="secondary"
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onEdit(policy);
                  }}
                >
                  Edit
                </Button>
                <Button
                  variant="danger"
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (
                      window.confirm(
                        `Are you sure you want to delete the ${policy.provider} policy? This action cannot be undone.`
                      )
                    ) {
                      onDelete(policy.id);
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
