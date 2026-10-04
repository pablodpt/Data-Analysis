"""Market endpoints with mocked LIVE providers (no network).

Exercises the live code paths (Stooq quotes/history, Yahoo screener) that the
demo-mode tests never touch — TOP is the only view that uses them.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from backend import config  # noqa: E402
from backend.main import app  # noqa: E402
from backend.providers import stooq  # noqa: E402
from backend.routers import market  # noqa: E402

client = TestClient(app)


async def _q(sym, **kw):
    return {"symbol": sym, "price": 100.0, "change": 1.5, "pct": 1.52,
            "volume": 1234567, "open": 99.0, "high": 101.0, "low": 98.0,
            "prevClose": 98.5, "name": sym}


async def _h(sym, rng="1Y", interval="1d"):
    return {"bars": [{"t": f"2026-01-{d:02d}", "o": 1.0, "h": 2.0, "l": 0.5,
                      "c": 1.5, "v": 10} for d in range(1, 11)]}


async def _scr(group, limit):
    return [{"symbol": "XYZ", "name": "Xyz Inc", "price": 10.0, "change": 1.0,
             "pct": 11.0, "volume": 999}]


def test_overview_all_live(monkeypatch):
    monkeypatch.setattr(config, "DEMO_MODE", "auto")
    monkeypatch.setattr(stooq, "quote", _q)
    monkeypatch.setattr(stooq, "history", _h)
    d = client.get("/api/market/overview").json()
    assert d["mode"] == "live" and d["source"] == "stooq"
    assert len(d["indices"]) == 10
    r = d["indices"][0]
    assert r["price"] == 100.0 and len(r["spark"]) == 10


def test_overview_partial_live_is_mixed(monkeypatch):
    async def _flaky(sym, **kw):
        return None if sym == "^VIX" else await _q(sym)

    monkeypatch.setattr(config, "DEMO_MODE", "auto")
    monkeypatch.setattr(stooq, "quote", _flaky)
    monkeypatch.setattr(stooq, "history", _h)
    d = client.get("/api/market/overview").json()
    assert d["mode"] == "mixed"
    assert len(d["indices"]) == 10  # demo fills the failed one


def test_movers_screener_live(monkeypatch):
    monkeypatch.setattr(config, "DEMO_MODE", "auto")
    monkeypatch.setattr(market, "_yahoo_screener", _scr)
    d = client.get("/api/market/movers", params={"group": "gainers"}).json()
    assert d["mode"] == "live" and d["source"] == "yahoo-screener"
    assert d["rows"][0]["symbol"] == "XYZ"


def test_movers_universe_fallback_live(monkeypatch):
    async def _none(group, limit):
        return None

    monkeypatch.setattr(config, "DEMO_MODE", "auto")
    monkeypatch.setattr(market, "_yahoo_screener", _none)
    monkeypatch.setattr(stooq, "quote", _q)
    d = client.get("/api/market/movers", params={"group": "losers"}).json()
    assert d["mode"] == "live" and d["source"] == "stooq"
    assert len(d["rows"]) == 10
