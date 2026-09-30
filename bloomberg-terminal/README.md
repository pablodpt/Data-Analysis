# OpenBerg — a free Bloomberg-style terminal

A Bloomberg-terminal-style web app for **stocks, news and macro** — powered 100% by
**free data sources**. Runs locally, no build step, no paid API required.

![status](https://img.shields.io/badge/data-free%20%7C%20delayed-orange) ![stack](https://img.shields.io/badge/stack-FastAPI%20%2B%20vanilla%20JS-black)

> **Not affiliated with Bloomberg L.P.** Educational project. All quotes are
> delayed and may be inaccurate — not investment advice.

---

## What you get (Bloomberg function map)

| Type it | Bloomberg equiv. | What it does |
|---|---|---|
| `TOP` | `TOP` | Market overview: indices, breadth, movers, heatmap |
| `AAPL` then `GP` | `AAPL US EQUITY GP` | Price chart (candles/line, volume, SMA, ranges, log scale) |
| `MSFT DES` | `DES` | Security description, profile, key stats |
| `NVDA FA` | `FA` | Financial analysis: income / balance / cash-flow, ratios, earnings |
| `SCR` | `EQS` | Stock screener: 112-symbol universe, value / yield / momentum filters + presets |
| `N TSLA` / `NEWS` | `N` | Symbol + market news feed |
| `ECO` | `ECO` | Economic calendar + FRED charts (GDP, CPI, jobs, Fed funds, yields) |
| `W` | `W` / `WL` | Your watchlist with live quotes, sparklines, day change |
| `HELP` | `HELP` | Command cheat-sheet |

Plus: ticker **search with autocomplete**, **CSV export**, price **alerts** (browser),
keyboard-first command bar (`/` to focus, `Enter` to run), and a brutalist
black-and-amber Bloomberg look. Zero frontend dependencies — no CDN, works offline.

## Quickstart

```bash
cd bloomberg-terminal
pip install -r requirements.txt
cp .env.example .env        # optional — works without keys in demo/hybrid mode
./run.sh                    # or: uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Then open **http://localhost:8000**.

> 🇪🇸 ¿Lo instalas en tu laptop? Guía paso a paso en español:
> **[INSTALACION.md](INSTALACION.md)** — sin copiar archivos, sin pagar nada.

### Docker

```bash
docker build -t openberg .
docker run -p 8000:8000 --env-file .env openberg
```

## Data modes

The backend always responds — it degrades gracefully and tells you which mode
each response came from (shown as a `LIVE` / `DEMO` badge in the UI):

1. **LIVE** — real data from free providers (needs internet; some endpoints
   work better with free API keys, see below).
2. **DEMO** — deterministic, realistic simulated data (seeded random-walk) so
   the UI is fully explorable offline. Used automatically when offline or when
   a provider fails, or forced with `DEMO_MODE=always`.

```
DEMO_MODE=auto     # live when possible, demo fallback (default)
DEMO_MODE=always   # force demo (offline development, screenshots)
DEMO_MODE=never    # live only (API errors surface as errors)
```

## Free API keys (optional, recommended)

You don't need any key to run the app — but two free keys unlock the best data:

| Key | What it unlocks | How to get it (free) |
|---|---|---|
| `FRED_API_KEY` | 800k+ macro series, 120 req/min [1](https://apis.io/plans/fred/fred-plans-pricing/) | Register at `fred.stlouisfed.org/docs/api/api_key.html`, key is instant & free [2](https://github.com/armanobosyan/FRED-API-ID-Fetcher) |
| `FINNHUB_API_KEY` | Real-time US quotes, company news, econ calendar, ~60 calls/min, no credit card [3](https://apicostcalc.com/finnhub.html) | Sign up at `finnhub.io`, free for personal use [4](https://thenextgennexus.com/2026/05/15/10-best-free-stock-market-apis-2026/) |

Put them in `.env`:

```ini
FRED_API_KEY=your_32_char_fred_key
FINNHUB_API_KEY=your_finnhub_key
```

### Keyless sources used (no signup)

- **Stooq** — keyless CSV quotes & daily history (fallback price engine).
- **Yahoo Finance** (via `yfinance`) — quotes, history, info, financials, news.
  Unofficial endpoint; can be rate-limited — the app falls back automatically.
- **FRED `fredgraph.csv`** — keyless CSV for headline macro series.
- **SEC EDGAR** — keyless company facts & filings (`User-Agent` required).
- **Google News RSS** — keyless news search per ticker.

Expected delays on free tiers: ~15 min for quotes, end-of-day for some series.

## Commands

```
AAPL            load Apple, open price chart (GP)
AAPL GP         price chart          MSFT DES   description
NVDA FA         financials           N TSLA     news for Tesla
TOP             market overview      ECO        econ calendar + indicators
SCR             stock screener       W          watchlist
HELP            this help
"apple"         search (or just type + pick autocomplete)
```

You can also type Bloomberg-style `AAPL US EQUITY GP` — country/market words are ignored.

Keyboard: `/` focus command · `Enter` run · `Esc` clear · `Alt+1..9` jump to function.

## Project structure

```
bloomberg-terminal/
├── backend/
│   ├── main.py            # FastAPI app + static frontend serving
│   ├── config.py          # env settings (.env)
│   ├── cache.py           # tiny TTL cache (avoids hammering free tiers)
│   ├── demo.py            # deterministic demo-data generator (offline mode)
│   ├── providers/         # yahoo.py stooq.py fred.py finnhub.py sec.py news_rss.py
│   └── routers/           # market.py security.py news_router.py econ.py
├── frontend/
│   ├── index.html
│   ├── css/styles.css     # Bloomberg black/amber theme
│   └── js/  api.js charts.js views.js app.js   # zero-dependency vanilla JS
├── data/defaults.json     # indices, FRED series, watchlist defaults, calendar rules
├── tests/                 # pytest (runs fully offline in DEMO_MODE=always)
├── requirements.txt  .env.example  Dockerfile  run.sh
└── README.md
```

## API (backend)

All endpoints return JSON with a `mode` field (`live` | `demo` | `cache`).

```
GET /api/health
GET /api/search?q=apple
GET /api/quote?symbol=AAPL            POST /api/quotes  {"symbols":[...]}
GET /api/history?symbol=AAPL&range=1Y&interval=1d
GET /api/profile?symbol=AAPL
GET /api/financials?symbol=AAPL&statement=income&period=annual
GET /api/earnings?symbol=AAPL
GET /api/screener/universe         POST /api/screener/run  (filters, sort, limit)
GET /api/news?symbol=AAPL&limit=20    GET /api/news/market?limit=20
GET /api/market/overview              GET /api/market/movers?group=gainers
GET /api/econ/indicators              GET /api/econ/series?id=DGS10
GET /api/econ/calendar?days=14
```

Interactive docs: **http://localhost:8000/docs**

## Roadmap

- [x] Screener (filter 112-symbol universe by P/E, yield, momentum, sector…)
- [ ] Portfolio tracker with cost basis + P&L
- [ ] FX / crypto / commodities tabs
- [ ] Earnings calendar + transcripts
- [ ] Alert rules (server-side, email/webhook)
- [ ] Export to Excel / Sheets, embeddable widgets

## Disclaimer

Delayed, possibly inaccurate free data for education only. Not investment advice.
Bloomberg® and Bloomberg Terminal® are trademarks of Bloomberg L.P.; this project
is an independent homage and is not affiliated with or endorsed by Bloomberg.
