/* OpenBerg charts.js — tiny canvas chart engine (line, candles, volume, spark, heatmap). */
"use strict";

const C_UP = "#00d664", C_DN = "#ff4332", C_AMBER = "#ffa100", C_GRID = "#1e1e22", C_TXT = "#8a8a90";

function setupCanvas(cv, hCss) {
  const dpr = window.devicePixelRatio || 1;
  const w = cv.clientWidth || cv.parentElement.clientWidth || 800;
  const h = hCss;
  cv.width = w * dpr; cv.height = h * dpr;
  cv.style.height = h + "px";
  const ctx = cv.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { ctx, W: w, H: h };
}

function sma(vals, n) {
  const out = new Array(vals.length).fill(null);
  let s = 0;
  for (let i = 0; i < vals.length; i++) {
    s += vals[i];
    if (i >= n) s -= vals[i - n];
    if (i >= n - 1) out[i] = s / n;
  }
  return out;
}

function niceTicks(lo, hi, n = 5) {
  if (lo === hi) { lo -= 1; hi += 1; }
  const span = hi - lo, step0 = span / n, mag = Math.pow(10, Math.floor(Math.log10(step0)));
  const norm = step0 / mag;
  const step = (norm < 1.5 ? 1 : norm < 3.5 ? 2 : norm < 7.5 ? 5 : 10) * mag;
  const ticks = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi; v += step) ticks.push(+v.toFixed(10));
  return ticks;
}

/* Main OHLC chart with crosshair. bars: [{t,o,h,l,c,v}] */
function drawOHLC(cv, bars, opts = {}) {
  const { ctx, W, H } = setupCanvas(cv, opts.height || 340);
  const padL = 8, padR = 64, padT = 12, padB = 22;
  const volH = opts.volume === false ? 0 : Math.round(H * 0.18);
  const plotH = H - padT - padB - volH - 6, plotW = W - padL - padR;
  ctx.clearRect(0, 0, W, H);
  if (!bars || !bars.length) { ctx.fillStyle = C_TXT; ctx.fillText("no data", 20, 30); return; }

  let lo = Infinity, hi = -Infinity, vmax = 0;
  for (const b of bars) { lo = Math.min(lo, b.l); hi = Math.max(hi, b.h); vmax = Math.max(vmax, b.v || 0); }
  const spanPad = (hi - lo) * 0.06 || 1;
  lo -= spanPad; hi += spanPad;
  const log = !!opts.log;
  const fy = log
    ? (v) => { const L0 = Math.log(lo), L1 = Math.log(hi); return padT + plotH - ((Math.log(Math.max(v, 1e-9)) - L0) / (L1 - L0)) * plotH; }
    : (v) => padT + plotH - ((v - lo) / (hi - lo)) * plotH;
  const fx = (i) => padL + (bars.length === 1 ? plotW / 2 : (i / (bars.length - 1)) * plotW);

  // grid + y labels
  ctx.strokeStyle = C_GRID; ctx.fillStyle = C_TXT; ctx.font = "10px ui-monospace, monospace";
  ctx.lineWidth = 1; ctx.textBaseline = "middle";
  for (const t of niceTicks(lo, hi)) {
    const y = Math.round(fy(t)) + 0.5;
    ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W - padR, y); ctx.stroke();
    ctx.fillText(fmtPx(t), W - padR + 5, y);
  }
  // x labels (5)
  ctx.textAlign = "center";
  for (let k = 0; k < 5; k++) {
    const i = Math.round((k / 4) * (bars.length - 1));
    ctx.fillText(String(bars[i].t).slice(0, 10), fx(i), H - 8);
  }
  ctx.textAlign = "left";

  const closes = bars.map(b => b.c);
  const upDay = closes[closes.length - 1] >= closes[0];

  if (opts.type === "line") {
    // area fill
    const grad = ctx.createLinearGradient(0, padT, 0, padT + plotH);
    const base = upDay ? "0,214,100" : "255,67,50";
    grad.addColorStop(0, `rgba(${base},.28)`); grad.addColorStop(1, `rgba(${base},0)`);
    ctx.beginPath(); ctx.moveTo(fx(0), fy(closes[0]));
    closes.forEach((c, i) => ctx.lineTo(fx(i), fy(c)));
    ctx.lineTo(fx(bars.length - 1), padT + plotH); ctx.lineTo(fx(0), padT + plotH); ctx.closePath();
    ctx.fillStyle = grad; ctx.fill();
    // line
    ctx.beginPath(); ctx.moveTo(fx(0), fy(closes[0]));
    closes.forEach((c, i) => ctx.lineTo(fx(i), fy(c)));
    ctx.strokeStyle = upDay ? C_UP : C_DN; ctx.lineWidth = 1.6; ctx.stroke();
  } else {
    const bw = Math.max(1, Math.min(14, (plotW / bars.length) * 0.62));
    for (let i = 0; i < bars.length; i++) {
      const b = bars[i], x = fx(i), c = b.c >= b.o ? C_UP : C_DN;
      ctx.strokeStyle = c; ctx.fillStyle = c;
      ctx.beginPath(); ctx.moveTo(x, fy(b.h)); ctx.lineTo(x, fy(b.l)); ctx.stroke();
      const yO = fy(b.o), yC = fy(b.c);
      ctx.fillRect(x - bw / 2, Math.min(yO, yC), bw, Math.max(1, Math.abs(yC - yO)));
    }
  }

  // SMAs
  for (const [n, col] of [[20, C_AMBER], [50, "#35c4ff"]]) {
    if ((n === 20 && !opts.sma20) || (n === 50 && !opts.sma50)) continue;
    if (bars.length < n) continue;
    ctx.strokeStyle = col; ctx.lineWidth = 1.2; ctx.beginPath();
    let started = false;
    sma(closes, n).forEach((v, i) => {
      if (v === null) return;
      if (!started) { ctx.moveTo(fx(i), fy(v)); started = true; } else ctx.lineTo(fx(i), fy(v));
    });
    ctx.stroke();
  }

  // last price line
  const last = closes[closes.length - 1];
  ctx.setLineDash([4, 3]);
  ctx.strokeStyle = upDay ? C_UP : C_DN;
  ctx.beginPath(); ctx.moveTo(padL, fy(last)); ctx.lineTo(W - padR, fy(last)); ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = upDay ? C_UP : C_DN;
  ctx.fillRect(W - padR + 2, fy(last) - 8, padR - 4, 16);
  ctx.fillStyle = "#000"; ctx.fillText(fmtPx(last), W - padR + 6, fy(last));

  // volume
  if (volH > 0 && vmax > 0) {
    const vy0 = padT + plotH + 6;
    ctx.fillStyle = C_TXT;
    const bw = Math.max(1, Math.min(14, (plotW / bars.length) * 0.62));
    for (let i = 0; i < bars.length; i++) {
      const b = bars[i];
      ctx.fillStyle = b.c >= b.o ? "rgba(0,214,100,.45)" : "rgba(255,67,50,.45)";
      const h = ((b.v || 0) / vmax) * (volH - 4);
      ctx.fillRect(fx(i) - bw / 2, vy0 + (volH - 4) - h, bw, h);
    }
  }

  // crosshair
  cv.onmousemove = (ev) => {
    const r = cv.getBoundingClientRect();
    const mx = ev.clientX - r.left;
    let best = 0, bd = 1e9;
    for (let i = 0; i < bars.length; i++) { const d = Math.abs(fx(i) - mx); if (d < bd) { bd = d; best = i; } }
    drawOHLC_static(cv, bars, opts, { hi: best });
    let tip = document.getElementById("chartTip");
    if (!tip) { tip = document.createElement("div"); tip.id = "chartTip"; tip.className = "tip"; document.body.appendChild(tip); }
    const b = bars[best];
    tip.style.display = "block";
    tip.style.left = Math.min(window.innerWidth - 190, ev.clientX + 14) + "px";
    tip.style.top = (ev.clientY + 14) + "px";
    const ch = best > 0 ? ((b.c / bars[best - 1].c - 1) * 100) : 0;
    tip.textContent = `${b.t}\nO ${fmtPx(b.o)}  H ${fmtPx(b.h)}\nL ${fmtPx(b.l)}  C ${fmtPx(b.c)}\nVol ${fmtBig(b.v)}  ${fmtPct(ch)}`;
  };
  cv.onmouseleave = () => {
    const tip = document.getElementById("chartTip");
    if (tip) tip.style.display = "none";
    drawOHLC_static(cv, bars, opts, {});
  };
}

/* Static variant with optional highlight index (used by crosshair redraw). */
function drawOHLC_static(cv, bars, opts, extra = {}) {
  const keepMove = cv.onmousemove, keepLeave = cv.onmouseleave;
  cv.onmousemove = null;
  const { ctx, W, H } = setupCanvas(cv, opts.height || 340);
  const padL = 8, padR = 64, padT = 12, padB = 22;
  const volH = opts.volume === false ? 0 : Math.round(H * 0.18);
  const plotH = H - padT - padB - volH - 6, plotW = W - padL - padR;
  ctx.clearRect(0, 0, W, H);
  let lo = Infinity, hi = -Infinity, vmax = 0;
  for (const b of bars) { lo = Math.min(lo, b.l); hi = Math.max(hi, b.h); vmax = Math.max(vmax, b.v || 0); }
  const spanPad = (hi - lo) * 0.06 || 1;
  lo -= spanPad; hi += spanPad;
  const log = !!opts.log;
  const fy = log
    ? (v) => { const L0 = Math.log(lo), L1 = Math.log(hi); return padT + plotH - ((Math.log(Math.max(v, 1e-9)) - L0) / (L1 - L0)) * plotH; }
    : (v) => padT + plotH - ((v - lo) / (hi - lo)) * plotH;
  const fx = (i) => padL + (bars.length === 1 ? plotW / 2 : (i / (bars.length - 1)) * plotW);
  ctx.strokeStyle = C_GRID; ctx.fillStyle = C_TXT; ctx.font = "10px ui-monospace, monospace";
  ctx.lineWidth = 1; ctx.textBaseline = "middle";
  for (const t of niceTicks(lo, hi)) {
    const y = Math.round(fy(t)) + 0.5;
    ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W - padR, y); ctx.stroke();
    ctx.fillText(fmtPx(t), W - padR + 5, y);
  }
  ctx.textAlign = "center";
  for (let k = 0; k < 5; k++) {
    const i = Math.round((k / 4) * (bars.length - 1));
    ctx.fillText(String(bars[i].t).slice(0, 10), fx(i), H - 8);
  }
  ctx.textAlign = "left";
  const closes = bars.map(b => b.c);
  const upDay = closes[closes.length - 1] >= closes[0];
  if (opts.type === "line") {
    const grad = ctx.createLinearGradient(0, padT, 0, padT + plotH);
    const base = upDay ? "0,214,100" : "255,67,50";
    grad.addColorStop(0, `rgba(${base},.28)`); grad.addColorStop(1, `rgba(${base},0)`);
    ctx.beginPath(); ctx.moveTo(fx(0), fy(closes[0]));
    closes.forEach((c, i) => ctx.lineTo(fx(i), fy(c)));
    ctx.lineTo(fx(bars.length - 1), padT + plotH); ctx.lineTo(fx(0), padT + plotH); ctx.closePath();
    ctx.fillStyle = grad; ctx.fill();
    ctx.beginPath(); ctx.moveTo(fx(0), fy(closes[0]));
    closes.forEach((c, i) => ctx.lineTo(fx(i), fy(c)));
    ctx.strokeStyle = upDay ? C_UP : C_DN; ctx.lineWidth = 1.6; ctx.stroke();
  } else {
    const bw = Math.max(1, Math.min(14, (plotW / bars.length) * 0.62));
    for (let i = 0; i < bars.length; i++) {
      const b = bars[i], x = fx(i), c = b.c >= b.o ? C_UP : C_DN;
      ctx.strokeStyle = c; ctx.fillStyle = c;
      ctx.beginPath(); ctx.moveTo(x, fy(b.h)); ctx.lineTo(x, fy(b.l)); ctx.stroke();
      const yO = fy(b.o), yC = fy(b.c);
      ctx.fillRect(x - bw / 2, Math.min(yO, yC), bw, Math.max(1, Math.abs(yC - yO)));
    }
  }
  for (const [n, col] of [[20, C_AMBER], [50, "#35c4ff"]]) {
    if ((n === 20 && !opts.sma20) || (n === 50 && !opts.sma50)) continue;
    if (bars.length < n) continue;
    ctx.strokeStyle = col; ctx.lineWidth = 1.2; ctx.beginPath();
    let st = false;
    sma(closes, n).forEach((v, i) => {
      if (v === null) return;
      if (!st) { ctx.moveTo(fx(i), fy(v)); st = true; } else ctx.lineTo(fx(i), fy(v));
    });
    ctx.stroke();
  }
  const last = closes[closes.length - 1];
  ctx.setLineDash([4, 3]); ctx.strokeStyle = upDay ? C_UP : C_DN;
  ctx.beginPath(); ctx.moveTo(padL, fy(last)); ctx.lineTo(W - padR, fy(last)); ctx.stroke();
  ctx.setLineDash([]);
  if (volH > 0 && vmax > 0) {
    const vy0 = padT + plotH + 6;
    const bw = Math.max(1, Math.min(14, (plotW / bars.length) * 0.62));
    for (let i = 0; i < bars.length; i++) {
      const b = bars[i];
      ctx.fillStyle = b.c >= b.o ? "rgba(0,214,100,.45)" : "rgba(255,67,50,.45)";
      const h = ((b.v || 0) / vmax) * (volH - 4);
      ctx.fillRect(fx(i) - bw / 2, vy0 + (volH - 4) - h, bw, h);
    }
  }
  if (extra.hi !== undefined && bars[extra.hi]) {
    const i = extra.hi, b = bars[i];
    ctx.strokeStyle = "#666"; ctx.setLineDash([3, 3]);
    ctx.beginPath(); ctx.moveTo(fx(i), padT); ctx.lineTo(fx(i), padT + plotH); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = C_AMBER;
    ctx.beginPath(); ctx.arc(fx(i), fy(b.c), 3, 0, 7); ctx.fill();
  }
  cv.onmousemove = keepMove; cv.onmouseleave = keepLeave;
}

/* Simple series line chart (econ). points: [{t, v}] */
function drawSeries(cv, points, opts = {}) {
  const { ctx, W, H } = setupCanvas(cv, opts.height || 220);
  ctx.clearRect(0, 0, W, H);
  if (!points || !points.length) { ctx.fillStyle = C_TXT; ctx.fillText("no data", 20, 30); return; }
  const padL = 8, padR = 64, padT = 12, padB = 22;
  const plotW = W - padL - padR, plotH = H - padT - padB;
  const vs = points.map(p => p.v);
  let lo = Math.min(...vs), hi = Math.max(...vs);
  if (lo === hi) { lo -= 1; hi += 1; }
  const pad = (hi - lo) * 0.08; lo -= pad; hi += pad;
  const fx = (i) => padL + (i / (points.length - 1)) * plotW;
  const fy = (v) => padT + plotH - ((v - lo) / (hi - lo)) * plotH;
  ctx.strokeStyle = C_GRID; ctx.fillStyle = C_TXT; ctx.font = "10px ui-monospace, monospace";
  ctx.textBaseline = "middle";
  for (const t of niceTicks(lo, hi)) {
    const y = Math.round(fy(t)) + 0.5;
    ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W - padR, y); ctx.stroke();
    ctx.fillText(fmtPx(t), W - padR + 5, y);
  }
  ctx.textAlign = "center";
  for (let k = 0; k < 5; k++) {
    const i = Math.round((k / 4) * (points.length - 1));
    ctx.fillText(String(points[i].t).slice(0, 10), fx(i), H - 8);
  }
  ctx.textAlign = "left";
  const col = opts.color || C_AMBER;
  const grad = ctx.createLinearGradient(0, padT, 0, padT + plotH);
  grad.addColorStop(0, "rgba(255,161,0,.25)"); grad.addColorStop(1, "rgba(255,161,0,0)");
  ctx.beginPath(); ctx.moveTo(fx(0), fy(vs[0]));
  vs.forEach((v, i) => ctx.lineTo(fx(i), fy(v)));
  ctx.lineTo(fx(vs.length - 1), padT + plotH); ctx.lineTo(fx(0), padT + plotH); ctx.closePath();
  ctx.fillStyle = grad; ctx.fill();
  ctx.beginPath(); ctx.moveTo(fx(0), fy(vs[0]));
  vs.forEach((v, i) => ctx.lineTo(fx(i), fy(v)));
  ctx.strokeStyle = col; ctx.lineWidth = 1.6; ctx.stroke();
  const last = vs[vs.length - 1];
  ctx.fillStyle = col;
  ctx.beginPath(); ctx.arc(fx(vs.length - 1), fy(last), 3, 0, 7); ctx.fill();
}

/* Sparkline. values: [n] */
function drawSpark(cv, values) {
  const dpr = window.devicePixelRatio || 1;
  const w = cv.clientWidth || 90, h = cv.clientHeight || 24;
  cv.width = w * dpr; cv.height = h * dpr;
  const ctx = cv.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, w, h);
  if (!values || values.length < 2) return;
  const lo = Math.min(...values), hi = Math.max(...values), sp = (hi - lo) || 1;
  const up = values[values.length - 1] >= values[0];
  ctx.strokeStyle = up ? C_UP : C_DN; ctx.lineWidth = 1.2;
  ctx.beginPath();
  values.forEach((v, i) => {
    const x = (i / (values.length - 1)) * w, y = h - 2 - ((v - lo) / sp) * (h - 4);
    i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  });
  ctx.stroke();
}

/* Heatmap tiles. items: [{symbol, pct}] */
function drawHeatmap(cv, items) {
  const dpr = window.devicePixelRatio || 1;
  const w = cv.clientWidth || 600, rows = Math.ceil(items.length / 5), h = Math.max(90, rows * 56);
  cv.width = w * dpr; cv.height = h * dpr; cv.style.height = h + "px";
  const ctx = cv.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, w, h);
  const cols = 5, tw = w / cols, th = h / rows;
  ctx.font = "bold 12px ui-monospace, monospace"; ctx.textBaseline = "middle";
  items.forEach((it, i) => {
    const x = (i % cols) * tw, y = Math.floor(i / cols) * th;
    const p = Math.max(-3, Math.min(3, it.pct || 0)) / 3;
    ctx.fillStyle = p >= 0 ? `rgba(0,214,100,${0.12 + p * 0.55})` : `rgba(255,67,50,${0.12 - p * 0.55})`;
    ctx.fillRect(x + 2, y + 2, tw - 4, th - 4);
    ctx.fillStyle = "#fff";
    ctx.fillText(it.symbol, x + 8, y + th / 2 - 9);
    ctx.font = "11px ui-monospace, monospace";
    ctx.fillStyle = p >= 0 ? C_UP : C_DN;
    ctx.fillText(fmtPct(it.pct), x + 8, y + th / 2 + 9);
    ctx.font = "bold 12px ui-monospace, monospace";
  });
}
