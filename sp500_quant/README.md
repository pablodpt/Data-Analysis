# sp500_quant — Suite de análisis de patrones sobre `sp500.duckdb`

Conjunto de scripts y SQL (DuckDB) para **descubrir y medir patrones
estadísticos** en precios diarios del S&P 500: momentum, reversión, volatilidad,
máximos de 52 semanas, breakouts, medias móviles, volumen, co-movimientos,
regímenes y señales compuestas — todo con métricas de probabilidad condicional,
hit ratio, IC/IR y Sharpe.

> ⚠️ **No es asesoramiento financiero.** Es análisis estadístico descriptivo de
> patrones históricos.

---

## 1. Ejecutar sobre TU base (recomendado)

Tu base está en `C:\Users\pablo\Documents\sp500_db\db\sp500.duckdb`.
Los scripts abren la conexión en **modo `read_only=True`**: no escriben nada.

```bash
pip install duckdb pandas numpy scipy matplotlib

# Windows (PowerShell), dentro de esta carpeta:
python run_analysis.py --db "C:\Users\pablo\Documents\sp500_db\db\sp500.duckdb"
python significancia.py
python make_figures.py
```

Resultados en `resultados/` (CSV por patrón + `resumen.json` +
`significancia_vs_base.csv` + figuras).

Si tu base es la fuente de verdad y quieres que **recalcule el informe completo
con tus datos** (2015-2026), exporta y comparte, por ejemplo:

```sql
COPY (SELECT * FROM prices)  TO 'prices.parquet' (FORMAT PARQUET);
COPY (SELECT * FROM tickers) TO 'tickers.parquet' (FORMAT PARQUET);
```

…o adjunta directamente el `.duckdb` (~decenas de MB).

---

## 2. Construir la réplica local (si no tienes la base a mano)

```bash
python build_replica.py            # descarga datos públicos y crea data/sp500_replica.duckdb
```

Fuente: `plotly/datasets :: all_stocks_5yr.csv` (505 tickers, 2013-02-08 →
2018-02-07) + sectores GICS de `datasets/s-and-p-500-companies`.

Crea las **21 tablas y vistas** del esquema original:

* Tablas: `prices`, `tickers`, `dividends`, `splits`, `fundamentals`, `news`,
  `filings`, `filings_annual`, `pca_loadings`, `pca_scores`, `signals`,
  `selected_15_tickers`, `weights_inv_variance`, `weights_max_sharpe`, `update_log`
* Vistas: `base_diaria`, `v_precios_mensuales`, `v_precios_semanales`,
  `v_momentum_12_1`, `v_momentum_sector_neutral`, `v_universo_liquido`

`pca_*` y `weights_*` se **calculan de verdad** (SVD sobre retornos, covarianza
1 año). `fundamentals`, `news`, `filings*`, `dividends`, `splits`, `signals` y
`selected_15_tickers` quedan **vacías con el esquema correcto** (no hay fuente
pública equivalente en el entorno).

---

## 3. Contenido

| Archivo | Qué hace |
|---|---|
| `sql/patrones.sql` | **Toda la librería SQL**, comentada y validada (17 bloques). Pegable en tu cliente DuckDB. |
| `run_analysis.py` | Ejecuta la suite completa y calcula hit ratios + IC Wilson, t-stats, Sharpe, IC de Spearman e IR de portfolios L/S. |
| `significancia.py` | Contrasta cada probabilidad condicional contra la tasa base (z-test + IC95 % de Wilson). |
| `make_figures.py` | Figura resumen de 4 paneles. |
| `build_replica.py` | Construye la réplica con el esquema idéntico. |
| `RESULTADOS.md` | **Informe**: SQL, resultados, interpretación, probabilidades y limitaciones. |

### Consultas incluidas

`momentum_quintiles` (1m/3m/6m/12m/12-1) · `momentum_ic` · `monthly_signals`
(versión no solapada) · `short_term_reversal` · `autocorrelation` ·
`volatility_level` · `volatility_compression` · `dist_52w_high` ·
`new_52w_high_event` · `breakout_20d` · `trend_sma` · `volume_ratio` ·
`market_regime` · `extreme_down_events` · `composite_signal` ·
`composite_by_period` · `seasonality`

---

## 4. Convenciones metodológicas

* **Sin look-ahead**: toda señal en `t` usa datos ≤ `t`; los retornos forward se
  calculan con `LEAD(px, h) / px − 1`.
* **Precio**: `COALESCE(adj_close, close)` → en tu base usará el ajustado real.
* **Bucketización**: `NTILE(5)` cross-sectional por fecha (o por mes en las
  versiones no solapadas).
* **Comparación clave**: toda probabilidad condicional se contrasta contra la
  **tasa base incondicional** del mismo periodo/horizonte.
* **Caveat estadístico**: los horizontes de 21/63 días sobre datos diarios
  **solapan**; los t-stats están inflados ~√h. Las conclusiones robustas salen de
  las versiones mensuales no solapadas.

---

## 5. Advertencias

1. La réplica cubre **2013-2018**, una muestra alcista: las probabilidades de
   subida son altas en términos absolutos (57,99 % a 21d; 63,30 % a 63d) y hay
   que leerlas siempre como *exceso sobre la base*.
2. Los 505 tickers son **supervivientes** → sesgo al alza.
3. En la réplica `adj_close = close` (el dataset público no trae ajuste real).
4. Sin `fundamentals`/`news` no se puede testear *value*, *quality* ni
   sentimiento.
5. Nada de esto es una recomendación de compra o venta.
