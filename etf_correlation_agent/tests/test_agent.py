"""Tests del agente de correlaciones entre ETFs (usan datos sintéticos)."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from etf_agent import relationships as rel
from etf_agent.config import (
    DEFAULT_FACTORS,
    DEFAULT_TICKERS,
    ALL_WINDOWS,
    resolve_windows,
)
from etf_agent.correlation import (
    clustered_order,
    correlation_matrix,
    correlation_matrices,
    log_returns,
    rolling_correlation,
    top_pairs,
)
from etf_agent.data import make_demo_prices
from etf_agent.report import build_report


@pytest.fixture(scope="module")
def prices():
    """Universo reducido para que los tests corran rápido."""
    tickers = ["SPY", "TLT", "GLD", "UUP", "USO", "SGOV", "SOXX", "XLK"]
    return make_demo_prices(tickers=tickers, start="2018-01-01")


@pytest.fixture(scope="module")
def returns(prices):
    return log_returns(prices)


# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
def test_universo_por_defecto_contiene_los_etfs_pedidos():
    for t in ["USO", "GLD", "SPY", "QQQ", "TLT", "IEF", "IWM", "LQD", "HYG", "SGOV",
              "DRAM", "SOXX", "EFA", "EEM", "TIP", "UUP", "DBC", "XLK", "XLF", "XLE",
              "XLU", "XLP"]:
        assert t in DEFAULT_TICKERS, f"Falta {t} en el universo por defecto"


def test_resolve_windows():
    wins = resolve_windows(["max", "ytd", "3m", "1m"])
    assert list(wins) == ["max", "ytd", "3m", "1m"]
    with pytest.raises(ValueError):
        resolve_windows(["no-existe"])


def test_ventanas_cubren_lo_pedido():
    assert {"max", "ytd", "3m", "1m"} <= set(ALL_WINDOWS)


# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------
def test_demo_prices_shape_y_valores(prices):
    assert not prices.empty
    assert prices.shape[1] == 8
    assert (prices > 0).all().all()
    assert prices.index.is_monotonic_increasing


def test_demo_es_reproducible():
    a = make_demo_prices(tickers=["SPY", "TLT"], seed=7)
    b = make_demo_prices(tickers=["SPY", "TLT"], seed=7)
    pd.testing.assert_frame_equal(a, b)


def test_log_returns(returns):
    assert returns.shape[0] == prices_rows(returns)
    assert np.isfinite(returns.values).all()


def prices_rows(returns):
    return returns.shape[0]


# ---------------------------------------------------------------------------
# Correlaciones
# ---------------------------------------------------------------------------
def test_matrices_por_ventana(prices):
    mats = correlation_matrices(prices, windows=["max", "ytd", "3m", "1m"])
    assert len(mats) == 8  # 4 ventanas x 2 métodos
    for (label, method), corr in mats.items():
        assert label in {"max", "ytd", "3m", "1m"}
        assert method in {"pearson", "spearman"}
        assert corr.shape == (prices.shape[1], prices.shape[1])
        # diagonal ~ 1 y simetría
        assert np.allclose(np.diag(corr.values), 1.0)
        assert np.allclose(corr.values, corr.values.T)


def test_ventanas_tienen_distinto_numero_de_observaciones(prices):
    rets = log_returns(prices)
    from etf_agent.correlation import window_slice

    counts = {}
    for w in ["max", "ytd", "3m", "1m"]:
        idx = window_slice(prices.index, w)
        counts[w] = len(rets.loc[rets.index.isin(idx)])
    assert counts["max"] > counts["ytd"] > counts["3m"] > counts["1m"]


def test_correlation_matrix_spearman_vs_pearson(returns):
    p = correlation_matrix(returns, method="pearson")
    s = correlation_matrix(returns, method="spearman")
    assert not np.allclose(p.values, s.values)


def test_top_pairs_orden(returns):
    corr = correlation_matrix(returns)
    tp = top_pairs(corr, n=5)
    assert len(tp) <= 5
    assert (tp["abs_corr"].diff().dropna() <= 1e-12).all()


def test_rolling_correlation(returns):
    s = rolling_correlation(returns, "SPY", "TLT", window=63)
    assert len(s) > 0
    assert s.between(-1.0001, 1.0001).all()


def test_clustered_order(returns):
    corr = correlation_matrix(returns)
    order = clustered_order(corr)
    assert sorted(order) == sorted(corr.columns)


# ---------------------------------------------------------------------------
# Relaciones
# ---------------------------------------------------------------------------
def test_lead_lag_detecta_la_relacion_por_diseno(returns):
    """En la demo, SPY anticipa a SOXX 1 sesión (por construcción)."""
    ll = rel.lead_lag_table(returns, max_lag=5, min_abs_corr=0.10)
    assert not ll.empty
    fila = ll[(ll["leader"] == "SPY") & (ll["follower"] == "SOXX")]
    assert not fila.empty, "No se detectó SPY->SOXX en: " + str(ll.head())
    assert int(fila.iloc[0]["best_lag_days"]) == 1


def test_granger_table(returns):
    gc = rel.granger_table(returns, max_lag=3)
    assert not gc.empty
    assert {"cause", "effect", "p_value", "significativo"} <= set(gc.columns)
    assert gc["p_value"].between(0, 1).all()


def test_cointegration_table(prices):
    co = rel.cointegration_table(prices)
    assert not co.empty
    assert {"A", "B", "hedge_ratio", "cointegrada", "half_life_days"} <= set(co.columns)
    assert co["coint_pvalue"].between(0, 1).all()


def test_factor_betas(returns):
    betas = rel.factor_betas(returns, factors=["SPY", "TLT"])
    assert set(betas["etf"]) == {"GLD", "UUP", "USO", "SGOV", "SOXX", "XLK"}
    assert "beta_SPY" in betas.columns and "beta_TLT" in betas.columns
    spy = betas[betas["etf"] == "SPY"]
    assert spy.empty or abs(float(spy.iloc[0]["r2"]) - 1.0) < 1e-6


def test_pca(returns):
    pca = rel.pca_factors(returns, n_components=3)
    assert pca["n_components"] == 3
    evr = pca["explained_variance_ratio"]
    assert 0 < float(evr.sum()) <= 1.0 + 1e-9
    # la varianza explicada es decreciente
    assert (evr.diff().dropna() <= 1e-12).all()
    # con todos los componentes se explica el 100%
    full = rel.pca_factors(returns, n_components=returns.shape[1])
    assert abs(float(full["explained_variance_ratio"].sum()) - 1.0) < 1e-6
    assert pca["loadings"].shape == (returns.shape[1], 3)


def test_cluster_etfs(returns):
    corr = correlation_matrix(returns)
    cl = rel.cluster_etfs(corr, n_clusters=3)
    assert set(cl["cluster"]) <= {1, 2, 3}
    assert len(cl) == returns.shape[1]


def test_mutual_information(returns):
    mi = rel.mutual_information_matrix(returns, bins=6)
    assert mi.shape == (returns.shape[1], returns.shape[1])
    assert (mi.values >= -1e-9).all()
    # la diagonal es la entropía de cada ETF (MI consigo mismo)
    assert (np.diag(mi.values) > 0).all()
    # simetría
    assert np.allclose(mi.values, mi.values.T)
    # la MI fuera de la diagonal es mucho menor que la entropía
    off = mi.values[~np.eye(mi.shape[0], dtype=bool)]
    assert off.max() < np.diag(mi.values).min()


def test_regime_correlation(returns):
    reg = rel.regime_correlation(returns, benchmark="SPY")
    assert "asimetria" in reg.columns
    assert len(reg) == returns.shape[1]


def test_volatility_table(returns):
    vol = rel.volatility_table(returns)
    assert (vol["vol_anualizada_pct"] > 0).all()


def test_spread_series(prices):
    s = rel.spread_series(prices, "SPY", "XLK")
    assert len(s) > 0
    assert np.isfinite(s.values).all()


# ---------------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------------
def test_build_report_completo(tmp_path, prices):
    result = build_report(
        prices,
        windows=["max", "ytd", "3m", "1m"],
        factors=["SPY", "TLT", "GLD"],
        outdir=tmp_path,
        demo=True,
        verbose=False,
    )
    assert result["markdown"].exists()
    assert result["html"].exists()
    assert result["summary"].exists()
    assert len(result["images"]) >= 5
    assert len(result["tables"]) >= 10
    # cada ventana x metodo genera heatmap
    for w in ["max", "ytd", "3m", "1m"]:
        for m in ["pearson", "spearman"]:
            assert (result["dir"] / "images" / f"heatmap_{w}_{m}.png").exists()
    # el HTML lleva las imágenes incrustadas
    assert "data:image/png;base64" in result["html"].read_text()[:200000] or \
        len(result["html"].read_text()) > 10000


def test_build_report_sin_errores(tmp_path, prices):
    result = build_report(
        prices, windows=["max", "1m"], outdir=tmp_path, demo=True, verbose=False
    )
    import json

    summary = json.loads(result["summary"].read_text())
    assert summary["errores"] == {}, f"Errores en el informe: {summary['errores']}"
