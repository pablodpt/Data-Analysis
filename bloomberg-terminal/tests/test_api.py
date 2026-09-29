"""API smoke tests — forced DEMO_MODE=always, fully offline."""
import os
import sys
from pathlib import Path

os.environ["DEMO_MODE"] = "always"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from backend import config  # noqa: E402
from backend.main import app  # noqa: E402

assert config.DEMO_MODE == "always"
client = TestClient(app)


def test_health_and_status():
    assert client.get("/api/health").json()["status"] == "ok"
    st = client.get("/api/status").json()
    assert st["default_watchlist"] and st["indices"]


def test_quote_and_history():
    q = client.get("/api/quote", params={"symbol": "AAPL"}).json()
    assert q["mode"] == "demo" and q["price"] > 0
    h = client.get("/api/history", params={"symbol": "AAPL", "range": "1Y"}).json()
    assert len(h["bars"]) == 252
    r = client.post("/api/quotes", json={"symbols": ["AAPL", "MSFT"]}).json()
    assert len(r["quotes"]) == 2


def test_profile_fundamentals():
    p = client.get("/api/profile", params={"symbol": "MSFT"}).json()
    assert p["name"] == "Microsoft Corp."
    f = client.get("/api/financials", params={"symbol": "MSFT"}).json()
    assert f["rows"]
    e = client.get("/api/earnings", params={"symbol": "MSFT"}).json()
    assert e["past"]
    fl = client.get("/api/filings", params={"symbol": "MSFT"}).json()
    assert fl["filings"]


def test_market_and_news():
    o = client.get("/api/market/overview").json()
    assert o["indices"]
    m = client.get("/api/market/movers", params={"group": "losers"}).json()
    assert m["rows"]
    n = client.get("/api/news", params={"symbol": "AAPL"}).json()
    assert n["articles"]
    mn = client.get("/api/news/market").json()
    assert mn["articles"]


def test_econ():
    i = client.get("/api/econ/indicators").json()
    assert len(i["indicators"]) >= 10
    s = client.get("/api/econ/series", params={"id": "DGS10"}).json()
    assert len(s["points"]) > 200
    c = client.get("/api/econ/calendar").json()
    assert c["events"]


def test_frontend_served():
    r = client.get("/")
    assert r.status_code == 200 and "OpenBerg" in r.text
