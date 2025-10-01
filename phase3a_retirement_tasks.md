# Phase 3A: Retirement Module (UK & SA)

**Last Updated:** October 1, 2025
**Timeline:** 2-2.5 months (Part of Phase 3: 5-6 months total)
**Critical Rule:** ⛔ **DO NOT PROCEED TO NEXT SECTION UNTIL ALL TESTS PASS** ⛔

---

## 📋 Overview

**Goal:** Build comprehensive retirement planning for UK pensions and SA retirement funds

**Prerequisites:** Phase 2 complete (Protection, Investment, Tax Intelligence, AI Recommendations functional)

**Module Focus:**
- 3.1-3.4: UK Retirement Module (Pensions, Annual Allowance)
- 3.5-3.6: SA Retirement Module (Retirement Funds)

**Outputs:**
- UK pension tracking (DB, DC, SIPP, State Pension)
- Annual Allowance and Lifetime Allowance tracking
- Retirement income modeling
- SA retirement fund management (Pension Fund, Provident Fund, RA)
- SA tax deduction limits tracking
- Integration with Central Dashboard

**Related Files:**
- Next: `phase3b_iht_tasks.md` - IHT Planning Module
- Then: `phase3c_dta_residency_tasks.md` - DTA Calculator and Tax Residency

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
## 3.1 Retirement Module - UK Pension Data Models

### Task 3.1.1: UK Pension Database Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Retirement.md`, `Architecture.md`, `DataManagement.md`

**Agent Instructions:**
1. Read Retirement.md - Feature 7.1: UK Pension Management
2. Read Architecture.md for data model design patterns
3. Read DataManagement.md for temporal data requirements
4. Implement comprehensive UK pension models

**Tasks:**
- [ ] Create `uk_pensions` table
  - Pension type (OCCUPATIONAL_DB, OCCUPATIONAL_DC, PERSONAL_PENSION, SIPP, etc.)
  - Provider, scheme_reference, employer_name
  - Current value (for DC), contributions details
  - Start date, expected retirement date
  - Investment strategy, assumed growth/inflation rates
  - MPAA triggered flag and date
  - User_id, created/updated timestamps
- [ ] Create `uk_pension_contributions` table
  - Pension_id (foreign key)
  - Employee contribution (amount, frequency, type)
  - Employer contribution (amount, frequency, type)
  - Personal contribution (amount, frequency)
  - Tax relief method (NET_PAY, RELIEF_AT_SOURCE)
  - Contribution date, tax year
  - Effective_from, effective_to (temporal)
- [ ] Create `uk_pension_db_details` table
  - Pension_id (foreign key)
  - Accrual rate, pensionable service years
  - Final salary or career average
  - Scheme type (FINAL_SALARY, CAREER_AVERAGE, CASH_BALANCE)
  - Normal retirement age
  - Guaranteed pension amount, spouse pension %
  - Lump sum entitlement, indexation type
- [ ] Create `annual_allowance_tracking` table
  - User_id, tax_year
  - Total contributions, annual_allowance_limit
  - Carry_forward_available (from previous 3 years)
  - Tapered_allowance flag, adjusted_income
  - Allowance_used, allowance_remaining
- [ ] Create `state_pension_forecast` table
  - User_id, forecast_date
  - Qualifying years, years_needed_for_full
  - Estimated_weekly_amount, estimated_annual_amount
  - State pension age
- [ ] Add indexes on user_id, pension_id, tax_year
- [ ] Add CHECK constraints (values >= 0, retirement_date > today)
- [ ] Implement soft delete
- [ ] **Alembic Migration:**
  - Create migration for all pension tables
  - Test upgrade and downgrade
- [ ] **Test Suite:**
  - Test pension creation (DC and DB)
  - Test contribution tracking
  - Test DB pension details
  - Test annual allowance tracking
  - Test state pension forecast
  - Test temporal data handling
  - Test constraints
- [ ] **Run:** `pytest tests/models/test_uk_pensions.py -v`
- [ ] **Acceptance:** UK pension models complete with temporal tracking

### Task 3.1.2: Retirement Projection Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Retirement.md`, `DataManagement.md`

**Agent Instructions:**
1. Read Retirement.md - Retirement income modeling section
2. Implement models for retirement projections and income scenarios

**Tasks:**
- [ ] Create `retirement_projections` table
  - User_id, projection_date, target_retirement_age
  - Total_projected_pot, annual_income_needed
  - Income_sources (state pension, DB pensions, DC drawdown, other)
  - Income_gap (if any), on_track flag
  - Effective_from, effective_to
- [ ] Create `drawdown_scenarios` table
  - Pension_id, scenario_name
  - Drawdown_rate (% per year), start_age
  - Projected_income, pot_depletion_age
  - Tax_implications
- [ ] **Test Suite:**
  - Test retirement projection creation
  - Test income gap calculation
  - Test drawdown scenario modeling
- [ ] **Run:** `pytest tests/models/test_retirement_projections.py -v`
- [ ] **Acceptance:** Retirement projection models complete

---

## 3.2 Retirement Module - UK Pension Business Logic

### Task 3.2.1: Pension Management Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Retirement.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read Retirement.md - Pension management requirements
2. Read securityCompliance.md for scheme reference encryption
3. Implement service layer for pension CRUD and validations

**Tasks:**
- [ ] Create `services/retirement/uk_pension_service.py`
- [ ] Implement `create_pension()` method
  - Validate pension data
  - Encrypt scheme_reference
  - Store with audit trail
  - Link to user
- [ ] Implement `add_contribution()` method
  - Validate contribution amounts
  - Store with temporal data (effective_from/to)
  - Update annual allowance tracking
- [ ] Implement `calculate_current_value_dc()` method
  - Sum all contributions with tax relief
  - Apply growth rate
  - Return projected current value
- [ ] Implement `calculate_db_value()` method
  - For DB pensions: accrual_rate * service_years * final_salary
  - Return current transfer value estimate
- [ ] Implement `get_total_pension_pot()` method
  - Sum all DC pension values
  - Add DB transfer value estimates
  - Return total
- [ ] **Test Suite:**
  - Test pension creation and updates
  - Test contribution tracking
  - Test DC value calculation
  - Test DB value calculation
  - Test total pot aggregation
  - Test encryption
- [ ] **Run:** `pytest tests/services/retirement/test_uk_pension_service.py -v`
- [ ] **Acceptance:** UK pension service complete with accurate calculations

### Task 3.2.2: Annual Allowance Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Retirement.md`

**Agent Instructions:**
1. Read Retirement.md - Annual Allowance and carry forward rules
2. Implement Annual Allowance tracking with tapering and carry forward

**Tasks:**
- [ ] Create `services/retirement/annual_allowance_service.py`
- [ ] Implement `calculate_annual_allowance()` method
  - Standard allowance: £60,000 (2024/25)
  - If MPAA triggered: £10,000
  - If adjusted_income > £260,000: apply tapering
    - Taper: £1 reduction per £2 over threshold
    - Minimum tapered allowance: £10,000
  - Return applicable allowance
- [ ] Implement `calculate_carry_forward()` method
  - Look back 3 previous tax years
  - Calculate unused allowance from each year
  - Return total carry forward available
- [ ] Implement `calculate_allowance_usage()` method
  - Sum all pension contributions for tax year
  - Include employee + employer + personal + tax relief
  - Compare to allowance (including carry forward)
  - Return used, remaining, and excess (if any)
- [ ] Implement `check_annual_allowance_charge()` method
  - If contributions > (allowance + carry_forward):
    - Calculate excess
    - Calculate tax charge (at marginal rate)
    - Return charge amount and explanation
- [ ] **Test Suite:**
  - Test standard allowance (£60,000)
  - Test MPAA (£10,000)
  - Test tapering for high earners
  - Test carry forward from previous years
  - Test excess calculation
  - Test annual allowance charge
- [ ] **Run:** `pytest tests/services/retirement/test_annual_allowance.py -v`
- [ ] **Acceptance:** Annual Allowance calculations accurate with tapering and carry forward

### Task 3.2.3: Retirement Income Projection Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Retirement.md`

**Agent Instructions:**
1. Read Retirement.md - Retirement income modeling requirements
2. Implement service to project retirement income from all sources

**Tasks:**
- [ ] Create `services/retirement/income_projection_service.py`
- [ ] Implement `project_dc_pension_value()` method
  - Take current value, monthly contributions, growth rate
  - Project to retirement age
  - Return projected pot at retirement
- [ ] Implement `calculate_drawdown_income()` method
  - Take pot value, drawdown rate, start age
  - Calculate annual income
  - Model pot depletion
  - Return annual income and depletion age
- [ ] Implement `calculate_annuity_income()` method
  - Take pot value, annuity rate (market rates)
  - Calculate guaranteed annual income
  - Include spouse provision if selected
- [ ] Implement `calculate_total_retirement_income()` method
  - State pension (estimated)
  - DB pensions (guaranteed amounts)
  - DC drawdown or annuity
  - Other income sources
  - Return total annual income and breakdown
- [ ] Implement `calculate_retirement_income_gap()` method
  - Compare total projected income to needed income
  - Return gap (positive or negative) and on_track flag
- [ ] **Test Suite:**
  - Test DC projection with growth
  - Test drawdown calculations
  - Test annuity income
  - Test total income aggregation
  - Test income gap calculation
  - Test different scenarios
- [ ] **Run:** `pytest tests/services/retirement/test_income_projection.py -v`
- [ ] **Acceptance:** Retirement income projections accurate and comprehensive

---

## 3.3 Retirement Module - UK Pension API Endpoints

### Task 3.3.1: UK Pension CRUD Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Retirement.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read Retirement.md - API specifications
2. Read securityCompliance.md for authentication and rate limiting
3. Implement RESTful endpoints for pension management

**Tasks:**
- [ ] Create `api/v1/retirement/uk_pensions.py`
- [ ] **POST /api/v1/retirement/uk-pensions** - Create pension
  - Require authentication
  - Validate request body with Pydantic
  - Support both DC and DB pensions
  - Return 201 with pension details
- [ ] **GET /api/v1/retirement/uk-pensions** - List user pensions
  - Require authentication
  - Filter by type, provider
  - Return all user's pensions
- [ ] **GET /api/v1/retirement/uk-pensions/{id}** - Get single pension
  - Require authentication and ownership
- [ ] **PUT /api/v1/retirement/uk-pensions/{id}** - Update pension
  - Require authentication and ownership
  - Apply rate limiting
- [ ] **POST /api/v1/retirement/uk-pensions/{id}/contributions** - Add contribution
  - Validate contribution data
  - Update annual allowance tracking
- [ ] **GET /api/v1/retirement/annual-allowance** - Get annual allowance status
  - Return allowance for current tax year
  - Return usage, remaining, carry forward
- [ ] **GET /api/v1/retirement/total-pot** - Get total pension pot value
  - Aggregate all pensions
  - Return total and breakdown by pension
- [ ] **Test Suite:**
  - Test all CRUD operations
  - Test authentication and authorization
  - Test validation errors
  - Test annual allowance tracking
  - Test rate limiting
- [ ] **Run:** `pytest tests/api/retirement/test_uk_pensions_api.py -v`
- [ ] **Acceptance:** UK pension endpoints functional and secure

### Task 3.3.2: Retirement Projection Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Retirement.md`

**Agent Instructions:**
1. Read Retirement.md - Retirement projection requirements
2. Implement endpoints for income projections and scenarios

**Tasks:**
- [ ] **POST /api/v1/retirement/projections** - Calculate retirement projection
  - Accept target_retirement_age, annual_income_needed
  - Return projected pot, income sources, gap
- [ ] **GET /api/v1/retirement/income-projection** - Get retirement income projection
  - Project income from all sources at retirement
  - Return breakdown (state pension, DB, DC, other)
- [ ] **POST /api/v1/retirement/drawdown-scenario** - Model drawdown scenario
  - Accept drawdown_rate, start_age
  - Return projected income and pot depletion age
- [ ] **POST /api/v1/retirement/annuity-quote** - Calculate annuity income
  - Accept pot_value, annuity_rate
  - Return guaranteed annual income
- [ ] **Test Suite:**
  - Test projection calculations
  - Test income aggregation
  - Test scenario modeling
  - Test edge cases
- [ ] **Run:** `pytest tests/api/retirement/test_projections_api.py -v`
- [ ] **Acceptance:** Retirement projection endpoints accurate

---

## 3.4 Retirement Module - UK Pension Frontend UI

### Task 3.4.1: Pension List and Management

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Retirement.md`, `UserFlows.md`

**Agent Instructions:**
1. Read Retirement.md - UI requirements
2. Read UserFlows.md for UX patterns
3. Import UI components from 'internal-packages/ui'
4. Create comprehensive pension management interface

**Tasks:**
- [ ] Create `components/retirement/PensionList.jsx`
- [ ] Import UI components from 'internal-packages/ui' (Table, Card, Badge, Progress)
- [ ] Display pensions in table
  - Columns: Provider, Type, Current Value, Contributions, Retirement Age, Actions
  - Filter by type (DB, DC, SIPP, etc.)
  - Show MPAA badge if triggered
- [ ] Show total pension pot prominently
- [ ] Add "Add Pension" button
- [ ] Add edit and delete actions
- [ ] Create `components/retirement/PensionForm.jsx`
  - Pension type selector
  - Provider, scheme reference
  - DC fields: Current value, contributions
  - DB fields: Accrual rate, service years, final salary
  - Expected retirement date
  - Client-side validation
- [ ] **Jest Tests:**
  - Test pension list renders
  - Test filtering and sorting
  - Test total pot calculation
  - Test form validation
  - Test CRUD actions
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/PensionList.test.jsx`
- [ ] **Acceptance:** Pension list and management fully functional

### Task 3.4.2: Annual Allowance Tracker

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Retirement.md`, `UserFlows.md`

**Agent Instructions:**
1. Read Retirement.md - Annual Allowance tracking requirements
2. Create visual tracker for annual allowance usage
3. Import UI components from 'internal-packages/ui'

**Tasks:**
- [ ] Create `components/retirement/AnnualAllowanceTracker.jsx`
- [ ] Import UI components from 'internal-packages/ui' (Card, Progress, Alert)
- [ ] Display annual allowance information:
  - Allowance for current tax year (£60,000 or tapered)
  - Total contributions to date
  - Allowance remaining
  - Carry forward available
  - Visual progress bar
- [ ] Color coding:
  - Green: <80% used
  - Yellow: 80-100% used
  - Red: >100% (excess - charge applies)
- [ ] Show warning if approaching or exceeding allowance
- [ ] Display carry forward from previous 3 years
- [ ] Link to add contribution
- [ ] **Jest Tests:**
  - Test displays allowance data correctly
  - Test color coding
  - Test carry forward display
  - Test excess warning
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/AnnualAllowanceTracker.test.jsx`
- [ ] **Acceptance:** Annual allowance tracker clear and actionable

### Task 3.4.3: Retirement Income Projection Dashboard

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Retirement.md`, `UserFlows.md`

**Agent Instructions:**
1. Read Retirement.md - Retirement projection requirements
2. Create comprehensive retirement income dashboard
3. Import UI components from 'internal-packages/ui'

**Tasks:**
- [ ] Create `components/retirement/RetirementDashboard.jsx`
- [ ] Import UI components from 'internal-packages/ui' (Card, Chart, Table, Slider)
- [ ] Display retirement projection:
  - Projected total pot at retirement age
  - Projected annual income from all sources
  - Income breakdown (state pension, DB, DC, other)
  - Income gap (if needed income entered)
  - On-track indicator (green/yellow/red)
- [ ] Interactive scenario modeling:
  - Slider for retirement age (55-70)
  - Slider for drawdown rate (2-8%)
  - Update projections in real-time
- [ ] Chart showing pot growth over time to retirement
- [ ] Chart showing income in retirement (drawdown vs annuity)
- [ ] "What if" scenarios (increase contributions, delay retirement)
- [ ] **Jest Tests:**
  - Test dashboard renders with projection data
  - Test scenario sliders update calculations
  - Test charts display correctly
  - Test what-if scenarios
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/RetirementDashboard.test.jsx`
- [ ] **E2E Test (Playwright):** `npx playwright test e2e/retirement-uk.spec.js`
- [ ] **Acceptance:** Retirement dashboard provides clear, interactive projections

---

## 🚦 PHASE 3 UK RETIREMENT MODULE TESTING GATE

### Security Tests (CRITICAL)

- [ ] ✅ Scheme references encrypted in database
- [ ] ✅ Authentication required on all endpoints
- [ ] ✅ Users cannot access others' pensions
- [ ] ✅ Rate limiting on pension updates

### Functional Tests

- [ ] ✅ Can create DC and DB pensions
- [ ] ✅ Contributions tracked correctly
- [ ] ✅ Annual Allowance calculated accurately (including tapering)
- [ ] ✅ Carry forward calculated correctly
- [ ] ✅ Annual Allowance charge calculated when exceeded
- [ ] ✅ DC pension values projected accurately
- [ ] ✅ DB pension values calculated correctly
- [ ] ✅ Total pension pot aggregates all pensions
- [ ] ✅ Retirement income projections accurate
- [ ] ✅ Drawdown scenarios modeled correctly

### Integration Tests

- [ ] ✅ Full journey: Add pension → Add contributions → View annual allowance → View retirement projection
- [ ] ✅ Pension data appears in Central Dashboard net worth

### Code Quality

- [ ] ✅ Test coverage >80% for UK retirement module
- [ ] ✅ All linting passes
- [ ] ✅ API documentation complete

**Acceptance Criteria:**
🎯 UK Retirement module complete: Users can track pensions, monitor annual allowance, and project retirement income

---

## 3.5 Retirement Module - SA Retirement Funds Data Models

### Task 3.5.1: SA Retirement Fund Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Retirement.md`, `Architecture.md`, `DataManagement.md`

**Agent Instructions:**
1. Read Retirement.md - Feature 7.2: SA Retirement Fund Management
2. Implement SA retirement fund models (Pension Fund, Provident Fund, RA)

**Tasks:**
- [ ] Create `sa_retirement_funds` table
  - Fund type (PENSION_FUND, PROVIDENT_FUND, RETIREMENT_ANNUITY, PRESERVATION_FUND)
  - Provider, fund_name, fund_number
  - Current value, contributions
  - Start date, retirement age
  - Investment strategy
  - User_id, created/updated timestamps
- [ ] Create `sa_fund_contributions` table
  - Fund_id, employee_contribution, employer_contribution
  - Contribution_date, tax_year
  - Tax_deduction_claimed
  - Effective_from, effective_to (temporal)
- [ ] Create `sa_retirement_deduction_limits` table
  - User_id, tax_year
  - Annual_deduction_limit (27.5% of income, max R350,000)
  - Deductions_claimed, deductions_remaining
- [ ] Add indexes and constraints
- [ ] Implement soft delete
- [ ] **Alembic Migration:**
  - Create migration for SA retirement tables
- [ ] **Test Suite:**
  - Test SA fund creation
  - Test contribution tracking
  - Test deduction limit tracking
  - Test temporal data
- [ ] **Run:** `pytest tests/models/test_sa_retirement.py -v`
- [ ] **Acceptance:** SA retirement fund models complete

---

## 3.6 Retirement Module - SA Retirement Business Logic and API

### Task 3.6.1: SA Retirement Service and Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Retirement.md`

**Agent Instructions:**
1. Read Retirement.md - SA retirement fund requirements
2. Implement service and API for SA retirement funds

**Tasks:**
- [ ] Create `services/retirement/sa_retirement_service.py`
- [ ] Implement `create_fund()` method
- [ ] Implement `calculate_tax_deduction()` method
  - Deduction limit: 27.5% of remuneration or taxable income, capped at R350,000/year
  - Calculate deduction claimed and remaining
- [ ] Implement `project_retirement_value()` method
- [ ] Create API endpoints `api/v1/retirement/sa-funds.py`
  - POST /api/v1/retirement/sa-funds (create fund)
  - GET /api/v1/retirement/sa-funds (list funds)
  - POST /api/v1/retirement/sa-funds/{id}/contributions (add contribution)
  - GET /api/v1/retirement/sa-tax-deduction (get deduction status)
- [ ] **Test Suite:**
  - Test fund creation
  - Test tax deduction calculation
  - Test API endpoints
- [ ] **Run:** `pytest tests/services/retirement/test_sa_retirement.py -v` and `pytest tests/api/retirement/test_sa_funds_api.py -v`
- [ ] **Acceptance:** SA retirement service and API functional

### Task 3.6.2: SA Retirement Frontend

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Retirement.md`, `UserFlows.md`

**Agent Instructions:**
1. Read Retirement.md - SA retirement UI requirements
2. Create SA retirement fund management UI
3. Import UI components from 'internal-packages/ui'

**Tasks:**
- [ ] Create `components/retirement/SAFundList.jsx`
- [ ] Import UI components from 'internal-packages/ui'
- [ ] Display SA funds in table (Provider, Type, Value, Contributions)
- [ ] Create SA fund form (fund type, provider, value, contributions)
- [ ] Create SA tax deduction tracker
  - Show deduction limit (27.5% of income, max R350k)
  - Show deductions claimed and remaining
  - Visual progress bar
- [ ] **Jest Tests:**
  - Test SA fund list and form
  - Test tax deduction tracker
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/SAFundList.test.jsx`
- [ ] **Acceptance:** SA retirement management functional

---


**Next Step:**
➡️ Proceed to `phase3b_iht_tasks.md` to build IHT Planning Module

---
