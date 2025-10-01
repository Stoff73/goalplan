#!/bin/bash

# GoalPlan Startup Script
# Starts both backend and frontend services

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

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

# Start backend in background
cd "$PROJECT_DIR/backend"
source venv/bin/activate
nohup uvicorn main:app --reload > "$PROJECT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$PROJECT_DIR/.backend.pid"

echo -e "${GREEN}✓ Backend starting on http://localhost:8000${NC}"
echo -e "  API Docs: http://localhost:8000/docs"
echo -e "  Logs: $PROJECT_DIR/backend.log"
echo -e "  PID: $BACKEND_PID"

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready!${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Backend failed to start. Check backend.log${NC}"
        exit 1
    fi
done

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Starting Frontend (React + Vite)${NC}"
echo -e "${BLUE}========================================${NC}"

# Start frontend in background
cd "$PROJECT_DIR"
nohup npm run dev > "$PROJECT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$PROJECT_DIR/.frontend.pid"

echo -e "${GREEN}✓ Frontend starting on http://localhost:5173${NC}"
echo -e "  Logs: $PROJECT_DIR/frontend.log"
echo -e "  PID: $FRONTEND_PID"

# Wait for frontend to start
echo -e "${YELLOW}Waiting for frontend to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is ready!${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}⚠ Frontend may still be starting. Check frontend.log${NC}"
    fi
done

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✓ GoalPlan is running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Services:"
echo -e "  ${BLUE}Backend:${NC}  http://localhost:8000"
echo -e "  ${BLUE}API Docs:${NC} http://localhost:8000/docs"
echo -e "  ${BLUE}Frontend:${NC} http://localhost:5173"
echo ""
echo -e "Logs:"
echo -e "  ${BLUE}Backend:${NC}  tail -f $PROJECT_DIR/backend.log"
echo -e "  ${BLUE}Frontend:${NC} tail -f $PROJECT_DIR/frontend.log"
echo ""
echo -e "To stop services:"
echo -e "  ${BLUE}./stop.sh${NC}"
echo ""
