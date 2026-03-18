# Guía de Desarrollo - Sistema de Gestión de Tickets

## Configuración del Entorno de Desarrollo

### 1. Requisitos Previos

- Python 3.10 o superior
- MySQL 8.0 o superior
- pip (gestor de paquetes de Python)
- Virtualenv o venv

### 2. Instalación Paso a Paso

#### a) Clonar el repositorio

```bash
cd c:\pruebas\ticketSystem
```

#### b) Crear entorno virtual

```bash
python -m venv venv
```

#### c) Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

#### d) Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configuración de Base de Datos

#### a) Crear base de datos MySQL

Conectarse a MySQL:
```bash
mysql -u root -p
```

Ejecutar:
```sql
CREATE DATABASE ticket_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ticketuser'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON ticket_system.* TO 'ticketuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### b) Configurar variables de entorno

Copiar archivo de ejemplo:
```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:
```env
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=ticket_system
DB_USER=ticketuser
DB_PASSWORD=password123
DB_HOST=localhost
DB_PORT=3306
```

### 4. Migraciones de Base de Datos

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate
```

### 5. Inicializar Datos Básicos

```bash
python manage.py init_data
```

Este comando crea:
- 3 roles (Operativo, Jefe de Área, Supervisión General)
- 3 áreas (Soporte, Infraestructura, Por Definir)
- 4 prioridades (Crítica, Alta, Media, Baja)
- 4 SLAs predefinidos
- 3 jornadas (Matutina, Vespertina, Nocturna)

### 6. Crear Superusuario

```bash
python manage.py createsuperuser
```

Proporciona:
- Email: admin@example.com
- Nombre: Administrador
- Password: (tu contraseña segura)

### 7. Ejecutar Servidor de Desarrollo

```bash
python manage.py runserver
```

El sistema estará disponible en: http://localhost:8000

Admin panel: http://localhost:8000/admin

## Estructura del Proyecto

```
ticketSystem/
├── apps/                       # Aplicaciones Django
│   ├── core/                  # Funcionalidad común
│   │   ├── models.py         # Modelos base
│   │   └── ...
│   ├── usuarios/              # Gestión de usuarios
│   │   ├── models.py         # Usuario, Rol
│   │   ├── admin.py          # Admin personalizado
│   │   └── ...
│   ├── tickets/               # Sistema de tickets
│   │   ├── models.py         # Ticket, SLA, Area, etc.
│   │   ├── admin.py          # Admin con indicadores SLA
│   │   ├── management/       # Comandos personalizados
│   │   └── ...
│   └── reportes/              # Reportes y KPIs
│       ├── models.py         # Reporte, KPI
│       └── ...
├── services/                  # Capa de servicios
│   ├── ticket_service.py     # Lógica de negocio de tickets
│   └── reporte_service.py    # Lógica de reportes
├── config/                    # Configuración del proyecto
│   ├── settings/             # Settings por ambiente
│   │   ├── base.py          # Configuración base
│   │   ├── development.py   # Desarrollo
│   │   └── production.py    # Producción
│   ├── urls.py              # URLs principales
│   ├── wsgi.py
│   └── asgi.py
├── docs/                     # Documentación
│   └── ARQUITECTURA.md
├── static/                   # Archivos estáticos
├── media/                    # Archivos de usuario
├── logs/                     # Logs del sistema
├── requirements.txt          # Dependencias
├── .env.example             # Ejemplo de variables
├── .gitignore
├── manage.py
└── README.md
```

## Convenciones de Código

### Nomenclatura

- **Modelos**: PascalCase (`Usuario`, `Ticket`)
- **Métodos**: snake_case (`crear_ticket`, `obtener_tickets`)
- **Constantes**: UPPER_SNAKE_CASE (`ESTADO_ABIERTO`, `NIVEL_OPERATIVO`)
- **Variables**: snake_case (`usuario_asignado`, `fecha_creacion`)

### Modelos

Siempre heredar de `BaseModel`:

```python
from apps.core.models import BaseModel

class MiModelo(BaseModel):
    nombre = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'mi_tabla'
        verbose_name = 'Mi Modelo'
        verbose_name_plural = 'Mis Modelos'
```

### Servicios

Siempre usar métodos estáticos y transacciones:

```python
from django.db import transaction

class MiServicio:
    @staticmethod
    @transaction.atomic
    def realizar_operacion(datos):
        # Lógica aquí
        pass
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def mi_funcion():
    logger.info("Información importante")
    logger.error("Error ocurrido", exc_info=True)
```

## Testing

### Estructura de Tests

```
apps/tickets/tests/
├── __init__.py
├── test_models.py
├── test_services.py
└── test_views.py
```

### Ejecutar Tests

```bash
# Todos los tests
python manage.py test

# Tests de una app específica
python manage.py test apps.tickets

# Test específico
python manage.py test apps.tickets.tests.test_models.TicketModelTest
```

### Ejemplo de Test

```python
from django.test import TestCase
from apps.tickets.models import Ticket

class TicketModelTest(TestCase):
    def setUp(self):
        # Preparar datos
        pass
    
    def test_crear_ticket(self):
        # Test aquí
        pass
```

## Comandos Útiles

### Django Shell

```bash
python manage.py shell

# O con extensiones (mejor autocompletado)
python manage.py shell_plus
```

### Crear Nueva App

```bash
python manage.py startapp nombre_app apps/nombre_app
```

### Crear Migración Vacía

```bash
python manage.py makemigrations --empty nombre_app
```

### Revertir Migración

```bash
python manage.py migrate nombre_app numero_migracion
```

### Limpiar Base de Datos

```bash
python manage.py flush
```

## Workflow de Desarrollo

### 1. Crear Feature Branch

```bash
git checkout -b feature/nombre-feature
```

### 2. Desarrollar

- Escribir código siguiendo convenciones
- Agregar logging apropiado
- Documentar funciones complejas

### 3. Testing

```bash
python manage.py test
```

### 4. Verificar Errores

```bash
python manage.py check
```

### 5. Commit

```bash
git add .
git commit -m "feat: descripción del cambio"
```

### 6. Push y Pull Request

```bash
git push origin feature/nombre-feature
```

## Depuración

### Django Debug Toolbar

Ya está configurado en development. Accede a:
http://localhost:8000/__debug__/

### Logs

Los logs se guardan en:
- Consola (development)
- Archivo: `logs/ticketSystem.log`

### Shell Interactivo

```bash
python manage.py shell_plus

# Ejemplo de uso
from apps.tickets.models import Ticket
from services.ticket_service import TicketService

tickets = Ticket.objects.abiertos()
print(tickets.count())
```

## Buenas Prácticas

### 1. Separación de Responsabilidades

❌ **Incorrecto** - Lógica en la vista:
```python
def crear_ticket(request):
    ticket = Ticket.objects.create(...)
    # Mucha lógica aquí
```

✅ **Correcto** - Usar Service Layer:
```python
def crear_ticket(request):
    ticket = TicketService.crear_ticket(datos, request.user)
    return Response(...)
```

### 2. Usar Managers Personalizados

❌ **Incorrecto**:
```python
tickets = Ticket.objects.filter(estado='Abierto', is_active=True)
```

✅ **Correcto**:
```python
tickets = Ticket.objects.abiertos()
```

### 3. Validaciones en Servicios

❌ **Incorrecto** - Validaciones en vista:
```python
if not nombre or not prioridad:
    return error
```

✅ **Correcto** - En el servicio:
```python
@staticmethod
def crear_ticket(datos):
    if not datos.get('nombre'):
        raise ValidationError('Nombre requerido')
```

### 4. Usar Transactions

❌ **Incorrecto**:
```python
ticket.save()
historial.save()
```

✅ **Correcto**:
```python
@transaction.atomic
def operacion():
    ticket.save()
    historial.save()
```

## Solución de Problemas Comunes

### Error de Migración

```bash
# Eliminar migraciones y recrear
python manage.py migrate --fake nombre_app zero
rm apps/nombre_app/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
```

### Error de MySQL Connection

Verificar:
1. MySQL está corriendo
2. Credenciales en `.env` son correctas
3. Base de datos existe
4. Usuario tiene permisos

### ModuleNotFoundError

```bash
# Reinstalar dependencias
pip install -r requirements.txt
```

## Recursos Adicionales

- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/
- MySQL Docs: https://dev.mysql.com/doc/

## Contacto

Para dudas o soporte, contactar al equipo de desarrollo.
