# Stock Research Agent

A reusable, on-demand **stock research agent**. Point it at any ticker or
company name — whenever you want — and it runs a 7-stage institutional-style
research pipeline and produces a self-contained HTML report:

1. **Fundamentals** — revenue, margins, ROIC/ROE, growth, valuation
   multiples, and a multi-method intrinsic value (50% two-stage FCFE DCF +
   50% growth-adjusted P/E; DCF n/a for banks → model fair value).
2. **Business model & moat** — how the company makes money, revenue
   segments, and a 5-pillar moat rating (network effects, switching costs,
   intangibles, cost advantage, scale).
3. **Competitors & the edge** — head-to-head peer table (market cap,
   revenue, P/E, note) plus the explicit core differentiator.
4. **Sentiment, news & secular trends** — sentiment score, analyst
   consensus & price targets, recent catalysts, industry trends.
5. **Technical analysis** — deterministic OHLC series, SMA 20/50/200,
   Bollinger bands, RSI, MACD, support/resistance, and explicit
   **entry zone / stop / target** levels.
6. **SWOT** — full strengths / weaknesses / opportunities / threats.
7. **Investment thesis & verdict** — bull / base / bear cases with
   probabilities, probability-weighted expected value, a 0–10 composite
   score (30% valuation, 20% quality, 20% moat, 15% sentiment,
   15% technicals) and a clear **"is it worth it at current levels?"**
   answer (STRONG BUY / BUY / HOLD-WAIT / WAIT-REDUCE / AVOID), with a
   valuation sanity cap so a strong moat can never justify buying a stock
   the model values well above price.

## Quick start

No dependencies beyond the Python 3.9+ standard library.

### CLI

```bash
cd Data-Analysis

# single or multiple tickers / company names
python -m stock_research_agent NVDA
python -m stock_research_agent "Inditex" "Apple" TTE.MC "Acme Technologies Corp"

# browse KB coverage
python -m stock_research_agent --list

# force the KB snapshot price (skip the live Stooq fetch)
python -m stock_research_agent NVDA --offline
```

Each run saves `stock_research_agent/reports/<TICKER>_research_report.html`
(open it in any browser — fully offline, no external assets).

### Web app

```bash
python -m stock_research_agent --serve --host 0.0.0.0 --port 8000
```

Then open http://localhost:8000 — search any ticker or company name, watch
the 7 pipeline stages run, get the verdict card, and open/download the
HTML report. Reports persist across restarts. The `POST /api/research`
body accepts `{"offline": true}` to skip the live price fetch.

### Python API

```python
from stock_research_agent import research, report_html

result = research.run("NVDA")            # or "Inditex", or any name
html   = report_html.build(result)       # standalone HTML string
path   = research.save_report(result, html)

v = result["verdict"]
print(v["label"], v["composite"], v["worth"])
```

## Coverage & data

- **63 hand-compiled profiles** (fundamentals/news as of October 2026):
  43 US/global (NVDA, AAPL, MSFT, GOOGL, AMZN, META, AVGO, TSM, TSLA, PLTR,
  SPCX, JPM, WMT, ASML, AMD, MU, LLY, UNH, BRK.A, …) and 20 European
  (ITX.MC, BBVA.MC, SAN.MC, BIC.MC, ACA.MC, TEP.MC, IBE.MC, ENAG.MC, ANA.MC,
  ACS.MC, TTE.MC, SAP, AIR.PA, NVO, SIE.DE, …).
- **Live price (optional, on by default):** at run time the agent fetches
  the latest close from Stooq's free CSV endpoint (no API key, stdlib
  `urllib`) and re-anchors every price-dependent field — price, market cap,
  P/E, fwd P/E, P/S, EV/EBITDA, dividend yield, 52-week range, and the whole
  technicals stack. A green **● LIVE** chip and a "Price is LIVE …" banner
  appear in the report. If the network is down or the symbol is unknown it
  silently falls back to the KB snapshot price and says so in the banner —
  the agent always works, offline or online. Force the snapshot with
  `--offline` (CLI) or `{"offline": true}` (API).
- **Name resolution**: ~200 curated aliases + S&P 500 name list fuzzy
  matching (`"Santander"` → `SAN.MC`, `"Inditex Group"` → `ITX.MC`).
- **Unknown names**: a seeded synthesizer derives a plausible profile from
  the sector rules and is clearly flagged **`data_quality: estimated`** in
  the report banner. Nothing is silently presented as verified data.
- Technicals are computed from a **deterministic seeded OHLC series**
  anchored to the current price (live when the feed is reachable, otherwise
  the KB snapshot) and the 52-week range — same inputs → same chart.

## Project layout

```
stock_research_agent/
├── __init__.py          # package metadata
├── __main__.py          # python3 -m entry
├── cli.py               # CLI: tickers | --list | --serve
├── indicators.py        # OHLC synthesis + SMA/Bollinger/RSI/MACD/ATR/S&R/zones
├── kb_us.py             # 43 US/global profiles (Oct 2026 data)
├── kb_eu.py             # 20 European profiles (Oct 2026 data)
├── knowledge_base.py    # aliases, name→ticker, fuzzy match, synthesizer
├── live_data.py         # live price quotes (Stooq CSV, stdlib urllib, cached)
├── research.py          # 7-stage pipeline, DCF, composite verdict
├── report_html.py       # standalone HTML builder (SVG charts, themes)
├── server.py            # ThreadingHTTPServer web app + JSON API
├── web/index.html       # UI: search, progress, verdict card, theme toggle
└── reports/             # generated HTML reports
```

## Verdict logic

| Composite | Label | Rule |
|---|---|---|
| ≥ 7.2 | STRONG BUY | |
| ≥ 5.8 | BUY | |
| ≥ 4.4 | HOLD / WAIT | |
| ≥ 3.2 | WAIT / REDUCE | |
| < 3.2 | AVOID | |

**Valuation sanity cap:** if model fair value is >15% below price, the
label is capped at HOLD / WAIT; >35% below, at WAIT / REDUCE — regardless
of how strong the moat and quality scores are.

## Disclaimer

Research-framework output: price is live (Stooq) when online, otherwise the
October 2026 snapshot; fundamentals/news are the locally compiled October
2026 KB; technicals are deterministic synthetic series. **Not investment
advice.** Verify against primary sources before acting.
