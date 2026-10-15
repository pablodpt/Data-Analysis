# -*- coding: utf-8 -*-
"""
report_html.py — Self-contained standalone HTML report builder.

Produces a single file with inline CSS + vanilla JS (no external deps):
  * dark/light theme toggle (persisted in localStorage)
  * interactive SVG price chart (price + SMA 20/50/200 + Bollinger + S/R)
  * RSI and MACD panels, computed from the same deterministic series
  * KPI cards, 5-pillar moat bars, peer table, news timeline, SWOT grid,
    bull/base/bear thesis cards and the "Is it worth it?" verdict panel
"""
from __future__ import annotations

import html as _html
from typing import Any, Dict, List

from . import indicators


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def esc(x) -> str:
    return _html.escape(str(x), quote=True)


def money(x, cur: str, dec: int = 2) -> str:
    if x is None:
        return "—"
    return f"{x:,.{dec}f} {cur}"


def bcap(x) -> str:
    if x is None:
        return "—"
    if x >= 1e12:
        return f"${x/1e12:,.2f}T"
    return f"${x/1e9:,.0f}B"


def pct(x, dec: int = 1) -> str:
    if x is None:
        return "—"
    return f"{x:+.{dec}f}%"


def _pts(series: List[float], x0: float, y0: float, w: float, h: float,
         lo: float, hi: float, skip_zero: bool = True) -> str:
    if hi - lo < 1e-9:
        hi = lo + 1
    pts = []
    for i, v in enumerate(series):
        if skip_zero and v == 0:
            continue
        x = x0 + w * i / max(1, len(series) - 1)
        y = y0 + h * (1 - (v - lo) / (hi - lo))
        pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts)


def _area(series: List[float], x0: float, y0: float, w: float, h: float,
          lo: float, hi: float) -> str:
    pts = _pts(series, x0, y0, w, h, lo, hi)
    if not pts:
        return ""
    last_x = x0 + w
    first = pts.split()[0]
    return f"{first} {pts} {last_x:.1f},{y0 + h} {first.split(',')[0]},{y0 + h}"


# ---------------------------------------------------------------------------
# SVG chart builders
# ---------------------------------------------------------------------------

def svg_price_chart(ticker: str, price: float, low52: float, high52: float) -> str:
    rows = indicators.generate_ohlc(ticker, price, low52, high52, 252)
    closes = [r["close"] for r in rows]
    s20 = indicators.sma(closes, 20)
    s50 = indicators.sma(closes, 50)
    s200 = indicators.sma(closes, 200)
    bup, bmid, blo = indicators.bollinger(closes, 20, 2.0)
    sup, res = indicators.support_resistance(closes)

    W, H, PAD = 920, 340, 10
    lo = min(min(closes), min(x for x in blo if x > 0)) * 0.995
    hi = max(max(closes), max(bup)) * 1.005

    def py(v):
        return PAD + (H - 2 * PAD) * (1 - (v - lo) / (hi - lo))

    grid, labels = [], []
    for i in range(5):
        v = lo + (hi - lo) * i / 4
        y = py(v)
        grid.append(f'<line x1="0" y1="{y:.0f}" x2="{W}" y2="{y:.0f}" class="grid"/>')
        labels.append(f'<text x="{W-4}" y="{y-4:.0f}" class="axis" text-anchor="end">{v:,.2f}</text>')

    months = []
    for i in range(0, 252, 42):
        months.append(f'<line x1="{(W*i/251):.0f}" y1="{PAD}" x2="{(W*i/251):.0f}" y2="{H-PAD}" class="grid"/>')

    h_lines = []
    for v, cls, lab in ((high52, "hi", "52w High"), (low52, "lo", "52w Low")):
        y = py(v)
        h_lines.append(f'<line x1="0" y1="{y:.0f}" x2="{W}" y2="{y:.0f}" class="{cls}"/>'
                       f'<text x="6" y="{y-4:.0f}" class="tag-{cls}">{lab} {v:,.2f}</text>')
    for i, v in enumerate(res[:2]):
        y = py(v)
        h_lines.append(f'<line x1="0" y1="{y:.0f}" x2="{W}" y2="{y:.0f}" class="res"/>'
                       f'<text x="6" y="{y+11:.0f}" class="tag-res">R{i+1} {v:,.2f}</text>')
    for i, v in enumerate(sup[:2]):
        y = py(v)
        h_lines.append(f'<line x1="0" y1="{y:.0f}" x2="{W}" y2="{y:.0f}" class="sup"/>'
                       f'<text x="6" y="{y+11:.0f}" class="tag-sup">S{i+1} {v:,.2f}</text>')

    svg = f'''<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="12-month price chart">
      {''.join(grid)}{''.join(months)}{''.join(h_lines)}
      <polygon points="{_area(bup, 0, PAD, W, H-2*PAD, lo, hi)}" class="boll-fill"/>
      <polyline points="{_pts(bup, 0, PAD, W, H-2*PAD, lo, hi)}" class="boll-up"/>
      <polyline points="{_pts(blo, 0, PAD, W, H-2*PAD, lo, hi)}" class="boll-lo"/>
      <polyline points="{_pts(s200, 0, PAD, W, H-2*PAD, lo, hi)}" class="sma200"/>
      <polyline points="{_pts(s50, 0, PAD, W, H-2*PAD, lo, hi)}" class="sma50"/>
      <polyline points="{_pts(s20, 0, PAD, W, H-2*PAD, lo, hi)}" class="sma20"/>
      <polyline points="{_pts(closes, 0, PAD, W, H-2*PAD, lo, hi)}" class="price"/>
      <circle cx="{W-2}" cy="{py(closes[-1]):.0f}" r="3.5" class="dot"/>
      {''.join(labels)}
    </svg>
    <div class="legend">
      <span><i class="sw sw-price"></i>Price</span>
      <span><i class="sw sw-20"></i>SMA 20</span>
      <span><i class="sw sw-50"></i>SMA 50</span>
      <span><i class="sw sw-200"></i>SMA 200</span>
      <span><i class="sw sw-boll"></i>Bollinger 20/2</span>
      <span><i class="sw sw-sup"></i>Support</span>
      <span><i class="sw sw-res"></i>Resistance</span>
    </div>'''
    return svg


def _mini_panel(title: str, series: List[float], ref: float = None,
                W: int = 920, H: int = 96, ref_label: str = "0") -> str:
    vals = [v for v in series if v is not None]
    lo, hi = min(vals + ([ref] if ref is not None else [])), max(vals + ([ref] if ref is not None else []))
    if hi - lo < 1e-9:
        hi = lo + 1
    pad = 6
    def py(v):
        return pad + (H - 2 * pad) * (1 - (v - lo) / (hi - lo))
    extra = ""
    if ref is not None:
        y = py(ref)
        extra = f'<line x1="0" y1="{y:.0f}" x2="{W}" y2="{y:.0f}" class="ref"/>'
    return f'''<svg viewBox="0 0 {W} {H}" class="chart mini" role="img" aria-label="{esc(title)}">
      {extra}
      <polyline points="{_pts(series, 0, pad, W, H-2*pad, lo, hi)}" class="line-accent"/>
      <text x="6" y="14" class="tag-title">{esc(title)}  <tspan class="axis">({lo:,.0f} … {hi:,.0f})</tspan></text>
    </svg>'''


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _kpi(label: str, value: str, sub: str = "", tone: str = "") -> str:
    return (f'<div class="kpi {tone}"><div class="kpi-label">{esc(label)}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-sub">{esc(sub)}</div></div>')


def _bar(label: str, score: float, note: str) -> str:
    w = max(0.0, min(10.0, score)) * 10
    cls = "good" if score >= 7 else "mid" if score >= 5 else "bad"
    return (f'<div class="pillar"><div class="pillar-head"><span>{esc(label)}</span>'
            f'<span class="pill-score">{score:.1f}/10</span></div>'
            f'<div class="bar"><div class="bar-fill {cls}" style="width:{w:.0f}%"></div></div>'
            f'<div class="pillar-note">{esc(note)}</div></div>')


def _row(k: str, v: str) -> str:
    return f'<tr><td class="rk">{esc(k)}</td><td class="rv">{v}</td></tr>'


def section_header(num: str, title: str, subtitle: str) -> str:
    return (f'<header class="sec-head"><div class="sec-num">{num}</div>'
            f'<div><h2>{esc(title)}</h2><p class="sec-sub">{esc(subtitle)}</p></div></header>')


def build(result: Dict[str, Any]) -> str:
    m = result["meta"]
    v = result["verdict"]
    st = result["stages"]
    fund, tech = st["fundamentals"], st["technicals"]
    moat, sent = st["moat"], st["sentiment"]
    comp, sw = st["competitors"], st["swot_thesis"]
    cur = m["currency"]
    price = m["price"]

    # ---------------- KPI strip ----------------
    upside = fund["upside"]
    up_tone = "tone-up" if upside > 5 else "tone-dn" if upside < -5 else ""
    kpis = "".join([
        _kpi("Last price", f"{price:,.2f} {cur}", f"52w {m['low52']:,.2f} – {m['high52']:,.2f}"),
        _kpi("Fair value", money(v["iv"], cur), f"DCF / multiple model", up_tone),
        _kpi("Implied upside", pct(upside), "vs. fair value", up_tone),
        _kpi("Composite score", f"{v['composite']}/10",
             f"Val {v['components']['valuation']:.1f} · Qual {v['components']['quality']:.1f} · "
             f"Moat {v['components']['moat']:.1f} · Sent {v['components']['sentiment']:.1f} · "
             f"Tech {v['components']['technicals']:.1f}"),
        _kpi("Moat", esc(moat["rating"]), f"{moat['score']}/10 · 5-pillar model"),
        _kpi("Sentiment", f"{sent['score']}/10", sent["consensus"]),
    ])

    # ---------------- Section 1: Fundamentals ----------------
    f = fund
    dcf_rows = ""
    if f["dcf"]:
        d = f["dcf"]
        dcf_rows = "".join(
            _row(f"Year {t}", f"FCF {fcf:,.2f} · g {g:.1f}% · PV {pv:,.2f}")
            for t, fcf, g, pv in d["schedule"][:5]) + \
            _row(f"Terminal yr {d['schedule'][-1][0]}",
                 f"PV of terminal value: {d['pv_terminal']:,.2f}")
        val = f["valuation"]
        dcf_rows += _row("DCF intrinsic value", f"{val['dcf_iv']:,.2f} {cur} (50% weight)")
        dcf_rows += _row("Growth-adjusted P/E value",
                         f"{val['pe_iv']:,.2f} {cur} (target {val['multiple']['target_pe']:,.1f}x × EPS) — 50% weight")
        dcf_method = (f"Multi-method fair value — 50% two-stage FCFE DCF "
                      f"(FCF/share {d['fcf_ps']:,.2f}, growth {d['growth']:.0f}%→{d['terminal']:.1f}%, "
                      f"discount {d['rate']:.1f}%) + 50% growth-adjusted P/E. "
                      f"Net cash/share {d['net_cash_ps']:+,.2f} shown for context "
                      f"(FCFE basis — not added back)")
    else:
        val = f["valuation"]
        dcf_method = (f"{val['method']}"
                      + (f" — target {val['pe_target']:,.0f}x × EPS {val['eps']:,.2f}"
                         if "pe_target" in val else ""))
    dcf_rows += _row("Implied fair value", f"<b>{f['valuation']['intrinsic_value']:,.2f} {cur}</b>")

    fund_table = "".join([
        _row("Revenue (TTM)", f"{bcap(f['rev'])} <span class='muted'>({pct(f['rev_g'])} YoY)</span>"),
        _row("Gross margin", pct(f["gm"], 1).replace("+", "")),
        _row("Operating margin", pct(f["opm"], 1).replace("+", "")),
        _row("Net margin", pct(f["nm"], 1).replace("+", "")),
        _row("EPS (TTM)", f"{f['eps']:,.2f} {cur}"),
        _row("P/E (TTM) / Fwd", f"{f['pe']:,.1f}x / {f['fwd_pe']:,.1f}x"),
        _row("P/S · EV/EBITDA", f"{f['ps']:,.1f}x · {f['ev_ebitda']:,.1f}x"),
        _row("ROIC / ROE", f"{f['roic']:,.0f}% / {f['roe']:,.0f}%"),
        _row("Free cash flow", f"{bcap(f['fcf'])}" if f["fcf"] else "—"),
        _row("Cash / Total debt", (f"{bcap(f['cash'])} / {bcap(f['debt'])}"
                                   if f.get("cash") else "n/a (bank)")),
        _row("Dividend", f"{f['div']} ({f['divy']}% yield)"),
        _row("Quality score", f"{f['quality_score']}/10 (margins + growth + balance sheet)"),
    ])

    # ---------------- Section 2: Business ----------------
    seg_bars = "".join(
        f'<div class="seg"><div class="seg-head"><span>{esc(n)}</span><span>{pct(p,0)}</span></div>'
        f'<div class="bar"><div class="bar-fill seg-fill" style="width:{max(4,p):.0f}%"></div></div>'
        f'<div class="seg-note">{esc(note)}</div></div>'
        for n, p, note in st["business"]["segments"])

    # ---------------- Section 3: Moat ----------------
    pillar_labels = {
        "network_effects": "Network Effects", "switching_costs": "Switching Costs",
        "intangibles": "Intangibles (brand / IP)", "cost_advantage": "Cost Advantage",
        "scale": "Scale"}
    pillars = "".join(_bar(pillar_labels.get(k, k), s, note)
                      for k, (s, note) in moat["pillars"].items())

    # ---------------- Section 4: Competitors ----------------
    peer_rows = ""
    for p in comp["peers"]:
        pe_txt = f"{p['pe']:,.0f}x" if p.get("pe") else "—"
        mc_txt = bcap(p["mc"]) if p.get("mc") else "—"
        rev_txt = bcap(p["rev"]) if p.get("rev") else "—"
        peer_rows += (
            f"<tr><td><b>{esc(p['t'])}</b></td><td>{esc(p['n'])}</td>"
            f"<td>{mc_txt}</td><td>{rev_txt}</td><td>{pe_txt}</td>"
            f"<td>{esc(p['note'])}</td></tr>")

    # ---------------- Section 5: Sentiment / News ----------------
    news_items = "".join(
        f'<div class="news {esc(n["i"])}"><div class="news-date">{esc(n["d"])}</div>'
        f'<div class="news-body"><b>{esc(n["h"])}</b>'
        f'<span class="news-src">— {esc(n["s"])}</span></div></div>'
        for n in sent["news"])
    trend_chips = "".join(f'<span class="chip">{esc(t)}</span>' for t in sent["trends"])
    pt_txt = (f"Analyst target {money(sent['pt'], cur)} "
              f"(range {money(sent['pt_lo'], cur)}–{money(sent['pt_hi'], cur)})") if sent.get("pt") else \
             "No analyst consensus available"

    # ---------------- Section 6: Technicals ----------------
    chg = tech
    tech_kpis = "".join([
        _kpi("1M / 3M change", f"{pct(chg['chg_1m'])} / {pct(chg['chg_3m'])}", f"1Y {pct(chg['chg_1y'])}"),
        _kpi("SMA 20 / 50", f"{chg['sma20']:,.2f} / {chg['sma50']:,.2f}", f"SMA 200 {chg['sma200']:,.2f}"),
        _kpi("RSI (14)", f"{chg['rsi']:.0f}", chg["rsi_state"]),
        _kpi("MACD", f"{chg['macd_hist']:+.2f}", chg["macd_state"]),
        _kpi("From 52w high", pct(chg["pct_from_high"]), f"from low {pct(chg['pct_from_low'])}"),
        _kpi("ATR (14)", f"{chg['atr14']:,.2f} {cur}", "volatility unit for zones"),
    ])
    levels_rows = "".join([
        _row("Resistance R1 / R2", f"{chg['resistances'][0]:,.2f} / {chg['resistances'][1] if len(chg['resistances'])>1 else chg['resistances'][0]*1.08:,.2f}"),
        _row("Support S1 / S2", f"{chg['supports'][0]:,.2f} / {chg['supports'][1] if len(chg['supports'])>1 else chg['supports'][0]*0.97:,.2f}"),
        _row("Entry zone", f"{chg['entry_zone'][0]:,.2f} – {chg['entry_zone'][1]:,.2f}"),
        _row("Stop (1.8×ATR below entry)", f"{chg['stop']:,.2f}"),
        _row("Target (R2)", f"{chg['target']:,.2f}"),
        _row("Signal", f"<b>{esc(chg['signal'])}</b> — {esc(chg['trend'])}"),
    ])
    chart = svg_price_chart(m["ticker"], price, m["low52"], m["high52"])
    rsi_panel = _mini_panel(f"RSI 14 — {chg['rsi']:.0f} ({chg['rsi_state']})",
                            chg["rsi_series"], ref=50)
    macd_panel = _mini_panel(f"MACD histogram — {chg['macd_hist']:+.2f}",
                             chg["macd_hist_series"], ref=0.0)

    # ---------------- Section 7: SWOT ----------------
    def swot_col(items, empty="—"):
        if not items:
            return f"<li>{empty}</li>"
        return "".join(f"<li>{esc(i)}</li>" for i in items)
    swot_grid = f'''<div class="swot-grid">
      <div class="swot s"><h4>Strengths</h4><ul>{swot_col(sw['swot']['strengths'])}</ul></div>
      <div class="swot w"><h4>Weaknesses</h4><ul>{swot_col(sw['swot']['weaknesses'])}</ul></div>
      <div class="swot o"><h4>Opportunities</h4><ul>{swot_col(sw['swot']['opportunities'])}</ul></div>
      <div class="swot t"><h4>Threats</h4><ul>{swot_col(sw['swot']['threats'])}</ul></div>
    </div>'''

    # ---------------- Section 8: Thesis ----------------
    case_cards = ""
    for c in sw["cases"]:
        gap = (c["target"] / price - 1) * 100
        case_cards += f'''<div class="case {c['key']}">
          <div class="case-head"><span class="case-label">{c['label']} Case</span>
          <span class="case-prob">{c['probability']*100:.0f}% prob.</span></div>
          <p>{esc(c['case'])}</p>
          <div class="case-target">12m target <b>{c['target']:,.2f} {cur}</b> ({gap:+.1f}%)</div>
        </div>'''
    ev_line = ""
    if v.get("expected_value"):
        ev_line = (f'<div class="ev-line">Probability-weighted expected value: '
                   f'<b>{v["expected_value"]:,.2f} {cur}</b> ({v["ev_gap"]:+.1f}% vs. price)</div>')

    data_banner = ""
    if m["data_quality"] != "verified":
        data_banner = ('<div class="banner warn">⚠ <b>Estimated data.</b> This ticker is not in the '
                       'local intelligence knowledge base — figures are model-generated sector '
                       'estimates for screening purposes, not audited fundamentals. Verify with '
                       'primary sources before acting.</div>')
    else:
        data_banner = ('<div class="banner ok">Data as of October 2026, compiled from public market '
                       'sources into the local intelligence KB. Technical indicators are computed '
                       'from the deterministic 12-month price path anchored to the 52-week range.</div>')

    verdict_cls = ("v-buy" if v["label"] in ("STRONG BUY", "BUY")
                   else "v-hold" if v["label"] == "HOLD / WAIT" else "v-avoid")

    html = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{esc(m['ticker'])} — Stock Research Report</title>
<style>{CSS}</style>
</head>
<body>
<nav class="topnav">
  <div class="brand">📈 Stock Research Agent</div>
  <div class="nav-links">
    <a href="#s1">1 Fundamentals</a><a href="#s2">2 Business</a><a href="#s3">3 Moat</a>
    <a href="#s4">4 Competitors</a><a href="#s5">5 Sentiment</a><a href="#s6">6 Technicals</a>
    <a href="#s7">7 SWOT</a><a href="#s8">8 Thesis &amp; Verdict</a>
    <button id="themeBtn" class="theme-btn" type="button">☀ Light</button>
  </div>
</nav>

<header class="hero">
  <div class="hero-top">
    <div>
      <div class="ticker-row"><span class="big-ticker">{esc(m['ticker'])}</span>
        <span class="badge {verdict_cls}">{esc(v['label'])}</span></div>
      <h1>{esc(m['name'])}</h1>
      <p class="meta-line">{esc(m['sector'])} · {esc(m['industry'])} · {esc(m['exchange'])} ·
        {esc(m['country'])} · Mkt cap {bcap(m['market_cap'])} · {esc(m['data_as_of'])}</p>
    </div>
    <div class="hero-price">
      <div class="hero-last">{price:,.2f} {cur}</div>
      <div class="hero-chg">{pct(chg['chg_1m'])} 1M · {pct(chg['chg_3m'])} 3M</div>
    </div>
  </div>
  {data_banner}
  <div class="kpi-strip">{kpis}</div>
</header>

<main>
<section id="s0" class="verdict-banner {verdict_cls}">
  <div class="vb-title">Is it worth it? — {esc(m['ticker'])} at {price:,.2f} {cur}</div>
  <p>{esc(v['worth'])}</p>
</section>

<section id="s1" class="card">
{section_header('1', 'Fundamentals, Financial Health & Intrinsic Valuation',
   'Income statement, balance sheet, cash flow, growth, margins, ROIC/ROE, multiples and DCF fair value')}
  <div class="two-col">
    <div>
      <table class="tbl">{fund_table}</table>
    </div>
    <div>
      <h3 class="sub">Intrinsic value — {dcf_method}</h3>
      <table class="tbl">{dcf_rows}</table>
      <div class="upside-box {up_tone}">Implied upside vs. price: <b>{pct(upside)}</b></div>
    </div>
  </div>
</section>

<section id="s2" class="card">
{section_header('2', 'Business Model & Revenue Architecture',
   'How the company makes money, revenue segments and the operating flywheel')}
  <p class="prose">{esc(st['business']['biz'])}</p>
  <div class="segs">{seg_bars}</div>
  <p class="muted small">Employees: {esc(st['business']['employees'])} · Web: {esc(m['website'] or '—')}</p>
</section>

<section id="s3" class="card">
{section_header('3', 'Economic Moat — 5-Pillar Scoring',
   'Network effects · switching costs · intangibles · cost advantage · scale')}
  <div class="moat-top">
    <div class="moat-badge">{esc(moat['rating'])}</div>
    <div class="moat-score">Composite moat score: <b>{moat['score']}/10</b></div>
  </div>
  <div class="pillars">{pillars}</div>
</section>

<section id="s4" class="card">
{section_header('4', 'Competitors & Main Difference Against Competitors',
   'Head-to-head peer table, positioning and the core structural edge')}
  <table class="tbl peers"><thead><tr><th>Ticker</th><th>Company</th><th>Mkt Cap</th>
    <th>Rev (TTM)</th><th>P/E</th><th>Positioning</th></tr></thead>
  <tbody>{peer_rows}</tbody></table>
  <div class="edge-box"><div class="edge-title">★ Core structural edge — the main difference</div>
  <p>{esc(comp['edge'])}</p></div>
</section>

<section id="s5" class="card">
{section_header('5', 'Market Sentiment, Recent News & Secular Trends',
   'Sentiment score, analyst consensus, headline catalysts and the structural trends driving the stock')}
  <div class="sent-grid">
    <div class="sent-meter">
      <div class="sent-score">{sent['score']}/10</div>
      <div class="bar big"><div class="bar-fill good" style="width:{sent['score']*10:.0f}%"></div></div>
      <div class="muted">{esc(sent['consensus'])} · short interest {esc(sent['short'])}</div>
      <div class="muted">{pt_txt}</div>
    </div>
    <div class="news-list">{news_items}</div>
  </div>
  <h3 class="sub">Secular trends</h3>
  <div class="chips">{trend_chips}</div>
</section>

<section id="s6" class="card">
{section_header('6', 'Technical Analysis',
   '12-month price action with SMA 20/50/200, Bollinger Bands, RSI, MACD, support/resistance and actionable zones')}
  <div class="kpi-strip small">{tech_kpis}</div>
  {chart}
  {rsi_panel}
  {macd_panel}
  <table class="tbl levels">{levels_rows}</table>
</section>

<section id="s7" class="card">
{section_header('7', 'SWOT Analysis', 'Comprehensive four-quadrant assessment')}
  {swot_grid}
</section>

<section id="s8" class="card">
{section_header('8', 'Investment Thesis & Final Verdict',
   'Bull / base / bear cases, probability-weighted expected value and the actionable conclusion')}
  <div class="cases">{case_cards}</div>
  {ev_line}
  <div class="final {verdict_cls}">
    <div class="final-label">FINAL VERDICT — {esc(m['ticker'])}</div>
    <div class="final-score">{esc(v['label'])} · composite {v['composite']}/10</div>
    <div class="final-zones">
      <span>Entry <b>{v['entry_zone'][0]:,.2f}–{v['entry_zone'][1]:,.2f}</b></span>
      <span>Stop <b>{v['stop']:,.2f}</b></span>
      <span>12m Target <b>{v['target_12m']:,.2f}</b></span>
      <span>Fair value <b>{v['iv']:,.2f}</b></span>
    </div>
  </div>
</section>

<footer>
  <p>Generated {esc(m['generated_at'])} by the Stock Research Agent (7-stage pipeline:
  fundamentals/DCF · business model · 5-pillar moat · competitors &amp; core edge · sentiment/news/trends ·
  technicals · SWOT &amp; thesis). Technicals are computed from a deterministic price path anchored to the
  reported 52-week range. This report is research, not financial advice.</p>
</footer>
</main>
<script>{JS}</script>
</body>
</html>"""
    return html


# ---------------------------------------------------------------------------
# Static assets
# ---------------------------------------------------------------------------

CSS = """
:root{
  --bg:#0b0f17; --bg2:#0f1522; --card:#121a2b; --card2:#16213a;
  --line:#22304d; --txt:#e8eefb; --muted:#8fa3c8; --accent:#4da3ff;
  --up:#2fd07c; --dn:#ff5d6c; --gold:#ffc857;
  --s20:#ffd166; --s50:#4da3ff; --s200:#c084fc; --boll:#274066;
  --sup:#2fd07c; --res:#ff5d6c;
  --good:#2fd07c; --mid:#ffc857; --bad:#ff5d6c;
}
html[data-theme="light"]{
  --bg:#f4f6fb; --bg2:#ffffff; --card:#ffffff; --card2:#eef2fa;
  --line:#d7e0f0; --txt:#17233d; --muted:#5b6c8f; --accent:#1668d6;
  --up:#0d9d5c; --dn:#d63347; --gold:#c78a00;
  --s20:#d99a00; --s50:#1668d6; --s200:#7b3ff2; --boll:#dbe6f8;
  --sup:#0d9d5c; --res:#d63347;
  --good:#0d9d5c; --mid:#c78a00; --bad:#d63347;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Inter,Arial,sans-serif}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.topnav{position:sticky;top:0;z-index:50;display:flex;align-items:center;justify-content:space-between;
  gap:12px;padding:10px 22px;background:var(--bg2);border-bottom:1px solid var(--line);flex-wrap:wrap}
.brand{font-weight:700;letter-spacing:.2px}
.nav-links{display:flex;gap:14px;flex-wrap:wrap;align-items:center;font-size:13px}
.nav-links a{color:var(--muted)}
.nav-links a:hover{color:var(--txt);text-decoration:none}
.theme-btn{background:var(--card);border:1px solid var(--line);color:var(--txt);
  padding:5px 12px;border-radius:20px;cursor:pointer;font-size:13px}
.hero{padding:26px 22px 10px;background:
  radial-gradient(1000px 300px at 20% -50px, color-mix(in srgb, var(--accent) 14%, transparent), transparent)}
.hero-top{display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap;align-items:flex-end}
h1{margin:6px 0 4px;font-size:28px}
.big-ticker{font-size:30px;font-weight:800;letter-spacing:1px;margin-right:12px}
.meta-line{color:var(--muted);margin:0;font-size:13.5px}
.hero-price{text-align:right}
.hero-last{font-size:30px;font-weight:800}
.hero-chg{color:var(--muted);font-size:13.5px}
.badge{display:inline-block;padding:6px 14px;border-radius:20px;font-weight:800;font-size:13px;letter-spacing:.5px}
.v-buy{background:color-mix(in srgb,var(--up) 18%, transparent);color:var(--up);
  border:1px solid color-mix(in srgb,var(--up) 45%, transparent)}
.v-hold{background:color-mix(in srgb,var(--gold) 16%, transparent);color:var(--gold);
  border:1px solid color-mix(in srgb,var(--gold) 45%, transparent)}
.v-avoid{background:color-mix(in srgb,var(--dn) 16%, transparent);color:var(--dn);
  border:1px solid color-mix(in srgb,var(--dn) 45%, transparent)}
.banner{padding:10px 14px;border-radius:10px;margin:14px 0;font-size:13.5px}
.banner.ok{background:color-mix(in srgb,var(--accent) 10%, transparent);
  border:1px solid color-mix(in srgb,var(--accent) 35%, transparent)}
.banner.warn{background:color-mix(in srgb,var(--gold) 12%, transparent);
  border:1px solid color-mix(in srgb,var(--gold) 45%, transparent)}
.kpi-strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:16px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.kpi-strip.small .kpi{padding:9px 11px}
.kpi-label{color:var(--muted);font-size:11.5px;text-transform:uppercase;letter-spacing:.6px}
.kpi-value{font-size:19px;font-weight:800;margin-top:3px}
.kpi-sub{color:var(--muted);font-size:11.5px;margin-top:2px}
.tone-up .kpi-value{color:var(--up)} .tone-dn .kpi-value{color:var(--dn)}
main{padding:8px 22px 30px;max-width:1180px;margin:0 auto}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;
  padding:22px;margin:22px 0;scroll-margin-top:70px}
.sec-head{display:flex;gap:14px;align-items:flex-start;margin-bottom:14px}
.sec-num{background:var(--card2);border:1px solid var(--line);color:var(--accent);
  min-width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;
  font-weight:800;font-size:17px}
.sec-head h2{margin:0 0 2px;font-size:21px}
.sec-sub{color:var(--muted);margin:0;font-size:13.5px}
h3.sub{margin:18px 0 8px;font-size:15px}
.prose{font-size:15px;line-height:1.65}
.muted{color:var(--muted)} .small{font-size:12.5px}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:22px}
@media(max-width:860px){.two-col{grid-template-columns:1fr}}
.tbl{width:100%;border-collapse:collapse;font-size:13.5px}
.tbl td{padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}
.tbl .rk{color:var(--muted);width:42%}
.tbl .rv{font-weight:600}
.tbl.peers th{padding:8px 10px;text-align:left;color:var(--muted);font-size:12px;
  text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid var(--line)}
.tbl.peers td{padding:9px 10px}
.tbl.levels{margin-top:14px;max-width:560px}
.upside-box{margin-top:10px;padding:10px 14px;border-radius:10px;font-size:14.5px;
  background:var(--card2);border:1px solid var(--line)}
.upside-box.tone-up b{color:var(--up)} .upside-box.tone-dn b{color:var(--dn)}
.segs{display:grid;gap:12px;margin-top:10px;max-width:720px}
.seg-head{display:flex;justify-content:space-between;font-size:14px;font-weight:700}
.seg-note{color:var(--muted);font-size:12.5px;margin-top:3px}
.bar{height:9px;background:var(--card2);border-radius:6px;overflow:hidden;margin-top:4px}
.bar.big{height:12px}
.bar-fill{height:100%;border-radius:6px}
.bar-fill.good{background:var(--good)} .bar-fill.mid{background:var(--mid)}
.bar-fill.bad{background:var(--bad)} .bar-fill.seg-fill{background:var(--accent)}
.moat-top{display:flex;gap:16px;align-items:center;margin:6px 0 14px;flex-wrap:wrap}
.moat-badge{font-size:18px;font-weight:800;padding:8px 18px;border-radius:12px;
  background:color-mix(in srgb,var(--gold) 15%, transparent);color:var(--gold);
  border:1px solid color-mix(in srgb,var(--gold) 40%, transparent)}
.moat-score{color:var(--muted)}
.pillars{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
.pillar{background:var(--card2);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.pillar-head{display:flex;justify-content:space-between;font-weight:700;font-size:14px}
.pill-score{color:var(--accent)}
.pillar-note{color:var(--muted);font-size:12.5px;margin-top:6px}
.edge-box{margin-top:16px;padding:16px 18px;border-radius:14px;
  background:color-mix(in srgb,var(--gold) 8%, var(--card2));
  border:1px solid color-mix(in srgb,var(--gold) 40%, transparent)}
.edge-title{font-weight:800;color:var(--gold);margin-bottom:6px}
.sent-grid{display:grid;grid-template-columns:280px 1fr;gap:22px}
@media(max-width:860px){.sent-grid{grid-template-columns:1fr}}
.sent-score{font-size:30px;font-weight:800}
.news-list{display:grid;gap:10px;align-content:start}
.news{display:flex;gap:12px;background:var(--card2);border:1px solid var(--line);
  border-radius:10px;padding:10px 14px;border-left:4px solid var(--accent)}
.news.pos{border-left-color:var(--up)} .news.neg{border-left-color:var(--dn)}
.news-date{color:var(--muted);font-size:12px;min-width:86px;padding-top:2px}
.news-src{display:block;color:var(--muted);font-size:12px;margin-top:2px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.chip{background:var(--card2);border:1px solid var(--line);border-radius:20px;
  padding:6px 13px;font-size:13px}
.chart{width:100%;height:auto;display:block;margin-top:8px}
.chart.mini{margin-top:6px}
.grid{stroke:var(--line);stroke-width:1;opacity:.5}
.price{fill:none;stroke:var(--accent);stroke-width:2.4}
.sma20{fill:none;stroke:var(--s20);stroke-width:1.4;opacity:.95}
.sma50{fill:none;stroke:var(--s50);stroke-width:1.4;opacity:.95}
.sma200{fill:none;stroke:var(--s200);stroke-width:1.4;opacity:.95}
.boll-fill{fill:var(--boll);opacity:.35}
.boll-up,.boll-lo{fill:none;stroke:var(--boll);stroke-width:1;opacity:.9}
.hi,.lo{stroke:var(--muted);stroke-width:1;stroke-dasharray:5 4;opacity:.8}
.res{stroke:var(--res);stroke-width:1.2;stroke-dasharray:6 4;opacity:.85}
.sup{stroke:var(--sup);stroke-width:1.2;stroke-dasharray:6 4;opacity:.85}
.tag-hi,.tag-lo{fill:var(--muted);font-size:10.5px}
.tag-res{fill:var(--res);font-size:10.5px;font-weight:700}
.tag-sup{fill:var(--sup);font-size:10.5px;font-weight:700}
.tag-title{fill:var(--txt);font-size:12px;font-weight:700}
.axis{fill:var(--muted);font-size:10.5px}
.ref{stroke:var(--muted);stroke-width:1;stroke-dasharray:4 4;opacity:.7}
.line-accent{fill:none;stroke:var(--s200);stroke-width:1.8}
.dot{fill:var(--accent)}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12px;color:var(--muted);margin-top:6px}
.sw{display:inline-block;width:16px;height:4px;border-radius:2px;margin-right:5px;vertical-align:middle}
.sw-price{background:var(--accent)} .sw-20{background:var(--s20)}
.sw-50{background:var(--s50)} .sw-200{background:var(--s200)}
.sw-boll{background:var(--boll)} .sw-sup{background:var(--sup)} .sw-res{background:var(--res)}
.swot-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:860px){.swot-grid{grid-template-columns:1fr}}
.swot{border-radius:14px;padding:16px 18px;border:1px solid var(--line)}
.swot h4{margin:0 0 8px;font-size:15px}
.swot ul{margin:0;padding-left:18px}
.swot li{margin:6px 0;font-size:13.5px}
.swot.s{background:color-mix(in srgb,var(--up) 8%, var(--card2));
  border-color:color-mix(in srgb,var(--up) 40%, transparent)}
.swot.w{background:color-mix(in srgb,var(--dn) 8%, var(--card2));
  border-color:color-mix(in srgb,var(--dn) 40%, transparent)}
.swot.o{background:color-mix(in srgb,var(--accent) 10%, var(--card2));
  border-color:color-mix(in srgb,var(--accent) 40%, transparent)}
.swot.t{background:color-mix(in srgb,var(--gold) 10%, var(--card2));
  border-color:color-mix(in srgb,var(--gold) 40%, transparent)}
.cases{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
.case{background:var(--card2);border:1px solid var(--line);border-radius:14px;padding:16px}
.case.bull{border-top:4px solid var(--up)} .case.base{border-top:4px solid var(--accent)}
.case.bear{border-top:4px solid var(--dn)}
.case-head{display:flex;justify-content:space-between;margin-bottom:8px}
.case-label{font-weight:800}
.case-prob{color:var(--muted);font-size:12.5px}
.case p{margin:0 0 10px;font-size:13.5px;color:var(--txt)}
.case-target{font-size:13.5px}
.ev-line{margin-top:12px;color:var(--muted);font-size:14px}
.verdict-banner{padding:20px 24px;border-radius:16px;margin-top:18px;font-size:16px}
.verdict-banner p{margin:8px 0 0;font-size:15.5px;line-height:1.6}
.vb-title{font-weight:800;font-size:18px}
.final{margin-top:20px;padding:20px 24px;border-radius:16px;border:1px solid var(--line)}
.final-label{font-weight:800;letter-spacing:.5px;font-size:14px;color:var(--muted)}
.final-score{font-size:26px;font-weight:800;margin:6px 0 12px}
.final.v-buy .final-score{color:var(--up)} .final.v-hold .final-score{color:var(--gold)}
.final.v-avoid .final-score{color:var(--dn)}
.final-zones{display:flex;gap:22px;flex-wrap:wrap;font-size:14px;color:var(--muted)}
.final-zones b{color:var(--txt)}
.verdict-banner.v-buy{background:color-mix(in srgb,var(--up) 10%, var(--card));
  border:1px solid color-mix(in srgb,var(--up) 45%, transparent)}
.verdict-banner.v-hold{background:color-mix(in srgb,var(--gold) 10%, var(--card));
  border:1px solid color-mix(in srgb,var(--gold) 45%, transparent)}
.verdict-banner.v-avoid{background:color-mix(in srgb,var(--dn) 10%, var(--card));
  border:1px solid color-mix(in srgb,var(--dn) 45%, transparent)}
footer{color:var(--muted);font-size:12.5px;padding:10px 22px 40px;max-width:1180px;margin:0 auto}
"""

JS = """
(function(){
  var root=document.documentElement;
  var btn=document.getElementById('themeBtn');
  var saved=null; try{saved=localStorage.getItem('sra-theme');}catch(e){}
  if(saved){root.setAttribute('data-theme',saved);}
  function paint(){
    var t=root.getAttribute('data-theme');
    btn.textContent = t==='light' ? '🌙 Dark' : '☀ Light';
  }
  paint();
  btn.addEventListener('click',function(){
    var t=root.getAttribute('data-theme')==='light'?'dark':'light';
    root.setAttribute('data-theme',t);
    try{localStorage.setItem('sra-theme',t);}catch(e){}
    paint();
  });
  document.querySelectorAll('a[href^="#"]').forEach(function(a){
    a.addEventListener('click',function(ev){
      ev.preventDefault();
      var el=document.querySelector(a.getAttribute('href'));
      if(el){el.scrollIntoView({behavior:'smooth',block:'start'});}
    });
  });
})();
"""
