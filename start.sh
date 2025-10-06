#!/bin/bash

# GoalPlan Startup Script
# Starts both backend and frontend services with real-time console output

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Cleanup function for graceful shutdown
cleanup() {
    echo ""
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}  Shutting down GoalPlan...${NC}"
    echo -e "${YELLOW}========================================${NC}"

    # Kill background processes
    if [ -f "$PROJECT_DIR/.backend.pid" ]; then
        BACKEND_PID=$(cat "$PROJECT_DIR/.backend.pid")
        echo -e "${YELLOW}Stopping backend (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        rm "$PROJECT_DIR/.backend.pid"
    fi

    if [ -f "$PROJECT_DIR/.frontend.pid" ]; then
        FRONTEND_PID=$(cat "$PROJECT_DIR/.frontend.pid")
        echo -e "${YELLOW}Stopping frontend (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null || true
        rm "$PROJECT_DIR/.frontend.pid"
    fi

    # Kill the tail processes
    jobs -p | xargs kill 2>/dev/null || true

    echo -e "${GREEN}✓ Services stopped${NC}"
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup INT TERM

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GoalPlan - Starting Services${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get the project root directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if PostgreSQL is running
echo -e "${YELLOW}Checking PostgreSQL...${NC}"
if brew services list | grep -q "postgresql@15.*started"; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${RED}✗ PostgreSQL is not running${NC}"
    echo -e "${YELLOW}Starting PostgreSQL...${NC}"
    brew services start postgresql@15
    sleep 2
    echo -e "${GREEN}✓ PostgreSQL started${NC}"
fi

# Check if Redis is running
echo -e "${YELLOW}Checking Redis...${NC}"
if brew services list | grep -q "redis.*started"; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}✗ Redis is not running${NC}"
    echo -e "${YELLOW}Starting Redis...${NC}"
    brew services start redis
    sleep 2
    echo -e "${GREEN}✓ Redis started${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Starting Backend (FastAPI)${NC}"
echo -e "${BLUE}========================================${NC}"

# Clear old log files
> "$PROJECT_DIR/backend.log"
> "$PROJECT_DIR/frontend.log"

# Check if virtual environment exists at project root
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    cd "$PROJECT_DIR"
    python3.12 -m venv .venv
    source .venv/bin/activate
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r backend/requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    source "$PROJECT_DIR/.venv/bin/activate"
fi

# Start backend in background
cd "$PROJECT_DIR/backend"
nohup python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001 > "$PROJECT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$PROJECT_DIR/.backend.pid"

echo -e "${GREEN}✓ Backend starting (PID: $BACKEND_PID)${NC}"
echo -e "  URL: http://localhost:8001"
echo -e "  API Docs: http://localhost:8001/docs"

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready!${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Backend failed to start. Showing logs:${NC}"
        cat "$PROJECT_DIR/backend.log"
        cleanup
        exit 1
    fi
done

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Starting Frontend (React + Vite)${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if frontend node_modules exists
cd "$PROJECT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo -e "${RED}✗ Node modules not found!${NC}"
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Start frontend in background (stay in frontend directory)
cd "$PROJECT_DIR/frontend"
nohup npm run dev > "$PROJECT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$PROJECT_DIR/.frontend.pid"

echo -e "${GREEN}✓ Frontend starting (PID: $FRONTEND_PID)${NC}"
echo -e "  URL: http://localhost:5173"

# Wait for frontend to start
echo -e "${YELLOW}Waiting for frontend to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is ready!${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}⚠ Frontend may still be starting...${NC}"
    fi
done

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✓ GoalPlan is running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Backend:${NC}  http://localhost:8001"
echo -e "${BLUE}API Docs:${NC} http://localhost:8001/docs"
echo -e "${BLUE}Frontend:${NC} http://localhost:5173"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Live Console Output${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Show real-time output from both services
# Backend output in blue, Frontend output in green
(tail -f "$PROJECT_DIR/backend.log" | sed "s/^/$(echo -e ${BLUE})[BACKEND]$(echo -e ${NC}) /" ) &
(tail -f "$PROJECT_DIR/frontend.log" | sed "s/^/$(echo -e ${GREEN})[FRONTEND]$(echo -e ${NC}) /" ) &

# Wait indefinitely (until Ctrl+C)
wait
