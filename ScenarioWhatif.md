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
 
