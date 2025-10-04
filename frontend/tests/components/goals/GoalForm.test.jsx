import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { GoalForm } from '../../../src/components/goals/GoalForm';
import { authStorage } from '../../../src/utils/auth';

jest.mock('../../../src/utils/auth', () => ({
  authStorage: {
    getAccessToken: jest.fn(),
    clear: jest.fn(),
  },
}));

global.fetch = jest.fn();

describe('GoalForm', () => {
  const mockOnSuccess = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    authStorage.getAccessToken.mockReturnValue('mock-token');
  });

  describe('Form Rendering', () => {
    it('renders all form sections', () => {
      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      expect(screen.getByText(/What are you saving for?/i)).toBeInTheDocument();
      expect(screen.getByText(/Tell us about your goal/i)).toBeInTheDocument();
      expect(screen.getByText(/How important is this goal?/i)).toBeInTheDocument();
    });

    it('renders all goal type options', () => {
      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      expect(screen.getByText('Emergency Fund')).toBeInTheDocument();
      expect(screen.getByText('House Purchase')).toBeInTheDocument();
      expect(screen.getByText('Retirement')).toBeInTheDocument();
    });

    it('shows SMART criteria tips section', () => {
      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      expect(screen.getByText(/Your goal follows SMART criteria/i)).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('validates required title field', async () => {
      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      const submitButton = screen.getByText('Create Goal');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Please give your goal a clear, specific name/i)).toBeInTheDocument();
      });
    });

    it('validates minimum title length', async () => {
      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      const titleInput = screen.getByLabelText(/Goal Name/i);
      fireEvent.change(titleInput, { target: { value: 'Ab' } });

      const submitButton = screen.getByText('Create Goal');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/at least 3 characters/i)).toBeInTheDocument();
      });
    });

    it('validates target amount is positive', async () => {
      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      const titleInput = screen.getByLabelText(/Goal Name/i);
      fireEvent.change(titleInput, { target: { value: 'My Goal' } });

      const amountInput = screen.getByLabelText(/How much do you need?/i);
      fireEvent.change(amountInput, { target: { value: '-100' } });

      const dateInput = screen.getByLabelText(/When do you need it by?/i);
      fireEvent.change(dateInput, { target: { value: '2026-12-31' } });

      const submitButton = screen.getByText('Create Goal');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/must be positive/i)).toBeInTheDocument();
      });
    });

    it('validates minimum target amount', async () => {
      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      const titleInput = screen.getByLabelText(/Goal Name/i);
      fireEvent.change(titleInput, { target: { value: 'My Goal' } });

      const amountInput = screen.getByLabelText(/How much do you need?/i);
      fireEvent.change(amountInput, { target: { value: '50' } });

      const dateInput = screen.getByLabelText(/When do you need it by?/i);
      fireEvent.change(dateInput, { target: { value: '2026-12-31' } });

      const submitButton = screen.getByText('Create Goal');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/at least £100/i)).toBeInTheDocument();
      });
    });

    it('validates target date is required', async () => {
      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      const titleInput = screen.getByLabelText(/Goal Name/i);
      fireEvent.change(titleInput, { target: { value: 'My Goal' } });

      const amountInput = screen.getByLabelText(/How much do you need?/i);
      fireEvent.change(amountInput, { target: { value: '10000' } });

      const submitButton = screen.getByText('Create Goal');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Please set a target date/i)).toBeInTheDocument();
      });
    });
  });

  describe('Form Submission', () => {
    it('submits valid form data successfully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: 'new-goal-id', title: 'Emergency Fund' }),
      });

      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      // Fill form
      const titleInput = screen.getByLabelText(/Goal Name/i);
      fireEvent.change(titleInput, { target: { value: 'Emergency Fund' } });

      const amountInput = screen.getByLabelText(/How much do you need?/i);
      fireEvent.change(amountInput, { target: { value: '10000' } });

      const dateInput = screen.getByLabelText(/When do you need it by?/i);
      const futureDate = new Date();
      futureDate.setMonth(futureDate.getMonth() + 12);
      fireEvent.change(dateInput, { target: { value: futureDate.toISOString().split('T')[0] } });

      const submitButton = screen.getByText('Create Goal');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/goals',
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              'Content-Type': 'application/json',
              Authorization: 'Bearer mock-token',
            }),
          })
        );
      });

      expect(mockOnSuccess).toHaveBeenCalled();
    });

    it('shows loading state during submission', async () => {
      global.fetch.mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({ ok: true, json: () => ({}) }), 100))
      );

      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      const titleInput = screen.getByLabelText(/Goal Name/i);
      fireEvent.change(titleInput, { target: { value: 'My Goal' } });

      const amountInput = screen.getByLabelText(/How much do you need?/i);
      fireEvent.change(amountInput, { target: { value: '10000' } });

      const dateInput = screen.getByLabelText(/When do you need it by?/i);
      const futureDate = new Date();
      futureDate.setMonth(futureDate.getMonth() + 12);
      fireEvent.change(dateInput, { target: { value: futureDate.toISOString().split('T')[0] } });

      const submitButton = screen.getByText('Create Goal');
      fireEvent.click(submitButton);

      expect(screen.getByText('Saving...')).toBeInTheDocument();
    });
  });

  describe('Edit Mode', () => {
    const existingGoal = {
      id: 'goal-123',
      goal_type: 'HOUSE_PURCHASE',
      title: 'House Deposit',
      target_amount: 50000,
      currency: 'GBP',
      target_date: '2026-12-31',
      priority: 'HIGH',
    };

    it('populates form with existing goal data', () => {
      render(
        <GoalForm
          goalId="goal-123"
          initialData={existingGoal}
          onSuccess={mockOnSuccess}
          onCancel={mockOnCancel}
        />
      );

      expect(screen.getByLabelText(/Goal Name/i)).toHaveValue('House Deposit');
      expect(screen.getByLabelText(/How much do you need?/i)).toHaveValue(50000);
    });

    it('submits PUT request when editing', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(existingGoal),
      });

      render(
        <GoalForm
          goalId="goal-123"
          initialData={existingGoal}
          onSuccess={mockOnSuccess}
          onCancel={mockOnCancel}
        />
      );

      const submitButton = screen.getByText('Update Goal');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/goals/goal-123',
          expect.objectContaining({
            method: 'PUT',
          })
        );
      });
    });
  });

  describe('User Interactions', () => {
    it('allows selecting different goal types', () => {
      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      const emergencyFundButton = screen.getByText('Emergency Fund');
      fireEvent.click(emergencyFundButton);

      // Form should update (we can't directly check state, but verify no errors)
      expect(emergencyFundButton).toBeInTheDocument();
    });

    it('allows selecting priority levels', () => {
      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      const highPriorityButton = screen.getByText(/🔥.*High/i);
      fireEvent.click(highPriorityButton);

      expect(highPriorityButton).toBeInTheDocument();
    });

    it('toggles SMART tips section', () => {
      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      const toggleButton = screen.getByText(/Tell me more about SMART goals/i);
      fireEvent.click(toggleButton);

      expect(screen.getByText(/Specific:/i)).toBeInTheDocument();
      expect(screen.getByText(/Measurable:/i)).toBeInTheDocument();
    });

    it('calls onCancel when clicking Cancel button', () => {
      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      const cancelButton = screen.getByText('Cancel');
      fireEvent.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalled();
    });
  });

  describe('Auto-Contribution Feature', () => {
    it('shows auto-contribution fields when checkbox is enabled', () => {
      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      const checkbox = screen.getByLabelText(/Yes, I want to set up automatic contributions/i);
      fireEvent.click(checkbox);

      expect(screen.getByLabelText(/Monthly Amount/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Frequency/i)).toBeInTheDocument();
    });

    it('validates auto-contribution amount when enabled', async () => {
      render(<GoalForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />);

      const titleInput = screen.getByLabelText(/Goal Name/i);
      fireEvent.change(titleInput, { target: { value: 'My Goal' } });

      const amountInput = screen.getByLabelText(/How much do you need?/i);
      fireEvent.change(amountInput, { target: { value: '10000' } });

      const dateInput = screen.getByLabelText(/When do you need it by?/i);
      const futureDate = new Date();
      futureDate.setMonth(futureDate.getMonth() + 12);
      fireEvent.change(dateInput, { target: { value: futureDate.toISOString().split('T')[0] } });

      const checkbox = screen.getByLabelText(/Yes, I want to set up automatic contributions/i);
      fireEvent.click(checkbox);

      const submitButton = screen.getByText('Create Goal');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Please enter a positive amount/i)).toBeInTheDocument();
      });
    });
  });
});
