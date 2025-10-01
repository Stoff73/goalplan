# Phase 2C: Tax Intelligence & AI Recommendations

**Last Updated:** October 1, 2025
**Timeline:** 1-1.5 months (Part of Phase 2: 4-5 months total)
**Critical Rule:** ⛔ **PHASE 2 TESTING GATE MUST PASS BEFORE PHASE 3** ⛔

---

## 📋 Overview

**Goal:** Build basic tax intelligence engine and rule-based AI recommendation system

**Prerequisites:** 
- Phase 1 complete (authentication, user information, savings module, and dashboard functional)
- Phase 2A complete (Protection module functional)
- Phase 2B complete (Investment module functional)

**Module Focus:**
- 2.9-2.10: Tax Intelligence Engine (Basic Calculations)
- 2.11: Basic AI Recommendations

**Outputs:**
- UK and SA tax calculations (Income Tax, NI, CGT, Dividend Tax)
- Tax summary dashboard
- Rule-based financial recommendations
- Integration with all modules for comprehensive tax view

**Related Files:**
- Previous: `phase2a_protection_tasks.md` - Protection Module
- Previous: `phase2b_investment_tasks.md` - Investment Module  
- Next (after Phase 2 complete): `phase3a_retirement_tasks.md` - Retirement Module

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
## 2.9 Tax Intelligence Engine - Basic Calculations

### Task 2.9.1: UK Tax Calculation Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `CoreTaxCalcs.md`, `Architecture.md`

**Agent Instructions:**
1. Read CoreTaxCalcs.md - Complete UK tax calculation specifications
2. Read Architecture.md for tax calculation service patterns
3. Implement comprehensive UK income tax, NI, CGT, and dividend tax calculations

**Tasks:**
- [ ] Create `services/tax/uk_tax_service.py`
- [ ] Implement `calculate_income_tax()` method
  - 2024/25 rates and bands:
    - Personal allowance: £12,570 (tapered for income >£100k)
    - Basic rate (20%): £12,571 - £50,270
    - Higher rate (40%): £50,271 - £125,140
    - Additional rate (45%): >£125,140
  - Handle personal allowance tapering (£1 reduction per £2 over £100k)
  - Apply Scottish rates if user is Scottish resident
- [ ] Implement `calculate_national_insurance()` method
  - Class 1 NI (employees):
    - 12% on £12,570 - £50,270
    - 2% on >£50,270
  - Class 2 NI (self-employed): £3.45/week if profits >£6,725
  - Class 4 NI (self-employed):
    - 9% on £12,570 - £50,270
    - 2% on >£50,270
- [ ] Implement `calculate_cgt()` method
  - Annual exempt amount: £3,000 (2024/25)
  - Basic rate: 10% (18% for residential property)
  - Higher rate: 20% (24% for residential property)
- [ ] Implement `calculate_dividend_tax()` method
  - Dividend allowance: £500 (2024/25)
  - Basic rate: 8.75%
  - Higher rate: 33.75%
  - Additional rate: 39.35%
- [ ] **Test Suite:**
  - Test income tax at all bands
  - Test personal allowance tapering
  - Test NI calculations (employee and self-employed)
  - Test CGT with annual exempt amount
  - Test dividend tax with allowance
  - Test edge cases (very high income, zero income)
- [ ] **Run:** `pytest tests/services/tax/test_uk_tax.py -v`
- [ ] **Acceptance:** UK tax calculations accurate for 2024/25 tax year

### Task 2.9.2: SA Tax Calculation Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `CoreTaxCalcs.md`

**Agent Instructions:**
1. Read CoreTaxCalcs.md - SA tax calculation specifications
2. Implement SA income tax and CGT calculations

**Tasks:**
- [ ] Create `services/tax/sa_tax_service.py`
- [ ] Implement `calculate_income_tax()` method
  - 2024/25 rates and bands:
    - Primary rebate: R17,235 (under 65)
    - Tax brackets:
      - 18% on R0 - R237,100
      - 26% on R237,101 - R370,500
      - 31% on R370,501 - R512,800
      - 36% on R512,801 - R673,000
      - 39% on R673,001 - R1,817,000
      - 45% on >R1,817,000
  - Handle age-based rebates (secondary, tertiary)
- [ ] Implement `calculate_cgt()` method
  - Inclusion rate:
    - Individuals: 40% of gain
    - Companies: 80% of gain
  - Annual exclusion: R40,000
  - Apply income tax rates to included gain
- [ ] Implement `calculate_dividend_tax()` method
  - Dividend withholding tax: 20%
  - Exemption: First R23,800 per year
- [ ] **Test Suite:**
  - Test SA income tax at all brackets
  - Test age-based rebates
  - Test CGT inclusion rate method
  - Test dividend withholding
  - Test annual exclusions applied
- [ ] **Run:** `pytest tests/services/tax/test_sa_tax.py -v`
- [ ] **Acceptance:** SA tax calculations accurate for 2024/25 tax year

### Task 2.9.3: Tax Summary API Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `CoreTaxCalcs.md`, `taxInformationModule.md`

**Agent Instructions:**
1. Read CoreTaxCalcs.md for calculation requirements
2. Read taxInformationModule.md for tax summary structure
3. Implement endpoints to calculate and return tax summaries

**Tasks:**
- [ ] Create `api/v1/tax/calculations.py`
- [ ] **POST /api/v1/tax/uk/income-tax** - Calculate UK income tax
  - Accept income, allowances, deductions
  - Return tax owed, breakdown by band
- [ ] **POST /api/v1/tax/uk/national-insurance** - Calculate UK NI
  - Accept employment income, self-employed flag
  - Return NI owed, breakdown
- [ ] **POST /api/v1/tax/uk/capital-gains** - Calculate UK CGT
  - Accept total gains, exemptions
  - Return tax owed
- [ ] **POST /api/v1/tax/sa/income-tax** - Calculate SA income tax
  - Accept income, rebates
  - Return tax owed, breakdown
- [ ] **GET /api/v1/tax/summary** - Get user's tax summary
  - Require authentication
  - Aggregate income from all sources (employment, dividends, capital gains)
  - Calculate total UK and SA tax liabilities
  - Return comprehensive summary
- [ ] **Test Suite:**
  - Test all calculation endpoints
  - Test summary aggregation
  - Test authentication required
  - Test validation errors
- [ ] **Run:** `pytest tests/api/tax/test_tax_api.py -v`
- [ ] **Acceptance:** Tax calculation endpoints working accurately

---

## 2.10 Tax Intelligence - Frontend UI

### Task 2.10.1: Tax Summary Dashboard

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `CoreTaxCalcs.md`, `taxInformationModule.md`, `UserFlows.md`

**Agent Instructions:**
1. Read CoreTaxCalcs.md and taxInformationModule.md for tax display requirements
2. Read UserFlows.md for dashboard UX
3. Import UI components from 'internal-packages/ui'
4. Create comprehensive tax summary visualization

**Tasks:**
- [ ] Create `components/tax/TaxSummary.jsx`
- [ ] Import UI components from 'internal-packages/ui' (Card, Table, Progress)
- [ ] Display tax summary sections:
  - UK tax liabilities (Income Tax, NI, CGT, Dividend Tax)
  - SA tax liabilities (Income Tax, CGT, Dividend Withholding)
  - Total tax owed by country
  - Effective tax rate
- [ ] Show income breakdown by source
  - Employment income
  - Dividend income
  - Capital gains
  - Other income
- [ ] Tax efficiency score (0-100)
  - Based on utilization of allowances
  - Suggestions to improve
- [ ] Link to detailed tax calculations
- [ ] Fetch data from tax summary endpoint
- [ ] **Jest Tests:**
  - Test tax summary renders correctly
  - Test breakdown displays
  - Test efficiency score calculation
  - Test loading and error states
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/TaxSummary.test.jsx`
- [ ] **Acceptance:** Tax summary dashboard clear and informative

---

## 2.11 Basic AI Recommendations

### Task 2.11.1: Recommendation Engine Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `AIAdvisoryRecommendation.md`, `Architecture.md`

**Agent Instructions:**
1. Read AIAdvisoryRecommendation.md - Basic recommendation requirements
2. Read Architecture.md for recommendation service patterns
3. Implement rule-based recommendation engine (AI integration in Phase 4)

**Tasks:**
- [ ] Create `services/ai/recommendation_service.py`
- [ ] Implement rule-based recommendations:
  - **Protection:** If coverage_gap > 0, recommend increasing life assurance
  - **ISA:** If ISA contributions < annual allowance, recommend maximizing
  - **TFSA:** If TFSA contributions < annual allowance, recommend using
  - **Emergency Fund:** If cash < 3 months expenses, recommend building emergency fund
  - **Tax Efficiency:** If using GIA but ISA allowance available, recommend moving to ISA
  - **Pension:** If not maximizing employer match, recommend increasing contributions
- [ ] Create `recommendations` table
  - User_id, recommendation_type, priority (HIGH, MEDIUM, LOW)
  - Title, description, action_items
  - Created_date, dismissed flag, completed flag
- [ ] Implement `generate_recommendations()` method
  - Analyze user's financial data
  - Apply rules to identify opportunities
  - Create recommendations sorted by priority
  - Store in database
- [ ] Implement `get_user_recommendations()` method
  - Return active (not dismissed) recommendations
  - Filter by priority or type
- [ ] **Test Suite:**
  - Test each recommendation rule
  - Test priority assignment
  - Test recommendation generation
  - Test filtering
- [ ] **Run:** `pytest tests/services/ai/test_recommendation_service.py -v`
- [ ] **Acceptance:** Basic recommendation engine generating relevant suggestions

### Task 2.11.2: Recommendations API and UI

**🐍 DELEGATE TO: `python-backend-engineer`**
**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `AIAdvisoryRecommendation.md`, `UserFlows.md`

**Agent Instructions:**
1. Backend: Create API endpoints for recommendations
2. Frontend: Create recommendations display component
3. Follow UX patterns from UserFlows.md

**Tasks:**
- [ ] **Backend (🐍):** Create `api/v1/recommendations.py`
  - **GET /api/v1/recommendations** - Get user recommendations
    - Filter by priority, type
    - Return sorted by priority
  - **POST /api/v1/recommendations/{id}/dismiss** - Dismiss recommendation
  - **POST /api/v1/recommendations/{id}/complete** - Mark as completed
- [ ] **Backend Test:** `pytest tests/api/test_recommendations_api.py -v`
- [ ] **Frontend (⚛️):** Create `components/recommendations/RecommendationsList.jsx`
  - Import UI components from 'internal-packages/ui' (Card, Badge, Button)
  - Display recommendations as cards
  - Show priority badge (RED=high, YELLOW=medium, GREEN=low)
  - Show title, description, action items
  - "Dismiss" and "Mark Complete" buttons
  - Filter by priority
- [ ] **Frontend (⚛️):** Add recommendations widget to Central Dashboard
  - Show top 3 high-priority recommendations
  - Link to full recommendations page
- [ ] **Jest Tests:**
  - Test recommendations list renders
  - Test dismiss and complete actions
  - Test priority filtering
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/RecommendationsList.test.jsx`
- [ ] **Acceptance:** Recommendations display and users can interact with them

---

## 🚦 PHASE 2 COMPLETE TESTING GATE

### Security Tests (CRITICAL)

- [ ] ✅ All PII encrypted (policy numbers, account numbers, beneficiary data)
- [ ] ✅ Authentication required on all endpoints
- [ ] ✅ Authorization working (users can't access others' data)
- [ ] ✅ Rate limiting on all mutation endpoints
- [ ] ✅ SQL injection blocked on all endpoints
- [ ] ✅ XSS attempts sanitized
- [ ] ✅ Security audit passes (npm audit / safety check)

### Functional Tests

**Protection Module (2.1-2.4):**
- [ ] ✅ Life assurance policies created, edited, deleted
- [ ] ✅ Beneficiaries managed correctly
- [ ] ✅ Trust details saved for UK policies
- [ ] ✅ Coverage gap calculation accurate
- [ ] ✅ IHT impact determined correctly
- [ ] ✅ Premium reminders configured

**Investment Module (2.5-2.8):**
- [ ] ✅ Investment accounts and holdings created
- [ ] ✅ Holdings price updates recalculate unrealized gains
- [ ] ✅ FIFO selling calculates realized gains correctly
- [ ] ✅ Dividend income recorded
- [ ] ✅ Asset allocation calculations accurate
- [ ] ✅ CGT and dividend tax calculations correct (UK and SA)
- [ ] ✅ EIS/SEIS/VCT holding periods tracked

**Tax Intelligence (2.9-2.10):**
- [ ] ✅ UK income tax calculated correctly
- [ ] ✅ UK NI calculated correctly
- [ ] ✅ UK CGT and dividend tax accurate
- [ ] ✅ SA income tax calculated correctly
- [ ] ✅ SA CGT inclusion rate applied
- [ ] ✅ Tax summary aggregates all sources

**AI Recommendations (2.11):**
- [ ] ✅ Recommendations generated based on rules
- [ ] ✅ Recommendations prioritized correctly
- [ ] ✅ Can dismiss and complete recommendations

### Integration Tests

- [ ] ✅ Full protection journey: Add policy → View coverage gap → Edit beneficiaries → View in dashboard
- [ ] ✅ Full investment journey: Create account → Add holdings → Update prices → View allocation → Sell holding → View tax
- [ ] ✅ Tax summary aggregates data from all modules
- [ ] ✅ Recommendations appear based on user's financial situation
- [ ] ✅ Protection and investment data appear in Central Dashboard net worth
- [ ] ✅ Load test: 100 concurrent users using all features

### Code Quality

- [ ] ✅ Test coverage >80% for all Phase 2 modules
- [ ] ✅ All linting passes (backend and frontend)
- [ ] ✅ API documentation complete for all endpoints
- [ ] ✅ Component documentation complete
- [ ] ✅ No console errors in browser
- [ ] ✅ Mobile responsive on all pages

### Data Quality

- [ ] ✅ Soft deletes work (no hard deletes of financial data)
- [ ] ✅ Historical data retained (audit trails)
- [ ] ✅ Currency conversion uses correct rates
- [ ] ✅ Tax calculations use correct tax year rates
- [ ] ✅ All monetary amounts have currency specified

### Performance Tests

- [ ] ✅ Portfolio dashboard loads in <2 seconds
- [ ] ✅ Tax calculations complete in <500ms
- [ ] ✅ Asset allocation endpoint <300ms
- [ ] ✅ API responses <500ms (95th percentile)
- [ ] ✅ Database queries optimized (no N+1)
- [ ] ✅ Frontend bundle size reasonable (<500KB gzipped)

### User Acceptance

- [ ] ✅ Can add and manage life assurance policies
- [ ] ✅ Coverage gap clearly displayed
- [ ] ✅ Can build and track investment portfolio
- [ ] ✅ Asset allocation visualizations clear
- [ ] ✅ Tax summary accurate and understandable
- [ ] ✅ Recommendations relevant and actionable
- [ ] ✅ All error messages clear and helpful
- [ ] ✅ Net worth in dashboard includes protection and investments

**Acceptance Criteria:**
🎯 **Phase 2 Complete**: Users can track life assurance and investments, view asset allocation, calculate taxes accurately, and receive basic financial recommendations.

🎯 **Protection & Investment Tracking**: Comprehensive tracking of life assurance policies with coverage gap analysis and full investment portfolio management with tax calculations.

🎯 **Ready for Phase 3**: Codebase clean, tested, documented, and ready to add Retirement, IHT Planning, and DTA capabilities.

---
