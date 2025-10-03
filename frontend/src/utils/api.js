import { authStorage } from './auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

/**
 * Enhanced API client with authentication support
 */
class AuthApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
    this.isRefreshing = false;
    this.refreshSubscribers = [];
  }

  /**
   * Subscribe to token refresh
   */
  subscribeTokenRefresh(callback) {
    this.refreshSubscribers.push(callback);
  }

  /**
   * Notify all subscribers when token is refreshed
   */
  onTokenRefreshed(token) {
    this.refreshSubscribers.forEach((callback) => callback(token));
    this.refreshSubscribers = [];
  }

  /**
   * Refresh access token
   */
  async refreshAccessToken() {
    const refreshToken = authStorage.getRefreshToken();

    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      authStorage.setTokens(data.accessToken, refreshToken);
      return data.accessToken;
    } catch (error) {
      // Clear auth data and redirect to login
      authStorage.clear();
      window.location.href = '/login';
      throw error;
    }
  }

  /**
   * Make authenticated API request with automatic token refresh
   */
  async request(endpoint, options = {}, isRetry = false) {
    const url = `${this.baseUrl}${endpoint}`;

    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add authorization header if token exists
    const token = authStorage.getAccessToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);

      // Handle 401 Unauthorized - try to refresh token
      if (response.status === 401 && !isRetry) {
        if (!this.isRefreshing) {
          this.isRefreshing = true;

          try {
            const newToken = await this.refreshAccessToken();
            this.isRefreshing = false;
            this.onTokenRefreshed(newToken);

            // Retry original request with new token
            return this.request(endpoint, options, true);
          } catch (refreshError) {
            this.isRefreshing = false;
            throw refreshError;
          }
        } else {
          // Wait for token refresh to complete
          return new Promise((resolve, reject) => {
            this.subscribeTokenRefresh((newToken) => {
              // Retry with new token
              this.request(endpoint, options, true)
                .then(resolve)
                .catch(reject);
            });
          });
        }
      }

      // Handle different response types
      if (response.status === 204) {
        return { success: true };
      }

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        // Extract error message from response
        const errorMessage = data.message || data.detail || response.statusText || 'Request failed';

        const error = new Error(errorMessage);
        error.status = response.status;
        error.data = data;
        throw error;
      }

      return data;
    } catch (error) {
      // Network errors or thrown errors
      if (!error.status) {
        error.message = 'Network error. Please check your connection.';
      }
      throw error;
    }
  }

  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }

  post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  patch(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }
}

export const authApi = new AuthApiClient(API_BASE_URL);

/**
 * Authentication API endpoints
 */
export const authEndpoints = {
  register: (data) => authApi.post('/api/v1/auth/register', data),

  verifyEmail: (token) => authApi.get(`/api/v1/auth/verify-email?token=${token}`),

  resendVerification: (email) => authApi.post('/api/v1/auth/resend-verification', { email }),

  login: (credentials) => authApi.post('/api/v1/auth/login', credentials),

  logout: () => authApi.post('/api/v1/auth/logout'),

  logoutAll: () => authApi.post('/api/v1/auth/logout-all'),

  refreshToken: (refreshToken) => authApi.post('/api/v1/auth/refresh', { refreshToken }),

  enable2FA: () => authApi.post('/api/v1/auth/2fa/enable'),

  verify2FASetup: (code) => authApi.post('/api/v1/auth/2fa/verify-setup', { code }),

  disable2FA: (code) => authApi.post('/api/v1/auth/2fa/disable', { code }),

  getSessions: () => authApi.get('/api/v1/auth/sessions'),
};

/**
 * Profile management API endpoints
 */
export const profileEndpoints = {
  getProfile: () => authApi.get('/api/v1/user/profile'),

  updateProfile: (data) => authApi.patch('/api/v1/user/profile', data),

  changePassword: (currentPassword, newPassword) =>
    authApi.post('/api/v1/user/change-password', {
      currentPassword,
      newPassword,
    }),

  changeEmail: (newEmail, password) =>
    authApi.post('/api/v1/user/change-email', {
      newEmail,
      password,
    }),

  verifyEmailChange: (token) =>
    authApi.post('/api/v1/user/verify-email-change', { token }),

  deleteAccount: (password, exportData = false) =>
    authApi.post('/api/v1/user/delete-account', {
      password,
      exportData,
    }),
};

/**
 * Tax Status API endpoints
 */
export const taxStatusEndpoints = {
  getCurrent: () => authApi.get('/api/v1/user/tax-status'),

  create: (data) => authApi.post('/api/v1/user/tax-status', data),

  getHistory: () => authApi.get('/api/v1/user/tax-status/history'),

  getAtDate: (date) => authApi.get(`/api/v1/user/tax-status/at-date?date=${date}`),

  calculateSRT: (data) => authApi.post('/api/v1/user/tax-status/srt-calculator', data),

  calculateSAPresence: (data) => authApi.post('/api/v1/user/tax-status/sa-presence-test', data),

  getDeemedDomicile: () => authApi.get('/api/v1/user/tax-status/deemed-domicile'),
};

/**
 * Income API endpoints
 */
export const incomeEndpoints = {
  /**
   * Get all income entries with optional filters
   * @param {object} filters - Optional filter parameters (taxYear, incomeType, sourceCountry)
   * @returns {Promise} Income entries
   */
  getAll: async (filters = {}) => {
    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params.append(key, value);
      }
    });

    const queryString = params.toString();
    const endpoint = queryString
      ? `/api/v1/user/income?${queryString}`
      : '/api/v1/user/income';

    return authApi.get(endpoint);
  },

  /**
   * Create new income entry
   * @param {object} data - Income data
   * @returns {Promise} Created income entry
   */
  create: (data) => authApi.post('/api/v1/user/income', data),

  /**
   * Get single income entry by ID
   * @param {string} id - Income ID
   * @returns {Promise} Income entry
   */
  get: (id) => authApi.get(`/api/v1/user/income/${id}`),

  /**
   * Update income entry
   * @param {string} id - Income ID
   * @param {object} data - Updated income data
   * @returns {Promise} Updated income entry
   */
  update: (id, data) => authApi.patch(`/api/v1/user/income/${id}`, data),

  /**
   * Delete income entry (soft delete)
   * @param {string} id - Income ID
   * @returns {Promise} Success response
   */
  delete: (id) => authApi.delete(`/api/v1/user/income/${id}`),

  /**
   * Get income summary for tax year
   * @param {string} taxYear - Tax year (e.g., '2024/25')
   * @param {string} country - Country code (UK or SA)
   * @returns {Promise} Income summary
   */
  getSummary: (taxYear, country = 'UK') => {
    return authApi.get(`/api/v1/user/income/summary/${taxYear}?country=${country}`);
  },
};
