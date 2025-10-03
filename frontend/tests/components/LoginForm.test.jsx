import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { LoginForm } from '../../src/components/auth/LoginForm';
import { authEndpoints } from '../../src/utils/api';
import { authStorage } from '../../src/utils/auth';

// Mock the API and storage
jest.mock('../../src/utils/api', () => ({
  authEndpoints: {
    login: jest.fn(),
  },
}));

jest.mock('../../src/utils/auth', () => ({
  authStorage: {
    setTokens: jest.fn(),
    setUser: jest.fn(),
  },
  validateEmail: jest.fn((email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)),
}));

// Mock window.location
delete window.location;
window.location = { href: '' };

describe('LoginForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    window.location.href = '';
  });

  test('renders login form with all fields', () => {
    render(<LoginForm />);

    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: /remember me/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByText(/forgot password/i)).toBeInTheDocument();
  });

  test('validates email format', async () => {
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email address/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
    });
  });

  test('validates required fields', async () => {
    render(<LoginForm />);

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  test('successfully logs in with valid credentials', async () => {
    const mockResponse = {
      accessToken: 'access-token-123',
      refreshToken: 'refresh-token-456',
      user: {
        id: '123',
        email: 'test@example.com',
        firstName: 'John',
        lastName: 'Doe',
      },
    };

    authEndpoints.login.mockResolvedValueOnce(mockResponse);

    const onSuccess = jest.fn();
    render(<LoginForm onSuccess={onSuccess} />);

    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'password123' },
    });

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(authEndpoints.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });

    await waitFor(() => {
      expect(authStorage.setTokens).toHaveBeenCalledWith('access-token-123', 'refresh-token-456');
      expect(authStorage.setUser).toHaveBeenCalledWith(mockResponse.user);
      expect(onSuccess).toHaveBeenCalledWith(mockResponse);
    });
  });

  test('handles 2FA required response', async () => {
    const mockResponse = {
      requiresTwoFactor: true,
      message: 'Please provide your 2FA code',
    };

    authEndpoints.login.mockResolvedValueOnce(mockResponse);

    render(<LoginForm />);

    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'password123' },
    });

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/two-factor authentication/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/authentication code/i)).toBeInTheDocument();
    });
  });

  test('submits 2FA code when required', async () => {
    // First response requires 2FA
    authEndpoints.login.mockResolvedValueOnce({
      requiresTwoFactor: true,
    });

    render(<LoginForm />);

    // Submit initial login
    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByLabelText(/authentication code/i)).toBeInTheDocument();
    });

    // Mock successful 2FA verification
    const mockSuccess = {
      accessToken: 'access-token-123',
      refreshToken: 'refresh-token-456',
      user: { id: '123', email: 'test@example.com' },
    };
    authEndpoints.login.mockResolvedValueOnce(mockSuccess);

    // Submit 2FA code
    fireEvent.change(screen.getByLabelText(/authentication code/i), {
      target: { value: '123456' },
    });
    fireEvent.click(screen.getByRole('button', { name: /verify/i }));

    await waitFor(() => {
      expect(authEndpoints.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
        totpCode: '123456',
      });
    });
  });

  test('toggles backup code input', async () => {
    authEndpoints.login.mockResolvedValueOnce({
      requiresTwoFactor: true,
    });

    render(<LoginForm />);

    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/use backup code/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/use backup code/i));

    expect(screen.getByLabelText(/backup code/i)).toBeInTheDocument();
    expect(screen.getByText(/use authenticator code instead/i)).toBeInTheDocument();
  });

  test('handles invalid credentials error (401)', async () => {
    const mockError = new Error('Invalid email or password');
    mockError.status = 401;
    authEndpoints.login.mockRejectedValueOnce(mockError);

    render(<LoginForm />);

    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'wrongpassword' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument();
    });
  });

  test('handles account locked error (423)', async () => {
    const mockError = new Error('Account locked');
    mockError.status = 423;
    authEndpoints.login.mockRejectedValueOnce(mockError);

    render(<LoginForm />);

    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/account temporarily locked/i)).toBeInTheDocument();
    });
  });

  test('handles unverified email error (403)', async () => {
    const mockError = new Error('Email not verified');
    mockError.status = 403;
    authEndpoints.login.mockRejectedValueOnce(mockError);

    render(<LoginForm />);

    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/please verify your email address/i)).toBeInTheDocument();
    });
  });

  test('disables submit button while submitting', async () => {
    authEndpoints.login.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(<LoginForm />);

    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'password123' },
    });

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(submitButton).toBeDisabled();
      expect(screen.getByText(/signing in/i)).toBeInTheDocument();
    });
  });
});
