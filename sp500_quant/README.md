# sp500_quant — Suite de análisis de patrones sobre `sp500.duckdb`

Conjunto de scripts y SQL (DuckDB) para **descubrir y medir patrones
estadísticos** en precios diarios del S&P 500: momentum, reversión, volatilidad,
máximos de 52 semanas, breakouts, medias móviles, volumen, co-movimientos,
regímenes y señales compuestas — todo con métricas de probabilidad condicional,
hit ratio, IC/IR y Sharpe.

> ⚠️ **No es asesoramiento financiero.** Es análisis estadístico descriptivo de
> patrones históricos.

---

## 0. Windows: instalación en 4 pasos (sin saber programar)

**1. Descarga la carpeta.** Elige una opción:

| Opción | Cómo |
|---|---|
| **ZIP (más fácil)** | Descarga `sp500_quant_windows.zip`, clic derecho → *Extraer todo* → por ejemplo en `C:\sp500_quant` |
| **Si ya tienes el repo clonado** | `git fetch origin` y luego `git checkout origin/arena/01a105cf-data-analysis -- sp500_quant` |
| **Archivos sueltos** | Descarga cada archivo desde GitHub: `https://raw.githubusercontent.com/pablodpt/Data-Analysis/arena/01a105cf-data-analysis/sp500_quant/INSTALAR.bat` (y lo mismo con `ANALIZAR.bat`, `run_analysis.py`, `significancia.py`, `make_figures.py`, `sql/patrones.sql`) |

> **Importante:** extrae el ZIP **antes** de usar los `.bat`. Si los ejecutas
> desde dentro del ZIP, Windows no los ejecutará bien.

**2. Doble clic en `INSTALAR.bat`.** Una sola vez. Hace todo esto solo:

* comprueba si tienes Python (si no lo tienes, te da el comando `winget` exacto);
* crea un entorno virtual aislado en `.venv\` (no toca tu Python del sistema);
* instala `duckdb`, `pandas`, `numpy`, `scipy` y `matplotlib`;
* verifica que todo importa correctamente.

**3. Doble clic en `ANALIZAR.bat`.** Te pedirá la ruta de tu base. Puedes:

* escribir la ruta completa, o
* **arrastrar el archivo `.duckdb` encima de `ANALIZAR.bat`**, o
* escribir `demo` para que descargue y construya una base de ejemplo.

La ruta se guarda en `db_path.txt`, así que las siguientes veces solo tienes que
hacer doble clic. Al terminar se abre automáticamente la carpeta `resultados\`.

**4. Mira los resultados** en `resultados\`:

* `significancia_vs_base.csv` → las probabilidades condicionales y su significancia;
* un CSV por patrón;
* `figuras\patrones_sp500.png`.

> **Cierra antes DBeaver / DuckDB CLI / cualquier programa que tenga la base
> abierta**, o Windows bloqueará la lectura del archivo.
> Los scripts abren la base con `read_only=True`: **nunca escriben en tu base**.

---

## 1. Ejecutar sobre TU base (a mano, si prefieres la terminal)

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
python build_replica.py            # descarga datos publicos y crea data/sp500_replica.duckdb
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
