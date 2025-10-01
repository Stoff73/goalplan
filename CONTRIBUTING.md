# Contributing to GoalPlan

Thank you for your interest in contributing to GoalPlan! This guide will help you get started.

## Development Workflow

### 1. Read the Documentation First

Before starting work, read these essential documents:

- **`.claude/instructions.md`** - Complete development workflow and rules
- **`TASKS_README.md`** - Current phase and task structure
- **`CLAUDE.md`** - Project overview and conventions
- Relevant feature specs (e.g., `userAuth.md`, `Savings.md`)

### 2. Work Sequentially Through Phases

Development is organized into phases. Each phase must be **100% complete** with all tests passing before moving to the next:

- Phase 0: Project Setup ✓
- Phase 1: Authentication & User Management
- Phase 2: Core Modules
- Phase 3: Advanced Features
- Phase 4: Intelligence & AI
- Phase 5: Enhancement & Scale

See phase task files (`phase1a_authentication_tasks.md`, etc.) for detailed tasks.

### 3. Follow the Task Workflow

For each task:

1. **Read context files** - Listed at the top of each task
2. **Implement code** - Follow specifications exactly
3. **Write tests** - Comprehensive coverage (>80%)
4. **Run tests** - All must pass
5. **Run linting** - Must pass with 0 errors
6. **Mark complete** - Only when 100% done

## Code Standards

### Python Backend

**Style:**
```bash
black .                # Format code
isort .                # Sort imports
mypy .                 # Type checking
```

**Requirements:**
- Comprehensive type hints throughout
- Docstrings for all public functions
- SOLID principles
- >80% test coverage
- All tests pass

**File Naming:**
- `snake_case.py` for modules
- `test_*.py` or `*_test.py` for tests

### React Frontend

**Style:**
```bash
npm run lint           # ESLint
npm run lint:fix       # Auto-fix
```

**Requirements:**
- **ALWAYS** import UI components from `'internal-packages/ui'`
- **NEVER** use `forwardRef` (React 19 doesn't need it)
- **AVOID** `useEffect` unless absolutely necessary
- Simple, obvious component structure
- Comprehensive Jest tests

**File Naming:**
- `PascalCase.jsx` for components
- `camelCase.js` for utilities
- `*.test.jsx` for tests

## Testing Requirements

### Backend (pytest)

```bash
cd backend
pytest tests/ -v                    # Run all tests
pytest --cov=. --cov-report=html   # With coverage
```

**Test Types:**
- Unit tests - Individual functions
- Integration tests - API endpoints and database
- Load tests - Performance under load

**Coverage:** Must maintain >80%

### Frontend (Jest + Playwright)

```bash
# Component tests (Jest)
npm test
npm run test:watch

# E2E tests (Playwright)
npx playwright test
npx playwright test --ui
```

**Test Types:**
- **Jest:** Component unit tests, integration tests, snapshots
- **Playwright:** End-to-end user flows only (NOT component testing)

**Requirements:**
- Mock all API calls in component tests
- Test loading states, error states, success states
- Test user interactions

## Git Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Development branch
- Feature branches: `feature/task-description`
- Bug fixes: `fix/bug-description`

### Commit Messages

Follow conventional commits:

```
feat: add user registration endpoint
fix: correct tax calculation for SA residents
docs: update database setup guide
test: add tests for authentication flow
refactor: simplify user model structure
chore: update dependencies
```

All commits should include:
```
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Before Committing

1. Run all tests - must pass
2. Run linting - must pass with 0 errors
3. Update documentation if needed
4. Ensure code follows project conventions

## Security Guidelines

**Critical Requirements** (from CLAUDE.md):

- **Password Hashing:** Argon2 only (NOT bcrypt)
- **JWT Tokens:** RS256 asymmetric signing (NOT HS256 in production)
- **Sessions:** Redis-backed, 15min access + 7-day refresh
- **Rate Limiting:** On all mutation endpoints
- **Encryption:** PII fields (account numbers, sensitive data)
- **Account Lockout:** 5 failed attempts = 30min lockout
- **2FA:** TOTP with backup codes

Never:
- Commit secrets or credentials
- Use weak password hashing
- Skip input validation
- Disable security features

## Performance Targets

- API responses: <500ms (95th percentile)
- Authentication: <200ms
- Dashboard load: <2 seconds
- No N+1 database queries
- Frontend bundle: <500KB gzipped

## Documentation

Update documentation when:
- Adding new features
- Changing API endpoints
- Modifying database schema
- Updating configuration

Document in:
- Code comments (for complex logic)
- Docstrings (for public APIs)
- README files (for setup/usage)
- ADRs (for architectural decisions)

## Architecture Decision Records (ADRs)

For significant architectural decisions, create an ADR in `docs/adr/`:

```markdown
# ADR NNNN: Title

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated | Superseded

## Context
[Describe the problem and context]

## Decision
[Describe the decision made]

## Rationale
[Explain why this decision was made]

## Consequences
[Describe positive, negative, and neutral consequences]

## Alternatives Considered
[List alternatives and why they were rejected]
```

## Getting Help

### Documentation
- `.claude/instructions.md` - Development rules
- `SHARDS_README.md` - Feature specifications
- `TASKS_README.md` - Task structure
- Feature shard files - Detailed requirements

### Resources
- FastAPI: https://fastapi.tiangolo.com/
- React 19: https://react.dev/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Playwright: https://playwright.dev/

## Testing Gates

**⛔ CRITICAL:** Do NOT proceed to the next phase until:

1. **All tests pass** - Backend and frontend
2. **Linting passes** - 0 errors
3. **Coverage >80%** - For all modules
4. **Security audit passes** - No vulnerabilities
5. **Documentation complete** - All changes documented
6. **User acceptance** - Features work end-to-end

## Code Review Checklist

Before marking a task complete:

- [ ] Tests written and passing
- [ ] Linting passes
- [ ] Type hints complete (Python)
- [ ] Error handling implemented
- [ ] Security best practices followed
- [ ] Performance acceptable
- [ ] Documentation updated
- [ ] No console errors/warnings
- [ ] Follows project conventions
- [ ] Ready for production

## Questions?

Consult the project documentation first. Most answers are in:
- `.claude/instructions.md`
- Feature shard files
- `CLAUDE.md`
- Phase task files

---

**Remember:** Quality over speed. The app must remain functional at all times.
