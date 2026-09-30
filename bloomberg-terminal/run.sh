#!/usr/bin/env bash
# OpenBerg launcher (macOS / Linux) — bash run.sh
set -euo pipefail
cd "$(dirname "$0")"

if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

if [ ! -f ".env" ]; then
  echo "[openberg] No .env found — copying .env.example (demo/hybrid mode, no keys needed)."
  cp .env.example .env
fi

python3 -c "import fastapi" 2>/dev/null || {
  echo "[openberg] Installing requirements..."
  python3 -m pip install -r requirements.txt
}

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
echo "[openberg] Starting on http://${HOST}:${PORT}  (docs: /docs, Ctrl+C to stop)"
exec python3 -m uvicorn backend.main:app --host "${HOST}" --port "${PORT}"
