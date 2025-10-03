import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { PersonalInformationSection } from '../../src/components/profile/PersonalInformationSection';
import { profileEndpoints } from '../../src/utils/api';

// Mock the API module
jest.mock('../../src/utils/api', () => ({
  profileEndpoints: {
    updateProfile: jest.fn(),
  },
}));

describe('PersonalInformationSection', () => {
  const mockProfile = {
    firstName: 'John',
    lastName: 'Doe',
    phone: '+447700900000',
    dateOfBirth: '1990-01-15',
    addressLine1: '123 Main St',
    addressLine2: 'Apt 4B',
    city: 'London',
    postalCode: 'SW1A 1AA',
    country: 'GB',
    timezone: 'Europe/London',
  };

  const mockOnProfileUpdate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders profile information in view mode by default', () => {
    render(<PersonalInformationSection profile={mockProfile} onProfileUpdate={mockOnProfileUpdate} />);

    expect(screen.getByDisplayValue('John')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Doe')).toBeInTheDocument();
    expect(screen.getByDisplayValue('+447700900000')).toBeInTheDocument();
    expect(screen.getByText('Edit')).toBeInTheDocument();
  });

  it('enters edit mode when Edit button is clicked', () => {
    render(<PersonalInformationSection profile={mockProfile} onProfileUpdate={mockOnProfileUpdate} />);

    const editButton = screen.getByText('Edit');
    fireEvent.click(editButton);

    expect(screen.getByText('Save changes')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.queryByText('Edit')).not.toBeInTheDocument();
  });

  it('allows editing of form fields', () => {
    render(<PersonalInformationSection profile={mockProfile} onProfileUpdate={mockOnProfileUpdate} />);

    // Enter edit mode
    fireEvent.click(screen.getByText('Edit'));

    const firstNameInput = screen.getByLabelText('First name');
    fireEvent.change(firstNameInput, { target: { name: 'firstName', value: 'Jane' } });

    expect(firstNameInput.value).toBe('Jane');
  });

  it('successfully updates profile when valid data is submitted', async () => {
    const updatedProfile = { ...mockProfile, firstName: 'Jane' };
    profileEndpoints.updateProfile.mockResolvedValue(updatedProfile);

    render(<PersonalInformationSection profile={mockProfile} onProfileUpdate={mockOnProfileUpdate} />);

    // Enter edit mode and change first name
    fireEvent.click(screen.getByText('Edit'));
    const firstNameInput = screen.getByLabelText('First name');
    fireEvent.change(firstNameInput, { target: { name: 'firstName', value: 'Jane' } });

    // Save
    fireEvent.click(screen.getByText('Save changes'));

    await waitFor(() => {
      expect(profileEndpoints.updateProfile).toHaveBeenCalledWith(
        expect.objectContaining({
          firstName: 'Jane',
        })
      );
    });

    await waitFor(() => {
      expect(screen.getByText('Your personal information has been updated successfully')).toBeInTheDocument();
    });

    expect(mockOnProfileUpdate).toHaveBeenCalledWith(updatedProfile);
  });

  it('validates phone number format', async () => {
    render(<PersonalInformationSection profile={mockProfile} onProfileUpdate={mockOnProfileUpdate} />);

    fireEvent.click(screen.getByText('Edit'));

    const phoneInput = screen.getByLabelText('Phone number');
    fireEvent.change(phoneInput, { target: { name: 'phone', value: 'invalid-phone' } });

    fireEvent.click(screen.getByText('Save changes'));

    await waitFor(() => {
      expect(
        screen.getByText(/Please enter a valid phone number with country code/)
      ).toBeInTheDocument();
    });

    expect(profileEndpoints.updateProfile).not.toHaveBeenCalled();
  });

  it('validates date of birth (must be 18+)', async () => {
    render(<PersonalInformationSection profile={mockProfile} onProfileUpdate={mockOnProfileUpdate} />);

    fireEvent.click(screen.getByText('Edit'));

    const dobInput = screen.getByLabelText('Date of birth');
    const today = new Date();
    const recentDate = new Date(today.getFullYear() - 10, 0, 1); // 10 years ago
    const recentDateString = recentDate.toISOString().split('T')[0];

    fireEvent.change(dobInput, { target: { name: 'dateOfBirth', value: recentDateString } });

    fireEvent.click(screen.getByText('Save changes'));

    await waitFor(() => {
      expect(screen.getByText('You must be at least 18 years old')).toBeInTheDocument();
    });

    expect(profileEndpoints.updateProfile).not.toHaveBeenCalled();
  });

  it('handles API errors gracefully', async () => {
    profileEndpoints.updateProfile.mockRejectedValue(new Error('Network error'));

    render(<PersonalInformationSection profile={mockProfile} onProfileUpdate={mockOnProfileUpdate} />);

    fireEvent.click(screen.getByText('Edit'));

    const firstNameInput = screen.getByLabelText('First name');
    fireEvent.change(firstNameInput, { target: { name: 'firstName', value: 'Jane' } });

    fireEvent.click(screen.getByText('Save changes'));

    await waitFor(() => {
      expect(screen.getByText(/Failed to update profile/)).toBeInTheDocument();
    });
  });

  it('cancels editing and resets form when Cancel is clicked', () => {
    render(<PersonalInformationSection profile={mockProfile} onProfileUpdate={mockOnProfileUpdate} />);

    // Enter edit mode
    fireEvent.click(screen.getByText('Edit'));

    // Change a field
    const firstNameInput = screen.getByLabelText('First name');
    fireEvent.change(firstNameInput, { target: { name: 'firstName', value: 'Jane' } });

    // Cancel
    fireEvent.click(screen.getByText('Cancel'));

    // Should be back in view mode with original data
    expect(screen.getByText('Edit')).toBeInTheDocument();
    expect(screen.getByDisplayValue('John')).toBeInTheDocument();
  });

  it('disables inputs when not in edit mode', () => {
    render(<PersonalInformationSection profile={mockProfile} onProfileUpdate={mockOnProfileUpdate} />);

    const firstNameInput = screen.getByLabelText('First name');
    expect(firstNameInput).toBeDisabled();
  });

  it('shows loading state while saving', async () => {
    profileEndpoints.updateProfile.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(mockProfile), 100))
    );

    render(<PersonalInformationSection profile={mockProfile} onProfileUpdate={mockOnProfileUpdate} />);

    fireEvent.click(screen.getByText('Edit'));
    fireEvent.click(screen.getByText('Save changes'));

    expect(screen.getByText('Saving...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText('Saving...')).not.toBeInTheDocument();
    });
  });
});
