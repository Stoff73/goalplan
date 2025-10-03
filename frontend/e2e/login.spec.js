import { test, expect } from '@playwright/test';

test.describe('User Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should display login form', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
    await expect(page.getByLabel(/email address/i)).toBeVisible();
    await expect(page.getByLabel(/^password$/i)).toBeVisible();
    await expect(page.getByRole('checkbox', { name: /remember me/i })).toBeVisible();
    await expect(page.getByText(/forgot password/i)).toBeVisible();
  });

  test('should show validation errors', async ({ page }) => {
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page.getByText(/email is required/i)).toBeVisible();
    await expect(page.getByText(/password is required/i)).toBeVisible();
  });

  test('should successfully login with valid credentials', async ({ page, context }) => {
    // Mock successful login
    await context.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          accessToken: 'mock-access-token',
          refreshToken: 'mock-refresh-token',
          user: {
            id: '123',
            email: 'test@example.com',
            firstName: 'John',
            lastName: 'Doe',
          },
        }),
      });
    });

    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/^password$/i).fill('password123');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard.*/);
  });

  test('should handle invalid credentials error', async ({ page, context }) => {
    // Mock 401 error
    await context.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Invalid email or password',
        }),
      });
    });

    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/^password$/i).fill('wrongpassword');
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page.getByText(/invalid email or password/i)).toBeVisible();
  });

  test('should handle account locked error', async ({ page, context }) => {
    // Mock 423 error
    await context.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 423,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Account locked',
        }),
      });
    });

    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/^password$/i).fill('password123');
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page.getByText(/account temporarily locked/i)).toBeVisible();
  });

  test('should handle unverified email error', async ({ page, context }) => {
    // Mock 403 error
    await context.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Email not verified',
        }),
      });
    });

    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/^password$/i).fill('password123');
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page.getByText(/please verify your email address/i)).toBeVisible();
  });

  test('should remember me checkbox work', async ({ page }) => {
    const rememberMeCheckbox = page.getByRole('checkbox', { name: /remember me/i });

    await expect(rememberMeCheckbox).not.toBeChecked();
    await rememberMeCheckbox.check();
    await expect(rememberMeCheckbox).toBeChecked();
  });

  test('should disable submit button while submitting', async ({ page, context }) => {
    // Mock slow API
    await context.route('**/api/v1/auth/login', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          accessToken: 'token',
          refreshToken: 'token',
          user: { id: '123', email: 'test@example.com' },
        }),
      });
    });

    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/^password$/i).fill('password123');
    await page.getByRole('button', { name: /sign in/i }).click();

    const submitButton = page.getByRole('button', { name: /signing in/i });
    await expect(submitButton).toBeDisabled();
  });
});
