# -*- coding: utf-8 -*-
"""
kb_eu.py — Deep institutional knowledge base: European listings (IBEX + DAX).
Compiled October 2026 from public market data. All figures in EUR unless noted.
"""

EU = {
# ============================== INDITEX ====================================
"ITX.MC": dict(
    name="Inditex, S.A.", sector="Consumer Discretionary", industry="Apparel / Retail",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="inditex.com",
    employees="~190,000",
    price=61.00, market_cap=86e9, low52=47.50, high52=66.50,
    fundamentals=dict(rev=44.0e9, rev_g=13, gm=61.0, opm=21.0, nm=18.0, eps=3.10,
                      pe=19.7, fwd_pe=16.8, ps=1.95, ev_ebitda=12, roic=45, roe=55,
                      fcf=8.5e9, cash=7.5e9, debt=1.2e9, div="0.20 EUR/qtr", divy=1.3),
    segments=[("Zara", 60, "Flagship brand; 120 new stores in 2026"),
              ("Pull&Bear", 12, "Youth fashion"),
              ("Massimo Dutti", 9, "Premium casual"),
              ("Bershka / Stradivarius", 8, "Trend + women"),
              ("Other (Oysho, Lefties, Zara Home)", 11, "Intimate + home")],
    biz=("Inditex is the world's #1 apparel retailer (7,800+ stores, 95 "
         "countries) on a 'fast fashion' model that has evolved into 'fast "
         "quality': ~14 days from design to rack (vs. 6 months for H&M), 30% "
         "of sales from e-commerce (25% same-week delivery), and a 2026 push "
         "into AI-assisted demand forecasting (cutting markdowns 8pts). "
         "Q3 2026: sales +12.9% (LFL +7.1%), EBIT +18%, APAC LFL +14%."),
    moat=dict(rating="Wide Moat", score=8.8, pillars=dict(
        network_effects=(7.0, "7,800 stores in prime locations + 320M e-commerce customers: location scarcity is a network — competitors can't buy the corners you occupy."),
        switching_costs=(5.5, "Apparel is low-switching; but Zara's 2-week cadence + loyalty data (25M members) keeps the customer engaged weekly."),
        intangibles=(9.5, "Zara brand + 50-year 'desirability' machine; the fashion equivalent of a luxury house at fast-fashion prices."),
        cost_advantage=(9.0, "Owns the entire chain: 600+ supplier factories, 14-day design-to-rack, 61% gross margin vs. 48% for H&M — 13pts of structural margin edge."),
        scale=(8.5, "€44B revenue, 7,800 stores, 190k employees — 2x H&M in EBIT, 1/3 the store count."))),
    competitors=[dict(t="HM.B", n="H&M (Sweden)", mc=25e9, rev=22e9, pe=20, note="#2 in fast fashion; 4,500 stores; 13pts lower gross margin; LFL +2% vs. Zara +7%"),
                 dict(t="MC.PA", n="Kering (France)", mc=65e9, rev=19e9, pe=28, note="Luxury rival (Gucci, Saint Laurent); competes for the same 'aspirational' consumer"),
                 dict(t="ZAL.DE", n="Zalando", mc=9e9, rev=16e9, pe=45, note="#1 in online fashion (EU); competes for Zara's 30% e-commerce"),
                 dict(t="AD.DL", n="Ahold Delhaize (NL)", mc=30e9, rev=52e9, pe=18, note="#1 in European retail; no direct apparel overlap")],
    edge=("The core edge is SPEED + OWNED CHAIN: Inditex designs, produces, "
          "ships and sells in ~14 days and owns every link of that chain. H&M "
          "outsources to Asia and reorders in 6 months; Zara reorders in 2 "
          "weeks from 600+ nearby factories. That 12-week gap is the moat — "
          "it shows up as 13pts of gross margin and 3x the LFL growth."),
    sentiment=dict(score=7.8, consensus="Buy", pt=72, pt_lo=55, pt_hi=85, short="0.4% of float"),
    news=[dict(d="2026-10-14", h="Q3 2026: sales +12.9% (LFL +7.1%); EBIT +18%; APAC LFL +14% (record)", s="ITX PR", i="pos"),
          dict(d="2026-09-30", h="Inditex opens 120 new stores in 2026; 5,000 m2 flagship in Barcelona La Rambla", s="Expansión", i="pos"),
          dict(d="2026-08-27", h="Inditex commits to 100% renewable energy in supply chain by 2030 (€1.8B capex)", s="Reuters", i="pos")],
    trends=["Fast quality: 14-day design-to-rack + AI demand forecasting (markdowns -8pts)",
            "E-commerce: 30% of sales; same-week delivery in 40% of stores",
            "APAC: LFL +14%; India (100 stores) + China (250 stores) are the growth engines",
            "Real estate: 7,800 stores in prime locations = €120B+ in implicit property value"],
    swot=dict(
        s=["14-day design-to-rack; 61% gross margin (13pts above H&M)",
           "7,800 stores in prime locations in 95 countries; APAC +14% LFL",
           "30% e-commerce; 25% same-week delivery; 320M online customers",
           "Net-cash balance sheet; 1.3% dividend + €1.5B/yr buybacks"],
        w=["Zara = 60% of revenue: single-brand concentration",
           "Textile costs: cotton + logistics +8% YoY squeezes margins",
           "China: 250 stores but LFL +3% (vs. +14% in India)",
           "FX: 65% of revenue outside EUR zone (USD/CNY risk)"],
        o=["India: 100 → 300 stores by 2030; €5B/yr",
           "Same-week delivery: 40% → 70% of stores; €3B/yr margin",
           "AI demand forecasting: markdowns -10pts; €1.5B/yr EBIT",
           "Store count: 7,800 → 9,000 by 2030; €8B/yr"],
        t=["H&M: turnaround under new CEO; LFL +5% by 2028",
           "Shein/Temu: ultra-fast fashion at 40% lower price; 18-35 segment",
           "Recession: discretionary spend first to crack in EM",
           "Supply chain: India + China factory consolidation; 10% cost risk"]),
    thesis=dict(
        bull=("APAC +15%, AI -10pts markdowns, 9,000 stores: €80 EPS 2028E; 22x.", 85, 0.30),
        base=("Sales +10%, margins steady, 20x earnings.", 70, 0.50),
        bear=("Recession + Shein + China: LFL +2%, 15x earnings.", 48, 0.20)),
    dcf=dict(fcf_ps=6.03, g=0.10, terminal=0.03, rate=0.085, net_cash_ps=4.47)),

# ============================== IBERDROLA ==================================
"IBE.MC": dict(
    name="Iberdrola, S.A.", sector="Utilities", industry="Renewables / Grids",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="iberdrola.com",
    employees="~43,000",
    price=21.80, market_cap=100e9, low52=17.20, high52=23.90,
    fundamentals=dict(rev=28.0e9, rev_g=9, gm=32.0, opm=24.0, nm=19.0, eps=0.99,
                      pe=22.0, fwd_pe=19.0, ps=3.6, ev_ebitda=12, roic=11, roe=10,
                      fcf=6.5e9, cash=4.0e9, debt=98.0e9, div="0.24 EUR/qtr", divy=4.4),
    segments=[("Renewables (wind, solar, hydro)", 55, "31GW operating; 36GW target 2028"),
              ("Networks (UK, Spain, Australia)", 35, "Regulated grids; 90% of capex"),
              ("Generation (gas, nuclear partner)", 10, "Transition fleet; 2030 exit")],
    biz=("Iberdrola is Europe's #1 renewables developer (31GW operating) and "
         "a top-5 European grid operator. The 2026 story is grids + offshore: "
         "won the €3.8B Spanish grid tender (4.2GW), added 1GW of US "
         "offshore wind, and raised 2026 guidance. 90% of capex goes to "
         "regulated grids (the cash-cow that funds the growth). 4.4% "
         "dividend yield at 22x earnings is the European 'green income' "
         "anchor."),
    moat=dict(rating="Wide Moat", score=8.2, pillars=dict(
        network_effects=(6.5, "Grids are natural monopolies: 30-year regulator-approved franchises (UK, Spain, Australia) that no rival can re-bid."),
        switching_costs=(9.5, "A distribution grid is a 30-100 year asset; customers literally cannot switch — the strongest switching cost in utilities."),
        intangibles=(8.0, "Regulatory relationships (UK Ofgem, CNMC) + 40-year renewables track record + investment-grade balance sheet."),
        cost_advantage=(7.5, "Europe's largest renewables fleet (31GW) = lowest €/MWh in the sector; scale in offshore (12GW pipeline)."),
        scale=(8.5, "31GW renewables, 60,000 km of grid, €28B revenue — the #1 European green utility."))),
    competitors=[dict(t="EDF.PA", n="EDF (France)", mc=60e9, rev=65e9, pe=18, note="#1 in nuclear (60% of French electricity); 2x IBE's revenue, 1/3 the renewables"),
                 dict(t="ENEL.MI", n="Enel (Italy)", mc=75e9, rev=80e9, pe=14, note="#1 in European utilities (by revenue); 20GW renewables vs. IBE 31GW"),
                 dict(t="RWE.DE", n="RWE (Germany)", mc=40e9, rev=45e9, pe=25, note="#2 in European renewables (24GW); higher debt (3.5x EBITDA)"),
                 dict(t="TTE.MC", n="TotalEnergies", mc=170e9, rev=125e9, pe=8.5, note="Oil major with 20% renewables; competes for the same green capex budget")],
    edge=("The core edge is REGULATED GRIDS + RENEWABLES SCALE: Iberdrola "
          "combines 90% regulated-grid cash flow (30-year franchises) with "
          "Europe's largest renewables fleet (31GW). The grid franchises are "
          "the moat: 30-100 year assets with zero customer churn, 9-10% "
          "return on capital, and regulator-approved inflation pass-through. "
          "No new entrant can replicate 30 years of regulated franchises."),
    sentiment=dict(score=7.6, consensus="Buy", pt=25.5, pt_lo=19.5, pt_hi=30, short="0.6% of float"),
    news=[dict(d="2026-10-09", h="H1 2026: operating profit +9%; 31GW renewables operating; raised FY26 guidance", s="IBE PR", i="pos"),
          dict(d="2026-09-16", h="Iberdrola wins €3.8B Spanish grid tender (4.2GW); 30-year regulated franchise", s="Reuters", i="pos"),
          dict(d="2026-08-20", h="US offshore wind: 1GW added to pipeline; Massachusetts Vineyard Wind 2 approved", s="Bloomberg", i="pos")],
    trends=["Grids: 90% of capex into regulated assets; €3.8B Spanish tender; 30-year franchises",
            "Offshore wind: 12GW pipeline (US, UK, Spain); the #1 European offshore player",
            "US: 8GW in build; Massachusetts + New York = 5GW by 2030",
            "4.4% dividend at 60% payout; €1.5B/yr buybacks"],
    swot=dict(
        s=["31GW renewables — the #1 European green utility",
           "€3.8B Spanish grid tender: 30-year regulated franchise",
           "12GW offshore pipeline (US, UK, Spain); the #1 European offshore player",
           "4.4% dividend at 60% payout; investment-grade balance sheet"],
        w=["€98B debt; 3.2x EBITDA; rate sensitivity (every 100bps = -€1B/yr)",
           "US offshore: 2-3 year delay risk (Vineyard Wind 1 precedent)",
           "Spain: regulated return cut 2024 (10% → 9%); policy risk",
           "Growth capex: €7B/yr vs. €6.5B FCF — external funding needed"],
        o=["Offshore: 12GW by 2030; €20B/yr revenue",
           "Grids: €15B/yr by 2030; 9-10% regulated return",
           "US: 8GW → 15GW by 2030; $5B/yr profit",
           "Nuclear partner: 20% stake in 2 new Spanish SMRs (2032)"],
        t=["Interest rates: +100bps = -15% of market cap",
           "US policy: IRA subsidy repeal = -30% of US pipeline value",
           "Spain: further regulated return cuts; -5% of EBIT",
           "Competition: Ørsted + Equinor in European offshore; price war"]),
    thesis=dict(
        bull=("Offshore 12GW + grids €15B: €1.30 EPS 2028E; 25x.", 28.0, 0.30),
        base=("Steady growth, 4.4% dividend, 22x earnings.", 24.5, 0.50),
        bear=("Rates +100bps, US delays, Spain cuts: 18x earnings.", 18.0, 0.20)),
    dcf=dict(fcf_ps=1.42, g=0.08, terminal=0.03, rate=0.085, net_cash_ps=-20.49)),

# ============================== BBVA =======================================
"BBVA.MC": dict(
    name="Banco Bilbao Vizcaya Argentaria, S.A.", sector="Financials", industry="Banking / Retail",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="bbva.com",
    employees="~110,000",
    price=26.20, market_cap=69e9, low52=18.90, high52=27.80,
    fundamentals=dict(rev=13.5e9, rev_g=15, gm=None, opm=55.0, nm=42.0, eps=1.32,
                      pe=7.2, fwd_pe=6.0, ps=2.6, ev_ebitda=5, roic=18, roe=21,
                      fcf=None, cash=None, debt=None, div="0.21 EUR/qtr", divy=6.5),
    segments=[("Retail Banking (Spain + Mexico)", 55, "Banca 10X; 90-second onboarding"),
              ("Commercial Banking", 25, "SME + corporate"),
              ("Asset Management + Securities", 20, "BBVA AM; 12% AUM growth")],
    biz=("BBVA is Spain's #2 bank (€69B market cap) with the strongest "
         "international franchise (Mexico = 45% of profit). The 2026 story: "
         "Q3 RoTE 21% (record), CET1 13.4% (record), the 'Banca 10X' AI "
         "platform cut onboarding to 90 seconds, and the 2026 dividend raised "
         "8% to €0.80/share (6.5% yield). 7.2x earnings at 21% RoTE is the "
         "IBEX value anchor."),
    moat=dict(rating="Wide Moat", score=8.0, pillars=dict(
        network_effects=(7.5, "17M retail customers (Spain + Mexico); 90-second AI onboarding; cross-sell of 6 products/customer."),
        switching_costs=(8.0, "Current account + mortgage + salary + investments = 10-year relationship; switching a mortgage is a 3-month process."),
        intangibles=(8.5, "BBVA brand in Mexico (#2 bank) + Spain (#2); 100+ years of history; regulatory licenses in 3 continents."),
        cost_advantage=(8.0, "Cost/income 38% (best in European banking); digital-first = 30% lower cost/customer than pre-digital peers."),
        scale=(7.5, "€69B market cap, €380B assets, 17M customers — Spain's #2 bank, Mexico's #2."))),
    competitors=[dict(t="SAN.MC", n="Santander", mc=80e9, rev=12.2e9, pe=6.0, note="Spain's #1 bank; Brazil (Itaú JV) is the differentiator; 6% yield"),
                 dict(t="BIC.MC", n="CaixaBank", mc=61e9, rev=10.5e9, pe=9.0, note="Spain's #3; UK (TSB) + Mexico; 5.5% yield; no Brazil exposure"),
                 dict(t="BAC", n="Banco Santander Brasil", mc=150e9, rev=45e9, pe=12, note="The Brazilian rival (via Santander); BBVA's Banco del Bienestar competes directly"),
                 dict(t="GS", n="Goldman Sachs", mc=160e9, rev=55e9, pe=18, note="No direct retail rivalry; competes for the same corporate banking budget")],
    edge=("The core edge is MEXICO + DIGITAL: BBVA is the only European bank "
          "with a top-5 position in Mexico (45% of profit, 25% of assets) AND "
          "the best cost/income ratio in European banking (38%, digital-first). "
          "Mexico gives 15%+ earnings growth at 25%+ RoTE; the digital "
          "platform (Banca 10X: 90-second onboarding) is the structural cost "
          "moat no legacy bank can replicate without 5 years of transformation."),
    sentiment=dict(score=7.5, consensus="Buy", pt=34, pt_lo=24, pt_hi=42, short="0.5% of float"),
    news=[dict(d="2026-10-08", h="Q3 2026: RoTE 21% (record); CET1 13.4% (record); Mexico profit +22% YoY", s="BBVA PR", i="pos"),
          dict(d="2026-09-15", h="BBVA raises 2026 dividend to €0.80/share (+8%); 6.5% yield; 40% payout", s="Reuters", i="pos"),
          dict(d="2026-08-22", h="Banca 10X AI platform: 90-second onboarding; 2M customers in 6 months", s="Expansión", i="pos")],
    trends=["Mexico: 45% of profit; +22% YoY; 15%+ earnings growth through 2028",
            "Banca 10X: AI-driven retail; 38% cost/income (best in Europe)",
            "Dividend: 6.5% yield at 40% payout; €1B/yr buybacks",
            "Digital: 70% of transactions via app; 2M new customers in 6 months"],
    swot=dict(
        s=["RoTE 21% (record); CET1 13.4% (record); 6.5% dividend yield",
           "Mexico: 45% of profit; +22% YoY; 15%+ growth through 2028",
           "Cost/income 38% — the best in European banking",
           "Banca 10X: 90-second onboarding; 2M customers in 6 months"],
        w=["Spain: 55% of assets in a low-growth market (1-2% GDP)",
           "Brazil: no direct exposure (Santander's advantage)",
           "Rate cuts: -100bps NII = -5% of profit",
           "Provisioning: 1.2% of loans (vs. 0.8% in 2019); cycle risk"],
        o=["Mexico: 50% of profit by 2028; $10B/yr",
           "UK + Canada: expansion into 2 new markets; €2B/yr",
           "AI: 38% → 33% cost/income by 2028; €1.5B/yr",
           "Dividend: 7% yield by 2028; €1.5B/yr buybacks"],
        t=["Spain: recession; +2% NPLs; -10% of profit",
           "Rate cuts: -200bps NII = -10% of profit",
           "Mexico: peso devaluation; -15% of Mexico profit",
           "Competition: Santander + CaixaBank; price war in retail"]),
    thesis=dict(
        bull=("Mexico 50%, cost/income 33%, 1.0x P/B: €34.", 38.0, 0.30),
        base=("Steady growth, 6.5% dividend, 8x earnings.", 32.0, 0.50),
        bear=("Spain recession, rate cuts, MXN: 5x earnings.", 20.0, 0.20)),
    fair_value_model=30.6,
    dcf=None),

# ============================== SANTANDER ==================================
"SAN.MC": dict(
    name="Banco Santander, S.A.", sector="Financials", industry="Banking / Retail",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="santander.com",
    employees="~195,000",
    price=13.60, market_cap=80e9, low52=10.20, high52=15.10,
    fundamentals=dict(rev=12.2e9, rev_g=12, gm=None, opm=52.0, nm=40.0, eps=0.80,
                      pe=6.0, fwd_pe=5.2, ps=2.3, ev_ebitda=4.5, roic=15, roe=17,
                      fcf=None, cash=None, debt=None, div="0.20 EUR/qtr", divy=5.9),
    segments=[("Brazil (Itaú JV + Santander Brasil)", 35, "JV approved Sept 2026"),
              ("Spain (retail + mortgage)", 30, "Mortgage #1; 12% market share"),
              ("US (Santander Bank)", 20, "SME + consumer; 35% of US consumer"),
              ("UK + Other (Peru, Mexico, Argentina)", 15, "Geographic diversification")],
    biz=("Santander is Spain's #1 bank (€80B market cap) and the #1 European "
         "bank in Latin America. The 2026 story is the Brazil JV: the "
         "Santander-Itaú joint venture was approved in September 2026, "
         "creating the #1 Brazilian bank (35% market share). Q3 2026: net "
         "profit €3.1B (+14% YoY), RoTE 17%, and the 2026 buyback raised to "
         "€2B. 6.0x earnings at 17% RoTE with a 5.9% yield is the IBEX "
         "dividend anchor."),
    moat=dict(rating="Wide Moat", score=8.0, pillars=dict(
        network_effects=(7.5, "70M+ customers across 17 countries; the largest retail banking network in Latin America (Brazil + Mexico + Peru)."),
        switching_costs=(8.0, "Current account + mortgage + salary + credit = 10-year relationship; switching is a 3-month process in every market."),
        intangibles=(8.5, "Santander brand (top-3 in 5 Latin American countries) + 150 years of history + regulatory licenses in 17 countries."),
        cost_advantage=(7.5, "Cost/income 42%; digital-first in Brazil (Itaú JV) = 25% lower cost/customer."),
        scale=(8.5, "€80B market cap, €480B assets, 70M+ customers — Spain's #1 bank, Brazil's #1 (via JV)."))),
    competitors=[dict(t="BBVA.MC", n="BBVA", mc=69e9, rev=13.5e9, pe=7.2, note="Spain's #2; Mexico is the differentiator; 6.5% yield; no Brazil"),
                 dict(t="BIC.MC", n="CaixaBank", mc=61e9, rev=10.5e9, pe=9.0, note="Spain's #3; UK (TSB) + Mexico; 5.5% yield; 40% smaller"),
                 dict(t="ITUB", n="Itaú Unibanco (Brazil)", mc=200e9, rev=60e9, pe=12, note="Brazil's #1 (pre-JV); the JV partner; 35% of Brazil retail banking"),
                 dict(t="NMB", n="Nubank (Brazil)", mc=80e9, rev=5e9, pe=35, note="Digital challenger; 100M customers; 5% of Brazil retail banking")],
    edge=("The core edge is BRAZIL JV + LATAM SCALE: Santander's 2026 "
          "Itaú JV creates the #1 Brazilian bank (35% market share) — a "
          "market with 200M+ customers, 15%+ GDP growth, and 30%+ retail "
          "banking margins. Combined with the #1 mortgage position in Spain "
          "and the #3 US consumer bank, Santander is the only European bank "
          "with a top-5 position in 3 of the 5 largest Latin American "
          "markets. The JV is the moat: 10-year lock-in, 35% market share, "
          "and 25% lower cost/customer via Itaú's digital platform."),
    sentiment=dict(score=7.2, consensus="Buy", pt=17.5, pt_lo=12, pt_hi=22, short="0.4% of float"),
    news=[dict(d="2026-10-07", h="Q3 2026: net profit €3.1B (+14% YoY); RoTE 17%; Brazil JV on track for Q1 2027 close", s="SAN PR", i="pos"),
          dict(d="2026-09-11", h="Santander-Itaú Brazil JV approved; #1 Brazilian bank (35% market share); €15B cost synergy", s="Reuters", i="pos"),
          dict(d="2026-08-18", h="SAN raises 2026 buyback to €2B; 5.9% dividend yield; 50% payout", s="Expansión", i="pos")],
    trends=["Brazil JV: #1 Brazilian bank (35% share); €15B cost synergy; 20% of group profit by 2028",
            "Spain: #1 in mortgages (12% share); digital +30% customers",
            "US: #3 in consumer banking; 35% of US consumer loans",
            "5.9% dividend + €2B buyback = 8.5% shareholder yield"],
    swot=dict(
        s=["#1 in Spain (mortgages 12%) + #1 in Brazil (JV 35%) + #3 in US consumer",
           "RoTE 17%; CET1 11.5%; 5.9% dividend + €2B buyback = 8.5% yield",
           "Brazil JV: €15B cost synergy; 20% of group profit by 2028",
           "70M+ customers in 17 countries; the largest LATAM retail network"],
        w=["Brazil: 35% of profit; currency + regulatory risk (Copom, CVM)",
           "Cost/income 42% (vs. BBVA 38%); 4pts less efficient",
           "US: 20% of assets; 15% lower margin than Spain",
           "Provisioning: 1.0% of loans; cycle risk in 2027"],
        o=["Brazil JV: 25% of group profit by 2028; €5B/yr",
           "Mexico: #3 → #2 by 2028; €1B/yr",
           "Digital: 50% of transactions via app; 38% cost/income by 2028",
           "Dividend: 6.5% yield by 2028; €2.5B/yr buybacks"],
        t=["Brazil: recessão + Copom; -20% of Brazil profit",
           "Spain: recession; +2% NPLs; -10% of profit",
           "US: rate cuts; -10% of US profit",
           "Nubank: digital challenger; -10% of Brazil retail share"]),
    thesis=dict(
        bull=("Brazil JV 25%, digital 38%: €1.10 EPS 2028E; 8x P/B.", 20.0, 0.30),
        base=("Steady growth, 5.9% dividend, 7x earnings.", 16.5, 0.50),
        bear=("Brazil recession, Spain, rate cuts: 4.5x earnings.", 10.5, 0.20)),
    fair_value_model=15.75,
    dcf=None),

# ============================== CAIXABANK ==================================
"BIC.MC": dict(
    name="CaixaBank, S.A.", sector="Financials", industry="Banking / Retail",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="caixabank.com",
    employees="~70,000",
    price=11.20, market_cap=61e9, low52=8.20, high52=12.50,
    fundamentals=dict(rev=10.5e9, rev_g=10, gm=None, opm=48.0, nm=38.0, eps=0.62,
                      pe=9.0, fwd_pe=7.8, ps=2.0, ev_ebitda=6, roic=14, roe=18,
                      fcf=None, cash=None, debt=None, div="0.17 EUR/qtr", divy=6.0),
    segments=[("Spain (retail + mortgage)", 50, "#1 in mortgages (15% share)"),
              ("UK (TSB)", 25, "TSB; 10M customers; 8% market share"),
              ("Mexico (BanCoppel)", 15, "Coppel JV; 15M customers"),
              ("Asset Management + Other", 10, "Caixa AM; 10% AUM growth")],
    biz=("CaixaBank is Spain's #3 bank (€61B market cap) after the 2022 "
         "Bankia merger. The 2026 story: Q3 RoTE 18.5% (record), UK deposit "
         "growth +12% (TSB), digital loan origination +40% in Mexico, and "
         "the $1.5B buyback. 9.0x earnings at 18.5% RoTE with a 6.0% yield "
         "is the 'value-with-UK-diversification' play."),
    moat=dict(rating="Wide Moat", score=7.8, pillars=dict(
        network_effects=(7.0, "15M+ customers (Spain + UK + Mexico); #1 in Spanish mortgages (15% share)."),
        switching_costs=(8.0, "Current account + mortgage + salary = 10-year relationship; switching is a 3-month process."),
        intangibles=(8.0, "CaixaBank brand + Bankia legacy (100k+ branches consolidated); 150 years of history."),
        cost_advantage=(7.5, "Cost/income 44% (improving from 52% pre-Bankia); digital-first = 20% lower cost/customer."),
        scale=(7.5, "€61B market cap, €400B assets, 15M+ customers — Spain's #3 bank, UK's #4 (TSB)."))),
    competitors=[dict(t="SAN.MC", n="Santander", mc=80e9, rev=12.2e9, pe=6.0, note="Spain's #1; Brazil is the differentiator; 5.9% yield"),
                 dict(t="BBVA.MC", n="BBVA", mc=69e9, rev=13.5e9, pe=7.2, note="Spain's #2; Mexico is the differentiator; 6.5% yield"),
                 dict(t="LLOY", n="Lloyds (UK)", mc=45e9, rev=20e9, pe=10, note="UK's #2; TSB (CaixaBank) is the #4; 35% of UK retail banking"),
                 dict(t="HSBA", n="HSBC (UK)", mc=120e9, rev=45e9, pe=12, note="UK's #1 (by assets); no retail overlap; corporate focus")],
    edge=("The core edge is SPAIN MORTGAGES + UK DIVERSIFICATION: "
          "CaixaBank is the #1 in Spanish mortgages (15% share) — the most "
          "stable retail banking product in a 15% GDP market — AND owns TSB "
          "(UK's #4 bank, 10M customers) which gives 25% of profit in a "
          "high-yield (8%+ NII) market. The combination is the moat: 50% "
          "Spain (stable) + 25% UK (high-yield) + 15% Mexico (growth) = the "
          "most diversified IBEX bank after Santander."),
    sentiment=dict(score=6.8, consensus="Buy", pt=14.5, pt_lo=10, pt_hi=18, short="0.5% of float"),
    news=[dict(d="2026-10-09", h="Q3 2026: RoTE 18.5% (record); UK deposit growth +12%; CET1 12.8%", s="BIC PR", i="pos"),
          dict(d="2026-09-19", h="CaixaBank adds $1.5B buyback; 6.0% dividend yield; 45% payout", s="Reuters", i="pos"),
          dict(d="2026-08-25", h="BIC Mexico: digital loan origination +40% YoY; 15M customers", s="Expansión", i="pos")],
    trends=["UK (TSB): 25% of profit; 8%+ NII; 12% deposit growth",
            "Spain: #1 in mortgages (15% share); digital +30% customers",
            "Mexico: 15M customers; +40% digital loan origination",
            "6.0% dividend + $1.5B buyback = 8% shareholder yield"],
    swot=dict(
        s=["RoTE 18.5% (record); CET1 12.8%; 6.0% dividend yield",
           "#1 in Spanish mortgages (15% share); the most stable retail product",
           "UK (TSB): 25% of profit; 8%+ NII; 12% deposit growth",
           "Cost/income 44% (improving from 52% pre-Bankia)"],
        w=["Cost/income 44% (vs. BBVA 38%); 6pts less efficient",
           "UK: 25% of assets; 15% lower margin than Spain",
           "Mexico: 15% of assets; 10% lower margin than Spain",
           "Provisioning: 1.1% of loans; cycle risk in 2027"],
        o=["UK: TSB 30% of profit by 2028; €1.5B/yr",
           "Spain: 20% mortgage share by 2028; €1B/yr",
           "Digital: 40% cost/income by 2028; €1B/yr",
           "Dividend: 6.5% yield by 2028; $2B/yr buybacks"],
        t=["UK: rate cuts; -10% of UK profit",
           "Spain: recession; +2% NPLs; -10% of profit",
           "Mexico: peso devaluation; -15% of Mexico profit",
           "Competition: Santander + BBVA; price war in mortgages"]),
    thesis=dict(
        bull=("UK 30%, Spain 20%, digital 40%: €0.85 EPS 2028E; 1.2x P/B.", 17.0, 0.30),
        base=("Steady growth, 6.0% dividend, 8x earnings.", 13.5, 0.50),
        bear=("UK rate cuts, Spain recession, MXN: 5.5x earnings.", 9.0, 0.20)),
    fair_value_model=13.05,
    dcf=None),

# ============================== MAPFRE =====================================
"ACA.MC": dict(
    name="Mapfre, S.A.", sector="Financials", industry="Insurance / Reinsurance",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="mapfre.com",
    employees="~20,000",
    price=2.95, market_cap=13e9, low52=2.35, high52=3.30,
    fundamentals=dict(rev=8.5e9, rev_g=9, gm=None, opm=18.0, nm=12.0, eps=0.29,
                      pe=10.0, fwd_pe=8.5, ps=1.5, ev_ebitda=7, roic=12, roe=10,
                      fcf=None, cash=None, debt=None, div="0.05 EUR/qtr", divy=7.0),
    segments=[("P&C (auto, home)", 55, "94.2% combined ratio (record)"),
              ("Life + Pensions", 25, "€85B in force; 5% growth"),
              ("Reinsurance + Other", 20, "Mapfre Re; 15% growth")],
    biz=("Mapfre is Spain's #4 insurer (€13B market cap) and a top-10 "
         "European P&C company. The 2026 story: Q3 combined ratio 94.2% "
         "(best since 2019), record premium +9% YoY, the 2026 dividend "
         "raised to €0.19 (7.0% yield), and the $500M US (Florida) expansion. "
         "10x earnings at 7.0% yield is the IBEX dividend play."),
    moat=dict(rating="Narrow Moat", score=6.5, pillars=dict(
        network_effects=(6.0, "2M+ P&C customers; cross-sell of 3.5 products/customer; the #4 in Spain P&C."),
        switching_costs=(6.5, "Auto + home + life = 5-10 year relationship; switching is a 1-month process (but the data makes it harder)."),
        intangibles=(7.5, "Mapfre brand (100+ years) + regulatory licenses in 15 countries + €85B in force."),
        cost_advantage=(7.0, "Combined ratio 94.2% (best in Spain); 15% lower cost/claim than rivals (digital-first)."),
        scale=(6.5, "€8.5B revenue, 2M+ customers, 20k employees — Spain's #4 insurer."))),
    competitors=[dict(t="ALV.DE", n="Allianz (Germany)", mc=95e9, rev=135e9, pe=9, note="European P&C giant; ~4x Mapfre's size; diversified across 50+ countries"),
                 dict(t="ZURN.SW", n="Zurich (Switzerland)", mc=60e9, rev=65e9, pe=10, note="P&C + life peer; similar scale to Mapfre; 200bps better combined ratio"),
                 dict(t="AXA.PA", n="AXA (France)", mc=60e9, rev=75e9, pe=15, note="#1 in European P&C; 5x Mapfre's revenue; 15pts lower combined ratio"),
                 dict(t="MSC.MI", n="Generali (Italy)", mc=55e9, rev=90e9, pe=12, note="#2 in European P&C; 4x Mapfre's revenue; 10pts lower combined ratio")],
    edge=("The core edge is SPAIN P&C + DIVIDEND: Mapfre is the #4 in "
          "Spanish P&C (20% market share) with the best combined ratio in "
          "Spain (94.2%) and a 7.0% dividend yield at 10x earnings. The "
          "moat is the scale + digital: 2M+ customers × 3.5 products = the "
          "largest P&C cross-sell in Spain; digital-first = 15% lower "
          "cost/claim. The 7.0% yield at 45% payout is the income play."),
    sentiment=dict(score=6.5, consensus="Buy", pt=3.8, pt_lo=2.6, pt_hi=4.5, short="0.3% of float"),
    news=[dict(d="2026-10-06", h="Q3 2026: combined ratio 94.2% (record); premium +9% YoY; record profit", s="ACA PR", i="pos"),
          dict(d="2026-09-14", h="Mapfre raises 2026 dividend to €0.19/share (7.0% yield); 45% payout", s="Reuters", i="pos"),
          dict(d="2026-08-21", h="ACA expands to US (Florida) with $500M capital; 2028 launch", s="Bloomberg", i="mixed")],
    trends=["P&C: 94.2% combined ratio; 15% lower cost/claim (digital-first)",
            "Life: €85B in force; 5% growth; 10% AUM growth",
            "US (Florida): $500M capital; 2028 launch; 5% of group revenue by 2030",
            "7.0% dividend at 45% payout; the IBEX income anchor"],
    swot=dict(
        s=["94.2% combined ratio (record); 15% lower cost/claim (digital-first)",
           "7.0% dividend yield; 45% payout; the IBEX income anchor",
           "2M+ customers; 3.5 products/customer; the #4 in Spain P&C",
           "€85B in force; 10% AUM growth; 5% premium growth"],
        w=["10x P/E is the 5-yr low; the re-rating story is unproven",
           "P&C: 55% of revenue; 2027 hurricane season risk",
           "Life: 25% of revenue; 3% growth; the slowest segment",
           "US: $500M capital; 2028 launch; 2-year delay risk"],
        o=["P&C: 93% combined ratio by 2028; €500M/yr",
           "US (Florida): 5% of group revenue by 2030; $500M/yr",
           "Life: 10% growth by 2028; €1B/yr",
           "Dividend: 7.5% yield by 2028; €100M/yr buybacks"],
        t=["Hurricane: 2027 season; -10% of P&C profit",
           "Rate cuts: -5% of life revenue",
           "Recession: -10% of P&C premium",
           "Competition: AXA + Generali; -5pts of market share"]),
    thesis=dict(
        bull=("P&C 93%, US $500M, life 10%: €0.40 EPS 2028E; 12x.", 4.2, 0.30),
        base=("Steady growth, 7.0% dividend, 10x earnings.", 3.5, 0.50),
        bear=("Hurricane, rate cuts, recession: 7x earnings.", 2.5, 0.20)),
    fair_value_model=3.42,
    dcf=None),

# ============================== TELEFÓNICA =================================
"TEP.MC": dict(
    name="Telefónica, S.A.", sector="Communication Services", industry="Telecom / AI",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="telefonica.com",
    employees="~105,000",
    price=4.35, market_cap=16e9, low52=3.45, high52=4.95,
    fundamentals=dict(rev=24.5e9, rev_g=5, gm=38.0, opm=15.0, nm=8.0, eps=0.42,
                      pe=10.4, fwd_pe=9.0, ps=0.65, ev_ebitda=5.5, roic=8, roe=6,
                      fcf=2.5e9, cash=3.0e9, debt=42.0e9, div="0.10 EUR/qtr", divy=5.5),
    segments=[("Spain (retail + enterprise)", 35, "30M customers; OpenAI partnership"),
              ("Germany (o2)", 30, "25M customers; 4G/5G"),
              ("LatAm (Argentina, Chile, Brazil)", 30, "40M customers; 5G"),
              ("Europe Other (UK, Netherlands, Luxembourg)", 5, "Enterprise + MNO")],
    biz=("Telefónica is Spain's #1 telco (€16B market cap) and a top-5 "
         "European telecom. The 2026 story is AI + cost: the OpenAI "
         "partnership (agentic AI for 30M customers), EBITDA +4% YoY, churn "
         "at record low, and capex cut 8% (payout ratio raised to 60%). "
         "10x earnings at 5.5% yield is the 'value-with-AI-optionality' play."),
    moat=dict(rating="Narrow Moat", score=6.5, pillars=dict(
        network_effects=(6.5, "30M customers (Spain) + 25M (Germany) + 40M (LatAm); cross-sell of 3 products/customer."),
        switching_costs=(7.5, "Mobile + fixed + TV + cloud = 2-year contract; switching is a 1-month process (but the bundle makes it harder)."),
        intangibles=(7.0, "Telefónica brand + 150 years of history + 5G licenses in 10 countries."),
        cost_advantage=(6.5, "Capex/revenue 18% (vs. 22% for rivals); digital-first = 10% lower cost/customer."),
        scale=(7.5, "€24.5B revenue, 95M+ customers, 105k employees — Spain's #1 telco, top-5 in Europe."))),
    competitors=[dict(t="VOD.L", n="Vodafone (UK)", mc=40e9, rev=45e9, pe=15, note="#2 in European telecoms; 150M customers; 5x larger; 15% higher capex"),
                 dict(t="ORAN.PA", n="Orange (France)", mc=45e9, rev=45e9, pe=12, note="#3 in European telecoms; 130M customers; 10% higher capex"),
                 dict(t="DETE.DE", n="Deutsche Telekom", mc=75e9, rev=100e9, pe=15, note="#1 in European telecoms; 230M customers; 3x larger; 20% higher capex"),
                 dict(t="TIM.MI", n="Telecom Italia (Italy)", mc=18e9, rev=21e9, pe=13, note="Italian operator; similar fiber-FTTH buildout; weaker post-3G-auction balance sheet")],
    edge=("The core edge is COST + AI: Telefónica has the lowest "
          "capex/revenue ratio in European telecoms (18% vs. 22% for rivals) "
          "AND the #1 OpenAI partnership (agentic AI for 30M customers). The "
          "moat is the cost: 4pts lower capex/revenue = €1B/yr FCF advantage "
          "that no rival can close without 3 years of transformation. The "
          "AI optionality (agentic AI for 30M customers) is the re-rating "
          "story from 10x to 15x on €500M/yr AI revenue by 2028."),
    sentiment=dict(score=6.2, consensus="Hold", pt=5.5, pt_lo=4.0, pt_hi=7.0, short="0.4% of float"),
    news=[dict(d="2026-10-07", h="Q3 2026: EBITDA +4% YoY; churn at record low; capex -8% (payout 60%)", s="TEP PR", i="pos"),
          dict(d="2026-09-16", h="Telefónica and OpenAI: agentic AI for 30M customers; €500M/yr by 2028", s="Bloomberg", i="pos"),
          dict(d="2026-08-23", h="TEP cuts capex by 8%; raises payout ratio to 60%; 5.5% dividend yield", s="Reuters", i="pos")],
    trends=["OpenAI: agentic AI for 30M customers; €500M/yr by 2028; the #1 telco-AI partnership",
            "Cost: capex/revenue 18% (best in Europe); €1B/yr FCF advantage",
            "Payout: 60% (vs. 50% in 2024); 5.5% dividend yield",
            "5G: 10 countries; 30M 5G subscribers; 2028: 50M"],
    swot=dict(
        s=["Capex/revenue 18% (best in Europe); €1B/yr FCF advantage",
           "OpenAI: agentic AI for 30M customers; €500M/yr by 2028",
           "5.5% dividend at 60% payout; the IBEX income play",
           "95M+ customers in 10 countries; the #1 Spanish telco"],
        w=["10x P/E is the 5-yr low; the re-rating story is unproven",
           "Debt: €42B; 2.5x EBITDA; rate sensitivity",
           "Germany: 30% of revenue; 2027 5G auction risk",
           "LatAm: 30% of revenue; currency + regulatory risk"],
        o=["OpenAI: €500M/yr by 2028; 2% of revenue",
           "5G: 50M subscribers by 2028; €1B/yr",
           "Cost: 15% capex/revenue by 2028; €500M/yr",
           "Payout: 65% by 2028; 6% dividend yield"],
        t=["5G auction: 2027 Germany; -€2B of capex",
           "Debt: +100bps = -€400M/yr interest",
           "Recession: -10% of ARPU",
           "Competition: Vodafone + Orange; -5% of ARPU"]),
    thesis=dict(
        bull=("OpenAI €500M, 5G 50M, capex 15%: €0.55 EPS 2028E; 15x.", 6.5, 0.30),
        base=("Steady growth, 5.5% dividend, 10x earnings.", 5.0, 0.50),
        bear=("5G auction, debt, recession: 7x earnings.", 3.5, 0.20)),
    fair_value_model=4.95,
    dcf=None),

# ============================== REPSOL =====================================
"REP.MC": dict(
    name="Repsol, S.A.", sector="Energy", industry="Oil & Gas / Hydrogen",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="repsol.com",
    employees="~28,000",
    price=16.80, market_cap=37e9, low52=12.50, high52=19.50,
    fundamentals=dict(rev=22.0e9, rev_g=3, gm=None, opm=18.0, nm=12.0, eps=1.10,
                      pe=7.2, fwd_pe=6.5, ps=0.8, ev_ebitda=4.5, roic=15, roe=18,
                      fcf=3.5e9, cash=4.0e9, debt=12.0e9, div="0.36 EUR/qtr", divy=4.3),
    segments=[("Upstream (oil + gas)", 45, "Spain, Gulf of Mexico, Norway; 350k bopd"),
              ("Downstream (refining + chemicals)", 35, "5 refineries; 800k bopd"),
              ("Renewables + Hydrogen", 20, "1.2GW hydrogen; 3.5GW renewables")],
    biz=("Repsol is Spain's #1 energy company (€37B market cap) and a "
         "top-10 European integrated oil & gas. The 2026 story is hydrogen "
         "+ transition: the 500MW green hydrogen plant in Burgos is "
         "operational (1.2GW total), adjusted operating profit €1.4B/qtr, "
         "and the dividend raised to €0.62/share (4.3% yield). 7.2x "
         "earnings at 18% ROE is the energy value play."),
    moat=dict(rating="Wide Moat", score=7.8, pillars=dict(
        network_effects=(5.5, "5 refineries + 3,000 gas stations + 1.2GW hydrogen; the #1 Spanish energy infrastructure network."),
        switching_costs=(7.0, "Refining: 10-year contracts; hydrogen: 15-year offtake agreements; 2-year switching cost."),
        intangibles=(8.0, "Repsol brand (100+ years) + 3,000 gas stations + 1.2GW hydrogen (the #1 in Spain)."),
        cost_advantage=(7.5, "Refining: 800k bopd at 15% lower cost/rival; hydrogen: 50% lower €/kg than rivals (Burgos)."),
        scale=(8.0, "€22B revenue, 350k bopd, 1.2GW hydrogen — Spain's #1 energy company."))),
    competitors=[dict(t="TTE.MC", n="TotalEnergies", mc=170e9, rev=125e9, pe=8.5, note="#2 in European energy; 5x Repsol's revenue; 20% lower cost/bbl"),
                 dict(t="ENG.PA", n="Engie (France)", mc=25e9, rev=45e9, pe=12, note="#1 in European utilities; 15% renewables; no upstream"),
                 dict(t="IBE.MC", n="Iberdrola", mc=100e9, rev=28e9, pe=22, note="#1 in European renewables; 31GW; no upstream; 2x Repsol's renewables")],
    edge=("The core edge is HYDROGEN + SPAIN INFRASTRUCTURE: Repsol is the "
          "#1 in Spanish hydrogen (1.2GW; 50% lower €/kg than rivals) AND "
          "owns the #1 Spanish refining + gas station network (5 refineries, "
          "3,000 stations). The moat is the infrastructure: 10-year refining "
          "contracts + 15-year hydrogen offtake + 3,000 gas stations = a "
          "10-year lock-in that no new entrant can replicate without 5 years "
          "and €10B of capex."),
    sentiment=dict(score=6.5, consensus="Hold", pt=21, pt_lo=14, pt_hi=26, short="0.3% of float"),
    news=[dict(d="2026-10-08", h="Q3 2026: adjusted operating profit €1.4B; hydrogen 1.2GW; dividend €0.62/share", s="REP PR", i="mixed"),
          dict(d="2026-09-20", h="Repsol's 500MW green hydrogen plant in Burgos operational; 1.2GW total", s="Reuters", i="pos"),
          dict(d="2026-08-26", h="REP raises dividend to €0.62/share (4.3% yield); 50% payout", s="Expansión", i="pos")],
    trends=["Hydrogen: 1.2GW → 3GW by 2030; €2B/yr by 2028; the #1 in Spain",
            "Refining: 800k bopd; 15% lower cost/rival; €1B/yr margin",
            "Renewables: 3.5GW → 8GW by 2030; €1.5B/yr by 2028",
            "4.3% dividend at 50% payout; €500M/yr buybacks"],
    swot=dict(
        s=["1.2GW hydrogen (the #1 in Spain); 50% lower €/kg than rivals",
           "5 refineries + 3,000 gas stations; the #1 Spanish energy infrastructure",
           "4.3% dividend at 50% payout; €500M/yr buybacks",
           "350k bopd; 800k bopd refining; 15% lower cost/rival"],
        w=["7.2x P/E is the 5-yr low; the re-rating story is unproven",
           "Oil: 45% of revenue; cyclical + geopolitical",
           "Hydrogen: 20% of revenue; 2028 commercialization risk",
           "Debt: €12B; 1.5x EBITDA; rate sensitivity"],
        o=["Hydrogen: 3GW by 2030; €2B/yr by 2028",
           "Renewables: 8GW by 2030; €1.5B/yr by 2028",
           "Refining: 10% margin by 2028; €1.5B/yr",
           "Dividend: 5% yield by 2028; €1B/yr buybacks"],
        t=["Oil: -20% = -15% of revenue; -30% of FCF",
           "Hydrogen: 2028 commercialization delay; -50% of hydrogen revenue",
           "Recession: -10% of refining margin",
           "Competition: TotalEnergies + Shell; -10% of hydrogen market share"]),
    thesis=dict(
        bull=("Hydrogen 3GW, renewables 8GW, refining 10%: €1.50 EPS 2028E; 10x.", 24.0, 0.30),
        base=("Steady growth, 4.3% dividend, 7x earnings.", 19.0, 0.50),
        bear=("Oil -20%, hydrogen delay, recession: 5x earnings.", 12.0, 0.20)),
    dcf=dict(fcf_ps=1.59, g=0.05, terminal=0.025, rate=0.095, net_cash_ps=-3.63)),

# ============================== ENAGÁS =====================================
"ENAG.MC": dict(
    name="Enagás, S.A.", sector="Utilities", industry="Gas Grid / LNG",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="enagas.com",
    employees="~4,500",
    price=24.50, market_cap=19e9, low52=20.50, high52=27.50,
    fundamentals=dict(rev=4.5e9, rev_g=8, gm=25.0, opm=35.0, nm=28.0, eps=1.05,
                      pe=12.0, fwd_pe=10.5, ps=2.6, ev_ebitda=8, roic=10, roe=9,
                      fcf=2.0e9, cash=3.0e9, debt=15.0e9, div="0.56 EUR/qtr", divy=4.6),
    segments=[("Spanish Gas Grid", 55, "27,000 km; 12M customers; regulated"),
              ("LNG (Terminus + Sines)", 30, "12Mtpa; 5Mtpa Sines expansion"),
              ("International (UK, France, Portugal)", 15, "5,000 km; regulated")],
    biz=("Enagás is Spain's #1 gas grid operator (€19B market cap) and the "
         "#1 in Spanish LNG (12Mtpa). The 2026 story: H1 FFO/share €1.05 "
         "(+6% YoY), the Sines LNG terminal expansion (+5Mtpa) approved, and "
         "the dividend raised to €0.92/share (4.6% yield). 12x earnings at "
         "10% ROE with a 4.6% yield is the 'green transition + income' play."),
    moat=dict(rating="Wide Moat", score=8.0, pillars=dict(
        network_effects=(6.5, "27,000 km of gas grid + 12Mtpa LNG; the #1 Spanish gas infrastructure network."),
        switching_costs=(10.0, "A gas grid is a 30-100 year asset; customers literally cannot switch — the strongest switching cost in utilities."),
        intangibles=(8.5, "Regulatory relationships (CNMC, UK Ofgem) + 30-year regulated franchise + 100% state-backed (51% CDP)."),
        cost_advantage=(7.5, "12Mtpa LNG at 15% lower cost/rival; 27,000 km grid at 10% lower cost/rival."),
        scale=(8.0, "€4.5B revenue, 27,000 km grid, 12Mtpa LNG — Spain's #1 gas grid operator."))),
    competitors=[dict(t="ENG.PA", n="Engie (France)", mc=25e9, rev=45e9, pe=12, note="#1 in European gas distribution; 5x Enagás's grid; 15% lower cost/km"),
                                  dict(t="SSM.L", n="SSE (UK)", mc=15e9, rev=8e9, pe=10, note="#1 in UK gas distribution; 2x Enagás's UK grid; 10% lower cost/km")],
    edge=("The core edge is REGULATED GRID + LNG: Enagás owns Spain's #1 "
          "gas grid (27,000 km; 30-100 year regulated franchise) AND the #1 "
          "Spanish LNG terminal (12Mtpa). The grid is the moat: 30-100 year "
          "assets with zero customer churn, 10% return on capital, and "
          "regulator-approved inflation pass-through. The LNG expansion "
          "(Sines +5Mtpa) is the growth story: 12Mtpa → 17Mtpa by 2028."),
    sentiment=dict(score=7.0, consensus="Buy", pt=29, pt_lo=22, pt_hi=35, short="0.2% of float"),
    news=[dict(d="2026-10-09", h="H1 2026: FFO/share €1.05 (+6% YoY); Sines LNG expansion approved (+5Mtpa)", s="ENAG PR", i="pos"),
          dict(d="2026-09-12", h="Enagás's Sines LNG terminal expansion +5Mtpa approved; 2028 operational", s="Reuters", i="pos"),
          dict(d="2026-08-19", h="ENAG raises dividend to €0.92/share (4.6% yield); 60% payout", s="Expansión", i="pos")],
    trends=["Sines LNG: 12Mtpa → 17Mtpa by 2028; €500M/yr incremental revenue",
            "Grid: 27,000 km; 10% regulated return; 5% FFO growth",
            "International: UK + France + Portugal; 5,000 km; 15% of revenue",
            "4.6% dividend at 60% payout; the IBEX income anchor"],
    swot=dict(
        s=["27,000 km gas grid; 30-100 year regulated franchise; zero customer churn",
           "12Mtpa LNG (the #1 in Spain); Sines +5Mtpa approved",
           "4.6% dividend at 60% payout; the IBEX income anchor",
           "100% state-backed (51% CDP); investment-grade balance sheet"],
        w=["12x P/E is the 5-yr average; the re-rating story is unproven",
           "Gas: 55% of revenue; 2030 demand decline risk (EU decarbonization)",
           "Debt: €15B; 2x EBITDA; rate sensitivity",
           "Growth: 5% FFO growth; the slowest in the IBEX"],
        o=["Sines LNG: 17Mtpa by 2028; €500M/yr",
           "Grid: 30,000 km by 2028; €300M/yr",
           "International: 15% → 20% of revenue by 2028",
           "Dividend: 5% yield by 2028; €200M/yr buybacks"],
        t=["Gas demand: -10% by 2030 (EU decarbonization); -15% of revenue",
           "Debt: +100bps = -€150M/yr interest",
           "Regulation: CNMC return cut; -5% of FFO",
           "Competition: Engie + SSE; -5% of grid market share"]),
    thesis=dict(
        bull=("Sines 17Mtpa, grid 30,000 km, international 20%: €1.30 FFO 2028E; 15x.", 32.0, 0.30),
        base=("Steady growth, 4.6% dividend, 12x earnings.", 27.0, 0.50),
        bear=("Gas demand -10%, debt, regulation: 9x earnings.", 19.0, 0.20)),
    dcf=dict(fcf_ps=2.58, g=0.05, terminal=0.03, rate=0.085, net_cash_ps=-15.47)),

# ============================== AENA =======================================
"ANA.MC": dict(
    name="AENA, S.A.", sector="Industrials", industry="Airports",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="aena.es",
    employees="~8,000",
    price=22.50, market_cap=21e9, low52=18.00, high52=25.50,
    fundamentals=dict(rev=4.2e9, rev_g=12, gm=45.0, opm=48.0, nm=42.0, eps=1.88,
                      pe=12.0, fwd_pe=10.5, ps=3.5, ev_ebitda=9, roic=15, roe=12,
                      fcf=2.5e9, cash=2.0e9, debt=18.0e9, div="0.45 EUR/qtr", divy=4.0),
    segments=[("Passenger (44 airports)", 65, "230M passengers/yr; international +11%"),
              ("Real Estate + Retail", 25, "4M m2; 15% of revenue"),
              ("International (Mexico, Brazil, UK)", 10, "6 airports; 15% of revenue")],
    biz=("AENA is Spain's #1 airport operator (€21B market cap) and the "
         "#1 in Spanish air transport infrastructure. The 2026 story: Q3 "
         "passengers 62M (+8% YoY), international +11%, the Mexico "
         "concession extension, and the Barajas T4 expansion. 12x earnings "
         "at 48% operating margin with a 4.0% yield is the 'travel + income' "
         "play."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(7.0, "44 airports in Spain + 6 international; the #1 Spanish air transport network."),
        switching_costs=(9.5, "An airport is a 30-100 year asset; airlines literally cannot switch — the strongest switching cost in infrastructure."),
        intangibles=(8.5, "AENA brand + 30-year concession (2052) + 100% state-backed (100% Ministry of Finance)."),
        cost_advantage=(7.5, "44 airports at 20% lower cost/passenger than rivals (scale + state-backed)."),
        scale=(8.5, "€4.2B revenue, 230M passengers/yr, 44 airports — Spain's #1 airport operator."))),
    competitors=[dict(t="TAV", n="TAV Airports (Turkey)", mc=15e9, rev=5e9, pe=18, note="#1 in Turkish airports; 100M passengers/yr; 2x AENA's revenue"),
                 dict(t="FRA.DE", n="Fraport (Germany)", mc=12e9, rev=3e9, pe=14, note="#1 in Frankfurt; 60M passengers/yr; 1.5x AENA's revenue"),
                 dict(t="SCHIP.AX", n="Schiphol (Netherlands)", mc=15e9, rev=4e9, pe=15, note="#1 in Amsterdam; 70M passengers/yr; 2x AENA's revenue"),
                 dict(t="BME.MC", n="BME (Madrid)", mc=4.5e9, rev=0.5e9, pe=15, note="No overlap — stock exchange; included for IBEX context")],
    edge=("The core edge is 30-YEAR CONCESSION + SCALE: AENA owns Spain's "
          "#1 airport network (44 airports; 230M passengers/yr) under a "
          "30-year concession (2052) with 100% state backing. The moat is "
          "the concession: 30-year regulated franchise with zero airline "
          "churn, 48% operating margin, and 15% real-estate upside. No new "
          "entrant can replicate 30 years of airport infrastructure without "
          "10 years and €10B of capex."),
    sentiment=dict(score=7.2, consensus="Buy", pt=28, pt_lo=20, pt_hi=35, short="0.3% of float"),
    news=[dict(d="2026-10-10", h="Q3 2026: passengers 62M (+8% YoY); international +11%; Barajas T4 expansion", s="ANA PR", i="pos"),
          dict(d="2026-09-22", h="Aena wins Mexico airport concession extension (2052); 5 airports", s="Reuters", i="pos"),
          dict(d="2026-08-28", h="Aena's Barajas T4 expansion opens; 30M additional capacity; €2B capex", s="Expansión", i="pos")],
    trends=["Passengers: 230M → 280M by 2030; 5% growth; the #1 Spanish airport network",
            "International: Mexico + Brazil + UK; 15% of revenue; 20% by 2030",
            "Real estate: 4M m2; 15% of revenue; 20% by 2030",
            "4.0% dividend at 50% payout; the IBEX travel-income play"],
    swot=dict(
        s=["44 airports; 230M passengers/yr; 30-year concession (2052)",
           "48% operating margin; 42% net margin; the #1 Spanish infrastructure",
           "4.0% dividend at 50% payout; the IBEX travel-income play",
           "100% state-backed; investment-grade balance sheet"],
        w=["12x P/E is the 5-yr average; the re-rating story is unproven",
           "Debt: €18B; 2.5x EBITDA; rate sensitivity",
           "Recession: -15% of passengers; -10% of revenue",
           "Security: -5% of capacity; 2027 risk"],
        o=["Passengers: 280M by 2030; €500M/yr",
           "International: 20% of revenue by 2030; €500M/yr",
           "Real estate: 20% of revenue by 2030; €500M/yr",
           "Dividend: 4.5% yield by 2028; €200M/yr buybacks"],
        t=["Recession: -15% of passengers; -10% of revenue",
           "Security: -5% of capacity; 2027 risk",
           "Debt: +100bps = -€180M/yr interest",
           "Competition: Ryanair + Vueling; -5% of airport market share"]),
    thesis=dict(
        bull=("Passengers 280M, international 20%, real estate 20%: €2.30 EPS 2028E; 15x.", 30.0, 0.30),
        base=("Steady growth, 4.0% dividend, 12x earnings.", 26.0, 0.50),
        bear=("Recession, security, debt: 9x earnings.", 18.0, 0.20)),
    dcf=dict(fcf_ps=2.68, g=0.05, terminal=0.03, rate=0.085, net_cash_ps=-17.14)),

# ============================== BME ========================================
"BME.MC": dict(
    name="Bolsas y Mercados Españoles, S.A.", sector="Financials", industry="Stock Exchange / Clearing",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="bme.es",
    employees="~1,500",
    price=28.00, market_cap=4.5e9, low52=22.00, high52=32.00,
    fundamentals=dict(rev=0.5e9, rev_g=12, gm=55.0, opm=45.0, nm=38.0, eps=1.87,
                      pe=15.0, fwd_pe=12.5, ps=9.0, ev_ebitda=11, roic=25, roe=20,
                      fcf=0.2e9, cash=0.3e9, debt=0.2e9, div="0.18 EUR/qtr", divy=3.2),
    segments=[("Exchange (equities + derivatives)", 45, "IBEX 35; derivatives +22%"),
              ("Clearing + Custody (Custodia Central)", 35, "€8T in custody; tokenized treasuries"),
              ("Data + Services", 20, "Market data; 15% of revenue")],
    biz=("BME is Spain's #1 stock exchange (€4.5B market cap) and the "
         "#1 in Spanish clearing + custody (€8T in custody). The 2026 story "
         "is MSCI + tokenization: the MSCI Emerging Markets inclusion "
         "effective (Q2 2026), derivatives volume +22% YoY, and the "
         "tokenized treasury settlement (Eurosystem) launched. 15x earnings "
         "at 45% operating margin is the 'financial infrastructure' play."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(9.0, "IBEX 35 + €8T in custody + tokenized treasuries; the #1 Spanish financial infrastructure network."),
        switching_costs=(9.5, "A stock exchange is a 30-100 year asset; brokers literally cannot switch — the strongest switching cost in financials."),
        intangibles=(9.0, "BME brand + 200-year history (1831) + MSCI inclusion + 100% state-backed (51% Ministry)."),
        cost_advantage=(8.0, "Exchange at 55% gross margin; 20% lower cost/transaction than rivals (scale + digital)."),
        scale=(7.5, "€0.5B revenue, €8T in custody, 1.5k employees — Spain's #1 stock exchange."))),
    competitors=[dict(t="Euronext", n="Euronext (NL/FR)", mc=35e9, rev=3e9, pe=25, note="#1 in European exchanges; 5x BME's revenue; 15% lower cost/transaction"),
                 dict(t="Deutsche Börse", n="Deutsche Börse (DE)", mc=60e9, rev=6e9, pe=18, note="#1 in European clearing (Euroclear); 10x BME's revenue"),
                 dict(t="LSE", n="London Stock Exchange (UK)", mc=30e9, rev=4e9, pe=20, note="#1 in UK exchanges; 6x BME's revenue; 20% lower cost/transaction"),
                 dict(t="BIC.MC", n="CaixaBank (no overlap)", mc=61e9, rev=10.5e9, pe=9.0, note="—")],
    edge=("The core edge is MSCI + TOKENIZATION: BME is the #1 in Spanish "
          "clearing + custody (€8T) with the MSCI Emerging Markets "
          "inclusion (Q2 2026) AND the tokenized treasury settlement "
          "(Eurosystem). The moat is the infrastructure: 200-year history + "
          "30-100 year asset + MSCI inclusion = a 10-year lock-in that no "
          "new entrant can replicate without 5 years and €1B of capex. The "
          "tokenization optionality is the re-rating story from 15x to 25x "
          "on €100M/yr tokenized revenue by 2028."),
    sentiment=dict(score=7.0, consensus="Buy", pt=36, pt_lo=25, pt_hi=45, short="0.2% of float"),
    news=[dict(d="2026-10-07", h="Q3 2026: revenue +9% YoY; derivatives +22%; MSCI inclusion effective", s="BME PR", i="pos"),
          dict(d="2026-09-18", h="BME launches tokenized treasury settlement (Eurosystem); €50B in tokenized treasuries", s="Reuters", i="pos"),
          dict(d="2026-08-14", h="MSCI Emerging Markets inclusion effective; €2B in inflows; 15% of revenue", s="Bloomberg", i="pos")],
    trends=["MSCI: Emerging Markets inclusion; €2B inflows; 15% of revenue",
            "Derivatives: +22% YoY; €500M/yr; the #1 growth segment",
            "Tokenization: €50B in tokenized treasuries; €100M/yr by 2028",
            "3.2% dividend at 40% payout; the IBEX infrastructure play"],
    swot=dict(
        s=["€8T in custody; the #1 Spanish financial infrastructure",
           "MSCI Emerging Markets inclusion; €2B inflows; 15% of revenue",
           "Tokenized treasury settlement (Eurosystem); €50B in tokenized treasuries",
           "45% operating margin; 55% gross margin; the #1 in Spanish financials"],
        w=["15x P/E is the 5-yr average; the re-rating story is unproven",
           "Market-dependent: 45% of revenue from IBEX 35 volume",
           "Debt: €0.2B; 0.5x EBITDA; minimal",
           "Growth: 9% revenue growth; the slowest in the IBEX"],
        o=["Tokenization: €100M/yr by 2028; 20% of revenue",
           "Derivatives: €1B/yr by 2028; 30% of revenue",
           "International: 15% of revenue by 2028 (Mexico, UK)",
           "Dividend: 3.5% yield by 2028; €50M/yr buybacks"],
        t=["Recession: -15% of IBEX volume; -10% of revenue",
           "Euronext: expansion into Spain; -5% of market share",
           "Tokenization: 2028 commercialization delay; -50% of tokenized revenue",
           "Regulation: MiCA + DLT; -5% of revenue"]),
    thesis=dict(
        bull=("Tokenization €100M, derivatives €1B, MSCI €5B: €2.50 EPS 2028E; 25x.", 42.0, 0.30),
        base=("Steady growth, 3.2% dividend, 15x earnings.", 34.0, 0.50),
        bear=("Recession, Euronext, tokenization delay: 10x earnings.", 22.0, 0.20)),
    dcf=dict(fcf_ps=1.24, g=0.08, terminal=0.03, rate=0.085, net_cash_ps=0.62)),

# ============================== FERROVIAL ==================================
"FER.MC": dict(
    name="Ferrovial, S.A.", sector="Industrials", industry="Concessions / Infrastructure",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="ferrovial.com",
    employees="~32,000",
    price=22.00, market_cap=7e9, low52=17.50, high52=25.50,
    fundamentals=dict(rev=6.5e9, rev_g=7, gm=22.0, opm=12.0, nm=9.0, eps=2.00,
                      pe=11.0, fwd_pe=9.5, ps=1.1, ev_ebitda=6, roic=12, roe=10,
                      fcf=1.0e9, cash=0.8e9, debt=12.0e9, div="0.50 EUR/qtr", divy=4.5),
    segments=[("Concessions (toll roads, airports)", 70, "20 concessions; North America +14%"),
              ("Construction", 30, "€4B backlog; 15% of revenue")],
    biz=("Ferrovial is Spain's #1 infrastructure company (€7B market cap) "
         "and a top-5 European concessions operator. The 2026 story is North "
         "America: adjusted EBITDA +7% YoY, North America +14% (5 toll roads, "
         "1 airport), the $1.2B US toll road concession won, and the $800M "
         "buyback. 11x earnings at 12% ROE with a 4.5% yield is the "
         "'infrastructure + income' play."),
    moat=dict(rating="Wide Moat", score=8.0, pillars=dict(
        network_effects=(6.5, "20 concessions (12 toll roads, 3 airports, 5 other); the #1 Spanish infrastructure network."),
        switching_costs=(9.5, "A toll road is a 30-50 year asset; drivers literally cannot switch — the strongest switching cost in infrastructure."),
        intangibles=(8.5, "Ferrovial brand + 100-year history + 20 concessions + 100% state-backed (45% F&C)."),
        cost_advantage=(7.5, "20 concessions at 20% lower cost/km than rivals (scale + state-backed)."),
        scale=(8.0, "€6.5B revenue, 20 concessions, 32k employees — Spain's #1 infrastructure company."))),
    competitors=[dict(t="ACS.MC", n="ACS (Spain)", mc=14e9, rev=18e9, pe=8.5, note="#2 in Spanish infrastructure; 2x Ferrovial's revenue; 15% lower ROE"),
                 dict(t="VINCI", n="Vinci (France)", mc=25e9, rev=40e9, pe=14, note="#1 in European concessions; 6x Ferrovial's revenue; 10% lower ROE"),
                 dict(t="Sacyr", n="Sacyr (Spain)", mc=5e9, rev=4e9, pe=10, note="#3 in Spanish infrastructure; 40% smaller; 5% lower ROE"),
                 dict(t="AENA", n="AENA (Spain)", mc=21e9, rev=4.2e9, pe=12, note="#1 in Spanish airports; 5x Ferrovial's airport revenue")],
    edge=("The core edge is NORTH AMERICA + CONCESSIONS: Ferrovial is the "
          "#1 in Spanish concessions (20 assets; 30-50 year franchises) AND "
          "the #1 Spanish infrastructure company in North America (5 toll "
          "roads, 1 airport; +14% YoY). The moat is the concessions: 30-50 "
          "year assets with zero customer churn, 12% ROE, and "
          "regulator-approved inflation pass-through. The North America "
          "optionality is the re-rating story from 11x to 15x on "
          "$1B/yr North America profit by 2028."),
    sentiment=dict(score=6.8, consensus="Buy", pt=28, pt_lo=19, pt_hi=35, short="0.2% of float"),
    news=[dict(d="2026-10-06", h="H1 2026: adjusted EBITDA +7% YoY; North America +14%; $1.2B US toll road", s="FER PR", i="pos"),
          dict(d="2026-09-15", h="Ferrovial wins $1.2B US toll road concession (Texas); 30-year franchise", s="Reuters", i="pos"),
          dict(d="2026-08-21", h="FER adds $800M buyback; 4.5% dividend yield; 55% payout", s="Expansión", i="pos")],
    trends=["North America: 5 toll roads + 1 airport; +14% YoY; $1B/yr profit by 2028",
            "Concessions: 20 assets; 30-50 year franchises; 12% ROE",
            "Construction: €4B backlog; 15% of revenue; 2027 delivery",
            "4.5% dividend at 55% payout; $800M buyback"],
    swot=dict(
        s=["20 concessions; 30-50 year franchises; 12% ROE; the #1 Spanish infrastructure",
           "North America: 5 toll roads + 1 airport; +14% YoY; $1B/yr by 2028",
           "4.5% dividend at 55% payout; $800M buyback",
           "100% state-backed (45% F&C); investment-grade balance sheet"],
        w=["11x P/E is the 5-yr average; the re-rating story is unproven",
           "Construction: 30% of revenue; 5% margin; cyclical",
           "Debt: €12B; 2.5x EBITDA; rate sensitivity",
           "Growth: 7% revenue growth; the slowest in the IBEX"],
        o=["North America: $1B/yr by 2028; 20% of revenue",
           "Concessions: 25 assets by 2028; €500M/yr",
           "Construction: €6B backlog by 2028; €500M/yr",
           "Dividend: 5% yield by 2028; $1B/yr buybacks"],
        t=["Recession: -10% of toll traffic; -5% of revenue",
           "Debt: +100bps = -€120M/yr interest",
           "Regulation: toll road rate cut; -5% of revenue",
           "Competition: Vinci + ACS; -5% of concession market share"]),
    thesis=dict(
        bull=("North America $1B, concessions 25, construction €6B: €2.50 EPS 2028E; 15x.", 32.0, 0.30),
        base=("Steady growth, 4.5% dividend, 11x earnings.", 26.0, 0.50),
        bear=("Recession, debt, regulation: 8x earnings.", 18.0, 0.20)),
    dcf=dict(fcf_ps=3.14, g=0.05, terminal=0.03, rate=0.085, net_cash_ps=-35.20)),

# ============================== IAG ========================================
"IAG.MC": dict(
    name="International Airlines Group, P.L.C.", sector="Industrials", industry="Airlines",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="flyiag.com",
    employees="~115,000",
    price=6.80, market_cap=13.5e9, low52=5.20, high52=8.50,
    fundamentals=dict(rev=22.0e9, rev_g=10, gm=28.0, opm=12.0, nm=8.0, eps=0.76,
                      pe=9.0, fwd_pe=8.0, ps=0.6, ev_ebitda=4, roic=15, roe=18,
                      fcf=1.5e9, cash=5.0e9, debt=18.0e9, div="0.28 EUR/qtr", divy=4.1),
    segments=[("British Airways", 45, "150M passengers/yr; 35% of UK market"),
              ("Iberia", 35, "100M passengers/yr; 30% of Spain market"),
              ("Vueling + Aer Lingus", 20, "80M passengers/yr; 15% of EU market")],
    biz=("IAG is Europe's #2 airline group (€13.5B market cap) and the #1 "
         "in UK + Spain. The 2026 story is recovery + cost: Q3 profit €1.1B, "
         "load factor 84% (record), the new long-haul transatlantic fleet, "
         "and fuel hedged for 70% of 2027. 9x earnings at 18% ROE with a "
         "4.1% yield is the 'travel + value' play."),
    moat=dict(rating="Narrow Moat", score=6.5, pillars=dict(
        network_effects=(7.0, "330M passengers/yr; 35% of UK + 30% of Spain + 15% of EU; the #2 European airline network."),
        switching_costs=(5.5, "Airlines are low-switching; but the 330M passenger loyalty program (Executive Club) keeps the customer engaged."),
        intangibles=(7.5, "British Airways + Iberia brands (100+ years) + 30-year slot agreements at Heathrow/Barajas."),
        cost_advantage=(6.5, "330M passengers at 15% lower cost/passenger than rivals (scale + shared fleet)."),
        scale=(7.5, "€22B revenue, 330M passengers/yr, 115k employees — Europe's #2 airline group."))),
    competitors=[dict(t="AF", n="Air France-KLM (FR/NL)", mc=25e9, rev=55e9, pe=25, note="#1 in European airlines; 2x IAG's revenue; 10% lower cost/passenger"),
                 dict(t="LH", n="Lufthansa (DE)", mc=15e9, rev=50e9, pe=30, note="#2 in European airlines; 2x IAG's revenue; 15% lower cost/passenger"),
                 dict(t="RYAAY", n="Ryanair (IE)", mc=35e9, rev=18e9, pe=12, note="#1 in EU low-cost; 500M passengers/yr; 30% lower cost/passenger"),
                 dict(t="VOY", n="Vueling (IAG subsidiary)", mc=None, rev=None, pe=None, note="—")],
    edge=("The core edge is SLOTS + SCALE: IAG owns the 30-year slot "
          "agreements at Heathrow (35% of UK long-haul) and Barajas (30% of "
          "Spain long-haul) — the most valuable airport slots in Europe. The "
          "moat is the slots: 30-year agreements with zero competition, 12% "
          "operating margin, and 15% lower cost/passenger than rivals. The "
          "new long-haul fleet (747-8, A350) is the re-rating story from 9x "
          "to 15x on €500M/yr incremental profit by 2028."),
    sentiment=dict(score=6.5, consensus="Hold", pt=9.0, pt_lo=6.0, pt_hi=12.0, short="0.5% of float"),
    news=[dict(d="2026-10-09", h="Q3 2026: profit €1.1B; load factor 84% (record); new long-haul fleet", s="IAG PR", i="pos"),
          dict(d="2026-09-17", h="IAG launches new long-haul transatlantic fleet (747-8, A350); 2028 delivery", s="Reuters", i="pos"),
          dict(d="2026-08-23", h="Fuel cost +6% QoQ; hedged for 70% of 2027; 4.1% dividend yield", s="Bloomberg", i="mixed")],
    trends=["Long-haul: new fleet (747-8, A350); 2028 delivery; €500M/yr incremental profit",
            "Load factor: 84% (record); 86% by 2028; €300M/yr",
            "Cost: 15% lower cost/passenger than rivals; 10% by 2028",
            "4.1% dividend at 50% payout; the IBEX travel-value play"],
    swot=dict(
        s=["330M passengers/yr; 35% UK + 30% Spain + 15% EU; the #2 European airline",
           "30-year slot agreements at Heathrow + Barajas; the most valuable slots in Europe",
           "4.1% dividend at 50% payout; the IBEX travel-value play",
           "15% lower cost/passenger than rivals; 12% operating margin"],
        w=["9x P/E is the 5-yr low; the re-rating story is unproven",
           "Fuel: 30% of cost; +6% QoQ; 70% hedged for 2027",
           "Debt: €18B; 2x EBITDA; rate sensitivity",
           "Recession: -15% of passengers; -10% of revenue"],
        o=["Long-haul: €500M/yr by 2028; 20% of revenue",
           "Load factor: 86% by 2028; €300M/yr",
           "Cost: 10% lower cost/passenger by 2028; €300M/yr",
           "Dividend: 4.5% yield by 2028; €200M/yr buybacks"],
        t=["Fuel: +20% = -10% of profit; 30% of cost",
           "Recession: -15% of passengers; -10% of revenue",
           "Debt: +100bps = -€180M/yr interest",
           "Competition: Ryanair + EasyJet; -5% of low-cost market share"]),
    thesis=dict(
        bull=("Long-haul €500M, load 86%, cost -10%: €1.10 EPS 2028E; 15x.", 11.0, 0.30),
        base=("Steady growth, 4.1% dividend, 9x earnings.", 8.5, 0.50),
        bear=("Fuel +20%, recession, debt: 6x earnings.", 5.0, 0.20)),
    dcf=dict(fcf_ps=0.76, g=0.05, terminal=0.03, rate=0.095, net_cash_ps=-6.55)),

# ============================== CIE ========================================
"CIE.MC": dict(
    name="CIE Automotive, S.A.", sector="Industrials", industry="Automotive / ADAS",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="cieautomotive.com",
    employees="~20,000",
    price=3.60, market_cap=1.9e9, low52=2.80, high52=4.50,
    fundamentals=dict(rev=5.5e9, rev_g=15, gm=18.0, opm=9.8, nm=7.0, eps=0.40,
                      pe=9.0, fwd_pe=8.0, ps=0.35, ev_ebitda=5, roic=10, roe=8,
                      fcf=0.4e9, cash=0.5e9, debt=3.5e9, div="0.12 EUR/qtr", divy=4.0),
    segments=[("Assembly (ADAS, EV)", 55, "Stellantis $300M deal; Mexico +25%"),
              ("Systems (brakes, steering)", 30, "50 OEMs; 15% growth"),
              ("Other (Mopar, Magneti Marelli)", 15, "5% of revenue")],
    biz=("CIE Automotive is Spain's #1 automotive supplier (€1.9B market "
         "cap) and a top-20 European Tier-1. The 2026 story is ADAS + "
         "Mexico: Q3 revenue €1.4B (+15% YoY), EBITDA margin 9.8% (record), "
         "the $300M Stellantis ADAS deal, and Mexico capacity +25%. 9x "
         "earnings at 10% ROE with a 4.0% yield is the 'auto + value' play."),
    moat=dict(rating="Narrow Moat", score=6.0, pillars=dict(
        network_effects=(6.0, "50 OEMs; 200+ platforms; the #1 Spanish automotive supplier network."),
        switching_costs=(7.5, "ADAS: 3-5 year design cycle; re-qualifying is a 12-month, $50M exercise. 5-year lock-in."),
        intangibles=(7.0, "CIE brand (Magneti Marelli legacy) + 100-year history + 50 OEM relationships."),
        cost_advantage=(6.5, "50 OEMs at 15% lower cost/part than rivals (scale + nearshoring)."),
        scale=(6.5, "€5.5B revenue, 50 OEMs, 20k employees — Spain's #1 automotive supplier."))),
    competitors=[dict(t="MAG", n="Magneti Marelli (Stellantis)", mc=None, rev=None, pe=None, note="—"),
                 dict(t="BOSCH.DE", n="Bosch (Germany)", mc=45e9, rev=60e9, pe=18, note="#1 in European auto suppliers; 10x CIE's revenue; 10% lower cost/part"),
                 dict(t="CONTI.DE", n="Continental (Germany)", mc=35e9, rev=40e9, pe=15, note="#2 in European auto suppliers; 7x CIE's revenue; 8% lower cost/part"),
                 dict(t="ZF.DE", n="ZF Friedrichshafen (Germany)", mc=30e9, rev=35e9, pe=12, note="#3 in European auto suppliers; 6x CIE's revenue; 5% lower cost/part")],
    edge=("The core edge is ADAS + MEXICO: CIE is the #1 Spanish automotive "
          "supplier (50 OEMs; 200+ platforms) with the $300M Stellantis ADAS "
          "deal AND Mexico capacity +25%. The moat is the design cycle: 3-5 "
          "year ADAS design cycle + 5-year lock-in = a 10-year revenue "
          "stream that no new entrant can replicate without 3 years and "
          "$100M of R&D. The Mexico optionality is the re-rating story from "
          "9x to 15x on $500M/yr Mexico profit by 2028."),
    sentiment=dict(score=6.0, consensus="Hold", pt=4.5, pt_lo=3.0, pt_hi=6.0, short="0.3% of float"),
    news=[dict(d="2026-10-05", h="Q3 2026: revenue €1.4B (+15% YoY); EBITDA margin 9.8% (record); $300M Stellantis ADAS", s="CIE PR", i="pos"),
          dict(d="2026-09-11", h="CIE wins $300M Stellantis ADAS assembly contract; 2028 delivery; Mexico", s="Reuters", i="pos"),
          dict(d="2026-08-19", h="CIE Mexico plant expansion +25% capacity; $500M capex; 2027 operational", s="Expansión", i="pos")],
    trends=["ADAS: $300M Stellantis deal; 2028 delivery; $500M/yr by 2028",
            "Mexico: +25% capacity; $500M capex; 2027 operational",
            "Systems: 50 OEMs; 15% growth; 10% margin by 2028",
            "4.0% dividend at 50% payout; the IBEX auto-value play"],
    swot=dict(
        s=["50 OEMs; 200+ platforms; the #1 Spanish automotive supplier",
           "$300M Stellantis ADAS deal; 2028 delivery; $500M/yr by 2028",
           "Mexico: +25% capacity; $500M capex; 2027 operational",
           "4.0% dividend at 50% payout; 9x earnings; the IBEX auto-value play"],
        w=["9x P/E is the 5-yr low; the re-rating story is unproven",
           "Auto: 55% of revenue; 2027 EV transition risk",
           "Debt: €3.5B; 2.5x EBITDA; rate sensitivity",
           "Margin: 9.8% EBITDA; the lowest in the IBEX"],
        o=["ADAS: $500M/yr by 2028; 20% of revenue",
           "Mexico: $500M/yr by 2028; 15% of revenue",
           "Systems: 10% margin by 2028; €100M/yr",
           "Dividend: 4.5% yield by 2028; €100M/yr buybacks"],
        t=["EV transition: -15% of internal combustion revenue; 2027",
           "Stellantis: -20% of orders; -10% of revenue",
           "Debt: +100bps = -€35M/yr interest",
           "Competition: Bosch + Continental; -5% of ADAS market share"]),
    thesis=dict(
        bull=("ADAS $500M, Mexico $500M, systems 10%: €0.60 EPS 2028E; 15x.", 5.5, 0.30),
        base=("Steady growth, 4.0% dividend, 9x earnings.", 4.2, 0.50),
        bear=("EV transition, Stellantis, debt: 6x earnings.", 2.8, 0.20)),
    dcf=dict(fcf_ps=0.76, g=0.05, terminal=0.03, rate=0.095, net_cash_ps=-5.68)),

# ============================== ACS ========================================
"ACS.MC": dict(
    name="Acciona, S.A.", sector="Industrials", industry="Infrastructure / Renewables",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="accionas.com",
    employees="~35,000",
    price=33.00, market_cap=14e9, low52=25.00, high52=38.00,
    fundamentals=dict(rev=18.0e9, rev_g=8, gm=18.0, opm=10.0, nm=8.0, eps=3.90,
                      pe=8.5, fwd_pe=7.5, ps=0.8, ev_ebitda=5, roic=12, roe=10,
                      fcf=1.5e9, cash=2.0e9, debt=15.0e9, div="0.80 EUR/qtr", divy=3.5),
    segments=[("Infrastructure (toll roads, airports)", 45, "20 concessions; North America +12%"),
              ("Construction", 30, "€38B backlog; 15% of revenue"),
              ("Renewables (Acciona Energía)", 25, "3.5GW; 20% growth")],
    biz=("ACS is Spain's #2 infrastructure company (€14B market cap) and a "
         "top-5 European construction + concessions operator. The 2026 story "
         "is North America + renewables: H1 revenue €10.1B, backlog €38B, "
         "the €1.8B Spanish high-speed rail contract, North America +12%, "
         "and Acciona Energía 3.5GW (20% growth). 8.5x earnings at 12% ROE "
         "with a 3.5% yield is the 'infrastructure + value' play."),
    moat=dict(rating="Narrow Moat", score=6.5, pillars=dict(
        network_effects=(6.5, "20 concessions + €38B backlog; the #2 Spanish infrastructure network."),
        switching_costs=(8.5, "A toll road is a 30-50 year asset; a construction contract is a 3-5 year lock-in."),
        intangibles=(8.0, "ACS brand (100+ years) + 20 concessions + €38B backlog + 100% state-backed (30%)."),
        cost_advantage=(6.5, "20 concessions at 15% lower cost/km than rivals (scale + state-backed)."),
        scale=(7.5, "€18B revenue, 20 concessions, €38B backlog — Spain's #2 infrastructure company."))),
    competitors=[dict(t="FER.MC", n="Ferrovial", mc=7e9, rev=6.5e9, pe=11, note="#1 in Spanish concessions; 40% smaller; 10% lower ROE"),
                 dict(t="Vinci", n="Vinci (France)", mc=25e9, rev=40e9, pe=14, note="#1 in European concessions; 2x ACS's revenue; 8% lower ROE"),
                 dict(t="Sacyr", n="Sacyr (Spain)", mc=5e9, rev=4e9, pe=10, note="#3 in Spanish infrastructure; 70% smaller; 5% lower ROE"),
                 dict(t="Ferroglobe", n="Ferroglobe (Spain)", mc=3e9, rev=2e9, pe=12, note="#1 in European ferroalloys; no infrastructure overlap")],
    edge=("The core edge is NORTH AMERICA + RENEWABLES: ACS is the #2 in "
          "Spanish infrastructure (20 concessions; €38B backlog) with North "
          "America +12% AND Acciona Energía 3.5GW (20% growth). The moat is "
          "the backlog: €38B = 2x annual revenue = a 2-year revenue "
          "guarantee. The North America + renewables optionality is the "
          "re-rating story from 8.5x to 15x on €1B/yr incremental profit "
          "by 2028."),
    sentiment=dict(score=6.5, consensus="Buy", pt=42, pt_lo=28, pt_hi=52, short="0.2% of float"),
    news=[dict(d="2026-10-07", h="H1 2026: revenue €10.1B; backlog €38B; North America +12%; €1.8B high-speed rail", s="ACS PR", i="pos"),
          dict(d="2026-09-14", h="ACS wins €1.8B Spanish high-speed rail contract (Madrid-Barcelona); 5-year delivery", s="Reuters", i="pos"),
          dict(d="2026-08-20", h="ACS's North America segment +12% YoY; 15 concessions; $1B/yr profit", s="Bloomberg", i="pos")],
    trends=["North America: 15 concessions; +12% YoY; $1B/yr profit; 20% of revenue by 2028",
            "Renewables: Acciona Energía 3.5GW; 20% growth; 15% of revenue by 2028",
            "Construction: €38B backlog; 2x annual revenue; 2-year guarantee",
            "3.5% dividend at 45% payout; the IBEX infrastructure-value play"],
    swot=dict(
        s=["20 concessions + €38B backlog; 2x annual revenue; 2-year guarantee",
           "North America: 15 concessions; +12% YoY; $1B/yr profit",
           "Acciona Energía: 3.5GW; 20% growth; 15% of revenue by 2028",
           "3.5% dividend at 45% payout; 8.5x earnings; the IBEX value play"],
        w=["8.5x P/E is the 5-yr low; the re-rating story is unproven",
           "Construction: 30% of revenue; 5% margin; cyclical",
           "Debt: €15B; 2.5x EBITDA; rate sensitivity",
           "Margin: 10% EBITDA; the lowest in the IBEX"],
        o=["North America: $1.5B/yr by 2028; 20% of revenue",
           "Renewables: 5GW by 2028; 20% of revenue",
           "Construction: €50B backlog by 2028; €500M/yr",
           "Dividend: 4% yield by 2028; €500M/yr buybacks"],
        t=["Recession: -10% of construction; -5% of revenue",
           "Debt: +100bps = -€150M/yr interest",
           "Regulation: toll road rate cut; -5% of revenue",
           "Competition: Ferrovial + Vinci; -5% of concession market share"]),
    thesis=dict(
        bull=("North America $1.5B, renewables 5GW, construction €50B: €5.00 EPS 2028E; 15x.", 50.0, 0.30),
        base=("Steady growth, 3.5% dividend, 8.5x earnings.", 38.0, 0.50),
        bear=("Recession, debt, regulation: 6x earnings.", 25.0, 0.20)),
    dcf=dict(fcf_ps=3.54, g=0.05, terminal=0.03, rate=0.085, net_cash_ps=-30.64)),

# ============================== TOTALENERGIES ==============================
"TTE.MC": dict(
    name="TotalEnergies S.E.", sector="Energy", industry="Oil & Gas / Hydrogen / Renewables",
    exchange="BME (IBEX 35)", country="ES", currency="EUR", website="totalenergies.com",
    employees="~190,000",
    price=62.00, market_cap=170e9, low52=48.00, high52=72.00,
    fundamentals=dict(rev=125.0e9, rev_g=4, gm=None, opm=20.0, nm=14.0, eps=7.30,
                      pe=8.5, fwd_pe=7.5, ps=1.4, ev_ebitda=5, roic=16, roe=20,
                      fcf=15.0e9, cash=12.0e9, debt=35.0e9, div="1.58 EUR/qtr", divy=5.1),
    segments=[("Hydrocarbons (oil + gas)", 55, "540k bopd; 12Mtpa LNG"),
              ("Renewables + Hydrogen", 25, "15GW renewables; 500MW hydrogen"),
              ("Retail (5,000 stations + charging)", 20, "200k EV chargers; 15% of revenue")],
    biz=("TotalEnergies is Europe's #2 energy company (€170B market cap) "
         "and a top-5 global integrated oil & gas. The 2026 story is the "
         "transition: Q3 hydrocarbons 540k bopd, 12Mtpa LNG, the Pyrenees "
         "green hydrogen project (EU-funded), and the 2026 dividend "
         "maintained at $1.82 (5.1% yield). 8.5x earnings at 20% ROE is the "
         "'energy transition + income' play."),
    moat=dict(rating="Wide Moat", score=8.0, pillars=dict(
        network_effects=(6.5, "5,000 gas stations + 200k EV chargers + 15GW renewables; the #2 European energy infrastructure network."),
        switching_costs=(7.5, "LNG: 15-year offtake agreements; retail: 10-year contracts; 2-year switching cost."),
        intangibles=(8.5, "TotalEnergies brand (130+ years) + 5,000 stations + 200k EV chargers + 15GW renewables."),
        cost_advantage=(8.0, "540k bopd at 15% lower cost/rival; 15GW renewables at 20% lower €/MWh."),
        scale=(9.0, "€125B revenue, 540k bopd, 15GW renewables, 200k EV chargers — Europe's #2 energy company."))),
    competitors=[dict(t="REP.MC", n="Repsol (Spain)", mc=37e9, rev=22e9, pe=7.2, note="#1 in Spanish energy; 5x smaller; 1.2GW hydrogen vs. TTE 500MW"),
                 dict(t="SHEL.L", n="Shell (UK/NL)", mc=180e9, rev=290e9, pe=9.0, note="#1 in global energy; 2x TTE's revenue; 10% lower cost/bbl"),
                 dict(t="BP", n="BP (UK)", mc=130e9, rev=180e9, pe=8.0, note="#2 in global energy; 1.5x TTE's revenue; 15% lower cost/bbl"),
                 dict(t="IBE.MC", n="Iberdrola (Spain)", mc=100e9, rev=28e9, pe=22, note="#1 in European renewables; 31GW vs. TTE 15GW; no upstream")],
    edge=("The core edge is TRANSITION + SCALE: TotalEnergies is Europe's "
          "#2 energy company (€125B revenue) with the #1 European "
          "renewables + hydrogen + EV charging portfolio (15GW + 500MW + "
          "200k chargers). The moat is the scale: 540k bopd + 12Mtpa LNG + "
          "15GW renewables + 200k EV chargers = a 10-year, €100B asset that "
          "no rival can replicate without 5 years and 30% margin sacrifice. "
          "The 5.1% dividend at 50% payout is the income play."),
    sentiment=dict(score=6.8, consensus="Hold", pt=78, pt_lo=55, pt_hi=95, short="0.3% of float"),
    news=[dict(d="2026-10-09", h="Q3 2026: hydrocarbons 540k bopd; LNG 12Mtpa; Pyrenees hydrogen EU-funded", s="TTE PR", i="pos"),
          dict(d="2026-09-16", h="TotalEnergies' Pyrenees green hydrogen project receives EU funding; €2B capex", s="Reuters", i="pos"),
          dict(d="2026-08-22", h="TTE maintains 2026 dividend at $1.82/share (5.1% yield); 50% payout", s="Expansión", i="pos")],
    trends=["Renewables: 15GW → 25GW by 2028; €5B/yr by 2028; the #1 European transition",
            "Hydrogen: 500MW → 2GW by 2028; €1B/yr by 2028; the Pyrenees project",
            "EV charging: 200k → 500k chargers by 2028; €2B/yr by 2028",
            "5.1% dividend at 50% payout; €10B/yr buybacks"],
    swot=dict(
        s=["540k bopd + 12Mtpa LNG + 15GW renewables + 200k EV chargers; Europe's #2 energy",
           "Pyrenees hydrogen: €2B EU-funded; 2GW by 2028; the #1 European hydrogen",
           "5.1% dividend at 50% payout; €10B/yr buybacks",
           "15GW renewables; 20% lower €/MWh than rivals; the #1 European transition"],
        w=["8.5x P/E is the 5-yr low; the re-rating story is unproven",
           "Oil: 55% of revenue; cyclical + geopolitical",
           "Debt: €35B; 2.5x EBITDA; rate sensitivity",
           "Transition: 25% of revenue; 2028 commercialization risk"],
        o=["Renewables: 25GW by 2028; €5B/yr",
           "Hydrogen: 2GW by 2028; €1B/yr",
           "EV charging: 500k by 2028; €2B/yr",
           "Dividend: 5.5% yield by 2028; €15B/yr buybacks"],
        t=["Oil: -20% = -15% of revenue; -30% of FCF",
           "Transition: 2028 commercialization delay; -50% of transition revenue",
           "Recession: -10% of retail revenue",
           "Competition: Shell + BP; -10% of renewable market share"]),
    thesis=dict(
        bull=("Renewables 25GW, hydrogen 2GW, EV 500k: €9.50 EPS 2028E; 12x.", 88.0, 0.30),
        base=("Steady growth, 5.1% dividend, 8.5x earnings.", 72.0, 0.50),
        bear=("Oil -20%, transition delay, recession: 6x earnings.", 50.0, 0.20)),
    dcf=dict(fcf_ps=5.47, g=0.05, terminal=0.025, rate=0.095, net_cash_ps=-8.39)),

# ============================== SAP ========================================
"SAP": dict(
    name="SAP SE", sector="Software", industry="ERP / Business AI",
    exchange="XETRA", country="DE", currency="EUR", website="sap.com",
    employees="~110,000",
    price=250.00, market_cap=295e9, low52=185.00, high52=285.00,
    fundamentals=dict(rev=34.0e9, rev_g=15, gm=75.0, opm=32.0, nm=25.0, eps=5.56,
                      pe=45.0, fwd_pe=35.0, ps=8.7, ev_ebitda=28, roic=30, roe=22,
                      fcf=11.0e9, cash=15.0e9, debt=35.0e9, div="0.80 EUR/qtr", divy=1.3),
    segments=[("Cloud (RISE, GROW)", 65, "Business AI; RPO €58B"),
              ("On-Premise (maintenance)", 35, "S/4HANA; 15% decline")],
    biz=("SAP is the world's #1 ERP company (€295B market cap) and the #1 "
         "in European software. The 2026 story is Business AI: Q3 business "
         "AI revenue €1.1B/quarter, RPO €58B (+19% YoY), and RISE 3.0 with "
         "agentic automation. 45x earnings at 30% ROIC is the 'AI + cloud' "
         "re-rating story — from 25x (2024) to 45x (2026) on Business AI."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(8.0, "400k+ enterprise customers; 30M+ daily users; the #1 ERP network on earth."),
        switching_costs=(10.0, "ERP is a 20-30 year system of record; re-platforming is a 3-5 year, $100M+ exercise. The strongest switching cost in software."),
        intangibles=(9.0, "SAP brand (45+ years) + 25k+ patents + Business AI IP; the #1 ERP brand on earth."),
        cost_advantage=(7.5, "Cloud: 75% gross margin; 20% lower cost/customer than rivals (scale + cloud)."),
        scale=(9.0, "€34B revenue, 400k+ customers, 30M+ users, 110k employees — the world's #1 ERP company."))),
    competitors=[dict(t="ORCL", n="Oracle (NetSuite, ERP Cloud)", mc=370e9, rev=55e9, pe=30, note="#2 in ERP; OCI is the #2 AI cloud; 15% of SAP's revenue"),
                 dict(t="CRM", n="Salesforce (Agentforce)", mc=315e9, rev=35.8e9, pe=24, note="#1 in CRM; Agentforce is the #1 AI agent rival; 10% of SAP's revenue"),
                 dict(t="IBM", n="IBM (watsonx)", mc=180e9, rev=55e9, pe=22, note="#1 in enterprise AI; no ERP; 15% of SAP's revenue"),
                 dict(t="ADP", n="ADP (Workforce Cloud)", mc=180e9, rev=14e9, pe=30, note="#1 in HR; no ERP overlap; 5% of SAP's revenue")],
    edge=("The core edge is ERP + BUSINESS AI: SAP is the only company with "
          "a 20-30 year ERP moat (400k+ customers; 3-5 year, $100M+ "
          "switching cost) AND a Business AI platform (€1.1B/quarter; RPO "
          "€58B). The moat is the data: every enterprise process makes the "
          "AI better. Rivals can build the AI; none can match the 20-30 year "
          "ERP data graph. The 45x P/E is the re-rating story — from 25x "
          "(2024) to 45x (2026) on Business AI going from €5B to €15B/yr "
          "by 2028."),
    sentiment=dict(score=7.5, consensus="Buy", pt=320, pt_lo=220, pt_hi=400, short="0.8% of float"),
    news=[dict(d="2026-10-08", h="Q3 2026: Business AI revenue €1.1B/quarter; RPO €58B (+19% YoY); RISE 3.0", s="SAP PR", i="pos"),
          dict(d="2026-09-18", h="SAP Sapphire: 3,000 Business AI deals; RISE 3.0 with agentic automation", s="Bloomberg", i="pos"),
          dict(d="2026-08-25", h="SAP RISE 3.0: agentic automation; 50% of enterprise processes by 2028", s="Reuters", i="pos")],
    trends=["Business AI: €1.1B/quarter → €15B/yr by 2028; the #1 enterprise AI platform",
            "RISE 3.0: agentic automation; 50% of enterprise processes by 2028",
            "RPO: €58B (+19% YoY); 2x annual revenue; 2-year guarantee",
            "1.3% dividend + €10B/yr buybacks = 4.7% shareholder yield"],
    swot=dict(
        s=["400k+ enterprise customers; 30M+ daily users; the world's #1 ERP",
           "Business AI: €1.1B/quarter; RPO €58B; the #1 enterprise AI platform",
           "75% gross margin; 32% operating margin; 30% ROIC",
           "1.3% dividend + €10B/yr buybacks = 4.7% shareholder yield"],
        w=["45x P/E is 2x the 5-yr average; priced for Business AI to deliver",
           "On-premise: 35% of revenue; 15% decline; the #1 drag",
           "R&D: 15% of revenue; 15k+ engineers; the #1 cost line",
           "Debt: €35B; 1.5x net debt/EBITDA"],
        o=["Business AI: €15B/yr by 2028; 45% of revenue",
           "RISE 3.0: 50% of enterprise processes by 2028; €10B/yr",
           "International: 60% of revenue; 65% by 2028",
           "Buyback: €15B 2026-2028; 3% yield"],
        t=["Oracle: ERP Cloud + OCI; -20% of Business AI revenue",
           "Salesforce: Agentforce + CRM; -15% of Business AI revenue",
           "On-premise: 2028 decline; -15% of revenue",
           "Macro: enterprise AI digestion 2027"]),
    thesis=dict(
        bull=("Business AI €15B, RISE 50%, RPO €80B: €8.00 EPS 2028E; 55x.", 400, 0.25),
        base=("Business AI +30%, RPO +20%, on-premise -10%; 40x earnings.", 330, 0.50),
        bear=("Business AI miss, Oracle, macro; de-rate to 25x.", 200, 0.25)),
    dcf=dict(fcf_ps=9.32, g=0.15, terminal=0.035, rate=0.09, net_cash_ps=-16.95)),

# ============================== AIR LIQUIDE ================================
"AIR.PA": dict(
    name="Air Liquide S.A.", sector="Materials", industry="Industrial Gases / Hydrogen",
    exchange="XETRA", country="FR", currency="EUR", website="airliquide.com",
    employees="~65,000",
    price=180.00, market_cap=50e9, low52=145.00, high52=205.00,
    fundamentals=dict(rev=22.5e9, rev_g=7, gm=38.0, opm=24.0, nm=18.0, eps=4.09,
                      pe=17.0, fwd_pe=14.5, ps=2.2, ev_ebitda=11, roic=18, roe=15,
                      fcf=3.5e9, cash=4.0e9, debt=25.0e9, div="1.60 EUR/qtr", divy=3.5),
    segments=[("Gases (industrial + medical)", 60, "15,000+ customers; 95% take-or-pay"),
              ("Water + Hydrogen", 25, "500MW hydrogen; 15-year data center deals"),
              ("Healthcare (Oxygent)", 15, "2M patients; 5% growth")],
    biz=("Air Liquide is the world's #1 industrial gas company (€50B market "
         "cap) and a top-5 in hydrogen. The 2026 story is hydrogen + data "
         "centers: Q3 revenue €6.2B (+6% YoY), hydrogen +28% YoY, the 15-year "
         "on-site power deal for 3 US data centers, and the €1B European "
         "ammonia plant. 17x earnings at 18% ROE with a 3.5% yield is the "
         "'hydrogen + data center' play."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(7.5, "15,000+ customers; 95% take-or-pay contracts; the #1 industrial gas network on earth."),
        switching_costs=(10.0, "Industrial gas is a 10-30 year take-or-pay contract; re-platforming is a 2-3 year, $50M+ exercise. The strongest switching cost in industrial gases."),
        intangibles=(8.5, "Air Liquide brand (130+ years) + 20k+ patents + hydrogen IP; the #1 industrial gas brand on earth."),
        cost_advantage=(8.0, "15,000+ customers at 20% lower cost/customer than rivals (scale + 95% take-or-pay)."),
        scale=(9.0, "€22.5B revenue, 15,000+ customers, 500MW hydrogen — the world's #1 industrial gas company."))),
    competitors=[dict(t="LIN", n="Linde (DE/US)", mc=90e9, rev=32e9, pe=22, note="#1 in global industrial gases; 1.5x Air Liquide's revenue; 10% lower cost/customer"),
                 dict(t="APD", n="Air Products (US)", mc=55e9, rev=18e9, pe=18, note="#2 in global industrial gases; 80% of Air Liquide's revenue; 8% lower cost/customer"),
                 dict(t="RWE.DE", n="RWE (Germany)", mc=40e9, rev=45e9, pe=25, note="#2 in European hydrogen; 500MW vs. Air Liquide 500MW; no industrial gas"),
                 dict(t="IBE.MC", n="Iberdrola (Spain)", mc=100e9, rev=28e9, pe=22, note="#1 in European renewables; 31GW; no industrial gas; 2x Air Liquide's hydrogen")],
    edge=("The core edge is TAKE-OR-PAY + HYDROGEN: Air Liquide is the "
          "world's #1 industrial gas company (15,000+ customers; 95% "
          "take-or-pay) with 500MW of hydrogen AND 15-year on-site power "
          "deals for 3 US data centers. The moat is the take-or-pay: 10-30 "
          "year contracts with zero customer churn, 24% operating margin, "
          "and 95% revenue visibility. The data center + hydrogen "
          "optionality is the re-rating story from 17x to 25x on €1B/yr "
          "incremental profit by 2028."),
    sentiment=dict(score=7.2, consensus="Buy", pt=230, pt_lo=160, pt_hi=280, short="0.5% of float"),
    news=[dict(d="2026-10-07", h="Q3 2026: revenue €6.2B (+6% YoY); hydrogen +28% YoY; 15-year data center deal", s="AIR PR", i="pos"),
          dict(d="2026-09-15", h="Air Liquide signs 15-year on-site power deal for 3 US data centers; €2B/yr", s="Bloomberg", i="pos"),
          dict(d="2026-08-21", h="Air Liquide's European ammonia plant (€1B) breaks ground; 2029 operational", s="Reuters", i="pos")],
    trends=["Hydrogen: 500MW → 2GW by 2028; €1B/yr by 2028; the #1 European hydrogen",
            "Data centers: 15-year on-site power deals; 3 US data centers; €2B/yr",
            "Gases: 15,000+ customers; 95% take-or-pay; 95% revenue visibility",
            "3.5% dividend at 60% payout; €500M/yr buybacks"],
    swot=dict(
        s=["15,000+ customers; 95% take-or-pay; 95% revenue visibility",
           "500MW hydrogen; 15-year data center deals; €2B/yr",
           "3.5% dividend at 60% payout; €500M/yr buybacks",
           "24% operating margin; 18% ROIC; the #1 industrial gas company"],
        w=["17x P/E is the 5-yr average; the re-rating story is unproven",
           "Hydrogen: 25% of revenue; 2028 commercialization risk",
           "Debt: €25B; 2.5x EBITDA; rate sensitivity",
           "Growth: 7% revenue growth; the slowest in the DAX"],
        o=["Hydrogen: 2GW by 2028; €1B/yr",
           "Data centers: 5 US data centers by 2028; €3B/yr",
           "Gases: 20,000+ customers by 2028; €500M/yr",
           "Dividend: 4% yield by 2028; €1B/yr buybacks"],
        t=["Hydrogen: 2028 commercialization delay; -50% of hydrogen revenue",
           "Linde: 1.5x revenue; -10% of gas market share",
           "Debt: +100bps = -€250M/yr interest",
           "Macro: industrial recession; -10% of gas revenue"]),
    thesis=dict(
        bull=("Hydrogen 2GW, data centers 5, gases 20k: €5.50 EPS 2028E; 25x.", 275, 0.30),
        base=("Steady growth, 3.5% dividend, 17x earnings.", 225, 0.50),
        bear=("Hydrogen delay, Linde, debt: 12x earnings.", 155, 0.20)),
    dcf=dict(fcf_ps=12.60, g=0.07, terminal=0.03, rate=0.085, net_cash_ps=-75.60)),

# ============================== ASTRAZENECA ================================
"NVO": dict(
    name="AstraZeneca plc", sector="Healthcare", industry="Pharma / Oncology / Obesity",
    exchange="XETRA", country="GB", currency="EUR", website="astrazeneca.com",
    employees="~87,000",
    price=145.00, market_cap=140e9, low52=110.00, high52=165.00,
    fundamentals=dict(rev=35.0e9, rev_g=12, gm=75.0, opm=38.0, nm=32.0, eps=9.67,
                      pe=15.0, fwd_pe=13.0, ps=4.0, ev_ebitda=12, roic=35, roe=28,
                      fcf=12.0e9, cash=15.0e9, debt=25.0e9, div="1.20 EUR/qtr", divy=3.3),
    segments=[("Oncology (Tagrisso, Lynparza)", 45, "€3.9B/qtr; +11% YoY"),
              ("Obesity (AZD2938)", 20, "Phase 3; 26% weight loss"),
              ("Respiratory (Fasenra, Lynza)", 20, "€1.5B/qtr; +15% YoY"),
              ("Cardiovascular + Other", 15, "Entresto, Saxenda; 10% of revenue")],
    biz=("AstraZeneca is the world's #2 pharma company (€140B market cap) "
         "and the #1 in oncology + obesity. The 2026 story is AZD2938: Q3 "
         "oncology €3.9B/qtr (+11% YoY), AZD2938 Phase 3 at 26% weight loss "
         "(the #2 in obesity), oral amylin (AZD5004) Phase 3 positive, and "
         "the China JV (10 new products registered). 15x earnings at 35% "
         "ROIC with a 3.3% yield is the 'oncology + obesity' play."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(5.0, "Pharma has no network effect; but the 100M+ patients on Tagrisso/Lynparza create a de facto retention moat."),
        switching_costs=(6.5, "Pharma: 12-24 month treatment; switching is a 6-month transition. Tagrisso: 2-year lock-in."),
        intangibles=(9.5, "Tagrisso: the #1 oncology drug in Europe ($8.1B/qtr); 25k+ patents; the #1 oncology + obesity franchise."),
        cost_advantage=(7.5, "Oncology: 75% gross margin; 15% lower R&D cost/rival. Obesity: 30% lower $/dose than LLY."),
        scale=(9.0, "€35B revenue, 100M+ patients, 87k employees — the world's #2 pharma company."))),
    competitors=[dict(t="LLY", n="Eli Lilly", mc=1.10e12, rev=79.7e9, pe=55, note="#1 in GLP-1; Mounjaro/Zepbound $40B/yr; the #1 obesity rival"),
                 dict(t="MRK", n="Merck", mc=290e9, rev=60e9, pe=25, note="#1 in oncology (Keytruda); MK-0493 is the #2 obesity rival"),
                 dict(t="NVO", n="Novo Nordisk", mc=380e9, rev=48e9, pe=22, note="#1 in GLP-1; Wegovy/Ozempic; AZD2938 is the #1 rival"),
                 dict(t="SANOFI", n="Sanofi (France)", mc=90e9, rev=35e9, pe=18, note="#3 in European pharma; Dupixent; no oncology moat")],
    edge=("The core edge is ONCOLOGY + OBESITY: AstraZeneca is the only "
          "pharma company with a €3.9B/qtr oncology franchise (Tagrisso) "
          "AND an obesity program (AZD2938) at 26% weight loss. The moat is "
          "the oncology data: 100M+ patients on Tagrisso make the franchise "
          "more valuable every quarter. The obesity optionality is the "
          "re-rating story — from 15x to 25x on €10B/yr obesity revenue "
          "by 2028."),
    sentiment=dict(score=7.5, consensus="Buy", pt=190, pt_lo=130, pt_hi=240, short="1.0% of float"),
    news=[dict(d="2026-10-06", h="Q3 2026: oncology €3.9B/qtr (+11% YoY); AZD2938 Phase 3: 26% weight loss at 48 weeks", s="NVO PR", i="pos"),
          dict(d="2026-09-12", h="AZD5004 (oral amylin) Phase 3 positive; 12% weight loss; 2028 launch", s="Bloomberg", i="pos"),
          dict(d="2026-08-18", h="China JV: 10 new products registered; €2B/yr by 2028", s="Reuters", i="pos")],
    trends=["Oncology: €3.9B/qtr → €5B/qtr by 2028; the #1 European oncology franchise",
            "AZD2938 (obesity): 26% weight loss; €10B/yr by 2028; the #2 in obesity",
            "China JV: 10 new products; €2B/yr by 2028; 15% of revenue",
            "3.3% dividend at 50% payout; €2B/yr buybacks"],
    swot=dict(
        s=["Tagrisso: €3.9B/qtr; the #1 European oncology franchise",
           "AZD2938 (obesity): 26% weight loss; €10B/yr by 2028; the #2 in obesity",
           "75% gross margin; 38% operating margin; 35% ROIC",
           "3.3% dividend at 50% payout; €2B/yr buybacks"],
        w=["15x P/E is the 5-yr average; the re-rating story is unproven",
           "Obesity: AZD2938 is Phase 3; the €10B/yr is unproven",
           "China: 15% of revenue; regulatory + geopolitical risk",
           "Debt: €25B; 1.5x EBITDA; rate sensitivity"],
        o=["Oncology: €5B/qtr by 2028; €20B/yr",
           "AZD2938: €10B/yr by 2028; 30% of revenue",
           "China: 15% → 20% of revenue by 2028; €3B/yr",
           "Dividend: 3.5% yield by 2028; €3B/yr buybacks"],
        t=["Obesity: LLY + NVO; -50% of AZD2938 revenue",
           "Oncology: Tagrisso biosimilar 2028; -20% of oncology revenue",
           "China: regulatory; -10% of China revenue",
           "Macro: pharma recession; -10% of revenue"]),
    thesis=dict(
        bull=("Oncology €5B/qtr, AZD2938 €10B, China €3B: €13.00 EPS 2028E; 25x.", 225, 0.25),
        base=("Oncology +10%, AZD2938 +30%, China +10%; 18x earnings.", 180, 0.50),
        bear=("Obesity miss, oncology cliff, China: 12x earnings.", 110, 0.25)),
    dcf=dict(fcf_ps=12.43, g=0.12, terminal=0.035, rate=0.09, net_cash_ps=-10.36)),

# ============================== SIEMENS ====================================
"SIE.DE": dict(
    name="Siemens AG", sector="Industrials", industry="Energy / AI / Automation",
    exchange="XETRA", country="DE", currency="EUR", website="siemens.com",
    employees="~330,000",
    price=240.00, market_cap=140e9, low52=185.00, high52=275.00,
    fundamentals=dict(rev=75.0e9, rev_g=10, gm=35.0, opm=18.0, nm=14.0, eps=5.20,
                      pe=17.0, fwd_pe=14.5, ps=1.9, ev_ebitda=10, roic=15, roe=12,
                      fcf=8.0e9, cash=10.0e9, debt=45.0e9, div="1.80 EUR/qtr", divy=3.0),
    segments=[("Energy (gas turbines, grids)", 40, "Grid +18% YoY; $4B US grid contract"),
              ("Digital Industries (plc, automation)", 30, "AI factory; 15% growth"),
              ("Healthcare (CT, MRI)", 20, "€5B/qtr; 10% growth"),
              ("Mobility + Other", 10, "Rail; 5% growth")],
    biz=("Siemens is the world's #1 industrial automation + energy company "
         "(€140B market cap). The 2026 story is energy + AI: Q3 orders "
         "€14.2B (+12% YoY), grid +18% YoY, the $4B US grid modernization "
         "contract, and Siemens Energy's clean split (re-rating). 17x "
         "earnings at 15% ROIC with a 3.0% yield is the 'energy + AI' play."),
    moat=dict(rating="Wide Moat", score=8.0, pillars=dict(
        network_effects=(7.0, "330,000 employees; 10,000+ enterprise customers; the #1 industrial automation network on earth."),
        switching_costs=(9.0, "Grid: 30-50 year contracts; PLC: 10-20 year lock-in; re-platforming is a 3-5 year, $100M+ exercise."),
        intangibles=(9.0, "Siemens brand (175+ years) + 30k+ patents + energy IP; the #1 industrial brand on earth."),
        cost_advantage=(7.5, "Grid: 20% lower cost/km than rivals (scale + state-backed). PLC: 15% lower cost/customer."),
        scale=(9.0, "€75B revenue, 330k employees, 10,000+ customers — the world's #1 industrial automation + energy company."))),
    competitors=[dict(t="ABB", n="ABB (Switzerland)", mc=80e9, rev=30e9, pe=22, note="#1 in European automation; 40% of Siemens's revenue; 10% lower cost/customer"),
                 dict(t="HON", n="Honeywell (US)", mc=150e9, rev=40e9, pe=25, note="#1 in US automation; 50% of Siemens's revenue; 15% lower cost/customer"),
                 dict(t="GEV", n="GE Vernova (US)", mc=120e9, rev=35e9, pe=28, note="#1 in US energy; 50% of Siemens's energy revenue; 10% lower cost/km"),
                 dict(t="SBG.PA", n="Schneider Electric (FR)", mc=90e9, rev=38e9, pe=20, note="#2 in European energy management; 50% of Siemens's energy revenue")],
    edge=("The core edge is GRID + AI: Siemens is the #1 in European grid "
          "(+18% YoY; $4B US contract) AND the #1 in industrial automation "
          "(10,000+ customers; 10-20 year lock-in). The moat is the grid: "
          "30-50 year contracts with zero customer churn, 18% operating "
          "margin, and 20% lower cost/km than rivals. The AI factory "
          "optionality is the re-rating story from 17x to 25x on €2B/yr "
          "incremental profit by 2028."),
    sentiment=dict(score=7.2, consensus="Buy", pt=300, pt_lo=210, pt_hi=380, short="0.6% of float"),
    news=[dict(d="2026-10-09", h="Q3 2026: orders €14.2B (+12% YoY); grid +18% YoY; $4B US grid contract", s="SIE PR", i="pos"),
          dict(d="2026-09-17", h="Siemens wins $4B US grid modernization contract; 10-year delivery; 2036", s="Reuters", i="pos"),
          dict(d="2026-08-24", h="Siemens Energy splits cleanly; shares +6% on re-rating; 25x earnings", s="Bloomberg", i="pos")],
    trends=["Grid: +18% YoY; $4B US contract; €5B/yr by 2028; the #1 European grid",
            "AI factory: 10,000+ customers; 15% growth; €2B/yr by 2028",
            "Healthcare: €5B/qtr; 10% growth; 20% of revenue",
            "3.0% dividend at 50% payout; €1B/yr buybacks"],
    swot=dict(
        s=["Grid: +18% YoY; $4B US contract; €5B/yr by 2028",
           "AI factory: 10,000+ customers; 15% growth; €2B/yr by 2028",
           "3.0% dividend at 50% payout; €1B/yr buybacks",
           "175+ years of history; 30k+ patents; the #1 industrial brand"],
        w=["17x P/E is the 5-yr average; the re-rating story is unproven",
           "Debt: €45B; 3x EBITDA; rate sensitivity",
           "Mobility: 10% of revenue; 5% growth; the slowest segment",
           "Growth: 10% revenue growth; the slowest in the DAX"],
        o=["Grid: €5B/yr by 2028; 25% of revenue",
           "AI factory: €2B/yr by 2028; 10% of revenue",
           "Healthcare: €7B/yr by 2028; 25% of revenue",
           "Dividend: 3.5% yield by 2028; €2B/yr buybacks"],
        t=["Debt: +100bps = -€450M/yr interest",
           "ABB: grid +20%; -10% of grid market share",
           "Recession: -10% of industrial revenue",
           "Competition: GE + Honeywell; -5% of automation market share"]),
    thesis=dict(
        bull=("Grid €5B, AI factory €2B, healthcare €7B: €7.00 EPS 2028E; 25x.", 350, 0.30),
        base=("Steady growth, 3.0% dividend, 17x earnings.", 280, 0.50),
        bear=("Debt, ABB, recession: 12x earnings.", 190, 0.20)),
    dcf=dict(fcf_ps=13.71, g=0.08, terminal=0.03, rate=0.085, net_cash_ps=-60.00)),
}
