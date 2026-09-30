# OpenBerg launcher (Windows) — doble clic en run.bat
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $MyInvocation.MyCommand.Path)
if (Test-Path .\.venv\Scripts\Activate.ps1) {
  & .\.venv\Scripts\Activate.ps1
}
if (-not (Test-Path .env)) {
  Copy-Item .env.example .env
}
& python -c "import fastapi" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Instalando dependencias..."
  & python -m pip install -r requirements.txt
}
$port = if ($env:PORT) { $env:PORT } else { "8000" }
Write-Host "OpenBerg en http://localhost:$port  (Ctrl+C para parar)" -ForegroundColor Green
& python -m uvicorn backend.main:app --host 127.0.0.1 --port $port
