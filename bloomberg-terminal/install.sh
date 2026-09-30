#!/usr/bin/env bash
# OpenBerg installer (macOS / Linux) — run once:  bash install.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "== OpenBerg installer =="

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: necesitas Python 3.11+ (gratis): https://www.python.org/downloads/"
  exit 1
fi
echo "Python: $(python3 --version)"

if [ ! -d ".venv" ]; then
  echo "Creando entorno virtual..."
  if ! python3 -m venv .venv 2>/dev/null; then
    echo "ERROR: falta python3-venv. En Ubuntu/Debian: sudo apt install python3-venv"
    exit 1
  fi
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "Instalando dependencias (la primera vez tarda unos minutos)..."
python -m pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Creado .env (sin claves: funciona igual con datos gratuitos)."
fi

echo ""
echo "OK Instalado. Para arrancar el terminal:"
echo "   bash run.sh"
echo "Luego abre http://localhost:8000 en tu navegador."
