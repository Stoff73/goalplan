5. SAVINGS MODULE
Feature 5.1: Cash Account Management
Feature Name: Multi-Currency Cash Account Tracking
User Story: As a user with bank accounts in UK and SA, I want to track all my cash accounts, see total savings, and understand the tax treatment of interest earned.
Acceptance Criteria:
•	User can add bank accounts from UK, SA, and other countries
•	Each account includes: bank name, account type, balance, currency, interest rate
•	Support for current accounts, savings accounts, fixed deposits
•	Track interest earned and tax treatment
•	Calculate total savings across all accounts
•	Emergency fund assessment
•	Account categorization (emergency, short-term goals, long-term)
•	Interest rate comparison and alerts for better rates
•	Manual balance updates with historical tracking
•	Bank account aggregation via Open Banking (future enhancement)
•	ISA allowance tracking (UK)
•	TFSA contribution tracking (SA)
Technical Requirements:
•	Multi-currency support with real-time conversion
•	Interest calculation engine (simple and compound)
•	Historical balance tracking (snapshots)
•	Tax calculation integration for interest income
•	Open Banking API integration capability (Phase 2)
•	Encryption for sensitive bank details
Constraints:
•	Balance updates: Max 10 per day per account (prevent abuse)
•	Historical data: Retain 7 years minimum (regulatory requirement)
•	Interest rates: Percentage format, max 2 decimal places
•	Account deletion: Soft delete only (audit trail)
Implementation Approach:
ENDPOINT: POST /api/v1/savings/accounts
REQUEST BODY:
{
  bankName: string,
  accountType: enum['CURRENT', 'SAVINGS', 'FIXED_DEPOSIT', 'MONEY_MARKET', 
                    'CASH_ISA', 'TFSA', 'NOTICE_ACCOUNT', 'OTHER'],
  accountNumber: string (last 4 digits only for security),
  country: enum['UK', 'SA', 'OTHER'],
  currency: string,
  currentBalance: decimal,
  interestRate: decimal (annual percentage),
  interestPaymentFrequency: enum['MONTHLY', 'QUARTERLY', 'ANNUALLY', 'MATURITY'],
  accountPurpose: enum['EMERGENCY_FUND', 'SHORT_TERM_GOAL', 'LONG_TERM_SAVINGS', 'GENERAL'],
  openDate: date,
  maturityDate: date (optional, for fixed deposits),
  noticePeriod: integer (days, for notice accounts),
  accessRestrictions: text,
  isJointAccount: boolean,
  jointAccountHolder: string (if applicable)
}

BUSINESS LOGIC:
1. Validate account data:
   - Balance >= 0
   - Interest rate between 0 and 20% (sanity check)
   - Account number encrypted before storage
   
2. Determine tax treatment:
   IF country = 'UK':
     apply_uk_interest_tax_rules()
     // PSA: £1000 for basic rate, £500 for higher rate, £0 for additional rate
     // Starting rate for savings: £5000 if income < £17,570
     
   IF accountType = 'CASH_ISA':
     interest_tax_free = TRUE
     track_isa_subscription()
     
   IF country = 'SA':
     apply_sa_interest_exemption()
     // First R23,800 exempt (under 65), R34,500 (65+)
     
   IF accountType = 'TFSA':
     interest_tax_free = TRUE
     track_tfsa_contribution()

3. Calculate projected interest:
   IF interestPaymentFrequency = 'MONTHLY':
     monthly_rate = annual_rate / 12
     projected_annual = balance * (1 + monthly_rate)^12 - balance
   ELSE IF interestPaymentFrequency = 'ANNUALLY':
     projected_annual = balance * annual_rate

4. Assess emergency fund adequacy:
   IF accountPurpose = 'EMERGENCY_FUND':
     recommended_emergency = user.monthly_expenses * 6
     current_emergency = SUM(accounts WHERE purpose = 'EMERGENCY_FUND')
     emergency_fund_status = current_emergency / recommended_emergency

5. Create balance snapshot

6. Check for better rates (background job)

RESPONSE:
{
  id: uuid,
  accountDetails: {...},
  taxTreatment: {
    interestTaxFree: boolean,
    applicableTaxRate: decimal,
    annualExemptionUsed: decimal,
    annualExemptionRemaining: decimal
  },
  projections: {
    projectedAnnualInterest: decimal,
    projectedMonthlyInterest: decimal,
    effectiveRate: decimal
  },
  conversionDetails: {
    balanceGbp: decimal,
    balanceZar: decimal,
    exchangeRate: decimal
  }
}
User Flow:
[Savings Dashboard] → [Cash Accounts Tab]
     ↓
[Account Summary Cards]
  - Total savings (prominent)
  - By currency breakdown
  - By purpose breakdown
  - Emergency fund status indicator
     ↓
[Add Account Button]
     ↓
[Account Entry Form - Step 1: Bank Details]
  - Bank name (autocomplete with popular banks)
  - Country
  - Account type (visual cards with descriptions)
     ↓
[Account Entry Form - Step 2: Balance & Interest]
  - Current balance and currency
  - Interest rate (with comparison to market average)
  - Interest payment frequency
  - Account number (last 4 digits)
     ↓
[Account Entry Form - Step 3: Purpose & Dates]
  - Account purpose (Emergency, Goals, etc.)
  - Open date
  - Maturity date (if applicable)
  - Access restrictions/notice period
     ↓
[Tax Treatment Preview]
  - Show if interest is taxable
  - Exemption status (PSA/SA exemption)
  - ISA/TFSA allowance impact
     ↓
[Save Account]
     ↓
[Account List View]
  - Card view with key metrics per account
  - Quick balance update buttons
  - Filter: By type, country, purpose
  - Sort: By balance, interest rate
  - Visual indicators: High interest (green), Low interest (amber)
API Endpoints:
•	POST /api/v1/savings/accounts - Add account
•	PUT /api/v1/savings/accounts/{id} - Update account
•	DELETE /api/v1/savings/accounts/{id} - Delete account (soft delete)
•	GET /api/v1/savings/accounts - List all accounts
•	GET /api/v1/savings/accounts/{id} - Get specific account
•	POST /api/v1/savings/accounts/{id}/update-balance - Update balance
•	GET /api/v1/savings/accounts/{id}/balance-history - Get balance history
•	GET /api/v1/savings/summary - Get savings summary with totals
•	GET /api/v1/savings/emergency-fund-status - Emergency fund assessment
•	POST /api/v1/savings/compare-rates - Compare rates with market
Data Models:
TABLE: savings_accounts
- id: UUID (PK)
- user_id: UUID (FK to users)
- bank_name: VARCHAR(255)
- account_type: ENUM('CURRENT', 'SAVINGS', 'FIXED_DEPOSIT', 'MONEY_MARKET', 
                     'CASH_ISA', 'TFSA', 'NOTICE_ACCOUNT', 'OTHER')
- account_number_encrypted: VARCHAR(255) (last 4 digits only, encrypted)
- country: ENUM('UK', 'SA', 'OTHER')
- currency: CHAR(3)
- current_balance: DECIMAL(15,2)
- balance_gbp: DECIMAL(15,2) (calculated)
- balance_zar: DECIMAL(15,2) (calculated)
- interest_rate: DECIMAL(5,2)
- interest_payment_frequency: ENUM('MONTHLY', 'QUARTERLY', 'ANNUALLY', 'MATURITY')
- account_purpose: ENUM('EMERGENCY_FUND', 'SHORT_TERM_GOAL', 'LONG_TERM_SAVINGS', 'GENERAL')
- open_date: DATE
- maturity_date: DATE
- notice_period_days: INTEGER
- access_restrictions: TEXT
- is_joint_account: BOOLEAN DEFAULT FALSE
- joint_account_holder: VARCHAR(255)
- status: ENUM('ACTIVE', 'CLOSED', 'MATURED')
- deleted: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: account_balance_history
- id: UUID (PK)
- account_id: UUID (FK to savings_accounts)
- balance: DECIMAL(15,2)
- balance_date: DATE
- update_type: ENUM('MANUAL', 'AUTO', 'INTEREST_PAYMENT', 'WITHDRAWAL', 'DEPOSIT')
- notes: TEXT
- created_at: TIMESTAMP

TABLE: interest_payments
- id: UUID (PK)
- account_id: UUID (FK to savings_accounts)
- payment_date: DATE
- gross_interest: DECIMAL(10,2)
- tax_withheld: DECIMAL(10,2)
- net_interest: DECIMAL(10,2)
- tax_year_uk: VARCHAR(7)
- tax_year_sa: VARCHAR(9)
- created_at: TIMESTAMP

TABLE: isa_contributions
- id: UUID (PK)
- user_id: UUID (FK to users)
- account_id: UUID (FK to savings_accounts)
- tax_year: VARCHAR(7) (e.g., '2024/25')
- contribution_amount: DECIMAL(10,2)
- contribution_date: DATE
- contribution_type: ENUM('CASH_ISA', 'STOCKS_ISA', 'LISA', 'JUNIOR_ISA')
- created_at: TIMESTAMP

TABLE: tfsa_contributions
- id: UUID (PK)
- user_id: UUID (FK to users)
- account_id: UUID (FK to savings_accounts)
- tax_year: VARCHAR(9) (e.g., '2024/2025')
- contribution_amount: DECIMAL(10,2)
- contribution_date: DATE
- lifetime_contributions: DECIMAL(10,2) (running total)
- created_at: TIMESTAMP

TABLE: emergency_fund_settings
- user_id: UUID (PK, FK to users)
- monthly_expenses: DECIMAL(10,2)
- target_months: INTEGER (typically 3-6)
- target_amount: DECIMAL(15,2) (calculated)
- updated_at: TIMESTAMP

INDEX on savings_accounts(user_id, status)
INDEX on account_balance_history(account_id, balance_date DESC)
INDEX on interest_payments(account_id, payment_date)
INDEX on isa_contributions(user_id, tax_year)
INDEX on tfsa_contributions(user_id, tax_year)
Error Handling:
ERROR CASES:
1. Negative balance entered
   - Response: 400 Bad Request
   - Message: "Account balance cannot be negative"
   
2. Interest rate exceeds reasonable threshold
   - Response: 400 Bad Request
   - Message: "Interest rate seems unusually high. Please verify (max 20%)"
   
3. ISA contribution exceeds annual allowance
   - Response: 400 Bad Request
   - Message: "This contribution would exceed your £{allowance} ISA allowance for {tax_year}"
   - Show: Current contributions: £{current}, Allowance remaining: £{remaining}
   
4. TFSA lifetime contribution exceeds R500,000
   - Response: 400 Bad Request
   - Message: "This contribution would exceed the R500,000 lifetime TFSA limit"
   - Show: Current lifetime contributions: R{current}, Remaining: R{remaining}
   
5. Too many balance updates in a day
   - Response: 429 Too Many Requests
   - Message: "Maximum 10 balance updates per day reached. Please try again tomorrow"
   
6. Maturity date before open date
   - Response: 400 Bad Request
   - Message: "Maturity date must be after account opening date"
   
7. Closed account balance update attempt
   - Response: 400 Bad Request
   - Message: "Cannot update balance for a closed account"

EDGE CASES:
- Multiple ISAs of same type in same tax year: Warn user (HMRC rules allow but must track total)
- ISA transfer from previous year: Don't count against current year allowance
- TFSA withdrawal: Doesn't free up contribution room (lifetime limit)
- Joint account: Assume 50/50 ownership unless specified otherwise
- Foreign currency accounts: Daily exchange rate updates for GBP/ZAR equivalents
- Fixed deposit early withdrawal: Penalty calculation and note
- Notice account withdrawal: Flag if within notice period
- Account closure: Move to 'CLOSED' status, retain historical data
- Negative interest rates: Rare but valid (some currencies)
- Interest paid gross (no tax withheld): User responsible for declaring
- Accounts in cryptocurrencies: Not supported (too volatile for savings)
Performance Considerations:
•	Balance history: Paginate if >100 entries
•	Currency conversion: Cache exchange rates (1 day TTL)
•	Interest calculations: Pre-calculate and store monthly
•	Emergency fund assessment: Cache for 1 week or until balance changes
•	Balance update: Real-time, <200ms response
•	Account list query with balances: <500ms
•	Expected accounts per user: 3-10
•	Historical balance queries: Index on date field
•	ISA/TFSA allowance checks: Cache current tax year data
•	Interest payment tracking: Background job (monthly)
•	Market rate comparison: Daily batch job, cache results
 
Feature 5.2: ISA and TFSA Allowance Tracking
Feature Name: Tax-Advantaged Savings Allowance Management
User Story: As a UK tax resident, I want to track my ISA allowance usage across all ISA types, and as an SA tax resident, I want to track my TFSA contributions, so I can maximize my tax-efficient savings.
Acceptance Criteria:
•	Track ISA allowance for current tax year (UK: April-April)
•	Support Cash ISA, Stocks & Shares ISA, LISA, Junior ISA
•	Show allowance used and remaining
•	Alert when approaching limit (90% used)
•	Track TFSA contributions for SA (March-February tax year)
•	TFSA lifetime limit tracking (R500,000)
•	Historical allowance usage by tax year
•	Suggest optimal use of remaining allowance
•	ISA transfer tracking (doesn't count against allowance)
•	Flexible ISA rule support (withdrawals and recontributions)
Technical Requirements:
•	Tax year calculation logic (UK and SA)
•	Running total calculations
•	ISA transfer vs new contribution differentiation
•	Flexible ISA withdrawal tracking
•	Alert/notification system
•	Historical data migration when allowances change
Constraints:
•	ISA allowance (2024/25): £20,000 across all ISAs
•	LISA: £4,000 per year (part of overall £20,000)
•	Junior ISA: £9,000 per year (separate from adult allowance)
•	TFSA annual limit: R36,000 (as of last update)
•	TFSA lifetime limit: R500,000
•	Cannot backdate contributions to previous tax years
Implementation Approach:
ENDPOINT: GET /api/v1/savings/tax-efficient-allowances
QUERY PARAMS:
- taxYear: string (e.g., 'UK-2024/25' or 'SA-2024/2025')
- country: enum['UK', 'SA']

BUSINESS LOGIC:
1. Determine current tax year:
   UK: April 6 to April 5
   SA: March 1 to February 28/29

2. Fetch allowance limits (from configuration):
   uk_isa_limit = 20000  // £20,000 for 2024/25
   uk_lisa_limit = 4000  // Within overall limit
   uk_junior_isa_limit = 9000
   sa_tfsa_annual_limit = 36000  // R36,000
   sa_tfsa_lifetime_limit = 500000  // R500,000

3. Calculate usage:
   FOR UK:
     total_isa_contributions = SUM(isa_contributions WHERE tax_year = current_tax_year)
     lisa_contributions = SUM(isa_contributions WHERE type = 'LISA' AND tax_year = current_tax_year)
     
     isa_allowance_remaining = uk_isa_limit - total_isa_contributions
     lisa_allowance_remaining = uk_lisa_limit - lisa_contributions
     
     // Flexible ISA adjustments
     IF has_flexible_isa:
       flexible_isa_withdrawals = SUM(withdrawals WHERE tax_year = current_tax_year)
       additional_allowance = flexible_isa_withdrawals
       adjusted_allowance_remaining = isa_allowance_remaining + additional_allowance
   
   FOR SA:
     tfsa_contributions_this_year = SUM(tfsa_contributions WHERE tax_year = current_tax_year)
     tfsa_lifetime_total = SUM(tfsa_contributions WHERE created_at <= NOW())
     
     tfsa_annual_remaining = sa_tfsa_annual_limit - tfsa_contributions_this_year
     tfsa_lifetime_remaining = sa_tfsa_lifetime_limit - tfsa_lifetime_total

4. Check alert thresholds:
   IF isa_allowance_remaining < (uk_isa_limit * 0.1):
     trigger_alert("90% of ISA allowance used")
   
   IF days_until_tax_year_end < 30 AND isa_allowance_remaining > 5000:
     trigger_alert("Significant ISA allowance unused, tax year ending soon")

5. Generate recommendations:
   recommend_isa_usage()
   recommend_tfsa_usage()

RESPONSE:
{
  country: 'UK',
  taxYear: '2024/25',
  taxYearStart: date,
  taxYearEnd: date,
  daysRemainingInTaxYear: integer,
  isaAllowances: {
    overallLimit: 20000,
    used: decimal,
    remaining: decimal,
    percentageUsed: decimal,
    byType: [
      {type: 'CASH_ISA', used: decimal},
      {type: 'STOCKS_ISA', used: decimal},
      {type: 'LISA', used: decimal, limit: 4000, remaining: decimal}
    ],
    flexibleIsaWithdrawals: decimal (if applicable),
    additionalAllowanceFromWithdrawals: decimal
  },
  tfsaAllowances: {
    annualLimit: 36000,
    annualUsed: decimal,
    annualRemaining: decimal,
    lifetimeLimit: 500000,
    lifetimeUsed: decimal,
    lifetimeRemaining: decimal,
    percentageOfLifetimeUsed: decimal
  },
  alerts: [
    {
      severity: enum['INFO', 'WARNING', 'CRITICAL'],
      message: string,
      actionRequired: string
    }
  ],
  recommendations: [
    {
      title: string,
      description: string,
      estimatedBenefit: decimal
    }
  ],
  historicalUsage: [
    {taxYear: string, isaUsed: decimal, tfsaUsed: decimal},
    ...
  ]
}
User Flow:
[Savings Dashboard] → [Tax-Efficient Allowances Card]
     ↓
[Allowance Overview Display]
  - ISA Allowance (if UK resident):
    - Progress bar: Used vs Remaining
    - Breakdown by ISA type
    - Days remaining in tax year
  - TFSA Allowance (if SA resident):
    - Annual: Progress bar
    - Lifetime: Progress bar with milestone markers
     ↓
[Contribution Actions]
  - "Add ISA Contribution" button → Links to add account or update balance
  - "Add TFSA Contribution" button → Links to add account or update balance
     ↓
[Alerts Section]
  - Critical: Red banner (e.g., "Only £2,000 ISA allowance left, 45 days until tax year end")
  - Warning: Amber banner
  - Info: Blue banner
     ↓
[Recommendations Section]
  - AI-generated suggestions
  - "Transfer cash savings to ISA" with estimated tax saving
  - "Maximize LISA for home purchase bonus" (25% government bonus)
     ↓
[Historical Tab]
  - Table: Tax year, ISA used, TFSA used
  - Chart: Allowance usage trend over years
     ↓
[Settings/Configuration]
  - Set notification preferences
  - Customize alert thresholds
API Endpoints:
•	GET /api/v1/savings/tax-efficient-allowances - Get allowance summary
•	GET /api/v1/savings/tax-efficient-allowances/history - Historical usage
•	POST /api/v1/savings/isa-contribution - Record ISA contribution
•	POST /api/v1/savings/tfsa-contribution - Record TFSA contribution
•	POST /api/v1/savings/isa-transfer - Record ISA transfer (doesn't count against allowance)
•	POST /api/v1/savings/flexible-isa-withdrawal - Record flexible ISA withdrawal
•	GET /api/v1/savings/allowance-alerts - Get current alerts
•	PUT /api/v1/savings/allowance-alerts/preferences - Update alert preferences
Data Models:
TABLE: tax_efficient_allowances_config
- id: UUID (PK)
- country: ENUM('UK', 'SA')
- tax_year: VARCHAR(10)
- allowance_type: ENUM('ISA_OVERALL', 'LISA', 'JUNIOR_ISA', 'TFSA_ANNUAL', 'TFSA_LIFETIME')
- limit_amount: DECIMAL(10,2)
- currency: CHAR(3)
- effective_from: DATE
- effective_to: DATE
- notes: TEXT

TABLE: isa_transfers
- id: UUID (PK)
- user_id: UUID (FK to users)
- from_provider: VARCHAR(255)
- to_provider: VARCHAR(255)
- amount: DECIMAL(10,2)
- isa_type: ENUM('CASH_ISA', 'STOCKS_ISA', 'LISA')
- tax_year_transferred: VARCHAR(7)
- transfer_date: DATE
- transfer_reference: VARCHAR(100)
- created_at: TIMESTAMP

TABLE: flexible_isa_withdrawals
- id: UUID (PK)
- account_id: UUID (FK to savings_accounts)
- withdrawal_amount: DECIMAL(10,2)
- withdrawal_date: DATE
- tax_year: VARCHAR(7)
- recontribution_allowance_created: DECIMAL(10,2)
- recontribution_allowance_used: DECIMAL(10,2)
- expires_at: DATE (end of tax year)
- created_at: TIMESTAMP

TABLE: allowance_alerts
- id: UUID (PK)
- user_id: UUID (FK to users)
- alert_type: ENUM('ISA_90_PERCENT', 'ISA_TAX_YEAR_END', 'TFSA_90_PERCENT', 
                   'TFSA_LIFETIME_APPROACHING', 'TFSA_TAX_YEAR_END')
- severity: ENUM('INFO', 'WARNING', 'CRITICAL')
- message: TEXT
- action_required: TEXT
- triggered_at: TIMESTAMP
- dismissed: BOOLEAN DEFAULT FALSE
- dismissed_at: TIMESTAMP

TABLE: allowance_alert_preferences
- user_id: UUID (PK, FK to users)
- isa_allowance_alerts_enabled: BOOLEAN DEFAULT TRUE
- isa_alert_threshold_percentage: DECIMAL(5,2) DEFAULT 90.0
- tfsa_allowance_alerts_enabled: BOOLEAN DEFAULT TRUE
- tfsa_alert_threshold_percentage: DECIMAL(5,2) DEFAULT 90.0
- tax_year_end_reminder_days: INTEGER DEFAULT 30
- notification_channels: JSON ['EMAIL', 'IN_APP', 'SMS']
- updated_at: TIMESTAMP

VIEW: v_current_allowance_usage (materialized view, refreshed daily)
- user_id
- country
- current_tax_year
- isa_overall_used
- isa_overall_remaining
- lisa_used
- lisa_remaining
- tfsa_annual_used
- tfsa_annual_remaining
- tfsa_lifetime_used
- tfsa_lifetime_remaining
- last_updated: TIMESTAMP

INDEX on isa_contributions(user_id, tax_year)
INDEX on tfsa_contributions(user_id, tax_year)
INDEX on isa_transfers(user_id, tax_year_transferred)
INDEX on allowance_alerts(user_id, triggered_at, dismissed)
Error Handling:
ERROR CASES:
1. ISA contribution exceeds remaining allowance
   - Response: 400 Bad Request
   - Message: "This contribution of £{amount} would exceed your ISA allowance by £{excess}"
   - Suggestion: "Maximum contribution allowed: £{remaining}"
   
2. TFSA contribution exceeds annual limit
   - Response: 400 Bad Request
   - Message: "This contribution of R{amount} would exceed your TFSA annual limit by R{excess}"
   
3. TFSA contribution exceeds lifetime limit
   - Response: 400 Bad Request
   - Message: "This contribution would exceed the R500,000 lifetime TFSA limit"
   - Show: "You have R{remaining} lifetime allowance remaining"
   
4. LISA contribution for user over 50
   - Response: 400 Bad Request
   - Message: "LISA contributions not permitted after age 50"
   
5. Multiple adult ISAs of same type in same tax year
   - Response: 400 Bad Request
   - Message: "You can only contribute to one Cash ISA per tax year"
   - Suggestion: "Consider an ISA transfer instead"
   
6. Backdated contribution to previous tax year
   - Response: 400 Bad Request
   - Message: "Cannot add contributions to previous tax year {year}"
   
7. ISA transfer amount doesn't match provider statement
   - Response: 400 Bad Request (validation warning)
   - Message: "Transfer amount seems inconsistent with typical ISA values. Please verify"

EDGE CASES:
- User turns 18 mid-tax-year: Junior ISA converts to adult ISA, track both allowances
- User becomes UK resident mid-tax-year: Pro-rata ISA allowance (actually full allowance available)
- User becomes SA resident mid-tax-year: Pro-rata TFSA allowance (actually annual limit applies)
- ISA provider failure: Transferred ISAs may have delays, don't count against new allowance
- Flexible ISA withdrawal and recontribution in same tax year: Track carefully
- LISA government bonus: 25% bonus paid by government, doesn't count against allowance
- LISA withdrawal before 60 (except first home/terminal illness): 25% penalty
- Help to Buy ISA (closed to new savers): Existing accounts can continue
- Bed and ISA: Selling shares to buy within ISA, counts as new contribution
- In-specie ISA transfer: Value at transfer date, not original purchase value
- TFSA withdrawal: Never creates additional contribution room (unlike UK pension annual allowance)
- Death of ISA holder: Becomes a "continuing ISA" with additional permitted subscription for spouse
Performance Considerations:
•	Allowance calculation: Use materialized view, refresh daily
•	Real-time contribution validation: Cache current tax year allowances
•	Alert generation: Daily batch job at midnight
•	Historical usage queries: Pre-aggregate by tax year
•	Expected API calls: High frequency during tax year-end (March-April)
•	Response time target: <200ms for allowance summary
•	Alert check: <50ms (from cache)
•	Flexible ISA calculation complexity: Cache withdrawal allowances
•	Tax year-end surge: Scale infrastructure, expect 10x normal traffic
•	Notification dispatch: Queue-based async processing
 
