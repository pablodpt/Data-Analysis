/* OpenBerg api.js — state, fetch wrapper, formatters, toasts. No dependencies. */
"use strict";

const store = {
  get(k, d) { try { const v = localStorage.getItem("ob:" + k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem("ob:" + k, JSON.stringify(v)); } catch {} },
};

const state = {
  symbol: "AAPL",
  fn: "GP",
  range: "1Y",
  chartType: "candle",
  showVol: true,
  showSMA20: true,
  showSMA50: false,
  logScale: false,
  stmt: "income",
  period: "annual",
  moversGroup: "gainers",
  ecoSeries: "DGS10",
  watchlist: store.get("watchlist", null),
  alerts: store.get("alerts", []),
  fired: new Set(),
  status: null,
  lastMode: "—",
  lastSrc: "—",
};

async function api(path, params = {}, opts = {}) {
  const qs = new URLSearchParams(params).toString();
  const url = path + (qs ? "?" + qs : "");
  const ms = opts.timeout || 25000;
  const ctl = new AbortController();
  const to = setTimeout(() => ctl.abort(), ms);
  try {
    const r = await fetch(url, { signal: ctl.signal, ...(opts.fetch || {}) });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const j = await r.json();
    if (j && j.mode) setMode(j.mode, j.source || "—");
    return j;
  } catch (err) {
    // Chrome reports a bare abort() as cryptic "signal is aborted without reason"
    if (ctl.signal.aborted) throw new Error(`request timed out after ${Math.round(ms / 1000)}s`);
    throw err;
  } finally { clearTimeout(to); }
}

async function apiPost(path, body) {
  const r = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  const j = await r.json();
  if (j && j.mode) {
    // show the dominant real provider (yahoo/stooq/...) instead of "watchlist"
    const counts = {};
    for (const q of j.quotes || []) if (q.source) counts[q.source] = (counts[q.source] || 0) + 1;
    const top = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
    setMode(j.mode, top ? top[0] : "—");
  }
  return j;
}

function setMode(mode, src) {
  state.lastMode = mode; state.lastSrc = src;
  const b = document.getElementById("modeBadge");
  b.textContent = mode.toUpperCase();
  b.className = "badge " + (mode === "live" ? "live" : mode === "mixed" ? "mixed" : "demo");
  b.title = `Data mode: ${mode} · source: ${src}`;
  document.getElementById("stMode").textContent = "mode: " + mode;
  document.getElementById("stSrc").textContent = "src: " + src;
}

/* ---------- formatters ---------- */
const nf0 = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
const nf2 = new Intl.NumberFormat("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

function fmtPx(v) {
  if (v === null || v === undefined || isNaN(v)) return "—";
  const a = Math.abs(v);
  if (a >= 1000) return nf2.format(v);
  if (a >= 1) return nf2.format(v);
  if (a === 0) return "0.00";
  return String(+v.toFixed(4));
}
function fmtChg(v) { return (v === null || v === undefined || isNaN(v)) ? "—" : (v >= 0 ? "+" : "") + fmtPx(v); }
function fmtPct(v) { return (v === null || v === undefined || isNaN(v)) ? "—" : (v >= 0 ? "+" : "") + (+v).toFixed(2) + "%"; }
function fmtMs(v) { return v === null || v === undefined ? "" : (v >= 1000 ? ` ${(v / 1000).toFixed(1)}s` : ` ${v}ms`); }
function cls(v) { return v === null || v === undefined ? "" : (v >= 0 ? "up" : "down"); }
function fmtBig(v) {
  if (v === null || v === undefined || isNaN(v)) return "—";
  const a = Math.abs(v);
  if (a >= 1e12) return (v / 1e12).toFixed(2) + "T";
  if (a >= 1e9) return (v / 1e9).toFixed(2) + "B";
  if (a >= 1e6) return (v / 1e6).toFixed(1) + "M";
  if (a >= 1e3) return (v / 1e3).toFixed(1) + "K";
  return nf0.format(v);
}
function fmtDate(iso) { return (iso || "").slice(0, 10); }
function ago(iso) {
  const t = Date.parse(iso);
  if (!t) return (iso || "").slice(0, 16).replace("T", " ");
  const m = Math.max(0, (Date.now() - t) / 60000);
  if (m < 1) return "now";
  if (m < 60) return `${m | 0}m ago`;
  const h = m / 60;
  if (h < 24) return `${h | 0}h ago`;
  const d = h / 24;
  if (d < 7) return `${d | 0}d ago`;
  return (iso || "").slice(0, 10);
}
function esc(s) { return String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c])); }

/* ---------- toasts ---------- */
function toast(msg, kind = "") {
  const box = document.getElementById("toasts");
  const el = document.createElement("div");
  el.className = "toast " + kind;
  el.innerHTML = msg;
  box.appendChild(el);
  setTimeout(() => { el.style.opacity = "0"; el.style.transition = "opacity .4s"; setTimeout(() => el.remove(), 450); }, 4200);
}

/* ---------- CSV ---------- */
function downloadCSV(name, rows) {
  const csv = rows.map(r => r.map(c => `"${String(c ?? "").replace(/"/g, '""')}"`).join(",")).join("\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 5000);
}
