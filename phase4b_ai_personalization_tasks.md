# Phase 4B: AI Advisory & Personalization

**Last Updated:** October 1, 2025
**Timeline:** 1.5-2 months (Part of Phase 4: 4-5 months total)
**Critical Rule:** ⛔ **PHASE 4 TESTING GATE MUST PASS BEFORE PHASE 5** ⛔

---

## 📋 Overview

**Goal:** Build AI-powered financial advice with LLM integration and personalized user experience

**Prerequisites:** 
- Phase 3 complete
- Phase 4A complete (Goal Planning and Scenario Analysis functional)

**Module Focus:**
- 4.7-4.9: AI Advisory Engine (Full LLM Integration)
- 4.10-4.11: Personalization Engine

**Outputs:**
- LLM integration for financial advice
- AI-powered recommendations (retirement, investment, tax, goals)
- Proactive financial alerts
- Monthly AI-generated insights
- Personalized dashboard and user preferences
- Behavioral learning and adaptive UI

**Related Files:**
- Previous: `phase4a_goals_scenarios_tasks.md` - Goal Planning & Scenarios
- Next (after Phase 4 complete): `phase5a_ml_jurisdictions_tasks.md` - ML and Additional Jurisdictions

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
## 4.7 AI Advisory Engine - Infrastructure and LLM Integration

### Task 4.7.1: LLM Integration Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `AIAdvisoryRecommendation.md`, `Architecture.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read AIAdvisoryRecommendation.md - AI advisory specifications
2. Read Architecture.md for AI service patterns
3. Read securityCompliance.md for data privacy in AI
4. Implement LLM integration for financial advice

**Tasks:**
- [ ] Create `services/ai/llm_service.py`
- [ ] Set up OpenAI API integration (or alternative LLM provider)
  - Store API key in environment variables
  - Configure rate limiting
  - Implement retry logic for API failures
- [ ] Implement `generate_completion()` method
  - Send prompt to LLM
  - Receive response
  - Parse and validate response
  - Log interactions for audit
  - Handle errors gracefully
- [ ] Implement `create_financial_context()` method
  - Gather user's financial data (net worth, income, goals, etc.)
  - Format into structured context for LLM
  - Anonymize PII before sending to LLM
  - Return context string
- [ ] Implement `validate_ai_response()` method
  - Check response for harmful advice
  - Ensure compliance with regulations
  - Flag for human review if uncertain
  - Return validated response or error
- [ ] Create prompt templates for common advisory scenarios
  - Retirement planning advice
  - Investment allocation advice
  - Tax optimization advice
  - Debt payoff strategy
  - Emergency fund recommendations
- [ ] **Test Suite:**
  - Test LLM API integration
  - Test prompt generation
  - Test context creation (with PII anonymization)
  - Test response validation
  - Mock LLM API calls
- [ ] **Run:** `pytest tests/services/ai/test_llm_service.py -v`
- [ ] **Acceptance:** LLM integration functional with proper safety guardrails

### Task 4.7.2: AI Advisory Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `AIAdvisoryRecommendation.md`

**Agent Instructions:**
1. Read AIAdvisoryRecommendation.md - AI advisory features
2. Implement AI-powered financial advisory service

**Tasks:**
- [ ] Create `services/ai/advisory_service.py`
- [ ] Implement `generate_retirement_advice()` method
  - Gather user's retirement data (pensions, goals, projections)
  - Create prompt asking LLM for retirement advice
  - Send to LLM
  - Parse response into actionable recommendations
  - Return advice with confidence score
- [ ] Implement `generate_investment_advice()` method
  - Gather portfolio data (allocation, performance, risk tolerance)
  - Ask LLM for investment optimization advice
  - Return recommendations (rebalance, diversify, etc.)
- [ ] Implement `generate_tax_optimization_advice()` method
  - Gather tax data (income sources, allowances used, deductions)
  - Ask LLM for tax-saving strategies
  - Return specific, actionable tax advice
- [ ] Implement `generate_goal_advice()` method
  - Gather goal data (target, progress, timeline)
  - Ask LLM for advice to achieve goal faster
  - Return strategies (increase savings, adjust timeline, etc.)
- [ ] Implement `answer_financial_question()` method
  - Accept user's free-form question
  - Include financial context
  - Send to LLM
  - Return personalized answer
  - Cite sources where applicable
- [ ] Implement `generate_monthly_insights()` method
  - Analyze user's financial changes in past month
  - Identify trends, wins, concerns
  - Generate personalized monthly summary
  - Return insights with recommendations
- [ ] **Test Suite:**
  - Test each advisory method
  - Test with various financial scenarios
  - Test response quality
  - Mock LLM API calls
- [ ] **Run:** `pytest tests/services/ai/test_advisory_service.py -v`
- [ ] **Acceptance:** AI advisory provides relevant, accurate financial advice

---

## 4.8 AI Advisory Engine - Proactive Recommendations

### Task 4.8.1: Proactive Alert Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `AIAdvisoryRecommendation.md`, `Notifications.md`

**Agent Instructions:**
1. Read AIAdvisoryRecommendation.md - Proactive recommendations
2. Read Notifications.md for notification system
3. Implement proactive financial alerts using AI

**Tasks:**
- [ ] Create `services/ai/proactive_alerts_service.py`
- [ ] Implement `analyze_financial_changes()` method
  - Run daily analysis of user's financial data
  - Detect significant changes (large expenses, income changes, account balance drops)
  - Identify opportunities (unused allowances, goal milestones, savings opportunities)
  - Return list of changes and opportunities
- [ ] Implement `generate_alerts()` method
  - For each significant change/opportunity, generate alert
  - Use LLM to create personalized alert message
  - Determine urgency (HIGH, MEDIUM, LOW)
  - Store alert in notifications table
- [ ] Implement specific alert types:
  - **Allowance alerts:** "You've used only £5,000 of your £20,000 ISA allowance - consider transferring from GIA"
  - **Goal alerts:** "You're 25% of the way to your emergency fund goal! Keep it up!"
  - **Tax alerts:** "You're approaching the higher rate tax threshold - consider pension contributions"
  - **Spending alerts:** "Your spending increased 30% this month - review budget?"
  - **Investment alerts:** "Your portfolio is overweight in UK equities - consider rebalancing"
  - **Retirement alerts:** "Increasing your pension by £100/month could save £25k in tax over 10 years"
- [ ] Implement `batch_generate_monthly_insights()` method
  - Run for all users at month-end
  - Generate personalized monthly insights
  - Send via email and in-app notifications
- [ ] **Test Suite:**
  - Test change detection
  - Test alert generation
  - Test each alert type
  - Test batch processing
  - Mock LLM API calls
- [ ] **Run:** `pytest tests/services/ai/test_proactive_alerts.py -v`
- [ ] **Acceptance:** Proactive alerts provide timely, valuable insights

---

## 4.9 AI Advisory Engine - API and UI

### Task 4.9.1: AI Advisory API Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `AIAdvisoryRecommendation.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read AIAdvisoryRecommendation.md - API requirements
2. Implement endpoints for AI advisory features

**Tasks:**
- [ ] Create `api/v1/ai/advisory.py`
- [ ] **POST /api/v1/ai/advice/retirement** - Get retirement advice
  - Require authentication
  - Generate personalized retirement advice
  - Return advice with reasoning
- [ ] **POST /api/v1/ai/advice/investment** - Get investment advice
  - Return portfolio optimization recommendations
- [ ] **POST /api/v1/ai/advice/tax** - Get tax optimization advice
  - Return tax-saving strategies
- [ ] **POST /api/v1/ai/advice/goal** - Get goal achievement advice
  - Accept goal_id
  - Return strategies to achieve goal
- [ ] **POST /api/v1/ai/ask** - Ask AI a financial question
  - Accept question text
  - Return personalized answer with sources
  - Apply rate limiting (10 questions per day)
- [ ] **GET /api/v1/ai/insights/monthly** - Get monthly insights
  - Return AI-generated monthly summary
- [ ] **GET /api/v1/ai/alerts** - Get proactive alerts
  - Return active alerts sorted by urgency
- [ ] **POST /api/v1/ai/alerts/{id}/dismiss** - Dismiss alert
- [ ] **Test Suite:**
  - Test all AI endpoints
  - Test authentication and rate limiting
  - Test response quality
- [ ] **Run:** `pytest tests/api/ai/test_advisory_api.py -v`
- [ ] **Acceptance:** AI advisory API functional and secure

### Task 4.9.2: AI Advisory UI

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `AIAdvisoryRecommendation.md`, `UserFlows.md`

**Agent Instructions:**
1. Read AIAdvisoryRecommendation.md - UI requirements
2. Create engaging AI advisory interface
3. Import UI components from 'internal-packages/ui'

**Tasks:**
- [ ] Create `components/ai/AIAdvisor.jsx`
- [ ] Import UI components from 'internal-packages/ui' (Card, Chat, Badge, Button)
- [ ] **AI Chat Interface:**
  - Chat input for asking questions
  - Display AI responses in chat format
  - Show "AI is thinking..." loading state
  - Display sources/citations
  - Rate limiting indicator (questions remaining today)
- [ ] **Advice Sections:**
  - Retirement advice card (click to get AI advice)
  - Investment advice card
  - Tax optimization advice card
  - Goal-specific advice cards
- [ ] **Monthly Insights:**
  - Display AI-generated monthly summary
  - Highlight wins, concerns, trends
  - Show recommendations
  - Visual charts to support insights
- [ ] **Proactive Alerts:**
  - Alert feed showing recent alerts
  - Urgency badges (red/yellow/green)
  - Dismiss and act on alerts
  - Filter by type
- [ ] Create `components/ai/AIInsightCard.jsx`
  - Reusable component for displaying AI insight
  - Icon, title, description, action button
- [ ] **Jest Tests:**
  - Test AI advisor renders
  - Test chat interface
  - Test advice sections
  - Test monthly insights display
  - Test alerts feed
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/AIAdvisor.test.jsx`
- [ ] **E2E Test (Playwright):** `npx playwright test e2e/ai-advisor.spec.js`
- [ ] **Acceptance:** AI advisory interface engaging and provides valuable advice

---

## 🚦 PHASE 4 AI ADVISORY TESTING GATE

### Security Tests (CRITICAL)

- [ ] ✅ PII anonymized before sending to LLM
- [ ] ✅ API keys secured in environment variables
- [ ] ✅ Rate limiting on AI endpoints
- [ ] ✅ AI responses validated for safety
- [ ] ✅ LLM interactions logged for audit

### Functional Tests

- [ ] ✅ LLM integration working
- [ ] ✅ Retirement advice relevant and accurate
- [ ] ✅ Investment advice actionable
- [ ] ✅ Tax optimization advice compliant
- [ ] ✅ Goal advice helpful
- [ ] ✅ AI question answering working
- [ ] ✅ Monthly insights generated
- [ ] ✅ Proactive alerts triggered appropriately
- [ ] ✅ Alerts dismissed and acted upon

### Integration Tests

- [ ] ✅ Full journey: Ask AI question → Receive answer → Get retirement advice → View monthly insights → Act on alert

### Code Quality

- [ ] ✅ Test coverage >80% for AI module
- [ ] ✅ All linting passes
- [ ] ✅ API documentation complete

**Acceptance Criteria:**
🎯 AI advisory complete: Users receive intelligent, personalized financial advice and proactive insights

---

## 4.10 Personalization Engine - User Preferences and Learning

### Task 4.10.1: Personalization Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Personalization.md`, `Architecture.md`, `DataManagement.md`

**Agent Instructions:**
1. Read Personalization.md - Complete personalization specifications
2. Implement user preference tracking and learning

**Tasks:**
- [ ] Create `user_preferences` table
  - User_id, preference_type, preference_value
  - Examples: dashboard_layout, default_currency, notification_frequency
- [ ] Create `user_behavior` table
  - User_id, action_type, action_context, timestamp
  - Track: page_views, feature_usage, time_spent, clicks
- [ ] Create `personalized_insights` table
  - User_id, insight_type, insight_text
  - Relevance_score, shown_date, clicked flag, dismissed flag
- [ ] Create `services/personalization/preference_service.py`
- [ ] Implement `save_preference()` method
  - Store user preference
- [ ] Implement `get_preferences()` method
  - Return all user preferences
- [ ] Implement `track_behavior()` method
  - Log user action
  - Store timestamp and context
- [ ] Implement `analyze_behavior()` method
  - Identify frequently used features
  - Identify ignored features
  - Calculate engagement scores
  - Return behavioral insights
- [ ] Implement `personalize_dashboard()` method
  - Based on behavior, determine which widgets to show
  - Prioritize frequently accessed sections
  - Hide rarely used features (or move to "More" menu)
  - Return personalized dashboard layout
- [ ] Implement `generate_personalized_insights()` method
  - Based on user's profile, goals, behavior
  - Generate relevant insights
  - Rank by relevance
  - Return top N insights
- [ ] **Test Suite:**
  - Test preference storage and retrieval
  - Test behavior tracking
  - Test behavior analysis
  - Test dashboard personalization
  - Test insight generation
- [ ] **Run:** `pytest tests/services/personalization/test_preference_service.py -v`
- [ ] **Acceptance:** Personalization engine learns from user behavior

---

## 4.11 Personalization Engine - UI Customization

### Task 4.11.1: Personalized Dashboard and Settings

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Personalization.md`, `UserFlows.md`

**Agent Instructions:**
1. Read Personalization.md - UI personalization requirements
2. Implement adaptive dashboard and user settings
3. Import UI components from 'internal-packages/ui'

**Tasks:**
- [ ] Create `components/personalization/PersonalizedDashboard.jsx`
- [ ] Fetch personalized layout from API
- [ ] Dynamically render widgets based on user preferences and behavior
- [ ] Allow drag-and-drop to rearrange widgets (save layout)
- [ ] Show/hide widgets based on relevance
- [ ] Create `components/personalization/PersonalizationSettings.jsx`
  - Default currency selector
  - Date format selector
  - Number format selector
  - Notification preferences (email, in-app, frequency)
  - Dashboard widget visibility toggles
  - Theme selector (light/dark mode)
  - Language selector (future)
- [ ] Create `components/personalization/InsightsFeed.jsx`
  - Display personalized insights
  - Ranked by relevance
  - Dismiss and save insights
  - Track which insights are most engaging
- [ ] Implement behavior tracking on frontend
  - Track page views, clicks, time spent
  - Send to backend periodically
- [ ] **Jest Tests:**
  - Test personalized dashboard renders
  - Test widget rearrangement
  - Test settings updates
  - Test insights feed
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/PersonalizedDashboard.test.jsx`
- [ ] **Acceptance:** Dashboard adapts to user preferences and behavior

---

## 🚦 PHASE 4 COMPLETE TESTING GATE

### Security Tests (CRITICAL)

- [ ] ✅ User data privacy maintained with AI (PII anonymized)
- [ ] ✅ LLM API keys secured
- [ ] ✅ Rate limiting on AI endpoints
- [ ] ✅ AI responses validated for safety
- [ ] ✅ Personalization respects user privacy

### Functional Tests

**Goal Planning (4.1-4.3):**
- [ ] ✅ Goals created and tracked
- [ ] ✅ Progress calculated accurately
- [ ] ✅ Monthly savings needed calculated
- [ ] ✅ Goal optimization allocates savings intelligently
- [ ] ✅ Milestones tracked

**Scenario Analysis (4.4-4.6):**
- [ ] ✅ Scenarios created and run
- [ ] ✅ Retirement age modeling accurate
- [ ] ✅ Career change impact calculated
- [ ] ✅ Property purchase analyzed
- [ ] ✅ Monte Carlo simulations provide probability distributions

**AI Advisory (4.7-4.9):**
- [ ] ✅ LLM integration working
- [ ] ✅ Retirement, investment, tax, and goal advice relevant
- [ ] ✅ AI question answering functional
- [ ] ✅ Monthly insights generated
- [ ] ✅ Proactive alerts triggered appropriately

**Personalization (4.10-4.11):**
- [ ] ✅ User preferences saved and applied
- [ ] ✅ Behavior tracked and analyzed
- [ ] ✅ Dashboard personalized based on behavior
- [ ] ✅ Insights ranked by relevance

### Integration Tests

- [ ] ✅ Full goal journey: Create goal → Track progress → Get AI advice → Achieve goal
- [ ] ✅ Full scenario journey: Model retirement age → Compare scenarios → Get AI insights → Make decision
- [ ] ✅ Full AI journey: Ask question → Get advice → Receive proactive alert → Act on recommendation
- [ ] ✅ Personalization adapts dashboard over time based on usage
- [ ] ✅ Load test: 100 concurrent users using AI features

### Code Quality

- [ ] ✅ Test coverage >80% for all Phase 4 modules
- [ ] ✅ All linting passes (backend and frontend)
- [ ] ✅ API documentation complete for all endpoints
- [ ] ✅ Component documentation complete
- [ ] ✅ No console errors in browser
- [ ] ✅ Mobile responsive on all pages

### Data Quality

- [ ] ✅ Soft deletes work
- [ ] ✅ Historical data retained
- [ ] ✅ PII protected in AI interactions
- [ ] ✅ Behavior tracking accurate

### Performance Tests

- [ ] ✅ Goal dashboard loads in <2 seconds
- [ ] ✅ Scenario calculations complete in <1 second
- [ ] ✅ AI responses return in <5 seconds
- [ ] ✅ Monte Carlo simulations complete in <10 seconds
- [ ] ✅ API responses <500ms (95th percentile, excluding AI)
- [ ] ✅ Database queries optimized

### User Acceptance

- [ ] ✅ Can set and track financial goals
- [ ] ✅ Can model major life decisions
- [ ] ✅ Can ask AI financial questions
- [ ] ✅ Receives valuable monthly insights
- [ ] ✅ Proactive alerts are timely and relevant
- [ ] ✅ Dashboard personalizes over time
- [ ] ✅ All error messages clear and helpful

**Acceptance Criteria:**
🎯 **Phase 4 Complete**: Users can set goals, model scenarios, receive AI-powered advice, and experience a personalized financial planning platform.

🎯 **Intelligence & AI**: Intelligent goal tracking, scenario modeling, AI advisory with LLM integration, and adaptive personalization.

🎯 **Ready for Phase 5**: Codebase clean, tested, documented, and ready to add ML optimization, additional jurisdictions, advanced integrations, and mobile apps.

---
