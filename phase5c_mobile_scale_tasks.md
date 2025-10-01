# Phase 5C: Mobile Apps, Performance & Reporting

**Last Updated:** October 1, 2025
**Timeline:** 2-2.5 months (Part of Phase 5: 6-8 months total)
**Critical Rule:** ⛔ **PHASE 5 TESTING GATE = PRODUCTION READY** ⛔

---

## 📋 Overview

**Goal:** Build native mobile apps, optimize for scale, and add advanced reporting capabilities

**Prerequisites:** 
- Phase 4 complete
- Phase 5A complete (ML and Additional Jurisdictions functional)
- Phase 5B complete (Advanced Integrations functional)

**Module Focus:**
- 5.8-5.10: Mobile Applications (iOS and Android)
- 5.11: Performance Optimization and Scaling
- 5.12: Advanced Reporting and Analytics

**Outputs:**
- Native mobile apps (iOS and Android)
- Push notifications
- Performance optimization for 10,000+ concurrent users
- Backend caching and load balancing
- Frontend bundle optimization
- Custom report builder
- Admin dashboard and analytics
- Platform ready for production launch

**Related Files:**
- Previous: `phase5a_ml_jurisdictions_tasks.md` - ML and Jurisdictions
- Previous: `phase5b_integrations_tasks.md` - Advanced Integrations
- This is the FINAL phase!

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
- Mobile: Unit tests for business logic, E2E tests for critical flows
- See `.claude/instructions.md` for complete testing strategy

---
## 5.8 Mobile Applications - Architecture and Setup

### Task 5.8.1: Mobile App Architecture Decision

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Architecture.md`, `roadmapConsideration.md`

**Agent Instructions:**
1. Read Architecture.md for mobile architecture patterns
2. Decide on mobile framework: React Native (cross-platform) or native (Swift for iOS, Kotlin for Android)
3. Recommendation: React Native for faster development and code reuse

**Tasks:**
- [ ] Set up React Native development environment
  - Install React Native CLI
  - Set up Xcode (for iOS development)
  - Set up Android Studio (for Android development)
- [ ] Initialize React Native project
  - `npx react-native init GoalPlanMobile`
  - Set up folder structure
- [ ] Configure navigation (React Navigation)
  - Stack Navigator for screens
  - Tab Navigator for main sections
- [ ] Set up state management (Context API or Redux)
- [ ] Configure API client
  - Axios for HTTP requests
  - Base URL pointing to backend API
  - Authentication token storage (secure storage)
- [ ] Set up testing framework
  - Jest for unit tests
  - Detox for E2E tests
- [ ] **Test Suite:**
  - Test navigation setup
  - Test API client configuration
- [ ] **Run:** `npm test` (React Native tests)
- [ ] **Acceptance:** Mobile app scaffolding complete

---

## 5.9 Mobile Applications - Core Features

### Task 5.9.1: Mobile Authentication and Dashboard

**⚛️ DELEGATE TO: `react-coder`** (React Native)
**Context Files:** `userAuth.md`, `CentralDashboard.md`, `UserFlows.md`

**Agent Instructions:**
1. Read userAuth.md for authentication requirements
2. Read CentralDashboard.md for dashboard content
3. Implement mobile authentication and dashboard using React Native

**Tasks:**
- [ ] Create mobile authentication screens
  - `screens/auth/LoginScreen.js`
    - Email and password inputs
    - "Login" button
    - "Forgot password" link
    - Navigate to dashboard on success
  - `screens/auth/RegisterScreen.js`
    - Registration form
    - Navigate to onboarding
  - `screens/auth/TwoFactorScreen.js`
    - TOTP code input
    - Verify and login
- [ ] Implement secure token storage
  - Use react-native-keychain or Expo SecureStore
  - Store access and refresh tokens securely
  - Auto-refresh tokens
- [ ] Create `screens/DashboardScreen.js`
  - Display net worth (large, prominent)
  - Asset allocation chart (pie chart)
  - Recent transactions (last 5)
  - Goals progress (cards for active goals)
  - Quick actions (add transaction, view goals, etc.)
- [ ] Implement pull-to-refresh
  - Refresh dashboard data on pull-down
- [ ] **Tests:**
  - Unit tests for authentication logic
  - E2E tests for login flow (Detox)
- [ ] **Run:** `npm test` and `detox test`
- [ ] **Acceptance:** Mobile authentication and dashboard functional

### Task 5.9.2: Mobile Core Modules (Savings, Investments, Retirement)

**⚛️ DELEGATE TO: `react-coder`** (React Native)
**Context Files:** `Savings.md`, `Investment.md`, `Retirement.md`, `UserFlows.md`

**Agent Instructions:**
1. Implement mobile views for core modules
2. Adapt web UI to mobile form factor

**Tasks:**
- [ ] Create `screens/savings/SavingsScreen.js`
  - List savings accounts
  - Tap account to view details
  - Add account button
- [ ] Create `screens/savings/AddAccountScreen.js`
  - Form to add savings account (name, balance, type)
  - Save and navigate back
- [ ] Create `screens/investments/PortfolioScreen.js`
  - Portfolio summary (total value, unrealized gains)
  - Holdings list (scrollable)
  - Asset allocation chart
  - Tap holding for details
- [ ] Create `screens/investments/HoldingDetailsScreen.js`
  - Holding details, performance chart
  - Sell button (opens modal)
- [ ] Create `screens/retirement/PensionsScreen.js`
  - List pensions (UK and SA)
  - Total pension pot
  - Annual Allowance tracker
  - Tap pension for details
- [ ] Create `screens/retirement/RetirementProjectionScreen.js`
  - Retirement income projection
  - Interactive slider for retirement age
  - Chart showing pot growth
- [ ] **Tests:**
  - Unit tests for each screen
  - E2E tests for critical flows
- [ ] **Run:** `npm test` and `detox test`
- [ ] **Acceptance:** Core modules functional on mobile

### Task 5.9.3: Mobile Goals and AI Features

**⚛️ DELEGATE TO: `react-coder`** (React Native)
**Context Files:** `GoalPlanning.md`, `AIAdvisoryRecommendation.md`, `UserFlows.md`

**Agent Instructions:**
1. Implement mobile goals and AI advisory features

**Tasks:**
- [ ] Create `screens/goals/GoalsScreen.js`
  - List financial goals
  - Progress bars for each goal
  - On-track indicators
  - Add goal button
- [ ] Create `screens/goals/GoalDetailsScreen.js`
  - Full goal details
  - Progress chart over time
  - Milestones
  - Edit and delete buttons
- [ ] Create `screens/ai/AIAdvisorScreen.js`
  - AI chat interface
  - Ask question input
  - Display AI responses
  - Quick action buttons (get retirement advice, tax advice, etc.)
- [ ] Create `screens/ai/InsightsScreen.js`
  - Monthly insights from AI
  - Proactive alerts feed
  - Dismiss and act on alerts
- [ ] Implement push notifications for alerts
  - Configure Firebase Cloud Messaging (FCM) or APNs
  - Send notifications for high-priority alerts
- [ ] **Tests:**
  - Unit tests for goals and AI screens
  - E2E tests for goal creation and AI chat
- [ ] **Run:** `npm test` and `detox test`
- [ ] **Acceptance:** Goals and AI features functional on mobile with push notifications

---

## 5.10 Mobile Applications - Deployment

### Task 5.10.1: iOS and Android Build and Deployment

**🐍 DELEGATE TO: `python-backend-engineer`** (DevOps focus)
**Context Files:** `roadmapConsideration.md`

**Agent Instructions:**
1. Prepare mobile apps for deployment to App Store and Google Play
2. Set up CI/CD for mobile builds

**Tasks:**
- [ ] **iOS Build:**
  - Configure Xcode project
  - Set up app icons and launch screens
  - Create Apple Developer account (if needed)
  - Generate signing certificates and provisioning profiles
  - Build release version
  - Upload to App Store Connect
  - Submit for review
- [ ] **Android Build:**
  - Configure Android Studio project
  - Set up app icons and splash screens
  - Create Google Play Console account
  - Generate signing key
  - Build release APK/AAB
  - Upload to Google Play Console
  - Submit for review
- [ ] Set up CI/CD for mobile (GitHub Actions or Bitrise)
  - Automated builds on commit
  - Automated testing
  - Automated deployment to TestFlight (iOS) and Internal Testing (Android)
- [ ] **Test Suite:**
  - Test build process
  - Test app installation and launch
- [ ] **Acceptance:** Mobile apps deployed to App Store and Google Play

---

## 🚦 PHASE 5 MOBILE APPS TESTING GATE

### Functional Tests

- [ ] ✅ Mobile authentication working
- [ ] ✅ Mobile dashboard displays net worth and summary
- [ ] ✅ Savings, investments, retirement modules functional
- [ ] ✅ Goals and AI features working
- [ ] ✅ Push notifications working
- [ ] ✅ App works offline (cached data)
- [ ] ✅ iOS and Android builds successful

### Performance Tests

- [ ] ✅ App launches in <2 seconds
- [ ] ✅ Screens render smoothly (60fps)
- [ ] ✅ API calls optimized (no excessive requests)

### User Acceptance

- [ ] ✅ Can login and view dashboard on mobile
- [ ] ✅ Can track goals on mobile
- [ ] ✅ Can ask AI questions on mobile
- [ ] ✅ Receive push notifications for alerts

### Code Quality

- [ ] ✅ Test coverage >70% for mobile code
- [ ] ✅ All linting passes
- [ ] ✅ App passes store review guidelines

**Acceptance Criteria:**
🎯 Native mobile apps (iOS and Android) available on App Store and Google Play with core features

---

## 5.11 Performance Optimization and Scaling

### Task 5.11.1: Backend Performance Optimization

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `performance.md`, `Architecture.md`

**Agent Instructions:**
1. Read performance.md - Performance targets and requirements
2. Optimize backend for 10,000+ concurrent users
3. Implement caching, database optimization, and load balancing

**Tasks:**
- [ ] **Database Optimization:**
  - Add missing indexes (analyze slow queries)
  - Optimize complex queries (use EXPLAIN)
  - Implement database connection pooling (SQLAlchemy pool)
  - Partition large tables (transactions, holdings)
- [ ] **Caching:**
  - Implement Redis caching for frequently accessed data
  - Cache user profiles, dashboard data, tax rates
  - Set appropriate TTLs (Time To Live)
  - Implement cache invalidation on updates
- [ ] **API Optimization:**
  - Implement rate limiting (per user, per endpoint)
  - Use pagination on all list endpoints
  - Compress responses (gzip)
  - Implement API versioning
- [ ] **Background Jobs:**
  - Move long-running tasks to background jobs (Celery)
  - Examples: ML model training, daily account syncing, monthly insights generation
  - Use Redis as message broker
  - Monitor job queue
- [ ] **Load Balancing:**
  - Deploy multiple app server instances
  - Set up load balancer (Nginx or cloud load balancer)
  - Implement health checks
- [ ] **Monitoring:**
  - Set up application monitoring (Prometheus, Grafana, or Datadog)
  - Monitor API response times, error rates, queue lengths
  - Set up alerts for performance degradation
- [ ] **Test Suite:**
  - Load test with 1,000 concurrent users (using Locust or JMeter)
  - Verify API responses <500ms (95th percentile)
  - Verify database query times <100ms
- [ ] **Run:** `locust -f tests/load/locustfile.py`
- [ ] **Acceptance:** Backend handles 10,000+ concurrent users with <500ms response times

### Task 5.11.2: Frontend Performance Optimization

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `performance.md`, `UserFlows.md`

**Agent Instructions:**
1. Read performance.md - Frontend performance targets
2. Optimize React app for fast load times and smooth interactions

**Tasks:**
- [ ] **Code Splitting:**
  - Implement React.lazy() and Suspense for route-based code splitting
  - Load modules on demand (not upfront)
  - Reduce initial bundle size to <500KB gzipped
- [ ] **Image Optimization:**
  - Compress images
  - Use WebP format where supported
  - Lazy load images (load when visible)
- [ ] **Memoization:**
  - Use React.memo() for expensive components
  - Use useMemo() and useCallback() to prevent unnecessary re-renders
- [ ] **API Request Optimization:**
  - Implement request deduplication
  - Cache API responses on frontend (SWR or React Query)
  - Debounce search inputs
  - Prefetch data for likely navigation (e.g., dashboard data while logging in)
- [ ] **Lighthouse Audit:**
  - Run Lighthouse on key pages
  - Achieve score >90 for Performance, Accessibility, Best Practices, SEO
  - Fix any identified issues
- [ ] **Test Suite:**
  - Measure bundle size (webpack-bundle-analyzer)
  - Measure page load times
  - Test on slow 3G network (DevTools throttling)
- [ ] **Run:** `npm run build` and analyze bundle, run Lighthouse
- [ ] **Acceptance:** Frontend bundle <500KB, page load <2 seconds, Lighthouse score >90

---

## 5.12 Advanced Reporting and Analytics

### Task 5.12.1: Custom Report Builder

**🐍 DELEGATE TO: `python-backend-engineer`**
**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `reporting.md`, `UserFlows.md`

**Agent Instructions:**
1. Read reporting.md - Reporting requirements
2. Implement custom report builder for users to generate reports

**Tasks:**
- [ ] **Backend (🐍):** Create `services/reporting/report_service.py`
  - Implement `generate_net_worth_report()` method
    - Net worth over time (monthly snapshots)
    - Breakdown by asset class
    - Export to PDF or CSV
  - Implement `generate_tax_report()` method
    - Income by source (employment, dividends, capital gains)
    - Tax liabilities (UK, SA, other)
    - Deductions and allowances used
    - Export to PDF for filing
  - Implement `generate_goal_progress_report()` method
    - All goals with progress
    - On-track analysis
    - Milestones achieved
  - Implement `generate_investment_performance_report()` method
    - Portfolio performance over time
    - Holdings breakdown
    - Realized and unrealized gains
    - Dividend income
- [ ] **Backend (🐍):** Create API endpoints
  - **POST /api/v1/reports/net-worth** - Generate net worth report
  - **POST /api/v1/reports/tax** - Generate tax report
  - **POST /api/v1/reports/goals** - Generate goal progress report
  - **POST /api/v1/reports/investments** - Generate investment report
  - Accept date ranges, filters
  - Return report data or download link (PDF)
- [ ] **Backend Test:** `pytest tests/services/reporting/test_report_service.py -v`
- [ ] **Frontend (⚛️):** Create `components/reports/ReportBuilder.jsx`
  - Import UI components from 'internal-packages/ui'
  - Report type selector (Net Worth, Tax, Goals, Investments)
  - Date range picker
  - Filters (account type, goal type, etc.)
  - "Generate Report" button
  - Display report in browser or download as PDF/CSV
- [ ] **Jest Tests:**
  - Test report builder form
  - Test report generation
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/ReportBuilder.test.jsx`
- [ ] **Acceptance:** Users can generate custom reports and export to PDF/CSV

### Task 5.12.2: Admin Dashboard and Analytics

**🐍 DELEGATE TO: `python-backend-engineer`**
**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `successMetrics.md`, `Architecture.md`

**Agent Instructions:**
1. Read successMetrics.md - KPIs and metrics to track
2. Build admin dashboard for platform analytics

**Tasks:**
- [ ] **Backend (🐍):** Create admin analytics service
  - `services/admin/analytics_service.py`
  - Implement `get_platform_metrics()` method
    - Total users, active users (last 30 days)
    - Total accounts, total net worth (aggregated)
    - User engagement metrics (avg session duration, feature usage)
    - Goal achievement rate
    - Return metrics
  - Implement `get_user_growth_metrics()` method
    - New registrations over time (daily, weekly, monthly)
    - User retention rate
    - Churn rate
- [ ] **Backend (🐍):** Create admin API endpoints
  - **GET /api/v1/admin/metrics** - Platform metrics
    - Require admin authentication
    - Return comprehensive metrics
  - **GET /api/v1/admin/users** - User management
    - List users with filters
    - User activity logs
- [ ] **Backend Test:** `pytest tests/api/admin/test_analytics_api.py -v`
- [ ] **Frontend (⚛️):** Create `components/admin/AdminDashboard.jsx`
  - Import UI components from 'internal-packages/ui'
  - Display platform metrics:
    - Total users, active users
    - Total net worth
    - User growth chart
    - Feature usage heatmap
    - Goal achievement rate
  - User management section (search, filter, view user details)
- [ ] **Jest Tests:**
  - Test admin dashboard renders correctly
  - Test metrics display
  - Mock API calls
- [ ] **Component Test (Jest):** `npm test tests/components/AdminDashboard.test.jsx`
- [ ] **Acceptance:** Admin dashboard provides comprehensive platform analytics

---

## 🚦 PHASE 5 COMPLETE TESTING GATE

### Security Tests (CRITICAL)

- [ ] ✅ All integrations use encrypted credentials
- [ ] ✅ Admin endpoints require admin authentication
- [ ] ✅ Mobile app uses secure token storage
- [ ] ✅ Rate limiting prevents abuse
- [ ] ✅ All APIs pass security audit

### Functional Tests

**ML Predictions (5.1-5.2):**
- [ ] ✅ Spending prediction model accurate (>70%)
- [ ] ✅ Income forecasting functional
- [ ] ✅ Goal success prediction provides useful insights
- [ ] ✅ ML predictions displayed in UI

**Additional Jurisdictions (5.3-5.4):**
- [ ] ✅ US tax calculations accurate (federal and state)
- [ ] ✅ US retirement accounts (401k, IRA) tracked
- [ ] ✅ EU tax calculations functional for Germany, France, Ireland, Netherlands
- [ ] ✅ Australian tax and superannuation calculated correctly
- [ ] ✅ UI adapts to selected jurisdictions

**Integrations (5.5-5.7):**
- [ ] ✅ Open Banking integration working
- [ ] ✅ Investment platform integration working
- [ ] ✅ Pension Tracing Service integrated
- [ ] ✅ Daily syncing functional

**Mobile Apps (5.8-5.10):**
- [ ] ✅ iOS and Android apps deployed
- [ ] ✅ Mobile authentication working
- [ ] ✅ Core modules functional on mobile
- [ ] ✅ Goals and AI features working on mobile
- [ ] ✅ Push notifications working

**Performance (5.11):**
- [ ] ✅ Backend handles 10,000+ concurrent users
- [ ] ✅ API responses <500ms (95th percentile)
- [ ] ✅ Frontend bundle <500KB gzipped
- [ ] ✅ Page load <2 seconds
- [ ] ✅ Lighthouse score >90

**Reporting (5.12):**
- [ ] ✅ Custom reports generated accurately
- [ ] ✅ Reports export to PDF/CSV
- [ ] ✅ Admin dashboard functional with analytics

### Integration Tests

- [ ] ✅ Full journey: Connect bank via Open Banking → Auto-sync transactions → View in dashboard → Generate report
- [ ] ✅ Full journey: Connect investment platform → Sync portfolio → View performance → Get AI advice
- [ ] ✅ Full mobile journey: Login → View dashboard → Track goal → Ask AI question → Receive push notification
- [ ] ✅ Load test: 10,000 concurrent users across all features

### Code Quality

- [ ] ✅ Test coverage >80% for all Phase 5 modules
- [ ] ✅ All linting passes (backend, frontend, mobile)
- [ ] ✅ API documentation complete for all endpoints
- [ ] ✅ Mobile apps pass store review guidelines
- [ ] ✅ No console errors in browser or mobile
- [ ] ✅ Mobile responsive on all pages (web)

### Data Quality

- [ ] ✅ Synced data accurate (banks, investments)
- [ ] ✅ Historical data retained
- [ ] ✅ ML models versioned and tracked
- [ ] ✅ All monetary amounts have currency specified

### Performance Tests

- [ ] ✅ Backend API <500ms (95th percentile)
- [ ] ✅ Frontend load <2 seconds
- [ ] ✅ Mobile app launch <2 seconds
- [ ] ✅ ML inference <500ms
- [ ] ✅ Report generation <5 seconds
- [ ] ✅ Database queries optimized (no N+1)
- [ ] ✅ 10,000+ concurrent users supported

### User Acceptance

- [ ] ✅ Can use platform in US, EU, or Australia
- [ ] ✅ Can connect bank accounts and auto-sync
- [ ] ✅ Can connect investment platforms and auto-sync
- [ ] ✅ ML predictions are valuable and accurate
- [ ] ✅ Mobile app provides full functionality
- [ ] ✅ Can generate custom reports
- [ ] ✅ Platform is fast and responsive
- [ ] ✅ All error messages clear and helpful

**Acceptance Criteria:**
🎯 **Phase 5 Complete**: GoalPlan is a comprehensive, scalable, dual-country financial planning platform with ML predictions, multi-jurisdiction support, extensive integrations, and mobile apps.

🎯 **Enhancement & Scale**: Platform supports US, EU, and Australia; integrates with banks, investment platforms, and pension providers; has native mobile apps; and handles 10,000+ concurrent users.

🎯 **Production Ready**: Fully tested, documented, optimized, and ready for public launch. Platform is world-class dual-country financial planning solution.

---

## 🎉 GOALPLAN PLATFORM COMPLETE

**All 6 phases complete:**
- ✅ Phase 0: Project setup and foundation
- ✅ Phase 1: Authentication, user info, savings, dashboard
- ✅ Phase 2: Protection, investment, basic tax intelligence
- ✅ Phase 3: Retirement, IHT planning, DTA calculator, tax residency
- ✅ Phase 4: Goal planning, scenario analysis, AI advisory, personalization
- ✅ Phase 5: ML predictions, multi-jurisdiction, integrations, mobile apps, scaling

**GoalPlan is now a comprehensive dual-country financial planning platform that:**
- Tracks finances across UK, SA, and additional jurisdictions (US, EU, Australia)
- Provides intelligent tax optimization and DTA relief calculations
- Offers AI-powered financial advice and proactive insights
- Enables goal-based planning with scenario modeling
- Integrates with banks, investment platforms, and pension providers
- Delivers seamless experience on web and mobile
- Scales to serve thousands of users simultaneously

**Ready for launch! 🚀**

---
