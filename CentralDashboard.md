3. CENTRAL DASHBOARD
Feature 3.1: Net Worth Summary Dashboard
Feature Name: Comprehensive Net Worth Aggregation and Visualization
User Story: As a user, I want to see my complete net worth across all accounts, investments, properties, and liabilities in one place, with breakdowns by country, currency, and asset type.
Acceptance Criteria:
•	Display total net worth (assets - liabilities)
•	Breakdown by country (UK, SA, Offshore)
•	Breakdown by currency (with conversion to base currency)
•	Breakdown by asset class (Cash, Investments, Property, Pensions, Other)
•	Liability summary
•	Net worth trend over time (line chart)
•	Asset allocation pie chart
•	Currency exposure visualization
•	Quick links to each module
•	Refresh data button with last updated timestamp
Technical Requirements:
•	Aggregate data from all modules
•	Real-time currency conversion
•	Historical net worth tracking (snapshots)
•	Caching for performance
•	Responsive charts library (Chart.js, D3, or Recharts)
•	WebSocket for real-time updates (optional)
Constraints:
•	Dashboard must load in <2 seconds
•	Data refresh max every 5 minutes for external data
•	Support for up to 1000 line items per user
•	Mobile responsive design required
Implementation Approach:
ENDPOINT: GET /api/v1/dashboard/net-worth
QUERY PARAMS:
- baseCurrency: string (default: GBP)
- asOfDate: date (optional, default: today)

BUSINESS LOGIC:
1. Fetch all assets from modules:
   - Savings accounts → SavingsModule
   - Investments → InvestmentModule
   - Pensions → RetirementModule
   - Properties → IHTModule.assets
   - Protection policies (cash value) → ProtectionModule
   - Other assets → IHTModule.assets

2. Fetch all liabilities from modules:
   - Mortgages → IHTModule.liabilities
   - Loans → IHTModule.liabilities
   - Credit cards → SavingsModule (negative balance)

3. Convert all amounts to baseCurrency using latest rates

4. Calculate totals:
   total_assets = SUM(all_asset_values_in_base_currency)
   total_liabilities = SUM(all_liability_values_in_base_currency)
   net_worth = total_assets - total_liabilities

5. Group and aggregate:
   BY country: UK, SA, Offshore, Other
   BY asset_class: Cash, Investments, Property, Pensions, Protection, Other
   BY currency: Original currency exposure

6. Fetch historical snapshots for trend

7. Calculate changes:
   net_worth_change_30d = current_net_worth - net_worth_30_days_ago
   net_worth_change_percent = (change / previous) * 100

RESPONSE:
{
  netWorth: {
    total: decimal,
    totalAssets: decimal,
    totalLiabilities: decimal,
    baseCurrency: string,
    asOfDate: date,
    lastUpdated: timestamp
  },
  byCountry: [
    {country: 'UK', amount: decimal, percentage: decimal},
    {country: 'SA', amount: decimal, percentage: decimal},
    ...
  ],
  byAssetClass: [
    {class: 'Cash', amount: decimal, percentage: decimal},
    {class: 'Investments', amount: decimal, percentage: decimal},
    ...
  ],
  byCurrency: [
    {currency: 'GBP', amount: decimal, percentage: decimal},
    {currency: 'ZAR', amount: decimal, percentage: decimal},
    ...
  ],
  trend: [
    {date: date, netWorth: decimal},
    {date: date, netWorth: decimal},
    ... (last 12 months)
  ],
  changes: {
    day: {amount: decimal, percentage: decimal},
    month: {amount: decimal, percentage: decimal},
    year: {amount: decimal, percentage: decimal}
  }
}
User Flow:
[User Login] → [Dashboard Landing]
     ↓
[Net Worth Summary - Hero Section]
  - Large total net worth display
  - Color-coded change indicator (green up, red down)
  - Period selector (1D, 1M, 3M, 1Y, All)
     ↓
[Asset Allocation Section]
  - Pie chart (by asset class)
  - Bar chart (by country)
  - Toggle between views
     ↓
[Net Worth Trend]
  - Line chart with date range selector
  - Hover to see specific date values
     ↓
[Quick Module Access Cards]
  - Protection: Total cover amount
  - Savings: Total saved
  - Investments: Portfolio value
  - Retirement: Pension pot
  - IHT: Estate value
  - Click card → Navigate to module
     ↓
[Refresh Button] → [Reload data]
API Endpoints:
•	GET /api/v1/dashboard/net-worth - Get net worth summary
•	GET /api/v1/dashboard/net-worth/trend - Historical trend data
•	GET /api/v1/dashboard/snapshot - Create manual snapshot
•	GET /api/v1/dashboard/currency-exposure - Detailed currency breakdown
Data Models:
TABLE: net_worth_snapshots
- id: UUID (PK)
- user_id: UUID (FK to users)
- snapshot_date: DATE
- total_assets_gbp: DECIMAL(15,2)
- total_liabilities_gbp: DECIMAL(15,2)
- net_worth_gbp: DECIMAL(15,2)
- total_assets_zar: DECIMAL(15,2)
- total_liabilities_zar: DECIMAL(15,2)
- net_worth_zar: DECIMAL(15,2)
- snapshot_type: ENUM('AUTO', 'MANUAL', 'TAX_YEAR_END')
- created_at: TIMESTAMP

TABLE: net_worth_by_category
- id: UUID (PK)
- snapshot_id: UUID (FK to net_worth_snapshots)
- category_type: ENUM('COUNTRY', 'ASSET_CLASS', 'CURRENCY')
- category_value: VARCHAR(50)
- amount_gbp: DECIMAL(15,2)
- amount_zar: DECIMAL(15,2)
- percentage_of_total: DECIMAL(5,2)

TABLE: dashboard_cache
- user_id: UUID (PK)
- cache_key: VARCHAR(255)
- cache_data: JSONB
- expires_at: TIMESTAMP
- created_at: TIMESTAMP

VIEW: v_user_net_worth_current (materialized view, refreshed hourly)
- user_id
- total_cash (from savings)
- total_investments (from investments)
- total_pensions (from retirement)
- total_property (from IHT assets)
- total_liabilities (from IHT liabilities)
- net_worth_gbp
- net_worth_zar
- last_calculated: TIMESTAMP

INDEX on net_worth_snapshots(user_id, snapshot_date DESC)
INDEX on net_worth_by_category(snapshot_id, category_type)
INDEX on dashboard_cache(user_id, cache_key, expires_at)
Error Handling:
ERROR CASES:
1. No data available (new user)
   - Response: 200 OK
   - Return zero values with message: "Add your first account to see your net worth"
   
2. Exchange rate unavailable
   - Response: 200 OK (partial data)
   - Message: "Some currency conversions unavailable. Showing in original currencies"
   - Flag affected items
   
3. Module data fetch timeout
   - Response: 206 Partial Content
   - Return available data with warning: "Some data unavailable. Showing cached values from {timestamp}"
   
4. Cache expired and refresh in progress
   - Response: 200 OK
   - Return cached data with indicator: "Data refreshing in background"
   
5. Snapshot creation failure
   - Response: 500 Internal Server Error (log and retry)
   - User sees previous snapshot
   - Admin alert triggered

EDGE CASES:
- Negative net worth: Display normally with messaging
- First-time user: Show onboarding prompts
- Data inconsistency between modules: Flag for review, show best estimate
- Large portfolio (1000+ items): Implement pagination in detail views
- Multiple base currencies: User can switch, recalculate on fly
- Assets in cryptocurrencies: Fetch current rates, high volatility warning
- Liabilities exceeding assets: Risk indicator shown
Performance Considerations:
•	Cache dashboard data for 5 minutes (Redis)
•	Materialized view for net worth calculation (refresh hourly)
•	Async aggregation for large portfolios
•	Lazy loading for historical trend data
•	Snapshot creation: Daily automated job (off-peak hours)
•	Manual snapshots: Rate limited to 1 per hour
•	Expected load: 50,000 dashboard views/day
•	Target response time: <1 second (from cache)
•	Cold load (no cache): <2 seconds
•	Optimize queries with proper indexing
•	Consider GraphQL for flexible data fetching
•	Implement pagination for large datasets (>100 items)
 
Feature 3.2: AI Recommendations Summary
Feature Name: Personalized AI-Driven Action Recommendations
User Story: As a user, I want to see prioritized, actionable recommendations on my dashboard so that I know what financial actions to take next to improve my situation.
Acceptance Criteria:
•	Display top 5 prioritized recommendations
•	Recommendations categorized by urgency (Critical, High, Medium, Low)
•	Each recommendation includes: title, description, estimated impact, required action
•	User can dismiss recommendations
•	User can mark recommendations as "in progress" or "completed"
•	Recommendations update based on user actions
•	Link to relevant module for action
•	Explanation of why recommendation is made
•	Estimated tax savings or benefit amount where applicable
Technical Requirements:
•	Integration with AI Advisory Engine
•	Rules engine for recommendation priority
•	ML model for personalization (optional future enhancement)
•	Recommendation tracking and effectiveness measurement
•	Real-time recalculation when data changes
Constraints:
•	Max 10 active recommendations per user
•	Recommendations expire after 90 days if not acted upon
•	Recalculate recommendations max once per day
•	Must explain reasoning (no black box AI)
Implementation Approach:
ENDPOINT: GET /api/v1/dashboard/recommendations
QUERY PARAMS:
- limit: integer (default: 5, max: 20)
- priority: enum['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] (optional filter)
- category: string (optional: 'TAX', 'INVESTMENT', 'PROTECTION', etc.)

BUSINESS LOGIC:
1. Fetch user profile and all financial data
2. Run recommendation engine rules:

RULE EXAMPLES:
// Critical: Urgent action needed
IF user.protectionModule.lifeCover < (user.income.annual * 10) AND user.dependents > 0:
  CREATE recommendation(
    priority: CRITICAL,
    category: PROTECTION,
    title: "Insufficient life cover for dependents",
    description: "Your life cover is below recommended levels for your family",
    estimatedImpact: "Protect your family's financial future",
    action: "Review life cover options",
    linkTo: "/protection"
  )

// High: Significant opportunity
IF user.taxStatus.uk_tax_resident AND 
   user.income.annual < 100000 AND
   user.savings.isa_unused_allowance > 10000:
  CREATE recommendation(
    priority: HIGH,
    category: TAX,
    title: "Use your £{amount} unused ISA allowance",
    description: "Tax year ends {date}. ISA allowances don't roll over",
    estimatedImpact: "Save up to £{tax_saved} in tax on investment returns",
    action: "Transfer savings to ISA",
    linkTo: "/savings"
  )

// Medium: Good practice
IF user.retirement.uk_pension_contributions < user.retirement.annual_allowance * 0.5:
  CREATE recommendation(
    priority: MEDIUM,
    category: RETIREMENT,
    title: "Consider increasing pension contributions",
    description: "You're using only {percent}% of your pension allowance",
    estimatedImpact: "Tax relief up to £{amount} available",
    action: "Review pension contributions",
    linkTo: "/retirement"
  )

3. Score and rank recommendations:
   score = base_priority_score + estimated_impact_value + urgency_factor + personalization_score

4. Filter dismissed and completed recommendations

5. Apply limit and return top N

RESPONSE:
{
  recommendations: [
    {
      id: uuid,
      priority: 'CRITICAL',
      category: 'PROTECTION',
      title: string,
      description: string,
      reasoning: string (why this recommendation),
      estimatedImpact: {
        description: string,
        monetaryValue: decimal (optional),
        currency: string
      },
      action: {
        description: string,
        linkTo: string (module URL),
        externalLink: string (optional)
      },
      dueDate: date (optional, e.g., tax year end),
      status: enum['NEW', 'VIEWED', 'IN_PROGRESS', 'COMPLETED', 'DISMISSED'],
      createdAt: timestamp,
      lastUpdated: timestamp
    },
    ...
  ],
  metadata: {
    totalRecommendations: integer,
    byCriticalityCount: {critical: int, high: int, medium: int, low: int},
    lastCalculated: timestamp,
    nextCalculation: timestamp
  }
}
User Flow:
[Dashboard Landing] → [Recommendations Section]
     ↓
[Prioritized List Display]
  Each recommendation card shows:
  - Priority badge (color-coded)
  - Title
  - Brief description
  - Estimated impact (highlighted)
  - Action button
     ↓
[User Actions per Card]
  1. Click "Take Action" → Navigate to module
  2. Click "Learn More" → Expand card with full reasoning
  3. Mark as "In Progress" → Status updated
  4. Dismiss → Card removed, feedback optional
     ↓
[Filter/Sort Options]
  - By priority
  - By category
  - By estimated impact
     ↓
[View All Recommendations] → [Full recommendations page]
  - Historical recommendations
  - Completed recommendations with outcomes
  - Effectiveness tracking
API Endpoints:
•	GET /api/v1/dashboard/recommendations - Get active recommendations
•	GET /api/v1/dashboard/recommendations/{id} - Get specific recommendation
•	PUT /api/v1/dashboard/recommendations/{id}/status - Update status
•	POST /api/v1/dashboard/recommendations/{id}/dismiss - Dismiss recommendation
•	POST /api/v1/dashboard/recommendations/recalculate - Trigger recalculation
•	GET /api/v1/dashboard/recommendations/history - Get historical recommendations
Data Models:
TABLE: ai_recommendations
- id: UUID (PK)
- user_id: UUID (FK to users)
- priority: ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')
- category: ENUM('TAX', 'INVESTMENT', 'PROTECTION', 'RETIREMENT', 'IHT', 'SAVINGS', 'GENERAL')
- title: VARCHAR(255)
- description: TEXT
- reasoning: TEXT
- estimated_impact_description: TEXT
- estimated_impact_value: DECIMAL(15,2)
- estimated_impact_currency: CHAR(3)
- action_description: TEXT
- action_link_to: VARCHAR(255)
- action_external_link: VARCHAR(500)
- due_date: DATE (optional)
- status: ENUM('NEW', 'VIEWED', 'IN_PROGRESS', 'COMPLETED', 'DISMISSED')
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
- expires_at: TIMESTAMP (created_at + 90 days)
- completed_at: TIMESTAMP
- dismissed_at: TIMESTAMP
- score: DECIMAL(10,2) (for ranking)

TABLE: recommendation_rules
- id: UUID (PK)
- rule_name: VARCHAR(100) UNIQUE
- rule_code: TEXT (stored rule logic reference)
- category: ENUM(...)
- base_priority: ENUM(...)
- active: BOOLEAN
- version: INTEGER
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: recommendation_feedback
- id: UUID (PK)
- recommendation_id: UUID (FK to ai_recommendations)
- user_id: UUID (FK to users)
- action_taken: ENUM('FOLLOWED', 'DISMISSED', 'PARTIALLY_FOLLOWED')
- feedback_text: TEXT
- rating: INTEGER (1-5)
- created_at: TIMESTAMP

TABLE: recommendation_effectiveness
- id: UUID (PK)
- recommendation_id: UUID (FK to ai_recommendations)
- user_id: UUID (FK to users)
- predicted_impact: DECIMAL(15,2)
- actual_impact: DECIMAL(15,2) (measured post-action)
- accuracy_score: DECIMAL(5,2)
- measurement_date: TIMESTAMP

INDEX on ai_recommendations(user_id, status, priority, due_date)
INDEX on ai_recommendations(user_id, created_at DESC)
INDEX on ai_recommendations(expires_at) (for cleanup job)
Error Handling:
ERROR CASES:
1. Recommendation engine failure
   - Response: 200 OK
   - Return cached recommendations with flag: "Showing previous recommendations"
   - Log error for investigation
   - Retry engine in background
   
2. No recommendations available (all completed/dismissed)
   - Response: 200 OK
   - Message: "Great job! You're on top of your finances. Check back tomorrow for new insights"
   
3. Stale data (user changed something affecting recommendations)
   - Response: 200 OK with flag: "Recommendations updating based on your recent changes"
   - Trigger async recalculation
   
4. Invalid status update
   - Response: 400 Bad Request
   - Message: "Cannot mark dismissed recommendation as in progress"
   
5. Recommendation expired
   - Response: 410 Gone
   - Message: "This recommendation has expired. Refresh to see current recommendations"

EDGE CASES:
- Conflicting recommendations: Engine deduplicates and prioritizes
- Recommendation becomes invalid after user action: Auto-mark completed
- Seasonal recommendations (e.g., tax year end): Increase priority as deadline approaches
- User dismisses repeatedly: Reduce frequency of similar recommendations
- Circular recommendations: Detect and prevent (e.g., "invest more" vs "save more")
- Cross-module recommendations: Ensure recommendation considers all modules
- Rapid user data changes: Debounce recalculation (max once per hour)
Performance Considerations:
•	Recommendation calculation: Async job, run nightly
•	Trigger on-demand recalculation: Rate limited to once per hour
•	Cache recommendation list: 1 hour TTL
•	Rules engine: Optimize for <5 seconds execution time
•	Expected recommendations per user: 5-15 active at any time
•	Status updates: Real-time (no caching)
•	Recommendation scoring: Pre-calculate during generation
•	Historical recommendations: Archive after 1 year (keep summary only)
•	Machine learning enhancement (future): Batch train models weekly
•	A/B testing framework: Track which recommendations drive action
 
