"""Spanish Markdown report rendering."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable
import json

import numpy as np
import pandas as pd


def _fmt(value: Any, kind: str = "num", digits: int = 3) -> str:
    if value is None or pd.isna(value):
        return "—"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if kind == "pct":
        return f"{100.0 * number:.2f}%"
    if kind == "bp":
        return f"{number * 10000.0:.1f} pb"
    if kind == "p":
        return "<0.001" if number < 0.001 else f"{number:.3f}"
    if kind == "num6":
        return f"{number:.6f}"
    if kind == "int":
        return f"{int(number):,}".replace(",", ".")
    return f"{number:.{digits}f}"


def _fmt_int(value: Any) -> str:
    try:
        return f"{int(value):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


def _markdown_table(frame: pd.DataFrame, columns: list[tuple[str, str, str]], max_rows: int | None = None) -> str:
    """Render a small table without depending on optional `tabulate`."""
    if frame is None or frame.empty:
        return "_Sin filas._"
    shown = frame.head(max_rows) if max_rows is not None else frame
    headers = [label for _, label, _ in columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for _, row in shown.iterrows():
        cells = []
        for key, _, kind in columns:
            value = row.get(key, np.nan)
            text = _fmt(value, kind) if kind in {"pct", "bp", "int", "num", "p", "num6"} else str(value) if pd.notna(value) else "—"
            text = text.replace("|", "\\|").replace("\n", " ")
            cells.append(text)
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _escape(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def render_report(
    output_path: str | Path,
    metadata: dict[str, Any],
    tables: pd.DataFrame,
    quality: pd.DataFrame,
    descriptive: pd.DataFrame,
    annual: pd.DataFrame,
    shift_tests: pd.DataFrame,
    feature_catalog: pd.DataFrame,
    discovery_summary: dict[str, Any],
    conditions: pd.DataFrame,
    candidates: pd.DataFrame,
    ranking: pd.DataFrame,
    periods: pd.DataFrame,
    model_metrics: pd.DataFrame,
    fold_metrics: pd.DataFrame,
    backtests: pd.DataFrame,
    feature_importance: pd.DataFrame,
    shap_status: pd.DataFrame,
    plot_files: list[str],
) -> None:
    out = Path(output_path)
    lines: list[str] = []
    lines.extend([
        "# Informe de Quant Research — S&P 500",
        "",
        f"**Generado:** {metadata.get('generated_at', '—')}  ",
        f"**Fuente:** `{metadata.get('source', '—')}`  ",
        f"**Relación:** `{metadata.get('relation', '—')}`  ",
        f"**Muestra:** {metadata.get('start_date', '—')} a {metadata.get('end_date', '—')} · {_fmt_int(metadata.get('rows', 0))} observaciones",
        "",
        "> **Conclusión ejecutiva.** Este informe busca señales predictivas, no describe el mercado por sí mismo. Solo se consideran hallazgos los patrones que superan los filtros preespecificados de frecuencia, significancia fuera de muestra, consistencia temporal y backtest neto. No inferir causalidad ni usarlo como recomendación financiera.",
        "",
    ])
    if not metadata.get("database_used", False):
        lines.extend([
            "> **DuckDB:** no se consultó una relación DuckDB en esta ejecución; se utilizó el CSV local disponible. El CLI admite una base DuckDB read-only mediante `--database` y puede listar tablas con `--table` opcional.",
            "",
        ])
    lines.extend([
        "## 1. Resumen de resultados",
        "",
        f"- Reglas/hipótesis de cribado con n≥{discovery_summary.get('min_cases', 100)} en descubrimiento: **{_fmt_int(discovery_summary.get('hypotheses_tested', 0))} tests direccionales** (antes de FDR).",
        f"- Átomos de condición: **{_fmt_int(discovery_summary.get('conditions', 0))}**; conjunciones generadas: **{_fmt_int(discovery_summary.get('candidate_rules', 0))}**; máximo {discovery_summary.get('max_conditions', 4)} condiciones, combinadas entre familias distintas.",
        f"- Reglas evaluadas en holdout cronológico: **{discovery_summary.get('holdout_candidates_tested', 0)}**; reglas con ≥100 casos OOS: **{discovery_summary.get('holdout_candidates_with_100_cases', 0)}**; reglas que superaron todos los filtros: **{discovery_summary.get('validated_patterns', 0)}**.",
    ])
    if ranking.empty:
        lines.append("- **No se validó ningún patrón** bajo los filtros establecidos. La recomendación cuantitativa es no desplegar una regla basada en esta muestra; una tabla vacía de hallazgos validados es preferible a rebajar los criterios tras ver los resultados.")
    else:
        lines.append(f"- Se validaron **{len(ranking)}** patrón(es); ver ranking y fichas en la sección 5.")
    lines.extend([
        "- La muestra termina en **{end}**; no constituye información actual. La serie es de precio del índice y puede no incluir dividendos; el volumen agregado del índice no es directamente ejecutable.".format(end=metadata.get("end_date", "—")),
        "",
        "## 2. Fuente, tablas y calidad de datos",
        "",
        f"Relación seleccionada: `{metadata.get('relation', '—')}`. El cierre de análisis usa `Adj Close` cuando está disponible y no nulo; en caso contrario, `Close`.",
        "",
        _markdown_table(tables, [
            ("schema", "Esquema", "text"), ("table", "Tabla/relación", "text"), ("type", "Tipo", "text"),
            ("row_count", "Filas", "int"), ("ohlcv_coverage", "Campos OHLCV", "int"),
        ], max_rows=30),
        "",
        f"Filas de entrada: {metadata.get('input_rows', 0)}; filas tras limpieza: {metadata.get('rows', 0)}; fechas duplicadas descartadas: {metadata.get('duplicate_date_rows', 0)}; fechas inválidas: {metadata.get('invalid_date_rows', 0)}; cierres inválidos eliminados: {metadata.get('rows_removed_bad_close', 0)}.",
        "",
        "Se calculan nulos por columna, valores únicos y atípicos univariados por regla de 1,5×IQR. Ese umbral es descriptivo y no elimina observaciones: los eventos de cola permanecen en la serie.",
        "",
    ])
    if quality is not None and not quality.empty:
        missing_cols = quality[(quality["missing"].fillna(0) > 0) & ~quality["column"].astype(str).str.startswith("cleanup_")]
        if missing_cols.empty:
            lines.append("No se observaron nulos en las columnas originales usadas por el análisis. Los NaN de calentamiento de indicadores (por ejemplo, SMA200) son esperados y se excluyen de ML hasta que las features están disponibles.")
        else:
            lines.append("Columnas con faltantes relevantes:")
            lines.append(_markdown_table(missing_cols.sort_values("missing_pct", ascending=False), [
                ("column", "Columna", "text"), ("missing", "Nulos", "int"), ("missing_pct", "% nulos", "num"),
                ("iqr_outliers_1_5", "Atípicos IQR", "int"),
            ], max_rows=20))
    lines.extend([
        "",
        "### Estadísticas y distribuciones",
        "",
        "`descriptive_stats.csv` incluye media, desviación, cuantiles 1/5/25/50/75/95/99, asimetría, curtosis y conteo IQR para columnas numéricas, retornos y una selección de indicadores.",
        "",
    ])
    return_stats = descriptive[descriptive["series"] == "close_to_close_return_1d"] if not descriptive.empty else pd.DataFrame()
    if not return_stats.empty:
        row = return_stats.iloc[0]
        lines.append(
            f"Retorno diario close-to-close: media {_fmt(row['mean'], 'pct')}, desviación {_fmt(row['std'], 'pct')}, "
            f"q01 {_fmt(row['q01'], 'pct')}, mediana {_fmt(row['median'], 'pct')}, q99 {_fmt(row['q99'], 'pct')}, "
            f"mínimo {_fmt(row['min'], 'pct')}, máximo {_fmt(row['max'], 'pct')}; atípicos 1,5×IQR = {int(row['iqr_outliers_1_5'])}.")
    lines.extend([
        "",
        "### Cambios temporales / regímenes",
        "",
        "La tabla anual y la figura de volatilidad muestran cambios descriptivos. Tres contrastes de dos mitades se fijan antes de minar reglas, no buscan la fecha de ruptura que maximice el estadístico y sus p se ajustan con Holm; no prueban un régimen permanente.",
        "",
        _markdown_table(annual, [
            ("year", "Año", "text"), ("sessions", "Sesiones", "int"), ("price_return", "Retorno precio", "pct"),
            ("annualized_volatility", "Vol anualizada", "pct"), ("daily_sharpe_rf0", "Sharpe diario", "num"),
            ("up_session_rate", "Días al alza", "pct"), ("max_drawdown_within_year", "Máx. DD intra-año", "pct"),
        ]),
        "",
        _markdown_table(shift_tests, [
            ("test", "Contraste", "text"), ("split_date", "Corte", "text"), ("first_mean", "1ª mitad", "num6"),
            ("second_mean", "2ª mitad", "num6"), ("p_value", "p", "p"),
            ("p_value_holm", "p Holm", "p"),
        ]),
        "",
        "## 3. Features generadas",
        "",
        f"Se generaron **{len(feature_catalog)}** columnas de features; {int(feature_catalog['used_by_ml'].sum())} figuran como entrada candidata para ML. Las SMA absolutas, ATR en puntos y OBV se conservan y documentan, pero el set ML prioriza distancias, pendientes y ratios estacionarios para reducir dependencia del nivel del índice.",
        "",
        "Familias: retornos 1/3/5/10/20d; volatilidad anualizada rolling 5/10/20, ratio 20/60 y ATR(14) de Wilder; SMA 5/10/20/50/200, distancia y pendiente; RSI14, ROC10/20, MACD/Signal/Histograma y z-score20; día de semana/mes/semana ISO, mes, codificación cíclica y flags de cierres festivos; volumen relativo/spike y OBV/pendiente. `feature_catalog.csv` contiene la definición operativa y faltantes por indicador. Al recibirse una única serie (^GSPC), no se calcula fuerza relativa cross-sectional entre activos; se analizan momentum y tendencia de esa misma serie.",
        "",
        "**Festivos:** cuando se dispone de calendario NYSE se usan sesiones programadas; el informe marca pre/post-cierre. En su defecto el código cae a gaps observados, que pueden confundirse con días de datos ausentes y quedan documentados en la implementación.",
        "",
        "## 4. Discovery Engine y validación de patrones",
        "",
        f"Corte cronológico: descubrimiento hasta **{discovery_summary.get('discovery_end', '—')}**; holdout desde **{discovery_summary.get('holdout_start', '—')}**. Los cuantiles de umbral se estiman solo en descubrimiento. Se probaron horizontes de 1, 3 y 5 sesiones; etiquetas de precio forward close-to-close.",
        "",
        f"En descubrimiento hubo {_fmt_int(discovery_summary.get('train_nominal_p_le_05_directional_tests', 0))} tests con p nominal≤0,05 y {_fmt_int(discovery_summary.get('train_bh_q_le_05_directional_tests', 0))} con q Benjamini–Hochberg≤0,05, de {_fmt_int(discovery_summary.get('hypotheses_tested', 0))} tests elegibles. El cribado usa una aproximación binomial solo para ordenar y reducir candidatos; no se interpreta como inferencia final.",
        "",
        "El holdout está reservado a las candidatas elegidas usando únicamente descubrimiento. En el holdout se contrasta la mejora de acierto frente a los días sin señal con errores estándar HAC/Newey–West (rezago máximo al menos 5, ampliado al horizonte), y se vuelve a controlar FDR sobre las candidatas. Los retornos forward de 3/5d se solapan; el ajuste HAC no elimina todos los sesgos posibles.",
        "",
        f"Filtros de publicación: ≥{metadata.get('min_cases', 100)} observaciones tanto en descubrimiento como en holdout; p y q OOS ≤0,05; win rate direccional OOS ≥55%; retorno direccional medio positivo; Sharpe neto positivo; habilidad positiva en ≥3 de 4 subperiodos con ≥20 señales cada uno; como máximo 3 condiciones para publicar. El ranking ordena primero la consistencia, después penaliza complejidad.",
        "",
        "### Ranking final de patrones validados",
        "",
    ])
    if ranking.empty:
        lines.append("**Ninguna regla superó simultáneamente los filtros. No se relajan los umbrales.** Las reglas cribadas pero rechazadas permanecen en `pattern_candidates.csv` para auditoría.")
    else:
        lines.append(_markdown_table(ranking, [
            ("rank", "Rank", "int"), ("pattern", "Patrón", "text"), ("test_cases", "Casos OOS", "int"),
            ("test_win_rate", "Win rate", "pct"), ("test_mean_directional_return", "Retorno medio direccional", "pct"),
            ("oos_net_sharpe", "Sharpe neto", "num"), ("robustness_score", "Robustez 0–100", "num"),
        ], max_rows=20))
        for _, row in ranking.iterrows():
            lines.extend([
                "",
                f"#### Patrón {int(row['rank'])}: {_escape(row['pattern'])}",
                "",
                f"- **Regla/dirección:** `{_escape(row['pattern'])}` → {row['direction']} a {int(row['horizon'])} sesión(es).",
                f"- **Lógica económica:** interpretación de la condición candidata, no causalidad; el efecto OOS es lo único que se reporta como validación.",
                f"- **Frecuencia:** {int(row['test_cases'])} casos OOS; win rate {_fmt(row['test_win_rate'], 'pct')} frente a base {_fmt(row['test_baseline_rate'], 'pct')}.",
                f"- **Retorno esperado:** {_fmt(row['test_mean_directional_return'], 'pct')} direccional medio por horizonte; raw {_fmt(row['test_raw_mean_return'], 'pct')}.",
                f"- **Backtest:** Sharpe neto {_fmt(row['oos_net_sharpe'])}, CAGR {_fmt(row['oos_cagr'], 'pct')}, MDD {_fmt(row['oos_max_drawdown'], 'pct')}.",
                f"- **Significancia/robustez:** HAC p={_fmt(row['test_p_value_hac'])}, q={_fmt(row['test_q_value'])}; {int(row['periods_positive_skill'])}/{int(row['periods_valid'])} subperiodos con skill; score {_fmt(row['robustness_score'])}/100.",
                "- **Riesgo de sobreajuste:** reducido respecto a una regla minada dentro de muestra, pero no nulo: la selección múltiple, el cambio de régimen y el uso de un único holdout siguen siendo límites.",
            ])
    lines.extend([
        "",
        "### Candidatas top de descubrimiento (NO validadas por defecto)",
        "",
        "Esta tabla es un registro de búsqueda, no una recomendación. La selección de estas filas se hizo en el train; cada estado rechazado nombra los filtros incumplidos.",
        "",
    ])
    if candidates is not None and not candidates.empty:
        top = candidates.sort_values("holdout_rank").head(12)
        lines.append(_markdown_table(top, [
            ("holdout_rank", "Selección", "int"), ("pattern", "Condición", "text"), ("horizon", "H", "int"),
            ("direction", "Dirección", "text"), ("train_cases", "n train", "int"), ("test_cases", "n OOS", "int"),
            ("test_win_rate", "WR OOS", "pct"), ("test_p_value_hac", "HAC p", "p"),
            ("test_q_value", "q OOS", "p"), ("oos_net_sharpe", "Sharpe", "num"),
        ]))
        lines.extend(["", "Métricas de subperiodo para candidatas: `pattern_periods.csv` (incluye los periodos donde la señal no tuvo skill o frecuencia suficiente)."])
    else:
        lines.append("No se generaron candidatas elegibles con el mínimo de observaciones del train.")
    lines.extend([
        "",
        "## 5. Machine learning exploratorio",
        "",
        f"Validación: `TimeSeriesSplit` expansivo, {metadata.get('folds', 5)} pliegues, `gap` igual al horizonte (purga del solapamiento del target). Imputación/escalado se ajustan dentro del pliegue. No hay particiones aleatorias ni tuning de hiperparámetros sobre el test.",
        "",
        "Modelos de clasificación: Logistic Regression, Random Forest, Gradient Boosting, XGBoost, LightGBM y CatBoost. En regresión se usan Ridge Regression, Random Forest, Gradient Boosting, XGBoost, LightGBM y CatBoost (la regresión logística no aplica). Los modelos que no se pudieron importar aparecen como `skipped` en `model_metrics.csv`/`model_availability.csv`.",
        "",
    ])
    if model_metrics is not None and not model_metrics.empty:
        ranked_models = model_metrics.copy()
        if "status" in ranked_models:
            ranked_models = ranked_models[ranked_models["status"].astype(str).str.startswith(("ok", "partial"))]
        if not ranked_models.empty:
            one_day = ranked_models[(ranked_models["task"] == "classification") & (ranked_models["horizon"] == 1)].sort_values("roc_auc", ascending=False)
            five_day = ranked_models[(ranked_models["task"] == "classification") & (ranked_models["horizon"] == 5)].sort_values("roc_auc", ascending=False)
            lines.extend([
                "### Clasificación direction(t+1)",
                "",
                _markdown_table(one_day, [
                    ("model", "Modelo", "text"), ("oos_observations", "n OOS", "int"), ("accuracy", "Accuracy", "pct"),
                    ("baseline_accuracy", "Baseline mayoritaria", "pct"), ("precision", "Precision", "pct"), ("recall", "Recall", "pct"), ("f1", "F1", "num"),
                    ("roc_auc", "ROC AUC", "num"), ("sharpe", "Sharpe neto", "num"),
                    ("cagr", "CAGR", "pct"), ("max_drawdown", "MDD", "pct"),
                ], max_rows=12),
                "",
                "### Clasificación direction(t+5)",
                "",
                _markdown_table(five_day, [
                    ("model", "Modelo", "text"), ("oos_observations", "n OOS", "int"), ("accuracy", "Accuracy", "pct"),
                    ("baseline_accuracy", "Baseline mayoritaria", "pct"), ("precision", "Precision", "pct"), ("recall", "Recall", "pct"), ("f1", "F1", "num"),
                    ("roc_auc", "ROC AUC", "num"), ("sharpe", "Sharpe neto", "num"),
                    ("cagr", "CAGR", "pct"), ("max_drawdown", "MDD", "pct"),
                ], max_rows=12),
                "",
            ])
            for horizon in (1, 5):
                subset = ranked_models[(ranked_models["task"] == "regression") & (ranked_models["horizon"] == horizon)].sort_values("roc_auc", ascending=False)
                lines.extend([
                    f"### Regresión return(t+{horizon})",
                    "",
                    _markdown_table(subset, [
                        ("model", "Modelo", "text"), ("oos_observations", "n OOS", "int"), ("mae", "MAE", "num"),
                        ("rmse", "RMSE", "num"), ("r2", "R²", "num"), ("spearman_ic", "Spearman IC", "num"),
                        ("accuracy", "Accuracy signo", "pct"), ("baseline_accuracy", "Baseline mayoritaria", "pct"),
                        ("roc_auc", "ROC AUC signo", "num"),
                        ("sharpe", "Sharpe neto", "num"), ("max_drawdown", "MDD", "pct"),
                    ], max_rows=12),
                    "",
                ])
        else:
            lines.append("No hubo ajuste ML exitoso; consulte `model_metrics.csv` y `model_availability.csv`.")
    else:
        lines.append("No se produjeron métricas de modelos.")
    lines.extend([
        "`baseline_accuracy` es el clasificador mayoritario sin features; se reporta para evitar confundir una tasa de acierto alta por tendencia base con capacidad predictiva. `model_fold_metrics.csv` contiene el desglose temporal por fold; `model_predictions.csv` contiene predicciones OOF. En regresión, ROC AUC y accuracy se aplican al signo pronosticado. El backtest usa umbral p(up)≥0,55 / ≤0,45 para clasificación y signo de retorno para regresión.",
        "",
        "## 6. Backtests y costes",
        "",
        f"Se usa coste de **{metadata.get('cost_bps', 5.0):.1f} pb por cambio de una unidad de posición**, long/short/caja, cash=0%, señal conocida al cierre y entrada en la siguiente apertura. Cada señal se mantiene por el horizonte pronosticado (1/3/5 sesiones); las vintages solapadas se promedian para limitar la exposición bruta a 1. El P&L es apertura-a-apertura; si no hay Open, se usa Close-to-Close con retardo. La ejecución sobre el propio índice S&P 500 es un proxy; no modela ETF/futuros, dividendos, borrow fees, impacto, spread ni límites de capacidad.",
        "",
    ])
    if backtests is not None and not backtests.empty:
        lines.append(_markdown_table(backtests, [
            ("strategy", "Estrategia", "text"), ("bars", "Barras", "int"), ("total_return", "Retorno total", "pct"),
            ("cagr", "CAGR", "pct"), ("sharpe", "Sharpe", "num"), ("max_drawdown", "MDD", "pct"),
            ("exposure", "Exposición", "pct"), ("trades", "Entradas", "int"),
        ], max_rows=25))
    else:
        lines.append("No hay backtests ejecutables en la muestra.")
    lines.extend([
        "",
        "## 7. Information Gain, Mutual Information e importancia",
        "",
        "La información mutua (bits) de cada conjunción frente a la etiqueta alcista se calcula con su tabla de contingencia en train; para una partición binaria, coincide con la ganancia de información. Solo se exporta para la shortlist holdout para mantener el tamaño manejable; el cribado completo contabiliza la familia de hipótesis y su FDR.",
        "",
    ])
    if feature_importance is not None and not feature_importance.empty:
        perm = feature_importance[feature_importance["importance_type"] == "permutation_roc_auc"].sort_values("importance_mean", ascending=False)
        if not perm.empty:
            lines.append("Importancia por permutación OOS (último fold cronológico; variación de ROC AUC):")
            lines.append(_markdown_table(perm, [
                ("feature", "Feature", "text"), ("importance_mean", "Δ AUC medio", "num"),
                ("importance_std", "Desv. entre permutaciones", "num"),
            ], max_rows=12))
            lines.append("")
        shap_rows = feature_importance[feature_importance["importance_type"] == "shap_mean_abs"].sort_values("importance_mean", ascending=False)
        if not shap_rows.empty:
            lines.append("SHAP (media de valor absoluto en la muestra explicada; unidad del output del modelo):")
            lines.append(_markdown_table(shap_rows, [
                ("feature", "Feature", "text"), ("importance_mean", "mean |SHAP|", "num"),
            ], max_rows=12))
            lines.append("")
    if shap_status is not None and not shap_status.empty:
        status_row = shap_status.iloc[0].to_dict()
        lines.append(f"Estado de explicación: `{json.dumps(status_row, ensure_ascii=False, default=str)}`.")
    else:
        lines.append("SHAP no produjo explicaciones; ver `shap_status.csv`.")
    lines.extend([
        "",
        "## 8. Figuras",
        "",
    ])
    plot_captions = {
        "price_volatility_drawdown.png": "Precio, volatilidad realizada y drawdown",
        "daily_return_distribution.png": "Distribución y CDF empírica de retornos diarios",
        "annual_regimes.png": "Retorno y volatilidad por año",
        "oos_equity_curves.png": "Equity OOS de modelos/reglas seleccionadas",
        "feature_importance.png": "Importancia de variables en el último fold OOS",
    }
    for name in plot_files:
        caption = plot_captions.get(name, name)
        lines.extend([f"### {caption}", "", f"![{caption}]({name})", ""])
    lines.extend([
        "",
        "## 9. Recomendación y limitaciones",
        "",
    ])
    if ranking.empty:
        lines.append("**No desplegar ninguna señal** de este experimento. La muestra ofrece precios históricos hasta 2019-02 y la búsqueda amplia no encontró una regla que sobreviva a todas las pruebas requeridas. Accuracy o Sharpe atractivos de un modelo individual no bastan si faltan estabilidad, datos recientes, estrategia ejecutable y validación externa independiente.")
    else:
        lines.append("Considerar las reglas validadas solo como hipótesis para una replicación independiente (datos posteriores, ETF/futuros y costes realistas); no desplegar ni asumir persistencia sin repetir el protocolo en un periodo nuevo.")
    lines.extend([
        "",
        "Limitaciones principales: muestra única y antigua; retornos de precio; posible volumen proxy; p-valores aproximados en el cribado; dependencia serial y solapamiento; un único holdout para reglas; variables técnicas muy correlacionadas; resultados ML con hiperparámetros fijos, no optimizados; backtest de baja fidelidad. Los valores p no implican causalidad.",
        "",
        "## 10. Archivos reproducibles",
        "",
        "- SQL de extracción/perfil: `sql_used.sql` y plantilla `../sql/exploration.sql`.",
        "- Configuración, corte y procedencia: `analysis_metadata.json` y `discovery_summary.json`.",
        "- Features/condiciones: `feature_catalog.csv`, `condition_catalog.csv`; `features.csv` solo si se solicitó `--export-features`.",
        "- Patrones: `pattern_ranking.csv`, `pattern_candidates.csv`, `pattern_periods.csv`.",
        "- ML/backtest: `model_metrics.csv`, `model_fold_metrics.csv`, `model_predictions.csv`, `backtests.csv`, `feature_importance.csv`, `shap_status.csv`.",
        "- Todos los retornos, condiciones y reglas usan sesiones ordenadas; no se usa validación aleatoria.",
        "",
        "---",
        "_Informe de investigación cuantitativa; no constituye asesoramiento financiero._",
    ])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
