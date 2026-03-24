@echo off
REM Script para instalar automáticamente las dependencias del proyecto
REM Este script activa el entorno virtual y instala los paquetes de requirements.txt

echo ============================================
echo Instalador de Dependencias - Ticket System
echo ============================================
echo.

REM Verificar si existe el entorno virtual
if not exist venv (
    echo [!] Entorno virtual no encontrado
    echo [*] Creando entorno virtual...
    python -m venv venv
)

REM Activar el entorno virtual
echo [*] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar las dependencias
echo [*] Instalando dependencias desde requirements.txt...
pip install -r requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo [✓] Dependencias instaladas correctamente
    echo ============================================
    echo.
    echo Siguiente paso: ejecuta "ejecutar_proyecto.bat"
    echo.
) else (
    echo.
    echo ============================================
    echo [✗] Error al instalar dependencias
    echo ============================================
    echo.
    pause
)

pause
