#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec .venv/bin/python pipeline.py --config "${1:-config.json}" --as-of "${2:-$(date +%F)}" --strict
