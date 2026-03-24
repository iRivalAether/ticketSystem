@echo off
REM Script para ejecutar migraciones de la base de datos
REM Este script activa el entorno virtual y ejecuta las migraciones Django

echo ============================================
echo Ejecutor de Migraciones - Ticket System
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

REM Crear migraciones
echo [*] Creando archivos de migraciones...
python manage.py makemigrations

if %ERRORLEVEL% NEQ 0 (
    echo [!] Error al crear migraciones
    pause
    exit /b 1
)

REM Aplicar migraciones
echo [*] Aplicando migraciones a la base de datos...
python manage.py migrate

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo [✓] Migraciones ejecutadas correctamente
    echo ============================================
    echo.
    echo Base de datos actualizada exitosamente
    echo.
) else (
    echo.
    echo ============================================
    echo [✗] Error al aplicar migraciones
    echo ============================================
    echo.
    pause
    exit /b 1
)

pause
