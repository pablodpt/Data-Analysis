# Marketwatch dashboard

A responsive, interactive stock-market overview concept built with vanilla HTML, CSS, and JavaScript. It includes major US indices, a performance chart with time-range controls, market movers, key market values, and a searchable/editable watchlist.

## Run locally

Requires Python 3. From this folder, run:

```bash
python server.py
```

Then open `http://localhost:8000`. You can also open `index.html` directly in a browser; some browsers restrict local-file scripts, so the server is recommended.

## Data note

All prices, percentage changes, chart points, and dates are **illustrative sample values**, not live or historical quotes. The interface prominently labels the demo data so it cannot be mistaken for a real-time feed. A production version needs a market-data provider and its licensing/API credentials; the quote objects in `app.js` are the intended integration point. Do not use this demo for trading or investment decisions.
