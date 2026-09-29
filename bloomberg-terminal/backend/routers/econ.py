"""Macro endpoints: FRED indicators, series history, economic calendar."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Query

from .. import demo
from ..providers import finnhub, fred
from . import allow_demo, demo_ok, live_ok, ok, unavailable, want_live

router = APIRouter(prefix="/api/econ", tags=["econ"])


@router.get("/indicators")
async def indicators():
    defs = demo.defaults()["fred_series"]
    if want_live():
        res = await asyncio.gather(*[fred.series(d["id"]) for d in defs])
        rows, n_live = [], 0
        for d, r in zip(defs, res):
            if r and len(r["points"]) >= 2:
                n_live += 1
                pts = r["points"]
                v, p = pts[-1]["v"], pts[-2]["v"]
                rows.append({"id": d["id"], "label": d["label"], "unit": d["unit"],
                             "value": round(v, 3), "prev": round(p, 3),
                             "change": round(v - p, 3),
                             "pct": round((v / p - 1) * 100, 3) if p else 0,
                             "spark": [x["v"] for x in pts[-24:]],
                             "asOf": pts[-1]["t"]})
            elif allow_demo():
                rows.append(_demo_indicator(d))
        if rows:
            mode = "live" if n_live == len(rows) else ("demo" if n_live == 0 else "mixed")
            src = "fred" if n_live == len(rows) else ("simulated" if n_live == 0 else "fred+simulated")
            return ok({"asOf": datetime.now(timezone.utc).isoformat(),
                       "indicators": rows}, mode, src)
    if allow_demo():
        return demo_ok(demo.gen_indicators())
    raise unavailable("indicators")


@router.get("/series")
async def series(id: str = Query(min_length=1), years: int = 10):
    sid = id.upper()
    if want_live():
        r = await fred.series(sid)
        if r and r["points"]:
            pts = r["points"]
            if years and years < 60:
                pts = pts[-(252 if sid in ("DGS10", "DGS2", "T10Y2Y", "DEXUSEU", "VIXCLS", "DFF", "SOFR") else 12 * years):]
                if sid in ("DGS10", "DGS2", "T10Y2Y", "DEXUSEU", "VIXCLS", "DFF", "SOFR"):
                    pts = r["points"][-(252 * years):]
            meta = next((d for d in demo.defaults()["fred_series"] if d["id"] == sid),
                         {"label": sid, "unit": "", "freq": "D"})
            return live_ok({"id": sid, "label": meta["label"], "unit": meta.get("unit", ""),
                            "freq": meta.get("freq", "D"), "points": pts}, "fred")
    if allow_demo():
        d = demo.gen_series(sid, years)
        if d:
            return demo_ok(d)
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=f"Unknown series {sid}")


@router.get("/calendar")
async def calendar(days: int = 14):
    days = max(1, min(days, 60))
    if want_live():
        cal = await finnhub.econ_calendar(days)
        if cal:
            return live_ok({"asOf": datetime.now(timezone.utc).isoformat(),
                            "events": cal}, "finnhub")
    if allow_demo():
        return demo_ok(demo.gen_calendar(days))
    raise unavailable("calendar")


def _demo_indicator(d: dict) -> dict:
    full = demo.gen_indicators()["indicators"]
    return next(x for x in full if x["id"] == d["id"])
