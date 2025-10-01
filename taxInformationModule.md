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
