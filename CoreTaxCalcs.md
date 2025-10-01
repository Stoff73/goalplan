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
 
