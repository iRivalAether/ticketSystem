# Inicio Rápido - Sistema Web de Tickets

## 🚀 Pasos para Ejecutar el Sistema

### 1. Activar el Entorno Virtual
```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Aplicar Migraciones (primera vez)
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 3. Inicializar Datos del Sistema
```powershell
python manage.py init_data
```

Este comando crea:
- ✅ 3 Roles (Operativo, Jefe de Área, Supervisión General)
- ✅ 3 Áreas (Soporte, Infraestructura, Por Definir)
- ✅ 4 Prioridades (Crítica, Alta, Media, Baja)
- ✅ 4 SLAs (Crítico, Alto, Medio, Bajo)
- ✅ 3 Jornadas (Matutina, Vespertina, Nocturna)

### 4. Crear Usuarios de Prueba

#### Crear Superusuario (Administrador)
```powershell
python manage.py createsuperuser
# Email: admin@ticketsystem.com
# Contraseña: (la que desees)
```

#### Crear Usuarios en el Shell de Django
```powershell
python manage.py shell
```

```python
from apps.usuarios.models import Usuario, Rol
from apps.tickets.models import Area

# Obtener roles y áreas
rol_operativo = Rol.objects.get(nivel=1)
rol_jefe = Rol.objects.get(nivel=2)  
rol_supervisor = Rol.objects.get(nivel=3)

area_soporte = Area.objects.get(nombre='Soporte')
area_infra = Area.objects.get(nombre='Infraestructura')

# 1. Crear Supervisor General
supervisor = Usuario.objects.create_user(
    email='supervisor@ticketsystem.com',
    password='supervisor123',
    nombre='Carlos Mendoza',
    rol=rol_supervisor
)

# 2. Crear Jefe de Área - Soporte
jefe_soporte = Usuario.objects.create_user(
    email='jefe.soporte@ticketsystem.com',
    password='jefe123',
    nombre='María González',
    rol=rol_jefe,
    area=area_soporte
)

# 3. Crear Jefe de Área - Infraestructura
jefe_infra = Usuario.objects.create_user(
    email='jefe.infra@ticketsystem.com',
    password='jefe123',
    nombre='Roberto Pérez',
    rol=rol_jefe,
    area=area_infra
)

# 4. Crear Operativo - Soporte
operativo1 = Usuario.objects.create_user(
    email='soporte1@ticketsystem.com',
    password='operativo123',
    nombre='Ana Torres',
    rol=rol_operativo,
    area=area_soporte
)

# 5. Crear Operativo - Soporte
operativo2 = Usuario.objects.create_user(
    email='soporte2@ticketsystem.com',
    password='operativo123',
    nombre='Luis Ramírez',
    rol=rol_operativo,
    area=area_soporte
)

# 6. Crear Operativo - Infraestructura
operativo3 = Usuario.objects.create_user(
    email='infra1@ticketsystem.com',
    password='operativo123',
    nombre='Diana Flores',
    rol=rol_operativo,
    area=area_infra
)

print("✅ Usuarios creados exitosamente")
exit()
```

### 5. Ejecutar el Servidor de Desarrollo
```powershell
python manage.py runserver
```

El servidor estará disponible en: **http://127.0.0.1:8000/**

## 🎭 Usuarios de Prueba Creados

| Email | Contraseña | Rol | Área |
|-------|-----------|-----|------|
| supervisor@ticketsystem.com | supervisor123 | Supervisión General | N/A |
| jefe.soporte@ticketsystem.com | jefe123 | Jefe de Área | Soporte |
| jefe.infra@ticketsystem.com | jefe123 | Jefe de Área | Infraestructura |
| soporte1@ticketsystem.com | operativo123 | Operativo | Soporte |
| soporte2@ticketsystem.com | operativo123 | Operativo | Soporte |
| infra1@ticketsystem.com | operativo123 | Operativo | Infraestructura |

## 📋 Flujo de Trabajo Típico

### Como Operativo (Nivel 1)

1. **Login** → http://127.0.0.1:8000/login/
   - Email: soporte1@ticketsystem.com
   - Contraseña: operativo123

2. **Dashboard** → Ver próximo ticket FIFO y tus tickets asignados

3. **Crear Ticket** → Botón "+ Crear Nuevo Ticket"
   - Título: "Error en módulo de facturación"
   - Descripción: "El sistema no genera el PDF de la factura"
   - Prioridad: Alta

4. **Ver Tickets** → Menú "Tickets"

5. **Iniciar Atención** → Botón "Iniciar Atención" en ticket asignado

6. **Cerrar Ticket** → Botón "Cerrar Ticket" → Describir solución

### Como Jefe de Área (Nivel 2)

1. **Login** → http://127.0.0.1:8000/login/
   - Email: jefe.soporte@ticketsystem.com
   - Contraseña: jefe123

2. **Dashboard** → Ver tickets pendientes de triaje

3. **Gestionar Triaje** → Menú "Triaje"
   - Ver tickets sin asignar
   - Asignar área
   - Opcionalmente asignar usuario específico
   - Si no asignas usuario, quedará en cola FIFO

4. **Ver Todos los Tickets de tu Área** → Menú "Tickets"

### Como Supervisión General (Nivel 3)

1. **Login** → http://127.0.0.1:8000/login/
   - Email: supervisor@ticketsystem.com
   - Contraseña: supervisor123

2. **Dashboard** → Ver estadísticas globales por jornada

3. **Reportes** → Menú "Reportes"
   - Ver cumplimiento de SLA
   - Tickets verde/amarillo/rojo
   - Estadísticas generales

4. **Ver Todos los Tickets** → Acceso completo al sistema

## 🎨 Diseño del Sistema

El sistema utiliza un esquema de colores elegante:

- **Blanco (#FFFFFF)**: Fondos y backgrounds
- **Negro (#1a1a1a)**: Texto, bordes, estructura
- **Dorado (#D4AF37)**: Botones, elementos destacados, indicadores activos

### Indicadores SLA (Semáforo)

- 🟢 **Verde**: Ticket con tiempo suficiente (< 80% del SLA)
- 🟡 **Amarillo**: Ticket próximo a vencer (80-100% del SLA)
- 🔴 **Rojo**: Ticket vencido (> 100% del SLA)

## 🔧 Panel de Administración

Django Admin está disponible en: **http://127.0.0.1:8000/admin/**

Usa el superusuario que creaste anteriormente.

En el admin puedes:
- Ver todos los modelos
- Gestionar usuarios, áreas, prioridades, SLAs
- Ver indicadores visuales de SLA en tickets
- Acceder al historial de estados y asignaciones

## 📊 Características Principales

### Jerarquía de 3 Niveles
- **Nivel 1 - Operativo**: Crea tickets, atiende tickets asignados
- **Nivel 2 - Jefe de Área**: Realiza triaje, asigna tickets, supervisa su área
- **Nivel 3 - Supervisión General**: Acceso global, reportes, métricas

### Sistema FIFO
- Los tickets sin asignar se muestran en cola FIFO
- Cada operativo ve su próximo ticket según orden de llegada
- Al iniciar atención, sale de la cola FIFO

### Control de SLA
- Cada prioridad tiene un SLA asociado
- Semáforo visual en todas las vistas
- Tiempo de primera respuesta + tiempo de resolución
- Alertas visuales cuando los tickets están próximos a vencer

### Trazabilidad Completa
- Historial de estados (Abierto → Asignado → En Atención → Cerrado)
- Historial de asignaciones
- Registro de usuario y fecha en cada cambio
- Comentarios en cada transición

## 🛠️ Comandos Útiles

### Ver logs
```powershell
Get-Content .\logs\ticketSystem.log -Tail 50
```

### Crear datos de prueba adicionales
```powershell
python manage.py shell
```

```python
from services.ticket_service import TicketService
from apps.usuarios.models import Usuario
from apps.tickets.models import Prioridad

# Obtener usuario
usuario = Usuario.objects.get(email='soporte1@ticketsystem.com')
prioridad = Prioridad.objects.get(nombre='Alta')

# Crear ticket
ticket = TicketService.crear_ticket(
    usuario_solicitante=usuario,
    titulo='Problema con el servidor de correo',
    descripcion='No se pueden enviar correos desde el sistema',
    prioridad=prioridad
)

print(f"Ticket creado: {ticket.folio}")
```

### Cerrar tickets inactivos automáticamente
```powershell
python manage.py cerrar_tickets_inactivos
```

## 📱 URLs Principales

| Ruta | Descripción |
|------|-------------|
| `/` | Dashboard principal |
| `/login/` | Inicio de sesión |
| `/logout/` | Cerrar sesión |
| `/tickets/` | Lista de todos los tickets |
| `/tickets/crear/` | Crear nuevo ticket |
| `/tickets/<id>/` | Detalle de ticket |
| `/triaje/` | Gestión de triaje (Jefes) |
| `/reportes/` | Dashboard de reportes (Supervisión) |
| `/admin/` | Panel de administración Django |
| `/api/docs/` | Documentación Swagger (pendiente) |

## ⚡ Solución de Problemas

### Error: No module named 'apps'
```powershell
# Asegúrate de estar en el directorio del proyecto
cd c:\pruebas\ticketSystem
```

### Error: Base de datos no existe
```powershell
# Crear la base de datos en MySQL
mysql -u root -p
CREATE DATABASE ticket_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;

# Aplicar migraciones
python manage.py migrate
```

### Error: STATIC_ROOT not found
```powershell
# Crear directorio de estáticos
python manage.py collectstatic --noinput
```

### No se ven los estilos CSS
```powershell
# Verificar que existe el directorio static/css/
# Verificar que DEBUG=True en development.py
# Reiniciar el servidor
```

## 🎯 Próximos Pasos

Después de probar el sistema web, puedes:

1. **Implementar API REST** → Serializers y ViewSets para consumir desde frontend separado
2. **Crear Frontend con React/Vue** → Interfaz moderna desacoplada
3. **Agregar Tests** → Pruebas unitarias y de integración
4. **Implementar WebSockets** → Notificaciones en tiempo real
5. **Añadir Reportes Avanzados** → Gráficas con Chart.js/D3.js
6. **Docker** → Containerizar la aplicación

---

**¡El sistema está listo para usar!** 🎉
