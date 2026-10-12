@echo off
chcp 65001 >nul
echo ============================================================
echo   ANALISIS CON DATOS REALES - descarga de Yahoo Finance
echo ============================================================
echo.
if not exist .venv (
    echo [AVISO] Primero ejecuta INSTALAR_WINDOWS.bat
    echo.
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
cd /d "%~dp0"

echo Puedes cambiar los ETFs y ventanas editando este archivo ^(linea set TICKERS^).
echo.
set TICKERS=
set WINDOWS=max,ytd,3m,1m

if "%TICKERS%"=="" (
    python -m etf_agent analyze --windows %WINDOWS%
) else (
    python -m etf_agent analyze --tickers %TICKERS% --windows %WINDOWS%
)

echo.
echo Informe generado en la carpeta: reports\
echo Abre el archivo report.html con tu navegador.
echo.
pause
