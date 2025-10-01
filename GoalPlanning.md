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
