# Phase 3C: DTA Calculator & Tax Residency

**Last Updated:** October 1, 2025
**Timeline:** 1-1.5 months (Part of Phase 3: 5-6 months total)
**Critical Rule:** ⛔ **PHASE 3 TESTING GATE MUST PASS BEFORE PHASE 4** ⛔

---

## 📋 Overview

**Goal:** Build Double Tax Agreement relief calculator and enhanced tax residency determination

**Prerequisites:** 
- Phase 2 complete
- Phase 3A complete (Retirement module functional)
- Phase 3B complete (IHT Planning functional)

**Module Focus:**
- 3.11-3.12: DTA Calculator
- 3.13-3.14: Enhanced Tax Residency Determination

**Outputs:**
- DTA relief calculations for employment income, dividends, capital gains, pensions
- Tie-breaker rules for dual residents
- UK Statutory Residence Test (SRT) calculator
- SA Physical Presence Test calculator
- Dual residency determination with clear explanations

**Related Files:**
- Previous: `phase3a_retirement_tasks.md` - Retirement Module
- Previous: `phase3b_iht_tasks.md` - IHT Planning Module
- Next (after Phase 3 complete): `phase4a_goals_scenarios_tasks.md` - Goal Planning & Scenarios

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
## 3.11 DTA Calculator - Service and API

### Task 3.11.1: Double Tax Agreement Relief Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `DTA.md`, `CoreTaxCalcs.md`

**Agent Instructions:**
1. Read DTA.md - Complete DTA relief specifications
2. Read CoreTaxCalcs.md for UK and SA tax calculations
3. Implement DTA relief calculator for various income types

**Tasks:**
- [ ] Create `services/tax/dta_service.py`
- [ ] Implement `calculate_dta_relief_employment_income()` method
  - If dual resident: Apply tie-breaker rules (permanent home, center of vital interests, habitual abode, nationality)
  - If UK resident earning SA income: SA taxes, UK gives credit
  - If SA resident earning UK income: UK taxes, SA gives credit
  - Calculate foreign tax credit
  - Return relief amount and explanation
- [ ] Implement `calculate_dta_relief_dividends()` method
  - Dividend source country has primary taxing right
  - Withholding tax limits: 15% (UK-SA DTA)
  - Residence country gives credit for withholding tax
  - Calculate credit and net tax
- [ ] Implement `calculate_dta_relief_interest()` method
  - Interest taxed in source country and residence country
  - Withholding tax: 0% under UK-SA DTA
  - Residence country gives full credit
- [ ] Implement `calculate_dta_relief_capital_gains()` method
  - Immovable property: Taxed in country where located
  - Business property: Taxed in country where PE located
  - Shares/securities: Taxed in residence country (unless >50% immovable property)
  - Calculate relief
- [ ] Implement `calculate_dta_relief_pensions()` method
  - Private pensions: Taxed in residence country
  - Government pensions: Taxed in source country
  - Calculate relief
- [ ] Implement `apply_tie_breaker_rules()` method
  - Permanent home test
  - Center of vital interests test
  - Habitual abode test
  - Nationality test
  - Return sole residence determination
- [ ] **Test Suite:**
  - Test employment income relief
  - Test dividend withholding and credit
  - Test interest relief
  - Test capital gains relief (property vs securities)
  - Test pension relief
  - Test tie-breaker rules
- [ ] **Run:** `pytest tests/services/tax/test_dta_service.py -v`
- [ ] **Acceptance:** DTA relief calculations accurate for all income types

### Task 3.11.2: DTA API Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `DTA.md`

**Agent Instructions:**
1. Read DTA.md - API requirements
2. Implement endpoints for DTA calculations

**Tasks:**
- [ ] Create `api/v1/tax/dta.py`
- [ ] **POST /api/v1/tax/dta/employment-income** - Calculate DTA relief on employment income
  - Accept UK and SA income, residency status
  - Return relief amount and explanation
- [ ] **POST /api/v1/tax/dta/dividends** - Calculate DTA relief on dividends
  - Accept dividend income, source country, withholding tax
  - Return foreign tax credit
- [ ] **POST /api/v1/tax/dta/capital-gains** - Calculate DTA relief on capital gains
  - Accept gain details, asset type, location
  - Return taxing country and relief
- [ ] **POST /api/v1/tax/dta/pensions** - Calculate DTA relief on pensions
  - Accept pension type (private/government), source country
  - Return taxing country and relief
- [ ] **POST /api/v1/tax/dta/tie-breaker** - Apply tie-breaker rules for dual residents
  - Accept residency factors
  - Return sole residence determination
- [ ] **Test Suite:**
  - Test all DTA endpoints
  - Test authentication
  - Test validation
- [ ] **Run:** `pytest tests/api/tax/test_dta_api.py -v`
- [ ] **Acceptance:** DTA endpoints functional and accurate

---

## 3.12 DTA Calculator - Frontend UI

### Task 3.12.1: DTA Relief Calculator UI

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `DTA.md`, `UserFlows.md`

**Agent Instructions:**
1. Read DTA.md - DTA calculator UI requirements
2. Create interactive DTA relief calculator
3. Import UI components from 'internal-packages/ui'

**Tasks:**
- [ ] Create `components/tax/DTACalculator.jsx`
- [ ] Import UI components from 'internal-packages/ui' (Form, Input, Select, Card, Table)
- [ ] Create tabbed interface:
  - Tab 1: Employment Income
  - Tab 2: Dividends
  - Tab 3: Capital Gains
  - Tab 4: Pensions
  - Tab 5: Tie-Breaker Rules
- [ ] Each tab has input form and results display
- [ ] Display relief calculation breakdown
- [ ] Show which country has taxing rights
- [ ] Show foreign tax credit calculation
- [ ] Explain DTA article applied
- [ ] **Jest Tests:**
  - Test DTA calculator renders
  - Test tab switching
  - Test form submissions
  - Test calculation displays
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/DTACalculator.test.jsx`
- [ ] **Acceptance:** DTA calculator provides clear relief calculations

---

## 3.13 Enhanced Tax Residency - UK SRT Calculator

### Task 3.13.1: UK Statutory Residence Test Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `TaxResidency.md`, `UserInfo.md`

**Agent Instructions:**
1. Read TaxResidency.md - Complete UK SRT specifications
2. Implement comprehensive SRT calculator with all tests and ties

**Tasks:**
- [ ] Create `services/tax/uk_srt_service.py`
- [ ] Implement `automatic_overseas_test()` method
  - Test 1: <16 days in UK (if not UK resident in prior 3 years)
  - Test 2: <46 days in UK (if UK resident in prior 1-3 years)
  - Test 3: Full-time work abroad (no significant breaks, <91 UK days, no >30 consecutive UK days)
  - Return TRUE if passes any test (non-resident)
- [ ] Implement `automatic_uk_test()` method
  - Test 1: ≥183 days in UK
  - Test 2: UK home for ≥91 days AND present at least 30 days
  - Test 3: Full-time work in UK (≥35hrs/week average)
  - Return TRUE if passes any test (resident)
- [ ] Implement `sufficient_ties_test()` method
  - Calculate UK ties:
    - Family tie: Spouse/partner or minor children UK resident
    - Accommodation tie: UK accommodation available ≥91 days AND present ≥1 night
    - Work tie: ≥40 days work in UK (≥3hrs/day)
    - 90-day tie: ≥90 days in UK in either of prior 2 tax years
    - Country tie: More days in UK than any other single country (for leavers only)
  - Apply sufficient ties rules based on days in UK:
    - Arrivers: 0-1 ties → 183 days, 2 ties → 120 days, 3 ties → 90 days, 4 ties → 46 days
    - Leavers: 0 ties → 183 days, 1 tie → 120 days, 2 ties → 90 days, 3 ties → 46 days, 4 ties → 16 days
  - Return UK resident if days ≥ threshold for tie count
- [ ] Implement `calculate_uk_residence()` method
  - Run automatic overseas test (if passes: non-resident)
  - Run automatic UK test (if passes: resident)
  - Run sufficient ties test (return result)
  - Return residency determination and explanation
- [ ] **Test Suite:**
  - Test automatic overseas test (all 3 tests)
  - Test automatic UK test (all 3 tests)
  - Test ties calculation
  - Test sufficient ties thresholds
  - Test full SRT for various scenarios
  - Test edge cases
- [ ] **Run:** `pytest tests/services/tax/test_uk_srt.py -v`
- [ ] **Acceptance:** UK SRT calculator accurate and comprehensive

### Task 3.13.2: UK SRT API and UI

**🐍 DELEGATE TO: `python-backend-engineer`**
**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `TaxResidency.md`, `UserFlows.md`

**Agent Instructions:**
1. Backend: Create API endpoint for UK SRT
2. Frontend: Create interactive SRT calculator UI

**Tasks:**
- [ ] **Backend (🐍):** Create `api/v1/tax/uk-srt.py`
  - **POST /api/v1/tax/uk-srt/calculate** - Calculate UK residence
    - Accept days in UK, ties, prior residence history
    - Return residence determination, tests applied, explanation
- [ ] **Backend Test:** `pytest tests/api/tax/test_uk_srt_api.py -v`
- [ ] **Frontend (⚛️):** Create `components/tax/UKSRTCalculator.jsx`
  - Import UI components from 'internal-packages/ui'
  - Input form: Days in UK, ties (checkboxes), prior residence
  - Display automatic test results
  - Display ties count and sufficient ties threshold
  - Display final residence determination with clear explanation
  - Show which SRT test determined the result
- [ ] **Jest Tests:**
  - Test SRT calculator form
  - Test results display
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/UKSRTCalculator.test.jsx`
- [ ] **Acceptance:** UK SRT calculator functional and provides clear residence determination

---

## 3.14 Enhanced Tax Residency - SA Physical Presence Test

### Task 3.14.1: SA Physical Presence Test Service and API

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `TaxResidency.md`

**Agent Instructions:**
1. Read TaxResidency.md - SA Physical Presence Test specifications
2. Implement SA residency calculator

**Tasks:**
- [ ] Create `services/tax/sa_presence_service.py`
- [ ] Implement `calculate_sa_residence()` method
  - Ordinarily resident test: Traditional home in SA
  - Physical presence test:
    - Present in SA ≥91 days in current year AND
    - Present ≥91 days in each of prior 5 years AND
    - ≥915 days total in prior 5 years
  - Return SA resident if either test passes
- [ ] Create `api/v1/tax/sa-presence.py`
  - **POST /api/v1/tax/sa-presence/calculate**
    - Accept days in SA (current and prior 5 years)
    - Accept ordinarily resident flag
    - Return residence determination
- [ ] **Test Suite:**
  - Test physical presence test
  - Test ordinarily resident test
  - Test API endpoint
- [ ] **Run:** `pytest tests/services/tax/test_sa_presence.py -v` and `pytest tests/api/tax/test_sa_presence_api.py -v`
- [ ] **Acceptance:** SA presence test calculator accurate

### Task 3.14.2: SA Presence Test UI

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `TaxResidency.md`, `UserFlows.md`

**Agent Instructions:**
1. Read TaxResidency.md - SA presence test requirements
2. Create SA presence test calculator UI

**Tasks:**
- [ ] Create `components/tax/SAPresenceCalculator.jsx`
- [ ] Import UI components from 'internal-packages/ui'
- [ ] Input form: Days in SA (current year and prior 5 years)
- [ ] Ordinarily resident checkbox
- [ ] Display physical presence test results:
  - Current year ≥91 days? (✓/✗)
  - Each prior year ≥91 days? (✓/✗)
  - Total prior 5 years ≥915 days? (✓/✗)
- [ ] Display final SA residence determination
- [ ] **Jest Tests:**
  - Test SA calculator form and results
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/SAPresenceCalculator.test.jsx`
- [ ] **E2E Test (Playwright):** `npx playwright test e2e/tax-residency.spec.js`
- [ ] **Acceptance:** SA presence calculator functional

---

## 🚦 PHASE 3 COMPLETE TESTING GATE

### Security Tests (CRITICAL)

- [ ] ✅ All PII encrypted (scheme references, estate data)
- [ ] ✅ Authentication required on all endpoints
- [ ] ✅ Authorization working (users can't access others' data)
- [ ] ✅ Rate limiting on all mutation endpoints
- [ ] ✅ SQL injection blocked on all endpoints
- [ ] ✅ XSS attempts sanitized
- [ ] ✅ Security audit passes

### Functional Tests

**UK Retirement (3.1-3.4):**
- [ ] ✅ UK pensions (DC and DB) created and tracked
- [ ] ✅ Annual Allowance calculated with tapering
- [ ] ✅ Carry forward calculated correctly
- [ ] ✅ Retirement income projections accurate
- [ ] ✅ Drawdown scenarios modeled correctly

**SA Retirement (3.5-3.6):**
- [ ] ✅ SA retirement funds tracked
- [ ] ✅ Tax deduction limits calculated (27.5%, R350k cap)
- [ ] ✅ Retirement value projections accurate

**IHT Planning (3.7-3.10):**
- [ ] ✅ Estate assets and liabilities tracked
- [ ] ✅ IHT calculated correctly (NRB, RNRB, transferable NRB)
- [ ] ✅ RNRB tapering applied
- [ ] ✅ Gifts and PETs tracked
- [ ] ✅ Taper relief on PETs calculated
- [ ] ✅ Exemptions applied correctly
- [ ] ✅ SA estate duty calculated

**DTA Calculator (3.11-3.12):**
- [ ] ✅ DTA relief calculated for employment income
- [ ] ✅ DTA relief calculated for dividends
- [ ] ✅ DTA relief calculated for capital gains
- [ ] ✅ DTA relief calculated for pensions
- [ ] ✅ Tie-breaker rules applied for dual residents

**Tax Residency (3.13-3.14):**
- [ ] ✅ UK SRT calculated correctly (automatic tests and sufficient ties)
- [ ] ✅ SA physical presence test calculated correctly
- [ ] ✅ Dual residency determined with tie-breakers

### Integration Tests

- [ ] ✅ Full retirement journey: Add pension → Track contributions → View annual allowance → Project retirement income
- [ ] ✅ Full IHT journey: Add estate assets → Calculate IHT → Record gift → View PET tracker
- [ ] ✅ Full DTA journey: Enter dual income → Calculate DTA relief → View net tax
- [ ] ✅ Full residency journey: Calculate UK SRT → Calculate SA presence → Apply tie-breakers → Determine sole residence
- [ ] ✅ Retirement and estate data appear in Central Dashboard
- [ ] ✅ Load test: 100 concurrent users using all Phase 3 features

### Code Quality

- [ ] ✅ Test coverage >80% for all Phase 3 modules
- [ ] ✅ All linting passes (backend and frontend)
- [ ] ✅ API documentation complete for all endpoints
- [ ] ✅ Component documentation complete
- [ ] ✅ No console errors in browser
- [ ] ✅ Mobile responsive on all pages

### Data Quality

- [ ] ✅ Soft deletes work
- [ ] ✅ Historical data retained (audit trails)
- [ ] ✅ Temporal data handled correctly (effective_from/to)
- [ ] ✅ Currency conversion accurate
- [ ] ✅ Tax year handling correct (UK: Apr 6-Apr 5, SA: Mar 1-Feb 28)

### Performance Tests

- [ ] ✅ Retirement dashboard loads in <2 seconds
- [ ] ✅ IHT calculations complete in <500ms
- [ ] ✅ DTA calculations complete in <300ms
- [ ] ✅ SRT calculation <200ms
- [ ] ✅ API responses <500ms (95th percentile)
- [ ] ✅ Database queries optimized (no N+1)

### User Acceptance

- [ ] ✅ Can track UK and SA retirement funds
- [ ] ✅ Annual Allowance clearly displayed with warnings
- [ ] ✅ Retirement income projections clear and interactive
- [ ] ✅ Estate valuation and IHT liability clear
- [ ] ✅ Gift tracker shows PET period clearly
- [ ] ✅ DTA relief calculations understandable
- [ ] ✅ Tax residency determinations clear with explanations
- [ ] ✅ All error messages clear and helpful

**Acceptance Criteria:**
🎯 **Phase 3 Complete**: Users can plan for retirement across UK and SA, manage IHT and estate planning, calculate DTA relief, and determine tax residency accurately.

🎯 **Retirement & IHT Planning**: Comprehensive retirement planning with annual allowance tracking, income projections, estate valuation, and inheritance tax optimization.

🎯 **DTA & Residency**: Accurate double tax agreement relief calculations and tax residency determination using UK SRT and SA physical presence test.

🎯 **Ready for Phase 4**: Codebase clean, tested, documented, and ready to add goal-based planning, AI recommendations, and scenario analysis.

---
