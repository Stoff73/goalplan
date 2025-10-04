# GoalPlan Debug Quick Reference

## 🚨 CRITICAL ISSUES - FIX FIRST

### 1. Rate Limiter Blocks Testing
**Problem:** Login limited to 5 attempts per 15 minutes
**Impact:** E2E tests fail, development blocked
**Quick Fix:**
```bash
redis-cli FLUSHDB  # Clear rate limits
```
**Permanent Fix:** Update `backend/middleware/rate_limiter.py` line 131
```python
def rate_limit_login():
    if settings.is_development():
        return limiter.limit("100/minute", ...)
    return limiter.limit("5/15 minutes", ...)
```

### 2. Missing /api/v1/users/me Endpoint
**Problem:** Frontend expects this, backend doesn't have it
**Quick Fix:** Add to `backend/api/v1/user/__init__.py`:
```python
@router.get("/me")
async def get_me(...):
    return await get_user_profile(...)
```

### 3. Scenarios Router Not Included
**Problem:** GET /api/v1/scenarios returns 404
**Fix:** Add to `backend/main.py`:
```python
from api.v1.scenarios import router as scenarios_router
app.include_router(scenarios_router, prefix=f"{settings.API_V1_PREFIX}/scenarios")
```

---

## 📋 API ENDPOINT MISMATCH TABLE

| Frontend Expects | Backend Has | Fix Needed |
|---|---|---|
| GET /api/v1/users/me | GET /api/v1/user/profile | ✅ Add alias |
| GET /api/v1/income | GET /api/v1/user/income | ✅ Update frontend |
| GET /api/v1/protection/policies | GET /api/v1/protection/coverage | ⚠️ Verify correct |
| GET /api/v1/scenarios | (missing router) | ✅ Add router |
| GET /api/v1/goals/summary | /{goal_id} catches it | ✅ Reorder routes |

---

## 🔧 QUICK FIXES

### Create Test User
```python
# Run from backend/
python -c "
import asyncio
from database import AsyncSessionLocal
from models.user import User
from utils.password import hash_password
import uuid

async def create_test_user():
    async with AsyncSessionLocal() as db:
        user = User(
            id=uuid.uuid4(),
            email='testuser@example.com',
            password_hash=hash_password('TestPassword123'),
            first_name='Test',
            last_name='User',
            country_preference='UK',
            email_verified=True,
            status='ACTIVE',
            terms_accepted_at=datetime.utcnow()
        )
        db.add(user)
        await db.commit()

asyncio.run(create_test_user())
"
```

### Clear Account Lockout
```python
# Clear login attempts
python -c "
import asyncio
from database import AsyncSessionLocal
from models.session import LoginAttempt
from sqlalchemy import delete

async def clear_lockout():
    async with AsyncSessionLocal() as db:
        await db.execute(delete(LoginAttempt).where(LoginAttempt.email == 'testuser@example.com'))
        await db.commit()

asyncio.run(clear_lockout())
"
```

---

## 📊 TEST RESULTS SUMMARY

### API Endpoints: 65.4% Working
- ✅ 17/26 endpoints working
- ❌ 9/26 broken (404, 307, or 422)

### E2E Tests: 0% Passing
- ❌ All 13 tests failed (rate limiting)
- After fix: Expect 80%+ pass rate

### Critical Endpoints Status:
- ✅ POST /api/v1/auth/login - Working
- ❌ GET /api/v1/users/me - Missing
- ✅ GET /api/v1/user/profile - Working
- ❌ GET /api/v1/scenarios - Router not included

---

## 🎯 RECOMMENDED FIX ORDER

1. **Rate limiter** (5 min) - Blocks everything else
2. **Test user setup** (5 min) - Needed for testing
3. **Add /users/me** (10 min) - Critical endpoint
4. **Include scenarios router** (2 min) - Simple fix
5. **Frontend API path fixes** (30 min) - Update all calls
6. **Browser test verification** (15 min) - MANDATORY

Total estimated time: **~90 minutes** to functional state

---

## 🔍 BROWSER TESTING CHECKLIST

After fixes, test each page manually:

```
□ http://localhost:5173/login
  - Can login successfully
  - No console errors
  - Redirects to dashboard

□ http://localhost:5173/dashboard
  - Page loads
  - No 404 network errors
  - Data displays (or empty state)

□ http://localhost:5173/income
  - Page loads
  - No 500 errors
  - Can add income

□ http://localhost:5173/tax-status
  - Page loads
  - No 500 errors

□ http://localhost:5173/protection
  - Page loads
  - API calls succeed

□ http://localhost:5173/investments
  - Page loads
  - Portfolio data or empty state

□ http://localhost:5173/retirement
  - Page loads
  - No critical errors

□ http://localhost:5173/iht
  - Page loads
  - Estate data accessible

□ http://localhost:5173/goals
  - Page loads
  - Can create goals

□ http://localhost:5173/scenarios
  - Page loads (after router fix)
  - Scenarios load

□ http://localhost:5173/ai-advisor
  - Page loads
  - AI features work

□ http://localhost:5173/recommendations
  - Page loads
  - Recommendations display
```

---

## 💡 COMMON ERRORS & SOLUTIONS

### 429 Too Many Requests
**Cause:** Rate limiting
**Solution:** `redis-cli FLUSHDB` or fix rate_limiter.py

### 423 Account Locked
**Cause:** Too many failed login attempts
**Solution:** Clear login_attempts table for that email

### 404 on /api/v1/scenarios
**Cause:** Router not included in main.py
**Solution:** Add router import and include

### Login returns wrong password
**Cause:** Password hash mismatch
**Solution:** Use `utils.password.hash_password()` not passlib

### User not found
**Cause:** Test user doesn't exist or not verified
**Solution:** Create user with email_verified=True

---

## 📞 DEBUGGING COMMANDS

```bash
# Check if services running
ps aux | grep -E "(uvicorn|vite)"

# Test login API
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d @/tmp/login.json

# Check Redis keys
redis-cli KEYS "*"

# Check user in database
psql goalplan_db -c "SELECT email, email_verified, status FROM users WHERE email='testuser@example.com';"

# View backend logs
tail -f backend/logs/app.log

# Check API docs
open http://localhost:8000/docs
```

---

## 🎓 LESSONS LEARNED

1. **Always test in browser** - Code compiles ≠ app works
2. **Rate limiting** needs environment-specific configuration
3. **API contract testing** prevents frontend/backend drift
4. **Test data seeding** essential for development
5. **Route order matters** - Specific routes before parametric ones

---

**Last Updated:** October 4, 2025
**Status:** Ready for fixes
