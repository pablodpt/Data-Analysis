#!/usr/bin/env bash
# OpenBerg launcher — installs deps (if needed) and starts the server.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f ".env" ]; then
  echo "[openberg] No .env found — copying .env.example (demo/hybrid mode, no keys needed)."
  cp .env.example .env
fi

python3 -c "import fastapi" 2>/dev/null || {
  echo "[openberg] Installing requirements..."
  pip install -r requirements.txt
}

PORT="${PORT:-8000}"
echo "[openberg] Starting on http://localhost:${PORT}  (docs: /docs)"
exec uvicorn backend.main:app --host 0.0.0.0 --port "${PORT}"
