import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { EmailVerification } from '../../src/components/auth/EmailVerification';
import { authEndpoints } from '../../src/utils/api';

// Mock the API
jest.mock('../../src/utils/api', () => ({
  authEndpoints: {
    verifyEmail: jest.fn(),
  },
}));

// Mock window.location
delete window.location;
window.location = { href: '' };

describe('EmailVerification', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    window.location.href = '';
  });

  test('shows verifying state initially', () => {
    render(<EmailVerification token="valid-token" />);

    expect(screen.getByText(/verifying your email/i)).toBeInTheDocument();
  });

  test('shows success message on successful verification', async () => {
    const mockResponse = {
      success: true,
      message: 'Email verified successfully',
    };

    authEndpoints.verifyEmail.mockResolvedValueOnce(mockResponse);

    render(<EmailVerification token="valid-token" />);

    await waitFor(() => {
      expect(screen.getByText(/success/i)).toBeInTheDocument();
      expect(screen.getByText(/email verified successfully/i)).toBeInTheDocument();
    });
  });

  test('shows countdown and redirects after success', async () => {
    jest.useFakeTimers();

    const mockResponse = {
      success: true,
      message: 'Email verified successfully',
    };

    authEndpoints.verifyEmail.mockResolvedValueOnce(mockResponse);

    const onSuccess = jest.fn();
    render(<EmailVerification token="valid-token" onSuccess={onSuccess} />);

    await waitFor(() => {
      expect(screen.getByText(/redirecting to login in 3 seconds/i)).toBeInTheDocument();
    });

    // Fast-forward time
    jest.advanceTimersByTime(3000);

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled();
    });

    jest.useRealTimers();
  });

  test('shows error message on failed verification', async () => {
    const mockError = new Error('Invalid or expired token');
    authEndpoints.verifyEmail.mockRejectedValueOnce(mockError);

    render(<EmailVerification token="invalid-token" />);

    await waitFor(() => {
      expect(screen.getByText(/verification failed/i)).toBeInTheDocument();
      expect(screen.getByText(/invalid or expired token/i)).toBeInTheDocument();
    });
  });

  test('shows error when no token provided', async () => {
    render(<EmailVerification token="" />);

    await waitFor(() => {
      expect(screen.getByText(/verification failed/i)).toBeInTheDocument();
      expect(screen.getByText(/no token provided/i)).toBeInTheDocument();
    });
  });

  test('calls verifyEmail API with correct token', async () => {
    const mockResponse = { success: true };
    authEndpoints.verifyEmail.mockResolvedValueOnce(mockResponse);

    render(<EmailVerification token="test-token-123" />);

    await waitFor(() => {
      expect(authEndpoints.verifyEmail).toHaveBeenCalledWith('test-token-123');
    });
  });

  test('shows resend verification button on error', async () => {
    const mockError = new Error('Token expired');
    authEndpoints.verifyEmail.mockRejectedValueOnce(mockError);

    render(<EmailVerification token="expired-token" />);

    await waitFor(() => {
      expect(screen.getByText(/request new verification link/i)).toBeInTheDocument();
      expect(screen.getByText(/back to login/i)).toBeInTheDocument();
    });
  });

  test('shows go to login button on success', async () => {
    const mockResponse = { success: true };
    authEndpoints.verifyEmail.mockResolvedValueOnce(mockResponse);

    render(<EmailVerification token="valid-token" />);

    await waitFor(() => {
      expect(screen.getByText(/go to login now/i)).toBeInTheDocument();
    });
  });
});
