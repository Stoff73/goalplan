import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { GoalsDashboard } from '../../../src/components/goals/GoalsDashboard';
import { authStorage } from '../../../src/utils/auth';

// Mock authStorage
jest.mock('../../../src/utils/auth', () => ({
  authStorage: {
    getAccessToken: jest.fn(),
    clear: jest.fn(),
  },
}));

// Mock fetch
global.fetch = jest.fn();

describe('GoalsDashboard', () => {
  const mockOnGoalSelect = jest.fn();
  const mockOnCreateGoal = jest.fn();

  const mockOverview = {
    total_goals: 3,
    total_target_amount: 100000,
    total_current_progress: 45000,
    total_monthly_required: 2500,
    on_track_count: 2,
    needs_attention_count: 1,
  };

  const mockGoals = [
    {
      id: 'goal-1',
      title: 'Emergency Fund',
      goal_type: 'EMERGENCY_FUND',
      target_amount: 10000,
      currency: 'GBP',
      current_progress: 7500,
      progress_percentage: 75,
      target_date: '2025-12-31',
      priority: 'HIGH',
      required_monthly_contribution: 500,
      on_track: true,
      created_at: '2025-01-01',
    },
    {
      id: 'goal-2',
      title: 'House Deposit',
      goal_type: 'HOUSE_PURCHASE',
      target_amount: 50000,
      currency: 'GBP',
      current_progress: 20000,
      progress_percentage: 40,
      target_date: '2026-06-30',
      priority: 'MEDIUM',
      required_monthly_contribution: 1500,
      on_track: true,
      created_at: '2025-01-01',
    },
    {
      id: 'goal-3',
      title: 'Holiday to Japan',
      goal_type: 'HOLIDAY_TRAVEL',
      target_amount: 5000,
      currency: 'GBP',
      current_progress: 500,
      progress_percentage: 10,
      target_date: '2025-09-01',
      priority: 'LOW',
      required_monthly_contribution: 500,
      on_track: false,
      created_at: '2025-01-01',
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    authStorage.getAccessToken.mockReturnValue('mock-token');

    // Setup default successful fetch responses
    global.fetch.mockImplementation((url) => {
      if (url.includes('/overview')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockOverview),
        });
      }
      if (url.includes('/goals?')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockGoals),
        });
      }
      return Promise.reject(new Error('Unknown URL'));
    });
  });

  describe('Loading State', () => {
    it('shows loading message while fetching data', () => {
      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      expect(screen.getByText('Loading your goals...')).toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('shows empty state when no goals exist', async () => {
      global.fetch.mockImplementation((url) => {
        if (url.includes('/overview')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ total_goals: 0 }),
          });
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([]),
        });
      });

      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByText('Start Your Journey')).toBeInTheDocument();
      });

      expect(screen.getByText(/You haven't set any financial goals yet/i)).toBeInTheDocument();
      expect(screen.getByText('Create Your First Goal →')).toBeInTheDocument();
    });

    it('calls onCreateGoal when clicking create first goal button', async () => {
      global.fetch.mockImplementation((url) => {
        if (url.includes('/overview')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ total_goals: 0 }),
          });
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([]),
        });
      });

      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByText('Create Your First Goal →')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Create Your First Goal →'));
      expect(mockOnCreateGoal).toHaveBeenCalled();
    });
  });

  describe('Goals Dashboard with Data', () => {
    it('renders overview narrative section with goal count', async () => {
      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByText(/You're tracking/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/3/)).toBeInTheDocument();
      expect(screen.getByText(/financial goals/i)).toBeInTheDocument();
    });

    it('displays total target amount correctly', async () => {
      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByText(/£100,000/)).toBeInTheDocument();
      });
    });

    it('shows on-track and needs-attention counts', async () => {
      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByText(/2/)).toBeInTheDocument();
      });

      expect(screen.getByText(/on track/i)).toBeInTheDocument();
      expect(screen.getByText(/1/)).toBeInTheDocument();
      expect(screen.getByText(/needs attention/i)).toBeInTheDocument();
    });

    it('renders all goal cards', async () => {
      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByText('Emergency Fund')).toBeInTheDocument();
      });

      expect(screen.getByText('House Deposit')).toBeInTheDocument();
      expect(screen.getByText('Holiday to Japan')).toBeInTheDocument();
    });

    it('shows correct progress percentage for each goal', async () => {
      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByText(/75% of the way/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/40% of the way/i)).toBeInTheDocument();
      expect(screen.getByText(/10% of the way/i)).toBeInTheDocument();
    });

    it('displays goal icons correctly', async () => {
      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByText('🛡️')).toBeInTheDocument(); // Emergency Fund
      });

      expect(screen.getByText('🏠')).toBeInTheDocument(); // House Purchase
      expect(screen.getByText('✈️')).toBeInTheDocument(); // Holiday Travel
    });

    it('calls onGoalSelect when clicking a goal card', async () => {
      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByText('Emergency Fund')).toBeInTheDocument();
      });

      const goalCard = screen.getByText('Emergency Fund').closest('div');
      fireEvent.click(goalCard);

      expect(mockOnGoalSelect).toHaveBeenCalledWith('goal-1');
    });
  });

  describe('Filtering and Sorting', () => {
    it('renders filter dropdowns', async () => {
      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByLabelText(/Filter by type:/i)).toBeInTheDocument();
      });

      expect(screen.getByLabelText(/Status:/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Sort by:/i)).toBeInTheDocument();
    });

    it('updates goals when filter changes', async () => {
      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByLabelText(/Filter by type:/i)).toBeInTheDocument();
      });

      const filterSelect = screen.getByLabelText(/Filter by type:/i);
      fireEvent.change(filterSelect, { target: { value: 'EMERGENCY_FUND' } });

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('goal_type=EMERGENCY_FUND'),
          expect.any(Object)
        );
      });
    });

    it('updates goals when sort changes', async () => {
      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByLabelText(/Sort by:/i)).toBeInTheDocument();
      });

      const sortSelect = screen.getByLabelText(/Sort by:/i);
      fireEvent.change(sortSelect, { target: { value: 'target_date' } });

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('sort_by=target_date'),
          expect.any(Object)
        );
      });
    });
  });

  describe('Error Handling', () => {
    it('shows error message when API fails', async () => {
      global.fetch.mockRejectedValueOnce(new Error('API Error'));

      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByText(/Failed to load goals data/i)).toBeInTheDocument();
      });

      expect(screen.getByText('Try Again')).toBeInTheDocument();
    });

    it('redirects to login on 401 error', async () => {
      delete window.location;
      window.location = { href: '' };

      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(authStorage.clear).toHaveBeenCalled();
        expect(window.location.href).toBe('/login');
      });
    });

    it('retries loading data when clicking Try Again', async () => {
      global.fetch.mockRejectedValueOnce(new Error('API Error'));

      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByText('Try Again')).toBeInTheDocument();
      });

      // Setup successful fetch for retry
      global.fetch.mockImplementation((url) => {
        if (url.includes('/overview')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockOverview),
          });
        }
        if (url.includes('/goals?')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockGoals),
          });
        }
      });

      fireEvent.click(screen.getByText('Try Again'));

      await waitFor(() => {
        expect(screen.getByText('Emergency Fund')).toBeInTheDocument();
      });
    });
  });

  describe('Create Goal Button', () => {
    it('shows Create Goal button when goals exist', async () => {
      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByText('Create Goal +')).toBeInTheDocument();
      });
    });

    it('calls onCreateGoal when clicking Create Goal button', async () => {
      render(<GoalsDashboard onGoalSelect={mockOnGoalSelect} onCreateGoal={mockOnCreateGoal} />);

      await waitFor(() => {
        expect(screen.getByText('Create Goal +')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Create Goal +'));
      expect(mockOnCreateGoal).toHaveBeenCalled();
    });
  });
});
