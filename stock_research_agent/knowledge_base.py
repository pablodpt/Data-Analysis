# -*- coding: utf-8 -*-
"""
knowledge_base.py — Unified access to the equity intelligence knowledge base.

* Deep, hand-compiled institutional profiles (40+ tickers, Oct 2026) from
  kb_us / kb_eu.
* S&P 500 company-name -> ticker resolution (from the repo's pickle).
* A deterministic sector-aware SYNTHESIZER that produces a complete,
  clearly-labelled research profile for ANY ticker not in the KB, so the
  agent can research on-demand with zero dead ends.
"""
from __future__ import annotations

import hashlib
import os
import pickle
import random
import re
from typing import Any, Dict, List, Optional

from . import kb_us, kb_eu

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

KB: Dict[str, Dict[str, Any]] = {}
KB.update({k: dict(v) for k, v in kb_us.US.items()})
KB.update({k: dict(v) for k, v in kb_eu.EU.items()})

ALIAS = {
    "GOOG": "GOOGL", "GOOGL.X": "GOOGL", "GOOG.X": "GOOGL",
    "AAPL.US": "AAPL", "MSFT.US": "MSFT", "NVDA.US": "NVDA",
    "TSLA.US": "TSLA", "AMZN.US": "AMZN", "META.US": "META",
    "INTC.X": "INTC", "ASML.AS": "ASML", "SAP.DE": "SAP",
    "NVO.L": "NVO",
    "SPCE": "SPCX", "TSLA": "TSLA", "XPEV": "XPEV", "LI": "LI",
    "BYDDF": "BYD", "700.HK": "BYD", "BABA.X": "BABA", "TCEHY": "TCEHY",
    "TCOM": "BABA", "JD.X": "JD", "PDD.X": "PDD", "SNAP.X": "SNAP",
}

NAME_STOPWORDS = {"inc", "corp", "corporation", "incorporated", "plc", "ltd",
                 "limited", "group", "holdings", "sa", "s.a.", "ag", "se",
                 "n.v.", "nv", "p.l.c.", "p.l.c.", "sa", "s.p.a.", "gmbh"}


def _norm(t: str) -> str:
    t = t.strip().upper()
    return ALIAS.get(t, t)


def known_tickers() -> list:
    return sorted(KB.keys())


# ---------------------------------------------------------------------------
# S&P 500 name resolution (repo pickle)
# ---------------------------------------------------------------------------

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PICKLE = os.path.join(_REPO_ROOT, "sp500tickers.pickle")

def _load_sp500_names() -> list:
    try:
        with open(_PICKLE, "rb") as f:
            return pickle.load(f)
    except Exception:
        return []

_SP500_NAMES = _load_sp500_names()

_NAME_TO_TICKER = {
    "apple inc.": "AAPL", "apple": "AAPL",
    "microsoft corp.": "MSFT", "microsoft": "MSFT",
    "alphabet inc class a": "GOOGL", "alphabet inc class c": "GOOGL",
    "alphabet": "GOOGL", "google": "GOOGL",
    "amazon.com inc.": "AMZN", "amazon": "AMZN",
    "meta platforms inc": "META", "meta": "META", "facebook": "META",
    "nvidia corp.": "NVDA", "nvidia": "NVDA",
    "advanced micro devices inc": "AMD",
    "broadcom inc.": "AVGO",
    "tesla inc.": "TSLA", "tesla": "TSLA",
    "micron technology inc.": "MU",
    "intel corp.": "INTC",
    "qualcomm inc.": "QCOM",
    "texas instruments inc.": "TXN",
    "adobe systems inc": "ADBE",
    "cisco systems inc.": "CSCO",
    "oracle corp.": "ORCL",
    "salesforce.com inc": "CRM",
    "service now inc.": "NOW",
    "workday inc.": "WDAY",
    "intuit inc.": "INTU",
    "citigroup inc.": "C",
    "jpmorgan chase & co.": "JPM", "jpmorgan chase": "JPM", "jpmorgan": "JPM",
    "bank of america corp.": "BAC", "bank of america": "BAC",
    "wells fargo & co.": "WFC", "wells fargo": "WFC",
    "goldman sachs group inc.": "GS", "goldman sachs": "GS",
    "morgan stanley": "MS",
    "charles schwab corp.": "SCHW",
    "visa inc.": "V", "visa": "V",
    "mastercard inc.": "MA",
    "exxon mobil corp.": "XOM", "exxon": "XOM",
    "chevron corp.": "CVX", "chevron": "CVX",
    "conocophillips": "COP",
    "occidental petroleum corp.": "OXY",
    "coca-cola co.": "KO",
    "pepsi co., inc.": "PEP",
    "procter & gamble co.": "PG",
    "colgate-palmolive co.": "CL",
    "kellogg co.": "K",
    "mondelez international inc.": "MDLZ",
    "general motors co.": "GM",
    "ford motor co.": "F",
    "alcoa corp.": "AA",
    "boeing co.": "BA", "boeing": "BA",
    "caterpillar inc.": "CAT",
    "deere & co.": "DE",
    "honeywell international inc.": "HON",
    "3m co.": "MMM",
    "abbott laboratories": "ABT",
    "abbvie inc.": "ABBV",
    "accenture plc": "ACN",
    "allstate corp.": "ALL",
    "amgen inc.": "AMGN",
    "annaly capital management inc.": "NLY",
    "aon plc": "AON",
    "aptiv plc": "APTV",
    "asml holding n.v.": "ASML",
    "att inc.": "T",
    "autodesk inc.": "ADSK",
    "aflac inc.": "AFL",
    "air products & chemicals inc.": "APD",
    "akamai technologies inc.": "AKAM",
    "alaska air group inc.": "ALK",
    "albemarle corp.": "ALB",
    "allergan, plc": "AGN",
    "alliant energy corp.": "LNT",
    "altria group inc.": "MO",
    "ameren corp.": "AEE",
    "amc entertainment holdings inc.": "AMC",
    "american electric power co.": "AEP",
    "american express co.": "AXP",
    "american international group inc.": "AIG",
    "american tower corp.": "AMT",
    "american Airlines Group inc.": "AAL",
    "amphenol corp.": "APH",
    "analog devices inc.": "ADI",
    "arista networks inc.": "ANET",
    "applied materials inc.": "AMAT",
    "apache corp.": "APA",
    "atmos energy corp.": "ATO",
    "avery dennison corp.": "AVY",
    "baker hughes co.": "BKR",
    "ball corp.": "B",
    "baxter international inc.": "BAX",
    "blackrock inc.": "BLK",
    "boston scientific corp.": "BSX",
    "bristol-myers squibb co.": "BMY",
    "cadence design systems inc.": "CDNS",
    "caesars entertainment inc.": "CZR",
    "cal-maine foods inc.": "CALM",
    "campbell soup co.": "CPB",
    "capital one financial corp.": "COF",
    "cardinal health inc.": "CAH",
    "carlyle group inc.": "CG",
    "cbre group inc.": "CBRE",
    "cdw corp.": "CDW",
    "centene corp.": "CNC",
    "chipotle mexican grill inc.": "CMG",
    "cincinnati financial corp.": "CINF",
    "cigna corp.": "CI",
    "citrix systems inc.": "CTXS",
    "clorox co.": "CLX",
    "cme group inc.": "CME",
    "cognizant technology solutions corp.": "CTSH",
    "coinbase global inc.": "COIN",
    "colfax corp.": "CLFX",
    "comcast corp.": "CMCSA",
    "comerica inc.": "CMA",
    "conagra brands inc.": "CAG",
    "concentrix corp.": "CNXC",
    "conduent inc.": "CNDT",
    "constellation brands inc.": "STZ",
    "cooper standards inc.": "CPS",
    "copart inc.": "CPRT",
    "copeland inc.": "CP",
    "corning inc.": "GLW",
    "costco wholesale corp.": "COST",
    "crowdstrike holdings inc.": "CRWD",
    "csx corp.": "CSX",
    "cummins inc.": "CMI",
    "cvs health corp.": "CVS",
    "danaher corp.": "DHR",
    "deckers outdoor corp.": "DECK",
    "dell technologies": "DELL",
    "diageo plc": "DEO",
    "discover financial services": "DFS",
    "the walt disney co.": "DIS", "disney": "DIS",
    "dover co.": "DOV",
    "eaton corp plc": "ETN",
    "emcor group inc.": "EMR",
    "entergy corp.": "ETR",
    "equifax inc.": "EFX",
    "exelon corp.": "EXC",
    "fedex corp.": "FDX", "fedex": "FDX",
    "flowserve corp.": "FLS",
    "gillette co.": "G",
    "halliburton co.": "HAL",
    "hewlett packard enterprise": "HPE",
    "hormel foods corp.": "HRL",
    "ibm": "IBM", "international business machines corp.": "IBM",
    "intuitive surgical inc.": "ISRG",
    "jpmorgan chase & co.": "JPM",
    "jnj": "JNJ", "johnson & johnson": "JNJ",
    "laboratory corporation of america": "LH",
    "lam research corp.": "LRCX",
    "ellie lilly and co.": "LLY", "lilly": "LLY",
    "linde plc": "LIN",
    "loews corp.": "L",
    "lyondellbasell": "LYB",
    "mcdonald's corp.": "MCD", "mcdonald's": "MCD",
    "medtronic plc": "MDT",
    "merck & co.": "MRK", "merck": "MRK",
    "metlife": "MET",
    "microchip technology inc.": "MCHP",
    "michigan": "MICH",
    "mondelez international inc.": "MDLZ",
    "morgan stanley": "MS",
    "motorola solutions inc.": "MSI",
    "mu": "MU",
    "nvidia corp.": "NVDA",
    "occidental petroleum corp.": "OXY",
    "oracle corp.": "ORCL",
    "palantir technologies inc.": "PLTR", "palantir": "PLTR",
    "palo alto networks inc.": "PANW",
    "pepsi co., inc.": "PEP",
    "pfizer inc.": "PFE",
    "philips": "PHG",
    "pinterest inc.": "PINS",
    "pmc": "PMC",
    "procter & gamble co.": "PG",
    "progressive corp.": "PGR",
    "public service enterprise group": "PEG",
    "qualcomm inc.": "QCOM",
    "raytheon technologies": "RTX",
    "robinhood markets inc.": "HOOD", "robinhood": "HOOD",
    "salesforce.com inc": "CRM",
    "sap se": "SAP", "sap": "SAP",
    "shockwave": "SW",
    "snowflake inc.": "SNOW",
    "softbank": "SFTBY",
    "spacex": "SPCX",
    "space exploration technologies": "SPCX",
    "super micro computer": "SMCI",
    "tesla inc.": "TSLA",
    "tsmc": "TSM", "tsmc ltd.": "TSM",
    "unitedhealth group": "UNH",
    "united natural foods": "UNFI",
    "verizon communications": "VZ",
    "vertex pharmaceuticals inc.": "VRTX",
    "visa inc.": "V",
    "walmart inc.": "WMT", "walmart": "WMT",
    "walgreens boots alliance": "WBA",
    "warner bros. discovery": "WBD",
    "wells fargo & co.": "WFC",
    "westinghouse electric": "WST",
    "workday inc.": "WDAY",
    "xom": "XOM",
    "inditex, s.a.": "ITX.MC", "inditex": "ITX.MC", "zarape": "ITX.MC",
    "iberdrola, s.a.": "IBE.MC", "iberdrola": "IBE.MC",
    "banco Bilbao Vizcaya Argentaria": "BBVA.MC", "bbva": "BBVA.MC",
    "banco santander, s.a.": "SAN.MC", "santander": "SAN.MC",
    "caixabank, s.a.": "BIC.MC", "caixa bank": "BIC.MC",
    "mapfre, s.a.": "ACA.MC", "mapfre": "ACA.MC",
    "telefonica, s.a.": "TEP.MC", "telefónica": "TEP.MC", "telefonica": "TEP.MC",
    "repsol, s.a.": "REP.MC", "repsol": "REP.MC",
    "enagás, s.a.": "ENAG.MC", "enagas": "ENAG.MC",
    "aena, s.a.": "ANA.MC", "aena": "ANA.MC",
    "bolsas y mercados españoles": "BME.MC", "bme": "BME.MC",
    "ferrovial, s.a.": "FER.MC", "ferrovial": "FER.MC",
    "international airlines group": "IAG.MC", "iag": "IAG.MC",
    "cie automotive": "CIE.MC",
    "acciona, s.a.": "ACS.MC", "acciona": "ACS.MC",
    "totalenergies": "TTE.MC", "total energies": "TTE.MC",
    "air liquide": "AIR.PA",
    "astrazeneca": "NVO",
    "siemens ag": "SIE.DE", "siemens": "SIE.DE",
}


def _kb_ticker_for(name: str) -> str:
    ln = name.lower()
    for tk in KB:
        if KB[tk]["name"].lower() == ln:
            return tk
    return _NAME_TO_TICKER.get(ln, "")


def _norm_name(name: str) -> str:
    n = re.sub(r"[^a-z0-9 ]", "", name.lower())
    n = re.sub(r"\b(inc|corp|corporation|incorporated|plc|ltd|limited|group|"
               r"holdings|co|company|sa|ag|se|nv|gmbh|class a|class c)\b", "", n)
    return re.sub(r"\s+", " ", n).strip()


# Fuzzy candidate index: S&P 500 names + KB company names, each tagged with a
# ticker when known.
_FUZZY_CANDS: List[tuple] = []
for _name in set(_SP500_NAMES) | {KB[_t]["name"] for _t in KB}:
    _n = _norm_name(_name)
    if _n:
        _FUZZY_CANDS.append((_n, _name, _kb_ticker_for(_name)))


def resolve_ticker(query: str) -> tuple:
    """Resolve a user query (ticker or company name) to (ticker, display_name)."""
    q = (query or "").strip()
    if not q:
        return "", ""
    t = _norm(q)
    if t in KB:
        return t, KB[t]["name"]
    # exact name match
    low = q.lower()
    if low in _NAME_TO_TICKER:
        tk = _norm(_NAME_TO_TICKER[low])
        return tk, (KB.get(tk, {}).get("name") or q.title())
    # fuzzy name match against S&P 500 + KB company names
    cand = _norm_name(low)
    if cand:
        best, best_score = None, 0
        cw = set(cand.split())
        for n, name, tk in _FUZZY_CANDS:
            nw = set(n.split())
            if cand == n:
                score = 100
            elif cw and nw and (cw <= nw or nw <= cw):
                # word-set containment (avoids 'acme'~'cme' substring false hits)
                shared = [w for w in (cw & nw) if len(w) >= 4]
                score = (60 + min(20, len(cand) // 2)) if shared else 0
            else:
                common = [w for w in (cw & nw) if len(w) >= 4]
                score = (len(common) / max(1, len(cw))) * 40
            if (score > best_score
                    or (score == best_score and score >= 60
                        and tk and not (best and best[2]))):
                best, best_score = (n, name, tk), score
        if best and best_score >= 60:
            _n, _name, _tk = best
            if not _tk:
                _tk = _NAME_TO_TICKER.get(_name.lower(), "")
            return _tk, _name
    return t, q.title() if len(q) <= 12 else q


# ---------------------------------------------------------------------------
# Dynamic synthesizer for unknown tickers
# ---------------------------------------------------------------------------

SECTOR_RULES = [
    ("Banking & Financial Services", ["bank", "financial", "capital", "securities",
        "insurance", "credit", "fidelity", "morgan", "citigroup", "monetary"]),
    ("Healthcare", ["health", "pharma", "medical", "labs", "lab", "biotech", "bio",
        "therapeutics", "dental", "hospital", "care", "gene", "immune", "vaccine"]),
    ("Energy & Utilities", ["energy", "oil", "gas", "petroleum", "power", "utility",
        "electric", "solar", "wind", "nuclear", "fuel", "lpg", "lng", "uranium"]),
    ("Telecommunications", ["telecom", "communication", "wireless", "mobile",
        "broadband", "fiber", "network"]),
    ("Semiconductors", ["semiconductor", "micro", "chip", "integrated circuit",
        "processor", "electronics"]),
    ("Software & Internet", ["software", "systems", "solutions", "computing",
        "data", "cloud", "digital", "cyber", "analytics", "network", "online"]),
    ("Retail & Consumer", ["retail", "stores", "merchandise", "fashion",
        "clothing", "beverage", "food", "grocery", "outdoor", "home", "consumer"]),
    ("Industrials", ["industrial", "aerospace", "defense", "aircraft", "transport",
        "materials", "mining", "minerals", "chemical", "steel", "machinery", "engineering"]),
    ("Autos & Components", ["motor", "vehicle", "auto", "truck", "car", "parts"]),
    ("Real Estate", ["real estate", "realty", "properties", "property", "apartments"]),
    ("Media & Entertainment", ["media", "entertainment", "gaming", "games",
        "content", "publishing", "broadcast", "streaming"]),
]

SECTOR_PROFILES = {
    "Banking & Financial Services": dict(gm=None, nm=(18, 35), pe=(8, 16),
        growth=(-5, 15), fcf_ratio=0.5, dcf=False),
    "Healthcare": dict(gm=(65, 85), nm=(15, 35), pe=(12, 35),
        growth=(0, 25), fcf_ratio=0.7, dcf=True),
    "Energy & Utilities": dict(gm=(25, 55), nm=(8, 22), pe=(7, 16),
        growth=(-5, 12), fcf_ratio=0.8, dcf=True),
    "Telecommunications": dict(gm=(35, 55), nm=(8, 20), pe=(10, 20),
        growth=(0, 10), fcf_ratio=0.6, dcf=True),
    "Semiconductors": dict(gm=(40, 60), nm=(10, 30), pe=(15, 45),
        growth=(0, 40), fcf_ratio=0.55, dcf=True),
    "Software & Internet": dict(gm=(70, 85), nm=(10, 35), pe=(20, 60),
        growth=(10, 45), fcf_ratio=0.55, dcf=True),
    "Retail & Consumer": dict(gm=(25, 50), nm=(3, 15), pe=(12, 30),
        growth=(-5, 15), fcf_ratio=0.5, dcf=True),
    "Industrials": dict(gm=(18, 40), nm=(5, 18), pe=(10, 25),
        growth=(0, 15), fcf_ratio=0.5, dcf=True),
    "Autos & Components": dict(gm=(15, 30), nm=(2, 12), pe=(8, 30),
        growth=(-10, 25), fcf_ratio=0.4, dcf=True),
    "Real Estate": dict(gm=None, nm=(5, 20), pe=(12, 25),
        growth=(0, 10), fcf_ratio=0.3, dcf=False),
    "Media & Entertainment": dict(gm=(35, 60), nm=(5, 25), pe=(12, 40),
        growth=(0, 25), fcf_ratio=0.5, dcf=True),
    "Diversified / Unclassified": dict(gm=(30, 55), nm=(5, 20), pe=(10, 30),
        growth=(-5, 15), fcf_ratio=0.5, dcf=True),
}


def guess_sector(name: str) -> str:
    low = name.lower()
    for sector, kws in SECTOR_RULES:
        if any(k in low for k in kws):
            return sector
    return "Diversified / Unclassified"


def build_synthetic_profile(ticker: str, name: str) -> Dict[str, Any]:
    """Deterministic, clearly-labelled estimate profile for any ticker."""
    seed = int(hashlib.sha256(("syn:" + ticker.upper()).encode()).hexdigest()[:12], 16)
    rng = random.Random(seed)
    sector = guess_sector(name)
    sp = SECTOR_PROFILES[sector]

    price = round(rng.uniform(12, 280), 2)
    shares = rng.uniform(0.4e9, 9e9)
    mcap = price * shares
    rev = mcap * rng.uniform(0.30, 2.2)
    growth = rng.uniform(*sp["growth"])
    if "gm" in sp and sp["gm"] is not None:
        gm = rng.uniform(*sp["gm"])
    else:
        gm = None
    nm = rng.uniform(*sp["nm"])
    pe = rng.uniform(*sp["pe"])
    eps = price / pe
    fcf = rev * (nm / 100) * sp["fcf_ratio"]
    divy = rng.choice([0.0, 0.0, 0.0, 1.5, 2.5, 3.5])

    low52 = round(price * rng.uniform(0.62, 0.85), 2)
    high52 = round(price * rng.uniform(1.05, 1.45), 2)

    moat_score = rng.uniform(4.5, 7.0)
    moat_rating = "Wide Moat" if moat_score >= 7.5 else ("Narrow Moat" if moat_score >= 5.5 else "No Moat")

    return dict(
        name=name, sector=sector, industry=sector,
        exchange="Unknown", country="US", currency="USD", website="",
        employees="—",
        price=price, market_cap=mcap, low52=low52, high52=high52,
        data_quality="estimated",
        fundamentals=dict(rev=rev, rev_g=round(growth, 1), gm=round(gm, 1) if gm else None,
                          opm=round(nm * 0.8, 1), nm=round(nm, 1), eps=round(eps, 2),
                          pe=round(pe, 1), fwd_pe=round(pe * 0.85, 1),
                          ps=round(mcap / rev, 2), ev_ebitda=round(pe * 0.75, 1),
                          roic=round(nm * 0.6, 1), roe=round(nm * 0.75, 1),
                          fcf=fcf, cash=fcf * 0.4, debt=fcf * 0.3,
                          div=("—" if divy == 0 else f"~{divy}% est."), divy=divy),
        segments=[(sector + " — Core Operations", 100, "Segmental detail unavailable; model assumes single-segment economics")],
        biz=(f"{name} operates in the {sector} sector. No verified segmental detail "
             f"is in the local knowledge base, so this profile is a "
             f"model-generated estimate from sector-level norms (see disclaimer)."),
        moat=dict(rating=moat_rating + " (est.)", score=round(moat_score, 1), pillars=dict(
            network_effects=(round(rng.uniform(3, 7), 1), "Estimated from sector norms — unverified"),
            switching_costs=(round(rng.uniform(3, 7), 1), "Estimated from sector norms — unverified"),
            intangibles=(round(rng.uniform(3, 7.5), 1), "Estimated from sector norms — unverified"),
            cost_advantage=(round(rng.uniform(3, 7), 1), "Estimated from sector norms — unverified"),
            scale=(round(rng.uniform(3, 7), 1), "Estimated from sector norms — unverified"))),
        competitors=[dict(t="PEER 1", n="Sector peer (est.)", mc=None, rev=None, pe=None, note="Peer comparison unavailable for this ticker"),
                     dict(t="PEER 2", n="Sector peer (est.)", mc=None, rev=None, pe=None, note="Peer comparison unavailable for this ticker")],
        edge=("No verified competitive analysis is available for this ticker. "
              "Use the fundamentals and valuation sections as a first-pass "
              "screen; verify with primary sources before trading."),
        sentiment=dict(score=5.0, consensus="No Coverage", pt=None, pt_lo=None, pt_hi=None,
                       short="n/a"),
        news=[dict(d="—", h="No recent headline coverage in the local knowledge base for this ticker.", s="Local KB", i="mixed")],
        trends=[f"General {sector} sector dynamics (model-generated context)",
                "Macro: rates, inflation and AI capex remain the cross-sector drivers",
                "Watch: management guidance, guidance revisions and sector rotation"],
        swot=dict(
            s=[f"{sector} sector positioning (estimated)",
               f"Revenue base of ~{rev/1e9:.1f}B at {nm:.0f}% net margin (estimated)",
               "Deterministic model profile — verify with primary sources"],
            w=["No verified fundamentals in the local knowledge base",
               "Figures are model estimates from sector norms, not audited data",
               "No analyst coverage data available"],
            o=["Sector tailwinds (model context)",
               "Potential for re-rating if verified fundamentals confirm estimates",
               "Add primary-source data to upgrade this profile"],
            t=["Estimation risk: real fundamentals may differ materially",
               "Sector-specific risks (see trends)",
               "Liquidity and information risk for less-covered names"]),
        thesis=dict(
            bull=(f"Verified fundamentals beat model estimates; sector tailwind; re-rate to 1.3x model fair value.", round(price * 1.30, 2), 0.30),
            base=(f"Fundamentals in line with model estimates; steady growth to fair value.", round(price * 1.05, 2), 0.50),
            bear=(f"Fundamentals miss model estimates; sector headwind; de-rate to 0.75x model fair value.", round(price * 0.75, 2), 0.20)),
        dcf=None,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_TICKER_STOPWORDS = {"inc", "corp", "corp.", "corporation", "plc", "ltd", "limited",
                     "group", "holdings", "co", "company", "s.a.", "sa", "ag", "se",
                     "n.v.", "nv", "gmbh", "s.a", "systems", "technologies", "tech",
                     "industries", "international", "solutions", "services", "networks",
                     "communications", "digital", "pharma", "pharmaceutical", "capital",
                     "global", "worldwide", "enterprise", "partners", "labs", "laboratory"}


def derive_ticker(name: str) -> str:
    words = re.sub(r"[^a-z0-9 ]", " ", name.lower()).split()
    words = [w for w in words if w and w not in _TICKER_STOPWORDS]
    if not words:
        return "STOCK"
    core = re.sub(r"[^a-z0-9]", "", words[0])[:6].upper()
    return core or "STOCK"


def get_profile(query: str) -> Dict[str, Any]:
    """Return a full profile dict for any query (ticker or company name)."""
    ticker, display = resolve_ticker(query)
    if ticker in KB:
        p = dict(KB[ticker])
        p["ticker"] = ticker
        p.setdefault("data_quality", "verified")
        return p
    # Real tickers never contain spaces — if resolution fell back to the
    # upper-cased company name, derive a proper ticker instead.
    if not ticker or " " in ticker:
        ticker = derive_ticker(display)
    p = build_synthetic_profile(ticker, display)
    p["ticker"] = ticker
    p["resolved_from_name"] = (display.lower() != query.strip().lower())
    return p


def list_profiles() -> list:
    return [
        dict(ticker=k, name=v["name"], sector=v["sector"], price=v["price"],
             currency=v.get("currency", "USD"), country=v.get("country", "US"),
             exchange=v.get("exchange", ""))
        for k, v in sorted(KB.items())
    ]
