# Instalar OpenBerg en tu laptop (gratis, ~10 minutos)

No pagas nada, no copias archivos a mano y no necesitas cuenta en ningún sitio.
Solo hacen falta **Python** (gratis) y descargar el proyecto.

## Paso 0 — Instala Python 3.11+ (gratis, una sola vez)

- **Windows**: entra en <https://www.python.org/downloads/>, instala, y marca la casilla
  **"Add python.exe to PATH"** durante la instalación.
- **Mac**: entra en <https://www.python.org/downloads/> e instala el paquete de macOS.
- **Linux**: suele venir instalado. Si no: `sudo apt install python3 python3-venv`.

Compruébalo: abre PowerShell (Windows) o Terminal (Mac/Linux) y escribe:

```bash
python --version    # Windows
python3 --version   # Mac / Linux
```

Si muestra `Python 3.11` o superior, listo.

## Paso 1 — Descarga el proyecto (gratis, sin cuenta)

👉 **[Descargar OpenBerg (.zip)](https://github.com/pablodpt/Data-Analysis/archive/refs/heads/arena/01a0ee37-data-analysis.zip)**

> El ZIP trae todo el repositorio (~290 MB, una sola vez). Si prefieres, con `git`:
> `git clone --branch arena/01a0ee37-data-analysis --depth 1 https://github.com/pablodpt/Data-Analysis.git`

## Paso 2 — Descomprime y entra en `bloomberg-terminal`

Descomprime el ZIP donde quieras (por ejemplo, tu carpeta de usuario).
Dentro encontrarás una carpeta `Data-Analysis-...`; entra en **`bloomberg-terminal`**.
Solo necesitas esa carpeta — el resto lo puedes borrar si quieres.

## Paso 3 — Instala y arranca

**Windows** (con doble clic, sin escribir comandos):

1. Doble clic en **`install.bat`** — solo la primera vez, tarda unos minutos.
2. Doble clic en **`run.bat`**.
3. Abre <http://localhost:8000> en tu navegador. 🎉

**Mac / Linux** (en la Terminal, dentro de la carpeta `bloomberg-terminal`):

```bash
bash install.sh   # solo la primera vez (unos minutos)
bash run.sh       # para arrancar; luego abre http://localhost:8000
```

### Todo en un solo comando (opcional, avanzado)

<details>
<summary>Windows (PowerShell)</summary>

```powershell
$u="https://github.com/pablodpt/Data-Analysis/archive/refs/heads/arena/01a0ee37-data-analysis.zip"; $z="$env:TEMP\openberg.zip"; Invoke-WebRequest -Uri $u -OutFile $z; $d="$env:USERPROFILE\openberg"; if (Test-Path $d){Remove-Item -Recurse -Force $d}; Expand-Archive -Path $z -DestinationPath $d -Force; Start-Process ((Get-ChildItem $d -Directory | Select-Object -First 1).FullName + "\bloomberg-terminal\install.bat")
```

Después, doble clic en `run.bat` dentro de `~\openberg\...\bloomberg-terminal`.
</details>

<details>
<summary>Mac / Linux (Terminal)</summary>

```bash
rm -rf ~/openberg && mkdir -p ~/openberg && curl -sL "https://github.com/pablodpt/Data-Analysis/archive/refs/heads/arena/01a0ee37-data-analysis.zip" -o /tmp/openberg.zip && python3 -c "import zipfile,os; zipfile.ZipFile('/tmp/openberg.zip').extractall(os.path.expanduser('~/openberg'))" && bash ~/openberg/Data-Analysis-arena-01a0ee37-data-analysis/bloomberg-terminal/install.sh && bash ~/openberg/Data-Analysis-arena-01a0ee37-data-analysis/bloomberg-terminal/run.sh
```

Luego abre <http://localhost:8000>.
</details>

## Preguntas frecuentes

- **¿Cuesta algo?** No. Todo es gratis y de código abierto.
- **¿Necesito claves API?** No para empezar. La app funciona con fuentes gratuitas
  sin registro. (Si más adelante quieres, puedes añadir 2 claves gratuitas en el
  archivo `.env` — ver `README.md`.)
- **¿Veré datos reales?** Sí. En tu laptop, con internet, la insignia pasará a
  **LIVE** automáticamente (datos con ~15 min de retraso, gratis).
- **¿Cómo lo paro?** `Ctrl+C` en la ventana negra, o ciérrala.
- **Windows SmartScreen / "editor desconocido"**: es normal (el script es nuestro,
  no está firmado). Pulsa "Más información → Ejecutar de todas formas".
- **¿Cómo actualizo a una versión nueva?** 1) Para el servidor (Ctrl+C en la
  ventana negra y ciérrala). 2) Descarga el ZIP otra vez y sustituye la carpeta
  (o `git pull` si usaste git). 3) Arranca de nuevo. 4) En el navegador pulsa
  **Ctrl+F5** (recarga forzada: sin esto puede seguir usando archivos viejos en
  caché). El pie de la pantalla muestra la versión (v0.2.1, …): si no cambia,
  repite la recarga forzada. Tus listas y alertas se guardan en el navegador,
  no se pierden.
- **¿Ocupa mucho?** El programa en sí ~1 MB + dependencias de Python (~200 MB).
  Puedes borrar todo lo descargado excepto la carpeta `bloomberg-terminal`.
