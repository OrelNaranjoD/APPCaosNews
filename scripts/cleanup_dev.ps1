# Script para limpiar completamente el entorno de desarrollo y eliminar scripts obsoletos
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
    Write-ColorOutput " LIMPIEZA COMPLETA DEL ENTORNO DE DESARROLLO" "Magenta"
    Write-ColorOutput "============================================" "Magenta"
    Write-ColorOutput ""
}

function Remove-DevFile {
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

function Show-DevStatus {
    Write-ColorOutput "Estado actual del entorno de desarrollo:" "Cyan"
    Write-ColorOutput ""

    $projectPath = Split-Path -Parent $PSScriptRoot

    # Archivos y directorios de desarrollo
    $devFiles = @{
        "Base de datos DEV" = "$projectPath\db_dev.sqlite3"
        "Directorio media DEV" = "$projectPath\media_dev"
        "Archivo de logs DEV" = "$projectPath\dev_debug.log"
        "Directorio emails DEV" = "$projectPath\dev_emails"
        "Reporte cobertura DEV" = "$projectPath\htmlcov_dev"
    }

    $totalSize = 0
    $totalFiles = 0

    foreach ($item in $devFiles.GetEnumerator()) {
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
    Write-ColorOutput "Resumen:" "Magenta"
    Write-ColorOutput "  Tamaño total archivos: $totalSize MB" "Cyan"
    Write-ColorOutput "  Total archivos en directorios: $totalFiles" "Cyan"
}

function Clean-DevEnvironment {
    $projectPath = Split-Path -Parent $PSScriptRoot
    Set-Location $projectPath

    Write-ColorOutput "Iniciando limpieza del entorno de desarrollo..." "Cyan"
    Write-ColorOutput ""

    # 1. Usar el comando Django clean_dev si existe el entorno virtual
    if ((Test-Path "venv\Scripts\Activate.ps1") -or (Test-Path ".venv\Scripts\Activate.ps1")) {
        Write-ColorOutput "Ejecutando comando Django clean_dev..." "Cyan"

        try {
            # Activar entorno virtual
            if (Test-Path "venv\Scripts\Activate.ps1") {
                & "venv\Scripts\Activate.ps1"
            } elseif (Test-Path ".venv\Scripts\Activate.ps1") {
                & ".venv\Scripts\Activate.ps1"
            }

            if (-not $DryRun) {
                # Configurar entorno DEV y ejecutar limpieza
                $env:DJANGO_SETTINGS_MODULE = "CaosNews.settings.settings_dev"
                python manage.py clean_dev --all --force

                if ($LASTEXITCODE -eq 0) {
                    Write-ColorOutput "  Comando Django clean_dev ejecutado exitosamente" "Green"
                } else {
                    Write-ColorOutput "  El comando Django clean_dev fallo, continuando con limpieza manual..." "Yellow"
                }
            } else {
                Write-ColorOutput "[DRY RUN] Se ejecutaria: python manage.py clean_dev --all" "Cyan"
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

    # 2. Limpiar archivos y directorios DEV manualmente
    Remove-DevFile "$projectPath\db_dev.sqlite3" "Base de datos DEV"
    Remove-DevFile "$projectPath\db_dev.sqlite3-journal" "Journal de base de datos DEV"
    Remove-DevFile "$projectPath\media_dev" "Directorio media DEV"
    Remove-DevFile "$projectPath\dev_debug.log" "Archivo de logs DEV"
    Remove-DevFile "$projectPath\dev_debug.log.1" "Archivo de logs DEV (rotado 1)"
    Remove-DevFile "$projectPath\dev_debug.log.2" "Archivo de logs DEV (rotado 2)"
    Remove-DevFile "$projectPath\dev_emails" "Directorio emails DEV"
    Remove-DevFile "$projectPath\htmlcov_dev" "Directorio reporte cobertura DEV"

    # 3. Limpiar archivos de prueba adicionales específicos de desarrollo
    Remove-DevFile "$projectPath\.coverage" "Archivo cobertura pytest"
    Remove-DevFile "$projectPath\.pytest_cache" "Cache de pytest"
    Remove-DevFile "$projectPath\__pycache__" "Cache de Python raíz"
    Remove-DevFile "$projectPath\CaosNewsApp\__pycache__" "Cache de Python CaosNewsApp"
    Remove-DevFile "$projectPath\CaosNews\__pycache__" "Cache de Python CaosNews"

    # 4. Limpiar archivos de desarrollo temporales
    Write-ColorOutput ""
    Write-ColorOutput "Limpiando archivos temporales de desarrollo..." "Cyan"
    Remove-DevFile "$projectPath\caosnews_dev.log" "Archivo de logs de desarrollo"

    # Buscar y eliminar archivos .pyc y __pycache__ recursivamente
    if (-not $DryRun) {
        Get-ChildItem -Path $projectPath -Name "*.pyc" -Recurse -Force | ForEach-Object {
            $fullPath = Join-Path $projectPath $_
            Remove-DevFile $fullPath "Archivo .pyc"
        }

        Get-ChildItem -Path $projectPath -Name "__pycache__" -Directory -Recurse -Force | ForEach-Object {
            $fullPath = Join-Path $projectPath $_
            Remove-DevFile $fullPath "Directorio __pycache__"
        }
    } else {
        Write-ColorOutput "[DRY RUN] Se eliminarian todos los archivos .pyc y directorios __pycache__" "Cyan"
    }
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
        Write-ColorOutput "   .\scripts\cleanup_dev.ps1" "Cyan"
    } else {
        Write-ColorOutput "El entorno de desarrollo ha sido limpiado completamente:" "Green"
        Write-ColorOutput ""
        Write-ColorOutput "Se eliminaron:" "Cyan"
        Write-ColorOutput "  • Base de datos DEV (db_dev.sqlite3)" "Green"
        Write-ColorOutput "  • Archivos media DEV (media_dev/)" "Green"
        Write-ColorOutput "  • Logs de DEV (dev_debug.log*)" "Green"
        Write-ColorOutput "  • Emails de DEV (dev_emails/)" "Green"
        Write-ColorOutput "  • Reportes de cobertura (htmlcov_dev/)" "Green"
        Write-ColorOutput "  • Cache de Python (__pycache__/, *.pyc)" "Green"
        Write-ColorOutput "  • Cache de pytest (.coverage, .pytest_cache)" "Green"
        Write-ColorOutput ""
        Write-ColorOutput "Para recrear el entorno de desarrollo en el futuro, usa:" "Cyan"
        Write-ColorOutput "   .\scripts\run_dev_server.ps1" "Cyan"
        Write-ColorOutput "   python manage.py setup_dev" "Cyan"
    }
}

function Show-Help {
    Write-ColorOutput "Script de Limpieza DEV - CaosNews" "Magenta"
    Write-ColorOutput ""
    Write-ColorOutput "DESCRIPCION:" "Cyan"
    Write-ColorOutput "  Limpia completamente el entorno de desarrollo eliminando todos los datos"
    Write-ColorOutput "  de desarrollo, archivos temporales y cache de Python."
    Write-ColorOutput "  NOTA: No pide confirmacion, ejecuta la limpieza directamente."
    Write-ColorOutput ""
    Write-ColorOutput "USO:" "Cyan"
    Write-ColorOutput "  .\scripts\cleanup_dev.ps1 [opciones]" "Cyan"
    Write-ColorOutput ""
    Write-ColorOutput "OPCIONES:" "Cyan"
    Write-ColorOutput "  -DryRun     Simula la operacion sin hacer cambios reales"
    Write-ColorOutput "  -Verbose    Muestra informacion detallada durante la ejecucion"
    Write-ColorOutput ""
    Write-ColorOutput "EJEMPLOS:" "Cyan"
    Write-ColorOutput "  .\scripts\cleanup_dev.ps1                    # Limpieza directa"
    Write-ColorOutput "  .\scripts\cleanup_dev.ps1 -DryRun            # Ver que se eliminaria"
    Write-ColorOutput "  .\scripts\cleanup_dev.ps1 -DryRun -Verbose   # Ver detalles de la simulacion"
    Write-ColorOutput ""
    Write-ColorOutput "PASOS DESPUES DE LA LIMPIEZA:" "Cyan"
    Write-ColorOutput "  1. .\scripts\run_dev_server.ps1              # Recrear entorno automáticamente"
    Write-ColorOutput "  2. python manage.py setup_dev                # O recrear manualmente"
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
Show-DevStatus

# Ejecutar limpieza directamente sin confirmación
Clean-DevEnvironment

# Mostrar resumen
Show-Summary

Write-ColorOutput ""
Write-ColorOutput "Estado final:" "Cyan"
Show-DevStatus
