# Phase 5B: Advanced Integrations

**Last Updated:** October 1, 2025
**Timeline:** 2-2.5 months (Part of Phase 5: 6-8 months total)
**Critical Rule:** ⛔ **DO NOT PROCEED TO NEXT SECTION UNTIL ALL TESTS PASS** ⛔

---

## 📋 Overview

**Goal:** Integrate with banks, investment platforms, and pension providers for seamless data syncing

**Prerequisites:** 
- Phase 4 complete
- Phase 5A complete (ML and Additional Jurisdictions functional)

**Module Focus:**
- 5.5-5.7: Advanced External Integrations

**Outputs:**
- Open Banking integration (UK)
- Bank account aggregation and transaction sync
- Investment platform integration
- Real-time portfolio syncing
- Pension Tracing Service integration
- Automated daily data syncing

**Related Files:**
- Previous: `phase5a_ml_jurisdictions_tasks.md` - ML and Jurisdictions
- Next: `phase5c_mobile_scale_tasks.md` - Mobile Apps and Scaling

---

## 🔧 Instructions

**Before starting any task:**
1. Read `.claude/instructions.md` for complete agent delegation rules and testing strategy
2. Each task below marked with 🐍 or ⚛️ shows which agent to use
3. Read all listed "Context Files" before implementing

**Task markers:**
- 🐍 = Delegate to `python-backend-engineer` agent
- ⚛️ = Delegate to `react-coder` agent

**Testing:**
- Backend: `pytest` for all Python code
- Frontend: `Jest` for component tests, `Playwright` for E2E only
- See `.claude/instructions.md` for complete testing strategy

---
## 5.5 Advanced Integrations - Open Banking

### Task 5.5.1: Open Banking Integration (UK)

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `integration.md`, `securityCompliance.md`, `DataManagement.md`

**Agent Instructions:**
1. Read integration.md - Open Banking specifications
2. Read securityCompliance.md for API security and data protection
3. Integrate with UK Open Banking API (via aggregator like TrueLayer or Plaid)

**Tasks:**
- [ ] Set up Open Banking provider (TrueLayer, Plaid, or Yapily)
  - Register application
  - Obtain API credentials
  - Store securely in environment variables
- [ ] Create `services/integrations/open_banking_service.py`
- [ ] Implement `initiate_bank_connection()` method
  - Generate authorization URL for user
  - User authenticates with their bank
  - Receive authorization code and exchange for access token
  - Store encrypted access token and refresh token
  - Return connection status
- [ ] Implement `fetch_accounts()` method
  - Retrieve list of user's bank accounts from provider
  - Return account details (name, type, balance, account number)
- [ ] Implement `fetch_transactions()` method
  - Retrieve transactions for connected accounts
  - Parse transaction data
  - Categorize transactions (groceries, bills, etc.)
  - Store in database
  - Return transactions
- [ ] Implement `fetch_balances()` method
  - Retrieve current balances for all connected accounts
  - Update in database
  - Return balances
- [ ] Implement `sync_accounts()` method (scheduled job)
  - Run daily to fetch latest transactions and balances
  - Update user's financial data
- [ ] Create `connected_bank_accounts` table
  - User_id, provider, bank_name, account_id
  - Account_type, balance, currency
  - Access_token (encrypted), refresh_token (encrypted)
  - Last_sync, created/updated timestamps
- [ ] **Test Suite:**
  - Test bank connection initiation
  - Test account fetching (mock API responses)
  - Test transaction fetching and categorization
  - Test balance syncing
  - Test scheduled sync job
- [ ] **Run:** `pytest tests/services/integrations/test_open_banking.py -v`
- [ ] **Acceptance:** Open Banking integration functional and secure

### Task 5.5.2: Open Banking UI

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `integration.md`, `UserFlows.md`

**Agent Instructions:**
1. Read integration.md - Open Banking user flow
2. Read UserFlows.md for integration UX
3. Create seamless bank connection experience

**Tasks:**
- [ ] Create `components/integrations/BankConnectionFlow.jsx`
  - Import UI components from 'internal-packages/ui'
  - "Connect Bank" button
  - Clicking opens authorization flow (redirect to bank)
  - After authorization, redirect back to app
  - Display connected accounts
  - Show sync status and last sync time
  - "Disconnect" option
- [ ] Create `components/integrations/ConnectedAccounts.jsx`
  - List all connected bank accounts
  - Display balance for each
  - Show recent transactions
  - Manual sync button
- [ ] Update `components/savings/SavingsAccounts.jsx`
  - Show both manual and connected accounts
  - Differentiate with badge (🔗 for connected)
  - Auto-update balances from connected accounts
- [ ] **Jest Tests:**
  - Test bank connection flow
  - Test connected accounts display
  - Test sync functionality
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/BankConnectionFlow.test.jsx`
- [ ] **E2E Test (Playwright):** `npx playwright test e2e/open-banking.spec.js`
- [ ] **Acceptance:** Users can connect banks and auto-sync transactions

---

## 5.6 Advanced Integrations - Investment Platforms

### Task 5.6.1: Investment Platform Integration

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `integration.md`, `Investment.md`

**Agent Instructions:**
1. Read integration.md - Investment platform integration specs
2. Integrate with investment platforms (e.g., Vanguard API, Trading 212, Hargreaves Lansdown)
3. Enable real-time portfolio syncing

**Tasks:**
- [ ] Set up investment platform API access
  - Register with platforms
  - Obtain API credentials
- [ ] Create `services/integrations/investment_platform_service.py`
- [ ] Implement `connect_investment_account()` method
  - User authorizes platform connection
  - Store encrypted access credentials
  - Return connection status
- [ ] Implement `sync_portfolio()` method
  - Fetch current holdings from platform
  - Update holdings in database
  - Fetch current prices
  - Recalculate unrealized gains
  - Return updated portfolio
- [ ] Implement `sync_transactions()` method
  - Fetch buy/sell transactions from platform
  - Store in investment_transactions table
  - Update holdings accordingly
- [ ] Implement scheduled sync (daily)
- [ ] Create `connected_investment_accounts` table
  - User_id, platform, account_id
  - Access_token (encrypted), last_sync
- [ ] **Test Suite:**
  - Test investment account connection
  - Test portfolio syncing
  - Test transaction syncing
  - Mock API responses
- [ ] **Run:** `pytest tests/services/integrations/test_investment_platform.py -v`
- [ ] **Acceptance:** Investment platforms integrated with auto-sync

### Task 5.6.2: Investment Platform UI

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `integration.md`, `UserFlows.md`

**Agent Instructions:**
1. Create UI for connecting investment platforms

**Tasks:**
- [ ] Create `components/integrations/InvestmentPlatformConnection.jsx`
  - Import UI components from 'internal-packages/ui'
  - List supported platforms (with logos)
  - "Connect" button for each platform
  - Authorization flow
  - Display connected status
- [ ] Update `components/investment/PortfolioDashboard.jsx`
  - Show synced portfolios alongside manual entries
  - Display last sync time
  - Manual sync button
  - Differentiate synced holdings with badge
- [ ] **Jest Tests:**
  - Test platform connection flow
  - Test portfolio display with synced data
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/InvestmentPlatformConnection.test.jsx`
- [ ] **Acceptance:** Users can connect investment platforms and auto-sync portfolios

---

## 5.7 Advanced Integrations - Pension Providers

### Task 5.7.1: Pension Provider Integration (UK)

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `integration.md`, `Retirement.md`

**Agent Instructions:**
1. Read integration.md - Pension provider integration
2. Integrate with UK pension providers (Pension Finder Service or direct APIs where available)

**Tasks:**
- [ ] Implement Pension Tracing Service integration
  - Use UK government Pension Tracing Service
  - Search for lost pensions by user details
  - Return list of pension schemes
- [ ] Create `services/integrations/pension_provider_service.py`
- [ ] Implement `find_pensions()` method
  - Search for user's pensions
  - Return list of found schemes with contact details
- [ ] Implement `request_pension_statement()` method
  - For supported providers, request current value via API
  - Store pension details
- [ ] Note: Direct integration limited due to lack of open APIs
  - Focus on Pension Tracing Service for finding pensions
  - Manual entry for values (until more APIs available)
- [ ] **Test Suite:**
  - Test pension search
  - Test data parsing
  - Mock API responses
- [ ] **Run:** `pytest tests/services/integrations/test_pension_provider.py -v`
- [ ] **Acceptance:** Pension Tracing Service integrated to help users find lost pensions

---

## 🚦 PHASE 5 INTEGRATIONS TESTING GATE

### Security Tests (CRITICAL)

- [ ] ✅ Bank access tokens encrypted
- [ ] ✅ Investment platform credentials encrypted
- [ ] ✅ API credentials stored securely
- [ ] ✅ OAuth flows secure
- [ ] ✅ User can revoke connections

### Functional Tests

- [ ] ✅ Open Banking connection working
- [ ] ✅ Transactions fetched and categorized
- [ ] ✅ Balances synced daily
- [ ] ✅ Investment platform connection working
- [ ] ✅ Portfolio synced accurately
- [ ] ✅ Pension Tracing Service integrated

### Integration Tests

- [ ] ✅ Full journey: Connect bank → View transactions → Auto-categorize → Update budget
- [ ] ✅ Full journey: Connect investment platform → Sync portfolio → View updated allocation

### Code Quality

- [ ] ✅ Test coverage >80% for integrations
- [ ] ✅ All linting passes
- [ ] ✅ API documentation complete

**Acceptance Criteria:**
🎯 Platform integrates with banks, investment platforms, and pension providers for seamless data syncing

---


**Next Step:**
➡️ Proceed to `phase5c_mobile_scale_tasks.md` to build Mobile Apps and Performance Optimization

---
