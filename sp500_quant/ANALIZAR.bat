@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"
title sp500_quant - Analisis

if not exist ".venv\Scripts\python.exe" (
    echo [!] Primero tienes que ejecutar INSTALAR.bat una vez.
    pause
    exit /b 1
)

rem --- Ruta de la base: argumento, archivo guardado o valor por defecto ----
set "DB=%~1"
if not defined DB (
    if exist "db_path.txt" set /p DB=<"db_path.txt"
)
if not defined DB set "DB=C:\Users\pablo\Documents\sp500_db\db\sp500.duckdb"

if not exist "!DB!" (
    echo.
    echo [!] No encuentro la base de datos en:
    echo     !DB!
    echo.
    echo     Opciones:
    echo       1^) Arrastra tu archivo .duckdb sobre este ANALIZAR.bat
    echo       2^) Escribe la ruta completa aqui abajo
    echo       3^) Escribe  demo  para descargar una base de ejemplo
    echo.
    set /p DB="Ruta del .duckdb ^(o demo^): "
)

if /i "!DB!"=="demo" (
    echo.
    echo [..] Descargando datos publicos y construyendo base de ejemplo ...
    ".venv\Scripts\python.exe" build_replica.py
    if errorlevel 1 (
        echo [!] Fallo la descarga. Comprueba tu conexion a internet.
        pause
        exit /b 1
    )
    set "DB=!CD!\data\sp500_replica.duckdb"
)

if not exist "!DB!" (
    echo [!] Esa ruta no existe. Saliendo.
    pause
    exit /b 1
)

(echo !DB!)>"db_path.txt"

echo.
echo ============================================================
echo    Base de datos: !DB!
echo ============================================================
echo.
echo    NOTA: si tienes la base abierta en otro programa
echo          ^(DBeaver, DuckDB CLI...^), cierrala antes.
echo.
echo [1/4] Calculando patrones ...
".venv\Scripts\python.exe" run_analysis.py --db "!DB!"
if errorlevel 1 goto :error

echo.
echo [2/4] Contrastando contra la tasa base ...
".venv\Scripts\python.exe" significancia.py
if errorlevel 1 goto :error

echo.
echo [3/4] Generando figuras ...
".venv\Scripts\python.exe" make_figures.py
if errorlevel 1 goto :error

echo.
echo [4/4] Generando el dashboard HTML ...
".venv\Scripts\python.exe" make_dashboard.py --db "!DB!"
if errorlevel 1 goto :error

echo.
echo ============================================================
echo    LISTO.
echo.
echo    Se abre el DASHBOARD en tu navegador.
echo    Tambien tienes, en la carpeta "resultados":
echo      - dashboard.html              ^(dashboard interactivo^)
echo      - significancia_vs_base.csv   ^(probabilidades vs tasa base^)
echo      - un CSV por patron
echo      - figuras\patrones_sp500.png
echo.
echo    Abre RESULTADOS.md para la interpretacion del metodo.
echo ============================================================
echo.
start "" "resultados\dashboard.html"
pause
exit /b 0

:error
echo.
echo [!] Hubo un error durante el analisis.
echo     Copia el mensaje de arriba si necesitas ayuda.
echo.
pause
exit /b 1
