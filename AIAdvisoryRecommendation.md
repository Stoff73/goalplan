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
