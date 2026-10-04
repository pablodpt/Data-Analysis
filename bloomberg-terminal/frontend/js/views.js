/* OpenBerg views.js — renderers for TOP GP DES FA N ECO W HELP + rails. */
"use strict";

let viewTimer = null;
function clearViewTimer() { if (viewTimer) { clearInterval(viewTimer); viewTimer = null; } }

const FN_TITLES = { TOP: "TOP — MARKET OVERVIEW", GP: "GP — PRICE GRAPH", DES: "DES — DESCRIPTION",
  FA: "FA — FINANCIAL ANALYSIS", SCR: "SCR — STOCK SCREENER", N: "N — NEWS", ECO: "ECO — ECONOMICS", W: "W — WATCHLIST", HELP: "HELP" };

function loading(el, msg = "loading…") { el.innerHTML = `<div class="muted" style="padding:20px">${esc(msg)}</div>`; }
function verror(el, msg, retry) {
  el.innerHTML = `<div style="padding:20px"><span class="down">■</span> ${esc(msg)} ` +
    `<button class="btn" id="vRetry">RETRY</button></div>`;
  document.getElementById("vRetry").onclick = retry;
}

/* ================= TOP ================= */
async function vTop(el) {
  clearViewTimer();
  // Sections load independently: if movers hang/fail, indices still render (and vice versa).
  el.innerHTML = `
    <h3 class="sub">INDICES & BENCHMARKS</h3>
    <div id="topIdx"><div class="muted" style="padding:12px">loading indices…</div></div>
    <div id="topBreadth"></div>
    <h3 class="sub">MOVERS — US EQUITIES <span class="muted" id="topMvMeta"></span></h3>
    <div class="toolbar"><div class="seg" id="mvSeg">
      ${["gainers", "losers", "actives"].map(g => `<button data-g="${g}" class="${state.moversGroup === g ? "on" : ""}">${g.toUpperCase()}</button>`).join("")}
    </div></div>
    <div id="topMovers"><div class="muted" style="padding:12px">loading movers…</div></div>
    <h3 class="sub">HEATMAP <span class="muted" id="topHmMeta"></span></h3>
    <div id="topHeat"><canvas class="chart" id="heatmap" style="height:120px"></canvas></div>
    <div class="muted" id="topMeta" style="margin-top:6px"></div>`;
  el.querySelectorAll("#mvSeg button").forEach(btn => btn.onclick = () => {
    state.moversGroup = btn.dataset.g;
    el.querySelectorAll("#mvSeg button").forEach(x => x.classList.toggle("on", x === btn));
    loadMovers();
  });
  loadIndices();
  loadMovers();
}

function topMeta() {
  const box = document.getElementById("topMeta");
  if (box) box.textContent = `indices: ${state.topIdxMeta || "…"} · movers: ${state.topMvMeta || "…"}`;
}

async function loadIndices() {
  const box = document.getElementById("topIdx");
  if (!box) return;
  try {
    const ov = await api("/api/market/overview", {}, { timeout: 45000 });
    if (!box.isConnected) return;  // user switched views mid-fetch
    state.topIdxMeta = `${ov.mode} (${ov.source || "?"})`;
    const idx = ov.indices || [];
    const b = ov.breadth;
    let bHtml = "";
    if (b) {
      const tot = (b.advancers || 0) + (b.decliners || 0) + (b.unchanged || 0) || 1;
      const pa = ((b.advancers || 0) / tot * 100), pd = ((b.decliners || 0) / tot * 100);
      bHtml = `<h3 class="sub">MARKET BREADTH — ${esc(b.universe || "")}</h3>
      <div style="display:flex;height:18px;border:1px solid var(--line);margin-bottom:4px">
        <div style="width:${pa}%;background:var(--up)"></div><div style="width:${pd}%;background:var(--down)"></div>
      </div>
      <div><span class="up">▲ ${b.advancers ?? 0} adv</span> · <span class="down">▼ ${b.decliners ?? 0} dec</span> · ${b.unchanged ?? 0} unch</div>`;
    }
    box.innerHTML = `
      <table class="t num"><thead><tr><th>Index</th><th>Last</th><th>Chg</th><th>%</th><th class="l">Trend (1M)</th></tr></thead>
      <tbody>${idx.map((r, i) => `<tr class="click" data-sym="${esc(r.symbol)}">
        <td class="l"><b style="color:var(--amber)">${esc(r.label)}</b> <span class="muted">${esc(r.symbol)}</span></td>
        <td>${fmtPx(r.price)}</td><td class="${cls(r.change)}">${fmtChg(r.change)}</td>
        <td class="${cls(r.pct)}">${fmtPct(r.pct)}</td>
        <td class="l"><canvas class="spark" id="sp${i}"></canvas></td></tr>`).join("")}</tbody></table>`;
    const bb = document.getElementById("topBreadth");
    if (bb) bb.innerHTML = bHtml;
    idx.forEach((r, i) => { const c = document.getElementById("sp" + i); if (c) drawSpark(c, r.spark); });
    box.querySelectorAll("tr.click").forEach(tr => tr.onclick = () => goSymbol(tr.dataset.sym, "GP"));
  } catch (e) {
    state.topIdxMeta = "error";
    if (box.isConnected) box.innerHTML = `<div style="padding:12px"><span class="down">■</span> indices failed: ${esc(e.message)} <button class="btn" id="idxRetry">RETRY</button></div>`;
    const rb = document.getElementById("idxRetry");
    if (rb) rb.onclick = loadIndices;
  }
  topMeta();
}

async function loadMovers() {
  const box = document.getElementById("topMovers");
  if (!box) return;
  box.innerHTML = `<div class="muted" style="padding:12px">loading movers…</div>`;
  try {
    const mv = await api("/api/market/movers", { group: state.moversGroup, limit: 10 }, { timeout: 45000 });
    if (!box.isConnected) return;  // user switched views mid-fetch
    state.topMvMeta = `${mv.mode} (${mv.source || "?"})`;
    const rows = mv.rows || [];
    const mm = document.getElementById("topMvMeta");
    if (mm) mm.textContent = `(${(mv.group || state.moversGroup).toUpperCase()} · ${mv.mode})`;
    const hm = document.getElementById("topHmMeta");
    if (hm) hm.textContent = `(${(mv.group || state.moversGroup).toUpperCase()})`;
    box.innerHTML = `
      <table class="t num"><thead><tr><th>Symbol</th><th class="l">Name</th><th>Last</th><th>Chg</th><th>%</th><th>Vol</th></tr></thead>
      <tbody>${rows.map(r => `<tr class="click" data-sym="${esc(r.symbol)}">
        <td><b style="color:var(--amber)">${esc(r.symbol)}</b></td><td class="l muted">${esc(r.name || "")}</td>
        <td>${fmtPx(r.price)}</td><td class="${cls(r.change)}">${fmtChg(r.change)}</td>
        <td class="${cls(r.pct)}">${fmtPct(r.pct)}</td><td>${fmtBig(r.volume)}</td></tr>`).join("")}</tbody></table>
      <div class="muted" style="margin-top:6px">as of ${esc(mv.asOf || "").replace("T", " ").slice(0, 19)}</div>`;
    box.querySelectorAll("tr.click").forEach(tr => tr.onclick = () => goSymbol(tr.dataset.sym, "GP"));
    const heat = document.getElementById("heatmap");
    if (heat && rows.length) drawHeatmap(heat, rows);
  } catch (e) {
    state.topMvMeta = "error";
    if (box.isConnected) box.innerHTML = `<div style="padding:12px"><span class="down">■</span> movers failed: ${esc(e.message)} <button class="btn" id="mvRetry">RETRY</button></div>`;
    const rb = document.getElementById("mvRetry");
    if (rb) rb.onclick = loadMovers;
  }
  topMeta();
}

/* ================= GP ================= */
const RANGES = ["1D", "5D", "1M", "3M", "6M", "YTD", "1Y", "2Y", "5Y", "MAX"];
async function vGP(el) {
  loading(el);
  const sym = state.symbol;
  try {
    const [h, q] = await Promise.all([
      api("/api/history", { symbol: sym, range: state.range, interval: "1d" }),
      api("/api/quote", { symbol: sym }).catch(() => null),
    ]);
    const bars = h.bars || [];
    const first = bars[0]?.c, last = bars[bars.length - 1]?.c;
    const pret = first && last ? (last / first - 1) * 100 : null;
    const hi = Math.max(...bars.map(b => b.h)), lo = Math.min(...bars.map(b => b.l));
    // annualized vol from daily returns
    let vol = null;
    if (bars.length > 5) {
      const rets = [];
      for (let i = 1; i < bars.length; i++) rets.push(Math.log(bars[i].c / bars[i - 1].c));
      const m = rets.reduce((a, b) => a + b, 0) / rets.length;
      vol = Math.sqrt(rets.reduce((a, r) => a + (r - m) ** 2, 0) / rets.length) * Math.sqrt(252) * 100;
    }
    el.innerHTML = `
      <div class="toolbar">
        <div class="seg" id="rgSeg">${RANGES.map(r => `<button data-r="${r}" class="${state.range === r ? "on" : ""}">${r}</button>`).join("")}</div>
        <div class="seg" id="tySeg">
          <button data-t="candle" class="${state.chartType === "candle" ? "on" : ""}">CANDLE</button>
          <button data-t="line" class="${state.chartType === "line" ? "on" : ""}">LINE</button>
        </div>
        <label class="chk"><input type="checkbox" id="cVol" ${state.showVol ? "checked" : ""}> VOL</label>
        <label class="chk"><input type="checkbox" id="cS20" ${state.showSMA20 ? "checked" : ""}> SMA20</label>
        <label class="chk"><input type="checkbox" id="cS50" ${state.showSMA50 ? "checked" : ""}> SMA50</label>
        <label class="chk"><input type="checkbox" id="cLog" ${state.logScale ? "checked" : ""}> LOG</label>
        <button class="btn" id="csvBtn">CSV ⭳</button>
      </div>
      <div class="cards">
        ${card("LAST", fmtPx(last), cls(h.last?.change))}${card("CHG", `${fmtChg(h.last?.change)} (${fmtPct(h.last?.pct)})`, cls(h.last?.change))}
        ${card("PERIOD RET", fmtPct(pret), cls(pret))}${card("RANGE HI / LO", `${fmtPx(hi)} / ${fmtPx(lo)}`)}
        ${card("VOL (ANN)", vol === null ? "—" : vol.toFixed(1) + "%")}${card("BARS", nf0.format(bars.length))}
      </div>
      <canvas class="chart" id="mainChart"></canvas>
      <div class="cards">
        ${card("OPEN", fmtPx(q?.open))}${card("HIGH", fmtPx(q?.high))}${card("LOW", fmtPx(q?.low))}
        ${card("PREV CLOSE", fmtPx(q?.prevClose ?? h.prevClose))}${card("VOLUME", fmtBig(q?.volume))}
        ${card("MKT CAP", fmtBig(q?.mktCap))}${card("P/E", q?.pe ?? "—")}${card("52W", `${fmtPx(q?.week52Low)} – ${fmtPx(q?.week52High)}`)}
      </div>
      <h3 class="sub">RECENT BARS</h3>
      <table class="t num"><thead><tr><th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Chg%</th><th>Volume</th></tr></thead>
      <tbody>${bars.slice(-10).reverse().map((b, i, a) => {
        const prev = a[i + 1]?.c ?? b.o;
        const p = (b.c / prev - 1) * 100;
        return `<tr><td>${esc(String(b.t).slice(0, bars[0].t.length > 10 ? 16 : 10))}</td><td>${fmtPx(b.o)}</td><td>${fmtPx(b.h)}</td><td>${fmtPx(b.l)}</td><td>${fmtPx(b.c)}</td><td class="${cls(p)}">${fmtPct(p)}</td><td>${fmtBig(b.v)}</td></tr>`;
      }).join("")}</tbody></table>
      <div class="muted" style="margin-top:6px">mode: ${esc(h.mode)} (${esc(h.source || "")}) · interval ${esc(h.interval || "")}</div>`;
    drawOHLC(document.getElementById("mainChart"), bars,
      { type: state.chartType, volume: state.showVol, sma20: state.showSMA20, sma50: state.showSMA50, log: state.logScale });
    el.querySelector("#rgSeg").onclick = (e) => { const b = e.target.closest("button"); if (b) { state.range = b.dataset.r; vGP(el); } };
    el.querySelector("#tySeg").onclick = (e) => { const b = e.target.closest("button"); if (b) { state.chartType = b.dataset.t; vGP(el); } };
    const re = () => vGP(el);
    el.querySelector("#cVol").onchange = (e) => { state.showVol = e.target.checked; re(); };
    el.querySelector("#cS20").onchange = (e) => { state.showSMA20 = e.target.checked; re(); };
    el.querySelector("#cS50").onchange = (e) => { state.showSMA50 = e.target.checked; re(); };
    el.querySelector("#cLog").onchange = (e) => { state.logScale = e.target.checked; re(); };
    el.querySelector("#csvBtn").onclick = () => {
      downloadCSV(`${sym}_${state.range}.csv`, [["date", "open", "high", "low", "close", "volume"],
        ...bars.map(b => [b.t, b.o, b.h, b.l, b.c, b.v])]);
      toast(`Exported ${bars.length} bars for ${esc(sym)}`, "ok");
    };
  } catch (e) { verror(el, `chart for ${sym} failed: ` + e.message, () => vGP(el)); }
}
function card(k, v, c = "") { return `<div class="card"><div class="k">${esc(k)}</div><div class="v ${c}">${v}</div></div>`; }

/* ================= DES ================= */
async function vDes(el) {
  loading(el);
  const sym = state.symbol;
  try {
    const [p, f] = await Promise.all([
      api("/api/profile", { symbol: sym }),
      api("/api/filings", { symbol: sym, limit: 10 }).catch(() => null),
    ]);
    el.innerHTML = `
      <h3 class="sub">${esc(p.name)} (${esc(p.symbol)})</h3>
      <div class="cards">
        ${card("LAST", `${fmtPx(p.price)} <span class="${cls(p.change)}" style="font-size:12px">${fmtChg(p.change)} (${fmtPct(p.pct)})</span>`)}
        ${card("MKT CAP", fmtBig(p.mktCap))}${card("P/E", p.pe ?? "—")}${card("EPS", p.eps ?? "—")}
        ${card("DIV YLD", p.divYield === null || p.divYield === undefined ? "—" : (+p.divYield).toFixed(2) + "%")}
        ${card("52W", `${fmtPx(p.week52Low)} – ${fmtPx(p.week52High)}`)}
      </div>
      <table class="t"><tbody>
        ${desRow("Sector", p.sector)}${desRow("Industry", p.industry)}${desRow("Exchange", p.exchange)}
        ${desRow("Currency", p.currency)}${desRow("Employees", p.employees ? nf0.format(p.employees) : "—")}
        ${desRow("Website", p.website && p.website !== "—" ? `<a href="${esc(p.website)}" target="_blank" rel="noopener">${esc(p.website)}</a>` : "—")}
      </tbody></table>
      <h3 class="sub">BUSINESS SUMMARY</h3>
      <p style="color:var(--dim);max-width:900px">${esc(p.description || "—")}</p>
      <h3 class="sub">FILINGS — SEC EDGAR ${f ? `<span class="muted">(${esc(f.mode)})</span>` : ""}</h3>
      ${f && f.filings?.length ? `<table class="t"><thead><tr><th>Form</th><th>Date</th><th class="l">Link</th></tr></thead><tbody>
        ${f.filings.map(x => `<tr><td><b style="color:var(--amber)">${esc(x.form)}</b></td><td>${esc(x.date)}</td>
          <td class="l"><a href="${esc(x.link)}" target="_blank" rel="noopener">open ↗</a></td></tr>`).join("")}</tbody></table>`
        : `<div class="muted">No filings available for ${esc(sym)} (ETFs/indices have none).</div>`}
      <div class="muted" style="margin-top:6px">mode: ${esc(p.mode)} (${esc(p.source || "")})</div>`;
  } catch (e) { verror(el, `description for ${sym} failed: ` + e.message, () => vDes(el)); }
}
function desRow(k, v) { return `<tr><td class="l" style="color:var(--faint);width:140px">${esc(k)}</td><td class="l">${v}</td></tr>`; }

/* ================= FA ================= */
async function vFA(el) {
  loading(el);
  const sym = state.symbol;
  try {
    const [f, e] = await Promise.all([
      api("/api/financials", { symbol: sym, statement: state.stmt, period: state.period }),
      api("/api/earnings", { symbol: sym }).catch(() => null),
    ]);
    el.innerHTML = `
      <div class="toolbar">
        <div class="seg" id="stSeg">${["income", "balance", "cashflow"].map(s => `<button data-s="${s}" class="${state.stmt === s ? "on" : ""}">${s.toUpperCase()}</button>`).join("")}</div>
        <div class="seg" id="pdSeg">${["annual", "quarterly"].map(s => `<button data-s="${s}" class="${state.period === s ? "on" : ""}">${s.toUpperCase()}</button>`).join("")}</div>
        <span class="muted">USD ${esc(f.scale || "millions")}</span>
        <button class="btn" id="faCsv">CSV ⭳</button>
      </div>
      ${f.ratios ? `<div class="cards">${Object.entries(f.ratios).map(([k, v]) => card(k.toUpperCase(), v)).join("")}</div>` : ""}
      <div style="overflow-x:auto"><table class="t num"><thead><tr><th>Breakdown</th>${f.dates.map(d => `<th>${esc(d)}</th>`).join("")}</tr></thead>
      <tbody>${f.rows.map(r => `<tr><td class="l">${esc(r.label)}</td>${r.values.map(v => `<td>${v === null ? "—" : nf0.format(v)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>
      ${e ? `<h3 class="sub">EARNINGS</h3>
      <div class="news2"><div><h3 class="sub">REPORTED</h3>
        <table class="t num"><thead><tr><th>Date</th><th>Est</th><th>Actual</th><th>Surpr</th></tr></thead><tbody>
        ${(e.past || []).map(x => `<tr><td>${esc(x.date)}</td><td>${x.estimate ?? "—"}</td><td>${x.actual ?? "—"}</td><td class="${cls(x.surprisePct)}">${x.surprisePct === undefined || x.surprisePct === null ? "—" : fmtPct(x.surprisePct)}</td></tr>`).join("") || `<tr><td colspan="4" class="muted">—</td></tr>`}</tbody></table></div>
      <div><h3 class="sub">UPCOMING</h3>
        <table class="t num"><thead><tr><th>Date</th><th>Est</th></tr></thead><tbody>
        ${(e.upcoming || []).map(x => `<tr><td>${esc(x.date)}</td><td>${x.estimate ?? "—"}</td></tr>`).join("") || `<tr><td colspan="2" class="muted">—</td></tr>`}</tbody></table></div></div>` : ""}
      <div class="muted" style="margin-top:6px">mode: ${esc(f.mode)} (${esc(f.source || "")})</div>`;
    el.querySelector("#stSeg").onclick = (ev) => { const b = ev.target.closest("button"); if (b) { state.stmt = b.dataset.s; vFA(el); } };
    el.querySelector("#pdSeg").onclick = (ev) => { const b = ev.target.closest("button"); if (b) { state.period = b.dataset.s; vFA(el); } };
    el.querySelector("#faCsv").onclick = () => {
      downloadCSV(`${sym}_${state.stmt}_${state.period}.csv`,
        [["breakdown", ...f.dates], ...f.rows.map(r => [r.label, ...r.values])]);
      toast("Financials exported", "ok");
    };
  } catch (e) { verror(el, `financials for ${sym} failed: ` + e.message, () => vFA(el)); }
}

/* ================= SCR (screener) ================= */
const SCR_DEFAULTS = { minPrice: "", maxPrice: "", minMktCapB: "", maxMktCapB: "", minPE: "", maxPE: "",
  minDivY: "", maxDivY: "", minChgPct: "", maxChgPct: "", minVolumeM: "", minWeek52: "", maxWeek52: "",
  sectors: [], sort: "mktCap", dir: "desc", limit: 50 };
const SCR_PRESETS = {
  "MEGA CAPS": { minMktCapB: 200, sort: "mktCap", dir: "desc" },
  "VALUE": { maxPE: 15, minDivY: 1, sort: "pe", dir: "asc" },
  "HIGH YIELD": { minDivY: 3, sort: "divYield", dir: "desc" },
  "MOMENTUM": { minChgPct: 2, minVolumeM: 10, sort: "pct", dir: "desc" },
  "OVERSOLD": { maxWeek52: 15, sort: "week52pos", dir: "asc" },
  "BIG TECH": { sectors: ["Technology"], minMktCapB: 100, sort: "mktCap", dir: "desc" },
};
function ffield(label, a, b) {
  return `<div class="ffield"><label>${label}</label><div class="frow">${a}${b || ""}</div></div>`;
}
async function vScreener(el) {
  clearViewTimer();
  loading(el, "loading universe…");
  try {
    if (!state.scrU) state.scrU = await api("/api/screener/universe");
  } catch (e) { verror(el, "screener universe failed: " + e.message, () => vScreener(el)); return; }
  const F = { ...SCR_DEFAULTS, ...(store.get("scr", {})) };
  const num = (k, ph) => `<input class="txt" data-f="${k}" placeholder="${ph}" value="${esc(F[k] ?? "")}" style="width:100%">`;
  el.innerHTML = `
    <div class="toolbar"><span class="muted">PRESETS:</span>
      ${Object.keys(SCR_PRESETS).map(p => `<button class="btn" data-preset="${p}">${p}</button>`).join("")}
      <button class="btn" data-preset="__clear">CLEAR</button>
      <span class="muted">universe: ${state.scrU.count} US stocks + ETFs</span>
    </div>
    <div class="fgrid">
      ${ffield("PRICE $", num("minPrice", "min"), num("maxPrice", "max"))}
      ${ffield("MKT CAP $B", num("minMktCapB", "min"), num("maxMktCapB", "max"))}
      ${ffield("P/E", num("minPE", "min"), num("maxPE", "max"))}
      ${ffield("DIV YLD %", num("minDivY", "min"), num("maxDivY", "max"))}
      ${ffield("DAY CHG %", num("minChgPct", "min"), num("maxChgPct", "max"))}
      ${ffield("VOLUME ≥ M", num("minVolumeM", "min"))}
      ${ffield("52W POS %", num("minWeek52", "0–100"), num("maxWeek52", "0–100"))}
      <div class="ffield"><label>SORT</label>
        <select class="sel" data-f="sort" style="width:100%">${["mktCap", "price", "pct", "volume", "pe", "divYield", "week52pos", "beta", "symbol"].map(s => `<option ${F.sort === s ? "selected" : ""}>${s}</option>`).join("")}</select>
        <div class="seg" id="scrDir" style="margin-top:4px">
          <button data-d="desc" class="${F.dir !== "asc" ? "on" : ""}">▼ DESC</button>
          <button data-d="asc" class="${F.dir === "asc" ? "on" : ""}">▲ ASC</button>
        </div></div>
    </div>
    <div class="toolbar"><span class="muted">SECTORS:</span>
      <div class="pills" id="scrSectors">${state.scrU.sectors.map(s => `<label class="pill ${(F.sectors || []).includes(s) ? "on" : ""}"><input type="checkbox" value="${esc(s)}" ${(F.sectors || []).includes(s) ? "checked" : ""} hidden>${esc(s)}</label>`).join("")}</div>
    </div>
    <div class="toolbar">
      <select class="sel" data-f="limit">${[25, 50, 100, 200].map(n => `<option ${+F.limit === n ? "selected" : ""}>${n}</option>`).join("")}</select>
      <button class="btn primary" id="scrRun">RUN SCREEN</button>
      <button class="btn" id="scrCsv">CSV ⭳</button>
      <span class="muted" id="scrMeta"></span>
    </div>
    <div id="scrOut"><div class="muted">…</div></div>`;

  const collect = () => {
    const g = (k) => {
      const raw = (el.querySelector(`[data-f="${k}"]`)?.value ?? "").trim();
      if (k === "sort") return raw || "mktCap";
      if (k === "limit") return parseInt(raw, 10) || 50;
      if (raw === "") return null;
      const v = parseFloat(raw);
      return isNaN(v) ? null : v;
    };
    const w52 = (k) => { const v = g(k); return v === null ? null : v / 100; };
    return {
      minPrice: g("minPrice"), maxPrice: g("maxPrice"),
      minMktCapB: g("minMktCapB"), maxMktCapB: g("maxMktCapB"),
      minPE: g("minPE"), maxPE: g("maxPE"),
      minDivY: g("minDivY"), maxDivY: g("maxDivY"),
      minChgPct: g("minChgPct"), maxChgPct: g("maxChgPct"),
      minVolumeM: g("minVolumeM"),
      minWeek52Pos: w52("minWeek52"), maxWeek52Pos: w52("maxWeek52"),
      sectors: [...el.querySelectorAll("#scrSectors input:checked")].map(c => c.value),
      sort: g("sort"), dir: el.querySelector("#scrDir button.on")?.dataset.d || "desc",
      limit: g("limit"),
    };
  };
  const renderRows = (d) => {
    document.getElementById("scrMeta").textContent =
      `${d.count} matches · showing ${d.returned} · mode ${d.mode} (${d.source})`;
    const out = document.getElementById("scrOut");
    if (!d.rows.length) { out.innerHTML = `<div class="muted" style="padding:12px">No matches — loosen the filters.</div>`; return; }
    out.innerHTML = `<table class="t num"><thead><tr><th>Symbol</th><th class="l">Name</th><th class="l">Sector</th><th>Price</th><th>Day %</th><th>Mkt Cap</th><th>P/E</th><th>Div %</th><th>Vol</th><th class="l">52W Pos</th></tr></thead>
    <tbody>${d.rows.map(r => `<tr class="click" data-sym="${esc(r.symbol)}">
      <td><b style="color:var(--amber)">${esc(r.symbol)}</b></td><td class="l muted">${esc(r.name || "")}</td><td class="l muted">${esc(r.sector || "")}</td>
      <td>${fmtPx(r.price)}</td><td class="${cls(r.pct)}">${fmtPct(r.pct)}</td><td>${fmtBig(r.mktCap)}</td>
      <td>${r.pe === null || r.pe === undefined ? "—" : (+r.pe).toFixed(1)}</td>
      <td>${r.divYield === null || r.divYield === undefined ? "—" : (+r.divYield).toFixed(2)}</td>
      <td>${fmtBig(r.volume)}</td>
      <td class="l">${r.week52pos === null || r.week52pos === undefined ? "—" : `<div class="posbar"><i style="left:${(r.week52pos * 100).toFixed(1)}%"></i></div>`}</td></tr>`).join("")}</tbody></table>`;
    out.querySelectorAll("tr.click").forEach(tr => tr.onclick = () => goSymbol(tr.dataset.sym, "GP"));
  };
  const run = async () => {
    const body = collect();
    store.set("scr", { ...body, minWeek52: body.minWeek52Pos === null ? "" : body.minWeek52Pos * 100, maxWeek52: body.maxWeek52Pos === null ? "" : body.maxWeek52Pos * 100 });
    document.getElementById("scrOut").innerHTML = `<div class="muted" style="padding:12px">screening ${state.scrU.count} symbols… (first live run can take ~15s on free tiers)</div>`;
    try {
      state.scrLast = await apiPost("/api/screener/run", body);
      renderRows(state.scrLast);
    } catch (e) {
      document.getElementById("scrOut").innerHTML = `<div style="padding:12px"><span class="down">■</span> screen failed: ${esc(e.message)}</div>`;
    }
  };

  el.querySelector("#scrSectors").onclick = (e) => {
    const lab = e.target.closest("label.pill");
    if (!lab) return;
    const cb = lab.querySelector("input");
    cb.checked = !cb.checked;
    lab.classList.toggle("on", cb.checked);
  };
  el.querySelector("#scrDir").onclick = (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    el.querySelectorAll("#scrDir button").forEach(x => x.classList.toggle("on", x === b));
  };
  el.querySelectorAll("[data-preset]").forEach(b => b.onclick = () => {
    const p = b.dataset.preset;
    const v = p === "__clear" ? { ...SCR_DEFAULTS } : { ...SCR_DEFAULTS, ...SCR_PRESETS[p] };
    for (const k of ["minPrice", "maxPrice", "minMktCapB", "maxMktCapB", "minPE", "maxPE", "minDivY", "maxDivY", "minChgPct", "maxChgPct", "minVolumeM", "minWeek52", "maxWeek52"])
      el.querySelector(`[data-f="${k}"]`).value = v[k] ?? "";
    el.querySelector(`[data-f="sort"]`).value = v.sort;
    el.querySelector(`[data-f="limit"]`).value = String(v.limit ?? 50);
    el.querySelectorAll("#scrDir button").forEach(x => x.classList.toggle("on", x.dataset.d === (v.dir || "desc")));
    el.querySelectorAll("#scrSectors input").forEach(cb => {
      cb.checked = (v.sectors || []).includes(cb.value);
      cb.closest("label").classList.toggle("on", cb.checked);
    });
    run();
  });
  el.querySelector("#scrRun").onclick = run;
  el.querySelector("#scrCsv").onclick = () => {
    const d = state.scrLast;
    if (!d || !d.rows?.length) { toast("Run a screen first", "err"); return; }
    downloadCSV("screener.csv", [["symbol", "name", "sector", "price", "day_pct", "mkt_cap", "pe", "div_yield", "volume", "w52pos"],
      ...d.rows.map(r => [r.symbol, r.name, r.sector, r.price, r.pct, r.mktCap, r.pe, r.divYield, r.volume, r.week52pos])]);
    toast(`Exported ${d.rows.length} rows`, "ok");
  };
  el.addEventListener("keydown", (e) => { if (e.key === "Enter" && e.target.matches("input.txt")) run(); });
  run();
}

/* ================= N (news) ================= */
function artHtml(a) {
  return `<div class="art"><div class="hd"><span class="pub">${esc(a.publisher || "—")}</span><time>${esc(ago(a.published))}</time></div>
    <a class="ti" href="${esc(a.link || "#")}" target="_blank" rel="noopener">${esc(a.title)}</a>
    ${a.summary ? `<div class="sm">${esc(a.summary)}</div>` : ""}</div>`;
}
async function vNews(el) {
  loading(el);
  const sym = state.symbol;
  try {
    const [sn, mn] = await Promise.all([
      api("/api/news", { symbol: sym, limit: 20 }),
      api("/api/news/market", { limit: 20 }),
    ]);
    el.innerHTML = `<div class="news2">
      <div><h3 class="sub">NEWS — ${esc(sym)} <span class="muted">(${esc(sn.mode)}/${esc(sn.source || "")})</span></h3>
        ${sn.articles.map(artHtml).join("") || `<div class="muted">No articles.</div>`}</div>
      <div><h3 class="sub">MARKET NEWS <span class="muted">(${esc(mn.mode)}/${esc(mn.source || "")})</span></h3>
        ${mn.articles.map(artHtml).join("") || `<div class="muted">No articles.</div>`}</div></div>`;
  } catch (e) { verror(el, "news failed: " + e.message, () => vNews(el)); }
}

/* ================= ECO ================= */
async function vEco(el) {
  loading(el);
  try {
    const [ind, cal] = await Promise.all([
      api("/api/econ/indicators"),
      api("/api/econ/calendar", { days: 14 }),
    ]);
    const byDate = {};
    for (const e of cal.events) { (byDate[e.date] = byDate[e.date] || []).push(e); }
    const dates = Object.keys(byDate).sort();
    const today = new Date().toISOString().slice(0, 10);
    el.innerHTML = `
      <div class="toolbar"><span class="muted">Click an indicator to chart it · mode ${esc(ind.mode)} (${esc(ind.source || "")})</span></div>
      <table class="t num"><thead><tr><th>Indicator</th><th>Last</th><th>Chg</th><th>%</th><th>As of</th><th class="l">Trend</th></tr></thead>
      <tbody>${ind.indicators.map((r, i) => `<tr class="click ${state.ecoSeries === r.id ? "sel" : ""}" data-id="${esc(r.id)}" style="${state.ecoSeries === r.id ? "background:#141006" : ""}">
        <td class="l"><b style="color:var(--amber)">${esc(r.label)}</b> <span class="muted">${esc(r.id)} · ${esc(r.unit || "")}</span></td>
        <td>${fmtPx(r.value)}</td><td class="${cls(r.change)}">${fmtChg(r.change)}</td><td class="${cls(r.pct)}">${fmtPct(r.pct)}</td>
        <td class="muted">${esc(r.asOf || "")}</td><td class="l"><canvas class="spark" id="esp${i}"></canvas></td></tr>`).join("")}</tbody></table>
      <h3 class="sub" id="ecoChartTitle">${esc(state.ecoSeries)}</h3>
      <canvas class="chart" id="ecoChart"></canvas>
      <h3 class="sub">ECONOMIC CALENDAR — NEXT 14 DAYS <span class="muted">(${esc(cal.mode)}/${esc(cal.source || "")})</span></h3>
      ${dates.map(d => `<h3 class="sub" style="color:${d < today ? "var(--faint)" : d === today ? "var(--up)" : "var(--cyan)"}">${esc(d)}${d === today ? " — TODAY" : ""}</h3>
      <table class="t num"><thead><tr><th>Time</th><th class="l">Event</th><th>Imp</th><th>Forecast</th><th>Prev</th><th>Actual</th></tr></thead><tbody>
      ${byDate[d].map(e => `<tr><td>${esc(e.time || "")}</td><td class="l">${esc(e.name)} <span class="muted">${esc(e.country || "")}</span></td>
        <td class="${e.importance >= 3 ? "dot3" : e.importance === 2 ? "dot2" : "dot1"}">${"●".repeat(e.importance || 1)}</td>
        <td>${e.forecast ?? "—"}</td><td>${e.previous ?? "—"}</td><td><b>${e.actual ?? "—"}</b></td></tr>`).join("")}</tbody></table>`).join("")}`;
    ind.indicators.forEach((r, i) => { const c = document.getElementById("esp" + i); if (c) drawSpark(c, r.spark); });
    el.querySelectorAll("tr.click").forEach(tr => tr.onclick = () => { state.ecoSeries = tr.dataset.id; vEco(el); });
    loadEcoSeries();
  } catch (e) { verror(el, "economics failed: " + e.message, () => vEco(el)); }
}
async function loadEcoSeries() {
  try {
    const s = await api("/api/econ/series", { id: state.ecoSeries, years: 10 });
    const t = document.getElementById("ecoChartTitle");
    if (t) t.textContent = `${s.label} (${s.id}) — ${s.unit || ""} · ${s.freq} · ${s.mode}`;
    const cv = document.getElementById("ecoChart");
    if (cv) drawSeries(cv, s.points, { height: 220 });
  } catch { /* chart stays empty, table still useful */ }
}

/* ================= W (watchlist) ================= */
function wl() {
  if (!state.watchlist) state.watchlist = [...(state.status?.default_watchlist || ["AAPL", "MSFT", "NVDA", "SPY"])];
  return state.watchlist;
}
async function vWatch(el) {
  loading(el);
  clearViewTimer();
  try {
    const d = await apiPost("/api/quotes", { symbols: wl() });
    checkAlerts(d.quotes);
    el.innerHTML = `
      <div class="toolbar">
        <input class="txt" id="wlAdd" placeholder="ADD SYMBOL…" style="width:140px;text-transform:uppercase">
        <button class="btn primary" id="wlAddBtn">ADD</button>
        <button class="btn" id="wlRef">REFRESH</button>
        <span class="muted">auto-refresh 60s · click a row to open GP</span>
      </div>
      <table class="t num"><thead><tr><th>Symbol</th><th class="l">Name</th><th>Last</th><th>Chg</th><th>%</th><th>Vol</th><th class="l">Trend</th><th class="l">Alert</th><th></th></tr></thead>
      <tbody>${d.quotes.map((q, i) => {
        const a = state.alerts.find(x => x.symbol === q.symbol);
        return `<tr data-sym="${esc(q.symbol)}">
        <td class="click" style="cursor:pointer"><b style="color:var(--amber)">${esc(q.symbol)}</b></td>
        <td class="l muted">${esc(q.name || "")}</td><td>${fmtPx(q.price)}</td>
        <td class="${cls(q.change)}">${fmtChg(q.change)}</td><td class="${cls(q.pct)}">${fmtPct(q.pct)}</td><td>${fmtBig(q.volume)}</td>
        <td class="l"><canvas class="spark" id="wsp${i}"></canvas></td>
        <td class="l">${a ? `<span class="badge ${a.dir === "above" ? "live" : "demo"}">${a.dir === "above" ? "▲" : "▼"} ${fmtPx(a.px)}</span> <a href="#" data-unalert="${esc(q.symbol)}">x</a>`
          : `<input class="txt" data-alpx="${esc(q.symbol)}" placeholder="px" style="width:70px"> <select class="sel" data-aldir="${esc(q.symbol)}"><option value="above">▲</option><option value="below">▼</option></select> <a href="#" data-alert="${esc(q.symbol)}">set</a>`}</td>
        <td><a href="#" data-del="${esc(q.symbol)}">del</a></td></tr>`; }).join("")}</tbody></table>
      <div class="muted" style="margin-top:6px">mode: ${esc(d.mode)} · alerts are stored in this browser only</div>`;
    // lazy sparks
    d.quotes.forEach((q, i) => {
      api("/api/history", { symbol: q.symbol, range: "1M" })
        .then(h => { const c = document.getElementById("wsp" + i); if (c && h.bars) drawSpark(c, h.bars.map(b => b.c)); })
        .catch(() => {});
    });
    el.querySelectorAll("td.click").forEach(td => td.onclick = () => goSymbol(td.closest("tr").dataset.sym, "GP"));
    el.querySelector("#wlAddBtn").onclick = () => addToWl(el);
    el.querySelector("#wlAdd").onkeydown = (e) => { if (e.key === "Enter") addToWl(el); };
    el.querySelector("#wlRef").onclick = () => vWatch(el);
    el.querySelectorAll("[data-del]").forEach(a => a.onclick = (e) => {
      e.preventDefault();
      state.watchlist = wl().filter(s => s !== a.dataset.del);
      store.set("watchlist", state.watchlist);
      refreshWlMini(); vWatch(el);
    });
    el.querySelectorAll("[data-alert]").forEach(a => a.onclick = (e) => {
      e.preventDefault();
      const px = parseFloat(el.querySelector(`[data-alpx="${a.dataset.alert}"]`).value);
      const dir = el.querySelector(`[data-aldir="${a.dataset.alert}"]`).value;
      if (!px || px <= 0) { toast("Enter a valid target price", "err"); return; }
      state.alerts = state.alerts.filter(x => x.symbol !== a.dataset.alert);
      state.alerts.push({ symbol: a.dataset.alert, px, dir });
      store.set("alerts", state.alerts);
      toast(`Alert set: ${esc(a.dataset.alert)} ${dir === "above" ? "▲" : "▼"} ${fmtPx(px)}`, "ok");
      vWatch(el);
    });
    el.querySelectorAll("[data-unalert]").forEach(a => a.onclick = (e) => {
      e.preventDefault();
      state.alerts = state.alerts.filter(x => x.symbol !== a.dataset.unalert);
      store.set("alerts", state.alerts);
      vWatch(el);
    });
    clearViewTimer();
    viewTimer = setInterval(() => { if (state.fn === "W") vWatch(el); }, 60000);
  } catch (e) { verror(el, "watchlist failed: " + e.message, () => vWatch(el)); }
}
function addToWl(el) {
  const inp = el.querySelector("#wlAdd");
  const s = (inp.value || "").trim().toUpperCase();
  if (!s) return;
  if (!wl().includes(s)) { wl().push(s); store.set("watchlist", state.watchlist); }
  refreshWlMini(); vWatch(el);
}
function checkAlerts(quotes) {
  for (const q of quotes || []) {
    const a = state.alerts.find(x => x.symbol === q.symbol);
    if (!a || q.price === null) continue;
    const hit = a.dir === "above" ? q.price >= a.px : q.price <= a.px;
    const key = a.symbol + a.dir + a.px;
    if (hit && !state.fired.has(key)) {
      state.fired.add(key);
      toast(`🔔 <b>${esc(a.symbol)}</b> ${a.dir === "above" ? "rose above" : "fell below"} <b>${fmtPx(a.px)}</b> (now ${fmtPx(q.price)})`, "ok");
      if ("Notification" in window && Notification.permission === "granted") {
        try { new Notification(`${a.symbol} ${a.dir === "above" ? "▲" : "▼"} ${fmtPx(a.px)}`, { body: `Now ${fmtPx(q.price)}` }); } catch {}
      }
      state.alerts = state.alerts.filter(x => x !== a);
      store.set("alerts", state.alerts);
      if (state.fn === "W") { const el = document.getElementById("view"); if (el) vWatch(el); }
    }
  }
  if ("Notification" in window && Notification.permission === "default" && state.alerts.length) {
    Notification.requestPermission().catch(() => {});
  }
}

/* ================= HELP ================= */
function vHelp(el) {
  clearViewTimer();
  el.innerHTML = `
    <h3 class="sub">COMMANDS — type in the bar, press Enter (or click &lt;GO&gt;)</h3>
    <table class="t"><thead><tr><th>Command</th><th class="l">Does</th></tr></thead><tbody>
    ${[["AAPL", "Load Apple, open price chart"], ["AAPL GP / GP AAPL", "Price chart for a ticker"],
      ["MSFT DES", "Company description + filings"], ["NVDA FA", "Financial statements + earnings"],
      ["N TSLA / TSLA N", "News for a ticker"], ["NEWS", "News for current ticker"],
      ["TOP", "Market overview"], ["ECO", "Economic calendar + FRED charts"],
      ["SCR", "Stock screener — value / yield / momentum"],
      ["W", "Your watchlist + alerts"], ["HELP", "This screen"]]
      .map(([a, b]) => `<tr><td><b style="color:var(--amber)">${a}</b></td><td class="l">${b}</td></tr>`).join("")}</tbody></table>
    <p class="muted">Bloomberg style works too: <b>AAPL US EQUITY GP</b> (country/market words ignored). Just typing a name shows search matches.</p>
    <h3 class="sub">KEYBOARD</h3>
    <table class="t"><tbody>
    ${[["/", "Focus command bar"], ["Enter", "Run command"], ["Esc", "Clear / close autocomplete"],
      ["Alt+1 … Alt+9", "Jump to TOP GP DES FA SCR N ECO W HELP"], ["↑ / ↓", "Move in autocomplete"]]
      .map(([a, b]) => `<tr><td><b style="color:var(--amber)">${a}</b></td><td class="l">${b}</td></tr>`).join("")}</tbody></table>
    <h3 class="sub">DATA & FREE KEYS</h3>
    <p class="muted">Keyless: Yahoo Finance, Stooq, FRED csv, SEC EDGAR, Google News RSS.<br>
    Optional free keys in <b>.env</b> unlock more: <b>FRED_API_KEY</b> (800k series, 120 req/min, instant at fred.stlouisfed.org) and
    <b>FINNHUB_API_KEY</b> (~60 calls/min real-time US quotes + news + econ calendar at finnhub.io).<br><br>
    Quotes are delayed. Demo mode (amber badge) = offline simulation. Not investment advice. Not affiliated with Bloomberg.</p>`;
}

/* ================= rails + header ================= */
async function updateSecBox() {
  const sym = state.symbol;
  document.getElementById("secSym").textContent = sym;
  try {
    const q = await api("/api/quote", { symbol: sym });
    document.getElementById("secName").textContent = q.name || sym;
    const px = document.getElementById("secPx");
    px.textContent = fmtPx(q.price);
    px.className = "sec-px " + cls(q.change);
    const ch = document.getElementById("secChg");
    ch.textContent = `${fmtChg(q.change)} (${fmtPct(q.pct)})`;
    ch.className = "sec-chg " + cls(q.change);
  } catch {
    document.getElementById("secPx").textContent = "—";
  }
}

async function refreshWlMini() {
  const box = document.getElementById("wlMini");
  try {
    const d = await apiPost("/api/quotes", { symbols: wl().slice(0, 12) });
    checkAlerts(d.quotes);
    box.innerHTML = d.quotes.map(q => `<div class="wlrow" data-sym="${esc(q.symbol)}">
      <span class="s">${esc(q.symbol)}</span><span class="p num">${fmtPx(q.price)}</span>
      <span class="c ${cls(q.pct)}">${fmtPct(q.pct)}</span></div>`).join("");
    box.querySelectorAll(".wlrow").forEach(r => r.onclick = () => goSymbol(r.dataset.sym, "GP"));
  } catch { box.innerHTML = `<div class="muted">offline</div>`; }
}

async function refreshRails() {
  const nb = document.getElementById("newsRail"), eb = document.getElementById("ecoRail");
  try {
    const n = await api("/api/news/market", { limit: 6 });
    nb.innerHTML = n.articles.map(a => `<div class="rail-item" data-link="${esc(a.link || "")}">
      <span class="t">${esc(a.title)}</span><span class="m">${esc(a.publisher || "")} · ${esc(ago(a.published))}</span></div>`).join("");
    nb.querySelectorAll(".rail-item").forEach(r => r.onclick = () => { if (r.dataset.link) window.open(r.dataset.link, "_blank"); });
  } catch { nb.innerHTML = `<div class="muted">offline</div>`; }
  try {
    const c = await api("/api/econ/calendar", { days: 7 });
    const today = new Date().toISOString().slice(0, 10);
    const up = c.events.filter(e => e.date >= today).slice(0, 6);
    eb.innerHTML = up.map(e => `<div class="rail-item"><span class="t">${esc(e.date.slice(5))} ${esc(e.time || "")} — ${esc(e.name)}</span>
      <span class="m ${e.importance >= 3 ? "dot3" : e.importance === 2 ? "dot2" : "dot1"}">${"●".repeat(e.importance || 1)} f/c ${e.forecast ?? "—"} · prev ${e.previous ?? "—"}</span></div>`).join("")
      || `<div class="muted">no events</div>`;
  } catch { eb.innerHTML = `<div class="muted">offline</div>`; }
}
