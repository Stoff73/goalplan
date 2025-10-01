6. INVESTMENT MODULE
Feature 6.1: Portfolio Management
Feature Name: Comprehensive Investment Portfolio Tracking
User Story: As an investor with holdings across UK and SA markets, I want to track all my investments including stocks, funds, ISAs, and tax-advantaged schemes so that I can monitor performance and manage tax efficiently.
Acceptance Criteria:
•	Track holdings in Stocks & Shares ISA, General Investment Account (GIA), Unit Trusts, ETFs
•	Support for VCTs, EIS, SEIS investments with tax relief tracking
•	SA investments: Unit Trusts, ETFs, JSE-listed stocks
•	Record purchase price, current value, unrealized gains/losses
•	Track dividend income by source country
•	Capital gains tracking (realized and unrealized)
•	Asset allocation analysis
•	Performance metrics vs benchmarks
•	Currency exposure reporting
•	Tax lot tracking (FIFO, average cost methods)
Technical Requirements:
•	Market data integration for pricing (manual or API)
•	Capital gains calculation engine (UK and SA rules)
•	Dividend tax treatment calculation
•	Asset allocation algorithms
•	Performance calculation (time-weighted returns)
•	Corporate action tracking (splits, mergers, dividends)
•	EIS/SEIS/VCT holding period tracking (for tax relief retention)
Constraints:
•	Market data refresh: Real-time for premium, daily for standard
•	Historical price data: 10 years minimum
•	Tax lot tracking: Required for accurate CGT calculation
•	EIS/SEIS minimum holding: 3 years for tax relief retention
•	VCT minimum holding: 5 years for tax relief retention
Implementation Approach:
ENDPOINT: POST /api/v1/investments/holdings
REQUEST BODY:
{
  accountType: enum['STOCKS_ISA', 'GIA', 'UNIT_TRUST', 'VCT', 'EIS', 'SEIS', 
                    'SA_UNIT_TRUST', 'SA_ETF', 'SA_DIRECT_SHARES', 'OFFSHORE_BOND'],
  accountProvider: string,
  accountNumber: string (last 4 digits),
  country: enum['UK', 'SA', 'OFFSHORE'],
  holdings: [
    {
      securityType: enum['STOCK', 'FUND', 'ETF', 'BOND', 'VCT', 'EIS_SHARE', 'SEIS_SHARE'],
      ticker: string,
      name: string,
      quantity: decimal,
      purchaseDate: date,
      purchasePrice: decimal,
      purchaseCurrency: string,
      currentPrice: decimal,
      currentValue: decimal,
      unrealizedGain: decimal,
      assetClass: enum['EQUITY', 'FIXED_INCOME', 'PROPERTY', 'COMMODITY', 'CASH', 'ALTERNATIVE'],
      region: enum['UK', 'US', 'EUROPE', 'ASIA', 'EMERGING', 'GLOBAL'],
      sector: string
    }
  ],
  taxReliefClaimed: {  // For EIS/SEIS/VCT
    reliefType: enum['INCOME_TAX_RELIEF', 'CGT_EXEMPTION', 'CGT_DEFERRAL'],
    reliefAmount: decimal,
    taxYear: string,
    holdingPeriodRequired: integer (years),
    holdingPeriodEndDate: date
  }
}

BUSINESS LOGIC:
1. Validate holding data:
   - Quantity > 0
   - Purchase price >= 0
   - Purchase date <= today
   
2. Calculate metrics:
   unrealized_gain = (current_price - purchase_price) * quantity
   unrealized_gain_percentage = (unrealized_gain / (purchase_price * quantity)) * 100
   
   IF accountType = 'STOCKS_ISA':
     gains_tax_free = TRUE
     dividends_tax_free = TRUE
   ELSE IF accountType = 'GIA':
     apply_uk_cgt_rules()
     apply_uk_dividend_tax_rules()
   
   IF country = 'SA':
     apply_sa_cgt_rules()  // Inclusion rate method
     apply_sa_dividend_tax_rules()  // Dividend withholding tax

3. Track tax lots for CGT:
   // FIFO method for UK
   // Average cost method allowed for SA
   tax_lot = {
     purchase_date: date,
     quantity: decimal,
     cost_basis: decimal,
     disposal_method: 'FIFO' or 'AVERAGE_COST'
   }

4. VCT/EIS/SEIS tracking:
   IF accountType IN ['VCT', 'EIS', 'SEIS']:
     holding_period_remaining = required_period - years_held
     at_risk_of_losing_relief = (holding_period_remaining > 0)
     
     IF at_risk_of_losing_relief:
       CREATE alert("Hold for {remaining} more years to retain tax relief")

5. Asset allocation calculation:
   total_portfolio_value = SUM(all_holdings.current_value)
   
   FOR EACH holding:
     allocation_percentage = (holding.current_value / total_portfolio_value) * 100
   
   GROUP BY asset_class, region, sector

6. Performance calculation:
   time_weighted_return = calculate_twr(cash_flows, valuations)
   vs_benchmark = portfolio_return - benchmark_return

RESPONSE:
{
  id: uuid,
  accountDetails: {...},
  holdings: [...],
  portfolioMetrics: {
    totalValue: {gbp: decimal, zar: decimal},
    totalCost: {gbp: decimal, zar: decimal},
    totalUnrealizedGain: {amount: decimal, percentage: decimal},
    totalRealizedGain: decimal (from previous disposals),
    assetAllocation: [
      {assetClass: string, value: decimal, percentage: decimal},
      ...
    ],
    regionAllocation: [...],
    sectorAllocation: [...],
    currencyExposure: [...]
  },
  taxImplications: {
    isaHoldings: {value: decimal, gains: decimal, taxFree: true},
    giaHoldings: {
      value: decimal,
      unrealizedGains: decimal,
      estimatedCgtLiability: decimal,
      cgtAllowanceUsed: decimal,
      cgtAllowanceRemaining: decimal
    },
    taxReliefAtRisk: [
      {type: string, amount: decimal, holdUntil: date}
    ]
  },
  performance: {
    timeWeightedReturn: decimal,
    moneyWeightedReturn: decimal,
    benchmarkComparison: {
      portfolioReturn: decimal,
      benchmarkReturn: decimal,
      outperformance: decimal
    }
  }
}
User Flow:
[Investment Dashboard] → [Portfolio Overview]
     ↓
[Portfolio Summary Cards]
  - Total Portfolio Value (prominent)
  - Unrealized Gain/Loss (color-coded)
  - Asset Allocation Pie Chart
  - Performance vs Benchmark
     ↓
[Add Investment Account Button]
     ↓
[Account Entry - Step 1: Account Type]
  - Select account type (visual cards):
    - Stocks & Shares ISA
    - General Investment Account
    - VCT/EIS/SEIS
    - SA Unit Trust / ETF
    - Offshore Bond
     ↓
[Account Entry - Step 2: Provider Details]
  - Provider name (autocomplete)
  - Account number (last 4 digits)
  - Country
     ↓
[Account Entry - Step 3: Add Holdings]
  - Manual entry:
    - Search security by ticker/name
    - Enter quantity, purchase price, date
  - Bulk import:
    - Upload CSV file
    - Map columns to fields
    - Validate and import
  - For VCT/EIS/SEIS:
    - Tax relief details
    - Holding period tracker
     ↓
[Holdings List View]
  - Table with sortable columns:
    - Security, Quantity, Cost, Value, Gain/Loss, %
  - Filter: By account, asset class, region
  - Color coding: Gains (green), Losses (red)
     ↓
[Detailed Holding View] (click on any holding)
  - Purchase history (tax lots)
  - Dividend history
  - Corporate actions
  - Performance chart
  - Tax lot tracking
  - CGT calculator (if GIA)
     ↓
[Portfolio Analysis Tab]
  - Asset allocation (multiple views):
    - By asset class
    - By region
    - By sector
    - By currency
  - Diversification score
  - Risk metrics
  - Rebalancing recommendations
API Endpoints:
•	POST /api/v1/investments/accounts - Add investment account
•	PUT /api/v1/investments/accounts/{id} - Update account
•	DELETE /api/v1/investments/accounts/{id} - Delete account (soft delete)
•	POST /api/v1/investments/accounts/{accountId}/holdings - Add holding
•	PUT /api/v1/investments/holdings/{id} - Update holding
•	DELETE /api/v1/investments/holdings/{id} - Delete holding (soft delete)
•	POST /api/v1/investments/holdings/{id}/update-price - Update current price
•	GET /api/v1/investments/portfolio - Get complete portfolio summary
•	GET /api/v1/investments/portfolio/performance - Performance metrics
•	GET /api/v1/investments/portfolio/asset-allocation - Asset allocation breakdown
•	GET /api/v1/investments/cgt-calculator - CGT liability calculator
•	POST /api/v1/investments/holdings/bulk-import - Bulk import holdings
•	GET /api/v1/investments/dividends - Dividend income report
•	GET /api/v1/investments/tax-relief-tracker - VCT/EIS/SEIS tracker
Data Models:
TABLE: investment_accounts
- id: UUID (PK)
- user_id: UUID (FK to users)
- account_type: ENUM('STOCKS_ISA', 'GIA', 'UNIT_TRUST', 'VCT', 'EIS', 'SEIS', 
                     'SA_UNIT_TRUST', 'SA_ETF', 'SA_DIRECT_SHARES', 'OFFSHORE_BOND')
- provider: VARCHAR(255)
- account_number_encrypted: VARCHAR(255)
- country: ENUM('UK', 'SA', 'OFFSHORE')
- base_currency: CHAR(3)
- account_open_date: DATE
- status: ENUM('ACTIVE', 'CLOSED')
- deleted: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: investment_holdings
- id: UUID (PK)
- account_id: UUID (FK to investment_accounts)
- security_type: ENUM('STOCK', 'FUND', 'ETF', 'BOND', 'VCT', 'EIS_SHARE', 'SEIS_SHARE')
- ticker: VARCHAR(20)
- isin: VARCHAR(12)
- security_name: VARCHAR(255)
- quantity: DECIMAL(15,4)
- average_cost_basis: DECIMAL(15,4) (calculated)
- current_price: DECIMAL(15,4)
- price_currency: CHAR(3)
- current_value: DECIMAL(15,2) (calculated)
- unrealized_gain: DECIMAL(15,2) (calculated)
- unrealized_gain_percentage: DECIMAL(10,2) (calculated)
- asset_class: ENUM('EQUITY', 'FIXED_INCOME', 'PROPERTY', 'COMMODITY', 'CASH', 'ALTERNATIVE')
- region: ENUM('UK', 'US', 'EUROPE', 'ASIA', 'EMERGING', 'GLOBAL')
- sector: VARCHAR(100)
- last_price_update: TIMESTAMP
- deleted: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

TABLE: tax_lots
- id: UUID (PK)
- holding_id: UUID (FK to investment_holdings)
- purchase_date: DATE
- quantity: DECIMAL(15,4)
- purchase_price: DECIMAL(15,4)
- purchase_currency: CHAR(3)
- cost_basis_gbp: DECIMAL(15,2)
- cost_basis_zar: DECIMAL(15,2)
- exchange_rate: DECIMAL(10,6)
- disposal_date: DATE (NULL if not disposed)
- disposal_quantity: DECIMAL(15,4)
- disposal_proceeds: DECIMAL(15,2)
- realized_gain: DECIMAL(15,2) (calculated on disposal)
- cgt_tax_year: VARCHAR(7) (UK) or VARCHAR(9) (SA)
- disposal_method: ENUM('FIFO', 'AVERAGE_COST', 'SPECIFIC_IDENTIFICATION')
- created_at: TIMESTAMP

TABLE: dividends
- id: UUID (PK)
- holding_id: UUID (FK to investment_holdings)
- payment_date: DATE
- ex_dividend_date: DATE
- dividend_per_share: DECIMAL(10,4)
- total_dividend_gross: DECIMAL(10,2)
- withholding_tax: DECIMAL(10,2)
- total_dividend_net: DECIMAL(10,2)
- currency: CHAR(3)
- source_country: ENUM('UK', 'SA', 'US', 'OTHER')
- uk_tax_year: VARCHAR(7)
- sa_tax_year: VARCHAR(9)
- qualified_dividend: BOOLEAN (for US stocks)
- created_at: TIMESTAMP

TABLE: corporate_actions
- id: UUID (PK)
- holding_id: UUID (FK to investment_holdings)
- action_type: ENUM('SPLIT', 'REVERSE_SPLIT', 'MERGER', 'SPINOFF', 'RIGHTS_ISSUE', 
                    'BONUS_ISSUE', 'DELISTING')
- action_date: DATE
- ratio: VARCHAR(20) (e.g., '2:1' for split)
- description: TEXT
- quantity_before: DECIMAL(15,4)
- quantity_after: DECIMAL(15,4)
- cost_basis_adjustment: DECIMAL(15,2)
- created_at: TIMESTAMP

TABLE: tax_relief_schemes
- id: UUID (PK)
- holding_id: UUID (FK to investment_holdings)
- scheme_type: ENUM('VCT', 'EIS', 'SEIS')
- investment_date: DATE
- investment_amount: DECIMAL(15,2)
- income_tax_relief_claimed: DECIMAL(10,2)
- income_tax_relief_percentage: DECIMAL(5,2) (30% EIS, 50% SEIS, 30% VCT)
- tax_year_claimed: VARCHAR(7)
- minimum_holding_period_years: INTEGER (5 for VCT, 3 for EIS/SEIS)
- holding_period_end_date: DATE (calculated)
- cgt_deferral_claimed: DECIMAL(10,2) (EIS only)
- cgt_exemption_eligible: BOOLEAN (EIS/SEIS after holding period)
- relief_withdrawn: BOOLEAN DEFAULT FALSE
- relief_withdrawal_reason: TEXT
- created_at: TIMESTAMP

TABLE: portfolio_snapshots
- id: UUID (PK)
- user_id: UUID (FK to users)
- snapshot_date: DATE
- total_value_gbp: DECIMAL(15,2)
- total_value_zar: DECIMAL(15,2)
- total_cost_basis_gbp: DECIMAL(15,2)
- unrealized_gain_gbp: DECIMAL(15,2)
- realized_gain_ytd_gbp: DECIMAL(15,2)
- asset_allocation_json: JSON
- performance_metrics_json: JSON
- created_at: TIMESTAMP

VIEW: v_portfolio_summary (materialized view, refreshed on demand)
- user_id
- total_portfolio_value_gbp
- total_portfolio_value_zar
- total_unrealized_gain
- total_realized_gain_ytd
- isa_holdings_value
- gia_holdings_value
- vct_eis_seis_value
- estimated_cgt_liability
- last_updated: TIMESTAMP

INDEX on investment_holdings(account_id, deleted)
INDEX on tax_lots(holding_id, disposal_date)
INDEX on dividends(holding_id, payment_date)
INDEX on tax_relief_schemes(holding_id, holding_period_end_date)
INDEX on portfolio_snapshots(user_id, snapshot_date DESC)
Error Handling:
ERROR CASES:
1. Negative quantity or price
   - Response: 400 Bad Request
   - Message: "Quantity and price must be positive values"
   
2. Purchase date in future
   - Response: 400 Bad Request
   - Message: "Purchase date cannot be in the future"
   
3. ISA holding exceeds subscription limits
   - Response: 400 Bad Request
   - Message: "This holding would exceed your ISA subscription limit for {tax_year}"
   
4. VCT/EIS/SEIS disposal before holding period
   - Response: 400 Bad Request (validation warning)
   - Message: "Disposing before {date} will result in loss of £{amount} tax relief"
   - Allow user to confirm and proceed
   
5. Tax lot disposal quantity exceeds available
   - Response: 400 Bad Request
   - Message: "Cannot dispose {quantity} shares. Only {available} shares available from this tax lot"
   
6. Invalid ticker symbol
   - Response: 404 Not Found
   - Message: "Unable to find security with ticker {ticker}. Please verify or enter manually"
   
7. Currency mismatch
   - Response: 400 Bad Request
   - Message: "Security {name} trades in {currency}, but you entered {entered_currency}"
   
8. Duplicate holding in same account
   - Response: 409 Conflict (warning)
   - Message: "You already have a holding of {security} in this account. Merge or add as separate lot?"

EDGE CASES:
- Stock split: Adjust all tax lots proportionally, maintain cost basis
- Reverse split: Consolidate shares, maintain cost basis
- Merger/acquisition: Create new holdings for acquirer, close acquired
- Spinoff: Allocate cost basis between parent and spun-off entity
- Rights issue: New tax lot at subscription price
- Bonus issue: Additional shares, zero cost basis, adjust average cost
- Bed and ISA: Dispose from GIA (CGT event), purchase in ISA (new tax lot)
- Same-day rule (UK CGT): Disposals matched with acquisitions on same day first
- 30-day rule (UK CGT): Disposals matched with acquisitions within 30 days (prevent bed and breakfasting)
- Section 104 holding (UK): Pooled holding with average cost
- Dividend reinvestment: New tax lot at reinvestment price
- Foreign dividends with withholding tax: Claim DTA relief
- Accumulation funds: No dividend distribution, increases share price
- Offshore bonds: Complex tax treatment (top-slicing relief)
- EIS loss relief: Can claim against income tax if EIS shares sold at loss
- VCT dividend: Tax-free regardless of investor's tax band
- Fractional shares: Support decimal quantities for ETFs/funds
- Currency hedged funds: Track hedge separately from underlying
Performance Considerations:
•	Price updates: Batch process, cache for 15 minutes (real-time)
•	Portfolio calculation: Materialized view, refresh on material changes
•	CGT calculation: Complex, cache per holding, recalculate on disposal
•	Asset allocation: Pre-calculate, store in snapshot
•	Performance metrics: Time-intensive, calculate daily (background job)
•	Expected holdings per user: 10-100
•	Portfolio summary: Target <1 second response
•	Historical performance: Pre-aggregate monthly/quarterly
•	Dividend income report: Index on payment_date
•	Tax lot queries: Optimize FIFO lookups with proper indexing
•	Bulk import: Process asynchronously, max 1000 holdings per import
•	Market data API: Rate limiting, caching, fallback to manual updates
 

