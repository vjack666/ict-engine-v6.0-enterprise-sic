# Script de Limpieza Completa de Caché - ICT Engine v6.0
# Creado para limpiar todos los archivos de caché y temporales

Write-Host "=== INICIANDO LIMPIEZA COMPLETA DE CACHÉ ===" -ForegroundColor Green

$basePath = "C:\Users\v_jac\Desktop\ict-engine-v6.0-enterprise-sic"

# 1. Eliminar directorios __pycache__
Write-Host "1. Eliminando directorios __pycache__..." -ForegroundColor Yellow
$pycacheDirs = Get-ChildItem -Path $basePath -Name "__pycache__" -Recurse -Directory
if ($pycacheDirs) {
    $pycacheDirs | ForEach-Object { 
        Remove-Item -Path "$basePath\$_" -Recurse -Force -Verbose 
    }
    Write-Host "   ✓ Eliminados $($pycacheDirs.Count) directorios __pycache__" -ForegroundColor Green
} else {
    Write-Host "   ✓ No se encontraron directorios __pycache__" -ForegroundColor Green
}

# 2. Eliminar archivos .pyc
Write-Host "2. Eliminando archivos .pyc..." -ForegroundColor Yellow
$pycFiles = Get-ChildItem -Path $basePath -Filter "*.pyc" -Recurse
if ($pycFiles) {
    $pycFiles | Remove-Item -Force -Verbose
    Write-Host "   ✓ Eliminados $($pycFiles.Count) archivos .pyc" -ForegroundColor Green
} else {
    Write-Host "   ✓ No se encontraron archivos .pyc" -ForegroundColor Green
}

# 3. Eliminar archivos temporales
Write-Host "3. Eliminando archivos temporales..." -ForegroundColor Yellow
$tempFiles = Get-ChildItem -Path $basePath -Filter "*.tmp" -Recurse
if ($tempFiles) {
    $tempFiles | Remove-Item -Force -Verbose
    Write-Host "   ✓ Eliminados $($tempFiles.Count) archivos temporales" -ForegroundColor Green
} else {
    Write-Host "   ✓ No se encontraron archivos temporales" -ForegroundColor Green
}

# 4. Limpiar logs (opcional - descomentar si deseas limpiar logs)
# Write-Host "4. Limpiando archivos de log..." -ForegroundColor Yellow
# $logPath = "$basePath\09-DASHBOARD\data\logs"
# if (Test-Path $logPath) {
#     Get-ChildItem -Path $logPath -Recurse -File | Remove-Item -Force -Verbose
#     Write-Host "   ✓ Logs limpiados" -ForegroundColor Green
# }

# 5. Eliminar archivos de cache específicos
Write-Host "4. Verificando archivos de caché específicos..." -ForegroundColor Yellow
$cacheFiles = Get-ChildItem -Path $basePath -Filter "*.cache" -Recurse
if ($cacheFiles) {
    $cacheFiles | Remove-Item -Force -Verbose
    Write-Host "   ✓ Eliminados $($cacheFiles.Count) archivos de caché" -ForegroundColor Green
} else {
    Write-Host "   ✓ No se encontraron archivos de caché específicos" -ForegroundColor Green
}

# 6. Mostrar estadísticas finales
Write-Host "5. Generando estadísticas finales..." -ForegroundColor Yellow
$totalFiles = (Get-ChildItem -Path $basePath -Recurse -File).Count
$totalSize = [math]::Round((Get-ChildItem -Path $basePath -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)

Write-Host ""
Write-Host "=== LIMPIEZA COMPLETADA ===" -ForegroundColor Green
Write-Host "Archivos totales en el proyecto: $totalFiles" -ForegroundColor Cyan
Write-Host "Tamaño total del proyecto: $totalSize MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "El sistema está ahora completamente limpio y listo para usar." -ForegroundColor Green
Write-Host "Los archivos de caché se regenerarán automáticamente cuando ejecutes el sistema." -ForegroundColor White
