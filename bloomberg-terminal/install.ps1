# OpenBerg installer (Windows) — doble clic en install.bat
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $MyInvocation.MyCommand.Path)
Write-Host "== OpenBerg installer =="
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
  Write-Host "ERROR: instala Python 3.11+ gratis desde https://www.python.org/downloads/ (marca 'Add python.exe to PATH')" -ForegroundColor Red
  Read-Host "Pulsa Enter para salir"
  exit 1
}
& python --version
if (-not (Test-Path .venv)) {
  Write-Host "Creando entorno virtual..."
  & python -m venv .venv
}
& .\.venv\Scripts\Activate.ps1
Write-Host "Instalando dependencias (la primera vez tarda unos minutos)..."
& python -m pip install -q -r requirements.txt
if (-not (Test-Path .env)) {
  Copy-Item .env.example .env
  Write-Host "Creado .env (sin claves: funciona igual con datos gratuitos)."
}
Write-Host ""
Write-Host "OK Instalado. Para arrancar: doble clic en run.bat  (luego abre http://localhost:8000)" -ForegroundColor Green
Read-Host "Pulsa Enter para salir"
