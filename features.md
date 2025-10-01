Features Document: Dual-Country Financial Planning Platform
EXECUTIVE SUMMARY: COMPLETE FEATURES DOCUMENT
This comprehensive Product Requirements Document and Features Specification covers a complete dual-country (UK and South Africa) financial planning web application with the following major components:
1. CORE INFRASTRUCTURE
•	User Authentication & Profile Management: 2FA, session management, secure login
•	User Information Module: Tax status, domicile tracking, income management, family details
•	Central Dashboard: Net worth aggregation, real-time updates, goal tracking
2. FINANCIAL MODULES
Protection Module
•	Life assurance, critical illness, income protection tracking
•	Coverage gap analysis
•	Tax treatment (UK trusts, SA estate duty)
•	Beneficiary management
•	Premium tracking and reminders
Savings Module
•	Multi-currency cash account tracking
•	ISA and TFSA allowance management
•	Emergency fund assessment
•	Interest income tax calculation
•	Bank account aggregation capability
Investment Module
•	Portfolio management (stocks, funds, ETFs)
•	ISA, GIA, VCT, EIS, SEIS tracking
•	SA unit trusts and equity investments
•	Asset allocation analysis
•	Tax lot tracking for CGT
•	Dividend income management
Retirement Module
•	UK: DB/DC pensions, SIPP, personal pensions, state pension
•	SA: Pension funds, provident funds, retirement annuities, preservation funds
•	Cross-border: QROPS/ROPS tracking
•	Annual allowance monitoring (UK)
•	Section 10C deduction tracking (SA)
•	Retirement income projection
Inheritance Tax Planning Module
•	Comprehensive asset register (all jurisdictions)
•	Liabilities register with deductibility rules
•	UK IHT calculation (NRB, RNRB, reliefs)
•	SA Estate Duty calculation
•	Lifetime gifts register (PETs tracking, 7-year rule)
•	Estate value projection
•	DTA relief application
3. TAX INTELLIGENCE ENGINE
Core Tax Calculations
•	UK Income Tax (including Scottish rates)
•	UK National Insurance (Class 1, 2, 4)
•	UK Capital Gains Tax
•	UK Dividend Tax
•	SA Income Tax with rebates
•	SA Capital Gains Tax (inclusion rate)
•	SA Dividend Withholding Tax
Double Tax Agreement (DTA) Relief
•	Automated DTA provision application
•	Foreign tax credit calculation
•	Source vs residence taxation determination
•	Tie-breaker rules for dual residents
•	Income categorization by DTA article
Tax Residency Determination
•	UK Statutory Residence Test (SRT) automation
•	SA Physical Presence Test
•	UK domicile and deemed domicile tracking
•	Split year treatment identification
•	Historical residency tracking
4. AI ADVISORY ENGINE
Recommendation Generation
•	Protection recommendations (coverage gaps, trust structures)
•	Savings recommendations (emergency fund, ISA/TFSA usage)
•	Investment recommendations (diversification, tax efficiency, CGT harvesting)
•	Retirement recommendations (contribution optimization, carry forward)
•	Tax optimization recommendations (allowance usage, marriage allowance)
•	IHT planning recommendations (gifting strategies, estate equalization)
•	Prioritization by urgency and impact
•	Estimated benefit calculations
Goal-Based Financial Planning
•	SMART goal creation and validation
•	Required contribution calculations
•	Savings vehicle recommendations
•	Feasibility assessment
•	Progress tracking with milestones
•	Monte Carlo simulation for success probability
•	Goal conflict resolution
•	Alternative scenario generation
Scenario Analysis & What-If Modeling
•	Major life event modeling (retirement, relocation, business sale)
•	Side-by-side scenario comparison
•	Impact analysis across all modules
•	Sensitivity analysis
•	Risk assessment
•	Probability-weighted outcomes
•	Trade-off identification
Personalization Engine
•	Behavioral tracking and learning
•	User profile building (demographics, behavior, preferences)
•	Recommendation personalization
•	Collaborative filtering
•	A/B testing framework
•	Feedback loop processing
•	Model retraining pipeline
•	Explainable AI
5. KEY TECHNICAL FEATURES
Architecture
•	Modular design (each module independent)
•	API-first approach
•	Multi-currency support (GBP, ZAR, others)
•	Historical data tracking (temporal queries)
•	Real-time calculations
•	Async job processing
•	Caching strategies
Data Management
•	Versioned tax configurations
•	Audit trails for all calculations
•	Document storage and OCR
•	Integration with external modules
•	Bank aggregation (Open Banking)
•	Currency conversion services
Security & Compliance
•	Bank-level encryption
•	GDPR and POPIA compliance
•	Role-based access control
•	Two-factor authentication
•	Data sovereignty considerations
•	Audit logging
Performance
•	Target response times: <1s dashboard, <200ms tax calc, <3s recommendations
•	Caching strategies (Redis, materialized views)
•	Async processing for heavy computations
•	Batch jobs for periodic updates
•	Scalable infrastructure
6. USER EXPERIENCE
Key User Flows
•	Progressive onboarding with guided setup
•	Intuitive data entry with validation
•	Real-time feedback and calculations
•	Visual dashboards and charts
•	Mobile-responsive design
•	Contextual help and education
Notifications & Alerts
•	Tax year-end reminders
•	Allowance usage warnings
•	Goal milestone achievements
•	Recommendation updates
•	Document expiry alerts
•	Multi-channel delivery (email, in-app, SMS)
7. REPORTING & EXPORT
•	Net worth statements
•	Tax preparation reports (self-assessment, provisional tax)
•	Portfolio performance reports
•	Goal progress reports
•	Estate planning summaries
•	Scenario comparison reports
•	PDF export functionality
•	CSV/Excel data export
8. INTEGRATION CAPABILITIES
•	Bank account aggregation
•	Investment platform APIs
•	Pension scheme data imports
•	HMRC/SARS integration (future)
•	Financial advisor collaboration
•	Third-party financial tools
9. ROADMAP CONSIDERATIONS
Phase 1: Foundation 
Core authentication and user management
•	User Information Module
•	Central Dashboard (basic)
•	One module (Savings - simplest) fully built
Phase 2: Core Modules 
•	Protection Module
•	Investment Module
•	Tax Intelligence Engine (basic)
•	Basic recommendations
Phase 3: Advanced Features 
•	Retirement Module (all products)
•	IHT Planning Module
•	DTA Relief Calculator
•	Enhanced Tax Intelligence
Phase 4: Intelligence 
•	Goal-Based Planning
•	Scenario Analysis
•	Advanced Recommendations
•	Personalization Engine
Phase 5: Enhancement 
•	Machine learning optimization
•	Additional jurisdictions
•	Advanced integrations
•	Mobile app development
10. SUCCESS METRICS
User Engagement
•	Daily/Monthly Active Users
•	Average session duration
•	Feature adoption rates
•	Recommendation acceptance rates
Value Delivery
•	Tax savings identified
•	Goals achieved on time
•	IHT liability reduction
•	Investment performance vs benchmarks
Quality
•	Calculation accuracy (>99.9%)
•	User satisfaction (NPS >50)
•	Support ticket volume (trend down)
•	System uptime (>99.5%)
11. RISK MITIGATION
Technical Risks
•	Complex tax calculations: Professional review, extensive testing
•	Data security: Best practices, regular audits, insurance
•	Performance at scale: Scalable architecture, load testing
•	Integration failures: Robust error handling, fallback mechanisms
Regulatory Risks
•	Crossing into regulated advice: Clear disclaimers, legal review
•	Tax law changes: Regular updates, versioned configurations
•	Data protection: GDPR/POPIA compliance by design
Operational Risks
•	Tax calculation errors: Multi-layer validation, professional oversight
•	User adoption: Excellent UX, comprehensive onboarding
•	Maintaining currency: Partnerships with tax professionals, regular updates
Table of Contents
1.	User Authentication & Profile Management
2.	User Information Module
3.	Central Dashboard
4.	Protection Module
5.	Savings Module
6.	Investment Module
7.	Retirement Module
8.	Inheritance Tax Planning Module
9.	Tax Intelligence Engine
10.	AI Advisory Engine
 
1. USER AUTHENTICATION & PROFILE MANAGEMENT
Feature 1.1: User Registration
Feature Name: User Registration and Onboarding
User Story: As a new user, I want to create an account with email and password so that I can securely access the financial planning platform.
Acceptance Criteria:
•	User can register with email and password
•	Email verification required before full access
•	Password must meet security requirements (min 12 chars, uppercase, lowercase, number, special char)
•	User receives welcome email with onboarding guide
•	Account created with default settings
•	GDPR/POPIA consent captured
•	User can select preferred country (UK/SA/Both)
Technical Requirements:
•	Encryption: bcrypt or Argon2 for password hashing
•	JWT tokens for session management
•	Email service integration (SendGrid, AWS SES, or similar)
•	Rate limiting on registration endpoint (max 5 attempts per IP per hour)
•	CAPTCHA integration to prevent bot registrations
Constraints:
•	Must comply with UK GDPR and SA POPIA
•	No Node.js backend
•	Session timeout: 30 minutes inactivity, 24 hours absolute
Implementation Approach:
ENDPOINT: POST /api/v1/auth/register
REQUEST BODY:
{
  email: string (valid email format),
  password: string (meets complexity requirements),
  firstName: string,
  lastName: string,
  country: enum['UK', 'SA', 'BOTH'],
  termsAccepted: boolean,
  marketingConsent: boolean
}

PROCESS:
1. Validate input data
2. Check if email already exists
3. Hash password using Argon2
4. Generate email verification token (UUID, expires in 24h)
5. Create user record with status='PENDING_VERIFICATION'
6. Store verification token in cache/DB
7. Send verification email
8. Return success response (do not reveal if email exists)

RESPONSE:
{
  success: true,
  message: "Registration successful. Please check your email.",
  userId: uuid
}
User Flow:
[Landing Page] → [Register Button]
     ↓
[Registration Form]
  - Email input
  - Password input (with strength indicator)
  - Confirm password
  - First name / Last name
  - Country selection
  - Terms checkbox
  - Marketing consent checkbox
     ↓
[Submit] → [Validation]
     ↓
[Success Message] → [Email Sent Notification]
     ↓
[User checks email] → [Clicks verification link]
     ↓
[Account Activated] → [Redirect to Login]
API Endpoints:
•	POST /api/v1/auth/register - Register new user
•	GET /api/v1/auth/verify-email?token={token} - Verify email
•	POST /api/v1/auth/resend-verification - Resend verification email
Data Models:
TABLE: users
- id: UUID (PK)
- email: VARCHAR(255) UNIQUE NOT NULL
- password_hash: VARCHAR(255) NOT NULL
- first_name: VARCHAR(100)
- last_name: VARCHAR(100)
- country_preference: ENUM('UK', 'SA', 'BOTH')
- status: ENUM('PENDING_VERIFICATION', 'ACTIVE', 'SUSPENDED', 'DELETED')
- email_verified: BOOLEAN DEFAULT FALSE
- terms_accepted_at: TIMESTAMP
- marketing_consent: BOOLEAN
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
- last_login_at: TIMESTAMP

TABLE: email_verification_tokens
- id: UUID (PK)
- user_id: UUID (FK to users)
- token: VARCHAR(255) UNIQUE
- expires_at: TIMESTAMP
- used: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP

INDEX on users.email
INDEX on email_verification_tokens.token
INDEX on email_verification_tokens.expires_at
Error Handling:
ERROR CASES:
1. Email already registered
   - Response: 409 Conflict
   - Message: "An account with this email already exists"
   
2. Invalid email format
   - Response: 400 Bad Request
   - Message: "Please provide a valid email address"
   
3. Password too weak
   - Response: 400 Bad Request
   - Message: "Password must be at least 12 characters and include uppercase, lowercase, number, and special character"
   
4. Terms not accepted
   - Response: 400 Bad Request
   - Message: "You must accept the terms and conditions"
   
5. Rate limit exceeded
   - Response: 429 Too Many Requests
   - Message: "Too many registration attempts. Please try again later"
   
6. Email service failure
   - Response: 500 Internal Server Error
   - Log error, queue for retry
   - Message: "Registration successful but verification email delayed"

EDGE CASES:
- User tries to register with existing email: Return generic success message (security)
- Token expired: Allow resend with new token
- User clicks verify link multiple times: Idempotent operation
- Simultaneous registrations with same email: DB unique constraint handles it
Performance Considerations:
•	Password hashing is CPU intensive: Use async hashing, consider queuing
•	Email sending should be async (message queue)
•	Cache email existence checks (5 min TTL) to reduce DB queries
•	Verification tokens in Redis for fast lookup
•	Rate limiting via Redis counter
•	Expected load: 1000 registrations/day, <500ms response time
 
Feature 1.2: User Login with 2FA
Feature Name: Secure Login with Two-Factor Authentication
User Story: As a registered user, I want to log in securely with my email and password, and enable two-factor authentication for enhanced security.
Acceptance Criteria:
•	User can login with email and password
•	Optional 2FA via authenticator app (TOTP)
•	Remember device option (30 days)
•	Account lockout after 5 failed attempts (30 min cooldown)
•	Notification sent on new device login
•	Session management with JWT tokens
•	Refresh token mechanism for extended sessions
Technical Requirements:
•	TOTP library for 2FA (pyotp, Google Authenticator compatible)
•	JWT with RS256 signing
•	Redis for session management and rate limiting
•	Device fingerprinting for "remember device"
•	IP logging for security monitoring
Constraints:
•	Access token lifetime: 15 minutes
•	Refresh token lifetime: 7 days
•	2FA code valid for 30 seconds (1 time-step)
•	Maximum 5 concurrent sessions per user
Implementation Approach:
ENDPOINT: POST /api/v1/auth/login
REQUEST BODY:
{
  email: string,
  password: string,
  deviceId: string (optional, for remember device),
  totpCode: string (optional, if 2FA enabled)
}

PROCESS:
1. Rate limit check (max 5 attempts per IP per 15 min)
2. Fetch user by email
3. Check account status (must be ACTIVE)
4. Verify password hash
5. If 2FA enabled and not remembered device:
   a. If totpCode provided, verify it
   b. If totpCode not provided, return 2FA_REQUIRED
6. Check device trust status
7. Generate access token (JWT, 15 min expiry)
8. Generate refresh token (JWT, 7 days expiry)
9. Store session in Redis
10. Update last_login_at
11. Log login event
12. Send notification if new device
13. Return tokens

RESPONSE SUCCESS:
{
  accessToken: string,
  refreshToken: string,
  expiresIn: 900,
  user: {
    id: uuid,
    email: string,
    firstName: string,
    lastName: string,
    twoFactorEnabled: boolean
  }
}

RESPONSE 2FA REQUIRED:
{
  requiresTwoFactor: true,
  message: "Please provide your 2FA code"
}
User Flow:
[Login Page]
     ↓
[Enter Email & Password] → [Submit]
     ↓
[Backend Validation]
     ↓
[2FA Enabled?] → YES → [2FA Code Entry Page]
     |                        ↓
     |                   [Enter TOTP Code]
     |                        ↓
     |                   [Verify Code]
     |                        ↓
     NO ← ← ← ← ← ← ← ← ← ← [Success]
     ↓
[Generate Tokens]
     ↓
[Redirect to Dashboard]
API Endpoints:
•	POST /api/v1/auth/login - User login
•	POST /api/v1/auth/refresh - Refresh access token
•	POST /api/v1/auth/logout - Invalidate session
•	POST /api/v1/auth/logout-all - Invalidate all sessions
•	GET /api/v1/auth/sessions - List active sessions
•	POST /api/v1/auth/enable-2fa - Enable 2FA
•	POST /api/v1/auth/disable-2fa - Disable 2FA
•	POST /api/v1/auth/verify-2fa-setup - Verify 2FA during setup
Data Models:
TABLE: user_sessions
- id: UUID (PK)
- user_id: UUID (FK to users)
- access_token_jti: VARCHAR(255) UNIQUE (JWT ID)
- refresh_token_jti: VARCHAR(255) UNIQUE
- device_id: VARCHAR(255)
- device_name: VARCHAR(255)
- ip_address: VARCHAR(45)
- user_agent: TEXT
- is_trusted: BOOLEAN DEFAULT FALSE
- last_activity: TIMESTAMP
- created_at: TIMESTAMP
- expires_at: TIMESTAMP

TABLE: user_2fa
- user_id: UUID (PK, FK to users)
- secret: VARCHAR(255) ENCRYPTED
- enabled: BOOLEAN DEFAULT FALSE
- backup_codes: JSON ENCRYPTED (array of hashed codes)
- created_at: TIMESTAMP
- last_used_at: TIMESTAMP

TABLE: login_attempts
- id: UUID (PK)
- email: VARCHAR(255)
- ip_address: VARCHAR(45)
- success: BOOLEAN
- failure_reason: VARCHAR(100)
- timestamp: TIMESTAMP

INDEX on user_sessions.user_id
INDEX on user_sessions.access_token_jti
INDEX on user_sessions.expires_at
INDEX on login_attempts.ip_address, timestamp
Error Handling:
ERROR CASES:
1. Invalid credentials
   - Response: 401 Unauthorized
   - Message: "Invalid email or password"
   - Log attempt in login_attempts table
   
2. Account locked (5 failed attempts)
   - Response: 423 Locked
   - Message: "Account temporarily locked due to multiple failed login attempts. Try again in 30 minutes"
   
3. Account not verified
   - Response: 403 Forbidden
   - Message: "Please verify your email address before logging in"
   
4. 2FA code invalid
   - Response: 401 Unauthorized
   - Message: "Invalid or expired 2FA code"
   
5. Rate limit exceeded
   - Response: 429 Too Many Requests
   - Message: "Too many login attempts. Please try again later"
   
6. Session limit exceeded
   - Response: 409 Conflict
   - Message: "Maximum number of active sessions reached. Please logout from another device"
   - Provide option to force logout oldest session

EDGE CASES:
- Concurrent logins: Allow up to 5 sessions
- Token refresh while access token still valid: Allow, extend session
- Logout with expired refresh token: Return success (idempotent)
- Time synchronization issues with TOTP: Accept codes from previous/next time window (90 sec total window)
- User changes password: Invalidate all existing sessions except current
Performance Considerations:
•	Redis session store for fast token validation
•	JWT signature verification is CPU intensive: Cache public key
•	Rate limiting counters in Redis (sliding window algorithm)
•	Async notification sending (queue)
•	Expected load: 10,000 logins/day, <200ms response time
•	Session validation on every API call must be <10ms
•	Consider token payload size (keep under 1KB)
 
2. USER INFORMATION MODULE
Feature 2.1: Tax Status & Domicile Management
Feature Name: Comprehensive Tax Status and Domicile Tracking
User Story: As a user with ties to both UK and SA, I want to input and track my tax residency status, domicile information, and years of residency so that the system can provide accurate tax advice.
Acceptance Criteria:
•	User can input current tax residency (UK, SA, both, neither)
•	User can track domicile status (UK, SA, or non-domiciled)
•	System tracks years of residency in each country
•	UK Statutory Residence Test (SRT) calculator available
•	SA physical presence test calculator available
•	Historical changes tracked with effective dates
•	Deemed domicile status automatically calculated (UK)
•	Remittance basis vs arising basis selection
•	Future domicile projections based on planned residence
Technical Requirements:
•	Complex business logic for SRT calculation
•	Date-based calculations for residency tracking
•	Historical state management (temporal data)
•	Rules engine for deemed domicile determination
•	Integration with Income Tax calculation engine
Constraints:
•	Must support backdating for historical accuracy
•	Cannot delete historical records (audit trail)
•	SRT rules change periodically (versioned rule sets)
•	SA physical presence test: 91 days in current year + 91 days in previous 5 years average
Implementation Approach:
ENDPOINT: POST /api/v1/user/tax-status
REQUEST BODY:
{
  effectiveDate: date,
  ukTaxResident: boolean,
  saTaxResident: boolean,
  domicile: enum['UK_DOMICILED', 'SA_DOMICILED', 'NON_UK_DOMICILED', 'NON_SA_DOMICILED'],
  domicileOfOrigin: enum['UK', 'SA', 'OTHER'],
  ukResidenceBasis: enum['ARISING', 'REMITTANCE'] (if non-UK domiciled),
  yearsInUk: integer,
  yearsInSa: integer,
  notes: text
}

BUSINESS LOGIC:
1. Calculate deemed domicile status:
   UK_DEEMED_DOMICILE = (yearsInUk >= 15 out of last 20 years) OR 
                        (UK domicile of origin AND yearsInUk >= 1 out of last 2 years)

2. Determine applicable tax regimes:
   IF ukTaxResident AND domicile = 'UK_DOMICILED' THEN
     worldwide_income_taxed_in_uk = TRUE
   ELSE IF ukTaxResident AND domicile = 'NON_UK_DOMICILED' AND basis = 'REMITTANCE' THEN
     only_uk_source_and_remitted_income_taxed = TRUE
   
3. Validate residency status:
   IF both UK and SA tax resident THEN
     apply_DTA_tie_breaker_rules()

4. Store with temporal validity
5. Recalculate tax implications across all modules
6. Trigger AI advisory engine to review recommendations

RESPONSE:
{
  id: uuid,
  effectiveDate: date,
  calculatedStatus: {
    ukDeemedDomicile: boolean,
    ukTaxLiability: enum['WORLDWIDE', 'UK_SOURCE_ONLY', 'REMITTANCE_ONLY'],
    saTaxLiability: enum['WORLDWIDE', 'SA_SOURCE_ONLY'],
    dualResident: boolean,
    dtaTieBreakerResult: enum['UK_RESIDENT', 'SA_RESIDENT', 'N/A']
  }
}
User Flow:
[User Information Dashboard] → [Tax Status Section]
     ↓
[Edit Tax Status Button]
     ↓
[Tax Status Form]
  - Effective date selector
  - "Are you UK tax resident?" toggle
  - "Are you SA tax resident?" toggle
  - Domicile status dropdown
  - Domicile of origin dropdown
  - Years in UK input (auto-calculated if dates provided)
  - Years in SA input (auto-calculated if dates provided)
  - If non-UK domiciled: Remittance basis selection
     ↓
[Calculate Button] → [Show calculated status preview]
  - Deemed domicile status
  - Tax liability scope
  - DTA implications
     ↓
[Save] → [Confirmation]
     ↓
[Trigger recalculation across modules]
     ↓
[Show updated recommendations]
API Endpoints:
•	POST /api/v1/user/tax-status - Create/update tax status
•	GET /api/v1/user/tax-status - Get current tax status
•	GET /api/v1/user/tax-status/history - Get historical tax status
•	GET /api/v1/user/tax-status/at-date?date={date} - Get status at specific date
•	POST /api/v1/user/tax-status/srt-calculator - UK SRT calculator
•	POST /api/v1/user/tax-status/sa-presence-test - SA physical presence test
Data Models:
TABLE: user_tax_status
- id: UUID (PK)
- user_id: UUID (FK to users)
- effective_from: DATE NOT NULL
- effective_to: DATE (NULL = current)
- uk_tax_resident: BOOLEAN
- sa_tax_resident: BOOLEAN
- domicile: ENUM('UK_DOMICILED', 'SA_DOMICILED', 'NON_UK_DOMICILED', 'OTHER')
- domicile_of_origin: ENUM('UK', 'SA', 'OTHER')
- uk_residence_basis: ENUM('ARISING', 'REMITTANCE') NULL
- years_in_uk: INTEGER
- years_in_sa: INTEGER
- uk_deemed_domicile: BOOLEAN (calculated)
- dual_resident: BOOLEAN (calculated)
- dta_tie_breaker_result: ENUM('UK_RESIDENT', 'SA_RESIDENT', 'N/A')
- notes: TEXT
- created_at: TIMESTAMP
- created_by: UUID (FK to users)

TABLE: uk_srt_data
- id: UUID (PK)
- user_id: UUID (FK to users)
- tax_year: VARCHAR(7) (e.g., '2024/25')
- days_in_uk: INTEGER
- tie_1_family: BOOLEAN
- tie_2_accommodation: BOOLEAN
- tie_3_work: BOOLEAN
- tie_4_90_days_previous_years: BOOLEAN
- tie_5_more_days_uk_than_other: BOOLEAN
- sufficient_ties_count: INTEGER
- automatic_overseas_test: BOOLEAN
- automatic_uk_test: BOOLEAN
- sufficient_ties_test_result: BOOLEAN
- final_result: ENUM('UK_RESIDENT', 'NON_RESIDENT')
- created_at: TIMESTAMP

TABLE: sa_presence_data
- id: UUID (PK)
- user_id: UUID (FK to users)
- tax_year: VARCHAR(9) (e.g., '2024/2025')
- days_in_sa: INTEGER
- days_in_sa_previous_5_years: JSON (array of {year, days})
- average_days_previous_5_years: DECIMAL
- physically_present_test_result: BOOLEAN
- ordinarily_resident: BOOLEAN
- created_at: TIMESTAMP

INDEX on user_tax_status(user_id, effective_from, effective_to)
INDEX on uk_srt_data(user_id, tax_year)
INDEX on sa_presence_data(user_id, tax_year)
Error Handling:
ERROR CASES:
1. Effective date in future beyond reasonable period
   - Response: 400 Bad Request
   - Message: "Effective date cannot be more than 1 year in the future"
   
2. Overlapping effective periods
   - Response: 409 Conflict
   - Message: "A tax status record already exists for this period"
   - Auto-adjust previous record's effective_to date
   
3. Invalid domicile + residence combination
   - Response: 400 Bad Request
   - Message: "Cannot be UK domiciled and non-UK tax resident for more than 5 years"
   
4. Remittance basis selected but UK domiciled
   - Response: 400 Bad Request
   - Message: "Remittance basis only available for non-UK domiciled individuals"
   
5. Years in UK exceeds age
   - Response: 400 Bad Request
   - Message: "Years of UK residency cannot exceed your age"

EDGE CASES:
- User lived in UK before birth (parents): Allow with warning
- Split year treatment: Create two records for same tax year
- Dual resident with no DTA: Manual tie-breaker input required
- Non-dom claiming remittance basis: Track remittance basis claim fee payment
- Temporary non-residence rules: Flag if left UK and returning within 5 years
- Crown employees: Override SRT rules (special status flag)
Performance Considerations:
•	SRT calculation is complex: Cache results for tax year
•	Historical queries use temporal query optimization
•	Deemed domicile calculation runs on save: <100ms
•	Recalculation triggers: Use async job queue for module updates
•	Expected usage: Multiple updates per user per year
•	Index on effective_from and effective_to for fast temporal queries
 
Feature 2.2: Income Information Management
Feature Name: Multi-Jurisdiction Income Tracking
User Story: As a user with income from multiple sources and countries, I want to record all my income streams with their source country and type so that the system can calculate my tax liability accurately in both jurisdictions.
Acceptance Criteria:
•	User can add multiple income sources
•	Each income has: type, amount, currency, country of source, frequency
•	Support for employment, self-employment, rental, dividend, interest, pension income
•	Foreign income flagged and tracked
•	PAYE/PASE details captured (tax already paid at source)
•	Tax year allocation for income received
•	Gross and net income recording
•	Tax withheld at source tracked
Technical Requirements:
•	Multi-currency support with historical exchange rates
•	Income categorization aligned with UK and SA tax categories
•	Integration with Tax Intelligence Engine
•	Support for grossing up net income
•	Temporal tracking (income changes over time)
Constraints:
•	Must handle both UK tax year (April-April) and SA tax year (March-February)
•	Currency conversion uses HMRC/SARS official rates where applicable
•	Historic income cannot be modified after tax return filed flag set
Implementation Approach:
ENDPOINT: POST /api/v1/user/income
REQUEST BODY:
{
  incomeType: enum['EMPLOYMENT', 'SELF_EMPLOYMENT', 'RENTAL', 'DIVIDEND', 
                   'INTEREST', 'PENSION', 'CAPITAL_GAINS', 'OTHER'],
  sourceCountry: enum['UK', 'SA', 'OTHER'],
  description: string,
  amount: decimal,
  currency: string (ISO 4217),
  frequency: enum['ANNUAL', 'MONTHLY', 'QUARTERLY', 'ONE_OFF'],
  taxYear: string (e.g., 'UK-2024/25' or 'SA-2024/2025'),
  grossIncome: boolean (true if gross, false if net),
  taxWithheldAtSource: decimal (optional),
  payeReference: string (optional, for employment),
  startDate: date,
  endDate: date (optional, NULL = ongoing),
  relatedEntity: string (employer name, rental property, etc.)
}

BUSINESS LOGIC:
1. Validate income type and source country combination
2. Convert to GBP and ZAR using exchange rate for date
3. Determine tax treatment based on:
   - Income type
   - Source country
   - User's tax residency
   - DTA provisions
4. Calculate expected tax liability
5. If net income provided, gross up using applicable tax rate
6. Allocate to correct tax year(s) based on receipt date
7. Store with currency conversion metadata
8. Trigger recalculation of total income for tax purposes

PROCESS:
calculate_tax_treatment(income):
  IF user.uk_tax_resident AND (income.sourceCountry = 'UK' OR user.domicile_basis = 'ARISING'):
    uk_taxable = TRUE
    apply_uk_tax_rates(income.type)
  
  IF user.sa_tax_resident AND (income.sourceCountry = 'SA' OR income.sourceCountry = 'OTHER'):
    sa_taxable = TRUE
    apply_sa_tax_rates(income.type)
  
  IF uk_taxable AND sa_taxable:
    apply_DTA_relief()  // Avoid double taxation
  
  RETURN tax_summary

RESPONSE:
{
  id: uuid,
  incomeDetails: {...},
  taxTreatment: {
    ukTaxable: boolean,
    ukTaxAmount: decimal,
    saTaxable: boolean,
    saTaxAmount: decimal,
    dtaRelief: decimal,
    effectiveTaxRate: decimal
  },
  conversionDetails: {
    gbpAmount: decimal,
    zarAmount: decimal,
    exchangeRate: decimal,
    rateDate: date
  }
}
User Flow:
[User Information Dashboard] → [Income Section]
     ↓
[Add Income Button]
     ↓
[Income Entry Form - Step 1: Type]
  - Select income type (visual cards)
     ↓
[Income Entry Form - Step 2: Details]
  - Source country
  - Description/name
  - Amount and currency
  - Frequency
  - Is this gross or net? toggle
  - Start date (end date if applicable)
     ↓
[Income Entry Form - Step 3: Tax Details]
  - Tax withheld at source (if applicable)
  - PAYE reference (if employment)
  - Related entity details
     ↓
[Preview Calculation]
  - Show UK tax treatment
  - Show SA tax treatment
  - Show DTA relief
  - Total expected tax
     ↓
[Save] → [Confirmation]
     ↓
[Income List View - Updated]
  - Grouped by type
  - Total annual income display
  - Tax liability summary
API Endpoints:
•	POST /api/v1/user/income - Add new income source
•	PUT /api/v1/user/income/{id} - Update income source
•	DELETE /api/v1/user/income/{id} - Delete income source (soft delete)
•	GET /api/v1/user/income - List all income sources
•	GET /api/v1/user/income/summary - Income summary by type and country
•	GET /api/v1/user/income/tax-year/{taxYear} - Income for specific tax year
•	POST /api/v1/user/income/gross-up - Calculate gross from net
Data Models:
TABLE: user_income
- id: UUID (PK)
- user_id: UUID (FK to users)
- income_type: ENUM('EMPLOYMENT', 'SELF_EMPLOYMENT', 'RENTAL', 'DIVIDEND', 
                    'INTEREST', 'PENSION', 'CAPITAL_GAINS', 'OTHER')
- source_country: ENUM('UK', 'SA', 'OTHER')
- description: VARCHAR(255)
- amount: DECIMAL(15,2)
- currency: CHAR(3)
- frequency: ENUM('ANNUAL', 'MONTHLY', 'QUARTERLY', 'ONE_OFF')
- uk_tax_year: VARCHAR(7) (e.g., '2024/25')
- sa_tax_year: VARCHAR(9) (e.g., '2024/2025')
- is_gross: BOOLEAN
- tax_withheld_at_source: DECIMAL(15,2)
- paye_reference: VARCHAR(50)
- start_date: DATE
- end_date: DATE (NULL = ongoing)
- related_entity: VARCHAR(255)
- gbp_amount: DECIMAL(15,2) (calculated)
- zar_amount: DECIMAL(15,2) (calculated)
- exchange_rate_used: DECIMAL(10,6)
- exchange_rate_date: DATE
- deleted: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: income_tax_treatment
- id: UUID (PK)
- income_id: UUID (FK to user_income)
- uk_taxable: BOOLEAN
- uk_tax_estimated: DECIMAL(15,2)
- sa_taxable: BOOLEAN
- sa_tax_estimated: DECIMAL(15,2)
- dta_relief_claimed: DECIMAL(15,2)
- effective_tax_rate: DECIMAL(5,2)
- calculation_date: TIMESTAMP
- tax_status_id: UUID (FK to user_tax_status - for audit)

TABLE: exchange_rates
- id: UUID (PK)
- from_currency: CHAR(3)
- to_currency: CHAR(3)
- rate: DECIMAL(10,6)
- rate_date: DATE
- source: VARCHAR(50) (e.g., 'HMRC', 'SARS', 'ECB')
- created_at: TIMESTAMP

UNIQUE INDEX on exchange_rates(from_currency, to_currency, rate_date)
INDEX on user_income(user_id, uk_tax_year)
INDEX on user_income(user_id, sa_tax_year)
INDEX on user_income(user_id, income_type)
Error Handling:
ERROR CASES:
1. Invalid currency code
   - Response: 400 Bad Request
   - Message: "Invalid currency code. Please use ISO 4217 format (e.g., GBP, ZAR)"
   
2. Exchange rate not available for date
   - Response: 404 Not Found
   - Message: "Exchange rate not available for {date}. Using nearest available rate from {actualDate}"
   - Warning flag set on income record
   
3. Negative income amount
   - Response: 400 Bad Request
   - Message: "Income amount must be positive. Use expenses to record negative amounts"
   
4. End date before start date
   - Response: 400 Bad Request
   - Message: "End date must be after start date"
   
5. Tax withheld exceeds income
   - Response: 400 Bad Request
   - Message: "Tax withheld cannot exceed income amount"
   
6. Attempt to modify locked tax year
   - Response: 423 Locked
   - Message: "Cannot modify income for tax year {year} as tax return has been filed"

EDGE CASES:
- Income received in foreign currency: Store original + converted amounts
- Income spanning multiple tax years (arrears): Allocate based on receipt date
- Bonus payments: Create separate one-off income entry
- Pension splitting for tax: Create separate entries for UK and SA portions
- Grossing up net dividends: Apply correct dividend tax credit rate
- Foreign dividend with withholding tax: Record both gross and net, claim DTA relief
- Self-employment: Separate entry for each source if needed
- Rental income: Net of expenses, link to property records in future
Performance Considerations:
•	Exchange rate lookups: Cache daily rates (1 day TTL)
•	Tax calculation: Cache results per income record
•	Income summary queries: Materialized view for tax year totals
•	Recalculation triggers: Debounce multiple income entries (batch process)
•	Expected usage: 5-20 income sources per user
•	Summary calculation: <500ms for all income sources
•	Indexed queries on tax_year fields for fast filtering
 
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
 
4. PROTECTION MODULE
Feature 4.1: Life Assurance Policy Management
Feature Name: Comprehensive Life Assurance Policy Tracking
User Story: As a user, I want to track all my life assurance policies across UK and SA, including coverage amounts, beneficiaries, and tax implications, so I can ensure my family is adequately protected.
Acceptance Criteria:
•	User can add multiple life assurance policies
•	Each policy includes: provider, policy type, cover amount, premium, term, beneficiaries
•	Support for UK and SA policies with different tax treatments
•	Track if policy written in trust (UK)
•	Track estate duty implications (SA)
•	Coverage gap analysis based on family needs
•	Premium comparison across providers
•	Beneficiary management with percentages
•	Policy renewal reminders
•	Claims process guidance
Technical Requirements:
•	File upload for policy documents (PDF)
•	OCR for policy data extraction (optional enhancement)
•	Beneficiary relationship tracking
•	Premium payment reminder system
•	Integration with IHT module for estate planning
•	Currency support (GBP, ZAR, USD, EUR)
Constraints:
•	Policy documents: Max 10MB per file
•	Beneficiaries: Max 10 per policy
•	Historical policy records retained indefinitely (audit trail)
•	Premium reminders: Email and in-app notification
Implementation Approach:
ENDPOINT: POST /api/v1/protection/life-assurance
REQUEST BODY:
{
  policyNumber: string,
  provider: string,
  providerCountry: enum['UK', 'SA', 'OTHER'],
  policyType: enum['TERM', 'WHOLE_OF_LIFE', 'DECREASING_TERM', 'LEVEL_TERM', 
                   'INCREASING_TERM', 'FAMILY_INCOME_BENEFIT', 'OTHER'],
  coverAmount: decimal,
  currency: string,
  premiumAmount: decimal,
  premiumFrequency: enum['MONTHLY', 'ANNUALLY', 'SINGLE'],
  startDate: date,
  endDate: date (NULL for whole of life),
  writtenInTrust: boolean (UK only),
  trustDetails: {
    trustType: enum['BARE', 'DISCRETIONARY', 'INTEREST_IN_POSSESSION'],
    trustees: array[string],
    beneficiaries: array[{name: string, relationship: string, percentage: decimal}]
  },
  beneficiariesDirectPolicy: array[{
    name: string,
    dateOfBirth: date,
    relationship: enum['SPOUSE', 'CHILD', 'PARENT', 'SIBLING', 'OTHER'],
    percentage: decimal,
    address: string
  }],
  indexationRate: decimal (optional, for increasing policies),
  criticalIllnessRider: boolean,
  waiverOfPremium: boolean,
  notes: text
}

BUSINESS LOGIC:
1. Validate policy data:
   - Sum of beneficiary percentages = 100%
   - Cover amount > 0
   - End date > start date (if applicable)
   - Premium amount reasonable for cover amount

2. Determine tax treatment:
   IF providerCountry = 'UK' AND writtenInTrust = TRUE:
     outside_uk_estate_for_iht = TRUE
   ELSE IF providerCountry = 'UK':
     in_uk_estate_for_iht = TRUE
   
   IF providerCountry = 'SA':
     apply_sa_estate_duty_rules()
     // SA policies generally part of estate

3. Calculate recommended cover (family needs analysis):
   recommended_cover = (annual_income * income_multiplier) +
                      outstanding_debts +
                      (children_count * education_cost_per_child) +
                      funeral_costs -
                      existing_assets
   
   coverage_gap = recommended_cover - total_current_cover

4. Store policy with encrypted document reference

5. Set up premium payment reminders

6. Link to IHT module if not in trust

RESPONSE:
{
  id: uuid,
  policyDetails: {...},
  taxTreatment: {
    ukIhtImpact: boolean,
    saEstateDutyImpact: boolean,
    writtenInTrust: boolean
  },
  coverageAnalysis: {
    currentTotalCover: decimal,
    recommendedCover: decimal,
    coverageGap: decimal,
    gapPercentage: decimal
  },
  annualPremiumCost: decimal
}
User Flow:
[Protection Dashboard] → [Life Assurance Tab]
     ↓
[Add Policy Button]
     ↓
[Policy Entry Form - Step 1: Provider Details]
  - Policy number
  - Provider name (autocomplete with popular providers)
  - Provider country
  - Policy type (visual cards with descriptions)
     ↓
[Policy Entry Form - Step 2: Cover Details]
  - Cover amount and currency
  - Premium amount and frequency
  - Start date and end date (if applicable)
  - Optional riders (CI, waiver)
     ↓
[Policy Entry Form - Step 3: Beneficiaries]
  - Written in trust? (UK policies) → If YES: Trust details
  - Beneficiary list (add multiple)
    - Name, relationship, percentage
    - Validation: percentages total 100%
     ↓
[Policy Entry Form - Step 4: Upload Document]
  - Upload policy document (optional)
  - OCR extraction attempt (if available)
  - Review and confirm extracted data
     ↓
[Coverage Analysis Display]
  - Current total cover
  - Recommended cover (calculated)
  - Gap visualization
  - Recommendation: "Consider increasing cover by £X"
     ↓
[Save Policy]
     ↓
[Policy List View]
  - Card view: Each policy with key details
  - Total cover amount (header)
  - Coverage gap indicator
  - Filter: By provider, type, country
  - Sort: By cover amount, premium, end date
API Endpoints:
•	POST /api/v1/protection/life-assurance - Add policy
•	PUT /api/v1/protection/life-assurance/{id} - Update policy
•	DELETE /api/v1/protection/life-assurance/{id} - Delete policy (soft delete)
•	GET /api/v1/protection/life-assurance - List all policies
•	GET /api/v1/protection/life-assurance/{id} - Get specific policy
•	POST /api/v1/protection/life-assurance/coverage-analysis - Run coverage needs analysis
•	POST /api/v1/protection/life-assurance/{id}/upload-document - Upload policy document
•	GET /api/v1/protection/life-assurance/{id}/document - Download policy document
Data Models:
TABLE: life_assurance_policies
- id: UUID (PK)
- user_id: UUID (FK to users)
- policy_number: VARCHAR(100)
- provider: VARCHAR(255)
- provider_country: ENUM('UK', 'SA', 'OTHER')
- policy_type: ENUM('TERM', 'WHOLE_OF_LIFE', 'DECREASING_TERM', 'LEVEL_TERM', 
                    'INCREASING_TERM', 'FAMILY_INCOME_BENEFIT', 'OTHER')
- cover_amount: DECIMAL(15,2)
- currency: CHAR(3)
- cover_amount_gbp: DECIMAL(15,2) (calculated)
- cover_amount_zar: DECIMAL(15,2) (calculated)
- premium_amount: DECIMAL(10,2)
- premium_frequency: ENUM('MONTHLY', 'ANNUALLY', 'SINGLE')
- annual_premium: DECIMAL(10,2) (calculated)
- start_date: DATE
- end_date: DATE (NULL for whole of life)
- written_in_trust: BOOLEAN DEFAULT FALSE
- trust_type: ENUM('BARE', 'DISCRETIONARY', 'INTEREST_IN_POSSESSION')
- critical_illness_rider: BOOLEAN DEFAULT FALSE
- waiver_of_premium: BOOLEAN DEFAULT FALSE
- indexation_rate: DECIMAL(5,2)
- uk_iht_impact: BOOLEAN (calculated)
- sa_estate_duty_impact: BOOLEAN (calculated)
- document_reference: UUID (FK to documents table)
- status: ENUM('ACTIVE', 'LAPSED', 'CLAIMED', 'MATURED')
- notes: TEXT
- deleted: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: policy_beneficiaries
- id: UUID (PK)
- policy_id: UUID (FK to life_assurance_policies)
- name: VARCHAR(255)
- date_of_birth: DATE
- relationship: ENUM('SPOUSE', 'CHILD', 'PARENT', 'SIBLING', 'OTHER')
- percentage: DECIMAL(5,2)
- address: TEXT
- created_at: TIMESTAMP

TABLE: policy_trustees (for trust policies)
- id: UUID (PK)
- policy_id: UUID (FK to life_assurance_policies)
- name: VARCHAR(255)
- relationship_to_policyholder: VARCHAR(100)
- created_at: TIMESTAMP

TABLE: coverage_needs_analysis
- id: UUID (PK)
- user_id: UUID (FK to users)
- analysis_date: DATE
- annual_income: DECIMAL(15,2)
- income_multiplier: DECIMAL(3,1) (typically 10)
- outstanding_debts: DECIMAL(15,2)
- number_of_children: INTEGER
- education_cost_per_child: DECIMAL(15,2)
- funeral_costs: DECIMAL(10,2)
- existing_liquid_assets: DECIMAL(15,2)
- recommended_cover: DECIMAL(15,2)
- current_total_cover: DECIMAL(15,2)
- coverage_gap: DECIMAL(15,2)
- notes: TEXT
- created_at: TIMESTAMP

TABLE: premium_reminders
- id: UUID (PK)
- policy_id: UUID (FK to life_assurance_policies)
- reminder_date: DATE
- reminder_sent: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP

INDEX on life_assurance_policies(user_id, status)
INDEX on policy_beneficiaries(policy_id)
INDEX on premium_reminders(reminder_date, reminder_sent)
CONSTRAINT: SUM(policy_beneficiaries.percentage WHERE policy_id = X) = 100
Error Handling:
ERROR CASES:
1. Beneficiary percentages don't total 100%
   - Response: 400 Bad Request
   - Message: "Beneficiary percentages must total 100%. Current total: {calculated_total}%"
   
2. Invalid trust setup (trust selected but no trustees)
   - Response: 400 Bad Request
   - Message: "Trust policies must have at least one trustee"
   
3. End date before start date
   - Response: 400 Bad Request
   - Message: "Policy end date must be after start date"
   
4. Duplicate policy number for same provider
   - Response: 409 Conflict
   - Message: "A policy with this number already exists for {provider}"
   - Option to update existing or confirm as separate policy
   
5. Document upload too large
   - Response: 413 Payload Too Large
   - Message: "Document size exceeds 10MB limit. Please compress or split the file"
   
6. Invalid currency code
   - Response: 400 Bad Request
   - Message: "Invalid currency code. Supported: GBP, ZAR, USD, EUR"

EDGE CASES:
- Whole of life policies: No end date (NULL), validation skip
- Single premium policies: Annual premium = premium_amount, frequency = 'SINGLE'
- Multiple beneficiaries with same name: Allow, distinguish by relationship and DOB
- Policy in trust but user not UK resident: Warning (unusual but valid)
- Child beneficiary: Flag for review (may need trust structure)
- Policy matured: Status = 'MATURED', show in separate view
- Policy lapsed: Status = 'LAPSED', keep for reference but exclude from coverage total
- Indexation rate: Apply annually to cover amount (background job)
- Critical illness claim: Reduce life cover by CI payout amount
- Currency fluctuation: Recalculate GBP/ZAR values daily
Performance Considerations:
•	Document storage: Use cloud storage (S3, Azure Blob)
•	OCR processing: Async job (if implemented), may take 30-60 seconds
•	Coverage analysis: Cache results for 30 days (recalculate if significant data change)
•	Currency conversion: Daily batch job for all policies
•	Premium reminders: Daily cron job, send 7 days before due date
•	Expected policies per user: 1-5
•	Policy list query: <500ms
•	Document upload: Progress indicator for files >2MB
•	Beneficiary validation: Client-side + server-side
 
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
 
6. INVESTMENT MODULE
Feature 6.1: Portfolio Management
Feature Name: Comprehensive Investment Portfolio Tracking
User Story: As an investor with holdings across UK and SA markets, I want to track all my investments including stocks, funds, ISAs, and tax-advantaged schemes so that I can monitor performance and manage tax efficiently.
Acceptance Criteria:
•	Track holdings in Stocks & Shares ISA, General Investment Account (GIA), Unit Trusts, ETFs
•	Support for VCTs, EIS, SEIS investments with tax relief tracking
•	SA investments: Unit Trusts, ETFs, JSE-listed stocks
•	Record purchase price, current value, unrealized gains/losses
•	Track dividend income by source country
•	Capital gains tracking (realized and unrealized)
•	Asset allocation analysis
•	Performance metrics vs benchmarks
•	Currency exposure reporting
•	Tax lot tracking (FIFO, average cost methods)
Technical Requirements:
•	Market data integration for pricing (manual or API)
•	Capital gains calculation engine (UK and SA rules)
•	Dividend tax treatment calculation
•	Asset allocation algorithms
•	Performance calculation (time-weighted returns)
•	Corporate action tracking (splits, mergers, dividends)
•	EIS/SEIS/VCT holding period tracking (for tax relief retention)
Constraints:
•	Market data refresh: Real-time for premium, daily for standard
•	Historical price data: 10 years minimum
•	Tax lot tracking: Required for accurate CGT calculation
•	EIS/SEIS minimum holding: 3 years for tax relief retention
•	VCT minimum holding: 5 years for tax relief retention
Implementation Approach:
ENDPOINT: POST /api/v1/investments/holdings
REQUEST BODY:
{
  accountType: enum['STOCKS_ISA', 'GIA', 'UNIT_TRUST', 'VCT', 'EIS', 'SEIS', 
                    'SA_UNIT_TRUST', 'SA_ETF', 'SA_DIRECT_SHARES', 'OFFSHORE_BOND'],
  accountProvider: string,
  accountNumber: string (last 4 digits),
  country: enum['UK', 'SA', 'OFFSHORE'],
  holdings: [
    {
      securityType: enum['STOCK', 'FUND', 'ETF', 'BOND', 'VCT', 'EIS_SHARE', 'SEIS_SHARE'],
      ticker: string,
      name: string,
      quantity: decimal,
      purchaseDate: date,
      purchasePrice: decimal,
      purchaseCurrency: string,
      currentPrice: decimal,
      currentValue: decimal,
      unrealizedGain: decimal,
      assetClass: enum['EQUITY', 'FIXED_INCOME', 'PROPERTY', 'COMMODITY', 'CASH', 'ALTERNATIVE'],
      region: enum['UK', 'US', 'EUROPE', 'ASIA', 'EMERGING', 'GLOBAL'],
      sector: string
    }
  ],
  taxReliefClaimed: {  // For EIS/SEIS/VCT
    reliefType: enum['INCOME_TAX_RELIEF', 'CGT_EXEMPTION', 'CGT_DEFERRAL'],
    reliefAmount: decimal,
    taxYear: string,
    holdingPeriodRequired: integer (years),
    holdingPeriodEndDate: date
  }
}

BUSINESS LOGIC:
1. Validate holding data:
   - Quantity > 0
   - Purchase price >= 0
   - Purchase date <= today
   
2. Calculate metrics:
   unrealized_gain = (current_price - purchase_price) * quantity
   unrealized_gain_percentage = (unrealized_gain / (purchase_price * quantity)) * 100
   
   IF accountType = 'STOCKS_ISA':
     gains_tax_free = TRUE
     dividends_tax_free = TRUE
   ELSE IF accountType = 'GIA':
     apply_uk_cgt_rules()
     apply_uk_dividend_tax_rules()
   
   IF country = 'SA':
     apply_sa_cgt_rules()  // Inclusion rate method
     apply_sa_dividend_tax_rules()  // Dividend withholding tax

3. Track tax lots for CGT:
   // FIFO method for UK
   // Average cost method allowed for SA
   tax_lot = {
     purchase_date: date,
     quantity: decimal,
     cost_basis: decimal,
     disposal_method: 'FIFO' or 'AVERAGE_COST'
   }

4. VCT/EIS/SEIS tracking:
   IF accountType IN ['VCT', 'EIS', 'SEIS']:
     holding_period_remaining = required_period - years_held
     at_risk_of_losing_relief = (holding_period_remaining > 0)
     
     IF at_risk_of_losing_relief:
       CREATE alert("Hold for {remaining} more years to retain tax relief")

5. Asset allocation calculation:
   total_portfolio_value = SUM(all_holdings.current_value)
   
   FOR EACH holding:
     allocation_percentage = (holding.current_value / total_portfolio_value) * 100
   
   GROUP BY asset_class, region, sector

6. Performance calculation:
   time_weighted_return = calculate_twr(cash_flows, valuations)
   vs_benchmark = portfolio_return - benchmark_return

RESPONSE:
{
  id: uuid,
  accountDetails: {...},
  holdings: [...],
  portfolioMetrics: {
    totalValue: {gbp: decimal, zar: decimal},
    totalCost: {gbp: decimal, zar: decimal},
    totalUnrealizedGain: {amount: decimal, percentage: decimal},
    totalRealizedGain: decimal (from previous disposals),
    assetAllocation: [
      {assetClass: string, value: decimal, percentage: decimal},
      ...
    ],
    regionAllocation: [...],
    sectorAllocation: [...],
    currencyExposure: [...]
  },
  taxImplications: {
    isaHoldings: {value: decimal, gains: decimal, taxFree: true},
    giaHoldings: {
      value: decimal,
      unrealizedGains: decimal,
      estimatedCgtLiability: decimal,
      cgtAllowanceUsed: decimal,
      cgtAllowanceRemaining: decimal
    },
    taxReliefAtRisk: [
      {type: string, amount: decimal, holdUntil: date}
    ]
  },
  performance: {
    timeWeightedReturn: decimal,
    moneyWeightedReturn: decimal,
    benchmarkComparison: {
      portfolioReturn: decimal,
      benchmarkReturn: decimal,
      outperformance: decimal
    }
  }
}
User Flow:
[Investment Dashboard] → [Portfolio Overview]
     ↓
[Portfolio Summary Cards]
  - Total Portfolio Value (prominent)
  - Unrealized Gain/Loss (color-coded)
  - Asset Allocation Pie Chart
  - Performance vs Benchmark
     ↓
[Add Investment Account Button]
     ↓
[Account Entry - Step 1: Account Type]
  - Select account type (visual cards):
    - Stocks & Shares ISA
    - General Investment Account
    - VCT/EIS/SEIS
    - SA Unit Trust / ETF
    - Offshore Bond
     ↓
[Account Entry - Step 2: Provider Details]
  - Provider name (autocomplete)
  - Account number (last 4 digits)
  - Country
     ↓
[Account Entry - Step 3: Add Holdings]
  - Manual entry:
    - Search security by ticker/name
    - Enter quantity, purchase price, date
  - Bulk import:
    - Upload CSV file
    - Map columns to fields
    - Validate and import
  - For VCT/EIS/SEIS:
    - Tax relief details
    - Holding period tracker
     ↓
[Holdings List View]
  - Table with sortable columns:
    - Security, Quantity, Cost, Value, Gain/Loss, %
  - Filter: By account, asset class, region
  - Color coding: Gains (green), Losses (red)
     ↓
[Detailed Holding View] (click on any holding)
  - Purchase history (tax lots)
  - Dividend history
  - Corporate actions
  - Performance chart
  - Tax lot tracking
  - CGT calculator (if GIA)
     ↓
[Portfolio Analysis Tab]
  - Asset allocation (multiple views):
    - By asset class
    - By region
    - By sector
    - By currency
  - Diversification score
  - Risk metrics
  - Rebalancing recommendations
API Endpoints:
•	POST /api/v1/investments/accounts - Add investment account
•	PUT /api/v1/investments/accounts/{id} - Update account
•	DELETE /api/v1/investments/accounts/{id} - Delete account (soft delete)
•	POST /api/v1/investments/accounts/{accountId}/holdings - Add holding
•	PUT /api/v1/investments/holdings/{id} - Update holding
•	DELETE /api/v1/investments/holdings/{id} - Delete holding (soft delete)
•	POST /api/v1/investments/holdings/{id}/update-price - Update current price
•	GET /api/v1/investments/portfolio - Get complete portfolio summary
•	GET /api/v1/investments/portfolio/performance - Performance metrics
•	GET /api/v1/investments/portfolio/asset-allocation - Asset allocation breakdown
•	GET /api/v1/investments/cgt-calculator - CGT liability calculator
•	POST /api/v1/investments/holdings/bulk-import - Bulk import holdings
•	GET /api/v1/investments/dividends - Dividend income report
•	GET /api/v1/investments/tax-relief-tracker - VCT/EIS/SEIS tracker
Data Models:
TABLE: investment_accounts
- id: UUID (PK)
- user_id: UUID (FK to users)
- account_type: ENUM('STOCKS_ISA', 'GIA', 'UNIT_TRUST', 'VCT', 'EIS', 'SEIS', 
                     'SA_UNIT_TRUST', 'SA_ETF', 'SA_DIRECT_SHARES', 'OFFSHORE_BOND')
- provider: VARCHAR(255)
- account_number_encrypted: VARCHAR(255)
- country: ENUM('UK', 'SA', 'OFFSHORE')
- base_currency: CHAR(3)
- account_open_date: DATE
- status: ENUM('ACTIVE', 'CLOSED')
- deleted: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: investment_holdings
- id: UUID (PK)
- account_id: UUID (FK to investment_accounts)
- security_type: ENUM('STOCK', 'FUND', 'ETF', 'BOND', 'VCT', 'EIS_SHARE', 'SEIS_SHARE')
- ticker: VARCHAR(20)
- isin: VARCHAR(12)
- security_name: VARCHAR(255)
- quantity: DECIMAL(15,4)
- average_cost_basis: DECIMAL(15,4) (calculated)
- current_price: DECIMAL(15,4)
- price_currency: CHAR(3)
- current_value: DECIMAL(15,2) (calculated)
- unrealized_gain: DECIMAL(15,2) (calculated)
- unrealized_gain_percentage: DECIMAL(10,2) (calculated)
- asset_class: ENUM('EQUITY', 'FIXED_INCOME', 'PROPERTY', 'COMMODITY', 'CASH', 'ALTERNATIVE')
- region: ENUM('UK', 'US', 'EUROPE', 'ASIA', 'EMERGING', 'GLOBAL')
- sector: VARCHAR(100)
- last_price_update: TIMESTAMP
- deleted: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: tax_lots
- id: UUID (PK)
- holding_id: UUID (FK to investment_holdings)
- purchase_date: DATE
- quantity: DECIMAL(15,4)
- purchase_price: DECIMAL(15,4)
- purchase_currency: CHAR(3)
- cost_basis_gbp: DECIMAL(15,2)
- cost_basis_zar: DECIMAL(15,2)
- exchange_rate: DECIMAL(10,6)
- disposal_date: DATE (NULL if not disposed)
- disposal_quantity: DECIMAL(15,4)
- disposal_proceeds: DECIMAL(15,2)
- realized_gain: DECIMAL(15,2) (calculated on disposal)
- cgt_tax_year: VARCHAR(7) (UK) or VARCHAR(9) (SA)
- disposal_method: ENUM('FIFO', 'AVERAGE_COST', 'SPECIFIC_IDENTIFICATION')
- created_at: TIMESTAMP

TABLE: dividends
- id: UUID (PK)
- holding_id: UUID (FK to investment_holdings)
- payment_date: DATE
- ex_dividend_date: DATE
- dividend_per_share: DECIMAL(10,4)
- total_dividend_gross: DECIMAL(10,2)
- withholding_tax: DECIMAL(10,2)
- total_dividend_net: DECIMAL(10,2)
- currency: CHAR(3)
- source_country: ENUM('UK', 'SA', 'US', 'OTHER')
- uk_tax_year: VARCHAR(7)
- sa_tax_year: VARCHAR(9)
- qualified_dividend: BOOLEAN (for US stocks)
- created_at: TIMESTAMP

TABLE: corporate_actions
- id: UUID (PK)
- holding_id: UUID (FK to investment_holdings)
- action_type: ENUM('SPLIT', 'REVERSE_SPLIT', 'MERGER', 'SPINOFF', 'RIGHTS_ISSUE', 
                    'BONUS_ISSUE', 'DELISTING')
- action_date: DATE
- ratio: VARCHAR(20) (e.g., '2:1' for split)
- description: TEXT
- quantity_before: DECIMAL(15,4)
- quantity_after: DECIMAL(15,4)
- cost_basis_adjustment: DECIMAL(15,2)
- created_at: TIMESTAMP

TABLE: tax_relief_schemes
- id: UUID (PK)
- holding_id: UUID (FK to investment_holdings)
- scheme_type: ENUM('VCT', 'EIS', 'SEIS')
- investment_date: DATE
- investment_amount: DECIMAL(15,2)
- income_tax_relief_claimed: DECIMAL(10,2)
- income_tax_relief_percentage: DECIMAL(5,2) (30% EIS, 50% SEIS, 30% VCT)
- tax_year_claimed: VARCHAR(7)
- minimum_holding_period_years: INTEGER (5 for VCT, 3 for EIS/SEIS)
- holding_period_end_date: DATE (calculated)
- cgt_deferral_claimed: DECIMAL(10,2) (EIS only)
- cgt_exemption_eligible: BOOLEAN (EIS/SEIS after holding period)
- relief_withdrawn: BOOLEAN DEFAULT FALSE
- relief_withdrawal_reason: TEXT
- created_at: TIMESTAMP

TABLE: portfolio_snapshots
- id: UUID (PK)
- user_id: UUID (FK to users)
- snapshot_date: DATE
- total_value_gbp: DECIMAL(15,2)
- total_value_zar: DECIMAL(15,2)
- total_cost_basis_gbp: DECIMAL(15,2)
- unrealized_gain_gbp: DECIMAL(15,2)
- realized_gain_ytd_gbp: DECIMAL(15,2)
- asset_allocation_json: JSON
- performance_metrics_json: JSON
- created_at: TIMESTAMP

VIEW: v_portfolio_summary (materialized view, refreshed on demand)
- user_id
- total_portfolio_value_gbp
- total_portfolio_value_zar
- total_unrealized_gain
- total_realized_gain_ytd
- isa_holdings_value
- gia_holdings_value
- vct_eis_seis_value
- estimated_cgt_liability
- last_updated: TIMESTAMP

INDEX on investment_holdings(account_id, deleted)
INDEX on tax_lots(holding_id, disposal_date)
INDEX on dividends(holding_id, payment_date)
INDEX on tax_relief_schemes(holding_id, holding_period_end_date)
INDEX on portfolio_snapshots(user_id, snapshot_date DESC)
Error Handling:
ERROR CASES:
1. Negative quantity or price
   - Response: 400 Bad Request
   - Message: "Quantity and price must be positive values"
   
2. Purchase date in future
   - Response: 400 Bad Request
   - Message: "Purchase date cannot be in the future"
   
3. ISA holding exceeds subscription limits
   - Response: 400 Bad Request
   - Message: "This holding would exceed your ISA subscription limit for {tax_year}"
   
4. VCT/EIS/SEIS disposal before holding period
   - Response: 400 Bad Request (validation warning)
   - Message: "Disposing before {date} will result in loss of £{amount} tax relief"
   - Allow user to confirm and proceed
   
5. Tax lot disposal quantity exceeds available
   - Response: 400 Bad Request
   - Message: "Cannot dispose {quantity} shares. Only {available} shares available from this tax lot"
   
6. Invalid ticker symbol
   - Response: 404 Not Found
   - Message: "Unable to find security with ticker {ticker}. Please verify or enter manually"
   
7. Currency mismatch
   - Response: 400 Bad Request
   - Message: "Security {name} trades in {currency}, but you entered {entered_currency}"
   
8. Duplicate holding in same account
   - Response: 409 Conflict (warning)
   - Message: "You already have a holding of {security} in this account. Merge or add as separate lot?"

EDGE CASES:
- Stock split: Adjust all tax lots proportionally, maintain cost basis
- Reverse split: Consolidate shares, maintain cost basis
- Merger/acquisition: Create new holdings for acquirer, close acquired
- Spinoff: Allocate cost basis between parent and spun-off entity
- Rights issue: New tax lot at subscription price
- Bonus issue: Additional shares, zero cost basis, adjust average cost
- Bed and ISA: Dispose from GIA (CGT event), purchase in ISA (new tax lot)
- Same-day rule (UK CGT): Disposals matched with acquisitions on same day first
- 30-day rule (UK CGT): Disposals matched with acquisitions within 30 days (prevent bed and breakfasting)
- Section 104 holding (UK): Pooled holding with average cost
- Dividend reinvestment: New tax lot at reinvestment price
- Foreign dividends with withholding tax: Claim DTA relief
- Accumulation funds: No dividend distribution, increases share price
- Offshore bonds: Complex tax treatment (top-slicing relief)
- EIS loss relief: Can claim against income tax if EIS shares sold at loss
- VCT dividend: Tax-free regardless of investor's tax band
- Fractional shares: Support decimal quantities for ETFs/funds
- Currency hedged funds: Track hedge separately from underlying
Performance Considerations:
•	Price updates: Batch process, cache for 15 minutes (real-time)
•	Portfolio calculation: Materialized view, refresh on material changes
•	CGT calculation: Complex, cache per holding, recalculate on disposal
•	Asset allocation: Pre-calculate, store in snapshot
•	Performance metrics: Time-intensive, calculate daily (background job)
•	Expected holdings per user: 10-100
•	Portfolio summary: Target <1 second response
•	Historical performance: Pre-aggregate monthly/quarterly
•	Dividend income report: Index on payment_date
•	Tax lot queries: Optimize FIFO lookups with proper indexing
•	Bulk import: Process asynchronously, max 1000 holdings per import
•	Market data API: Rate limiting, caching, fallback to manual updates
 

7. RETIREMENT MODULE
Feature 7.1: UK Pension Management
Feature Name: Comprehensive UK Pension Tracking and Planning
User Story: As a UK pension saver, I want to track all my pension schemes including workplace pensions, personal pensions, SIPPs, and state pension entitlement so that I can plan for retirement and optimize my contributions.
Acceptance Criteria:
•	Track multiple UK pension schemes (Occupational DB/DC, Personal Pensions, SIPP)
•	Record contributions (employee, employer, personal)
•	Track pension pot values (current and projected)
•	Annual Allowance tracking and carry forward
•	Lifetime Allowance tracking (historical and current rules)
•	State Pension forecast integration
•	Pension Commencement Lump Sum (PCLS) projection
•	Retirement income modeling
•	Tax relief tracking (net pay vs relief at source)
•	Pension freedom options analysis (drawdown vs annuity)
Technical Requirements:
•	Defined Benefit (DB) pension valuation
•	Defined Contribution (DC) projection modeling
•	Annual Allowance calculator with taper for high earners
•	Lifetime Allowance calculator (noting 2023 changes)
•	State Pension API integration (HMRC Gateway - future)
•	Retirement income tax calculator
•	Inflation adjustment for projections
•	Investment return modeling (Monte Carlo optional)
Constraints:
•	Annual Allowance (2024/25): £60,000
•	Money Purchase Annual Allowance (MPAA): £10,000 (if triggered)
•	Tapered Annual Allowance: Reduced for adjusted income >£260,000
•	Lifetime Allowance: Abolished April 2024, but lump sum limits apply
•	Lump Sum Allowance: £268,275
•	Lump Sum and Death Benefit Allowance: £1,073,100
•	State Pension Age: Dynamic based on DOB
•	Minimum pension access age: 55 (rising to 57 in 2028)
Implementation Approach:
ENDPOINT: POST /api/v1/retirement/uk-pensions
REQUEST BODY:
{
  pensionType: enum['OCCUPATIONAL_DB', 'OCCUPATIONAL_DC', 'PERSONAL_PENSION', 
                    'SIPP', 'STAKEHOLDER', 'GROUP_PERSONAL_PENSION'],
  provider: string,
  schemeReference: string,
  employerName: string (for occupational),
  
  // For Defined Contribution
  currentValue: decimal,
  contributionDetails: {
    employeeContribution: {
      amount: decimal,
      frequency: enum['MONTHLY', 'ANNUALLY'],
      type: enum['PERCENTAGE_SALARY', 'FIXED_AMOUNT']
    },
    employerContribution: {
      amount: decimal,
      frequency: enum['MONTHLY', 'ANNUALLY'],
      type: enum['PERCENTAGE_SALARY', 'FIXED_AMOUNT']
    },
    personalContribution: {
      amount: decimal,
      frequency: enum['MONTHLY', 'ANNUALLY']
    },
    taxReliefMethod: enum['NET_PAY', 'RELIEF_AT_SOURCE']
  },
  
  // For Defined Benefit
  definedBenefitDetails: {
    accrualRate: decimal (e.g., 1/60, 1/80),
    pensionableService: decimal (years),
    finalSalary: decimal (or CARE: career average),
    schemeType: enum['FINAL_SALARY', 'CAREER_AVERAGE', 'CASH_BALANCE'],
    normalRetirementAge: integer,
    guaranteedPension: decimal (annual amount at NRA),
    spousePension: decimal (percentage, e.g., 50%),
    lumpSumEntitlement: decimal (if applicable),
    indexation: enum['CPI', 'RPI', 'FIXED_PERCENTAGE', 'NONE']
  },
  
  startDate: date,
  expectedRetirementDate: date,
  investmentStrategy: enum['CONSERVATIVE', 'BALANCED', 'AGGRESSIVE', 'CUSTOM'],
  assumedGrowthRate: decimal (annual percentage),
  assumedInflationRate: decimal,
  
  mpaaTriggered: boolean (money purchase annual allowance),
  mpaaDate: date (when triggered)
}

BUSINESS LOGIC:
1. Validate pension data:
   - Current value >= 0
   - Contributions >= 0
   - Expected retirement date > today
   - For DB: Validate accrual rate and service years

2. Calculate Annual Allowance usage:
   total_annual_contribution = employee_contribution + employer_contribution + 
                               personal_contribution + tax_relief
   
   IF mpaaTriggered:
     annual_allowance = 10000  // MPAA
   ELSE:
     base_allowance = 60000
     
     // Taper for high earners
     IF adjusted_income > 260000:
       reduction = MIN((adjusted_income - 260000) / 2, 56000)
       annual_allowance = MAX(base_allowance - reduction, 10000)
     ELSE:
       annual_allowance = base_allowance
   
   allowance_used = total_annual_contribution
   allowance_remaining = annual_allowance - allowance_used
   
   // Carry forward unused allowance (previous 3 years)
   carry_forward_available = calculate_carry_forward()

3. Calculate Lifetime Allowance impact (for pre-2024 protections):
   // Post-April 2024: No LTA charge, but lump sum limits apply
   
   lump_sum_allowance = 268275  // 25% of old LTA
   lump_sum_death_benefit_allowance = 1073100
   
   projected_pension_value = calculate_projection()
   available_tax_free_cash = MIN(projected_pension_value * 0.25, lump_sum_allowance)

4. Project future pension pot (DC):
   FOR year IN range(current_year, retirement_year):
     annual_contribution = calculate_contributions(year)
     investment_return = pot_value * growth_rate
     pot_value = pot_value + annual_contribution + investment_return
   
   projected_pot_at_retirement = pot_value

5. Calculate DB pension value:
   // For Annual Allowance purposes
   pension_input_amount = (pension_accrued_this_year * 16) + 
                          (lump_sum_accrued_this_year)
   
   // Current value for net worth
   transfer_value_equivalent = request_from_scheme_or_estimate()

6. Retirement income projection:
   // Drawdown scenario
   sustainable_withdrawal = projected_pot * safe_withdrawal_rate  // e.g., 4%
   
   // Annuity scenario (estimate)
   annuity_rate = get_current_annuity_rates(age, health_status)
   annuity_income = projected_pot * annuity_rate
   
   // DB pension income
   db_annual_income = pensionable_service * accrual_rate * final_salary

7. Tax relief calculation:
   IF tax_relief_method = 'NET_PAY':
     tax_relief = contribution * user.marginal_tax_rate
   ELSE IF tax_relief_method = 'RELIEF_AT_SOURCE':
     basic_rate_relief = contribution * 0.20  // Automatic
     higher_rate_relief = contribution * (user.marginal_tax_rate - 0.20)  // Claim via tax return

8. State Pension integration:
   state_pension_amount = fetch_or_estimate_state_pension()
   state_pension_age = calculate_spa(user.date_of_birth)

RESPONSE:
{
  id: uuid,
  pensionDetails: {...},
  currentStatus: {
    currentValue: decimal (DC) or transferValue: decimal (DB),
    totalContributions: decimal,
    investmentReturns: decimal
  },
  annualAllowance: {
    taxYear: string,
    allowance: decimal,
    used: decimal,
    remaining: decimal,
    carryForwardAvailable: decimal,
    mpaaApplies: boolean
  },
  projection: {
    projectedValueAtRetirement: decimal,
    retirementAge: integer,
    yearsToRetirement: integer,
    assumptions: {
      growthRate: decimal,
      inflationRate: decimal,
      contributions: string
    }
  },
  retirementIncome: {
    taxFreeCash: decimal,
    annuityOption: {
      estimatedAnnualIncome: decimal,
      assumptions: string
    },
    drawdownOption: {
      sustainableAnnualIncome: decimal,
      withdrawalRate: decimal
    },
    dbPensionIncome: decimal (if applicable)
  },
  taxImplications: {
    taxReliefReceived: decimal,
    taxOnRetirementIncome: decimal (estimated),
    lumpSumAllowanceUsed: decimal,
    lumpSumAllowanceRemaining: decimal
  },
  recommendations: [
    {message: string, estimatedBenefit: decimal}
  ]
}
User Flow:
[Retirement Dashboard] → [UK Pensions Tab]
     ↓
[Pension Summary]
  - Total pension pot value (all schemes combined)
  - Projected retirement income
  - Annual Allowance usage this year
  - Years to retirement countdown
     ↓
[Add Pension Button]
     ↓
[Pension Entry - Step 1: Type]
  - Select pension type (visual cards):
    - Workplace Pension (DB or DC)
    - Personal Pension / SIPP
    - State Pension (tracked separately)
     ↓
[Pension Entry - Step 2: Provider & Scheme]
  - Provider name
  - Scheme reference
  - Employer (if workplace)
  - Start date
     ↓
[Pension Entry - Step 3: Contributions] (DC)
  - Current pot value
  - Your contribution (£ or %)
  - Employer contribution (£ or %)
  - Personal contributions
  - Tax relief method
     ↓
[Pension Entry - Step 3: Benefit Details] (DB)
  - Accrual rate
  - Pensionable service
  - Final/Career average salary
  - Normal retirement age
  - Guaranteed annual pension
     ↓
[Pension Entry - Step 4: Projections]
  - Expected retirement age
  - Investment strategy (DC)
  - Assumed growth rate
  - Inflation assumption
     ↓
[Projection Display]
  - Pot value at retirement
  - Tax-free cash available
  - Income options
  - Visual timeline chart
     ↓
[Annual Allowance Check]
  - This year's usage
  - Carry forward available
  - Warnings if exceeding
     ↓
[Save Pension]
     ↓
[Pension List View]
  - Card view: Each pension with key details
  - Total retirement income projection
  - Filter: By type, employer
  - Sort: By value, contribution
     ↓
[State Pension Section]
  - NI record summary
  - Forecast amount
  - State Pension Age
  - Voluntary contribution calculator
API Endpoints:
•	POST /api/v1/retirement/uk-pensions - Add pension
•	PUT /api/v1/retirement/uk-pensions/{id} - Update pension
•	DELETE /api/v1/retirement/uk-pensions/{id} - Delete pension (soft delete)
•	GET /api/v1/retirement/uk-pensions - List all pensions
•	GET /api/v1/retirement/uk-pensions/{id} - Get specific pension
•	POST /api/v1/retirement/uk-pensions/{id}/update-value - Update pot value
•	GET /api/v1/retirement/annual-allowance - Annual Allowance summary
•	POST /api/v1/retirement/annual-allowance/calculate - Calculate AA with carry forward
•	GET /api/v1/retirement/projection - Combined retirement projection
•	POST /api/v1/retirement/retirement-income-calculator - Model retirement income
•	GET /api/v1/retirement/state-pension - State Pension details
•	POST /api/v1/retirement/state-pension/voluntary-contributions - Calculate voluntary NI
Data Models:
TABLE: uk_pensions
- id: UUID (PK)
- user_id: UUID (FK to users)
- pension_type: ENUM('OCCUPATIONAL_DB', 'OCCUPATIONAL_DC', 'PERSONAL_PENSION', 
                     'SIPP', 'STAKEHOLDER', 'GROUP_PERSONAL_PENSION')
- provider: VARCHAR(255)
- scheme_reference: VARCHAR(100)
- employer_name: VARCHAR(255)
- start_date: DATE
- expected_retirement_date: DATE
- normal_retirement_age: INTEGER
- status: ENUM('ACTIVE', 'DEFERRED', 'IN_PAYMENT', 'TRANSFERRED_OUT')
- mpaa_triggered: BOOLEAN DEFAULT FALSE
- mpaa_trigger_date: DATE
- deleted: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: dc_pension_details
- pension_id: UUID (PK, FK to uk_pensions)
- current_value: DECIMAL(15,2)
- employee_contribution_amount: DECIMAL(10,2)
- employee_contribution_frequency: ENUM('MONTHLY', 'ANNUALLY')
- employee_contribution_type: ENUM('PERCENTAGE_SALARY', 'FIXED_AMOUNT')
- employee_contribution_percentage: DECIMAL(5,2)
- employer_contribution_amount: DECIMAL(10,2)
- employer_contribution_frequency: ENUM('MONTHLY', 'ANNUALLY')
- employer_contribution_type: ENUM('PERCENTAGE_SALARY', 'FIXED_AMOUNT')
- employer_contribution_percentage: DECIMAL(5,2)
- personal_contribution_amount: DECIMAL(10,2)
- personal_contribution_frequency: ENUM('MONTHLY', 'ANNUALLY')
- tax_relief_method: ENUM('NET_PAY', 'RELIEF_AT_SOURCE')
- investment_strategy: ENUM('CONSERVATIVE', 'BALANCED', 'AGGRESSIVE', 'CUSTOM')
- assumed_growth_rate: DECIMAL(5,2)
- assumed_inflation_rate: DECIMAL(5,2)
- last_value_update: DATE
- updated_at: TIMESTAMP

TABLE: db_pension_details
- pension_id: UUID (PK, FK to uk_pensions)
- accrual_rate: VARCHAR(10) (e.g., '1/60', '1/80')
- pensionable_service_years: DECIMAL(5,2)
- scheme_type: ENUM('FINAL_SALARY', 'CAREER_AVERAGE', 'CASH_BALANCE')
- final_salary: DECIMAL(10,2) (or career average)
- guaranteed_annual_pension: DECIMAL(10,2)
- spouse_pension_percentage: DECIMAL(5,2)
- lump_sum_entitlement: DECIMAL(10,2)
- indexation_type: ENUM('CPI', 'RPI', 'FIXED_PERCENTAGE', 'NONE')
- indexation_rate: DECIMAL(5,2) (if fixed)
- transfer_value_equivalent: DECIMAL(15,2) (CETV)
- cetv_date: DATE
- updated_at: TIMESTAMP

TABLE: pension_value_history
- id: UUID (PK)
- pension_id: UUID (FK to uk_pensions)
- value_date: DATE
- pension_value: DECIMAL(15,2)
- contributions_this_period: DECIMAL(10,2)
- investment_return: DECIMAL(10,2)
- value_source: ENUM('MANUAL', 'PROVIDER_STATEMENT', 'PROVIDER_API')
- created_at: TIMESTAMP

TABLE: annual_allowance_tracking
- id: UUID (PK)
- user_id: UUID (FK to users)
- tax_year: VARCHAR(7)
- annual_allowance: DECIMAL(10,2) (60000 or tapered)
- total_contributions: DECIMAL(10,2)
- allowance_used: DECIMAL(10,2)
- allowance_remaining: DECIMAL(10,2)
- carry_forward_year_1: DECIMAL(10,2) (previous year unused)
- carry_forward_year_2: DECIMAL(10,2)
- carry_forward_year_3: DECIMAL(10,2)
- total_carry_forward_available: DECIMAL(10,2)
- excess_contributions: DECIMAL(10,2) (if over limit)
- annual_allowance_charge: DECIMAL(10,2)
- adjusted_income: DECIMAL(15,2) (for taper calculation)
- threshold_income: DECIMAL(15,2) (for taper calculation)
- mpaa_applies: BOOLEAN
- created_at: TIMESTAMP

TABLE: pension_contributions
- id: UUID (PK)
- pension_id: UUID (FK to uk_pensions)
- contribution_date: DATE
- employee_contribution: DECIMAL(10,2)
- employer_contribution: DECIMAL(10,2)
- personal_contribution: DECIMAL(10,2)
- tax_relief_received: DECIMAL(10,2)
- total_contribution: DECIMAL(10,2)
- tax_year: VARCHAR(7)
- created_at: TIMESTAMP

TABLE: state_pension
- user_id: UUID (PK, FK to users)
- ni_number: VARCHAR(13) ENCRYPTED
- qualifying_years: INTEGER
- years_needed_for_full_pension: INTEGER (typically 35)
- forecast_weekly_amount: DECIMAL(10,2)
- forecast_annual_amount: DECIMAL(10,2)
- state_pension_age: INTEGER
- state_pension_date: DATE (calculated)
- gaps_in_record: INTEGER
- voluntary_contribution_cost: DECIMAL(10,2) (to fill gaps)
- last_updated: DATE
- data_source: ENUM('HMRC_API', 'MANUAL', 'ESTIMATED')

TABLE: retirement_projections
- id: UUID (PK)
- user_id: UUID (FK to users)
- projection_date: DATE
- retirement_age: INTEGER
- total_pension_pot_dc: DECIMAL(15,2)
- total_db_annual_income: DECIMAL(15,2)
- state_pension_annual: DECIMAL(15,2)
- tax_free_lump_sum: DECIMAL(15,2)
- annuity_income_estimate: DECIMAL(15,2)
- drawdown_income_estimate: DECIMAL(15,2)
- total_retirement_income: DECIMAL(15,2)
- income_after_tax: DECIMAL(15,2)
- assumptions_json: JSON
- created_at: TIMESTAMP

INDEX on uk_pensions(user_id, status)
INDEX on pension_value_history(pension_id, value_date DESC)
INDEX on annual_allowance_tracking(user_id, tax_year)
INDEX on pension_contributions(pension_id, tax_year)
Error Handling:
ERROR CASES:
1. Contributions exceed Annual Allowance
   - Response: 400 Bad Request (warning)
   - Message: "Your contributions of £{amount} exceed your Annual Allowance of £{allowance}"
   - Details: "This may result in an Annual Allowance charge of £{charge}"
   - Allow user to proceed with acknowledgment
   
2. MPAA triggered but high contributions entered
   - Response: 400 Bad Request
   - Message: "Money Purchase Annual Allowance (£10,000) applies. Your contributions of £{amount} exceed this"
   
3. Retirement age below minimum (55, soon 57)
   - Response: 400 Bad Request
   - Message: "Minimum pension access age is {age}. You've entered {entered_age}"
   
4. DB accrual rate invalid
   - Response: 400 Bad Request
   - Message: "Accrual rate must be in format like '1/60' or '1/80'"
   
5. Negative pension value
   - Response: 400 Bad Request
   - Message: "Pension value cannot be negative"
   
6. Transfer value date too old (>3 months for DB)
   - Response: 400 Bad Request (warning)
   - Message: "CETV dated {date} is more than 3 months old. Consider requesting updated valuation"
   
7. State Pension forecast: insufficient NI years
   - Response: 200 OK with warning
   - Message: "You have {years} qualifying years. You need {required} for full State Pension"
   - Recommendation: "Consider voluntary NI contributions (cost: £{amount})"

EDGE CASES:
- Multiple pensions from same employer: Allow, track separately
- Pension transfer in: Create new pension, close old one, link transfer
- Pension transfer out: Mark status as 'TRANSFERRED_OUT', retain history
- DB to DC transfer: Complex, requires CETV and conversion
- Pension recycling rules: If take TFC and reinvest, may trigger MPAA
- Protected pension age (e.g., 50 for police): Override minimum age check
- LTA protection (Fixed Protection, Individual Protection): Track protection type
- Small pots rule: Can take 3 pensions under £10k without triggering MPAA
- Trivial commutation: Full pension as lump sum if total < £30k
- Flexible drawdown: Track if taking income (triggers MPAA for other pensions)
- Death before retirement: Nominee drawdown or lump sum (usually tax-free if under 75)
- Scheme Pays: Employer pays AA charge, reduces pension
- Salary sacrifice: Reduces net pay, increases employer contribution
- Auto-enrolment: Minimum contributions (8% total: 3% employer, 5% employee)
- Career Average Revalued Earnings (CARE): Annual accrual revalued by inflation
- Pension commencement: Options at 75 (no BCE, but rules change)
Performance Considerations:
•	Projection calculations: Complex, cache for 24 hours
•	Annual Allowance calc: Pre-calculate at each contribution, cache current tax year
•	State Pension API: Rate limited, cache for 30 days
•	Pension value updates: Manual or via provider API (daily batch)
•	Expected pensions per user: 2-8
•	Projection query: Target <1 second
•	Retirement income calculator: Multiple scenarios, may take 2-3 seconds
•	Historical value tracking: Index on date for trend queries
•	Carry forward calculation: Requires 3 previous tax years, pre-aggregate
•	DB pension valuation: Complex actuarial calc, use cached CETV
 
Feature 7.2: SA Retirement Fund Management
Feature Name: South African Retirement and Preservation Fund Tracking
User Story: As a South African resident or someone with SA retirement funds, I want to track my pension funds, provident funds, retirement annuities, and preservation funds so I can plan for retirement and manage my contributions.
Acceptance Criteria:
•	Track Pension Funds, Provident Funds, Retirement Annuities (RA)
•	Track Preservation Funds (pension and provident)
•	Record contributions and employer contributions
•	Section 10C tax deduction tracking (27.5% of income, max R350,000)
•	Fund value and investment choice tracking
•	Retirement age options (55+ for most funds)
•	One-third lump sum option tracking
•	Two-thirds annuity requirement (pension funds)
•	Full cash withdrawal option (provident funds, with limits)
•	Regulation 28 compliance monitoring
•	Withdrawal rules and penalties
Technical Requirements:
•	SA tax calculation for retirement contributions
•	Section 10C deduction calculator
•	Lump sum tax tables (2024: R550,000 tax-free, then progressive)
•	Annuity income tax calculation
•	Regulation 28 compliance checker (max 75% equity, max 30% offshore)
•	Integration with SA income tax module
Constraints:
•	Section 10C deduction: 27.5% of remuneration or taxable income, capped at R350,000 per tax year
•	Retirement age: Typically 55 minimum
•	Pension fund: Min 2/3 to annuity, max 1/3 lump sum
•	Provident fund: Full withdrawal option (subject to limits for recent contributions)
•	Preservation fund: One withdrawal allowed before retirement
•	Tax-free lump sum (2024): R550,000 (first R550k tax-free, then tiered rates)
Implementation Approach:
ENDPOINT: POST /api/v1/retirement/sa-retirement-funds
REQUEST BODY:
{
  fundType: enum['PENSION_FUND', 'PROVIDENT_FUND', 'RETIREMENT_ANNUITY', 
                 'PRESERVATION_FUND_PENSION', 'PRESERVATION_FUND_PROVIDENT'],
  provider: string,
  fundName: string,
  employerName: string (for pension/provident),
  memberNumber: string,
  
  currentValue: decimal,
  currency: string (typically ZAR),
  
  contributionDetails: {
    employeeContribution: {
      amount: decimal,
      frequency: enum['MONTHLY', 'ANNUALLY'],
      percentage: decimal (if percentage of salary)
    },
    employerContribution: {
      amount: decimal,
      frequency: enum['MONTHLY', 'ANNUALLY']
    }
  },
  
  investmentChoice: {
    portfolioName: string,
    assetAllocation: {
      equityPercentage: decimal,
      bondsPercentage: decimal,
      cashPercentage: decimal,
      propertyPercentage: decimal,
      offshorePercentage: decimal
    },
    regulation28Compliant: boolean
  },
  
  startDate: date,
  expectedRetirementAge: integer,
  normalRetirementAge: integer (fund specific),
  
  // For preservation funds
  preservationFundSource: enum['PENSION_FUND', 'PROVIDENT_FUND'],
  transferDate: date,
  withdrawalTaken: boolean,
  withdrawalDate: date,
  withdrawalAmount: decimal,
  
  // For provident funds (new rules)
  contributionsBeforeMarch2021: decimal,
  contributionsAfterMarch2021: decimal
}

BUSINESS LOGIC:
1. Validate fund data:
   - Current value >= 0
   - Retirement age >= 55 (typically)
   - Contributions >= 0

2. Calculate Section 10C tax deduction:
   annual_contribution = employee_contribution * frequency_multiplier
   
   // 27.5% of the greater of remuneration or taxable income
   max_deductible = MIN(user.annual_income * 0.275, 350000)
   
   deduction_claimed = MIN(annual_contribution, max_deductible)
   tax_saving = deduction_claimed * user.marginal_tax_rate

3. Check Regulation 28 compliance:
   IF fundType IN ['PENSION_FUND', 'PROVIDENT_FUND', 'RETIREMENT_ANNUITY']:
     reg28_equity_limit = 75
     reg28_offshore_limit = 30
     reg28_property_limit = 25
     
     IF equity_percentage > reg28_equity_limit:
       non_compliant = TRUE
       violation = "Equity allocation exceeds 75%"
     
     IF offshore_percentage > reg28_offshore_limit:
       non_compliant = TRUE
       violation = "Offshore allocation exceeds 30%"

4. Calculate retirement options:
   // Pension Fund and RA
   IF fundType IN ['PENSION_FUND', 'RETIREMENT_ANNUITY']:
     max_lump_sum = fund_value * (1/3)
     min_annuity = fund_value * (2/3)
     
     // Unless fund value < R247,500 (trivial amount)
     IF fund_value < 247500:
       can_take_full_cash = TRUE
   
   // Provident Fund (complex post-2021 rules)
   IF fundType = 'PROVIDENT_FUND':
     // Contributions before 1 March 2021: Full cash withdrawal
     // Contributions after 1 March 2021: Subject to 1/3 rule
     
     cash_portion = contributionsBeforeMarch2021 + 
                   (contributionsAfterMarch2021 * (1/3))
     annuity_portion = contributionsAfterMarch2021 * (2/3)

5. Calculate lump sum tax (SA 2024 tax tables):
   tax_free_portion = 550000  // First R550k tax-free
   
   IF lump_sum <= tax_free_portion:
     tax = 0
   ELSE:
     taxable_amount = lump_sum - tax_free_portion
     
     // Progressive rates
     IF taxable_amount <= 200000:
       tax = taxable_amount * 0.18
     ELSE IF taxable_amount <= 350000:
       tax = 36000 + (taxable_amount - 200000) * 0.27
     ELSE IF taxable_amount <= 700000:
       tax = 76500 + (taxable_amount - 350000) * 0.36
     ELSE:
       tax = 202500 + (taxable_amount - 700000) * 0.45

6. Project fund value at retirement:
   years_to_retirement = retirement_age - current_age
   annual_contribution = calculate_annual_contributions()
   assumed_growth_rate = 0.08  // 8% default
   
   projected_value = calculate_future_value(
     current_value,
     annual_contribution,
     assumed_growth_rate,
     years_to_retirement
   )

7. Calculate retirement income:
   // Annuity options (life annuity vs living annuity)
   life_annuity_rate = get_annuity_rates(age, gender)  // Typically 8-12% at 65
   life_annuity_income = annuity_portion * life_annuity_rate
   
   living_annuity_withdrawal_min = 2.5  // 2.5% minimum
   living_annuity_withdrawal_max = 17.5  // 17.5% maximum
   living_annuity_income_range = {
     min: annuity_portion * 0.025,
     max: annuity_portion * 0.175
   }

RESPONSE:
{
  id: uuid,
  fundDetails: {...},
  currentStatus: {
    currentValue: decimal,
    currentValueZAR: decimal,
    totalContributions: decimal,
    investmentReturns: decimal
  },
  taxDeduction: {
    taxYear: string,
    annualContribution: decimal,
    maxDeductible: decimal,
    deductionClaimed: decimal,
    taxSaving: decimal,
    remainingAllowance: decimal
  },
  regulation28: {
    compliant: boolean,
    violations: [string],
    currentAllocation: {...},
    limits: {...}
  },
  projection: {
    projectedValueAtRetirement: decimal,
    retirementAge: integer,
    yearsToRetirement: integer,
    assumptions: {
      growthRate: decimal,
      contributions: string
    }
  },
  retirementOptions: {
    lumpSumOption: {
      maxLumpSum: decimal,
      estimatedTax: decimal,
      netLumpSum: decimal
    },
    annuityRequirement: {
      minAnnuityAmount: decimal,
      canTakeFullCash: boolean (if trivial)
    },
    incomeProjection: {
      lifeAnnuity: {
        estimatedMonthlyIncome: decimal,
        assumptions: string
      },
      livingAnnuity: {
        minMonthlyIncome: decimal,
        maxMonthlyIncome: decimal,
        recommendedRate: decimal
      }
    }
  }
}
User Flow:
[Retirement Dashboard] → [SA Retirement Funds Tab]
     ↓
[Fund Summary]
  - Total retirement savings (all SA funds)
  - Section 10C deduction used this year
  - Projected retirement income
  - Regulation 28 compliance status
     ↓
[Add Fund Button]
     ↓
[Fund Entry - Step 1: Type]
  - Select fund type (visual cards):
    - Pension Fund
    - Provident Fund
    - Retirement Annuity (RA)
    - Preservation Fund
     ↓
[Fund Entry - Step 2: Provider & Details]
  - Provider name
  - Fund name
  - Member number
  - Employer (if applicable)
  - Start date
     ↓
[Fund Entry - Step 3: Value & Contributions]
  - Current fund value
  - Your contribution (R or %)
  - Employer contribution
  - Contribution frequency
     ↓
[Fund Entry - Step 4: Investment Choice]
  - Portfolio name
  - Asset allocation sliders:
    - Equity %
    - Bonds %
    - Cash %
    - Property %
    - Offshore %
  - Regulation 28 compliance checker (real-time)
     ↓
[Fund Entry - Step 5: Retirement Planning]
  - Expected retirement age
  - Growth rate assumption
     ↓
[Tax Deduction Preview]
  - Annual contribution total
  - Section 10C deduction
  - Tax saving estimate
  - Remaining deduction allowance
     ↓
[Projection Display]
  - Fund value at retirement
  - Lump sum options
  - Annuity income options
     ↓
[Save Fund]
     ↓
[Fund List View]
  - Card view: Each fund with key details
  - Total Section 10C deduction tracker
  - Regulation 28 compliance indicators
  - Filter: By type, employer
  - Sort: By value, contribution
API Endpoints:
•	POST /api/v1/retirement/sa-retirement-funds - Add fund
•	PUT /api/v1/retirement/sa-retirement-funds/{id} - Update fund
•	DELETE /api/v1/retirement/sa-retirement-funds/{id} - Delete fund (soft delete)
•	GET /api/v1/retirement/sa-retirement-funds - List all funds
•	GET /api/v1/retirement/sa-retirement-funds/{id} - Get specific fund
•	POST /api/v1/retirement/sa-retirement-funds/{id}/update-value - Update value
•	GET /api/v1/retirement/sa-section-10c - Section 10C deduction summary
•	POST /api/v1/retirement/sa-lump-sum-tax-calculator - Calculate lump sum tax
•	POST /api/v1/retirement/sa-regulation-28-checker - Check Reg 28 compliance
•	GET /api/v1/retirement/sa-retirement-income-calculator - Model retirement income
Data Models:
TABLE: sa_retirement_funds
- id: UUID (PK)
- user_id: UUID (FK to users)
- fund_type: ENUM('PENSION_FUND', 'PROVIDENT_FUND', 'RETIREMENT_ANNUITY', 
                  'PRESERVATION_FUND_PENSION', 'PRESERVATION_FUND_PROVIDENT')
- provider: VARCHAR(255)
- fund_name: VARCHAR(255)
- employer_name: VARCHAR(255)
- member_number_encrypted: VARCHAR(255)
- current_value: DECIMAL(15,2)
- currency: CHAR(3) DEFAULT 'ZAR'
- start_date: DATE
- expected_retirement_age: INTEGER
- normal_retirement_age: INTEGER
- status: ENUM('ACTIVE', 'PRESERVED', 'PAID_OUT', 'TRANSFERRED')
- deleted: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: sa_fund_contributions
- fund_id: UUID (PK, FK to sa_retirement_funds)
- employee_contribution_amount: DECIMAL(10,2)
- employee_contribution_frequency: ENUM('MONTHLY', 'ANNUALLY')
- employee_contribution_percentage: DECIMAL(5,2)
- employer_contribution_amount: DECIMAL(10,2)
- employer_contribution_frequency: ENUM('MONTHLY', 'ANNUALLY')
- contributions_before_march_2021: DECIMAL(15,2) (for provident funds)
- contributions_after_march_2021: DECIMAL(15,2) (for provident funds)
- updated_at: TIMESTAMP

TABLE: sa_fund_investment_choice
- fund_id: UUID (PK, FK to sa_retirement_funds)
- portfolio_name: VARCHAR(255)
- equity_percentage: DECIMAL(5,2)
- bonds_percentage: DECIMAL(5,2)
- cash_percentage: DECIMAL(5,2)
- property_percentage: DECIMAL(5,2)
- offshore_percentage: DECIMAL(5,2)
- regulation_28_compliant: BOOLEAN
- last_rebalance_date: DATE
- updated_at: TIMESTAMP

TABLE: sa_preservation_fund_details
- fund_id: UUID (PK, FK to sa_retirement_funds)
- source_fund_type: ENUM('PENSION_FUND', 'PROVIDENT_FUND')
- transfer_date: DATE
- transfer_value: DECIMAL(15,2)
- withdrawal_allowed: BOOLEAN DEFAULT TRUE
- withdrawal_taken: BOOLEAN DEFAULT FALSE
- withdrawal_date: DATE
- withdrawal_amount: DECIMAL(15,2)
- updated_at: TIMESTAMP

TABLE: sa_section_10c_tracking
- id: UUID (PK)
- user_id: UUID (FK to users)
- tax_year: VARCHAR(9) (e.g., '2024/2025')
- total_contributions: DECIMAL(15,2)
- remuneration: DECIMAL(15,2)
- taxable_income: DECIMAL(15,2)
- max_deductible: DECIMAL(15,2)
- deduction_claimed: DECIMAL(15,2)
- tax_saving: DECIMAL(15,2)
- created_at: TIMESTAMP

TABLE: sa_fund_value_history
- id: UUID (PK)
- fund_id: UUID (FK to sa_retirement_funds)
- value_date: DATE
- fund_value: DECIMAL(15,2)
- contributions_this_period: DECIMAL(10,2)
- investment_return: DECIMAL(10,2)
- created_at: TIMESTAMP

TABLE: sa_retirement_projections
- id: UUID (PK)
- user_id: UUID (FK to users)
- projection_date: DATE
- retirement_age: INTEGER
- total_fund_value: DECIMAL(15,2)
- lump_sum_option: DECIMAL(15,2)
- lump_sum_tax: DECIMAL(15,2)
- annuity_portion: DECIMAL(15,2)
- life_annuity_income: DECIMAL(15,2)
- living_annuity_income_min: DECIMAL(15,2)
- living_annuity_income_max: DECIMAL(15,2)
- assumptions_json: JSON
- created_at: TIMESTAMP

INDEX on sa_retirement_funds(user_id, status)
INDEX on sa_section_10c_tracking(user_id, tax_year)
INDEX on sa_fund_value_history(fund_id, value_date DESC)
Error Handling:
ERROR CASES:
1. Contributions exceed Section 10C limit
   - Response: 400 Bad Request (warning)
   - Message: "Your contributions of R{amount} exceed the deductible limit"
   - Details: "Max deductible: R{max}. Excess: R{excess} (no tax benefit)"
   
2. Regulation 28 violation
   - Response: 400 Bad Request (warning)
   - Message: "Asset allocation violates Regulation 28"
   - Details: "Equity: {equity}% (max 75%), Offshore: {offshore}% (max 30%)"
   - Allow user to save with acknowledgment
   
3. Preservation fund second withdrawal attempt
   - Response: 400 Bad Request
   - Message: "Only one withdrawal allowed from preservation funds before retirement"
   - Details: "Previous withdrawal: R{amount} on {date}"
   
4. Retirement age below minimum
   - Response: 400 Bad Request
   - Message: "Minimum retirement age for {fund_type} is 55"
   
5. Negative fund value
   - Response: 400 Bad Request
   - Message: "Fund value cannot be negative"
   
6. Asset allocation doesn't total 100%
   - Response: 400 Bad Request
   - Message: "Asset allocation must total 100%. Current total: {total}%"

EDGE CASES:
- Provident fund to preservation fund: Track original contributions split (pre/post March 2021)
- Multiple employers: Multiple pension funds, track separately
- Fund switch within RA: Update investment choice, no tax event
- Emigration (financial): Tax implications on withdrawal (complex)
- Retrenchment/resignation: Options to preserve or withdraw
- Early retirement (50-55): May be allowed by fund rules, penalties may apply
- Disability retirement: May have different tax treatment
- Death before retirement: Lump sum to beneficiaries (usually tax-free)
- Divorce: Pension interest awarded to ex-spouse (no tax if clean break)
- Retirement reform: Provident fund rules changed March 2021
- Living annuity: Can change income drawdown rate annually
- Guaranteed life annuity: Fixed income for life, no flexibility
- With-profit annuity: Potential for income increases
- Living annuity depletion: Risk of running out if withdrawal rate too high
- Offshore pension to SA: Tax implications, may need SARS approval
Performance Considerations:
•	Section 10C calculation: Pre-calculate for current tax year, cache
•	Regulation 28 checking: Real-time validation, simple calculation
•	Lump sum tax calculation: Use lookup table for tax brackets
•	Fund value updates: Manual or via provider statement (monthly/quarterly)
•	Expected funds per user: 1-4
•	Projection query: Target <1 second
•	Retirement income calculator: Multiple scenarios, <2 seconds
•	Historical value tracking: Index on date
•	Asset allocation visualization: Pre-calculate percentages
 
Feature 7.3: QROPS / ROPS Management
Feature Name: Cross-Border Pension Transfer Tracking (QROPS/ROPS)
User Story: As someone who has transferred or is considering transferring a UK pension overseas, I want to track QROPS (Qualifying Recognised Overseas Pension Scheme) or ROPS (Recognised Overseas Pension Scheme in SA) so I can manage cross-border pension arrangements and understand tax implications.
Acceptance Criteria:
•	Track QROPS/ROPS pension schemes
•	Record UK pension transfer details (source scheme, transfer value, date)
•	Track overseas tax charges (25% if not EEA and resident <5 years)
•	Monitor reporting requirements to HMRC
•	Track contributions post-transfer (if allowed)
•	Dual-country tax treatment
•	Currency exposure management
•	Retirement benefit options (based on receiving country rules)
Technical Requirements:
•	UK-SA pension transfer rules engine
•	Overseas Transfer Charge calculator (25% if applicable)
•	HMRC reporting requirement tracker (5 years post-transfer)
•	Exchange rate tracking at transfer date
•	Integration with both UK and SA retirement modules
•	DTA application for pension income
Constraints:
•	Overseas Transfer Charge: 25% if transferring to non-EEA and member not resident in destination country
•	HMRC reporting: Annual reporting required for 5 years post-transfer (until April 2024 rules)
•	SA ROPS: Must be SARS-approved
•	Minimum transfer value: Typically £30,000 (scheme rules)
•	Transfer testing: Protection of benefits
Implementation Approach:
ENDPOINT: POST /api/v1/retirement/qrops-rops
REQUEST BODY:
{
  schemeType: enum['QROPS', 'ROPS', 'OTHER_OVERSEAS_PENSION'],
  destinationCountry: enum['SA', 'OTHER'],
  
  schemeName: string,
  schemeProvider: string,
  qropsReferenceNumber: string,
  schemeAddress: text,
  
  ukSourcePension: {
    ukPensionId: uuid (FK to uk_pensions),
    sourceSchemeName: string,
    sourceProvider: string,
    transferValue: decimal,
    transferDate: date,
    transferCurrency: string,
    exchangeRate: decimal (GBP to destination currency)
  },
  
  overseasTransferCharge: {
    applicable: boolean,
    chargeRate: decimal (typically 25%),
    chargeAmount: decimal,
    reasonForCharge: string,
    paidBy: enum['MEMBER', 'SCHEME']
  },
  
  memberResidency: {
    residencyAtTransfer: enum['UK', 'SA', 'OTHER'],
    taxResidencyAtTransfer: enum['UK', 'SA', 'BOTH'],
    yearsOutOfUk: integer
  },
  
  currentValue: decimal,
  destinationCurrency: string,
  
  reportingRequirements: {
    hmrcReportingRequired: boolean,
    reportingPeriodEnd: date (transfer_date + 10 years),
    lastReportDate: date,
    nextReportDue: date
  },
  
  benefitOptions: {
    retirementAge: integer,
    lumpSumAvailable: boolean,
    lumpSumPercentage: decimal,
    annuityRequired: boolean,
    drawdownAvailable: boolean
  },
  
  notes: text
}

BUSINESS LOGIC:
1. Validate QROPS/ROPS data:
   - Transfer date <= today
   - Transfer value > 0
   - Destination country valid

2. Calculate Overseas Transfer Charge:
   // 25% charge applies if:
   // - Transfer to non-EEA QROPS, AND
   // - Member not tax resident in same country as QROPS for 5 full UK tax years before transfer
   
   IF destinationCountry NOT IN ['EEA_COUNTRIES']:
     IF member_tax_resident_in_destination_country < 5_years:
       overseas_transfer_charge_applicable = TRUE
       charge_amount = transfer_value * 0.25
     ELSE:
       overseas_transfer_charge_applicable = FALSE
   
   // Exception: UK/SA DTA may provide relief
   IF destinationCountry = 'SA' AND uk_sa_dta_applies:
     // Check specific DTA provisions
     may_avoid_charge = TRUE

3. Determine reporting requirements:
   // Pre-April 2024: 10 years of reporting
   // Post-April 2024: 5 years for certain transfers
   
   IF transfer_date < '2024-04-06':
     reporting_period_years = 10
   ELSE:
     reporting_period_years = 5
   
   reporting_end_date = transfer_date + reporting_period_years * 365
   
   // Report required events:
   // - Receiving scheme losing QROPS status
   // - Member becoming UK resident again
   // - Payments made from scheme
   // - Transfers out of scheme

4. Track currency exposure:
   value_in_gbp = current_value / current_exchange_rate
   value_in_zar = current_value * current_zar_gbp_rate
   
   currency_gain_loss = value_in_gbp - (transfer_value / transfer_exchange_rate)

5. Calculate retirement benefits (destination country rules):
   IF destinationCountry = 'SA':
     // SA ROPS follows SA retirement fund rules
     apply_sa_retirement_rules()
     max_lump_sum = calculate_sa_lump_sum()
     annuity_requirement = calculate_sa_annuity_requirement()
   
   ELSE:
     // Other jurisdictions
     apply_destination_country_rules()

6. Tax treatment of pension income:
   // DTA determines which country taxes pension
   // Typically: Country of residence at time of payment
   
   IF member_tax_resident = 'SA':
     sa_tax_applies = TRUE
     apply_sa_pension_tax_rates()
   
   IF member_tax_resident = 'UK':
     uk_tax_applies = TRUE
     apply_uk_pension_tax_rates()
   
   // DTA relief to avoid double taxation
   apply_uk_sa_dta()

7. Integration with UK and SA modules:
   // Link to original UK pension (now transferred out)
   UPDATE uk_pensions 
   SET status = 'TRANSFERRED_OUT', 
       transferred_to_scheme = qrops_id
   WHERE id = ukSourcePension.ukPensionId
   
   // Potentially create SA retirement fund entry if ROPS
   IF destinationCountry = 'SA':
     CREATE sa_retirement_fund_entry()

RESPONSE:
{
  id: uuid,
  schemeDetails: {...},
  transferDetails: {
    ukSourceScheme: string,
    transferValue: {gbp: decimal, destinationCurrency: decimal},
    transferDate: date,
    exchangeRate: decimal
  },
  overseasTransferCharge: {
    applicable: boolean,
    chargeAmount: decimal,
    paidDate: date,
    reason: string
  },
  currentStatus: {
    currentValue: decimal,
    valueGbp: decimal,
    valueZar: decimal,
    currencyGainLoss: decimal
  },
  reportingRequirements: {
    hmrcReportingRequired: boolean,
    nextReportDue: date,
    reportingPeriodEnds: date,
    eventsToReport: [string]
  },
  taxTreatment: {
    currentResidence: string,
    pensionIncomeTaxedIn: enum['UK', 'SA', 'BOTH'],
    dtaRelief: string
  },
  retirementProjection: {
    retirementAge: integer,
    projectedValue: decimal,
    lumpSumOption: decimal,
    annuityRequirement: decimal,
    estimatedIncome: decimal
  }
}
User Flow:
[Retirement Dashboard] → [International Pensions Tab]
     ↓
[QROPS/ROPS Summary]
  - Overseas pension value
  - Reporting status (HMRC)
  - Currency exposure
  - Years until reporting ends
     ↓
[Add QROPS/ROPS Button]
     ↓
[Transfer Entry - Step 1: Destination Scheme]
  - Scheme name and provider
  - Destination country
  - QROPS reference number
  - Scheme address
     ↓
[Transfer Entry - Step 2: UK Source Pension]
  - Select from existing UK pensions OR enter manually
  - Source scheme name
  - Transfer value (GBP)
  - Transfer date
     ↓
[Transfer Entry - Step 3: Transfer Charge]
  - System calculates if charge applies
  - "Were you tax resident in {country} for 5 years before transfer?"
  - If charge applies: Amount, paid date, paid by
     ↓
[Transfer Entry - Step 4: Current Position]
  - Current scheme value
  - Currency
  - Investment choices (if applicable)
     ↓
[Transfer Entry - Step 5: Reporting]
  - HMRC reporting required? (auto-calculated)
  - Reporting period
  - Next report due date
     ↓
[Tax Treatment Display]
  - Current residency
  - Which country will tax pension income
  - DTA provisions
     ↓
[Currency Exposure Analysis]
  - Transfer exchange rate
  - Current exchange rate
  - Currency gain/loss
  - Hedging recommendations
     ↓
[Save QROPS/ROPS]
     ↓
[Scheme Detail View]
  - All scheme details
  - Reporting checklist
  - Currency tracking chart
  - Link to UK source pension (now transferred out)
     ↓
[Reporting Section]
  - Reportable events tracker
  - Submission history
  - Upcoming deadlines
API Endpoints:
•	POST /api/v1/retirement/qrops-rops - Add QROPS/ROPS
•	PUT /api/v1/retirement/qrops-rops/{id} - Update scheme
•	DELETE /api/v1/retirement/qrops-rops/{id} - Delete scheme (soft delete)
•	GET /api/v1/retirement/qrops-rops - List all schemes
•	GET /api/v1/retirement/qrops-rops/{id} - Get specific scheme
•	POST /api/v1/retirement/qrops-rops/{id}/update-value - Update value
•	POST /api/v1/retirement/qrops-rops/transfer-charge-calculator - Calculate OTC
•	POST /api/v1/retirement/qrops-rops/{id}/report-event - Log reportable event
•	GET /api/v1/retirement/qrops-rops/{id}/reporting-checklist - Get reporting status
•	GET /api/v1/retirement/qrops-rops/{id}/currency-exposure - Currency analysis
Data Models:
TABLE: qrops_rops_schemes
- id: UUID (PK)
- user_id: UUID (FK to users)
- scheme_type: ENUM('QROPS', 'ROPS', 'OTHER_OVERSEAS_PENSION')
- destination_country: VARCHAR(100)
- scheme_name: VARCHAR(255)
- scheme_provider: VARCHAR(255)
- qrops_reference_number: VARCHAR(100)
- scheme_address: TEXT
- current_value: DECIMAL(15,2)
- destination_currency: CHAR(3)
- current_value_gbp: DECIMAL(15,2) (calculated)
- current_value_zar: DECIMAL(15,2) (calculated)
- status: ENUM('ACTIVE', 'TRANSFERRED_OUT', 'IN_PAYMENT')
- deleted: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: qrops_transfers
- id: UUID (PK)
- qrops_scheme_id: UUID (FK to qrops_rops_schemes)
- uk_source_pension_id: UUID (FK to uk_pensions, nullable)
- source_scheme_name: VARCHAR(255)
- source_provider: VARCHAR(255)
- transfer_value_gbp: DECIMAL(15,2)
- transfer_value_destination: DECIMAL(15,2)
- transfer_currency: CHAR(3)
- transfer_date: DATE
- exchange_rate_at_transfer: DECIMAL(10,6)
- member_residency_at_transfer: VARCHAR(100)
- member_tax_residency_at_transfer: VARCHAR(100)
- years_out_of_uk: INTEGER
- created_at: TIMESTAMP

TABLE: overseas_transfer_charges
- id: UUID (PK)
- transfer_id: UUID (FK to qrops_transfers)
- charge_applicable: BOOLEAN
- charge_rate: DECIMAL(5,2)
- charge_amount_gbp: DECIMAL(15,2)
- charge_amount_destination: DECIMAL(15,2)
- charge_paid_by: ENUM('MEMBER', 'SCHEME')
- charge_paid_date: DATE
- reason_for_charge: TEXT
- exemption_claimed: BOOLEAN
- exemption_reason: TEXT
- created_at: TIMESTAMP

TABLE: qrops_reporting_requirements
- id: UUID (PK)
- qrops_scheme_id: UUID (FK to qrops_rops_schemes)
- hmrc_reporting_required: BOOLEAN
- reporting_period_years: INTEGER (10 or 5)
- reporting_start_date: DATE
- reporting_end_date: DATE
- last_report_submitted_date: DATE
- next_report_due_date: DATE
- reporting_complete: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: qrops_reportable_events
- id: UUID (PK)
- qrops_scheme_id: UUID (FK to qrops_rops_schemes)
- event_type: ENUM('SCHEME_LOST_QROPS_STATUS', 'MEMBER_BECAME_UK_RESIDENT', 
                   'PAYMENT_MADE', 'TRANSFER_OUT', 'DEATH', 'OTHER')
- event_date: DATE
- event_description: TEXT
- reported_to_hmrc: BOOLEAN DEFAULT FALSE
- report_date: DATE
- hmrc_reference: VARCHAR(100)
- created_at: TIMESTAMP

TABLE: qrops_value_history
- id: UUID (PK)
- qrops_scheme_id: UUID (FK to qrops_rops_schemes)
- value_date: DATE
- scheme_value: DECIMAL(15,2)
- value_currency: CHAR(3)
- exchange_rate_gbp: DECIMAL(10,6)
- exchange_rate_zar: DECIMAL(10,6)
- value_gbp: DECIMAL(15,2) (calculated)
- value_zar: DECIMAL(15,2) (calculated)
- created_at: TIMESTAMP

TABLE: qrops_benefit_options
- qrops_scheme_id: UUID (PK, FK to qrops_rops_schemes)
- retirement_age: INTEGER
- lump_sum_available: BOOLEAN
- lump_sum_percentage: DECIMAL(5,2)
- annuity_required: BOOLEAN
- annuity_percentage: DECIMAL(5,2)
- drawdown_available: BOOLEAN
- death_benefits: TEXT
- updated_at: TIMESTAMP

INDEX on qrops_rops_schemes(user_id, status)
INDEX on qrops_transfers(qrops_scheme_id)
INDEX on qrops_reporting_requirements(next_report_due_date)
INDEX on qrops_reportable_events(qrops_scheme_id, event_date)
INDEX on qrops_value_history(qrops_scheme_id, value_date DESC)
Error Handling:
ERROR CASES:
1. Transfer date in future
   - Response: 400 Bad Request
   - Message: "Transfer date cannot be in the future"
   
2. Invalid QROPS reference number format
   - Response: 400 Bad Request
   - Message: "QROPS reference number must be in format: QROPS######"
   
3. Transfer value below minimum
   - Response: 400 Bad Request (warning)
   - Message: "Transfer value {value} is below typical minimum of £30,000. Please verify"
   
4. Overseas transfer charge not paid when applicable
   - Response: 400 Bad Request
   - Message: "Overseas Transfer Charge of £{amount} was applicable but not recorded as paid"
   
5. HMRC report overdue
   - Response: 200 OK with alert
   - Alert: "HMRC report was due on {date}. Submit report immediately to avoid penalties"
   
6. Scheme lost QROPS status
   - Response: 400 Bad Request (critical)
   - Message: "This scheme is no longer a registered QROPS. Tax charges may apply"
   - Action: "Report to HMRC immediately"

EDGE CASES:
- Multiple transfers to same QROPS: Track each separately
- Transfer from QROPS to another QROPS: Another reportable event, may trigger new charges
- Member returns to UK within 5 years: May trigger Overseas Transfer Charge retrospectively
- QROPS becomes ROPS: SA-based schemes after Brexit
- Death while in QROPS: Death benefits subject to destination country rules, report to HMRC
- Taking benefits before UK minimum pension age (55/57): May trigger UK tax charge
- Unapproved payments from QROPS: Unauthorized payments, report to HMRC, tax charge
- Currency hedging within scheme: Track separately, affects value
- Protected pension age: May lose protection on transfer
- Enhanced protection / Fixed protection: May lose on transfer
- Transfer to non-QROPS: Not allowed without severe tax consequences
- EEA transfers (pre-Brexit): No OTC, but still reporting requirements
- Gibraltar QROPS: Special rules, still part of HMRC QROPS list
Performance Considerations:
•	Exchange rate updates: Daily batch job for currency conversions
•	QROPS status verification: Weekly check against HMRC QROPS list (API or manual)
•	Reporting deadline calculations: Pre-calculate, set reminders 30/60/90 days before
•	Transfer charge calculation: Complex, cache result with transfer
•	Expected schemes per user: 0-2 (relatively uncommon)
•	Value tracking: Manual updates or annual statements
•	Currency exposure analysis: Calculate on demand, cache for 24 hours
•	Integration with UK pensions: Link source pension, mark as transferred out
 

8. INHERITANCE TAX PLANNING MODULE
Feature 8.1: Assets Register
Feature Name: Comprehensive Multi-Jurisdiction Asset Tracking for Estate Planning
User Story: As a user with assets in UK and SA, I want to maintain a complete register of all my assets including their location, ownership structure, and value so that I can plan my estate and understand potential inheritance tax/estate duty liabilities.
Acceptance Criteria:
•	Track all assets by type (property, investments, cash, business interests, personal possessions)
•	Record asset location (UK-situs, SA-situs, offshore)
•	Track ownership structure (sole, joint, trust, company)
•	Support for excluded property (non-UK domiciled assets)
•	Valuation tracking with historical updates
•	Asset categorization for IHT/Estate Duty purposes
•	Integration with other modules (investments, savings, property)
•	Document attachment for valuations and ownership proof
•	Beneficiary designation where applicable
Technical Requirements:
•	Complex ownership structure modeling
•	Situs determination rules engine
•	Excluded property calculator
•	Asset valuation history tracking
•	Integration with Investment and Savings modules
•	Document management system
•	Multi-currency support with conversion
Constraints:
•	UK IHT: Applies to UK-situs assets regardless of domicile
•	UK IHT: Applies to worldwide assets if UK domiciled/deemed domiciled
•	SA Estate Duty: Applies based on residency and asset location
•	Excluded property rules: Complex, based on domicile and asset type
•	Valuation date: Date of death (or alternate valuation date)
•	Joint ownership: Determines how assets pass (joint tenants vs tenants in common)
Implementation Approach:
ENDPOINT: POST /api/v1/iht/assets
REQUEST BODY:
{
  assetType: enum['PROPERTY', 'INVESTMENT', 'CASH', 'BUSINESS_INTEREST', 
                  'LIFE_POLICY', 'PENSION', 'PERSONAL_POSSESSION', 'OTHER'],
  assetCategory: enum['RESIDENTIAL_PROPERTY', 'COMMERCIAL_PROPERTY', 'LAND',
                      'QUOTED_SHARES', 'UNQUOTED_SHARES', 'UNIT_TRUSTS',
                      'BANK_ACCOUNT', 'ISA', 'SIPP', 'ARTWORK', 'JEWELRY',
                      'VEHICLE', 'INTELLECTUAL_PROPERTY', 'OTHER'],
  
  description: string,
  location: enum['UK', 'SA', 'OFFSHORE', 'OTHER'],
  situs: enum['UK_SITUS', 'SA_SITUS', 'NON_UK_NON_SA_SITUS', 'MOVEABLE'],
  
  valuation: {
    currentValue: decimal,
    currency: string,
    valuationDate: date,
    valuationMethod: enum['MARKET_VALUE', 'PROBATE_VALUE', 'PROFESSIONAL_VALUATION', 
                          'COST_BASIS', 'ESTIMATED'],
    valuationSource: string (e.g., professional valuer name)
  },
  
  ownership: {
    ownershipType: enum['SOLE', 'JOINT_TENANTS', 'TENANTS_IN_COMMON', 
                        'TRUST', 'COMPANY', 'PARTNERSHIP'],
    ownershipPercentage: decimal (if not 100%),
    jointOwners: [
      {
        name: string,
        relationship: string,
        percentage: decimal
      }
    ],
    trustDetails: {
      trustName: string,
      trustType: enum['BARE', 'DISCRETIONARY', 'INTEREST_IN_POSSESSION', 'OTHER'],
      settlor: string,
      beneficiaries: [string]
    },
    companyDetails: {
      companyName: string,
      registrationNumber: string,
      jurisdiction: string,
      ownershipPercentage: decimal
    }
  },
  
  acquisition: {
    acquisitionDate: date,
    acquisitionCost: decimal,
    acquisitionMethod: enum['PURCHASE', 'INHERITANCE', 'GIFT', 'TRANSFER']
  },
  
  taxation: {
    ukIhtApplicable: boolean,
    saEstateDutyApplicable: boolean,
    excludedProperty: boolean,
    excludedPropertyReason: string,
    businessPropertyRelief: boolean,
    bprPercentage: decimal (50% or 100%),
    agriculturalPropertyRelief: boolean,
    aprPercentage: decimal (50% or 100%)
  },
  
  mortgageDebt: {
    hasMortgage: boolean,
    outstandingBalance: decimal,
    lender: string,
    linkedLiabilityId: uuid (FK to liabilities)
  },
  
  beneficiaryDesignation: {
    hasBeneficiaries: boolean,
    beneficiaries: [
      {
        name: string,
        relationship: string,
        percentage: decimal
      }
    ],
    passesByWill: boolean
  },
  
  notes: text,
  documentReferences: [uuid]  // FKs to document storage
}

BUSINESS LOGIC:
1. Validate asset data:
   - Current value >= 0 (can be 0 for depreciated assets)
   - Ownership percentages total 100% (if joint ownership)
   - Acquisition date <= today
   - Valuation date <= today or reasonable projection

2. Determine situs (location for tax purposes):
   // UK situs assets
   IF assetCategory IN ['RESIDENTIAL_PROPERTY', 'COMMERCIAL_PROPERTY', 'LAND'] AND location = 'UK':
     situs = 'UK_SITUS'
   
   IF assetCategory IN ['QUOTED_SHARES'] AND company_registered_uk = TRUE:
     situs = 'UK_SITUS'
   
   IF assetCategory IN ['BANK_ACCOUNT', 'CASH'] AND bank_branch_uk = TRUE:
     situs = 'UK_SITUS'
   
   // SA situs assets
   IF location = 'SA' AND assetCategory IN ['PROPERTY', 'LAND']:
     situs = 'SA_SITUS'
   
   // Moveable property (jewelry, artwork, vehicles)
   IF assetCategory IN ['JEWELRY', 'ARTWORK', 'VEHICLE']:
     situs = 'MOVEABLE'  // Situs = location of owner at death

3. Determine IHT applicability:
   user_domicile = get_user_domicile()
   
   // UK IHT applies if:
   IF user_domicile IN ['UK_DOMICILED', 'UK_DEEMED_DOMICILED']:
     uk_iht_applicable = TRUE  // Worldwide assets
   ELSE IF situs = 'UK_SITUS':
     uk_iht_applicable = TRUE  // UK assets even if non-dom
   ELSE:
     uk_iht_applicable = FALSE
   
   // Check for excluded property
   IF user_domicile = 'NON_UK_DOMICILED' AND situs != 'UK_SITUS':
     excluded_property = TRUE
     uk_iht_applicable = FALSE

4. Determine SA Estate Duty applicability:
   // SA Estate Duty applies to:
   // - Worldwide assets of SA residents
   // - SA-situs assets of non-residents
   
   IF user.sa_resident:
     sa_estate_duty_applicable = TRUE  // Worldwide
   ELSE IF situs = 'SA_SITUS':
     sa_estate_duty_applicable = TRUE
   ELSE:
     sa_estate_duty_applicable = FALSE

5. Calculate reliefs (UK):
   // Business Property Relief (BPR)
   IF assetCategory = 'UNQUOTED_SHARES' AND held_for >= 2_years:
     bpr_available = TRUE
     bpr_percentage = 100  // 100% relief
   
   IF assetCategory = 'BUSINESS_INTEREST' AND held_for >= 2_years:
     bpr_available = TRUE
     bpr_percentage = 100  // 100% relief for sole trader/partnership
   
   IF assetCategory = 'QUOTED_SHARES' AND company_qualifies:
     bpr_available = TRUE
     bpr_percentage = 50  // 50% relief for controlling shareholding
   
   // Agricultural Property Relief (APR)
   IF assetCategory = 'LAND' AND agricultural_use AND ownership_or_occupation_criteria_met:
     apr_available = TRUE
     apr_percentage = 100 or 50  // Depends on occupation

6. Calculate net asset value:
   gross_value = current_value * (ownership_percentage / 100)
   
   IF hasMortgage:
     net_value = gross_value - outstanding_mortgage_balance
   ELSE:
     net_value = gross_value
   
   IF bpr_available:
     relievable_value = net_value * (bpr_percentage / 100)
     taxable_value = net_value - relievable_value
   ELSE:
     taxable_value = net_value

7. Integration with other modules:
   // Link to existing investment holdings
   IF assetType = 'INVESTMENT':
     linked_investment_id = find_matching_investment()
     sync_valuation_with_investment_module()
   
   // Link to savings accounts
   IF assetType = 'CASH':
     linked_savings_account_id = find_matching_account()
     sync_valuation_with_savings_module()
   
   // Link to protection policies
   IF assetType = 'LIFE_POLICY':
     linked_policy_id = find_matching_policy()
     check_if_written_in_trust()

8. Currency conversion:
   value_gbp = convert_to_gbp(current_value, currency, valuation_date)
   value_zar = convert_to_zar(current_value, currency, valuation_date)

RESPONSE:
{
  id: uuid,
  assetDetails: {...},
  valuation: {
    currentValue: decimal,
    currency: string,
    valueGbp: decimal,
    valueZar: decimal,
    lastValuationDate: date
  },
  ownership: {
    type: string,
    userPercentage: decimal,
    jointOwners: [...],
    netValueToUser: decimal
  },
  taxation: {
    situs: string,
    ukIhtApplicable: boolean,
    saEstateDutyApplicable: boolean,
    excludedProperty: boolean,
    reliefs: {
      bpr: {available: boolean, percentage: decimal, relievedAmount: decimal},
      apr: {available: boolean, percentage: decimal, relievedAmount: decimal}
    },
    taxableValue: {
      uk: decimal,
      sa: decimal
    }
  },
  linkedAssets: {
    investmentId: uuid,
    savingsAccountId: uuid,
    policyId: uuid
  },
  netValue: decimal (after mortgages/debts)
}
User Flow:
[IHT Dashboard] → [Assets Register Tab]
     ↓
[Assets Overview]
  - Total estate value (gross and net)
  - Assets by type (pie chart)
  - Assets by location (UK, SA, Offshore)
  - IHT/Estate Duty exposure
     ↓
[Add Asset Button]
     ↓
[Asset Entry - Step 1: Type & Category]
  - Select asset type (visual cards):
    - Property
    - Investments
    - Cash & Bank Accounts
    - Business Interests
    - Life Insurance
    - Personal Possessions
    - Other
  - Select specific category
     ↓
[Asset Entry - Step 2: Location & Description]
  - Asset description/name
  - Physical location
  - Situs (auto-calculated, can override)
     ↓
[Asset Entry - Step 3: Valuation]
  - Current value and currency
  - Valuation date
  - Valuation method
  - Valuation source (if professional)
  - Upload valuation documents
     ↓
[Asset Entry - Step 4: Ownership]
  - Ownership type selection:
    - Sole ownership
    - Joint ownership → Add co-owners with %
    - Trust → Trust details
    - Company → Company details
  - Your ownership percentage
     ↓
[Asset Entry - Step 5: Acquisition]
  - When acquired
  - How acquired (purchase/gift/inheritance)
  - Original cost (if applicable)
     ↓
[Asset Entry - Step 6: Tax Treatment]
  - System calculates IHT applicability
  - System calculates Estate Duty applicability
  - Excluded property? (auto-determined)
  - Eligible for BPR/APR? (if applicable)
  - Mortgage/debt against asset?
     ↓
[Asset Entry - Step 7: Beneficiaries]
  - Passes by will? OR
  - Specific beneficiary designation
  - Beneficiary details and percentages
     ↓
[Tax Treatment Summary]
  - UK IHT impact
  - SA Estate Duty impact
  - Reliefs available
  - Net taxable value
     ↓
[Save Asset]
     ↓
[Assets List View]
  - Table/Card view with filters:
    - Filter by type, location, ownership
    - Sort by value, date acquired
  - Quick actions: Edit, Update valuation, View details
  - Color coding: UK IHT (red), SA Estate Duty (blue), Both (purple)
     ↓
[Asset Detail View]
  - Complete asset information
  - Valuation history chart
  - Ownership structure diagram
  - Tax treatment breakdown
  - Linked liabilities
  - Documents attached
  - Edit/Delete options
API Endpoints:
•	POST /api/v1/iht/assets - Add asset
•	PUT /api/v1/iht/assets/{id} - Update asset
•	DELETE /api/v1/iht/assets/{id} - Delete asset (soft delete)
•	GET /api/v1/iht/assets - List all assets
•	GET /api/v1/iht/assets/{id} - Get specific asset
•	POST /api/v1/iht/assets/{id}/update-valuation - Update valuation
•	GET /api/v1/iht/assets/{id}/valuation-history - Get valuation history
•	GET /api/v1/iht/assets/summary - Assets summary by type/location
•	POST /api/v1/iht/assets/bulk-import - Bulk import assets
•	GET /api/v1/iht/assets/tax-treatment - Tax treatment summary
•	POST /api/v1/iht/assets/{id}/upload-document - Upload document
•	GET /api/v1/iht/assets/{id}/documents - Get asset documents
Data Models:
TABLE: iht_assets
- id: UUID (PK)
- user_id: UUID (FK to users)
- asset_type: ENUM('PROPERTY', 'INVESTMENT', 'CASH', 'BUSINESS_INTEREST', 
                   'LIFE_POLICY', 'PENSION', 'PERSONAL_POSSESSION', 'OTHER')
- asset_category: VARCHAR(100)
- description: VARCHAR(500)
- location: ENUM('UK', 'SA', 'OFFSHORE', 'OTHER')
- situs: ENUM('UK_SITUS', 'SA_SITUS', 'NON_UK_NON_SA_SITUS', 'MOVEABLE')
- current_value: DECIMAL(15,2)
- currency: CHAR(3)
- value_gbp: DECIMAL(15,2) (calculated)
- value_zar: DECIMAL(15,2) (calculated)
- valuation_date: DATE
- valuation_method: VARCHAR(100)
- valuation_source: VARCHAR(255)
- acquisition_date: DATE
- acquisition_cost: DECIMAL(15,2)
- acquisition_method: ENUM('PURCHASE', 'INHERITANCE', 'GIFT', 'TRANSFER')
- deleted: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: asset_ownership
- id: UUID (PK)
- asset_id: UUID (FK to iht_assets)
- ownership_type: ENUM('SOLE', 'JOINT_TENANTS', 'TENANTS_IN_COMMON', 
                       'TRUST', 'COMPANY', 'PARTNERSHIP')
- user_ownership_percentage: DECIMAL(5,2) DEFAULT 100.00
- joint_ownership: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP

TABLE: asset_joint_owners
- id: UUID (PK)
- asset_id: UUID (FK to iht_assets)
- owner_name: VARCHAR(255)
- relationship: VARCHAR(100)
- ownership_percentage: DECIMAL(5,2)
- created_at: TIMESTAMP

TABLE: asset_trust_details
- asset_id: UUID (PK, FK to iht_assets)
- trust_name: VARCHAR(255)
- trust_type: ENUM('BARE', 'DISCRETIONARY', 'INTEREST_IN_POSSESSION', 'OTHER')
- settlor_name: VARCHAR(255)
- trustee_names: JSON (array)
- beneficiary_names: JSON (array)
- trust_deed_reference: UUID (FK to documents)
- created_at: TIMESTAMP

TABLE: asset_company_ownership
- asset_id: UUID (PK, FK to iht_assets)
- company_name: VARCHAR(255)
- company_registration_number: VARCHAR(100)
- jurisdiction: VARCHAR(100)
- user_ownership_percentage: DECIMAL(5,2)
- created_at: TIMESTAMP

TABLE: asset_taxation
- asset_id: UUID (PK, FK to iht_assets)
- uk_iht_applicable: BOOLEAN
- sa_estate_duty_applicable: BOOLEAN
- excluded_property: BOOLEAN
- excluded_property_reason: TEXT
- business_property_relief: BOOLEAN
- bpr_percentage: DECIMAL(5,2)
- bpr_relieved_amount: DECIMAL(15,2)
- agricultural_property_relief: BOOLEAN
- apr_percentage: DECIMAL(5,2)
- apr_relieved_amount: DECIMAL(15,2)
- uk_taxable_value: DECIMAL(15,2)
- sa_taxable_value: DECIMAL(15,2)
- updated_at: TIMESTAMP

TABLE: asset_valuation_history
- id: UUID (PK)
- asset_id: UUID (FK to iht_assets)
- valuation_date: DATE
- value: DECIMAL(15,2)
- currency: CHAR(3)
- value_gbp: DECIMAL(15,2)
- value_zar: DECIMAL(15,2)
- valuation_method: VARCHAR(100)
- valuation_source: VARCHAR(255)
- notes: TEXT
- created_at: TIMESTAMP

TABLE: asset_beneficiary_designation
- id: UUID (PK)
- asset_id: UUID (FK to iht_assets)
- beneficiary_name: VARCHAR(255)
- beneficiary_relationship: VARCHAR(100)
- percentage: DECIMAL(5,2)
- passes_by_will: BOOLEAN DEFAULT TRUE
- created_at: TIMESTAMP

TABLE: asset_documents
- id: UUID (PK)
- asset_id: UUID (FK to iht_assets)
- document_type: ENUM('VALUATION', 'DEED', 'TITLE', 'CERTIFICATE', 'OTHER')
- document_name: VARCHAR(255)
- document_reference: UUID (FK to document_storage)
- upload_date: DATE
- created_at: TIMESTAMP

TABLE: asset_module_links
- asset_id: UUID (PK, FK to iht_assets)
- investment_holding_id: UUID (FK to investment_holdings)
- savings_account_id: UUID (FK to savings_accounts)
- life_policy_id: UUID (FK to life_assurance_policies)
- uk_pension_id: UUID (FK to uk_pensions)
- sa_retirement_fund_id: UUID (FK to sa_retirement_funds)
- sync_enabled: BOOLEAN DEFAULT TRUE
- last_sync: TIMESTAMP

VIEW: v_estate_summary (materialized view, refreshed daily)
- user_id
- total_gross_estate_gbp
- total_gross_estate_zar
- total_net_estate_gbp (after liabilities)
- total_net_estate_zar
- uk_iht_liable_assets_gbp
- sa_estate_duty_liable_assets_zar
- excluded_property_value_gbp
- bpr_relief_total_gbp
- apr_relief_total_gbp
- asset_count
- last_updated: TIMESTAMP

INDEX on iht_assets(user_id, deleted)
INDEX on iht_assets(asset_type, location)
INDEX on asset_ownership(asset_id)
INDEX on asset_valuation_history(asset_id, valuation_date DESC)
INDEX on asset_taxation(asset_id)
CONSTRAINT: SUM(asset_joint_owners.ownership_percentage WHERE asset_id = X) + 
            asset_ownership.user_ownership_percentage = 100
Error Handling:
ERROR CASES:
1. Negative asset value
   - Response: 400 Bad Request
   - Message: "Asset value cannot be negative. Use zero for worthless assets"
   
2. Valuation date in future
   - Response: 400 Bad Request
   - Message: "Valuation date cannot be in the future"
   
3. Ownership percentages don't total 100%
   - Response: 400 Bad Request
   - Message: "Total ownership percentages must equal 100%. Current total: {total}%"
   
4. Acquisition date after valuation date
   - Response: 400 Bad Request
   - Message: "Acquisition date must be before valuation date"
   
5. BPR claimed but holding period < 2 years
   - Response: 400 Bad Request (warning)
   - Message: "Business Property Relief requires 2 years ownership. Current ownership: {years} years"
   - Allow user to save with acknowledgment that relief not yet available
   
6. Asset in trust but trust details missing
   - Response: 400 Bad Request
   - Message: "Please provide trust details for assets held in trust"
   
7. Mortgage exceeds asset value
   - Response: 400 Bad Request (warning)
   - Message: "Mortgage of £{mortgage} exceeds asset value of £{value} (negative equity)"
   - Allow to proceed with warning
   
8. Duplicate asset detection
   - Response: 409 Conflict (warning)
   - Message: "Similar asset already exists: {description}. Continue adding?"

EDGE CASES:
- Joint tenants: Passes automatically to survivor, not by will
- Tenants in common: Passes by will, specify percentage
- Asset partly in UK, partly overseas: Split into separate assets
- Foreign property with UK mortgage: Complex situs rules, both may apply
- Reversionary interest in trust: May not have current value but future entitlement
- Life insurance in trust: Not part of estate if properly structured
- Pension death benefits: Normally discretionary, not estate assets
- Business assets used partly for business: Partial BPR available
- Agricultural land with development potential: May affect APR
- Quoted shares in suspended company: Valuation difficult, may be zero
- Art, antiques, collectibles: Professional valuation recommended
- Intellectual property: Difficult to value, may need specialist
- Cryptocurrency: Valuation at date of death, high volatility
- Foreign currency accounts: Value in GBP/ZAR at death
- Jointly owned property: Severance of joint tenancy affects IHT
- Property owned through company: Shares are the asset, not property
- Overseas property: May have local death taxes in addition to UK IHT
- Excluded property becoming liable: If non-dom becomes deemed domiciled
- BPR/APR withdrawal: If asset changes use before death
- Lifetime gifts with reservation: May still be in estate
Performance Considerations:
•	Asset list with calculations: Use materialized view, refresh daily
•	Valuation history: Paginate if >50 entries per asset
•	Currency conversions: Batch update daily, cache exchange rates
•	Tax treatment calculation: Complex, cache result per asset
•	BPR/APR eligibility: Business rules engine, <100ms execution
•	Expected assets per user: 5-50
•	Estate summary calculation: Pre-aggregate, <500ms response
•	Document uploads: Async processing for large files
•	Bulk import: Process asynchronously, max 100 assets per import
•	Integration sync: Daily batch job to sync with other modules
•	Search and filter: Full-text search on description, indexed queries
 
Feature 8.2: Liabilities Register
Feature Name: Comprehensive Debt and Liability Tracking for Estate Calculation
User Story: As a user planning my estate, I want to record all my liabilities including mortgages, loans, credit cards, and other debts so that my net estate value is accurately calculated for inheritance tax purposes.
Acceptance Criteria:
•	Track all liabilities (mortgages, personal loans, credit cards, business debts)
•	Record liability details (creditor, amount, interest rate, repayment terms)
•	Link liabilities to specific assets (e.g., mortgage to property)
•	Deductibility determination for IHT/Estate Duty
•	Track payment history and outstanding balance
•	Project future liability reduction
•	Alert for liabilities that may not be deductible
•	Support for joint liabilities
Technical Requirements:
•	Liability amortization calculator
•	Deductibility rules engine (UK and SA)
•	Asset-liability linking
•	Payment tracking system
•	Interest calculation
•	Future projection modeling
Constraints:
•	UK IHT: Liabilities deductible if legally owed at death
•	UK IHT: Liabilities to "connected persons" may be restricted
•	UK IHT: Foreign liabilities only deductible against foreign assets (non-doms)
•	SA Estate Duty: Similar deductibility rules
•	Double deduction: Cannot deduct same liability in both jurisdictions
•	Contingent liabilities: May or may not be deductible
Implementation Approach:
ENDPOINT: POST /api/v1/iht/liabilities
REQUEST BODY:
{
  liabilityType: enum['MORTGAGE', 'PERSONAL_LOAN', 'CREDIT_CARD', 'BUSINESS_LOAN', 
                      'OVERDRAFT', 'TAX_LIABILITY', 'LEGAL_OBLIGATION', 'GUARANTEE', 'OTHER'],
  
  description: string,
  creditor: string,
  accountReference: string,
  
  financial: {
    outstandingBalance: decimal,
    currency: string,
    originalAmount: decimal,
    interestRate: decimal (annual percentage),
    startDate: date,
    endDate: date (for term loans),
    repaymentFrequency: enum['MONTHLY', 'QUARTERLY', 'ANNUALLY', 'BULLET', 'REVOLVING'],
    monthlyPayment: decimal (if applicable)
  },
  
  linkedAsset: {
    isSecured: boolean,
    linkedAssetId: uuid (FK to iht_assets),
    securityType: enum['MORTGAGE', 'CHARGE', 'PLEDGE', 'UNSECURED']
  },
  
  ownership: {
    jointLiability: boolean,
    userPercentage: decimal,
    jointDebtors: [
      {
        name: string,
        relationship: string,
        percentage: decimal
      }
    ]
  },
  
  deductibility: {
    ukIhtDeductible: boolean,
    ukIhtDeductibleReason: text,
    ukIhtDeductibleAmount: decimal,
    saEstateDutyDeductible: boolean,
    saEstateDutyDeductibleReason: text,
    saEstateDutyDeductibleAmount: decimal,
    connectedPerson: boolean,
    connectedPersonDetails: string
  },
  
  status: enum['ACTIVE', 'PAID_OFF', 'DEFAULTED', 'DISPUTED'],
  notes: text
}

BUSINESS LOGIC:
1. Validate liability data:
   - Outstanding balance >= 0
   - Interest rate reasonable (0-30%)
   - Start date <= today
   - End date > start date (if applicable)
   - If joint: percentages total 100%

2. Calculate user's share:
   user_liability_share = outstanding_balance * (user_percentage / 100)

3. Determine deductibility for UK IHT:
   // General rule: Deductible if legally owed
   deductible = TRUE
   
   // Restrictions:
   IF creditor_is_connected_person:
     // May be restricted or disallowed
     deductible = FALSE or RESTRICTED
     reason = "Liability to connected person - may not be deductible"
   
   IF user.domicile = 'NON_UK_DOMICILED' AND liability_location = 'OVERSEAS':
     // Can only deduct against overseas assets, not UK assets
     deduction_limited_to_overseas_assets = TRUE
   
   IF liability_type = 'GUARANTEE' AND not_yet_called:
     deductible = FALSE
     reason = "Contingent liability - only deductible if called upon"
   
   IF liability_incurred_to_acquire_excluded_property:
     // May not be deductible for UK IHT
     deductible = FALSE
     reason = "Liability to acquire excluded property"
   
   // Calculate deductible amount
   IF deductible:
     uk_iht_deductible_amount = user_liability_share
   ELSE:
     uk_iht_deductible_amount = 0

4. Determine deductibility for SA Estate Duty:
   // Similar principles to UK
   sa_deductible = TRUE
   
   IF liability_to_connected_person:
     sa_deductible = RESTRICTED
   
   IF contingent_liability:
     sa_deductible = FALSE
   
   sa_estate_duty_deductible_amount = calculate_sa_deduction()

5. Link to asset (if secured):
   IF isSecured AND linkedAssetId:
     asset = get_asset(linkedAssetId)
     
     // Check if liability exceeds asset value
     IF user_liability_share > asset.net_value:
       alert = "Liability exceeds asset value (negative equity)"
     
     // Update asset with linked liability
     UPDATE iht_assets 
     SET linked_liability_id = liability_id,
         net_value = asset_value - liability
     WHERE id = linkedAssetId

6. Calculate projected payoff:
   IF repaymentFrequency = 'MONTHLY':
     months_remaining = (end_date - today) / 30
     projected_balance = calculate_amortization(
       outstanding_balance,
       interest_rate,
       monthly_payment,
       months_remaining
     )
   
   // Project balance at expected death (actuarial age)
   expected_death_age = user.life_expectancy
   years_to_expected_death = expected_death_age - user.current_age
   balance_at_death = project_balance(years_to_expected_death)

7. Currency conversion:
   liability_gbp = convert_to_gbp(outstanding_balance, currency)
   liability_zar = convert_to_zar(outstanding_balance, currency)

RESPONSE:
{
  id: uuid,
  liabilityDetails: {...},
  financial: {
    outstandingBalance: decimal,
    currency: string,
    balanceGbp: decimal,
    balanceZar: decimal,
    userShare: decimal,
    monthlyPayment: decimal,
    interestRate: decimal
  },
  linkedAsset: {
    assetId: uuid,
    assetDescription: string,
    assetValue: decimal,
    loanToValue: decimal (percentage)
  },
  deductibility: {
    ukIht: {
      deductible: boolean,
      deductibleAmount: decimal,
      reason: string,
      restrictions: [string]
    },
    saEstateDuty: {
      deductible: boolean,
      deductibleAmount: decimal,
      reason: string,
      restrictions: [string]
    }
  },
  projection: {
    yearsRemaining: decimal,
    projectedPayoffDate: date,
    balanceAtExpectedDeath: decimal
  }
}
User Flow:
[IHT Dashboard] → [Liabilities Register Tab]
     ↓
[Liabilities Overview]
  - Total liabilities (gross and net to user)
  - Liabilities by type (pie chart)
  - Secured vs unsecured
  - Deductible vs non-deductible
     ↓
[Add Liability Button]
     ↓
[Liability Entry - Step 1: Type]
  - Select liability type (visual cards):
    - Mortgage
    - Personal Loan
    - Credit Card
    - Business Loan
    - Other Debt
     ↓
[Liability Entry - Step 2: Creditor & Details]
  - Liability description
  - Creditor name
  - Account/reference number
     ↓
[Liability Entry - Step 3: Financial Details]
  - Outstanding balance and currency
  - Original amount
  - Interest rate
  - Start date and end date
  - Repayment frequency
  - Monthly payment amount
     ↓
[Liability Entry - Step 4: Security]
  - Is this secured against an asset?
  - If YES: Select asset from list
  - Security type (mortgage, charge, etc.)
  - System shows asset value and LTV
     ↓
[Liability Entry - Step 5: Ownership]
  - Is this a joint liability?
  - If YES: Add joint debtors with %
  - Your percentage share
     ↓
[Liability Entry - Step 6: Deductibility]
  - System calculates deductibility
  - Is creditor a connected person?
  - If YES: Warn about potential restrictions
  - Show UK IHT deductibility
  - Show SA Estate Duty deductibility
     ↓
[Deductibility Summary]
  - UK IHT: Deductible £X (or not deductible with reason)
  - SA Estate Duty: Deductible RX (or not deductible with reason)
  - Any restrictions or warnings
     ↓
[Projection Display]
  - Payoff timeline chart
  - Balance at expected death (based on life expectancy)
  - Effect on net estate
     ↓
[Save Liability]
     ↓
[Liabilities List View]
  - Table/Card view with key details
  - Filter: By type, creditor, deductibility
  - Sort: By balance, interest rate, payoff date
  - Color coding: Deductible (green), Non-deductible (red), Restricted (amber)
  - Quick actions: Make payment, Update balance, View details
     ↓
[Liability Detail View]
  - Complete liability information
  - Payment history
  - Amortization schedule
  - Linked asset details
  - Deductibility breakdown
  - Edit/Delete options
API Endpoints:
•	POST /api/v1/iht/liabilities - Add liability
•	PUT /api/v1/iht/liabilities/{id} - Update liability
•	DELETE /api/v1/iht/liabilities/{id} - Delete liability (soft delete)
•	GET /api/v1/iht/liabilities - List all liabilities
•	GET /api/v1/iht/liabilities/{id} - Get specific liability
•	POST /api/v1/iht/liabilities/{id}/payment - Record payment
•	GET /api/v1/iht/liabilities/{id}/amortization-schedule - Get schedule
•	GET /api/v1/iht/liabilities/summary - Liabilities summary
•	POST /api/v1/iht/liabilities/{id}/update-balance - Update balance
•	GET /api/v1/iht/liabilities/deductibility-analysis - Deductibility summary
Data Models:
TABLE: iht_liabilities
- id: UUID (PK)
- user_id: UUID (FK to users)
- liability_type: ENUM('MORTGAGE', 'PERSONAL_LOAN', 'CREDIT_CARD', 'BUSINESS_LOAN', 
                       'OVERDRAFT', 'TAX_LIABILITY', 'LEGAL_OBLIGATION', 'GUARANTEE', 'OTHER')
- description: VARCHAR(500)
- creditor: VARCHAR(255)
- account_reference: VARCHAR(100) ENCRYPTED
- outstanding_balance: DECIMAL(15,2)
- currency: CHAR(3)
- balance_gbp: DECIMAL(15,2) (calculated)
- balance_zar: DECIMAL(15,2) (calculated)
- original_amount: DECIMAL(15,2)
- interest_rate: DECIMAL(5,2)
- start_date: DATE
- end_date: DATE
- repayment_frequency: ENUM('MONTHLY', 'QUARTERLY', 'ANNUALLY', 'BULLET', 'REVOLVING')
- monthly_payment: DECIMAL(10,2)
- status: ENUM('ACTIVE', 'PAID_OFF', 'DEFAULTED', 'DISPUTED')
- deleted: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: liability_security
- liability_id: UUID (PK, FK to iht_liabilities)
- is_secured: BOOLEAN
- linked_asset_id: UUID (FK to iht_assets)
- security_type: ENUM('MORTGAGE', 'CHARGE', 'PLEDGE', 'UNSECURED')
- loan_to_value: DECIMAL(5,2) (calculated)
- created_at: TIMESTAMP

TABLE: liability_ownership
- id: UUID (PK)
- liability_id: UUID (FK to iht_liabilities)
- joint_liability: BOOLEAN DEFAULT FALSE
- user_percentage: DECIMAL(5,2) DEFAULT 100.00
- user_liability_share: DECIMAL(15,2) (calculated)
- created_at: TIMESTAMP

TABLE: liability_joint_debtors
- id: UUID (PK)
- liability_id: UUID (FK to iht_liabilities)
- debtor_name: VARCHAR(255)
- relationship: VARCHAR(100)
- percentage: DECIMAL(5,2)
- created_at: TIMESTAMP

TABLE: liability_deductibility
- liability_id: UUID (PK, FK to iht_liabilities)
- uk_iht_deductible: BOOLEAN
- uk_iht_deductible_amount: DECIMAL(15,2)
- uk_iht_deductible_reason: TEXT
- uk_iht_restrictions: JSON (array of restrictions)
- sa_estate_duty_deductible: BOOLEAN
- sa_estate_duty_deductible_amount: DECIMAL(15,2)
- sa_estate_duty_deductible_reason: TEXT
- sa_estate_duty_restrictions: JSON
- connected_person: BOOLEAN DEFAULT FALSE
- connected_person_details: TEXT
- contingent_liability: BOOLEAN DEFAULT FALSE
- updated_at: TIMESTAMP

TABLE: liability_payments
- id: UUID (PK)
- liability_id: UUID (FK to iht_liabilities)
- payment_date: DATE
- payment_amount: DECIMAL(10,2)
- principal_paid: DECIMAL(10,2)
- interest_paid: DECIMAL(10,2)
- balance_after_payment: DECIMAL(15,2)
- payment_reference: VARCHAR(100)
- created_at: TIMESTAMP

TABLE: liability_projections
- liability_id: UUID (PK, FK to iht_liabilities)
- projection_date: DATE
- years_remaining: DECIMAL(5,2)
- projected_payoff_date: DATE
- balance_at_expected_death: DECIMAL(15,2)
- total_interest_to_pay: DECIMAL(15,2)
- last_calculated: TIMESTAMP

VIEW: v_liabilities_summary (materialized view)
- user_id
- total_liabilities_gbp
- total_liabilities_zar
- total_secured_liabilities
- total_unsecured_liabilities
- uk_iht_deductible_total
- sa_estate_duty_deductible_total
- non_deductible_total
- liability_count
- last_updated: TIMESTAMP

INDEX on iht_liabilities(user_id, status)
INDEX on liability_security(linked_asset_id)
INDEX on liability_payments(liability_id, payment_date DESC)
CONSTRAINT: SUM(liability_joint_debtors.percentage) + 
            liability_ownership.user_percentage = 100
Error Handling:
ERROR CASES:
1. Negative outstanding balance
   - Response: 400 Bad Request
   - Message: "Outstanding balance cannot be negative"
   
2. Interest rate unreasonable
   - Response: 400 Bad Request (warning)
   - Message: "Interest rate of {rate}% seems unusually high. Please verify"
   - Allow if user confirms
   
3. Monthly payment insufficient for interest
   - Response: 400 Bad Request (warning)
   - Message: "Monthly payment of £{payment} does not cover monthly interest of £{interest}. Loan will never be repaid"
   - Allow with warning (negative amortization)
   
4. End date before start date
   - Response: 400 Bad Request
   - Message: "Loan end date must be after start date"
   
5. Linked asset not found
   - Response: 404 Not Found
   - Message: "Asset with ID {id} not found. Please select a valid asset"
   
6. Joint liability percentages don't total 100%
   - Response: 400 Bad Request
   - Message: "Total liability percentages must equal 100%. Current total: {total}%"
   
7. Secured liability exceeds asset value
   - Response: 400 Bad Request (warning)
   - Message: "Liability of £{liability} exceeds asset value of £{asset}. This is negative equity"
   - Allow with warning
   
8. Connected person liability without justification
   - Response: 400 Bad Request (warning)
   - Message: "Liabilities to connected persons may not be deductible for IHT. Please provide details"

EDGE CASES:
- Revolving credit: Balance fluctuates, use current balance
- Interest-only mortgage: No principal repayment, balloon payment at end
- Payment holiday: Adjust amortization schedule
- Early repayment charge: Factor into payoff calculation
- Variable interest rate: Use current rate for projection, note assumption
- Foreign currency loan: Exchange rate risk affects balance
- Joint and several liability: Each debtor liable for full amount
- Liability paid off: Mark as PAID_OFF, retain for history
- Disputed liability: May not be deductible until resolved
- Contingent liability (guarantee): Only deductible if called upon
- Mortgage with life insurance: May be paid off at death (note this)
- Tax liability: Deductible for estate duty if legally due
- Funeral expenses: Deductible from estate (estimate)
- Business loan with personal guarantee: Track separately
- Shareholder loan: May be treated as part of business valuation
- Liability in trust: May not be personal liability
- Post-death liabilities: Probate costs, executor fees (estimate separately)
Performance Considerations:
•	Amortization calculation: Complex, cache schedule
•	Payment history: Paginate if >100 payments
•	Deductibility determination: Business rules engine, <100ms
•	Currency conversion: Daily batch update
•	Expected liabilities per user: 2-15
•	Liabilities summary: Use materialized view, <500ms response
•	Projection calculations: Pre-calculate monthly, store results
•	Integration with assets: Real-time LTV calculation
•	Bulk operations: Support batch payment recording
 
Feature 8.3: Estate Calculation & IHT/Estate Duty Projection
Feature Name: Comprehensive Estate Valuation and Tax Liability Calculation
User Story: As a user, I want to see my complete estate calculation including UK Inheritance Tax and SA Estate Duty projections so that I can understand my potential tax liability and plan accordingly.
Acceptance Criteria:
•	Calculate gross estate value (all assets)
•	Calculate net estate value (assets minus liabilities)
•	Apply UK IHT calculation with Nil Rate Band, Residence NRB, and reliefs
•	Apply SA Estate Duty calculation with abatement
•	Show tax liability in both jurisdictions
•	Account for Double Tax Agreement provisions
•	Show available allowances and reliefs
•	Project estate value at expected death
•	Scenario modeling (different death ages, asset values)
•	Recommendations for tax reduction
Technical Requirements:
•	Complex multi-jurisdiction estate calculation engine
•	NRB and RNRB calculator
•	Transferable NRB from deceased spouse tracking
•	BPR and APR application
•	SA Estate Duty calculator with Section 4(q) deductions
•	DTA relief calculator
•	Monte Carlo simulation for projections (optional)
•	Scenario modeling engine
Constraints:
•	UK IHT: 40% on estate above NRB (£325,000) + RNRB (up to £175,000)
•	UK RNRB: Tapered away if estate >£2 million
•	UK IHT: Reduced to 36% if 10%+ left to charity
•	SA Estate Duty: 20% on dutiable amount over R30 million (2024)
•	SA Abatement: R3.5 million (2024)
•	DTA: Relief for assets taxed in both jurisdictions
•	Calculations at date of death (not current date)
Implementation Approach:
ENDPOINT: GET /api/v1/iht/estate-calculation
QUERY PARAMS:
- asOfDate: date (default: today, or projected death date)
- scenarioType: enum['CURRENT', 'EXPECTED_DEATH', 'CUSTOM']
- customAge: integer (for custom scenarios)

BUSINESS LOGIC:
1. Gather all estate components:
   total_assets = SUM(iht_assets WHERE user_id = user.id AND deleted = FALSE)
   total_liabilities = SUM(iht_liabilities WHERE user_id = user.id AND deleted = FALSE)
   
   gross_estate = total_assets
   net_estate = total_assets - total_liabilities

2. Separate assets by jurisdiction:
   uk_assets = SUM(iht_assets WHERE uk_iht_applicable = TRUE)
   sa_assets = SUM(iht_assets WHERE sa_estate_duty_applicable = TRUE)
   excluded_property = SUM(iht_assets WHERE excluded_property = TRUE)
   
   // Adjust for excluded property
   uk_taxable_estate = uk_assets - excluded_property
   sa_taxable_estate = sa_assets

3. Calculate UK Inheritance Tax:
   // Nil Rate Band (NRB)
   current_nrb = 325000  // £325k as of 2024
   
   // Transferable NRB from deceased spouse
   transferable_nrb = get_transferable_nrb_from_spouse()
   total_nrb = current_nrb + transferable_nrb
   
   // Residence Nil Rate Band (RNRB)
   max_rnrb = 175000  // £175k as of 2024
   
   // RNRB conditions:
   // - Must own qualifying residential property
   // - Must pass to direct descendants
   // - Tapered if estate > £2m
   
   IF has_qualifying_residence AND passes_to_descendants:
     IF net_estate <= 2000000:
       rnrb = max_rnrb
     ELSE:
       taper = (net_estate - 2000000) / 2  // £1 reduction for every £2 over
       rnrb = MAX(max_rnrb - taper, 0)
   ELSE:
     rnrb = 0
   
   // Transferable RNRB from deceased spouse
   transferable_rnrb = get_transferable_rnrb_from_spouse()
   total_rnrb = rnrb + transferable_rnrb
   
   // Total nil rate bands
   total_nil_rate_bands = total_nrb + total_rnrb
   
   // Apply reliefs (BPR and APR)
   bpr_relief = SUM(iht_assets.bpr_relieved_amount WHERE user_id = user.id)
   apr_relief = SUM(iht_assets.apr_relieved_amount WHERE user_id = user.id)
   total_reliefs = bpr_relief + apr_relief
   
   // Calculate taxable estate
   taxable_estate_after_reliefs = uk_taxable_estate - total_reliefs
   chargeable_estate = MAX(taxable_estate_after_reliefs - total_nil_rate_bands, 0)
   
   // Standard IHT rate: 40%
   standard_rate = 0.40
   
   // Reduced rate: 36% if 10%+ left to charity
   IF charitable_legacy_percentage >= 10:
     iht_rate = 0.36
   ELSE:
     iht_rate = standard_rate
   
   uk_iht_liability = chargeable_estate * iht_rate

4. Calculate SA Estate Duty:
   // SA Estate Duty calculation
   gross_estate_sa = sa_taxable_estate
   
   // Deductions under Section 4(q)
   section_4q_deductions = [
     funeral_expenses,
     executor_fees,
     master_fees,
     valuator_fees,
     other_admin_costs
   ]
   total_section_4q = SUM(section_4q_deductions)
   
   // Property in spouse's estate (Section 4A)
   property_in_spouse_estate = calculate_spouse_estate_property()
   
   // Deductible liabilities
   deductible_liabilities = SUM(iht_liabilities.sa_estate_duty_deductible_amount)
   
   // Net value of estate
   net_estate_sa = gross_estate_sa - total_section_4q - deductible_liabilities
   
   // Abatement (R3.5 million as of 2024)
   abatement = 3500000
   
   // Dutiable amount
   dutiable_amount = MAX(net_estate_sa - abatement, 0)
   
   // Estate duty threshold (R30 million as of 2024)
   estate_duty_threshold = 30000000
   
   IF dutiable_amount > estate_duty_threshold:
     // 20% on amount over R30 million
     sa_estate_duty = (dutiable_amount - estate_duty_threshold) * 0.20
   ELSE:
     sa_estate_duty = 0

5. Apply Double Tax Agreement relief:
   // Assets taxed in both jurisdictions
   dual_taxed_assets = identify_dual_taxed_assets()
   
   // DTA relief: Credit for tax paid in other jurisdiction
   // Typically, country of situs taxes first, residence country gives credit
   
   FOR EACH dual_taxed_asset:
     IF asset.situs = 'UK':
       uk_tax_on_asset = calculate_uk_tax(asset)
       sa_tax_on_asset = calculate_sa_tax(asset)
       
       // SA gives credit for UK tax paid
       sa_dta_relief += MIN(uk_tax_on_asset, sa_tax_on_asset)
     
     ELSE IF asset.situs = 'SA':
       sa_tax_on_asset = calculate_sa_tax(asset)
       uk_tax_on_asset = calculate_uk_tax(asset)
       
       // UK gives credit for SA tax paid
       uk_dta_relief += MIN(sa_tax_on_asset, uk_tax_on_asset)
   
   // Apply relief
   uk_iht_liability_after_dta = uk_iht_liability - uk_dta_relief
   sa_estate_duty_after_dta = sa_estate_duty - sa_dta_relief
   
   total_death_taxes = uk_iht_liability_after_dta + sa_estate_duty_after_dta

6. Calculate effective tax rate:
   effective_uk_rate = (uk_iht_liability / uk_taxable_estate) * 100
   effective_sa_rate = (sa_estate_duty / sa_taxable_estate) * 100
   effective_overall_rate = (total_death_taxes / net_estate) * 100

7. Project future estate value:
   IF scenarioType = 'EXPECTED_DEATH':
     years_to_death = user.life_expectancy - user.current_age
     
     // Project asset growth
     projected_assets = project_assets(current_assets, years_to_death)
     
     // Project liability reduction
     projected_liabilities = project_liabilities(current_liabilities, years_to_death)
     
     // Recalculate with projections
     projected_estate_calculation = calculate_estate(projected_assets, projected_liabilities)

8. Identify planning opportunities:
   recommendations = []
   
   IF uk_iht_liability > 0:
     IF not_using_full_nrb:
       recommendations.add("Consider equalizing estates with spouse to use both NRBs")
     
     IF rnrb = 0 AND has_direct_descendants:
       recommendations.add("Consider purchasing qualifying residence to utilize RNRB")
     
     IF has_business_assets AND not_claiming_bpr:
       recommendations.add("Review business assets for potential BPR")
     
     IF charitable_legacy_percentage < 10:
       recommendations.add("Consider 10% charitable legacy for reduced IHT rate (36%)")
   
   IF sa_estate_duty > 0:
     IF not_using_spouse_benefits:
       recommendations.add("Consider Section 4A deductions for property in spouse's estate")

RESPONSE:
{
  calculationDate: date,
  scenarioType: string,
  
  estateValuation: {
    grossEstate: {gbp: decimal, zar: decimal},
    totalLiabilities: {gbp: decimal, zar: decimal},
    netEstate: {gbp: decimal, zar: decimal}
  },
  
  assetBreakdown: {
    ukAssets: {gbp: decimal, percentage: decimal},
    saAssets: {zar: decimal, percentage: decimal},
    excludedProperty: {gbp: decimal},
    byCategoryGbp: {...},
    byCategoryZar: {...}
  },
  
  ukInheritanceTax: {
    taxableEstate: decimal,
    nilRateBand: {
      current: decimal,
      transferredFromSpouse: decimal,
      total: decimal,
      unused: decimal
    },
    residenceNilRateBand: {
      maximum: decimal,
      taperReduction: decimal,
      available: decimal,
      transferredFromSpouse: decimal,
      total: decimal
    },
    reliefs: {
      businessPropertyRelief: decimal,
      agriculturalPropertyRelief: decimal,
      total: decimal
    },
    chargeableEstate: decimal,
    taxRate: decimal,
    grossTaxLiability: decimal,
    dtaRelief: decimal,
    netTaxLiability: decimal,
    effectiveRate: decimal
  },
  
  saEstateDuty: {
    grossEstate: decimal,
    section4qDeductions: decimal,
    deductibleLiabilities: decimal,
    netEstate: decimal,
    abatement: decimal,
    dutiableAmount: decimal,
    threshold: decimal,
    taxRate: decimal (20%),
    grossTaxLiability: decimal,
    dtaRelief: decimal,
    netTaxLiability: decimal,
    effectiveRate: decimal
  },
  
  totalDeathTaxes: {
    ukIht: decimal,
    saEstateDuty: decimal,
    total: {gbp: decimal, zar: decimal},
    effectiveOverallRate: decimal
  },
  
  netEstateAfterTax: {
    beforeTax: {gbp: decimal, zar: decimal},
    totalTax: {gbp: decimal, zar: decimal},
    afterTax: {gbp: decimal, zar: decimal},
    percentageReduction: decimal
  },
  
  projection: {
    yearsToProjectedDeath: integer,
    projectedGrossEstate: {gbp: decimal, zar: decimal},
    projectedTaxLiability: {gbp: decimal, zar: decimal},
    assumptions: {...}
  },
  
  recommendations: [
    {
      category: string,
      title: string,
      description: string,
      estimatedSaving: {gbp: decimal, zar: decimal},
      priority: enum['HIGH', 'MEDIUM', 'LOW']
    }
  ],
  
  comparisonWithPreviousCalculation: {
    previousDate: date,
    estateValueChange: {amount: decimal, percentage: decimal},
    taxLiabilityChange: {amount: decimal, percentage: decimal}
  }
}
User Flow:
[IHT Dashboard] → [Estate Calculation Tab]
     ↓
[Estate Summary (Hero Section)]
  - Net estate value (prominent)
  - Total tax liability (UK + SA)
  - Effective tax rate %
  - Net estate after tax
     ↓
[Scenario Selector]
  - Current position (today's values)
  - At expected death (life expectancy projection)
  - Custom age scenario
     ↓
[UK Inheritance Tax Section]
  - Taxable estate £X
  - Nil Rate Bands:
    - Your NRB: £325,000
    - Transferred from spouse: £X
    - RNRB: £X
    - Total: £X
  - Reliefs applied:
    - BPR: £X
    - APR: £X
  - Chargeable estate: £X
  - Tax rate: 40% (or 36% if charity)
  - IHT liability: £X
     ↓
[SA Estate Duty Section]
  - Gross estate: RX
  - Deductions: RX
  - Abatement: R3.5m
  - Dutiable amount: RX
  - Estate Duty: RX
     ↓
[DTA Relief Section]
  - Assets taxed in both jurisdictions
  - Relief applied
  - Net tax in each country
     ↓
[Visual Breakdown]
  - Waterfall chart: Gross estate → Reliefs → NRBs → Tax → Net estate
  - Pie chart: Where tax is payable (UK vs SA)
  - Comparison: Before tax vs After tax
     ↓
[Planning Opportunities Section]
  - AI-generated recommendations
  - Prioritized by potential saving
  - Action buttons for each
     ↓
[Projection Timeline]
  - Chart: Estate value over time
  - Chart: Tax liability over time
  - Slider: Adjust age at death for scenarios
     ↓
[Detailed Breakdown (Expandable)]
  - All assets listed with values
  - All liabilities listed
  - Full calculation methodology
  - Assumptions stated
     ↓
[Actions]
  - Download PDF report
  - Share with advisor
  - Schedule review reminder
  - Model "what-if" scenarios
API Endpoints:
•	GET /api/v1/iht/estate-calculation - Get estate calculation
•	POST /api/v1/iht/estate-calculation/scenario - Run scenario analysis
•	GET /api/v1/iht/estate-calculation/history - Historical calculations
•	POST /api/v1/iht/estate-calculation/compare - Compare scenarios
•	GET /api/v1/iht/nil-rate-bands - Get NRB and RNRB details
•	POST /api/v1/iht/transferable-nrb - Calculate transferable NRB
•	GET /api/v1/iht/planning-opportunities - Get recommendations
•	POST /api/v1/iht/estate-projection - Project future estate
•	GET /api/v1/iht/estate-calculation/pdf - Generate PDF report
Data Models:
TABLE: estate_calculations
- id: UUID (PK)
- user_id: UUID (FK to users)
- calculation_date: DATE
- calculation_type: ENUM('CURRENT', 'EXPECTED_DEATH', 'CUSTOM_SCENARIO', 'WHAT_IF')
- scenario_age: INTEGER (if custom)
- gross_estate_gbp: DECIMAL(15,2)
- gross_estate_zar: DECIMAL(15,2)
- total_liabilities_gbp: DECIMAL(15,2)
- total_liabilities_zar: DECIMAL(15,2)
- net_estate_gbp: DECIMAL(15,2)
- net_estate_zar: DECIMAL(15,2)
- uk_iht_liability: DECIMAL(15,2)
- sa_estate_duty_liability: DECIMAL(15,2)
- total_death_taxes_gbp: DECIMAL(15,2)
- total_death_taxes_zar: DECIMAL(15,2)
- net_estate_after_tax_gbp: DECIMAL(15,2)
- net_estate_after_tax_zar: DECIMAL(15,2)
- effective_tax_rate: DECIMAL(5,2)
- calculation_details_json: JSON (full calculation breakdown)
- created_at: TIMESTAMP

TABLE: uk_nil_rate_bands
- user_id: UUID (PK, FK to users)
- current_nrb: DECIMAL(15,2) DEFAULT 325000
- transferable_nrb_available: DECIMAL(15,2)
- transferable_nrb_source: TEXT (spouse details)
- transferable_nrb_date: DATE
- current_rnrb: DECIMAL(15,2)
- max_rnrb: DECIMAL(15,2) DEFAULT 175000
- rnrb_taper_reduction: DECIMAL(15,2)
- transferable_rnrb_available: DECIMAL(15,2)
- total_nrb: DECIMAL(15,2) (calculated)
- total_rnrb: DECIMAL(15,2) (calculated)
- updated_at: TIMESTAMP

TABLE: estate_planning_recommendations
- id: UUID (PK)
- user_id: UUID (FK to users)
- calculation_id: UUID (FK to estate_calculations)
- recommendation_category: ENUM('NRB_OPTIMIZATION', 'RNRB_PLANNING', 'RELIEF_CLAIMING', 
                                'CHARITABLE_GIVING', 'GIFT_PLANNING', 'TRUST_STRUCTURE', 'OTHER')
- recommendation_title: VARCHAR(255)
- recommendation_description: TEXT
- estimated_saving_gbp: DECIMAL(15,2)
- estimated_saving_zar: DECIMAL(15,2)
- priority: ENUM('HIGH', 'MEDIUM', 'LOW')
- status: ENUM('NEW', 'IN_PROGRESS', 'COMPLETED', 'DISMISSED')
- action_taken: TEXT
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: estate_projections
- id: UUID (PK)
- user_id: UUID (FK to users)
- projection_date: DATE
- years_projected: INTEGER
- projected_age_at_death: INTEGER
- projected_gross_estate_gbp: DECIMAL(15,2)
- projected_net_estate_gbp: DECIMAL(15,2)
- projected_tax_liability_gbp: DECIMAL(15,2)
- assumptions: JSON (growth rates, asset changes, etc.)
- created_at: TIMESTAMP

TABLE: dta_relief_calculations
- id: UUID (PK)
- calculation_id: UUID (FK to estate_calculations)
- asset_id: UUID (FK to iht_assets)
- asset_description: VARCHAR(255)
- asset_situs: VARCHAR(50)
- uk_tax_on_asset: DECIMAL(15,2)
- sa_tax_on_asset: DECIMAL(15,2)
- relief_given_by: ENUM('UK', 'SA')
- relief_amount: DECIMAL(15,2)
- created_at: TIMESTAMP

VIEW: v_current_estate_summary (materialized view, refreshed on asset/liability change)
- user_id
- gross_estate_gbp
- net_estate_gbp
- uk_iht_estimate
- sa_estate_duty_estimate
- total_tax_estimate
- net_after_tax
- last_updated: TIMESTAMP

INDEX on estate_calculations(user_id, calculation_date DESC)
INDEX on estate_planning_recommendations(user_id, status, priority)
INDEX on estate_projections(user_id, projection_date DESC)
Error Handling:
ERROR CASES:
1. Insufficient data for calculation
   - Response: 400 Bad Request
   - Message: "Cannot calculate estate tax. Please add at least one asset"
   
2. Missing critical tax status information
   - Response: 400 Bad Request
   - Message: "Domicile status required for accurate I

HT calculation. Please complete your tax status information"
3.	RNRB calculation error - no qualifying residence 
o	Response: 200 OK (with warning)
o	Warning: "RNRB not applied: No qualifying residential property found in estate"
o	Recommendation: "Consider property ownership for RNRB eligibility"
4.	Transferable NRB claimed but no spouse details 
o	Response: 400 Bad Request
o	Message: "Cannot calculate transferable NRB without deceased spouse details"
5.	BPR/APR claimed on assets not meeting holding period 
o	Response: 200 OK (with warning)
o	Warning: "BPR not applied to {asset}: Held for {period}, requires 2 years"
6.	Scenario projection beyond reasonable age 
o	Response: 400 Bad Request
o	Message: "Custom age {age} exceeds reasonable life expectancy. Maximum: 120"
7.	DTA relief calculation error 
o	Response: 200 OK (with warning)
o	Warning: "Unable to calculate DTA relief for some assets. Manual review recommended"
8.	Negative net estate (liabilities exceed assets) 
o	Response: 200 OK
o	Message: "Net estate is negative. No inheritance tax liability"
o	Alert: "Consider reviewing liability levels"
EDGE CASES:
•	Estate exactly at NRB threshold: Tax = £0, but planning still beneficial
•	Estate £1 over threshold: Marginal rate applies to that £1
•	RNRB taper: Precise calculation needed, £1 for £2 reduction
•	Multiple deaths in quick succession: Consider quick succession relief
•	Non-UK domiciled with UK assets: Only UK assets taxed
•	Deemed domicile acquired mid-year: Pro-rata calculation
•	Assets in trust: May or may not be in estate (depends on trust type)
•	Life insurance in trust: Outside estate if properly structured
•	Joint tenancy: Passes outside will, but still in estate for IHT
•	Business assets sold before death: BPR lost
•	Gifts with reservation: Back in estate for IHT
•	Potentially exempt transfers (PETs): Taxable if death within 7 years
•	Taper relief on gifts: Reduces tax if death 3-7 years after gift
•	Charitable legacy exactly 10%: Qualifies for reduced rate
•	Charitable legacy 9.9%: Doesn't qualify, consider rounding up
•	Assets in different currencies: Exchange rate at death applies
•	Valuation disputes: Probate value may differ from current estimate
•	Business assets: Valuation complex, may need professional
•	Quoted shares: Valuation = lower of quarter-up or average
•	Unquoted shares: Professional valuation required
•	Property: Market value, not mortgage outstanding
•	Jointly owned assets: Only deceased's share in estate
•	Foreign assets: May have local death taxes too
•	Pension death benefits: Usually discretionary, not in estate
•	ISA on death: Becomes a "continuing ISA" for spouse
•	Offshore bonds: Complex tax treatment on death
•	Intellectual property: Valuation challenging
•	Digital assets: Cryptocurrency, domain names, etc.

**Performance Considerations:**
- Estate calculation: Complex, cache results for 24 hours
- Trigger recalculation when: Assets change, liabilities change, tax status changes
- NRB/RNRB lookup: Fast, simple calculation
- BPR/APR application: Iterate through assets, apply rules
- DTA relief: Most complex part, may take 1-2 seconds
- Scenario modeling: Multiple calculations, async processing for >3 scenarios
- Expected calculation time: <3 seconds for complete estate
- Projection calculations: Time-intensive, use background job for long projections
- PDF generation: Async job, 10-30 seconds depending on estate complexity
- Historical comparison: Pre-aggregate monthly snapshots
- Real-time updates: WebSocket for live recalculation as user adds assets

---

### Feature 8.4: Lifetime Gifts Register & PETs Tracking

**Feature Name:** Lifetime Gifts and Potentially Exempt Transfers Management

**User Story:**
As a user planning to reduce my estate through gifting, I want to track all lifetime gifts and understand their IHT implications, including the 7-year rule and taper relief, so I can manage my gift planning effectively.

**Acceptance Criteria:**
- Record all lifetime gifts with date, recipient, and value
- Track Potentially Exempt Transfers (PETs)
- Track Chargeable Lifetime Transfers (CLTs) to trusts
- Monitor 7-year clock for each gift
- Calculate taper relief if death within 7 years
- Track annual exemption usage (£3,000 per year)
- Track small gifts exemption (£250 per person)
- Track wedding/civil partnership gifts exemptions
- Track gifts out of income exemption
- Alert when gifts may become chargeable
- Integration with estate calculation

**Technical Requirements:**
- Gift tracking with date-based calculations
- 7-year running total calculator
- Taper relief calculator
- Exemption tracker (annual, small gifts, normal expenditure)
- Gift categorization engine
- PET/CLT classification logic
- Integration with IHT calculation

**Constraints:**
- PET becomes exempt if donor survives 7 years
- Taper relief: Reduces tax (not value) if death 3-7 years after gift
- Annual exemption: £3,000 per year (can carry forward 1 year unused)
- Small gifts: £250 per person per year (not if used annual exemption)
- Wedding gifts: £5,000 (child), £2,500 (grandchild), £1,000 (other)
- Normal expenditure out of income: Must be regular and leave donor with adequate income
- CLT: Immediate IHT charge if exceeds NRB

**Implementation Approach:**
```pseudo
ENDPOINT: POST /api/v1/iht/gifts
REQUEST BODY:
{
  giftDate: date,
  recipient: {
    name: string,
    relationship: enum['SPOUSE', 'CHILD', 'GRANDCHILD', 'PARENT', 'SIBLING', 
                       'FRIEND', 'CHARITY', 'TRUST', 'OTHER'],
    age: integer (optional)
  },
  
  giftType: enum['CASH', 'PROPERTY', 'SHARES', 'OTHER_ASSET'],
  giftDescription: string,
  giftValue: decimal,
  currency: string,
  
  giftCategory: enum['OUTRIGHT_GIFT', 'GIFT_TO_TRUST', 'GIFT_WITH_RESERVATION'],
  
  trustDetails: {
    trustName: string,
    trustType: enum['BARE', 'DISCRETIONARY', 'INTEREST_IN_POSSESSION'],
    beneficiaries: [string]
  },
  
  exemptions: {
    annualExemption: {
      claimCurrent: boolean,
      claimPreviousYear: boolean,
      amountClaimed: decimal
    },
    smallGiftsExemption: boolean,  // £250 per person
    weddingGiftExemption: {
      applicable: boolean,
      amount: decimal  // £5000/£2500/£1000
    },
    normalExpenditureOutOfIncome: boolean,
    spouseExemption: boolean,  // Unlimited if spouse
    charityExemption: boolean   // Unlimited to charity
  },
  
  reservationOfBenefit: {
    hasReservation: boolean,
    reservationDetails: text
  },
  
  notes: text
}

BUSINESS LOGIC:
1. Validate gift data:
   - Gift date <= today
   - Gift value > 0
   - Recipient details provided
   - Gift date not more than 7 years in past (for tracking purposes)

2. Classify gift (PET vs CLT):
   IF recipient.relationship = 'SPOUSE':
     classification = 'SPOUSE_EXEMPT'
     potentially_exempt = FALSE
     immediately_exempt = TRUE
   
   ELSE IF recipient.relationship = 'CHARITY':
     classification = 'CHARITY_EXEMPT'
     potentially_exempt = FALSE
     immediately_exempt = TRUE
   
   ELSE IF giftCategory = 'OUTRIGHT_GIFT':
     classification = 'PET'  // Potentially Exempt Transfer
     potentially_exempt = TRUE
     immediately_exempt = FALSE
   
   ELSE IF giftCategory = 'GIFT_TO_TRUST':
     IF trustType = 'BARE':
       classification = 'PET'
       potentially_exempt = TRUE
     ELSE:  // Discretionary or IIP trusts
       classification = 'CLT'  // Chargeable Lifetime Transfer
       potentially_exempt = FALSE
       calculate_immediate_iht_charge()

3. Apply exemptions:
   gift_value_before_exemptions = gift_value
   
   // Spouse exemption (unlimited)
   IF exemptions.spouseExemption:
     taxable_value = 0
     RETURN  // Fully exempt
   
   // Charity exemption (unlimited)
   IF exemptions.charityExemption:
     taxable_value = 0
     RETURN  // Fully exempt
   
   // Annual exemption (£3,000 per year)
   IF exemptions.annualExemption.claimCurrent:
     current_year_exemption_used = get_annual_exemption_used(gift_date.year)
     current_year_exemption_available = MAX(3000 - current_year_exemption_used, 0)
     
     exemption_applied = MIN(gift_value, current_year_exemption_available)
     gift_value -= exemption_applied
     
     // Carry forward previous year's unused exemption
     IF exemptions.annualExemption.claimPreviousYear AND gift_value > 0:
       previous_year_unused = get_previous_year_unused_exemption(gift_date.year - 1)
       previous_exemption_applied = MIN(gift_value, previous_year_unused)
       gift_value -= previous_exemption_applied
   
   // Small gifts exemption (£250 per person per year)
   IF exemptions.smallGiftsExemption:
     IF gift_value <= 250 AND not_already_claimed_annual_exemption_for_recipient:
       gift_value = 0  // Fully exempt
   
   // Wedding gift exemption
   IF exemptions.weddingGiftExemption.applicable:
     IF recipient.relationship = 'CHILD':
       wedding_exemption = MIN(5000, gift_value)
     ELSE IF recipient.relationship = 'GRANDCHILD':
       wedding_exemption = MIN(2500, gift_value)
     ELSE:
       wedding_exemption = MIN(1000, gift_value)
     
     gift_value -= wedding_exemption
   
   // Normal expenditure out of income
   IF exemptions.normalExpenditureOutOfIncome:
     // This is a qualitative exemption, mark for evidence
     requires_income_evidence = TRUE
     // If proven, fully exempt
     IF can_prove_normal_expenditure:
       gift_value = 0
   
   taxable_value = MAX(gift_value, 0)

4. Check for gift with reservation:
   IF reservationOfBenefit.hasReservation:
     // Gift with reservation treated as still in estate
     gift_with_reservation = TRUE
     alert = "This gift may remain in your estate for IHT purposes"

5. Calculate 7-year status:
   years_since_gift = (today - gift_date) / 365
   years_remaining = MAX(7 - years_since_gift, 0)
   
   IF years_remaining = 0:
     pet_status = 'EXEMPT'  // Survived 7 years
   ELSE:
     pet_status = 'POTENTIALLY_EXEMPT'
     pet_becomes_exempt_date = gift_date + 7_years

6. Calculate potential IHT on gift if death now:
   // Only relevant for PETs or CLTs
   IF classification IN ['PET', 'CLT']:
     // Check 7-year cumulation
     gifts_in_previous_7_years = get_gifts_in_previous_7_years(gift_date)
     cumulative_total = SUM(gifts_in_previous_7_years) + taxable_value
     
     // Apply NRB
     nrb_at_gift_date = 325000  // Use historical NRB if older gift
     
     IF cumulative_total > nrb_at_gift_date:
       excess = cumulative_total - nrb_at_gift_date
       potential_iht = excess * 0.20  // 20% lifetime rate (half death rate)
       
       // Taper relief if death 3-7 years after gift
       IF years_since_gift >= 3 AND years_since_gift < 7:
         taper_relief_percentage = calculate_taper_relief(years_since_gift)
         potential_iht = potential_iht * (1 - taper_relief_percentage)
     ELSE:
       potential_iht = 0

7. Calculate taper relief:
   calculate_taper_relief(years_since_gift):
     IF years_since_gift < 3:
       RETURN 0  // No taper relief
     ELSE IF years_since_gift >= 3 AND years_since_gift < 4:
       RETURN 0.20  // 20% relief
     ELSE IF years_since_gift >= 4 AND years_since_gift < 5:
       RETURN 0.40  // 40% relief
     ELSE IF years_since_gift >= 5 AND years_since_gift < 6:
       RETURN 0.60  // 60% relief
     ELSE IF years_since_gift >= 6 AND years_since_gift < 7:
       RETURN 0.80  // 80% relief
     ELSE:
       RETURN 1.00  // 100% relief (exempt)

8. Integration with estate calculation:
   // Gifts within 7 years added back to estate
   IF pet_status = 'POTENTIALLY_EXEMPT':
     add_to_estate_calculation(taxable_value, potential_iht)

9. Currency conversion:
   gift_value_gbp = convert_to_gbp(gift_value, currency, gift_date)
   gift_value_zar = convert_to_zar(gift_value, currency, gift_date)

RESPONSE:
{
  id: uuid,
  giftDetails: {...},
  classification: {
    type: enum['PET', 'CLT', 'SPOUSE_EXEMPT', 'CHARITY_EXEMPT'],
    potentiallyExempt: boolean,
    immediatelyExempt: boolean
  },
  exemptions: {
    applied: [
      {type: string, amount: decimal}
    ],
    totalExemptions: decimal,
    taxableValue: decimal
  },
  sevenYearStatus: {
    yearsElapsed: decimal,
    yearsRemaining: decimal,
    becomesExemptDate: date,
    currentStatus: enum['POTENTIALLY_EXEMPT', 'EXEMPT', 'CHARGEABLE']
  },
  potentialIht: {
    ifDeathToday: decimal,
    taperRelief: {
      applicable: boolean,
      percentage: decimal,
      reliefAmount: decimal
    },
    cumulativeGifts: decimal
  },
  alerts: [
    {severity: string, message: string}
  ],
  recommendations: [
    {message: string}
  ]
}
User Flow:
[IHT Dashboard] → [Gifts Register Tab]
     ↓
[Gifts Overview]
  - Total gifts in last 7 years
  - PETs still within 7-year period
  - Gifts becoming exempt soon
  - Annual exemption used/available
     ↓
[Add Gift Button]
     ↓
[Gift Entry - Step 1: When & To Whom]
  - Gift date
  - Recipient name
  - Relationship to you
     ↓
[Gift Entry - Step 2: What Was Given]
  - Gift type (cash, property, shares, etc.)
  - Description
  - Value and currency
     ↓
[Gift Entry - Step 3: Gift Structure]
  - Outright gift OR
  - Gift to trust → Trust details
  - Did you keep any benefit? (reservation)
     ↓
[Gift Entry - Step 4: Exemptions]
  System suggests applicable exemptions:
  - Spouse? → Unlimited exemption
  - Charity? → Unlimited exemption
  - Use annual exemption (£3,000)? → Check available
  - Small gift (≤£250)?
  - Wedding gift?
  - Normal expenditure out of income?
     ↓
[Exemption Calculator]
  - Shows gift value before exemptions
  - Shows exemptions applied
  - Shows taxable value after exemptions
     ↓
[7-Year Timeline Display]
  - Current date
  - Gift date marked
  - 7-year countdown
  - Date gift becomes exempt
  - Timeline visualization
     ↓
[Potential IHT Calculation]
  - "If you died today, potential IHT: £X"
  - Taper relief: £X (if 3-7 years)
  - Cumulative gifts: £X
     ↓
[Save Gift]
     ↓
[Gifts List View]
  - Timeline view: All gifts on 7-year timeline
  - Card view: Each gift with key details
  - Filter: By status, recipient, year
  - Sort: By date, value, years remaining
  - Color coding: 
    - Red: Within 3 years (no taper)
    - Amber: 3-7 years (partial taper)
    - Green: >7 years (exempt)
     ↓
[Gift Detail View]
  - Complete gift information
  - 7-year timeline
  - Exemptions breakdown
  - Potential IHT calculation
  - Edit/Delete options
     ↓
[Annual Exemption Tracker]
  - Current year: £X used of £3,000
  - Previous year: £X unused (can carry forward)
  - Historical usage chart
     ↓
[Gift Planning Tools]
  - "Plan a Gift" wizard
  - Calculates optimal gift strategy
  - Shows impact on estate
API Endpoints:
•	POST /api/v1/iht/gifts - Record gift
•	PUT /api/v1/iht/gifts/{id} - Update gift
•	DELETE /api/v1/iht/gifts/{id} - Delete gift (soft delete)
•	GET /api/v1/iht/gifts - List all gifts
•	GET /api/v1/iht/gifts/{id} - Get specific gift
•	GET /api/v1/iht/gifts/seven-year-summary - 7-year gifts summary
•	GET /api/v1/iht/gifts/annual-exemption - Annual exemption status
•	POST /api/v1/iht/gifts/calculate-iht - Calculate IHT on gifts
•	GET /api/v1/iht/gifts/timeline - Get gifts timeline visualization
•	POST /api/v1/iht/gifts/planning-tool - Gift planning calculator
Data Models:
TABLE: lifetime_gifts
- id: UUID (PK)
- user_id: UUID (FK to users)
- gift_date: DATE
- recipient_name: VARCHAR(255)
- recipient_relationship: ENUM('SPOUSE', 'CHILD', 'GRANDCHILD', 'PARENT', 'SIBLING', 
                                'FRIEND', 'CHARITY', 'TRUST', 'OTHER')
- gift_type: ENUM('CASH', 'PROPERTY', 'SHARES', 'OTHER_ASSET')
- gift_description: TEXT
- gift_value: DECIMAL(15,2)
- currency: CHAR(3)
- gift_value_gbp: DECIMAL(15,2) (calculated)
- gift_value_zar: DECIMAL(15,2) (calculated)
- gift_category: ENUM('OUTRIGHT_GIFT', 'GIFT_TO_TRUST', 'GIFT_WITH_RESERVATION')
- classification: ENUM('PET', 'CLT', 'SPOUSE_EXEMPT', 'CHARITY_EXEMPT')
- potentially_exempt: BOOLEAN
- becomes_exempt_date: DATE (gift_date + 7 years)
- pet_status: ENUM('POTENTIALLY_EXEMPT', 'EXEMPT', 'CHARGEABLE')
- deleted: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: gift_trust_details
- gift_id: UUID (PK, FK to lifetime_gifts)
- trust_name: VARCHAR(255)
- trust_type: ENUM('BARE', 'DISCRETIONARY', 'INTEREST_IN_POSSESSION')
- beneficiaries: JSON (array)
- trust_deed_reference: UUID (FK to documents)
- created_at: TIMESTAMP

TABLE: gift_exemptions
- id: UUID (PK)
- gift_id: UUID (FK to lifetime_gifts)
- exemption_type: ENUM('ANNUAL_EXEMPTION_CURRENT', 'ANNUAL_EXEMPTION_PREVIOUS', 
                       'SMALL_GIFTS', 'WEDDING', 'NORMAL_EXPENDITURE', 'SPOUSE', 'CHARITY')
- exemption_amount: DECIMAL(15,2)
- exemption_year: INTEGER (for annual exemption tracking)
- created_at: TIMESTAMP

TABLE: gift_reservation_of_benefit
- gift_id: UUID (PK, FK to lifetime_gifts)
- has_reservation: BOOLEAN
- reservation_details: TEXT
- gift_with_reservation_flag: BOOLEAN
- created_at: TIMESTAMP

TABLE: gift_iht_calculations
- gift_id: UUID (PK, FK to lifetime_gifts)
- taxable_value: DECIMAL(15,2)
- cumulative_gifts_7_years: DECIMAL(15,2)
- nil_rate_band_used: DECIMAL(15,2)
- potential_iht_if_death_today: DECIMAL(15,2)
- taper_relief_applicable: BOOLEAN
- taper_relief_percentage: DECIMAL(5,2)
- taper_relief_amount: DECIMAL(15,2)
- iht_after_taper: DECIMAL(15,2)
- last_calculated: TIMESTAMP

TABLE: annual_exemption_tracking
- id: UUID (PK)
- user_id: UUID (FK to users)
- tax_year: INTEGER
- annual_exemption_limit: DECIMAL(10,2) DEFAULT 3000
- exemption_used: DECIMAL(10,2)
- exemption_available: DECIMAL(10,2)
- carry_forward_from_previous: DECIMAL(10,2)
- created_at: TIMESTAMP

TABLE: gift_planning_scenarios
- id: UUID (PK)
- user_id: UUID (FK to users)
- scenario_name: VARCHAR(255)
- planned_gifts: JSON (array of planned gifts)
- projected_estate_reduction: DECIMAL(15,2)
- projected_iht_saving: DECIMAL(15,2)
- created_at: TIMESTAMP

VIEW: v_active_pets (gifts within 7 years)
- user_id
- gift_id
- gift_date
- recipient_name
- gift_value_gbp
- taxable_value
- years_elapsed
- years_remaining
- becomes_exempt_date
- potential_iht

INDEX on lifetime_gifts(user_id, gift_date DESC)
INDEX on lifetime_gifts(user_id, pet_status, becomes_exempt_date)
INDEX on gift_exemptions(gift_id, exemption_type)
INDEX on annual_exemption_tracking(user_id, tax_year)
Error Handling:
ERROR CASES:
1. Gift date in future
   - Response: 400 Bad Request
   - Message: "Gift date cannot be in the future"
   
2. Gift date more than 7 years ago
   - Response: 400 Bad Request (warning)
   - Message: "Gift is more than 7 years old and should be exempt. Still record?"
   - Allow with confirmation (for historical records)
   
3. Annual exemption exceeded
   - Response: 400 Bad Request (warning)
   - Message: "Annual exemption of £{available} exceeded. Claim amount: £{claimed}"
   - Allow with warning that excess is taxable
   
4. Small gifts exemption misapplied
   - Response: 400 Bad Request
   - Message: "Small gifts exemption (£250) cannot be used with annual exemption for same recipient"
   
5. Spouse/charity exemption with other exemptions
   - Response: 400 Bad Request (warning)
   - Message: "Spouse/charity gifts are fully exempt. Other exemptions not needed"
   
6. Normal expenditure out of income without evidence
   - Response: 200 OK (with alert)
   - Alert: "Normal expenditure exemption requires evidence of regular gifts from income. Ensure records kept"
   
7. Wedding gift exemption without wedding context
   - Response: 400 Bad Request
   - Message: "Wedding gift exemption requires wedding/civil partnership date"
   
8. Gift to discretionary trust exceeding NRB
   - Response: 200 OK (with alert)
   - Alert: "CLT of £{amount} exceeds NRB. Immediate IHT charge of £{tax} may apply"

EDGE CASES:
- Gift to spouse who is non-UK domiciled: Limited to £325,000
- Gift to charity via will (not lifetime): Not a PET, handled in will planning
- Gift of property with mortgage: Value = property value - mortgage
- Gift of shares: Valuation on date of gift
- Gift of business asset: May qualify for BPR (50% or 100%)
- Gift of agricultural land: May qualify for APR
- Gifts to political parties: Exempt if party meets criteria
- Gifts to museums/galleries: Exempt if qualifying
- Gifts to housing associations: Exempt
- Conditional exemption for heritage assets: Complex rules
- Potentially exempt transfer failing: Becomes chargeable if death within 7 years
- CLT to discretionary trust: Periodic charges every 10 years
- Exit charges from trusts: Complex trust taxation
- Gift and leaseback: May be gift with reservation
- Gift of property but continue living there: Gift with reservation
- Gift with reservation released before death: May still be in estate
- Failed PETs: Tax calculated at death, not gift date
- Taper relief: Reduces tax, not value
- Cumulation: Gifts cumulate backwards 7 years from each gift
- Multiple gifts same day: Treated as single gift for cumulation
- Death within 7 years of multiple PETs: All become chargeable
- Quick succession relief: If recipient dies within 5 years
Performance Considerations:
•	7-year calculation: Simple date arithmetic, <10ms
•	Cumulative gifts calculation: Query last 7 years, <50ms
•	Annual exemption lookup: Index on tax_year, <20ms
•	IHT calculation on gifts: More complex, cache results
•	Timeline visualization: Pre-calculate data points
•	Expected gifts per user: 5-50 over lifetime
•	Gifts list query: <500ms with filters
•	Background job: Daily check for gifts becoming exempt
•	Alert generation: When gift enters final year before exemption
•	Integration with estate calc: Real-time for active PETs
 

9. TAX INTELLIGENCE ENGINE
Feature 9.1: Core Tax Calculation Service
Feature Name: Multi-Jurisdiction Tax Calculation Engine
User Story: As the system, I need a centralized tax calculation engine that can accurately compute income tax, capital gains tax, dividend tax, and other taxes for both UK and SA jurisdictions, applying the correct rates, bands, and allowances based on user circumstances.
Acceptance Criteria:
•	Calculate UK Income Tax (including Scottish rates where applicable)
•	Calculate SA Income Tax (PAYE and provisional tax)
•	Calculate UK Capital Gains Tax with annual exemption
•	Calculate SA Capital Gains Tax (inclusion rate method)
•	Calculate UK Dividend Tax with dividend allowance
•	Calculate SA Dividend Withholding Tax
•	Apply correct tax bands and rates for each jurisdiction
•	Handle personal allowance tapering (UK)
•	Support rebates and tax credits (SA)
•	Version control for historical tax rates
•	Real-time calculation API
Technical Requirements:
•	Tax rules engine with versioned rate tables
•	Progressive tax band calculator
•	Allowance and relief calculator
•	High-precision decimal arithmetic
•	Historical tax rate database
•	Calculation audit trail
•	Performance optimization for multiple calculations
•	Stateless calculation service
Constraints:
•	Tax rates change annually (April for UK, March for SA)
•	Must support historical calculations for past tax years
•	Calculations must be reproducible (audit trail)
•	Performance: <50ms per calculation
•	Precision: 2 decimal places for currency
•	Must handle edge cases (£0 income, negative adjustments)
Implementation Approach:
SERVICE: TaxCalculationService

CLASS TaxCalculationService:
  
  # ===== UK INCOME TAX =====
  FUNCTION calculate_uk_income_tax(
    income: decimal,
    tax_year: string,
    scotland_resident: boolean,
    personal_allowance_restriction: decimal = 0
  ) -> UkIncomeTaxResult:
    
    # Get tax year configuration
    config = get_uk_tax_config(tax_year)
    
    # Personal Allowance calculation
    personal_allowance = config.personal_allowance  # £12,570 for 2024/25
    
    # Taper personal allowance if income > £100,000
    IF income > 100000:
      taper = (income - 100000) / 2
      personal_allowance = MAX(personal_allowance - taper, 0)
    
    # Apply any additional restrictions
    personal_allowance = MAX(personal_allowance - personal_allowance_restriction, 0)
    
    # Taxable income
    taxable_income = MAX(income - personal_allowance, 0)
    
    # Get appropriate tax bands (England/Wales/NI or Scotland)
    IF scotland_resident:
      bands = config.scottish_income_tax_bands
    ELSE:
      bands = config.uk_income_tax_bands
    
    # Example bands for England/Wales 2024/25:
    # £0 - £37,700: 20% (Basic rate)
    # £37,701 - £125,140: 40% (Higher rate)
    # £125,141+: 45% (Additional rate)
    
    # Calculate tax by band
    tax_by_band = []
    remaining_income = taxable_income
    cumulative_threshold = 0
    
    FOR EACH band IN bands:
      band_size = band.upper_limit - cumulative_threshold
      
      IF remaining_income <= 0:
        BREAK
      
      IF band.upper_limit = INFINITY:  # Top band
        taxable_in_band = remaining_income
      ELSE:
        taxable_in_band = MIN(remaining_income, band_size)
      
      tax_in_band = taxable_in_band * band.rate
      
      tax_by_band.append({
        band_name: band.name,
        taxable_amount: taxable_in_band,
        rate: band.rate,
        tax: tax_in_band
      })
      
      remaining_income -= taxable_in_band
      cumulative_threshold = band.upper_limit
    
    total_tax = SUM(tax_by_band[].tax)
    
    # Calculate effective rate
    effective_rate = (total_tax / income) * 100 IF income > 0 ELSE 0
    
    # Calculate marginal rate
    marginal_rate = determine_marginal_rate(income, bands)
    
    RETURN {
      gross_income: income,
      personal_allowance: personal_allowance,
      taxable_income: taxable_income,
      tax_by_band: tax_by_band,
      total_tax: total_tax,
      net_income: income - total_tax,
      effective_rate: effective_rate,
      marginal_rate: marginal_rate,
      tax_year: tax_year
    }
  
  
  # ===== UK NATIONAL INSURANCE =====
  FUNCTION calculate_uk_national_insurance(
    income: decimal,
    tax_year: string,
    employment_type: enum['EMPLOYED', 'SELF_EMPLOYED']
  ) -> UkNationalInsuranceResult:
    
    config = get_uk_tax_config(tax_year)
    
    IF employment_type = 'EMPLOYED':
      # Class 1 NI (Employees)
      # 2024/25: 8% on £12,570 - £50,270, 2% above
      
      primary_threshold = config.ni_primary_threshold  # £12,570
      upper_earnings_limit = config.ni_upper_earnings_limit  # £50,270
      
      ni_class_1 = 0
      
      IF income > primary_threshold:
        # 8% band
        band_1_income = MIN(income - primary_threshold, 
                            upper_earnings_limit - primary_threshold)
        ni_class_1 += band_1_income * 0.08
        
        # 2% band (above UEL)
        IF income > upper_earnings_limit:
          band_2_income = income - upper_earnings_limit
          ni_class_1 += band_2_income * 0.02
      
      RETURN {
        gross_income: income,
        class_1_ni: ni_class_1,
        total_ni: ni_class_1,
        effective_rate: (ni_class_1 / income) * 100
      }
    
    ELSE IF employment_type = 'SELF_EMPLOYED':
      # Class 2 and Class 4 NI
      class_2_threshold = config.ni_class_2_threshold  # £12,570
      class_4_lower_limit = config.ni_class_4_lower  # £12,570
      class_4_upper_limit = config.ni_class_4_upper  # £50,270
      
      # Class 2: Flat rate if profits > threshold
      class_2_ni = 0
      IF income > class_2_threshold:
        class_2_ni = config.ni_class_2_weekly_rate * 52  # £3.45/week * 52
      
      # Class 4: 6% on £12,570 - £50,270, 2% above
      class_4_ni = 0
      
      IF income > class_4_lower_limit:
        band_1_income = MIN(income - class_4_lower_limit,
                            class_4_upper_limit - class_4_lower_limit)
        class_4_ni += band_1_income * 0.06
        
        IF income > class_4_upper_limit:
          band_2_income = income - class_4_upper_limit
          class_4_ni += band_2_income * 0.02
      
      total_ni = class_2_ni + class_4_ni
      
      RETURN {
        gross_income: income,
        class_2_ni: class_2_ni,
        class_4_ni: class_4_ni,
        total_ni: total_ni,
        effective_rate: (total_ni / income) * 100
      }
  
  
  # ===== UK CAPITAL GAINS TAX =====
  FUNCTION calculate_uk_capital_gains_tax(
    capital_gain: decimal,
    asset_type: enum['RESIDENTIAL_PROPERTY', 'OTHER'],
    tax_year: string,
    income: decimal,
    basic_rate_band_remaining: decimal
  ) -> UkCapitalGainsTaxResult:
    
    config = get_uk_tax_config(tax_year)
    
    # Annual Exempt Amount (AEA)
    annual_exemption = config.cgt_annual_exemption  # £3,000 for 2024/25
    
    taxable_gain = MAX(capital_gain - annual_exemption, 0)
    
    # CGT rates depend on asset type and tax band
    IF asset_type = 'RESIDENTIAL_PROPERTY':
      basic_rate_cgt = 0.18
      higher_rate_cgt = 0.24
    ELSE:  # Other assets
      basic_rate_cgt = 0.10
      higher_rate_cgt = 0.20
    
    # Determine how much gain falls in basic rate band
    gain_in_basic_rate = MIN(taxable_gain, basic_rate_band_remaining)
    gain_in_higher_rate = MAX(taxable_gain - basic_rate_band_remaining, 0)
    
    tax_at_basic_rate = gain_in_basic_rate * basic_rate_cgt
    tax_at_higher_rate = gain_in_higher_rate * higher_rate_cgt
    
    total_cgt = tax_at_basic_rate + tax_at_higher_rate
    
    RETURN {
      capital_gain: capital_gain,
      annual_exemption_used: MIN(capital_gain, annual_exemption),
      taxable_gain: taxable_gain,
      gain_at_basic_rate: gain_in_basic_rate,
      gain_at_higher_rate: gain_in_higher_rate,
      tax_at_basic_rate: tax_at_basic_rate,
      tax_at_higher_rate: tax_at_higher_rate,
      total_cgt: total_cgt,
      effective_rate: (total_cgt / capital_gain) * 100 IF capital_gain > 0 ELSE 0
    }
  
  
  # ===== UK DIVIDEND TAX =====
  FUNCTION calculate_uk_dividend_tax(
    dividend_income: decimal,
    tax_year: string,
    other_income: decimal,
    basic_rate_band_remaining: decimal
  ) -> UkDividendTaxResult:
    
    config = get_uk_tax_config(tax_year)
    
    # Dividend Allowance
    dividend_allowance = config.dividend_allowance  # £500 for 2024/25
    
    taxable_dividends = MAX(dividend_income - dividend_allowance, 0)
    
    # Dividend tax rates (2024/25):
    # Basic rate: 8.75%
    # Higher rate: 33.75%
    # Additional rate: 39.35%
    
    # Determine tax band utilization
    dividends_at_basic_rate = MIN(taxable_dividends, basic_rate_band_remaining)
    
    # Calculate remaining income after basic rate band used
    remaining_after_basic = MAX(taxable_dividends - dividends_at_basic_rate, 0)
    
    # Higher rate band threshold (£125,140 - £37,700 = £87,440)
    higher_rate_band_size = 125140 - 37700
    income_in_higher_band = other_income - 37700
    higher_rate_band_remaining = MAX(higher_rate_band_size - income_in_higher_band, 0)
    
    dividends_at_higher_rate = MIN(remaining_after_basic, higher_rate_band_remaining)
    dividends_at_additional_rate = MAX(remaining_after_basic - dividends_at_higher_rate, 0)
    
    # Calculate tax
    tax_at_basic_rate = dividends_at_basic_rate * 0.0875
    tax_at_higher_rate = dividends_at_higher_rate * 0.3375
    tax_at_additional_rate = dividends_at_additional_rate * 0.3935
    
    total_dividend_tax = tax_at_basic_rate + tax_at_higher_rate + tax_at_additional_rate
    
    RETURN {
      dividend_income: dividend_income,
      dividend_allowance_used: MIN(dividend_income, dividend_allowance),
      taxable_dividends: taxable_dividends,
      dividends_at_basic_rate: dividends_at_basic_rate,
      dividends_at_higher_rate: dividends_at_higher_rate,
      dividends_at_additional_rate: dividends_at_additional_rate,
      tax_at_basic_rate: tax_at_basic_rate,
      tax_at_higher_rate: tax_at_higher_rate,
      tax_at_additional_rate: tax_at_additional_rate,
      total_tax: total_dividend_tax,
      effective_rate: (total_dividend_tax / dividend_income) * 100 IF dividend_income > 0 ELSE 0
    }
  
  
  # ===== SA INCOME TAX =====
  FUNCTION calculate_sa_income_tax(
    taxable_income: decimal,
    tax_year: string,
    age_group: enum['UNDER_65', '65_TO_74', '75_PLUS']
  ) -> SaIncomeTaxResult:
    
    config = get_sa_tax_config(tax_year)
    
    # SA Income Tax Bands (2024/2025):
    # R0 - R237,100: 18%
    # R237,101 - R370,500: 26%
    # R370,501 - R512,800: 31%
    # R512,801 - R673,000: 36%
    # R673,001 - R857,900: 39%
    # R857,901+: 45%
    
    bands = config.income_tax_bands
    
    # Calculate tax by band
    tax_by_band = []
    remaining_income = taxable_income
    
    FOR EACH band IN bands:
      IF remaining_income <= 0:
        BREAK
      
      IF band.upper_limit = INFINITY:
        taxable_in_band = remaining_income
      ELSE:
        band_size = band.upper_limit - band.lower_limit
        taxable_in_band = MIN(remaining_income, band_size)
      
      tax_in_band = taxable_in_band * band.rate
      
      tax_by_band.append({
        band_name: band.name,
        taxable_amount: taxable_in_band,
        rate: band.rate,
        tax: tax_in_band
      })
      
      remaining_income -= taxable_in_band
    
    gross_tax = SUM(tax_by_band[].tax)
    
    # Apply Primary Rebate (age-dependent)
    IF age_group = 'UNDER_65':
      primary_rebate = config.primary_rebate  # R17,235 for 2024/25
    ELSE IF age_group = '65_TO_74':
      primary_rebate = config.secondary_rebate  # R19,500
    ELSE:  # 75+
      primary_rebate = config.tertiary_rebate  # R21,720
    
    # Tax payable after rebate
    tax_payable = MAX(gross_tax - primary_rebate, 0)
    
    # Calculate effective rate
    effective_rate = (tax_payable / taxable_income) * 100 IF taxable_income > 0 ELSE 0
    
    # Determine marginal rate
    marginal_rate = determine_sa_marginal_rate(taxable_income, bands)
    
    RETURN {
      taxable_income: taxable_income,
      tax_by_band: tax_by_band,
      gross_tax: gross_tax,
      primary_rebate: primary_rebate,
      tax_payable: tax_payable,
      net_income: taxable_income - tax_payable,
      effective_rate: effective_rate,
      marginal_rate: marginal_rate,
      tax_year: tax_year
    }
  
  
  # ===== SA CAPITAL GAINS TAX =====
  FUNCTION calculate_sa_capital_gains_tax(
    capital_gain: decimal,
    tax_year: string,
    taxable_income: decimal
  ) -> SaCapitalGainsTaxResult:
    
    config = get_sa_tax_config(tax_year)
    
    # SA CGT uses inclusion rate method
    # Annual exclusion: R40,000 (2024/25)
    # Inclusion rate: 40% for individuals
    
    annual_exclusion = config.cgt_annual_exclusion  # R40,000
    
    # Apply annual exclusion
    gain_after_exclusion = MAX(capital_gain - annual_exclusion, 0)
    
    # Apply inclusion rate (40%)
    inclusion_rate = 0.40
    taxable_capital_gain = gain_after_exclusion * inclusion_rate
    
    # This taxable gain is added to income and taxed at marginal rate
    combined_taxable_income = taxable_income + taxable_capital_gain
    
    # Calculate tax on combined income
    tax_on_combined = calculate_sa_income_tax(
      combined_taxable_income,
      tax_year,
      age_group
    ).tax_payable
    
    # Calculate tax on income only
    tax_on_income_only = calculate_sa_income_tax(
      taxable_income,
      tax_year,
      age_group
    ).tax_payable
    
    # CGT is the difference
    cgt = tax_on_combined - tax_on_income_only
    
    RETURN {
      capital_gain: capital_gain,
      annual_exclusion_used: MIN(capital_gain, annual_exclusion),
      gain_after_exclusion: gain_after_exclusion,
      inclusion_rate: inclusion_rate,
      taxable_capital_gain: taxable_capital_gain,
      cgt: cgt,
      effective_rate: (cgt / capital_gain) * 100 IF capital_gain > 0 ELSE 0
    }
  
  
  # ===== SA DIVIDEND TAX =====
  FUNCTION calculate_sa_dividend_tax(
    dividend_income: decimal,
    dividend_type: enum['LOCAL', 'FOREIGN'],
    tax_year: string
  ) -> SaDividendTaxResult:
    
    config = get_sa_tax_config(tax_year)
    
    # SA Dividend Tax (2024/25):
    # Local dividends: 20% Dividends Tax (withheld at source)
    # Foreign dividends: Included in income, taxed at marginal rate
    
    IF dividend_type = 'LOCAL':
      # Dividends Tax withheld at source (20%)
      dividend_tax = dividend_income * 0.20
      net_dividend = dividend_income - dividend_tax
      
      # Exemptions (first R23,800 exempt for individuals under 65)
      # But this is interest exemption, not dividend
      # Dividends Tax applies regardless
      
      RETURN {
        gross_dividend: dividend_income,
        dividend_tax_rate: 0.20,
        dividend_tax_withheld: dividend_tax,
        net_dividend: net_dividend,
        included_in_taxable_income: FALSE
      }
    
    ELSE:  # FOREIGN
      # Foreign dividends included in taxable income
      # Taxed at marginal rate
      # May qualify for foreign tax credit under DTA
      
      RETURN {
        gross_dividend: dividend_income,
        included_in_taxable_income: TRUE,
        taxed_at_marginal_rate: TRUE,
        foreign_tax_credit_may_apply: TRUE
      }
  
  
  # ===== HELPER FUNCTIONS =====
  
  FUNCTION determine_marginal_rate(income: decimal, bands: array) -> decimal:
    # Find which band the next £1 of income falls into
    cumulative = 0
    FOR EACH band IN bands:
      IF income <= band.upper_limit:
        RETURN band.rate
      cumulative = band.upper_limit
    RETURN bands[last].rate
  
  
  FUNCTION get_uk_tax_config(tax_year: string) -> UkTaxConfig:
    # Retrieve tax configuration for specified year
    # Versioned in database
    RETURN db.query("SELECT * FROM uk_tax_config WHERE tax_year = ?", tax_year)
  
  
  FUNCTION get_sa_tax_config(tax_year: string) -> SaTaxConfig:
    # Retrieve SA tax configuration for specified year
    RETURN db.query("SELECT * FROM sa_tax_config WHERE tax_year = ?", tax_year)


# ===== COMPOSITE TAX CALCULATION =====
FUNCTION calculate_total_tax_liability(
  user_id: uuid,
  tax_year: string
) -> CompleteTaxLiabilityResult:
  
  # Gather all user income sources
  income_sources = get_user_income(user_id, tax_year)
  
  # UK Tax Calculations
  uk_employment_income = SUM(income WHERE source_country = 'UK' AND type = 'EMPLOYMENT')
  uk_self_employment_income = SUM(income WHERE source_country = 'UK' AND type = 'SELF_EMPLOYMENT')
  uk_rental_income = SUM(income WHERE source_country = 'UK' AND type = 'RENTAL')
  uk_pension_income = SUM(income WHERE source_country = 'UK' AND type = 'PENSION')
  uk_dividend_income = SUM(income WHERE source_country = 'UK' AND type = 'DIVIDEND')
  uk_interest_income = SUM(income WHERE source_country = 'UK' AND type = 'INTEREST')
  
  # Calculate UK Income Tax
  total_uk_income = uk_employment_income + uk_self_employment_income + 
                    uk_rental_income + uk_pension_income
  
  uk_income_tax = calculate_uk_income_tax(total_uk_income, tax_year, FALSE)
  
  # Calculate UK NI
  uk_ni = calculate_uk_national_insurance(uk_employment_income, tax_year, 'EMPLOYED')
  
  # Calculate UK Dividend Tax
  uk_dividend_tax = calculate_uk_dividend_tax(
    uk_dividend_income,
    tax_year,
    total_uk_income,
    37700 - total_uk_income  # Basic rate band remaining
  )
  
  # Calculate UK CGT (if any capital gains)
  uk_capital_gains = get_user_capital_gains(user_id, tax_year, 'UK')
  uk_cgt = calculate_uk_capital_gains_tax(
    uk_capital_gains,
    'OTHER',
    tax_year,
    total_uk_income,
    37700 - total_uk_income
  )
  
  # SA Tax Calculations
  sa_employment_income = SUM(income WHERE source_country = 'SA' AND type = 'EMPLOYMENT')
  sa_dividend_income = SUM(income WHERE source_country = 'SA' AND type = 'DIVIDEND')
  sa_interest_income = SUM(income WHERE source_country = 'SA' AND type = 'INTEREST')
  
  total_sa_taxable_income = sa_employment_income + sa_interest_income
  
  sa_income_tax = calculate_sa_income_tax(total_sa_taxable_income, tax_year, 'UNDER_65')
  
  # SA Dividend Tax (withheld at source for local dividends)
  sa_dividend_tax = calculate_sa_dividend_tax(sa_dividend_income, 'LOCAL', tax_year)
  
  # SA CGT
  sa_capital_gains = get_user_capital_gains(user_id, tax_year, 'SA')
  sa_cgt = calculate_sa_capital_gains_tax(sa_capital_gains, tax_year, total_sa_taxable_income)
  
  # Apply DTA relief (if applicable)
  dta_relief = calculate_dta_relief(user_id, uk_taxes, sa_taxes)
  
  RETURN {
    uk_taxes: {
      income_tax: uk_income_tax.total_tax,
      national_insurance: uk_ni.total_ni,
      dividend_tax: uk_dividend_tax.total_tax,
      capital_gains_tax: uk_cgt.total_cgt,
      total: uk_income_tax.total_tax + uk_ni.total_ni + uk_dividend_tax.total_tax + uk_cgt.total_cgt
    },
    sa_taxes: {
      income_tax: sa_income_tax.tax_payable,
      dividend_tax: sa_dividend_tax.dividend_tax_withheld,
      capital_gains_tax: sa_cgt.cgt,
      total: sa_income_tax.tax_payable + sa_dividend_tax.dividend_tax_withheld + sa_cgt.cgt
    },
    dta_relief: dta_relief,
    total_tax_liability: (uk_taxes.total - dta_relief.uk_credit) + 
                        (sa_taxes.total - dta_relief.sa_credit)
  }
API Endpoints:
# UK Tax Calculations
POST /api/v1/tax/uk/income-tax
POST /api/v1/tax/uk/national-insurance
POST /api/v1/tax/uk/capital-gains-tax
POST /api/v1/tax/uk/dividend-tax

# SA Tax Calculations
POST /api/v1/tax/sa/income-tax
POST /api/v1/tax/sa/capital-gains-tax
POST /api/v1/tax/sa/dividend-tax

# Composite Calculations
POST /api/v1/tax/calculate-total-liability
POST /api/v1/tax/compare-scenarios

# Tax Configuration
GET /api/v1/tax/config/uk/{taxYear}
GET /api/v1/tax/config/sa/{taxYear}

# Tax Planning
POST /api/v1/tax/optimization-analysis
POST /api/v1/tax/marginal-rate-calculator
Data Models:
TABLE: uk_tax_config
- tax_year: VARCHAR(7) (PK) (e.g., '2024/25')
- personal_allowance: DECIMAL(10,2)
- basic_rate_band_upper: DECIMAL(10,2)
- higher_rate_band_upper: DECIMAL(10,2)
- basic_rate: DECIMAL(5,4)
- higher_rate: DECIMAL(5,4)
- additional_rate: DECIMAL(5,4)
- cgt_annual_exemption: DECIMAL(10,2)
- cgt_basic_rate_other: DECIMAL(5,4)
- cgt_higher_rate_other: DECIMAL(5,4)
- cgt_basic_rate_property: DECIMAL(5,4)
- cgt_higher_rate_property: DECIMAL(5,4)
- dividend_allowance: DECIMAL(10,2)
- dividend_basic_rate: DECIMAL(5,4)
- dividend_higher_rate: DECIMAL(5,4)
- dividend_additional_rate: DECIMAL(5,4)
- ni_primary_threshold: DECIMAL(10,2)
- ni_upper_earnings_limit: DECIMAL(10,2)
- ni_class_1_rate: DECIMAL(5,4)
- ni_class_1_additional_rate: DECIMAL(5,4)
- effective_from: DATE
- effective_to: DATE

TABLE: scottish_income_tax_bands
- tax_year: VARCHAR(7) (FK to uk_tax_config)
- band_order: INTEGER
- band_name: VARCHAR(50)
- lower_limit: DECIMAL(10,2)
- upper_limit: DECIMAL(10,2)
- rate: DECIMAL(5,4)

TABLE: sa_tax_config
- tax_year: VARCHAR(9) (PK) (e.g., '2024/2025')
- primary_rebate: DECIMAL(10,2)
- secondary_rebate: DECIMAL(10,2)
- tertiary_rebate: DECIMAL(10,2)
- interest_exemption_under_65: DECIMAL(10,2)
- interest_exemption_65_plus: DECIMAL(10,2)
- cgt_annual_exclusion: DECIMAL(10,2)
- cgt_inclusion_rate: DECIMAL(5,4)
- dividend_tax_rate: DECIMAL(5,4)
- medical_tax_credit: DECIMAL(10,2)
- effective_from: DATE
- effective_to: DATE

TABLE: sa_income_tax_bands
- tax_year: VARCHAR(9) (FK to sa_tax_config)
- band_order: INTEGER
- band_name: VARCHAR(50)
- lower_limit: DECIMAL(15,2)
- upper_limit: DECIMAL(15,2)
- rate: DECIMAL(5,4)

TABLE: tax_calculations
- id: UUID (PK)
- user_id: UUID (FK to users)
- calculation_type: ENUM('UK_INCOME_TAX', 'SA_INCOME_TAX', 'UK_CGT', 'SA_CGT', etc.)
- tax_year: VARCHAR(10)
- input_data: JSON
- calculation_result: JSON
- calculated_at: TIMESTAMP
- calculation_version: VARCHAR(10)

INDEX on tax_calculations(user_id, tax_year, calculation_type)
INDEX on uk_tax_config(tax_year)
INDEX on sa_tax_config(tax_year)
Error Handling:
ERROR CASES:
1. Tax year configuration not found
   - Response: 404 Not Found
   - Message: "Tax configuration for year {year} not available"
   
2. Negative income value
   - Response: 400 Bad Request
   - Message: "Income cannot be negative. Use losses/deductions separately"
   
3. Invalid tax year format
   - Response: 400 Bad Request
   - Message: "Invalid tax year format. Use 'YYYY/YY' for UK or 'YYYY/YYYY' for SA"
   
4. Historical calculation with unavailable rates
   - Response: 404 Not Found
   - Message: "Tax rates for {year} not available in system"

EDGE CASES:
- Income exactly at band threshold: Apply higher rate to next £1
- Personal allowance fully tapered: Calculate without allowance
- Zero income: Return zero tax, full allowances unused
- Income above additional rate threshold: All excess at top rate
- Scottish resident with mixed income: Apply Scottish rates to earned income only
- Non-resident with UK income: Different tax treatment
- Savings starting rate: First £5,000 at 0% if income low enough
- Marriage allowance transfer: 10% of personal allowance transferable
Performance Considerations:
•	All calculations stateless: No database dependency during calc
•	Tax config cached in memory: <5ms lookup
•	Single calculation: Target <50ms
•	Batch calculations: Optimize for bulk processing
•	Precision: Use Decimal type, avoid floating point
•	Audit trail: Log all calculations asynchronously
•	Historical calculations: Pre-load tax configs for common years
 
Feature 9.2: Double Tax Agreement (DTA) Relief Calculator
Feature Name: UK-SA Double Tax Agreement Relief Application
User Story: As a user with income or assets in both UK and SA, I need the system to automatically calculate Double Tax Agreement relief so that I don't pay tax twice on the same income or gains.
Acceptance Criteria:
•	Identify income/gains taxed in both jurisdictions
•	Apply UK-SA DTA provisions correctly
•	Calculate foreign tax credit
•	Determine which country has primary taxing rights
•	Apply tie-breaker rules for dual residents
•	Handle different income types (employment, business, dividends, interest, pensions, capital gains)
•	Show relief calculation breakdown
•	Integration with tax calculation engine
Technical Requirements:
•	DTA rules engine
•	Source vs residence taxation logic
•	Foreign tax credit calculator
•	Tie-breaker rules for dual residency
•	Income categorization by DTA article
•	Relief limitation calculator (cannot exceed tax on that income)
Constraints:
•	UK-SA DTA: Effective from 2002
•	Relief limited to lower of: tax paid abroad or tax due in residence country
•	Different rules for different income types
•	Residency determined by DTA tie-breaker if dual resident
•	Must track which country taxes first (source vs residence)
Implementation Approach:
SERVICE: DtaReliefCalculator

FUNCTION calculate_dta_relief(
  user: User,
  income_items: array[IncomeItem],
  tax_year: string
) -> DtaReliefResult:
  
  # 1. Determine tax residency under DTA
  dta_residence = determine_dta_residence(user)
  
  # 2. Categorize income by DTA treatment
  categorized_income = categorize_income_by_dta_article(income_items)
  
  # 3. Calculate relief for each income type
  relief_by_income_type = []
  
  FOR EACH income_category IN categorized_income:
    relief = calculate_relief_for_category(
      income_category,
      dta_residence,
      user.uk_tax_resident,
      user.sa_tax_resident
    )
    relief_by_income_type.append(relief)
  
  # 4. Aggregate total relief
  total_uk_relief = SUM(relief_by_income_type WHERE relief_country = 'UK')
  total_sa_relief = SUM(relief_by_income_type WHERE relief_country = 'SA')
  
  RETURN {
    dta_residence_determination: dta_residence,
    relief_by_income_type: relief_by_income_type,
    total_uk_foreign_tax_credit: total_uk_relief,
    total_sa_foreign_tax_credit: total_sa_relief,
    net_tax_saving: total_uk_relief + total_sa_relief
  }


FUNCTION determine_dta_residence(user: User) -> DtaResidenceResult:
  # UK-SA DTA Article 4: Residence tie-breaker rules
  
  IF NOT user.uk_tax_resident AND NOT user.sa_tax_resident:
    RETURN {residence: 'NEITHER', reason: 'Not resident in either country'}
  
  IF user.uk_tax_resident AND NOT user.sa_tax_resident:
    RETURN {residence: 'UK', reason: 'UK resident only'}
  
  IF user.sa_tax_resident AND NOT user.uk_tax_resident:
    RETURN {residence: 'SA', reason: 'SA resident only'}
  
  # Dual resident - apply tie-breaker rules
  IF user.uk_tax_resident AND user.sa_tax_resident:
    # Article 4(2) tie-breaker cascade:
    
    # (a) Permanent home available
    IF has_permanent_home_in('UK') AND NOT has_permanent_home_in('SA'):
      RETURN {residence: 'UK', reason: 'Permanent home in UK only'}
    
    IF has_permanent_home_in('SA') AND NOT has_permanent_home_in('UK'):
      RETURN {residence: 'SA', reason: 'Permanent home in SA only'}
    
    # (b) Centre of vital interests (stronger personal/economic ties)
    IF has_permanent_home_in('UK') AND has_permanent_home_in('SA'):
      IF centre_of_vital_interests = 'UK':
        RETURN {residence: 'UK', reason: 'Centre of vital interests in UK'}
      ELSE IF centre_of_vital_interests = 'SA':
        RETURN {residence: 'SA', reason: 'Centre of vital interests in SA'}
    
    # (c) Habitual abode (where person normally lives)
    IF habitual_abode_country = 'UK':
      RETURN {residence: 'UK', reason: 'Habitual abode in UK'}
    ELSE IF habitual_abode_country = 'SA':
      RETURN {residence: 'SA', reason: 'Habitual abode in SA'}
    
    # (d) Nationality
    IF user.nationality = 'UK' AND user.nationality != 'SA':
      RETURN {residence: 'UK', reason: 'UK national'}
    ELSE IF user.nationality = 'SA' AND user.nationality != 'UK':
      RETURN {residence: 'SA', reason: 'SA national'}
    
    # (e) Mutual agreement procedure
    RETURN {
      residence: 'UNDETERMINED',
      reason: 'Requires mutual agreement between UK and SA tax authorities',
      action_required: 'Contact tax advisor'
    }


FUNCTION categorize_income_by_dta_article(
  income_items: array[IncomeItem]
) -> array[CategorizedIncome]:
  
  categorized = []
  
  FOR EACH income IN income_items:
    category = {
      income: income,
      dta_article: determine_dta_article(income.type),
      taxing_rights: determine_taxing_rights(income),
      relief_method: determine_relief_method(income)
    }
    categorized.append(category)
  
  RETURN categorized


FUNCTION determine_dta_article(income_type: string) -> integer:
  # Map income types to DTA articles
  MATCH income_type:
    CASE 'EMPLOYMENT':
      RETURN 15  # Article 15: Employment income
    CASE 'SELF_EMPLOYMENT':
      RETURN 7   # Article 7: Business profits
    CASE 'DIVIDEND':
      RETURN 10  # Article 10: Dividends
    CASE 'INTEREST':
      RETURN 11  # Article 11: Interest
    CASE 'ROYALTY':
      RETURN 12  # Article 12: Royalties
    CASE 'PENSION':
      RETURN 17  # Article 17: Pensions
    CASE 'GOVERNMENT_SERVICE':
      RETURN 19  # Article 19: Government service
    CASE 'CAPITAL_GAIN':
      RETURN 13  # Article 13: Capital gains
    DEFAULT:
      RETURN 21  # Article 21: Other income


FUNCTION determine_taxing_rights(income: IncomeItem) -> TaxingRights:
  # Determine which country can tax under DTA
  
  dta_article = determine_dta_article(income.type)
  
  MATCH dta_article:
    
    CASE 7:  # Business profits
      # Taxable only in residence country unless PE in source country
      IF income.has_permanent_establishment_in_source_country:
        RETURN {
          source_country_can_tax: TRUE,
          residence_country_can_tax: TRUE,
          primary_taxing_rights: 'SOURCE'
        }
      ELSE:
        RETURN {
          source_country_can_tax: FALSE,
          residence_country_can_tax: TRUE,
          primary_taxing_rights: 'RESIDENCE'
        }
    
    CASE 10:  # Dividends
      # Both can tax, but source limited to 15% (10% if >10% shareholding)
      IF income.shareholding_percentage >= 10:
        source_country_rate_limit = 0.10
      ELSE:
        source_country_rate_limit = 0.15
      
      RETURN {
        source_country_can_tax: TRUE,
        source_country_rate_limit: source_country_rate_limit,
        residence_country_can_tax: TRUE,
        primary_taxing_rights: 'SOURCE',
        relief_method: 'CREDIT'
      }
    
    CASE 11:  # Interest
      # Both can tax, but source limited to 10%
      RETURN {
        source_country_can_tax: TRUE,
        source_country_rate_limit: 0.10,
        residence_country_can_tax: TRUE,
        primary_taxing_rights: 'SOURCE',
        relief_method: 'CREDIT'
      }
    
    CASE 13:  # Capital gains
      # Immovable property: Taxed in country where situated
      # Moveable property of PE: Taxed in PE country
      # Shares: Taxed in residence country
      # Other: Taxed in residence country
      
      IF income.asset_type = 'IMMOVABLE_PROPERTY':
        RETURN {
          source_country_can_tax: TRUE,
          residence_country_can_tax: TRUE,
          primary_taxing_rights: 'SOURCE'
        }
      ELSE IF income.asset_type = 'SHARES_DERIVING_VALUE_FROM_PROPERTY':
        # Shares deriving >50% value from immovable property
        RETURN {
          source_country_can_tax: TRUE,
          residence_country_can_tax: TRUE,
          primary_taxing_rights: 'SOURCE'
        }
      ELSE:
        RETURN {
          source_country_can_tax: FALSE,
          residence_country_can_tax: TRUE,
          primary_taxing_rights: 'RESIDENCE'
        }
    
    CASE 15:  # Employment income
      # Taxed in country where employment exercised
      # Exceptions if: <183 days, paid by non-resident employer, no PE
      
      IF income.days_worked_in_source < 183 AND 
         income.employer_not_resident_in_source AND
         income.not_borne_by_pe_in_source:
        # Exempt in source country
        RETURN {
          source_country_can_tax: FALSE,
          residence_country_can_tax: TRUE,
          primary_taxing_rights: 'RESIDENCE'
        }
      ELSE:
        RETURN {
          source_country_can_tax: TRUE,
          residence_country_can_tax: TRUE,
          primary_taxing_rights: 'SOURCE'
        }
    
    CASE 17:  # Pensions
      # Private pensions: Taxed only in residence country
      # Government pensions: Taxed in source country (unless national of other state)
      
      IF income.pension_type = 'GOVERNMENT':
        IF income.beneficiary_national_of_residence_country:
          RETURN {
            source_country_can_tax: FALSE,
            residence_country_can_tax: TRUE,
            primary_taxing_rights: 'RESIDENCE'
          }
        ELSE:
          RETURN {
            source_country_can_tax: TRUE,
            residence_country_can_tax: FALSE,
            primary_taxing_rights: 'SOURCE'
          }
      ELSE:  # Private pension
        RETURN {
          source_country_can_tax: FALSE,
          residence_country_can_tax: TRUE,
          primary_taxing_rights: 'RESIDENCE'
        }


FUNCTION calculate_relief_for_category(
  income_category: CategorizedIncome,
  dta_residence: string,
  uk_tax_resident: boolean,
  sa_tax_resident: boolean
) -> ReliefCalculation:
  
  income = income_category.income
  taxing_rights = income_category.taxing_rights
  
  # Calculate tax in source country
  IF income.source_country = 'UK':
    source_tax = calculate_uk_tax_on_income(income)
  ELSE IF income.source_country = 'SA':
    source_tax = calculate_sa_tax_on_income(income)
  
  # Calculate tax in residence country
  IF dta_residence = 'UK':
    residence_tax = calculate_uk_tax_on_income(income)
    relief_country = 'UK'
  ELSE IF dta_residence = 'SA':
    residence_tax = calculate_sa_tax_on_income(income)
    relief_country = 'SA'
  
  # Determine relief
  IF taxing_rights.primary_taxing_rights = 'SOURCE':
    # Source country taxes first
    # Residence country gives credit
    
    foreign_tax_paid = source_tax
    
    # Relief limited to lower of: foreign tax or domestic tax on that income
    relief_amount = MIN(foreign_tax_paid, residence_tax)
    
    RETURN {
      income_description: income.description,
      income_amount: income.amount,
      source_country: income.source_country,
      source_country_tax: source_tax,
      residence_country: dta_residence,
      residence_country_tax_before_relief: residence_tax,
      foreign_tax_credit: relief_amount,
      residence_country_tax_after_relief: MAX(residence_tax - relief_amount, 0),
      relief_given_by: relief_country,
      net_tax_on_income: source_tax + (residence_tax - relief_amount)
    }
  
  ELSE IF taxing_rights.primary_taxing_rights = 'RESIDENCE':
    # Only residence country taxes
    # No relief needed
    
    RETURN {
      income_description: income.description,
      income_amount: income.amount,
      taxed_in: dta_residence,
      tax_amount: residence_tax,
      foreign_tax_credit: 0,
      no_relief_needed: TRUE
    }


FUNCTION calculate_uk_tax_on_income(income: IncomeItem) -> decimal:
  # Calculate UK tax on specific income item
  # Use appropriate UK tax calculation based on income type
  
  MATCH income.type:
    CASE 'EMPLOYMENT', 'SELF_EMPLOYMENT', 'PENSION':
      result = calculate_uk_income_tax(income.amount, income.tax_year, FALSE)
      RETURN result.total_tax
    
    CASE 'DIVIDEND':
      result = calculate_uk_dividend_tax(income.amount, income.tax_year, 0, 37700)
      RETURN result.total_tax
    
    CASE 'INTEREST':
      # Interest taxed as income at marginal rate
      result = calculate_uk_income_tax(income.amount, income.tax_year, FALSE)
      RETURN result.total_tax
    
    CASE 'CAPITAL_GAIN':
      result = calculate_uk_capital_gains_tax(income.amount, 'OTHER', income.tax_year, 0, 37700)
      RETURN result.total_cgt


FUNCTION calculate_sa_tax_on_income(income: IncomeItem) -> decimal:
  # Calculate SA tax on specific income item
  
  MATCH income.type:
    CASE 'EMPLOYMENT', 'SELF_EMPLOYMENT', 'PENSION', 'INTEREST':
      result = calculate_sa_income_tax(income.amount, income.tax_year, 'UNDER_65')
      RETURN result.tax_payable
    
    CASE 'DIVIDEND':
      result = calculate_sa_dividend_tax(income.amount, 'FOREIGN', income.tax_year)
      # Foreign dividends taxed at marginal rate
      # Approximate using income tax calculation
      result = calculate_sa_income_tax(income.amount, income.tax_year, 'UNDER_65')
      RETURN result.tax_payable
    
    CASE 'CAPITAL_GAIN':
      result = calculate_sa_capital_gains_tax(income.amount, income.tax_year, 0)
      RETURN result.cgt
API Endpoints:
POST /api/v1/tax/dta/calculate-relief
POST /api/v1/tax/dta/determine-residence
POST /api/v1/tax/dta/categorize-income
GET /api/v1/tax/dta/treaty-provisions/{article}
POST /api/v1/tax/dta/foreign-tax-credit
Data Models:
TABLE: dta_provisions
- id: UUID (PK)
- treaty: VARCHAR(50) DEFAULT 'UK_SA'
- article_number: INTEGER
- article_title: VARCHAR(255)
- provision_text: TEXT
- income_type: VARCHAR(100)
- source_taxing_rights: BOOLEAN
- residence_taxing_rights: BOOLEAN
- source_rate_limit: DECIMAL(5,4)
- relief_method: ENUM('CREDIT', 'EXEMPTION', 'DEDUCTION')
- effective_from: DATE
- effective_to: DATE

TABLE: dta_relief_calculations
- id: UUID (PK)
- user_id: UUID (FK to users)
- income_id: UUID (FK to user_income)
- tax_year: VARCHAR(10)
- dta_article: INTEGER
- source_country: ENUM('UK', 'SA')
- residence_country: ENUM('UK', 'SA')
- income_amount: DECIMAL(15,2)
- source_country_tax: DECIMAL(15,2)
- residence_country_tax_before_relief: DECIMAL(15,2)
- foreign_tax_credit: DECIMAL(15,2)
- residence_country_tax_after_relief: DECIMAL(15,2)
- relief_given_by: ENUM('UK', 'SA')
- calculation_date: TIMESTAMP

TABLE: dta_residence_determinations
- id: UUID (PK)
- user_id: UUID (FK to users)
- determination_date: DATE
- tax_year: VARCHAR(10)
- uk_tax_resident: BOOLEAN
- sa_tax_resident: BOOLEAN
- permanent_home_uk: BOOLEAN
- permanent_home_sa: BOOLEAN
- centre_of_vital_interests: ENUM('UK', 'SA', 'UNCLEAR')
- habitual_abode: ENUM('UK', 'SA', 'BOTH')
- nationality: VARCHAR(50)
- dta_residence_conclusion: ENUM('UK', 'SA', 'UNDETERMINED')
- tie_breaker_rule_applied: VARCHAR(100)
- reasoning: TEXT
- created_at: TIMESTAMP

INDEX on dta_relief_calculations(user_id, tax_year)
INDEX on dta_provisions(article_number, income_type)
Error Handling:
ERROR CASES:
1. Dual residence cannot be determined
   - Response: 200 OK with warning
   - Message: "DTA residence cannot be automatically determined. Manual review required"
   - Recommendation: "Contact tax advisor for mutual agreement procedure"
   
2. Income type not covered by DTA
   - Response: 400 Bad Request
   - Message: "Income type {type} not explicitly covered by UK-SA DTA"
   - Fallback: "Apply general 'Other Income' provisions (Article 21)"
   
3. Conflicting tax residence claims
   - Response: 409 Conflict
   - Message: "Tax residence conflict detected. Both countries may claim taxing rights"
   - Action: "Apply DTA tie-breaker rules"
   
4. Missing required information for DTA determination
   - Response: 400 Bad Request
   - Message: "Insufficient information to determine DTA treatment"
   - Required: "Please provide: {list of missing data}"

EDGE CASES:
- Triple residence (UK, SA, and third country): Not handled, manual review
- Income from third country: No DTA relief for UK-SA treaty
- Treaty shopping: Beneficial ownership requirements
- Permanent establishment determination: Complex, may need manual review
- Employment income split across countries: Apportion by days worked
- Pension from third country: DTA may not apply
- Government service pensions: Special rules apply
- Students and trainees: Special exemptions (Article 20)
- Artists and sportspersons: Special provisions (Article 16)
- Offshore structures: Anti-avoidance provisions
- Limitation of benefits clause: May restrict DTA access
 
Feature 9.3: Tax Residency Status Determination
Feature Name: Automated Tax Residency and Domicile Status Assessment
User Story: As a user with ties to multiple countries, I need the system to accurately determine my tax residency and domicile status so that I understand which tax rules apply to me.
Acceptance Criteria:
•	UK Statutory Residence Test (SRT) automation
•	SA Physical Presence Test automation
•	UK domicile status determination
•	Deemed domicile calculation (UK)
•	Split year treatment identification (UK)
•	Temporary non-residence rules (UK)
•	Residency history tracking
•	Tax certificate generation support
Technical Requirements:
•	Rules engine for SRT (complex logic)
•	Day counting algorithms
•	Tie-breaker logic
•	Historical residency tracking
•	Date-based calculations
•	Supporting documentation references
Constraints:
•	UK SRT: Based on days in UK, ties, and automatic tests
•	SA test: 91 days in current year + average 91 days over 5 years
•	Domicile: Long-term concept, difficult to change
•	Deemed domicile: 15 of last 20 years UK resident OR UK domicile of origin + 1 of last 2 years resident
•	Split year: Only applies in specific circumstances
Implementation Approach:
SERVICE: TaxResidencyDetermination

# ===== UK STATUTORY RESIDENCE TEST =====
FUNCTION calculate_uk_srt(
  user_id: uuid,
  tax_year: string,
  days_in_uk: integer,
  ties: UkTiesData
) -> UkSrtResult:
  
  # UK SRT has three parts:
  # 1. Automatic Overseas Test (definitely NOT resident)
  # 2. Automatic UK Test (definitely resident)
  # 3. Sufficient Ties Test (depends on days and ties)
  
  # Part 1: Automatic Overseas Test
  automatic_overseas = check_automatic_overseas_test(user_id, tax_year, days_in_uk)
  
  IF automatic_overseas.result = TRUE:
    RETURN {
      uk_resident: FALSE,
      determination_method: 'AUTOMATIC_OVERSEAS_TEST',
      test_met: automatic_overseas.test_met,
      days_in_uk: days_in_uk,
      reasoning: automatic_overseas.reasoning
    }
  
  # Part 2: Automatic UK Test
  automatic_uk = check_automatic_uk_test(user_id, tax_year, days_in_uk)
  
  IF automatic_uk.result = TRUE:
    RETURN {
      uk_resident: TRUE,
      determination_method: 'AUTOMATIC_UK_TEST',
      test_met: automatic_uk.test_met,
      days_in_uk: days_in_uk,
      reasoning: automatic_uk.reasoning
    }
  
  # Part 3: Sufficient Ties Test
  sufficient_ties = check_sufficient_ties_test(user_id, tax_year, days_in_uk, ties)
  
  RETURN {
    uk_resident: sufficient_ties.result,
    determination_method: 'SUFFICIENT_TIES_TEST',
    days_in_uk: days_in_uk,
    ties_count: sufficient_ties.ties_count,
    ties_needed: sufficient_ties.ties_needed,
    ties_detail: sufficient_ties.ties_detail,
    reasoning: sufficient_ties.reasoning
  }


FUNCTION check_automatic_overseas_test(
  user_id: uuid,
  tax_year: string,
  days_in_uk: integer
) -> AutomaticOverseasTestResult:
  
  # Test 1: Present in UK for fewer than 16 days
  IF days_in_uk < 16:
    RETURN {
      result: TRUE,
      test_met: 'FEWER_THAN_16_DAYS',
      reasoning: 'Present in UK for fewer than 16 days'
    }
  
  # Test 2: Not UK resident in all 3 preceding tax years AND present < 46 days
  was_non_resident_previous_3_years = check_previous_residence(user_id, 3)
  
  IF was_non_resident_previous_3_years AND days_in_uk < 46:
    RETURN {
      result: TRUE,
      test_met: 'NON_RESIDENT_3_YEARS_PLUS_UNDER_46_DAYS',
      reasoning: 'Non-resident in previous 3 years and present fewer than 46 days'
    }
  
  # Test 3: Full-time work abroad AND present < 91 days AND no more than 30 working days in UK
  full_time_work_abroad = check_full_time_work_abroad(user_id, tax_year)
  working_days_in_uk = get_working_days_in_uk(user_id, tax_year)
  
  IF full_time_work_abroad AND days_in_uk < 91 AND working_days_in_uk <= 30:
    RETURN {
      result: TRUE,
      test_met: 'FULL_TIME_WORK_ABROAD',
      reasoning: 'Full-time work abroad with fewer than 91 days in UK and no more than 30 working days'
    }
  
  RETURN {
    result: FALSE,
    reasoning: 'No automatic overseas test met'
  }


FUNCTION check_automatic_uk_test(
  user_id: uuid,
  tax_year: string,
  days_in_uk: integer
) -> AutomaticUkTestResult:
  
  # Test 1: Present in UK for 183 days or more
  IF days_in_uk >= 183:
    RETURN {
      result: TRUE,
      test_met: '183_DAYS_OR_MORE',
      reasoning: 'Present in UK for 183 days or more'
    }
  
  # Test 2: Only home in UK (or no home anywhere)
  home_status = check_home_status(user_id, tax_year)
  
  IF home_status.only_home_in_uk:
    IF home_status.present_in_home_for_at_least_30_days:
      RETURN {
        result: TRUE,
        test_met: 'ONLY_HOME_IN_UK',
        reasoning: 'Only home in UK and present for at least 30 days in tax year'
      }
  
  # Test 3: Full-time work in UK
  full_time_work_uk = check_full_time_work_uk(user_id, tax_year)
  
  IF full_time_work_uk.qualifies:
    RETURN {
      result: TRUE,
      test_met: 'FULL_TIME_WORK_UK',
      reasoning: 'Full-time work in UK for at least 365 days with no significant breaks'
    }
  
  RETURN {
    result: FALSE,
    reasoning: 'No automatic UK test met'
  }


FUNCTION check_sufficient_ties_test(
  user_id: uuid,
  tax_year: string,
  days_in_uk: integer,
  ties: UkTiesData
) -> SufficientTiesTestResult:
  
  # Five UK ties:
  # 1. Family tie: Spouse/civil partner or minor children resident in UK
  # 2. Accommodation tie: Available accommodation in UK (used during year)
  # 3. Work tie: 40+ days doing >3 hours work in UK
  # 4. 90-day tie: Spent 90+ days in UK in either of previous 2 tax years
  # 5. Country tie: Present in UK more than any other single country
  
  ties_count = 0
  ties_detail = []
  
  # Tie 1: Family
  IF ties.has_uk_resident_spouse OR ties.has_uk_resident_minor_children:
    ties_count += 1
    ties_detail.append({
      tie: 'FAMILY',
      met: TRUE,
      reason: 'Spouse or minor children resident in UK'
    })
  ELSE:
    ties_detail.append({tie: 'FAMILY', met: FALSE})
  
  # Tie 2: Accommodation
  IF ties.has_uk_accommodation_available AND ties.spent_at_least_one_night:
    ties_count += 1
    ties_detail.append({
      tie: 'ACCOMMODATION',
      met: TRUE,
      reason: 'UK accommodation available and used'
    })
  ELSE:
    ties_detail.append({tie: 'ACCOMMODATION', met: FALSE})
  
  # Tie 3: Work
  IF ties.uk_working_days >= 40:
    ties_count += 1
    ties_detail.append({
      tie: 'WORK',
      met: TRUE,
      reason: '40+ days working more than 3 hours in UK'
    })
  ELSE:
    ties_detail.append({tie: 'WORK', met: FALSE})
  
  # Tie 4: 90-day
  days_in_previous_years = get_days_in_previous_years(user_id, 2)
  IF days_in_previous_years[0] >= 90 OR days_in_previous_years[1] >= 90:
    ties_count += 1
    ties_detail.append({
      tie: '90_DAY',
      met: TRUE,
      reason: '90+ days in UK in one of previous 2 tax years'
    })
  ELSE:
    ties_detail.append({tie: '90_DAY', met: FALSE})
  
  # Tie 5: Country (only for "leavers" - UK resident in 1+ of previous 3 years)
  was_uk_resident_in_previous_3_years = check_previous_residence(user_id, 3)
  
  IF was_uk_resident_in_previous_3_years:
    IF ties.days_in_uk_greater_than_any_other_country:
      ties_count += 1
      ties_detail.append({
        tie: 'COUNTRY',
        met: TRUE,
        reason: 'More days in UK than any other single country'
      })
    ELSE:
      ties_detail.append({tie: 'COUNTRY', met: FALSE})
  ELSE:
    ties_detail.append({
      tie: 'COUNTRY',
      met: 'N/A',
      reason: 'Not a "leaver" - not UK resident in previous 3 years'
    })
  
  # Determine if sufficient ties
  # Different thresholds for "arrivers" vs "leavers"
  
  IF was_uk_resident_in_previous_3_years:
    # "Leaver" - lower thresholds
    IF days_in_uk < 16:
      ties_needed = 4  # 4 ties needed (impossible - max 4 ties apply)
    ELSE IF days_in_uk >= 16 AND days_in_uk <= 45:
      ties_needed = 4
    ELSE IF days_in_uk >= 46 AND days_in_uk <= 90:
      ties_needed = 3
    ELSE IF days_in_uk >= 91 AND days_in_uk <= 120:
      ties_needed = 2
    ELSE IF days_in_uk >= 121:
      ties_needed = 1
  ELSE:
    # "Arriver" - higher thresholds (country tie doesn't apply)
    IF days_in_uk < 46:
      ties_needed = 4  # 4 ties needed (impossible - max 4 ties for arrivers)
    ELSE IF days_in_uk >= 46 AND days_in_uk <= 90:
      ties_needed = 4
    ELSE IF days_in_uk >= 91 AND days_in_uk <= 120:
      ties_needed = 3
    ELSE IF days_in_uk >= 121:
      ties_needed = 2
  
  is_uk_resident = (ties_count >= ties_needed)
  
  RETURN {
    result: is_uk_resident,
    ties_count: ties_count,
    ties_needed: ties_needed,
    ties_detail: ties_detail,
    status: IF was_uk_resident_in_previous_3_years THEN 'LEAVER' ELSE 'ARRIVER',
    reasoning: IF is_uk_resident THEN 
                 "UK resident: {ties_count} ties, {ties_needed} needed" 
               ELSE 
                 "Not UK resident: {ties_count} ties, {ties_needed} needed"
  }


# ===== SA PHYSICAL PRESENCE TEST =====
FUNCTION calculate_sa_residence(
  user_id: uuid,
  tax_year: string,
  days_in_sa: integer
) -> SaResidenceResult:
  
  # SA Physical Presence Test:
  # Resident if:
  # 1. Physically present for > 91 days in current year, AND
  # 2. Physically present for > 91 days on average over current + previous 5 years
  # OR
  # 3. Ordinarily resident (habitual residence)
  
  # Test 1: Current year
  IF days_in_sa <= 91:
    RETURN {
      sa_resident: FALSE,
      determination_method: 'PHYSICAL_PRESENCE',
      days_current_year: days_in_sa,
      reasoning: 'Not present for more than 91 days in current year'
    }
  
  # Test 2: Average over 5 years
  days_previous_5_years = get_sa_days_previous_years(user_id, 5)
  total_days_6_years = days_in_sa + SUM(days_previous_5_years)
  average_days = total_days_6_years / 6
  
  IF average_days <= 91:
    RETURN {
      sa_resident: FALSE,
      determination_method: 'PHYSICAL_PRESENCE',
      days_current_year: days_in_sa,
      average_days_6_years: average_days,
      reasoning: 'Average days over 6 years (current + 5 previous) not more than 91'
    }
  
  # Both tests passed
  RETURN {
    sa_resident: TRUE,
    determination_method: 'PHYSICAL_PRESENCE',
    days_current_year: days_in_sa,
    days_by_year: days_previous_5_years,
    average_days_6_years: average_days,
    reasoning: 'Present more than 91 days current year AND average > 91 days over 6 years'
  }


# ===== UK DOMICILE DETERMINATION =====
FUNCTION determine_uk_domicile(
  user_id: uuid,
  current_date: date
) -> UkDomicileResult:
  
  user = get_user(user_id)
  
  # Domicile of Origin
  domicile_of_origin = user.domicile_of_origin
  
  # Current domicile (may have been changed by choice)
  current_domicile = user.current_domicile
  
  # UK Deemed Domicile (for IHT purposes)
  # Deemed domiciled if:
  # 1. UK resident for 15 of last 20 tax years, OR
  # 2. UK domicile of origin AND UK resident in 1 of previous 2 tax years
  
  residence_history = get_residence_history(user_id, 20)
  uk_resident_years = COUNT(residence_history WHERE uk_resident = TRUE)
  
  deemed_domicile_rule_1 = (uk_resident_years >= 15)
  
  previous_2_years = get_residence_history(user_id, 2)
  uk_resident_previous_2 = ANY(previous_2_years WHERE uk_resident = TRUE)
  
  deemed_domicile_rule_2 = (domicile_of_origin = 'UK' AND uk_resident_previous_2)
  
  is_deemed_domiciled = (deemed_domicile_rule_1 OR deemed_domicile_rule_2)
  
  RETURN {
    domicile_of_origin: domicile_of_origin,
    current_domicile: current_domicile,
    uk_deemed_domicile: is_deemed_domiciled,
    deemed_domicile_reason: IF deemed_domicile_rule_1 THEN
                              '15 of last 20 years UK resident'
                            ELSE IF deemed_domicile_rule_2 THEN
                              'UK domicile of origin + UK resident in previous 2 years'
                            ELSE
                              'N/A',
    uk_resident_years_in_last_20: uk_resident_years,
    for_iht_purposes: IF is_deemed_domiciled THEN
                       'Treated as UK domiciled - worldwide assets in scope'
                     ELSE IF current_domicile = 'UK' THEN
                       'UK domiciled - worldwide assets in scope'
                     ELSE
                       'Non-UK domiciled - only UK assets in scope (excluded property applies)'
  }


# ===== SPLIT YEAR TREATMENT =====
FUNCTION check_split_year_treatment(
  user_id: uuid,
  tax_year: string
) -> SplitYearResult:
  
  # Split year treatment applies in 8 specific cases:
  # Cases 1-3: Arriving in UK
  # Cases 4-8: Leaving UK
  
  # This is complex - simplified version
  
  residence_status = calculate_uk_srt(user_id, tax_year, days_in_uk, ties)
  
  IF NOT residence_status.uk_resident:
    RETURN {
      split_year_applies: FALSE,
      reasoning: 'Not UK resident - split year not relevant'
    }
  
  # Check for qualifying circumstances
  circumstances = analyze_split_year_circumstances(user_id, tax_year)
  
  IF circumstances.started_full_time_work_abroad:
    # Case 1: Starting full-time work abroad
    split_date = circumstances.departure_date
    
    RETURN {
      split_year_applies: TRUE,
      case: 'CASE_1_STARTING_FULL_TIME_WORK_ABROAD',
      split_date: split_date,
      uk_part: {from: tax_year_start, to: split_date},
      overseas_part: {from: split_date + 1, to: tax_year_end},
      reasoning: 'Started full-time work abroad'
    }
  
  IF circumstances.ceased_uk_residence_on_leaving:
    # Case 8: Ceasing to have a home in UK
    # ... other cases
    
  RETURN {
    split_year_applies: FALSE,
    reasoning: 'No qualifying circumstances for split year treatment'
  }
API Endpoints:
POST /api/v1/tax/residency/uk-srt
POST /api/v1/tax/residency/sa-physical-presence
POST /api/v1/tax/residency/uk-domicile
POST /api/v1/tax/residency/split-year-check
GET /api/v1/tax/residency/history/{userId}
POST /api/v1/tax/residency/day-count-calculator
Data Models:
TABLE: residency_determinations
- id: UUID (PK)
- user_id: UUID (FK to users)
- tax_year: VARCHAR(10)
- country: ENUM('UK', 'SA')
- determination_date: DATE
- days_in_country: INTEGER
- resident: BOOLEAN
- determination_method: VARCHAR(100)
- test_details: JSON
- reasoning: TEXT
- created_at: TIMESTAMP

TABLE: uk_srt_tie_data
- id: UUID (PK)
- user_id: UUID (FK to users)
- tax_year: VARCHAR(7)
- family_tie: BOOLEAN
- accommodation_tie: BOOLEAN
- work_tie: BOOLEAN
- ninety_day_tie: BOOLEAN
- country_tie: BOOLEAN
- ties_count: INTEGER
- uk_working_days: INTEGER
- accommodation_details: TEXT
- updated_at: TIMESTAMP

TABLE: day_count_records
- id: UUID (PK)
- user_id: UUID (FK to users)
- country: ENUM('UK', 'SA', 'OTHER')
- entry_date: DATE
- exit_date: DATE
- days_count: INTEGER
- purpose: VARCHAR(255)
- notes: TEXT
- created_at: TIMESTAMP

TABLE: domicile_history
- id: UUID (PK)
- user_id: UUID (FK to users)
- effective_from: DATE
- effective_to: DATE
- domicile_of_origin: VARCHAR(50)
- domicile_of_choice: VARCHAR(50)
- deemed_domicile_uk: BOOLEAN
- reasoning: TEXT
- created_at: TIMESTAMP

INDEX on residency_determinations(user_id, tax_year, country)
INDEX on day_count_records(user_id, country, entry_date, exit_date)
Performance Considerations:
•	SRT calculation: Complex logic, cache result per tax year
•	Day counting: Optimize queries with date range indexes
•	Historical lookups: Pre-aggregate yearly totals
•	Tie determination: May require multiple sub-queries
•	Expected calculations: Once per tax year per user
•	Target: <500ms for complete SRT determination
 

10. AI ADVISORY ENGINE
Feature 10.1: Recommendation Generation System
Feature Name: Intelligent Financial Recommendations Based on User Context
User Story: As a user, I want to receive personalized, actionable financial recommendations based on my complete financial situation, goals, tax status, and life circumstances so that I can make informed decisions to improve my financial position.
Acceptance Criteria:
•	Generate recommendations across all modules (protection, savings, investment, retirement, IHT)
•	Prioritize recommendations by impact and urgency
•	Provide clear reasoning for each recommendation
•	Calculate estimated financial benefit (tax savings, returns, protection gap closure)
•	Consider user's risk tolerance and life stage
•	Avoid conflicting recommendations
•	Update recommendations when user data changes
•	Track recommendation acceptance and outcomes
Technical Requirements:
•	Rules engine for recommendation logic
•	Machine learning model for personalization (optional future)
•	Multi-criteria decision analysis for prioritization
•	Natural language generation for explanations
•	Integration with all financial modules
•	A/B testing framework for recommendation effectiveness
•	Recommendation versioning and audit trail
Constraints:
•	Must not provide regulated financial advice (information only)
•	Recommendations must be explainable (no black box)
•	Must consider user's complete situation (holistic)
•	Update frequency: Real-time on data change, daily batch for periodic checks
•	Maximum 20 active recommendations per user
•	Performance: Generate recommendations in <3 seconds
Implementation Approach:
SERVICE: RecommendationEngine

FUNCTION generate_recommendations(user_id: uuid) -> RecommendationSet:
  
  # 1. Gather complete user context
  context = build_user_context(user_id)
  
  # 2. Run all recommendation rules
  raw_recommendations = []
  
  # Protection recommendations
  raw_recommendations.extend(generate_protection_recommendations(context))
  
  # Savings recommendations
  raw_recommendations.extend(generate_savings_recommendations(context))
  
  # Investment recommendations
  raw_recommendations.extend(generate_investment_recommendations(context))
  
  # Retirement recommendations
  raw_recommendations.extend(generate_retirement_recommendations(context))
  
  # Tax optimization recommendations
  raw_recommendations.extend(generate_tax_recommendations(context))
  
  # IHT planning recommendations
  raw_recommendations.extend(generate_iht_recommendations(context))
  
  # Cross-cutting recommendations
  raw_recommendations.extend(generate_cross_cutting_recommendations(context))
  
  # 3. Score and prioritize
  scored_recommendations = score_recommendations(raw_recommendations, context)
  
  # 4. Filter and deduplicate
  filtered_recommendations = filter_recommendations(scored_recommendations, context)
  
  # 5. Rank by priority
  ranked_recommendations = rank_recommendations(filtered_recommendations)
  
  # 6. Limit to top N
  top_recommendations = ranked_recommendations[0:20]
  
  # 7. Generate explanations
  final_recommendations = generate_explanations(top_recommendations, context)
  
  # 8. Store recommendations
  store_recommendations(user_id, final_recommendations)
  
  RETURN {
    recommendations: final_recommendations,
    generated_at: NOW(),
    context_snapshot: context.summary,
    total_potential_benefit: SUM(final_recommendations.estimated_benefit)
  }


FUNCTION build_user_context(user_id: uuid) -> UserContext:
  
  user = get_user(user_id)
  
  RETURN {
    # Demographics
    age: calculate_age(user.date_of_birth),
    life_stage: determine_life_stage(user),
    dependents: get_dependents(user_id),
    
    # Financial position
    income: get_total_income(user_id),
    net_worth: get_net_worth(user_id),
    liquid_assets: get_liquid_assets(user_id),
    liabilities: get_total_liabilities(user_id),
    
    # Tax status
    uk_tax_resident: user.uk_tax_resident,
    sa_tax_resident: user.sa_tax_resident,
    domicile: user.domicile,
    marginal_tax_rate_uk: calculate_marginal_rate_uk(user_id),
    marginal_tax_rate_sa: calculate_marginal_rate_sa(user_id),
    
    # Module-specific
    protection: {
      life_cover: get_total_life_cover(user_id),
      critical_illness_cover: get_ci_cover(user_id),
      income_protection: get_income_protection(user_id)
    },
    
    savings: {
      emergency_fund: get_emergency_fund(user_id),
      isa_allowance_used: get_isa_allowance_used(user_id),
      tfsa_allowance_used: get_tfsa_allowance_used(user_id),
      total_cash: get_total_cash(user_id)
    },
    
    investments: {
      portfolio_value: get_portfolio_value(user_id),
      asset_allocation: get_asset_allocation(user_id),
      unrealized_gains: get_unrealized_gains(user_id),
      cgt_allowance_used: get_cgt_allowance_used(user_id)
    },
    
    retirement: {
      total_pension_pot: get_total_pension_pot(user_id),
      annual_allowance_used: get_annual_allowance_used(user_id),
      years_to_retirement: user.expected_retirement_age - calculate_age(user.date_of_birth),
      on_track: assess_retirement_readiness(user_id)
    },
    
    iht: {
      estate_value: get_estate_value(user_id),
      iht_liability: get_iht_liability(user_id),
      gifts_in_7_years: get_gifts_in_7_years(user_id),
      nrb_used: get_nrb_utilization(user_id)
    },
    
    # Goals and preferences
    goals: get_user_goals(user_id),
    risk_tolerance: user.risk_tolerance,
    investment_horizon: user.investment_horizon,
    
    # Behavioral
    recommendation_acceptance_rate: calculate_acceptance_rate(user_id),
    preferred_recommendation_types: get_preferred_types(user_id)
  }


# ===== PROTECTION RECOMMENDATIONS =====
FUNCTION generate_protection_recommendations(context: UserContext) -> array[Recommendation]:
  
  recommendations = []
  
  # Rule 1: Insufficient life cover
  recommended_life_cover = calculate_recommended_life_cover(context)
  current_life_cover = context.protection.life_cover
  
  IF current_life_cover < recommended_life_cover:
    gap = recommended_life_cover - current_life_cover
    
    recommendations.append({
      category: 'PROTECTION',
      type: 'INCREASE_LIFE_COVER',
      priority: 'HIGH',
      title: "Increase life cover to protect your family",
      description: "Your current life cover of £{current_life_cover} may not be sufficient. We recommend £{recommended_life_cover} based on your income, debts, and family needs.",
      estimated_benefit: {
        type: 'RISK_MITIGATION',
        description: "Protect your family's financial future",
        coverage_gap: gap
      },
      action_required: "Review life insurance options",
      reasoning: [
        "Current cover: £{current_life_cover}",
        "Recommended: £{recommended_life_cover}",
        "Based on: {calculation_factors}"
      ],
      urgency_score: 90,
      impact_score: 95
    })
  
  # Rule 2: No income protection with dependents
  IF context.protection.income_protection = 0 AND context.dependents.count > 0:
    
    recommendations.append({
      category: 'PROTECTION',
      type: 'ADD_INCOME_PROTECTION',
      priority: 'HIGH',
      title: "Consider income protection insurance",
      description: "You have {dependents} dependents but no income protection. This could help maintain your family's lifestyle if you're unable to work due to illness or injury.",
      estimated_benefit: {
        type: 'RISK_MITIGATION',
        description: "Protect {percentage}% of your income",
        monthly_benefit: context.income.monthly * 0.65
      },
      action_required: "Explore income protection policies",
      reasoning: [
        "You have {dependents} dependents",
        "No income protection in place",
        "Typical replacement: 65% of income"
      ],
      urgency_score: 80,
      impact_score: 85
    })
  
  # Rule 3: Life insurance not in trust (UK)
  IF context.uk_tax_resident:
    policies_not_in_trust = get_policies_not_in_trust(context.user_id)
    
    IF policies_not_in_trust.count > 0:
      total_value = SUM(policies_not_in_trust.cover_amount)
      potential_iht = total_value * 0.40
      
      recommendations.append({
        category: 'PROTECTION',
        type: 'WRITE_POLICY_IN_TRUST',
        priority: 'MEDIUM',
        title: "Write life insurance policies in trust",
        description: "You have {count} life insurance policies not written in trust. Writing them in trust would remove them from your estate for IHT purposes.",
        estimated_benefit: {
          type: 'TAX_SAVING',
          description: "Potential IHT saving",
          amount_gbp: potential_iht,
          currency: 'GBP'
        },
        action_required: "Contact insurers to set up trust arrangements",
        reasoning: [
          "{count} policies not in trust",
          "Total cover: £{total_value}",
          "Potential IHT at 40%: £{potential_iht}"
        ],
        urgency_score: 60,
        impact_score: 70
      })
  
  RETURN recommendations


# ===== SAVINGS RECOMMENDATIONS =====
FUNCTION generate_savings_recommendations(context: UserContext) -> array[Recommendation]:
  
  recommendations = []
  
  # Rule 1: Inadequate emergency fund
  recommended_emergency_fund = context.income.monthly * 6  # 6 months expenses
  current_emergency_fund = context.savings.emergency_fund
  
  IF current_emergency_fund < recommended_emergency_fund:
    shortfall = recommended_emergency_fund - current_emergency_fund
    
    recommendations.append({
      category: 'SAVINGS',
      type: 'BUILD_EMERGENCY_FUND',
      priority: 'HIGH',
      title: "Build up your emergency fund",
      description: "Your emergency fund is currently £{current} but we recommend £{recommended} (6 months of expenses).",
      estimated_benefit: {
        type: 'FINANCIAL_RESILIENCE',
        description: "Protection against unexpected expenses",
        target_amount: recommended_emergency_fund
      },
      action_required: "Set up regular savings of £{monthly_target} per month",
      monthly_target: shortfall / 12,  # Build over 12 months
      reasoning: [
        "Current emergency fund: £{current}",
        "Recommended: £{recommended} (6 months)",
        "Shortfall: £{shortfall}"
      ],
      urgency_score: 85,
      impact_score: 90
    })
  
  # Rule 2: Unused ISA allowance (UK)
  IF context.uk_tax_resident:
    isa_allowance = 20000  # 2024/25
    isa_used = context.savings.isa_allowance_used
    isa_remaining = isa_allowance - isa_used
    
    IF isa_remaining > 5000:  # Threshold for recommendation
      days_until_year_end = calculate_days_until_uk_tax_year_end()
      
      # Calculate potential tax saving
      assumed_return = 0.05  # 5% return assumption
      annual_return = isa_remaining * assumed_return
      tax_on_return = annual_return * context.marginal_tax_rate_uk
      
      recommendations.append({
        category: 'SAVINGS',
        type: 'USE_ISA_ALLOWANCE',
        priority: IF days_until_year_end < 60 THEN 'HIGH' ELSE 'MEDIUM',
        title: "Use your remaining ISA allowance",
        description: "You have £{isa_remaining} of unused ISA allowance for this tax year. ISA allowances don't carry forward.",
        estimated_benefit: {
          type: 'TAX_SAVING',
          description: "Tax-free returns on investment",
          annual_tax_saving: tax_on_return,
          currency: 'GBP'
        },
        action_required: "Transfer £{isa_remaining} to ISA before April 5",
        deadline: calculate_uk_tax_year_end(),
        reasoning: [
          "ISA allowance: £{isa_allowance}",
          "Used: £{isa_used}",
          "Remaining: £{isa_remaining}",
          "Tax year ends in {days} days"
        ],
        urgency_score: IF days_until_year_end < 60 THEN 90 ELSE 60,
        impact_score: 70
      })
  
  # Rule 3: Unused TFSA allowance (SA)
  IF context.sa_tax_resident:
    tfsa_annual_limit = 36000  # 2024/25
    tfsa_lifetime_limit = 500000
    tfsa_used_this_year = context.savings.tfsa_allowance_used.annual
    tfsa_lifetime_used = context.savings.tfsa_allowance_used.lifetime
    
    tfsa_annual_remaining = tfsa_annual_limit - tfsa_used_this_year
    tfsa_lifetime_remaining = tfsa_lifetime_limit - tfsa_lifetime_used
    
    IF tfsa_annual_remaining > 10000 AND tfsa_lifetime_remaining > tfsa_annual_remaining:
      days_until_year_end = calculate_days_until_sa_tax_year_end()
      
      recommendations.append({
        category: 'SAVINGS',
        type: 'USE_TFSA_ALLOWANCE',
        priority: IF days_until_year_end < 60 THEN 'HIGH' ELSE 'MEDIUM',
        title: "Maximize your Tax-Free Savings Account",
        description: "You have R{tfsa_annual_remaining} of unused TFSA allowance this year. TFSA returns are completely tax-free.",
        estimated_benefit: {
          type: 'TAX_SAVING',
          description: "Tax-free investment returns",
          currency: 'ZAR'
        },
        action_required: "Contribute to TFSA before February 28",
        deadline: calculate_sa_tax_year_end(),
        reasoning: [
          "Annual limit: R{tfsa_annual_limit}",
          "Used this year: R{tfsa_used_this_year}",
          "Remaining: R{tfsa_annual_remaining}",
          "Lifetime remaining: R{tfsa_lifetime_remaining}"
        ],
        urgency_score: IF days_until_year_end < 60 THEN 85 ELSE 55,
        impact_score: 65
      })
  
  RETURN recommendations


# ===== INVESTMENT RECOMMENDATIONS =====
FUNCTION generate_investment_recommendations(context: UserContext) -> array[Recommendation]:
  
  recommendations = []
  
  # Rule 1: Poor diversification
  allocation = context.investments.asset_allocation
  
  # Check for concentration risk
  IF allocation.equity > 90:
    recommendations.append({
      category: 'INVESTMENT',
      type: 'IMPROVE_DIVERSIFICATION',
      priority: 'MEDIUM',
      title: "Reduce concentration risk in your portfolio",
      description: "Your portfolio is {equity_pct}% equities. Consider diversifying across asset classes to reduce risk.",
      estimated_benefit: {
        type: 'RISK_REDUCTION',
        description: "Lower portfolio volatility"
      },
      action_required: "Rebalance portfolio to target allocation",
      reasoning: [
        "Current equity allocation: {equity_pct}%",
        "Recommended max for your risk profile: 80%",
        "Consider bonds, property, or cash"
      ],
      urgency_score: 50,
      impact_score: 60
    })
  
  # Rule 2: CGT harvesting opportunity (UK)
  IF context.uk_tax_resident:
    unrealized_gains = context.investments.unrealized_gains
    cgt_allowance = 3000  # 2024/25
    cgt_allowance_used = context.investments.cgt_allowance_used
    cgt_allowance_remaining = cgt_allowance - cgt_allowance_used
    
    IF unrealized_gains > 0 AND cgt_allowance_remaining > 1000:
      # Opportunity to harvest gains tax-free
      
      recommendations.append({
        category: 'INVESTMENT',
        type: 'CGT_HARVESTING',
        priority: 'MEDIUM',
        title: "Use your Capital Gains Tax allowance",
        description: "You have £{cgt_allowance_remaining} of unused CGT allowance. Consider selling and rebuying investments to 'realize' gains tax-free and reset the cost base.",
        estimated_benefit: {
          type: 'TAX_EFFICIENCY',
          description: "Future tax savings by resetting cost base",
          amount_gbp: cgt_allowance_remaining * 0.20  # Approx future saving
        },
        action_required: "Review portfolio for bed-and-breakfast opportunities",
        reasoning: [
          "Unrealized gains: £{unrealized_gains}",
          "CGT allowance remaining: £{cgt_allowance_remaining}",
          "Realize gains tax-free before April 5"
        ],
        urgency_score: 55,
        impact_score: 50
      })
  
  # Rule 3: Investment in GIA when ISA allowance available
  IF context.uk_tax_resident:
    gia_holdings = get_gia_holdings(context.user_id)
    isa_allowance_remaining = 20000 - context.savings.isa_allowance_used
    
    IF gia_holdings.value > 0 AND isa_allowance_remaining > 5000:
      
      # Calculate potential tax saving
      annual_return_assumption = gia_holdings.value * 0.06
      tax_on_return = annual_return_assumption * context.marginal_tax_rate_uk
      
      recommendations.append({
        category: 'INVESTMENT',
        type: 'TRANSFER_TO_ISA',
        priority: 'MEDIUM',
        title: "Transfer investments from GIA to ISA",
        description: "You have £{gia_value} in a General Investment Account that could be sheltered in an ISA.",
        estimated_benefit: {
          type: 'TAX_SAVING',
          description: "Annual tax saving on returns",
          amount_gbp: tax_on_return,
          currency: 'GBP'
        },
        action_required: "Consider 'Bed and ISA' to transfer holdings",
        reasoning: [
          "GIA holdings: £{gia_value}",
          "ISA allowance available: £{isa_allowance_remaining}",
          "Estimated annual tax saving: £{tax_on_return}"
        ],
        urgency_score: 50,
        impact_score: 60
      })
  
  # Rule 4: No EIS/SEIS investments for higher rate taxpayers (UK)
  IF context.uk_tax_resident AND context.marginal_tax_rate_uk >= 0.40:
    eis_seis_investments = get_eis_seis_investments(context.user_id)
    
    IF eis_seis_investments.total_value = 0 AND context.net_worth > 250000:
      
      recommendations.append({
        category: 'INVESTMENT',
        type: 'CONSIDER_EIS_SEIS',
        priority: 'LOW',
        title: "Consider EIS/SEIS investments for tax relief",
        description: "As a higher-rate taxpayer with substantial assets, EIS and SEIS investments offer attractive tax reliefs (30-50% income tax relief plus CGT exemptions).",
        estimated_benefit: {
          type: 'TAX_RELIEF',
          description: "Income tax relief + CGT benefits",
          potential_relief: "30-50% of investment"
        },
        action_required: "Speak with financial advisor about EIS/SEIS opportunities",
        warnings: [
          "High risk investments",
          "Illiquid - 3-5 year hold required",
          "Only suitable for experienced investors",
          "Loss of capital is possible"
        ],
        reasoning: [
          "Higher-rate taxpayer: {marginal_rate}%",
          "EIS: 30% income tax relief",
          "SEIS: 50% income tax relief",
          "CGT exemption after 3 years"
        ],
        urgency_score: 20,
        impact_score: 40
      })
  
  RETURN recommendations


# ===== RETIREMENT RECOMMENDATIONS =====
FUNCTION generate_retirement_recommendations(context: UserContext) -> array[Recommendation]:
  
  recommendations = []
  
  # Rule 1: Not on track for retirement
  IF NOT context.retirement.on_track:
    shortfall = calculate_retirement_shortfall(context)
    additional_monthly_contribution = calculate_required_monthly_contribution(shortfall, context.retirement.years_to_retirement)
    
    recommendations.append({
      category: 'RETIREMENT',
      type: 'INCREASE_PENSION_CONTRIBUTIONS',
      priority: 'HIGH',
      title: "Increase pension contributions to meet retirement goals",
      description: "Based on your retirement age of {target_age}, you're projected to have a shortfall of £{shortfall}. Increasing contributions by £{additional} per month would get you on track.",
      estimated_benefit: {
        type: 'RETIREMENT_ADEQUACY',
        description: "Close retirement savings gap",
        shortfall_closed: shortfall
      },
      action_required: "Increase pension contributions by £{additional}/month",
      monthly_increase: additional_monthly_contribution,
      reasoning: [
        "Current pension pot: £{current_pot}",
        "Projected at retirement: £{projected}",
        "Target: £{target}",
        "Shortfall: £{shortfall}",
        "Years to retirement: {years}"
      ],
      urgency_score: 80,
      impact_score: 90
    })
  
  # Rule 2: Unused pension annual allowance (UK)
  IF context.uk_tax_resident:
    annual_allowance = calculate_pension_annual_allowance(context)
    allowance_used = context.retirement.annual_allowance_used
    allowance_remaining = annual_allowance - allowance_used
    
    IF allowance_remaining > 10000:
      # Calculate tax relief
      tax_relief = allowance_remaining * context.marginal_tax_rate_uk
      
      recommendations.append({
        category: 'RETIREMENT',
        type: 'USE_PENSION_ALLOWANCE',
        priority: 'MEDIUM',
        title: "Maximize pension tax relief",
        description: "You have £{allowance_remaining} of unused pension annual allowance. Pension contributions receive tax relief at your marginal rate of {marginal_rate}%.",
        estimated_benefit: {
          type: 'TAX_RELIEF',
          description: "Tax relief on contributions",
          amount_gbp: tax_relief,
          currency: 'GBP'
        },
        action_required: "Consider additional pension contribution before April 5",
        reasoning: [
          "Annual allowance: £{annual_allowance}",
          "Used: £{allowance_used}",
          "Remaining: £{allowance_remaining}",
          "Tax relief at {marginal_rate}%: £{tax_relief}"
        ],
        urgency_score: 65,
        impact_score: 75
      })
  
  # Rule 3: Consider carry forward (UK)
  IF context.uk_tax_resident:
    carry_forward_available = calculate_carry_forward_available(context.user_id)
    
    IF carry_forward_available > 10000:
      
      recommendations.append({
        category: 'RETIREMENT',
        type: 'USE_CARRY_FORWARD',
        priority: 'MEDIUM',
        title: "Use pension carry forward allowance",
        description: "You have £{carry_forward} of unused allowance from previous years that you can carry forward for pension contributions.",
        estimated_benefit: {
          type: 'TAX_RELIEF',
          description: "Additional tax relief opportunity",
          amount_gbp: carry_forward_available * context.marginal_tax_rate_uk
        },
        action_required: "Consider one-off contribution using carry forward",
        reasoning: [
          "Carry forward from previous 3 years: £{carry_forward}",
          "Expires if not used",
          "Tax relief available: £{tax_relief}"
        ],
        urgency_score: 60,
        impact_score: 70
      })
  
  # Rule 4: Section 10C deduction not maximized (SA)
  IF context.sa_tax_resident:
    max_deductible = MIN(context.income.annual * 0.275, 350000)
    current_contributions = get_sa_retirement_contributions(context.user_id)
    deduction_unused = max_deductible - current_contributions
    
    IF deduction_unused > 20000:
      tax_saving = deduction_unused * context.marginal_tax_rate_sa
      
      recommendations.append({
        category: 'RETIREMENT',
        type: 'MAXIMIZE_SECTION_10C',
        priority: 'MEDIUM',
        title: "Maximize Section 10C retirement tax deduction",
        description: "You can deduct up to R{max_deductible} for retirement contributions (27.5% of income, max R350k). You have R{deduction_unused} unused.",
        estimated_benefit: {
          type: 'TAX_SAVING',
          description: "Tax saving on additional contributions",
          amount_zar: tax_saving,
          currency: 'ZAR'
        },
        action_required: "Increase retirement annuity contributions",
        reasoning: [
          "Maximum deductible: R{max_deductible}",
          "Current contributions: R{current_contributions}",
          "Unused: R{deduction_unused}",
          "Tax saving potential: R{tax_saving}"
        ],
        urgency_score: 60,
        impact_score: 70
      })
  
  # Rule 5: QROPS transfer consideration
  IF context.uk_tax_resident = FALSE AND context.sa_tax_resident = TRUE:
    uk_pensions = get_uk_pensions(context.user_id)
    
    IF uk_pensions.total_value > 50000:
      
      recommendations.append({
        category: 'RETIREMENT',
        type: 'CONSIDER_QROPS',
        priority: 'LOW',
        title: "Consider QROPS transfer to South Africa",
        description: "You have UK pensions worth £{uk_pension_value}. If you're permanently resident in SA, a QROPS transfer might provide benefits.",
        estimated_benefit: {
          type: 'FLEXIBILITY',
          description: "Currency matching and flexibility",
          considerations: [
            "Match pension to spending currency",
            "SA retirement rules may be more flexible",
            "Avoid UK IHT on pension death benefits"
          ]
        },
        action_required: "Speak with cross-border pension specialist",
        warnings: [
          "Complex area - professional advice essential",
          "Overseas Transfer Charge may apply (25%)",
          "HMRC reporting requirements",
          "Consider costs vs benefits carefully"
        ],
        reasoning: [
          "UK pension value: £{uk_pension_value}",
          "Resident in SA",
          "QROPS can provide currency matching"
        ],
        urgency_score: 30,
        impact_score: 50
      })
  
  RETURN recommendations


# ===== TAX OPTIMIZATION RECOMMENDATIONS =====
FUNCTION generate_tax_recommendations(context: UserContext) -> array[Recommendation]:
  
  recommendations = []
  
  # Rule 1: Personal allowance taper (UK)
  IF context.uk_tax_resident AND context.income.annual > 100000:
    excess = context.income.annual - 100000
    allowance_lost = excess / 2
    effective_tax_rate_on_excess = 0.60  # 40% tax + 40% from lost allowance
    
    # Pension contribution could reduce income below £100k
    contribution_needed = excess + 1000  # Slightly over to be safe
    tax_saved = contribution_needed * effective_tax_rate_on_excess
    
    recommendations.append({
      category: 'TAX',
      type: 'AVOID_ALLOWANCE_TAPER',
      priority: 'HIGH',
      title: "Avoid personal allowance taper with pension contribution",
      description: "Your income of £{income} triggers personal allowance taper. A pension contribution of £{contribution_needed} would save £{tax_saved} in tax (effective rate: 60%).",
      estimated_benefit: {
        type: 'TAX_SAVING',
        description: "Save tax and restore personal allowance",
        amount_gbp: tax_saved,
        currency: 'GBP'
      },
      action_required: "Make pension contribution to reduce adjusted net income below £100,000",
      reasoning: [
        "Income: £{income}",
        "Excess over £100k: £{excess}",
        "Personal allowance lost: £{allowance_lost}",
        "Effective tax rate: 60%"
      ],
      urgency_score: 85,
      impact_score: 90
    })
  
  # Rule 2: Marriage allowance (UK)
  IF context.uk_tax_resident:
    spouse = get_spouse(context.user_id)
    
    IF spouse EXISTS:
      user_uses_full_allowance = (context.income.annual > 12570)
      spouse_uses_full_allowance = (spouse.income.annual > 12570)
      
      IF user_uses_full_allowance XOR spouse_uses_full_allowance:
        # One uses full allowance, one doesn't - marriage allowance beneficial
        
        transferable_amount = 12570 * 0.10  # £1,257
        tax_saving = transferable_amount * 0.20  # £251
        
        recommendations.append({
          category: 'TAX',
          type: 'CLAIM_MARRIAGE_ALLOWANCE',
          priority: 'MEDIUM',
          title: "Claim Marriage Allowance",
          description: "You can transfer £{transferable} of unused personal allowance to your spouse, saving £{saving} per year.",
          estimated_benefit: {
            type: 'TAX_SAVING',
            description: "Annual tax saving",
            amount_gbp: tax_saving,
            currency: 'GBP'
          },
          action_required: "Apply via HMRC to transfer allowance",
          reasoning: [
            "One spouse not using full allowance",
            "10% transferable (£{transferable})",
            "Tax saving: £{saving}/year"
          ],
          urgency_score: 50,
          impact_score: 40
        })
  
  # Rule 3: Dividend tax planning
  IF context.uk_tax_resident AND context.investments.dividend_income > 500:
    dividend_allowance = 500  # 2024/25
    excess_dividends = context.investments.dividend_income - dividend_allowance
    
    IF excess_dividends > 0:
      # Could reduce dividends or move to ISA
      
      recommendations.append({
        category: 'TAX',
        type: 'DIVIDEND_TAX_PLANNING',
        priority: 'LOW',
        title: "Optimize dividend tax strategy",
        description: "You're paying dividend tax on £{excess} of dividends above the £500 allowance. Consider moving dividend-paying investments to an ISA.",
        estimated_benefit: {
          type: 'TAX_SAVING',
          description: "Avoid dividend tax",
          annual_saving: excess_dividends * 0.0875  # Basic rate
        },
        action_required: "Transfer dividend-paying investments to ISA",
        reasoning: [
          "Dividend income: £{dividend_income}",
          "Dividend allowance: £500",
          "Taxable: £{excess}",
          "Consider ISA wrapper"
        ],
        urgency_score: 40,
        impact_score: 45
      })
  
  RETURN recommendations


# ===== IHT PLANNING RECOMMENDATIONS =====
FUNCTION generate_iht_recommendations(context: UserContext) -> array[Recommendation]:
  
  recommendations = []
  
  # Rule 1: Significant IHT liability
  IF context.iht.iht_liability > 50000:
    
    recommendations.append({
      category: 'IHT',
      type: 'IHT_PLANNING_NEEDED',
      priority: 'HIGH',
      title: "Reduce Inheritance Tax liability",
      description: "Your estate has a projected IHT liability of £{iht_liability}. There are strategies to reduce this through gifting, trusts, and reliefs.",
      estimated_benefit: {
        type: 'TAX_SAVING',
        description: "Potential IHT reduction",
        amount_gbp: context.iht.iht_liability * 0.50  # Could reduce by 50%
      },
      action_required: "Consult estate planning specialist",
      suggested_strategies: [
        "Lifetime gifting (7-year rule)",
        "Write life insurance in trust",
        "Consider Business Property Relief assets",
        "Utilize spousal exemption",
        "Charitable giving (reduce rate to 36%)"
      ],
      reasoning: [
        "Estate value: £{estate_value}",
        "IHT liability: £{iht_liability}",
        "Multiple planning options available"
      ],
      urgency_score: 75,
      impact_score: 85
    })
  
  # Rule 2: Not using NRB efficiently (spouse)
  IF context.uk_tax_resident:
    spouse = get_spouse(context.user_id)
    
    IF spouse EXISTS:
      nrb_utilization = assess_nrb_utilization(context.user_id, spouse.id)
      
      IF nrb_utilization.inefficient:
        
        recommendations.append({
          category: 'IHT',
          type: 'EQUALIZE_ESTATES',
          priority: 'MEDIUM',
          title: "Equalize estates to use both NRBs",
          description: "Your estates are unbalanced. Equalizing can ensure both spouses' Nil Rate Bands (£325,000 each) are utilized effectively.",
          estimated_benefit: {
            type: 'TAX_EFFICIENCY',
            description: "Better use of allowances",
            potential_saving: "Up to £130,000"
          },
          action_required: "Review asset ownership and consider rebalancing",
          reasoning: [
            "Imbalanced estates",
            "Both NRBs should be utilized",
            "Transferable NRB available but not optimal"
          ],
          urgency_score: 55,
          impact_score: 65
        })
  
  # Rule 3: No RNRB planning (UK)
  IF context.uk_tax_resident:
    has_qualifying_residence = check_for_qualifying_residence(context.user_id)
    has_direct_descendants = (context.dependents.children > 0)
    
    IF NOT has_qualifying_residence AND has_direct_descendants:
      rnrb = 175000  # Additional IHT saving potential
      iht_saving = rnrb * 0.40
      
      recommendations.append({
        category: 'IHT',
        type: 'RNRB_PLANNING',
        priority: 'MEDIUM',
        title: "Consider Residence Nil Rate Band planning",
        description: "You have children but no qualifying residential property. Owning a qualifying residence that passes to descendants could save up to £{iht_saving} in IHT.",
        estimated_benefit: {
          type: 'TAX_SAVING',
          description: "Additional RNRB (£175,000)",
          amount_gbp: iht_saving
        },
        action_required: "Consider residential property ownership for RNRB",
        reasoning: [
          "RNRB available: £175,000",
          "Must own qualifying residence",
          "Must pass to direct descendants",
          "Potential IHT saving: £{iht_saving}"
        ],
        urgency_score: 50,
        impact_score: 60
      })
  
  # Rule 4: Gifts within 7 years approaching exempt status
  gifts_approaching_7_years = get_gifts_approaching_7_years(context.user_id, months_threshold: 12)
  
  IF gifts_approaching_7_years.count > 0:
    
    recommendations.append({
      category: 'IHT',
      type: 'GIFTS_BECOMING_EXEMPT',
      priority: 'INFO',
      title: "Gifts approaching 7-year exemption",
      description: "You have {count} gifts that will become fully exempt from IHT in the next 12 months (total value: £{total_value}).",
      estimated_benefit: {
        type: 'TAX_EXEMPTION',
        description: "Gifts becoming IHT-exempt",
        total_value: SUM(gifts_approaching_7_years.value)
      },
      action_required: "No action needed - informational",
      gifts_list: gifts_approaching_7_years,
      reasoning: [
        "{count} gifts approaching 7 years",
        "Will be fully exempt from IHT",
        "Total value: £{total_value}"
      ],
      urgency_score: 10,
      impact_score: 20
    })
  
  RETURN recommendations


# ===== SCORING AND PRIORITIZATION =====
FUNCTION score_recommendations(
  recommendations: array[Recommendation],
  context: UserContext
) -> array[ScoredRecommendation]:
  
  scored = []
  
  FOR EACH rec IN recommendations:
    # Base score from urgency and impact
    base_score = (rec.urgency_score * 0.4) + (rec.impact_score * 0.6)
    
    # Adjust for user preferences
    IF rec.category IN context.preferred_recommendation_types:
      base_score *= 1.2
    
    # Adjust for estimated benefit
    benefit_score = calculate_benefit_score(rec.estimated_benefit)
    
    # Adjust for user's historical acceptance rate of similar recommendations
    acceptance_adjustment = get_category_acceptance_rate(context.user_id, rec.category)
    
    # Final score
    final_score = base_score * (1 + benefit_score) * acceptance_adjustment
    
    scored.append({
      recommendation: rec,
      score: final_score,
      base_score: base_score,
      benefit_score: benefit_score,
      acceptance_adjustment: acceptance_adjustment
    })
  
  RETURN scored


FUNCTION rank_recommendations(recommendations: array[ScoredRecommendation]) -> array:
  # Sort by score descending
  RETURN SORT(recommendations, BY score DESC)


FUNCTION filter_recommendations(
  recommendations: array[ScoredRecommendation],
  context: UserContext
) -> array:
  
  filtered = []
  
  FOR EACH rec IN recommendations:
    # Remove duplicates
    IF NOT already_exists(filtered, rec.recommendation.type):
      
      # Remove conflicting recommendations
      IF NOT conflicts_with_existing(filtered, rec):
        
        # Remove if already actioned recently
        IF NOT recently_actioned(context.user_id, rec.recommendation.type):
          
          # Remove if dismissed recently
          IF NOT recently_dismissed(context.user_id, rec.recommendation.type):
            
            filtered.append(rec)
  
  RETURN filtered
API Endpoints:
POST /api/v1/advisory/generate-recommendations
GET /api/v1/advisory/recommendations/{userId}
PUT /api/v1/advisory/recommendations/{id}/status
POST /api/v1/advisory/recommendations/{id}/dismiss
POST /api/v1/advisory/recommendations/{id}/accept
GET /api/v1/advisory/recommendation-history
POST /api/v1/advisory/recalculate
Data Models:
TABLE: ai_recommendations (reusing from earlier, expanded)
- id: UUID (PK)
- user_id: UUID (FK to users)
- priority: ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO')
- category: ENUM('PROTECTION', 'SAVINGS', 'INVESTMENT', 'RETIREMENT', 'TAX', 'IHT', 'CROSS_CUTTING')
- recommendation_type: VARCHAR(100)
- title: VARCHAR(255)
- description: TEXT
- reasoning: JSON (array of reasoning points)
- estimated_benefit: JSON
- action_required: TEXT
- deadline: DATE (optional)
- urgency_score: INTEGER (0-100)
- impact_score: INTEGER (0-100)
- final_score: DECIMAL(10,2)
- status: ENUM('NEW', 'VIEWED', 'IN_PROGRESS', 'COMPLETED', 'DISMISSED')
- generated_at: TIMESTAMP
- expires_at: TIMESTAMP
- completed_at: TIMESTAMP
- dismissed_at: TIMESTAMP
- dismissal_reason: TEXT

TABLE: recommendation_user_actions
- id: UUID (PK)
- recommendation_id: UUID (FK to ai_recommendations)
- user_id: UUID (FK to users)
- action_type: ENUM('VIEWED', 'ACCEPTED', 'DISMISSED', 'COMPLETED')
- action_date: TIMESTAMP
- notes: TEXT

TABLE: recommendation_effectiveness
- id: UUID (PK)
- recommendation_type: VARCHAR(100)
- user_id: UUID (FK to users)
- acceptance_rate: DECIMAL(5,2)
- completion_rate: DECIMAL(5,2)
- average_time_to_action: INTEGER (days)
- measured_benefit: DECIMAL(15,2)
- last_calculated: TIMESTAMP

INDEX on ai_recommendations(user_id, status, priority, generated_at DESC)
INDEX on recommendation_user_actions(user_id, recommendation_id, action_type)

10. AI ADVISORY ENGINE (Continued)
Feature 10.2: Goal-Based Financial Planning
Feature Name: Comprehensive Goal Setting and Progress Tracking with AI-Driven Planning
User Story: As a user, I want to set specific financial goals (e.g., buy a house, retire comfortably, children's education) and receive a personalized plan showing whether I'm on track, what actions to take, and how to prioritize competing goals.
Acceptance Criteria:
•	User can create multiple financial goals with target amounts and dates
•	System calculates required monthly savings/contributions for each goal
•	Track progress toward each goal in real-time
•	Prioritize goals based on urgency and feasibility
•	Identify conflicts between goals (insufficient resources)
•	Generate actionable plans to achieve goals
•	Adjust plans when circumstances change
•	Show trade-offs between different goal scenarios
•	Integration with all financial modules
•	Multi-currency goal support
Technical Requirements:
•	Goal modeling engine with time-value-of-money calculations
•	Monte Carlo simulation for probability of success
•	Optimization algorithm for resource allocation
•	Constraint satisfaction solver for competing goals
•	Real-time progress tracking
•	Scenario comparison engine
•	Inflation adjustment
•	Investment return modeling
Constraints:
•	Goals must be SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
•	Maximum 10 active goals per user
•	Minimum goal timeline: 6 months
•	Maximum goal timeline: 50 years
•	Must consider existing commitments (expenses, debt payments)
•	Cannot allocate more than 100% of available income
Implementation Approach:
SERVICE: GoalPlanningEngine

# ===== GOAL CREATION AND VALIDATION =====
FUNCTION create_goal(user_id: uuid, goal_data: GoalInput) -> Goal:
  
  # Validate goal data
  validate_goal_data(goal_data)
  
  # Create goal
  goal = {
    id: generate_uuid(),
    user_id: user_id,
    goal_type: goal_data.goal_type,
    title: goal_data.title,
    description: goal_data.description,
    target_amount: goal_data.target_amount,
    currency: goal_data.currency,
    target_date: goal_data.target_date,
    priority: goal_data.priority,
    current_progress: 0,
    linked_accounts: goal_data.linked_accounts,
    created_at: NOW(),
    status: 'ACTIVE'
  }
  
  # Calculate plan
  plan = generate_goal_plan(user_id, goal)
  
  # Store goal and plan
  store_goal(goal)
  store_goal_plan(goal.id, plan)
  
  # Recalculate all goals (check for conflicts)
  recalculate_all_goals(user_id)
  
  RETURN {
    goal: goal,
    plan: plan,
    feasibility: plan.feasibility_assessment
  }


FUNCTION validate_goal_data(goal_data: GoalInput) -> boolean:
  
  # Validate target amount
  IF goal_data.target_amount <= 0:
    THROW ValidationError("Target amount must be positive")
  
  # Validate target date
  months_to_goal = calculate_months_between(NOW(), goal_data.target_date)
  
  IF months_to_goal < 6:
    THROW ValidationError("Goal must be at least 6 months in the future")
  
  IF months_to_goal > 600:  # 50 years
    THROW ValidationError("Goal cannot be more than 50 years in the future")
  
  # Check goal limit
  active_goals_count = count_active_goals(goal_data.user_id)
  IF active_goals_count >= 10:
    THROW ValidationError("Maximum 10 active goals allowed")
  
  RETURN TRUE


# ===== GOAL TYPES =====
ENUM GoalType:
  EMERGENCY_FUND
  HOUSE_PURCHASE
  HOME_IMPROVEMENT
  DEBT_REPAYMENT
  VEHICLE_PURCHASE
  WEDDING
  HOLIDAY_TRAVEL
  EDUCATION_CHILDREN
  EDUCATION_SELF
  RETIREMENT
  BUSINESS_START
  INHERITANCE_PLANNING
  FINANCIAL_INDEPENDENCE
  CHARITABLE_GIVING
  OTHER


# ===== GOAL PLAN GENERATION =====
FUNCTION generate_goal_plan(user_id: uuid, goal: Goal) -> GoalPlan:
  
  # Get user financial context
  context = build_user_context(user_id)
  
  # Calculate time to goal
  months_to_goal = calculate_months_between(NOW(), goal.target_date)
  years_to_goal = months_to_goal / 12
  
  # Determine appropriate savings vehicle
  savings_vehicle = determine_savings_vehicle(goal, years_to_goal, context)
  
  # Estimate investment return
  expected_return = estimate_expected_return(savings_vehicle, years_to_goal)
  
  # Calculate required monthly contribution
  required_monthly = calculate_required_monthly_contribution(
    target_amount: goal.target_amount,
    months: months_to_goal,
    annual_return: expected_return,
    current_savings: goal.current_progress
  )
  
  # Assess feasibility
  feasibility = assess_goal_feasibility(user_id, required_monthly, context)
  
  # Generate milestones
  milestones = generate_goal_milestones(goal, months_to_goal)
  
  # Generate recommendations
  recommendations = generate_goal_recommendations(goal, required_monthly, feasibility, context)
  
  # Calculate probability of success
  probability_of_success = calculate_success_probability(
    goal: goal,
    monthly_contribution: required_monthly,
    expected_return: expected_return,
    time_horizon: years_to_goal,
    market_volatility: get_market_volatility(savings_vehicle)
  )
  
  RETURN {
    goal_id: goal.id,
    target_amount: goal.target_amount,
    current_progress: goal.current_progress,
    required_monthly_contribution: required_monthly,
    recommended_savings_vehicle: savings_vehicle,
    expected_annual_return: expected_return,
    months_to_goal: months_to_goal,
    projected_final_amount: calculate_future_value(
      required_monthly,
      months_to_goal,
      expected_return
    ),
    probability_of_success: probability_of_success,
    feasibility_assessment: feasibility,
    milestones: milestones,
    recommendations: recommendations,
    alternative_scenarios: generate_alternative_scenarios(goal, context)
  }


FUNCTION determine_savings_vehicle(
  goal: Goal,
  years_to_goal: decimal,
  context: UserContext
) -> SavingsVehicle:
  
  # Short-term goals (<2 years): Cash savings
  IF years_to_goal < 2:
    IF context.uk_tax_resident AND has_isa_allowance(context):
      RETURN 'CASH_ISA'
    ELSE IF context.sa_tax_resident AND has_tfsa_allowance(context):
      RETURN 'TFSA_CASH'
    ELSE:
      RETURN 'SAVINGS_ACCOUNT'
  
  # Medium-term goals (2-5 years): Conservative investments
  ELSE IF years_to_goal >= 2 AND years_to_goal < 5:
    IF context.risk_tolerance = 'LOW':
      RETURN 'CASH_ISA'
    ELSE:
      IF context.uk_tax_resident AND has_isa_allowance(context):
        RETURN 'STOCKS_SHARES_ISA_CONSERVATIVE'
      ELSE:
        RETURN 'BALANCED_PORTFOLIO'
  
  # Long-term goals (5+ years): Growth investments
  ELSE:
    IF goal.goal_type = 'RETIREMENT':
      IF context.uk_tax_resident:
        RETURN 'PENSION_SIPP'
      ELSE IF context.sa_tax_resident:
        RETURN 'RETIREMENT_ANNUITY'
    ELSE:
      IF context.uk_tax_resident AND has_isa_allowance(context):
        RETURN 'STOCKS_SHARES_ISA_GROWTH'
      ELSE IF context.sa_tax_resident AND has_tfsa_allowance(context):
        RETURN 'TFSA_EQUITY'
      ELSE:
        RETURN 'GROWTH_PORTFOLIO'


FUNCTION estimate_expected_return(
  vehicle: SavingsVehicle,
  years_to_goal: decimal
) -> decimal:
  
  # Conservative estimates (post-inflation, post-tax where applicable)
  
  MATCH vehicle:
    CASE 'SAVINGS_ACCOUNT':
      RETURN 0.01  # 1% real return
    
    CASE 'CASH_ISA', 'TFSA_CASH':
      RETURN 0.02  # 2% real return
    
    CASE 'STOCKS_SHARES_ISA_CONSERVATIVE', 'BALANCED_PORTFOLIO':
      RETURN 0.04  # 4% real return
    
    CASE 'STOCKS_SHARES_ISA_GROWTH', 'TFSA_EQUITY', 'GROWTH_PORTFOLIO':
      RETURN 0.06  # 6% real return
    
    CASE 'PENSION_SIPP', 'RETIREMENT_ANNUITY':
      IF years_to_goal > 20:
        RETURN 0.07  # 7% real return (long-term equity)
      ELSE IF years_to_goal > 10:
        RETURN 0.06
      ELSE:
        RETURN 0.05  # More conservative as approaching retirement


FUNCTION calculate_required_monthly_contribution(
  target_amount: decimal,
  months: integer,
  annual_return: decimal,
  current_savings: decimal
) -> decimal:
  
  # Future value of current savings
  monthly_rate = annual_return / 12
  fv_current_savings = current_savings * POWER(1 + monthly_rate, months)
  
  # Required additional savings
  additional_needed = target_amount - fv_current_savings
  
  IF additional_needed <= 0:
    RETURN 0  # Already have enough
  
  # Calculate monthly payment using future value of annuity formula
  # FV = PMT × [((1 + r)^n - 1) / r]
  # PMT = FV / [((1 + r)^n - 1) / r]
  
  IF monthly_rate = 0:
    # No growth assumption
    monthly_contribution = additional_needed / months
  ELSE:
    numerator = additional_needed * monthly_rate
    denominator = POWER(1 + monthly_rate, months) - 1
    monthly_contribution = numerator / denominator
  
  RETURN ROUND(monthly_contribution, 2)


# ===== FEASIBILITY ASSESSMENT =====
FUNCTION assess_goal_feasibility(
  user_id: uuid,
  required_monthly: decimal,
  context: UserContext
) -> FeasibilityAssessment:
  
  # Calculate available monthly income
  monthly_income = context.income.monthly
  
  # Calculate committed expenses
  essential_expenses = calculate_essential_expenses(user_id)
  existing_goal_contributions = calculate_existing_goal_contributions(user_id)
  debt_payments = calculate_debt_payments(user_id)
  
  committed_monthly = essential_expenses + existing_goal_contributions + debt_payments
  
  # Calculate available for new goals
  available_monthly = monthly_income - committed_monthly
  
  # Calculate percentage of income required
  percentage_of_income = (required_monthly / monthly_income) * 100
  
  # Feasibility assessment
  IF required_monthly <= 0:
    feasibility = 'ALREADY_ACHIEVED'
    recommendation = "You already have sufficient savings for this goal"
  
  ELSE IF required_monthly <= available_monthly:
    IF percentage_of_income < 10:
      feasibility = 'HIGHLY_FEASIBLE'
      recommendation = "This goal is easily achievable with your current income"
    ELSE IF percentage_of_income < 20:
      feasibility = 'FEASIBLE'
      recommendation = "This goal is achievable with disciplined saving"
    ELSE:
      feasibility = 'CHALLENGING'
      recommendation = "This goal will require significant commitment"
  
  ELSE IF required_monthly <= available_monthly * 1.2:
    feasibility = 'REQUIRES_ADJUSTMENT'
    recommendation = "Consider reducing expenses or extending timeline"
  
  ELSE:
    feasibility = 'NOT_FEASIBLE'
    recommendation = "Goal not achievable with current income. Consider alternative approach"
  
  RETURN {
    feasibility_level: feasibility,
    required_monthly: required_monthly,
    available_monthly: available_monthly,
    shortfall: MAX(required_monthly - available_monthly, 0),
    percentage_of_income: percentage_of_income,
    recommendation: recommendation,
    suggested_adjustments: generate_feasibility_adjustments(
      required_monthly,
      available_monthly,
      context
    )
  }


FUNCTION generate_feasibility_adjustments(
  required_monthly: decimal,
  available_monthly: decimal,
  context: UserContext
) -> array[Adjustment]:
  
  adjustments = []
  shortfall = required_monthly - available_monthly
  
  IF shortfall <= 0:
    RETURN []  # No adjustments needed
  
  # Adjustment 1: Extend timeline
  current_months = context.goal.months_to_goal
  extended_months = calculate_months_needed_for_affordable_payment(
    context.goal.target_amount,
    available_monthly,
    context.expected_return
  )
  
  IF extended_months > current_months:
    adjustments.append({
      type: 'EXTEND_TIMELINE',
      description: "Extend goal timeline to {extended_months} months",
      new_timeline_months: extended_months,
      new_monthly_required: available_monthly,
      impact: "Makes goal achievable within current budget"
    })
  
  # Adjustment 2: Reduce target amount
  affordable_target = calculate_affordable_target_amount(
    available_monthly,
    current_months,
    context.expected_return,
    context.goal.current_progress
  )
  
  IF affordable_target < context.goal.target_amount:
    adjustments.append({
      type: 'REDUCE_TARGET',
      description: "Reduce target from {original} to {affordable_target}",
      original_target: context.goal.target_amount,
      adjusted_target: affordable_target,
      reduction: context.goal.target_amount - affordable_target,
      impact: "Achievable with current budget and timeline"
    })
  
  # Adjustment 3: Increase income
  required_income_increase = shortfall
  percentage_increase = (required_income_increase / context.income.monthly) * 100
  
  adjustments.append({
    type: 'INCREASE_INCOME',
    description: "Increase monthly income by {amount}",
    amount_needed: required_income_increase,
    percentage_increase: percentage_increase,
    suggestions: [
      "Seek salary increase or promotion",
      "Take on additional work or side income",
      "Monetize skills or hobbies"
    ]
  })
  
  # Adjustment 4: Reduce expenses
  potential_savings = identify_expense_reduction_opportunities(context.user_id)
  
  IF potential_savings.total >= shortfall:
    adjustments.append({
      type: 'REDUCE_EXPENSES',
      description: "Reduce monthly expenses by {amount}",
      amount_to_reduce: shortfall,
      potential_areas: potential_savings.areas,
      suggestions: potential_savings.suggestions
    })
  
  # Adjustment 5: Deprioritize other goals
  lower_priority_goals = get_lower_priority_goals(context.user_id, context.goal.priority)
  
  IF lower_priority_goals.count > 0:
    freed_up_budget = SUM(lower_priority_goals.monthly_contribution)
    
    IF freed_up_budget >= shortfall:
      adjustments.append({
        type: 'DEPRIORITIZE_GOALS',
        description: "Pause contributions to lower priority goals",
        goals_to_pause: lower_priority_goals,
        budget_freed: freed_up_budget,
        impact: "Allows focus on higher priority goal"
      })
  
  RETURN adjustments


# ===== GOAL MILESTONES =====
FUNCTION generate_goal_milestones(
  goal: Goal,
  months_to_goal: integer
) -> array[Milestone]:
  
  milestones = []
  
  # Create quarterly milestones
  milestone_count = CEIL(months_to_goal / 3)  # Every 3 months
  
  FOR i FROM 1 TO milestone_count:
    milestone_date = ADD_MONTHS(NOW(), i * 3)
    
    IF milestone_date > goal.target_date:
      milestone_date = goal.target_date
    
    progress_percentage = (i / milestone_count) * 100
    target_amount_at_milestone = goal.target_amount * (progress_percentage / 100)
    
    milestones.append({
      milestone_number: i,
      milestone_date: milestone_date,
      target_progress_percentage: progress_percentage,
      target_amount: target_amount_at_milestone,
      description: "{progress_percentage}% toward goal",
      achieved: FALSE
    })
  
  RETURN milestones


# ===== GOAL PROGRESS TRACKING =====
FUNCTION update_goal_progress(goal_id: uuid) -> GoalProgress:
  
  goal = get_goal(goal_id)
  
  # Calculate current progress from linked accounts
  current_progress = 0
  
  FOR EACH account_id IN goal.linked_accounts:
    account_balance = get_account_balance(account_id)
    current_progress += account_balance
  
  # Update goal
  goal.current_progress = current_progress
  goal.progress_percentage = (current_progress / goal.target_amount) * 100
  goal.last_updated = NOW()
  
  # Check milestones
  milestones = get_goal_milestones(goal_id)
  
  FOR EACH milestone IN milestones:
    IF NOT milestone.achieved AND current_progress >= milestone.target_amount:
      milestone.achieved = TRUE
      milestone.achieved_date = NOW()
      
      # Trigger celebration notification
      send_milestone_notification(goal.user_id, goal, milestone)
  
  # Recalculate plan if significantly off track
  plan = get_goal_plan(goal_id)
  
  # Calculate expected progress at this point
  months_elapsed = calculate_months_between(goal.created_at, NOW())
  expected_progress = calculate_expected_progress(plan, months_elapsed)
  
  variance = current_progress - expected_progress
  variance_percentage = (variance / expected_progress) * 100
  
  # If more than 10% off track, recalculate
  IF ABS(variance_percentage) > 10:
    new_plan = generate_goal_plan(goal.user_id, goal)
    update_goal_plan(goal_id, new_plan)
    
    # Notify user of plan adjustment
    send_plan_adjustment_notification(goal.user_id, goal, new_plan)
  
  store_goal(goal)
  
  RETURN {
    goal_id: goal_id,
    current_progress: current_progress,
    progress_percentage: goal.progress_percentage,
    target_amount: goal.target_amount,
    on_track: variance_percentage >= -10,
    variance: variance,
    variance_percentage: variance_percentage,
    milestones_achieved: COUNT(milestones WHERE achieved = TRUE),
    next_milestone: FIRST(milestones WHERE achieved = FALSE),
    updated_plan: IF plan_was_updated THEN new_plan ELSE NULL
  }


# ===== MONTE CARLO SIMULATION FOR SUCCESS PROBABILITY =====
FUNCTION calculate_success_probability(
  goal: Goal,
  monthly_contribution: decimal,
  expected_return: decimal,
  time_horizon: decimal,
  market_volatility: decimal
) -> decimal:
  
  # Run Monte Carlo simulation (10,000 iterations)
  simulation_count = 10000
  success_count = 0
  
  FOR iteration FROM 1 TO simulation_count:
    simulated_final_value = simulate_investment_outcome(
      initial_amount: goal.current_progress,
      monthly_contribution: monthly_contribution,
      months: goal.months_to_goal,
      expected_annual_return: expected_return,
      annual_volatility: market_volatility
    )
    
    IF simulated_final_value >= goal.target_amount:
      success_count += 1
  
  probability = (success_count / simulation_count) * 100
  
  RETURN ROUND(probability, 1)


FUNCTION simulate_investment_outcome(
  initial_amount: decimal,
  monthly_contribution: decimal,
  months: integer,
  expected_annual_return: decimal,
  annual_volatility: decimal
) -> decimal:
  
  balance = initial_amount
  
  FOR month FROM 1 TO months:
    # Generate random monthly return using normal distribution
    monthly_return = generate_normal_random(
      mean: expected_annual_return / 12,
      std_dev: annual_volatility / SQRT(12)
    )
    
    # Apply return to current balance
    balance = balance * (1 + monthly_return)
    
    # Add monthly contribution
    balance = balance + monthly_contribution
  
  RETURN balance


# ===== GOAL PRIORITIZATION =====
FUNCTION prioritize_user_goals(user_id: uuid) -> array[PrioritizedGoal]:
  
  goals = get_active_goals(user_id)
  context = build_user_context(user_id)
  
  # Calculate priority score for each goal
  scored_goals = []
  
  FOR EACH goal IN goals:
    score = calculate_goal_priority_score(goal, context)
    
    scored_goals.append({
      goal: goal,
      priority_score: score.total_score,
      urgency_score: score.urgency,
      importance_score: score.importance,
      feasibility_score: score.feasibility
    })
  
  # Sort by priority score (descending)
  prioritized = SORT(scored_goals, BY priority_score DESC)
  
  RETURN prioritized


FUNCTION calculate_goal_priority_score(
  goal: Goal,
  context: UserContext
) -> GoalScore:
  
  # Urgency score (based on time remaining)
  months_remaining = calculate_months_between(NOW(), goal.target_date)
  
  IF months_remaining < 12:
    urgency_score = 100
  ELSE IF months_remaining < 24:
    urgency_score = 80
  ELSE IF months_remaining < 60:
    urgency_score = 60
  ELSE:
    urgency_score = 40
  
  # Importance score (based on goal type and user priority)
  base_importance = {
    'EMERGENCY_FUND': 100,
    'DEBT_REPAYMENT': 95,
    'RETIREMENT': 90,
    'HOUSE_PURCHASE': 85,
    'EDUCATION_CHILDREN': 85,
    'WEDDING': 70,
    'VEHICLE_PURCHASE': 60,
    'HOLIDAY_TRAVEL': 40,
    'OTHER': 50
  }
  
  importance_score = base_importance[goal.goal_type]
  
  # Adjust for user-specified priority
  IF goal.priority = 'HIGH':
    importance_score *= 1.2
  ELSE IF goal.priority = 'LOW':
    importance_score *= 0.8
  
  # Feasibility score (how achievable)
  plan = get_goal_plan(goal.id)
  
  MATCH plan.feasibility_assessment.feasibility_level:
    CASE 'HIGHLY_FEASIBLE':
      feasibility_score = 100
    CASE 'FEASIBLE':
      feasibility_score = 80
    CASE 'CHALLENGING':
      feasibility_score = 60
    CASE 'REQUIRES_ADJUSTMENT':
      feasibility_score = 40
    CASE 'NOT_FEASIBLE':
      feasibility_score = 20
  
  # Life stage relevance
  life_stage_multiplier = calculate_life_stage_relevance(goal, context.age)
  
  # Calculate total score (weighted average)
  total_score = (
    urgency_score * 0.3 +
    importance_score * 0.4 +
    feasibility_score * 0.3
  ) * life_stage_multiplier
  
  RETURN {
    urgency: urgency_score,
    importance: importance_score,
    feasibility: feasibility_score,
    life_stage_multiplier: life_stage_multiplier,
    total_score: total_score
  }


# ===== GOAL CONFLICT RESOLUTION =====
FUNCTION identify_goal_conflicts(user_id: uuid) -> array[Conflict]:
  
  goals = get_active_goals(user_id)
  context = build_user_context(user_id)
  
  # Calculate total required contributions
  total_required_monthly = 0
  
  FOR EACH goal IN goals:
    plan = get_goal_plan(goal.id)
    total_required_monthly += plan.required_monthly_contribution
  
  # Calculate available budget
  available_monthly = calculate_available_monthly_income(context)
  
  conflicts = []
  
  # Conflict 1: Insufficient income
  IF total_required_monthly > available_monthly:
    shortfall = total_required_monthly - available_monthly
    
    conflicts.append({
      conflict_type: 'INSUFFICIENT_INCOME',
      severity: 'HIGH',
      description: "Total required contributions (£{total_required_monthly}) exceed available income (£{available_monthly})",
      shortfall: shortfall,
      affected_goals: goals,
      resolution_options: [
        {
          option: 'PRIORITIZE_GOALS',
          description: "Focus on highest priority goals only",
          action: generate_prioritization_recommendation(goals, available_monthly)
        },
        {
          option: 'EXTEND_TIMELINES',
          description: "Extend timelines for lower priority goals",
          action: generate_timeline_extension_recommendation(goals, shortfall)
        },
        {
          option: 'INCREASE_INCOME',
          description: "Increase income by £{shortfall}/month",
          required_increase: shortfall
        }
      ]
    })
  
  # Conflict 2: Competing deadlines
  near_term_goals = FILTER(goals, WHERE months_to_goal < 12)
  
  IF near_term_goals.count > 2:
    conflicts.append({
      conflict_type: 'COMPETING_DEADLINES',
      severity: 'MEDIUM',
      description: "{count} goals have deadlines within 12 months",
      affected_goals: near_term_goals,
      resolution_options: [
        {
          option: 'STAGGER_GOALS',
          description: "Extend some goal deadlines to spread out timing",
          recommendation: generate_staggering_recommendation(near_term_goals)
        }
      ]
    })
  
  # Conflict 3: Retirement underfunded while pursuing other goals
  retirement_goals = FILTER(goals, WHERE goal_type = 'RETIREMENT')
  
  IF retirement_goals.exists:
    retirement_goal = retirement_goals[0]
    retirement_plan = get_goal_plan(retirement_goal.id)
    
    IF retirement_plan.feasibility_assessment.feasibility_level IN ['REQUIRES_ADJUSTMENT', 'NOT_FEASIBLE']:
      non_retirement_contribution = total_required_monthly - retirement_plan.required_monthly_contribution
      
      IF non_retirement_contribution > retirement_plan.required_monthly_contribution:
        conflicts.append({
          conflict_type: 'RETIREMENT_UNDERPRIORITIZED',
          severity: 'HIGH',
          description: "Retirement goal underfunded while pursuing short-term goals",
          affected_goals: [retirement_goal],
          resolution_options: [
            {
              option: 'INCREASE_RETIREMENT_PRIORITY',
              description: "Reduce other goal contributions to adequately fund retirement",
              recommended_allocation: {
                retirement: retirement_plan.required_monthly_contribution,
                other_goals: available_monthly - retirement_plan.required_monthly_contribution
              }
            }
          ]
        })
  
  RETURN conflicts


# ===== GOAL RECOMMENDATIONS =====
FUNCTION generate_goal_recommendations(
  goal: Goal,
  required_monthly: decimal,
  feasibility: FeasibilityAssessment,
  context: UserContext
) -> array[Recommendation]:
  
  recommendations = []
  
  # Recommendation 1: Open appropriate account
  IF goal.linked_accounts.count = 0:
    suggested_vehicle = determine_savings_vehicle(goal, goal.years_to_goal, context)
    
    recommendations.append({
      type: 'OPEN_ACCOUNT',
      priority: 'HIGH',
      title: "Open a {vehicle} for this goal",
      description: "We recommend a {vehicle} to maximize returns and tax efficiency",
      vehicle: suggested_vehicle,
      action: "Open account and link to this goal"
    })
  
  # Recommendation 2: Set up automatic contributions
  has_automatic_transfer = check_automatic_transfers(goal.id)
  
  IF NOT has_automatic_transfer:
    recommendations.append({
      type: 'AUTOMATE_SAVINGS',
      priority: 'HIGH',
      title: "Set up automatic monthly transfer of £{required_monthly}",
      description: "Automate your savings to ensure consistent progress",
      amount: required_monthly,
      action: "Set up standing order"
    })
  
  # Recommendation 3: One-off contribution if windfall
  IF context.liquid_assets > goal.target_amount * 0.5:
    lump_sum_contribution = MIN(
      goal.target_amount * 0.25,
      context.liquid_assets * 0.2
    )
    
    recommendations.append({
      type: 'LUMP_SUM_CONTRIBUTION',
      priority: 'MEDIUM',
      title: "Consider one-off contribution of £{lump_sum}",
      description: "You have liquid assets that could accelerate this goal",
      amount: lump_sum_contribution,
      impact: "Would reduce monthly contribution to £{new_monthly}",
      new_monthly: calculate_required_monthly_with_lump_sum(
        goal,
        lump_sum_contribution
      )
    })
  
  # Recommendation 4: Tax-efficient approach
  IF goal.goal_type = 'RETIREMENT':
    IF context.uk_tax_resident:
      tax_relief = required_monthly * context.marginal_tax_rate_uk
      
      recommendations.append({
        type: 'MAXIMIZE_TAX_RELIEF',
        priority: 'HIGH',
        title: "Maximize pension tax relief",
        description: "Pension contributions receive {rate}% tax relief",
        tax_relief_rate: context.marginal_tax_rate_uk * 100,
        monthly_tax_relief: tax_relief,
        action: "Ensure contributions made via pension scheme"
      })
  
  # Recommendation 5: If not feasible, suggest adjustments
  IF feasibility.feasibility_level IN ['REQUIRES_ADJUSTMENT', 'NOT_FEASIBLE']:
    FOR EACH adjustment IN feasibility.suggested_adjustments:
      recommendations.append({
        type: 'ADJUST_GOAL',
        priority: 'HIGH',
        title: adjustment.description,
        description: adjustment.impact,
        adjustment: adjustment
      })
  
  RETURN recommendations


# ===== ALTERNATIVE SCENARIOS =====
FUNCTION generate_alternative_scenarios(
  goal: Goal,
  context: UserContext
) -> array[Scenario]:
  
  scenarios = []
  
  # Scenario 1: Aggressive (higher contributions)
  aggressive_monthly = plan.required_monthly_contribution * 1.5
  aggressive_timeline = calculate_months_needed(goal.target_amount, aggressive_monthly, plan.expected_annual_return)
  
  scenarios.append({
    scenario_name: 'AGGRESSIVE',
    description: "Achieve goal faster with higher contributions",
    monthly_contribution: aggressive_monthly,
    timeline_months: aggressive_timeline,
    timeline_reduction: goal.months_to_goal - aggressive_timeline,
    total_contributed: aggressive_monthly * aggressive_timeline,
    final_amount: goal.target_amount,
    feasible: aggressive_monthly <= context.available_monthly
  })
  
  # Scenario 2: Conservative (lower contributions, longer timeline)
  conservative_monthly = plan.required_monthly_contribution * 0.75
  conservative_timeline = calculate_months_needed(goal.target_amount, conservative_monthly, plan.expected_annual_return)
  
  scenarios.append({
    scenario_name: 'CONSERVATIVE',
    description: "Lower monthly commitment with extended timeline",
    monthly_contribution: conservative_monthly,
    timeline_months: conservative_timeline,
    timeline_extension: conservative_timeline - goal.months_to_goal,
    total_contributed: conservative_monthly * conservative_timeline,
    final_amount: goal.target_amount,
    feasible: TRUE  # Lower contribution always more feasible
  })
  
  # Scenario 3: Stretch target (achieve more than target)
  stretch_target = goal.target_amount * 1.25
  stretch_monthly = calculate_required_monthly_contribution(
    stretch_target,
    goal.months_to_goal,
    plan.expected_annual_return,
    goal.current_progress
  )
  
  scenarios.append({
    scenario_name: 'STRETCH',
    description: "Exceed your target by 25%",
    monthly_contribution: stretch_monthly,
    timeline_months: goal.months_to_goal,
    total_contributed: stretch_monthly * goal.months_to_goal,
    final_amount: stretch_target,
    additional_amount: stretch_target - goal.target_amount,
    feasible: stretch_monthly <= context.available_monthly
  })
  
  # Scenario 4: Current pace (if contributing but not enough)
  IF goal.current_contributions > 0 AND goal.current_contributions < plan.required_monthly_contribution:
    current_pace_timeline = calculate_months_needed(
      goal.target_amount,
      goal.current_contributions,
      plan.expected_annual_return
    )
    
    current_pace_final = calculate_future_value(
      goal.current_contributions,
      goal.months_to_goal,
      plan.expected_annual_return
    )
    
    scenarios.append({
      scenario_name: 'CURRENT_PACE',
      description: "Continue at current contribution rate",
      monthly_contribution: goal.current_contributions,
      timeline_months: current_pace_timeline,
      final_amount: current_pace_final,
      shortfall: goal.target_amount - current_pace_final,
      feasible: TRUE,
      warning: "Will not reach target on time"
    })
  
  RETURN scenarios
API Endpoints:
# Goal Management
POST /api/v1/goals
PUT /api/v1/goals/{id}
DELETE /api/v1/goals/{id}
GET /api/v1/goals/{userId}
GET /api/v1/goals/{id}

# Goal Planning
GET /api/v1/goals/{id}/plan
POST /api/v1/goals/{id}/recalculate-plan
GET /api/v1/goals/{id}/scenarios
POST /api/v1/goals/{id}/select-scenario

# Progress Tracking
POST /api/v1/goals/{id}/update-progress
GET /api/v1/goals/{id}/progress
GET /api/v1/goals/{id}/milestones
POST /api/v1/goals/{id}/milestones/{milestoneId}/complete

# Goal Prioritization
GET /api/v1/goals/{userId}/prioritized
POST /api/v1/goals/{userId}/resolve-conflicts
GET /api/v1/goals/{userId}/conflicts

# Contributions
POST /api/v1/goals/{id}/contributions
GET /api/v1/goals/{id}/contributions/history
POST /api/v1/goals/{id}/link-account
DELETE /api/v1/goals/{id}/unlink-account/{accountId}

# Recommendations
GET /api/v1/goals/{id}/recommendations
POST /api/v1/goals/{id}/recommendations/{recId}/accept
Data Models:
TABLE: financial_goals
- id: UUID (PK)
- user_id: UUID (FK to users)
- goal_type: ENUM('EMERGENCY_FUND', 'HOUSE_PURCHASE', 'RETIREMENT', etc.)
- title: VARCHAR(255)
- description: TEXT
- target_amount: DECIMAL(15,2)
- currency: CHAR(3)
- target_date: DATE
- priority: ENUM('HIGH', 'MEDIUM', 'LOW')
- current_progress: DECIMAL(15,2)
- progress_percentage: DECIMAL(5,2)
- status: ENUM('ACTIVE', 'COMPLETED', 'PAUSED', 'CANCELLED')
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
- completed_at: TIMESTAMP

TABLE: goal_plans
- goal_id: UUID (PK, FK to financial_goals)
- required_monthly_contribution: DECIMAL(10,2)
- recommended_savings_vehicle: VARCHAR(100)
- expected_annual_return: DECIMAL(5,4)
- months_to_goal: INTEGER
- projected_final_amount: DECIMAL(15,2)
- probability_of_success: DECIMAL(5,2)
- feasibility_level: ENUM('HIGHLY_FEASIBLE', 'FEASIBLE', 'CHALLENGING', 'REQUIRES_ADJUSTMENT', 'NOT_FEASIBLE')
- plan_generated_at: TIMESTAMP
- last_recalculated: TIMESTAMP

TABLE: goal_milestones
- id: UUID (PK)
- goal_id: UUID (FK to financial_goals)
- milestone_number: INTEGER
- milestone_date: DATE
- target_progress_percentage: DECIMAL(5,2)
- target_amount: DECIMAL(15,2)
- description: VARCHAR(255)
- achieved: BOOLEAN DEFAULT FALSE
- achieved_date: DATE
- created_at: TIMESTAMP

TABLE: goal_linked_accounts
- id: UUID (PK)
- goal_id: UUID (FK to financial_goals)
- account_type: ENUM('SAVINGS_ACCOUNT', 'ISA', 'INVESTMENT_ACCOUNT', 'PENSION')
- account_id: UUID (FK to respective account tables)
- linked_at: TIMESTAMP

TABLE: goal_contributions
- id: UUID (PK)
- goal_id: UUID (FK to financial_goals)
- contribution_date: DATE
- contribution_amount: DECIMAL(10,2)
- contribution_type: ENUM('MANUAL', 'AUTOMATIC', 'LUMP_SUM', 'WINDFALL')
- source_account_id: UUID
- notes: TEXT
- created_at: TIMESTAMP

TABLE: goal_scenarios
- id: UUID (PK)
- goal_id: UUID (FK to financial_goals)
- scenario_name: VARCHAR(100)
- monthly_contribution: DECIMAL(10,2)
- timeline_months: INTEGER
- final_amount: DECIMAL(15,2)
- probability_of_success: DECIMAL(5,2)
- is_selected: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP

TABLE: goal_conflicts
- id: UUID (PK)
- user_id: UUID (FK to users)
- conflict_type: ENUM('INSUFFICIENT_INCOME', 'COMPETING_DEADLINES', 'RETIREMENT_UNDERPRIORITIZED')
- severity: ENUM('HIGH', 'MEDIUM', 'LOW')
- description: TEXT
- affected_goals: JSON (array of goal_ids)
- resolution_options: JSON
- resolved: BOOLEAN DEFAULT FALSE
- resolved_at: TIMESTAMP
- created_at: TIMESTAMP

VIEW: v_goal_progress_summary
- goal_id
- user_id
- title
- target_amount
- current_progress
- progress_percentage
- required_monthly_contribution
- months_to_goal
- months_elapsed
- on_track: BOOLEAN
- next_milestone_date
- next_milestone_amount

INDEX on financial_goals(user_id, status)
INDEX on goal_contributions(goal_id, contribution_date DESC)
INDEX on goal_milestones(goal_id, achieved, milestone_date)
INDEX on goal_conflicts(user_id, resolved, created_at DESC)
Performance Considerations:
•	Monte Carlo simulation: 10,000 iterations, target <1 second
•	Goal plan recalculation: Cache unless data changes significantly
•	Progress updates: Real-time for linked accounts
•	Conflict detection: Run daily batch job + on-demand
•	Expected goals per user: 1-10 active
•	Milestone checks: Trigger on contribution or weekly batch
•	Scenario generation: Pre-calculate common scenarios
Feature 10.3: Scenario Analysis & What-If Modeling
Feature Name: Interactive Financial Scenario Modeling and Comparison
User Story: As a user, I want to model different financial scenarios (e.g., "What if I retire at 60 vs 65?", "What if I move to SA permanently?", "What if I sell my business?") and compare outcomes so that I can make informed decisions about major life changes.
Acceptance Criteria:
•	Model major life events and financial decisions
•	Compare multiple scenarios side-by-side
•	Show impact across all modules (tax, retirement, IHT, etc.)
•	Save and revisit scenarios
•	Share scenarios with advisors
•	Export scenario comparisons
•	Real-time recalculation as assumptions change
•	Risk analysis for each scenario
•	Probability-weighted outcomes
Technical Requirements:
•	Scenario engine with deep copy of user financial state
•	Parallel calculation for multiple scenarios
•	Differential analysis (what changed)
•	Sensitivity analysis
•	Monte Carlo simulation for uncertainty
•	Scenario versioning and history
•	Complex tax rule application across scenarios
Constraints:
•	Maximum 5 active scenarios per user
•	Scenarios expire after 90 days if not accessed
•	Calculation time: <5 seconds per scenario
•	Can model up to 30 years into future
•	Must maintain data consistency across scenarios
Implementation Approach:
SERVICE: ScenarioAnalysisEngine

# ===== SCENARIO TYPES =====
ENUM ScenarioType:
  RETIREMENT_AGE_CHANGE
  RELOCATION
  CAREER_CHANGE
  BUSINESS_SALE
  PROPERTY_PURCHASE
  PROPERTY_SALE
  INHERITANCE_RECEIVED
  MAJOR_EXPENSE
  INVESTMENT_STRATEGY_CHANGE
  TAX_RESIDENCY_CHANGE
  DIVORCE_SEPARATION
  MARRIAGE
  CHILD_BIRTH
  CUSTOM


# ===== SCENARIO CREATION =====
FUNCTION create_scenario(
  user_id: uuid,
  scenario_config: ScenarioConfig
) -> Scenario:
  
  # Validate scenario count
  active_scenarios = count_active_scenarios(user_id)
  IF active_scenarios >= 5:
    THROW ValidationError("Maximum 5 active scenarios allowed")
  
  # Create baseline (current state)
  baseline = create_baseline_snapshot(user_id)
  
  # Create scenario with modifications
  scenario = {
    id: generate_uuid(),
    user_id: user_id,
    name: scenario_config.name,
    description: scenario_config.description,
    scenario_type: scenario_config.type,
    baseline_snapshot_id: baseline.id,
    assumptions: scenario_config.assumptions,
    modifications: scenario_config.modifications,
    created_at: NOW(),
    last_accessed: NOW(),
    expires_at: NOW() + 90_DAYS
  }
  
  # Apply scenario modifications and calculate
  scenario_state = apply_scenario_modifications(baseline, scenario.modifications)
  scenario_results = calculate_scenario_outcomes(scenario_state, scenario.assumptions)
  
  # Store scenario
  store_scenario(scenario)
  store_scenario_results(scenario.id, scenario_results)
  
  RETURN {
    scenario: scenario,
    baseline: baseline,
    results: scenario_results,
    comparison: compare_to_baseline(baseline, scenario_results)
  }


FUNCTION create_baseline_snapshot(user_id: uuid) -> BaselineSnapshot:
  
  # Capture complete current state
  context = build_user_context(user_id)
  
  baseline = {
    id: generate_uuid(),
    user_id: user_id,
    snapshot_date: NOW(),
    
    # Demographics
    age: context.age,
    dependents: context.dependents,
    
    # Tax status
    tax_status: {
      uk_resident: context.uk_tax_resident,
      sa_resident: context.sa_tax_resident,
      domicile: context.domicile,
      deemed_domicile: context.deemed_domicile
    },
    
    # Financial position
    income: context.income,
    net_worth: context.net_worth,
    assets: get_all_assets(user_id),
    liabilities: get_all_liabilities(user_id),
    
    # Module data
    protection: context.protection,
    savings: context.savings,
    investments: context.investments,
    retirement: context.retirement,
    iht: context.iht,
    
    # Goals
    goals: get_all_goals(user_id),
    
    # Calculated metrics
    current_tax_liability: calculate_total_tax_liability(user_id, current_tax_year()),
    retirement_readiness: assess_retirement_readiness(user_id),
    iht_liability: get_iht_liability(user_id)
  }
  
  store_baseline_snapshot(baseline)
  
  RETURN baseline


# ===== SCENARIO MODIFICATIONS =====
FUNCTION apply_scenario_modifications(
  baseline: BaselineSnapshot,
  modifications: array[Modification]
) -> ScenarioState:
  
  # Deep copy baseline
  scenario_state = deep_copy(baseline)
  
  # Apply each modification
  FOR EACH mod IN modifications:
    MATCH mod.type:
      
      CASE 'CHANGE_AGE':
        scenario_state.age = mod.new_age
        scenario_state.years_elapsed = mod.new_age - baseline.age
      
      CASE 'CHANGE_INCOME':
        scenario_state.income = mod.new_income
      
      CASE 'CHANGE_TAX_RESIDENCY':
        scenario_state.tax_status.uk_resident = mod.uk_resident
        scenario_state.tax_status.sa_resident = mod.sa_resident
        
        # Recalculate domicile based on new residency
        scenario_state.tax_status = determine_tax_status_future(
          scenario_state,
          mod.change_date
        )
      
      CASE 'RETIRE':
        scenario_state.retirement.retired = TRUE
        scenario_state.retirement.retirement_date = mod.retirement_date
        scenario_state.retirement.retirement_age = calculate_age_at_date(
          baseline.date_of_birth,
          mod.retirement_date
        )
        
        # Stop pension contributions
        scenario_state.retirement.active_contributions = 0
        
        # Start drawing pension income
        scenario_state.retirement.drawing_income = TRUE
        scenario_state.income.pension = calculate_pension_income(scenario_state)
        
        # Remove employment income
        scenario_state.income.employment = 0
      
      CASE 'SELL_ASSET':
        # Remove asset from portfolio
        asset_to_sell = find_asset(scenario_state.assets, mod.asset_id)
        scenario_state.assets = remove_asset(scenario_state.assets, mod.asset_id)
        
        # Calculate CGT on sale
        capital_gain = mod.sale_price - asset_to_sell.cost_basis
        cgt = calculate_cgt(capital_gain, scenario_state.tax_status)
        
        # Add proceeds to cash (minus CGT)
        net_proceeds = mod.sale_price - cgt
        scenario_state.savings.cash += net_proceeds
      
      CASE 'PURCHASE_ASSET':
        # Add new asset
        new_asset = {
          id: generate_uuid(),
          type: mod.asset_type,
          description: mod.description,
          value: mod.purchase_price,
          purchase_date: mod.purchase_date,
          cost_basis: mod.purchase_price
        }
        scenario_state.assets.append(new_asset)
        
        # Reduce cash
        scenario_state.savings.cash -= mod.purchase_price
        
        # Add mortgage if applicable
        IF mod.mortgage_amount > 0:
          new_mortgage = {
            id: generate_uuid(),
            linked_asset_id: new_asset.id,
            amount: mod.mortgage_amount,
            interest_rate: mod.mortgage_rate,
            term_months: mod.mortgage_term
          }
          scenario_state.liabilities.append(new_mortgage)
      
      CASE 'RECEIVE_INHERITANCE':
        scenario_state.savings.cash += mod.inheritance_amount
        scenario_state.net_worth += mod.inheritance_amount
      
      CASE 'CHANGE_INVESTMENT_STRATEGY':
        # Rebalance portfolio to new allocation
        scenario_state.investments.asset_allocation = mod.new_allocation
        scenario_state.investments.expected_return = calculate_portfolio_return(mod.new_allocation)
      
      CASE 'ADD_GOAL':
        new_goal = mod.goal_data
        scenario_state.goals.append(new_goal)
      
      CASE 'MODIFY_GOAL':
        goal = find_goal(scenario_state.goals, mod.goal_id)
        goal.target_amount = mod.new_target_amount
        goal.target_date = mod.new_target_date
      
      CASE 'SELL_BUSINESS':
        # Remove business asset
        business_asset = find_business_asset(scenario_state.assets, mod.business_id)
        scenario_state.assets = remove_asset(scenario_state.assets, mod.business_id)
        
        # Calculate tax (BPR may apply if held >2 years)
        IF business_asset.held_years >= 2:
          bpr_relief = business_asset.value * 1.00  # 100% BPR
        ELSE:
          bpr_relief = 0
        
        taxable_gain = (mod.sale_price - business_asset.cost_basis) - bpr_relief
        cgt = calculate_cgt(taxable_gain, scenario_state.tax_status)
        
        # Add proceeds
        net_proceeds = mod.sale_price - cgt
        scenario_state.savings.cash += net_proceeds
        
        # Remove business income
        scenario_state.income.business = 0
      
      CASE 'RELOCATE':
        # Change country of residence
        scenario_state.location = mod.new_country
        scenario_state.tax_status = determine_tax_status_after_relocation(
          scenario_state,
          mod.new_country,
          mod.relocation_date
        )
        
        # Update asset situs where relevant
        scenario_state.assets = update_asset_situs(scenario_state.assets, mod.new_country)
      
      CASE 'GIFT_ASSET':
        # Remove asset from estate
        gifted_asset = find_asset(scenario_state.assets, mod.asset_id)
        scenario_state.assets = remove_asset(scenario_state.assets, mod.asset_id)
        
        # Record PET (Potentially Exempt Transfer)
        pet = {
          gift_date: mod.gift_date,
          value: gifted_asset.value,
          recipient: mod.recipient,
          becomes_exempt: mod.gift_date + 7_YEARS
        }
        scenario_state.iht.pets.append(pet)
      
      CASE 'MARRIAGE':
        scenario_state.marital_status = 'MARRIED'
        scenario_state.spouse = mod.spouse_data
        
        # Potential tax changes (marriage allowance, IHT spouse exemption)
        scenario_state.tax_benefits.marriage_allowance_eligible = TRUE
      
      CASE 'DIVORCE':
        scenario_state.marital_status = 'DIVORCED'
        scenario_state.spouse = NULL
        
        # Asset division
        IF mod.asset_split_percentage:
          scenario_state.assets = apply_asset_split(
            scenario_state.assets,
            mod.asset_split_percentage
          )
          scenario_state.net_worth *= (1 - mod.asset_split_percentage)
      
      CASE 'CHILD_BIRTH':
        scenario_state.dependents.children += 1
        scenario_state.dependents.list.append({
          name: mod.child_name,
          date_of_birth: mod.birth_date,
          dependent: TRUE
        })
        
        # Increase recommended life cover
        scenario_state.protection.recommended_life_cover += 100000
        
        # Add education goal
        education_goal = {
          type: 'EDUCATION_CHILDREN',
          target_amount: 50000,  # Estimate
          target_date: mod.birth_date + 18_YEARS
        }
        scenario_state.goals.append(education_goal)
      
      CASE 'CUSTOM_MODIFICATION':
        # Allow arbitrary modifications via custom logic
        apply_custom_modification(scenario_state, mod.custom_logic)
  
  RETURN scenario_state


# ===== SCENARIO CALCULATION =====
FUNCTION calculate_scenario_outcomes(
  scenario_state: ScenarioState,
  assumptions: Assumptions
) -> ScenarioResults:
  
  results = {
    scenario_state: scenario_state,
    projections: {},
    comparisons: {},
    risks: {}
  }
  
  # Project forward
  projection_years = assumptions.projection_years OR 30
  
  results.projections = {
    net_worth: project_net_worth(scenario_state, projection_years, assumptions),
    income: project_income(scenario_state, projection_years, assumptions),
    expenses: project_expenses(scenario_state, projection_years, assumptions),
    tax: project_tax_liability(scenario_state, projection_years, assumptions),
    retirement: project_retirement_income(scenario_state, assumptions),
    iht: project_iht_liability(scenario_state, assumptions),
    goals: assess_goal_achievement(scenario_state, assumptions)
  }
  
  # Calculate key metrics
  results.metrics = {
    lifetime_tax_paid: SUM(results.projections.tax),
    total_retirement_income: SUM(results.projections.retirement),
    retirement_adequacy_ratio: calculate_retirement_adequacy(results.projections),
    estate_value_at_death: calculate_estate_value_at_death(scenario_state, assumptions),
    iht_liability_at_death: calculate_iht_at_death(scenario_state, assumptions),
    goals_achieved_count: COUNT(results.projections.goals WHERE achieved = TRUE),
    goals_achieved_percentage: (goals_achieved / total_goals) * 100
  }
  
  # Risk analysis
  results.risks = {
    longevity_risk: assess_longevity_risk(scenario_state, results.projections),
    market_risk: assess_market_risk(scenario_state, assumptions),
    inflation_risk: assess_inflation_risk(scenario_state, assumptions),
    tax_change_risk: assess_tax_change_risk(scenario_state),
    health_risk: assess_health_risk(scenario_state)
  }
  
  # Monte Carlo simulation for uncertainty
  results.probability_distribution = run_monte_carlo_simulation(
    scenario_state,
    assumptions,
    simulations: 5000
  )
  
  RETURN results


FUNCTION project_net_worth(
  state: ScenarioState,
  years: integer,
  assumptions: Assumptions
) -> array[YearlyNetWorth]:
  
  projections = []
  current_state = state
  
  FOR year FROM 1 TO years:
    # Project asset growth
    investment_return = assumptions.investment_return OR 0.06
    assets_growth = current_state.assets.total * investment_return
    
    # Project income and savings
    annual_income = current_state.income.total
    annual_expenses = current_state.expenses.total
    annual_savings = annual_income - annual_expenses - current_state.tax.total
    
    # Update net worth
    new_net_worth = current_state.net_worth + assets_growth + annual_savings
    
    # Age by one year
    current_state.age += 1
    current_state.net_worth = new_net_worth
    
    # Check for life events
    IF current_state.age = current_state.retirement.planned_retirement_age:
      current_state = apply_retirement_changes(current_state)
    
    # Adjust for inflation
    inflation_rate = assumptions.inflation_rate OR 0.025
    current_state.expenses.total *= (1 + inflation_rate)
    
    projections.append({
      year: year,
      age: current_state.age,
      net_worth: new_net_worth,
      assets: current_state.assets.total,
      liabilities: current_state.liabilities.total,
      income: annual_income,
      expenses: annual_expenses,
      savings: annual_savings
    })
  
  RETURN projections


FUNCTION project_retirement_income(
  state: ScenarioState,
  assumptions: Assumptions
) -> RetirementProjection:
  
  retirement_age = state.retirement.planned_retirement_age
  
  # Pension pot at retirement
  years_to_retirement = retirement_age - state.age
  
  IF years_to_retirement <= 0:
    # Already retired
    pension_pot = state.retirement.current_pension_pot
  ELSE:
    # Project pension pot growth
    annual_contributions = state.retirement.annual_contributions
    growth_rate = assumptions.pension_growth_rate OR 0.06
    
    pension_pot = calculate_future_value(
      current_value: state.retirement.current_pension_pot,
      annual_contribution: annual_contributions,
      years: years_to_retirement,
      growth_rate: growth_rate
    )
  
  # Calculate tax-free lump sum (25%)
  tax_free_lump_sum = pension_pot * 0.25
  remaining_pension = pension_pot * 0.75
  
  # Calculate sustainable income (4% rule)
  sustainable_annual_income = remaining_pension * 0.04
  
  # Add state pension
  IF state.tax_status.uk_resident:
    state_pension_annual = estimate_uk_state_pension(state)
  ELSE IF state.tax_status.sa_resident:
    state_pension_annual = 0  # SA has no state pension
  ELSE:
    state_pension_annual = 0
  
  total_retirement_income = sustainable_annual_income + state_pension_annual
  
  # Calculate replacement ratio
  current_income = state.income.employment + state.income.self_employment
  replacement_ratio = (total_retirement_income / current_income) * 100
  
  RETURN {
    retirement_age: retirement_age,
    pension_pot_at_retirement: pension_pot,
    tax_free_lump_sum: tax_free_lump_sum,
    remaining_for_income: remaining_pension,
    sustainable_annual_income: sustainable_annual_income,
    state_pension_annual: state_pension_annual,
    total_annual_income: total_retirement_income,
    monthly_income: total_retirement_income / 12,
    replacement_ratio: replacement_ratio,
    adequate: replacement_ratio >= 70  # 70% is typical target
  }


# ===== SCENARIO COMPARISON =====
FUNCTION compare_scenarios(
  scenario_ids: array[uuid]
) -> ScenarioComparison:
  
  IF scenario_ids.length < 2:
    THROW ValidationError("Need at least 2 scenarios to compare")
  
  scenarios = []
  FOR EACH id IN scenario_ids:
    scenario = get_scenario(id)
    results = get_scenario_results(id)
    scenarios.append({scenario: scenario, results: results})
  
  # Compare key metrics
  comparison = {
    scenarios: scenarios,
    metric_comparisons: {},
    winner_by_metric: {},
    trade_offs: [],
    recommendations: []
  }
  
  # Compare net worth
  comparison.metric_comparisons.net_worth = compare_metric(
    scenarios,
    'projections.net_worth[final]',
    higher_is_better: TRUE
  )
  
  # Compare retirement income
  comparison.metric_comparisons.retirement_income = compare_metric(
    scenarios,
    'projections.retirement.total_annual_income',
    higher_is_better: TRUE
  )
  
  # Compare lifetime tax paid
  comparison.metric_comparisons.lifetime_tax = compare_metric(
    scenarios,
    'metrics.lifetime_tax_paid',
    higher_is_better: FALSE
  )
  
  # Compare IHT liability
  comparison.metric_comparisons.iht_liability = compare_metric(
    scenarios,
    'metrics.iht_liability_at_death',
    higher_is_better: FALSE
  )
  
  # Compare goals achieved
  comparison.metric_comparisons.goals_achieved = compare_metric(
    scenarios,
    'metrics.goals_achieved_percentage',
    higher_is_better: TRUE
  )
  
  # Compare retirement age
  comparison.metric_comparisons.retirement_age = compare_metric(
    scenarios,
    'scenario_state.retirement.retirement_age',
    higher_is_better: FALSE  # Earlier retirement is better
  )
  
  # Identify trade-offs
  comparison.trade_offs = identify_trade_offs(scenarios)
  
  # Generate recommendations
  comparison.recommendations = generate_scenario_recommendations(scenarios, comparison)
  
  # Overall best scenario
  comparison.overall_best = determine_best_scenario(scenarios, comparison)
  
  RETURN comparison


FUNCTION compare_metric(
  scenarios: array,
  metric_path: string,
  higher_is_better: boolean
) -> MetricComparison:
  
  values = []
  
  FOR EACH scenario IN scenarios:
    value = extract_value_by_path(scenario.results, metric_path)
    values.append({
      scenario_id: scenario.scenario.id,
      scenario_name: scenario.scenario.name,
      value: value
    })
  
  # Sort
  IF higher_is_better:
    sorted_values = SORT(values, BY value DESC)
  ELSE:
    sorted_values = SORT(values, BY value ASC)
  
  # Calculate differences
  best_value = sorted_values[0].value
  worst_value = sorted_values[last].value
  
  FOR EACH item IN sorted_values:
    item.difference_from_best = item.value - best_value
    item.percentage_difference = ((item.value - best_value) / best_value) * 100
  
  RETURN {
    metric_name: metric_path,
    higher_is_better: higher_is_better,
    values: sorted_values,
    best_scenario: sorted_values[0].scenario_id,
    worst_scenario: sorted_values[last].scenario_id,
    range: worst_value - best_value,
    average: AVERAGE(values.value)
  }


FUNCTION identify_trade_offs(scenarios: array) -> array[TradeOff]:
  
  trade_offs = []
  
  # Example: Early retirement vs higher net worth
  early_retirement_scenario = find_scenario_with_earliest_retirement(scenarios)
  highest_net_worth_scenario = find_scenario_with_highest_net_worth(scenarios)
  
  IF early_retirement_scenario.id != highest_net_worth_scenario.id:
    retirement_age_diff = highest_net_worth_scenario.retirement_age - 
                         early_retirement_scenario.retirement_age
    net_worth_diff = highest_net_worth_scenario.final_net_worth - 
                     early_retirement_scenario.final_net_worth
    
    trade_offs.append({
      trade_off_type: 'RETIREMENT_AGE_VS_NET_WORTH',
      description: "Retiring {retirement_age_diff} years later results in £{net_worth_diff} higher net worth",
      scenario_a: early_retirement_scenario,
      scenario_b: highest_net_worth_scenario,
      decision_factors: [
        "Personal preference for leisure vs wealth",
        "Health considerations",
        "Legacy intentions"
      ]
    })
  
  # Example: Tax residency change vs complexity
  uk_resident_scenario = find_uk_resident_scenario(scenarios)
  sa_resident_scenario = find_sa_resident_scenario(scenarios)
  
  IF uk_resident_scenario AND sa_resident_scenario:
    tax_diff = uk_resident_scenario.lifetime_tax - sa_resident_scenario.lifetime_tax
    
    trade_offs.append({
      trade_off_type: 'TAX_RESIDENCY_CHANGE',
      description: "Moving to SA saves £{tax_diff} in lifetime tax but adds complexity",
      scenario_a: uk_resident_scenario,
      scenario_b: sa_resident_scenario,
      decision_factors: [
        "Tax savings: £{tax_diff}",
        "Complexity of dual compliance",
        "Family and lifestyle preferences",
        "Healthcare considerations",
        "Currency risk"
      ]
    })
  
  # Example: Property purchase vs investment
  property_scenario = find_property_purchase_scenario(scenarios)
  investment_scenario = find_increased_investment_scenario(scenarios)
  
  IF property_scenario AND investment_scenario:
    trade_offs.append({
      trade_off_type: 'PROPERTY_VS_INVESTMENT',
      description: "Property provides stability but lower returns vs flexible investments",
      scenario_a: property_scenario,
      scenario_b: investment_scenario,
      decision_factors: [
        "Property: Tangible asset, housing security",
        "Investments: Higher potential returns, liquidity",
        "Property: Maintenance costs, less flexible",
        "Investments: Market volatility, no housing benefit"
      ]
    })
  
  RETURN trade_offs


# ===== WHAT-IF MODELING =====
FUNCTION run_what_if_analysis(
  user_id: uuid,
  base_scenario_id: uuid,
  what_if_variables: array[WhatIfVariable]
) -> WhatIfResults:
  
  base_scenario = get_scenario(base_scenario_id)
  base_results = get_scenario_results(base_scenario_id)
  
  what_if_results = []
  
  FOR EACH variable IN what_if_variables:
    # Create temporary scenario with variable changed
    modified_scenario = deep_copy(base_scenario)
    
    # Apply variable change
    MATCH variable.type:
      CASE 'INCOME_CHANGE':
        modified_scenario.state.income.total *= (1 + variable.percentage_change / 100)
      
      CASE 'INVESTMENT_RETURN':
        modified_scenario.assumptions.investment_return = variable.new_value
      
      CASE 'INFLATION_RATE':
        modified_scenario.assumptions.inflation_rate = variable.new_value
      
      CASE 'RETIREMENT_AGE':
        modified_scenario.state.retirement.planned_retirement_age = variable.new_value
      
      CASE 'PROPERTY_VALUE_CHANGE':
        property = find_property(modified_scenario.state.assets)
        property.value *= (1 + variable.percentage_change / 100)
      
      CASE 'MARKET_CRASH':
        modified_scenario.state.investments.portfolio_value *= (1 - variable.crash_percentage / 100)
      
      CASE 'INTEREST_RATE_CHANGE':
        FOR EACH liability IN modified_scenario.state.liabilities:
          IF liability.type = 'MORTGAGE':
            liability.interest_rate += variable.rate_change
    
    # Recalculate scenario
    what_if_result = calculate_scenario_outcomes(modified_scenario.state, modified_scenario.assumptions)
    
    # Compare to base
    impact = {
      variable: variable,
      base_value: extract_base_value(base_results, variable),
      new_value: extract_base_value(what_if_result, variable),
      difference: calculate_difference(base_results, what_if_result, variable),
      percentage_impact: calculate_percentage_impact(base_results, what_if_result, variable)
    }
    
    what_if_results.append({
      variable: variable,
      results: what_if_result,
      impact: impact
    })
  
  RETURN {
    base_scenario: base_scenario,
    base_results: base_results,
    what_if_results: what_if_results,
    sensitivity_analysis: generate_sensitivity_analysis(base_results, what_if_results)
  }


FUNCTION generate_sensitivity_analysis(
  base_results: ScenarioResults,
  what_if_results: array[WhatIfResult]
) -> SensitivityAnalysis:
  
  # Identify which variables have biggest impact on outcomes
  
  sensitivity_rankings = []
  
  FOR EACH what_if IN what_if_results:
    # Measure impact on key metrics
    net_worth_impact = ABS(what_if.impact.difference.net_worth)
    retirement_income_impact = ABS(what_if.impact.difference.retirement_income)
    tax_impact = ABS(what_if.impact.difference.lifetime_tax)
    
    # Combined sensitivity score
    sensitivity_score = (
      net_worth_impact * 0.4 +
      retirement_income_impact * 0.4 +
      tax_impact * 0.2
    ) / base_results.metrics.net_worth  # Normalize
    
    sensitivity_rankings.append({
      variable: what_if.variable,
      sensitivity_score: sensitivity_score,
      impacts: {
        net_worth: net_worth_impact,
        retirement_income: retirement_income_impact,
        lifetime_tax: tax_impact
      }
    })
  
  # Sort by sensitivity
  ranked = SORT(sensitivity_rankings, BY sensitivity_score DESC)
  
  # Classify
  FOR EACH item IN ranked:
    IF item.sensitivity_score > 0.10:  # >10% impact
      item.sensitivity_level = 'HIGH'
    ELSE IF item.sensitivity_score > 0.05:
      item.sensitivity_level = 'MEDIUM'
    ELSE:
      item.sensitivity_level = 'LOW'
  
  RETURN {
    ranked_sensitivities: ranked,
    most_sensitive_variable: ranked[0].variable,
    least_sensitive_variable: ranked[last].variable,
    high_sensitivity_variables: FILTER(ranked, WHERE sensitivity_level = 'HIGH'),
    recommendations: generate_sensitivity_recommendations(ranked)
  }


FUNCTION generate_sensitivity_recommendations(
  sensitivity_rankings: array
) -> array[Recommendation]:
  
  recommendations = []
  
  high_sensitivity_vars = FILTER(sensitivity_rankings, WHERE sensitivity_level = 'HIGH')
  
  FOR EACH var IN high_sensitivity_vars:
    MATCH var.variable.type:
      CASE 'INVESTMENT_RETURN':
        recommendations.append({
          title: "Your outcome is highly sensitive to investment returns",
          description: "A 1% change in returns significantly impacts your retirement. Consider diversification and risk management.",
          priority: 'HIGH',
          actions: [
            "Review investment strategy with advisor",
            "Consider diversifying across asset classes",
            "Don't rely on optimistic return assumptions"
          ]
        })
      
      CASE 'RETIREMENT_AGE':
        recommendations.append({
          title: "Retirement age has major impact on outcomes",
          description: "Working even 1-2 years longer significantly improves your position.",
          priority: 'HIGH',
          actions: [
            "Keep retirement age flexible",
            "Consider phased retirement",
            "Build multiple income streams"
          ]
        })
      
      CASE 'INFLATION_RATE':
        recommendations.append({
          title: "Outcomes sensitive to inflation",
          description: "Higher inflation erodes purchasing power and retirement adequacy.",
          priority: 'MEDIUM',
          actions: [
            "Consider inflation-protected investments",
            "Build buffer into retirement plans",
            "Review spending assumptions regularly"
          ]
        })
  
  RETURN recommendations


# ===== MONTE CARLO SIMULATION =====
FUNCTION run_monte_carlo_simulation(
  scenario_state: ScenarioState,
  assumptions: Assumptions,
  simulations: integer
) -> ProbabilityDistribution:
  
  # Run multiple simulations with randomized returns
  simulation_results = []
  
  FOR iteration FROM 1 TO simulations:
    # Randomize key variables
    random_assumptions = {
      investment_return: generate_random_return(
        mean: assumptions.investment_return,
        volatility: 0.15  # 15% volatility
      ),
      inflation_rate: generate_random_inflation(
        mean: assumptions.inflation_rate,
        volatility: 0.02
      ),
      longevity: generate_random_age_at_death(
        scenario_state.age,
        scenario_state.gender,
        scenario_state.health_status
      )
    }
    
    # Run simulation
    sim_result = calculate_scenario_outcomes(
      scenario_state,
      {
        ...assumptions,
        ...random_assumptions
      }
    )
    
    simulation_results.append({
      iteration: iteration,
      final_net_worth: sim_result.projections.net_worth[final],
      retirement_income: sim_result.projections.retirement.total_annual_income,
      estate_value: sim_result.metrics.estate_value_at_death,
      goals_achieved: sim_result.metrics.goals_achieved_count
    })
  
  # Analyze distribution
  net_worth_distribution = analyze_distribution(simulation_results, 'final_net_worth')
  retirement_distribution = analyze_distribution(simulation_results, 'retirement_income')
  
  # Calculate confidence intervals
  confidence_95 = {
    net_worth: calculate_percentile_range(net_worth_distribution, 2.5, 97.5),
    retirement_income: calculate_percentile_range(retirement_distribution, 2.5, 97.5)
  }
  
  # Probability of success
  success_criteria = {
    retirement_income_adequate: assumptions.target_retirement_income,
    net_worth_positive: 0,
    goals_all_achieved: scenario_state.goals.length
  }
  
  success_count = COUNT(simulation_results WHERE 
    retirement_income >= success_criteria.retirement_income_adequate AND
    final_net_worth > success_criteria.net_worth_positive AND
    goals_achieved = success_criteria.goals_all_achieved
  )
  
  probability_of_success = (success_count / simulations) * 100
  
  RETURN {
    simulations_run: simulations,
    distributions: {
      net_worth: net_worth_distribution,
      retirement_income: retirement_distribution
    },
    confidence_intervals: confidence_95,
    probability_of_success: probability_of_success,
    percentiles: {
      p10: calculate_percentile(net_worth_distribution, 10),
      p25: calculate_percentile(net_worth_distribution, 25),
      p50: calculate_percentile(net_worth_distribution, 50),  # Median
      p75: calculate_percentile(net_worth_distribution, 75),
      p90: calculate_percentile(net_worth_distribution, 90)
    },
    worst_case: MIN(simulation_results.final_net_worth),
    best_case: MAX(simulation_results.final_net_worth),
    expected_value: AVERAGE(simulation_results.final_net_worth)
  }


FUNCTION analyze_distribution(results: array, field: string) -> Distribution:
  
  values = EXTRACT(results, field)
  
  RETURN {
    mean: AVERAGE(values),
    median: MEDIAN(values),
    std_dev: STDEV(values),
    min: MIN(values),
    max: MAX(values),
    skewness: calculate_skewness(values),
    kurtosis: calculate_kurtosis(values),
    histogram: generate_histogram(values, bins: 20)
  }
API Endpoints:
# Scenario Management
POST /api/v1/scenarios
PUT /api/v1/scenarios/{id}
DELETE /api/v1/scenarios/{id}
GET /api/v1/scenarios/{userId}
GET /api/v1/scenarios/{id}

# Scenario Calculation
POST /api/v1/scenarios/{id}/calculate
POST /api/v1/scenarios/{id}/recalculate
GET /api/v1/scenarios/{id}/results

# Scenario Comparison
POST /api/v1/scenarios/compare
GET /api/v1/scenarios/comparison/{comparisonId}

# What-If Analysis
POST /api/v1/scenarios/{id}/what-if
POST /api/v1/scenarios/{id}/sensitivity-analysis
POST /api/v1/scenarios/{id}/monte-carlo

# Baseline
POST /api/v1/scenarios/baseline/create
GET /api/v1/scenarios/baseline/{userId}/current
Data Models:
TABLE: baseline_snapshots
- id: UUID (PK)
- user_id: UUID (FK to users)
- snapshot_date: TIMESTAMP
- age: INTEGER
- financial_state: JSON (complete state)
- tax_status: JSON
- created_at: TIMESTAMP

TABLE: scenarios
- id: UUID (PK)
- user_id: UUID (FK to users)
- name: VARCHAR(255)
- description: TEXT
- scenario_type: ENUM(...)
- baseline_snapshot_id: UUID (FK to baseline_snapshots)
- assumptions: JSON
- modifications: JSON
- status: ENUM('DRAFT', 'CALCULATED', 'ARCHIVED')
- created_at: TIMESTAMP
- last_accessed: TIMESTAMP
- expires_at: TIMESTAMP

TABLE: scenario_results
- scenario_id: UUID (PK, FK to scenarios)
- projections: JSON
- metrics: JSON
- risks: JSON
- probability_distribution: JSON
- calculated_at: TIMESTAMP

TABLE: scenario_comparisons
- id: UUID (PK)
- user_id: UUID (FK to users)
- name: VARCHAR(255)
- scenario_ids: JSON (array of UUIDs)
- comparison_data: JSON
- created_at: TIMESTAMP

TABLE: what_if_analyses
- id: UUID (PK)
- base_scenario_id: UUID (FK to scenarios)
- variables_tested: JSON
- results: JSON
- sensitivity_analysis: JSON
- created_at: TIMESTAMP

INDEX on scenarios(user_id, status, last_accessed)
INDEX on scenario_results(scenario_id)
This completes Scenario Analysis & What-If Modeling. Now proceeding to the Personalization Engine...
 
Feature 10.4: Personalization Engine
Feature Name: Adaptive Learning and Personalization System
User Story: As a user, I want the system to learn from my behavior, preferences, and feedback so that recommendations and advice become increasingly relevant and tailored to my specific situation over time.
Acceptance Criteria:
•	Learn from user interactions and behavior
•	Adapt recommendation style to user preferences
•	Track which recommendations users act on
•	Adjust priority and content based on success rates
•	Personalize communication frequency and channels
•	Adapt to user's financial literacy level
•	Remember user preferences across sessions
•	A/B test recommendation approaches
•	Provide transparency into personalization
Technical Requirements:
•	Machine learning models (collaborative filtering, content-based)
•	Behavioral tracking system
•	Feedback loop mechanism
•	A/B testing framework
•	Preference learning algorithms
•	User segmentation
•	Model retraining pipeline
•	Explainable AI for transparency
Constraints:
•	Must respect user privacy (GDPR/POPIA compliant)
•	Cannot make fully automated regulated financial decisions
•	Must allow user to override personalization
•	Model updates: Weekly retraining
•	Minimum data: 30 days of interactions before full personalization
•	Performance: Recommendations generated in <3 seconds
Implementation Approach:
SERVICE: PersonalizationEngine

# ===== USER PROFILE =====
FUNCTION build_user_profile(user_id: uuid) -> UserProfile:
  
  # Demographic factors
  demographics = {
    age: get_user_age(user_id),
    life_stage: determine_life_stage(user_id),
    country: get_primary_country(user_id),
    income_level: categorize_income_level(user_id),
    net_worth_level: categorize_net_worth(user_id)
  }
  
  # Behavioral factors
  behavior = {
    engagement_level: calculate_engagement_level(user_id),
    login_frequency: calculate_login_frequency(user_id),
    feature_usage: track_feature_usage(user_id),
    recommendation_interaction_rate: calculate_interaction_rate(user_id),
    goal_completion_rate: calculate_goal_completion_rate(user_id),
    average_session_duration: calculate_avg_session_duration(user_id)
  }
  
  # Preference factors
  preferences = {
    risk_tolerance: get_risk_tolerance(user_id),
    investment_style: infer_investment_style(user_id),
    communication_preference: get_communication_preference(user_id),
    detail_level_preference: infer_detail_preference(user_id),
    recommendation_categories_preferred: get_preferred_categories(user_id),
    notification_frequency: get_notification_frequency(user_id)
  }
  
  # Financial sophistication
  sophistication = {
    financial_literacy_score: assess_financial_literacy(user_id),
    complexity_comfortable_with: infer_complexity_level(user_id),
    terminology_familiarity: assess_terminology_knowledge(user_id),
    self_reported_expertise: get_self_reported_expertise(user_id)
  }
  
  # Historical performance
  history = {
    recommendations_accepted: get_accepted_recommendations(user_id),
    recommendations_dismissed: get_dismissed_recommendations(user_id),
    average_time_to_action: calculate_avg_time_to_action(user_id),
    most_successful_recommendation_types: identify_successful_types(user_id),
    abandoned_features: identify_abandoned_features(user_id)
  }
  
  RETURN {
    user_id: user_id,
    demographics: demographics,
    behavior: behavior,
    preferences: preferences,
    sophistication: sophistication,
    history: history,
    profile_completeness: calculate_profile_completeness(demographics, behavior, preferences),
    last_updated: NOW()
  }


# ===== BEHAVIORAL TRACKING =====
FUNCTION track_user_interaction(
  user_id: uuid,
  interaction: UserInteraction
) -> void:
  
  # Record interaction
  interaction_record = {
    user_id: user_id,
    interaction_type: interaction.type,
    target_id: interaction.target_id,
    target_type: interaction.target_type,
    action: interaction.action,
    context: interaction.context,
    timestamp: NOW()
  }
  
  store_interaction(interaction_record)
  
  # Update real-time profile elements
  MATCH interaction.type:
    CASE 'RECOMMENDATION_VIEWED':
      increment_metric(user_id, 'recommendations_viewed')
    
    CASE 'RECOMMENDATION_ACCEPTED':
      increment_metric(user_id, 'recommendations_accepted')
      record_successful_recommendation(
        user_id,
        interaction.target_id,
        interaction.recommendation_category
      )
    
    CASE 'RECOMMENDATION_DISMISSED':
      increment_metric(user_id, 'recommendations_dismissed')
      record_dismissal_reason(user_id, interaction.target_id, interaction.reason)
    
    CASE 'FEATURE_USED':
      record_feature_usage(user_id, interaction.feature_name)
    
    CASE 'GOAL_CREATED':
      record_goal_type_preference(user_id, interaction.goal_type)
    
    CASE 'CONTENT_READ':
      record_content_interest(user_id, interaction.content_topic)
    
    CASE 'TIME_SPENT':
      update_avg_session_duration(user_id, interaction.duration)
  
  # Trigger personalization update if threshold met
  IF should_update_personalization(user_id):
    async_update_user_personalization(user_id)


# ===== RECOMMENDATION PERSONALIZATION =====
FUNCTION personalize_recommendations(
  user_id: uuid,
  base_recommendations: array[Recommendation]
) -> array[PersonalizedRecommendation]:
  
  profile = build_user_profile(user_id)
  
  personalized = []
  
  FOR EACH rec IN base_recommendations:
    # Calculate personalization score
    personalization_score = calculate_personalization_score(rec, profile)
    
    # Adjust recommendation based on profile
    personalized_rec = {
      ...rec,
      personalization_score: personalization_score,
      
      # Adjust title based on sophistication
      title: adapt_title_to_sophistication(rec.title, profile.sophistication),
      
      # Adjust description detail level
      description: adapt_description_detail(rec.description, profile.preferences.detail_level_preference),
      
      # Adjust tone
      tone: adapt_tone(profile.demographics.age, profile.sophistication),
      
      # Add personalized reasoning
      personalized_reasoning: generate_personalized_reasoning(rec, profile),
      
      # Adjust estimated benefit format
      benefit_presentation: adapt_benefit_presentation(rec.estimated_benefit, profile),
      
      # Add relevant examples
      examples: generate_relevant_examples(rec, profile),
      
      # Adjust priority based on user history
      adjusted_priority: adjust_priority_for_user(rec.priority, rec.category, profile)
    }
    
    personalized.append(personalized_rec)
  
  # Re-rank based on personalization
  ranked = rank_by_personalization(personalized, profile)
  
  # Filter out recommendations user consistently dismisses
  filtered = filter_consistently_dismissed(ranked, profile)
  
  RETURN filtered


FUNCTION calculate_personalization_score(
  recommendation: Recommendation,
  profile: UserProfile
) -> decimal:
  
  score = 0.0
  
  # Category preference weight (40%)
  category_preference = profile.history.most_successful_recommendation_types[recommendation.category] OR 0.5
  score += category_preference * 0.40
  
  # Sophistication match (20%)
  sophistication_match = assess_sophistication_match(recommendation, profile.sophistication)
  score += sophistication_match * 0.20
  
  # Life stage relevance (20%)
  life_stage_relevance = assess_life_stage_relevance(recommendation, profile.demographics)
  score += life_stage_relevance * 0.20
  
  # Timing appropriateness (10%)
  timing_score = assess_timing(recommendation, profile.behavior)
  score += timing_score * 0.10
  
  # Recent interaction patterns (10%)
  recency_score = assess_recency_relevance(recommendation, profile.history)
  score += recency_score * 0.10
  
  RETURN score


FUNCTION adapt_description_detail(
  description: string,
  detail_preference: enum['CONCISE', 'MODERATE', 'DETAILED']
) -> string:
  
  MATCH detail_preference:
    CASE 'CONCISE':
      # Extract key sentence only
      RETURN extract_key_sentence(description) + " [Show more]"
    
    CASE 'MODERATE':
      # Keep 2-3 sentences
      RETURN extract_summary(description, sentences: 3)
    
    CASE 'DETAILED':
      # Full description plus additional context
      RETURN description + "\n\n" + generate_additional_context(description)


FUNCTION generate_personalized_reasoning(
  recommendation: Recommendation,
  profile: UserProfile
) -> array[string]:
  
  reasoning = []
  
  # Add life-stage specific reasoning
  MATCH profile.demographics.life_stage:
    CASE 'EARLY_CAREER':
      IF recommendation.category = 'RETIREMENT':
        reasoning.append("Starting early gives your investments decades to grow through compounding")
    
    CASE 'MID_CAREER':
      IF recommendation.category = 'PROTECTION':
        reasoning.append("At your stage, protecting your family's financial security is crucial")
    
    CASE 'PRE_RETIREMENT':
      IF recommendation.category = 'TAX':
        reasoning.append("Tax planning now can significantly impact your retirement income")
  
  # Add country-specific reasoning
  IF profile.demographics.country = 'UK':
    reasoning.append("This takes advantage of UK tax allowances and reliefs")
  ELSE IF profile.demographics.country = 'SA':
    reasoning.append("This optimizes for South African tax efficiency")
  
  # Add historical success reasoning
  IF profile.history.similar_recommendations_successful:
    reasoning.append("Similar recommendations have worked well for you in the past")
  
  RETURN reasoning


# ===== COLLABORATIVE FILTERING =====
FUNCTION get_collaborative_recommendations(user_id: uuid) -> array[Recommendation]:
  
  # Find similar users
  similar_users = find_similar_users(user_id, count: 20)
  
  # Get recommendations that similar users accepted
  collaborative_recommendations = []
  
  FOR EACH similar_user IN similar_users:
    accepted_recs = get_accepted_recommendations(similar_user.user_id)
    
    FOR EACH rec IN accepted_recs:
      # Check if this user hasn't seen this recommendation type yet
      IF NOT user_has_seen_recommendation_type(user_id, rec.type):
        
        # Calculate relevance score
        relevance = calculate_collaborative_relevance(
          recommendation: rec,
          target_user_id: user_id,
          source_user_similarity: similar_user.similarity_score
        )
        
        collaborative_recommendations.append({
          recommendation: rec,
          relevance_score: relevance,
          source: 'COLLABORATIVE_FILTERING',
          similar_user_count: COUNT(similar_users WHERE accepted this rec)
        })
  
  # Rank and return top recommendations
  ranked = SORT(collaborative_recommendations, BY relevance_score DESC)
  
  RETURN ranked[0:5]  # Top 5


FUNCTION find_similar_users(target_user_id: uuid, count: integer) -> array[SimilarUser]:
  
  target_profile = build_user_profile(target_user_id)
  all_users = get_all_active_users()
  
  similarities = []
  
  FOR EACH user IN all_users:
    IF user.id = target_user_id:
      CONTINUE  # Skip self
    
    user_profile = build_user_profile(user.id)
    
    # Calculate similarity score
    similarity = calculate_profile_similarity(target_profile, user_profile)
    
    IF similarity > 0.5:  # Threshold
      similarities.append({
        user_id: user.id,
        similarity_score: similarity,
        common_attributes: identify_common_attributes(target_profile, user_profile)
      })
  
  # Sort by similarity
  sorted_similar = SORT(similarities, BY similarity_score DESC)
  
  RETURN sorted_similar[0:count]


FUNCTION calculate_profile_similarity(
  profile_a: UserProfile,
  profile_b: UserProfile
) -> decimal:
  
  # Weighted similarity across dimensions
  
  # Demographic similarity (30%)
  demo_similarity = (
    age_similarity(profile_a.demographics.age, profile_b.demographics.age) * 0.4 +
    (profile_a.demographics.life_stage = profile_b.demographics.life_stage ? 1.0 : 0.0) * 0.3 +
    income_similarity(profile_a.demographics.income_level, profile_b.demographics.income_level) * 0.3
  )
  
  # Behavioral similarity (30%)
  behavior_similarity = (
    engagement_similarity(profile_a.behavior.engagement_level, profile_b.behavior.engagement_level) * 0.5 +
    feature_usage_overlap(profile_a.behavior.feature_usage, profile_b.behavior.feature_usage) * 0.5
  )
  
  # Preference similarity (20%)
  pref_similarity = (
    (profile_a.preferences.risk_tolerance = profile_b.preferences.risk_tolerance ? 1.0 : 0.5) * 0.5 +
    category_preference_overlap(profile_a.preferences, profile_b.preferences) * 0.5
  )
  
  # Financial sophistication similarity (20%)
  soph_similarity = ABS(profile_a.sophistication.financial_literacy_score - 
                        profile_b.sophistication.financial_literacy_score) / 10.0
  soph_similarity = 1.0 - soph_similarity  # Invert so closer = higher score
  
  # Weighted total
  total_similarity = (
    demo_similarity * 0.30 +
    behavior_similarity * 0.30 +
    pref_similarity * 0.20 +
    soph_similarity * 0.20
  )
  
  RETURN total_similarity


# ===== A/B TESTING FRAMEWORK =====
FUNCTION assign_ab_test_variant(
  user_id: uuid,
  test_name: string
) -> string:
  
  # Check if user already assigned to this test
  existing_assignment = get_ab_test_assignment(user_id, test_name)
  
  IF existing_assignment:
    RETURN existing_assignment.variant
  
  # Get test configuration
  test_config = get_ab_test_config(test_name)
  
  IF NOT test_config.active:
    RETURN 'CONTROL'  # Default if test not active
  
  # Assign variant based on consistent hash
  hash = consistent_hash(user_id + test_name)
  variant_index = hash MOD 100
  
  cumulative = 0
  FOR EACH variant IN test_config.variants:
    cumulative += variant.traffic_percentage
    IF variant_index < cumulative:
      selected_variant = variant.name
      BREAK
  
  # Record assignment
  record_ab_test_assignment(user_id, test_name, selected_variant)
  
  RETURN selected_variant


FUNCTION apply_ab_test_personalization(
  recommendation: Recommendation,
  user_id: uuid
) -> Recommendation:
  
  # Example tests
  
  # Test 1: Benefit emphasis
  benefit_test_variant = assign_ab_test_variant(user_id, 'BENEFIT_EMPHASIS')
  
  MATCH benefit_test_variant:
    CASE 'CONTROL':
      # Standard benefit presentation
      PASS
    
    CASE 'MONETARY_FOCUS':
      # Emphasize monetary benefits
      IF recommendation.estimated_benefit.amount:
        recommendation.title = "Save £{amount}: " + recommendation.title
    
    CASE 'PERCENTAGE_FOCUS':
      # Emphasize percentage improvements
      IF recommendation.estimated_benefit.percentage:
        recommendation.title = "Improve by {percentage}%: " + recommendation.title
  
  # Test 2: Urgency framing
  urgency_test_variant = assign_ab_test_variant(user_id, 'URGENCY_FRAMING')
  
  MATCH urgency_test_variant:
    CASE 'CONTROL':
      PASS
    
    CASE 'HIGH_URGENCY':
      IF recommendation.deadline:
        days_remaining = calculate_days_until(recommendation.deadline)
        recommendation.description = "⚠️ Only {days} days left! " + recommendation.description
    
    CASE 'LOW_PRESSURE':
      # Remove urgency language
      recommendation.description = remove_urgency_words(recommendation.description)
  
  # Test 3: Social proof
  social_proof_variant = assign_ab_test_variant(user_id, 'SOCIAL_PROOF')
  
  MATCH social_proof_variant:
    CASE 'CONTROL':
      PASS
    
    CASE 'SOCIAL_PROOF':
      # Add social proof element
      similar_users_count = count_similar_users_who_accepted(recommendation)
      IF similar_users_count > 10:
        recommendation.description += "\n\n✓ {count} users in similar situations have acted on this."
  
  RETURN recommendation


FUNCTION record_ab_test_outcome(
  user_id: uuid,
  test_name: string,
  recommendation_id: uuid,
  outcome: enum['VIEWED', 'ACCEPTED', 'DISMISSED', 'IGNORED']
) -> void:
  
  variant = get_ab_test_assignment(user_id, test_name).variant
  
  outcome_record = {
    test_name: test_name,
    variant: variant,
    user_id: user_id,
    recommendation_id: recommendation_id,
    outcome: outcome,
    timestamp: NOW()
  }
  
  store_ab_test_outcome(outcome_record)


FUNCTION analyze_ab_test_results(test_name: string) -> ABTestAnalysis:
  
  test_config = get_ab_test_config(test_name)
  
  variant_performance = []
  
  FOR EACH variant IN test_config.variants:
    outcomes = get_ab_test_outcomes(test_name, variant.name)
    
    total = outcomes.count
    accepted = COUNT(outcomes WHERE outcome = 'ACCEPTED')
    dismissed = COUNT(outcomes WHERE outcome = 'DISMISSED')
    viewed = COUNT(outcomes WHERE outcome = 'VIEWED')
    
    acceptance_rate = (accepted / total) * 100
    dismissal_rate = (dismissed / total) * 100
    engagement_rate = ((viewed + accepted) / total) * 100
    
    variant_performance.append({
      variant_name: variant.name,
      sample_size: total,
      acceptance_rate: acceptance_rate,
      dismissal_rate: dismissal_rate,
      engagement_rate: engagement_rate,
      statistical_significance: calculate_statistical_significance(
        variant,
        test_config.variants[0],  # Compare to control
        outcomes
      )
    })
  
  # Determine winner
  winner = MAX(variant_performance, BY acceptance_rate)
  
  # Calculate lift over control
  control_performance = FIRST(variant_performance WHERE variant_name = 'CONTROL')
  lift = ((winner.acceptance_rate - control_performance.acceptance_rate) / 
          control_performance.acceptance_rate) * 100
  
  RETURN {
    test_name: test_name,
    variant_performance: variant_performance,
    winner: winner.variant_name,
    lift_over_control: lift,
    recommendation: IF lift > 10 AND winner.statistical_significance > 0.95 THEN
                      "Roll out winning variant to all users"
                   ELSE
                      "Continue testing or refine hypothesis"
  }


# ===== FEEDBACK LOOP =====
FUNCTION process_user_feedback(
  user_id: uuid,
  feedback: Feedback
) -> void:
  
  # Store feedback
  store_feedback(feedback)
  
  # Update personalization based on feedback
  MATCH feedback.type:
    CASE 'RECOMMENDATION_RATING':
      # User rated a recommendation (1-5 stars)
      update_recommendation_type_preference(
        user_id,
        feedback.recommendation_category,
        feedback.rating
      )
    
    CASE 'FEATURE_RATING':
      # User rated a feature
      update_feature_preference(
        user_id,
        feedback.feature_name,
        feedback.rating
      )
    
    CASE 'CONTENT_PREFERENCE':
      # User indicated preference for content style
      update_content_style_preference(
        user_id,
        feedback.preferred_style
      )
    
    CASE 'NOTIFICATION_PREFERENCE':
      # User adjusted notification settings
      update_notification_preferences(
        user_id,
        feedback.notification_settings
      )
    
    CASE 'GENERAL_FEEDBACK':
      # Qualitative feedback - analyze sentiment
      sentiment = analyze_sentiment(feedback.text)
      update_satisfaction_score(user_id, sentiment)
  
  # Trigger model retraining if significant feedback accumulated
  IF should_retrain_model(user_id):
    schedule_model_retraining(user_id)


# ===== MODEL RETRAINING =====
FUNCTION retrain_personalization_models() -> void:
  
  # Run weekly (scheduled job)
  
  # Get all users with sufficient interaction history
  eligible_users = get_users_with_min_interactions(min_interactions: 50)
  
  FOR EACH user IN eligible_users:
    # Extract features
    features = extract_user_features(user.id)
    
    # Extract labels (successful recommendations)
    labels = extract_recommendation_outcomes(user.id)
    
    # Train user-specific model
    model = train_recommendation_model(features, labels)
    
    # Evaluate model
    performance = evaluate_model(model, validation_data)
    
    # Store model if performance acceptable
    IF performance.accuracy > 0.70:
      store_user_model(user.id, model, performance)
  
  # Train global collaborative filtering model
  global_cf_model = train_collaborative_filtering_model(all_user_interactions)
  store_global_model('COLLABORATIVE_FILTERING', global_cf_model)
  
  # Log retraining metrics
  log_model_retraining_metrics({
    users_retrained: eligible_users.count,
    average_accuracy: AVERAGE(all_models.accuracy),
    timestamp: NOW()
  })


# ===== EXPLAINABILITY =====
FUNCTION explain_personalization(
  user_id: uuid,
  recommendation_id: uuid
) -> PersonalizationExplanation:
  
  recommendation = get_recommendation(recommendation_id)
  profile = build_user_profile(user_id)
  
  # Explain why this recommendation was shown
  explanation = {
    primary_reasons: [],
    contributing_factors: [],
    how_to_improve_relevance: []
  }
  
  # Analyze recommendation selection
  IF recommendation.category IN profile.history.most_successful_recommendation_types:
    explanation.primary_reasons.append(
      "You've successfully acted on similar {category} recommendations before"
    )
  
  IF recommendation matches profile.demographics.life_stage:
    explanation.primary_reasons.append(
      "This is particularly relevant for your current life stage"
    )
  
  IF recommendation.estimated_benefit.amount > profile.typical_benefit_threshold:
    explanation.primary_reasons.append(
      "The potential benefit (£{amount}) is significant for your situation"
    )
  
  # Contributing factors
  IF recommendation selected via collaborative filtering:
    similar_count = count_similar_users_who_accepted(recommendation_id)
    explanation.contributing_factors.append(
      "{count} users with similar profiles have benefited from this"
    )
  
  IF recommendation.urgency_score > 80:
    explanation.contributing_factors.append(
      "This is time-sensitive and requires prompt action"
    )
  
  # How to improve relevance
  explanation.how_to_improve_relevance = [
    "Rate recommendations to help us understand your preferences",
    "Complete your financial goals for more targeted advice",
    "Provide feedback on what types of recommendations you find most valuable"
  ]
  
  RETURN explanation
API Endpoints:
# Profile Management
GET /api/v1/personalization/profile/{userId}
PUT /api/v1/personalization/profile/{userId}/preferences
POST /api/v1/personalization/profile/{userId}/refresh

# Interaction Tracking
POST /api/v1/personalization/track-interaction
POST /api/v1/personalization/track-event

# Feedback
POST /api/v1/personalization/feedback
GET /api/v1/personalization/feedback/{userId}/history

# A/B Testing
GET /api/v1/personalization/ab-test/{testName}/variant
POST /api/v1/personalization/ab-test/{testName}/outcome

# Explainability
GET /api/v1/personalization/explain/{recommendationId}
GET /api/v1/personalization/why-seeing-this

# Admin (for monitoring)
GET /api/v1/personalization/model-performance
POST /api/v1/personalization/retrain-models
GET /api/v1/personalization/ab-test/{testName}/results
Data Models:
TABLE: user_personalization_profiles
- user_id: UUID (PK, FK to users)
- engagement_level: ENUM('LOW', 'MEDIUM', 'HIGH')
- financial_literacy_score: INTEGER (1-10)
- risk_tolerance: ENUM('LOW', 'MEDIUM', 'HIGH')
- detail_preference: ENUM('CONCISE', 'MODERATE', 'DETAILED')
- preferred_categories: JSON (array)
- dismissed_categories: JSON (array)
- communication_style: VARCHAR(50)
- notification_frequency: ENUM('REAL_TIME', 'DAILY', 'WEEKLY', 'MONTHLY')
- preferred_channels: JSON (array: 'EMAIL', 'IN_APP', 'SMS')
- profile_completeness: DECIMAL(5,2)
- last_updated: TIMESTAMP
- created_at: TIMESTAMP

TABLE: user_interactions
- id: UUID (PK)
- user_id: UUID (FK to users)
- interaction_type: ENUM('RECOMMENDATION_VIEWED', 'RECOMMENDATION_ACCEPTED', 
                        'RECOMMENDATION_DISMISSED', 'FEATURE_USED', 'GOAL_CREATED',
                        'CONTENT_READ', 'TIME_SPENT', 'SEARCH_PERFORMED')
- target_id: UUID
- target_type: VARCHAR(50)
- action: VARCHAR(100)
- context: JSON
- session_id: UUID
- timestamp: TIMESTAMP
- device_type: VARCHAR(50)

TABLE: recommendation_feedback
- id: UUID (PK)
- recommendation_id: UUID (FK to ai_recommendations)
- user_id: UUID (FK to users)
- feedback_type: ENUM('RATING', 'HELPFUL', 'NOT_HELPFUL', 'ALREADY_DONE', 'NOT_RELEVANT')
- rating: INTEGER (1-5, nullable)
- feedback_text: TEXT
- timestamp: TIMESTAMP

TABLE: recommendation_outcomes
- id: UUID (PK)
- recommendation_id: UUID (FK to ai_recommendations)
- user_id: UUID (FK to users)
- outcome: ENUM('ACCEPTED', 'PARTIALLY_ACCEPTED', 'DISMISSED', 'IGNORED', 'EXPIRED')
- outcome_date: TIMESTAMP
- time_to_action_days: INTEGER
- actual_benefit_realized: DECIMAL(15,2) (measured post-action)
- notes: TEXT

TABLE: category_preferences
- user_id: UUID (FK to users)
- category: VARCHAR(100)
- preference_score: DECIMAL(5,2) (0-1 scale)
- acceptance_count: INTEGER
- dismissal_count: INTEGER
- total_shown: INTEGER
- last_interaction: TIMESTAMP
- PRIMARY KEY (user_id, category)

TABLE: similar_user_mappings
- user_id: UUID (FK to users)
- similar_user_id: UUID (FK to users)
- similarity_score: DECIMAL(5,4)
- common_attributes: JSON
- calculated_at: TIMESTAMP
- PRIMARY KEY (user_id, similar_user_id)

TABLE: ab_test_configurations
- test_name: VARCHAR(100) (PK)
- description: TEXT
- hypothesis: TEXT
- start_date: DATE
- end_date: DATE
- active: BOOLEAN
- variants: JSON (array of {name, description, traffic_percentage})
- success_metric: VARCHAR(100)
- minimum_sample_size: INTEGER
- created_by: UUID (FK to users - admin)
- created_at: TIMESTAMP

TABLE: ab_test_assignments
- id: UUID (PK)
- user_id: UUID (FK to users)
- test_name: VARCHAR(100) (FK to ab_test_configurations)
- variant: VARCHAR(50)
- assigned_at: TIMESTAMP
- UNIQUE (user_id, test_name)

TABLE: ab_test_outcomes
- id: UUID (PK)
- test_name: VARCHAR(100) (FK to ab_test_configurations)
- variant: VARCHAR(50)
- user_id: UUID (FK to users)
- recommendation_id: UUID (FK to ai_recommendations)
- outcome: ENUM('VIEWED', 'ACCEPTED', 'DISMISSED', 'IGNORED', 'COMPLETED')
- timestamp: TIMESTAMP
- context: JSON

TABLE: personalization_models
- user_id: UUID (PK, FK to users)
- model_type: ENUM('RECOMMENDATION_RANKING', 'CONTENT_PREFERENCE', 'TIMING_OPTIMIZATION')
- model_data: BYTEA (serialized model)
- model_version: VARCHAR(20)
- training_date: TIMESTAMP
- performance_metrics: JSON
- feature_importance: JSON
- active: BOOLEAN DEFAULT TRUE

TABLE: user_feature_vectors
- user_id: UUID (PK, FK to users)
- features: JSON (feature vector for ML models)
- calculated_at: TIMESTAMP

TABLE: personalization_events_log
- id: UUID (PK)
- user_id: UUID (FK to users)
- event_type: VARCHAR(100)
- event_data: JSON
- timestamp: TIMESTAMP
- processing_status: ENUM('PENDING', 'PROCESSED', 'FAILED')

INDEX on user_interactions(user_id, timestamp DESC)
INDEX on user_interactions(interaction_type, timestamp DESC)
INDEX on recommendation_outcomes(user_id, outcome, outcome_date)
INDEX on ab_test_outcomes(test_name, variant, outcome)
INDEX on category_preferences(user_id, preference_score DESC)
INDEX on personalization_events_log(processing_status, timestamp)
Error Handling:
ERROR CASES:
1. Insufficient interaction data for personalization
   - Response: 200 OK
   - Behavior: Fall back to general recommendations
   - Message: "Building your personalized profile. Complete more actions for tailored advice"
   
2. Model training failure
   - Response: 500 Internal Server Error (logged internally)
   - Behavior: Use previous model version or fallback
   - User impact: None (transparent failover)
   
3. A/B test assignment conflict
   - Response: 200 OK
   - Behavior: Use existing assignment
   - Log: Warning for investigation
   
4. Feature extraction failure
   - Response: 200 OK
   - Behavior: Use partial features or defaults
   - Log: Error for debugging
   
5. User opts out of personalization
   - Response: 200 OK
   - Behavior: Disable personalization, use standard recommendations
   - Store: User preference permanently

EDGE CASES:
- New user: Use demographic-based recommendations until sufficient data
- Inactive user returning: Check for stale profile, update before personalizing
- User behavior changes dramatically: Detect concept drift, retrain model
- Privacy mode: Limit tracking, use aggregated patterns only
- Multiple devices: Merge interaction data across sessions
- Shared account: Detect multiple user patterns, suggest separate profiles
- Extreme outlier user: Fall back to robust general recommendations
- Testing environment: Separate A/B test assignments from production
Performance Considerations:
•	Profile building: Cache for 1 hour, recalculate on significant events
•	Interaction tracking: Async processing via message queue
•	Model inference: <100ms for recommendation scoring
•	Similarity calculation: Pre-compute weekly for active users
•	A/B test assignment: Hash-based, deterministic, <5ms
•	Feature extraction: Batch process daily, cache results
•	Model retraining: Weekly batch job, off-peak hours
•	Expected interactions per user: 10-100 per session
•	Collaborative filtering: Use approximate nearest neighbors for scale
•	Real-time personalization: Hot path <200ms end-to-end
 

11. TAX INFORMATION MODULE
Feature 11.1: Comprehensive Tax Reference Library
Feature Name: Interactive Tax Rates, Allowances, and Rules Reference
User Story: As a user, I want to access a comprehensive, up-to-date reference of all tax rates, allowances, bands, and rules for both UK and South Africa so that I understand the tax treatment of my financial decisions and can verify calculations made by the system.
Acceptance Criteria:
•	Display current tax rates and allowances for both UK and SA
•	Show historical tax rates (previous 5 years minimum)
•	Include detailed explanations of each tax type
•	Provide examples and calculators for each tax
•	Tax year selector (switch between years)
•	Country toggle (UK/SA/Both)
•	Search functionality for specific tax topics
•	Links to official government resources
•	Export tax reference data
•	Comparison tool (year-over-year changes)
•	Personal view (shows user's applicable rates based on status)
•	Educational content about tax planning
Technical Requirements:
•	Tax data repository (versioned by tax year)
•	Content management system for educational content
•	Search indexing for tax topics
•	Calculation widgets embedded in page
•	Historical data storage and retrieval
•	Real-time updates when tax year changes
•	Responsive layout for mobile
•	Integration with Tax Intelligence Engine
Constraints:
•	Data must be sourced from official government publications
•	Updates required at start of each tax year (April for UK, March for SA)
•	Historical data retained indefinitely
•	Must include disclaimer about using official sources for filing
•	Cannot provide tax filing advice (information only)
Implementation Approach:
SERVICE: TaxInformationService

# ===== TAX INFORMATION RETRIEVAL =====
FUNCTION get_tax_information_page(
  user_id: uuid,
  country: enum['UK', 'SA', 'BOTH'],
  tax_year: string
) -> TaxInformationPage:
  
  # Get user context for personalization
  user_context = get_user_context(user_id)
  
  # Retrieve tax data
  IF country = 'BOTH':
    uk_data = get_uk_tax_data(tax_year)
    sa_data = get_sa_tax_data(tax_year)
    
    RETURN {
      view_mode: 'COMPARISON',
      uk_tax_data: uk_data,
      sa_tax_data: sa_data,
      comparison: generate_uk_sa_comparison(uk_data, sa_data),
      personalized_view: generate_personalized_view(user_context, uk_data, sa_data)
    }
  
  ELSE IF country = 'UK':
    uk_data = get_uk_tax_data(tax_year)
    RETURN {
      view_mode: 'UK_ONLY',
      tax_data: uk_data,
      personalized_view: generate_personalized_uk_view(user_context, uk_data)
    }
  
  ELSE IF country = 'SA':
    sa_data = get_sa_tax_data(tax_year)
    RETURN {
      view_mode: 'SA_ONLY',
      tax_data: sa_data,
      personalized_view: generate_personalized_sa_view(user_context, sa_data)
    }


# ===== UK TAX DATA STRUCTURE =====
FUNCTION get_uk_tax_data(tax_year: string) -> UkTaxData:
  
  config = get_uk_tax_config(tax_year)
  
  RETURN {
    tax_year: tax_year,
    tax_year_dates: {
      start: format_date(tax_year, 'start'),  # 6 April
      end: format_date(tax_year, 'end')       # 5 April
    },
    
    # Income Tax
    income_tax: {
      personal_allowance: {
        standard: config.personal_allowance,  # £12,570 for 2024/25
        description: "Amount you can earn tax-free",
        taper: {
          threshold: 100000,
          rate: "£1 lost for every £2 over £100,000",
          fully_lost_at: 125140
        },
        restrictions: [
          "Reduced if income over £100,000",
          "Not available if income over £125,140",
          "May be restricted if claiming certain benefits"
        ]
      },
      
      tax_bands: [
        {
          name: "Basic Rate",
          band: "£0 - £37,700",
          rate: 0.20,
          rate_display: "20%",
          description: "First £37,700 of taxable income",
          applies_to: "Taxable income after personal allowance"
        },
        {
          name: "Higher Rate",
          band: "£37,701 - £125,140",
          rate: 0.40,
          rate_display: "40%",
          description: "Taxable income between £37,701 and £125,140"
        },
        {
          name: "Additional Rate",
          band: "Over £125,140",
          rate: 0.45,
          rate_display: "45%",
          description: "Taxable income over £125,140"
        }
      ],
      
      scottish_tax_bands: [
        {
          name: "Starter Rate",
          band: "£0 - £2,162",
          rate: 0.19,
          rate_display: "19%",
          note: "Applies to Scottish residents only"
        },
        {
          name: "Basic Rate",
          band: "£2,163 - £13,118",
          rate: 0.20,
          rate_display: "20%"
        },
        {
          name: "Intermediate Rate",
          band: "£13,119 - £31,092",
          rate: 0.21,
          rate_display: "21%"
        },
        {
          name: "Higher Rate",
          band: "£31,093 - £125,140",
          rate: 0.42,
          rate_display: "42%"
        },
        {
          name: "Top Rate",
          band: "Over £125,140",
          rate: 0.47,
          rate_display: "47%"
        }
      ],
      
      savings_rates: {
        starting_rate: {
          amount: 5000,
          rate: 0.00,
          condition: "Available if income below £17,570"
        },
        personal_savings_allowance: {
          basic_rate: 1000,
          higher_rate: 500,
          additional_rate: 0,
          description: "Tax-free interest on savings"
        }
      },
      
      marriage_allowance: {
        transferable_amount: 1260,  # 10% of personal allowance
        tax_saving: 252,  # 20% of transferable amount
        eligibility: "One partner not using full personal allowance, other a basic rate taxpayer"
      },
      
      examples: [
        {
          scenario: "£30,000 salary",
          calculation: {
            gross_income: 30000,
            personal_allowance: 12570,
            taxable_income: 17430,
            tax_due: 3486,
            effective_rate: "11.62%",
            breakdown: [
              "£17,430 @ 20% = £3,486"
            ]
          }
        },
        {
          scenario: "£60,000 salary",
          calculation: {
            gross_income: 60000,
            personal_allowance: 12570,
            taxable_income: 47430,
            basic_rate_tax: 7540,
            higher_rate_tax: 3892,
            total_tax: 11432,
            effective_rate: "19.05%",
            breakdown: [
              "£37,700 @ 20% = £7,540",
              "£9,730 @ 40% = £3,892"
            ]
          }
        }
      ]
    },
    
    # National Insurance
    national_insurance: {
      class_1_employee: {
        primary_threshold: config.ni_primary_threshold,  # £12,570
        upper_earnings_limit: config.ni_upper_earnings_limit,  # £50,270
        rates: [
          {
            band: "£12,570 - £50,270",
            rate: 0.08,
            rate_display: "8%"
          },
          {
            band: "Over £50,270",
            rate: 0.02,
            rate_display: "2%"
          }
        ]
      },
      
      class_1_employer: {
        secondary_threshold: 9100,
        rate: 0.138,
        rate_display: "13.8%",
        note: "Paid by employer on earnings above £9,100"
      },
      
      class_2_self_employed: {
        small_profits_threshold: 12570,
        weekly_rate: 3.45,
        annual_equivalent: 179.40,
        note: "Flat rate if profits over £12,570"
      },
      
      class_4_self_employed: {
        lower_profits_limit: 12570,
        upper_profits_limit: 50270,
        rates: [
          {
            band: "£12,570 - £50,270",
            rate: 0.06,
            rate_display: "6%"
          },
          {
            band: "Over £50,270",
            rate: 0.02,
            rate_display: "2%"
          }
        ]
      }
    },
    
    # Capital Gains Tax
    capital_gains_tax: {
      annual_exempt_amount: config.cgt_annual_exemption,  # £3,000 for 2024/25
      
      rates: {
        residential_property: {
          basic_rate: 0.18,
          higher_rate: 0.24,
          rates_display: "18% / 24%"
        },
        other_assets: {
          basic_rate: 0.10,
          higher_rate: 0.20,
          rates_display: "10% / 20%"
        }
      },
      
      exemptions: [
        "Principal Private Residence (main home)",
        "Personal possessions worth £6,000 or less",
        "ISAs and PEPs",
        "UK Government Gilts",
        "Qualifying corporate bonds",
        "Betting, lottery or pools winnings"
      ],
      
      reliefs: {
        business_asset_disposal_relief: {
          lifetime_limit: 1000000,
          rate: 0.10,
          rate_display: "10%",
          description: "On disposal of business or business assets",
          conditions: [
            "Must have owned business for 2 years",
            "Business must be trading company",
            "Must be disposing of whole or part of business"
          ]
        },
        investors_relief: {
          lifetime_limit: 10000000,
          rate: 0.10,
          rate_display: "10%",
          description: "On disposal of unlisted trading company shares",
          conditions: [
            "Shares must be newly issued",
            "Must have held for 3 years from April 2016",
            "Must be employee or officer of company"
          ]
        }
      }
    },
    
    # Dividend Tax
    dividend_tax: {
      dividend_allowance: config.dividend_allowance,  # £500 for 2024/25
      
      rates: [
        {
          band: "Basic Rate",
          rate: 0.0875,
          rate_display: "8.75%"
        },
        {
          band: "Higher Rate",
          rate: 0.3375,
          rate_display: "33.75%"
        },
        {
          band: "Additional Rate",
          rate: 0.3935,
          rate_display: "39.35%"
        }
      ],
      
      note: "Dividends received within ISAs are tax-free"
    },
    
    # ISA Allowances
    isa_allowances: {
      overall_limit: 20000,
      
      types: [
        {
          name: "Cash ISA",
          limit: 20000,
          description: "Tax-free savings account"
        },
        {
          name: "Stocks & Shares ISA",
          limit: 20000,
          description: "Tax-free investment account"
        },
        {
          name: "Lifetime ISA (LISA)",
          limit: 4000,
          description: "For first home or retirement (age 60+)",
          bonus: "25% government bonus",
          restrictions: "Must be 18-39 to open, can contribute up to age 50"
        },
        {
          name: "Innovative Finance ISA",
          limit: 20000,
          description: "Peer-to-peer lending"
        },
        {
          name: "Junior ISA",
          limit: 9000,
          description: "For children under 18",
          note: "Separate from adult allowance"
        }
      ],
      
      rules: [
        "Can only contribute to one of each type per tax year",
        "Can split £20,000 across types",
        "LISA £4,000 counts toward overall £20,000",
        "Can transfer between ISAs without affecting allowance"
      ]
    },
    
    # Pension Allowances
    pension_allowances: {
      annual_allowance: {
        standard: 60000,
        description: "Maximum pension contributions with tax relief",
        
        money_purchase_annual_allowance: {
          amount: 10000,
          triggered_by: "Accessing pension flexibly",
          description: "Reduced allowance if you've accessed pension"
        },
        
        tapered_annual_allowance: {
          threshold_income: 200000,
          adjusted_income: 260000,
          taper_rate: "£1 for every £2 over £260,000",
          minimum: 10000,
          description: "Reduced for high earners"
        },
        
        carry_forward: {
          years: 3,
          description: "Can carry forward unused allowance from previous 3 years",
          conditions: "Must have been member of pension scheme in those years"
        }
      },
      
      lifetime_allowance: {
        note: "Abolished from April 2024",
        replaced_by: {
          lump_sum_allowance: 268275,
          lump_sum_death_benefit_allowance: 1073100
        },
        historical: {
          "2023/24": 1073100,
          "2020/21 - 2022/23": 1073100,
          "2018/19 - 2019/20": 1055000
        }
      }
    },
    
    # Inheritance Tax
    inheritance_tax: {
      nil_rate_band: {
        amount: 325000,
        transferable: true,
        description: "Tax-free threshold for estates",
        transferable_note: "Unused portion can transfer to spouse"
      },
      
      residence_nil_rate_band: {
        maximum: 175000,
        description: "Additional allowance for main residence left to direct descendants",
        
        taper: {
          threshold: 2000000,
          rate: "£1 reduction for every £2 over £2m",
          fully_lost_at: 2350000
        },
        
        transferable: true,
        conditions: [
          "Must leave main residence to direct descendants",
          "Includes children, grandchildren, step-children",
          "Property must have been residence at some point"
        ]
      },
      
      rate: {
        standard: 0.40,
        rate_display: "40%",
        reduced: 0.36,
        reduced_display: "36%",
        reduced_condition: "If 10% or more of estate left to charity"
      },
      
      exemptions: [
        "Spouse/civil partner (unlimited)",
        "Charity (unlimited)",
        "Political parties (meeting certain conditions)",
        "Annual exemption: £3,000",
        "Small gifts: £250 per person",
        "Wedding gifts: £5,000 (child), £2,500 (grandchild), £1,000 (other)"
      ],
      
      pets_and_7_year_rule: {
        description: "Potentially Exempt Transfers (PETs)",
        rule: "Gifts become exempt if you survive 7 years",
        taper_relief: [
          {years: "3-4", relief: "20%"},
          {years: "4-5", relief: "40%"},
          {years: "5-6", relief: "60%"},
          {years: "6-7", relief: "80%"},
          {years: "7+", relief: "100% (fully exempt)"}
        ],
        note: "Taper relief reduces tax, not value"
      },
      
      business_property_relief: {
        rates: {
          "100%": [
            "Business or interest in business",
            "Shares in unlisted company"
          ],
          "50%": [
            "Shares controlling >50% of listed company",
            "Land, buildings, machinery owned and used in business"
          ]
        },
        holding_period: "Must be owned for 2 years"
      },
      
      agricultural_property_relief: {
        rates: {
          "100%": "Agricultural property with vacant possession or let after 1 Sept 1995",
          "50%": "Other agricultural property"
        },
        holding_period: "Must be owned for 2 years (or 7 if not occupied)"
      }
    },
    
    # Stamp Duty Land Tax
    stamp_duty: {
      residential: [
        {
          band: "£0 - £250,000",
          rate: 0.00,
          rate_display: "0%",
          first_time_buyer_band: "£0 - £425,000"
        },
        {
          band: "£250,001 - £925,000",
          rate: 0.05,
          rate_display: "5%"
        },
        {
          band: "£925,001 - £1,500,000",
          rate: 0.10,
          rate_display: "10%"
        },
        {
          band: "Over £1,500,000",
          rate: 0.12,
          rate_display: "12%"
        }
      ],
      
      additional_property_surcharge: {
        rate: 0.03,
        rate_display: "3%",
        description: "Additional 3% on all bands for second homes and buy-to-let"
      },
      
      first_time_buyer_relief: {
        threshold: 625000,
        relief_up_to: 425000,
        rate_after: 0.05,
        description: "No SDLT up to £425,000 for first-time buyers (if property ≤£625,000)"
      }
    },
    
    # Other Allowances
    other_allowances: {
      blind_persons_allowance: {
        amount: 3070,
        transferable_to_spouse: true
      },
      
      trading_allowance: {
        amount: 1000,
        description: "Tax-free trading income allowance"
      },
      
      property_allowance: {
        amount: 1000,
        description: "Tax-free property income allowance"
      }
    }
  }


# ===== SA TAX DATA STRUCTURE =====
FUNCTION get_sa_tax_data(tax_year: string) -> SaTaxData:
  
  config = get_sa_tax_config(tax_year)
  
  RETURN {
    tax_year: tax_year,
    tax_year_dates: {
      start: format_date(tax_year, 'start'),  # 1 March
      end: format_date(tax_year, 'end')       # 28/29 February
    },
    
    # Income Tax
    income_tax: {
      tax_brackets: [
        {
          band: "R0 - R237,100",
          rate: 0.18,
          rate_display: "18%",
          tax_calculation: "18% of taxable income"
        },
        {
          band: "R237,101 - R370,500",
          rate: 0.26,
          rate_display: "26%",
          tax_calculation: "R42,678 + 26% of taxable income above R237,100"
        },
        {
          band: "R370,501 - R512,800",
          rate: 0.31,
          rate_display: "31%",
          tax_calculation: "R77,362 + 31% of taxable income above R370,500"
        },
        {
          band: "R512,801 - R673,000",
          rate: 0.36,
          rate_display: "36%",
          tax_calculation: "R121,475 + 36% of taxable income above R512,800"
        },
        {
          band: "R673,001 - R857,900",
          rate: 0.39,
          rate_display: "39%",
          tax_calculation: "R179,147 + 39% of taxable income above R673,000"
        },
        {
          band: "Over R857,900",
          rate: 0.45,
          rate_display: "45%",
          tax_calculation: "R251,258 + 45% of taxable income above R857,900"
        }
      ],
      
      rebates: {
        primary: {
          amount: config.primary_rebate,  # R17,235 for 2024/25
          description: "Primary rebate for all individuals under 65",
          age_requirement: "Under 65"
        },
        secondary: {
          amount: config.secondary_rebate,  # R19,500
          description: "Additional rebate for individuals 65-74",
          age_requirement: "65-74 years",
          total_rebate: config.primary_rebate + 2265
        },
        tertiary: {
          amount: config.tertiary_rebate,  # R21,720
          description: "Additional rebate for individuals 75+",
          age_requirement: "75 years and over",
          total_rebate: config.primary_rebate + 4485
        }
      },
      
      tax_thresholds: {
        below_65: {
          amount: 95750,
          description: "Income below this amount is effectively tax-free for under 65s"
        },
        age_65_to_74: {
          amount: 148217,
          description: "Income below this amount is effectively tax-free for 65-74s"
        },
        age_75_plus: {
          amount: 165689,
          description: "Income below this amount is effectively tax-free for 75+"
        }
      },
      
      interest_exemption: {
        under_65: {
          amount: 23800,
          description: "First R23,800 of local interest income is exempt"
        },
        age_65_plus: {
          amount: 34500,
          description: "First R34,500 of local interest income is exempt for 65+"
        }
      },
      
      medical_tax_credits: {
        main_member: {
          monthly: 364,
          annual: 4368,
          description: "Medical scheme fees tax credit for main member"
        },
        first_dependent: {
          monthly: 364,
          annual: 4368
        },
        additional_dependents: {
          monthly: 246,
          annual: 2952,
          per: "each additional dependent"
        },
        
        additional_credit: {
          threshold_age_65_plus: "4 × (medical scheme contributions - tax credits)",
          threshold_disabled: "4 × (medical scheme contributions - tax credits)",
          rate: 0.33,
          rate_display: "33.3%",
          description: "Additional credit for qualifying medical expenses"
        }
      },
      
      examples: [
        {
          scenario: "R500,000 salary (age 40)",
          calculation: {
            taxable_income: 500000,
            tax_before_rebate: 86611,
            primary_rebate: 17235,
            tax_payable: 69376,
            effective_rate: "13.88%"
          }
        },
        {
          scenario: "R500,000 salary (age 70)",
          calculation: {
            taxable_income: 500000,
            tax_before_rebate: 86611,
            secondary_rebate: 19500,
            tax_payable: 67111,
            effective_rate: "13.42%"
          }
        }
      ]
    },
    
    # Capital Gains Tax
    capital_gains_tax: {
      annual_exclusion: config.cgt_annual_exclusion,  # R40,000 for 2024/25
      inclusion_rate: {
        individuals: 0.40,
        rate_display: "40%",
        description: "40% of capital gain is included in taxable income"
      },
      
      method: "Inclusion rate method",
      description: "CGT is not a separate tax. Capital gains are added to taxable income after applying inclusion rate",
      
      calculation_example: {
        capital_gain: 100000,
        annual_exclusion: 40000,
        net_gain: 60000,
        inclusion_rate: 0.40,
        taxable_amount: 24000,
        description: "R24,000 added to taxable income, taxed at marginal rate"
      },
      
      exemptions: [
        "Primary residence (main dwelling)",
        "Personal use assets (furniture, clothing, etc.)",
        "Retirement fund lump sums",
        "Proceeds from life insurance policies",
        "Compensation for personal injury, illness or defamation",
        "Annual exclusion: R40,000"
      ],
      
      special_rules: {
        primary_residence: {
          exemption: 2000000,
          description: "R2m exclusion on primary residence",
          condition: "Must be primary residence throughout ownership"
        },
        
        small_business_assets: {
          age_55_plus_exclusion: 1800000,
          lifetime_limit: 1800000,
          conditions: [
            "Must be 55 or older",
            "Business owned for 5 years minimum",
            "Active business asset"
          ]
        }
      }
    },
    
    # Dividends Tax
    dividends_tax: {
      rate: config.dividend_tax_rate,  # 20% for 2024/25
      rate_display: "20%",
      description: "Withholding tax on dividends",
      
      exemptions: [
        "Dividends from retirement funds",
        "Dividends from foreign companies",
        "Dividends in specie (non-cash)",
        "Dividends from shares held in tax-free savings account",
        "Certain dividends between companies (inter-company)"
      ],
      
      treatment: {
        local: "Withheld at source by company paying dividend",
        foreign: "Included in taxable income, may qualify for foreign tax credit"
      }
    },
    
    # Tax-Free Savings Account
    tfsa: {
      annual_contribution_limit: 36000,
      lifetime_contribution_limit: 500000,
      
      rules: [
        "No age limit",
        "Contributions are not tax deductible",
        "Returns (interest, dividends, capital gains) are tax-free",
        "Withdrawals do not create additional contribution room",
        "Lifetime limit is cumulative (not per year)",
        "Penalties for excess contributions: 40% of excess amount"
      ],
      
      benefits: [
        "Interest tax-free",
        "Dividends tax-free (no dividends tax)",
        "Capital gains tax-free",
        "No tax on withdrawals",
        "Estate duty free"
      ]
    },
    
    # Retirement Fund Contributions
    retirement_contributions: {
      section_10c_deduction: {
        limit: "27.5% of remuneration or taxable income (whichever is higher)",
        annual_cap: 350000,
        description: "Tax deduction for retirement fund contributions",
        
        calculation: "MIN(contributions, 27.5% × MAX(remuneration, taxable income), R350,000)"
      },
      
      types_of_funds: [
        "Pension Fund",
        "Provident Fund",
        "Retirement Annuity Fund (RA)"
      ],
      
      lump_sum_tax_tables: {
        retirement: [
          {
            band: "R0 - R550,000",
            rate: 0.00,
            rate_display: "0%"
          },
          {
            band: "R550,001 - R770,000",
            rate: 0.18,
            rate_display: "18%",
            calculation: "18% of amount above R550,000"
          },
          {
            band: "R770,001 - R1,155,000",
            rate: 0.27,
            rate_display: "27%",
            calculation: "R39,600 + 27% of amount above R770,000"
          },
          {
            band: "Over R1,155,000",
            rate: 0.36,
            rate_display: "36%",
            calculation: "R143,550 + 36% of amount above R1,155,000"
          }
        ],
        
        withdrawal: [
          {
            band: "R0 - R27,500",
            rate: 0.00,
            rate_display: "0%"
          },
          {
            band: "R27,501 - R726,000",
            rate: 0.18,
            rate_display: "18%"
          },
          {
            band: "R726,001 - R1,089,000",
            rate: 0.27,
            rate_display: "27%"
          },
          {
            band: "Over R1,089,000",
            rate: 0.36,
            rate_display: "36%"
          }
        ],
        
        note: "Retirement lump sums and withdrawal lump sums taxed separately"
      }
    },
    
    # Estate Duty
    estate_duty: {
      rate: 0.20,
      rate_display: "20%",
      description: "Levied on dutiable amount of deceased estate",
      
      abatement: {
        amount: 3500000,
        description: "First R3.5 million of estate is exempt"
      },
      
      calculation: "20% of (Estate value - R3.5m)",
      
      deductions: {
        section_4q: [
          "Funeral expenses",
          "Costs of administration",
          "Debts owed by deceased",
          "Bequests to public benefit organizations",
          "Property accruing to surviving spouse"
        ],
        
        section_4a: {
          description: "Deduction for property deemed to be in deceased's estate but accruing to surviving spouse",
          effect: "Effective estate splitting with spouse"
        }
      },
      
      exemptions: [
        "Property accruing to surviving spouse (unlimited)",
        "Property left to public benefit organization (Section 18A approved)",
        "Abatement: R3.5 million"
      ],
      
      example: {
        gross_estate: 10000000,
        deductions: 1000000,
        net_estate: 9000000,
        abatement: 3500000,
        dutiable_amount: 5500000,
        estate_duty: 1100000,
        calculation_display: "20% of (R9m - R3.5m) = R1.1m"
      }
    },
    
    # Transfer Duty
    transfer_duty: {
      description: "Tax on transfer of property",
      
      rates: [
        {
          band: "R0 - R1,100,000",
          rate: 0.00,
          rate_display: "0%"
        },
        {
          band: "R1,100,001 - R1,512,500",
          rate: 0.03,
          rate_display: "3%",
          calculation: "3% of value above R1,100,000"
        },
        {
          band: "R1,512,501 - R2,117,500",
          rate: 0.06,
          rate_display: "6%",
          calculation: "R12,375 + 6% of value above R1,512,500"
        },
        {
          band: "R2,117,501 - R2,722,500",
          rate: 0.08,
          rate_display: "8%",
          calculation: "R48,675 + 8% of value above R2,117,500"
        },
        {
          band: "R2,722,501 - R12,100,000",
          rate: 0.11,
          rate_display: "11%",
          calculation: "R97,075 + 11% of value above R2,722,500"
        },
        {
          band: "Over R12,100,000",
          rate: 0.13,
          rate_display: "13%",
          calculation: "R1,128,625 + 13% of value above R12,100,000"
        }
      ],
      
      exemptions: [
        "Transfers to/from spouse",
        "Transfers to certain public benefit organizations",
        "Certain government-to-government transfers"
      ]
    },
    
    # Donations Tax
    donations_tax: {
      rate: 0.20,
      rate_display: "20%",
      description: "Tax on value of property donated",
      
      annual_exemption: {
        amount: 100000,
        description: "R100,000 per year tax-free donations"
      },
      
      exemptions: [
        "Donations to spouse",
        "Donations to public benefit organizations (Section 18A)",
        "Donations not exceeding R100,000 per annum",
        "Bona fide maintenance payments",
        "Donations to political parties"
      ],
      
      casual_gifts: {
        exemption: 5000,
        description: "Casual gifts under R5,000 exempt"
      }
    },
    
    # Other Taxes
    other_taxes: {
      securities_transfer_tax: {
        rate: 0.0025,
        rate_display: "0.25%",
        description: "On transfer of listed securities (shares)",
        maximum: "Uncapped"
      },
      
      vat: {
        standard_rate: 0.15,
        rate_display: "15%",
        description: "Value-Added Tax",
        registration_threshold: 1000000,
        note: "Compulsory registration if turnover exceeds R1 million in 12 months"
      }
    }
  }


# ===== PERSONALIZED VIEW =====
FUNCTION generate_personalized_view(
  user_context: UserContext,
  uk_data: UkTaxData,
  sa_data: SaTaxData
) -> PersonalizedTaxView:
  
  personalized = {
    your_tax_rates: {},
    applicable_allowances: {},
    tax_planning_tips: []
  }
  
  # UK personalization
  IF user_context.uk_tax_resident:
    # Determine user's tax band
    IF user_context.income.annual <= 12570:
      personalized.your_tax_rates.uk_income_tax = "0% (within personal allowance)"
    ELSE IF user_context.income.annual <= 50270:
      personalized.your_tax_rates.uk_income_tax = "20% (basic rate taxpayer)"
    ELSE IF user_context.income.annual <= 125140:
      personalized.your_tax_rates.uk_income_tax = "40% (higher rate taxpayer)"
    ELSE:
      personalized.your_tax_rates.uk_income_tax = "45% (additional rate taxpayer)"
    
    # Personal allowance status
    IF user_context.income.annual > 100000:
      allowance_lost = MIN((user_context.income.annual - 100000) / 2, 12570)
      remaining_allowance = 12570 - allowance_lost
      personalized.applicable_allowances.personal_allowance = {
        amount: remaining_allowance,
        note: "Reduced due to income over £100,000"
      }
    ELSE:
      personalized.applicable_allowances.personal_allowance = {
        amount: 12570,
        note: "Full personal allowance available"
      }
    
    # Savings allowance
    IF user_context.income.annual <= 50270:
      personalized.applicable_allowances.personal_savings_allowance = {
        amount: 1000,
        note: "Basic rate taxpayer"
      }
    ELSE IF user_context.income.annual <= 125140:
      personalized.applicable_allowances.personal_savings_allowance = {
        amount: 500,
        note: "Higher rate taxpayer"
      }
    ELSE:
      personalized.applicable_allowances.personal_savings_allowance = {
        amount: 0,
        note: "Not available for additional rate taxpayers"
      }
    
    # Dividend allowance
    personalized.applicable_allowances.dividend_allowance = {
      amount: 500,
      note: "Applies to all taxpayers"
    }
    
    # ISA allowance
    personalized.applicable_allowances.isa_allowance = {
      amount: 20000,
      used: user_context.isa_used,
      remaining: 20000 - user_context.isa_used
    }
    
    # Pension annual allowance
    IF user_context.income.adjusted > 260000:
      tapered_allowance = MAX(60000 - ((user_context.income.adjusted - 260000) / 2), 10000)
      personalized.applicable_allowances.pension_annual_allowance = {
        amount: tapered_allowance,
        note: "Tapered due to high income"
      }
    ELSE:
      personalized.applicable_allowances.pension_annual_allowance = {
        amount: 60000,
        note: "Full annual allowance available"
      }
  
  # SA personalization
  IF user_context.sa_tax_resident:
    # Determine user's marginal rate
    IF user_context.income.annual <= 237100:
      personalized.your_tax_rates.sa_income_tax = "18% (marginal rate)"
    ELSE IF user_context.income.annual <= 370500:
      personalized.your_tax_rates.sa_income_tax = "26% (marginal rate)"
    ELSE IF user_context.income.annual <= 512800:
      personalized.your_tax_rates.sa_income_tax = "31% (marginal rate)"
    ELSE IF user_context.income.annual <= 673000:
      personalized.your_tax_rates.sa_income_tax = "36% (marginal rate)"
    ELSE IF user_context.income.annual <= 857900:
      personalized.your_tax_rates.sa_income_tax = "39% (marginal rate)"
    ELSE:
      personalized.your_tax_rates.sa_income_tax = "45% (marginal rate)"
    
    # Tax rebate
    IF user_context.age < 65:
      personalized.applicable_allowances.sa_rebate = {
        amount: 17235,
        type: "Primary rebate"
      }
    ELSE IF user_context.age < 75:
      personalized.applicable_allowances.sa_rebate = {
        amount: 19500,
        type: "Secondary rebate (65-74)"
      }
    ELSE:
      personalized.applicable_allowances.sa_rebate = {
        amount: 21720,
        type: "Tertiary rebate (75+)"
      }
    
    # Interest exemption
    IF user_context.age < 65:
      personalized.applicable_allowances.interest_exemption = {
        amount: 23800,
        note: "First R23,800 of interest tax-free"
      }
    ELSE:
      personalized.applicable_allowances.interest_exemption = {
        amount: 34500,
        note: "First R34,500 of interest tax-free (65+)"
      }
    
    # TFSA
    personalized.applicable_allowances.tfsa = {
      annual_limit: 36000,
      lifetime_limit: 500000,
      annual_used: user_context.tfsa_used.annual,
      lifetime_used: user_context.tfsa_used.lifetime,
      annual_remaining: 36000 - user_context.tfsa_used.annual,
      lifetime_remaining: 500000 - user_context.tfsa_used.lifetime
    }
    
    # Retirement contribution deduction
    max_deduction = MIN(user_context.income.annual * 0.275, 350000)
    personalized.applicable_allowances.retirement_deduction = {
      max_deductible: max_deduction,
      used: user_context.retirement_contributions,
      remaining: max_deduction - user_context.retirement_contributions
    }
  
  # Generate personalized tips
  personalized.tax_planning_tips = generate_tax_tips(user_context, personalized)
  
  RETURN personalized


# ===== HISTORICAL COMPARISON =====
FUNCTION generate_historical_comparison(
  country: enum['UK', 'SA'],
  metric: string,
  years: integer
) -> HistoricalComparison:
  
  historical_data = []
  
  FOR year FROM (current_tax_year - years) TO current_tax_year:
    IF country = 'UK':
      config = get_uk_tax_config(format_tax_year(year))
      value = extract_metric_value(config, metric)
    ELSE:
      config = get_sa_tax_config(format_tax_year(year))
      value = extract_metric_value(config, metric)
    
    historical_data.append({
      tax_year: format_tax_year(year),
      value: value
    })
  
  # Calculate changes
  year_over_year_changes = []
  FOR i FROM 1 TO historical_data.length - 1:
    change = historical_data[i].value - historical_data[i-1].value
    percentage_change = (change / historical_data[i-1].value) * 100
    
    year_over_year_changes.append({
      from_year: historical_data[i-1].tax_year,
      to_year: historical_data[i].tax_year,
      absolute_change: change,
      percentage_change: percentage_change
    })
  
  RETURN {
    metric_name: metric,
    historical_values: historical_data,
    changes: year_over_year_changes,
    trend: determine_trend(historical_data)
  }
User Interface Structure:
TAX INFORMATION PAGE LAYOUT:

┌─────────────────────────────────────────────────────────┐
│ TAX INFORMATION CENTER                                   │
│                                                          │
│ [Country: UK ▼] [Tax Year: 2024/25 ▼] [👤 Personal View]│
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ QUICK NAVIGATION                                         │
│ • Income Tax  • National Insurance  • CGT  • Dividends   │
│ • ISAs  • Pensions  • Inheritance Tax  • Other          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ YOUR TAX STATUS (Personalized)                          │
│ ┌─────────────┬──────────────┬────────────────────────┐│
│ │Your Marginal│Personal      │ISA Allowance           ││
│ │Rate: 40%    │Allowance:£12,570│Used: £8,000/£20,000││
│ └─────────────┴──────────────┴────────────────────────┘│
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ INCOME TAX                                [Show Details ▼]│
│                                                          │
│ Personal Allowance: £12,570                             │
│ • Tax-free amount you can earn                          │
│ • Reduced if income over £100,000                       │
│                                                          │
│ TAX BANDS (2024/25)                                     │
│ ├─ Basic Rate:    £0-£37,700        @ 20%              │
│ ├─ Higher Rate:   £37,701-£125,140  @ 40% ◄ You are here│
│ └─ Additional:    Over £125,140     @ 45%              │
│                                                          │
│ [Try Calculator] [View Examples] [Historical Rates]     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ TAX CALCULATOR WIDGET                                    │
│ Enter your income: £ [______]                           │
│ ┌────────────────────────────────────────────┐         │
│ │ Gross Income:        £60,000                │         │
│ │ Personal Allowance: -£12,570                │         │
│ │ Taxable Income:      £47,430                │         │
│ │                                              │         │
│ │ Tax Due:                                     │         │
│ │  £37,700 @ 20% = £7,540                     │         │
│ │  £9,730 @ 40%  = £3,892                     │         │
│ │ Total Tax:          £11,432                 │         │
│ │ Effective Rate:     19.05%                  │         │
│ └────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────┘

[Similar sections for each tax type...]

┌─────────────────────────────────────────────────────────┐
│ COMPARISON TOOLS                                         │
│ • Year-over-Year Changes                                │
│ • UK vs SA Comparison                                   │
│ • Historical Trends (5 years)                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ EDUCATIONAL RESOURCES                                    │
│ • Tax Planning Guides                                   │
│ • Official Government Links (HMRC / SARS)               │
│ • Glossary of Terms                                     │
│ • Video Tutorials                                       │
└─────────────────────────────────────────────────────────┘
API Endpoints:
GET /api/v1/tax-information/uk/{taxYear}
GET /api/v1/tax-information/sa/{taxYear}
GET /api/v1/tax-information/comparison/{taxYear}
GET /api/v1/tax-information/personalized/{userId}/{taxYear}
GET /api/v1/tax-information/historical/{country}/{metric}
GET /api/v1/tax-information/search?q={query}
POST /api/v1/tax-information/calculate/{taxType}
GET /api/v1/tax-information/changes/{taxYear}  // What changed this year
GET /api/v1/tax-information/export/{format}
Data Models:
TABLE: tax_information_content
- id: UUID (PK)
- country: ENUM('UK', 'SA')
- tax_type: VARCHAR(100)
- section: VARCHAR(100)
- content: TEXT
- content_type: ENUM('DESCRIPTION', 'EXAMPLE', 'RULE', 'TIP')
- effective_tax_year: VARCHAR(10)
- last_updated: TIMESTAMP
- source_reference: TEXT (official source URL)

TABLE: tax_year_changes
- id: UUID (PK)
- tax_year: VARCHAR(10)
- country: ENUM('UK', 'SA')
- change_type: ENUM('RATE_CHANGE', 'ALLOWANCE_CHANGE', 'NEW_RULE', 'ABOLISHED')
- metric_affected: VARCHAR(100)
- old_value: DECIMAL(15,2)
- new_value: DECIMAL(15,2)
- description: TEXT
- impact_assessment: TEXT
- announced_date: DATE
- effective_date: DATE

TABLE: user_tax_page_preferences
- user_id: UUID (PK, FK to users)
- default_country: ENUM('UK', 'SA', 'BOTH')
- show_personalized_view: BOOLEAN DEFAULT TRUE
- favorite_sections: JSON (array)
- collapsed_sections: JSON (array)
- last_viewed_tax_year: VARCHAR(10)

INDEX on tax_information_content(country, tax_type, effective_tax_year)
INDEX on tax_year_changes(tax_year, country)
CONCLUSION
This Features Document provides comprehensive technical specifications for building a sophisticated dual-country financial planning platform. The modular architecture allows for phased development while the detailed specifications ensure consistency and completeness across all features.
Key Differentiators:
1.	True dual-country integration: Not just two separate systems, but genuine cross-border tax optimization
2.	Comprehensive coverage: All major financial areas in both jurisdictions
3.	Intelligent automation: AI-driven recommendations with personalization
4.	Goal-oriented approach: Users plan for life goals, not just track numbers
5.	Scenario modeling: Empowers users to make informed major decisions
6.	Tax optimization: Built-in DTA application and cross-border planning
Development Priorities:
•	Start with framework and one complete module
•	Build tax engine early (dependencies across modules)
•	Iterate based on user feedback
•	Maintain modularity for independent development
•	Focus on accuracy and regulatory compliance
•	Invest in automation and intelligence features
This specification provides all the detail needed for development teams to begin implementation while maintaining flexibility for refinement during the build process.
