"""FRED provider — keyless fredgraph.csv, richer API when FRED_API_KEY set."""
from __future__ import annotations

import csv
import io

import httpx

from .. import config
from ..cache import cached


@cached(config.TTL_ECON, lambda sid: f"fred:{sid.upper()}")
async def series(sid: str) -> dict | None:
    """Return {"points": [{t, v}]} or None."""
    sid = sid.upper()
    pts = await _via_api(sid) if config.FRED_API_KEY else None
    if pts is None:
        pts = await _via_csv(sid)
    if not pts:
        return None
    return {"points": pts}


async def _via_api(sid: str) -> list[dict] | None:
    try:
        async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT) as c:
            r = await c.get("https://api.stlouisfed.org/fred/series/observations",
                            params={"series_id": sid, "api_key": config.FRED_API_KEY,
                                    "file_type": "json"},
                            headers={"User-Agent": config.USER_AGENT})
        if r.status_code != 200:
            return None
        out = []
        for o in r.json().get("observations", []):
            try:
                out.append({"t": o["date"], "v": float(o["value"])})
            except (ValueError, TypeError, KeyError):
                continue
        return out or None
    except Exception:
        return None


async def _via_csv(sid: str) -> list[dict] | None:
    try:
        async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT) as c:
            r = await c.get("https://fred.stlouisfed.org/graph/fredgraph.csv",
                            params={"id": sid},
                            headers={"User-Agent": config.USER_AGENT})
        if r.status_code != 200 or "DATE" not in r.text[:500]:
            return None
        out = []
        for row in csv.DictReader(io.StringIO(r.text)):
            try:
                out.append({"t": row["DATE"], "v": float(row[sid])})
            except (ValueError, TypeError, KeyError):
                continue
        return out or None
    except Exception:
        return None
