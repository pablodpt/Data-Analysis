"""Screener endpoints: filter a liquid-US universe by price & fundamentals."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .. import demo
from ..providers import stooq, yahoo
from . import allow_demo, demo_ok, live_ok, ok, unavailable, want_live

router = APIRouter(prefix="/api/screener", tags=["screener"])

# Bulk-fetch guard: stay gentle with free tiers (also skips Finnhub here —
# 100+ quotes would blow its 60/min free quota; Yahoo/Stooq absorb it).
_SEM = asyncio.Semaphore(12)


class ScreenReq(BaseModel):
    minPrice: float | None = None
    maxPrice: float | None = None
    minMktCapB: float | None = None
    maxMktCapB: float | None = None
    minPE: float | None = None
    maxPE: float | None = None
    minDivY: float | None = None
    maxDivY: float | None = None
    minChgPct: float | None = None
    maxChgPct: float | None = None
    minVolumeM: float | None = None
    minWeek52Pos: float | None = None  # 0..1
    maxWeek52Pos: float | None = None
    sectors: list[str] = Field(default_factory=list)
    sort: str = "mktCap"
    dir: str = "desc"
    limit: int = 50


_META: dict[str, dict] | None = None


def _meta() -> dict[str, dict]:
    global _META
    if _META is None:
        _META = {e["symbol"]: e for e in demo.defaults()["screener_universe"]}
    return _META


def _universe() -> list[dict]:
    return demo.defaults()["screener_universe"]


@router.get("/universe")
async def get_universe():
    u = _universe()
    sectors = sorted({e["sector"] for e in u})
    return live_ok({"count": len(u), "sectors": sectors, "symbols": u}, "local-index")


async def _bulk_row(symbol: str) -> tuple[dict | None, str]:
    """Live row: Yahoo quote+info, Stooq fallback. No Finnhub (bulk quota)."""
    s = symbol.upper()
    meta = _meta().get(s, {})
    async with _SEM:
        q = await asyncio.to_thread(yahoo.quote, s)
        src = "yahoo"
        if not q or not q.get("price"):
            q = await stooq.quote(s)
            src = "stooq"
        if not q or not q.get("price"):
            return None, ""
        info = await asyncio.to_thread(yahoo.info, s) or {}
    hi, lo = info.get("week52High"), info.get("week52Low")
    px = q["price"]
    pos = (px - lo) / (hi - lo) if hi and lo and hi > lo else None
    sector = info.get("sector")
    return {
        "symbol": s,
        "name": info.get("name") or meta.get("name") or demo.profile_name(s),
        "sector": sector if sector not in (None, "—", "") else meta.get("sector", "—"),
        "price": px, "change": q.get("change"), "pct": q.get("pct"),
        "volume": q.get("volume"),
        "mktCap": info.get("mktCap") or q.get("mktCap"),
        "pe": info.get("pe"), "divYield": info.get("divYield"),
        "beta": info.get("beta"),
        "week52High": hi, "week52Low": lo,
        "week52pos": round(max(0.0, min(1.0, pos)), 4) if pos is not None else None,
        "source": src,
    }, src


def _demo_row(symbol: str) -> dict:
    meta = _meta().get(symbol.upper(), {})
    q = demo.gen_quote(symbol)
    hi, lo = q["week52High"], q["week52Low"]
    pos = (q["price"] - lo) / (hi - lo) if hi and lo and hi > lo else None
    return {
        "symbol": symbol.upper(),
        "name": meta.get("name") or q["name"],
        "sector": meta.get("sector", "—"),
        "price": q["price"], "change": q["change"], "pct": q["pct"],
        "volume": q["volume"], "mktCap": q["mktCap"],
        "pe": q["pe"], "divYield": q["divYield"], "beta": None,
        "week52High": hi, "week52Low": lo,
        "week52pos": round(max(0.0, min(1.0, pos)), 4) if pos is not None else None,
        "source": "simulated",
    }


def _in_range(v: float | None, lo: float | None, hi: float | None, scale: float = 1.0) -> bool:
    if lo is None and hi is None:
        return True
    if v is None:  # N/A fails any active bound (e.g. ETFs have no P/E)
        return False
    v = v / scale
    return (lo is None or v >= lo) and (hi is None or v <= hi)


def _apply_filters(rows: list[dict], r: ScreenReq) -> list[dict]:
    sectors = {s for s in r.sectors} if r.sectors else None
    out = []
    for x in rows:
        if sectors and x["sector"] not in sectors:
            continue
        if not _in_range(x["price"], r.minPrice, r.maxPrice):
            continue
        if not _in_range(x["mktCap"], r.minMktCapB, r.maxMktCapB, 1e9):
            continue
        if not _in_range(x["pe"], r.minPE, r.maxPE):
            continue
        if not _in_range(x["divYield"], r.minDivY, r.maxDivY):
            continue
        if not _in_range(x["pct"], r.minChgPct, r.maxChgPct):
            continue
        if not _in_range(x["volume"], r.minVolumeM, None, 1e6):
            continue
        if not _in_range(x["week52pos"], r.minWeek52Pos, r.maxWeek52Pos):
            continue
        out.append(x)
    return out


SORT_KEYS = {"symbol", "price", "pct", "volume", "mktCap", "pe", "divYield", "week52pos", "beta"}


def _apply_sort(rows: list[dict], r: ScreenReq) -> list[dict]:
    key = r.sort if r.sort in SORT_KEYS else "mktCap"
    rev = (r.dir or "desc").lower() != "asc"
    if key == "symbol":
        return sorted(rows, key=lambda x: x["symbol"], reverse=rev)
    noval = [x for x in rows if x.get(key) is None]
    val = sorted([x for x in rows if x.get(key) is not None],
                 key=lambda x: x[key], reverse=rev)
    return val + noval  # N/A always last


@router.post("/run")
async def run_screen(req: ScreenReq):
    u = _universe()
    rows: list[dict] = []
    if want_live():
        res = await asyncio.gather(*[_bulk_row(e["symbol"]) for e in u])
        for e, (row, _src) in zip(u, res):
            if row:
                rows.append(row)
            elif allow_demo():
                rows.append(_demo_row(e["symbol"]))
    else:
        if not allow_demo():
            raise unavailable("screener")
        rows = [_demo_row(e["symbol"]) for e in u]

    live_srcs = sorted({x["source"] for x in rows if x["source"] != "simulated"})
    n_sim = sum(1 for x in rows if x["source"] == "simulated")
    if live_srcs and not n_sim:
        mode, src = "live", "+".join(live_srcs)
    elif not live_srcs:
        mode, src = "demo", "simulated"
    else:
        mode, src = "mixed", "+".join(live_srcs + ["simulated"])

    rows = _apply_sort(_apply_filters(rows, req), req)
    total = len(rows)
    rows = rows[: max(1, min(req.limit or 50, 200))]
    return ok({"asOf": datetime.now(timezone.utc).isoformat(),
               "universe": len(u), "count": total, "returned": len(rows),
               "rows": rows}, mode, src)
