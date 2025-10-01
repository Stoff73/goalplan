# Phase 2B: Investment Module

**Last Updated:** October 1, 2025
**Timeline:** 1.5-2 months (Part of Phase 2: 4-5 months total)
**Critical Rule:** ⛔ **DO NOT PROCEED TO NEXT SECTION UNTIL ALL TESTS PASS** ⛔

---

## 📋 Overview

**Goal:** Build investment portfolio management with asset allocation, tax calculations, and performance tracking

**Prerequisites:** 
- Phase 1 complete (authentication, user information, savings module, and dashboard functional)
- Phase 2A complete (Protection module functional)

**Module Focus:**
- 2.5-2.8: Investment Module (Portfolio Management)

**Outputs:**
- Investment portfolio management across UK and SA
- Capital gains and dividend tax calculations
- Asset allocation and performance tracking
- Tax lot tracking with FIFO selling
- EIS/SEIS/VCT tax relief tracking
- Integration with Central Dashboard for net worth updates

**Related Files:**
- Previous: `phase2a_protection_tasks.md` - Protection Module
- Next: `phase2c_tax_ai_tasks.md` - Tax Intelligence and AI Recommendations

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
## 2.5 Investment Module - Data Models

### Task 2.5.1: Investment Account and Holdings Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Investment.md`, `Architecture.md`, `DataManagement.md`

**Agent Instructions:**
1. Read Investment.md - Feature 6.1: Portfolio Management
2. Read Architecture.md for data model patterns
3. Read DataManagement.md for temporal data requirements
4. Implement investment account and holdings models

**Tasks:**
- [ ] Create `investment_accounts` table
  - Account type (STOCKS_ISA, GIA, VCT, EIS, SEIS, SA_UNIT_TRUST, etc.)
  - Provider, account_number (encrypted, last 4 digits)
  - Country (UK, SA, OFFSHORE)
  - User_id, created/updated timestamps
- [ ] Create `investment_holdings` table
  - Account_id (foreign key)
  - Security type (STOCK, FUND, ETF, BOND, VCT, EIS_SHARE)
  - Ticker, name, quantity
  - Purchase date, purchase price, purchase currency
  - Current price, current value, unrealized gain
  - Asset class, region, sector
  - Created/updated timestamps
- [ ] Create `tax_lot_tracking` table
  - Holding_id (foreign key)
  - Purchase date, quantity, cost basis
  - Disposal method (FIFO, AVERAGE_COST)
  - Realized flag
- [ ] Create `dividend_income` table
  - Holding_id, payment date, amount, currency
  - Tax withheld, country of source
  - UK dividend tax paid, SA dividend tax paid
- [ ] Create `capital_gains_realized` table
  - Holding_id, disposal date, quantity sold
  - Sale price, sale value
  - Cost basis, gain/loss
  - Tax year, country
- [ ] Add indexes on user_id, account_id, ticker
- [ ] Add CHECK constraints (quantity > 0, amounts >= 0)
- [ ] Implement soft delete
- [ ] **Alembic Migration:**
  - Create migration for all tables
  - Test upgrade and downgrade
- [ ] **Test Suite:**
  - Test account creation
  - Test holdings creation with all fields
  - Test tax lot tracking
  - Test dividend recording
  - Test capital gains tracking
  - Test constraints and indexes
- [ ] **Run:** `pytest tests/models/test_investments.py -v`
- [ ] **Acceptance:** Investment models complete and migrated

### Task 2.5.2: EIS/SEIS/VCT Tax Relief Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Investment.md`

**Agent Instructions:**
1. Read Investment.md - EIS/SEIS/VCT tracking section
2. Implement models for tax-advantaged investments with holding period tracking

**Tasks:**
- [ ] Create `tax_advantaged_investments` table
  - Holding_id (foreign key)
  - Relief type (INCOME_TAX_RELIEF, CGT_EXEMPTION, CGT_DEFERRAL)
  - Relief amount, tax year claimed
  - Holding period required (years)
  - Holding period end date
  - At_risk flag (auto-calculated)
- [ ] Add business logic to calculate at_risk status
  - EIS: 3-year minimum holding period
  - SEIS: 3-year minimum holding period
  - VCT: 5-year minimum holding period
- [ ] **Test Suite:**
  - Test tax relief recording
  - Test holding period calculation
  - Test at_risk flag updates
  - Test for EIS, SEIS, and VCT
- [ ] **Run:** `pytest tests/models/test_tax_advantaged.py -v`
- [ ] **Acceptance:** Tax-advantaged investment tracking complete

---

## 2.6 Investment Module - Business Logic Services

### Task 2.6.1: Portfolio Management Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Investment.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read Investment.md - Portfolio management requirements
2. Read securityCompliance.md for account number encryption
3. Implement service for portfolio CRUD and calculations

**Tasks:**
- [ ] Create `services/investment/portfolio_service.py`
- [ ] Implement `create_account()` method
  - Encrypt account_number
  - Validate account type
  - Store with audit trail
- [ ] Implement `add_holding()` method
  - Validate quantity > 0, purchase price >= 0
  - Calculate initial unrealized gain (0 on purchase)
  - Create tax lot entry
- [ ] Implement `update_holding_price()` method
  - Update current price and value
  - Recalculate unrealized gain: (current_price - purchase_price) * quantity
  - Calculate unrealized gain %
- [ ] Implement `sell_holding()` method (partial or full)
  - Use FIFO for UK tax lots
  - Calculate realized gain
  - Record in capital_gains_realized
  - Update holding quantity or mark as sold
- [ ] Implement `record_dividend()` method
  - Record dividend payment
  - Track tax withheld
  - Link to holding
- [ ] **Test Suite:**
  - Test account and holding creation
  - Test price updates and gain calculations
  - Test selling holdings (FIFO)
  - Test dividend recording
  - Test account number encryption
- [ ] **Run:** `pytest tests/services/investment/test_portfolio_service.py -v`
- [ ] **Acceptance:** Portfolio service complete with accurate calculations

### Task 2.6.2: Asset Allocation Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Investment.md`

**Agent Instructions:**
1. Read Investment.md - Asset allocation analysis requirements
2. Implement asset allocation calculations by class, region, and sector

**Tasks:**
- [ ] Create `services/investment/asset_allocation_service.py`
- [ ] Implement `calculate_allocation_by_asset_class()` method
  - Group holdings by asset_class (EQUITY, FIXED_INCOME, PROPERTY, etc.)
  - Calculate total value per class
  - Return percentages
- [ ] Implement `calculate_allocation_by_region()` method
  - Group by region (UK, US, EUROPE, ASIA, etc.)
  - Calculate percentages
- [ ] Implement `calculate_allocation_by_sector()` method
  - Group by sector
  - Calculate percentages
- [ ] Implement `get_portfolio_summary()` method
  - Total portfolio value
  - Total unrealized gains/losses
  - Asset allocation breakdown
  - Top 10 holdings
  - Currency exposure
- [ ] **Test Suite:**
  - Test asset class allocation
  - Test region allocation
  - Test sector allocation
  - Test with multiple holdings across classes
  - Test portfolio summary aggregation
- [ ] **Run:** `pytest tests/services/investment/test_asset_allocation.py -v`
- [ ] **Acceptance:** Asset allocation analysis accurate

### Task 2.6.3: Tax Calculation Service (Investments)

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Investment.md`, `CoreTaxCalcs.md`

**Agent Instructions:**
1. Read Investment.md - Tax treatment section
2. Read CoreTaxCalcs.md for UK CGT and dividend tax rules
3. Implement investment tax calculations

**Tasks:**
- [ ] Create `services/investment/investment_tax_service.py`
- [ ] Implement `calculate_cgt_uk()` method
  - If account type = STOCKS_ISA: gains_tax_free = TRUE
  - If GIA: apply UK CGT rules
    - Annual exempt amount: £3,000 (2024/25)
    - Basic rate: 10%, higher rate: 20%
  - Calculate tax owed on realized gains
- [ ] Implement `calculate_dividend_tax_uk()` method
  - If STOCKS_ISA: dividends_tax_free = TRUE
  - If GIA: apply UK dividend tax
    - Dividend allowance: £500 (2024/25)
    - Basic rate: 8.75%, higher rate: 33.75%, additional: 39.35%
- [ ] Implement `calculate_cgt_sa()` method
  - Inclusion rate method (40% of gain included)
  - Apply SA income tax rates to included gain
- [ ] Implement `calculate_dividend_tax_sa()` method
  - Dividend withholding tax: 20%
- [ ] **Test Suite:**
  - Test UK CGT calculation (GIA vs ISA)
  - Test UK dividend tax
  - Test SA CGT inclusion rate
  - Test SA dividend withholding
  - Test annual allowances applied
- [ ] **Run:** `pytest tests/services/investment/test_investment_tax.py -v`
- [ ] **Acceptance:** Investment tax calculations accurate for UK and SA

---

## 2.7 Investment Module - API Endpoints

### Task 2.7.1: Investment Account and Holdings Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Investment.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read Investment.md - API specifications
2. Read securityCompliance.md for authentication and rate limiting
3. Implement RESTful endpoints for investment management

**Tasks:**
- [ ] Create `api/v1/investments/accounts.py`
- [ ] **POST /api/v1/investments/accounts** - Create investment account
  - Require authentication
  - Validate request body
  - Return 201 with account details
- [ ] **GET /api/v1/investments/accounts** - List user accounts
  - Support filtering by type, country
- [ ] **POST /api/v1/investments/holdings** - Add holding
  - Require authentication and account ownership
  - Validate holding data
  - Apply rate limiting
- [ ] **GET /api/v1/investments/holdings** - List holdings
  - Support filtering by account, ticker, asset_class
  - Return paginated results
- [ ] **PUT /api/v1/investments/holdings/{id}/price** - Update holding price
  - Recalculate unrealized gains
- [ ] **POST /api/v1/investments/holdings/{id}/sell** - Sell holding
  - Validate quantity <= owned
  - Calculate realized gains using FIFO
  - Return gain details
- [ ] **POST /api/v1/investments/dividends** - Record dividend
  - Link to holding
  - Track tax withheld
- [ ] **Test Suite:**
  - Test all CRUD operations
  - Test authentication and authorization
  - Test validation errors
  - Test FIFO selling logic
  - Test rate limiting
- [ ] **Run:** `pytest tests/api/investment/test_holdings_api.py -v`
- [ ] **Acceptance:** Investment endpoints functional and secure

### Task 2.7.2: Portfolio Analysis Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Investment.md`

**Agent Instructions:**
1. Read Investment.md - Portfolio analysis requirements
2. Implement endpoints for asset allocation and performance

**Tasks:**
- [ ] **GET /api/v1/investments/portfolio/summary** - Portfolio summary
  - Require authentication
  - Return total value, unrealized gains, allocation breakdown
- [ ] **GET /api/v1/investments/portfolio/allocation** - Asset allocation
  - Support query params: by=asset_class|region|sector
  - Return allocation percentages
- [ ] **GET /api/v1/investments/portfolio/performance** - Performance metrics
  - Total return, unrealized gains/losses
  - Dividend income to date
- [ ] **GET /api/v1/investments/tax/capital-gains** - Realized gains for tax year
  - Filter by tax year
  - Return UK and SA gains separately
- [ ] **Test Suite:**
  - Test portfolio summary aggregation
  - Test allocation calculations
  - Test performance metrics
  - Test tax year filtering
- [ ] **Run:** `pytest tests/api/investment/test_portfolio_api.py -v`
- [ ] **Acceptance:** Portfolio analysis endpoints working accurately

---

## 2.8 Investment Module - Frontend UI

### Task 2.8.1: Portfolio Dashboard Component

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Investment.md`, `UserFlows.md`

**Agent Instructions:**
1. Read Investment.md - Portfolio dashboard requirements
2. Read UserFlows.md for dashboard UX patterns
3. Import UI components from 'internal-packages/ui'
4. Create comprehensive portfolio overview

**Tasks:**
- [ ] Create `components/investment/PortfolioDashboard.jsx`
- [ ] Import UI components from 'internal-packages/ui' (Card, Chart, Table)
- [ ] Display portfolio summary:
  - Total portfolio value
  - Total unrealized gains/losses (with % and color)
  - Number of holdings
  - YTD dividend income
- [ ] Asset allocation chart (pie or donut chart)
  - By asset class
  - Clickable segments to filter holdings
- [ ] Top holdings table
  - Ticker, name, current value, unrealized gain, % of portfolio
  - Sortable by value or gain
- [ ] Recent transactions (last 10)
- [ ] Performance chart (line chart over time)
- [ ] Fetch data from portfolio summary endpoint
- [ ] **Jest Tests:**
  - Test dashboard renders with portfolio data
  - Test summary calculations display
  - Test asset allocation chart
  - Test top holdings table
  - Test loading and error states
  - Mock all API calls
- [ ] **Component Test (Jest):** `npm test tests/components/PortfolioDashboard.test.jsx`
- [ ] **Acceptance:** Portfolio dashboard displays comprehensive overview

### Task 2.8.2: Holdings List and Management

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Investment.md`, `UserFlows.md`

**Agent Instructions:**
1. Read Investment.md - Holdings management requirements
2. Import UI components from 'internal-packages/ui'
3. Create holdings list with add/edit/sell functionality

**Tasks:**
- [ ] Create `components/investment/HoldingsList.jsx`
- [ ] Import UI components from 'internal-packages/ui' (Table, Button, Badge)
- [ ] Display holdings in sortable, filterable table
  - Columns: Ticker, Name, Quantity, Purchase Price, Current Price, Value, Unrealized Gain, Actions
  - Filter by account, asset class, region
  - Sort by any column
- [ ] Add "Add Holding" button
- [ ] Add "Sell" and "Update Price" actions per row
- [ ] Show color coding for gains (green) and losses (red)
- [ ] Show badges for tax-advantaged investments (ISA, VCT, EIS, SEIS)
- [ ] Handle loading and error states
- [ ] Create `components/investment/AddHoldingForm.jsx`
  - Account selector
  - Security type, ticker, name
  - Quantity, purchase price, purchase date
  - Asset class, region, sector
  - Client-side validation
- [ ] Create `components/investment/SellHoldingModal.jsx`
  - Quantity to sell (max = owned)
  - Sale price
  - Calculate realized gain preview
  - Confirm sale
- [ ] **Jest Tests:**
  - Test holdings list renders correctly
  - Test filtering and sorting
  - Test add holding form validation
  - Test sell modal calculation
  - Test action handlers
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/HoldingsList.test.jsx`
- [ ] **Acceptance:** Holdings management fully functional

### Task 2.8.3: Asset Allocation Visualization

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Investment.md`, `UserFlows.md`

**Agent Instructions:**
1. Read Investment.md - Asset allocation requirements
2. Create interactive allocation visualizations
3. Import chart components from 'internal-packages/ui'

**Tasks:**
- [ ] Create `components/investment/AssetAllocation.jsx`
- [ ] Import UI components from 'internal-packages/ui' (PieChart, BarChart, Tabs)
- [ ] Create tabbed interface:
  - Tab 1: Asset Class allocation (EQUITY, FIXED_INCOME, etc.)
  - Tab 2: Region allocation (UK, US, EUROPE, etc.)
  - Tab 3: Sector allocation
- [ ] Each tab shows:
  - Pie chart visualization
  - Table with category, value, percentage
  - Drill-down to holdings in that category
- [ ] Color-coded segments
- [ ] Interactive tooltips
- [ ] **Jest Tests:**
  - Test renders with allocation data
  - Test tab switching
  - Test charts display correctly
  - Test drill-down functionality
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/AssetAllocation.test.jsx`
- [ ] **E2E Test (Playwright):** `npx playwright test e2e/investments.spec.js`
- [ ] **Acceptance:** Asset allocation visualizations clear and interactive

---

## 🚦 PHASE 2 INVESTMENT MODULE TESTING GATE

### Security Tests (CRITICAL)

- [ ] ✅ Account numbers encrypted in database
- [ ] ✅ Authentication required on all endpoints
- [ ] ✅ Users cannot access others' portfolios
- [ ] ✅ Rate limiting on holding updates

### Functional Tests

- [ ] ✅ Can create investment account
- [ ] ✅ Can add holdings to account
- [ ] ✅ Unrealized gain calculations accurate
- [ ] ✅ Selling uses FIFO correctly
- [ ] ✅ Dividend recording works
- [ ] ✅ Asset allocation calculations accurate
- [ ] ✅ CGT and dividend tax calculations correct
- [ ] ✅ EIS/SEIS/VCT holding period tracking works

### Integration Tests

- [ ] ✅ Full journey: Create account → Add holdings → Update prices → View allocation → Sell holding → View realized gains
- [ ] ✅ Investment data appears in Central Dashboard net worth

### Code Quality

- [ ] ✅ Test coverage >80% for investment module
- [ ] ✅ All linting passes
- [ ] ✅ API documentation complete

**Acceptance Criteria:**
🎯 Investment module complete: Users can track portfolios, view allocation, calculate taxes, and manage holdings

---

**Next Step:**
➡️ Proceed to `phase2c_tax_ai_tasks.md` to build Tax Intelligence and AI Recommendations

---
