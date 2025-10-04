// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * E2E Tests for Goals Flow
 *
 * Tests complete user journey:
 * 1. View goals dashboard
 * 2. Create new goal
 * 3. View goal details
 * 4. Edit goal
 * 5. Track progress and milestones
 *
 * Prerequisites:
 * - Backend API running on localhost:8000
 * - Frontend running on localhost:5173
 * - Test user authenticated
 */

test.describe('Goals Management Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login and authenticate
    await page.goto('http://localhost:5173/login');

    // Login with test credentials
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'Test123!@#');
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard');

    // Navigate to goals page
    await page.goto('http://localhost:5173/goals');
  });

  test('displays goals dashboard correctly', async ({ page }) => {
    // Wait for page load
    await page.waitForSelector('h1');

    // Check page title
    const title = await page.textContent('h1');
    expect(title).toContain('Your Financial Goals');

    // Check if dashboard elements are present
    const hasOverview = await page.isVisible('text=Your Progress Overview');
    const hasCreateButton = await page.isVisible('text=Create Goal');

    // Either has overview (goals exist) or empty state
    expect(hasOverview || (await page.isVisible('text=Start Your Journey'))).toBeTruthy();
  });

  test('creates a new goal successfully', async ({ page }) => {
    // Click Create Goal button
    await page.click('text=Create Goal');

    // Wait for form to load
    await page.waitForSelector('text=What are you saving for?');

    // Select goal type - Emergency Fund
    await page.click('text=Emergency Fund');

    // Fill in goal details
    await page.fill('input[id="title"]', 'Emergency Fund - 6 Months Expenses');
    await page.fill('textarea[id="description"]', 'Build up emergency fund to cover 6 months of expenses');
    await page.fill('input[id="target_amount"]', '15000');

    // Set target date (12 months from now)
    const futureDate = new Date();
    futureDate.setMonth(futureDate.getMonth() + 12);
    const dateString = futureDate.toISOString().split('T')[0];
    await page.fill('input[id="target_date"]', dateString);

    // Select High priority
    await page.click('text=High');

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for redirect to goal details
    await page.waitForSelector('text=Your Goal Story', { timeout: 5000 });

    // Verify goal was created
    expect(await page.textContent('h1')).toContain('Emergency Fund');
  });

  test('displays goal details with narrative storytelling', async ({ page }) => {
    // Assuming at least one goal exists, click on first goal card
    const goalCard = page.locator('[style*="cursor: pointer"]').first();
    if (await goalCard.isVisible()) {
      await goalCard.click();

      // Wait for details page
      await page.waitForSelector('text=Your Goal Story');

      // Check narrative elements
      expect(await page.isVisible('text=You started this goal on')).toBeTruthy();

      // Check progress indicators
      const hasProgressBar = await page.locator('[style*="background-color"]').count() > 0;
      expect(hasProgressBar).toBeTruthy();

      // Check action buttons
      expect(await page.isVisible('text=Edit')).toBeTruthy();
      expect(await page.isVisible('text=Delete')).toBeTruthy();
      expect(await page.isVisible('text=← Back')).toBeTruthy();
    }
  });

  test('edits an existing goal', async ({ page }) => {
    // Navigate to first goal (if exists)
    const goalCard = page.locator('[style*="cursor: pointer"]').first();
    if (await goalCard.isVisible()) {
      await goalCard.click();

      // Wait for details page
      await page.waitForSelector('text=Edit');

      // Click Edit button
      await page.click('text=Edit');

      // Wait for form to load
      await page.waitForSelector('input[id="title"]');

      // Modify title
      const currentTitle = await page.inputValue('input[id="title"]');
      await page.fill('input[id="title"]', currentTitle + ' - Updated');

      // Submit changes
      await page.click('button[type="submit"]');

      // Wait for redirect back to details
      await page.waitForSelector('text=Your Goal Story', { timeout: 5000 });

      // Verify title was updated
      expect(await page.textContent('h1')).toContain('Updated');
    }
  });

  test('validates form input correctly', async ({ page }) => {
    // Click Create Goal button
    await page.click('text=Create Goal');

    // Wait for form
    await page.waitForSelector('text=What are you saving for?');

    // Try to submit empty form
    await page.click('button[type="submit"]');

    // Check for validation errors
    await page.waitForSelector('text=/Please give your goal a clear/');
    expect(await page.isVisible('text=/Please enter a specific target amount/')).toBeTruthy();
    expect(await page.isVisible('text=/Please set a target date/')).toBeTruthy();
  });

  test('filters goals by type', async ({ page }) => {
    // Wait for dashboard to load
    await page.waitForSelector('text=Filter by type:', { timeout: 5000 });

    // Find filter dropdown
    const filterSelect = page.locator('select').first();
    await filterSelect.selectOption('EMERGENCY_FUND');

    // Wait for filtered results
    await page.waitForTimeout(1000); // Allow time for API call

    // Verify filter was applied (goals list should update)
    const hasGoals = await page.isVisible('text=Emergency Fund');
    const hasEmptyMessage = await page.isVisible('text=No goals match your current filters');

    // Either has matching goals or empty message
    expect(hasGoals || hasEmptyMessage).toBeTruthy();
  });

  test('shows SMART criteria tips in form', async ({ page }) => {
    // Click Create Goal button
    await page.click('text=Create Goal');

    // Wait for form
    await page.waitForSelector('text=What are you saving for?');

    // Check for SMART criteria section
    expect(await page.isVisible('text=Your goal follows SMART criteria')).toBeTruthy();

    // Click to expand tips
    await page.click('text=Tell me more about SMART goals');

    // Verify tips are shown
    await page.waitForSelector('text=Specific:');
    expect(await page.isVisible('text=Measurable:')).toBeTruthy();
    expect(await page.isVisible('text=Achievable:')).toBeTruthy();
    expect(await page.isVisible('text=Relevant:')).toBeTruthy();
    expect(await page.isVisible('text=Time-bound:')).toBeTruthy();
  });

  test('enables auto-contribution setup', async ({ page }) => {
    // Click Create Goal button
    await page.click('text=Create Goal');

    // Wait for form
    await page.waitForSelector('text=Automate your savings');

    // Enable auto-contribution
    await page.check('input[type="checkbox"]');

    // Verify auto-contribution fields appear
    await page.waitForSelector('text=Monthly Amount');
    expect(await page.isVisible('text=Frequency')).toBeTruthy();

    // Fill in auto-contribution details
    await page.fill('input[id="auto_contribution_amount"]', '500');
    await page.selectOption('select[id="auto_contribution_frequency"]', 'MONTHLY');
  });

  test('deletes a goal with confirmation', async ({ page }) => {
    // Navigate to first goal (if exists)
    const goalCard = page.locator('[style*="cursor: pointer"]').first();
    if (await goalCard.isVisible()) {
      const goalTitle = await goalCard.textContent();

      await goalCard.click();

      // Wait for details page
      await page.waitForSelector('text=Delete');

      // Click Delete button
      await page.click('text=Delete');

      // Wait for confirmation dialog
      await page.waitForSelector('text=Delete this goal?');
      expect(await page.isVisible('text=Are you sure you want to delete')).toBeTruthy();

      // Confirm deletion
      await page.click('text=Yes, Delete Goal');

      // Wait for redirect to dashboard
      await page.waitForURL('**/goals', { timeout: 5000 });

      // Verify goal was deleted (not in list anymore)
      const stillExists = await page.isVisible(`text="${goalTitle}"`);
      expect(stillExists).toBeFalsy();
    }
  });

  test('navigates back to dashboard from goal details', async ({ page }) => {
    // Navigate to first goal (if exists)
    const goalCard = page.locator('[style*="cursor: pointer"]').first();
    if (await goalCard.isVisible()) {
      await goalCard.click();

      // Wait for details page
      await page.waitForSelector('text=← Back');

      // Click Back button
      await page.click('text=← Back');

      // Verify we're back on dashboard
      await page.waitForURL('**/goals');
      expect(await page.isVisible('text=Your Financial Goals')).toBeTruthy();
    }
  });

  test('displays empty state when no goals exist', async ({ page }) => {
    // This test assumes no goals exist for the user
    // In practice, you might want to delete all goals first or use a fresh test user

    await page.waitForSelector('h1', { timeout: 5000 });

    // Check for empty state elements
    const hasEmptyState = await page.isVisible('text=Start Your Journey');

    if (hasEmptyState) {
      expect(await page.isVisible('text=You haven\'t set any financial goals yet')).toBeTruthy();
      expect(await page.isVisible('text=Create Your First Goal')).toBeTruthy();
      expect(await page.isVisible('text=Tips for Setting Goals')).toBeTruthy();
    }
  });

  test('shows encouraging messages based on progress', async ({ page }) => {
    // Navigate to first goal (if exists)
    const goalCard = page.locator('[style*="cursor: pointer"]').first();
    if (await goalCard.isVisible()) {
      await goalCard.click();

      // Wait for details page
      await page.waitForSelector('text=Your Goal Story');

      // Check for encouraging messages (will vary based on progress)
      const hasEncouragement = await page.isVisible('text=/excellent progress|great work|making steady progress|getting started/i');
      expect(hasEncouragement).toBeTruthy();
    }
  });
});
