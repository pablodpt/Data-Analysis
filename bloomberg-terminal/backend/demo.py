"""Deterministic demo-data generator.

Used when offline, when a provider fails (DEMO_MODE=auto), or when forced
(DEMO_MODE=always). Seeded random-walks => stable, realistic-looking data.
Every response built from here must be labelled mode="demo".
"""
from __future__ import annotations

import calendar
import hashlib
import json
import random
from datetime import date, datetime, timedelta, timezone

from .config import DATA_FILE

_defaults: dict | None = None


def defaults() -> dict:
    global _defaults
    if _defaults is None:
        _defaults = json.loads(DATA_FILE.read_text())
    return _defaults


# ---------------------------------------------------------------- helpers

def seed_of(*parts: str) -> int:
    h = hashlib.md5("|".join(parts).encode()).hexdigest()
    return int(h[:8], 16)


def today_utc() -> date:
    return datetime.now(timezone.utc).date()


BASE_PRICES = {
    "AAPL": 232.0, "MSFT": 428.0, "NVDA": 131.0, "TSFT": 0.0, "TSLA": 248.0,
    "AMZN": 197.0, "META": 585.0, "GOOGL": 176.0, "GOOG": 177.0, "AMD": 122.0,
    "AVGO": 172.0, "JPM": 244.0, "XOM": 118.0, "LLY": 775.0, "NFLX": 760.0,
    "COIN": 264.0, "PLTR": 66.0, "SMCI": 42.0, "MSTR": 1680.0, "GME": 22.0,
    "AMC": 4.4, "ARM": 134.0, "SPY": 595.0, "QQQ": 535.0, "DIA": 445.0,
    "IWM": 228.0, "^GSPC": 5960.0, "^IXIC": 21480.0, "^DJI": 44290.0,
    "^RUT": 2280.0, "^VIX": 14.6, "^TNX": 4.21, "GC=F": 2655.0, "CL=F": 71.4,
    "BTC-USD": 97400.0, "EURUSD=X": 1.052,
}


def base_price(symbol: str) -> float:
    s = symbol.upper()
    if s in BASE_PRICES:
        return BASE_PRICES[s]
    for idx in defaults()["indices"]:
        if idx["symbol"].upper() == s:
            return float(idx["demo_base"])
    r = random.Random(seed_of("px", s))
    return round(r.uniform(18, 480), 2)


def business_days(n: int, end: date | None = None) -> list[date]:
    end = end or today_utc()
    out: list[date] = []
    d = end
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d -= timedelta(days=1)
    return sorted(out)


def randwalk(rng: random.Random, n: int, start: float, drift: float, vol: float,
             lo: float = 0.01) -> list[float]:
    px = start
    out = []
    for _ in range(n):
        px = max(lo, px * (1 + drift + rng.gauss(0, vol)))
        out.append(px)
    return out


def round_px(px: float) -> float:
    if px >= 1000:
        return round(px, 2)
    if px >= 100:
        return round(px, 2)
    if px >= 1:
        return round(px, 3 if px < 10 else 2)
    return round(px, 4)


# ---------------------------------------------------------------- history

RANGE_DAYS = {"1M": 22, "3M": 66, "6M": 132, "1Y": 252, "2Y": 504,
              "5Y": 1258, "10Y": 2516, "MAX": 2516, "YTD": 252}


def gen_history(symbol: str, rng: str = "1Y", interval: str = "1d") -> dict:
    s = symbol.upper()
    rng = rng.upper()
    base = base_price(s)
    vol = 0.016 if not s.startswith("^") else 0.009
    if s in ("BTC-USD", "MSTR", "GME", "AMC", "SMCI", "COIN"):
        vol = 0.035
    if s in ("^VIX",):
        vol, drift = 0.05, 0.0
    else:
        drift = 0.0006

    if rng in ("1D", "5D"):
        days = 1 if rng == "1D" else 5
        per_day = 78  # 5-min bars 9:30-16:00
        n = per_day * days
        r = random.Random(seed_of("intra", s, today_utc().isoformat()))
        closes = randwalk(r, n, base * (1 + (r.random() - 0.5) * 0.01), 0.00004, 0.0016)
        bars = []
        day_list = business_days(days)
        i = 0
        for d in day_list:
            t0 = datetime(d.year, d.month, d.day, 9, 30)
            for b in range(per_day):
                c = closes[i]
                o = closes[i - 1] if i > 0 else c * (1 - r.gauss(0, 0.0006))
                h = max(o, c) * (1 + abs(r.gauss(0, 0.0008)))
                lo = min(o, c) * (1 - abs(r.gauss(0, 0.0008)))
                v = int(r.uniform(80_000, 900_000) * (50 if s in ("SPY", "QQQ") else 1))
                bars.append({"t": (t0 + timedelta(minutes=5 * b)).isoformat(),
                             "o": round_px(o), "h": round_px(h),
                             "l": round_px(lo), "c": round_px(c), "v": v})
                i += 1
        prev = bars[0]["o"]
    else:
        n = RANGE_DAYS.get(rng, 252)
        if rng == "YTD":
            jan1 = date(today_utc().year, 1, 1)
            n = max(10, sum(1 for i in range((today_utc() - jan1).days + 1)
                            if (jan1 + timedelta(days=i)).weekday() < 5))
        r = random.Random(seed_of("daily", s))
        # walk backwards from an anchored end so the last price ~= base
        fwd = randwalk(r, n, 100.0, drift, vol)
        scale = base / fwd[-1]
        closes = [x * scale for x in fwd]
        # small day-to-day jitter so quotes feel alive, stable within a day
        jr = random.Random(seed_of("jit", s, today_utc().isoformat()))
        jig = 1 + (jr.random() - 0.5) * vol * 0.9
        closes[-1] *= jig
        days = business_days(n)
        bars = []
        for i, d in enumerate(days):
            c = closes[i]
            o = closes[i - 1] if i > 0 else c / (1 + r.gauss(0, vol * 0.5))
            h = max(o, c) * (1 + abs(r.gauss(0, vol * 0.35)))
            lo = min(o, c) * (1 - abs(r.gauss(0, vol * 0.35)))
            v = int(r.uniform(4e6, 60e6) * (3 if s in ("SPY", "QQQ", "AAPL", "NVDA") else 1))
            bars.append({"t": d.isoformat(), "o": round_px(o), "h": round_px(h),
                         "l": round_px(lo), "c": round_px(c), "v": v})
        prev = bars[-2]["c"] if len(bars) > 1 else bars[0]["o"]

    if interval in ("1wk", "1mo"):
        bars = _resample(bars, interval)
    last = bars[-1]
    chg = last["c"] - prev
    return {
        "symbol": s, "range": rng, "interval": interval,
        "currency": "USD", "prevClose": round_px(prev),
        "bars": bars,
        "last": {"price": last["c"], "change": round(last["c"] - prev, 4),
                 "pct": round((last["c"] / prev - 1) * 100, 3)},
    }


def _resample(bars: list[dict], interval: str) -> list[dict]:
    out, cur, key = [], None, None
    for b in bars:
        d = b["t"][:10]
        dt = date.fromisoformat(d)
        k = f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}" if interval == "1wk" else d[:7]
        if k != key:
            if cur:
                out.append(cur)
            cur = {"t": d, "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"], "v": b["v"]}
            key = k
        else:
            cur["h"] = max(cur["h"], b["h"])
            cur["l"] = min(cur["l"], b["l"])
            cur["c"] = b["c"]
            cur["v"] += b["v"]
    if cur:
        out.append(cur)
    return out


# ---------------------------------------------------------------- quotes

def gen_quote(symbol: str) -> dict:
    s = symbol.upper()
    h = gen_history(s, "1M")
    bars = h["bars"]
    last, prev = bars[-1], h["prevClose"]
    r = random.Random(seed_of("q", s))
    hi = max(b["h"] for b in bars[-22:])
    lo = min(b["l"] for b in bars[-22:])
    # 52w from a longer walk
    h52 = gen_history(s, "1Y")["bars"]
    w52h = max(b["h"] for b in h52)
    w52l = min(b["l"] for b in h52)
    px = last["c"]
    return {
        "symbol": s, "name": profile_name(s), "currency": "USD",
        "price": px, "change": round(px - prev, 4),
        "pct": round((px / prev - 1) * 100, 3),
        "open": last["o"], "high": last["h"], "low": last["l"],
        "prevClose": round_px(prev), "volume": last["v"],
        "avgVolume": int(sum(b["v"] for b in bars[-20:]) / 20),
        "mktCap": int(px * r.uniform(0.3e9, 15e9)),
        "pe": round(r.uniform(12, 38), 2), "eps": round(px / r.uniform(12, 38), 2),
        "divYield": round(r.uniform(0, 2.4), 2),
        "week52High": round_px(w52h), "week52Low": round_px(w52l),
        "dayRange": f"{last['l']} - {last['h']}",
        "asOf": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------- profile & fundamentals

PROFILES = {
    "AAPL": ("Apple Inc.", "Technology", "Consumer Electronics", 161000, "https://www.apple.com",
             "Apple designs, manufactures and markets smartphones, personal computers, tablets, wearables and accessories, and sells related services."),
    "MSFT": ("Microsoft Corp.", "Technology", "Software — Infrastructure", 228000, "https://www.microsoft.com",
             "Microsoft develops, licenses and supports software, services, devices and cloud solutions including Azure, Office and Windows."),
    "NVDA": ("NVIDIA Corp.", "Technology", "Semiconductors", 29600, "https://www.nvidia.com",
             "NVIDIA designs graphics processing units and AI computing platforms for data centers, gaming, automotive and visualization."),
    "TSLA": ("Tesla Inc.", "Consumer Cyclical", "Auto Manufacturers", 140000, "https://www.tesla.com",
             "Tesla designs and manufactures electric vehicles, battery energy storage, solar products and related services."),
    "AMZN": ("Amazon.com Inc.", "Consumer Cyclical", "Internet Retail", 1608000, "https://www.amazon.com",
             "Amazon operates e-commerce marketplaces, the AWS cloud platform, devices, streaming and logistics businesses."),
    "META": ("Meta Platforms Inc.", "Communication", "Internet Content", 74000, "https://www.meta.com",
             "Meta builds social apps (Facebook, Instagram, WhatsApp) and Reality Labs hardware, monetized primarily by advertising."),
    "GOOGL": ("Alphabet Inc.", "Communication", "Internet Content", 183000, "https://abc.xyz",
              "Alphabet is the parent of Google Search, YouTube, Android, Cloud and Other Bets including Waymo and Verily."),
    "AMD": ("Advanced Micro Devices", "Technology", "Semiconductors", 26000, "https://www.amd.com",
            "AMD designs CPUs, GPUs and adaptive computing products for data center, client, gaming and embedded markets."),
    "SPY": ("SPDR S&P 500 ETF", "ETF", "Large Blend", 0, "https://www.ssga.com",
            "SPY tracks the S&P 500 index, holding ~500 large-cap U.S. equities."),
    "QQQ": ("Invesco QQQ Trust", "ETF", "Large Growth", 0, "https://www.invesco.com",
            "QQQ tracks the Nasdaq-100 index of the largest non-financial Nasdaq listings."),
}


def profile_name(symbol: str) -> str:
    s = symbol.upper()
    if s in PROFILES:
        return PROFILES[s][0]
    for idx in defaults()["indices"]:
        if idx["symbol"].upper() == s:
            return idx["label"]
    return f"{s} Inc."


def gen_profile(symbol: str) -> dict:
    s = symbol.upper()
    q = gen_quote(s)
    if s in PROFILES:
        name, sector, industry, emp, site, desc = PROFILES[s]
    else:
        r = random.Random(seed_of("prof", s))
        sector = r.choice(["Technology", "Healthcare", "Financials", "Industrials", "Energy", "Consumer Cyclical"])
        industry = {"Technology": "Software — Application", "Healthcare": "Biotechnology",
                    "Financials": "Banks — Diversified", "Industrials": "Aerospace & Defense",
                    "Energy": "Oil & Gas E&P", "Consumer Cyclical": "Apparel"}[sector]
        name, emp, site = f"{s} Inc.", int(r.uniform(2e3, 9e4)), f"https://www.{s.lower()}.com"
        desc = f"{name} operates in the {industry.lower()} industry within the {sector.lower()} sector. (Demo description — connect to the internet for live fundamentals.)"
    return {
        "symbol": s, "name": name, "sector": sector, "industry": industry,
        "exchange": "XNGS" if s not in ("SPY", "QQQ") else "ARCX",
        "currency": "USD", "employees": emp, "website": site, "description": desc,
        "price": q["price"], "change": q["change"], "pct": q["pct"],
        "mktCap": q["mktCap"], "pe": q["pe"], "eps": q["eps"],
        "divYield": q["divYield"], "week52High": q["week52High"], "week52Low": q["week52Low"],
    }


INCOME_ROWS = ["Total Revenue", "Cost of Revenue", "Gross Profit", "Operating Expenses",
               "Operating Income", "Interest Expense", "Income Tax", "Net Income", "EPS (diluted)"]
BALANCE_ROWS = ["Cash & Equivalents", "Receivables", "Inventory", "Total Current Assets",
                "PP&E (net)", "Goodwill", "Total Assets", "Payables", "Short-term Debt",
                "Total Current Liabilities", "Long-term Debt", "Total Liabilities",
                "Retained Earnings", "Total Equity"]
CASH_ROWS = ["Net Income", "Depreciation & Amort.", "Change in Working Capital",
             "Operating Cash Flow", "CapEx", "Free Cash Flow", "Dividends Paid",
             "Buybacks", "Net Change in Cash"]


def gen_financials(symbol: str, statement: str = "income", period: str = "annual") -> dict:
    s = symbol.upper()
    rev0 = gen_quote(s)["price"] * random.Random(seed_of("rev", s)).uniform(0.15e9, 0.9e9)
    r = random.Random(seed_of("fin", s, statement, period))
    growth = r.uniform(0.04, 0.16)
    n = 4 if period == "annual" else 8
    dates = []
    t = today_utc()
    if period == "annual":
        for i in range(n):
            dates.append(str(t.year - (n - 1 - i)))
    else:
        q = (t.month - 1) // 3
        for i in range(n):
            qq = q - (n - 1 - i)
            yy = t.year + qq // 4
            dates.append(f"{yy}Q{(qq % 4) + 1}")
    scale = 1 if period == "annual" else 0.26
    revs = [rev0 * scale * (1 + growth) ** (i - (n - 1)) for i in range(n)]
    margin = r.uniform(0.12, 0.32)
    rowspec = {"income": INCOME_ROWS, "balance": BALANCE_ROWS, "cashflow": CASH_ROWS}[statement]
    rows = []
    for row in rowspec:
        vals = []
        for i, rev in enumerate(revs):
            f = r.uniform(0.97, 1.03)
            v = _statement_value(row, rev, revs, i, margin, scale) * f
            vals.append(round(v / 1e6, 1))  # USD millions
        rows.append({"label": row, "values": vals})
    return {"symbol": s, "statement": statement, "period": period,
            "currency": "USD", "scale": "millions", "dates": dates, "rows": rows,
            "ratios": {
                "Gross Margin %": round(margin * 100 + r.uniform(-2, 2), 1),
                "Operating Margin %": round(margin * 68 + r.uniform(-2, 2), 1),
                "Net Margin %": round(margin * 62 + r.uniform(-2, 2), 1),
                "ROE %": round(r.uniform(12, 45), 1),
                "Debt/Equity": round(r.uniform(0.1, 1.8), 2),
                "Current Ratio": round(r.uniform(0.9, 2.6), 2),
            }}


def _statement_value(row, rev, revs, i, margin, scale):
    n = len(revs)
    tot_assets = revs[-1] * 3.4
    if row == "Total Revenue":
        return rev
    if row == "Cost of Revenue":
        return rev * (1 - margin - 0.22)
    if row == "Gross Profit":
        return rev * (margin + 0.22)
    if row == "Operating Expenses":
        return rev * 0.22
    if row == "Operating Income":
        return rev * margin
    if row == "Interest Expense":
        return rev * 0.012
    if row == "Income Tax":
        return rev * margin * 0.16
    if row == "Net Income":
        return rev * margin * 0.83
    if row == "EPS (diluted)":
        return rev * margin * 0.83 / (revs[-1] * 1.7)
    if row == "Total Assets":
        return tot_assets * (0.82 + 0.06 * i)
    if row == "Total Current Assets":
        return tot_assets * 0.34 * (0.9 + 0.03 * i)
    if row == "Cash & Equivalents":
        return tot_assets * 0.12
    if row == "Receivables":
        return rev * 0.14
    if row == "Inventory":
        return rev * 0.05
    if row == "PP&E (net)":
        return tot_assets * 0.2
    if row == "Goodwill":
        return tot_assets * 0.16
    if row == "Total Liabilities":
        return tot_assets * 0.52 * (0.9 + 0.03 * i)
    if row == "Payables":
        return rev * 0.12
    if row == "Short-term Debt":
        return tot_assets * 0.04
    if row == "Total Current Liabilities":
        return tot_assets * 0.2
    if row == "Long-term Debt":
        return tot_assets * 0.3
    if row == "Retained Earnings":
        return tot_assets * 0.3 * (0.8 + 0.07 * i)
    if row == "Total Equity":
        return tot_assets * 0.48 * (0.85 + 0.05 * i)
    if row == "Depreciation & Amort.":
        return rev * 0.05
    if row == "Change in Working Capital":
        return rev * 0.01 * (1 if i % 2 else -1)
    if row == "Operating Cash Flow":
        return rev * margin * 1.05
    if row == "CapEx":
        return -rev * 0.06
    if row == "Free Cash Flow":
        return rev * margin * 0.99
    if row == "Dividends Paid":
        return -rev * 0.02
    if row == "Buybacks":
        return -rev * 0.05
    if row == "Net Change in Cash":
        return rev * 0.015
    return rev * 0.1


def gen_earnings(symbol: str) -> dict:
    s = symbol.upper()
    r = random.Random(seed_of("earn", s))
    t = today_utc()
    past, future = [], []
    for k in range(4, 0, -1):
        m = t.month - 3 * k
        yy = t.year + (m - 1) // 12
        mm = (m - 1) % 12 + 1
        est = round(r.uniform(0.8, 6.5), 2)
        act = round(est * r.uniform(0.92, 1.12), 2)
        past.append({"date": date(yy, mm, 15).isoformat(), "estimate": est,
                     "actual": act, "surprisePct": round((act / est - 1) * 100, 2)})
    for k in range(1, 3):
        m = t.month + 3 * k
        yy = t.year + (m - 1) // 12
        mm = (m - 1) % 12 + 1
        future.append({"date": date(yy, mm, 15).isoformat(),
                       "estimate": round(r.uniform(0.8, 6.5), 2)})
    return {"symbol": s, "past": past, "upcoming": future}


# ---------------------------------------------------------------- news

PUBS = ["Reuters", "Bloomberg", "Wall Street Journal", "CNBC", "Financial Times",
        "MarketWatch", "Barron's", "Seeking Alpha"]
HEADLINES = [
    "{name} beats quarterly estimates as margins expand",
    "Analysts raise price targets on {sym} after investor day",
    "{name} unveils buyback plan, raises dividend",
    "Options traders pile into {sym} ahead of earnings",
    "{name} guides higher on strong demand outlook",
    "{sym} slips as sector rotation hits growth stocks",
    "Insiders disclose open-market purchases of {sym}",
    "{name} announces new product line, shares rally",
    "Wall Street split on {sym} valuation after record run",
    "{name} expands partnership in data-center push",
]


def gen_news(symbol: str, limit: int = 20) -> list[dict]:
    s = symbol.upper()
    r = random.Random(seed_of("news", s, today_utc().isoformat()))
    name = profile_name(s)
    out = []
    now = datetime.now(timezone.utc)
    for i in range(limit):
        pub = PUBS[r.randrange(len(PUBS))]
        hl = HEADLINES[r.randrange(len(HEADLINES))].format(sym=s, name=name)
        ts = now - timedelta(hours=r.randrange(1, 160), minutes=r.randrange(60))
        out.append({"title": hl, "publisher": pub, "symbol": s,
                    "published": ts.isoformat(),
                    "link": f"https://news.google.com/search?q={s}%20stock%20{pub.replace(' ', '%20')}",
                    "summary": f"{pub} reports on {name} ({s}). Demo headline — connect to the internet for live news."})
    return sorted(out, key=lambda x: x["published"], reverse=True)


def gen_market_news(limit: int = 20) -> list[dict]:
    r = random.Random(seed_of("mnews", today_utc().isoformat()))
    topics = ["S&P 500", "Nasdaq", "Treasury yields", "the Fed", "oil prices",
              "gold", "the dollar", "Bitcoin", "chip stocks", "banks"]
    verbs = ["rallies", "slips", "holds steady", "climbs to record", "retreats",
             "outperforms", "lags", "rebounds", "consolidates", "jumps"]
    out, now = [], datetime.now(timezone.utc)
    for i in range(limit):
        t, v = r.choice(topics), r.choice(verbs)
        ts = now - timedelta(hours=r.randrange(1, 120))
        out.append({"title": f"Markets: {t} {v} as investors weigh data",
                    "publisher": PUBS[r.randrange(len(PUBS))], "symbol": None,
                    "published": ts.isoformat(),
                    "link": "https://news.google.com/search?q=stock%20market",
                    "summary": "Demo market headline — connect to the internet for live news."})
    return sorted(out, key=lambda x: x["published"], reverse=True)


# ---------------------------------------------------------------- market

def gen_overview() -> dict:
    idx = []
    for e in defaults()["indices"]:
        s = e["symbol"]
        q = gen_quote(s)
        h = gen_history(s, "1M")["bars"]
        idx.append({"symbol": s, "label": e["label"], "price": q["price"],
                    "change": q["change"], "pct": q["pct"],
                    "spark": [b["c"] for b in h[-30:]]})
    r = random.Random(seed_of("breadth", today_utc().isoformat()))
    adv, dec = r.randrange(180, 380), r.randrange(120, 320)
    return {"asOf": datetime.now(timezone.utc).isoformat(), "indices": idx,
            "breadth": {"advancers": adv, "decliners": dec, "unchanged": 500 - adv - dec
                        if adv + dec < 500 else 8, "universe": "S&P 500 (demo)"}}


def gen_movers(group: str = "gainers", limit: int = 10) -> dict:
    rows = []
    for s in defaults()["movers_universe"]:
        q = gen_quote(s)
        rows.append({"symbol": s, "name": profile_name(s), "price": q["price"],
                     "change": q["change"], "pct": q["pct"], "volume": q["volume"]})
    if group == "losers":
        rows.sort(key=lambda x: x["pct"])
    elif group == "actives":
        rows.sort(key=lambda x: x["volume"], reverse=True)
    else:
        rows.sort(key=lambda x: x["pct"], reverse=True)
    return {"group": group, "asOf": datetime.now(timezone.utc).isoformat(), "rows": rows[:limit]}


# ---------------------------------------------------------------- econ

def gen_indicators() -> dict:
    out = []
    for e in defaults()["fred_series"]:
        r = random.Random(seed_of("fred", e["id"]))
        base = float(e["demo_base"])
        vol = 0.004 if e["freq"] != "D" else 0.01
        hist = randwalk(r, 60, base * 0.94, 0.0012, vol)
        v, p = hist[-1], hist[-2]
        out.append({"id": e["id"], "label": e["label"], "unit": e["unit"],
                    "value": round(v, 3), "prev": round(p, 3),
                    "change": round(v - p, 3),
                    "pct": round((v / p - 1) * 100, 3),
                    "spark": [round(x, 3) for x in hist[-24:]],
                    "asOf": today_utc().isoformat()})
    return {"asOf": datetime.now(timezone.utc).isoformat(), "indicators": out}


def gen_series(sid: str, years: int = 10) -> dict | None:
    meta = next((e for e in defaults()["fred_series"] if e["id"].upper() == sid.upper()), None)
    if meta is None:
        return None
    r = random.Random(seed_of("freds", meta["id"]))
    freq = meta["freq"]
    n = {"D": 252 * years, "M": 12 * years, "Q": 4 * years}[freq]
    vol = {"D": 0.008, "M": 0.004, "Q": 0.006}[freq]
    hist = randwalk(r, n, float(meta["demo_base"]) * 0.9, 0.0009, vol)
    pts, t = [], today_utc()
    step = {"D": 1, "M": 30, "Q": 91}[freq]
    for i in range(n - 1, -1, -1):
        d = t - timedelta(days=step * (n - 1 - i))
        if freq == "D" and d.weekday() >= 5:
            continue
        pts.append({"t": d.isoformat(), "v": round(hist[i], 3)})
    return {"id": meta["id"], "label": meta["label"], "unit": meta["unit"],
            "freq": freq, "points": pts}


def gen_calendar(days: int = 14) -> dict:
    t = today_utc()
    start = t - timedelta(days=3)
    events = []
    for i in range(days + 3):
        d = start + timedelta(days=i)
        for rule in defaults()["calendar_rules"]:
            if _rule_hits(rule, d):
                r = random.Random(seed_of("cal", rule["name"], d.isoformat()))
                fc = {"k": round(r.uniform(200, 260), 0), "%": round(r.uniform(0.1, 0.5), 1),
                      "rate": round(r.uniform(3.75, 4.5), 2), "idx": round(r.uniform(47, 53), 1)}[rule["unit"]]
                pv = round(fc * r.uniform(0.94, 1.06), 2 if rule["unit"] != "k" else 0)
                events.append({"date": d.isoformat(), "time": rule["time"], "name": rule["name"],
                               "country": "US", "importance": rule["importance"],
                               "forecast": fc, "previous": pv,
                               "actual": round(fc * r.uniform(0.96, 1.04), 2) if d < t else None})
    events.sort(key=lambda e: (e["date"], e["time"]))
    return {"asOf": datetime.now(timezone.utc).isoformat(), "events": events}


def _rule_hits(rule: dict, d: date) -> bool:
    if "weekday" in rule:
        return d.weekday() == rule["weekday"]
    kind = rule.get("rule")
    if kind == "first_friday":
        return d.weekday() == 4 and d.day <= 7
    if kind == "monthly_day_1":
        return d.day == 1 and d.weekday() < 5
    if kind and kind.startswith("monthly_day_"):
        want = int(kind.split("_")[-1])
        dd = d
        while dd.weekday() >= 5:
            dd += timedelta(days=1)
        return d == dd.replace(day=min(want, calendar.monthrange(d.year, d.month)[1])) \
            if want <= 28 else d.day == min(want, calendar.monthrange(d.year, d.month)[1]) and d.weekday() < 5
    if kind == "every_6w_tue":
        epoch = date(2024, 1, 30)
        return d.weekday() == 1 and (d - epoch).days % 42 == 0
    if kind == "quarter_month2_day29":
        return d.month in (1, 4, 7, 10) and d.day == 29 and d.weekday() < 5
    return False


# ---------------------------------------------------------------- search

SEARCH_INDEX = [
    ("AAPL", "Apple Inc."), ("MSFT", "Microsoft Corp."), ("NVDA", "NVIDIA Corp."),
    ("TSLA", "Tesla Inc."), ("AMZN", "Amazon.com Inc."), ("META", "Meta Platforms"),
    ("GOOGL", "Alphabet A"), ("GOOG", "Alphabet C"), ("AMD", "Advanced Micro Devices"),
    ("AVGO", "Broadcom"), ("JPM", "JPMorgan Chase"), ("XOM", "Exxon Mobil"),
    ("LLY", "Eli Lilly"), ("NFLX", "Netflix"), ("COIN", "Coinbase"), ("PLTR", "Palantir"),
    ("ARM", "Arm Holdings"), ("SPY", "SPDR S&P 500"), ("QQQ", "Invesco QQQ"),
    ("DIA", "SPDR Dow Jones"), ("IWM", "iShares Russell 2000"),
    ("^GSPC", "S&P 500 Index"), ("^IXIC", "Nasdaq Composite"), ("^DJI", "Dow Jones Industrial"),
    ("^RUT", "Russell 2000"), ("^VIX", "VIX Volatility"), ("BTC-USD", "Bitcoin USD"),
    ("GC=F", "Gold Futures"), ("CL=F", "WTI Crude Futures"), ("EURUSD=X", "Euro / US Dollar"),
]


def search_local(q: str, limit: int = 10) -> list[dict]:
    ql = q.strip().lower()
    if not ql:
        return []
    scored = []
    for sym, name in SEARCH_INDEX:
        s, n = sym.lower(), name.lower()
        if s == ql:
            score = 0
        elif s.startswith(ql):
            score = 1
        elif ql in s:
            score = 2
        elif n.startswith(ql):
            score = 3
        elif ql in n:
            score = 4
        else:
            continue
        scored.append((score, {"symbol": sym, "name": name,
                              "type": "INDEX" if sym.startswith("^") else
                              ("CRYPTO" if sym.endswith("-USD") else "EQUITY"),
                              "exchange": "US"}))
    scored.sort(key=lambda x: x[0])
    return [x[1] for x in scored[:limit]]
