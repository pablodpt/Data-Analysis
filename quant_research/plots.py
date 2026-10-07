"""Publication-lightweight PNG charts for the research report."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def _matplotlib():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def create_plots(
    output_dir: str | Path,
    prices: pd.DataFrame,
    close: pd.Series,
    features: pd.DataFrame,
    targets: pd.DataFrame,
    annual: pd.DataFrame,
    model_metrics: pd.DataFrame,
    model_curves: dict[str, pd.DataFrame],
    pattern_curves: dict[str, pd.DataFrame],
    pattern_ranking: pd.DataFrame,
    feature_importance: pd.DataFrame,
    cutoff: pd.Timestamp,
) -> list[str]:
    plt = _matplotlib()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    files: list[str] = []

    # Price, rolling realized volatility, and drawdown.
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True, constrained_layout=True)
    axes[0].plot(close.index, close, color="#1f4e79", linewidth=1.15)
    axes[0].axvline(cutoff, color="#c44e52", linestyle="--", linewidth=1, label="Corte descubrimiento/holdout")
    axes[0].set_ylabel("Nivel de cierre")
    axes[0].set_title("S&P 500: precio, volatilidad y drawdown (muestra disponible)")
    axes[0].legend(loc="upper left")
    if "rolling_vol_20d" in features:
        axes[1].plot(features.index, features["rolling_vol_20d"] * 100.0, color="#dd8452", linewidth=1)
    axes[1].set_ylabel("Volatilidad 20d (%)"); axes[1].grid(alpha=0.2)
    daily_ret = close.pct_change()
    equity = (1 + daily_ret.fillna(0)).cumprod()
    drawdown = equity / equity.cummax().clip(lower=1.0) - 1.0
    axes[2].fill_between(drawdown.index, drawdown.to_numpy() * 100.0, 0, color="#c44e52", alpha=0.55)
    axes[2].set_ylabel("Drawdown (%)"); axes[2].grid(alpha=0.2)
    path = out / "price_volatility_drawdown.png"
    fig.savefig(path, dpi=160); plt.close(fig); files.append(path.name)

    # Return distribution and empirical CDF; winsorization is not applied.
    returns = close.pct_change().dropna() * 100.0
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), constrained_layout=True)
    axes[0].hist(returns, bins=65, color="#4c72b0", alpha=0.8, density=True)
    axes[0].axvline(returns.mean(), color="#c44e52", linestyle="--", label=f"Media {returns.mean():.3f}%")
    axes[0].set_title("Distribución de retornos diarios")
    axes[0].set_xlabel("Retorno close-to-close (%)"); axes[0].set_ylabel("Densidad"); axes[0].legend()
    ordered = np.sort(returns.to_numpy())
    cdf = np.arange(1, len(ordered) + 1) / max(len(ordered), 1)
    axes[1].plot(ordered, cdf, color="#55a868")
    axes[1].set_title("Distribución empírica acumulada")
    axes[1].set_xlabel("Retorno diario (%)"); axes[1].set_ylabel("Probabilidad acumulada"); axes[1].grid(alpha=0.2)
    path = out / "daily_return_distribution.png"
    fig.savefig(path, dpi=160); plt.close(fig); files.append(path.name)

    # Calendar-year price-return/volatility regime diagnostics.
    if not annual.empty:
        fig, ax1 = plt.subplots(figsize=(12, 5), constrained_layout=True)
        years = annual["year"].astype(int).astype(str)
        ax1.bar(years, annual["price_return"] * 100, color="#4c72b0", alpha=0.75, label="Retorno anual precio")
        ax1.axhline(0, color="black", linewidth=0.7)
        ax1.set_ylabel("Retorno anual (%)")
        ax2 = ax1.twinx()
        ax2.plot(years, annual["annualized_volatility"] * 100, color="#c44e52", marker="o", linewidth=1.4, label="Volatilidad anualizada")
        ax2.set_ylabel("Volatilidad anualizada (%)")
        ax1.set_title("Regímenes por año calendario (descriptivo, no predictivo)")
        ax1.tick_params(axis="x", rotation=45)
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(handles1 + handles2, labels1 + labels2, loc="upper left")
        path = out / "annual_regimes.png"
        fig.savefig(path, dpi=160); plt.close(fig); files.append(path.name)

    # OOS strategy equity curves; show no false pattern when none passed filters.
    candidates: list[tuple[str, pd.DataFrame, str]] = []
    if not pattern_ranking.empty:
        for _, row in pattern_ranking.head(3).iterrows():
            name = f"pattern_{int(row['holdout_rank'])}"
            if name in pattern_curves:
                candidates.append((name, pattern_curves[name], f"Regla validada #{int(row['rank'])}"))
    if model_metrics is not None and not model_metrics.empty:
        rankable = model_metrics[
            (model_metrics.get("task") == "classification")
            & (model_metrics.get("horizon") == 1)
            & (model_metrics.get("status") == "ok")
        ].copy()
        if not rankable.empty:
            rankable = rankable.sort_values("roc_auc", ascending=False)
            for _, row in rankable.head(2).iterrows():
                name = f"{row['model']}_classification_1d"
                if name in model_curves:
                    candidates.append((name, model_curves[name], f"{row['model']} (AUC {row['roc_auc']:.3f})"))
    if candidates:
        fig, ax = plt.subplots(figsize=(12, 5.5), constrained_layout=True)
        for name, curve, label in candidates:
            if "equity" in curve and curve["equity"].notna().any():
                y = curve["equity"]
            elif "net_return" in curve:
                y = (1.0 + curve["net_return"].fillna(0)).cumprod()
            else:
                continue
            ax.plot(y.index, y, linewidth=1.2, label=label)
        ax.set_title("Equity OOS (señales conocidas al cierre, ejecución con retardo)")
        ax.set_ylabel("Equity normalizada"); ax.grid(alpha=0.2); ax.legend(loc="best")
        path = out / "oos_equity_curves.png"
        fig.savefig(path, dpi=160); plt.close(fig); files.append(path.name)
    else:
        fig, ax = plt.subplots(figsize=(12, 4.5), constrained_layout=True)
        ax.text(0.5, 0.5, "No hay estrategias que superen los filtros de validación.", ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
        ax.set_title("Backtest de estrategias: sin señales validadas")
        path = out / "oos_equity_curves.png"
        fig.savefig(path, dpi=160); plt.close(fig); files.append(path.name)

    # Out-of-sample permutation/native/SHAP feature diagnostics.
    if feature_importance is not None and not feature_importance.empty:
        importance = feature_importance[feature_importance["importance_type"] == "permutation_roc_auc"].copy()
        if importance.empty:
            importance = feature_importance[feature_importance["importance_type"] == "shap_mean_abs"].copy()
        if not importance.empty:
            importance = importance.sort_values("importance_mean", ascending=True).tail(18)
            fig, ax = plt.subplots(figsize=(9, 7), constrained_layout=True)
            ax.barh(importance["feature"], importance["importance_mean"], color="#8172b2")
            ax.set_title("Importancia permutada en el último fold temporal")
            ax.set_xlabel("Δ ROC AUC (mayor = más importancia)"); ax.grid(axis="x", alpha=0.2)
            path = out / "feature_importance.png"
            fig.savefig(path, dpi=160); plt.close(fig); files.append(path.name)

    return files
