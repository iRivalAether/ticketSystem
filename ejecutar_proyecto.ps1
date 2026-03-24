# Script para ejecutar el servidor Django del Ticket System
# PowerShell version - Ejecutar como: .\ejecutar_proyecto.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Ejecutor de Proyecto - Ticket System" -ForegroundColor Cyan
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

# Verificar conexión a la base de datos y ejecutar migraciones si es necesario
Write-Host "[*] Verificando integridad del proyecto..." -ForegroundColor Green
python manage.py check
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Error en la configuración del proyecto" -ForegroundColor Red
    Read-Host "Presiona Enter para cerrar"
    exit 1
}

# Ejecutar el servidor
Write-Host "[*] Iniciando servidor Django..." -ForegroundColor Green
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Servidor iniciado correctamente" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Abre tu navegador en: " -ForegroundColor Yellow -NoNewline
Write-Host "http://localhost:8000" -ForegroundColor Cyan
Write-Host "Para parar el servidor: " -ForegroundColor Yellow -NoNewline
Write-Host "Ctrl + C" -ForegroundColor Cyan
Write-Host ""

python manage.py runserver
