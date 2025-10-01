# GoalPlan Startup Guide

Quick reference for starting and stopping the GoalPlan application.

## Prerequisites

Ensure these services are installed and running:
- **PostgreSQL 15+** - `brew services start postgresql@15`
- **Redis 7+** - `brew services start redis`

## Starting the Application

### Option 1: Start Everything (Recommended)

```bash
./start.sh
```

This script will:
- ✅ Check PostgreSQL is running (start if not)
- ✅ Check Redis is running (start if not)
- ✅ Start backend on http://localhost:8000
- ✅ Start frontend on http://localhost:5173
- ✅ Wait for services to be ready
- ✅ Display access URLs and log locations

**Output:**
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Logs: `backend.log` and `frontend.log`

### Option 2: Start Services Individually

**Backend only:**
```bash
./start-backend.sh
```
Runs in foreground. Access: http://localhost:8000

**Frontend only:**
```bash
./start-frontend.sh
```
Runs in foreground. Access: http://localhost:5173

### Option 3: Manual Start (Development)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

## Stopping the Application

### Stop all services:

```bash
./stop.sh
```

This will:
- Stop backend process
- Stop frontend process
- Kill any processes on ports 8000 and 5173
- Clean up PID files

### Stop individual services:

**Backend:**
```bash
# If started with start.sh
kill $(cat .backend.pid)

# If running in terminal, press Ctrl+C
```

**Frontend:**
```bash
# If started with start.sh
kill $(cat .frontend.pid)

# If running in terminal, press Ctrl+C
```

## Viewing Logs

When using `./start.sh`, logs are written to files:

```bash
# Watch backend logs
tail -f backend.log

# Watch frontend logs
tail -f frontend.log

# View both simultaneously
tail -f backend.log frontend.log
```

## Troubleshooting

### Port Already in Use

If you see "address already in use" errors:

```bash
# Check what's using port 8000 (backend)
lsof -ti:8000

# Check what's using port 5173 (frontend)
lsof -ti:5173

# Kill process on port
kill -9 $(lsof -ti:8000)  # Backend
kill -9 $(lsof -ti:5173)  # Frontend

# Or use stop.sh which does this automatically
./stop.sh
```

### PostgreSQL Not Running

```bash
# Check status
brew services list | grep postgresql

# Start PostgreSQL
brew services start postgresql@15

# Verify connection
/opt/homebrew/opt/postgresql@15/bin/psql -U goalplan_user -d goalplan_dev -h localhost
```

### Redis Not Running

```bash
# Check status
brew services list | grep redis

# Start Redis
brew services start redis

# Verify connection
redis-cli ping  # Should return PONG
```

### Backend Won't Start

1. **Check virtual environment:**
   ```bash
   cd backend
   source venv/bin/activate
   python --version  # Should show 3.12.11
   ```

2. **Check database connection:**
   ```bash
   cat .env  # Verify DATABASE_PASSWORD matches
   ```

3. **Check logs:**
   ```bash
   tail -n 50 backend.log
   ```

4. **Test manually:**
   ```bash
   cd backend
   source venv/bin/activate
   python -c "from config import settings; print(settings.DATABASE_URL)"
   ```

### Frontend Won't Start

1. **Check dependencies:**
   ```bash
   npm install
   ```

2. **Check logs:**
   ```bash
   tail -n 50 frontend.log
   ```

3. **Clear cache:**
   ```bash
   rm -rf node_modules/.vite
   npm run dev
   ```

## Health Checks

### Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "GoalPlan API",
  "version": "0.1.0",
  "environment": "development",
  "redis": "connected"
}
```

### Frontend Health

```bash
curl http://localhost:5173
```

Should return HTML with status 200.

## Development Workflow

### Daily Development

1. **Start services:**
   ```bash
   ./start.sh
   ```

2. **Make changes** - Both services auto-reload:
   - Backend: FastAPI auto-reloads on file changes
   - Frontend: Vite HMR (Hot Module Replacement)

3. **Check logs** if issues occur:
   ```bash
   tail -f backend.log frontend.log
   ```

4. **Stop when done:**
   ```bash
   ./stop.sh
   ```

### Running Tests

**Backend:**
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

**Frontend:**
```bash
npm test                  # Jest
npx playwright test       # E2E
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./start.sh` | Start all services |
| `./stop.sh` | Stop all services |
| `./start-backend.sh` | Backend only (foreground) |
| `./start-frontend.sh` | Frontend only (foreground) |
| `tail -f backend.log` | View backend logs |
| `tail -f frontend.log` | View frontend logs |
| `curl localhost:8000/health` | Check backend health |
| `lsof -ti:8000` | Find process on port 8000 |
| `brew services list` | Check service status |

## URLs

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **API ReDoc:** http://localhost:8000/redoc

---

**See also:**
- `README.md` - Complete setup instructions
- `backend/DATABASE_SETUP.md` - Database configuration
- `PHASE0_COMPLETION.md` - Setup completion status
