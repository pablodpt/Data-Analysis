"""Stooq provider — keyless CSV quotes & daily history. Rock-solid fallback."""
from __future__ import annotations

import csv
import io
from datetime import datetime, timezone

import httpx

from .. import config
from ..cache import cached

ALIASES = {"^GSPC": "^spx", "^IXIC": "^ndq", "^DJI": "^dji", "^RUT": "^rut",
           "^VIX": "^vix", "^TNX": "10usy.b", "GC=F": "xauusd", "CL=F": "cl.f",
           "BTC-USD": "btcusd", "EURUSD=X": "eurusd", "SPY": "spy.us", "QQQ": "qqq.us",
           "DIA": "dia.us", "IWM": "iwm.us"}


def stooq_symbol(symbol: str) -> str:
    s = symbol.upper()
    if s in ALIASES:
        return ALIASES[s]
    if s.startswith("^"):
        return s.lower()
    if s.endswith("=F") or s.endswith("=X") or s.endswith("-USD"):
        return s.lower().replace("=f", "").replace("=x", "").replace("-usd", "usd")
    if "." in s:
        return s.lower()
    return s.lower() + ".us"


RANGE_N = {"1M": 22, "3M": 66, "6M": 132, "1Y": 252, "2Y": 504,
           "5Y": 1258, "10Y": 2516, "MAX": 2516}


@cached(config.TTL_QUOTE, lambda s: f"sq:{s.upper()}")
async def quote(symbol: str) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT) as c:
            r = await c.get("https://stooq.com/q/l/",
                            params={"s": stooq_symbol(symbol), "f": "sd2t2ohlcv",
                                   "h": "", "e": "csv"},
                            headers={"User-Agent": config.USER_AGENT})
        if r.status_code != 200:
            return None
        row = next(csv.DictReader(io.StringIO(r.text)), None)
        if not row or not row.get("Close") or row["Close"] in ("N/D", ""):
            return None
        px = float(row["Close"])
        prev = float(row.get("Open") or 0)  # stooq /l/ has no prevClose; use Open as ref
        return {"symbol": symbol.upper(), "currency": "USD", "price": px,
                "open": _f(row.get("Open")), "high": _f(row.get("High")),
                "low": _f(row.get("Low")), "prevClose": prev or px,
                "change": px - (prev or px),
                "pct": ((px / prev - 1) * 100) if prev else 0.0,
                "volume": _i(row.get("Volume")),
                "asOf": datetime.now(timezone.utc).isoformat()}
    except Exception:
        return None


@cached(config.TTL_HISTORY, lambda s, r="1Y", i="1d": f"sh:{s.upper()}:{r}:{i}")
async def history(symbol: str, rng: str = "1Y", interval: str = "1d") -> dict | None:
    try:
        iv = {"1d": "d", "1wk": "w", "1mo": "m"}.get(interval, "d")
        async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT) as c:
            r = await c.get("https://stooq.com/q/d/l/",
                            params={"s": stooq_symbol(symbol), "i": iv},
                            headers={"User-Agent": config.USER_AGENT})
        if r.status_code != 200 or "<" in r.text[:200]:
            return None
        rows = [x for x in csv.DictReader(io.StringIO(r.text)) if x.get("Close")]
        n = RANGE_N.get(rng.upper(), 252)
        if rng.upper() in ("1D", "5D"):
            n = 5
        rows = rows[-n:]
        if not rows:
            return None
        bars = [{"t": x["Date"], "o": float(x["Open"]), "h": float(x["High"]),
                 "l": float(x["Low"]), "c": float(x["Close"]), "v": _i(x.get("Volume")) or 0}
                for x in rows]
        prev = bars[-2]["c"] if len(bars) > 1 else bars[0]["o"]
        last = bars[-1]["c"]
        return {"symbol": symbol.upper(), "range": rng.upper(), "interval": interval,
                "currency": "USD", "prevClose": prev, "bars": bars,
                "last": {"price": last, "change": last - prev,
                         "pct": (last / prev - 1) * 100 if prev else 0}}
    except Exception:
        return None


def _f(x) -> float | None:
    try:
        return float(x)
    except Exception:
        return None


def _i(x) -> int | None:
    try:
        return int(float(x))
    except Exception:
        return None
