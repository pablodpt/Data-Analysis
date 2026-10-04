"""Tiny in-memory TTL cache — keeps us inside free-tier rate limits."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class _Entry:
    value: Any
    expires: float


_store: dict[str, _Entry] = {}


def get(key: str) -> Optional[Any]:
    e = _store.get(key)
    if e is None:
        return None
    if time.time() > e.expires:
        _store.pop(key, None)
        return None
    return e.value


def put(key: str, value: Any, ttl: int) -> None:
    _store[key] = _Entry(value, time.time() + max(ttl, 1))


def cached(ttl: int, key_fn: Callable[..., str]):
    """Decorator for sync/async provider functions returning data or None."""

    def wrap(fn):
        import asyncio
        import functools

        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def a(*a_, **k_):
                k = key_fn(*a_, **k_)
                v = get(k)
                if v is not None:
                    return v
                v = await fn(*a_, **k_)
                if v is not None:
                    put(k, v, ttl)
                return v

            return a

        @functools.wraps(fn)
        def s(*a_, **k_):
            k = key_fn(*a_, **k_)
            v = get(k)
            if v is not None:
                return v
            v = fn(*a_, **k_)
            if v is not None:
                put(k, v, ttl)
            return v

        return s

    return wrap


def clear() -> None:
    """Empty the cache (used by tests)."""
    _store.clear()
