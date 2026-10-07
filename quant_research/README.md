# Motor de investigación cuantitativa (S&P 500)

Herramienta reproducible de investigación, no una señal de inversión. Lee CSV/Parquet o una base DuckDB en modo solo lectura, crea indicadores sin mirar hacia delante, explora reglas y compara modelos con validación cronológica.

## Estado de los datos en este checkout

No se encontró un fichero `.duckdb` ni una conexión DuckDB persistida en el repositorio. Sí está disponible `economics/^GSPC.csv` (3.522 filas, febrero de 2005–febrero de 2019, OHLCV). El informe incluido se calcula exclusivamente con ese fichero y no representa datos actuales. El programa también admite una base DuckDB que se proporcione al ejecutarlo.

## Instalación y ejecución

Desde la raíz del repositorio:

```bash
python -m pip install -r quant_research/requirements.txt
python -m quant_research.run_research \
  --data 'economics/^GSPC.csv' \
  --out quant_research/output
```

Para una base DuckDB:

```bash
python -m quant_research.run_research \
  --database /ruta/mercado.duckdb \
  --table esquema.tabla_precios \
  --out quant_research/output
```

Sin `--table`, el motor lista las tablas/vistas y elige la relación con mejor cobertura de fecha y cierre. Las consultas son de solo lectura. Los nombres de columnas habituales (`Date`, `Open`, `High`, `Low`, `Close`, `Adj Close`, `Volume`) se reconocen sin distinguir mayúsculas; se aceptan variantes comunes. Si una columna OHLCV no existe, la función correspondiente se marca como no disponible.

`--help` muestra los parámetros de coste, número de pliegues, cortes y tamaño del conjunto de reglas de validación.

## Qué genera

- `report.md`: informe en español, conclusiones, límites y referencias a los artefactos.
- `sql_used.sql`: SQL de catálogo, extracción y perfilado reproducible.
- `tables.csv`, `data_quality.csv`, `descriptive_stats.csv`, `annual_regimes.csv`, `structural_shift_tests.csv`.
- `features.csv` (opcional con `--export-features`), `feature_catalog.csv`.
- `pattern_ranking.csv` (solo reglas que superan los filtros), `pattern_candidates.csv` (candidatas de holdout, también las rechazadas), `pattern_periods.csv`.
- `model_metrics.csv`, `model_fold_metrics.csv`, `model_predictions.csv`, `backtests.csv`, `feature_importance.csv`, `shap_status.csv`.
- Gráficos de distribución, regímenes, drawdown y validación.

## Salvaguardas estadísticas

- Corte cronológico único para el motor de reglas; los umbrales de cuantiles se calculan solo con el segmento de descubrimiento.
- Discovery exhaustivo hasta cuatro condiciones (una por familia conceptual); el holdout independiente y el ranking publicable se restringen a tres condiciones para penalizar complejidad. Se evalúan reglas simples además de combinaciones.
- Corrección Benjamini–Hochberg sobre todos los tests del cribado (dirección × horizonte incluidos). La selección de candidatas se hace en descubrimiento; la evaluación final se realiza en un holdout posterior independiente y corrige otra vez los valores p.
- El contraste de holdout usa errores estándar HAC/Newey–West para no tratar como independientes resultados temporales solapados. Se excluyen reglas con menos de 100 casos en descubrimiento u holdout.
- Filtros de publicación: win rate fuera de muestra ≥55%, p y q de holdout ≤0,05, media direccional positiva, Sharpe neto positivo y habilidad positiva en al menos 3 de 4 subperiodos. La complejidad reduce la puntuación de robustez.
- ML con `TimeSeriesSplit`/ventana expansiva, `gap` igual al horizonte del target, sin partición aleatoria ni tuning sobre el holdout. Se comparan Logistic Regression, Random Forest, Gradient Boosting y, cuando están instalados, XGBoost, LightGBM y CatBoost.
- Backtest de reglas y modelos con señal conocida al cierre, ejecución en la siguiente apertura y mantenimiento alineado al horizonte pronosticado (1/3/5 sesiones); las señales diarias con solapamiento se promedian para limitar la exposición bruta a 1. Coste configurable (por defecto 5 pb por cambio de una unidad de posición). Incluye long/short/caja; cash=0% de tipo libre de riesgo. No incluye impacto de mercado.

Los p-valores de cribado son una aproximación binomial usada únicamente para reducir el universo; no sustituyen el contraste HAC de holdout. La búsqueda exhaustiva no elimina el sesgo de selección. Resultados nulos son resultados válidos.

## Pruebas

```bash
python -m pytest quant_research/tests
```
