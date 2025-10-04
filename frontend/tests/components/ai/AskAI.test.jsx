import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AskAI } from '../../../src/components/ai/AskAI';

// Mock authStorage
jest.mock('../../../src/utils/auth', () => ({
  authStorage: {
    getAccessToken: jest.fn(() => 'mock-token'),
    clear: jest.fn(),
  },
}));

// Mock fetch
global.fetch = jest.fn();

describe('AskAI', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders question input and example questions', () => {
    render(<AskAI />);

    expect(screen.getByPlaceholderText(/Type your financial question here/i)).toBeInTheDocument();
    expect(screen.getByText('Ask Your AI Financial Advisor')).toBeInTheDocument();
    expect(screen.getByText(/Or try one of these example questions/i)).toBeInTheDocument();
  });

  test('displays character count', () => {
    render(<AskAI />);

    const textarea = screen.getByPlaceholderText(/Type your financial question here/i);

    fireEvent.change(textarea, { target: { value: 'Test question' } });

    expect(screen.getByText(/13 \/ 500 characters/i)).toBeInTheDocument();
  });

  test('submit button is disabled when question is too short', () => {
    render(<AskAI />);

    const submitButton = screen.getByRole('button', { name: /Get AI Advice/i });
    expect(submitButton).toBeDisabled();

    const textarea = screen.getByPlaceholderText(/Type your financial question here/i);
    fireEvent.change(textarea, { target: { value: 'Short' } }); // Less than 10 chars

    expect(submitButton).toBeDisabled();
  });

  test('submit button is enabled when question meets minimum length', () => {
    render(<AskAI />);

    const textarea = screen.getByPlaceholderText(/Type your financial question here/i);
    fireEvent.change(textarea, { target: { value: 'This is a valid question with enough characters' } });

    const submitButton = screen.getByRole('button', { name: /Get AI Advice/i });
    expect(submitButton).not.toBeDisabled();
  });

  test('clicking example question populates textarea', () => {
    render(<AskAI />);

    const exampleButton = screen.getByText(/How much should I contribute to my pension/i);
    fireEvent.click(exampleButton);

    const textarea = screen.getByPlaceholderText(/Type your financial question here/i);
    expect(textarea.value).toContain('How much should I contribute to my pension');
  });

  test('successfully submits question and displays response', async () => {
    const mockResponse = {
      advice: 'You should increase your pension contributions by £200/month.',
      recommendations: ['Increase contributions', 'Review allowance'],
      confidence: 'high',
      sources: ['HMRC guidelines'],
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    render(<AskAI />);

    const textarea = screen.getByPlaceholderText(/Type your financial question here/i);
    fireEvent.change(textarea, { target: { value: 'How much should I save for retirement?' } });

    const submitButton = screen.getByRole('button', { name: /Get AI Advice/i });
    fireEvent.click(submitButton);

    // Should show loading state
    await waitFor(() => {
      expect(screen.getByText(/Getting AI Advice/i)).toBeInTheDocument();
    });

    // Should display response
    await waitFor(() => {
      expect(screen.getByText(mockResponse.advice)).toBeInTheDocument();
    });
  });

  test('handles rate limit error (429)', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 429,
      json: async () => ({ detail: 'Rate limit exceeded' }),
    });

    render(<AskAI />);

    const textarea = screen.getByPlaceholderText(/Type your financial question here/i);
    fireEvent.change(textarea, { target: { value: 'Test question that will trigger rate limit' } });

    const submitButton = screen.getByRole('button', { name: /Get AI Advice/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Rate limit exceeded/i)).toBeInTheDocument();
    });
  });

  test('handles generic error', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ detail: 'Internal server error' }),
    });

    render(<AskAI />);

    const textarea = screen.getByPlaceholderText(/Type your financial question here/i);
    fireEvent.change(textarea, { target: { value: 'Test question that will fail' } });

    const submitButton = screen.getByRole('button', { name: /Get AI Advice/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Internal server error/i)).toBeInTheDocument();
    });
  });

  test('enforces maximum character limit', () => {
    render(<AskAI />);

    const textarea = screen.getByPlaceholderText(/Type your financial question here/i);

    // Try to set text longer than 500 chars
    const text500 = 'a'.repeat(500);
    fireEvent.change(textarea, { target: { value: text500 } });

    // Should show 500/500 for exactly 500 chars
    expect(screen.getByText('500 / 500 characters')).toBeInTheDocument();

    // Try to add more - component should prevent it
    const text600 = 'a'.repeat(600);
    fireEvent.change(textarea, { target: { value: text600 } });

    // Should still be at 500 (component prevents going over in handleQuestionChange)
    expect(screen.getByText('500 / 500 characters')).toBeInTheDocument();
  });
});
