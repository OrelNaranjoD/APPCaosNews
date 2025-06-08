# Script para ejecutar el servidor en modo NORMAL/DESARROLLO
# PowerShell version

Write-Host "============================================" -ForegroundColor Green
Write-Host " CaosNews - Servidor de Desarrollo" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

# Cambiar al directorio del proyecto
$projectPath = Split-Path -Parent $PSScriptRoot
Set-Location $projectPath

Write-Host "Configurando entorno de desarrollo..." -ForegroundColor Yellow
$env:DJANGO_SETTINGS_MODULE = "CaosNews.settings.settings_dev"
python manage.py setup_dev

Write-Host ""
Write-Host "Iniciando servidor de desarrollo..." -ForegroundColor Green
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Red
Write-Host "Abrir en navegador: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""

python manage.py runserver 127.0.0.1:8000
