"""Run the complete S&P 500 research pipeline."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any

import numpy as np
import pandas as pd

from .discovery import MIN_CASES, run_discovery
from .exploration import (
    annual_regimes,
    data_quality_report,
    descriptive_statistics,
    distribution_outliers,
    structural_shift_tests,
)
from .features import build_features, feature_catalog
from .io import load_market_data, normalized_name, standardize_ohlcv
from .models import run_walk_forward
from .plots import create_plots
from .report import render_report


REPO_ROOT = Path(__file__).resolve().parents[1]


def _json_native(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_native(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_native(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if value is pd.NA:
        return None
    return value


def _quote_identifier(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'


def _write_sql_log(path: Path, loaded: Any, original_frame: pd.DataFrame, mapping: dict[str, str]) -> None:
    lines = [
        "-- SQL de lectura ejecutado por el motor (DuckDB read-only cuando está disponible).",
        f"-- Fuente: {loaded.source}",
        f"-- Relación seleccionada: {loaded.relation}",
        "",
    ]
    lines.extend(statement.rstrip(";") + ";" for statement in loaded.sql_statements)
    lines.extend(["", "-- Plantilla de perfil para la relación seleccionada (ajustar schema/tabla o ruta):"])
    if loaded.source.startswith("DuckDB read-only:"):
        pieces = loaded.relation.split(".", 1)
        relation_sql = f"{_quote_identifier(pieces[0])}.{_quote_identifier(pieces[1])}" if len(pieces) == 2 else _quote_identifier(loaded.relation)
    else:
        source_path = Path(loaded.source).as_posix().replace("'", "''")
        if Path(source_path).suffix.lower() == ".parquet":
            relation_sql = f"read_parquet('{source_path}')"
        else:
            relation_sql = f"read_csv_auto('{source_path}', header=true, sample_size=-1)"
    date_col = mapping.get("date")
    close_col = mapping.get("adj_close") or mapping.get("close")
    if date_col and close_col:
        date_sql = _quote_identifier(date_col)
        close_sql = _quote_identifier(close_col)
        lines.extend([
            "SELECT",
            "    COUNT(*) AS row_count,",
            f"    COUNT(*) FILTER (WHERE {date_sql} IS NULL) AS missing_date,",
            f"    COUNT(*) FILTER (WHERE {close_sql} IS NULL) AS missing_close,",
            f"    MIN({date_sql}) AS first_date, MAX({date_sql}) AS last_date,",
            f"    MIN({close_sql}) AS min_close, MAX({close_sql}) AS max_close,",
            f"    AVG({close_sql}) AS mean_close, STDDEV_SAMP({close_sql}) AS sd_close",
            f"FROM {relation_sql};",
        ])
        lines.extend([
            "",
            f"SELECT {date_sql}, COUNT(*) AS rows_per_date FROM {relation_sql}",
            f"GROUP BY {date_sql} HAVING COUNT(*) > 1 ORDER BY {date_sql};",
        ])
    lines.extend([
        "",
        "-- El perfil de faltantes/quantiles y las features se completan en Python;",
        "-- ver quant_research/sql/exploration.sql para plantillas parametrizables.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _flatten_summary(summary: dict[str, Any]) -> pd.DataFrame:
    records: list[dict[str, str]] = []
    for key, value in summary.items():
        if isinstance(value, dict):
            for inner_key, inner_value in value.items():
                records.append({"metric": f"{key}.{inner_key}", "value": json.dumps(_json_native(inner_value), ensure_ascii=False)})
        else:
            records.append({"metric": key, "value": json.dumps(_json_native(value), ensure_ascii=False)})
    return pd.DataFrame(records)


def _arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Descubrimiento cuantitativo y backtesting temporal del S&P 500.")
    parser.add_argument("--data", default=str(REPO_ROOT / "economics" / "^GSPC.csv"), help="CSV/Parquet con OHLCV (por defecto: economics/^GSPC.csv).")
    parser.add_argument("--database", help="Ruta a una base DuckDB; se abre read-only.")
    parser.add_argument("--table", help="Tabla/vista DuckDB, opcionalmente schema.tabla.")
    parser.add_argument("--out", default="quant_research/output", help="Directorio de entregables.")
    parser.add_argument("--discovery-fraction", type=float, default=0.70, help="Fracción cronológica inicial para descubrimiento (0.55–0.85).")
    parser.add_argument("--min-cases", type=int, default=MIN_CASES, help="Mínimo de eventos requerido (no debe ser menor de 100).")
    parser.add_argument("--holdout-rules", type=int, default=100, help="Presupuesto de candidatas seleccionadas solo en train para contrastar en holdout.")
    parser.add_argument("--max-conditions", type=int, default=4, choices=(1, 2, 3, 4), help="Máximo de condiciones en el cribado automático.")
    parser.add_argument("--folds", type=int, default=5, help="Pliegues expansivos para TimeSeriesSplit.")
    parser.add_argument("--cost-bps", type=float, default=5.0, help="Coste por cambio de una unidad de posición, en puntos básicos.")
    parser.add_argument("--export-features", action="store_true", help="Exporta features y targets completos a features.csv.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _arg_parser().parse_args(argv)
    if args.database and args.data != str(REPO_ROOT / "economics" / "^GSPC.csv"):
        raise SystemExit("Use --database o --data, no ambos.")
    if not 0.55 <= args.discovery_fraction <= 0.85:
        raise SystemExit("--discovery-fraction debe estar entre 0.55 y 0.85.")
    if args.min_cases < 100:
        raise SystemExit("Por diseño escéptico, --min-cases no puede ser menor de 100.")
    if args.holdout_rules < 20:
        raise SystemExit("--holdout-rules debe ser al menos 20 para el ajuste de FDR OOS.")
    if args.folds < 3:
        raise SystemExit("--folds debe ser al menos 3.")
    if args.cost_bps < 0:
        raise SystemExit("--cost-bps no puede ser negativo.")

    output = Path(args.out)
    if not output.is_absolute():
        output = (REPO_ROOT / output).resolve()
    output.mkdir(parents=True, exist_ok=True)

    loaded = load_market_data(
        data_path=None if args.database else args.data,
        database_path=args.database,
        table=args.table,
    )
    raw_original = loaded.frame.copy()
    ohlcv, column_mapping, cleanup = standardize_ohlcv(raw_original)
    if len(ohlcv) < 500:
        raise SystemExit(f"Muestra insuficiente: {len(ohlcv)} sesiones; se requieren al menos 500.")

    features, targets, analysis_close = build_features(ohlcv)
    cutoff_position = int(np.floor(len(ohlcv) * args.discovery_fraction)) - 1
    cutoff_position = min(max(cutoff_position, 1), len(ohlcv) - 2)
    cutoff = pd.Timestamp(ohlcv.index[cutoff_position])

    quality = data_quality_report(raw_original, ohlcv, cleanup)
    descriptive = descriptive_statistics(raw_original, ohlcv, features)
    annual = annual_regimes(ohlcv, analysis_close)
    shift_tests = structural_shift_tests(analysis_close)
    catalog = feature_catalog(features)

    print(f"[1/5] Cargados {len(ohlcv):,} registros desde {loaded.source} ({ohlcv.index.min().date()}–{ohlcv.index.max().date()}).")
    print(f"[2/5] Features: {len(features.columns)}; corte de descubrimiento: {cutoff.date()}.")
    discovery = run_discovery(
        features=features,
        targets=targets,
        prices=ohlcv,
        close=analysis_close,
        cutoff=cutoff,
        cost_bps=args.cost_bps,
        min_cases=args.min_cases,
        max_holdout_rules=args.holdout_rules,
        max_conditions=args.max_conditions,
    )
    print(
        f"[3/5] Discovery: {discovery['summary'].get('candidate_rules', 0):,} reglas; "
        f"{discovery['summary'].get('hypotheses_tested', 0):,} tests direccionales; "
        f"{discovery['summary'].get('validated_patterns', 0)} validados."
    )
    ml = run_walk_forward(features, targets, ohlcv, cost_bps=args.cost_bps, n_splits=args.folds)
    print(f"[4/5] ML: {len(ml['metrics'])} combinaciones modelo/tarea/horizonte; importancia {ml['best_classifier_1d'] or 'sin clasificador válido'}. ")

    tables = loaded.tables.copy()
    if not tables.empty and loaded.source.startswith("DuckDB read-only:"):
        selected_schema, selected_table = loaded.relation.split(".", 1)
        tables["selected_for_analysis"] = (tables["schema"] == selected_schema) & (tables["table"] == selected_table)
    else:
        tables["selected_for_analysis"] = True

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": loaded.source,
        "relation": loaded.relation,
        "database_used": loaded.source.startswith("DuckDB read-only:"),
        "start_date": ohlcv.index.min().date().isoformat(),
        "end_date": ohlcv.index.max().date().isoformat(),
        "rows": int(len(ohlcv)),
        "input_rows": int(len(raw_original)),
        "duplicate_date_rows": cleanup.get("duplicate_date_rows", 0),
        "invalid_date_rows": cleanup.get("invalid_date_rows", 0),
        "rows_removed_bad_close": cleanup.get("rows_removed_bad_close", 0),
        "cutoff_date": cutoff.date().isoformat(),
        "discovery_fraction": args.discovery_fraction,
        "cost_bps": args.cost_bps,
        "folds": args.folds,
        "min_cases": args.min_cases,
        "selected_close": "Adj Close with Close fallback" if ohlcv["adj_close"].notna().any() else "Close",
        "ohlcv_columns_available": {column: bool(ohlcv[column].notna().any()) for column in ("open", "high", "low", "close", "adj_close", "volume")},
        **distribution_outliers(analysis_close),
    }

    # Save all requested reproducible tables.
    tables.to_csv(output / "tables.csv", index=False)
    quality.to_csv(output / "data_quality.csv", index=False)
    descriptive.to_csv(output / "descriptive_stats.csv", index=False)
    annual.to_csv(output / "annual_regimes.csv", index=False)
    shift_tests.to_csv(output / "structural_shift_tests.csv", index=False)
    catalog.to_csv(output / "feature_catalog.csv", index=False)
    discovery["condition_catalog"].to_csv(output / "condition_catalog.csv", index=False)
    discovery["candidates"].to_csv(output / "pattern_candidates.csv", index=False)
    discovery["ranking"].to_csv(output / "pattern_ranking.csv", index=False)
    discovery["periods"].to_csv(output / "pattern_periods.csv", index=False)
    ml["metrics"].to_csv(output / "model_metrics.csv", index=False)
    ml["fold_metrics"].to_csv(output / "model_fold_metrics.csv", index=False)
    ml["predictions"].to_csv(output / "model_predictions.csv", index=False)
    ml["backtests"].to_csv(output / "backtests.csv", index=False)
    ml["feature_importance"].to_csv(output / "feature_importance.csv", index=False)
    ml["shap_status"].to_csv(output / "shap_status.csv", index=False)
    ml["model_status"].to_csv(output / "model_availability.csv", index=False)
    _flatten_summary(discovery["summary"]).to_csv(output / "discovery_summary.csv", index=False)
    (output / "discovery_summary.json").write_text(
        json.dumps(_json_native(discovery["summary"]), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if args.export_features:
        export = features.join(targets).copy()
        export.insert(0, "close_analysis", analysis_close)
        export.to_csv(output / "features.csv", index_label="date")
    metadata["discovery"] = discovery["summary"]
    metadata["column_mapping"] = column_mapping
    metadata["model_names_available"] = sorted(ml["model_status"].loc[ml["model_status"]["available"], "model"].unique().tolist())
    metadata["models_best_classifier_1d"] = ml["best_classifier_1d"]
    (output / "analysis_metadata.json").write_text(
        json.dumps(_json_native(metadata), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _write_sql_log(output / "sql_used.sql", loaded, raw_original, column_mapping)

    all_pattern_backtests = pd.DataFrame(discovery["backtest_metrics"])
    pattern_curves = discovery["backtest_curves"]
    model_backtests = ml["backtests"]
    if not all_pattern_backtests.empty:
        all_pattern_backtests.to_csv(output / "pattern_backtests.csv", index=False)
    plot_files = create_plots(
        output_dir=output,
        prices=ohlcv,
        close=analysis_close,
        features=features,
        targets=targets,
        annual=annual,
        model_metrics=ml["metrics"],
        model_curves=ml["backtest_curves"],
        pattern_curves=pattern_curves,
        pattern_ranking=discovery["ranking"],
        feature_importance=ml["feature_importance"],
        cutoff=cutoff,
    )
    metadata["plot_files"] = plot_files
    metadata["shap_status"] = ml["shap_status"].to_dict(orient="records")
    (output / "analysis_metadata.json").write_text(
        json.dumps(_json_native(metadata), ensure_ascii=False, indent=2), encoding="utf-8"
    )

    render_report(
        output_path=output / "report.md",
        metadata=metadata,
        tables=tables,
        quality=quality,
        descriptive=descriptive,
        annual=annual,
        shift_tests=shift_tests,
        feature_catalog=catalog,
        discovery_summary=discovery["summary"],
        conditions=discovery["condition_catalog"],
        candidates=discovery["candidates"],
        ranking=discovery["ranking"],
        periods=discovery["periods"],
        model_metrics=ml["metrics"],
        fold_metrics=ml["fold_metrics"],
        backtests=model_backtests,
        feature_importance=ml["feature_importance"],
        shap_status=ml["shap_status"],
        plot_files=plot_files,
    )
    print(f"[5/5] Entregables guardados en: {output}")
    print(f"Informe: {output / 'report.md'}")
    if discovery["ranking"].empty:
        print("Conclusión: no se validó ningún patrón bajo los filtros predefinidos; consulte las candidatas rechazadas.")
    else:
        print(f"Conclusión: {len(discovery['ranking'])} patrón(es) superaron los filtros; confirmar con datos independientes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
