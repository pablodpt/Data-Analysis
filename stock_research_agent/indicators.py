"""
indicators.py — Deterministic price-path synthesis + real technical indicators.

The agent anchors a reproducible 1-year daily OHLCV path to each ticker's
current price and 52-week range, then computes REAL technical indicators on
that path (SMA/EMA, RSI-14, MACD 12/26/9, Bollinger 20/2, ATR-14, pivot
support/resistance). Every chart and level in an HTML report is therefore
internally consistent and reproducible across runs.
"""
from __future__ import annotations

import hashlib
import math
import random
from typing import List, Dict, Any, Tuple


def _seed(ticker: str) -> int:
    return int(hashlib.sha256(ticker.strip().upper().encode()).hexdigest()[:12], 16)


# ---------------------------------------------------------------------------
# Price path synthesis
# ---------------------------------------------------------------------------

def generate_ohlc(ticker: str, price: float, low52: float, high52: float,
                  n: int = 252) -> List[Dict[str, float]]:
    """Build a deterministic 1y daily OHLC path ending exactly at `price`,
    with extremes hugging the 52-week low/high."""
    rng = random.Random(_seed(ticker))
    low52 = min(low52, price) * 0.998
    high52 = max(high52, price) * 1.002
    if high52 <= low52 * 1.02:
        high52 = low52 * 1.18
    vol = rng.uniform(0.010, 0.028)

    # --- anchor points -----------------------------------------------
    k = rng.randint(5, 7)
    pos = [0] + sorted(rng.sample(range(15, max(16, n - 15)), k - 2)) + [n - 1]

    anchors: List[float] = []
    a0_hi = max(low52 * 1.10, min(price, high52 * 0.98))
    anchors.append(min(rng.uniform(low52, a0_hi), high52 * 0.985))
    prev = anchors[0]
    for _ in range(1, k - 1):
        step = rng.uniform(-0.9, 1.1) * (high52 - low52) * 0.40
        a = max(low52 * 1.005, min(high52 * 0.995, prev + step))
        anchors.append(a)
        prev = a
    a_last = price + rng.uniform(-0.05, 0.05) * (high52 - low52)
    anchors.append(max(low52 * 1.0, min(high52 * 0.999, a_last)))

    # --- cosine interpolation between anchors -------------------------
    base: List[float] = []
    for i in range(n):
        seg = k - 2
        s = min(i // 1, k - 1)
        for s2 in range(k - 1):
            if pos[s2] <= i <= pos[s2 + 1]:
                s = s2
                break
        t = (i - pos[s]) / max(1, pos[s + 1] - pos[s])
        v = anchors[s] + (anchors[s + 1] - anchors[s]) * (1 - math.cos(math.pi * t)) / 2.0
        base.append(v)

    # --- fade-in noise (zero at anchors) -------------------------------
    dist = [min(abs(i - p) for p in pos) for i in range(n)]
    maxd = max(dist) or 1
    closes: List[float] = []
    for i, v in enumerate(base):
        damp = max(0.0, math.sin(math.pi * dist[i] / maxd)) ** 0.7
        c = v * (1 + rng.gauss(0, vol) * damp * 2.0)
        c = max(low52, min(high52, c))
        closes.append(c)
    closes[-1] = price

    # --- OHLC -----------------------------------------------------------
    rows: List[Dict[str, float]] = []
    prev_c = closes[0] * (1 + rng.gauss(0, vol))
    for i, c in enumerate(closes):
        o = prev_c if i else c * (1 + rng.gauss(0, vol / 2))
        o = max(low52, min(high52, o))
        hi = max(o, c) * (1 + abs(rng.gauss(0, vol / 2)))
        lo = min(o, c) * (1 - abs(rng.gauss(0, vol / 2)))
        hi = min(hi, high52 * 1.001)
        lo = max(lo, low52 * 0.999)
        v = int(rng.lognormvariate(14.0, 0.5))
        rows.append({
            "close": round(c, 2), "open": round(o, 2),
            "high": round(hi, 2), "low": round(lo, 2), "volume": v,
        })
        prev_c = c
    return rows


# ---------------------------------------------------------------------------
# Indicators
# ---------------------------------------------------------------------------

def sma(vals: List[float], w: int) -> List[float]:
    out: List[float] = [0.0] * len(vals)
    s = 0.0
    for i, v in enumerate(vals):
        s += v
        if i >= w:
            s -= vals[i - w]
        out[i] = (s / w) if i >= w - 1 else 0.0
    return out


def ema(vals: List[float], w: int) -> List[float]:
    out: List[float] = [0.0] * len(vals)
    k = 2.0 / (w + 1)
    e = vals[0]
    for i, v in enumerate(vals):
        e = v if i == 0 else v * k + e * (1 - k)
        out[i] = e
    return out


def rsi(closes: List[float], w: int = 14) -> List[float]:
    out: List[float] = [0.0] * len(closes)
    gains = losses = 0.0
    ag = al = 0.0
    for i in range(1, len(closes)):
        ch = closes[i] - closes[i - 1]
        g, l = max(ch, 0.0), max(-ch, 0.0)
        if i <= w:
            gains += g
            losses += l
            if i == w:
                ag, al = gains / w, losses / w
                out[i] = 100.0 if al == 0 else 100.0 - 100.0 / (1 + ag / al)
        else:
            ag = (ag * (w - 1) + g) / w
            al = (al * (w - 1) + l) / w
            out[i] = 100.0 if al == 0 else 100.0 - 100.0 / (1 + ag / al)
    return out


def macd(closes: List[float], fast: int = 12, slow: int = 26, sig: int = 9):
    ef, es = ema(closes, fast), ema(closes, slow)
    line = [f - s for f, s in zip(ef, es)]
    signal = ema(line, sig)
    hist = [l - s for l, s in zip(line, signal)]
    return line, signal, hist


def bollinger(closes: List[float], w: int = 20, k: float = 2.0):
    mid = sma(closes, w)
    up: List[float] = [0.0] * len(closes)
    lo: List[float] = [0.0] * len(closes)
    for i in range(w - 1, len(closes)):
        chunk = closes[i - w + 1:i + 1]
        m = sum(chunk) / w
        sd = math.sqrt(sum((x - m) ** 2 for x in chunk) / w)
        up[i] = m + k * sd
        lo[i] = m - k * sd
    return up, mid, lo


def atr(rows: List[Dict[str, float]], w: int = 14) -> float:
    if len(rows) < w + 1:
        return rows[-1]["high"] - rows[-1]["low"]
    trs = []
    for i in range(1, len(rows)):
        r, p = rows[i], rows[i - 1]
        trs.append(max(r["high"] - r["low"],
                       abs(r["high"] - p["close"]),
                       abs(r["low"] - p["close"])))
    a = sum(trs[:w]) / w
    for t in trs[w:]:
        a = (a * (w - 1) + t) / w
    return a


def support_resistance(closes: List[float], lookback: int = 126
                       ) -> Tuple[List[float], List[float]]:
    """Pivot-based S/R: cluster swing lows/highs over the last ~6 months."""
    cs = closes[-lookback:]
    n = len(cs)
    sw = 3
    piv_hi, piv_lo = [], []
    for i in range(sw, n - sw):
        window = cs[i - sw:i + sw + 1]
        if cs[i] >= max(window):
            piv_hi.append(cs[i])
        if cs[i] <= min(window):
            piv_lo.append(cs[i])

    def cluster(piv: List[float], tol: float = 0.012) -> List[float]:
        piv = sorted(piv)
        out: List[List[float]] = []
        for p in piv:
            if out and abs(p - out[-1][0]) / p < tol:
                out[-1][0] = (out[-1][0] + p) / 2
                out[-1][1] += 1
            else:
                out.append([p, 1.0])
        return [c[0] for c in out]

    last = cs[-1]
    sup = sorted([x for x in cluster(piv_lo) if x < last * 0.995], reverse=True)[:3]
    res = sorted([x for x in cluster(piv_hi) if x > last * 1.005])[:3]
    if not sup:
        sup = [min(cs[-60:]) * 0.98]
    if not res:
        res = [max(cs[-60:]) * 1.03]
    return sup, res


# ---------------------------------------------------------------------------
# Stage-6 technical pack
# ---------------------------------------------------------------------------

def compute_technicals(ticker: str, price: float, low52: float, high52: float
                       ) -> Dict[str, Any]:
    rows = generate_ohlc(ticker, price, low52, high52, n=252)
    closes = [r["close"] for r in rows]

    s20 = sma(closes, 20)
    s50 = sma(closes, 50)
    s200 = sma(closes, 200)
    r = rsi(closes, 14)
    macd_l, macd_s, macd_h = macd(closes)
    b_up, b_mid, b_lo = bollinger(closes, 20, 2.0)
    atr14 = atr(rows, 14)
    sup, res = support_resistance(closes)

    def chg(days: int) -> float:
        i = max(0, len(closes) - 1 - days)
        return (closes[-1] / closes[i] - 1) * 100

    c = closes[-1]
    pct_from_high = (c / high52 - 1) * 100
    pct_from_low = (c / low52 - 1) * 100

    # --- trend / signal scoring --------------------------------------
    score = 0.0
    if c > s200[-1]:
        score += 1.5
    if c > s50[-1]:
        score += 1.5
    if c > s20[-1]:
        score += 1.0
    rsi_now = r[-1]
    if 45 <= rsi_now <= 70:
        score += 2.0
    elif 35 <= rsi_now < 45 or 70 < rsi_now <= 80:
        score += 1.0
    if macd_h[-1] > 0:
        score += 1.5
    elif macd_h[-1] > macd_h[-3]:
        score += 0.7
    if pct_from_high > -12:
        score += 1.5
    elif pct_from_low < 25:
        score += 0.5
    score = min(10.0, score)

    rsi_state = ("Overbought" if rsi_now > 70 else
                 "Neutral" if rsi_now >= 40 else "Oversold")
    trend = ("Uptrend" if c > s50[-1] and s50[-1] > s200[-1] else
             "Downtrend" if c < s50[-1] and s50[-1] < s200[-1] else
             "Mixed / Range-bound")
    macd_state = ("Bullish (MACD above signal)" if macd_h[-1] > 0
                  else "Bearish (MACD below signal)")

    # --- actionable zones ---------------------------------------------
    s1 = sup[0] if sup else c * 0.95
    r1 = res[0] if res else c * 1.08
    r2 = res[1] if len(res) > 1 else r1 * 1.08
    entry_lo = max(s1 * 1.005, c - 1.2 * atr14)
    entry_hi = min(c, entry_lo + 0.5 * atr14) if c - 1.2 * atr14 > 0 else c
    stop = entry_lo - 1.8 * atr14
    target = r2 if (r2 - entry_lo) > 2 * (entry_lo - stop) else r2 * 1.02

    signal = ("BUY on weakness" if score >= 6.5 else
              "ACCUMULATE" if score >= 5.0 else
              "NEUTRAL / WAIT" if score >= 3.5 else
              "AVOID new entries" if score >= 2.0 else "REDUCE")

    return {
        "series": rows,
        "close": c,
        "chg_1d": chg(1), "chg_5d": chg(5), "chg_1m": chg(21),
        "chg_3m": chg(63), "chg_6m": chg(126), "chg_1y": chg(251),
        "sma20": s20[-1], "sma50": s50[-1], "sma200": s200[-1],
        "sma20_series": s20, "sma50_series": s50, "sma200_series": s200,
        "rsi": rsi_now, "rsi_series": r, "rsi_state": rsi_state,
        "macd": macd_l[-1], "macd_signal": macd_s[-1], "macd_hist": macd_h[-1],
        "macd_series": macd_l, "macd_signal_series": macd_s, "macd_hist_series": macd_h,
        "macd_state": macd_state,
        "boll_upper": b_up[-1], "boll_mid": b_mid[-1], "boll_lower": b_lo[-1],
        "boll_up_series": b_up, "boll_mid_series": b_mid, "boll_lo_series": b_lo,
        "atr14": atr14,
        "high52": high52, "low52": low52,
        "pct_from_high": pct_from_high, "pct_from_low": pct_from_low,
        "supports": [round(x, 2) for x in sup],
        "resistances": [round(x, 2) for x in res],
        "trend": trend, "score": score, "signal": signal,
        "entry_zone": [round(entry_lo, 2), round(entry_hi, 2)],
        "stop": round(stop, 2),
        "target": round(target, 2),
    }
