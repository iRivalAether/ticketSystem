# Script para inicializar datos del sistema
# PowerShell version - Ejecutar como: .\inicializar_datos.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Inicializador de Datos - Ticket System" -ForegroundColor Cyan
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

# Mostrar qué se va a crear
Write-Host "[*] Cargando datos iniciales en la base de datos..." -ForegroundColor Green
Write-Host "[*] Esto creará:" -ForegroundColor Yellow
Write-Host "     - 3 roles (Operativo, Jefe de Área, Supervisión General)" -ForegroundColor Gray
Write-Host "     - 3 áreas (Soporte, Infraestructura, Por Definir)" -ForegroundColor Gray
Write-Host "     - 4 prioridades (Crítica, Alta, Media, Baja)" -ForegroundColor Gray
Write-Host "     - 4 SLAs predefinidos" -ForegroundColor Gray
Write-Host "     - 3 jornadas laborales" -ForegroundColor Gray
Write-Host ""

# Ejecutar comando de inicialización
python manage.py init_data

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "[✓] Datos inicializados correctamente" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "El sistema está listo con datos de ejemplo" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "[✗] Error al inicializar datos" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    Write-Host ""
    Read-Host "Presiona Enter para cerrar"
    exit 1
}

Read-Host "Presiona Enter para cerrar"
