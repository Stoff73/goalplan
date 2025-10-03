import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ChangeEmailSection } from '../../src/components/profile/ChangeEmailSection';
import { profileEndpoints } from '../../src/utils/api';

// Mock the API module
jest.mock('../../src/utils/api', () => ({
  profileEndpoints: {
    changeEmail: jest.fn(),
  },
}));

describe('ChangeEmailSection', () => {
  const currentEmail = 'user@example.com';

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the change email form', () => {
    render(<ChangeEmailSection currentEmail={currentEmail} />);

    expect(screen.getByLabelText('Current email address')).toBeInTheDocument();
    expect(screen.getByLabelText('New email address')).toBeInTheDocument();
    expect(screen.getByLabelText('Confirm your password')).toBeInTheDocument();
    expect(screen.getByText('Send verification email')).toBeInTheDocument();
  });

  it('displays current email as read-only', () => {
    render(<ChangeEmailSection currentEmail={currentEmail} />);

    const currentEmailInput = screen.getByLabelText('Current email address');
    expect(currentEmailInput.value).toBe(currentEmail);
    expect(currentEmailInput).toBeDisabled();
  });

  it('displays how email change works', () => {
    render(<ChangeEmailSection currentEmail={currentEmail} />);

    expect(screen.getByText('How email change works:')).toBeInTheDocument();
    expect(screen.getByText(/Enter your new email address and password/)).toBeInTheDocument();
    expect(screen.getByText(/We'll send a verification link to your new email/)).toBeInTheDocument();
  });

  it('validates that new email is required', async () => {
    render(<ChangeEmailSection currentEmail={currentEmail} />);

    const passwordInput = screen.getByLabelText('Confirm your password');
    fireEvent.change(passwordInput, { target: { name: 'password', value: 'Password123!' } });

    fireEvent.click(screen.getByText('Send verification email'));

    await waitFor(() => {
      expect(screen.getByText('Email is required')).toBeInTheDocument();
    });

    expect(profileEndpoints.changeEmail).not.toHaveBeenCalled();
  });

  it('validates email format', async () => {
    render(<ChangeEmailSection currentEmail={currentEmail} />);

    const emailInput = screen.getByLabelText('New email address');
    const passwordInput = screen.getByLabelText('Confirm your password');

    fireEvent.change(emailInput, { target: { name: 'newEmail', value: 'invalid-email' } });
    fireEvent.change(passwordInput, { target: { name: 'password', value: 'Password123!' } });

    fireEvent.click(screen.getByText('Send verification email'));

    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
    });

    expect(profileEndpoints.changeEmail).not.toHaveBeenCalled();
  });

  it('validates that new email is different from current email', async () => {
    render(<ChangeEmailSection currentEmail={currentEmail} />);

    const emailInput = screen.getByLabelText('New email address');
    const passwordInput = screen.getByLabelText('Confirm your password');

    fireEvent.change(emailInput, { target: { name: 'newEmail', value: currentEmail } });
    fireEvent.change(passwordInput, { target: { name: 'password', value: 'Password123!' } });

    fireEvent.click(screen.getByText('Send verification email'));

    await waitFor(() => {
      expect(screen.getByText('New email must be different from current email')).toBeInTheDocument();
    });

    expect(profileEndpoints.changeEmail).not.toHaveBeenCalled();
  });

  it('validates that password is required', async () => {
    render(<ChangeEmailSection currentEmail={currentEmail} />);

    const emailInput = screen.getByLabelText('New email address');
    fireEvent.change(emailInput, { target: { name: 'newEmail', value: 'newemail@example.com' } });

    fireEvent.click(screen.getByText('Send verification email'));

    await waitFor(() => {
      expect(screen.getByText('Password is required to confirm email change')).toBeInTheDocument();
    });

    expect(profileEndpoints.changeEmail).not.toHaveBeenCalled();
  });

  it('successfully sends verification email with valid data', async () => {
    profileEndpoints.changeEmail.mockResolvedValue({ success: true });

    render(<ChangeEmailSection currentEmail={currentEmail} />);

    const emailInput = screen.getByLabelText('New email address');
    const passwordInput = screen.getByLabelText('Confirm your password');

    fireEvent.change(emailInput, { target: { name: 'newEmail', value: 'newemail@example.com' } });
    fireEvent.change(passwordInput, { target: { name: 'password', value: 'Password123!' } });

    fireEvent.click(screen.getByText('Send verification email'));

    await waitFor(() => {
      expect(profileEndpoints.changeEmail).toHaveBeenCalledWith('newemail@example.com', 'Password123!');
    });

    await waitFor(() => {
      expect(
        screen.getByText(/Verification email sent to newemail@example.com/)
      ).toBeInTheDocument();
    });

    // Form should be reset
    expect(emailInput.value).toBe('');
    expect(passwordInput.value).toBe('');
  });

  it('displays important notice after successful submission', async () => {
    profileEndpoints.changeEmail.mockResolvedValue({ success: true });

    render(<ChangeEmailSection currentEmail={currentEmail} />);

    const emailInput = screen.getByLabelText('New email address');
    const passwordInput = screen.getByLabelText('Confirm your password');

    fireEvent.change(emailInput, { target: { name: 'newEmail', value: 'newemail@example.com' } });
    fireEvent.change(passwordInput, { target: { name: 'password', value: 'Password123!' } });

    fireEvent.click(screen.getByText('Send verification email'));

    await waitFor(() => {
      expect(screen.getByText('Important:')).toBeInTheDocument();
      expect(
        screen.getByText(/A notification has been sent to your current email address/)
      ).toBeInTheDocument();
      expect(screen.getByText(/The verification link expires in 24 hours/)).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    profileEndpoints.changeEmail.mockRejectedValue(new Error('Email already in use'));

    render(<ChangeEmailSection currentEmail={currentEmail} />);

    const emailInput = screen.getByLabelText('New email address');
    const passwordInput = screen.getByLabelText('Confirm your password');

    fireEvent.change(emailInput, { target: { name: 'newEmail', value: 'newemail@example.com' } });
    fireEvent.change(passwordInput, { target: { name: 'password', value: 'Password123!' } });

    fireEvent.click(screen.getByText('Send verification email'));

    await waitFor(() => {
      expect(screen.getByText(/Email already in use/)).toBeInTheDocument();
    });
  });

  it('shows loading state while sending verification email', async () => {
    profileEndpoints.changeEmail.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ success: true }), 100))
    );

    render(<ChangeEmailSection currentEmail={currentEmail} />);

    const emailInput = screen.getByLabelText('New email address');
    const passwordInput = screen.getByLabelText('Confirm your password');

    fireEvent.change(emailInput, { target: { name: 'newEmail', value: 'newemail@example.com' } });
    fireEvent.change(passwordInput, { target: { name: 'password', value: 'Password123!' } });

    fireEvent.click(screen.getByText('Send verification email'));

    expect(screen.getByText('Sending verification email...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText('Sending verification email...')).not.toBeInTheDocument();
    });
  });

  it('clears validation errors when user starts typing', async () => {
    render(<ChangeEmailSection currentEmail={currentEmail} />);

    const emailInput = screen.getByLabelText('New email address');

    // Trigger validation error
    fireEvent.change(emailInput, { target: { name: 'newEmail', value: 'invalid' } });
    fireEvent.click(screen.getByText('Send verification email'));

    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
    });

    // Start typing a valid email
    fireEvent.change(emailInput, { target: { name: 'newEmail', value: 'valid@example.com' } });

    // Error should be cleared
    expect(screen.queryByText('Please enter a valid email address')).not.toBeInTheDocument();
  });
});
