"""Out-of-sample, next-session execution backtests."""
from __future__ import annotations

import math
import numpy as np
import pandas as pd


def backtest_positions(
    prices: pd.DataFrame,
    signal: pd.Series,
    evaluation_start: pd.Timestamp | None = None,
    cost_bps: float = 5.0,
    name: str = "strategy",
    holding_horizon: int = 1,
) -> tuple[dict[str, float | int | str], pd.DataFrame]:
    """Backtest close-known signals with delayed entry and horizon-aligned holds.

    A signal observed after close t enters at the next available open and is
    held for `holding_horizon` open-to-open intervals. Daily predictions create
    overlapping vintages; their signed exposures are averaged over the horizon
    (gross exposure is capped at one). Open-to-open returns are indexed at the
    ending session, so the first position P&L is shifted two rows. If Open is
    missing, close-to-close is a proxy. A change of one net position unit costs
    `cost_bps`; cash is flat and the risk-free rate is zero. Signals in the
    final horizon-plus-two rows are ignored because their holding/exit costs
    cannot be observed in the available sample.
    """
    idx = prices.index
    signal = pd.Series(signal, index=idx, dtype=float).replace([np.inf, -np.inf], np.nan)
    signal = signal.clip(-1.0, 1.0)
    if prices.get("open", pd.Series(np.nan, index=idx)).notna().any():
        execution_price = prices["open"].astype(float)
        return_name = "open_to_open"
    else:
        close_col = "adj_close" if prices["adj_close"].notna().any() else "close"
        execution_price = prices[close_col].astype(float)
        return_name = "close_to_close_proxy"

    market_return = execution_price.pct_change()
    horizon = int(holding_horizon)
    if horizon < 1:
        raise ValueError("holding_horizon must be at least 1")
    trade_signal = signal.copy()
    tail = horizon + 2
    if len(trade_signal) >= tail:
        trade_signal.iloc[-tail:] = 0.0
    else:
        trade_signal[:] = 0.0
    # At return row i, the active daily vintages are the signals from
    # i-horizon-1 through i-2. Their mean keeps gross exposure <= 1.
    position = trade_signal.rolling(horizon, min_periods=1).sum().shift(2) / float(horizon)
    position = position.fillna(0.0)
    turnover = position.diff().abs().fillna(position.abs())
    gross = position * market_return
    transaction_cost = turnover * (float(cost_bps) / 10000.0)
    net = gross - transaction_cost
    pnl = pd.DataFrame({
        "signal": signal,
        "position": position,
        "market_return": market_return,
        "turnover": turnover,
        "gross_return": gross,
        "transaction_cost": transaction_cost,
        "net_return": net,
    }, index=idx)
    if evaluation_start is not None:
        eval_mask = pd.Series(idx >= pd.Timestamp(evaluation_start), index=idx)
        pnl = pnl.loc[eval_mask]
    pnl = pnl.loc[pnl["market_return"].notna()]
    if pnl.empty:
        metrics = {
            "strategy": name,
            "bars": 0,
            "total_return": np.nan,
            "cagr": np.nan,
            "sharpe": np.nan,
            "max_drawdown": np.nan,
            "win_day_rate": np.nan,
            "exposure": np.nan,
            "trades": 0,
            "turnover": 0.0,
            "cost_bps_one_way": float(cost_bps),
            "return_basis": return_name,
        }
        return metrics, pnl

    # During non-invested days, returns are zero, so CAGR uses the full
    # evaluation calendar (not only days with an open position).
    net_returns = pnl["net_return"].fillna(0.0).astype(float)
    gross_returns = pnl["gross_return"].fillna(0.0).astype(float)
    equity = (1.0 + net_returns).cumprod()
    peak = equity.cummax().clip(lower=1.0)
    drawdown = equity / peak - 1.0
    years = len(net_returns) / 252.0
    total_return = float(equity.iloc[-1] - 1.0)
    cagr = float((equity.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 and equity.iloc[-1] > 0 else np.nan)
    standard_deviation = float(net_returns.std(ddof=1)) if len(net_returns) > 1 else np.nan
    sharpe = float(np.sqrt(252.0) * net_returns.mean() / standard_deviation) if standard_deviation and np.isfinite(standard_deviation) else np.nan
    active = pnl["position"].abs() > 0
    prev_active = active.shift(1, fill_value=False)
    entries = int((active & ~prev_active).sum())
    metrics = {
        "strategy": name,
        "bars": int(len(pnl)),
        "total_return": total_return,
        "cagr": cagr,
        "sharpe": sharpe,
        "max_drawdown": float(drawdown.min()),
        "win_day_rate": float((net_returns > 0).mean()),
        "exposure": float(pnl["position"].abs().mean()),
        "trades": entries,
        "turnover": float(pnl["turnover"].sum()),
        "mean_gross_daily_return": float(gross_returns.mean()),
        "cost_bps_one_way": float(cost_bps),
        "return_basis": return_name,
    }
    pnl["equity"] = equity
    pnl["drawdown"] = drawdown
    return metrics, pnl


def buy_and_hold_metrics(prices: pd.DataFrame, evaluation_start: pd.Timestamp | None = None) -> dict[str, float | int | str]:
    """Benchmark over the same open/close-to-open return convention."""
    signal = pd.Series(1.0, index=prices.index)
    metrics, _ = backtest_positions(prices, signal, evaluation_start=evaluation_start, cost_bps=0.0, name="buy_and_hold")
    # A benchmark is already invested, so the strategy signal's latency would
    # otherwise omit the first two returns. For apples-to-apples metrics use a
    # direct buy-and-hold series below.
    if prices.get("open", pd.Series(np.nan, index=prices.index)).notna().any():
        price = prices["open"].astype(float)
    else:
        price = prices["adj_close"].where(prices["adj_close"].notna(), prices["close"]).astype(float)
    returns = price.pct_change()
    if evaluation_start is not None:
        returns = returns.loc[returns.index >= pd.Timestamp(evaluation_start)]
    returns = returns.dropna()
    if returns.empty:
        return metrics
    equity = (1.0 + returns).cumprod()
    years = len(returns) / 252.0
    dd = equity / equity.cummax().clip(lower=1.0) - 1.0
    sd = returns.std(ddof=1)
    metrics.update({
        "bars": int(len(returns)),
        "total_return": float(equity.iloc[-1] - 1.0),
        "cagr": float(equity.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 and equity.iloc[-1] > 0 else np.nan,
        "sharpe": float(np.sqrt(252.0) * returns.mean() / sd) if sd > 0 else np.nan,
        "max_drawdown": float(dd.min()),
        "win_day_rate": float((returns > 0).mean()),
        "exposure": 1.0,
        "trades": 1,
        "turnover": 1.0,
        "mean_gross_daily_return": float(returns.mean()),
        "cost_bps_one_way": 0.0,
    })
    return metrics
