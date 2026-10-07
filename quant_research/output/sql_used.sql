-- SQL de lectura ejecutado por el motor (DuckDB read-only cuando está disponible).
-- Fuente: /home/user/Data-Analysis/economics/^GSPC.csv
-- Relación seleccionada: ^GSPC.csv

SELECT * FROM read_csv_auto('/home/user/Data-Analysis/economics/^GSPC.csv', header=true, sample_size=-1);

-- Plantilla de perfil para la relación seleccionada (ajustar schema/tabla o ruta):
SELECT
    COUNT(*) AS row_count,
    COUNT(*) FILTER (WHERE "Date" IS NULL) AS missing_date,
    COUNT(*) FILTER (WHERE "Adj Close" IS NULL) AS missing_close,
    MIN("Date") AS first_date, MAX("Date") AS last_date,
    MIN("Adj Close") AS min_close, MAX("Adj Close") AS max_close,
    AVG("Adj Close") AS mean_close, STDDEV_SAMP("Adj Close") AS sd_close
FROM read_csv_auto('/home/user/Data-Analysis/economics/^GSPC.csv', header=true, sample_size=-1);

SELECT "Date", COUNT(*) AS rows_per_date FROM read_csv_auto('/home/user/Data-Analysis/economics/^GSPC.csv', header=true, sample_size=-1)
GROUP BY "Date" HAVING COUNT(*) > 1 ORDER BY "Date";

-- El perfil de faltantes/quantiles y las features se completan en Python;
-- ver quant_research/sql/exploration.sql para plantillas parametrizables.
