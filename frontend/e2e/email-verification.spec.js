import { test, expect } from '@playwright/test';

test.describe('Email Verification Flow', () => {
  test('should show verifying state', async ({ page }) => {
    await page.goto('/verify-email?token=test-token');

    await expect(page.getByText(/verifying your email/i)).toBeVisible();
  });

  test('should show success message on valid token', async ({ page, context }) => {
    // Mock successful verification
    await context.route('**/api/v1/auth/verify-email?token=valid-token', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: 'Email verified successfully',
        }),
      });
    });

    await page.goto('/verify-email?token=valid-token');

    await expect(page.getByText(/success/i)).toBeVisible();
    await expect(page.getByText(/email verified successfully/i)).toBeVisible();
  });

  test('should show countdown timer', async ({ page, context }) => {
    await context.route('**/api/v1/auth/verify-email?token=valid-token', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: 'Email verified successfully',
        }),
      });
    });

    await page.goto('/verify-email?token=valid-token');

    await expect(page.getByText(/redirecting to login in 3 seconds/i)).toBeVisible();
  });

  test('should show error message on invalid token', async ({ page, context }) => {
    // Mock verification failure
    await context.route('**/api/v1/auth/verify-email?token=invalid-token', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Invalid or expired token',
        }),
      });
    });

    await page.goto('/verify-email?token=invalid-token');

    await expect(page.getByText(/verification failed/i)).toBeVisible();
    await expect(page.getByText(/invalid or expired token/i)).toBeVisible();
  });

  test('should show error when no token provided', async ({ page }) => {
    await page.goto('/verify-email');

    await expect(page.getByText(/no token provided/i)).toBeVisible();
  });

  test('should have resend verification button on error', async ({ page, context }) => {
    await context.route('**/api/v1/auth/verify-email?token=expired-token', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Token expired',
        }),
      });
    });

    await page.goto('/verify-email?token=expired-token');

    await expect(page.getByRole('button', { name: /request new verification link/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /back to login/i })).toBeVisible();
  });

  test('should redirect to login on success', async ({ page, context }) => {
    await context.route('**/api/v1/auth/verify-email?token=valid-token', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: 'Email verified successfully',
        }),
      });
    });

    await page.goto('/verify-email?token=valid-token');

    // Click "Go to Login Now" button
    const loginButton = page.getByRole('button', { name: /go to login now/i });
    await expect(loginButton).toBeVisible();
    await loginButton.click();

    await expect(page).toHaveURL(/.*login.*/);
  });
});
