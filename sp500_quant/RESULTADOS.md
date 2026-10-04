# Patrones estadísticos con valor predictivo en precios diarios del S&P 500

**Informe cuantitativo — análisis de patrones, no asesoramiento financiero.**

> **Nota de honestidad sobre los datos (léela primero).** Tu base vive en
> `C:\Users\pablo\Documents\sp500_db\db\sp500.duckdb`, en tu equipo; este agente
> no tiene acceso a esa ruta. Para poder **ejecutar y validar** todo el SQL antes
> de entregártelo, construí una **réplica local con el mismo esquema** (21 tablas
> y vistas idénticas) a partir de datos públicos reales de S&P 500
> (`plotly/datasets :: all_stocks_5yr.csv`, 505 tickers, **2013-02-08 → 2018-02-07**,
> 619.040 filas; sectores GICS de `datasets/s-and-p-500-companies`).
> Los números de este informe son, por tanto, de **ese periodo**, no de tu ventana
> 2015-2026. El SQL es 100 % portable: al ejecutarlo en tu base saldrán *tus*
> cifras (y probablemente distintas). Ver *Limitaciones*.

---

## 1. Resumen ejecutivo

Sobre 587.244 observaciones (505 tickers, diario, 2013-2018), la **tasa base
incondicional** fue:

| Horizonte | P(sube) | Retorno medio |
|---|---|---|
| 5 días | 54,33 % | — |
| 21 días (~1 mes) | **57,99 %** | +1,11 % |
| 63 días (~3 meses) | **63,30 %** | +3,38 % |

En una muestra alcista la mayoría de patrones “parecen” buenos simplemente
porque todo sube. La pregunta correcta es: **¿qué patrones baten su tasa base?**

### Lo que SÍ bate la tasa base (estadísticamente significativo, α=5 %)

| Patrón | Condición | P(sube 21d) | Δ vs base | P(sube 63d) | Δ vs base |
|---|---|---|---|---|---|
| Tendencia | Precio **bajo SMA200** | 63,10 % | **+5,1 pp** | 66,63 % | +3,3 pp |
| Sobre-reacción | Caída ≥10 % en 5 días | 59,79 % | +1,8 pp | **66,68 %** | +3,4 pp |
| Sobre-reacción | Día ≤ −2,5 σ | 60,79 % | +2,8 pp | 65,57 % | +2,3 pp |
| Sobre-reacción | Día −2 a −2,5 σ | 60,41 % | +2,4 pp | 65,97 % | +2,7 pp |
| Anclaje 52s | Precio a <3,5 % del máximo 52s (Q4) | 59,46 % | +1,5 pp | 65,27 % | +2,0 pp |
| Anclaje 52s | Máximo de 52 semanas cercano (Q5) | 59,08 % | +1,1 pp | 65,33 % | +2,0 pp |
| Volatilidad | Vol 21d en Q1-Q2 (baja) | 59,26-59,70 % | +1,3/+1,7 pp | — | — |
| Compresión vol | vol21/vol252 en Q2 | — | — | 64,69 % | +1,4 pp |
| Tendencia suave | Sobre SMA200 pero sin apilar | 59,60 % | +1,6 pp | 64,46 % | +1,2 pp |

### Lo que NO funciona en esta muestra (y por qué importa)

| Patrón | Resultado | Lectura |
|---|---|---|
| **Momentum 1 mes** | L/S Sharpe **−0,46**; IC −0,024 | Es **reversión**, no momentum |
| **Breakouts de 20 días** | P(sube 21d) 55,6-56,5 % (−1,5 a −2,0 pp) | Comprar rupturas *empeoró* la probabilidad |
| **Nuevo máximo de 52 semanas** | 56,65 % (−1,3 pp) a 21d | Elevada probabilidad de continuación solo a 63d (+1,2 pp) |
| **Volumen alto** (Q5 de vol/avg20) | 57,86 % (ns) | Sin ventaja; el volumen bajo fue mejor |
| **Score compuesto** (Q5) | 57,28 % (−0,7 pp) | Bate en *magnitud* (63d: +3,36 % vs +2,49 %) pero **no** en probabilidad |
| **Momentum 6m/12m** | Sharpe 0,41 / 0,09 / 0,32 (L/S) | Positivo pero **no significativo** (t≈0,9) |

### El hallazgo central

En esta muestra el **exceso de probabilidad** no viene de “seguir la fuerza”,
sino de **comprar debilidad/sobre-reacción** (caídas extremas, precio bajo SMA200)
y de **comprar calidad/estabilidad** (baja volatilidad, proximidad al máximo de
52 semanas). Es coherente con la literatura de *short-term reversal* y *low-vol
anomaly*, pero contradice el “momentum/breakout” de libro en este periodo concreto.

---

## 2. Cómo se generó (metodología)

* **Panel de features** (una sola CTE, sólo `prices` + `tickers`):
  retornos 5d/1m/3m/6m/12m, volatilidad 21d y 252d anualizada, máximo/mínimo 52
  semanas, máximo de 20 días *previo*, volumen medio 20d, SMA50/SMA200 y retornos
  forward 5/21/63 días con `LEAD(px, h)/px − 1` (**sin look-ahead**).
* **Precio**: `COALESCE(adj_close, close)` — en tu base usará el ajustado real.
* **Bucketing**: `NTILE(5)` cross-sectional **por fecha** (o por mes en las
  versiones mensuales no solapadas).
* **Métricas**: P(sube) con IC95 % de Wilson, Δ vs tasa base con z-test de
  proporciones, t-stat de medias, Sharpe anualizado de cada quintil, IC de
  Spearman mensual e Information Ratio del portfolio L/S (Q5−Q1) con rebalanceo
  mensual **no solapado**.
* **PCA** (PC1..PC10) sobre retornos diarios estandarizados vía SVD.

SQL completo y comentado, listo para copiar y pegar: **`sql/patrones.sql`**
(17 bloques, 5 variantes de momentum). Todos los bloques fueron ejecutados
contra la réplica antes de entregarse.

Ejemplo del patrón base (idéntico en todas las consultas):

```sql
WITH d AS (
    SELECT p.symbol, p.date, COALESCE(p.adj_close, p.close) AS px,
           p.high, p.volume, t.sector
    FROM prices p LEFT JOIN tickers t ON t.symbol = p.symbol
),
r AS (
    SELECT *,
           CASE WHEN LAG(px) OVER (PARTITION BY symbol ORDER BY date) > 0
                THEN px / LAG(px) OVER (PARTITION BY symbol ORDER BY date) - 1 END AS ret
    FROM d
),
f AS (
    SELECT *,
        px / NULLIF(LAG(px, 21)  OVER (PARTITION BY symbol ORDER BY date), 0) - 1 AS r_1m,
        STDDEV_SAMP(ret) OVER (PARTITION BY symbol ORDER BY date
                               ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) * SQRT(252) AS vol_21,
        LEAD(px, 21) OVER (PARTITION BY symbol ORDER BY date) / px - 1 AS fwd_21
    FROM r
)
SELECT ... FROM f;
```

---

## 3. Patrones analizados

### 3.1 Momentum (1m, 3m, 6m, 12m y 12-1)

**SQL** (versión canónica; `{MOM}` ∈ `mom_1m, mom_3m, mom_6m, mom_12m, mom_12_1`):

```sql
WITH m AS (
    SELECT symbol, mes, close,
           LAG(close, 1) OVER w AS c_1, LAG(close, 3) OVER w AS c_3,
           LAG(close, 6) OVER w AS c_6, LAG(close, 12) OVER w AS c_12,
           LEAD(close, 1) OVER w AS c_next
    FROM v_precios_mensuales WINDOW w AS (PARTITION BY symbol ORDER BY mes)
),
s AS (
    SELECT mes, c_next / close - 1 AS fwd_1m,
           close / NULLIF(c_1,0) - 1 AS mom_1m,
           close / NULLIF(c_3,0) - 1 AS mom_3m,
           close / NULLIF(c_6,0) - 1 AS mom_6m,
           close / NULLIF(c_12,0) - 1 AS mom_12m,
           c_1   / NULLIF(c_12,0) - 1 AS mom_12_1
    FROM m
),
b AS (
    SELECT mes, fwd_1m,
           NTILE(5) OVER (PARTITION BY mes ORDER BY mom_12_1) AS q
    FROM s WHERE mom_12_1 IS NOT NULL AND fwd_1m IS NOT NULL
)
SELECT q, COUNT(*) n, AVG(fwd_1m) mean_fwd,
       AVG(CASE WHEN fwd_1m > 0 THEN 1.0 ELSE 0 END) hit
FROM b GROUP BY q ORDER BY q;
```

**Resultado** (rebalanceo mensual, no solapado, 48–59 meses):

| Señal | Q1 media | Q5 media | Spread Q5−Q1 | Sharpe L/S anual. | Hit L/S | IC medio | IC-IR |
|---|---|---|---|---|---|---|---|
| mom_1m | +1,18 % | +0,85 % | **−0,33 %** | **−0,46** | 49,2 % | −0,0240 | −0,57 |
| mom_3m | +1,06 % | +1,13 % | +0,07 % | 0,08 | 49,1 % | +0,0054 | 0,11 |
| mom_6m | +0,90 % | +1,32 % | **+0,42 %** | **0,41** | 55,6 % | +0,0185 | 0,32 |
| mom_12m | +0,78 % | +0,89 % | +0,11 % | 0,09 | 56,3 % | +0,0078 | 0,12 |
| mom_12_1 | +0,71 % | +1,08 % | **+0,36 %** | **0,32** | 54,2 % | +0,0129 | 0,21 |

**Insight cuantitativo.** El eje temporal importa radicalmente: a **1 mes domina
la reversión** (el quintil ganador rinde *menos* que el perdedor y el IC es
negativo), mientras que a 6-12 meses aparece momentum débil y positivo. Los
Sharpe L/S (0,3-0,4) **no son significativos**: con ~4,5 años, t ≈ Sharpe·√años
≈ 0,9. El IC medio es del orden de 0,01-0,02, es decir, ~1-2 % de correlación
de rangos: mucha dispersión, poca señal.

**Probabilidad condicional.** P(sube 1m | quintil 5 de mom_12_1) = **55,95 %** vs
P(sube 1m | quintil 1) = 53,54 % → **+2,4 pp**. Para mom_6m: Q5 = 57,66 % vs
Q1 = 54,74 % (**+2,9 pp**). Nótese que ambas están **por debajo** de la tasa base
del 57,99 % para horizontes de 21 días, porque aquí el forward es exactamente 1
mes de calendario.

**Limitaciones.** (i) Momentum de **large caps** en una muestra alcista; (ii) el
universo son 505 supervivientes → sesgo de supervivencia; (iii) el spread no
sobrevive a costes de transacción realistas (rotación mensual de ~100 %);
(iv) `adj_close` ausente en la réplica.

**Patrones similares.** Momentum sector-neutral (`v_momentum_sector_neutral`),
“momentum + proximidad a máximo de 52 semanas” (doble filtro), momentum de
volatilidad (cambio en vol 21d), y *time-series momentum* del índice.

---

### 3.2 Reversión a la media y autocorrelación

**SQL** (reversión de 5 días — fragmento):

```sql
, b AS (
    SELECT date, r_5d, fwd_5d, fwd_21,
           NTILE(5) OVER (PARTITION BY date ORDER BY r_5d) AS q
    FROM f
    WHERE r_5d IS NOT NULL AND fwd_5d IS NOT NULL AND fwd_21 IS NOT NULL
)
SELECT q, COUNT(*) n, AVG(fwd_5d) mean_fwd5, AVG(fwd_21) mean_fwd21,
       AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) hit21
FROM b GROUP BY q ORDER BY q;
```

**Resultado** (retorno de los últimos 5 días → forward):

| Quintil r_5d | fwd 5d | fwd 21d | P(sube 21d) | corr(r_5d, fwd_5d) |
|---|---|---|---|---|
| Q1 (peor) | +0,34 % | **+1,33 %** | 57,85 % | −0,053 |
| Q2 | +0,33 % | +1,26 % | 58,98 % | −0,068 |
| Q3 | +0,29 % | +1,18 % | 58,97 % | −0,052 |
| Q4 | +0,26 % | +1,14 % | 58,85 % | −0,029 |
| Q5 (mejor) | +0,23 % | +1,03 % | 57,17 % | −0,006 |

**Autocorrelación por ticker (496 símbolos):**

| Métrica | Media | Mediana | % negativo |
|---|---|---|---|
| AC(1) diaria | −0,0106 | −0,0098 | 61,3 % |
| AC(5) diaria | −0,0104 | — | — |
| **AC(1) mensual** | **−0,0984** | −0,1005 | **78,0 %** |

**Insight.** La reversión es **poco intensa pero sistemática**: 61 % de los
tickers tienen autocorrelación diaria negativa y 78 % mensual negativa (media
−0,10). Econométricamente, un AC(1) mensual de −0,10 implica que ~10 % del
retorno del mes previsto se revierte dentro de la sección de rangos. El spread
de quintiles (Q1 vs Q5) es de +0,30 pp a 5 días y +0,30 pp a 21 días, con
orden casi monótono: señal débil pero coherente.

**Probabilidad condicional.** P(sube 21d | peor quintil 5d) = **57,85 %** vs
57,17 % para el mejor quintil → **+0,7 pp**. El efecto está en la *magnitud*, no
en la probabilidad: el quintil perdedor tiene media más alta con probabilidad
similar. La reversión paga por asimetría, no por acierto.

**Limitaciones.** (i) Autocorrelación agregada puede deberse a
`bid-ask bounce` y no ser explotable; (ii) efecto más fuerte en microcaps, ausente
aquí; (iii) el forward diario solapa 21 días → t-stats inflados.

**Patrones similares.** Contrario de RSI(2) < 10, caída de 3 días consecutivos,
desviación >2σ respecto a SMA20, y reversión condicionada por régimen
(solo funciona en vol alta).

---

### 3.3 Volatilidad y compresión de volatilidad

**SQL** (nivel; la compresión usa `vol_21/vol_252` análogamente):

```sql
, b AS (
    SELECT date, vol_21, fwd_21, fwd_63,
           NTILE(5) OVER (PARTITION BY date ORDER BY vol_21) AS q
    FROM f WHERE vol_21 IS NOT NULL AND fwd_21 IS NOT NULL
)
SELECT q, COUNT(*) n, AVG(vol_21) vol_media,
       AVG(fwd_21) mean_fwd21, AVG(fwd_63) mean_fwd63,
       AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) hit21
FROM b GROUP BY q ORDER BY q;
```

**Resultado — nivel de volatilidad (21d anualizada):**

| Quintil | vol media | fwd 21d | fwd 63d | P(sube 21d) | Sharpe(fwd21) |
|---|---|---|---|---|---|
| Q1 (baja) | 13,0 % | +0,93 % | +2,96 % | **59,26 %** | **0,183** |
| Q2 | 16,9 % | +1,18 % | +3,30 % | **59,70 %** | 0,207 |
| Q3 | 20,2 % | +1,18 % | +3,28 % | 58,39 % | 0,185 |
| Q4 | 24,7 % | +1,12 % | +3,25 % | 56,90 % | 0,152 |
| Q5 (alta) | 38,2 % | +1,16 % | **+4,08 %** | 55,51 % | 0,123 |

**Resultado — compresión (`vol_21/vol_252`):**

| Quintil | ratio | fwd 63d | P(sube 63d) |
|---|---|---|---|
| Q1 (compresión fuerte) | 0,65 | +3,50 % | 63,71 % |
| **Q2** | 0,81 | **+3,68 %** | **64,69 %** |
| Q3 | 0,91 | +3,37 % | 63,70 % |
| Q4 | 1,04 | +3,09 % | 62,39 % |
| Q5 (expansión) | 1,33 | +3,23 % | 61,79 % |

**Insight.** Hay dos efectos distintos y conviene no confundirlos:
1. **Probabilidad**: decrece monótonamente con la volatilidad (59,7 % → 55,5 %
   a 21d, −4,2 pp). La volatilidad alta ensancha la distribución en ambas colas.
2. **Magnitud**: el quintil de vol alta tiene el mayor retorno medio a 63d
   (+4,08 %), pero a costa de mucha más dispersión → su Sharpe es el peor (0,123).

La compresión extrema (Q1) **no** es el mejor bucket: el óptimo está en Q2
(ratio ≈0,8), con +1,4 pp de P(sube 63d). La “compresión → expansión” es real
pero modesta y no monótona.

**Probabilidad condicional.** P(sube 21d | vol en Q2) = 59,70 % (**+1,7 pp** vs
base); P(sube 63d | ratio en Q2) = 64,69 % (**+1,4 pp**).

**Limitaciones.** (i) `vol_21` es *ex-post*: conocida en t, utilizable sin
look-ahead; (ii) el efecto “vol alta = mejor retorno medio” es típico de
recuperaciones y puede invertirse en mercados bajistas sostenidos; (iii) el
Sharpe por quintil asume rebalanceo diario sin costes.

**Patrones similares.** ATR(14) vs ATR(50), compresión de rangos de Bollinger
(band width percentil), ratio de volatilidad realizada/implícita, y régimen de
vol (terciles) como condicionante de otras señales.

---

### 3.4 Máximos de 52 semanas, breakouts y drawdowns

**SQL** (evento):

```sql
, ev AS (
    SELECT date, symbol,
           CASE WHEN px >= hi_52w THEN 'nuevo_max_52w'
                WHEN px <= 0.7 * hi_52w THEN 'drawdown_>30%'
                ELSE 'resto' END AS estado,
           fwd_21, fwd_63
    FROM f WHERE hi_52w IS NOT NULL AND fwd_21 IS NOT NULL
)
SELECT estado, COUNT(*) n, AVG(fwd_21) mean_fwd21,
       AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) hit21
FROM ev GROUP BY estado;
```

**Resultado — distancia al máximo de 52 semanas (quintiles):**

| Quintil | dist media | fwd 21d | fwd 63d | P(sube 21d) | Δ vs base |
|---|---|---|---|---|---|
| Q1 (muy lejos) | −24,2 % | +1,06 % | +3,30 % | 55,34 % | **−2,7 pp** |
| Q2 | −11,5 % | +1,16 % | +3,39 % | 57,60 % | −0,4 pp |
| Q3 | −6,6 % | +1,16 % | +3,33 % | 58,47 % | +0,5 pp |
| Q4 | −3,4 % | +1,14 % | +3,40 % | **59,46 %** | **+1,5 pp** |
| Q5 (pegado al máx.) | −1,0 % | +1,06 % | **+3,48 %** | 59,08 % | +1,1 pp |

**Resultado — eventos:**

| Estado | n | fwd 21d | fwd 63d | P(sube 21d) | P(sube 63d) |
|---|---|---|---|---|---|
| resto | 508.867 | +1,12 % | +3,33 % | 58,24 % | 63,45 % |
| nuevo máximo 52s | 46.076 | +0,76 % | +3,49 % | 56,65 % (−1,3 pp) | 64,48 % (+1,2 pp) |
| **drawdown >30 %** | 32.301 | **+1,56 %** | **+4,05 %** | 55,82 % (−2,2 pp) | 59,13 % (−4,2 pp) |

**Insight.** Hay una **asimetría fundamental** que separa probabilidad de
magnitud:
* Cerca del máximo (Q4-Q5): **más probable** que suba a 21d (+1,1/+1,5 pp) —
  efecto de anclaje/continuación suave.
* Drawdown profundo (>30 %): **menos probable** que suba en cualquier horizonte
  (55,8 % y 59,1 %), pero con **mayor retorno medio** (+1,56 % a 21d; +4,05 % a
  63d). Es la clásica distribución de “reversión con cola derecha gruesa”: la
  lotería es peor en frecuencia, mejor en pago.

**Probabilidad condicional.** P(sube 21d | a <3,5 % del máximo 52s) = **59,46 %**;
P(sube 63d | nuevo máximo 52s) = 64,48 %; P(sube 63d | drawdown >30 %) = 59,13 %.
Ojo: el “nuevo máximo” a 21d es *peor* que la base (−1,3 pp): comprar rupturas de
52 semanas no mejoró la probabilidad en esta muestra, aunque sí el retorno medio
a 63d.

**Limitaciones.** (i) El máximo de 52 semanas se calcula sobre precios ajustados
retroactivamente (puede introducir mínima inconsistencia); (ii) en la réplica
`hi_52w` usa 252 sesiones fijas, no semanas naturales; (iii) eventos solapados.

**Patrones similares.** Distancia al mínimo de 52 semanas, *anchoring* al precio
de cierre del año anterior, tiempo transcurrido desde el último máximo, y
combinación “drawdown >30 % **y** vol alta” (máxima asimetría).

---

### 3.5 Breakouts de 20 días y patrones de volumen

**SQL** (fragmento):

```sql
, ev AS (
    SELECT date, symbol, fwd_21, fwd_63,
           (px > hh_20_prev)          AS breakout,
           (volume > 1.5 * vol_avg20) AS vol_alto,
           (ret > 0)                  AS dia_positivo
    FROM f WHERE hh_20_prev IS NOT NULL AND vol_avg20 IS NOT NULL
)
SELECT CASE WHEN breakout AND vol_alto THEN 'breakout + volumen'
            WHEN breakout AND NOT vol_alto THEN 'breakout sin volumen'
            WHEN NOT breakout AND vol_alto AND dia_positivo THEN 'volumen sin breakout'
            ELSE 'sin señal' END AS estado,
       COUNT(*) n, AVG(fwd_21) mean_fwd21,
       AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) hit21
FROM ev GROUP BY estado;
```

**Resultado:**

| Estado | n | fwd 5d | fwd 21d | fwd 63d | P(sube 21d) | Δ vs base |
|---|---|---|---|---|---|---|
| sin señal | 520.319 | +0,29 % | +1,15 % | +3,41 % | 58,16 % | +0,2 pp |
| breakout + volumen | 9.398 | +0,01 % | +0,78 % | +3,22 % | 56,49 % | **−1,5 pp** |
| breakout sin volumen | 38.635 | +0,04 % | **+0,60 %** | +2,78 % | 55,98 % | **−2,0 pp** |
| **volumen sin breakout** | 18.386 | +0,32 % | **+1,24 %** | **+3,76 %** | 57,64 % | −0,3 pp |

**Resultado — ratio de volumen (`volume / avg20`) por quintiles:**

| Quintil | ratio | fwd 21d | P(sube 21d) |
|---|---|---|---|
| Q1 (menos volumen) | 0,62 | **+1,31 %** | **58,73 %** |
| Q2 | 0,79 | +1,21 % | 58,61 % |
| Q3 | 0,93 | +1,17 % | 58,66 % |
| Q4 | 1,09 | +1,14 % | 58,29 % |
| Q5 (más volumen) | 1,62 | +1,14 % | 57,86 % |

**Insight.** Doble sorpresa respecto al manual técnico clásico:
1. Los **breakouts de 20 días rinden peor que la media** (−2,0 pp de probabilidad
   sin volumen). Son el único grupo con retorno forward 5d prácticamente nulo.
2. El **volumen alto sin ruptura precedente** es el mejor de los tres grupos
   (−0,3 pp, no significativo, pero con el mayor fwd 63d: +3,76 %). El “ruido de
   volumen” sin extensión de precio no penaliza tanto como la ruptura.
3. La relación volumen→retorno es **negativa y monótona en los extremos**: menos
   volumen, mejor.

**Probabilidad condicional.** P(sube 21d | breakout + volumen) = 56,49 %
(IC95 % 55,49-57,49 %); P(sube 21d | Q1 de volumen) = 58,73 %.

**Limitaciones.** (i) Umbrales elegidos (20 días, 1,5×) sin optimizar → riesgo de
*multiple testing*; (ii) el volumen de la réplica no está ajustado por splits;
(iii) el “breakout” con `high` diario tiene ruido intradía.

**Patrones similares.** Ruptura de rango de Bollinger con expansión de ancho,
breakout de 60 días, *volume climax* (vol >3× con rango diario extremo), y
divergencia precio-volumen (subida sin volumen).

---

### 3.6 Tendencias con medias móviles (SMA)

**SQL** (fragmento):

```sql
SELECT CASE WHEN (px > sma50 AND sma50 > sma200) THEN 'px>sma50>sma200'
            WHEN (px < sma200 AND sma50 < sma200) THEN 'px<sma50<sma200'
            WHEN (px > sma200) THEN 'sobre sma200 (no apilada)'
            ELSE 'bajo sma200' END AS estado,
       COUNT(*) n, AVG(fwd_21) mean_fwd21,
       AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) hit21
FROM f WHERE sma200 IS NOT NULL GROUP BY estado;
```

**Resultado (diario):**

| Estado | n | fwd 21d | fwd 63d | P(sube 21d) | P(sube 63d) |
|---|---|---|---|---|---|
| **bajo SMA200** | 51.211 | **+2,13 %** | **+4,76 %** | **63,10 % (+5,1 pp)** | **66,63 % (+3,3 pp)** |
| sobre SMA200 (no apilada) | 142.664 | +1,30 % | +3,48 % | 59,60 % (+1,6 pp) | 64,46 % (+1,2 pp) |
| px>sma50>sma200 | 253.264 | +0,85 % | +3,36 % | 56,89 % (−1,1 pp) | 63,68 % (+0,4 pp) |
| px<sma50<sma200 | 140.105 | +1,04 % | +2,82 % | 56,46 % (−1,5 pp) | 60,19 % (−3,1 pp) |

**Resultado (versión MENSUAL no solapada — control):**

| Estado | n | fwd 1m | P(sube 1m) |
|---|---|---|---|
| sobre SMA200 | 15.644 | +0,75 % | 56,04 % |
| bajo SMA200 | 7.832 | **+1,02 %** | 55,21 % |

**Insight — y advertencia crítica.** La versión diaria sugiere que el precio bajo
SMA200 es la mejor condición del estudio (+5,1 pp, el mayor exceso de
probabilidad de todo el análisis). Sin embargo, **la versión mensual no lo
confirma**: el retorno medio sigue favoreciendo al precio bajo SMA200 (+1,02 %
vs +0,75 %) pero la *probabilidad* se invierte ligeramente (55,2 % vs 56,0 %).
Esto indica que (a) el efecto diario está parcialmente inflado por el solapamiento
de ventanas, y (b) el verdadero patrón es de **magnitud asimétrica**, no de
probabilidad. Es exactamente el tipo de resultado que hay que contrastar antes de
dar por bueno un backtest.

**Probabilidad condicional.** Diario: P(sube 21d | px < SMA200) = **63,10 %**
(IC95 % 62,68-63,51 %). Mensual: 55,21 %. La discrepancia es un recordatorio de
que el horizonte y la frecuencia de muestreo cambian la conclusión.

**Limitaciones.** (i) SMA200 = 200 sesiones; (ii) la muestra contiene un solo
ciclo bajista breve (ago-2015/feb-2016) → poca variación de régimen;
(iii) `px < SMA200` agrupa tanto correcciones sanas como deterioros estructurales.

**Patrones similares.** Golden/death cross (cruce SMA50-SMA200 en los últimos
5 días), precio > EMA21 (más reactivo), pendiente de SMA200 (derivada),
ADX para filtrar tendencias laterales.

---

### 3.7 Regímenes de mercado y co-movimientos (PCA)

**SQL** (régimen, fragmento):

```sql
idx0 AS (
    SELECT date, AVG(ret) OVER () AS _, mkt_ret,
           EXP(SUM(LN(1 + mkt_ret)) OVER (ORDER BY date)) AS idx_level
    FROM mkt WHERE n_vals >= 100
),
idx AS (
    SELECT *, AVG(idx_level) OVER (ORDER BY date ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) AS sma200_mkt,
              STDDEV_SAMP(mkt_ret) OVER (ORDER BY date ROWS BETWEEN 20 PRECEDING AND CURRENT ROW)*SQRT(252) AS vol_mkt
    FROM idx0
)
SELECT CASE WHEN idx_level > sma200_mkt AND vol_mkt <= mediana THEN 'alcista + vol baja' ...
```

**Resultado (índice equiponderado; n = días):**

| Régimen | n días | fwd 21d | fwd 63d | P(sube 21d) |
|---|---|---|---|---|
| alcista + vol baja | 570 | +0,68 % | +3,05 % | 65,61 % |
| **alcista + vol alta** | 480 | **+1,54 %** | +3,74 % | **71,67 %** |
| bajista + vol alta | 144 | +1,53 % | +3,84 % | 65,28 % |
| bajista + vol baja | 0 | — | — | — (no ocurrió) |

**PCA** (retornos diarios estandarizados, 1.145 fechas × 482 tickers):

| Componente | PC1 | PC2 | PC3 | … | PC10 |
|---|---|---|---|---|---|
| Varianza explicada | **29,36 %** | 5,81 % | 2,91 % | … | 0,80 % |

PC1..PC10 explican **46,9 %** de la varianza total → un único factor de mercado
explica ~30 %; el resto es idiosincrático (límite estructural de cualquier
estrategia cross-sectional en large caps).

**Insight.** No hubo ni un solo día en el que el índice equiponderado estuviese
bajo su SMA200 **con volatilidad baja**: los dos regímenes bajistas fueron
siempre de vol alta. Los retornos forward son *mayores* tras vol alta (1,53-1,54 %)
que tras vol baja (0,68 %) — coherente con el patrón de sobre-reacción: los
puntos de máxima tensión son los de mejor retorno forward en una muestra alcista.

**Probabilidad condicional.** P(sube 21d | régimen alcista + vol alta) = 71,67 %
(n=480, muy pocas observaciones independientes: en la práctica ~23 meses).

**Limitaciones.** Observaciones fuertemente solapadas (21 y 63 días sobre 1.194
días de muestra) → los IC son engañosamente estrechos; el régimen “bajista + vol
baja” no tiene datos; el peso del factor de mercado (29 %) implica que gran parte
de los resultados cross-sectional es beta disfrazada.

**Patrones similares.** Correlación media por pares rolling, dispersión
cross-sectional como proxy de VIX, cambio en la varianza explicada por PC1,
régimen de tipos/dólar (no disponible en la base).

---

### 3.8 Señal compuesta y estacionalidad

**SQL** — z-scores combinados:

```sql
, z AS (
    SELECT date, symbol, fwd_21, fwd_63,
           (r_12m - AVG(r_12m) OVER (PARTITION BY date))
             / NULLIF(STDDEV_SAMP(r_12m) OVER (PARTITION BY date),0)     AS z_mom,
           (px/NULLIF(hi_52w,0) - AVG(px/NULLIF(hi_52w,0)) OVER (PARTITION BY date))
             / NULLIF(STDDEV_SAMP(px/NULLIF(hi_52w,0)) OVER (PARTITION BY date),0) AS z_hi,
           (vol_21/NULLIF(vol_252,0) - AVG(vol_21/NULLIF(vol_252,0)) OVER (PARTITION BY date))
             / NULLIF(STDDEV_SAMP(vol_21/NULLIF(vol_252,0)) OVER (PARTITION BY date),0) AS z_volratio,
           (CASE WHEN px > sma200 THEN 1.0 ELSE 0 END
             - AVG(CASE WHEN px > sma200 THEN 1.0 ELSE 0 END) OVER (PARTITION BY date))
             / NULLIF(STDDEV_SAMP(CASE WHEN px > sma200 THEN 1.0 ELSE 0 END) OVER (PARTITION BY date),0) AS z_trend
    FROM f
)
SELECT score = z_mom + z_hi - z_volratio + z_trend ...
```

**Resultado (quintiles del score, diario):**

| Quintil | fwd 21d | fwd 63d | P(sube 21d) | P(sube 63d) |
|---|---|---|---|---|
| Q1 | +0,69 % | +2,49 % | 53,91 % | 58,08 % |
| Q2 | +0,81 % | +2,37 % | 55,82 % | 59,76 % |
| Q3 | **+1,00 %** | +2,72 % | 58,00 % | 62,01 % |
| Q4 | +0,87 % | +2,89 % | 57,40 % | 63,45 % |
| Q5 | +0,95 % | **+3,36 %** | 57,28 % | 63,55 % |

**Estabilidad temporal (train/test):**

| Periodo | Q1 (fwd 21d / hit) | Q5 (fwd 21d / hit) |
|---|---|---|
| 2013-2015 (in-sample) | −0,44 % / 49,68 % | +0,55 % / 54,61 % |
| 2016-2018 (out-of-sample) | **+2,03 %** / 59,21 % | +1,51 % / 60,92 % |

**Estacionalidad (retorno mensual medio por mes natural):**

| Mes | Ret. medio | P(sube) | | Mes | Ret. medio | P(sube) |
|---|---|---|---|---|---|---|
| Ene | −0,60 % | 47,6 % | | Jul | +2,09 % | 64,1 % |
| Feb | +1,86 % | 59,9 % | | Ago | **−1,06 %** | 43,5 % |
| Mar | +2,39 % | 64,6 % | | Sep | +0,26 % | 50,9 % |
| Abr | +0,59 % | 53,7 % | | **Oct** | **+2,70 %** | **66,6 %** |
| May | +1,60 % | 65,0 % | | **Nov** | **+2,78 %** | **68,1 %** |
| Jun | +0,11 % | 50,6 % | | Dic | +0,54 % | 56,8 % |

**Insight.** El score compuesto ordena bien la **magnitud** a 63 días
(2,49 % → 3,36 %, monótono salvo un par de inversiones) pero **no** la
probabilidad a 21 días (Q5 = 57,3 %, por *debajo* de la base). Y sobre todo:
**el edge desaparece fuera de muestra** — en 2016-2018 el quintil Q1 rindió más
que Q5 (+2,03 % vs +1,51 %) y las probabilidades convergen (59,2 % vs 60,9 %).
La estacionalidad muestra un patrón muy marcado (ago y ene negativos; oct/nov
muy fuertes), pero con 5 observaciones por mes es indistinguible de ruido:
trátala como descriptiva, no explotable.

**Probabilidad condicional.** P(sube 63d | Q5 del score) = 63,55 %, IC95 %
(63,24-63,87 %) — **no** significativamente distinta de la base (63,30 %).
P(sube 1m | octubre) = 66,6 %; P(sube 1m | agosto) = 43,5 %.

**Limitaciones.** (i) Los z-scores usan la sección completa del día (sin
look-ahead, están disponibles en el cierre); (ii) elección de pesos
1:1:−1:1 *ad hoc* → sobreajuste potencial; (iii) la pérdida de edge OOS es la
prueba de que un score combinado en una muestra de 5 años no es un modelo.

**Patrones similares.** Score con pesos por IC (ponderación por *information
coefficient*), composite sector-neutral, y *ensemble* de señales ortogonalizadas
(regresión cross-sectional de retornos futuros sobre z-scores).

---

## 4. Síntesis: probabilidades condicionales y su fiabilidad

| # | Condición (en t) | Horizonte | P(sube) | IC95 % Wilson | Δ vs base | p-valor |
|---|---|---|---|---|---|---|
| 1 | Caída ≥10 % en 5 días | 63d | **66,68 %** | 65,17-68,15 % | +3,4 pp | <0,0001 |
| 2 | Precio < SMA200 | 21d | **63,10 %** | 62,68-63,51 % | +5,1 pp | <0,0001 |
| 3 | Caída 2-2,5σ | 63d | 65,97 % | 65,02-66,91 % | +2,7 pp | <0,0001 |
| 4 | Día ≤ −2,5σ | 21d | 60,79 % | 59,66-61,91 % | +2,8 pp | <0,0001 |
| 5 | Dist. máx 52s en Q4 (−3,4 %) | 21d | 59,46 % | 59,18-59,75 % | +1,5 pp | <0,0001 |
| 6 | Vol 21d en Q2 (16,9 %) | 21d | 59,70 % | 59,42-59,98 % | +1,7 pp | <0,0001 |
| 7 | vol21/vol252 en Q2 (0,81) | 63d | 64,69 % | 64,42-64,96 % | +1,4 pp | <0,0001 |
| 8 | Nuevo máximo 52s | 21d | 56,65 % | 56,20-57,11 % | −1,3 pp | <0,0001 |
| 9 | Breakout 20d + volumen | 21d | 56,49 % | 55,49-57,49 % | −1,5 pp | 0,003 |
| 10 | Score compuesto Q5 | 21d | 57,28 % | 56,96-57,60 % | −0,7 pp | <0,0001 |

> Los p-valores son contra la tasa base usando el tamaño de muestra (cientos de
> miles), pero **las observaciones solapadas no son independientes**: el tamaño
> efectivo de muestra es ~h veces menor (h = horizonte en días). Con 505 acciones
> durante 5 años, el número de *eventos verdaderamente independientes* de una
> señal diaria es del orden de **cientos**, no de cientos de miles. Trata los
> p-valores como cotas inferiores de la incertidumbre.

---

## 5. Limitaciones (leer antes de usar cualquier conclusión)

1. **Los datos no son tu base.** Réplica 2013-02→2018-02 vs. tu ventana
   2015→2026. La muestra de la réplica es **extremadamente alcista** (P(sube
   21d) = 58 %; cualquier señal “larga” parece buena). Un análisis con tus datos
   cubriría 2020 (COVID), 2022 (bear market) y 2025-2026.
2. **Sesgo de supervivencia.** Los 505 tickers son los que sobrevivieron hasta
   2018 (y los sectores son los actuales). Las empresas que quebraron o salieron
   del índice no están → los retornos forward están sesgados al alza.
3. **`adj_close` ausente en la réplica.** Se replica con `close` y filtro
   |ret| > 50 % (artefactos de splits). En tu base, `adj_close` es real:
   **usa siempre `adj_close`** para retornos.
4. **Sin fundamentales/noticias/sentimiento.** `fundamentals`, `news`,
   `filings*`, `dividends`, `splits` y `signals` están vacías en la réplica: no
   se pudo testear el *value*, el *quality*, el *earnings momentum* ni el
   sentimiento, que en la literatura tienen tanto o más poder que el precio.
5. **Solapamiento de horizontes.** Los t-stats diarios están inflados ~√h.
   Solo las consultas **mensuales** (`momentum_quintiles`, `monthly_signals`)
   son no solapadas.
6. **Multiple testing.** Se probaron decenas de umbrales/quintiles: a α=5 %,
   ~1 de cada 20 hallazgos es falso positivo por construcción. Los patrones con
   |Δ| < 1 pp deben considerarse provisionales.
7. **Sin costes de transacción ni capacidad.** Un Sharpe L/S de 0,4 antes de
   costes se anula con 10-20 pb de coste por rebalanceo mensual.
8. **Un solo ciclo de mercado, un solo universo.** Nada de esto es un modelo
   predictivo; son **regularidades condicionales de esta muestra**.

**Lo que sí puedes confiar:** el SQL (validado, sin look-ahead, portable), la
metodología (comparación contra tasa base, IC de Wilson, IC/IR, train-test) y la
dirección de los efectos principales.

---

## 6. Sugerencias de análisis adicional

1. **Re-ejecución con tus datos** (lo más importante): `python3 run_analysis.py
   --db "C:\...\sp500.duckdb"`. Con 2015-2026 podremos ver si los patrones de
   sobre-reacción resisten en 2022 y si la reversión de 1 mes se mantiene.
2. **Condicionar por régimen**: repetir cada patrón dentro de los 3 regímenes de
   mercado. Sospecho que “precio < SMA200” funciona solo en régimen alcista y se
   invierte en bear markets sostenidos.
3. **Añadir las tablas que ya tienes**: `fundamentals` (PE, ROE, crecimiento) y
   `news` (sentimiento) permiten testear *value × momentum* y el efecto del
   sentimiento sobre la reversión — la combinación más prometedora de tu base.
4. **Doble ordenación (2×2)**: p. ej. bajo SMA200 × vol alta, o drawdown >30 % ×
   momentum 12m positivo; buscar asimetrías de magnitud, no solo de probabilidad.
5. **Estimación con intervalos bootstrap por bloques** (block bootstrap de 21
   días) para cuantificar la incertidumbre real de los hit ratios condicionales.
6. **Neutralización sector-neutral sistemática** (`v_momentum_sector_neutral`
   ya existe): repetir el compuesto en versión sector-neutral.
7. **Costes**: anualizar el turnover de cada señal y calcular el Sharpe neto con
   supuestos de 5/10/20 pb.

---

## 7. Archivos generados

```
sp500_quant/
├── RESULTADOS.md              ← este informe
├── README.md                  ← cómo ejecutarlo sobre tu base
├── build_replica.py           ← construye la réplica con el esquema de tu base
├── run_analysis.py            ← suite de 17 consultas + estadística
├── significancia.py           ← hit ratios vs tasa base (Wilson + z-test)
├── make_figures.py            ← figuras
├── sql/patrones.sql           ← TODA la librería SQL, comentada y validada
└── resultados/
    ├── *.csv                  ← una tabla por patrón
    ├── significancia_vs_base.csv
    ├── resumen.json
    └── figuras/patrones_sp500.png
```

---

*Este documento analiza patrones estadísticos históricos. No constituye
recomendación de inversión, ni asesoramiento financiero, ni una predicción. Las
probabilidades estimadas son condicionales a una muestra concreta y pueden no
repetirse.*
