#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null
    wait 2>/dev/null
    echo -e "${GREEN}Done.${NC}"
}
trap cleanup EXIT INT TERM

# Check Python dependencies
echo -e "${YELLOW}[1/4] Checking Python dependencies...${NC}"
MISSING_DEPS=false
python3 -c "import fastapi, uvicorn, cv2, numpy, PIL, httpx, sklearn" 2>/dev/null || MISSING_DEPS=true

if [ "$MISSING_DEPS" = true ]; then
    echo -e "  Installing backend dependencies..."
    pip3 install --break-system-packages -q -r "$BACKEND_DIR/requirements.txt" 2>/dev/null || \
    pip3 install -q -r "$BACKEND_DIR/requirements.txt"
fi
echo -e "  ${GREEN}Python dependencies ready.${NC}"

# Check Node dependencies
echo -e "${YELLOW}[2/4] Checking Node dependencies...${NC}"
if [ ! -d "$FRONTEND_DIR/node_modules/next" ]; then
    echo -e "  Installing frontend dependencies..."
    cd "$FRONTEND_DIR" && npm install --silent
fi
echo -e "  ${GREEN}Node dependencies ready.${NC}"

# Start backend
echo -e "${YELLOW}[3/4] Starting backend...${NC}"
cd "$BACKEND_DIR"
uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Start frontend
echo -e "${YELLOW}[4/4] Starting frontend...${NC}"
cd "$FRONTEND_DIR"
npm run dev -- --port 3000 &
FRONTEND_PID=$!

# Wait for servers to be ready
sleep 2
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Servers running:${NC}"
echo -e "${GREEN}  Frontend:  http://localhost:3000${NC}"
echo -e "${GREEN}  Backend:   http://localhost:8000${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Press Ctrl+C to stop."

wait
