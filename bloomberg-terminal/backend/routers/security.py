"""Security endpoints: search, quote(s), history, profile, financials, earnings, filings."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Query
from pydantic import BaseModel

from .. import config, demo
from ..providers import finnhub, stooq, yahoo, sec
from . import allow_demo, demo_ok, live_ok, unavailable, want_live

router = APIRouter(prefix="/api", tags=["security"])


class QuotesReq(BaseModel):
    symbols: list[str]


async def _live_quote(symbol: str) -> tuple[dict | None, str]:
    s = symbol.upper()
    if config.FINNHUB_API_KEY:
        q = await finnhub.quote(s)
        if q:
            q["name"] = demo.profile_name(s)
            q["asOf"] = datetime.now(timezone.utc).isoformat()
            return q, "finnhub"
    q = await asyncio.to_thread(yahoo.quote, s)
    if q:
        q["name"] = demo.profile_name(s)
        return q, "yahoo"
    q = await stooq.quote(s)
    if q:
        q["name"] = demo.profile_name(s)
        return q, "stooq"
    return None, ""


@router.get("/search")
async def search(q: str = Query(min_length=1), limit: int = 10):
    if want_live():
        res = await asyncio.to_thread(yahoo.search, q)
        if res:
            return live_ok({"query": q, "results": res[:limit]}, "yahoo")
    local = demo.search_local(q, limit)
    return live_ok({"query": q, "results": local}, "local-index")


@router.get("/quote")
async def quote(symbol: str):
    if want_live():
        q, src = await _live_quote(symbol)
        if q:
            return live_ok(q, src)
    if allow_demo():
        return demo_ok(demo.gen_quote(symbol))
    raise unavailable("quote")


@router.post("/quotes")
async def quotes(req: QuotesReq):
    syms = [s.upper() for s in req.symbols[:40]]
    out, modes = [], set()
    if want_live():
        res = await asyncio.gather(*[_live_quote(s) for s in syms])
        for s, (q, src) in zip(syms, res):
            if q:
                out.append({**q, "source": src})
                modes.add("live")
            elif allow_demo():
                out.append({**demo.gen_quote(s), "source": "simulated"})
                modes.add("demo")
    else:
        if not allow_demo():
            raise unavailable("quotes")
        out = [{**demo.gen_quote(s), "source": "simulated"} for s in syms]
        modes = {"demo"}
    mode = "live" if modes == {"live"} else ("demo" if modes == {"demo"} else "mixed")
    return {"mode": mode, "quotes": out}


@router.get("/history")
async def history(symbol: str, range: str = "1Y", interval: str = "1d"):
    s = symbol.upper()
    if want_live():
        h = await asyncio.to_thread(yahoo.history, s, range, interval)
        if h:
            return live_ok(h, "yahoo")
        if range.upper() not in ("1D", "5D"):
            h = await stooq.history(s, range, interval)
            if h:
                return live_ok(h, "stooq")
    if allow_demo():
        return demo_ok(demo.gen_history(s, range, interval))
    raise unavailable("history")


@router.get("/profile")
async def profile(symbol: str):
    s = symbol.upper()
    if want_live():
        p = await asyncio.to_thread(yahoo.info, s)
        if p and p.get("name"):
            return live_ok(p, "yahoo")
    if allow_demo():
        return demo_ok(demo.gen_profile(s))
    raise unavailable("profile")


@router.get("/financials")
async def financials(symbol: str, statement: str = "income", period: str = "annual"):
    statement = statement if statement in ("income", "balance", "cashflow") else "income"
    period = period if period in ("annual", "quarterly") else "annual"
    s = symbol.upper()
    if want_live():
        f = await asyncio.to_thread(yahoo.financials, s, statement, period)
        if f:
            return live_ok(f, "yahoo")
    if allow_demo():
        return demo_ok(demo.gen_financials(s, statement, period))
    raise unavailable("financials")


@router.get("/earnings")
async def earnings(symbol: str):
    s = symbol.upper()
    if want_live():
        e = await asyncio.to_thread(yahoo.earnings, s)
        if e and (e.get("past") or e.get("upcoming")):
            return live_ok(e, "yahoo")
    if allow_demo():
        return demo_ok(demo.gen_earnings(s))
    raise unavailable("earnings")


@router.get("/filings")
async def filings(symbol: str, limit: int = 12):
    s = symbol.upper()
    if want_live():
        f = await sec.filings(s, limit)
        if f:
            return live_ok({"symbol": s, "filings": f}, "sec-edgar")
    if allow_demo():
        # plausible recent filing dates ( Wednesdays after quarter-ends )
        from datetime import date, timedelta
        import random

        r = random.Random(demo.seed_of("fil", s))
        t = date.today()
        forms = ["10-Q", "8-K", "10-K", "8-K", "DEF 14A", "10-Q", "8-K", "4"]
        out = []
        for i, form in enumerate(forms[:limit]):
            d = t - timedelta(days=r.randrange(15, 400))
            out.append({"form": form, "date": d.isoformat(),
                        "link": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={s}&type={form}"})
        out.sort(key=lambda x: x["date"], reverse=True)
        return demo_ok({"symbol": s, "filings": out})
    raise unavailable("filings")
