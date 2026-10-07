"""Descriptive profiling and pre-specified temporal diagnostics."""
from __future__ import annotations

import numpy as np
import pandas as pd


def data_quality_report(raw: pd.DataFrame, standardized: pd.DataFrame, cleanup: dict[str, int]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for column in raw.columns:
        series = raw[column]
        numeric = pd.to_numeric(series, errors="coerce")
        is_numeric = pd.api.types.is_numeric_dtype(series) or numeric.notna().any()
        outlier_count = np.nan
        if is_numeric:
            values = numeric.replace([np.inf, -np.inf], np.nan).dropna()
            if len(values):
                q1, q3 = values.quantile([0.25, 0.75])
                iqr = q3 - q1
                outlier_count = int(((values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr)).sum())
        rows.append({
            "column": str(column),
            "dtype": str(series.dtype),
            "rows": int(len(series)),
            "missing": int(series.isna().sum()),
            "missing_pct": float(series.isna().mean() * 100.0),
            "unique_nonmissing": int(series.nunique(dropna=True)),
            "iqr_outliers_1_5": outlier_count,
        })
    for key, value in cleanup.items():
        rows.append({
            "column": f"cleanup_{key}",
            "dtype": "diagnostic",
            "rows": int(value),
            "missing": np.nan,
            "missing_pct": np.nan,
            "unique_nonmissing": np.nan,
            "iqr_outliers_1_5": np.nan,
        })
    for column in standardized.columns:
        if column in {"open", "high", "low", "close", "adj_close", "volume"}:
            continue
        series = standardized[column]
        rows.append({
            "column": f"standardized_{column}",
            "dtype": str(series.dtype),
            "rows": int(len(series)),
            "missing": int(series.isna().sum()),
            "missing_pct": float(series.isna().mean() * 100.0),
            "unique_nonmissing": int(series.nunique(dropna=True)),
            "iqr_outliers_1_5": np.nan,
        })
    return pd.DataFrame(rows)


def descriptive_statistics(raw: pd.DataFrame, standardized: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
    series_map: dict[str, pd.Series] = {}
    for column in raw.columns:
        values = pd.to_numeric(raw[column], errors="coerce")
        if values.notna().any():
            series_map[f"raw.{column}"] = values
    price = standardized["adj_close"].where(standardized["adj_close"].notna(), standardized["close"])
    series_map["close_to_close_return_1d"] = price.pct_change()
    for name in ("return_3d", "return_5d", "rolling_vol_20d", "rsi_14", "zscore_close_20d", "volume_ratio_20d"):
        if name in features:
            series_map[name] = features[name]
    results: list[dict[str, object]] = []
    for name, values in series_map.items():
        x = pd.to_numeric(values, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        if x.empty:
            continue
        quantiles = x.quantile([0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99])
        q1, q3 = quantiles.loc[0.25], quantiles.loc[0.75]
        iqr = q3 - q1
        try:
            skew = float(x.skew())
            kurtosis = float(x.kurt())
        except Exception:
            skew, kurtosis = np.nan, np.nan
        results.append({
            "series": name,
            "count": int(x.size),
            "mean": float(x.mean()),
            "std": float(x.std(ddof=1)) if x.size > 1 else np.nan,
            "min": float(x.min()),
            "q01": float(quantiles.loc[0.01]),
            "q05": float(quantiles.loc[0.05]),
            "q25": float(q1),
            "median": float(quantiles.loc[0.5]),
            "q75": float(q3),
            "q95": float(quantiles.loc[0.95]),
            "q99": float(quantiles.loc[0.99]),
            "max": float(x.max()),
            "skew": skew,
            "excess_kurtosis": kurtosis,
            "iqr_outliers_1_5": int(((x < q1 - 1.5 * iqr) | (x > q3 + 1.5 * iqr)).sum()),
        })
    return pd.DataFrame(results)


def annual_regimes(ohlcv: pd.DataFrame, close: pd.Series) -> pd.DataFrame:
    daily = close.pct_change()
    rows: list[dict[str, object]] = []
    years = pd.Index(ohlcv.index.year).unique()
    for year in years:
        selected = ohlcv.index.year == year
        r = daily.loc[selected].dropna()
        p = close.loc[selected].dropna()
        if r.empty or p.empty:
            continue
        equity = (1.0 + r).cumprod()
        drawdown = equity / equity.cummax().clip(lower=1.0) - 1.0
        sd = r.std(ddof=1)
        rows.append({
            "year": int(year),
            "first_session": p.index.min().date().isoformat(),
            "last_session": p.index.max().date().isoformat(),
            "sessions": int(r.size),
            "price_return": float(equity.iloc[-1] - 1.0),
            "annualized_volatility": float(sd * np.sqrt(252.0)) if pd.notna(sd) else np.nan,
            "daily_sharpe_rf0": float(np.sqrt(252.0) * r.mean() / sd) if pd.notna(sd) and sd > 0 else np.nan,
            "up_session_rate": float((r > 0).mean()),
            "max_drawdown_within_year": float(drawdown.min()),
            "worst_day": float(r.min()),
            "best_day": float(r.max()),
        })
    return pd.DataFrame(rows)


def structural_shift_tests(close: pd.Series) -> pd.DataFrame:
    """Compare two pre-specified chronological halves; not a break-date search."""
    returns = close.pct_change().dropna()
    if len(returns) < 60:
        return pd.DataFrame([{"test": "not_run", "reason": "Menos de 60 retornos."}])
    midpoint = returns.index[len(returns) // 2]
    early = returns.loc[returns.index < midpoint]
    late = returns.loc[returns.index >= midpoint]
    try:
        from scipy.stats import levene, ttest_ind
        mean_test = ttest_ind(early, late, equal_var=False, nan_policy="omit")
        vol_test = ttest_ind(early.abs(), late.abs(), equal_var=False, nan_policy="omit")
        variance_test = levene(early, late, center="median")
        t_p, abs_p, var_p = float(mean_test.pvalue), float(vol_test.pvalue), float(variance_test.pvalue)
        t_stat, abs_stat, var_stat = float(mean_test.statistic), float(vol_test.statistic), float(variance_test.statistic)
    except Exception:
        t_p = abs_p = var_p = t_stat = abs_stat = var_stat = np.nan
    result = pd.DataFrame([
        {
            "test": "Welch mean daily return: first vs second half",
            "split_date": midpoint.date().isoformat(),
            "first_n": int(len(early)),
            "second_n": int(len(late)),
            "first_mean": float(early.mean()),
            "second_mean": float(late.mean()),
            "statistic": t_stat,
            "p_value": t_p,
            "interpretation": "Diagnóstico preespecificado; no estima una fecha causal de ruptura.",
        },
        {
            "test": "Welch absolute daily return: first vs second half",
            "split_date": midpoint.date().isoformat(),
            "first_n": int(len(early)),
            "second_n": int(len(late)),
            "first_mean": float(early.abs().mean()),
            "second_mean": float(late.abs().mean()),
            "statistic": abs_stat,
            "p_value": abs_p,
            "interpretation": "Diferencia de magnitud media; complementa los regímenes anuales.",
        },
        {
            "test": "Levene variance: first vs second half",
            "split_date": midpoint.date().isoformat(),
            "first_n": int(len(early)),
            "second_n": int(len(late)),
            "first_mean": float(early.var(ddof=1)),
            "second_mean": float(late.var(ddof=1)),
            "statistic": var_stat,
            "p_value": var_p,
            "interpretation": "Diagnóstico de varianzas preespecificado; no se busca una fecha de ruptura.",
        },
    ])
    p_values = pd.to_numeric(result["p_value"], errors="coerce").to_numpy(dtype=float)
    valid = np.isfinite(p_values)
    adjusted = np.full(len(p_values), np.nan, dtype=float)
    if valid.any():
        selected = p_values[valid]
        order = np.argsort(selected, kind="mergesort")
        sorted_p = selected[order]
        m = len(sorted_p)
        holm_sorted = np.maximum.accumulate(sorted_p * (m - np.arange(m)))
        restored = np.empty_like(holm_sorted)
        restored[order] = np.minimum(holm_sorted, 1.0)
        adjusted[valid] = restored
    result["p_value_holm"] = adjusted
    return result


def distribution_outliers(close: pd.Series) -> dict[str, float | int]:
    returns = close.pct_change().dropna()
    if returns.empty:
        return {"daily_return_outliers_1_5_iqr": 0, "daily_return_min": np.nan, "daily_return_max": np.nan}
    q1, q3 = returns.quantile([0.25, 0.75])
    iqr = q3 - q1
    count = int(((returns < q1 - 1.5 * iqr) | (returns > q3 + 1.5 * iqr)).sum())
    return {
        "daily_return_outliers_1_5_iqr": count,
        "daily_return_min": float(returns.min()),
        "daily_return_max": float(returns.max()),
        "daily_return_q01": float(returns.quantile(0.01)),
        "daily_return_q99": float(returns.quantile(0.99)),
    }
