#!/bin/bash
# Start the OSINT Cold Call platform (backend + frontend)
# Run from the project root: ./start.sh

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Activate virtualenv
source "$PROJECT_DIR/.venv/bin/activate"

# Start backend
echo "Starting backend on http://localhost:8000 ..."
cd "$PROJECT_DIR/backend"
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend on http://localhost:5173 ..."
cd "$PROJECT_DIR/frontend"

# Load nvm if available
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

npm run dev &
FRONTEND_PID=$!

echo ""
echo "Platform running:"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
