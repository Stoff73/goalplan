/**
 * COMPREHENSIVE DEBUG AUDIT
 * Tests every page, API endpoint, and user flow
 */

const { test, expect } = require('@playwright/test');

// Test configuration
const BASE_URL = 'http://localhost:5173';
const API_URL = 'http://localhost:8000';
const TEST_USER = {
  email: 'testuser@example.com',
  password: 'Test123!@#'
};

// Utility to capture console errors
function setupConsoleCapture(page, pageName, consoleErrors) {
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push({
        page: pageName,
        message: msg.text(),
        timestamp: new Date().toISOString()
      });
    }
  });

  page.on('pageerror', error => {
    consoleErrors.push({
      page: pageName,
      message: `PAGE ERROR: ${error.message}`,
      stack: error.stack,
      timestamp: new Date().toISOString()
    });
  });
}

// Utility to capture network errors
function setupNetworkCapture(page, pageName, networkErrors) {
  page.on('response', response => {
    if (response.status() >= 400) {
      networkErrors.push({
        page: pageName,
        url: response.url(),
        status: response.status(),
        statusText: response.statusText(),
        timestamp: new Date().toISOString()
      });
    }
  });

  page.on('requestfailed', request => {
    networkErrors.push({
      page: pageName,
      url: request.url(),
      failure: request.failure()?.errorText || 'Unknown error',
      timestamp: new Date().toISOString()
    });
  });
}

test.describe('COMPREHENSIVE APPLICATION AUDIT', () => {
  let consoleErrors = [];
  let networkErrors = [];

  test.beforeEach(async ({ page }) => {
    // Clear error arrays for each test
    consoleErrors = [];
    networkErrors = [];
  });

  test.afterAll(async ({}, testInfo) => {
    // Output all collected errors
    console.log('\n========== AUDIT SUMMARY ==========');
    console.log(`Total Console Errors: ${consoleErrors.length}`);
    console.log(`Total Network Errors: ${networkErrors.length}`);

    if (consoleErrors.length > 0) {
      console.log('\n--- Console Errors ---');
      consoleErrors.forEach(err => {
        console.log(`[${err.page}] ${err.message}`);
        if (err.stack) console.log(`  Stack: ${err.stack}`);
      });
    }

    if (networkErrors.length > 0) {
      console.log('\n--- Network Errors ---');
      networkErrors.forEach(err => {
        console.log(`[${err.page}] ${err.url} - ${err.status || err.failure}`);
      });
    }
  });

  test('1. LOGIN FLOW TEST', async ({ page }) => {
    setupConsoleCapture(page, 'Login', consoleErrors);
    setupNetworkCapture(page, 'Login', networkErrors);

    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    // Check for login form elements
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();

    // Fill and submit login
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);

    // Take screenshot before submit
    await page.screenshot({ path: 'test-results/login-before-submit.png' });

    await page.click('button[type="submit"]');

    // Wait for navigation or error
    try {
      await page.waitForURL(/\/(dashboard|$)/, { timeout: 10000 });
      console.log('✓ Login successful - redirected to dashboard');
    } catch (error) {
      await page.screenshot({ path: 'test-results/login-failed.png' });
      console.log('✗ Login failed - no redirect');
      throw error;
    }
  });

  test('2. DASHBOARD PAGE TEST', async ({ page, context }) => {
    setupConsoleCapture(page, 'Dashboard', consoleErrors);
    setupNetworkCapture(page, 'Dashboard', networkErrors);

    // Login first
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(dashboard|$)/, { timeout: 10000 });

    // Navigate to dashboard
    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/dashboard.png' });

    // Check for dashboard elements
    const hasContent = await page.locator('body').textContent();
    console.log('Dashboard loaded with content length:', hasContent.length);

    // Check for common dashboard elements
    const hasDashboardHeading = await page.locator('h1, h2').count();
    console.log('Dashboard headings found:', hasDashboardHeading);
  });

  test('3. INCOME PAGE TEST', async ({ page }) => {
    setupConsoleCapture(page, 'Income', consoleErrors);
    setupNetworkCapture(page, 'Income', networkErrors);

    // Login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(dashboard|$)/, { timeout: 10000 });

    // Navigate to income page
    await page.goto(`${BASE_URL}/income`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/income-page.png' });

    // Check page loaded
    const pageContent = await page.textContent('body');
    console.log('Income page content length:', pageContent.length);
  });

  test('4. TAX STATUS PAGE TEST', async ({ page }) => {
    setupConsoleCapture(page, 'TaxStatus', consoleErrors);
    setupNetworkCapture(page, 'TaxStatus', networkErrors);

    // Login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(dashboard|$)/, { timeout: 10000 });

    // Navigate to tax status page
    await page.goto(`${BASE_URL}/tax-status`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/tax-status-page.png' });

    const pageContent = await page.textContent('body');
    console.log('Tax Status page content length:', pageContent.length);
  });

  test('5. PROTECTION PAGE TEST', async ({ page }) => {
    setupConsoleCapture(page, 'Protection', consoleErrors);
    setupNetworkCapture(page, 'Protection', networkErrors);

    // Login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(dashboard|$)/, { timeout: 10000 });

    await page.goto(`${BASE_URL}/protection`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/protection-page.png' });

    const pageContent = await page.textContent('body');
    console.log('Protection page content length:', pageContent.length);
  });

  test('6. INVESTMENT PAGE TEST', async ({ page }) => {
    setupConsoleCapture(page, 'Investment', consoleErrors);
    setupNetworkCapture(page, 'Investment', networkErrors);

    // Login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(dashboard|$)/, { timeout: 10000 });

    await page.goto(`${BASE_URL}/investments`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/investments-page.png' });

    const pageContent = await page.textContent('body');
    console.log('Investments page content length:', pageContent.length);
  });

  test('7. RETIREMENT PAGE TEST', async ({ page }) => {
    setupConsoleCapture(page, 'Retirement', consoleErrors);
    setupNetworkCapture(page, 'Retirement', networkErrors);

    // Login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(dashboard|$)/, { timeout: 10000 });

    await page.goto(`${BASE_URL}/retirement`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/retirement-page.png' });

    const pageContent = await page.textContent('body');
    console.log('Retirement page content length:', pageContent.length);
  });

  test('8. IHT PAGE TEST', async ({ page }) => {
    setupConsoleCapture(page, 'IHT', consoleErrors);
    setupNetworkCapture(page, 'IHT', networkErrors);

    // Login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(dashboard|$)/, { timeout: 10000 });

    await page.goto(`${BASE_URL}/iht`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/iht-page.png' });

    const pageContent = await page.textContent('body');
    console.log('IHT page content length:', pageContent.length);
  });

  test('9. GOALS PAGE TEST', async ({ page }) => {
    setupConsoleCapture(page, 'Goals', consoleErrors);
    setupNetworkCapture(page, 'Goals', networkErrors);

    // Login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(dashboard|$)/, { timeout: 10000 });

    await page.goto(`${BASE_URL}/goals`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/goals-page.png' });

    const pageContent = await page.textContent('body');
    console.log('Goals page content length:', pageContent.length);
  });

  test('10. SCENARIOS PAGE TEST', async ({ page }) => {
    setupConsoleCapture(page, 'Scenarios', consoleErrors);
    setupNetworkCapture(page, 'Scenarios', networkErrors);

    // Login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(dashboard|$)/, { timeout: 10000 });

    await page.goto(`${BASE_URL}/scenarios`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/scenarios-page.png' });

    const pageContent = await page.textContent('body');
    console.log('Scenarios page content length:', pageContent.length);
  });

  test('11. AI ADVISOR PAGE TEST', async ({ page }) => {
    setupConsoleCapture(page, 'AIAdvisor', consoleErrors);
    setupNetworkCapture(page, 'AIAdvisor', networkErrors);

    // Login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(dashboard|$)/, { timeout: 10000 });

    await page.goto(`${BASE_URL}/ai-advisor`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/ai-advisor-page.png' });

    const pageContent = await page.textContent('body');
    console.log('AI Advisor page content length:', pageContent.length);
  });

  test('12. RECOMMENDATIONS PAGE TEST', async ({ page }) => {
    setupConsoleCapture(page, 'Recommendations', consoleErrors);
    setupNetworkCapture(page, 'Recommendations', networkErrors);

    // Login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(dashboard|$)/, { timeout: 10000 });

    await page.goto(`${BASE_URL}/recommendations`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/recommendations-page.png' });

    const pageContent = await page.textContent('body');
    console.log('Recommendations page content length:', pageContent.length);
  });

  test('13. API HEALTH CHECK - All Endpoints', async ({ request }) => {
    // First, login to get token
    const loginResponse = await request.post(`${API_URL}/api/v1/auth/login`, {
      data: {
        email: TEST_USER.email,
        password: TEST_USER.password
      }
    });

    expect(loginResponse.ok()).toBeTruthy();
    const loginData = await loginResponse.json();
    const token = loginData.access_token;

    console.log('\n--- Testing API Endpoints ---');

    // Test user endpoints
    const endpoints = [
      { method: 'GET', path: '/api/v1/users/me', name: 'Get Current User' },
      { method: 'GET', path: '/api/v1/income', name: 'Get Income List' },
      { method: 'GET', path: '/api/v1/tax-status', name: 'Get Tax Status' },
      { method: 'GET', path: '/api/v1/dashboard/summary', name: 'Dashboard Summary' },
      { method: 'GET', path: '/api/v1/protection/policies', name: 'Protection Policies' },
      { method: 'GET', path: '/api/v1/investments/portfolio', name: 'Investment Portfolio' },
      { method: 'GET', path: '/api/v1/retirement/overview', name: 'Retirement Overview' },
      { method: 'GET', path: '/api/v1/iht/summary', name: 'IHT Summary' },
      { method: 'GET', path: '/api/v1/goals', name: 'Goals List' },
      { method: 'GET', path: '/api/v1/scenarios', name: 'Scenarios List' },
      { method: 'GET', path: '/api/v1/ai/insights', name: 'AI Insights' },
      { method: 'GET', path: '/api/v1/recommendations', name: 'Recommendations' }
    ];

    for (const endpoint of endpoints) {
      try {
        const response = await request[endpoint.method.toLowerCase()](
          `${API_URL}${endpoint.path}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );

        console.log(`${endpoint.name}: ${response.status()} ${response.statusText()}`);

        if (!response.ok()) {
          const body = await response.text();
          console.log(`  Error: ${body}`);
        }
      } catch (error) {
        console.log(`${endpoint.name}: ERROR - ${error.message}`);
      }
    }
  });
});
