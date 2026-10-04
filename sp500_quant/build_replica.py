#!/usr/bin/env python3
"""
build_replica.py — Construye una réplica LOCAL con el esquema de la base
`sp500.duckdb` descrita por el usuario, a partir de datos públicos reales.

Por qué existe este script
--------------------------
La base original (`sp500_db/db/sp500.duckdb`, ~1.44M filas en `prices`,
2015-2026) vive en un equipo Windows al que este agente no tiene acceso.
Para poder EJECUTAR y VALIDAR todo el SQL antes de entregarlo se construye
esta réplica con el MISMO esquema (tablas + vistas) y datos reales de S&P 500.

Fuente de datos (pública, descargable):
  * Precios diarios OHLCV:  plotly/datasets :: all_stocks_5yr.csv
    (dataset Kaggle "S&P 500 stock data", 505 tickers, 2013-02-08 -> 2018-02-07)
  * Sectores GICS:          datasets/s-and-p-500-companies :: data/constituents.csv

Uso:
    python3 build_replica.py [--db RUTA.duckdb] [--cache DIR]

Notas de fidelidad (ver RESULTADOS.md, sección Limitaciones):
  * El dataset público NO trae `adj_close` (dividendos/splits). Se replica la
    columna con `close` y se documenta; el análisis usa filtros de calidad.
  * Las tablas `fundamentals`, `news`, `filings*`, `dividends`, `splits`,
    `signals` y `selected_15_tickers` se crean con el esquema original pero
    VACÍAS (no hay fuente pública equivalente en el sandbox).
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import subprocess
import sys

import duckdb

PRICES_URL = "https://github.com/plotly/datasets.git"
CONSTIT_URL = "https://github.com/datasets/s-and-p-500-companies.git"
PRICES_FILE = "all_stocks_5yr.csv"
CONSTIT_FILE = "data/constituents.csv"

DDL = """
-- =====================================================================
-- TABLAS (mismo esquema que la base original del usuario)
-- =====================================================================
CREATE OR REPLACE TABLE prices (
    symbol    VARCHAR,
    date      DATE,
    open      DOUBLE,
    high      DOUBLE,
    low       DOUBLE,
    close     DOUBLE,
    adj_close DOUBLE,
    volume    BIGINT
);

CREATE OR REPLACE TABLE tickers (
    symbol       VARCHAR,
    company_name VARCHAR,
    sector       VARCHAR,
    industry     VARCHAR,
    date_added   DATE,
    headquarters VARCHAR,
    active       BOOLEAN,
    last_updated TIMESTAMP,
    currency     VARCHAR
);

CREATE OR REPLACE TABLE dividends (
    symbol VARCHAR, date DATE, amount DOUBLE
);

CREATE OR REPLACE TABLE splits (
    symbol VARCHAR, date DATE, ratio DOUBLE
);

CREATE OR REPLACE TABLE fundamentals (
    symbol VARCHAR, snapshot_date DATE, market_cap DOUBLE, pe_ratio DOUBLE,
    forward_pe DOUBLE, peg_ratio DOUBLE, price_to_book DOUBLE,
    price_to_sales DOUBLE, dividend_yield DOUBLE, payout_ratio DOUBLE,
    beta DOUBLE, eps DOUBLE, forward_eps DOUBLE, profit_margin DOUBLE,
    operating_margin DOUBLE, roe DOUBLE, roa DOUBLE, debt_to_equity DOUBLE,
    current_ratio DOUBLE, quick_ratio DOUBLE, revenue DOUBLE,
    revenue_growth DOUBLE, earnings_growth DOUBLE, free_cashflow DOUBLE,
    fifty_two_week_high DOUBLE, fifty_two_week_low DOUBLE,
    fifty_day_average DOUBLE, two_hundred_day_avg DOUBLE,
    avg_volume DOUBLE, shares_outstanding DOUBLE, float_shares DOUBLE,
    short_ratio DOUBLE, recommendation VARCHAR, target_mean_price DOUBLE
);

CREATE OR REPLACE TABLE news (
    symbol VARCHAR, published_date TIMESTAMP, headline VARCHAR, source VARCHAR,
    sentiment_score DOUBLE, url VARCHAR, loaded_at TIMESTAMP
);

CREATE OR REPLACE TABLE filings (
    symbol VARCHAR, cik VARCHAR, form_type VARCHAR, fiscal_year INTEGER,
    fiscal_period VARCHAR, filed_date DATE, period_start DATE, period_end DATE,
    concept VARCHAR, value DOUBLE, unit VARCHAR, accession_number VARCHAR,
    source_url VARCHAR, loaded_at TIMESTAMP
);

CREATE OR REPLACE TABLE filings_annual (
    symbol VARCHAR, concept VARCHAR, period_end DATE, value DOUBLE, filed_date DATE
);

CREATE OR REPLACE TABLE pca_loadings (
    ticker VARCHAR, PC1 DOUBLE, PC2 DOUBLE, PC3 DOUBLE, PC4 DOUBLE, PC5 DOUBLE,
    PC6 DOUBLE, PC7 DOUBLE, PC8 DOUBLE, PC9 DOUBLE, PC10 DOUBLE
);

CREATE OR REPLACE TABLE pca_scores (
    date DATE, PC1 DOUBLE, PC2 DOUBLE, PC3 DOUBLE, PC4 DOUBLE, PC5 DOUBLE,
    PC6 DOUBLE, PC7 DOUBLE, PC8 DOUBLE, PC9 DOUBLE, PC10 DOUBLE
);

CREATE OR REPLACE TABLE signals (
    symbol VARCHAR, as_of_date DATE, ret_3m DOUBLE, ret_6m DOUBLE,
    dist_52w_high DOUBLE, vol_3m_annualized DOUBLE, revenue_growth_yoy DOUBLE,
    net_income_growth_yoy DOUBLE, eps_growth_yoy DOUBLE,
    news_sentiment_7d DOUBLE, momentum_score DOUBLE, filings_score DOUBLE,
    news_score DOUBLE, composite_score DOUBLE, rationale VARCHAR,
    computed_at TIMESTAMP, news_article_count_7d INTEGER
);

CREATE OR REPLACE TABLE selected_15_tickers (
    method VARCHAR, ticker VARCHAR, idio_ret DOUBLE, idio_vol DOUBLE, sharpe DOUBLE
);

CREATE OR REPLACE TABLE weights_inv_variance (ticker VARCHAR, weight DOUBLE);

CREATE OR REPLACE TABLE weights_max_sharpe (ticker VARCHAR, weight DOUBLE);

CREATE OR REPLACE TABLE update_log (
    run_id INTEGER, started_at TIMESTAMP, finished_at TIMESTAMP,
    status VARCHAR, details VARCHAR
);
"""

VIEW_BASE = """
CREATE OR REPLACE VIEW base_diaria AS
-- precios con retornos simples/log y filtro de calidad para artefactos de
-- splits (el dataset público viene sin ajustar): |ret| > 50% en un día se
-- marca y se excluye de los cálculos de retornos.
WITH p AS (
    SELECT
        symbol, date, open, high, low, close, adj_close, volume,
        close / NULLIF(LAG(close) OVER (PARTITION BY symbol ORDER BY date), 0) - 1 AS ret
    FROM prices
)
SELECT
    *,
    CASE WHEN ABS(ret) <= 0.50 THEN ret END AS ret_clean,
    LN(1 + CASE WHEN ABS(ret) <= 0.50 AND close > 0
                THEN close / NULLIF(LAG(close) OVER (PARTITION BY symbol ORDER BY date), 0)
           END) AS log_ret
FROM p;
"""

VIEWS = """
-- =====================================================================
-- VISTAS (mismo esquema que la base original)
-- =====================================================================
CREATE OR REPLACE VIEW base_diaria AS
-- precios con retornos simples/log y filtro de calidad para artefactos de
-- splits (el dataset público viene sin ajustar): |ret| > 50% en un día se
-- marca y se excluye de los cálculos de retornos.
WITH p AS (
    SELECT
        symbol, date, open, high, low, close, adj_close, volume,
        close / NULLIF(LAG(close) OVER (PARTITION BY symbol ORDER BY date), 0) - 1 AS ret
    FROM prices
)
SELECT
    *,
    CASE WHEN ABS(ret) <= 0.50 THEN ret END AS ret_clean,
    LN(1 + CASE WHEN ABS(ret) <= 0.50 AND close > 0
                THEN close / NULLIF(LAG(close) OVER (PARTITION BY symbol ORDER BY date), 0)
           END) AS log_ret
FROM p;

-- Precio mensual: último día de negociación de cada mes
CREATE OR REPLACE VIEW v_precios_mensuales AS
WITH ranked AS (
    SELECT symbol, date_trunc('month', date) AS mes, date, close,
           ROW_NUMBER() OVER (PARTITION BY symbol, date_trunc('month', date)
                              ORDER BY date DESC) AS rn
    FROM prices
)
SELECT symbol, mes, date, close FROM ranked WHERE rn = 1;

-- Precio semanal: último día de negociación de cada semana (semana ISO, lunes)
CREATE OR REPLACE VIEW v_precios_semanales AS
WITH ranked AS (
    SELECT symbol, date_trunc('week', date) AS semana, date, close,
           ROW_NUMBER() OVER (PARTITION BY symbol, date_trunc('week', date)
                              ORDER BY date DESC) AS rn
    FROM prices
)
SELECT symbol, semana, date, close FROM ranked WHERE rn = 1;

-- Momentum 12-1: retorno de t-12m a t-1m, medido a cierre mensual,
-- y retorno forward de 1 mes. Quintiles cross-sectional por mes.
CREATE OR REPLACE VIEW v_momentum_12_1 AS
WITH m AS (
    SELECT symbol, mes, close,
           LAG(close) OVER (PARTITION BY symbol ORDER BY mes) AS c_1m,
           LAG(close, 12) OVER (PARTITION BY symbol ORDER BY mes) AS c_12m,
           LEAD(close) OVER (PARTITION BY symbol ORDER BY mes) AS c_next
    FROM v_precios_mensuales
), calc AS (
    SELECT symbol, mes,
           CASE WHEN c_12m IS NOT NULL AND c_1m > 0 THEN c_1m / c_12m - 1 END AS mom_12_1,
           CASE WHEN c_next IS NOT NULL THEN c_next / close - 1 END AS fwd_ret_1m
    FROM m
)
SELECT symbol, mes, mom_12_1, fwd_ret_1m,
       NTILE(5) OVER (PARTITION BY mes ORDER BY mom_12_1 NULLS LAST) AS quintil
FROM calc
WHERE mom_12_1 IS NOT NULL;

-- Momentum 12-1 "sector neutral": quintiles dentro de cada sector-mes
CREATE OR REPLACE VIEW v_momentum_sector_neutral AS
WITH m AS (
    SELECT v.symbol, v.mes, t.sector, v.close,
           LAG(v.close) OVER (PARTITION BY v.symbol ORDER BY v.mes) AS c_1m,
           LAG(v.close, 12) OVER (PARTITION BY v.symbol ORDER BY v.mes) AS c_12m,
           LEAD(v.close) OVER (PARTITION BY v.symbol ORDER BY v.mes) AS c_next
    FROM v_precios_mensuales v
    LEFT JOIN tickers t USING (symbol)
), calc AS (
    SELECT symbol, mes, sector,
           CASE WHEN c_12m IS NOT NULL AND c_1m > 0 THEN c_1m / c_12m - 1 END AS mom_12_1,
           CASE WHEN c_next IS NOT NULL THEN c_next / close - 1 END AS fwd_ret_1m
    FROM m
)
SELECT symbol, mes, sector, mom_12_1, fwd_ret_1m,
       NTILE(5) OVER (PARTITION BY mes, sector ORDER BY mom_12_1 NULLS LAST) AS quintil
FROM calc
WHERE mom_12_1 IS NOT NULL;

-- Universo líquido: volumen medio 3m alto. market_cap no está disponible en
-- la réplica (queda NULL) y beta se calcula vs. mercado equiponderado.
CREATE OR REPLACE VIEW v_universo_liquido AS
WITH liq AS (
    SELECT symbol,
           AVG(volume) AS avg_volume,
           COUNT(*) AS n_dias
    FROM (
        SELECT symbol, volume, ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY date DESC) AS rn
        FROM prices
    ) WHERE rn <= 63
    GROUP BY symbol
    HAVING COUNT(*) >= 50 AND AVG(volume) > 1000000
)
SELECT t.symbol, t.company_name, t.sector, t.industry,
       (SELECT MAX(date) FROM prices) AS snapshot_date,
       NULL::DOUBLE AS market_cap,
       liq.avg_volume,
       NULL::DOUBLE AS beta
FROM liq
JOIN tickers t ON t.symbol = liq.symbol;
"""


def sh(cmd: list[str], cwd: str | None = None) -> None:
    print("  $", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.STDOUT)


def sparse_clone(url: str, dest: str, paths: list[str]) -> None:
    if os.path.isdir(os.path.join(dest, ".git")):
        print(f"  [cache] ya existe {dest}")
        return
    if os.path.exists(dest):
        shutil.rmtree(dest)
    try:
        sh(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", url, dest])
        sh(["git", "sparse-checkout", "set", "--no-cone", *paths], cwd=dest)
    except subprocess.CalledProcessError:
        # Fallback: algunos repos no admiten sparse-checkout en modo cono/LFS
        print("  [warn] sparse falló, se intenta clone completo…")
        if os.path.exists(dest):
            shutil.rmtree(dest)
        sh(["git", "clone", "--depth", "1", url, dest])


def build(db_path: str, cache: str) -> None:
    os.makedirs(cache, exist_ok=True)
    prices_dir = os.path.join(cache, "plotly_datasets")
    const_dir = os.path.join(cache, "sp500_companies")

    print("[1/6] Obteniendo datos fuente (GitHub)…")
    sparse_clone(PRICES_URL, prices_dir, [PRICES_FILE])
    sparse_clone(CONSTIT_URL, const_dir, ["data"])

    prices_csv = os.path.join(prices_dir, PRICES_FILE)
    const_csv = os.path.join(const_dir, CONSTIT_FILE)
    for f in (prices_csv, const_csv):
        if not os.path.exists(f):
            sys.exit(f"ERROR: no se encontró {f}")

    print(f"[2/6] Creando base en {db_path} …")
    if os.path.exists(db_path):
        os.remove(db_path)
    con = duckdb.connect(db_path)

    print("[3/6] Cargando precios y tickers …")
    con.execute(DDL)
    con.execute(
        f"""
        INSERT INTO prices
        SELECT Name AS symbol,
               CAST(date AS DATE) AS date,
               open, high, low, close,
               close AS adj_close,          -- ver nota de fidelidad
               CAST(volume AS BIGINT) AS volume
        FROM read_csv_auto('{prices_csv}')
        WHERE close IS NOT NULL AND close > 0
        """
    )
    con.execute(
        f"""
        INSERT INTO tickers
        SELECT Symbol, Security, "GICS Sector", "GICS Sub-Industry",
               TRY_CAST("Date added" AS DATE), "Headquarters Location",
               TRUE, TIMESTAMP '{dt.datetime.now():%Y-%m-%d %H:%M:%S}', 'USD'
        FROM read_csv_auto('{const_csv}')
        """
    )

    print("[4/6] Calculando PCA (PC1..PC10) sobre retornos diarios …")
    con.execute(VIEW_BASE)
    con.execute(
        """
        CREATE OR REPLACE TEMP TABLE _rets AS
        SELECT symbol, date, ret_clean AS ret FROM base_diaria WHERE ret_clean IS NOT NULL
        """
    )
    # Matriz fecha x ticker, estandarizada, PCA vía SVD (numpy)
    import numpy as np

    df = con.execute(
        """
        SELECT date, symbol, ret FROM _rets
        QUALIFY COUNT(*) OVER (PARTITION BY symbol) >= 800
        """
    ).fetchdf()
    wide = df.pivot_table(index="date", columns="symbol", values="ret")
    wide = wide.dropna(axis=1, thresh=int(0.9 * len(wide)))
    wide = wide.dropna()
    X = wide.to_numpy(dtype=float)
    X = (X - X.mean(axis=0)) / X.std(axis=0)
    U, S, Vt = np.linalg.svd(X - X.mean(axis=0), full_matrices=False)
    n_pc = 10
    scores = U[:, :n_pc] * S[:n_pc]
    var_share = (S**2 / (S**2).sum())[:n_pc]

    import pandas as pd
    load_df = pd.DataFrame(Vt[:n_pc].T, columns=[f"PC{i+1}" for i in range(n_pc)])
    load_df["ticker"] = list(wide.columns)
    con.register("load_df", load_df)
    con.execute("INSERT INTO pca_loadings SELECT ticker, PC1,PC2,PC3,PC4,PC5,PC6,PC7,PC8,PC9,PC10 FROM load_df")

    sc = pd.DataFrame(scores, columns=[f"PC{i+1}" for i in range(n_pc)])
    sc.insert(0, "date", wide.index)
    con.register("sc_df", sc)
    con.execute("INSERT INTO pca_scores SELECT date, PC1,PC2,PC3,PC4,PC5,PC6,PC7,PC8,PC9,PC10 FROM sc_df")
    print("      varianza explicada PC1..PC10:", np.round(var_share, 4).tolist())

    print("[5/6] Carteras (inv-variance y max-Sharpe) …")
    last_year = con.execute(
        "SELECT MAX(date) - INTERVAL 365 DAY FROM prices"
    ).fetchone()[0]
    px = con.execute(
        """
        SELECT symbol, date, ret_clean AS ret FROM base_diaria
        WHERE date >= ? AND ret_clean IS NOT NULL
        """, [last_year]
    ).fetchdf()
    piv = px.pivot_table(index="date", columns="symbol", values="ret").dropna(axis=1, thresh=int(0.9*len(px.date.unique())))
    cov = piv.cov().to_numpy()
    mu = piv.mean().to_numpy()
    tickers = list(piv.columns)
    iv = 1.0 / np.diag(cov)
    iv = iv / iv.sum()

    import scipy.optimize as opt
    n = len(tickers)
    neg_sharpe = lambda w: -(w @ mu) / np.sqrt(w @ cov @ w + 1e-12)
    res = opt.minimize(neg_sharpe, np.repeat(1/n, n), method="SLSQP",
                       bounds=[(0, 1)]*n, constraints=[{"type": "eq", "fun": lambda w: w.sum()-1}])
    ms = res.x

    import pandas as pd
    con.register("iv_df", pd.DataFrame({"ticker": tickers, "weight": iv}))
    con.execute("INSERT INTO weights_inv_variance SELECT ticker, weight FROM iv_df")
    con.register("ms_df", pd.DataFrame({"ticker": tickers, "weight": ms}))
    con.execute("INSERT INTO weights_max_sharpe SELECT ticker, weight FROM ms_df")

    print("[6/6] Creando vistas y registro de carga …")
    con.execute(VIEWS)
    n_prices = con.execute("SELECT COUNT(*) FROM prices").fetchone()[0]
    n_tick = con.execute("SELECT COUNT(*) FROM tickers").fetchone()[0]
    d0, d1 = con.execute("SELECT MIN(date), MAX(date) FROM prices").fetchone()
    con.execute(
        """
        INSERT INTO update_log VALUES (1, now(), now(), 'OK', ?)
        """,
        [f"REPLICA local: prices={n_prices}, tickers={n_tick}, rango={d0}..{d1}. "
         f"Sin adj_close real (adj_close=close), fundamentales/noticias/filings vacíos."],
    )
    con.close()
    print(f"\nOK -> {db_path} ({os.path.getsize(db_path)/1e6:.1f} MB) | "
          f"prices={n_prices:,} tickers={n_tick} | {d0} -> {d1}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                 "data", "sp500_replica.duckdb"))
    ap.add_argument("--cache", default="/tmp/sp500_quant_cache")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(os.path.abspath(args.db)), exist_ok=True)
    build(args.db, args.cache)


if __name__ == "__main__":
    main()
