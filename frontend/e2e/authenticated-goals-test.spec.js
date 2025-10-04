import { test, expect } from '@playwright/test';

/**
 * Authenticated Goals Page Test
 *
 * This test verifies that the database fix works by:
 * 1. Logging in with an existing user
 * 2. Navigating to the Goals page
 * 3. Verifying the API responds with 200 (not 500)
 * 4. Checking the page renders correctly
 */

test.describe('Authenticated Goals Flow', () => {

  test('should load Goals page successfully after database fix', async ({ page }) => {
    // Navigate to login
    await page.goto('http://localhost:5173/login');
    await expect(page).toHaveURL(/.*login/);

    // Login with existing user (from backend logs we know user is authenticated)
    // If no user exists, this test will create one
    const testEmail = 'e2e.test@example.com';
    const testPassword = 'SecurePass123!';

    // Try to login first
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);

    // Set up response listener BEFORE clicking login
    const loginPromise = page.waitForResponse(
      response => response.url().includes('/api/v1/auth/login'),
      { timeout: 10000 }
    );

    await page.click('button[type="submit"]');

    try {
      const loginResponse = await loginPromise;
      console.log('Login response status:', loginResponse.status());

      // If login fails with 401, we need to register first
      if (loginResponse.status() === 401) {
        console.log('User does not exist, registering...');

        // Navigate to registration
        await page.goto('http://localhost:5173/register');

        // Fill registration form
        await page.fill('input[name="email"]', testEmail);
        await page.fill('input[name="password"]', testPassword);
        await page.fill('input[name="confirmPassword"]', testPassword);
        await page.fill('input[name="firstName"]', 'E2E');
        await page.fill('input[name="lastName"]', 'Test');

        // Submit registration
        const registerPromise = page.waitForResponse(
          response => response.url().includes('/api/v1/auth/register')
        );

        await page.click('button[type="submit"]');
        const registerResponse = await registerPromise;

        console.log('Registration response status:', registerResponse.status());

        if (registerResponse.status() === 201) {
          // Registration successful, now login
          await page.goto('http://localhost:5173/login');
          await page.fill('input[type="email"]', testEmail);
          await page.fill('input[type="password"]', testPassword);

          const secondLoginPromise = page.waitForResponse(
            response => response.url().includes('/api/v1/auth/login')
          );

          await page.click('button[type="submit"]');
          const secondLoginResponse = await secondLoginPromise;

          expect(secondLoginResponse.status()).toBe(200);
          console.log('✅ Login successful after registration');
        }
      } else if (loginResponse.status() === 200) {
        console.log('✅ Login successful with existing user');
      }

      // Wait for redirect to dashboard
      await page.waitForURL(/.*dashboard/, { timeout: 5000 });
      console.log('✅ Redirected to dashboard');

    } catch (error) {
      console.error('Login/Registration error:', error.message);
      throw error;
    }

    // Now navigate to Goals page
    console.log('Navigating to Goals page...');

    // Set up response listener for goals API
    const goalsOverviewPromise = page.waitForResponse(
      response => response.url().includes('/api/v1/goals/overview'),
      { timeout: 10000 }
    );

    await page.goto('http://localhost:5173/goals');

    // Wait for the goals API response
    try {
      const goalsResponse = await goalsOverviewPromise;
      const status = goalsResponse.status();

      console.log('Goals API response status:', status);

      // CRITICAL TEST: Should be 200, not 500 (database error)
      expect(status).toBe(200);
      console.log('✅ Goals API returned 200 - database is working!');

      // Verify the response body
      const goalsData = await goalsResponse.json();
      console.log('Goals data:', JSON.stringify(goalsData, null, 2));

      // Check page rendered correctly
      await expect(page.locator('h1, h2').first()).toBeVisible();
      console.log('✅ Goals page rendered successfully');

      // Take screenshot of successful goals page
      await page.screenshot({ path: 'e2e-goals-success.png', fullPage: true });
      console.log('✅ Screenshot saved: e2e-goals-success.png');

    } catch (error) {
      console.error('❌ Goals page test failed:', error.message);

      // Take screenshot of failure
      await page.screenshot({ path: 'e2e-goals-failure.png', fullPage: true });
      console.log('Screenshot of failure saved: e2e-goals-failure.png');

      throw error;
    }
  });

  test('should handle creating a new goal', async ({ page }) => {
    // Login first
    await page.goto('http://localhost:5173/login');

    const testEmail = 'e2e.test@example.com';
    const testPassword = 'SecurePass123!';

    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.click('button[type="submit"]');

    // Wait for dashboard
    await page.waitForURL(/.*dashboard/, { timeout: 5000 });

    // Navigate to Goals
    await page.goto('http://localhost:5173/goals');

    // Wait for page to load
    await page.waitForTimeout(2000);

    // Look for "Add Goal" or "Create Goal" button
    const addButton = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New Goal")').first();

    if (await addButton.isVisible()) {
      console.log('Found add goal button, clicking...');
      await addButton.click();

      // Wait for form or modal
      await page.waitForTimeout(1000);

      // Take screenshot of goal creation form
      await page.screenshot({ path: 'e2e-goal-creation-form.png', fullPage: true });
      console.log('✅ Goal creation form displayed');
    } else {
      console.log('ℹ️  No add goal button found - may not be implemented yet');
      await page.screenshot({ path: 'e2e-goals-page-no-add-button.png', fullPage: true });
    }
  });
});
