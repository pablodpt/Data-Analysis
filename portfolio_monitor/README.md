# Monitor de mercado y cartera con DuckDB

> **Versión 2: proceso completo disponible.** Para ejecutar los diez puntos de principio a fin, empieza por [PROCESS.md](PROCESS.md): `python pipeline.py --config config.json --as-of 2026-09-30`. Este README documenta especialmente el monitor de cartera y su ledger. Los límites de la primera interfaz se amplían mediante `research.py` y `pipeline.py`.

Paquete independiente del resto del repositorio. Python 3.10+. Interfaz e informes en español. **No necesita claves API ni modifica la base de mercado.** Usa el esquema descrito por el usuario; probado con datos sintéticos, no con su archivo real.

## 1. Instalar

Desde la raíz del repositorio:

```bash
cd portfolio_monitor
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell: `py -m venv .venv`, luego `.venv\Scripts\Activate.ps1` (o ejecutar directamente `.venv\Scripts\python.exe`).

## 2. Probar SIN datos reales

```bash
python demo.py
python report.py --config demo_data/config.json --as-of 2026-09-30
```

Abrir `demo_data/reports/2026-09-30/report.html` en el navegador. Son tres empresas **ficticias**. `demo.py` se niega a sobrescribir una base existente.

Dashboard de demostración (Linux/macOS):

```bash
MONITOR_CONFIG=demo_data/config.json python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

En Windows o cualquier sistema también puede arrancar `python -m streamlit run app.py` y escribir `demo_data/config.json` en la barra lateral. Elegir **2026-09-30** como fecha de corte de la demostración.

## 3. Conectar tu DuckDB

```bash
cp config.example.json config.json
cp examples/ledger.csv ledger.csv
```

Editar `config.json`: `database` debe apuntar al archivo DuckDB existente. Todas las rutas son relativas al JSON (también se aceptan rutas absolutas). **Sustituir completamente las filas de ejemplo de ledger.csv por las operaciones reales.** Si solo se desea investigación sin cartera, dejar únicamente la cabecera.

```json
{
  "database": "/ruta/a/tu/base.duckdb",
  "ledger": "ledger.csv",
  "report_dir": "reports",
  "base_currency": "USD",
  "lookback_days": 365,
  "event_days": 7,
  "stale_days": 7,
  "max_position_weight": 0.15,
  "max_sector_weight": 0.35,
  "drawdown_warning": -0.15
}
```

```bash
python report.py --config config.json --as-of 2026-09-30
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

No hay subida de datos a un servicio remoto. Streamlit no incluye autenticación en este paquete: no publicar una cartera privada en una URL accesible sin control de acceso. No se desactivan las protecciones CORS/XSRF de Streamlit.

## 4. Libro de cartera: reglas imprescindibles

CSV con cabecera:

```csv
date,type,symbol,quantity,price,amount,fee,currency,note
2026-09-01,DEPOSIT,,0,0,10000,0,USD,Aportacion
2026-09-01,BUY,AAPL,10,230,0,1,USD,Compra
2026-09-10,SELL,AAPL,2,240,0,1,USD,Venta parcial
2026-09-15,DIVIDEND,AAPL,0,0,2,0,USD,Cobro neto
2026-09-16,FEE,,0,0,3,0,USD,Custodia
2026-09-20,WITHDRAWAL,,0,0,100,0,USD,Retirada
```

| type | quantity | price | amount | fee |
|---|---|---|---|---|
| DEPOSIT / WITHDRAWAL | 0 | 0 | importe positivo | 0 |
| BUY / SELL | acciones positivas | precio ejecutado | 0 | comisión positiva o 0 |
| DIVIDEND | 0 | 0 | cobro **neto** positivo | 0 |
| FEE | 0 | 0 | gasto positivo | 0 |
| SPLIT | multiplicador, p.ej. 4 o 0.1 | 0 | 0 | 0 |

- Moneda admitida: USD en operaciones y tickers. **No hay conversión a EUR.**
- BUY, SELL, DIVIDEND y SPLIT requieren symbol exacto; no se normalizan sufijos del proveedor.
- Las filas del mismo día se procesan en su orden original: aporte antes de compra, split antes de operaciones sobre las nuevas acciones.
- No se permiten posiciones cortas ni saldo de efectivo negativo. Ventas sin tenencias fallan explícitamente.
- Registrar splits manualmente en la fecha efectiva, incluidos reverse splits. Los eventos de la base generan avisos, no operaciones automáticas.
- Dividendos: registrar en la fecha de cobro. El CSV usa caja, no devengo de dividendos pendientes. No se suma `dividends` a `adj_close`.
- Evitar duplicados: cada fila se contabiliza una vez por ejecución; duplicar una fila duplica la operación. Reejecutar el informe no inserta operaciones en ninguna base.
- Introducir toda la historia desde saldo cero. Para arrancar con cartera existente, usar una aportación igual al patrimonio inicial y compras al precio de valoración inicial, comisión cero: el rendimiento medido comienza ahí, no en las compras originales.
- No se calculan plusvalías fiscales, lotes FIFO, intereses, fusiones ni spin-offs automáticamente. Requieren reconciliación y eventualmente ampliar el modelo.

### Importante: significado de `close`

La valoración usa **close histórico no ajustado**, acciones realmente poseídas, dividendos netos y splits explícitos del ledger. Algunos proveedores entregan `close` ya ajustado por splits: en ese caso debe prepararse una serie no ajustada antes de usar el módulo. No deducir el tipo de ajuste por el nombre de la columna. Con `close` ajustado y splits en el ledger se duplicaría el ajuste. El módulo no puede detectar universalmente esta semántica.

## 5. Qué incluye el dashboard

1. **Oportunidades:** último `signals` disponible por empresa, ranking por composite_score, variación de score y posición respecto al snapshot anterior a la ventana. Fundamentales recientes. Los nulos quedan al final. Esta pestaña no recalcula el score. La pestaña del pipeline añade ranking propio y evaluación histórica exploratoria.
2. **Riesgo:** posición y sector como porcentaje del NAV (incluido efectivo), alertas de concentración, curva de drawdown y volatilidad realizada.
3. **Cambios:** noticias deduplicadas por symbol/URL, filings publicados, cambios absolutos entre snapshots fundamentales, dividendos y splits. Posibles recortes comparan pagos consecutivos: **no son recortes confirmados**, pueden ser extraordinarios, splits o distinta frecuencia.
4. **Resultados:** patrimonio, índice TWR, P&L acumulado y de la ventana, atribución por acción/sector, efectivo y serie diaria exportable.
5. **Calidad:** antigüedad de precios, señales y fundamentales; estado del actualizador; metadatos y exportación.

`event_days` son días naturales inclusivos. `lookback_days` controla lectura mínima para investigación, pero para valorar la cartera se carga desde el primer movimiento (más 30 días de margen para un precio previo). Las métricas de cartera cubren **toda la historia del ledger hasta el corte**, no solo la ventana de eventos.

## 6. Cálculos y supuestos

- NAV = efectivo + suma(acciones × close). Se arrastra el último precio conocido, sin traer precios futuros; si no existe precio previo válido para una posición abierta, el informe falla. Precios antiguos generan avisos, pero no bloquean NAV: revisar esos avisos antes de confiar en el resultado.
- P&L diario = NAV actual − NAV anterior − aportaciones netas.
- Retorno diario = P&L / (NAV anterior + aportaciones netas del día). Supone aportaciones/retiros **al inicio del día**. No es TWR intradía exacto si los flujos ocurren a otras horas. Si no existe capital positivo para un P&L no nulo, se aborta.
- TWR = producto(1 + retorno diario) − 1. Incluye costes registrados.
- Drawdown sobre índice TWR, con valor inicial 1, para no confundir retiradas de capital con pérdidas.
- Volatilidad: desviación típica muestral de retornos diarios **naturales**, anualizada por √365 (incluye fines de semana y sus movimientos de caja). Historial corto = estimación poco fiable. No se publica Sharpe sin una tasa libre de riesgo.
- Atribución USD por acción = variación de su valor + cobros de ventas/dividendos − pagos de compras − comisiones. Los gastos generales van a `CASH_COSTS`. Suma exactamente el P&L de cartera, incluyendo posiciones ya cerradas. No separa plusvalía realizada/no realizada ni hace atribución Brinson o de selección frente a benchmark.
- Sectores de `tickers` son actuales; pueden no coincidir con los históricos. El P&L no depende de que haya sector.

## 7. Disponibilidad histórica y calidad

- `signals`: exige `as_of_date <= corte` y `computed_at < día siguiente`. Por seguridad, una señal recalculada después no se considera disponible en un informe anterior.
- Noticias y filings: fecha de publicación y `loaded_at` deben estar dentro del corte. Es una política conservadora de **disponibilidad en este sistema**, no solo en el mercado; una carga retrospectiva quedará excluida de fechas anteriores.
- Timestamps se comparan tal como están almacenados. Normalizar previamente publicación/carga a una zona coherente; no se inventa una zona horaria para timestamps sin zona.
- `fundamentals`: solo `snapshot_date`; precios, dividendos y splits no tienen versiones de carga en el esquema. **No se garantiza reconstrucción point-in-time estricta** si se revisan o sobrescriben datos.
- Para reproducibilidad estricta, conservar copia inmutable/versionada de DuckDB y del ledger usado. `metadata.json` registra configuración, corte, generación, ruta y SHA256 del ledger; no copia ni hashea la base completa.
- Tablas opcionales ausentes generan avisos y paneles vacíos. Columnas requeridas ausentes producen error explícito de DuckDB: no se inventan valores. Precios duplicados y tickers duplicados detienen el cálculo. `prices` es obligatoria; con operaciones por símbolo también se exige `tickers` para validar moneda.
- No depende de `pca_*`, `weights_*`, vistas de momentum ni `selected_15_tickers`: son modelos de investigación, no posiciones reales. El pipeline de investigación recalcula PCA y carteras con metadatos de entrenamiento, sin reutilizar esas tablas no versionadas.
- Sin benchmark no hay afirmación de alpha. Sin histórico de universo no hay backtest libre de sesgo de supervivencia.

## 8. Informe automatizado

```bash
./run_weekly.sh /ruta/absoluta/config.json
# O fijar una fecha:
./run_weekly.sh config.json 2026-09-30
```

Ejemplo cron, viernes a las 23:00 **en la zona horaria de la máquina** (ajustar rutas):

```cron
0 23 * * 5 /ruta/Data-Analysis/portfolio_monitor/run_weekly.sh /ruta/Data-Analysis/portfolio_monitor/config.json >> /ruta/monitor.log 2>&1
```

En Windows Programador de tareas: programa `.venv\Scripts\python.exe`, argumentos `report.py --config config.json`, directorio de trabajo `portfolio_monitor`. Planificar después de terminar el actualizador de datos. Este paquete **no descarga cotizaciones ni noticias**: lee la base que ya alimenta tu proceso. Si otro proceso mantiene un bloqueo de escritura DuckDB, terminarlo o analizar una copia consistente.

Salida `reports/AAAA-MM-DD/`: HTML independiente, métricas JSON, metadatos JSON y CSV completos por panel. El HTML limita a 100 filas por tabla y escapa contenido externo. Mismo corte sobrescribe sus archivos; archivar la carpeta si se quieren conservar revisiones. No requiere servidor para leerlo. No se envían emails ni se ejecutan órdenes bursátiles.

## 9. Pruebas

```bash
python -m pytest tests -q
```

Cobertura funcional: NAV, comisiones, dividendos, splits, atribución reconciliada, aportaciones, corte histórico, precios duplicados/ausentes, venta sin posición, CSV inválido y exportación integral con DuckDB sintético.

## Archivos

- `core.py`: lectura, validaciones, cartera, alertas y análisis.
- `app.py`: dashboard Streamlit.
- `report.py`: CLI e informe HTML/CSV/JSON.
- `demo.py`: base y libro sintéticos reproducibles.
- `run_weekly.sh`: ejecución por calendario.
- `config.example.json`, `examples/ledger.csv`: plantillas.
- `tests/test_monitor.py`: pruebas automáticas.

Antes de uso real, reconciliar NAV, efectivo y cantidades con tu bróker para varias fechas, incluidos días de dividendos y splits. Ninguna alerta sustituye esa comprobación.
