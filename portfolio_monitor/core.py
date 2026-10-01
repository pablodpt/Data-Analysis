"""Analytics shared by the dashboard and batch report. Market database is read-only."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import duckdb


def config(path):
    path = Path(path).resolve()
    cfg = json.loads(path.read_text(encoding="utf-8"))
    for key in ("database", "ledger", "report_dir"):
        cfg[key] = str((path.parent / cfg[key]).resolve())
    if cfg.get("base_currency", "USD") != "USD":
        raise ValueError("Esta version requiere USD; no convierte divisas.")
    return cfg


def read_ledger(path):
    df = pd.read_csv(path, keep_default_na=False)
    required = {"date", "type", "symbol", "quantity", "price", "amount", "fee", "currency", "note"}
    if not required.issubset(df.columns):
        raise ValueError(f"Faltan columnas en ledger: {required - set(df.columns)}")
    df["date"] = pd.to_datetime(df.date, errors="raise").dt.normalize()
    for col in ("quantity", "price", "amount", "fee"):
        df[col] = pd.to_numeric(df[col], errors="raise")
        if not np.isfinite(df[col]).all() or (df[col] < 0).any():
            raise ValueError(f"{col}: se requieren numeros finitos no negativos")
    allowed = {"DEPOSIT", "WITHDRAWAL", "BUY", "SELL", "DIVIDEND", "FEE", "SPLIT"}
    if not df.type.isin(allowed).all() or not df.currency.eq("USD").all():
        raise ValueError("Tipo no admitido o moneda distinta de USD")
    for r in df.itertuples():
        if r.type in {"BUY", "SELL", "SPLIT", "DIVIDEND"} and not r.symbol:
            raise ValueError("Operacion sin symbol")
        if r.type in {"BUY", "SELL", "SPLIT"} and r.quantity <= 0:
            raise ValueError("quantity debe ser positiva; para SPLIT es el multiplicador")
        if r.type in {"BUY", "SELL"} and r.price <= 0:
            raise ValueError("Precio de ejecucion debe ser positivo")
        if r.type not in {"BUY", "SELL"} and r.fee != 0:
            raise ValueError("fee solo se admite en BUY/SELL; usar FEE para otros gastos")
        if r.type in {"BUY", "SELL", "SPLIT"} and r.amount != 0:
            raise ValueError("amount debe ser cero en BUY/SELL/SPLIT")
        if r.type not in {"BUY", "SELL", "SPLIT"} and (r.quantity != 0 or r.price != 0):
            raise ValueError("quantity y price deben ser cero en movimientos de efectivo")
        if r.type == "SPLIT" and r.price != 0:
            raise ValueError("price debe ser cero en SPLIT")
    return df.sort_values("date", kind="stable")


def portfolio(prices, ledger, tickers, as_of):
    """Daily close NAV; flows assumed at beginning of day. No shorting/margin/FX."""
    end = pd.Timestamp(as_of).normalize()
    ledger = ledger[ledger.date <= end].copy()
    if ledger.empty:
        return {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    start = ledger.date.min()
    p = prices.copy()
    p["date"] = pd.to_datetime(p.date).dt.normalize()
    if p.duplicated(["date", "symbol"]).any():
        raise ValueError("Precios duplicados por symbol/date; corregir antes de valorar")
    p = p[p.date <= end]
    days = pd.date_range(start, end)
    symbols = sorted(set(ledger.loc[ledger.symbol.ne(""), "symbol"]))
    if p.empty:
        wide = pd.DataFrame(index=days, columns=symbols, dtype=float)
    else:
        wide = p.pivot(index="date", columns="symbol", values="close")
        wide = wide.reindex(wide.index.union(days)).sort_index().ffill().reindex(days)
    qty = dict.fromkeys(symbols, 0.0)
    prev_values = dict.fromkeys(symbols, 0.0)
    cash = prev_nav = 0.0
    daily, attribution = [], []
    groups = {d: g for d, g in ledger.groupby("date", sort=False)}
    for day in days:
        flow = other_pnl = 0.0
        symbol_cash = dict.fromkeys(symbols, 0.0)
        for r in groups.get(day, pd.DataFrame()).itertuples():
            if r.type == "DEPOSIT":
                cash += r.amount; flow += r.amount
            elif r.type == "WITHDRAWAL":
                cash -= r.amount; flow -= r.amount
            elif r.type == "FEE":
                cash -= r.amount; other_pnl -= r.amount
            elif r.type == "DIVIDEND":
                cash += r.amount; symbol_cash[r.symbol] += r.amount
            elif r.type == "SPLIT":
                qty[r.symbol] *= r.quantity
            else:
                sign = 1 if r.type == "BUY" else -1
                qty[r.symbol] += sign * r.quantity
                delta = -sign * r.quantity * r.price - r.fee
                cash += delta; symbol_cash[r.symbol] += delta
            if cash < -1e-7 or any(q < -1e-7 for q in qty.values()):
                raise ValueError(f"Saldo negativo o venta sin posicion el {day.date()}")
        values = {}
        for s, q in qty.items():
            price = wide.at[day, s] if s in wide else np.nan
            if q > 1e-9 and (not np.isfinite(price) or price <= 0):
                raise ValueError(f"No hay precio close valido para {s} en {day.date()}")
            values[s] = q * price if q > 1e-9 else 0.0
            attribution.append({"date": day, "symbol": s,
                                "pnl_usd": values[s] - prev_values[s] + symbol_cash[s]})
        attribution.append({"date": day, "symbol": "CASH_COSTS", "pnl_usd": other_pnl})
        nav = cash + sum(values.values())
        pnl = nav - prev_nav - flow
        denominator = prev_nav + flow
        if denominator <= 0 and abs(pnl) > 1e-7:
            raise ValueError("Retorno no definido: capital inicial diario no positivo")
        ret = pnl / denominator if denominator > 0 else 0.0
        daily.append({"date": day, "nav": nav, "cash": cash, "external_flow": flow,
                      "pnl_usd": pnl, "return": ret})
        prev_values, prev_nav = values, nav
    daily = pd.DataFrame(daily)
    daily["wealth"] = (1 + daily["return"]).cumprod()
    daily["drawdown"] = daily.wealth / daily.wealth.cummax().clip(lower=1) - 1
    # Calendar-day series includes weekend cash events; annualization uses 365.
    vol = daily["return"].std(ddof=1) * np.sqrt(365) if len(daily) > 1 else None
    sector_map = tickers.set_index("symbol").sector.to_dict() if not tickers.empty else {}
    positions = pd.DataFrame([{"symbol": s, "quantity": q, "value_usd": prev_values[s],
        "weight": prev_values[s] / prev_nav if prev_nav else 0,
        "sector": sector_map.get(s, "Sin sector"),
        "price_date": p.loc[p.symbol.eq(s), "date"].max()} for s, q in qty.items() if q > 1e-9])
    attribution = pd.DataFrame(attribution)
    attribution["sector"] = attribution.symbol.map(sector_map).fillna("Sin sector / gastos")
    stats = {"nav_usd": prev_nav, "cash_usd": cash, "pnl_usd": float(daily.pnl_usd.sum()),
             "twr": float(daily.wealth.iloc[-1] - 1), "max_drawdown": float(daily.drawdown.min()),
             "volatility_calendar_annualized": vol, "days": len(daily)}
    return stats, positions, daily, attribution


def analyze(cfg, as_of):
    cutoff = pd.Timestamp(as_of).normalize()
    next_day = cutoff + pd.Timedelta(days=1)
    since = cutoff - pd.Timedelta(days=cfg.get("event_days", 7)-1)
    alerts = []
    frames = {}
    ledger = read_ledger(cfg["ledger"])
    with duckdb.connect(cfg["database"], read_only=True) as con:
        tables = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
        def query(name, sql, params):
            if name not in tables:
                alerts.append({"level": "WARN", "message": f"Tabla ausente: {name}"})
                return pd.DataFrame()
            return con.execute(sql, params).df()
        tickers = query("tickers", "SELECT symbol, company_name, sector, currency FROM tickers", [])
        if not tickers.empty and tickers.symbol.duplicated().any():
            raise ValueError("tickers contiene simbolos duplicados")
        start = min(cutoff - pd.Timedelta(days=cfg.get("lookback_days", 365)),
                    ledger.date.min()) if not ledger.empty else cutoff-pd.Timedelta(days=365)
        prices = query("prices", "SELECT symbol,date,close,adj_close,volume FROM prices WHERE date <= ? AND date >= ?", [cutoff, start-pd.Timedelta(days=30)])
        if prices.empty:
            raise ValueError("No hay precios para el periodo solicitado")
        frames["freshness"] = con.execute("SELECT symbol, max(date) AS last_price FROM prices WHERE date <= ? GROUP BY symbol", [cutoff]).df()
        for r in frames["freshness"].itertuples():
            if (cutoff - pd.Timestamp(r.last_price)).days > cfg.get("stale_days", 7):
                alerts.append({"level": "WARN", "message": f"Precio obsoleto: {r.symbol}, {r.last_price}"})
        signals = query("signals", """SELECT * FROM signals WHERE as_of_date <= ? AND computed_at < ?
            QUALIFY row_number() OVER (PARTITION BY symbol ORDER BY as_of_date DESC, computed_at DESC)=1
            ORDER BY composite_score DESC NULLS LAST""", [cutoff, next_day])
        previous = query("signals", """SELECT * FROM signals WHERE as_of_date < ? AND computed_at < ?
            QUALIFY row_number() OVER (PARTITION BY symbol ORDER BY as_of_date DESC, computed_at DESC)=1""", [since, since])
        if not signals.empty:
            signals["rank"] = np.arange(1, len(signals)+1)
            if not previous.empty:
                previous = previous.sort_values("composite_score", ascending=False, na_position="last")
                previous["previous_rank"] = np.arange(1, len(previous)+1)
                signals = signals.merge(previous[["symbol", "previous_rank", "composite_score"]].rename(columns={"composite_score": "previous_score"}), on="symbol", how="left")
                signals["score_change"] = signals.composite_score - signals.previous_score
                signals["rank_improvement"] = signals.previous_rank - signals["rank"]
            else:
                alerts.append({"level": "INFO", "message": "Sin snapshot anterior comparable de signals"})
            stale = pd.to_datetime(signals.as_of_date) < cutoff-pd.Timedelta(days=cfg.get("stale_days", 7))
            if stale.any():
                alerts.append({"level": "WARN", "message": f"{stale.sum()} señales obsoletas"})
        frames["opportunities"] = signals
        frames["news"] = query("news", "SELECT * FROM news WHERE published_date >= ? AND published_date < ? AND loaded_at < ? QUALIFY row_number() OVER (PARTITION BY symbol,url ORDER BY loaded_at)=1 ORDER BY published_date DESC", [since, next_day, next_day])
        frames["filings"] = query("filings", "SELECT DISTINCT symbol, form_type, filed_date, period_end, accession_number, source_url FROM filings WHERE filed_date >= ? AND filed_date <= ? AND loaded_at < ? ORDER BY filed_date DESC", [since, cutoff, next_day])
        for name in ("dividends", "splits"):
            frames[name] = query(name, f'SELECT * FROM {name} WHERE date >= ? AND date <= ? ORDER BY date DESC', [since, cutoff])
        frames["fundamentals"] = query("fundamentals", "SELECT * FROM fundamentals WHERE snapshot_date <= ? QUALIFY row_number() OVER (PARTITION BY symbol ORDER BY snapshot_date DESC)=1", [cutoff])
        previous_funds = query("fundamentals", "SELECT * FROM fundamentals WHERE snapshot_date < ? QUALIFY row_number() OVER (PARTITION BY symbol ORDER BY snapshot_date DESC)=1", [since])
        funds = frames["fundamentals"]
        if not funds.empty and not previous_funds.empty:
            columns = [c for c in ["revenue_growth", "earnings_growth", "profit_margin", "operating_margin", "roe", "debt_to_equity", "free_cashflow"] if c in funds and c in previous_funds]
            changes = funds[["symbol", "snapshot_date"] + columns].merge(previous_funds[["symbol", "snapshot_date"] + columns], on="symbol", suffixes=("", "_previous"))
            for col in columns:
                changes[col + "_change"] = changes[col] - changes[col + "_previous"]
            frames["fundamental_changes"] = changes
        if not funds.empty:
            stale_funds = pd.to_datetime(funds.snapshot_date) < cutoff-pd.Timedelta(days=cfg.get("stale_days", 7))
            if stale_funds.any():
                alerts.append({"level": "WARN", "message": f"{stale_funds.sum()} snapshots fundamentales superan el umbral de antiguedad"})
        dividend_history = query("dividends", "SELECT * FROM dividends WHERE date <= ?", [cutoff])
        if not dividend_history.empty:
            dividend_history = dividend_history.sort_values(["symbol", "date"])
            dividend_history["previous_amount"] = dividend_history.groupby("symbol").amount.shift()
            candidates = dividend_history[(pd.to_datetime(dividend_history.date) >= since) & (dividend_history.amount < dividend_history.previous_amount)].copy()
            frames["possible_dividend_cuts"] = candidates
            if not candidates.empty:
                alerts.append({"level": "INFO", "message": "Dividendos inferiores al pago anterior: revisar splits, extraordinarios y periodicidad antes de interpretar como recorte"})
        frames["updates"] = query("update_log", "SELECT * FROM update_log WHERE started_at < ? ORDER BY started_at DESC LIMIT 10", [next_day])
        if not frames["updates"].empty and frames["updates"].iloc[0]["status"] != "OK":
            alerts.append({"level": "WARN", "message": "La ultima actualizacion no tiene estado OK"})
        # Notify, never auto-book corporate actions: source semantics may be unknown.
        all_splits = query("splits", "SELECT * FROM splits WHERE date >= ? AND date <= ?", [start, cutoff])
        traded = set(ledger.loc[ledger.type.isin(["BUY", "SELL"]), "symbol"])
        if not all_splits.empty:
            for r in all_splits[all_splits.symbol.isin(traded)].itertuples():
                booked = ledger[(ledger.type == "SPLIT") & (ledger.symbol == r.symbol) & (ledger.date == pd.Timestamp(r.date))]
                if booked.empty:
                    alerts.append({"level": "WARN", "message": f"Revisar split {r.symbol} {r.date}: no registrado; NAV puede ser incorrecto"})
    if tickers.empty and ledger.symbol.ne("").any():
        raise ValueError("Se requiere tickers para verificar moneda de la cartera")
    if not tickers.empty:
        missing = (set(ledger.symbol)-{""}) - set(tickers.symbol)
        if missing:
            raise ValueError(f"No se puede verificar moneda: faltan tickers {sorted(missing)}")
        held = tickers[tickers.symbol.isin(set(ledger.symbol)-{""})]
        if held.currency.isna().any() or not held.currency.eq("USD").all():
            raise ValueError("Cartera con moneda no USD o desconocida")
    stats, positions, daily, attribution = portfolio(prices, ledger, tickers, cutoff)
    if not positions.empty:
        for r in positions.itertuples():
            if r.weight > cfg.get("max_position_weight", .15):
                alerts.append({"level": "WARN", "message": f"Concentracion {r.symbol}: {r.weight:.1%}"})
        sectors = positions.groupby("sector", as_index=False).agg(weight=("weight", "sum"), value_usd=("value_usd", "sum"))
        for r in sectors.itertuples():
            if r.weight > cfg.get("max_sector_weight", .35):
                alerts.append({"level": "WARN", "message": f"Concentracion sector {r.sector}: {r.weight:.1%}"})
        frames["sectors"] = sectors
    if stats and stats["max_drawdown"] < cfg.get("drawdown_warning", -.15):
        alerts.append({"level": "WARN", "message": "Drawdown historico supera el umbral"})
    frames.update(positions=positions, daily=daily, attribution_daily=attribution)
    if not attribution.empty:
        frames["attribution_symbols"] = attribution.groupby("symbol", as_index=False).pnl_usd.sum()
        frames["attribution_sectors"] = attribution.groupby("sector", as_index=False).pnl_usd.sum()
        frames["attribution_week"] = attribution[attribution.date >= since].groupby("symbol", as_index=False).pnl_usd.sum()
    frames["alerts"] = pd.DataFrame(alerts, columns=["level", "message"])
    metadata = {"as_of": str(cutoff.date()), "generated_at_utc": pd.Timestamp.now(tz="UTC").isoformat(),
                "database": cfg["database"], "ledger_sha256": hashlib.sha256(Path(cfg["ledger"]).read_bytes()).hexdigest(),
                "configuration": cfg, "version": "1.0"}
    return {"stats": stats, "frames": frames, "metadata": metadata}
