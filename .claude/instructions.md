# GoalPlan Development Instructions

**Last Updated:** October 1, 2025

---

## Critical Rules

### ⛔ DO NOT PROCEED TO NEXT PHASE UNTIL ALL TESTS PASS ⛔

- **App functionality must be maintained at all times**
- **All tests must pass before moving to the next task**
- **Testing gates are mandatory between phases**

---

## Agent Delegation Rules

### When to Delegate

**MANDATORY delegation for:**
- 🐍 **All Python backend code** → `python-backend-engineer` agent
- ⚛️ **All React frontend code** → `react-coder` agent

**Look for task markers:**
```markdown
**🐍 DELEGATE TO: `python-backend-engineer`**
**⚛️ DELEGATE TO: `react-coder`**
```

### How to Delegate

#### 🐍 Python Backend Tasks

**Agent:** `python-backend-engineer`

**Process:**
1. Agent MUST read all listed "Context Files" before starting
2. Implement code following specifications exactly as written in context files
3. Write comprehensive tests (pytest)
4. Ensure all tests pass before marking complete
5. Follow SOLID principles and clean architecture

**Responsibilities:**
- API endpoint implementation (FastAPI)
- Database models and migrations (SQLAlchemy, Alembic)
- Business logic services
- Authentication and security
- Background jobs and async tasks
- Testing (pytest: unit, integration, load tests)

**Requirements:**
- Use `pip` for dependency management
- Comprehensive type hints throughout
- Test coverage >80%
- Follow PEP standards
- Document all public APIs

#### ⚛️ React Frontend Tasks

**Agent:** `react-coder`

**Process:**
1. Agent MUST read all listed "Context Files" before starting
2. Import UI components from 'internal-packages/ui' (NOT '@/components/ui')
3. Follow React 19 patterns (no forwardRef)
4. Keep components simple and obvious
5. Write comprehensive tests using Jest

**Responsibilities:**
- React components
- UI/UX implementation
- Forms and validation
- State management (Context API)
- Routing
- Component testing (Jest only)

**Requirements:**
- **ALWAYS** import from 'internal-packages/ui'
- **NEVER** use forwardRef (React 19 doesn't need it)
- **AVOID** useEffect unless absolutely necessary
- Keep components simple, functional, and obvious
- Write comprehensive Jest tests for all logic

---

## Testing Strategy

### Backend Testing

**Framework:** `pytest`

**Types:**
- **Unit tests** - Test individual functions and methods
- **Integration tests** - Test API endpoints and database interactions
- **Load tests** - Test performance under load

**Requirements:**
- All test files: `tests/**/*_test.py`
- Test coverage >80%
- All tests must pass before proceeding
- Mock external dependencies

**Example:**
```bash
pytest tests/models/test_user_model.py -v
pytest tests/api/auth/test_registration.py -v
```

### Frontend Testing

**Component Testing:** `Jest` (EXCLUSIVELY)

**E2E Testing:** `Playwright` (ONLY for user flows)

**Types:**
- **Jest** - Component unit tests, integration tests, snapshot tests
- **Playwright** - End-to-end user flow testing only (NOT component testing)

**Requirements:**
- Component tests: `tests/components/*.test.jsx` (Jest)
- E2E tests: `e2e/*.spec.js` (Playwright)
- Test all user interactions
- Mock all API calls in component tests
- Test loading states, error states, success states

**Example:**
```bash
# Component testing with Jest
npm test tests/components/LoginForm.test.jsx

# E2E testing with Playwright
npx playwright test e2e/login.spec.js
```

---

## Context Files

Every task lists required "Context Files" - these are shard documents containing detailed specifications.

**Agent MUST:**
1. Read ALL listed context files before starting
2. Follow specifications exactly as written
3. Reference specific sections mentioned in task instructions

**Available Context Files:**

### Core Modules
- `userAuth.md` - User authentication and profile management
- `UserInfo.md` - Tax status, domicile, income tracking
- `CentralDashboard.md` - Dashboard and net worth aggregation
- `Protection.md` - Life assurance policy management
- `Savings.md` - Cash accounts, ISA/TFSA tracking
- `Investment.md` - Portfolio and investment tracking
- `Retirement.md` - Pensions and retirement funds
- `IHT.md` - Inheritance tax planning

### Tax & Compliance
- `CoreTaxCalcs.md` - UK and SA tax calculations
- `DTA.md` - Double Tax Agreement relief
- `TaxResidency.md` - Tax residency determination (SRT, SA presence test)
- `taxInformationModule.md` - Tax reference library

### AI & Intelligence
- `AIAdvisoryRecommendation.md` - AI recommendation engine
- `GoalPlanning.md` - Goal-based financial planning
- `ScenarioWhatif.md` - Scenario analysis
- `Personalization.md` - Personalization engine

### Cross-Cutting Concerns
- `Architecture.md` - System architecture and design principles
- `DataManagement.md` - Data handling, versioning, audit trails
- `securityCompliance.md` - Security measures and regulatory compliance
- `performance.md` - Performance targets and optimization
- `UserFlows.md` - User journeys and UX principles
- `Notifications.md` - Notification system and alerts
- `reporting.md` - Reporting capabilities and export formats
- `integration.md` - External system integrations
- `roadmapConsideration.md` - Development roadmap
- `successMetrics.md` - KPIs and success measurement
- `riskMitigation.md` - Risk management strategy

**Location:** All context files are in the project root directory.

---

## Task Workflow

### For Each Task:

1. **Read Context Files**
   - Read ALL listed context files
   - Find the specific sections mentioned in "Agent Instructions"
   - Understand complete requirements

2. **Implement Code**
   - Follow specifications exactly
   - Use correct patterns for technology (React 19, FastAPI, etc.)
   - Keep code simple and maintainable

3. **Write Tests**
   - Write ALL required tests listed in task
   - Aim for comprehensive coverage
   - Test happy paths AND error cases

4. **Run Tests**
   - Run all tests for the component/feature
   - Fix any failures immediately
   - Ensure 100% pass rate

5. **Verify**
   - Run linting (must pass with 0 errors)
   - Check test coverage (>80%)
   - Manually test functionality

6. **Mark Complete**
   - Check box ONLY when 100% complete
   - All tests passing
   - All acceptance criteria met

---

## Code Quality Standards

### Python Backend

**Style:**
- Follow PEP 8
- Use black for formatting
- Use isort for imports
- Use mypy for type checking

**Structure:**
- SOLID principles
- Clean architecture (separate layers)
- Comprehensive type hints
- Docstrings for all public functions

**Testing:**
- pytest for all tests
- Mock external dependencies
- Test edge cases
- >80% coverage

### React Frontend

**Style:**
- ESLint configuration
- Prettier for formatting
- Consistent component structure

**Patterns:**
- React 19 (no forwardRef)
- Import from 'internal-packages/ui'
- Minimal useEffect usage
- Simple, obvious components

**Testing:**
- Jest for component tests
- Mock all API calls
- Test all user interactions
- Snapshot tests for structure

---

## Performance Targets

**Backend:**
- API responses: <500ms (95th percentile)
- Authentication: <200ms
- Dashboard load: <2 seconds
- Database queries: Optimized (no N+1)

**Frontend:**
- Initial load: <3 seconds
- Dashboard render: <2 seconds
- Bundle size: <500KB gzipped
- Mobile responsive

---

## Security Requirements

**Backend:**
- Argon2 password hashing
- RS256 JWT tokens
- Rate limiting on all endpoints
- Input validation (Pydantic)
- SQL injection prevention
- XSS protection

**Frontend:**
- Secure token storage
- CSRF protection (if using cookies)
- Input sanitization
- No sensitive data in console/errors

---

## Phase Testing Gates

Each phase ends with a comprehensive testing gate. **DO NOT PROCEED** until all tests pass:

### Security Tests (CRITICAL)
- Password hashing correct
- JWT tokens secure
- Sessions expire correctly
- Rate limiting works
- SQL injection blocked
- XSS attempts sanitized

### Functional Tests
- All features work as specified
- Error cases handled gracefully
- Edge cases tested

### Integration Tests
- End-to-end user journeys work
- Cross-module data flows correctly
- Load testing passes

### Code Quality
- Test coverage >80%
- Linting passes (0 errors)
- Security audit passes
- Documentation complete

### Performance Tests
- Response times meet targets
- Database queries optimized
- Frontend loads quickly

### User Acceptance
- Complete user flows work
- Error messages clear and helpful
- UX smooth and intuitive

---

## Example Agent Workflow

```markdown
### Task 1.1.1: User Registration - Data Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`, `DataManagement.md`

**Agent Instructions:**
1. Read userAuth.md - Feature 1.1: User Registration, Data Models section
2. Read securityCompliance.md for encryption requirements
3. Read DataManagement.md for audit trail requirements
4. Implement exact table structure specified in userAuth.md

**Tasks:**
- [ ] Create `users` table with all fields from specification
- [ ] Create `email_verification_tokens` table
- [ ] Add appropriate indexes
- [ ] Create database migration using Alembic
- [ ] Create User model/entity with Pydantic/SQLAlchemy
- [ ] **Test Suite:**
  - Test user model creation
  - Test unique email constraint
  - Test default status is PENDING_VERIFICATION
- [ ] **Run:** `pytest tests/models/test_user_model.py -v`
- [ ] **Acceptance:** All model tests pass

**Agent Process:**
Step 1: Read userAuth.md (Feature 1.1 section)
Step 2: Read securityCompliance.md
Step 3: Read DataManagement.md
Step 4: Implement exact table structure
Step 5: Write comprehensive tests
Step 6: Run pytest - ensure 100% pass
Step 7: Mark task complete
```

---

## Key Principles

1. **Quality First** - Comprehensive testing before moving forward
2. **Simplicity** - Keep code simple, obvious, and maintainable
3. **Security** - Always implement security best practices
4. **Performance** - Meet performance targets from the start
5. **Documentation** - Code should be self-documenting
6. **Testing** - Test continuously, not at the end
7. **Modularity** - Each module independent and focused

---

## Getting Help

- **Task unclear?** Read the context files listed
- **Specification unclear?** Check the shard documentation
- **Testing issues?** Review testing strategy above
- **Agent questions?** Check `.claude/agents/` configs

---

**Remember:** The app must remain functional at all times. Every change must be tested and working before proceeding to the next task.
