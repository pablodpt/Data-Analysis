"""Yahoo Finance provider (via yfinance + Yahoo search API). Keyless, unofficial."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from .. import config
from ..cache import cached

RANGE_MAP = {"1D": "1d", "5D": "5d", "1M": "1mo", "3M": "3mo", "6M": "6mo",
             "1Y": "1y", "2Y": "2y", "5Y": "5y", "10Y": "10y", "YTD": "ytd", "MAX": "max"}
INT_MAP = {"1D": "5m", "5D": "15m"}


def _tk(symbol: str):
    import yfinance as yf  # lazy: import only when live mode runs

    return yf.Ticker(symbol)


@cached(config.TTL_QUOTE, lambda s: f"yq:{s.upper()}")
def quote(symbol: str) -> dict | None:
    try:
        t = _tk(symbol)
        fi = t.fast_info
        price = float(fi.last_price)
        prev = float(fi.previous_close)
        if not price or not prev:
            return None
        return {
            "symbol": symbol.upper(), "currency": getattr(fi, "currency", "USD") or "USD",
            "price": price, "change": price - prev, "pct": (price / prev - 1) * 100,
            "open": _f(fi.open), "high": _f(fi.day_high), "low": _f(fi.day_low),
            "prevClose": prev, "volume": _i(fi.last_volume),
            "mktCap": _i(getattr(fi, "market_cap", 0)),
            "week52High": _f(fi.year_high), "week52Low": _f(fi.year_low),
            "asOf": datetime.now(timezone.utc).isoformat(),
        }
    except Exception:
        return None


@cached(config.TTL_HISTORY, lambda s, r="1Y", i="1d": f"yh:{s.upper()}:{r}:{i}")
def history(symbol: str, rng: str = "1Y", interval: str = "1d") -> dict | None:
    try:
        iv = INT_MAP.get(rng.upper(), interval if interval in ("1d", "1wk", "1mo") else "1d")
        df = _tk(symbol).history(period=RANGE_MAP.get(rng.upper(), "1y"),
                                 interval=iv, auto_adjust=False)
        if df is None or df.empty:
            return None
        bars = []
        for ts, row in df.iterrows():
            try:
                iso = ts.tz_convert("UTC").isoformat() if getattr(ts, "tzinfo", None) else ts.isoformat()
            except Exception:
                iso = str(ts)
            bars.append({"t": iso[:19] if iv != "1d" and "T" in iso else iso[:10],
                         "o": _f(row.get("Open")), "h": _f(row.get("High")),
                         "l": _f(row.get("Low")), "c": _f(row.get("Close")),
                         "v": _i(row.get("Volume"))})
        prev = bars[0]["o"]
        last = bars[-1]["c"]
        return {"symbol": symbol.upper(), "range": rng.upper(), "interval": iv,
                "currency": "USD", "prevClose": prev, "bars": bars,
                "last": {"price": last, "change": last - prev,
                         "pct": (last / prev - 1) * 100 if prev else 0}}
    except Exception:
        return None


@cached(config.TTL_PROFILE, lambda s: f"yi:{s.upper()}")
def info(symbol: str) -> dict | None:
    try:
        i = _tk(symbol).get_info() or {}
        if not i or not i.get("shortName" if "shortName" in i else "longName", None) and not i.get("regularMarketPrice"):
            # yfinance sometimes returns {} on failure
            if not i:
                return None
        px = _f(i.get("regularMarketPrice")) or _f(i.get("currentPrice"))
        prev = _f(i.get("regularMarketPreviousClose")) or _f(i.get("previousClose"))
        return {
            "symbol": symbol.upper(), "name": i.get("longName") or i.get("shortName") or symbol.upper(),
            "sector": i.get("sector", "—"), "industry": i.get("industry", "—"),
            "exchange": i.get("exchange", "—"), "currency": i.get("currency", "USD"),
            "employees": i.get("fullTimeEmployees"), "website": i.get("website", "—"),
            "description": i.get("longBusinessSummary", "—"),
            "price": px, "change": (px - prev) if px and prev else None,
            "pct": ((px / prev - 1) * 100) if px and prev else None,
            "mktCap": i.get("marketCap"), "pe": i.get("trailingPE"),
            "eps": i.get("trailingEps"), "divYield": (i.get("dividendYield") or 0) * 100 if i.get("dividendYield") else None,
            "week52High": i.get("fiftyTwoWeekHigh"), "week52Low": i.get("fiftyTwoWeekLow"),
        }
    except Exception:
        return None


@cached(config.TTL_FINANCIALS, lambda s, st="income", p="annual": f"yf:{s.upper()}:{st}:{p}")
def financials(symbol: str, statement: str = "income", period: str = "annual") -> dict | None:
    try:
        t = _tk(symbol)
        q = period == "quarterly"
        df = {"income": t.quarterly_income_stmt if q else t.income_stmt,
              "balance": t.quarterly_balance_sheet if q else t.balance_sheet,
              "cashflow": t.quarterly_cashflow if q else t.cashflow}[statement]
        if df is None or getattr(df, "empty", True):
            return None
        df = df.iloc[:, :8] if q else df.iloc[:, :4]
        dates = [str(c)[:10] for c in df.columns][::-1]
        rows = [{"label": str(idx), "values": [round(float(v) / 1e6, 1) if v == v else None
                                               for v in reversed(list(df.loc[idx].values))]}
                for idx in df.index[:28]]
        return {"symbol": symbol.upper(), "statement": statement, "period": period,
                "currency": "USD", "scale": "millions", "dates": dates, "rows": rows}
    except Exception:
        return None


@cached(config.TTL_FINANCIALS, lambda s: f"ye:{s.upper()}")
def earnings(symbol: str) -> dict | None:
    try:
        cal = _tk(symbol).get_earnings_dates(limit=8)
        if cal is None or getattr(cal, "empty", True):
            return None
        past, upcoming = [], []
        now = datetime.now(timezone.utc).date().isoformat()
        for ts, row in cal.iterrows():
            d = str(ts)[:10]
            e = {"date": d, "estimate": _f(row.get("EPS Estimate")), "actual": _f(row.get("Reported EPS"))}
            if e["actual"] is not None and e["estimate"]:
                e["surprisePct"] = round((e["actual"] / e["estimate"] - 1) * 100, 2)
            (past if d < now else upcoming).append(e)
        return {"symbol": symbol.upper(), "past": past[:6], "upcoming": upcoming[:4]}
    except Exception:
        return None


@cached(config.TTL_NEWS, lambda s: f"yn:{s.upper()}")
def news(symbol: str) -> list[dict] | None:
    try:
        items = _tk(symbol).news or []
        out = []
        for a in items[:25]:
            c = a.get("content", a)
            out.append({"title": c.get("title", "—"),
                        "publisher": c.get("provider", {}).get("displayName", "Yahoo") if isinstance(c.get("provider"), dict) else "Yahoo",
                        "symbol": symbol.upper(),
                        "published": c.get("pubDate") or c.get("displayTime") or "",
                        "link": c.get("canonicalUrl", {}).get("url", "") if isinstance(c.get("canonicalUrl"), dict) else c.get("link", ""),
                        "summary": c.get("summary", "")[:300]})
        return out or None
    except Exception:
        return None


@cached(config.TTL_SEARCH, lambda q: f"ys:{q.lower()}")
def search(q: str) -> list[dict] | None:
    try:
        r = httpx.get("https://query1.finance.yahoo.com/v1/finance/search",
                      params={"q": q, "quotesCount": 10, "newsCount": 0},
                      headers={"User-Agent": config.USER_AGENT}, timeout=config.HTTP_TIMEOUT)
        if r.status_code != 200:
            return None
        out = []
        for x in (r.json().get("quotes") or [])[:10]:
            out.append({"symbol": x.get("symbol"), "name": x.get("longname") or x.get("shortname") or x.get("symbol"),
                        "type": x.get("quoteType"), "exchange": x.get("exchange")})
        return out or None
    except Exception:
        return None


def _f(x: Any) -> float | None:
    try:
        v = float(x)
        return v if v == v else None
    except Exception:
        return None


def _i(x: Any) -> int | None:
    try:
        return int(float(x))
    except Exception:
        return None
