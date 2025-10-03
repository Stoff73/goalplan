import { test, expect } from '@playwright/test';

test.describe('Login with 2FA Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should show 2FA prompt when required', async ({ page, context }) => {
    // Mock login response requiring 2FA
    await context.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          requiresTwoFactor: true,
          message: 'Please provide your 2FA code',
        }),
      });
    });

    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/^password$/i).fill('password123');
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page.getByRole('heading', { name: /two-factor authentication/i })).toBeVisible();
    await expect(page.getByLabel(/authentication code/i)).toBeVisible();
  });

  test('should successfully verify 2FA code', async ({ page, context }) => {
    let loginAttempts = 0;

    await context.route('**/api/v1/auth/login', async (route) => {
      loginAttempts++;

      if (loginAttempts === 1) {
        // First attempt: require 2FA
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            requiresTwoFactor: true,
          }),
        });
      } else {
        // Second attempt with 2FA code: success
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            accessToken: 'mock-access-token',
            refreshToken: 'mock-refresh-token',
            user: {
              id: '123',
              email: 'test@example.com',
            },
          }),
        });
      }
    });

    // Initial login
    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/^password$/i).fill('password123');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait for 2FA prompt
    await expect(page.getByLabel(/authentication code/i)).toBeVisible();

    // Enter 2FA code
    await page.getByLabel(/authentication code/i).fill('123456');
    await page.getByRole('button', { name: /verify/i }).click();

    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard.*/);
  });

  test('should handle invalid 2FA code', async ({ page, context }) => {
    let loginAttempts = 0;

    await context.route('**/api/v1/auth/login', async (route) => {
      loginAttempts++;

      if (loginAttempts === 1) {
        // First attempt: require 2FA
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            requiresTwoFactor: true,
          }),
        });
      } else {
        // Second attempt with invalid code
        await route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({
            message: 'Invalid or expired 2FA code',
          }),
        });
      }
    });

    // Initial login
    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/^password$/i).fill('password123');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Enter invalid 2FA code
    await page.getByLabel(/authentication code/i).fill('000000');
    await page.getByRole('button', { name: /verify/i }).click();

    await expect(page.getByText(/invalid or expired 2fa code/i)).toBeVisible();
  });

  test('should toggle to backup code input', async ({ page, context }) => {
    // Mock login requiring 2FA
    await context.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          requiresTwoFactor: true,
        }),
      });
    });

    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/^password$/i).fill('password123');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait for 2FA prompt
    await expect(page.getByText(/use backup code/i)).toBeVisible();

    // Click toggle
    await page.getByText(/use backup code/i).click();

    // Should show backup code input
    await expect(page.getByLabel(/backup code/i)).toBeVisible();
    await expect(page.getByText(/use authenticator code instead/i)).toBeVisible();

    // Toggle back
    await page.getByText(/use authenticator code instead/i).click();
    await expect(page.getByLabel(/authentication code/i)).toBeVisible();
  });

  test('should successfully verify with backup code', async ({ page, context }) => {
    let loginAttempts = 0;

    await context.route('**/api/v1/auth/login', async (route) => {
      loginAttempts++;

      if (loginAttempts === 1) {
        // First attempt: require 2FA
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            requiresTwoFactor: true,
          }),
        });
      } else {
        // Second attempt with backup code: success
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            accessToken: 'mock-access-token',
            refreshToken: 'mock-refresh-token',
            user: { id: '123', email: 'test@example.com' },
          }),
        });
      }
    });

    // Initial login
    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/^password$/i).fill('password123');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait for 2FA and toggle to backup code
    await page.getByText(/use backup code/i).click();

    // Enter backup code
    await page.getByLabel(/backup code/i).fill('BACKUP123');
    await page.getByRole('button', { name: /verify/i }).click();

    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard.*/);
  });

  test('should validate 2FA code is 6 digits', async ({ page, context }) => {
    await context.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          requiresTwoFactor: true,
        }),
      });
    });

    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/^password$/i).fill('password123');
    await page.getByRole('button', { name: /sign in/i }).click();

    const codeInput = page.getByLabel(/authentication code/i);
    await codeInput.fill('123');

    await expect(page.getByRole('button', { name: /verify/i })).toBeVisible();
  });
});
