"""Market endpoints: overview (indices) and movers."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Query

from .. import config, demo
from ..providers import stooq
from . import allow_demo, demo_ok, live_ok, ok, unavailable, want_live

router = APIRouter(prefix="/api/market", tags=["market"])

SCREENER_IDS = {"gainers": "day_gainers", "losers": "day_losers", "actives": "day_most_active"}


@router.get("/overview")
async def overview():
    if want_live():
        idx_defs = demo.defaults()["indices"]
        # one combined gather: quotes + histories in parallel (halves worst-case wait)
        quotes, hists = await asyncio.gather(
            asyncio.gather(*[stooq.quote(d["symbol"]) for d in idx_defs]),
            asyncio.gather(*[stooq.history(d["symbol"], "1M", "1d") for d in idx_defs]),
        )
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
            return ok({"asOf": datetime.now(timezone.utc).isoformat(),
                       "indices": rows, "breadth": None}, mode, src)
    if allow_demo():
        return demo_ok(demo.gen_overview())
    raise unavailable("market overview")


@router.get("/movers")
async def movers(group: str = Query("gainers"), limit: int = 10):
    group = group if group in SCREENER_IDS else "gainers"
    limit = max(1, min(limit, 25))
    if want_live():
        rows = await _yahoo_screener(group, limit)
        if rows:
            return live_ok({"group": group, "asOf": datetime.now(timezone.utc).isoformat(),
                            "rows": rows}, "yahoo-screener")
        rows = await _universe_quotes(group, limit)
        if rows:
            return live_ok({"group": group, "asOf": datetime.now(timezone.utc).isoformat(),
                            "rows": rows}, "stooq")
    if allow_demo():
        return demo_ok(demo.gen_movers(group, limit))
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
        quotes = await asyncio.gather(*[stooq.quote(s) for s in syms])
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
