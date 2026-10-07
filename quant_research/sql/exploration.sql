-- Plantillas SQL DuckDB. Sustituir "schema"."table_name" y los nombres
-- de columnas por los identificados mediante el catálogo de la base.

-- 1) Relaciones persistentes y vistas visibles para la sesión:
SELECT table_schema, table_name, table_type
FROM information_schema.tables
WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
ORDER BY table_schema, table_name;

-- 2) Esquema de la relación seleccionada:
DESCRIBE SELECT * FROM "schema"."table_name";

-- 3) Extracción sin modificar la base:
SELECT * FROM "schema"."table_name" ORDER BY "Date";

-- 4) Perfil básico (ajustar los nombres de columna según DESCRIBE):
SELECT
    COUNT(*) AS rows,
    COUNT(*) FILTER (WHERE "Date" IS NULL) AS missing_date,
    COUNT(*) FILTER (WHERE "Close" IS NULL) AS missing_close,
    COUNT(*) FILTER (WHERE "Open" IS NULL) AS missing_open,
    COUNT(*) FILTER (WHERE "High" IS NULL) AS missing_high,
    COUNT(*) FILTER (WHERE "Low" IS NULL) AS missing_low,
    COUNT(*) FILTER (WHERE "Volume" IS NULL) AS missing_volume,
    MIN("Date") AS first_date,
    MAX("Date") AS last_date,
    MIN("Close") AS min_close,
    MAX("Close") AS max_close,
    AVG("Close") AS mean_close,
    STDDEV_SAMP("Close") AS sd_close
FROM "schema"."table_name";

-- 5) Duplicados por fecha:
SELECT "Date", COUNT(*) AS rows_per_date
FROM "schema"."table_name"
GROUP BY "Date"
HAVING COUNT(*) > 1
ORDER BY "Date";

-- 6) Filas a revisar; el motor calcula métricas de retornos/features en Python
--    para mantener idénticas las reglas de indicadores entre CSV y DuckDB.
SELECT * FROM "schema"."table_name"
WHERE "Date" IS NULL OR "Close" IS NULL OR "Close" <= 0
ORDER BY "Date";
