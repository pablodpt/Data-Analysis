"""Screener tests — forced DEMO_MODE=always, fully offline."""
import os
import sys
from pathlib import Path

os.environ["DEMO_MODE"] = "always"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from backend.main import app  # noqa: E402

client = TestClient(app)


def test_universe():
    u = client.get("/api/screener/universe").json()
    assert u["count"] >= 100
    assert "Technology" in u["sectors"] and "ETF" in u["sectors"]
    syms = {s["symbol"] for s in u["symbols"]}
    assert {"AAPL", "MSFT", "JPM", "XOM", "SPY"} <= syms


def test_run_default():
    d = client.post("/api/screener/run", json={}).json()
    assert d["mode"] == "demo" and d["count"] == d["universe"] >= 100
    assert len(d["rows"]) == 50  # default limit
    r0 = d["rows"][0]
    assert {"symbol", "name", "sector", "price", "pct", "volume",
            "mktCap", "pe", "divYield", "week52pos"} <= set(r0)
    # default sort mktCap desc
    caps = [r["mktCap"] for r in d["rows"]]
    assert caps == sorted(caps, reverse=True)


def test_run_sector_filter():
    d = client.post("/api/screener/run",
                    json={"sectors": ["Energy"], "limit": 50}).json()
    assert d["count"] == 7
    assert all(r["sector"] == "Energy" for r in d["rows"])


def test_run_numeric_filters_and_sort():
    d = client.post("/api/screener/run", json={
        "minPrice": 100, "maxPE": 25, "minDivY": 1.0,
        "sort": "pe", "dir": "asc", "limit": 20}).json()
    assert d["rows"], "filters should match something in demo data"
    assert all(r["price"] >= 100 and r["pe"] <= 25 and r["divYield"] >= 1.0
               for r in d["rows"])
    pes = [r["pe"] for r in d["rows"]]
    assert pes == sorted(pes)


def test_run_impossible_filter():
    d = client.post("/api/screener/run", json={"minMktCapB": 1e9}).json()
    assert d["count"] == 0 and d["rows"] == []
