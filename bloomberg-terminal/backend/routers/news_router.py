"""News endpoints: per-symbol and market-wide."""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, Query

from .. import demo
from ..providers import finnhub, news_rss, yahoo
from . import allow_demo, demo_ok, live_ok, unavailable, want_live

router = APIRouter(prefix="/api", tags=["news"])


@router.get("/news")
async def symbol_news(symbol: str = Query(min_length=1), limit: int = 20):
    s = symbol.upper()
    limit = max(1, min(limit, 50))
    if want_live():
        n = await finnhub.company_news(s)
        if n:
            return live_ok({"symbol": s, "articles": n[:limit]}, "finnhub")
        n = await asyncio.to_thread(yahoo.news, s)
        if n:
            return live_ok({"symbol": s, "articles": n[:limit]}, "yahoo")
        n = await news_rss.symbol_news(s, limit)
        if n:
            return live_ok({"symbol": s, "articles": n[:limit]}, "google-news-rss")
    if allow_demo():
        return demo_ok({"symbol": s, "articles": demo.gen_news(s, limit)})
    raise unavailable("news")


@router.get("/news/market")
async def market_news(limit: int = 20):
    limit = max(1, min(limit, 50))
    if want_live():
        n = await finnhub.market_news()
        if n:
            return live_ok({"articles": n[:limit]}, "finnhub")
        n = await news_rss.market_news(limit)
        if n:
            return live_ok({"articles": n[:limit]}, "google-news-rss")
    if allow_demo():
        return demo_ok({"articles": demo.gen_market_news(limit)})
    raise unavailable("market news")
