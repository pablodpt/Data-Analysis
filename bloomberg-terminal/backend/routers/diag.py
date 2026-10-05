"""Connectivity diagnostics: which free providers work from THIS machine."""
from __future__ import annotations

import asyncio
import time

import httpx
from fastapi import APIRouter

from .. import config
from ..providers.stooq import stooq_symbol

router = APIRouter(prefix="/api", tags=["diag"])

CHECK_TIMEOUT = 10


async def _check(name, fn):
    t0 = time.time()
    try:
        detail = await asyncio.wait_for(fn(), timeout=CHECK_TIMEOUT)
        ok = True
    except asyncio.TimeoutError:
        detail, ok = "timed out after 10s", False
    except Exception as e:  # noqa: BLE001 — diagnosis wants the message
        detail, ok = f"{type(e).__name__}: {str(e)[:160]}", False
    return {"name": name, "ok": ok, "ms": int((time.time() - t0) * 1000), "detail": detail}


async def _yahoo():
    def _run():
        import yfinance as yf

        px = float(yf.Ticker("AAPL").fast_info.last_price)
        return f"AAPL last = {px}"

    return await asyncio.to_thread(_run)


async def _stooq():
    async with httpx.AsyncClient(timeout=CHECK_TIMEOUT) as c:
        r = await c.get("https://stooq.com/q/l/",
                        params={"s": stooq_symbol("AAPL"), "f": "sd2t2ohlcv",
                                "h": "", "e": "csv"},
                        headers={"User-Agent": config.USER_AGENT})
    if r.status_code != 200 or "Close" not in r.text[:200]:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:80]!r}")
    return "CSV quote OK"


async def _fred():
    async with httpx.AsyncClient(timeout=CHECK_TIMEOUT) as c:
        r = await c.get("https://fred.stlouisfed.org/graph/fredgraph.csv",
                        params={"id": "DGS10"},
                        headers={"User-Agent": config.USER_AGENT})
    if r.status_code != 200 or "DATE" not in r.text[:200]:
        raise RuntimeError(f"HTTP {r.status_code}")
    return "fredgraph.csv OK"


async def _yh_raw():
    """Raw Yahoo screener call (no cookies/impersonation) — often EU-blocked."""
    async with httpx.AsyncClient(timeout=CHECK_TIMEOUT) as c:
        r = await c.get("https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved",
                        params={"id": "day_gainers", "count": 5},
                        headers={"User-Agent": config.USER_AGENT})
    j = r.json() if r.status_code == 200 else {}
    n = len((((j.get("finance") or {}).get("result") or [{}])[0].get("quotes") or []))
    if not n:
        raise RuntimeError(f"HTTP {r.status_code}: no quotes in response")
    return f"{n} quotes OK"


async def _finnhub():
    if not config.FINNHUB_API_KEY:
        return "no key configured (optional)"
    async with httpx.AsyncClient(timeout=CHECK_TIMEOUT) as c:
        r = await c.get("https://finnhub.io/api/v1/quote",
                        params={"symbol": "AAPL", "token": config.FINNHUB_API_KEY},
                        headers={"User-Agent": config.USER_AGENT})
    j = r.json() if r.status_code == 200 else {}
    if not j.get("c"):
        raise RuntimeError(f"HTTP {r.status_code}: {str(j)[:80]}")
    return f"AAPL last = {j['c']}"


@router.get("/diag")
async def diag():
    import platform

    try:
        import yfinance

        yfv = yfinance.__version__
    except Exception as e:  # noqa: BLE001
        yfv = f"import failed: {e}"
    checks = await asyncio.gather(
        _check("yahoo", _yahoo), _check("yahoo-raw", _yh_raw),
        _check("stooq", _stooq), _check("fred", _fred),
        _check("finnhub", _finnhub),
    )
    return {"demo_mode": config.DEMO_MODE, "python": platform.python_version(),
            "yfinance": yfv, "has_fred_key": bool(config.FRED_API_KEY),
            "has_finnhub_key": bool(config.FINNHUB_API_KEY), "checks": checks}
