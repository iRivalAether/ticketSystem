@echo off
REM Script para ejecutar el servidor Django del Ticket System
REM Este script activa el entorno virtual y ejecuta el servidor de desarrollo

echo ============================================
echo Ejecutor de Proyecto - Ticket System
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

REM Verificar conexión a la base de datos y ejecutar migraciones si es necesario
echo [*] Verificando integridad del proyecto...
python manage.py check
if %ERRORLEVEL% NEQ 0 (
    echo [!] Error en la configuración del proyecto
    pause
    exit /b 1
)

REM Ejecutar el servidor
echo [*] Iniciando servidor Django...
echo.
echo ============================================
echo Servidor iniciado correctamente
echo ============================================
echo.
echo Abre tu navegador en: http://localhost:8000
echo Para parar el servidor: Ctrl + C
echo.

python manage.py runserver

