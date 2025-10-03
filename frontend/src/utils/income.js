/**
 * Income utility functions
 * Helper functions for formatting, calculating, and managing income data
 */

/**
 * Format currency with symbol
 * @param {number} amount - The amount to format
 * @param {string} currency - Currency code (GBP, ZAR, USD, EUR)
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (amount, currency) => {
  const symbols = {
    GBP: '£',
    ZAR: 'R',
    USD: '$',
    EUR: '€'
  };

  const symbol = symbols[currency] || currency;
  const formattedAmount = amount.toLocaleString('en-GB', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });

  return `${symbol}${formattedAmount}`;
};

/**
 * Format currency in compact form (e.g., £325k)
 * @param {number} amount - The amount to format
 * @param {string} currency - Currency code
 * @returns {string} Compact formatted currency string
 */
export const formatCurrencyCompact = (amount, currency) => {
  const symbols = {
    GBP: '£',
    ZAR: 'R',
    USD: '$',
    EUR: '€'
  };

  const symbol = symbols[currency] || currency;

  if (amount >= 1000000) {
    return `${symbol}${(amount / 1000000).toFixed(1)}m`;
  } else if (amount >= 1000) {
    return `${symbol}${(amount / 1000).toFixed(1)}k`;
  }

  return `${symbol}${amount.toFixed(0)}`;
};

/**
 * Get income type icon
 * @param {string} type - Income type
 * @returns {string} Emoji icon for income type
 */
export const getIncomeTypeIcon = (type) => {
  const icons = {
    employment: '💼',
    self_employment: '👔',
    rental: '🏠',
    dividend: '📊',
    interest: '💰',
    investment: '📈',
    pension: '👴',
    capital_gains: '💎',
    other: '💵'
  };
  return icons[type] || '💵';
};

/**
 * Get income type label
 * @param {string} type - Income type
 * @returns {string} Human-readable label
 */
export const getIncomeTypeLabel = (type) => {
  const labels = {
    employment: 'Employment',
    self_employment: 'Self-Employment',
    rental: 'Rental Income',
    dividend: 'Dividend Income',
    interest: 'Interest Income',
    investment: 'Investment Income',
    pension: 'Pension',
    capital_gains: 'Capital Gains',
    other: 'Other Income'
  };
  return labels[type] || 'Income';
};

/**
 * Get current UK tax year
 * @returns {string} Current UK tax year (e.g., '2024/25')
 */
export const getCurrentUKTaxYear = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;
  const day = now.getDate();

  // UK tax year runs from 6 April to 5 April
  if (month < 4 || (month === 4 && day < 6)) {
    return `${year - 1}/${(year % 100).toString().padStart(2, '0')}`;
  }
  return `${year}/${((year + 1) % 100).toString().padStart(2, '0')}`;
};

/**
 * Get current SA tax year
 * @returns {string} Current SA tax year (e.g., '2024/2025')
 */
export const getCurrentSATaxYear = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;

  // SA tax year runs from 1 March to 28/29 February
  if (month < 3) {
    return `${year - 1}/${year}`;
  }
  return `${year}/${year + 1}`;
};

/**
 * Get UK tax year dates
 * @param {string} taxYear - UK tax year (e.g., '2024/25')
 * @returns {object} Start and end dates
 */
export const getUKTaxYearDates = (taxYear) => {
  const [startYear] = taxYear.split('/');
  const year = parseInt(startYear, 10);

  return {
    start: `6 April ${year}`,
    end: `5 April ${year + 1}`
  };
};

/**
 * Get SA tax year dates
 * @param {string} taxYear - SA tax year (e.g., '2024/2025')
 * @returns {object} Start and end dates
 */
export const getSATaxYearDates = (taxYear) => {
  const [startYear, endYear] = taxYear.split('/');

  return {
    start: `1 March ${startYear}`,
    end: `28 February ${endYear}`
  };
};

/**
 * Get list of recent UK tax years
 * @param {number} count - Number of years to return
 * @returns {Array<string>} Array of tax years
 */
export const getRecentUKTaxYears = (count = 6) => {
  const currentYear = getCurrentUKTaxYear();
  const [startYear] = currentYear.split('/');
  const year = parseInt(startYear, 10);

  const years = [];
  for (let i = 0; i < count; i++) {
    const y = year - i;
    years.push(`${y}/${((y + 1) % 100).toString().padStart(2, '0')}`);
  }

  return years;
};

/**
 * Get list of recent SA tax years
 * @param {number} count - Number of years to return
 * @returns {Array<string>} Array of tax years
 */
export const getRecentSATaxYears = (count = 6) => {
  const currentYear = getCurrentSATaxYear();
  const [startYear] = currentYear.split('/');
  const year = parseInt(startYear, 10);

  const years = [];
  for (let i = 0; i < count; i++) {
    const y = year - i;
    years.push(`${y}/${y + 1}`);
  }

  return years;
};

/**
 * Format frequency
 * @param {string} frequency - Frequency code
 * @returns {string} Human-readable frequency
 */
export const formatFrequency = (frequency) => {
  const labels = {
    annual: 'Annually',
    monthly: 'Monthly',
    weekly: 'Weekly',
    quarterly: 'Quarterly',
    one_time: 'One-time'
  };
  return labels[frequency] || frequency;
};

/**
 * Get country flag emoji
 * @param {string} country - Country code
 * @returns {string} Flag emoji
 */
export const getCountryFlag = (country) => {
  const flags = {
    UK: '🇬🇧',
    ZA: '🇿🇦',
    US: '🇺🇸',
    EU: '🇪🇺',
    OTHER: '🌍'
  };
  return flags[country] || '🌍';
};

/**
 * Get country label
 * @param {string} country - Country code
 * @returns {string} Country name
 */
export const getCountryLabel = (country) => {
  const labels = {
    UK: 'United Kingdom',
    ZA: 'South Africa',
    US: 'United States',
    EU: 'European Union',
    OTHER: 'Other'
  };
  return labels[country] || country;
};

/**
 * Format date in friendly format
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
export const formatDate = (dateString) => {
  if (!dateString) return '';

  const date = new Date(dateString);
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return date.toLocaleDateString('en-GB', options);
};

/**
 * Calculate annual amount from frequency
 * @param {number} amount - Amount
 * @param {string} frequency - Frequency (annual, monthly, weekly, quarterly, one_time)
 * @returns {number} Annual amount
 */
export const calculateAnnualAmount = (amount, frequency) => {
  const multipliers = {
    annual: 1,
    monthly: 12,
    weekly: 52,
    quarterly: 4,
    one_time: 1
  };

  return amount * (multipliers[frequency] || 1);
};

/**
 * Group income by type
 * @param {Array} incomes - Array of income objects
 * @returns {object} Income grouped by type
 */
export const groupIncomeByType = (incomes) => {
  return incomes.reduce((acc, income) => {
    const type = income.income_type || income.incomeType;
    if (!acc[type]) {
      acc[type] = [];
    }
    acc[type].push(income);
    return acc;
  }, {});
};

/**
 * Group income by country
 * @param {Array} incomes - Array of income objects
 * @returns {object} Income grouped by country
 */
export const groupIncomeByCountry = (incomes) => {
  return incomes.reduce((acc, income) => {
    const country = income.source_country || income.sourceCountry;
    if (!acc[country]) {
      acc[country] = [];
    }
    acc[country].push(income);
    return acc;
  }, {});
};

/**
 * Calculate total income
 * @param {Array} incomes - Array of income objects
 * @param {string} currency - Target currency (GBP or ZAR)
 * @returns {number} Total income in target currency
 */
export const calculateTotalIncome = (incomes, currency = 'GBP') => {
  return incomes.reduce((total, income) => {
    let amount = 0;

    if (currency === 'GBP') {
      amount = income.gbp_amount || income.gbpAmount || 0;
    } else if (currency === 'ZAR') {
      amount = income.zar_amount || income.zarAmount || 0;
    }

    return total + amount;
  }, 0);
};

/**
 * Get income type color
 * @param {string} type - Income type
 * @returns {string} Color class or hex code
 */
export const getIncomeTypeColor = (type) => {
  const colors = {
    employment: '#2563EB',
    self_employment: '#7C3AED',
    rental: '#059669',
    dividend: '#DC2626',
    interest: '#D97706',
    investment: '#DB2777',
    pension: '#0891B2',
    capital_gains: '#65A30D',
    other: '#6B7280'
  };
  return colors[type] || '#6B7280';
};
