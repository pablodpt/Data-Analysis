@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title sp500_quant - Instalacion

echo.
echo ============================================================
echo    sp500_quant - Instalacion en Windows
echo ============================================================
echo.

rem --- 1) Buscar Python ---------------------------------------------------
set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY (
    python --version >nul 2>&1 && set "PY=python"
)
if not defined PY (
    echo [!] No se ha encontrado Python en este equipo.
    echo.
    echo     Abre PowerShell y ejecuta este comando:
    echo.
    echo         winget install -e --id Python.Python.3.12
    echo.
    echo     Cuando termine, cierra esa ventana y vuelve a hacer
    echo     doble clic aqui.
    echo.
    pause
    exit /b 1
)
for /f "delims=" %%v in ('%PY% --version 2^>^&1') do echo [ok] %%v encontrado.

rem --- 2) Entorno virtual -------------------------------------------------
if exist ".venv\Scripts\python.exe" (
    echo [ok] El entorno .venv ya existe, no se recrea.
) else (
    echo [..] Creando entorno virtual .venv ...
    %PY% -m venv .venv
    if errorlevel 1 (
        echo [!] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo [ok] Entorno creado.
)

rem --- 3) Dependencias ----------------------------------------------------
echo.
echo [..] Instalando duckdb, pandas, numpy, scipy y matplotlib ...
echo      Puede tardar entre 1 y 3 minutos.
echo.
".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
".venv\Scripts\python.exe" -m pip install --quiet duckdb pandas numpy scipy matplotlib
if errorlevel 1 (
    echo.
    echo [!] Fallo la instalacion de dependencias.
    echo     Comprueba tu conexion a internet e intentalo de nuevo.
    pause
    exit /b 1
)

rem --- 4) Comprobacion ----------------------------------------------------
".venv\Scripts\python.exe" -c "import duckdb, pandas, numpy, scipy, matplotlib; print('[ok] Comprobado: duckdb ' + duckdb.__version__)"
if errorlevel 1 (
    echo [!] La comprobacion fallo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo    INSTALACION COMPLETADA
echo.
echo    Siguiente paso: doble clic en  ANALIZAR.bat
echo ============================================================
echo.
pause
