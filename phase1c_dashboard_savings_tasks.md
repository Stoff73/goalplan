# Phase 1C: Central Dashboard & Savings Module

**Last Updated:** October 1, 2025
**Timeline:** 1-1.5 months (Part of Phase 1: 3-4 months total)
**Critical Rule:** ⛔ **PHASE 1 TESTING GATE MUST PASS BEFORE PHASE 2** ⛔

---

## 📋 Overview

**Goal:** Build central dashboard with net worth aggregation and first financial module (savings accounts)

**Prerequisites:** 
- Phase 0 complete (development environment operational)
- Phase 1A complete (Authentication system functional)
- Phase 1B complete (User Information Management functional)

**Module Focus:**
- 1.8: Central Dashboard
- 1.9: Savings Module

**Outputs:**
- Central Dashboard with net worth visualization
- Asset and liability aggregation
- Real-time net worth calculation
- Savings accounts management (Cash, ISA, TFSA)
- ISA and TFSA allowance tracking
- Multi-currency account support
- Dashboard widgets and charts

**Related Files:**
- Previous: `phase1a_authentication_tasks.md` - Authentication System
- Previous: `phase1b_user_info_tasks.md` - User Information Management
- Next (after Phase 1 complete): `phase2a_protection_tasks.md` - Protection Module

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
## 1.8 Central Dashboard

### Task 1.8.1: Dashboard Data Aggregation Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `CentralDashboard.md`, `performance.md`, `DataManagement.md`

**Agent Instructions:**
1. Read CentralDashboard.md - Feature 3.1 complete section
2. Read performance.md for dashboard load time (<2 seconds)
3. Aggregate data from all modules
4. Implement caching strategy

**Tasks:**
- [ ] Create dashboard aggregation service
- [ ] Fetch data from all modules (savings will be only module in Phase 1)
- [ ] Convert all amounts to base currency
- [ ] Calculate total assets
- [ ] Calculate total liabilities
- [ ] Calculate net worth
- [ ] Group by country, asset class, currency
- [ ] Implement Redis caching (5 min TTL)
- [ ] **Test Suite:**
  - Test data aggregation from multiple sources
  - Test currency conversion
  - Test net worth calculation
  - Test grouping by country/asset class
  - Test caching mechanism
  - Test performance (<2 seconds)
- [ ] **Run:** `pytest tests/services/test_dashboard_aggregation.py -v`
- [ ] **Acceptance:** Dashboard aggregation fast and accurate

### Task 1.8.2: Net Worth Snapshot Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `CentralDashboard.md`, `DataManagement.md`

**Agent Instructions:**
1. Read CentralDashboard.md for snapshot requirements
2. Create daily snapshots for trend tracking
3. Implement background job for snapshot creation
4. Retain 2 years of daily snapshots

**Tasks:**
- [ ] Create `net_worth_snapshots` table
- [ ] Create snapshot generation service
- [ ] Implement daily snapshot job (background task)
- [ ] Store snapshot with all breakdown data
- [ ] Calculate changes (day, month, year)
- [ ] **Test Suite:**
  - Test snapshot creation
  - Test snapshot contains all required data
  - Test change calculations
  - Test historical snapshot retrieval
- [ ] **Run:** `pytest tests/services/test_net_worth_snapshot.py -v`
- [ ] **Acceptance:** Snapshots track net worth over time

### Task 1.8.3: Dashboard Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `CentralDashboard.md`, `performance.md`

**Agent Instructions:**
1. Read CentralDashboard.md - Implementation Approach section
2. Implement exact response structure from spec
3. Support base currency parameter
4. Use caching for performance

**Tasks:**
- [ ] Create `GET /api/v1/dashboard/net-worth` endpoint
- [ ] Accept baseCurrency query parameter
- [ ] Accept asOfDate query parameter
- [ ] Return net worth summary
- [ ] Return breakdown by country
- [ ] Return breakdown by asset class
- [ ] Return breakdown by currency
- [ ] Return trend data (last 12 months)
- [ ] Return changes (day, month, year)
- [ ] Implement caching
- [ ] **Test Suite:**
  - Test dashboard data retrieval
  - Test base currency conversion
  - Test historical date query
  - Test all breakdowns present
  - Test trend data
  - Test change calculations
  - Test caching
- [ ] **Run:** `pytest tests/api/dashboard/test_net_worth.py -v`
- [ ] **Acceptance:** Dashboard endpoint returns complete data

### Task 1.8.4: Dashboard UI Components

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `CentralDashboard.md`, `UserFlows.md`, `performance.md`

**Agent Instructions:**
1. Read CentralDashboard.md - User Flow section
2. Read UserFlows.md for dashboard UX principles
3. Read performance.md for loading requirements (<2 sec)
4. Import UI components from 'internal-packages/ui'
5. Use Chart.js or Recharts for visualizations
6. Write comprehensive Jest tests

**Tasks:**
- [ ] Create dashboard page component
- [ ] Import UI components from 'internal-packages/ui'
- [ ] Net worth summary card (total, assets, liabilities)
- [ ] Change indicators (day, month, year)
- [ ] Base currency selector
- [ ] Breakdown by country (pie chart)
- [ ] Breakdown by asset class (pie chart)
- [ ] Breakdown by currency (table)
- [ ] Net worth trend chart (line chart, 12 months)
- [ ] Quick links to modules
- [ ] Refresh button with last updated timestamp
- [ ] Loading states
- [ ] Empty states (no data yet)
- [ ] **Jest Tests:**
  - Test dashboard data rendering
  - Test chart rendering (with mock data)
  - Test base currency switching
  - Test refresh functionality
  - Test loading states
  - Test empty states
  - Test quick links
  - Mock all API calls
- [ ] **Manual Test:**
  - View dashboard
  - See net worth summary
  - View charts
  - Switch base currency
  - Refresh data
  - Click quick links
- [ ] **Component Test (Jest):** `tests/components/Dashboard.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/dashboard.spec.js`
- [ ] **Acceptance:** Dashboard loads <2 seconds, displays all data

---

## 1.9 Savings Module

### Task 1.9.1: Savings Account Data Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Savings.md`, `DataManagement.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read Savings.md - Feature 5.1 complete section
2. Read DataManagement.md for historical tracking
3. Read securityCompliance.md for account number encryption
4. Implement exact table structure from Savings.md

**Tasks:**
- [ ] Create `savings_accounts` table
- [ ] Create `account_balance_history` table
- [ ] Add indexes for efficient queries
- [ ] Create Pydantic models
- [ ] Implement account number encryption
- [ ] Support ISA and TFSA account types
- [ ] **Test Suite:**
  - Test account creation
  - Test account number encryption
  - Test balance history tracking
  - Test ISA/TFSA flag handling
  - Test multi-currency support
- [ ] **Run:** `pytest tests/models/test_savings_account.py -v`
- [ ] **Acceptance:** Savings account models complete

### Task 1.9.2: Interest Calculation Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Savings.md`, `CoreTaxCalcs.md`

**Agent Instructions:**
1. Read Savings.md - Business Logic section (interest calculation)
2. Support simple and compound interest
3. Handle different payment frequencies
4. Project future interest

**Tasks:**
- [ ] Create interest calculation service
- [ ] Implement simple interest calculation
- [ ] Implement compound interest calculation
- [ ] Support monthly, quarterly, annual frequencies
- [ ] Project annual interest earned
- [ ] **Test Suite:**
  - Test simple interest calculation
  - Test compound interest (monthly)
  - Test compound interest (quarterly)
  - Test annual interest projection
  - Test different interest rates
- [ ] **Run:** `pytest tests/services/test_interest_calculation.py -v`
- [ ] **Acceptance:** Interest calculations accurate

### Task 1.9.3: ISA/TFSA Allowance Tracking

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Savings.md`, `CoreTaxCalcs.md`

**Agent Instructions:**
1. Read Savings.md for ISA/TFSA requirements
2. Track annual allowances
3. Calculate remaining allowance
4. Handle tax year boundaries

**Tasks:**
- [ ] Create `isa_contributions` table
- [ ] Create `tfsa_contributions` table
- [ ] Implement ISA allowance tracking (£20,000 for 2024/25)
- [ ] Implement TFSA allowance tracking (R36,000 for 2024)
- [ ] Calculate used and remaining allowance
- [ ] Handle lifetime TFSA limit (R500,000)
- [ ] Alert when nearing limit
- [ ] **Test Suite:**
  - Test ISA contribution tracking
  - Test ISA allowance calculation
  - Test TFSA contribution tracking
  - Test TFSA annual and lifetime limits
  - Test tax year rollover
- [ ] **Run:** `pytest tests/services/test_isa_tfsa_tracking.py -v`
- [ ] **Acceptance:** ISA/TFSA allowances tracked correctly

### Task 1.9.4: Savings Interest Tax Treatment

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Savings.md`, `CoreTaxCalcs.md`

**Agent Instructions:**
1. Read Savings.md - Tax Treatment section
2. Read CoreTaxCalcs.md for UK and SA interest tax rules
3. Apply PSA (UK) and interest exemption (SA)
4. ISA/TFSA interest is tax-free

**Tasks:**
- [ ] Create savings tax treatment service
- [ ] Implement UK PSA calculation (£1000/£500/£0 based on tax band)
- [ ] Implement UK starting rate for savings (£5000 if income < £17,570)
- [ ] Implement SA interest exemption (R23,800 / R34,500)
- [ ] Mark ISA interest as tax-free
- [ ] Mark TFSA interest/growth as tax-free
- [ ] Calculate taxable interest
- [ ] **Test Suite:**
  - Test UK PSA application
  - Test starting rate for savings
  - Test SA interest exemption
  - Test ISA tax-free status
  - Test TFSA tax-free status
  - Test taxable interest calculation
- [ ] **Run:** `pytest tests/services/test_savings_tax_treatment.py -v`
- [ ] **Acceptance:** Savings tax treatment accurate

### Task 1.9.5: Emergency Fund Assessment

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Savings.md`, `AIAdvisoryRecommendation.md`

**Agent Instructions:**
1. Read Savings.md - Emergency Fund Assessment section
2. Calculate recommended emergency fund (6 months expenses)
3. Compare current emergency accounts to target
4. Generate recommendations

**Tasks:**
- [ ] Create emergency fund assessment service
- [ ] Calculate recommended amount (6 × monthly expenses)
- [ ] Sum current emergency fund accounts
- [ ] Calculate emergency fund ratio (current / target)
- [ ] Generate status (adequate, insufficient, none)
- [ ] **Test Suite:**
  - Test recommended calculation
  - Test current sum calculation
  - Test ratio calculation
  - Test status determination
- [ ] **Run:** `pytest tests/services/test_emergency_fund.py -v`
- [ ] **Acceptance:** Emergency fund assessment accurate

### Task 1.9.6: Savings Account Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Savings.md`, `performance.md`

**Agent Instructions:**
1. Read Savings.md - API Endpoints section
2. Implement CRUD operations
3. Support balance updates with history
4. Calculate aggregates

**Tasks:**
- [ ] Create `POST /api/v1/savings/accounts` endpoint
- [ ] Create `GET /api/v1/savings/accounts` endpoint
- [ ] Create `GET /api/v1/savings/accounts/:id` endpoint
- [ ] Create `PATCH /api/v1/savings/accounts/:id` endpoint
- [ ] Create `DELETE /api/v1/savings/accounts/:id` endpoint (soft delete)
- [ ] Create `POST /api/v1/savings/accounts/:id/balance` endpoint
- [ ] Create `GET /api/v1/savings/summary` endpoint
- [ ] Create `GET /api/v1/savings/isa-allowance` endpoint
- [ ] Create `GET /api/v1/savings/tfsa-allowance` endpoint
- [ ] Validate balance updates (max 10/day)
- [ ] Track balance history
- [ ] Calculate total savings
- [ ] **Test Suite:**
  - Test create account
  - Test get all accounts
  - Test update account
  - Test update balance
  - Test balance update limit
  - Test delete account
  - Test summary calculations
  - Test ISA/TFSA allowance queries
- [ ] **Run:** `pytest tests/api/savings/test_accounts.py -v`
- [ ] **Acceptance:** Savings account management complete

### Task 1.9.7: Savings Account UI

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Savings.md`, `UserFlows.md`

**Agent Instructions:**
1. Read Savings.md - Feature 5.1 complete section
2. Read UserFlows.md for UX principles
3. Import UI components from 'internal-packages/ui'
4. Support account list and detail views
5. Write comprehensive Jest tests

**Tasks:**
- [ ] Create savings account list component
- [ ] Create account detail component
- [ ] Create add/edit account form
- [ ] Import UI components from 'internal-packages/ui'
- [ ] Bank name and account type inputs
- [ ] Balance input with currency selector
- [ ] Interest rate input
- [ ] Account purpose dropdown
- [ ] ISA/TFSA checkbox
- [ ] Balance history chart
- [ ] Interest projection display
- [ ] Update balance modal
- [ ] Total savings summary
- [ ] Emergency fund status indicator
- [ ] ISA/TFSA allowance widgets
- [ ] **Jest Tests:**
  - Test account list rendering
  - Test add account form
  - Test edit account
  - Test balance update
  - Test summary calculations
  - Test ISA/TFSA allowance display
  - Test emergency fund indicator
  - Mock all API calls
- [ ] **Manual Test:**
  - Add savings account
  - Update balance
  - View balance history
  - See interest projection
  - Check ISA allowance
  - Check TFSA allowance
  - View emergency fund status
- [ ] **Component Test (Jest):** `tests/components/SavingsAccount.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/savings-account.spec.js`
- [ ] **Acceptance:** Savings account UI complete

---

## 🚦 PHASE 1 COMPLETE TESTING GATE

### Security Tests (CRITICAL)

- [ ] ✅ All authentication security tests pass (from Auth Gate)
- [ ] ✅ PII encryption working (tax status, income, account numbers)
- [ ] ✅ API endpoints require authentication
- [ ] ✅ Users can only access own data
- [ ] ✅ SQL injection blocked on all endpoints
- [ ] ✅ XSS attempts sanitized
- [ ] ✅ Rate limiting on all mutation endpoints

### Functional Tests

**Authentication (1.1-1.4):**
- [ ] ✅ Registration, verification, login, 2FA, logout work
- [ ] ✅ Profile management complete
- [ ] ✅ Password change, email change, account deletion work

**User Information (1.6-1.7):**
- [ ] ✅ Tax status CRUD operations work
- [ ] ✅ SRT calculator accurate
- [ ] ✅ SA presence test accurate
- [ ] ✅ Deemed domicile calculated correctly
- [ ] ✅ Income tracking works
- [ ] ✅ Multi-currency income supported
- [ ] ✅ Tax treatment calculated correctly

**Dashboard (1.8):**
- [ ] ✅ Dashboard loads in <2 seconds
- [ ] ✅ Net worth aggregation correct
- [ ] ✅ All breakdowns display (country, asset class, currency)
- [ ] ✅ Trend chart shows 12 months
- [ ] ✅ Changes calculated correctly

**Savings Module (1.9):**
- [ ] ✅ Account CRUD operations work
- [ ] ✅ Balance updates with history tracking
- [ ] ✅ Interest calculations accurate
- [ ] ✅ ISA allowance tracking correct
- [ ] ✅ TFSA allowance tracking correct
- [ ] ✅ Emergency fund assessment works
- [ ] ✅ Tax treatment calculations correct

### Integration Tests

- [ ] ✅ Full user journey: register → verify → login → setup profile → add tax status → add income → add savings account → view dashboard
- [ ] ✅ Tax status changes reflect in income tax calculations
- [ ] ✅ Savings balances reflect in dashboard
- [ ] ✅ Currency conversion consistent across modules
- [ ] ✅ Load test: 50 concurrent users using all features

### Code Quality

- [ ] ✅ Test coverage >80% for all modules
- [ ] ✅ All linting passes (backend and frontend)
- [ ] ✅ Security audit passes (npm audit / safety check)
- [ ] ✅ API documentation complete for all endpoints
- [ ] ✅ Component documentation complete
- [ ] ✅ No console errors in browser
- [ ] ✅ Mobile responsive on all pages

### Data Quality

- [ ] ✅ All temporal data (tax status) handles overlaps correctly
- [ ] ✅ Historical data retained (balance snapshots, audit trails)
- [ ] ✅ Currency conversion uses correct rates
- [ ] ✅ Tax year boundaries handled correctly (UK and SA)
- [ ] ✅ Soft deletes work (no hard deletes)

### Performance Tests

- [ ] ✅ Dashboard loads in <2 seconds
- [ ] ✅ SRT calculation <100ms
- [ ] ✅ API responses <500ms (95th percentile)
- [ ] ✅ Database queries optimized (no N+1)
- [ ] ✅ Frontend bundle size reasonable (<500KB gzipped)

### User Acceptance

- [ ] ✅ Can complete full onboarding flow
- [ ] ✅ Can track tax status over time
- [ ] ✅ Can track income from multiple sources
- [ ] ✅ Can track savings accounts
- [ ] ✅ Can view consolidated net worth
- [ ] ✅ ISA/TFSA allowances visible and accurate
- [ ] ✅ Emergency fund status clear
- [ ] ✅ All error messages clear and helpful

**Acceptance Criteria:**
🎯 **Phase 1 Complete**: Users can register, manage their profile, track tax status, record income, manage savings accounts, and view a consolidated dashboard showing their financial position.

🎯 **Foundation Solid**: All authentication, authorization, data management, and basic financial tracking working correctly.

🎯 **Ready for Phase 2**: Codebase clean, tested, documented, and ready to add Protection, Investment, and Tax Intelligence modules.

---
