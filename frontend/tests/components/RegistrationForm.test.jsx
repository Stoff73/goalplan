import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { RegistrationForm } from '../../src/components/auth/RegistrationForm';
import { authEndpoints } from '../../src/utils/api';

// Mock the API
jest.mock('../../src/utils/api', () => ({
  authEndpoints: {
    register: jest.fn(),
    resendVerification: jest.fn(),
  },
}));

describe('RegistrationForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders registration form with all fields', () => {
    render(<RegistrationForm />);

    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/country preference/i)).toBeInTheDocument();
    expect(screen.getByText(/i accept the/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
  });

  test('validates email format', async () => {
    render(<RegistrationForm />);

    const emailInput = screen.getByLabelText(/email address/i);
    const submitButton = screen.getByRole('button', { name: /create account/i });

    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
    });
  });

  test('validates password strength', async () => {
    render(<RegistrationForm />);

    const passwordInput = screen.getByLabelText(/^password$/i);
    const submitButton = screen.getByRole('button', { name: /create account/i });

    // Test weak password
    fireEvent.change(passwordInput, { target: { value: 'weak' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/password must be at least 12 characters/i)).toBeInTheDocument();
    });
  });

  test('validates password confirmation', async () => {
    render(<RegistrationForm />);

    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitButton = screen.getByRole('button', { name: /create account/i });

    fireEvent.change(passwordInput, { target: { value: 'ValidPassword123!' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'DifferentPassword123!' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
    });
  });

  test('validates required fields', async () => {
    render(<RegistrationForm />);

    const submitButton = screen.getByRole('button', { name: /create account/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/first name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/last name is required/i)).toBeInTheDocument();
    });
  });

  test('validates terms acceptance', async () => {
    render(<RegistrationForm />);

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const firstNameInput = screen.getByLabelText(/first name/i);
    const lastNameInput = screen.getByLabelText(/last name/i);
    const countrySelect = screen.getByLabelText(/country preference/i);
    const submitButton = screen.getByRole('button', { name: /create account/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'ValidPassword123!' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'ValidPassword123!' } });
    fireEvent.change(firstNameInput, { target: { value: 'John' } });
    fireEvent.change(lastNameInput, { target: { value: 'Doe' } });
    fireEvent.change(countrySelect, { target: { value: 'UK' } });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/you must accept the terms and conditions/i)).toBeInTheDocument();
    });
  });

  test('shows password strength indicator', () => {
    render(<RegistrationForm />);

    const passwordInput = screen.getByLabelText(/^password$/i);

    // Weak password
    fireEvent.change(passwordInput, { target: { value: 'weak' } });
    expect(screen.getByText(/weak/i)).toBeInTheDocument();

    // Strong password
    fireEvent.change(passwordInput, { target: { value: 'VeryStrongPassword123!' } });
    expect(screen.getByText(/strong/i)).toBeInTheDocument();
  });

  test('successfully submits valid form', async () => {
    const mockResponse = {
      success: true,
      userId: '123',
      message: 'Registration successful',
    };

    authEndpoints.register.mockResolvedValueOnce(mockResponse);

    const onSuccess = jest.fn();
    render(<RegistrationForm onSuccess={onSuccess} />);

    // Fill in valid data
    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/first name/i), {
      target: { value: 'John' },
    });
    fireEvent.change(screen.getByLabelText(/last name/i), {
      target: { value: 'Doe' },
    });
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'ValidPassword123!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm password/i), {
      target: { value: 'ValidPassword123!' },
    });
    fireEvent.change(screen.getByLabelText(/country preference/i), {
      target: { value: 'UK' },
    });

    const termsCheckbox = screen.getByRole('checkbox', { name: /i accept the/i });
    fireEvent.click(termsCheckbox);

    const submitButton = screen.getByRole('button', { name: /create account/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(authEndpoints.register).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'ValidPassword123!',
        firstName: 'John',
        lastName: 'Doe',
        country: 'UK',
        termsAccepted: true,
        marketingConsent: false,
      });
    });

    await waitFor(() => {
      expect(screen.getByText(/registration successful/i)).toBeInTheDocument();
    });
  });

  test('handles API error', async () => {
    const mockError = new Error('Email already exists');
    authEndpoints.register.mockRejectedValueOnce(mockError);

    render(<RegistrationForm />);

    // Fill in valid data
    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/first name/i), {
      target: { value: 'John' },
    });
    fireEvent.change(screen.getByLabelText(/last name/i), {
      target: { value: 'Doe' },
    });
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'ValidPassword123!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm password/i), {
      target: { value: 'ValidPassword123!' },
    });
    fireEvent.change(screen.getByLabelText(/country preference/i), {
      target: { value: 'UK' },
    });

    const termsCheckbox = screen.getByRole('checkbox', { name: /i accept the/i });
    fireEvent.click(termsCheckbox);

    const submitButton = screen.getByRole('button', { name: /create account/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/email already exists/i)).toBeInTheDocument();
    });
  });

  test('disables submit button while submitting', async () => {
    authEndpoints.register.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(<RegistrationForm />);

    // Fill in valid data
    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/first name/i), {
      target: { value: 'John' },
    });
    fireEvent.change(screen.getByLabelText(/last name/i), {
      target: { value: 'Doe' },
    });
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'ValidPassword123!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm password/i), {
      target: { value: 'ValidPassword123!' },
    });
    fireEvent.change(screen.getByLabelText(/country preference/i), {
      target: { value: 'UK' },
    });

    const termsCheckbox = screen.getByRole('checkbox', { name: /i accept the/i });
    fireEvent.click(termsCheckbox);

    const submitButton = screen.getByRole('button', { name: /create account/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(submitButton).toBeDisabled();
      expect(screen.getByText(/creating account/i)).toBeInTheDocument();
    });
  });
});
