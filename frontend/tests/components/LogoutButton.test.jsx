import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { LogoutButton } from '../../src/components/auth/LogoutButton';
import { authEndpoints } from '../../src/utils/api';
import { authStorage } from '../../src/utils/auth';

// Mock the API and storage
jest.mock('../../src/utils/api', () => ({
  authEndpoints: {
    logout: jest.fn(),
  },
}));

jest.mock('../../src/utils/auth', () => ({
  authStorage: {
    clear: jest.fn(),
  },
}));

// Mock window.location
delete window.location;
window.location = { href: '' };

describe('LogoutButton', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    window.location.href = '';
  });

  test('renders logout button with default text', () => {
    render(<LogoutButton />);

    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
  });

  test('renders with custom children text', () => {
    render(<LogoutButton>Sign Out</LogoutButton>);

    expect(screen.getByRole('button', { name: /sign out/i })).toBeInTheDocument();
  });

  test('calls logout API when clicked', async () => {
    authEndpoints.logout.mockResolvedValueOnce({ success: true });

    render(<LogoutButton />);

    const button = screen.getByRole('button', { name: /logout/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(authEndpoints.logout).toHaveBeenCalled();
    });
  });

  test('clears auth storage on logout', async () => {
    authEndpoints.logout.mockResolvedValueOnce({ success: true });

    render(<LogoutButton />);

    const button = screen.getByRole('button', { name: /logout/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(authStorage.clear).toHaveBeenCalled();
    });
  });

  test('redirects to login page after logout', async () => {
    authEndpoints.logout.mockResolvedValueOnce({ success: true });

    render(<LogoutButton />);

    const button = screen.getByRole('button', { name: /logout/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(window.location.href).toBe('/login');
    });
  });

  test('calls onSuccess callback if provided', async () => {
    authEndpoints.logout.mockResolvedValueOnce({ success: true });

    const onSuccess = jest.fn();
    render(<LogoutButton onSuccess={onSuccess} />);

    const button = screen.getByRole('button', { name: /logout/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  test('clears storage even if API call fails', async () => {
    const mockError = new Error('Network error');
    authEndpoints.logout.mockRejectedValueOnce(mockError);

    // Mock console.error to avoid test output noise
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    render(<LogoutButton />);

    const button = screen.getByRole('button', { name: /logout/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(authStorage.clear).toHaveBeenCalled();
      expect(window.location.href).toBe('/login');
    });

    consoleErrorSpy.mockRestore();
  });

  test('shows loading state while logging out', async () => {
    authEndpoints.logout.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(<LogoutButton />);

    const button = screen.getByRole('button', { name: /logout/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(button).toHaveTextContent(/logging out/i);
      expect(button).toBeDisabled();
    });
  });

  test('accepts custom variant prop', () => {
    render(<LogoutButton variant="danger" />);

    const button = screen.getByRole('button', { name: /logout/i });
    expect(button).toBeInTheDocument();
  });

  test('accepts custom className prop', () => {
    render(<LogoutButton className="custom-class" />);

    const button = screen.getByRole('button', { name: /logout/i });
    expect(button).toHaveClass('custom-class');
  });
});
