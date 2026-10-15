# -*- coding: utf-8 -*-
"""
research.py — The 7-stage autonomous research pipeline.

  Stage 1  Fundamentals, financial health & intrinsic valuation (DCF + multiples)
  Stage 2  Business model & revenue architecture
  Stage 3  Economic moat — 5-pillar scoring & rating
  Stage 4  Competitors & the MAIN DIFFERENCE against competitors
  Stage 5  Market sentiment, analyst consensus, recent news & secular trends
  Stage 6  Technical analysis (price action, SMAs, RSI, MACD, S/R, entry zones)
  Stage 7  SWOT + investment thesis (bull/base/bear) + "Is it worth it?" verdict
"""
from __future__ import annotations

import datetime as _dt
import math
from typing import Any, Dict

from . import indicators, live_data
from .knowledge_base import get_profile

REPORTS_DIR = "reports"  # relative to package dir, resolved in save_report


# ---------------------------------------------------------------------------
# Valuation
# ---------------------------------------------------------------------------

def run_dcf(fcf_ps: float, growth: float, terminal: float, rate: float,
            net_cash_ps: float = 0.0, years: int = 10) -> Dict[str, Any]:
    """Two-stage FCFE DCF (FCF after interest & net debt change, discounted at
    cost of equity) — values EQUITY directly, no net-cash add-back."""
    if not fcf_ps or fcf_ps <= 0:
        return None
    fcf = fcf_ps
    pv, schedule = 0.0, []
    g1 = min(max(growth, 0.01), 0.45)
    for t in range(1, years + 1):
        g = terminal + (g1 - terminal) * (0.82 ** (t - 1))
        fcf = fcf * (1 + g)
        pv_t = fcf / (1 + rate) ** t
        pv += pv_t
        schedule.append((t, round(fcf, 2), round(g * 100, 1), round(pv_t, 2)))
    tv = fcf * (1 + terminal) / max(1e-9, rate - terminal)
    pv_tv = tv / (1 + rate) ** years
    iv = pv + pv_tv
    return dict(fcf_ps=fcf_ps, growth=g1 * 100, terminal=terminal * 100,
                rate=rate * 100, net_cash_ps=net_cash_ps or 0.0,
                pv_fcf=pv, pv_terminal=pv_tv, iv_ps=iv, intrinsic_value=iv,
                schedule=schedule)


def multiple_value(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Growth-adjusted P/E method: target multiple blends today's P/E with a
    PEG-style multiple implied by revenue growth."""
    f = profile["fundamentals"]
    g = f.get("rev_g") or 0.0
    peg_pe = min(8.0 + 0.55 * g, 45.0)
    target_pe = max(10.0, min(50.0, 0.5 * f["pe"] + 0.5 * peg_pe))
    iv = f["eps"] * target_pe
    return dict(method="growth-adjusted P/E", target_pe=target_pe,
                intrinsic_value=iv, eps=f["eps"])


def valuation_fallback(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Fair value for DCF-inapplicable names (banks, insurers, conglomerates):
    KB model fair value when available, else sector P/E anchor."""
    f = profile["fundamentals"]
    if profile.get("fair_value_model"):
        return dict(method="model fair value (peer P/B + P/E; DCF n/a)",
                    intrinsic_value=profile["fair_value_model"], eps=f["eps"])
    pe_target = {"Financials": 13, "Banking & Financial Services": 12}.get(
        profile.get("sector", ""), 22)
    iv = f["eps"] * pe_target
    return dict(method="P/E multiple fallback", pe_target=pe_target,
                intrinsic_value=iv, eps=f["eps"])


# ---------------------------------------------------------------------------
# Stage builders
# ---------------------------------------------------------------------------

def stage_fundamentals(profile: Dict[str, Any]) -> Dict[str, Any]:
    f = profile["fundamentals"]
    cur = profile.get("currency", "USD")
    d = profile.get("dcf")
    dcf = run_dcf(d["fcf_ps"], d["g"], d["terminal"], d["rate"],
                  d.get("net_cash_ps", 0.0)) if d else None
    mult = multiple_value(profile)

    if dcf:
        # Blend: 50% DCF + 50% growth-adjusted P/E (standard multi-method FV)
        fair = 0.5 * dcf["intrinsic_value"] + 0.5 * mult["intrinsic_value"]
        val = dict(method="multi-method (50% DCF + 50% P/E)",
                   dcf_iv=dcf["intrinsic_value"], pe_iv=mult["intrinsic_value"],
                   intrinsic_value=fair, dcf=dcf, multiple=mult)
    else:
        val = valuation_fallback(profile)

    price = profile["price"]
    upside = (val["intrinsic_value"] / price - 1) * 100
    return dict(
        currency=cur, price=price,
        rev=f["rev"], rev_g=f["rev_g"], gm=f["gm"], opm=f["opm"],
        nm=f["nm"], eps=f["eps"], pe=f["pe"], fwd_pe=f["fwd_pe"],
        ps=f["ps"], ev_ebitda=f["ev_ebitda"], roic=f["roic"], roe=f["roe"],
        fcf=f["fcf"], cash=f.get("cash"), debt=f.get("debt"),
        div=f.get("div"), divy=f.get("divy"),
        dcf=dcf, valuation=val, upside=upside,
        quality_score=quality_score(f),
    )


def quality_score(f: Dict[str, Any]) -> float:
    s = 5.0
    nm = f.get("nm") or 0
    s += 2.5 if nm > 30 else 1.8 if nm > 20 else 1.0 if nm > 12 else 0.4 if nm > 5 else -1.0
    g = f.get("rev_g") or 0
    s += 1.5 if g > 25 else 1.0 if g > 12 else 0.5 if g > 5 else -0.8 if g < 0 else 0
    roic = f.get("roic") or 0
    s += 1.0 if roic > 25 else 0.5 if roic > 15 else 0
    if (f.get("cash") or 0) > (f.get("debt") or 0) and f.get("cash"):
        s += 0.8
    return max(0.0, min(10.0, s))


def stage_business(profile: Dict[str, Any]) -> Dict[str, Any]:
    return dict(biz=profile.get("biz", ""), segments=profile.get("segments", []),
                employees=profile.get("employees", "—"))


def stage_moat(profile: Dict[str, Any]) -> Dict[str, Any]:
    m = profile.get("moat", {})
    return dict(rating=m.get("rating", "No Moat"), score=m.get("score", 0.0),
                pillars=m.get("pillars", {}))


def stage_competitors(profile: Dict[str, Any]) -> Dict[str, Any]:
    return dict(peers=profile.get("competitors", []), edge=profile.get("edge", ""))


def stage_sentiment(profile: Dict[str, Any]) -> Dict[str, Any]:
    s = profile.get("sentiment", {})
    return dict(score=s.get("score", 5.0), consensus=s.get("consensus", "n/a"),
                pt=s.get("pt"), pt_lo=s.get("pt_lo"), pt_hi=s.get("pt_hi"),
                short=s.get("short", "n/a"),
                news=profile.get("news", []), trends=profile.get("trends", []))


def stage_technicals(profile: Dict[str, Any]) -> Dict[str, Any]:
    t = indicators.compute_technicals(
        profile["ticker"], profile["price"], profile["low52"], profile["high52"])
    # keep series out of the persisted JSON summary (report builder re-computes)
    t.pop("series", None)
    return t


def stage_swot_thesis(profile: Dict[str, Any]) -> Dict[str, Any]:
    sw = profile.get("swot", {})
    th = profile.get("thesis", {})
    bull, base, bear = (th.get("bull"), th.get("base"), th.get("bear"))
    cases = []
    for key, label, c in (("bull", "Bull", bull), ("base", "Base", base),
                          ("bear", "Bear", bear)):
        if not c:
            continue
        txt, target, prob = c
        cases.append(dict(label=label, case=txt, target=target, probability=prob,
                          key=key))
    return dict(swot=dict(
        strengths=sw.get("strengths", []), weaknesses=sw.get("weaknesses", []),
        opportunities=sw.get("opportunities", []), threats=sw.get("threats", [])),
        cases=cases)


# ---------------------------------------------------------------------------
# Composite scoring & verdict
# ---------------------------------------------------------------------------

def _upside_score(upside: float) -> float:
    if upside > 30:
        return 10.0
    if upside > 15:
        return 8.0
    if upside > 5:
        return 6.5
    if upside > 0:
        return 5.0
    if upside > -10:
        return 3.5
    return 1.5


def build_verdict(fund: Dict[str, Any], moat: Dict[str, Any],
                  sent: Dict[str, Any], tech: Dict[str, Any],
                  profile: Dict[str, Any]) -> Dict[str, Any]:
    q = fund["quality_score"]
    m = moat.get("score", 5.0)
    s = sent.get("score", 5.0)
    t = tech.get("score", 5.0)
    u = _upside_score(fund["upside"])
    composite = 0.30 * u + 0.20 * q + 0.20 * m + 0.15 * s + 0.15 * t

    if composite >= 7.2:
        label = "STRONG BUY"
    elif composite >= 5.8:
        label = "BUY"
    elif composite >= 4.4:
        label = "HOLD / WAIT"
    elif composite >= 3.2:
        label = "WAIT / REDUCE"
    else:
        label = "AVOID"

    # Valuation sanity cap: quality & moat cannot justify buying a stock the
    # model values at 15%+ below price (35%+ below for 'wait/reduce').
    order = ["AVOID", "WAIT / REDUCE", "HOLD / WAIT", "BUY", "STRONG BUY"]
    upside = fund["upside"]
    if upside < -35 and order.index(label) > order.index("WAIT / REDUCE"):
        label = "WAIT / REDUCE"
    elif upside < -15 and order.index(label) > order.index("HOLD / WAIT"):
        label = "HOLD / WAIT"

    price = profile["price"]
    iv = fund["valuation"]["intrinsic_value"]
    entry_lo, entry_hi = tech["entry_zone"]
    stop = tech["stop"]
    target12 = sent.get("pt") or tech["target"]

    if label in ("STRONG BUY", "BUY"):
        if upside >= -5:
            worth = (f"YES — worth buying at current levels. Composite {composite:.1f}/10. "
                     f"Fair value {iv:,.2f} vs. price {price:,.2f} "
                     f"({upside:+.1f}%). Build a position in the "
                     f"{entry_lo:,.2f}–{entry_hi:,.2f} zone with a stop at {stop:,.2f} "
                     f"and a 12-month target of {target12:,.2f}.")
        else:
            worth = (f"CAUTIOUS YES — excellent business and moat justify ownership, "
                     f"but the price already sits within {abs(upside):.0f}% of the "
                     f"model's fair value ({iv:,.2f} vs. {price:,.2f}). "
                     f"Composite {composite:.1f}/10. Prefer buying in the "
                     f"{entry_lo:,.2f}–{entry_hi:,.2f} zone or on a dip; a 12-month "
                     f"target of {target12:,.2f} implies limited upside here.")
    elif label == "HOLD / WAIT":
        worth = (f"NEUTRAL — fair to slightly full at {price:,.2f}. "
                 f"Fair value {iv:,.2f} ({upside:+.1f}%). Good business, "
                 f"unconvincing price — wait for a pullback into "
                 f"{entry_lo:,.2f}–{entry_hi:,.2f} or for the thesis "
                 f"(catalysts in §5) to confirm before committing new capital.")
    else:
        worth = (f"NO — not worth buying at {price:,.2f}. Composite {composite:.1f}/10 "
                 f"with fair value {iv:,.2f} ({upside:+.1f}%). Avoid new entries; "
                 f"existing holders should respect the {stop:,.2f} invalidation level.")

    # probability-weighted expected value from thesis cases
    cases = profile.get("thesis_cases", [])
    if cases:
        ev = sum(c["probability"] * c["target"] for c in cases)
        ev_gap = (ev / price - 1) * 100
    else:
        ev, ev_gap = None, None

    return dict(
        label=label, composite=round(composite, 2),
        components=dict(valuation=u, quality=q, moat=m, sentiment=s, technicals=t),
        worth=worth, iv=iv, entry_zone=tech["entry_zone"], stop=stop,
        target_12m=target12, expected_value=ev, ev_gap=ev_gap,
        technical_signal=tech.get("signal", ""),
    )


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def rebase_price(profile: Dict[str, Any], new_price: float) -> Dict[str, Any]:
    """Return a copy of the profile with price-dependent fields scaled to a
    live quote. Fundamental levels (revenue, margins, FCF, debt, EPS) stay on
    the KB snapshot; only market-ratio fields are re-anchored to the price."""
    p = dict(profile)
    old = profile["price"] or new_price
    r = new_price / old if old else 1.0
    f = dict(profile["fundamentals"])
    p["price"] = new_price
    p["market_cap"] = profile["market_cap"] * r
    p["low52"] = min(profile["low52"], new_price)
    p["high52"] = max(profile["high52"], new_price)
    if f.get("pe") and f.get("eps"):
        f["pe"] = round(new_price / f["eps"], 1)
    if f.get("fwd_pe"):
        f["fwd_pe"] = round(f["fwd_pe"] * r, 1)
    if f.get("ps"):
        f["ps"] = round(f["ps"] * r, 2)
    if f.get("ev_ebitda"):
        f["ev_ebitda"] = round(f["ev_ebitda"] * r, 1)
    if f.get("divy"):
        f["divy"] = round(f["divy"] / r, 2)
    p["fundamentals"] = f
    return p


def run(query: str, offline: bool = False) -> Dict[str, Any]:
    profile = get_profile(query)
    ticker = profile["ticker"]

    # Live price (Stooq) when online; falls back to the KB snapshot on any
    # failure so the agent always works, even fully offline.
    live = None if offline else live_data.get_quote(ticker,
                                                    profile.get("currency", "USD"))
    if live and live.get("close"):
        profile = rebase_price(profile, live["close"])
        profile["live_quote"] = live

    fund = stage_fundamentals(profile)
    biz = stage_business(profile)
    moat = stage_moat(profile)
    comp = stage_competitors(profile)
    sent = stage_sentiment(profile)
    tech = stage_technicals(profile)
    swot_thesis = stage_swot_thesis(profile)

    profile["thesis_cases"] = swot_thesis["cases"]
    verdict = build_verdict(fund, moat, sent, tech, profile)

    now = _dt.datetime.now()
    lq = profile.get("live_quote")
    if lq:
        price_source = f"LIVE — Stooq {lq['symbol']} (close {lq['date']} {lq['time']})"
    else:
        price_source = "KB snapshot — October 15, 2026 (no live feed)"
    return dict(
        meta=dict(
            ticker=ticker, name=profile["name"], sector=profile["sector"],
            industry=profile.get("industry", profile["sector"]),
            country=profile.get("country", "US"), currency=profile.get("currency", "USD"),
            exchange=profile.get("exchange", ""), website=profile.get("website", ""),
            price=profile["price"], market_cap=profile["market_cap"],
            data_quality=profile.get("data_quality", "verified"),
            price_source=price_source,
            price_live=bool(lq),
            generated_at=now.strftime("%Y-%m-%d %H:%M"),
            data_as_of=("price: " + (lq["date"] if lq else "October 2026")
                        + " | fundamentals/news: local intelligence KB (Oct 2026)"),
            low52=profile["low52"], high52=profile["high52"],
        ),
        verdict=verdict,
        stages=dict(
            fundamentals=fund, business=biz, moat=moat, competitors=comp,
            sentiment=sent, technicals=tech, swot_thesis=swot_thesis,
        ),
        _profile=profile,
    )


def summary_lines(result: Dict[str, Any]) -> list:
    """Compact console summary for CLI output."""
    m, v = result["meta"], result["verdict"]
    f, tech = result["stages"]["fundamentals"], result["stages"]["technicals"]
    cur = m["currency"]
    L = []
    L.append("=" * 78)
    L.append(f"  {m['name']}  [{m['ticker']}]   {m['sector']} — {m['industry']}")
    live_tag = "  [LIVE price]" if m.get("price_live") else ""
    L.append(f"  Price {m['price']:,.2f} {cur}{live_tag}   Mkt Cap {m['market_cap']/1e9:,.0f}B "
             f"   52w {m['low52']:,.2f}–{m['high52']:,.2f}   ({m['data_quality']})")
    L.append(f"  Price source: {m.get('price_source', 'n/a')}")
    L.append("-" * 78)
    L.append(f"  VERDICT:  {v['label']}   (composite {v['composite']}/10)")
    L.append(f"  Fair value (DCF/multiple): {v['iv']:,.2f} {cur}  "
             f"→ upside {f['upside']:+.1f}%")
    L.append(f"  Moat: {result['stages']['moat']['rating']} "
             f"({result['stages']['moat']['score']}/10)   "
             f"Sentiment: {result['stages']['sentiment']['score']}/10 "
             f"({result['stages']['sentiment']['consensus']})")
    L.append(f"  Technicals: {tech['trend']}, RSI {tech['rsi']:.0f}, "
             f"{tech['macd_state']}, signal {tech['signal']}")
    L.append(f"  Zones: entry {v['entry_zone'][0]:,.2f}–{v['entry_zone'][1]:,.2f}, "
             f"stop {v['stop']:,.2f}, 12m target {v['target_12m']:,.2f}")
    L.append("-" * 78)
    L.append("  " + v["worth"])
    L.append("=" * 78)
    return L


def save_report(result: Dict[str, Any], html: str) -> str:
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(here, REPORTS_DIR)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{result['meta']['ticker']}_research_report.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path
