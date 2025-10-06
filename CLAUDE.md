# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**GoalPlan** is a dual-country financial planning platform for users with ties to both the United Kingdom and South Africa. It provides comprehensive financial management across both jurisdictions with AI-driven advice that accounts for dual tax treaties, domicile rules, and country-specific regulations.

**Key Value Proposition:** Single platform eliminating the complexity of managing finances across two tax jurisdictions.

---

## ⚠️ CRITICAL: Mandatory Testing Protocol

**RULE: NO CODE CHANGE IS COMPLETE WITHOUT BROWSER TESTING**

After making ANY code change affecting the application:

1. **Restart services** (if backend changes):
   ```bash
   ./stop.sh && ./start.sh
   ```

2. **Wait for startup** (5-10 seconds)

3. **Open browser** to http://localhost:5173

4. **Test affected pages** manually

5. **Check browser console** (F12) for JavaScript errors

6. **Check Network tab** for failed API requests (404, 500, etc.)

7. **Verify functionality** actually works as expected

8. **ONLY THEN** mark task complete

**Why This Is Mandatory:**
- Code can compile successfully but still break the application
- Type annotations can be wrong even if syntax is correct
- Backend logs show requests but NOT whether the app actually works
- **Real Example:** Bug #18 was discovered by user after API fixes because browser testing was skipped
  - Code compiled ✓
  - Backend logs clean ✓
  - Did NOT test browser ✗
  - Result: Tax Status and Income pages completely broken (500 errors) ✗
  - User unable to use core functionality ✗

**This testing protocol applies to:**
- All code changes (backend and frontend)
- All agent-delegated work (verify their work in browser)
- All bug fixes (verify the fix works in browser)
- All new features (verify they work in browser)

See `.claude/instructions.md` and `BUG_FIX_SUMMARY.md` for detailed lessons learned.

---

## Architecture

### Modular Design Philosophy
- Each financial domain operates as an independent module with its own dashboard
- Modules can function standalone or as part of the integrated platform
- Central dashboard aggregates data from all active modules
- API-first approach with well-defined interfaces between modules

### Core Modules
1. **User Information Module** - Tax status, domicile tracking, income management
2. **Central Dashboard** - Net worth aggregation and financial overview
3. **Savings Module** - Cash accounts, ISA/TFSA tracking
4. **Protection Module** - Life assurance and critical illness cover
5. **Investment Module** - Portfolio management across jurisdictions
6. **Retirement Module** - UK pensions, SA retirement funds, QROPS
7. **IHT Planning Module** - Inheritance tax and estate duty planning
8. **Tax Intelligence Engine** - Cross-cutting tax calculation service
9. **AI Advisory Engine** - Cross-cutting recommendation service

### Tech Stack
- **Backend:** Python with FastAPI
- **Frontend:** React 19
- **Database:** PostgreSQL (relational data)
- **Caching/Sessions:** Redis
- **Testing:** pytest (backend), Jest (frontend components), Playwright (E2E flows)
- **Package Management:** pip (backend)
- **UI Components:** Import from 'internal-packages/ui' (NOT '@/components/ui')
- **Design System:** Follow `STYLEGUIDE.md` for all UI/UX implementation

## Development Workflow

### Phase-Based Development
Development is organized into 5 phases, each building on the previous:
- **Phase 0:** Project setup and foundation (2-3 weeks)
- **Phase 1:** Authentication and user management (3-4 months)
- **Phase 2:** Core modules (4-5 months)
- **Phase 3:** Advanced features (5-6 months)
- **Phase 4:** Intelligence and AI (4-5 months)
- **Phase 5:** Enhancement and scale (6-8 months)

**Task Files:**
- `phase0_tasks.md` - Environment setup
- `phase1_tasks.md` - Auth, user info, savings, dashboard
- Additional phases in development

### Critical Rules
⛔ **DO NOT PROCEED TO NEXT PHASE UNTIL ALL TESTS PASS**
- App functionality must be maintained at all times
- All tests must pass before moving to the next task
- Testing gates are mandatory between phases

### Agent Delegation
Tasks are delegated to specialized agents:

**⚠️ CRITICAL QUALITY CONTROL PROCESS:**

All agent work MUST be verified before acceptance:
1. **Run actual tests** - Do NOT trust agent reports of passing tests
2. **Verify code quality** - Read implementation to ensure spec compliance
3. **Re-delegate if needed** - Send work back with specific fix instructions if:
   - Tests fail
   - Code quality is poor
   - Specifications not followed
4. **Repeat until perfect** - Continue verification cycle until 100% pass rate
5. **Never mark complete** without personal verification

This is MANDATORY for all delegated work. See `.claude/instructions.md` for detailed workflow.

**🐍 Python Backend Tasks → `python-backend-engineer` agent**
- API endpoints (FastAPI)
- Database models (SQLAlchemy) and migrations (Alembic)
- Business logic services
- Authentication and security
- Background jobs
- Testing with pytest

**⚛️ React Frontend Tasks → `react-coder` agent**
- React 19 components (no forwardRef)
- UI/UX implementation following `STYLEGUIDE.md`
- Forms and validation
- State management (Context API)
- Component testing with Jest
- **ALWAYS import from 'internal-packages/ui'**
- **MANDATORY: Follow narrative storytelling approach from STYLEGUIDE.md**

## UI/UX Design System (MANDATORY)

### Style Guide Compliance
**⚠️ CRITICAL: All frontend work MUST follow `/Users/CSJ/Desktop/goalplan/STYLEGUIDE.md`**

**Key Requirements:**
1. **Narrative Storytelling Approach**
   - Use conversational language: "You're worth £325,000" NOT "Net Worth: £325,000"
   - Explain the "why" behind every number
   - Embed metrics in sentences, not standalone displays
   - 2-3 sentence paragraphs maximum
   - Line height 1.7 for narrative text

2. **Visual Design**
   - Narrative section cards with 32px padding
   - 48-64px spacing between major sections
   - Border radius: 12px for cards
   - Shadow: subtle (shadow-sm)
   - Generous white space for readability

3. **Typography**
   - Page headlines: Bold, conversational status (e.g., "Your Financial Health: Strong")
   - Body text: 16px, line-height 1.7, text-secondary color
   - Metrics: Monospace font, embedded in sentences with <strong> tags
   - No uppercase labels, use normal case

4. **Progressive Disclosure**
   - "Tell me more" expandable sections for details
   - Callout boxes for tips/warnings with colored backgrounds
   - Clear "What to do next" action sections
   - Complexity is optional, not default

5. **Color Usage**
   - Primary: #2563EB (blue for actions/links)
   - Success: #10B981 (green for positive metrics)
   - Warning: #F59E0B (amber for attention)
   - Error: #EF4444 (red for negative/alerts)
   - Text: #0F172A (primary), #475569 (secondary), #94A3B8 (tertiary)

**Before Implementing ANY Frontend Feature:**
- [ ] Read STYLEGUIDE.md section relevant to component type
- [ ] Use narrative storytelling, not data display
- [ ] Implement responsive design (mobile-first)
- [ ] Add dark mode support
- [ ] Include progressive disclosure patterns
- [ ] Test with keyboard navigation
- [ ] Ensure WCAG AA accessibility

## Documentation Structure

### Feature Specifications (Shards)
Detailed feature specs are in sharded markdown files in project root:

**Core Modules:**
- `userAuth.md` - Authentication and profile management
- `UserInfo.md` - Tax status, domicile, income tracking
- `CentralDashboard.md` - Dashboard and aggregation
- `Savings.md` - Cash accounts, ISA/TFSA
- `Investment.md` - Portfolio tracking
- `Retirement.md` - Pensions and retirement funds
- `Protection.md` - Life assurance
- `IHT.md` - Inheritance tax planning

**Tax & Compliance:**
- `CoreTaxCalcs.md` - UK and SA tax calculations
- `DTA.md` - Double Tax Agreement relief
- `TaxResidency.md` - SRT and SA presence test
- `taxInformationModule.md` - Tax reference library

**Cross-Cutting:**
- `Architecture.md` - Design principles
- `DataManagement.md` - Data handling, audit trails
- `securityCompliance.md` - Security and compliance
- `performance.md` - Performance targets
- `UserFlows.md` - UX principles
- `integration.md` - External integrations
- `riskMitigation.md` - Risk management

**See `SHARDS_README.md` for complete documentation index**

### Task Management
- `TASKS_README.md` - Overview of phase-based task structure
- `.claude/instructions.md` - **START HERE** - Complete development rules and workflows
- `.claude/agents/` - Agent configurations for delegation

## Testing Strategy

### Backend Testing (pytest)
- **Unit tests:** Individual functions and methods
- **Integration tests:** API endpoints and database interactions
- **Load tests:** Performance under load
- **Coverage target:** >80%
- **Location:** `tests/**/*_test.py`

### Frontend Testing
- **Component tests (Jest):** Unit, integration, snapshot tests for all components
  - Location: `tests/components/*.test.jsx`
  - Mock all API calls
  - Test loading/error/success states
- **E2E tests (Playwright):** User flows only (NOT component testing)
  - Location: `e2e/*.spec.js`
  - Complete user journeys

## Key Technical Requirements

### Multi-Currency Support
- GBP, ZAR, USD, EUR minimum
- Real-time exchange rates
- Historical rate tracking
- Currency risk analysis

### Tax Year Handling
- UK tax year: April 6 - April 5
- SA tax year: March 1 - February 28/29
- Temporal data with effective_from/effective_to
- Point-in-time queries supported

### Dual Tax System
- UK tax calculations (Income Tax, NI, CGT, IHT)
- SA tax calculations (Income Tax, CGT, Estate Duty)
- Double Tax Agreement (DTA) relief calculator
- UK Statutory Residence Test (SRT)
- SA physical presence test
- Deemed domicile tracking

### Security Requirements
- **Password hashing:** Argon2 (NOT bcrypt)
- **JWT tokens:** RS256 (asymmetric signing)
- **Session management:** Redis-backed with 15min access, 7-day refresh
- **Rate limiting:** On all mutation endpoints
- **Encryption:** PII fields (account numbers, sensitive data)
- **Account lockout:** 5 failed attempts = 30min lockout
- **2FA:** TOTP with backup codes

### Performance Targets
- API responses: <500ms (95th percentile)
- Authentication: <200ms
- Dashboard load: <2 seconds
- Database queries: Optimized (no N+1 queries)
- Frontend bundle: <500KB gzipped
- Mobile responsive

### ISA/TFSA Allowances
- **UK ISA:** £20,000 annual allowance (2024/25)
- **SA TFSA:** R36,000 annual + R500,000 lifetime limit
- Track contributions per tax year
- Alert when nearing limits

## Demo User & Mock Data

A comprehensive demo user with realistic mock data is available for testing and development.

**Demo Credentials:**
- **Email:** `demo@goalplan.com`
- **Password:** `Demo123!`

**To populate demo data:**
```bash
cd backend
source .venv/bin/activate  # Activate virtual environment
python populate_demo_data.py
```

**Demo user includes:**
- User profile (John Smith, dual UK/SA citizenship, born in SA, lives in UK)
- Tax status (UK resident, SA-born, non-UK domicile)
- Income (£140k UK employment + R15k/month SA rental)
- Savings (3 accounts: UK current, Cash ISA, SA savings)
- Investments (Stocks & Shares ISA + Offshore bond)
- Retirement (UK occupational pension, SIPP, SA retirement annuity)
- Life insurance (£500k cover, NOT in trust, wife as beneficiary)
- Assets (UK house £650k joint, SA rental R2.4m)
- Liabilities (UK mortgage £320k, credit card £2.5k)

**Mock data specification:** See `mockData.md` for profile details.

---

## Common Commands

### Backend
```bash
# ⚠️ CRITICAL: Always use .venv Python (3.12.11), NOT system python3 (3.9.6)
# Virtual environment is at PROJECT ROOT: .venv/
#
# Two ways to run Python commands:
# 1. Activate venv (from project root):
source .venv/bin/activate
python --version  # Should show 3.12.11

# 2. Use full path (RECOMMENDED for scripts/tests):
/Users/CSJ/Desktop/goalplan/.venv/bin/python --version

# Install dependencies (from project root)
pip install -r backend/requirements.txt

# Navigate to backend directory
cd backend

# Run database migrations
alembic upgrade head

# Populate demo data (after migrations)
python populate_demo_data.py

# Run tests - ALWAYS use .venv Python:
/Users/CSJ/Desktop/goalplan/.venv/bin/python -m pytest tests/ -v
/Users/CSJ/Desktop/goalplan/.venv/bin/python -m pytest tests/api/auth/test_registration.py -v

# Or after activating venv:
python -m pytest tests/ -v
python -m pytest tests/api/auth/test_registration.py -v

# Run linting
black .
isort .
mypy .

# Start backend server
python -m uvicorn main:app --reload

# Verify Python version (should show 3.12.x, NOT 3.9.6)
python --version
```

### Frontend
```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Run component tests (Jest)
npm test
npm test tests/components/LoginForm.test.jsx

# Run E2E tests (Playwright)
npx playwright test
npx playwright test e2e/login.spec.js

# Run linting
npm run lint

# Build for production
npm run build
```

## Important Patterns

### React 19 Patterns
- **NO forwardRef** - React 19 doesn't need it
- **Avoid useEffect** - Use React 19's built-in solutions where possible
- **Import UI components:** ALWAYS from 'internal-packages/ui'
- Keep components simple, functional, and obvious
- **CRITICAL:** Follow `STYLEGUIDE.md` for all design patterns, components, and UX
  - Narrative storytelling approach (conversational, educational tone)
  - Generous white space and readability
  - Progressive disclosure patterns
  - Accessibility standards (WCAG 2.1 Level AA)

### API Endpoints
- RESTful design
- Version prefix: `/api/v1/`
- Authentication required for all user-specific endpoints
- Pydantic models for request/response validation
- Consistent error responses

### Database Migrations
- Use Alembic for all schema changes
- Never edit past migrations
- Test migrations up and down
- Include both upgrade and downgrade functions

### Temporal Data
- Use effective_from/effective_to for historical tracking
- No overlapping validity periods
- Support point-in-time queries
- Auto-adjust previous record on new insert

## Domain-Specific Knowledge

### UK Statutory Residence Test (SRT)
Three-part test determines UK tax residency:
1. **Automatic overseas test:** <16 days in UK = non-resident
2. **Automatic UK test:** ≥183 days in UK = resident
3. **Sufficient ties test:** 5 ties considered based on days in UK

### SA Physical Presence Test
Two criteria for SA tax residency:
1. **91 days in current year:** Present in SA for at least 91 days
2. **5-year average:** 91 days average over current + prior 4 years

### Deemed Domicile (UK)
Individual becomes deemed domiciled if:
- UK resident for 15 of last 20 tax years, OR
- Born in UK with domicile of origin in UK and returned as resident

### Double Tax Agreement Relief
- Treaty between UK and SA prevents double taxation
- Different treatment for different income types
- Tie-breaker rules for dual residents
- Credit method vs exemption method

## Code Quality Standards

- **Test coverage:** >80% for all modules
- **Linting:** Must pass with 0 errors
- **Type hints:** Comprehensive (Python), TypeScript preferred (frontend)
- **Documentation:** Self-documenting code, docstrings for public APIs
- **SOLID principles:** Clean architecture, separation of concerns
- **Security:** Always validate input, sanitize output, use parameterized queries

## Design System & UI/UX

**CRITICAL:** All UI/UX work MUST follow `STYLEGUIDE.md`

### Narrative Storytelling Approach
- Use conversational, second-person language ("you", "your")
- Explain the "why" behind every number
- Lead with plain-language narratives, not raw data
- Example: "You're worth **£325,000** after debts" NOT "Net Worth: £325,000"

### Key Design Principles
1. **Storytelling Over Data Display** - Numbers support the story, don't replace it
2. **Educational by Default** - Teach users through use, explain technical terms
3. **Empowerment Through Understanding** - Help users understand recommendations
4. **Conversational & Human Tone** - Write like a trusted advisor
5. **Generous White Space** - Text-focused design requires excellent readability
6. **Progressive Disclosure** - Start simple, complexity is optional

### Component Guidelines
- Import UI components from 'internal-packages/ui'
- Use NarrativeSection cards for story sections
- Embed metrics in sentences, not standalone
- Use Callout boxes for tips/warnings
- Implement "Tell me more" expandable sections
- Line height 1.7 for narrative text
- 32px padding for narrative cards
- 48-64px spacing between sections

### Color & Typography
- Primary: #2563EB (professional blue)
- Success: #10B981 (green for positive metrics)
- Warning: #F59E0B (amber for attention)
- Error: #EF4444 (red for negative values)
- Font: System fonts (-apple-system, BlinkMacSystemFont, "Segoe UI", "Inter")
- Monospace for currency values

### Accessibility Requirements
- WCAG 2.1 Level AA compliance
- Keyboard navigation for all interactive elements
- Screen reader support (semantic HTML, ARIA labels)
- 4.5:1 color contrast minimum
- Focus indicators required

**See `STYLEGUIDE.md` for complete specifications**

## Before Starting Work

1. **Read `.claude/instructions.md`** - Complete development workflow and rules
2. **Read `STYLEGUIDE.md`** - Design system and UI/UX patterns (for frontend work)
3. **Check current phase** - Look at `TASKS_README.md` for current status
4. **Review feature specs** - Read relevant shard files for task context
5. **Verify tests pass** - Run existing test suite before making changes
6. **Populate demo data** - Run `python populate_demo_data.py` for testing (demo@goalplan.com / Demo123!)
7. **Plan delegation** - Identify which agent should handle the work

## Resources

- **Main README:** `TASKS_README.md` - Phase structure and progress
- **Instructions:** `.claude/instructions.md` - Development workflow
- **Shards Index:** `SHARDS_README.md` - Feature specifications
- **PRD:** `prd.md` - Product requirements document
- **Architecture:** `Architecture.md` - System design principles
