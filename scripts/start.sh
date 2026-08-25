#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "=== Manufacturing Agent Platform ==="
echo ""

# Backend venv
if [ ! -d "backend/.venv" ]; then
    echo "[1/4] Creating Python virtual environment..."
    python3 -m venv backend/.venv
fi

echo "[2/4] Installing backend dependencies..."
source backend/.venv/bin/activate
pip install -r backend/requirements.txt -q

echo "[3/4] Seeding demo data..."
PYTHONPATH=backend python scripts/seed_demo.py

echo "[4/4] Starting backend on http://127.0.0.1:8000 ..."
echo ""
echo "Frontend: cd frontend && npm install && npm run dev"
echo "Login:    admin / Admin123!"
echo ""
cd backend
uvicorn app.main:app --reload --host 127.0.0.1
