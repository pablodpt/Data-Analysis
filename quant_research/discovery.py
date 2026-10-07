"""Large-scale, train-only rule mining and independent holdout validation."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
import math
from typing import Any

import numpy as np
import pandas as pd

from .backtest import backtest_positions
from .features import CONTINUOUS_PATTERN_FEATURES, FEATURE_GROUPS


MIN_CASES = 100
DISCOVERY_HORIZONS = (1, 3, 5)


@dataclass
class Condition:
    name: str
    feature: str
    family: str
    mask: np.ndarray
    kind: str
    threshold: float | None = None


def benjamini_hochberg(p_values: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values, retaining input order."""
    p = np.asarray(p_values, dtype=float)
    q = np.ones(p.shape, dtype=float)
    valid = np.isfinite(p) & (p >= 0.0) & (p <= 1.0)
    if not valid.any():
        return q
    selected = p[valid]
    order = np.argsort(selected, kind="mergesort")
    ranked = selected[order]
    m = len(ranked)
    adjusted = ranked * m / np.arange(1, m + 1, dtype=float)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    restored = np.empty_like(adjusted)
    restored[order] = np.clip(adjusted, 0.0, 1.0)
    q[valid] = restored
    return q


def _normal_sf(z: np.ndarray) -> np.ndarray:
    try:
        from scipy.special import ndtr
        return ndtr(-np.asarray(z, dtype=float))
    except ImportError:
        values = np.asarray(z, dtype=float)
        return np.vectorize(lambda value: 0.5 * math.erfc(value / math.sqrt(2.0)))(values)


def _binomial_score_pvalue(successes: np.ndarray, counts: np.ndarray, baseline: float) -> np.ndarray:
    """One-sided binomial score approximation used only for candidate screening."""
    successes = np.asarray(successes, dtype=float)
    counts = np.asarray(counts, dtype=float)
    out = np.full(counts.shape, np.nan, dtype=float)
    if not (0.0 < baseline < 1.0):
        return out
    valid = (counts >= MIN_CASES) & (successes >= 0) & (successes <= counts)
    if valid.any():
        se = np.sqrt(baseline * (1.0 - baseline) / counts[valid])
        z = (successes[valid] / counts[valid] - baseline) / se
        out[valid] = _normal_sf(z)
    return out


def hac_directional_test(y: np.ndarray, signal: np.ndarray, max_lag: int) -> tuple[float, float, float]:
    """HAC/Newey-West test that signal days improve a binary hit rate.

    OLS of hit ~ constant + signal makes the slope exactly the hit-rate
    difference between triggered and non-triggered observations. HAC standard
    errors account for short-run serial dependence and overlapping horizons.
    Returns (slope, one-sided p-value, t-statistic).
    """
    y = np.asarray(y, dtype=float)
    x = np.asarray(signal, dtype=float)
    valid = np.isfinite(y) & np.isfinite(x)
    y, x = y[valid], x[valid]
    if len(y) < 20 or x.min(initial=0.0) == x.max(initial=0.0):
        return np.nan, 1.0, np.nan
    design = np.column_stack([np.ones(len(x)), x])
    xtx = design.T @ design
    try:
        bread = np.linalg.inv(xtx)
    except np.linalg.LinAlgError:
        return np.nan, 1.0, np.nan
    beta = bread @ (design.T @ y)
    residual = y - design @ beta
    scores = design * residual[:, None]
    meat = scores.T @ scores
    max_lag = min(max(0, int(max_lag)), len(y) - 1)
    for lag in range(1, max_lag + 1):
        weight = 1.0 - lag / (max_lag + 1.0)
        cross = scores[lag:].T @ scores[:-lag]
        meat += weight * (cross + cross.T)
    covariance = bread @ meat @ bread
    standard_error = float(np.sqrt(max(covariance[1, 1], 0.0)))
    if not np.isfinite(standard_error) or standard_error <= 1e-15:
        return float(beta[1]), 1.0, np.nan
    t_stat = float(beta[1] / standard_error)
    p_value = float(_normal_sf(np.asarray([t_stat]))[0])
    return float(beta[1]), p_value, t_stat


def _group_for_feature(name: str) -> str:
    return FEATURE_GROUPS.get(name, "seasonality")


def build_conditions(
    features: pd.DataFrame,
    close: pd.Series,
    discovery_mask: np.ndarray,
    min_cases: int = MIN_CASES,
) -> list[Condition]:
    """Create fixed and discovery-quantile rule atoms.

    Quantiles are fit only on the pre-cutoff discovery segment. Each atom is
    then applied to the full timeline, including untouched holdout dates.
    """
    n = len(features)
    discovery_mask = np.asarray(discovery_mask, dtype=bool)
    train_n = int(discovery_mask.sum())
    conditions: list[Condition] = []
    seen_masks: set[bytes] = set()

    def add(name: str, feature: str, family: str, values: Any, kind: str, threshold: float | None = None) -> None:
        arr = np.asarray(values)
        if arr.ndim == 0 or arr.shape[0] != n:
            return
        if arr.dtype != bool:
            arr = pd.to_numeric(pd.Series(arr), errors="coerce").fillna(0).to_numpy(dtype=bool)
        else:
            arr = np.nan_to_num(arr.astype(bool), nan=False)
        active_n = int(arr[discovery_mask].sum())
        if active_n < min_cases or active_n > int(train_n * 0.95):
            return
        key = np.packbits(arr, bitorder="little").tobytes()
        if key in seen_masks:
            return
        seen_masks.add(key)
        conditions.append(Condition(name, feature, family, arr, kind, threshold))

    # Canonical, interpretable events included before generic quantile atoms.
    r1 = features.get("return_1d", pd.Series(np.nan, index=features.index))
    for streak in (3, 5):
        up = r1.gt(0).rolling(streak, min_periods=streak).sum().eq(streak)
        down = r1.lt(0).rolling(streak, min_periods=streak).sum().eq(streak)
        add(f"{streak} sesiones alcistas consecutivas", f"streak_up_{streak}", "momentum", up, "fijo")
        add(f"{streak} sesiones bajistas consecutivas", f"streak_down_{streak}", "momentum", down, "fijo")
    ret3 = features.get("return_3d", pd.Series(np.nan, index=features.index))
    for threshold in (-0.03, -0.05):
        add(f"Caída 3d ≤ {threshold:.0%}", f"return_3d_le_{threshold}", "momentum", ret3.le(threshold), "fijo", threshold)
    rsi = features.get("rsi_14", pd.Series(np.nan, index=features.index))
    add("RSI(14) < 30", "rsi_14_below_30", "momentum", rsi.lt(30), "fijo", 30.0)
    add("RSI(14) > 70", "rsi_14_above_70", "momentum", rsi.gt(70), "fijo", 70.0)
    for w in (20, 50):
        if w in (20, 50):
            previous_high = close.shift(1).rolling(w, min_periods=w).max()
            previous_low = close.shift(1).rolling(w, min_periods=w).min()
            add(f"Nuevo máximo de cierre {w}d", f"close_breakout_high_{w}", "trend", close.gt(previous_high), "fijo")
            add(f"Nuevo mínimo de cierre {w}d", f"close_breakout_low_{w}", "trend", close.lt(previous_low), "fijo")
    if "dist_sma_200d" in features:
        dist200 = features["dist_sma_200d"]
        add("Precio sobre SMA(200)", "above_sma_200", "trend", dist200.gt(0), "fijo", 0.0)
        add("Precio bajo SMA(200)", "below_sma_200", "trend", dist200.lt(0), "fijo", 0.0)
    if "volume_spike" in features:
        add("Volumen > 2× media 20d", "volume_spike", "volume", features["volume_spike"].eq(1), "fijo", 2.0)
    dow = features.get("day_of_week", pd.Series(np.nan, index=features.index))
    previous_return = r1.shift(1)
    previous_dow = dow.shift(1)
    monday_after_down_friday = dow.eq(0) & previous_dow.eq(4) & previous_return.lt(0)
    add("Lunes tras viernes bajista", "monday_after_down_friday", "seasonality", monday_after_down_friday, "fijo")
    add("Pre-cierre festivo observado", "pre_holiday", "seasonality", features.get("pre_holiday", False), "fijo")
    add("Post-cierre festivo observado", "post_holiday", "seasonality", features.get("post_holiday", False), "fijo")
    add("Primeras 3 sesiones del mes", "month_start_3", "seasonality", features.get("month_start_3", pd.Series(False, index=features.index)).astype(bool), "fijo")
    add("Últimas 3 sesiones del mes", "month_end_3", "seasonality", features.get("month_end_3", pd.Series(False, index=features.index)).astype(bool), "fijo")

    # Calendar-only hypotheses; sparse weekdays/months are removed by MIN_CASES.
    for weekday in range(5):
        add(f"Día de semana = {weekday} (lunes=0)", f"weekday_{weekday}", "seasonality", dow.eq(weekday), "fijo", float(weekday))
    month = features.get("month_of_year", pd.Series(np.nan, index=features.index))
    for month_number in range(1, 13):
        add(f"Mes calendario = {month_number}", f"month_{month_number}", "seasonality", month.eq(month_number), "fijo", float(month_number))

    # Quantile thresholds from the discovery period only: two lower-tail and
    # two upper-tail cutoffs per feature. Keep an explicit definition in CSV.
    for feature in CONTINUOUS_PATTERN_FEATURES:
        if feature not in features:
            continue
        train_values = pd.to_numeric(features.loc[discovery_mask, feature], errors="coerce").dropna()
        if train_values.nunique() < 5:
            continue
        for quantile, direction in ((0.10, "le"), (0.25, "le"), (0.75, "ge"), (0.90, "ge")):
            cutoff = float(train_values.quantile(quantile))
            series = pd.to_numeric(features[feature], errors="coerce")
            condition = series.le(cutoff) if direction == "le" else series.ge(cutoff)
            symbol = "≤" if direction == "le" else "≥"
            name = f"{feature} {symbol} Q{int(quantile * 100)} ({cutoff:.5g})"
            add(name, feature, _group_for_feature(feature), condition, f"Q{int(quantile * 100)}", cutoff)
    return conditions


def build_candidate_combinations(conditions: list[Condition], max_conditions: int = 4) -> np.ndarray:
    """Generate singles and distinct-family conjunctions up to `max_conditions`."""
    by_family: dict[str, list[int]] = {}
    for i, condition in enumerate(conditions):
        by_family.setdefault(condition.family, []).append(i)
    families = list(by_family)
    combos: list[tuple[int, ...]] = [(i,) for i in range(len(conditions))]
    for size in range(2, min(max_conditions, len(families)) + 1):
        for chosen_families in combinations(families, size):
            for selected in product(*(by_family[family] for family in chosen_families)):
                combos.append(tuple(sorted(selected)))
    packed = np.full((len(combos), max_conditions), -1, dtype=np.int16)
    for row, combo in enumerate(combos):
        packed[row, :len(combo)] = combo
    return packed


def _mutual_information_binary(n_total: int, n_up_total: int, n_signal: np.ndarray, n_up_signal: np.ndarray) -> np.ndarray:
    """MI(rule signal; forward-up) in bits, computed from 2x2 counts."""
    n_signal = np.asarray(n_signal, dtype=float)
    up_signal = np.asarray(n_up_signal, dtype=float)
    total = float(n_total)
    up_total = float(n_up_total)
    down_total = total - up_total
    n_off = total - n_signal
    up_off = up_total - up_signal
    down_signal = n_signal - up_signal
    down_off = n_off - up_off
    cells = np.column_stack([up_signal, down_signal, up_off, down_off])
    row_totals = np.column_stack([n_signal, n_off])
    col_totals = np.asarray([up_total, down_total], dtype=float)
    # Cell order matches (signal/up, signal/down, off/up, off/down).
    expected = np.column_stack([
        row_totals[:, 0] * col_totals[0] / total,
        row_totals[:, 0] * col_totals[1] / total,
        row_totals[:, 1] * col_totals[0] / total,
        row_totals[:, 1] * col_totals[1] / total,
    ])
    terms = np.zeros_like(cells)
    valid = (cells > 0) & (expected > 0)
    terms[valid] = cells[valid] / total * np.log2(cells[valid] / expected[valid])
    return terms.sum(axis=1)


def _screen_rules(
    conditions: list[Condition],
    combinations_array: np.ndarray,
    targets: pd.DataFrame,
    train_mask: np.ndarray,
    chunk_size: int = 20_000,
) -> tuple[dict[int, dict[str, np.ndarray]], dict[str, Any]]:
    """Compute discovery counts/p-values/MI using packed boolean bitsets."""
    lookup = np.unpackbits(np.arange(256, dtype=np.uint8)[:, None], axis=1).sum(axis=1).astype(np.uint8)
    metrics_by_horizon: dict[int, dict[str, np.ndarray]] = {}
    train_mask = np.asarray(train_mask, dtype=bool)
    summaries: dict[str, Any] = {"conditions": len(conditions), "candidate_rules": len(combinations_array)}
    for horizon in DISCOVERY_HORIZONS:
        target = targets[f"forward_return_{horizon}d"].to_numpy(dtype=float)
        valid = train_mask & np.isfinite(target)
        idx = np.flatnonzero(valid)
        y = target[valid]
        up_flag = y > 0
        down_flag = y < 0
        base_up = float(up_flag.mean()) if len(y) else np.nan
        base_down = float(down_flag.mean()) if len(y) else np.nan
        if len(idx) == 0:
            raise ValueError("No hay etiquetas válidas en el segmento de descubrimiento.")
        condition_matrix = np.vstack([condition.mask[idx] for condition in conditions]).astype(np.uint8)
        condition_bits = np.packbits(condition_matrix, axis=1, bitorder="little")
        up_bits = np.packbits(up_flag.astype(np.uint8), bitorder="little")
        down_bits = np.packbits(down_flag.astype(np.uint8), bitorder="little")
        number = len(combinations_array)
        counts = np.zeros(number, dtype=np.uint16)
        ups = np.zeros(number, dtype=np.uint16)
        downs = np.zeros(number, dtype=np.uint16)
        for start in range(0, number, chunk_size):
            end = min(number, start + chunk_size)
            combo = combinations_array[start:end]
            first = condition_bits[combo[:, 0]]
            rule_bits = first.copy()
            for column in range(1, combo.shape[1]):
                used = combo[:, column] >= 0
                if used.any():
                    rule_bits[used] &= condition_bits[combo[used, column]]
            counts[start:end] = lookup[rule_bits].sum(axis=1, dtype=np.uint32).astype(np.uint16)
            ups[start:end] = lookup[np.bitwise_and(rule_bits, up_bits)].sum(axis=1, dtype=np.uint32).astype(np.uint16)
            downs[start:end] = lookup[np.bitwise_and(rule_bits, down_bits)].sum(axis=1, dtype=np.uint32).astype(np.uint16)
        eligible = counts >= MIN_CASES
        p_up = _binomial_score_pvalue(ups, counts, base_up)
        p_down = _binomial_score_pvalue(downs, counts, base_down)
        mi = _mutual_information_binary(len(y), int(up_flag.sum()), counts, ups)
        metrics_by_horizon[horizon] = {
            "n": counts,
            "up": ups,
            "down": downs,
            "p_up": p_up,
            "p_down": p_down,
            "mi_bits": mi,
            "baseline_up": np.full(number, base_up),
            "baseline_down": np.full(number, base_down),
            "train_n_total": np.full(number, len(y), dtype=np.int32),
        }
        summaries[str(horizon)] = {
            "train_rows": int(len(y)),
            "base_up_rate": base_up,
            "base_down_rate": base_down,
            "eligible_rule_count": int(eligible.sum()),
            "eligible_directional_tests": int(np.isfinite(p_up).sum() + np.isfinite(p_down).sum()),
        }
    summaries["hypotheses_tested"] = int(sum(
        np.isfinite(metric["p_up"]).sum() + np.isfinite(metric["p_down"]).sum()
        for metric in metrics_by_horizon.values()
    ))
    return metrics_by_horizon, summaries


def _condition_catalog(conditions: list[Condition]) -> pd.DataFrame:
    return pd.DataFrame([{
        "condition_id": i,
        "condition": condition.name,
        "underlying_feature": condition.feature,
        "family": condition.family,
        "threshold_type": condition.kind,
        "threshold": condition.threshold,
    } for i, condition in enumerate(conditions)])


def _format_rule(candidate: np.ndarray, conditions: list[Condition]) -> str:
    used = [int(i) for i in candidate if i >= 0]
    return " AND ".join(conditions[i].name for i in used)


def _candidate_list(
    conditions: list[Condition],
    combinations_array: np.ndarray,
    metrics_by_horizon: dict[int, dict[str, np.ndarray]],
    max_holdout_rules: int,
) -> pd.DataFrame:
    # Correct every eligible directional hypothesis across every horizon in one
    # family. Keep q-values as NumPy arrays; never materialize all millions of
    # rule descriptions as Python dictionaries.
    p_pieces: list[np.ndarray] = []
    q_locations: list[tuple[int, str, np.ndarray]] = []
    for horizon, metric in metrics_by_horizon.items():
        for direction in ("UP", "DOWN"):
            p_values = metric[f"p_{direction.lower()}"]
            valid_idx = np.flatnonzero(np.isfinite(p_values))
            p_pieces.append(p_values[valid_idx])
            q_locations.append((horizon, direction, valid_idx))
    all_p = np.concatenate(p_pieces) if p_pieces else np.asarray([], dtype=float)
    all_q = benjamini_hochberg(all_p)
    cursor = 0
    for horizon, direction, valid_idx in q_locations:
        q_array = np.ones(len(combinations_array), dtype=float)
        stop = cursor + len(valid_idx)
        q_array[valid_idx] = all_q[cursor:stop]
        metrics_by_horizon[horizon][f"q_{direction.lower()}"] = q_array
        cursor = stop

    # Only simple rules (up to three conditions) enter the independent holdout;
    # all one-to-four-condition hypotheses are nevertheless included in the
    # discovery-wide FDR family above. Stratify the finite holdout budget across
    # discovery evidence, information gain, and train-only event frequency so
    # the test set is not spent exclusively on rare, high-variance rules.
    complexity = np.count_nonzero(combinations_array >= 0, axis=1)
    group_keys = [(horizon, direction) for horizon in metrics_by_horizon for direction in ("UP", "DOWN")]
    quotas = {
        "significance": int(round(max_holdout_rules * 0.40)),
        "information_gain": int(round(max_holdout_rules * 0.25)),
        "frequency": int(round(max_holdout_rules * 0.25)),
    }
    quotas["simple_significance"] = max_holdout_rules - sum(quotas.values())
    shortlist: list[tuple[float, int, int, str]] = []
    seen_signatures: set[tuple[int, int, str]] = set()

    def group_quotas(total: int) -> list[int]:
        base, remainder = divmod(total, max(len(group_keys), 1))
        return [base + int(i < remainder) for i in range(len(group_keys))]

    for criterion, budget in quotas.items():
        if budget <= 0:
            continue
        for (horizon, direction), quota in zip(group_keys, group_quotas(budget)):
            if quota <= 0:
                continue
            metric = metrics_by_horizon[horizon]
            eligible = np.flatnonzero(
                np.isfinite(metric[f"p_{direction.lower()}"]) & (complexity <= 3)
            )
            if criterion == "simple_significance":
                eligible = eligible[complexity[eligible] <= 2]
            if len(eligible) == 0:
                continue
            p_values = metric[f"p_{direction.lower()}"][eligible]
            significance_score = -np.log10(np.maximum(p_values, 1e-300)) - 0.30 * (complexity[eligible] - 1)
            if criterion in {"significance", "simple_significance"}:
                scores = significance_score
            elif criterion == "information_gain":
                scores = metric["mi_bits"][eligible] - 0.01 * (complexity[eligible] - 1)
            else:
                scores = metric["n"][eligible].astype(float) - 0.01 * (complexity[eligible] - 1)
            order = np.argsort(-scores, kind="mergesort")
            chosen = 0
            for local in order:
                idx = int(eligible[local])
                signature = (idx, int(horizon), direction)
                if signature in seen_signatures:
                    continue
                seen_signatures.add(signature)
                shortlist.append((float(significance_score[local]), idx, int(horizon), direction))
                chosen += 1
                if chosen >= quota:
                    break
    if len(shortlist) < max_holdout_rules:
        fill: list[tuple[float, int, int, str]] = []
        for horizon, metric in metrics_by_horizon.items():
            for direction in ("UP", "DOWN"):
                p_values = metric[f"p_{direction.lower()}"]
                eligible = np.flatnonzero(np.isfinite(p_values) & (complexity <= 3))
                scores = -np.log10(np.maximum(p_values[eligible], 1e-300)) - 0.30 * (complexity[eligible] - 1)
                order = np.argsort(-scores, kind="mergesort")
                for local in order:
                    idx = int(eligible[local])
                    signature = (idx, int(horizon), direction)
                    if signature not in seen_signatures:
                        fill.append((float(scores[local]), idx, int(horizon), direction))
        fill.sort(key=lambda item: item[0], reverse=True)
        for item in fill:
            signature = (item[1], item[2], item[3])
            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)
            shortlist.append(item)
            if len(shortlist) >= max_holdout_rules:
                break
    if not shortlist:
        return pd.DataFrame()
    shortlist.sort(key=lambda item: (item[0], -int(complexity[item[1]])), reverse=True)

    records: list[dict[str, Any]] = []
    seen: set[tuple[int, int, str]] = set()
    for score, idx, horizon, direction in shortlist:
        signature = (idx, horizon, direction)
        if signature in seen:
            continue
        seen.add(signature)
        metric = metrics_by_horizon[horizon]
        train_hits = metric["up"] if direction == "UP" else metric["down"]
        baseline = metric[f"baseline_{direction.lower()}"]
        n_cases = int(metric["n"][idx])
        records.append({
            "candidate_id": idx,
            "horizon": horizon,
            "direction": direction,
            "condition_ids": tuple(int(i) for i in combinations_array[idx] if i >= 0),
            "pattern": _format_rule(combinations_array[idx], conditions),
            "complexity": int(complexity[idx]),
            "train_cases": n_cases,
            "train_hits": int(train_hits[idx]),
            "train_win_rate": float(train_hits[idx] / n_cases),
            "train_baseline_rate": float(baseline[idx]),
            "train_excess_win_rate": float(train_hits[idx] / n_cases - baseline[idx]),
            "train_mean_information_gain_bits": float(metric["mi_bits"][idx]),
            "train_p_value": float(metric[f"p_{direction.lower()}"][idx]),
            "train_q_value": float(metric[f"q_{direction.lower()}"][idx]),
            "discovery_rank_score": score,
        })
        if len(records) >= max_holdout_rules:
            break
    result = pd.DataFrame.from_records(records)
    if not result.empty:
        result.insert(0, "holdout_rank", np.arange(1, len(result) + 1))
    return result


def _evaluate_holdout_candidate(
    row: dict[str, Any],
    conditions: list[Condition],
    targets: pd.DataFrame,
    test_mask: np.ndarray,
    prices: pd.DataFrame,
    cutoff: pd.Timestamp,
    cost_bps: float,
    period_count: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any] | None]:
    horizon = int(row["horizon"])
    direction = str(row["direction"])
    sign = 1.0 if direction == "UP" else -1.0
    condition_ids = row["condition_ids"]
    signal_condition = np.ones(len(targets), dtype=bool)
    for condition_id in condition_ids:
        signal_condition &= conditions[int(condition_id)].mask
    target = targets[f"forward_return_{horizon}d"].to_numpy(dtype=float)
    valid_test = np.asarray(test_mask, dtype=bool) & np.isfinite(target)
    event_test = valid_test & signal_condition
    test_n = int(event_test.sum())
    record = dict(row)
    record.update({
        "test_cases": test_n,
        "test_hits": np.nan,
        "test_win_rate": np.nan,
        "test_baseline_rate": np.nan,
        "test_excess_win_rate": np.nan,
        "test_mean_directional_return": np.nan,
        "test_raw_mean_return": np.nan,
        "test_p_value_hac": np.nan,
        "test_q_value": np.nan,
        "hac_t_stat": np.nan,
        "periods_valid": 0,
        "periods_positive_skill": 0,
        "period_consistency": 0.0,
        "oos_net_sharpe": np.nan,
        "oos_cagr": np.nan,
        "oos_max_drawdown": np.nan,
        "oos_total_return": np.nan,
        "oos_exposure": np.nan,
        "filter_status": "REJECTED: OOS cases < 100",
    })
    period_rows: list[dict[str, Any]] = []
    if test_n < MIN_CASES:
        return record, period_rows, None

    event_returns = target[event_test]
    event_hits = sign * event_returns > 0
    all_test_returns = target[valid_test]
    all_test_hits = sign * all_test_returns > 0
    baseline_rate = float(all_test_hits.mean())
    win_rate = float(event_hits.mean())
    signed_event_returns = sign * event_returns
    signed_all = sign * all_test_returns
    record.update({
        "test_hits": int(event_hits.sum()),
        "test_win_rate": win_rate,
        "test_baseline_rate": baseline_rate,
        "test_excess_win_rate": win_rate - baseline_rate,
        "test_mean_directional_return": float(signed_event_returns.mean()),
        "test_raw_mean_return": float(event_returns.mean()),
    })
    y = (sign * target[valid_test] > 0).astype(float)
    x = signal_condition[valid_test].astype(float)
    beta, p_value, t_stat = hac_directional_test(y, x, max_lag=max(5, horizon))
    record["test_p_value_hac"] = p_value
    record["hac_t_stat"] = t_stat

    valid_indices = np.flatnonzero(valid_test)
    chunks = np.array_split(valid_indices, period_count)
    positive_periods = 0
    valid_periods = 0
    for period_index, indices in enumerate(chunks, start=1):
        period_signal = signal_condition[indices]
        period_returns = target[indices]
        event = period_signal & np.isfinite(period_returns)
        if int(event.sum()) < 20:
            period_rows.append({
                "holdout_rank": row["holdout_rank"],
                "pattern": row["pattern"],
                "horizon": horizon,
                "direction": direction,
                "period": period_index,
                "period_start": prices.index[indices[0]].date().isoformat() if len(indices) else "",
                "period_end": prices.index[indices[-1]].date().isoformat() if len(indices) else "",
                "cases": int(event.sum()),
                "win_rate": np.nan,
                "baseline_rate": np.nan,
                "excess_win_rate": np.nan,
                "mean_directional_return": np.nan,
                "period_status": "insufficient event count (<20)",
            })
            continue
        event_hit_rate = float((sign * period_returns[event] > 0).mean())
        base_rate = float((sign * period_returns[np.isfinite(period_returns)] > 0).mean())
        skill = event_hit_rate - base_rate
        positive_periods += int(skill > 0)
        valid_periods += 1
        period_rows.append({
            "holdout_rank": row["holdout_rank"],
            "pattern": row["pattern"],
            "horizon": horizon,
            "direction": direction,
            "period": period_index,
            "period_start": prices.index[indices[0]].date().isoformat() if len(indices) else "",
            "period_end": prices.index[indices[-1]].date().isoformat() if len(indices) else "",
            "cases": int(event.sum()),
            "win_rate": event_hit_rate,
            "baseline_rate": base_rate,
            "excess_win_rate": skill,
            "mean_directional_return": float((sign * period_returns[event]).mean()),
            "period_status": "positive skill" if skill > 0 else "no positive skill",
        })
    consistency = positive_periods / valid_periods if valid_periods else 0.0
    record["periods_valid"] = valid_periods
    record["periods_positive_skill"] = positive_periods
    record["period_consistency"] = consistency

    # OOS-only trading signal; the backtest helper delays it to the next open.
    strategy_signal = np.where((prices.index > cutoff) & signal_condition, sign, 0.0)
    bt, _ = backtest_positions(
        prices,
        pd.Series(strategy_signal, index=prices.index),
        cutoff,
        cost_bps,
        name=f"pattern_{row['holdout_rank']}",
        holding_horizon=horizon,
    )
    record["oos_net_sharpe"] = bt.get("sharpe", np.nan)
    record["oos_cagr"] = bt.get("cagr", np.nan)
    record["oos_max_drawdown"] = bt.get("max_drawdown", np.nan)
    record["oos_total_return"] = bt.get("total_return", np.nan)
    record["oos_exposure"] = bt.get("exposure", np.nan)
    return record, period_rows, bt


def run_discovery(
    features: pd.DataFrame,
    targets: pd.DataFrame,
    prices: pd.DataFrame,
    close: pd.Series,
    cutoff: pd.Timestamp,
    cost_bps: float = 5.0,
    min_cases: int = MIN_CASES,
    max_holdout_rules: int = 100,
    max_conditions: int = 4,
    period_count: int = 4,
) -> dict[str, Any]:
    """Mine multi-family rules on the past and validate a bounded shortlist."""
    primary_target = targets["forward_return_5d"].notna().to_numpy()
    train_mask = (features.index <= cutoff) & primary_target
    test_mask = features.index > cutoff
    conditions = build_conditions(features, close, train_mask, min_cases=min_cases)
    if len(conditions) < 2:
        raise ValueError("No se generaron suficientes condiciones tras aplicar el mínimo de casos.")
    candidate_combinations = build_candidate_combinations(conditions, max_conditions=max_conditions)
    metrics_by_horizon, summary = _screen_rules(conditions, candidate_combinations, targets, train_mask)
    summary.update({
        "discovery_start": features.index[train_mask].min().date().isoformat(),
        "discovery_end": pd.Timestamp(cutoff).date().isoformat(),
        "holdout_start": features.index[test_mask].min().date().isoformat(),
        "holdout_end": features.index[test_mask].max().date().isoformat(),
        "min_cases": int(min_cases),
        "max_conditions": int(max_conditions),
        "max_holdout_rules": int(max_holdout_rules),
    })
    holdout_candidates = _candidate_list(
        conditions, candidate_combinations, metrics_by_horizon, max_holdout_rules=max_holdout_rules
    )
    if holdout_candidates.empty:
        return {
            "conditions": conditions,
            "condition_catalog": _condition_catalog(conditions),
            "candidate_combinations": candidate_combinations,
            "summary": summary,
            "candidates": pd.DataFrame(),
            "ranking": pd.DataFrame(),
            "periods": pd.DataFrame(),
            "backtest_metrics": [],
            "backtest_curves": {},
        }

    evaluated: list[dict[str, Any]] = []
    period_records: list[dict[str, Any]] = []
    backtest_metrics: list[dict[str, Any]] = []
    backtest_curves: dict[str, pd.DataFrame] = {}
    for row in holdout_candidates.to_dict(orient="records"):
        result, periods, curve = _evaluate_holdout_candidate(
            row, conditions, targets, test_mask, prices, cutoff, cost_bps, period_count
        )
        evaluated.append(result)
        period_records.extend(periods)
        if curve is not None:
            backtest_metrics.append({
                "strategy": f"pattern_{row['holdout_rank']}",
                "pattern": row["pattern"],
                "horizon": row["horizon"],
                "direction": row["direction"],
                **{key: value for key, value in result.items() if key.startswith("oos_")},
            })
            backtest_curves[f"pattern_{row['holdout_rank']}"] = curve

    candidates = pd.DataFrame(evaluated)
    valid_q = candidates["test_cases"].ge(min_cases) & candidates["test_p_value_hac"].notna()
    candidates["test_q_value"] = np.nan
    if valid_q.any():
        candidates.loc[valid_q, "test_q_value"] = benjamini_hochberg(
            candidates.loc[valid_q, "test_p_value_hac"].to_numpy(dtype=float)
        )
    candidates["robustness_score"] = (
        100.0 * candidates["period_consistency"].fillna(0.0)
        - 8.0 * (candidates["complexity"].astype(float) - 1.0)
        + 2.0 * np.minimum(-np.log10(candidates["test_q_value"].fillna(1.0).clip(lower=1e-12)), 5.0)
    ).clip(lower=0.0, upper=100.0)

    status = []
    for _, row in candidates.iterrows():
        reasons = []
        if row["train_cases"] < min_cases:
            reasons.append("train_n<100")
        if row["test_cases"] < min_cases:
            reasons.append("test_n<100")
        if row["train_p_value"] > 0.05:
            reasons.append("train_p>0.05")
        if row["test_cases"] >= min_cases:
            if pd.isna(row["test_p_value_hac"]) or row["test_p_value_hac"] > 0.05:
                reasons.append("holdout_HAC_p>0.05")
            if pd.isna(row["test_q_value"]) or row["test_q_value"] > 0.05:
                reasons.append("holdout_FDR_q>0.05")
            if row["test_win_rate"] < 0.55:
                reasons.append("holdout_win_rate<55%")
            if row["test_mean_directional_return"] <= 0:
                reasons.append("nonpositive_directional_return")
            if row["oos_net_sharpe"] <= 0:
                reasons.append("nonpositive_net_Sharpe")
        if row["periods_valid"] < 3:
            reasons.append("insufficient_valid_subperiods")
        elif row["periods_positive_skill"] < 3:
            reasons.append("not_consistent_in_3_of_4_periods")
        if row["complexity"] > 3:
            reasons.append("complexity>3_conditions")
        status.append("VALIDATED" if not reasons else "REJECTED: " + "; ".join(reasons))
    candidates["filter_status"] = status
    validated = candidates[candidates["filter_status"] == "VALIDATED"].copy()
    validated = validated.sort_values(
        ["robustness_score", "test_q_value", "complexity", "oos_net_sharpe"],
        ascending=[False, True, True, False], kind="mergesort",
    ).reset_index(drop=True)
    if not validated.empty:
        validated.insert(0, "rank", np.arange(1, len(validated) + 1))
    periods_df = pd.DataFrame(period_records)
    summary.update({
        "holdout_candidates_tested": int(len(candidates)),
        "holdout_candidates_with_100_cases": int(valid_q.sum()),
        "validated_patterns": int(len(validated)),
        "train_nominal_p_le_05_directional_tests": int(sum(
            (metric[direction] <= 0.05).sum()
            for metric in metrics_by_horizon.values()
            for direction in ("p_up", "p_down")
        )), 
        "train_bh_q_le_05_directional_tests": int(sum(
            (metric[f"q_{direction}"] <= 0.05).sum()
            for metric in metrics_by_horizon.values()
            for direction in ("up", "down")
        )),
    })
    # Retain only discovery summaries/condition definitions, not millions of
    # intermediate bitsets, in the returned object.
    return {
        "conditions": conditions,
        "condition_catalog": _condition_catalog(conditions),
        "candidate_combinations": candidate_combinations,
        "summary": summary,
        "candidates": candidates,
        "ranking": validated,
        "periods": periods_df,
        "backtest_metrics": backtest_metrics,
        "backtest_curves": backtest_curves,
    }


def _get_train_q_for_summary(
    conditions: list[Condition],
    combinations_array: np.ndarray,
    metrics_by_horizon: dict[int, dict[str, np.ndarray]],
    horizon: int,
    direction: str,
) -> np.ndarray:
    # Used only to report the familywise training FDR count. Recompute the BH
    # mapping cheaply for a horizon/direction group; total candidates are stored
    # in compact NumPy arrays, not materialized as millions of Python records.
    metric = metrics_by_horizon[horizon]
    pvalues = metric[f"p_{direction.lower()}"]
    return benjamini_hochberg(pvalues)
