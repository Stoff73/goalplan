import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import { DeleteAccountSection } from '../../src/components/profile/DeleteAccountSection';
import * as api from '../../src/utils/api';
import * as auth from '../../src/utils/auth';

// Mock the API module
jest.mock('../../src/utils/api', () => ({
  profileEndpoints: {
    deleteAccount: jest.fn(),
  },
}));

// Mock auth storage
jest.mock('../../src/utils/auth', () => ({
  authStorage: {
    clear: jest.fn(),
  },
}));

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', async () => {
  const actual = await jest.requireActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock window.alert
const mockAlert = jest.fn();
global.alert = mockAlert;

describe('DeleteAccountSection', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the delete account section with warning', () => {
    render(
      <MemoryRouter>
        <DeleteAccountSection />
      </MemoryRouter>
    );

    expect(screen.getByText('Delete your account')).toBeInTheDocument();
    expect(screen.getByText(/This will permanently delete your account/)).toBeInTheDocument();
    expect(screen.getByText('Warning: This will delete:')).toBeInTheDocument();
  });

  it('displays list of data that will be deleted', () => {
    render(
      <MemoryRouter>
        <DeleteAccountSection />
      </MemoryRouter>
    );

    expect(screen.getByText(/All your financial data/)).toBeInTheDocument();
    expect(screen.getByText(/Tax records and calculations/)).toBeInTheDocument();
    expect(screen.getByText(/Investment and retirement information/)).toBeInTheDocument();
    expect(screen.getByText(/All saved documents and reports/)).toBeInTheDocument();
    expect(screen.getByText(/Your profile and preferences/)).toBeInTheDocument();
  });

  it('displays 30-day grace period notice', () => {
    render(
      <MemoryRouter>
        <DeleteAccountSection />
      </MemoryRouter>
    );

    expect(screen.getByText('30-day grace period:')).toBeInTheDocument();
    expect(
      screen.getByText(/you can contact support to cancel the deletion/)
    ).toBeInTheDocument();
  });

  it('shows data export checkbox option', () => {
    render(
      <MemoryRouter>
        <DeleteAccountSection />
      </MemoryRouter>
    );

    const checkbox = screen.getByLabelText(/Download a copy of your data before deletion/);
    expect(checkbox).toBeInTheDocument();
    expect(checkbox).not.toBeChecked();
  });

  it('validates that password is required', async () => {
    render(
      <MemoryRouter>
        <DeleteAccountSection />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText('Delete my account'));

    await waitFor(() => {
      expect(screen.getByText('Please enter your password to continue')).toBeInTheDocument();
    });

    expect(api.profileEndpoints.deleteAccount).not.toHaveBeenCalled();
  });

  it('shows confirmation modal when delete button is clicked with valid password', async () => {
    render(
      <MemoryRouter>
        <DeleteAccountSection />
      </MemoryRouter>
    );

    const passwordInput = screen.getByLabelText('Confirm your password');
    fireEvent.change(passwordInput, { target: { name: 'password', value: 'Password123!' } });

    fireEvent.click(screen.getByText('Delete my account'));

    await waitFor(() => {
      expect(screen.getByText('Are you absolutely sure?')).toBeInTheDocument();
    });

    expect(
      screen.getByText(/This will delete all your financial data, tax records/)
    ).toBeInTheDocument();
  });

  it('closes confirmation modal when Cancel is clicked', async () => {
    render(
      <MemoryRouter>
        <DeleteAccountSection />
      </MemoryRouter>
    );

    const passwordInput = screen.getByLabelText('Confirm your password');
    fireEvent.change(passwordInput, { target: { name: 'password', value: 'Password123!' } });

    fireEvent.click(screen.getByText('Delete my account'));

    await waitFor(() => {
      expect(screen.getByText('Are you absolutely sure?')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Cancel'));

    await waitFor(() => {
      expect(screen.queryByText('Are you absolutely sure?')).not.toBeInTheDocument();
    });
  });

  it('successfully deletes account without data export', async () => {
    api.profileEndpoints.deleteAccount.mockResolvedValue({ success: true, deletionDate: '2025-11-01' });

    render(
      <MemoryRouter>
        <DeleteAccountSection />
      </MemoryRouter>
    );

    const passwordInput = screen.getByLabelText('Confirm your password');
    fireEvent.change(passwordInput, { target: { name: 'password', value: 'Password123!' } });

    fireEvent.click(screen.getByText('Delete my account'));

    await waitFor(() => {
      expect(screen.getByText('Are you absolutely sure?')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Yes, delete my account'));

    await waitFor(() => {
      expect(api.profileEndpoints.deleteAccount).toHaveBeenCalledWith('Password123!', false);
    });

    expect(auth.authStorage.clear).toHaveBeenCalled();
    expect(mockAlert).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  it('successfully deletes account with data export', async () => {
    api.profileEndpoints.deleteAccount.mockResolvedValue({ success: true, deletionDate: '2025-11-01' });

    render(
      <MemoryRouter>
        <DeleteAccountSection />
      </MemoryRouter>
    );

    const exportCheckbox = screen.getByLabelText(/Download a copy of your data before deletion/);
    fireEvent.click(exportCheckbox);

    const passwordInput = screen.getByLabelText('Confirm your password');
    fireEvent.change(passwordInput, { target: { name: 'password', value: 'Password123!' } });

    fireEvent.click(screen.getByText('Delete my account'));

    await waitFor(() => {
      expect(screen.getByText('Are you absolutely sure?')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Yes, delete my account'));

    await waitFor(() => {
      expect(api.profileEndpoints.deleteAccount).toHaveBeenCalledWith('Password123!', true);
    });

    expect(auth.authStorage.clear).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  it('handles API errors gracefully', async () => {
    api.profileEndpoints.deleteAccount.mockRejectedValue(new Error('Incorrect password'));

    render(
      <MemoryRouter>
        <DeleteAccountSection />
      </MemoryRouter>
    );

    const passwordInput = screen.getByLabelText('Confirm your password');
    fireEvent.change(passwordInput, { target: { name: 'password', value: 'WrongPassword!' } });

    fireEvent.click(screen.getByText('Delete my account'));

    await waitFor(() => {
      expect(screen.getByText('Are you absolutely sure?')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Yes, delete my account'));

    await waitFor(() => {
      expect(screen.getByText(/Incorrect password/)).toBeInTheDocument();
    });

    // Modal should be closed
    expect(screen.queryByText('Are you absolutely sure?')).not.toBeInTheDocument();

    // Should not navigate or clear auth
    expect(auth.authStorage.clear).not.toHaveBeenCalled();
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('shows loading state while deleting account', async () => {
    api.profileEndpoints.deleteAccount.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ success: true }), 100))
    );

    render(
      <MemoryRouter>
        <DeleteAccountSection />
      </MemoryRouter>
    );

    const passwordInput = screen.getByLabelText('Confirm your password');
    fireEvent.change(passwordInput, { target: { name: 'password', value: 'Password123!' } });

    fireEvent.click(screen.getByText('Delete my account'));

    await waitFor(() => {
      expect(screen.getByText('Are you absolutely sure?')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Yes, delete my account'));

    expect(screen.getByText('Deleting account...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText('Deleting account...')).not.toBeInTheDocument();
    });
  });

  it('closes modal when clicking outside', async () => {
    render(
      <MemoryRouter>
        <DeleteAccountSection />
      </MemoryRouter>
    );

    const passwordInput = screen.getByLabelText('Confirm your password');
    fireEvent.change(passwordInput, { target: { name: 'password', value: 'Password123!' } });

    fireEvent.click(screen.getByText('Delete my account'));

    await waitFor(() => {
      expect(screen.getByText('Are you absolutely sure?')).toBeInTheDocument();
    });

    // Click the modal overlay (backdrop)
    const modal = screen.getByText('Are you absolutely sure?').closest('div').parentElement;
    fireEvent.click(modal);

    await waitFor(() => {
      expect(screen.queryByText('Are you absolutely sure?')).not.toBeInTheDocument();
    });
  });

  it('displays deletion date in confirmation modal', async () => {
    render(
      <MemoryRouter>
        <DeleteAccountSection />
      </MemoryRouter>
    );

    const passwordInput = screen.getByLabelText('Confirm your password');
    fireEvent.change(passwordInput, { target: { name: 'password', value: 'Password123!' } });

    fireEvent.click(screen.getByText('Delete my account'));

    await waitFor(() => {
      expect(screen.getByText('Are you absolutely sure?')).toBeInTheDocument();
    });

    // Should show the deletion date (30 days from now)
    const deletionDate = new Date();
    deletionDate.setDate(deletionDate.getDate() + 30);
    const monthName = deletionDate.toLocaleDateString('en-GB', { month: 'long' });

    expect(screen.getByText(new RegExp(monthName))).toBeInTheDocument();
  });
});
