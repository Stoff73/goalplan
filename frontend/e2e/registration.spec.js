import { test, expect } from '@playwright/test';

test.describe('User Registration Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/register');
  });

  test('should display registration form', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /create your account/i })).toBeVisible();
    await expect(page.getByLabel(/email address/i)).toBeVisible();
    await expect(page.getByLabel(/first name/i)).toBeVisible();
    await expect(page.getByLabel(/last name/i)).toBeVisible();
    await expect(page.getByLabel(/^password$/i)).toBeVisible();
    await expect(page.getByLabel(/confirm password/i)).toBeVisible();
    await expect(page.getByLabel(/country preference/i)).toBeVisible();
  });

  test('should show validation errors for empty form', async ({ page }) => {
    await page.getByRole('button', { name: /create account/i }).click();

    await expect(page.getByText(/email is required/i)).toBeVisible();
    await expect(page.getByText(/first name is required/i)).toBeVisible();
    await expect(page.getByText(/last name is required/i)).toBeVisible();
  });

  test('should show email validation error', async ({ page }) => {
    await page.getByLabel(/email address/i).fill('invalid-email');
    await page.getByRole('button', { name: /create account/i }).click();

    await expect(page.getByText(/please enter a valid email address/i)).toBeVisible();
  });

  test('should show password strength indicator', async ({ page }) => {
    const passwordInput = page.getByLabel(/^password$/i);

    await passwordInput.fill('weak');
    await expect(page.getByText(/weak/i)).toBeVisible();

    await passwordInput.fill('VeryStrongPassword123!');
    await expect(page.getByText(/strong/i)).toBeVisible();
  });

  test('should validate password mismatch', async ({ page }) => {
    await page.getByLabel(/^password$/i).fill('ValidPassword123!');
    await page.getByLabel(/confirm password/i).fill('DifferentPassword123!');
    await page.getByRole('button', { name: /create account/i }).click();

    await expect(page.getByText(/passwords do not match/i)).toBeVisible();
  });

  test('should require terms acceptance', async ({ page }) => {
    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/first name/i).fill('John');
    await page.getByLabel(/last name/i).fill('Doe');
    await page.getByLabel(/^password$/i).fill('ValidPassword123!');
    await page.getByLabel(/confirm password/i).fill('ValidPassword123!');
    await page.getByLabel(/country preference/i).selectOption('UK');

    await page.getByRole('button', { name: /create account/i }).click();

    await expect(page.getByText(/you must accept the terms/i)).toBeVisible();
  });

  test('should successfully register with valid data', async ({ page, context }) => {
    // Mock the API response
    await context.route('**/api/v1/auth/register', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          userId: '123',
          message: 'Registration successful',
        }),
      });
    });

    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/first name/i).fill('John');
    await page.getByLabel(/last name/i).fill('Doe');
    await page.getByLabel(/^password$/i).fill('ValidPassword123!');
    await page.getByLabel(/confirm password/i).fill('ValidPassword123!');
    await page.getByLabel(/country preference/i).selectOption('UK');
    await page.getByRole('checkbox', { name: /i accept the/i }).check();

    await page.getByRole('button', { name: /create account/i }).click();

    await expect(page.getByText(/registration successful/i)).toBeVisible();
    await expect(page.getByText(/verification email/i)).toBeVisible();
  });

  test('should handle API error gracefully', async ({ page, context }) => {
    // Mock API error
    await context.route('**/api/v1/auth/register', async (route) => {
      await route.fulfill({
        status: 409,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Email already exists',
        }),
      });
    });

    await page.getByLabel(/email address/i).fill('existing@example.com');
    await page.getByLabel(/first name/i).fill('John');
    await page.getByLabel(/last name/i).fill('Doe');
    await page.getByLabel(/^password$/i).fill('ValidPassword123!');
    await page.getByLabel(/confirm password/i).fill('ValidPassword123!');
    await page.getByLabel(/country preference/i).selectOption('UK');
    await page.getByRole('checkbox', { name: /i accept the/i }).check();

    await page.getByRole('button', { name: /create account/i }).click();

    await expect(page.getByText(/email already exists/i)).toBeVisible();
  });

  test('should disable form during submission', async ({ page, context }) => {
    // Mock slow API
    await context.route('**/api/v1/auth/register', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    });

    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/first name/i).fill('John');
    await page.getByLabel(/last name/i).fill('Doe');
    await page.getByLabel(/^password$/i).fill('ValidPassword123!');
    await page.getByLabel(/confirm password/i).fill('ValidPassword123!');
    await page.getByLabel(/country preference/i).selectOption('UK');
    await page.getByRole('checkbox', { name: /i accept the/i }).check();

    await page.getByRole('button', { name: /create account/i }).click();

    const submitButton = page.getByRole('button', { name: /creating account/i });
    await expect(submitButton).toBeDisabled();
  });
});
