import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { TwoFactorSetup } from '../../src/components/auth/TwoFactorSetup';
import { authEndpoints } from '../../src/utils/api';

// Mock the API
jest.mock('../../src/utils/api', () => ({
  authEndpoints: {
    enable2FA: jest.fn(),
    verify2FASetup: jest.fn(),
  },
}));

// Mock URL.createObjectURL
global.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
global.URL.revokeObjectURL = jest.fn();

describe('TwoFactorSetup', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('shows loading state initially', () => {
    render(<TwoFactorSetup />);

    expect(screen.getByText(/generating setup code/i)).toBeInTheDocument();
  });

  test('displays QR code and secret after initialization', async () => {
    const mockResponse = {
      qrCode: 'data:image/png;base64,mock-qr-code',
      secret: 'JBSWY3DPEHPK3PXP',
    };

    authEndpoints.enable2FA.mockResolvedValueOnce(mockResponse);

    render(<TwoFactorSetup />);

    await waitFor(() => {
      expect(screen.getByAltText(/2fa qr code/i)).toBeInTheDocument();
      expect(screen.getByText(/JBSWY3DPEHPK3PXP/i)).toBeInTheDocument();
    });
  });

  test('validates verification code length', async () => {
    const mockResponse = {
      qrCode: 'data:image/png;base64,mock-qr-code',
      secret: 'JBSWY3DPEHPK3PXP',
    };

    authEndpoints.enable2FA.mockResolvedValueOnce(mockResponse);

    render(<TwoFactorSetup />);

    await waitFor(() => {
      expect(screen.getByLabelText(/verification code/i)).toBeInTheDocument();
    });

    const codeInput = screen.getByLabelText(/verification code/i);
    const submitButton = screen.getByRole('button', { name: /verify & continue/i });

    fireEvent.change(codeInput, { target: { value: '123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/please enter a valid 6-digit code/i)).toBeInTheDocument();
    });
  });

  test('successfully verifies code and shows backup codes', async () => {
    const mockSetupResponse = {
      qrCode: 'data:image/png;base64,mock-qr-code',
      secret: 'JBSWY3DPEHPK3PXP',
    };

    const mockVerifyResponse = {
      backupCodes: ['CODE1', 'CODE2', 'CODE3', 'CODE4', 'CODE5', 'CODE6', 'CODE7', 'CODE8', 'CODE9', 'CODE10'],
    };

    authEndpoints.enable2FA.mockResolvedValueOnce(mockSetupResponse);
    authEndpoints.verify2FASetup.mockResolvedValueOnce(mockVerifyResponse);

    render(<TwoFactorSetup />);

    await waitFor(() => {
      expect(screen.getByLabelText(/verification code/i)).toBeInTheDocument();
    });

    const codeInput = screen.getByLabelText(/verification code/i);
    fireEvent.change(codeInput, { target: { value: '123456' } });

    const submitButton = screen.getByRole('button', { name: /verify & continue/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(authEndpoints.verify2FASetup).toHaveBeenCalledWith('123456');
      expect(screen.getByText(/2fa successfully enabled/i)).toBeInTheDocument();
      expect(screen.getByText(/save your backup codes/i)).toBeInTheDocument();
    });

    // Verify all backup codes are displayed
    mockVerifyResponse.backupCodes.forEach((code) => {
      expect(screen.getByText(code)).toBeInTheDocument();
    });
  });

  test('handles verification error', async () => {
    const mockSetupResponse = {
      qrCode: 'data:image/png;base64,mock-qr-code',
      secret: 'JBSWY3DPEHPK3PXP',
    };

    authEndpoints.enable2FA.mockResolvedValueOnce(mockSetupResponse);
    authEndpoints.verify2FASetup.mockRejectedValueOnce(new Error('Invalid code'));

    render(<TwoFactorSetup />);

    await waitFor(() => {
      expect(screen.getByLabelText(/verification code/i)).toBeInTheDocument();
    });

    const codeInput = screen.getByLabelText(/verification code/i);
    fireEvent.change(codeInput, { target: { value: '123456' } });

    const submitButton = screen.getByRole('button', { name: /verify & continue/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid code/i)).toBeInTheDocument();
    });
  });

  test('downloads backup codes', async () => {
    const mockSetupResponse = {
      qrCode: 'data:image/png;base64,mock-qr-code',
      secret: 'JBSWY3DPEHPK3PXP',
    };

    const mockVerifyResponse = {
      backupCodes: ['CODE1', 'CODE2'],
    };

    authEndpoints.enable2FA.mockResolvedValueOnce(mockSetupResponse);
    authEndpoints.verify2FASetup.mockResolvedValueOnce(mockVerifyResponse);

    // Mock document methods
    const mockClick = jest.fn();
    const mockAppendChild = jest.fn();
    const mockRemoveChild = jest.fn();
    document.createElement = jest.fn(() => ({
      click: mockClick,
    }));
    document.body.appendChild = mockAppendChild;
    document.body.removeChild = mockRemoveChild;

    render(<TwoFactorSetup />);

    await waitFor(() => {
      expect(screen.getByLabelText(/verification code/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/verification code/i), {
      target: { value: '123456' },
    });
    fireEvent.click(screen.getByRole('button', { name: /verify & continue/i }));

    await waitFor(() => {
      expect(screen.getByText(/download backup codes/i)).toBeInTheDocument();
    });

    const downloadButton = screen.getByRole('button', { name: /download backup codes/i });
    fireEvent.click(downloadButton);

    await waitFor(() => {
      expect(screen.getByText(/downloaded/i)).toBeInTheDocument();
    });
  });

  test('requires backup codes download before completion', async () => {
    const mockSetupResponse = {
      qrCode: 'data:image/png;base64,mock-qr-code',
      secret: 'JBSWY3DPEHPK3PXP',
    };

    const mockVerifyResponse = {
      backupCodes: ['CODE1', 'CODE2'],
    };

    authEndpoints.enable2FA.mockResolvedValueOnce(mockSetupResponse);
    authEndpoints.verify2FASetup.mockResolvedValueOnce(mockVerifyResponse);

    render(<TwoFactorSetup />);

    await waitFor(() => {
      expect(screen.getByLabelText(/verification code/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/verification code/i), {
      target: { value: '123456' },
    });
    fireEvent.click(screen.getByRole('button', { name: /verify & continue/i }));

    await waitFor(() => {
      const completeButton = screen.getByRole('button', { name: /i've saved my backup codes/i });
      expect(completeButton).toBeDisabled();
    });

    // Try to complete without downloading
    const completeButton = screen.getByRole('button', { name: /i've saved my backup codes/i });
    fireEvent.click(completeButton);

    await waitFor(() => {
      expect(screen.getByText(/you must download your backup codes/i)).toBeInTheDocument();
    });
  });

  test('calls onSuccess after completing setup', async () => {
    const mockSetupResponse = {
      qrCode: 'data:image/png;base64,mock-qr-code',
      secret: 'JBSWY3DPEHPK3PXP',
    };

    const mockVerifyResponse = {
      backupCodes: ['CODE1', 'CODE2'],
    };

    authEndpoints.enable2FA.mockResolvedValueOnce(mockSetupResponse);
    authEndpoints.verify2FASetup.mockResolvedValueOnce(mockVerifyResponse);

    const onSuccess = jest.fn();
    render(<TwoFactorSetup onSuccess={onSuccess} />);

    await waitFor(() => {
      expect(screen.getByLabelText(/verification code/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/verification code/i), {
      target: { value: '123456' },
    });
    fireEvent.click(screen.getByRole('button', { name: /verify & continue/i }));

    await waitFor(() => {
      expect(screen.getByText(/download backup codes/i)).toBeInTheDocument();
    });

    // Download codes
    fireEvent.click(screen.getByRole('button', { name: /download backup codes/i }));

    await waitFor(() => {
      const completeButton = screen.getByRole('button', { name: /i've saved my backup codes/i });
      expect(completeButton).not.toBeDisabled();
    });

    // Complete setup
    fireEvent.click(screen.getByRole('button', { name: /i've saved my backup codes/i }));

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  test('shows skip button when allowSkip is true', async () => {
    const mockResponse = {
      qrCode: 'data:image/png;base64,mock-qr-code',
      secret: 'JBSWY3DPEHPK3PXP',
    };

    authEndpoints.enable2FA.mockResolvedValueOnce(mockResponse);

    const onSkip = jest.fn();
    render(<TwoFactorSetup allowSkip={true} onSkip={onSkip} />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /skip for now/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /skip for now/i }));

    expect(onSkip).toHaveBeenCalled();
  });

  test('disables button while verifying', async () => {
    const mockSetupResponse = {
      qrCode: 'data:image/png;base64,mock-qr-code',
      secret: 'JBSWY3DPEHPK3PXP',
    };

    authEndpoints.enable2FA.mockResolvedValueOnce(mockSetupResponse);
    authEndpoints.verify2FASetup.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(<TwoFactorSetup />);

    await waitFor(() => {
      expect(screen.getByLabelText(/verification code/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/verification code/i), {
      target: { value: '123456' },
    });

    const submitButton = screen.getByRole('button', { name: /verify & continue/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(submitButton).toBeDisabled();
      expect(screen.getByText(/verifying/i)).toBeInTheDocument();
    });
  });
});
