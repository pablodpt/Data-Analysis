"""Keyless news via Google News RSS. No dependencies beyond httpx + stdlib xml."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import httpx

from .. import config
from ..cache import cached

BASE = "https://news.google.com/rss/search"


def _parse(xml: str, symbol: str | None, limit: int) -> list[dict] | None:
    try:
        root = ET.fromstring(xml)
    except Exception:
        return None
    out = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "—").strip()
        # Google appends " - Publisher" to titles
        publisher, clean = "Google News", title
        if " - " in title:
            clean, publisher = title.rsplit(" - ", 1)
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        try:
            pub = parsedate_to_datetime(pub).isoformat()
        except Exception:
            pass
        desc = re.sub(r"<[^>]+>", "", item.findtext("description") or "")[:300]
        desc = desc.replace("&nbsp;", " ").strip()
        out.append({"title": clean.strip(), "publisher": publisher.strip(),
                    "symbol": symbol, "published": pub, "link": link,
                    "summary": desc})
        if len(out) >= limit:
            break
    return out or None


async def _fetch(q: str, symbol: str | None, limit: int) -> list[dict] | None:
    try:
        async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT,
                                     follow_redirects=True) as c:
            r = await c.get(BASE, params={"q": q, "hl": "en-US", "gl": "US",
                                          "ceid": "US:en"},
                            headers={"User-Agent": config.USER_AGENT})
        if r.status_code != 200:
            return None
        return _parse(r.text, symbol, limit)
    except Exception:
        return None


@cached(config.TTL_NEWS, lambda s, lim=20: f"rss:{s.upper()}:{lim}")
async def symbol_news(symbol: str, limit: int = 20) -> list[dict] | None:
    return await _fetch(f"{symbol} stock when:7d", symbol.upper(), limit)


@cached(config.TTL_NEWS, lambda lim=20: f"rssm:{lim}")
async def market_news(limit: int = 20) -> list[dict] | None:
    return await _fetch("stock market when:1d", None, limit)
