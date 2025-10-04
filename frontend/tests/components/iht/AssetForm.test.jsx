import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AssetForm } from '../../../src/components/iht/AssetForm';
import { authStorage } from '../../../src/utils/auth';

// Mock auth storage
jest.mock('../../../src/utils/auth', () => ({
  authStorage: {
    getAccessToken: jest.fn(() => 'mock-token'),
  },
}));

// Mock fetch
global.fetch = jest.fn();

describe('AssetForm Component', () => {
  const mockOnClose = jest.fn();
  const mockOnSave = jest.fn();

  const mockAsset = {
    id: 'asset-1',
    assetType: 'PROPERTY',
    assetCategory: 'RESIDENTIAL_PROPERTY',
    description: 'Main residence',
    location: 'UK',
    currentValue: 350000,
    currency: 'GBP',
    valuationDate: '2024-10-01',
    ownership: {
      type: 'SOLE',
      userPercentage: 100,
    },
    ukIhtApplicable: true,
    saEstateDutyApplicable: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders add asset form with empty fields', () => {
    render(<AssetForm onClose={mockOnClose} onSave={mockOnSave} />);

    expect(screen.getByText(/Add Asset/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Asset Type/i)).toHaveValue('');
    expect(screen.getByLabelText(/Description/i)).toHaveValue('');
    expect(screen.getByLabelText(/Current Value/i)).toHaveValue(null);
  });

  it('renders edit asset form with populated fields', () => {
    render(<AssetForm asset={mockAsset} onClose={mockOnClose} onSave={mockOnSave} />);

    expect(screen.getByText(/Edit Asset/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Asset Type/i)).toHaveValue('PROPERTY');
    expect(screen.getByLabelText(/Description/i)).toHaveValue('Main residence');
    expect(screen.getByLabelText(/Current Value/i)).toHaveValue(350000);
  });

  it('validates required fields on submit', async () => {
    render(<AssetForm onClose={mockOnClose} onSave={mockOnSave} />);

    const submitButton = screen.getByText(/Add Asset/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Asset type is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Description is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Value must be greater than zero/i)).toBeInTheDocument();
    });

    expect(fetch).not.toHaveBeenCalled();
  });

  it('submits form with valid data for new asset', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: 'new-asset-id', ...mockAsset }),
    });

    render(<AssetForm onClose={mockOnClose} onSave={mockOnSave} />);

    // Fill in form
    fireEvent.change(screen.getByLabelText(/Asset Type/i), { target: { value: 'PROPERTY' } });
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'Main residence' } });
    fireEvent.change(screen.getByLabelText(/Current Value/i), { target: { value: '350000' } });
    fireEvent.change(screen.getByLabelText(/Valuation Date/i), { target: { value: '2024-10-01' } });

    const submitButton = screen.getByText(/Add Asset/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        '/api/v1/iht/assets',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            Authorization: 'Bearer mock-token',
          }),
          body: expect.stringContaining('"assetType":"PROPERTY"'),
        })
      );
    });

    expect(mockOnSave).toHaveBeenCalled();
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('submits form with valid data for editing asset', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockAsset),
    });

    render(<AssetForm asset={mockAsset} onClose={mockOnClose} onSave={mockOnSave} />);

    // Edit description
    const descriptionInput = screen.getByLabelText(/Description/i);
    fireEvent.change(descriptionInput, { target: { value: 'Updated residence' } });

    const submitButton = screen.getByText(/Update Asset/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        '/api/v1/iht/assets/asset-1',
        expect.objectContaining({
          method: 'PUT',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    expect(mockOnSave).toHaveBeenCalled();
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('displays ownership percentage field when not sole ownership', () => {
    render(<AssetForm onClose={mockOnClose} onSave={mockOnSave} />);

    // Initially hidden for sole ownership
    expect(screen.queryByLabelText(/Your Ownership Percentage/i)).not.toBeInTheDocument();

    // Change to joint ownership
    fireEvent.change(screen.getByLabelText(/Ownership Structure/i), {
      target: { value: 'JOINT_TENANTS' },
    });

    expect(screen.getByLabelText(/Your Ownership Percentage/i)).toBeInTheDocument();
  });

  it('validates ownership percentage between 0 and 100', async () => {
    render(<AssetForm onClose={mockOnClose} onSave={mockOnSave} />);

    // Set ownership to joint
    fireEvent.change(screen.getByLabelText(/Ownership Structure/i), {
      target: { value: 'JOINT_TENANTS' },
    });

    // Fill other required fields
    fireEvent.change(screen.getByLabelText(/Asset Type/i), { target: { value: 'PROPERTY' } });
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'Test' } });
    fireEvent.change(screen.getByLabelText(/Current Value/i), { target: { value: '100000' } });

    // Set invalid percentage
    fireEvent.change(screen.getByLabelText(/Your Ownership Percentage/i), {
      target: { value: '150' },
    });

    const submitButton = screen.getByText(/Add Asset/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Percentage must be between 0 and 100/i)).toBeInTheDocument();
    });
  });

  it('handles API error on submit', async () => {
    window.alert = jest.fn();

    fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ detail: 'Asset creation failed' }),
    });

    render(<AssetForm onClose={mockOnClose} onSave={mockOnSave} />);

    // Fill valid data
    fireEvent.change(screen.getByLabelText(/Asset Type/i), { target: { value: 'PROPERTY' } });
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'Test' } });
    fireEvent.change(screen.getByLabelText(/Current Value/i), { target: { value: '100000' } });

    const submitButton = screen.getByText(/Add Asset/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Asset creation failed');
    });

    expect(mockOnSave).not.toHaveBeenCalled();
    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('closes modal on cancel button click', () => {
    render(<AssetForm onClose={mockOnClose} onSave={mockOnSave} />);

    const cancelButton = screen.getByText(/Cancel/i);
    fireEvent.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('closes modal on overlay click', () => {
    render(<AssetForm onClose={mockOnClose} onSave={mockOnSave} />);

    const overlay = screen.getByText(/Add Asset/i).closest('div').parentElement;
    fireEvent.click(overlay);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('does not close modal on content click', () => {
    render(<AssetForm onClose={mockOnClose} onSave={mockOnSave} />);

    const content = screen.getByText(/Add Asset/i).closest('div');
    fireEvent.click(content);

    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('displays all currency options', () => {
    render(<AssetForm onClose={mockOnClose} onSave={mockOnSave} />);

    const currencySelect = screen.getByLabelText(/Currency/i);

    expect(currencySelect).toContainHTML('<option value="GBP">GBP (£)</option>');
    expect(currencySelect).toContainHTML('<option value="ZAR">ZAR (R)</option>');
    expect(currencySelect).toContainHTML('<option value="USD">USD ($)</option>');
    expect(currencySelect).toContainHTML('<option value="EUR">EUR (€)</option>');
  });

  it('displays tax treatment checkboxes', () => {
    render(<AssetForm onClose={mockOnClose} onSave={mockOnSave} />);

    expect(screen.getByText(/Include in UK Inheritance Tax calculation/i)).toBeInTheDocument();
    expect(screen.getByText(/Include in SA Estate Duty calculation/i)).toBeInTheDocument();
  });

  it('clears field error when field is edited', async () => {
    render(<AssetForm onClose={mockOnClose} onSave={mockOnSave} />);

    // Submit to trigger validation
    const submitButton = screen.getByText(/Add Asset/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Description is required/i)).toBeInTheDocument();
    });

    // Edit the field
    fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'Test' } });

    expect(screen.queryByText(/Description is required/i)).not.toBeInTheDocument();
  });
});
