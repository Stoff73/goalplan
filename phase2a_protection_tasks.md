# Phase 2A: Protection Module

**Last Updated:** October 1, 2025
**Timeline:** 1.5-2 months (Part of Phase 2: 4-5 months total)
**Critical Rule:** ⛔ **DO NOT PROCEED TO NEXT SECTION UNTIL ALL TESTS PASS** ⛔

---

## 📋 Overview

**Goal:** Build life assurance policy tracking with coverage gap analysis and tax treatment

**Prerequisites:** Phase 1 complete (authentication, user information, savings module, and dashboard functional)

**Module Focus:**
- 2.1-2.4: Protection Module (Life Assurance)

**Outputs:**
- Life assurance policy tracking with beneficiary management
- Coverage gap analysis for life insurance
- IHT tax treatment determination
- Integration with Central Dashboard for net worth updates

**Related Files:**
- Next: `phase2b_investment_tasks.md` - Investment Module
- Then: `phase2c_tax_ai_tasks.md` - Tax Intelligence and AI Recommendations

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

# PHASE 2A: PROTECTION MODULE

## 2.1 Protection Module - Data Models

### Task 2.1.1: Life Assurance Policy Database Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Protection.md`, `Architecture.md`, `DataManagement.md`

**Agent Instructions:**
1. Read Protection.md - Feature 4.1: Life Assurance Policy Management
2. Read Architecture.md for modular data model design patterns
3. Read DataManagement.md for temporal data and audit trail requirements
4. Implement complete database models for life assurance policies and beneficiaries

**Tasks:**
- [ ] Create `life_assurance_policies` table with all fields from Protection.md
  - Policy number, provider, country, type, cover amount, currency
  - Premium amount and frequency
  - Start/end dates, written in trust flag
  - Critical illness rider, waiver of premium flags
  - Created/updated timestamps, user_id foreign key
- [ ] Create `policy_beneficiaries` table
  - Name, DOB, relationship, percentage
  - Address, created/updated timestamps
  - Foreign key to life_assurance_policies
- [ ] Create `policy_trust_details` table
  - Trust type, trustees array
  - Trust beneficiaries, created date
  - Foreign key to life_assurance_policies
- [ ] Create `policy_documents` table
  - Document type, file path, upload date
  - File size, mime type
  - Foreign key to life_assurance_policies
- [ ] Add indexes on user_id, policy_number, provider
- [ ] Add CHECK constraints (cover_amount > 0, beneficiary percentages = 100)
- [ ] Implement soft delete (is_deleted flag)
- [ ] **Alembic Migration:**
  - Create migration file for all tables
  - Test upgrade and downgrade
- [ ] **Test Suite:**
  - Test policy creation with valid data
  - Test beneficiary assignment
  - Test trust details storage
  - Test constraint violations (invalid amounts, percentages)
  - Test soft delete functionality
  - Test indexes exist and work
- [ ] **Run:** `pytest tests/models/test_life_assurance.py -v`
- [ ] **Acceptance:** All policy and beneficiary models created, migrated, and tested

### Task 2.1.2: Coverage Calculation Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Protection.md`, `DataManagement.md`

**Agent Instructions:**
1. Read Protection.md - Coverage gap analysis section
2. Read DataManagement.md for calculation storage patterns
3. Implement models for storing coverage needs and gap analysis

**Tasks:**
- [ ] Create `coverage_needs_analysis` table
  - User_id, calculation_date, annual_income
  - Income_multiplier (default 10), outstanding_debts
  - Children_count, education_cost_per_child
  - Funeral_costs, existing_assets
  - Recommended_cover (calculated), coverage_gap (calculated)
  - Effective_from, effective_to (temporal data)
- [ ] Add business logic for recommended cover calculation
- [ ] Create `policy_premium_reminders` table
  - Policy_id, reminder_date, sent flag
  - Reminder_type (email/in-app)
- [ ] **Test Suite:**
  - Test coverage calculation logic
  - Test temporal data (effective_from/to)
  - Test premium reminder creation
- [ ] **Run:** `pytest tests/models/test_coverage.py -v`
- [ ] **Acceptance:** Coverage models complete with calculation logic

---

## 2.2 Protection Module - Business Logic Services

### Task 2.2.1: Policy Management Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Protection.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read Protection.md - Business logic section
2. Read securityCompliance.md for PII encryption requirements
3. Implement service layer for policy CRUD operations

**Tasks:**
- [ ] Create `services/protection/policy_service.py`
- [ ] Implement `create_policy()` method
  - Validate beneficiary percentages sum to 100%
  - Validate cover amount > 0
  - Validate end_date > start_date (if applicable)
  - Encrypt policy_number and beneficiary PII
  - Store policy with audit trail
- [ ] Implement `update_policy()` method with validation
- [ ] Implement `delete_policy()` (soft delete only)
- [ ] Implement `get_user_policies()` with filtering
- [ ] Implement `add_beneficiary()` and `update_beneficiary()` methods
- [ ] **Test Suite:**
  - Test policy creation with valid data
  - Test validation errors (invalid percentages, amounts)
  - Test beneficiary management
  - Test soft delete
  - Test PII encryption
- [ ] **Run:** `pytest tests/services/protection/test_policy_service.py -v`
- [ ] **Acceptance:** Policy service complete with full validation and encryption

### Task 2.2.2: Coverage Gap Analysis Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Protection.md`

**Agent Instructions:**
1. Read Protection.md - Coverage gap calculation formula
2. Implement family needs analysis algorithm
3. Calculate recommended coverage and identify gaps

**Tasks:**
- [ ] Create `services/protection/coverage_analysis_service.py`
- [ ] Implement `calculate_recommended_cover()` method
  - Formula: (annual_income * multiplier) + debts + (children * education_cost) + funeral - assets
  - Default multiplier: 10
  - Education cost per child: Configurable (default £100k UK, R500k SA)
  - Funeral costs: Configurable (default £5k UK, R50k SA)
- [ ] Implement `calculate_coverage_gap()` method
  - Get all user policies
  - Sum total current coverage
  - Gap = recommended - total_current
- [ ] Implement `get_coverage_summary()` method
  - Return current coverage, recommended coverage, gap, gap percentage
- [ ] Store coverage analysis with temporal data (effective_from/to)
- [ ] **Test Suite:**
  - Test recommended cover calculation
  - Test coverage gap calculation
  - Test with multiple policies
  - Test with different family situations
  - Test edge cases (no policies, zero income)
- [ ] **Run:** `pytest tests/services/protection/test_coverage_service.py -v`
- [ ] **Acceptance:** Coverage gap analysis working accurately

### Task 2.2.3: Tax Treatment Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Protection.md`, `IHT.md`

**Agent Instructions:**
1. Read Protection.md - Tax treatment logic
2. Read IHT.md for UK inheritance tax rules
3. Implement tax implications for life assurance policies

**Tasks:**
- [ ] Create `services/protection/tax_treatment_service.py`
- [ ] Implement `determine_iht_impact()` method
  - If UK policy AND written_in_trust = TRUE: outside UK estate
  - If UK policy AND written_in_trust = FALSE: in UK estate
  - Return IHT impact boolean and explanation
- [ ] Implement `determine_sa_estate_duty_impact()` method
  - SA policies generally part of estate
  - Return estate duty impact and percentage
- [ ] Implement `get_policy_tax_summary()` method
  - Return comprehensive tax treatment for policy
- [ ] **Test Suite:**
  - Test UK trust policy (no IHT)
  - Test UK non-trust policy (IHT applies)
  - Test SA policy (estate duty applies)
  - Test edge cases
- [ ] **Run:** `pytest tests/services/protection/test_tax_treatment.py -v`
- [ ] **Acceptance:** Tax treatment logic accurate for UK and SA

---

## 2.3 Protection Module - API Endpoints

### Task 2.3.1: Life Assurance CRUD Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Protection.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read Protection.md - API endpoint specifications
2. Read securityCompliance.md for authentication and rate limiting
3. Implement RESTful endpoints for policy management

**Tasks:**
- [ ] Create `api/v1/protection/life_assurance.py`
- [ ] **POST /api/v1/protection/life-assurance** - Create policy
  - Require authentication
  - Validate request body with Pydantic
  - Call policy_service.create_policy()
  - Return 201 with policy details
- [ ] **GET /api/v1/protection/life-assurance** - List user policies
  - Require authentication
  - Support filtering (provider, type, country)
  - Return paginated results
- [ ] **GET /api/v1/protection/life-assurance/{id}** - Get single policy
  - Require authentication and ownership
  - Return 404 if not found
- [ ] **PUT /api/v1/protection/life-assurance/{id}** - Update policy
  - Require authentication and ownership
  - Validate updates
  - Apply rate limiting (5 updates per minute)
- [ ] **DELETE /api/v1/protection/life-assurance/{id}** - Soft delete policy
  - Require authentication and ownership
  - Soft delete only
- [ ] **POST /api/v1/protection/life-assurance/{id}/beneficiaries** - Add beneficiary
  - Validate percentages sum to 100%
- [ ] **Test Suite:**
  - Test all CRUD operations
  - Test authentication required
  - Test authorization (user can't access others' policies)
  - Test validation errors return 400
  - Test rate limiting
  - Test pagination
- [ ] **Run:** `pytest tests/api/protection/test_life_assurance_api.py -v`
- [ ] **Acceptance:** All policy endpoints functional and secure

### Task 2.3.2: Coverage Analysis Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Protection.md`

**Agent Instructions:**
1. Read Protection.md - Coverage gap analysis requirements
2. Implement endpoints for coverage needs and gap analysis

**Tasks:**
- [ ] **POST /api/v1/protection/coverage-analysis** - Calculate coverage needs
  - Accept annual_income, debts, children_count, etc.
  - Return recommended coverage and gap
- [ ] **GET /api/v1/protection/coverage-summary** - Get current coverage summary
  - Require authentication
  - Return total coverage, recommended, gap, policies contributing
- [ ] **Test Suite:**
  - Test coverage calculation
  - Test summary aggregation
  - Test with no policies
  - Test with multiple policies
- [ ] **Run:** `pytest tests/api/protection/test_coverage_api.py -v`
- [ ] **Acceptance:** Coverage endpoints working accurately

---

## 2.4 Protection Module - Frontend UI

### Task 2.4.1: Policy List Component

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Protection.md`, `UserFlows.md`

**Agent Instructions:**
1. Read Protection.md - User interface requirements
2. Read UserFlows.md for UX principles
3. Import UI components from 'internal-packages/ui'
4. Follow React 19 patterns (no forwardRef)
5. Write comprehensive Jest tests

**Tasks:**
- [ ] Create `components/protection/PolicyList.jsx` component
- [ ] Import UI components from 'internal-packages/ui' (Table, Card, Badge)
- [ ] Display policies in sortable table
  - Columns: Provider, Type, Cover Amount, Premium, Beneficiaries, Actions
  - Support filtering by provider, type, country
  - Show IHT impact badge (green if in trust, yellow if not)
- [ ] Add "Add Policy" button
- [ ] Add edit and delete actions per row
- [ ] Show loading state while fetching
- [ ] Show empty state if no policies
- [ ] Handle errors gracefully
- [ ] **Jest Tests:**
  - Test component renders with policies
  - Test empty state
  - Test loading state
  - Test error state
  - Test filtering
  - Test sorting
  - Test action buttons call correct handlers
  - Mock all API calls
- [ ] **Manual Test:**
  - Add a policy and see it appear
  - Filter and sort policies
  - Edit and delete policies
- [ ] **Component Test (Jest):** `npm test tests/components/PolicyList.test.jsx`
- [ ] **Acceptance:** Policy list displays correctly with all interactions working

### Task 2.4.2: Add/Edit Policy Form

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Protection.md`, `UserFlows.md`

**Agent Instructions:**
1. Read Protection.md - Form field requirements
2. Read UserFlows.md for form UX patterns
3. Import form components from 'internal-packages/ui'
4. Implement comprehensive validation

**Tasks:**
- [ ] Create `components/protection/PolicyForm.jsx` component
- [ ] Import UI components from 'internal-packages/ui' (Form, Input, Select, DatePicker, Checkbox)
- [ ] Form fields:
  - Policy number, provider, country dropdown
  - Policy type dropdown (TERM, WHOLE_OF_LIFE, etc.)
  - Cover amount with currency selector
  - Premium amount and frequency
  - Start/end dates
  - Written in trust checkbox (UK only)
  - Critical illness rider, waiver of premium checkboxes
- [ ] Beneficiary section (dynamic add/remove)
  - Name, DOB, relationship, percentage
  - Auto-calculate total percentage (must = 100%)
  - Show warning if not 100%
- [ ] Trust details section (conditional on written_in_trust)
  - Trust type, trustees
- [ ] Client-side validation
  - Required fields
  - Cover amount > 0
  - End date > start date
  - Beneficiary percentages = 100%
- [ ] Submit to API endpoint
- [ ] Show success message and redirect to policy list
- [ ] **Jest Tests:**
  - Test form renders with all fields
  - Test validation errors display
  - Test beneficiary percentage validation
  - Test conditional fields (trust section)
  - Test form submission
  - Test error handling on submit
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/PolicyForm.test.jsx`
- [ ] **Acceptance:** Policy form fully functional with validation

### Task 2.4.3: Coverage Gap Dashboard Widget

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Protection.md`, `UserFlows.md`

**Agent Instructions:**
1. Read Protection.md - Coverage gap display requirements
2. Create visual dashboard widget showing coverage status
3. Import UI components from 'internal-packages/ui'

**Tasks:**
- [ ] Create `components/protection/CoverageGapWidget.jsx`
- [ ] Import UI components from 'internal-packages/ui' (Card, Progress, Alert)
- [ ] Display coverage summary:
  - Current total coverage
  - Recommended coverage
  - Coverage gap (with visual indicator)
  - Percentage covered (progress bar)
- [ ] Color coding:
  - Green: 100%+ covered
  - Yellow: 70-99% covered
  - Red: <70% covered
- [ ] Link to "Add Policy" if undercovered
- [ ] Fetch data from coverage summary endpoint
- [ ] **Jest Tests:**
  - Test displays coverage data correctly
  - Test color coding for different coverage levels
  - Test loading and error states
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/CoverageGapWidget.test.jsx`
- [ ] **E2E Test (Playwright):** `npx playwright test e2e/protection.spec.js`
- [ ] **Acceptance:** Coverage gap widget shows accurate, visual coverage status

---

## 🚦 PHASE 2A PROTECTION MODULE TESTING GATE

### Security Tests (CRITICAL)

- [ ] ✅ Policy numbers encrypted in database
- [ ] ✅ Beneficiary PII encrypted
- [ ] ✅ Authentication required on all endpoints
- [ ] ✅ Users cannot access others' policies
- [ ] ✅ Rate limiting on policy update endpoint

### Functional Tests

- [ ] ✅ Can create life assurance policy with beneficiaries
- [ ] ✅ Beneficiary percentage validation works
- [ ] ✅ Trust details save correctly for UK policies
- [ ] ✅ Coverage gap calculation accurate
- [ ] ✅ IHT impact determined correctly
- [ ] ✅ Policies display in list
- [ ] ✅ Can edit and delete policies

### Integration Tests

- [ ] ✅ Full journey: Add policy → View in list → View coverage gap → Edit policy → Delete policy
- [ ] ✅ Protection data appears in Central Dashboard net worth

### Code Quality

- [ ] ✅ Test coverage >80% for protection module
- [ ] ✅ All linting passes
- [ ] ✅ API documentation complete

**Acceptance Criteria:**
🎯 Protection module complete: Users can track life assurance policies, see coverage gaps, and understand tax implications

**Next Step:**
➡️ Proceed to `phase2b_investment_tasks.md` to build the Investment Module

---
