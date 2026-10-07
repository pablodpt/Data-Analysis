from __future__ import annotations

import numpy as np
import pandas as pd

from quant_research.backtest import backtest_positions
from quant_research.discovery import (
    Condition,
    benjamini_hochberg,
    build_candidate_combinations,
    build_conditions,
    hac_directional_test,
)
from quant_research.exploration import structural_shift_tests
from quant_research.features import build_features
from quant_research.io import standardize_ohlcv


def test_benjamini_hochberg_preserves_order_and_controls_values():
    p_values = np.array([0.04, 0.001, 0.03, np.nan])
    q_values = benjamini_hochberg(p_values)
    assert np.allclose(q_values[:3], [0.04, 0.003, 0.04])
    assert q_values[3] == 1.0


def test_rule_combinations_require_distinct_families():
    conditions = [
        Condition("m1", "r1", "momentum", np.array([1, 0], dtype=bool), "fixed"),
        Condition("m2", "r2", "momentum", np.array([1, 1], dtype=bool), "fixed"),
        Condition("v1", "vol", "volatility", np.array([0, 1], dtype=bool), "fixed"),
        Condition("t1", "trend", "trend", np.array([1, 1], dtype=bool), "fixed"),
    ]
    combos = build_candidate_combinations(conditions, max_conditions=3)
    assert any(np.array_equal(row[:2], [0, 2]) for row in combos if row[2] == -1)
    assert not any(set(row[row >= 0].tolist()) == {0, 1} for row in combos)
    assert any(set(row[row >= 0].tolist()) == {0, 2, 3} for row in combos)


def test_discovery_quantiles_are_fit_from_train_only():
    n = 2000
    index = pd.bdate_range("2010-01-01", periods=n)
    values = np.linspace(-1, 1, n)
    frame = pd.DataFrame({"return_1d": values}, index=index)
    close = pd.Series(np.arange(1, n + 1, dtype=float), index=index)
    train = np.arange(n) < 1400
    conditions = build_conditions(frame, close, train, min_cases=100)
    upper = next(c for c in conditions if c.feature == "return_1d" and "Q90" in c.name)
    assert upper.threshold < values[1399]
    assert upper.threshold < 0.5  # a full-sample Q90 would be close to 0.8
    assert upper.mask[1999]


def test_feature_targets_are_forward_and_indicators_are_trailing():
    n = 260
    index = pd.bdate_range("2010-01-01", periods=n)
    close = 100 * np.cumprod(1 + np.full(n, 0.001))
    raw = pd.DataFrame({
        "close": close,
        "adj_close": np.nan,
        "open": close * (1 - 0.001),
        "high": close * 1.01,
        "low": close * 0.99,
        "volume": np.full(n, 1000.0),
    }, index=index)
    features, targets, analyzed = build_features(raw)
    assert np.isclose(features.loc[index[220], "return_1d"], 0.001, atol=1e-9)
    assert targets.loc[index[-1], "forward_return_1d"] != targets.loc[index[-1], "forward_return_1d"]
    assert np.isfinite(features.loc[index[-1], "sma_200d"])
    # Changing a future price must not change the indicator at t.
    changed = raw.copy()
    changed.loc[index[250], "close"] *= 3
    changed_features, _, _ = build_features(changed)
    assert features.loc[index[220], "sma_200d"] == changed_features.loc[index[220], "sma_200d"]


def test_hac_test_detects_positive_hit_rate_difference():
    rng = np.random.default_rng(3)
    signal = np.tile([0, 1], 500)
    hit = rng.binomial(1, 0.5, len(signal)).astype(float)
    hit[signal == 1] = rng.binomial(1, 0.72, int(signal.sum()))
    beta, p_value, _ = hac_directional_test(hit, signal, max_lag=5)
    assert beta > 0
    assert p_value < 0.05


def test_backtest_delays_signal_two_rows_for_next_open_to_open_execution():
    index = pd.bdate_range("2020-01-01", periods=5)
    prices = pd.DataFrame({
        "open": [100.0, 101.0, 103.0, 105.0, 106.0],
        "close": [101.0, 102.0, 104.0, 106.0, 107.0],
        "adj_close": [np.nan] * 5,
    }, index=index)
    signal = pd.Series([1.0, 0.0, 0.0, 0.0, 0.0], index=index)
    _, pnl = backtest_positions(prices, signal, cost_bps=0.0)
    assert pnl.loc[index[2], "position"] == 1.0
    assert np.isclose(pnl.loc[index[2], "market_return"], 103 / 101 - 1)
    assert pnl.loc[index[1], "position"] == 0.0


def test_horizon_backtest_averages_overlapping_daily_vintages():
    index = pd.bdate_range("2020-01-01", periods=9)
    prices = pd.DataFrame({
        "open": np.arange(100.0, 109.0),
        "close": np.arange(101.0, 110.0),
        "adj_close": [np.nan] * 9,
    }, index=index)
    signal = pd.Series(0.0, index=index)
    signal.iloc[0] = 1.0
    _, pnl = backtest_positions(prices, signal, cost_bps=0.0, holding_horizon=2)
    assert pnl.loc[index[2], "position"] == 0.5
    assert pnl.loc[index[3], "position"] == 0.5
    assert pnl.loc[index[4], "position"] == 0.0


def test_standardize_uses_adjusted_close_when_raw_close_missing():
    original = pd.DataFrame({
        "Date": ["2020-01-02", "2020-01-03"],
        "Close": [np.nan, 101.0],
        "Adj Close": [100.0, 101.0],
    })
    standardized, mapping, stats = standardize_ohlcv(original)
    assert len(standardized) == 2
    assert standardized["close"].iloc[0] != standardized["close"].iloc[0]
    assert standardized["adj_close"].iloc[0] == 100.0
    assert stats["rows_removed_bad_close"] == 0
    assert mapping["adj_close"] == "Adj Close"


def test_structural_shift_diagnostics_include_holm_adjustment():
    index = pd.bdate_range("2000-01-01", periods=500)
    returns = np.r_[np.full(250, 0.001), np.full(250, -0.001)]
    close = pd.Series(100.0 * np.cumprod(1.0 + returns), index=index)
    tests = structural_shift_tests(close)
    assert len(tests) == 3
    assert "p_value_holm" in tests
    assert np.all(tests["p_value_holm"] >= tests["p_value"])
