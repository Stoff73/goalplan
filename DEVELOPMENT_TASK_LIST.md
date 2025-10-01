# Comprehensive Development Task List

## Dual-Country Financial Planning Platform

**Last Updated:** October 1, 2025
**Document Purpose:** Step-by-step development checklist with testing gates and agent delegation
**Critical Rule:** ⛔ **DO NOT PROCEED TO NEXT PHASE UNTIL ALL TESTS PASS** ⛔

---

## How to Use This Document

1. **Work sequentially** - Complete tasks in order within each phase
2. **Reference shard files** - Each task references the relevant shard(s) for detailed specs
3. **Delegate to agents** - Use specialized agents for Python backend and React frontend tasks
4. **Test continuously** - Run tests after each task, fix immediately
5. **Testing Gates** - Must pass 100% of tests before proceeding to next phase
6. **Check boxes** - Mark tasks complete only when all tests pass
7. **Maintain functionality** - App must remain functional throughout development

## Agent Delegation Rules

### 🐍 Python Backend Tasks

**MANDATORY:** All Python backend code MUST be delegated to `python-backend-engineer` agent

- API endpoint implementation
- Database models and migrations
- Business logic services
- Authentication and security
- Background jobs and async tasks
- Testing (pytest)

### ⚛️ React Frontend Tasks

**MANDATORY:** All React frontend code MUST be delegated to `react-coder` agent

- React components
- UI/UX implementation
- Forms and validation
- State management
- Routing
- Testing (Jest/Cypress)

---

# PHASE 0: PROJECT SETUP & FOUNDATION

## 0.1 Development Environment Setup

### Task 0.1.1: Initialize Project Structure

- [ ] Create repository with appropriate .gitignore
- [ ] Set up monorepo structure (frontend/backend/shared)
- [ ] Initialize package managers (npm/yarn for frontend, pip/uv for backend)
- [ ] Configure version control (Git with feature branch workflow)
- [ ] Set up development branch protection rules
- [ ] **Test:** Verify clean repository structure, all team members can clone

### Task 0.1.2: Configure Development Tools

- [ ] Set up linting (ESLint, Prettier for frontend)
- [ ] Configure backend linting/formatting (black, isort, mypy)
- [ ] Set up pre-commit hooks (lint, format, basic tests)
- [ ] Configure EditorConfig for consistency
- [ ] Set up CI/CD pipeline basics (GitHub Actions/GitLab CI)
- [ ] **Test:** Run lint on empty project structure, should pass with 0 errors

### Task 0.1.3: Database Setup

**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Choose database (PostgreSQL recommended for relational data)
- [ ] Set up local development database
- [ ] Configure database migrations system (Alembic)
- [ ] Create initial database connection config
- [ ] Set up Redis for caching and sessions
- [ ] **Test:** Connect to database successfully, run empty migration

### Task 0.1.4: Backend Framework Setup

**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Initialize backend framework (FastAPI recommended)
- [ ] Use `uv` for dependency management
- [ ] Configure environment variables (.env setup)
- [ ] Set up logging system
- [ ] Configure error handling middleware
- [ ] Set up health check endpoint (`/health`)
- [ ] **Test:** Start backend server, access health check endpoint, returns 200

### Task 0.1.5: Frontend Framework Setup

**⚛️ DELEGATE TO: `react-coder`**

- [ ] Initialize frontend framework (React 19)
- [ ] Set up routing system
- [ ] Configure state management (Context API or Zustand)
- [ ] Set up API client (axios/fetch wrapper)
- [ ] Configure environment-specific settings
- [ ] Import UI components from 'internal-packages/ui'
- [ ] **Test:** Start frontend dev server, see default page load without errors

### Task 0.1.6: Testing Infrastructure

- [ ] **Backend (🐍 DELEGATE):** Set up pytest framework
- [ ] **Frontend (⚛️ DELEGATE):** Set up Jest/Vitest
- [ ] Configure integration testing framework
- [ ] Set up E2E testing framework (Playwright/Cypress)
- [ ] Create test database seeding scripts
- [ ] Configure test coverage reporting (aim for >80%)
- [ ] **Test:** Run empty test suite, should pass (0 tests, 0 failures)

### Task 0.1.7: Documentation Setup

- [ ] Set up API documentation (Swagger/OpenAPI)
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

**Context Shards:** `userAuth.md`, `securityCompliance.md`, `Architecture.md`

## 1.1 User Authentication System

### Task 1.1.1: User Registration - Data Models

**Reference:** `userAuth.md` (Feature 1.1: User Registration, Data Models section)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (Technical Requirements: Argon2 hashing)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (Technical Requirements: SendGrid/AWS SES)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (Feature 1.1: Implementation Approach)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (API Endpoints: verify-email)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (Technical Requirements: Rate limiting, Error Handling)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (Feature 1.1: Complete flow)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (Feature 1.2: JWT with RS256, Data Models)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (Feature 1.2: Session management with Redis)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (Feature 1.2: Login flow, PROCESS section)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (Acceptance Criteria: Account lockout after 5 failed attempts)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (API Endpoints: /auth/refresh)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (API Endpoints: /auth/logout, /auth/logout-all)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (Technical Requirements: Session management)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (Feature 1.2: Data Models - user_2fa table)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (Technical Requirements: TOTP library)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (API Endpoints: /auth/enable-2fa)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (Feature 1.2: Login flow with 2FA)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (API Endpoints: /auth/disable-2fa)
**🐍 DELEGATE TO: `python-backend-engineer`**

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

**Reference:** `userAuth.md` (Feature 1.1: User Flow)
**⚛️ DELEGATE TO: `react-coder`**

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
- [ ] **Manual Test:**
  - Register new user successfully
  - Try duplicate email, see error
  - Enter weak password, see validation
  - See password strength indicator work
  - Submit form and see success message
- [ ] **E2E Test:** `cypress/e2e/registration.cy.js`
- [ ] **Acceptance:** Registration page works, all validations trigger

### Task 1.4.2: Email Verification Page

**Reference:** `userAuth.md` (Feature 1.1: User Flow)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create email verification landing page (simple, functional)
- [ ] Extract token from URL query parameter
- [ ] Call verification API on page load (avoid useEffect if possible)
- [ ] Show success message on verification
- [ ] Show error message if token invalid/expired
- [ ] Provide resend verification link
- [ ] Redirect to login after 3 seconds on success
- [ ] **Manual Test:**
  - Click verification link in email
  - See success message
  - Try expired token, see error
  - Test resend functionality
- [ ] **E2E Test:** `cypress/e2e/email-verification.cy.js`
- [ ] **Acceptance:** Email verification works end-to-end

### Task 1.4.3: Login Page

**Reference:** `userAuth.md` (Feature 1.2: User Flow)
**⚛️ DELEGATE TO: `react-coder`**

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
- [ ] **Manual Test:**
  - Login with valid credentials
  - Login with invalid credentials, see error
  - Login with unverified account, see error
  - Try 5 failed attempts, see lockout
- [ ] **E2E Test:** `cypress/e2e/login.cy.js`
- [ ] **Acceptance:** Login page works, all error cases handled

### Task 1.4.4: 2FA Setup Page

**Reference:** `userAuth.md` (Feature 1.2: 2FA setup)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create 2FA setup page (in settings or onboarding)
- [ ] Import necessary UI components
- [ ] Call enable-2FA API
- [ ] Display QR code for scanning
- [ ] Show text secret as fallback
- [ ] Provide input for verification code
- [ ] Call verify-2fa-setup API
- [ ] Show backup codes on success
- [ ] Force user to download/save backup codes
- [ ] **Manual Test:**
  - Scan QR with authenticator app
  - Enter code and verify
  - See backup codes
  - Download backup codes
- [ ] **E2E Test:** `cypress/e2e/2fa-setup.cy.js`
- [ ] **Acceptance:** Can setup 2FA successfully

### Task 1.4.5: Login with 2FA UI

**Reference:** `userAuth.md` (Feature 1.2: 2FA login flow)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Modify login page to handle 2FA flow
- [ ] Show TOTP input if requiresTwoFactor response
- [ ] Submit TOTP code
- [ ] Show "Use backup code" option
- [ ] Handle invalid code error
- [ ] **Manual Test:**
  - Login with 2FA enabled account
  - Enter TOTP code from app
  - Login successfully
  - Try invalid code, see error
  - Use backup code successfully
- [ ] **E2E Test:** `cypress/e2e/login-with-2fa.cy.js`
- [ ] **Acceptance:** 2FA login flow works

### Task 1.4.6: Logout Functionality

**Reference:** `userAuth.md` (API Endpoints: logout)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Add logout button to navigation (simple, clear)
- [ ] Call logout API
- [ ] Clear stored tokens
- [ ] Clear application state
- [ ] Redirect to login page
- [ ] Show logout confirmation message
- [ ] **Manual Test:**
  - Click logout
  - See confirmation
  - Redirect to login
  - Cannot access protected pages
- [ ] **E2E Test:** `cypress/e2e/logout.cy.js`
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

# PHASE 1 (continued): USER INFORMATION MODULE

**Context Shards:** `UserInfo.md`, `DataManagement.md`

## 1.5 User Profile Management

### Task 1.5.1: User Profile Data Models

**Reference:** `UserInfo.md` (Feature 2.1: Data Models)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create `user_tax_status` table (temporal data with SQLAlchemy)
- [ ] Create `uk_srt_data` table (Statutory Residence Test)
- [ ] Create `sa_presence_data` table (Physical Presence Test)
- [ ] Add appropriate indexes for temporal queries
- [ ] Create Pydantic models for all profile entities
- [ ] **Test Suite:**
  - Test tax status model with effective dates
  - Test temporal queries (status at specific date)
  - Test SRT data storage
  - Test SA presence data storage
  - Test overlapping period detection
- [ ] **Run:** `pytest tests/models/test_user_profile_models.py -v`
- [ ] **Acceptance:** Profile models tests pass

### Task 1.5.2: Tax Status Service

**Reference:** `UserInfo.md` (Feature 2.1: Business Logic - Calculate deemed domicile)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create tax status calculation service
- [ ] Implement deemed domicile calculation (UK: 15/20 years rule)
- [ ] Implement DTA tie-breaker logic
- [ ] Implement tax liability scope calculation
- [ ] Create helper functions for tax status queries
- [ ] Use type hints throughout
- [ ] **Test Suite:**
  - Test deemed domicile calculation (15/20 years)
  - Test domicile of origin rules
  - Test dual resident tie-breaker
  - Test remittance basis eligibility
  - Test UK tax liability scope (worldwide/remittance)
  - Test SA tax liability scope
- [ ] **Run:** `pytest tests/services/test_tax_status_service.py -v`
- [ ] **Acceptance:** Tax status calculations accurate

### Task 1.5.3: UK SRT Calculator

**Reference:** `UserInfo.md` (Feature 2.1: UK SRT calculator)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create SRT calculator service (clean, modular code)
- [ ] Implement automatic overseas tests
- [ ] Implement automatic UK tests
- [ ] Implement sufficient ties test
- [ ] Calculate days in UK
- [ ] Evaluate all 5 ties
- [ ] Return SRT result with explanation
- [ ] **Test Suite:**
  - Test automatic overseas test scenarios
  - Test automatic UK test scenarios
  - Test sufficient ties calculations
  - Test all tie combinations
  - Test edge cases (exactly 183 days, etc.)
  - Test split year treatment indication
- [ ] **Run:** `pytest tests/services/test_srt_calculator.py -v`
- [ ] **Acceptance:** SRT calculator matches HMRC guidance

### Task 1.5.4: SA Physical Presence Test

**Reference:** `UserInfo.md` (Feature 2.1: SA presence test)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create SA presence test calculator
- [ ] Implement 91 days current year test
- [ ] Implement 91 days average over 5 years test
- [ ] Implement ordinarily resident logic
- [ ] **Test Suite:**
  - Test 91 days in current year
  - Test average days calculation
  - Test ordinarily resident determination
  - Test edge cases
- [ ] **Run:** `pytest tests/services/test_sa_presence_test.py -v`
- [ ] **Acceptance:** SA presence test accurate

### Task 1.5.5: Tax Status API Endpoints

**Reference:** `UserInfo.md` (Feature 2.1: API Endpoints)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create `POST /api/v1/user/tax-status` endpoint (FastAPI)
- [ ] Create `GET /api/v1/user/tax-status` endpoint (current)
- [ ] Create `GET /api/v1/user/tax-status/history` endpoint
- [ ] Create `GET /api/v1/user/tax-status/at-date?date={date}` endpoint
- [ ] Create `POST /api/v1/user/tax-status/srt-calculator` endpoint
- [ ] Create `POST /api/v1/user/tax-status/sa-presence-test` endpoint
- [ ] Implement request validation with Pydantic
- [ ] Implement business logic calls
- [ ] Handle overlapping periods
- [ ] Trigger recalculations across modules when tax status changes
- [ ] **Test Suite:**
  - Test create tax status
  - Test get current status
  - Test get historical status
  - Test status at specific date
  - Test SRT calculator endpoint
  - Test SA presence test endpoint
  - Test effective date validation
  - Test overlapping period handling
- [ ] **Run:** `pytest tests/api/user/test_tax_status.py -v`
- [ ] **Acceptance:** Tax status API works correctly

---

## 1.6 Income Information Management

### Task 1.6.1: Income Data Models

**Reference:** `UserInfo.md` (Feature 2.2: Data Models)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create `user_income` table with all fields (SQLAlchemy)
- [ ] Create `income_tax_treatment` table
- [ ] Create `exchange_rates` table
- [ ] Add appropriate indexes
- [ ] Create Pydantic models for income entities
- [ ] **Test Suite:**
  - Test income model creation
  - Test currency fields
  - Test tax year allocation
  - Test soft delete
- [ ] **Run:** `pytest tests/models/test_income_models.py -v`
- [ ] **Acceptance:** Income models tests pass

### Task 1.6.2: Currency Exchange Service

**Reference:** `UserInfo.md` (Feature 2.2: Currency conversion)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Integrate with currency exchange API (e.g., exchangerate-api.io)
- [ ] Create exchange rate service
- [ ] Implement rate fetching and caching (Redis)
- [ ] Store historical rates in database
- [ ] Create conversion functions (GBP <-> ZAR)
- [ ] Implement proper error handling
- [ ] **Test Suite:**
  - Test rate fetching
  - Test rate caching (1 day TTL)
  - Test historical rate retrieval
  - Test currency conversion calculations
  - Mock API for deterministic tests
- [ ] **Run:** `pytest tests/services/test_currency_service.py -v`
- [ ] **Acceptance:** Currency service works, rates cached

### Task 1.6.3: Income Tax Treatment Service

**Reference:** `UserInfo.md` (Feature 2.2: Business Logic - calculate_tax_treatment)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create income tax treatment calculator
- [ ] Implement UK tax treatment logic
- [ ] Implement SA tax treatment logic
- [ ] Apply DTA relief calculation
- [ ] Calculate effective tax rate
- [ ] **Test Suite:**
  - Test UK-source income taxed in UK
  - Test SA-source income taxed in SA
  - Test foreign income with arising basis
  - Test foreign income with remittance basis
  - Test DTA relief application
  - Test dual taxation scenarios
- [ ] **Run:** `pytest tests/services/test_income_tax_treatment.py -v`
- [ ] **Acceptance:** Income tax treatment accurate

### Task 1.6.4: Income API Endpoints

**Reference:** `UserInfo.md` (Feature 2.2: API Endpoints)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create `POST /api/v1/user/income` endpoint
- [ ] Create `PUT /api/v1/user/income/{id}` endpoint
- [ ] Create `DELETE /api/v1/user/income/{id}` endpoint (soft delete)
- [ ] Create `GET /api/v1/user/income` endpoint (list)
- [ ] Create `GET /api/v1/user/income/summary` endpoint
- [ ] Create `GET /api/v1/user/income/tax-year/{taxYear}` endpoint
- [ ] Implement validation (income type, currency, amounts)
- [ ] Calculate tax treatment on save
- [ ] Convert to GBP and ZAR
- [ ] Prevent modification of locked tax years
- [ ] **Test Suite:**
  - Test create income
  - Test update income
  - Test delete income (soft delete)
  - Test list income
  - Test summary calculation
  - Test tax year filtering
  - Test currency conversion applied
  - Test tax treatment calculated
  - Test locked tax year rejection
- [ ] **Run:** `pytest tests/api/user/test_income.py -v`
- [ ] **Acceptance:** Income API works correctly

---

## 1.7 Frontend: User Profile UI

### Task 1.7.1: Profile Setup Wizard

**Reference:** `UserInfo.md` (User Flow - step-by-step onboarding)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create multi-step profile wizard component (React 19)
- [ ] Use UI components from 'internal-packages/ui'
- [ ] Step 1: Basic Information (name, DOB, family)
- [ ] Step 2: Tax Status (domicile, residency)
- [ ] Step 3: Income Sources (summary level)
- [ ] Progress indicator
- [ ] Form validation on each step
- [ ] Save draft capability
- [ ] Keep component structure simple and obvious
- [ ] **Manual Test:**
  - Complete wizard end-to-end
  - Navigate back and forth
  - See data persisted
  - Validation works on each step
- [ ] **E2E Test:** `cypress/e2e/profile-setup.cy.js`
- [ ] **Acceptance:** Wizard guides user through profile setup

### Task 1.7.2: Tax Status Page

**Reference:** `UserInfo.md` (Feature 2.1: User Flow - Tax Status Form)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create tax status management page
- [ ] Import UI components from 'internal-packages/ui'
- [ ] Effective date selector
- [ ] Tax residency toggles (UK/SA)
- [ ] Domicile dropdowns
- [ ] Years of residency inputs
- [ ] Remittance basis selector (if applicable)
- [ ] Show calculated status (deemed domicile, tax liability)
- [ ] Connect to tax status API
- [ ] Show historical changes
- [ ] **Manual Test:**
  - Enter tax status
  - See calculated results
  - Change effective date
  - View history
- [ ] **E2E Test:** `cypress/e2e/tax-status.cy.js`
- [ ] **Acceptance:** Tax status page functional

### Task 1.7.3: SRT Calculator Tool

**Reference:** `UserInfo.md` (Feature 2.1: SRT calculator)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create SRT calculator modal/page (simple design)
- [ ] Input: Days in UK
- [ ] Input: Each of 5 ties (checkboxes with explanations)
- [ ] Call SRT calculator API
- [ ] Show result (UK Resident / Non-Resident)
- [ ] Show explanation of result
- [ ] Option to save result to profile
- [ ] **Manual Test:**
  - Enter various scenarios
  - See correct results
  - Save to profile
- [ ] **E2E Test:** `cypress/e2e/srt-calculator.cy.js`
- [ ] **Acceptance:** SRT calculator works and is user-friendly

### Task 1.7.4: SA Presence Test Tool

**Reference:** `UserInfo.md` (Feature 2.1: SA presence test)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create SA presence test calculator
- [ ] Input: Days in SA current year
- [ ] Input: Days for previous 5 years
- [ ] Call SA presence test API
- [ ] Show result (Resident / Non-Resident)
- [ ] Show average days calculation
- [ ] Option to save result to profile
- [ ] **Manual Test:**
  - Enter days data
  - See result
  - Save to profile
- [ ] **E2E Test:** `cypress/e2e/sa-presence-test.cy.js`
- [ ] **Acceptance:** SA presence test works

### Task 1.7.5: Income Management Page

**Reference:** `UserInfo.md` (Feature 2.2: User Flow - Income Entry Form)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create income list page (simple, functional layout)
- [ ] Display all income sources
- [ ] Group by type
- [ ] Show totals
- [ ] Add income button → opens form
- [ ] Income entry form (3 steps):
  - Step 1: Type selection
  - Step 2: Details (amount, currency, frequency)
  - Step 3: Tax details (PAYE, withholding)
- [ ] Show tax treatment preview
- [ ] Edit and delete functionality
- [ ] **Manual Test:**
  - Add employment income
  - Add self-employment income
  - Add dividend income
  - See tax treatment calculated
  - Edit income
  - Delete income
- [ ] **E2E Test:** `cypress/e2e/income-management.cy.js`
- [ ] **Acceptance:** Income management fully functional

---

## 🚦 PHASE 1 PROFILE TESTING GATE

### Data Integrity Tests

- [ ] ✅ Tax status temporal queries work correctly
- [ ] ✅ Income tax treatment calculations accurate
- [ ] ✅ Currency conversions correct
- [ ] ✅ Historical data preserved
- [ ] ✅ Overlapping periods prevented

### Business Logic Tests

- [ ] ✅ Deemed domicile calculation matches UK rules
- [ ] ✅ SRT calculator matches HMRC guidance (test with examples)
- [ ] ✅ SA presence test matches SARS rules
- [ ] ✅ DTA tie-breaker logic correct
- [ ] ✅ Tax liability scope calculated correctly

### Integration Tests

- [ ] ✅ Tax status change triggers recalculations
- [ ] ✅ Income addition updates totals
- [ ] ✅ Profile data flows to other modules
- [ ] ✅ Currency conversion real-time or cached appropriately

### User Experience Tests

- [ ] ✅ Profile wizard intuitive and complete
- [ ] ✅ Tax calculators work and explain results
- [ ] ✅ Income management easy to use
- [ ] ✅ Data persists correctly

### Performance Tests

- [ ] ✅ Profile page loads < 1 second
- [ ] ✅ Tax calculations < 200ms
- [ ] ✅ Currency conversions cached, fast

**Acceptance Criteria:**
🎯 Users can fully configure profile, tax status, and income.
🎯 Tax calculations are accurate and auditable.
🎯 Foundation ready for financial modules.

---

# PHASE 1 (continued): CENTRAL DASHBOARD (BASIC)

**Context Shards:** `CentralDashboard.md`, `performance.md`

## 1.8 Basic Dashboard

### Task 1.8.1: Dashboard Data Models

**Reference:** `CentralDashboard.md` (Feature 3.1: Data Models)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create `net_worth_snapshots` table (SQLAlchemy)
- [ ] Create `net_worth_by_category` table
- [ ] Create `dashboard_cache` table
- [ ] Create materialized view `v_user_net_worth_current`
- [ ] Add appropriate indexes
- [ ] **Test Suite:**
  - Test snapshot creation
  - Test category breakdown storage
  - Test materialized view refresh
- [ ] **Run:** `pytest tests/models/test_dashboard_models.py -v`
- [ ] **Acceptance:** Dashboard models tests pass

### Task 1.8.2: Net Worth Aggregation Service (Basic)

**Reference:** `CentralDashboard.md` (Feature 3.1: Business Logic)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create net worth calculation service
- [ ] For now, just aggregate cash from savings (Phase 1)
- [ ] Implement currency conversion to base currency
- [ ] Calculate total assets (cash only for now)
- [ ] Calculate total liabilities (if any loans entered)
- [ ] Calculate net worth
- [ ] Store snapshot
- [ ] **Test Suite:**
  - Test net worth calculation
  - Test currency conversion
  - Test snapshot creation
  - Test with no data (new user)
- [ ] **Run:** `pytest tests/services/test_net_worth_service.py -v`
- [ ] **Acceptance:** Basic net worth calculation works

### Task 1.8.3: Dashboard API Endpoint

**Reference:** `CentralDashboard.md` (Feature 3.1: API Endpoints)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create `GET /api/v1/dashboard/net-worth` endpoint (FastAPI)
- [ ] Accept `baseCurrency` query param (default GBP)
- [ ] Accept `asOfDate` query param (default today)
- [ ] Return net worth summary
- [ ] Return breakdown by currency
- [ ] Implement caching (5 minutes in Redis)
- [ ] **Test Suite:**
  - Test dashboard data retrieval
  - Test base currency conversion
  - Test caching works
  - Test with no data returns zeros
- [ ] **Run:** `pytest tests/api/dashboard/test_dashboard.py -v`
- [ ] **Acceptance:** Dashboard API works

### Task 1.8.4: Dashboard Frontend

**Reference:** `CentralDashboard.md` (Feature 3.1: User Flow)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create dashboard page (landing after login)
- [ ] Use UI components from 'internal-packages/ui'
- [ ] Hero section: Total net worth display
- [ ] Currency selector (GBP/ZAR)
- [ ] Change indicator (if historical data available)
- [ ] Quick module access cards (placeholders for now)
- [ ] Refresh button
- [ ] Last updated timestamp
- [ ] Empty state for new users (call-to-action)
- [ ] Keep design simple and focused
- [ ] **Manual Test:**
  - Login and see dashboard
  - See net worth (if data entered)
  - Change currency
  - Refresh data
  - New user sees empty state
- [ ] **E2E Test:** `cypress/e2e/dashboard.cy.js`
- [ ] **Acceptance:** Dashboard displays correctly

---

## 🚦 PHASE 1 COMPLETE - FINAL GATE

### Comprehensive Integration Tests

- [ ] ✅ Full user journey: Register → Verify → Login → Setup Profile → See Dashboard
- [ ] ✅ 2FA user journey
- [ ] ✅ Tax status affects calculations
- [ ] ✅ Income appears in dashboard totals
- [ ] ✅ All pages accessible and functional

### Performance Tests

- [ ] ✅ Dashboard loads < 1 second
- [ ] ✅ Profile pages load < 500ms
- [ ] ✅ API response times meet targets
- [ ] ✅ Database queries optimized (explain plans checked)

### Security Audit

- [ ] ✅ Authentication cannot be bypassed
- [ ] ✅ Users can only access own data (authorization checks)
- [ ] ✅ SQL injection tests pass
- [ ] ✅ XSS tests pass
- [ ] ✅ CSRF protection enabled
- [ ] ✅ Security headers configured (CSP, HSTS, etc.)

### Code Quality

- [ ] ✅ Test coverage >80% overall
- [ ] ✅ No critical security vulnerabilities (npm audit / safety)
- [ ] ✅ Linting passes
- [ ] ✅ Code reviewed and approved
- [ ] ✅ API documentation complete
- [ ] ✅ User documentation complete

### Deployment Readiness

- [ ] ✅ Environment variables documented
- [ ] ✅ Database migrations tested
- [ ] ✅ Deployment scripts created
- [ ] ✅ Monitoring and logging configured
- [ ] ✅ Backup strategy defined

**PHASE 1 ACCEPTANCE:**
✅ **Foundation complete and production-ready**
✅ **Users can register, login, set up profile, and see basic dashboard**
✅ **All security measures implemented and tested**
✅ **System is stable and performant**

---

# PHASE 2: CORE MODULES - SAVINGS MODULE

**Context Shards:** `Savings.md`, `DataManagement.md`, `reporting.md`

## 2.1 Savings Account Management

### Task 2.1.1: Savings Account Data Models

**Reference:** `Savings.md` (Feature 5.1: Data Models)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create `savings_accounts` table with all fields (SQLAlchemy)
- [ ] Create `account_balance_history` table (temporal tracking)
- [ ] Create `interest_payments` table
- [ ] Create `isa_contributions` table (UK)
- [ ] Create `tfsa_contributions` table (SA)
- [ ] Create `emergency_fund_settings` table
- [ ] Add appropriate indexes
- [ ] Create Pydantic models for all savings entities
- [ ] **Test Suite:**
  - Test savings account model creation
  - Test balance history tracking
  - Test interest payment recording
  - Test ISA contribution tracking
  - Test TFSA contribution tracking
  - Test emergency fund settings
- [ ] **Run:** `pytest tests/models/test_savings_models.py -v`
- [ ] **Acceptance:** Savings models tests pass

### Task 2.1.2: Interest Calculation Service

**Reference:** `Savings.md` (Feature 5.1: Business Logic - Calculate projected interest)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create interest calculation service
- [ ] Implement simple interest calculation
- [ ] Implement compound interest calculation (monthly, quarterly, annually)
- [ ] Project annual interest earnings
- [ ] Calculate tax on interest (PSA for UK, exemption for SA)
- [ ] **Test Suite:**
  - Test simple interest calculation
  - Test compound interest (monthly compounding)
  - Test annual projection
  - Test UK PSA application (£1000 basic, £500 higher, £0 additional)
  - Test SA interest exemption (R23,800 under 65, R34,500 65+)
- [ ] **Run:** `pytest tests/services/test_interest_calculation.py -v`
- [ ] **Acceptance:** Interest calculations accurate

### Task 2.1.3: ISA/TFSA Allowance Tracker

**Reference:** `Savings.md` (Feature 5.2: ISA and TFSA Allowance Tracking)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create ISA allowance tracking service
- [ ] Track annual ISA allowance (£20,000 for 2024/25)
- [ ] Track TFSA annual allowance (R36,000)
- [ ] Track TFSA lifetime limit (R500,000)
- [ ] Calculate remaining allowances
- [ ] Validate contributions against limits
- [ ] **Test Suite:**
  - Test ISA allowance calculation for tax year
  - Test TFSA annual allowance tracking
  - Test TFSA lifetime limit enforcement
  - Test contribution validation
  - Test exceeding allowance rejection
- [ ] **Run:** `pytest tests/services/test_isa_tfsa_allowance.py -v`
- [ ] **Acceptance:** Allowance tracking accurate

### Task 2.1.4: Emergency Fund Assessment

**Reference:** `Savings.md` (Feature 5.1: Emergency fund assessment)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create emergency fund assessment service
- [ ] Calculate recommended emergency fund (monthly expenses × 3-6 months)
- [ ] Aggregate current emergency fund accounts
- [ ] Calculate adequacy percentage
- [ ] Recommend currency allocation
- [ ] **Test Suite:**
  - Test emergency fund calculation (3 months, 6 months)
  - Test current fund aggregation
  - Test adequacy percentage
  - Test currency allocation recommendations
- [ ] **Run:** `pytest tests/services/test_emergency_fund.py -v`
- [ ] **Acceptance:** Emergency fund assessment works

### Task 2.1.5: Savings Account API Endpoints

**Reference:** `Savings.md` (Feature 5.1: API Endpoints)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create `POST /api/v1/savings/accounts` endpoint (FastAPI)
- [ ] Create `PUT /api/v1/savings/accounts/{id}` endpoint
- [ ] Create `DELETE /api/v1/savings/accounts/{id}` endpoint (soft delete)
- [ ] Create `GET /api/v1/savings/accounts` endpoint (list)
- [ ] Create `GET /api/v1/savings/accounts/{id}` endpoint
- [ ] Create `POST /api/v1/savings/accounts/{id}/update-balance` endpoint
- [ ] Create `GET /api/v1/savings/accounts/{id}/balance-history` endpoint
- [ ] Create `GET /api/v1/savings/summary` endpoint
- [ ] Create `GET /api/v1/savings/emergency-fund-status` endpoint
- [ ] Implement request validation with Pydantic
- [ ] Calculate tax treatment on save
- [ ] Convert to GBP and ZAR
- [ ] Track ISA/TFSA contributions
- [ ] Limit balance updates (max 10 per day)
- [ ] **Test Suite:**
  - Test create account
  - Test update account
  - Test delete account (soft delete)
  - Test list accounts
  - Test get account details
  - Test update balance
  - Test balance history retrieval
  - Test savings summary
  - Test emergency fund status
  - Test ISA contribution validation
  - Test TFSA contribution validation
  - Test rate limiting on balance updates
- [ ] **Run:** `pytest tests/api/savings/test_savings_accounts.py -v`
- [ ] **Acceptance:** Savings API works correctly

---

## 2.2 Frontend: Savings UI

### Task 2.2.1: Savings Dashboard

**Reference:** `Savings.md` (User Flow - Savings Dashboard)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create savings dashboard page (React 19)
- [ ] Use UI components from 'internal-packages/ui'
- [ ] Display total savings (prominent)
- [ ] Show breakdown by currency
- [ ] Show breakdown by account type
- [ ] Emergency fund status indicator (progress bar)
- [ ] Quick add account button
- [ ] Account list with key details
- [ ] **Manual Test:**
  - View savings dashboard
  - See total savings
  - See currency breakdown
  - See emergency fund status
- [ ] **E2E Test:** `cypress/e2e/savings-dashboard.cy.js`
- [ ] **Acceptance:** Savings dashboard displays correctly

### Task 2.2.2: Add/Edit Account Form

**Reference:** `Savings.md` (User Flow - Account Entry Form)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create account entry form (multi-step, simple design)
- [ ] Step 1: Bank Details (bank name, country, account type)
- [ ] Step 2: Balance & Interest (balance, currency, interest rate, frequency)
- [ ] Step 3: Purpose & Dates (account purpose, open date, maturity date)
- [ ] Show tax treatment preview
- [ ] Show ISA/TFSA allowance impact
- [ ] Connect to savings API
- [ ] Handle validation errors
- [ ] **Manual Test:**
  - Add Cash ISA account
  - Add TFSA account
  - See allowance tracking
  - See tax treatment
  - Edit account
  - Delete account
- [ ] **E2E Test:** `cypress/e2e/savings-account-management.cy.js`
- [ ] **Acceptance:** Account form works, validation triggers

### Task 2.2.3: ISA/TFSA Allowance Tracker UI

**Reference:** `Savings.md` (Feature 5.2: User Flow)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create ISA allowance tracker component
- [ ] Show annual allowance (£20,000)
- [ ] Show used amount
- [ ] Show remaining amount
- [ ] Visual progress bar
- [ ] Warning when approaching limit (80%, 95%)
- [ ] Create TFSA allowance tracker component
- [ ] Show annual and lifetime allowances
- [ ] **Manual Test:**
  - Add ISA contribution
  - See allowance update
  - Add TFSA contribution
  - See lifetime limit tracking
  - Try exceeding limit, see error
- [ ] **E2E Test:** `cypress/e2e/isa-tfsa-allowance.cy.js`
- [ ] **Acceptance:** Allowance trackers work correctly

### Task 2.2.4: Emergency Fund Widget

**Reference:** `Savings.md` (Feature 5.1: Emergency fund adequacy assessment)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create emergency fund widget (dashboard component)
- [ ] Display target amount
- [ ] Display current amount
- [ ] Display adequacy percentage
- [ ] Color-coded status (red < 50%, yellow 50-80%, green > 80%)
- [ ] Recommendations for improvement
- [ ] **Manual Test:**
  - Set monthly expenses
  - See recommended emergency fund
  - Add emergency fund accounts
  - See adequacy percentage update
- [ ] **E2E Test:** `cypress/e2e/emergency-fund.cy.js`
- [ ] **Acceptance:** Emergency fund widget functional

---

## 🚦 PHASE 2 SAVINGS TESTING GATE

### Functional Tests

- [ ] ✅ Can add, edit, delete savings accounts
- [ ] ✅ Balance history tracked correctly
- [ ] ✅ Interest calculations accurate
- [ ] ✅ ISA allowance tracking works (£20,000 limit)
- [ ] ✅ TFSA allowance tracking works (annual + lifetime)
- [ ] ✅ Emergency fund assessment accurate
- [ ] ✅ Tax treatment calculated correctly (PSA, SA exemption)

### Integration Tests

- [ ] ✅ Savings totals appear in dashboard
- [ ] ✅ Currency conversion applied
- [ ] ✅ Interest income flows to tax calculations
- [ ] ✅ ISA/TFSA limits enforced

### Performance Tests

- [ ] ✅ Savings dashboard loads < 1 second
- [ ] ✅ Account list with 20+ accounts loads < 500ms

**Acceptance Criteria:**
🎯 Users can manage all savings accounts with tax-efficient tracking.
🎯 ISA and TFSA allowances properly monitored.
🎯 Emergency fund adequacy assessed.

---

# PHASE 2 (continued): PROTECTION MODULE

**Context Shards:** `Protection.md`

## 2.3 Life Assurance Policy Management

### Task 2.3.1: Life Assurance Data Models

**Reference:** `Protection.md` (Feature 4.1: Data Models)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create `life_assurance_policies` table (SQLAlchemy)
- [ ] Create `policy_beneficiaries` table
- [ ] Create `policy_trustees` table (for trust policies)
- [ ] Create `coverage_needs_analysis` table
- [ ] Create `premium_reminders` table
- [ ] Add appropriate indexes
- [ ] Create Pydantic models
- [ ] Add constraint: beneficiary percentages must total 100%
- [ ] **Test Suite:**
  - Test policy model creation
  - Test beneficiary relationship
  - Test trustee relationship
  - Test beneficiary percentage constraint
  - Test coverage needs model
- [ ] **Run:** `pytest tests/models/test_protection_models.py -v`
- [ ] **Acceptance:** Protection models tests pass

### Task 2.3.2: Coverage Needs Analysis Service

**Reference:** `Protection.md` (Feature 4.1: Business Logic - Calculate recommended cover)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create coverage needs analysis service
- [ ] Implement family needs calculation:
  - (Annual income × multiplier) + outstanding debts + (children × education cost) + funeral costs - existing assets
- [ ] Calculate coverage gap (recommended - current)
- [ ] Recommend policy structures
- [ ] **Test Suite:**
  - Test coverage calculation with dependents
  - Test coverage calculation without dependents
  - Test coverage gap calculation
  - Test recommendations
- [ ] **Run:** `pytest tests/services/test_coverage_needs.py -v`
- [ ] **Acceptance:** Coverage needs analysis accurate

### Task 2.3.3: Policy Tax Treatment Service

**Reference:** `Protection.md` (Feature 4.1: Business Logic - Determine tax treatment)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create policy tax treatment calculator
- [ ] UK: Determine if written in trust (outside estate)
- [ ] UK: Calculate IHT impact if not in trust
- [ ] SA: Calculate estate duty impact
- [ ] **Test Suite:**
  - Test UK trust policy (outside estate)
  - Test UK non-trust policy (in estate)
  - Test SA policy estate duty treatment
- [ ] **Run:** `pytest tests/services/test_policy_tax_treatment.py -v`
- [ ] **Acceptance:** Tax treatment calculations correct

### Task 2.3.4: Life Assurance API Endpoints

**Reference:** `Protection.md` (Feature 4.1: API Endpoints)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create `POST /api/v1/protection/life-assurance` endpoint
- [ ] Create `PUT /api/v1/protection/life-assurance/{id}` endpoint
- [ ] Create `DELETE /api/v1/protection/life-assurance/{id}` endpoint
- [ ] Create `GET /api/v1/protection/life-assurance` endpoint (list)
- [ ] Create `GET /api/v1/protection/life-assurance/{id}` endpoint
- [ ] Create `POST /api/v1/protection/life-assurance/coverage-analysis` endpoint
- [ ] Create `POST /api/v1/protection/life-assurance/{id}/upload-document` endpoint
- [ ] Validate beneficiary percentages total 100%
- [ ] Calculate tax treatment on save
- [ ] Link to IHT module if not in trust
- [ ] **Test Suite:**
  - Test create policy
  - Test beneficiary validation
  - Test tax treatment calculation
  - Test coverage analysis
  - Test document upload
  - Test policy listing
- [ ] **Run:** `pytest tests/api/protection/test_life_assurance.py -v`
- [ ] **Acceptance:** Protection API works correctly

---

## 2.4 Frontend: Protection UI

### Task 2.4.1: Protection Dashboard

**Reference:** `Protection.md` (User Flow)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create protection dashboard (React 19)
- [ ] Use UI components from 'internal-packages/ui'
- [ ] Display total cover amount
- [ ] Show coverage gap (if exists)
- [ ] List all policies
- [ ] Coverage analysis widget
- [ ] Add policy button
- [ ] **Manual Test:**
  - View protection dashboard
  - See total cover
  - See coverage gap indicator
- [ ] **E2E Test:** `cypress/e2e/protection-dashboard.cy.js`
- [ ] **Acceptance:** Protection dashboard displays correctly

### Task 2.4.2: Add/Edit Policy Form

**Reference:** `Protection.md` (User Flow - Policy Entry Form)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create policy entry form (4-step wizard)
- [ ] Step 1: Provider Details (policy number, provider, type)
- [ ] Step 2: Cover Details (amount, premium, dates, riders)
- [ ] Step 3: Beneficiaries (add multiple, percentages must total 100%)
- [ ] Step 4: Upload Document (optional)
- [ ] Show coverage analysis after save
- [ ] Beneficiary validation (total = 100%)
- [ ] **Manual Test:**
  - Add term life policy
  - Add beneficiaries
  - See validation if percentages != 100%
  - Upload policy document
  - See coverage analysis
- [ ] **E2E Test:** `cypress/e2e/life-assurance-policy.cy.js`
- [ ] **Acceptance:** Policy form works, validation triggers

### Task 2.4.3: Coverage Needs Analysis UI

**Reference:** `Protection.md` (Feature 4.1: Coverage gap analysis)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create coverage needs analysis tool
- [ ] Input: Annual income, dependents, debts, education costs
- [ ] Calculate recommended cover
- [ ] Show current cover
- [ ] Show gap (visual indicator)
- [ ] Recommendations for closing gap
- [ ] **Manual Test:**
  - Enter family details
  - See recommended cover
  - See coverage gap
  - See recommendations
- [ ] **E2E Test:** `cypress/e2e/coverage-needs-analysis.cy.js`
- [ ] **Acceptance:** Coverage analysis tool works

---

## 🚦 PHASE 2 PROTECTION TESTING GATE

### Functional Tests

- [ ] ✅ Can add, edit, delete life assurance policies
- [ ] ✅ Beneficiary percentages validated (must total 100%)
- [ ] ✅ Coverage needs analysis accurate
- [ ] ✅ Coverage gap calculated correctly
- [ ] ✅ Tax treatment determined (UK trust, SA estate duty)

### Integration Tests

- [ ] ✅ Policies linked to IHT module if not in trust
- [ ] ✅ Total cover displayed in dashboard

**Acceptance Criteria:**
🎯 Users can manage all protection policies with beneficiaries.
🎯 Coverage gap identified and recommendations provided.

---

# PHASE 2 (continued): INVESTMENT MODULE (BASIC)

**Context Shards:** `Investment.md`

## 2.5 Portfolio Management (Basic)

### Task 2.5.1: Investment Data Models

**Reference:** `Investment.md` (Feature 6.1: Data Models - implied)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create `investment_accounts` table (ISA, GIA, TFSA, etc.)
- [ ] Create `investment_holdings` table
- [ ] Create `investment_transactions` table
- [ ] Create `tax_lots` table (for CGT tracking)
- [ ] Create `dividend_payments` table
- [ ] Add appropriate indexes
- [ ] Create Pydantic models
- [ ] **Test Suite:**
  - Test account model
  - Test holding model
  - Test transaction model
  - Test tax lot tracking
  - Test dividend payment recording
- [ ] **Run:** `pytest tests/models/test_investment_models.py -v`
- [ ] **Acceptance:** Investment models tests pass

### Task 2.5.2: Portfolio Valuation Service

**Reference:** `Investment.md` (Feature 6.1: Business Logic - Calculate metrics)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create portfolio valuation service
- [ ] Fetch current prices (integrate with market data API)
- [ ] Calculate total portfolio value
- [ ] Calculate unrealized gains/losses
- [ ] Calculate asset allocation by class, geography, currency
- [ ] **Test Suite:**
  - Test portfolio valuation
  - Test unrealized gain/loss calculation
  - Test asset allocation calculation
  - Mock market data API
- [ ] **Run:** `pytest tests/services/test_portfolio_valuation.py -v`
- [ ] **Acceptance:** Portfolio valuation accurate

### Task 2.5.3: Tax Lot Tracking Service (CGT)

**Reference:** `Investment.md` (Feature 6.1: Tax lot tracking for CGT)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create tax lot tracking service
- [ ] Implement FIFO (First In, First Out) for UK
- [ ] Implement same-day and bed & breakfast rules (UK)
- [ ] Calculate capital gains on disposal
- [ ] Track UK CGT annual exemption usage (£3,000)
- [ ] Calculate SA CGT (inclusion rate method)
- [ ] **Test Suite:**
  - Test FIFO allocation
  - Test same-day rule
  - Test bed & breakfast rule (30 days)
  - Test UK CGT calculation
  - Test SA CGT calculation
  - Test annual exemption tracking
- [ ] **Run:** `pytest tests/services/test_tax_lot_tracking.py -v`
- [ ] **Acceptance:** Tax lot tracking accurate

### Task 2.5.4: Investment API Endpoints (Basic)

**Reference:** `Investment.md` (Feature 6.1: API Endpoints - implied)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create `POST /api/v1/investments/accounts` endpoint
- [ ] Create `POST /api/v1/investments/holdings` endpoint (add holding)
- [ ] Create `POST /api/v1/investments/transactions` endpoint (buy/sell)
- [ ] Create `GET /api/v1/investments/portfolio/summary` endpoint
- [ ] Create `GET /api/v1/investments/cgt-position` endpoint
- [ ] Validate ISA subscriptions against allowance
- [ ] Calculate tax lots on sell transactions
- [ ] **Test Suite:**
  - Test create account
  - Test add holding
  - Test buy transaction
  - Test sell transaction (with CGT calculation)
  - Test portfolio summary
  - Test CGT position report
- [ ] **Run:** `pytest tests/api/investments/test_investments.py -v`
- [ ] **Acceptance:** Investment API works

---

## 2.6 Frontend: Investment UI (Basic)

### Task 2.6.1: Investment Dashboard

**Reference:** `Investment.md` (User Flow - implied)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create investment dashboard (React 19)
- [ ] Display total portfolio value
- [ ] Show asset allocation pie chart
- [ ] Show holdings list
- [ ] Show unrealized gains/losses
- [ ] Add holding button
- [ ] **Manual Test:**
  - View investment dashboard
  - See portfolio value
  - See asset allocation
  - See holdings
- [ ] **E2E Test:** `cypress/e2e/investment-dashboard.cy.js`
- [ ] **Acceptance:** Investment dashboard displays

### Task 2.6.2: Add Investment Form

**Reference:** `Investment.md` (User Flow - implied)
**⚛️ DELEGATE TO: `react-coder`**

- [ ] Create add investment form
- [ ] Select account type (ISA, GIA, TFSA, etc.)
- [ ] Enter holding details (ticker, quantity, price)
- [ ] Transaction type (buy/sell)
- [ ] Show ISA allowance impact if ISA
- [ ] Connect to investment API
- [ ] **Manual Test:**
  - Add holding to ISA
  - Add holding to GIA
  - See ISA allowance update
  - Sell holding, see CGT calculation
- [ ] **E2E Test:** `cypress/e2e/add-investment.cy.js`
- [ ] **Acceptance:** Add investment form works

---

## 🚦 PHASE 2 INVESTMENT TESTING GATE

### Functional Tests

- [ ] ✅ Can add investment accounts and holdings
- [ ] ✅ Portfolio valuation accurate
- [ ] ✅ Buy/sell transactions processed correctly
- [ ] ✅ Tax lot tracking works (FIFO, same-day, B&B rules)
- [ ] ✅ CGT calculations accurate (UK and SA)
- [ ] ✅ ISA allowance tracked

### Integration Tests

- [ ] ✅ Portfolio value in dashboard
- [ ] ✅ CGT gains flow to tax calculations

**Acceptance Criteria:**
🎯 Users can manage basic investment portfolio.
🎯 Tax lot tracking and CGT calculations accurate.

---

# PHASE 2 (continued): TAX INTELLIGENCE ENGINE (BASIC)

**Context Shards:** `CoreTaxCalcs.md`

## 2.7 Core Tax Calculations (UK & SA)

### Task 2.7.1: Tax Configuration Data Models

**Reference:** `CoreTaxCalcs.md` (Feature 9.1: Tax configuration versioning)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create `tax_configurations` table (versioned by tax year)
- [ ] Create `tax_rates` table (bands and rates)
- [ ] Create `tax_allowances` table (personal allowance, PSA, etc.)
- [ ] Seed with UK 2024/25 tax data
- [ ] Seed with SA 2024/2025 tax data
- [ ] Create Pydantic models
- [ ] **Test Suite:**
  - Test tax config retrieval by year
  - Test rate lookup
  - Test allowance lookup
  - Test versioning
- [ ] **Run:** `pytest tests/models/test_tax_config_models.py -v`
- [ ] **Acceptance:** Tax config models tests pass

### Task 2.7.2: UK Income Tax Calculator

**Reference:** `CoreTaxCalcs.md` (Feature 9.1: UK Income Tax calculation)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create UK income tax calculation service
- [ ] Implement personal allowance (£12,570, tapered)
- [ ] Implement tax bands (basic 20%, higher 40%, additional 45%)
- [ ] Implement Scottish rates (if applicable)
- [ ] Calculate tax liability
- [ ] **Test Suite:**
  - Test with income < personal allowance (£0 tax)
  - Test basic rate taxpayer
  - Test higher rate taxpayer
  - Test additional rate taxpayer
  - Test personal allowance taper (income > £100k)
  - Test Scottish rates
- [ ] **Run:** `pytest tests/services/test_uk_income_tax.py -v`
- [ ] **Acceptance:** UK income tax calculations accurate

### Task 2.7.3: UK National Insurance Calculator

**Reference:** `CoreTaxCalcs.md` (Feature 9.1: UK National Insurance)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create UK NI calculation service
- [ ] Implement Class 1 employee NI (8% + 2%)
- [ ] Implement Class 2 self-employed (flat £3.45/week)
- [ ] Implement Class 4 self-employed (6% + 2%)
- [ ] **Test Suite:**
  - Test Class 1 NI calculation
  - Test Class 2 NI (profits > £12,570)
  - Test Class 4 NI calculation
- [ ] **Run:** `pytest tests/services/test_uk_ni.py -v`
- [ ] **Acceptance:** UK NI calculations accurate

### Task 2.7.4: UK CGT Calculator

**Reference:** `CoreTaxCalcs.md` (Feature 9.1: UK CGT calculation)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create UK CGT calculation service
- [ ] Implement annual exempt amount (£3,000)
- [ ] Implement rates: 10%/20% (general), 18%/24% (residential property)
- [ ] Determine taxpayer rate band (basic/higher/additional)
- [ ] Calculate CGT liability
- [ ] **Test Suite:**
  - Test with gains < annual exemption (£0 tax)
  - Test general asset at basic rate (10%)
  - Test general asset at higher rate (20%)
  - Test residential property CGT (18%/24%)
- [ ] **Run:** `pytest tests/services/test_uk_cgt.py -v`
- [ ] **Acceptance:** UK CGT calculations accurate

### Task 2.7.5: SA Income Tax Calculator

**Reference:** `CoreTaxCalcs.md` (Feature 9.1: SA Income Tax calculation)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create SA income tax calculation service
- [ ] Implement tax brackets (18%, 26%, 31%, 36%, 39%, 45%)
- [ ] Implement rebates (primary, secondary, tertiary)
- [ ] Calculate tax liability
- [ ] **Test Suite:**
  - Test with income < rebate threshold (£0 tax)
  - Test each tax bracket
  - Test rebate application (age-based)
- [ ] **Run:** `pytest tests/services/test_sa_income_tax.py -v`
- [ ] **Acceptance:** SA income tax calculations accurate

### Task 2.7.6: SA CGT Calculator

**Reference:** `CoreTaxCalcs.md` (Feature 9.1: SA CGT - inclusion rate)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create SA CGT calculation service
- [ ] Implement inclusion rate method (40% included in income)
- [ ] Apply annual exclusion (R40,000)
- [ ] Calculate tax on included amount
- [ ] **Test Suite:**
  - Test with gains < annual exclusion (£0 tax)
  - Test inclusion rate calculation
  - Test tax on included amount
- [ ] **Run:** `pytest tests/services/test_sa_cgt.py -v`
- [ ] **Acceptance:** SA CGT calculations accurate

### Task 2.7.7: Tax Calculation API Endpoints

**Reference:** `CoreTaxCalcs.md` (Feature 9.1: API Endpoints - implied)
**🐍 DELEGATE TO: `python-backend-engineer`**

- [ ] Create `POST /api/v1/tax/uk/income-tax` endpoint
- [ ] Create `POST /api/v1/tax/uk/national-insurance` endpoint
- [ ] Create `POST /api/v1/tax/uk/cgt` endpoint
- [ ] Create `POST /api/v1/tax/sa/income-tax` endpoint
- [ ] Create `POST /api/v1/tax/sa/cgt` endpoint
- [ ] Create `GET /api/v1/tax/summary/{userId}/{taxYear}` endpoint
- [ ] Accept calculation parameters (income, gains, etc.)
- [ ] Return detailed calculation breakdown
- [ ] **Test Suite:**
  - Test each endpoint with valid inputs
  - Test with edge cases
  - Test summary endpoint
- [ ] **Run:** `pytest tests/api/tax/test_tax_calculations.py -v`
- [ ] **Acceptance:** Tax API works correctly

---

## 🚦 PHASE 2 TAX ENGINE TESTING GATE

### Calculation Accuracy Tests

- [ ] ✅ UK income tax matches HMRC calculations (test with examples)
- [ ] ✅ UK NI matches HMRC calculations
- [ ] ✅ UK CGT matches HMRC calculations
- [ ] ✅ SA income tax matches SARS calculations
- [ ] ✅ SA CGT matches SARS calculations

### Integration Tests

- [ ] ✅ Tax calculations use versioned config correctly
- [ ] ✅ Tax year transitions handled
- [ ] ✅ Tax summary aggregates correctly

### Performance Tests

- [ ] ✅ Tax calculations complete in < 200ms

**Acceptance Criteria:**
🎯 Core tax calculations accurate for both UK and SA.
🎯 Versioned tax configuration system working.
🎯 Tax engine ready for integration with modules.

---

## 🚦 PHASE 2 COMPLETE - FINAL GATE

### Module Integration Tests

- [ ] ✅ Savings, Protection, Investment modules integrated
- [ ] ✅ Data flows between modules correctly
- [ ] ✅ Dashboard aggregates from all modules
- [ ] ✅ Tax calculations use data from all modules

### End-to-End Tests

- [ ] ✅ Add savings account → appears in dashboard
- [ ] ✅ Add life policy → coverage gap calculated
- [ ] ✅ Buy investment → CGT tracked
- [ ] ✅ Income + gains → tax calculated

### Performance & Scale

- [ ] ✅ Dashboard with 50+ accounts loads < 2 seconds
- [ ] ✅ Tax calculation with complex scenario < 500ms

**PHASE 2 ACCEPTANCE:**
✅ **Core financial modules operational**
✅ **Basic tax engine functional**
✅ **Multi-module integration working**

---

# PHASE 3-5 CONTINUATION

_The task list continues with the same detailed structure for:_

**Phase 3:**

- Retirement Module (UK pensions, SA funds, QROPS)
- IHT Planning Module (assets, liabilities, estate calculation, gifts)
- Enhanced Tax Engine (DTA, Tax Residency)

**Phase 4:**

- AI Advisory Engine (recommendations, goal planning, scenarios, personalization)

**Phase 5:**

- Advanced integrations
- Mobile optimization
- Additional jurisdictions
- Machine learning enhancements

_Each phase includes:_

- Detailed tasks with agent delegation
- Comprehensive test suites
- Testing gates
- Acceptance criteria

---

## Document Usage

✅ **Check off tasks as completed**
⛔ **Do not skip testing gates**
🐍 **Delegate Python tasks to `python-backend-engineer`**
⚛️ **Delegate React tasks to `react-coder`**
📚 **Reference shard files for detailed specifications**
🔒 **Maintain app functionality at all times**
🧪 **Fix failing tests before proceeding**

---

**Total Tasks Defined:** 150+ detailed tasks with ~500+ test cases
**Estimated Development Time (Phase 1-2):** 4-6 months with 2-3 developers
**Would you like Phase 3-5 expanded with the same detail level?**
