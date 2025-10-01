# Phase 4A: Goal Planning & Scenario Analysis

**Last Updated:** October 1, 2025
**Timeline:** 2-2.5 months (Part of Phase 4: 4-5 months total)
**Critical Rule:** ⛔ **DO NOT PROCEED TO NEXT SECTION UNTIL ALL TESTS PASS** ⛔

---

## 📋 Overview

**Goal:** Build intelligent goal-based planning and comprehensive scenario modeling

**Prerequisites:** Phase 3 complete (Retirement, IHT, DTA, Tax Residency functional)

**Module Focus:**
- 4.1-4.3: Goal-Based Financial Planning
- 4.4-4.6: Scenario Analysis and What-If Modeling

**Outputs:**
- SMART financial goals with progress tracking
- Goal prioritization and optimization
- Scenario modeling (retirement age, career change, property purchase)
- Monte Carlo simulations for retirement planning
- Interactive what-if analysis

**Related Files:**
- Next: `phase4b_ai_personalization_tasks.md` - AI Advisory and Personalization

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
## 4.1 Goal-Based Planning - Data Models

### Task 4.1.1: Financial Goals Database Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `GoalPlanning.md`, `Architecture.md`, `DataManagement.md`

**Agent Instructions:**
1. Read GoalPlanning.md - Complete goal-based planning specifications
2. Read Architecture.md for data model patterns
3. Read DataManagement.md for temporal tracking
4. Implement comprehensive goal management models

**Tasks:**
- [ ] Create `financial_goals` table
  - User_id, goal_name, goal_type (RETIREMENT, PROPERTY_PURCHASE, EDUCATION, EMERGENCY_FUND, DEBT_PAYOFF, CUSTOM)
  - Target_amount, currency
  - Current_amount (calculated from linked accounts)
  - Target_date, start_date
  - Priority (HIGH, MEDIUM, LOW)
  - Status (NOT_STARTED, IN_PROGRESS, ON_TRACK, AT_RISK, ACHIEVED, ABANDONED)
  - Linked_accounts (array of account IDs)
  - Auto_contribution flag, contribution_amount, contribution_frequency
  - Created/updated timestamps
- [ ] Create `goal_milestones` table
  - Goal_id (foreign key)
  - Milestone_name, milestone_target_amount
  - Milestone_target_date, achieved_date
  - Status (PENDING, ACHIEVED, MISSED)
- [ ] Create `goal_progress_history` table
  - Goal_id, snapshot_date
  - Amount_at_snapshot, target_amount_at_snapshot
  - Progress_percentage, on_track flag
  - Projected_completion_date
  - Effective_from, effective_to (temporal)
- [ ] Create `goal_recommendations` table
  - Goal_id, recommendation_type
  - Recommendation_text, action_items
  - Priority, created_date, dismissed flag
- [ ] Add indexes on user_id, goal_id, goal_type, status
- [ ] Add CHECK constraints (target_amount > 0, target_date > start_date)
- [ ] Implement soft delete
- [ ] **Alembic Migration:**
  - Create migration for goals tables
  - Test upgrade and downgrade
- [ ] **Test Suite:**
  - Test goal creation with all types
  - Test milestone tracking
  - Test progress history with temporal data
  - Test goal recommendations
  - Test constraints and indexes
- [ ] **Run:** `pytest tests/models/test_goals.py -v`
- [ ] **Acceptance:** Goal planning models complete with temporal tracking

---

## 4.2 Goal-Based Planning - Business Logic Services

### Task 4.2.1: Goal Management Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `GoalPlanning.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read GoalPlanning.md - Goal management requirements
2. Implement service for creating and managing financial goals

**Tasks:**
- [ ] Create `services/goals/goal_service.py`
- [ ] Implement `create_goal()` method
  - Validate goal data (SMART criteria)
  - Set initial status (NOT_STARTED or IN_PROGRESS)
  - Link to user accounts if specified
  - Create initial progress snapshot
  - Store with audit trail
- [ ] Implement `update_goal_progress()` method
  - Calculate current_amount from linked accounts
  - Calculate progress_percentage = (current / target) * 100
  - Determine if on_track based on time elapsed vs progress
  - Project completion date based on current rate
  - Update status (ON_TRACK, AT_RISK, ACHIEVED)
  - Store progress snapshot
- [ ] Implement `calculate_monthly_savings_needed()` method
  - Shortfall = target_amount - current_amount
  - Months_remaining = (target_date - today).months
  - Monthly_needed = shortfall / months_remaining
  - Return monthly savings required to stay on track
- [ ] Implement `link_account_to_goal()` method
  - Link savings account, ISA, or investment account to goal
  - Auto-track contributions from that account
- [ ] Implement `create_milestone()` method
  - Add milestone to goal
  - Track achievement
- [ ] Implement `check_goal_achievements()` method
  - Check if current_amount >= target_amount
  - Mark goal as ACHIEVED if met
  - Trigger celebration notification
- [ ] **Test Suite:**
  - Test goal creation
  - Test progress calculation
  - Test on-track determination
  - Test monthly savings calculation
  - Test account linking
  - Test milestone creation and tracking
  - Test goal achievement
- [ ] **Run:** `pytest tests/services/goals/test_goal_service.py -v`
- [ ] **Acceptance:** Goal management service complete with accurate tracking

### Task 4.2.2: Goal Optimization Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `GoalPlanning.md`

**Agent Instructions:**
1. Read GoalPlanning.md - Goal optimization requirements
2. Implement intelligent goal prioritization and allocation

**Tasks:**
- [ ] Create `services/goals/goal_optimization_service.py`
- [ ] Implement `prioritize_goals()` method
  - Consider user-set priority (HIGH, MEDIUM, LOW)
  - Consider urgency (time until target_date)
  - Consider shortfall amount
  - Return prioritized list of goals
- [ ] Implement `allocate_available_savings()` method
  - Take total_available_monthly_savings
  - Allocate to goals based on priority
  - Ensure high-priority goals funded first
  - Return allocation breakdown
- [ ] Implement `identify_conflicting_goals()` method
  - Check if total monthly savings needed > available
  - Identify goals that conflict (same target dates, insufficient funds)
  - Return conflicts and recommendations
- [ ] Implement `suggest_goal_adjustments()` method
  - If goal at risk: Suggest increasing contributions or extending target date
  - If conflicting goals: Suggest re-prioritization or adjustments
  - Return suggestions
- [ ] **Test Suite:**
  - Test goal prioritization
  - Test savings allocation
  - Test conflict detection
  - Test adjustment suggestions
- [ ] **Run:** `pytest tests/services/goals/test_goal_optimization.py -v`
- [ ] **Acceptance:** Goal optimization provides intelligent prioritization and allocation

---

## 4.3 Goal-Based Planning - API and UI

### Task 4.3.1: Goals API Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `GoalPlanning.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read GoalPlanning.md - API requirements
2. Implement RESTful endpoints for goal management

**Tasks:**
- [ ] Create `api/v1/goals/goals.py`
- [ ] **POST /api/v1/goals** - Create financial goal
  - Require authentication
  - Validate SMART criteria
  - Return 201 with goal details
- [ ] **GET /api/v1/goals** - List user goals
  - Filter by type, status, priority
  - Sort by priority or target_date
  - Return goals with progress
- [ ] **GET /api/v1/goals/{id}** - Get single goal
  - Include progress, milestones, recommendations
- [ ] **PUT /api/v1/goals/{id}** - Update goal
  - Allow adjusting target, date, priority
  - Recalculate progress and projections
- [ ] **POST /api/v1/goals/{id}/milestones** - Add milestone
- [ ] **POST /api/v1/goals/{id}/link-account** - Link account to goal
- [ ] **GET /api/v1/goals/overview** - Goals dashboard
  - Total goals, goals on track, at risk
  - Total monthly savings needed
  - Allocation recommendations
- [ ] **POST /api/v1/goals/optimize** - Optimize goal allocation
  - Accept available_monthly_savings
  - Return optimized allocation
- [ ] **Test Suite:**
  - Test all CRUD operations
  - Test authentication and authorization
  - Test validation
  - Test optimization endpoint
- [ ] **Run:** `pytest tests/api/goals/test_goals_api.py -v`
- [ ] **Acceptance:** Goals API functional and secure

### Task 4.3.2: Goals Dashboard UI

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `GoalPlanning.md`, `UserFlows.md`

**Agent Instructions:**
1. Read GoalPlanning.md - UI requirements
2. Read UserFlows.md for goal UX patterns
3. Import UI components from 'internal-packages/ui'
4. Create engaging goal tracking interface

**Tasks:**
- [ ] Create `components/goals/GoalsDashboard.jsx`
- [ ] Import UI components from 'internal-packages/ui' (Card, Progress, Chart, Badge)
- [ ] Display goals overview:
  - Total goals, goals on track (green), at risk (yellow), achieved (blue)
  - Total monthly savings allocated to goals
  - Visual progress chart for all active goals
- [ ] Goal cards with progress bars
  - Goal name, type icon, target amount
  - Current amount and progress %
  - On-track indicator (✓ or ⚠)
  - Target date and time remaining
  - Link to goal details
- [ ] Filter by type, status, priority
- [ ] Sort by priority, target date, progress
- [ ] Add "Create Goal" button
- [ ] Create `components/goals/GoalForm.jsx`
  - Goal type selector (with icons)
  - Target amount and currency
  - Target date picker
  - Priority selector
  - Linked accounts (multi-select)
  - Auto-contribution setup
  - SMART criteria validation (Specific, Measurable, Achievable, Relevant, Time-bound)
- [ ] Create `components/goals/GoalDetails.jsx`
  - Full goal information
  - Progress chart over time
  - Milestones timeline with checkmarks
  - Monthly savings required
  - Recommendations section
  - Edit and delete actions
- [ ] **Jest Tests:**
  - Test goals dashboard renders correctly
  - Test goal cards display progress accurately
  - Test filtering and sorting
  - Test goal form validation
  - Test goal details view
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/GoalsDashboard.test.jsx`
- [ ] **E2E Test (Playwright):** `npx playwright test e2e/goals.spec.js`
- [ ] **Acceptance:** Goals dashboard provides motivating, clear goal tracking

---

## 🚦 PHASE 4 GOAL PLANNING TESTING GATE

### Functional Tests

- [ ] ✅ Financial goals created with SMART validation
- [ ] ✅ Progress calculated accurately based on linked accounts
- [ ] ✅ On-track status determined correctly
- [ ] ✅ Monthly savings needed calculated
- [ ] ✅ Milestones tracked and achieved
- [ ] ✅ Goal optimization allocates savings intelligently
- [ ] ✅ Conflicting goals identified
- [ ] ✅ Goal achievements celebrated

### Integration Tests

- [ ] ✅ Full journey: Create goal → Link account → Track progress → Achieve milestone → Reach goal

### Code Quality

- [ ] ✅ Test coverage >80% for goals module
- [ ] ✅ All linting passes
- [ ] ✅ API documentation complete

**Acceptance Criteria:**
🎯 Goal planning complete: Users can set financial goals, track progress, and get optimization recommendations

---

## 4.4 Scenario Analysis - Data Models and Services

### Task 4.4.1: Scenario Models and Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `ScenarioWhatif.md`, `Architecture.md`, `DataManagement.md`

**Agent Instructions:**
1. Read ScenarioWhatif.md - Complete scenario analysis specifications
2. Read Architecture.md for modeling patterns
3. Implement scenario modeling infrastructure

**Tasks:**
- [ ] Create `scenarios` table
  - User_id, scenario_name, scenario_type (RETIREMENT_AGE, CAREER_CHANGE, PROPERTY_PURCHASE, DIVORCE, INHERITANCE, CUSTOM)
  - Base_case flag (one per user)
  - Created_date, updated_date
- [ ] Create `scenario_assumptions` table
  - Scenario_id, assumption_type, assumption_value
  - Examples: retirement_age=65, salary_increase_rate=3%, property_value=500000
- [ ] Create `scenario_results` table
  - Scenario_id, result_date, calculation_version
  - Net_worth_projection, retirement_income_projection
  - Tax_liability_projection, goal_achievement_likelihood
  - JSON field for detailed breakdown
- [ ] Create `services/scenarios/scenario_service.py`
- [ ] Implement `create_scenario()` method
  - Create new scenario with assumptions
  - Clone base case data if needed
- [ ] Implement `run_scenario()` method
  - Apply scenario assumptions to user's financial data
  - Run projections (net worth, retirement income, tax)
  - Store results
  - Return comparison to base case
- [ ] Implement `compare_scenarios()` method
  - Compare multiple scenarios side-by-side
  - Highlight differences
  - Return comparison matrix
- [ ] **Test Suite:**
  - Test scenario creation
  - Test scenario running with various assumptions
  - Test scenario comparison
- [ ] **Run:** `pytest tests/models/test_scenarios.py -v` and `pytest tests/services/scenarios/test_scenario_service.py -v`
- [ ] **Acceptance:** Scenario infrastructure complete

---

## 4.5 Scenario Analysis - Specific Scenarios

### Task 4.5.1: Retirement Age Scenario Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `ScenarioWhatif.md`, `Retirement.md`

**Agent Instructions:**
1. Read ScenarioWhatif.md - Retirement age scenario requirements
2. Implement service to model different retirement ages

**Tasks:**
- [ ] Create `services/scenarios/retirement_age_scenario.py`
- [ ] Implement `model_retirement_age()` method
  - Accept retirement_age (55-70)
  - Project pension pot growth to that age
  - Calculate retirement income from that age
  - Calculate tax implications
  - Project pot depletion age
  - Return results and comparison to base case (target retirement age)
- [ ] Implement `optimize_retirement_age()` method
  - Model ages from 55 to 70
  - Find age that maximizes income sustainability
  - Consider life expectancy, desired income, pot size
  - Return optimal retirement age with reasoning
- [ ] **Test Suite:**
  - Test retirement age modeling
  - Test optimization
  - Test various ages and pot sizes
- [ ] **Run:** `pytest tests/services/scenarios/test_retirement_age_scenario.py -v`
- [ ] **Acceptance:** Retirement age scenario provides clear projections

### Task 4.5.2: Career Change and Property Purchase Scenarios

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `ScenarioWhatif.md`

**Agent Instructions:**
1. Read ScenarioWhatif.md - Career change and property scenarios
2. Implement modeling for major life events

**Tasks:**
- [ ] Create `services/scenarios/career_change_scenario.py`
- [ ] Implement `model_career_change()` method
  - Accept new_salary, change_date
  - Project impact on pension contributions, tax, net worth
  - Calculate break-even point
  - Return financial impact analysis
- [ ] Create `services/scenarios/property_scenario.py`
- [ ] Implement `model_property_purchase()` method
  - Accept property_value, deposit, mortgage_rate, mortgage_term
  - Calculate monthly mortgage payment
  - Project impact on cash flow, net worth
  - Calculate total interest paid
  - Consider stamp duty, legal fees
  - Return affordability analysis
- [ ] **Test Suite:**
  - Test career change modeling
  - Test property purchase modeling
  - Test various scenarios
- [ ] **Run:** `pytest tests/services/scenarios/test_career_scenario.py -v` and `pytest tests/services/scenarios/test_property_scenario.py -v`
- [ ] **Acceptance:** Career and property scenarios provide actionable insights

### Task 4.5.3: Monte Carlo Simulation Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `ScenarioWhatif.md`, `Retirement.md`

**Agent Instructions:**
1. Read ScenarioWhatif.md - Monte Carlo simulation requirements
2. Implement probabilistic retirement planning

**Tasks:**
- [ ] Create `services/scenarios/monte_carlo_service.py`
- [ ] Implement `run_monte_carlo_retirement()` method
  - Run 10,000 simulations of retirement
  - Vary investment returns (normal distribution around assumed rate)
  - Vary inflation rates
  - Vary life expectancy
  - Calculate probability of success (pot lasting entire retirement)
  - Return distribution of outcomes, success probability, confidence intervals
- [ ] Implement `calculate_safe_withdrawal_rate()` method
  - Use Monte Carlo to determine safe withdrawal rate
  - Target: 90% probability of success
  - Return safe withdrawal rate as % of starting pot
- [ ] **Test Suite:**
  - Test Monte Carlo simulation runs
  - Test probability calculations
  - Test safe withdrawal rate determination
- [ ] **Run:** `pytest tests/services/scenarios/test_monte_carlo.py -v`
- [ ] **Acceptance:** Monte Carlo simulations provide probabilistic retirement analysis

---

## 4.6 Scenario Analysis - API and UI

### Task 4.6.1: Scenarios API Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `ScenarioWhatif.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read ScenarioWhatif.md - API requirements
2. Implement endpoints for scenario analysis

**Tasks:**
- [ ] Create `api/v1/scenarios/scenarios.py`
- [ ] **POST /api/v1/scenarios** - Create scenario
  - Accept scenario_type, assumptions
  - Return scenario_id
- [ ] **POST /api/v1/scenarios/{id}/run** - Run scenario
  - Calculate projections
  - Return results and comparison to base case
- [ ] **POST /api/v1/scenarios/compare** - Compare scenarios
  - Accept array of scenario_ids
  - Return side-by-side comparison
- [ ] **POST /api/v1/scenarios/retirement-age** - Model retirement age
  - Accept retirement_age
  - Return projections
- [ ] **POST /api/v1/scenarios/career-change** - Model career change
  - Accept new_salary, change_date
  - Return impact analysis
- [ ] **POST /api/v1/scenarios/property-purchase** - Model property purchase
  - Accept property details
  - Return affordability analysis
- [ ] **POST /api/v1/scenarios/monte-carlo** - Run Monte Carlo simulation
  - Accept parameters
  - Return probability distribution and success rate
- [ ] **Test Suite:**
  - Test all scenario endpoints
  - Test authentication
  - Test validation
- [ ] **Run:** `pytest tests/api/scenarios/test_scenarios_api.py -v`
- [ ] **Acceptance:** Scenarios API functional

### Task 4.6.2: Scenario Analysis UI

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `ScenarioWhatif.md`, `UserFlows.md`

**Agent Instructions:**
1. Read ScenarioWhatif.md - UI requirements
2. Create interactive scenario modeling interface
3. Import UI components from 'internal-packages/ui'

**Tasks:**
- [ ] Create `components/scenarios/ScenarioDashboard.jsx`
- [ ] Import UI components from 'internal-packages/ui' (Card, Tabs, Chart, Slider, Table)
- [ ] Create tabbed interface for different scenario types:
  - Tab 1: Retirement Age
  - Tab 2: Career Change
  - Tab 3: Property Purchase
  - Tab 4: Custom Scenario
  - Tab 5: Monte Carlo Simulation
- [ ] **Retirement Age Tab:**
  - Slider for retirement age (55-70)
  - Real-time projection chart as slider moves
  - Display: Projected pot, annual income, pot depletion age
  - Comparison to base case
- [ ] **Career Change Tab:**
  - Input new salary
  - Date picker for change date
  - Display: Impact on pension, tax, net worth over time
  - Break-even analysis
- [ ] **Property Purchase Tab:**
  - Inputs: Property value, deposit, mortgage rate, term
  - Display: Monthly payment, affordability, total interest
  - Impact on cash flow chart
- [ ] **Monte Carlo Tab:**
  - Display: Probability distribution chart (histogram)
  - Success probability (% chance pot lasts entire retirement)
  - Safe withdrawal rate
  - Confidence intervals
- [ ] Create `components/scenarios/ScenarioComparison.jsx`
  - Side-by-side comparison table
  - Highlight differences
  - Visual charts for each scenario
- [ ] **Jest Tests:**
  - Test scenario dashboard renders
  - Test each scenario tab
  - Test interactive sliders update projections
  - Test comparison view
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/ScenarioDashboard.test.jsx`
- [ ] **E2E Test (Playwright):** `npx playwright test e2e/scenarios.spec.js`
- [ ] **Acceptance:** Scenario analysis provides interactive, insightful modeling

---

## 🚦 PHASE 4 SCENARIO ANALYSIS TESTING GATE

### Functional Tests

- [ ] ✅ Scenarios created and run successfully
- [ ] ✅ Retirement age modeling accurate
- [ ] ✅ Career change impact calculated correctly
- [ ] ✅ Property purchase affordability analyzed
- [ ] ✅ Monte Carlo simulations run and provide probability distributions
- [ ] ✅ Safe withdrawal rate calculated
- [ ] ✅ Scenario comparison shows differences clearly

### Integration Tests

- [ ] ✅ Full journey: Create base case → Model retirement age scenario → Compare results → Make decision

### Code Quality

- [ ] ✅ Test coverage >80% for scenarios module
- [ ] ✅ All linting passes
- [ ] ✅ API documentation complete

**Acceptance Criteria:**
🎯 Scenario analysis complete: Users can model major life decisions and see financial impacts

---


**Next Step:**
➡️ Proceed to `phase4b_ai_personalization_tasks.md` to build AI Advisory Engine and Personalization

---
