/**
 * COMPREHENSIVE APPLICATION BUG ASSESSMENT
 *
 * This test systematically checks EVERY page, endpoint, and feature
 * to identify ALL bugs, errors, and issues in the GoalPlan application.
 *
 * Test Coverage:
 * 1. Authentication flow (login, logout, registration, 2FA)
 * 2. All module pages (Dashboard, Tax Status, Income, Savings, Protection, etc.)
 * 3. Console errors (JavaScript errors)
 * 4. Network errors (API failures, 404s, 500s, CORS issues)
 * 5. Visual rendering issues
 * 6. Functional testing (user interactions)
 */

import { test, expect } from '@playwright/test';

const TEST_USER = {
  email: 'test@goalplan.com',
  password: 'TestPass@123',
};

// Store all discovered issues
const issues = {
  consoleErrors: [],
  networkErrors: [],
  renderingIssues: [],
  functionalIssues: [],
  authIssues: []
};

test.describe('COMPREHENSIVE APPLICATION ASSESSMENT', () => {

  test.beforeEach(async ({ page }) => {
    // Clear issues for each test
    issues.consoleErrors = [];
    issues.networkErrors = [];

    // Monitor console errors
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        issues.consoleErrors.push({
          text: msg.text(),
          location: msg.location(),
          timestamp: new Date().toISOString()
        });
      }
    });

    // Monitor network errors
    page.on('response', async (response) => {
      if (response.status() >= 400) {
        const url = response.url();
        const status = response.status();
        let body = 'Unable to parse';

        try {
          body = await response.text();
        } catch (e) {
          // Ignore parsing errors
        }

        issues.networkErrors.push({
          url,
          status,
          statusText: response.statusText(),
          body: body.substring(0, 500), // Limit body size
          timestamp: new Date().toISOString()
        });
      }
    });
  });

  test('1. PUBLIC PAGES - Test login page loads', async ({ page }) => {
    console.log('\n=== TESTING PUBLIC PAGES ===\n');

    await page.goto('http://localhost:5173/login');

    // Check page loads
    await expect(page.locator('input[type="email"]')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button:has-text("Sign In")')).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: 'test-results/screenshots/login-page.png', fullPage: true });

    console.log('✅ Login page loads correctly');

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on login page:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on login page:', issues.networkErrors);
    }
  });

  test('2. AUTHENTICATION - Test login flow', async ({ page }) => {
    console.log('\n=== TESTING AUTHENTICATION ===\n');

    await page.goto('http://localhost:5173/login');

    // Fill in credentials
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);

    // Click login
    await page.click('button:has-text("Sign In")');

    // Wait for redirect (either to dashboard or 2FA)
    try {
      await page.waitForURL('**/dashboard', { timeout: 5000 });
      console.log('✅ Login successful - redirected to dashboard');
    } catch (e) {
      // Check if we're on 2FA page
      const on2FA = await page.locator('text=two-factor').isVisible().catch(() => false) ||
                    await page.locator('text=2FA').isVisible().catch(() => false);

      if (on2FA) {
        console.log('ℹ️ 2FA is enabled for test user');
      } else {
        console.log('❌ Login failed - not redirected to dashboard or 2FA');
        issues.authIssues.push('Login did not redirect to dashboard or 2FA');

        // Take screenshot of error
        await page.screenshot({ path: 'test-results/screenshots/login-error.png', fullPage: true });
      }
    }

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors during login:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors during login:', issues.networkErrors);
    }
  });

  test('3. DASHBOARD - Test dashboard page', async ({ page }) => {
    console.log('\n=== TESTING DASHBOARD ===\n');

    // Login first
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');

    try {
      await page.waitForURL('**/dashboard', { timeout: 5000 });
    } catch (e) {
      console.log('❌ Failed to reach dashboard after login');
      issues.functionalIssues.push('Cannot reach dashboard after login');
      return;
    }

    // Wait for page to settle
    await page.waitForTimeout(2000);

    // Check for key dashboard elements
    const hasHeader = await page.locator('header').isVisible();
    const hasNavigation = await page.locator('nav').isVisible();
    const hasNetWorth = await page.locator('text=/net worth/i').isVisible().catch(() => false);

    console.log('Dashboard elements:', {
      hasHeader,
      hasNavigation,
      hasNetWorth
    });

    // Take screenshot
    await page.screenshot({ path: 'test-results/screenshots/dashboard.png', fullPage: true });

    if (!hasHeader) {
      issues.renderingIssues.push('Dashboard missing header');
    }
    if (!hasNavigation) {
      issues.renderingIssues.push('Dashboard missing navigation');
    }

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on dashboard:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on dashboard:', issues.networkErrors);
    }
  });

  test('4. TAX STATUS PAGE - Test tax status module', async ({ page }) => {
    console.log('\n=== TESTING TAX STATUS PAGE ===\n');

    // Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {});

    // Navigate to tax status
    await page.goto('http://localhost:5173/tax-status');
    await page.waitForTimeout(2000);

    // Check if page loads
    const hasContent = await page.locator('body').textContent();
    console.log('Tax Status page loaded, content includes:', hasContent.substring(0, 200));

    // Take screenshot
    await page.screenshot({ path: 'test-results/screenshots/tax-status.png', fullPage: true });

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on tax status page:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on tax status page:', issues.networkErrors);
    }
  });

  test('5. INCOME PAGE - Test income module', async ({ page }) => {
    console.log('\n=== TESTING INCOME PAGE ===\n');

    // Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {});

    // Navigate to income
    await page.goto('http://localhost:5173/income');
    await page.waitForTimeout(2000);

    // Check if page loads
    const hasContent = await page.locator('body').textContent();
    console.log('Income page loaded, content includes:', hasContent.substring(0, 200));

    // Take screenshot
    await page.screenshot({ path: 'test-results/screenshots/income.png', fullPage: true });

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on income page:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on income page:', issues.networkErrors);
    }
  });

  test('6. SAVINGS PAGE - Test savings module', async ({ page }) => {
    console.log('\n=== TESTING SAVINGS PAGE ===\n');

    // Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {});

    // Navigate to savings
    await page.goto('http://localhost:5173/savings');
    await page.waitForTimeout(2000);

    const hasContent = await page.locator('body').textContent();
    console.log('Savings page loaded');

    await page.screenshot({ path: 'test-results/screenshots/savings.png', fullPage: true });

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on savings page:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on savings page:', issues.networkErrors);
    }
  });

  test('7. PROTECTION PAGE - Test protection module', async ({ page }) => {
    console.log('\n=== TESTING PROTECTION PAGE ===\n');

    // Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {});

    // Navigate to protection
    await page.goto('http://localhost:5173/protection');
    await page.waitForTimeout(2000);

    await page.screenshot({ path: 'test-results/screenshots/protection.png', fullPage: true });

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on protection page:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on protection page:', issues.networkErrors);
    }
  });

  test('8. INVESTMENTS PAGE - Test investment module', async ({ page }) => {
    console.log('\n=== TESTING INVESTMENTS PAGE ===\n');

    // Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {});

    // Navigate to investments
    await page.goto('http://localhost:5173/investments');
    await page.waitForTimeout(2000);

    await page.screenshot({ path: 'test-results/screenshots/investments.png', fullPage: true });

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on investments page:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on investments page:', issues.networkErrors);
    }
  });

  test('9. RETIREMENT PAGE - Test retirement module', async ({ page }) => {
    console.log('\n=== TESTING RETIREMENT PAGE ===\n');

    // Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {});

    // Navigate to retirement
    await page.goto('http://localhost:5173/retirement');
    await page.waitForTimeout(2000);

    await page.screenshot({ path: 'test-results/screenshots/retirement.png', fullPage: true });

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on retirement page:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on retirement page:', issues.networkErrors);
    }
  });

  test('10. IHT PAGE - Test IHT module', async ({ page }) => {
    console.log('\n=== TESTING IHT PAGE ===\n');

    // Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {});

    // Navigate to IHT
    await page.goto('http://localhost:5173/iht');
    await page.waitForTimeout(2000);

    await page.screenshot({ path: 'test-results/screenshots/iht.png', fullPage: true });

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on IHT page:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on IHT page:', issues.networkErrors);
    }
  });

  test('11. TAX PAGE - Test tax module', async ({ page }) => {
    console.log('\n=== TESTING TAX PAGE ===\n');

    // Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {});

    // Navigate to tax
    await page.goto('http://localhost:5173/tax');
    await page.waitForTimeout(2000);

    await page.screenshot({ path: 'test-results/screenshots/tax.png', fullPage: true });

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on tax page:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on tax page:', issues.networkErrors);
    }
  });

  test('12. GOALS PAGE - Test goals module', async ({ page }) => {
    console.log('\n=== TESTING GOALS PAGE ===\n');

    // Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {});

    // Navigate to goals
    await page.goto('http://localhost:5173/goals');
    await page.waitForTimeout(2000);

    await page.screenshot({ path: 'test-results/screenshots/goals.png', fullPage: true });

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on goals page:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on goals page:', issues.networkErrors);
    }
  });

  test('13. SCENARIOS PAGE - Test scenarios module', async ({ page }) => {
    console.log('\n=== TESTING SCENARIOS PAGE ===\n');

    // Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {});

    // Navigate to scenarios
    await page.goto('http://localhost:5173/scenarios');
    await page.waitForTimeout(2000);

    await page.screenshot({ path: 'test-results/screenshots/scenarios.png', fullPage: true });

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on scenarios page:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on scenarios page:', issues.networkErrors);
    }
  });

  test('14. AI ADVISOR PAGE - Test AI advisor module', async ({ page }) => {
    console.log('\n=== TESTING AI ADVISOR PAGE ===\n');

    // Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {});

    // Navigate to AI advisor
    await page.goto('http://localhost:5173/ai-advisor');
    await page.waitForTimeout(2000);

    await page.screenshot({ path: 'test-results/screenshots/ai-advisor.png', fullPage: true });

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on AI advisor page:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on AI advisor page:', issues.networkErrors);
    }
  });

  test('15. RECOMMENDATIONS PAGE - Test recommendations module', async ({ page }) => {
    console.log('\n=== TESTING RECOMMENDATIONS PAGE ===\n');

    // Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {});

    // Navigate to recommendations
    await page.goto('http://localhost:5173/recommendations');
    await page.waitForTimeout(2000);

    await page.screenshot({ path: 'test-results/screenshots/recommendations.png', fullPage: true });

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on recommendations page:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on recommendations page:', issues.networkErrors);
    }
  });

  test('16. PERSONALIZATION PAGE - Test personalization module', async ({ page }) => {
    console.log('\n=== TESTING PERSONALIZATION PAGE ===\n');

    // Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {});

    // Navigate to personalization (if route exists)
    await page.goto('http://localhost:5173/personalization');
    await page.waitForTimeout(2000);

    await page.screenshot({ path: 'test-results/screenshots/personalization.png', fullPage: true });

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on personalization page:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on personalization page:', issues.networkErrors);
    }
  });

  test('17. PROFILE PAGE - Test profile page', async ({ page }) => {
    console.log('\n=== TESTING PROFILE PAGE ===\n');

    // Login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard', { timeout: 5000 }).catch(() => {});

    // Navigate to profile
    await page.goto('http://localhost:5173/profile');
    await page.waitForTimeout(2000);

    await page.screenshot({ path: 'test-results/screenshots/profile.png', fullPage: true });

    if (issues.consoleErrors.length > 0) {
      console.log('❌ Console errors on profile page:', issues.consoleErrors);
    }
    if (issues.networkErrors.length > 0) {
      console.log('❌ Network errors on profile page:', issues.networkErrors);
    }
  });

  test('18. API ENDPOINTS - Test backend API health', async ({ page }) => {
    console.log('\n=== TESTING API ENDPOINTS ===\n');

    // Test health endpoint
    const healthResponse = await page.request.get('http://localhost:8000/health');
    console.log('Health endpoint status:', healthResponse.status());
    expect(healthResponse.status()).toBe(200);

    const healthBody = await healthResponse.json();
    console.log('Health response:', healthBody);

    // Test API docs
    const docsResponse = await page.request.get('http://localhost:8000/docs');
    console.log('API docs status:', docsResponse.status());

    console.log('✅ API endpoints accessible');
  });
});
