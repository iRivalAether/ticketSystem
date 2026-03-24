@echo off
REM Script para inicializar datos del sistema
REM Este script activa el entorno virtual y carga datos iniciales

echo ============================================
echo Inicializador de Datos - Ticket System
echo ============================================
echo.

REM Verificar si existe el entorno virtual
if not exist venv (
    echo [!] Entorno virtual no encontrado
    echo [*] Primero debes ejecutar "instalar_dependencias.bat"
    echo.
    pause
    exit /b 1
)

REM Activar el entorno virtual
echo [*] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Ejecutar comando de inicialización
echo [*] Cargando datos iniciales en la base de datos...
echo [*] Esto creará:
echo     - 3 roles (Operativo, Jefe de Área, Supervisión General)
echo     - 3 áreas (Soporte, Infraestructura, Por Definir)
echo     - 4 prioridades (Crítica, Alta, Media, Baja)
echo     - 4 SLAs predefinidos
echo     - 3 jornadas laborales
echo.

python manage.py init_data

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo [✓] Datos inicializados correctamente
    echo ============================================
    echo.
    echo El sistema está listo con datos de ejemplo
    echo Siguiente paso: ejecuta "crear_superusuario.bat"
    echo.
) else (
    echo.
    echo ============================================
    echo [✗] Error al inicializar datos
    echo ============================================
    echo.
    pause
    exit /b 1
)

pause
