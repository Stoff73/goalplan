# GoalPlan - Quick Start Guide

## Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 15
- Redis

## First Time Setup

1. **Start the application:**
   ```bash
   ./start.sh
   ```

   The script will automatically:
   - Check and start PostgreSQL
   - Check and start Redis
   - Set up Python virtual environment (if needed)
   - Install dependencies (if needed)
   - Start backend on http://localhost:8000
   - Start frontend on http://localhost:5173

2. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API Docs: http://localhost:8000/docs
   - Backend API: http://localhost:8000/api/v1

3. **Stop the application:**
   - Press `Ctrl+C` in the terminal where start.sh is running
   - Or run `./stop.sh` in a new terminal

## Manual Testing

### 1. Registration Flow
1. Go to http://localhost:5173
2. You'll see the Login page
3. Click "Register" or go to http://localhost:5173/register
4. Fill in the registration form
5. Check the backend console for the verification email (console output)
6. Copy the verification token from the logs
7. Go to http://localhost:5173/verify-email?token=YOUR_TOKEN
8. Your account is now verified!

### 2. Login Flow
1. Go to http://localhost:5173/login
2. Enter your email and password
3. You'll be redirected to the dashboard

### 3. 2FA Setup (Optional)
1. After logging in, go to http://localhost:5173/setup-2fa
2. Scan the QR code with Google Authenticator
3. Enter the 6-digit code to verify
4. Save the backup codes (download them!)

### 4. Login with 2FA
1. Log out
2. Log in again
3. After password, you'll be asked for TOTP code
4. Enter the code from your authenticator app

## Development Workflow

### Watch Console Output
The startup script shows real-time logs from both backend and frontend:
- **[BACKEND]** - Blue text, backend logs
- **[FRONTEND]** - Green text, frontend logs

### Check API Documentation
http://localhost:8000/docs - Interactive Swagger API docs

### Run Tests

**Backend Tests:**
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

**Frontend Tests:**
```bash
cd frontend
npm test                    # Jest component tests
npm run test:e2e           # Playwright E2E tests
```

## Troubleshooting

### Backend won't start
1. Check PostgreSQL is running: `brew services list`
2. Check logs: `cat backend.log`
3. Verify virtual environment: `cd backend && source venv/bin/activate`

### Frontend won't start
1. Check logs: `cat frontend.log`
2. Install dependencies: `cd frontend && npm install`
3. Check node version: `node --version` (should be 18+)

### Can't access pages
1. Make sure both services are running
2. Check console for errors (F12 in browser)
3. Verify API URL in `frontend/.env`

### Database errors
```bash
# Reset database
cd backend
source venv/bin/activate
alembic downgrade base
alembic upgrade head
```

## Next Steps

- Read `PHASE1A_COMPLETION_SUMMARY.md` for complete feature list
- Check `phase1a_authentication_tasks.md` for implementation details
- Review API docs at http://localhost:8000/docs
- Start building Phase 1B features!

## Support

For issues or questions:
1. Check the logs (backend.log, frontend.log)
2. Review the comprehensive documentation in the project root
3. Check the test files for usage examples
