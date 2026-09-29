"""SEC EDGAR provider — keyless. Filings + best-effort XBRL facts summary."""
from __future__ import annotations

import httpx

from .. import config
from ..cache import cached

HEADERS = {"User-Agent": config.USER_AGENT, "Accept-Encoding": "gzip",
           "Host": "data.sec.gov"}


@cached(86400, lambda: "sec:tickers")
async def _cik_for(symbol: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT) as c:
            r = await c.get("https://www.sec.gov/files/company_tickers.json",
                            headers={"User-Agent": config.USER_AGENT})
        if r.status_code != 200:
            return None
        for v in r.json().values():
            if str(v.get("ticker", "")).upper() == symbol.upper():
                return str(v["cik_str"]).zfill(10)
        return None
    except Exception:
        return None


@cached(config.TTL_FINANCIALS, lambda s, lim=12: f"secf:{s.upper()}:{lim}")
async def filings(symbol: str, limit: int = 12) -> list[dict] | None:
    try:
        cik = await _cik_for(symbol)
        if not cik:
            return None
        async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT) as c:
            r = await c.get(f"https://data.sec.gov/submissions/CIK{cik}.json",
                            headers=HEADERS)
        if r.status_code != 200:
            return None
        recent = r.json().get("filings", {}).get("recent", {})
        out = []
        n = min(len(recent.get("form", [])), limit * 3)
        for i in range(n):
            form = recent["form"][i]
            if form not in ("10-K", "10-Q", "8-K", "S-1", "DEF 14A", "4"):
                continue
            acc = recent["accessionNumber"][i].replace("-", "")
            doc = recent["primaryDocument"][i]
            out.append({"form": form, "date": recent["filingDate"][i],
                        "link": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{doc}"})
            if len(out) >= limit:
                break
        return out or None
    except Exception:
        return None
