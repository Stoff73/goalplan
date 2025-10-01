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
 
