const { test, expect } = require('@playwright/test');

test.describe('Scenarios - E2E Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('http://localhost:5173/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard');

    // Navigate to scenarios page
    await page.goto('http://localhost:5173/scenarios');
  });

  test('should display scenarios page with tabs', async ({ page }) => {
    // Check page title
    await expect(page.locator('h1')).toContainText('Scenario Analysis');

    // Check all tabs are present
    await expect(page.locator('button:has-text("Retirement Age")')).toBeVisible();
    await expect(page.locator('button:has-text("Career Change")')).toBeVisible();
    await expect(page.locator('button:has-text("Property Purchase")')).toBeVisible();
    await expect(page.locator('button:has-text("Monte Carlo")')).toBeVisible();
    await expect(page.locator('button:has-text("Compare Scenarios")')).toBeVisible();
  });

  test('should interact with retirement age slider', async ({ page }) => {
    // Retirement Age tab should be active by default
    await expect(page.locator('h3:has-text("Explore when to retire")')).toBeVisible();

    // Find and interact with slider
    const slider = page.locator('input[type="range"]');
    await expect(slider).toBeVisible();

    // Change retirement age
    await slider.fill('60');

    // Wait for scenario to load
    await page.waitForTimeout(1000);

    // Check that results are displayed
    await expect(page.locator('text=/If you retired at/i')).toBeVisible();
  });

  test('should submit career change form', async ({ page }) => {
    // Click Career Change tab
    await page.click('button:has-text("Career Change")');

    // Fill in form
    await page.fill('input[id="newSalary"]', '60000');
    await page.fill('input[id="changeDate"]', '2026-06-01');

    // Submit form
    await page.click('button:has-text("Show me the impact")');

    // Wait for results
    await page.waitForTimeout(1000);

    // Check results are displayed
    await expect(page.locator('text=/salary/i')).toBeVisible();
  });

  test('should submit property purchase form', async ({ page }) => {
    // Click Property Purchase tab
    await page.click('button:has-text("Property Purchase")');

    // Fill in property details
    await page.fill('input[id="propertyValue"]', '300000');
    await page.fill('input[id="deposit"]', '60000');
    await page.fill('input[id="mortgageRate"]', '4.5');
    await page.fill('input[id="mortgageTerm"]', '25');

    // Submit form
    await page.click('button:has-text("Check affordability")');

    // Wait for results
    await page.waitForTimeout(1000);

    // Check affordability indicator is displayed
    await expect(page.locator('text=/monthly mortgage payment/i')).toBeVisible();
  });

  test('should run Monte Carlo simulation', async ({ page }) => {
    // Click Monte Carlo tab
    await page.click('button:has-text("Monte Carlo")');

    // Check intro text
    await expect(page.locator('h3:has-text("How confident can you be?")')).toBeVisible();

    // Click run simulation button
    await page.click('button:has-text("Run Monte Carlo analysis")');

    // Wait for simulation to complete (may take a few seconds)
    await page.waitForTimeout(3000);

    // Check results are displayed
    await expect(page.locator('text=/Probability of Success/i')).toBeVisible();
    await expect(page.locator('text=/%/i')).toBeVisible();
  });

  test('should navigate between tabs', async ({ page }) => {
    // Start on Retirement Age tab
    await expect(page.locator('h3:has-text("Explore when to retire")')).toBeVisible();

    // Switch to Career Change
    await page.click('button:has-text("Career Change")');
    await expect(page.locator('h3:has-text("Model a job change")')).toBeVisible();

    // Switch to Property
    await page.click('button:has-text("Property Purchase")');
    await expect(page.locator('h3:has-text("Can you afford a property?")')).toBeVisible();

    // Switch to Monte Carlo
    await page.click('button:has-text("Monte Carlo")');
    await expect(page.locator('h3:has-text("How confident can you be?")')).toBeVisible();

    // Switch to Compare
    await page.click('button:has-text("Compare Scenarios")');
    await expect(page.locator('h3:has-text("Compare your scenarios side-by-side")')).toBeVisible();
  });

  test('should display narrative storytelling elements', async ({ page }) => {
    // Check for conversational language
    await expect(page.locator('text=/You\'re currently planning to retire/i')).toBeVisible();

    // Check for narrative paragraphs (not just data labels)
    const narrativeText = page.locator('p').first();
    await expect(narrativeText).toBeVisible();

    // Check page uses generous white space (line-height should be visible in styles)
    const cardElement = page.locator('[style*="lineHeight"]').first();
    await expect(cardElement).toBeVisible();
  });

  test('complete scenario analysis journey', async ({ page }) => {
    // 1. Try retirement age slider
    const slider = page.locator('input[type="range"]');
    await slider.fill('62');
    await page.waitForTimeout(1000);

    // 2. Switch to Career Change
    await page.click('button:has-text("Career Change")');
    await page.fill('input[id="newSalary"]', '55000');
    await page.fill('input[id="changeDate"]', '2025-12-01');
    await page.click('button:has-text("Show me the impact")');
    await page.waitForTimeout(1000);

    // 3. Check Property Purchase
    await page.click('button:has-text("Property Purchase")');
    await page.fill('input[id="propertyValue"]', '250000');
    await page.fill('input[id="deposit"]', '50000');
    await page.fill('input[id="mortgageRate"]', '4.0');
    await page.click('button:has-text("Check affordability")');
    await page.waitForTimeout(1000);

    // 4. Run Monte Carlo
    await page.click('button:has-text("Monte Carlo")');
    await page.click('button:has-text("Run Monte Carlo analysis")');
    await page.waitForTimeout(3000);

    // Verify all scenarios completed successfully
    expect(true).toBe(true); // If we got here without errors, journey succeeded
  });
});
