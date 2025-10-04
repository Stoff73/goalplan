import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { GoalDetails } from '../../../src/components/goals/GoalDetails';
import { authStorage } from '../../../src/utils/auth';

jest.mock('../../../src/utils/auth', () => ({
  authStorage: {
    getAccessToken: jest.fn(),
    clear: jest.fn(),
  },
}));

global.fetch = jest.fn();

describe('GoalDetails', () => {
  const mockOnEdit = jest.fn();
  const mockOnDelete = jest.fn();
  const mockOnBack = jest.fn();

  const mockGoal = {
    id: 'goal-1',
    title: 'Emergency Fund',
    goal_type: 'EMERGENCY_FUND',
    description: 'Build 6 months of expenses',
    target_amount: 10000,
    currency: 'GBP',
    current_progress: 7500,
    progress_percentage: 75,
    target_date: '2025-12-31',
    created_at: '2025-01-01',
    priority: 'HIGH',
    required_monthly_contribution: 500,
    on_track: true,
    linked_accounts_count: 1,
    auto_contribution_enabled: true,
  };

  const mockMilestones = [
    {
      id: 'milestone-1',
      target_progress_percentage: 25,
      target_amount: 2500,
      milestone_date: '2025-04-01',
      achieved: true,
      achieved_date: '2025-03-15',
    },
    {
      id: 'milestone-2',
      target_progress_percentage: 50,
      target_amount: 5000,
      milestone_date: '2025-07-01',
      achieved: true,
      achieved_date: '2025-06-20',
    },
    {
      id: 'milestone-3',
      target_progress_percentage: 75,
      target_amount: 7500,
      milestone_date: '2025-10-01',
      achieved: false,
    },
  ];

  const mockRecommendations = [
    {
      priority: 'HIGH',
      title: 'Set up automatic monthly transfer',
      description: 'Automate your savings to ensure consistent progress',
      action: 'Set up standing order',
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    authStorage.getAccessToken.mockReturnValue('mock-token');

    global.fetch.mockImplementation((url) => {
      if (url.includes('/goals/goal-1') && !url.includes('milestones') && !url.includes('recommendations')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockGoal),
        });
      }
      if (url.includes('/milestones')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockMilestones),
        });
      }
      if (url.includes('/recommendations')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockRecommendations),
        });
      }
      return Promise.reject(new Error('Unknown URL'));
    });
  });

  describe('Loading State', () => {
    it('shows loading message while fetching data', () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      expect(screen.getByText('Loading goal details...')).toBeInTheDocument();
    });
  });

  describe('Goal Details Display', () => {
    it('renders goal title and icon', async () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText('Emergency Fund')).toBeInTheDocument();
      });

      expect(screen.getByText('🛡️')).toBeInTheDocument();
    });

    it('displays goal story with narrative approach', async () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText(/You started this goal on/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/£10,000/)).toBeInTheDocument();
      expect(screen.getByText(/£7,500/)).toBeInTheDocument();
    });

    it('shows progress percentage and encouraging message', async () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText(/75%/)).toBeInTheDocument();
      });

      expect(screen.getByText(/excellent progress/i)).toBeInTheDocument();
    });

    it('displays savings plan section', async () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText('Your Savings Plan')).toBeInTheDocument();
      });

      expect(screen.getByText(/£500\/month/)).toBeInTheDocument();
    });

    it('shows on-track indicator when goal is on track', async () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText(/You're on track!/i)).toBeInTheDocument();
      });
    });
  });

  describe('Milestones Timeline', () => {
    it('renders milestones section', async () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText('Milestones')).toBeInTheDocument();
      });
    });

    it('displays achieved milestones with checkmarks', async () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText(/✓.*25% milestone/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/✓.*50% milestone/i)).toBeInTheDocument();
    });

    it('shows achievement dates for completed milestones', async () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText(/Achieved on/i)).toBeInTheDocument();
      });
    });

    it('displays pending milestones without checkmarks', async () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText(/75% milestone/i)).toBeInTheDocument();
      });
    });
  });

  describe('Recommendations', () => {
    it('renders recommendations section with toggle', async () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText('Recommendations')).toBeInTheDocument();
      });

      expect(screen.getByText(/Show recommendations/i)).toBeInTheDocument();
    });

    it('toggles recommendations visibility', async () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText(/Show recommendations/i)).toBeInTheDocument();
      });

      const toggleButton = screen.getByText(/Show recommendations/i);
      fireEvent.click(toggleButton);

      expect(screen.getByText('Set up automatic monthly transfer')).toBeInTheDocument();
      expect(screen.getByText(/Hide recommendations/i)).toBeInTheDocument();
    });
  });

  describe('Action Buttons', () => {
    it('renders all action buttons', async () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText('← Back')).toBeInTheDocument();
      });

      expect(screen.getByText('Edit')).toBeInTheDocument();
      expect(screen.getByText('Delete')).toBeInTheDocument();
    });

    it('calls onBack when clicking Back button', async () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText('← Back')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('← Back'));
      expect(mockOnBack).toHaveBeenCalled();
    });

    it('calls onEdit when clicking Edit button', async () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText('Edit')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Edit'));
      expect(mockOnEdit).toHaveBeenCalledWith(mockGoal);
    });

    it('shows delete confirmation when clicking Delete button', async () => {
      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText('Delete')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Delete'));

      expect(screen.getByText(/Delete this goal?/i)).toBeInTheDocument();
      expect(screen.getByText(/Are you sure you want to delete/i)).toBeInTheDocument();
    });

    it('deletes goal when confirming deletion', async () => {
      global.fetch.mockImplementation((url, options) => {
        if (options?.method === 'DELETE') {
          return Promise.resolve({ ok: true });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockGoal) });
      });

      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText('Delete')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Delete'));

      await waitFor(() => {
        expect(screen.getByText('Yes, Delete Goal')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Yes, Delete Goal'));

      await waitFor(() => {
        expect(mockOnDelete).toHaveBeenCalled();
      });
    });
  });

  describe('Completed Goal', () => {
    it('shows celebration message for completed goal', async () => {
      const completedGoal = { ...mockGoal, progress_percentage: 100, current_progress: 10000 };

      global.fetch.mockImplementation((url) => {
        if (url.includes('/goals/goal-1') && !url.includes('milestones')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(completedGoal),
          });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
      });

      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText(/Congratulations! You've Achieved Your Goal!/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('shows error message when API fails', async () => {
      global.fetch.mockRejectedValueOnce(new Error('API Error'));

      render(<GoalDetails goalId="goal-1" onEdit={mockOnEdit} onDelete={mockOnDelete} onBack={mockOnBack} />);

      await waitFor(() => {
        expect(screen.getByText(/Failed to load goal details/i)).toBeInTheDocument();
      });
    });
  });
});
