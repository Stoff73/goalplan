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
 

