"""OpenBerg settings — everything comes from env / .env, all optional."""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:
    pass  # python-dotenv missing -> plain env vars still work


def _get(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


FRED_API_KEY = _get("FRED_API_KEY")
FINNHUB_API_KEY = _get("FINNHUB_API_KEY")

# auto | always | never
DEMO_MODE = _get("DEMO_MODE", "auto").lower() or "auto"

PORT = int(_get("PORT", "8000") or 8000)

HTTP_TIMEOUT = 12.0
USER_AGENT = "OpenBerg/0.1 (free terminal; contact: openberg-local)"

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "defaults.json"

# TTLs (seconds) — be gentle with free tiers
TTL_QUOTE = 30
TTL_HISTORY = 300
TTL_PROFILE = 3600
TTL_FINANCIALS = 21600
TTL_NEWS = 600
TTL_OVERVIEW = 60
TTL_ECON = 3600
TTL_SEARCH = 3600


def demo_always() -> bool:
    return DEMO_MODE == "always"


def demo_never() -> bool:
    return DEMO_MODE == "never"
