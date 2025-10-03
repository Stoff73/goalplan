/**
 * Tax Status utility functions
 * Helper functions for formatting and working with tax status data
 */

/**
 * Format a UK tax year (e.g., "2024/25")
 */
export function formatUKTaxYear(year) {
  if (!year) return '';
  if (year.includes('/')) return year;

  const nextYear = (parseInt(year) + 1).toString().slice(-2);
  return `${year}/${nextYear}`;
}

/**
 * Format a SA tax year (e.g., "2024/2025")
 */
export function formatSATaxYear(year) {
  if (!year) return '';
  if (year.includes('/')) return year;

  const nextYear = parseInt(year) + 1;
  return `${year}/${nextYear}`;
}

/**
 * Format a date range in a friendly format
 */
export function formatDateRange(fromDate, toDate) {
  if (!fromDate) return '';

  const from = new Date(fromDate);
  const fromStr = from.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  if (!toDate) {
    return `from ${fromStr}`;
  }

  const to = new Date(toDate);
  const toStr = to.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  return `${fromStr} to ${toStr}`;
}

/**
 * Get current UK tax year
 */
export function getCurrentUKTaxYear() {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;
  const day = now.getDate();

  // UK tax year starts April 6
  if (month < 4 || (month === 4 && day < 6)) {
    return formatUKTaxYear((year - 1).toString());
  }
  return formatUKTaxYear(year.toString());
}

/**
 * Get current SA tax year
 */
export function getCurrentSATaxYear() {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;

  // SA tax year starts March 1
  if (month < 3) {
    return formatSATaxYear((year - 1).toString());
  }
  return formatSATaxYear(year.toString());
}

/**
 * Get UK residency status description
 */
export function getUKResidencyDescription(isResident) {
  if (isResident) {
    return "You're considered a UK tax resident. This means you're liable to UK tax on your worldwide income.";
  }
  return "You're not a UK tax resident. You're only taxed on UK-source income.";
}

/**
 * Get SA residency status description
 */
export function getSAResidencyDescription(isResident) {
  if (isResident) {
    return "You're considered a South African tax resident. This means you're liable to SA tax on your worldwide income.";
  }
  return "You're not a South African tax resident. You're only taxed on SA-source income.";
}

/**
 * Get domicile status description
 */
export function getDomicileDescription(domicile) {
  const descriptions = {
    UK_DOMICILED: "You're UK domiciled. This means you're subject to UK inheritance tax on your worldwide estate.",
    NON_UK_DOMICILED: "You're non-UK domiciled. You're only subject to UK inheritance tax on UK-based assets.",
    DEEMED_UK_DOMICILE: "You're deemed UK domiciled. After 15 years of UK residence, you're treated as UK domiciled for inheritance tax purposes.",
  };

  return descriptions[domicile] || '';
}

/**
 * Get DTA tie-breaker description
 */
export function getDTATieBreakerDescription(result) {
  if (result === 'UK_RESIDENT') {
    return "Under the Double Tax Agreement, you're treated as UK resident for tax purposes.";
  }
  if (result === 'SA_RESIDENT') {
    return "Under the Double Tax Agreement, you're treated as SA resident for tax purposes.";
  }
  return '';
}

/**
 * Get SRT tie description
 */
export function getSRTTieDescription(tieName) {
  const descriptions = {
    FAMILY: 'Family tie: You have a spouse, civil partner, or minor child who is UK resident',
    ACCOMMODATION: 'Accommodation tie: You have UK accommodation available and used it during the year',
    WORK: 'Work tie: You worked in the UK for 40+ days, doing more than 3 hours work per day',
    '90_DAY': '90-day tie: You spent 90+ days in the UK in either of the previous 2 tax years',
    COUNTRY: 'Country tie: You were present in the UK more than any other single country',
  };

  return descriptions[tieName] || '';
}

/**
 * Format a date to YYYY-MM-DD for inputs
 */
export function formatDateForInput(date) {
  if (!date) return '';
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Get years until deemed domicile
 */
export function getYearsUntilDeemedDomicile(yearsResident) {
  if (yearsResident >= 15) return 0;
  return 15 - yearsResident;
}

/**
 * Calculate deemed domicile progress percentage
 */
export function getDeemedDomicileProgress(yearsResident) {
  return Math.min((yearsResident / 15) * 100, 100);
}
