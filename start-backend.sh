#!/bin/bash

# Start Backend Only

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Starting GoalPlan Backend...${NC}"

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check services
echo -e "${YELLOW}Checking PostgreSQL...${NC}"
if ! brew services list | grep -q "postgresql@15.*started"; then
    brew services start postgresql@15
    sleep 2
fi

echo -e "${YELLOW}Checking Redis...${NC}"
if ! brew services list | grep -q "redis.*started"; then
    brew services start redis
    sleep 2
fi

# Start backend
cd "$PROJECT_DIR/backend"
source venv/bin/activate
echo -e "${GREEN}✓ Starting backend on http://localhost:8000${NC}"
echo -e "  API Docs: http://localhost:8000/docs"
uvicorn main:app --reload
