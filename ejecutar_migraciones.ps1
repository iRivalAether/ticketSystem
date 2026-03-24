# Script para ejecutar migraciones de la base de datos
# PowerShell version - Ejecutar como: .\ejecutar_migraciones.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Ejecutor de Migraciones - Ticket System" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si existe el entorno virtual
if (-not (Test-Path "venv")) {
    Write-Host "[!] Entorno virtual no encontrado" -ForegroundColor Red
    Write-Host "[*] Primero debes ejecutar '.\instalar_dependencias.ps1'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter para cerrar"
    exit 1
}

# Activar el entorno virtual
Write-Host "[*] Activando entorno virtual..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"

# Crear migraciones
Write-Host "[*] Creando archivos de migraciones..." -ForegroundColor Green
python manage.py makemigrations

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Error al crear migraciones" -ForegroundColor Red
    Read-Host "Presiona Enter para cerrar"
    exit 1
}

# Aplicar migraciones
Write-Host "[*] Aplicando migraciones a la base de datos..." -ForegroundColor Green
python manage.py migrate

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "[✓] Migraciones ejecutadas correctamente" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Base de datos actualizada exitosamente" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "[✗] Error al aplicar migraciones" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    Write-Host ""
    Read-Host "Presiona Enter para cerrar"
    exit 1
}

Read-Host "Presiona Enter para cerrar"
