"""OpenBerg — FastAPI app serving the JSON API + the static terminal frontend."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import config, demo
from .routers import econ, market, news_router, screener, security

app = FastAPI(title="OpenBerg Terminal", version="0.2.0",
              description="Free Bloomberg-style terminal API (stocks, news, macro).")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"])

app.include_router(security.router)
app.include_router(screener.router)
app.include_router(market.router)
app.include_router(news_router.router)
app.include_router(econ.router)

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": app.version, "demo_mode": config.DEMO_MODE}


@app.get("/api/status")
async def status():
    """Config + defaults the frontend needs at boot (no secrets exposed)."""
    d = demo.defaults()
    return {"demo_mode": config.DEMO_MODE,
            "has_fred_key": bool(config.FRED_API_KEY),
            "has_finnhub_key": bool(config.FINNHUB_API_KEY),
            "indices": d["indices"], "fred_series": d["fred_series"],
            "default_watchlist": d["default_watchlist"]}


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(FRONTEND / "index.html")


app.mount("/css", StaticFiles(directory=FRONTEND / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND / "js"), name="js")
