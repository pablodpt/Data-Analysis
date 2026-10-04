#!/usr/bin/env python3
"""
run_analysis.py — Suite de análisis cuantitativo de patrones sobre una base
DuckDB con el esquema `sp500.duckdb`.

Ejecuta SQL válido DuckDB (sin inventar tablas/columnas: usa `prices` y
`tickers`, presentes en el esquema original) y produce, por patrón:
  * quintiles / eventos
  * nº de observaciones, retorno medio/mediano forward
  * hit ratio (P(suba)) con IC95% de Wilson
  * t-stat (con caveats de solapamiento)
  * Sharpe anualizado del portfolio long-only del quintil superior
  * Information Ratio vs. benchmark equiponderado

Uso:
    python3 run_analysis.py --db data/sp500_replica.duckdb --out resultados
"""
from __future__ import annotations

import argparse
import json
import math
import os

import duckdb
import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Panel de features (SQL base que usan todas las consultas).
# Sólo `prices` y `tickers` — columnas existentes en el esquema original.
# --------------------------------------------------------------------------
PANEL = """
WITH d AS (
    SELECT p.symbol, p.date,
           COALESCE(p.adj_close, p.close) AS px,
           p.high, p.low, p.volume, t.sector
    FROM prices p
    LEFT JOIN tickers t ON t.symbol = p.symbol
),
r AS (
    SELECT *,
           CASE WHEN LAG(px) OVER (PARTITION BY symbol ORDER BY date) > 0
                THEN px / LAG(px) OVER (PARTITION BY symbol ORDER BY date) - 1
           END AS ret
    FROM d
),
f AS (
    SELECT *,
        px / NULLIF(LAG(px, 5)   OVER (PARTITION BY symbol ORDER BY date), 0) - 1 AS r_5d,
        px / NULLIF(LAG(px, 21)  OVER (PARTITION BY symbol ORDER BY date), 0) - 1 AS r_1m,
        px / NULLIF(LAG(px, 63)  OVER (PARTITION BY symbol ORDER BY date), 0) - 1 AS r_3m,
        px / NULLIF(LAG(px, 126) OVER (PARTITION BY symbol ORDER BY date), 0) - 1 AS r_6m,
        px / NULLIF(LAG(px, 252) OVER (PARTITION BY symbol ORDER BY date), 0) - 1 AS r_12m,
        STDDEV_SAMP(ret) OVER (PARTITION BY symbol ORDER BY date
                               ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) * SQRT(252) AS vol_21,
        STDDEV_SAMP(ret) OVER (PARTITION BY symbol ORDER BY date
                               ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) * SQRT(252) AS vol_252,
        MAX(px) OVER (PARTITION BY symbol ORDER BY date
                      ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS hi_52w,
        MAX(high) OVER (PARTITION BY symbol ORDER BY date
                        ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS hh_20_prev,
        AVG(volume) OVER (PARTITION BY symbol ORDER BY date
                          ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS vol_avg20,
        AVG(px) OVER (PARTITION BY symbol ORDER BY date
                      ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS sma50,
        AVG(px) OVER (PARTITION BY symbol ORDER BY date
                      ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) AS sma200,
        LEAD(px, 5)  OVER (PARTITION BY symbol ORDER BY date) / px - 1 AS fwd_5d,
        LEAD(px, 21) OVER (PARTITION BY symbol ORDER BY date) / px - 1 AS fwd_21,
        LEAD(px, 63) OVER (PARTITION BY symbol ORDER BY date) / px - 1 AS fwd_63
    FROM r
)
"""

# --------------------------------------------------------------------------
# QUERIES  (cada una es SQL DuckDB autónomo y copiable a la base del usuario)
# --------------------------------------------------------------------------
QUERIES: dict[str, str] = {}

# --- 1. Momentum mensual: quintiles por horizonte -> retorno forward 1 mes ---
QUERIES["momentum_quintiles"] = """
WITH m AS (
    SELECT symbol, mes, close,
           LAG(close, 1)  OVER w AS c_1,
           LAG(close, 3)  OVER w AS c_3,
           LAG(close, 6)  OVER w AS c_6,
           LAG(close, 12) OVER w AS c_12,
           LEAD(close, 1) OVER w AS c_next
    FROM v_precios_mensuales
    WINDOW w AS (PARTITION BY symbol ORDER BY mes)
),
s AS (
    SELECT symbol, mes, c_next / close - 1 AS fwd_1m,
           close / NULLIF(c_1,0)  - 1 AS mom_1m,
           close / NULLIF(c_3,0)  - 1 AS mom_3m,
           close / NULLIF(c_6,0)  - 1 AS mom_6m,
           close / NULLIF(c_12,0) - 1 AS mom_12m,
           c_1   / NULLIF(c_12,0) - 1 AS mom_12_1
    FROM m
),
b AS (
    SELECT mes, {MOM} AS sig, fwd_1m,
           NTILE(5) OVER (PARTITION BY mes ORDER BY {MOM}) AS q
    FROM s
    WHERE {MOM} IS NOT NULL AND fwd_1m IS NOT NULL
)
SELECT q,
       COUNT(*)                                                        AS n,
       AVG(fwd_1m)                                                     AS mean_fwd,
       MEDIAN(fwd_1m)                                                  AS median_fwd,
       AVG(CASE WHEN fwd_1m > 0 THEN 1.0 ELSE 0 END)                   AS hit,
       STDDEV_SAMP(fwd_1m)                                             AS sd_fwd,
       AVG(fwd_1m) / (STDDEV_SAMP(fwd_1m) / SQRT(COUNT(*)))            AS t_stat
FROM b
GROUP BY q
ORDER BY q
"""

# --- 2. IC mensual (Spearman) entre señal y retorno forward ---
QUERIES["momentum_ic"] = """
WITH m AS (
    SELECT symbol, mes, close,
           LAG(close, 1)  OVER w AS c_1,
           LAG(close, 3)  OVER w AS c_3,
           LAG(close, 6)  OVER w AS c_6,
           LAG(close, 12) OVER w AS c_12,
           LEAD(close, 1) OVER w AS c_next
    FROM v_precios_mensuales
    WINDOW w AS (PARTITION BY symbol ORDER BY mes)
),
s AS (
    SELECT mes, c_next / close - 1 AS fwd_1m,
           close / NULLIF(c_1,0)  - 1 AS mom_1m,
           close / NULLIF(c_3,0)  - 1 AS mom_3m,
           close / NULLIF(c_6,0)  - 1 AS mom_6m,
           close / NULLIF(c_12,0) - 1 AS mom_12m,
           c_1   / NULLIF(c_12,0) - 1 AS mom_12_1
    FROM m
    WHERE c_next IS NOT NULL
),
rk AS (
    SELECT mes, fwd_1m,
           RANK() OVER (PARTITION BY mes ORDER BY {MOM})         AS r_sig,
           RANK() OVER (PARTITION BY mes ORDER BY fwd_1m)        AS r_fwd
    FROM s
    WHERE {MOM} IS NOT NULL AND fwd_1m IS NOT NULL
)
SELECT mes, COUNT(*) AS n,
       CORR(r_sig, r_fwd) AS ic_spearman
FROM rk
GROUP BY mes
HAVING COUNT(*) >= 50
ORDER BY mes
"""

# --- 3. Reversión a corto plazo (r_5d) -> forward 5d / 21d ---
QUERIES["short_term_reversal"] = f"""
{PANEL}
, b AS (
    SELECT date, r_5d, fwd_5d, fwd_21,
           NTILE(5) OVER (PARTITION BY date ORDER BY r_5d) AS q
    FROM f
    WHERE r_5d IS NOT NULL AND fwd_5d IS NOT NULL AND fwd_21 IS NOT NULL
),
b2 AS (
    SELECT q,
           COUNT(*) n,
           AVG(fwd_5d)  AS mean_fwd5,
           AVG(fwd_21)  AS mean_fwd21,
           AVG(CASE WHEN fwd_5d  > 0 THEN 1.0 ELSE 0 END) AS hit5,
           AVG(CASE WHEN fwd_21  > 0 THEN 1.0 ELSE 0 END) AS hit21,
           CORR(r_5d, fwd_5d) AS corr_sig_fwd5
    FROM b GROUP BY q
)
SELECT * FROM b2 ORDER BY q
"""

# --- 4. Autocorrelación de retornos por símbolo (diaria y mensual) ---
QUERIES["autocorrelation"] = f"""
{PANEL}
, lag AS (
    SELECT symbol,
           ret,
           LAG(ret, 1) OVER (PARTITION BY symbol ORDER BY date) AS ret_l1,
           LAG(ret, 5) OVER (PARTITION BY symbol ORDER BY date) AS ret_l5
    FROM f
),
daily AS (
    SELECT symbol,
           COUNT(*) FILTER (WHERE ret IS NOT NULL AND ret_l1 IS NOT NULL) AS n_d,
           CORR(ret, ret_l1) AS ac1_d,
           CORR(ret, ret_l5) AS ac5_d
    FROM lag GROUP BY symbol
),
m AS (
    SELECT symbol, mes, close,
           LAG(close) OVER (PARTITION BY symbol ORDER BY mes) AS c_prev
    FROM v_precios_mensuales
),
mr AS (
    SELECT symbol, mes, close / NULLIF(c_prev,0) - 1 AS mret,
           LAG(close / NULLIF(c_prev,0) - 1) OVER (PARTITION BY symbol ORDER BY mes) AS mret_l1
    FROM m
),
monthly AS (
    SELECT symbol, CORR(mret, mret_l1) AS ac1_m
    FROM mr WHERE mret IS NOT NULL AND mret_l1 IS NOT NULL GROUP BY symbol
)
SELECT d.symbol, d.n_d, d.ac1_d, d.ac5_d, mo.ac1_m,
       AVG(d.ac1_d) OVER () AS media_ac1_diaria,
       MEDIAN(d.ac1_d) OVER () AS mediana_ac1_diaria
FROM daily d
LEFT JOIN monthly mo USING (symbol)
WHERE d.n_d >= 500
ORDER BY d.ac1_d
"""

# --- 5. Nivel de volatilidad (vol_21) -> forward ---
QUERIES["volatility_level"] = f"""
{PANEL}
, b AS (
    SELECT date, vol_21, fwd_21, fwd_63,
           NTILE(5) OVER (PARTITION BY date ORDER BY vol_21) AS q
    FROM f
    WHERE vol_21 IS NOT NULL AND fwd_21 IS NOT NULL AND fwd_63 IS NOT NULL
)
SELECT q, COUNT(*) n,
       AVG(vol_21) AS vol_media,
       AVG(fwd_21) AS mean_fwd21,
       AVG(fwd_63) AS mean_fwd63,
       AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) AS hit21,
       AVG(fwd_21) / (STDDEV_SAMP(fwd_21) / SQRT(COUNT(*)))            AS t21,
       AVG(fwd_21) / STDDEV_SAMP(fwd_21)                                AS sharpe_ratio_21
FROM b GROUP BY q ORDER BY q
"""

# --- 6. Compresión de volatilidad (vol_21 / vol_252) -> forward ---
QUERIES["volatility_compression"] = f"""
{PANEL}
, b AS (
    SELECT date, vol_21 / NULLIF(vol_252, 0) AS vol_ratio, fwd_21, fwd_63,
           NTILE(5) OVER (PARTITION BY date ORDER BY vol_21 / NULLIF(vol_252,0)) AS q
    FROM f
    WHERE vol_252 IS NOT NULL AND vol_21 IS NOT NULL
      AND fwd_21 IS NOT NULL AND fwd_63 IS NOT NULL
)
SELECT q, COUNT(*) n,
       AVG(vol_ratio) AS ratio_medio,
       AVG(fwd_21) AS mean_fwd21,
       AVG(fwd_63) AS mean_fwd63,
       AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) AS hit21,
       AVG(CASE WHEN fwd_63 > 0 THEN 1.0 ELSE 0 END) AS hit63,
       AVG(fwd_21) / (STDDEV_SAMP(fwd_21)/SQRT(COUNT(*))) AS t21
FROM b GROUP BY q ORDER BY q
"""

# --- 7. Distancia al máximo de 52 semanas -> forward ---
QUERIES["dist_52w_high"] = f"""
{PANEL}
, b AS (
    SELECT date, px / NULLIF(hi_52w, 0) - 1 AS dist_hi, fwd_21, fwd_63,
           NTILE(5) OVER (PARTITION BY date ORDER BY px / NULLIF(hi_52w,0)) AS q
    FROM f
    WHERE hi_52w IS NOT NULL AND fwd_21 IS NOT NULL AND fwd_63 IS NOT NULL
)
SELECT q, COUNT(*) n,
       AVG(dist_hi) AS dist_medio,
       AVG(fwd_21) AS mean_fwd21,
       AVG(fwd_63) AS mean_fwd63,
       AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) AS hit21,
       AVG(CASE WHEN fwd_63 > 0 THEN 1.0 ELSE 0 END) AS hit63,
       AVG(fwd_21) / (STDDEV_SAMP(fwd_21)/SQRT(COUNT(*))) AS t21
FROM b GROUP BY q ORDER BY q
"""

# --- 7b. Evento: nuevo máximo de 52 semanas ---
QUERIES["new_52w_high_event"] = f"""
{PANEL}
, ev AS (
    SELECT date, symbol,
           CASE WHEN px >= hi_52w THEN 'nuevo_max_52w'
                WHEN px <= (1 - 0.30) * hi_52w THEN 'drawdown_>30%'
                ELSE 'resto' END AS estado,
           fwd_21, fwd_63
    FROM f WHERE hi_52w IS NOT NULL AND fwd_21 IS NOT NULL AND fwd_63 IS NOT NULL
)
SELECT estado, COUNT(*) n,
       AVG(fwd_21) mean_fwd21, AVG(fwd_63) mean_fwd63,
       AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) hit21,
       AVG(CASE WHEN fwd_63 > 0 THEN 1.0 ELSE 0 END) hit63,
       AVG(fwd_21) / (STDDEV_SAMP(fwd_21)/SQRT(COUNT(*))) t21
FROM ev GROUP BY estado ORDER BY n DESC
"""

# --- 8. Breakout de máximos de 20 días, con y sin confirmación de volumen ---
QUERIES["breakout_20d"] = f"""
{PANEL}
, ev AS (
    SELECT date, symbol, fwd_5d, fwd_21, fwd_63,
           (px > hh_20_prev)                       AS breakout,
           (volume > 1.5 * vol_avg20)              AS vol_alto,
           (ret > 0)                               AS dia_positivo
    FROM f
    WHERE hh_20_prev IS NOT NULL AND vol_avg20 IS NOT NULL
      AND fwd_5d IS NOT NULL AND fwd_21 IS NOT NULL AND fwd_63 IS NOT NULL
),
g AS (
    SELECT CASE WHEN breakout AND vol_alto THEN 'breakout + volumen'
                WHEN breakout AND NOT vol_alto THEN 'breakout sin volumen'
                WHEN NOT breakout AND vol_alto AND dia_positivo THEN 'volumen sin breakout'
                ELSE 'sin señal' END AS estado,
           fwd_5d, fwd_21, fwd_63
    FROM ev
)
SELECT estado, COUNT(*) n,
       AVG(fwd_5d) mean_fwd5, AVG(fwd_21) mean_fwd21, AVG(fwd_63) mean_fwd63,
       AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) hit21,
       AVG(fwd_21) / (STDDEV_SAMP(fwd_21)/SQRT(COUNT(*))) t21
FROM g GROUP BY estado ORDER BY n DESC
"""

# --- 9. Estados de tendencia (SMA) ---
QUERIES["trend_sma"] = f"""
{PANEL}
, ev AS (
    SELECT date, symbol, fwd_21, fwd_63,
           (px > sma200)              AS sobre_sma200,
           (sma50 > sma200)           AS cruce_dorado,
           (px > sma50 AND sma50 > sma200) AS tendencia_apilada,
           (px < sma200 AND sma50 < sma200) AS tendencia_bajista
    FROM f
    WHERE sma200 IS NOT NULL AND fwd_21 IS NOT NULL AND fwd_63 IS NOT NULL
),
g AS (
    SELECT CASE WHEN tendencia_apilada THEN 'px>sma50>sma200'
                WHEN tendencia_bajista  THEN 'px<sma50<sma200'
                WHEN sobre_sma200       THEN 'sobre sma200 (no apilada)'
                ELSE 'bajo sma200' END AS estado,
           fwd_21, fwd_63
    FROM ev
)
SELECT estado, COUNT(*) n,
       AVG(fwd_21) mean_fwd21, AVG(fwd_63) mean_fwd63,
       AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) hit21,
       AVG(CASE WHEN fwd_63 > 0 THEN 1.0 ELSE 0 END) hit63,
       AVG(fwd_21) / (STDDEV_SAMP(fwd_21)/SQRT(COUNT(*))) t21
FROM g GROUP BY estado ORDER BY n DESC
"""

# --- 10. Volumen: ratio vs media 20d -> forward ---
QUERIES["volume_ratio"] = f"""
{PANEL}
, b AS (
    SELECT date, volume / NULLIF(vol_avg20, 0) AS volratio, fwd_21,
           NTILE(5) OVER (PARTITION BY date
                          ORDER BY volume / NULLIF(vol_avg20, 0)) AS q
    FROM f
    WHERE vol_avg20 IS NOT NULL AND vol_avg20 > 0 AND fwd_21 IS NOT NULL
)
SELECT q, COUNT(*) n,
       AVG(volratio) ratio_medio,
       AVG(fwd_21) mean_fwd21,
       AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) hit21,
       AVG(fwd_21) / (STDDEV_SAMP(fwd_21)/SQRT(COUNT(*))) t21
FROM b GROUP BY q ORDER BY q
"""

# --- 11. Régimen de mercado (índice equiponderado + volatilidad media) ---
QUERIES["market_regime"] = """
WITH d AS (
    SELECT p.symbol, p.date, COALESCE(p.adj_close, p.close) AS px, p.volume
    FROM prices p
),
r AS (
    SELECT symbol, date, px,
           CASE WHEN LAG(px) OVER (PARTITION BY symbol ORDER BY date) > 0
                THEN px / LAG(px) OVER (PARTITION BY symbol ORDER BY date) - 1 END AS ret
    FROM d
),
mkt AS (
    SELECT date, AVG(ret) AS mkt_ret, STDDEV_SAMP(ret) AS disp,
           COUNT(ret) AS n_vals
    FROM r GROUP BY date
),
idx0 AS (
    SELECT date, mkt_ret, disp, n_vals,
           EXP(SUM(LN(1 + mkt_ret)) OVER (ORDER BY date)) AS idx_level
    FROM mkt
    WHERE n_vals >= 100
),
idx AS (
    SELECT date, mkt_ret, disp, n_vals, idx_level,
           AVG(idx_level) OVER (ORDER BY date ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) AS sma200_mkt,
           STDDEV_SAMP(mkt_ret) OVER (ORDER BY date ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) * SQRT(252) AS vol_mkt
    FROM idx0
),
lead AS (
    SELECT *,
           LEAD(idx_level, 21) OVER (ORDER BY date) / idx_level - 1 AS fwd_21,
           LEAD(idx_level, 63) OVER (ORDER BY date) / idx_level - 1 AS fwd_63
    FROM idx
)
SELECT estado, COUNT(*) n_dias,
       AVG(fwd_21) mean_fwd21, AVG(fwd_63) mean_fwd63,
       AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) hit21,
       AVG(fwd_21) / (STDDEV_SAMP(fwd_21)/SQRT(COUNT(*))) t21
FROM (
    SELECT *,
        CASE WHEN idx_level > sma200_mkt AND vol_mkt <=
                  (SELECT MEDIAN(vol_mkt) FROM lead) THEN 'alcista + vol baja'
             WHEN idx_level > sma200_mkt THEN 'alcista + vol alta'
             WHEN idx_level <= sma200_mkt AND vol_mkt >
                  (SELECT MEDIAN(vol_mkt) FROM lead) THEN 'bajista + vol alta'
             ELSE 'bajista + vol baja' END AS estado
    FROM lead
    WHERE fwd_21 IS NOT NULL AND fwd_63 IS NOT NULL AND sma200_mkt IS NOT NULL AND vol_mkt IS NOT NULL
)
GROUP BY estado ORDER BY n_dias DESC
"""

# --- 12. Señal compuesta (z-scores) -> forward ---
QUERIES["composite_signal"] = f"""
{PANEL}
, z AS (
    SELECT date, symbol, sector, fwd_21, fwd_63, px, sma200, hi_52w,
           (r_12m - AVG(r_12m) OVER (PARTITION BY date)) / NULLIF(STDDEV_SAMP(r_12m) OVER (PARTITION BY date), 0) AS z_mom,
           (px/NULLIF(hi_52w,0) - AVG(px/NULLIF(hi_52w,0)) OVER (PARTITION BY date))
             / NULLIF(STDDEV_SAMP(px/NULLIF(hi_52w,0)) OVER (PARTITION BY date), 0)             AS z_hi,
           (vol_21/NULLIF(vol_252,0) - AVG(vol_21/NULLIF(vol_252,0)) OVER (PARTITION BY date))
             / NULLIF(STDDEV_SAMP(vol_21/NULLIF(vol_252,0)) OVER (PARTITION BY date), 0)        AS z_volratio,
           (CASE WHEN px > sma200 THEN 1.0 ELSE 0 END
             - AVG(CASE WHEN px > sma200 THEN 1.0 ELSE 0 END) OVER (PARTITION BY date))
             / NULLIF(STDDEV_SAMP(CASE WHEN px > sma200 THEN 1.0 ELSE 0 END)
                      OVER (PARTITION BY date), 0)                                              AS z_trend
    FROM f
    WHERE r_12m IS NOT NULL AND hi_52w IS NOT NULL AND vol_252 IS NOT NULL
      AND sma200 IS NOT NULL AND fwd_21 IS NOT NULL AND fwd_63 IS NOT NULL
),
sc AS (
    SELECT *,
           z_mom + z_hi - z_volratio + z_trend AS score
    FROM z
),
b AS (
    SELECT *,
           NTILE(5) OVER (PARTITION BY date ORDER BY score) AS q,
           NTILE(2) OVER (PARTITION BY date ORDER BY score) AS mitad
    FROM sc
)
SELECT q, COUNT(*) n,
       AVG(score) score_medio,
       AVG(fwd_21) mean_fwd21, AVG(fwd_63) mean_fwd63,
       AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) hit21,
       AVG(CASE WHEN fwd_63 > 0 THEN 1.0 ELSE 0 END) hit63,
       AVG(fwd_21) / (STDDEV_SAMP(fwd_21)/SQRT(COUNT(*))) t21
FROM b GROUP BY q ORDER BY q
"""

# --- 12b. Compuesto: estabilidad temporal (2013-2015 vs 2016-2018) ---
QUERIES["composite_by_period"] = f"""
{PANEL}
, z AS (
    SELECT date, symbol, fwd_21,
           (r_12m - AVG(r_12m) OVER (PARTITION BY date)) / NULLIF(STDDEV_SAMP(r_12m) OVER (PARTITION BY date), 0) AS z_mom,
           (px/NULLIF(hi_52w,0) - AVG(px/NULLIF(hi_52w,0)) OVER (PARTITION BY date))
             / NULLIF(STDDEV_SAMP(px/NULLIF(hi_52w,0)) OVER (PARTITION BY date), 0)             AS z_hi,
           (vol_21/NULLIF(vol_252,0) - AVG(vol_21/NULLIF(vol_252,0)) OVER (PARTITION BY date))
             / NULLIF(STDDEV_SAMP(vol_21/NULLIF(vol_252,0)) OVER (PARTITION BY date), 0)        AS z_volratio,
           (CASE WHEN px > sma200 THEN 1.0 ELSE 0 END
             - AVG(CASE WHEN px > sma200 THEN 1.0 ELSE 0 END) OVER (PARTITION BY date))
             / NULLIF(STDDEV_SAMP(CASE WHEN px > sma200 THEN 1.0 ELSE 0 END)
                      OVER (PARTITION BY date), 0)                                              AS z_trend
    FROM f
    WHERE r_12m IS NOT NULL AND hi_52w IS NOT NULL AND vol_252 IS NOT NULL
      AND sma200 IS NOT NULL AND fwd_21 IS NOT NULL
),
sc AS (SELECT *, z_mom + z_hi - z_volratio + z_trend AS score FROM z),
b AS (
    SELECT *,
           CASE WHEN date < DATE '2016-01-01' THEN '2013-2015 (in-sample)'
                ELSE '2016-2018 (out-of-sample)' END AS periodo,
           NTILE(5) OVER (PARTITION BY date ORDER BY score) AS q
    FROM sc
)
SELECT periodo, q, COUNT(*) n,
       AVG(fwd_21) mean_fwd21,
       AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) hit21,
       AVG(fwd_21) / (STDDEV_SAMP(fwd_21)/SQRT(COUNT(*))) t21
FROM b GROUP BY periodo, q ORDER BY periodo, q
"""

# --- 12c. Eventos extremos de caída (sobre-reacción) -> forward ---
QUERIES["extreme_down_events"] = f"""
{PANEL}
, ev AS (
    SELECT date, symbol, ret, vol_21 / SQRT(252) AS vol_diaria,
           r_5d, fwd_5d, fwd_21, fwd_63
    FROM f
    WHERE vol_21 IS NOT NULL AND fwd_5d IS NOT NULL AND fwd_21 IS NOT NULL AND fwd_63 IS NOT NULL
),
g AS (
    SELECT CASE
             WHEN ret <= -2.5 * vol_diaria THEN 'caida >=2.5 sigma'
             WHEN ret <= -2.0 * vol_diaria THEN 'caida 2-2.5 sigma'
             WHEN r_5d <= -0.10 THEN 'caida 10% en 5 dias'
             WHEN ret >= 2.0 * vol_diaria THEN 'subida >=2 sigma'
             ELSE 'resto' END AS estado,
           fwd_5d, fwd_21, fwd_63
    FROM ev
)
SELECT estado, COUNT(*) n,
       AVG(fwd_5d) mean_fwd5, AVG(fwd_21) mean_fwd21, AVG(fwd_63) mean_fwd63,
       AVG(CASE WHEN fwd_5d  > 0 THEN 1.0 ELSE 0 END) hit5,
       AVG(CASE WHEN fwd_21  > 0 THEN 1.0 ELSE 0 END) hit21,
       AVG(CASE WHEN fwd_63  > 0 THEN 1.0 ELSE 0 END) hit63
FROM g GROUP BY estado ORDER BY n DESC
"""

# --- 12d. Versión MENSUAL no solapada de las señales clave ---
QUERIES["monthly_signals"] = """
WITH m AS (
    SELECT symbol, mes, close,
           LAG(close, 12) OVER w AS c_12,
           LEAD(close)   OVER w AS c_next
    FROM v_precios_mensuales
    WINDOW w AS (PARTITION BY symbol ORDER BY mes)
),
d AS (
    SELECT p.symbol, p.date, COALESCE(p.adj_close, p.close) AS px, t.sector
    FROM prices p LEFT JOIN tickers t ON t.symbol = p.symbol
),
f AS (
    SELECT *,
           MAX(px) OVER (PARTITION BY symbol ORDER BY date
                         ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS hi_52w,
           AVG(px) OVER (PARTITION BY symbol ORDER BY date
                         ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) AS sma200
    FROM d
),
mm AS (
    SELECT m.symbol, m.mes, m.c_12, m.c_next, m.close,
           f.hi_52w, f.sma200, f.px,
           ROW_NUMBER() OVER (PARTITION BY m.symbol, m.mes ORDER BY f.date DESC) AS rn
    FROM m JOIN f ON f.symbol = m.symbol
      AND date_trunc('month', f.date) = m.mes
),
last_day AS (
    SELECT * FROM mm WHERE rn = 1
),
sig AS (
    SELECT symbol, mes,
           close / NULLIF(c_12,0) - 1                            AS mom_12m,
           px / NULLIF(hi_52w,0) - 1                             AS dist_hi,
           CASE WHEN px > sma200 THEN 'sobre_sma200' ELSE 'bajo_sma200' END AS trend,
           c_next / NULLIF(close,0) - 1                          AS fwd_1m
    FROM last_day
    WHERE c_next IS NOT NULL AND hi_52w IS NOT NULL AND sma200 IS NOT NULL
),
b AS (
    SELECT mes, trend, fwd_1m,
           NTILE(5) OVER (PARTITION BY mes ORDER BY mom_12m) AS q_mom,
           NTILE(5) OVER (PARTITION BY mes ORDER BY dist_hi) AS q_hi
    FROM sig WHERE mom_12m IS NOT NULL AND dist_hi IS NOT NULL
)
SELECT 'momentum_12m' AS señal, CAST(q_mom AS VARCHAR) AS bucket, COUNT(*) n,
       AVG(fwd_1m) mean_fwd, AVG(CASE WHEN fwd_1m > 0 THEN 1.0 ELSE 0 END) hit
FROM b GROUP BY 1,2
UNION ALL
SELECT 'dist_52w_high', CAST(q_hi AS VARCHAR), COUNT(*),
       AVG(fwd_1m), AVG(CASE WHEN fwd_1m > 0 THEN 1.0 ELSE 0 END)
FROM b GROUP BY 1,2
UNION ALL
SELECT 'tendencia_sma200', trend, COUNT(*),
       AVG(fwd_1m), AVG(CASE WHEN fwd_1m > 0 THEN 1.0 ELSE 0 END)
FROM b GROUP BY 1,2
ORDER BY 1, 2
"""

# --- 13. Estacionalidad por mes natural ---
QUERIES["seasonality"] = """
WITH m AS (
    SELECT symbol, mes, close,
           LAG(close) OVER (PARTITION BY symbol ORDER BY mes) AS c_prev
    FROM v_precios_mensuales
)
SELECT MONTH(mes) AS mes_natural,
       COUNT(*) n,
       AVG(close / NULLIF(c_prev,0) - 1) AS ret_medio,
       MEDIAN(close / NULLIF(c_prev,0) - 1) AS ret_mediano,
       AVG(CASE WHEN close > c_prev THEN 1.0 ELSE 0 END) AS hit,
       AVG(close / NULLIF(c_prev,0) - 1)
         / (STDDEV_SAMP(close / NULLIF(c_prev,0) - 1)/SQRT(COUNT(*))) AS t_stat
FROM m
WHERE c_prev IS NOT NULL
GROUP BY 1 ORDER BY 1
"""


# --------------------------------------------------------------------------
# Post-proceso estadístico
# --------------------------------------------------------------------------
def wilson(k: float, n: float, z: float = 1.96) -> tuple[float, float]:
    """IC95% de Wilson para una proporción."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / den
    return (centre - half, centre + half)


def add_wilson(df: pd.DataFrame, hit_col: str = "hit", n_col: str = "n") -> pd.DataFrame:
    if hit_col in df and n_col in df:
        ci = [wilson(h * n, n) for h, n in zip(df[hit_col], df[n_col])]
        df["hit_lo95"] = [c[0] for c in ci]
        df["hit_hi95"] = [c[1] for c in ci]
    return df


def monthly_ls_stats(con: duckdb.DuckDBPyConnection, mom_col: str) -> dict:
    """Sharpe e IR mensuales del portfolio L/S (Q5-Q1) por señal de momentum."""
    q = QUERIES["momentum_quintiles"].replace("{MOM}", mom_col)
    df = con.execute(q).fetchdf()
    # reconstruir serie mensual de medias por quintil
    series = con.execute(
        QUERIES["momentum_quintiles"].replace("{MOM}", mom_col)
        .replace("SELECT q,", "SELECT mes, q,")
        .replace("GROUP BY q", "GROUP BY mes, q")
    ).fetchdf()
    piv = series.pivot_table(index="mes", columns="q", values="mean_fwd")
    if 5 not in piv or 1 not in piv:
        return {}
    ls = piv[5] - piv[1]
    ew = piv.mean(axis=1)
    ann = math.sqrt(12)
    return {
        "señal": mom_col,
        "meses": int(ls.notna().sum()),
        "ret_medio_ls_mensual": float(ls.mean()),
        "sharpe_ls_anualizado": float(ls.mean() / ls.std(ddof=1) * ann) if ls.std(ddof=1) else float("nan"),
        "hit_ls": float((ls > 0).mean()),
        "ir_vs_ew": float((ls - 0).mean() / (ls.std(ddof=1)) * ann) if ls.std(ddof=1) else float("nan"),
        "ret_medio_ew_mensual": float(ew.mean()),
    }


def ic_stats(con: duckdb.DuckDBPyConnection, mom_col: str) -> dict:
    df = con.execute(QUERIES["momentum_ic"].replace("{MOM}", mom_col)).fetchdf()
    ic = df["ic_spearman"].dropna()
    return {
        "señal": mom_col,
        "meses": int(len(ic)),
        "ic_medio": float(ic.mean()),
        "ic_std": float(ic.std(ddof=1)),
        "ic_ir_anualizado": float(ic.mean() / ic.std(ddof=1) * math.sqrt(12)),
        "ic_hit": float((ic > 0).mean()),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--db", default=os.path.join(here, "data", "sp500_replica.duckdb"))
    ap.add_argument("--out", default=os.path.join(here, "resultados"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    con = duckdb.connect(args.db, read_only=True)
    print(f"DB: {args.db}")

    resumen: dict[str, object] = {"db": args.db, "queries": {}, "extras": {}}

    # --- queries simples (con expansión de plantilla por columna de momentum) ---
    simple = ["short_term_reversal", "volatility_level", "volatility_compression",
              "dist_52w_high", "new_52w_high_event", "breakout_20d", "trend_sma",
              "volume_ratio", "market_regime", "composite_signal",
              "composite_by_period", "extreme_down_events", "monthly_signals",
              "seasonality"]

    for name in simple:
        sql = QUERIES[name]
        try:
            df = con.execute(sql).fetchdf()
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] {name}: {exc}")
            resumen["queries"][name] = {"error": str(exc)}
            continue
        df = add_wilson(df)
        df.to_csv(os.path.join(args.out, f"{name}.csv"), index=False)
        resumen["queries"][name] = df.to_dict(orient="records")
        print(f"[ok] {name:26s} filas={len(df)}")

    # --- momentum: 5 variantes ---
    mom_stats, ic_all, q_all = [], [], {}
    for col in ["mom_1m", "mom_3m", "mom_6m", "mom_12m", "mom_12_1"]:
        try:
            df = con.execute(QUERIES["momentum_quintiles"].replace("{MOM}", col)).fetchdf()
            df = add_wilson(df)
            df.to_csv(os.path.join(args.out, f"momentum_quintiles_{col}.csv"), index=False)
            q_all[col] = df.to_dict(orient="records")
            mom_stats.append(monthly_ls_stats(con, col))
            ic_all.append(ic_stats(con, col))
            print(f"[ok] momentum {col:10s} quintiles")
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] momentum {col}: {exc}")
    resumen["queries"]["momentum_quintiles"] = q_all
    resumen["extras"]["momentum_ls"] = mom_stats
    resumen["extras"]["momentum_ic"] = ic_all

    # --- autocorrelación: resumen agregado ---
    try:
        ac = con.execute(QUERIES["autocorrelation"]).fetchdf()
        ac.to_csv(os.path.join(args.out, "autocorrelation_por_simbolo.csv"), index=False)
        resumen["extras"]["autocorrelacion"] = {
            "n_simbolos": int(len(ac)),
            "ac1_diaria_media": float(ac["ac1_d"].mean()),
            "ac1_diaria_mediana": float(ac["ac1_d"].median()),
            "pct_ac1_diaria_negativa": float((ac["ac1_d"] < 0).mean()),
            "ac5_diaria_media": float(ac["ac5_d"].mean()),
            "ac1_mensual_media": float(ac["ac1_m"].mean()),
            "ac1_mensual_mediana": float(ac["ac1_m"].median()),
            "pct_ac1_mensual_negativa": float((ac["ac1_m"] < 0).mean()),
        }
        print(f"[ok] autocorrelacion  simbolos={len(ac)}")
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] autocorrelacion: {exc}")
        resumen["extras"]["autocorrelacion"] = {"error": str(exc)}

    # --- base rates (probabilidad incondicional) ---
    try:
        base = con.execute(f"""
            {PANEL}
            SELECT COUNT(*) n,
                   AVG(CASE WHEN fwd_21 > 0 THEN 1.0 ELSE 0 END) hit21,
                   AVG(CASE WHEN fwd_63 > 0 THEN 1.0 ELSE 0 END) hit63,
                   AVG(fwd_21) mean21, AVG(fwd_63) mean63,
                   AVG(CASE WHEN r_5d > 0 THEN 1.0 ELSE 0 END) hit5d
            FROM f WHERE fwd_21 IS NOT NULL AND fwd_63 IS NOT NULL
        """).fetchdf().to_dict(orient="records")[0]
        resumen["extras"]["base_rates"] = base
        print(f"[ok] base rates: {base}")
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] base rates: {exc}")

    with open(os.path.join(args.out, "resumen.json"), "w") as fh:
        json.dump(resumen, fh, indent=1, default=str)
    print(f"\nResultados en {args.out}/")


if __name__ == "__main__":
    main()
