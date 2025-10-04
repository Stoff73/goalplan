import { test, expect } from '@playwright/test';

/**
 * Visual Walkthrough E2E Test
 *
 * This test walks through the entire application with visual feedback
 */

test.describe('GoalPlan - Visual Application Walkthrough', () => {
  test('Complete Application Walkthrough', async ({ page }) => {
    const findings = [];
    const screenshot = async (name) => {
      await page.screenshot({ path: `test-results/screenshots/${name}.png`, fullPage: true });
    };

    // ===== STEP 1: Home Page =====
    await test.step('1. Navigate to home page', async () => {
      await page.goto('/');
      await page.waitForTimeout(2000);
      await screenshot('01-home-page');

      const currentUrl = page.url();
      findings.push({
        step: 'Home Page',
        url: '/',
        redirectsTo: currentUrl,
        status: currentUrl.includes('/login') ? '✅ PASS' : '⚠️ UNEXPECTED',
        note: `Should redirect to /login. Actual: ${currentUrl}`
      });

      console.log(`✓ Step 1: Home redirects to ${currentUrl}`);
    });

    // ===== STEP 2: Login Page =====
    await test.step('2. Check login page', async () => {
      await page.goto('/login');
      await page.waitForTimeout(2000);
      await screenshot('02-login-page');

      const hasEmailInput = await page.locator('input[name="email"]').count() > 0;
      const hasPasswordInput = await page.locator('input[type="password"]').count() > 0;
      const hasSubmitButton = await page.locator('button[type="submit"]').count() > 0;

      findings.push({
        step: 'Login Page',
        url: '/login',
        hasEmailInput,
        hasPasswordInput,
        hasSubmitButton,
        status: (hasEmailInput && hasPasswordInput && hasSubmitButton) ? '✅ PASS' : '❌ FAIL',
        note: 'Login form elements'
      });

      console.log(`✓ Step 2: Login page - Email: ${hasEmailInput}, Password: ${hasPasswordInput}, Submit: ${hasSubmitButton}`);
    });

    // ===== STEP 3: Registration Page =====
    await test.step('3. Check registration page', async () => {
      await page.goto('/register');
      await page.waitForTimeout(2000);
      await screenshot('03-registration-page');

      const pageText = await page.textContent('body');
      const hasForm = await page.locator('form').count() > 0;
      const hasEmailInput = await page.locator('input[name="email"]').count() > 0;
      const hasPasswordInput = await page.locator('input[name="password"]').count() > 0;
      const hasTermsCheckbox = await page.locator('input[name="termsAccepted"]').count() > 0;

      findings.push({
        step: 'Registration Page',
        url: '/register',
        hasForm,
        hasEmailInput,
        hasPasswordInput,
        hasTermsCheckbox,
        status: hasForm ? '✅ PASS' : '❌ FAIL',
        note: 'Registration form present'
      });

      console.log(`✓ Step 3: Registration page loaded with form: ${hasForm}`);
    });

    // ===== STEP 4: Protected Pages (Unauthenticated) =====
    await test.step('4. Test protected pages without authentication', async () => {
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
        await page.waitForTimeout(1000);

        const currentUrl = page.url();
        const pageText = await page.textContent('body');
        const hasContent = pageText.length > 100;
        const redirectsToLogin = currentUrl.includes('/login');

        // Take screenshot of each page
        const safeName = pagePath.replace('/', '');
        await screenshot(`04-protected-${safeName || 'root'}`);

        findings.push({
          step: `Protected Page: ${pagePath}`,
          url: pagePath,
          finalUrl: currentUrl,
          redirectsToLogin,
          hasContent,
          contentLength: pageText.length,
          status: redirectsToLogin ? '✅ REDIRECTS' : hasContent ? '⚠️ NO AUTH' : '❌ FAIL',
          note: redirectsToLogin ? 'Correctly redirects to login' : hasContent ? 'Shows content without auth (security issue?)' : 'No content'
        });

        console.log(`  ${pagePath}: ${redirectsToLogin ? 'Redirects to login' : `Shows content (${pageText.length} chars)`}`);
      }

      console.log(`✓ Step 4: Tested ${protectedPages.length} protected pages`);
    });

    // ===== STEP 5: API Health Check =====
    await test.step('5. Check API endpoints', async () => {
      try {
        const docsResponse = await page.request.get('http://localhost:8000/docs');
        findings.push({
          step: 'API Docs Endpoint',
          url: 'http://localhost:8000/docs',
          status: docsResponse.ok() ? '✅ PASS' : '❌ FAIL',
          httpStatus: docsResponse.status(),
          note: `API documentation ${docsResponse.ok() ? 'accessible' : 'not accessible'}`
        });

        console.log(`✓ Step 5: API docs accessible (${docsResponse.status()})`);
      } catch (error) {
        findings.push({
          step: 'API Docs Endpoint',
          status: '❌ FAIL',
          error: error.message
        });
        console.log(`✗ Step 5: API docs failed - ${error.message}`);
      }
    });

    // ===== STEP 6: Check for JavaScript Errors =====
    await test.step('6. Scan for JavaScript errors', async () => {
      const jsErrors = [];

      page.on('console', msg => {
        if (msg.type() === 'error') {
          jsErrors.push(msg.text());
        }
      });

      page.on('pageerror', error => {
        jsErrors.push(error.message);
      });

      // Navigate through key pages to trigger any errors
      const pages = ['/login', '/register', '/dashboard', '/savings'];
      for (const p of pages) {
        await page.goto(p);
        await page.waitForTimeout(500);
      }

      findings.push({
        step: 'JavaScript Errors',
        totalErrors: jsErrors.length,
        status: jsErrors.length === 0 ? '✅ PASS' : '⚠️ ERRORS FOUND',
        errors: jsErrors.slice(0, 5), // Show first 5
        note: jsErrors.length === 0 ? 'No JavaScript errors' : `Found ${jsErrors.length} errors`
      });

      console.log(`✓ Step 6: JavaScript errors: ${jsErrors.length}`);
    });

    // ===== FINAL REPORT =====
    await test.step('7. Generate final report', async () => {
      console.log('\n\n');
      console.log('═'.repeat(100));
      console.log('                    GOALPLAN E2E VISUAL WALKTHROUGH REPORT');
      console.log('═'.repeat(100));
      console.log('\n');

      findings.forEach((finding, idx) => {
        console.log(`${idx + 1}. ${finding.step}`);
        console.log(`   Status: ${finding.status}`);
        if (finding.url) console.log(`   URL: ${finding.url}`);
        if (finding.finalUrl && finding.finalUrl !== finding.url) {
          console.log(`   Final URL: ${finding.finalUrl}`);
        }
        if (finding.note) console.log(`   Note: ${finding.note}`);

        // Print additional details
        Object.keys(finding).forEach(key => {
          if (!['step', 'status', 'url', 'finalUrl', 'note'].includes(key)) {
            console.log(`   ${key}: ${JSON.stringify(finding[key])}`);
          }
        });
        console.log('');
      });

      console.log('═'.repeat(100));
      console.log('SUMMARY');
      console.log('═'.repeat(100));
      const passed = findings.filter(f => f.status && f.status.includes('PASS')).length;
      const failed = findings.filter(f => f.status && f.status.includes('FAIL')).length;
      const warnings = findings.filter(f => f.status && (f.status.includes('WARN') || f.status.includes('UNEXPECTED'))).length;

      console.log(`Total Tests: ${findings.length}`);
      console.log(`Passed: ${passed} ✅`);
      console.log(`Failed: ${failed} ❌`);
      console.log(`Warnings: ${warnings} ⚠️`);
      console.log(`Success Rate: ${((passed / findings.length) * 100).toFixed(1)}%`);
      console.log('\n');
      console.log('Screenshots saved to: test-results/screenshots/');
      console.log('═'.repeat(100));
      console.log('\n\n');
    });
  });
});
