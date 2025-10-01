1. USER AUTHENTICATION & PROFILE MANAGEMENT
Feature 1.1: User Registration
Feature Name: User Registration and Onboarding
User Story: As a new user, I want to create an account with email and password so that I can securely access the financial planning platform.
Acceptance Criteria:
•	User can register with email and password
•	Email verification required before full access
•	Password must meet security requirements (min 12 chars, uppercase, lowercase, number, special char)
•	User receives welcome email with onboarding guide
•	Account created with default settings
•	GDPR/POPIA consent captured
•	User can select preferred country (UK/SA/Both)
Technical Requirements:
•	Encryption: bcrypt or Argon2 for password hashing
•	JWT tokens for session management
•	Email service integration (SendGrid, AWS SES, or similar)
•	Rate limiting on registration endpoint (max 5 attempts per IP per hour)
•	CAPTCHA integration to prevent bot registrations
Constraints:
•	Must comply with UK GDPR and SA POPIA
•	No Node.js backend
•	Session timeout: 30 minutes inactivity, 24 hours absolute
Implementation Approach:
ENDPOINT: POST /api/v1/auth/register
REQUEST BODY:
{
  email: string (valid email format),
  password: string (meets complexity requirements),
  firstName: string,
  lastName: string,
  country: enum['UK', 'SA', 'BOTH'],
  termsAccepted: boolean,
  marketingConsent: boolean
}

PROCESS:
1. Validate input data
2. Check if email already exists
3. Hash password using Argon2
4. Generate email verification token (UUID, expires in 24h)
5. Create user record with status='PENDING_VERIFICATION'
6. Store verification token in cache/DB
7. Send verification email
8. Return success response (do not reveal if email exists)

RESPONSE:
{
  success: true,
  message: "Registration successful. Please check your email.",
  userId: uuid
}
User Flow:
[Landing Page] → [Register Button]
     ↓
[Registration Form]
  - Email input
  - Password input (with strength indicator)
  - Confirm password
  - First name / Last name
  - Country selection
  - Terms checkbox
  - Marketing consent checkbox
     ↓
[Submit] → [Validation]
     ↓
[Success Message] → [Email Sent Notification]
     ↓
[User checks email] → [Clicks verification link]
     ↓
[Account Activated] → [Redirect to Login]
API Endpoints:
•	POST /api/v1/auth/register - Register new user
•	GET /api/v1/auth/verify-email?token={token} - Verify email
•	POST /api/v1/auth/resend-verification - Resend verification email
Data Models:
TABLE: users
- id: UUID (PK)
- email: VARCHAR(255) UNIQUE NOT NULL
- password_hash: VARCHAR(255) NOT NULL
- first_name: VARCHAR(100)
- last_name: VARCHAR(100)
- country_preference: ENUM('UK', 'SA', 'BOTH')
- status: ENUM('PENDING_VERIFICATION', 'ACTIVE', 'SUSPENDED', 'DELETED')
- email_verified: BOOLEAN DEFAULT FALSE
- terms_accepted_at: TIMESTAMP
- marketing_consent: BOOLEAN
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
- last_login_at: TIMESTAMP

TABLE: email_verification_tokens
- id: UUID (PK)
- user_id: UUID (FK to users)
- token: VARCHAR(255) UNIQUE
- expires_at: TIMESTAMP
- used: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP

INDEX on users.email
INDEX on email_verification_tokens.token
INDEX on email_verification_tokens.expires_at
Error Handling:
ERROR CASES:
1. Email already registered
   - Response: 409 Conflict
   - Message: "An account with this email already exists"
   
2. Invalid email format
   - Response: 400 Bad Request
   - Message: "Please provide a valid email address"
   
3. Password too weak
   - Response: 400 Bad Request
   - Message: "Password must be at least 12 characters and include uppercase, lowercase, number, and special character"
   
4. Terms not accepted
   - Response: 400 Bad Request
   - Message: "You must accept the terms and conditions"
   
5. Rate limit exceeded
   - Response: 429 Too Many Requests
   - Message: "Too many registration attempts. Please try again later"
   
6. Email service failure
   - Response: 500 Internal Server Error
   - Log error, queue for retry
   - Message: "Registration successful but verification email delayed"

EDGE CASES:
- User tries to register with existing email: Return generic success message (security)
- Token expired: Allow resend with new token
- User clicks verify link multiple times: Idempotent operation
- Simultaneous registrations with same email: DB unique constraint handles it
Performance Considerations:
•	Password hashing is CPU intensive: Use async hashing, consider queuing
•	Email sending should be async (message queue)
•	Cache email existence checks (5 min TTL) to reduce DB queries
•	Verification tokens in Redis for fast lookup
•	Rate limiting via Redis counter
•	Expected load: 1000 registrations/day, <500ms response time
 
Feature 1.2: User Login with 2FA
Feature Name: Secure Login with Two-Factor Authentication
User Story: As a registered user, I want to log in securely with my email and password, and enable two-factor authentication for enhanced security.
Acceptance Criteria:
•	User can login with email and password
•	Optional 2FA via authenticator app (TOTP)
•	Remember device option (30 days)
•	Account lockout after 5 failed attempts (30 min cooldown)
•	Notification sent on new device login
•	Session management with JWT tokens
•	Refresh token mechanism for extended sessions
Technical Requirements:
•	TOTP library for 2FA (pyotp, Google Authenticator compatible)
•	JWT with RS256 signing
•	Redis for session management and rate limiting
•	Device fingerprinting for "remember device"
•	IP logging for security monitoring
Constraints:
•	Access token lifetime: 15 minutes
•	Refresh token lifetime: 7 days
•	2FA code valid for 30 seconds (1 time-step)
•	Maximum 5 concurrent sessions per user
Implementation Approach:
ENDPOINT: POST /api/v1/auth/login
REQUEST BODY:
{
  email: string,
  password: string,
  deviceId: string (optional, for remember device),
  totpCode: string (optional, if 2FA enabled)
}

PROCESS:
1. Rate limit check (max 5 attempts per IP per 15 min)
2. Fetch user by email
3. Check account status (must be ACTIVE)
4. Verify password hash
5. If 2FA enabled and not remembered device:
   a. If totpCode provided, verify it
   b. If totpCode not provided, return 2FA_REQUIRED
6. Check device trust status
7. Generate access token (JWT, 15 min expiry)
8. Generate refresh token (JWT, 7 days expiry)
9. Store session in Redis
10. Update last_login_at
11. Log login event
12. Send notification if new device
13. Return tokens

RESPONSE SUCCESS:
{
  accessToken: string,
  refreshToken: string,
  expiresIn: 900,
  user: {
    id: uuid,
    email: string,
    firstName: string,
    lastName: string,
    twoFactorEnabled: boolean
  }
}

RESPONSE 2FA REQUIRED:
{
  requiresTwoFactor: true,
  message: "Please provide your 2FA code"
}
User Flow:
[Login Page]
     ↓
[Enter Email & Password] → [Submit]
     ↓
[Backend Validation]
     ↓
[2FA Enabled?] → YES → [2FA Code Entry Page]
     |                        ↓
     |                   [Enter TOTP Code]
     |                        ↓
     |                   [Verify Code]
     |                        ↓
     NO ← ← ← ← ← ← ← ← ← ← [Success]
     ↓
[Generate Tokens]
     ↓
[Redirect to Dashboard]
API Endpoints:
•	POST /api/v1/auth/login - User login
•	POST /api/v1/auth/refresh - Refresh access token
•	POST /api/v1/auth/logout - Invalidate session
•	POST /api/v1/auth/logout-all - Invalidate all sessions
•	GET /api/v1/auth/sessions - List active sessions
•	POST /api/v1/auth/enable-2fa - Enable 2FA
•	POST /api/v1/auth/disable-2fa - Disable 2FA
•	POST /api/v1/auth/verify-2fa-setup - Verify 2FA during setup
Data Models:
TABLE: user_sessions
- id: UUID (PK)
- user_id: UUID (FK to users)
- access_token_jti: VARCHAR(255) UNIQUE (JWT ID)
- refresh_token_jti: VARCHAR(255) UNIQUE
- device_id: VARCHAR(255)
- device_name: VARCHAR(255)
- ip_address: VARCHAR(45)
- user_agent: TEXT
- is_trusted: BOOLEAN DEFAULT FALSE
- last_activity: TIMESTAMP
- created_at: TIMESTAMP
- expires_at: TIMESTAMP

TABLE: user_2fa
- user_id: UUID (PK, FK to users)
- secret: VARCHAR(255) ENCRYPTED
- enabled: BOOLEAN DEFAULT FALSE
- backup_codes: JSON ENCRYPTED (array of hashed codes)
- created_at: TIMESTAMP
- last_used_at: TIMESTAMP

TABLE: login_attempts
- id: UUID (PK)
- email: VARCHAR(255)
- ip_address: VARCHAR(45)
- success: BOOLEAN
- failure_reason: VARCHAR(100)
- timestamp: TIMESTAMP

INDEX on user_sessions.user_id
INDEX on user_sessions.access_token_jti
INDEX on user_sessions.expires_at
INDEX on login_attempts.ip_address, timestamp
Error Handling:
ERROR CASES:
1. Invalid credentials
   - Response: 401 Unauthorized
   - Message: "Invalid email or password"
   - Log attempt in login_attempts table
   
2. Account locked (5 failed attempts)
   - Response: 423 Locked
   - Message: "Account temporarily locked due to multiple failed login attempts. Try again in 30 minutes"
   
3. Account not verified
   - Response: 403 Forbidden
   - Message: "Please verify your email address before logging in"
   
4. 2FA code invalid
   - Response: 401 Unauthorized
   - Message: "Invalid or expired 2FA code"
   
5. Rate limit exceeded
   - Response: 429 Too Many Requests
   - Message: "Too many login attempts. Please try again later"
   
6. Session limit exceeded
   - Response: 409 Conflict
   - Message: "Maximum number of active sessions reached. Please logout from another device"
   - Provide option to force logout oldest session

EDGE CASES:
- Concurrent logins: Allow up to 5 sessions
- Token refresh while access token still valid: Allow, extend session
- Logout with expired refresh token: Return success (idempotent)
- Time synchronization issues with TOTP: Accept codes from previous/next time window (90 sec total window)
- User changes password: Invalidate all existing sessions except current
Performance Considerations:
•	Redis session store for fast token validation
•	JWT signature verification is CPU intensive: Cache public key
•	Rate limiting counters in Redis (sliding window algorithm)
•	Async notification sending (queue)
•	Expected load: 10,000 logins/day, <200ms response time
•	Session validation on every API call must be <10ms
•	Consider token payload size (keep under 1KB)
 
