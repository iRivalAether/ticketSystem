# Script para instalar automáticamente las dependencias del proyecto
# PowerShell version - Ejecutar como: .\instalar_dependencias.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Instalador de Dependencias - Ticket System" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si existe el entorno virtual
if (-not (Test-Path "venv")) {
    Write-Host "[!] Entorno virtual no encontrado" -ForegroundColor Yellow
    Write-Host "[*] Creando entorno virtual..." -ForegroundColor Green
    python -m venv venv
}

# Activar el entorno virtual
Write-Host "[*] Activando entorno virtual..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"

# Instalar las dependencias
Write-Host "[*] Instalando dependencias desde requirements.txt..." -ForegroundColor Green
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "[✓] Dependencias instaladas correctamente" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Siguiente paso: ejecuta '.\ejecutar_proyecto.ps1'" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "[✗] Error al instalar dependencias" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    Write-Host ""
}

Write-Host "Presiona Enter para cerrar..." -ForegroundColor Gray
Read-Host
