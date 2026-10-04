"""Market endpoints: overview (indices) and movers."""
from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Query

from .. import config, demo
from ..cache import get as cache_get, put as cache_put
from ..providers import stooq
from . import allow_demo, demo_ok, live_ok, ok, unavailable, want_live

router = APIRouter(prefix="/api/market", tags=["market"])

SCREENER_IDS = {"gainers": "day_gainers", "losers": "day_losers", "actives": "day_most_active"}

# Upper bound for bulk upstream fan-out: slow symbols degrade to demo
# instead of hanging the whole response (free tiers can stall).
BULK_TIMEOUT = 14


def _ms(t0: float) -> int:
    return int((time.time() - t0) * 1000)


async def _gather_best(coros, timeout: float = BULK_TIMEOUT) -> list:
    """Like asyncio.gather, but slow/failed entries become None (never raises)."""
    if not coros:
        return []
    tasks = [asyncio.ensure_future(c) for c in coros]
    try:
        _done, pending = await asyncio.wait(tasks, timeout=timeout)
    except Exception:
        pending = set(tasks)
    if pending:
        for x in pending:
            x.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
    out = []
    for x in tasks:
        try:
            out.append(x.result() if x.done() and not x.cancelled() else None)
        except Exception:
            out.append(None)
    return out


@router.get("/overview")
async def overview():
    t0 = time.time()
    hit = cache_get("mkt:overview")
    if hit is not None:
        return hit
    if want_live():
        idx_defs = demo.defaults()["indices"]
        n = len(idx_defs)
        res = await _gather_best(
            [stooq.quote(d["symbol"]) for d in idx_defs]
            + [stooq.history(d["symbol"], "1M", "1d") for d in idx_defs]
        )
        quotes, hists = res[:n], res[n:]
        rows, n_live = [], 0
        for d, q, h in zip(idx_defs, quotes, hists):
            if q and q.get("price"):
                n_live += 1
                spark = [b["c"] for b in (h["bars"][-30:] if h else [])]
                rows.append({"symbol": d["symbol"], "label": d["label"],
                             "price": q["price"], "change": q.get("change"),
                             "pct": q.get("pct"), "spark": spark})
            elif allow_demo():
                dq = demo.gen_quote(d["symbol"])
                dh = demo.gen_history(d["symbol"], "1M")["bars"]
                rows.append({"symbol": d["symbol"], "label": d["label"] + " *",
                             "price": dq["price"], "change": dq["change"],
                             "pct": dq["pct"], "spark": [b["c"] for b in dh[-30:]]})
        if rows:
            mode = "live" if n_live == len(rows) else ("demo" if n_live == 0 else "mixed")
            src = "stooq" if n_live == len(rows) else ("simulated" if n_live == 0 else "stooq+simulated")
            resp = ok({"asOf": datetime.now(timezone.utc).isoformat(),
                       "indices": rows, "breadth": None, "tookMs": _ms(t0)}, mode, src)
            cache_put("mkt:overview", resp, config.TTL_OVERVIEW)
            return resp
    if allow_demo():
        resp = demo_ok({**demo.gen_overview(), "tookMs": _ms(t0)})
        cache_put("mkt:overview", resp, config.TTL_OVERVIEW)
        return resp
    raise unavailable("market overview")


@router.get("/movers")
async def movers(group: str = Query("gainers"), limit: int = 10):
    t0 = time.time()
    group = group if group in SCREENER_IDS else "gainers"
    limit = max(1, min(limit, 25))
    key = f"mkt:movers:{group}:{limit}"
    hit = cache_get(key)
    if hit is not None:
        return hit
    if want_live():
        try:
            rows = await asyncio.wait_for(_yahoo_screener(group, limit), timeout=8)
        except Exception:
            rows = None
        if rows:
            resp = live_ok({"group": group, "asOf": datetime.now(timezone.utc).isoformat(),
                            "rows": rows, "tookMs": _ms(t0)}, "yahoo-screener")
            cache_put(key, resp, config.TTL_OVERVIEW)
            return resp
        rows = await _universe_quotes(group, limit)
        if rows:
            resp = live_ok({"group": group, "asOf": datetime.now(timezone.utc).isoformat(),
                            "rows": rows, "tookMs": _ms(t0)}, "stooq")
            cache_put(key, resp, config.TTL_OVERVIEW)
            return resp
    if allow_demo():
        resp = demo_ok({**demo.gen_movers(group, limit), "tookMs": _ms(t0)})
        cache_put(key, resp, config.TTL_OVERVIEW)
        return resp
    raise unavailable("movers")


async def _yahoo_screener(group: str, limit: int) -> list[dict] | None:
    try:
        async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT) as c:
            r = await c.get("https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved",
                            params={"id": SCREENER_IDS[group], "count": limit},
                            headers={"User-Agent": config.USER_AGENT})
        if r.status_code != 200:
            return None
        out = []
        for q in r.json()["finance"]["result"][0]["quotes"][:limit]:
            out.append({"symbol": q.get("symbol"), "name": q.get("shortName") or q.get("longName") or q.get("symbol"),
                        "price": q.get("regularMarketPrice"), "change": q.get("regularMarketChange"),
                        "pct": q.get("regularMarketChangePercent"), "volume": q.get("regularMarketVolume")})
        return out or None
    except Exception:
        return None


async def _universe_quotes(group: str, limit: int) -> list[dict] | None:
    try:
        syms = demo.defaults()["movers_universe"]
        quotes = await _gather_best([stooq.quote(s) for s in syms])
        rows = []
        for s, q in zip(syms, quotes):
            if q and q.get("price"):
                rows.append({"symbol": s, "name": demo.profile_name(s),
                             "price": q["price"], "change": q.get("change"),
                             "pct": q.get("pct") or 0, "volume": q.get("volume") or 0})
        if len(rows) < 5:
            return None
        if group == "losers":
            rows.sort(key=lambda x: x["pct"])
        elif group == "actives":
            rows.sort(key=lambda x: x["volume"], reverse=True)
        else:
            rows.sort(key=lambda x: x["pct"], reverse=True)
        return rows[:limit]
    except Exception:
        return None
