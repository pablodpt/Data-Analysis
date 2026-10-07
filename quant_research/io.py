"""Read market data from CSV/Parquet or a read-only DuckDB relation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import pandas as pd


DATE_ALIASES = {"date", "datetime", "timestamp", "time", "trading_date", "as_of_date"}
CLOSE_ALIASES = {"close", "last", "settle", "price", "close_price"}
COLUMN_ALIASES = {
    "date": DATE_ALIASES,
    "open": {"open", "open_price"},
    "high": {"high", "high_price"},
    "low": {"low", "low_price"},
    "close": CLOSE_ALIASES,
    "adj_close": {"adj_close", "adjusted_close", "adjustedclose"},
    "volume": {"volume", "vol", "total_volume"},
}


@dataclass
class LoadedMarketData:
    frame: pd.DataFrame
    source: str
    relation: str
    tables: pd.DataFrame
    sql_statements: list[str]
    original_columns: list[str]


def normalized_name(name: Any) -> str:
    """Normalize a column name for alias matching."""
    text = str(name).strip().lower().replace("&", "and")
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text


def _quote_identifier(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'


def _qualified_name(schema: str, table: str) -> str:
    return f"{_quote_identifier(schema)}.{_quote_identifier(table)}"


def _map_market_columns(columns: list[str]) -> dict[str, str]:
    mapped: dict[str, str] = {}
    for original in columns:
        key = normalized_name(original)
        for standard, aliases in COLUMN_ALIASES.items():
            if key in aliases and standard not in mapped:
                mapped[standard] = original
    # Prefer an adjusted close for return/indicator calculations, but retain
    # both raw close columns when present.
    for original in columns:
        key = normalized_name(original)
        if key in {"adj_close", "adjusted_close", "adjustedclose"}:
            mapped["adj_close"] = original
    return mapped


def _relation_columns(connection: Any, qualified: str) -> list[str]:
    result = connection.execute(f"DESCRIBE SELECT * FROM {qualified}").fetchdf()
    if "column_name" in result.columns:
        return result["column_name"].astype(str).tolist()
    return result.iloc[:, 0].astype(str).tolist()


def _database_catalog(connection: Any) -> tuple[pd.DataFrame, list[str]]:
    catalog_sql = (
        "SELECT table_schema, table_name, table_type "
        "FROM information_schema.tables "
        "WHERE table_schema NOT IN ('information_schema', 'pg_catalog') "
        "ORDER BY table_schema, table_name"
    )
    catalog = connection.execute(catalog_sql).fetchdf()
    rows: list[dict[str, Any]] = []
    statements = [catalog_sql]
    for _, item in catalog.iterrows():
        schema, table = str(item["table_schema"]), str(item["table_name"])
        qualified = _qualified_name(schema, table)
        columns = _relation_columns(connection, qualified)
        count_sql = f"SELECT COUNT(*) AS row_count FROM {qualified}"
        try:
            count = int(connection.execute(count_sql).fetchone()[0])
        except Exception:
            count = None
        mapped = _map_market_columns(columns)
        rows.append({
            "schema": schema,
            "table": table,
            "type": str(item["table_type"]),
            "row_count": count,
            "columns": ", ".join(columns),
            "has_date": "date" in mapped,
            "has_close": "close" in mapped or "adj_close" in mapped,
            "ohlcv_coverage": sum(key in mapped for key in ("open", "high", "low", "close", "volume")),
        })
        statements.extend([f"DESCRIBE SELECT * FROM {qualified}", count_sql])
    return pd.DataFrame(rows), statements


def _select_relation(tables: pd.DataFrame, requested: str | None) -> tuple[str, str]:
    if tables.empty:
        raise ValueError("La base DuckDB no contiene tablas ni vistas visibles.")
    if requested:
        target = requested.split(".", 1)
        if len(target) == 2:
            schema, name = target
            hit = tables[(tables["schema"] == schema) & (tables["table"] == name)]
        else:
            name = target[0]
            hit = tables[tables["table"] == name]
        if hit.empty:
            raise ValueError(f"No se encontró la tabla/vista DuckDB solicitada: {requested}")
        row = hit.iloc[0]
        return str(row["schema"]), str(row["table"])

    suitable = tables[tables["has_date"] & tables["has_close"]].copy()
    if suitable.empty:
        raise ValueError(
            "No se encontró una tabla con una columna de fecha y otra de cierre. "
            "Indique --table o adapte los alias en quant_research/io.py."
        )
    suitable = suitable.sort_values(["ohlcv_coverage", "row_count"], ascending=False)
    chosen = suitable.iloc[0]
    return str(chosen["schema"]), str(chosen["table"])


def load_market_data(
    data_path: str | Path | None = None,
    database_path: str | Path | None = None,
    table: str | None = None,
) -> LoadedMarketData:
    """Load one market relation and retain a catalog/query trail.

    DuckDB is opened read-only. For CSV/Parquet DuckDB is used when installed;
    pandas is a deliberately supported fallback for lightweight environments.
    """
    if data_path is not None and database_path is not None:
        raise ValueError("Use --data o --database, no ambos.")

    if database_path is not None:
        try:
            import duckdb  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Para leer una base .duckdb instale quant_research/requirements.txt."
            ) from exc
        db_path = Path(database_path).expanduser().resolve()
        if not db_path.is_file():
            raise FileNotFoundError(f"No existe la base DuckDB: {db_path}")
        connection = duckdb.connect(str(db_path), read_only=True)
        try:
            catalog, statements = _database_catalog(connection)
            schema, selected = _select_relation(catalog, table)
            qualified = _qualified_name(schema, selected)
            extraction_sql = f"SELECT * FROM {qualified}"
            frame = connection.execute(extraction_sql).fetchdf()
            statements.append(extraction_sql)
        finally:
            connection.close()
        return LoadedMarketData(
            frame=frame,
            source=f"DuckDB read-only: {db_path}",
            relation=f"{schema}.{selected}",
            tables=catalog,
            sql_statements=statements,
            original_columns=[str(c) for c in frame.columns],
        )

    if data_path is None:
        raise ValueError("Proporcione --data o --database.")
    path = Path(data_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"No existe el fichero de datos: {path}")

    suffix = path.suffix.lower()
    relation = path.name
    statements: list[str] = []
    frame: pd.DataFrame
    try:
        import duckdb  # type: ignore

        connection = duckdb.connect(database=":memory:")
        escaped_path = str(path).replace("'", "''")
        if suffix == ".csv":
            sql = f"SELECT * FROM read_csv_auto('{escaped_path}', header=true, sample_size=-1)"
        elif suffix in {".parquet", ".pq"}:
            sql = f"SELECT * FROM read_parquet('{escaped_path}')"
        else:
            raise ValueError(f"Formato de datos no soportado: {suffix}")
        frame = connection.execute(sql).fetchdf()
        statements.append(sql)
        connection.close()
    except ImportError:
        if suffix == ".csv":
            frame = pd.read_csv(path)
            statements.append(f"-- DuckDB no instalado; fallback pandas.read_csv('{path}')")
        elif suffix in {".parquet", ".pq"}:
            frame = pd.read_parquet(path)
            statements.append(f"-- DuckDB no instalado; fallback pandas.read_parquet('{path}')")
        else:
            raise ValueError(f"Formato de datos no soportado: {suffix}")

    mapped = _map_market_columns([str(c) for c in frame.columns])
    if not ("date" in mapped and ("close" in mapped or "adj_close" in mapped)):
        raise ValueError(
            "El fichero necesita una fecha y un precio de cierre (Close/Adj Close). "
            f"Columnas encontradas: {list(frame.columns)}"
        )
    tables = pd.DataFrame([{
        "schema": "file",
        "table": relation,
        "type": suffix.lstrip("." ).upper(),
        "row_count": len(frame),
        "columns": ", ".join(map(str, frame.columns)),
        "has_date": "date" in mapped,
        "has_close": "close" in mapped or "adj_close" in mapped,
        "ohlcv_coverage": sum(key in mapped for key in ("open", "high", "low", "close", "volume")),
    }])
    return LoadedMarketData(
        frame=frame,
        source=str(path),
        relation=relation,
        tables=tables,
        sql_statements=statements,
        original_columns=[str(c) for c in frame.columns],
    )


def standardize_ohlcv(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str], dict[str, int]]:
    """Normalize OHLCV names, parse/sort dates, and remove unusable rows.

    Duplicate timestamps keep the last input observation. Counts are returned
    so the report can disclose every cleanup decision.
    """
    if frame.empty:
        raise ValueError("La relación de precios está vacía.")
    original = frame.copy()
    mapping = _map_market_columns([str(c) for c in original.columns])
    if "date" not in mapping or not ("close" in mapping or "adj_close" in mapping):
        raise ValueError("No se reconocieron las columnas fecha/cierre.")

    out = pd.DataFrame(index=original.index)
    for standard in ("date", "open", "high", "low", "close", "adj_close", "volume"):
        raw_name = mapping.get(standard)
        if raw_name is not None:
            out[standard] = original[raw_name]
    out["date"] = pd.to_datetime(out["date"], errors="coerce", utc=True).dt.tz_convert(None)
    for column in ("open", "high", "low", "close", "adj_close", "volume"):
        if column in out:
            out[column] = pd.to_numeric(out[column], errors="coerce")

    usable_price = out.get("adj_close", pd.Series(float("nan"), index=out.index))
    raw_close = out.get("close", pd.Series(float("nan"), index=out.index))
    usable_price = usable_price.where(usable_price.notna(), raw_close)
    stats = {
        "input_rows": int(len(out)),
        "invalid_date_rows": int(out["date"].isna().sum()),
        "invalid_or_nonpositive_close_rows": int((usable_price.isna() | (usable_price <= 0)).sum()),
    }
    out = out.dropna(subset=["date"])
    out = out.sort_values("date", kind="mergesort")
    stats["duplicate_date_rows"] = int(out["date"].duplicated(keep="last").sum())
    out = out.drop_duplicates(subset=["date"], keep="last").set_index("date")
    raw_close = out["close"] if "close" in out else pd.Series(float("nan"), index=out.index)
    adjusted = out["adj_close"] if "adj_close" in out else pd.Series(float("nan"), index=out.index)
    valid_price = adjusted.where(adjusted.notna(), raw_close)
    valid_close = valid_price.notna() & (valid_price > 0)
    stats["rows_removed_bad_close"] = int((~valid_close).sum())
    out = out.loc[valid_close]
    if "close" not in out:
        out["close"] = out["adj_close"]
    if "adj_close" not in out:
        out["adj_close"] = float("nan")
    if "open" not in out:
        out["open"] = float("nan")
    if "high" not in out:
        out["high"] = float("nan")
    if "low" not in out:
        out["low"] = float("nan")
    if "volume" not in out:
        out["volume"] = float("nan")
    out.index.name = "date"
    return out, mapping, stats
