/**
 * Profile management utility functions
 */

/**
 * Validate phone number format (international)
 * Format: +[country code][number]
 */
export function validatePhone(phone) {
  if (!phone) {
    return { valid: true, message: '' }; // Phone is optional
  }

  // International phone format: +[1-9][1-14 digits]
  const phoneRegex = /^\+?[1-9]\d{1,14}$/;

  if (!phoneRegex.test(phone)) {
    return {
      valid: false,
      message: 'Please enter a valid phone number with country code (e.g., +44 7700 900000)',
    };
  }

  return { valid: true, message: '' };
}

/**
 * Validate date of birth
 * Must be at least 18 years old, max 120 years
 */
export function validateDateOfBirth(dateOfBirth) {
  if (!dateOfBirth) {
    return { valid: true, message: '' }; // Optional
  }

  const birthDate = new Date(dateOfBirth);
  const today = new Date();

  // Check if valid date
  if (isNaN(birthDate.getTime())) {
    return { valid: false, message: 'Please enter a valid date' };
  }

  // Calculate age
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }

  // Must be at least 18 years old
  if (age < 18) {
    return { valid: false, message: 'You must be at least 18 years old' };
  }

  // Max age 120 years
  if (age > 120) {
    return { valid: false, message: 'Please enter a valid date of birth' };
  }

  return { valid: true, message: '' };
}

/**
 * Validate timezone
 */
export function validateTimezone(timezone) {
  if (!timezone) {
    return { valid: true, message: '' }; // Optional
  }

  // Check if timezone is valid using Intl API
  try {
    Intl.DateTimeFormat(undefined, { timeZone: timezone });
    return { valid: true, message: '' };
  } catch (error) {
    return { valid: false, message: 'Please select a valid timezone' };
  }
}

/**
 * Common timezone options for UK/SA users
 */
export const commonTimezones = [
  { value: 'Europe/London', label: 'London (GMT/BST)' },
  { value: 'Africa/Johannesburg', label: 'Johannesburg (SAST)' },
  { value: 'UTC', label: 'UTC' },
  { value: 'America/New_York', label: 'New York (EST/EDT)' },
  { value: 'Europe/Paris', label: 'Paris (CET/CEST)' },
  { value: 'Asia/Dubai', label: 'Dubai (GST)' },
  { value: 'Asia/Hong_Kong', label: 'Hong Kong (HKT)' },
  { value: 'Australia/Sydney', label: 'Sydney (AEST/AEDT)' },
];

/**
 * Format date for display
 */
export function formatDate(dateString) {
  if (!dateString) return '';

  const date = new Date(dateString);
  return date.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
}

/**
 * Format date for input field (YYYY-MM-DD)
 */
export function formatDateForInput(dateString) {
  if (!dateString) return '';

  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');

  return `${year}-${month}-${day}`;
}

/**
 * Format phone number for display
 */
export function formatPhoneForDisplay(phone) {
  if (!phone) return '';

  // Basic formatting - add spaces for readability
  // This is a simple implementation; production should handle various formats
  return phone.replace(/(\d{1,3})(\d{1,4})(\d{1,})/, '$1 $2 $3').trim();
}

/**
 * Calculate account deletion date (30 days from now)
 */
export function getAccountDeletionDate() {
  const date = new Date();
  date.setDate(date.getDate() + 30);

  return date.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
}
