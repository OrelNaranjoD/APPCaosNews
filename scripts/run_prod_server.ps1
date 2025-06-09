# Script para ejecutar el servidor en modo PRODUCCIÓN
# PowerShell version

Write-Host "============================================" -ForegroundColor Red
Write-Host " CaosNews - Servidor de Produccion" -ForegroundColor Red
Write-Host "============================================" -ForegroundColor Red
Write-Host ""

# Cambiar al directorio del proyecto
$projectPath = Split-Path -Parent $PSScriptRoot
Set-Location $projectPath

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "manage.py")) {
    Write-Host "[ERROR] No se encontro manage.py en el directorio actual" -ForegroundColor Red
    Write-Host "   Directorio actual: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "   Asegurese de estar en el directorio raiz del proyecto Django" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] Directorio del proyecto: $(Get-Location)" -ForegroundColor Green

# Activar entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    try {
        & "venv\Scripts\Activate.ps1"
        Write-Host "[OK] Entorno virtual activado" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Error activando entorno virtual: $_" -ForegroundColor Red
        exit 1
    }
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    try {
        & ".venv\Scripts\Activate.ps1"
        Write-Host "[OK] Entorno virtual activado" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Error activando entorno virtual: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[ERROR] Entorno virtual no encontrado." -ForegroundColor Red
    Write-Host "   Ejecute: python -m venv venv" -ForegroundColor Yellow
    Write-Host "   Luego: venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "   Y: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host "Configurando entorno de produccion..." -ForegroundColor Yellow
$env:DJANGO_SETTINGS_MODULE = "CaosNews.settings.settings_prod"

# Verificar que Django este disponible
Write-Host "Verificando instalacion de Django..." -ForegroundColor Yellow
try {
    $djangoVersion = python -c "import django; print(django.get_version())" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Django $djangoVersion encontrado" -ForegroundColor Green
    } else {
        throw "Django no encontrado"
    }
} catch {
    Write-Host "[ERROR] Django no esta instalado o no es accesible" -ForegroundColor Red
    Write-Host "   Ejecute: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host "Aplicando migraciones..." -ForegroundColor Yellow
try {
    python manage.py migrate
    if ($LASTEXITCODE -ne 0) {
        throw "Error en migraciones"
    }
    Write-Host "[OK] Migraciones aplicadas correctamente" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Error aplicando migraciones: $_" -ForegroundColor Red
    Write-Host "   Verifique la configuracion de la base de datos" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Iniciando servidor de produccion..." -ForegroundColor Red
Write-Host "   URL principal: http://127.0.0.1" -ForegroundColor Green
Write-Host "   Panel admin:   http://127.0.0.1/admin/" -ForegroundColor Green
Write-Host "   API REST:      http://127.0.0.1/api/" -ForegroundColor Green
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Ejecutar el servidor con el entorno virtual ya activado
try {
    Write-Host "Iniciando servidor Django en http://127.0.0.1" -ForegroundColor Cyan
    python manage.py runserver 127.0.0.1:80 --noreload
} catch {
    Write-Host "[ERROR] Error iniciando el servidor: $_" -ForegroundColor Red
    Write-Host "   Verifique que el puerto 80 no este en uso" -ForegroundColor Yellow
    Write-Host "   Use: netstat -an | findstr :80" -ForegroundColor Yellow
    exit 1
}
