#!/usr/bin/env bash
# Run the platform locally without Docker (backend + frontend dev servers).
# Usage, from the project root:  ./start.sh
# Needs Python 3.12+ and Node.js 20+. The first run installs dependencies.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load nvm if it is installed, so the right Node.js is on PATH
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
# shellcheck disable=SC1091
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

command -v python3 >/dev/null || { echo "python3 not found: install Python 3.12+"; exit 1; }
command -v npm >/dev/null || { echo "npm not found: install Node.js 20+"; exit 1; }

# Backend: virtualenv + dependencies
if [ ! -d "$PROJECT_DIR/.venv" ]; then
  echo "Creating Python virtualenv in .venv ..."
  python3 -m venv "$PROJECT_DIR/.venv"
  "$PROJECT_DIR/.venv/bin/pip" install --upgrade pip >/dev/null
  "$PROJECT_DIR/.venv/bin/pip" install -r "$PROJECT_DIR/backend/requirements.txt"
fi

# Backend: config
if [ ! -f "$PROJECT_DIR/backend/.env" ]; then
  # Outside Docker the LLM on this machine is at localhost, not host.docker.internal
  sed 's#host.docker.internal#localhost#' "$PROJECT_DIR/backend/.env.example" > "$PROJECT_DIR/backend/.env"
  echo "Created backend/.env from .env.example. Edit it to set your LLM endpoint and any API keys."
fi

# Frontend: dependencies
if [ ! -d "$PROJECT_DIR/frontend/node_modules" ]; then
  echo "Installing frontend dependencies ..."
  (cd "$PROJECT_DIR/frontend" && npm ci)
fi

echo "Starting backend on http://localhost:8000 ..."
(cd "$PROJECT_DIR/backend" && "$PROJECT_DIR/.venv/bin/uvicorn" main:app --reload --port 8000) &
BACKEND_PID=$!

echo "Starting frontend on http://localhost:5173 ..."
(cd "$PROJECT_DIR/frontend" && npm run dev) &
FRONTEND_PID=$!

trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null' EXIT

echo ""
echo "Platform running:"
echo "  Frontend:    http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  API docs:    http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers."
wait
