import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ChangePasswordSection } from '../../src/components/profile/ChangePasswordSection';
import { profileEndpoints } from '../../src/utils/api';

// Mock the API module
jest.mock('../../src/utils/api', () => ({
  profileEndpoints: {
    changePassword: jest.fn(),
  },
}));

describe('ChangePasswordSection', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the change password form', () => {
    render(<ChangePasswordSection />);

    expect(screen.getByLabelText('Current password')).toBeInTheDocument();
    expect(screen.getByLabelText('New password')).toBeInTheDocument();
    expect(screen.getByLabelText('Confirm new password')).toBeInTheDocument();
    expect(screen.getByText('Change password')).toBeInTheDocument();
  });

  it('displays password requirements', () => {
    render(<ChangePasswordSection />);

    expect(screen.getByText('Password requirements:')).toBeInTheDocument();
    expect(screen.getByText(/At least 12 characters long/)).toBeInTheDocument();
    expect(screen.getByText(/At least 1 uppercase letter/)).toBeInTheDocument();
    expect(screen.getByText(/At least 1 lowercase letter/)).toBeInTheDocument();
    expect(screen.getByText(/At least 1 number/)).toBeInTheDocument();
    expect(screen.getByText(/At least 1 special character/)).toBeInTheDocument();
  });

  it('shows password strength indicator', () => {
    render(<ChangePasswordSection />);

    const newPasswordInput = screen.getByLabelText('New password');

    // Weak password
    fireEvent.change(newPasswordInput, { target: { name: 'newPassword', value: 'weak' } });
    expect(screen.getByText('Weak')).toBeInTheDocument();

    // Medium password
    fireEvent.change(newPasswordInput, { target: { name: 'newPassword', value: 'Medium123!' } });
    expect(screen.getByText('Medium')).toBeInTheDocument();

    // Strong password
    fireEvent.change(newPasswordInput, {
      target: { name: 'newPassword', value: 'VeryStrong123!@#' },
    });
    expect(screen.getByText('Strong')).toBeInTheDocument();
  });

  it('toggles password visibility', () => {
    render(<ChangePasswordSection />);

    const currentPasswordInput = screen.getByLabelText('Current password');
    expect(currentPasswordInput.type).toBe('password');

    const showButtons = screen.getAllByText('Show');
    fireEvent.click(showButtons[0]);

    expect(currentPasswordInput.type).toBe('text');

    const hideButtons = screen.getAllByText('Hide');
    fireEvent.click(hideButtons[0]);

    expect(currentPasswordInput.type).toBe('password');
  });

  it('validates that current password is required', async () => {
    render(<ChangePasswordSection />);

    const newPasswordInput = screen.getByLabelText('New password');
    const confirmPasswordInput = screen.getByLabelText('Confirm new password');

    fireEvent.change(newPasswordInput, { target: { name: 'newPassword', value: 'NewPassword123!' } });
    fireEvent.change(confirmPasswordInput, {
      target: { name: 'confirmPassword', value: 'NewPassword123!' },
    });

    fireEvent.click(screen.getByText('Change password'));

    await waitFor(() => {
      expect(screen.getByText('Current password is required')).toBeInTheDocument();
    });

    expect(profileEndpoints.changePassword).not.toHaveBeenCalled();
  });

  it('validates password strength requirements', async () => {
    render(<ChangePasswordSection />);

    const currentPasswordInput = screen.getByLabelText('Current password');
    const newPasswordInput = screen.getByLabelText('New password');
    const confirmPasswordInput = screen.getByLabelText('Confirm new password');

    fireEvent.change(currentPasswordInput, { target: { name: 'currentPassword', value: 'OldPassword123!' } });
    fireEvent.change(newPasswordInput, { target: { name: 'newPassword', value: 'weak' } });
    fireEvent.change(confirmPasswordInput, { target: { name: 'confirmPassword', value: 'weak' } });

    fireEvent.click(screen.getByText('Change password'));

    await waitFor(() => {
      expect(screen.getByText(/Password must be at least 12 characters/)).toBeInTheDocument();
    });

    expect(profileEndpoints.changePassword).not.toHaveBeenCalled();
  });

  it('validates that passwords match', async () => {
    render(<ChangePasswordSection />);

    const currentPasswordInput = screen.getByLabelText('Current password');
    const newPasswordInput = screen.getByLabelText('New password');
    const confirmPasswordInput = screen.getByLabelText('Confirm new password');

    fireEvent.change(currentPasswordInput, { target: { name: 'currentPassword', value: 'OldPassword123!' } });
    fireEvent.change(newPasswordInput, { target: { name: 'newPassword', value: 'NewPassword123!' } });
    fireEvent.change(confirmPasswordInput, {
      target: { name: 'confirmPassword', value: 'DifferentPassword123!' },
    });

    fireEvent.click(screen.getByText('Change password'));

    await waitFor(() => {
      expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
    });

    expect(profileEndpoints.changePassword).not.toHaveBeenCalled();
  });

  it('validates that new password is different from current', async () => {
    render(<ChangePasswordSection />);

    const currentPasswordInput = screen.getByLabelText('Current password');
    const newPasswordInput = screen.getByLabelText('New password');
    const confirmPasswordInput = screen.getByLabelText('Confirm new password');

    fireEvent.change(currentPasswordInput, { target: { name: 'currentPassword', value: 'SamePassword123!' } });
    fireEvent.change(newPasswordInput, { target: { name: 'newPassword', value: 'SamePassword123!' } });
    fireEvent.change(confirmPasswordInput, {
      target: { name: 'confirmPassword', value: 'SamePassword123!' },
    });

    fireEvent.click(screen.getByText('Change password'));

    await waitFor(() => {
      expect(screen.getByText('New password must be different from current password')).toBeInTheDocument();
    });

    expect(profileEndpoints.changePassword).not.toHaveBeenCalled();
  });

  it('successfully changes password with valid data', async () => {
    profileEndpoints.changePassword.mockResolvedValue({ success: true });

    render(<ChangePasswordSection />);

    const currentPasswordInput = screen.getByLabelText('Current password');
    const newPasswordInput = screen.getByLabelText('New password');
    const confirmPasswordInput = screen.getByLabelText('Confirm new password');

    fireEvent.change(currentPasswordInput, { target: { name: 'currentPassword', value: 'OldPassword123!' } });
    fireEvent.change(newPasswordInput, { target: { name: 'newPassword', value: 'NewPassword123!' } });
    fireEvent.change(confirmPasswordInput, {
      target: { name: 'confirmPassword', value: 'NewPassword123!' },
    });

    fireEvent.click(screen.getByText('Change password'));

    await waitFor(() => {
      expect(profileEndpoints.changePassword).toHaveBeenCalledWith('OldPassword123!', 'NewPassword123!');
    });

    await waitFor(() => {
      expect(
        screen.getByText(/Your password has been changed successfully/)
      ).toBeInTheDocument();
    });

    // Form should be reset
    expect(currentPasswordInput.value).toBe('');
    expect(newPasswordInput.value).toBe('');
    expect(confirmPasswordInput.value).toBe('');
  });

  it('handles API errors gracefully', async () => {
    profileEndpoints.changePassword.mockRejectedValue(new Error('Incorrect current password'));

    render(<ChangePasswordSection />);

    const currentPasswordInput = screen.getByLabelText('Current password');
    const newPasswordInput = screen.getByLabelText('New password');
    const confirmPasswordInput = screen.getByLabelText('Confirm new password');

    fireEvent.change(currentPasswordInput, { target: { name: 'currentPassword', value: 'WrongPassword!' } });
    fireEvent.change(newPasswordInput, { target: { name: 'newPassword', value: 'NewPassword123!' } });
    fireEvent.change(confirmPasswordInput, {
      target: { name: 'confirmPassword', value: 'NewPassword123!' },
    });

    fireEvent.click(screen.getByText('Change password'));

    await waitFor(() => {
      expect(screen.getByText(/Incorrect current password/)).toBeInTheDocument();
    });
  });

  it('shows loading state while changing password', async () => {
    profileEndpoints.changePassword.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ success: true }), 100))
    );

    render(<ChangePasswordSection />);

    const currentPasswordInput = screen.getByLabelText('Current password');
    const newPasswordInput = screen.getByLabelText('New password');
    const confirmPasswordInput = screen.getByLabelText('Confirm new password');

    fireEvent.change(currentPasswordInput, { target: { name: 'currentPassword', value: 'OldPassword123!' } });
    fireEvent.change(newPasswordInput, { target: { name: 'newPassword', value: 'NewPassword123!' } });
    fireEvent.change(confirmPasswordInput, {
      target: { name: 'confirmPassword', value: 'NewPassword123!' },
    });

    fireEvent.click(screen.getByText('Change password'));

    expect(screen.getByText('Changing password...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText('Changing password...')).not.toBeInTheDocument();
    });
  });

  it('displays warning about logging out other devices', async () => {
    profileEndpoints.changePassword.mockResolvedValue({ success: true });

    render(<ChangePasswordSection />);

    const currentPasswordInput = screen.getByLabelText('Current password');
    const newPasswordInput = screen.getByLabelText('New password');
    const confirmPasswordInput = screen.getByLabelText('Confirm new password');

    fireEvent.change(currentPasswordInput, { target: { name: 'currentPassword', value: 'OldPassword123!' } });
    fireEvent.change(newPasswordInput, { target: { name: 'newPassword', value: 'NewPassword123!' } });
    fireEvent.change(confirmPasswordInput, {
      target: { name: 'confirmPassword', value: 'NewPassword123!' },
    });

    fireEvent.click(screen.getByText('Change password'));

    await waitFor(() => {
      expect(screen.getByText(/All other devices will be logged out/)).toBeInTheDocument();
    });
  });
});
