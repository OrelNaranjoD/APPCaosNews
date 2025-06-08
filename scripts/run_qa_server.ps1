# Script para ejecutar servidor en modo TESTING con datos de prueba
# PowerShell version

Write-Host "============================================" -ForegroundColor Magenta
Write-Host " CaosNews - Servidor de QA" -ForegroundColor Magenta
Write-Host "============================================" -ForegroundColor Magenta

# Cambiar al directorio del proyecto
$projectPath = Split-Path -Parent $PSScriptRoot
Set-Location $projectPath

Write-Host "Configurando entorno de QA..." -ForegroundColor Yellow
$env:DJANGO_SETTINGS_MODULE = "CaosNews.settings.settings_qa"

Write-Host "Reseteando y configurando base de datos de QA..." -ForegroundColor Yellow
python manage.py setup_qa

Write-Host ""
Write-Host "Iniciando servidor de testing..." -ForegroundColor Magenta
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Red
Write-Host "Abrir en navegador: http://127.0.0.1:8001" -ForegroundColor Cyan
Write-Host "Admin: http://127.0.0.1:8001/adminDJango/ (testadmin/testpass123)" -ForegroundColor Cyan
Write-Host ""

python manage.py runserver 127.0.0.1:8001
