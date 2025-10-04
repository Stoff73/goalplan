import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AdviceCard } from '../../../src/components/ai/AdviceCard';

describe('AdviceCard', () => {
  const mockProps = {
    advice: 'Based on your current pension contributions, you should increase by £200/month.',
    recommendations: [
      'Increase pension contributions by £200/month',
      'Review your annual allowance usage',
      'Consider salary sacrifice for tax efficiency',
    ],
    confidence: 'high',
    sources: ['UK Pension Annual Allowance Rules', 'Your current contribution data'],
  };

  test('renders advice text correctly', () => {
    render(<AdviceCard {...mockProps} />);

    expect(screen.getByText(mockProps.advice)).toBeInTheDocument();
  });

  test('displays confidence badge', () => {
    render(<AdviceCard {...mockProps} />);

    expect(screen.getByText('HIGH CONFIDENCE')).toBeInTheDocument();
  });

  test('renders recommendations list', () => {
    render(<AdviceCard {...mockProps} />);

    expect(screen.getByText('What You Should Do Next')).toBeInTheDocument();
    mockProps.recommendations.forEach((rec) => {
      expect(screen.getByText(rec)).toBeInTheDocument();
    });
  });

  test('sources section is collapsible', () => {
    render(<AdviceCard {...mockProps} />);

    const sourcesButton = screen.getByText('Sources & References');
    expect(sourcesButton).toBeInTheDocument();

    // Sources should not be visible initially
    expect(screen.queryByText(mockProps.sources[0])).not.toBeInTheDocument();

    // Click to expand
    fireEvent.click(sourcesButton);

    // Sources should now be visible
    expect(screen.getByText(mockProps.sources[0])).toBeInTheDocument();
    expect(screen.getByText(mockProps.sources[1])).toBeInTheDocument();

    // Click to collapse
    fireEvent.click(sourcesButton);

    // Sources should be hidden again
    expect(screen.queryByText(mockProps.sources[0])).not.toBeInTheDocument();
  });

  test('always displays disclaimer', () => {
    render(<AdviceCard {...mockProps} />);

    expect(
      screen.getByText(/This is AI-generated advice for informational purposes only/i)
    ).toBeInTheDocument();
  });

  test('renders loading state correctly', () => {
    render(<AdviceCard loading={true} />);

    // Should not render actual content in loading state
    expect(screen.queryByText(mockProps.advice)).not.toBeInTheDocument();
    expect(screen.queryByText('What You Should Do Next')).not.toBeInTheDocument();
  });

  test('handles missing recommendations gracefully', () => {
    render(<AdviceCard advice={mockProps.advice} confidence={mockProps.confidence} />);

    expect(screen.getByText(mockProps.advice)).toBeInTheDocument();
    expect(screen.queryByText('What You Should Do Next')).not.toBeInTheDocument();
  });

  test('handles missing sources gracefully', () => {
    render(
      <AdviceCard
        advice={mockProps.advice}
        recommendations={mockProps.recommendations}
        confidence={mockProps.confidence}
      />
    );

    expect(screen.queryByText('Sources & References')).not.toBeInTheDocument();
  });

  test('confidence badge uses correct styling for different levels', () => {
    const { rerender } = render(<AdviceCard {...mockProps} confidence="high" />);
    expect(screen.getByText('HIGH CONFIDENCE')).toBeInTheDocument();

    rerender(<AdviceCard {...mockProps} confidence="medium" />);
    expect(screen.getByText('MEDIUM CONFIDENCE')).toBeInTheDocument();

    rerender(<AdviceCard {...mockProps} confidence="low" />);
    expect(screen.getByText('LOW CONFIDENCE')).toBeInTheDocument();
  });
});
