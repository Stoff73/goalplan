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
 
