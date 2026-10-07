"""Leakage-safe technical, calendar, and OHLCV features."""
from __future__ import annotations

import numpy as np
import pandas as pd


RETURN_WINDOWS = (1, 3, 5, 10, 20)
VOL_WINDOWS = (5, 10, 20)
SMA_WINDOWS = (5, 10, 20, 50, 200)
TARGET_HORIZONS = (1, 3, 5, 10, 20)

# Stationary/scale-free subset used by the ML models. Raw SMA/ATR/OBV levels
# are still generated and documented, but not fed to models as price-levels.
MODEL_FEATURES = [
    *(f"return_{w}d" for w in RETURN_WINDOWS),
    *(f"rolling_vol_{w}d" for w in VOL_WINDOWS),
    "volatility_ratio_20_60",
    "atr_pct_14d",
    *(f"dist_sma_{w}d" for w in SMA_WINDOWS),
    *(f"slope_sma_{w}d" for w in SMA_WINDOWS),
    "rsi_14",
    "roc_10d",
    "roc_20d",
    "macd_pct",
    "macd_signal_pct",
    "macd_hist_pct",
    "zscore_close_20d",
    "day_of_week",
    "day_of_month",
    "week_of_year",
    "month_of_year",
    "dow_sin",
    "dow_cos",
    "month_sin",
    "month_cos",
    "day_of_month_sin",
    "day_of_month_cos",
    "pre_holiday",
    "post_holiday",
    "month_start_3",
    "month_end_3",
    "volume_spike",
    "volume_ratio_20d",
    "obv_slope_20d",
]

CONTINUOUS_PATTERN_FEATURES = [
    *(f"return_{w}d" for w in RETURN_WINDOWS),
    *(f"rolling_vol_{w}d" for w in VOL_WINDOWS),
    "volatility_ratio_20_60",
    "atr_pct_14d",
    "dist_sma_5d",
    "dist_sma_20d",
    "dist_sma_50d",
    "dist_sma_200d",
    "slope_sma_20d",
    "slope_sma_50d",
    "slope_sma_200d",
    "rsi_14",
    "roc_10d",
    "roc_20d",
    "macd_hist_pct",
    "zscore_close_20d",
    "volume_ratio_20d",
    "obv_slope_20d",
]

FEATURE_GROUPS: dict[str, str] = {}
for _name in [*(f"return_{w}d" for w in RETURN_WINDOWS), "rsi_14", "roc_10d", "roc_20d", "macd_pct", "macd_signal_pct", "macd_hist_pct", "zscore_close_20d"]:
    FEATURE_GROUPS[_name] = "momentum"
for _name in [*(f"rolling_vol_{w}d" for w in VOL_WINDOWS), "volatility_ratio_20_60", "atr_14d", "atr_pct_14d"]:
    FEATURE_GROUPS[_name] = "volatility"
for _name in [*(f"sma_{w}d" for w in SMA_WINDOWS), *(f"dist_sma_{w}d" for w in SMA_WINDOWS), *(f"slope_sma_{w}d" for w in SMA_WINDOWS)]:
    FEATURE_GROUPS[_name] = "trend"
for _name in ["volume_spike", "volume_ratio_20d", "obv", "obv_slope_20d"]:
    FEATURE_GROUPS[_name] = "volume"
for _name in ["day_of_week", "day_of_month", "week_of_year", "month_of_year", "pre_holiday", "post_holiday", "dow_sin", "dow_cos", "month_sin", "month_cos", "day_of_month_sin", "day_of_month_cos", "month_start_3", "month_end_3"]:
    FEATURE_GROUPS[_name] = "seasonality"

FEATURE_DEFINITIONS: dict[str, tuple[str, str]] = {}
for _w in RETURN_WINDOWS:
    FEATURE_DEFINITIONS[f"return_{_w}d"] = ("Retornos", f"Close(t) / Close(t-{_w}) - 1; retorno histórico acumulado de {_w} sesión(es).")
for _w in VOL_WINDOWS:
    FEATURE_DEFINITIONS[f"rolling_vol_{_w}d"] = ("Volatilidad", f"Desviación típica muestral de los retornos diarios en {_w} sesiones, anualizada por √252.")
FEATURE_DEFINITIONS["volatility_ratio_20_60"] = ("Volatilidad", "Volatilidad realizada 20d dividida por la volatilidad 60d; expansión/contracción relativa.")
FEATURE_DEFINITIONS["atr_14d"] = ("Volatilidad", "ATR 14 de Wilder sobre OHLC, en puntos de índice.")
FEATURE_DEFINITIONS["atr_pct_14d"] = ("Volatilidad", "ATR 14 de Wilder dividido por el precio de cierre.")
for _w in SMA_WINDOWS:
    FEATURE_DEFINITIONS[f"sma_{_w}d"] = ("Tendencia", f"Media móvil simple de {_w} cierres.")
    FEATURE_DEFINITIONS[f"dist_sma_{_w}d"] = ("Tendencia", f"Close / SMA({_w}) - 1.")
    FEATURE_DEFINITIONS[f"slope_sma_{_w}d"] = ("Tendencia", f"Cambio de SMA({_w}) en 5 sesiones, dividido por 5 y por el precio actual.")
FEATURE_DEFINITIONS.update({
    "rsi_14": ("Momentum", "RSI de Wilder de 14 sesiones, escala 0–100."),
    "roc_10d": ("Momentum", "Rate of Change del cierre a 10 sesiones."),
    "roc_20d": ("Momentum", "Rate of Change del cierre a 20 sesiones."),
    "macd": ("Momentum", "EMA(12) - EMA(26), en puntos de índice."),
    "macd_signal": ("Momentum", "EMA(9) de MACD, en puntos de índice."),
    "macd_hist": ("Momentum", "MACD menos su línea de señal, en puntos de índice."),
    "macd_pct": ("Momentum", "MACD dividido por el cierre."),
    "macd_signal_pct": ("Momentum", "Línea de señal MACD dividida por el cierre."),
    "macd_hist_pct": ("Momentum", "Histograma MACD dividido por el cierre."),
    "zscore_close_20d": ("Momentum", "(Close - SMA20) / desviación típica de Close de 20 sesiones."),
    "day_of_week": ("Estacionalidad", "Día de semana de la fecha de negociación; lunes=0.",),
    "day_of_month": ("Estacionalidad", "Día calendario del mes, 1–31."),
    "week_of_year": ("Estacionalidad", "Semana ISO del año, 1–53."),
    "month_of_year": ("Estacionalidad", "Mes calendario, 1–12."),
    "dow_sin": ("Estacionalidad", "Codificación seno cíclica del día de semana."),
    "dow_cos": ("Estacionalidad", "Codificación coseno cíclica del día de semana."),
    "month_sin": ("Estacionalidad", "Codificación seno cíclica del mes."),
    "month_cos": ("Estacionalidad", "Codificación coseno cíclica del mes."),
    "day_of_month_sin": ("Estacionalidad", "Codificación seno cíclica del día del mes."),
    "day_of_month_cos": ("Estacionalidad", "Codificación coseno cíclica del día del mes."),
    "pre_holiday": ("Estacionalidad", "Sesión previa a un cierre programado de NYSE; fallback transparente a gaps observados si el calendario no está instalado."),
    "post_holiday": ("Estacionalidad", "Sesión posterior a un cierre programado de NYSE; fallback transparente a gaps observados si el calendario no está instalado."),
    "month_start_3": ("Estacionalidad", "Una de las tres primeras sesiones observadas del mes, identificable en tiempo real."),
    "month_end_3": ("Estacionalidad", "Una de las tres últimas sesiones programadas del mes, según el calendario NYSE."),
    "volume_spike": ("Volumen", "Indicador: volumen actual > 2 × media móvil de volumen de 20 sesiones."),
    "volume_ratio_20d": ("Volumen", "Volumen actual dividido por la media móvil de 20 sesiones."),
    "obv": ("Volumen", "On-Balance Volume acumulado: volumen con signo del cambio de cierre."),
    "obv_slope_20d": ("Volumen", "Cambio de OBV en 20 sesiones dividido por volumen total de 20 sesiones."),
})


def _market_calendar_flags(index: pd.DatetimeIndex) -> tuple[pd.Series, pd.Series]:
    """Create pre/post NYSE closure flags using a known session calendar.

    If the optional NYSE calendar is absent, observed weekday gaps are used as
    a transparent fallback; in that mode a data outage can be mistaken for a
    holiday, so the report labels the limitation.
    """
    pre = np.zeros(len(index), dtype=bool)
    post = np.zeros(len(index), dtype=bool)
    if len(index) == 0:
        return pd.Series(pre, index=index), pd.Series(post, index=index)
    try:
        import pandas_market_calendars as mcal
        cal = mcal.get_calendar("NYSE")
        start = (index.min() - pd.Timedelta(days=10)).date().isoformat()
        end = (index.max() + pd.Timedelta(days=10)).date().isoformat()
        schedule = cal.schedule(start_date=start, end_date=end)
        sessions = set(pd.DatetimeIndex(schedule.index).date)
        calendar_days = pd.date_range(start=start, end=end, freq="B")
        closed_weekdays = set(calendar_days.date) - sessions
        for position, date in enumerate(index):
            next_weekday = (date + pd.offsets.BDay(1)).date()
            previous_weekday = (date - pd.offsets.BDay(1)).date()
            pre[position] = next_weekday in closed_weekdays
            post[position] = previous_weekday in closed_weekdays
    except Exception:
        dates = index.values.astype("datetime64[D]")
        if len(index) > 1:
            weekday_gaps = np.busday_count(dates[:-1], dates[1:]) > 1
            pre[:-1] = weekday_gaps
            post[1:] = weekday_gaps
    return pd.Series(pre, index=index), pd.Series(post, index=index)


def build_features(ohlcv: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """Return (features, forward targets, chosen close series).

    Features at row t use information through the close of t only; targets are
    forward close-to-close returns and are never passed into model X.
    """
    index = ohlcv.index
    close_raw = ohlcv["close"]
    if "adj_close" in ohlcv:
        close = ohlcv["adj_close"].where(ohlcv["adj_close"].notna(), close_raw)
    else:
        close = close_raw.copy()
    close = pd.to_numeric(close, errors="coerce").astype(float).rename("analysis_close")
    daily_return = close.pct_change()
    f = pd.DataFrame(index=index)

    for window in RETURN_WINDOWS:
        f[f"return_{window}d"] = close.pct_change(window)
    for window in VOL_WINDOWS:
        f[f"rolling_vol_{window}d"] = daily_return.rolling(window, min_periods=window).std() * np.sqrt(252.0)
    vol60 = daily_return.rolling(60, min_periods=60).std() * np.sqrt(252.0)
    f["volatility_ratio_20_60"] = f["rolling_vol_20d"] / vol60.replace(0, np.nan)

    for window in SMA_WINDOWS:
        sma = close.rolling(window, min_periods=window).mean()
        f[f"sma_{window}d"] = sma
        f[f"dist_sma_{window}d"] = close / sma - 1.0
        f[f"slope_sma_{window}d"] = sma.diff(5) / (5.0 * close)

    high = pd.to_numeric(ohlcv.get("high", pd.Series(np.nan, index=index)), errors="coerce").astype(float)
    low = pd.to_numeric(ohlcv.get("low", pd.Series(np.nan, index=index)), errors="coerce").astype(float)
    previous_close = close.shift(1)
    true_range = pd.concat(
        [(high - low).abs(), (high - previous_close).abs(), (low - previous_close).abs()], axis=1
    ).max(axis=1, skipna=True)
    # No OHLC coverage means the row-wise max is also missing.
    if high.isna().all() or low.isna().all():
        true_range[:] = np.nan
    else:
        true_range = true_range.where(high.notna() & low.notna())
    f["atr_14d"] = true_range.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    f["atr_pct_14d"] = f["atr_14d"] / close

    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100.0 - 100.0 / (1.0 + rs)
    rsi = rsi.mask((loss == 0) & (gain > 0), 100.0)
    rsi = rsi.mask((loss == 0) & (gain == 0), 50.0)
    f["rsi_14"] = rsi
    f["roc_10d"] = close.pct_change(10)
    f["roc_20d"] = close.pct_change(20)

    ema12 = close.ewm(span=12, min_periods=12, adjust=False).mean()
    ema26 = close.ewm(span=26, min_periods=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, min_periods=9, adjust=False).mean()
    f["macd"] = macd
    f["macd_signal"] = macd_signal
    f["macd_hist"] = macd - macd_signal
    f["macd_pct"] = macd / close
    f["macd_signal_pct"] = macd_signal / close
    f["macd_hist_pct"] = f["macd_hist"] / close
    rolling_mean20 = close.rolling(20, min_periods=20).mean()
    rolling_std20 = close.rolling(20, min_periods=20).std()
    f["zscore_close_20d"] = (close - rolling_mean20) / rolling_std20.replace(0, np.nan)

    dow = pd.Series(index.dayofweek, index=index, dtype=float)
    day = pd.Series(index.day, index=index, dtype=float)
    month = pd.Series(index.month, index=index, dtype=float)
    iso_week = pd.Series(index.isocalendar().week.astype(int).to_numpy(), index=index, dtype=float)
    f["day_of_week"] = dow
    f["day_of_month"] = day
    f["week_of_year"] = iso_week
    f["month_of_year"] = month
    f["dow_sin"] = np.sin(2 * np.pi * dow / 5.0)
    f["dow_cos"] = np.cos(2 * np.pi * dow / 5.0)
    f["month_sin"] = np.sin(2 * np.pi * (month - 1) / 12.0)
    f["month_cos"] = np.cos(2 * np.pi * (month - 1) / 12.0)
    f["day_of_month_sin"] = np.sin(2 * np.pi * (day - 1) / 31.0)
    f["day_of_month_cos"] = np.cos(2 * np.pi * (day - 1) / 31.0)
    pre, post = _market_calendar_flags(index)
    f["pre_holiday"] = pre.astype(float)
    f["post_holiday"] = post.astype(float)
    periods = pd.Series(index.to_period("M"), index=index)
    position_in_month = periods.groupby(periods).cumcount()
    f["month_start_3"] = (position_in_month < 3).astype(float)
    # Month-end uses a published calendar, never the subsequently observed
    # number of price rows. Calendar dates are known at decision time.
    try:
        import pandas_market_calendars as mcal
        cal = mcal.get_calendar("NYSE")
        schedule = cal.schedule(
            start_date=(index.min() - pd.Timedelta(days=5)).date().isoformat(),
            end_date=(index.max() + pd.Timedelta(days=5)).date().isoformat(),
        )
        sessions = pd.DatetimeIndex(schedule.index)
        last_sessions = sessions.to_series(index=sessions).groupby(sessions.to_period("M")).tail(3).index
        last_session_dates = set(last_sessions.date)
        f["month_end_3"] = pd.Series(index.date, index=index).isin(last_session_dates).astype(float)
    except Exception:
        month_ends = (index.to_period("M") + 1).to_timestamp()
        calendar_days_remaining = np.busday_count(index.values.astype("datetime64[D]"), month_ends.values.astype("datetime64[D]"))
        f["month_end_3"] = (calendar_days_remaining <= 3).astype(float)

    volume = pd.to_numeric(ohlcv.get("volume", pd.Series(np.nan, index=index)), errors="coerce").astype(float)
    volume_mean20 = volume.rolling(20, min_periods=20).mean()
    f["volume_ratio_20d"] = volume / volume_mean20.replace(0, np.nan)
    f["volume_spike"] = (f["volume_ratio_20d"] > 2.0).astype(float).where(f["volume_ratio_20d"].notna())
    signed_volume = np.sign(daily_return).fillna(0.0) * volume.fillna(0.0)
    f["obv"] = signed_volume.cumsum().where(volume.notna().cummax())
    volume_sum20 = volume.rolling(20, min_periods=20).sum().replace(0, np.nan)
    f["obv_slope_20d"] = f["obv"].diff(20) / volume_sum20
    if volume.isna().all():
        for name in ("volume_ratio_20d", "volume_spike", "obv", "obv_slope_20d"):
            f[name] = np.nan

    targets = pd.DataFrame(index=index)
    for horizon in (1, 3, 5, 10, 20):
        targets[f"forward_return_{horizon}d"] = close.shift(-horizon) / close - 1.0
        targets[f"direction_{horizon}d"] = np.sign(targets[f"forward_return_{horizon}d"]).replace(0, np.nan)

    f = f.replace([np.inf, -np.inf], np.nan)
    targets = targets.replace([np.inf, -np.inf], np.nan)
    return f, targets, close


def feature_catalog(features: pd.DataFrame) -> pd.DataFrame:
    records = []
    for name in features.columns:
        category, definition = FEATURE_DEFINITIONS.get(name, (FEATURE_GROUPS.get(name, "Otro"), "Indicador derivado."))
        values = features[name]
        records.append({
            "feature": name,
            "category": category,
            "definition": definition,
            "non_missing": int(values.notna().sum()),
            "missing": int(values.isna().sum()),
            "available": bool(values.notna().any()),
            "used_by_ml": name in MODEL_FEATURES,
            "used_by_discovery": name in CONTINUOUS_PATTERN_FEATURES,
        })
    return pd.DataFrame(records)
