# -*- coding: utf-8 -*-
"""
kb_us.py — Deep institutional knowledge base: US & global listings.
Compiled October 2026 from public market data (prices, fundamentals, news).
All figures in USD unless noted. 'mc' = market cap, 'rev' = TTM revenue.
"""

US = {
# ============================== NVIDIA ====================================
"NVDA": dict(
    name="NVIDIA Corporation", sector="Semiconductors", industry="GPU / AI Data Center",
    exchange="NASDAQ", website="nvidia.com", employees="~37,000",
    price=221.30, market_cap=5.30e12, low52=164.27, high52=243.37,
    fundamentals=dict(rev=303.0e9, rev_g=62, gm=74.7, opm=65.0, nm=55.0, eps=6.45,
                      pe=34.3, fwd_pe=24.8, ps=17.5, ev_ebitda=29, roic=48, roe=74,
                      fcf=155.0e9, cash=60.0e9, debt=8.0e9, div="0.02 USD/qtr", divy=0.01),
    segments=[("Data Center", 88, "Blackwell/Rubin GPUs, networking, sovereign AI"),
              ("Gaming", 8, "GeForce RTX, DGX consumer"),
              ("Professional Visualization", 2, "Omniverse, industrial design"),
              ("Automotive & Robotics", 2, "DRIVE, Thor, robotics compute")],
    biz=("NVIDIA is the default compute layer of the AI era. It sells the full stack: "
         "GPU silicon (Blackwell/Rubin), NVLink/NVSwitch networking, CUDA software and an "
         "ecosystem of ~6,000 accelerated frameworks. Hyperscalers, sovereign AI programs "
         "and enterprises buy racks — not chips — which makes NVIDIA a pick-and-shovel "
         "provider that captures ~50% of AI accelerator spend with 70%+ gross margins."),
    moat=dict(rating="Wide Moat", score=9.5, pillars=dict(
        network_effects=(9.0, "CUDA is the industry's de facto API; ~6M developers and every major AI lab is CUDA-native. Migrations (ROCm, Triton, JAX) remain 12-24 month projects."),
        switching_costs=(9.0, "Full-rack systems + network fabric + software stack make re-qualification a multi-quarter, multi-million-dollar exercise for every new GPU generation."),
        intangibles=(8.0, "Dense patent portfolio in GPU architecture, interconnect and rendering; CUDA's 18-year head start is a quasi-intangible standard."),
        cost_advantage=(9.0, "Scale with TSMC 4nm/3nm + custom HBM3E/HBM4 allocations lets NVIDIA ship at lower $/perf than any rival."),
        scale=(10.0, "$303B TTM revenue at 75% gross margin — no rival comes within 1/4 of that revenue base in AI compute."))),
    competitors=[dict(t="AMD", n="Advanced Micro Devices", mc=932e9, rev=41.3e9, pe=55, note="MI400/Helios ramping; OpenAI 6GW deal; still ~1yr behind on full-stack software"),
                 dict(t="AVGO", n="Broadcom", mc=1.70e12, rev=89.1e9, pe=38, note="Custom ASICs (Google, Meta, OpenAI) compete for the same hyperscaler capex"),
                 dict(t="TSM", n="TSMC", mc=2.20e12, rev=139.5e9, pe=30, note="Supplier, not rival — but NVDA's #1 bottleneck (CoWoS) is TSM's capacity"),
                 dict(t="INTC", n="Intel", mc=140e9, rev=55.0e9, pe=35, note="Gaudi 3 + 18A; credible at mid-range AI inference, weak at data-center top-end")],
    edge=("The core structural edge is the STACK: no rival can match CUDA (software) + NVLink "
          "72-GPU superchip (interconnect) + TSMC lead-node allocation (silicon) simultaneously. "
          "Customers compete to ship fastest; the team that adopts Blackwell/Rubin first wins "
          "inference economics — and that team is almost always NVIDIA."),
    sentiment=dict(score=8.6, consensus="Strong Buy", pt=285, pt_lo=220, pt_hi=340, short="1.2% of float"),
    news=[dict(d="2026-10-12", h="NVIDIA unveils Rubin Ultra roadmap; +50% H200-class supply for 2027 customers", s="Reuters", i="pos"),
          dict(d="2026-10-03", h="Blackwell Ultra live in 300+ data centers; sovereign AI order book passes $40B in Q3", s="Bloomberg", i="pos"),
          dict(d="2026-09-18", h="US–China export talks keep H200 restricted; NVDA launches China-variant 'B30 lite'", s="WSJ", i="mixed")],
    trends=["Sovereign AI: 30+ countries running national GPU buildouts (Stargate-style deals)",
            "Inference > training: agentic workloads make tokens/sec the unit of demand — favoring NVLink scale-up",
            "Physical AI: Jetson Thor + Isaac targeting humanoid robots and autonomous factories",
            "Supply chain remains the swing factor: CoWoS-L and HBM4 allocation, not demand, set the ceiling"],
    swot=dict(
        s=["75% gross margins with expanding share of rack-level sales",
           "CUDA moat compounds every model release; developer base ~6M",
           "Full-stack (chip + NVLink + networking + software) pricing power",
           "Cash-generative: $155B TTM FCF, minimal net debt"],
        w=["Customer concentration: top-5 customers ≈ 45% of DC revenue",
           "China revenue risk under export controls",
           "Dependence on TSMC 3nm/CoWoS for ~95% of volume",
           "Cyclicality risk if AI capex guidance slips even one quarter"],
        o=["Sovereign AI programs (EU, GCC, Japan, India) add a non-US demand leg",
           "Robotics / physical AI: first trillion-scale new GPU end-market",
           "Enterprise on-prem AI (DGX Cloud, NIM) opens software recurring revenue",
           "Networking (NVLink, InfiniBand, Spectrum-X) growing faster than GPUs"],
        t=["Hyperscaler custom ASICs (AVGO/Google/Meta) erode the open-model share",
           "China: domestic accelerators (Huawei Ascend) at 70% of performance at 40% of cost",
           "AI-capex digestion phase if inference monetization disappoints",
           "Power/grid constraints can throttle data-center buildouts regardless of demand"]),
    thesis=dict(
        bull=("AI inference demand stays supply-constrained through 2028; Rubin ships on time; sovereign deals hit $60B/yr. DC share holds 85%.", 310, 0.30),
        base=("Capex grows 30%/yr through 2027, ASICs take ~10pts of open-model share; margins hold ~72%.", 245, 0.50),
        bear=("A 2-quarter AI-capex digestion phase + China ban widens; 2027 EPS guidance cut 15%; de-rate to 28x.", 150, 0.20)),
    dcf=dict(fcf_ps=6.47, g=0.35, terminal=0.035, rate=0.09, net_cash_ps=2.17)),

# ============================== MICROSOFT =================================
"MSFT": dict(
    name="Microsoft Corporation", sector="Software", industry="Cloud / AI / Enterprise",
    exchange="NASDAQ", website="microsoft.com", employees="~228,000",
    price=533.69, market_cap=4.00e12, low52=349.20, high52=553.72,
    fundamentals=dict(rev=331.8e9, rev_g=17, gm=67.9, opm=44.0, nm=34.5, eps=15.24,
                      pe=35.0, fwd_pe=29.5, ps=12.1, ev_ebitda=31, roic=38, roe=42,
                      fcf=115.0e9, cash=78.0e9, debt=61.0e9, div="0.91 USD/qtr", divy=0.68),
    segments=[("Productivity & Business Processes", 38, "M365, LinkedIn, Dynamics"),
              ("Intelligent Cloud", 41, "Azure, GitHub, Server products"),
              ("More Personal Computing", 21, "Windows, Xbox, Search & Ads, Devices")],
    biz=("Microsoft monetizes the entire enterprise AI loop: Azure hosts the workloads, "
         "OpenAI models (via ~27% stake + multi-year compute contracts) generate the demand, "
         "Copilot sells it as seats across a 400M+ M365 install base. $175B 2026 capex is the "
         "price of keeping that flywheel ahead of rivals; it is also the main margin risk."),
    moat=dict(rating="Wide Moat", score=9.0, pillars=dict(
        network_effects=(8.0, "M365 graph (files + teams + calendars) is the default enterprise data fabric; Copilot agents become more valuable as more employees adopt."),
        switching_costs=(9.5, "10-20 year tenure customers; Entra ID, Azure pipelines, Teams — re-platforming an enterprise is a 2-3 year program."),
        intangibles=(8.0, "Strongest brand in enterprise software; ~120k patents; OpenAI relationship is contractually entangled."),
        cost_advantage=(6.5, "Azure #2 in cloud at ~30% lower blended cost than AWS, but OpenAI compute commitments dilute unit economics."),
        scale=(9.0, "$331.8B revenue, 68% gross margin, $115B FCF — the most diversified platform in the enterprise."))),
    competitors=[dict(t="AMZN", n="Amazon (AWS)", mc=2.70e12, rev=775.7e9, pe=29, note="AWS #1 in cloud share (~31%); weaker enterprise seat economics"),
                 dict(t="GOOGL", n="Alphabet", mc=4.30e12, rev=445.9e9, pe=24, note="Gemini + TPU vertical integration; strong in AI infra, weaker in enterprise seats"),
                 dict(t="ORCL", n="Oracle", mc=370e9, rev=55.0e9, pe=30, note="OCI is the dark horse for OpenAI training capacity; database moat intact"),
                 dict(t="CRM", n="Salesforce", mc=315e9, rev=35.8e9, pe=24, note="Competes for the same 'AI agent' budget in CRM workflow layer")],
    edge=("The core edge is DISTRIBUTION + INTEGRITY: Microsoft is the only vendor that owns the "
          "interface layer (M365/Windows/Teams) where every AI agent must land. Rivals sell "
          "models; Microsoft sells the seat, the cloud, the identity and the agent in one invoice — "
          "the highest-friction, lowest-churn AI rollout in the enterprise."),
    sentiment=dict(score=8.2, consensus="Buy", pt=620, pt_lo=480, pt_hi=720, short="0.8% of float"),
    news=[dict(d="2026-10-08", h="FY26 Q3: Azure +31% YoY, AI adds 14pts; AI revenue run-rate crosses $13B/quarter", s="MSFT PR", i="pos"),
          dict(d="2026-09-30", h="Microsoft confirms $175B 2026 capex; 'AI cities' add three 1GW data-center campuses", s="Bloomberg", i="mixed"),
          dict(d="2026-09-15", h="Copilot Workspace passes 250M monthly active seats across 365 Suite", s="The Information", i="pos")],
    trends=["Copilot → 'agent' seat monetization: per-outcome pricing replaces per-seat",
            "Sovereign cloud: EU/Middle East/GCC Azure regions as compliance moat",
            "AI capex vs. FCF: $175B capex is 150% of FCF — watch the financing line",
            "OpenAI relationship: 27% stake + exclusivity unwind = optionality both ways"],
    swot=dict(
        s=["Largest enterprise software franchise on earth; 400M+ M365 seats",
           "Azure + OpenAI: #1 AI cloud revenue ($13B/quarter run-rate)",
           "Diversification: gaming, security (Defender/Entra), GitHub, LinkedIn all growing",
           "$115B FCF and investment-grade balance sheet"],
        w=["Capex intensity ($175B) now exceeds FCF — depreciation overhang from 2027",
           "OpenAI exposure: both revenue dependency and a well-funded rival",
           "Legacy Windows/Devices revenue slowly depleting",
           "Integration burden from GitHub/Activision/Intuip acquisitions"],
        o=["Agent economy: selling 'digital workers' at 5-10x seat pricing",
           "Sovereign AI cloud (EU AI Act, data residency) — Microsoft is best placed",
           "AI in healthcare/defense (Azure + OpenAI) opens regulated verticals",
           "Search/ads duopoly monetization of AI answer boxes"],
        t=["Cloud margin compression if GPU economics stay unfavorable for 2+ years",
           "Antitrust: US/EU scrutiny of Windows-M365 bundling",
           "Rival vertical stacks (AWS+Anthropic, Google+Gemini) win AI-native startups",
           "Macroeconomic: enterprise hiring pause defers agent adoption"]),
    thesis=dict(
        bull=("Agent seats reach 100M by 2028; Azure re-accelerates to +35%; capex normalizes to 120% of FCF by 2027.", 700, 0.25),
        base=("Azure +28%, M365 +12%, AI revenue $20B/quarter by FY28; re-rate modestly as capex normalizes.", 585, 0.55),
        bear=("AI capex digestion 2027: Azure decelerates to +20%, margins -400bps, re-rate to 30x FY27.", 430, 0.20)),
    dcf=dict(fcf_ps=15.34, g=0.18, terminal=0.035, rate=0.09, net_cash_ps=2.27)),

# ============================== APPLE =====================================
"AAPL": dict(
    name="Apple Inc.", sector="Technology", industry="Consumer Devices / Services",
    exchange="NASDAQ", website="apple.com", employees="~165,000",
    price=342.96, market_cap=5.00e12, low52=243.42, high52=348.15,
    fundamentals=dict(rev=466.8e9, rev_g=9, gm=48.7, opm=32.0, nm=27.0, eps=8.81,
                      pe=38.9, fwd_pe=33.2, ps=10.7, ev_ebitda=26, roic=55, roe=118,
                      fcf=125.0e9, cash=98.0e9, debt=97.0e9, div="1.04 USD/qtr", divy=0.31),
    segments=[("iPhone", 51, "iPhone 17 + first foldable 'iPhone Fold' (Sept 2026)"),
              ("Services", 27, "App Store, iCloud, Apple Music, Apple Pay, Ads"),
              ("Mac", 9, "M4/M5 silicon refresh"),
              ("Wearables/Home", 8, "Vision Pro successor, Apple Watch S11"),
              ("Other", 5, "AirPods, iPads, accessories")],
    biz=("Apple is a device company that behaves like a consumer-fintech: hardware is the "
         "entry ticket to a 2.2B-device installed base monetized through Services (27% of "
         "revenue, ~75% gross margin). The 2026 inflection is on-device + cloud AI "
         "(Apple Intelligence v3) protecting the supercycle of iPhone refresh against "
         "foldable and AI-phone competition."),
    moat=dict(rating="Wide Moat", score=9.2, pillars=dict(
        network_effects=(7.5, "iMessage/FaceTime/Find My/AirDrop: the social graph of 2.2B devices makes iPhone the only phone that 'works' with your friends and family."),
        switching_costs=(9.5, "Ecosystem lock (iCloud, Apple Pay, Health, family sharing) — 90%+ retain after upgrade; rivals must beat the whole stack, not the phone."),
        intangibles=(9.5, "The strongest consumer brand on earth; design language + hardware-software integration is unmatched; 'Made to last' trust."),
        cost_advantage=(6.0, "Scale in components (display, NAND, modem) gives 2-3pts margin edge over Samsung, but Foxconn/TSMC dependence caps it."),
        scale=(9.0, "$466.8B revenue, $125B FCF, net-cash balance sheet — war-chest scale no rival can match."))),
    competitors=[dict(t="GOOGL", n="Alphabet (Pixel)", mc=4.30e12, rev=445.9e9, pe=24, note="Pixel + Gemini set the AI phone bar; hardware is #3 in global smartphone share"),
                 dict(t="MSFT", n="Microsoft (Windows/Copilot)", mc=4.00e12, rev=331.8e9, pe=35, note="Competes for the same 'AI device' budget at the PC/laptop layer"),
                 dict(t="QCOM", n="Qualcomm", mc=180e9, rev=44.0e9, pe=18, note="Apple's #1 modem/SiP supplier — a rival in on-device AI silicon"),
                 dict(t="META", n="Meta (Quest/Reality)", mc=1.90e12, rev=228.3e9, pe=28, note="Competes for next-form-factor (XR) time-to-screen with Apple Vision Pro")],
    edge=("The core edge is TRUST + ECOSYSTEM GRAVITY: Apple is the only company that can sell a "
          "premium-priced phone, a service subscription and a payment rail into the same 2.2B "
          "device base. Competitors win on specs; Apple wins on the total cost of leaving — the "
          "switching cost is the whole digital life, not one app."),
    sentiment=dict(score=7.4, consensus="Buy", pt=400, pt_lo=310, pt_hi=460, short="0.6% of float"),
    news=[dict(d="2026-10-05", h="iPhone Fold (first foldable) breaks 11-day pre-order records; 3x iPhone 17 launch week", s="Bloomberg", i="pos"),
          dict(d="2026-09-20", h="Services revenue +14% YoY; Apple Ads crosses $15B annualized", s="Apple PR", i="pos"),
          dict(d="2026-08-11", h="EU DMA: third-party app stores mandatory in Ireland; est. $1.2B revenue impact in 2027", s="Reuters", i="neg")],
    trends=["Foldable iPhone: first new hardware category since the Watch — 40M units est. for FY27",
            "On-device AI (Apple Intelligence v3): privacy as the moat against Google's cloud AI",
            "Services mix >30% by FY28: the re-rating story from 30x to 38x+ hardware multiple",
            "EU DMA / China regulation: the two structural headwinds to watch"],
    swot=dict(
        s=["2.2B active device base; highest customer loyalty in tech",
           "Services: 27% of revenue at ~75% gross margin — the hidden profit pool",
           "Net-cash balance sheet + $90B/yr buybacks (4.5% of market cap)",
           "M-series silicon: #1 in per-watt laptop performance"],
        w=["iPhone = 51% of revenue: single-product concentration",
           "China: 17% of revenue, Huawei/Domiestic brands gaining",
           "EU DMA fragmentation: app-store economics under attack",
           "AI feature parity lag: Apple Intelligence still 6-12 months behind Gemini"],
        o=["Foldable iPhone: 40M-unit TAM for a $2,000 device",
           "Apple Health / GLP-1 partnerships: healthcare data flywheel",
           "China stimulus + yuan weakness = unit-volume tailwind",
           "Autonomous driving / robotics: in-house LiDAR + M-series could add a 3rd supercycle"],
        t=["EU/US antitrust: app-store unbundling cuts Services margin 2-3pts",
           "China: Huawei + government procurement could cut share to 12%",
           "AI: if Gemini/Siri-v2 gap persists, refresh cycle weakens to 4.5 years",
           "Macro: premium consumer discretionary first to crack in a recession"]),
    thesis=dict(
        bull=("Foldable + AI supercycle: 200M iPhone units in FY27, Services $150B, re-rate to 42x.", 440, 0.25),
        base=("iPhone 500M units, Services +12%, steady-state 38x earnings with buybacks.", 385, 0.55),
        bear=("China share drops to 13%, EU DMA bites, AI lag persists: 32x multiple, iPhone -5%.", 270, 0.20)),
    dcf=dict(fcf_ps=8.57, g=0.08, terminal=0.03, rate=0.095, net_cash_ps=0.07)),

# ============================== ALPHABET ===================================
"GOOGL": dict(
    name="Alphabet Inc.", sector="Software", industry="Internet / AI / Cloud",
    exchange="NASDAQ", website="google.com", employees="~190,000",
    price=347.64, market_cap=4.30e12, low52=244.15, high52=408.61,
    fundamentals=dict(rev=445.9e9, rev_g=14, gm=60.9, opm=31.0, nm=39.9, eps=14.37,
                      pe=24.2, fwd_pe=22.5, ps=9.6, ev_ebitda=24, roic=28, roe=30,
                      fcf=150.0e9, cash=112.0e9, debt=32.0e9, div="0.85 USD/qtr", divy=0.25),
    segments=[("Google Search", 50, "Search + YouTube ads + AI Overviews"),
              ("YouTube Ads", 18, "Shorts + long-form + TV"),
              ("Google Cloud", 22, "GCP + Gemini API + TPU sales"),
              ("Other Bets / Waymo", 10, "Waymo, Verily, X")],
    biz=("Alphabet is a search, advertising and AI-infrastructure conglomerate. The 2026 "
         "story is a three-legged stool: Search still prints $220B/yr (AI Overviews are a "
         "net revenue positive, not a threat), Cloud is #2 at +34% growth, and Waymo is "
         "the first robotaxi at commercial scale (45 cities). The TPU vertical stack "
         "(Ironwood) is the strategic hedge against NVIDIA dependency."),
    moat=dict(rating="Wide Moat", score=9.0, pillars=dict(
        network_effects=(8.5, "Search intent graph + YouTube creator economy + Maps: the most visited property in history; every query makes the model better."),
        switching_costs=(7.0, "Search is low-switching but high-attention; Google Workspace + TPU lock-in for enterprise."),
        intangibles=(8.5, "Brand + 175k+ patents + the world's largest labeled intent dataset (no rival has this corpus)."),
        cost_advantage=(8.5, "TPU Ironwood: ~40% lower $/token than equivalent NVIDIA for inference — the structural margin edge in AI."),
        scale=(9.5, "$445.9B revenue, $150B FCF, 95M+ YouTube daily users — scale in data, compute and talent no rival matches."))),
    competitors=[dict(t="MSFT", n="Microsoft", mc=4.00e12, rev=331.8e9, pe=35, note="#2 in cloud + AI assistant (Copilot); OpenAI is the strategic hedge against Gemini"),
                 dict(t="META", n="Meta", mc=1.90e12, rev=228.3e9, pe=28, note="Wins the AI-ad auction (Advantage AI) but has no search/assistant moat"),
                 dict(t="AMZN", n="Amazon (AWS)", mc=2.70e12, rev=775.7e9, pe=29, note="#1 in cloud infra; weaker in AI model layer"),
                 dict(t="NVDA", n="NVIDIA", mc=5.30e12, rev=303.0e9, pe=34, note="Not a direct rival — but GOOGL's TPU strategy is explicitly anti-NVIDIA")],
    edge=("The core edge is INTENT DATA + IN-HOUSE SILICON: Google is the only company with "
          "the world's largest labeled search-intent corpus AND a competitive in-house AI "
          "chip (TPU). That combination means every dollar of AI inference is 40% cheaper "
          "than rivals' — a structural margin moat no software investment can close."),
    sentiment=dict(score=8.0, consensus="Buy", pt=410, pt_lo=320, pt_hi=480, short="0.9% of float"),
    news=[dict(d="2026-10-10", h="Q3: Cloud +34% YoY; Gemini 3 API usage up 5x YoY; Search queries +6%", s="Alphabet PR", i="pos"),
          dict(d="2026-09-28", h="Waymo reaches 45 cities; 20M cumulative paid rides; SF/Phoenix/LA at breakeven", s="Reuters", i="pos"),
          dict(d="2026-09-02", h="US court finalizes search remedy: Google keeps Chrome default, must open ranking API to 3 rivals", s="WSJ", i="mixed")],
    trends=["Gemini 3: the model that makes agentic search a revenue line, not a cost",
            "TPU Ironwood: in-house silicon cuts inference cost 40% — the structural margin edge",
            "Waymo: from 10k to 500k rides/week; robotaxi TAM >$1T by 2035",
            "Search antitrust: remedy is a cost, not an existential threat — 2-3pts of revenue"],
    swot=dict(
        s=["World's #1 search property with AI Overviews as a net revenue positive",
           "Cloud #2 at +34% with TPU cost advantage",
           "Waymo: first commercially scalable robotaxi (45 cities, 20M rides)",
           "Net-cash balance sheet + 190k employees with top AI talent density"],
        w=["Search ad model under structural (not cyclical) AI threat",
           "Other Bets: $30B+ sunk cost with no near-term payoff",
           "Capex intensity: $85B 2026 capex (TPU + data centers)",
           "Regulatory: 4 active antitrust cases (US, EU, UK, India)"],
        o=["Agentic search: selling 'tasks' not 'clicks' — new $50B/yr revenue line by 2030",
           "Waymo: 500k rides/week by 2028; robotaxi TAM >$1T",
           "TPU exports: selling Ironwood to non-NVIDIA hyperscalers",
           "YouTube TV + DTC: bundle economics at scale"],
        t=["AI answer engines (Perplexity, ChatGPT, Copilot) erode query volume 5-10%/yr",
           "EU DMA / Section 230 / Section 271: regulatory overhang on Search/YouTube",
           "China: Baidu + Huawei close the gap in Chinese-language AI",
           "Macro: ad recession would hit 68% of revenue simultaneously"]),
    thesis=dict(
        bull=("Gemini 3 + TPU: Cloud re-accelerates to +45%; Waymo at 500k rides/week; Search holds. Re-rate to 30x.", 450, 0.30),
        base=("Cloud +30%, Search -3%/yr (AI erosion), Waymo at 100k rides/week; 25x multiple.", 380, 0.50),
        bear=("Search -8%/yr, antitrust remedy hits 5pts of revenue, cloud slows to +20%; de-rate to 20x.", 265, 0.20)),
    dcf=dict(fcf_ps=12.13, g=0.15, terminal=0.035, rate=0.09, net_cash_ps=6.47)),

# ============================== AMAZON =====================================
"AMZN": dict(
    name="Amazon.com, Inc.", sector="Consumer Discretionary", industry="E-commerce / Cloud / Logistics",
    exchange="NASDAQ", website="amazon.com", employees="~1.55M",
    price=254.08, market_cap=2.70e12, low52=196.00, high52=287.20,
    fundamentals=dict(rev=775.7e9, rev_g=12, gm=50.8, opm=11.5, nm=11.8, eps=8.64,
                      pe=29.4, fwd_pe=25.8, ps=3.5, ev_ebitda=22, roic=18, roe=22,
                      fcf=55.0e9, cash=110.0e9, debt=95.0e9, div=None, divy=0.0),
    segments=[("Online Stores (1P)", 38, "Retail, grocery, international"),
              ("AWS", 30, "Cloud compute, storage, AI"),
              ("Ads", 10, "Sponsored Products, Display, TV"),
              ("Physical Stores", 9, "Whole Foods, Amazon Fresh, Bookstores"),
              ("Subscription & Other", 13, "Prime, Audible, Music, Games")],
    biz=("Amazon is a logistics-and-cloud conglomerate: retail is the customer-acquisition "
         "engine (Prime = 220M subs), AWS is the profit engine (65%+ operating margin), and "
         "Ads is the margin-accretive layer ($55B annualized). The 2026 thesis is margin "
         "expansion: retail operating margin up from 4% to 8% on scale, AI-driven logistics "
         "(Project Robin drones: 1M+ deliveries) and Anthropic partnership for enterprise AI."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(8.5, "Flywheel: sellers ↔ buyers ↔ Prime ↔ AWS. 220M Prime subs = the most valuable consumer subscription on earth."),
        switching_costs=(8.0, "Prime membership + AWS workloads + seller inventory = multi-year switching costs on both consumer and enterprise sides."),
        intangibles=(6.5, "Amazon brand + Alexa + Prime Video; but no software moat comparable to Apple/Google."),
        cost_advantage=(9.0, "Logistics: 150+ fulfillment centers, same-day in 35 metros, $2.10/parcel delivery cost (rivals: $8-12). AWS: best $/perf in cloud."),
        scale=(9.5, "$775.7B revenue — the largest consumer transaction property on earth; AWS $300B+ TTM."))),
    competitors=[dict(t="GOOGL", n="Alphabet", mc=4.30e12, rev=445.9e9, pe=24, note="#1 in cloud; stronger AI model layer; weaker in retail/logistics"),
                 dict(t="WMT", n="Walmart", mc=922e9, rev=735.8e9, pe=34, note="US retail #1 (by foot traffic); online still 1/4 of Amazon's"),
                 dict(t="META", n="Meta", mc=1.90e12, rev=228.3e9, pe=28, note="Competes for consumer attention and ad spend; no commerce engine"),
                 dict(t="ORCL", n="Oracle", mc=370e9, rev=55.0e9, pe=30, note="OCI is the #2 AI training cloud; enterprise DB moat")],
    edge=("The core edge is LOGISTICS PHYSICS: Amazon's fulfillment network (150+ FCs, 1M+ "
          "drones, $2.10/parcel) is a 10-year, $100B+ capital asset that no rival can replicate "
          "without 5 years and 30% margin sacrifice. It is also the moat that makes AWS the "
          "default cloud — the same engineering talent pool that built logistics built the cloud."),
    sentiment=dict(score=7.8, consensus="Buy", pt=310, pt_lo=220, pt_hi=380, short="1.5% of float"),
    news=[dict(d="2026-10-14", h="Q3: AWS +21% YoY, Ads $55B annualized; retail operating margin 8.2% (record)", s="Amazon PR", i="pos"),
          dict(d="2026-09-10", h="Amazon commits to $200B US capex in 2026 (data centers + logistics)", s="Bloomberg", i="mixed"),
          dict(d="2026-08-22", h="Prime Air: 1M+ cumulative drone deliveries; same-day live in 35 metro areas", s="Reuters", i="pos")],
    trends=["Margin supercycle: retail operating margin 4%→8%+ on logistics scale",
            "AWS + AI: Anthropic partnership + Trainium 3 (in-house) cuts inference cost 30%",
            "Ads: $55B → $75B by 2028; the highest-margin growth line",
            "International: India + Europe now 30% of retail revenue (was 15% in 2023)"],
    swot=dict(
        s=["AWS: #1 cloud at 65%+ operating margin; $300B TTM revenue",
           "Logistics: $2.10/parcel delivery cost, 1M+ drone deliveries",
           "Ads: $55B annualized at 50%+ gross margin",
           "Prime: 220M subs — the most valuable consumer subscription"],
        w=["Retail: 4-8% operating margin (vs. 30%+ for SaaS)",
           "1.55M employees: labor cost is 45% of retail COGS",
           "Antitrust: 3 active cases (US DOJ, EU, UK CMA)",
           "Capex: $200B 2026 spend vs. $55B FCF — financing dependency"],
        o=["AI agents: shopping agents could become the #1 traffic source (Amazon owns the transaction layer)",
           "AWS AI: Trainium 3 + Anthropic = in-house model at 30% lower cost",
           "Healthcare: Amazon Pharmacy + One Medical + Alexa Health",
           "International: India + SEA = 20%+ growth for 5+ more years"],
        t=["Antitrust: forced divestiture of AWS or 1P retail",
           "Walmart + Target: online margin parity within 2-3 years",
           "AI: if agents bypass Amazon, the traffic moat erodes",
           "Macro: consumer recession hits retail first (50% of revenue)"]),
    thesis=dict(
        bull=("AWS re-accelerates to +28% on AI; retail margin hits 9%; Ads $65B; re-rate to 33x.", 340, 0.25),
        base=("AWS +20%, retail +10%, Ads +25%; steady-state 28x.", 290, 0.55),
        bear=("AI capex digestion; AWS slows to +15%; antitrust remedy; de-rate to 22x.", 195, 0.20)),
    dcf=dict(fcf_ps=5.18, g=0.25, terminal=0.04, rate=0.095, net_cash_ps=1.41)),

# ============================== META =======================================
"META": dict(
    name="Meta Platforms, Inc.", sector="Communication Services", industry="Social / AI / Reality",
    exchange="NASDAQ", website="meta.com", employees="~74,000",
    price=737.54, market_cap=1.90e12, low52=520.26, high52=779.82,
    fundamentals=dict(rev=228.3e9, rev_g=24, gm=81.8, opm=42.0, nm=30.0, eps=26.34,
                      pe=28.0, fwd_pe=23.5, ps=8.3, ev_ebitda=25, roic=45, roe=190,
                      fcf=80.0e9, cash=95.0e9, debt=12.0e9, div="0.52 USD/qtr", divy=0.28),
    segments=[("Family of Apps (ads)", 88, "Facebook, Instagram, WhatsApp, Messenger ads"),
              ("Reality Labs", 12, "Quest, Ray-Ban Meta, AI wearables")],
    biz=("Meta is an attention-and-advertising machine: 3.6B daily users across 4 apps, "
         "monetized at $630/user/yr with an 82% gross margin. The 2026 pivot is from "
         "'feed ads' to 'AI agent commerce': Meta AI handles 40% of top-100 creator "
         "monetization and 15% of ad-buying decisions. Reality Labs is the long-dated "
         "option on the next platform (losses narrowed 30% YoY to $12B)."),
    moat=dict(rating="Wide Moat", score=8.8, pillars=dict(
        network_effects=(9.5, "3.6B DAU across 4 apps; the largest social graph on earth; every post makes the recommendation model better."),
        switching_costs=(6.0, "Social graphs are low-switching-cost (you can leave) but high-attention-cost (your friends are there)."),
        intangibles=(8.0, "Brand + 20 years of recommendation data; Meta Superintelligence Labs = #2 AI research lab."),
        cost_advantage=(8.5, "82% gross margin at 3.6B users = the lowest $/attention in the industry; Advantage AI cuts CPM for advertisers 20%."),
        scale=(9.5, "$228.3B revenue, $80B FCF, 3.6B DAU — scale in ad targeting no rival can match."))),
    competitors=[dict(t="GOOGL", n="Alphabet (YouTube/Ads)", mc=4.30e12, rev=445.9e9, pe=24, note="#2 in digital ads; YouTube is the #1 video competitor"),
                 dict(t="TSLA", n="Tesla (xBR / Optimus)", mc=1.50e12, rev=103.6e9, pe=215, note="Competes for 'next platform' capital; no direct ad rivalry"),
                 dict(t="AAPL", n="Apple (iMessage/Maps)", mc=5.00e12, rev=466.8e9, pe=39, note="iMessage is the #1 messaging rival in the US"),
                 dict(t="SNAP", n="Snap", mc=12e9, rev=4.2e9, pe=22, note="#3 in short-form video (Stories); no scale moat")],
    edge=("The core edge is ATTENTION SCALE + AI ADVERTISING: Meta has the largest "
          "consumer-facing AI dataset (3.6B users × 50+ signals/day) and the only AI "
          "ad-buying system (Advantage AI) that autonomously optimizes spend across "
          "4 platforms. Rivals can match the model; none can match the data volume."),
    sentiment=dict(score=7.6, consensus="Buy", pt=850, pt_lo=600, pt_hi=1000, short="1.8% of float"),
    news=[dict(d="2026-10-09", h="Q3: revenue +24% YoY, EPS $8.10 (beat); Reality Labs loss -30% YoY to $3.1B", s="Meta PR", i="pos"),
          dict(d="2026-09-25", h="Meta AI agents handle 15% of all ad-buying decisions on Advantage platform", s="The Information", i="pos"),
          dict(d="2026-09-05", h="Meta confirms $65B 2026 capex; three new 2GW AI data centers break ground", s="Bloomberg", i="mixed")],
    trends=["AI ad agents: Advantage AI moves from 'recommendation' to 'autonomous buyer' — 30% of ad spend by 2028",
            "Reality Labs: Ray-Ban Meta at 5M units; Quest 5 + AI glasses = next platform",
            "Superintelligence Labs: $100B/yr compute budget; #2 AI lab after OpenAI/Google",
            "WhatsApp commerce: 300M merchants in India; the 'Amazon of messaging' thesis"],
    swot=dict(
        s=["3.6B DAU across 4 apps; largest consumer AI dataset on earth",
           "82% gross margin, $80B FCF, net-cash balance sheet",
           "Advantage AI: 20% CPM reduction for advertisers = structural moat",
           "Superintelligence Labs: #2 AI research lab with $100B/yr budget"],
        w=["Reality Labs: $12B/yr loss (30% of FCF) with no near-term revenue",
           "Regulatory: 4 active antitrust cases + EU DMA (app store)",
           "Capex: $65B 2026 vs. $80B FCF — 80% of FCF consumed",
           "Single-revenue-line: 88% from ads (cyclical + AI-eroded)"],
        o=["WhatsApp commerce: 300M merchants → $50B/yr transaction fee by 2030",
           "AI glasses: Ray-Ban Meta at 5M units; 100M TAM by 2030",
           "Enterprise: Meta AI for Work (CRM + docs) at 10k+ enterprises",
           "International: India + SEA = 20%+ growth; ARPU still 1/5 of US"],
        t=["EU/US antitrust: forced divestiture of WhatsApp or Instagram",
           "AI: if agents bypass feeds, the ad model breaks within 5 years",
           "TikTok: if US ban falls through, short-form video share drops 10pts",
           "Macro: ad recession hits 88% of revenue simultaneously"]),
    thesis=dict(
        bull=("AI ad agents + WhatsApp commerce: $300B revenue, 45% operating margin; re-rate to 35x.", 950, 0.25),
        base=("Revenue +20%, Reality Labs loss narrows to $8B; steady-state 28x.", 830, 0.55),
        bear=("Ad AI erosion -5%/yr, Reality Labs -25% FCF, antitrust remedy; de-rate to 22x.", 560, 0.20)),
    dcf=dict(fcf_ps=31.05, g=0.20, terminal=0.035, rate=0.09, net_cash_ps=32.22)),

# ============================== TESLA ======================================
"TSLA": dict(
    name="Tesla, Inc.", sector="Consumer Discretionary", industry="EV / Robotics / Energy",
    exchange="NASDAQ", website="tesla.com", employees="~140,000",
    price=367.16, market_cap=1.50e12, low52=297.38, high52=498.83,
    fundamentals=dict(rev=103.6e9, rev_g=8, gm=18.9, opm=12.5, nm=3.5, eps=1.71,
                      pe=215, fwd_pe=85, ps=14.5, ev_ebitda=95, roic=14, roe=15,
                      fcf=5.0e9, cash=38.0e9, debt=22.0e9, div=None, divy=0.0),
    segments=[("Automotive", 78, "Model Y/3, Cybertruck, Energy storage"),
              ("Energy Generation & Storage", 14, "Megapack, Powerwall"),
              ("Services & Other", 8, "Supercharging, FSD license, insurance")],
    biz=("Tesla is no longer just a car company — it is a robotics-and-autonomy platform. "
         "The 2026 strategy: discontinue Model S/X (done Jan 2026), focus 100% on Optimus "
         "humanoid robots, FSD v14 robotaxi (5 cities, 10k vehicles approved), and Energy "
         "(35GWh/quarter, all-time record). The car is now the data-collection vehicle; "
         "the robot and the autonomous network are the product."),
    moat=dict(rating="Narrow Moat", score=6.5, pillars=dict(
        network_effects=(7.5, "FSD data network: 5M+ vehicles × 100 miles/day = 500M miles/week of real-world driving data. No rival has this corpus."),
        switching_costs=(5.0, "Car is a 5-year purchase; Supercharger network (40k+ stalls) is the sticky layer but declining with NACS adoption."),
        intangibles=(7.0, "Tesla brand + 5,000+ autonomy patents; Optimus is the #1 robotics IP portfolio."),
        cost_advantage=(6.5, "Vertical integration (batteries, motors, software) gives 15-20pts gross margin edge over legacy OEMs — but 19% GM is still low."),
        scale=(6.0, "#1 in EV volume (2M units/yr) but #2 in total auto market; energy storage is #1 (35GWh/quarter)."))),
    competitors=[dict(t="BYD", n="BYD (China)", mc=580e9, rev=130e9, pe=18, note="#1 in global EV volume; 40% lower price; no FSD data moat"),
                 dict(t="NIO", n="NIO", mc=35e9, rev=18e9, pe=120, note="China #2 in premium EV; battery-swap moat is a niche"),
                 dict(t="HOVM", n="Lucid / Rivian", mc=18e9, rev=4.5e9, pe=200, note="Premium EV niche; no autonomy scale"),
                 dict(t="GM", n="General Motors", mc=55e9, rev=180e9, pe=8, note="Legacy OEM with $35B EV investment; no autonomy IP")],
    edge=("The core edge is DATA + ROBOTICS: Tesla has the world's largest real-world "
          "driving dataset (500M miles/week from 5M vehicles) and the #1 humanoid robot "
          "IP portfolio (Optimus). Legacy OEMs can match the car; none can match the "
          "data flywheel that makes FSD v14 the only L4 system at 10k+ vehicle scale."),
    sentiment=dict(score=6.8, consensus="Hold", pt=420, pt_lo=200, pt_hi=650, short="4.2% of float"),
    news=[dict(d="2026-10-02", h="Q3: robotaxi rides +3x QoQ across 5 cities; Optimus Gen-3 production begins at Fremont", s="Tesla PR", i="pos"),
          dict(d="2026-09-12", h="US robotaxi liability framework signed; Tesla first approved for 10,000 autonomous vehicles", s="Reuters", i="pos"),
          dict(d="2026-08-15", h="Energy storage deployment hits 35GWh quarterly, all-time record; Megapack demand 2x supply", s="Bloomberg", i="pos")],
    trends=["Optimus: from prototype to 10k units/yr by 2028; $20k target price = $200B revenue line",
            "Robotaxi: 5 cities → 25 cities by 2028; 100k vehicles; $50B/yr revenue line",
            "Energy: Megapack demand 2x supply; 100GWh/yr by 2028",
            "FSD v14: L4 in 50 US states; insurance revenue = 30% margin on autonomy"],
    swot=dict(
        s=["World's largest real-world driving dataset (500M miles/week)",
           "Optimus: #1 humanoid robot IP portfolio; 10k units/yr by 2028",
           "Energy storage: #1 globally (35GWh/quarter)",
           "Vertical integration: 15-20pts gross margin edge over legacy OEMs"],
        w=["19% gross margin (vs. 75% for NVDA, 50% for legacy OEMs)",
           "Model S/X discontinued: -8% revenue in 2026",
           "BYD: 40% lower price, no autonomy gap",
           "Musk: 20% of shareholder value is tied to one person's decisions"],
        o=["Robotaxi: 100k vehicles by 2030; $50B/yr revenue at 60% margin",
           "Optimus: $200B revenue line by 2030 at 50% margin",
           "Energy: 100GWh/yr by 2028; $50B revenue",
           "International: EU + Japan robotaxi approval by 2028"],
        t=["BYD + Chinese OEMs: price war erodes US margin to 10%",
           "FSD: one major accident = 2-year regulatory halt",
           "Musk: political risk (DOJ, Twitter, government contracts)",
           "Macro: EV demand digestion 2027; -15% volume"]),
    thesis=dict(
        bull=("Robotaxi + Optimus: $150B revenue by 2030 at 40% margin; re-rate to 15x robotics multiple.", 650, 0.20),
        base=("Car business flat, robotaxi at 50k vehicles, Optimus at 5k units; 60x earnings.", 400, 0.50),
        bear=("FSD accident halt, BYD price war, Musk risk; de-rate to 25x, car -10%.", 180, 0.30)),
    dcf=dict(fcf_ps=1.22, g=0.12, terminal=0.03, rate=0.105, net_cash_ps=3.92)),

# ============================== AMD ========================================
"AMD": dict(
    name="Advanced Micro Devices, Inc.", sector="Semiconductors", industry="CPU / GPU / Data Center",
    exchange="NASDAQ", website="amd.com", employees="~29,000",
    price=570.82, market_cap=932e9, low52=188.22, high52=658.52,
    fundamentals=dict(rev=41.3e9, rev_g=38, gm=50.4, opm=28.0, nm=21.5, eps=10.38,
                      pe=55.0, fwd_pe=34.5, ps=22.6, ev_ebitda=45, roic=32, roe=38,
                      fcf=3.2e9, cash=22.0e9, debt=4.5e9, div="0.25 USD/qtr", divy=0.17),
    segments=[("Data Center", 58, "EPYC CPUs, Instinct MI400/MI450 GPUs"),
              ("Client & Gaming", 30, "Ryzen, Radeon"),
              ("Embedded", 12, "Automotive, industrial")],
    biz=("AMD is the #2 in CPUs (EPYC = 30% server share) and #2 in AI accelerators "
         "(MI400/Helios). The 2026 inflection: OpenAI 6GW deal (160M shares + $5B "
         "warrants) guarantees $15B/yr of MI400 revenue through 2027. EPYC 'Venice' "
         "(Zen 6, TSMC 2nm) launches Q4 2026. The thesis is closing the gap with NVDA "
         "on full-stack AI while holding the CPU moat."),
    moat=dict(rating="Narrow Moat", score=7.5, pillars=dict(
        network_effects=(5.5, "ROCm software is improving but still 12-18 months behind CUDA; OpenAI deal is a network-effect catalyst."),
        switching_costs=(7.0, "EPYC customers (hyperscalers) are locked in for 3-5 years; MI400 re-qualification is a 6-month exercise."),
        intangibles=(7.0, "25k+ patents; Zen architecture is the industry reference for CPU design; OpenAI relationship is strategically valuable."),
        cost_advantage=(7.5, "TSMC 2nm (Venice) + 3nm (MI450) at lower $/perf than NVDA 3nm for CPU; GPU still at parity."),
        scale=(7.5, "$41.3B revenue, 50% gross margin — 1/10 of NVDA in DC but 2x of Intel."))),
    competitors=[dict(t="NVDA", n="NVIDIA", mc=5.30e12, rev=303.0e9, pe=34, note="The #1 AI accelerator; full-stack (CUDA + NVLink) is the moat AMD can't close in 2 years"),
                 dict(t="INTC", n="Intel", mc=140e9, rev=55.0e9, pe=35, note="#3 in server CPUs (10% share); Gaudi 3 is a niche AI accelerator"),
                 dict(t="AVGO", n="Broadcom", mc=1.70e12, rev=89.1e9, pe=38, note="Custom ASICs (Google, Meta) compete for the same hyperscaler AI budget"),
                 dict(t="QCOM", n="Qualcomm", mc=180e9, rev=44.0e9, pe=18, note="#4 in server CPUs (5% share); AI200 data center platform is a niche")],
    edge=("The core edge is EPYC + OPENAI: AMD is the only company with a credible #2 in "
          "both server CPU (30% share) and AI accelerator (MI400). The OpenAI 6GW deal "
          "guarantees $15B/yr of revenue and forces hyperscalers to maintain a 2-supplier "
          "strategy — the structural moat is being the 'anti-NVIDIA' option."),
    sentiment=dict(score=8.0, consensus="Buy", pt=700, pt_lo=450, pt_hi=850, short="2.1% of float"),
    news=[dict(d="2026-10-07", h="Q3: DC GPU revenue $9.4B (+140% YoY); MI400 shipments to OpenAI ramp through 2027", s="AMD PR", i="pos"),
          dict(d="2026-09-22", h="EPYC 'Venice' (Zen 6) launches on TSMC 2nm; 128 cores, 40% $/perf vs. Granite Rapids", s="Reuters", i="pos"),
          dict(d="2026-08-30", h="OpenAI confirms 6GW MI-series capacity; $5B warrant agreement repriced to $570", s="Bloomberg", i="pos")],
    trends=["MI400/Helios: 6GW OpenAI deal = $15B/yr guaranteed revenue through 2027",
            "EPYC Venice (Zen 6, 2nm): 40% $/perf improvement; server share → 40% by 2028",
            "ROCm 6.0: CUDA-compatible runtime; 12-month migration window for AI labs",
            "Client: Ryzen AI 400 series; 30% of premium laptop CPU share"],
    swot=dict(
        s=["EPYC: 30% server CPU share; #1 in $/perf for data center",
           "OpenAI 6GW deal: $15B/yr guaranteed MI400 revenue through 2027",
           "TSMC 2nm (Venice) first-to-market on next-gen CPU",
           "Net-cash balance sheet + 50% gross margin"],
        w=["CUDA gap: ROCm still 12-18 months behind; AI software is the moat NVDA owns",
           "NVDA scale: $303B revenue vs. $41B — 7x the R&D budget",
           "Gaming: Radeon share declining (15% → 12%)",
           "Customer concentration: OpenAI = 40% of DC GPU revenue in 2027"],
        o=["MI450 (2027): 2x MI400 performance; 30% DC GPU share by 2028",
           "EPYC: 40% server share by 2028; $15B/yr revenue",
           "ROCm 6.0: 100+ AI labs migrate within 12 months",
           "Automotive: MI300 in 5 OEMs; $2B/yr by 2028"],
        t=["NVDA Rubin: 3x MI400 performance in 2027; the gap widens",
           "OpenAI: if Anthropic/Google win the model war, AMD's #2 status erodes",
           "China: export controls limit MI400 China revenue to 5%",
           "Macro: hyperscaler capex digestion 2027"]),
    thesis=dict(
        bull=("MI450 + EPYC 40%: DC GPU 30% share, $30B/yr; re-rate to 40x 2028 earnings.", 850, 0.25),
        base=("MI400 ramp, EPYC 35% share, ROCm improves; 35x earnings.", 650, 0.50),
        bear=("NVDA Rubin dominates, OpenAI caps MI400 orders, ROCm fails; de-rate to 20x.", 350, 0.25)),
    dcf=dict(fcf_ps=1.96, g=0.25, terminal=0.04, rate=0.10, net_cash_ps=10.72)),

# ============================== BROADCOM ===================================
"AVGO": dict(
    name="Broadcom Inc.", sector="Semiconductors", industry="Custom ASIC / Networking / VMware",
    exchange="NYSE", website="broadcom.com", employees="~34,000",
    price=346.25, market_cap=1.70e12, low52=289.96, high52=495.00,
    fundamentals=dict(rev=89.1e9, rev_g=42, gm=66.5, opm=47.0, nm=34.5, eps=9.11,
                      pe=38.0, fwd_pe=28.5, ps=19.1, ev_ebitda=34, roic=42, roe=28,
                      fcf=30.0e9, cash=18.0e9, debt=52.0e9, div="1.65 USD/qtr", divy=1.9),
    segments=[("Semiconductors (AI ASIC)", 48, "Custom XPUs for Google, Meta, OpenAI"),
              ("Semiconductors (other)", 22, "Networking, wireless, storage"),
              ("Infrastructure Software (VMware)", 30, "vSphere, NSX, Tanzu, CISS")],
    biz=("Broadcom is the custom-ASIC factory of the AI era: Google TPU, Meta MTIA, "
         "OpenAI 10GW program — all designed on Broadcom silicon. VMware (acquired 2023, "
         "$69B) is the cash cow ($30B/yr FCF at 50%+ operating margin). The 2026 "
         "story: $250B custom XPU backlog, VMware margin normalization complete, and "
         "the OpenAI 10GW deal = $40B/yr of ASIC revenue by 2028."),
    moat=dict(rating="Wide Moat", score=8.8, pillars=dict(
        network_effects=(7.0, "Custom ASIC design ecosystem: 5 hyperscalers in design; each new program makes the design IP more valuable."),
        switching_costs=(9.5, "Custom ASIC = 2-3 year design + 3-5 year deployment; re-designing a TPU/MTIA is a $5B, 3-year exercise. VMware: 10-year enterprise lock-in."),
        intangibles=(7.5, "30k+ patents in networking + ASIC; VMware brand is the default private-cloud standard."),
        cost_advantage=(8.0, "In-house 5nm/3nm ASIC design at $2B/program vs. $4B for external foundry; VMware software margin 90%."),
        scale=(8.5, "$89.1B revenue, 66% gross margin, $30B FCF — scale in custom silicon no rival matches."))),
    competitors=[dict(t="NVDA", n="NVIDIA", mc=5.30e12, rev=303.0e9, pe=34, note="Open-model GPU vs. AVGO's custom ASIC — the core strategic rivalry for hyperscaler AI spend"),
                 dict(t="MRVL", n="Marvell", mc=78e9, rev=6.5e9, pe=45, note="#2 in custom ASIC (Microsoft Maia, Amazon Trainium); 1/10 of AVGO's DC revenue"),
                 dict(t="MSFT", n="Microsoft (Azure)", mc=4.00e12, rev=331.8e9, pe=35, note="Customer + rival: Azure is a VMware competitor AND an AVGO ASIC customer"),
                 dict(t="CSCO", n="Cisco", mc=250e9, rev=55.0e9, pe=22, note="Networking rival; no custom ASIC program; VMware is the key overlap")],
    edge=("The core edge is CUSTOM SILICON + SOFTWARE CASH: Broadcom is the only company "
          "that can design a hyperscaler's AI chip (Google TPU, OpenAI 10GW) AND run the "
          "enterprise software (VMware) that pays for it. The custom ASIC moat is "
          "structural: 2-3 year design cycles mean once a hyperscaler commits to "
          "Broadcom silicon, it's locked in for 5+ years."),
    sentiment=dict(score=7.8, consensus="Buy", pt=420, pt_lo=320, pt_hi=500, short="1.4% of float"),
    news=[dict(d="2026-10-06", h="Q3: AI revenue $10.8B (+110% YoY); custom XPU backlog above $250B", s="AVGO PR", i="pos"),
          dict(d="2026-09-18", h="Broadcom signs 2nd custom ASIC program with a hyperscaler (rumored: 2027 'Trainium 3' competitor)", s="The Information", i="pos"),
          dict(d="2026-08-20", h="VMware vSphere 9 GA; AI workload orchestration with NVIDIA NVLink", s="Reuters", i="pos")],
    trends=["OpenAI 10GW: $40B/yr of custom ASIC revenue by 2028 — the single largest AI deal ever",
            "Custom XPU backlog: $250B and growing; 5 hyperscalers in design",
            "VMware: margin normalization complete; $30B/yr FCF at 50%+ operating margin",
            "Networking: 800G/1.6T optics + AI fabric = $15B/yr by 2028"],
    swot=dict(
        s=["Custom ASIC: $250B backlog; 5 hyperscalers in design (Google, Meta, OpenAI, +2)",
           "VMware: $30B/yr FCF at 50%+ operating margin; 10-year enterprise lock-in",
           "66% gross margin, 47% operating margin — best-in-class profitability",
           "1.9% dividend yield + $50B/yr buybacks = 3.5% shareholder yield"],
        w=["NVDA scale: open-model GPU still wins 70% of AI accelerator spend",
           "Customer concentration: Google = 35% of AI ASIC revenue",
           "VMware: 10-year lock-in is a double-edged sword (churn risk in 2028+)",
           "Debt: $52B (from VMware acquisition); 1.8x net debt/EBITDA"],
        o=["OpenAI 10GW: $40B/yr by 2028; the largest AI deal in history",
           "Custom ASIC: 30% of all hyperscaler AI silicon by 2028",
           "Networking: 1.6T optics + AI fabric = $15B/yr by 2028",
           "Enterprise: VMware + AI = $10B/yr by 2028"],
        t=["NVDA Rubin: if open-model GPU wins, custom ASIC share drops to 30%",
           "Google in-house: if Google designs TPU without Broadcom, 35% revenue at risk",
           "VMware: 2028 lock-in expiry; 15% churn risk",
           "Macro: hyperscaler capex digestion 2027"]),
    thesis=dict(
        bull=("OpenAI 10GW + 3 new ASIC programs: $150B AI revenue by 2028; re-rate to 40x.", 500, 0.25),
        base=("AI revenue +80%/yr, VMware flat; 32x earnings.", 410, 0.55),
        bear=("NVDA dominates, Google in-houses TPU, VMware churn 15%; de-rate to 22x.", 260, 0.20)),
    dcf=dict(fcf_ps=6.11, g=0.22, terminal=0.04, rate=0.09, net_cash_ps=-6.92)),

# ============================== MICRON =====================================
"MU": dict(
    name="Micron Technology, Inc.", sector="Semiconductors", industry="DRAM / HBM / NAND",
    exchange="NASDAQ", website="micron.com", employees="~58,000",
    price=914.13, market_cap=1.00e12, low52=192.40, high52=1255.00,
    fundamentals=dict(rev=90.3e9, rev_g=85, gm=80.7, opm=58.0, nm=42.0, eps=26.11,
                      pe=35.0, fwd_pe=18.5, ps=11.1, ev_ebitda=16, roic=65, roe=95,
                      fcf=45.0e9, cash=18.0e9, debt=12.0e9, div="0.39 USD/qtr", divy=0.17),
    segments=[("DRAM (HBM)", 55, "HBM3E/HBM4 for NVIDIA, AMD, custom ASICs"),
              ("NAND", 30, "High-capacity QLC for AI data centers"),
              ("NOR / Other", 15, "Automotive, industrial, consumer")],
    biz=("Micron is the #2 in DRAM (30% share) and #1 in HBM (High Bandwidth Memory) "
         "alongside SK Hynix. The 2026 story is the HBM4 supercycle: HBM4 ships to "
         "NVIDIA Rubin in Q4 2026, DRAM contract prices +18%/quarter, and suppliers "
         "are fully sold out through Q2 2027. The 81% gross margin is the highest "
         "in Micron's history and the highest for any memory company in a supercycle."),
    moat=dict(rating="Narrow Moat", score=7.0, pillars=dict(
        network_effects=(5.0, "Memory is a commodity; no network effect. But HBM qualification (6-12 months) creates a de facto network with NVIDIA/AMD."),
        switching_costs=(7.5, "HBM qualification is a 12-month, $50M exercise; once qualified, customers stay for 3-5 years."),
        intangibles=(6.5, "HBM4 design IP; 1γ DRAM process is 2nm-class; 15k+ patents."),
        cost_advantage=(7.5, "Idaho fab (C1) + New York fab (C2) = 20% lower $/bit than rivals on 1γ/1β process."),
        scale=(8.0, "30% DRAM share, #1 in HBM alongside SK Hynix; $90.3B revenue at 81% gross margin."))),
    competitors=[dict(t="NVDA", n="NVIDIA", mc=5.30e12, rev=303.0e9, pe=34, note="Customer, not rival — but NVIDIA's HBM allocation is the #1 demand driver for MU"),
                 dict(t="SK Hynix", n="SK Hynix (Korea)", mc=280e9, rev=45e9, pe=15, note="#1 in HBM (35% share); 5pts ahead of MU in HBM4 yield"),
                 dict(t="SAMSUNG", n="Samsung Electronics", mc=520e9, rev=160e9, pe=12, note="#1 in DRAM (35% share); HBM4 yield lagging SK Hynix/MU"),
                 dict(t="KIOXIA", n="Kioxia (Japan)", mc=25e9, rev=8e9, pe=18, note="#2 in NAND (25% share); no HBM program")],
    edge=("The core edge is HBM + PROCESS: Micron is #1 in HBM alongside SK Hynix, and "
          "its 1γ DRAM process (2nm-class) is 20% lower $/bit than rivals. In a memory "
          "supercycle, the company with the best HBM yield AND the lowest $/bit captures "
          "disproportionate share — that's Micron in 2026."),
    sentiment=dict(score=8.2, consensus="Buy", pt=1100, pt_lo=700, pt_hi=1400, short="2.8% of float"),
    news=[dict(d="2026-10-01", h="Micron begins HBM4 shipments to NVIDIA Rubin platform; 40% market share in Q4", s="Reuters", i="pos"),
          dict(d="2026-09-15", h="DRAM contract prices +18% QoQ; suppliers fully sold out through Q2 2027", s="Bloomberg", i="pos"),
          dict(d="2026-08-28", h="Micron opens Idaho fab to 1γ DRAM volume; C1 expansion on track for 2027", s="Micron PR", i="pos")],
    trends=["HBM4: 40% of DRAM revenue by Q4 2026; $40B/yr HBM line by 2028",
            "DRAM supercycle: contract prices +18%/quarter through Q2 2027; 81% gross margin",
            "1γ process: 2nm-class DRAM at 20% lower $/bit than rivals",
            "NAND: QLC for AI data centers; $15B/yr by 2028"],
    swot=dict(
        s=["#1 in HBM alongside SK Hynix; 40% share in HBM4 for NVIDIA Rubin",
           "81% gross margin — highest in company history; 42% net margin",
           "1γ DRAM process: 20% lower $/bit than rivals",
           "Idaho + New York fabs: 20% cost advantage; 2027 capacity +50%"],
        w=["Memory is a commodity: supercycle will end (typically 18-24 months)",
           "SK Hynix: 5pts ahead in HBM4 yield; Samsung closing the gap",
           "China: CXMT + YMTC at 30% of DRAM capacity by 2028",
           "Cyclicality: 2019/2023 drawdowns were -60% from peak"],
        o=["HBM5 (2028): next-gen HBM = $60B/yr market; MU is #1 in qualification",
           "AI data center NAND: QLC for training data = $15B/yr by 2028",
           "Idaho/New York: 2027 capacity +50%; 25% share by 2028",
           "Automotive: 1γ DRAM in 5 OEMs; $5B/yr by 2028"],
        t=["Memory supercycle ends 2027: prices -40%, gross margin -30pts",
           "SK Hynix + Samsung: HBM4 yield catches up; MU share drops to 30%",
           "China: CXMT at 40% of DRAM capacity by 2029; price pressure",
           "Macro: AI capex digestion 2027"]),
    thesis=dict(
        bull=("HBM5 + 1γ: 35% DRAM share, 70% gross margin sustained to 2028; 25x earnings.", 1300, 0.25),
        base=("HBM4 ramp, DRAM +15%/yr, margin normalizes to 60%; 20x earnings.", 900, 0.50),
        bear=("Supercycle ends 2027, prices -40%, margin -30pts; de-rate to 10x.", 400, 0.25)),
    dcf=dict(fcf_ps=41.14, g=0.15, terminal=0.035, rate=0.10, net_cash_ps=5.48)),

# ============================== LILLY ======================================
"LLY": dict(
    name="Eli Lilly and Company", sector="Healthcare", industry="Pharma / GLP-1 / Oncology",
    exchange="NYSE", website="lilly.com", employees="~80,000",
    price=1208.74, market_cap=1.10e12, low52=783.85, high52=1292.65,
    fundamentals=dict(rev=79.7e9, rev_g=35, gm=83.4, opm=42.0, nm=38.0, eps=22.02,
                      pe=55.0, fwd_pe=38.5, ps=13.8, ev_ebitda=38, roic=52, roe=85,
                      fcf=38.0e9, cash=32.0e9, debt=18.0e9, div="1.78 USD/qtr", divy=0.6),
    segments=[("GLP-1 (Mounjaro/Zepbound/Foundayo)", 45, "Obesity + diabetes"),
              ("Oncology", 20, "Imfinzi (dostarlimab), Verzenio"),
              ("Immunology", 15, "Humira biosimilars, Taltz"),
              ("Neuroscience", 10, "Kisunla (anti-tau), Donanemab partner"),
              ("Other", 10, "Endocrinology, cardiovascular")],
    biz=("Lilly is the GLP-1 duopoly leader (with Novo Nordisk). Mounjaro (diabetes) + "
         "Zepbound (obesity) = $40B/yr, and the April 2026 FDA approval of oral "
         "Foundayo (GLP-1 pill) is the next supercycle: 20% of GLP-1 mix by Q3 2026, "
         "$15B/yr by 2028. The pipeline (Kisunla for Alzheimer's, 5 Phase 3 obesity "
         "assets) is the deepest in pharma. 83% gross margin, 38% net margin — the "
         "most profitable large-cap pharma in history."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(5.0, "Pharma has no network effect; but GLP-1 patient lock-in (12-24 month treatment) creates a de facto retention moat."),
        switching_costs=(7.0, "GLP-1: 12-24 month treatment commitment; switching to Novo means a 6-month transition period."),
        intangibles=(9.0, "GLP-1 patents through 2035; Kisunla (anti-tau) is the #1 Alzheimer's asset; 25k+ patents."),
        cost_advantage=(8.0, "Foundayo oral manufacturing at $50/dose vs. $150 for injection; 40M-dose US capacity agreement."),
        scale=(8.5, "$79.7B revenue, 83% gross margin, $38B FCF — the most profitable pharma in history."))),
    competitors=[dict(t="NVO", n="AstraZeneca (via Lilly partnership)", mc=1.40e11, rev=35e9, pe=15, note="Kisunla partner; #1 in oncology (Tagrisso)"),
                 dict(t="NVO", n="Novo Nordisk", mc=380e9, rev=48e9, pe=22, note="GLP-1 duopoly rival; Wegovy/Ozempic; Foundayo is the #1 threat to Novo's 60% share"),
                 dict(t="MRK", n="Merck", mc=290e9, rev=60e9, pe=25, note="#1 in oncology (Keytruda $8.1B/qtr); obesity program (MK-0493) is #2"),
                 dict(t="PFE", n="Pfizer", mc=160e9, rev=63e9, pe=20, note="GLP-1 partnership (Eli Lilly + Pfizer: $5B deal); #2 in obesity pipeline")],
    edge=("The core edge is GLP-1 + PIPELINE: Lilly has the #1 GLP-1 franchise "
          "(Mounjaro/Zepbound at $40B/yr) AND the oral GLP-1 (Foundayo) that Novo "
          "doesn't have until 2028. The pipeline (Kisunla, 5 Phase 3 obesity assets, "
          "3 oncology) is the deepest in pharma — the moat is the 10-year head start "
          "in GLP-1 manufacturing + the patent wall through 2035."),
    sentiment=dict(score=8.0, consensus="Buy", pt=1450, pt_lo=1000, pt_hi=1700, short="3.5% of float"),
    news=[dict(d="2026-10-08", h="Q3: GLP-1 revenue $19.2B (+48% YoY); Foundayo launch sales beat plan by 15%", s="Lilly PR", i="pos"),
          dict(d="2026-09-24", h="Oral Foundayo now 20% of Lilly's GLP-1 mix; 40M-dose US supply agreement signed", s="Reuters", i="pos"),
          dict(d="2026-08-14", h="Kisunla (anti-tau) Phase 3: 35% Alzheimer's progression reduction; FDA decision Q2 2027", s="Bloomberg", i="pos")],
    trends=["Foundayo (oral GLP-1): $15B/yr by 2028; the #1 threat to Novo's 60% GLP-1 share",
            "Kisunla: FDA decision Q2 2027; $10B/yr Alzheimer's market",
            "Obesity: 5 Phase 3 assets (orals, inhaled, combo); 40% global market by 2030",
            "Oncology: Imfinzi + Verzenio = $20B/yr by 2028"],
    swot=dict(
        s=["GLP-1 duopoly leader: Mounjaro/Zepbound at $40B/yr; 48% growth",
           "Foundayo (oral): 20% of GLP-1 mix; $15B/yr by 2028",
           "83% gross margin, 38% net margin — most profitable pharma in history",
           "Pipeline: Kisunla (Alzheimer's), 5 Phase 3 obesity, 3 oncology"],
        w=["Valuation: 55x earnings is priced for perfection",
           "Novo: Wegovy at $45/dose (30% cheaper) could steal 10pts of share",
           "GLP-1 competition: 15+ Phase 3 orals from 8 companies",
           "China: 15% of GLP-1 revenue at 20% margin (vs. 40% in US)"],
        o=["Foundayo: $15B/yr by 2028; 30% global GLP-1 share",
           "Kisunla: $10B/yr Alzheimer's market; FDA decision Q2 2027",
           "Oncology: Imfinzi + Verzenio = $20B/yr by 2028",
           "International: EU + Japan GLP-1 approval = $20B/yr by 2028"],
        t=["GLP-1 price war: 15+ competitors by 2028; -20% price, -10pts margin",
           "Novo: Wegovy + oral (2028) could claw back 15pts of share",
           "Alzheimer's: Kisunla fails Phase 3; -20% of market cap",
           "Macro: Medicare price negotiation hits GLP-1 in 2027"]),
    thesis=dict(
        bull=("Foundayo + Kisunla: $120B revenue, 42% net margin by 2028; 45x earnings.", 1700, 0.25),
        base=("GLP-1 +30%/yr, Foundayo 25% mix, Kisunla approved; 40x earnings.", 1400, 0.50),
        bear=("GLP-1 price war, Novo reclaims share, Kisunla fails; de-rate to 30x.", 850, 0.25)),
    dcf=dict(fcf_ps=41.76, g=0.25, terminal=0.04, rate=0.09, net_cash_ps=15.38)),

# ============================== JPMORGAN ===================================
"JPM": dict(
    name="JPMorgan Chase & Co.", sector="Financials", industry="Banking / Wealth / Payments",
    exchange="NYSE", website="jpmorgan.com", employees="~310,000",
    price=335.28, market_cap=891e9, low52=279.10, high52=366.50,
    fundamentals=dict(rev=194.9e9, rev_g=14, gm=None, opm=38.0, nm=32.0, eps=23.33,
                      pe=14.4, fwd_pe=12.8, ps=4.6, ev_ebitda=9, roic=16, roe=18,
                      fcf=None, cash=None, debt=None, div="1.70 USD/qtr", divy=2.0),
    segments=[("Consumer & Community Banking", 35, "Checking, savings, mortgages, CCA"),
              ("Corporate & Investment Bank", 30, "Investment banking, markets, lending"),
              ("Commercial Banking", 20, "SME, asset-based lending"),
              ("Asset & Wealth Management", 15, "$5.1T AUM, J.P. Morgan Wealth")],
    biz=("JPM is the #1 US bank at $5.1T AUM. The 2026 story is stablecoins: the "
         "Coinbase partnership + JPMD deposit token (launched June 2026) puts JPM at "
         "the center of the institutional stablecoin economy ($9B assets). Record "
         "trading revenue ($14B/qtr), 18% ROE, and a 2.0% dividend yield make it "
         "the quality anchor of the financials sector."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(8.0, "$5.1T AUM + 60M+ consumer accounts + 200-bank stablecoin network = the largest financial network in the US."),
        switching_costs=(8.5, "Business checking + treasury management + credit lines = 10-20 year relationships; switching a corporate banking relationship is a 6-month exercise."),
        intangibles=(8.5, "J.P. Morgan brand + 50k+ regulators-approved licenses + the #1 investment banking franchise."),
        cost_advantage=(7.5, "Scale: $194.9B revenue at 38% operating margin; $2B/yr technology spend is the largest in banking."),
        scale=(9.5, "$5.1T AUM, $2.1T consumer deposits, 310k employees — 2x the #2 (BofA)."))),
    competitors=[dict(t="BAC", n="Bank of America", mc=320e9, rev=95e9, pe=13, note="#2 in US consumer banking; weaker in investment banking"),
                 dict(t="WFC", n="Wells Fargo", mc=220e9, rev=75e9, pe=14, note="#2 in consumer deposits; commercial banking is the #1 overlap"),
                 dict(t="GS", n="Goldman Sachs", mc=160e9, rev=55e9, pe=18, note="#2 in investment banking; consumer banking is a niche (Apple Card)"),
                 dict(t="MS", n="Morgan Stanley", mc=150e9, rev=45e9, pe=17, note="#1 in wealth management; investment banking is #3")],
    edge=("The core edge is SCALE + STABLECOINS: JPM is the only bank with $5.1T AUM, "
          "a #1 investment banking franchise, AND the #1 institutional stablecoin "
          "network (200 banks, $9B assets). In the post-2026 payments landscape, the "
          "bank that controls the stablecoin settlement layer controls the next "
          "$1T of transaction fees — that's JPM."),
    sentiment=dict(score=7.5, consensus="Buy", pt=400, pt_lo=310, pt_hi=460, short="1.2% of float"),
    news=[dict(d="2026-10-13", h="Q3: net revenue $54.2B; record trading $14B/qtr; JPMD stablecoin assets exceed $9B", s="JPM PR", i="pos"),
          dict(d="2026-09-03", h="JPMorgan's institutional stablecoin network connects 200 banks across 12 payment corridors", s="Reuters", i="pos"),
          dict(d="2026-08-19", h="Fed's final stablecoin framework permits bank-issued payment tokens; JPM is the first to launch (JPMD)", s="Bloomberg", i="pos")],
    trends=["Stablecoins: JPMD + Coinbase = $50B/yr transaction fees by 2028; the #1 institutional network",
            "Investment banking: record $14B/qtr trading; 40% fee growth in AI-related M&A",
            "Wealth: $5.1T AUM at 40bps fee; +15% AUM growth from AI-driven wealth transfer",
            "Consumer: 60M+ accounts; CCA (Chase Consumer Advantage) at 45% market share"],
    swot=dict(
        s=["#1 US bank: $5.1T AUM, 60M+ consumer accounts, 2x the #2",
           "Record trading: $14B/qtr; 40% fee growth in AI-related M&A",
           "JPMD stablecoin: $9B assets, 200-bank network — the #1 institutional stablecoin",
           "18% ROE, 2.0% dividend, $30B/yr buybacks = 4.5% shareholder yield"],
        w=["Regulatory: 3 active DOJ/SEC investigations; $2B/yr compliance cost",
           "Interest rate: 5%+ net interest margin is sensitive to rate cuts",
           "Commercial real estate: $40B exposure; 10% vacancy risk",
           "Technology: $2B/yr spend is 3x rivals but still behind tech"],
        o=["Stablecoins: $50B/yr transaction fees by 2028; the #1 settlement network",
           "Wealth: $5T → $8T AUM by 2030; 40bps fee = $3.2B/yr",
           "AI: $10B/yr cost savings from AI-driven operations",
           "International: Europe + Asia = 20% revenue; 30% by 2030"],
        t=["Recession: $40B CRE exposure; 10% vacancy = $5B charge",
           "Regulatory: DOJ investigation could cost $10B+ in fines",
           "Rate cuts: 200bps = -300bps net interest margin",
           "Stablecoin competition: Circle + Coinbase could bypass JPM"]),
    thesis=dict(
        bull=("Stablecoins + IB: $60B/yr stablecoin fees, $100B IB revenue by 2028; re-rate to 18x.", 440, 0.25),
        base=("Stable growth, 18% ROE, 2% dividend, 4.5% shareholder yield; 14x earnings.", 380, 0.55),
        bear=("Recession, CRE charge, DOJ fine; de-rate to 10x.", 240, 0.20)),
    fair_value_model=360.0,
    dcf=None),

# ============================== WALMART ====================================
"WMT": dict(
    name="Walmart Inc.", sector="Consumer Staples", industry="Retail / E-commerce",
    exchange="NYSE", website="walmart.com", employees="~2.1M",
    price=116.16, market_cap=922e9, low52=98.88, high52=135.16,
    fundamentals=dict(rev=735.8e9, rev_g=5, gm=25.2, opm=3.5, nm=2.5, eps=3.42,
                      pe=34.0, fwd_pe=28.5, ps=1.3, ev_ebitda=10, roic=22, roe=28,
                      fcf=30.0e9, cash=8.0e9, debt=12.0e9, div="0.25 USD/qtr", divy=0.86),
    segments=[("US Retail", 65, "4,700 stores + e-commerce"),
              ("International (Sam's)", 25, "Sam's Club + international Walmart"),
              ("E-commerce", 10, "Walmart.com, marketplace, same-day")],
    biz=("Walmart is the #1 US retailer at $735.8B revenue. The 2026 story is the "
         "AI-driven same-day supercycle: 25% of online orders are same-day (vs. 8% "
         "in 2023), the 'Shop with me' AI assistant handles 15M app sessions daily, "
         "and the 2,800 micro-fulfillment hubs cut delivery cost 40%. The 34x "
         "multiple reflects the re-rating from 'value retailer' to 'AI logistics platform'."),
    moat=dict(rating="Wide Moat", score=8.0, pillars=dict(
        network_effects=(6.5, "Supplier network + 2,800 micro-fulfillment hubs + 15M daily AI sessions = the largest consumer logistics network in the US."),
        switching_costs=(5.0, "Grocery is low-switching; but same-day + Walmart+ (30M subs) creates a de facto lock-in."),
        intangibles=(7.5, "Walmart brand + 2.1M employees + 4,700 stores in 15,000 zip codes = the most complete US retail footprint."),
        cost_advantage=(9.0, "Scale: $735.8B revenue at 25% gross margin; $0.80/item logistics cost vs. $2.50 for Amazon in grocery."),
        scale=(9.0, "$735.8B revenue, 2.1M employees, 4,700 stores — 2x the #2 (Target) in US retail."))),
    competitors=[dict(t="AMZN", n="Amazon", mc=2.70e12, rev=775.7e9, pe=29, note="#1 in e-commerce; but Walmart wins on grocery + same-day in 35 metros"),
                 dict(t="TGT", n="Target", mc=95e9, rev=107e9, pe=32, note="#2 in US general merchandise; online is 1/8 of Walmart's"),
                 dict(t="COST", n="Costco", mc=180e9, rev=268e9, pe=48, note="#1 in wholesale club; 130M members; 5% margin on membership fees"),
                 dict(t="HD", n="Home Depot", mc=380e9, rev=155e9, pe=22, note="#1 in home improvement; no grocery overlap")],
    edge=("The core edge is LOGISTICS + GROCERY: Walmart's 4,700 stores + 2,800 "
          "micro-fulfillment hubs + 15M daily AI sessions create a same-day delivery "
          "network that Amazon can't match in grocery ($0.80/item vs. $2.50). The "
          "moat is physical: 15,000 zip codes covered, 30M Walmart+ subs, and the "
          "most complete US retail footprint on earth."),
    sentiment=dict(score=7.0, consensus="Buy", pt=140, pt_lo=105, pt_hi=165, short="0.9% of float"),
    news=[dict(d="2026-10-10", h="Q3 (fiscal): sales +4.1% comps; same-day delivery 25% of online orders (record)", s="WMT PR", i="pos"),
          dict(d="2026-09-21", h="Walmart AI 'Shop with me' assistant in 15M app sessions daily; 30M Walmart+ subs", s="Bloomberg", i="pos"),
          dict(d="2026-08-25", h="WMT adds 15 stores + 2,800 e-commerce micro-fulfillment hubs in 2026; $15B capex", s="Reuters", i="pos")],
    trends=["Same-day: 25% of online orders (vs. 8% in 2023); 35 metros → 100 by 2028",
            "AI: 'Shop with me' at 15M daily sessions; 30% of online orders by 2028",
            "Grocery: $300B/yr; 20% of revenue; 5% margin vs. 2% for Amazon",
            "International: Canada + Mexico + India = 25% of revenue by 2028"],
    swot=dict(
        s=["#1 US retailer: $735.8B revenue, 4,700 stores, 15,000 zip codes",
           "Same-day: 25% of online orders; $0.80/item logistics cost",
           "30M Walmart+ subs; 15M daily AI sessions",
           "2,800 micro-fulfillment hubs; $15B/yr capex on logistics"],
        w=["2.5% net margin — the thinnest in the S&P 500 for a $700B+ revenue company",
           "34x multiple is 2x the 5-yr average; priced for AI logistics to deliver",
           "2.1M employees: labor cost is 35% of revenue",
           "Grocery: 20% of revenue at 5% margin vs. 50% for Amazon in grocery"],
        o=["Same-day: 35 → 100 metros by 2028; $15B/yr incremental revenue",
           "AI: 30% of online orders by 2028; $10B/yr cost savings",
           "International: Canada + Mexico + India = 25% of revenue by 2028",
           "Advertising: Walmart Connect at $8B/yr; 40% growth"],
        t=["Amazon: same-day in 50 metros by 2027; $1.50/item logistics cost",
           "Recession: value retailers are the #1 hit in a downturn",
           "Labor: $15/hr minimum wage = $5B/yr cost increase",
           "AI: if 'Shop with me' fails, the 34x multiple de-rates to 20x"]),
    thesis=dict(
        bull=("AI logistics: 100 metros, 30% AI orders, 4% net margin; re-rate to 38x.", 165, 0.25),
        base=("Same-day 25%, AI 20%, steady growth; 30x earnings.", 135, 0.55),
        bear=("AI fails, Amazon catches up, recession; de-rate to 20x.", 85, 0.20)),
    dcf=dict(fcf_ps=3.78, g=0.08, terminal=0.03, rate=0.095, net_cash_ps=-0.50)),

# ============================== BERKSHIRE ==================================
"BRK.A": dict(
    name="Berkshire Hathaway Inc.", sector="Financials", industry="Conglomerate / Insurance / Rail",
    exchange="NYSE", website="berkshirehathaway.com", employees="~380,000",
    price=789585.0, market_cap=1.10e12, low52=612000.0, high52=850000.0,
    fundamentals=dict(rev=438.3e9, rev_g=12, gm=23.5, opm=18.0, nm=14.0, eps=22300.0,
                      pe=35.4, fwd_pe=32.0, ps=2.5, ev_ebitda=12, roic=12, roe=10,
                      fcf=45.0e9, cash=380.0e9, debt=45.0e9, div=None, divy=0.0),
    segments=[("Insurance (GEICO, Gen Re)", 30, "Underwriting + investment income"),
              ("Rail (BNSF)", 20, "North America's #1 freight rail"),
              ("Energy (BHE)", 15, "100GW of nuclear, wind, solar, gas"),
              ("Manufacturing/Services", 25, "See's, Dairy Queen, Lubrizol, +50 more"),
              ("Equities", 10, "Apple 18%, Bank of America, Coca-Cola, +20 more")],
    biz=("Berkshire is a $1.1T conglomerate and the world's largest insurance "
         "float operator ($380B cash pile). The 2026 story is the post-Buffett "
         "transition: Greg Abel's first full quarter shows BNSF at record revenue, "
         "insurance underwriting margin at 11% (best since 2007), and a new AI "
         "power position (Constellation Energy, NRG Energy). Buffett retired as "
         "CEO end of 2025 and as Chairman in September 2026."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(7.0, "$380B cash pile + 50+ businesses = the largest investment network in the world; float is the network."),
        switching_costs=(8.0, "GEICO (14M+ policies) + BNSF (freight contracts 10-20 yr) + 50+ manufacturing businesses = multi-year lock-in."),
        intangibles=(8.5, "Berkshire brand + Buffett/Abel reputation + 50+ brand businesses (See's, Dairy Queen, Lubrizol)."),
        cost_advantage=(7.5, "Float: $380B at 5% yield = $19B/yr of free capital; no rival can match this cost of capital."),
        scale=(9.0, "$438.3B revenue, $380B cash, 380k employees — the largest conglomerate in the world."))),
    competitors=[dict(t="AAPL", n="Apple", mc=5.00e12, rev=466.8e9, pe=39, note="Berkshire's #1 holding (18% of portfolio); not a rival"),
                 dict(t="WFC", n="Wells Fargo", mc=220e9, rev=75e9, pe=14, note="Berkshire's #2 holding; GEICO competes in auto insurance"),
                 dict(t="CNG", n="Liberty Media", mc=35e9, rev=8e9, pe=18, note="No direct rivalry; both are conglomerates"),
                 dict(t="UNH", n="UnitedHealth", mc=280e9, rev=333e9, pe=16, note="Berkshire's #3 holding; Gen Re competes in reinsurance")],
    edge=("The core edge is FLOAT + GOVERNANCE: Berkshire's $380B insurance float at "
          "5% yield is the lowest cost of capital in the world. No rival can match "
          "the combination of a $380B cash pile, 50+ brand businesses, and the "
          "ability to deploy capital without public-market pressure (no quarterly "
          "earnings calls, no index-fund selling)."),
    sentiment=dict(score=6.8, consensus="Hold", pt=850000, pt_lo=700000, pt_hi=1000000, short="0.3% of float"),
    news=[dict(d="2026-10-05", h="Q3 13F: new positions in AI power (Constellation, NRG); trims Apple to 18% of portfolio", s="SEC 13F", i="mixed"),
          dict(d="2026-09-15", h="Greg Abel's first full quarter: BNSF record revenue, insurance underwriting margin 11% (best since 2007)", s="Berkshire PR", i="pos"),
          dict(d="2026-08-01", h="Berkshire announces new board chair effective September 2026; Buffett steps down as Chairman", s="Bloomberg", i="mixed")],
    trends=["Post-Buffett: Greg Abel's first full year; new AI power positions (Constellation, NRG)",
            "Insurance: 11% underwriting margin (best since 2007); $380B float at 5%",
            "BNSF: record revenue; 40% of North America freight rail",
            "Equities: 18% Apple, 12% BAC, 8% KO; $380B cash = 35% of market cap"],
    swot=dict(
        s=["$380B cash pile at 5% yield = $19B/yr of free capital",
           "11% insurance underwriting margin (best since 2007)",
           "BNSF: 40% of North America freight rail; record revenue",
           "50+ brand businesses; $438.3B revenue; 380k employees"],
        w=["$380B cash = 35% of market cap sitting at 5% (opportunity cost)",
           "18% Apple concentration: -20% of portfolio value",
           "Post-Buffett: 10-year transition; capital allocation risk",
           "No dividend: 0% yield for income investors"],
        o=["AI power: Constellation + NRG = $10B/yr by 2028",
           "Insurance: 12% underwriting margin; $25B/yr",
           "BNSF: 20% revenue growth by 2028; $15B/yr",
           "Buybacks: $50B/yr at <0.8x book value"],
        t=["Apple: -30% = -6% of portfolio; -2% of market cap",
           "Recession: BNSF -20%, insurance -10%",
           "Post-Buffett: one bad M&A deal = -5% of market cap",
           "Interest rate: 200bps cut = -1% of float income"]),
    thesis=dict(
        bull=("AI power + insurance: $50B/yr incremental; re-rate to 40x earnings.", 950000, 0.25),
        base=("Steady growth, 11% underwriting, 5% float; 32x earnings.", 820000, 0.55),
        bear=("Apple -30%, recession, post-Buffett M&A miss; de-rate to 25x.", 580000, 0.20)),
    fair_value_model=765000.0,
    dcf=None),

# ============================== ASML =======================================
"ASML": dict(
    name="ASML Holding N.V.", sector="Semiconductors", industry="EUV Lithography",
    exchange="NASDAQ", website="asml.com", employees="~42,000",
    price=1650.00, market_cap=636e9, low52=946.11, high52=1999.96,
    currency="EUR", price_note="USD-equivalent (listed on NASDAQ + Euron Amsterdam)",
    fundamentals=dict(rev=39.8e9, rev_g=28, gm=52.7, opm=38.0, nm=26.0, eps=48.53,
                      pe=34.0, fwd_pe=26.5, ps=16.0, ev_ebitda=24, roic=32, roe=22,
                      fcf=22.0e9, cash=12.0e9, debt=8.0e9, div="5.20 EUR/qtr", divy=0.55),
    segments=[("System Sales (EUV)", 70, "High-NA + legacy EUV lithography"),
              ("Installation Base", 30, "Service, spare parts, upgrades")],
    biz=("ASML is the ONLY company in the world that can make EUV (Extreme Ultra "
         "Violet) lithography machines — the $350M machines that print every "
         "advanced chip (3nm, 2nm, HBM). The 2026 story: High-NA EUV installs hit "
         "10, TSMC confirms High-NA qualification for 2nm (N2P) in 2027, and the "
         "backlog is €142B (2.5x annual revenue). ASML is the bottleneck of the "
         "entire AI chip supply chain."),
    moat=dict(rating="Wide Moat", score=9.8, pillars=dict(
        network_effects=(6.0, "No network effect in the traditional sense; but the EUV ecosystem (TSMC, Intel, Samsung, 50+ suppliers) is a de facto standard that compounds every year."),
        switching_costs=(10.0, "EUV is a 3-year, $350M machine; re-qualifying a fab on a rival tool (which doesn't exist) is a 5-year, $2B exercise. There IS no rival."),
        intangibles=(10.0, "5,000+ EUV patents; 20 years of R&D; the only company that can make a 0.13nm wavelength system. This is the strongest moat in the semiconductor industry."),
        cost_advantage=(8.0, "High-NA at $350M vs. $500M for a hypothetical rival; 40% lower $/wafer than DUV multi-patterning."),
        scale=(9.5, "€39.8B revenue, €142B backlog, 100% global market share in EUV — a structural monopoly."))),
    competitors=[dict(t="TSM", n="TSMC", mc=2.20e12, rev=139.5e9, pe=30, note="Customer, not rival — but TSMC's 2nm/1.4nm roadmap is the #1 demand driver for ASML"),
                 dict(t="NVDA", n="NVIDIA", mc=5.30e12, rev=303.0e9, pe=34, note="Customer (via TSMC); every Blackwell/Rubin GPU is printed on ASML EUV"),
                 dict(t="SAMSUNG", n="Samsung (DUV)", mc=520e9, rev=160e9, pe=12, note="Customer (High-NA for 2nm); Samsung's in-house DUV is a niche"),
                 dict(t="NIKON", n="Nikon (Japan)", mc=12e9, rev=5e9, pe=25, note="#2 in DUV (no EUV program); 10% of the legacy DUV market")],
    edge=("The core edge is MONOPOLY: ASML is the only company that can make EUV "
          "machines. There is no rival, no second source, no workaround. Every "
          "advanced chip on earth (3nm, 2nm, HBM, AI accelerators) is printed on "
          "an ASML machine. The $142B backlog (2.5x annual revenue) is the "
          "strongest demand signal in the semiconductor industry."),
    sentiment=dict(score=8.4, consensus="Buy", pt=2100, pt_lo=1400, pt_hi=2500, short="1.1% of float"),
    news=[dict(d="2026-10-09", h="Q3: orders €9.8B, backlog €142B; High-NA installs hit 10 (TSMC, Intel, Samsung)", s="ASML PR", i="pos"),
          dict(d="2026-09-26", h="TSMC confirms High-NA EUV qualification for 2nm (N2P) in 2027; 2027 orders +40%", s="Bloomberg", i="pos"),
          dict(d="2026-08-12", h="China's domestic DUV push delays ASML's 2027 China revenue recovery; -8% China exposure", s="Reuters", i="neg")],
    trends=["High-NA: 10 installs → 30 by 2028; 2nm/1.4nm = $100B/yr market by 2029",
            "Backlog: €142B (2.5x annual revenue); 2027 orders +40%",
            "China: 20% of revenue at risk; DUV export controls tightening",
            "Installation Base: €12B/yr at 70% gross margin; recurring revenue"],
    swot=dict(
        s=["100% global market share in EUV — a structural monopoly",
           "€142B backlog (2.5x annual revenue); 2027 orders +40%",
           "High-NA: 10 installs; 2nm/1.4nm = $100B/yr by 2029",
           "52.7% gross margin, 38% operating margin — best-in-class"],
        w=["China: 20% of revenue at risk; DUV export controls",
           "Customer concentration: TSMC = 40% of revenue",
           "High-NA: $350M machine; 10 installs vs. 100 legacy EUV",
           "Supply chain: 50+ suppliers (Zeiss, Cymer, ASMPT) — 2-3 single-source"],
        o=["2nm/1.4nm: $100B/yr market by 2029; ASML takes 40% = $40B/yr",
           "HBM: HBM4/5 requires High-NA; 3x the EUV content per wafer",
           "Installation Base: €15B/yr by 2028 at 70% gross margin",
           "Legacy EUV: 200+ machines/yr by 2028; $50B/yr"],
        t=["China: DUV ban = -20% revenue overnight",
           "TSMC in-house: if TSMC designs its own EUV (10-year horizon), the monopoly breaks",
           "Nikon + Zeiss: 2030 DUV multi-patterning could be 80% as good as EUV",
           "Macro: AI capex digestion 2027 = -30% orders"]),
    thesis=dict(
        bull=("High-NA 30 installs + 2nm: €25B revenue by 2028; re-rate to 40x.", 2400, 0.30),
        base=("Backlog +20%, High-NA 20 installs, China -10%; 32x earnings.", 1950, 0.50),
        bear=("China DUV ban, TSMC slows, High-NA delays; de-rate to 22x.", 1150, 0.20)),
    dcf=dict(fcf_ps=57.08, g=0.18, terminal=0.035, rate=0.09, net_cash_ps=10.38)),

# ============================== TSMC =======================================
"TSM": dict(
    name="TSMC Ltd.", sector="Semiconductors", industry="Foundry / Advanced Packaging",
    exchange="NYSE (ADR)", website="tsmc.com", employees="~85,000",
    price=430.00, market_cap=2.20e12, low52=266.82, high52=487.47,
    fundamentals=dict(rev=139.5e9, rev_g=32, gm=63.1, opm=50.0, nm=42.0, eps=14.33,
                      pe=30.0, fwd_pe=24.5, ps=15.8, ev_ebitda=22, roic=45, roe=35,
                      fcf=70.0e9, cash=52.0e9, debt=8.0e9, div="3.80 TWD/qtr", divy=0.88),
    segments=[("Leading-edge (3nm/2nm)", 55, "N3, N2, N2P; CoWoS advanced packaging"),
              ("Mature nodes (7nm+)", 30, "N7, N12, N22; automotive, IoT"),
              ("Other (packaging, OSAT)", 15, "CoWoS, SoIC, InFO")],
    biz=("TSMC is the world's #1 foundry at 65% of advanced-node revenue. The 2026 "
         "story is AI capacity: CoWoS (Chip-on-Wafer-on-Substrate) for NVIDIA/AMD is "
         "the #1 bottleneck in the AI supply chain; $265B US fab expansion (2 new "
         "Arizona fabs); 2nm (N2) volume production in Q4 2026. TSMC is the "
         "structural moat of the entire AI chip industry — every NVIDIA, AMD, "
         "Apple, and custom ASIC is printed on TSMC silicon."),
    moat=dict(rating="Wide Moat", score=9.5, pillars=dict(
        network_effects=(7.0, "The foundry ecosystem (ASML EUV, customers, 85k engineers) is a de facto standard; every new node compounds the moat."),
        switching_costs=(9.5, "Re-qualifying a chip on a rival foundry (Samsung) is a 2-year, $500M exercise; 65% of advanced-node customers are TSMC-exclusive."),
        intangibles=(9.0, "20 years of leading-edge process; 15k+ patents; the #1 talent pool in semiconductor manufacturing."),
        cost_advantage=(9.5, "63% gross margin at 3nm vs. 45% for Samsung; CoWoS at 95% yield vs. 80% for Samsung."),
        scale=(10.0, "$139.5B revenue, 65% advanced-node share, $70B FCF — the largest and most profitable foundry in the world."))),
    competitors=[dict(t="SAMSUNG", n="Samsung Foundry", mc=520e9, rev=160e9, pe=12, note="#2 in foundry (10% advanced-node share); 3nm yield 80% vs. TSMC 95%"),
                 dict(t="INTC", n="Intel Foundry (18A)", mc=140e9, rev=55.0e9, pe=35, note="#3 in foundry (5% advanced-node share); 18A yield 80%; 2 external customers"),
                 dict(t="UMC", n="UMC (Taiwan)", mc=30e9, rev=7e9, pe=15, note="#2 in mature nodes; no advanced-node program"),
                 dict(t="ASML", n="ASML", mc=636e9, rev=39.8e9, pe=34, note="Supplier (EUV), not rival — but ASML's capacity is TSMC's #1 bottleneck")],
    edge=("The core edge is YIELD + CAPACITY: TSMC's 3nm/2nm at 95% yield vs. "
          "Samsung's 80% is a structural moat that no capital investment can close "
          "in 5 years. The CoWoS capacity (4x 2025) is the #1 bottleneck in the "
          "AI supply chain — TSMC is the chokepoint of the entire AI industry."),
    sentiment=dict(score=8.5, consensus="Buy", pt=520, pt_lo=380, pt_hi=620, short="0.7% of float"),
    news=[dict(d="2026-10-14", h="Q3: gross margin 63.5%; AI revenue 28% of total; 2026 capex $43B", s="TSMC PR", i="pos"),
          dict(d="2026-09-08", h="Arizona N2 fab reaches volume production; US revenue crosses 15% of total", s="Bloomberg", i="pos"),
          dict(d="2026-08-16", h="TSMC announces $265B 10-year US investment including two new fabs in Arizona", s="Reuters", i="mixed")],
    trends=["2nm (N2): volume production Q4 2026; 30% of advanced-node revenue by 2028",
            "CoWoS: 4x capacity 2025→2026; the #1 AI supply chain bottleneck",
            "US: $265B 10-year investment; 2 new Arizona fabs; 15% of revenue by 2028",
            "AI: 28% of revenue from AI (NVIDIA, AMD, custom ASICs); 40% by 2028"],
    swot=dict(
        s=["65% advanced-node share; 95% yield at 3nm vs. Samsung 80%",
           "CoWoS: 4x capacity; the #1 AI supply chain bottleneck",
           "63% gross margin, $70B FCF — the most profitable foundry in history",
           "$265B US investment; 2 new Arizona fabs; 15% US revenue by 2028"],
        w=["Taiwan: 95% of capacity in Taiwan; geopolitical risk",
           "ASML dependency: 100% of EUV from ASML; 2-year lead time",
           "CoWoS: 4x capacity is still not enough; 2027 bottleneck persists",
           "Mature nodes: 30% of revenue at 40% gross margin (vs. 65% for leading-edge)"],
        o=["2nm: 30% of advanced-node revenue by 2028; $30B/yr",
           "CoWoS: 6x capacity by 2028; $50B/yr",
           "US: 20% of revenue by 2028; $30B/yr at 55% gross margin",
           "AI: 40% of revenue by 2028; $60B/yr"],
        t=["Taiwan: any conflict = -95% of revenue overnight",
           "ASML: EUV lead time 2 years; any delay = -20% capacity",
           "Samsung: 3nm yield catches up to 90%; price war",
           "Macro: AI capex digestion 2027 = -30% orders"]),
    thesis=dict(
        bull=("2nm + CoWoS 6x: $200B revenue by 2028; re-rate to 35x.", 580, 0.30),
        base=("2nm ramp, CoWoS 4x, US 15%; 28x earnings.", 480, 0.50),
        bear=("Taiwan risk, ASML delay, AI digestion; de-rate to 20x.", 300, 0.20)),
    dcf=dict(fcf_ps=13.68, g=0.20, terminal=0.04, rate=0.09, net_cash_ps=8.60)),

# ============================== PALANTIR ===================================
"PLTR": dict(
    name="Palantir Technologies Inc.", sector="Software", industry="AI Data Platform / Defense",
    exchange="NASDAQ", website="palantir.com", employees="~4,500",
    price=205.00, market_cap=502e9, low52=106.37, high52=209.58,
    fundamentals=dict(rev=6.16e9, rev_g=71, gm=84.8, opm=52.0, nm=49.0, eps=1.23,
                      pe=167, fwd_pe=85, ps=81.5, ev_ebitda=120, roic=65, roe=55,
                      fcf=2.5e9, cash=3.5e9, debt=0.5e9, div=None, divy=0.0),
    segments=[("US Government (AIP)", 55, "DoD, CIA, FBI, NATO; Project Titan"),
              ("US Commercial (AIP)", 35, "Energy, healthcare, manufacturing, finance"),
              ("International Government", 10, "UK, Australia, Germany, Japan")],
    biz=("Palantir is the AI data platform for the world's most dangerous and most "
         "valuable problems. The 2026 inflection: GAAP profitability (net income "
         "$3.02B, 49% net margin), commercial +85% YoY, FCF margin 41%, and the "
         "DoD 'Project Titan' contract ($2.4B, 5 years). AIP (Artificial "
         "Intelligence Platform) is the #1 enterprise AI deployment platform "
         "(400+ production deployments). The 167x P/E is the price of being the "
         "only AI company with a government moat + a commercial flywheel."),
    moat=dict(rating="Narrow Moat", score=7.5, pillars=dict(
        network_effects=(7.0, "AIP: every customer deployment makes the ontology more valuable; 400+ production deployments = the largest AI agent network in the enterprise."),
        switching_costs=(9.0, "AIP is embedded in the customer's data ontology; re-platforming is a 12-18 month, $10M+ exercise. Government contracts are 5-10 year."),
        intangibles=(8.0, "Cleared personnel (Top Secret/SCI), 500+ government contracts, AIP IP portfolio, 4,500 employees with the highest AI talent density."),
        cost_advantage=(6.0, "No cost advantage; 84.8% gross margin is the best in enterprise software but R&D is 25% of revenue."),
        scale=(6.5, "$6.16B revenue, 49% net margin, 41% FCF margin — profitable at scale but 1/50 of the #1 AI company (NVDA)."))),
    competitors=[dict(t="MSFT", n="Microsoft (Azure AI)", mc=4.00e12, rev=331.8e9, pe=35, note="Azure AI + Copilot is the #1 enterprise AI platform; but no government clearance"),
                 dict(t="GOOGL", n="Alphabet (Vertex AI)", mc=4.30e12, rev=445.9e9, pe=24, note="GCP + Gemini is #2 in enterprise AI; no government moat"),
                 dict(t="CRM", n="Salesforce (Agentforce)", mc=315e9, rev=35.8e9, pe=24, note="#1 in CRM AI agents; no government clearance"),
                 dict(t="IBM", n="IBM (watsonx)", mc=180e9, rev=55.0e9, pe=22, note="#3 in enterprise AI; no government clearance; 4,500 AIP deployments")],
    edge=("The core edge is GOVERNMENT + AIP: Palantir is the only AI company with "
          "Top Secret/SCI clearance, 500+ government contracts, AND a commercial "
          "AI platform (AIP) at 400+ production deployments. The government moat "
          "is structural: 10-20 year contracts, cleared personnel, and the "
          "ontology that no rival can replicate. The commercial flywheel "
          "(+85% YoY) is the re-rating story."),
    sentiment=dict(score=7.2, consensus="Buy (High Conviction)", pt=280, pt_lo=150, pt_hi=380, short="6.5% of float"),
    news=[dict(d="2026-10-06", h="Q3: revenue $1.9B (+71% YoY); commercial +85%; FCF margin 41%", s="PLTR PR", i="pos"),
          dict(d="2026-09-19", h="PLTR signs 5-year DoD 'Project Titan' data platform contract ($2.4B)", s="Reuters", i="pos"),
          dict(d="2026-08-27", h="AIP Platform launches for commercial finance; 400+ production deployments", s="Bloomberg", i="pos")],
    trends=["AIP: 400+ → 1000+ production deployments by 2028; the #1 enterprise AI platform",
            "Government: Project Titan ($2.4B) + 500+ contracts; 55% of revenue",
            "Commercial: +85% YoY; 35% of revenue; the re-rating story",
            "FCF: 41% margin; $2.5B FCF; the #1 profitable AI company by margin"],
    swot=dict(
        s=["GAAP profitable: $3.02B net income, 49% net margin, 41% FCF margin",
           "Government moat: 500+ contracts, Top Secret/SCI clearance, 10-20 year terms",
           "AIP: 400+ production deployments; the #1 enterprise AI platform",
           "Commercial +85% YoY; 35% of revenue; the re-rating story"],
        w=["Valuation: 167x P/E, 81x P/S — priced for perfection",
           "6.5% short interest — the highest in the S&P 500",
           "Customer concentration: DoD = 40% of revenue",
           "4,500 employees: R&D is 25% of revenue; talent is the #1 bottleneck"],
        o=["AIP: 1000+ deployments by 2028; $10B/yr",
           "Government: $5B/yr by 2028; NATO + 10 new countries",
           "Commercial: 50% of revenue by 2028; $5B/yr",
           "International: 10% → 20% by 2028; $2B/yr"],
        t=["Valuation: any growth miss = -30% overnight",
           "MSFT/GOOGL: enterprise AI competition; AIP share drops to 30%",
           "Government: budget cuts; -20% DoD spending",
           "Macro: enterprise AI digestion 2027"]),
    thesis=dict(
        bull=("AIP 1000+ deployments, commercial 50%: $15B revenue, 50% FCF margin; 100x earnings.", 380, 0.25),
        base=("AIP 700, commercial 40%, government 50%; 80x earnings.", 270, 0.50),
        bear=("Growth miss, MSFT/GOOGL competition, budget cuts; de-rate to 40x.", 130, 0.25)),
    dcf=dict(fcf_ps=1.02, g=0.40, terminal=0.04, rate=0.105, net_cash_ps=1.23)),

# ============================== SPACEX =====================================
"SPCX": dict(
    name="Space Exploration Technologies Corp.", sector="Technology", industry="Space / Starlink / xAI",
    exchange="NASDAQ (IPO June 2026)", website="spacex.com", employees="~12,000",
    price=152.16, market_cap=2.10e12, low52=104.83, high52=225.64,
    fundamentals=dict(rev=23.0e9, rev_g=45, gm=52.0, opm=18.0, nm=11.0, eps=0.18,
                      pe=845, fwd_pe=320, ps=91.3, ev_ebitda=280, roic=15, roe=12,
                      fcf=1.2e9, cash=8.0e9, debt=5.0e9, div=None, divy=0.0),
    segments=[("Starlink", 55, "90M subs, direct-to-cell, broadband"),
              ("Launch Services", 25, "Falcon 9 Mk5, Starship"),
              ("xAI (merged Feb 2026)", 20, "Grok 5, Starlink edge inference")],
    biz=("SpaceX is the world's #1 launch company (80% of global launch mass) and "
         "the #1 satellite broadband operator (Starlink: 90M subs, $45B/yr "
         "run-rate). The Feb 2026 xAI merger adds Grok 5 + edge AI inference on "
         "Starlink. The June 2026 IPO at $104.83 (52-week low) raised $75B. The "
         "845x P/E is the price of being the only company with a reusable rocket, "
         "a satellite mega-constellation, AND an AI model (Grok) running on the "
         "satellites themselves."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(8.0, "Starlink: 90M subs; more users = more revenue = more satellites = better service. The #1 satellite broadband network on earth."),
        switching_costs=(7.5, "Starlink: 2-year contract; enterprise/government contracts are 5-10 year. Re-launching a rival constellation is a 5-year, $50B exercise."),
        intangibles=(9.0, "Falcon 9 Mk5 (10 launches/week), Starship (orbital refueling), Grok 5 (xAI), 5,000+ patents — the most advanced space program in history."),
        cost_advantage=(10.0, "Falcon 9: $1,500/kg to LEO vs. $10,000 for rivals. Starship: $100/kg (target). No rival can match this cost curve."),
        scale=(9.0, "80% of global launch mass, 90M Starlink subs, 12,000 employees — the largest private space company in history."))),
    competitors=[dict(t="RKLB", n="Rocket Lab", mc=12e9, rev=0.8e9, pe=200, note="#2 in small satellite launch; Neutron is 18 months behind Falcon 9"),
                 dict(t="AMZN", n="Amazon (Kuiper)", mc=2.70e12, rev=775.7e9, pe=29, note="#2 in satellite broadband (1,000 subs vs. Starlink 90M); 3-year delay"),
                 dict(t="GOOGL", n="Alphabet (Project Suncatcher)", mc=4.30e12, rev=445.9e9, pe=24, note="Solar-powered satellite compute; 5-year horizon; no launch vehicle"),
                 dict(t="ULA", n="United Launch Alliance", mc=8e9, rev=3.5e9, pe=15, note="#2 in US government launch; no reusability; 20 launches/yr vs. SpaceX 140")],
    edge=("The core edge is LAUNCH COST + STARLINK: SpaceX's $1,500/kg to LEO "
          "(vs. $10,000 for rivals) is a 7x cost advantage that no capital "
          "investment can close in 5 years. Starlink (90M subs) is the #1 "
          "satellite broadband network; the xAI merger adds Grok 5 + edge AI "
          "inference on the satellites themselves — a vertical integration "
          "no rival can match."),
    sentiment=dict(score=7.5, consensus="Buy (Post-IPO)", pt=200, pt_lo=120, pt_hi=300, short="3.8% of float"),
    news=[dict(d="2026-10-11", h="Starlink crosses 90M subs; revenue run-rate $45B/yr; direct-to-cell live in 12 countries", s="SpaceX PR", i="pos"),
          dict(d="2026-09-23", h="SpaceX–xAI combined: Grok 5 + Starlink edge inference announced; 10,000 edge nodes", s="Reuters", i="pos"),
          dict(d="2026-08-10", h="Falcon 9 Mk5 cadence: 10 launches in week 33, all-time record; 140 launches in 2026", s="Bloomberg", i="pos")],
    trends=["Starlink: 90M → 150M subs by 2028; $100B/yr revenue",
            "Starship: 2027 orbital refueling; $100/kg to LEO; the #1 launch vehicle in history",
            "xAI: Grok 5 + 10,000 edge inference nodes on Starlink",
            "Direct-to-cell: 12 → 50 countries by 2028; $10B/yr"],
    swot=dict(
        s=["Falcon 9 Mk5: $1,500/kg to LEO; 7x cost advantage over rivals",
           "Starlink: 90M subs; $45B/yr run-rate; the #1 satellite broadband network",
           "Starship: 2027 orbital refueling; $100/kg target",
           "xAI: Grok 5 + 10,000 edge inference nodes on Starlink"],
        w=["845x P/E — the highest valuation in the S&P 500",
           "12,000 employees: labor cost is 30% of revenue",
           "Starship: 2027 orbital refueling is unproven; 3-year delay risk",
           "IPO lockup: 30% of shares unlock Dec 2026; -20% sell-off risk"],
        o=["Starlink: 150M subs by 2028; $100B/yr revenue",
           "Starship: $100/kg to LEO; $50B/yr launch revenue by 2030",
           "Direct-to-cell: 50 countries by 2028; $10B/yr",
           "xAI: Grok 5 + edge AI = $20B/yr by 2028"],
        t=["IPO lockup: 30% of shares unlock Dec 2026; -20% sell-off",
           "Kuiper: Amazon catches up in 3 years; Starlink share drops to 70%",
           "Regulatory: FCC + ITU spectrum allocation; 10,000 satellite cap",
           "Macro: post-IPO digestion; -30% in 2027"]),
    thesis=dict(
        bull=("Starship + Starlink 150M: $100B revenue, $20B FCF by 2028; 300x earnings.", 300, 0.25),
        base=("Starlink 120M, Starship 2028, Grok 5; 150x earnings.", 200, 0.50),
        bear=("IPO lockup, Kuiper, Starship delay; de-rate to 80x.", 90, 0.25)),
    dcf=dict(fcf_ps=0.09, g=0.30, terminal=0.04, rate=0.11, net_cash_ps=0.22)),

# ============================== BABA =======================================
"BABA": dict(
    name="Alibaba Group Holding Ltd.", sector="Consumer Discretionary", industry="E-commerce / Cloud / AI",
    exchange="NYSE (ADR)", website="alibabagroup.com", employees="~210,000",
    price=132.00, market_cap=355e9, low52=78.00, high52=158.00,
    fundamentals=dict(rev=98.0e9, rev_g=22, gm=38.0, opm=18.0, nm=14.0, eps=10.98,
                      pe=12.0, fwd_pe=10.5, ps=3.6, ev_ebitda=11, roic=15, roe=12,
                      fcf=30.0e9, cash=220.0e9, debt=25.0e9, div=None, divy=0.0),
    segments=[("Taobao/Tmall (China e-commerce)", 45, "China retail + marketplace"),
              ("Cloud + AI (Aliyun)", 25, "Alibaba Cloud + Qwen models"),
              ("International (Lazada, AliExpress)", 15, "SEA + Europe + LatAm"),
              ("Logistics (Cainiao)", 8, "5-day global delivery"),
              ("Local Services (Ele.me, Fliggy)", 7, "Food delivery + travel")],
    biz=("Alibaba is China's #1 e-commerce + cloud company. The 2026 story is "
         "AI + Cloud: Qwen-3.5 (open weights) has 20M downloads in 30 days, "
         "cloud revenue +26% YoY with AI products tripling for the 7th straight "
         "quarter, and a $52B AI infrastructure investment over 3 years. The "
         "12x P/E is the price of China risk + the option value of being the "
         "only Chinese company with a global cloud + AI stack."),
    moat=dict(rating="Narrow Moat", score=7.0, pillars=dict(
        network_effects=(8.0, "Taobao/Tmall: 1B+ annual active consumers; 9M+ sellers; the largest e-commerce network in China."),
        switching_costs=(7.0, "Cainiao logistics + Aliyun cloud + Qwen models = a 3-year lock-in for enterprise customers."),
        intangibles=(7.5, "Qwen-3.5: the #1 open-weights model in China; 20M downloads; 500+ enterprise deployments."),
        cost_advantage=(7.5, "Aliyun: 30% lower $/token than rivals in China; $52B AI capex gives 2x the capacity of Tencent Cloud."),
        scale=(8.5, "$98B revenue, 210k employees, 1B+ consumers, 9M+ sellers — the largest Chinese tech company."))),
    competitors=[dict(t="TCEHY", n="Tencent (SEA)", mc=680e9, rev=130e9, pe=20, note="#1 in China social + gaming; #2 in cloud; WeChat is the #1 messaging app"),
                 dict(t="JD", n="JD.com", mc=95e9, rev=160e9, pe=10, note="#2 in China e-commerce; 1P model (vs. Alibaba's 3P); 5-day delivery"),
                 dict(t="PDD", n="Pinduoduo (Temu)", mc=180e9, rev=100e9, pe=15, note="#3 in China e-commerce; Temu is the #1 US marketplace rival"),
                 dict(t="AMZN", n="Amazon", mc=2.70e12, rev=775.7e9, pe=29, note="#1 in global e-commerce; no China presence; but AliExpress is a niche")],
    edge=("The core edge is CHINA SCALE + AI: Alibaba is the only Chinese company "
          "with a 1B+ consumer network, a global cloud (Aliyun: #1 in China, "
          "#3 in APAC), AND an open-weights AI model (Qwen-3.5: 20M downloads). "
          "The 12x P/E is the price of China risk — but the option value of "
          "being the only Chinese AI + cloud company is the re-rating story."),
    sentiment=dict(score=6.5, consensus="Buy (Value)", pt=180, pt_lo=110, pt_hi=250, short="2.5% of float"),
    news=[dict(d="2026-10-15", h="FY26 Q2: cloud revenue +26% YoY; AI products tripled for 7th straight quarter", s="BABA PR", i="pos"),
          dict(d="2026-09-09", h="Alibaba commits to $52B AI infrastructure over 3 years; 10 new data centers", s="Bloomberg", i="mixed"),
          dict(d="2026-08-18", h="Qwen-3.5 open weights released; 20M downloads in 30 days; 500+ enterprise deployments", s="Reuters", i="pos")],
    trends=["Qwen-3.5: the #1 open-weights model in China; 500+ enterprise deployments",
            "Cloud: +26% YoY; AI products tripling; $52B 3-year capex",
            "International: Temu + AliExpress = 30% of revenue by 2028",
            "Buybacks: $25B/yr at 12x P/E = 7% shareholder yield"],
    swot=dict(
        s=["1B+ consumers, 9M+ sellers — the largest e-commerce network in China",
           "Qwen-3.5: the #1 open-weights model; 20M downloads; 500+ enterprise deployments",
           "Aliyun: #1 in China cloud; 30% lower $/token than rivals",
           "12x P/E + 7% buyback yield — the cheapest large-cap tech in the world"],
        w=["China risk: 40% of revenue in China; regulatory + geopolitical",
           "Temu: PDD is the #1 US marketplace rival; -15% international revenue",
           "Cloud: 15% market share in APAC; 2x behind AWS in Asia",
           "210k employees: labor cost is 25% of revenue"],
        o=["Qwen: 1000+ enterprise deployments by 2028; $10B/yr",
           "Cloud: 25% of revenue by 2028; $30B/yr",
           "International: 30% of revenue by 2028; $30B/yr",
           "Buybacks: $25B/yr at 12x = 7% shareholder yield"],
        t=["China: regulatory + geopolitical; -20% of market cap overnight",
           "Tencent: WeChat + cloud; 20% of Alibaba's revenue at risk",
           "PDD: Temu + 1P model; 30% of international revenue at risk",
           "Macro: China recession; -15% e-commerce revenue"]),
    thesis=dict(
        bull=("Qwen + Cloud: $50B cloud revenue, 20% net margin; re-rate to 20x.", 250, 0.25),
        base=("Cloud +25%, e-commerce +10%, buybacks; 14x earnings.", 160, 0.50),
        bear=("China risk, PDD, cloud slowdown; de-rate to 8x.", 80, 0.25)),
    dcf=dict(fcf_ps=11.15, g=0.15, terminal=0.035, rate=0.10, net_cash_ps=72.51)),

# ============================== NETFLIX =====================================
"NFLX": dict(
    name="Netflix, Inc.", sector="Communication Services", industry="Streaming / Content / Ads",
    exchange="NASDAQ", website="netflix.com", employees="~14,000",
    price=980.00, market_cap=360e9, low52=680.00, high52=1050.00,
    fundamentals=dict(rev=40.0e9, rev_g=16, gm=45.0, opm=35.0, nm=28.0, eps=24.50,
                      pe=40.0, fwd_pe=32.0, ps=9.0, ev_ebitda=24, roic=45, roe=65,
                      fcf=14.0e9, cash=8.0e9, debt=14.0e9, div=None, divy=0.0),
    segments=[("Subscription (ad-free)", 55, "322M subs, $12.99/mo avg"),
              ("Subscription (ad-supported)", 30, "30M subs, $7.99/mo"),
              ("Ads", 15, "30M ad-tier subs; $3.1B/qtr")],
    biz=("Netflix is the world's #1 streaming service at 322M subs and $40B "
         "revenue. The 2026 story is ads + DTC: the ad-supported tier (30M subs) "
         "is the margin-accretive growth engine ($3.1B/qtr), DTC sports (MLS) "
         "is the #1 live event property, and the 2027 content spend ($18B, "
         "record) is the investment in the next supercycle. The 40x P/E is the "
         "price of being the only streaming company with a 320M+ sub base AND "
         "a profitable ad business."),
    moat=dict(rating="Wide Moat", score=8.0, pillars=dict(
        network_effects=(7.5, "322M subs; more subs = more content spend = better catalog = more subs. The #1 streaming network on earth."),
        switching_costs=(6.0, "Streaming is low-switching (cancel anytime) but high-attention; Netflix is the default for 80% of streaming time."),
        intangibles=(8.5, "Netflix brand + 4,000+ hours of original content; the #1 content library in streaming; 2x the #2 (Disney)."),
        cost_advantage=(7.0, "Content: $16B/yr at 322M subs = $50/sub/yr vs. $80 for Disney; scale + ad revenue (30% of cost)."),
        scale=(9.0, "322M subs, $40B revenue, $14B FCF — the largest streaming company in the world."))),
    competitors=[dict(t="DIS", n="Disney (Hulu/Disney+)", mc=190e9, rev=80e9, pe=14, note="#2 in streaming (120M subs); DTC is 50% smaller than Netflix"),
                 dict(t="AMZN", n="Amazon (Prime Video)", mc=2.70e12, rev=775.7e9, pe=29, note="#3 in streaming (200M Prime subs); but 50% are bundled, not standalone"),
                 dict(t="WBD", n="Warner Bros. Discovery (Max)", mc=25e9, rev=35e9, pe=12, note="#4 in streaming (80M subs); 1/4 the scale of Netflix"),
                 dict(t="SPOT", n="Spotify (video)", mc=140e9, rev=18e9, pe=35, note="#1 in audio; video is a niche (30M subs) but the #1 ad rival")],
    edge=("The core edge is CONTENT + SCALE: Netflix's $16B/yr content spend at "
          "322M subs is the most efficient in the industry ($50/sub/yr vs. $80 "
          "for Disney). The 30M ad-tier subs ($3.1B/qtr) is the margin-accretive "
          "growth engine that no rival has at scale. The moat is the 20-year "
          "content library + the 322M sub base that no rival can match without "
          "5 years and $100B of content spend."),
    sentiment=dict(score=7.8, consensus="Buy", pt=1200, pt_lo=850, pt_hi=1500, short="2.0% of float"),
    news=[dict(d="2026-10-07", h="Q3: 322M subs; ad revenue $3.1B/qtr; DTC sports (MLS) a hit with 50M+ viewers", s="NFLX PR", i="pos"),
          dict(d="2026-09-21", h="Netflix hits 30M paid ad-tier subs; ad revenue +45% YoY", s="Bloomberg", i="pos"),
          dict(d="2026-08-22", h="New 2027 content spend $18B, record; 200+ original titles", s="Reuters", i="mixed")],
    trends=["Ads: 30M ad-tier subs → 50M by 2028; $15B/yr ad revenue",
            "DTC: MLS + 10 new sports deals; $5B/yr by 2028",
            "Content: $18B 2027 spend; 40% international; the next supercycle",
            "Gaming: 200+ titles; 50M players; the #1 streaming game library"],
    swot=dict(
        s=["322M subs; the #1 streaming company in the world",
           "Ads: 30M ad-tier subs; $3.1B/qtr; +45% YoY",
           "$16B/yr content spend at 322M subs = $50/sub/yr (most efficient)",
           "$14B FCF, net-cash balance sheet, 40% ROIC"],
        w=["40x P/E is 2x the 5-yr average; priced for ad + DTC to deliver",
           "$18B 2027 content spend = 45% of revenue; FCF pressure",
           "International: 50% of subs at 60% lower ARPU",
           "Content: $18B/yr is a 20% investment in a 5-year supercycle"],
        o=["Ads: 50M ad-tier subs by 2028; $15B/yr",
           "DTC: $5B/yr by 2028; 10 new sports deals",
           "International: 60% of subs by 2028; 30% ARPU growth",
           "Gaming: 50M players; $5B/yr by 2028"],
        t=["Disney: 200M subs by 2028; -15% Netflix share",
           "Amazon: Prime Video at 300M subs; -20% standalone revenue",
           "Content: $18B/yr miss = -30% overnight",
           "Macro: streaming recession; -10% churn"]),
    thesis=dict(
        bull=("Ads + DTC: $60B revenue, 35% net margin; re-rate to 45x.", 1400, 0.25),
        base=("Ads +30%, DTC +50%, content $18B; 35x earnings.", 1100, 0.55),
        bear=("Content miss, Disney/Amazon, churn; de-rate to 25x.", 700, 0.20)),
    dcf=dict(fcf_ps=38.11, g=0.15, terminal=0.04, rate=0.095, net_cash_ps=-16.33)),

# ============================== SALESFORCE =================================
"CRM": dict(
    name="Salesforce, Inc.", sector="Software", industry="CRM / AI Agents",
    exchange="NYSE", website="salesforce.com", employees="~74,000",
    price=240.00, market_cap=315e9, low52=165.00, high52=285.00,
    fundamentals=dict(rev=35.8e9, rev_g=13, gm=77.0, opm=28.0, nm=22.0, eps=10.00,
                      pe=24.0, fwd_pe=19.5, ps=8.8, ev_ebitda=18, roic=35, roe=28,
                      fcf=9.0e9, cash=12.0e9, debt=18.0e9, div="0.45 USD/qtr", divy=0.75),
    segments=[("Platform (Sales Cloud, Service Cloud)", 55, "CRM + AI agents"),
              ("Agentforce", 20, "AI agent platform; $2B ARR"),
              ("Tableau + Mulesoft", 15, "Analytics + integration"),
              ("Other (Work.com, Slack)", 10, "Collaboration + identity")],
    biz=("Salesforce is the #1 CRM platform at $35.8B revenue and 150k+ "
         "enterprise customers. The 2026 story is Agentforce: the AI agent "
         "platform has $2B ARR (launched Feb 2026), handles 80% of SDR tasks "
         "at top-100 accounts, and is the #1 enterprise AI agent deployment "
         "platform (200+ production deployments). The 24x P/E is the cheapest "
         "in the enterprise AI complex — the re-rating story is Agentforce "
         "going from $2B to $10B ARR by 2028."),
    moat=dict(rating="Wide Moat", score=8.0, pillars=dict(
        network_effects=(8.0, "150k+ enterprise customers; 10M+ daily users; the CRM data graph makes Agentforce more valuable with every deployment."),
        switching_costs=(9.5, "CRM is a 10-20 year system of record; re-platforming is a 2-3 year, $50M+ exercise. Agentforce is embedded in the CRM ontology."),
        intangibles=(8.0, "Salesforce brand + 30k+ patents + Agentforce IP; the #1 enterprise AI agent platform."),
        cost_advantage=(6.5, "No cost advantage; 77% gross margin is best-in-class but R&D is 20% of revenue."),
        scale=(8.5, "$35.8B revenue, 150k+ customers, 74k employees — the #1 CRM platform in the world."))),
    competitors=[dict(t="ADP", n="ADP (Workforce Cloud)", mc=180e9, rev=14e9, pe=30, note="#1 in HR; no CRM overlap; but Agentforce competes for the same AI budget"),
                 dict(t="NOW", n="ServiceNow", mc=135e9, rev=10.5e9, pe=25, note="#1 in IT service management; Agentforce + Now Assist = the #1 AI agent rivalry"),
                 dict(t="MSFT", n="Microsoft (Dynamics 365)", mc=4.00e12, rev=331.8e9, pe=35, note="#2 in CRM (Dynamics); but M365 + Copilot is the #1 enterprise AI platform"),
                 dict(t="SIE", n="Siemens (Industry X)", mc=140e9, rev=32e9, pe=17, note="#1 in industrial software; no CRM overlap")],
    edge=("The core edge is CRM DATA + AGENTS: Salesforce is the only company "
          "with a 10-20 year CRM data graph (150k+ customers, 10M+ daily users) "
          "AND an AI agent platform (Agentforce: $2B ARR, 200+ production "
          "deployments). The moat is the data: every customer interaction makes "
          "the agent smarter. Rivals can build the agent; none can match the data."),
    sentiment=dict(score=7.2, consensus="Buy", pt=320, pt_lo=220, pt_hi=400, short="1.5% of float"),
    news=[dict(d="2026-10-13", h="Q4 FY26: revenue $10.2B (+13%); Agentforce $2B ARR; 200+ production deployments", s="CRM PR", i="pos"),
          dict(d="2026-09-08", h="Salesforce acquires AI coding startup for $2B; Agentforce + GitHub Copilot integration", s="Bloomberg", i="pos"),
          dict(d="2026-08-15", h="Agentforce: 80% of SDR tasks automated at top-100 accounts; $1.5B/yr customer savings", s="Reuters", i="pos")],
    trends=["Agentforce: $2B → $10B ARR by 2028; the #1 enterprise AI agent platform",
            "Platform: $35.8B revenue at 77% gross margin; 30% of revenue from AI",
            "Data: 150k+ customers; 10M+ daily users; the #1 CRM data graph",
            "International: 35% of revenue; 50% by 2028"],
    swot=dict(
        s=["#1 CRM: 150k+ customers, 10M+ daily users, 77% gross margin",
           "Agentforce: $2B ARR, 200+ production deployments, 80% SDR task automation",
           "10-20 year customer lock-in; 2-3 year, $50M+ switching cost",
           "$9B FCF, 24x P/E — the cheapest in the enterprise AI complex"],
        w=["Agentforce: $2B ARR is 5% of revenue; the re-rating story is unproven",
           "MSFT: Dynamics + Copilot is the #1 enterprise AI rival",
           "R&D: 20% of revenue; 20k+ engineers; the #1 cost line",
           "Debt: $18B (from Slack acquisition); 1.5x net debt/EBITDA"],
        o=["Agentforce: $10B ARR by 2028; 30% of revenue",
           "Platform: $50B revenue by 2028; 80% gross margin",
           "International: 50% of revenue by 2028; $20B/yr",
           "Data: 200k+ customers by 2028; 15M+ daily users"],
        t=["MSFT: Dynamics + Copilot; -20% of CRM revenue",
           "Agentforce: if adoption misses, -30% overnight (40x → 20x)",
           "NOW: Now Assist + IT service management; -15% of Agentforce revenue",
           "Macro: enterprise AI digestion 2027"]),
    thesis=dict(
        bull=("Agentforce $10B ARR, platform $50B: re-rate to 30x.", 380, 0.25),
        base=("Agentforce $5B, platform +12%; 22x earnings.", 300, 0.55),
        bear=("Agentforce miss, MSFT, macro; de-rate to 15x.", 180, 0.20)),
    dcf=dict(fcf_ps=6.86, g=0.14, terminal=0.035, rate=0.09, net_cash_ps=-4.57)),

# ============================== SERVICENOW =================================
"NOW": dict(
    name="ServiceNow, Inc.", sector="Software", industry="IT Service Management / AI",
    exchange="NYSE", website="servicenow.com", employees="~16,000",
    price=950.00, market_cap=135e9, low52=650.00, high52=1050.00,
    fundamentals=dict(rev=10.5e9, rev_g=22, gm=80.0, opm=35.0, nm=30.0, eps=3.25,
                      pe=25.0, fwd_pe=20.0, ps=12.9, ev_ebitda=17, roic=45, roe=38,
                      fcf=4.5e9, cash=8.0e9, debt=15.0e9, div=None, divy=0.0),
    segments=[("IT Service Management", 45, "Now Platform + AI agents"),
              ("HR/CRM/Workday", 30, "Employee + customer service"),
              ("AI Agents (Now Assist)", 25, "Digital workers; 1.2B sessions")],
    biz=("ServiceNow is the #1 IT service management platform at $10.5B revenue "
         "and 9,000+ enterprise customers. The 2026 story is Now Assist: the "
         "AI agent platform has 1.2B sessions, handles 40% of Tier-1 IT service "
         "requests for enterprise, and is the #1 'digital worker' deployment "
         "platform. The 25x P/E is the cheapest in the enterprise AI complex "
         "(vs. 40x for PLTR, 35x for MSFT)."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(8.5, "Now Platform: 1.2B AI sessions; every deployment makes the agent more valuable; 9,000+ enterprise customers = the #1 AI agent network."),
        switching_costs=(9.5, "ITSM is a 10-20 year system of record; re-platforming is a 2-3 year, $50M+ exercise. Now Assist is embedded in the Now Platform ontology."),
        intangibles=(8.5, "ServiceNow brand + 20k+ patents + Now Assist IP; the #1 ITSM + AI agent platform."),
        cost_advantage=(6.0, "No cost advantage; 80% gross margin is best-in-class but R&D is 25% of revenue."),
        scale=(8.0, "$10.5B revenue, 9,000+ customers, 16k employees — the #1 ITSM platform in the world."))),
    competitors=[dict(t="CRM", n="Salesforce", mc=315e9, rev=35.8e9, pe=24, note="#1 in CRM; Agentforce is the #1 AI agent rival"),
                 dict(t="MSFT", n="Microsoft (Copilot)", mc=4.00e12, rev=331.8e9, pe=35, note="#1 in enterprise AI; M365 + Copilot is the #1 platform"),
                 dict(t="SIE", n="Siemens (Industry X)", mc=140e9, rev=32e9, pe=17, note="#1 in industrial ITSM; no AI agent platform"),
                 dict(t="HPE", n="Hewlett Packard", mc=80e9, rev=35e9, pe=20, note="#2 in IT infrastructure; no AI agent platform")],
    edge=("The core edge is ITSM DATA + DIGITAL WORKERS: ServiceNow is the only "
          "company with a 10-20 year ITSM data graph (9,000+ customers, 1.2B "
          "AI sessions) AND a 'digital worker' platform (Now Assist: 40% of "
          "Tier-1 IT requests). The moat is the data: every IT ticket makes the "
          "agent smarter. Rivals can build the agent; none can match the data."),
    sentiment=dict(score=7.5, consensus="Buy", pt=1200, pt_lo=850, pt_hi=1500, short="1.2% of float"),
    news=[dict(d="2026-10-08", h="Q3 FY26: Now Assist digital workers cross 1.2B sessions; RPO +19%", s="NOW PR", i="pos"),
          dict(d="2026-09-02", h="Now Assist agents handle 40% of Tier-1 IT service requests for enterprise", s="Bloomberg", i="pos"),
          dict(d="2026-08-11", h="Now Platform expands to financial services risk agents; 500+ deployments", s="Reuters", i="pos")],
    trends=["Now Assist: 1.2B sessions; 40% of Tier-1 IT requests; the #1 digital worker platform",
            "Platform: $10.5B revenue at 80% gross margin; 30% from AI",
            "Data: 9,000+ customers; 1.2B sessions; the #1 ITSM data graph",
            "International: 40% of revenue; 50% by 2028"],
    swot=dict(
        s=["#1 ITSM: 9,000+ customers, 1.2B AI sessions, 80% gross margin",
           "Now Assist: 40% of Tier-1 IT requests; the #1 digital worker platform",
           "10-20 year customer lock-in; 2-3 year, $50M+ switching cost",
           "25x P/E — the cheapest in the enterprise AI complex"],
        w=["Now Assist: 25% of revenue; the re-rating story is unproven",
           "MSFT: Copilot + M365 is the #1 enterprise AI rival",
           "R&D: 25% of revenue; 4k+ engineers; the #1 cost line",
           "Debt: $15B (from acquisitions); 1.2x net debt/EBITDA"],
        o=["Now Assist: 50% of revenue by 2028; $10B/yr",
           "Platform: $15B revenue by 2028; 82% gross margin",
           "International: 50% of revenue by 2028; $7.5B/yr",
           "Data: 12,000+ customers by 2028; 2B+ sessions"],
        t=["MSFT: Copilot + M365; -20% of Now Assist revenue",
           "CRM: Agentforce + CRM; -15% of Now Assist revenue",
           "Macro: enterprise AI digestion 2027",
           "Valuation: any growth miss = -30% overnight"]),
    thesis=dict(
        bull=("Now Assist 50%, platform $15B: re-rate to 30x.", 1400, 0.25),
        base=("Now Assist 35%, platform +20%; 25x earnings.", 1150, 0.55),
        bear=("Now Assist miss, MSFT, macro; de-rate to 15x.", 650, 0.20)),
    dcf=dict(fcf_ps=31.67, g=0.16, terminal=0.035, rate=0.09, net_cash_ps=-49.26)),

# ============================== SHOPIFY ====================================
"SHOP": dict(
    name="Shopify Inc.", sector="Software", industry="E-commerce Platform",
    exchange="NYSE", website="shopify.com", employees="~11,000",
    price=135.00, market_cap=200e9, low52=85.00, high52=165.00,
    currency="USD", price_note="Listed in CAD; USD-equivalent",
    fundamentals=dict(rev=7.3e9, rev_g=32, gm=55.0, opm=28.0, nm=18.0, eps=4.56,
                      pe=45.0, fwd_pe=35.0, ps=27.4, ev_ebitda=28, roic=35, roe=25,
                      fcf=1.3e9, cash=6.0e9, debt=8.0e9, div=None, divy=0.0),
    segments=[("Merchandising (subscriptions + transactions)", 55, "22M merchants"),
              ("Shop Pay (payments)", 25, "Top-3 US checkout"),
              ("Logistics (Shopify Fulfillment)", 20, "2M sq ft warehouse")],
    biz=("Shopify is the #1 independent e-commerce platform at 22M merchants and "
         "$7.3B revenue. The 2026 story is AI + payments: Sidekick AI agent "
         "handles 25% of merchant chat, Shop Pay is the #3 US checkout (15% "
         "market share), and Shopify Fulfillment (2M sq ft) is the logistics "
         "moat. The 45x P/E is the price of being the #1 SMB e-commerce "
         "platform with a 32% growth rate AND a payments flywheel."),
    moat=dict(rating="Narrow Moat", score=7.5, pillars=dict(
        network_effects=(8.0, "22M merchants; more merchants = more Shop Pay volume = better pricing = more merchants. The #1 SMB e-commerce network."),
        switching_costs=(7.5, "Shopify: 12-24 month integration; Shop Pay data + Fulfillment = a 3-year lock-in for mid-market merchants."),
        intangibles=(7.5, "Shopify brand + 10k+ patents + Sidekick AI; the #1 SMB e-commerce platform."),
        cost_advantage=(7.0, "Shop Pay: 2.9% fee vs. Stripe 2.7% + 30 cents; 2M sq ft Fulfillment = 20% lower logistics cost."),
        scale=(8.0, "22M merchants, $7.3B revenue, 11k employees — the #1 independent e-commerce platform."))),
    competitors=[dict(t="AMZN", n="Amazon (Seller Central)", mc=2.70e12, rev=775.7e9, pe=29, note="#1 in e-commerce; but Amazon is a rival (1P) AND a platform (3P)"),
                 dict(t="Ebay", n="eBay", mc=40e9, rev=10e9, pe=22, note="#2 in marketplace; 180M active buyers; no e-commerce platform"),
                 dict(t="WCOM", n="Wix (e-commerce)", mc=20e9, rev=2.5e9, pe=35, note="#2 in website builder; 200M merchants; no payments flywheel"),
                 dict(t="STRIPE", n="Stripe (payments)", mc=90e9, rev=5e9, pe=45, note="#1 in payments; 2.7% fee; no e-commerce platform")],
    edge=("The core edge is SMB SCALE + PAYMENTS: Shopify is the only company "
          "with 22M merchants, a #3 US checkout (Shop Pay: 15% market share), "
          "AND a logistics network (2M sq ft). The moat is the payments "
          "flywheel: every merchant transaction makes Shop Pay better, which "
          "makes Shopify stickier, which makes more merchants choose Shopify. "
          "Rivals can build the platform; none can match the payments data."),
    sentiment=dict(score=7.0, consensus="Buy", pt=180, pt_lo=110, pt_hi=250, short="2.2% of float"),
    news=[dict(d="2026-10-12", h="Q3: GMV +29%; 22M merchants; Shop Pay 15% US market share", s="SHOP PR", i="pos"),
          dict(d="2026-09-17", h="Sidekick AI agent handles 25% of merchant chat; 1M+ merchants using AI", s="Bloomberg", i="pos"),
          dict(d="2026-08-29", h="Shop Pay becomes top-3 US checkout; 15% market share (vs. 10% in 2024)", s="Reuters", i="pos")],
    trends=["Shop Pay: 15% → 25% US checkout share by 2028; $5B/yr",
            "Sidekick: 25% → 50% merchant chat by 2028; $2B/yr",
            "Fulfillment: 2M → 5M sq ft by 2028; $3B/yr",
            "International: 40% of GMV; 50% by 2028"],
    swot=dict(
        s=["22M merchants; the #1 independent e-commerce platform",
           "Shop Pay: 15% US checkout share; the payments flywheel",
           "Sidekick AI: 25% of merchant chat; 1M+ merchants",
           "2M sq ft Fulfillment; 20% lower logistics cost"],
        w=["45x P/E is 2x the 5-yr average; priced for AI + payments to deliver",
           "Amazon: 1P + 3P; -20% of Shopify's merchant base",
           "R&D: 20% of revenue; 3k+ engineers; the #1 cost line",
           "Debt: $8B (from acquisitions); 1.5x net debt/EBITDA"],
        o=["Shop Pay: 25% US checkout share by 2028; $5B/yr",
           "Sidekick: 50% of merchant chat by 2028; $2B/yr",
           "Fulfillment: 5M sq ft by 2028; $3B/yr",
           "International: 50% of GMV by 2028; $5B/yr"],
        t=["Amazon: -20% of merchant base; -30% of GMV",
           "Stripe: 2.7% fee; -15% of Shop Pay revenue",
           "Macro: SMB recession; -15% of merchant base",
           "Valuation: any growth miss = -30% overnight"]),
    thesis=dict(
        bull=("Shop Pay 25%, Sidekick 50%, Fulfillment 5M: re-rate to 55x.", 250, 0.25),
        base=("Shop Pay 20%, Sidekick 35%, GMV +25%; 40x earnings.", 180, 0.55),
        bear=("Amazon, Stripe, SMB recession; de-rate to 25x.", 100, 0.20)),
    dcf=dict(fcf_ps=0.88, g=0.22, terminal=0.04, rate=0.095, net_cash_ps=-1.35)),

# ============================== COINBASE ===================================
"COIN": dict(
    name="Coinbase Global, Inc.", sector="Financials", industry="Crypto Exchange / Infrastructure",
    exchange="NASDAQ", website="coinbase.com", employees="~4,500",
    price=285.00, market_cap=62e9, low52=145.00, high52=385.00,
    fundamentals=dict(rev=4.1e9, rev_g=55, gm=45.0, opm=28.0, nm=22.0, eps=19.00,
                      pe=15.0, fwd_pe=12.0, ps=15.1, ev_ebitda=11, roic=40, roe=35,
                      fcf=0.9e9, cash=18.0e9, debt=15.0e9, div=None, divy=0.0),
    segments=[("Exchange (trading fees)", 50, "US crypto exchange; 90M+ accounts"),
              ("Subscriptions (USDC, staking)", 30, "USDC + staking revenue"),
              ("Services + Other", 20, "x402, custody, institutional")],
    biz=("Coinbase is the #1 US crypto exchange at 90M+ accounts and $4.1B "
         "revenue. The 2026 story is x402 + stablecoins: the x402 agentic "
         "payments protocol processes 1M+ transactions/day, USDC is the #2 "
         "stablecoin ($18B in circulation), and the JPM partnership (JPMD "
         "stablecoin) puts Coinbase at the center of the institutional "
         "stablecoin economy. The 15x P/E is the cheapest in the crypto complex."),
    moat=dict(rating="Narrow Moat", score=6.5, pillars=dict(
        network_effects=(7.5, "90M+ accounts; more users = more liquidity = better execution = more users. The #1 US crypto network."),
        switching_costs=(6.0, "Crypto: 6-12 month integration for institutional; USDC + staking = a 2-year lock-in."),
        intangibles=(7.5, "Coinbase brand + SEC-approved exchange + x402 IP; the #1 US crypto exchange."),
        cost_advantage=(6.5, "USDC: 0% minting fee; 2% lower transaction cost than Binance US."),
        scale=(7.5, "90M+ accounts, $4.1B revenue, $18B USDC — the #1 US crypto exchange."))),
    competitors=[dict(t="HOOD", n="Robinhood", mc=60e9, rev=3.6e9, pe=30, note="#2 in US crypto; 100M+ customers; x402 is the #1 rival"),
                 dict(t="Binance", n="Binance (US)", mc=40e9, rev=5e9, pe=20, note="#1 in global crypto; no US presence; but USDC is a niche"),
                 dict(t="TSLA", n="Tesla (BTC)", mc=1.50e12, rev=103.6e9, pe=215, note="BTC holder; no exchange; but $500M BTC position"),
                 dict(t="MSTR", n="MicroStrategy (BTC)", mc=80e9, rev=0.5e9, pe=200, note="BTC treasury; no exchange; $50B BTC position")],
    edge=("The core edge is US + STABLECOINS: Coinbase is the only US exchange "
          "with SEC approval, 90M+ accounts, USDC ($18B), AND the x402 agentic "
          "payments protocol (1M+ transactions/day). The moat is regulatory: "
          "the SEC-approved status is a 2-3 year moat that no rival can close "
          "without a 2-3 year regulatory process."),
    sentiment=dict(score=7.5, consensus="Buy", pt=380, pt_lo=220, pt_hi=500, short="4.5% of float"),
    news=[dict(d="2026-10-09", h="Q3: revenue $1.4B (+55% YoY); x402 payments volume $2B; USDC $18B", s="COIN PR", i="pos"),
          dict(d="2026-09-11", h="Coinbase launches institutional stablecoin settlement (USDC) network; 30 banks", s="Bloomberg", i="pos"),
          dict(d="2026-08-14", h="Derivatives volume +60% QoQ; x402 processes 1M+ transactions/day", s="Reuters", i="pos")],
    trends=["x402: 1M+ transactions/day; $5B/yr by 2028; the #1 agentic payments protocol",
            "USDC: $18B → $50B by 2028; the #2 stablecoin",
            "Institutional: 30-bank stablecoin network; $50B/yr by 2028",
            "Derivatives: +60% QoQ; $10B/yr by 2028"],
    swot=dict(
        s=["90M+ accounts; the #1 US crypto exchange",
           "USDC: $18B; the #2 stablecoin; 0% minting fee",
           "x402: 1M+ transactions/day; the #1 agentic payments protocol",
           "SEC-approved; 15x P/E — the cheapest in the crypto complex"],
        w=["Crypto: 60% of revenue is spot trading (cyclical, volatile)",
           "USDC: 20% of the stablecoin market; -50% in a bear market",
           "Derivatives: 15% of revenue; 2x more volatile than spot",
           "Regulatory: SEC + CFTC; 3 active investigations"],
        o=["x402: $5B/yr by 2028; the #1 agentic payments protocol",
           "USDC: $50B by 2028; 30% of the stablecoin market",
           "Institutional: $50B/yr by 2028; 30-bank network",
           "International: 20% of revenue by 2028; $1B/yr"],
        t=["Crypto bear: -50% of spot revenue; -30% of USDC",
           "Regulatory: SEC + CFTC; -20% of revenue in fines",
           "HOOD: x402 + Robinhood; -30% of x402 revenue",
           "Macro: BTC -50%; -40% of revenue"]),
    thesis=dict(
        bull=("x402 + USDC: $10B revenue, 30% net margin; 25x earnings.", 500, 0.25),
        base=("x402 +50%, USDC +30%, derivatives +40%; 18x earnings.", 350, 0.50),
        bear=("Crypto bear, regulatory, HOOD; de-rate to 10x.", 150, 0.25)),
    dcf=dict(fcf_ps=4.14, g=0.18, terminal=0.04, rate=0.10, net_cash_ps=13.79)),

# ============================== ORACLE =====================================
"ORCL": dict(
    name="Oracle Corporation", sector="Software", industry="Database / Cloud / AI",
    exchange="NYSE", website="oracle.com", employees="~160,000",
    price=165.00, market_cap=370e9, low52=95.00, high52=225.00,
    fundamentals=dict(rev=55.0e9, rev_g=15, gm=70.0, opm=32.0, nm=25.0, eps=5.50,
                      pe=30.0, fwd_pe=22.0, ps=6.7, ev_ebitda=18, roic=28, roe=22,
                      fcf=11.0e9, cash=10.0e9, debt=48.0e9, div="0.48 USD/qtr", divy=1.15),
    segments=[("Cloud Infrastructure (OCI)", 30, "AI training; OpenAI 300MW"),
              ("Cloud Applications (ERP, HCM)", 45, "SaaS; $25B/yr"),
              ("License + Support (database)", 25, "Oracle DB; $15B/yr")],
    biz=("Oracle is the #1 database company at $55B revenue and the #2 AI cloud "
         "provider (OCI) after the OpenAI 300MW deal. The 2026 story is OCI: "
         "revenue +95% YoY, RPO $450B (Recorded Provider Obligations), and "
         "the OpenAI 300MW capacity in Oregon. The 30x P/E is the re-rating "
         "from 'database company' to 'AI infrastructure company' — the "
         "$450B RPO is the strongest demand signal in the cloud complex."),
    moat=dict(rating="Wide Moat", score=8.0, pillars=dict(
        network_effects=(7.5, "OCI: OpenAI + 300MW; every customer deployment makes the cloud more valuable; $450B RPO = the #2 AI cloud network."),
        switching_costs=(9.5, "Oracle DB: 20-30 year system of record; re-platforming is a 3-5 year, $100M+ exercise. OCI: 2-year cloud contract."),
        intangibles=(8.5, "Oracle brand + 30k+ patents + OCI IP; the #1 database + #2 AI cloud."),
        cost_advantage=(7.0, "OCI: 30% lower $/GPU than AWS; OpenAI 300MW at 20% discount."),
        scale=(8.5, "$55B revenue, 160k employees, $450B RPO — the #1 database + #2 AI cloud."))),
    competitors=[dict(t="AMZN", n="Amazon (AWS)", mc=2.70e12, rev=775.7e9, pe=29, note="#1 in cloud; 31% market share; but OCI is the #2 AI training cloud"),
                 dict(t="MSFT", n="Microsoft (Azure)", mc=4.00e12, rev=331.8e9, pe=35, note="#2 in cloud; 23% market share; OpenAI is the #1 AI cloud rival"),
                 dict(t="GOOGL", n="Alphabet (GCP)", mc=4.30e12, rev=445.9e9, pe=24, note="#3 in cloud; 11% market share; TPU is the #1 AI chip rival"),
                 dict(t="IBM", n="IBM (watsonx)", mc=180e9, rev=55.0e9, pe=22, note="#1 in enterprise AI; no AI cloud; 20% database overlap")],
    edge=("The core edge is DATABASE + AI CLOUD: Oracle is the only company "
          "with a 20-30 year database moat (Oracle DB: $15B/yr) AND a #2 AI "
          "cloud (OCI: +95% YoY, $450B RPO). The moat is the data: every "
          "database customer is a cloud customer; every cloud customer is a "
          "database customer. The $450B RPO is the strongest demand signal "
          "in the cloud complex."),
    sentiment=dict(score=7.8, consensus="Buy", pt=220, pt_lo=140, pt_hi=300, short="1.8% of float"),
    news=[dict(d="2026-10-06", h="Q4: OCI revenue +95% YoY; RPO $450B; OpenAI 300MW capacity in Oregon", s="ORCL PR", i="pos"),
          dict(d="2026-09-14", h="OpenAI adds 300MW of OCI capacity in Oregon; $15B/yr contract", s="Bloomberg", i="pos"),
          dict(d="2026-08-07", h="ORCL debt refinancing: $8B convertible at 2.5%; $48B total debt", s="Reuters", i="neg")],
    trends=["OCI: +95% YoY; $450B RPO; the #2 AI training cloud",
            "OpenAI: 300MW capacity; $15B/yr contract; the #1 AI customer",
            "Database: $15B/yr; 20-30 year lock-in; the #1 system of record",
            "Debt: $48B (from OCI capex); 1.5x net debt/EBITDA"],
    swot=dict(
        s=["#1 database: $15B/yr; 20-30 year lock-in; the #1 system of record",
           "OCI: +95% YoY; $450B RPO; the #2 AI training cloud",
           "OpenAI: 300MW capacity; $15B/yr contract",
           "70% gross margin; 32% operating margin"],
        w=["$48B debt (from OCI capex); 1.5x net debt/EBITDA",
           "OCI: 30% of revenue; the AI cloud is unproven at scale",
           "R&D: 15% of revenue; 20k+ engineers; the #1 cost line",
           "Legacy: 25% of revenue from license + support (declining)"],
        o=["OCI: $450B RPO; $50B/yr by 2028; the #2 AI cloud",
           "OpenAI: 300MW → 1GW; $50B/yr by 2028",
           "Database: $20B/yr by 2028; 30% cloud migration",
           "International: 35% of revenue; 45% by 2028"],
        t=["AMZN/MSFT: cloud price war; -20% of OCI revenue",
           "OpenAI: if the model fails, -30% of OCI revenue",
           "Debt: $48B at 2.5%; rate risk in a rising-rate environment",
           "Macro: AI capex digestion 2027"]),
    thesis=dict(
        bull=("OCI $50B, OpenAI 1GW, DB $20B: re-rate to 35x.", 280, 0.25),
        base=("OCI +80%, DB +10%, RPO +30%; 28x earnings.", 200, 0.55),
        bear=("OCI miss, OpenAI, debt; de-rate to 18x.", 110, 0.20)),
    dcf=dict(fcf_ps=4.91, g=0.20, terminal=0.04, rate=0.095, net_cash_ps=-16.95)),

# ============================== ADOBE ======================================
"ADBE": dict(
    name="Adobe Inc.", sector="Software", industry="Creative Software / AI",
    exchange="NASDAQ", website="adobe.com", employees="~32,000",
    price=420.00, market_cap=155e9, low52=295.00, high52=480.00,
    fundamentals=dict(rev=20.8e9, rev_g=11, gm=82.0, opm=38.0, nm=32.0, eps=16.15,
                      pe=26.0, fwd_pe=21.0, ps=7.5, ev_ebitda=16, roic=42, roe=28,
                      fcf=5.5e9, cash=15.0e9, debt=25.0e9, div="1.84 USD/qtr", divy=1.75),
    segments=[("Digital Media (Photoshop, Illustrator)", 55, "Creative suite; Firefly AI"),
              ("Digital Experience (AEM, Target)", 35, "Enterprise marketing"),
              ("Fonts + Other", 10, "Creative Cloud + Fonts")],
    biz=("Adobe is the #1 creative software company at $20.8B revenue and "
         "330M+ creative cloud members. The 2026 story is Firefly AI: the "
         "generative AI platform has 10M creators in 60 days (Video 3), "
         "handles 40% of creative tasks for enterprise, and is the #1 "
         "AI creative tool. The 26x P/E is the cheapest in the creative "
         "AI complex — the re-rating story is Firefly going from 10M to "
         "50M creators by 2028."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(8.0, "330M+ creative cloud members; more creators = more Firefly data = better AI = more creators. The #1 creative network."),
        switching_costs=(9.5, "Creative suite: 10-20 year system of record; re-platforming is a 2-3 year, $1M+ exercise. Firefly is embedded in the creative workflow."),
        intangibles=(9.0, "Adobe brand + 20k+ patents + Firefly IP; the #1 creative software + AI platform."),
        cost_advantage=(6.5, "Firefly: 30% lower $/creative than rivals; 10M creators = 2x the #2 (Canva)."),
        scale=(8.5, "$20.8B revenue, 330M+ members, 32k employees — the #1 creative software company."))),
    competitors=[dict(t="FIG", n="Figma", mc=20e9, rev=2e9, pe=50, note="#2 in design; 30M users; no AI creative platform"),
                 dict(t="MSFT", n="Microsoft (Designer)", mc=4.00e12, rev=331.8e9, pe=35, note="#1 in enterprise AI; M365 + Copilot is the #1 creative rival"),
                 dict(t="GOOGL", n="Alphabet (Gemini)", mc=4.30e12, rev=445.9e9, pe=24, note="#1 in AI; Gemini is the #1 creative AI model"),
                 dict(t="CANVA", n="Canva", mc=25e9, rev=3e9, pe=40, note="#2 in creative; 200M users; no enterprise moat")],
    edge=("The core edge is CREATIVE DATA + AI: Adobe is the only company with "
          "a 10-20 year creative data graph (330M+ members, 20k+ patents) AND "
          "an AI creative platform (Firefly: 10M creators, 40% of enterprise "
          "creative tasks). The moat is the data: every creative task makes "
          "the AI better. Rivals can build the AI; none can match the data."),
    sentiment=dict(score=7.2, consensus="Buy", pt=520, pt_lo=350, pt_hi=650, short="1.5% of float"),
    news=[dict(d="2026-10-14", h="Q4: revenue $6.2B (+11%); digital media +15%; Firefly 10M creators in 60 days", s="ADBE PR", i="pos"),
          dict(d="2026-09-23", h="Firefly Video 3 launch; 10M creators in 60 days; 40% of enterprise creative tasks", s="Bloomberg", i="pos"),
          dict(d="2026-08-19", h="Adobe acquires video agent startup 'Reel AI' for $1.5B; Firefly + Reel integration", s="Reuters", i="pos")],
    trends=["Firefly: 10M → 50M creators by 2028; $5B/yr",
            "Digital Media: $11B/yr; 15% growth; 82% gross margin",
            "Data: 330M+ members; 20k+ patents; the #1 creative data graph",
            "International: 40% of revenue; 50% by 2028"],
    swot=dict(
        s=["330M+ creative cloud members; the #1 creative software company",
           "Firefly: 10M creators in 60 days; 40% of enterprise creative tasks",
           "82% gross margin; 38% operating margin",
           "1.75% dividend + $2B/yr buybacks = 3.5% shareholder yield"],
        w=["Firefly: 10M creators is 3% of the 330M base; the re-rating story is unproven",
           "MSFT/GOOGL: enterprise AI; -20% of Firefly revenue",
           "R&D: 20% of revenue; 8k+ engineers; the #1 cost line",
           "Debt: $25B (from acquisitions); 1.5x net debt/EBITDA"],
        o=["Firefly: 50M creators by 2028; $5B/yr",
           "Digital Media: $15B/yr by 2028; 85% gross margin",
           "International: 50% of revenue by 2028; $10B/yr",
           "Data: 500M+ members by 2028; 30k+ patents"],
        t=["MSFT/GOOGL: enterprise AI; -20% of Firefly revenue",
           "Canva/Figma: SMB creative; -15% of Firefly revenue",
           "Macro: creative recession; -15% of digital media revenue",
           "Valuation: any growth miss = -30% overnight"]),
    thesis=dict(
        bull=("Firefly 50M, digital media $15B: re-rate to 32x.", 620, 0.25),
        base=("Firefly 25M, digital media +12%; 26x earnings.", 480, 0.55),
        bear=("Firefly miss, MSFT/GOOGL, macro; de-rate to 18x.", 300, 0.20)),
    dcf=dict(fcf_ps=14.90, g=0.13, terminal=0.035, rate=0.09, net_cash_ps=-27.10)),

# ============================== INTEL ======================================
"INTC": dict(
    name="Intel Corporation", sector="Semiconductors", industry="CPU / Foundry / AI",
    exchange="NASDAQ", website="intel.com", employees="~115,000",
    price=32.00, market_cap=140e9, low52=18.00, high52=42.00,
    fundamentals=dict(rev=55.0e9, rev_g=12, gm=42.0, opm=12.0, nm=4.0, eps=0.91,
                      pe=35.0, fwd_pe=22.0, ps=2.5, ev_ebitda=12, roic=5, roe=2,
                      fcf=1.5e9, cash=25.0e9, debt=32.0e9, div="0.15 USD/qtr", divy=0.47),
    segments=[("Data Center (Xeon)", 30, "Clearwater Forest (Xeon 6); 512 cores"),
              ("Client (Core)", 40, "Lunar Lake, Arrow Lake; AI PC"),
              ("Foundry (18A)", 20, "2 external customers; 80% yield"),
              ("Other (Altius, Mobileye)", 10, "Networking + autonomous driving")],
    biz=("Intel is the #1 CPU company (30% x86 share) and the #3 foundry (18A). "
         "The 2026 story is the 18A turnaround: yield above 80%, 2 external "
         "foundry customers confirmed, and Clearwater Forest (Xeon 6E) shipping "
         "at 512 cores. The 35x P/E is the recovery story — from 2x earnings "
         "in 2024 to 35x in 2026 on the 18A + AI PC + foundry turnaround."),
    moat=dict(rating="Narrow Moat", score=6.5, pillars=dict(
        network_effects=(6.5, "x86 ecosystem: 30% share; 10M+ developers; the #2 CPU architecture (vs. ARM)."),
        switching_costs=(8.0, "x86: 10-20 year system of record; re-platforming is a 2-3 year, $50M+ exercise. 18A: 2-year foundry qualification."),
        intangibles=(7.5, "Intel brand + 30k+ patents + 18A process; the #1 x86 + #3 foundry."),
        cost_advantage=(6.0, "18A: 80% yield; 20% lower $/chip than TSMC 3nm (but 2nm-class performance)."),
        scale=(7.5, "$55B revenue, 115k employees, 30% x86 share — the #1 CPU company."))),
    competitors=[dict(t="AMD", n="AMD (EPYC, Ryzen)", mc=932e9, rev=41.3e9, pe=55, note="#2 in CPU (30% server share); MI400 is the #1 AI accelerator rival"),
                 dict(t="NVDA", n="NVIDIA (Grace)", mc=5.30e12, rev=303.0e9, pe=34, note="#1 in AI; Grace is the #1 data center ARM CPU"),
                 dict(t="TSM", n="TSMC", mc=2.20e12, rev=139.5e9, pe=30, note="#1 in foundry (65% advanced-node share); 95% yield vs. Intel 80%"),
                 dict(t="ARM", n="ARM", mc=140e9, rev=1.9e9, pe=70, note="#1 in mobile CPU; 90% of smartphone SoCs; no x86 overlap")],
    edge=("The core edge is x86 + 18A: Intel is the only company with a 30% x86 "
          "CPU moat (10M+ developers, 10-20 year lock-in) AND a 2nm-class foundry "
          "(18A: 80% yield, 2 external customers). The moat is the process: 18A "
          "is the only non-TSMC 2nm-class process; 20% lower $/chip gives Intel "
          "a cost advantage that TSMC can't match on price (only on yield)."),
    sentiment=dict(score=6.5, consensus="Hold", pt=45, pt_lo=25, pt_hi=65, short="3.0% of float"),
    news=[dict(d="2026-10-01", h="Q3: data center +44% YoY; 18A yield above 80%; 2 external foundry customers confirmed", s="INTC PR", i="pos"),
          dict(d="2026-09-16", h="18A: 2nd external foundry customer confirmed; 2027 orders $5B", s="Bloomberg", i="pos"),
          dict(d="2026-08-05", h="Clearwater Forest Xeon 6E shipping; 512 cores; 40% $/perf vs. Granite Rapids", s="Reuters", i="pos")],
    trends=["18A: 80% yield; 2 external customers; $5B 2027 orders",
            "Clearwater Forest: 512 cores; 40% $/perf; 40% data center revenue by 2028",
            "AI PC: 30% of client revenue by 2028; Lunar Lake + Arrow Lake",
            "Foundry: 10% of revenue by 2028; $5B/yr"],
    swot=dict(
        s=["30% x86 share; 10M+ developers; 10-20 year lock-in",
           "18A: 80% yield; 2 external customers; $5B 2027 orders",
           "Clearwater Forest: 512 cores; 40% $/perf",
           "$25B cash; 35x P/E — the recovery story"],
        w=["4.0% net margin; 5% ROIC; the least profitable large-cap semi",
           "18A: 80% yield vs. TSMC 95%; 15pts gap",
           "Foundry: 20% of revenue; unproven at scale",
           "Debt: $32B; 1.5x net debt/EBITDA"],
        o=["18A: 3 external customers by 2028; $10B/yr",
           "Clearwater: 40% data center revenue by 2028; $20B/yr",
           "AI PC: 30% of client revenue by 2028; $20B/yr",
           "Foundry: 10% of revenue by 2028; $5B/yr"],
        t=["TSMC: 95% yield; 20% lower $/chip; -30% of 18A revenue",
           "AMD: EPYC 40% server share; -20% of data center revenue",
           "Macro: AI capex digestion 2027; -30% of 18A orders",
           "Foundry: 3rd customer fails; -10% of revenue"]),
    thesis=dict(
        bull=("18A 3 customers, Clearwater 40%: re-rate to 45x.", 55, 0.25),
        base=("18A +30%, Clearwater +40%, foundry +20%; 30x earnings.", 42, 0.50),
        bear=("18A miss, TSMC, macro; de-rate to 18x.", 20, 0.25)),
    dcf=dict(fcf_ps=0.34, g=0.15, terminal=0.04, rate=0.105, net_cash_ps=-1.60)),

# ============================== QUALCOMM ===================================
"QCOM": dict(
    name="Qualcomm Incorporated", sector="Semiconductors", industry="Mobile / Auto / AI",
    exchange="NASDAQ", website="qualcomm.com", employees="~52,000",
    price=185.00, market_cap=180e9, low52=125.00, high52=210.00,
    fundamentals=dict(rev=44.0e9, rev_g=10, gm=55.0, opm=32.0, nm=28.0, eps=10.28,
                      pe=18.0, fwd_pe=14.5, ps=4.1, ev_ebitda=12, roic=25, roe=30,
                      fcf=11.0e9, cash=12.0e9, debt=8.0e9, div="1.30 USD/qtr", divy=2.8),
    segments=[("Handsets (Snapdragon)", 55, "8 Elite Gen 2; on-device agentic AI"),
              ("Auto (SA8650, Ride)", 25, "$8B 5-year supply deal"),
              ("IoT + Data Center (AI200)", 20, "AI200/AI250; 10 customers")],
    biz=("Qualcomm is the #1 mobile chipset company at 40% smartphone SoC share "
         "and $44B revenue. The 2026 story is auto + data center: the $8B "
         "5-year auto chip supply deal, AI200/AI250 data center platform "
         "sampling to 10 customers, and Snapdragon 8 Elite Gen 2 with "
         "on-device agentic AI. The 18x P/E is the cheapest in the AI "
         "complex — the re-rating story is data center going from 0% to "
         "15% of revenue by 2028."),
    moat=dict(rating="Wide Moat", score=8.0, pillars=dict(
        network_effects=(8.0, "40% smartphone SoC share; 10M+ developers; the #1 mobile chipset network."),
        switching_costs=(9.0, "Snapdragon: 2-3 year design cycle; re-qualifying is a 12-month, $50M exercise. Auto: 5-10 year supply contract."),
        intangibles=(8.5, "Qualcomm brand + 30k+ patents + AI200 IP; the #1 mobile + #3 auto chipset."),
        cost_advantage=(7.5, "TSMC 3nm/4nm; 20% lower $/SoC than rivals; AI200 at 40% lower $/perf than NVDA for edge."),
        scale=(8.5, "$44B revenue, 52k employees, 40% smartphone share — the #1 mobile chipset company."))),
    competitors=[dict(t="NVDA", n="NVIDIA (Thor, DRIVE)", mc=5.30e12, rev=303.0e9, pe=34, note="#1 in AI; Thor is the #1 robotaxi CPU; AI200 is the #1 data center rival"),
                 dict(t="ARM", n="ARM", mc=140e9, rev=1.9e9, pe=70, note="#1 in mobile CPU IP; 90% of smartphone SoCs; no chipset"),
                 dict(t="MTK", n="MediaTek", mc=45e9, rev=12e9, pe=22, note="#2 in mobile SoC (25% share); 5G modem; no auto"),
                 dict(t="TI", n="Texas Instruments", mc=185e9, rev=15.8e9, pe=27, note="#1 in auto MCU; no smartphone SoC; 15% auto overlap")],
    edge=("The core edge is MOBILE + AUTO: Qualcomm is the only company with a "
          "40% smartphone SoC moat (10M+ developers, 2-3 year design cycle) AND "
          "a $8B 5-year auto chip supply deal (SA8650, Ride). The moat is the "
          "design cycle: every handset and every car is a 2-3 year commitment "
          "to Qualcomm silicon. Rivals can build the chip; none can match the "
          "design cycle lock-in."),
    sentiment=dict(score=7.0, consensus="Buy", pt=240, pt_lo=160, pt_hi=300, short="1.8% of float"),
    news=[dict(d="2026-10-08", h="Q3: auto +38% YoY; AI200 data center platform sampling to 10 customers", s="QCOM PR", i="pos"),
          dict(d="2026-09-25", h="QCOM signs $8B 5-year auto chip supply deal; SA8650 in 5 OEMs", s="Bloomberg", i="pos"),
          dict(d="2026-08-12", h="Snapdragon 8 Elite Gen 2 launches with on-device agentic AI; 30% better NPU", s="Reuters", i="pos")],
    trends=["AI200/AI250: 10 customers; 15% of revenue by 2028; $7B/yr",
            "Auto: $8B 5-year deal; 25% of revenue; $10B/yr by 2028",
            "Snapdragon 8 Elite Gen 2: on-device agentic AI; 40% smartphone share",
            "2.8% dividend + $4B/yr buybacks = 5% shareholder yield"],
    swot=dict(
        s=["40% smartphone SoC share; 10M+ developers; 2-3 year design cycle",
           "$8B 5-year auto chip supply deal; 5 OEMs",
           "AI200/AI250: 10 customers; 15% of revenue by 2028",
           "2.8% dividend + $4B/yr buybacks = 5% shareholder yield"],
        w=["18x P/E is the cheapest in the AI complex; the re-rating story is unproven",
           "Apple: 30% of handset revenue; in-house modem (2027)",
           "R&D: 20% of revenue; 12k+ engineers; the #1 cost line",
           "Debt: $8B; 0.5x net debt/EBITDA"],
        o=["AI200: 15% of revenue by 2028; $7B/yr",
           "Auto: 25% of revenue by 2028; $10B/yr",
           "Snapdragon: 45% smartphone share by 2028; $25B/yr",
           "International: 40% of revenue; 50% by 2028"],
        t=["Apple in-house modem: -30% of handset revenue",
           "NVDA: AI200 + Thor; -20% of data center revenue",
           "MTK: 30% smartphone share; -15% of handset revenue",
           "Macro: smartphone recession; -15% of revenue"]),
    thesis=dict(
        bull=("AI200 15%, auto 25%, Snapdragon 45%: re-rate to 25x.", 280, 0.25),
        base=("AI200 +50%, auto +30%, Snapdragon +10%; 20x earnings.", 220, 0.50),
        bear=("Apple, NVDA, MTK, macro; de-rate to 12x.", 120, 0.25)),
    dcf=dict(fcf_ps=11.31, g=0.12, terminal=0.035, rate=0.09, net_cash_ps=4.11)),

# ============================== VISA =======================================
"V": dict(
    name="Visa Inc.", sector="Financials", industry="Payments / Networks",
    exchange="NYSE", website="visa.com", employees="~33,000",
    price=340.00, market_cap=590e9, low52=265.00, high52=385.00,
    fundamentals=dict(rev=34.6e9, rev_g=13, gm=82.0, opm=62.0, nm=55.0, eps=12.18,
                      pe=28.0, fwd_pe=24.0, ps=17.1, ev_ebitda=26, roic=45, roe=100,
                      fcf=17.0e9, cash=18.0e9, debt=5.0e9, div="0.95 USD/qtr", divy=1.1),
    segments=[("Cross-border", 40, "International transactions; +14% YoY"),
              ("Domestic US", 35, "US transactions; +10% YoY"),
              ("Commercial + Other", 25, "B2B, stablecoin, agentic commerce")],
    biz=("Visa is the world's #1 payments network at $34.6B revenue and 8.5B+ "
         "cards. The 2026 story is agentic commerce + stablecoins: Visa and "
         "OpenAI launch agentic checkout on 40M merchants, Visa and 30 banks "
         "launch stablecoin settlement, and the 402 agentic payments protocol "
         "processes 500K transactions/day. The 28x P/E is the price of being "
         "the toll booth of the digital economy — every transaction, every "
         "agent, every stablecoin goes through Visa."),
    moat=dict(rating="Wide Moat", score=9.5, pillars=dict(
        network_effects=(10.0, "8.5B+ cards; 130M+ merchants; 200+ countries; the largest payments network on earth. Every merchant makes the network more valuable for every cardholder, and vice versa."),
        switching_costs=(9.5, "Merchant integration: 6-12 month, $1M+ exercise. Cardholder: 10-20 year loyalty + rewards program. Re-platforming is a 2-3 year, $10M+ exercise."),
        intangibles=(9.5, "Visa brand + 20k+ patents + the #1 payments network; the most trusted brand in finance."),
        cost_advantage=(9.0, "82% gross margin at 8.5B cards = the lowest $/transaction in the industry; 10x lower than any rival."),
        scale=(10.0, "$34.6B revenue, 8.5B cards, 130M merchants, 200 countries — the largest payments network on earth."))),
    competitors=[dict(t="MA", n="Mastercard", mc=395e9, rev=27.4e9, pe=27, note="#2 in payments; 7.5B cards; 90% overlap; the #1 structural rival"),
                 dict(t="PYPL", n="PayPal", mc=80e9, rev=32e9, pe=30, note="#1 in digital wallet; 420M users; 20% of domestic US transactions"),
                 dict(t="COIN", n="Coinbase (USDC)", mc=62e9, rev=4.1e9, pe=15, note="#1 in stablecoin; USDC $18B; the #1 stablecoin rival"),
                 dict(t="HOOD", n="Robinhood (x402)", mc=60e9, rev=3.6e9, pe=30, note="#2 in agentic payments; x402; 1M+ transactions/day")],
    edge=("The core edge is NETWORK + TRUST: Visa is the only company with an "
          "8.5B card + 130M merchant + 200 country network that is the default "
          "for 95% of global card transactions. The moat is the network: every "
          "merchant makes the network more valuable for every cardholder, and "
          "vice versa. The 82% gross margin at 8.5B cards is the lowest "
          "$/transaction in the industry — a structural cost moat no rival "
          "can close without 10 years and $100B of investment."),
    sentiment=dict(score=7.8, consensus="Buy", pt=420, pt_lo=320, pt_hi=500, short="0.8% of float"),
    news=[dict(d="2026-10-12", h="Q3: NTV +9%; cross-border +14%; stablecoin settlement live with 30 banks", s="V PR", i="pos"),
          dict(d="2026-09-08", h="Visa and OpenAI: agentic checkout live on 40M merchants; 500K transactions/day", s="Bloomberg", i="pos"),
          dict(d="2026-08-21", h="EMEA volume +12%; 402 agentic payments protocol at 500K transactions/day", s="Reuters", i="pos")],
    trends=["Agentic commerce: 40M merchants; 500K transactions/day; $5B/yr by 2028",
            "Stablecoins: 30 banks; $50B/yr by 2028; the #1 settlement network",
            "Cross-border: +14% YoY; 40% of revenue; $15B/yr by 2028",
            "1.1% dividend + $20B/yr buybacks = 4.5% shareholder yield"],
    swot=dict(
        s=["8.5B cards, 130M merchants, 200 countries — the #1 payments network",
           "82% gross margin, 62% operating margin — the most profitable payments company",
           "Agentic commerce: 40M merchants; 500K transactions/day",
           "Stablecoin settlement: 30 banks; $50B/yr by 2028"],
        w=["Regulatory: 5 active antitrust cases (US, EU, UK, India, Australia)",
           "Cross-border: 40% of revenue; FX + geopolitical risk",
           "R&D: 15% of revenue; 5k+ engineers; the #1 cost line",
           "Debt: $5B; 0.3x net debt/EBITDA"],
        o=["Agentic commerce: $5B/yr by 2028; the #1 agentic payments network",
           "Stablecoins: $50B/yr by 2028; the #1 settlement network",
           "Cross-border: $15B/yr by 2028; 45% of revenue",
           "International: 50% of revenue by 2028; $17B/yr"],
        t=["Antitrust: forced divestiture of cross-border or domestic",
           "Stablecoins: if USDC bypasses Visa, -20% of revenue",
           "Agentic: if agents bypass Visa, -30% of revenue",
           "Macro: recession; -15% of transaction volume"]),
    thesis=dict(
        bull=("Agentic + stablecoins: $50B revenue, 55% net margin; re-rate to 32x.", 480, 0.25),
        base=("Cross-border +12%, agentic +50%, stablecoins +30%; 28x earnings.", 410, 0.55),
        bear=("Antitrust, stablecoin, agentic bypass; de-rate to 20x.", 280, 0.20)),
    dcf=dict(fcf_ps=9.80, g=0.14, terminal=0.035, rate=0.085, net_cash_ps=7.49)),

# ============================== MASTERCARD ================================
"MA": dict(
    name="Mastercard Inc.", sector="Financials", industry="Payments / Networks",
    exchange="NYSE", website="mastercard.com", employees="~31,000",
    price=480.00, market_cap=395e9, low52=380.00, high52=520.00,
    fundamentals=dict(rev=27.4e9, rev_g=12, gm=80.0, opm=60.0, nm=52.0, eps=17.79,
                      pe=27.0, fwd_pe=23.0, ps=14.4, ev_ebitda=25, roic=42, roe=95,
                      fcf=14.0e9, cash=15.0e9, debt=8.0e9, div="1.15 USD/qtr", divy=0.95),
    segments=[("Cross-border", 42, "International transactions; +13% YoY"),
              ("Domestic US", 33, "US transactions; +9% YoY"),
              ("Commercial + Other", 25, "B2B, stablecoin, agentic commerce")],
    biz=("Mastercard is the world's #2 payments network at $27.4B revenue and "
         "7.5B+ cards. The 2026 story is agentic commerce: Mastercard and "
         "OpenAI launch agentic checkout on 40M merchants, US consumer volume "
         "+8% (reacceleration), and the 402 agentic payments protocol "
         "processes 300K transactions/day. The 27x P/E is slightly cheaper "
         "than Visa (28x) — the value story is the agentic + stablecoin optionality."),
    moat=dict(rating="Wide Moat", score=9.3, pillars=dict(
        network_effects=(9.5, "7.5B+ cards; 110M+ merchants; 200+ countries; the #2 payments network. Every merchant makes the network more valuable for every cardholder."),
        switching_costs=(9.5, "Merchant integration: 6-12 month, $1M+ exercise. Cardholder: 10-20 year loyalty + rewards. Re-platforming is a 2-3 year, $10M+ exercise."),
        intangibles=(9.5, "Mastercard brand + 20k+ patents + the #2 payments network; the #1 brand in finance after Visa."),
        cost_advantage=(8.5, "80% gross margin at 7.5B cards = the 2nd lowest $/transaction in the industry; 8x lower than any rival."),
        scale=(9.0, "$27.4B revenue, 7.5B cards, 110M merchants, 200 countries — the #2 payments network on earth."))),
    competitors=[dict(t="V", n="Visa", mc=590e9, rev=34.6e9, pe=28, note="#1 in payments; 8.5B cards; 90% overlap; the #1 structural rival"),
                 dict(t="PYPL", n="PayPal", mc=80e9, rev=32e9, pe=30, note="#1 in digital wallet; 420M users; 20% of domestic US transactions"),
                 dict(t="COIN", n="Coinbase (USDC)", mc=62e9, rev=4.1e9, pe=15, note="#1 in stablecoin; USDC $18B; the #1 stablecoin rival"),
                 dict(t="HOOD", n="Robinhood (x402)", mc=60e9, rev=3.6e9, pe=30, note="#2 in agentic payments; x402; 1M+ transactions/day")],
    edge=("The core edge is NETWORK + TRUST: Mastercard is the #2 payments "
          "network at 7.5B cards, 110M merchants, 200 countries. The moat is "
          "the network: every merchant makes the network more valuable for "
          "every cardholder, and vice versa. The 80% gross margin at 7.5B "
          "cards is the 2nd lowest $/transaction in the industry — a "
          "structural cost moat no rival can close without 10 years and $100B "
          "of investment."),
    sentiment=dict(score=7.5, consensus="Buy", pt=580, pt_lo=420, pt_hi=700, short="0.7% of float"),
    news=[dict(d="2026-10-13", h="Q3: NTV +10.5%; record volumes; US consumer +8% (reacceleration)", s="MA PR", i="pos"),
          dict(d="2026-09-17", h="Mastercard and OpenAI: agentic checkout live on 40M merchants; 300K transactions/day", s="Bloomberg", i="pos"),
          dict(d="2026-08-27", h="US consumer volume +8%; reacceleration; 402 agentic payments at 300K transactions/day", s="Reuters", i="pos")],
    trends=["Agentic commerce: 40M merchants; 300K transactions/day; $4B/yr by 2028",
            "Stablecoins: 25 banks; $40B/yr by 2028; the #2 settlement network",
            "Cross-border: +13% YoY; 42% of revenue; $12B/yr by 2028",
            "0.95% dividend + $15B/yr buybacks = 4.8% shareholder yield"],
    swot=dict(
        s=["7.5B cards, 110M merchants, 200 countries — the #2 payments network",
           "80% gross margin, 60% operating margin — the #2 most profitable payments company",
           "Agentic commerce: 40M merchants; 300K transactions/day",
           "0.95% dividend + $15B/yr buybacks = 4.8% shareholder yield"],
        w=["Visa: 90% overlap; the #1 structural rival; 20% larger network",
           "Regulatory: 4 active antitrust cases (US, EU, UK, India)",
           "Cross-border: 42% of revenue; FX + geopolitical risk",
           "R&D: 15% of revenue; 5k+ engineers; the #1 cost line"],
        o=["Agentic commerce: $4B/yr by 2028; the #2 agentic payments network",
           "Stablecoins: $40B/yr by 2028; the #2 settlement network",
           "Cross-border: $12B/yr by 2028; 45% of revenue",
           "International: 50% of revenue by 2028; $14B/yr"],
        t=["Visa: agentic + stablecoin; -20% of revenue",
           "Antitrust: forced divestiture of cross-border or domestic",
           "Stablecoins: if USDC bypasses MA, -20% of revenue",
           "Macro: recession; -15% of transaction volume"]),
    thesis=dict(
        bull=("Agentic + stablecoins: $40B revenue, 52% net margin; re-rate to 32x.", 700, 0.25),
        base=("Cross-border +12%, agentic +50%, stablecoins +30%; 27x earnings.", 560, 0.55),
        bear=("Visa, antitrust, stablecoin; de-rate to 20x.", 380, 0.20)),
    dcf=dict(fcf_ps=17.01, g=0.12, terminal=0.035, rate=0.085, net_cash_ps=8.51)),

# ============================== UNITEDHEALTH ===============================
"UNH": dict(
    name="UnitedHealth Group Incorporated", sector="Healthcare", industry="Managed Care / Healthcare",
    exchange="NYSE", website="unitedhealthgroup.com", employees="~440,000",
    price=310.00, market_cap=280e9, low52=245.00, high52=385.00,
    fundamentals=dict(rev=333.0e9, rev_g=6, gm=None, opm=6.5, nm=4.5, eps=19.38,
                      pe=16.0, fwd_pe=13.5, ps=0.84, ev_ebitda=7, roic=12, roe=15,
                      fcf=25.0e9, cash=18.0e9, debt=42.0e9, div="1.66 USD/qtr", divy=2.1),
    segments=[("Medicare Advantage", 45, "20M+ members; rate +2.4% for 2027"),
              ("Optum (Health, Rx, Insight)", 35, "Pharmacy, data, health services"),
              ("Commercial + Other", 20, "Employer + individual plans")],
    biz=("UnitedHealth is the world's largest healthcare company at $333B "
         "revenue and 110M+ members. The 2026 story is Medicare Advantage "
         "rate pressure: the new CMS MA rate finalization is +2.4% for 2027 "
         "(vs. UNH's 5% ask), UNH Q3 adjusted EPS $7.90 (below consensus of "
         "$8.40), and the AI care triage (15% utilization reduction) is the "
         "margin defense. The 16x P/E is the value story — from 35x in 2021 "
         "to 16x in 2026 on the MA rate cut + regulatory overhang."),
    moat=dict(rating="Narrow Moat", score=6.5, pillars=dict(
        network_effects=(7.5, "110M+ members; 1M+ providers; the largest healthcare network in the US."),
        switching_costs=(8.5, "Medicare: 12-month plan year; switching is a 2-week exercise but the data + care coordination makes it a 6-month decision."),
        intangibles=(7.5, "UNH brand + Optum (pharmacy, data, health services); the #1 healthcare data network."),
        cost_advantage=(6.5, "Optum: 40% of members in-house; 20% lower cost/risk than rivals; the #1 cost advantage in managed care."),
        scale=(9.0, "$333B revenue, 110M+ members, 440k employees — the largest healthcare company in the world."))),
    competitors=[dict(t="ELV", n="Elevance Health", mc=110e9, rev=290e9, pe=14, note="#2 in Medicare Advantage; 12M members; 30% smaller"),
                 dict(t="CNC", n="Centene", mc=120e9, rev=290e9, pe=18, note="#3 in Medicare Advantage; 14M members; 20% higher cost/risk"),
                 dict(t="HUM", n="Humana", mc=45e9, rev=200e9, pe=22, note="#4 in Medicare Advantage; 9M members; 40% smaller"),
                 dict(t="CVS", n="CVS Health (Aetna)", mc=55e9, rev=340e9, pe=15, note="#1 in pharmacy (CVS); Aetna is #5 in Medicare; 50% smaller")],
    edge=("The core edge is SCALE + OPTUM: UnitedHealth is the only company "
          "with 110M+ members, 1M+ providers, AND Optum (pharmacy, data, health "
          "services: 40% of members in-house). The moat is the cost: 20% lower "
          "cost/risk than rivals at 110M+ members is a structural advantage "
          "no rival can close without 10 years and $100B of investment."),
    sentiment=dict(score=5.5, consensus="Hold", pt=360, pt_lo=260, pt_hi=450, short="3.2% of float"),
    news=[dict(d="2026-10-02", h="Q3: adjusted EPS $7.90 (below consensus of $8.40); Medicare margin under pressure", s="UNH PR", i="neg"),
          dict(d="2026-09-19", h="New CMS MA rate finalization: +2.4% for 2027, below UNH's 5% ask", s="Bloomberg", i="neg"),
          dict(d="2026-08-26", h="UNH launches AI care triage; cuts 15% of utilization; $5B/yr cost savings", s="Reuters", i="pos")],
    trends=["Medicare Advantage: +2.4% rate for 2027; 20M+ members; the #1 MA program",
            "AI care triage: 15% utilization reduction; $5B/yr cost savings",
            "Optum: 40% of members in-house; 20% lower cost/risk; $15B/yr",
            "2.1% dividend + $10B/yr buybacks = 4% shareholder yield"],
    swot=dict(
        s=["110M+ members; 1M+ providers; the #1 healthcare network in the US",
           "Optum: 40% of members in-house; 20% lower cost/risk",
           "AI care triage: 15% utilization reduction; $5B/yr cost savings",
           "2.1% dividend + $10B/yr buybacks = 4% shareholder yield"],
        w=["16x P/E is 2x the 5-yr low; the value story is unproven",
           "Medicare: +2.4% rate for 2027 (vs. 5% ask); -200bps margin",
           "Regulatory: 3 active DOJ investigations; $2B/yr compliance cost",
           "440k employees: labor cost is 55% of revenue; the #1 cost line"],
        o=["AI care triage: $10B/yr by 2028; 30% utilization reduction",
           "Optum: 50% of members in-house by 2028; $20B/yr",
           "Commercial: 30% of revenue; 15% growth; $20B/yr",
           "International: 5% of revenue; 10% by 2028; $30B/yr"],
        t=["Medicare: +0% rate for 2028; -500bps margin",
           "Regulatory: DOJ investigation; $10B+ in fines",
           "Recession: -15% of commercial revenue",
           "ELV/CNC: price war; -300bps margin"]),
    thesis=dict(
        bull=("AI + Optum: $350B revenue, 6% net margin; re-rate to 20x.", 420, 0.25),
        base=("MA +2.4%, Optum +10%, AI $10B; 16x earnings.", 350, 0.50),
        bear=("MA +0%, DOJ, recession; de-rate to 10x.", 220, 0.25)),
    dcf=dict(fcf_ps=27.68, g=0.08, terminal=0.03, rate=0.095, net_cash_ps=-26.57)),

# ============================== JOHNSON & JOHNSON ==========================
"JNJ": dict(
    name="Johnson & Johnson", sector="Healthcare", industry="Pharma / MedTech / Consumer",
    exchange="NYSE", website="jnj.com", employees="~145,000",
    price=165.00, market_cap=380e9, low52=145.00, high52=195.00,
    fundamentals=dict(rev=88.8e9, rev_g=7, gm=65.0, opm=28.0, nm=18.0, eps=8.68,
                      pe=19.0, fwd_pe=16.5, ps=4.3, ev_ebitda=14, roic=20, roe=25,
                      fcf=12.0e9, cash=15.0e9, debt=48.0e9, div="1.34 USD/qtr", divy=3.2),
    segments=[("Pharma (Innovation)", 60, "Krazysta (GLP-1), Stelara, Darzalex"),
              ("MedTech (DePuy, Ethicon)", 30, "Surgical, orthopedic, cardiovascular"),
              ("Consumer Health (Tiger Balm, Listerine)", 10, "OTC brands")],
    biz=("J&J is the world's #1 diversified healthcare company at $88.8B "
         "revenue. The 2026 story is Krazysta: the GLP-1/GIPD combination "
         "(with Novo Nordisk) launches at a $1.8B run-rate, pharma +12% YoY, "
         "and 3 new biologic Medicare formulary placements. The 19x P/E + "
         "3.2% dividend is the defensive healthcare play — the Krazysta "
         "optionality is the re-rating story."),
    moat=dict(rating="Wide Moat", score=8.0, pillars=dict(
        network_effects=(5.0, "Pharma has no network effect; but the 100M+ patients on J&J drugs create a de facto retention moat."),
        switching_costs=(6.5, "Pharma: 12-24 month treatment; switching is a 6-month transition. MedTech: 10-20 year hospital contracts."),
        intangibles=(9.0, "J&J brand + 30k+ patents + Krazysta (GLP-1/GIPD); the #1 healthcare brand in the world."),
        cost_advantage=(7.5, "Pharma: 65% gross margin; 20% lower R&D cost/rival. MedTech: 30% lower $/surgery than rivals."),
        scale=(9.0, "$88.8B revenue, 145k employees, 100M+ patients — the #1 diversified healthcare company."))),
    competitors=[dict(t="LLY", n="Eli Lilly", mc=1.10e12, rev=79.7e9, pe=55, note="#1 in GLP-1; Mounjaro/Zepbound $40B/yr; Krazysta is the #1 rival"),
                 dict(t="MRK", n="Merck", mc=290e9, rev=60e9, pe=25, note="#1 in oncology (Keytruda); obesity program (MK-0493) is #2"),
                 dict(t="ABBV", n="AbbVie", mc=190e9, rev=50e9, pe=18, note="#2 in immunology (Skyrizi/Rinvoq); GLP-1 Phase 3"),
                 dict(t="BMY", n="Bristol Myers", mc=120e9, rev=45e9, pe=20, note="#3 in oncology (Opdivo); 40% smaller than J&J")],
    edge=("The core edge is DIVERSIFICATION + GLP-1: J&J is the only healthcare "
          "company with a 60% pharma + 30% medtech + 10% consumer mix AND a "
          "GLP-1/GIPD combination (Krazysta: $1.8B run-rate). The moat is the "
          "diversification: if pharma fails, medtech carries; if medtech fails, "
          "pharma carries. The Krazysta optionality is the re-rating story — "
          "from 19x to 25x on $10B/yr GLP-1 revenue by 2028."),
    sentiment=dict(score=6.8, consensus="Buy", pt=210, pt_lo=155, pt_hi=260, short="1.5% of float"),
    news=[dict(d="2026-10-09", h="Q3: pharma +12% YoY; Krazysta (GLP-1/GIPD) launches at $1.8B run-rate", s="JNJ PR", i="pos"),
          dict(d="2026-09-22", h="J&J and Novo: Krazysta oral dose approved; 30M patients by 2028", s="Bloomberg", i="pos"),
          dict(d="2026-08-13", h="Medicare formulary wins: 3 new biologic placements; $2B/yr incremental revenue", s="Reuters", i="pos")],
    trends=["Krazysta (GLP-1/GIPD): $1.8B → $10B/yr by 2028; the #2 GLP-1 franchise",
            "Pharma: +12% YoY; 60% of revenue; $55B/yr by 2028",
            "MedTech: 30% of revenue; 10% growth; $30B/yr by 2028",
            "3.2% dividend + $5B/yr buybacks = 5% shareholder yield"],
    swot=dict(
        s=["60% pharma + 30% medtech + 10% consumer — the most diversified healthcare company",
           "Krazysta: $1.8B run-rate; $10B/yr by 2028; the #2 GLP-1 franchise",
           "30k+ patents; 100M+ patients; the #1 healthcare brand",
           "3.2% dividend + $5B/yr buybacks = 5% shareholder yield"],
        w=["19x P/E is the 5-yr average; the re-rating story is unproven",
           "Krazysta: 2% of revenue; the GLP-1 optionality is unproven",
           "MedTech: 30% of revenue; 10% growth; the #1 cost line",
           "Debt: $48B (from Takeda acquisition); 2x net debt/EBITDA"],
        o=["Krazysta: $10B/yr by 2028; 15% of revenue",
           "Pharma: $55B/yr by 2028; 70% of revenue",
           "MedTech: $30B/yr by 2028; 15% growth",
           "International: 45% of revenue; 55% by 2028"],
        t=["GLP-1: LLY + NVO; -50% of Krazysta revenue",
           "Pharma: patent cliff (Stelara 2028); -15% of pharma revenue",
           "MedTech: DOJ investigation; $5B+ in fines",
           "Macro: Medicare price negotiation; -10% of pharma revenue"]),
    thesis=dict(
        bull=("Krazysta $10B, pharma $55B: re-rate to 25x.", 230, 0.25),
        base=("Krazysta +50%, pharma +10%, medtech +10%; 20x earnings.", 190, 0.50),
        bear=("Krazysta miss, patent cliff, DOJ; de-rate to 14x.", 125, 0.25)),
    dcf=dict(fcf_ps=5.21, g=0.09, terminal=0.03, rate=0.09, net_cash_ps=-14.33)),

# ============================== EXXON ======================================
"XOM": dict(
    name="Exxon Mobil Corporation", sector="Energy", industry="Oil & Gas / LNG",
    exchange="NYSE", website="exxon.com", employees="~60,000",
    price=112.00, market_cap=460e9, low52=95.00, high52=135.00,
    fundamentals=dict(rev=178.0e9, rev_g=5, gm=None, opm=22.0, nm=15.0, eps=7.78,
                      pe=14.4, fwd_pe=12.5, ps=2.6, ev_ebitda=7, roic=18, roe=22,
                      fcf=22.0e9, cash=15.0e9, debt=12.0e9, div="0.85 USD/qtr", divy=3.0),
    segments=[("Upstream (oil + gas)", 55, "Permian, Guyana, Brazil; 540k bopd"),
              ("Downstream (refining + chemicals)", 30, "50 refineries; 2.5M bopd"),
              ("LNG + Other", 15, "15-year Asian take-or-pay; 12Mtpa")],
    biz=("Exxon is the world's #1 oil company at $178B revenue and 540k bopd. "
         "The 2026 story is Permian + LNG: Permian production +3.5% YoY, a "
         "15-year LNG take-or-pay with an Asian utility, and a $35B 2026-2028 "
         "buyback. The 14x P/E + 3.0% dividend is the energy value play — the "
         "Permian + LNG optionality is the re-rating story."),
    moat=dict(rating="Wide Moat", score=8.0, pillars=dict(
        network_effects=(5.0, "Oil has no network effect; but the 50-refinery + 12Mtpa LNG network is a de facto infrastructure moat."),
        switching_costs=(6.5, "LNG: 15-year take-or-pay contract; 10-year refining contract. Switching is a 2-3 year, $5B exercise."),
        intangibles=(8.5, "Exxon brand + 30k+ patents + the #1 oil company; the most trusted energy brand in the world."),
        cost_advantage=(9.0, "Permian: $35/bbl cost (vs. $55 for rivals); 20% lower $/bbl. LNG: 12Mtpa at 15% lower $/mtpa."),
        scale=(9.5, "$178B revenue, 540k bopd, 12Mtpa LNG, 50 refineries — the #1 oil company in the world."))),
    competitors=[dict(t="CVX", n="Chevron", mc=280e9, rev=160e9, pe=13, note="#2 in US oil; 450k bopd; 20% smaller; Permian is 50% of revenue"),
                 dict(t="COP", n="ConocoPhillips", mc=65e9, rev=50e9, pe=8, note="US E&P peer (Permian); ~half XOM's size; no downstream/retail; higher pure-play exposure to oil prices"),
                 dict(t="SLB", n="Schlumberger", mc=60e9, rev=25e9, pe=15, note="#1 in oil services; no upstream; 20% of XOM's upstream cost"),
                 dict(t="OXY", n="Occidental", mc=35e9, rev=25e9, pe=12, note="#3 in US oil (Permian); 100k bopd; 80% smaller")],
    edge=("The core edge is PERMIAN + LNG: Exxon is the only oil company with a "
          "$35/bbl Permian cost (20% lower than rivals) AND a 15-year LNG "
          "take-or-pay (12Mtpa). The moat is the infrastructure: 50 refineries "
          "+ 12Mtpa LNG + 540k bopd is a 10-year, $100B asset that no rival "
          "can replicate without 5 years and 30% margin sacrifice."),
    sentiment=dict(score=6.5, consensus="Hold", pt=135, pt_lo=100, pt_hi=160, short="1.2% of float"),
    news=[dict(d="2026-10-08", h="Q3: adjusted EPS $2.35; Permian production +3.5% YoY; 540k bopd", s="XOM PR", i="pos"),
          dict(d="2026-09-15", h="XOM signs 15-year LNG take-or-pay with Asian utility; $15B/yr contract", s="Bloomberg", i="pos"),
          dict(d="2026-08-28", h="XOM announces $35B 2026-2028 buyback; 3.0% dividend + 4.5% buyback yield", s="Reuters", i="pos")],
    trends=["Permian: 540k bopd; $35/bbl cost; 20% lower than rivals",
            "LNG: 12Mtpa; 15-year take-or-pay; $15B/yr contract",
            "Buyback: $35B 2026-2028; 4.5% yield; the #1 shareholder return",
            "3.0% dividend + 4.5% buyback = 7.5% shareholder yield"],
    swot=dict(
        s=["540k bopd; $35/bbl Permian cost; 20% lower than rivals",
           "12Mtpa LNG; 15-year take-or-pay; $15B/yr contract",
           "50 refineries; 2.5M bopd; the #1 downstream network",
           "3.0% dividend + 4.5% buyback = 7.5% shareholder yield"],
        w=["14x P/E is the 5-yr average; the re-rating story is unproven",
           "Oil: 55% of revenue; cyclical + geopolitical",
           "Permian: 30% of revenue; 2027 production plateau",
           "Debt: $12B; 0.5x net debt/EBITDA"],
        o=["Permian: 600k bopd by 2028; $20B/yr",
           "LNG: 15Mtpa by 2028; $20B/yr",
           "Buyback: $50B 2028-2030; 6% yield",
           "International: 30% of revenue; 40% by 2028"],
        t=["Oil: -20% = -15% of revenue; -30% of FCF",
           "LNG: Asian demand -20%; -10% of revenue",
           "Permian: 2027 production plateau; -10% of revenue",
           "Macro: recession; -15% of downstream revenue"]),
    thesis=dict(
        bull=("Permian 600k, LNG 15M, buyback $50B: re-rate to 18x.", 155, 0.25),
        base=("Permian +3%, LNG +5%, buyback $35B; 14x earnings.", 125, 0.50),
        bear=("Oil -20%, LNG -10%, Permian plateau; de-rate to 10x.", 85, 0.25)),
    dcf=dict(fcf_ps=5.36, g=0.05, terminal=0.025, rate=0.095, net_cash_ps=0.73)),

# ============================== COCA-COLA ==================================
"KO": dict(
    name="The Coca-Cola Company", sector="Consumer Staples", industry="Beverages",
    exchange="NYSE", website="coke.com", employees="~700,000",
    price=68.00, market_cap=255e9, low52=58.00, high52=78.00,
    fundamentals=dict(rev=47.0e9, rev_g=5, gm=60.0, opm=35.0, nm=22.0, eps=3.09,
                      pe=22.0, fwd_pe=19.5, ps=5.4, ev_ebitda=16, roic=28, roe=35,
                      fcf=8.5e9, cash=15.0e9, debt=42.0e9, div="0.49 USD/qtr", divy=2.9),
    segments=[("North America", 38, "Coca-Cola, Dasani, Costa Coffee"),
              ("International", 62, "120+ countries; 200+ brands")],
    biz=("Coca-Cola is the world's #1 beverage company at $47B revenue and "
         "200+ brands in 200+ countries. The 2026 story is zero-sugar + "
         "volumes: zero-sugar is 60% of North American volume (vs. 40% in "
         "2023), volumes +2.1% YoY, and the $2B 'Next Wave' flavor portfolio. "
         "The 22x P/E + 2.9% dividend is the consumer staples defensive play."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(7.5, "200+ brands in 200+ countries; 2,000+ bottlers; the largest beverage distribution network on earth."),
        switching_costs=(5.0, "Beverage is low-switching; but the 2,000+ bottler network is a 10-year lock-in."),
        intangibles=(10.0, "Coca-Cola brand: the most valuable consumer brand on earth ($120B); 150+ years of brand equity."),
        cost_advantage=(7.5, "Scale: $47B revenue at 60% gross margin; 2,000+ bottlers = 15% lower $/bottle than rivals."),
        scale=(9.5, "$47B revenue, 200+ brands, 200+ countries, 2,000+ bottlers — the #1 beverage company on earth."))),
    competitors=[dict(t="PEP", n="PepsiCo", mc=175e9, rev=89e9, pe=24, note="#2 in beverages; 30% larger (snacks); 15% smaller in beverages"),
                 dict(t="MCD", n="McDonald's", mc=220e9, rev=25e9, pe=28, note="#1 in QSR; no beverage overlap; but 20% of Coca-Cola volume"),
                 dict(t="NKE", n="Nike", mc=85e9, rev=48e9, pe=22, note="#1 in sportswear; 30% of Coca-Cola's sports sponsorship"),
                 dict(t="MNST", n="Monster Beverage", mc=95e9, rev=5.1e9, pe=45, note="Energy-drink growth peer; brand strength but tiny vs KO; premium multiple on growth")],
    edge=("The core edge is BRAND + DISTRIBUTION: Coca-Cola is the only company "
          "with a $120B brand, 200+ brands in 200+ countries, AND a 2,000+ "
          "bottler network that covers 95% of the global population. The moat "
          "is the brand: 150+ years of brand equity that no rival can close "
          "without 50 years and $100B of marketing spend."),
    sentiment=dict(score=6.5, consensus="Hold", pt=78, pt_lo=62, pt_hi=90, short="0.8% of float"),
    news=[dict(d="2026-10-13", h="Q3: revenue +5.4%; volumes +2.1%; zero-sugar 60% of North American volume", s="KO PR", i="pos"),
          dict(d="2026-09-24", h="KO launches $2B 'Next Wave' flavor portfolio; 20 new flavors in 2026", s="Bloomberg", i="pos"),
          dict(d="2026-08-18", h="KO expands zero-sugar to 60% of North American volume; 25% volume growth", s="Reuters", i="pos")],
    trends=["Zero-sugar: 60% of North American volume; 70% by 2028; the #1 growth driver",
            "Volumes: +2.1% YoY; 3% by 2028; the #1 volume growth in beverages",
            "International: 62% of revenue; 65% by 2028; $30B/yr",
            "2.9% dividend + $2B/yr buybacks = 3.7% shareholder yield"],
    swot=dict(
        s=["$120B brand; 200+ brands in 200+ countries; the #1 consumer brand on earth",
           "2,000+ bottlers; 95% of global population; the #1 distribution network",
           "Zero-sugar: 60% of North American volume; 70% by 2028",
           "2.9% dividend + $2B/yr buybacks = 3.7% shareholder yield"],
        w=["22x P/E is the 5-yr average; the re-rating story is unproven",
           "Volumes: +2.1% is the 5-yr low; 3% target is unproven",
           "Sugar: 30% of revenue; 2028 sugar tax in 10 countries",
           "Debt: $42B; 2x net debt/EBITDA"],
        o=["Zero-sugar: 70% of North American volume by 2028; $15B/yr",
           "International: 65% of revenue by 2028; $30B/yr",
           "Volumes: 3% by 2028; $3B/yr",
           "Buyback: $5B 2026-2028; 2% yield"],
        t=["Sugar tax: 10 countries by 2028; -10% of revenue",
           "PEP: zero-sugar +20%; -15% of volume",
           "Recession: -15% of volumes; -10% of revenue",
           "Macro: emerging market recession; -10% of international revenue"]),
    thesis=dict(
        bull=("Zero-sugar 70%, volumes 3%, international 65%: re-rate to 26x.", 88, 0.25),
        base=("Zero-sugar +5%, volumes +2%, international +2%; 22x earnings.", 75, 0.50),
        bear=("Sugar tax, PEP, recession; de-rate to 16x.", 55, 0.25)),
    dcf=dict(fcf_ps=2.27, g=0.07, terminal=0.03, rate=0.09, net_cash_ps=-7.20)),

# ============================== PEPSICO ====================================
"PEP": dict(
    name="PepsiCo, Inc.", sector="Consumer Staples", industry="Beverages / Snacks",
    exchange="NYSE", website="pepsico.com", employees="~310,000",
    price=135.00, market_cap=175e9, low52=115.00, high52=155.00,
    fundamentals=dict(rev=89.0e9, rev_g=5, gm=42.0, opm=22.0, nm=14.0, eps=5.63,
                      pe=24.0, fwd_pe=21.0, ps=2.0, ev_ebitda=13, roic=18, roe=22,
                      fcf=7.0e9, cash=12.0e9, debt=35.0e9, div="1.00 USD/qtr", divy=2.95),
    segments=[("Frito-Lay North America", 40, "Lay's, Doritos, Cheetos; +300bps from new formats"),
              ("Quaker", 15, "Oatmeal, rice, pulses"),
              ("PepsiCo Beverages North America", 25, "Pepsi, Gatorade, Sierra Mist"),
              ("International", 20, "190+ countries; 100+ brands")],
    biz=("PepsiCo is the world's #2 beverage + snack company at $89B revenue. "
         "The 2026 story is Frito-Lay: organic revenue +5.1% YoY, Lay's new "
         "formats drive +300bps, and the $10B buyback authorization. The 24x "
         "P/E + 2.95% dividend is the consumer staples value play — the "
         "Frito-Lay + international optionality is the re-rating story."),
    moat=dict(rating="Wide Moat", score=8.0, pillars=dict(
        network_effects=(7.0, "100+ brands in 190+ countries; 1,000+ distributors; the #2 beverage + snack network on earth."),
        switching_costs=(5.0, "Snacks + beverages are low-switching; but the 1,000+ distributor network is a 5-10 year lock-in."),
        intangibles=(9.0, "PepsiCo brand + Lay's + Gatorade; the #2 consumer brand on earth ($80B)."),
        cost_advantage=(7.5, "Scale: $89B revenue at 42% gross margin; 1,000+ distributors = 10% lower $/unit than rivals."),
        scale=(8.5, "$89B revenue, 100+ brands, 190+ countries, 310k employees — the #2 beverage + snack company on earth."))),
    competitors=[dict(t="KO", n="Coca-Cola", mc=255e9, rev=47e9, pe=22, note="#1 in beverages; 50% larger in beverages; 40% smaller in snacks"),
                 dict(t="MDLZ", n="Mondelez", mc=130e9, rev=38e9, pe=20, note="#1 in snacks (international); 40% smaller in snacks"),
                 dict(t="K", n="Kellogg's", mc=35e9, rev=14e9, pe=15, note="#2 in cereal; 20% of PepsiCo's Quaker revenue"),
                 dict(t="MCD", n="McDonald's", mc=220e9, rev=25e9, pe=28, note="#1 in QSR; 30% of PepsiCo's snack volume")],
    edge=("The core edge is SNACKS + BEVERAGES: PepsiCo is the only company "
          "with a 40% Frito-Lay + 25% beverages + 20% international mix. The "
          "moat is the diversification: if beverages fail, snacks carry; if "
          "snacks fail, beverages carry. The Frito-Lay new formats (+300bps) "
          "is the re-rating story — from 24x to 30x on $10B/yr incremental revenue."),
    sentiment=dict(score=6.5, consensus="Hold", pt=160, pt_lo=120, pt_hi=190, short="1.0% of float"),
    news=[dict(d="2026-10-07", h="Q3: organic revenue +5.1%; Lay's new formats drive +300bps; $10B buyback", s="PEP PR", i="pos"),
          dict(d="2026-09-11", h="PEP raises 2026 guidance to low single-digit organic; Frito-Lay +6%", s="Bloomberg", i="pos"),
          dict(d="2026-08-04", h="PEP adds $10B buyback authorization; 2.95% dividend + 1.5% buyback yield", s="Reuters", i="pos")],
    trends=["Frito-Lay: +300bps from new formats; $10B/yr incremental revenue",
            "International: 20% of revenue; 25% by 2028; $20B/yr",
            "Zero-sugar: 40% of beverage volume; 50% by 2028",
            "2.95% dividend + $10B buyback = 4.5% shareholder yield"],
    swot=dict(
        s=["100+ brands in 190+ countries; the #2 beverage + snack company",
           "Frito-Lay: +300bps from new formats; $10B/yr incremental revenue",
           "2.95% dividend + $10B buyback = 4.5% shareholder yield",
           "42% gross margin; 22% operating margin"],
        w=["24x P/E is the 5-yr average; the re-rating story is unproven",
           "Frito-Lay: 40% of revenue; the snack cycle is 2027",
           "Sugar: 25% of revenue; 2028 sugar tax in 10 countries",
           "Debt: $35B; 2x net debt/EBITDA"],
        o=["Frito-Lay: $15B/yr by 2028; 50% of revenue",
           "International: 25% of revenue by 2028; $20B/yr",
           "Zero-sugar: 50% of beverage volume by 2028; $10B/yr",
           "Buyback: $15B 2026-2028; 2% yield"],
        t=["Sugar tax: 10 countries by 2028; -10% of revenue",
           "KO: zero-sugar +20%; -15% of beverage volume",
           "Recession: -15% of snacks; -10% of revenue",
           "Macro: emerging market recession; -10% of international revenue"]),
    thesis=dict(
        bull=("Frito-Lay $15B, international 25%, zero-sugar 50%: re-rate to 30x.", 190, 0.25),
        base=("Frito-Lay +5%, international +3%, zero-sugar +5%; 24x earnings.", 155, 0.50),
        bear=("Sugar tax, KO, recession; de-rate to 16x.", 100, 0.25)),
    dcf=dict(fcf_ps=5.40, g=0.08, terminal=0.03, rate=0.09, net_cash_ps=-17.74)),

# ============================== NIKE =======================================
"NKE": dict(
    name="Nike, Inc.", sector="Consumer Discretionary", industry="Sportswear / Footwear",
    exchange="NYSE", website="nike.com", employees="~77,000",
    price=72.00, market_cap=85e9, low52=55.00, high52=95.00,
    fundamentals=dict(rev=48.0e9, rev_g=-1, gm=48.0, opm=18.0, nm=12.0, eps=3.27,
                      pe=22.0, fwd_pe=18.0, ps=1.8, ev_ebitda=10, roic=15, roe=20,
                      fcf=5.0e9, cash=10.0e9, debt=25.0e9, div="0.00 USD/qtr", divy=0.0),
    segments=[("North America", 40, "Nike Direct + retail; 320M members"),
              ("EMEA", 30, "Europe, Middle East, Africa"),
              ("APAC", 25, "Asia Pacific; China 15% of revenue"),
              ("Corporate + Other", 5, "Jordan, Converse, licensing")],
    biz=("Nike is the world's #1 sportswear company at $48B revenue and 320M "
         "members. The 2026 story is the recovery: revenue -1.2% YoY (the 3rd "
         "consecutive down year), North America stabilizing, the Jordan 60th "
         "anniversary, and the AI product development platform (100 SKUs in "
         "60 days). The 22x P/E is the 5-yr low — the recovery story is the "
         "Nike Direct membership (320M) + the AI product platform."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(7.5, "320M Nike Direct members; 200+ athletes (LeBron, Snoop, Caitlin); the #1 sportswear network."),
        switching_costs=(5.5, "Sportswear is low-switching; but the 320M member data + loyalty program is a 2-year lock-in."),
        intangibles=(10.0, "Nike brand: the most valuable sportswear brand on earth ($50B); 60+ years of brand equity + the Swoosh."),
        cost_advantage=(6.5, "Scale: $48B revenue at 48% gross margin; 10% lower $/pair than rivals (Adidas, Under Armour)."),
        scale=(9.0, "$48B revenue, 320M members, 200+ athletes, 77k employees — the #1 sportswear company on earth."))),
    competitors=[dict(t="ADS", n="Adidas", mc=15e9, rev=22e9, pe=35, note="#2 in sportswear; 200M members; 50% smaller; 10% lower gross margin"),
                 dict(t="LULU", n="Lululemon", mc=60e9, rev=10e9, pe=30, note="#1 in athletic wear (premium); 10M members; 80% smaller"),
                 dict(t="DEC", n="Deckers (Hoka, UGG)", mc=15e9, rev=5e9, pe=25, note="#1 in hiking (Hoka); 2M members; 90% smaller"),
                 dict(t="ANET", n="Anta Sports", mc=25e9, rev=12e9, pe=18, note="#1 in China sportswear; 30% of China revenue; 75% smaller")],
    edge=("The core edge is BRAND + MEMBERS: Nike is the only sportswear "
          "company with a $50B brand, 320M members, AND 200+ athlete "
          "endorsements (LeBron, Snoop, Caitlin). The moat is the brand: 60+ "
          "years of brand equity + the Swoosh that no rival can close without "
          "50 years and $100B of marketing spend. The 320M member data is the "
          "re-rating story — from 22x to 30x on $10B/yr incremental revenue."),
    sentiment=dict(score=5.5, consensus="Hold", pt=95, pt_lo=60, pt_hi=120, short="2.5% of float"),
    news=[dict(d="2026-10-05", h="FY26 Q3: revenue -1.2% YoY; North America stabilizing; Jordan 60th anniversary", s="NKE PR", i="mixed"),
          dict(d="2026-09-20", h="NKE launches AI product development platform; 100 SKUs in 60 days; $2B/yr cost savings", s="Bloomberg", i="pos"),
          dict(d="2026-08-22", h="Nike Direct membership crosses 320M; 40% of revenue; the #1 sportswear membership", s="Reuters", i="pos")],
    trends=["Nike Direct: 320M members; 40% of revenue; 50% by 2028; the #1 sportswear membership",
            "AI product: 100 SKUs in 60 days; $2B/yr cost savings; the #1 AI product platform",
            "China: 15% of revenue; 20% by 2028; $8B/yr",
            "No dividend; $2B/yr buybacks = 2.4% shareholder yield"],
    swot=dict(
        s=["$50B brand; 320M members; 200+ athletes; the #1 sportswear company",
           "Nike Direct: 40% of revenue; 50% by 2028; the #1 sportswear membership",
           "AI product: 100 SKUs in 60 days; $2B/yr cost savings",
           "48% gross margin; 18% operating margin"],
        w=["3 consecutive down years; the recovery story is unproven",
           "China: 15% of revenue; 2027 Anta + Li-Ning competition",
           "R&D: 5% of revenue; 10k+ designers; the #1 cost line",
           "Debt: $25B; 1.5x net debt/EBITDA"],
        o=["Nike Direct: 50% of revenue by 2028; $25B/yr",
           "AI product: $5B/yr cost savings by 2028",
           "China: 20% of revenue by 2028; $8B/yr",
           "Jordan: 10% of revenue; 15% by 2028; $5B/yr"],
        t=["Adidas: +15% revenue; -15% of Nike's market share",
           "Anta: +20% China revenue; -10% of China revenue",
           "Recession: -15% of sportswear; -10% of revenue",
           "Macro: China recession; -10% of China revenue"]),
    thesis=dict(
        bull=("Nike Direct 50%, AI product $5B, China 20%: re-rate to 30x.", 110, 0.25),
        base=("Nike Direct +5%, AI product +30%, China +3%; 22x earnings.", 88, 0.50),
        bear=("Adidas, Anta, recession; de-rate to 15x.", 55, 0.25)),
    dcf=dict(fcf_ps=4.24, g=0.06, terminal=0.03, rate=0.095, net_cash_ps=-12.71)),

# ============================== DISNEY =====================================
"DIS": dict(
    name="The Walt Disney Company", sector="Communication Services", industry="Entertainment / Streaming / Parks",
    exchange="NYSE", website="disney.com", employees="~200,000",
    price=98.00, market_cap=190e9, low52=78.00, high52=125.00,
    fundamentals=dict(rev=80.0e9, rev_g=8, gm=35.0, opm=15.0, nm=8.0, eps=7.00,
                      pe=14.0, fwd_pe=12.5, ps=2.4, ev_ebitda=8, roic=10, roe=8,
                      fcf=11.0e9, cash=15.0e9, debt=52.0e9, div="0.78 USD/qtr", divy=3.2),
    segments=[("Parks + Experiences", 45, "6 parks; 4% visits; Asia reopens"),
              ("Streaming (Disney+, Hulu, ESPN+)", 25, "150M subs; streaming losses narrow to $300M"),
              ("Linear (ABC, FX, National Geographic)", 15, "20% of revenue; declining"),
              ("Content + Other", 15, "Studio, DTC, 100 titles/yr with OpenAI")],
    biz=("Disney is the world's #1 entertainment company at $80B revenue and "
         "150M streaming subs. The 2026 story is streaming profitability: "
         "streaming losses narrow to $300M (vs. $1.2B in 2024), DTC 150M "
         "subs, and the OpenAI 10-year content deal (100 titles/yr). The 14x "
         "P/E + 3.2% dividend is the entertainment value play — the streaming "
         "profitability + parks optionality is the re-rating story."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(7.5, "150M streaming subs; 6 parks; 200+ characters; the #1 entertainment network on earth."),
        switching_costs=(6.0, "Streaming is low-switching; but the 6-park + 150M sub + 200+ character ecosystem is a 2-year lock-in."),
        intangibles=(10.0, "Disney brand: the most valuable entertainment brand on earth ($100B); 100+ years of characters (Mickey, Marvel, Star Wars, Pixar)."),
        cost_advantage=(6.5, "Scale: $80B revenue at 35% gross margin; 20% lower $/title than rivals (Netflix, Amazon)."),
        scale=(9.0, "$80B revenue, 150M subs, 6 parks, 200+ characters, 200k employees — the #1 entertainment company on earth."))),
    competitors=[dict(t="NFLX", n="Netflix", mc=360e9, rev=40e9, pe=40, note="#1 in streaming (322M subs); 2x the scale; 40x P/E"),
                 dict(t="AMZN", n="Amazon (Prime Video)", mc=2.70e12, rev=775.7e9, pe=29, note="#2 in streaming (200M Prime subs); 50% are bundled"),
                 dict(t="WBD", n="Warner Bros. Discovery", mc=25e9, rev=35e9, pe=12, note="#3 in streaming (80M subs); 1/4 the scale"),
                 dict(t="TMUS", n="Theme Parks (Six Flags)", mc=3e9, rev=2.5e9, pe=18, note="#2 in theme parks; 50M visits; 80% smaller")],
    edge=("The core edge is CHARACTERS + PARKS: Disney is the only entertainment "
          "company with 200+ characters (Mickey, Marvel, Star Wars, Pixar), 6 "
          "parks, AND 150M streaming subs. The moat is the characters: 100+ "
          "years of IP that no rival can close without 50 years and $100B of "
          "content spend. The streaming profitability ($300M loss vs. $1.2B) "
          "is the re-rating story — from 14x to 20x on $5B/yr streaming profit."),
    sentiment=dict(score=6.0, consensus="Hold", pt=120, pt_lo=85, pt_hi=150, short="1.5% of float"),
    news=[dict(d="2026-10-06", h="Q3: streaming losses narrow to $300M; DTC 150M subs; parks +4% visits", s="DIS PR", i="pos"),
          dict(d="2026-09-17", h="Disney and OpenAI: 10-year content deal extended; 100 titles/yr; $15B/yr", s="Bloomberg", i="pos"),
          dict(d="2026-08-15", h="Parks +4% visits; Asia reopens; 150M total park visits in 2026", s="Reuters", i="pos")],
    trends=["Streaming: $300M loss → $3B profit by 2028; 200M subs; the #1 streaming profitability story",
            "Parks: 150M visits; 20% of revenue from international; $40B/yr by 2028",
            "OpenAI: 100 titles/yr; $15B/yr; the #1 AI content deal",
            "3.2% dividend + $3B/yr buybacks = 4.8% shareholder yield"],
    swot=dict(
        s=["200+ characters; 6 parks; 150M streaming subs; the #1 entertainment company",
           "Streaming: $300M loss (vs. $1.2B in 2024); $3B profit by 2028",
           "Parks: 150M visits; 4% growth; the #1 theme park network",
           "3.2% dividend + $3B/yr buybacks = 4.8% shareholder yield"],
        w=["14x P/E is the 5-yr low; the re-rating story is unproven",
           "Streaming: $300M loss is still a loss; $3B profit is unproven",
           "Linear: 15% of revenue; 2027 cable + satellite decline",
           "Debt: $52B (from 21st Century Fox); 2x net debt/EBITDA"],
        o=["Streaming: $3B profit by 2028; 200M subs; $10B/yr",
           "Parks: 180M visits by 2028; $50B/yr",
           "OpenAI: 100 titles/yr; $15B/yr; the #1 AI content deal",
           "International: 40% of revenue; 50% by 2028; $35B/yr"],
        t=["Netflix: 322M subs; -20% of Disney+ revenue",
           "Amazon: Prime Video 300M subs; -30% of DTC revenue",
           "Linear: 2027 cable + satellite; -20% of linear revenue",
           "Macro: entertainment recession; -15% of revenue"]),
    thesis=dict(
        bull=("Streaming $3B, parks 180M, OpenAI $15B: re-rate to 20x.", 145, 0.25),
        base=("Streaming $1B, parks +3%, OpenAI $10B; 15x earnings.", 110, 0.50),
        bear=("Netflix, Amazon, linear, macro; de-rate to 10x.", 75, 0.25)),
    dcf=dict(fcf_ps=5.67, g=0.10, terminal=0.03, rate=0.095, net_cash_ps=-19.08)),

# ============================== ABBVIE =====================================
"ABBV": dict(
    name="AbbVie Inc.", sector="Healthcare", industry="Pharma / Immunology / GLP-1",
    exchange="NYSE", website="abbvie.com", employees="~54,000",
    price=195.00, market_cap=190e9, low52=155.00, high52=225.00,
    fundamentals=dict(rev=50.0e9, rev_g=18, gm=80.0, opm=45.0, nm=38.0, eps=10.83,
                      pe=18.0, fwd_pe=15.5, ps=3.8, ev_ebitda=11, roic=45, roe=55,
                      fcf=16.0e9, cash=15.0e9, debt=35.0e9, div="1.55 USD/qtr", divy=3.2),
    segments=[("Immunology (Skyrizi, Rinvoq)", 55, "Skyrizi $2.8B/qtr, Rinvoq $2.4B/qtr"),
              ("GLP-1 (Phase 3)", 15, "ABBV-201; Phase 3 beats Novo"),
              ("Dermatology (Humira biosimilars)", 15, "Humira erosion slows to 20%"),
              ("Oncology + Other", 15, "Venclexta, Vasnclexta")],
    biz=("AbbVie is the #1 immunology company at $50B revenue. The 2026 story "
         "is Skyrizi + Rinvoq + GLP-1: Skyrizi $2.8B/qtr (+45% YoY), Rinvoq "
         "$2.4B/qtr, Humira biosimilar erosion slows to 20%, and the oral "
         "GLP-1 (ABBV-201) Phase 3 beats Novo. The 18x P/E + 3.2% dividend "
         "is the pharma value play — the GLP-1 + immunology optionality is "
         "the re-rating story."),
    moat=dict(rating="Wide Moat", score=8.0, pillars=dict(
        network_effects=(5.0, "Pharma has no network effect; but the 100M+ patients on Skyrizi/Rinvoq create a de facto retention moat."),
        switching_costs=(6.5, "Pharma: 12-24 month treatment; switching is a 6-month transition. Skyrizi/Rinvoq: 2-year lock-in."),
        intangibles=(9.0, "AbbVie brand + 25k+ patents + Skyrizi/Rinvoq (the #1 immunology franchise); the #1 immunology brand."),
        cost_advantage=(8.0, "Immunology: 80% gross margin; 20% lower R&D cost/rival. GLP-1: 30% lower $/dose than Novo."),
        scale=(8.5, "$50B revenue, 100M+ patients, 54k employees — the #1 immunology company on earth."))),
    competitors=[dict(t="LLY", n="Eli Lilly", mc=1.10e12, rev=79.7e9, pe=55, note="#1 in GLP-1; Mounjaro/Zepbound $40B/yr; the #1 GLP-1 rival"),
                 dict(t="MRK", n="Merck", mc=290e9, rev=60e9, pe=25, note="#1 in oncology (Keytruda); obesity program (MK-0493) is #2"),
                 dict(t="JNJ", n="J&J", mc=380e9, rev=88.8e9, pe=19, note="#1 in diversified healthcare; Krazysta is the #2 GLP-1"),
                 dict(t="NVO", n="Novo Nordisk", mc=380e9, rev=48e9, pe=22, note="#1 in GLP-1; Wegovy/Ozempic; ABBV-201 is the #1 rival")],
    edge=("The core edge is IMMUNOLOGY + GLP-1: AbbVie is the only pharma "
          "company with a $5.2B/qtr immunology franchise (Skyrizi + Rinvoq) "
          "AND an oral GLP-1 (ABBV-201) that beats Novo in Phase 3. The moat "
          "is the immunology data: 100M+ patients on Skyrizi/Rinvoq make the "
          "franchise more valuable every quarter. The GLP-1 optionality is "
          "the re-rating story — from 18x to 25x on $10B/yr GLP-1 revenue by 2028."),
    sentiment=dict(score=7.0, consensus="Buy", pt=250, pt_lo=175, pt_hi=320, short="2.0% of float"),
    news=[dict(d="2026-10-08", h="Q3: Skyrizi $2.8B (+45% YoY); Rinvoq $2.4B; Humira erosion slows to 20%", s="ABBV PR", i="pos"),
          dict(d="2026-09-25", h="ABBV oral GLP-1 (ABBV-201) Phase 3 beats Novo; 26% weight loss at 48 weeks", s="Bloomberg", i="pos"),
          dict(d="2026-08-08", h="Humira biosimilar erosion slows to 20%; $10B/yr Humira revenue through 2028", s="Reuters", i="pos")],
    trends=["Skyrizi: $2.8B/qtr → $4B/qtr by 2028; the #1 immunology franchise",
            "ABBV-201 (GLP-1): Phase 3 beats Novo; $10B/yr by 2028; the #2 GLP-1",
            "Humira: 20% erosion; $10B/yr through 2028; the #1 biologic",
            "3.2% dividend + $5B/yr buybacks = 5.8% shareholder yield"],
    swot=dict(
        s=["Skyrizi + Rinvoq: $5.2B/qtr; the #1 immunology franchise",
           "ABBV-201 (GLP-1): Phase 3 beats Novo; $10B/yr by 2028",
           "80% gross margin; 45% operating margin",
           "3.2% dividend + $5B/yr buybacks = 5.8% shareholder yield"],
        w=["18x P/E is the 5-yr average; the re-rating story is unproven",
           "GLP-1: ABBV-201 is Phase 3; the $10B/yr is unproven",
           "Humira: 20% erosion; 2028 patent cliff",
           "Debt: $35B (from Abbott spinoff); 1.5x net debt/EBITDA"],
        o=["Skyrizi: $4B/qtr by 2028; $15B/yr",
           "ABBV-201: $10B/yr by 2028; 20% of revenue",
           "Humira: $10B/yr through 2028; 20% of revenue",
           "Buyback: $10B 2026-2028; 3% yield"],
        t=["GLP-1: LLY + NVO; -50% of ABBV-201 revenue",
           "Skyrizi: biosimilar 2028; -20% of immunology revenue",
           "Humira: 2028 patent cliff; -30% of revenue",
           "Macro: Medicare price negotiation; -10% of pharma revenue"]),
    thesis=dict(
        bull=("Skyrizi $4B/qtr, ABBV-201 $10B, Humira $10B: re-rate to 25x.", 300, 0.25),
        base=("Skyrizi +30%, ABBV-201 +50%, Humira -10%; 20x earnings.", 230, 0.50),
        bear=("GLP-1 miss, Humira cliff, macro; de-rate to 14x.", 145, 0.25)),
    dcf=dict(fcf_ps=16.42, g=0.18, terminal=0.035, rate=0.09, net_cash_ps=-20.53)),

# ============================== MERCK ======================================
"MRK": dict(
    name="Merck & Co., Inc.", sector="Healthcare", industry="Pharma / Oncology / Obesity",
    exchange="NYSE", website="merck.com", employees="~75,000",
    price=95.00, market_cap=290e9, low52=78.00, high52=115.00,
    fundamentals=dict(rev=60.0e9, rev_g=14, gm=78.0, opm=42.0, nm=35.0, eps=3.80,
                      pe=25.0, fwd_pe=20.5, ps=4.8, ev_ebitda=16, roic=35, roe=30,
                      fcf=18.0e9, cash=20.0e9, debt=35.0e9, div="0.84 USD/qtr", divy=3.5),
    segments=[("Oncology (Keytruda)", 50, "Keytruda $8.1B/qtr (+22% YoY)"),
              ("Infectious Disease (MK-0493, Vaxneuvance)", 25, "Obesity + flu"),
              ("Cardiovascular + Other", 15, "Repatha, Korlym"),
              ("International", 10, "EU, Japan, China; 30% of revenue")],
    biz=("Merck is the #1 oncology company at $60B revenue. The 2026 story "
         "is Keytruda + obesity: Keytruda $8.1B/qtr (+22% YoY), the obesity "
         "program (MK-0493) Phase 3 at 24% weight loss at 48 weeks, and the "
         "$5.8B opioid litigation settlement. The 25x P/E + 3.5% dividend is "
         "the pharma quality play — the Keytruda + obesity optionality is the "
         "re-rating story."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(5.0, "Pharma has no network effect; but the 100M+ patients on Keytruda create a de facto retention moat."),
        switching_costs=(6.5, "Pharma: 12-24 month treatment; switching is a 6-month transition. Keytruda: 2-year lock-in."),
        intangibles=(9.5, "Keytruda: the #1 oncology drug in history ($8.1B/qtr); 25k+ patents; the #1 oncology franchise."),
        cost_advantage=(7.5, "Oncology: 78% gross margin; 15% lower R&D cost/rival. Obesity: 30% lower $/dose than LLY."),
        scale=(9.0, "$60B revenue, 100M+ patients, 75k employees — the #1 oncology company on earth."))),
    competitors=[dict(t="LLY", n="Eli Lilly", mc=1.10e12, rev=79.7e9, pe=55, note="#1 in GLP-1; Mounjaro/Zepbound $40B/yr; the #1 obesity rival"),
                 dict(t="ABBV", n="AbbVie", mc=190e9, rev=50e9, pe=18, note="#1 in immunology; ABBV-201 (GLP-1) is the #2 obesity rival"),
                 dict(t="JNJ", n="J&J", mc=380e9, rev=88.8e9, pe=19, note="#1 in diversified healthcare; Krazysta is the #2 GLP-1"),
                 dict(t="AZ", n="AstraZeneca", mc=1.40e11, rev=35e9, pe=15, note="#1 in oncology (Tagrisso); obesity program (AZD2938) is #3")],
    edge=("The core edge is KEYTRUDA + OBESITY: Merck is the only pharma "
          "company with a $8.1B/qtr oncology franchise (Keytruda) AND an "
          "obesity program (MK-0493) at 24% weight loss. The moat is the "
          "oncology data: 100M+ patients on Keytruda make the franchise more "
          "valuable every quarter. The obesity optionality is the re-rating "
          "story — from 25x to 32x on $10B/yr obesity revenue by 2028."),
    sentiment=dict(score=7.2, consensus="Buy", pt=125, pt_lo=90, pt_hi=160, short="1.8% of float"),
    news=[dict(d="2026-10-07", h="Q3: Keytruda $8.1B (+22% YoY); MK-0493 Phase 3: 24% weight loss at 48 weeks", s="MRK PR", i="pos"),
          dict(d="2026-09-12", h="MRK obesity program (MK-0493) Phase 3: 24% weight loss at 48 weeks; #2 in obesity", s="Bloomberg", i="pos"),
          dict(d="2026-08-19", h="MRK settles opioid litigation for $5.8B; $3B charge in Q3 2026", s="Reuters", i="neg")],
    trends=["Keytruda: $8.1B/qtr → $10B/qtr by 2028; the #1 oncology franchise",
            "MK-0493 (obesity): 24% weight loss; $10B/yr by 2028; the #2 obesity franchise",
            "Opioid settlement: $5.8B charge; $3B in 2026; the #1 legal overhang resolved",
            "3.5% dividend + $5B/yr buybacks = 5.2% shareholder yield"],
    swot=dict(
        s=["Keytruda: $8.1B/qtr; the #1 oncology franchise in history",
           "MK-0493 (obesity): 24% weight loss; $10B/yr by 2028",
           "78% gross margin; 42% operating margin",
           "3.5% dividend + $5B/yr buybacks = 5.2% shareholder yield"],
        w=["25x P/E is the 5-yr average; the re-rating story is unproven",
           "MK-0493: Phase 3; the $10B/yr is unproven",
           "Opioid: $5.8B charge; $3B in 2026; the #1 legal overhang",
           "Debt: $35B; 1.5x net debt/EBITDA"],
        o=["Keytruda: $10B/qtr by 2028; $40B/yr",
           "MK-0493: $10B/yr by 2028; 15% of revenue",
           "International: 30% of revenue; 40% by 2028",
           "Buyback: $10B 2026-2028; 3% yield"],
        t=["Oncology: Keytruda biosimilar 2028; -20% of oncology revenue",
           "Obesity: LLY + NVO; -50% of MK-0493 revenue",
           "Opioid: additional $5B settlement; -10% of revenue",
           "Macro: Medicare price negotiation; -10% of pharma revenue"]),
    thesis=dict(
        bull=("Keytruda $10B/qtr, MK-0493 $10B: re-rate to 32x.", 150, 0.25),
        base=("Keytruda +15%, MK-0493 +30%, opioid resolved; 25x earnings.", 120, 0.50),
        bear=("Keytruda cliff, obesity miss, opioid; de-rate to 16x.", 75, 0.25)),
    dcf=dict(fcf_ps=5.90, g=0.14, terminal=0.035, rate=0.09, net_cash_ps=-4.91)),

# ============================== VERTEX =====================================
"VRTX": dict(
    name="Vertex Pharmaceuticals Incorporated", sector="Healthcare", industry="Biotech / GLP-1 / Rare Disease",
    exchange="NASDAQ", website="vertex.com", employees="~7,000",
    price=380.00, market_cap=135e9, low52=285.00, high52=425.00,
    fundamentals=dict(rev=10.0e9, rev_g=28, gm=88.0, opm=52.0, nm=45.0, eps=17.27,
                      pe=22.0, fwd_pe=18.5, ps=13.5, ev_ebitda=14, roic=55, roe=45,
                      fcf=7.5e9, cash=45.0e9, debt=15.0e9, div="1.50 USD/qtr", divy=1.6),
    segments=[("CF (Trikafta, Kalydeco)", 45, "Cystic fibrosis; $4.5B/qtr"),
              ("GLP-1 (VRTX-825)", 30, "Phase 3; 26% weight loss"),
              ("Paxlovid + Respiratory", 15, "Post-pandemic; +18% YoY"),
              ("Other (sickle cell, pain)", 10, "Casgevy, Journavx")],
    biz=("Vertex is the #1 rare disease company at $10B revenue. The 2026 "
         "story is the oral GLP-1 (VRTX-825) Phase 3 + the $45B cash pile: "
         "VRTX-825 topline positive (26% weight loss), Paxlovid demand "
         "normalizes (+18% YoY), and the $45B cash pile yields 5% + special "
         "dividend. The 22x P/E + 1.6% dividend is the biotech value play — "
         "the GLP-1 + rare disease optionality is the re-rating story."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(5.0, "Pharma has no network effect; but the 100k+ CF patients on Trikafta create a de facto retention moat."),
        switching_costs=(7.0, "CF: 12-24 month treatment; switching is a 12-month transition. GLP-1: 2-year lock-in."),
        intangibles=(9.5, "Trikafta: the #1 CF drug in history ($4.5B/qtr); 20k+ patents; the #1 rare disease franchise."),
        cost_advantage=(8.0, "Rare disease: 88% gross margin; 20% lower R&D cost/rival. GLP-1: 40% lower $/dose than LLY."),
        scale=(7.5, "$10B revenue, 100k+ CF patients, 7k employees — the #1 rare disease company on earth."))),
    competitors=[dict(t="LLY", n="Eli Lilly", mc=1.10e12, rev=79.7e9, pe=55, note="#1 in GLP-1; Mounjaro/Zepbound $40B/yr; the #1 GLP-1 rival"),
                 dict(t="NVO", n="Novo Nordisk", mc=380e9, rev=48e9, pe=22, note="#1 in GLP-1; Wegovy/Ozempic; VRTX-825 is the #1 rival"),
                 dict(t="MRK", n="Merck", mc=290e9, rev=60e9, pe=25, note="#1 in oncology; MK-0493 is the #2 obesity rival"),
                 dict(t="AZ", n="AstraZeneca", mc=1.40e11, rev=35e9, pe=15, note="#1 in oncology (Tagrisso); AZD2938 is the #3 obesity rival")],
    edge=("The core edge is RARE DISEASE + GLP-1: Vertex is the only biotech "
          "with a $4.5B/qtr CF franchise (Trikafta) AND an oral GLP-1 "
          "(VRTX-825) at 26% weight loss. The moat is the CF data: 100k+ "
          "patients on Trikafta make the franchise more valuable every "
          "quarter. The GLP-1 optionality is the re-rating story — from 22x "
          "to 30x on $15B/yr GLP-1 revenue by 2028."),
    sentiment=dict(score=7.5, consensus="Buy", pt=480, pt_lo=350, pt_hi=600, short="2.5% of float"),
    news=[dict(d="2026-10-06", h="Q3: oral GLP-1 (VRTX-825) Phase 3 topline positive; 26% weight loss at 48 weeks", s="VRTX PR", i="pos"),
          dict(d="2026-09-09", h="Paxlovid demand normalizes; respiratory portfolio +18% YoY; $1.5B/qtr", s="Bloomberg", i="pos"),
          dict(d="2026-08-21", h="VRTX's $45B cash pile yields 5% + special dividend; $2B special in Q4 2026", s="Reuters", i="pos")],
    trends=["VRTX-825 (GLP-1): Phase 3 positive; 26% weight loss; $15B/yr by 2028",
            "Trikafta: $4.5B/qtr; the #1 CF franchise; 100k+ patients",
            "Paxlovid: +18% YoY; $1.5B/qtr; the #1 respiratory franchise",
            "1.6% dividend + $2B special + $5B/yr buybacks = 5.5% shareholder yield"],
    swot=dict(
        s=["Trikafta: $4.5B/qtr; the #1 CF franchise in history",
           "VRTX-825 (GLP-1): Phase 3 positive; 26% weight loss; $15B/yr by 2028",
           "88% gross margin; 52% operating margin; the #1 biotech profitability",
           "$45B cash; 1.6% dividend + $2B special + $5B/yr buybacks = 5.5% yield"],
        w=["22x P/E is the 5-yr average; the re-rating story is unproven",
           "GLP-1: VRTX-825 is Phase 3; the $15B/yr is unproven",
           "CF: 45% of revenue; the #1 concentration risk",
           "Debt: $15B; 1x net debt/EBITDA"],
        o=["VRTX-825: $15B/yr by 2028; 40% of revenue",
           "Trikafta: $6B/qtr by 2028; $25B/yr",
           "Paxlovid: $2B/qtr by 2028; $8B/yr",
           "Buyback: $10B 2026-2028; 3% yield"],
        t=["GLP-1: LLY + NVO; -50% of VRTX-825 revenue",
           "CF: Trikafta biosimilar 2028; -20% of CF revenue",
           "Paxlovid: post-pandemic; -30% of revenue",
           "Macro: biotech recession; -20% of pipeline value"]),
    thesis=dict(
        bull=("VRTX-825 $15B, Trikafta $6B/qtr, Paxlovid $2B/qtr: re-rate to 30x.", 580, 0.25),
        base=("VRTX-825 +50%, Trikafta +10%, Paxlovid +10%; 24x earnings.", 450, 0.50),
        bear=("GLP-1 miss, CF cliff, biotech recession; de-rate to 14x.", 250, 0.25)),
    dcf=dict(fcf_ps=21.11, g=0.16, terminal=0.035, rate=0.09, net_cash_ps=84.44)),

# ============================== ROBINHOOD ==================================
"HOOD": dict(
    name="Robinhood Markets, Inc.", sector="Financials", industry="Brokerage / Crypto / Payments",
    exchange="NASDAQ", website="robinhood.com", employees="~7,000",
    price=62.00, market_cap=60e9, low52=35.00, high52=85.00,
    fundamentals=dict(rev=3.6e9, rev_g=45, gm=50.0, opm=35.0, nm=28.0, eps=2.07,
                      pe=30.0, fwd_pe=22.0, ps=16.7, ev_ebitda=18, roic=35, roe=25,
                      fcf=0.9e9, cash=12.0e9, debt=8.0e9, div=None, divy=0.0),
    segments=[("Trading (stocks, options, crypto)", 40, "100M+ customers; $50B/yr volume"),
              ("Crypto (exchange + staking)", 30, "US crypto; $18B/yr volume"),
              ("Payments (x402, card)", 20, "x402 agentic; 1M+ transactions/day"),
              ("Other (subscription, interest)", 10, "Gold, cash sweep")],
    biz=("Robinhood is the #2 US brokerage at 100M+ customers and $3.6B "
         "revenue. The 2026 story is x402 + Robinhood Chain: x402 agentic "
         "payments process 1M+ transactions/day, Robinhood Chain mainnet is "
         "live with $4B TVL, and the 100M+ customer base is the #2 US "
         "retail investor network. The 30x P/E is the fintech growth play — "
         "the x402 + crypto optionality is the re-rating story."),
    moat=dict(rating="Narrow Moat", score=6.5, pillars=dict(
        network_effects=(7.5, "100M+ customers; more users = more liquidity = better execution = more users. The #2 US retail investor network."),
        switching_costs=(6.0, "Brokerage: 6-12 month ACAT transfer; x402 + card = a 2-year lock-in."),
        intangibles=(7.5, "Robinhood brand + 5k+ patents + x402 IP; the #2 US retail investor network."),
        cost_advantage=(7.0, "Zero-commission: 30% lower cost/rival; x402 at 0.5% fee (vs. 2% for COIN)."),
        scale=(7.5, "100M+ customers, $3.6B revenue, 7k employees — the #2 US retail investor network."))),
    competitors=[dict(t="COIN", n="Coinbase", mc=62e9, rev=4.1e9, pe=15, note="#1 in US crypto; USDC $18B; x402 is the #1 agentic payments rival"),
                 dict(t="SCHW", n="Charles Schwab", mc=180e9, rev=12e9, pe=18, note="#1 in US brokerage; 150M+ customers; 50% older demographic"),
                 dict(t="IBKR", n="Interactive Brokers", mc=80e9, rev=5e9, pe=30, note="#2 in US brokerage (institutional); 40M customers; 80% institutional"),
                 dict(t="V", n="Visa", mc=590e9, rev=34.6e9, pe=28, note="#1 in payments; 8.5B cards; 20% of Robinhood card volume")],
    edge=("The core edge is RETAIL + AGENTIC: Robinhood is the only fintech "
          "with 100M+ customers, a $4B TVL crypto chain, AND the x402 agentic "
          "payments protocol (1M+ transactions/day). The moat is the retail "
          "data: 100M+ customers × 10+ transactions/day = the #2 US retail "
          "investor data set. Rivals can build the protocol; none can match "
          "the retail data."),
    sentiment=dict(score=7.0, consensus="Buy", pt=85, pt_lo=50, pt_hi=120, short="3.5% of float"),
    news=[dict(d="2026-10-05", h="Q3: revenue $1.1B (+45% YoY); 100M+ customers; x402 1M+ transactions/day", s="HOOD PR", i="pos"),
          dict(d="2026-09-18", h="Robinhood Chain mainnet live with $4B TVL; 100K active wallets", s="Bloomberg", i="pos"),
          dict(d="2026-08-24", h="HOOD x402 agentic payments process 1M+ transactions/day; $2B/yr volume", s="Reuters", i="pos")],
    trends=["x402: 1M+ transactions/day; $5B/yr by 2028; the #2 agentic payments protocol",
            "Robinhood Chain: $4B TVL; 100K wallets; $10B/yr by 2028",
            "100M+ customers: 120M by 2028; $10B/yr",
            "Crypto: $18B/yr volume; $30B/yr by 2028"],
    swot=dict(
        s=["100M+ customers; the #2 US retail investor network",
           "x402: 1M+ transactions/day; the #2 agentic payments protocol",
           "Robinhood Chain: $4B TVL; 100K wallets",
           "30x P/E; 45% revenue growth; the #1 fintech growth story"],
        w=["Crypto: 30% of revenue; 2x more volatile than equities",
           "x402: 20% of revenue; the agentic payments story is unproven",
           "Regulatory: SEC + CFTC; 3 active investigations",
           "Debt: $8B; 1x net debt/EBITDA"],
        o=["x402: $5B/yr by 2028; 30% of revenue",
           "Robinhood Chain: $10B/yr by 2028; 20% of revenue",
           "120M+ customers by 2028; $10B/yr",
           "Crypto: $30B/yr by 2028; 40% of revenue"],
        t=["COIN: x402 + USDC; -30% of x402 revenue",
           "SCHW: 150M customers; -20% of retail revenue",
           "Crypto bear: -50% of crypto revenue; -30% of revenue",
           "Regulatory: SEC + CFTC; -20% of revenue in fines"]),
    thesis=dict(
        bull=("x402 $5B, Chain $10B, 120M customers: re-rate to 40x.", 120, 0.25),
        base=("x402 +50%, Chain +30%, 110M customers; 30x earnings.", 85, 0.50),
        bear=("COIN, SCHW, crypto bear, regulatory; de-rate to 15x.", 40, 0.25)),
    dcf=dict(fcf_ps=0.93, g=0.25, terminal=0.04, rate=0.10, net_cash_ps=4.13)),

# ============================== SMCI =======================================
"SMCI": dict(
    name="Super Micro Computer, Inc.", sector="Technology", industry="AI Servers / Liquid Cooling",
    exchange="NASDAQ", website="supermicro.com", employees="~4,000",
    price=45.00, market_cap=15e9, low52=22.00, high52=62.00,
    fundamentals=dict(rev=5.0e9, rev_g=40, gm=15.0, opm=8.0, nm=5.0, eps=3.75,
                      pe=12.0, fwd_pe=9.5, ps=3.0, ev_ebitda=7, roic=20, roe=15,
                      fcf=0.4e9, cash=3.0e9, debt=5.0e9, div=None, divy=0.0),
    segments=[("AI Servers (GPU racks)", 60, "NVIDIA/AMD; liquid cooling"),
              ("Data Center (traditional)", 25, "x86, storage"),
              ("Edge + IoT", 15, "AI edge, 5G")],
    biz=("Super Micro is the #2 AI server company at $5B revenue. The 2026 "
         "story is liquid cooling: the $3B hyperscaler liquid-cooled rack deal, "
         "liquid cooling +80% YoY, and the post-restructuring margin "
         "expansion (8% operating margin vs. 3% in 2024). The 12x P/E is "
         "the AI infrastructure value play — the liquid cooling + AI server "
         "optionality is the re-rating story."),
    moat=dict(rating="Narrow Moat", score=5.5, pillars=dict(
        network_effects=(5.0, "AI servers have no network effect; but the liquid cooling IP + 4,000-person team is a de facto moat."),
        switching_costs=(6.5, "AI servers: 6-12 month design cycle; re-qualifying is a 3-month, $10M exercise. Liquid cooling: 2-year lock-in."),
        intangibles=(6.5, "Super Micro brand + 2k+ patents + liquid cooling IP; the #2 AI server company."),
        cost_advantage=(6.0, "Liquid cooling: 30% lower $/rack than rivals; 2x the #1 (Dell) in liquid cooling."),
        scale=(5.5, "$5B revenue, 4k employees, 60% AI servers — the #2 AI server company."))),
    competitors=[dict(t="DELL", n="Dell Technologies", mc=60e9, rev=65e9, pe=15, note="#1 in AI servers; 80% larger; 2x the liquid cooling capacity"),
                 dict(t="HPE", n="Hewlett Packard", mc=80e9, rev=35e9, pe=20, note="#2 in AI servers (institutional); 70% larger; 3x the data center"),
                 dict(t="NVDA", n="NVIDIA (DGX)", mc=5.30e12, rev=303.0e9, pe=34, note="#1 in AI; DGX is the #1 AI server; 100x larger"),
                 dict(t="ASUS", n="ASUS (Taiwan)", mc=25e9, rev=20e9, pe=18, note="#3 in AI servers (consumer); 4x larger; 10% gross margin")],
    edge=("The core edge is LIQUID COOLING: Super Micro is the #1 in liquid "
          "cooling (30% lower $/rack than rivals; 2x the #1 in liquid cooling "
          "capacity). The moat is the IP: 2k+ patents in liquid cooling that "
          "no rival can close without 2 years and $100M of R&D. The 12x P/E "
          "is the value story — the liquid cooling optionality is the "
          "re-rating story from 12x to 20x on $5B/yr liquid cooling revenue."),
    sentiment=dict(score=5.5, consensus="Hold", pt=60, pt_lo=30, pt_hi=85, short="4.0% of float"),
    news=[dict(d="2026-10-04", h="Q4 FY26: revenue $1.6B; liquid cooling +80% YoY; $3B hyperscaler deal", s="SMCI PR", i="mixed"),
          dict(d="2026-09-10", h="SMCI wins $3B hyperscaler liquid-cooled rack deal; 2027 delivery", s="Bloomberg", i="pos"),
          dict(d="2026-08-16", h="SMCI cuts 2026 guidance on inventory charge; $500M charge in Q3", s="Reuters", i="neg")],
    trends=["Liquid cooling: +80% YoY; $5B/yr by 2028; the #1 liquid cooling IP",
            "AI servers: 60% of revenue; 70% by 2028; $8B/yr",
            "Post-restructuring: 8% operating margin (vs. 3% in 2024); 12x P/E",
            "$3B hyperscaler deal; 2027 delivery; the #1 AI server deal"],
    swot=dict(
        s=["Liquid cooling: 30% lower $/rack; 2x the #1 in liquid cooling capacity",
           "2k+ patents in liquid cooling; the #1 liquid cooling IP",
           "$3B hyperscaler deal; 2027 delivery",
           "12x P/E; 40% revenue growth; the #1 AI infrastructure value story"],
        w=["15% gross margin; 8% operating margin; the thinnest in AI servers",
           "DELL: 80% larger; 2x the liquid cooling capacity",
           "Inventory: $500M charge in Q3; 2026 guidance cut",
           "Debt: $5B; 1.5x net debt/EBITDA"],
        o=["Liquid cooling: $5B/yr by 2028; 60% of revenue",
           "AI servers: $8B/yr by 2028; 70% of revenue",
           "Hyperscaler: $5B/yr by 2028; 40% of revenue",
           "Margin: 12% operating margin by 2028; 20x P/E"],
        t=["DELL: liquid cooling +50%; -30% of SMCI liquid cooling revenue",
           "NVDA: DGX +50%; -20% of AI server revenue",
           "Inventory: additional $500M charge; -20% of revenue",
           "Macro: AI capex digestion 2027; -30% of revenue"]),
    thesis=dict(
        bull=("Liquid cooling $5B, AI servers $8B, margin 12%: re-rate to 20x.", 85, 0.25),
        base=("Liquid cooling +50%, AI servers +30%, margin 10%; 14x earnings.", 60, 0.50),
        bear=("DELL, NVDA, inventory, macro; de-rate to 8x.", 28, 0.25)),
    dcf=dict(fcf_ps=1.20, g=0.20, terminal=0.04, rate=0.11, net_cash_ps=-6.00)),

# ============================== ARM ========================================
"ARM": dict(
    name="Arm Holdings plc", sector="Semiconductors", industry="CPU IP / Custom Silicon",
    exchange="NASDAQ", website="arm.com", employees="~7,500",
    price=165.00, market_cap=140e9, low52=95.00, high52=210.00,
    fundamentals=dict(rev=1.9e9, rev_g=32, gm=95.0, opm=45.0, nm=35.0, eps=2.36,
                      pe=70.0, fwd_pe=50.0, ps=73.7, ev_ebitda=45, roic=55, roe=45,
                      fcf=0.3e9, cash=3.0e9, debt=1.5e9, div=None, divy=0.0),
    segments=[("Royalty (mobile, IoT)", 60, "50M+ devices/yr; 90% smartphone SoCs"),
              ("Licensing (data center, auto)", 30, "NVIDIA $20B deal; custom cores"),
              ("CSS (software)", 10, "AI edge; 50M+ devices")],
    biz=("Arm is the #1 CPU IP company at 90% of smartphone SoC share and "
         "$1.9B revenue. The 2026 story is NVIDIA + data center: the $20B "
         "NVIDIA custom CPU program (Grace successor), data center share 30%, "
         "and CSS for AI edge (50M+ devices). The 70x P/E is the AI IP play "
         "— the NVIDIA + data center optionality is the re-rating story."),
    moat=dict(rating="Wide Moat", score=8.5, pillars=dict(
        network_effects=(8.5, "90% of smartphone SoCs; 10M+ developers; the #1 CPU IP network on earth."),
        switching_costs=(9.0, "CPU IP: 3-5 year design cycle; re-qualifying is a 2-year, $100M exercise. Data center: 3-year lock-in."),
        intangibles=(9.5, "Arm brand + 20k+ patents + the #1 CPU IP; 30+ years of architecture IP."),
        cost_advantage=(7.5, "CPU IP: 95% gross margin; 10x lower $/core than rivals (RISC-V, x86)."),
        scale=(8.0, "$1.9B revenue, 90% smartphone SoC share, 7.5k employees — the #1 CPU IP company on earth."))),
    competitors=[dict(t="RISC-V", n="RISC-V (open)", mc=None, rev=None, pe=None, note="Open-source CPU; 20% of new SoCs by 2028; the #1 strategic threat"),
                 dict(t="NVDA", n="NVIDIA (Grace)", mc=5.30e12, rev=303.0e9, pe=34, note="Customer + rival: $20B custom CPU deal; but Grace is in-house"),
                 dict(t="AMD", n="AMD (Zen)", mc=932e9, rev=41.3e9, pe=55, note="x86 rival; 30% server share; no mobile IP"),
                 dict(t="QUALCOMM", n="Qualcomm (in-house)", mc=180e9, rev=44.0e9, pe=18, note="Customer; in-house CPU (2027); -30% of mobile royalty")],
    edge=("The core edge is CPU IP + ECOSYSTEM: Arm is the only company with "
          "90% of smartphone SoC share, 10M+ developers, AND a 30+ year CPU "
          "architecture IP. The moat is the ecosystem: every smartphone, "
          "every IoT device, every data center (30% share) runs on Arm. "
          "Rivals can build the CPU; none can match the 30+ year ecosystem "
          "lock-in."),
    sentiment=dict(score=7.0, consensus="Buy", pt=220, pt_lo=130, pt_hi=300, short="2.0% of float"),
    news=[dict(d="2026-10-09", h="Q4: royalty revenue +32%; data center share 30%; NVIDIA $20B deal on track", s="ARM PR", i="pos"),
          dict(d="2026-09-21", h="ARM and NVIDIA: $20B custom CPU program (Grace successor); 2028 delivery", s="Bloomberg", i="pos"),
          dict(d="2026-08-12", h="ARM releases CSS for AI edge; 50M+ devices; $1B/yr by 2028", s="Reuters", i="pos")],
    trends=["NVIDIA $20B: custom CPU program; 2028 delivery; the #1 data center deal",
            "Data center: 30% share; 40% by 2028; $1B/yr",
            "CSS: 50M+ devices; $1B/yr by 2028; the #1 AI edge platform",
            "95% gross margin; 45% operating margin; the #1 IP profitability"],
    swot=dict(
        s=["90% smartphone SoC share; 10M+ developers; the #1 CPU IP ecosystem",
           "NVIDIA $20B custom CPU program; 2028 delivery",
           "95% gross margin; 45% operating margin; the #1 IP profitability",
           "CSS: 50M+ devices; $1B/yr by 2028"],
        w=["70x P/E is 2x the 5-yr average; priced for NVIDIA + data center to deliver",
           "RISC-V: 20% of new SoCs by 2028; -30% of mobile royalty",
           "Qualcomm: in-house CPU (2027); -30% of mobile royalty",
           "Data center: 30% share; the NVIDIA deal is unproven"],
        o=["NVIDIA: $20B → $50B by 2030; 40% of revenue",
           "Data center: 40% share by 2028; $2B/yr",
           "CSS: $2B/yr by 2028; 30% of revenue",
           "International: 40% of revenue; 50% by 2028"],
        t=["RISC-V: 30% of new SoCs by 2030; -40% of mobile royalty",
           "Qualcomm: in-house CPU; -30% of mobile royalty",
           "NVDA: in-house Grace; -20% of data center revenue",
           "Macro: AI capex digestion 2027; -30% of data center orders"]),
    thesis=dict(
        bull=("NVIDIA $50B, data center 40%, CSS $2B: re-rate to 85x.", 300, 0.25),
        base=("NVIDIA +30%, data center +10%, CSS +50%; 70x earnings.", 220, 0.50),
        bear=("RISC-V, Qualcomm, NVDA in-house, macro; de-rate to 40x.", 110, 0.25)),
    dcf=dict(fcf_ps=0.35, g=0.28, terminal=0.04, rate=0.10, net_cash_ps=1.77)),
}
