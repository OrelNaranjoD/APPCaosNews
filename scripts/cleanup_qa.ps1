# Script para limpiar completamente el entorno QA y eliminar scripts obsoletos
param(
    [switch]$DryRun,
    [switch]$Verbose
)

function Write-ColorOutput {
    param($Message, $Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Show-Header {
    Write-ColorOutput "============================================" "Magenta"
    Write-ColorOutput " LIMPIEZA COMPLETA DEL ENTORNO QA" "Magenta"
    Write-ColorOutput "============================================" "Magenta"
    Write-ColorOutput ""
}

function Remove-QAFile {
    param($Path, $Description)

    if (-not (Test-Path $Path)) {
        Write-ColorOutput "  $Description no encontrado: $Path" "Yellow"
        return
    }

    if ($DryRun) {
        Write-ColorOutput "[DRY RUN] Se eliminaria: $Description ($Path)" "Cyan"
        return
    }

    try {
        if (Test-Path $Path -PathType Container) {
            Remove-Item $Path -Recurse -Force
        } else {
            Remove-Item $Path -Force
        }
        Write-ColorOutput "  $Description eliminado exitosamente" "Green"

        if ($Verbose) {
            Write-ColorOutput "    Ruta: $Path" "Cyan"
        }
    } catch {
        Write-ColorOutput "  Error eliminando $Description`: $_" "Red"
    }
}

function Get-FileSize {
    param($Path)
    if (Test-Path $Path) {
        $size = (Get-Item $Path).Length / 1MB
        return [math]::Round($size, 2)
    }
    return 0
}

function Get-DirectoryFileCount {
    param($Path)
    if (Test-Path $Path) {
        return (Get-ChildItem $Path -Recurse -File | Measure-Object).Count
    }
    return 0
}

function Show-QAStatus {
    Write-ColorOutput "Estado actual del entorno QA:" "Cyan"
    Write-ColorOutput ""

    $projectPath = Split-Path -Parent $PSScriptRoot

    # Archivos y directorios de QA
    $qaFiles = @{
        "Base de datos QA" = "$projectPath\db_qa.sqlite3"
        "Directorio media QA" = "$projectPath\media_qa"
        "Archivo de logs QA" = "$projectPath\qa_debug.log"
        "Directorio emails QA" = "$projectPath\qa_emails"
        "Reporte cobertura QA" = "$projectPath\htmlcov_qa"
        "Archivo cobertura XML" = "$projectPath\coverage.xml"
    }

    # Scripts obsoletos (ya deberian estar eliminados)
    $obsoleteScripts = @{
        "Script qa.ps1" = "$projectPath\scripts\qa.ps1"
        "Script manage_qa.ps1" = "$projectPath\scripts\manage_qa.ps1"
    }

    $totalSize = 0
    $totalFiles = 0

    foreach ($item in $qaFiles.GetEnumerator()) {
        $exists = Test-Path $item.Value
        $status = if ($exists) { "Existe" } else { "No existe" }
        $color = if ($exists) { "Green" } else { "Yellow" }

        Write-ColorOutput "  $($item.Key): $status" $color

        if ($exists) {
            if (Test-Path $item.Value -PathType Container) {
                $fileCount = Get-DirectoryFileCount $item.Value
                Write-ColorOutput "    Archivos: $fileCount" "Cyan"
                $totalFiles += $fileCount
            } else {
                $size = Get-FileSize $item.Value
                Write-ColorOutput "    Tamaño: $size MB" "Cyan"
                $totalSize += $size
            }
        }
    }

    Write-ColorOutput ""
    Write-ColorOutput "Scripts obsoletos:" "Cyan"

    foreach ($script in $obsoleteScripts.GetEnumerator()) {
        $exists = Test-Path $script.Value
        $status = if ($exists) { "Existe (PENDIENTE ELIMINAR)" } else { "Eliminado" }
        $color = if ($exists) { "Yellow" } else { "Green" }

        Write-ColorOutput "  $($script.Key): $status" $color
    }

    Write-ColorOutput ""
    Write-ColorOutput "Resumen:" "Magenta"
    Write-ColorOutput "  Tamaño total archivos: $totalSize MB" "Cyan"
    Write-ColorOutput "  Total archivos en directorios: $totalFiles" "Cyan"
}

function Clean-QAEnvironment {
    $projectPath = Split-Path -Parent $PSScriptRoot
    Set-Location $projectPath

    Write-ColorOutput "Iniciando limpieza del entorno QA..." "Cyan"
    Write-ColorOutput ""

    # 1. Usar el comando Django clean_qa si existe el entorno virtual
    if ((Test-Path "venv\Scripts\Activate.ps1") -or (Test-Path ".venv\Scripts\Activate.ps1")) {
        Write-ColorOutput "Ejecutando comando Django clean_qa..." "Cyan"

        try {
            # Activar entorno virtual
            if (Test-Path "venv\Scripts\Activate.ps1") {
                & "venv\Scripts\Activate.ps1"
            } elseif (Test-Path ".venv\Scripts\Activate.ps1") {
                & ".venv\Scripts\Activate.ps1"
            }

            if (-not $DryRun) {
                # Configurar entorno QA y ejecutar limpieza
                $env:DJANGO_SETTINGS_MODULE = "CaosNews.settings.settings_qa"
                python manage.py clean_qa --all --force

                if ($LASTEXITCODE -eq 0) {
                    Write-ColorOutput "  Comando Django clean_qa ejecutado exitosamente" "Green"
                } else {
                    Write-ColorOutput "  El comando Django clean_qa fallo, continuando con limpieza manual..." "Yellow"
                }
            } else {
                Write-ColorOutput "[DRY RUN] Se ejecutaria: python manage.py clean_qa --all" "Cyan"
            }
        } catch {
            Write-ColorOutput "  Error ejecutando comando Django, continuando con limpieza manual..." "Yellow"
            if ($Verbose) {
                Write-ColorOutput "    Error: $_" "Red"
            }
        }
    } else {
        Write-ColorOutput "  Entorno virtual no encontrado, usando limpieza manual..." "Yellow"
    }

    Write-ColorOutput ""
    Write-ColorOutput "Limpieza manual de archivos y directorios..." "Cyan"

    # 2. Limpiar archivos y directorios QA manualmente
    Remove-QAFile "$projectPath\db_qa.sqlite3" "Base de datos QA"
    Remove-QAFile "$projectPath\media_qa" "Directorio media QA"
    Remove-QAFile "$projectPath\qa_debug.log" "Archivo de logs QA"
    Remove-QAFile "$projectPath\qa_debug.log.1" "Archivo de logs QA (rotado 1)"
    Remove-QAFile "$projectPath\qa_debug.log.2" "Archivo de logs QA (rotado 2)"
    Remove-QAFile "$projectPath\qa_emails" "Directorio emails QA"
    Remove-QAFile "$projectPath\htmlcov_qa" "Directorio reporte cobertura QA"
    Remove-QAFile "$projectPath\coverage.xml" "Archivo cobertura XML"

    # 3. Limpiar archivos de prueba adicionales
    Remove-QAFile "$projectPath\.coverage" "Archivo cobertura pytest"
    Remove-QAFile "$projectPath\.pytest_cache" "Cache de pytest"

    # 4. Eliminar logs
    Remove-QAFile "$projectPath\caosnews_qa.log" "Log de QA"
}

function Show-Summary {
    Write-ColorOutput ""
    Write-ColorOutput "============================================" "Green"
    Write-ColorOutput " LIMPIEZA COMPLETADA" "Green"
    Write-ColorOutput "============================================" "Green"
    Write-ColorOutput ""

    if ($DryRun) {
        Write-ColorOutput "Esta fue una ejecucion de prueba (DRY RUN)" "Cyan"
        Write-ColorOutput "Para ejecutar la limpieza real, ejecuta:" "Cyan"
        Write-ColorOutput "   .\scripts\cleanup_qa.ps1" "Cyan"
    } else {
        Write-ColorOutput "El entorno QA ha sido limpiado completamente:" "Green"
        Write-ColorOutput ""
        Write-ColorOutput "Se eliminaron:" "Cyan"
        Write-ColorOutput "  • Base de datos QA (db_qa.sqlite3)" "Green"
        Write-ColorOutput "  • Archivos media QA (media_qa/)" "Green"
        Write-ColorOutput "  • Logs de QA (qa_debug.log*)" "Green"
        Write-ColorOutput "  • Emails de QA (qa_emails/)" "Green"
        Write-ColorOutput "  • Reportes de cobertura (htmlcov_qa/, coverage.xml)" "Green"
        Write-ColorOutput "  • Cache de pytest (.coverage, .pytest_cache)" "Green"
        Write-ColorOutput "  • Scripts obsoletos (qa.ps1, manage_qa.ps1)" "Green"
        Write-ColorOutput ""
        Write-ColorOutput "Para recrear el entorno QA en el futuro, usa:" "Cyan"
        Write-ColorOutput "   .\scripts\run_qa_server.ps1" "Cyan"
    }
}

function Show-Help {
    Write-ColorOutput "Script de Limpieza QA - CaosNews" "Magenta"
    Write-ColorOutput ""
    Write-ColorOutput "DESCRIPCION:" "Cyan"
    Write-ColorOutput "  Limpia completamente el entorno QA eliminando todos los datos"
    Write-ColorOutput "  de prueba, archivos temporales y scripts obsoletos."
    Write-ColorOutput "  NOTA: No pide confirmacion, ejecuta la limpieza directamente."
    Write-ColorOutput ""
    Write-ColorOutput "USO:" "Cyan"
    Write-ColorOutput "  .\scripts\cleanup_qa.ps1 [opciones]" "Cyan"
    Write-ColorOutput ""
    Write-ColorOutput "OPCIONES:" "Cyan"
    Write-ColorOutput "  -DryRun     Simula la operacion sin hacer cambios reales"
    Write-ColorOutput "  -Verbose    Muestra informacion detallada durante la ejecucion"
    Write-ColorOutput ""
    Write-ColorOutput "EJEMPLOS:" "Cyan"
    Write-ColorOutput "  .\scripts\cleanup_qa.ps1                    # Limpieza directa"
    Write-ColorOutput "  .\scripts\cleanup_qa.ps1 -DryRun            # Ver que se eliminaria"
    Write-ColorOutput "  .\scripts\cleanup_qa.ps1 -DryRun -Verbose   # Ver detalles de la simulacion"
    Write-ColorOutput ""
}

# === PROGRAMA PRINCIPAL ===

# Verificar si se pidio ayuda
if ($args -contains "--help" -or $args -contains "-h" -or $args -contains "help") {
    Show-Help
    exit 0
}

# Mostrar encabezado
Show-Header

# Mostrar estado actual
Show-QAStatus

# Ejecutar limpieza directamente sin confirmación
Clean-QAEnvironment

# Mostrar resumen
Show-Summary

Write-ColorOutput ""
Write-ColorOutput "Estado final:" "Cyan"
Show-QAStatus
