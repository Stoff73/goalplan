Product Requirements Document: Dual-Country Financial Planning Platform
1. EXECUTIVE SUMMARY
Product Vision A comprehensive, modular financial planning web application that enables users with ties to both the United Kingdom and South Africa to manage their complete financial picture across both jurisdictions, with intelligent AI-driven advice that accounts for dual tax treaties, domicile rules, tax residency status, and country-specific regulatory frameworks.
Target Users
•	UK/SA dual nationals
•	Expats living in either country with assets in both
•	Individuals planning relocation between UK and SA
•	Financial advisors serving cross-border clients
•	High-net-worth individuals with international portfolios
Core Value Proposition Single platform that eliminates the complexity of managing finances across two tax jurisdictions, providing actionable, compliant recommendations based on individual circumstances.
 
2. PRODUCT ARCHITECTURE
Modular Design Philosophy
•	Each financial domain operates as an independent module with its own dashboard
•	Modules can function standalone or as part of the integrated platform
•	Central dashboard aggregates data from all active modules
•	Phased development approach: framework first, then module-by-module build-out
Module Structure
1.	Central Dashboard (Hub)
2.	User Information Module (Profile & Settings)
3.	Protection Module
4.	Savings Module
5.	Investment Module
6.	Retirement Module
7.	Inheritance Tax (IHT) Planning Module
8.	Tax Intelligence Engine (Cross-cutting service)
9.	AI Advisory Engine (Cross-cutting service)
 
3. CORE FUNCTIONAL REQUIREMENTS
3.1 User Information Module
User Profile Management
•	Personal information (name, DOB, nationality/nationalities)
•	Family structure (spouse, dependents, ages, relationships)
•	Contact details
Tax Status & Domicile
•	Current domicile (UK, SA, or deemed domicile)
•	Domicile of origin
•	Tax residency status (UK, SA, dual resident)
•	Years of residency in each country
•	Statutory residence test (SRT) calculator for UK
•	SA physical presence test calculator
•	Domicile status tracker and forecast
•	Non-dom status (if applicable)
•	Remittance basis vs arising basis election
Income Information
•	Employment income (by country)
•	Self-employment income (by country)
•	Rental income (by country and property)
•	Dividend income (by country of source)
•	Interest income (by country of source)
•	Pension income (by country and scheme)
•	Foreign income details
•	Income tax rates applicable in each country
Life Context
•	Hobbies and interests (for holistic planning)
•	Career information
•	Life goals and objectives
•	Planned relocations or migrations
•	Risk tolerance assessment
•	Financial literacy level
•	Preferred communication style for AI advice
Information Hub
•	Tax year calendars (UK: April-April, SA: March-February)
•	Income tax bands and rates for both countries
•	Allowances and reliefs available in each country
•	Educational content library
•	Dual Tax Agreement (DTA) summary
•	Document storage and organization
 
3.2 Protection Module
Life Assurance
•	Policy details (provider, country of domicile of insurer)
•	Cover amount and currency
•	Policy type (term, whole of life, etc.)
•	Beneficiaries and trust arrangements
•	Premium amount and frequency
•	Policy start date and term
•	Country where policy is held
•	Tax treatment in UK (e.g., written in trust)
•	Tax treatment in SA (e.g., estate duty implications)
Critical Illness Cover
•	Policy details
•	Conditions covered
•	Claim definitions (UK vs SA differences)
•	Premium and term information
•	Tax treatment in each jurisdiction
Income Protection / Disability Cover
•	Deferred period
•	Benefit amount and period
•	Definition of incapacity
•	Premium payment method
•	Tax treatment of premiums and benefits
•	Family Income Benefit arrangements
Protection Dashboard Features
•	Coverage gap analysis
•	Cross-border implications of claims
•	Recommendations for coverage levels based on goals
•	Premium comparison across jurisdictions
•	Beneficiary review and optimization
•	Trust structure recommendations
•	Estate planning integration
AI Advisory Features
•	Assess adequacy of cover based on family needs
•	Identify gaps in protection across life stages
•	Recommend optimal jurisdiction for new policies
•	Alert to changes in circumstances requiring review
•	Tax efficiency recommendations for premium structure
 
3.3 Savings Module
Cash Accounts
•	Bank accounts (UK and SA)
•	Account type (current, savings, fixed deposit)
•	Balance and currency
•	Interest rates
•	Access terms (instant, notice period)
•	Country where account is held
•	Tax treatment of interest (PSA in UK, interest exemption in SA)
UK-Specific Savings Products
•	Cash ISA (current year subscription, total value)
•	Lifetime ISA (LISA)
•	Help to Buy ISA (if still held)
•	Junior ISA (for children)
•	NS&I products (Premium Bonds, savings certificates)
•	ISA allowance tracking and optimization
SA-Specific Savings Products
•	Tax-Free Savings Accounts (TFSA)
•	Fixed deposits
•	Money market accounts
•	Unit trusts (money market funds)
Emergency Fund
•	Target amount calculation
•	Current emergency fund status
•	Recommended allocation across currencies
•	Currency risk management
Savings Dashboard Features
•	Total savings across all accounts and currencies
•	Savings by country and currency breakdown
•	Interest income tracking and tax reporting
•	Savings goals progress tracking
•	Emergency fund adequacy assessment
•	Currency exposure analysis
•	Optimal account placement recommendations
AI Advisory Features
•	Emergency fund calculation based on income and circumstances
•	Optimal currency allocation based on spending patterns
•	Tax-efficient savings structure recommendations
•	Interest rate optimization across jurisdictions
•	TFSA and ISA allowance maximization strategies
•	Alerts for better rates or products
•	Savings goal achievement pathways
 
3.4 Investment Module
UK Investment Products
•	Stocks & Shares ISA
o	Holdings detail (individual stocks, funds, ETFs)
o	Current value and contributions this year
o	ISA allowance utilization
o	Capital gains (sheltered within ISA)
•	General Investment Account (GIA)
o	Holdings detail
o	Acquisition costs and dates
o	Unrealized gains/losses
o	Dividend history
o	Capital Gains Tax (CGT) implications
•	Venture Capital Trusts (VCTs)
o	VCT name and holdings
o	Income tax relief claimed
o	Holding period requirements
o	Dividend income (tax-free status)
•	Enterprise Investment Schemes (EIS)
o	Company details
o	Amount invested and date
o	Income tax relief and CGT reliefs
o	Holding period requirements
o	Risk rating
•	Seed Enterprise Investment Schemes (SEIS)
o	Similar structure to EIS
o	CGT reinvestment relief tracking
•	Unit Trusts and OEICs
o	Fund details and holdings
o	Accumulation vs income
o	Tax treatment
SA Investment Products
•	Unit Trusts 
o	Fund details, holdings, values
o	Tax treatment (interest, dividends, capital gains)
•	Exchange Traded Funds (ETFs)
•	Collective Investment Schemes
•	Direct shareholdings (JSE listed)
•	Offshore investments held by SA residents
•	Tax-Free Savings Account (investment portion)
Offshore Investments
•	Offshore bonds (Isle of Man, etc.)
•	International fund platforms
•	Treatment under UK and SA tax rules
•	Reporting fund status (UK)
Investment Dashboard Features
•	Total portfolio value across all jurisdictions
•	Asset allocation (by asset class, geography, currency)
•	Performance tracking (absolute and relative)
•	Dividend and income tracking
•	Capital gains/losses realized and unrealized
•	Tax efficiency scoring
•	Portfolio rebalancing recommendations
•	Risk analysis and diversification metrics
•	Currency exposure and hedging
AI Advisory Features
•	Asset allocation optimization based on goals and risk tolerance
•	Tax-efficient investment structure recommendations
•	ISA vs TFSA prioritization based on circumstances
•	CGT harvesting opportunities (using UK annual exemption)
•	Dividend income optimization across jurisdictions
•	EIS/SEIS/VCT suitability assessment
•	Offshore structure recommendations
•	Rebalancing guidance accounting for tax implications
•	Currency risk management strategies
•	DTA relief optimization (avoiding double taxation on dividends)
•	Domicile-based investment strategy adjustments
 
3.5 Retirement Module
UK Retirement Products
•	Occupational Pension Schemes
o	Scheme name and type (DB/DC)
o	Employer and member contributions
o	Current value (for DC)
o	Expected benefits (for DB)
o	Normal retirement age
o	Death benefits and dependents' pensions
•	Personal Pensions
o	Provider and plan details
o	Fund value and contributions
o	Tax relief claimed
o	Investment choices
•	Self-Invested Personal Pensions (SIPP)
o	Provider
o	Current holdings and value
o	Contribution history
o	Tax relief tracking
o	Annual allowance usage
o	Lifetime allowance considerations (historical)
•	State Pension
o	National Insurance record
o	Qualifying years
o	Forecast state pension amount
o	Gaps and voluntary contributions options
UK Pension Transfers
•	Overseas Pension Schemes (OPS)
•	Qualifying Recognised Overseas Pension Schemes (QROPS)
•	Qualifying Non-UK Pension Schemes (QNUPS)
SA Retirement Products
•	Pension Funds
o	Fund details and current value
o	Contribution rates
o	Investment strategy
•	Provident Funds
o	Similar structure to pension funds
o	Access differences
•	Retirement Annuities (RA)
o	Provider and fund value
o	Contribution history
o	Tax deductions claimed
o	Regulation 28 compliance
•	Preservation Funds
o	Origin (pension or provident)
o	Current value
o	Withdrawal rules
Cross-Border Retirement Schemes
•	QROPS (Qualifying Recognised Overseas Pension Scheme) 
o	Transfer details and date
o	UK tax charges paid
o	Ongoing reporting requirements
•	Overseas Pension Schemes Recognised (ROPSA) - SA equivalent
Retirement Dashboard Features
•	Total retirement wealth across all jurisdictions
•	Contribution tracking by tax year (both countries)
•	Tax relief optimization tracker
•	Annual allowance monitoring (UK)
•	Section 10C deduction tracking (SA - 27.5% of income cap)
•	Pension commencement lump sum projection (UK)
•	Retirement income forecasting
•	Retirement age scenario modeling
•	Pension access timelines (UK vs SA rules)
•	Currency risk in retirement
•	Cross-border retirement planning
AI Advisory Features
•	Contribution optimization across UK and SA schemes
•	Tax relief maximization strategies
•	QROPS/ROPS transfer suitability analysis
•	Retirement income tax efficiency planning
•	Lump sum vs income trade-off analysis
•	State pension optimization (UK voluntary contributions)
•	Drawdown strategy recommendations
•	Currency diversification in retirement
•	Domicile-based pension strategy
•	Early retirement impact analysis
•	Longevity risk assessment
•	Annuity vs drawdown recommendations
•	International pension consolidation advice
•	Estate planning integration with pensions
 
3.6 Inheritance Tax Planning Module
Assets Register
•	UK-situated assets
o	UK property (value, ownership structure)
o	UK bank accounts
o	UK investments and pensions
o	UK business interests
o	Personal possessions in UK
•	SA-situated assets
o	SA property (value, ownership structure)
o	SA bank accounts
o	SA investments and retirement funds
o	SA business interests
o	Personal possessions in SA
•	Worldwide assets (for domicile/deemed domicile)
•	Excluded property status tracking
Liabilities
•	Mortgages (by property and jurisdiction)
•	Loans and credit facilities
•	Other debts
•	Deductibility for IHT/Estate Duty purposes
UK IHT Planning
•	Nil Rate Band (NRB) utilization
•	Residence Nil Rate Band (RNRB) availability
•	Transferable NRB from deceased spouse
•	Potentially Exempt Transfers (PETs) register
•	Chargeable Lifetime Transfers (CLTs)
•	7-year tracking for gifts
•	Business Property Relief (BPR) assets
•	Agricultural Property Relief (APR) assets
•	Annual exemption usage (£3,000)
•	Small gifts exemption tracking
SA Estate Duty Planning
•	Estate duty calculation (20% on dutiable amount over R30m)
•	Abatement (R3.5m as of last knowledge)
•	Section 4(q) deductions
•	Property in spouse's estate
•	Deemed property provisions
Lifetime Gifting Strategy
•	Gift register (dates, amounts, recipients)
•	CLTs and PETs tracking
•	SA donations tax considerations (20% on amounts over R100k per year)
•	Gift planning optimization
Will & Estate Planning
•	Will existence and date (UK and/or SA)
•	Executors named
•	Guardians for minor children
•	Trust arrangements
•	Letter of wishes
•	Lasting Power of Attorney (UK)
•	Living will preferences
IHT Dashboard Features
•	Current IHT/Estate Duty liability projection
•	UK IHT calculation (40% over threshold)
•	SA Estate Duty calculation
•	Total cross-border estate duty exposure
•	NRB and RNRB tracking
•	PETs timeline visualization
•	Gift planning effectiveness
•	Asset ownership structure analysis
•	Will review reminders
•	Beneficiary tracking
AI Advisory Features
•	IHT liability forecasting under different scenarios
•	Gift planning strategies (UK 7-year rule, SA donations tax)
•	Domicile planning for IHT purposes
•	Non-dom estate planning strategies
•	Excluded property optimization
•	Trust structure recommendations
•	Life assurance policy optimization for IHT
•	Business relief planning
•	Residence nil rate band maximization
•	Spousal exemption optimization
•	Asset location recommendations (UK vs SA vs offshore)
•	Will structure recommendations
•	Equalisation of estates between spouses
•	Charitable giving strategies
•	Estate liquidity planning
 
3.7 Central Dashboard (Hub)
Overview Features
•	Net worth summary (across all modules and currencies)
•	Net worth by country and currency
•	Financial health score
•	Goal progress tracking
•	Key recommendations summary from AI
•	Upcoming actions and deadlines
•	Tax year-end reminders (both countries)
•	Module quick access
Data Visualization
•	Net worth trend over time
•	Asset allocation across all holdings
•	Geographic allocation
•	Currency exposure
•	Income vs expenditure
•	Tax efficiency metrics
Goal Tracking
•	User-defined financial goals
•	Progress indicators
•	Timeline projections
•	Recommended actions for each goal
Alerts & Notifications
•	Tax year-end deadlines
•	Contribution limit warnings
•	Review reminders (annual policy reviews, etc.)
•	Regulatory changes affecting user
•	Opportunities for action (tax relief, allowance usage)
 
4. TAX INTELLIGENCE ENGINE
Core Functions This is a cross-cutting service that powers tax calculations and recommendations across all modules.
UK Tax Calculations
•	Income tax (including Scottish rates if applicable)
•	National Insurance contributions
•	Capital Gains Tax
•	Dividend tax
•	Inheritance Tax
•	Stamp Duty Land Tax / Land Transaction Tax
•	Annual allowances: Personal Allowance, PSA, Dividend Allowance, CGT Annual Exempt Amount, ISA allowance, Pension Annual Allowance
SA Tax Calculations
•	Income tax (PAYE and provisional tax)
•	Capital Gains Tax (inclusion rate method)
•	Estate Duty
•	Donations Tax
•	Transfer Duty
•	Securities Transfer Tax
Dual Tax Agreement (DTA) Engine
•	Treaty article application
•	Double taxation relief methods: 
o	Credit method
o	Exemption method
•	Source vs residence taxation rules
•	Specific income type treatment: 
o	Employment income
o	Business profits
o	Dividends
o	Interest
o	Royalties
o	Capital gains
o	Pensions
o	Government service
•	Tie-breaker rules for dual residents
•	Foreign tax credit calculations
Domicile & Residence Rules Engine
•	UK Statutory Residence Test automation
•	SA physical presence test
•	Domicile determination and tracking
•	Deemed domicile rules (UK)
•	Remittance basis calculations
•	Split year treatment (UK)
Regulatory Compliance
•	UK FCA regulations awareness
•	SA FSCA regulations
•	HMRC reporting requirements
•	SARS reporting requirements
•	FATCA implications
•	Common Reporting Standard (CRS) considerations
 
5. AI ADVISORY ENGINE
Core Capabilities This is the intelligent layer that provides personalized, context-aware recommendations.
Analysis Functions
•	Multi-dimensional data analysis across all modules
•	Goal-based planning algorithms
•	Scenario modeling and projection
•	Risk assessment
•	Tax optimization identification
•	Opportunity recognition
Recommendation Types
•	Immediate actions ("You have £5,000 unused ISA allowance this tax year")
•	Strategic planning ("Consider a QROPS transfer if you plan to remain in SA")
•	Risk warnings ("Your protection cover is inadequate for your family needs")
•	Optimization opportunities ("You could save £X in tax by restructuring investments")
•	Regulatory alerts ("Changes to pension rules may affect your plans")
Contextual Intelligence The AI must consider:
•	Current domicile and tax residence
•	Future migration intentions
•	Family circumstances
•	Risk tolerance
•	Investment knowledge level
•	Time horizon for goals
•	Income level and stability
•	Age and life stage
•	Both countries' legal and tax frameworks
•	Cross-border implications of every decision
Advisory Approach
•	Natural language explanations
•	Justification for each recommendation
•	Citations to relevant tax law or regulation
•	Consideration of DTA provisions
•	Multiple scenario comparisons
•	Action prioritization
•	Step-by-step implementation guidance
Learning & Adaptation
•	User feedback on recommendations
•	Outcomes tracking (what advice was followed)
•	Continuous improvement of advice quality
•	Personalization based on user behavior
•	Market data integration for timely advice
 
6. KEY FEATURES SUMMARY
6.1 Cross-Cutting Features
Multi-Currency Management
•	Support for GBP, ZAR, and major currencies
•	Real-time exchange rates
•	Currency risk analysis
•	Historical currency performance
Document Management
•	Secure document upload and storage
•	Document categorization by module
•	OCR for data extraction from statements
•	Version control
•	Sharing capabilities (with advisors)
Collaboration Features
•	Share access with financial advisors
•	Multi-user households (joint accounts)
•	Advisor comments and recommendations
•	Permission levels
Data Security
•	Bank-level encryption
•	Two-factor authentication
•	Biometric login options
•	Regular security audits
•	GDPR and POPIA compliance
•	Data sovereignty considerations
Integration Capabilities
•	Bank account aggregation (Open Banking UK, similar in SA)
•	Investment platform APIs
•	Pension scheme data imports
•	HMRC integration (potential future)
•	SARS eFiling integration (potential future)
 
6.2 User Experience Features
Onboarding
•	Guided setup wizard
•	Progressive disclosure (start simple, add complexity)
•	Educational tooltips and guidance
•	Sample data for exploration
•	Risk profiling questionnaire
•	Goal-setting workshop
Customization
•	Module activation/deactivation
•	Dashboard widget customization
•	Report preferences
•	Alert preferences
•	AI advice frequency and detail settings
Reporting
•	Net worth statements
•	Tax reports (preparation for self-assessment/provisional tax)
•	Portfolio performance reports
•	Goal progress reports
•	Custom date range reports
•	Export to PDF, Excel, CSV
Mobile Experience
•	Responsive design for all modules
•	Quick actions (add transaction, check balance)
•	Notification management
•	Biometric authentication
 
7. DATA MODEL CONSIDERATIONS
Entity Relationships
•	User → Multiple Modules
•	User → Tax Status (temporal - changes over time)
•	User → Goals
•	Each Module → Assets/Products
•	Assets → Tax Treatment (varies by jurisdiction and user status)
•	Goals → Multiple Modules (e.g., retirement goal links to retirement, investment, and savings modules)
Temporal Data
•	Historical tracking of all changes
•	Point-in-time views (e.g., "what was my position at end of last tax year?")
•	Future projections
•	Audit trail for compliance
Reference Data
•	Tax rates and bands (versioned by tax year)
•	Allowances and limits (versioned)
•	DTA provisions
•	Product types and definitions
•	Currency exchange rates (historical)
 

8. TECHNICAL CONSIDERATIONS
Architecture Principles
•	Modular microservices architecture
•	API-first design
•	Scalability for user growth
•	Performance optimization (complex calculations)
•	Offline capability considerations
Technology Stack Considerations (You mentioned no code, but high-level considerations for PRD)
•	Modern web framework (React, Vue, Angular)
•	Robust backend (Python, Java, .NET, Go, or Ruby)
•	Database: relational for structured data, consider document DB for flexibility
•	Cloud hosting (AWS, Azure, GCP) with data residency compliance
•	AI/ML framework for advisory engine
Third-Party Services
•	Currency exchange rate providers
•	Market data feeds
•	Bank aggregation services (Plaid, TrueLayer, etc.)
•	Identity verification
•	Document OCR services
•	Calculation engines (tax, investment projections)
 
9. COMPLIANCE & REGULATORY
UK Regulatory Considerations
•	FCA regulations (if providing advice vs information)
•	Data Protection Act 2018 / UK GDPR
•	Financial advice vs information distinction
•	Consumer Duty obligations
•	Appropriate labeling of AI-generated content
SA Regulatory Considerations
•	Financial Sector Conduct Authority (FSCA) regulations
•	Protection of Personal Information Act (POPIA)
•	Financial advice licensing requirements
•	FAIS (Financial Advisory and Intermediary Services Act)
Disclaimers Required
•	Not a substitute for professional advice
•	Information vs advice distinction
•	AI limitations and need for human review
•	Tax law complexity and change
•	User responsibility for accuracy of data entered
Professional Standards
•	Integration with human advisors
•	Clear escalation path to professionals
•	Limitations of automated advice
•	When to seek specialist advice
 
10. PHASED DEVELOPMENT APPROACH
Phase 1: Foundation
•	Framework and architecture
•	User authentication and profiles
•	Central dashboard (basic version)
•	User Information Module
•	Basic data entry for one module (suggest starting with Savings as simplest)
Phase 2: Core Modules
•	Protection Module build-out
•	Investment Module build-out
•	Tax Intelligence Engine (basic version)
•	Basic AI recommendations
Phase 3: Retirement & Planning
•	Retirement Module build-out
•	IHT Planning Module build-out
•	Enhanced Tax Intelligence Engine
•	DTA integration
Phase 4: Intelligence & Integration
•	Advanced AI Advisory Engine
•	Cross-module insights
•	Goal-based planning
•	Scenario modeling
•	Third-party integrations
Phase 5: Enhancement & Scale
•	Mobile app development
•	Advanced reporting
•	Collaboration features
•	Additional jurisdictions (future expansion)
•	Marketplace integrations
 
11. SUCCESS METRICS
User Engagement
•	Daily/monthly active users
•	Module adoption rates
•	Feature usage frequency
•	Time spent in platform
•	Data completeness rates
Value Delivery
•	Tax savings identified
•	Goals achieved on time
•	Investment performance vs benchmarks
•	User-reported confidence levels
•	NPS (Net Promoter Score)
Business Metrics
•	User acquisition rate
•	User retention rate
•	Revenue (if subscription model)
•	Cost per user
•	Support ticket volume
Quality Metrics
•	Accuracy of calculations
•	AI recommendation acceptance rate
•	Recommendation outcome tracking
•	User satisfaction with advice
 
12. RISKS & MITIGATION
Technical Risks
•	Complex calculations with edge cases → Extensive testing, professional review
•	Data security breaches → Best practice security, insurance, audits
•	Integration failures → Robust error handling, fallback mechanisms
•	Performance issues → Scalable architecture, optimization
Regulatory Risks
•	Crossing into regulated advice → Clear T&Cs, legal review, disclaimers
•	Data protection violations → GDPR/POPIA compliance by design
•	Tax calculation errors → Professional review, disclaimers, user verification
Market Risks
•	Limited target market size → Market research, phased expansion
•	Competition from established players → Unique cross-border value proposition
•	User adoption challenges → Excellent UX, education, onboarding
Operational Risks
•	Maintaining tax law updates → Partnerships with tax professionals, regular updates
•	AI advice quality → Human oversight, feedback loops, continuous improvement
•	Customer support complexity → Comprehensive knowledge base, tiered support
 
