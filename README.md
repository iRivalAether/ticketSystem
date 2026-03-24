# Sistema de Gestión de Tickets

Sistema profesional de gestión de tickets con seguimiento de SLA, asignaciones y reportes.

## 🎯 Características Principales

- ✅ **Interfaz Web Profesional** con diseño Blanco/Negro/Dorado
- ✅ **Gestión completa de tickets** con estados y seguimiento
- ✅ **Control de SLA** con semáforos (Verde, Amarillo, Rojo)
- ✅ **Jerarquía de 3 niveles**: Operativos, Jefes de Área, Supervisión General
- ✅ **Principio FIFO** (First In, First Out)
- ✅ **Jornadas laborales**: Matutina, Vespertina, Nocturna
- ✅ **Reportes y KPIs** avanzados
- ✅ **Cierre automático** de tickets inactivos
- ✅ **Trazabilidad completa** con historial inalterable
- ✅ **Arquitectura profesional** con patrones de diseño
- ✅ **Dashboard interactivo** con estadísticas en tiempo real

## 📋 Requisitos

- Python 3.10+
- MySQL 8.0+
- pip (gestor de paquetes)

## 🚀 Inicio Rápido

### 1. Crear entorno virtual

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 2. Opción A: Instalación Automática (Recomendado) ⚡

#### Flujo Completo - Primera vez:

1. **Instalar dependencias:**
   ```batch
   instalar_dependencias.bat
   ```
   o
   ```powershell
   .\instalar_dependencias.ps1
   ```

2. **Ejecutar migraciones:**
   ```batch
   ejecutar_migraciones.bat
   ```
   o
   ```powershell
   .\ejecutar_migraciones.ps1
   ```

3. **Inicializar datos:**
   ```batch
   inicializar_datos.bat
   ```
   o
   ```powershell
   .\inicializar_datos.ps1
   ```

4. **Ejecutar servidor:**
   ```batch
   ejecutar_proyecto.bat
   ```
   o
   ```powershell
   .\ejecutar_proyecto.ps1
   ```

#### Scripts Disponibles:

| Script | Función | Cuándo usar |
|--------|---------|------------|
| `instalar_dependencias.*` | Crea venv e instala todas las dependencias | Solo la primera vez |
| `ejecutar_migraciones.*` | Ejecuta makemigrations + migrate | Después de instalar dependencias |
| `inicializar_datos.*` | Carga roles, áreas, prioridades, SLAs y jornadas | Después de migraciones |
| `ejecutar_proyecto.*` | Inicia el servidor Django | Cada vez que quieras correr la app |

#### Acceso Rápido:
- **Aplicación Web**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

---

### 2. Opción B: Instalación Manual

#### Instalar dependencias

```bash
pip install -r requirements.txt
```

#### Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:
```env
DB_NAME=ticket_system
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=3306
```

#### Crear base de datos

```sql
CREATE DATABASE ticket_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Ejecutar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

#### Inicializar datos básicos

```bash
python manage.py init_data
```

Esto crea:
- 3 roles (Operativo, Jefe de Área, Supervisión General)
- 3 áreas (Soporte, Infraestructura, Por Definir)
- 4 prioridades (Crítica, Alta, Media, Baja)
- 4 SLAs predefinidos
- 3 jornadas

#### Crear superusuario

```bash
python manage.py createsuperuser
```

#### Ejecutar servidor

```bash
python manage.py runserver
```

---

### Acceder al Sistema

- **Aplicación Web**: http://localhost:8000 ← **¡Interfaz principal!**
- **Admin Panel**: http://localhost:8000/admin
- **API Docs (Swagger)**: http://localhost:8000/api/docs
- **API Docs (ReDoc)**: http://localhost:8000/api/redoc

## 🖥️ Interfaz Web

El sistema incluye una **interfaz web completa y profesional** con diseño elegante:

### Esquema de Colores
- **Blanco (#FFFFFF)**: Fondos principales
- **Negro (#1a1a1a)**: Texto, bordes, estructura
- **Dorado (#D4AF37)**: Botones, elementos destacados

### Páginas Disponibles

#### 1. **Login** (`/login/`)
Pantalla de autenticación con diseño elegante

#### 2. **Dashboard** (`/`)
- KPIs principales (tickets abiertos, en atención, cumplimiento SLA)
- Próximo ticket FIFO (para operativos)
- Tabla de tickets activos
- Tickets pendientes de triaje (para jefes de área)
- Estadísticas por jornada (para supervisión general)

#### 3. **Lista de Tickets** (`/tickets/`)
- Tabla completa con paginación
- Filtros por: Estado, Área, Prioridad, SLA
- Indicadores visuales de SLA (semáforo 🟢🟡🔴)
- Búsqueda avanzada

#### 4. **Detalle de Ticket** (`/tickets/<id>/`)
- Información completa del ticket
- Historial de estados con timeline visual
- Panel de control SLA
- Fechas clave
- Botones de acción según permisos

#### 5. **Crear Ticket** (`/tickets/crear/`)
Formulario para crear nuevos tickets (operativos)

#### 6. **Gestión de Triaje** (`/triaje/`)
- Lista de tickets sin área asignada
- Asignación de área y usuario
- Solo para Jefes de Área

#### 7. **Reportes** (`/reportes/`)
Dashboard de estadísticas globales (Supervisión General)

### Usuarios de Prueba

Después de ejecutar las migraciones y `init_data`, crear estos usuarios:

```python
# python manage.py shell
from apps.usuarios.models import Usuario, Rol
from apps.tickets.models import Area

# Obtener roles
rol_operativo = Rol.objects.get(nivel=1)
rol_jefe = Rol.objects.get(nivel=2)
rol_supervisor = Rol.objects.get(nivel=3)
area_soporte = Area.objects.get(nombre='Soporte')

# Crear usuarios
Usuario.objects.create_user(
    email='supervisor@test.com',
    password='123456',
    nombre='Supervisor',
    rol=rol_supervisor
)

Usuario.objects.create_user(
    email='jefe@test.com',
    password='123456',
    nombre='Jefe Soporte',
    rol=rol_jefe,
    area=area_soporte
)

Usuario.objects.create_user(
    email='operativo@test.com',
    password='123456',
    nombre='Operativo',
    rol=rol_operativo,
    area=area_soporte
)
```

**Ver guía completa**: [docs/INICIO_RAPIDO.md](docs/INICIO_RAPIDO.md)

## 🏗️ Arquitectura

Este proyecto sigue una **arquitectura en capas profesional**:

```
┌─────────────────────────────────────┐
│     Capa de Presentación            │ ← Templates / API REST
├─────────────────────────────────────┤
│     Capa de Controladores           │ ← Views / ViewSets
├─────────────────────────────────────┤
│     Capa de Servicios               │ ← Lógica de Negocio
├─────────────────────────────────────┤
│     Capa de Datos (ORM)             │ ← Models / Managers
├─────────────────────────────────────┤
│     Base de Datos MySQL             │
└─────────────────────────────────────┘
```

**Ver documentación completa**: [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md)

## 🎨 Patrones de Diseño Implementados

1. **Service Layer Pattern**: Separación de lógica de negocio
2. **Repository Pattern**: Abstracción de acceso a datos mediante Managers
3. **Factory Pattern**: Creación controlada de objetos
4. **Strategy Pattern**: Comportamiento dinámico según rol
5. **Template Method Pattern**: Modelos base reutilizables
6. **Soft Delete Pattern**: Preservación de datos históricos
7. **Command Pattern**: Encapsulación de operaciones
8. **Facade Pattern**: Simplificación de interfaces complejas

## 📁 Estructura del Proyecto

```
ticketSystem/
├── config/                 # Configuración del proyecto
│   ├── settings/          # Settings por ambiente (base, dev, prod)
│   ├── urls.py           # URLs principales
│   └── wsgi.py
├── apps/                  # Aplicaciones Django
│   ├── core/             # Funcionalidad común (BaseModel)
│   ├── usuarios/         # Gestión de usuarios y roles
│   ├── tickets/          # Sistema de tickets (núcleo)
│   └── reportes/         # Reportes y KPIs
├── services/             # Capa de servicios (lógica de negocio)
│   ├── ticket_service.py
│   └── reporte_service.py
├── docs/                 # Documentación
│   ├── ARQUITECTURA.md
│   ├── DESARROLLO.md
│   └── database.sql
├── logs/                 # Logs del sistema
├── static/               # Archivos estáticos
├── media/                # Archivos de usuario
├── templates/            # Plantillas HTML
├── requirements.txt      # Dependencias Python
├── .env.example         # Ejemplo de configuración
├── .gitignore
├── manage.py
└── README.md
```

## 🔐 Jerarquía de Usuarios

### Nivel 1 - Operativos
- ✓ Solo visualizan tickets asignados
- ✓ Gestionan sus tickets
- ✗ No ven información global

### Nivel 2 - Jefes de Área
- ✓ Visualizan todos los tickets de su área
- ✓ Realizan triaje y asignación
- ✓ Reasignan tickets
- ✓ Supervisan desempeño operativo
- ✓ Generan reportes por área

### Nivel 3 - Supervisión General
- ✓ Visualizan todos los tickets del sistema
- ✓ Monitorean métricas globales
- ✓ Acceden a reportes generales
- ✓ Supervisan cumplimiento de SLA organizacional
- ✓ Administran configuraciones estratégicas

## 📊 Control de SLA

### Semáforo de Estados

| Color | Estado | Condición |
|-------|--------|-----------|
| 🟢 Verde | Dentro de tiempo | < 80% del SLA |
| 🟡 Amarillo | Próximo a vencer | 80-100% del SLA |
| 🔴 Rojo | SLA vencido | > 100% del SLA |

## 🔄 Estados del Ticket

1. **Abierto** → Ticket recién creado
2. **Asignado** → Ticket asignado a operativo
3. **En Atención** → Operativo trabajando en el ticket
4. **Cerrado** → Ticket resuelto manualmente
5. **Cerrado Automático** → Cerrado por inactividad

## 🛠️ Comandos de Management

### Inicializar datos del sistema

```bash
python manage.py init_data
```

### Cerrar tickets inactivos

```bash
python manage.py cerrar_tickets_inactivos
```

### Django Shell mejorado

```bash
python manage.py shell_plus
```

## 📚 Documentación

- **[Arquitectura del Sistema](docs/ARQUITECTURA.md)**: Patrones, componentes y diseño
- **[Guía de Desarrollo](docs/DESARROLLO.md)**: Setup, convenciones y buenas prácticas
- **[Script SQL](docs/database.sql)**: Creación de base de datos

## 🧪 Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Tests de una app específica
python manage.py test apps.tickets

# Con coverage
coverage run --source='.' manage.py test
coverage report
```

## 🔧 Configuración por Ambiente

El proyecto soporta múltiples ambientes:

- **Development**: `config/settings/development.py`
- **Production**: `config/settings/production.py`

Cambiar ambiente modificando `DJANGO_SETTINGS_MODULE` en `manage.py`.

## 📦 Tecnologías Utilizadas

- **Backend**: Django 5.0.2
- **API**: Django REST Framework 3.14.0
- **Base de Datos**: MySQL 8.0+
- **Documentación API**: drf-yasg (Swagger/ReDoc)
- **Variables de entorno**: python-decouple

## 🌟 Próximas Funcionalidades

- [ ] API REST completa con ViewSets
- [ ] Autenticación JWT
- [ ] Frontend con React/Vue
- [ ] Dashboard de métricas en tiempo real
- [ ] Notificaciones por email
- [ ] Exportación de reportes a PDF/Excel
- [ ] Sistema de adjuntos en tickets
- [ ] Chat en tiempo real

## 📝 Licencia

Proyecto propietario - Todos los derechos reservados

## 👥 Contacto

Para soporte o consultas, contactar al equipo de desarrollo.
