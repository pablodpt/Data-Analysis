#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
CONFIG="${1:-config.json}"
DATE="${2:-$(date +%F)}"
exec .venv/bin/python report.py --config "$CONFIG" --as-of "$DATE"
