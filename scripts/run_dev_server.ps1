# Script para ejecutar el servidor en modo NORMAL/DESARROLLO
# PowerShell version

Write-Host "============================================" -ForegroundColor Green
Write-Host " CaosNews - Servidor de Desarrollo" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

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

Write-Host "Configurando entorno de desarrollo..." -ForegroundColor Yellow
$env:DJANGO_SETTINGS_MODULE = "CaosNews.settings.settings_dev"

Write-Host "Verificando configuración de Django..." -ForegroundColor Yellow
python manage.py check
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error en la configuración de Django" -ForegroundColor Red
    pause
    exit 1
}

python manage.py setup_dev

Write-Host "Aplicando migraciones..." -ForegroundColor Yellow
python manage.py migrate
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migraciones aplicadas correctamente" -ForegroundColor Green
} else {
    Write-Host "❌ Error al aplicar migraciones" -ForegroundColor Red
    Write-Host "💡 Sugerencias:" -ForegroundColor Yellow
    Write-Host "   - Verificar la integridad de la base de datos" -ForegroundColor Yellow
    Write-Host "   - Hacer backup y recrear la BD si es necesario" -ForegroundColor Yellow
    Write-Host "   - Usar: python manage.py migrate --fake-initial" -ForegroundColor Yellow

    $choice = Read-Host "¿Continuar sin migraciones? (s/N)"
    if ($choice -ne "s" -and $choice -ne "S") {
        exit 1
    }
}

Write-Host ""
Write-Host "Iniciando servidor de desarrollo..." -ForegroundColor Green
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Red
Write-Host "Abrir en navegador: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""

python manage.py runserver 127.0.0.1:8000
