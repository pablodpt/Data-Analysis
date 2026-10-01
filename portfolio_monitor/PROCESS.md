# Proceso completo: de DuckDB al informe (versión 2)

Este documento sustituye el alcance limitado de la primera entrega. Se implementa una **primera versión de investigación de las diez etapas**, no solo la interfaz. No es un sistema de trading en producción ni una demostración de rentabilidad. La fuente es tu DuckDB ya alimentado: este paquete no incluye nuevos descargadores de SEC/cotizaciones/noticias.

## Arquitectura

```text
DuckDB de mercado (solo lectura) ──┬─ 1. Auditoría
                                 ├─ 2. Ranking multifactor ─────────────┐
                                 ├─ 3. Backtest momentum              │
                                 ├─ 4. Contabilidad anual             │
                                 ├─ 5. Evaluación de señales          │
                                 ├─ 6. Carteras actuales ◄────────────┘
                                 │     + comparación walk-forward
                                 ├─ 7. PCA y exposiciones de objetivos
                                 ├─ 8. Eventos y atención de noticias
                                 └─ 9. Dividendos
Libro de operaciones (CSV) ────────── 10. Cartera real y atribución
                                                 ↓
                   runs/<run_id>/analytics.duckdb + HTML/CSV/JSON
                                                 ↓
                         Dashboard + informe programado
```

**Objetivos de cartera ≠ cartera realmente mantenida.** Los resultados del optimizador no crean operaciones en tu ledger ni se envían a un bróker. Sus backtests se mantienen separados de tu rendimiento real.

## Primer arranque completo: sin tu base

Desde la raíz del repositorio, Linux/macOS:

```bash
cd portfolio_monitor
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# Genera 30 empresas FICTICIAS, varias series anuales y señales históricas
python demo_research.py

# Ejecuta las 10 etapas y conserva la ejecución
python pipeline.py --config demo_full/config.json --as-of 2026-09-30 --strict

# Interfaz; seleccionar 2026-09-30 y pestaña «Proceso completo 1–9»
MONITOR_CONFIG=demo_full/config.json python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Windows PowerShell: crear entorno con `py -m venv .venv`, usar `.venv\Scripts\python.exe` en lugar de `python`, y arrancar `app.py`. Introducir `demo_full/config.json` en la barra lateral. `demo_research.py` no sobrescribe una base existente; para otra demo: `python demo_research.py --output otra_carpeta`.

La demo completa tiene ledger vacío: sirve para probar la investigación sin inventar operaciones. Para probar la cartera real con operaciones sintéticas sigue la demo corta de `README.md`.

## Conectar los datos reales

1. Copiar `config.example.json` a `config.json`.
2. Configurar `database`, `ledger` y `report_dir`. Rutas relativas al JSON, no al directorio de ejecución.
3. Introducir tus operaciones en `ledger.csv` según `README.md`, o dejar solo la cabecera si aún no quieres valorar una cartera.
4. Verificar en la documentación y con ejemplos del proveedor:
   - `adj_close` es una serie de **retorno total**, con splits y dividendos. Solo entonces activar `research.adj_close_is_total_return`.
   - Los dividendos por acción están ajustados a una base de splits comparable al corte. Solo entonces activar `research.dividends_split_adjusted`.
   - Para cartera real, `close` debe ser **no ajustado** y el ledger incluir splits explícitos. Esta condición es diferente de la primera.
5. Ejecutar:

```bash
python pipeline.py --config config.json --as-of 2026-09-30
```

Por defecto las dos confirmaciones están en `false`. **No activarlas solo para que desaparezca un bloqueo.** No se convierte automáticamente una serie cuyo significado se desconoce. Si el proveedor no cumple estas convenciones, se necesita una transformación específica, validada antes de analizar retornos o valorar posiciones.

`--strict` devuelve código 2 si hay etapas `BLOCKED`, `PARTIAL` o `ERROR`, útil para automatización. Sin `--strict`, un bloqueo esperado por poca historia no impide generar el resto del informe; los errores de ejecución sí devuelven código 2. Un fallo fatal al abrir la fuente puede terminar antes de crear el informe.

## Qué calcula exactamente cada punto

### 1. Auditoría — `research_01_audit_*`

Conteos, nulos por columna, duplicados en claves principales, precios inválidos y coherencia OHLC cuando está disponible. Los precios duplicados o inválidos bloquean cálculos de retornos; duplicados de tickers impiden las uniones de riesgo. La pestaña original añade antigüedad de precios, fundamentales, señales y estado del actualizador.

La auditoría no puede inferir si `adj_close` realmente incluye dividendos, si el dataset contiene empresas desaparecidas o si se han sobrescrito datos. Las tablas opcionales vacías bloquean solo sus etapas. Conteos corresponden a filas elegibles al corte, no necesariamente a toda la fuente.

### 2. Ranking — `research_02_ranking_result`

Cinco dimensiones con pesos iguales:

- Valoración: earnings yield (solo PER positivo), FCF/capitalización.
- Calidad: ROA y margen operativo.
- Crecimiento: ventas y beneficio.
- Momentum: aproximación 252–21 sesiones.
- Riesgo: menor volatilidad de 63 sesiones.

Percentiles dentro de sector, mínimo configurable de pares por variable. Exige al menos cuatro de cinco dimensiones; guarda valores brutos, cobertura y antigüedad. Los snapshots viejos se excluyen. Financials y Real Estate quedan sin puntuación genérica porque requieren métricas especializadas; no se simula un modelo bancario o de REITs. Los percentiles acotan extremos sin optimizar parámetros retrospectivamente.

Un score alto es una lista de investigación, no una estimación de retorno esperado ni una recomendación de compra.

### 3. Momentum — `research_03_momentum_*`

Se reconstruye desde precios para no asumir que las vistas existentes usan retornos ajustados. Señal al final del mes t: precio al final de t−1 / precio al final de t−12 − 1. El último mes parcial no se usa como formación.

Comparadores long-only:

- 20% superior global, equiponderado.
- 20% superior **por sector**, con igual peso entre sectores.
- Universo equiponderado.
- Universo con igual peso entre sectores (baseline adecuado para distinguir selección de sesgo sectorial).

Filtro de volumen monetario medio de las últimas 63 sesiones anteriores a formación. Ejecución al cierre de la siguiente sesión, salida al cierre siguiente a la próxima formación. Costes sobre compras + ventas, incluyendo la entrada inicial, usando pesos anteriores desplazados por sus retornos. No descuenta liquidación terminal porque la cartera sigue abierta.

Guarda pesos, fechas, retornos brutos/netos, rotación, CAGR, volatilidad, drawdown, resultados por año y ratio retorno/volatilidad con **rf=0 explícito**. El drawdown aquí es mensual y puede subestimar pérdidas intramensuales. No es una prueba de Sharpe con tipos históricos.

Si falta precio de ejecución/salida de un activo seleccionado, la estrategia queda sin métricas agregadas fiables: no se elimina a posteriori ese activo. Si falta un rebalanceo entero, las estadísticas de rendimiento agregado se dejan vacías y se informa `PARTIAL`. Las curvas con huecos no se dibujan.

### 4. Filings — `research_04_filings_*`

Diccionario visible `CONCEPTS` en `research.py`: revenue, net income, operating income, CFO, capex y EPS. Admite los nombres alternativos de ingresos del ejemplo. Conserva concepto fuente, unidad, fechas y accession.

Usa 10-K/10-K/A, duración de 300–400 días, USD o USD/shares según concepto, y publicaciones/cargas disponibles al corte. Selecciona versiones disponibles más recientes por concepto y una prioridad explícita entre alias. Calcula crecimiento entre ejercicios comparables, aceleración de ingresos, margen operativo, conversión en caja, FCF y aviso de beneficio creciente con caja decreciente.

**Alcance anual:** no convierte todavía 10-Q acumulados a trimestres aislados, no calcula deuda de balance y no realiza detección de fraude. Revisar el diccionario: etiquetas parecidas no garantizan equivalencia semántica universal. Un comparativo reformulado disponible al corte puede diferir del dato publicado originalmente; no se usa esta tabla para un backtest histórico de fundamentales.

### 5. Señales — `research_05_signals_*`

Evalúa scores existentes a 21, 63 y 126 sesiones. Disponibilidad efectiva = máximo entre `as_of_date` y día de `computed_at`; entra al cierre de la sesión siguiente. No prueba una señal retrospectiva como si hubiese sido calculada antes.

IC de rangos, rentabilidad por quintiles, diferencial superior−inferior, proporción de IC positivo y número de fechas. Aporte incremental exploratorio: correlación parcial de rangos controlando momentum cuando exista. No es una validación causal ni una regresión predictiva fuera de muestra.

Mínimo de empresas por corte configurable. Menos de 24 fechas se etiqueta como evidencia insuficiente. Incluso con más fechas, horizontes solapados y selección de múltiples señales impiden tratarlas como observaciones independientes. No se publican p-values engañosos ni se optimizan pesos con estos resultados.

### 6. Carteras — `research_06_portfolios_*`

Dos salidas distintas:

- **Objetivos actuales:** ranking multifactor del punto 2 (si existe), universo con momentum/precio/liquidez disponibles, hasta `portfolio_size` empresas. Si el ranking existe pero no tiene suficientes candidatos, no se rellena silenciosamente con otra selección. Si la etapa de ranking no pudo producir tabla, se usa selección momentum explícitamente identificada.
- **Walk-forward histórico:** selecciona por momentum pasado y entrena con hasta 252 sesiones anteriores a cada formación. **No es un backtest del ranking fundamental actual.** Haría falta reconstruir fundamentales point-in-time durante todo el histórico para eso.

Compara equiponderación e inversa de varianza proyectadas a límites, mínima varianza y máximo ratio Sharpe con rf=0. Covarianza: 80% muestra + 20% diagonal. Medias: 25% muestra + 75% media transversal. Son reglas fijas iniciales, no parámetros validados como óptimos.

Pesos long-only, suma 1, límite individual y sectorial. Si los límites hacen el problema imposible o el optimizador no converge, se informa el fallo; no se devuelve una cartera equiponderada disfrazada de máximo Sharpe. Equiponderación/inversa con restricciones pueden diferir de sus fórmulas puras.

No hay restricciones de turnover máximo, impacto de mercado o participación de una cuenta concreta en volumen: el filtro de liquidez y los costes proporcionales son una primera aproximación. `current_targets` son objetivos teóricos, no órdenes.

### 7. PCA — `research_07_pca_*`

Se recalcula sobre retornos ajustados diarios estandarizados, solo hasta el corte. SVD con convención de signo estable, componentes, varianza explicada, scores, medias/escalas, volatilidad residual y fechas de entrenamiento. Excluye activos con huecos en la ventana o varianza nula; requiere al menos 60 sesiones y tres activos.

Exposiciones de **objetivos actuales del punto 6**, ajustando las cargas por la escala de retornos. Si falta un activo de un objetivo en PCA, no se presenta una exposición parcial como completa. No se etiquetan componentes automáticamente como «tecnología» o «mercado», ni se confunden cargas estandarizadas con betas.

Este PCA es descriptivo al corte: no se introduce retrospectivamente en el backtest. La cartera real del ledger mantiene por separado sus métricas en el monitor; estas exposiciones no son sus exposiciones salvo que coincida con los objetivos.

### 8. Noticias — `research_08_news_*`

Deduplicación por símbolo/URL y titular normalizado/día, clasificación por reglas transparentes de palabras inglesas (earnings, merger, legal, product, analyst, other). No llama a un LLM ni fabrica sentimiento: usa el campo existente.

Disponibilidad conservadora según publicación/carga; estudia retorno desde el cierre siguiente, a 1/5/20 sesiones, frente al resto del universo equiponderado con datos. Tabla de muestras, medias y medianas, más atención de últimos siete días frente al promedio semanal de los 28 anteriores.

Es **retorno posterior al evento**, no captura la reacción inmediata previa a esa entrada. No prueba causalidad, la clasificación es aproximada, las noticias correlacionadas siguen siendo dependientes y el benchmark disponible puede tener sesgo de supervivencia. No existe un índice de mercado externo incluido.

### 9. Dividendos — `research_09_dividends_result`

Dividendos por acción de últimos 365 días, periodo anterior, crecimiento, CAGR 3/5 años cuando hay base suficiente, número de pagos, posible interrupción por retraso respecto a cadencia reciente y posible reducción de pago. Filtra corte temporal y exige confirmación de ajuste por splits.

Cobertura FCF y yield **aproximados** a partir de acciones actuales × dividendos TTM, si el snapshot no está obsoleto. No sustituye pagos de dividendos reales de cash-flow statement; no demuestra sostenibilidad futura. Un pago inferior puede ser split, extraordinario, moneda o frecuencia: necesita revisión. No se reconstruyen splits retroactivamente sin saber cómo ajusta el proveedor.

### 10. Dashboard e informe

Conserva los cinco paneles iniciales y añade **«Proceso completo 1–9»**. Permite ejecutar, consultar estado por etapa, descargar resultados y ver curvas de backtests válidos. Leer `README.md` para las fórmulas de NAV/TWR/atribución real.

Si falla el ledger, el pipeline conserva la investigación e informa el error en etapa 10. La interfaz permite ejecutar investigación aunque la valoración real esté bloqueada. Las noticias y fuentes se muestran como datos; no se ejecuta contenido de titulares.

## Resultados y trazabilidad

Cada ejecución crea una carpeta única:

```text
reports/
  latest.json
  runs/<timestamp_uuid>/
    manifest.json
    analytics.duckdb
    AAAA-MM-DD/
      report.html
      metadata.json
      metrics.json
      research_status.csv
      research_*.csv
      ...monitor de cartera...
```

`analytics.duckdb` contiene una tabla por resultado y `run_metadata`. Se escribe en una transacción. `latest.json` solo cambia de forma atómica cuando la exportación termina. Ejecuciones del mismo corte no se sobrescriben; `report.py` antiguo sigue teniendo el comportamiento de sobrescribir por fecha documentado en README.

Metadatos: configuración, fecha de corte, hora UTC, hash del código, tamaño/mtime de fuente y hash de ledger cuando pudo analizarse. **No equivalen a versionar los datos.** Conservar copia inmutable de la DuckDB fuente, ledger y código para reproducibilidad estricta. No ejecutar mientras el actualizador mantenga bloqueo de escritura; usar una copia consistente o planificar después de la actualización.

El dashboard solo carga el último archivo si coincide la ruta de base y el corte. Si cambias la fuente o parámetros, debes ejecutar de nuevo: no interpreta un archivo anterior como cálculo recién actualizado. Para otras ejecuciones, abrir su HTML o DuckDB archivado directamente.

## Automatización

```bash
./run_pipeline.sh /ruta/absoluta/config.json 2026-09-30
# Sin fecha: usa fecha local de la máquina
./run_pipeline.sh /ruta/absoluta/config.json
```

Cron, viernes 23:00 de la máquina (ajustar zona y ruta):

```cron
0 23 * * 5 /ruta/Data-Analysis/portfolio_monitor/run_pipeline.sh /ruta/config.json >> /ruta/pipeline.log 2>&1
```

Windows Programador de tareas: `.venv\Scripts\python.exe`, argumentos `pipeline.py --config C:\ruta\config.json --strict`, directorio de trabajo `portfolio_monitor`.

Para una primera base de unas 500 empresas puede tardar minutos y usar memoria significativa: lee las tablas requeridas a pandas y luego calcula las etapas. No se cargan las vistas derivadas ni las tablas PCA/pesos existentes para no reutilizar modelos sin fecha de entrenamiento. No hay límite de recursos ni proceso distribuido.

## Verificación y límites pendientes

```bash
python -m pytest tests -q
```

Pruebas de contabilidad, pipeline completo, fuente intacta, archivos, cortes de disponibilidad, conceptos anuales, restricciones y fallos del optimizador, pesos sin acceso al futuro, costes, precios ausentes, PCA y confirmación de ajustes.

**Antes de usar resultados para decidir inversiones:**

1. Validar las convenciones de precios/dividendos con tu proveedor.
2. Revisar `research_status`, auditoría, cobertura y huecos.
3. Reconciliar el ledger y NAV con el bróker.
4. Incorporar empresas desaparecidas y composición histórica si quieres backtests invertibles.
5. Versionar fuentes y normalizar zonas horarias para point-in-time estricto.
6. Ampliar modelo contable trimestral y sectorial según tu universo.
7. Validar reglas congeladas en un periodo futuro/paper trading; la demo solo prueba software, no alpha.

No incluye ingesta desde APIs, fiscalidad española, conversión USD/EUR, ejecución bursátil, validación causal de noticias, modelo predictivo entrenado, email o autenticación web. La versión cubre el recorrido analítico de los diez puntos con este alcance explícito; no afirma resolver todos los posibles análisis de cada área.
