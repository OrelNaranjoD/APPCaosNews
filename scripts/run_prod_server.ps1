# Script para ejecutar el servidor en modo PRODUCCIÓN
# PowerShell version

Write-Host "============================================" -ForegroundColor Red
Write-Host " CaosNews - Servidor de Producción" -ForegroundColor Red
Write-Host "============================================" -ForegroundColor Red

# Cambiar al directorio del proyecto
$projectPath = Split-Path -Parent $PSScriptRoot
Set-Location $projectPath

# Activar entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
    Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
    Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
} else {
    Write-Host "⚠️  Entorno virtual no encontrado. Continuando..." -ForegroundColor Yellow
    Write-Host "   Asegúrese de tener las dependencias instaladas" -ForegroundColor Yellow
}

Write-Host "Configurando entorno de producción..." -ForegroundColor Yellow
$env:DJANGO_SETTINGS_MODULE = "CaosNews.settings.settings_prod"

Write-Host "Recolectando archivos estáticos..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

Write-Host "Aplicando migraciones..." -ForegroundColor Yellow
python manage.py migrate

Write-Host ""
Write-Host "Iniciando servidor de producción..." -ForegroundColor Red
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host "NOTA: En producción real usar Gunicorn + Nginx" -ForegroundColor Yellow
Write-Host ""

python manage.py runserver 0.0.0.0:8000
