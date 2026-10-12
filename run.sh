#!/usr/bin/env bash

# LazyHire - Dual Service Runner (FastAPI Backend + Vite React Frontend)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Terminal Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================================${NC}"
echo -e "${RED}          LazyHire Unified Workspace Runner         ${NC}"
echo -e "${BLUE}====================================================${NC}"

# 1. Environment Verification
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        echo -e "${YELLOW}[!] .env not found. Creating from .env.example...${NC}"
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    fi
fi

# 2. Determine Python / Uvicorn executable
if [ -f "$PROJECT_ROOT/.venv/bin/uvicorn" ]; then
    UVICORN_BIN="$PROJECT_ROOT/.venv/bin/uvicorn"
elif command -v uvicorn &> /dev/null; then
    UVICORN_BIN="uvicorn"
elif [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
    UVICORN_BIN="$PROJECT_ROOT/.venv/bin/python -m uvicorn"
else
    UVICORN_BIN="python3 -m uvicorn"
fi

# 3. Check UI dependencies
if [ ! -d "$PROJECT_ROOT/UI/node_modules" ]; then
    echo -e "${YELLOW}[!] UI node_modules missing. Installing dependencies...${NC}"
    npm --prefix "$PROJECT_ROOT/UI" install
fi

# 4. Graceful Shutdown Trap
cleanup() {
    echo ""
    echo -e "${YELLOW}[*] Shutting down LazyHire services...${NC}"
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    wait 2>/dev/null || true
    echo -e "${GREEN}[✓] All services stopped cleanly.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# 5. Start Backend Server (FastAPI)
echo -e "${GREEN}[1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...${NC}"
$UVICORN_BIN src.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# Brief pause to let backend initialize
sleep 1.5

# 6. Start Frontend Dev Server (Vite React)
echo -e "${GREEN}[2/2] Starting Vite React Frontend on http://localhost:5173 ...${NC}"
npm --prefix "$PROJECT_ROOT/UI" run dev -- --host &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}====================================================${NC}"
echo -e "  ${GREEN}✔ LazyHire Services Running:${NC}"
echo -e "  • Frontend UI:    ${BLUE}http://localhost:5173${NC}"
echo -e "  • Backend API:    ${BLUE}http://127.0.0.1:8000${NC}"
echo -e "  • Swagger Docs:   ${BLUE}http://127.0.0.1:8000/docs${NC}"
echo -e "${GREEN}====================================================${NC}"
echo -e "${YELLOW}Press Ctrl+C to terminate both services.${NC}"
echo ""

# Wait for background processes
wait "$BACKEND_PID" "$FRONTEND_PID"
