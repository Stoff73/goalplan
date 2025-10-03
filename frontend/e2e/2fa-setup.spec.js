import { test, expect } from '@playwright/test';

test.describe('2FA Setup Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/setup-2fa');
  });

  test('should show loading state initially', async ({ page }) => {
    await expect(page.getByText(/generating setup code/i)).toBeVisible();
  });

  test('should display QR code and secret', async ({ page, context }) => {
    // Mock 2FA enable endpoint
    await context.route('**/api/v1/auth/2fa/enable', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          qrCode: 'data:image/png;base64,mock-qr-code',
          secret: 'JBSWY3DPEHPK3PXP',
        }),
      });
    });

    await page.waitForLoadState('networkidle');

    await expect(page.getByAltText(/2fa qr code/i)).toBeVisible();
    await expect(page.getByText(/JBSWY3DPEHPK3PXP/i)).toBeVisible();
  });

  test('should require 6-digit verification code', async ({ page, context }) => {
    await context.route('**/api/v1/auth/2fa/enable', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          qrCode: 'data:image/png;base64,mock-qr-code',
          secret: 'JBSWY3DPEHPK3PXP',
        }),
      });
    });

    await page.waitForLoadState('networkidle');

    const codeInput = page.getByLabel(/verification code/i);
    await codeInput.fill('123');

    await page.getByRole('button', { name: /verify & continue/i }).click();

    await expect(page.getByText(/please enter a valid 6-digit code/i)).toBeVisible();
  });

  test('should successfully verify and show backup codes', async ({ page, context }) => {
    // Mock enable 2FA
    await context.route('**/api/v1/auth/2fa/enable', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          qrCode: 'data:image/png;base64,mock-qr-code',
          secret: 'JBSWY3DPEHPK3PXP',
        }),
      });
    });

    // Mock verify setup
    await context.route('**/api/v1/auth/2fa/verify-setup', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          backupCodes: ['CODE1', 'CODE2', 'CODE3', 'CODE4', 'CODE5', 'CODE6', 'CODE7', 'CODE8', 'CODE9', 'CODE10'],
        }),
      });
    });

    await page.waitForLoadState('networkidle');

    await page.getByLabel(/verification code/i).fill('123456');
    await page.getByRole('button', { name: /verify & continue/i }).click();

    await expect(page.getByText(/2fa successfully enabled/i)).toBeVisible();
    await expect(page.getByText(/save your backup codes/i)).toBeVisible();
    await expect(page.getByText(/CODE1/)).toBeVisible();
  });

  test('should handle invalid verification code', async ({ page, context }) => {
    await context.route('**/api/v1/auth/2fa/enable', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          qrCode: 'data:image/png;base64,mock-qr-code',
          secret: 'JBSWY3DPEHPK3PXP',
        }),
      });
    });

    await context.route('**/api/v1/auth/2fa/verify-setup', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Invalid code',
        }),
      });
    });

    await page.waitForLoadState('networkidle');

    await page.getByLabel(/verification code/i).fill('000000');
    await page.getByRole('button', { name: /verify & continue/i }).click();

    await expect(page.getByText(/invalid code/i)).toBeVisible();
  });

  test('should require backup codes download', async ({ page, context }) => {
    await context.route('**/api/v1/auth/2fa/enable', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          qrCode: 'data:image/png;base64,mock-qr-code',
          secret: 'JBSWY3DPEHPK3PXP',
        }),
      });
    });

    await context.route('**/api/v1/auth/2fa/verify-setup', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          backupCodes: ['CODE1', 'CODE2'],
        }),
      });
    });

    await page.waitForLoadState('networkidle');

    await page.getByLabel(/verification code/i).fill('123456');
    await page.getByRole('button', { name: /verify & continue/i }).click();

    await expect(page.getByRole('button', { name: /i've saved my backup codes/i })).toBeDisabled();
  });

  test('should download backup codes', async ({ page, context }) => {
    await context.route('**/api/v1/auth/2fa/enable', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          qrCode: 'data:image/png;base64,mock-qr-code',
          secret: 'JBSWY3DPEHPK3PXP',
        }),
      });
    });

    await context.route('**/api/v1/auth/2fa/verify-setup', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          backupCodes: ['CODE1', 'CODE2'],
        }),
      });
    });

    await page.waitForLoadState('networkidle');

    await page.getByLabel(/verification code/i).fill('123456');
    await page.getByRole('button', { name: /verify & continue/i }).click();

    const downloadButton = page.getByRole('button', { name: /download backup codes/i });
    await expect(downloadButton).toBeVisible();

    const downloadPromise = page.waitForEvent('download');
    await downloadButton.click();

    await expect(page.getByText(/downloaded/i)).toBeVisible();
  });

  test('should show skip button when allowed', async ({ page, context }) => {
    await context.route('**/api/v1/auth/2fa/enable', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          qrCode: 'data:image/png;base64,mock-qr-code',
          secret: 'JBSWY3DPEHPK3PXP',
        }),
      });
    });

    await page.goto('/setup-2fa?allowSkip=true');
    await page.waitForLoadState('networkidle');

    await expect(page.getByRole('button', { name: /skip for now/i })).toBeVisible();
  });
});
