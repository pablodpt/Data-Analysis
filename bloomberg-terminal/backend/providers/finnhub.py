"""Finnhub provider — free tier (~60 calls/min). Needs FINNHUB_API_KEY."""
from __future__ import annotations

from datetime import date, timedelta

import httpx

from .. import config
from ..cache import cached

BASE = "https://finnhub.io/api/v1"


def _enabled() -> bool:
    return bool(config.FINNHUB_API_KEY)


async def _get(path: str, **params):
    async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT) as c:
        r = await c.get(BASE + path, params={"token": config.FINNHUB_API_KEY, **params},
                        headers={"User-Agent": config.USER_AGENT})
    if r.status_code != 200:
        return None
    try:
        return r.json()
    except Exception:
        return None


@cached(config.TTL_QUOTE, lambda s: f"fhq:{s.upper()}")
async def quote(symbol: str) -> dict | None:
    if not _enabled():
        return None
    try:
        j = await _get("/quote", symbol=symbol.upper())
        if not j or not j.get("c"):
            return None
        px, prev = float(j["c"]), float(j.get("pc") or j["c"])
        return {"symbol": symbol.upper(), "currency": "USD", "price": px,
                "change": px - prev, "pct": (px / prev - 1) * 100 if prev else 0,
                "open": j.get("o"), "high": j.get("h"), "low": j.get("l"),
                "prevClose": prev}
    except Exception:
        return None


@cached(config.TTL_NEWS, lambda s: f"fhn:{s.upper()}")
async def company_news(symbol: str, days: int = 7) -> list[dict] | None:
    if not _enabled():
        return None
    try:
        to = date.today()
        frm = to - timedelta(days=days)
        j = await _get("/company-news", symbol=symbol.upper(),
                       **{"from": frm.isoformat(), "to": to.isoformat()})
        if not j:
            return None
        from datetime import datetime, timezone
        out = []
        for a in j[:30]:
            ts = a.get("datetime")
            pub = datetime.fromtimestamp(ts, timezone.utc).isoformat() if ts else ""
            out.append({"title": a.get("headline", "—"), "publisher": a.get("source", "Finnhub"),
                        "symbol": symbol.upper(), "published": pub,
                        "link": a.get("url", ""), "summary": (a.get("summary") or "")[:300]})
        return out or None
    except Exception:
        return None


@cached(config.TTL_NEWS, lambda: "fhm")
async def market_news() -> list[dict] | None:
    if not _enabled():
        return None
    try:
        j = await _get("/news", category="general")
        if not j:
            return None
        from datetime import datetime, timezone
        out = []
        for a in j[:30]:
            ts = a.get("datetime")
            pub = datetime.fromtimestamp(ts, timezone.utc).isoformat() if ts else ""
            out.append({"title": a.get("headline", "—"), "publisher": a.get("source", "Finnhub"),
                        "symbol": None, "published": pub,
                        "link": a.get("url", ""), "summary": (a.get("summary") or "")[:300]})
        return out or None
    except Exception:
        return None


@cached(config.TTL_ECON, lambda d=14: f"fhc:{d}")
async def econ_calendar(days: int = 14) -> list[dict] | None:
    if not _enabled():
        return None
    try:
        to = date.today()
        frm = to - timedelta(days=3)
        j = await _get("/calendar/economic")
        if not j or "economicCalendar" not in j:
            return None
        end = (to + timedelta(days=days)).isoformat()
        out = []
        for e in j["economicCalendar"]:
            d = (e.get("time") or "")[:10]
            if d < frm.isoformat() or d > end:
                continue
            out.append({"date": d, "time": (e.get("time") or "")[11:16] or "—",
                        "name": e.get("event", "—"), "country": e.get("country", "US"),
                        "importance": {"high": 3, "medium": 2, "low": 1}.get(
                            (e.get("impact") or "").lower(), 2),
                        "forecast": e.get("estimate"), "previous": e.get("prev"),
                        "actual": e.get("actual") if e.get("actual") not in (None, "") else None})
        return sorted(out, key=lambda x: (x["date"], x["time"])) or None
    except Exception:
        return None
