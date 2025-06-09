# Script para ejecutar pruebas pytest en el entorno QA
# PowerShell version

Write-Host "============================================" -ForegroundColor Magenta
Write-Host " CaosNews - Pruebas QA" -ForegroundColor Magenta
Write-Host " (Ejecutar despues de iniciar el entorno QA)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Magenta

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

# Verificar que el entorno QA este configurado
Write-Host "Verificando entorno QA..." -ForegroundColor Yellow
$env:DJANGO_SETTINGS_MODULE = "CaosNews.settings.settings_qa"

# Verificar que existe la base de datos QA
if (-not (Test-Path "db_qa.sqlite3")) {
    Write-Host " Base de datos QA no encontrada." -ForegroundColor Red
    Write-Host "   Ejecute primero: .\scripts\run_qa_server.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host " Entorno QA verificado" -ForegroundColor Green
Write-Host ""

# Bucle principal del menú
do {
    # Mostrar opciones de ejecucion
    Write-Host " Opciones de prueba:" -ForegroundColor Cyan
    Write-Host "1. Pruebas unitarias (solo units/)" -ForegroundColor White
    Write-Host "2. Pruebas selenium (solo selenium_tests/)" -ForegroundColor White
    Write-Host "3. Pruebas con coverage (todas)" -ForegroundColor White
    Write-Host "4. Pruebas especificas (por archivo)" -ForegroundColor White
    Write-Host "5. Salir" -ForegroundColor White
    Write-Host ""

    # Leer opcion del usuario
    $opcion = Read-Host "Seleccione una opcion (1-5)"

    switch ($opcion) {
        "1" {
            Write-Host "Ejecutando solo pruebas unitarias..." -ForegroundColor Green
            python manage.py run_qa_tests --test-path "CaosNewsApp/tests/units/"
            Write-Host ""
            Write-Host "============================================" -ForegroundColor Green
            Write-Host " PRUEBAS UNITARIAS COMPLETADAS" -ForegroundColor Green
            Write-Host "============================================" -ForegroundColor Green
            Write-Host ""
            Start-Sleep -Seconds 2
        }
        "2" {
            Write-Host "Ejecutando solo pruebas selenium..." -ForegroundColor Green
            python manage.py run_qa_tests --test-path "CaosNewsApp/tests/selenium_tests/" --verbose
            Write-Host ""
            Write-Host "============================================" -ForegroundColor Green
            Write-Host " PRUEBAS SELENIUM COMPLETADAS" -ForegroundColor Green
            Write-Host "============================================" -ForegroundColor Green
            Write-Host ""
            Start-Sleep -Seconds 2
        }
        "3" {
            Write-Host "Ejecutando todas las pruebas con coverage..." -ForegroundColor Green
            python manage.py run_qa_tests --coverage --verbose
            Write-Host ""
            Write-Host "============================================" -ForegroundColor Green
            Write-Host " PRUEBAS CON COVERAGE COMPLETADAS" -ForegroundColor Green
            Write-Host "============================================" -ForegroundColor Green
            Write-Host ""
            Write-Host " Ver coverage: Abrir htmlcov_qa/index.html" -ForegroundColor Cyan
            Write-Host ""
            Start-Sleep -Seconds 2
        }        "4" {
            Write-Host ""
            Write-Host " Pruebas especificas disponibles:" -ForegroundColor Yellow
            Write-Host ""

            # Lista de archivos de test disponibles
            $testFiles = @(
                "CaosNewsApp/tests/units/test_models.py",
                "CaosNewsApp/tests/selenium_tests/test_create_news.py",
                "CaosNewsApp/tests/selenium_tests/test_success_login.py",
                "CaosNewsApp/tests/selenium_tests/test_failed_login.py"
            )

            # Mostrar lista numerada
            for ($i = 0; $i -lt $testFiles.Length; $i++) {
                $fileName = Split-Path $testFiles[$i] -Leaf
                $testType = if ($testFiles[$i] -like "*units*") { "[UNITARIA]" } else { "[SELENIUM]" }
                Write-Host "   $($i + 1). $fileName $testType" -ForegroundColor Gray
            }
            Write-Host ""
            Write-Host "   0. Escribir ruta manualmente" -ForegroundColor Cyan
            Write-Host ""

            $selection = Read-Host "Seleccione un archivo de pruebas (0-$($testFiles.Length)) o Enter para cancelar"

            if ([string]::IsNullOrWhiteSpace($selection)) {
                Write-Host "Operacion cancelada. Volviendo al menu..." -ForegroundColor Yellow
                Write-Host ""
                Start-Sleep -Seconds 1
            }
            elseif ($selection -eq "0") {
                Write-Host ""
                $testFile = Read-Host "Ingrese la ruta completa del archivo de pruebas"

                if ([string]::IsNullOrWhiteSpace($testFile)) {
                    Write-Host "Ruta de pruebas vacia. Volviendo al menu..." -ForegroundColor Yellow
                    Write-Host ""
                    Start-Sleep -Seconds 1
                }
                elseif (Test-Path $testFile) {
                    Write-Host "Ejecutando pruebas del archivo: $testFile" -ForegroundColor Green
                    python manage.py run_qa_tests --test-path "$testFile" --verbose
                    Write-Host ""
                    Write-Host "============================================" -ForegroundColor Green
                    Write-Host " PRUEBAS DEL ARCHIVO COMPLETADAS" -ForegroundColor Green
                    Write-Host "============================================" -ForegroundColor Green
                    Write-Host ""
                    Start-Sleep -Seconds 2
                }
                else {
                    Write-Host "Archivo no encontrado: $testFile" -ForegroundColor Red
                    Write-Host ""
                    Start-Sleep -Seconds 2
                }
            }
            elseif ($selection -match '^\d+$' -and [int]$selection -ge 1 -and [int]$selection -le $testFiles.Length) {
                $selectedFile = $testFiles[[int]$selection - 1]
                $testType = if ($selectedFile -like "*units*") { "UNITARIAS" } else { "SELENIUM" }

                Write-Host "Ejecutando pruebas $testType`: $selectedFile" -ForegroundColor Green
                python manage.py run_qa_tests --test-path "$selectedFile" --verbose
                Write-Host ""
                Write-Host "============================================" -ForegroundColor Green
                Write-Host " PRUEBAS $testType COMPLETADAS" -ForegroundColor Green
                Write-Host "============================================" -ForegroundColor Green
                Write-Host ""
                Start-Sleep -Seconds 2
            }
            else {
                Write-Host "Seleccion invalida. Debe ser un numero entre 0-$($testFiles.Length)." -ForegroundColor Red
                Write-Host ""
                Start-Sleep -Seconds 2
            }
        }
        "5" {
            Write-Host "Saliendo del script..." -ForegroundColor Yellow
            Write-Host ""
            Write-Host " Comandos útiles:" -ForegroundColor Cyan
            Write-Host "   Reiniciar entorno QA: python manage.py setup_qa" -ForegroundColor White
            Write-Host "   Ver coverage: Abrir htmlcov_qa/index.html" -ForegroundColor White
            Write-Host "   Ejecutar servidor QA: .\scripts\run_qa_server.ps1" -ForegroundColor White
            Write-Host ""
            break
        }
        default {
            Write-Host "Opcion no valida. Por favor seleccione una opcion entre 1-5." -ForegroundColor Red
            Write-Host ""
            Start-Sleep -Seconds 2
        }
    }
} while ($opcion -ne "5")
