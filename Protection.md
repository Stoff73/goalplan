4. PROTECTION MODULE
Feature 4.1: Life Assurance Policy Management
Feature Name: Comprehensive Life Assurance Policy Tracking
User Story: As a user, I want to track all my life assurance policies across UK and SA, including coverage amounts, beneficiaries, and tax implications, so I can ensure my family is adequately protected.
Acceptance Criteria:
•	User can add multiple life assurance policies
•	Each policy includes: provider, policy type, cover amount, premium, term, beneficiaries
•	Support for UK and SA policies with different tax treatments
•	Track if policy written in trust (UK)
•	Track estate duty implications (SA)
•	Coverage gap analysis based on family needs
•	Premium comparison across providers
•	Beneficiary management with percentages
•	Policy renewal reminders
•	Claims process guidance
Technical Requirements:
•	File upload for policy documents (PDF)
•	OCR for policy data extraction (optional enhancement)
•	Beneficiary relationship tracking
•	Premium payment reminder system
•	Integration with IHT module for estate planning
•	Currency support (GBP, ZAR, USD, EUR)
Constraints:
•	Policy documents: Max 10MB per file
•	Beneficiaries: Max 10 per policy
•	Historical policy records retained indefinitely (audit trail)
•	Premium reminders: Email and in-app notification
Implementation Approach:
ENDPOINT: POST /api/v1/protection/life-assurance
REQUEST BODY:
{
  policyNumber: string,
  provider: string,
  providerCountry: enum['UK', 'SA', 'OTHER'],
  policyType: enum['TERM', 'WHOLE_OF_LIFE', 'DECREASING_TERM', 'LEVEL_TERM', 
                   'INCREASING_TERM', 'FAMILY_INCOME_BENEFIT', 'OTHER'],
  coverAmount: decimal,
  currency: string,
  premiumAmount: decimal,
  premiumFrequency: enum['MONTHLY', 'ANNUALLY', 'SINGLE'],
  startDate: date,
  endDate: date (NULL for whole of life),
  writtenInTrust: boolean (UK only),
  trustDetails: {
    trustType: enum['BARE', 'DISCRETIONARY', 'INTEREST_IN_POSSESSION'],
    trustees: array[string],
    beneficiaries: array[{name: string, relationship: string, percentage: decimal}]
  },
  beneficiariesDirectPolicy: array[{
    name: string,
    dateOfBirth: date,
    relationship: enum['SPOUSE', 'CHILD', 'PARENT', 'SIBLING', 'OTHER'],
    percentage: decimal,
    address: string
  }],
  indexationRate: decimal (optional, for increasing policies),
  criticalIllnessRider: boolean,
  waiverOfPremium: boolean,
  notes: text
}

BUSINESS LOGIC:
1. Validate policy data:
   - Sum of beneficiary percentages = 100%
   - Cover amount > 0
   - End date > start date (if applicable)
   - Premium amount reasonable for cover amount

2. Determine tax treatment:
   IF providerCountry = 'UK' AND writtenInTrust = TRUE:
     outside_uk_estate_for_iht = TRUE
   ELSE IF providerCountry = 'UK':
     in_uk_estate_for_iht = TRUE
   
   IF providerCountry = 'SA':
     apply_sa_estate_duty_rules()
     // SA policies generally part of estate

3. Calculate recommended cover (family needs analysis):
   recommended_cover = (annual_income * income_multiplier) +
                      outstanding_debts +
                      (children_count * education_cost_per_child) +
                      funeral_costs -
                      existing_assets
   
   coverage_gap = recommended_cover - total_current_cover

4. Store policy with encrypted document reference

5. Set up premium payment reminders

6. Link to IHT module if not in trust

RESPONSE:
{
  id: uuid,
  policyDetails: {...},
  taxTreatment: {
    ukIhtImpact: boolean,
    saEstateDutyImpact: boolean,
    writtenInTrust: boolean
  },
  coverageAnalysis: {
    currentTotalCover: decimal,
    recommendedCover: decimal,
    coverageGap: decimal,
    gapPercentage: decimal
  },
  annualPremiumCost: decimal
}
User Flow:
[Protection Dashboard] → [Life Assurance Tab]
     ↓
[Add Policy Button]
     ↓
[Policy Entry Form - Step 1: Provider Details]
  - Policy number
  - Provider name (autocomplete with popular providers)
  - Provider country
  - Policy type (visual cards with descriptions)
     ↓
[Policy Entry Form - Step 2: Cover Details]
  - Cover amount and currency
  - Premium amount and frequency
  - Start date and end date (if applicable)
  - Optional riders (CI, waiver)
     ↓
[Policy Entry Form - Step 3: Beneficiaries]
  - Written in trust? (UK policies) → If YES: Trust details
  - Beneficiary list (add multiple)
    - Name, relationship, percentage
    - Validation: percentages total 100%
     ↓
[Policy Entry Form - Step 4: Upload Document]
  - Upload policy document (optional)
  - OCR extraction attempt (if available)
  - Review and confirm extracted data
     ↓
[Coverage Analysis Display]
  - Current total cover
  - Recommended cover (calculated)
  - Gap visualization
  - Recommendation: "Consider increasing cover by £X"
     ↓
[Save Policy]
     ↓
[Policy List View]
  - Card view: Each policy with key details
  - Total cover amount (header)
  - Coverage gap indicator
  - Filter: By provider, type, country
  - Sort: By cover amount, premium, end date
API Endpoints:
•	POST /api/v1/protection/life-assurance - Add policy
•	PUT /api/v1/protection/life-assurance/{id} - Update policy
•	DELETE /api/v1/protection/life-assurance/{id} - Delete policy (soft delete)
•	GET /api/v1/protection/life-assurance - List all policies
•	GET /api/v1/protection/life-assurance/{id} - Get specific policy
•	POST /api/v1/protection/life-assurance/coverage-analysis - Run coverage needs analysis
•	POST /api/v1/protection/life-assurance/{id}/upload-document - Upload policy document
•	GET /api/v1/protection/life-assurance/{id}/document - Download policy document
Data Models:
TABLE: life_assurance_policies
- id: UUID (PK)
- user_id: UUID (FK to users)
- policy_number: VARCHAR(100)
- provider: VARCHAR(255)
- provider_country: ENUM('UK', 'SA', 'OTHER')
- policy_type: ENUM('TERM', 'WHOLE_OF_LIFE', 'DECREASING_TERM', 'LEVEL_TERM', 
                    'INCREASING_TERM', 'FAMILY_INCOME_BENEFIT', 'OTHER')
- cover_amount: DECIMAL(15,2)
- currency: CHAR(3)
- cover_amount_gbp: DECIMAL(15,2) (calculated)
- cover_amount_zar: DECIMAL(15,2) (calculated)
- premium_amount: DECIMAL(10,2)
- premium_frequency: ENUM('MONTHLY', 'ANNUALLY', 'SINGLE')
- annual_premium: DECIMAL(10,2) (calculated)
- start_date: DATE
- end_date: DATE (NULL for whole of life)
- written_in_trust: BOOLEAN DEFAULT FALSE
- trust_type: ENUM('BARE', 'DISCRETIONARY', 'INTEREST_IN_POSSESSION')
- critical_illness_rider: BOOLEAN DEFAULT FALSE
- waiver_of_premium: BOOLEAN DEFAULT FALSE
- indexation_rate: DECIMAL(5,2)
- uk_iht_impact: BOOLEAN (calculated)
- sa_estate_duty_impact: BOOLEAN (calculated)
- document_reference: UUID (FK to documents table)
- status: ENUM('ACTIVE', 'LAPSED', 'CLAIMED', 'MATURED')
- notes: TEXT
- deleted: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: policy_beneficiaries
- id: UUID (PK)
- policy_id: UUID (FK to life_assurance_policies)
- name: VARCHAR(255)
- date_of_birth: DATE
- relationship: ENUM('SPOUSE', 'CHILD', 'PARENT', 'SIBLING', 'OTHER')
- percentage: DECIMAL(5,2)
- address: TEXT
- created_at: TIMESTAMP

TABLE: policy_trustees (for trust policies)
- id: UUID (PK)
- policy_id: UUID (FK to life_assurance_policies)
- name: VARCHAR(255)
- relationship_to_policyholder: VARCHAR(100)
- created_at: TIMESTAMP

TABLE: coverage_needs_analysis
- id: UUID (PK)
- user_id: UUID (FK to users)
- analysis_date: DATE
- annual_income: DECIMAL(15,2)
- income_multiplier: DECIMAL(3,1) (typically 10)
- outstanding_debts: DECIMAL(15,2)
- number_of_children: INTEGER
- education_cost_per_child: DECIMAL(15,2)
- funeral_costs: DECIMAL(10,2)
- existing_liquid_assets: DECIMAL(15,2)
- recommended_cover: DECIMAL(15,2)
- current_total_cover: DECIMAL(15,2)
- coverage_gap: DECIMAL(15,2)
- notes: TEXT
- created_at: TIMESTAMP

TABLE: premium_reminders
- id: UUID (PK)
- policy_id: UUID (FK to life_assurance_policies)
- reminder_date: DATE
- reminder_sent: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP

INDEX on life_assurance_policies(user_id, status)
INDEX on policy_beneficiaries(policy_id)
INDEX on premium_reminders(reminder_date, reminder_sent)
CONSTRAINT: SUM(policy_beneficiaries.percentage WHERE policy_id = X) = 100
Error Handling:
ERROR CASES:
1. Beneficiary percentages don't total 100%
   - Response: 400 Bad Request
   - Message: "Beneficiary percentages must total 100%. Current total: {calculated_total}%"
   
2. Invalid trust setup (trust selected but no trustees)
   - Response: 400 Bad Request
   - Message: "Trust policies must have at least one trustee"
   
3. End date before start date
   - Response: 400 Bad Request
   - Message: "Policy end date must be after start date"
   
4. Duplicate policy number for same provider
   - Response: 409 Conflict
   - Message: "A policy with this number already exists for {provider}"
   - Option to update existing or confirm as separate policy
   
5. Document upload too large
   - Response: 413 Payload Too Large
   - Message: "Document size exceeds 10MB limit. Please compress or split the file"
   
6. Invalid currency code
   - Response: 400 Bad Request
   - Message: "Invalid currency code. Supported: GBP, ZAR, USD, EUR"

EDGE CASES:
- Whole of life policies: No end date (NULL), validation skip
- Single premium policies: Annual premium = premium_amount, frequency = 'SINGLE'
- Multiple beneficiaries with same name: Allow, distinguish by relationship and DOB
- Policy in trust but user not UK resident: Warning (unusual but valid)
- Child beneficiary: Flag for review (may need trust structure)
- Policy matured: Status = 'MATURED', show in separate view
- Policy lapsed: Status = 'LAPSED', keep for reference but exclude from coverage total
- Indexation rate: Apply annually to cover amount (background job)
- Critical illness claim: Reduce life cover by CI payout amount
- Currency fluctuation: Recalculate GBP/ZAR values daily
Performance Considerations:
•	Document storage: Use cloud storage (S3, Azure Blob)
•	OCR processing: Async job (if implemented), may take 30-60 seconds
•	Coverage analysis: Cache results for 30 days (recalculate if significant data change)
•	Currency conversion: Daily batch job for all policies
•	Premium reminders: Daily cron job, send 7 days before due date
•	Expected policies per user: 1-5
•	Policy list query: <500ms
•	Document upload: Progress indicator for files >2MB
•	Beneficiary validation: Client-side + server-side
 
