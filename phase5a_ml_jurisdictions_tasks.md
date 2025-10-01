# Phase 5A: ML Predictions & Additional Jurisdictions

**Last Updated:** October 1, 2025
**Timeline:** 2-3 months (Part of Phase 5: 6-8 months total)
**Critical Rule:** ⛔ **DO NOT PROCEED TO NEXT SECTION UNTIL ALL TESTS PASS** ⛔

---

## 📋 Overview

**Goal:** Add ML-powered predictions and expand to support US, EU, and Australian tax systems

**Prerequisites:** Phase 4 complete (Goals, Scenarios, AI, Personalization functional)

**Module Focus:**
- 5.1-5.2: ML-Powered Predictions
- 5.3-5.4: Additional Jurisdictions (US, EU, Australia)

**Outputs:**
- Spending prediction model
- Income forecasting
- Goal success probability predictions
- US tax calculations (federal and state)
- US retirement accounts (401k, IRA, Roth IRA)
- EU tax systems (Germany, France, Ireland, Netherlands)
- Australian tax and superannuation
- Multi-jurisdiction UI support

**Related Files:**
- Next: `phase5b_integrations_tasks.md` - Advanced Integrations
- Then: `phase5c_mobile_scale_tasks.md` - Mobile Apps and Scaling

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
## 5.1 ML-Powered Predictions - Infrastructure

### Task 5.1.1: ML Infrastructure Setup

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Architecture.md`, `performance.md`

**Agent Instructions:**
1. Read Architecture.md for ML service patterns
2. Read performance.md for ML performance requirements
3. Set up ML infrastructure for training and inference

**Tasks:**
- [ ] Set up ML dependencies
  - Install scikit-learn, pandas, numpy
  - Install joblib for model serialization
  - Consider TensorFlow/PyTorch for deep learning (optional)
- [ ] Create ML data pipeline infrastructure
  - `services/ml/data_pipeline.py`
  - Extract training data from database
  - Clean and preprocess data
  - Feature engineering
  - Train/test split
- [ ] Create model storage and versioning
  - `models/` directory for serialized models
  - Version tracking (model_v1.pkl, model_v2.pkl)
  - Model metadata (training date, accuracy metrics)
- [ ] Create `services/ml/model_service.py`
  - Load trained models
  - Run inference
  - Track prediction accuracy
  - Retrain models periodically
- [ ] Implement model evaluation framework
  - Calculate accuracy, precision, recall
  - A/B testing for model versions
  - Monitor model drift
- [ ] **Test Suite:**
  - Test data pipeline
  - Test model loading
  - Test inference
  - Test evaluation metrics
- [ ] **Run:** `pytest tests/services/ml/test_ml_infrastructure.py -v`
- [ ] **Acceptance:** ML infrastructure ready for model development

### Task 5.1.2: Spending Prediction Model

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Personalization.md`, `AIAdvisoryRecommendation.md`

**Agent Instructions:**
1. Read Personalization.md and AIAdvisoryRecommendation.md for prediction use cases
2. Build ML model to predict future spending

**Tasks:**
- [ ] Create `services/ml/spending_prediction.py`
- [ ] Collect training data
  - Historical spending by category (6-12 months)
  - Time-based features (month, day of week, holidays)
  - User features (income, family size, location)
- [ ] Engineer features
  - Moving averages (7-day, 30-day)
  - Spending trends
  - Seasonality indicators
  - One-hot encoding for categories
- [ ] Train model
  - Algorithm: Random Forest or Gradient Boosting
  - Target: Predicted spending next month
  - Train on 80% of data, validate on 20%
- [ ] Implement `predict_next_month_spending()` method
  - Accept user_id
  - Load model
  - Predict spending by category
  - Return predictions with confidence intervals
- [ ] Implement `identify_spending_anomalies()` method
  - Detect unusual spending patterns
  - Flag potential overspending
  - Return anomalies
- [ ] **Test Suite:**
  - Test model training
  - Test predictions
  - Test anomaly detection
  - Validate prediction accuracy (>70%)
- [ ] **Run:** `pytest tests/services/ml/test_spending_prediction.py -v`
- [ ] **Acceptance:** Spending prediction model accurate and useful

### Task 5.1.3: Income Forecasting and Goal Success Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `GoalPlanning.md`, `AIAdvisoryRecommendation.md`

**Agent Instructions:**
1. Build ML models for income forecasting and goal success prediction

**Tasks:**
- [ ] Create `services/ml/income_forecasting.py`
- [ ] Implement `forecast_income()` method
  - Train on historical income data
  - Consider income sources, job changes, bonuses
  - Predict income next 12 months
  - Return forecast with confidence intervals
- [ ] Create `services/ml/goal_success_prediction.py`
- [ ] Implement `predict_goal_success()` method
  - Features: Current progress, time remaining, savings rate, income, spending
  - Target: Probability of achieving goal on time
  - Return success probability (0-100%)
- [ ] Implement `recommend_savings_adjustments()` method
  - Based on success probability
  - Recommend increase in monthly savings to reach target probability (e.g., 90%)
  - Return recommended adjustment
- [ ] **Test Suite:**
  - Test income forecasting
  - Test goal success prediction
  - Test savings recommendations
  - Validate model accuracy
- [ ] **Run:** `pytest tests/services/ml/test_income_forecasting.py -v` and `pytest tests/services/ml/test_goal_success.py -v`
- [ ] **Acceptance:** Income and goal success models provide actionable insights

---

## 5.2 ML-Powered Predictions - Integration

### Task 5.2.1: ML Predictions API and UI

**🐍 DELEGATE TO: `python-backend-engineer`**
**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Personalization.md`, `UserFlows.md`

**Agent Instructions:**
1. Backend: Create API endpoints for ML predictions
2. Frontend: Integrate predictions into UI
3. Display predictions in engaging, understandable way

**Tasks:**
- [ ] **Backend (🐍):** Create `api/v1/ml/predictions.py`
  - **GET /api/v1/ml/predict/spending** - Predict next month spending
    - Require authentication
    - Return predictions by category
  - **GET /api/v1/ml/predict/income** - Forecast income
    - Return 12-month forecast
  - **GET /api/v1/ml/predict/goal-success/{goal_id}** - Predict goal success
    - Return probability and recommended adjustments
  - **GET /api/v1/ml/anomalies/spending** - Get spending anomalies
    - Return unusual spending detected
- [ ] **Backend Test:** `pytest tests/api/ml/test_predictions_api.py -v`
- [ ] **Frontend (⚛️):** Create `components/ml/PredictionsWidget.jsx`
  - Import UI components from 'internal-packages/ui'
  - Display spending prediction
    - Next month predicted spending by category
    - Comparison to current month
    - Visual chart
  - Display income forecast
    - 12-month income projection chart
  - Display goal success probability
    - Success gauge (0-100%)
    - Recommended savings adjustment
- [ ] **Frontend (⚛️):** Create `components/ml/SpendingAnomalies.jsx`
  - Display detected anomalies
  - Flag unusual spending with alerts
- [ ] **Jest Tests:**
  - Test predictions widgets render correctly
  - Test data visualization
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/PredictionsWidget.test.jsx`
- [ ] **Acceptance:** ML predictions integrated and displayed clearly

---

## 🚦 PHASE 5 ML PREDICTIONS TESTING GATE

### Functional Tests

- [ ] ✅ ML infrastructure setup and working
- [ ] ✅ Spending prediction model trained and accurate (>70%)
- [ ] ✅ Income forecasting model trained and accurate
- [ ] ✅ Goal success prediction model provides useful probabilities
- [ ] ✅ Spending anomalies detected correctly
- [ ] ✅ ML predictions displayed in UI

### Performance Tests

- [ ] ✅ Model inference <500ms
- [ ] ✅ Predictions cached appropriately

### Code Quality

- [ ] ✅ Test coverage >80% for ML module
- [ ] ✅ Model versioning tracked
- [ ] ✅ API documentation complete

**Acceptance Criteria:**
🎯 ML predictions provide valuable insights to users for spending, income, and goal achievement

---

## 5.3 Additional Jurisdictions - US Tax System

### Task 5.3.1: US Tax Calculation Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `CoreTaxCalcs.md` (expand for US), `Architecture.md`

**Agent Instructions:**
1. Research US tax system (federal and state)
2. Implement US tax calculations following same pattern as UK/SA
3. Consider federal + state tax complexity

**Tasks:**
- [ ] Create `services/tax/us_tax_service.py`
- [ ] Implement `calculate_federal_income_tax()` method
  - 2024 federal tax brackets (MFJ, Single, HoH):
    - 10%: $0 - $11,000 (Single) / $0 - $22,000 (MFJ)
    - 12%: $11,001 - $44,725 (Single) / $22,001 - $89,075 (MFJ)
    - 22%: $44,726 - $95,375 (Single) / $89,076 - $190,750 (MFJ)
    - 24%: $95,376 - $182,100 (Single) / $190,751 - $364,200 (MFJ)
    - 32%: $182,101 - $231,250 (Single) / $364,201 - $462,500 (MFJ)
    - 35%: $231,251 - $578,125 (Single) / $462,501 - $693,750 (MFJ)
    - 37%: >$578,125 (Single) / >$693,750 (MFJ)
  - Standard deduction: $13,850 (Single), $27,700 (MFJ) for 2024
  - Return federal tax owed
- [ ] Implement `calculate_state_income_tax()` method
  - Support major states (CA, NY, TX, FL, etc.)
  - CA progressive rates (1% - 13.3%)
  - NY progressive rates (4% - 10.9%)
  - TX: No state income tax
  - FL: No state income tax
  - Return state tax owed
- [ ] Implement `calculate_social_security_medicare_tax()` method
  - Social Security: 6.2% on wages up to $160,200 (2024)
  - Medicare: 1.45% on all wages
  - Additional Medicare: 0.9% on wages >$200k (Single), >$250k (MFJ)
  - Return FICA taxes
- [ ] Implement `calculate_us_capital_gains()` method
  - Long-term CGT rates: 0%, 15%, 20% based on income
  - Short-term CGT: Ordinary income rates
  - Return capital gains tax
- [ ] **Test Suite:**
  - Test federal income tax at all brackets
  - Test state taxes for major states
  - Test FICA taxes
  - Test capital gains tax
- [ ] **Run:** `pytest tests/services/tax/test_us_tax.py -v`
- [ ] **Acceptance:** US tax calculations accurate for federal and state

### Task 5.3.2: US Retirement Accounts (401k, IRA, Roth IRA)

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Retirement.md` (expand for US), `Architecture.md`

**Agent Instructions:**
1. Research US retirement accounts (401k, IRA, Roth IRA)
2. Implement models and services for US retirement tracking

**Tasks:**
- [ ] Create `us_retirement_accounts` table
  - Account type (401K, TRADITIONAL_IRA, ROTH_IRA, SEP_IRA, SIMPLE_IRA)
  - Provider, account_number, current_value
  - Contributions (employee, employer match)
  - User_id, created/updated timestamps
- [ ] Create `services/retirement/us_retirement_service.py`
- [ ] Implement `calculate_401k_contribution_limits()` method
  - 2024 limits: $23,000 (under 50), $30,500 (50+)
  - Employer match tracking
  - Return contribution limits and usage
- [ ] Implement `calculate_ira_contribution_limits()` method
  - 2024 limits: $7,000 (under 50), $8,000 (50+)
  - Income phase-out for Roth IRA
  - Return contribution limits
- [ ] Implement `calculate_rmd()` method
  - Required Minimum Distribution (age 73+ as of 2024)
  - RMD = account_balance / life_expectancy_factor
  - Return RMD amount
- [ ] **Test Suite:**
  - Test US retirement account creation
  - Test contribution limits
  - Test RMD calculation
- [ ] **Run:** `pytest tests/services/retirement/test_us_retirement.py -v`
- [ ] **Acceptance:** US retirement accounts tracked with accurate contribution limits

---

## 5.4 Additional Jurisdictions - EU and Australia

### Task 5.4.1: EU Tax Systems (Simplified)

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `CoreTaxCalcs.md` (expand for EU)

**Agent Instructions:**
1. Implement simplified tax calculations for major EU countries
2. Focus on Germany, France, Ireland, Netherlands

**Tasks:**
- [ ] Create `services/tax/eu_tax_service.py`
- [ ] Implement `calculate_germany_tax()` method
  - Progressive rates: 14% - 45%
  - Solidarity surcharge: 5.5% of tax
  - Return total tax
- [ ] Implement `calculate_france_tax()` method
  - Progressive rates: 0% - 45%
  - Social contributions: ~17%
  - Return total tax and contributions
- [ ] Implement `calculate_ireland_tax()` method
  - Standard rate: 20% (€0 - €40k)
  - Higher rate: 40% (>€40k)
  - USC (Universal Social Charge): 0.5% - 8%
  - PRSI (social insurance): 4%
  - Return total tax
- [ ] Implement `calculate_netherlands_tax()` method
  - Box 1 (employment): Progressive 36.97% - 49.5%
  - Box 2 (substantial interest): 26.9%
  - Box 3 (savings/investments): 32% on deemed return
  - Return total tax
- [ ] **Test Suite:**
  - Test each EU country tax calculation
- [ ] **Run:** `pytest tests/services/tax/test_eu_tax.py -v`
- [ ] **Acceptance:** EU tax calculations functional for major countries

### Task 5.4.2: Australia Tax System

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `CoreTaxCalcs.md` (expand for Australia)

**Agent Instructions:**
1. Implement Australian tax calculations

**Tasks:**
- [ ] Create `services/tax/au_tax_service.py`
- [ ] Implement `calculate_income_tax()` method
  - 2024-25 rates:
    - 0%: $0 - $18,200
    - 19%: $18,201 - $45,000
    - 32.5%: $45,001 - $120,000
    - 37%: $120,001 - $180,000
    - 45%: >$180,000
  - Medicare Levy: 2% of taxable income
  - Return tax owed
- [ ] Implement `calculate_superannuation()` method
  - Employer contribution: 11.5% (2024)
  - Concessional cap: $27,500/year
  - Non-concessional cap: $110,000/year
  - Return super calculations
- [ ] **Test Suite:**
  - Test Australian income tax
  - Test Medicare Levy
  - Test superannuation calculations
- [ ] **Run:** `pytest tests/services/tax/test_au_tax.py -v`
- [ ] **Acceptance:** Australian tax calculations accurate

### Task 5.4.3: Multi-Jurisdiction UI Support

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `UserInfo.md`, `UserFlows.md`

**Agent Instructions:**
1. Update UI to support multiple jurisdictions
2. Allow users to select jurisdictions and see relevant features

**Tasks:**
- [ ] Update `components/settings/JurisdictionSelector.jsx`
  - Allow selecting primary and secondary jurisdictions
  - Options: UK, SA, US, Germany, France, Ireland, Netherlands, Australia
  - Save to user profile
- [ ] Update tax calculators to show fields for selected jurisdiction
- [ ] Update retirement module to show relevant accounts (401k for US, Super for AU, etc.)
- [ ] Create jurisdiction-specific help text and tooltips
- [ ] **Jest Tests:**
  - Test jurisdiction selector
  - Test UI adapts to selected jurisdictions
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/JurisdictionSelector.test.jsx`
- [ ] **Acceptance:** UI supports multiple jurisdictions seamlessly

---

## 🚦 PHASE 5 ADDITIONAL JURISDICTIONS TESTING GATE

### Functional Tests

- [ ] ✅ US federal and state income tax calculated correctly
- [ ] ✅ US FICA taxes calculated correctly
- [ ] ✅ US retirement accounts (401k, IRA, Roth IRA) tracked
- [ ] ✅ EU tax calculations accurate for Germany, France, Ireland, Netherlands
- [ ] ✅ Australian income tax and superannuation calculated correctly
- [ ] ✅ UI adapts to selected jurisdictions

### Code Quality

- [ ] ✅ Test coverage >80% for jurisdiction modules
- [ ] ✅ All linting passes
- [ ] ✅ API documentation complete

**Acceptance Criteria:**
🎯 Platform supports US, EU (major countries), and Australia in addition to UK and SA

---


**Next Step:**
➡️ Proceed to `phase5b_integrations_tasks.md` to build Advanced Integrations

---
