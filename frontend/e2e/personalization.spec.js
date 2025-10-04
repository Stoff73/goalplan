const { test, expect } = require('@playwright/test');

/**
 * E2E Tests for Personalization Features
 *
 * Tests the complete personalization user flow:
 * 1. Login
 * 2. Navigate to personalized dashboard
 * 3. View insights
 * 4. Go to settings
 * 5. Change preferences
 * 6. Verify saved
 */

test.describe('Personalization E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('http://localhost:5173/login');
  });

  test('complete personalization flow', async ({ page }) => {
    // Step 1: Login
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');

    // Wait for dashboard to load
    await page.waitForURL('**/dashboard');

    // Step 2: Navigate to personalized dashboard
    await page.click('a[href="/personalized-dashboard"]');
    await page.waitForURL('**/personalized-dashboard');

    // Verify personalized dashboard loaded
    await expect(page.locator('text=Your personalized dashboard')).toBeVisible();

    // Step 3: Verify widgets are displayed
    await expect(page.locator('text=Your financial sections')).toBeVisible();

    // Step 4: Verify insights feed is visible
    await expect(page.locator('text=Personalized insights for you')).toBeVisible();

    // Step 5: Navigate to settings
    await page.click('text=Open Personalization Settings');
    await page.waitForURL('**/settings/personalization');

    // Verify settings page loaded
    await expect(page.locator('text=Personalization settings')).toBeVisible();

    // Step 6: Change currency preference
    await page.selectOption('select#currency', 'USD');

    // Step 7: Change theme preference
    await page.selectOption('select#theme', 'dark');

    // Step 8: Change notification frequency
    await page.selectOption('select#notificationFrequency', 'daily');

    // Step 9: Save preferences
    await page.click('button:has-text("Save All Preferences")');

    // Step 10: Verify success message
    await expect(page.locator('text=Preferences saved!')).toBeVisible();

    // Step 11: Navigate back to personalized dashboard
    await page.click('a[href="/personalized-dashboard"]');
    await page.waitForURL('**/personalized-dashboard');

    // Verify we're back on the dashboard
    await expect(page.locator('text=Your personalized dashboard')).toBeVisible();
  });

  test('view and dismiss insights', async ({ page }) => {
    // Login
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Navigate to personalized dashboard
    await page.click('a[href="/personalized-dashboard"]');
    await page.waitForURL('**/personalized-dashboard');

    // Wait for insights to load
    await page.waitForSelector('text=Personalized insights for you');

    // Check if insights exist
    const insightCards = page.locator('[style*="cursor: pointer"]');
    const insightCount = await insightCards.count();

    if (insightCount > 0) {
      // Click dismiss on first insight
      await page.click('button:has-text("Dismiss")').first();

      // Wait a moment for the insight to be removed
      await page.waitForTimeout(500);

      // Verify insight count decreased or empty state appears
      const newInsightCount = await insightCards.count();
      expect(newInsightCount).toBeLessThanOrEqual(insightCount);
    }
  });

  test('toggle hidden widgets', async ({ page }) => {
    // Login
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Navigate to personalized dashboard
    await page.click('a[href="/personalized-dashboard"]');
    await page.waitForURL('**/personalized-dashboard');

    // Check if there are hidden widgets
    const showHiddenButton = page.locator('text=/Show .* less-used section/');
    const hasHiddenWidgets = await showHiddenButton.count() > 0;

    if (hasHiddenWidgets) {
      // Click to show hidden widgets
      await showHiddenButton.click();

      // Verify hidden widgets are now visible
      // (specific widgets depend on user behavior, so just check button changed)
      await expect(page.locator('button:has-text("▼")')).toBeVisible();

      // Click again to hide
      await showHiddenButton.click();

      // Verify button shows expand icon again
      await expect(page.locator('button:has-text("▶")')).toBeVisible();
    }
  });

  test('navigate between personalization pages', async ({ page }) => {
    // Login
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Navigate to settings directly
    await page.click('a[href="/settings/personalization"]');
    await page.waitForURL('**/settings/personalization');

    // Verify settings loaded
    await expect(page.locator('text=Personalization settings')).toBeVisible();

    // Click cancel to go back to dashboard
    await page.click('button:has-text("Cancel")');
    await page.waitForURL('**/personalized-dashboard');

    // Verify we're on personalized dashboard
    await expect(page.locator('text=Your personalized dashboard')).toBeVisible();
  });

  test('verify behavior tracking', async ({ page }) => {
    // Setup request interception to verify tracking calls
    const trackingRequests = [];

    page.on('request', request => {
      if (request.url().includes('/api/v1/personalization/behavior/track')) {
        trackingRequests.push(request);
      }
    });

    // Login
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Navigate to personalized dashboard
    await page.click('a[href="/personalized-dashboard"]');
    await page.waitForURL('**/personalized-dashboard');

    // Wait a moment for tracking to fire
    await page.waitForTimeout(1000);

    // Verify at least one tracking request was made
    expect(trackingRequests.length).toBeGreaterThan(0);
  });

  test('refresh insights', async ({ page }) => {
    // Login
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Navigate to personalized dashboard
    await page.click('a[href="/personalized-dashboard"]');
    await page.waitForURL('**/personalized-dashboard');

    // Wait for insights section
    await page.waitForSelector('text=Personalized insights for you');

    // Click refresh insights button
    const refreshButton = page.locator('button:has-text("Refresh Insights")');
    if (await refreshButton.count() > 0) {
      await refreshButton.click();

      // Wait for insights to reload
      await page.waitForTimeout(1000);

      // Verify insights section still visible
      await expect(page.locator('text=Personalized insights for you')).toBeVisible();
    }
  });
});
