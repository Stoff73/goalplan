import { test, expect } from '@playwright/test';

test.describe('Logout Flow', () => {
  test.beforeEach(async ({ page, context }) => {
    // Mock logged-in state
    await context.addCookies([
      {
        name: 'goalplan_access_token',
        value: 'mock-token',
        domain: 'localhost',
        path: '/',
      },
    ]);

    // Set localStorage
    await page.goto('/dashboard');
    await page.evaluate(() => {
      localStorage.setItem('goalplan_access_token', 'mock-token');
      localStorage.setItem('goalplan_refresh_token', 'mock-refresh');
      localStorage.setItem('goalplan_user', JSON.stringify({ id: '123', email: 'test@example.com' }));
    });
  });

  test('should have logout button in navigation', async ({ page }) => {
    await expect(page.getByRole('button', { name: /logout/i })).toBeVisible();
  });

  test('should successfully logout and clear tokens', async ({ page, context }) => {
    // Mock logout endpoint
    await context.route('**/api/v1/auth/logout', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
        }),
      });
    });

    await page.getByRole('button', { name: /logout/i }).click();

    // Should redirect to login
    await expect(page).toHaveURL(/.*login.*/);

    // Verify tokens cleared
    const tokens = await page.evaluate(() => ({
      accessToken: localStorage.getItem('goalplan_access_token'),
      refreshToken: localStorage.getItem('goalplan_refresh_token'),
      user: localStorage.getItem('goalplan_user'),
    }));

    expect(tokens.accessToken).toBeNull();
    expect(tokens.refreshToken).toBeNull();
    expect(tokens.user).toBeNull();
  });

  test('should clear tokens even if API fails', async ({ page, context }) => {
    // Mock logout failure
    await context.route('**/api/v1/auth/logout', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Server error',
        }),
      });
    });

    await page.getByRole('button', { name: /logout/i }).click();

    // Should still redirect and clear tokens
    await expect(page).toHaveURL(/.*login.*/);

    const tokens = await page.evaluate(() => ({
      accessToken: localStorage.getItem('goalplan_access_token'),
      refreshToken: localStorage.getItem('goalplan_refresh_token'),
    }));

    expect(tokens.accessToken).toBeNull();
    expect(tokens.refreshToken).toBeNull();
  });

  test('should show logging out state', async ({ page, context }) => {
    // Mock slow logout
    await context.route('**/api/v1/auth/logout', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    });

    await page.getByRole('button', { name: /logout/i }).click();

    const logoutButton = page.getByRole('button', { name: /logging out/i });
    await expect(logoutButton).toBeDisabled();
  });

  test('should not allow access to protected routes after logout', async ({ page, context }) => {
    await context.route('**/api/v1/auth/logout', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    });

    await page.getByRole('button', { name: /logout/i }).click();
    await expect(page).toHaveURL(/.*login.*/);

    // Try to navigate to dashboard
    await page.goto('/dashboard');

    // Should redirect back to login
    await expect(page).toHaveURL(/.*login.*/);
  });
});
