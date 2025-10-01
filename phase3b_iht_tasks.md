# Phase 3B: IHT Planning Module

**Last Updated:** October 1, 2025
**Timeline:** 1.5-2 months (Part of Phase 3: 5-6 months total)
**Critical Rule:** ⛔ **DO NOT PROCEED TO NEXT SECTION UNTIL ALL TESTS PASS** ⛔

---

## 📋 Overview

**Goal:** Build inheritance tax planning with estate valuation, gift tracking, and PET management

**Prerequisites:** 
- Phase 2 complete
- Phase 3A complete (Retirement module functional)

**Module Focus:**
- 3.7-3.10: IHT Planning Module

**Outputs:**
- Estate asset and liability tracking
- IHT calculation (NRB, RNRB, transferable NRB)
- Gift and Potentially Exempt Transfer (PET) tracking
- SA Estate Duty calculations
- 7-year PET period visualization

**Related Files:**
- Previous: `phase3a_retirement_tasks.md` - Retirement Module
- Next: `phase3c_dta_residency_tasks.md` - DTA Calculator and Tax Residency

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
## 3.7 IHT Planning Module - Data Models

### Task 3.7.1: Estate Valuation Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `IHT.md`, `Architecture.md`, `DataManagement.md`

**Agent Instructions:**
1. Read IHT.md - Feature 9.1: Estate Valuation for IHT
2. Read Architecture.md for data model patterns
3. Implement comprehensive estate valuation models

**Tasks:**
- [ ] Create `estate_assets` table
  - User_id, asset_type (PROPERTY, INVESTMENTS, PENSIONS, LIFE_ASSURANCE, BUSINESS, OTHER)
  - Description, estimated_value, currency
  - Owned_individually or joint_ownership
  - Included_in_uk_estate flag, included_in_sa_estate flag
  - Effective_from, effective_to (temporal)
  - Created/updated timestamps
- [ ] Create `estate_liabilities` table
  - User_id, liability_type (MORTGAGE, LOAN, CREDIT_CARD, OTHER)
  - Description, amount_outstanding, currency
  - Deductible_from_estate flag
  - Effective_from, effective_to
- [ ] Create `iht_calculations` table
  - User_id, calculation_date, tax_year
  - Gross_estate_value, net_estate_value
  - Nil_rate_band (£325,000), residence_nil_rate_band (£175,000)
  - Transferable_nil_rate_band (from spouse)
  - Total_nil_rate_band_available
  - Taxable_estate, iht_owed (40% on excess)
- [ ] Create `sa_estate_duty_calculations` table
  - User_id, calculation_date
  - Estate_value, abatement (R3.5M)
  - Dutiable_amount, estate_duty_rate (20% on R0-30M, 25% on >30M)
  - Estate_duty_owed
- [ ] Add indexes and constraints
- [ ] **Alembic Migration:**
  - Create migration for estate and IHT tables
- [ ] **Test Suite:**
  - Test estate asset and liability tracking
  - Test IHT calculation storage
  - Test SA estate duty storage
  - Test temporal data
- [ ] **Run:** `pytest tests/models/test_estate_iht.py -v`
- [ ] **Acceptance:** Estate and IHT models complete

### Task 3.7.2: Gifts and PET Tracking Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `IHT.md`, `DataManagement.md`

**Agent Instructions:**
1. Read IHT.md - Gifts and Potentially Exempt Transfers (PET) section
2. Implement models for gift tracking and PET aging

**Tasks:**
- [ ] Create `gifts` table
  - User_id, recipient, gift_date, gift_value, currency
  - Gift_type (PET, EXEMPT, CHARGEABLE)
  - Exemption_type (ANNUAL_EXEMPTION, SMALL_GIFTS, NORMAL_EXPENDITURE, etc.)
  - Becomes_exempt_date (gift_date + 7 years for PET)
  - Still_in_pet_period flag (auto-calculated)
  - Description
- [ ] Create `iht_exemptions` table
  - User_id, tax_year
  - Annual_exemption_used (£3,000/year)
  - Small_gifts_exemption_used (£250/person)
  - Wedding_gifts_exemption_used
- [ ] Add business logic to calculate PET status
  - If gift_date > 7 years ago: exempt
  - If gift_date <= 7 years ago: still in PET period (potentially chargeable)
- [ ] **Test Suite:**
  - Test gift recording
  - Test PET period calculation
  - Test exemption tracking
  - Test 7-year rule
- [ ] **Run:** `pytest tests/models/test_gifts_pets.py -v`
- [ ] **Acceptance:** Gift and PET tracking models complete

---

## 3.8 IHT Planning Module - Business Logic Services

### Task 3.8.1: Estate Valuation Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `IHT.md`

**Agent Instructions:**
1. Read IHT.md - Estate valuation and IHT calculation logic
2. Implement service for estate valuation and IHT calculations

**Tasks:**
- [ ] Create `services/iht/estate_valuation_service.py`
- [ ] Implement `calculate_gross_estate()` method
  - Sum all estate assets included in UK estate
  - Include property, investments, pensions (not in trust), life assurance (not in trust)
  - Return gross estate value
- [ ] Implement `calculate_net_estate()` method
  - Gross estate - deductible liabilities (mortgages, debts)
  - Return net estate value
- [ ] Implement `calculate_iht()` method
  - Nil Rate Band: £325,000 (2024/25)
  - Residence Nil Rate Band: £175,000 (if leaving home to direct descendants)
  - Transferable NRB: Add unused % from deceased spouse
  - Total NRB available = standard NRB + RNRB + transferable NRB
  - Taxable estate = net_estate - total_NRB
  - IHT = taxable_estate * 40%
  - Return IHT owed and breakdown
- [ ] Implement `calculate_residence_nil_rate_band()` method
  - Check if property left to children/grandchildren
  - Check property value (RNRB tapered if estate > £2M)
  - Return applicable RNRB
- [ ] **Test Suite:**
  - Test gross and net estate calculation
  - Test IHT calculation with NRB and RNRB
  - Test transferable NRB from spouse
  - Test RNRB tapering
  - Test various estate values
- [ ] **Run:** `pytest tests/services/iht/test_estate_valuation.py -v`
- [ ] **Acceptance:** Estate valuation and IHT calculations accurate

### Task 3.8.2: Gift and PET Analysis Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `IHT.md`

**Agent Instructions:**
1. Read IHT.md - Gifts, PETs, and exemptions
2. Implement service for gift analysis and PET tracking

**Tasks:**
- [ ] Create `services/iht/gift_analysis_service.py`
- [ ] Implement `record_gift()` method
  - Validate gift data
  - Determine gift type (PET, exempt, chargeable)
  - Apply exemptions (annual, small gifts, etc.)
  - Calculate becomes_exempt_date (gift_date + 7 years)
  - Store gift with audit trail
- [ ] Implement `get_gifts_in_pet_period()` method
  - Return all gifts made in last 7 years
  - Calculate time remaining until exempt
  - Flag high-value PETs
- [ ] Implement `calculate_potential_iht_on_pets()` method
  - If donor dies within 7 years of PET:
    - 0-3 years: 40% IHT on gift (taper relief 0%)
    - 3-4 years: 32% (taper relief 20%)
    - 4-5 years: 24% (taper relief 40%)
    - 5-6 years: 16% (taper relief 60%)
    - 6-7 years: 8% (taper relief 80%)
    - >7 years: 0% (exempt)
  - Return potential IHT on each PET
- [ ] Implement `apply_exemptions()` method
  - Annual exemption: £3,000/year (can carry forward 1 year)
  - Small gifts: £250/person/year
  - Wedding gifts: £5,000 (child), £2,500 (grandchild), £1,000 (other)
  - Normal expenditure out of income
  - Return exemption applied and remaining gift value
- [ ] **Test Suite:**
  - Test gift recording
  - Test PET identification
  - Test taper relief calculation
  - Test exemption application
  - Test carry forward of annual exemption
- [ ] **Run:** `pytest tests/services/iht/test_gift_analysis.py -v`
- [ ] **Acceptance:** Gift and PET analysis accurate

### Task 3.8.3: SA Estate Duty Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `IHT.md`

**Agent Instructions:**
1. Read IHT.md - SA Estate Duty section
2. Implement SA estate duty calculations

**Tasks:**
- [ ] Create `services/iht/sa_estate_duty_service.py`
- [ ] Implement `calculate_estate_duty()` method
  - Gross estate value (all SA assets)
  - Less: Liabilities, funeral expenses
  - Less: Abatement (R3.5M - 2024/25)
  - Dutiable amount = net_estate - abatement
  - Estate duty rates:
    - 20% on R0 - R30M
    - 25% on >R30M
  - Return estate duty owed
- [ ] **Test Suite:**
  - Test SA estate duty calculation
  - Test abatement application
  - Test progressive rates
- [ ] **Run:** `pytest tests/services/iht/test_sa_estate_duty.py -v`
- [ ] **Acceptance:** SA estate duty calculations accurate

---

## 3.9 IHT Planning Module - API Endpoints

### Task 3.9.1: Estate and IHT API Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `IHT.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read IHT.md - API requirements
2. Implement RESTful endpoints for estate management and IHT

**Tasks:**
- [ ] Create `api/v1/iht/estate.py`
- [ ] **POST /api/v1/iht/estate/assets** - Add estate asset
  - Require authentication
  - Validate asset data
  - Return 201
- [ ] **GET /api/v1/iht/estate/assets** - List estate assets
  - Return all user's assets
  - Filter by type
- [ ] **POST /api/v1/iht/estate/liabilities** - Add liability
- [ ] **GET /api/v1/iht/estate/valuation** - Get estate valuation
  - Return gross and net estate values
  - Breakdown by asset type
- [ ] **POST /api/v1/iht/calculate** - Calculate IHT
  - Calculate current IHT liability
  - Return NRBs used, taxable estate, IHT owed
- [ ] **POST /api/v1/iht/gifts** - Record gift
  - Validate gift data
  - Apply exemptions
  - Return gift record with PET status
- [ ] **GET /api/v1/iht/gifts/pet-period** - Get gifts in PET period
  - Return all gifts in last 7 years
  - Show potential IHT if donor dies now
- [ ] **Test Suite:**
  - Test all estate and IHT endpoints
  - Test authentication and authorization
  - Test validation
- [ ] **Run:** `pytest tests/api/iht/test_estate_api.py -v`
- [ ] **Acceptance:** Estate and IHT endpoints functional

---

## 3.10 IHT Planning Module - Frontend UI

### Task 3.10.1: Estate Dashboard

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `IHT.md`, `UserFlows.md`

**Agent Instructions:**
1. Read IHT.md - Estate dashboard requirements
2. Create comprehensive estate planning dashboard
3. Import UI components from 'internal-packages/ui'

**Tasks:**
- [ ] Create `components/iht/EstateDashboard.jsx`
- [ ] Import UI components from 'internal-packages/ui' (Card, Table, Chart, Alert)
- [ ] Display estate summary:
  - Gross estate value
  - Net estate value (after liabilities)
  - Total nil rate bands available
  - Taxable estate
  - IHT owed (with visual impact indicator)
- [ ] Asset breakdown table (Property, Investments, Pensions, etc.)
- [ ] Liabilities table
- [ ] Visual chart showing IHT breakdown
- [ ] Show warnings if estate exceeds NRB
- [ ] Link to add assets and liabilities
- [ ] **Jest Tests:**
  - Test estate dashboard renders correctly
  - Test summary calculations
  - Test asset breakdown
  - Test warnings display
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/EstateDashboard.test.jsx`
- [ ] **Acceptance:** Estate dashboard provides clear estate overview and IHT liability

### Task 3.10.2: Gift and PET Tracker

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `IHT.md`, `UserFlows.md`

**Agent Instructions:**
1. Read IHT.md - Gift tracking requirements
2. Create gift tracker with PET period visualization
3. Import UI components from 'internal-packages/ui'

**Tasks:**
- [ ] Create `components/iht/GiftTracker.jsx`
- [ ] Import UI components from 'internal-packages/ui' (Table, Timeline, Badge, Progress)
- [ ] Display gifts in PET period (last 7 years)
  - Columns: Recipient, Date, Value, Time Until Exempt, Potential IHT
  - Visual timeline showing 7-year period
  - Color-coded by years remaining (red <3 years, yellow 3-5, green >5)
- [ ] Show exemptions used and available (annual, small gifts, etc.)
- [ ] Add "Record Gift" button
- [ ] Create gift form with exemption application
- [ ] Show potential IHT impact if donor dies today
- [ ] **Jest Tests:**
  - Test gift list renders
  - Test PET period calculation
  - Test timeline visualization
  - Test exemption tracking
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/GiftTracker.test.jsx`
- [ ] **E2E Test (Playwright):** `npx playwright test e2e/iht-planning.spec.js`
- [ ] **Acceptance:** Gift tracker provides clear PET period visualization

---

## 🚦 PHASE 3 IHT MODULE TESTING GATE

### Security Tests (CRITICAL)

- [ ] ✅ Authentication required on all IHT endpoints
- [ ] ✅ Users cannot access others' estate data
- [ ] ✅ Sensitive estate data encrypted

### Functional Tests

- [ ] ✅ Estate assets and liabilities tracked correctly
- [ ] ✅ Gross and net estate valuation accurate
- [ ] ✅ IHT calculation correct (NRB, RNRB, transferable NRB)
- [ ] ✅ RNRB tapering applied correctly
- [ ] ✅ Gifts recorded and PET period calculated
- [ ] ✅ Taper relief on PETs calculated correctly
- [ ] ✅ Exemptions applied (annual, small gifts, wedding)
- [ ] ✅ SA estate duty calculated correctly

### Integration Tests

- [ ] ✅ Full journey: Add assets → Add liabilities → View estate valuation → Calculate IHT → Record gift → View PET tracker

### Code Quality

- [ ] ✅ Test coverage >80% for IHT module
- [ ] ✅ All linting passes
- [ ] ✅ API documentation complete

**Acceptance Criteria:**
🎯 IHT Planning module complete: Users can value estate, calculate IHT, track gifts and PETs, and plan to reduce IHT

---


**Next Step:**
➡️ Proceed to `phase3c_dta_residency_tasks.md` to build DTA Calculator and Tax Residency

---
