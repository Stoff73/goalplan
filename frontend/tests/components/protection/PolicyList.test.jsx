import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { PolicyList } from '../../../src/components/protection/PolicyList';

describe('PolicyList Component', () => {
  const mockPolicies = [
    {
      id: '1',
      provider: 'Legal & General',
      policyType: 'TERM',
      coverAmount: 500000,
      currency: 'GBP',
      premiumAmount: 50,
      premiumFrequency: 'MONTHLY',
      annualPremium: 600,
      providerCountry: 'UK',
      status: 'ACTIVE',
      writtenInTrust: true,
      beneficiaries: [
        { name: 'Jane Doe', relationship: 'SPOUSE' },
        { name: 'John Doe Jr', relationship: 'CHILD' },
      ],
      criticalIllnessRider: true,
      startDate: '2020-01-01',
    },
    {
      id: '2',
      provider: 'Aviva',
      policyType: 'WHOLE_OF_LIFE',
      coverAmount: 250000,
      currency: 'GBP',
      premiumAmount: 100,
      premiumFrequency: 'MONTHLY',
      annualPremium: 1200,
      providerCountry: 'UK',
      status: 'ACTIVE',
      writtenInTrust: false,
      beneficiaries: [{ name: 'Jane Doe', relationship: 'SPOUSE' }],
      criticalIllnessRider: false,
      startDate: '2019-06-15',
    },
    {
      id: '3',
      provider: 'Old Mutual',
      policyType: 'TERM',
      coverAmount: 1000000,
      currency: 'ZAR',
      premiumAmount: 500,
      premiumFrequency: 'MONTHLY',
      annualPremium: 6000,
      providerCountry: 'ZA',
      status: 'LAPSED',
      writtenInTrust: false,
      beneficiaries: [],
      criticalIllnessRider: false,
      startDate: '2018-03-01',
    },
  ];

  const mockHandlers = {
    onEdit: jest.fn(),
    onDelete: jest.fn(),
    onView: jest.fn(),
    onAdd: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    test('renders loading state', () => {
      render(<PolicyList policies={[]} loading={true} {...mockHandlers} />);
      expect(screen.getByText(/loading life assurance policies/i)).toBeInTheDocument();
    });

    test('renders empty state when no policies', () => {
      render(<PolicyList policies={[]} loading={false} {...mockHandlers} />);
      expect(screen.getByText(/no policies yet/i)).toBeInTheDocument();
      expect(screen.getByText(/start protecting your family/i)).toBeInTheDocument();
    });

    test('renders policies when data is provided', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      expect(screen.getByText('Legal & General')).toBeInTheDocument();
      expect(screen.getByText('Aviva')).toBeInTheDocument();
      // Old Mutual might be filtered if we're only showing ACTIVE by default, so check it exists in data
      expect(screen.getByText('Old Mutual')).toBeInTheDocument();
    });

    test('displays policy cover amounts correctly', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      expect(screen.getByText('£500,000')).toBeInTheDocument();
      expect(screen.getByText('£250,000')).toBeInTheDocument();
      expect(screen.getByText('R1,000,000')).toBeInTheDocument();
    });

    test('displays status badges correctly', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      const activeStatuses = screen.getAllByText('Active');
      expect(activeStatuses.length).toBeGreaterThan(0);
      expect(screen.getByText('Lapsed')).toBeInTheDocument();
    });

    test('displays IHT badge for UK policies in trust', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      expect(screen.getByText(/IHT: In Trust/i)).toBeInTheDocument();
    });

    test('displays IHT warning for UK policies not in trust', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      expect(screen.getByText(/IHT: Not in Trust/i)).toBeInTheDocument();
    });

    test('displays beneficiary count', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      expect(screen.getByText('2 beneficiaries')).toBeInTheDocument();
      expect(screen.getByText('1 beneficiary')).toBeInTheDocument();
    });

    test('displays critical illness indicator when present', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      expect(screen.getByText('Critical Illness')).toBeInTheDocument();
    });
  });

  describe('Filtering', () => {
    test('renders filter controls when policies exist', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      // Verify filter labels are present
      expect(screen.getByText('Filter by Provider')).toBeInTheDocument();
      expect(screen.getByText('Filter by Type')).toBeInTheDocument();
      expect(screen.getByText('Filter by Country')).toBeInTheDocument();
      expect(screen.getByText('Filter by Status')).toBeInTheDocument();
      expect(screen.getByText('Sort By')).toBeInTheDocument();
    });

    test('does not render filters when no policies', () => {
      render(<PolicyList policies={[]} loading={false} {...mockHandlers} />);

      // Filters should not be shown in empty state
      expect(screen.queryByText('Filter by Provider')).not.toBeInTheDocument();
    });
  });

  describe('Sorting', () => {
    test('renders sort control', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      // Sort control should be present
      expect(screen.getByText('Sort By')).toBeInTheDocument();
    });

    test('displays all policies when rendered', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      // All policies should be visible (default sort)
      expect(screen.getByText('Aviva')).toBeInTheDocument();
      expect(screen.getByText('Legal & General')).toBeInTheDocument();
      expect(screen.getByText('Old Mutual')).toBeInTheDocument();
    });
  });

  describe('Actions', () => {
    test('calls onView when View Details button is clicked', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      const viewButtons = screen.getAllByRole('button', { name: /view details/i });
      fireEvent.click(viewButtons[0]);

      expect(mockHandlers.onView).toHaveBeenCalledTimes(1);
      // First policy in sorted order (provider_asc) is Aviva
      expect(mockHandlers.onView).toHaveBeenCalledWith(expect.objectContaining({
        provider: expect.any(String)
      }));
    });

    test('calls onEdit when Edit button is clicked', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      const editButtons = screen.getAllByRole('button', { name: /^edit$/i });
      fireEvent.click(editButtons[0]);

      expect(mockHandlers.onEdit).toHaveBeenCalledTimes(1);
      expect(mockHandlers.onEdit).toHaveBeenCalledWith(expect.objectContaining({
        provider: expect.any(String)
      }));
    });

    test('calls onDelete when Delete button is clicked and confirmed', () => {
      // Mock window.confirm to return true
      global.confirm = jest.fn(() => true);

      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      fireEvent.click(deleteButtons[0]);

      expect(global.confirm).toHaveBeenCalledWith(
        expect.stringContaining('Are you sure')
      );
      expect(mockHandlers.onDelete).toHaveBeenCalledTimes(1);
      expect(mockHandlers.onDelete).toHaveBeenCalledWith(expect.any(String));
    });

    test('does not call onDelete when Delete is cancelled', () => {
      // Mock window.confirm to return false
      global.confirm = jest.fn(() => false);

      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      const deleteButtons = screen.getAllByText('Delete');
      fireEvent.click(deleteButtons[0]);

      expect(global.confirm).toHaveBeenCalled();
      expect(mockHandlers.onDelete).not.toHaveBeenCalled();
    });

    test('calls onAdd when Add Policy button is clicked in empty state', () => {
      render(<PolicyList policies={[]} loading={false} {...mockHandlers} />);

      const addButton = screen.getByRole('button', { name: /add your first policy/i });
      fireEvent.click(addButton);

      expect(mockHandlers.onAdd).toHaveBeenCalledTimes(1);
    });

    test('calls onAdd when Add Policy button is clicked in header', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      const addButton = screen.getByText('+ Add Policy');
      fireEvent.click(addButton);

      expect(mockHandlers.onAdd).toHaveBeenCalledTimes(1);
    });

    test('calls onView when policy card is clicked', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      // Find a policy card by its provider name and click it
      const policyCard = screen.getByText('Legal & General').closest('div[style*="cursor: pointer"]');
      fireEvent.click(policyCard);

      expect(mockHandlers.onView).toHaveBeenCalledWith(mockPolicies[0]);
    });
  });

  describe('Accessibility', () => {
    test('renders filter labels correctly', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      expect(screen.getByText('Filter by Provider')).toBeInTheDocument();
      expect(screen.getByText('Filter by Type')).toBeInTheDocument();
      expect(screen.getByText('Filter by Country')).toBeInTheDocument();
      expect(screen.getByText('Filter by Status')).toBeInTheDocument();
      expect(screen.getByText('Sort By')).toBeInTheDocument();
    });

    test('buttons have appropriate text', () => {
      render(<PolicyList policies={mockPolicies} loading={false} {...mockHandlers} />);

      expect(screen.getAllByText('View Details').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Edit').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Delete').length).toBeGreaterThan(0);
    });
  });

  describe('Edge Cases', () => {
    test('handles policies with missing optional fields', () => {
      const minimalPolicy = {
        id: '4',
        provider: 'Minimal Provider',
        policyType: 'TERM',
        coverAmount: 100000,
        currency: 'GBP',
        premiumAmount: 20,
        premiumFrequency: 'MONTHLY',
        providerCountry: 'UK',
        status: 'ACTIVE',
      };

      render(<PolicyList policies={[minimalPolicy]} loading={false} {...mockHandlers} />);

      expect(screen.getByText('Minimal Provider')).toBeInTheDocument();
      expect(screen.getByText('£100,000')).toBeInTheDocument();
    });

    test('handles empty beneficiaries array', () => {
      const policyNoBeneficiaries = {
        ...mockPolicies[0],
        beneficiaries: [],
      };

      render(<PolicyList policies={[policyNoBeneficiaries]} loading={false} {...mockHandlers} />);

      // Should not show beneficiary count when none exist
      expect(screen.queryByText(/beneficiary|beneficiaries/i)).not.toBeInTheDocument();
    });

    test('handles different currency codes', () => {
      const usdPolicy = {
        ...mockPolicies[0],
        id: '5',
        currency: 'USD',
        coverAmount: 300000,
      };

      render(<PolicyList policies={[usdPolicy]} loading={false} {...mockHandlers} />);

      expect(screen.getByText('$300,000')).toBeInTheDocument();
    });
  });
});
