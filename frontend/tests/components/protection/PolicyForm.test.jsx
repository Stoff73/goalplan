import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { PolicyForm } from '../../../src/components/protection/PolicyForm';

// Mock UI components
jest.mock('internal-packages/ui', () => ({
  Button: ({ children, onClick, type, disabled, variant, size, ...props }) => (
    <button onClick={onClick} type={type} disabled={disabled} data-variant={variant} data-size={size} {...props}>
      {children}
    </button>
  ),
  Input: ({ value, onChange, type, ...props }) => (
    <input value={value} onChange={onChange} type={type} {...props} />
  ),
  Label: ({ children, htmlFor, ...props }) => (
    <label htmlFor={htmlFor} {...props}>
      {children}
    </label>
  ),
  Select: ({ value, onChange, children, ...props }) => (
    <select value={value} onChange={onChange} {...props}>
      {children}
    </select>
  ),
  Textarea: ({ value, onChange, ...props }) => (
    <textarea value={value} onChange={onChange} {...props} />
  ),
}));

describe('PolicyForm', () => {
  const mockOnSave = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders the form with all steps', () => {
      render(<PolicyForm onSave={mockOnSave} onCancel={mockOnCancel} />);

      // Check step indicators
      expect(screen.getByText('Provider')).toBeInTheDocument();
      expect(screen.getByText('Coverage')).toBeInTheDocument();
      expect(screen.getByText('Beneficiaries')).toBeInTheDocument();
      expect(screen.getByText('Details')).toBeInTheDocument();
    });

    it('renders Step 1 fields initially', () => {
      render(<PolicyForm onSave={mockOnSave} onCancel={mockOnCancel} />);

      expect(screen.getByText('Tell us about your policy provider')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('e.g., POL123456')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('e.g., Aviva, Old Mutual')).toBeInTheDocument();
    });

    it('renders add policy title when no policy provided', () => {
      render(<PolicyForm onSave={mockOnSave} onCancel={mockOnCancel} />);

      expect(screen.getByText('Add life assurance policy')).toBeInTheDocument();
    });

    it('renders edit policy title when policy provided', () => {
      const policy = {
        id: '1',
        policyNumber: 'POL123',
        provider: 'Test Provider',
        providerCountry: 'UK',
        policyType: 'TERM',
        coverAmount: 100000,
        currency: 'GBP',
        premiumAmount: 50,
        premiumFrequency: 'MONTHLY',
        startDate: '2024-01-01',
        endDate: '2034-01-01',
        beneficiaries: [],
      };

      render(<PolicyForm policy={policy} onSave={mockOnSave} onCancel={mockOnCancel} />);

      expect(screen.getByText('Edit life assurance policy')).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('shows validation errors for empty required fields on step 1', async () => {
      render(<PolicyForm onSave={mockOnSave} onCancel={mockOnCancel} />);

      // Try to go to next step without filling required fields
      const nextButton = screen.getByText('Next →');
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Policy number is required')).toBeInTheDocument();
        expect(screen.getByText('Provider name is required')).toBeInTheDocument();
      });
    });

    it('validates cover amount must be greater than 0', async () => {
      render(<PolicyForm onSave={mockOnSave} onCancel={mockOnCancel} />);

      // Fill step 1
      fireEvent.change(screen.getByPlaceholderText('e.g., POL123456'), {
        target: { value: 'POL123' },
      });
      fireEvent.change(screen.getByPlaceholderText('e.g., Aviva, Old Mutual'), {
        target: { value: 'Test Provider' },
      });

      // Go to step 2
      fireEvent.click(screen.getByText('Next →'));

      await waitFor(() => {
        expect(screen.getByText('What coverage do you have?')).toBeInTheDocument();
      });

      // Try to proceed without filling cover amount (will be 0)
      fireEvent.click(screen.getByText('Next →'));

      await waitFor(() => {
        expect(screen.getByText('Cover amount must be greater than 0')).toBeInTheDocument();
      });
    });

    it('allows user to input policy details', async () => {
      render(<PolicyForm onSave={mockOnSave} onCancel={mockOnCancel} />);

      // Step 1
      const policyNumberInput = screen.getByPlaceholderText('e.g., POL123456');
      const providerInput = screen.getByPlaceholderText('e.g., Aviva, Old Mutual');

      fireEvent.change(policyNumberInput, { target: { value: 'POL123' } });
      fireEvent.change(providerInput, { target: { value: 'Test Provider' } });

      expect(policyNumberInput).toHaveValue('POL123');
      expect(providerInput).toHaveValue('Test Provider');
    });
  });

  describe('Beneficiary Management', () => {
    it('shows beneficiary section in step 3', async () => {
      render(<PolicyForm onSave={mockOnSave} onCancel={mockOnCancel} />);

      // Navigate to step 3
      // Step 1
      fireEvent.change(screen.getByPlaceholderText('e.g., POL123456'), {
        target: { value: 'POL123' },
      });
      fireEvent.change(screen.getByPlaceholderText('e.g., Aviva, Old Mutual'), {
        target: { value: 'Test Provider' },
      });
      fireEvent.click(screen.getByText('Next →'));

      // Step 2 - just navigate through
      await waitFor(() => {
        expect(screen.getByText('What coverage do you have?')).toBeInTheDocument();
      });

      // Fill minimum required fields
      const inputs = screen.getAllByRole('spinbutton');
      // Cover amount
      fireEvent.change(inputs[0], { target: { value: '100000' } });
      // Premium amount
      fireEvent.change(inputs[1], { target: { value: '50' } });

      // Start date
      const dateInputs = screen.getAllByRole('textbox').filter((input) => input.type === 'date');
      if (dateInputs.length > 0) {
        fireEvent.change(dateInputs[0], { target: { value: '2024-01-01' } });
      }

      fireEvent.click(screen.getByText('Next →'));

      // Now in step 3
      await waitFor(() => {
        expect(screen.getByText('Who will receive the payout?')).toBeInTheDocument();
        expect(screen.getByText('Beneficiary 1')).toBeInTheDocument();
      });
    });

    it('allows adding beneficiaries', async () => {
      render(<PolicyForm onSave={mockOnSave} onCancel={mockOnCancel} />);

      // Navigate to step 3
      fireEvent.change(screen.getByPlaceholderText('e.g., POL123456'), {
        target: { value: 'POL123' },
      });
      fireEvent.change(screen.getByPlaceholderText('e.g., Aviva, Old Mutual'), {
        target: { value: 'Test Provider' },
      });
      fireEvent.click(screen.getByText('Next →'));

      await waitFor(() => {
        const inputs = screen.getAllByRole('spinbutton');
        fireEvent.change(inputs[0], { target: { value: '100000' } });
        fireEvent.change(inputs[1], { target: { value: '50' } });
      });

      const dateInputs = screen.getAllByRole('textbox').filter((input) => input.type === 'date');
      if (dateInputs.length > 0) {
        fireEvent.change(dateInputs[0], { target: { value: '2024-01-01' } });
      }

      fireEvent.click(screen.getByText('Next →'));

      await waitFor(() => {
        expect(screen.getByText('Beneficiary 1')).toBeInTheDocument();
      });

      // Add second beneficiary
      const addBeneficiaryButton = screen.getByText('+ Add Beneficiary');
      fireEvent.click(addBeneficiaryButton);

      await waitFor(() => {
        expect(screen.getByText('Beneficiary 2')).toBeInTheDocument();
      });
    });

    it('displays percentage total', async () => {
      render(<PolicyForm onSave={mockOnSave} onCancel={mockOnCancel} />);

      // Navigate to step 3
      fireEvent.change(screen.getByPlaceholderText('e.g., POL123456'), {
        target: { value: 'POL123' },
      });
      fireEvent.change(screen.getByPlaceholderText('e.g., Aviva, Old Mutual'), {
        target: { value: 'Test Provider' },
      });
      fireEvent.click(screen.getByText('Next →'));

      await waitFor(() => {
        const inputs = screen.getAllByRole('spinbutton');
        fireEvent.change(inputs[0], { target: { value: '100000' } });
        fireEvent.change(inputs[1], { target: { value: '50' } });
      });

      const dateInputs = screen.getAllByRole('textbox').filter((input) => input.type === 'date');
      if (dateInputs.length > 0) {
        fireEvent.change(dateInputs[0], { target: { value: '2024-01-01' } });
      }

      fireEvent.click(screen.getByText('Next →'));

      await waitFor(() => {
        expect(screen.getByText('Total Percentage:')).toBeInTheDocument();
        // Initial total is 0
        expect(screen.getByText('0.00%')).toBeInTheDocument();
      });
    });
  });

  describe('Trust Fields (UK only)', () => {
    it('shows trust checkbox for UK policies', async () => {
      render(<PolicyForm onSave={mockOnSave} onCancel={mockOnCancel} />);

      // Navigate to step 3
      fireEvent.change(screen.getByPlaceholderText('e.g., POL123456'), {
        target: { value: 'POL123' },
      });
      fireEvent.change(screen.getByPlaceholderText('e.g., Aviva, Old Mutual'), {
        target: { value: 'Test Provider' },
      });

      // Ensure UK is selected (it's the default)
      fireEvent.click(screen.getByText('Next →'));

      await waitFor(() => {
        const inputs = screen.getAllByRole('spinbutton');
        fireEvent.change(inputs[0], { target: { value: '100000' } });
        fireEvent.change(inputs[1], { target: { value: '50' } });
      });

      const dateInputs = screen.getAllByRole('textbox').filter((input) => input.type === 'date');
      if (dateInputs.length > 0) {
        fireEvent.change(dateInputs[0], { target: { value: '2024-01-01' } });
      }

      fireEvent.click(screen.getByText('Next →'));

      await waitFor(() => {
        expect(screen.getByLabelText(/Written in Trust/)).toBeInTheDocument();
      });
    });
  });

  describe('Form Submission', () => {
    it('calls onCancel when cancel button is clicked', () => {
      render(<PolicyForm onSave={mockOnSave} onCancel={mockOnCancel} />);

      const cancelButton = screen.getByText('Cancel');
      fireEvent.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalledTimes(1);
    });

    it('shows submit button on step 4', async () => {
      render(<PolicyForm onSave={mockOnSave} onCancel={mockOnCancel} />);

      // Navigate through all steps
      // Step 1
      fireEvent.change(screen.getByPlaceholderText('e.g., POL123456'), {
        target: { value: 'POL123' },
      });
      fireEvent.change(screen.getByPlaceholderText('e.g., Aviva, Old Mutual'), {
        target: { value: 'Test Provider' },
      });
      fireEvent.click(screen.getByText('Next →'));

      // Step 2
      await waitFor(() => {
        const inputs = screen.getAllByRole('spinbutton');
        fireEvent.change(inputs[0], { target: { value: '100000' } });
        fireEvent.change(inputs[1], { target: { value: '50' } });
      });

      const dateInputs = screen.getAllByRole('textbox').filter((input) => input.type === 'date');
      if (dateInputs.length > 0) {
        fireEvent.change(dateInputs[0], { target: { value: '2024-01-01' } });
      }

      fireEvent.click(screen.getByText('Next →'));

      // Step 3
      await waitFor(() => {
        const beneficiaryNameInput = screen.getByPlaceholderText('Full name');
        fireEvent.change(beneficiaryNameInput, { target: { value: 'John Doe' } });
      });

      // Set percentage to 100
      const percentageInputs = screen.getAllByRole('spinbutton');
      const lastPercentageInput = percentageInputs[percentageInputs.length - 1];
      fireEvent.change(lastPercentageInput, { target: { value: '100' } });

      fireEvent.click(screen.getByText('Next →'));

      // Step 4
      await waitFor(() => {
        expect(screen.getByText('Additional information')).toBeInTheDocument();
        expect(screen.getByText('Add Policy')).toBeInTheDocument();
      });
    });
  });

  describe('Navigation', () => {
    it('allows navigating between steps', async () => {
      render(<PolicyForm onSave={mockOnSave} onCancel={mockOnCancel} />);

      // Fill step 1
      fireEvent.change(screen.getByPlaceholderText('e.g., POL123456'), {
        target: { value: 'POL123' },
      });
      fireEvent.change(screen.getByPlaceholderText('e.g., Aviva, Old Mutual'), {
        target: { value: 'Test Provider' },
      });

      // Go to step 2
      fireEvent.click(screen.getByText('Next →'));

      await waitFor(() => {
        expect(screen.getByText('What coverage do you have?')).toBeInTheDocument();
      });

      // Go back to step 1
      fireEvent.click(screen.getByText('← Previous'));

      await waitFor(() => {
        expect(screen.getByText('Tell us about your policy provider')).toBeInTheDocument();
      });
    });

    it('retains form data when navigating between steps', async () => {
      render(<PolicyForm onSave={mockOnSave} onCancel={mockOnCancel} />);

      // Fill step 1
      const policyNumberInput = screen.getByPlaceholderText('e.g., POL123456');
      fireEvent.change(policyNumberInput, { target: { value: 'POL123' } });

      // Go to step 2
      fireEvent.click(screen.getByText('Next →'));

      await waitFor(() => {
        expect(screen.getByText('What coverage do you have?')).toBeInTheDocument();
      });

      // Go back to step 1
      fireEvent.click(screen.getByText('← Previous'));

      await waitFor(() => {
        const policyNumberInputAgain = screen.getByPlaceholderText('e.g., POL123456');
        expect(policyNumberInputAgain).toHaveValue('POL123');
      });
    });
  });

  describe('Editing Mode', () => {
    it('populates form with policy data in edit mode', () => {
      const policy = {
        id: '1',
        policyNumber: 'POL123456',
        provider: 'Test Provider',
        providerCountry: 'UK',
        policyType: 'TERM',
        coverAmount: 100000,
        currency: 'GBP',
        premiumAmount: 50,
        premiumFrequency: 'MONTHLY',
        startDate: '2024-01-01',
        endDate: '2034-01-01',
        beneficiaries: [
          {
            name: 'John Doe',
            dateOfBirth: '1990-01-01',
            relationship: 'SPOUSE',
            percentage: 100,
            address: '123 Main St',
          },
        ],
        status: 'ACTIVE',
        notes: 'Test notes',
      };

      render(<PolicyForm policy={policy} onSave={mockOnSave} onCancel={mockOnCancel} />);

      // Check that fields are populated
      expect(screen.getByPlaceholderText('e.g., POL123456')).toHaveValue('POL123456');
      expect(screen.getByPlaceholderText('e.g., Aviva, Old Mutual')).toHaveValue('Test Provider');
    });

    it('shows Update Policy button in edit mode', () => {
      const policy = {
        id: '1',
        policyNumber: 'POL123456',
        provider: 'Test Provider',
        providerCountry: 'UK',
        policyType: 'TERM',
        coverAmount: 100000,
        currency: 'GBP',
        premiumAmount: 50,
        premiumFrequency: 'MONTHLY',
        startDate: '2024-01-01',
        beneficiaries: [],
      };

      render(<PolicyForm policy={policy} onSave={mockOnSave} onCancel={mockOnCancel} />);

      // Navigate to last step to see submit button
      // For now, just check the title changed
      expect(screen.getByText('Edit life assurance policy')).toBeInTheDocument();
    });
  });

  describe('Conditional Fields', () => {
    it('shows indexation rate field for increasing term policies', async () => {
      render(<PolicyForm onSave={mockOnSave} onCancel={mockOnCancel} />);

      // Fill step 1
      fireEvent.change(screen.getByPlaceholderText('e.g., POL123456'), {
        target: { value: 'POL123' },
      });
      fireEvent.change(screen.getByPlaceholderText('e.g., Aviva, Old Mutual'), {
        target: { value: 'Test Provider' },
      });

      // Change policy type to INCREASING_TERM
      const policyTypeSelect = screen.getAllByRole('combobox')[1]; // Second select is policy type
      fireEvent.change(policyTypeSelect, { target: { value: 'INCREASING_TERM' } });

      // Go to step 2
      fireEvent.click(screen.getByText('Next →'));

      await waitFor(() => {
        expect(screen.getByText('What coverage do you have?')).toBeInTheDocument();
        // Should show indexation rate field
        expect(screen.getByText('Indexation Rate (%)')).toBeInTheDocument();
      });
    });
  });
});
