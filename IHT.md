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
 

