#!/usr/bin/env python3
"""
make_dashboard.py — Genera un dashboard HTML **autocontenido** a partir de
`resultados/resumen.json` y `resultados/significancia_vs_base.csv`.

Diseño:
  * Un único archivo `resultados/dashboard.html` que se abre con doble clic.
  * Los datos van INCRUSTADOS en el HTML (no usa fetch → funciona con file://
    sin servidor y sin CORS).
  * Los gráficos se dibujan con SVG/JS puro: **cero dependencias externas, cero
    CDN, funciona sin internet**.
  * Botón para cargar otro `resumen.json` distinto (File API, también funciona
    en local).

Uso:
    python make_dashboard.py                       # usa resultados/resumen.json
    python make_dashboard.py --db ruta.duckdb      # + metadatos de la base
"""
from __future__ import annotations

import argparse
import csv
import json
import os

# --------------------------------------------------------------------------
# Carga de datos
# --------------------------------------------------------------------------
def cargar_resumen(path_json: str, path_csv: str) -> dict:
    with open(path_json, encoding="utf-8") as fh:
        res = json.load(fh)

    sig: list[dict] = []
    if os.path.exists(path_csv):
        with open(path_csv, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                def num(k, conv=float):
                    v = row.get(k)
                    try:
                        return conv(v)
                    except (TypeError, ValueError):
                        return None
                sig.append({
                    "patron": row.get("patron"),
                    "bucket": row.get("bucket"),
                    "h": num("horizonte_d", int),
                    "n": num("n", int),
                    "hit": num("hit"),
                    "lo": num("hit_lo95"),
                    "hi": num("hit_hi95"),
                    "base": num("base"),
                    "delta_pp": num("delta_pp"),
                    "p": num("p_valor"),
                    "sig": (row.get("significativo_5%") == "sí"),
                })

    q = res.get("queries", {})
    ex = res.get("extras", {})

    # series de quintiles: cualquier patrón con columna 'q'
    quintiles = {k: v for k, v in q.items() if v and isinstance(v, list) and "q" in v[0]}

    data = {
        "meta": {
            "db": res.get("db", ""),
            "generado": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "base": ex.get("base_rates", {}),
        "significancia": sig,
        "quintiles": quintiles,
        "momentum_quintiles": q.get("momentum_quintiles", {}),
        "momentum_ls": ex.get("momentum_ls", []),
        "momentum_ic": ex.get("momentum_ic", []),
        "autocorr": ex.get("autocorrelacion", {}),
        "seasonality": q.get("seasonality", []),
        "regime": q.get("market_regime", []),
        "eventos": q.get("new_52w_high_event", []),
        "extremos": q.get("extreme_down_events", []),
        "trend": q.get("trend_sma", []),
        "breakout": q.get("breakout_20d", []),
        "composite_periodo": q.get("composite_by_period", []),
        "monthly": q.get("monthly_signals", []),
        "n_patrones": len(q),
    }
    return data


def meta_desde_db(db_path: str) -> dict:
    """Lee rango de fechas y nº de tickers de la base (si es accesible)."""
    try:
        import duckdb
        con = duckdb.connect(db_path, read_only=True)
        d0, d1, n = con.execute(
            "SELECT MIN(date), MAX(date), COUNT(DISTINCT symbol) FROM prices"
        ).fetchone()
        filas = con.execute("SELECT COUNT(*) FROM prices").fetchone()[0]
        con.close()
        return {"fecha_min": str(d0), "fecha_max": str(d1),
                "n_tickers": int(n), "n_filas": int(filas)}
    except Exception as exc:  # noqa: BLE001
        print(f"[aviso] no se pudieron leer metadatos de la base: {exc}")
        return {}


# --------------------------------------------------------------------------
# Plantilla HTML
# --------------------------------------------------------------------------
HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard de patrones — S&P 500</title>
<style>
:root{
  --bg:#f4f6f9; --card:#fff; --ink:#16202c; --muted:#5b6b7f; --line:#e2e8f0;
  --pos:#137a4b; --posbg:#e6f5ec; --neg:#b3261e; --negbg:#fdecea;
  --acc:#1f4e79; --acc2:#2e7ebf; --warn:#8a6100; --warnbg:#fff6e0;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
     font:14px/1.5 "Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header{background:linear-gradient(135deg,#12314f,#1f4e79 55%,#2e7ebf);
       color:#fff;padding:26px 28px 22px}
header h1{margin:0 0 4px;font-size:23px;font-weight:650;letter-spacing:.2px}
header .sub{opacity:.9;font-size:13px}
header .sub b{font-weight:600}
main{max-width:1240px;margin:0 auto;padding:20px 18px 60px}
section{background:var(--card);border:1px solid var(--line);border-radius:12px;
        padding:18px 20px;margin-bottom:18px;box-shadow:0 1px 2px rgba(16,32,48,.04)}
h2{margin:0 0 4px;font-size:17px;color:var(--acc)}
h2+.hint{margin:0 0 16px;color:var(--muted);font-size:12.5px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:12px}
.kpi{background:#fafcfe;border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi .v{font-size:22px;font-weight:650;color:var(--acc);line-height:1.2}
.kpi .l{font-size:11.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.4px;margin-top:2px}
.kpi .s{font-size:11.5px;color:var(--muted);margin-top:3px}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{padding:7px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:middle}
th{background:#f7fafd;color:var(--acc);font-weight:600;cursor:pointer;white-space:nowrap;
   position:sticky;top:0;font-size:12.5px}
th:hover{background:#eef4fa}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
tbody tr:hover{background:#f9fbfd}
.wrap{max-height:520px;overflow:auto;border:1px solid var(--line);border-radius:10px}
.pill{display:inline-block;padding:1px 7px;border-radius:20px;font-size:11.5px;font-weight:600}
.pill.pos{background:var(--posbg);color:var(--pos)}
.pill.neg{background:var(--negbg);color:var(--neg)}
.pill.neu{background:#eef2f6;color:var(--muted)}
.bar{position:relative;height:16px;background:#eef2f6;border-radius:4px;min-width:90px}
.bar i{position:absolute;top:0;bottom:0;border-radius:4px}
.bar i.p{background:var(--pos)} .bar i.n{background:var(--neg)}
.bar span{position:absolute;top:0;bottom:0;width:1px;background:#9aa8b8}
.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:12px}
.controls label{font-size:12.5px;color:var(--muted)}
select,input[type=search],input[type=file],button{
  font:inherit;font-size:13px;padding:6px 9px;border:1px solid #cbd6e2;border-radius:8px;background:#fff}
button{cursor:pointer;background:#f7fafd}
button:hover{background:#eef4fa}
.charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(430px,1fr));gap:16px}
.chart{background:#fbfdff;border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.chart h3{margin:2px 0 8px;font-size:13.5px;color:var(--acc)}
.legend{display:flex;flex-wrap:wrap;gap:10px;margin-top:8px;font-size:12px}
.legend span{display:flex;align-items:center;gap:5px;cursor:pointer;color:var(--muted)}
.legend span.off{opacity:.35;text-decoration:line-through}
.dot{width:10px;height:10px;border-radius:50%;display:inline-block}
.note{background:var(--warnbg);border:1px solid #f0dfae;border-radius:10px;
      padding:12px 14px;color:#4a3a10;font-size:13px}
.note ul{margin:6px 0 0 18px;padding:0}
.note li{margin:3px 0}
.foot{color:var(--muted);font-size:12px;text-align:center;padding:6px 0 0}
.mono{font-family:Consolas,Menlo,monospace;font-size:12px}
code{background:#eef2f6;padding:1px 5px;border-radius:4px;font-size:12.5px}
</style>
</head>
<body>
<header>
  <h1>Dashboard de patrones estadísticos — S&amp;P 500</h1>
  <div class="sub" id="sub"></div>
</header>

<main>
  <section>
    <h2>Resumen</h2>
    <p class="hint">La tasa base es la probabilidad incondicional de que una acción suba.
      Todo patrón se juzga por su <b>exceso</b> sobre esa base, no por su valor absoluto.</p>
    <div class="kpis" id="kpis"></div>
  </section>

  <section>
    <h2>Ranking de señales: P(sube) condicional vs. tasa base</h2>
    <p class="hint">Ordena haciendo clic en las cabeceras. La barra muestra el exceso en puntos
      porcentuales; verde = mejor que la base, rojo = peor. Solo las filas marcadas como
      significativas superan un contraste bilateral al 5&nbsp;%.</p>
    <div class="controls">
      <label>Horizonte
        <select id="fH">
          <option value="">todos</option>
          <option value="21">21 días (~1 mes)</option>
          <option value="63">63 días (~3 meses)</option>
          <option value="5">5 días (~1 semana)</option>
        </select>
      </label>
      <label>Patrón <select id="fP"><option value="">todos</option></select></label>
      <label><input type="checkbox" id="fS"> solo significativas</label>
      <input type="search" id="fQ" placeholder="buscar condición…" style="min-width:190px">
      <button id="btnCsv">Descargar CSV</button>
    </div>
    <div class="wrap"><table id="tRank">
      <thead><tr>
        <th data-k="patron">Patrón</th>
        <th data-k="bucket">Condición</th>
        <th data-k="h" class="num">Horiz.</th>
        <th data-k="n" class="num">n</th>
        <th data-k="hit" class="num">P(sube)</th>
        <th data-k="lo" class="num">IC95&nbsp;%</th>
        <th data-k="delta_pp" class="num">&Delta; vs base</th>
        <th data-k="delta_pp" class="num">Exceso</th>
        <th data-k="sig">Sig.</th>
      </tr></thead>
      <tbody></tbody>
    </table></div>
  </section>

  <section>
    <h2>Probabilidad por quintil</h2>
    <p class="hint">Cada línea es una señal: qué probabilidad de subida tiene cada quintil
      (1 = valor más bajo de la señal, 5 = más alto). La línea discontinua es la tasa base.</p>
    <div class="controls">
      <label>Horizonte
        <select id="qH">
          <option value="hit21">21 días</option>
          <option value="hit63">63 días</option>
          <option value="hit5">5 días</option>
        </select>
      </label>
      <span style="font-size:12.5px;color:var(--muted)">Haz clic en la leyenda para ocultar series.</span>
    </div>
    <div class="chart"><h3 id="qTitle"></h3><div id="qChart"></div><div class="legend" id="qLegend"></div></div>
  </section>

  <section>
    <h2>Eventos y patrones discretos</h2>
    <p class="hint">Comparación directa contra la base: sobre-reacción a caídas, tendencia,
      breakouts y eventos de 52 semanas.</p>
    <div class="charts">
      <div class="chart"><h3>Caídas extremas y sobre-reacción</h3><div id="cEventos"></div></div>
      <div class="chart"><h3>Estados de tendencia (SMA)</h3><div id="cTrend"></div></div>
      <div class="chart"><h3>Estados de 52 semanas</h3><div id="c52w"></div></div>
      <div class="chart"><h3>Breakouts de 20 días</h3><div id="cBreak"></div></div>
    </div>
  </section>

  <section>
    <h2>Momentum (mensual, sin solapamiento)</h2>
    <p class="hint">Versión robusta: rebalanceo mensual, horizontes no solapados.
      Sharpe del portfolio long-short (Q5&minus;Q1) e Information Coefficient de Spearman.</p>
    <div class="charts">
      <div class="chart"><h3>P(sube 1 mes) por quintil de momentum</h3><div id="cMomQ"></div><div class="legend" id="lMomQ"></div></div>
      <div class="chart"><h3>Sharpe L/S e IC por señal</h3><div id="cMomLS"></div></div>
    </div>
    <div class="wrap" style="margin-top:14px"><table id="tMom">
      <thead><tr><th>Señal</th><th class="num">Meses</th><th class="num">Ret. L/S mensual</th>
        <th class="num">Sharpe L/S anual.</th><th class="num">Hit L/S</th>
        <th class="num">IC medio</th><th class="num">IC-IR anual.</th><th class="num">Hit IC</th></tr></thead>
      <tbody></tbody>
    </table></div>
  </section>

  <section>
    <h2>Estacionalidad y regímenes de mercado</h2>
    <div class="charts">
      <div class="chart"><h3>Retorno medio por mes natural</h3><div id="cSeason"></div>
        <div class="hint" style="margin-top:6px">Con ~5 años de datos, trátalo como descriptivo.</div></div>
      <div class="chart"><h3>Régimen de mercado &rarr; retorno forward del índice</h3><div id="cRegime"></div></div>
    </div>
  </section>

  <section>
    <h2>Cómo leer este dashboard</h2>
    <div class="note">
      <b>Advertencias metodológicas (importantes)</b>
      <ul>
        <li><b>Solapamiento:</b> los retornos forward de 21/63 días sobre datos diarios solapan
          entre sí; los t-stats y p-valores están inflados. La muestra efectiva es ~h veces menor
          de lo que sugiere <code>n</code>. Las conclusiones sólidas salen de las versiones
          mensuales no solapadas.</li>
        <li><b>Comparación múltiple:</b> se probaron decenas de umbrales; a &alpha;=5&nbsp;%,
          ~1 de cada 20 hallazgos es falso positivo por construcción. Desconfía de los excesos
          menores a ~1&nbsp;pp.</li>
        <li><b>Sin costes ni capacidad:</b> ningún resultado incluye comisiones, slippage ni
          impacto de mercado.</li>
        <li><b>Muestra:</b> consulta el periodo en la cabecera. Si es una muestra alcista,
          las probabilidades absolutas serán altas y lo relevante es el exceso sobre la base.</li>
        <li><b>Sesgo de supervivencia:</b> la lista de tickers son empresas que siguen en el
          índice hoy.</li>
      </ul>
    </div>
    <p class="hint" style="margin:14px 0 0">
      ¿Otros datos? Este HTML lleva los resultados incrustados; para ver otra ejecución usa
      <input type="file" id="loadJson" accept=".json" style="display:inline-block;padding:3px 6px">.
    </p>
    <div class="note" style="background:#eef4fa;border-color:#cfe0f0;color:#1f4e79;margin-top:12px">
      <b>Esto no es asesoramiento financiero.</b> Son regularidades condicionales de una muestra
      concreta; no son predicciones ni recomendaciones de compra o venta.
    </div>
  </section>

  <div class="foot" id="foot"></div>
</main>

<script>const DATA = /*__DATA__*/;</script>
<script>
/* =====================================================================
   Utilidades
   ===================================================================== */
const NS = 'http://www.w3.org/2000/svg';
const $ = (s, r) => (r || document).querySelector(s);
const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));

const esN = (x, d) => {
  if (x === null || x === undefined || (typeof x === 'number' && isNaN(x))) return '—';
  return Number(x).toFixed(d === undefined ? 2 : d).replace('.', ',');
};
const miles = (x) => (x === null || x === undefined) ? '—'
  : Math.round(x).toLocaleString('es-ES');
const pct = (x, d) => esN(x * 100, d === undefined ? 2 : d) + ' %';
const signo = (x, d) => (x >= 0 ? '+' : '') + esN(x, d === undefined ? 2 : d);

function mk(tag, attrs, padre) {
  const e = document.createElementNS(NS, tag);
  for (const k in (attrs || {})) e.setAttribute(k, attrs[k]);
  if (padre) padre.appendChild(e);
  return e;
}
function txt(svg, x, y, s, o) {
  o = o || {};
  const t = mk('text', {
    x: x, y: y, 'font-size': o.size || 11,
    fill: o.fill || '#5b6b7f', 'text-anchor': o.anchor || 'start',
    'font-weight': o.weight || 400
  }, svg);
  if (o.rotate) t.setAttribute('transform', 'rotate(' + o.rotate + ' ' + x + ' ' + y + ')');
  t.textContent = s;
  return t;
}
function raiz(host, W, H) {
  host.innerHTML = '';
  const s = mk('svg', { viewBox: '0 0 ' + W + ' ' + H, width: '100%',
                        style: 'height:auto;display:block' }, host);
  return s;
}
const COLORES = ['#2e7ebf', '#e08b00', '#137a4b', '#b3261e', '#7d4bbf',
                 '#0f8b8d', '#c2410c', '#4a5568'];

/* =====================================================================
   Cabecera + KPIs
   ===================================================================== */
const B = DATA.base || {};
const M = DATA.meta || {};
const sig = DATA.significancia || [];
const mejoras = sig.filter(r => r.sig && r.delta_pp > 0).length;
const empeora = sig.filter(r => r.sig && r.delta_pp < 0).length;

$('#sub').innerHTML = [
  M.db ? '<b>Base:</b> <span class="mono">' + M.db + '</span>' : '',
  M.fecha_min ? '<b>Periodo:</b> ' + M.fecha_min + ' &rarr; ' + M.fecha_max : '',
  M.n_tickers ? '<b>Tickers:</b> ' + M.n_tickers : '',
  '<b>Generado:</b> ' + (M.generado || '')
].filter(Boolean).join(' &nbsp;&middot;&nbsp; ');

$('#kpis').innerHTML = [
  ['P(sube 21d)', pct(B.hit21), 'tasa base incondicional'],
  ['P(sube 63d)', pct(B.hit63), 'tasa base incondicional'],
  ['Observaciones', miles(B.n), 'retornos forward con datos'],
  ['Señales evaluadas', miles(sig.length), 'condiciones contrastadas'],
  ['Baten la base', miles(mejoras), 'significativas con exceso &gt; 0'],
  ['Pierden vs. base', miles(empeora), 'significativas con exceso &lt; 0']
].map(k => '<div class="kpi"><div class="v">' + k[1] + '</div><div class="l">' + k[0] +
           '</div><div class="s">' + k[2] + '</div></div>').join('');

/* =====================================================================
   Tabla de ranking
   ===================================================================== */
const NOMBRES = {
  volatility_level: 'Volatilidad 21d',
  volatility_compression: 'Compresión de volatilidad',
  dist_52w_high: 'Distancia al máximo 52s',
  new_52w_high_event: 'Eventos 52 semanas',
  breakout_20d: 'Breakout 20 días',
  trend_sma: 'Tendencia SMA',
  volume_ratio: 'Volumen relativo',
  market_regime: 'Régimen de mercado',
  composite_signal: 'Score compuesto',
  composite_by_period: 'Score compuesto (periodo)',
  extreme_down_events: 'Caídas extremas',
  short_term_reversal: 'Reversión 5 días',
  monthly_signals: 'Señales mensuales',
  seasonality: 'Estacionalidad',
  momentum_quintiles: 'Momentum'
};
const bonito = (s) => {
  if (NOMBRES[s]) return NOMBRES[s];
  const t = String(s).replace(/^(monthly_)/, '');
  if (NOMBRES[t]) return 'Mensual: ' + NOMBRES[t].toLowerCase();
  return t.replace(/_/g, ' ').replace(/^\w/, c => c.toUpperCase());
};
const HOR = { 5: '5d', 21: '21d', 63: '63d' };

let orden = { k: 'delta_pp', asc: false };
const selP = $('#fP');
Array.from(new Set(sig.map(r => r.patron))).sort().forEach(p => {
  const o = document.createElement('option');
  o.value = p; o.textContent = bonito(p); selP.appendChild(o);
});

function filasFiltradas() {
  const h = $('#fH').value, p = selP.value, soloSig = $('#fS').checked;
  const q = $('#fQ').value.trim().toLowerCase();
  let out = sig.filter(r =>
    (!h || String(r.h) === h) &&
    (!p || r.patron === p) &&
    (!soloSig || r.sig) &&
    (!q || (String(r.bucket) + ' ' + bonito(r.patron)).toLowerCase().includes(q)));
  out.sort((a, b) => {
    const va = a[orden.k], vb = b[orden.k];
    if (typeof va === 'string' || typeof vb === 'string') {
      const r = String(va).localeCompare(String(vb));
      return orden.asc ? r : -r;
    }
    return orden.asc ? (va - vb) : (vb - va);
  });
  return out;
}

function pintarTabla() {
  const maxAbs = Math.max(1, ...sig.map(r => Math.abs(r.delta_pp || 0)));
  const tbody = $('#tRank tbody');
  tbody.innerHTML = filasFiltradas().map(r => {
    const w = Math.abs(r.delta_pp || 0) / maxAbs * 100;
    const pos = (r.delta_pp || 0) >= 0;
    const pill = r.sig ? '<span class="pill ' + (pos ? 'pos' : 'neg') + '">' +
      (pos ? 'mejor' : 'peor') + '</span>' : '<span class="pill neu">n.s.</span>';
    return '<tr>' +
      '<td>' + bonito(r.patron) + '</td>' +
      '<td>' + String(r.bucket) + '</td>' +
      '<td class="num">' + (HOR[r.h] || r.h) + '</td>' +
      '<td class="num">' + miles(r.n) + '</td>' +
      '<td class="num"><b>' + pct(r.hit) + '</b></td>' +
      '<td class="num" style="color:#5b6b7f">' + esN(r.lo * 100, 1) + '–' + esN(r.hi * 100, 1) + '</td>' +
      '<td class="num">' + signo(r.delta_pp) + ' pp</td>' +
      '<td><div class="bar"><span style="left:' + (pos ? 50 : 50 - w / 2) + '%"></span>' +
        '<i class="' + (pos ? 'p' : 'n') + '" style="' +
        (pos ? 'left:50%;width:' + (w / 2) + '%' : 'right:50%;width:' + (w / 2) + '%') + '"></i></div></td>' +
      '<td>' + pill + '</td>' +
      '</tr>';
  }).join('') || '<tr><td colspan="9" style="color:#5b6b7f;padding:16px">Sin resultados con esos filtros.</td></tr>';
  $$('#tRank thead th').forEach(th => {
    th.textContent = th.textContent.replace(/ [▲▼]$/, '');
    if (th.dataset.k === orden.k) th.textContent += orden.asc ? ' ▲' : ' ▼';
  });
}
$$('#tRank thead th').forEach(th => th.addEventListener('click', () => {
  const k = th.dataset.k;
  orden = { k: k, asc: (orden.k === k) ? !orden.asc : false };
  pintarTabla();
}));
['#fH', '#fP', '#fS', '#fQ'].forEach(s => $(s).addEventListener('input', pintarTabla));
$('#btnCsv').addEventListener('click', () => {
  const filas = filasFiltradas();
  const cab = ['patron', 'bucket', 'horizonte_d', 'n', 'hit', 'ic95_lo', 'ic95_hi', 'delta_pp', 'p_valor', 'significativo'];
  const csv = [cab.join(',')].concat(filas.map(r => [
    bonito(r.patron), '"' + String(r.bucket).replace(/"/g, '""') + '"', r.h, r.n,
    r.hit, r.lo, r.hi, r.delta_pp, r.p, r.sig
  ].join(','))).join('\n');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
  a.download = 'ranking_senales_filtrado.csv';
  a.click();
});
pintarTabla();

/* =====================================================================
   Gráficos SVG
   ===================================================================== */
function lineas(host, series, base, ylab) {
  const W = 900, H = 380, mL = 64, mR = 216, mT = 20, mB = 44;
  const svg = raiz(host, W, H);
  const vals = [];
  series.forEach(s => s.pts.forEach(p => vals.push(p.y)));
  if (base !== null && base !== undefined) vals.push(base);
  let y0 = Math.min(...vals), y1 = Math.max(...vals);
  const pad = (y1 - y0) * 0.18 || 0.01;
  y0 -= pad; y1 += pad;
  const X = i => mL + (i - 1) * ((W - mL - mR) / 4);
  const Y = v => mT + (y1 - v) / (y1 - y0) * (H - mT - mB);
  let baseEtq = null;
  for (let g = 0; g <= 4; g++) {
    const v = y0 + (y1 - y0) * g / 4, y = Y(v);
    mk('line', { x1: mL, y1: y, x2: W - mR, y2: y, stroke: '#e8eef4', 'stroke-width': 1 }, svg);
    txt(svg, mL - 8, y + 4, pct(v, 1), { anchor: 'end', size: 10.5 });
  }
  txt(svg, mL - 56, 11, ylab, { size: 10.5, weight: 600, fill: '#1f4e79' });
  if (base !== null && base !== undefined) {
    mk('line', { x1: mL, y1: Y(base), x2: W - mR, y2: Y(base), stroke: '#16202c',
                 'stroke-width': 1.3, 'stroke-dasharray': '6 4' }, svg);
    baseEtq = 'tasa base ' + pct(base, 1);
  }
  series.forEach(s => {
    if (s.off) return;
    const d = s.pts.map((p, i) => (i ? 'L' : 'M') + X(p.x) + ' ' + Y(p.y)).join(' ');
    mk('path', { d: d, fill: 'none', stroke: s.color, 'stroke-width': 2.4,
                 'stroke-linejoin': 'round', 'stroke-opacity': .92 }, svg);
    s.pts.forEach(p => {
      const c = mk('circle', { cx: X(p.x), cy: Y(p.y), r: 4, fill: '#fff',
                               stroke: s.color, 'stroke-width': 2.2 }, svg);
      const t = mk('title', {}, svg);
      t.textContent = s.name + ' · quintil ' + p.x + ': ' + pct(p.y, 2);
      c.appendChild(t);
    });
  });
  // etiquetas a la derecha, separadas verticalmente para que no se solapen
  const etiquetas = series.filter(s => !s.off)
    .map(s => ({ nombre: s.name, color: s.color, y: Y(s.pts[s.pts.length - 1].y) }))
    .sort((a, b) => a.y - b.y);
  let previa = -1e9;
  etiquetas.forEach(e => { e.y = Math.max(e.y, previa + 13.5, mT + 8); previa = e.y; });
  const sobra = previa - (H - mB - 6);
  if (sobra > 0) etiquetas.forEach(e => { e.y -= sobra; });
  etiquetas.forEach(e => {
    const yd = Y(series.filter(s => s.name === e.nombre)[0].pts.slice(-1)[0].y);
    if (Math.abs(yd - e.y) > 2) {
      mk('line', { x1: W - mR - 4, y1: yd, x2: W - mR + 6, y2: e.y, stroke: '#dbe4ec' }, svg);
    }
    txt(svg, W - mR + 9, e.y + 4, e.nombre, { size: 11, fill: e.color, weight: 600 });
  });
  if (baseEtq !== null) {
    const ancho = baseEtq.length * 5.6 + 12;
    mk('rect', { x: mL + 3, y: Y(base) - 18, width: ancho, height: 16,
                 fill: '#fbfdff', stroke: '#dfe7ee', rx: 4 }, svg);
    txt(svg, mL + 9, Y(base) - 6, baseEtq, { size: 10.5, fill: '#16202c', weight: 600 });
  }
  for (let i = 1; i <= 5; i++) txt(svg, X(i), H - 17, 'Q' + i, { anchor: 'middle', size: 11 });
  txt(svg, (mL + W - mR) / 2, H - 3, 'Quintil de la señal (1 = más bajo, 5 = más alto)',
      { anchor: 'middle', size: 10.5 });
  return svg;
}

function barrasH(host, filas, base, unidad) {
  const n = filas.length;
  const W = 560, rowh = 46, H = n * rowh + 40, mL = 168, mR = 56, mT = 10;
  const svg = raiz(host, W, H);
  const maxAbs = Math.max(0.01, ...filas.map(f => Math.max(Math.abs(f.v1 || 0), Math.abs(f.v2 || 0))));
  const X = v => mL + (v + maxAbs * 1.05) / (maxAbs * 2.1) * (W - mL - mR);
  mk('line', { x1: X(0), y1: mT, x2: X(0), y2: H - 26, stroke: '#9aa8b8', 'stroke-width': 1.2 }, svg);
  filas.forEach((f, i) => {
    const y = mT + i * rowh + 6, hb = 13;
    const c1 = (f.v1 || 0) >= 0 ? '#2e7ebf' : '#b3261e';
    const c2 = (f.v2 || 0) >= 0 ? '#e08b00' : '#b3261e';
    if (f.v1 !== null && f.v1 !== undefined) {
      const x = Math.min(X(0), X(f.v1)), w = Math.abs(X(f.v1) - X(0));
      mk('rect', { x: x, y: y, width: Math.max(w, 1), height: hb, fill: c1, rx: 2 }, svg)
        .appendChild(mk('title', {}, svg)).textContent =
        f.label + ' · ' + (f.h1 || '21d') + ': ' + signo(f.v1) + ' pp';
      txt(svg, X(f.v1) + (f.v1 >= 0 ? 5 : -5), y + hb - 2, signo(f.v1, 1),
          { size: 10, anchor: f.v1 >= 0 ? 'start' : 'end', fill: c1 });
    }
    if (f.v2 !== null && f.v2 !== undefined) {
      const x = Math.min(X(0), X(f.v2)), w = Math.abs(X(f.v2) - X(0));
      mk('rect', { x: x, y: y + hb + 2, width: Math.max(w, 1), height: hb, fill: c2, rx: 2 }, svg)
        .appendChild(mk('title', {}, svg)).textContent =
        f.label + ' · ' + (f.h2 || '63d') + ': ' + signo(f.v2) + ' pp';
      txt(svg, X(f.v2) + (f.v2 >= 0 ? 5 : -5), y + 2 * hb, signo(f.v2, 1),
          { size: 10, anchor: f.v2 >= 0 ? 'start' : 'end', fill: c2 });
    }
    txt(svg, mL - 10, y + 14, f.label.length > 26 ? f.label.slice(0, 25) + '…' : f.label,
        { anchor: 'end', size: 10.5, fill: '#16202c' });
  });
  txt(svg, (mL + W - mR) / 2, H - 8, 'Exceso de P(sube) vs. tasa base, en puntos porcentuales',
      { anchor: 'middle', size: 10.5 });
  return svg;
}

function barrasV(host, filas) {
  const W = 560, H = 300, mL = 52, mR = 14, mT = 14, mB = 46;
  const svg = raiz(host, W, H);
  const vs = filas.map(f => f.v);
  const maxAbs = Math.max(0.01, ...vs.map(Math.abs));
  const Y = v => mT + (maxAbs - v) / (2 * maxAbs) * (H - mT - mB);
  const bw = (W - mL - mR) / filas.length;
  mk('line', { x1: mL, y1: Y(0), x2: W - mR, y2: Y(0), stroke: '#9aa8b8' }, svg);
  [-maxAbs, 0, maxAbs].forEach(v => txt(svg, mL - 8, Y(v) + 4, pct(v, 1),
    { anchor: 'end', size: 10.5 }));
  filas.forEach((f, i) => {
    const x = mL + i * bw + bw * 0.16, w = bw * 0.68;
    const y = Math.min(Y(0), Y(f.v)), h = Math.abs(Y(f.v) - Y(0));
    mk('rect', { x: x, y: y, width: w, height: Math.max(h, 1),
                 fill: f.v >= 0 ? '#137a4b' : '#b3261e', rx: 2 }, svg)
      .appendChild(mk('title', {}, svg)).textContent =
      f.label + ': ret. medio ' + signo(f.v) + ' %, P(sube) ' + pct(f.hit) + ' (n=' + miles(f.n) + ')';
    txt(svg, x + w / 2, H - 27, f.label, { anchor: 'middle', size: 10.5 });
    txt(svg, x + w / 2, Y(f.v) + (f.v >= 0 ? -6 : 13), (f.v >= 0 ? '+' : '') + esN(f.v * 100, 1) + ' %',
        { anchor: 'middle', size: 10, fill: f.v >= 0 ? '#137a4b' : '#b3261e', weight: 600 });
  });
  return svg;
}

/* ---- 1) Probabilidad por quintil + leyenda interactiva ---- */
const qH = $('#qH'), seriesQ = [];
(function initQ() {
  const orden = ['dist_52w_high', 'volatility_level', 'volume_ratio',
                 'composite_signal', 'volatility_compression', 'short_term_reversal'];
  Object.keys(DATA.quintiles).sort((a, b) => orden.indexOf(a) - orden.indexOf(b))
    .forEach((k, i) => {
      const filas = DATA.quintiles[k];
      if (!filas || !filas.length || !('q' in filas[0])) return;
      if (!('hit21' in filas[0]) && !('hit63' in filas[0]) && !('hit5' in filas[0])) return;
      seriesQ.push({ key: k, color: COLORES[i % COLORES.length], off: false });
    });
  const cont = $('#qLegend');
  cont.innerHTML = seriesQ.map(s =>
    '<span data-k="' + s.key + '"><i class="dot" style="background:' + s.color + '"></i>' +
    bonito(s.key) + '</span>').join('');
  $$('#qLegend span').forEach(sp => sp.addEventListener('click', () => {
    const s = seriesQ.filter(x => x.key === sp.dataset.k)[0];
    s.off = !s.off; sp.classList.toggle('off', s.off); pintarQ();
  }));
})();

function pintarQ() {
  const h = qH.value;                        // p.ej. hit21
  const horizonte = parseInt(h.replace('hit', ''), 10);
  const titulo = $('#qTitle');
  titulo.textContent = 'P(sube en ' + horizonte + ' días) por quintil de la señal';
  const series = [];
  seriesQ.forEach(s => {
    const filas = DATA.quintiles[s.key];
    if (!filas || !filas.length || !(h in filas[0])) return;
    series.push({
      name: bonito(s.key), color: s.color, off: s.off,
      pts: filas.map(r => ({ x: Number(r.q), y: r[h] }))
    });
  });
  const base = horizonte === 21 ? B.hit21 : (horizonte === 63 ? B.hit63 : B.hit5d);
  if (!series.length) {
    $('#qChart').innerHTML = '<p style="color:#5b6b7f;padding:20px">' +
      'Ninguna señal tiene datos para ese horizonte.</p>';
    return;
  }
  lineas($('#qChart'), series, base, 'P(sube)');
}
qH.addEventListener('change', pintarQ);
pintarQ();

/* ---- 2) Eventos discretos ---- */
function delta(filas, hk, hbase) {
  return filas.map(r => ({
    label: r.estado,
    v: (r[hk] - hbase) * 100,
    h1: '21d', h2: '63d'
  }));
}
if (DATA.extremos && DATA.extremos.length) {
  const filas = DATA.extremos.filter(r => r.estado !== 'resto').map(r => ({
    label: r.estado,
    v1: (r.hit21 - B.hit21) * 100,
    v2: (r.hit63 - B.hit63) * 100
  }));
  barrasH($('#cEventos'), filas);
}
if (DATA.trend && DATA.trend.length) {
  barrasH($('#cTrend'), DATA.trend.map(r => ({
    label: r.estado, v1: (r.hit21 - B.hit21) * 100, v2: (r.hit63 - B.hit63) * 100
  })));
}
if (DATA.eventos && DATA.eventos.length) {
  barrasH($('#c52w'), DATA.eventos.map(r => ({
    label: r.estado, v1: (r.hit21 - B.hit21) * 100, v2: (r.hit63 - B.hit63) * 100
  })));
}
if (DATA.breakout && DATA.breakout.length) {
  barrasH($('#cBreak'), DATA.breakout.map(r => ({
    label: r.estado, v1: (r.hit21 - B.hit21) * 100, v2: (r.hit63 - B.hit63) * 100
  })));
}

/* ---- 3) Momentum ---- */
(function momentum() {
  const mq = DATA.momentum_quintiles || {};
  const claves = Object.keys(mq);
  const series = claves.map((k, i) => ({
    name: k.replace('mom_', '').replace('_', '-'), color: COLORES[i % COLORES.length],
    pts: (mq[k] || []).map(r => ({ x: Number(r.q), y: r.hit }))
  }));
  if (series.length) lineas($('#cMomQ'), series, B.hit21, 'P(sube 1 mes)');
  $('#lMomQ').innerHTML = series.map(s =>
    '<span><i class="dot" style="background:' + s.color + '"></i>' + s.name + '</span>').join('');

  const ls = DATA.momentum_ls || [], ic = DATA.momentum_ic || [];
  $('#tMom tbody').innerHTML = claves.map(k => {
    const a = ls.filter(r => r['señal'] === k)[0] || {};
    const b = ic.filter(r => r['señal'] === k)[0] || {};
    return '<tr><td><b>' + k + '</b></td>' +
      '<td class="num">' + miles(a.meses) + '</td>' +
      '<td class="num">' + (a.ret_medio_ls_mensual === undefined ? '—' :
        signo(a.ret_medio_ls_mensual * 100) + ' %') + '</td>' +
      '<td class="num" style="color:' + ((a.sharpe_ls_anualizado || 0) >= 0 ? '#137a4b' : '#b3261e') +
        '"><b>' + esN(a.sharpe_ls_anualizado) + '</b></td>' +
      '<td class="num">' + pct(a.hit_ls, 1) + '</td>' +
      '<td class="num">' + esN(b.ic_medio, 4) + '</td>' +
      '<td class="num">' + esN(b.ic_ir_anualizado) + '</td>' +
      '<td class="num">' + pct(b.ic_hit, 1) + '</td></tr>';
  }).join('');
  if (claves.length) {
    const filas = claves.map(k => ({
      label: k,
      v: (ls.filter(r => r['señal'] === k)[0] || {}).sharpe_ls_anualizado || 0
    }));
    const W = 520, H = filas.length * 34 + 46, mL = 90, mR = 40, mT = 12, mB = 26;
    const svg = raiz($('#cMomLS'), W, H);
    const maxAbs = Math.max(0.2, ...filas.map(f => Math.abs(f.v)));
    const X = v => mL + (v + maxAbs) / (2 * maxAbs) * (W - mL - mR);
    mk('line', { x1: X(0), y1: mT, x2: X(0), y2: H - mB, stroke: '#9aa8b8' }, svg);
    filas.forEach((f, i) => {
      const y = mT + i * 34, x = Math.min(X(0), X(f.v)), w = Math.abs(X(f.v) - X(0));
      mk('rect', { x: x, y: y + 6, width: Math.max(w, 1), height: 16,
                   fill: f.v >= 0 ? '#137a4b' : '#b3261e', rx: 2 }, svg)
        .appendChild(mk('title', {}, svg)).textContent =
        f.label + ': Sharpe L/S ' + esN(f.v) + ' (Q5−Q1, mensual)';
      txt(svg, mL - 8, y + 18, f.label, { anchor: 'end', size: 11, fill: '#16202c' });
      txt(svg, X(f.v) + (f.v >= 0 ? 5 : -5), y + 18, esN(f.v),
          { size: 10.5, anchor: f.v >= 0 ? 'start' : 'end' });
    });
    txt(svg, (mL + W - mR) / 2, H - 8,
        'Sharpe anualizado del portfolio long-short Q5−Q1 (mensual)', { anchor: 'middle' });
  }
})();

/* ---- 4) Estacionalidad y regímenes ---- */
(function estacionalidad() {
  const S = DATA.seasonality || [];
  if (!S.length) return;
  const MES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
  barrasV($('#cSeason'), S.map(r => ({
    label: MES[Number(r.mes_natural) - 1], v: r.ret_medio, hit: r.hit, n: r.n
  })));
})();
(function regimenes() {
  const R = DATA.regime || [];
  if (!R.length) return;
  const filas = R.map(r => ({
    label: r.estado, v1: (r.hit21 - B.hit21) * 100, v2: (r.hit63 - B.hit63) * 100
  }));
  barrasH($('#cRegime'), filas);
})();

/* ---- 5) Cargar otro resumen.json (opcional) ---- */
$('#loadJson').addEventListener('change', (ev) => {
  const f = ev.target.files[0];
  if (!f) return;
  const rd = new FileReader();
  rd.onload = () => {
    try {
      const nuevo = JSON.parse(rd.result);
      alert('Cargado ' + f.name + ' (' + Object.keys(nuevo.queries || {}).length +
            ' consultas).\n\nNota: este archivo aporta las tablas de patrones; ' +
            'las probabilidades condicionales y los gráficos usan el conjunto incrustado. ' +
            'Para un dashboard completo, vuelve a ejecutar make_dashboard.py con el JSON nuevo.');
    } catch (e) {
      alert('No se pudo leer el JSON: ' + e.message);
    }
  };
  rd.readAsText(f);
});

$('#foot').textContent = 'Generado por make_dashboard.py · ' + (M.generado || '') +
  ' · Análisis estadístico de patrones históricos: no es asesoramiento financiero.';
</script>
</body>
</html>
"""


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default=os.path.join(here, "resultados"))
    ap.add_argument("--db", default=None, help="base DuckDB para metadatos (opcional)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    pj = os.path.join(args.res, "resumen.json")
    pc = os.path.join(args.res, "significancia_vs_base.csv")
    if not os.path.exists(pj):
        raise SystemExit(f"No encuentro {pj}. Ejecuta antes run_analysis.py.")

    data = cargar_resumen(pj, pc)
    if args.db:
        data["meta"].update(meta_desde_db(args.db))
    elif data["meta"].get("db"):
        data["meta"].update(meta_desde_db(data["meta"]["db"]))

    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = HTML.replace("/*__DATA__*/", payload)

    out = args.out or os.path.join(args.res, "dashboard.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"[ok] dashboard -> {out} ({os.path.getsize(out)/1024:.0f} KB, "
          f"{len(data['significancia'])} filas de ranking, "
          f"{len(data['quintiles'])} señales por quintil)")


if __name__ == "__main__":
    main()
