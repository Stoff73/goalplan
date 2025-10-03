# ADR 0001: Technology Stack Selection

**Date:** 2025-10-01
**Status:** Accepted

## Context

GoalPlan requires a robust technology stack for building a dual-country financial planning platform. The platform must handle complex tax calculations, multi-currency support, temporal data, and provide a responsive user experience.

## Decision

We have selected the following technology stack:

### Backend
- **Python 3.12+** with **FastAPI**: Modern async framework with excellent performance and automatic API documentation
- **PostgreSQL 15+**: Robust relational database with strong ACID compliance for financial data
- **Redis 7+**: High-performance caching and session management
- **SQLAlchemy 2.0**: Async ORM with comprehensive features
- **Alembic**: Database migration tool
- **Argon2**: Password hashing algorithm (security requirement)

### Frontend
- **React 19**: Latest version with improved patterns (no forwardRef needed)
- **Vite**: Fast build tool and development server
- **React Router**: Client-side routing
- **Context API**: Simple state management for current requirements

### Testing
- **pytest**: Python testing framework
- **Jest**: React component testing
- **Playwright**: End-to-end testing

### Development Tools
- **Black, isort, mypy**: Python code quality
- **ESLint, Prettier**: JavaScript code quality
- **Pre-commit hooks**: Automated code quality checks

## Rationale

### FastAPI over Django/Flask
- Async support out of the box for better performance
- Automatic OpenAPI documentation
- Modern Python type hints throughout
- Better suited for API-first architecture

### PostgreSQL over MySQL/MongoDB
- Superior support for complex queries and joins (essential for financial calculations)
- Better ACID compliance for financial data integrity
- Rich type system including JSON support
- Excellent temporal data support

### React 19 over Vue/Angular
- Large ecosystem and community
- Strong TypeScript support
- Latest version with simplified patterns
- Team familiarity

### Redis over Memcached
- Richer data structures
- Persistence options
- Pub/sub capabilities for future real-time features
- Session management support

### Context API over Redux/MobX
- Simpler for current requirements
- Built into React (no external dependency)
- Sufficient for current complexity
- Can migrate to more complex solution if needed in Phase 4+

## Consequences

### Positive
- Modern, performant stack
- Strong type safety (Python type hints, TypeScript potential)
- Excellent developer experience
- Good documentation and community support
- Meets all security requirements from CLAUDE.md

### Negative
- Learning curve for team members unfamiliar with FastAPI or React 19
- PostgreSQL requires more operational overhead than simpler databases
- Context API may need replacement in Phase 4+ if state complexity grows

### Neutral
- Need to maintain Python and Node.js environments
- Multiple testing frameworks (pytest, Jest, Playwright)

## Alternatives Considered

1. **Django + Django REST Framework**
   - Rejected: More opinionated, heavier framework, less async support

2. **Node.js + Express**
   - Rejected: Python preferred for data science/ML features in Phase 4+

3. **Next.js**
   - Rejected: SSR not required, additional complexity not justified

4. **MongoDB**
   - Rejected: Financial data requires strong ACID compliance and relational integrity

## References

- CLAUDE.md - Security requirements (Argon2, RS256 JWT)
- Architecture.md - API-first, modular design principles
- performance.md - Performance targets requiring async operations
