/**
 * Authentication utility functions for token management
 * Uses localStorage for token storage (consider httpOnly cookies for production)
 */

const ACCESS_TOKEN_KEY = 'goalplan_access_token';
const REFRESH_TOKEN_KEY = 'goalplan_refresh_token';
const USER_KEY = 'goalplan_user';

export const authStorage = {
  /**
   * Store authentication tokens
   */
  setTokens(accessToken, refreshToken) {
    if (accessToken) {
      localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    }
    if (refreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    }
  },

  /**
   * Get access token
   */
  getAccessToken() {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  },

  /**
   * Get refresh token
   */
  getRefreshToken() {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },

  /**
   * Store user information
   */
  setUser(user) {
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
  },

  /**
   * Get user information
   */
  getUser() {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!this.getAccessToken();
  },

  /**
   * Clear all authentication data
   */
  clear() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
};

/**
 * Validate email format
 */
export function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate password strength
 * Requirements: min 12 chars, uppercase, lowercase, number, special char
 */
export function validatePassword(password) {
  if (password.length < 12) {
    return { valid: false, message: 'Password must be at least 12 characters long' };
  }

  if (!/[A-Z]/.test(password)) {
    return { valid: false, message: 'Password must contain at least one uppercase letter' };
  }

  if (!/[a-z]/.test(password)) {
    return { valid: false, message: 'Password must contain at least one lowercase letter' };
  }

  if (!/[0-9]/.test(password)) {
    return { valid: false, message: 'Password must contain at least one number' };
  }

  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    return { valid: false, message: 'Password must contain at least one special character' };
  }

  return { valid: true, message: 'Password is strong' };
}

/**
 * Calculate password strength for UI indicator
 * Returns: weak, medium, strong
 */
export function getPasswordStrength(password) {
  if (!password) return 'none';

  let strength = 0;

  if (password.length >= 12) strength++;
  if (password.length >= 16) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;

  if (strength <= 2) return 'weak';
  if (strength <= 4) return 'medium';
  return 'strong';
}
