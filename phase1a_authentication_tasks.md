# Phase 1A: Authentication System

**Last Updated:** October 1, 2025
**Timeline:** 1-1.5 months (Part of Phase 1: 3-4 months total)
**Critical Rule:** ⛔ **DO NOT PROCEED TO NEXT SECTION UNTIL ALL TESTS PASS** ⛔

---

## 📋 Overview

**Goal:** Build complete, secure authentication system with registration, login, 2FA, and session management

**Prerequisites:** Phase 0 complete (development environment fully operational)

**Module Focus:**
- 1.1-1.4: User Authentication System

**Outputs:**
- User registration with email verification
- Login with JWT authentication (RS256)
- Two-Factor Authentication (TOTP)
- Session management with refresh tokens
- Password reset functionality
- Rate limiting and security features
- Complete authentication UI

**Related Files:**
- Next: `phase1b_user_info_tasks.md` - User Profile and Information Management
- Then: `phase1c_dashboard_savings_tasks.md` - Dashboard and Savings Module

---

## 🔧 Instructions

**Before starting any task:**
1. Read `.claude/instructions.md` for complete agent delegation rules and testing strategy
2. Each task below marked with 🐍 or ⚛️ shows which agent to use
3. Read all listed "Context Files" before implementing

**Task markers:**
- 🐍 = Delegate to `python-backend-engineer` agent
- ⚛️ = Delegate to `react-coder` agent

**Testing:**
- Backend: `pytest` for all Python code
- Frontend: `Jest` for component tests, `Playwright` for E2E only
- See `.claude/instructions.md` for complete testing strategy

---
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


**Next Step:**
➡️ Proceed to `phase1b_user_info_tasks.md` to build User Profile and Information Management

---
