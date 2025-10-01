# Phase 1B: User Profile & Information Management

**Last Updated:** October 1, 2025
**Timeline:** 1-1.5 months (Part of Phase 1: 3-4 months total)
**Critical Rule:** ⛔ **DO NOT PROCEED TO NEXT SECTION UNTIL ALL TESTS PASS** ⛔

---

## 📋 Overview

**Goal:** Build user profile management, tax status tracking, domicile tracking, and income management

**Prerequisites:** 
- Phase 0 complete (development environment operational)
- Phase 1A complete (Authentication system functional)

**Module Focus:**
- 1.5-1.7: User Information Management

**Outputs:**
- User profile management
- Tax status and domicile tracking (UK and SA)
- Deemed domicile calculation
- Income tracking (employment, self-employment, other)
- Multi-currency support
- Tax year handling (UK and SA)

**Related Files:**
- Previous: `phase1a_authentication_tasks.md` - Authentication System
- Next: `phase1c_dashboard_savings_tasks.md` - Dashboard and Savings Module

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
## 1.5 User Profile Management

### Task 1.5.1: Profile Data Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `DataManagement.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read userAuth.md for user table structure
2. Read DataManagement.md for audit requirements
3. Read securityCompliance.md for data protection
4. Extend user model with profile fields

**Tasks:**
- [ ] Add profile fields to users table (phone, date_of_birth, address, timezone)
- [ ] Create `user_profile_history` table for audit trail
- [ ] Add indexes for efficient queries
- [ ] Create Pydantic models for profile updates
- [ ] **Test Suite:**
  - Test profile model creation
  - Test profile update with history tracking
  - Test data validation (phone format, date ranges)
  - Test timezone handling
- [ ] **Run:** `pytest tests/models/test_user_profile.py -v`
- [ ] **Acceptance:** Profile model tests pass

### Task 1.5.2: Get Profile Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read userAuth.md for user data structure
2. Read securityCompliance.md for PII protection
3. Return only safe, non-sensitive data
4. Require authentication

**Tasks:**
- [ ] Create `GET /api/v1/user/profile` endpoint (authenticated)
- [ ] Return user profile data (excluding password, sensitive fields)
- [ ] Include account status and metadata
- [ ] **Test Suite:**
  - Test authenticated user can get own profile
  - Test unauthenticated request rejected (401)
  - Test sensitive fields not returned
  - Test response structure correct
- [ ] **Run:** `pytest tests/api/user/test_get_profile.py -v`
- [ ] **Acceptance:** Get profile works securely

### Task 1.5.3: Update Profile Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `DataManagement.md`

**Agent Instructions:**
1. Read userAuth.md for allowed profile fields
2. Read DataManagement.md for audit trail requirements
3. Implement partial updates (PATCH semantics)
4. Track all changes in history table

**Tasks:**
- [ ] Create `PATCH /api/v1/user/profile` endpoint
- [ ] Allow updates: firstName, lastName, phone, dateOfBirth, address, timezone
- [ ] Validate all input data
- [ ] Log changes to profile_history table
- [ ] Email notification on profile change
- [ ] **Test Suite:**
  - Test successful profile update
  - Test partial update (only some fields)
  - Test invalid data rejected
  - Test history recorded
  - Test email notification sent
- [ ] **Run:** `pytest tests/api/user/test_update_profile.py -v`
- [ ] **Acceptance:** Profile updates work with audit trail

### Task 1.5.4: Change Password Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`, `riskMitigation.md`

**Agent Instructions:**
1. Read userAuth.md for password requirements
2. Read securityCompliance.md for password security
3. Read riskMitigation.md for account takeover prevention
4. Require current password verification

**Tasks:**
- [ ] Create `POST /api/v1/user/change-password` endpoint
- [ ] Require current password verification
- [ ] Validate new password meets complexity requirements
- [ ] Hash new password with Argon2
- [ ] Invalidate all existing sessions except current
- [ ] Send email notification
- [ ] **Test Suite:**
  - Test password change with correct current password
  - Test wrong current password rejected
  - Test weak new password rejected
  - Test all other sessions invalidated
  - Test email sent
- [ ] **Run:** `pytest tests/api/user/test_change_password.py -v`
- [ ] **Acceptance:** Password change works securely

### Task 1.5.5: Change Email Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read userAuth.md for email verification flow
2. Implement 2-step verification (new and old email)
3. Prevent email conflicts
4. Require password confirmation

**Tasks:**
- [ ] Create `POST /api/v1/user/change-email` endpoint
- [ ] Require password confirmation
- [ ] Check new email not already in use
- [ ] Send verification to new email
- [ ] Send notification to old email
- [ ] Update email only after verification
- [ ] **Test Suite:**
  - Test email change request
  - Test duplicate email rejected
  - Test verification emails sent
  - Test email updated after verification
  - Test notifications sent
- [ ] **Run:** `pytest tests/api/user/test_change_email.py -v`
- [ ] **Acceptance:** Email change secure and verified

### Task 1.5.6: Delete Account Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`, `DataManagement.md`

**Agent Instructions:**
1. Read securityCompliance.md for GDPR/POPIA compliance
2. Read DataManagement.md for data retention
3. Implement soft delete with retention period
4. Allow data export before deletion

**Tasks:**
- [ ] Create `POST /api/v1/user/delete-account` endpoint
- [ ] Require password confirmation
- [ ] Implement soft delete (mark deleted, retain 30 days)
- [ ] Provide data export option
- [ ] Anonymize user data after retention period
- [ ] Send confirmation email
- [ ] **Test Suite:**
  - Test account deletion request
  - Test password required
  - Test account marked deleted
  - Test user cannot login after deletion
  - Test data export generated
- [ ] **Run:** `pytest tests/api/user/test_delete_account.py -v`
- [ ] **Acceptance:** Account deletion GDPR/POPIA compliant

### Task 1.5.7: Profile Management UI

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `userAuth.md`, `UserFlows.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read userAuth.md for profile fields
2. Read UserFlows.md for UX principles
3. Import UI components from 'internal-packages/ui'
4. Keep forms simple and clear
5. Write comprehensive Jest tests

**Tasks:**
- [ ] Create profile page component
- [ ] Import form components from 'internal-packages/ui'
- [ ] Display current profile data
- [ ] Editable fields: name, phone, address, timezone
- [ ] Change password section
- [ ] Change email section
- [ ] Delete account section (with confirmation)
- [ ] Form validation
- [ ] Success/error message handling
- [ ] **Jest Tests:**
  - Test profile data display
  - Test form validation
  - Test profile update submission
  - Test password change flow
  - Test email change flow
  - Test delete account confirmation
  - Mock all API calls
- [ ] **Manual Test:**
  - View profile page
  - Update profile fields
  - Change password
  - Change email
  - Test delete account flow
- [ ] **Component Test (Jest):** `tests/components/UserProfile.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/user-profile.spec.js`
- [ ] **Acceptance:** Profile management works completely

---

## 1.6 User Information Module - Tax Status

### Task 1.6.1: Tax Status Data Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `TaxResidency.md`, `DataManagement.md`

**Agent Instructions:**
1. Read UserInfo.md - Feature 2.1 complete section
2. Read TaxResidency.md for SRT and SA presence test requirements
3. Read DataManagement.md for temporal data handling
4. Implement exact table structures from UserInfo.md

**Tasks:**
- [ ] Create `user_tax_status` table (temporal data)
- [ ] Create `uk_srt_data` table
- [ ] Create `sa_presence_data` table
- [ ] Add appropriate indexes for temporal queries
- [ ] Create Pydantic models
- [ ] Implement effective_from/effective_to logic
- [ ] **Test Suite:**
  - Test tax status record creation
  - Test temporal validity (no overlaps)
  - Test effective date handling
  - Test domicile calculation logic
  - Test dual residency detection
- [ ] **Run:** `pytest tests/models/test_tax_status.py -v`
- [ ] **Acceptance:** Tax status models work with temporal logic

### Task 1.6.2: Deemed Domicile Calculation Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `TaxResidency.md`

**Agent Instructions:**
1. Read UserInfo.md - Business Logic section (deemed domicile calculation)
2. Implement exact formula from specification
3. Handle edge cases (split year, non-residence)
4. Cache results for performance

**Tasks:**
- [ ] Create deemed domicile calculation service
- [ ] Implement 15/20 year rule
- [ ] Implement domicile of origin rule
- [ ] Handle temporary non-residence
- [ ] **Test Suite:**
  - Test 15 out of 20 years triggers deemed domicile
  - Test domicile of origin rule
  - Test edge cases (exactly 15 years, split years)
  - Test performance (<100ms)
- [ ] **Run:** `pytest tests/services/test_deemed_domicile.py -v`
- [ ] **Acceptance:** Deemed domicile calculated correctly

### Task 1.6.3: UK Statutory Residence Test (SRT) Calculator

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `TaxResidency.md`

**Agent Instructions:**
1. Read TaxResidency.md - Complete UK SRT section
2. Implement automatic overseas test
3. Implement automatic UK test
4. Implement sufficient ties test
5. Follow exact HMRC rules

**Tasks:**
- [ ] Create SRT calculator service
- [ ] Implement automatic overseas test (< 16 days)
- [ ] Implement automatic UK test (>= 183 days)
- [ ] Implement sufficient ties test (5 ties)
- [ ] Calculate ties based on user data
- [ ] Store calculation results
- [ ] **Test Suite:**
  - Test automatic overseas (< 16 days)
  - Test automatic UK (>= 183 days)
  - Test sufficient ties scenarios
  - Test tie calculations (family, accommodation, work, etc.)
  - Test edge cases
- [ ] **Run:** `pytest tests/services/test_srt_calculator.py -v`
- [ ] **Acceptance:** SRT calculator accurate to HMRC rules

### Task 1.6.4: SA Physical Presence Test Calculator

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `TaxResidency.md`

**Agent Instructions:**
1. Read TaxResidency.md - SA physical presence test section
2. Implement 91-day rule (current year)
3. Implement 5-year average rule
4. Handle ordinarily resident status

**Tasks:**
- [ ] Create SA presence test calculator
- [ ] Implement 91 days in current year test
- [ ] Implement 91 days average over 5 years test
- [ ] Determine ordinarily resident status
- [ ] Store calculation results
- [ ] **Test Suite:**
  - Test 91 days current year
  - Test 5-year average calculation
  - Test ordinarily resident determination
  - Test edge cases (exactly 91 days)
- [ ] **Run:** `pytest tests/services/test_sa_presence.py -v`
- [ ] **Acceptance:** SA presence test accurate to SARS rules

### Task 1.6.5: Tax Status Management Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `performance.md`

**Agent Instructions:**
1. Read UserInfo.md - API Endpoints section complete
2. Read performance.md for response time targets
3. Implement temporal data management
4. Trigger recalculation on save

**Tasks:**
- [ ] Create `POST /api/v1/user/tax-status` endpoint
- [ ] Create `GET /api/v1/user/tax-status` endpoint (current)
- [ ] Create `GET /api/v1/user/tax-status/history` endpoint
- [ ] Create `GET /api/v1/user/tax-status/at-date?date={date}` endpoint
- [ ] Create `POST /api/v1/user/tax-status/srt-calculator` endpoint
- [ ] Create `POST /api/v1/user/tax-status/sa-presence-test` endpoint
- [ ] Implement validation (no overlaps, valid combinations)
- [ ] Auto-adjust previous record's effective_to on new insert
- [ ] Calculate deemed domicile and DTA tie-breaker
- [ ] **Test Suite:**
  - Test create new tax status
  - Test temporal validity maintained
  - Test history retrieval
  - Test at-date queries
  - Test calculators work
  - Test validation rules
- [ ] **Run:** `pytest tests/api/user/test_tax_status.py -v`
- [ ] **Acceptance:** Tax status management works completely

### Task 1.6.6: Tax Status UI Components

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `UserInfo.md`, `UserFlows.md`, `TaxResidency.md`

**Agent Instructions:**
1. Read UserInfo.md - User Flow section
2. Read UserFlows.md for UX principles
3. Import UI components from 'internal-packages/ui'
4. Create clear, simple forms for complex data
5. Write comprehensive Jest tests

**Tasks:**
- [ ] Create tax status form component
- [ ] Import UI components from 'internal-packages/ui'
- [ ] Effective date picker
- [ ] UK tax resident toggle
- [ ] SA tax resident toggle
- [ ] Domicile selection dropdown
- [ ] Years in UK/SA inputs
- [ ] Remittance basis selection (if applicable)
- [ ] Show calculated status preview
- [ ] SRT calculator modal
- [ ] SA presence test calculator modal
- [ ] Historical status timeline view
- [ ] **Jest Tests:**
  - Test form validation
  - Test calculated status display
  - Test SRT calculator integration
  - Test SA presence test integration
  - Test history timeline rendering
  - Mock all API calls
- [ ] **Manual Test:**
  - Create new tax status
  - Use SRT calculator
  - Use SA presence test
  - View history timeline
  - See calculated deemed domicile
- [ ] **Component Test (Jest):** `tests/components/TaxStatus.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/tax-status.spec.js`
- [ ] **Acceptance:** Tax status management UI complete

---

## 1.7 User Information Module - Income Tracking

### Task 1.7.1: Income Data Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `CoreTaxCalcs.md`, `DataManagement.md`

**Agent Instructions:**
1. Read UserInfo.md - Feature 2.2 complete section
2. Read CoreTaxCalcs.md for tax calculation integration
3. Read DataManagement.md for multi-currency handling
4. Support UK and SA tax years

**Tasks:**
- [ ] Create `user_income` table
- [ ] Create `income_tax_withholding` table
- [ ] Add indexes for tax year queries
- [ ] Create Pydantic models
- [ ] Implement currency conversion metadata storage
- [ ] **Test Suite:**
  - Test income record creation
  - Test multi-currency support
  - Test tax year allocation
  - Test gross/net income handling
  - Test PAYE/PASE data storage
- [ ] **Run:** `pytest tests/models/test_income.py -v`
- [ ] **Acceptance:** Income models support all requirements

### Task 1.7.2: Currency Conversion Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `performance.md`, `integration.md`

**Agent Instructions:**
1. Read UserInfo.md for currency conversion requirements
2. Read integration.md for exchange rate API options
3. Cache rates for performance
4. Use official HMRC/SARS rates where applicable

**Tasks:**
- [ ] Integrate exchange rate API (exchangerate-api.com or similar)
- [ ] Create currency conversion service
- [ ] Store historical exchange rates
- [ ] Implement rate caching (daily updates)
- [ ] Support GBP, ZAR, USD, EUR minimum
- [ ] **Test Suite:**
  - Test currency conversion accuracy
  - Test historical rate lookup
  - Test caching mechanism
  - Test fallback on API failure
- [ ] **Run:** `pytest tests/services/test_currency_conversion.py -v`
- [ ] **Acceptance:** Currency conversion accurate and cached

### Task 1.7.3: Income Tax Treatment Calculator

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `CoreTaxCalcs.md`, `DTA.md`

**Agent Instructions:**
1. Read UserInfo.md - Business Logic section
2. Read CoreTaxCalcs.md for UK and SA tax rules
3. Read DTA.md for foreign income treatment
4. Determine tax treatment based on source and residency

**Tasks:**
- [ ] Create income tax treatment service
- [ ] Determine applicable jurisdiction (UK, SA, both, neither)
- [ ] Apply PSA exemption (UK interest)
- [ ] Apply SA interest exemption
- [ ] Handle foreign income based on DTA
- [ ] Calculate expected tax liability
- [ ] **Test Suite:**
  - Test UK source income for UK resident
  - Test foreign income for UK resident (different domiciles)
  - Test SA source income for SA resident
  - Test dual resident scenarios
  - Test exemptions (PSA, SA interest)
- [ ] **Run:** `pytest tests/services/test_income_tax_treatment.py -v`
- [ ] **Acceptance:** Tax treatment calculated correctly

### Task 1.7.4: Income Management Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `performance.md`

**Agent Instructions:**
1. Read UserInfo.md - API Endpoints section
2. Implement CRUD operations
3. Support filtering by tax year
4. Calculate aggregates

**Tasks:**
- [ ] Create `POST /api/v1/user/income` endpoint
- [ ] Create `GET /api/v1/user/income` endpoint (with filters)
- [ ] Create `GET /api/v1/user/income/:id` endpoint
- [ ] Create `PATCH /api/v1/user/income/:id` endpoint
- [ ] Create `DELETE /api/v1/user/income/:id` endpoint (soft delete)
- [ ] Create `GET /api/v1/user/income/summary?taxYear={year}` endpoint
- [ ] Implement tax year filtering
- [ ] Calculate total income aggregates
- [ ] Convert all to base currency
- [ ] **Test Suite:**
  - Test create income record
  - Test retrieve all income
  - Test filter by tax year
  - Test update income
  - Test delete income
  - Test summary calculations
  - Test currency conversion
- [ ] **Run:** `pytest tests/api/user/test_income.py -v`
- [ ] **Acceptance:** Income management endpoints complete

### Task 1.7.5: Income Tracking UI

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `UserInfo.md`, `UserFlows.md`

**Agent Instructions:**
1. Read UserInfo.md - Feature 2.2 complete section
2. Read UserFlows.md for UX principles
3. Import UI components from 'internal-packages/ui'
4. Support multiple income entries
5. Write comprehensive Jest tests

**Tasks:**
- [ ] Create income list view component
- [ ] Create income form component (add/edit)
- [ ] Import UI components from 'internal-packages/ui'
- [ ] Income type dropdown
- [ ] Source country selection
- [ ] Amount and currency inputs
- [ ] Frequency selection
- [ ] Tax year selection
- [ ] PAYE/PASE details section
- [ ] Gross/net toggle
- [ ] Tax withheld input
- [ ] Income summary by tax year
- [ ] Total income display (converted to base currency)
- [ ] **Jest Tests:**
  - Test income list rendering
  - Test add income form
  - Test edit income
  - Test delete income
  - Test summary calculations
  - Test currency conversion display
  - Mock all API calls
- [ ] **Manual Test:**
  - Add employment income
  - Add foreign income
  - View income summary
  - Filter by tax year
  - See total in GBP and ZAR
- [ ] **Component Test (Jest):** `tests/components/IncomeTracking.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/income-tracking.spec.js`
- [ ] **Acceptance:** Income tracking UI complete

---


**Next Step:**
➡️ Proceed to `phase1c_dashboard_savings_tasks.md` to build Central Dashboard and Savings Module

---
