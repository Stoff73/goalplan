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
 

