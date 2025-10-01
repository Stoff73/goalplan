#!/bin/bash

# Start Frontend Only

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting GoalPlan Frontend...${NC}"

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$PROJECT_DIR"
echo -e "${GREEN}✓ Starting frontend on http://localhost:5173${NC}"
npm run dev
