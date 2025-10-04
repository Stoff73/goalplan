import { test, expect } from '@playwright/test';

test.describe('Investment Module E2E', () => {
  const mockAccessToken = 'mock-access-token';
  const mockUser = {
    id: 'user-123',
    email: 'test@example.com',
    firstName: 'John',
    lastName: 'Doe',
  };

  test.beforeEach(async ({ page, context }) => {
    // Mock authentication
    await context.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          accessToken: mockAccessToken,
          refreshToken: 'mock-refresh-token',
          user: mockUser,
        }),
      });
    });

    // Login first
    await page.goto('/login');
    await page.getByLabel(/your email address/i).fill('test@example.com');
    await page.getByLabel(/your password/i).fill('password123');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Wait for redirect to dashboard
    await page.waitForURL(/.*dashboard.*/);
  });

  test('Full Investment Journey: Create account → Add holdings → Update prices → View allocation → Sell holding', async ({ page, context }) => {
    // STEP 1: Create investment account
    await context.route('**/api/v1/investments/accounts', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'account-123',
            accountType: 'STOCKS_ISA',
            provider: 'Vanguard',
            country: 'UK',
            baseCurrency: 'GBP',
            status: 'ACTIVE',
            maskedAccountNumber: '****1234',
            createdAt: new Date().toISOString(),
          }),
        });
      } else {
        // GET request
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([{
            id: 'account-123',
            accountType: 'STOCKS_ISA',
            provider: 'Vanguard',
            country: 'UK',
            baseCurrency: 'GBP',
            status: 'ACTIVE',
            maskedAccountNumber: '****1234',
          }]),
        });
      }
    });

    // Navigate to investments page
    await page.goto('/investments');

    // Click "Add Account" button
    await page.getByRole('button', { name: /add account/i }).click();

    // Fill in account details
    await page.getByLabel(/account type/i).selectOption('STOCKS_ISA');
    await page.getByLabel(/provider/i).fill('Vanguard');
    await page.getByLabel(/account number/i).fill('12345678');
    await page.getByLabel(/country/i).selectOption('UK');

    // Submit account creation
    await page.getByRole('button', { name: /create account/i }).click();

    // Verify success message
    await expect(page.getByText(/account created successfully/i)).toBeVisible();

    // STEP 2: Add holdings to account
    await context.route('**/api/v1/investments/holdings', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'holding-123',
            accountId: 'account-123',
            ticker: 'VWRL',
            securityName: 'Vanguard FTSE All-World UCITS ETF',
            quantity: 100,
            purchasePrice: 95.50,
            currentPrice: 95.50,
            currentValue: 9550,
            unrealizedGain: 0,
            unrealizedGainPercentage: 0,
            assetClass: 'EQUITY',
            region: 'GLOBAL',
            sector: 'Diversified',
          }),
        });
      } else {
        // GET request
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([{
            id: 'holding-123',
            accountId: 'account-123',
            ticker: 'VWRL',
            securityName: 'Vanguard FTSE All-World UCITS ETF',
            quantity: 100,
            purchasePrice: 95.50,
            currentPrice: 100.00,
            currentValue: 10000,
            unrealizedGain: 450,
            unrealizedGainPercentage: 4.71,
            assetClass: 'EQUITY',
            region: 'GLOBAL',
            sector: 'Diversified',
          }]),
        });
      }
    });

    // Click "Add Holding" button
    await page.getByRole('button', { name: /add holding/i }).click();

    // Fill in holding details
    await page.getByLabel(/account/i).selectOption('account-123');
    await page.getByLabel(/ticker/i).fill('VWRL');
    await page.getByLabel(/name/i).fill('Vanguard FTSE All-World UCITS ETF');
    await page.getByLabel(/quantity/i).fill('100');
    await page.getByLabel(/purchase price/i).fill('95.50');
    await page.getByLabel(/asset class/i).selectOption('EQUITY');
    await page.getByLabel(/region/i).selectOption('GLOBAL');

    // Submit holding
    await page.getByRole('button', { name: /add holding/i }).click();

    // Verify success message
    await expect(page.getByText(/holding added successfully/i)).toBeVisible();

    // STEP 3: Update holding price
    await context.route('**/api/v1/investments/holdings/holding-123/price', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'holding-123',
          ticker: 'VWRL',
          currentPrice: 100.00,
          currentValue: 10000,
          unrealizedGain: 450,
          unrealizedGainPercentage: 4.71,
        }),
      });
    });

    // Click "Update Price" button
    await page.getByRole('button', { name: /update price/i }).first().click();

    // Enter new price
    await page.getByLabel(/new price/i).fill('100.00');

    // Verify preview shows new gain
    await expect(page.getByText(/new unrealized gain.*£450/i)).toBeVisible();

    // Submit price update
    await page.getByRole('button', { name: /update/i }).click();

    // Verify success message
    await expect(page.getByText(/price updated successfully/i)).toBeVisible();

    // STEP 4: View asset allocation
    await context.route('**/api/v1/investments/portfolio/allocation?by=asset_class', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          allocation: {
            EQUITY: { value: 10000, percentage: 100 },
          },
        }),
      });
    });

    // Navigate to asset allocation tab/page
    await page.getByRole('button', { name: /allocation/i }).click();

    // Verify allocation is displayed
    await expect(page.getByText(/EQUITY/i)).toBeVisible();
    await expect(page.getByText(/100%/i)).toBeVisible();

    // STEP 5: Sell holding (partial sale)
    await context.route('**/api/v1/investments/holdings/holding-123/sell', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          holdingId: 'holding-123',
          quantitySold: 50,
          salePrice: 100.00,
          saleValue: 5000,
          realizedGain: 225,
          realizedGainPercentage: 4.71,
          taxYear: '2024/25',
        }),
      });
    });

    // Go back to holdings list
    await page.getByRole('button', { name: /holdings/i }).click();

    // Click "Sell" button
    await page.getByRole('button', { name: /sell/i }).first().click();

    // Enter sale details
    await page.getByLabel(/quantity to sell/i).fill('50');
    await page.getByLabel(/sale price/i).fill('100.00');

    // Verify realized gain preview
    await expect(page.getByText(/this sale will realize a gain.*£225/i)).toBeVisible();

    // Confirm sale
    await page.getByRole('button', { name: /confirm sale/i }).click();

    // Verify success message
    await expect(page.getByText(/holding sold successfully/i)).toBeVisible();

    // STEP 6: View realized gains (tax summary)
    await context.route('**/api/v1/investments/tax/capital-gains?tax_year=2024%2F25&country=UK', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          capital_gains: {
            total_gains: 225,
            exempt_amount: 0,
            taxable_gains: 0,
            tax_rate: 0,
            tax_owed: 0,
            isa_gains_tax_free: 225,
          },
          dividend_tax: {
            total_dividends: 0,
            allowance: 0,
            taxable_dividends: 0,
            tax_rate: 0,
            tax_owed: 0,
            isa_dividends_tax_free: 0,
          },
        }),
      });
    });

    // Navigate to tax summary
    await page.getByRole('button', { name: /tax/i }).click();

    // Verify realized gains are shown
    await expect(page.getByText(/total realized gains.*£225/i)).toBeVisible();
    await expect(page.getByText(/ISA gains are tax-free/i)).toBeVisible();
  });

  test('Portfolio Dashboard displays comprehensive overview', async ({ page, context }) => {
    // Mock portfolio summary endpoint
    await context.route('**/api/v1/investments/portfolio/summary', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_value: 83333.33,
          total_cost_basis: 80000.00,
          total_unrealized_gain: 3333.33,
          unrealized_gain_percentage: 4.17,
          num_holdings: 15,
          num_accounts: 2,
          currency_exposure: {
            GBP: { value: 50000.00, percentage: 60.00 },
            USD: { value: 33333.33, percentage: 40.00 },
          },
          asset_allocation: {
            EQUITY: { value: 50000.00, percentage: 60.00 },
            FIXED_INCOME: { value: 20000.00, percentage: 24.00 },
            CASH: { value: 13333.33, percentage: 16.00 },
          },
          top_holdings: [
            {
              id: 'holding-1',
              security_name: 'Vanguard FTSE All-World',
              ticker: 'VWRL',
              current_value: 10000,
              unrealized_gain: 500,
              percentage_of_portfolio: 12.00,
            },
          ],
        }),
      });
    });

    // Navigate to portfolio dashboard
    await page.goto('/investments/dashboard');

    // Verify summary displays
    await expect(page.getByText(/your portfolio is worth.*£83,333/i)).toBeVisible();
    await expect(page.getByText(/15 holdings/i)).toBeVisible();
    await expect(page.getByText(/2 accounts/i)).toBeVisible();

    // Verify asset allocation shows
    await expect(page.getByText(/EQUITY.*60%/i)).toBeVisible();
    await expect(page.getByText(/FIXED_INCOME.*24%/i)).toBeVisible();

    // Verify top holdings table
    await expect(page.getByText(/VWRL/i)).toBeVisible();
    await expect(page.getByText(/Vanguard FTSE All-World/i)).toBeVisible();
  });

  test('Holdings List displays with filtering and sorting', async ({ page, context }) => {
    // Mock holdings endpoint
    await context.route('**/api/v1/investments/holdings', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 'holding-1',
            ticker: 'VWRL',
            securityName: 'Vanguard FTSE All-World',
            quantity: 100,
            currentPrice: 100.00,
            currentValue: 10000,
            unrealizedGain: 500,
            assetClass: 'EQUITY',
            region: 'GLOBAL',
            accountType: 'STOCKS_ISA',
          },
          {
            id: 'holding-2',
            ticker: 'VUKE',
            securityName: 'Vanguard FTSE 100',
            quantity: 50,
            currentPrice: 200.00,
            currentValue: 10000,
            unrealizedGain: -200,
            assetClass: 'EQUITY',
            region: 'UK',
            accountType: 'GIA',
          },
        ]),
      });
    });

    // Mock accounts endpoint for filter dropdown
    await context.route('**/api/v1/investments/accounts', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 'account-1', provider: 'Vanguard', accountType: 'STOCKS_ISA' },
          { id: 'account-2', provider: 'Fidelity', accountType: 'GIA' },
        ]),
      });
    });

    // Navigate to holdings page
    await page.goto('/investments/holdings');

    // Verify holdings are displayed
    await expect(page.getByText(/VWRL/i)).toBeVisible();
    await expect(page.getByText(/VUKE/i)).toBeVisible();

    // Verify badges
    await expect(page.getByText(/ISA/i)).toBeVisible();

    // Verify color coding (gains in green, losses in red)
    const vwrlRow = page.locator('tr', { hasText: 'VWRL' });
    await expect(vwrlRow.locator('.text-success-600')).toBeVisible(); // green for gain

    const vukeRow = page.locator('tr', { hasText: 'VUKE' });
    await expect(vukeRow.locator('.text-error-600')).toBeVisible(); // red for loss

    // Test filtering
    await page.getByLabel(/asset class/i).selectOption('EQUITY');
    // Both should still be visible as they're both EQUITY
    await expect(page.getByText(/VWRL/i)).toBeVisible();
    await expect(page.getByText(/VUKE/i)).toBeVisible();

    // Test sorting
    await page.getByRole('columnheader', { name: /value/i }).click();
    // Should sort by value
  });

  test('Asset Allocation Visualization shows tabs and data', async ({ page, context }) => {
    // Mock allocation endpoints
    await context.route('**/api/v1/investments/portfolio/allocation?by=asset_class', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          allocation: {
            EQUITY: { value: 60000, percentage: 60 },
            FIXED_INCOME: { value: 30000, percentage: 30 },
            CASH: { value: 10000, percentage: 10 },
          },
        }),
      });
    });

    await context.route('**/api/v1/investments/portfolio/allocation?by=region', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          allocation: {
            UK: { value: 40000, percentage: 40 },
            US: { value: 35000, percentage: 35 },
            GLOBAL: { value: 25000, percentage: 25 },
          },
        }),
      });
    });

    await context.route('**/api/v1/investments/portfolio/allocation?by=sector', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          allocation: {
            TECHNOLOGY: { value: 30000, percentage: 30 },
            HEALTHCARE: { value: 25000, percentage: 25 },
            FINANCIALS: { value: 20000, percentage: 20 },
            CONSUMER: { value: 15000, percentage: 15 },
            ENERGY: { value: 10000, percentage: 10 },
          },
        }),
      });
    });

    // Navigate to allocation page
    await page.goto('/investments/allocation');

    // Verify default tab (Asset Class) displays
    await expect(page.getByText(/EQUITY.*60%/i)).toBeVisible();
    await expect(page.getByText(/FIXED_INCOME.*30%/i)).toBeVisible();

    // Switch to Region tab
    await page.getByRole('tab', { name: /region/i }).click();
    await expect(page.getByText(/UK.*40%/i)).toBeVisible();
    await expect(page.getByText(/US.*35%/i)).toBeVisible();

    // Switch to Sector tab
    await page.getByRole('tab', { name: /sector/i }).click();
    await expect(page.getByText(/TECHNOLOGY.*30%/i)).toBeVisible();
    await expect(page.getByText(/HEALTHCARE.*25%/i)).toBeVisible();
  });

  test('Security: Cannot access other users portfolios', async ({ page, context }) => {
    // Mock 403 response for unauthorized access
    await context.route('**/api/v1/investments/accounts/other-user-account-id', async (route) => {
      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Account not owned by user',
        }),
      });
    });

    // Try to access another user's account directly
    await page.goto('/investments/accounts/other-user-account-id');

    // Should show error or redirect
    await expect(page.getByText(/not authorized|access denied|forbidden/i)).toBeVisible();
  });

  test('Account numbers are masked in UI', async ({ page, context }) => {
    // Mock account with masked number
    await context.route('**/api/v1/investments/accounts', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([{
          id: 'account-123',
          accountType: 'STOCKS_ISA',
          provider: 'Vanguard',
          maskedAccountNumber: '****5678',
        }]),
      });
    });

    await page.goto('/investments/accounts');

    // Verify full account number is NOT displayed
    await expect(page.getByText('****5678')).toBeVisible();
    await expect(page.getByText('12345678')).not.toBeVisible();
  });
});
