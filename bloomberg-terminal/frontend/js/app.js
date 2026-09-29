/* OpenBerg app.js — boot, command bar, autocomplete, keyboard. */
"use strict";

const FNS = ["TOP", "GP", "DES", "FA", "N", "ECO", "W", "HELP"];
const FN_ALIAS = { NEWS: "N", WL: "W", WATCH: "W", H: "HELP", "?": "HELP", CHART: "GP", ECON: "ECO" };
const FILLER = new Set(["US", "USA", "UE", "EQUITY", "EQUITIES", "STOCK", "CORP", "<GO>", "GO"]);
const RENDER = { TOP: vTop, GP: vGP, DES: vDes, FA: vFA, N: vNews, ECO: vEco, W: vWatch, HELP: vHelp };

function goSymbol(sym, fn) {
  state.symbol = sym.toUpperCase();
  updateSecBox();
  setFn(fn || "GP");
  document.getElementById("cmdInput").value = "";
}

function setFn(fn) {
  state.fn = fn;
  clearViewTimer();
  document.querySelectorAll("#fnTabs button").forEach(b => b.classList.toggle("on", b.dataset.fn === fn));
  document.querySelectorAll("#fnList li").forEach(li => li.classList.toggle("on", li.dataset.fn === fn));
  document.getElementById("viewTitle").textContent = FN_TITLES[fn] + (["GP", "DES", "FA", "N"].includes(fn) ? ` — ${state.symbol}` : "");
  RENDER[fn](document.getElementById("view"));
}

/* ---------- command parser ---------- */
function parseCmd(raw) {
  const toks = raw.trim().split(/\s+/).filter(t => !FILLER.has(t.toUpperCase().replace(/[<>\s]/g, "")));
  if (!toks.length) return null;
  const norm = toks.map(t => t.toUpperCase());
  const fnAt = norm.findIndex(t => FNS.includes(t) || FN_ALIAS[t]);
  let fn = fnAt >= 0 ? (FN_ALIAS[norm[fnAt]] || norm[fnAt]) : null;
  const symToks = toks.filter((_, i) => i !== fnAt);
  let sym = null;
  if (symToks.length) {
    const cand = symToks[0].toUpperCase().replace(/[^A-Z0-9^.\-=]/g, "");
    if (/^[A-Z0-9^][A-Z0-9^.\-=]{0,11}$/.test(cand) && !FILLER.has(cand)) sym = cand;
  }
  return { fn, sym, raw: toks.join(" ") };
}

async function runCommand(raw) {
  const input = document.getElementById("cmdInput");
  hideAC();
  const p = parseCmd(raw || input.value);
  if (!p) return;
  if (p.fn === "HELP" && !p.sym) { setFn("HELP"); input.value = ""; return; }
  if (p.sym && !p.fn) {
    // bare symbol/name: validate via search, default to GP
    const exact = await resolveSymbol(p.sym, p.raw);
    if (exact) { goSymbol(exact, "GP"); }
    return;
  }
  if (p.sym && p.fn) {
    if (["TOP", "ECO", "W", "HELP"].includes(p.fn)) { setFn(p.fn); }
    else {
      const exact = await resolveSymbol(p.sym, p.raw);
      if (exact) goSymbol(exact, p.fn);
    }
    input.value = "";
    return;
  }
  if (!p.sym && p.fn) { setFn(p.fn); input.value = ""; return; }
  // free text -> search
  await resolveSymbol(p.raw, p.raw);
}

async function resolveSymbol(cand, rawText) {
  try {
    const r = await api("/api/search", { q: cand, limit: 6 });
    const res = r.results || [];
    if (!res.length) {
      // try full raw text
      const r2 = await api("/api/search", { q: rawText, limit: 6 });
      if (!(r2.results || []).length) { toast(`No matches for “${esc(rawText)}”`, "err"); return null; }
      return pickSearch(r2.results, rawText);
    }
    const exact = res.find(x => (x.symbol || "").toUpperCase() === cand.toUpperCase());
    if (exact) return exact.symbol;
    return pickSearch(res, rawText);
  } catch { toast("Search failed (offline?)", "err"); return null; }
}

function pickSearch(results, rawText) {
  // show autocomplete-style picker via toast-less inline: reuse AC box
  const box = document.getElementById("acBox");
  acItems = results;
  box.innerHTML = results.map((r, i) => `<div data-i="${i}" class="${i === 0 ? "sel" : ""}"><b>${esc(r.symbol)}</b><span>${esc(r.name || "")}</span></div>`).join("");
  box.hidden = false;
  box.querySelectorAll("div").forEach(d => d.onclick = () => { hideAC(); goSymbol(results[+d.dataset.i].symbol, state.fn === "TOP" || state.fn === "ECO" || state.fn === "W" ? "GP" : state.fn); });
  toast(`Multiple matches for “${esc(rawText)}” — pick one`, "");
  return null;
}

/* ---------- autocomplete ---------- */
let acItems = [], acTimer = null;
function hideAC() { document.getElementById("acBox").hidden = true; acItems = []; }

function wireAutocomplete() {
  const input = document.getElementById("cmdInput"), box = document.getElementById("acBox");
  input.addEventListener("input", () => {
    clearTimeout(acTimer);
    const q = input.value.trim();
    if (q.length < 1) { hideAC(); return; }
    acTimer = setTimeout(async () => {
      // don't autocomplete pure function codes
      if (/^(TOP|GP|DES|FA|NEWS?|ECO|WATCH?|HELP)\s*$/i.test(q)) { hideAC(); return; }
      try {
        const r = await api("/api/search", { q, limit: 8 });
        acItems = r.results || [];
        if (!acItems.length) { hideAC(); return; }
        box.innerHTML = acItems.map((x, i) => `<div data-i="${i}" class="${i === 0 ? "sel" : ""}"><b>${esc(x.symbol)}</b><span>${esc(x.name || "")}</span></div>`).join("");
        box.hidden = false;
        box.querySelectorAll("div").forEach(d => d.onclick = () => {
          input.value = acItems[+d.dataset.i].symbol + " ";
          hideAC(); input.focus();
        });
      } catch { hideAC(); }
    }, 220);
  });
  input.addEventListener("keydown", (e) => {
    if (!box.hidden && acItems.length && (e.key === "ArrowDown" || e.key === "ArrowUp")) {
      e.preventDefault();
      const sels = [...box.querySelectorAll("div")];
      let i = sels.findIndex(d => d.classList.contains("sel"));
      i = e.key === "ArrowDown" ? (i + 1) % sels.length : (i - 1 + sels.length) % sels.length;
      sels.forEach((d, j) => d.classList.toggle("sel", j === i));
    } else if (e.key === "Enter") {
      if (!box.hidden && acItems.length) {
        const sel = box.querySelector("div.sel");
        if (sel && input.value.trim().indexOf(" ") === -1) {
          e.preventDefault();
          hideAC();
          goSymbol(acItems[+sel.dataset.i].symbol, "GP");
          return;
        }
      }
      runCommand(input.value);
    } else if (e.key === "Escape") {
      if (!box.hidden) hideAC(); else input.value = "";
      input.blur();
    }
  });
  document.addEventListener("click", (e) => { if (!e.target.closest(".cmd")) hideAC(); });
}

/* ---------- clock ---------- */
function tickClock() {
  const d = new Date();
  const days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
  const p = (n) => String(n).padStart(2, "0");
  document.getElementById("clock").textContent =
    `${days[d.getDay()]} ${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

/* ---------- boot ---------- */
async function boot() {
  // tabs + fn list
  document.querySelectorAll("#fnTabs button").forEach(b => b.onclick = () => setFn(b.dataset.fn));
  document.querySelectorAll("#fnList li").forEach(li => li.onclick = () => setFn(li.dataset.fn));
  document.querySelectorAll("[data-goto]").forEach(a => a.onclick = (e) => { e.preventDefault(); setFn(a.dataset.goto); });
  document.getElementById("wlEdit").onclick = (e) => { e.preventDefault(); setFn("W"); };
  document.getElementById("goBtn").onclick = () => runCommand();
  wireAutocomplete();

  // global keys
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== document.getElementById("cmdInput")) {
      e.preventDefault(); document.getElementById("cmdInput").focus();
    }
    if (e.altKey && e.key >= "1" && e.key <= "8") {
      e.preventDefault(); setFn(FNS[+e.key - 1]);
    }
  });

  tickClock(); setInterval(tickClock, 1000);

  try {
    state.status = await api("/api/status");
    const kb = document.getElementById("keyBadge");
    const keys = [state.status.has_fred_key && "FRED", state.status.has_finnhub_key && "FINNHUB"].filter(Boolean);
    kb.textContent = "keys: " + (keys.join("+") || "none");
    kb.title = keys.length ? `${keys.join(", ")} key(s) configured` : "No API keys — running on keyless sources + demo fallback. See HELP.";
    if (!state.watchlist) {
      state.watchlist = [...(state.status.default_watchlist || ["AAPL"])];
      store.set("watchlist", state.watchlist);
    }
  } catch {
    toast("Backend unreachable — is the server running?", "err");
  }

  updateSecBox();
  refreshWlMini();
  refreshRails();
  setFn("GP");
  setInterval(refreshWlMini, 60000);
  setInterval(refreshRails, 600000);
  setInterval(updateSecBox, 60000);
}

document.addEventListener("DOMContentLoaded", boot);
