"""Demo generator is deterministic and well-shaped (runs offline)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import demo


def test_history_deterministic():
    a = demo.gen_history("AAPL", "1Y")
    b = demo.gen_history("AAPL", "1Y")
    assert a == b
    assert len(a["bars"]) == 252
    assert set(a["bars"][0]) == {"t", "o", "h", "l", "c", "v"}


def test_history_intraday():
    d = demo.gen_history("MSFT", "1D")
    assert len(d["bars"]) == 78
    assert "T" in d["bars"][0]["t"]


def test_quote_shape():
    q = demo.gen_quote("NVDA")
    assert q["price"] > 0 and q["prevClose"] > 0
    assert q["week52High"] >= q["week52Low"]


def test_financials_shape():
    f = demo.gen_financials("AAPL", "income", "annual")
    assert len(f["dates"]) == 4
    assert f["rows"] and len(f["rows"][0]["values"]) == 4
    q = demo.gen_financials("AAPL", "balance", "quarterly")
    assert len(q["dates"]) == 8


def test_news_sorted():
    n = demo.gen_news("TSLA", 10)
    assert len(n) == 10
    assert n[0]["published"] >= n[-1]["published"]


def test_overview_and_movers():
    o = demo.gen_overview()
    assert len(o["indices"]) >= 8
    m = demo.gen_movers("gainers", 5)
    assert len(m["rows"]) == 5
    assert m["rows"][0]["pct"] >= m["rows"][-1]["pct"]


def test_econ():
    ind = demo.gen_indicators()
    assert len(ind["indicators"]) >= 10
    s = demo.gen_series("DGS10")
    assert s and len(s["points"]) > 200
    cal = demo.gen_calendar(14)
    assert cal["events"], "calendar should have events in a 14d window"


def test_search():
    assert demo.search_local("aapl")[0]["symbol"] == "AAPL"
    assert demo.search_local("apple")
    assert demo.search_local("zzzzzz") == []
