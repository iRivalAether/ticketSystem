# Comandos Rápidos - Sistema de Tickets

## Comandos de Instalación y Setup

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Copiar configuración
cp .env.example .env
# Editar .env con tus credenciales

# 4. Crear base de datos MySQL
mysql -u root -p
CREATE DATABASE ticket_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 5. Migraciones
python manage.py makemigrations
python manage.py migrate

# 6. Inicializar datos
python manage.py init_data

# 7. Crear superusuario
python manage.py createsuperuser

# 8. Ejecutar servidor
python manage.py runserver
```

## Comandos de Desarrollo

```bash
# Servidor de desarrollo
python manage.py runserver
python manage.py runserver 0.0.0.0:8000  # Accesible desde red

# Shell interactivo
python manage.py shell
python manage.py shell_plus  # Con extensiones

# Ver logs en tiempo real (Windows PowerShell)
Get-Content logs\ticketSystem.log -Wait

# Crear nueva app
python manage.py startapp nombre_app apps/nombre_app
```

## Comandos de Base de Datos

```bash
# Crear migraciones
python manage.py makemigrations
python manage.py makemigrations nombre_app

# Aplicar migraciones
python manage.py migrate
python manage.py migrate nombre_app

# Ver SQL de migraciones (sin aplicar)
python manage.py sqlmigrate nombre_app numero_migracion

# Verificar migraciones pendientes
python manage.py showmigrations

# Revertir migración
python manage.py migrate nombre_app numero_anterior

# Limpiar base de datos (¡CUIDADO!)
python manage.py flush
```

## Comandos Personalizados

```bash
# Inicializar datos del sistema
python manage.py init_data

# Cerrar tickets inactivos
python manage.py cerrar_tickets_inactivos
```

## Comandos de Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Tests de una app específica
python manage.py test apps.tickets

# Test específico
python manage.py test apps.tickets.tests.test_models.TicketModelTest

# Con verbosity
python manage.py test --verbosity=2

# Mantener base de datos de test
python manage.py test --keepdb
```

## Comandos de Usuario

```bash
# Crear superusuario
python manage.py createsuperuser

# Cambiar password de usuario
python manage.py changepassword email@ejemplo.com
```

## Comandos de Verificación

```bash
# Verificar problemas del proyecto
python manage.py check

# Verificar solo seguridad
python manage.py check --deploy

# Ver configuración actual
python manage.py diffsettings
```

## Comandos de Archivos Estáticos

```bash
# Recopilar archivos estáticos
python manage.py collectstatic

# Limpiar archivos estáticos anteriores
python manage.py collectstatic --clear --noinput
```

## Comandos de Información

```bash
# Ver versión de Django
python -m django --version

# Ver apps instaladas
python manage.py showmigrations

# Ver configuración de BD
python manage.py dbshell
```

## Ejemplos en Django Shell

```python
# Acceder al shell
python manage.py shell_plus

# Importar modelos
from apps.usuarios.models import Usuario, Rol
from apps.tickets.models import Ticket, Area, Prioridad, SLA
from services.ticket_service import TicketService

# Crear usuario
rol = Rol.objects.get(nombre='Operativo')
usuario = Usuario.objects.create_user(
    email='test@example.com',
    nombre='Usuario Test',
    password='password123',
    rol=rol
)

# Crear ticket
prioridad = Prioridad.objects.get(nombre='Media')
sla = SLA.objects.get(nombre='SLA Medio')
datos = {
    'nombre': 'Problema de conexión',
    'descripcion': 'No puedo conectarme al servidor',
    'prioridad_id': prioridad.id,
    'sla_id': sla.id,
}
ticket = TicketService.crear_ticket(datos)

# Ver tickets
tickets = Ticket.objects.abiertos()
print(f"Tickets abiertos: {tickets.count()}")

# Ver tickets de un usuario
mis_tickets = Ticket.objects.por_usuario(usuario)

# Verificar SLA de ticket
ticket = Ticket.objects.first()
print(f"Estado SLA: {ticket.sla_status}")
print(f"Folio: {ticket.folio}")

# Generar reporte
from services.reporte_service import ReporteService
reporte = ReporteService.generar_reporte_semanal(usuario)
kpi = reporte.kpis.first()
print(f"Cumplimiento SLA: {kpi.cumplimiento_sla}%")
```

## URLs Importantes

```
# Aplicación
http://localhost:8000/

# Admin Panel
http://localhost:8000/admin/

# API Documentation (Swagger)
http://localhost:8000/api/docs/

# API Documentation (ReDoc)
http://localhost:8000/api/redoc/

# Debug Toolbar (en desarrollo)
http://localhost:8000/__debug__/
```

## Git Commands (Workflow)

```bash
# Inicializar repositorio
git init
git add .
git commit -m "Initial commit: Django project structure"

# Trabajar con branches
git checkout -b feature/nueva-funcionalidad
git add .
git commit -m "feat: descripción del cambio"
git push origin feature/nueva-funcionalidad

# Volver a main
git checkout main
git pull origin main
git merge feature/nueva-funcionalidad
```

## Comandos de Producción

```bash
# Cambiar a settings de producción
export DJANGO_SETTINGS_MODULE=config.settings.production  # Linux/Mac
$env:DJANGO_SETTINGS_MODULE="config.settings.production"  # PowerShell

# Recopilar estáticos para producción
python manage.py collectstatic --noinput

# Verificar deployment
python manage.py check --deploy

# Crear archivo de fixtures (backup de datos)
python manage.py dumpdata > backup.json

# Cargar fixtures
python manage.py loaddata backup.json
```

## Troubleshooting Commands

```bash
# Limpiar archivos .pyc
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item  # PowerShell
find . -name "*.pyc" -delete  # Linux/Mac

# Reinstalar dependencias
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Ver paquetes instalados
pip list
pip freeze

# Actualizar pip
python -m pip install --upgrade pip
```

## Comandos MySQL Útiles

```sql
-- Conectar a MySQL
mysql -u root -p

-- Ver bases de datos
SHOW DATABASES;

-- Usar base de datos
USE ticket_system;

-- Ver tablas
SHOW TABLES;

-- Ver estructura de tabla
DESCRIBE nombre_tabla;

-- Backup de base de datos
-- En terminal (fuera de MySQL):
mysqldump -u root -p ticket_system > backup.sql

-- Restaurar backup
mysql -u root -p ticket_system < backup.sql

-- Ver tamaño de tablas
SELECT 
    table_name AS 'Tabla',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Tamaño (MB)'
FROM information_schema.TABLES 
WHERE table_schema = 'ticket_system'
ORDER BY (data_length + index_length) DESC;
```

## Atajos de Desarrollo

```bash
# Alias útiles (agregar a tu .bashrc o perfil de PowerShell)

# alias para activar entorno
alias activate='venv\Scripts\activate'

# alias para servidor
alias runserver='python manage.py runserver'

# alias para shell
alias shell='python manage.py shell_plus'

# alias para migraciones
alias mkmigrations='python manage.py makemigrations'
alias migrate='python manage.py migrate'

# alias para tests
alias test='python manage.py test'
```

---

**Tip**: Guarda este archivo en favoritos para acceso rápido a comandos comunes.
