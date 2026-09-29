"""Router helpers — uniform {mode, source, ...data} envelopes."""
from __future__ import annotations

from fastapi import HTTPException

from .. import config


def ok(data: dict, mode: str, source: str) -> dict:
    return {"mode": mode, "source": source, **data}


def live_ok(data: dict, source: str) -> dict:
    return ok(data, "live", source)


def demo_ok(data: dict) -> dict:
    return ok(data, "demo", "simulated")


def unavailable(what: str) -> HTTPException:
    return HTTPException(status_code=502, detail=f"Live {what} unavailable (DEMO_MODE=never)")


def want_live() -> bool:
    return not config.demo_always()


def allow_demo() -> bool:
    return not config.demo_never()
