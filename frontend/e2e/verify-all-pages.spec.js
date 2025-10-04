/**
 * Comprehensive verification test - Tests all pages load correctly
 *
 * This test:
 * 1. Logs in with test user
 * 2. Navigates to every page in the app
 * 3. Verifies each page loads without errors
 * 4. Checks for navigation header
 * 5. Takes screenshot of each page
 */

import { test, expect } from '@playwright/test';

const TEST_USER = {
  email: 'test@goalplan.com',
  password: 'TestPass@123',
};

test.describe('Full Application Verification', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('http://localhost:5173/login');

    // Wait for login form
    await expect(page.locator('input[type="email"]')).toBeVisible();

    // Fill in credentials
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);

    // Click login button
    await page.click('button:has-text("Sign In")');

    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard', { timeout: 5000 });
  });

  test('Dashboard page loads correctly', async ({ page }) => {
    await page.goto('http://localhost:5173/dashboard');

    // Check header is present
    await expect(page.locator('header')).toBeVisible();
    await expect(page.getByText('GoalPlan')).toBeVisible();

    // Check navigation links
    await expect(page.locator('a[href="/dashboard"]')).toBeVisible();

    // Check page content loads
    await expect(page.locator('text=Net Worth')).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: 'test-results/dashboard.png', fullPage: true });

    console.log('✅ Dashboard page loads correctly');
  });

  test('Tax Status page loads correctly', async ({ page }) => {
    await page.goto('http://localhost:5173/tax-status');

    // Check header
    await expect(page.locator('header')).toBeVisible();

    // Check navigation
    await expect(page.locator('a[href="/tax-status"]')).toBeVisible();

    // Check page loads (either shows data or empty state)
    const hasContent = await page.locator('text=Tax Residency').isVisible().catch(() => false) ||
                       await page.locator('text=tax status').isVisible().catch(() => false);

    expect(hasContent || await page.locator('text=Start').isVisible()).toBeTruthy();

    await page.screenshot({ path: 'test-results/tax-status.png', fullPage: true });

    console.log('✅ Tax Status page loads correctly');
  });

  test('Income page loads correctly', async ({ page }) => {
    await page.goto('http://localhost:5173/income');

    // Check header
    await expect(page.locator('header')).toBeVisible();

    // Check navigation
    await expect(page.locator('a[href="/income"]')).toBeVisible();

    // Check page loads
    const hasContent = await page.locator('text=Income').isVisible();
    expect(hasContent).toBeTruthy();

    await page.screenshot({ path: 'test-results/income.png', fullPage: true });

    console.log('✅ Income page loads correctly');
  });

  test('Savings page loads correctly', async ({ page }) => {
    await page.goto('http://localhost:5173/savings');

    // Check header
    await expect(page.locator('header')).toBeVisible();

    // Check navigation
    await expect(page.locator('a[href="/savings"]')).toBeVisible();

    // Check page loads
    const hasContent = await page.locator('text=Savings').isVisible() ||
                       await page.locator('text=savings').isVisible();
    expect(hasContent).toBeTruthy();

    await page.screenshot({ path: 'test-results/savings.png', fullPage: true });

    console.log('✅ Savings page loads correctly');
  });

  test('Protection page loads correctly', async ({ page }) => {
    await page.goto('http://localhost:5173/protection');

    // Check header
    await expect(page.locator('header')).toBeVisible();

    // Check navigation
    await expect(page.locator('a[href="/protection"]')).toBeVisible();

    // Check page loads
    const hasContent = await page.locator('text=Protection').isVisible() ||
                       await page.locator('text=coverage').isVisible();
    expect(hasContent).toBeTruthy();

    await page.screenshot({ path: 'test-results/protection.png', fullPage: true });

    console.log('✅ Protection page loads correctly');
  });

  test('Investments page loads correctly', async ({ page }) => {
    await page.goto('http://localhost:5173/investments');

    // Check header
    await expect(page.locator('header')).toBeVisible();

    // Check navigation
    await expect(page.locator('a[href="/investments"]')).toBeVisible();

    // Check page loads (should show either data or empty state)
    const hasContent = await page.locator('text=Investment').isVisible() ||
                       await page.locator('text=Portfolio').isVisible() ||
                       await page.locator('text=portfolio').isVisible();
    expect(hasContent).toBeTruthy();

    await page.screenshot({ path: 'test-results/investments.png', fullPage: true });

    console.log('✅ Investments page loads correctly');
  });

  test('Goals page loads correctly', async ({ page }) => {
    await page.goto('http://localhost:5173/goals');

    // Check header
    await expect(page.locator('header')).toBeVisible();

    // Check navigation
    await expect(page.locator('a[href="/goals"]')).toBeVisible();

    // Check page loads
    const hasContent = await page.locator('text=Goals').isVisible() ||
                       await page.locator('text=Financial Goals').isVisible();
    expect(hasContent).toBeTruthy();

    await page.screenshot({ path: 'test-results/goals.png', fullPage: true });

    console.log('✅ Goals page loads correctly');
  });

  test('Profile page loads correctly', async ({ page }) => {
    await page.goto('http://localhost:5173/profile');

    // Check header
    await expect(page.locator('header')).toBeVisible();

    // Check navigation
    await expect(page.locator('a[href="/profile"]')).toBeVisible();

    // Check page loads
    const hasContent = await page.locator('text=Profile').isVisible() ||
                       await page.locator('text=profile').isVisible() ||
                       await page.locator('text=Test User').isVisible();
    expect(hasContent).toBeTruthy();

    await page.screenshot({ path: 'test-results/profile.png', fullPage: true });

    console.log('✅ Profile page loads correctly');
  });

  test('No console errors on any page', async ({ page }) => {
    const consoleErrors = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Visit all pages
    const pages = [
      'http://localhost:5173/dashboard',
      'http://localhost:5173/tax-status',
      'http://localhost:5173/income',
      'http://localhost:5173/savings',
      'http://localhost:5173/protection',
      'http://localhost:5173/investments',
      'http://localhost:5173/goals',
      'http://localhost:5173/profile',
    ];

    for (const url of pages) {
      await page.goto(url);
      await page.waitForTimeout(1000); // Wait for page to settle
    }

    // Filter out known acceptable errors (like 404 for personalization)
    const criticalErrors = consoleErrors.filter(err =>
      !err.includes('404') &&
      !err.includes('personalization/preferences')
    );

    if (criticalErrors.length > 0) {
      console.error('❌ Console errors found:');
      criticalErrors.forEach(err => console.error('  -', err));
    }

    expect(criticalErrors.length).toBe(0);

    console.log('✅ No critical console errors on any page');
  });
});
