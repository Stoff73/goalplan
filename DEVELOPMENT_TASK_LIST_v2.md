# Comprehensive Development Task List

## Dual-Country Financial Planning Platform

**Last Updated:** October 1, 2025
**Document Purpose:** Step-by-step development checklist with testing gates and agent delegation
**Critical Rule:** ⛔ **DO NOT PROCEED TO NEXT PHASE UNTIL ALL TESTS PASS** ⛔

---

## How to Use This Document

1. **Work sequentially** - Complete tasks in order within each phase
2. **Reference shard files** - Each task lists required context files to read BEFORE starting
3. **Delegate to agents** - Use specialized agents for Python backend and React frontend tasks
4. **Test continuously** - Run tests after each task, fix immediately
5. **Testing Gates** - Must pass 100% of tests before proceeding to next phase
6. **Check boxes** - Mark tasks complete only when all tests pass
7. **Maintain functionality** - App must remain functional throughout development

---

## Agent Delegation Rules

### 🐍 Python Backend Tasks

**MANDATORY:** All Python backend code MUST be delegated to `python-backend-engineer` agent

**Process:**
1. Agent MUST read all listed "Context Files" before starting
2. Implement code following specifications in context files
3. Write comprehensive tests
4. Ensure all tests pass before marking complete

Tasks include:
- API endpoint implementation
- Database models and migrations
- Business logic services
- Authentication and security
- Background jobs and async tasks
- Testing (pytest)

### ⚛️ React Frontend Tasks

**MANDATORY:** All React frontend code MUST be delegated to `react-coder` agent

**Process:**
1. Agent MUST read all listed "Context Files" before starting
2. Import UI components from 'internal-packages/ui'
3. Follow React 19 patterns (no forwardRef)
4. Keep components simple and obvious
5. Write comprehensive tests using Jest (component testing, integration testing)

**Testing Strategy:**
- **Jest** - Component unit tests, integration tests, snapshot tests
- **Playwright** - End-to-end user flow testing only (not component testing)

Tasks include:
- React components
- UI/UX implementation
- Forms and validation
- State management
- Routing
- Component testing (Jest only)

---

# PHASE 0: PROJECT SETUP & FOUNDATION

## 0.1 Development Environment Setup

### Task 0.1.1: Initialize Project Structure

**Context Files:** `Architecture.md`, `DataManagement.md`

- [ ] Create repository with appropriate .gitignore
- [ ] Set up monorepo structure (frontend/backend/shared)
- [ ] Initialize package managers (npm for frontend, pip for backend)
- [ ] Configure version control (Git with feature branch workflow)
- [ ] Set up development branch protection rules
- [ ] **Test:** Verify clean repository structure, all team members can clone

### Task 0.1.2: Configure Development Tools

**Context Files:** `Architecture.md`

- [ ] Set up linting (ESLint, Prettier for frontend)
- [ ] Configure backend linting/formatting (black, isort, mypy)
- [ ] Set up pre-commit hooks (lint, format, basic tests)
- [ ] Configure EditorConfig for consistency
- [ ] Set up CI/CD pipeline basics (GitHub Actions/GitLab CI)
- [ ] **Test:** Run lint on empty project structure, should pass with 0 errors

### Task 0.1.3: Database Setup

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Architecture.md`, `DataManagement.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read Architecture.md for database design principles
2. Read DataManagement.md for data handling requirements
3. Read securityCompliance.md for security requirements

**Tasks:**
- [ ] Choose database (PostgreSQL recommended for relational data)
- [ ] Set up local development database
- [ ] Configure database migrations system (Alembic)
- [ ] Create initial database connection config
- [ ] Set up Redis for caching and sessions
- [ ] **Test:** Connect to database successfully, run empty migration

### Task 0.1.4: Backend Framework Setup

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Architecture.md`, `performance.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read Architecture.md for API-first approach and modular design
2. Read performance.md for performance targets
3. Read securityCompliance.md for security headers and logging requirements

**Tasks:**
- [ ] Initialize backend framework (FastAPI recommended)
- [ ] Use `pip` for dependency management
- [ ] Configure environment variables (.env setup)
- [ ] Set up logging system
- [ ] Configure error handling middleware
- [ ] Set up health check endpoint (`/health`)
- [ ] **Test:** Start backend server, access health check endpoint, returns 200

### Task 0.1.5: Frontend Framework Setup

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Architecture.md`, `UserFlows.md`, `performance.md`

**Agent Instructions:**
1. Read Architecture.md for frontend architecture principles
2. Read UserFlows.md for UX requirements
3. Read performance.md for performance targets

**Tasks:**
- [ ] Initialize frontend framework (React 19)
- [ ] Set up routing system
- [ ] Configure state management (Context API)
- [ ] Set up API client (fetch wrapper)
- [ ] Configure environment-specific settings
- [ ] Import UI components from 'internal-packages/ui'
- [ ] **Test:** Start frontend dev server, see default page load without errors

### Task 0.1.6: Testing Infrastructure

**Context Files:** `Architecture.md`, `riskMitigation.md`

- [ ] **Backend (🐍 DELEGATE):** Set up pytest framework
- [ ] **Frontend (⚛️ DELEGATE):** Set up Jest
- [ ] Configure integration testing framework
- [ ] Set up E2E testing framework (Playwright)
- [ ] Create test database seeding scripts
- [ ] Configure test coverage reporting (aim for >80%)
- [ ] **Test:** Run empty test suite, should pass (0 tests, 0 failures)

### Task 0.1.7: Documentation Setup

**Context Files:** `Architecture.md`

- [ ] Set up API documentation (OpenAPI)
- [ ] Create README with setup instructions
- [ ] Initialize architecture decision records (ADR) folder
- [ ] Set up inline code documentation standards
- [ ] Create CONTRIBUTING.md guidelines
- [ ] **Test:** Generate API documentation, view in browser

---

## 🚦 PHASE 0 TESTING GATE

### Must Pass Before Proceeding

- [ ] ✅ All services start without errors (backend, frontend, database, Redis)
- [ ] ✅ Health check endpoint returns 200 OK
- [ ] ✅ Frontend loads default page successfully
- [ ] ✅ Database connection successful
- [ ] ✅ Linting passes with 0 errors
- [ ] ✅ Empty test suites run successfully
- [ ] ✅ API documentation generates and displays
- [ ] ✅ Git pre-commit hooks function correctly

**Acceptance Criteria:** Development environment fully operational, team can start coding.

---

# PHASE 1: FOUNDATION - AUTHENTICATION & USER MANAGEMENT

## 1.1 User Authentication System

### Task 1.1.1: User Registration - Data Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`, `DataManagement.md`

**Agent Instructions:**
1. Read userAuth.md - Feature 1.1: User Registration, Data Models section
2. Read securityCompliance.md for encryption and data protection requirements
3. Read DataManagement.md for audit trail requirements
4. Implement exact table structure specified in userAuth.md

**Tasks:**
- [ ] Create `users` table with all fields from specification
- [ ] Create `email_verification_tokens` table
- [ ] Add appropriate indexes (email, token, expires_at)
- [ ] Create database migration using Alembic
- [ ] Create User model/entity with Pydantic/SQLAlchemy
- [ ] **Test Suite:**
  - Test user model creation
  - Test unique email constraint
  - Test password field is nullable (not set yet)
  - Test default status is PENDING_VERIFICATION
  - Test timestamps auto-populate
- [ ] **Run:** `pytest tests/models/test_user_model.py -v`
- [ ] **Acceptance:** All model tests pass (aim for 100% coverage on models)

### Task 1.1.2: Password Hashing Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`, `riskMitigation.md`

**Agent Instructions:**
1. Read userAuth.md - Technical Requirements: Argon2 hashing section
2. Read securityCompliance.md for encryption standards
3. Read riskMitigation.md for password security best practices
4. Use Argon2 (not bcrypt) as specified

**Tasks:**
- [ ] Install Argon2 library (argon2-cffi)
- [ ] Create password hashing utility module
- [ ] Implement hash_password() function
- [ ] Implement verify_password() function
- [ ] Configure Argon2 parameters (time cost, memory cost, parallelism)
- [ ] **Test Suite:**
  - Test password hashing produces different hash each time (salt)
  - Test password verification with correct password returns True
  - Test password verification with wrong password returns False
  - Test password hash is not reversible
  - Test performance (should hash in <500ms)
- [ ] **Run:** `pytest tests/security/test_password_hashing.py -v`
- [ ] **Acceptance:** 100% pass, all security tests green

### Task 1.1.3: Email Service Integration

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `Notifications.md`

**Agent Instructions:**
1. Read userAuth.md - Technical Requirements: SendGrid/AWS SES section
2. Read Notifications.md for email delivery requirements
3. Implement async email queue as specified

**Tasks:**
- [ ] Choose email service (SendGrid recommended for start)
- [ ] Set up email service account and API key
- [ ] Create email sending service/module
- [ ] Create email template for verification
- [ ] Implement send_verification_email() function
- [ ] Add email to message queue (async processing)
- [ ] **Test Suite:**
  - Test email service connection
  - Test verification email template renders correctly
  - Test email contains verification token
  - Test email queues successfully
  - Mock send and verify payload structure
- [ ] **Run:** `pytest tests/services/test_email_service.py -v`
- [ ] **Acceptance:** All tests pass, send test email successfully received

### Task 1.1.4: Registration Endpoint Implementation

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`, `performance.md`

**Agent Instructions:**
1. Read userAuth.md - Feature 1.1: Implementation Approach (complete section)
2. Read securityCompliance.md for input validation requirements
3. Read performance.md for response time targets (<500ms)
4. Implement exact endpoint structure from userAuth.md

**Tasks:**
- [ ] Create `POST /api/v1/auth/register` endpoint (FastAPI)
- [ ] Implement request validation (Pydantic models)
- [ ] Implement email uniqueness check
- [ ] Implement password complexity validation
- [ ] Generate email verification token (UUID)
- [ ] Hash password and create user record
- [ ] Store verification token in database/Redis
- [ ] Queue verification email
- [ ] Return appropriate response (don't reveal if email exists)
- [ ] **Test Suite:**
  - Test successful registration flow
  - Test duplicate email returns 409 Conflict
  - Test weak password rejected (400)
  - Test invalid email format rejected (400)
  - Test terms not accepted rejected (400)
  - Test verification token generated and stored
  - Test verification email queued
  - Test response doesn't leak user existence
- [ ] **Run:** `pytest tests/api/auth/test_registration.py -v`
- [ ] **Acceptance:** All tests pass, manual registration test successful

### Task 1.1.5: Email Verification Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`

**Agent Instructions:**
1. Read userAuth.md - API Endpoints: verify-email section
2. Implement idempotent verification as specified
3. Handle all edge cases listed

**Tasks:**
- [ ] Create `GET /api/v1/auth/verify-email?token={token}` endpoint
- [ ] Implement token lookup and validation
- [ ] Check token expiration (24 hours)
- [ ] Update user status to ACTIVE
- [ ] Mark token as used
- [ ] Handle idempotent verification (already verified)
- [ ] **Test Suite:**
  - Test valid token verifies successfully
  - Test expired token returns error
  - Test invalid token returns error
  - Test already used token returns success (idempotent)
  - Test user status changes to ACTIVE
  - Test multiple verification attempts
- [ ] **Run:** `pytest tests/api/auth/test_email_verification.py -v`
- [ ] **Acceptance:** All tests pass, can verify email successfully

### Task 1.1.6: Rate Limiting Implementation

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`, `riskMitigation.md`

**Agent Instructions:**
1. Read userAuth.md - Technical Requirements: Rate limiting section
2. Read securityCompliance.md for rate limiting requirements
3. Read riskMitigation.md for brute force protection
4. Use Redis for rate limit counters

**Tasks:**
- [ ] Install rate limiting library (slowapi for FastAPI)
- [ ] Configure Redis for rate limiting counters
- [ ] Implement rate limit middleware
- [ ] Apply to registration endpoint (5 attempts/IP/hour)
- [ ] Implement rate limit error response (429)
- [ ] **Test Suite:**
  - Test normal requests pass through
  - Test 6th request from same IP returns 429
  - Test counter resets after time window
  - Test different IPs have separate limits
  - Test rate limit headers in response
- [ ] **Run:** `pytest tests/middleware/test_rate_limiting.py -v`
- [ ] **Acceptance:** Rate limiting works, tests pass

### Task 1.1.7: Registration Integration Tests

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `riskMitigation.md`

**Agent Instructions:**
1. Read userAuth.md - Feature 1.1: Complete flow section
2. Test entire registration journey end-to-end
3. Include load testing as specified

**Tasks:**
- [ ] Create end-to-end registration test
- [ ] Test complete flow: register → email sent → verify → login
- [ ] Test error scenarios end-to-end
- [ ] **Test Suite:**
  - Test full happy path registration flow
  - Test registration with duplicate email
  - Test verification with expired token
  - Test rate limiting in action
  - Load test: 100 concurrent registrations
- [ ] **Run:** `pytest tests/integration/test_registration_flow.py -v`
- [ ] **Acceptance:** Full registration flow works, all edge cases handled

---

## 1.2 User Login & Session Management

### Task 1.2.1: JWT Token Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read userAuth.md - Feature 1.2: JWT with RS256, Data Models
2. Read securityCompliance.md for token security requirements
3. Use RS256 (asymmetric) not HS256 as specified

**Tasks:**
- [ ] Generate RSA key pair for JWT signing
- [ ] Create JWT token generation utility (using python-jose)
- [ ] Implement access token generation (15 min expiry)
- [ ] Implement refresh token generation (7 days expiry)
- [ ] Store keys securely (env variables/vault)
- [ ] **Test Suite:**
  - Test access token generation
  - Test refresh token generation
  - Test tokens contain correct claims (user_id, jti, exp)
  - Test token signature verification
  - Test expired token detection
  - Test token payload decoding
- [ ] **Run:** `pytest tests/security/test_jwt_service.py -v`
- [ ] **Acceptance:** JWT service tests 100% pass

### Task 1.2.2: Session Management

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `DataManagement.md`, `performance.md`

**Agent Instructions:**
1. Read userAuth.md - Feature 1.2: Session management with Redis
2. Read DataManagement.md for audit trail requirements
3. Read performance.md for session validation performance (<10ms)
4. Implement max 5 concurrent sessions as specified

**Tasks:**
- [ ] Create `user_sessions` table (SQLAlchemy model)
- [ ] Create `login_attempts` table
- [ ] Add appropriate indexes
- [ ] Create session model
- [ ] Implement session creation in Redis
- [ ] Implement session validation middleware
- [ ] Implement session cleanup (expired sessions)
- [ ] **Test Suite:**
  - Test session creation
  - Test session storage in Redis
  - Test session retrieval
  - Test session expiration
  - Test max 5 concurrent sessions per user
  - Test oldest session removal when limit exceeded
- [ ] **Run:** `pytest tests/services/test_session_management.py -v`
- [ ] **Acceptance:** Session management tests pass

### Task 1.2.3: Login Endpoint Implementation

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `performance.md`

**Agent Instructions:**
1. Read userAuth.md - Feature 1.2: Login flow, PROCESS section (complete)
2. Read performance.md for login response time target (<200ms)
3. Follow exact 13-step process from userAuth.md

**Tasks:**
- [ ] Create `POST /api/v1/auth/login` endpoint
- [ ] Implement rate limiting (5 attempts/IP/15 min)
- [ ] Fetch user by email
- [ ] Verify account status (must be ACTIVE)
- [ ] Verify password hash
- [ ] Generate access and refresh tokens
- [ ] Create session record
- [ ] Update last_login_at timestamp
- [ ] Log login attempt (success/failure)
- [ ] Return tokens and user data
- [ ] **Test Suite:**
  - Test successful login flow
  - Test invalid credentials return 401
  - Test unverified account returns 403
  - Test suspended account cannot login
  - Test password verification
  - Test tokens generated and returned
  - Test session created in database and Redis
  - Test login attempt logged
- [ ] **Run:** `pytest tests/api/auth/test_login.py -v`
- [ ] **Acceptance:** All login tests pass

### Task 1.2.4: Account Lockout Implementation

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`, `riskMitigation.md`

**Agent Instructions:**
1. Read userAuth.md - Acceptance Criteria: Account lockout section
2. Read riskMitigation.md for brute force protection requirements
3. Implement 30-minute lockout as specified

**Tasks:**
- [ ] Track failed login attempts per email/IP
- [ ] Implement lockout after 5 failed attempts
- [ ] Set lockout duration (30 minutes)
- [ ] Return 423 Locked status
- [ ] Reset counter on successful login
- [ ] **Test Suite:**
  - Test 5 failed attempts locks account
  - Test locked account returns 423
  - Test lockout expires after 30 minutes
  - Test successful login resets counter
  - Test lockout is per user, not global
- [ ] **Run:** `pytest tests/security/test_account_lockout.py -v`
- [ ] **Acceptance:** Account lockout works correctly

### Task 1.2.5: Token Refresh Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`

**Agent Instructions:**
1. Read userAuth.md - API Endpoints: /auth/refresh
2. Validate refresh token as specified
3. Generate new access token only (not new refresh token)

**Tasks:**
- [ ] Create `POST /api/v1/auth/refresh` endpoint
- [ ] Validate refresh token
- [ ] Check session still valid
- [ ] Generate new access token
- [ ] Update session last_activity timestamp
- [ ] **Test Suite:**
  - Test valid refresh token gets new access token
  - Test expired refresh token rejected
  - Test invalid refresh token rejected
  - Test revoked session cannot refresh
  - Test new access token works
- [ ] **Run:** `pytest tests/api/auth/test_token_refresh.py -v`
- [ ] **Acceptance:** Token refresh works correctly

### Task 1.2.6: Logout Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`

**Agent Instructions:**
1. Read userAuth.md - API Endpoints: /auth/logout, /auth/logout-all
2. Implement idempotent logout
3. Support logout-all for security purposes

**Tasks:**
- [ ] Create `POST /api/v1/auth/logout` endpoint
- [ ] Invalidate current session
- [ ] Remove session from Redis
- [ ] Create `POST /api/v1/auth/logout-all` endpoint
- [ ] Invalidate all user sessions
- [ ] **Test Suite:**
  - Test logout invalidates session
  - Test logged out token cannot be used
  - Test logout-all invalidates all sessions
  - Test logout is idempotent
- [ ] **Run:** `pytest tests/api/auth/test_logout.py -v`
- [ ] **Acceptance:** Logout functionality works

### Task 1.2.7: Authentication Middleware

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `performance.md`

**Agent Instructions:**
1. Read userAuth.md - Technical Requirements: Session management
2. Read performance.md for validation performance (<10ms)
3. Implement as FastAPI dependency for reusability

**Tasks:**
- [ ] Create authentication dependency (FastAPI Depends)
- [ ] Extract JWT from Authorization header
- [ ] Verify token signature
- [ ] Check token expiration
- [ ] Validate session exists and is active
- [ ] Inject user context into request
- [ ] Handle authentication errors gracefully
- [ ] **Test Suite:**
  - Test valid token passes through
  - Test expired token rejected (401)
  - Test invalid signature rejected (401)
  - Test missing token rejected (401)
  - Test user context injected correctly
  - Test session validation
- [ ] **Run:** `pytest tests/middleware/test_auth_middleware.py -v`
- [ ] **Acceptance:** Middleware protects endpoints correctly

---

## 1.3 Two-Factor Authentication (2FA)

### Task 1.3.1: 2FA Data Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read userAuth.md - Feature 1.2: Data Models - user_2fa table
2. Read securityCompliance.md for encryption requirements
3. Encrypt secret and backup_codes columns

**Tasks:**
- [ ] Create `user_2fa` table with SQLAlchemy
- [ ] Implement encryption for secret column
- [ ] Implement encryption for backup_codes column (JSON)
- [ ] Create 2FA Pydantic models
- [ ] **Test Suite:**
  - Test 2FA record creation
  - Test secret encryption/decryption
  - Test backup codes storage
- [ ] **Run:** `pytest tests/models/test_2fa_model.py -v`
- [ ] **Acceptance:** 2FA model tests pass

### Task 1.3.2: TOTP Service Implementation

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read userAuth.md - Technical Requirements: TOTP library (pyotp)
2. Implement 30-second time window as specified
3. Support time window tolerance (90 sec total) for clock skew

**Tasks:**
- [ ] Install TOTP library (pyotp)
- [ ] Create TOTP service
- [ ] Implement secret generation
- [ ] Implement QR code generation for setup (using qrcode library)
- [ ] Implement TOTP verification (with time window)
- [ ] Generate backup codes
- [ ] **Test Suite:**
  - Test secret generation
  - Test TOTP verification with valid code
  - Test TOTP verification with invalid code
  - Test time window tolerance (previous/next)
  - Test backup code generation
  - Test backup code validation
- [ ] **Run:** `pytest tests/services/test_totp_service.py -v`
- [ ] **Acceptance:** TOTP service tests pass

### Task 1.3.3: Enable 2FA Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`

**Agent Instructions:**
1. Read userAuth.md - API Endpoints: /auth/enable-2fa, /auth/verify-2fa-setup
2. Implement 2-step process: setup then verify
3. Only enable 2FA after successful verification

**Tasks:**
- [ ] Create `POST /api/v1/auth/enable-2fa` endpoint (authenticated)
- [ ] Generate TOTP secret
- [ ] Return QR code and secret for setup
- [ ] Store secret (encrypted) but don't enable yet
- [ ] Create `POST /api/v1/auth/verify-2fa-setup` endpoint
- [ ] Verify TOTP code from user
- [ ] Enable 2FA if code valid
- [ ] Generate and return backup codes
- [ ] **Test Suite:**
  - Test 2FA setup initiation
  - Test QR code generation
  - Test verification with correct code enables 2FA
  - Test verification with wrong code fails
  - Test backup codes generated and returned
- [ ] **Run:** `pytest tests/api/auth/test_2fa_setup.py -v`
- [ ] **Acceptance:** 2FA setup flow works

### Task 1.3.4: Login with 2FA

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`

**Agent Instructions:**
1. Read userAuth.md - Feature 1.2: Login flow with 2FA (complete section)
2. Follow exact flow diagram in userAuth.md
3. Support both TOTP codes and backup codes

**Tasks:**
- [ ] Modify login endpoint to check if 2FA enabled
- [ ] If 2FA enabled and not trusted device, require TOTP code
- [ ] Return `requiresTwoFactor: true` response if code needed
- [ ] Accept `totpCode` in login request (optional Pydantic field)
- [ ] Verify TOTP code
- [ ] Support backup code usage
- [ ] Invalidate used backup codes
- [ ] **Test Suite:**
  - Test login without 2FA works as before
  - Test login with 2FA requires code
  - Test login with valid TOTP code succeeds
  - Test login with invalid TOTP code fails
  - Test login with backup code succeeds
  - Test backup code single use
- [ ] **Run:** `pytest tests/api/auth/test_login_with_2fa.py -v`
- [ ] **Acceptance:** 2FA login works correctly

### Task 1.3.5: Disable 2FA Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read userAuth.md - API Endpoints: /auth/disable-2fa
2. Require re-authentication for security
3. Remove secret and backup codes on disable

**Tasks:**
- [ ] Create `POST /api/v1/auth/disable-2fa` endpoint
- [ ] Require password re-entry for security
- [ ] Require TOTP code or backup code
- [ ] Disable 2FA and remove secret
- [ ] **Test Suite:**
  - Test 2FA disabled with correct credentials
  - Test cannot disable without password
  - Test cannot disable without valid TOTP
  - Test 2FA state updated correctly
- [ ] **Run:** `pytest tests/api/auth/test_2fa_disable.py -v`
- [ ] **Acceptance:** 2FA disable works securely

---

## 1.4 Frontend: Authentication UI

### Task 1.4.1: Registration Page

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `userAuth.md`, `UserFlows.md`

**Agent Instructions:**
1. Read userAuth.md - Feature 1.1: User Flow (complete section)
2. Read UserFlows.md for UX principles
3. Import UI components from 'internal-packages/ui'
4. Use React 19 patterns (no forwardRef)
5. Follow flow diagram exactly from userAuth.md
6. Write comprehensive Jest tests for all component logic

**Tasks:**
- [ ] Create registration form component (React 19, no forwardRef)
- [ ] Import UI components from 'internal-packages/ui'
- [ ] Implement email input with validation
- [ ] Implement password input with strength indicator
- [ ] Implement confirm password field
- [ ] Add name fields (first, last)
- [ ] Add country selection dropdown (UK/SA/BOTH)
- [ ] Add terms checkbox
- [ ] Add marketing consent checkbox
- [ ] Implement form validation (client-side with proper state management)
- [ ] Connect to registration API
- [ ] Show success message and verification instructions
- [ ] Handle all error cases (duplicate email, weak password, etc.)
- [ ] **Jest Tests:**
  - Test form validation (email, password strength, required fields)
  - Test API integration (mock API calls)
  - Test error state handling
  - Test success state rendering
  - Snapshot test for component structure
- [ ] **Manual Test:**
  - Register new user successfully
  - Try duplicate email, see error
  - Enter weak password, see validation
  - See password strength indicator work
  - Submit form and see success message
- [ ] **Component Test (Jest):** `tests/components/RegistrationForm.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/registration.spec.js`
- [ ] **Acceptance:** Registration page works, all validations trigger

### Task 1.4.2: Email Verification Page

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `userAuth.md`, `UserFlows.md`

**Agent Instructions:**
1. Read userAuth.md - Feature 1.1: User Flow
2. Keep component simple and functional
3. Avoid useEffect if possible (React 19 best practices)
4. Write Jest tests for all verification states

**Tasks:**
- [ ] Create email verification landing page (simple, functional)
- [ ] Extract token from URL query parameter
- [ ] Call verification API on page load (avoid useEffect if possible)
- [ ] Show success message on verification
- [ ] Show error message if token invalid/expired
- [ ] Provide resend verification link
- [ ] Redirect to login after 3 seconds on success
- [ ] **Jest Tests:**
  - Test successful verification state
  - Test error states (invalid/expired token)
  - Test resend functionality
  - Mock API calls for all scenarios
- [ ] **Manual Test:**
  - Click verification link in email
  - See success message
  - Try expired token, see error
  - Test resend functionality
- [ ] **Component Test (Jest):** `tests/components/EmailVerification.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/email-verification.spec.js`
- [ ] **Acceptance:** Email verification works end-to-end

### Task 1.4.3: Login Page

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `userAuth.md`, `UserFlows.md`

**Agent Instructions:**
1. Read userAuth.md - Feature 1.2: User Flow (complete login section)
2. Read UserFlows.md for login UX principles
3. Use UI components from 'internal-packages/ui'
4. Handle 2FA flow as specified in userAuth.md
5. Write comprehensive Jest tests for all login states

**Tasks:**
- [ ] Create login form component (React 19 patterns)
- [ ] Use UI components from 'internal-packages/ui'
- [ ] Email and password inputs
- [ ] Remember me checkbox
- [ ] Submit connects to login API
- [ ] Store tokens in secure storage (httpOnly cookies preferred)
- [ ] Handle 2FA required response
- [ ] Show 2FA code input if required
- [ ] Handle account locked error (423)
- [ ] Handle invalid credentials error (401)
- [ ] Redirect to dashboard on success
- [ ] **Jest Tests:**
  - Test form validation
  - Test successful login flow (mock API)
  - Test 2FA required state
  - Test error states (401, 403, 423)
  - Test token storage
  - Test remember me functionality
- [ ] **Manual Test:**
  - Login with valid credentials
  - Login with invalid credentials, see error
  - Login with unverified account, see error
  - Try 5 failed attempts, see lockout
- [ ] **Component Test (Jest):** `tests/components/LoginForm.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/login.spec.js`
- [ ] **Acceptance:** Login page works, all error cases handled

### Task 1.4.4: 2FA Setup Page

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `userAuth.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read userAuth.md - Feature 1.2: 2FA setup
2. Display QR code and text secret
3. Force user to download backup codes
4. Write Jest tests for setup flow

**Tasks:**
- [ ] Create 2FA setup page (in settings and onboarding with skip option in onboarding)
- [ ] Import necessary UI components
- [ ] Call enable-2FA API
- [ ] Display QR code for scanning
- [ ] Show text secret as fallback
- [ ] Provide input for verification code
- [ ] Call verify-2fa-setup API
- [ ] Show backup codes on success
- [ ] Force user to download/save backup codes
- [ ] **Jest Tests:**
  - Test QR code display
  - Test verification code input
  - Test successful setup flow
  - Test backup code display and download
  - Mock all API calls
- [ ] **Manual Test:**
  - Scan QR with authenticator app
  - Enter code and verify
  - See backup codes
  - Download backup codes
- [ ] **Component Test (Jest):** `tests/components/TwoFactorSetup.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/2fa-setup.spec.js`
- [ ] **Acceptance:** Can setup 2FA successfully

### Task 1.4.5: Login with 2FA UI

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `userAuth.md`

**Agent Instructions:**
1. Read userAuth.md - Feature 1.2: 2FA login flow
2. Follow exact flow from userAuth.md
3. Support both TOTP and backup codes
4. Write Jest tests for 2FA flow

**Tasks:**
- [ ] Modify login page to handle 2FA flow
- [ ] Show TOTP input if requiresTwoFactor response
- [ ] Submit TOTP code
- [ ] Show "Use backup code" option
- [ ] Handle invalid code error
- [ ] **Jest Tests:**
  - Test 2FA prompt display
  - Test TOTP code submission
  - Test backup code option
  - Test invalid code error handling
  - Mock API responses
- [ ] **Manual Test:**
  - Login with 2FA enabled account
  - Enter TOTP code from app
  - Login successfully
  - Try invalid code, see error
  - Use backup code successfully
- [ ] **Component Test (Jest):** `tests/components/LoginWith2FA.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/login-with-2fa.spec.js`
- [ ] **Acceptance:** 2FA login flow works

### Task 1.4.6: Logout Functionality

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `userAuth.md`, `UserFlows.md`

**Agent Instructions:**
1. Read userAuth.md - API Endpoints: logout
2. Clear all application state
3. Keep UI simple and clear
4. Write Jest tests for logout flow

**Tasks:**
- [ ] Add logout button to navigation (simple, clear)
- [ ] Call logout API
- [ ] Clear stored tokens
- [ ] Clear application state
- [ ] Redirect to login page
- [ ] Show logout confirmation message
- [ ] **Jest Tests:**
  - Test logout API call
  - Test token clearing
  - Test state clearing
  - Test redirect behavior
  - Mock API calls
- [ ] **Manual Test:**
  - Click logout
  - See confirmation
  - Redirect to login
  - Cannot access protected pages
- [ ] **Component Test (Jest):** `tests/components/Logout.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/logout.spec.js`
- [ ] **Acceptance:** Logout works correctly

---

## 🚦 PHASE 1 AUTH TESTING GATE

### Security Tests (CRITICAL)

- [ ] ✅ Password hashing uses Argon2 correctly
- [ ] ✅ JWT tokens signed with RS256
- [ ] ✅ Sessions expire correctly (15 min access, 7 days refresh)
- [ ] ✅ Rate limiting prevents brute force (tested)
- [ ] ✅ Account lockout works after 5 failed attempts
- [ ] ✅ 2FA cannot be bypassed
- [ ] ✅ SQL injection attempts blocked (test with ' OR '1'='1)
- [ ] ✅ XSS attempts sanitized
- [ ] ✅ CSRF tokens implemented (if using cookies)

### Functional Tests

- [ ] ✅ Complete registration flow works
- [ ] ✅ Email verification works
- [ ] ✅ Login works with valid credentials
- [ ] ✅ 2FA setup and login works
- [ ] ✅ Token refresh works
- [ ] ✅ Logout invalidates session
- [ ] ✅ All error cases handled gracefully

### Integration Tests

- [ ] ✅ End-to-end registration → verification → login
- [ ] ✅ Full 2FA setup and usage flow
- [ ] ✅ Load test: 100 concurrent logins

### Code Quality

- [ ] ✅ Test coverage >80% for auth module
- [ ] ✅ All linting passes
- [ ] ✅ Security audit passes (npm audit / safety check)
- [ ] ✅ API documentation complete for all auth endpoints

**Acceptance Criteria:**
🎯 Users can register, verify email, login (with optional 2FA), and logout securely.
🎯 All security measures implemented and tested.
🎯 Authentication system production-ready.

---

## 1.5 User Profile Management

### Task 1.5.1: Profile Data Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `DataManagement.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read userAuth.md for user table structure
2. Read DataManagement.md for audit requirements
3. Read securityCompliance.md for data protection
4. Extend user model with profile fields

**Tasks:**
- [ ] Add profile fields to users table (phone, date_of_birth, address, timezone)
- [ ] Create `user_profile_history` table for audit trail
- [ ] Add indexes for efficient queries
- [ ] Create Pydantic models for profile updates
- [ ] **Test Suite:**
  - Test profile model creation
  - Test profile update with history tracking
  - Test data validation (phone format, date ranges)
  - Test timezone handling
- [ ] **Run:** `pytest tests/models/test_user_profile.py -v`
- [ ] **Acceptance:** Profile model tests pass

### Task 1.5.2: Get Profile Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read userAuth.md for user data structure
2. Read securityCompliance.md for PII protection
3. Return only safe, non-sensitive data
4. Require authentication

**Tasks:**
- [ ] Create `GET /api/v1/user/profile` endpoint (authenticated)
- [ ] Return user profile data (excluding password, sensitive fields)
- [ ] Include account status and metadata
- [ ] **Test Suite:**
  - Test authenticated user can get own profile
  - Test unauthenticated request rejected (401)
  - Test sensitive fields not returned
  - Test response structure correct
- [ ] **Run:** `pytest tests/api/user/test_get_profile.py -v`
- [ ] **Acceptance:** Get profile works securely

### Task 1.5.3: Update Profile Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `DataManagement.md`

**Agent Instructions:**
1. Read userAuth.md for allowed profile fields
2. Read DataManagement.md for audit trail requirements
3. Implement partial updates (PATCH semantics)
4. Track all changes in history table

**Tasks:**
- [ ] Create `PATCH /api/v1/user/profile` endpoint
- [ ] Allow updates: firstName, lastName, phone, dateOfBirth, address, timezone
- [ ] Validate all input data
- [ ] Log changes to profile_history table
- [ ] Email notification on profile change
- [ ] **Test Suite:**
  - Test successful profile update
  - Test partial update (only some fields)
  - Test invalid data rejected
  - Test history recorded
  - Test email notification sent
- [ ] **Run:** `pytest tests/api/user/test_update_profile.py -v`
- [ ] **Acceptance:** Profile updates work with audit trail

### Task 1.5.4: Change Password Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`, `riskMitigation.md`

**Agent Instructions:**
1. Read userAuth.md for password requirements
2. Read securityCompliance.md for password security
3. Read riskMitigation.md for account takeover prevention
4. Require current password verification

**Tasks:**
- [ ] Create `POST /api/v1/user/change-password` endpoint
- [ ] Require current password verification
- [ ] Validate new password meets complexity requirements
- [ ] Hash new password with Argon2
- [ ] Invalidate all existing sessions except current
- [ ] Send email notification
- [ ] **Test Suite:**
  - Test password change with correct current password
  - Test wrong current password rejected
  - Test weak new password rejected
  - Test all other sessions invalidated
  - Test email sent
- [ ] **Run:** `pytest tests/api/user/test_change_password.py -v`
- [ ] **Acceptance:** Password change works securely

### Task 1.5.5: Change Email Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read userAuth.md for email verification flow
2. Implement 2-step verification (new and old email)
3. Prevent email conflicts
4. Require password confirmation

**Tasks:**
- [ ] Create `POST /api/v1/user/change-email` endpoint
- [ ] Require password confirmation
- [ ] Check new email not already in use
- [ ] Send verification to new email
- [ ] Send notification to old email
- [ ] Update email only after verification
- [ ] **Test Suite:**
  - Test email change request
  - Test duplicate email rejected
  - Test verification emails sent
  - Test email updated after verification
  - Test notifications sent
- [ ] **Run:** `pytest tests/api/user/test_change_email.py -v`
- [ ] **Acceptance:** Email change secure and verified

### Task 1.5.6: Delete Account Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `userAuth.md`, `securityCompliance.md`, `DataManagement.md`

**Agent Instructions:**
1. Read securityCompliance.md for GDPR/POPIA compliance
2. Read DataManagement.md for data retention
3. Implement soft delete with retention period
4. Allow data export before deletion

**Tasks:**
- [ ] Create `POST /api/v1/user/delete-account` endpoint
- [ ] Require password confirmation
- [ ] Implement soft delete (mark deleted, retain 30 days)
- [ ] Provide data export option
- [ ] Anonymize user data after retention period
- [ ] Send confirmation email
- [ ] **Test Suite:**
  - Test account deletion request
  - Test password required
  - Test account marked deleted
  - Test user cannot login after deletion
  - Test data export generated
- [ ] **Run:** `pytest tests/api/user/test_delete_account.py -v`
- [ ] **Acceptance:** Account deletion GDPR/POPIA compliant

### Task 1.5.7: Profile Management UI

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `userAuth.md`, `UserFlows.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read userAuth.md for profile fields
2. Read UserFlows.md for UX principles
3. Import UI components from 'internal-packages/ui'
4. Keep forms simple and clear
5. Write comprehensive Jest tests

**Tasks:**
- [ ] Create profile page component
- [ ] Import form components from 'internal-packages/ui'
- [ ] Display current profile data
- [ ] Editable fields: name, phone, address, timezone
- [ ] Change password section
- [ ] Change email section
- [ ] Delete account section (with confirmation)
- [ ] Form validation
- [ ] Success/error message handling
- [ ] **Jest Tests:**
  - Test profile data display
  - Test form validation
  - Test profile update submission
  - Test password change flow
  - Test email change flow
  - Test delete account confirmation
  - Mock all API calls
- [ ] **Manual Test:**
  - View profile page
  - Update profile fields
  - Change password
  - Change email
  - Test delete account flow
- [ ] **Component Test (Jest):** `tests/components/UserProfile.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/user-profile.spec.js`
- [ ] **Acceptance:** Profile management works completely

---

## 1.6 User Information Module - Tax Status

### Task 1.6.1: Tax Status Data Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `TaxResidency.md`, `DataManagement.md`

**Agent Instructions:**
1. Read UserInfo.md - Feature 2.1 complete section
2. Read TaxResidency.md for SRT and SA presence test requirements
3. Read DataManagement.md for temporal data handling
4. Implement exact table structures from UserInfo.md

**Tasks:**
- [ ] Create `user_tax_status` table (temporal data)
- [ ] Create `uk_srt_data` table
- [ ] Create `sa_presence_data` table
- [ ] Add appropriate indexes for temporal queries
- [ ] Create Pydantic models
- [ ] Implement effective_from/effective_to logic
- [ ] **Test Suite:**
  - Test tax status record creation
  - Test temporal validity (no overlaps)
  - Test effective date handling
  - Test domicile calculation logic
  - Test dual residency detection
- [ ] **Run:** `pytest tests/models/test_tax_status.py -v`
- [ ] **Acceptance:** Tax status models work with temporal logic

### Task 1.6.2: Deemed Domicile Calculation Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `TaxResidency.md`

**Agent Instructions:**
1. Read UserInfo.md - Business Logic section (deemed domicile calculation)
2. Implement exact formula from specification
3. Handle edge cases (split year, non-residence)
4. Cache results for performance

**Tasks:**
- [ ] Create deemed domicile calculation service
- [ ] Implement 15/20 year rule
- [ ] Implement domicile of origin rule
- [ ] Handle temporary non-residence
- [ ] **Test Suite:**
  - Test 15 out of 20 years triggers deemed domicile
  - Test domicile of origin rule
  - Test edge cases (exactly 15 years, split years)
  - Test performance (<100ms)
- [ ] **Run:** `pytest tests/services/test_deemed_domicile.py -v`
- [ ] **Acceptance:** Deemed domicile calculated correctly

### Task 1.6.3: UK Statutory Residence Test (SRT) Calculator

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `TaxResidency.md`

**Agent Instructions:**
1. Read TaxResidency.md - Complete UK SRT section
2. Implement automatic overseas test
3. Implement automatic UK test
4. Implement sufficient ties test
5. Follow exact HMRC rules

**Tasks:**
- [ ] Create SRT calculator service
- [ ] Implement automatic overseas test (< 16 days)
- [ ] Implement automatic UK test (>= 183 days)
- [ ] Implement sufficient ties test (5 ties)
- [ ] Calculate ties based on user data
- [ ] Store calculation results
- [ ] **Test Suite:**
  - Test automatic overseas (< 16 days)
  - Test automatic UK (>= 183 days)
  - Test sufficient ties scenarios
  - Test tie calculations (family, accommodation, work, etc.)
  - Test edge cases
- [ ] **Run:** `pytest tests/services/test_srt_calculator.py -v`
- [ ] **Acceptance:** SRT calculator accurate to HMRC rules

### Task 1.6.4: SA Physical Presence Test Calculator

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `TaxResidency.md`

**Agent Instructions:**
1. Read TaxResidency.md - SA physical presence test section
2. Implement 91-day rule (current year)
3. Implement 5-year average rule
4. Handle ordinarily resident status

**Tasks:**
- [ ] Create SA presence test calculator
- [ ] Implement 91 days in current year test
- [ ] Implement 91 days average over 5 years test
- [ ] Determine ordinarily resident status
- [ ] Store calculation results
- [ ] **Test Suite:**
  - Test 91 days current year
  - Test 5-year average calculation
  - Test ordinarily resident determination
  - Test edge cases (exactly 91 days)
- [ ] **Run:** `pytest tests/services/test_sa_presence.py -v`
- [ ] **Acceptance:** SA presence test accurate to SARS rules

### Task 1.6.5: Tax Status Management Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `performance.md`

**Agent Instructions:**
1. Read UserInfo.md - API Endpoints section complete
2. Read performance.md for response time targets
3. Implement temporal data management
4. Trigger recalculation on save

**Tasks:**
- [ ] Create `POST /api/v1/user/tax-status` endpoint
- [ ] Create `GET /api/v1/user/tax-status` endpoint (current)
- [ ] Create `GET /api/v1/user/tax-status/history` endpoint
- [ ] Create `GET /api/v1/user/tax-status/at-date?date={date}` endpoint
- [ ] Create `POST /api/v1/user/tax-status/srt-calculator` endpoint
- [ ] Create `POST /api/v1/user/tax-status/sa-presence-test` endpoint
- [ ] Implement validation (no overlaps, valid combinations)
- [ ] Auto-adjust previous record's effective_to on new insert
- [ ] Calculate deemed domicile and DTA tie-breaker
- [ ] **Test Suite:**
  - Test create new tax status
  - Test temporal validity maintained
  - Test history retrieval
  - Test at-date queries
  - Test calculators work
  - Test validation rules
- [ ] **Run:** `pytest tests/api/user/test_tax_status.py -v`
- [ ] **Acceptance:** Tax status management works completely

### Task 1.6.6: Tax Status UI Components

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `UserInfo.md`, `UserFlows.md`, `TaxResidency.md`

**Agent Instructions:**
1. Read UserInfo.md - User Flow section
2. Read UserFlows.md for UX principles
3. Import UI components from 'internal-packages/ui'
4. Create clear, simple forms for complex data
5. Write comprehensive Jest tests

**Tasks:**
- [ ] Create tax status form component
- [ ] Import UI components from 'internal-packages/ui'
- [ ] Effective date picker
- [ ] UK tax resident toggle
- [ ] SA tax resident toggle
- [ ] Domicile selection dropdown
- [ ] Years in UK/SA inputs
- [ ] Remittance basis selection (if applicable)
- [ ] Show calculated status preview
- [ ] SRT calculator modal
- [ ] SA presence test calculator modal
- [ ] Historical status timeline view
- [ ] **Jest Tests:**
  - Test form validation
  - Test calculated status display
  - Test SRT calculator integration
  - Test SA presence test integration
  - Test history timeline rendering
  - Mock all API calls
- [ ] **Manual Test:**
  - Create new tax status
  - Use SRT calculator
  - Use SA presence test
  - View history timeline
  - See calculated deemed domicile
- [ ] **Component Test (Jest):** `tests/components/TaxStatus.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/tax-status.spec.js`
- [ ] **Acceptance:** Tax status management UI complete

---

## 1.7 User Information Module - Income Tracking

### Task 1.7.1: Income Data Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `CoreTaxCalcs.md`, `DataManagement.md`

**Agent Instructions:**
1. Read UserInfo.md - Feature 2.2 complete section
2. Read CoreTaxCalcs.md for tax calculation integration
3. Read DataManagement.md for multi-currency handling
4. Support UK and SA tax years

**Tasks:**
- [ ] Create `user_income` table
- [ ] Create `income_tax_withholding` table
- [ ] Add indexes for tax year queries
- [ ] Create Pydantic models
- [ ] Implement currency conversion metadata storage
- [ ] **Test Suite:**
  - Test income record creation
  - Test multi-currency support
  - Test tax year allocation
  - Test gross/net income handling
  - Test PAYE/PASE data storage
- [ ] **Run:** `pytest tests/models/test_income.py -v`
- [ ] **Acceptance:** Income models support all requirements

### Task 1.7.2: Currency Conversion Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `performance.md`, `integration.md`

**Agent Instructions:**
1. Read UserInfo.md for currency conversion requirements
2. Read integration.md for exchange rate API options
3. Cache rates for performance
4. Use official HMRC/SARS rates where applicable

**Tasks:**
- [ ] Integrate exchange rate API (exchangerate-api.com or similar)
- [ ] Create currency conversion service
- [ ] Store historical exchange rates
- [ ] Implement rate caching (daily updates)
- [ ] Support GBP, ZAR, USD, EUR minimum
- [ ] **Test Suite:**
  - Test currency conversion accuracy
  - Test historical rate lookup
  - Test caching mechanism
  - Test fallback on API failure
- [ ] **Run:** `pytest tests/services/test_currency_conversion.py -v`
- [ ] **Acceptance:** Currency conversion accurate and cached

### Task 1.7.3: Income Tax Treatment Calculator

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `CoreTaxCalcs.md`, `DTA.md`

**Agent Instructions:**
1. Read UserInfo.md - Business Logic section
2. Read CoreTaxCalcs.md for UK and SA tax rules
3. Read DTA.md for foreign income treatment
4. Determine tax treatment based on source and residency

**Tasks:**
- [ ] Create income tax treatment service
- [ ] Determine applicable jurisdiction (UK, SA, both, neither)
- [ ] Apply PSA exemption (UK interest)
- [ ] Apply SA interest exemption
- [ ] Handle foreign income based on DTA
- [ ] Calculate expected tax liability
- [ ] **Test Suite:**
  - Test UK source income for UK resident
  - Test foreign income for UK resident (different domiciles)
  - Test SA source income for SA resident
  - Test dual resident scenarios
  - Test exemptions (PSA, SA interest)
- [ ] **Run:** `pytest tests/services/test_income_tax_treatment.py -v`
- [ ] **Acceptance:** Tax treatment calculated correctly

### Task 1.7.4: Income Management Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `UserInfo.md`, `performance.md`

**Agent Instructions:**
1. Read UserInfo.md - API Endpoints section
2. Implement CRUD operations
3. Support filtering by tax year
4. Calculate aggregates

**Tasks:**
- [ ] Create `POST /api/v1/user/income` endpoint
- [ ] Create `GET /api/v1/user/income` endpoint (with filters)
- [ ] Create `GET /api/v1/user/income/:id` endpoint
- [ ] Create `PATCH /api/v1/user/income/:id` endpoint
- [ ] Create `DELETE /api/v1/user/income/:id` endpoint (soft delete)
- [ ] Create `GET /api/v1/user/income/summary?taxYear={year}` endpoint
- [ ] Implement tax year filtering
- [ ] Calculate total income aggregates
- [ ] Convert all to base currency
- [ ] **Test Suite:**
  - Test create income record
  - Test retrieve all income
  - Test filter by tax year
  - Test update income
  - Test delete income
  - Test summary calculations
  - Test currency conversion
- [ ] **Run:** `pytest tests/api/user/test_income.py -v`
- [ ] **Acceptance:** Income management endpoints complete

### Task 1.7.5: Income Tracking UI

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `UserInfo.md`, `UserFlows.md`

**Agent Instructions:**
1. Read UserInfo.md - Feature 2.2 complete section
2. Read UserFlows.md for UX principles
3. Import UI components from 'internal-packages/ui'
4. Support multiple income entries
5. Write comprehensive Jest tests

**Tasks:**
- [ ] Create income list view component
- [ ] Create income form component (add/edit)
- [ ] Import UI components from 'internal-packages/ui'
- [ ] Income type dropdown
- [ ] Source country selection
- [ ] Amount and currency inputs
- [ ] Frequency selection
- [ ] Tax year selection
- [ ] PAYE/PASE details section
- [ ] Gross/net toggle
- [ ] Tax withheld input
- [ ] Income summary by tax year
- [ ] Total income display (converted to base currency)
- [ ] **Jest Tests:**
  - Test income list rendering
  - Test add income form
  - Test edit income
  - Test delete income
  - Test summary calculations
  - Test currency conversion display
  - Mock all API calls
- [ ] **Manual Test:**
  - Add employment income
  - Add foreign income
  - View income summary
  - Filter by tax year
  - See total in GBP and ZAR
- [ ] **Component Test (Jest):** `tests/components/IncomeTracking.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/income-tracking.spec.js`
- [ ] **Acceptance:** Income tracking UI complete

---

## 1.8 Central Dashboard

### Task 1.8.1: Dashboard Data Aggregation Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `CentralDashboard.md`, `performance.md`, `DataManagement.md`

**Agent Instructions:**
1. Read CentralDashboard.md - Feature 3.1 complete section
2. Read performance.md for dashboard load time (<2 seconds)
3. Aggregate data from all modules
4. Implement caching strategy

**Tasks:**
- [ ] Create dashboard aggregation service
- [ ] Fetch data from all modules (savings will be only module in Phase 1)
- [ ] Convert all amounts to base currency
- [ ] Calculate total assets
- [ ] Calculate total liabilities
- [ ] Calculate net worth
- [ ] Group by country, asset class, currency
- [ ] Implement Redis caching (5 min TTL)
- [ ] **Test Suite:**
  - Test data aggregation from multiple sources
  - Test currency conversion
  - Test net worth calculation
  - Test grouping by country/asset class
  - Test caching mechanism
  - Test performance (<2 seconds)
- [ ] **Run:** `pytest tests/services/test_dashboard_aggregation.py -v`
- [ ] **Acceptance:** Dashboard aggregation fast and accurate

### Task 1.8.2: Net Worth Snapshot Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `CentralDashboard.md`, `DataManagement.md`

**Agent Instructions:**
1. Read CentralDashboard.md for snapshot requirements
2. Create daily snapshots for trend tracking
3. Implement background job for snapshot creation
4. Retain 2 years of daily snapshots

**Tasks:**
- [ ] Create `net_worth_snapshots` table
- [ ] Create snapshot generation service
- [ ] Implement daily snapshot job (background task)
- [ ] Store snapshot with all breakdown data
- [ ] Calculate changes (day, month, year)
- [ ] **Test Suite:**
  - Test snapshot creation
  - Test snapshot contains all required data
  - Test change calculations
  - Test historical snapshot retrieval
- [ ] **Run:** `pytest tests/services/test_net_worth_snapshot.py -v`
- [ ] **Acceptance:** Snapshots track net worth over time

### Task 1.8.3: Dashboard Endpoint

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `CentralDashboard.md`, `performance.md`

**Agent Instructions:**
1. Read CentralDashboard.md - Implementation Approach section
2. Implement exact response structure from spec
3. Support base currency parameter
4. Use caching for performance

**Tasks:**
- [ ] Create `GET /api/v1/dashboard/net-worth` endpoint
- [ ] Accept baseCurrency query parameter
- [ ] Accept asOfDate query parameter
- [ ] Return net worth summary
- [ ] Return breakdown by country
- [ ] Return breakdown by asset class
- [ ] Return breakdown by currency
- [ ] Return trend data (last 12 months)
- [ ] Return changes (day, month, year)
- [ ] Implement caching
- [ ] **Test Suite:**
  - Test dashboard data retrieval
  - Test base currency conversion
  - Test historical date query
  - Test all breakdowns present
  - Test trend data
  - Test change calculations
  - Test caching
- [ ] **Run:** `pytest tests/api/dashboard/test_net_worth.py -v`
- [ ] **Acceptance:** Dashboard endpoint returns complete data

### Task 1.8.4: Dashboard UI Components

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `CentralDashboard.md`, `UserFlows.md`, `performance.md`

**Agent Instructions:**
1. Read CentralDashboard.md - User Flow section
2. Read UserFlows.md for dashboard UX principles
3. Read performance.md for loading requirements (<2 sec)
4. Import UI components from 'internal-packages/ui'
5. Use Chart.js or Recharts for visualizations
6. Write comprehensive Jest tests

**Tasks:**
- [ ] Create dashboard page component
- [ ] Import UI components from 'internal-packages/ui'
- [ ] Net worth summary card (total, assets, liabilities)
- [ ] Change indicators (day, month, year)
- [ ] Base currency selector
- [ ] Breakdown by country (pie chart)
- [ ] Breakdown by asset class (pie chart)
- [ ] Breakdown by currency (table)
- [ ] Net worth trend chart (line chart, 12 months)
- [ ] Quick links to modules
- [ ] Refresh button with last updated timestamp
- [ ] Loading states
- [ ] Empty states (no data yet)
- [ ] **Jest Tests:**
  - Test dashboard data rendering
  - Test chart rendering (with mock data)
  - Test base currency switching
  - Test refresh functionality
  - Test loading states
  - Test empty states
  - Test quick links
  - Mock all API calls
- [ ] **Manual Test:**
  - View dashboard
  - See net worth summary
  - View charts
  - Switch base currency
  - Refresh data
  - Click quick links
- [ ] **Component Test (Jest):** `tests/components/Dashboard.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/dashboard.spec.js`
- [ ] **Acceptance:** Dashboard loads <2 seconds, displays all data

---

## 1.9 Savings Module

### Task 1.9.1: Savings Account Data Models

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Savings.md`, `DataManagement.md`, `securityCompliance.md`

**Agent Instructions:**
1. Read Savings.md - Feature 5.1 complete section
2. Read DataManagement.md for historical tracking
3. Read securityCompliance.md for account number encryption
4. Implement exact table structure from Savings.md

**Tasks:**
- [ ] Create `savings_accounts` table
- [ ] Create `account_balance_history` table
- [ ] Add indexes for efficient queries
- [ ] Create Pydantic models
- [ ] Implement account number encryption
- [ ] Support ISA and TFSA account types
- [ ] **Test Suite:**
  - Test account creation
  - Test account number encryption
  - Test balance history tracking
  - Test ISA/TFSA flag handling
  - Test multi-currency support
- [ ] **Run:** `pytest tests/models/test_savings_account.py -v`
- [ ] **Acceptance:** Savings account models complete

### Task 1.9.2: Interest Calculation Service

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Savings.md`, `CoreTaxCalcs.md`

**Agent Instructions:**
1. Read Savings.md - Business Logic section (interest calculation)
2. Support simple and compound interest
3. Handle different payment frequencies
4. Project future interest

**Tasks:**
- [ ] Create interest calculation service
- [ ] Implement simple interest calculation
- [ ] Implement compound interest calculation
- [ ] Support monthly, quarterly, annual frequencies
- [ ] Project annual interest earned
- [ ] **Test Suite:**
  - Test simple interest calculation
  - Test compound interest (monthly)
  - Test compound interest (quarterly)
  - Test annual interest projection
  - Test different interest rates
- [ ] **Run:** `pytest tests/services/test_interest_calculation.py -v`
- [ ] **Acceptance:** Interest calculations accurate

### Task 1.9.3: ISA/TFSA Allowance Tracking

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Savings.md`, `CoreTaxCalcs.md`

**Agent Instructions:**
1. Read Savings.md for ISA/TFSA requirements
2. Track annual allowances
3. Calculate remaining allowance
4. Handle tax year boundaries

**Tasks:**
- [ ] Create `isa_contributions` table
- [ ] Create `tfsa_contributions` table
- [ ] Implement ISA allowance tracking (£20,000 for 2024/25)
- [ ] Implement TFSA allowance tracking (R36,000 for 2024)
- [ ] Calculate used and remaining allowance
- [ ] Handle lifetime TFSA limit (R500,000)
- [ ] Alert when nearing limit
- [ ] **Test Suite:**
  - Test ISA contribution tracking
  - Test ISA allowance calculation
  - Test TFSA contribution tracking
  - Test TFSA annual and lifetime limits
  - Test tax year rollover
- [ ] **Run:** `pytest tests/services/test_isa_tfsa_tracking.py -v`
- [ ] **Acceptance:** ISA/TFSA allowances tracked correctly

### Task 1.9.4: Savings Interest Tax Treatment

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Savings.md`, `CoreTaxCalcs.md`

**Agent Instructions:**
1. Read Savings.md - Tax Treatment section
2. Read CoreTaxCalcs.md for UK and SA interest tax rules
3. Apply PSA (UK) and interest exemption (SA)
4. ISA/TFSA interest is tax-free

**Tasks:**
- [ ] Create savings tax treatment service
- [ ] Implement UK PSA calculation (£1000/£500/£0 based on tax band)
- [ ] Implement UK starting rate for savings (£5000 if income < £17,570)
- [ ] Implement SA interest exemption (R23,800 / R34,500)
- [ ] Mark ISA interest as tax-free
- [ ] Mark TFSA interest/growth as tax-free
- [ ] Calculate taxable interest
- [ ] **Test Suite:**
  - Test UK PSA application
  - Test starting rate for savings
  - Test SA interest exemption
  - Test ISA tax-free status
  - Test TFSA tax-free status
  - Test taxable interest calculation
- [ ] **Run:** `pytest tests/services/test_savings_tax_treatment.py -v`
- [ ] **Acceptance:** Savings tax treatment accurate

### Task 1.9.5: Emergency Fund Assessment

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Savings.md`, `AIAdvisoryRecommendation.md`

**Agent Instructions:**
1. Read Savings.md - Emergency Fund Assessment section
2. Calculate recommended emergency fund (6 months expenses)
3. Compare current emergency accounts to target
4. Generate recommendations

**Tasks:**
- [ ] Create emergency fund assessment service
- [ ] Calculate recommended amount (6 × monthly expenses)
- [ ] Sum current emergency fund accounts
- [ ] Calculate emergency fund ratio (current / target)
- [ ] Generate status (adequate, insufficient, none)
- [ ] **Test Suite:**
  - Test recommended calculation
  - Test current sum calculation
  - Test ratio calculation
  - Test status determination
- [ ] **Run:** `pytest tests/services/test_emergency_fund.py -v`
- [ ] **Acceptance:** Emergency fund assessment accurate

### Task 1.9.6: Savings Account Endpoints

**🐍 DELEGATE TO: `python-backend-engineer`**
**Context Files:** `Savings.md`, `performance.md`

**Agent Instructions:**
1. Read Savings.md - API Endpoints section
2. Implement CRUD operations
3. Support balance updates with history
4. Calculate aggregates

**Tasks:**
- [ ] Create `POST /api/v1/savings/accounts` endpoint
- [ ] Create `GET /api/v1/savings/accounts` endpoint
- [ ] Create `GET /api/v1/savings/accounts/:id` endpoint
- [ ] Create `PATCH /api/v1/savings/accounts/:id` endpoint
- [ ] Create `DELETE /api/v1/savings/accounts/:id` endpoint (soft delete)
- [ ] Create `POST /api/v1/savings/accounts/:id/balance` endpoint
- [ ] Create `GET /api/v1/savings/summary` endpoint
- [ ] Create `GET /api/v1/savings/isa-allowance` endpoint
- [ ] Create `GET /api/v1/savings/tfsa-allowance` endpoint
- [ ] Validate balance updates (max 10/day)
- [ ] Track balance history
- [ ] Calculate total savings
- [ ] **Test Suite:**
  - Test create account
  - Test get all accounts
  - Test update account
  - Test update balance
  - Test balance update limit
  - Test delete account
  - Test summary calculations
  - Test ISA/TFSA allowance queries
- [ ] **Run:** `pytest tests/api/savings/test_accounts.py -v`
- [ ] **Acceptance:** Savings account management complete

### Task 1.9.7: Savings Account UI

**⚛️ DELEGATE TO: `react-coder`**
**Context Files:** `Savings.md`, `UserFlows.md`

**Agent Instructions:**
1. Read Savings.md - Feature 5.1 complete section
2. Read UserFlows.md for UX principles
3. Import UI components from 'internal-packages/ui'
4. Support account list and detail views
5. Write comprehensive Jest tests

**Tasks:**
- [ ] Create savings account list component
- [ ] Create account detail component
- [ ] Create add/edit account form
- [ ] Import UI components from 'internal-packages/ui'
- [ ] Bank name and account type inputs
- [ ] Balance input with currency selector
- [ ] Interest rate input
- [ ] Account purpose dropdown
- [ ] ISA/TFSA checkbox
- [ ] Balance history chart
- [ ] Interest projection display
- [ ] Update balance modal
- [ ] Total savings summary
- [ ] Emergency fund status indicator
- [ ] ISA/TFSA allowance widgets
- [ ] **Jest Tests:**
  - Test account list rendering
  - Test add account form
  - Test edit account
  - Test balance update
  - Test summary calculations
  - Test ISA/TFSA allowance display
  - Test emergency fund indicator
  - Mock all API calls
- [ ] **Manual Test:**
  - Add savings account
  - Update balance
  - View balance history
  - See interest projection
  - Check ISA allowance
  - Check TFSA allowance
  - View emergency fund status
- [ ] **Component Test (Jest):** `tests/components/SavingsAccount.test.jsx`
- [ ] **E2E Test (Playwright):** `e2e/savings-account.spec.js`
- [ ] **Acceptance:** Savings account UI complete

---

## 🚦 PHASE 1 COMPLETE TESTING GATE

### Security Tests (CRITICAL)

- [ ] ✅ All authentication security tests pass (from Auth Gate)
- [ ] ✅ PII encryption working (tax status, income, account numbers)
- [ ] ✅ API endpoints require authentication
- [ ] ✅ Users can only access own data
- [ ] ✅ SQL injection blocked on all endpoints
- [ ] ✅ XSS attempts sanitized
- [ ] ✅ Rate limiting on all mutation endpoints

### Functional Tests

**Authentication (1.1-1.4):**
- [ ] ✅ Registration, verification, login, 2FA, logout work
- [ ] ✅ Profile management complete
- [ ] ✅ Password change, email change, account deletion work

**User Information (1.6-1.7):**
- [ ] ✅ Tax status CRUD operations work
- [ ] ✅ SRT calculator accurate
- [ ] ✅ SA presence test accurate
- [ ] ✅ Deemed domicile calculated correctly
- [ ] ✅ Income tracking works
- [ ] ✅ Multi-currency income supported
- [ ] ✅ Tax treatment calculated correctly

**Dashboard (1.8):**
- [ ] ✅ Dashboard loads in <2 seconds
- [ ] ✅ Net worth aggregation correct
- [ ] ✅ All breakdowns display (country, asset class, currency)
- [ ] ✅ Trend chart shows 12 months
- [ ] ✅ Changes calculated correctly

**Savings Module (1.9):**
- [ ] ✅ Account CRUD operations work
- [ ] ✅ Balance updates with history tracking
- [ ] ✅ Interest calculations accurate
- [ ] ✅ ISA allowance tracking correct
- [ ] ✅ TFSA allowance tracking correct
- [ ] ✅ Emergency fund assessment works
- [ ] ✅ Tax treatment calculations correct

### Integration Tests

- [ ] ✅ Full user journey: register → verify → login → setup profile → add tax status → add income → add savings account → view dashboard
- [ ] ✅ Tax status changes reflect in income tax calculations
- [ ] ✅ Savings balances reflect in dashboard
- [ ] ✅ Currency conversion consistent across modules
- [ ] ✅ Load test: 50 concurrent users using all features

### Code Quality

- [ ] ✅ Test coverage >80% for all modules
- [ ] ✅ All linting passes (backend and frontend)
- [ ] ✅ Security audit passes (npm audit / safety check)
- [ ] ✅ API documentation complete for all endpoints
- [ ] ✅ Component documentation complete
- [ ] ✅ No console errors in browser
- [ ] ✅ Mobile responsive on all pages

### Data Quality

- [ ] ✅ All temporal data (tax status) handles overlaps correctly
- [ ] ✅ Historical data retained (balance snapshots, audit trails)
- [ ] ✅ Currency conversion uses correct rates
- [ ] ✅ Tax year boundaries handled correctly (UK and SA)
- [ ] ✅ Soft deletes work (no hard deletes)

### Performance Tests

- [ ] ✅ Dashboard loads in <2 seconds
- [ ] ✅ SRT calculation <100ms
- [ ] ✅ API responses <500ms (95th percentile)
- [ ] ✅ Database queries optimized (no N+1)
- [ ] ✅ Frontend bundle size reasonable (<500KB gzipped)

### User Acceptance

- [ ] ✅ Can complete full onboarding flow
- [ ] ✅ Can track tax status over time
- [ ] ✅ Can track income from multiple sources
- [ ] ✅ Can track savings accounts
- [ ] ✅ Can view consolidated net worth
- [ ] ✅ ISA/TFSA allowances visible and accurate
- [ ] ✅ Emergency fund status clear
- [ ] ✅ All error messages clear and helpful

**Acceptance Criteria:**
🎯 **Phase 1 Complete**: Users can register, manage their profile, track tax status, record income, manage savings accounts, and view a consolidated dashboard showing their financial position.

🎯 **Foundation Solid**: All authentication, authorization, data management, and basic financial tracking working correctly.

🎯 **Ready for Phase 2**: Codebase clean, tested, documented, and ready to add Protection, Investment, and Tax Intelligence modules.

---

## Document Usage Summary

### For Each Task, Agents Must:

1. **Read ALL listed Context Files** before starting
2. **Follow specifications exactly** as written in context files
3. **Implement all tests** specified in the task
4. **Pass all tests** before marking task complete
5. **Reference shard files** for detailed requirements

### Example Agent Workflow:

```
Task: Implement User Registration Endpoint
Agent: python-backend-engineer

Step 1: Read context files
  - Read userAuth.md (Feature 1.1 section)
  - Read securityCompliance.md
  - Read performance.md

Step 2: Implement code following specs
  - Create endpoint as specified
  - Use Pydantic models from userAuth.md
  - Follow exact process flow

Step 3: Write tests
  - All test cases listed in task
  - Aim for 100% coverage

Step 4: Verify all tests pass
  - Run pytest
  - Fix any failures
  - Verify performance targets met

Step 5: Mark task complete
```

---

**Total Tasks Defined:** 150+ detailed tasks with ~500+ test cases
**Context Files:** 27 shard files referenced throughout
**Estimated Development Time (Phase 1-2):** 4-6 months with 2-3 developers
