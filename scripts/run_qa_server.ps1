# Script para ejecutar servidor en modo QA con datos clonados de producción
# PowerShell version
#
# Uso:
#   .\run_qa_server.ps1           - Ejecuta con configuración completa de datos
#   .\run_qa_server.ps1 -SkipData - Ejecuta sin configurar datos (usa BD existente)

param(
    [switch]$SkipData
)

if ($SkipData) {
    Write-Host "============================================" -ForegroundColor Magenta
    Write-Host " CaosNews - Servidor de QA" -ForegroundColor Magenta
    Write-Host " (Usando base de datos existente)" -ForegroundColor Yellow
    Write-Host "============================================" -ForegroundColor Magenta
} else {
    Write-Host "============================================" -ForegroundColor Magenta
    Write-Host " CaosNews - Servidor de QA" -ForegroundColor Magenta
    Write-Host " (Base de datos clonada de producción)" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Magenta
}

# Cambiar al directorio del proyecto
$projectPath = Split-Path -Parent $PSScriptRoot
Set-Location $projectPath

# Activar entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
    Write-Host "[OK] Entorno virtual activado" -ForegroundColor Green
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
    Write-Host "[OK] Entorno virtual activado" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Entorno virtual no encontrado. Continuando..." -ForegroundColor Yellow
    Write-Host "   Asegurese de tener las dependencias instaladas" -ForegroundColor Yellow
}

Write-Host "Configurando entorno de QA..." -ForegroundColor Yellow
$env:DJANGO_SETTINGS_MODULE = "CaosNews.settings.settings_qa"

if (-not $SkipData) {
    Write-Host "Clonando base de datos de produccion y configurando usuarios de prueba..." -ForegroundColor Yellow
    python manage.py setup_qa
} else {
    Write-Host "Clonando base de datos de produccion y copiando archivos media (sin usuarios de prueba)..." -ForegroundColor Yellow
    python manage.py setup_qa --skip-data
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error configurando el entorno QA" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host " ENTORNO QA CONFIGURADO CORRECTAMENTE" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

if (-not $SkipData) {
    Write-Host "Datos disponibles:" -ForegroundColor Cyan
    Write-Host "  - Base de datos clonada de produccion" -ForegroundColor White
    Write-Host "  - Usuarios de prueba agregados" -ForegroundColor White
    Write-Host "  - Archivos media copiados" -ForegroundColor White
} else {
    Write-Host "Datos disponibles:" -ForegroundColor Cyan
    Write-Host "  - Base de datos clonada de produccion" -ForegroundColor White
    Write-Host "  - Archivos media copiados" -ForegroundColor White
    Write-Host "  - Usuarios de prueba omitidos (usar usuarios existentes)" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Para ejecutar pruebas (comando separado):" -ForegroundColor Yellow
Write-Host "  python manage.py run_qa_tests" -ForegroundColor White
Write-Host "  python manage.py run_qa_tests --verbose --coverage" -ForegroundColor White
Write-Host ""
Write-Host "Iniciando servidor de QA..." -ForegroundColor Magenta
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Red
Write-Host "Abrir en navegador: http://127.0.0.1:8001" -ForegroundColor Cyan
Write-Host "Admin: http://127.0.0.1:8001/adminDJango/" -ForegroundColor Cyan
Write-Host ""

python manage.py runserver 127.0.0.1:8001
