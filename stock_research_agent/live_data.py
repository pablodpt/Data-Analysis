# -*- coding: utf-8 -*-
"""
live_data.py — Live price quotes via Stooq's free CSV endpoint (no API key).

    https://stooq.com/q/l/?s=aapl.us&f=sd2t2ohlcv&h&e=csv
    -> Symbol,Date,Time,Open,High,Low,Close,Volume

Design goals:
  * stdlib only (urllib), one small HTTP call per ticker
  * defensive: unknown symbol, N/D cells, bad dates, blocked network
    -> always returns None, caller falls back to the KB snapshot
  * per-process cache keyed by (symbol, day) so re-runs don't re-fetch
  * EU/UK ticker exchange suffixes mapped to Stooq's suffixes
    (.MC->.es, .PA->.fr, .DE->.de, .L->.uk, .MI->.mi, .AX->.nl, .SW->.ch)
"""
from __future__ import annotations

import csv
import io
import time
import urllib.request
from typing import Any, Dict, List, Optional

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
_URL = "https://stooq.com/q/l/?s={sym}&f=sd2t2ohlcv&h&e=csv"
_TIMEOUT = 10  # seconds
_GAP = 0.15    # polite pause between candidate symbols

_EXCHANGE_MAP = {
    "MC": "es",   # Madrid
    "PA": "fr",   # Paris
    "DE": "de",   # Frankfurt / XETRA
    "L": "uk",    # London
    "MI": "mi",   # Milan
    "AX": "nl",   # Amsterdam
    "NL": "nl",
    "SW": "ch",   # Zurich
    "UK": "uk",
}

_cache: Dict[str, Optional[Dict[str, Any]]] = {}


def _candidates(ticker: str) -> List[str]:
    """Ordered Stooq symbol candidates for a KB ticker like 'ITX.MC' or 'BRK.A'."""
    t = ticker.strip().upper()
    base, dot, exch = t.partition(".")
    out: List[str] = []
    if not dot:
        out += [f"{base.lower()}.us", base.lower()]
    elif exch in _EXCHANGE_MAP:
        out += [f"{base.lower()}.{_EXCHANGE_MAP[exch]}",
                f"{base.lower()}.{exch.lower()}", base.lower()]
    elif len(exch) <= 2:
        # share class (BRK.A) or unknown short suffix — try US dash form first
        out += [f"{base.lower()}-{exch.lower()}.us",
                f"{base.lower()}.{exch.lower()}.us",
                f"{base.lower()}.us", base.lower()]
    else:
        out += [f"{base.lower()}.{exch.lower()}", base.lower()]
    seen, uniq = set(), []
    for c in out:
        if c and c not in seen:
            seen.add(c)
            uniq.append(c)
    return uniq


def _fetch_csv(symbol: str) -> Optional[str]:
    req = urllib.request.Request(_URL.format(sym=urllib.request.quote(symbol)),
                                 headers={"User-Agent": _UA,
                                          "Referer": "https://stooq.com/"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
        return r.read(8192).decode("utf-8", "replace")


def _parse(row: Dict[str, str], symbol: str) -> Optional[Dict[str, Any]]:
    try:
        close = float(row.get("Close", ""))
    except (ValueError, TypeError):
        return None
    if close <= 0:
        return None

    def _f(key: str) -> Optional[float]:
        try:
            return float(row.get(key, ""))
        except (ValueError, TypeError):
            return None

    raw_d = (row.get("Date") or "").replace("-", "")
    raw_t = (row.get("Time") or "").replace(":", "")
    if len(raw_d) == 8 and raw_d.isdigit():
        date = f"{raw_d[:4]}-{raw_d[4:6]}-{raw_d[6:]}"
    else:
        date = row.get("Date") or ""
    if len(raw_t) == 4 and raw_t.isdigit():
        t = f"{raw_t[:2]}:{raw_t[2:]}"
    elif raw_t:
        t = row.get("Time") or ""
    else:
        t = ""
    return dict(symbol=row.get("Symbol") or symbol, date=date, time=t,
                open=_f("Open"), high=_f("High"), low=_f("Low"),
                close=close, volume=_f("Volume"))


def get_quote(ticker: str, currency: str = "USD",
              force: bool = False) -> Optional[Dict[str, Any]]:
    """Fetch the latest quote for a KB ticker. None on any failure."""
    if not ticker:
        return None
    if not force and ticker in _cache:
        return _cache[ticker]
    last_err = None
    for sym in _candidates(ticker):
        try:
            body = _fetch_csv(sym)
        except Exception as e:  # noqa: BLE001 — any network/parse failure
            last_err = e
            continue
        try:
            rows = [r for r in csv.DictReader(io.StringIO(body)) if r]
        except csv.Error:
            continue
        for row in rows:
            # tolerant match: stooq may echo the symbol with different
            # dash/dot casing (request 'brk-a.us' -> 'BRK.A.US')
            got = (row.get("Symbol") or "").upper().replace("-", "").replace(".", "")
            if got == sym.upper().replace("-", "").replace(".", ""):
                q = _parse(row, sym)
                if q:
                    q["source"] = "stooq"
                    q["currency"] = currency
                    _cache[ticker] = q
                    return q
        time.sleep(_GAP)
    _cache[ticker] = None  # remember the miss for this process
    return None


def clear_cache() -> None:
    _cache.clear()
