# GoalPlan

**Dual-Country Financial Planning Platform for UK and South Africa**

A comprehensive financial planning application for individuals managing finances across both the United Kingdom and South Africa, with AI-driven advice accounting for dual tax treaties, domicile rules, and country-specific regulations.

## Overview

GoalPlan eliminates the complexity of managing finances across two tax jurisdictions by providing a single integrated platform for:

- Financial planning and goal tracking
- Tax calculation and optimization (UK & SA)
- Investment portfolio management
- Retirement planning (pensions & retirement funds)
- Inheritance tax (IHT) and estate planning
- Savings management (ISA, TFSA, cash accounts)
- Protection planning (life assurance)

## Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 15+
- **Cache/Sessions:** Redis 7+
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Testing:** pytest

### Frontend
- **Framework:** React 19
- **Build Tool:** Vite
- **Routing:** React Router
- **State:** Context API
- **Testing:** Jest (components), Playwright (E2E)

### Infrastructure
- **API Style:** RESTful
- **Authentication:** JWT (RS256)
- **Password Hashing:** Argon2
- **Validation:** Pydantic

## Project Structure

```
goalplan/
├── backend/              # Python FastAPI backend
│   ├── alembic/         # Database migrations
│   ├── api/             # API endpoints (Phase 1+)
│   ├── models/          # Database models (Phase 1+)
│   ├── services/        # Business logic (Phase 1+)
│   ├── tests/           # Backend tests
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   ├── main.py          # FastAPI application
│   └── redis_client.py  # Redis client
├── frontend/            # React frontend
│   ├── src/
│   │   ├── api/        # API client
│   │   ├── components/ # React components
│   │   ├── contexts/   # Context providers
│   │   └── utils/      # Utility functions
│   └── vite.config.js
├── internal-packages/   # Internal UI library
│   └── ui/
├── e2e/                # Playwright E2E tests
├── tests/              # Shared test utilities
└── .claude/            # Claude Code configuration
    ├── agents/         # Custom agent definitions
    └── instructions.md # Development instructions
```

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **PostgreSQL 15+**
- **Redis 7+**

### Backend Setup

1. **Install PostgreSQL and Redis** (see `backend/DATABASE_SETUP.md` for detailed instructions)

2. **Create database and user:**
   ```bash
   createuser -P goalplan_user
   createdb -O goalplan_user goalplan_dev
   ```

3. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start backend server:**
   ```bash
   uvicorn main:app --reload
   # API available at http://localhost:8000
   # Docs available at http://localhost:8000/docs
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cd frontend
   cp .env.example .env
   ```

3. **Start development server:**
   ```bash
   npm run dev
   # Application available at http://localhost:5173
   ```

## Development

### Running Tests

**Backend:**
```bash
cd backend
pytest tests/ -v                          # All tests
pytest tests/test_connectivity.py -v     # Connectivity tests
pytest --cov=. --cov-report=html         # With coverage
```

**Frontend:**
```bash
npm test                                  # Jest component tests
npm run test:watch                        # Watch mode
npx playwright test                       # E2E tests
npx playwright test --ui                  # E2E with UI
```

### Code Quality

**Backend:**
```bash
cd backend
black .                # Format code
isort .                # Sort imports
mypy .                 # Type checking
```

**Frontend:**
```bash
npm run lint           # ESLint
npm run lint:fix       # Auto-fix issues
```

### API Documentation

With the backend running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Development Phases

Development is organized into 5 phases:

- **Phase 0:** Project Setup ✓ (Complete)
- **Phase 1:** Authentication & User Management (3-4 months)
- **Phase 2:** Core Modules (4-5 months)
- **Phase 3:** Advanced Features (5-6 months)
- **Phase 4:** Intelligence & AI (4-5 months)
- **Phase 5:** Enhancement & Scale (6-8 months)

See `TASKS_README.md` for detailed task breakdown.

## Key Features

### Multi-Currency Support
- GBP, ZAR, USD, EUR
- Real-time exchange rates
- Historical rate tracking

### Dual Tax System
- UK: Income Tax, NI, CGT, IHT
- SA: Income Tax, CGT, Estate Duty
- Double Tax Agreement (DTA) relief
- Tax residency determination (SRT, SA presence test)

### Tax Year Handling
- UK: April 6 - April 5
- SA: March 1 - February 28/29
- Temporal data with effective dates
- Point-in-time queries

### Security
- Argon2 password hashing
- RS256 JWT tokens
- Redis session management
- Rate limiting
- Field-level encryption for PII
- Account lockout protection
- 2FA (TOTP)

## Documentation

- **CLAUDE.md** - Project overview and conventions
- **TASKS_README.md** - Development tasks and phases
- **.claude/instructions.md** - Development workflow
- **SHARDS_README.md** - Feature specifications index
- **backend/DATABASE_SETUP.md** - Database setup guide
- **prd.md** - Product requirements
- **Architecture.md** - System architecture
- **securityCompliance.md** - Security requirements

## Contributing

1. Read `.claude/instructions.md` for development workflow
2. Check `TASKS_README.md` for current phase and tasks
3. Review relevant feature specs in the shard files
4. Ensure all tests pass before committing
5. Follow code quality standards (linting, type hints)

## License

Proprietary - All rights reserved

## Support

For project-specific questions, consult:
- Feature specs in root directory (e.g., `userAuth.md`, `Savings.md`)
- Development instructions in `.claude/instructions.md`
- Task files (`phase0_tasks.md`, `phase1a_authentication_tasks.md`, etc.)
