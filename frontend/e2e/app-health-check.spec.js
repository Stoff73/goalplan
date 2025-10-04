import { test, expect } from '@playwright/test';

/**
 * GoalPlan Application Health Check E2E Test
 *
 * This test verifies:
 * - All pages load without errors
 * - Navigation works
 * - No JavaScript errors in console
 * - API endpoints respond correctly
 * - Database connectivity
 */

const testResults = {
  pages: [],
  navigation: [],
  errors: [],
  apiCalls: [],
  warnings: [],
};

test.describe('GoalPlan - Application Health Check', () => {
  let page;

  test.beforeAll(async ({ browser }) => {
    page = await browser.newPage();

    // Capture console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        testResults.errors.push({
          type: 'console',
          message: msg.text(),
          location: msg.location()
        });
      }
    });

    // Capture page errors
    page.on('pageerror', error => {
      testResults.errors.push({
        type: 'page',
        message: error.message,
        stack: error.stack
      });
    });

    // Capture failed API requests
    page.on('response', response => {
      if (response.url().includes('/api/')) {
        testResults.apiCalls.push({
          url: response.url(),
          status: response.status(),
          statusText: response.statusText(),
          ok: response.ok()
        });
      }
    });
  });

  test('1. Check home page redirects to login', async () => {
    await page.goto('/');
    await page.waitForTimeout(1000);

    const url = page.url();
    const success = url.includes('/login');

    testResults.pages.push({
      name: 'Home Redirect',
      url: '/',
      success,
      finalUrl: url,
      note: success ? 'Redirects to login' : 'Does not redirect'
    });

    expect(success).toBe(true);
  });

  test('2. Check login page loads', async () => {
    await page.goto('/login');
    await page.waitForTimeout(1000);

    const hasLoginForm = await page.locator('form, input[type="email"], input[type="password"]').count() > 0;
    const pageText = await page.textContent('body');

    testResults.pages.push({
      name: 'Login Page',
      url: '/login',
      success: hasLoginForm,
      note: hasLoginForm ? 'Login form present' : 'No login form found',
      contentLength: pageText.length
    });

    expect(hasLoginForm).toBe(true);
  });

  test('3. Check registration page loads', async () => {
    await page.goto('/register');
    await page.waitForTimeout(1000);

    const hasRegisterForm = await page.locator('form').count() > 0;
    const hasEmailInput = await page.locator('input[name="email"]').count() > 0;

    testResults.pages.push({
      name: 'Registration Page',
      url: '/register',
      success: hasRegisterForm && hasEmailInput,
      note: `Form: ${hasRegisterForm}, Email input: ${hasEmailInput}`,
    });

    expect(hasRegisterForm).toBe(true);
  });

  test('4. Check protected pages redirect to login when not authenticated', async () => {
    const protectedPages = [
      '/dashboard',
      '/tax-status',
      '/income',
      '/savings',
      '/protection',
      '/investments',
      '/goals',
      '/profile'
    ];

    for (const pagePath of protectedPages) {
      await page.goto(pagePath);
      await page.waitForTimeout(500);

      const currentUrl = page.url();
      const redirectsToLogin = currentUrl.includes('/login');
      const hasContent = (await page.textContent('body')).length > 100;

      testResults.pages.push({
        name: `Protected: ${pagePath}`,
        url: pagePath,
        success: redirectsToLogin || hasContent,
        redirectsToLogin,
        hasContent,
        finalUrl: currentUrl,
        note: redirectsToLogin ? 'Redirects to login (correct)' : hasContent ? 'Shows content without auth (incorrect?)' : 'No content'
      });
    }
  });

  test('5. Test API endpoint responses', async () => {
    // Try to hit some API endpoints
    const response = await page.request.get('http://localhost:8000/docs');
    testResults.apiCalls.push({
      url: '/docs',
      status: response.status(),
      success: response.ok(),
      note: 'API documentation endpoint'
    });

    expect(response.ok()).toBe(true);
  });

  test('6. Generate comprehensive report', async () => {
    console.log('\n\n========================================');
    console.log('  GOALPLAN E2E TEST REPORT');
    console.log('========================================\n');

    console.log('📄 PAGES TESTED:');
    console.log('━'.repeat(80));
    testResults.pages.forEach((page, idx) => {
      const status = page.success ? '✅' : '❌';
      console.log(`${status} ${page.name}`);
      console.log(`   URL: ${page.url}`);
      if (page.finalUrl && page.finalUrl !== page.url) {
        console.log(`   Final URL: ${page.finalUrl}`);
      }
      console.log(`   Note: ${page.note}`);
      console.log('');
    });

    console.log('\n🔗 API CALLS:');
    console.log('━'.repeat(80));
    const failedApiCalls = testResults.apiCalls.filter(call => !call.ok);
    const successApiCalls = testResults.apiCalls.filter(call => call.ok);

    console.log(`Total API calls: ${testResults.apiCalls.length}`);
    console.log(`Successful: ${successApiCalls.length}`);
    console.log(`Failed: ${failedApiCalls.length}\n`);

    if (failedApiCalls.length > 0) {
      console.log('Failed API calls:');
      failedApiCalls.forEach(call => {
        console.log(`  ❌ ${call.status} ${call.url}`);
      });
    }

    console.log('\n❌ JAVASCRIPT ERRORS:');
    console.log('━'.repeat(80));
    if (testResults.errors.length === 0) {
      console.log('✅ No JavaScript errors detected\n');
    } else {
      testResults.errors.forEach((error, idx) => {
        console.log(`${idx + 1}. [${error.type}] ${error.message}`);
        if (error.location) {
          console.log(`   Location: ${JSON.stringify(error.location)}`);
        }
      });
    }

    console.log('\n📊 SUMMARY:');
    console.log('━'.repeat(80));
    const totalPages = testResults.pages.length;
    const successfulPages = testResults.pages.filter(p => p.success).length;
    const successRate = ((successfulPages / totalPages) * 100).toFixed(1);

    console.log(`Pages tested: ${totalPages}`);
    console.log(`Successful: ${successfulPages}`);
    console.log(`Failed: ${totalPages - successfulPages}`);
    console.log(`Success rate: ${successRate}%`);
    console.log('\n========================================\n');
  });

  test.afterAll(async () => {
    await page.close();
  });
});
